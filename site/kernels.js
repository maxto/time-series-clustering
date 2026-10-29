/* DTW kernels for the live figure. Same convention and loops as the Python
   reference (code/python/tsc/distances.py): squared local cost, closed
   endpoints, steps (1,0) (0,1) (1,1), Sakoe-Chiba window |i - j| <= w,
   result = square root of the accumulated cost. Plain script, no modules. */
(function (root) {
  "use strict";

  function invalid(message) {
    return new Error("invalid: " + message);
  }

  function checkSeries(x) {
    if (!Array.isArray(x) || x.length === 0) throw invalid("a series must be a non-empty array");
    for (var i = 0; i < x.length; i++) {
      if (typeof x[i] !== "number" || !isFinite(x[i])) throw invalid("a series must contain only finite numbers");
    }
  }

  // Validate once. Return the effective window (null means wide enough to never bind).
  function checkDtw(x, y, w) {
    checkSeries(x);
    checkSeries(y);
    if (w === null || w === undefined) return Math.max(x.length, y.length);
    if (typeof w !== "number" || !isFinite(w) || Math.floor(w) !== w || w < 0) {
      throw invalid("w must be a non-negative integer or null");
    }
    if (w < Math.abs(x.length - y.length)) throw invalid("no admissible path: w < |n - m|");
    return w;
  }

  // Accumulated squared cost D, cells outside the window stay at Infinity.
  function accumulated(x, y, w) {
    var n = x.length, m = y.length, D = [];
    for (var i = 0; i < n; i++) {
      D.push(new Array(m).fill(Infinity));
      for (var j = Math.max(0, i - w); j < Math.min(m, i + w + 1); j++) {
        var d = x[i] - y[j];
        var local = d * d;
        if (i === 0 && j === 0) {
          D[i][j] = local;
        } else {
          var up = i > 0 ? D[i - 1][j] : Infinity;
          var left = j > 0 ? D[i][j - 1] : Infinity;
          var diag = i > 0 && j > 0 ? D[i - 1][j - 1] : Infinity;
          D[i][j] = local + Math.min(up, left, diag);
        }
      }
    }
    return D;
  }

  function euclidean(x, y) {
    checkSeries(x);
    checkSeries(y);
    if (x.length !== y.length) throw invalid("euclidean needs series of equal length");
    var s = 0;
    for (var i = 0; i < x.length; i++) {
      var d = x[i] - y[i];
      s += d * d;
    }
    return Math.sqrt(s);
  }

  function dtw(x, y, w) {
    var ww = checkDtw(x, y, w);
    var D = accumulated(x, y, ww);
    return Math.sqrt(D[x.length - 1][y.length - 1]);
  }

  // Walk back from the end. Ties go to the diagonal, then (i-1, j), then (i, j-1).
  function dtwPath(x, y, w) {
    var ww = checkDtw(x, y, w);
    var D = accumulated(x, y, ww);
    var i = x.length - 1, j = y.length - 1;
    var path = [[i, j]];
    while (i !== 0 || j !== 0) {
      var candidates = [[i - 1, j - 1], [i - 1, j], [i, j - 1]];
      var best = null, bestCost = Infinity;
      for (var k = 0; k < candidates.length; k++) {
        var a = candidates[k][0], b = candidates[k][1];
        if (a < 0 || b < 0) continue;
        if (best === null || D[a][b] < bestCost) {
          best = candidates[k];
          bestCost = D[a][b];
        }
      }
      i = best[0];
      j = best[1];
      path.push([i, j]);
    }
    return path.reverse();
  }

  root.TSC_KERNELS = { euclidean: euclidean, dtw: dtw, dtwPath: dtwPath };
})(typeof window !== "undefined" ? window : globalThis);
