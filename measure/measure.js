// POLLEN measurement kit (PM-018): track a slow-motion side video by hand, then fit drag (Cd) from a no-spin shot and
// spin lift (Cl) from a backspin shot with the same settings (the twin test). Flight equations = viz/explorer/physics.js
// integrate (called directly); the fitting steps match src/fit_aero.py line for line (tests/test_fit_aero.py checks both
// on synthetic physics.js tracks). Everything runs in the page: files are read locally, nothing is uploaded.
// Labels: fitted numbers are derived (fits to the user's video); demo numbers and spin decay k are ASSUMED.
(function (root, factory) {
  "use strict";
  const isNode = typeof module !== "undefined" && module.exports;
  const PP = isNode ? require("../explorer/physics.js") : root.PollenPhysics;
  const api = factory(PP);
  if (isNode) module.exports = api;
  else {
    root.PollenMeasure = api;
    if (typeof document !== "undefined") {
      const go = function () { if (document.getElementById("measure-app")) api.ui(); };
      if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", go); else go();
    }
  }
})(typeof self !== "undefined" ? self : this, function (PP) {
  "use strict";
  // ball and air defaults: mass 24.95 g (AndyMark nominal, user/vendor), radius 35.5 mm (official nominal),
  // rho 1.204 kg/m^3 (20 C dry sea level, derived), spin decay k 0.03 1/s (ASSUMED, explorer default)
  const DEF = { rho: 1.204, mass: 0.02495, radius: 0.0355, k: 0.03, g: 9.80665 };
  const WHEEL_R = 0.049, CORR_FLAG = 0.995, CORR_NOTE = 0.9, REL_FLAG = 0.5, SEED = 20261031;
  const LIFT_NAMES = { single: ["Cl"], linear: ["c1"], capped: ["c1", "Cl_max"] };
  const LIFT_START = { single: [0.15], linear: [0.2], capped: [0.4, 0.25] };

  // ---------------------------------------------------------------- flight model (physics.js integrate)
  function physParams(p, Cd, lift, lp) {
    const q = Object.assign({}, DEF, p || {}, { Cd: Cd, c1: 0, clmax: 0, cl_table: null });
    if (lift === "single") q.cl_table = [[0, lp[0]]];               // flat table = one Cl for every S
    else if (lift === "linear") q.cl_table = [[1000, 1000 * lp[0]]]; // straight line c1 S (S < 1000)
    else if (lift === "capped") { q.c1 = lp[0]; q.clmax = lp[1]; }   // the explorer's min(c1 S, Cl_max)
    return q;
  }
  // positions at times t (s from the first tracked frame); spin {rpm} (ball, + = backspin toward +x) or {S0}
  function simulate(t, x0, z0, vx0, vz0, Cd, lift, lp, spin, p, dt) {
    dt = dt || 1e-3;
    const P = physParams(p, Cd, lift, lp || []), v0 = Math.hypot(vx0, vz0), thDeg = Math.atan2(vz0, vx0) * 180 / Math.PI;
    let S0 = 0;
    if (lift && spin) S0 = spin.rpm !== undefined ? (v0 > 0 ? spin.rpm * 2 * Math.PI / 60 * P.radius / v0 : 0) : spin.S0;
    let tmax = 0;
    for (let i = 0; i < t.length; i++) if (t[i] > tmax) tmax = t[i];
    const path = PP.integrate(v0, thDeg, S0, P, dt, tmax + 2 * dt, -1e9);
    const n = path.n, xs = new Float64Array(t.length), zs = new Float64Array(t.length);
    for (let i = 0; i < t.length; i++) {
      let j = Math.floor(t[i] / dt); j = j < 0 ? 0 : j > n - 2 ? n - 2 : j;
      const s = t[i] / dt - j, s2 = s * s, s3 = s2 * s;
      const h00 = 2 * s3 - 3 * s2 + 1, h10 = s3 - 2 * s2 + s, h01 = -2 * s3 + 3 * s2, h11 = s3 - s2;
      xs[i] = x0 + h00 * path.X[j] + h10 * dt * path.VX[j] + h01 * path.X[j + 1] + h11 * dt * path.VX[j + 1];
      zs[i] = z0 + h00 * path.Z[j] + h10 * dt * path.VZ[j] + h01 * path.Z[j + 1] + h11 * dt * path.VZ[j + 1];
    }
    return { x: xs, z: zs };
  }

  // ---------------------------------------------------------------- small linear algebra
  function solve(M, b) {
    const n = b.length, A = M.map(function (r, i) { return r.slice().concat([b[i]]); });
    for (let c = 0; c < n; c++) {
      let piv = c;
      for (let r = c + 1; r < n; r++) if (Math.abs(A[r][c]) > Math.abs(A[piv][c])) piv = r;
      if (!(Math.abs(A[piv][c]) > 1e-300)) return null;
      const tmp = A[c]; A[c] = A[piv]; A[piv] = tmp;
      for (let r = c + 1; r < n; r++) {
        const f = A[r][c] / A[c][c];
        for (let k = c; k <= n; k++) A[r][k] -= f * A[c][k];
      }
    }
    const x = new Array(n);
    for (let r = n - 1; r >= 0; r--) {
      let s = A[r][n];
      for (let k = r + 1; k < n; k++) s -= A[r][k] * x[k];
      x[r] = s / A[r][r];
    }
    return x;
  }
  function inverse(M) {
    const n = M.length, out = M.map(function () { return new Array(n).fill(0); });
    for (let c = 0; c < n; c++) {
      const e = new Array(n).fill(0); e[c] = 1;
      const col = solve(M, e);
      if (!col) return null;
      for (let r = 0; r < n; r++) out[r][c] = col[r];
    }
    return out;
  }
  function dot(a, b) { let s = 0; for (let i = 0; i < a.length; i++) s += a[i] * b[i]; return s; }

  // ---------------------------------------------------------------- Levenberg-Marquardt (same steps as fit_aero._lm)
  function jac(resid, th, r, scale) {
    const m = th.length, J = [];
    for (let i = 0; i < r.length; i++) J.push(new Float64Array(m));
    for (let c = 0; c < m; c++) {
      const h = 1e-6 * Math.max(Math.abs(th[c]), scale[c]), tp = th.slice(); tp[c] += h;
      const rp = resid(tp);
      for (let i = 0; i < r.length; i++) J[i][c] = (rp[i] - r[i]) / h;
    }
    return J;
  }
  function normalEq(J, r) {
    const m = J[0].length, A = [], g = new Array(m).fill(0);
    for (let a = 0; a < m; a++) A.push(new Array(m).fill(0));
    for (let i = 0; i < J.length; i++) {
      const row = J[i];
      for (let a = 0; a < m; a++) { g[a] += row[a] * r[i]; for (let b = a; b < m; b++) A[a][b] += row[a] * row[b]; }
    }
    for (let a = 0; a < m; a++) for (let b = 0; b < a; b++) A[a][b] = A[b][a];
    return { A: A, g: g };
  }
  function lm(resid, th0, scale, maxIter) {
    maxIter = maxIter || 60;
    let th = th0.slice(), r = resid(th), cost = dot(r, r), lam = 1e-3, rel = 1;
    for (let it = 0; it < maxIter; it++) {
      const J = jac(resid, th, r, scale), ne = normalEq(J, r);
      let improved = false;
      for (let k = 0; k < 12; k++) {
        const M = ne.A.map(function (row, i) { const q = row.slice(); q[i] += lam * Math.max(ne.A[i][i], 1e-30); return q; });
        const d = solve(M, ne.g);
        if (!d) { lam *= 10; continue; }
        const tn = th.map(function (v, i) { return v - d[i]; }), r2 = resid(tn), c2 = dot(r2, r2);
        if (c2 < cost) { rel = (cost - c2) / Math.max(cost, 1e-300); th = tn; r = r2; cost = c2; lam = Math.max(lam / 5, 1e-9); improved = true; break; }
        lam *= 8;
      }
      if (!improved || rel < 1e-12) break;
    }
    return { th: th, r: r, J: jac(resid, th, r, scale) };
  }

  function uncertainty(names, th, r, J) {
    const n = r.length, m = th.length, dof = Math.max(n - m, 1), s2 = dot(r, r) / dof;
    const A = normalEq(J, r).A, d = A.map(function (row, i) { return Math.sqrt(Math.max(row[i], 1e-300)); });
    const An = A.map(function (row, i) { return row.map(function (v, j) { return v / (d[i] * d[j]) + (i === j ? 1e-12 : 0); }); });
    const inv = inverse(An) || An.map(function (row, i) { return row.map(function (_, j) { return i === j ? 1e300 : 0; }); });
    const cov = inv.map(function (row, i) { return row.map(function (v, j) { return s2 * v / (d[i] * d[j]); }); });
    const sd = cov.map(function (row, i) { return Math.sqrt(Math.max(row[i], 0)); });
    const corr = cov.map(function (row, i) { return row.map(function (v, j) { return v / (Math.max(sd[i], 1e-300) * Math.max(sd[j], 1e-300)); }); });
    const zero = names.filter(function (_, i) { return A[i][i] < 1e-24; }), flags = [];
    zero.forEach(function (nm) { flags.push("the track does not depend on " + nm + " at all: it cannot be fitted from this shot"); });
    for (let i = 0; i < m; i++) for (let j = i + 1; j < m; j++)
      if (Math.abs(corr[i][j]) > CORR_FLAG && zero.indexOf(names[i]) < 0 && zero.indexOf(names[j]) < 0)
        flags.push("cannot separate " + names[i] + " and " + names[j] + " (correlation " + sgnF(corr[i][j], 3) + "): this track only sets a combination of the two");
    return { sd: sd, corr: corr, flags: flags, zero: zero };
  }
  function sgnF(v, d) { return (v >= 0 ? "+" : "") + v.toFixed(d); }
  function g3(v) { return Number(v).toPrecision(3).replace(/\.?0+e/, "e"); }
  function weakFlags(names, val, sd, corr, note, skip) {
    const out = [];
    names.forEach(function (nm, i) {
      if (i < 4 || (skip || []).indexOf(nm) >= 0 || 1.96 * sd[nm] <= REL_FLAG * Math.abs(val[nm])) return;
      let msg = nm + " is weakly set by this track" + (note || "") + ": 95 % half-width " + g3(1.96 * sd[nm]) + " is over half its value " + g3(val[nm]);
      let j = -1;
      names.forEach(function (_, k) { if (k !== i && (j < 0 || Math.abs(corr[i][k]) > Math.abs(corr[i][j]))) j = k; });
      if (j >= 0 && Math.abs(corr[i][j]) > CORR_NOTE) msg += ", mostly because it trades off against " + names[j] + " (correlation " + sgnF(corr[i][j], 3) + ")";
      out.push(msg);
    });
    return out;
  }
  function pack(names, th, r, J) {
    const u = uncertainty(names, th, r, J), val = {}, sd = {}, ci = {};
    names.forEach(function (nm, i) { val[nm] = th[i]; sd[nm] = u.sd[i]; ci[nm] = [th[i] - 1.96 * u.sd[i], th[i] + 1.96 * u.sd[i]]; });
    // rms_m = rms per coordinate (x and z residuals pooled), as fit_aero.py
    return { names: names, value: val, sd: sd, ci95: ci, rms_m: Math.sqrt(dot(r, r) / r.length), n: r.length / 2, corr: u.corr,
             flags: u.flags.concat(weakFlags(names, val, sd, u.corr, "", u.zero)), theta: th, r: r, zero: u.zero };
  }

  function guess(t, x, z) {
    const n = Math.min(t.length, 15);
    function fit2(y) {   // least-squares quadratic y = a + b t + c t^2 on the first n points
      const deg = n >= 4 ? 2 : 1, m = deg + 1, A = [], b = new Array(m).fill(0);
      for (let a = 0; a < m; a++) A.push(new Array(m).fill(0));
      for (let i = 0; i < n; i++) for (let a = 0; a < m; a++) { b[a] += Math.pow(t[i], a) * y[i]; for (let c = 0; c < m; c++) A[a][c] += Math.pow(t[i], a + c); }
      const s = solve(A, b) || [y[0], 0, 0];
      return [s[0], s[1]];
    }
    const fx = fit2(x), fz = fit2(z);
    return [fx[0], fz[0], fx[1], fz[1]];
  }
  function orient(x) {
    const s = x[x.length - 1] >= x[0] ? 1 : -1;
    return { x: Array.from(x, function (v) { return v * s; }), sign: s };
  }
  function residFor(model, xd, zd) {
    return function (th) {
      const m = model(th), n = xd.length, r = new Float64Array(2 * n);
      for (let i = 0; i < n; i++) { r[i] = m.x[i] - xd[i]; r[n + i] = m.z[i] - zd[i]; }
      return r;
    };
  }
  function percentile(a, q) {
    const s = Array.from(a).sort(function (u, v) { return u - v; }), pos = (s.length - 1) * q / 100, lo = Math.floor(pos), hi = Math.ceil(pos);
    return s[lo] + (s[hi] - s[lo]) * (pos - lo);
  }
  // residual bootstrap: resample (dx, dz) residual pairs onto the fitted path and refit; cdDraw adds Cd ~ N(Cd_A, sd_A)
  function bootstrap(fitted, makeResid, th, r, scale, names, nboot, seed, cdDraw) {
    const rnd = PP.mulberry32(seed), n = r.length / 2, draws = [];
    function gauss() { const u1 = 1 - rnd(), u2 = rnd(); return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2); }
    for (let b = 0; b < nboot; b++) {
      const xd = new Float64Array(n), zd = new Float64Array(n);
      for (let i = 0; i < n; i++) { const k = Math.floor(rnd() * n); xd[i] = fitted.x[i] + r[k]; zd[i] = fitted.z[i] + r[n + k]; }
      const extra = cdDraw ? cdDraw(gauss) : null;
      draws.push(lm(makeResid(xd, zd, extra), th, scale, 25).th);
    }
    const out = { n: nboot };
    names.forEach(function (nm, i) {
      const col = draws.map(function (d) { return d[i]; }), mu = col.reduce(function (a, v) { return a + v; }, 0) / col.length;
      const sd = Math.sqrt(col.reduce(function (a, v) { return a + (v - mu) * (v - mu); }, 0) / Math.max(col.length - 1, 1));
      out[nm] = { sd: sd, ci95: [percentile(col, 2.5), percentile(col, 97.5)] };
    });
    return out;
  }

  // ---------------------------------------------------------------- the two fits (same as fit_aero.fit_nospin / fit_lift)
  function fitNoSpin(track, opts) {
    opts = opts || {};
    const t = Array.from(track.t), o = orient(track.x), x = o.x, z = Array.from(track.z), p = opts.p;
    // fitScale: also fit len_scale = video metres / true metres (the gravity check, as fit_aero.fit_nospin)
    const fs = !!opts.fitScale, lsSd = opts.lenScaleSd || 0;
    const names = ["x0", "z0", "vx0", "vz0", "Cd"].concat(fs ? ["len_scale"] : []), scale = [0.1, 0.1, 1, 1, 0.1].concat(fs ? [0.01] : []);
    const model = function (th) {
      const m = simulate(t, th[0], th[1], th[2], th[3], th[4], null, null, null, p);
      if (fs) rescale(m, th);   // scale about the first tracked point, as fit_aero.fit_nospin
      return m;
    };
    const fit = lm(residFor(model, x, z), guess(t, x, z).concat([0.5], fs ? [1] : []), scale);
    const out = pack(names, fit.th, fit.r, fit.J);
    out.sd_total = Object.assign({}, out.sd);
    if (lsSd > 0 && !fs) {   // carry the clicked-scale error into Cd (refit at scale 1 +/- sd)
      const sh = names.map(function () { return 0; });
      [1, -1].forEach(function (g) {
        const k = 1 + g * lsSd, f2 = lm(residFor(model, x.map(function (v) { return v / k; }), z.map(function (v) { return v / k; })), fit.th, scale);
        f2.th.forEach(function (v, i) { sh[i] += Math.abs(v - fit.th[i]) / 2; });
      });
      out.sd_scale_part = {};
      names.forEach(function (nm, i) { out.sd_scale_part[nm] = sh[i]; out.sd_total[nm] = Math.hypot(out.sd[nm], sh[i]); });
    }
    if (opts.boot) out.boot = bootstrap(model(fit.th), function (xd, zd) { return residFor(model, xd, zd); }, fit.th, fit.r, scale, names, opts.boot, opts.seed || SEED);
    out.v0 = Math.hypot(fit.th[2], fit.th[3]); out.theta_deg = Math.atan2(fit.th[3], fit.th[2]) * 180 / Math.PI;
    out.sign = o.sign; out.kind = "nospin"; out.t = t;
    out.path = function (tt) { const m = simulate(tt, fit.th[0], fit.th[1], fit.th[2], fit.th[3], fit.th[4], null, null, null, p); return fs ? rescale(m, fit.th) : m; };
    return out;
  }

  function fitLift(track, opts) {
    const lift = opts.lift || "single", lnames = LIFT_NAMES[lift], nl = lnames.length, fitSpin = !!opts.fitSpin;
    const spin = opts.spin || { S0: 1 }, cd = opts.cd, cdSd = opts.cdSd || 0, p = opts.p;
    const ls = opts.lenScale || 1, lsSd = opts.lenScaleSd || 0;   // shot A's gravity check, or the clicked-scale error
    const t = Array.from(track.t), o = orient(track.x), x = o.x, z = Array.from(track.z);
    const names = ["x0", "z0", "vx0", "vz0"].concat(lnames, fitSpin ? ["S0"] : []);
    const scale = [0.1, 0.1, 1, 1].concat(lnames.map(function () { return 0.1; }), fitSpin ? [0.5] : []);
    const modelCd = function (cdv) {
      return function (th) { return simulate(t, th[0], th[1], th[2], th[3], cdv, lift, th.slice(4, 4 + nl), fitSpin ? { S0: th[4 + nl] } : spin, p); };
    };
    const th0 = guess(t, x, z).concat(opts.cl0 || LIFT_START[lift], fitSpin ? [spin.S0 !== undefined ? spin.S0 : 1] : []);
    const div = function (arr, k) { return arr.map(function (v) { return v / k; }); };
    const rf = function (cdv, sv, xd, zd) { return residFor(modelCd(cdv), div(xd, sv), div(zd, sv)); };
    const fit = lm(rf(cd, ls, x, z), th0, scale);
    const th = fit.th, out = pack(names, th, fit.r, fit.J);
    out.cd_used = cd; out.len_scale_used = ls;
    out.sd_total = Object.assign({}, out.sd);
    if (cdSd > 0 || lsSd > 0) {   // carry A's Cd error and the scale error (refit at +/- 1 sd, add in quadrature)
      const part = function (args) {
        const sh = names.map(function () { return 0; });
        args.forEach(function (a) { lm(rf(a[0], a[1], x, z), th, scale).th.forEach(function (v, i) { sh[i] += Math.abs(v - th[i]) / 2; }); });
        return sh;
      };
      const pc = cdSd > 0 ? part([[cd + cdSd, ls], [cd - cdSd, ls]]) : names.map(function () { return 0; });
      const ps = lsSd > 0 ? part([[cd, ls + lsSd], [cd, ls - lsSd]]) : names.map(function () { return 0; });
      out.sd_cd_part = {}; out.sd_scale_part = {};
      names.forEach(function (nm, i) { out.sd_cd_part[nm] = pc[i]; out.sd_scale_part[nm] = ps[i]; out.sd_total[nm] = Math.sqrt(out.sd[nm] * out.sd[nm] + pc[i] * pc[i] + ps[i] * ps[i]); });
      out.flags = out.flags.filter(function (f) { return f.indexOf("weakly set") < 0; })
        .concat(weakFlags(names, out.value, out.sd_total, out.corr, " (with A's Cd and scale error)", out.zero));
    }
    if (opts.boot) {
      const fitted = modelCd(cd)(th);
      for (let i = 0; i < t.length; i++) { fitted.x[i] *= ls; fitted.z[i] *= ls; }
      out.boot = bootstrap(fitted, function (xd, zd, d) { return rf(d[0], d[1], xd, zd); }, th, fit.r, scale, names, opts.boot, opts.seed || SEED,
        function (gauss) { return [cd + (cdSd > 0 ? gauss() * cdSd : 0), ls + (lsSd > 0 ? gauss() * lsSd : 0)]; });
    }
    const v0 = Math.hypot(th[2], th[3]), R = Object.assign({}, DEF, p || {}).radius;
    out.v0 = v0; out.theta_deg = Math.atan2(th[3], th[2]) * 180 / Math.PI;
    const S0 = fitSpin ? th[4 + nl] : spin.rpm !== undefined ? (v0 > 0 ? spin.rpm * 2 * Math.PI / 60 * R / v0 : 0) : spin.S0;
    out.S0 = S0;
    out.S_range = sRange(t, th, cd, S0, p);
    const tw = simulate(t, th[0], th[1], th[2], th[3], cd, null, null, null, p);
    const bs = simulate(t, th[0], th[1], th[2], th[3], cd, lift, th.slice(4, 4 + nl), { S0: S0 }, p);
    let dmax = 0;
    for (let i = 0; i < t.length; i++) dmax = Math.max(dmax, Math.hypot(bs.x[i] - tw.x[i], bs.z[i] - tw.z[i]));
    out.twin_dz_end = bs.z[t.length - 1] - tw.z[t.length - 1]; out.twin_dx_end = bs.x[t.length - 1] - tw.x[t.length - 1]; out.twin_dmax = dmax;
    out.table = table(lift, th.slice(4, 4 + nl), out.S_range);
    const sd0 = out.sd_total[lnames[0]], v = out.value[lnames[0]];
    out.lift_detected = !(v - 1.96 * sd0 <= 0 && 0 <= v + 1.96 * sd0);
    out.sign = o.sign; out.kind = "backspin"; out.lift = lift; out.t = t;
    out.path = function (tt) { return scaled(simulate(tt, th[0], th[1], th[2], th[3], cd, lift, th.slice(4, 4 + nl), { S0: S0 }, p), ls); };
    out.twinPath = function (tt) { return scaled(simulate(tt, th[0], th[1], th[2], th[3], cd, null, null, null, p), ls); };
    return out;
  }
  // gravity check: x0 + s (x - x0), z0 + s (z - z0); x0, z0 are then video metres and do not trade off against s
  function rescale(m, th) { for (let i = 0; i < m.x.length; i++) { m.x[i] = th[0] + th[5] * (m.x[i] - th[0]); m.z[i] = th[1] + th[5] * (m.z[i] - th[1]); } return m; }
  function scaled(m, k) { for (let i = 0; i < m.x.length; i++) { m.x[i] *= k; m.z[i] *= k; } return m; }
  function sRange(t, th, cd, S0, p) {
    const P = Object.assign({}, DEF, p || {}), R = P.radius, v0 = Math.hypot(th[2], th[3]), w0 = S0 * v0 / R;
    const tt = [t[0], t[0] + 1e-3, t[t.length - 1] - 1e-3, t[t.length - 1]], s = simulate(tt, th[0], th[1], th[2], th[3], cd, null, null, null, p);
    const va = Math.hypot(s.x[1] - s.x[0], s.z[1] - s.z[0]) / 1e-3, vb = Math.hypot(s.x[3] - s.x[2], s.z[3] - s.z[2]) / 1e-3;
    const Sa = Math.abs(w0) * Math.exp(-P.k * t[0]) * R / Math.max(va, 1e-9), Sb = Math.abs(w0) * Math.exp(-P.k * t[t.length - 1]) * R / Math.max(vb, 1e-9);
    return [Math.min(Sa, Sb), Math.max(Sa, Sb)];
  }
  function table(lift, lp, sr) {
    if (lift === "single") return ((sr[0] + sr[1]) / 2).toFixed(2) + ":" + lp[0].toFixed(3);
    if (lift === "linear") return "0:0, " + sr[1].toFixed(2) + ":" + (lp[0] * sr[1]).toFixed(3);
    const knee = lp[0] > 0 ? lp[1] / lp[0] : sr[1];
    return "0:0, " + knee.toFixed(2) + ":" + lp[1].toFixed(3);
  }

  // ---------------------------------------------------------------- synthetic tracks (demo and tests)
  // truth: {v, thDeg, x0, z0, Cd, lift, lp, S0}; frames every `step` captured frames at fps; noise sigma in metres.
  function synth(truth, o) {
    o = o || {};
    const fps = o.fps || 240, step = o.step || 1, nF = o.frames || 200, sig = o.sigma || 0, p = o.p;
    const sub = 4, dt = 1 / (fps * sub), P = physParams(p, truth.Cd, truth.lift || null, truth.lp || []);
    const path = PP.integrate(truth.v, truth.thDeg, truth.lift ? truth.S0 || 0 : 0, P, dt, (nF + 1) / fps, -1e9);
    const rnd = PP.mulberry32(o.seed || SEED);
    function gauss() { const u1 = 1 - rnd(), u2 = rnd(); return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2); }
    const out = { frame: [], t: [], x: [], z: [], xTrue: [], zTrue: [] };
    for (let f = 0; f < nF; f += step) {
      const j = f * sub;
      if (j >= path.n) break;
      const xt = truth.x0 + path.X[j], zt = truth.z0 + path.Z[j];
      out.frame.push(f); out.t.push(f / fps); out.xTrue.push(xt); out.zTrue.push(zt);
      out.x.push(xt + sig * gauss()); out.z.push(zt + sig * gauss());
    }
    return out;
  }

  // ---------------------------------------------------------------- CSV (read by src/fit_aero.py parse_csv)
  function toCSV(meta, rows) {
    const lines = ["# tool=pollen-measure v1 (PM-018); x_m, z_m are levelled and scaled, z up; t_s = frame / capture_fps"];
    Object.keys(meta).forEach(function (k) { if (meta[k] !== "" && meta[k] !== undefined && meta[k] !== null) lines.push("# " + k + "=" + meta[k]); });
    lines.push("shot,frame,t_s,x_m,z_m,x_px,y_px");
    rows.forEach(function (r) { lines.push([r.shot, r.frame, r.t.toFixed(6), r.x.toFixed(5), r.z.toFixed(5), r.px.toFixed(2), r.py.toFixed(2)].join(",")); });
    return lines.join("\n") + "\n";
  }
  function parseCSV(text) {
    const meta = {}, rows = [];
    let cols = null;
    String(text).split(/\r?\n/).forEach(function (line) {
      line = line.trim();
      if (!line) return;
      if (line[0] === "#") { const b = line.slice(1).trim(), i = b.indexOf("="); if (i > 0) meta[b.slice(0, i).trim()] = b.slice(i + 1).trim(); return; }
      const parts = line.split(",").map(function (s) { return s.trim(); });
      if (!cols) { cols = parts; return; }
      const r = {}; cols.forEach(function (c, i) { r[c] = parts[i]; });
      rows.push({ shot: r.shot || "A", frame: +r.frame, t: +r.t_s, x: +r.x_m, z: +r.z_m, px: r.x_px === undefined || r.x_px === "" ? NaN : +r.x_px, py: r.y_px === undefined || r.y_px === "" ? NaN : +r.y_px });
    });
    return { meta: meta, rows: rows };
  }

  // ---------------------------------------------------------------- page UI
  function ui() { return makeUI(); }

  function makeUI() {
    const $ = function (id) { return document.getElementById(id); };
    const DPR = function () { return window.devicePixelRatio || 1; };
    const shotDefaults = function (kind) { return { kind: kind, src: null, nFrames: 0, w: 1280, h: 720, fps: 240, fileFps: 240, pts: {}, fit: null, meta: {}, name: "" }; };
    const S = { shot: "A", mode: "track", step: 1, frame: 0, loupe: true, mouse: null,
      shots: { A: shotDefaults("nospin"), B: shotDefaults("backspin") },
      cal: { p: [], mm: 1000 }, level: { p: [] }, demoTruth: null, busy: false };
    const cur = function () { return S.shots[S.shot]; };
    const cv = $("cv"), ctx = cv.getContext("2d"), lp = $("loupe"), lctx = lp.getContext("2d");
    let view = { s: 1, ox: 0, oy: 0 };
    const frameCanvas = document.createElement("canvas"), fctx = frameCanvas.getContext("2d");
    let frameReady = -1;

    // ---- calibration: pixel <-> metre (origin at the bottom-left of the frame, z up, levelled)
    function mPerPx() {
      const c = S.cal;
      if (c.p.length < 2 || !(c.mm > 0)) return null;
      const d = Math.hypot(c.p[1][0] - c.p[0][0], c.p[1][1] - c.p[0][1]);
      return d > 0 ? c.mm / 1000 / d : null;
    }
    function clickSd() {   // relative error of the clicked scale: 0.5 px per end (ASSUMED) over its length
      const c = S.cal.p;
      if (c.length < 2) return 0;
      const L = Math.hypot(c[1][0] - c[0][0], c[1][1] - c[0][1]);
      return L > 0 ? Math.SQRT2 * 0.5 / L : 0;
    }
    function levelRad() {
      const l = S.level.p;
      if (l.length < 2) return 0;
      let a = Math.atan2(l[1][1] - l[0][1], l[1][0] - l[0][0]);
      if (a > Math.PI / 2) a -= Math.PI; if (a < -Math.PI / 2) a += Math.PI;
      return a;
    }
    function toM(px, py, H) {
      const s = mPerPx(), a = levelRad(), c = Math.cos(a), si = Math.sin(a), yy = py - H;
      return { x: s * (px * c + yy * si), z: -s * (-px * si + yy * c) };
    }
    function toPx(x, z, H) {
      const s = mPerPx(), a = levelRad(), c = Math.cos(a), si = Math.sin(a), u = x / s, w = -z / s;
      return { px: u * c - w * si, py: u * si + w * c + H };
    }

    // ---- frames
    function setStatus(msg) { $("status").textContent = msg; }
    function nFrames() { return cur().nFrames; }
    function gotoFrame(i) {
      const sh = cur();
      if (!sh.nFrames) { S.frame = 0; draw(); return; }
      S.frame = Math.max(0, Math.min(sh.nFrames - 1, i | 0));
      $("fslider").max = String(sh.nFrames - 1); $("fslider").value = String(S.frame);
      loadFrame();
    }
    function loadFrame() {
      const sh = cur(), src = sh.src, want = S.frame;
      frameReady = -1;
      if (!src) { draw(); return; }
      frameCanvas.width = sh.w; frameCanvas.height = sh.h;
      if (src.kind === "demo") { src.draw(fctx, want); frameReady = want; draw(); return; }
      if (src.kind === "images") {
        const img = src.imgs[want];
        if (img.complete && img.naturalWidth) { fctx.drawImage(img, 0, 0, sh.w, sh.h); frameReady = want; draw(); }
        else img.onload = function () { if (S.frame === want) loadFrame(); };
        return;
      }
      const v = src.el, tt = (want + 0.5) / sh.fileFps;
      const done = function () { if (S.frame !== want) return; fctx.drawImage(v, 0, 0, sh.w, sh.h); frameReady = want; draw(); };
      if (Math.abs(v.currentTime - tt) < 1e-4 && v.readyState >= 2) { done(); return; }
      v.onseeked = done;
      try { v.currentTime = Math.min(tt, Math.max(0, v.duration - 1e-3)); } catch (_) { /* ignore */ }
      draw();
    }
    function loadFiles(files) {
      const sh = cur();
      files = Array.from(files || []);
      if (!files.length) return;
      if (files[0].type.indexOf("video") === 0 || /\.(mp4|mov|m4v|webm)$/i.test(files[0].name)) {
        const v = document.createElement("video");
        v.muted = true; v.playsInline = true; v.preload = "auto";
        v.src = URL.createObjectURL(files[0]);
        v.onloadedmetadata = function () {
          sh.src = { kind: "video", el: v }; sh.w = v.videoWidth; sh.h = v.videoHeight; sh.name = files[0].name;
          sh.nFrames = Math.max(1, Math.floor(v.duration * sh.fileFps));
          setStatus("Shot " + S.shot + ": " + files[0].name + ", " + sh.w + "×" + sh.h + ", " + sh.nFrames + " frames at the file rate " + sh.fileFps + " fps");
          fitView(); gotoFrame(0); refresh();
        };
        v.onerror = function () { setStatus("This browser cannot decode that video. Export it as MP4 (H.264) or as numbered images."); };
        return;
      }
      files.sort(function (a, b) { return a.name.localeCompare(b.name, undefined, { numeric: true }); });
      const imgs = files.map(function (f) { const im = new Image(); im.src = URL.createObjectURL(f); return im; });
      imgs[0].onload = function () {
        sh.src = { kind: "images", imgs: imgs }; sh.w = imgs[0].naturalWidth; sh.h = imgs[0].naturalHeight; sh.nFrames = imgs.length; sh.name = files[0].name + " …";
        setStatus("Shot " + S.shot + ": " + imgs.length + " images, " + sh.w + "×" + sh.h);
        fitView(); gotoFrame(0); refresh();
      };
    }

    // ---- view + drawing
    function fitView() {
      const sh = cur(), r = cv.getBoundingClientRect(), W = r.width, H = r.height;
      const s = Math.min(W / sh.w, H / sh.h);
      view = { s: s, ox: (W - sh.w * s) / 2, oy: (H - sh.h * s) / 2 };
    }
    function sizeCanvas() {
      const r = cv.getBoundingClientRect(), d = DPR();
      cv.width = Math.round(r.width * d); cv.height = Math.round(r.height * d);
      fitView(); draw();
    }
    function f2c(px, py) { return [view.ox + px * view.s, view.oy + py * view.s]; }
    function c2f(cx, cy) { return [(cx - view.ox) / view.s, (cy - view.oy) / view.s]; }
    function sortedPts(sh) { return Object.keys(sh.pts).map(Number).sort(function (a, b) { return a - b; }); }
    function fitPathPx(sh) {
      if (!sh.fit || !mPerPx()) return null;
      const tt = [], t1 = sh.fit.t[sh.fit.t.length - 1];
      for (let k = 0; k <= 120; k++) tt.push(t1 * k / 120);
      const m = sh.fit.path(tt), tw = sh.fit.twinPath ? sh.fit.twinPath(tt) : null;
      const conv = function (q) { const o = []; for (let i = 0; i < tt.length; i++) o.push(toPx(q.x[i] * sh.fit.sign, q.z[i], sh.h)); return o; };
      return { fit: conv(m), twin: tw ? conv(tw) : null };
    }
    function draw() {
      const d = DPR(), W = cv.width / d, H = cv.height / d, sh = cur();
      ctx.setTransform(d, 0, 0, d, 0, 0);
      ctx.fillStyle = "#05080b"; ctx.fillRect(0, 0, W, H);
      if (sh.src && frameReady === S.frame) ctx.drawImage(frameCanvas, view.ox, view.oy, sh.w * view.s, sh.h * view.s);
      else if (!sh.src) {
        ctx.strokeStyle = "#24323f"; ctx.strokeRect(view.ox + 0.5, view.oy + 0.5, sh.w * view.s - 1, sh.h * view.s - 1);
        ctx.fillStyle = "#8d9caa"; ctx.font = "14px system-ui, sans-serif"; ctx.textAlign = "center";
        ctx.fillText(sortedPts(sh).length ? "No video for shot " + S.shot + " (points from pasted CSV)" : "Load a slow-motion video or image sequence for shot " + S.shot + ", or press Load demo", W / 2, H / 2);
        ctx.textAlign = "left";
      }
      // calibration and level lines
      const mark = function (pts, col, label) {
        ctx.strokeStyle = col; ctx.fillStyle = col; ctx.lineWidth = 2; ctx.setLineDash([6, 4]);
        if (pts.length === 2) { const a = f2c(pts[0][0], pts[0][1]), b = f2c(pts[1][0], pts[1][1]); ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke(); ctx.font = "12px ui-monospace, Consolas, monospace"; ctx.fillText(label, b[0] + 6, b[1] - 6); }
        ctx.setLineDash([]);
        pts.forEach(function (p) { const c = f2c(p[0], p[1]); ctx.beginPath(); ctx.moveTo(c[0] - 7, c[1]); ctx.lineTo(c[0] + 7, c[1]); ctx.moveTo(c[0], c[1] - 7); ctx.lineTo(c[0], c[1] + 7); ctx.stroke(); });
      };
      mark(S.cal.p, "#5fb3ff", S.cal.mm + " mm");
      mark(S.level.p, "#c792ea", "level");
      // other shot faint, this shot bright
      ["A", "B"].forEach(function (k) {
        const s2 = S.shots[k], mine = k === S.shot, col = k === "A" ? "#a9b4bf" : "#f4c430";
        if (!mine && (s2.w !== sh.w || s2.h !== sh.h)) return;
        sortedPts(s2).forEach(function (f) {
          const p = s2.pts[f], c = f2c(p[0], p[1]);
          ctx.globalAlpha = mine ? 1 : 0.35; ctx.fillStyle = col;
          ctx.beginPath(); ctx.arc(c[0], c[1], mine && f === S.frame ? 5 : 3, 0, 2 * Math.PI); ctx.fill();
          if (mine && f === S.frame) { ctx.strokeStyle = "#ffffff"; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.arc(c[0], c[1], 9, 0, 2 * Math.PI); ctx.stroke(); }
          ctx.globalAlpha = 1;
        });
        const fp = fitPathPx(s2);
        if (fp) {
          const line = function (arr, dash) { ctx.beginPath(); arr.forEach(function (q, i) { const c = f2c(q.px, q.py); if (i) ctx.lineTo(c[0], c[1]); else ctx.moveTo(c[0], c[1]); }); ctx.setLineDash(dash); ctx.stroke(); ctx.setLineDash([]); };
          ctx.strokeStyle = col; ctx.globalAlpha = mine ? 0.9 : 0.35; ctx.lineWidth = 2; line(fp.fit, []);
          if (fp.twin) { ctx.strokeStyle = "#a9b4bf"; line(fp.twin, [5, 5]); }
          ctx.globalAlpha = 1;
        }
      });
      // HUD
      const n = sortedPts(sh).length;
      $("hud").textContent = "Shot " + S.shot + (sh.kind === "nospin" ? " (no spin)" : " (backspin)") + " · frame " + (sh.nFrames ? S.frame + " / " + (sh.nFrames - 1) : "-") +
        " · t " + (S.frame / sh.fps).toFixed(4) + " s · " + n + " points · mode: " + ({ track: "click the ball centre", cal: "click both ends of the scale", level: "click two points on a level line" })[S.mode];
      drawLoupe();
    }
    function drawLoupe() {
      const show = S.loupe && S.mouse && cur().src;
      lp.style.display = show ? "block" : "none";
      if (!show) return;
      const d = DPR(), Z = 6, L = lp.clientWidth || 150;
      lp.width = Math.round(L * d); lp.height = Math.round(L * d);
      lctx.setTransform(d, 0, 0, d, 0, 0);
      lctx.imageSmoothingEnabled = false;
      lctx.fillStyle = "#05080b"; lctx.fillRect(0, 0, L, L);
      const f = c2f(S.mouse[0], S.mouse[1]), half = L / Z / 2;
      if (frameReady === S.frame) lctx.drawImage(frameCanvas, f[0] - half, f[1] - half, 2 * half, 2 * half, 0, 0, L, L);
      const p = cur().pts[S.frame];
      if (p) { lctx.fillStyle = cur().kind === "nospin" ? "#a9b4bf" : "#f4c430"; lctx.beginPath(); lctx.arc(L / 2 + (p[0] - f[0]) * Z, L / 2 + (p[1] - f[1]) * Z, 3, 0, 2 * Math.PI); lctx.fill(); }
      lctx.strokeStyle = "#ffffff"; lctx.lineWidth = 1; lctx.beginPath();
      lctx.moveTo(L / 2, 0); lctx.lineTo(L / 2, L / 2 - 6); lctx.moveTo(L / 2, L / 2 + 6); lctx.lineTo(L / 2, L);
      lctx.moveTo(0, L / 2); lctx.lineTo(L / 2 - 6, L / 2); lctx.moveTo(L / 2 + 6, L / 2); lctx.lineTo(L, L / 2); lctx.stroke();
    }

    // ---- input
    cv.addEventListener("mousemove", function (e) { const r = cv.getBoundingClientRect(); S.mouse = [e.clientX - r.left, e.clientY - r.top]; drawLoupe(); });
    cv.addEventListener("mouseleave", function () { S.mouse = null; drawLoupe(); });
    cv.addEventListener("click", function (e) {
      const r = cv.getBoundingClientRect(), f = c2f(e.clientX - r.left, e.clientY - r.top), sh = cur();
      if (f[0] < 0 || f[1] < 0 || f[0] > sh.w || f[1] > sh.h) return;
      if (S.mode === "cal") { if (S.cal.p.length >= 2) S.cal.p = []; S.cal.p.push(f); if (S.cal.p.length === 2) setMode("track"); }
      else if (S.mode === "level") { if (S.level.p.length >= 2) S.level.p = []; S.level.p.push(f); if (S.level.p.length === 2) setMode("track"); }
      else { sh.pts[S.frame] = f; sh.fit = null; if (sh.nFrames) gotoFrame(S.frame + S.step); }
      refresh();
    });
    document.addEventListener("keydown", function (e) {
      const tag = (e.target && e.target.tagName) || "";
      if (/INPUT|TEXTAREA|SELECT/.test(tag)) return;
      const big = e.shiftKey ? 10 : S.step;
      if (e.key === "ArrowRight" || e.key === ".") { gotoFrame(S.frame + big); e.preventDefault(); }
      else if (e.key === "ArrowLeft" || e.key === ",") { gotoFrame(S.frame - big); e.preventDefault(); }
      else if (e.key === "Delete" || e.key === "Backspace") { delete cur().pts[S.frame]; cur().fit = null; refresh(); e.preventDefault(); }
      else if (e.key === "z" || e.key === "Z") { S.loupe = !S.loupe; $("loupe-on").checked = S.loupe; drawLoupe(); }
    });
    function setMode(m) {
      S.mode = m;
      Array.from($("mode-seg").children).forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.v === m)); });
      draw();
    }
    function setShot(k) {
      S.shot = k;
      Array.from($("shot-seg").children).forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.v === k)); });
      const sh = cur();
      $("fps").value = sh.fps; $("ffps").value = sh.fileFps;
      $("brpm").value = sh.meta.ball_rpm || ""; $("wrpm").value = sh.meta.wheel_rpm || "";
      $("spin-row").style.display = k === "B" ? "" : "none";
      fitView(); gotoFrame(S.frame); refresh();
    }

    // ---- rows / CSV / chart / results
    function ballP() {
      const num = function (id, d) { const v = parseFloat($(id).value); return isFinite(v) && v > 0 ? v : d; };
      return { mass: num("mass", 24.95) / 1000, radius: num("diam", 71) / 2000, rho: num("rho", DEF.rho), k: (function () { const v = parseFloat($("kdec").value); return isFinite(v) && v >= 0 ? v : DEF.k; })() };
    }
    function trackOf(k) {
      const sh = S.shots[k], fr = sortedPts(sh);
      if (!mPerPx() || fr.length < 6) return null;
      const t = [], x = [], z = [], f0 = fr[0];
      fr.forEach(function (f) { const p = sh.pts[f], m = toM(p[0], p[1], sh.h); t.push((f - f0) / sh.fps); x.push(m.x); z.push(m.z); });
      return { t: t, x: x, z: z, frames: fr };
    }
    function spinOf() {
      const mode = $("spinsrc").value, rpm = parseFloat(S.shots.B.meta.ball_rpm);
      if (mode === "rpm" && isFinite(rpm) && rpm !== 0) return { spin: { rpm: rpm }, fitSpin: false, label: "ball " + rpm + " rpm (user, measured on video)" };
      if (mode === "fit") return { spin: { S0: 1 }, fitSpin: true, label: "S0 fitted (start 1.0)" };
      return { spin: { S0: 1 }, fitSpin: false, label: "S0 = 1.0 ideal hood (ASSUMED)" + (mode === "rpm" ? " because no ball rpm was entered" : "") };
    }
    function buildCSV() {
      const rows = [], meta = { m_per_px: mPerPx() ? mPerPx().toPrecision(7) : "", level_deg: (levelRad() * 180 / Math.PI).toFixed(3), cal_mm: S.cal.mm,
        cal_px: S.cal.p.map(function (p) { return p[0].toFixed(1) + " " + p[1].toFixed(1); }).join(" "),
        level_px: S.level.p.map(function (p) { return p[0].toFixed(1) + " " + p[1].toFixed(1); }).join(" ") };
      const bp = ballP(); meta.mass = bp.mass; meta.radius = bp.radius; meta.rho = bp.rho; meta.k = bp.k;
      ["A", "B"].forEach(function (k) {
        const sh = S.shots[k];
        meta[k + ".kind"] = sh.kind; meta[k + ".capture_fps"] = sh.fps; meta[k + ".file_fps"] = sh.fileFps; meta[k + ".frame_h_px"] = sh.h; meta[k + ".frame_w_px"] = sh.w;
        meta[k + ".source"] = sh.name.replace(/[\r\n,=]/g, " ");
        if (sh.meta.ball_rpm) meta[k + ".ball_rpm"] = sh.meta.ball_rpm;
        if (sh.meta.wheel_rpm) meta[k + ".wheel_rpm"] = sh.meta.wheel_rpm;
        if (k === "B" && $("spinsrc").value !== "rpm") meta["B.S0"] = 1;
        const fr = sortedPts(sh);
        if (!fr.length) return;
        fr.forEach(function (f) {
          const p = sh.pts[f], m = mPerPx() ? toM(p[0], p[1], sh.h) : { x: NaN, z: NaN };
          rows.push({ shot: k, frame: f, t: (f - fr[0]) / sh.fps, x: m.x, z: m.z, px: p[0], py: p[1] });
        });
      });
      return toCSV(meta, rows);
    }
    function importCSV(text) {
      const d = parseCSV(text), m = d.meta;
      const pair = function (s) { const v = String(s || "").split(/\s+/).map(Number).filter(isFinite); const o = []; for (let i = 0; i + 1 < v.length; i += 2) o.push([v[i], v[i + 1]]); return o; };
      S.cal.p = pair(m.cal_px); S.cal.mm = +m.cal_mm || 1000; $("calmm").value = S.cal.mm;
      S.level.p = pair(m.level_px);
      if (+m.mass) $("mass").value = (+m.mass * 1000).toFixed(2);
      if (+m.radius) $("diam").value = (+m.radius * 2000).toFixed(1);
      if (+m.rho) $("rho").value = m.rho;
      if (m.k !== undefined) $("kdec").value = m.k;
      ["A", "B"].forEach(function (k) {
        const sh = S.shots[k];
        sh.fps = +m[k + ".capture_fps"] || sh.fps; sh.fileFps = +m[k + ".file_fps"] || sh.fileFps;
        sh.h = +m[k + ".frame_h_px"] || sh.h; sh.w = +m[k + ".frame_w_px"] || sh.w;
        sh.meta.ball_rpm = m[k + ".ball_rpm"] || ""; sh.meta.wheel_rpm = m[k + ".wheel_rpm"] || "";
        sh.pts = {}; sh.fit = null;
      });
      let ok = 0;
      d.rows.forEach(function (r) {
        const sh = S.shots[r.shot]; if (!sh) return;
        if (isFinite(r.px) && isFinite(r.py)) { sh.pts[r.frame] = [r.px, r.py]; ok++; }
      });
      setStatus("Imported " + ok + " points from the text box." + (S.cal.p.length < 2 ? " No scale in it: set the scale before fitting." : ""));
      setShot(S.shot);
    }

    function refresh() {
      const s = mPerPx();
      $("cal-o").textContent = s ? (1 / s).toFixed(1) + " px per m (" + (s * 1000).toFixed(3) + " mm per px), user; click error ± " + (1.96 * clickSd() * 100).toFixed(2) + " % (95 %, ASSUMED 0.5 px per end)" : "not set: click Scale, then both ends of a known length";
      $("level-o").textContent = S.level.p.length === 2 ? "image tilted " + (levelRad() * 180 / Math.PI).toFixed(2) + "° (corrected)" : "not set: rows of pixels taken as level";
      const nA = sortedPts(S.shots.A).length, nB = sortedPts(S.shots.B).length;
      $("fitA").disabled = !(s && nA >= 6); $("fitB").disabled = !(s && nB >= 6);
      $("npts").textContent = "A " + nA + " points · B " + nB + " points";
      const wr = parseFloat(cur().meta.wheel_rpm);
      $("wheel-o").textContent = isFinite(wr) && wr > 0 ? "wheel surface speed u = " + (wr * 2 * Math.PI / 60 * WHEEL_R).toFixed(2) + " m/s (derived, 98 mm wheel)" : "";
      $("csv").value = buildCSV();
      draw(); chart(); results();
    }

    function fmt(v, d) { return isFinite(v) ? Number(v).toFixed(d) : "-"; }
    function resultTable(res, rows) {
      let h = '<table class="res"><thead><tr><th>Quantity</th><th>Value</th><th>± 95 % (Jacobian)</th><th>Bootstrap 95 %</th><th>Label</th></tr></thead><tbody>';
      rows.forEach(function (r) {
        const b = res.boot && res.boot[r.nm] ? fmt(res.boot[r.nm].ci95[0], r.d) + " … " + fmt(res.boot[r.nm].ci95[1], r.d) : "-";
        h += "<tr><td>" + r.lab + "</td><td>" + fmt(r.v !== undefined ? r.v : res.value[r.nm], r.d) + "</td><td>" + (r.nm ? "± " + fmt(1.96 * res.sd_total[r.nm], r.d) : r.sdv !== undefined ? "± " + fmt(1.96 * r.sdv, r.d) : "") + "</td><td>" + (r.nm ? b : "") + '</td><td><span class="lab">' + r.label + "</span></td></tr>";
      });
      return h + "</tbody></table>";
    }
    function flagList(res) {
      if (!res.flags.length) return '<p class="ok">The track separates every fitted number (no pair correlated above ' + CORR_FLAG + ", none weakly set).</p>";
      return '<ul class="flags">' + res.flags.map(function (f) { return "<li>" + f + "</li>"; }).join("") + "</ul>";
    }
    function results() {
      const A = S.shots.A.fit, B = S.shots.B.fit, out = [];
      const truth = S.demoTruth;
      if (A) {
        const wr = parseFloat(S.shots.A.meta.wheel_rpm);
        const rows = [{ lab: "Launch speed v0 at first tracked frame (m/s)", v: A.v0, d: 2, label: "derived" },
          { lab: "Launch angle (°)", v: A.theta_deg, d: 1, label: "derived" },
          { lab: "Drag coefficient Cd", nm: "Cd", d: 3, label: "derived" }];
        if (isFinite(wr) && wr > 0) rows.push({ lab: "Grip v/u (wheel " + wr + " rpm, user)", v: A.v0 / (wr * 2 * Math.PI / 60 * WHEEL_R), d: 3, label: "derived" });
        const ck = A.check, gs = ck ? ck.value.len_scale : NaN, gsd = ck ? ck.sd.len_scale : NaN;
        if (ck) rows.push({ lab: "Gravity check: video length / true length", v: gs, sdv: gsd, d: 4, label: "derived" });
        const disagree = ck && Math.abs(gs - 1) > 1.96 * Math.hypot(gsd, A.clickSd || 0);
        const near = A.value.Cd < 0.415 ? "Low drag (Cd 0.33)" : A.value.Cd < 0.7 ? "Nominal (Cd 0.5)" : "High drag (Cd 0.9)";
        out.push('<div class="rblock"><h3><i class="sw" style="background:#a9b4bf"></i>Shot A, no spin (the twin): drag</h3>' + resultTable(A, rows) +
          '<p class="hint">' + A.n + " points, rms residual " + fmt(A.rms_m * 1000, 1) + " mm. " + (truth ? "Demo truth (ASSUMED synthetic): Cd " + truth.Cd.toFixed(2) + ". " : "") +
          "Scale used: " + (A.scaleMode === "gravity" ? "gravity check from this shot" : "clicked bar, ± " + fmt(1.96 * (A.clickSd || 0) * 100, 2) + " % (ASSUMED 0.5 px clicks), carried into Cd") + ". " +
          (ck ? (disagree ? '<b style="color:var(--hit)">The clicked scale and gravity disagree by ' + sgnF((gs - 1) * 100, 2) + " %:</b> check that the scale bar is in the flight plane, or that the no-spin ball had no spin. "
                          : "Clicked scale and gravity agree within their errors. ") : "") +
          "Explorer: Advanced settings → Air model, nearest preset " + near + " (the explorer has no free Cd box yet).</p>" + flagList(A) + "</div>");
      }
      if (B) {
        const sp = spinOf(), ln = LIFT_NAMES[B.lift];
        const rows = [{ lab: "Launch speed v0 (m/s)", v: B.v0, d: 2, label: "derived" }, { lab: "Launch angle (°)", v: B.theta_deg, d: 1, label: "derived" }]
          .concat(ln.map(function (nm) { return { lab: nm === "Cl" ? "Lift coefficient Cl (one value)" : nm === "c1" ? "Lift slope c1 (Cl = c1 S)" : "Lift cap Cl_max", nm: nm, d: 3, label: "derived" }; }))
          .concat(B.names.indexOf("S0") >= 0 ? [{ lab: "Spin ratio S0", nm: "S0", d: 2, label: "derived" }] : [{ lab: "Spin ratio S0 = ωR/v at the first tracked frame", v: B.S0, d: 2, label: sp.spin.rpm !== undefined ? "user" : "ASSUMED" }]);
        out.push('<div class="rblock"><h3><i class="sw" style="background:#f4c430"></i>Shot B, backspin: spin lift (Cd held at A\'s ' + fmt(B.cd_used, 3) + ")</h3>" + resultTable(B, rows) +
          '<p class="twin"><b>No-spin twin</b> (same launch, same Cd, no lift; dashed): by the last tracked frame the lift has moved the ball ' + fmt(B.twin_dmax * 1000, 0) + " mm (height " + (B.twin_dz_end >= 0 ? "+" : "") + fmt(B.twin_dz_end * 1000, 0) + " mm), against a click noise of " + fmt(B.rms_m * 1000, 1) + " mm rms. " +
          "Lift " + (B.lift_detected ? "<b>detected</b> (95 % interval excludes 0)." : "<b>not detected</b> (95 % interval includes 0).") + " PREDICTED twin, derived fit.</p>" +
          '<p class="hint">Spin: ' + sp.label + "; S along the tracked part " + fmt(B.S_range[0], 2) + " … " + fmt(B.S_range[1], 2) + " (derived, k " + ballP().k + " 1/s ASSUMED). The lift error includes A's Cd error and the scale error (" + (B.scaleMode === "gravity" ? "gravity-checked scale from A" : "clicked bar") + ")." +
          (truth ? " Demo truth (ASSUMED synthetic): Cl = min(" + truth.c1 + " S, " + truth.clmax + ") = " + truth.clmax + " over this S range." : "") +
          '</p><p class="hint">Explorer: Advanced settings → Spin lift options → Lift table S:Cl, paste <code>' + B.table + "</code>. One shot covers one S range only; fit several spin settings to build a table.</p>" + flagList(B) + "</div>");
      }
      if (!A && !B) out.push('<p class="hint">Fit shot A first (no spin, sets Cd), then shot B (backspin with the same settings, sets Cl). Each needs a scale and at least 6 points.</p>');
      $("results").innerHTML = out.join("");
    }

    // ---- chart: tracked points and fits in metres, equal axes (SVG)
    function chart() {
      const svg = $("chart"), W = svg.clientWidth || 600, H = Math.max(220, Math.min(360, W * 0.5));
      svg.setAttribute("viewBox", "0 0 " + W + " " + H); svg.setAttribute("height", H);
      const ser = [];
      ["A", "B"].forEach(function (k) {
        const tr = trackOf(k), sh = S.shots[k]; if (!tr) return;
        const pts = tr.t.map(function (t, i) { return { t: t, x: tr.x[i], z: tr.z[i], f: tr.frames[i] }; });
        const s = { k: k, col: k === "A" ? "#a9b4bf" : "#f4c430", pts: pts, fit: null, twin: null };
        if (sh.fit) {
          const tt = []; const t1 = tr.t[tr.t.length - 1]; for (let i = 0; i <= 100; i++) tt.push(t1 * i / 100);
          const m = sh.fit.path(tt); s.fit = tt.map(function (_, i) { return { x: m.x[i] * sh.fit.sign, z: m.z[i] }; });
          if (sh.fit.twinPath) { const q = sh.fit.twinPath(tt); s.twin = tt.map(function (_, i) { return { x: q.x[i] * sh.fit.sign, z: q.z[i] }; }); }
        }
        ser.push(s);
      });
      if (!ser.length) { svg.innerHTML = '<text x="' + W / 2 + '" y="' + H / 2 + '" text-anchor="middle" class="ax">Set the scale and click the ball in 6 or more frames to see the path in metres.</text>'; return; }
      let x0 = Infinity, x1 = -Infinity, z0 = Infinity, z1 = -Infinity;
      ser.forEach(function (s) { s.pts.concat(s.fit || [], s.twin || []).forEach(function (p) { x0 = Math.min(x0, p.x); x1 = Math.max(x1, p.x); z0 = Math.min(z0, p.z); z1 = Math.max(z1, p.z); }); });
      const pad = { l: 46, r: 14, t: 24, b: 30 }, pw = W - pad.l - pad.r, ph = H - pad.t - pad.b;
      const sc = Math.min(pw / Math.max(x1 - x0, 1e-3), ph / Math.max(z1 - z0, 1e-3));
      const cx = pad.l + (pw - (x1 - x0) * sc) / 2, cz = pad.t + ph - (ph - (z1 - z0) * sc) / 2;
      const X = function (x) { return cx + (x - x0) * sc; }, Z = function (z) { return cz - (z - z0) * sc; };
      const step = [0.05, 0.1, 0.2, 0.25, 0.5, 1, 2].find(function (s) { return s * sc > 48; }) || 2;
      let h = "";
      for (let g = Math.ceil(x0 / step) * step; g <= x1 + 1e-9; g += step) h += '<line class="grid" x1="' + X(g) + '" x2="' + X(g) + '" y1="' + pad.t + '" y2="' + (H - pad.b) + '"/><text class="ax" x="' + X(g) + '" y="' + (H - 12) + '" text-anchor="middle">' + +g.toFixed(2) + "</text>";
      for (let g = Math.ceil(z0 / step) * step; g <= z1 + 1e-9; g += step) h += '<line class="grid" y1="' + Z(g) + '" y2="' + Z(g) + '" x1="' + pad.l + '" x2="' + (W - pad.r) + '"/><text class="ax" x="' + (pad.l - 6) + '" y="' + (Z(g) + 4) + '" text-anchor="end">' + +g.toFixed(2) + "</text>";
      h += '<text class="ax" x="' + (W - pad.r) + '" y="' + (H - 1) + '" text-anchor="end">x (m)</text><text class="ax" x="4" y="' + (pad.t + 8) + '">z (m)</text>';
      const pl = function (arr) { return arr.map(function (p, i) { return (i ? "L" : "M") + X(p.x).toFixed(1) + " " + Z(p.z).toFixed(1); }).join(""); };
      ser.forEach(function (s) {   // points first, fitted lines on top so both stay visible
        s.pts.forEach(function (p, i) { h += '<circle class="pt" cx="' + X(p.x).toFixed(1) + '" cy="' + Z(p.z).toFixed(1) + '" r="2.6" fill="' + s.col + '" opacity=".75" data-s="' + s.k + '" data-i="' + i + '"/>'; });
      });
      ser.forEach(function (s) {
        if (s.fit) h += '<path d="' + pl(s.fit) + '" fill="none" stroke="' + s.col + '" stroke-width="2" pointer-events="none"/>';
        if (s.twin) h += '<path d="' + pl(s.twin) + '" fill="none" stroke="#a9b4bf" stroke-width="2" stroke-dasharray="6 5" pointer-events="none"/>';
      });
      ser.forEach(function (s) {   // direct labels at the apex: B above its path, A below its path
        let top = s.pts[0];
        s.pts.forEach(function (p) { if (p.z > top.z) top = p; });
        const up = s.k === "B" || ser.length === 1;
        h += '<text class="dl" x="' + X(top.x).toFixed(1) + '" y="' + (Z(top.z) + (up ? -10 : 18)).toFixed(1) + '" text-anchor="middle">' + (s.k === "A" ? "A no spin" : "B backspin") + "</text>";
      });
      svg.innerHTML = h;
      svg.onmousemove = function (e) {
        const c = e.target.closest ? e.target.closest(".pt") : null, tip = $("tip");
        if (!c) { tip.style.display = "none"; return; }
        const s = ser.find(function (q) { return q.k === c.dataset.s; }), p = s.pts[+c.dataset.i], sh = S.shots[s.k];
        let res = "";
        if (sh.fit) { const n = sh.fit.r.length / 2, i = +c.dataset.i; res = "<br>residual " + fmt(Math.hypot(sh.fit.r[i], sh.fit.r[n + i]) * 1000, 1) + " mm"; }
        tip.innerHTML = "Shot " + s.k + " · frame " + p.f + "<br>t " + p.t.toFixed(4) + " s<br>x " + p.x.toFixed(3) + " m · z " + p.z.toFixed(3) + " m" + res;
        tip.style.display = "block"; tip.style.left = Math.min(e.clientX + 12, window.innerWidth - 200) + "px"; tip.style.top = (e.clientY + 12) + "px";
      };
      svg.onmouseleave = function () { $("tip").style.display = "none"; };
    }

    // ---- fitting buttons
    function runFit(k) {
      const tr = trackOf(k); if (!tr) return;
      const nb = Math.max(0, Math.min(400, parseInt($("nboot").value, 10) || 0)), p = ballP();
      setStatus("Fitting shot " + k + (nb ? " with " + nb + " bootstrap refits" : "") + " …");
      setTimeout(function () {
        try {
          const grav = $("scalesrc").value === "gravity";
          if (k === "A") {
            const chk = fitNoSpin(tr, { p: p, fitScale: true, boot: grav ? nb : 0 });
            S.shots.A.fit = grav ? chk : fitNoSpin(tr, { p: p, boot: nb, lenScaleSd: clickSd() });
            S.shots.A.fit.check = chk; S.shots.A.fit.clickSd = clickSd(); S.shots.A.fit.scaleMode = grav ? "gravity" : "clicked";
          } else {
            const A = S.shots.A.fit, sp = spinOf(), useG = grav && A && A.check;
            S.shots.B.fit = fitLift(tr, { p: p, boot: nb, lift: $("liftm").value, spin: sp.spin, fitSpin: sp.fitSpin,
              cd: A ? A.value.Cd : 0.5, cdSd: A ? A.sd.Cd : 0,
              lenScale: useG ? A.check.value.len_scale : 1, lenScaleSd: useG ? A.check.sd.len_scale : clickSd() });
            S.shots.B.fit.scaleMode = useG ? "gravity" : "clicked";
            if (!A) S.shots.B.fit.flags.unshift("no shot A fit: Cd held at 0.5 (ASSUMED), so these lift numbers are not a twin test");
          }
          setStatus("Shot " + k + " fitted.");
        } catch (err) { setStatus("Fit failed: " + err.message); }
        refresh();
      }, 20);
    }

    // ---- demo: synthetic twin tracks from physics.js (ASSUMED truth), drawn as frames
    function loadDemo() {
      const truth = { v: 7.0, thDeg: 55, x0: 0.3, z0: 0.35, Cd: 0.5, c1: 0.35, clmax: 0.25, S0: 1.0 };
      const fps = 240, mpp = 0.004, W = 1280, H = 720, sigPx = 1.5, nF = 210, p = ballP();
      const tA = synth({ v: truth.v, thDeg: truth.thDeg, x0: truth.x0, z0: truth.z0, Cd: truth.Cd }, { fps: fps, frames: nF, p: p, seed: SEED });
      const tB = synth({ v: truth.v, thDeg: truth.thDeg, x0: truth.x0, z0: truth.z0, Cd: truth.Cd, lift: "capped", lp: [truth.c1, truth.clmax], S0: truth.S0 }, { fps: fps, frames: nF, p: p, seed: SEED });
      S.cal = { p: [[100, 660], [350, 660]], mm: 1000 }; $("calmm").value = 1000; S.level.p = [];
      const rnd = PP.mulberry32(SEED + 7);
      const gauss = function () { const u1 = 1 - rnd(), u2 = rnd(); return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2); };
      [["A", tA], ["B", tB]].forEach(function (pair) {
        const k = pair[0], tr = pair[1], sh = S.shots[k];
        sh.w = W; sh.h = H; sh.fps = fps; sh.fileFps = fps; sh.nFrames = tr.frame.length; sh.pts = {}; sh.fit = null; sh.name = "synthetic demo";
        sh.meta = k === "B" ? { ball_rpm: "", wheel_rpm: "" } : { ball_rpm: "", wheel_rpm: "" };
        tr.frame.forEach(function (f, i) {
          if (f % 2) return;   // click every 2nd frame, as a person would
          sh.pts[f] = [tr.xTrue[i] / mpp + sigPx * gauss(), H - tr.zTrue[i] / mpp + sigPx * gauss()];
        });
        sh.src = { kind: "demo", draw: function (g, f) { demoFrame(g, W, H, mpp, tr, f, k); } };
      });
      $("spinsrc").value = "ideal";
      S.demoTruth = truth;
      setStatus("Demo loaded: synthetic twin shots from physics.js (ASSUMED truth v 7.0 m/s, 55°, Cd 0.50, backspin S0 1.0 with Cl = min(0.35 S, 0.25)), click noise 1.5 px. Press Fit A, then Fit B.");
      setShot(S.shot); gotoFrame(60);
    }
    function demoFrame(g, W, H, mpp, tr, f, k) {
      g.fillStyle = "#1b2128"; g.fillRect(0, 0, W, H);
      g.strokeStyle = "#2a333d"; g.lineWidth = 1;
      for (let x = 0; x < W; x += 0.5 / mpp) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, H); g.stroke(); }
      for (let y = H; y > 0; y -= 0.5 / mpp) { g.beginPath(); g.moveTo(0, y); g.lineTo(W, y); g.stroke(); }
      g.fillStyle = "#3a4048"; g.fillRect(0, H - 40, W, 40);
      g.fillStyle = "#e3eaf0"; g.fillRect(100, 652, 250, 16);
      for (let i = 0; i <= 10; i++) { g.fillStyle = i % 2 ? "#e3eaf0" : "#111921"; g.fillRect(100 + i * 25, 652, 25, 16); }
      g.fillStyle = "#e3eaf0"; g.font = "16px system-ui, sans-serif"; g.fillText("1 m scale bar", 110, 690);
      g.fillStyle = "#5a6470"; g.fillRect(20, H - 40 - 0.3 / mpp, 0.32 / mpp, 0.3 / mpp);
      g.fillStyle = "#8d9caa"; g.font = "15px ui-monospace, Consolas, monospace";
      g.fillText("SYNTHETIC DEMO (physics.js, ASSUMED) · shot " + k + (k === "A" ? " no spin" : " backspin") + " · frame " + f, 20, 26);
      const i = tr.frame.indexOf(f);
      if (i >= 0) {
        const cx = tr.xTrue[i] / mpp, cy = H - tr.zTrue[i] / mpp, r = 0.0355 / mpp;
        g.fillStyle = "#f4c430"; g.beginPath(); g.arc(cx, cy, r, 0, 2 * Math.PI); g.fill();
        g.fillStyle = "#8a6d12"; for (let a = 0; a < 6; a++) { const an = a * Math.PI / 3 + (k === "B" ? -f * 0.35 : 0); g.beginPath(); g.arc(cx + 0.55 * r * Math.cos(an), cy + 0.55 * r * Math.sin(an), 1.6, 0, 2 * Math.PI); g.fill(); }
      }
    }

    // ---- wire controls
    Array.from($("shot-seg").children).forEach(function (b) { b.onclick = function () { setShot(b.dataset.v); }; });
    Array.from($("mode-seg").children).forEach(function (b) { b.onclick = function () { setMode(b.dataset.v); }; });
    $("file").onchange = function (e) { loadFiles(e.target.files); e.target.value = ""; };
    $("fps").onchange = function () { const v = parseFloat($("fps").value); if (v > 0) { cur().fps = v; cur().fit = null; refresh(); } };
    $("ffps").onchange = function () { const v = parseFloat($("ffps").value); const sh = cur(); if (v > 0) { sh.fileFps = v; if (sh.src && sh.src.kind === "video") sh.nFrames = Math.max(1, Math.floor(sh.src.el.duration * v)); gotoFrame(S.frame); refresh(); } };
    $("calmm").onchange = function () { const v = parseFloat($("calmm").value); if (v > 0) { S.cal.mm = v; S.shots.A.fit = S.shots.B.fit = null; refresh(); } };
    $("brpm").onchange = function () { cur().meta.ball_rpm = $("brpm").value.trim(); if (S.shot === "B") cur().fit = null; refresh(); };
    $("wrpm").onchange = function () { cur().meta.wheel_rpm = $("wrpm").value.trim(); refresh(); };
    $("fpt").onchange = function () { const n = parseFloat($("fpt").value), sh = cur(); if (n > 0) { $("brpm").value = (sh.fps / n * 60).toFixed(0); $("brpm").onchange(); } };
    ["mass", "diam", "rho", "kdec"].forEach(function (id) { $(id).onchange = function () { S.shots.A.fit = S.shots.B.fit = null; refresh(); }; });
    $("spinsrc").onchange = function () { S.shots.B.fit = null; refresh(); };
    $("liftm").onchange = function () { S.shots.B.fit = null; refresh(); };
    $("scalesrc").onchange = function () { S.shots.A.fit = S.shots.B.fit = null; refresh(); };
    $("stepn").onchange = function () { S.step = Math.max(1, parseInt($("stepn").value, 10) || 1); };
    $("loupe-on").onchange = function () { S.loupe = $("loupe-on").checked; drawLoupe(); };
    $("prev").onclick = function () { gotoFrame(S.frame - S.step); };
    $("next").onclick = function () { gotoFrame(S.frame + S.step); };
    $("prev10").onclick = function () { gotoFrame(S.frame - 10); };
    $("next10").onclick = function () { gotoFrame(S.frame + 10); };
    $("fslider").oninput = function () { gotoFrame(+$("fslider").value); };
    $("delpt").onclick = function () { delete cur().pts[S.frame]; cur().fit = null; refresh(); };
    $("clear").onclick = function () { cur().pts = {}; cur().fit = null; refresh(); };
    $("fitA").onclick = function () { runFit("A"); };
    $("fitB").onclick = function () { runFit("B"); };
    $("demo").onclick = loadDemo;
    $("copy").onclick = function () {
      const ta = $("csv"), done = function () { $("copy-o").textContent = "Copied."; setTimeout(function () { $("copy-o").textContent = ""; }, 2000); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(ta.value).then(done, function () { ta.select(); try { document.execCommand("copy"); done(); } catch (_) { /* ignore */ } });
      else { ta.select(); try { document.execCommand("copy"); done(); } catch (_) { /* ignore */ } }
    };
    $("import").onclick = function () { importCSV($("csv").value); };
    window.addEventListener("resize", sizeCanvas);
    sizeCanvas(); setShot("A"); setMode("track");
    if (/demo/.test(location.hash)) { loadDemo(); if (/fit/.test(location.hash)) { runFit("A"); setTimeout(function () { runFit("B"); }, 60); } }
    return S;
  }

  return { DEF: DEF, WHEEL_R: WHEEL_R, simulate: simulate, fitNoSpin: fitNoSpin, fitLift: fitLift, synth: synth,
    toCSV: toCSV, parseCSV: parseCSV, lm: lm, solve: solve, inverse: inverse, ui: ui };
});
