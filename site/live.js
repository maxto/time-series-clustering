/* Live figures. Each <figure data-live="NAME"> is turned into an interactive figure by the component NAME.
   Plain script, no library, no request: the data is the figure's own <script class="live-data"> (JSON,
   validated at build time) and the maths is window.TSC_KERNELS (kernels.js).

   The "dtw" component, input contract (design 6.1), everything derived from the figure's data:
   - Pair: a <fieldset> with <legend>Pair</legend> and one native radio per pair, labelled "<a> and <b>",
     group name live-<n>-pair (n the position of the figure among the live figures, from 1). Shown only
     with two or more pairs. Starts on initial.pair.
   - Window: <input type="range"> with min, max and step 1 from w, starting at w.initial, a visible readout
     ("w = 4 samples (2 h)", "w = 1 sample (30 min)") and aria-valuetext with the same words. Duration is
     w * sample_minutes: below 60 minutes "N min", else hours, whole ("2 h") or with one decimal ("1.5 h").
   - No window: a checkbox "No window", shown only when w.none is true. Checked: the slider is disabled and
     the state uses w = null. Unchecked: the slider is enabled and the state takes its retained value.
   - Reset: back to initial.pair, w.initial, the box unchecked.
   - Readout under the figure, one line, aria-live="polite": "mon and sat, w = 4 samples (2 h): DTW 0.22,
     Euclidean 3.71", or "mon and sat, no window: DTW 0.22, Euclidean 3.71". Two decimals, from the kernels.
   - Text alternative: the live SVG's <title> and <desc> follow the geometry contract (AGENTS.md) and change
     with the state. The root carries data-pair and data-w, drawn parts carry data-part, like the static SVG.
   - Activation is atomic: the SVG and the controls are built detached, the initial state is rendered once,
     then they replace the static SVG in one step. The static SVG node is kept, detached, as the baseline.
   - Failure after activation (an exception while computing or drawing): the baseline goes back, the live SVG
     and the controls are removed, the readout says "The interactive figure stopped. Shown: the initial
     setting, <pair>, <window>." and one console.error starting "live figure:" is logged. Each figure is
     handled on its own, so a failure never touches another figure.
   - Rendering: at most 48 by 48 = 2,304 cells. Every redraw replaces the content of the SVG, no animation.
   - Width: the SVG has class "live" (no 360 px cap). Its viewBox width is the figure's content width, so one
     unit is one CSS pixel and labels keep their CSS size. Redrawn on resize (debounced), keeping the state. */
(function () {
  "use strict";

  var SVG_NS = "http://www.w3.org/2000/svg";

  function esc(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  // A coordinate with one decimal, no trailing .0 (the same as scripts/figures.py).
  function f(v) {
    var s = v.toFixed(1);
    return s.slice(-2) === ".0" ? s.slice(0, -2) : s;
  }

  function text(x, y, s, cls) {
    return '<text class="' + (cls || "t-sm t-mono") + '" x="' + f(x) + '" y="' + f(y) + '">' + esc(s) + "</text>";
  }

  function line(x1, y1, x2, y2, cls, extra) {
    return '<line class="' + cls + '" x1="' + f(x1) + '" y1="' + f(y1) + '" x2="' + f(x2) + '" y2="' + f(y2) + '"' + (extra || "") + "/>";
  }

  function polyline(points, cls, extra) {
    return '<polyline class="' + cls + '" points="' + points.map(function (p) { return f(p[0]) + "," + f(p[1]); }).join(" ") + '"' + (extra || "") + "/>";
  }

  function duration(w, minutes) {
    var m = w * minutes;
    if (m < 60) return m + " min";
    var h = m / 60;
    return (Math.round(h) === h ? String(h) : h.toFixed(1)) + " h";
  }

  function windowWords(w, minutes) {
    return "w = " + w + " sample" + (w === 1 ? "" : "s") + " (" + duration(w, minutes) + ")";
  }

  // Everything one state needs, computed before the DOM is touched. `w` is an integer or null.
  function compute(data, pair, w) {
    var K = window.TSC_KERNELS;
    if (!K) throw new Error("kernels are not loaded");
    var names = data.pairs[pair], a = data.series[names[0]], b = data.series[names[1]];
    var path = K.dtwPath(a, b, w);
    return { na: names[0], nb: names[1], a: a, b: b, w: w, path: path, euclid: K.euclidean(a, b), dist: K.dtw(a, b, w) };
  }

  // The SVG content of one state at width W, as a string. Geometry follows scripts/figures.py (fig_dtw_explorer).
  function draw(s, W) {
    var a = s.a, b = s.b, n = a.length, na = s.na, nb = s.nb, w = s.w, path = s.path;
    var ww = w === null ? n : w;
    var lo = Math.min.apply(null, a.concat(b)), hi = Math.max.apply(null, a.concat(b));
    if (hi === lo) hi = lo + 1;
    var xLab = 4, x0 = 40, wt = W - x0 - 4;
    var headH = 22, bandH = 44, midGap = 30, gap = 30;
    var topA = headH, topB = topA + bandH + midGap;
    var body = [text(xLab, 14, "Euclidean " + s.euclid.toFixed(2)), text(W - 4, 14, "DTW " + s.dist.toFixed(2), "t-sm t-mono end")];
    var tx = function (i) { return x0 + (n > 1 ? wt * i / (n - 1) : 0); };
    var ty = function (v, top) { return top + bandH - bandH * (v - lo) / (hi - lo); };
    var pa = a.map(function (v, i) { return [tx(i), ty(v, topA)]; });
    var pb = b.map(function (v, j) { return [tx(j), ty(v, topB)]; });
    for (var k = 0; k < path.length; k++) {
      if (k % 2 === 0 || k === path.length - 1) {
        var i0 = path[k][0], j0 = path[k][1];
        body.push(line(pa[i0][0], pa[i0][1], pb[j0][0], pb[j0][1], "ln-muted", ' data-part="link"'));
      }
    }
    body.push(polyline(pa, "ln", ' data-part="series-a"'));
    body.push(polyline(pb, "ln-accent", ' data-part="series-b"'));
    body.push(text(xLab, topA + bandH - 4, na));
    body.push(text(xLab, topB + bandH - 4, nb));
    // the grid block (labels, grid, strip) is centred when the figure is wide, never wider than 420
    var strip = 44, labelW = 68, gxGap = 6;
    var size = Math.min(W - 4 - 4 - labelW - gxGap, 420);
    var left = Math.max(4, (W - labelW - gxGap - size) / 2);
    var g0x = left + labelW + gxGap;
    var g0y = topB + bandH + gap + 26;
    var cell = size / n;
    var band = [], cmax = 0, i, j;
    for (i = 0; i < n; i++) {
      for (j = 0; j < n; j++) {
        if (Math.abs(i - j) <= ww) {
          var c = (a[i] - b[j]) * (a[i] - b[j]);
          band.push([i, j, c]);
          if (c > cmax) cmax = c;
        }
      }
    }
    var opacity = function (c) { return (0.12 + 0.78 * (cmax > 0 ? Math.sqrt(c / cmax) : 0)).toFixed(2); };
    var cx = function (jj) { return g0x + (jj + 0.5) * cell; };
    var cy = function (ii) { return g0y + size - (ii + 0.5) * cell; };
    band.forEach(function (t) {
      body.push('<rect class="fill-muted" data-part="cell" x="' + f(g0x + t[1] * cell) + '" y="' + f(g0y + size - (t[0] + 1) * cell) +
        '" width="' + f(cell) + '" height="' + f(cell) + '" opacity="' + opacity(t[2]) + '"/>');
    });
    body.push('<rect class="ln-soft" data-part="grid" x="' + f(g0x) + '" y="' + f(g0y) + '" width="' + f(size) + '" height="' + f(size) + '"/>');
    body.push(line(g0x, g0y + size, g0x + size, g0y, "ln-soft", ' stroke-dasharray="3 4"'));
    body.push(polyline(path.map(function (p) { return [cx(p[1]), cy(p[0])]; }), "ln", ' data-part="path"'));
    body.push(text(g0x + 10, g0y + 22, w === null ? "no window" : "|i − j| ≤ " + w));
    var right = g0x - gxGap;
    body.push(polyline(a.map(function (v, ii) { return [right - strip * (v - lo) / (hi - lo), cy(ii)]; }), "ln", ' stroke-width="1.5"'));
    body.push(text(left, g0y - 10, na + ", i ↑"));
    var sTop = g0y + size + gxGap;
    body.push(polyline(b.map(function (v, jj) { return [cx(jj), sTop + strip - strip * (v - lo) / (hi - lo)]; }), "ln-accent", ' stroke-width="1.5"'));
    body.push(text(left, sTop + strip - 2, nb + ", j →"));
    var ly = sTop + strip + 14, steps = 5, sw = 22;
    body.push(text(left, ly + 12, "0"));
    for (var q = 0; q < steps; q++) {
      body.push('<rect class="fill-muted" x="' + f(left + 14 + q * (sw + 2)) + '" y="' + f(ly) + '" width="' + sw + '" height="16" opacity="' + opacity(cmax * q / (steps - 1)) + '"/>');
    }
    body.push(text(left + 14 + steps * (sw + 2) + 4, ly + 12, cmax.toFixed(2)));
    body.push(text(g0x + size, ly + 12, "local cost", "t-sm end"));
    var height = ly + 24;
    var wtxt = w === null ? "no window" : "window w = " + w;
    var title = "DTW of " + na + " and " + nb + " with " + wtxt;
    var desc = "Pair " + na + " and " + nb + ", " + wtxt + ". Euclidean distance " + s.euclid.toFixed(2) + ", DTW distance " + s.dist.toFixed(2) +
      ". Top: " + na + " (ink) above " + nb + " (accent) on one scale, linked along the DTW warping path (every second link is drawn). Bottom: a " +
      n + " by " + n + " grid, rows the samples of " + na + " from the bottom, columns the samples of " + nb + " from the left. Only the band " +
      "of allowed cells is drawn. Higher opacity means higher local cost, the squared difference of the two samples, from 0 to " + cmax.toFixed(2) +
      ". The dashed diagonal is lock-step matching and the line through the cells is the warping path.";
    return { height: height, pair: na + "-" + nb, w: w === null ? "none" : String(w),
      html: "<title>" + esc(title) + "</title><desc>" + esc(desc) + "</desc>" + body.join("") };
  }

  function contentWidth(fig) {
    var cs = getComputedStyle(fig);
    var w = fig.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
    return Math.max(240, Math.round(w * 10) / 10);
  }

  function el(tag, attrs, children) {
    var e = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) { e.setAttribute(k, attrs[k]); });
    (children || []).forEach(function (c) { e.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return e;
  }

  function dtwComponent(fig, n) {
    var data = JSON.parse(fig.querySelector("script.live-data").textContent);
    var base = fig.querySelector("svg");
    if (!base) throw new Error("no static SVG");
    var minutes = data.sample_minutes;
    var init = { pair: data.initial.pair, w: data.w.initial };
    var state = { pair: init.pair, w: init.w, none: false };
    var dead = false;
    var width = contentWidth(fig);

    var svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("class", "live");
    svg.setAttribute("role", "img");

    var ctl = el("div", { "class": "live-ctl" });
    var out = el("p", { "class": "live-out", "aria-live": "polite" });
    var radios = [];
    if (data.pairs.length > 1) {
      var set = el("fieldset", { "class": "live-pair" }, [el("legend", {}, ["Pair"])]);
      data.pairs.forEach(function (p, k) {
        var r = el("input", { type: "radio", name: "live-" + n + "-pair", value: String(k) });
        r.addEventListener("change", function () { if (r.checked) { state.pair = k; update(); } });
        radios.push(r);
        set.appendChild(el("label", {}, [r, p[0] + " and " + p[1]]));
      });
      ctl.appendChild(set);
    }
    var sliderId = "live-" + n + "-w";
    var slider = el("input", { type: "range", id: sliderId, min: String(data.w.min), max: String(data.w.max), step: "1" });
    var wOut = el("span", { "class": "live-w" });
    ctl.appendChild(el("div", { "class": "live-win" }, [el("label", { "for": sliderId }, ["Window"]), slider, wOut]));
    slider.addEventListener("input", function () { state.w = Number(slider.value); update(); });
    var none = null;
    if (data.w.none) {
      none = el("input", { type: "checkbox" });
      none.addEventListener("change", function () { state.none = none.checked; update(); });
      ctl.appendChild(el("label", { "class": "live-none" }, [none, "No window"]));
    }
    var reset = el("button", { type: "button" }, ["Reset"]);
    reset.addEventListener("click", function () {
      state.pair = init.pair; state.w = init.w; state.none = false;
      update();
    });
    ctl.appendChild(reset);

    // Put the state into the controls, compute it, draw it. Nothing is written to the page before the maths
    // and the drawing have both succeeded.
    function render() {
      var w = state.none ? null : state.w;
      var s = compute(data, state.pair, w);
      var d = draw(s, width);
      var words = windowWords(state.w, minutes);
      radios.forEach(function (r, k) { r.checked = k === state.pair; });
      slider.value = String(state.w);
      slider.disabled = state.none;
      slider.setAttribute("aria-valuetext", words);
      wOut.textContent = words;
      if (none) none.checked = state.none;
      svg.setAttribute("viewBox", "0 0 " + f(width) + " " + f(d.height));
      svg.setAttribute("data-pair", d.pair);
      svg.setAttribute("data-w", d.w);
      svg.innerHTML = d.html;
      out.textContent = s.na + " and " + s.nb + ", " + (w === null ? "no window" : words) + ": DTW " + s.dist.toFixed(2) + ", Euclidean " + s.euclid.toFixed(2);
    }

    function fail(err) {
      if (dead) return;
      dead = true;
      window.removeEventListener("resize", onResize);
      clearTimeout(timer);
      var names = data.pairs[init.pair];
      if (svg.parentNode) svg.replaceWith(base);
      ctl.remove();
      out.textContent = "The interactive figure stopped. Shown: the initial setting, " + names[0] + " and " + names[1] + ", " + windowWords(init.w, minutes) + ".";
      console.error("live figure: " + (err && err.message ? err.message : err));
    }

    function update() {
      if (dead) return;
      try { render(); } catch (err) { fail(err); }
    }

    var timer = 0;
    function onResize() {
      clearTimeout(timer);
      timer = setTimeout(function () {
        var w = contentWidth(fig);
        if (Math.abs(w - width) >= 0.5) { width = w; update(); }
      }, 120);
    }

    // Atomic activation: render once while detached, then swap in one step. An error here leaves the static figure alone.
    render();
    base.replaceWith(svg);
    svg.after(ctl, out);
    window.addEventListener("resize", onResize);
  }

  var components = { dtw: dtwComponent };

  function start() {
    Array.prototype.forEach.call(document.querySelectorAll("figure[data-live]"), function (fig, k) {
      try {
        var make = components[fig.getAttribute("data-live")];
        if (!make) throw new Error("unknown component " + fig.getAttribute("data-live"));
        make(fig, k + 1);
      } catch (err) {
        console.error("live figure: " + (err && err.message ? err.message : err));
      }
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
