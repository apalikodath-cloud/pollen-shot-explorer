// Node checks for the PM-016 options (research/MISSING_EFFECTS.md build-next 2a-2f): shooting on the move
// (solver.js moveFor / frameFor / launch3 / fastShot3D / moveSens), the hit-chance Monte Carlo (hitChance),
// gyro-correct S, Cl table, reverse Magnus, effective mass and the 3D draft (physics.js makeAcc3 / integrate3D).
// Run: node tests/js_move_check.js            -> checks, JSON summary as the last line
//      node tests/js_move_check.js --dump     -> JSON for tests/test_move.py (launch states, 3D paths,
//                                                classifications, normals and hit-chance counts; python twin
//                                                = src/robustness.py launch_state / integrate3d / mc_shots)
// Exit 0 = pass, 1 = a check failed, 77 = field data missing (gitignored; viz/explorer/export_field.py).
"use strict";
const fs = require("fs"), path = require("path");
const EX = path.join(__dirname, "..", "viz", "explorer");
const FIELD = path.join(EX, "data", "field");
const P = require(path.join(EX, "physics.js"));
const Sv = require(path.join(EX, "solver.js"));

if (!fs.existsSync(path.join(FIELD, "index.json"))) { console.log("SKIP field data missing"); process.exit(77); }
const meta = JSON.parse(fs.readFileSync(path.join(FIELD, "index.json"), "utf8"));
const caseOf = function (S, v) { return meta.cases.find(function (c) { return c.S === S && c.var === (v || "nominal"); }); };
let seed = 20261031;
function rnd() { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; }
function pick(a) { return a[Math.floor(rnd() * a.length)]; }
function lh(side, d) { return side === "fav" ? Math.max(d - 0.401, 1e-3) : d + 0.401; }
function poseXY(side, d, psi) { return [side === "fav" ? d : -d, lh(side, d) * Math.tan(psi * Math.PI / 180)]; }
const OPTS = [
  {},
  { lift: { table: [[0, 0], [0.5, 0.2], [1.5, 0.35]] } },
  { lift: { rev: 0.1 } },
  { lift: { gyro: true } },
  { effMass: { phi: 0.5 } },
  { drag: { model: "morrison", spin: 0.08 } },
  { wind: { along: 0.3, up: -0.2 } },
  { lift: { table: [[0.4, 0.15], [1.2, 0.3]], rev: 0.05, gyro: true }, effMass: { phi: 1 }, wind: { along: -0.2, up: 0.1 } },
];
function randomPose(extra) {
  for (;;) {
    const side = rnd() < 0.5 ? "unfav" : "fav", S = pick([0, 0.5, 1.0, 1.5]);
    const d = 0.6 + rnd() * 1.1, psi = (rnd() < 0.5 ? -1 : 1) * rnd() * 50, h = 0.3 + rnd() * 0.437;
    const xy = poseXY(side, d, psi), c = caseOf(S);
    const q = Object.assign({ x: xy[0], y: xy[1], h: h, S: S, vu: 0.42, params: c.params, meta: meta }, extra || {});
    const ctx = Sv._context(q, true);
    if (ctx.ps.ok && ctx.F) return { q: q, ctx: ctx, side: side, S: S };
  }
}
function randomShot(side) {
  return side === "unfav" ? [5 + rnd() * 6, 60 + rnd() * 29.5] : [2.5 + rnd() * 7.5, 25 + rnd() * 64];
}
function randomMove() {
  const m = { along: (rnd() - 0.5) * 2, across: (rnd() - 0.5) * 1.2 };
  if (rnd() < 0.4) { m.vx = (rnd() - 0.5) * 0.6; m.vy = (rnd() - 0.5) * 0.6; }
  if (rnd() < 0.5) m.wz = (rnd() - 0.5) * 120;
  if (rnd() < 0.5) m.d0 = (rnd() - 0.5) * 4;
  if (rnd() < 0.3) m.lead = false;
  if (rnd() < 0.3) m.rExit = [0.1 + rnd() * 0.1, (rnd() - 0.5) * 0.2];
  return m;
}

if (process.argv[2] === "--dump") {
  const out = [0, 0, 0, 0], cases = [];
  while (cases.length < 10) {
    const opt = OPTS[cases.length % OPTS.length], extra = Object.assign({ move: randomMove() }, opt);
    if (rnd() < 0.5) extra.wind = Object.assign({}, opt.wind || {}, { side: (rnd() - 0.5) * 0.6 });
    const pz = randomPose(extra), q = pz.q, ctx = Sv._context(q), F = ctx.F, S = pz.S;
    const p = Sv.effParams(q).p, p3 = Sv._params3(p, F), cell = ctx.c3.cell;
    const cl = [], ot = [];
    for (let k = 0; k < 300 && cl.length < 3; k++) {
      const vt = randomShot(pz.side);
      (Sv._fastShot3D(F, vt[0], vt[1], S, p, ctx.pr, cell, q.h, ctx.zStop, out) === 1 ? cl : ot).push(vt);
    }
    if (!cl.length) continue;
    const shots = [];
    for (const vt of cl.concat(ot.slice(0, 3))) {
      const dpsi = (rnd() - 0.5) * 0.02;
      Sv._fastShot3D(F, vt[0], vt[1], S, p, ctx.pr, cell, q.h, ctx.zStop, out, dpsi);
      const code = out[2];
      const L = Sv._launch3(F, vt[0], vt[1], S, p.radius, dpsi, {});
      const pa = Sv._path3D(F, vt[0], vt[1], S, p, q.h, ctx.zStop, dpsi);
      const r = pa ? P.classifyPath3D(pa, cell, p.radius) : null;
      const idx = pa ? [1, 37, 150, 400, pa.n - 1].filter(function (i) { return i < pa.n; }) : [];
      shots.push({ v: vt[0], th: vt[1], dpsi: dpsi, code: code, launch: L, n: pa ? pa.n : 0,
                   pts: idx.map(function (i) { return [i, pa.X[i], pa.Y[i], pa.Z[i], pa.VX[i], pa.VY[i], pa.VZ[i]]; }),
                   cls: r ? { result: r.result, i: r.i, minClear: r.minClear } : null });
    }
    // hit chance at the first clean shot: every aero set of this S and the twin (at a nearby setting)
    const v = cl[0][0], th = cl[0][1], tw = { v: v * 0.995, theta: th + 0.3 };
    const hc = Sv.hitChance(q, v, th, { n: 160, seed: 7 + cases.length, twinAt: tw });
    const sets = {};
    for (const s of hc.sets) {
      const c = caseOf(S, s.name);
      sets[s.name] = Sv._params3(Sv.effParams(Object.assign({}, q, { params: c ? c.params : q.params })).p, F);
    }
    cases.push({ side: pz.side, ridge: true, wallT: P.CELL3D.WALL_T, h: q.h, zStop: ctx.zStop, S: S, R: p.radius,
                 F: F, p3: p3, shots: shots,
                 hc: { v: v, theta: th, seed: hc.seed, n: hc.n, sig: hc.sig, sets: hc.sets, twin: hc.twin, setParams: sets } });
  }
  process.stdout.write(JSON.stringify({ sections: { unfav: meta.sections.unfav_s0, fav: meta.sections.fav_s0 },
                                        normals: Array.from(P.normals(20261031, 31)), cases: cases }));
  process.exit(0);
}

const summary = {}; let failed = 0;
function check(name, ok, info) {
  console.log((ok ? "PASS " : "FAIL ") + name + (info ? "  " + info : ""));
  summary[name] = { ok: !!ok, info: info || "" };
  if (!ok) failed++;
}
const out = [0, 0, 0, 0], out2 = [0, 0, 0, 0];

// (1) robot at rest: the 3D path on the 3D cell gives the planar oblique answer (clean / not clean and the
// clearance), under every lift / mass / drag option and the along / up draft; gyro-correct S changes nothing
// for pure backspin
{
  let n = 0, bad = 0, badC = 0, maxdc = 0, clean = 0;
  for (let k = 0; k < 1600; k++) {
    const opt = OPTS[k % OPTS.length], pz = randomPose(opt), q = pz.q;
    const ctx0 = Sv._context(q), ctx3 = pz.ctx, p = Sv.effParams(q).p, vt = randomShot(pz.side);
    const a = Sv._shotCtx(ctx0, vt[0], vt[1], pz.S, p, q.h, out) === 1;
    const b = Sv._fastShot3D(ctx3.F, vt[0], vt[1], pz.S, p, ctx3.pr, ctx3.c3.cell, q.h, ctx3.zStop, out2) === 1;
    n++;
    if (a) clean++;
    if (a !== b) { if (Math.min(Math.abs(out[0]), Math.abs(out2[0])) > 1e-6) bad++; continue; }
    if (a) { const dc = Math.abs(out[0] - out2[0]); if (isFinite(dc)) maxdc = Math.max(maxdc, dc); if (dc > 1e-6) badC++; }
  }
  check("at rest: 3D path == planar model", bad === 0 && badC === 0 && clean > 30,
        n + " shots, " + clean + " clean, mismatches " + bad + ", clearance |d| max " + maxdc.toExponential(2));
}

// (2) fused fastShot3D == path3D + classifyPath3D for random moving robots, sideways drafts and every option
{
  let n = 0, bad = 0, clean = 0, inf = 0, badC = 0;
  for (let k = 0; k < 900; k++) {
    const extra = Object.assign({ move: randomMove() }, OPTS[k % OPTS.length]);
    if (k % 3 === 0) extra.wind = Object.assign({}, extra.wind || {}, { side: (rnd() - 0.5) * 0.8 });
    const pz = randomPose(extra), ctx = pz.ctx, q = pz.q, F = ctx.F, p = Sv.effParams(q).p, vt = randomShot(pz.side);
    const dpsi = (rnd() - 0.5) * 0.03;
    const code = Sv._fastShot3D(F, vt[0], vt[1], pz.S, p, ctx.pr, ctx.c3.cell, q.h, ctx.zStop, out, dpsi);
    const pa = Sv._path3D(F, vt[0], vt[1], pz.S, p, q.h, ctx.zStop, dpsi);
    n++;
    if (!pa) { inf++; if (out[2] !== 5) bad++; continue; }
    const r = P.classifyPath3D(pa, ctx.c3.cell, p.radius);
    const want = out[2] === 1 ? "clean" : out[2] === 2 ? "hit" : "miss";
    if (r.result !== want) bad++;
    if (r.result === "clean") { clean++; if (Math.abs(r.minClear - out[0]) > 1e-9 && isFinite(r.minClear)) badC++; }
  }
  check("moving: fused 3D shot == integrate3D + classifyPath3D", bad === 0 && badC === 0 && clean > 20,
        n + " shots, " + clean + " clean, " + inf + " beyond the lead, mismatches " + bad + " / clearance " + badC);
}

// (3) defaults unchanged: no move, an all-zero move and every new option at its off value give the same answer
const Q0 = { x: -1.0, y: 0.2, h: 0.737, S: 1.0, vu: 0.42, params: caseOf(1.0).params, meta: meta };
function key(r) {
  const f = function (x) { return x ? Math.round(x.rpm) + "@" + x.theta.toFixed(2) : "-"; };
  return r.count + " " + f(r.minRpm) + " " + f(r.minRpmTol) + " " + f(r.mostForgiving) + " | " +
         r.twin.count + " " + f(r.twin.minRpmTol);
}
const base = Sv.solve(Q0), k0 = key(base);
{
  const offs = [{ move: undefined }, { lift: { table: [], rev: 0, gyro: false } }, { effMass: null },
                { wind: { along: 0, up: 0, side: 0 } }];
  let same = true;
  for (const o of offs) if (key(Sv.solve(Object.assign({}, Q0, o))) !== k0) same = false;
  check("defaults unchanged with every new option off", same && !base.moveSens, k0);
  const atRest = Sv.solve(Object.assign({}, Q0, { move: {} }));
  check("robot at rest (3D path) == default answer", key(atRest) === k0 && !!atRest.moveSens, key(atRest));
}

// (4) moving changes the answer and the sensitivity per 0.1 m/s is reported for the shot and its twin
{
  const r = Sv.solve(Object.assign({}, Q0, { move: { along: 0.5 } })), ms = r.moveSens;
  check("moving toward the goal changes the answer", key(r) !== k0, key(r));
  check("sensitivity per 0.1 m/s present (shot and twin)", !!ms && isFinite(ms.toward.dTheta) && !!r.twin.moveSens &&
        ms.per === 0.1, ms ? "toward " + ms.toward.dTheta.toFixed(2) + " deg / " + Math.round(ms.toward.dRpm) +
        " rpm, sideways " + ms.sideways.dTheta.toFixed(2) + " deg / " + Math.round(ms.sideways.dRpm) + " rpm" : "");
  const far = Sv.solve(Object.assign({}, Q0, { move: { across: 17 } }));
  check("sideways speed beyond the lead gives no clean shot", far.count === 0, "count " + far.count);
}

// (5) hit chance: fast, reproducible, Wilson interval holds the estimate, twin present, assumed-scatter note
{
  const rec = base.minRpmTol, tr = base.twin.minRpmTol;
  const hc = Sv.hitChance(Q0, rec.v, rec.theta, { n: 1000, twinAt: { v: tr.v, theta: tr.theta } });
  const hc2 = Sv.hitChance(Q0, rec.v, rec.theta, { n: 1000, twinAt: { v: tr.v, theta: tr.theta } });
  const okW = hc.sets.concat([hc.twin]).every(function (s) { return s.lo <= s.p + 1e-12 && s.p <= s.hi + 1e-12 && s.k <= s.n; });
  check("hit chance: 3 aero sets + twin, Wilson holds p", hc.ok && hc.sets.length === 3 && !!hc.twin && okW,
        hc.sets.map(function (s) { return s.name + " " + s.p.toFixed(3) + " [" + s.lo.toFixed(3) + ", " + s.hi.toFixed(3) + "]"; }).join(", ") +
        "; twin " + hc.twin.p.toFixed(3));
  check("hit chance reproducible (same seed, same counts)", JSON.stringify(hc.sets) === JSON.stringify(hc2.sets) &&
        hc.twin.k === hc2.twin.k);
  // wall-clock limit fails only with STRICT_TIMING=1 (reported otherwise: shared, loaded machine)
  check("hit chance under 2 s for 4000 shots", process.env.STRICT_TIMING !== "1" || hc.ms < 2000,
        Math.round(hc.ms) + " ms" + (hc.ms < 2000 ? "" : " (over 2 s: " + (process.env.STRICT_TIMING === "1" ? "enforced" : "reported only; STRICT_TIMING=1 enforces") + ")"));
  check("hit chance labelled ASSUMED scatter, not repeatability", /ASSUMED/.test(hc.note) && /not a measured repeatability/.test(hc.note));
  // a user Cl table replaces every aero set's lift: one run named Cl_table, not three identical low/nominal/high
  const hcT = Sv.hitChance(Object.assign({}, Q0, { lift: { table: [[0.5, 0.2], [1.5, 0.35]] } }), rec.v, rec.theta, { n: 200 });
  check("hit chance with a Cl table: one set, named Cl_table", hcT.ok && hcT.sets.length === 1 && hcT.sets[0].name === "Cl_table" && !!hcT.twin,
        hcT.sets.map(function (s) { return s.name + " " + s.k; }).join(", "));
  const w0 = P.wilson(0, 50), w1 = P.wilson(50, 50);
  check("Wilson edges", w0[0] === 0 && w0[1] > 0 && w1[1] > 1 - 1e-12 && w1[0] < 1, JSON.stringify([w0, w1]));
  const nm = P.normals(1, 20000);
  let m = 0, v2 = 0;
  for (const z of nm) { m += z; v2 += z * z; }
  m /= nm.length; v2 = v2 / nm.length - m * m;
  check("normals mean 0, variance 1", Math.abs(m) < 0.03 && Math.abs(v2 - 1) < 0.04, m.toFixed(4) + " " + v2.toFixed(4));
}

// (6) options do something where they should: gyro-correct S lowers lift for a tilted spin axis (yaw rate),
// effective mass slows the fall, a negative Cl table point turns lift down
{
  const p = Object.assign({}, caseOf(1.0).params);
  const zAt = function (pp, w0) {
    const r = P.integrate3D([0, 0, 0], [3, 0, 6], w0, pp, 2e-3, 0.8, -1e9);
    return r.Z[r.n - 1];
  };
  const w = [0, -0.3 * Math.hypot(3, 6) / p.radius, 0];
  const pure = zAt(p, w), pureG = zAt(Object.assign({}, p, { s_perp: true }), w);
  const tilt = [0, w[1], -w[1]], tiltA = zAt(p, tilt), tiltG = zAt(Object.assign({}, p, { s_perp: true }), tilt);
  check("gyro-correct S: pure backspin unchanged, tilted axis less lift", Math.abs(pure - pureG) < 1e-9 && tiltG < tiltA,
        "pure d " + (pure - pureG).toExponential(1) + ", tilted " + tiltA.toFixed(4) + " -> " + tiltG.toFixed(4));
  const vac = { rho: 0, mass: p.mass, radius: p.radius, Cd: 0.5, c1: 0, clmax: 0, k: 0 };
  const zv = zAt(vac, [0, 0, 0]), ze = zAt(Object.assign({}, vac, { eps_mass: 0.01 }), [0, 0, 0]);
  const tt = 0.8;
  check("effective mass: g / (1 + eps) in vacuum", Math.abs((6 * tt - zv) * 1 / 1.01 - (6 * tt - ze)) < 1e-9,
        "drop " + (6 * tt - zv).toFixed(5) + " -> " + (6 * tt - ze).toFixed(5));
  const zneg = zAt(Object.assign({}, p, { cl_table: [[0, 0], [1, -0.2]] }), w), zpos = zAt(Object.assign({}, p, { cl_table: [[0, 0], [1, 0.2]] }), w);
  const znl = zAt(Object.assign({}, p, { c1: 0 }), w);
  check("Cl table sign carries through", zneg < znl && zpos > znl,
        zneg.toFixed(4) + " < " + zpos.toFixed(4));
  check("reverse Magnus only below Re 4.6e4 and S 0.5", P.clOf(Object.assign({}, p, { cl_rev: 0.1 }), 0.2, 2e4) < 0 &&
        P.clOf(Object.assign({}, p, { cl_rev: 0.1 }), 0.2, 6e4) === P.clOf(p, 0.2, 6e4) &&
        P.clOf(Object.assign({}, p, { cl_rev: 0.1 }), 0.8, 2e4) === P.clOf(p, 0.8, 2e4));
}

console.log(JSON.stringify({ failed: failed, checks: summary }));
process.exit(failed ? 1 : 0);
