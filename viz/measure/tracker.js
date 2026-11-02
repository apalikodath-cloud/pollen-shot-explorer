(function (root, factory) {
  "use strict";
  if (typeof module !== "undefined" && module.exports) module.exports = factory();
  else root.PollenTracker = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
  function pixel(frame, x, y) {
    var i = (y * frame.w + x) * 4;
    return [frame.data[i], frame.data[i + 1], frame.data[i + 2]];
  }

  function background(frames) {
    var w = frames[0].w, h = frames[0].h, out = new Uint8Array(w * h * 3);
    for (var y = 0; y < h; y++) for (var x = 0; x < w; x++) {
      for (var c = 0; c < 3; c++) {
        var a = [];
        for (var k = 0; k < frames.length; k++) a.push(frames[k].data[(y * w + x) * 4 + c]);
        a.sort(function (p, q) { return p - q; });
        out[(y * w + x) * 3 + c] = a[Math.floor(a.length / 2)];
      }
    }
    return { data: out, w: w, h: h };
  }

  function colourAt(frame, cx, cy, r) {
    var rr = 0.6 * r, x0 = Math.max(0, Math.floor(cx - rr)), x1 = Math.min(frame.w - 1, Math.ceil(cx + rr));
    var y0 = Math.max(0, Math.floor(cy - rr)), y1 = Math.min(frame.h - 1, Math.ceil(cy + rr));
    // per-channel median, not the mean: POLLEN's holes show the background, and a mean of two tones matches neither
    var ch = [[], [], []];
    for (var y = y0; y <= y1; y++) for (var x = x0; x <= x1; x++) {
      var dx = x + 0.5 - cx, dy = y + 0.5 - cy;
      if (dx * dx + dy * dy <= rr * rr) {
        var p = pixel(frame, x, y); ch[0].push(p[0]); ch[1].push(p[1]); ch[2].push(p[2]);
      }
    }
    if (!ch[0].length) return [0, 0, 0];
    return ch.map(function (a) { a.sort(function (p, q) { return p - q; }); return a[a.length >> 1]; });
  }

  function findBall(frame, bg, opts) {
    var cx = opts.cx, cy = opts.cy, win = opts.win, r = opts.r;
    var thr = opts.thr === undefined ? 28 : opts.thr, tol = opts.colTol === undefined ? 60 : opts.colTol;
    var x0 = Math.max(0, Math.floor(cx - win)), x1 = Math.min(frame.w - 1, Math.ceil(cx + win));
    var y0 = Math.max(0, Math.floor(cy - win)), y1 = Math.min(frame.h - 1, Math.ceil(cy + win));
    var ww = x1 - x0 + 1, hh = y1 - y0 + 1, mask = new Float64Array(ww * hh);
    for (var y = y0; y <= y1; y++) for (var x = x0; x <= x1; x++) {
      var i4 = (y * frame.w + x) * 4, i3 = (y * bg.w + x) * 3;
      var dr = frame.data[i4] - bg.data[i3], dg = frame.data[i4 + 1] - bg.data[i3 + 1], db = frame.data[i4 + 2] - bg.data[i3 + 2];
      if (Math.max(Math.abs(dr), Math.abs(dg), Math.abs(db)) > thr) {
        var cr = frame.data[i4] - opts.col[0], cg = frame.data[i4 + 1] - opts.col[1], cb = frame.data[i4 + 2] - opts.col[2];
        mask[(y - y0) * ww + x - x0] = clamp(1 - Math.sqrt(cr * cr + cg * cg + cb * cb) / tol, 0, 1);
      }
    }
    var seen = new Uint8Array(mask.length), best = null;
    for (var sy = 0; sy < hh; sy++) for (var sx = 0; sx < ww; sx++) {
      var start = sy * ww + sx;
      if (!mask[start] || seen[start]) continue;
      var stack = [start], comp = [], sumW = 0, sumX = 0, sumY = 0, edge = false;
      seen[start] = 1;
      while (stack.length) {
        var q = stack.pop(), qx = q % ww, qy = (q - qx) / ww, wx = mask[q];
        comp.push(q); sumW += wx; sumX += wx * (x0 + qx + 0.5); sumY += wx * (y0 + qy + 0.5);
        if (!qx || !qy || qx === ww - 1 || qy === hh - 1) edge = true;
        var ni;
        if (qx && mask[q - 1] && !seen[ni = q - 1]) { seen[ni] = 1; stack.push(ni); }
        if (qx + 1 < ww && mask[q + 1] && !seen[ni = q + 1]) { seen[ni] = 1; stack.push(ni); }
        if (qy && mask[q - ww] && !seen[ni = q - ww]) { seen[ni] = 1; stack.push(ni); }
        if (qy + 1 < hh && mask[q + ww] && !seen[ni = q + ww]) { seen[ni] = 1; stack.push(ni); }
      }
      if (!best || sumW > best.sumW) best = { n: comp.length, sumW: sumW, x: sumX / sumW, y: sumY / sumW, edge: edge };
    }
    if (!best || best.n < 0.15 * Math.PI * r * r) return null;
    var mean = best.sumW / best.n, conf = Math.min(1, best.n / (Math.PI * r * r)) * mean;
    if (best.edge) conf *= 0.5;
    return { px: best.x, py: best.y, conf: conf, area: best.n, r: Math.sqrt(best.n / Math.PI) };
  }

  function predict(pts, fNext) {
    if (!pts.length) return [0, 0];
    var a = pts.slice(-3), n = a.length;
    if (fNext === undefined) fNext = a[n - 1].f + (pts.step || 1);
    if (n === 1) return [a[0].px, a[0].py];
    if (n === 2) {
      var dt = a[1].f - a[0].f, scale = (fNext - a[1].f) / dt;
      return [a[1].px + (a[1].px - a[0].px) * scale, a[1].py + (a[1].py - a[0].py) * scale];
    }
    var x = 0, y = 0;
    for (var i = 0; i < 3; i++) {
      var li = 1;
      for (var j = 0; j < 3; j++) if (i !== j) li *= (fNext - a[j].f) / (a[i].f - a[j].f);
      x += a[i].px * li; y += a[i].py * li;
    }
    return [x, y];
  }

  async function track(getFrame, opts) {
    var start = opts.start, end = opts.end, step = opts.step === undefined ? 1 : opts.step;
    var r = opts.r, pts = [], misses = 0, stopped = "end", cache = {};
    // only the start frame is cached: a long clip would not fit in memory
    var get = async function (f) { if (f === start) { if (!(f in cache)) cache[f] = await getFrame(f); return cache[f]; } return getFrame(f); };
    var lo = Math.min(start, end), hi = Math.max(start, end), indices = opts.bgFrames;
    if (!indices) { indices = []; for (var bi = 0; bi < 9; bi++) indices.push(Math.round(lo + (hi - lo) * bi / 8)); }
    var bgFrames = [];
    for (var b = 0; b < indices.length; b++) { try { var bf = await get(indices[b]); if (bf) bgFrames.push(bf); } catch (e) {} }
    if (!bgFrames.length) return { pts: [], stopped: "lost" };
    var bg = background(bgFrames), first;
    try { first = await get(start); } catch (e) { first = null; }
    if (!first) return { pts: [], stopped: "lost" };
    var col = colourAt(first, opts.seed[0], opts.seed[1], r), f = start;
    while ((step > 0 && f <= hi) || (step < 0 && f >= lo)) {
      if (opts.shouldStop && opts.shouldStop()) { stopped = "stopped"; break; }
      var pred = pts.length ? predict(pts, f) : opts.seed.slice(), speed = 0;
      if (pts.length > 1) { var p0 = pts[pts.length - 2], p1 = pts[pts.length - 1], dt = p1.f - p0.f; speed = Math.hypot((p1.px - p0.px) / dt * step, (p1.py - p0.py) / dt * step); }
      var win = Math.max(3 * r, 1.5 * Math.abs(speed) + 2 * r);
      if (pred[0] < -r || pred[0] > first.w + r || pred[1] < -r || pred[1] > first.h + r) { stopped = "left the frame"; break; }
      var found = null, frame = null;
      try { frame = await get(f); if (frame) found = findBall(frame, bg, { cx: pred[0], cy: pred[1], win: win, r: r, col: col, thr: opts.thr, colTol: opts.colTol }); } catch (e) { found = null; }
      var dist = found ? Math.hypot(found.px - pred[0], found.py - pred[1]) : Infinity;
      if (found && found.conf >= (opts.minConf === undefined ? 0.25 : opts.minConf) && dist <= win) {
        pts.push({ f: f, px: found.px, py: found.py, conf: found.conf, area: found.area }); misses = 0;
        if (found.conf > 0.6) { var nc = colourAt(frame, found.px, found.py, r); col = [0.9 * col[0] + 0.1 * nc[0], 0.9 * col[1] + 0.1 * nc[1], 0.9 * col[2] + 0.1 * nc[2]]; }
      } else if (++misses >= (opts.maxMiss === undefined ? 3 : opts.maxMiss)) { stopped = "lost"; break; }
      if (opts.onProgress) opts.onProgress((f - start) / (end - start || 1));
      f += step;
    }
    if (stopped !== "stopped" && (f > hi || f < lo)) stopped = "end";
    // report confidence relative to the first (user-seeded) detection: a ball with holes never fills its disc,
    // so an absolute score is low even on a perfect frame. raw keeps the absolute score.
    var ref = pts.length ? Math.max(0.2, pts[0].conf) : 1;
    pts.forEach(function (p) { p.raw = p.conf; p.conf = Math.min(1, p.conf / ref); });
    return { pts: pts, stopped: stopped, refConf: ref };
  }

  function refine(pts) {
    var out = pts.map(function (p) { return Object.assign({}, p); });
    for (var i = 0; i < pts.length; i++) if (pts[i].conf < 0.5) {
      var q = pts.slice(Math.max(0, i - 3), Math.min(pts.length, i + 4)).filter(function (p) { return p.conf >= 0.5; });
      if (q.length < 3) continue;
      // least-squares quadratic in (f - f_i), so the fitted value at f_i is the constant term
      function fit(key) {
        var A = [[0, 0, 0], [0, 0, 0], [0, 0, 0]], t = [0, 0, 0];
        q.forEach(function (p) {
          var z = p.f - pts[i].f, b = [1, z, z * z];
          for (var r = 0; r < 3; r++) { t[r] += b[r] * p[key]; for (var c = 0; c < 3; c++) A[r][c] += b[r] * b[c]; }
        });
        for (var c = 0; c < 3; c++) {
          var pv = c;
          for (var r = c + 1; r < 3; r++) if (Math.abs(A[r][c]) > Math.abs(A[pv][c])) pv = r;
          var tmp = A[c]; A[c] = A[pv]; A[pv] = tmp; var tt = t[c]; t[c] = t[pv]; t[pv] = tt;
          if (Math.abs(A[c][c]) < 1e-12) return pts[i][key];
          for (var r2 = 0; r2 < 3; r2++) if (r2 !== c) {
            var m = A[r2][c] / A[c][c];
            for (var k = c; k < 3; k++) A[r2][k] -= m * A[c][k];
            t[r2] -= m * t[c];
          }
        }
        return t[0] / A[0][0];
      }
      out[i].px = fit("px"); out[i].py = fit("py"); out[i].smoothed = true;
    }
    return out;
  }

  return { background: background, colourAt: colourAt, findBall: findBall, predict: predict, track: track, refine: refine };
});
