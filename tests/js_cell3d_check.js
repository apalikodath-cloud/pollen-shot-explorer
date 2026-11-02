// Node checks for the 3D HIVE cell model (PM-013: physics.js buildCell3D / classifyOblique3D, solver.js
// sideWalls). Run: node tests/js_cell3d_check.js            -> checks, JSON summary as the last line
//                  node tests/js_cell3d_check.js --dump N   -> N+ shots (paths + JS results) for
//                                                             tests/test_cell3d.py (python cross-check)
// Exit 0 = pass, 1 = a check failed, 77 = field data missing (gitignored; viz/explorer/export_field.py).
"use strict";
const fs = require("fs"), path = require("path");
const EX = path.join(__dirname, "..", "viz", "explorer");
const FIELD = path.join(EX, "data", "field");
const P = require(path.join(EX, "physics.js"));
const Sv = require(path.join(EX, "solver.js"));

if (!fs.existsSync(path.join(FIELD, "index.json"))) { console.log("SKIP field data missing"); process.exit(77); }
const meta = JSON.parse(fs.readFileSync(path.join(FIELD, "index.json"), "utf8"));
const caseOf = function (S) { return meta.cases.find(function (c) { return c.S === S && c.var === "nominal"; }); };
let seed = 20261031;
function rnd() { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; }
function lh(side, d) { return side === "fav" ? Math.max(d - 0.401, 1e-3) : d + 0.401; }
// release point (field frame, pose_pos) for a side, d and signed bearing psi
function poseXY(side, d, psi) { return [side === "fav" ? d : -d, lh(side, d) * Math.tan(psi * Math.PI / 180)]; }
const R = 0.0355;

if (process.argv[2] === "--dump") {
  // random poses; for each, a coarse fast scan finds clean and non-clean (v, theta); the reference
  // classifyOblique3D result is stored with the exact path (float64, base64)
  const N = parseInt(process.argv[3] || "600", 10), shots = [];
  const b64 = function (a) { return Buffer.from(new Float64Array(a).buffer).toString("base64"); };
  const out = [0, 0, 0, 0];
  while (shots.length < N) {
    const side = rnd() < 0.5 ? "unfav" : "fav", S = [0, 0.5, 1.0, 1.5][Math.floor(rnd() * 4)];
    const d = 0.6 + rnd() * 1.1, psi = (rnd() < 0.5 ? -1 : 1) * rnd() * 60, h = 0.2 + rnd() * 0.537;
    const ridge = rnd() < 0.8, wallT = rnd() < 0.8 ? P.CELL3D.WALL_T : 0.02 + rnd() * 0.05;
    const c = caseOf(S), xy = poseXY(side, d, psi);
    const q = { x: xy[0], y: xy[1], h: h, S: S, params: c.params, meta: meta, sideWalls: true, ridge: ridge, wallT: wallT };
    const ctx = Sv._context(q);
    if (!ctx.c3) continue;
    const cl = [], ot = [];
    for (let k = 0; k < 160; k++) {
      const v = side === "unfav" ? 5 + rnd() * 6 : 2 + rnd() * 8, th = side === "unfav" ? 60 + rnd() * 29.8 : 20 + rnd() * 69.5;
      (Sv._shotCtx(ctx, v, th, S, c.params, h, out) === 1 ? cl : ot).push([v, th]);
    }
    const sel = cl.slice(0, 4).concat(ot.slice(0, 8 - Math.min(cl.length, 4)));
    for (const vt of sel) {
      const pa = P.integrateOblique(vt[0], vt[1], ctx.ps.psi, S, c.params, 2e-3, 3.0, ctx.zStop);
      const r = Sv._classifyCtx(ctx, pa, h, c.params.radius);
      shots.push({ side: side, d: ctx.ps.d, h: h, psi: ctx.ps.psi, aimX: ctx.c3.aimX, R: c.params.radius,
                   ridge: ridge, wallT: wallT, v: vt[0], th: vt[1], S: S,
                   X: b64(pa.X.subarray(0, pa.n)), Z: b64(pa.Z.subarray(0, pa.n)), js: r });
    }
  }
  process.stdout.write(JSON.stringify({ sections: { unfav: meta.sections.unfav_s0, fav: meta.sections.fav_s0 },
                                        half: P.CELL3D.CELL_HALF, slope: P.CELL3D.ROOF_SLOPE, shots: shots }));
  process.exit(0);
}

const summary = {}; let failed = 0;
function check(name, ok, info) {
  console.log((ok ? "PASS " : "FAIL ") + name + (info ? "  " + info : ""));
  summary[name] = { ok: !!ok, info: info || "" };
  if (!ok) failed++;
}

// (1) psi = 0, ridge off: exactly classifyOblique on the s = 0 section (result, i, hit, minClear, entry
// angle bit-identical). (2) ridge on is stricter only at psi = 0 (a pentagon roof is lower off the centre
// line; the s = 0 section has the full 14 in height everywhere): never clean where the section is not.
for (const side of ["unfav", "fav"]) {
  const sec = meta.sections[side + "_s0"];
  const flat = P.buildCell3D(sec, { ridge: false }), cell = P.buildCell3D(sec);
  let n = 0, clean = 0, bad = 0, looser = 0, diff = 0;
  for (let k = 0; k < 2500; k++) {
    const c = meta.cases[Math.floor(rnd() * meta.cases.length)];
    const h = 0.2 + rnd() * 0.537, d = 0.55 + rnd() * 1.2;
    const v = side === "unfav" ? 5 + rnd() * 6 : 2 + rnd() * 8, th = side === "unfav" ? 60 + rnd() * 29.8 : 20 + rnd() * 69.5;
    const pa = P.integrateOblique(v, th, 0, c.S, c.params, 2e-3, 3, 0.4);
    const aimX = lh(side, d) - d;
    const a = P.classifyOblique(pa, sec, d, h, R), b = P.classifyOblique3D(pa, flat, d, h, R, aimX, 0);
    const r = P.classifyOblique3D(pa, cell, d, h, R, aimX, 0);
    n++; if (a.result === "clean") clean++;
    if (a.result !== b.result || a.i !== b.i || a.hit !== b.hit || !(a.minClear === b.minClear) ||
        !(a.entryAngle === b.entryAngle)) bad++;
    if (r.result === "clean" && a.result !== "clean") looser++;
    if (r.result !== a.result) diff++;
  }
  check("psi0_identity_ridge_off_" + side, bad === 0, n + " shots, " + clean + " clean, " + bad + " differ");
  check("psi0_ridge_stricter_only_" + side, looser === 0, looser + " looser, " + diff + " differ (ridge)");
}

// (3) fused solver fast path == classifyOblique3D on shots around the solved windows (clean flag exact,
// clearance to 1e-12 m and entry angle to 1e-9 deg: the pruned face scan can round differently), and (4) full solve + twin time
const out = [0, 0, 0, 0];
let n = 0, nClean = 0, bad = 0, badM = 0;
const times = [];
for (const t of [["unfav", 1.0, 1.0, 30, 0.5], ["fav", 1.0, 1.2, 45, 0.5], ["unfav", 0, 1.4, 40, 0.737],
                 ["fav", 0.5, 0.9, 55, 0.3]]) {
  const side = t[0], S = t[1], d = t[2], psi = t[3], h = t[4], c = caseOf(S), xy = poseXY(side, d, psi);
  const q = { x: xy[0], y: xy[1], h: h, S: S, vu: 0.5, params: c.params, meta: meta };
  const res = Sv.solve(q);
  times.push(res.ms);
  if (!res.grid) { check("pose_ok_" + t.join("_"), false, "pose not solvable"); continue; }
  const ctx = Sv._context(q), g = res.grid, nTh = g.th.length, idx = [];
  for (let i = 0; i < g.clean.length; i++) if (g.clean[i]) idx.push(i);
  for (let k = 0; k < 250; k++) {
    const i = idx.length && rnd() < 0.6 ? idx[Math.floor(rnd() * idx.length)] : Math.floor(rnd() * g.clean.length);
    const v = g.v[Math.floor(i / nTh)] + (rnd() - 0.5) * 0.2, th = g.th[i % nTh] + (rnd() - 0.5) * 0.4;
    const pa = P.integrateOblique(v, th, ctx.ps.psi, S, c.params, 2e-3, 3, ctx.zStop);
    const r = Sv._classifyCtx(ctx, pa, h, c.params.radius), f = Sv._shotCtx(ctx, v, th, S, c.params, h, out);
    n++; if (f === 1) nClean++;
    if ((r.result === "clean") !== (f === 1)) bad++;
    else if (f === 1 && (!(Math.abs(r.minClear - out[0]) <= 1e-12) || (r.entryAngle !== null && !(Math.abs(r.entryAngle - out[1]) <= 1e-9)))) badM++;
  }
}
check("fused_fast_path_equals_reference", bad === 0 && badM === 0 && nClean > 100,
      n + " shots, " + nClean + " clean, " + bad + " class / " + badM + " clearance or angle differ");
// (3b) the same on random poses and shots (signed psi, ridge on/off, wall thickness), all classes;
// clearance compared for clean and hit (a miss may stop early in the fast path)
{
  let m = 0, mc = 0, mh = 0, b1 = 0, b2 = 0;
  while (m < 6000) {
    const side = rnd() < 0.5 ? "unfav" : "fav", S = [0, 0.5, 1.0, 1.5][Math.floor(rnd() * 4)];
    const d = 0.6 + rnd() * 1.1, psi = (rnd() < 0.5 ? -1 : 1) * rnd() * 60, h = 0.2 + rnd() * 0.537;
    const c = caseOf(S), xy = poseXY(side, d, psi);
    const q = { x: xy[0], y: xy[1], h: h, S: S, params: c.params, meta: meta, ridge: rnd() < 0.8,
                wallT: rnd() < 0.8 ? undefined : 0.02 + rnd() * 0.05 };
    const ctx = Sv._context(q);
    for (let k = 0; k < 60; k++, m++) {
      const v = side === "unfav" ? 5 + rnd() * 6 : 2 + rnd() * 8, th = side === "unfav" ? 60 + rnd() * 29.8 : 20 + rnd() * 69.5;
      const pa = P.integrateOblique(v, th, ctx.ps.psi, S, c.params, 2e-3, 3, ctx.zStop);
      const r = Sv._classifyCtx(ctx, pa, h, c.params.radius), f = Sv._shotCtx(ctx, v, th, S, c.params, h, out);
      const code = out[2] === 1 ? "clean" : out[2] === 2 ? "hit" : "miss";
      if (code === "clean") mc++; if (code === "hit") mh++;
      if (code !== r.result) b1++;
      else if (code !== "miss" && !(Math.abs(r.minClear - out[0]) <= 1e-12)) b2++;
    }
  }
  check("fused_equals_reference_random", b1 === 0 && b2 === 0 && mc > 80 && mh > 500,
        m + " shots (" + mc + " clean, " + mh + " hit), " + b1 + " class / " + b2 + " clearance differ");
}
// wall-clock limits fail only with STRICT_TIMING=1: on a shared, loaded machine they are reported, not enforced
const STRICT = process.env.STRICT_TIMING === "1";
const tOk = Math.max.apply(null, times) < 10000;
check("solve_with_twin_time", !STRICT || tOk,
      "ms " + times.map(function (x) { return x.toFixed(0); }).join(", ") + " (target about 3000 on an idle machine; under 10 s: " +
      (tOk ? "yes" : "NO, " + (STRICT ? "enforced" : "reported only; STRICT_TIMING=1 enforces")) + ")");

console.log(JSON.stringify({ failed: failed, checks: summary }));
process.exit(failed ? 1 : 0);
