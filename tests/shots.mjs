// Full-page screenshots of the built site for review by eye: `npm run shots`.
//
// Builds content/ in preview mode (the map is a draft) into tests/output/shots-site/ first, so the captures always match the current tree. Then captures
// the home and every published lesson (from content/_course.md), light and dark (through the
// system preference, with no stored choice), at 1280 and 375 px, as full-page PNGs in
// tests/output/shots/: <page>-<theme>-<width>-full.png. manifest.json records the commit, whether
// the tree had changes, and the files. The folder is cleared first, so no stale capture remains.
// Chrome: CHROME_PATH or /usr/bin/google-chrome (needs --disable-gpu to take screenshots).
import { chromium } from 'playwright-core';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const dist = path.join(root, 'tests', 'output', 'shots-site');
const out = path.join(root, 'tests', 'output', 'shots');
const contentDir = path.join(root, 'content');

if (!fs.existsSync(path.join(contentDir, '_course.md'))) {
  console.log('shots: no content/_course.md, nothing to capture');
  process.exit(0);
}
execFileSync('uv', ['run', 'python', 'scripts/build.py', '--preview', '--dist', dist], { cwd: root, stdio: 'inherit' });

const ids = [];
for (const line of fs.readFileSync(path.join(contentDir, '_course.md'), 'utf8').split('\n')) {
  const m = line.match(/^- (\S+) \| (published|planned) \| .+$/);
  if (m && m[2] === 'published') ids.push(m[1]);
}
const pages = [['home', 'index.html'], ...ids.map(id => [id, `${id}/index.html`])];

fs.rmSync(out, { recursive: true, force: true });
fs.mkdirSync(out, { recursive: true });

const git = args => execFileSync('git', args, { cwd: root, encoding: 'utf8' }).trim();
const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome',
  args: ['--disable-gpu', '--disable-software-rasterizer', '--use-gl=swiftshader'],
});
const files = [];
for (const theme of ['light', 'dark']) {
  for (const width of [1280, 375]) {
    const ctx = await browser.newContext({ viewport: { width, height: 900 }, colorScheme: theme });
    const p = await ctx.newPage();
    for (const [name, rel] of pages) {
      await p.goto(pathToFileURL(path.join(dist, rel)).href);
      await p.evaluate(() => document.fonts.ready);
      const file = `${name}-${theme}-${width}-full.png`;
      await p.screenshot({ path: path.join(out, file), fullPage: true });
      files.push(file);
    }
    await ctx.close();
  }
}
await browser.close();

const manifest = {
  commit: git(['rev-parse', '--short', 'HEAD']),
  tree_changed: git(['status', '--porcelain']) !== '',
  taken: new Date().toISOString(),
  kind: 'full-page captures (not viewport crops)',
  files,
};
fs.writeFileSync(path.join(out, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
console.log(`shots: ${files.length} full-page captures of ${manifest.commit}${manifest.tree_changed ? ' (tree has changes)' : ''} in ${path.relative(root, out)}/`);
