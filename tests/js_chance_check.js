// PM-017 checks of the best-chance search and the split solve (viz/explorer/solver.js bestChance / solve parts):
//      node tests/js_chance_check.js          -> PASS/FAIL lines + a JSON summary (default-pose numbers)
//      node tests/js_chance_check.js --dump   -> JSON for tests/test_best_chance.py (candidate lists, stage counts,
//                                                final and one-source-at-a-time counts; python twin =
//                                                src/robustness.py best_chance)
// Every number is a model output (PREDICTED) under ASSUMED launch scatter and ASSUMED aero sets: a model
// probability, not a measured repeatability. Exit 0 = pass, 1 = a check failed, 77 = field data missing.
"use strict";
const fs = require("fs"), path = require("path");
const EX = path.join(__dirname, "..", "viz", "explorer");
const FIELD = path.join(EX, "data", "field");
const P = require(path.join(EX, "physics.js"));
const Sv = require(path.join(EX, "solver.js"));

if (!fs.existsSync(path.join(FIELD, "index.json"))) { console.log("SKIP field data missing"); process.exit(77); }
const meta = JSON.parse(fs.readFileSync(path.join(FIELD, "index.json"), "utf8"));
const caseOf = function (S, v) { return meta.cases.find(function (c) { return c.S === S && c.var === (v || "nominal"); }); };
const now = function () { return Number(process.hrtime.bigint()) / 1e6; };
// the page's default Robot-view pose (page.html R): x -1.0, y 0.2, h 0.737 m, S 1.0, grip 0.42, still air
function q0(extra) {
  return Object.assign({ x: -1.0, y: 0.2, h: 0.737, S: 1.0, vu: 0.42, params: caseOf(1.0).params, meta: meta,
                         air: { tC: 20, altM: 0, rh: 0 }, drag: { model: "const", spin: 0 }, wind: { along: 0, up: 0, side: 0 },
                         robot: { length: 18 * 0.0254, width: 18 * 0.0254, offset: [0, 0] } }, extra || {});
}

if (process.argv[2] === "--dump") {
  // small searches (the Python replay integrates every shot in numpy)
  const SMALL = { n1: 24, n2: 72, n: 160, k1: 8, k2: 3 };
  const poses = [
    { tag: "default S1", q: q0() },
    { tag: "default S1 twin", q: q0(), twin: true },
    { tag: "moving S1", q: q0({ move: { along: 0.5, across: 0.3 } }), sig: { sv: 0.02, sth: 0.3, spsi: 0.8 } },
    { tag: "fav S0.5", q: q0({ x: 1.2, y: 0.9, h: 0.5, S: 0.5, params: caseOf(0.5).params }) },
  ];
  const cases = [];
  for (const pz of poses) {
    const q = pz.q, r = Sv.solve(q, null, { part: pz.twin ? "twin" : "main" });
    const b = Sv.bestChance(q, r, Object.assign({ seed: 11 + cases.length, sig: pz.sig }, SMALL));
    if (!b.ok) { process.stderr.write("no best chance for " + pz.tag + ": " + b.reason + "\n"); process.exit(1); }
    const ctx = Sv._context(Object.assign({}, q, { params: Sv.effParams(q).p }), true), F = ctx.F, ep = Sv.effParams(q).p;
    const setParams = {};
    for (const s of b.sets) {
      const c = caseOf(q.S, s.name);
      const p = pz.twin ? Sv.twinParams(ep) : Sv.effParams(Object.assign({}, q, { params: c ? c.params : q.params })).p;
      setParams[s.name] = Sv._params3(p, F);
    }
    cases.push({ tag: pz.tag, side: ctx.ps.side, ridge: true, wallT: P.CELL3D.WALL_T, h: q.h, zStop: ctx.zStop, S: b.S, F: F,
                 seed: b.seed, sig: b.sig, opts: SMALL, setParams: setParams,
                 candidates: b.search.stage1.map(function (c) { return { v: c.v, theta: c.theta, from: c.from }; }),
                 stage1: b.search.stage1, stage2: b.search.stage2, v: b.v, theta: b.theta, sets: b.sets, breakdown: b.breakdown });
  }
  process.stdout.write(JSON.stringify({ sections: { unfav: meta.sections.unfav_s0, fav: meta.sections.fav_s0 }, cases: cases }));
  process.exit(0);
}

const summary = {}; let failed = 0;
function check(name, ok, info) {
  console.log((ok ? "PASS " : "FAIL ") + name + (info ? "  " + info : ""));
  summary[name] = { ok: !!ok, info: info || "" };
  if (!ok) failed++;
}
// wall-clock limits fail only with STRICT_TIMING=1: on a shared, loaded machine they are reported, not enforced
const STRICT = process.env.STRICT_TIMING === "1";
const timed = function (ok, what) { return ok ? " (" + what + ": yes)" : " (" + what + ": NO, " + (STRICT ? "enforced" : "reported only; STRICT_TIMING=1 enforces") + ")"; };
const pc = function (x) { return (100 * x).toFixed(1) + " %"; };
const setStr = function (rows) { return rows.map(function (s) { return s.name + " " + pc(s.p); }).join(", "); };

// (1) split solve: the main and twin parts equal the combined solve
const Q = q0();
let t = now();
const full = Sv.solve(Q);
const tFull = now() - t;
t = now(); const rm = Sv.solve(Q, null, { part: "main" }); const tMain = now() - t;
t = now(); const rt = Sv.solve(Q, null, { part: "twin" }); const tTwin = now() - t;
{
  let diffM = 0, diffT = 0;
  for (let i = 0; i < full.grid.clean.length; i++) { if (full.grid.clean[i] !== rm.grid.clean[i]) diffM++; if (full.twin.grid.clean[i] !== rt.grid.clean[i]) diffT++; }
  const same = function (a, b) { return a && b && a.v === b.v && a.theta === b.theta; };
  check("solve parts == combined solve", diffM === 0 && diffT === 0 && rm.twinPending === true && rt.isTwin === true &&
        same(full.minRpmTol, rm.minRpmTol) && same(full.twin.minRpmTol, rt.minRpmTol) && same(full.twin.mostForgiving, rt.mostForgiving),
        "cells differing main " + diffM + " twin " + diffT + "; combined " + tFull.toFixed(0) + " ms, main part " + tMain.toFixed(0) +
        " ms, twin part " + tTwin.toFixed(0) + " ms (parallel wall = the slower part)");
}
// (2) S = 0: the twin reuses the main grid (no second solve), twin params have no lift
{
  const q = q0({ S: 0, params: caseOf(0).params });
  const r = Sv.solve(q);
  check("S = 0: twin is the main grid with no-lift params", r.twin && r.twin.isTwin && r.twin.sameAsMain && r.twin.params.c1 === 0 &&
        r.twin.grid === r.grid && !r.twinPending, "count " + r.count);
}
// (3) best chance at the default pose vs the tolerant lowest-rpm setting (the old recommendation)
t = now();
const B = Sv.bestChance(Q, rm);
const tBest = now() - t;
t = now();
const BT = Sv.bestChance(Q, rt);
const tBestT = now() - t;
const rec = rm.minRpmTol, hcRec = Sv.hitChance(Q, rec.v, rec.theta, { twinAt: rt.minRpmTol });
const mRec = hcRec.sets.reduce(function (a, s) { return a + s.p; }, 0) / hcRec.sets.length;
check("best chance >= the tolerant lowest-rpm setting", B.ok && B.mean >= mRec && B.sets.length === 3,
      "best " + B.v + " m/s @ " + B.theta + " deg (" + Math.round(B.rpm) + " rpm): " + setStr(B.sets) + ", mean " + pc(B.mean) +
      " | lowest rpm " + rec.v.toFixed(3) + " @ " + rec.theta.toFixed(2) + ": " + setStr(hcRec.sets) + ", mean " + pc(mRec));
check("twin best chance >= twin lowest-rpm setting", BT.ok && BT.isTwin && BT.sets.length === 1 && BT.mean >= hcRec.twin.p,
      "twin best " + BT.v + " @ " + BT.theta + " (" + Math.round(BT.rpm) + " rpm) " + pc(BT.mean) + " | twin lowest rpm " + pc(hcRec.twin.p));
check("best chance respects the grip limit", B.inCap && !B.gripLimited && B.v <= P.HOOD_V_MAX && BT.v <= P.HOOD_V_MAX,
      "cap " + P.HOOD_V_MAX + " m/s");
{
  const h = Sv.hitChance(Q, B.v, B.theta);
  check("best chance reported on fresh draws == hitChance there", h.sets.every(function (s, i) { return s.k === B.sets[i].k; }),
        setStr(h.sets));
  const wil = B.sets.every(function (s) { return s.lo <= s.p && s.p <= s.hi; });
  const B2 = Sv.bestChance(Q, rm);
  check("best chance reproducible, Wilson holds p", wil && B2.v === B.v && B2.theta === B.theta && B2.sets[1].k === B.sets[1].k, "");
  const bd = B.breakdown, lowest = bd.parts.reduce(function (a, b) { return b.p < a.p ? b : a; });
  check("scatter breakdown: one source at a time, lowest dominates", bd.parts.length === 3 && bd.dominant === lowest.source &&
        bd.parts.every(function (p) { return p.p >= bd.all.p - 0.03; }),
        bd.set + ": all " + pc(bd.all.p) + "; " + bd.parts.map(function (p) { return p.source + " only " + pc(p.p); }).join(", ") +
        " -> " + bd.dominant + " | twin: " + BT.breakdown.parts.map(function (p) { return p.source + " " + pc(p.p); }).join(", ") +
        " -> " + BT.breakdown.dominant);
  check("best chance labelled PREDICTED under ASSUMED scatter", /ASSUMED/.test(B.label) && /not a measured repeatability/.test(B.note), "");
}
// (4) scatter controls: no scatter at a clean setting = every shot in; heading-only scatter matches the breakdown
{
  const z = Sv.hitChance(Q, B.v, B.theta, { sig: { sv: 0, sth: 0, spsi: 0 }, sets: ["nominal"] });
  const hd = Sv.hitChance(Q, B.v, B.theta, { sig: { sv: 0, sth: 0 }, sets: ["nominal"] });
  check("scatter inputs reach the Monte Carlo", z.sets[0].p === 1 && hd.sets[0].k === B.breakdown.parts[2].k,
        "no scatter " + pc(z.sets[0].p) + ", heading only " + pc(hd.sets[0].p));
}
// (4b) the field-map chance layer's small search: no breakdown, one air set
{
  const f = Sv.bestChance(Q, rm, { n1: 32, n2: 128, n: 300, k1: 10, k2: 3, breakdown: false, sets: ["nominal"] });
  check("small search without breakdown (field chance layer)", f.ok && f.breakdown === null && f.sets.length === 1 && f.n === 300,
        f.v + " @ " + f.theta + " " + setStr(f.sets));
}
// (5) moving robot: the main part (the slower worker) stays near 2 s
{
  const qm = q0({ move: { along: 0.5, across: 0.3 } });
  t = now(); const m = Sv.solve(qm, null, { part: "main" }); const a = now() - t;
  t = now(); const tw = Sv.solve(qm, null, { part: "twin" }); const b = now() - t;
  t = now(); const bm = Sv.bestChance(qm, m); const c = now() - t;
  check("moving solve: split parts work" + timed(Math.max(a, b) < 3000, "slower part under 3 s, target about 2 s"), m.moveSens && tw.moveSens && bm.ok && (!STRICT || Math.max(a, b) < 3000),
        "main " + a.toFixed(0) + " ms, twin " + b.toFixed(0) + " ms, best chance " + c.toFixed(0) + " ms; best " + bm.v + " @ " + bm.theta +
        " " + setStr(bm.sets));
}
check("best chance search time" + timed(tBest < 5000 && tBestT < 3000, "main under 5 s, twin under 3 s"), !STRICT || (tBest < 5000 && tBestT < 3000), "main " + tBest.toFixed(0) + " ms, twin " + tBestT.toFixed(0) + " ms");

console.log(JSON.stringify({ failed: failed, checks: Object.keys(summary).length,
  default: { best: { v: B.v, theta: B.theta, rpm: Math.round(B.rpm), sets: B.sets.map(function (s) { return [s.name, s.p]; }), mean: B.mean,
                     dominant: B.breakdown.dominant },
             twinBest: { v: BT.v, theta: BT.theta, rpm: Math.round(BT.rpm), p: BT.mean, dominant: BT.breakdown.dominant },
             lowestRpm: { v: rec.v, theta: rec.theta, sets: hcRec.sets.map(function (s) { return [s.name, s.p]; }), mean: mRec, twin: hcRec.twin.p } } }));
process.exit(failed ? 1 : 0);
