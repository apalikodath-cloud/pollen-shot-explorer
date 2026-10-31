"""PM-021: does backspin beat the no-spin twin, field-wide, by hit chance?

Question (HANDOFF 0 and 3): from where on the field, at which release height and spin ratio, does a backspin shot
have a higher hit chance than the same ball with no spin (the no-spin twin, each at ITS own best setting)? And how
does the answer depend on the unmeasured lift level (Cl low / nominal / high, research/params_lit.json, ASSUMED)?

Model = the live solver's (viz/explorer/solver.js, 3D flight on the 3D cell, seed 20261031, ASSUMED launch scatter
1.5 % speed / 0.40 deg elevation / 0.50 deg heading, 1 sigma). Two parts:
 1. node runs the live solver's deterministic pieces for each job: the legality and bearing of the pose
    (solver.js pose), the clean (v, theta) grid at 0.1 m/s by 0.1 deg (far side) or 0.25 deg (near side) without
    scatter (solve), and the best-chance candidate list from that grid (bcCandidates: smoothed clean share,
    inside the PREDICTED 8.9 m/s hood grip cap), plus the moving-robot frame F, z_stop and the integrate3d
    parameters of every aero set. No Monte Carlo runs in node.
 2. Python runs the Monte Carlo search of solver.js bestChance stages 1 to 3 (two-stage search with common random
    numbers, then the winner on fresh draws with a Wilson 95 % interval) with src/robustness.py mc_shots (3D cell
    branch, the PM-016/PM-017 port that tests/test_best_chance.py checks shot for shot against the browser).
    search() equals robustness.best_chance without the stage-4 scatter breakdown (not needed here; it would cost a
    further 3 n shots per search).

Searches per pose and release height h:
  twin          S = 0, no lift (solver.js twinParams); candidates from the twin grid; one set.
  robust (S)    the page's best chance: candidates from the nominal-lift grid, the three lift sets pooled with equal
                weight (ASSUMED); the winner reported per set. = what you would set without knowing the lift.
  tuned (S, L)  the best chance for one lift set L alone, candidates from that set's own grid. = what you would set
                after measuring the lift.
The twin and the backspin winners are reported on the same fresh draws (paired).

Grip limit: only clean settings at or below the 8.9 m/s cap (PREDICTED, docs/04_launcher.md) are searched. A pose
with no clean in-cap setting gets status no_clean_in_cap and chance 0 (k = n = 0): no in-cap grid setting goes in
even without scatter.

Every chance is PREDICTED: a model probability under ASSUMED scatter and ASSUMED aero, NOT a measured
repeatability (HANDOFF 5). The no-spin twin is a reference: the one-wheel hood launcher always spins the ball
(S about 1.0 to 1.3 PREDICTED, src/launcher.py); a no-spin shooter is a different mechanism (out of scope).

Run (hours; background):  python -m src.spin_vs_twin run --work <dir> --workers 10
Then:                      python -m src.spin_vs_twin csv --work <dir>      (writes data/spin_vs_twin.csv)
                           python -m src.spin_vs_twin summary               (tables for research/SPIN_VS_TWIN.md)
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
from multiprocessing import Pool
from typing import Optional

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src import cell3d as c3d  # type: ignore
    from src import robustness as rb  # type: ignore
else:
    from . import cell3d as c3d
    from . import robustness as rb

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPLORER = os.path.join(_ROOT, "viz", "explorer")
FIELD_INDEX = os.path.join(EXPLORER, "data", "field", "index.json")
CSV_OUT = os.path.join(_ROOT, "data", "spin_vs_twin.csv")

#: coarse field grid (m, field frame of solver.js: x < 0 = unfavourable / far side, y along the pivot axis); ASSUMED
X_UNFAV = (-0.65, -0.95, -1.25, -1.55)
X_FAV = (0.65, 0.95, 1.25, 1.55)
YS = (-1.2, -0.8, -0.4, 0.0, 0.4, 0.8, 1.2, 1.6, 2.0)
HS = (0.35, 0.5, 0.737)          # release heights (m), ASSUMED robot options (0.737 = the page default)
SS = (0.5, 1.0, 1.5)             # spin ratios S = R w / v, ASSUMED sweep
SETS = ("Cl_low", "nominal", "Cl_high")
VU = 0.42                        # page default grip v/u (ASSUMED), only for the rpm column
WHEEL_D = 0.098                  # m (user)
SEED = 20261031
BC = dict(rb.BC)                 # n1 64, n2 400, n 1000, k2 5 (solver.js BC)
LABEL = ("PREDICTED: model probability under ASSUMED launch scatter (1.5 % / 0.40 deg / 0.50 deg) and ASSUMED aero "
         "(research/params_lit.json Cl low / nominal / high); not a measured repeatability")

# ---------------------------------------------------------------------------------------------- node driver
JS_DRIVER = r"""
"use strict";
const fs = require("fs"), path = require("path");
const EX = process.argv[2];
const P = require(path.join(EX, "physics.js")), Sv = require(path.join(EX, "solver.js"));
const meta = JSON.parse(fs.readFileSync(path.join(EX, "data", "field", "index.json"), "utf8"));
const caseOf = function (S, v) { return meta.cases.find(function (c) { return c.S === S && c.var === (v || "nominal"); }); };
const jobs = JSON.parse(fs.readFileSync(0, "utf8"));
const robot = { length: 18 * 0.0254, width: 18 * 0.0254, offset: [0, 0] };
const out = [];
for (const j of jobs) {
  const S = j.kind === "twin" ? 1.0 : j.S, setName = j.kind === "set" ? j.set : "nominal";
  const cs = caseOf(S, setName);
  const q = { x: j.x, y: j.y, h: j.h, S: S, vu: j.vu, params: cs.params, meta: meta, air: { tC: 20, altM: 0, rh: 0 },
              drag: { model: "const", spin: 0 }, wind: { along: 0, up: 0, side: 0 }, robot: robot };
  const ps = Sv.pose(j.x, j.y, meta, { robot: robot });
  const r = { id: j.id, kind: j.kind, x: j.x, y: j.y, h: j.h, S: j.kind === "twin" ? 0 : j.S, set: j.kind === "set" ? j.set : null,
              side: ps.side, d: ps.d, psi: ps.psi, status: ps.status, otherHive: ps.otherHive };
  if (ps.status !== "ok") { r.plan = null; out.push(r); continue; }
  const res = Sv.solve(q, null, { part: j.kind === "twin" ? "twin" : "main" });
  const ep = Sv.effParams(q), ctx = Sv._context(Object.assign({}, q, { params: ep.p }), true);
  r.count = res.count || 0;
  r.F = ctx.F; r.zStop = ctx.zStop; r.secKey = ctx.ps.side + "_s0";
  const sets = {};
  if (j.kind === "twin") sets["no-spin twin"] = Sv._params3(Sv.twinParams(ep.p), ctx.F);
  else if (j.kind === "set") sets[j.set] = Sv._params3(ep.p, ctx.F);
  else for (const nm of ["Cl_low", "nominal", "Cl_high"])
    sets[nm] = Sv._params3(Sv.effParams(Object.assign({}, q, { params: caseOf(S, nm).params })).p, ctx.F);
  r.sets = sets;
  if (!r.count) { r.candidates = []; r.inCap = false; r.cells = 0; out.push(r); continue; }
  const cd = Sv._bcCandidates(res, Sv.HC_SIG, Sv.BC.k1);
  r.inCap = cd.inCap; r.cells = cd.cells;
  r.candidates = cd.inCap ? cd.list.map(function (c) { return { v: c.v, theta: c.theta, from: c.from }; }) : [];
  if (j.js) {
    const o = Object.assign({ breakdown: false }, j.opts || {}, j.kind === "set" ? { sets: [j.set] } : {});
    const b = Sv.bestChance(q, res, o);
    r.js = { v: b.v, theta: b.theta, sets: b.sets, gripLimited: b.gripLimited };
  }
  out.push(r);
}
process.stdout.write(JSON.stringify(out));
"""


def _node() -> str:
    node = shutil.which("node")
    if not node:
        raise RuntimeError("node not found: the plans come from viz/explorer/solver.js")
    return node


def node_plans(jobs: list) -> list:
    """Run the live solver's deterministic parts (pose, clean grid, candidates, frame, set params) for jobs."""
    fd, js = tempfile.mkstemp(suffix=".js", prefix="spin_vs_twin_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(JS_DRIVER)
        r = subprocess.run([_node(), js, EXPLORER], input=json.dumps(jobs), capture_output=True, text=True,
                           timeout=3600)
        if r.returncode != 0:
            raise RuntimeError("node driver failed: " + r.stderr[-2000:])
        return json.loads(r.stdout)
    finally:
        try:
            os.remove(js)
        except OSError:
            pass


# ---------------------------------------------------------------------------------------------- Monte Carlo search
_CELLS: dict = {}
_META: dict = {}


def _meta() -> dict:
    if "m" not in _META:
        with open(FIELD_INDEX, encoding="utf-8") as fh:
            _META["m"] = json.load(fh)
    return _META["m"]


def cell_for(sec_key: str):
    if sec_key not in _CELLS:
        _CELLS[sec_key] = c3d.build_cell(_meta()["sections"][sec_key], ridge=True, wall_t=c3d.WALL_T)
    return _CELLS[sec_key]


def search(plan: dict, n1: int = BC["n1"], n2: int = BC["n2"], n: int = BC["n"], k2: int = BC["k2"],
           seed: int = SEED, sig: Optional[dict] = None) -> dict:
    """solver.js bestChance stages 1 to 3 on plan["candidates"] (= robustness.best_chance without stage 4).
    Returns dict(v, theta, from, sets [{name, k, n, p, lo, hi}], mean, n_cand). PREDICTED (see module doc)."""
    err = dict(rb.HC_SIG, **(sig or {}))
    cell, F = cell_for(plan["secKey"]), plan["F"]
    names = list(plan["sets"])
    nS = len(names)
    base = {"S": float(plan["S"]), "h": float(plan["h"]), "z_stop": float(plan["zStop"])}
    n1 = min(n1, n2)
    Zs = rb.mulberry32_normals(seed + 1, 3 * n2).reshape(n2, 3)

    def count(c, nm, Z):
        if len(Z) == 0:
            return 0
        aim = dict(base, v=c["v"], theta=c["theta"])
        return rb.mc_shots(aim, n=len(Z), err=err, cell=cell, frame=F, prm3=plan["sets"][nm], draws=Z)["k_clean"]

    def pooled(c, m):
        k = sum(c["k"])
        lo, hi = rb.wilson(k, m * nS)
        c.update(mean=k / (m * nS), lo=lo, hi=hi)

    C = [{"v": float(c["v"]), "theta": float(c["theta"]), "from": c.get("from", "given")} for c in plan["candidates"]]
    def counts(cs, nm, Z):          # count() for several candidates in one batch (same counts)
        aims = [dict(base, v=c["v"], theta=c["theta"]) for c in cs]
        return rb.mc_cell_counts(aims, Z, err, cell, F, plan["sets"][nm])

    K = [counts(C, nm, Zs[:n1]) for nm in names]
    for i, c in enumerate(C):
        c["k"] = [K[j][i] for j in range(nS)]
        pooled(c, n1)
    best_lo = max(c["lo"] for c in C)
    keep = sorted([c for c in C if c["hi"] >= best_lo], key=lambda c: (-c["mean"], c["v"], c["theta"]))[:k2]
    K = [counts(keep, nm, Zs[n1:n2]) for nm in names]
    for i, c in enumerate(keep):
        c["k"] = [k0 + K[j][i] for j, k0 in enumerate(c["k"])]
        pooled(c, n2)
    keep.sort(key=lambda c: (-c["mean"], c["v"], c["theta"]))
    w = keep[0]
    Z = rb.mulberry32_normals(seed, 3 * n).reshape(n, 3)
    rows = []
    for nm in names:
        k = count(w, nm, Z)
        lo, hi = rb.wilson(k, n)
        rows.append({"name": nm, "k": k, "n": n, "p": k / n, "lo": lo, "hi": hi})
    return {"v": w["v"], "theta": w["theta"], "from": w["from"], "sets": rows,
            "mean": sum(r["p"] for r in rows) / len(rows), "n_cand": len(C), "kept": len(keep)}


def run_plan(plan: dict, **kw) -> dict:
    """One plan -> result record (status ok / illegal pose / no_clean_in_cap)."""
    rec = {k: plan.get(k) for k in ("id", "kind", "x", "y", "h", "S", "set", "side", "d", "psi", "status", "otherHive",
                                    "count", "cells", "inCap")}
    if plan.get("status") != "ok":
        rec["result"] = "pose_" + str(plan.get("status"))
        return rec
    if not plan.get("candidates"):
        rec["result"] = "no_clean_in_cap" if plan.get("count") else "no_clean"
        rec["sets"] = [{"name": nm, "k": 0, "n": 0, "p": 0.0, "lo": 0.0, "hi": 0.0} for nm in plan["sets"]]
        return rec
    t = time.time()
    r = search(plan, **kw)
    rec.update(result="ok", v=r["v"], theta=r["theta"], frm=r["from"], sets=r["sets"], mean=r["mean"],
               n_cand=r["n_cand"], sec=round(time.time() - t, 1))
    return rec


# ---------------------------------------------------------------------------------------------- the sweep
def poses() -> list:
    return [(x, y) for x in X_UNFAV + X_FAV for y in YS]


def jobs_all() -> list:
    J = []
    for (x, y) in poses():
        for h in HS:
            base = {"x": x, "y": y, "h": h, "vu": VU}
            J.append(dict(base, kind="twin", id=f"twin|{x}|{y}|{h}"))
            for S in SS:
                J.append(dict(base, kind="robust", S=S, id=f"robust|{x}|{y}|{h}|{S}"))
                for L in SETS:
                    J.append(dict(base, kind="set", S=S, set=L, id=f"set|{x}|{y}|{h}|{S}|{L}"))
    return J


def _plan_batch(batch: list) -> list:
    return node_plans(batch)


def _run_one(plan: dict) -> dict:
    return run_plan(plan)


def make_plans(work: str, workers: int, verbose: bool = True) -> list:
    path = os.path.join(work, "plans.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    J = jobs_all()
    # legality first (cheap): one pose per (x, y) through the driver's pose check is inside node_plans anyway
    batches = [J[i:i + 13] for i in range(0, len(J), 13)]
    t = time.time()
    with Pool(workers) as pool:
        out = []
        for i, b in enumerate(pool.imap(_plan_batch, batches)):
            out.extend(b)
            if verbose and (i + 1) % 10 == 0:
                print(f"plans {i + 1}/{len(batches)} {time.time() - t:.0f} s", flush=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh)
    return out


def run(work: str, workers: int = 10, verbose: bool = True) -> None:
    os.makedirs(work, exist_ok=True)
    plans = make_plans(work, workers, verbose)
    done_path = os.path.join(work, "results.jsonl")
    done = set()
    if os.path.exists(done_path):
        with open(done_path, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    done.add(json.loads(line)["id"])
    todo = [p for p in plans if p["id"] not in done]
    # S = 1.5 last: every lift set is saturated (Cl = min(c1 S, Cl_max), S_sat = Cl_max / c1 <= 0.75) at S 1.0 and
    # 1.5 alike, so S 1.5 repeats S 1.0 shot for shot (see csv_rows); then biggest first (short pool tail)
    todo.sort(key=lambda p: (p.get("S") == 1.5, -(len(p.get("candidates") or []) * max(1, len(p.get("sets") or {})))))
    if verbose:
        n_ok = sum(1 for p in todo if p.get("candidates"))
        print(f"{len(plans)} plans, {len(done)} done, {len(todo)} to run ({n_ok} with a search)", flush=True)
    t = time.time()
    with Pool(workers) as pool, open(done_path, "a", encoding="utf-8") as fh:
        for i, rec in enumerate(pool.imap_unordered(_run_one, todo)):
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            if verbose and ((i + 1) % 20 == 0 or i + 1 == len(todo)):
                print(f"results {i + 1}/{len(todo)} {time.time() - t:.0f} s", flush=True)


# ---------------------------------------------------------------------------------------------- tables
def rpm(v: float) -> float:
    return v / VU / (math.pi * WHEEL_D) * 60.0


def load_results(work: str) -> dict:
    R = {}
    with open(os.path.join(work, "results.jsonl"), encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                R[r["id"]] = r
    return R


def verdict(sp: dict, tw: dict) -> str:
    """spin / twin / unclear: one Wilson interval wholly above the other, else unclear (same draws, paired)."""
    if sp["n"] and tw["n"]:
        if sp["lo"] > tw["hi"]:
            return "spin"
        if tw["lo"] > sp["hi"]:
            return "twin"
        return "unclear"
    if not sp["n"] and not tw["n"]:
        return "neither"
    if not sp["n"]:
        return "twin" if tw["lo"] > 0 else "neither"
    return "spin" if sp["lo"] > 0 else "neither"


CSV_FIELDS = ["side", "x", "y", "d", "psi_deg", "other_hive_line", "h", "S", "lift_set", "mode",
              "spin_status", "spin_v", "spin_theta", "spin_rpm", "spin_k", "spin_n", "spin_p", "spin_lo", "spin_hi",
              "twin_status", "twin_v", "twin_theta", "twin_rpm", "twin_k", "twin_n", "twin_p", "twin_lo", "twin_hi",
              "dp", "verdict", "computed"]
CSV_HDR = ("# PM-021 backspin vs the no-spin twin by hit chance (src/spin_vs_twin.py). " + LABEL + ". "
           "Live-solver model: 3D flight on the 3D cell, seed 20261031, n = 1000 fresh draws, Wilson 95 %; "
           "settings searched inside the PREDICTED 8.9 m/s grip cap; rpm at the ASSUMED page grip v/u 0.42. "
           "mode robust = one setting for the three lift sets pooled (ASSUMED equal weight), tuned = best setting "
           "for that lift set alone. twin = S 0, no lift, at its own best setting, same draws. "
           "x, y, h, S = ASSUMED sweep; d, psi derived; status no_clean_in_cap = no clean setting at or below the "
           "cap (chance 0). verdict: spin / twin = Wilson intervals do not overlap; unclear = they overlap. "
           "computed: run, or copied from S 1.0 for S 1.5 (every lift set saturated, Cl = min(c1 S, Cl_max): "
           "identical flight; checked on the S 1.5 jobs that were run).\n")


def _blank(prefix: str, rec: Optional[dict]) -> dict:
    st = "pose_illegal" if rec is None else rec["result"]
    return {prefix + "_status": st, prefix + "_v": "", prefix + "_theta": "", prefix + "_rpm": "", prefix + "_k": 0,
            prefix + "_n": 0, prefix + "_p": 0.0, prefix + "_lo": 0.0, prefix + "_hi": 0.0}


def _part(prefix: str, rec: dict, row: Optional[dict]) -> dict:
    if rec["result"] != "ok" or row is None:
        return _blank(prefix, rec)
    return {prefix + "_status": "ok", prefix + "_v": round(rec["v"], 4), prefix + "_theta": round(rec["theta"], 4),
            prefix + "_rpm": round(rpm(rec["v"])), prefix + "_k": row["k"], prefix + "_n": row["n"],
            prefix + "_p": round(row["p"], 4), prefix + "_lo": round(row["lo"], 4), prefix + "_hi": round(row["hi"], 4)}


def _get(R: dict, key: str, key_s1: str, S: float) -> tuple:
    """The result for key; for S 1.5 not run, the S 1.0 result (same flight: lift saturated in every set)."""
    if key in R:
        return R[key], "run"
    if S == 1.5 and key_s1 in R:
        return R[key_s1], "S1.0 (Cl saturated: identical flight)"
    return None, ""


def saturation_check(R: dict) -> tuple:
    """(pairs, identical): S 1.5 results run in full vs the S 1.0 result of the same job (same k in every set)."""
    n = same = 0
    for k, r in R.items():
        if r.get("S") == 1.5 and r.get("result") == "ok":
            parts = k.split("|")          # kind|x|y|h|S[|set]: swap the S field only (x 1.55 also holds "|1.5")
            parts[4] = "1.0"
            k1 = "|".join(parts)
            if k1 in R and R[k1].get("result") == "ok":
                n += 1
                same += int([s["k"] for s in r["sets"]] == [s["k"] for s in R[k1]["sets"]] and
                            (r["v"], r["theta"]) == (R[k1]["v"], R[k1]["theta"]))
    return n, same


def csv_rows(R: dict) -> list:
    rows = []
    for (x, y) in poses():
        for h in HS:
            tw = R.get(f"twin|{x}|{y}|{h}")
            if tw is None or not str(tw.get("result", "")).startswith(("ok", "no_clean")):
                continue
            twp = _part("twin", tw, tw["sets"][0] if tw.get("sets") else None)
            for S in SS:
                rob, rob_from = _get(R, f"robust|{x}|{y}|{h}|{S}", f"robust|{x}|{y}|{h}|1.0", S)
                for L in SETS:
                    tun, tun_from = _get(R, f"set|{x}|{y}|{h}|{S}|{L}", f"set|{x}|{y}|{h}|1.0|{L}", S)
                    for mode, rec, frm in (("robust", rob, rob_from), ("tuned", tun, tun_from)):
                        if rec is None:
                            continue
                        sr = next((s for s in rec.get("sets", []) if s["name"] == L), None)
                        sp = _part("spin", rec, sr)
                        row = {"side": tw["side"], "x": x, "y": y, "d": round(tw["d"], 4), "psi_deg": round(tw["psi"], 2),
                               "other_hive_line": int(bool(tw.get("otherHive"))), "h": h, "S": S, "lift_set": L,
                               "mode": mode, "computed": frm}
                        row.update(sp)
                        row.update(twp)
                        row["dp"] = round(row["spin_p"] - row["twin_p"], 4)
                        row["verdict"] = verdict({"n": row["spin_n"], "lo": row["spin_lo"], "hi": row["spin_hi"]},
                                                 {"n": row["twin_n"], "lo": row["twin_lo"], "hi": row["twin_hi"]})
                        rows.append(row)
    return rows


def write_csv(rows: list, path: str = CSV_OUT) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        fh.write(CSV_HDR)
        w = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def read_csv(path: str = CSV_OUT) -> list:
    with open(path, encoding="utf-8") as fh:
        lines = [ln for ln in fh if not ln.startswith("#")]
    out = []
    for r in csv.DictReader(lines):
        for k in ("x", "y", "d", "psi_deg", "h", "S", "spin_p", "spin_lo", "spin_hi", "twin_p", "twin_lo", "twin_hi", "dp"):
            r[k] = float(r[k])
        for k in ("spin_n", "twin_n", "spin_k", "twin_k", "other_hive_line"):
            r[k] = int(r[k])
        out.append(r)
    return out


def summary(rows: list) -> str:
    """Plain-text tables: per side, mode, lift set and S, the count of poses (x, y, h) where spin / twin wins,
    the median and best chances."""
    lines = []
    for side in ("unfav", "fav"):
        for mode in ("robust", "tuned"):
            lines.append(f"== side {side}, mode {mode}  (poses = legal (x, y, h); chance in %)")
            lines.append("S    set      spin>twin twin>spin unclear neither | spin med/max  twin med/max | "
                         "poses spin>=50% twin>=50%")
            for S in SS:
                for L in SETS:
                    rr = [r for r in rows if r["side"] == side and r["mode"] == mode and r["S"] == S and r["lift_set"] == L]
                    if not rr:
                        continue
                    c = {k: sum(1 for r in rr if r["verdict"] == k) for k in ("spin", "twin", "unclear", "neither")}
                    sp = sorted(r["spin_p"] for r in rr)
                    tw = sorted(r["twin_p"] for r in rr)
                    med = lambda a: a[len(a) // 2]  # noqa: E731
                    lines.append(f"{S:<4} {L:<8} {c['spin']:>9} {c['twin']:>9} {c['unclear']:>7} {c['neither']:>7} | "
                                 f"{100 * med(sp):5.1f}/{100 * sp[-1]:5.1f}  {100 * med(tw):5.1f}/{100 * tw[-1]:5.1f} | "
                                 f"{len(rr):>5} {sum(1 for x in sp if x >= 0.5):>9} {sum(1 for x in tw if x >= 0.5):>9}")
    return "\n".join(lines)


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["run", "csv", "summary"])
    ap.add_argument("--work", default=os.path.join(tempfile.gettempdir(), "spin_vs_twin_work"))
    ap.add_argument("--workers", type=int, default=10)
    a = ap.parse_args(argv)
    if a.cmd == "run":
        run(a.work, a.workers)
    elif a.cmd == "csv":
        R = load_results(a.work)
        rows = csv_rows(R)
        write_csv(rows)
        n, same = saturation_check(R)
        print(f"{len(rows)} rows -> data/spin_vs_twin.csv; S 1.5 vs S 1.0 identical in {same}/{n} pairs run")
    else:
        print(summary(read_csv()))


if __name__ == "__main__":
    main()
