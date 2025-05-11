const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
  });

  const page = await browser.newPage();

  const url = 'http://localhost:9090/#/overview';
  console.log(`🌐 Visiting ${url}`);

  // 🔍 Log all console messages
  page.on('console', msg => {
    const type = msg.type().toUpperCase();
    console.log(`[Console:${type}]`, msg.text());
  });

  // ⚠️ Log failed network requests (client-side failure)
  page.on('requestfailed', req => {
    console.warn('[Request Failed]', req.url(), '-', req.failure()?.errorText);
  });

  // 🧾 Log HTTP responses with error codes (e.g. 404, 500)
  page.on('response', async response => {
    if (!response.ok()) {
      console.warn(`[HTTP ${response.status()}] ${response.url()}`);
    }
  });

  await page.goto(url, { waitUntil: 'networkidle2' });
  await page.waitForTimeout(3000);

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const screenshotDir = './screenshots';
  const screenshotPath = path.join(screenshotDir, `ui-check-${timestamp}.png`);

  fs.mkdirSync(screenshotDir, { recursive: true });

  await page.screenshot({ path: screenshotPath, fullPage: true });

  console.log(`✅ Screenshot saved to: ${screenshotPath}`);

  await browser.close();
})();
