import puppeteer from 'puppeteer';
import { execSync } from 'child_process';
import { homedir } from 'os';

const url = process.argv[2];

if (!url || !url.startsWith("http")) {
  console.error("❌ Usage: html-check.js <url>");
  console.error("💡 Example: node html-check.js http://localhost:9090");
  process.exit(2);
}

// Optional: find Chromium from Puppeteer cache
function findChromiumBinary() {
  try {
    const cmd = `find ${homedir()}/.cache/puppeteer -name chrome -type f | sort | tail -1`;
    const path = execSync(cmd).toString().trim();
    if (path && path.endsWith('/chrome')) {
      console.log(`🧭 Using Chromium binary at: ${path}`);
      return path;
    }
  } catch (err) {
    console.warn('⚠️ Failed to locate Chromium binary in Puppeteer cache.');
  }
  return null;
}

const chromiumPath = findChromiumBinary();

(async () => {
  console.log(`🌐 Testing URL: ${url}`);
  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: chromiumPath || undefined
  });

  const page = await browser.newPage();

  try {
    await page.goto(url, {
      waitUntil: 'networkidle2',
      timeout: 10000
    });

    const errors = await page.$$eval('.error, .alert-danger', els =>
      els.map(el => el.innerText.trim()).filter(t => t.length > 0)
    );

    if (errors.length) {
      console.log("❌ Found visible error messages on the page:");
      for (const msg of errors) {
        console.log("→", msg);
      }
      await browser.close();
      process.exit(1);
    } else {
      console.log("✅ Page loaded successfully with no known errors.");
      await browser.close();
      process.exit(0);
    }
  } catch (err) {
    console.error("💥 Test failed:", err.message || err);
    await browser.close();
    process.exit(1);
  }
})();
