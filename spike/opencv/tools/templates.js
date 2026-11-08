// Render SMuFL glyph templates from Bravura (OFL-1.1) in headless Chromium.
//   node templates.js [sp=24] -> data/templates.json  {sp, glyphs: {name: {w, h, ox, oy, data(base64 u8 alpha)}}}
// 1 em = 4 staff spaces (SMuFL); ox/oy = glyph origin inside the bitmap (origin = baseline point).
const fs = require('fs'), path = require('path');
const { chromium } = require(path.join(__dirname, '../../../mvp/tools/pw/node_modules/playwright'));
const SP = +(process.argv[2] || 24);
const G = {
  'rest-breve': 0xE4E2, 'rest-whole': 0xE4E3, 'rest-half': 0xE4E4, 'rest-quarter': 0xE4E5, 'rest-8th': 0xE4E6, 'rest-16th': 0xE4E7, 'rest-32nd': 0xE4E8, 'rest-64th': 0xE4E9,
  'acc-flat': 0xE260, 'acc-natural': 0xE261, 'acc-sharp': 0xE262, 'acc-double-sharp': 0xE263, 'acc-double-flat': 0xE264,
  'clef-G': 0xE050, 'clef-C': 0xE05C, 'clef-F': 0xE062,
  'digit-0': 0xE080, 'digit-1': 0xE081, 'digit-2': 0xE082, 'digit-3': 0xE083, 'digit-4': 0xE084, 'digit-5': 0xE085, 'digit-6': 0xE086, 'digit-7': 0xE087, 'digit-8': 0xE088, 'digit-9': 0xE089,
  'time-C': 0xE08A, 'time-cut': 0xE08B,
  'fermata-up': 0xE4C0, 'fermata-down': 0xE4C1,
  'dyn-p': 0xE520, 'dyn-m': 0xE521, 'dyn-f': 0xE522, 'dyn-s': 0xE524, 'dyn-z': 0xE525,
  'flag-8th-up': 0xE240, 'flag-8th-down': 0xE241, 'flag-16th-up': 0xE242, 'flag-16th-down': 0xE243, 'flag-32nd-up': 0xE244, 'flag-32nd-down': 0xE245, 'flag-64th-up': 0xE246, 'flag-64th-down': 0xE247,
  'dot': 0xE1E7, 'head-filled': 0xE0A4, 'head-half': 0xE0A3, 'head-whole': 0xE0A2,
};
(async () => {
  const font = fs.readFileSync(path.join(__dirname, '../fonts/Bravura.woff2')).toString('base64');
  const cached = process.env.HOME + '/.cache/ms-playwright/chromium_headless_shell-1208/chrome-linux/headless_shell';
  const browser = await chromium.launch(fs.existsSync(cached) ? { executablePath: cached } : {});
  const page = await browser.newPage();
  await page.setContent(`<style>@font-face{font-family:B;src:url(data:font/woff2;base64,${font})}</style><span style="font-family:B">&#xE050;</span>`);
  await page.evaluate(() => document.fonts.ready);
  const out = await page.evaluate(({ G, SP }) => {
    const res = {};
    const size = 4 * SP, W = 8 * SP, H = 12 * SP, ox = 2 * SP, oy = 7 * SP;
    const c = document.createElement('canvas'); c.width = W; c.height = H;
    const g = c.getContext('2d', { willReadFrequently: true });
    for (const [name, cp] of Object.entries(G)) {
      g.clearRect(0, 0, W, H); g.font = `${size}px B`; g.fillStyle = '#000'; g.fillText(String.fromCodePoint(cp), ox, oy);
      const d = g.getImageData(0, 0, W, H).data;
      let x0 = W, y0 = H, x1 = -1, y1 = -1;
      for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) if (d[(y * W + x) * 4 + 3] > 0) { if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; }
      const w = x1 - x0 + 1, h = y1 - y0 + 1, a = new Uint8Array(w * h);
      for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) a[y * w + x] = d[((y + y0) * W + x + x0) * 4 + 3];
      res[name] = { w, h, ox: ox - x0, oy: oy - y0, data: btoa(String.fromCharCode(...a)) };
    }
    return res;
  }, { G, SP });
  await browser.close();
  fs.mkdirSync(path.join(__dirname, '../data'), { recursive: true });
  fs.writeFileSync(path.join(__dirname, '../data/templates.json'), JSON.stringify({ sp: SP, font: 'Bravura 1.392 (OFL-1.1)', glyphs: out }));
  console.log(Object.entries(out).map(([k, v]) => `${k}:${v.w}x${v.h}`).join(' '));
})();
