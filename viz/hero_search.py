"""Find the most robust clean backspin entry from the unfavourable side (PM-001 video shot).

Physics: src/flight.py (drag + Magnus + spin decay, cross-checked against an independent RK4
solver, 24/24 cases) with the literature-graded parameters in research/params_lit.json.
Geometry: data/hive_geometry.json (official CAD section, tilt 30 deg confirmed). Classifier:
src/hive.py (ball-centre configuration space, ball radius 35.5 mm). Nothing here is measured.

For each release distance d (m from the pivot plane) and ball-centre release height h, the
script scans (v, elevation) with exit spin S = 1.06 (hood nominal, research/params_lit.json
launcher.S_exit_hood). It keeps launches the hood can deliver (v <= V_CAP) and picks the one
with the most clean neighbours (robustness), breaking ties by obstacle clearance. It reports
the no-spin twin and the same launch under the other aero bounds.

    python viz/hero_search.py                      # -> viz/hero_search.json + viz/cases_hero.json
"""
import json
import math
import os
import sys

import numpy as np

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src import flight  # noqa: E402
from src import hive  # noqa: E402

LIT = os.path.join(ROOT, "research", "params_lit.json")
V_CAP = 8.9            # predicted hood grip cap, docs/04_launcher.md
S_HOOD = 1.06          # research/params_lit.json launcher.S_exit_hood.nominal (theory, grade B)
WHEEL_D = 0.098        # user: 98 mm flywheel
V_OVER_U = (0.30, 0.42, 0.50)   # research/params_lit.json launcher.v_over_surface_speed (grade C)
POSE = "pose_pos"      # the unfavourable shooter is on the side opposite favorable_side
AERO = {
    "nominal": {"Cd": "nominal", "Cl": "nominal", "spin_decay_k": "nominal"},
    "Cl_floor": {"Cd": "nominal", "Cl": "floor", "spin_decay_k": "nominal"},
    "Cl_low": {"Cd": "nominal", "Cl": "low", "spin_decay_k": "nominal"},
    "Cl_high": {"Cd": "nominal", "Cl": "high", "spin_decay_k": "nominal"},
    "Cd_low": {"Cd": "low", "Cl": "nominal", "spin_decay_k": "nominal"},
    "Cd_high": {"Cd": "high", "Cl": "nominal", "spin_decay_k": "nominal"},
}


def params(which):
    return flight.load_params(LIT, which)


GEOM = hive.load_geometry()
FAV = GEOM["poses"][POSE]["favorable_side"]
SHOOTER = "pos" if FAV == "neg" else "neg"
SGN = -1.0 if SHOOTER == "neg" else 1.0
R = float(GEOM["ball_radius"]["value"])


def shoot(d, h, v, el, S, prm, detail=False):
    x0 = [SGN * d, 0.0, h]
    e = math.radians(el)
    v0 = [-SGN * v * math.cos(e), 0.0, v * math.sin(e)]
    w0 = flight.backspin_omega(v0, S * v / R) if S else [0.0, 0.0, 0.0]
    tr = flight.simulate(x0, v0, w0, prm, t_max=3.0)
    res = hive.classify_detail(tr, POSE, SHOOTER)
    return res if detail else res["result"] if isinstance(res, dict) and "result" in res else res


def outcome(res):
    if isinstance(res, str):
        return res
    for k in ("result", "outcome", "label"):
        if k in res:
            return res[k]
    raise KeyError(f"classify_detail keys: {list(res)}")


def scan(d, h, S, prm, vs, els):
    grid = np.zeros((len(vs), len(els)), bool)
    for i, v in enumerate(vs):
        for j, el in enumerate(els):
            grid[i, j] = outcome(shoot(d, h, v, el, S, prm, detail=True)) == "clean"
    return grid


def best(grid):
    """Clean cell with the most clean cells in its 5x5 neighbourhood (robust centre)."""
    if not grid.any():
        return None, 0
    pad = np.pad(grid.astype(int), 2)
    nb = sum(pad[2 + a:2 + a + grid.shape[0], 2 + b:2 + b + grid.shape[1]]
             for a in range(-2, 3) for b in range(-2, 3))
    nb = np.where(grid, nb, -1)
    i, j = np.unravel_index(np.argmax(nb), nb.shape)
    return (int(i), int(j)), int(nb[i, j])


def rpm_for(v):
    return {f"v/u={k}": round(v / k / (math.pi * WHEEL_D) * 60) for k in V_OVER_U}


def main():
    nom = params(AERO["nominal"])
    vs = np.round(np.arange(6.0, V_CAP + 1e-9, 0.05), 3)
    els = np.round(np.arange(66.0, 82.0 + 1e-9, 0.1), 2)
    out = {"physics": "src/flight.py + research/params_lit.json (literature-graded, NOT measured)",
           "geometry": "data/hive_geometry.json (official CAD, tilt 30 deg)",
           "pose": POSE, "shooter_side": SHOOTER, "S_backspin": S_HOOD, "v_cap": V_CAP,
           "grid": {"v": [float(vs[0]), float(vs[-1]), 0.05], "elev": [float(els[0]), float(els[-1]), 0.1]},
           "rows": []}
    for d, h in [(1.75, 0.5), (1.5, 0.5), (1.2, 0.5), (1.75, 0.737)]:
        g_spin = scan(d, h, S_HOOD, nom, vs, els)
        g_none = scan(d, h, 0.0, nom, vs, els)
        cell, nb = best(g_spin)
        row = {"d": d, "h": h, "n_clean_backspin": int(g_spin.sum()), "n_clean_nospin": int(g_none.sum()),
               "n_both": int((g_spin & g_none).sum()), "cell_area": "0.05 m/s x 0.1 deg"}
        if cell:
            v, el = float(vs[cell[0]]), float(els[cell[1]])
            det = shoot(d, h, v, el, S_HOOD, nom, detail=True)
            row.update({
                "hero": {"v": v, "elev_deg": el, "spin_rpm": round(S_HOOD * v / R * 60 / (2 * math.pi)),
                         "clean_neighbours_of_25": nb, "detail": {k: det[k] for k in det if not hasattr(det[k], "__len__") or isinstance(det[k], str)}},
                "wheel_rpm_needed": rpm_for(v),
                "same_launch_no_spin": outcome(shoot(d, h, v, el, 0.0, nom, detail=True)),
                "same_launch_other_aero": {k: outcome(shoot(d, h, v, el, S_HOOD, params(w), detail=True))
                                           for k, w in AERO.items() if k != "nominal"},
                "window_backspin": {"v": [float(vs[g_spin.any(1)].min()), float(vs[g_spin.any(1)].max())],
                                    "elev": [float(els[g_spin.any(0)].min()), float(els[g_spin.any(0)].max())]},
            })
        out["rows"].append(row)
        print(json.dumps(row, default=str))
    with open(os.path.join(ROOT, "viz", "hero_search.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)

    cases = []
    for r in out["rows"]:
        if "hero" not in r:
            continue
        tag = f"d{int(round(r['d'] * 100))}_h{int(round(r['h'] * 1000))}"
        cases.append({"id": f"HERO_{tag}", "pose": POSE, "side": "unfavorable", "distance": r["d"],
                      "release_z": r["h"], "v": r["hero"]["v"], "elev_deg": r["hero"]["elev_deg"],
                      "S": S_HOOD, "aero_set": "nominal",
                      "title": (f"Backspin POLLEN enters the CELL from the unfavourable side, {r['d']:.2f} m from "
                                f"the pivot ({r['hero']['spin_rpm']} rpm backspin, {r['hero']['v']} m/s at "
                                f"{r['hero']['elev_deg']} deg; literature-graded aero, PREDICTED)")})
    with open(os.path.join(ROOT, "viz", "cases_hero.json"), "w", encoding="utf-8") as fh:
        json.dump({"_note": "Written by viz/hero_search.py. aero_set 'nominal' must be read from "
                            "research/params_lit.json (make_shots.py --aero-path).", "cases": cases}, fh, indent=1)


if __name__ == "__main__":
    main()
