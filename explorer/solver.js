// Live shot solver for the whole-field explorer (PM-009). UMD like physics.js: module.exports in
// node, self.PollenSolver in a browser or Web Worker. No DOM. Depends only on PollenPhysics: in a
// page or worker load physics.js first (worker: importScripts("physics.js", "solver.js")).
// API: pose(x, y, meta), sectionFor(side, psi, meta), solve(q, onProgress), shot(q, v, theta),
// rpm(v, vu), vFromRpm(rpm, vu), ballSpinRpm(v, S). meta = data/field/index.json (parsed).
// solve() grid order: v-major, index = iv * th.length + ith (theta fastest); minRpm = lowest clean v
// (it can sit on a narrow island: show thetaLo..thetaHi with it); twin = same solve with S = 0, c1 = 0.
//
// Flight = the PM-005 oblique model (FIELD_DATA.md, src/robustness.py "score from anywhere"):
// planar flight in the vertical plane of the bearing (spin axis perpendicular to it, no sideways
// Magnus), projected on the HIVE shot axis (X, VX scaled by cos psi). Classifier: default
// (q.sideWalls true, PM-013) = the 3D cell (physics.js buildCell3D / classifyOblique3D: s = 0 section
// extruded, side walls at +-0.254 m, ASSUMED wall thickness, derived pentagon roof) against the
// ball-centre path with lateral offset s = (aimX - x) tan psi; q.sideWalls false = the old section
// model at the ASSUMED offset s_eff(psi) = min(0.3 tan psi, 0.2), side walls NOT modelled. Air drag (Cd) and capped Magnus
// lift with exponential spin decay are included; their coefficients are ASSUMED (literature, not
// POLLEN measurements). Every window is PREDICTED (model output), not a hit probability.
// Air (2026-10-31, research/MISSING_EFFECTS.md build-next 1, 2, 4, 6): default still air 20 C / 101.325 kPa / dry,
// rho 1.2041 kg/m^3 (derived; q.air false keeps params.rho, the exports' rounded 1.20). Options q.air (venue),
// q.drag (Cd(Re) model, spin drag), q.wind (draft); results carry gripLimited above the PREDICTED 8.9 m/s hood cap.
//
// Continuous pose and release height: nothing is snapped to the export grid. Section model only:
// sections between the exported offsets are linearly interpolated, which is exact up to the 1e-5 m rounding of the export:
// src/hive.py _roof_drop lowers the roof linearly in |s| and the section is affine in that drop.
(function (root) {
  "use strict";
  const P = (typeof module !== "undefined" && module.exports && typeof require === "function")
    ? require("./physics.js") : root.PollenPhysics;

  // ---- field constants: JS twin of src/field_geom.py (field frame, pose_pos; tests/test_field_geom.py
  // cross-checks footprint() and sightBlocked() against it)
  const IN = 0.0254;
  const X_WALL = 1.8009, HIVE_HALF = 0.3236, Y_LO = -X_WALL + HIVE_HALF, Y_HI = X_WALL + HIVE_HALF;
  const BASE_HX = 38.95 / 2 * IN, BASE_HY = 49.46 / 2 * IN, BASE_CY = HIVE_HALF;   // CONFIRMED TU07 9.6.1
  const BASE_X = BASE_HX, BASE_Y = [BASE_CY - BASE_HY, BASE_CY + BASE_HY];
  const OTHER_HIVE_X = 0.6745, OTHER_HIVE_Y = [0.3455, 0.9495];   // derived box (plan envelope + R), ASSUMED as blocking
  const ROBOT_L = 18 * IN, ROBOT_W = 18 * IN, ROBOT_L_EXPANDED = 24 * IN;      // CONFIRMED R102 / R105 option
  const HEADING_STEP = 5;          // ASSUMED scan step for "any heading"
  const SIDE_WALL_S = 0.254 - 0.0355;   // derived: ball-centre limit |s| inside the cell
  const X_GATE = 0.401;            // up-cell gate centre at (+0.401, 0) seen from both sides
  const WHEEL_D = 0.098;           // wheel diameter (m) for rpm conversion
  const R_BALL = 0.0355;
  const Z_STOP_REL = 0.4;          // integrator stop height above release (export_field.py, z_stop)

  function deg(r) { return r * 180 / Math.PI; }
  function rad(d) { return d * Math.PI / 180; }
  function gridMeta(meta) {
    const g = (meta && meta.grid) || {};
    const d = g.d || [0.55, 1.75];
    return { dLo: d[0] - 0.025, dHi: d[d.length - 1] + 0.025,
             psiModel: g.psi_max_model !== undefined ? g.psi_max_model : 60,
             psiExport: g.psi_max_export !== undefined ? g.psi_max_export : 75,
             psiStep: g.psi && g.psi.length > 1 ? g.psi[1] - g.psi[0] : 5,
             psiWall: g.psi_side_wall !== undefined ? g.psi_side_wall : 35.57,
             h: g.h || [0.2, 0.35, 0.5, 0.65, 0.737] };
  }

  // ---------------------------------------------------------------- robot footprint and sight line
  // footprintAt: does the chassis (length along the heading, width across) whose release point is (x, y)
  // fit inside the field walls and off the A-frame base rectangle? off = [forward, left] of the release
  // point from the chassis centre in the chassis frame (ASSUMED default 0). Touching fits.
  // Returns { ok, wall, base, release } (true = that test fails). Same maths as field_geom.chassis_fits.
  function footprintAt(x, y, heading, L, W, off) {
    const t = rad(heading), c = Math.cos(t), sn = Math.sin(t), fo = off[0], lo = off[1];
    const cx = x - (c * fo - sn * lo), cy = y - (sn * fo + c * lo), hl = L / 2, hw = W / 2;
    const ac = Math.abs(c), as = Math.abs(sn), ex = hl * ac + hw * as, ey = hl * as + hw * ac, eps = 1e-9;
    const wall = !(Math.abs(cx) + ex <= X_WALL + eps && cy - ey >= Y_LO - eps && cy + ey <= Y_HI + eps);
    const dx = cx, dy = cy - BASE_CY;
    const bu = BASE_HX * ac + BASE_HY * as, bv = BASE_HX * as + BASE_HY * ac;
    const base = Math.abs(dx) < BASE_HX + ex - eps && Math.abs(dy) < BASE_HY + ey - eps &&
                 Math.abs(dx * c + dy * sn) < hl + bu - eps && Math.abs(-dx * sn + dy * c) < hw + bv - eps;
    const release = !(Math.abs(x) <= X_WALL + eps && y >= Y_LO - eps && y <= Y_HI + eps) ||
                    (Math.abs(x) < BASE_HX - eps && Math.abs(y - BASE_CY) < BASE_HY - eps);
    return { ok: !wall && !base && !release, wall: wall, base: base, release: release, cx: cx, cy: cy };
  }
  // robot = { heading (deg; undefined = any heading that fits, 5 deg scan), length, width, offset: [fwd, left] }
  // defaults: 18 x 18 in (CONFIRMED R102), offset 0 (ASSUMED)
  function footprint(x, y, robot) {
    const r = robot || {}, L = r.length || ROBOT_L, W = r.width || ROBOT_W, off = r.offset || [0, 0];
    if (r.heading !== undefined && r.heading !== null) {
      const f = footprintAt(x, y, r.heading, L, W, off);
      return Object.assign(f, { heading: r.heading, anyHeading: false, length: L, width: W, offset: off });
    }
    const sym = (off[0] || off[1]) ? 360 : (Math.abs(L - W) < 1e-12 ? 90 : 180);
    let first = null;
    for (let h = 0; h < sym - 1e-9; h += HEADING_STEP) {
      const f = footprintAt(x, y, h, L, W, off);
      if (f.ok) return Object.assign(f, { heading: h, anyHeading: true, length: L, width: W, offset: off });
      if (!first) first = f;
    }
    return Object.assign(first, { heading: null, anyHeading: true, length: L, width: W, offset: off });
  }
  function footprintText(f) {
    const parts = [];
    if (f.release) parts.push("release point outside the field or over the HIVE base");
    if (f.wall || f.base) parts.push("robot overlaps " + (f.wall && f.base ? "wall and HIVE base" : f.wall ? "wall" : "HIVE base"));
    return parts.join("; ") + " (" + (f.length / IN).toFixed(1) + " x " + (f.width / IN).toFixed(1) + " in chassis, " +
      (f.anyHeading ? "no heading fits" : "heading " + (+f.heading).toFixed(0) + " deg") +
      ", release offset " + f.offset[0].toFixed(3) + " / " + f.offset[1].toFixed(3) + " m ASSUMED)";
  }
  // exact segment-rectangle test (Liang-Barsky) from (x, y) to the aim point against the open other-HIVE box;
  // same maths as field_geom.sight_blocked
  function sightBlocked(x, y, ax, ay) {
    if (ax === undefined) ax = X_GATE;
    if (ay === undefined) ay = 0;
    const dx = ax - x, dy = ay - y;
    const Pk = [-dx, dx, -dy, dy], Qk = [x + OTHER_HIVE_X, OTHER_HIVE_X - x, y - OTHER_HIVE_Y[0], OTHER_HIVE_Y[1] - y];
    let t0 = 0, t1 = 1;
    for (let k = 0; k < 4; k++) {
      if (Math.abs(Pk[k]) < 1e-15) { if (Qk[k] <= 0) return false; continue; }
      const r = Qk[k] / Pk[k];
      if (Pk[k] < 0) { if (r > t0) t0 = r; } else if (r < t1) t1 = r;
    }
    return t1 - t0 > 1e-12;
  }

  // ---------------------------------------------------------------- pose
  // psi sign: + when the release point has y > 0 (side of the aim line); the model uses |psi|.
  // opts.sideWalls (default true) only changes the side-wall note text.
  // opts.robot (see footprint): the chassis must fit (walls, A-frame base), else status "illegal".
  function pose(x, y, meta, opts) {
    const sw = !(opts && opts.sideWalls === false);
    const gm = gridMeta(meta), notes = [];
    const side = x > 0 ? "fav" : "unfav", d = Math.abs(x);
    const Lh = side === "fav" ? Math.max(d - X_GATE, 1e-3) : d + X_GATE;
    const psiAbs = deg(Math.atan2(Math.abs(y), Lh));
    const psi = y < 0 ? -psiAbs : psiAbs;
    const aim = [X_GATE, 0];
    const bearingDeg = deg(Math.atan2(aim[1] - y, aim[0] - x));
    const otherHive = sightBlocked(x, y, aim[0], aim[1]);
    const fp = footprint(x, y, opts && opts.robot);
    let status = "ok";
    if (!fp.ok) { status = "illegal"; notes.push(footprintText(fp)); }
    else if (d < gm.dLo - 1e-9 || d > gm.dHi + 1e-9) {
      status = "beyond_model";
      notes.push("distance d = " + d.toFixed(3) + " m is outside the validated table " + gm.dLo.toFixed(3) +
                 ".." + gm.dHi.toFixed(3) + " m: live model still runs, not checked against the export");
    } else if (psiAbs > gm.psiExport + gm.psiStep / 2) {
      status = "beyond_model";
      notes.push("bearing psi " + psiAbs.toFixed(1) + " deg is beyond the exported 75 deg: ASSUMED extrapolation");
    } else if (psiAbs > gm.psiModel) {
      status = "psi_extrapolated";
      notes.push("psi above " + gm.psiModel + " deg: robustness.py treats this as infeasible; ASSUMED extrapolation");
    }
    const sideWallRisk = psiAbs >= gm.psiWall;
    if (sideWallRisk) notes.push(sw
      ? "psi >= " + gm.psiWall + " deg: the ball passes close to a cell side wall; the 3D cell model checks the side walls per shot"
      : "psi >= " + gm.psiWall + " deg: straight-line side-wall estimate (near-side estimate; far side not checked; side walls are not modelled in the section model)");
    if (otherHive) notes.push("straight line to the aim point crosses the other HIVE (derived plan box, ASSUMED; not modelled as an obstacle; a high far-side ball can pass above it)");
    return { ok: status !== "illegal", status: status, side: side, d: d, Lh: Lh, psi: psi,
             sideWallRisk: sideWallRisk, otherHive: otherHive, aim: aim, bearingDeg: bearingDeg,
             sEff: P.sEff(psiAbs), footprint: fp, notes: notes };
  }

  // ---------------------------------------------------------------- sections
  // Linear interpolation in s_eff between the two neighbouring exported sections of that side
  // (exact: see header). An exact match returns the exported section itself.
  const secCache = typeof WeakMap !== "undefined" ? new WeakMap() : null;
  function sideSections(meta, side) {
    let per = secCache && secCache.get(meta);
    if (!per) { per = {}; if (secCache) secCache.set(meta, per); }
    if (!per[side]) {
      const list = [];
      for (const k of Object.keys(meta.sections)) {
        const m = /^(unfav|fav)_s([0-9.eE+-]+)$/.exec(k);
        if (m && m[1] === side) list.push({ s: parseFloat(m[2]), key: k, sec: meta.sections[k] });
      }
      list.sort(function (a, b) { return a.s - b.s; });
      per[side] = { list: list, cache: {} };
    }
    return per[side];
  }
  function lerpArr(a, b, t) {
    return a.map(function (p, i) { return [p[0] + t * (b[i][0] - p[0]), p[1] + t * (b[i][1] - p[1])]; });
  }
  function sectionFor(side, psiDeg, meta) {
    const s = P.sEff(Math.abs(psiDeg)), ss = sideSections(meta, side), list = ss.list;
    if (!list.length) throw new Error("no sections for side " + side);
    const ck = s.toFixed(7);
    if (ss.cache[ck]) return ss.cache[ck];
    let out;
    for (const e of list) if (Math.abs(e.s - s) < 5e-5) { out = Object.assign({}, e.sec, { s: s, key: e.key, how: "exported" }); break; }
    if (!out) {
      let i = 0;
      while (i < list.length - 2 && list[i + 1].s < s) i++;
      const a = list[i], b = list[i + 1], t = (s - a.s) / (b.s - a.s);
      out = { names: a.sec.names, P0: lerpArr(a.sec.P0, b.sec.P0, t), P1: lerpArr(a.sec.P1, b.sec.P1, t),
              inside: lerpArr(a.sec.inside, b.sec.inside, t), gate: lerpArr(a.sec.gate, b.sec.gate, t),
              normal: a.sec.normal, s: s, key: a.key + "~" + b.key,
              how: "interpolated in s_eff between " + a.key + " and " + b.key + " (exact: roof drop linear in s)" };
    }
    ss.cache[ck] = out;
    return out;
  }

  // q.roofClear (section model only, default off = unchanged): lower the roof segments and the inside top by
  // R (sqrt(1 + k^2) - 1) = 0.00663 m (derived: a sphere under the 32.6 deg sloped pentagon roof needs a vertical
  // gap R sqrt(1 + k^2)); the JS twin of src/hive.py Hive.from_json(roof_clearance=True). The 3D cell
  // (default model) already includes it. Assumes a sharp roof apex (research/GEOMETRY_AUDIT.md U3).
  function roofClearDrop(R) { const k = P.CELL3D.ROOF_SLOPE; return R * (Math.sqrt(1 + k * k) - 1); }
  function roofClearSection(sec, R) {
    const ck = "_roofClear" + R;
    if (sec[ck]) return sec[ck];
    const n = sec.normal, sg = n[0] >= 0 ? 1 : -1, wa = [-sg * n[1], sg * n[0]], dw = roofClearDrop(R);
    const sh = function (p) { return [p[0] - dw * wa[0], p[1] - dw * wa[1]]; };
    const roof = /(roof_outer|upper_lip|roof_inner)$/;
    const P0 = sec.P0.map(function (p, i) { return roof.test(sec.names[i]) ? sh(p) : p.slice(); });
    const P1 = sec.P1.map(function (p, i) { return roof.test(sec.names[i]) ? sh(p) : p.slice(); });
    const proj = function (p) { return p[0] * wa[0] + p[1] * wa[1]; };
    const ins = sec.inside.map(proj), top = ins.slice().sort(function (a, b) { return b - a; })[1];
    const inside = sec.inside.map(function (p, i) { return ins[i] >= top - 1e-9 ? sh(p) : p.slice(); });
    const gp = sec.gate.map(proj);
    const gate = sec.gate.map(function (p, i) { return gp[i] >= Math.max(gp[0], gp[1]) - 1e-9 ? sh(p) : p.slice(); });
    const out = Object.assign({}, sec, { P0: P0, P1: P1, inside: inside, gate: gate, key: sec.key + "+roofR",
      how: (sec.how || "") + "; roof lowered " + dw.toFixed(5) + " m for the sloped-roof ball clearance (derived)", roofDrop: dw });
    Object.defineProperty(sec, ck, { value: out, enumerable: false });
    return out;
  }

  // ---------------------------------------------------------------- fused fast path
  // Prepared section: flat obstacle arrays + per-obstacle bounding boxes + the classify() bbox.
  function prepSection(sec) {
    if (sec._prep) return sec._prep;
    const ns = sec.P0.length, ob = new Float64Array(ns * 8);
    let bx0 = Infinity, bx1 = -Infinity, bz0 = Infinity, bz1 = -Infinity;
    for (let j = 0; j < ns; j++) {
      const a = sec.P0[j], b = sec.P1[j];
      ob[8 * j] = a[0]; ob[8 * j + 1] = a[1]; ob[8 * j + 2] = b[0]; ob[8 * j + 3] = b[1];
      ob[8 * j + 4] = Math.min(a[0], b[0]); ob[8 * j + 5] = Math.max(a[0], b[0]);
      ob[8 * j + 6] = Math.min(a[1], b[1]); ob[8 * j + 7] = Math.max(a[1], b[1]);
      bx0 = Math.min(bx0, a[0], b[0]); bx1 = Math.max(bx1, a[0], b[0]);
      bz0 = Math.min(bz0, a[1], b[1]); bz1 = Math.max(bz1, a[1], b[1]);
    }
    let izMin = Infinity;
    for (const q of sec.inside) {
      bx0 = Math.min(bx0, q[0]); bx1 = Math.max(bx1, q[0]); bz0 = Math.min(bz0, q[1]); bz1 = Math.max(bz1, q[1]);
      izMin = Math.min(izMin, q[1]);
    }
    const gt = sec.gate;
    const pr = { ns: ns, ob: ob, bx0: bx0, bx1: bx1, bz0: bz0, bz1: bz1, izMin: izMin, inside: sec.inside,
                 g0x: gt[0][0], g0z: gt[0][1], g1x: gt[1][0], g1z: gt[1][1] };
    Object.defineProperty(sec, "_prep", { value: pr, enumerable: false });
    return pr;
  }

  function zStopFor(h, pr) {
    // relative stop height: the export's 0.4 m, lowered if needed so the stop stays below the cell
    // (a stop anywhere below the inside polygon cannot change clean / not clean)
    return Math.min(Z_STOP_REL, pr.izMin - 0.05 - h);
  }

  // One shot: integrate (physics.js integrate, RK4, same arithmetic) and classify on the fly
  // (physics.js classify on X*cos(psi)). Returns 1 clean / 0 not; out[0] = minClear, out[1] = entry
  // angle (deg, NaN if none), out[2] = code (1 clean, 2 hit, 3 miss, 4 miss: descending past the HIVE),
  // out[3] = closest approach of the ball centre to the gate segment (m; only points inside the box,
  // used to decide which in-between hood-angle rows are worth evaluating). Early exits only when the rest
  // of the path provably cannot change the result (checked against physics.js in tests).
  // c3 (optional, PM-013) = {cell, aimX, tp}: classify against the 3D cell (physics.js classifyOblique3D,
  // s = (aimX - x) * tp with tp = tan(psi)) instead of the section; pr must then be the s = 0 section.
  function fastShot(v, thDeg, cps, S0, p, pr, d, h, zStop, out, dt, tMax, c3) {
    dt = dt || 2e-3; tMax = tMax || 3.0;
    const th = thDeg * Math.PI / 180, R = p.radius;
    const q = 0.5 * p.rho * Math.PI * R * R / p.mass, cd = p.Cd, g = p.g || 9.80665;
    const w0 = S0 * v / R, sgn = Math.sign(w0), aw0 = Math.abs(w0);
    const useM = p.c1 > 0 && S0 !== 0 && p.rho > 0;
    const k = p.k || 0, c1 = p.c1, clmax = p.clmax;
    const ns = pr.ns, ob = pr.ob, inside = pr.inside, Rb = R;
    const cell = c3 ? c3.cell : null, aimX = c3 ? c3.aimX : 0, tp = c3 ? c3.tp : 0;
    let hint = -1, lastI = -2;
    const m = Rb + 0.2, bx0 = pr.bx0 - m, bx1 = pr.bx1 + m, bz0 = pr.bz0 - m, bz1 = pr.bz1 + m;
    // x-exit is safe when lift can never beat gravity (speed^2 <= v^2 + 2 g max(0, -zStop)) and
    // the spin is backspin or zero: then once descending past the box the ball never comes back
    const vmax2 = v * v + 2 * g * Math.max(0, -zStop);
    // optional drag / draft terms (physics.js aeroExt): same RK4 through ext.acc; a draft can push the ball back,
    // so the x-exit shortcut is off then
    const ext = P.aeroExt(p, S0, v), EA = [0, 0];
    // (lift options: the largest |Cl| a Cl table / reverse-Magnus blend can reach, and no negative lift; eps scales
    // lift and gravity alike so it does not enter the bound)
    const liftAny = S0 !== 0 && p.rho > 0 && P.liftOn(p);
    const xExitOK = (!liftAny || (sgn >= 0 && P.liftNonNeg(p) && q * P.clMaxOf(p) * vmax2 < g)) && !(ext && ext.wind);
    const nT = Math.ceil(tMax / dt) + 1;
    let x = 0, z = 0, vx = v * Math.cos(th), vz = v * Math.sin(th), t = 0;
    let pX = 0, pZ = 0, ppX = 0, ppZ = 0;            // points n-1 and n-2 (shot-axis X, rel. z)
    let minC = Infinity, gNear = Infinity;
    const gx0 = pr.g0x, gz0 = pr.g0z, gdx = pr.g1x - pr.g0x, gdz = pr.g1z - pr.g0z, gden = gdx * gdx + gdz * gdz;
    out[3] = Infinity;
    for (let n = 1; n < nT; n++) {
      // ---- RK4 step (identical arithmetic to physics.js integrate/acc)
      let a1x, a1z, a2x, a2z, a3x, a3z, a4x, a4z;
      if (ext) {
        ext.acc(t, vx, vz, EA); a1x = EA[0]; a1z = EA[1];
        ext.acc(t + dt / 2, vx + dt / 2 * a1x, vz + dt / 2 * a1z, EA); a2x = EA[0]; a2z = EA[1];
        ext.acc(t + dt / 2, vx + dt / 2 * a2x, vz + dt / 2 * a2z, EA); a3x = EA[0]; a3z = EA[1];
        ext.acc(t + dt, vx + dt * a3x, vz + dt * a3z, EA); a4x = EA[0]; a4z = EA[1];
      } else {
        let ux = vx, uz = vz, tt = t;
        let sp = Math.sqrt(ux * ux + uz * uz);
        a1x = -q * cd * sp * ux; a1z = -q * cd * sp * uz - g;
        if (useM) { const w = aw0 * Math.exp(-k * tt), S = w * R / Math.sqrt(sp * sp + 1e-12), Cl = Math.min(c1 * S, clmax), f = q * Cl * sp * sgn; a1x -= f * uz; a1z += f * ux; }
        ux = vx + dt / 2 * a1x; uz = vz + dt / 2 * a1z; tt = t + dt / 2;
        sp = Math.sqrt(ux * ux + uz * uz);
        a2x = -q * cd * sp * ux; a2z = -q * cd * sp * uz - g;
        if (useM) { const w = aw0 * Math.exp(-k * tt), S = w * R / Math.sqrt(sp * sp + 1e-12), Cl = Math.min(c1 * S, clmax), f = q * Cl * sp * sgn; a2x -= f * uz; a2z += f * ux; }
        ux = vx + dt / 2 * a2x; uz = vz + dt / 2 * a2z;
        sp = Math.sqrt(ux * ux + uz * uz);
        a3x = -q * cd * sp * ux; a3z = -q * cd * sp * uz - g;
        if (useM) { const w = aw0 * Math.exp(-k * tt), S = w * R / Math.sqrt(sp * sp + 1e-12), Cl = Math.min(c1 * S, clmax), f = q * Cl * sp * sgn; a3x -= f * uz; a3z += f * ux; }
        ux = vx + dt * a3x; uz = vz + dt * a3z; tt = t + dt;
        sp = Math.sqrt(ux * ux + uz * uz);
        a4x = -q * cd * sp * ux; a4z = -q * cd * sp * uz - g;
        if (useM) { const w = aw0 * Math.exp(-k * tt), S = w * R / Math.sqrt(sp * sp + 1e-12), Cl = Math.min(c1 * S, clmax), f = q * Cl * sp * sgn; a4x -= f * uz; a4z += f * ux; }
      }
      x += dt * (vx + dt / 6 * (a1x + a2x + a3x));
      z += dt * (vz + dt / 6 * (a1z + a2z + a3z));
      vx += dt / 6 * (a1x + 2 * a2x + 2 * a3x + a4x);
      vz += dt / 6 * (a1z + 2 * a2z + 2 * a3z + a4z);
      t += dt;
      const cX = x * cps;
      // ---- classify segment i = n-1 (points n-1 -> n), as physics.js classify
      const i = n - 1;
      const ax = pX - d, az = pZ + h, bx = cX - d, bz = z + h;
      const sx0 = ax < bx ? ax : bx, sx1 = ax < bx ? bx : ax, sz0 = az < bz ? az : bz, sz1 = az < bz ? bz : az;
      if (!(sx1 < bx0 || sx0 > bx1 || sz1 < bz0 || sz0 > bz1)) {
        {
          let tg = ((bx - gx0) * gdx + (bz - gz0) * gdz) / gden;
          tg = tg < 0 ? 0 : tg > 1 ? 1 : tg;
          const ex = bx - gx0 - tg * gdx, ez = bz - gz0 - tg * gdz, e = ex * ex + ez * ez;
          if (e < gNear) { gNear = e; out[3] = Math.sqrt(e); }
        }
        const ay = cell ? (aimX - ax) * tp : 0;
        if (i > 0 && (cell ? P.inside3D(cell, ax, ay, az, Rb) : P.insideConvex(ax, az, inside))) {
          const dvx = pX - ppX, dvz = pZ - ppZ;
          out[0] = minC; out[1] = Math.atan2(-dvz, Math.abs(dvx) + 1e-300) * 180 / Math.PI; out[2] = 1;
          return 1;
        }
        let best = Infinity;
        const lim = minC + Rb;
        if (cell) { best = P.stepDist3D(cell, ax, ay, az, bx, (aimX - bx) * tp, bz, lim, hint, lastI === i - 1); hint = P.faceHit.j; lastI = i; }
        else for (let j = 0; j < ns; j++) {
          const o = 8 * j;
          // box lower bound: skip obstacles that cannot lower minClear (exact)
          const ddx = ob[o + 4] > sx1 ? ob[o + 4] - sx1 : (sx0 > ob[o + 5] ? sx0 - ob[o + 5] : 0);
          const ddz = ob[o + 6] > sz1 ? ob[o + 6] - sz1 : (sz0 > ob[o + 7] ? sz0 - ob[o + 7] : 0);
          if (ddx * ddx + ddz * ddz >= lim * lim && ddx + ddz > 0) continue;
          const dd = P.segSeg(ax, az, bx, bz, ob[o], ob[o + 1], ob[o + 2], ob[o + 3]);
          if (dd < best) best = dd;
        }
        if (best - Rb < minC) minC = best - Rb;
        if (best - Rb < 0) { out[0] = minC; out[1] = NaN; out[2] = 2; return 0; }
      } else if (xExitOK && vz < 0 && vx > 0 && bx > bx1) {
        out[0] = minC; out[1] = NaN; out[2] = 4; return 0;     // past the HIVE, descending: miss
      }
      ppX = pX; ppZ = pZ; pX = cX; pZ = z;
      if (z < zStop && vz < 0) break;
    }
    const lx = pX - d, lz = pZ + h;
    if (cell ? P.inside3D(cell, lx, (aimX - lx) * tp, lz, Rb) : P.insideConvex(lx, lz, inside)) {
      out[0] = minC; out[1] = NaN; out[2] = 1; return 1;
    }
    out[0] = minC; out[1] = NaN; out[2] = 3; return 0;
  }


  // ---------------------------------------------------------------- shooting on the move / 3D flight (PM-016)
  // research/MISSING_EFFECTS.md build-next 2a, 2b, 2f. Used only when q.move or a sideways draft is set (and by
  // hitChance); with every option off the planar fast path above is untouched.
  // Cell frame (3D cell of fastShot): x toward the HIVE (release at x = -d), s lateral, z up (absolute, release at h).
  // Field -> frame is a proper rotation: sg = +1 on the far (unfav) side, -1 on the near (fav) side; x_s = sg x_f,
  // s = sg y_f, velocities alike, yaw rates unchanged. (The planar model's s0 = y on both sides is a mirror on the
  // near side; the cell is symmetric in s, so at rest both give the same answer: tests/js_move_check.js.)
  // Robot ground velocity at the exit point (frame) = along u + across n + sg (vx, vy) + wz x r_exit, u = the
  // horizontal aim direction (release -> aim point), n = z x u (to the left of the shot).
  // Ball launch velocity = shooter-relative exit velocity + robot velocity. Shooter-relative: speed v, exit angle
  // theta + d0 (d0 = ASSUMED/user exit-angle offset from the hood angle). Lead on (default): the shooter turns so
  // the ground track of the ball still points at the aim point (its sideways part cancels the robot's); off: the
  // shooter points at the aim point and the ball drifts sideways. Spin: backspin S v / R about the horizontal axis
  // perpendicular to the shooter direction, plus the robot yaw rate about z (no-spin twin: no spin at all).
  function moveFor(q) {
    const mv = q.move || {}, w = q.wind || {};
    const along = +mv.along || 0, across = +mv.across || 0, vxf = +mv.vx || 0, vyf = +mv.vy || 0;
    const wz = rad(+mv.wz || 0), d0 = +mv.d0 || 0, side = +w.side || 0;
    // q.move given (even all zero) or a sideways draft: the 3D path is used (at rest it equals the 3D cell model)
    const any = !!q.move || side !== 0;
    return { any: any, along: along, across: across, vx: vxf, vy: vyf, wz: wz, d0: d0, lead: mv.lead !== false,
             rExit: mv.rExit, side: side };
  }
  function frameFor(ps, m, q) {
    const sg = ps.side === "unfav" ? 1 : -1, d = ps.d, aimX = ps.Lh - ps.d, s0 = sg * q.y;
    const hx = aimX + d, hy = -s0, hn = Math.sqrt(hx * hx + hy * hy), ux = hx / hn, uy = hy / hn, nx = -uy, ny = ux;
    // exit offset from the turn centre (field): q.move.rExit [fwd, left] in the chassis frame, else the robot
    // offset of the footprint (release point - chassis centre; ASSUMED 0 unless set)
    let rx = 0, ry = 0;
    const fp = ps.footprint || {};
    if (m.rExit) {
      const hd = rad(fp.heading !== null && fp.heading !== undefined ? fp.heading : ps.bearingDeg);
      rx = Math.cos(hd) * m.rExit[0] - Math.sin(hd) * m.rExit[1]; ry = Math.sin(hd) * m.rExit[0] + Math.cos(hd) * m.rExit[1];
    } else if (isFinite(fp.cx) && isFinite(fp.cy)) { rx = q.x - fp.cx; ry = q.y - fp.cy; }
    const vrx = m.along * ux + m.across * nx + sg * (m.vx - m.wz * ry), vry = m.along * uy + m.across * ny + sg * (m.vy + m.wz * rx);
    return { sg: sg, d: d, s0: s0, aimX: aimX, ux: ux, uy: uy, nx: nx, ny: ny, vrx: vrx, vry: vry,
             vr: Math.sqrt(vrx * vrx + vry * vry), wz: m.wz, d0: m.d0, lead: m.lead, rExit: [rx, ry], side: m.side };
  }
  // launch state for one shot (frame). dPsi (rad) = heading scatter of the shooter direction (+ = counter-clockwise
  // seen from above). Returns null when the lead cannot cancel the sideways robot speed (|v_n| > v cos theta).
  function launch3(F, v, thDeg, S, R, dPsi, out) {
    const te = rad(thDeg + F.d0), vh = v * Math.cos(te), vz = v * Math.sin(te);
    const rn = F.vrx * F.nx + F.vry * F.ny;
    let ex, ey;
    if (F.lead) {
      if (vh < Math.abs(rn)) return null;
      const a = Math.sqrt(vh * vh - rn * rn);
      ex = a * F.ux - rn * F.nx; ey = a * F.uy - rn * F.ny;
    } else { ex = vh * F.ux; ey = vh * F.uy; }
    if (dPsi) { const c = Math.cos(dPsi), s = Math.sin(dPsi), t = c * ex - s * ey; ey = s * ex + c * ey; ex = t; }
    const eh = Math.sqrt(ex * ex + ey * ey), w = S * v / R;
    out.x0 = [-F.d, F.s0, 0]; out.v0 = [ex + F.vrx, ey + F.vry, vz];
    out.w0 = S !== 0 ? [w * ey / eh, -w * ex / eh, F.wz] : [0, 0, 0];
    // shooter turn away from the aim line (deg, + = toward n, the left of the shot)
    out.lead = deg(Math.atan2(ey * F.ux - ex * F.uy, ex * F.ux + ey * F.uy));
    return out;
  }
  function params3(p, F) {
    const w = p.wind || [0, 0], al = +w[0] || 0, up = +w[1] || 0, sd = F.side || 0;
    if (!al && !up && !sd) return p;
    return Object.assign({}, p, { wind3: [al * F.ux + sd * F.nx, al * F.uy + sd * F.ny, up] });
  }
  // fastShot on the 3D path: same out contract (out[0] minClear, out[1] entry angle, out[2] code, out[3] gate
  // distance; code 5 = the lead cannot cancel the sideways robot speed). Classifies on the 3D cell on the fly.
  function fastShot3D(F, v, thDeg, S, p, pr, cell, h, zStop, out, dPsi) {
    const L = launch3(F, v, thDeg, S, p.radius, dPsi || 0, {});
    out[3] = Infinity;
    if (!L) { out[0] = -Infinity; out[1] = NaN; out[2] = 5; return 0; }
    const p3 = params3(p, F), acc = P.makeAcc3(p3, L.w0), Rb = p.radius, g = p.g || 9.80665, dt = 2e-3;
    const nT = Math.ceil(3.0 / dt) + 1;
    const m = Rb + 0.2, bx0 = pr.bx0 - m, bx1 = pr.bx1 + m, bz0 = pr.bz0 - m, bz1 = pr.bz1 + m;
    const q = 0.5 * p.rho * Math.PI * Rb * Rb / p.mass, vb = v + F.vr, vmax2 = vb * vb + 2 * g * Math.max(0, -zStop);
    const liftAny = S !== 0 && p.rho > 0 && P.liftOn(p);
    const xExitOK = (!liftAny || (S > 0 && P.liftNonNeg(p) && q * P.clMaxOf(p) * vmax2 < g)) && !p3.wind3;
    const gx0 = pr.g0x, gz0 = pr.g0z, gdx = pr.g1x - pr.g0x, gdz = pr.g1z - pr.g0z, gden = gdx * gdx + gdz * gdz;
    const a1 = [0, 0, 0], a2 = [0, 0, 0], a3 = [0, 0, 0], a4 = [0, 0, 0], hh = dt / 2, zs = zStop + h;
    let x = L.x0[0], y = L.x0[1], z = h, vx = L.v0[0], vy = L.v0[1], vz = L.v0[2], t = 0;
    let pX = x, pY = y, pZ = z, ppX = x, ppZ = z, minC = Infinity, gNear = Infinity, hint = -1, lastI = -2;
    for (let n = 1; n < nT; n++) {
      acc(t, vx, vy, vz, a1);
      acc(t + hh, vx + hh * a1[0], vy + hh * a1[1], vz + hh * a1[2], a2);
      acc(t + hh, vx + hh * a2[0], vy + hh * a2[1], vz + hh * a2[2], a3);
      acc(t + dt, vx + dt * a3[0], vy + dt * a3[1], vz + dt * a3[2], a4);
      x += dt * (vx + dt / 6 * (a1[0] + a2[0] + a3[0]));
      y += dt * (vy + dt / 6 * (a1[1] + a2[1] + a3[1]));
      z += dt * (vz + dt / 6 * (a1[2] + a2[2] + a3[2]));
      vx += dt / 6 * (a1[0] + 2 * a2[0] + 2 * a3[0] + a4[0]);
      vy += dt / 6 * (a1[1] + 2 * a2[1] + 2 * a3[1] + a4[1]);
      vz += dt / 6 * (a1[2] + 2 * a2[2] + 2 * a3[2] + a4[2]);
      t += dt;
      const i = n - 1, ax = pX, ay = pY, az = pZ, bx = x, by = y, bz = z;
      const sx0 = ax < bx ? ax : bx, sx1 = ax < bx ? bx : ax, sz0 = az < bz ? az : bz, sz1 = az < bz ? bz : az;
      if (!(sx1 < bx0 || sx0 > bx1 || sz1 < bz0 || sz0 > bz1)) {
        {
          let tg = ((bx - gx0) * gdx + (bz - gz0) * gdz) / gden;
          tg = tg < 0 ? 0 : tg > 1 ? 1 : tg;
          const ex = bx - gx0 - tg * gdx, ez = bz - gz0 - tg * gdz, e = ex * ex + ez * ez;
          if (e < gNear) { gNear = e; out[3] = Math.sqrt(e); }
        }
        if (i > 0 && P.inside3D(cell, ax, ay, az, Rb)) {
          out[0] = minC; out[1] = Math.atan2(-(pZ - ppZ), Math.abs(pX - ppX) + 1e-300) * 180 / Math.PI; out[2] = 1;
          return 1;
        }
        const best = P.stepDist3D(cell, ax, ay, az, bx, by, bz, minC + Rb, hint, lastI === i - 1);
        hint = P.faceHit.j; lastI = i;
        if (best - Rb < minC) minC = best - Rb;
        if (best - Rb < 0) { out[0] = minC; out[1] = NaN; out[2] = 2; return 0; }
      } else if (xExitOK && vz < 0 && vx > 0 && bx > bx1) {
        out[0] = minC; out[1] = NaN; out[2] = 4; return 0;
      }
      ppX = pX; ppZ = pZ; pX = x; pY = y; pZ = z;
      if (z < zs && vz < 0) break;
    }
    if (P.inside3D(cell, pX, pY, pZ, Rb)) { out[0] = minC; out[1] = NaN; out[2] = 1; return 1; }
    out[0] = minC; out[1] = NaN; out[2] = 3; return 0;
  }
  // reference (non-fused) 3D shot: physics.js integrate3D (absolute z, release at h); classify with P.classifyPath3D
  function path3D(F, v, thDeg, S, p, h, zStop, dPsi) {
    const L = launch3(F, v, thDeg, S, p.radius, dPsi || 0, {});
    if (!L) return null;
    const path = P.integrate3D([L.x0[0], L.x0[1], h], L.v0, L.w0, params3(p, F), 2e-3, 3.0, zStop + h);
    path.launch = L;
    return path;
  }


  // ---------------------------------------------------------------- helpers
  function rpm(v, vu) { return v / vu / (Math.PI * WHEEL_D) * 60; }
  function vFromRpm(r, vu) { return r / 60 * (Math.PI * WHEEL_D) * vu; }
  function ballSpinRpm(v, S) { return Math.abs(S) * v / R_BALL * 60 / (2 * Math.PI); }

  // ---------------------------------------------------------------- flywheel droop readout (PM-022)
  // JS twin of src/launcher.py droop_readout() (tests/js_droop_check.js, tests/test_launcher.py): coasting wheel during
  // contact, fixed hood. Per-shot drop = R_w m [(v - v_in) + kI S v R_b / r_c] / (2 I_w)   (impulse, generalised Brettle)
  //   + c_rr k_n delta rho T / I_w, rho = R_w + r_c, T = wrap rho / v   (rolling hysteresis), rad/s -> rpm. No fitted factor;
  // within about 1.5 % of hood_model on its RPM_GRID (PREDICTED), about 2 % at 2000-6000 rpm for I_w 5e-5..1e-3 (reads high
  // below 2000 rpm with a light wheel). Recovery = launcher.recovery_time: linear motor line at
  // V/12, Infinity when the rpm is at or above the free speed at that voltage. Not modelled: motor drive during contact,
  // controller lag, current limit, motor rotor inertia. Values = launcher PARAMS: m, R_b CONFIRMED; R_w, delta user;
  // kI, I_w, k_n, lam, c_rr, wrap, v_in ASSUMED.
  const DROOP = { m: 0.025, Rb: 0.0355, kI: 0.63, Rw: 0.049, Iw: 2.65e-4, delta: 0.004, kn: 4000, lam: 1.0, crr: 0.02,
    wrapDeg: 90, vIn: 0.5, volts: 12, gear: 1, motor: "gobilda",
    motors: { gobilda: { label: "goBILDA 5203 1:1", freeRpm: 6000, stall: 0.144 },      // CONFIRMED datasheet (PARAMS)
              revhd: { label: "REV HD Hex (bare)", freeRpm: 6000, stall: 0.105 } } };   // CONFIRMED datasheet (PARAMS)
  function droopReadout(wheelRpm, v, S, o) {
    const c = Object.assign({}, DROOP, o || {}), mo = DROOP.motors[c.motor] || DROOP.motors.gobilda, R2 = 2 * Math.PI / 60;
    const freeRpm = c.freeRpm !== undefined ? c.freeRpm : mo.freeRpm, stall = c.stall !== undefined ? c.stall : mo.stall;
    const rc = c.Rb - c.lam * c.delta / 2, rho = c.Rw + rc, ve = Math.max(v, 1e-9), vf = c.volts / 12;
    const jw = c.m * ((ve - c.vIn) + c.kI * S * ve * c.Rb / rc) / 2, dImp = c.Rw * Math.max(jw, 0) / c.Iw;
    const tc = rad(c.wrapDeg) * rho / ve, dHys = c.crr * c.kn * c.delta * rho * tc / c.Iw, drop = (dImp + dHys) / R2;
    const wf = freeRpm * R2 / c.gear * vf, wt = wheelRpm * R2;
    const rec = wt >= wf ? Infinity : c.Iw * wf / (c.gear * stall * vf) * Math.log((wf - (wt - drop * R2)) / (wf - wt));
    return { dropRpm: drop, dropPct: wheelRpm > 0 ? 100 * drop / wheelRpm : Infinity, impulseRpm: dImp / R2, hystRpm: dHys / R2,
             contactS: tc, recoverS: rec, minIntervalS: tc + rec, freeRpmLoaded: freeRpm / c.gear * vf, aboveFree: wt >= wf };
  }
  function now() { return (typeof performance !== "undefined" && performance.now) ? performance.now() : Date.now(); }
  function twinParams(p) { return Object.assign({}, p, { c1: 0, cl_table: null, cl_rev: 0 }); }
  function range(lo, hi, st) {
    const n = Math.max(1, Math.floor((hi - lo) / st + 1e-9) + 1), a = new Float64Array(n);
    for (let i = 0; i < n; i++) a[i] = Math.round((lo + i * st) * 1e6) / 1e6;
    return a;
  }

  // 3D cell (PM-013) for the s = 0 section of that side, cached on the section object
  function cellFor(sec, q) {
    const ridge = q.ridge !== false, wallT = q.wallT !== undefined ? q.wallT : P.CELL3D.WALL_T;
    const key = (ridge ? "r" : "f") + wallT;
    if (!sec._cells) Object.defineProperty(sec, "_cells", { value: {}, enumerable: false });
    return sec._cells[key] || (sec._cells[key] = P.buildCell3D(sec, { ridge: ridge, wallT: wallT }));
  }

  // q.sideWalls (default true): 3D cell model (side walls, pentagon roof along the real path);
  // false = the PM-005/PM-009 section model at s_eff(psi) (the exported masks).
  function context(q, force3D) {
    const mv = moveFor(q), use3 = mv.any || !!force3D;
    const sideWalls = q.sideWalls !== false || use3;      // the 3D path needs the 3D cell
    const ps = pose(q.x, q.y, q.meta, { sideWalls: sideWalls, robot: q.robot });
    let sec = sectionFor(ps.side, sideWalls ? 0 : ps.psi, q.meta);
    if (!sideWalls && q.roofClear) sec = roofClearSection(sec, (q.params && q.params.radius) || R_BALL);
    const pr = prepSection(sec);
    const cps = Math.cos(rad(Math.abs(ps.psi)));
    const c3 = sideWalls ? { cell: cellFor(sec, q), aimX: ps.Lh - ps.d, tp: Math.tan(rad(ps.psi)) } : null;
    const F = use3 && ps.ok ? frameFor(ps, mv, q) : null;
    return { ps: ps, sec: sec, pr: pr, cps: cps, zStop: zStopFor(q.h, pr), c3: c3, sideWalls: sideWalls, F: F,
             forced3D: use3 && q.sideWalls === false };
  }

  // the model's reference classifier on a physics.js integrateOblique path
  function classifyCtx(ctx, path, h, R) {
    return ctx.c3 ? P.classifyOblique3D(path, ctx.c3.cell, ctx.ps.d, h, R, ctx.c3.aimX, ctx.ps.psi)
                  : P.classifyOblique(path, ctx.sec, ctx.ps.d, h, R);
  }

  // largest all-clean k x k square (grid cells), like shooter_spec.best_square
  function bestSquare(clean, nTh, nV) {
    // clean is v-major: idx = iv * nTh + ith
    const dp = new Int32Array(nV * nTh);
    let bk = 0, bi = -1, bj = -1;
    for (let i = 0; i < nV; i++) for (let j = 0; j < nTh; j++) {
      const o = i * nTh + j;
      if (!clean[o]) continue;
      dp[o] = (i && j) ? 1 + Math.min(dp[o - nTh], dp[o - 1], dp[o - nTh - 1]) : 1;
      if (dp[o] > bk) { bk = dp[o]; bi = i - bk + 1; bj = j - bk + 1; }
    }
    return { k: bk, i0: bi, j0: bj };
  }

  // ---------------------------------------------------------------- solve
  function solveOne(q, S, p, ctx, onProgress, pFrom, pTo) {
    const t0 = now();
    const vR = q.vRange || [2, 16], tR = q.thRange || [15, 89.5];
    // far-side windows are narrow in theta (a few tenths of a degree): finer coarse step there
    const dv = q.dv || 0.1, dth = q.dth || (ctx.ps.side === "unfav" ? 0.1 : 0.25);
    const V = range(vR[0], vR[1], dv), TH = range(tR[0], tR[1], dth);
    const nV = V.length, nTh = TH.length, N = nV * nTh;
    const clean = new Uint8Array(N), margin = new Float32Array(N).fill(NaN), entry = new Float32Array(N).fill(NaN);
    const evald = new Uint8Array(N);
    const out = [0, 0, 0, 0], d = ctx.ps.d, h = q.h, pr = ctx.pr, cps = ctx.cps, zs = ctx.zStop;
    let nShots = 0;
    const c3 = ctx.c3;
    const F = ctx.F;
    function shot(v, th) {
      nShots++;
      return F ? fastShot3D(F, v, th, S, p, pr, c3.cell, h, zs, out) : fastShot(v, th, cps, S, p, pr, d, h, zs, out, 2e-3, 3.0, c3);
    }
    // apex bound (lift <= q*clmax*v^2 while rising): skip v whose apex cannot reach the inside polygon
    const qq = 0.5 * p.rho * Math.PI * p.radius * p.radius / p.mass, g = p.g || 9.80665;
    const dzNeed = pr.izMin - h, wnd = p.wind || [0, 0], windy = +wnd[0] !== 0 || +wnd[1] !== 0 || !!(ctx.F && ctx.F.side);
    const ieM = 1 / (1 + (+p.eps_mass || 0));
    let count = 0;
    const gate = new Float32Array(N).fill(Infinity), rowDone = new Uint8Array(nTh);
    function doRow(it, want) {
      rowDone[it] = 1;
      const th = TH[it], st = Math.sin(rad(th + (F ? F.d0 : 0)));
      let overRun = 0;
      for (let iv = 0; iv < nV; iv++) {
        if (want && !want(iv)) continue;
        const v = V[iv], o = iv * nTh + it;
        const vb = F ? v + F.vr : v;     // moving: the air speed can exceed the shooter speed by |v_robot|
        const gEff = (g - (S !== 0 && P.liftOn(p) ? qq * P.clMaxOf(p) * vb * vb : 0)) * ieM;
        if (!windy && dzNeed > 0 && gEff > 0 && (v * st) * (v * st) / (2 * gEff) < dzNeed) continue;   // cannot rise to the cell (still air only)
        evald[o] = 1;
        const c = shot(v, th);
        clean[o] = c; margin[o] = out[0]; entry[o] = out[1]; gate[o] = out[3];
        if (c) count++;
        // the ball flew over the whole HIVE box and came down past it: at this hood angle a faster
        // shot flies higher and farther still, so stop the row after 4 such shots in a row
        if (!want && out[2] === 4 && !isFinite(out[0])) { if (++overRun >= 4) break; }
        else overRun = 0;
      }
    }
    // pass 1: every stride-th hood-angle row (about 0.5 deg apart) plus the last row, all v
    const stride = q.prune === false ? 1 : Math.max(1, Math.round((q.coarseDth || 0.5) / dth));
    const nearGate = q.nearGate || 0.12, vPad = q.vPad || 3;
    for (let it = 0; it < nTh; it += stride) doRow(it, null);
    if (!rowDone[nTh - 1]) doRow(nTh - 1, null);
    if (onProgress) onProgress(pFrom + (pTo - pFrom) * 0.5);
    // pass 2: rows in between, only cells whose neighbouring pass-1 rows passed within nearGate of
    // the gate at a v within vPad cells (a clean shot passes through the gate; the pruning is
    // checked against the unpruned grid in tests/js_solver_check.js)
    for (let it = 0; it < nTh; it++) {
      if (rowDone[it]) continue;
      let a = it, b = it;
      while (a > 0 && !rowDone[a]) a--;
      while (b < nTh - 1 && !rowDone[b]) b++;
      const near = new Uint8Array(nV);
      let any = false;
      for (let iv = 0; iv < nV; iv++) {
        if (gate[iv * nTh + a] < nearGate || gate[iv * nTh + b] < nearGate) {
          any = true;
          for (let k = Math.max(0, iv - vPad); k <= Math.min(nV - 1, iv + vPad); k++) near[k] = 1;
        }
      }
      if (any) doRow(it, function (iv) { return near[iv] === 1; });
      else rowDone[it] = 2;
    }
    if (onProgress) onProgress(pFrom + (pTo - pFrom) * 0.8);
    const res = { grid: { v: V, th: TH, clean: clean, margin: margin, entry: entry, evaluated: evald, rowEvaluated: rowDone,
                          order: "v-major: index = iv * th.length + ith (theta fastest)", dv: dv, dth: dth },
                  count: count, minRpm: null, minAngle: null, minRpmTol: null, minAngleTol: null, mostForgiving: null };
    function info(v, th) { const c = shot(v, th); return { c: c, margin: out[0], entry: out[1], code: out[2] }; }
    if (count && q.refine !== false) refine(res, q, shot, info);
    else if (count) coarseOnly(res);
    if (count) {
      const bs = bestSquare(clean, nTh, nV);
      if (bs.k) {
        const ci = bs.i0 + (bs.k >> 1), cj = bs.j0 + (bs.k >> 1), o = ci * nTh + cj;
        res.mostForgiving = { v: V[ci], theta: TH[cj], rpm: rpm(V[ci], q.vu), margin: margin[o], entryAngle: entry[o],
                              k: bs.k, tolV: (bs.k - 1) / 2 * dv, tolTheta: (bs.k - 1) / 2 * dth };
      }
    }
    if (res.minRpm) Object.assign(res.minRpm, { rpm: rpm(res.minRpm.v, q.vu), ballSpinRpm: ballSpinRpm(res.minRpm.v, S) });
    if (res.mostForgiving) res.mostForgiving.ballSpinRpm = ballSpinRpm(res.mostForgiving.v, S);
    if (res.minAngle) Object.assign(res.minAngle, { rpmLo: rpm(res.minAngle.vLo, q.vu), rpmHi: rpm(res.minAngle.vHi, q.vu) });
    if (res.minRpmTol) Object.assign(res.minRpmTol, { rpm: rpm(res.minRpmTol.v, q.vu), ballSpinRpm: ballSpinRpm(res.minRpmTol.v, S) });
    if (res.minAngleTol) Object.assign(res.minAngleTol, { rpm: rpm(res.minAngleTol.v, q.vu), rpmLo: rpm(res.minAngleTol.vLo, q.vu),
                                                          rpmHi: rpm(res.minAngleTol.vHi, q.vu), ballSpinRpm: ballSpinRpm(res.minAngleTol.v, S) });
    res.S = S; res.params = p; res.shots = nShots; res.ms = now() - t0;
    return res;
  }

  function coarseOnly(res) {
    const g = res.grid, nTh = g.th.length;
    for (let iv = 0; iv < g.v.length && !res.minRpm; iv++) {
      let lo = Infinity, hi = -Infinity;
      for (let it = 0; it < nTh; it++) if (g.clean[iv * nTh + it]) { lo = Math.min(lo, g.th[it]); hi = Math.max(hi, g.th[it]); }
      if (lo <= hi) res.minRpm = { v: g.v[iv], thetaLo: lo, thetaHi: hi, refined: false };
    }
    for (let it = 0; it < nTh && !res.minAngle; it++) {
      let lo = Infinity, hi = -Infinity;
      for (let iv = 0; iv < g.v.length; iv++) if (g.clean[iv * nTh + it]) { lo = Math.min(lo, g.v[iv]); hi = Math.max(hi, g.v[iv]); }
      if (lo <= hi) res.minAngle = { theta: g.th[it], vLo: lo, vHi: hi, refined: false };
    }
  }

  // ENVELOPE: walk outward from a clean point in steps of st until 3 non-clean steps in a row (each
  // way); returns [lo, hi] of the clean values seen. It can contain hits (gaps up to 2 steps and any
  // hole narrower than st): it is NOT a clean interval. cleanFrac() samples how much of it is clean.
  function spanScan(fn, c, st, lo, hi) {
    let a = c, b = c;
    for (const dir of [-1, 1]) {
      let miss = 0;
      for (let k = 1; miss < 3; k++) {
        const x = c + dir * k * st;
        if (x < lo - 1e-9 || x > hi + 1e-9) break;
        if (fn(x)) { miss = 0; if (dir < 0) a = x; else b = x; } else miss++;
      }
    }
    return [a, b];
  }
  function cleanFrac(fn, a, b, st, maxN) {
    if (!(b > a)) return 1;
    const n = Math.min(maxN || 400, Math.max(2, Math.round((b - a) / st) + 1));
    let k = 0;
    for (let i = 0; i < n; i++) if (fn(a + (b - a) * i / (n - 1))) k++;
    return k / n;
  }
  // CONTINUOUS RUN: from a point where ok(c) holds, step outward while ok holds (no gaps), then
  // bisect the first failing step to tol. The first maxSteps steps are st/4 (the 3D cell model has thin
  // hit fringes of about 1.5 mm/s next to knife-edge minima, PM-013), later ones st. Continuous only at
  // that sampling step (narrower holes can hide between samples). A capped side is flagged.
  function cleanRun(ok, c, st, lo, hi, tol, maxSteps) {
    const e = [c, c], capped = [false, false], cap = maxSteps || 400;
    for (let k = 0; k < 2; k++) {
      const dir = k ? 1 : -1;
      let last = c, x = null, n = 0;
      for (;;) {
        const t = last + dir * (n < cap ? st / 4 : st);
        if (t < lo - 1e-9 || t > hi + 1e-9) break;
        if (!ok(t)) { x = t; break; }
        last = t;
        if (++n >= 2 * cap) { capped[k] = true; break; }
      }
      if (x !== null) { let a = last, b = x; while (Math.abs(b - a) > tol) { const m = (a + b) / 2; if (ok(m)) a = m; else b = m; } last = a; }
      e[k] = last;
    }
    return { lo: e[0], hi: e[1], capped: capped[0] || capped[1] };
  }

  // Refinement near the clean-window edges. Every refinement shot is recorded, so minRpm.v is the
  // lowest clean v seen anywhere and minAngle.theta the lowest clean theta seen anywhere.
  //  1. rows/columns at 1/5 of the coarse step around the coarse minimum: first clean value, bisected
  //  2. local pattern search around the best point (theta steps 0.025 deg / v steps 0.01 m/s)
  //  3. span at the minimum: walk outward until 3 non-clean steps
  function refine(res, q, shot0, info) {
    const g = res.grid, V = g.v, TH = g.th, nV = V.length, nTh = TH.length, dv = g.dv, dth = g.dth;
    const fv = 0.02, fth = 0.1, vTol = 0.01, thTol = 0.025;
    let mv = { v: Infinity, th: NaN }, mt = { v: NaN, th: Infinity };
    function shot(v, th) {
      const c = shot0(v, th);
      if (c) {
        if (v < mv.v || (v === mv.v && th < mv.th)) mv = { v: v, th: th };
        if (th < mt.th || (th === mt.th && v < mt.v)) mt = { v: v, th: th };
      }
      return c;
    }
    for (let iv = 0; iv < nV; iv++) for (let it = 0; it < nTh; it++) if (g.clean[iv * nTh + it]) {
      if (V[iv] < mv.v) mv = { v: V[iv], th: TH[it] };
      if (TH[it] < mt.th || (TH[it] === mt.th && V[iv] < mt.v)) mt = { v: V[iv], th: TH[it] };
    }
    const r4 = function (x) { return Math.round(x * 1e4) / 1e4; };
    // first clean v at angle th, scanning up from vFrom in steps st, bisected to vTol
    function firstV(th, vFrom, vTo, st) {
      let lo = vFrom;
      for (let v = vFrom + st; v <= vTo + 1e-9; v += st) {
        if (shot(v, th)) { let hi = v; while (hi - lo > vTol) { const m = (lo + hi) / 2; if (shot(m, th)) hi = m; else lo = m; } return hi; }
        lo = v;
      }
      return NaN;
    }
    function firstTh(v, tFrom, tTo, st) {
      let lo = tFrom;
      for (let th = tFrom + st; th <= tTo + 1e-9; th += st) {
        if (shot(v, th)) { let hi = th; while (hi - lo > thTol) { const m = (lo + hi) / 2; if (shot(v, m)) hi = m; else lo = m; } return hi; }
        lo = th;
      }
      return NaN;
    }
    // ---- 1. minimum v: thetas around every coarse row clean at the two lowest clean v columns
    const iv0 = Math.round((mv.v - V[0]) / dv);
    const thSet = new Set();
    for (let it = 0; it < nTh; it++) {
      if (!(g.clean[iv0 * nTh + it] || (iv0 + 1 < nV && g.clean[(iv0 + 1) * nTh + it]))) continue;
      for (let k = -5; k <= 5; k++) { const th = r4(TH[it] + k * dth / 5); if (th >= TH[0] - 1e-9 && th <= TH[nTh - 1] + 1e-9) thSet.add(th); }
    }
    for (const th of thSet) firstV(th, Math.max(V[0] - dv, mv.v - dv), mv.v, fv * 2.5);
    // ---- 1b. minimum theta: v columns around every coarse column clean at the two lowest clean rows
    const it0 = Math.round((mt.th - TH[0]) / dth);
    const vSet = new Set();
    for (let iv = 0; iv < nV; iv++) {
      if (!(g.clean[iv * nTh + it0] || (it0 + 1 < nTh && g.clean[iv * nTh + it0 + 1]))) continue;
      for (let k = -5; k <= 5; k++) { const v = r4(V[iv] + k * dv / 5); if (v >= V[0] - 1e-9 && v <= V[nV - 1] + 1e-9) vSet.add(v); }
    }
    for (const v of vSet) firstTh(v, Math.max(TH[0] - dth, mt.th - dth), mt.th, fth);
    // ---- 2. local pattern search (repeat while it improves, at most 3 rounds)
    for (let round = 0; round < 3; round++) {
      const before = mv.v;
      const c = mv;
      for (let k = -8; k <= 8; k++) {
        const th = r4(c.th + k * thTol);
        if (k === 0 || th < TH[0] - 1e-9 || th > TH[nTh - 1] + 1e-9) continue;
        firstV(th, c.v - 0.1, c.v - vTol, fv);
      }
      if (!(mv.v < before - 1e-9)) break;
    }
    for (let round = 0; round < 3; round++) {
      const before = mt.th;
      const c = mt;
      for (let k = -8; k <= 8; k++) {
        const v = r4(c.v + k * vTol);
        if (k === 0 || v < V[0] - 1e-9 || v > V[nV - 1] + 1e-9) continue;
        firstTh(v, c.th - 0.2, c.th - thTol, 0.05);
      }
      if (!(mt.th < before - 1e-9)) break;
    }
    // ---- 3. at each minimum: clearance and entry angle there, the continuous clean run through it
    // (sampled at 0.01 deg / 0.005 m/s, edges bisected) and the sampled envelope with its clean fraction
    const bv = mv, bt = mt, iR = info(bv.v, bv.th), iA = info(bt.v, bt.th);
    const fT = function (th) { return shot0(bv.v, th) === 1; }, fV = function (v) { return shot0(v, bt.th) === 1; };
    const rT = cleanRun(fT, bv.th, 0.01, TH[0], TH[nTh - 1], 0.002, 600);
    const rV = cleanRun(fV, bt.v, 0.005, V[0], V[nV - 1], 0.001, 2000);
    const ts = spanScan(fT, bv.th, thTol * 2, TH[0], TH[nTh - 1]);
    const vs = spanScan(fV, bt.v, fv, V[0], V[nV - 1]);
    const vEdge = Math.min(dv, 0.05);
    const tol = Object.assign({}, TOL, q.tol || {});
    res.tol = tol;
    res.minRpm = { v: bv.v, theta: bv.th, margin: iR.margin, entryAngle: iR.entry,
                   runLo: rT.lo, runHi: rT.hi, run: rT.hi - rT.lo,
                   thetaLo: ts[0], thetaHi: ts[1], envelopeCleanFrac: cleanFrac(fT, ts[0], ts[1], 0.01),
                   knifeEdge: rT.hi - rT.lo < tol.theta || !(iR.margin >= tol.margin), refined: true,
                   searchStep: { v: vTol, theta: thTol }, atRangeEdge: bv.v <= V[0] + vEdge };
    res.minAngle = { theta: bt.th, v: bt.v, margin: iA.margin, entryAngle: iA.entry,
                     runLo: rV.lo, runHi: rV.hi, run: rV.hi - rV.lo,
                     vLo: vs[0], vHi: vs[1], envelopeCleanFrac: cleanFrac(fV, vs[0], vs[1], 0.005),
                     knifeEdge: rV.hi - rV.lo < tol.v || !(iA.margin >= tol.margin), refined: true,
                     searchStep: { v: fv, theta: thTol },
                     atRangeEdge: bt.th <= TH[0] + 0.05 || vs[1] >= V[nV - 1] - vEdge || vs[0] <= V[0] + vEdge };
    // ---- 4. tolerant minima (ASSUMED tolerance, q.tol overrides): the lowest v whose hood-angle run is
    // clean with clearance >= margin over at least tol.theta, and the lowest hood angle whose speed run is
    // clean with clearance >= margin over at least tol.v. Found by search (coarse cells, then a fine scan
    // below the first qualifying column / row): the lowest one the search found, not a proven minimum.
    res.minRpmTol = tolMin(g, info, tol, "v");
    res.minAngleTol = tolMin(g, info, tol, "theta");
  }

  // ASSUMED shooter tolerance for the "tolerant" minima: a continuous clean hood-angle run of 0.2 deg
  // (about +-0.1 deg), or a speed run of 0.1 m/s (about +-0.05 m/s), with at least 2 mm clearance throughout
  const TOL = { theta: 0.2, v: 0.1, margin: 0.002 };

  function tolMin(g, info, tol, axis) {
    const V = g.v, TH = g.th, nV = V.length, nTh = TH.length;
    const byV = axis === "v";
    const need = byV ? tol.theta : tol.v, st = byV ? 0.01 : 0.005;
    const lo = byV ? TH[0] : V[0], hi = byV ? TH[nTh - 1] : V[nV - 1];
    const r4 = function (x) { return Math.round(x * 1e4) / 1e4; };
    // a = the fixed value (v when axis is "v"), x = the scanned value (theta when axis is "v")
    function ok(a, x) { const r = byV ? info(a, x) : info(x, a); return r.c === 1 && r.margin >= tol.margin; }
    function bestRun(a, cands) {
      let best = null; const seen = [];
      for (const x of cands) {
        if (seen.some(function (s) { return x >= s.lo - 1e-9 && x <= s.hi + 1e-9; })) continue;
        if (!ok(a, x)) continue;
        const r = cleanRun(function (t) { return ok(a, t); }, x, st, lo, hi, st / 4, Math.ceil(need / st) + 5);
        seen.push(r);
        if (r.hi - r.lo >= need - 1e-9 && (!best || r.hi - r.lo > best.hi - best.lo)) best = r;
      }
      return best;
    }
    function mk(a, r) {
      const c = r4((r.lo + r.hi) / 2), ic = byV ? info(a, c) : info(c, a);
      return byV ? { v: a, theta: c, thetaLo: r.lo, thetaHi: r.hi, run: r.hi - r.lo, runCapped: r.capped, margin: ic.margin, entryAngle: ic.entry }
                 : { theta: a, v: c, vLo: r.lo, vHi: r.hi, run: r.hi - r.lo, runCapped: r.capped, margin: ic.margin, entryAngle: ic.entry };
    }
    const nA = byV ? nV : nTh, A = byV ? V : TH, X = byV ? TH : V;
    const cell = function (ia, ix) { return byV ? g.clean[ia * nTh + ix] : g.clean[ix * nTh + ia]; };
    for (let ia = 0; ia < nA; ia++) {
      const cands = [];
      for (let ix = 0; ix < X.length; ix++) if (cell(ia, ix)) cands.push(X[ix]);
      if (!cands.length) continue;
      const run = bestRun(A[ia], cands);
      if (!run) continue;
      // fine scan between the previous coarse step (theta: the 0.5 deg pass-1 spacing) and this one
      const c = (run.lo + run.hi) / 2, fc = [], fs = byV ? 0.05 : 0.02;
      for (let k = -20; k <= 20; k++) fc.push(r4(c + k * fs));
      const aStep = byV ? 0.02 : 0.05, back = byV ? g.dv : Math.max(g.dth, 0.5);
      for (let a = r4(A[ia] - back + aStep); a < A[ia] - 1e-9; a = r4(a + aStep)) {
        if (a < A[0] - 1e-9) continue;
        const r2 = bestRun(a, fc);
        if (r2) return mk(a, r2);
      }
      return mk(A[ia], run);
    }
    return null;
  }

  const LABELS = {
    window: "PREDICTED (model output: clean air-only entry, not a hit probability; no repeatability claim)",
    aero: "ASSUMED (literature drag/Magnus coefficients, not POLLEN measurements)",
    drag: "included: quadratic drag Cd (ASSUMED) + capped Magnus lift with spin decay (ASSUMED)",
    section: "HIVE section at tilt 30 CONFIRMED (official CAD); 3D cell: roof drop along the real lateral path (derived from the opening profile), no s_eff",
    psi_gt_60: "ASSUMED extrapolation",
    side_walls: "modelled in 3D (default, PM-013): exact ball-centre path vs side walls, pentagon roof and lips inflated by R; side-wall inner faces at +-0.254 m CONFIRMED (manual 20 in), wall thickness 0.0508 m ASSUMED, roof slope derived from the opening profile; sideWalls: false = old section model (side walls NOT modelled, optimistic from psi 35.57 deg)",
    pose: "user", height: "user", spin: "user (S = surface spin ratio)", vu: "user/ASSUMED grip v/u",
    rpm: "derived: wheel rpm = v / (v/u) / (pi * 0.098 m) * 60",
    minRpm: "PREDICTED knife edge: lowest clean v the search found (search step 0.01 m/s); the window edge carries about 0.1 deg of path-sampling (2 ms) noise, so it can move with resolution",
    minAngle: "PREDICTED knife edge: lowest clean hood angle the search found (search step 0.025 deg); same edge noise",
    minRpmTol: "PREDICTED with an ASSUMED shooter tolerance: lowest v whose continuous clean hood-angle run (0.01 deg sampling) is at least tol.theta wide with clearance >= tol.margin at every sample (it can dip about 1 mm between samples)",
    minAngleTol: "PREDICTED with an ASSUMED shooter tolerance: lowest hood angle whose continuous clean speed run (0.005 m/s sampling) is at least tol.v wide with clearance >= tol.margin at every sample (path-sampling noise lets it dip about 1 mm between samples)",
    run: "continuous clean run through the point (runLo..runHi), sampled at 0.01 deg / 0.005 m/s, edges bisected",
    envelope: "envelope (thetaLo..thetaHi, vLo..vHi): outermost clean samples, can contain hits; envelopeCleanFrac = clean share at 0.01 deg / 0.005 m/s",
    twin: "no-spin twin (S = 0, same params, c1 = 0)",
    air: "derived from user inputs: rho = (p - 0.378 e) / (287.06 T) (simplified CIPM-2007), nu from Sutherland; default still air 20 C, 101.325 kPa, dry = 1.2041 kg/m^3",
    dragModel: "const = params Cd (ASSUMED); morrison = smooth-sphere reference curve (not POLLEN); blend = what-if partial drag crisis (ASSUMED); spin drag dCd ASSUMED",
    wind: "user: constant draft in the shot plane; drag, Magnus and S use v - w",
    grip: "PREDICTED hood cap 8.9 m/s (docs/04_launcher.md): results above it carry gripLimited = true; do not rest 'possible' on them",
  };

  const LABELS_SECTION = Object.assign({}, LABELS, {
    section: "HIVE section at tilt 30 CONFIRMED (official CAD); lateral offset s_eff ASSUMED",
    side_walls: "NOT modelled (section model, sideWalls: false); straight-line flag from psi 35.57 deg is a near-side estimate, far side not checked" });
  function labelsFor(ctx) { return ctx.sideWalls ? LABELS : LABELS_SECTION; }
  function modelNote(ctx) {
    return ctx.sideWalls
      ? "3D cell model: side walls, pentagon roof and lips along the real lateral path (ridge " + (ctx.c3.cell.ridge ? "on" : "off") +
        ", wall thickness " + ctx.c3.cell.wallT + " m ASSUMED); section model selectable with sideWalls: false"
      : "section model at s_eff = " + ctx.sec.s.toFixed(4) + " m (ASSUMED), cell side walls NOT modelled (same as the exported masks)" +
        (ctx.sec.roofDrop ? "; sloped-roof ball clearance on (roof lowered " + ctx.sec.roofDrop.toFixed(5) + " m, derived)" : "");
  }

  // ---------------------------------------------------------------- air, drag and draft options (build-next 1, 2, 4, 6)
  // q.air: undefined = still air 20 C / 101.325 kPa / dry (rho 1.2041 kg/m^3, derived; the exported masks use the
  //   rounded 1.20 of research/params_lit.json, about 1 mm apart at the reference shot, derived);
  //   {tC, pKPa or altM, rh (0..1)} = venue air (user inputs); false = keep params.rho as given.
  // q.drag: {model: 'const' (default) | 'morrison' | 'blend', spin: dCd (0 default, 0.08, 0.18), cdPost, re1, re2}.
  // q.wind: {along, up} m/s constant draft (along = toward the HIVE in the shot plane, up = vertical), default 0.
  // Every option only changes the flight; the twin gets the same air, drag model and draft (spin drag cannot act on it).
  function airFor(q) {
    if (q.air === false) return null;
    const a = q.air || {};
    const pPa = a.pKPa !== undefined ? a.pKPa * 1000 : (a.altM !== undefined ? P.pressureFromAltitude(a.altM) : 101325);
    return P.airState(a.tC !== undefined ? a.tC : 20, pPa, a.rh || 0);
  }
  function effParams(q) {
    const p = Object.assign({}, q.params), air = airFor(q), dr = q.drag || {}, w = q.wind || {};
    if (air) { p.rho = air.rho; p.nu = air.nu; }
    if (dr.model && dr.model !== "const") {
      p.cd_model = dr.model;
      if (dr.cdPost !== undefined) p.cd_post = dr.cdPost;
      if (dr.re1 !== undefined) p.re1 = dr.re1;
      if (dr.re2 !== undefined) p.re2 = dr.re2;
    }
    if (dr.spin) p.dcd_spin = +dr.spin;
    if (w.along || w.up) p.wind = [+w.along || 0, +w.up || 0];
    // lift options (2d): user Cl(S) table, reverse-Magnus blend; gyro-correct S on the 3D path (2c)
    const lf = q.lift || {};
    if (lf.table && lf.table.length) p.cl_table = lf.table.map(function (r) { return [+r[0], +r[1]]; }).sort(function (a, b) { return a[0] - b[0]; });
    if (+lf.rev) p.cl_rev = +lf.rev;
    if (lf.gyro) p.s_perp = true;
    // effective (added) mass (2e): eps = (0.5 + phi) rho V / m with the air density in use
    if (q.effMass && q.effMass.phi !== undefined && q.effMass.phi !== null)
      p.eps_mass = P.epsFromPhi(+q.effMass.phi, p.rho, p.mass, p.radius);
    return { p: p, air: air };
  }
  function optionNotes(q, ep) {
    const n = [], p = ep.p;
    n.push(ep.air ? "air: rho " + p.rho.toFixed(4) + " kg/m^3 (" + ep.air.t_c + " C, " + (ep.air.p_pa / 1000).toFixed(2) +
      " kPa, RH " + Math.round(ep.air.rh * 100) + " %; derived from the inputs)" : "air: params rho " + p.rho + " kg/m^3 as given");
    if (p.cd_model) n.push("drag: " + (p.cd_model === "morrison" ? "Morrison smooth-sphere Cd(Re) (reference curve, not POLLEN)"
      : "what-if partial drag crisis Cd " + (p.cd_sub !== undefined ? p.cd_sub : p.Cd) + " -> " + (p.cd_post !== undefined ? p.cd_post : 0.33) + " (ASSUMED)"));
    if (p.dcd_spin) n.push("spin drag +" + p.dcd_spin + " x min(S/0.6, 1) on the backspin shot only (ASSUMED)");
    const wSide = (q.wind && +q.wind.side) || 0;
    if (p.wind || wSide) n.push("draft " + (p.wind ? p.wind[0] : 0) + " m/s along, " + (wSide ? wSide + " m/s sideways, " : "") +
      (p.wind ? p.wind[1] : 0) + " m/s up (user)");
    if (p.cl_table) n.push("lift: user Cl(S) table " + p.cl_table.map(function (r) { return "(" + r[0] + ", " + r[1] + ")"; }).join(" ") +
      ", linear between points, flat after the last (user; replaces min(c1 S, Cl_max) on the backspin shot)");
    if (p.cl_rev) n.push("reverse Magnus: below Re 4.6e4 and S 0.5 lift blends to -" + p.cl_rev +
      " (ASSUMED; smooth-sphere data, Kim 2014 / Kray 2012, not a POLLEN measurement)");
    if (p.eps_mass) n.push("effective mass: eps " + p.eps_mass.toFixed(4) + " (phi " + q.effMass.phi +
      ", ASSUMED); acceleration = (F/m + g) / (1 + eps)");
    if (p.s_perp) n.push("gyro-correct spin ratio S_perp = |w x v| R / v^2 on the 3D path (no change for pure backspin)");
    const mv = moveFor(q);
    if (q.move) n.push("robot moving (user): " + mv.along + " m/s toward the goal, " + mv.across + " m/s sideways" +
      (mv.vx || mv.vy ? ", field (" + mv.vx + ", " + mv.vy + ") m/s" : "") + ", turn " + (+q.move.wz || 0) + " deg/s, exit-angle offset d0 " +
      mv.d0 + " deg, " + (mv.lead ? "shooter leads the sideways motion" : "no lead") + "; 3D flight on the 3D cell (PREDICTED)");
    return n;
  }
  // grip-limited flag: exit speed above the PREDICTED hood cap 8.9 m/s (v/u and spin uncertain there)
  function flagGrip(res, q) {
    if (!res) return;
    const cap = P.HOOD_V_MAX;
    [["minRpm", "v"], ["minRpmTol", "v"], ["minAngle", "vLo"], ["minAngleTol", "v"], ["mostForgiving", "v"]].forEach(function (kv) {
      const r = res[kv[0]]; if (r && isFinite(r[kv[1]])) r.gripLimited = r[kv[1]] > cap + 1e-9;
    });
    res.gripCap = { v: cap, rpm: rpm(cap, q.vu) };
  }

  // ---- how much the answer moves per 0.1 m/s of robot speed (2a). At the recommended setting rec (v, theta):
  // the centre of the continuous clean run (clearance >= tol.margin) in hood angle at that v, and in speed at that
  // hood angle, with the robot 0.1 m/s faster toward the goal and 0.1 m/s faster sideways (to the left of the
  // shot). Sampled at 0.02 deg / 0.01 m/s, so a shift below about one step reads as 0. PREDICTED.
  const SENS = { per: 0.1, thStep: 0.02, thSpan: 2.0, vStep: 0.01, vSpan: 0.5 };
  function runCentre(fn, c, lo, hi, st) {
    let best = null, a = null;
    const n = Math.round((hi - lo) / st);
    for (let i = 0; i <= n + 1; i++) {
      const x = lo + i * st, ok = i <= n && fn(x);
      if (ok && a === null) a = x;
      if (!ok && a !== null) {
        const b = x - st, dist = c < a ? a - c : (c > b ? c - b : 0);
        if (!best || dist < best.dist || (dist === best.dist && b - a > best.b - best.a)) best = { a: a, b: b, dist: dist };
        a = null;
      }
    }
    return best ? (best.a + best.b) / 2 : NaN;
  }
  function moveSens(q, S, p, ctx, rec) {
    if (!ctx.F || !rec || !isFinite(rec.v) || !isFinite(rec.theta)) return null;
    const tol = Object.assign({}, TOL, q.tol || {}), out = [0, 0, 0, 0], cell = ctx.c3.cell;
    function at(F) {
      const okT = function (th) { return fastShot3D(F, rec.v, th, S, p, ctx.pr, cell, q.h, ctx.zStop, out) === 1 && out[0] >= tol.margin; };
      const okV = function (v) { return fastShot3D(F, v, rec.theta, S, p, ctx.pr, cell, q.h, ctx.zStop, out) === 1 && out[0] >= tol.margin; };
      return { th: runCentre(okT, rec.theta, rec.theta - SENS.thSpan, rec.theta + SENS.thSpan, SENS.thStep),
               v: runCentre(okV, rec.v, rec.v - SENS.vSpan, rec.v + SENS.vSpan, SENS.vStep) };
    }
    function shifted(dx, dy) {
      const F = Object.assign({}, ctx.F, { vrx: ctx.F.vrx + dx, vry: ctx.F.vry + dy });
      F.vr = Math.sqrt(F.vrx * F.vrx + F.vry * F.vry);
      return F;
    }
    const F = ctx.F, b = at(F), t = at(shifted(SENS.per * F.ux, SENS.per * F.uy)), s = at(shifted(SENS.per * F.nx, SENS.per * F.ny));
    function d(x) { return { dTheta: x.th - b.th, dV: x.v - b.v, dRpm: rpm(x.v, q.vu) - rpm(b.v, q.vu), lost: !isFinite(x.th) && !isFinite(x.v) }; }
    return { per: SENS.per, at: { v: rec.v, theta: rec.theta, rpm: rpm(rec.v, q.vu) }, centre: { theta: b.th, v: b.v },
             toward: d(t), sideways: d(s), step: { theta: SENS.thStep, v: SENS.vStep },
             note: "PREDICTED shift of the centre of the clean run per " + SENS.per + " m/s (sampled at " + SENS.thStep +
                   " deg / " + SENS.vStep + " m/s; NaN = no clean run within " + SENS.thSpan + " deg / " + SENS.vSpan + " m/s)" };
  }

  // ---- chance it goes in (2b): Monte Carlo of the 3D path at one setting (v, theta) with ASSUMED launch scatter
  // (speed sigma sv relative, angle sigma sth deg, heading sigma spsi deg; defaults = src/robustness.py ERR_SETS
  // nominal). Every aero set of this spin (Cl low / nominal / high) and the no-spin twin use the SAME draws
  // (normals from P.normals(seed, 3 n): z_v, z_theta, z_psi per shot), counts with a Wilson 95 % interval.
  // A model probability under assumed scatter, NOT a measured repeatability. src/robustness.py hit_chance /
  // mc_shots(cell=...) is the Python twin (tests/test_move.py).
  const HC_SIG = { sv: 0.015, sth: 0.40, spsi: 0.50 };
  const HC_NOTE = "model probability under ASSUMED launch scatter (not a measured repeatability)";
  function hcSig(o) { return Object.assign({}, HC_SIG, (o && o.sig) || {}); }
  // the aero sets of this spin: Cl low / nominal / high from meta.cases (S != 0); a user Cl(S) table replaces the
  // lift of every set, so low / nominal / high would be the same run under three names: it runs once as "Cl_table"
  function hcSets(q, ep, names) {
    const S = q.S || 0, tab = !!(ep.p.cl_table && ep.p.cl_table.length);
    if (!names) names = S !== 0 && q.meta && !tab ? ["Cl_low", "nominal", "Cl_high"] : ["nominal"];
    const out = [];
    for (const nm of names) {
      const c = q.meta && q.meta.cases ? q.meta.cases.find(function (cc) { return cc.S === S && cc.var === nm; }) : null;
      const p = c ? effParams(Object.assign({}, q, { params: c.params })).p : ep.p;
      out.push({ name: tab && S !== 0 && nm === "nominal" ? "Cl_table" : nm, p: p });
    }
    if (!out.length) out.push({ name: "given", p: ep.p });
    return out;
  }
  // clean 3D shots among draws i0..i1-1 of Z (z_v, z_theta, z_psi per shot) at one setting
  function mcCount(ctx, h, S, p, v, theta, Z, sig, i0, i1, out) {
    const cell = ctx.c3.cell;
    let k = 0;
    for (let i = i0; i < i1; i++) {
      const vi = v * (1 + sig.sv * Z[3 * i]), ti = theta + sig.sth * Z[3 * i + 1], dp = rad(sig.spsi * Z[3 * i + 2]);
      if (fastShot3D(ctx.F, vi, ti, S, p, ctx.pr, cell, h, ctx.zStop, out, dp) === 1) k++;
    }
    return k;
  }
  function hcRow(k, n) { const w = P.wilson(k, n); return { k: k, n: n, p: k / n, lo: w[0], hi: w[1] }; }
  function hcNote(sig) {
    return HC_NOTE + "; scatter: speed " + (sig.sv * 100).toFixed(1) + " % , angle " + sig.sth + " deg, heading " +
           sig.spsi + " deg (1 sigma, ASSUMED; robustness.py ERR_SETS nominal by default); Wilson 95 % interval";
  }
  function hitChance(q, v, theta, opts) {
    const t0 = now(), o = opts || {}, n = o.n || 1000, seed = o.seed === undefined ? 20261031 : o.seed;
    const sig = hcSig(o);
    const ep = effParams(q), qq = Object.assign({}, q, { params: ep.p }), ctx = context(qq, true);
    if (!ctx.ps.ok) return { ok: false, reason: "pose not legal", n: n };
    const S = q.S || 0, Z = P.normals(seed, 3 * n), out = [0, 0, 0, 0];
    function run(Sx, p, v, theta) { return hcRow(mcCount(ctx, q.h, Sx, p, v, theta, Z, sig, 0, n, out), n); }
    const sets = hcSets(q, ep, o.sets).map(function (s) { return Object.assign({ name: s.name }, run(S, s.p, v, theta)); });
    // the twin has no lift, so it is the same for every aero set: computed once, at opts.twinAt (its own
    // recommended setting) or else at the same setting
    const ta = o.twinAt && isFinite(o.twinAt.v) && isFinite(o.twinAt.theta) ? o.twinAt : { v: v, theta: theta };
    const twin = S !== 0 ? Object.assign({ name: "no-spin twin", v: ta.v, theta: ta.theta, rpm: rpm(ta.v, q.vu),
                                           sameSetting: ta.v === v && ta.theta === theta }, run(0, twinParams(ep.p), ta.v, ta.theta)) : null;
    return { ok: true, v: v, theta: theta, rpm: rpm(v, q.vu), S: S, n: n, seed: seed, sig: sig, sets: sets, twin: twin,
             model: "3D flight on the 3D cell" + (ctx.forced3D ? " (used here although the section model is selected)" : ""),
             note: hcNote(sig), ms: now() - t0 };
  }

  // ---- best chance (PM-017): the clean-window setting (v, theta) with the highest hit chance under the ASSUMED
  // scatter, averaged over the aero sets of this spin (equal weight, ASSUMED). res = the main result of solve() or
  // its twin (res.isTwin: S = 0, no-lift params, one set). Search:
  //  0. candidates: clean grid cells at or below the hood cap 8.9 m/s (all clean cells when none is, flagged
  //     gripLimited), ranked by a smoothed clean share (Gaussian over the grid, sigma = the speed and angle
  //     scatter; heading ignored), greedy at least one sigma apart, the best k1; plus the tolerant lowest-rpm /
  //     lowest-hood and the most forgiving setting when inside the cap
  //  1. every candidate: n1 shots per set from the search draws P.normals(seed + 1, 3 n2) (common random numbers:
  //     the same draws for every candidate and set); keep those whose pooled Wilson upper bound reaches the best
  //     lower bound, at most k2 (highest mean first)
  //  2. the kept ones: extended to n2 shots on the same draws (a prefix of the longer list); winner = highest mean
  //     (ties: lower speed, then lower hood angle)
  //  3. the winner again on fresh draws P.normals(seed, 3 n) (the same draws as hitChance, so the reported chance is
  //     not biased by the selection and equals hitChance at that setting), per set with a Wilson 95 % interval
  //  4. which scatter matters most: at the winner, nominal set only, one source at a time (the other two
  //     set to 0) on the same draws; the source whose chance alone is lowest dominates
  //     (opts.breakdown === false skips it: the field-map chance layer)
  // src/robustness.py best_chance replays stages 1 to 4 on the same candidate list (tests/test_best_chance.py).
  // A model probability under ASSUMED scatter, not a measured repeatability.
  const BC = { n1: 64, n2: 400, n: 1000, k1: 24, k2: 5 };
  function bcCandidates(res, sig, k1) {
    const g = res.grid, V = g.v, TH = g.th, nV = V.length, nTh = TH.length, cap = P.HOOD_V_MAX + 1e-9, cl = g.clean;
    let inCap = false;
    for (let iv = 0; iv < nV && !inCap; iv++) {
      if (V[iv] > cap) break;
      for (let it = 0; it < nTh; it++) if (cl[iv * nTh + it]) { inCap = true; break; }
    }
    const lim = inCap ? cap : Infinity;
    // smoothed clean share: Gaussian along theta (sigma sth), then along v (sigma sv v) at candidate cells only
    const sT = Math.max(sig.sth, 0.02), rT = Math.min(nTh, Math.ceil(2.5 * sT / g.dth)), wT = [];
    for (let k = -rT; k <= rT; k++) wT.push(Math.exp(-0.5 * Math.pow(k * g.dth / sT, 2)));
    const sw = wT.reduce(function (a, b) { return a + b; }, 0);
    const sm = new Float32Array(nV * nTh);
    for (let iv = 0; iv < nV; iv++) {
      const b = iv * nTh;
      let any = false;
      for (let it = 0; it < nTh; it++) if (cl[b + it]) { any = true; break; }
      if (!any) continue;
      for (let it = 0; it < nTh; it++) {
        let s = 0;
        for (let k = -rT; k <= rT; k++) { const j = it + k; if (j >= 0 && j < nTh && cl[b + j]) s += wT[k + rT]; }
        sm[b + it] = s / sw;
      }
    }
    const cand = [];
    for (let iv = 0; iv < nV; iv++) {
      if (V[iv] > lim) break;
      const sV = Math.max(sig.sv * V[iv], 0.005), rV = Math.ceil(2.5 * sV / g.dv);
      for (let it = 0; it < nTh; it++) {
        if (!cl[iv * nTh + it]) continue;
        let s = 0, w = 0;
        for (let k = -rV; k <= rV; k++) {
          const wk = Math.exp(-0.5 * Math.pow(k * g.dv / sV, 2)), j = iv + k;
          w += wk;
          if (j >= 0 && j < nV) s += wk * sm[j * nTh + it];
        }
        cand.push({ v: V[iv], theta: TH[it], score: s / w });
      }
    }
    cand.sort(function (a, b) { return b.score - a.score || a.v - b.v || a.theta - b.theta; });
    const pick = [];
    for (const c of cand) {
      if (pick.length >= k1) break;
      const sV = Math.max(sig.sv * c.v, 0.005), sTh = Math.max(sig.sth, 0.02);
      if (pick.some(function (p) { return Math.pow((p.v - c.v) / sV, 2) + Math.pow((p.theta - c.theta) / sTh, 2) < 1; })) continue;
      pick.push({ v: c.v, theta: c.theta, from: "grid", smooth: c.score });
    }
    [["minRpmTol", "lowest rpm"], ["minAngleTol", "lowest hood"], ["mostForgiving", "most forgiving"]].forEach(function (kv) {
      const r = res[kv[0]];
      if (r && isFinite(r.v) && isFinite(r.theta) && r.v <= lim) pick.push({ v: r.v, theta: r.theta, from: kv[1], smooth: NaN });
    });
    return { list: pick, inCap: inCap, cells: cand.length };
  }
  function bestChance(q, res, opts) {
    const t0 = now(), o = Object.assign({}, BC, opts || {}), seed = o.seed === undefined ? 20261031 : o.seed;
    const sig = hcSig(o), isTwin = !!(res && res.isTwin);
    const base = { ok: false, isTwin: isTwin, sig: sig, note: hcNote(sig) };
    if (!res || !res.grid || !res.count) return Object.assign(base, { reason: "no clean setting here", ms: now() - t0 });
    const ep = effParams(q), qq = Object.assign({}, q, { params: ep.p }), ctx = context(qq, true);
    if (!ctx.ps.ok) return Object.assign(base, { reason: "pose not legal", ms: now() - t0 });
    const S = isTwin ? 0 : (q.S || 0);
    const sets = isTwin ? [{ name: "no-spin twin", p: twinParams(ep.p) }] : hcSets(q, ep, o.sets);
    const nS = sets.length, out = [0, 0, 0, 0], h = q.h;
    const cd = o.candidates ? { list: o.candidates.map(function (c) { return { v: c.v, theta: c.theta, from: c.from || "given" }; }),
                                inCap: true, cells: o.candidates.length } : bcCandidates(res, sig, o.k1);
    const C = cd.list;
    if (!C.length) return Object.assign(base, { reason: "no clean setting inside the search", ms: now() - t0 });
    const n1 = Math.min(o.n1, o.n2), n2 = o.n2, Zs = P.normals(seed + 1, 3 * n2);
    function pooled(c, n) {
      const k = c.k.reduce(function (a, b) { return a + b; }, 0), w = P.wilson(k, n * nS);
      return { mean: k / (n * nS), lo: w[0], hi: w[1] };
    }
    function better(a, b) { return a.mean - b.mean || b.v - a.v || b.theta - a.theta; }
    // stage 1
    for (const c of C) {
      c.k = sets.map(function (s) { return mcCount(ctx, h, S, s.p, c.v, c.theta, Zs, sig, 0, n1, out); });
      Object.assign(c, pooled(c, n1));
    }
    const bestLo = Math.max.apply(null, C.map(function (c) { return c.lo; }));
    const keep = C.filter(function (c) { return c.hi >= bestLo; }).sort(function (a, b) { return better(b, a); }).slice(0, o.k2);
    const s1 = C.map(function (c) { return { v: c.v, theta: c.theta, from: c.from, k: c.k.slice(), mean: c.mean }; });
    // stage 2
    for (const c of keep) {
      c.k = c.k.map(function (k0, j) { return k0 + mcCount(ctx, h, S, sets[j].p, c.v, c.theta, Zs, sig, n1, n2, out); });
      Object.assign(c, pooled(c, n2));
    }
    keep.sort(function (a, b) { return better(b, a); });
    const w = keep[0];
    // stage 3: fresh draws, the same as hitChance
    const n = o.n, Z = P.normals(seed, 3 * n);
    const rows = sets.map(function (s) { return Object.assign({ name: s.name }, hcRow(mcCount(ctx, h, S, s.p, w.v, w.theta, Z, sig, 0, n, out), n)); });
    const mean = rows.reduce(function (a, r) { return a + r.p; }, 0) / rows.length;
    // stage 4: one scatter source at a time, on the nominal set (or the Cl table / the only set)
    const ib = Math.max(0, rows.findIndex(function (r) { return r.name === "nominal" || r.name === "Cl_table"; }));
    const parts = o.breakdown === false ? [] : [["speed", { sv: sig.sv, sth: 0, spsi: 0 }], ["angle", { sv: 0, sth: sig.sth, spsi: 0 }],
                   ["heading", { sv: 0, sth: 0, spsi: sig.spsi }]].map(function (ps) {
      return Object.assign({ source: ps[0], sig: ps[1] }, hcRow(mcCount(ctx, h, S, sets[ib].p, w.v, w.theta, Z, ps[1], 0, n, out), n));
    });
    const act = parts.filter(function (r) { return r.sig.sv || r.sig.sth || r.sig.spsi; });
    const dom = act.length ? act.reduce(function (a, b) { return b.p < a.p ? b : a; }) : null;
    return { ok: true, isTwin: isTwin, S: S, v: w.v, theta: w.theta, rpm: rpm(w.v, q.vu), ballSpinRpm: ballSpinRpm(w.v, S),
             from: w.from, gripLimited: w.v > P.HOOD_V_MAX + 1e-9, inCap: cd.inCap, n: n, seed: seed, sig: sig,
             sets: rows, mean: mean, min: Math.min.apply(null, rows.map(function (r) { return r.p; })),
             max: Math.max.apply(null, rows.map(function (r) { return r.p; })),
             breakdown: o.breakdown === false ? null : { set: rows[ib].name, n: n, all: rows[ib], parts: parts, dominant: dom ? dom.source : null },
             search: { cells: cd.cells, candidates: C.length, n1: n1, n2: n2, k2: o.k2, seed: seed + 1, stage1: s1,
                       stage2: keep.map(function (c) { return { v: c.v, theta: c.theta, from: c.from, k: c.k.slice(), mean: c.mean }; }) },
             model: "3D flight on the 3D cell", label: "PREDICTED (model probability under ASSUMED scatter; aero sets ASSUMED, equal weight)",
             note: hcNote(sig) + "; best of " + C.length + " clean settings (two-stage search, common random numbers), reported on fresh draws",
             ms: now() - t0 };
  }

  // solve(q, onProgress, {part}): part "main" = the backspin grid only (twin left out unless it is the same grid),
  // "twin" = the no-spin twin only, undefined = both. A page can run the two parts in parallel workers and set
  // main.twin = the twin part. S = 0 with no Cl(S) table: the twin is the same flight, so its grid is reused.
  function solve(q, onProgress, sopt) {
    const t0 = now(), part = sopt && sopt.part;
    const ep = effParams(q);
    q = Object.assign({}, q, { params: ep.p });
    const ctx = context(q), LABELS = labelsFor(ctx);
    if (!ctx.ps.ok) {
      return { pose: ctx.ps, grid: null, count: 0, minRpm: null, minAngle: null, mostForgiving: null,
               twin: null, ms: now() - t0, labels: LABELS, section: null, sideWalls: ctx.sideWalls, part: part };
    }
    const S = q.S || 0, tp = twinParams(q.params);
    const same = S === 0 && !(q.params.cl_table && q.params.cl_table.length);
    function finishTwin(t) {
      t.labels = LABELS; t.pose = ctx.ps; t.isTwin = true; t.sideWalls = ctx.sideWalls;
      return t;
    }
    if (part === "twin") {
      const t = finishTwin(solveOne(q, 0, tp, ctx, onProgress, 0, 1));
      flagGrip(t, q);
      if (ctx.F) t.moveSens = moveSens(q, 0, tp, ctx, t.minRpmTol || t.minRpm);
      t.part = "twin"; t.ms = now() - t0;
      return t;
    }
    const both = !part && !same;
    const main = solveOne(q, S, q.params, ctx, onProgress, 0, both ? 0.5 : 1);
    let twin = null;
    if (both) twin = finishTwin(solveOne(q, 0, tp, ctx, onProgress, 0.5, 1.0));
    const notes = ctx.ps.notes.slice();
    notes.push(modelNote(ctx));
    optionNotes(q, ep).forEach(function (t) { notes.push(t); });
    flagGrip(main, q);
    if (twin) flagGrip(twin, q);
    if (ctx.F) {
      if (ctx.forced3D) notes.push("3D cell used although the section model is selected: the moving-robot / sideways-draft path is 3D");
      main.moveSens = moveSens(q, S, q.params, ctx, main.minRpmTol || main.minRpm);
      if (twin) twin.moveSens = moveSens(q, 0, tp, ctx, twin.minRpmTol || twin.minRpm);
    }
    // S = 0: the twin IS the main flight (no spin, so no lift or spin drag): same grid and answers, twin params
    if (same) twin = finishTwin(Object.assign({}, main, { params: tp, sameAsMain: true }));
    const gm = gridMeta(q.meta);
    if (q.h < gm.h[0] - 1e-9 || q.h > gm.h[gm.h.length - 1] + 1e-9)
      notes.push("release height " + q.h.toFixed(3) + " m is outside the exported 0.20..0.737 m (ASSUMED robot limit); live model still runs");
    if (onProgress) onProgress(1);
    return Object.assign(main, { pose: ctx.ps, twin: twin, twinPending: !twin, part: part, ms: now() - t0, labels: LABELS, notes: notes,
      section: ctx.sideWalls
        ? { key: ctx.sec.key, how: "3D cell built from the s = 0 section (" + ctx.sec.key + ")", sEff: null, model: "3d",
            ridge: ctx.c3.cell.ridge, wallT: ctx.c3.cell.wallT }
        : { key: ctx.sec.key, how: ctx.sec.how, sEff: ctx.sec.s, model: "section", roofDrop: ctx.sec.roofDrop || 0 },
      h: q.h, sideWalls: ctx.sideWalls, air: ep.air,
      move: ctx.F ? { lead: ctx.F.lead, d0: ctx.F.d0, vRobot: [ctx.F.sg * ctx.F.vrx, ctx.F.sg * ctx.F.vry], rExit: ctx.F.rExit } : null });
  }

  // side-wall verdict for one classified shot (research/GEOMETRY_AUDIT.md fix 6). 3D cell on: decided per shot
  // by the cell (hit on a *_side_wall* face, lateral offset s at entry vs the 0.2185 m ball-centre limit).
  // Section model: only the straight-line estimate from psi (near-side estimate; far side not checked).
  function sideWallInfo(ctx, cls) {
    if (ctx.c3) {
      const hit = !!(cls.hit && /side_wall/.test(cls.hit));
      return { model: "3d", hit: hit, sEntry: cls.s, limit: SIDE_WALL_S,
               text: hit ? "hits a cell side wall (3D cell, this shot)"
                 : "side walls checked by the 3D cell for this shot" + (cls.s !== null && cls.s !== undefined
                   ? ": lateral offset at entry " + Math.abs(cls.s).toFixed(3) + " m (ball-centre limit " + SIDE_WALL_S.toFixed(4) + " m)" : "") };
    }
    return { model: "section", hit: null, risk: ctx.ps.sideWallRisk, limit: SIDE_WALL_S,
             text: ctx.ps.sideWallRisk ? "straight-line side-wall estimate flags this bearing (near-side estimate; far side not checked)"
               : "side walls not modelled (section model)" };
  }

  // one shot plus its twin, mapped to field coordinates for drawing
  function shot(q, v, theta) {
    q = Object.assign({}, q, { params: effParams(q).p });
    const ctx = context(q), ps = ctx.ps, LABELS = labelsFor(ctx);
    const ux = Math.cos(rad(ps.bearingDeg)), uy = Math.sin(rad(ps.bearingDeg));
    function one3(S, p) {
      const zs = Math.min(ctx.zStop, -q.h), F = ctx.F, sg = F.sg;
      const path = path3D(F, v, theta, S, p, q.h, zs);
      if (!path) return { path: { x: new Float64Array([q.x]), y: new Float64Array([q.y]), z: new Float64Array([q.h]), n: 1, dt: 2e-3 },
                          cls: { result: "miss", hit: null, minClear: -Infinity, s: null, entryAngle: null, noLead: true }, S: S, lead: NaN };
      const cls = P.classifyPath3D(path, ctx.c3.cell, p.radius);
      const n = path.n, fx = new Float64Array(n), fy = new Float64Array(n), fz = new Float64Array(n);
      for (let i = 0; i < n; i++) { fx[i] = sg * path.X[i]; fy[i] = sg * path.Y[i]; fz[i] = path.Z[i]; }
      // the frame origin sits at the HIVE axis: shift so the release point is the robot point exactly
      const ox = q.x - fx[0], oy = q.y - fy[0];
      for (let i = 0; i < n; i++) { fx[i] += ox; fy[i] += oy; }
      return { path: { x: fx, y: fy, z: fz, n: n, dt: path.dt }, cls: cls, S: S, lead: path.launch.lead };
    }
    function one(S, p) {
      if (ctx.F) return one3(S, p);
      const zs = Math.min(ctx.zStop, -q.h);   // draw to the floor; classification unaffected below the cell
      const path = P.integrateOblique(v, theta, ps.psi, S, p, 2e-3, 3.0, zs);
      const cls = classifyCtx(ctx, path, q.h, p.radius);
      const n = path.n, fx = new Float64Array(n), fy = new Float64Array(n), fz = new Float64Array(n);
      const c = Math.cos(rad(ps.psi)), sn = Math.sin(rad(ps.psi));
      for (let i = 0; i < n; i++) {
        const s = path.X[i] * c + path.Y[i] * sn;        // along-bearing ground range
        fx[i] = q.x + s * ux; fy[i] = q.y + s * uy; fz[i] = q.h + path.Z[i];
      }
      return { path: { x: fx, y: fy, z: fz, n: n, dt: path.dt }, cls: cls, S: S };
    }
    const main = one(q.S || 0, q.params), twin = one(0, twinParams(q.params));
    main.sideWall = sideWallInfo(ctx, main.cls); twin.sideWall = sideWallInfo(ctx, twin.cls);
    return { path: main.path, cls: main.cls, twin: twin, pose: ps, section: ctx.sec.key, sideWalls: ctx.sideWalls,
             sideWall: main.sideWall, rpm: rpm(v, q.vu), ballSpinRpm: ballSpinRpm(v, q.S || 0), labels: LABELS,
             moving: !!ctx.F, lead: main.lead };
  }

  const api = { pose: pose, sectionFor: sectionFor, solve: solve, shot: shot, rpm: rpm, vFromRpm: vFromRpm,
    footprint: footprint, footprintAt: footprintAt, footprintText: footprintText, sightBlocked: sightBlocked,
    roofClearSection: roofClearSection, roofClearDrop: roofClearDrop,
    ballSpinRpm: ballSpinRpm, droopReadout: droopReadout, DROOP: DROOP, labels: LABELS, tol: TOL,
    _fastShot: fastShot, _prepSection: prepSection, _zStopFor: zStopFor, _context: context,
    _classifyCtx: classifyCtx, _cellFor: cellFor, effParams: effParams, _flagGrip: flagGrip,
    hitChance: hitChance, bestChance: bestChance, BC: BC, _bcCandidates: bcCandidates, HC_SIG: HC_SIG, HC_NOTE: HC_NOTE, _moveFor: moveFor, _frameFor: frameFor, _launch3: launch3,
    _fastShot3D: fastShot3D, _path3D: path3D, _params3: params3, _moveSens: moveSens, twinParams: twinParams,
    // one fused shot under a context (either model)
    _shotCtx: function (ctx, v, th, S, p, h, out) {
      return fastShot(v, th, ctx.cps, S, p, ctx.pr, ctx.ps.d, h, ctx.zStop, out, 2e-3, 3.0, ctx.c3);
    },
    constants: { X_WALL: X_WALL, Y_LO: Y_LO, Y_HI: Y_HI, BASE_X: BASE_X, BASE_Y: BASE_Y, X_GATE: X_GATE,
                 BASE_HX: BASE_HX, BASE_HY: BASE_HY, BASE_CY: BASE_CY, HIVE_HALF: HIVE_HALF,
                 OTHER_HIVE_X: OTHER_HIVE_X, OTHER_HIVE_Y: OTHER_HIVE_Y, ROBOT_L: ROBOT_L, ROBOT_W: ROBOT_W,
                 ROBOT_L_EXPANDED: ROBOT_L_EXPANDED, SIDE_WALL_S: SIDE_WALL_S,
                 WHEEL_D: WHEEL_D, R_BALL: R_BALL, Z_STOP_REL: Z_STOP_REL } };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.PollenSolver = api;
})(typeof self !== "undefined" ? self : this);
