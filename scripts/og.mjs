// Renders site/og.png, the 1200 x 630 card used in the README and in link previews.
// The curves are days of the fixture. Run: npm run og (Chrome at CHROME_PATH or /usr/bin/google-chrome).
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const rows = readFileSync(join(root, 'fixtures', 'demand-12.csv'), 'utf8').trim().split('\n').slice(1).map(l => l.split(','));
const day = id => rows.find(r => r[0] === id).slice(3).map(Number);
const max = Math.max(...rows.flatMap(r => r.slice(3).map(Number)));
const path = (y, x0, w, top, h) => y.map((v, i) => `${i ? 'L' : 'M'}${(x0 + w * i / 47).toFixed(1)} ${(top + h - h * v / max).toFixed(1)}`).join(' ');

const groups = [{ ids: ['mon', 'wed', 'sat'], cy: 200, colour: '#3b5bdb' }, { ids: ['sun', 'd10', 'd12'], cy: 430, colour: '#161a23' }];
let art = '', row = 0;
for (const g of groups) {
  const nx = 1050, r = 74;
  for (const id of g.ids) {
    const top = 92 + row * 76, mid = top + 30;
    art += `<path d="${path(day(id), 640, 170, top, 56)}" fill="none" stroke="#6f7689" stroke-width="2.5" stroke-linejoin="round"/>`;
    art += `<path d="M822 ${mid} C 890 ${mid}, 900 ${g.cy}, ${nx - r} ${g.cy}" fill="none" stroke="${g.colour}" stroke-width="2" opacity=".55"/>`;
    row++;
  }
  art += `<circle cx="${nx}" cy="${g.cy}" r="${r}" fill="#fff" stroke="${g.colour}" stroke-width="2.5"/>`;
  for (const id of g.ids) art += `<path d="${path(day(id), nx - 56, 112, g.cy - 42, 84)}" fill="none" stroke="${g.colour}" stroke-width="2.5" stroke-linejoin="round" opacity=".8"/>`;
}

const font = f => 'file://' + join(root, 'node_modules', 'geist', 'dist', 'fonts', f);
const html = `<!doctype html><meta charset="utf-8"><style>
@font-face { font-family: Geist; src: url(${font('geist-sans/Geist-Variable.woff2')}); font-weight: 100 900; }
@font-face { font-family: Mono; src: url(${font('geist-mono/GeistMono-Variable.woff2')}); font-weight: 100 900; }
body { margin: 0; width: 1200px; height: 630px; background: #f5f6fa; color: #161a23; font-family: Geist; position: relative; overflow: hidden; }
.logo { position: absolute; left: 72px; top: 107px; width: 64px; height: 64px; border-radius: 12px; background: #3b5bdb; color: #fff; font: 600 26px Mono; display: flex; align-items: center; justify-content: center; }
h1 { position: absolute; left: 72px; top: 196px; margin: 0; font-size: 72px; line-height: 78px; font-weight: 700; letter-spacing: -2px; }
p { position: absolute; left: 72px; top: 372px; margin: 0; width: 500px; font-size: 30px; line-height: 40px; color: #464d5e; }
small { position: absolute; left: 72px; top: 494px; font: 500 22px Mono; color: #3b5bdb; letter-spacing: 1px; }
svg { position: absolute; left: 0; top: 0; }
</style><div class="logo">TS</div><h1>Time series<br>clustering</h1>
<p>Which measure, which algorithm, how to validate.</p><small>FREE MINI COURSE</small>
<svg width="1200" height="630">${art}</svg>`;

const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome',
  args: ['--disable-gpu', '--disable-software-rasterizer', '--use-gl=swiftshader', '--allow-file-access-from-files'] });
const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
const tmp = join(root, 'tests', 'output', 'og.html');
mkdirSync(dirname(tmp), { recursive: true });
writeFileSync(tmp, html);
await page.goto('file://' + tmp);
await page.evaluate(() => document.fonts.ready);
await page.screenshot({ path: join(root, 'site', 'og.png') });
await browser.close();
