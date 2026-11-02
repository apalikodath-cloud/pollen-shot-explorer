// Shot Lab worker: runs the explorer's shot solver off the page thread. Jobs: "map" (rpm / exit-angle / time-of-flight
// against distance), "lip" (the near-lip hypothesis scan) and "sotm" (one moving shot checked in the 3D model).
// In node the module exports the factory (call it with the solver and shotcore) for tests.
if (typeof importScripts === "function" && typeof module === "undefined") importScripts("../explorer/physics.js", "../explorer/solver.js", "shotcore.js");
(function (root, factory) {
  "use strict";
  if (typeof module !== "undefined" && module.exports) { module.exports = factory; return; }
  var L = factory(root.PollenSolver, root.PollenShotCore);
  root.onmessage = function (e) { L.handle(e.data, function (msg) { root.postMessage(msg); }); };
})(typeof self !== "undefined" ? self : this, function (PS, C) {
  "use strict";
  var M = { meta: null };

  function rad(d) { return d * Math.PI / 180; }
  function legal(q) {
    var ctx = PS._context(Object.assign({}, q, { params: PS.effParams(q).p }));
    return { ok: ctx.ps.ok, status: ctx.ps.status, Lh: ctx.ps.Lh, d: ctx.ps.d, notes: ctx.ps.notes || [] };
  }
  function tofOf(s) { return s.cls && s.cls.result === "clean" && isFinite(s.cls.i) ? s.cls.i * s.path.dt : NaN; }
  // longest run of consecutive true values in a boolean list -> {lo, hi} indices, or null
  function longestRun(ok) {
    var best = null, start = -1;
    for (var i = 0; i <= ok.length; i++) {
      if (i < ok.length && ok[i]) { if (start < 0) start = i; continue; }
      if (start >= 0 && (!best || i - start > best.hi - best.lo + 1)) best = { lo: start, hi: i - 1 };
      start = -1;
    }
    return best;
  }
  // Spearman rank correlation (average ranks for ties)
  function ranks(a) {
    var idx = a.map(function (v, i) { return i; }).sort(function (i, j) { return a[i] - a[j]; }), r = new Array(a.length);
    for (var k = 0; k < idx.length;) {
      var e = k; while (e + 1 < idx.length && a[idx[e + 1]] === a[idx[k]]) e++;
      for (var m = k; m <= e; m++) r[idx[m]] = (k + e) / 2 + 1;
      k = e + 1;
    }
    return r;
  }
  function spearman(x, y) {
    var p = []; for (var i = 0; i < x.length; i++) if (isFinite(x[i]) && isFinite(y[i])) p.push([x[i], y[i]]);
    if (p.length < 3) return { rho: NaN, n: p.length };
    var rx = ranks(p.map(function (q) { return q[0]; })), ry = ranks(p.map(function (q) { return q[1]; }));
    var mx = 0, my = 0, sxx = 0, syy = 0, sxy = 0;
    for (i = 0; i < rx.length; i++) { mx += rx[i]; my += ry[i]; } mx /= rx.length; my /= ry.length;
    for (i = 0; i < rx.length; i++) { sxx += (rx[i] - mx) * (rx[i] - mx); syy += (ry[i] - my) * (ry[i] - my); sxy += (rx[i] - mx) * (ry[i] - my); }
    return { rho: sxx && syy ? sxy / Math.sqrt(sxx * syy) : NaN, n: p.length };
  }
  // Gaussian-weighted clean share around each cell of a (v x theta) grid: speed scatter sv (relative), angle sth (deg).
  // Cells closer than 3 sigma to the scan edge are flagged: the weight there is truncated.
  function gaussShare(clean, V, TH, sv, sth) {
    var nV = V.length, nT = TH.length, out = new Float32Array(nV * nT).fill(NaN), edge = new Uint8Array(nV * nT);
    var dv = V[1] - V[0], dt = TH[1] - TH[0], kt = Math.ceil(3 * sth / dt);
    for (var iv = 0; iv < nV; iv++) {
      var sg = sv * V[iv], kv = Math.ceil(3 * sg / dv);
      for (var it = 0; it < nT; it++) {
        if (!clean[iv * nT + it]) continue;
        var w = 0, k = 0;
        for (var a = Math.max(0, iv - kv); a <= Math.min(nV - 1, iv + kv); a++) for (var b = Math.max(0, it - kt); b <= Math.min(nT - 1, it + kt); b++) {
          var zv = (V[a] - V[iv]) / sg, zt = (TH[b] - TH[it]) / sth, g = Math.exp(-0.5 * (zv * zv + zt * zt));
          w += g; if (clean[a * nT + b]) k += g;
        }
        out[iv * nT + it] = k / w;
        if (iv - kv < 0 || iv + kv > nV - 1 || it - kt < 0 || it + kt > nT - 1) edge[iv * nT + it] = 1;
      }
    }
    return { share: out, edge: edge };
  }
  // the closest approach of a path to a segment, its index and the speed there (positional differencing)
  // (upto: last path index searched; entry: the cell-entry index for the entry speed)
  function lipInfo(path, seg, R, upto, mass, entry) {
    var best = Infinity, j = -1, n = Math.min(path.n, upto + 1);
    for (var i = 0; i < n; i++) {
      var dd = C.segDist(path.x[i], path.z[i], seg[0][0], seg[0][1], seg[1][0], seg[1][1]) - R;
      if (dd < best) { best = dd; j = i; }
    }
    function speed(i) {
      var a = Math.max(0, i - 1), b = Math.min(path.n - 1, i + 1), t = (b - a) * path.dt;
      return t > 0 ? Math.hypot(path.x[b] - path.x[a], path.y[b] - path.y[a], path.z[b] - path.z[a]) / t : NaN;
    }
    var vl = speed(j), ve = speed(entry === undefined ? upto : entry);
    return { clear: best, j: j, vLip: vl, keLip: 0.5 * mass * vl * vl, vEntry: ve, keEntry: 0.5 * mass * ve * ve };
  }

  // Clean half-width around a setting: step out along v (0.05 m/s) and along theta (0.1 deg) until the first
  // shot that is not clean; the smaller side counts. (The solver's own tolV/tolTheta is the largest clean square
  // in grid cells, which mixes units, so it is not used for the map.)
  function walkTol(q, v, th, twin) {
    function clean(vv, tt) { var s = PS.shot(q, vv, tt); return (twin ? s.twin.cls.result : s.cls.result) === "clean"; }
    function side(dv, dt, nMax) { var i = 0; while (i < nMax && clean(v + (i + 1) * dv, th + (i + 1) * dt)) i++; return i; }
    var nv = Math.min(side(0.05, 0, 40), side(-0.05, 0, 40)), nt = Math.min(side(0, 0.1, 60), side(0, -0.1, 60));
    return { v: +(nv * 0.05).toFixed(2), th: +(nt * 0.1).toFixed(1) };
  }

  // ---- jobs
  function mapJob(q, o, progress) {
    var rows = [], ds = o.ds;
    for (var k = 0; k < ds.length; k++) {
      var d = ds[k], qq = Object.assign({}, q, { x: -d, y: 0 }), row = { d: d };
      var lg = legal(qq); row.ok = lg.ok; row.status = lg.status; row.Lh = lg.Lh;
      if (lg.ok) {
        if (o.mode === "fixed") {
          var fx = function (twin) {
            var V = [], ok = [];
            for (var i = 0, n = Math.round((o.vHi - o.vLo) / o.vStep); i <= n; i++) { var v = +(o.vLo + i * o.vStep).toFixed(4), s = PS.shot(qq, v, o.theta); V.push(v); ok.push((twin ? s.twin.cls.result : s.cls.result) === "clean"); }
            var run = longestRun(ok);
            if (!run) return null;
            var vc = (V[run.lo] + V[run.hi]) / 2, sc = PS.shot(qq, vc, o.theta);
            return { v: vc, theta: o.theta, tol: (V[run.hi] - V[run.lo]) / 2, tof: twin ? tofOf(sc.twin) : tofOf(sc), entryAngle: (twin ? sc.twin : sc).cls.entryAngle };
          };
          row.main = fx(false); row.twin = (q.S || 0) !== 0 ? fx(true) : null;
        } else {
          var r = PS.solve(qq, null), mf = r.mostForgiving;
          var pick = function (m, twin) {
            if (!m) return null;
            var s = PS.shot(qq, m.v, m.theta), w = walkTol(qq, m.v, m.theta, twin);
            return { v: m.v, theta: m.theta, tol: w.v, tolTheta: w.th, margin: m.margin, entryAngle: m.entryAngle, tof: tofOf(twin ? s.twin : s), gripLimited: !!m.gripLimited };
          };
          row.main = pick(mf, false); row.twin = r.twin ? pick(r.twin.mostForgiving, true) : null;
        }
        if (row.main) row.main.rpm = PS.rpm(row.main.v, q.vu);
        if (row.twin) row.twin.rpm = PS.rpm(row.twin.v, q.vu);
      }
      rows.push(row);
      progress((k + 1) / ds.length);
    }
    return { rows: rows };
  }

  function lipJob(q, o, progress) {
    var qq = Object.assign({}, q, { x: -o.d, y: 0 }), lg = legal(qq);
    if (!lg.ok) return { ok: false, reason: "pose " + lg.status };
    var r = PS.solve(qq, null), mf = r.mostForgiving;
    progress(0.1);
    if (!mf) return { ok: false, reason: "no clean shot at this pose" };
    var sec = M.meta.sections.unfav_s0, li = sec.names.indexOf("up_lower_lip"), seg = [sec.P0[li], sec.P1[li]];
    var p = PS.effParams(qq).p, R = p.radius, mass = p.mass;
    var V = [], TH = [];
    var nv = Math.round(o.vHalf / o.vStep), nt = Math.round(o.thHalf / o.thStep);
    for (var a = -nv; a <= nv; a++) V.push(+(mf.v + a * o.vStep).toFixed(4));
    for (a = -nt; a <= nt; a++) TH.push(+(mf.theta + a * o.thStep).toFixed(4));
    var nV = V.length, nT = TH.length, N = nV * nT;
    var clean = new Uint8Array(N), twinClean = new Uint8Array(N), clear = new Float32Array(N).fill(NaN);
    var keLip = new Float32Array(N).fill(NaN), keEntry = new Float32Array(N).fill(NaN), minClear = new Float32Array(N).fill(NaN);
    for (var iv = 0; iv < nV; iv++) {
      for (var it = 0; it < nT; it++) {
        var s = PS.shot(qq, V[iv], TH[it]), c = iv * nT + it;
        if (s.twin.cls.result === "clean") twinClean[c] = 1;
        if (s.cls.result !== "clean") continue;
        clean[c] = 1; minClear[c] = s.cls.minClear;
        // up to the cell entry only: the classifier's verdict is made there, so later points are not checked by the model
        var L = lipInfo(s.path, seg, R, s.cls.i, mass);
        clear[c] = L.clear; keLip[c] = L.keLip; keEntry[c] = L.keEntry;
      }
      progress(0.1 + 0.5 * (iv + 1) / nV);
    }
    var sig = PS.HC_SIG, G = gaussShare(clean, V, TH, sig.sv, sig.sth);
    // cells whose scatter window is cut by the scan edge are left out of the statistics (their share is biased)
    var cells = [], nEdge = 0; for (c = 0; c < N; c++) if (clean[c]) { if (G.edge[c]) nEdge++; else cells.push(c); }
    var rhoClear = spearman(cells.map(function (k) { return clear[k]; }), cells.map(function (k) { return G.share[k]; }));
    var rhoKE = spearman(cells.map(function (k) { return keLip[k]; }), cells.map(function (k) { return G.share[k]; }));
    // the user's rule: most energy among shots that pass within nearCm of the lower lip
    var near = cells.filter(function (k) { return clear[k] <= o.nearM; });
    var rule = near.length ? near.reduce(function (a, b) { return keLip[b] > keLip[a] ? b : a; }) : -1;
    var robust = cells.length ? cells.reduce(function (a, b) { return G.share[b] > G.share[a] ? b : a; }) : -1;
    // 3D Monte Carlo (adds heading scatter) on cells spread over the clearance range, plus the two picks
    var byClear = cells.slice().sort(function (a, b) { return clear[a] - clear[b]; }), pickC = [];
    for (var m = 0; m < Math.min(o.mcCells, byClear.length); m++) pickC.push(byClear[Math.round(m * (byClear.length - 1) / Math.max(1, o.mcCells - 1))]);
    pickC = pickC.filter(function (k, i) { return pickC.indexOf(k) === i; });
    var mc = pickC.map(function (k, i) {
      var h = PS.hitChance(qq, V[Math.floor(k / nT)], TH[k % nT], { n: o.mcN, sets: ["nominal"] });
      progress(0.6 + 0.3 * (i + 1) / pickC.length);
      return { c: k, p: h.sets[0].p, lo: h.sets[0].lo, hi: h.sets[0].hi };
    });
    var rhoMC = spearman(mc.map(function (x) { return clear[x.c]; }), mc.map(function (x) { return x.p; }));
    function cellOut(k, n) {
      if (k < 0) return null;
      var v = V[Math.floor(k / nT)], th = TH[k % nT], h = PS.hitChance(qq, v, th, { n: n, sets: ["nominal"], twinAt: r.twin && r.twin.mostForgiving ? { v: r.twin.mostForgiving.v, theta: r.twin.mostForgiving.theta } : undefined });
      return { v: v, theta: th, rpm: PS.rpm(v, q.vu), clear: clear[k], keLip: keLip[k], keEntry: keEntry[k], share: G.share[k], edge: !!G.edge[k],
               hc: h.sets[0], twin: h.twin };
    }
    var out = { ok: true, d: o.d, V: V, TH: TH, clean: Array.from(clean), twinClean: Array.from(twinClean), clear: Array.from(clear),
      keLip: Array.from(keLip), keEntry: Array.from(keEntry), minClear: Array.from(minClear), share: Array.from(G.share), edge: Array.from(G.edge),
      nClean: cells.length + nEdge, nUsed: cells.length, nEdge: nEdge, nTwinClean: twinClean.reduce(function (a, b) { return a + b; }, 0), rhoClear: rhoClear, rhoKE: rhoKE, rhoMC: rhoMC,
      mc: mc.map(function (x) { return { v: V[Math.floor(x.c / nT)], theta: TH[x.c % nT], clear: clear[x.c], keLip: keLip[x.c], p: x.p, lo: x.lo, hi: x.hi }; }),
      rule: cellOut(rule, o.mcN2), robust: cellOut(robust, o.mcN2), nNear: near.length, seg: seg, sig: sig, note: PS.HC_NOTE,
      mostForgiving: { v: mf.v, theta: mf.theta } };
    progress(1);
    return out;
  }

  // one moving shot in the 3D model: the speed / angle looked up at the virtual distance (comp) and at the real one
  function sotmJob(q, o) {
    var qq = Object.assign({}, q, { x: -o.d, y: 0, move: { along: o.along, across: o.across } });
    function one(set) {
      if (!set) return null;
      var s = PS.shot(qq, set.v, set.theta);
      return { v: set.v, theta: set.theta, result: s.cls.result, twin: s.twin.cls.result, sideWall: s.sideWall && s.sideWall.hit ? true : false };
    }
    var still = PS.shot(Object.assign({}, q, { x: -o.d, y: 0 }), o.plain.v, o.plain.theta);
    return { comp: one(o.comp), plain: one(o.plain), still: still.cls.result };
  }

  function handle(m, post) {
    if (m.meta) { M.meta = m.meta; return; }
    if (!M.meta) { post({ id: m.id, error: "field data not loaded yet" }); return; }
    var q = m.q; q.meta = M.meta;
    var progress = function (f) { post({ id: m.id, progress: f }); };
    try {
      var res = m.job === "map" ? mapJob(q, m.o, progress) : m.job === "lip" ? lipJob(q, m.o, progress) : sotmJob(q, m.o);
      post({ id: m.id, result: res });
    } catch (e) { post({ id: m.id, error: String(e && e.stack || e) }); }
  }

  return { handle: handle, walkTol: walkTol, M: M, longestRun: longestRun, spearman: spearman, gaussShare: gaussShare, lipInfo: lipInfo,
    mapJob: mapJob, lipJob: lipJob, sotmJob: sotmJob, rad: rad };
});

