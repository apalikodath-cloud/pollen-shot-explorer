// Shot physics for the 3D explorer: a line-for-line port of src/feasibility.py integrate_batch
// (fixed-step RK4, drag + capped Magnus + exponential spin decay, planar shot toward +x) and of
// src/hive.py Hive.classify_path (ball centre vs obstacles inflated by R; clean = enters the
// inside polygon before any contact). Checked against the Python model by test_physics.js.
(function (root) {
  "use strict";

  // ---- venue air and optional drag / draft terms (line-for-line copy of src/air.py; MISSING_EFFECTS.md
  // build-next 1, 2, 4). Params keys (same as Python): cd_model 'const' (default, params Cd ASSUMED) | 'morrison'
  // (smooth-sphere reference curve, Morrison 2013 with 263000 in both places; NOT POLLEN) | 'blend' (what-if partial
  // crisis cd_sub -> cd_post between re1 and re2, ASSUMED); dcd_spin (0 / 0.08 / 0.18 ASSUMED) with s_sat 0.6;
  // wind [along-shot, vertical] m/s (user, constant per shot); nu (m^2/s) for Re. Drag, Magnus and S use v_rel = v - w.
  const R_DRY = 287.06, P0 = 101325, S_SAT = 0.6, BLEND = { cd_post: 0.33, re1: 3.0e4, re2: 5.0e4 };
  function airState(tC, pPa, rh) {
    tC = tC === undefined ? 20 : tC; pPa = pPa === undefined ? P0 : pPa; rh = rh || 0;
    const T = tC + 273.15, e = rh * 611.2 * Math.exp(17.62 * tC / (243.12 + tC));
    const rho = (pPa - 0.378 * e) / (R_DRY * T);
    const mu = 1.716e-5 * Math.pow(T / 273.15, 1.5) * (273.15 + 110.4) / (T + 110.4);
    return { rho: rho, mu: mu, nu: mu / rho, t_c: tC, p_pa: pPa, rh: rh };
  }
  function pressureFromAltitude(h) { return P0 * Math.pow(1 - 2.25577e-5 * h, 5.25588); }
  function morrisonCd(re) {
    re = Math.max(re, 1e-6);
    const a = re / 5, b = re / 263000, c = re / 1e6;
    return 24 / re + 2.6 * a / (1 + Math.pow(a, 1.52)) + 0.411 * Math.pow(b, -7.94) / (1 + Math.pow(b, -8)) + 0.25 * c / (1 + c);
  }
  function smoothstep(x) { x = x < 0 ? 0 : x > 1 ? 1 : x; return x * x * (3 - 2 * x); }
  function cdBase(p, re) {
    const m = p.cd_model || "const";
    if (m === "const") return p.Cd;
    if (m === "morrison") return morrisonCd(re);
    if (m === "blend") {
      const sub = p.cd_sub !== undefined ? p.cd_sub : p.Cd, post = p.cd_post !== undefined ? p.cd_post : BLEND.cd_post;
      const r1 = p.re1 !== undefined ? p.re1 : BLEND.re1, r2 = p.re2 !== undefined ? p.re2 : BLEND.re2;
      return sub + (post - sub) * smoothstep((re - r1) / (r2 - r1));
    }
    throw new Error("unknown cd_model " + m);
  }
  // ---- lift and mass options (MISSING_EFFECTS.md build-next: Cl table, reverse Magnus, effective mass; same keys and
  // arithmetic as src/air.py cl_of / eps_from_phi). cl_table [[S, Cl], ...] (user points, ASSUMED): linear between
  // points, from (0, 0) up to the first point when its S > 0, flat after the last point. cl_rev (0 = off; 0..0.1
  // ASSUMED, Kim et al. 2014 / Kray et al. 2012 smooth spheres, NOT POLLEN): when Re < re_rev (4.6e4) and S < s_rev
  // (0.5) Cl blends (smoothstep over the last 10 % of each bound) to -cl_rev min(S / 0.1, 1). eps_mass (0 = off):
  // added-mass factor, dv/dt = (F_aero / m + g) / (1 + eps), eps = (0.5 + phi) rho V / m, phi 0..1 ASSUMED.
  const REV = { re: 4.6e4, s: 0.5 };
  function clTable(T, S) {
    const n = T.length;
    if (S <= T[0][0]) return T[0][0] > 0 ? T[0][1] * Math.max(S, 0) / T[0][0] : T[0][1];
    for (let i = 1; i < n; i++) if (S <= T[i][0]) {
      const a = T[i - 1], b = T[i];
      return a[1] + (b[1] - a[1]) * (S - a[0]) / (b[0] - a[0]);
    }
    return T[n - 1][1];
  }
  function clOf(p, S, re) {
    let cl = p.cl_table && p.cl_table.length ? clTable(p.cl_table, S) : Math.min(p.c1 * S, p.clmax);
    const cr = +p.cl_rev || 0;
    if (cr !== 0) {
      const r0 = p.re_rev || REV.re, s0 = p.s_rev || REV.s;
      const b = smoothstep((r0 - re) / (0.1 * r0)) * smoothstep((s0 - S) / (0.1 * s0));
      if (b > 0) cl = (1 - b) * cl - b * cr * Math.min(S / 0.1, 1);
    }
    return cl;
  }
  // lift present at all / largest |Cl| it can reach (bounds for the solver's shortcuts)
  function liftOn(p) { return p.c1 > 0 || !!(p.cl_table && p.cl_table.length) || (+p.cl_rev || 0) !== 0; }
  function clMaxOf(p) {
    let m = p.cl_table && p.cl_table.length ? Math.max.apply(null, p.cl_table.map(function (r) { return Math.abs(r[1]); })) : (p.c1 > 0 ? p.clmax : 0);
    if (+p.cl_rev) m = Math.max(m, Math.abs(+p.cl_rev));
    return m;
  }
  // lift never turns negative (no reverse Magnus, no negative table point): the solver's x-exit shortcut needs it
  function liftNonNeg(p) { return !(+p.cl_rev) && !(p.cl_table && p.cl_table.some(function (r) { return r[1] < 0; })); }
  function epsFromPhi(phi, rho, mass, R) { return (0.5 + phi) * rho * (4 / 3) * Math.PI * R * R * R / mass; }
  function hasExt(p) {
    const w = p.wind || [0, 0];
    return (p.cd_model || "const") !== "const" || (+p.dcd_spin || 0) !== 0 || +w[0] !== 0 || +w[1] !== 0 ||
      !!(p.cl_table && p.cl_table.length) || (+p.cl_rev || 0) !== 0 || (+p.eps_mass || 0) !== 0;
  }
  // general acceleration (null when every optional term is off: callers then keep the plain arithmetic)
  function aeroExt(p, S0, v) {
    if (!hasExt(p)) return null;
    const R = p.radius, q = 0.5 * p.rho * Math.PI * R * R / p.mass, g = p.g || 9.80665;
    const w = p.wind || [0, 0], wx = +w[0], wz = +w[1], nu = p.nu || 1.5e-5;
    const dcd = +p.dcd_spin || 0, ssat = p.s_sat !== undefined ? p.s_sat : S_SAT;
    const w0 = S0 * v / R, sgn = Math.sign(w0), aw0 = Math.abs(w0), k = p.k || 0;
    const spin = S0 !== 0 && p.rho > 0, useM = liftOn(p) && spin, ie = 1 / (1 + (+p.eps_mass || 0));
    return { wind: wx !== 0 || wz !== 0, acc: function (t, vx, vz, out) {
      const ux = vx - wx, uz = vz - wz, sp = Math.sqrt(ux * ux + uz * uz), re = sp * (2 * R) / nu;
      let cde = cdBase(p, re), S = 0;
      if (spin) {
        S = aw0 * Math.exp(-k * t) * R / Math.sqrt(sp * sp + 1e-12);
        if (dcd !== 0) cde += dcd * Math.min(S / ssat, 1);
      }
      let ax = -q * cde * sp * ux, az = -q * cde * sp * uz - g;
      if (useM) { const f = q * clOf(p, S, re) * sp * sgn; ax -= f * uz; az += f * ux; }
      if (ie !== 1) { ax *= ie; az *= ie; }
      out[0] = ax; out[1] = az;
    } };
  }
  const HOOD_V_MAX = 8.9;   // PREDICTED grip-limited hood cap (docs/04_launcher.md); shots above it are flagged

  function integrate(v, thDeg, S0, p, dt, tMax, zStop) {
    dt = dt || 2e-3; tMax = tMax || 3.0; zStop = zStop === undefined ? -0.8 : zStop;
    const th = thDeg * Math.PI / 180, R = p.radius;
    const q = 0.5 * p.rho * Math.PI * R * R / p.mass, cd = p.Cd, g = p.g || 9.80665;
    const w0 = S0 * v / R, sgn = Math.sign(w0), aw0 = Math.abs(w0);
    const useM = p.c1 > 0 && S0 !== 0 && p.rho > 0;
    const k = p.k || 0;
    const ext = aeroExt(p, S0, v);
    const acc = ext ? ext.acc : function (t, vx, vz, out) {
      const sp = Math.sqrt(vx * vx + vz * vz);
      let ax = -q * cd * sp * vx, az = -q * cd * sp * vz - g;
      if (useM) {
        const w = aw0 * Math.exp(-k * t);
        const S = w * R / Math.sqrt(sp * sp + 1e-12);
        const Cl = Math.min(p.c1 * S, p.clmax);
        const f = q * Cl * sp * sgn;
        ax -= f * vz; az += f * vx;
      }
      out[0] = ax; out[1] = az;
    };
    const nT = Math.ceil(tMax / dt) + 1;
    const X = new Float64Array(nT), Z = new Float64Array(nT);
    const VX = new Float64Array(nT), VZ = new Float64Array(nT);
    let x = 0, z = 0, vx = v * Math.cos(th), vz = v * Math.sin(th), t = 0, last = nT - 1;
    VX[0] = vx; VZ[0] = vz;
    const a1 = [0, 0], a2 = [0, 0], a3 = [0, 0], a4 = [0, 0];
    for (let n = 1; n < nT; n++) {
      acc(t, vx, vz, a1);
      acc(t + dt / 2, vx + dt / 2 * a1[0], vz + dt / 2 * a1[1], a2);
      acc(t + dt / 2, vx + dt / 2 * a2[0], vz + dt / 2 * a2[1], a3);
      acc(t + dt, vx + dt * a3[0], vz + dt * a3[1], a4);
      x += dt * (vx + dt / 6 * (a1[0] + a2[0] + a3[0]));
      z += dt * (vz + dt / 6 * (a1[1] + a2[1] + a3[1]));
      vx += dt / 6 * (a1[0] + 2 * a2[0] + 2 * a3[0] + a4[0]);
      vz += dt / 6 * (a1[1] + 2 * a2[1] + 2 * a3[1] + a4[1]);
      t += dt;
      X[n] = x; Z[n] = z; VX[n] = vx; VZ[n] = vz;
      if (z < zStop && vz < 0) { last = n; break; }
    }
    return { X: X.subarray(0, last + 1), Z: Z.subarray(0, last + 1), VX: VX.subarray(0, last + 1),
             VZ: VZ.subarray(0, last + 1), dt: dt, n: last + 1, w0: w0, k: k };
  }

  function segPoint(px, pz, ax, az, bx, bz) {
    const abx = bx - ax, abz = bz - az, den = abx * abx + abz * abz;
    let t = den > 0 ? ((px - ax) * abx + (pz - az) * abz) / den : 0;
    t = t < 0 ? 0 : t > 1 ? 1 : t;
    const dx = px - (ax + t * abx), dz = pz - (az + t * abz);
    return Math.sqrt(dx * dx + dz * dz);
  }

  function segSeg(p0x, p0z, p1x, p1z, q0x, q0z, q1x, q1z) {
    const rx = p1x - p0x, rz = p1z - p0z, sx = q1x - q0x, sz = q1z - q0z;
    const den = rx * sz - rz * sx;
    if (Math.abs(den) > 1e-15) {
      const qpx = q0x - p0x, qpz = q0z - p0z;
      const t = (qpx * sz - qpz * sx) / den, u = (qpx * rz - qpz * rx) / den;
      if (t >= 0 && t <= 1 && u >= 0 && u <= 1) return 0;
    }
    return Math.min(segPoint(p0x, p0z, q0x, q0z, q1x, q1z), segPoint(p1x, p1z, q0x, q0z, q1x, q1z),
                    segPoint(q0x, q0z, p0x, p0z, p1x, p1z), segPoint(q1x, q1z, p0x, p0z, p1x, p1z));
  }

  function insideConvex(px, pz, poly) {
    let pos = true, neg = true;
    for (let i = 0; i < poly.length; i++) {
      const a = poly[i], b = poly[(i + 1) % poly.length];
      const c = (b[0] - a[0]) * (pz - a[1]) - (b[1] - a[1]) * (px - a[0]);
      if (c < -1e-12) pos = false;
      if (c > 1e-12) neg = false;
    }
    return pos || neg;
  }

  // path: result of integrate(); release at (-d, h) in the shot frame. Mirrors classify_path.
  function classify(path, geom, d, h, R) {
    const n = path.n, P0 = geom.P0, P1 = geom.P1, ns = P0.length;
    let lo = 0;
    // skip the part of the flight far from the HIVE (cheap bounding box; same result)
    let bx0 = Infinity, bx1 = -Infinity, bz0 = Infinity, bz1 = -Infinity;
    for (let j = 0; j < ns; j++) {
      bx0 = Math.min(bx0, P0[j][0], P1[j][0]); bx1 = Math.max(bx1, P0[j][0], P1[j][0]);
      bz0 = Math.min(bz0, P0[j][1], P1[j][1]); bz1 = Math.max(bz1, P0[j][1], P1[j][1]);
    }
    for (const q of geom.inside) {
      bx0 = Math.min(bx0, q[0]); bx1 = Math.max(bx1, q[0]); bz0 = Math.min(bz0, q[1]); bz1 = Math.max(bz1, q[1]);
    }
    const m = R + 0.2;
    let minC = Infinity, minAt = -1;
    for (let i = 0; i < n - 1; i++) {
      const ax = path.X[i] - d, az = path.Z[i] + h, bx = path.X[i + 1] - d, bz = path.Z[i + 1] + h;
      if (Math.max(ax, bx) < bx0 - m || Math.min(ax, bx) > bx1 + m ||
          Math.max(az, bz) < bz0 - m || Math.min(az, bz) > bz1 + m) continue;
      if (i > 0 && insideConvex(ax, az, geom.inside)) {
        const vx = path.X[i] - path.X[i - 1], vz = path.Z[i] - path.Z[i - 1];
        return { result: "clean", i: i, hit: null, minClear: minC,
                 entryAngle: Math.atan2(-vz, Math.abs(vx) + 1e-300) * 180 / Math.PI };
      }
      let best = Infinity, bj = -1;
      for (let j = 0; j < ns; j++) {
        const dd = segSeg(ax, az, bx, bz, P0[j][0], P0[j][1], P1[j][0], P1[j][1]);
        if (dd < best) { best = dd; bj = j; }
      }
      if (best - R < minC) { minC = best - R; minAt = i; }
      if (best - R < 0) return { result: "hit", i: i, hit: geom.names[bj], minClear: minC, entryAngle: null };
    }
    const lastIn = insideConvex(path.X[n - 1] - d, path.Z[n - 1] + h, geom.inside);
    if (lastIn) return { result: "clean", i: n - 1, hit: null, minClear: minC, entryAngle: null };
    return { result: "miss", i: n - 1, hit: null, minClear: minC, entryAngle: null };
  }


  // ---- oblique (whole-field) shots: same model as src/robustness.py "score from anywhere" ----
  // Planar flight in the vertical plane of bearing psi (spin axis perpendicular to that plane, no
  // sideways Magnus), projected on the HIVE shot axis: X and VX are scaled by cos(psi); the
  // lateral coordinate is Y = s sin(psi) (s = along-bearing ground range). The pentagon roof drop
  // is carried by the section geometry at offset sEff(psi); cell side walls are NOT modelled here (section
  // model). The 3D cell model (buildCell3D / classifyOblique3D below, PM-013) models them.
  function sEff(psiDeg) { return Math.min(0.3 * Math.tan(Math.abs(psiDeg) * Math.PI / 180), 0.2); }

  // returns the shape classify() expects (X, Z, n) plus Y, VX, VY, VZ; psi sign = side of the aim line
  function integrateOblique(v, thDeg, psiDeg, S0, p, dt, tMax, zStop) {
    const base = integrate(v, thDeg, S0, p, dt, tMax, zStop);
    const ps = psiDeg * Math.PI / 180, c = Math.cos(ps), sn = Math.sin(ps), n = base.n;
    const X = new Float64Array(n), Y = new Float64Array(n), VX = new Float64Array(n), VY = new Float64Array(n);
    for (let i = 0; i < n; i++) {
      X[i] = base.X[i] * c; Y[i] = base.X[i] * sn; VX[i] = base.VX[i] * c; VY[i] = base.VX[i] * sn;
    }
    return { X: X, Y: Y, Z: base.Z, VX: VX, VY: VY, VZ: base.VZ, dt: base.dt, n: n, w0: base.w0,
             k: base.k, psi: psiDeg };
  }

  // geom = the section for sEff(|psi|) (index.json "sections"); same exact classifier as classify()
  function classifyOblique(path, geom, d, h, R) { return classify(path, geom, d, h, R); }

  // ---- 3D cell (PM-013): exact ball-centre path vs the cell side walls, pentagon roof and lips ----
  // Frame: shot frame x (shot axis), z (height) as the sections, plus y = s = lateral offset from the
  // cell centre plane. The ball flies in the vertical plane of bearing psi through the aim point
  // (shot-frame x = aimX, s = 0), so s = (aimX - x) tan(psi): a straight line in the plan view.
  // Every obstacle is a convex planar polygon in 3D; distance(segment, polygon) is exact (0 if the
  // segment crosses it, else the closest of: endpoint projections inside it and the 3D segment-segment
  // distances to its edges), so edges and corners are inflated by R like faces. Section segments are
  // extruded along s: up/down cell parts over |s| <= half + wallT, every other part (pivot plates,
  // A-frame) without lateral bound (as in the section model). With ridge = true (real pentagon, default)
  // roof outer, upper lip, roof inner and the back-wall top drop by slope*|s| along the cell w axis
  // (hive.py _roof_drop, linear in |s|); side walls (inner face at s = +-half, outer face, front rim) are
  // added after the section obstacles. Clean = the ball centre enters the 3D inside region (section inside
  // polygon at s = 0, |s| <= half - R, below the roof planes offset by R along their normal) before any
  // contact. With ridge = false (flat roof at the s = 0 section height) a psi = 0 shot gives exactly
  // classifyOblique() on the s = 0 section (tested). half (0.254, manual 20 in opening) and slope (from the
  // opening profile 14 in -> 7.61 in at the walls) are CONFIRMED/derived; wallT 0.0508 (2 in) is ASSUMED.
  const ROOF_SLOPE = (0.3556 - 0.19329) / 0.254, CELL_HALF = 0.254, WALL_T = 0.0508;
  const ROOF_PARTS = { roof_outer: 1, upper_lip: 1, roof_inner: 1, back_wall: 1 };

  // exact distance between 3D segments p0-p1 and q0-q1 (Ericson, Real-Time Collision Detection 5.1.9)
  function segSeg3(p0x, p0y, p0z, p1x, p1y, p1z, q0x, q0y, q0z, q1x, q1y, q1z) {
    const d1x = p1x - p0x, d1y = p1y - p0y, d1z = p1z - p0z, d2x = q1x - q0x, d2y = q1y - q0y, d2z = q1z - q0z;
    const rx = p0x - q0x, ry = p0y - q0y, rz = p0z - q0z;
    const a = d1x * d1x + d1y * d1y + d1z * d1z, e = d2x * d2x + d2y * d2y + d2z * d2z;
    const f = d2x * rx + d2y * ry + d2z * rz, EPS = 1e-300;
    let s, t;
    if (a <= EPS && e <= EPS) { s = 0; t = 0; }
    else if (a <= EPS) { s = 0; t = f / e; t = t < 0 ? 0 : t > 1 ? 1 : t; }
    else {
      const c = d1x * rx + d1y * ry + d1z * rz;
      if (e <= EPS) { t = 0; s = -c / a; s = s < 0 ? 0 : s > 1 ? 1 : s; }
      else {
        const b = d1x * d2x + d1y * d2y + d1z * d2z, den = a * e - b * b;
        if (den > 0) { s = (b * f - c * e) / den; s = s < 0 ? 0 : s > 1 ? 1 : s; } else s = 0;
        t = (b * s + f) / e;
        if (t < 0) { t = 0; s = -c / a; s = s < 0 ? 0 : s > 1 ? 1 : s; }
        else if (t > 1) { t = 1; s = (b - c) / a; s = s < 0 ? 0 : s > 1 ? 1 : s; }
      }
    }
    const dx = rx + d1x * s - d2x * t, dy = ry + d1y * s - d2y * t, dz = rz + d1z * s - d2z * t;
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  }

  // convex planar polygon; V = [[x, y, z], ...] in order; ext = {ax, az, bx, bz, s0, s1} marks a section
  // segment (x, z) extruded over s in [s0, s1] (fast path: exact 2D distance when the path step stays in it)
  function makeFace(name, V, ext) {
    const f = { name: name, ext: ext || null, V: null, nv: 0, nx: 0, ny: 0, nz: 0, c: 0, M: null, EB: null,
                eax: 0, eaz: 0, ebx: 0, ebz: 0, es0: 0, es1: 0,
                bb: [Infinity, -Infinity, Infinity, -Infinity, Infinity, -Infinity] };
    if (ext) {
      f.bb = [Math.min(ext.ax, ext.bx), Math.max(ext.ax, ext.bx), ext.s0, ext.s1,
              Math.min(ext.az, ext.bz), Math.max(ext.az, ext.bz)];
      if (isFinite(ext.s0) && isFinite(ext.s1))
        V = [[ext.ax, ext.s0, ext.az], [ext.bx, ext.s0, ext.bz], [ext.bx, ext.s1, ext.bz], [ext.ax, ext.s1, ext.az]];
    }
    if (V) {
      const n = V.length, A = new Float64Array(3 * n);
      let nx = 0, ny = 0, nz = 0;
      for (let i = 0; i < n; i++) {
        const p = V[i], q = V[(i + 1) % n];
        A[3 * i] = p[0]; A[3 * i + 1] = p[1]; A[3 * i + 2] = p[2];
        nx += (p[1] - q[1]) * (p[2] + q[2]); ny += (p[2] - q[2]) * (p[0] + q[0]); nz += (p[0] - q[0]) * (p[1] + q[1]);
        if (!ext) {
          f.bb[0] = Math.min(f.bb[0], p[0]); f.bb[1] = Math.max(f.bb[1], p[0]); f.bb[2] = Math.min(f.bb[2], p[1]);
          f.bb[3] = Math.max(f.bb[3], p[1]); f.bb[4] = Math.min(f.bb[4], p[2]); f.bb[5] = Math.max(f.bb[5], p[2]);
        }
      }
      const L = Math.sqrt(nx * nx + ny * ny + nz * nz);
      f.V = A; f.nv = n; f.nx = nx / L; f.ny = ny / L; f.nz = nz / L;
      f.c = f.nx * A[0] + f.ny * A[1] + f.nz * A[2];
      // per edge: in-plane inward normal m = n x e (|e| scale) with offset m.V_i, and the edge bounding box
      const M = new Float64Array(4 * n), EB = new Float64Array(6 * n);
      for (let i = 0; i < n; i++) {
        const j = i + 1 < n ? i + 1 : 0;
        const ex = A[3 * j] - A[3 * i], ey = A[3 * j + 1] - A[3 * i + 1], ez = A[3 * j + 2] - A[3 * i + 2];
        const mx = f.ny * ez - f.nz * ey, my = f.nz * ex - f.nx * ez, mz = f.nx * ey - f.ny * ex;
        M[4 * i] = mx; M[4 * i + 1] = my; M[4 * i + 2] = mz; M[4 * i + 3] = mx * A[3 * i] + my * A[3 * i + 1] + mz * A[3 * i + 2];
        for (let q = 0; q < 3; q++) {
          const u = A[3 * i + q], w = A[3 * j + q];
          EB[6 * i + 2 * q] = u < w ? u : w; EB[6 * i + 2 * q + 1] = u < w ? w : u;
        }
      }
      f.M = M; f.EB = EB;
    }
    if (ext) { f.eax = ext.ax; f.eaz = ext.az; f.ebx = ext.bx; f.ebz = ext.bz; f.es0 = ext.s0; f.es1 = ext.s1; }
    return f;
  }

  // point (in the face plane) inside the convex polygon (vertices counter-clockwise about the normal;
  // per edge (n x e).(p - V_i) >= -1e-12)
  function inFace(f, x, y, z) {
    const M = f.M, n = f.nv;
    for (let i = 0; i < n; i++) {
      if (M[4 * i] * x + M[4 * i + 1] * y + M[4 * i + 2] * z - M[4 * i + 3] < -1e-12) return false;
    }
    return true;
  }

  // exact distance from the segment a-b (x, y = s, z) to face f. With a bound L (optional) the result is
  // exact when the distance is below L, otherwise a lower bound >= L (2D projection, plane distance, or
  // the smallest box gap of the skipped edges).
  function segFace(f, ax, ay, az, bx, by, bz, L) {
    if (f.ext) {
      const d2 = segSeg(ax, az, bx, bz, f.eax, f.eaz, f.ebx, f.ebz);   // exact inside the extrusion, else a lower bound
      if (((ay < by ? ay : by) >= f.es0 && (ay < by ? by : ay) <= f.es1) || (L !== undefined && d2 >= L)) return d2;
    }
    const nx = f.nx, ny = f.ny, nz = f.nz;
    const da = nx * ax + ny * ay + nz * az - f.c, db = nx * bx + ny * by + nz * bz - f.c;
    if (L !== undefined && ((da > 0 && db > 0) || (da < 0 && db < 0))) {
      const m = da > 0 ? (da < db ? da : db) : (da > db ? -da : -db);
      if (m >= L) return m;
    }
    if ((da <= 0 && db >= 0) || (da >= 0 && db <= 0)) {
      if (da !== db) {
        const t = da / (da - db);
        if (inFace(f, ax + t * (bx - ax), ay + t * (by - ay), az + t * (bz - az))) return 0;
      } else if (inFace(f, ax, ay, az) || inFace(f, bx, by, bz)) return 0;   // in-plane segment
    }
    let best = Infinity;
    const inA = inFace(f, ax - da * nx, ay - da * ny, az - da * nz), inB = inFace(f, bx - db * nx, by - db * ny, bz - db * nz);
    if (inA) best = Math.abs(da);
    if (inB) best = Math.min(best, Math.abs(db));
    // both ends project inside, no plane crossing: the whole step projects inside (convex), so the
    // distance is the smaller end-to-plane distance (exact)
    if (inA && inB && ((da > 0 && db > 0) || (da < 0 && db < 0))) return best;
    const A = f.V, EB = f.EB, n = f.nv;
    let gap2 = Infinity;
    const sx0 = ax < bx ? ax : bx, sx1 = ax < bx ? bx : ax, sy0 = ay < by ? ay : by, sy1 = ay < by ? by : ay;
    const sz0 = az < bz ? az : bz, sz1 = az < bz ? bz : az;
    for (let i = 0; i < n; i++) {
      const j = i + 1 < n ? i + 1 : 0, o = 6 * i;
      // edge bounding-box gap: a lower bound; skip edges that cannot beat the current best or L
      const B = best < L ? best : (L === undefined ? best : L);
      if (B < Infinity) {
        const gx = EB[o] > sx1 ? EB[o] - sx1 : (sx0 > EB[o + 1] ? sx0 - EB[o + 1] : 0);
        const gy = EB[o + 2] > sy1 ? EB[o + 2] - sy1 : (sy0 > EB[o + 3] ? sy0 - EB[o + 3] : 0);
        const gz = EB[o + 4] > sz1 ? EB[o + 4] - sz1 : (sz0 > EB[o + 5] ? sz0 - EB[o + 5] : 0);
        const g2 = gx * gx + gy * gy + gz * gz;
        if (g2 >= B * B && gx + gy + gz > 0) { if (g2 < gap2) gap2 = g2; continue; }
      }
      const dd = segSeg3(ax, ay, az, bx, by, bz, A[3 * i], A[3 * i + 1], A[3 * i + 2], A[3 * j], A[3 * j + 1], A[3 * j + 2]);
      if (dd < best) best = dd;
    }
    // skipped edges are at least sqrt(gap2) >= L away: min(best, that) is exact below L and a lower bound
    if (gap2 < Infinity) { const g = Math.sqrt(gap2); if (g < best) return g; }
    return best;
  }

  // sec = the s = 0 section of that side (index.json "sections", key "<side>_s0")
  function buildCell3D(sec, opts) {
    opts = opts || {};
    const ridge = opts.ridge !== false, half = opts.half || CELL_HALF;
    const wallT = opts.wallT !== undefined ? opts.wallT : WALL_T, slope = opts.slope || ROOF_SLOPE;
    const HT = half + wallT, k = ridge ? slope : 0, names = sec.names, P0 = sec.P0, P1 = sec.P1;
    const idx = {}; names.forEach(function (nm, j) { idx[nm] = j; });
    const wdir = {};
    for (const pre of ["up", "down"]) {
      const j = idx[pre + "_back_wall"];
      if (j === undefined) continue;
      const dx = P1[j][0] - P0[j][0], dz = P1[j][1] - P0[j][1], L = Math.sqrt(dx * dx + dz * dz);
      wdir[pre] = [dx / L, dz / L];   // cell w axis (floor -> roof) in the shot frame
    }
    const faces = [];
    const v3 = function (p, s, drop, W) { return [p[0] - drop * W[0], s, p[1] - drop * W[1]]; };
    for (let j = 0; j < names.length; j++) {
      const nm = names[j], a = P0[j], b = P1[j];
      const pre = nm.indexOf("up_") === 0 ? "up" : nm.indexOf("down_") === 0 ? "down" : null;
      const part = pre ? nm.slice(pre.length + 1) : null;
      if (!pre || !wdir[pre]) {
        faces.push(makeFace(nm, null, { ax: a[0], az: a[1], bx: b[0], bz: b[1], s0: -Infinity, s1: Infinity }));
      } else if (!ridge || !ROOF_PARTS[part]) {
        faces.push(makeFace(nm, null, { ax: a[0], az: a[1], bx: b[0], bz: b[1], s0: -HT, s1: HT }));
      } else {
        const W = wdir[pre], dr = k * HT;
        if (part === "back_wall") {      // P0 bottom, P1 top (meets the roof outer): pentagon
          faces.push(makeFace(nm, [v3(a, -HT, 0, W), v3(a, HT, 0, W), v3(b, HT, dr, W), v3(b, 0, 0, W), v3(b, -HT, dr, W)]));
        } else {
          faces.push(makeFace(nm, [v3(a, 0, 0, W), v3(b, 0, 0, W), v3(b, HT, dr, W), v3(a, HT, dr, W)]));
          faces.push(makeFace(nm, [v3(a, 0, 0, W), v3(b, 0, 0, W), v3(b, -HT, dr, W), v3(a, -HT, dr, W)]));
        }
      }
    }
    for (const pre of ["up", "down"]) {
      const jo = idx[pre + "_roof_outer"], ju = idx[pre + "_underside"];
      if (!wdir[pre] || jo === undefined || ju === undefined) continue;
      const W = wdir[pre], C1 = P0[jo], C2 = P1[jo], C3 = P0[ju];
      const C4 = [C3[0] + C1[0] - C2[0], C3[1] + C1[1] - C2[1]];
      for (const sg of [1, -1]) {
        const tag = sg > 0 ? "_pos" : "_neg", sH = sg * half, sT = sg * HT, dH = k * half, dT = k * HT;
        faces.push(makeFace(pre + "_side_wall" + tag, [v3(C4, sH, 0, W), v3(C3, sH, 0, W), v3(C2, sH, dH, W), v3(C1, sH, dH, W)]));
        faces.push(makeFace(pre + "_side_wall_rim" + tag, [v3(C3, sH, 0, W), v3(C3, sT, 0, W), v3(C2, sT, dT, W), v3(C2, sH, dH, W)]));
        faces.push(makeFace(pre + "_side_wall_outer" + tag, [v3(C4, sT, 0, W), v3(C3, sT, 0, W), v3(C2, sT, dT, W), v3(C1, sT, dT, W)]));
      }
    }
    // classify()'s skip box, computed exactly as there (section segments + inside polygon)
    let bx0 = Infinity, bx1 = -Infinity, bz0 = Infinity, bz1 = -Infinity;
    for (let j = 0; j < names.length; j++) {
      bx0 = Math.min(bx0, P0[j][0], P1[j][0]); bx1 = Math.max(bx1, P0[j][0], P1[j][0]);
      bz0 = Math.min(bz0, P0[j][1], P1[j][1]); bz1 = Math.max(bz1, P0[j][1], P1[j][1]);
    }
    for (const q of sec.inside) {
      bx0 = Math.min(bx0, q[0]); bx1 = Math.max(bx1, q[0]); bz0 = Math.min(bz0, q[1]); bz1 = Math.max(bz1, q[1]);
    }
    const ri = P0[idx.up_roof_inner], wu = wdir.up;
    const fbb = new Float64Array(6 * faces.length);
    faces.forEach(function (f, j) { for (let q = 0; q < 6; q++) fbb[6 * j + q] = f.bb[q]; });
    return { faces: faces, fbb: fbb, lb: new Float64Array(faces.length), ord: new Int32Array(faces.length), lbOff: 0, inside: sec.inside, half: half, wallT: wallT, slope: slope, ridge: ridge, k: k,
             kn: Math.sqrt(1 + k * k), w0x: ri[0], w0z: ri[1], wx: wu[0], wz: wu[1],
             bb: [bx0, bx1, bz0, bz1], gate: sec.gate, names: names };
  }

  // ball centre (x, s, z) in the 3D inside region (radius R)
  function inside3D(cell, x, y, z, R) {
    if (!insideConvex(x, z, cell.inside)) return false;
    const ay = y < 0 ? -y : y;
    if (ay > cell.half - R) return false;
    if (cell.k > 0 && (x - cell.w0x) * cell.wx + (z - cell.w0z) * cell.wz > -cell.k * ay - R * cell.kn) return false;
    return true;
  }

  // min distance from the step a-b to all faces, exact whenever it is below lim (lim = minClear + R: a
  // face at least lim away can neither lower minClear nor hit; lim = Infinity: always exact). Faces whose
  // bounding box or plane is at least min(lim, best so far) away are skipped (branch and bound).
  // hint (optional): face index tried first (the previous step's closest face; same exact minimum).
  // cont (optional): true when this step starts where the previous call's step ended. Each face then
  // keeps a lower bound from the earlier calls minus the path length since (every point of this step is
  // within this step's length of the previous step's end point); faces are visited in increasing bound
  // order and the scan stops at the first bound >= min(lim, best) (still exact). false/undefined resets.
  // The index of the closest face is left in faceHit.j (-1 when no face was below lim), a lower bound of
  // this step's distance to all faces in faceHit.lb (exact when below lim).
  const faceHit = { j: -1, lb: 0 };
  function faceLB(cell, j, ax, ay, az, bx, by, bz, sx0, sx1, sy0, sy1, sz0, sz1, L) {
    if (L < Infinity) {
      const fbb = cell.fbb, o = 6 * j;
      const gx = fbb[o] > sx1 ? fbb[o] - sx1 : (sx0 > fbb[o + 1] ? sx0 - fbb[o + 1] : 0);
      const gy = fbb[o + 2] > sy1 ? fbb[o + 2] - sy1 : (sy0 > fbb[o + 3] ? sy0 - fbb[o + 3] : 0);
      const gz = fbb[o + 4] > sz1 ? fbb[o + 4] - sz1 : (sz0 > fbb[o + 5] ? sz0 - fbb[o + 5] : 0);
      const g2 = gx * gx + gy * gy + gz * gz;
      if (g2 >= L * L && gx + gy + gz > 0) return -Math.sqrt(g2);    // negative = bound only (>= L)
    }
    return segFace(cell.faces[j], ax, ay, az, bx, by, bz, L);
  }
  function stepDist3D(cell, ax, ay, az, bx, by, bz, lim, hint, cont) {
    const nf = cell.faces.length, lb = cell.lb, ord = cell.ord;
    const sx0 = ax < bx ? ax : bx, sx1 = ax < bx ? bx : ax, sy0 = ay < by ? ay : by, sy1 = ay < by ? by : ay;
    const sz0 = az < bz ? az : bz, sz1 = az < bz ? bz : az;
    let best = Infinity, bj = -1;
    if (!cont) {
      const h0 = hint >= 0 && hint < nf ? hint : -1;
      for (let k = h0 >= 0 ? -1 : 0; k < nf; k++) {
        const j = k < 0 ? h0 : k;
        if (k >= 0 && k === h0) continue;
        const L = best < lim ? best : lim;
        let dd = faceLB(cell, j, ax, ay, az, bx, by, bz, sx0, sx1, sy0, sy1, sz0, sz1, L);
        if (dd < 0) dd = -dd;
        else if (dd < best) { best = dd; bj = j; }
        lb[j] = dd;
      }
      cell.lbOff = 0;
      for (let i = 0; i < nf; i++) ord[i] = i;
      for (let i = 1; i < nf; i++) {               // insertion sort by bound
        const e = ord[i], v = lb[e];
        let q = i - 1;
        while (q >= 0 && lb[ord[q]] > v) { ord[q + 1] = ord[q]; q--; }
        ord[q + 1] = e;
      }
      faceHit.j = bj; faceHit.lb = lb[ord[0]];
      return best;
    }
    // stored bounds are absolute: bound = lb[j] - off
    const off = cell.lbOff + Math.sqrt((bx - ax) * (bx - ax) + (by - ay) * (by - ay) + (bz - az) * (bz - az)) + 1e-12;
    cell.lbOff = off;
    let p = 0;
    for (; p < nf; p++) {
      const j = ord[p], lj = lb[j] - off, L = best < lim ? best : lim;
      if (lj >= L) break;
      let dd = faceLB(cell, j, ax, ay, az, bx, by, bz, sx0, sx1, sy0, sy1, sz0, sz1, L);
      if (dd < 0) dd = -dd;
      else if (dd < best) { best = dd; bj = j; }
      lb[j] = (dd > lj ? dd : lj) + off;
    }
    for (let i = p - 1; i >= 0; i--) {             // re-insert the visited faces (the rest stays sorted)
      const e = ord[i], v = lb[e];
      let q = i + 1;
      while (q < nf && lb[ord[q]] < v) { ord[q - 1] = ord[q]; q++; }
      ord[q - 1] = e;
    }
    faceHit.j = bj; faceHit.lb = lb[ord[0]] - off;
    return best;
  }

  // classifyOblique() in 3D. path = integrateOblique() result; aimX = shot-frame x of the aim point
  // (gate centre: Lh - d); psiDeg signed as in integrateOblique.
  function classifyOblique3D(path, cell, d, h, R, aimX, psiDeg) {
    const n = path.n, tp = Math.tan(psiDeg * Math.PI / 180), m = R + 0.2, bb = cell.bb;
    let minC = Infinity;
    for (let i = 0; i < n - 1; i++) {
      const ax = path.X[i] - d, az = path.Z[i] + h, bx = path.X[i + 1] - d, bz = path.Z[i + 1] + h;
      if (Math.max(ax, bx) < bb[0] - m || Math.min(ax, bx) > bb[1] + m ||
          Math.max(az, bz) < bb[2] - m || Math.min(az, bz) > bb[3] + m) continue;
      const ay = (aimX - ax) * tp, by = (aimX - bx) * tp;
      if (i > 0 && inside3D(cell, ax, ay, az, R)) {
        const vx = path.X[i] - path.X[i - 1], vz = path.Z[i] - path.Z[i - 1];
        return { result: "clean", i: i, hit: null, minClear: minC, s: ay,
                 entryAngle: Math.atan2(-vz, Math.abs(vx) + 1e-300) * 180 / Math.PI };
      }
      const best = stepDist3D(cell, ax, ay, az, bx, by, bz, Infinity), bj = faceHit.j;
      if (best - R < minC) minC = best - R;
      if (best - R < 0) return { result: "hit", i: i, hit: cell.faces[bj].name, minClear: minC, s: ay, entryAngle: null };
    }
    const lx = path.X[n - 1] - d, lz = path.Z[n - 1] + h;
    if (inside3D(cell, lx, (aimX - lx) * tp, lz, R)) return { result: "clean", i: n - 1, hit: null, minClear: minC, s: null, entryAngle: null };
    return { result: "miss", i: n - 1, hit: null, minClear: minC, s: null, entryAngle: null };
  }

  // ---- 3D flight (MISSING_EFFECTS.md build-next: shooting on the move, gyro spin ratio, sideways draft, hit chance).
  // Same physics as aeroExt in 3D (src/robustness.py integrate3d is the Python twin): v_rel = v - wind3 everywhere,
  // spin vector w(t) = w0 exp(-k t), Magnus q Cl |v_rel|^2 unit(w x v_rel), S = |w| R / |v_rel| (default) or, with
  // p.s_perp (gyro-correct, as src/flight.py), S_perp = |w x v_rel| R / |v_rel|^2 (equal for pure backspin).
  // p.wind3 = [x, y, z] m/s in the frame of the call. z up, gravity along -z.
  function makeAcc3(p, w0) {
    const R = p.radius, q = 0.5 * p.rho * Math.PI * R * R / p.mass, g = p.g || 9.80665, nu = p.nu || 1.5e-5;
    const w3 = p.wind3 || [0, 0, 0], wx0 = +w3[0] || 0, wy0 = +w3[1] || 0, wz0 = +w3[2] || 0;
    const dcd = +p.dcd_spin || 0, ssat = p.s_sat !== undefined ? p.s_sat : S_SAT, k = p.k || 0;
    const aw = Math.sqrt(w0[0] * w0[0] + w0[1] * w0[1] + w0[2] * w0[2]), spin = aw > 0 && p.rho > 0;
    const lift = spin && liftOn(p), sperp = !!p.s_perp, ie = 1 / (1 + (+p.eps_mass || 0));
    return function (t, vx, vy, vz, out) {
      const ux = vx - wx0, uy = vy - wy0, uz = vz - wz0, sp2 = ux * ux + uy * uy + uz * uz, sp = Math.sqrt(sp2);
      const re = sp * (2 * R) / nu;
      let cde = cdBase(p, re), S = 0, cx = 0, cy = 0, cz = 0;
      if (spin) {
        const dec = Math.exp(-k * t), ox = w0[0] * dec, oy = w0[1] * dec, oz = w0[2] * dec;
        cx = oy * uz - oz * uy; cy = oz * ux - ox * uz; cz = ox * uy - oy * ux;
        S = sperp ? Math.sqrt(cx * cx + cy * cy + cz * cz) * R / (sp2 + 1e-12) : aw * dec * R / Math.sqrt(sp2 + 1e-12);
        if (dcd !== 0) cde += dcd * Math.min(S / ssat, 1);
      }
      let ax = -q * cde * sp * ux, ay = -q * cde * sp * uy, az = -q * cde * sp * uz - g;
      if (lift) {
        const cm = Math.sqrt(cx * cx + cy * cy + cz * cz);
        if (cm > 0) { const f = q * clOf(p, S, re) * sp2 / cm; ax += f * cx; ay += f * cy; az += f * cz; }
      }
      if (ie !== 1) { ax *= ie; ay *= ie; az *= ie; }
      out[0] = ax; out[1] = ay; out[2] = az;
    };
  }
  // RK4 from x0 with velocity v0 and spin vector w0 (rad/s); stops below zStop (absolute z) while descending
  function integrate3D(x0, v0, w0, p, dt, tMax, zStop) {
    dt = dt || 2e-3; tMax = tMax || 3.0; zStop = zStop === undefined ? -1e9 : zStop;
    const acc = makeAcc3(p, w0), nT = Math.ceil(tMax / dt) + 1;
    const X = new Float64Array(nT), Y = new Float64Array(nT), Z = new Float64Array(nT);
    const VX = new Float64Array(nT), VY = new Float64Array(nT), VZ = new Float64Array(nT);
    let x = x0[0], y = x0[1], z = x0[2], vx = v0[0], vy = v0[1], vz = v0[2], t = 0, last = nT - 1;
    X[0] = x; Y[0] = y; Z[0] = z; VX[0] = vx; VY[0] = vy; VZ[0] = vz;
    const a1 = [0, 0, 0], a2 = [0, 0, 0], a3 = [0, 0, 0], a4 = [0, 0, 0], h = dt / 2;
    for (let n = 1; n < nT; n++) {
      acc(t, vx, vy, vz, a1);
      acc(t + h, vx + h * a1[0], vy + h * a1[1], vz + h * a1[2], a2);
      acc(t + h, vx + h * a2[0], vy + h * a2[1], vz + h * a2[2], a3);
      acc(t + dt, vx + dt * a3[0], vy + dt * a3[1], vz + dt * a3[2], a4);
      x += dt * (vx + dt / 6 * (a1[0] + a2[0] + a3[0]));
      y += dt * (vy + dt / 6 * (a1[1] + a2[1] + a3[1]));
      z += dt * (vz + dt / 6 * (a1[2] + a2[2] + a3[2]));
      vx += dt / 6 * (a1[0] + 2 * a2[0] + 2 * a3[0] + a4[0]);
      vy += dt / 6 * (a1[1] + 2 * a2[1] + 2 * a3[1] + a4[1]);
      vz += dt / 6 * (a1[2] + 2 * a2[2] + 2 * a3[2] + a4[2]);
      t += dt;
      X[n] = x; Y[n] = y; Z[n] = z; VX[n] = vx; VY[n] = vy; VZ[n] = vz;
      if (z < zStop && vz < 0) { last = n; break; }
    }
    const e = last + 1;
    return { X: X.subarray(0, e), Y: Y.subarray(0, e), Z: Z.subarray(0, e), VX: VX.subarray(0, e), VY: VY.subarray(0, e),
             VZ: VZ.subarray(0, e), n: e, dt: dt };
  }
  // classifyOblique3D on a path already in the cell frame (x, s, z absolute); src/cell3d.py classify_path3d
  function classifyPath3D(path, cell, R) {
    const n = path.n, m = R + 0.2, bb = cell.bb;
    let minC = Infinity;
    for (let i = 0; i < n - 1; i++) {
      const ax = path.X[i], ay = path.Y[i], az = path.Z[i], bx = path.X[i + 1], by = path.Y[i + 1], bz = path.Z[i + 1];
      if (Math.max(ax, bx) < bb[0] - m || Math.min(ax, bx) > bb[1] + m ||
          Math.max(az, bz) < bb[2] - m || Math.min(az, bz) > bb[3] + m) continue;
      if (i > 0 && inside3D(cell, ax, ay, az, R)) {
        const vx = path.X[i] - path.X[i - 1], vz = path.Z[i] - path.Z[i - 1];
        return { result: "clean", i: i, hit: null, minClear: minC, s: ay,
                 entryAngle: Math.atan2(-vz, Math.abs(vx) + 1e-300) * 180 / Math.PI };
      }
      const best = stepDist3D(cell, ax, ay, az, bx, by, bz, Infinity), bj = faceHit.j;
      if (best - R < minC) minC = best - R;
      if (best - R < 0) return { result: "hit", i: i, hit: cell.faces[bj].name, minClear: minC, s: ay, entryAngle: null };
    }
    if (inside3D(cell, path.X[n - 1], path.Y[n - 1], path.Z[n - 1], R)) return { result: "clean", i: n - 1, hit: null, minClear: minC, s: null, entryAngle: null };
    return { result: "miss", i: n - 1, hit: null, minClear: minC, s: null, entryAngle: null };
  }

  // seeded standard normals for the hit-chance Monte Carlo (mulberry32 + Box-Muller, both normals of each pair used;
  // src/robustness.py mulberry32_normals is the Python twin)
  function mulberry32(seed) {
    let a = seed >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function normals(seed, n) {
    const r = mulberry32(seed), out = new Float64Array(n);
    for (let i = 0; i < n; i += 2) {
      const u1 = 1 - r(), u2 = r(), m = Math.sqrt(-2 * Math.log(u1));
      out[i] = m * Math.cos(2 * Math.PI * u2);
      if (i + 1 < n) out[i + 1] = m * Math.sin(2 * Math.PI * u2);
    }
    return out;
  }
  // Wilson score interval (95 %), as src/robustness.py wilson
  function wilson(k, n, z) {
    z = z || 1.959964;
    if (!n) return [0, 1];
    const ph = k / n, den = 1 + z * z / n, c = (ph + z * z / (2 * n)) / den;
    const hw = z * Math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den;
    return [Math.max(0, c - hw), Math.min(1, c + hw)];
  }

  const api = { integrate: integrate, classify: classify, integrateOblique: integrateOblique,
    classifyOblique: classifyOblique, sEff: sEff, segSeg: segSeg, insideConvex: insideConvex,
    buildCell3D: buildCell3D, classifyOblique3D: classifyOblique3D, inside3D: inside3D, stepDist3D: stepDist3D, faceHit: faceHit,
    segSeg3: segSeg3, segFace: segFace, makeFace: makeFace,
    airState: airState, pressureFromAltitude: pressureFromAltitude, morrisonCd: morrisonCd, cdBase: cdBase,
    hasExt: hasExt, aeroExt: aeroExt, HOOD_V_MAX: HOOD_V_MAX,
    clOf: clOf, clMaxOf: clMaxOf, liftOn: liftOn, liftNonNeg: liftNonNeg, epsFromPhi: epsFromPhi, REV: REV,
    makeAcc3: makeAcc3, integrate3D: integrate3D, classifyPath3D: classifyPath3D, mulberry32: mulberry32, normals: normals, wilson: wilson,
    CELL3D: { ROOF_SLOPE: ROOF_SLOPE, CELL_HALF: CELL_HALF, WALL_T: WALL_T } };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.PollenPhysics = api;
})(typeof self !== "undefined" ? self : this);
