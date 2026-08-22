const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const page = await browser.newPage();
  await page.goto('file://' + __dirname + '/catalogo.html', { waitUntil: 'networkidle' });
  await page.pdf({
    path: 'Nexo_Academico_Guia_Alumno.pdf',
    printBackground: true,
    preferCSSPageSize: true,
  });
  await browser.close();
})();
