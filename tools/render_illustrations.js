// Render illustrations/*.svg -> illustrations/*.png (1200x675) with the Gilroy font.
// Usage: node tools/render_illustrations.js   (needs Playwright + Chromium)
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
(async () => {
  const dir = path.resolve(__dirname, '..', 'illustrations');
  const font = path.resolve(__dirname, '..', 'src', 'Gilroy-Bold.ttf');
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1200, height: 675 } });
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.svg'))) {
    const svgPath = path.join(dir, f), pngPath = svgPath.replace(/\.svg$/, '.png');
    if (fs.existsSync(pngPath) && fs.statSync(pngPath).mtimeMs >= fs.statSync(svgPath).mtimeMs) continue;
    const svg = fs.readFileSync(svgPath, 'utf8');
    await p.setContent(`<html><head><style>@font-face{font-family:Gilroy;src:url(file://${font});font-weight:700}body{margin:0}</style></head><body>${svg}</body></html>`);
    await p.waitForTimeout(250);
    await p.screenshot({ path: pngPath, clip: { x: 0, y: 0, width: 1200, height: 675 } });
    console.log('rendered', f);
  }
  await b.close();
})();
