// Behaviour shared by every page: layers (contents panel, citation popover, and later the search results),
// scroll-spy and reading progress, code tabs and copy, citation popovers, source topic filter.
// Plain script, no module loader, works from file://. Loaded with defer, so the DOM is ready.
(function () {
  'use strict';
  var doc = document;
  var TSC = window.TSC = window.TSC || {};

  // ---- layers: a stack of overlays. Escape closes only the top one and returns focus to its opener. ----
  // open(name, element, opener, {trap, onClose}): trap keeps Tab inside `element` while it is the top layer.
  // A layer opened above a trapping one suspends that trap, closing it restores the trap.
  var stack = [];
  function indexOf(name) {
    for (var i = 0; i < stack.length; i++) if (stack[i].name === name) return i;
    return -1;
  }
  function focusable(el) {
    return Array.prototype.filter.call(el.querySelectorAll('a[href], button, input, select, textarea, summary, [tabindex]'), function (n) {
      return !n.disabled && n.tabIndex >= 0 && n.getClientRects().length > 0;
    });
  }
  TSC.layers = {
    open: function (name, element, opener, opts) {
      opts = opts || {};
      var i = indexOf(name);
      if (i >= 0) { var old = stack.splice(i, 1)[0]; if (old.onClose) old.onClose(); }
      stack.push({ name: name, el: element, opener: opener || null, trap: !!opts.trap, onClose: opts.onClose });
      if (opts.trap && !element.contains(doc.activeElement)) {
        var f = focusable(element);
        if (f.length) f[0].focus(); else { element.tabIndex = -1; element.focus(); }
      }
    },
    // restore: false closes without moving focus (a link was followed, or the reader clicked elsewhere)
    close: function (name, opts) {
      var i = indexOf(name);
      if (i < 0) return;
      var wasTop = i === stack.length - 1;
      var layer = stack.splice(i, 1)[0];
      if (layer.onClose) layer.onClose();
      if (wasTop && !(opts && opts.restore === false) && layer.opener && doc.contains(layer.opener)) layer.opener.focus();
    },
    top: function () { return stack.length ? stack[stack.length - 1].name : null; },
    has: function (name) { return indexOf(name) >= 0; }
  };

  doc.addEventListener('keydown', function (e) {
    var top = stack[stack.length - 1];
    if (!top) return;
    if (e.key === 'Escape') {
      e.preventDefault();
      TSC.layers.close(top.name);
    } else if (e.key === 'Tab' && top.trap) {
      var f = focusable(top.el);
      if (!f.length) { e.preventDefault(); return; }
      var first = f[0], last = f[f.length - 1], active = doc.activeElement;
      if (!top.el.contains(active)) { e.preventDefault(); first.focus(); }
      else if (e.shiftKey && active === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && active === last) { e.preventDefault(); first.focus(); }
    }
  });

  // ---- contents panel (below 1180 px) ----
  var menu = doc.querySelector('header.top button.menu');
  var nav = doc.getElementById('contents');
  if (menu && nav) {
    var setOpen = function (open) { menu.setAttribute('aria-expanded', open ? 'true' : 'false'); };
    var openPanel = function () {
      setOpen(true);
      TSC.layers.open('contents', nav, menu, { trap: true, onClose: function () { setOpen(false); } });
    };
    menu.addEventListener('click', function () {
      if (TSC.layers.has('contents')) TSC.layers.close('contents'); else openPanel();
    });
    var close = nav.querySelector('.close');
    if (close) close.addEventListener('click', function () { TSC.layers.close('contents'); });
    var scrim = doc.querySelector('.scrim');
    if (scrim) scrim.addEventListener('click', function () { TSC.layers.close('contents', { restore: false }); });
    nav.addEventListener('click', function (e) {
      if (e.target.closest && e.target.closest('a[href]')) TSC.layers.close('contents', { restore: false });
    });
    window.matchMedia('(min-width: 1180px)').addEventListener('change', function (e) {
      if (e.matches) TSC.layers.close('contents', { restore: false });
    });
  }

  // ---- scroll-spy on the contents, reading progress ----
  var tocLinks = Array.prototype.slice.call(doc.querySelectorAll('#contents ol.toc a[href^="#"]'));
  var bar = doc.querySelector('header.top .progress > i');
  var mainEl = doc.getElementById('main');
  var targets = tocLinks.map(function (a) { return doc.getElementById(decodeURIComponent(a.getAttribute('href').slice(1))); });
  var queued = false;
  function update() {
    queued = false;
    var y = window.pageYOffset, vh = window.innerHeight;
    if (bar && mainEl) {
      var top = mainEl.getBoundingClientRect().top + y, span = mainEl.offsetHeight - vh;
      var f = span > 0 ? (y - top) / span : (y > 0 ? 1 : 0);
      bar.style.width = Math.max(0, Math.min(1, f)) * 100 + '%';
    }
    if (tocLinks.length) {
      var atEnd = y + vh >= doc.documentElement.scrollHeight - 2 && y > 0;
      var current = -1;
      targets.forEach(function (t, i) { if (t && t.getBoundingClientRect().top <= 100) current = i; });
      if (atEnd) current = targets.length - 1;
      tocLinks.forEach(function (a, i) {
        if (i === current) { a.setAttribute('aria-current', 'true'); a.classList.add('on'); }
        else { a.removeAttribute('aria-current'); a.classList.remove('on'); }
      });
    }
  }
  function schedule() { if (!queued) { queued = true; window.requestAnimationFrame(update); } }
  if (bar || tocLinks.length) {
    window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', schedule);
    update();
  }

  // ---- code: language tabs and copy ----
  function legacyCopy(text) {
    return new Promise(function (resolve, reject) {
      var t = doc.createElement('textarea');
      t.value = text; t.setAttribute('readonly', ''); t.style.cssText = 'position:fixed;top:0;left:0;opacity:0';
      doc.body.appendChild(t); t.select();
      var ok = false;
      try { ok = doc.execCommand('copy'); } catch (e) { ok = false; }
      doc.body.removeChild(t);
      if (ok) resolve(); else reject(new Error('copy failed'));
    });
  }
  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text).catch(function () { return legacyCopy(text); });
    }
    return legacyCopy(text);
  }
  Array.prototype.forEach.call(doc.querySelectorAll('section.code'), function (section) {
    var tabs = Array.prototype.slice.call(section.querySelectorAll('[role="tab"][data-lang]'));
    var panels = Array.prototype.slice.call(section.querySelectorAll('pre[data-lang]'));
    function show(lang) {
      tabs.forEach(function (t) {
        var on = t.dataset.lang === lang;
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
      });
      panels.forEach(function (p) { p.hidden = p.dataset.lang !== lang; });
    }
    if (tabs.length) {
      panels.forEach(function (p) {
        p.id = 'code-' + p.dataset.lang; p.setAttribute('role', 'tabpanel'); p.tabIndex = 0;
        p.setAttribute('aria-labelledby', 'tab-' + p.dataset.lang);
      });
      tabs.forEach(function (t, i) {
        t.id = 'tab-' + t.dataset.lang; t.setAttribute('aria-controls', 'code-' + t.dataset.lang);
        t.addEventListener('click', function () { show(t.dataset.lang); });
        t.addEventListener('keydown', function (e) {
          var step = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
          if (!step) return;
          e.preventDefault();
          var next = tabs[(i + step + tabs.length) % tabs.length];
          show(next.dataset.lang); next.focus();
        });
      });
      show(tabs[0].dataset.lang);
    }
    var copy = section.querySelector('button.copy');
    if (copy) {
      var timer = null;
      copy.addEventListener('click', function () {
        var pre = panels.filter(function (p) { return !p.hidden; })[0] || panels[0];
        if (!pre) return;
        copyText(pre.textContent).then(function () { return 'Copied'; }, function () { return 'Copy failed'; }).then(function (label) {
          copy.textContent = label;
          window.clearTimeout(timer);
          timer = window.setTimeout(function () { copy.textContent = 'Copy'; }, 1800);
        });
      });
      copy.setAttribute('aria-live', 'polite');
    }
  });

  // ---- citation popover: built from the entry under "Sources cited in this lesson" ----
  var pop = null;
  function closePop(opts) { TSC.layers.close('cite', opts); }
  function buildPop(link, entry) {
    var d = doc.createElement('div');
    d.className = 'pop'; d.setAttribute('role', 'dialog'); d.id = 'cite-pop'; d.tabIndex = -1;
    var title = doc.createElement('p');
    title.className = 'pt'; title.id = 'cite-pop-title'; title.textContent = link.textContent;
    d.setAttribute('aria-labelledby', 'cite-pop-title');
    d.appendChild(title);
    ['au', 'ti', 've', 'ln'].forEach(function (cls) {
      var src = entry.querySelector('.' + cls);
      if (!src) return;
      var p = doc.createElement('p');
      p.className = 'pb ' + cls;
      Array.prototype.forEach.call(src.childNodes, function (n) { p.appendChild(n.cloneNode(true)); });
      if (cls === 'ti') { var c = doc.createElement('cite'); while (p.firstChild) c.appendChild(p.firstChild); p.appendChild(c); }
      d.appendChild(p);
    });
    var more = doc.createElement('p');
    more.className = 'pb pm';
    var a = doc.createElement('a');
    a.href = '#' + entry.id; a.textContent = 'Go to the entry in the sources list';
    more.appendChild(a); d.appendChild(more);
    return d;
  }
  function placePop(d, link) {
    var r = link.getBoundingClientRect(), sx = window.pageXOffset, sy = window.pageYOffset;
    var w = Math.min(380, doc.documentElement.clientWidth - 24);
    d.style.width = w + 'px';
    var left = Math.max(12, Math.min(r.left, doc.documentElement.clientWidth - w - 12));
    d.style.left = left + sx + 'px';
    d.style.top = r.bottom + sy + 8 + 'px';
  }
  doc.addEventListener('click', function (e) {
    var link = e.target.closest && e.target.closest('a.cite[data-ref]');
    if (link) {
      var entry = doc.getElementById('src-' + link.dataset.ref);
      if (!entry) return;
      e.preventDefault();
      if (pop) { var same = pop.link === link; closePop({ restore: false }); if (same) { link.focus(); return; } }
      var d = buildPop(link, entry);
      doc.body.appendChild(d);
      placePop(d, link);
      pop = { el: d, link: link };
      TSC.layers.open('cite', d, link, { onClose: function () { if (pop && pop.el.parentNode) pop.el.parentNode.removeChild(pop.el); pop = null; } });
      d.focus();
    } else if (pop && !(e.target.closest && e.target.closest('#cite-pop'))) {
      closePop({ restore: false });
    } else if (pop && e.target.closest && e.target.closest('#cite-pop a[href^="#"]')) {
      closePop({ restore: false });
    }
  });
  window.addEventListener('resize', function () { closePop({ restore: false }); });

  // ---- sources page: topic filter ----
  var topics = doc.getElementById('f-topic');
  var list = doc.getElementById('src-list');
  if (topics && list) {
    topics.addEventListener('click', function (e) {
      var b = e.target.closest && e.target.closest('button[data-topic]');
      if (!b) return;
      var topic = b.dataset.topic;
      Array.prototype.forEach.call(topics.querySelectorAll('button[data-topic]'), function (x) {
        x.setAttribute('aria-pressed', x === b ? 'true' : 'false');
      });
      Array.prototype.forEach.call(list.querySelectorAll('li.ref'), function (li) {
        li.hidden = topic !== 'all' && (li.dataset.topics || '').split(' ').indexOf(topic) < 0;
      });
    });
  }
})();
