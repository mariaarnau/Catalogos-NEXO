// Uso: node render_pdf.js entrada.html salida.pdf
const path = require('path');
const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright');
(async () => {
  const [inp, out] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(inp), { waitUntil: 'networkidle' });
  await page.pdf({ path: out, width: '960px', height: '904px', printBackground: true, preferCSSPageSize: true });
  await browser.close();
})();
