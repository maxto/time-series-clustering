// The map of the field (home): filters that highlight items, and links that open an item card.
// Data comes from the inline JSON #atlas-data. Plain script, works from file://.
(function () {
  'use strict';
  var doc = document;
  var dataEl = doc.getElementById('atlas-data');
  var ignoreBox = doc.getElementById('f-ignore');
  var matrixBtn = doc.getElementById('f-matrix');
  var questionBox = doc.getElementById('f-question');
  var statusEl = doc.getElementById('f-status');
  if (!dataEl || !ignoreBox || !matrixBtn || !questionBox || !statusEl) return;
  var data = JSON.parse(dataEl.textContent);
  var items = Array.prototype.slice.call(doc.querySelectorAll('#map li.item[data-item]'));
  var total = items.length;
  var tags = [];            // selected "ignore" tags, in the order picked
  var matrix = false;
  var question = null;

  function el(tag, cls, text) {
    var n = doc.createElement(tag);
    if (cls) n.className = cls;
    if (text) n.textContent = text;
    return n;
  }
  function pressed(btn, on) { btn.setAttribute('aria-pressed', on ? 'true' : 'false'); }
  function list(words) {
    return words.length < 2 ? words.join('') : words.slice(0, -1).join(', ') + ' and ' + words[words.length - 1];
  }
  function plural(n, one, many) { return n + ' ' + (n === 1 ? one : many); }
  function has(arr, tag) { return arr.some(function (x) { return x.tag === tag; }); }
  function condOf(arr, tag) { var m = arr.filter(function (x) { return x.tag === tag; })[0]; return m ? m.cond : ''; }
  function label(tag) { return ignoreBox.querySelector('button[data-tag="' + tag + '"]').textContent.trim(); }

  function clearMarks() {
    items.forEach(function (li) {
      li.removeAttribute('data-state');
      Array.prototype.forEach.call(li.querySelectorAll('.fcond, .why'), function (n) { n.parentNode.removeChild(n); });
    });
  }
  function addCond(li, text) {
    if (!text) return;
    li.querySelector('summary.chip').appendChild(el('span', 'cond fcond', text));
  }

  function render() {
    clearMarks();
    Array.prototype.forEach.call(ignoreBox.querySelectorAll('button[data-tag]'), function (b) { pressed(b, tags.indexOf(b.dataset.tag) >= 0); });
    pressed(matrixBtn, matrix);
    Array.prototype.forEach.call(questionBox.querySelectorAll('button[data-question]'), function (b) { pressed(b, b.dataset.question === question); });

    if (question) {
      var q = data.questions[question];
      var fits = {};
      q.fits.forEach(function (f) { fits[f.item] = f; });
      var good = 0, avoid = 0;
      items.forEach(function (li) {
        var f = fits[li.dataset.item];
        if (!f || (f.mark !== 'good' && f.mark !== 'avoid')) { li.dataset.state = 'dim'; return; }
        li.dataset.state = f.mark;
        if (f.mark === 'good') good++; else avoid++;
        var why = el('p', 'why', (f.mark === 'good' ? 'Good fit: ' : 'Avoid: ') + f.reason);
        if (f.cond) why.appendChild(el('span', 'cond', f.cond));
        if (f.draft) why.appendChild(el('span', 'draft', 'draft'));
        li.appendChild(why);
      });
      statusEl.textContent = q.text + ' Good fits: ' + good + '. To avoid: ' + avoid + '.';
      return;
    }
    if (!tags.length && !matrix) {
      statusEl.textContent = 'Showing all ' + total + ' items.';
      return;
    }
    var hits = 0;
    items.forEach(function (li) {
      var it = data.items[li.dataset.item];
      var ok = tags.every(function (t) { return has(it.ignores, t); }) && (!matrix || has(it.needs, 'matrix'));
      li.dataset.state = ok ? 'hit' : 'dim';
      if (!ok) return;
      hits++;
      tags.forEach(function (t) { addCond(li, condOf(it.ignores, t)); });
      if (matrix) addCond(li, condOf(it.needs, 'matrix'));
    });
    var what = [];
    if (tags.length) what.push('ignore ' + list(tags.map(label)));
    if (matrix) what.push('work from a distance matrix');
    statusEl.textContent = 'Showing ' + hits + ' of ' + total + ' items that ' + list(what) + '.' +
      (hits === 0 ? ' No item matches all of them.' : '');
  }

  ignoreBox.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('button[data-tag]');
    if (!b) return;
    var i = tags.indexOf(b.dataset.tag);
    if (i >= 0) tags.splice(i, 1); else tags.push(b.dataset.tag);
    question = null;
    render();
  });
  matrixBtn.addEventListener('click', function () { matrix = !matrix; question = null; render(); });
  function choose(id, toggle) {
    if (!data.questions[id]) return;
    question = toggle && question === id ? null : id;
    if (question) { tags = []; matrix = false; }
    render();
  }
  questionBox.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('button[data-question]');
    if (b) choose(b.dataset.question, true);
  });
  doc.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('#sectors a.q[data-question]');
    if (a) choose(a.dataset.question, false);
  });

  // a link to #item-<id> opens that card
  function openFromHash() {
    var id = decodeURIComponent(location.hash.slice(1));
    if (id.indexOf('item-') !== 0) return;
    var d = doc.getElementById(id);
    if (d && d.tagName === 'DETAILS') { d.open = true; d.scrollIntoView(); }
  }
  window.addEventListener('hashchange', openFromHash);
  openFromHash();
  render();
})();
