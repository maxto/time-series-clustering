// End-to-end check of the built site in headless Chrome (playwright-core).
//
// 1. Builds the smoke fixture (tests/fixtures/smoke) into tests/output/smoke-dist and checks it
//    twice: from file:// and from a local HTTP server that serves it under /time-series-clustering/,
//    the GitHub Pages subpath. The smoke checks pin every engine feature (sections, math, figures,
//    the shell, the lesson page contract, links, planned lessons skipped by previous/next).
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
const REPO_URL = 'https://github.com/maxto/Time-Series-Clustering';
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

  expect(await p.locator('html').getAttribute('data-root') === '' && await count(p, 'header.top .progress') === 0, `${run}: home data-root or progress bar`);
  // home -> lesson
  await clickTo(p, '.modules a[href="alpha/index.html"]', 'alpha/index.html');
  expect(await p.locator('h1').innerText() === 'Alpha lesson', `${run}: alpha h1 missing`);
  expect(await p.locator('head link[rel="canonical"]').getAttribute('href') === SITE_URL + 'alpha/', `${run}: alpha canonical link`);
  expect(await p.locator('head meta[property="og:title"]').count() === 1, `${run}: alpha has no og:title`);
  await lessonContract(run, p);
  expect(await count(p, 'main figure svg[role="img"] > title') === 1, `${run}: alpha inline svg figure missing`);
  expect(await count(p, 'main figure figcaption') === 1, `${run}: alpha figcaption missing`);
  expect(await count(p, 'main .katex math') >= 2, `${run}: alpha has no KaTeX MathML`);
  expect(await count(p, 'main .katex-display') >= 2, `${run}: alpha display math missing`);
  expect(await count(p, 'section.measure .katex') === 1, `${run}: alpha measure card math missing`);
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
  expect(await count(p, 'section.finance') === 0 && await count(p, 'section.code') === 0 && await count(p, 'section.measure') === 0, `${run}: gamma has blocks it does not define`);
  expect(await count(p, 'nav#contents li:has(> a[aria-current="page"]) > ol.toc') === 1 && await count(p, 'nav#contents li:has(> a[aria-current="page"]) span.fin') === 0, `${run}: gamma contents entry`);
  expect(await count(p, 'a[href*="beta"]') === 0, `${run}: gamma links to the planned lesson beta`);

  // previous / next on every lesson: navigation() below, against the manifest

  // lesson -> home
  await clickTo(p, 'header.top a.logo', 'index.html');
  expect(await count(p, '.modules') === 1, `${run}: logo link did not load the home`);
}

// The lesson page contract of Task 5, checked on smoke lesson alpha (expected values written by hand
// from tests/fixtures/smoke/01-alpha.md and _course.md, not read back from the build).
async function lessonContract(run, p) {
  const attr = (sel, name) => p.locator(sel).first().getAttribute(name);
  expect(await attr('html', 'data-root') === '../' && await attr('html', 'data-build') === 'release', `${run}: alpha html data-root/data-build`);
  // top bar
  expect(await count(p, 'header.top') === 1, `${run}: header.top missing`);
  expect(await p.locator('header.top a.logo').innerText() === 'TS', `${run}: logo mark is not TS`);
  expect((await attr('header.top a.logo', 'href')) === '../index.html', `${run}: logo href is not ../index.html`);
  expect(await count(p, 'header.top form.search input#q[type="search"][aria-label="Search the course"]') === 1, `${run}: search input missing`);
  expect(await count(p, 'header.top .progress > i') === 1, `${run}: reading progress missing on a lesson`);
  expect(await count(p, 'header.top button.theme') === 1, `${run}: theme button missing`);
  expect(await attr('header.top a.gh', 'href') === REPO_URL && await attr('header.top a.gh', 'aria-label') === 'GitHub repository', `${run}: GitHub link`);
  expect(await attr('header.top button.menu', 'aria-controls') === 'contents' && await attr('header.top button.menu', 'aria-expanded') === 'false', `${run}: menu button attributes`);
  expect(await count(p, 'aside') === 0, `${run}: the pilot margin aside is still there`);
  // contents
  const nav = p.locator('nav#contents');
  expect(await nav.count() === 1, `${run}: nav#contents missing`);
  const top = await nav.locator(':scope > a').evaluateAll(as => as.map(a => a.getAttribute('href')));
  expect(JSON.stringify(top) === JSON.stringify(['../index.html', '../index.html#map', '../index.html#sectors', '../sources/index.html']),
    `${run}: contents top links ${JSON.stringify(top)}`);
  const lessonLinksIn = await nav.locator('ol:not(.toc) > li > a').evaluateAll(as => as.map(a => a.getAttribute('href')));
  expect(JSON.stringify(lessonLinksIn) === JSON.stringify(['../alpha/index.html', '../gamma/index.html']),
    `${run}: contents lesson links ${JSON.stringify(lessonLinksIn)}`);
  expect(await count(p, 'nav#contents li.coming') === 1 && (await nav.locator('li.coming').innerText()).includes('Beta')
    && await count(p, 'nav#contents li.coming a') === 0, `${run}: contents does not list beta as coming without a link`);
  expect(await count(p, 'nav#contents span.fin') === 1 && (await nav.locator('li:has(span.fin)').innerText()).includes('Alpha'), `${run}: Finance tag only on alpha`);
  expect(await count(p, 'nav#contents ol.toc') === 1 && await count(p, 'nav#contents li:has(> a[aria-current="page"]) > ol.toc') === 1, `${run}: ol.toc not under the current lesson`);
  const toc = await nav.locator('ol.toc a').evaluateAll(as => as.map(a => a.getAttribute('href')));
  expect(JSON.stringify(toc) === JSON.stringify(['#engine-features', '#a-second-section', '#in-finance', '#measure-card', '#code', '#common-mistake']),
    `${run}: toc links ${JSON.stringify(toc)}`);
  // every jump and toc link resolves to an id on the page
  const targets = await p.$$eval('nav.jump a, ol.toc a', as => as.map(a => [a.getAttribute('href'), !!document.getElementById(a.getAttribute('href').slice(1))]));
  expect(targets.length === 11 && targets.every(([, ok]) => ok), `${run}: jump/toc links without a target: ${JSON.stringify(targets.filter(([, ok]) => !ok))} of ${targets.length}`);
  // main
  expect(await count(p, 'main#main') === 1, `${run}: main#main missing`);
  const order = await p.$$eval('main#main > *', els => els.map(e => e.classList[0] || e.tagName.toLowerCase()));
  expect(JSON.stringify(order) === JSON.stringify(['hero', 'trade', 'jump', 'oneline', 'content', 'content', 'finance', 'measure', 'code', 'mistake', 'lsrc', 'pager']),
    `${run}: main children ${JSON.stringify(order)}`);
  expect((await p.locator('.hero').innerText()).includes('Alpha lesson') && await count(p, '.hero .lede') === 1, `${run}: hero`);
  const trade = await p.locator('.trade').innerText();
  expect(trade.includes('It ignores') && trade.includes('local timing, small shifts') && trade.includes('It keeps') && trade.includes('level, scale'), `${run}: trade boxes: ${trade}`);
  expect(await count(p, 'section.content#engine-features') === 1 && await count(p, 'section.finance#in-finance') === 1
    && await count(p, 'section.measure#measure-card') === 1 && await count(p, 'section.code#code') === 1, `${run}: section ids`);
  // code
  expect(JSON.stringify(await p.$$eval('#code [role="tablist"] button[role="tab"]', bs => bs.map(b => b.dataset.lang))) === JSON.stringify(['python', 'r']), `${run}: code tabs`);
  expect(JSON.stringify(await p.$$eval('#code pre[data-lang]', ps => ps.map(x => [x.dataset.lang, x.textContent.trim()]))) === JSON.stringify([['python', 'print(1)'], ['r', 'cat(1)']]), `${run}: both code languages in the HTML`);
  expect(await count(p, '#code button.copy') === 1, `${run}: copy button`);
  const libs = await p.locator('#code p.libs').innerText();
  expect(libs.startsWith('Related library functions:') && libs.includes('tsc.distances') && libs.includes('distances.R'), `${run}: libs line: ${libs}`);
  // sources
  expect(await count(p, 'section.lsrc li#src-sakoe78') === 1, `${run}: #src-sakoe78 not in section.lsrc`);
  expect(await attr('a.cite', 'href') === '#src-sakoe78', `${run}: citation does not point to #src-sakoe78`);
  // measures: one width for everything, 18 px text
  expect(await p.locator('section.content p').first().evaluate(e => getComputedStyle(e).fontSize) === '18px', `${run}: body text is not 18 px`);
}

// Layout at the widths of design 4.1: fixed contents at 1180 px and above, a drawer below.
async function layoutChecks(run, p, url) {
  const w = sel => p.locator(sel).first().evaluate(e => Math.round(e.getBoundingClientRect().width));
  await p.setViewportSize({ width: 1280, height: 900 });
  await p.goto(url('alpha/index.html'));
  expect(await p.locator('nav#contents').isVisible() && !(await p.locator('button.menu').isVisible()), `${run}: 1280 px: contents fixed, no menu button`);
  expect(await w('nav#contents') === 290, `${run}: contents column is ${await w('nav#contents')} px, expected 290`);
  expect(await w('.hero') === 760 && await w('section.finance') === 760 && await w('#code .codebox') === 760, `${run}: 1280 px column is not 760 px for hero/finance/code`);
  // finance block surface: --fin-bg of each theme (light --ink #161a23, dark --fig-bg #171a21), with a border
  const fin = () => p.locator('section.finance').evaluate(e => { const c = getComputedStyle(e); return [c.backgroundColor, c.borderTopWidth]; });
  const [lightBg, lightBorder] = await fin();
  expect(lightBg === 'rgb(22, 26, 35)' && parseFloat(lightBorder) > 0, `${run}: light finance background ${lightBg}, border ${lightBorder}`);
  await p.evaluate(() => { document.documentElement.dataset.theme = 'dark'; });
  const [darkBg, darkBorder] = await fin();
  expect(darkBg === 'rgb(23, 26, 33)' && parseFloat(darkBorder) > 0, `${run}: dark finance background ${darkBg}, border ${darkBorder}`);
  await p.evaluate(() => { delete document.documentElement.dataset.theme; });
  await p.setViewportSize({ width: 1100, height: 900 });
  await p.waitForTimeout(400); // the drawer hides after its slide-out transition
  expect(!(await p.locator('nav#contents').isVisible()) && await p.locator('button.menu').isVisible(), `${run}: 1100 px: contents drawer closed, menu button shown`);
  expect(await w('.hero') === 800 && await w('section.finance') === 800, `${run}: 1100 px column is not 800 px`);
  await p.setViewportSize({ width: 390, height: 800 });
  await p.locator('button.menu').click();
  await p.evaluate(() => document.querySelector('button.menu').setAttribute('aria-expanded', 'true')); // Task 7 will toggle this
  await p.waitForTimeout(400);
  expect(await w('nav#contents') === 390, `${run}: phone drawer is ${await w('nav#contents')} px, expected full width 390`);
  await p.evaluate(() => document.querySelector('button.menu').setAttribute('aria-expanded', 'false'));
  expect(await p.locator('.hero').evaluate(e => getComputedStyle(e.parentElement).paddingLeft) === '18px', `${run}: phone padding is not 18 px`);
}

// No JavaScript: the page reads. Both code blocks visible, a citation reaches its source entry.
async function noJsChecks(run, browserContext, url) {
  const p = await browserContext.newPage();
  await p.goto(url('alpha/index.html'));
  expect(await p.locator('#code pre[data-lang="python"]').isVisible() && await p.locator('#code pre[data-lang="r"]').isVisible(), `${run}: no JS: both code blocks must be visible`);
  expect(await p.locator('section.finance').isVisible() && await p.locator('section.measure').isVisible(), `${run}: no JS: finance and measure card visible`);
  await Promise.all([p.waitForURL(u => u.hash === '#src-sakoe78'), p.locator('a.cite').first().click()]);
  expect(await p.locator('section.lsrc li#src-sakoe78').isVisible(), `${run}: no JS: source entry not visible after the citation click`);
  await p.setViewportSize({ width: 390, height: 800 });
  expect(!(await p.locator('button.menu').isVisible()) && await p.locator('nav#contents a[href$="gamma/index.html"]').isVisible()
    && await p.locator('nav#contents a[href$="index.html#map"]').isVisible(), `${run}: no JS at 390 px: contents links not visible`);
  await p.close();
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
  await clickTo(p, 'header.top a.logo', 'index.html');
  expect(await count(p, '.modules') === 1, `${run}: logo link did not load the home`);
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
    if (smoke) await layoutChecks(run.name, p, run.url);
    await navigation(run.name, p, run.url, ids);

    await p.goto(run.url('index.html'));
    expect(await theme(p) === null && await bodyBg(p) !== DARK_BG, `${run.name}: home does not start light`);
    const button = p.locator('header.top button.theme');
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
      await p.locator('header.top button.theme').click();
      expect(await theme(p) === 'light' && await stored(p) === 'light', `${run.name}: theme button did not switch back to light`);
      if (smoke && run.http) {
        await p.screenshot({ path: path.join(out, 'smoke-lesson-light.png'), fullPage: true });
      }
    }
    await ctx.close();

    if (smoke) {
      ctx = await context(run.name, { viewport: { width: 1280, height: 900 }, javaScriptEnabled: false }, run.isLocal);
      await noJsChecks(run.name, ctx, run.url);
      await ctx.close();
    }

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
