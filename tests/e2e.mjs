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

// A context that records console errors, failed requests, HTTP errors, requests to other origins and any
// fetch or XHR request (the site makes none at runtime). `allow` is for the failure runs of the live figure
// and exempts only: the one blocked URL (its request, its failed load and the console line about it) with
// `blocked` (a path suffix, e.g. "assets/live.js"), and console errors that start "live figure:" with `liveErrors`.
async function context(run, opts, isLocal, allow = {}) {
  const ctx = await browser.newContext(opts);
  const isBlocked = url => !!allow.blocked && url.endsWith(allow.blocked);
  await ctx.route('**/*', route => {
    const url = route.request().url();
    if (isBlocked(url)) return route.abort();
    if (isLocal(url)) return route.continue();
    failures.push(`${run}: request to another origin: ${url}`);
    return route.abort();
  });
  ctx.on('request', r => ['fetch', 'xhr'].includes(r.resourceType()) && failures.push(`${run}: ${r.resourceType()} request to ${r.url()}`));
  ctx.on('requestfailed', r => isLocal(r.url()) && !isBlocked(r.url()) && failures.push(`${run}: request failed: ${r.url()} (${r.failure()?.errorText})`));
  ctx.on('response', r => r.status() >= 400 && failures.push(`${run}: HTTP ${r.status()} for ${r.url()}`));
  ctx.on('page', p => {
    p.on('console', m => {
      if (m.type() !== 'error') return;
      if (allow.liveErrors && m.text().startsWith('live figure:')) return;
      if (allow.blocked && isBlocked(m.location().url || '')) return;
      failures.push(`${run}: console error on ${p.url()}: ${m.text()}`);
    });
    p.on('pageerror', e => failures.push(`${run}: page error on ${p.url()}: ${e.message}`));
  });
  return ctx;
}

// Failure runs of the live figure: like context, but it exempts only the one blocked URL, or only the
// console errors that start "live figure:", and still fails on anything else.
const failureContext = (run, opts, isLocal, allow) => context(run, opts, isLocal, allow);

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
  // deep-dive: closed by default, opens with a click and with Enter on its summary, no heading or toc entry
  const dd = p.locator('main details.deep');
  expect(await dd.count() === 1 && await dd.evaluate(e => !e.open && !e.id), `${run}: alpha deep-dive missing, open or with an id`);
  expect((await dd.locator('summary').innerText()) === 'Library conventions differ', `${run}: deep-dive summary text`);
  await dd.locator('summary').click();
  expect(await dd.evaluate(e => e.open), `${run}: deep-dive did not open on click`);
  await dd.locator('summary').click();
  expect(await dd.evaluate(e => !e.open), `${run}: deep-dive did not close on a second click`);
  await dd.locator('summary').focus();
  await p.keyboard.press('Enter');
  expect(await dd.evaluate(e => e.open) && await dd.locator('.katex').count() === 1 && await dd.locator('a.cite').count() === 1 && await dd.locator('li').count() === 2, `${run}: deep-dive did not open on Enter or lacks math, citation or list`);
  expect(await count(p, 'main details.deep h2, main details.deep h3, nav#contents a[href*="library"]') === 0, `${run}: deep-dive has a heading or a contents entry`);
  await dd.locator('summary').click();
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


const BANNER = 'Draft map. Local preview only. What each item ignores or needs, its functions and its sector fits are not yet checked against sources. A release build refuses this map until every item is checked.';

// Task 6 contract on the smoke home and sources page. Expected values are written by hand from
// tests/fixtures/smoke (_map.toml, _sectors.toml, _sources.toml, the lessons), not read back from the build.
async function homeChecks(run, p, url) {
  await p.goto(url('index.html'));
  expect(await count(p, 'main .hero a.start[href="alpha/index.html"]') === 1, `${run}: hero has no "Start with lesson 1" link to alpha`);
  expect(await count(p, 'main section#map') === 1 && await count(p, 'main section#sectors') === 1 && await count(p, 'main section#lessons') === 1, `${run}: home sections missing`);
  expect(await count(p, '#map div.branch[data-branch] div.family ul li.item') === 5, `${run}: map does not show 5 items`);
  expect(await count(p, '#map div.branch') === 2 && await count(p, '#map div.family') === 3, `${run}: map does not show 2 branches and 3 families`);
  expect(await count(p, 'li.item[data-item="agglomerative"] > details#item-agglomerative > summary.chip') === 1, `${run}: agglomerative chip missing`);
  expect(await p.locator('#item-agglomerative summary.chip span.cond').innerText() === 'Ward: Euclidean', `${run}: chip condition label`);
  expect(await count(p, '#item-euclidean summary.chip span.cond') === 0, `${run}: chip without condition has a cond label`);
  // native disclosure: a click on the summary opens the card (also with JavaScript off, see noJsChecks)
  expect(await p.locator('#item-agglomerative').evaluate(e => e.open) === false, `${run}: card starts open`);
  await p.locator('#item-agglomerative summary').click();
  expect(await p.locator('#item-agglomerative').evaluate(e => e.open) === true, `${run}: summary click did not open the card`);
  expect((await p.locator('#item-agglomerative').innerText()).includes('single, complete, average linkage'), `${run}: matrix item card lacks its linkage condition`);
  expect((await p.locator('#item-agglomerative').innerText()).includes('Merges the two closest groups, again and again.'), `${run}: card lacks the does text`);
  expect(await count(p, '#item-agglomerative a[href="#"], #map button a, #map summary a') === 0, `${run}: bad anchor in the map`);
  // filters
  expect(await count(p, '#f-ignore button[data-tag][aria-pressed="false"]') === 6, `${run}: f-ignore does not have 6 pressed=false buttons`);
  expect(JSON.stringify(await p.$$eval('#f-ignore button', bs => bs.map(b => [b.dataset.tag, b.textContent.trim()])))
    === JSON.stringify([['level', 'level'], ['scale', 'scale'], ['shift', 'a global shift'], ['warp', 'local timing'], ['noise', 'noise'], ['length', 'different lengths']]),
    `${run}: f-ignore tags or labels`);
  expect(await p.locator('button#f-matrix').innerText() === 'I only have a distance matrix' && await p.locator('button#f-matrix').getAttribute('aria-pressed') === 'false', `${run}: f-matrix`);
  expect(JSON.stringify(await p.$$eval('#f-question button[data-question]', bs => bs.map(b => b.dataset.question)))
    === JSON.stringify(['energy/same-hours', 'finance/same-dates']), `${run}: f-question buttons`);
  expect(await p.locator('#f-question').innerText().then(t => t.includes('Energy') && t.includes('Finance')), `${run}: f-question not grouped under sector names`);
  expect(await p.locator('p#f-status').getAttribute('aria-live') === 'polite', `${run}: f-status aria-live`);
  // data contract for map.js
  const data = JSON.parse(await p.locator('script#atlas-data').evaluate(e => e.textContent));
  expect(Object.keys(data.items).sort().join() === 'agglomerative,correlation,dtw,euclidean,k-medoids', `${run}: atlas-data items ${Object.keys(data.items)}`);
  expect(JSON.stringify(data.items.correlation) === JSON.stringify({ name: 'Correlation', branch: 'compare', ignores: [{ tag: 'level', cond: '' }, { tag: 'scale', cond: '' }], needs: [], draft: false }), `${run}: atlas-data correlation ${JSON.stringify(data.items.correlation)}`);
  expect(JSON.stringify(data.items.agglomerative.needs) === JSON.stringify([{ tag: 'matrix', cond: 'single, complete, average linkage' }]) && data.items.agglomerative.branch === 'group', `${run}: atlas-data agglomerative`);
  expect(JSON.stringify(data.questions['finance/same-dates']) === JSON.stringify({ text: 'Which assets move together on the same dates?', fits: [
    { item: 'correlation', mark: 'good', reason: 'Co-movement on the same dates is the classic question.', cond: '', draft: false },
    { item: 'dtw', mark: 'avoid', reason: 'Warping pairs different dates.', cond: '', draft: false }] }), `${run}: atlas-data finance question`);
  expect(Object.keys(data.questions).length === 2, `${run}: atlas-data question count`);
  // sector cards
  expect(await count(p, '#sectors div.sector[data-sector]') === 2 && await count(p, '#sectors div.sector a.q') === 2, `${run}: sector cards`);
  expect(await count(p, '#sectors div.sector[data-sector="energy"] svg[role="img"][viewBox] polyline.ln') === 1
    && await p.locator('#sectors div.sector[data-sector="energy"] svg > title').textContent() === 'Energy example curve', `${run}: energy sparkline`);
  const q = p.locator('#sectors a.q[data-question="energy/same-hours"]');
  expect(await q.getAttribute('href') === '#map', `${run}: a.q href`);
  const qt = await q.innerText();
  expect(qt.includes('Same hours, or same shape?') && qt.includes('Euclidean') && qt.includes('DTW'), `${run}: a.q text ${qt}`);
  // lesson index
  expect(await count(p, '#lessons li#lesson-beta') === 1 && await count(p, '#lessons li#lesson-alpha span.fin') === 1 && await count(p, '#lessons li#lesson-gamma span.fin') === 0, `${run}: lesson index and finance tags`);
  // release build: nothing is draft
  expect(await count(p, '.draft-banner') === 0 && await count(p, 'span.draft') === 0, `${run}: release home shows draft marks`);
  // sources page
  await p.goto(url('sources/index.html'));
  expect(await p.locator('html').getAttribute('data-root') === '../' && await p.locator('head link[rel="canonical"]').getAttribute('href') === SITE_URL + 'sources/', `${run}: sources data-root or canonical`);
  expect(await count(p, 'main p.policy') === 1 && await count(p, 'div#f-topic button[data-topic]') === 7, `${run}: sources policy or topic filter`);
  expect(await p.locator('#f-topic button[data-topic="all"]').innerText() === 'All', `${run}: sources All button`);
  const src = p.locator('li#src-sakoe78');
  const st = await src.innerText();
  expect(st.includes('Hiroaki Sakoe and Seibi Chiba') && st.includes('1978') && st.includes('Dynamic programming algorithm optimization'), `${run}: sakoe78 entry ${st}`);
  expect(await src.getAttribute('data-topics') === 'compare', `${run}: sakoe78 data-topics`);
  expect(await src.locator('a[href="https://doi.org/10.1109/TASSP.1978.1163055"]').count() === 1, `${run}: sakoe78 publisher link`);
  expect(st.includes('Cited in') && await src.locator('a[href="../alpha/index.html"]').count() === 1 && await src.locator('a[href="../gamma/index.html"]').count() === 0, `${run}: sakoe78 cited in alpha only`);
  expect(await count(p, 'header.top .progress') === 0 && await count(p, 'nav#contents a.pg[aria-current="page"]') === 1, `${run}: sources shell`);
  // contents link reaches the sources page
  await p.goto(url('index.html'));
  await clickTo(p, 'nav#contents a.pg[href="sources/index.html"]', 'sources/index.html');
  expect(await p.locator('h1').innerText() === 'Sources', `${run}: sources h1`);
}

// The real content in a preview build: the draft is visible outside the cards.
async function previewChecks(run, p, url, contentDir) {
  const items = (fs.readFileSync(path.join(contentDir, '_map.toml'), 'utf8').match(/^\[\[branch\.family\.item\]\]/gm) || []).length;
  await p.goto(url('index.html'));
  expect(await count(p, '#map li.item') === items, `${run}: map shows ${await count(p, '#map li.item')} items, _map.toml has ${items}`);
  expect(await count(p, '#map .draft-banner') === 1 && (await p.locator('#map .draft-banner').innerText()).trim() === BANNER, `${run}: draft banner text`);
  expect(await count(p, '#map summary.chip span.draft') > 0, `${run}: no draft mark on chips`);
  expect(await count(p, '#sectors div.sector span.draft') > 0, `${run}: no draft mark on sector cards`);
  const data = JSON.parse(await p.locator('script#atlas-data').evaluate(e => e.textContent));
  expect(Object.keys(data.items).length === items && Object.values(data.items).some(i => i.draft), `${run}: atlas-data items or draft flags`);
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
  // measures: 17 px text (owner, 2026-10-29, design 4.1)
  expect(await p.locator('section.content p').first().evaluate(e => getComputedStyle(e).fontSize) === '17px', `${run}: body text is not 17 px`);
}

// Layout at the widths of design 4.1: fixed contents at 1180 px and above, a drawer below.
async function layoutChecks(run, p, url) {
  const w = sel => p.locator(sel).first().evaluate(e => Math.round(e.getBoundingClientRect().width));
  await p.setViewportSize({ width: 1280, height: 900 });
  await p.goto(url('alpha/index.html'));
  expect(await p.locator('nav#contents').isVisible() && !(await p.locator('button.menu').isVisible()), `${run}: 1280 px: contents fixed, no menu button`);
  expect(await w('nav#contents') === 290, `${run}: contents column is ${await w('nav#contents')} px, expected 290`);
  expect(await w('.hero') === 680 && await w('section.finance') === 680 && await w('#code .codebox') === 680, `${run}: 1280 px column is not 680 px for hero/finance/code`);
  // running text stops at 34em (578 px at 17 px), about 75 characters, inside the 680 px column
  expect(await w('section.content > p') === 578, `${run}: 1280 px reading measure is ${await w('section.content > p')} px, expected 578`);
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
  expect(await w('.hero') === 720 && await w('section.finance') === 720, `${run}: 1100 px column is not 720 px`);
  await p.setViewportSize({ width: 390, height: 800 });
  await p.locator('button.menu').click();
  await p.waitForTimeout(400);
  expect(await w('nav#contents') === 390, `${run}: phone drawer is ${await w('nav#contents')} px, expected full width 390`);
  await p.keyboard.press('Escape');
  expect(await p.locator('.hero').evaluate(e => getComputedStyle(e.parentElement).paddingLeft) === '18px', `${run}: phone padding is not 18 px`);
}

// --- Task 7: behaviour (course.js, map.js). Expected values are written by hand from the design
// (4.1, 5) and from tests/fixtures/smoke, not read back from the scripts. ---
// WCAG 2.x contrast. Colours are "rgb(r, g, b)" or "rgba(r, g, b, a)" strings from getComputedStyle.
const rgbOf = c => c.match(/[\d.]+/g).map(Number);
const lum = ([r, g, b]) => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }; return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); };
const contrast = (a, b) => { const [x, y] = [lum(rgbOf(a)), lum(rgbOf(b))].sort((m, n) => n - m); return (x + 0.05) / (y + 0.05); };
// published values: black on white 21, #767676 on white 4.54, #777777 on white 4.48
expect(Math.abs(contrast('rgb(0, 0, 0)', 'rgb(255, 255, 255)') - 21) < 0.01, 'contrast helper: black on white is not 21');
expect(Math.abs(contrast('rgb(118, 118, 118)', 'rgb(255, 255, 255)') - 4.54) < 0.01, 'contrast helper: #767676 on white is not 4.54');
expect(Math.abs(contrast('rgb(119, 119, 119)', 'rgb(255, 255, 255)') - 4.48) < 0.01, 'contrast helper: #777777 on white is not 4.48');
// text colour of an element against the first opaque background found going up the tree (the page root is the last resort)
const textContrast = (p, sel) => p.locator(sel).first().evaluate(e => {
  const alpha = c => (c.match(/[\d.]+/g) || [0, 0, 0, 1])[3] === undefined ? 1 : Number(c.match(/[\d.]+/g)[3]);
  let n = e, bg = null;
  while (n && !bg) { const c = getComputedStyle(n).backgroundColor; if (alpha(c) > 0) bg = c; n = n.parentElement; }
  return [getComputedStyle(e).color, bg || 'rgb(255, 255, 255)'];
}).then(([fg, bg]) => contrast(fg, bg));

const jump = (p, y) => p.evaluate(top => window.scrollTo({ top, behavior: 'instant' }), y);

// The contents panel below 1180 px: opens from the menu button, traps Tab, Escape closes and returns focus.
async function drawerChecks(run, p, url) {
  for (const width of [820, 375]) {
    await p.setViewportSize({ width, height: 800 });
    await p.goto(url('alpha/index.html'));
    const menu = p.locator('header.top button.menu');
    expect(await menu.getAttribute('aria-expanded') === 'false', `${run}: ${width} px: menu starts expanded`);
    await menu.click();
    await p.waitForTimeout(400);
    expect(await menu.getAttribute('aria-expanded') === 'true' && await p.locator('nav#contents').isVisible(), `${run}: ${width} px: menu button did not open the contents`);
    const n = await p.locator('nav#contents').evaluate(nav => nav.querySelectorAll('a[href], button').length);
    let outside = 0;
    for (let i = 0; i < n + 2; i++) {
      await p.keyboard.press('Tab');
      if (!await p.evaluate(() => !!document.activeElement.closest('nav#contents'))) outside++;
    }
    for (let i = 0; i < 3; i++) {
      await p.keyboard.press('Shift+Tab');
      if (!await p.evaluate(() => !!document.activeElement.closest('nav#contents'))) outside++;
    }
    expect(outside === 0, `${run}: ${width} px: Tab left the open contents ${outside} times`);
    await p.keyboard.press('Escape');
    await p.waitForTimeout(400);
    expect(await menu.getAttribute('aria-expanded') === 'false' && !(await p.locator('nav#contents').isVisible()), `${run}: ${width} px: Escape did not close the contents`);
    expect(await p.evaluate(() => document.activeElement === document.querySelector('header.top button.menu')), `${run}: ${width} px: focus did not return to the menu button`);
    // the scrim closes it too, but only where the drawer leaves a strip of page to hit (not at 375 px, where it is full width)
    await menu.click();
    await p.waitForTimeout(400);
    if (width >= 820) {
      const hit = await p.evaluate(([x, y]) => { const el = document.elementFromPoint(x, y); return el && (el.id || el.className || el.tagName); }, [width - 5, 700]);
      expect(/scrim/.test(String(hit)), `${run}: ${width} px: the point outside the drawer hits ${hit}, not the scrim`);
      await p.mouse.click(width - 5, 700);
      await p.waitForTimeout(400);
      expect(await menu.getAttribute('aria-expanded') === 'false', `${run}: ${width} px: a click on the scrim did not close the contents`);
    } else {
      await p.locator('nav#contents button.close, nav#contents .close').first().click();
      await p.waitForTimeout(400);
      expect(await menu.getAttribute('aria-expanded') === 'false', `${run}: ${width} px: the close button did not close the contents`);
    }
  }
  await p.setViewportSize({ width: 1440, height: 900 });
  await p.goto(url('alpha/index.html'));
  expect(await p.locator('nav#contents').isVisible() && !(await p.locator('button.menu').isVisible()), `${run}: 1440 px: contents not visible without the button`);
}

// Scroll-spy on the contents and the reading progress bar (lesson alpha, 1280 x 600).
async function spyChecks(run, p, url) {
  await p.setViewportSize({ width: 1280, height: 600 });
  await p.goto(url('alpha/index.html'));
  const frac = () => p.evaluate(() => { const i = document.querySelector('.progress > i'); return i.getBoundingClientRect().width / i.parentElement.getBoundingClientRect().width; });
  expect(await frac() === 0, `${run}: progress at the top is ${await frac()}`);
  await jump(p, await p.evaluate(() => document.getElementById('measure-card').getBoundingClientRect().top + scrollY - 80));
  await p.waitForTimeout(250);
  const cur = await p.$$eval('nav#contents ol.toc a[aria-current="true"]', as => as.map(a => a.getAttribute('href')));
  expect(JSON.stringify(cur) === JSON.stringify(['#measure-card']), `${run}: scroll-spy marks ${JSON.stringify(cur)} at #measure-card`);
  const mid = await frac();
  expect(mid > 0.1 && mid < 0.95, `${run}: progress mid-lesson is ${mid}`);
  await jump(p, await p.evaluate(() => document.documentElement.scrollHeight));
  await p.waitForTimeout(250);
  expect(await frac() >= 0.99, `${run}: progress at the bottom is ${await frac()}`);
  await jump(p, 0);
  await p.waitForTimeout(250);
  expect(await frac() === 0 && await count(p, 'nav#contents ol.toc a[aria-current="true"]') === 0, `${run}: top of the page leaves a toc link marked or progress above 0`);
}

// Code tabs, copy, citation popover (lesson alpha). Fixture code: python "print(1)", R "cat(1)".
async function codeChecks(run, p, url, http) {
  await p.setViewportSize({ width: 1280, height: 900 });
  await p.goto(url('alpha/index.html'));
  const vis = lang => p.locator(`#code pre[data-lang="${lang}"]`).isVisible();
  expect(await vis('python') && !(await vis('r')), `${run}: only the Python block should show at first`);
  const tabs = await p.$$eval('#code [role="tab"]', ts => ts.map(t => [t.dataset.lang, t.getAttribute('aria-selected'), !!t.getAttribute('aria-controls')]));
  expect(JSON.stringify(tabs) === JSON.stringify([['python', 'true', true], ['r', 'false', true]]), `${run}: tab states ${JSON.stringify(tabs)}`);
  expect(await count(p, '#code pre[role="tabpanel"]') === 2, `${run}: code panels lack role=tabpanel`);
  await p.locator('#code [role="tab"][data-lang="r"]').click();
  expect(!(await vis('python')) && await vis('r'), `${run}: the R tab did not show only R`);
  const after = await p.$$eval('#code [role="tab"]', ts => ts.map(t => t.getAttribute('aria-selected')));
  expect(JSON.stringify(after) === JSON.stringify(['false', 'true']), `${run}: aria-selected after the R click ${JSON.stringify(after)}`);
  const ctrl = await p.locator('#code [role="tab"][data-lang="r"]').getAttribute('aria-controls');
  expect(!!ctrl && await p.locator(`[id="${ctrl}"]`).getAttribute('data-lang') === 'r', `${run}: R tab aria-controls does not point at the R block`);
  await p.locator('#code button.copy').click();
  await p.waitForTimeout(150);
  if (http) {
    const clip = await p.evaluate(() => navigator.clipboard.readText());
    expect(clip.trim() === 'cat(1)' && !clip.includes('print'), `${run}: copy put ${JSON.stringify(clip)} on the clipboard, expected the R code`);
    expect(await p.locator('#code button.copy').innerText() === 'Copied', `${run}: copy button label after copying`);
    await p.locator('#code [role="tab"][data-lang="python"]').click();
    await p.locator('#code button.copy').click();
    await p.waitForTimeout(150);
    expect((await p.evaluate(() => navigator.clipboard.readText())).trim() === 'print(1)', `${run}: copy after switching back to Python`);
  }
  // citation popover
  const cite = p.locator('a.cite').first();
  const hash = await p.evaluate(() => location.hash);
  await cite.click();
  const dlg = p.locator('[role="dialog"]');
  expect(await dlg.count() === 1 && await dlg.isVisible(), `${run}: citation did not open a dialog`);
  if (await dlg.count() === 1) {
    const label = await dlg.evaluate(d => { const el = document.getElementById(d.getAttribute('aria-labelledby')); return el ? el.textContent : null; });
    expect(label === 'Sakoe and Chiba (1978)', `${run}: dialog label ${label}`);
    const t = await dlg.innerText();
    expect(t.includes('Hiroaki Sakoe and Seibi Chiba') && t.includes('1978') && t.includes('Dynamic programming algorithm optimization for spoken word recognition')
      && t.includes('IEEE Transactions on Acoustics, Speech, and Signal Processing 26(1), 43-49'), `${run}: dialog content ${t}`);
    expect(await p.evaluate(() => document.querySelector('a.cite').nextElementSibling === document.querySelector('[role="dialog"]')), `${run}: the dialog is not right after its citation link`);
    await p.keyboard.press('Tab');
    expect(await p.evaluate(() => !!document.activeElement.closest('[role="dialog"]')), `${run}: Tab from the citation did not enter the popover`);
    expect(await dlg.locator('a[href="https://doi.org/10.1109/TASSP.1978.1163055"]').count() === 1, `${run}: dialog lacks the publisher link`);
  }
  expect(await p.evaluate(() => location.hash) === hash, `${run}: the citation click navigated`);
  await p.keyboard.press('Escape');
  expect(await dlg.count() === 0, `${run}: Escape did not close the citation dialog`);
  expect(await p.evaluate(() => document.activeElement === document.querySelector('a.cite')), `${run}: focus did not return to the citation link`);
  // a citation in the finance block: the popover must not inherit the finance link and focus colours
  for (const t of ['light', 'dark']) {
    await p.evaluate(x => { document.documentElement.dataset.theme = x; }, t);
    await p.locator('section.finance a.cite').click();
    await p.keyboard.press('Tab');
    const cs = await dlg.evaluate(d => ({ bg: getComputedStyle(d).backgroundColor, links: [...d.querySelectorAll('a')].map(a => getComputedStyle(a).color),
      ring: getComputedStyle(document.activeElement).outlineColor, inside: d.contains(document.activeElement) }));
    expect(cs.links.length >= 2 && cs.inside, `${run}: ${t}: finance popover has ${cs.links.length} links, focus inside ${cs.inside}`);
    expect(cs.links.every(c => contrast(c, cs.bg) >= 4.5), `${run}: ${t}: finance popover link contrast ${cs.links.map(c => contrast(c, cs.bg).toFixed(2))}`);
    expect(contrast(cs.ring, cs.bg) >= 4.5, `${run}: ${t}: finance popover focus ring contrast ${contrast(cs.ring, cs.bg).toFixed(2)}`);
    await p.keyboard.press('Escape');
  }
  await p.evaluate(() => { delete document.documentElement.dataset.theme; });
}

// The map filters on the smoke home. Items: euclidean (no ignores), correlation (ignores level, scale),
// dtw (ignores warp, "alignment within w permitted"), agglomerative and k-medoids (need matrix).
async function mapChecks(run, p, url) {
  await p.setViewportSize({ width: 1280, height: 900 });
  await p.goto(url('index.html'));
  expect(await count(p, '#map div.map-root') === 1 && (await p.locator('#map div.map-root').innerText()).includes('compare, group, validate'), `${run}: map root box`);
  expect(await count(p, '#map svg.wires[aria-hidden="true"]') === 1 && await count(p, '#map svg.wires path') >= 1, `${run}: 1280 px: connector lines missing or not aria-hidden`);
  await p.setViewportSize({ width: 390, height: 800 });
  await p.waitForTimeout(150);
  expect(await count(p, '#map svg.wires[aria-hidden="true"]') === 1 && await count(p, '#map svg.wires path') === 0, `${run}: 390 px: connector lines drawn while the branches stack`);
  await p.setViewportSize({ width: 1440, height: 900 });
  await p.waitForTimeout(150);
  expect(await count(p, '#map svg.wires path') >= 1, `${run}: 1440 px: connector lines not redrawn after a resize`);
  const states = () => p.$$eval('li.item[data-item]', ls => Object.fromEntries(ls.map(l => [l.dataset.item, l.dataset.state || ''])));
  const is = async (want, msg) => { const got = await states(); const w = { euclidean: '', correlation: '', dtw: '', agglomerative: '', 'k-medoids': '', ...want }; expect(JSON.stringify(Object.entries(got).sort()) === JSON.stringify(Object.entries(w).sort()), `${run}: ${msg}: ${JSON.stringify(got)}`); };
  const status = () => p.locator('#f-status').innerText();
  const tag = t => p.locator(`#f-ignore button[data-tag="${t}"]`);
  const press = async sel => (await p.locator(sel).getAttribute('aria-pressed'));
  const dim = { euclidean: 'dim', correlation: 'dim', dtw: 'dim', agglomerative: 'dim', 'k-medoids': 'dim' };
  await is({}, 'initial state');
  await tag('warp').click();
  await is({ ...dim, dtw: 'hit' }, 'warp');
  expect(await tag('warp').getAttribute('aria-pressed') === 'true', `${run}: warp button not pressed`);
  expect((await p.locator('li.item[data-item="dtw"]').innerText()).includes('alignment within w permitted'), `${run}: the warp condition is not next to the DTW chip`);
  expect((await status()).includes('1 of 5') && (await status()).includes('local timing'), `${run}: status for warp: ${await status()}`);
  for (const t of ['light', 'dark']) {
    await p.evaluate(x => { document.documentElement.dataset.theme = x; }, t);
    const c = await textContrast(p, 'li.item[data-item="euclidean"] summary.chip');
    expect(c >= 4.5, `${run}: ${t} theme: dimmed chip text contrast ${c.toFixed(2)} is below 4.5`);
  }
  await p.evaluate(() => { delete document.documentElement.dataset.theme; });
  await tag('level').click();
  await is(dim, 'warp and level (AND)');
  expect((await status()).includes('0 of 5'), `${run}: status for no match: ${await status()}`);
  await tag('warp').click();
  await is({ ...dim, correlation: 'hit' }, 'level');
  await tag('scale').click();
  await is({ ...dim, correlation: 'hit' }, 'level and scale');
  await tag('level').click(); await tag('scale').click();
  await is({}, 'all tags off');
  expect((await status()).includes('all 5 items'), `${run}: status with no filter: ${await status()}`);
  await p.locator('#f-matrix').click();
  await is({ ...dim, agglomerative: 'hit', 'k-medoids': 'hit' }, 'matrix');
  expect((await p.locator('li.item[data-item="agglomerative"]').innerText()).includes('single, complete, average linkage'), `${run}: matrix condition missing next to agglomerative`);
  const q = '#f-question button[data-question="finance/same-dates"]';
  await p.locator(q).click();
  await is({ ...dim, correlation: 'good', dtw: 'avoid' }, 'finance question');
  expect(await press('#f-matrix') === 'false' && await press(q) === 'true', `${run}: a question did not reset the matrix button`);
  const why = await p.locator('li.item[data-item="correlation"]').innerText();
  const whyDtw = await p.locator('li.item[data-item="dtw"]').innerText();
  expect(why.includes('Co-movement on the same dates is the classic question.') && whyDtw.includes('Warping pairs different dates.'), `${run}: fit reasons not shown`);
  expect((await status()).includes('Which assets move together on the same dates?'), `${run}: status lacks the question text: ${await status()}`);
  await tag('noise').click();
  expect(await press(q) === 'false' && await press('#f-ignore button[data-tag="noise"]') === 'true', `${run}: an ignore tag did not reset the question`);
  await tag('noise').click();
  await p.locator(q).click(); await p.locator(q).click();
  await is({}, 'question toggled off');
  expect(await count(p, 'li.item .why') === 0 && await count(p, 'li.item .fcond') === 0, `${run}: labels left behind after reset`);
  // a sector card question: scrolls to the map with that question pressed
  await jump(p, await p.evaluate(() => document.getElementById('sectors').getBoundingClientRect().top + scrollY - 60));
  await p.locator('#sectors a.q[data-question="energy/same-hours"]').click();
  await p.waitForTimeout(1200);
  const top = await p.locator('section#map').evaluate(e => e.getBoundingClientRect().top);
  expect(await press('#f-question button[data-question="energy/same-hours"]') === 'true' && top > -10 && top < 160, `${run}: sector card question: pressed ${await press('#f-question button[data-question="energy/same-hours"]')}, map top ${top}`);
  await is({ ...dim, euclidean: 'good' }, 'energy question');
  // a link to an item opens its card
  await p.goto(url('sources/index.html'));
  await p.goto(url('index.html') + '#item-dtw');
  expect(await p.locator('#item-dtw').evaluate(e => e.open), `${run}: #item-dtw did not open the card`);
}

// Sources page topic filter. Smoke sources: sakoe78 (compare), kaufman90 (group).
async function sourcesChecks(run, p, url) {
  await p.goto(url('sources/index.html'));
  const shown = () => p.$$eval('#src-list li.ref', ls => ls.filter(l => l.getClientRects().length).map(l => l.id));
  expect(JSON.stringify(await shown()) === JSON.stringify(['src-kaufman90', 'src-sakoe78']), `${run}: sources at first ${JSON.stringify(await shown())}`);
  await p.locator('#f-topic button[data-topic="group"]').click();
  expect(JSON.stringify(await shown()) === JSON.stringify(['src-kaufman90']), `${run}: group topic shows ${JSON.stringify(await shown())}`);
  expect(await p.locator('#f-topic button[data-topic="group"]').getAttribute('aria-pressed') === 'true' && await p.locator('#f-topic button[data-topic="all"]').getAttribute('aria-pressed') === 'false', `${run}: topic aria-pressed`);
  await p.locator('#f-topic button[data-topic="compare"]').click();
  expect(JSON.stringify(await shown()) === JSON.stringify(['src-sakoe78']), `${run}: compare topic shows ${JSON.stringify(await shown())}`);
  await p.locator('#f-topic button[data-topic="validate"]').click();
  expect((await shown()).length === 0, `${run}: validate topic shows ${JSON.stringify(await shown())}`);
  await p.locator('#f-topic button[data-topic="all"]').click();
  expect((await shown()).length === 2, `${run}: All does not show every source`);
}

// The real content: generic checks only.
async function contentBehaviour(run, p, url, lessons) {
  await p.setViewportSize({ width: 1280, height: 900 });
  await p.goto(url('index.html'));
  await p.locator('#f-ignore button').first().click();
  const hit = await count(p, 'li.item[data-state="hit"]');
  const dim = await count(p, 'li.item[data-state="dim"]');
  expect(hit > 0 && hit + dim === await count(p, 'li.item'), `${run}: first ignore tag marks ${hit} hits and ${dim} dimmed of ${await count(p, 'li.item')}`);
  await p.locator('#f-question button').first().click();
  expect(await count(p, 'li.item[data-state="good"]') > 0, `${run}: first question marks no good fit`);
  for (const rel of lessons) {
    await p.goto(url(rel));
    if (await count(p, 'a.cite') === 0) continue;
    await p.locator('a.cite').first().click();
    expect(await count(p, '[role="dialog"]') === 1, `${run}: ${rel}: citation dialog`);
    await p.keyboard.press('Escape');
    break;
  }
}

// --- Task 8: search. Expected values come from the design (4.1) and tests/fixtures/smoke. ---
const results = p => p.locator('#results');
const resultsOpen = p => results(p).isVisible();
async function searchChecks(run, p, url) {
  await p.setViewportSize({ width: 1280, height: 900 });
  await p.goto(url('alpha/index.html'));
  const q = p.locator('#q');
  const focusedQ = () => p.evaluate(() => document.activeElement === document.getElementById('q'));
  await p.keyboard.press('/');
  expect(await focusedQ(), `${run}: search: "/" did not focus #q`);
  expect(await q.inputValue() === '', `${run}: search: the "/" shortcut left a character in #q`);
  await p.keyboard.press('/');
  expect(await q.inputValue() === '/', `${run}: search: "/" typed inside #q must stay as text`);
  await q.fill('');
  await p.evaluate(() => document.activeElement.blur());
  // "/" does not steal from another field either: a textarea added by the test
  await p.evaluate(() => { const t = document.createElement('textarea'); t.id = 'tmp-ta'; document.body.appendChild(t); t.focus(); });
  await p.keyboard.press('/');
  expect(await p.evaluate(() => document.activeElement.id === 'tmp-ta') && await p.locator('#tmp-ta').inputValue() === '/', `${run}: search: "/" in a textarea must stay in the textarea`);
  await p.evaluate(() => document.getElementById('tmp-ta').remove());

  // type, results replace the page, the match is marked, the count is a polite live region
  await jump(p, 300);
  const y0 = await p.evaluate(() => window.pageYOffset);
  await q.click();
  await q.fill('second');
  await p.waitForTimeout(200);
  expect(await resultsOpen(p) && !(await p.locator('main').isVisible()), `${run}: search: results did not replace the page`);
  expect(await p.locator('#results [aria-live="polite"]').count() === 1, `${run}: search: no polite live region for the count`);
  const first = p.locator('#results ul a').first();
  expect((await first.getAttribute('href')) === '../alpha/index.html#a-second-section', `${run}: search: first result href ${await first.getAttribute('href')}`);
  expect(((await first.locator('mark').first().textContent()) || '').toLowerCase() === 'second', `${run}: search: the match is not marked`);
  expect((await first.innerText()).includes('A second section') && (await first.innerText()).includes('Alpha lesson'), `${run}: search: first result lacks lesson and section`);
  // Escape: results gone, field cleared and focused, the page at its previous scroll position
  await p.keyboard.press('Escape');
  await p.waitForTimeout(100);
  expect(!(await resultsOpen(p)) && await p.locator('main').isVisible(), `${run}: search: Escape did not close the results`);
  expect(await focusedQ() && await q.inputValue() === '', `${run}: search: after Escape the field must be empty and focused`);
  expect(Math.abs(await p.evaluate(() => window.pageYOffset) - y0) <= 2, `${run}: search: scroll position not restored`);
  // Enter goes to the first result
  await q.fill('second');
  await Promise.all([p.waitForURL(u => u.href.endsWith('alpha/index.html#a-second-section')), q.press('Enter')]);
  expect(!(await resultsOpen(p)), `${run}: search: results still open after Enter`);
  // a word found only inside the deep-dive lands on its section
  await q.fill('wavefront');
  await p.waitForTimeout(200);
  expect(await p.locator('#results ul a').count() === 1 && (await p.locator('#results ul a').first().getAttribute('href')) === '../alpha/index.html#a-second-section',
    `${run}: search: a word inside the deep-dive must find its section`);
  await q.fill('conventions differ');
  await p.waitForTimeout(200);
  expect((await p.locator('#results ul a').first().getAttribute('href')) === '../alpha/index.html#a-second-section', `${run}: search: the deep-dive title must find its section`);
  await p.keyboard.press('Escape');
  // a planned lesson is listed as coming
  await q.fill('beta');
  expect((await results(p).innerText()).toLowerCase().includes('coming'), `${run}: search: planned lesson not shown as coming`);
  expect(await p.locator('#results ul a').first().getAttribute('href') === '../index.html#lesson-beta', `${run}: search: planned lesson href`);
  await q.fill('');
  expect(!(await resultsOpen(p)), `${run}: search: emptying the field must close the results`);
  // no match
  await q.fill('zzzqqq');
  expect((await results(p).innerText()).includes('No results'), `${run}: search: no "No results" message`);
  await q.fill('x = 1');
  expect(await p.locator('#results ul a').count() === 0, `${run}: search: code block text must not be indexed`);
  await q.fill('');
  // a map result goes to the home and opens its card
  await q.fill('dtw');
  const map = p.locator('#results ul a[href$="index.html#item-dtw"]');
  expect(await map.count() === 1, `${run}: search: no map result for DTW`);
  await Promise.all([p.waitForURL(u => u.href.endsWith('index.html#item-dtw')), map.click()]);
  await p.waitForTimeout(200);
  expect(await p.locator('details#item-dtw').evaluate(d => d.open), `${run}: search: the map result did not open its card`);
  expect(!(await resultsOpen(p)), `${run}: search: results still open on the home`);
  // on the home too: a map result opens a card that was closed
  await p.locator('details#item-dtw summary').click();
  await q.fill('euclid');
  await p.locator('#results ul a[href$="#item-euclidean"]').click();
  await p.waitForTimeout(200);
  expect(await p.locator('details#item-euclidean').evaluate(d => d.open), `${run}: search: on the home the map result did not open its card`);
  // loading the home with the hash opens the card (first load, no click)
  await p.goto(url('index.html') + '#item-correlation');
  await p.waitForTimeout(200);
  expect(await p.locator('details#item-correlation').evaluate(d => d.open), `${run}: search: the hash did not open the card on load`);

  // contrast of the result rows, both themes
  for (const mode of ['light', 'dark']) {
    await p.goto(url('alpha/index.html'));
    await p.evaluate(m => { document.documentElement.dataset.theme = m; }, mode);
    await q.fill('second');
    for (const sel of ['#results ul a .t', '#results ul a .sec', '#results ul a .snip', '#results ul a mark', '#results .count']) {
      const c = await textContrast(p, sel);
      expect(c >= 4.5, `${run}: search: ${mode}: ${sel} contrast ${c.toFixed(2)} below 4.5`);
    }
    await q.fill('beta');
    const c = await textContrast(p, '#results ul a .kind');
    expect(c >= 4.5, `${run}: search: ${mode}: coming label contrast ${c.toFixed(2)}`);
    await q.fill('');
  }
  await p.evaluate(() => { delete document.documentElement.dataset.theme; });

  // phone: the drawer is open, "/" moves to the field, Escape closes only the results, then the drawer
  await p.setViewportSize({ width: 375, height: 800 });
  await p.goto(url('alpha/index.html'));
  const menu = p.locator('header.top button.menu');
  await menu.click();
  await p.waitForTimeout(400);
  await p.keyboard.press('/');
  expect(await focusedQ(), `${run}: search: 375 px: "/" with the drawer open did not focus #q`);
  await q.fill('second');
  await p.waitForTimeout(200);
  expect(await resultsOpen(p) && await results(p).evaluate(r => { const b = r.getBoundingClientRect(); const e = document.elementFromPoint(b.left + b.width / 2, b.top + 80); return r.contains(e); }),
    `${run}: search: 375 px: results hidden under the drawer`);
  await p.keyboard.press('Escape');
  await p.waitForTimeout(400);
  expect(!(await resultsOpen(p)) && await menu.getAttribute('aria-expanded') === 'true' && await p.locator('nav#contents').isVisible(), `${run}: search: 375 px: first Escape must close only the results`);
  await p.keyboard.press('Escape');
  await p.waitForTimeout(400);
  expect(await menu.getAttribute('aria-expanded') === 'false', `${run}: search: 375 px: second Escape did not close the drawer`);
  expect(await p.evaluate(() => document.activeElement === document.querySelector('header.top button.menu')), `${run}: search: 375 px: focus did not return to the menu button`);
  await p.setViewportSize({ width: 1280, height: 900 });
}

// Preview build: a draft map item carries a visible "draft" label in the results, readable in both themes.
async function previewSearchChecks(run, p, url) {
  await p.setViewportSize({ width: 1280, height: 900 });
  await p.goto(url('index.html'));
  const draftTitle = await p.evaluate(() => (window.TSC_SEARCH.filter(e => e.kind === 'map' && e.draft)[0] || {}).title || '');
  expect(draftTitle !== '', `${run}: search: the preview index has no draft map item`);
  if (!draftTitle) return;
  for (const mode of ['light', 'dark']) {
    await p.evaluate(m => { document.documentElement.dataset.theme = m; }, mode);
    await p.locator('#q').fill(draftTitle);
    const row = p.locator('#results ul a', { hasText: draftTitle }).first();
    expect((await row.locator('.draft').count()) >= 1 && await row.locator('.draft').first().isVisible(), `${run}: search: ${mode}: no visible draft label on "${draftTitle}"`);
    if (await row.locator('.draft').count()) {
      const c = await textContrast(p, '#results ul a .draft');
      expect(c >= 4.5, `${run}: search: ${mode}: draft label contrast ${c.toFixed(2)}`);
    }
    await p.locator('#q').fill('');
  }
  await p.evaluate(() => { delete document.documentElement.dataset.theme; });
}

// --- Task 9: the contrast matrix and the layout widths. The ratio comes from the helper above. The page
// function only reads computed styles and composes each colour over its ancestors' backgrounds (alpha
// included) into an opaque rgb(), so the helper above is the only place that computes a ratio. ---
// Rows: [selector, fg, bg, need, role]. A row is one distinct (element path, colours) pair on the page.
const PAGE_TEXT_COLOURS = String.raw`(() => {
  const parse = c => {
    let m = c.match(/^rgba?\(([^)]+)\)$/);
    if (m) { const v = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number); return [v[0], v[1], v[2], v.length > 3 ? v[3] : 1]; }
    m = c.match(/^color\(srgb ([^)]+)\)$/);
    if (m) { const v = m[1].split(/[ \/]+/).filter(Boolean).map(Number); return [v[0] * 255, v[1] * 255, v[2] * 255, v.length > 3 ? v[3] : 1]; }
    throw new Error('unparsed colour ' + c);
  };
  const over = (top, bot) => { const a = top[3]; return [0, 1, 2].map(i => top[i] * a + bot[i] * (1 - a)).concat([1]); };
  const css = v => 'rgb(' + v.slice(0, 3).map(x => Math.round(x * 100) / 100).join(', ') + ')';
  const pageBg = () => { const b = getComputedStyle(document.body).backgroundColor, h = getComputedStyle(document.documentElement).backgroundColor;
    const pb = parse(b), ph = parse(h); return pb[3] > 0 ? over(pb, over(ph, [255, 255, 255, 1])) : over(ph, [255, 255, 255, 1]); };
  // opaque background under an element: root first, then each ancestor's colour on top of it
  const bgUnder = el => { const chain = []; for (let n = el; n; n = n.parentElement) chain.unshift(n);
    let bg = [255, 255, 255, 1]; for (const n of chain) { const c = parse(getComputedStyle(n).backgroundColor); if (c[3] > 0) bg = over(c, bg); } return bg; };
  const opacityOf = el => { let o = 1; for (let n = el; n; n = n.parentElement) o *= Number(getComputedStyle(n).opacity); return o; };
  const name = el => { const out = []; for (let n = el, i = 0; n && n !== document.body && i < 3; n = n.parentElement, i++)
    out.unshift(n.tagName.toLowerCase() + (n.id ? '#' + n.id : '') + [...n.classList].slice(0, 2).map(c => '.' + c).join('')); return out.join(' > '); };
  const visible = el => { const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
    return r.width > 1 && r.height > 1 && cs.visibility === 'visible' && cs.display !== 'none' && !el.closest('.katex-mathml, svg, script, style, [hidden]'); };
  // body text: any text inside a paragraph or list item of the reading column (content sections, One line, Common mistake, In finance,
  // Measure card and the introduction paragraphs of Code (not the .libs library line, a small label), or the p itself when it carries .oneline / .mistake)
  // whose computed colour equals that paragraph's own colour (strong, code, math included). Links, accent emphasis and popovers are other text.
  const bodyScope = 'main :is(section.content, section.finance, section.measure, section.code, .oneline, .mistake) :is(p, li):not(.libs), main :is(p, li):is(.oneline, .mistake)';
  const areaOf = b => b.closest('section.finance') ? 'finance' : b.closest('section.measure') ? 'measure' : b.closest('section.code') ? 'code'
    : b.closest('.oneline') ? 'oneline' : b.closest('.mistake') ? 'mistake' : 'content';
  const rows = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const seen = new Set();
  for (let t = walker.nextNode(); t; t = walker.nextNode()) {
    if (!t.nodeValue.trim()) continue;
    const el = t.parentElement;
    if (seen.has(el) || !visible(el)) continue;
    seen.add(el);
    const bg = bgUnder(el);
    const fg = parse(getComputedStyle(el).color); fg[3] *= opacityOf(el);
    const blk = el.closest('p, li');
    const own = !!blk && blk.matches(bodyScope) && !el.closest('a, .cite, .pop') && getComputedStyle(el).color === getComputedStyle(blk).color;
    rows.push([name(el), css(over(fg, bg)), css(bg), own ? 10 : 4.5, own ? 'body' : 'text', own ? areaOf(blk) : '']);
  }
  // figure text: its fill against the shapes under its centre, over the figure's own background
  for (const tx of document.querySelectorAll('main svg text')) {
    const r = tx.getBoundingClientRect();
    if (r.width < 1) continue;
    const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    const svg = tx.ownerSVGElement;
    let bg = bgUnder(svg);
    for (const sh of svg.querySelectorAll('rect, path, circle, ellipse, polygon')) {
      if (!(sh.compareDocumentPosition(tx) & Node.DOCUMENT_POSITION_FOLLOWING) || sh.contains(tx)) continue;
      const cs = getComputedStyle(sh);
      if (cs.fill === 'none') continue;
      const b = sh.getBoundingClientRect();
      if (cx < b.left || cx > b.right || cy < b.top || cy > b.bottom) continue;
      const f = parse(cs.fill); f[3] *= Number(cs.fillOpacity) * Number(cs.opacity);
      bg = over(f, bg);
    }
    const cs = getComputedStyle(tx);
    const fg = parse(cs.fill); fg[3] *= Number(cs.fillOpacity) * Number(cs.opacity);
    rows.push([name(tx) + ' "' + tx.textContent.trim().slice(0, 18) + '"', css(over(fg, bg)), css(bg), 4.5, 'figure', '']);
  }
  return rows;
})()`;

async function matrixState(run, p, page, theme, state, seenRows, areas) {
  const rows = await p.evaluate(PAGE_TEXT_COLOURS);
  for (const [sel, fg, bg, need, role, area] of rows) {
    // threshold and role are part of the key: a weaker measurement of the same element must not hide a stronger one
    const key = `${page}|${theme}|${sel}|${fg}|${bg}|${need}|${role}`;
    if (seenRows.has(key)) continue;
    seenRows.add(key);
    if (role === 'body') areas.set(area, (areas.get(area) || 0) + 1);
    const c = contrast(fg, bg);
    expect(c >= need, `${run}: contrast: ${page}, ${theme}, [${state}] ${role} ${sel}: ${fg} on ${bg} = ${c.toFixed(2)}, needs ${need}`);
  }
  return rows.length;
}

// Each page in both themes, with the states of the brief opened one at a time before measuring.
async function contrastMatrix(run, p, url, pages, requiredAreas = []) {
  let measured = 0;
  const seen = new Set();
  const areas = new Map(); // reading-column area -> body rows measured at 10:1
  for (const theme of ['light', 'dark']) {
    await p.emulateMedia({ colorScheme: theme });
    for (const page of pages) {
      const isHome = page === 'index.html', isSources = page.startsWith('sources');
      const open = async () => { await p.setViewportSize({ width: 1280, height: 900 }); await p.goto(url(page)); };
      const m = state => matrixState(run, p, page, theme, state, seen, areas);
      await open();
      measured += await m('initial');
      if (await p.locator('details.deep').count()) {
        await p.locator('details.deep').evaluateAll(ds => ds.forEach(d => { d.open = true; }));
        measured += await m('deep-dive open');
        await open();
      }
      if (isHome) {
        await p.locator('#map details.chip, #map details').evaluateAll(ds => ds.forEach(d => { d.open = true; }));
        measured += await m('every map card open');
        await open();
        await p.locator('#f-ignore button').first().click();
        measured += await m('ignore filter');
        await p.locator('#f-matrix').click();
        measured += await m('matrix filter');
        await p.locator('#f-question button').first().click();
        await p.locator('#map details').evaluateAll(ds => ds.forEach(d => { d.open = true; }));
        measured += await m('question filter, cards open');
      } else if (isSources) {
        await p.locator('#f-topic button[data-topic]:not([data-topic="all"])').first().click();
        measured += await m('topic filter');
      } else {
        const r = p.locator('#code [role="tab"][data-lang="r"]');
        if (await r.count()) { await r.click(); measured += await m('R tab'); await p.locator('#code [role="tab"][data-lang="python"]').click(); }
        for (const sel of ['main a.cite', 'section.finance a.cite']) {
          if (!await p.locator(sel).count()) continue;
          await p.locator(sel).first().scrollIntoViewIfNeeded();
          await p.locator(sel).first().click();
          await p.keyboard.press('Tab');
          measured += await m(`citation popover (${sel})`);
          await p.keyboard.press('Escape');
        }
        if (await p.locator('section.finance').count()) {
          // keyboard focus on a link inside the finance block: the ring against the block surface
          const info = await p.evaluate(() => {
            const a = document.querySelector('section.finance a[href]:not(.cite)') || document.querySelector('section.finance a.cite');
            if (!a) return null;
            a.scrollIntoView({ block: 'center' });
            return true;
          });
          if (info) {
            const ring = await p.evaluate(() => {
              const a = document.querySelector('section.finance a[href]:not(.cite)') || document.querySelector('section.finance a.cite');
              a.focus({ focusVisible: true });
              const f = document.querySelector('section.finance');
              return [getComputedStyle(a).outlineColor, getComputedStyle(a).outlineStyle, getComputedStyle(f).backgroundColor];
            });
            if (ring[1] !== 'none') {
              const c = contrast(ring[0], ring[2]);
              expect(c >= 4.5, `${run}: contrast: ${page}, ${theme}, [finance focus ring] ${ring[0]} on ${ring[2]} = ${c.toFixed(2)}, needs 4.5`);
            } else expect(false, `${run}: contrast: ${page}, ${theme}: finance link shows no focus ring`);
          }
        }
      }
      await open();
      await p.locator('#q').fill('e');
      await p.waitForTimeout(250);
      measured += await m('search results');
      await p.keyboard.press('Escape');
      await p.setViewportSize({ width: 820, height: 900 });
      await p.goto(url(page));
      await p.locator('header.top button.menu').click();
      await p.waitForTimeout(400);
      measured += await m('drawer open');
    }
  }
  await p.emulateMedia({ colorScheme: null });
  console.log(`contrast: ${run}: ${measured} text rows measured`);
  expect(measured > 200, `${run}: contrast: only ${measured} text rows measured, the matrix is not reaching the pages`);
  for (const area of requiredAreas) expect((areas.get(area) || 0) > 0, `${run}: contrast: no body row measured at 10:1 in the ${area} area`);
  console.log(`contrast: ${run}: body rows at 10:1 by area: ${[...areas].map(([a, n]) => `${a} ${n}`).join(', ')}`);
}

// Widths 1440, 1280, 820, 375, both themes, every page: no page-level horizontal scroll, and no clipped
// chip, sector card or sector question link.
async function widthChecks(run, p, url, pages) {
  for (const theme of ['light', 'dark']) {
    await p.emulateMedia({ colorScheme: theme });
    for (const width of [1440, 1280, 820, 375]) {
      await p.setViewportSize({ width, height: 900 });
      for (const page of pages) {
        await p.goto(url(page));
        if (page === 'index.html') await p.locator('#map details').evaluateAll(ds => ds.forEach(d => { d.open = true; }));
        const r = await p.evaluate(() => ({
          doc: document.documentElement.scrollWidth, view: document.documentElement.clientWidth,
          // inline boxes report clientWidth 0, so only boxes that lay out their content are compared
          clipped: [...document.querySelectorAll('summary.chip, .sector, a.q')].filter(e => getComputedStyle(e).display !== 'inline' && e.scrollWidth > e.clientWidth)
            .map(e => `${e.tagName.toLowerCase()}.${e.className} "${e.textContent.trim().slice(0, 24)}" ${e.scrollWidth}>${e.clientWidth}`),
          // static figures are drawn in viewBox units: a label must not be blown up past 16 px on screen
          // (the mockup's figure labels are 12.5 to 13 px, design 6: labels keep their size)
          bigText: [...document.querySelectorAll('figure svg[viewBox]')].flatMap(s => {
            const k = s.getBoundingClientRect().width / s.viewBox.baseVal.width;
            return [...s.querySelectorAll('text')].map(t => parseFloat(getComputedStyle(t).fontSize) * k)
              .filter(px => px > 16).map(px => `${s.querySelector('title')?.textContent.slice(0, 24)} ${px.toFixed(1)} px`).slice(0, 1);
          }),
        }));
        expect(r.doc <= width, `${run}: widths: ${page}, ${theme}, ${width} px: scrollWidth ${r.doc} exceeds the viewport`);
        expect(r.clipped.length === 0, `${run}: widths: ${page}, ${theme}, ${width} px: clipped ${r.clipped.join('; ')}`);
        expect(r.bigText.length === 0, `${run}: widths: ${page}, ${theme}, ${width} px: figure text too large: ${r.bigText.join('; ')}`);
      }
    }
  }
  await p.emulateMedia({ colorScheme: null });
}

// No JavaScript: the page reads. Both code blocks visible, a citation reaches its source entry.
async function noJsChecks(run, browserContext, url) {
  const p = await browserContext.newPage();
  await p.goto(url('alpha/index.html'));
  expect(await p.locator('#code pre[data-lang="python"]').isVisible() && await p.locator('#code pre[data-lang="r"]').isVisible(), `${run}: no JS: both code blocks must be visible`);
  expect(await p.locator('section.finance').isVisible() && await p.locator('section.measure').isVisible(), `${run}: no JS: finance and measure card visible`);
  expect((await p.locator('main details.deep').textContent()).includes('wavefront order'), `${run}: no JS: deep-dive text not in the page`);
  await p.locator('main details.deep summary').click();
  expect(await p.locator('main details.deep').evaluate(e => e.open), `${run}: no JS: deep-dive summary did not open it`);
  await Promise.all([p.waitForURL(u => u.hash === '#src-sakoe78'), p.locator('a.cite').first().click()]);
  expect(await p.locator('section.lsrc li#src-sakoe78').isVisible(), `${run}: no JS: source entry not visible after the citation click`);
  await p.setViewportSize({ width: 390, height: 800 });
  expect(!(await p.locator('button.menu').isVisible()) && await p.locator('nav#contents a[href$="gamma/index.html"]').isVisible()
    && await p.locator('nav#contents a[href$="index.html#map"]').isVisible(), `${run}: no JS at 390 px: contents links not visible`);
  // the map cards are native disclosures: they open without JavaScript, the script-only filters are hidden
  await p.goto(url('index.html'));
  await p.locator('#item-agglomerative summary').click();
  expect((await p.locator('#item-agglomerative').innerText()).includes('single, complete, average linkage'), `${run}: no JS: card did not open`);
  expect(!(await p.locator('#f-ignore').isVisible()), `${run}: no JS: filters are shown but cannot work`);
  await p.close();
}

// Expected state of a live figure from tests/live_expect.py (data file + reference package + the contract),
// never from a built figure. Returns the parsed list, one object per requested [pairIndex, w] state.
function liveExpect(dataFile, states) {
  const args = ['run', 'python', 'tests/live_expect.py', dataFile, ...states.flatMap(([pair, w]) => [String(pair), String(w)])];
  return JSON.parse(execFileSync('uv', args, { cwd: root, encoding: 'utf8' }));
}

// Read the geometry of one live figure through its data-part markers and compare it with `expected`
// (one object of liveExpect). `figure` is a locator of the <figure> or of its <svg>. Checks: the root
// markers, the band cells (position, count, opacity), the path through the cell centres, the series
// rows affine in the data of the named pair on one shared scale, the links matched to series points,
// and the distances in <desc>. Failures are pushed to `failures` with the label.
async function liveGeometry(p, figure, expected, label) {
  const svg = figure.locator('svg').first();
  const g = await svg.evaluate(el => {
    const pts = s => s.getAttribute('points').trim().split(/\s+/).map(t => t.split(',').map(Number));
    const part = k => [...el.querySelectorAll(`[data-part="${k}"]`)];
    const grid = part('grid');
    const num = (e, a) => Number(e.getAttribute(a));
    return {
      pair: el.getAttribute('data-pair'), w: el.getAttribute('data-w'),
      desc: el.querySelector('desc')?.textContent ?? '',
      grid: grid.map(r => ({ x: num(r, 'x'), y: num(r, 'y'), size: num(r, 'width'), h: num(r, 'height') })),
      cells: part('cell').map(r => ({ x: num(r, 'x'), y: num(r, 'y'), w: num(r, 'width'), h: num(r, 'height'), op: num(r, 'opacity') })),
      paths: part('path').map(pts), a: part('series-a').map(pts), b: part('series-b').map(pts),
      links: part('link').map(l => [num(l, 'x1'), num(l, 'y1'), num(l, 'x2'), num(l, 'y2')]),
    };
  });
  const bad = m => failures.push(`${label}: ${m}`);
  const near = (x, y, tol) => Math.abs(x - y) <= tol;
  const [na, nb] = expected.pair;
  const n = expected.n;
  if (g.pair !== `${na}-${nb}`) bad(`data-pair is ${g.pair}, expected ${na}-${nb}`);
  if (g.w !== String(expected.w ?? 'none')) bad(`data-w is ${g.w}, expected ${expected.w ?? 'none'}`);
  if (!g.desc.includes(`Euclidean distance ${expected.euclidean}, DTW distance ${expected.dtw}`) || !g.desc.includes(na) || !g.desc.includes(nb)) {
    bad(`desc does not state the pair and "Euclidean distance ${expected.euclidean}, DTW distance ${expected.dtw}": ${g.desc.slice(0, 100)}`);
  }
  if (g.grid.length !== 1 || g.paths.length !== 1 || g.a.length !== 1 || g.b.length !== 1) { bad('markers: need one grid, path, series-a and series-b'); return; }
  const { x: gx, y: gy, size } = g.grid[0];
  const cell = size / n;
  // band cells: set of "i,j" with opacity
  if (g.cells.length !== expected.cells.length) bad(`${g.cells.length} band cells, expected ${expected.cells.length}`);
  const want = new Map(expected.cells.map(([i, j], k) => [`${i},${j}`, expected.opacity[k]]));
  const seen = new Set();
  for (const c of g.cells) {
    if (!near(c.w, cell, 0.1) || !near(c.h, cell, 0.1)) bad(`cell size ${c.w}x${c.h}, expected ${cell.toFixed(2)}`);
    const j = Math.round((c.x - gx) / cell), i = Math.round((gy + size - c.y) / cell) - 1;
    if (!near(c.x, gx + j * cell, 0.1) || !near(c.y, gy + size - (i + 1) * cell, 0.1)) bad(`cell at ${c.x},${c.y} is not on the grid`);
    const key = `${i},${j}`;
    if (!want.has(key)) bad(`unexpected band cell (${key})`);
    else if (!near(c.op, want.get(key), 0.0051)) bad(`cell (${key}) opacity ${c.op}, expected ${want.get(key)}`);
    seen.add(key);
  }
  for (const key of want.keys()) if (!seen.has(key)) bad(`band cell (${key}) missing`);
  // path through the cell centres
  const path = g.paths[0].map(([x, y]) => [Math.round((gy + size - y) / cell - 0.5), Math.round((x - gx) / cell - 0.5)]);
  g.paths[0].forEach(([x, y], k) => {
    const [i, j] = path[k];
    if (!near(x, gx + (j + 0.5) * cell, 0.1) || !near(y, gy + size - (i + 0.5) * cell, 0.1)) bad(`path point ${k} is not on a cell centre`);
  });
  if (JSON.stringify(path) !== JSON.stringify(expected.path)) bad(`path ${JSON.stringify(path)}, expected ${JSON.stringify(expected.path)}`);
  // series: one point per sample, x growing, y decreasing affine in the value, one shared scale, A above B
  const rows = [[na, g.a[0]], [nb, g.b[0]]];
  const slopes = [];
  for (const [name, pts] of rows) {
    const v = expected.series[name];
    if (pts.length !== n) { bad(`${name}: ${pts.length} points, expected ${n}`); continue; }
    for (let k = 1; k < n; k++) if (!(pts[k][0] > pts[k - 1][0])) bad(`${name}: x does not grow at sample ${k}`);
    const vmin = Math.min(...v), vmax = Math.max(...v);
    const kmin = v.indexOf(vmin), kmax = v.indexOf(vmax);
    if (vmax > vmin) {
      const slope = (pts[kmax][1] - pts[kmin][1]) / (vmax - vmin);
      slopes.push(slope);
      if (!(slope < 0)) bad(`${name}: y does not decrease with the value`);
      v.forEach((val, k) => { if (!near(pts[k][1], pts[kmin][1] + slope * (val - vmin), 0.3)) bad(`${name}: sample ${k} is not affine in its value`); });
    } else if (!pts.every(q => near(q[1], pts[0][1], 0.1))) bad(`${name}: constant series is not flat`);
  }
  if (slopes.length === 2 && !near(slopes[0], slopes[1], Math.abs(slopes[0]) * 0.08)) bad(`the two series do not share a value scale (${slopes})`);
  if (g.a[0].length === n && g.b[0].length === n && Math.max(...g.a[0].map(q => q[1])) >= Math.min(...g.b[0].map(q => q[1]))) bad('series A is not above series B');
  // links: the kept path steps, from point i of A to point j of B
  const wantLinks = expected.links.map(k => expected.path[k]);
  if (g.links.length !== wantLinks.length) bad(`${g.links.length} links, expected ${wantLinks.length}`);
  const found = g.links.map(([x1, y1, x2, y2]) => {
    const i = g.a[0].findIndex(q => near(q[0], x1, 0.15) && near(q[1], y1, 0.15));
    const j = g.b[0].findIndex(q => near(q[0], x2, 0.15) && near(q[1], y2, 0.15));
    return [i, j];
  });
  if (JSON.stringify(found) !== JSON.stringify(wantLinks)) bad(`links ${JSON.stringify(found)}, expected ${JSON.stringify(wantLinks)}`);
}

// Gamma holds the two live figures (alpha keeps its single static one). Static SVG with JavaScript off,
// compared with the expected state of the initial pair and window, and with the hand-computed distances.
async function liveStaticChecks(run, browserContext, url) {
  const p = await browserContext.newPage();
  await p.goto(url('gamma/index.html'));
  const figs = p.locator('main figure[data-live="dtw"]');
  expect(await figs.count() === 2, `${run}: gamma needs two live figures, has ${await figs.count()}`);
  expect(await count(p, 'main figure') === 2 && await count(p, 'main figure script.live-data') === 2, `${run}: gamma figure and data script count`);
  expect(await count(p, 'main figure input, main figure button, main figure .live-ctl, main figure .live-out') === 0, `${run}: no JS: live figures show controls or a readout`);
  const dir = 'tests/fixtures/smoke/figures/';
  const cases = [['live-a', 0, 1, 7, '1.41', '1.00'], ['live-b', 0, 1, 10, '1.00', '0.00']];
  for (const [k, [name, pair, w, ncells, euclid, dist]] of cases.entries()) {
    const [exp] = liveExpect(dir + name + '.live.json', [[pair, w]]);
    expect(exp.cells.length === ncells && exp.euclidean === euclid && exp.dtw === dist,
      `${run}: ${name} expected state differs from the hand computation: ${exp.cells.length} cells, ${exp.euclidean}, ${exp.dtw}`);
    await liveGeometry(p, figs.nth(k), exp, `${run}: ${name} static`);
  }
  await p.close();
}

// --- The live figures on the smoke gamma page (the real lesson is checked with its own figure later). ---
const LIVE_DIR = 'tests/fixtures/smoke/figures/';
const LIVE_FILES = ['live-a', 'live-b'];
const figureClassNames = () => {
  const css = fs.readFileSync(path.join(root, 'site', 'theme.css'), 'utf8');
  const block = css.slice(css.indexOf('/* figure-classes:start */'), css.indexOf('/* figure-classes:end */'));
  return new Set([...block.matchAll(/figure svg \.([a-z-]+)/g)].map(m => m[1]));
};
// Words for a window of w samples at 30-minute sampling (the smoke data), written here from the input contract.
const winWords = w => `w = ${w} sample${w === 1 ? '' : 's'} (${w * 30 < 60 ? w * 30 + ' min' : (w * 30 / 60) + ' h'})`;
const readoutOf = e => `${e.pair[0]} and ${e.pair[1]}, ${e.w === null ? 'no window' : winWords(e.w)}: DTW ${e.dtw}, Euclidean ${e.euclidean}`;

// Every state the checks can reach, from tests/live_expect.py in one call per file.
function liveTable() {
  const table = {};
  const states = { 'live-a': [[0, 'none'], ...[0, 1, 2].map(w => [0, w])], 'live-b': [0, 1].flatMap(pr => [0, 1, 2, 3].map(w => [pr, w])) };
  for (const name of LIVE_FILES) {
    table[name] = {};
    liveExpect(LIVE_DIR + name + '.live.json', states[name]).forEach((e, k) => { table[name][`${states[name][k][0]},${states[name][k][1]}`] = e; });
  }
  return table;
}

const liveFig = (p, k) => p.locator('main figure[data-live="dtw"]').nth(k);
const readoutText = (p, k) => liveFig(p, k).locator('.live-out').innerText({ timeout: 1500 }).catch(() => '(no readout)');
// What a figure shows: checked inputs, path points and readout. Used to prove the other figure did not move.
const liveSnapshot = (p, k) => liveFig(p, k).evaluate(f => ({
  checked: [...f.querySelectorAll('input')].map(i => (i.type === 'range' ? i.value : i.checked) + (i.disabled ? 'd' : '')),
  path: f.querySelector('[data-part="path"]')?.getAttribute('points'), out: f.querySelector('.live-out')?.textContent,
}));
// Check figure k against state `e` (an object of liveTable) and its readout line.
async function liveState(run, p, k, e, label) {
  await liveGeometry(p, liveFig(p, k), e, `${run}: ${label}`);
  const out = await readoutText(p, k);
  expect(out === readoutOf(e), `${run}: ${label}: readout "${out}", expected "${readoutOf(e)}"`);
}
const activeIs = (p, sel) => p.evaluate(s => document.activeElement.matches(s), sel);

async function liveChecks(run, url, isLocal) {
  const T = liveTable();
  const A = T['live-a'], B = T['live-b'];
  const OPEN = { viewport: { width: 1280, height: 900 }, colorScheme: 'light' };
  let ctx = await context(run, OPEN, isLocal);
  let p = await ctx.newPage();
  await p.goto(url('gamma/index.html'));
  await p.waitForSelector('main figure[data-live] .live-out', { timeout: 3000 }).catch(() => failures.push(`${run}: no live readout appeared`));

  // initial agreement, the figure classes, no colour attributes
  await liveState(run, p, 0, A['0,1'], 'live-a initial');
  await liveState(run, p, 1, B['0,1'], 'live-b initial');
  expect(await readoutText(p, 0) === 'aa and ab, w = 1 sample (30 min): DTW 1.00, Euclidean 1.41', `${run}: live-a readout text`);
  expect(await readoutText(p, 1) === 'ba and bb, w = 1 sample (30 min): DTW 0.00, Euclidean 1.00', `${run}: live-b readout text`);
  const allowed = figureClassNames();
  for (const k of [0, 1]) {
    const bad = await liveFig(p, k).locator('svg').first().evaluate((svg, ok) => {
      const out = [];
      for (const el of [svg, ...svg.querySelectorAll('*')]) {
        for (const c of el.classList) if (!ok.includes(c) && !(el === svg && c === 'live')) out.push(`${el.tagName}.${c}`);
        for (const a of ['fill', 'stroke', 'style']) if (el.hasAttribute(a)) out.push(`${el.tagName}[${a}]`);
      }
      return out;
    }, [...allowed]);
    expect(bad.length === 0, `${run}: live SVG ${k} uses classes or attributes outside the figure rules: ${bad.slice(0, 5)}`);
    expect(await liveFig(p, k).locator('svg.live').count() === 1 && await liveFig(p, k).locator('svg').count() === 1, `${run}: live figure ${k} needs exactly one svg.live`);
    expect(await liveFig(p, k).locator('svg.live').evaluate(s => getComputedStyle(s).maxWidth) === 'none', `${run}: live SVG ${k} keeps the 360 px cap`);
  }
  expect(await liveFig(p, 0).locator('fieldset').count() === 0, `${run}: live-a has one pair and must show no pair group`);
  expect(await liveFig(p, 1).locator('fieldset legend').innerText() === 'Pair', `${run}: live-b pair group legend`);
  const radioNames = await p.locator('main figure[data-live] input[type=radio]').evaluateAll(rs => rs.map(r => [r.name, [...document.querySelectorAll('figure[data-live]')].indexOf(r.closest('figure'))]));
  expect(radioNames.length === 2 && radioNames.every(([n, f]) => n === 'live-2-pair' && f === 1), `${run}: radio names ${JSON.stringify(radioNames)}, expected only live-2-pair on live-b`);
  expect(await p.locator('figure[data-live]').evaluateAll(fs => new Set(fs.flatMap(f => [...new Set([...f.querySelectorAll('input[type=radio]')].map(r => r.name))])).size === fs.filter(f => f.querySelector('input[type=radio]')).length), `${run}: a radio name is shared across figures`);

  // keyboard only on live-b: pair group, then the slider, then Reset
  const b = liveFig(p, 1);
  // Review Focus 4: live-a (checked inputs, path points, readout) is the same after every live-b step
  const a0 = await liveSnapshot(p, 0);
  const step = async (e, label) => {
    await liveState(run, p, 1, e, label);
    expect(JSON.stringify(await liveSnapshot(p, 0)) === JSON.stringify(a0), `${run}: live-a changed after live-b step: ${label}`);
  };
  await b.locator('svg').click({ position: { x: 5, y: 5 } });
  await p.keyboard.press('Tab');
  expect(await activeIs(p, 'input[type=radio]:checked') && await p.evaluate(() => document.activeElement.closest('figure') === document.querySelectorAll('figure[data-live]')[1]), `${run}: Tab did not land on the checked pair radio of live-b`);
  await p.keyboard.press('ArrowDown');
  expect(await b.locator('input[type=radio]:checked').evaluate(r => r.labels[0].textContent.trim()) === 'ba and bc', `${run}: ArrowDown did not check "ba and bc"`);
  await step(B['1,1'], 'live-b ba and bc, w=1');
  await p.keyboard.press('Tab');
  expect(await activeIs(p, 'input[type=range]'), `${run}: second Tab did not reach the slider`);
  for (const w of [2, 3]) { await p.keyboard.press('ArrowRight'); await step(B[`1,${w}`], `live-b ba and bc, w=${w}`); }
  for (const w of [2, 1, 0]) { await p.keyboard.press('ArrowLeft'); await step(B[`1,${w}`], `live-b ba and bc, w=${w}`); }
  await p.keyboard.press('ArrowRight');
  await p.keyboard.press('Tab');
  expect(await activeIs(p, 'button'), `${run}: Tab after the slider did not reach Reset`);
  await p.keyboard.press('Enter');
  await step(B['0,1'], 'live-b after Reset');
  expect(await b.locator('input[type=range]').inputValue() === '1' && await b.locator('input[type=radio]:checked').evaluate(r => r.labels[0].textContent.trim()) === 'ba and bb', `${run}: Reset did not restore the pair and window controls`);

  // keyboard only on live-a: slider, No window (Space), retained value, Reset
  const a = liveFig(p, 0);
  await a.locator('svg').click({ position: { x: 5, y: 5 } });
  await p.keyboard.press('Tab');
  expect(await activeIs(p, 'input[type=range]'), `${run}: live-a: first Tab did not reach the slider`);
  await p.keyboard.press('ArrowRight');
  await liveState(run, p, 0, A['0,2'], 'live-a w=2');
  await p.keyboard.press('Tab');
  expect(await activeIs(p, 'input[type=checkbox]'), `${run}: live-a: Tab did not reach No window`);
  expect((await a.locator('input[type=checkbox]').evaluate(c => c.labels[0].textContent.trim())) === 'No window', `${run}: live-a checkbox label`);
  await p.keyboard.press('Space');
  expect(await a.locator('input[type=range]').isDisabled(), `${run}: live-a: No window did not disable the slider`);
  await liveState(run, p, 0, A['0,none'], 'live-a no window');
  expect((await readoutText(p, 0)).startsWith('aa and ab, no window: DTW '), `${run}: live-a readout form with no window`);
  await p.keyboard.press('Space');
  expect(await a.locator('input[type=range]').isEnabled() && await a.locator('input[type=range]').inputValue() === '2', `${run}: live-a: the slider did not keep its value`);
  await liveState(run, p, 0, A['0,2'], 'live-a unchecked, retained w=2');
  await p.keyboard.press('Tab');
  await p.keyboard.press('Enter');
  await liveState(run, p, 0, A['0,1'], 'live-a after Reset');
  expect(await a.locator('input[type=checkbox]').isChecked() === false, `${run}: live-a: Reset left No window checked`);
  await a.locator('input[type=checkbox]').check();
  await a.locator('button').click();
  await liveState(run, p, 0, A['0,1'], 'live-a Reset from no window');
  expect(await a.locator('input[type=range]').isEnabled(), `${run}: live-a: Reset from no window left the slider disabled`);

  // Review Focus 3: width. live-b at ba and bc, w = 2, from 1440 to 375 px
  await p.setViewportSize({ width: 1440, height: 900 });
  await b.locator('input[type=radio]').nth(1).check();
  await b.locator('input[type=range]').fill('2');
  await p.waitForTimeout(500);
  await liveState(run, p, 1, B['1,2'], 'live-b before resize');
  const widths = () => b.evaluate(f => {
    const cs = getComputedStyle(f), svg = f.querySelector('svg');
    return { content: f.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight), rendered: svg.getBoundingClientRect().width, viewBox: svg.viewBox.baseVal.width };
  });
  let m = await widths();
  expect(Math.abs(m.rendered - m.content) <= 1 && Math.abs(m.viewBox - m.content) <= 1, `${run}: live-b at 1440: content ${m.content}, rendered ${m.rendered}, viewBox ${m.viewBox}`);
  await p.setViewportSize({ width: 375, height: 812 });
  await p.waitForTimeout(500);
  m = await widths();
  expect(Math.abs(m.rendered - m.content) <= 1 && Math.abs(m.viewBox - m.content) <= 1, `${run}: live-b at 375: content ${m.content}, rendered ${m.rendered}, viewBox ${m.viewBox}`);
  expect(m.content < 340, `${run}: live-b at 375: content width ${m.content} is not the phone width`);
  await liveState(run, p, 1, B['1,2'], 'live-b after resize');
  expect(await p.evaluate(() => document.documentElement.scrollWidth) <= 375, `${run}: gamma overflows at 375 px with the live figures`);
  await ctx.close();

  // focus ring on every control, both themes
  for (const scheme of ['light', 'dark']) {
    ctx = await context(run, { ...OPEN, colorScheme: scheme }, isLocal);
    p = await ctx.newPage();
    await p.goto(url('gamma/index.html'));
    await p.waitForSelector('main figure[data-live] .live-out', { timeout: 3000 }).catch(() => failures.push(`${run}: no live readout appeared`));
    for (const k of [0, 1]) {
      const n = await liveFig(p, k).locator('input, button').count();
      expect(n >= 3, `${run}: live figure ${k} has ${n} controls`);
      for (let c = 0; c < n; c++) {
        const ring = await liveFig(p, k).locator('input, button').nth(c).evaluate(el => {
          el.focus({ focusVisible: true });
          const cs = getComputedStyle(el);
          return [cs.outlineWidth, cs.outlineStyle, cs.outlineColor, getComputedStyle(el.closest('figure')).backgroundColor, `${el.tagName}[${el.type}]`];
        });
        const ok = ring[1] !== 'none' && parseFloat(ring[0]) >= 2 && contrast(ring[2], ring[3]) >= 4.5;
        expect(ok, `${run}: ${scheme}: live figure ${k} ${ring[4]} focus ring ${ring[0]} ${ring[1]} ${ring[2]} on ${ring[3]} = ${contrast(ring[2], ring[3]).toFixed(2)}`);
      }
    }
    await ctx.close();
  }

  // Review Focus 2, blocked: no live.js, then no kernels.js. The static figures stand alone.
  for (const blocked of ['assets/live.js', 'assets/kernels.js']) {
    // live.js blocked: only that URL is exempt. kernels.js blocked: also the safe-failure "live figure:" errors, one per figure.
    ctx = await failureContext(run, OPEN, isLocal, blocked === 'assets/live.js' ? { blocked } : { blocked, liveErrors: true });
    p = await ctx.newPage();
    const seen = [];
    p.on('console', m => m.type() === 'error' && m.text().startsWith('live figure:') && seen.push(m.text()));
    await p.goto(url('gamma/index.html'));
    await p.waitForTimeout(400);
    expect(await count(p, 'main figure figcaption') === 2, `${run}: ${blocked} blocked: captions missing`);
    expect(await count(p, 'main figure input, main figure button, main figure .live-ctl, main figure .live-out') === 0, `${run}: ${blocked} blocked: controls or readout shown`);
    expect(seen.length === (blocked === 'assets/kernels.js' ? 2 : 0), `${run}: ${blocked} blocked: ${seen.length} "live figure:" errors, expected ${blocked === 'assets/kernels.js' ? 2 : 0}`);
    for (const k of [0, 1]) {
      expect(await liveFig(p, k).locator('svg').first().isVisible(), `${run}: ${blocked} blocked: static SVG ${k} not visible`);
      await liveGeometry(p, liveFig(p, k), (k === 0 ? A : B)['0,1'], `${run}: ${blocked} blocked: figure ${k}`);
    }
    await ctx.close();
  }

  // Review Focus 2, after activation: dtwPath throws for the 4-sample series of live-b only (the kernels are shared)
  ctx = await failureContext(run, OPEN, isLocal, { liveErrors: true });
  const errors = [];
  p = await ctx.newPage();
  p.on('console', mm => mm.type() === 'error' && errors.push(mm.text()));
  await p.goto(url('gamma/index.html'));
  await p.waitForSelector('main figure[data-live] .live-out', { timeout: 3000 }).catch(() => failures.push(`${run}: no live readout appeared`));
  await liveFig(p, 1).locator('input[type=radio]').nth(1).check();
  await liveState(run, p, 1, B['1,1'], 'live-b before the failure');
  await p.evaluate(() => { const real = window.TSC_KERNELS.dtwPath; window.TSC_KERNELS.dtwPath = (x, y, w) => { if (x.length === 4) throw new Error('boom'); return real(x, y, w); }; });
  await liveFig(p, 1).locator('input[type=range]').fill('2');
  await liveGeometry(p, liveFig(p, 1), B['0,1'], `${run}: live-b after the failure`);
  expect(await count(p, 'main figure:nth-of-type(2) input, main figure:nth-of-type(2) button, main figure:nth-of-type(2) .live-ctl') === 0 || await liveFig(p, 1).locator('input, button, .live-ctl').count() === 0, `${run}: live-b kept its controls after the failure`);
  expect(await liveFig(p, 1).locator('.live-out').innerText() === 'The interactive figure stopped. Shown: the initial setting, ba and bb, w = 1 sample (30 min).', `${run}: live-b failure readout: ${await liveFig(p, 1).locator('.live-out').innerText()}`);
  expect(errors.filter(t => t.startsWith('live figure:')).length === 1 && errors.length === 1, `${run}: failure console errors: ${JSON.stringify(errors)}`);
  await liveFig(p, 0).locator('input[type=range]').fill('2');
  await liveState(run, p, 0, A['0,2'], 'live-a after live-b failed');
  await ctx.close();
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
    let ctx = await context(run.name, { viewport: { width: 1280, height: 900 }, colorScheme: 'light', ...(run.http ? { permissions: ['clipboard-read', 'clipboard-write'] } : {}) }, run.isLocal);
    let p = await ctx.newPage();
    if (smoke) await smokeChecks(run.name, p, run.url);
    if (smoke) await homeChecks(run.name, p, run.url);
    else await previewChecks(run.name, p, run.url, contentDir);
    if (smoke) await layoutChecks(run.name, p, run.url);
    if (smoke) {
      await drawerChecks(run.name, p, run.url);
      await spyChecks(run.name, p, run.url);
      await codeChecks(run.name, p, run.url, run.http);
      await mapChecks(run.name, p, run.url);
      await sourcesChecks(run.name, p, run.url);
      await searchChecks(run.name, p, run.url);
    } else { await contentBehaviour(run.name, p, run.url, lessons); await previewSearchChecks(run.name, p, run.url); }
    await navigation(run.name, p, run.url, ids);
    if (!run.http) {
      const pages = ['index.html', 'sources/index.html', ...lessons];
      await contrastMatrix(run.name, p, run.url, pages, smoke ? ['content', 'oneline', 'mistake', 'finance', 'measure', 'code'] : ['content', 'oneline', 'mistake']);
      await widthChecks(run.name, p, run.url, pages);
    }

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
      await liveStaticChecks(run.name, ctx, run.url);
      await ctx.close();
      await liveChecks(run.name, run.url, run.isLocal);
    }

    // dark system preference with no stored choice: pages start dark
    ctx = await context(run.name, { viewport: { width: 1280, height: 900 }, colorScheme: 'dark' }, run.isLocal);
    p = await ctx.newPage();
    for (const rel of ['index.html', 'sources/index.html', ...lessons]) {
      await p.goto(run.url(rel));
      expect(await stored(p) === null, `${run.name}: storage not empty in a fresh context`);
      expect(await theme(p) === null && await bodyBg(p) === DARK_BG, `${run.name}: ${rel} does not start dark with a dark system preference`);
    }
    await ctx.close();

    // phone width: no horizontal overflow
    ctx = await context(run.name, { viewport: { width: 375, height: 812 }, colorScheme: 'light' }, run.isLocal);
    p = await ctx.newPage();
    for (const rel of ['index.html', 'sources/index.html', ...lessons]) {
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
