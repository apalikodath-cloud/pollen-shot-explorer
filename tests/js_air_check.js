// Node checks for the optional air / drag / draft terms (physics.js airState, cdBase, aeroExt; solver.js q.air,
// q.drag, q.wind, grip flag). Run: node tests/js_air_check.js
//   --dump  print JSON of JS trajectories for fixed option cases (tests/test_air.py compares them with
//           src/feasibility.integrate_batch + src/air.py; no field data needed).
// Without --dump: solver checks (fast path == physics.js under every option, defaults unchanged with every option
// off, twin present, grip flag). Exit 0 pass, 1 fail, 77 field data missing (gitignored). Last line = JSON summary.
"use strict";
const fs = require("fs"), path = require("path");
const EX = path.join(__dirname, "..", "viz", "explorer");
const P = require(path.join(EX, "physics.js"));

const BASE = { rho: 1.2041, mass: 0.02495, radius: 0.0355, Cd: 0.5, c1: 0.35, clmax: 0.25, k: 0.03, nu: 1.506e-5 };
const CASES = [
  { name: "plain", p: {} },
  { name: "morrison", p: { cd_model: "morrison" } },
  { name: "blend", p: { cd_model: "blend" } },
  { name: "blend_custom", p: { cd_model: "blend", cd_sub: 0.55, cd_post: 0.3, re1: 2e4, re2: 4e4 } },
  { name: "spin_drag", p: { dcd_spin: 0.18 } },
  { name: "wind_along", p: { wind: [0.3, 0] } },
  { name: "wind_down", p: { wind: [0, -0.3] } },
  { name: "all", p: { cd_model: "morrison", dcd_spin: 0.08, wind: [-0.2, 0.1] } },
  { name: "no_magnus_wind", p: { c1: 0, wind: [0.5, 0.5], dcd_spin: 0.18 } },
  // PM-016 lift and mass options (MISSING_EFFECTS.md 2d, 2e; values ASSUMED)
  { name: "cl_table", p: { cl_table: [[0, 0], [0.5, 0.2], [1.5, 0.35]] } },
  { name: "cl_table_late", p: { cl_table: [[0.4, 0.15], [1.2, 0.3]], wind: [0.2, 0] } },
  { name: "rev_magnus", p: { cl_rev: 0.1 } },
  { name: "eps_mass", p: { eps_mass: 0.0135 } },
  { name: "lift_all", p: { cl_table: [[0, 0], [1, 0.3]], cl_rev: 0.05, eps_mass: 0.009, cd_model: "morrison" } },
];
const SHOTS = [[6.0, 73.5, 1.0], [9.0, 80.5, 1.0], [4.5, 45, 0.5], [7.5, 78.75, 0], [8.0, 60, -0.5]];

if (process.argv.includes("--dump")) {
  const out = { air: [P.airState(), P.airState(30, 85000, 0.6), P.airState(15, P.pressureFromAltitude(1600), 0.3)],
                morrison: [1e2, 1e3, 1e4, 3.55e4, 1e5, 2.63e5, 5e5].map(re => [re, P.morrisonCd(re)]), traj: [] };
  for (const c of CASES) for (const s of SHOTS) {
    const p = Object.assign({}, BASE, c.p);
    const r = P.integrate(s[0], s[1], s[2], p, 2e-3, 3.0, -0.8);
    const idx = [1, 50, 200, r.n - 1].filter(i => i < r.n);
    out.traj.push({ case: c.name, p: p, v: s[0], th: s[1], S: s[2], n: r.n,
                    pts: idx.map(i => [i, r.X[i], r.Z[i], r.VX[i], r.VZ[i]]) });
  }
  console.log(JSON.stringify(out));
  process.exit(0);
}

const FIELD = path.join(EX, "data", "field");
if (!fs.existsSync(path.join(FIELD, "index.json"))) { console.log("SKIP field data missing"); process.exit(77); }
const Sv = require(path.join(EX, "solver.js"));
const meta = JSON.parse(fs.readFileSync(path.join(FIELD, "index.json"), "utf8"));
const summary = {}; let failed = 0;
function check(name, ok, info) {
  console.log((ok ? "PASS " : "FAIL ") + name + (info ? "  " + info : ""));
  summary[name] = { ok: !!ok, info: info || "" };
  if (!ok) failed++;
}
let seed = 20261031;
function rnd() { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; }
function pick(a) { return a[Math.floor(rnd() * a.length)]; }
function caseOf(S) { return meta.cases.find(c => c.S === S && c.var === "nominal"); }

// (1) fused fast path == physics.js integrate + classify (section and 3D cell) under the options
{
  let n = 0, bad = 0, badM = 0;
  const out = [0, 0, 0, 0];
  for (let k = 0; k < 900; k++) {
    const c = caseOf(pick([0, 0.5, 1.0, 1.5])), side = k % 2 ? "fav" : "unfav", opt = pick(CASES).p;
    const psi = (rnd() * 60) * (rnd() < 0.5 ? -1 : 1), h = 0.2 + rnd() * 0.55, d = 0.6 + rnd() * 1.0;
    const v = side === "unfav" ? 5 + rnd() * 5 : 2 + rnd() * 8, th = side === "unfav" ? 60 + rnd() * 29 : 20 + rnd() * 65;
    const p = Object.assign({}, c.params, { nu: 1.506e-5 }, opt);
    const use3d = rnd() < 0.5;
    const q = { x: 0, y: 0, h: h, S: c.S, vu: 0.5, params: p, meta: meta, sideWalls: use3d, air: false };
    const xy = side === "fav" ? [d, (Math.max(d - 0.401, 1e-3)) * Math.tan(psi * Math.PI / 180)]
                              : [-d, (d + 0.401) * Math.tan(psi * Math.PI / 180)];
    q.x = xy[0]; q.y = xy[1];
    const ctx = Sv._context(q);
    if (!ctx.ps.ok) continue;
    const zs = ctx.zStop;
    const pth = P.integrateOblique(v, th, ctx.ps.psi, c.S, p, 2e-3, 3.0, zs);
    const cl = Sv._classifyCtx(ctx, pth, h, p.radius);
    const f = Sv._shotCtx(ctx, v, th, c.S, p, h, out);
    n++;
    if ((cl.result === "clean") !== (f === 1)) bad++;
    else if (f === 1 && (Math.abs(cl.minClear - out[0]) > 1e-12)) badM++;
  }
  check("fast_path_equals_physics_js_with_options", n > 500 && bad === 0 && badM === 0,
        `${n} shots, class disagree ${bad}, margin disagree ${badM}`);
}

// (2) every option off = the old arithmetic (aeroExt returns null; air:false keeps params rho)
{
  const c = caseOf(1.0), p = c.params;
  const ep = Sv.effParams({ params: p, air: false, drag: { model: "const", spin: 0 }, wind: { along: 0, up: 0 } }).p;
  const same = P.aeroExt(ep, 1.0, 7) === null && ep.rho === p.rho && ep.Cd === p.Cd && !ep.wind && !ep.dcd_spin && !ep.cd_model;
  const def = Sv.effParams({ params: p }).p;
  check("options_off_unchanged", same && Math.abs(def.rho - 1.20408) < 1e-4 && Math.abs(def.nu - 1.506e-5) < 1e-8,
        `default rho ${def.rho.toFixed(5)}, nu ${def.nu.toExponential(4)}`);
}

// (3) solve with options: twin present with the same air and drag, grip flags set, notes list the options
{
  const c = caseOf(1.0);
  const q = { x: -1.0, y: 0.2, h: 0.737, S: 1.0, vu: 0.42, params: c.params, meta: meta,
              drag: { model: "blend", spin: 0.08 }, wind: { along: 0.1, up: 0 }, air: { tC: 25, altM: 300, rh: 0.4 } };
  const r = Sv.solve(q);
  const t = r.twin;
  const ok = t && t.isTwin && t.S === 0 && t.params.c1 === 0 && t.params.rho === r.params.rho &&
    t.params.cd_model === "blend" && r.params.dcd_spin === 0.08 && r.params.wind[0] === 0.1 &&
    r.gripCap && r.gripCap.v === 8.9 && (!r.minRpm || typeof r.minRpm.gripLimited === "boolean") &&
    r.notes.some(s => /draft/.test(s)) && r.notes.some(s => /air: rho/.test(s));
  check("solve_options_twin_and_flags", ok, `rho ${r.params.rho.toFixed(4)}, minRpm ${r.minRpm ? r.minRpm.rpm.toFixed(0) : "none"}` +
        ` (twin ${t && t.minRpm ? t.minRpm.rpm.toFixed(0) : "none"}), ${r.ms.toFixed(0)} ms`);
}

// (4) grip flag: results above the PREDICTED 8.9 m/s cap are flagged, below are not
{
  const res = { minRpm: { v: 9.2 }, minAngle: { vLo: 8.0 }, minRpmTol: { v: 8.9 }, minAngleTol: null, mostForgiving: { v: 9.0 } };
  Sv._flagGrip(res, { vu: 0.42 });
  const ok = res.minRpm.gripLimited === true && res.minAngle.gripLimited === false && res.minRpmTol.gripLimited === false &&
             res.mostForgiving.gripLimited === true && res.gripCap.v === 8.9 && Math.abs(res.gripCap.rpm - Sv.rpm(8.9, 0.42)) < 1e-9;
  check("grip_flag_above_cap", ok, `cap ${res.gripCap.v} m/s = ${res.gripCap.rpm.toFixed(0)} rpm at v/u 0.42`);
}

console.log(JSON.stringify({ failed: failed, summary: summary }));
process.exit(failed ? 1 : 0);
