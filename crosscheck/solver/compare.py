"""compare.py - compare ANY trajectory solver against reference_cases.json.

Usage (from the project root):
    python crosscheck/solver/compare.py --adapter my_adapter:run
    python crosscheck/solver/compare.py --adapter crosscheck.solver.compare:example_adapter  (self-demo)

The adapter is a function  run(inputs: dict, params: dict) -> dict  returning
the trajectory sampled densely (dt <= 1e-3 s recommended) from release until
the ball centre is below z = 0 (or at least below the release height):
    {"t": array, "x": array, "z": array, "vx": array, "vz": array}
All SI. `inputs` is a case's "inputs" block; `params` is a flat dict
{m, R, rho, Cd, c1, Cl_max, k_spin, g, wind, eps_v} for that case.

The metrics (apex, crossings, flight time, spin-vs-no-spin dz) are extracted
here with the SAME event code for both solvers, so a mismatch points at the
dynamics, not at post-processing. Tolerances (lead-set: 1 mm on lengths):
    lengths 1e-3 m, times 5e-4 s, velocities 1e-3 m/s.
"""
from __future__ import annotations

import argparse
import importlib
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import xflight as xf  # noqa: E402

TOL = {"len": 1e-3, "time": 5e-4, "vel": 1e-3}


def case_params(meta, inputs):
    P = meta["parameters"]
    return {"m": P["m_kg"][0], "R": P["R_m"][0], "rho": P["rho_kg_m3"][0], "Cd": P["Cd"][0],
            "c1": P["c1"][0], "Cl_max": P["Cl_max"][0], "k_spin": inputs["k_spin_1_s"],
            "g": P["g_m_s2"][0], "wind": inputs["wind_m_s"], "eps_v": P["eps_v_m_s"][0]}


def example_adapter(inputs, params):
    """Demo only: scipy DOP853 on xflight's own physics (proves the harness, NOT src/)."""
    from scipy.integrate import solve_ivp
    p = xf.Params(**{k: (tuple(v) if k == "wind" else v) for k, v in params.items()})
    L = xf.Launch(v0=inputs["v0_m_s"], elev_deg=inputs["elev_deg"], S0=inputs["S0"],
                  z0=inputs["z0_m"], x0=inputs["x0_m"], spin_axis=tuple(inputs["spin_axis"]))
    w0 = xf.omega0_mag(p, L)
    ax = np.asarray(L.spin_axis, float)
    e = math.radians(L.elev_deg)
    s0 = [L.x0, 0, L.z0, L.v0 * math.cos(e), 0, L.v0 * math.sin(e)]
    ev = lambda t, s: s[2] + 0.05
    ev.terminal, ev.direction = True, -1
    sol = solve_ivp(lambda t, s: np.concatenate((s[3:6], xf.accel(t, s, p, w0, ax))),
                    (0, 10), s0, method="DOP853", rtol=1e-11, atol=1e-12,
                    events=ev, dense_output=True)
    t = np.arange(0, sol.t[-1], 5e-4)
    y = sol.sol(t)
    return {"t": t, "x": y[0], "z": y[2], "vx": y[3], "vz": y[5]}


def metrics_from_traj(tr, z0, R):
    t = np.asarray(tr["t"], float)
    X = np.zeros((len(t), 6))
    X[:, 0], X[:, 2], X[:, 3], X[:, 5] = tr["x"], tr["z"], tr["vx"], tr["vz"]
    Ac = np.zeros((len(t), 3))
    Ac[:, 0] = np.gradient(X[:, 3], t, edge_order=2)
    Ac[:, 2] = np.gradient(X[:, 5], t, edge_order=2)
    out = {}
    ap = xf.find_apex(t, X, Ac)
    out["apex"] = None if ap is None else {k: ap[0][k] for k in ("t", "x", "z", "vx")}
    for key, zc in (("z1p0", 1.0), ("z0p3", z0), ("ground_R", R)):
        c = xf.find_descending_crossing(t, X, Ac, zc)
        out[key] = None if c is None else {"t": c["t"], "x": c["x"]}
    out["flight_time_s"] = out["z0p3"]["t"] if out["z0p3"] else None
    return out, (t, X, Ac)


def _cmp(name, ref, got, tol, rows):
    if ref is None or got is None:
        ok = (ref is None) == (got is None)
        rows.append((name, ref, got, None, ok))
        return ok
    d = abs(got - ref)
    ok = d <= tol
    rows.append((name, ref, got, d, ok))
    return ok


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter", required=True, help="module:function")
    ap.add_argument("--cases", default=str(HERE / "reference_cases.json"))
    a = ap.parse_args(argv)
    sys.path.insert(0, str(Path.cwd()))      # allow adapters in the current directory
    mod, fn = a.adapter.split(":")
    run = getattr(importlib.import_module(mod), fn)
    data = json.loads(Path(a.cases).read_text(encoding="utf-8"))
    meta, cases = data["meta"], data["cases"]
    got, trajs = {}, {}
    for c in cases:
        i = c["inputs"]
        tr = run(i, case_params(meta, i))
        got[c["id"]], trajs[c["id"]] = metrics_from_traj(tr, i["z0_m"], meta["parameters"]["R_m"][0])
    nfail, rows = 0, []
    for c in cases:
        r, g = c["outputs"], got[c["id"]]
        rows.append((f"== {c['id']} v={c['inputs']['v0_m_s']} el={c['inputs']['elev_deg']} "
                     f"S0={c['inputs']['S0']} k={c['inputs']['k_spin_1_s']}", None, None, None, True))
        for k, tl in (("t", "time"), ("x", "len"), ("z", "len"), ("vx", "vel")):
            nfail += not _cmp(f"apex.{k}", r["apex"] and r["apex"][k], g["apex"] and g["apex"][k], TOL[tl], rows)
        for key in ("z1p0", "z0p3"):
            nfail += not _cmp(f"{key}.x", r[key] and r[key]["x"], g[key] and g[key]["x"], TOL["len"], rows)
        nfail += not _cmp("flight_time_s", r["flight_time_s"], g["flight_time_s"], TOL["time"], rows)
        if c["id"] != c["twin_id"]:
            A, B = trajs[c["id"]], trajs[c["twin_id"]]
            d = xf.twin_difference(A, B, g["flight_time_s"], got[c["twin_id"]]["flight_time_s"])
            rs = r["spin_vs_nospin"]
            for mode, loc in (("equal_x", "x_m"), ("equal_t", "t_s")):
                if rs.get(mode) and d.get(mode):
                    nfail += not _cmp(f"dz.{mode}.max", rs[mode]["max_abs_dz_m"], d[mode]["max_abs_dz_m"], TOL["len"], rows)
                    nfail += not _cmp(f"dz.{mode}.{loc}", rs[mode][loc], d[mode][loc],
                                      TOL["len"] if loc == "x_m" else TOL["time"], rows)
    for name, ref, gv, d, ok in rows:
        if ref is None and gv is None and d is None and name.startswith("=="):
            print(name)
        else:
            print(f"  {'PASS' if ok else 'FAIL'} {name:22s} ref={ref!s:>14.12} got={gv!s:>14.12} diff={d!s:.10}")
    print(f"\n{nfail} FAIL(s) over {len(cases)} cases")
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main())
