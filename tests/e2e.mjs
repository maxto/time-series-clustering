// End-to-end check of the built site in headless Chrome (playwright-core).
//
// 1. Builds the smoke fixture (tests/fixtures/smoke) into tests/output/smoke-dist and checks it
//    twice: from file:// and from a local HTTP server that serves it under /time-series-clustering/,
//    the GitHub Pages subpath. The smoke checks pin every engine feature (sections, math, figures,
//    margin notes, links, planned lessons skipped by previous/next).
// 2. Builds the real content/ fresh into tests/output/content-preview (preview mode, the map is a draft) (never reading an old dist/) and runs the
//    general checks on it, when content/_course.md exists.
//
// General checks, in both runs: no console error, no failed request, no request to another
// origin, home links and every lesson's exact previous/next (from the source _course.md),
// lesson -> home, theme button and stored choice, system dark fallback, dark body colour,
// no horizontal overflow at 375 px.
// Chrome: CHROME_PATH or /usr/bin/google-chrome. Run via `npm test`.
import { chromium } from 'playwright-core';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const out = path.join(root, 'tests', 'output');
const PREFIX = '/time-series-clustering/';
const SITE_URL = 'https://maxto.github.io/time-series-clustering/';
const DARK_BG = 'rgb(28, 32, 41)';
const THEME_KEY = 'tsc:theme';
const failures = [];
const expect = (ok, msg) => { if (!ok) failures.push(msg); };

fs.mkdirSync(out, { recursive: true });
const smokeDist = path.join(out, 'smoke-dist');
const realDist = path.join(out, 'content-preview');
execFileSync('uv', ['run', 'python', 'scripts/build.py', '--content', 'tests/fixtures/smoke', '--dist', smokeDist],
  { cwd: root, stdio: 'inherit' });
if (fs.existsSync(path.join(root, 'content', '_course.md'))) {
  execFileSync('uv', ['run', 'python', 'scripts/build.py', '--preview', '--dist', realDist], { cwd: root, stdio: 'inherit' });
}

// --- tiny static server: the built directory under PREFIX, 404 for anything else ---
const TYPES = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.svg': 'image/svg+xml',
  '.woff2': 'font/woff2', '.js': 'text/javascript; charset=utf-8',
};
function serve(dir) {
  const server = http.createServer((req, res) => {
    const notFound = () => { res.writeHead(404, { 'content-type': 'text/plain' }); res.end('not found'); };
    const pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    if (!pathname.startsWith(PREFIX)) return notFound();
    let rel = pathname.slice(PREFIX.length);
    if (rel === '' || rel.endsWith('/')) rel += 'index.html';
    const file = path.resolve(dir, rel);
    const type = TYPES[path.extname(file)];
    if (!file.startsWith(dir + path.sep) || !type || !fs.existsSync(file) || !fs.statSync(file).isFile()) return notFound();
    res.writeHead(200, { 'content-type': type });
    fs.createReadStream(file).pipe(res);
  });
  return new Promise(resolve => server.listen(0, '127.0.0.1', () => resolve(server)));
}

const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome',
  args: ['--disable-gpu', '--disable-software-rasterizer', '--use-gl=swiftshader'],
});

// A context that records console errors, failed requests, HTTP errors and requests to other origins.
async function context(run, opts, isLocal) {
  const ctx = await browser.newContext(opts);
  await ctx.route('**/*', route => {
    const url = route.request().url();
    if (isLocal(url)) return route.continue();
    failures.push(`${run}: request to another origin: ${url}`);
    return route.abort();
  });
  ctx.on('requestfailed', r => isLocal(r.url()) && failures.push(`${run}: request failed: ${r.url()} (${r.failure()?.errorText})`));
  ctx.on('response', r => r.status() >= 400 && failures.push(`${run}: HTTP ${r.status()} for ${r.url()}`));
  ctx.on('page', p => {
    p.on('console', m => m.type() === 'error' && failures.push(`${run}: console error on ${p.url()}: ${m.text()}`));
    p.on('pageerror', e => failures.push(`${run}: page error on ${p.url()}: ${e.message}`));
  });
  return ctx;
}

const bodyBg = p => p.evaluate(() => getComputedStyle(document.body).backgroundColor);
const theme = p => p.evaluate(() => document.documentElement.dataset.theme || null);
const stored = p => p.evaluate(k => localStorage.getItem(k), THEME_KEY);
const count = (p, sel) => p.locator(sel).count();

async function clickTo(p, sel, endsWith) {
  await Promise.all([p.waitForURL(u => u.href.endsWith(endsWith)), p.locator(sel).first().click()]);
  await p.waitForLoadState('load');
}

// Lesson pages linked from the home, as paths relative to the site root ("alpha/index.html").
async function lessonLinks(p) {
  return p.$$eval('.modules a', as => as.map(a => a.getAttribute('href')));
}

async function smokeChecks(run, p, url) {
  // home lists all lessons, planned ones marked "coming" and not linked
  await p.goto(url('index.html'));
  expect(await count(p, '.modules li') === 3, `${run}: home does not list the 3 smoke lessons`);
  const beta = p.locator('.modules li', { hasText: 'Beta' });
  expect(await beta.count() === 1 && (await beta.textContent()).includes('coming'), `${run}: home does not mark beta as coming`);
  expect(await beta.locator('a').count() === 0, `${run}: planned lesson beta is linked from the home`);
  expect(JSON.stringify(await lessonLinks(p)) === JSON.stringify(['alpha/index.html', 'gamma/index.html']),
    `${run}: home links are not alpha and gamma: ${await lessonLinks(p)}`);
  expect(await p.locator('head link[rel="canonical"]').getAttribute('href') === SITE_URL, `${run}: home canonical link`);
  expect(await p.locator('head meta[property="og:url"]').getAttribute('content') === SITE_URL, `${run}: home og:url`);

  // home -> lesson
  await clickTo(p, '.modules a[href="alpha/index.html"]', 'alpha/index.html');
  expect(await p.locator('h1').innerText() === 'Alpha lesson', `${run}: alpha h1 missing`);
  expect(await p.locator('head link[rel="canonical"]').getAttribute('href') === SITE_URL + 'alpha/', `${run}: alpha canonical link`);
  expect(await p.locator('head meta[property="og:title"]').count() === 1, `${run}: alpha has no og:title`);
  expect(await count(p, 'aside .note') >= 3 && await p.locator('aside .note').first().isVisible(), `${run}: alpha margin notes missing`);
  expect(await count(p, 'aside .note.finance') === 1, `${run}: alpha In finance note missing`);
  expect(await count(p, 'main figure svg[role="img"] > title') === 1, `${run}: alpha inline svg figure missing`);
  expect(await count(p, 'main figure figcaption') === 1, `${run}: alpha figcaption missing`);
  expect(await count(p, 'main .katex math') >= 2, `${run}: alpha has no KaTeX MathML`);
  expect(await count(p, 'main .katex-display') >= 2, `${run}: alpha display math missing`);
  expect(await count(p, '.card.measure .katex') === 1, `${run}: alpha measure card math missing`);
  expect(await p.locator('pre code', { hasText: '## not a section' }).count() === 1, `${run}: fenced "## not a section" not shown as code`);
  expect(await p.locator('h2', { hasText: 'not a section' }).count() === 0, `${run}: fenced "## not a section" became a heading`);
  expect(await count(p, 'h3#a-subheading') === 1 && await count(p, 'main section a[href="#a-subheading"]') === 1,
    `${run}: fragment link #a-subheading has no heading target`);
  expect(await count(p, '.pager a.prev') === 0, `${run}: alpha has a previous link`);
  expect(await count(p, 'a[href*="beta"]') === 0, `${run}: alpha links to the planned lesson beta`);
  expect((await p.locator('.pager a.next').innerText()).includes('Gamma'), `${run}: alpha next does not skip to gamma`);

  // working link in the lesson body
  await clickTo(p, 'main section a[href="../gamma/index.html"]', 'gamma/index.html');
  expect(await p.locator('h1').innerText() === 'Gamma lesson', `${run}: body link to gamma did not load gamma`);
  expect(await count(p, 'main section#validity-example') === 1, `${run}: gamma content section "Validity example" missing`);
  expect(await count(p, '.pager a.next') === 0, `${run}: gamma has a next link`);
  expect(await count(p, 'a[href*="beta"]') === 0, `${run}: gamma links to the planned lesson beta`);

  // previous / next on every lesson: navigation() below, against the manifest

  // lesson -> home
  await clickTo(p, '.bar a.brand', 'index.html');
  expect(await count(p, '.modules') === 1, `${run}: brand link did not load the home`);
}

// Published lesson ids in course order, read from the source _course.md (not from the built pages).
function publishedIds(contentDir) {
  const ids = [];
  for (const line of fs.readFileSync(path.join(contentDir, '_course.md'), 'utf8').split('\n')) {
    const m = line.match(/^- (\S+) \| (published|planned) \| .+$/);
    if (m && m[2] === 'published') ids.push(m[1]);
  }
  return ids;
}

// Home links equal the published ids in order. Every lesson has exactly its manifest neighbours
// as previous/next (none before the first, none after the last). Walk forward with next and back
// with prev, clicking every pager link, then return home with the brand link.
async function navigation(run, p, url, ids) {
  await p.goto(url('index.html'));
  const expected = ids.map(id => `${id}/index.html`);
  const links = await lessonLinks(p);
  expect(JSON.stringify(links) === JSON.stringify(expected), `${run}: home links ${JSON.stringify(links)}, expected ${JSON.stringify(expected)}`);
  expect(ids.length > 0, `${run}: no published lesson in _course.md`);
  if (!ids.length) return;
  const pager = async i => {
    for (const [dir, j] of [['prev', i - 1], ['next', i + 1]]) {
      const hrefs = await p.$$eval(`.pager a.${dir}`, as => as.map(a => a.getAttribute('href')));
      const want = j >= 0 && j < ids.length ? [`../${ids[j]}/index.html`] : [];
      expect(JSON.stringify(hrefs) === JSON.stringify(want), `${run}: ${ids[i]} ${dir} links ${JSON.stringify(hrefs)}, expected ${JSON.stringify(want)}`);
    }
    expect(p.url().endsWith(`${ids[i]}/index.html`) && await count(p, 'main h1') === 1, `${run}: ${ids[i]} did not load (${p.url()})`);
  };
  await clickTo(p, `.modules a[href="${expected[0]}"]`, expected[0]);
  await pager(0);
  for (let i = 1; i < ids.length; i++) {
    if (await count(p, '.pager a.next') !== 1) return;
    await clickTo(p, '.pager a.next', expected[i]);
    await pager(i);
  }
  for (let i = ids.length - 2; i >= 0; i--) {
    if (await count(p, '.pager a.prev') !== 1) return;
    await clickTo(p, '.pager a.prev', expected[i]);
    await pager(i);
  }
  await clickTo(p, '.bar a.brand', 'index.html');
  expect(await count(p, '.modules') === 1, `${run}: brand link did not load the home`);
}

async function suite(label, dist, contentDir, smoke) {
  dist = path.resolve(dist);
  const ids = publishedIds(contentDir);
  const lessons = ids.map(id => `${id}/index.html`);
  const runs = [{ name: `${label} file://`, url: rel => pathToFileURL(path.join(dist, rel)).href, isLocal: u => u.startsWith('file://') }];
  const server = await serve(dist);
  const origin = `http://127.0.0.1:${server.address().port}`;
  runs.push({ name: `${label} http`, url: rel => origin + PREFIX + rel, isLocal: u => u.startsWith(origin + '/'), http: true });

  for (const run of runs) {
    // light system preference: navigation, smoke features, theme button and stored choice
    let ctx = await context(run.name, { viewport: { width: 1280, height: 900 }, colorScheme: 'light' }, run.isLocal);
    let p = await ctx.newPage();
    if (smoke) await smokeChecks(run.name, p, run.url);
    await navigation(run.name, p, run.url, ids);

    await p.goto(run.url('index.html'));
    expect(await theme(p) === null && await bodyBg(p) !== DARK_BG, `${run.name}: home does not start light`);
    const button = p.locator('.bar button.theme');
    expect(await button.count() === 1 && !!(await button.getAttribute('aria-label')), `${run.name}: theme button missing or has no aria-label`);
    await button.click();
    expect(await theme(p) === 'dark', `${run.name}: theme button did not set data-theme="dark"`);
    expect(await stored(p) === 'dark', `${run.name}: theme button did not store ${THEME_KEY}`);
    expect(await bodyBg(p) === DARK_BG, `${run.name}: dark body background is ${await bodyBg(p)}, expected ${DARK_BG}`);
    if (lessons.length) {
      await p.goto(run.url(lessons[0]));
      expect(await theme(p) === 'dark' && await bodyBg(p) === DARK_BG, `${run.name}: ${lessons[0]} did not load dark after the choice`);
      if (smoke && run.http) {
        await p.screenshot({ path: path.join(out, 'smoke-lesson-dark.png'), fullPage: true });
      }
      await p.locator('.bar button.theme').click();
      expect(await theme(p) === 'light' && await stored(p) === 'light', `${run.name}: theme button did not switch back to light`);
      if (smoke && run.http) {
        await p.screenshot({ path: path.join(out, 'smoke-lesson-light.png'), fullPage: true });
      }
    }
    await ctx.close();

    // dark system preference with no stored choice: pages start dark
    ctx = await context(run.name, { viewport: { width: 1280, height: 900 }, colorScheme: 'dark' }, run.isLocal);
    p = await ctx.newPage();
    for (const rel of ['index.html', ...lessons]) {
      await p.goto(run.url(rel));
      expect(await stored(p) === null, `${run.name}: storage not empty in a fresh context`);
      expect(await theme(p) === null && await bodyBg(p) === DARK_BG, `${run.name}: ${rel} does not start dark with a dark system preference`);
    }
    await ctx.close();

    // phone width: no horizontal overflow
    ctx = await context(run.name, { viewport: { width: 375, height: 812 }, colorScheme: 'light' }, run.isLocal);
    p = await ctx.newPage();
    for (const rel of ['index.html', ...lessons]) {
      await p.goto(run.url(rel));
      const w = await p.evaluate(() => document.documentElement.scrollWidth);
      expect(w <= 375, `${run.name}: ${rel} is ${w} px wide at 375 px`);
    }
    await ctx.close();
  }
  server.close();
}

await suite('smoke', smokeDist, path.join(root, 'tests', 'fixtures', 'smoke'), true);
if (fs.existsSync(path.join(root, 'content', '_course.md'))) await suite('content-preview', realDist, path.join(root, 'content'), false);
else console.log('e2e: no content/_course.md yet, skipping the checks on the real build (smoke fixture checked)');

await browser.close();
if (failures.length) { console.error('FAIL\n' + failures.join('\n')); process.exit(1); }
console.log('e2e ok (screenshots in tests/output/)');
