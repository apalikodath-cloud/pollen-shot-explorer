"""Shooter DESIGN TARGETS for a clean HIVE CELL entry (PM-001, user request 2026-10-30).

The team CADs the shooter toward these numbers, so this module does not ask what a hood or
roller can deliver. It asks the reverse question: what ball exit state must the shooter
produce at the release point for POLLEN to drop cleanly into the upward-facing CELL?

Exit state = (exit speed v, launch elevation theta, backspin S = w R / v, release height h,
horizontal distance d from the HIVE pivot plane). For each S, h and d the clean (v, theta)
window is found with the same vectorised RK4 + clearance-raster method as src/feasibility.py
(cross-checked against an independent solver, 24/24 cases), using the literature-graded
parameter ranges in research/params_lit.json. Nothing here is measured.

Robust target: a (v, theta) cell counts only if it is clean under EVERY aero variant for that
spin (Cd low/nominal/high, Cl low/nominal/high, spin decay nominal/high) and every CELL tilt
(28.80 / 30 / 31.77 deg: CAD 30 CONFIRMED, bounds derived, fz.TILT_BOUNDS). Clean = the 3D cell of
src/cell3d.py (side walls, pentagon roof; fz.SWEEP_CELL) on the straight shot, air density
fz.SWEEP_RHO = 1.2041 kg/m^3 (derived still air; PM-019 re-sweep). The centre of the largest all-clean square in that intersection is the
design target; the square's half-size is the exit tolerance the shooter must hold.

    python -m src.shooter_spec            # -> data/spec_*.csv (cached runs in data/_spec_cache)
"""
from __future__ import annotations

import csv
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src import feasibility as fz  # type: ignore
else:
    from . import feasibility as fz

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIT = os.path.join(ROOT, "research", "params_lit.json")
CACHE = os.path.join(ROOT, "data", "_spec_cache")
R_BALL = 0.0355
WHEEL_D = 0.098                    # user: 98 mm flywheel
V_OVER_U = (0.25, 0.30, 0.42, 0.50)  # params_lit launcher.v_over_surface_speed 0.30-0.50 (grade C);
                                     # 0.25 = Sakai & Kitade 2017 low end (research/EXTRA_SOURCES.md)

# design spin levels; negative = topspin (exploratory, HANDOFF scope is backspin)
SPINS = (0.0, 0.5, 1.0, 1.5, -1.0)
# geometries of the cache: the CORE sweep set of src/feasibility.py (3D cell, tilt 30 and the derived
# bounds fz.TILT_BOUNDS 28.80 / 31.77, favourable at 30)
GEOMS = list(fz.CORE_GEOMS)
UNFAV_KEYS = fz.SWEEP_UNFAV_KEYS
TILT_LABEL = f"{fz.TILT_BOUNDS[0]:.2f}/30/{fz.TILT_BOUNDS[1]:.2f}"
# model stamp stored in every cache file: a cache made with another cell model, air density or tilt
# set is stale (moved aside by hand to data/_spec_cache_stale/, gitignored)
MODEL_STAMP = (f"cell={fz.SWEEP_CELL};rho={fz.SWEEP_RHO:.5f};tilts={fz.TILT_BOUNDS[0]:g},30,"
               f"{fz.TILT_BOUNDS[1]:g};dt=0.002")


def grid() -> fz.SweepGrid:
    # unfavourable clean windows in the earlier wide sweep (data/clean_feasibility_map.csv)
    # never went below 68 deg or 5.3 m/s, so the search box starts a margin below that
    return fz.SweepGrid(v=np.round(np.arange(5.0, 10.5001, 0.05), 3),
                        theta=np.round(np.arange(62.0, 88.0001, 0.1), 2),
                        h=np.array([0.20, 0.35, 0.50, 0.65, 0.737]),
                        d=np.round(np.arange(0.60, 1.7501, 0.05), 3))


def variants(S: float) -> list:
    """Aero variants for one spin level (one changed at a time from nominal)."""
    V = [("nominal", "nominal", "nominal", "nominal"),
         ("Cd_low", "low", "nominal", "nominal"), ("Cd_high", "high", "nominal", "nominal")]
    if S != 0.0:
        V += [("Cl_low", "nominal", "low", "nominal"), ("Cl_high", "nominal", "high", "nominal"),
              ("k_high", "nominal", "nominal", "high")]
    return V


def jobs() -> list:
    # nominal runs first so the headline numbers land early
    J = [(S, *v) for S in SPINS for v in variants(S)]
    return sorted(J, key=lambda j: j[1] != "nominal")


def tag(S: float, var: str) -> str:
    return f"S{S:+.1f}_{var}"


def _cache_ok(path: str) -> bool:
    """A cached run counts only if it was made on the current grid and model (MODEL_STAMP)."""
    if not os.path.exists(path):
        return False
    g = grid()
    with np.load(path) as z:
        if "model" not in z.files or str(z["model"]) != MODEL_STAMP:
            return False
        return (all(f"{k}__clean" in z.files for k in UNFAV_KEYS)
                and z["unfav_t30__clean"].shape == (len(g.h), len(g.d), len(g.v), len(g.theta)))


def _run(job):
    S, var, Cd, Cl, k = job
    path = os.path.join(CACHE, tag(S, var) + ".npz")
    if _cache_ok(path):
        return tag(S, var), 0.0
    t0 = time.time()
    prm = fz.aero_case(tag(S, var), Cd=Cd, Cl=None if S == 0.0 else Cl, k=k, path=LIT)
    geoms = [fz.Geometry.make(**g) for g in GEOMS]
    res = fz.run_family(prm, S, grid(), geoms, block=2000, chunk_elems=1_500_000)
    arrs = {"model": np.array(MODEL_STAMP)}
    for gk, dd in res.items():
        if gk == "_paths":
            continue
        arrs[f"{gk}__clean"] = dd["clean"]
        arrs[f"{gk}__margin"] = dd["margin"]
        arrs[f"{gk}__ang"] = dd["ang"]
    tmp = path[:-4] + ".tmp.npz"
    np.savez_compressed(tmp, **arrs)
    os.replace(tmp, path)
    return tag(S, var), round(time.time() - t0, 1)


def run_all(workers: int = 6) -> None:
    os.makedirs(CACHE, exist_ok=True)
    for g in GEOMS:
        fz.Geometry.make(**g)          # build the 3D clearance rasters once (disk cache) before the pool
    js = jobs()
    with ProcessPoolExecutor(workers) as ex:
        for name, sec in ex.map(_run, js, chunksize=1):
            print(f"{name}: {sec}s", flush=True)


def load(S: float, var: str) -> dict:
    with np.load(os.path.join(CACHE, tag(S, var) + ".npz")) as z:
        return {k: z[k] for k in z.files}


# --------------------------------------------------------------------------- spec extraction
def wheel_rpm(v: float) -> list:
    return [round(v / r / (math.pi * WHEEL_D) * 60) for r in V_OVER_U]


def spin_rpm(S: float, v: float) -> int:
    return int(round(abs(S) * v / R_BALL * 60 / (2 * math.pi)))


def best_square(c: np.ndarray):
    """Largest all-True k x k block in a 2D mask: (k, i0, j0) or (0, None, None)."""
    nv, nt = c.shape
    P = np.zeros((nv + 1, nt + 1), np.int32)
    P[1:, 1:] = c.astype(np.int32).cumsum(0).cumsum(1)
    best = (0, None, None)
    k = 1
    while k <= min(nv, nt):
        w = P[k:, k:] - P[:-k, k:] - P[k:, :-k] + P[:-k, :-k]
        hit = np.argwhere(w == k * k)
        if hit.size == 0:
            break
        # prefer the block nearest the middle of all hits (stable, not edge-hugging)
        mid = hit.mean(axis=0)
        i0, j0 = hit[np.argmin(((hit - mid) ** 2).sum(1))]
        best = (k, int(i0), int(j0))
        k += 1
    return best


ELEV_TOLS = (0.2, 0.5, 1.0)  # deg: hood-angle tolerance the CAD might hold (assumed choices)


def fixed_elev(mask, margin, g, tol_deg):
    """Speed window for a hood set at one elevation that holds +/- tol_deg.

    A v cell counts only if it is clean at every elevation in [e - tol, e + tol]. Returns
    (elev, v_lo, v_hi, min_margin) for the elevation with the longest contiguous v run
    (ties: larger worst-case margin), or None. The clean windows are thin diagonal bands in
    (v, elevation), so this is the tolerance a fixed hood actually sees: elevation is set by
    the CAD, exit speed varies shot to shot.
    """
    dth = float(g.theta[1] - g.theta[0])
    k = int(round(tol_deg / dth))
    nv, nt = mask.shape
    if nt < 2 * k + 1:
        return None
    # AND over a sliding elevation window of 2k+1 columns (cumulative-sum trick)
    P = np.zeros((nv, nt + 1), np.int32)
    P[:, 1:] = mask.astype(np.int32).cumsum(1)
    W = (P[:, 2 * k + 1:] - P[:, :nt - 2 * k]) == 2 * k + 1      # columns j = k .. nt-k-1
    best = None
    for jj in np.nonzero(W.any(0))[0]:
        col = W[:, jj]
        edges = np.diff(np.concatenate(([0], col.astype(np.int8), [0])))
        starts, ends = np.nonzero(edges == 1)[0], np.nonzero(edges == -1)[0]
        L = ends - starts
        r = int(np.argmax(L))
        i0, i1 = int(starts[r]), int(ends[r])                   # v rows i0 .. i1-1
        j = jj + k
        mm = float(np.nanmin(margin[i0:i1, j - k:j + k + 1])) if margin is not None else 0.0
        key = (i1 - i0, mm)
        if best is None or key > best[0]:
            best = (key, (float(g.theta[j]), float(g.v[i0]), float(g.v[i1 - 1]), mm))
    return None if best is None else best[1]


def describe(mask, margin, ang, g, S, h, d, label, extra=None):
    """One spec row for a clean (v, theta) mask."""
    n = int(mask.sum())
    row = {"S": S, "spin": "none" if S == 0 else ("backspin" if S > 0 else "topspin"),
           "h_m": h, "d_m": d, "basis": label, "n_clean": n}
    if extra:
        row.update(extra)
    if n == 0:
        return row
    vi = np.nonzero(mask.any(1))[0]
    ti = np.nonzero(mask.any(0))[0]
    k, i0, j0 = best_square(mask)
    ic, jc = i0 + (k - 1) / 2, j0 + (k - 1) / 2
    vc = float(np.interp(ic, np.arange(len(g.v)), g.v))
    tc = float(np.interp(jc, np.arange(len(g.theta)), g.theta))
    blk = (slice(i0, i0 + k), slice(j0, j0 + k))
    dv, dth = float(g.v[1] - g.v[0]), float(g.theta[1] - g.theta[0])
    row.update({
        "v_min": float(g.v[vi[0]]), "v_max": float(g.v[vi[-1]]),
        "elev_min": float(g.theta[ti[0]]), "elev_max": float(g.theta[ti[-1]]),
        "target_v": round(vc, 3), "target_elev": round(tc, 2),
        "tol_v_pm": round((k - 1) / 2 * dv, 3), "tol_elev_pm": round((k - 1) / 2 * dth, 2),
        "square_cells": k,
        "target_margin_mm": round(1000 * float(np.nanmin(margin[blk])), 1) if margin is not None else "",
        "descent_deg": round(float(np.nanmean(ang[blk])), 1) if ang is not None else "",
        "spin_rpm": spin_rpm(S, vc),
        **{f"wheel_rpm_vu{int(round(r * 100)):03d}": w
           for r, w in zip(V_OVER_U, wheel_rpm(vc))},
    })
    for t in ELEV_TOLS:
        fe = fixed_elev(mask, margin, g, t)
        if fe is None:
            continue
        e, lo, hi, mm = fe
        tg = _tol_tag(t)
        row.update({f"hood{tg}_elev": round(e, 2), f"hood{tg}_v": round((lo + hi) / 2, 3),
                    f"hood{tg}_tol_v_pm": round((hi - lo) / 2, 3),
                    f"hood{tg}_margin_mm": round(1000 * mm, 1)})
    return row


def _tol_tag(t: float) -> str:
    return f"{int(round(t * 10)):02d}"     # 0.2 deg -> "02", 1.0 deg -> "10"


def spec_rows() -> tuple:
    g = grid()
    nominal_rows, robust_rows = [], []
    for S in SPINS:
        runs = {var: load(S, var) for var, *_ in variants(S)
                if _cache_ok(os.path.join(CACHE, tag(S, var) + ".npz"))}
        if "nominal" not in runs:
            continue
        nom = runs["nominal"]
        for ih, h in enumerate(g.h):
            for idd, d in enumerate(g.d):
                for side, gk in (("unfavorable", "unfav_t30"), ("favorable", "fav_t30")):
                    m = nom[f"{gk}__clean"][ih, idd]
                    nominal_rows.append(describe(
                        m, nom[f"{gk}__margin"][ih, idd], nom[f"{gk}__ang"][ih, idd], g, S,
                        float(h), float(d), f"{side}, nominal aero, tilt 30, 3D cell",
                        {"side": side}))
                # robust: unfavourable side, every aero variant x every tilt bound
                inter = np.ones_like(nom["unfav_t30__clean"][ih, idd])
                mg = np.full(inter.shape, np.inf, np.float32)
                for arr in runs.values():
                    for gk in UNFAV_KEYS:
                        inter &= arr[f"{gk}__clean"][ih, idd]
                        mg = np.fmin(mg, arr[f"{gk}__margin"][ih, idd])
                robust_rows.append(describe(
                    inter, np.where(inter, mg, np.nan), nom["unfav_t30__ang"][ih, idd], g, S,
                    float(h), float(d),
                    f"unfavorable, all {len(runs)} aero variants x tilt {TILT_LABEL}",
                    {"side": "unfavorable", "n_variants": f"{len(runs)}/{len(variants(S))}"}))
    return nominal_rows, robust_rows


FIELDS = ["side", "spin", "S", "h_m", "d_m", "basis", "n_variants", "n_clean", "target_v",
          "tol_v_pm", "target_elev", "tol_elev_pm", "square_cells", "v_min", "v_max",
          "elev_min", "elev_max", "target_margin_mm", "descent_deg", "spin_rpm",
          "wheel_rpm_vu025", "wheel_rpm_vu030", "wheel_rpm_vu042", "wheel_rpm_vu050"] + [
          f"hood{_tol_tag(t)}_{c}" for t in ELEV_TOLS for c in ("elev", "v", "tol_v_pm", "margin_mm")]
HEADER = ("PREDICTED shooter exit targets (src/shooter_spec.py; literature-graded aero "
          "research/params_lit.json (ASSUMED) with rho 1.2041 (derived still air); 3D HIVE cell (side walls; "
          "pentagon roof); CAD tilt 30 (CONFIRMED) with derived bounds 28.80 / 31.77; grid v 0.05 m/s x elev 0.1 deg). "
          "d = horizontal distance release point -> HIVE pivot plane; h = ball-centre release "
          "height above tiles. target_* = centre of the largest all-clean square; tol_*_pm = "
          "its half-size (what the shooter must hold). wheel_rpm_vuXXX = 98 mm wheel rpm if "
          "exit speed / wheel surface speed = 0.25/0.30/0.42/0.50 (hood slip, grade C). "
          "hoodXX_* = fixed hood elevation held to +/-0.XX deg (02 = 0.2, 05 = 0.5, 10 = 1.0): "
          "the elevation with the widest exit-speed window clean at every elevation in that band, "
          "its centre speed, +/- speed tolerance and worst-case clearance.")


# --------------------------------------------------------------------------- tunable spec
def longest_run(m: np.ndarray):
    """Longest run of True along the last axis: (length, centre index); centre is nan if none."""
    L = np.zeros(m.shape, np.int32)
    for i in range(m.shape[-1]):
        L[..., i] = np.where(m[..., i], (L[..., i - 1] + 1) if i else 1, 0)
    n = L.max(-1)
    centre = np.where(n > 0, L.argmax(-1) - (n - 1) / 2, np.nan)
    return n, centre


def tunable_rows(band_deg: float = 0.2) -> list:
    """Fixed hood, wheel speed tuned on the field (unfavourable side).

    A condition is one aero variant x one tilt bound (the real ball and field are each one fixed,
    unknown condition). For hood elevation t held to +/-band_deg, each condition needs a speed run
    that is clean at every elevation in the band. Feasible when every condition has one; the hood is
    the elevation with the widest worst-case run. tune_v_min..max = spread of the per-condition run
    centres (the speed range the shooter must be able to dial in); tol_v_pm = (narrowest run - 1
    cell) / 2, the same convention as describe()."""
    g = grid()
    dv = float(g.v[1] - g.v[0])
    nb = int(round(band_deg / float(g.theta[1] - g.theta[0])))
    rows = []
    for S in SPINS:
        vs = [v for v, *_ in variants(S) if _cache_ok(os.path.join(CACHE, tag(S, v) + ".npz"))]
        W, C = [], []
        for var in vs:
            z = load(S, var)
            for gk in UNFAV_KEYS:
                c = z[f"{gk}__clean"]                          # h, d, v, theta
                ok = np.zeros_like(c)
                for j in range(nb, c.shape[-1] - nb):
                    ok[..., j] = c[..., j - nb:j + nb + 1].all(-1)
                n, cen = longest_run(np.moveaxis(ok, -1, -2))  # -> h, d, theta
                W.append(n)
                C.append(cen)
        W, C = np.array(W), np.array(C)
        wmin = W.min(0)
        for ih, h in enumerate(g.h):
            for idd, d in enumerate(g.d):
                r = {"S": S, "spin": "none" if S == 0 else ("backspin" if S > 0 else "topspin"),
                     "h_m": float(h), "d_m": float(d), "band_deg": band_deg,
                     "n_conditions": len(W)}
                w = wmin[ih, idd]
                if (w > 0).any():
                    with np.errstate(invalid="ignore"):
                        spread = np.nanmax(C[:, ih, idd], 0) - np.nanmin(C[:, ih, idd], 0)
                    ti = int(np.argmax(np.where(w > 0, w * 1000 - spread, -np.inf)))
                    cc = C[:, ih, idd, ti]
                    r.update(hood_elev=round(float(g.theta[ti]), 2),
                             tune_v_min=round(float(g.v[0] + cc.min() * dv), 3),
                             tune_v_max=round(float(g.v[0] + cc.max() * dv), 3),
                             tol_v_pm=round((float(w[ti]) - 1) / 2 * dv, 3))
                rows.append(r)
    return rows


TUNE_FIELDS = ["spin", "S", "h_m", "d_m", "band_deg", "n_conditions", "hood_elev",
               "tune_v_min", "tune_v_max", "tol_v_pm"]
TUNE_HEADER = ("PREDICTED fixed-hood / field-tuned speed spec for the unfavourable side "
               "(src/shooter_spec.py tunable_rows; 3D cell; rho 1.2041). Conditions = every aero variant x tilt "
               "28.80/30/31.77. Blank hood_elev = no hood elevation works for every condition. "
               "tol_v_pm = 0 means a single 0.05 m/s grid cell is clean.")


def write(path, rows, fields=None, header=HEADER):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        fh.write("# " + header.replace(",", ";") + "\n")
        w = csv.DictWriter(fh, fieldnames=fields or FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--extract-only" not in argv:
        run_all(int(os.environ.get("SPEC_WORKERS", "4")))
    nominal_rows, robust_rows = spec_rows()
    write(os.path.join(ROOT, "data", "spec_nominal.csv"), nominal_rows)
    write(os.path.join(ROOT, "data", "spec_robust.csv"), robust_rows)
    print(f"wrote data/spec_nominal.csv ({len(nominal_rows)} rows), "
          f"data/spec_robust.csv ({len(robust_rows)} rows)")
    tune = tunable_rows(0.2) + tunable_rows(0.5)
    write(os.path.join(ROOT, "data", "spec_tunable.csv"), tune, TUNE_FIELDS, TUNE_HEADER)
    print(f"wrote data/spec_tunable.csv ({len(tune)} rows)")


if __name__ == "__main__":
    main()
