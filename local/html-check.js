// html-check.js
const puppeteer = require('puppeteer');
const { execSync, spawn } = require('child_process');
const net = require('net');

(async () => {
  const url = process.argv[2];

  if (!url) {
    console.error('❌ Error: No URL provided.\nUsage: node html-check.js <URL>');
    process.exit(1);
  }

  // 🔪 Kill uwsgi processes on 127.0.0.1:9091
  try {
    console.log('🔄 Killing existing uwsgi processes on 127.0.0.1:9091...');
    execSync(
      `ps -eo pid,cmd | grep '[u]wsgi' | grep '127.0.0.1:9091' | awk '{print $1}' | xargs -r kill`,
      { stdio: 'ignore', shell: '/bin/bash' }
    );
  } catch (err) {
    console.warn('⚠️ Warning: Could not kill uwsgi processes (maybe none running)');
  }

  // 🚀 Start the server
  console.log('🚀 Restarting the server with local/run-uwsgi.sh...');
  const serverProc = spawn('bash', ['local/run-uwsgi.sh'], {
    detached: true,
    stdio: 'ignore'
  });
  serverProc.unref(); // Let it run independently

  // ⏳ Wait for port 9090 to be available
  const waitForPort = (port, host = '127.0.0.1', timeout = 10000) => {
    return new Promise((resolve, reject) => {
      const start = Date.now();

      const tryConnect = () => {
        const socket = new net.Socket();
        socket.setTimeout(500);

        socket.once('connect', () => {
          socket.destroy();
          resolve(true);
        });

        socket.once('error', () => {
          socket.destroy();
          if (Date.now() - start >= timeout) {
            reject(new Error('Timed out waiting for server to start'));
          } else {
            setTimeout(tryConnect, 300);
          }
        });

        socket.once('timeout', () => {
          socket.destroy();
          if (Date.now() - start >= timeout) {
            reject(new Error('Timed out waiting for server to start'));
          } else {
            setTimeout(tryConnect, 300);
          }
        });

        socket.connect(port, host);
      };

      tryConnect();
    });
  };

  console.log('⏳ Waiting for server to be ready on port 9090...');
  try {
    await waitForPort(9090);
    console.log('✅ Server is up!');
  } catch (err) {
    console.error('❌ Server did not start in time.');
    process.exit(1);
  }

  // 🌐 Launch Puppeteer and test the page
  const browser = await puppeteer.launch({ headless: "new" });
  const page = await browser.newPage();

  try {
    await page.goto(url, { waitUntil: 'networkidle0' });

    const bodyText = await page.evaluate(() => document.body.innerText);

    if (bodyText.includes('The Document Service encountered an error')) {
      console.error('❌ Found known error message on the page.');
      await browser.close();
      process.exit(1);
    }

    console.log('✅ Page rendered without known error messages.');
    await browser.close();
    process.exit(0);

  } catch (err) {
    console.error('❌ Page load failed:', err.message);
    await browser.close();
    process.exit(1);
  }
})();
