"""Required vs achievable, Monte Carlo robustness and the "score from anywhere" field map.

HANDOFF section 3 Q4, Q6, Q7; Phase 3 step 9; deliverables 5 and 8.
Writes data/req_vs_ach_*.csv, data/robust_*.csv, figures/req_vs_ach_*.png, figures/map_*.png.
Every output number is PREDICTED (model output from ASSUMED aero bounds, CAD-derived HIVE
geometry and the PREDICTED launcher envelope). Nothing here is validated by a measured shot.

Inputs (read only)
------------------
data/clean_feasibility_map.csv   required clean (v, elevation) windows per aero case (feasibility.py)
data/launch_envelope.json        achievable (v_exit, spin, S) per launcher config (launcher.py)
--aero-path file                 Cd / Cl / k bounds (ASSUMED; default research/params_lit.json)
data/hive_geometry.json          HIVE section, tilt bounds, field extents

Step 1 (required vs achievable). For each aero case, geometry, release height h and distance
d with a clean window, the required v range and spin (S, rpm = S v / R * 60 / 2 pi) are
compared with each launcher's predicted v cap and S band. Gaps are reported in m/s, in S and
in spin rpm. Because Cl = min(c1 S, Cl_max) saturates at S_sat = Cl_max / c1 (0.50 - 0.71,
derived), every S >= S_sat gives the same lift: a launcher S of 1.03 - 1.27 "matches" any
required S >= S_sat of the same Cl set. S = 0 (no spin) is NOT reachable by either launcher
(hood S >= 1.03, passive roller S >= 0.91 in the model) - the drag case is a counterfactual.

Step 2 (Monte Carlo). 3D vectorised RK4 (same equations as flight.simulate: drag + Magnus
on v_rel = v - wind, exponential spin decay) with per-shot ball mass, radius, Cd, Cl, spin S,
wind, release error and HIVE pose error. Each path is classified EXACTLY with a per-shot
hive.Hive (tilt, pivot height, ball radius, lateral roof drop at the gate offset) using
Hive.classify_path; a gate offset |y| > half-width - R is a side-wall hit. Hit probability is
reported with Wilson 95 % intervals.

Step 3 (field map). For a release point at in-plane distance d = |x| from the pivot plane and
lateral offset y from the CELL centre line, the shot is aimed at the gate centre with azimuth
psi = atan(|y| / (d +- x_gate)). With walls extruded along y, the in-plane projection of the
3D path is the 2D path with horizontal coordinates scaled by cos(psi) (exact for extruded
obstacles, no wind). The roof drop of the pentagon section is applied at an ASSUMED effective
lateral offset s_eff = min(0.3 tan(psi), 0.2) m (sensitivity: centre section). The clean mask
(d, v, elevation) is convolved with the nominal release-error Gaussian; P(position) = max
over hardware-allowed (v, elevation) of that probability times a lateral factor
P(|e_y| < w_lat), e_y ~ N(0, sigma_lat). See docs/06_required_vs_achievable.md.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
import tempfile
import time
from typing import Any, Optional

import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.special import erf

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src import feasibility as fz  # type: ignore
    from src import flight as fl  # type: ignore
    from src import hive as hv  # type: ignore
    from src import field_geom as fg  # type: ignore
    from src import air  # type: ignore
    from src import cell3d as c3d  # type: ignore
else:
    from . import feasibility as fz
    from . import flight as fl
    from . import hive as hv
    from . import field_geom as fg
    from . import air
    from . import cell3d as c3d

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(_ROOT, "data")
FIGS = os.path.join(_ROOT, "figures")
G = fl.G_STANDARD
RPM = 60.0 / (2.0 * math.pi)

# --------------------------------------------------------------------------- constants
#: derived (geometry): gate (mouth inside-polygon edge) centre |x| in the shot frame, pose_pos
#: at tilt 30: mean of hive.Hive.gate = ((0.47298, 1.38728), (0.32979, 1.63529)) -> 0.401 m.
X_GATE = 0.401
#: confirmed (Manual TU07 9.6.2 Fig 9-11 via data/hive_geometry.json): CELL half-width 0.254 m.
CELL_HALF = 0.254
#: derived: field extents in the red-HIVE frame. Inner wall |x| = 1.8009 (CAD); along the
#: pivot axis the red HIVE centre is 0.3236 m toward red -> y in [-1.4773, 2.1245].
X_WALL = 1.8009
Y_WALL = (-1.8009 + 0.3236, 1.8009 + 0.3236)
#: CONFIRMED (TU07 9.6.1): A-frame base 38.95 (x) x 49.46 (y) in centred on the field centre
#: -> red frame x in [-0.494665, 0.494665], y in [-0.304542, 0.951742] (src/field_geom.py).
BASE_X = fg.BASE_HALF_X
BASE_Y = (fg.BASE_CY - fg.BASE_HALF_Y, fg.BASE_CY + fg.BASE_HALF_Y)
#: derived box, ASSUMED as blocking (research/GEOMETRY_AUDIT.md fix 5): the other HIVE's plan
#: envelope grown by R, |x| < 0.6745, y 0.3455-0.9495 (src/field_geom.py sight_blocked).
OTHER_HIVE_X = fg.OTHER_HIVE_X
OTHER_HIVE_Y = fg.OTHER_HIVE_Y
#: assumed: release grid stays 0.10 m inside the wall; legality is the robot footprint test
#: (src/field_geom.py chassis_ok: 18 x 18 in, any heading, release at the chassis centre)
WALL_MARGIN = fg.WALL_MARGIN
#: assumed: release points with |x| < 0.55 are not evaluated (HIVE base / under-HIVE region,
#: outside the swept d range) and are counted as P = 0 in the legal area.
X_MIN_EVAL = 0.55
#: assumed: release height for the map = robot height limit (R105, 0.7366 m, ball inside).
H_MAP = 0.737
#: assumed: azimuths beyond 60 deg are treated as infeasible (oblique entry through the side
#: of a 0.508 m wide opening is not represented by the 2D section).
PSI_MAX = 60.0
PSI_BINS = (0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0)

#: Launcher hardware (PREDICTED, data/launch_envelope.json; read at run time). The map uses:
HOOD_KEY = "hood_nominal"
ROLLER_KEY = "roller_nominal_rest"

#: Release-error sets (ASSUMED; no measured repeatability exists - HANDOFF 5: never infer
#: repeatability from one shot). sig_v_rel = shot-to-shot exit-speed spread (wheel rpm
#: control ~1 % plus ball-to-ball ~1 %), sig_th elevation, sig_psi azimuth, sig_d in-plane
#: release position (driving / localisation), sig_y lateral release position.
ERR_SETS = {
    "tight": dict(sig_v_rel=0.005, sig_th=0.15, sig_psi=0.25, sig_d=0.010, sig_y=0.010),
    "nominal": dict(sig_v_rel=0.015, sig_th=0.40, sig_psi=0.50, sig_d=0.025, sig_y=0.025),
    "loose": dict(sig_v_rel=0.030, sig_th=0.80, sig_psi=1.00, sig_d=0.050, sig_y=0.050),
}
#: ASSUMED aleatory physical scatter (per shot) used in the Monte Carlo.
PHYS = dict(
    sig_h=0.005,            # m release height
    mass_sig=0.0005,        # kg; clipped to the aero file mass low/high (assumed)
    radius_sig=0.00025,     # m; clipped to 0.0350-0.0360 (aero file radius low/high, assumed)
    cd_rel=0.05,            # ball-to-ball Cd scatter (perforation / seam orientation)
    cl_rel=0.10,            # ball-to-ball Cl scatter
    S_range=(1.03, 1.27),   # PREDICTED hood S band (launch_envelope reachable_S_summary)
    wind_sig=0.30,          # m/s per horizontal component, constant per shot (indoor drafts)
    tilt_sig=0.75,          # deg, clipped to the derived 28.80-31.77 bounds (TILT_BOUNDS)
    pivot_sig=0.005,        # m, clipped to the 1.0909-1.1417 bounds
    hive_x_sig=0.01,        # m HIVE placement along x
)
#: ASSUMED lateral acceptance half-width at the gate for the map (bounds): ball centre must
#: stay inside the CELL (|y| < 0.254 - R = 0.2185, derived) and the pentagon roof drops toward
#: the walls, so the usable half-width is between ~0.10 and 0.2185 m. Primary value 0.15.
W_LAT = {"low": 0.10, "primary": 0.15, "high": CELL_HALF - 0.0355}

D_GRID = np.round(np.arange(0.55, 1.8001, 0.01), 3)
GRIDS = {
    "unfav": dict(v=np.round(np.arange(4.5, 9.6001, 0.05), 3),
                  th=np.round(np.arange(60.0, 89.9001, 0.1), 3)),
    "fav": dict(v=np.round(np.arange(2.0, 9.6001, 0.05), 3),
                th=np.round(np.arange(20.0, 89.7501, 0.25), 3)),
}
MAP_CASES = ("drag", "S1_Cllow", "S1_Clnominal", "S1_Clhigh")
PROV_HDR = ("# PREDICTED (model output). Aero bounds = ASSUMED (file named in the AERO line); HIVE geometry "
            "= CAD-derived (tilt 30 confirmed, bounds derived); launcher envelope "
            "data/launch_envelope.json = PREDICTED; release-error sets = ASSUMED "
            "(src/robustness.py ERR_SETS/PHYS). Not validated by any measured shot.")


def _write_csv(path: str, rows: list, fields: list, header: str = PROV_HDR) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        for line in header.splitlines():
            fh.write(line if line.startswith("#") else "# " + line)
            fh.write("\n")
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None or (isinstance(r.get(k), float)
                                                        and not math.isfinite(r[k]))
                            else r[k]) for k in fields})


def _read_csv(path: str) -> list:
    with open(path, encoding="utf-8") as fh:
        lines = [ln for ln in fh if not ln.startswith("#")]
    return list(csv.DictReader(lines))


def _f(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return float("nan")


# --------------------------------------------------------------------------- statistics
def wilson(k: int, n: int, z: float = 1.959964) -> tuple:
    """Wilson score interval (lo, hi) for k successes in n trials."""
    if n <= 0:
        return (0.0, 1.0)
    p = k / n
    den = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - h), min(1.0, c + h))


# =========================================================================== step 1
def load_envelope(path: Optional[str] = None) -> dict:
    with open(path or os.path.join(DATA, "launch_envelope.json"), encoding="utf-8") as fh:
        return json.load(fh)


def launcher_curves(env: Optional[dict] = None) -> dict:
    """{config: dict(rpm, v, spin, S, drop arrays; v_cap; S_min; S_max)} (PREDICTED)."""
    env = env or load_envelope()
    out = {}
    for k, c in env["configs"].items():
        pts = c.get("points") or []
        if not pts:
            continue
        a = {q: np.array([_f(p.get(q)) for p in pts]) for q in
             ("wheel_rpm", "v_exit", "spin_rpm", "S", "rpm_drop")}
        out[k] = dict(rpm=a["wheel_rpm"], v=a["v_exit"], spin=a["spin_rpm"], S=a["S"],
                      drop=a["rpm_drop"], v_cap=float(np.nanmax(a["v_exit"])),
                      S_min=float(np.nanmin(a["S"])), S_max=float(np.nanmax(a["S"])),
                      note=c.get("note", ""))
    return out


def rpm_for_v(cur: dict, v: float) -> float:
    """Smallest wheel rpm whose exit speed reaches v (linear interpolation); NaN above cap."""
    vv, rr = cur["v"], cur["rpm"]
    if not np.isfinite(v) or v > cur["v_cap"] + 1e-9:
        return float("nan")
    if v <= vv[0]:
        return float(rr[0] * v / vv[0])
    j = int(np.argmax(vv >= v - 1e-12))
    v0, v1, r0, r1 = vv[j - 1], vv[j], rr[j - 1], rr[j]
    return float(r0 + (r1 - r0) * (v - v0) / max(v1 - v0, 1e-12))


def s_sat(cl_set: str, aero: Optional[dict] = None) -> float:
    """derived: S at which Cl = min(c1 S, Cl_max) saturates = Cl_max / c1."""
    if cl_set in (None, "", "none"):
        return float("nan")
    aero = aero or _aero_raw()
    s = aero["Cl"]["sets"][cl_set]
    return float(s["Cl_max"]) / float(s["c1"])


REQ_LAUNCHERS = ("hood_nominal", "hood_slick_short", "hood_soft_ball", "hood_stiff_ball_8mm",
                 "roller_nominal_rest", "roller_light_rest", "roller_heavy_rest")
REQ_GEOMS = fz.SWEEP_UNFAV_KEYS + (fz.geom_key(True),)   # precomputed at the old tilt bounds (fz.SWEEP_TILT)
REQ_FIELDS = ["launcher", "case", "S_req", "Cl", "geometry", "h", "d", "n_clean_req",
              "v_req_min", "v_req_max", "theta_req_min", "theta_req_max", "spin_rpm_req_min",
              "spin_rpm_req_max", "launcher_v_cap", "launcher_S_min", "launcher_S_max",
              "S_sat_derived", "S_equivalent", "S_gap", "speed_gap_mps", "rpm_gap_ideal",
              "wheel_rpm_at_v_req_min", "launcher_spin_rpm_at_v_req_min", "spin_rpm_gap",
              "v_overlap_lo", "v_overlap_hi", "status"]


def req_vs_ach_rows(map_csv: Optional[str] = None, env: Optional[dict] = None,
                    launchers=REQ_LAUNCHERS) -> list:
    """One row per (launcher, case, geometry, h, d) with a clean window (uncapped v grid)."""
    rows = _read_csv(map_csv or os.path.join(DATA, "clean_feasibility_map.csv"))
    curves = launcher_curves(env)
    aero = _aero_raw()
    ideal = curves.get("hood_ideal_brettle")
    v_per_rpm = float(ideal["v"][0] / ideal["rpm"][0]) if ideal else 2.3488e-3   # derived
    R = float(aero["radius"]["value"])
    out = []
    for r in rows:
        if r["geometry"] not in REQ_GEOMS or abs(_f(r["v_cap"]) - 11.0) > 1e-6:
            continue
        case = r["case"]
        if case == "vacuum" or case.startswith("topspin") or "_Cd" in case or "_k" in case:
            continue
        n = int(_f(r["n_clean"]) or 0)
        if n <= 0:
            continue
        S_req, cl = _f(r["S"]), r["Cl"]
        vmin, vmax = _f(r["v_min"]), _f(r["v_max"])
        ssat = s_sat(cl, aero)
        for lk in launchers:
            c = curves[lk]
            if S_req == 0.0:
                S_eq = False
                S_gap = c["S_min"]                      # launcher cannot reach S = 0
            else:
                lo_ok = c["S_min"] >= ssat - 1e-9 and S_req >= ssat - 1e-9
                in_band = c["S_min"] - 1e-9 <= S_req <= c["S_max"] + 1e-9
                S_eq = bool(lo_ok or in_band)
                S_gap = 0.0 if S_eq else (c["S_min"] - S_req if S_req < c["S_min"]
                                          else S_req - c["S_max"])
            gap = max(0.0, vmin - c["v_cap"])
            wr = rpm_for_v(c, vmin)
            S_l = float(np.interp(vmin, c["v"], c["S"])) if gap == 0 else c["S"][-1]
            v_at = vmin if gap == 0 else c["v_cap"]
            spin_l = S_l * v_at / R * RPM
            spin_req = S_req * vmin / R * RPM
            ol_hi = min(vmax, c["v_cap"])
            if gap > 0:
                status = "speed_gap"
            elif not S_eq:
                status = "spin_gap"
            else:
                status = "reachable"
            out.append(dict(
                launcher=lk, case=case, S_req=S_req, Cl=cl, geometry=r["geometry"],
                h=_f(r["h"]), d=_f(r["d"]), n_clean_req=n, v_req_min=vmin, v_req_max=vmax,
                theta_req_min=_f(r["theta_min"]), theta_req_max=_f(r["theta_max"]),
                spin_rpm_req_min=round(spin_req, 0),
                spin_rpm_req_max=round(S_req * vmax / R * RPM, 0),
                launcher_v_cap=round(c["v_cap"], 3), launcher_S_min=round(c["S_min"], 4),
                launcher_S_max=round(c["S_max"], 4),
                S_sat_derived=round(ssat, 3) if math.isfinite(ssat) else None,
                S_equivalent=S_eq, S_gap=round(S_gap, 4), speed_gap_mps=round(gap, 3),
                rpm_gap_ideal=round(gap / v_per_rpm, 0),
                wheel_rpm_at_v_req_min=None if not math.isfinite(wr) else round(wr, 0),
                launcher_spin_rpm_at_v_req_min=round(spin_l, 0),
                spin_rpm_gap=round(spin_l - spin_req, 0),
                v_overlap_lo=vmin if ol_hi >= vmin else None,
                v_overlap_hi=round(ol_hi, 3) if ol_hi >= vmin else None, status=status))
    return out


SUM_FIELDS = ["launcher", "case", "geometry", "h", "n_d_with_clean_window", "n_d_reachable",
              "d_min_reachable", "d_max_reachable", "min_speed_gap_mps", "max_speed_gap_mps",
              "status_counts"]


def req_vs_ach_summary(rows: list) -> list:
    groups: dict = {}
    for r in rows:
        groups.setdefault((r["launcher"], r["case"], r["geometry"], r["h"]), []).append(r)
    out = []
    for (lk, case, gk, h), rr in sorted(groups.items()):
        ok = [r for r in rr if r["status"] == "reachable"]
        st: dict = {}
        for r in rr:
            st[r["status"]] = st.get(r["status"], 0) + 1
        gaps = [r["speed_gap_mps"] for r in rr]
        out.append(dict(launcher=lk, case=case, geometry=gk, h=h,
                        n_d_with_clean_window=len(rr), n_d_reachable=len(ok),
                        d_min_reachable=min((r["d"] for r in ok), default=None),
                        d_max_reachable=max((r["d"] for r in ok), default=None),
                        min_speed_gap_mps=min(gaps), max_speed_gap_mps=max(gaps),
                        status_counts="; ".join(f"{k}:{v}" for k, v in sorted(st.items()))))
    return out


# =========================================================================== 3D integrator
def integrate3d(p0: np.ndarray, v0: np.ndarray, w0: np.ndarray, prm: dict,
                wind: Optional[np.ndarray] = None, dt: float = 2e-3, t_max: float = 2.5,
                z_stop: float = 0.4, eps_v: float = 1e-6, dtype=np.float32) -> dict:
    """Vectorised fixed-step RK4 of N independent shots (same physics as flight.simulate).

    p0, v0, w0: (N, 3) position, velocity, spin vector (rad/s). prm: dict of scalars or (N,)
    arrays: rho, mass, radius, Cd, c1, clmax (Cl = min(c1 S, clmax); c1 = 0 -> no Magnus),
    k (spin decay 1/s). wind: (N, 3) constant per shot. Stops once every shot is below z_stop
    and descending. Returns dict(P (N, T, 3), V (N, T, 3) of dtype (float32 default), t (T,)).

    Optional terms (all default off; physics.js makeAcc3 is the JS twin, PM-016): nu, cd_model (+ cd_sub,
    cd_post, re1, re2), dcd_spin (+ s_sat), cl_table / cl_rev (+ re_rev, s_rev) through air.cl_of, eps_mass
    (dv/dt = (F/m + g) / (1 + eps)) and s_perp (S = |w x v| R / |v|^2, gyro-correct).
    """
    p = np.array(p0, float)
    v = np.array(v0, float)
    w0 = np.array(w0, float)
    N = p.shape[0]

    def col(key, default=0.0):
        return np.broadcast_to(np.asarray(prm.get(key, default), float), (N,)).copy()

    rho, m, R, cd = col("rho"), col("mass"), col("radius"), col("Cd")
    c1, clmax, k = col("c1"), col("clmax"), col("k")
    q = 0.5 * rho * math.pi * R * R / m
    u = np.zeros((N, 3)) if wind is None else np.asarray(wind, float).reshape(N, 3)
    wmag0 = np.linalg.norm(w0, axis=1)
    use_m = bool(np.any((c1 > 0) & (wmag0 > 0) & (rho > 0)))
    ext = air.has_ext(prm) or bool(prm.get("s_perp"))

    def acc(t, vel):
        vr = vel - u
        sp2 = np.einsum("ij,ij->i", vr, vr)
        sp = np.sqrt(sp2)
        a = -(q * cd * sp)[:, None] * vr
        if use_m:
            dec = np.exp(-k * t)
            w = w0 * dec[:, None]
            wm = wmag0 * dec
            S = wm * R / np.sqrt(sp2 + eps_v * eps_v)
            cl = np.minimum(c1 * S, clmax)
            cx = np.cross(w, vr)
            den = np.sqrt(np.einsum("ij,ij->i", cx, cx) + (eps_v * wm) ** 2)
            km = np.where(den > 0, q * cl * sp2 / np.where(den > 0, den, 1.0), 0.0)
            a = a + km[:, None] * cx
        a[:, 2] -= G
        return a

    if ext:
        nu = float(prm.get("nu", fl.NU_AIR_DEFAULT))
        dcd = float(prm.get("dcd_spin", 0.0) or 0.0)
        ssat = float(prm.get("s_sat", air.S_SAT_DEFAULT))
        ie = 1.0 / (1.0 + float(prm.get("eps_mass", 0.0) or 0.0))
        sperp = bool(prm.get("s_perp", False))
        spin = wmag0 > 0
        lift = bool(np.any(spin & (rho > 0))) and (bool(np.any(c1 > 0)) or air.lift_on(prm))
        popt = {kk: prm[kk] for kk in ("cl_table", "cl_rev", "re_rev", "s_rev") if kk in prm}
        pcd = dict(prm, Cd=cd)

        def acc(t, vel):  # noqa: F811
            vr = vel - u
            sp2 = np.einsum("ij,ij->i", vr, vr)
            sp = np.sqrt(sp2)
            re = sp * (2.0 * R) / nu
            cde = air.cd_base(pcd, re) * np.ones(N)
            dec = np.exp(-k * t)
            w = w0 * dec[:, None]
            wm = wmag0 * dec
            cx = np.cross(w, vr)
            cm2 = np.einsum("ij,ij->i", cx, cx)
            if sperp:
                S = np.sqrt(cm2) * R / (sp2 + eps_v * eps_v)
            else:
                S = wm * R / np.sqrt(sp2 + eps_v * eps_v)
            S = np.where(spin, S, 0.0)
            if dcd != 0.0:
                cde = cde + np.where(spin, dcd * np.minimum(S / ssat, 1.0), 0.0)
            a = -(q * cde * sp)[:, None] * vr
            if lift:
                cl = air.cl_of(popt, S, re, (c1, clmax))
                cm = np.sqrt(cm2)
                km = np.where(cm > 0, q * cl * sp2 / np.where(cm > 0, cm, 1.0), 0.0)
                a = a + km[:, None] * cx
            a[:, 2] -= G
            return a * ie

    nT = int(math.ceil(t_max / dt)) + 1
    P = np.zeros((N, nT, 3), dtype)
    V = np.zeros((N, nT, 3), dtype)
    P[:, 0], V[:, 0] = p, v
    t = 0.0
    last = nT - 1
    for n in range(1, nT):
        a1 = acc(t, v)
        a2 = acc(t + dt / 2, v + dt / 2 * a1)
        a3 = acc(t + dt / 2, v + dt / 2 * a2)
        a4 = acc(t + dt, v + dt * a3)
        p = p + dt * (v + dt / 6 * (a1 + a2 + a3))
        v = v + dt / 6 * (a1 + 2 * a2 + 2 * a3 + a4)
        t += dt
        P[:, n], V[:, n] = p, v
        if n % 25 == 0 and np.all((p[:, 2] < z_stop) & (v[:, 2] < 0)):
            last = n
            break
    return {"P": P[:, :last + 1], "V": V[:, :last + 1], "t": np.arange(last + 1) * dt}


def backspin_axis(v0: np.ndarray) -> np.ndarray:
    """Unit backspin axes for launch velocities (N, 3): unit(v x z_hat) (flight convention)."""
    ax = np.cross(v0, np.array([0.0, 0.0, 1.0]))
    return ax / np.linalg.norm(ax, axis=1, keepdims=True)


# =========================================================================== Monte Carlo
def _aero_raw() -> dict:
    with open(fl.AERO_PARAMS_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def _clip_norm(rng, mu, sig, lo, hi, n):
    return np.clip(mu + sig * rng.standard_normal(n), lo, hi)


def mc_scenarios() -> dict:
    """Named scenarios (all ASSUMED). Keys override the defaults in ``mc_shots``."""
    return {
        "nominal": {},
        "tight_release": dict(err="tight"),
        "loose_release": dict(err="loose"),
        "release_error_only": dict(phys=False, wind_sig=0.0, hive=False),
        "no_wind": dict(wind_sig=0.0),
        "wind_1.0": dict(wind_sig=1.0),
        "hive_tilt_28.5_fixed": dict(tilt_fixed=28.5),
        "hive_tilt_31.5_fixed": dict(tilt_fixed=31.5),
        "sag_open_loop_0to4pct": dict(v_bias=(-0.04, 0.0)),
        "sag_rapid_fire_0to50pct_drop": dict(rpm_deficit_frac=(0.0, 0.5)),
        "Cl_low_transfer": dict(Cl="low"),
        "Cl_high_transfer": dict(Cl="high"),
        "Cd_low_transfer": dict(Cd="low"),
        "Cd_high_transfer": dict(Cd="high"),
        "k_high_transfer": dict(k="high"),
        # params_lit 'floor' set (c1 0.02, cap 0.04): spin lift nearly absent
        "Cl_floor_transfer": dict(Cl="floor"),
        # same aim, ball launched without spin (HANDOFF rule: a no-spin twin next to every backspin result)
        "nospin_twin": dict(Cl="none"),
    }


def mc_shots(aim: dict, n: int = 1500, seed: int = 0, err: str = "nominal", phys: bool = True,
             wind_sig: Optional[float] = None, hive: bool = True,
             tilt_fixed: Optional[float] = None, v_bias=(0.0, 0.0), rpm_deficit_frac=(0.0, 0.0),
             Cl: Optional[str] = None, Cd: str = "nominal", k: str = "nominal",
             env: Optional[dict] = None, return_paths: bool = False, cell=None, frame: Optional[dict] = None,
             prm3: Optional[dict] = None, draws=None) -> dict:
    """Monte Carlo of one aim. aim = dict(side 'unfav'|'fav', h, d, v, theta, S (0 = no spin,
    else spinning with S ~ U(PHYS S_range)), Cl ('low'|'nominal'|'high'|None),
    launcher (envelope key for the rpm-sag slope)).

    Returns dict(n, k_clean, p, lo, hi, outcomes {result: count}).

    3D-cell branch (cell given; PM-016 hit chance, twin of the browser hitChance): aim = dict(v, theta, S, h,
    z_stop); frame = the moving-robot frame of launch_state; prm3 = integrate3d params (+ optional wind3);
    err = an ERR_SETS name or a dict of sig_v_rel / sig_th / sig_psi; draws = (n, 3) standard normals
    (default mulberry32_normals(seed, 3 n)). Only launch scatter is drawn (no ball, HIVE or wind scatter).
    """
    if cell is not None:
        return _mc_cell(aim, n, seed, err, cell, frame, prm3, draws, return_paths)
    rng = np.random.default_rng(seed)
    E = ERR_SETS[err]
    raw = _aero_raw()
    cl_set = aim.get("Cl") if Cl is None else Cl
    spin = aim.get("S", 0.0) != 0.0 and cl_set not in (None, "none")
    mnom, Rnom = float(raw["mass"]["value"]), float(raw["radius"]["value"])
    rho = float(raw["rho"]["value"])
    cd_nom = float(raw["Cd"][Cd])
    kk = float(raw["spin_decay_k"][k])
    if spin:
        s = raw["Cl"]["sets"][cl_set]
        c1n, cln = float(s["c1"]), float(s["Cl_max"])
    else:
        c1n = cln = 0.0
    wsig = PHYS["wind_sig"] if wind_sig is None else wind_sig
    # ---- release
    v = aim["v"] * (1 + E["sig_v_rel"] * rng.standard_normal(n))
    v = v * (1 + rng.uniform(v_bias[0], v_bias[1], n))
    if rpm_deficit_frac[1] > 0:
        cur = launcher_curves(env)[aim.get("launcher", HOOD_KEY)]
        rpm = rpm_for_v(cur, aim["v"])
        drop = float(np.interp(rpm, cur["rpm"], cur["drop"]))
        dvdr = float(np.interp(rpm, cur["rpm"][1:], np.diff(cur["v"]) / np.diff(cur["rpm"])))
        v = v - dvdr * drop * rng.uniform(rpm_deficit_frac[0], rpm_deficit_frac[1], n)
    th = np.radians(aim["theta"] + E["sig_th"] * rng.standard_normal(n))
    psi = np.radians(E["sig_psi"] * rng.standard_normal(n))
    x0 = -(aim["d"] + E["sig_d"] * rng.standard_normal(n))
    y0 = E["sig_y"] * rng.standard_normal(n)
    z0 = aim["h"] + (PHYS["sig_h"] * rng.standard_normal(n) if phys else np.zeros(n))
    # ---- ball and aero
    if phys:
        mass = _clip_norm(rng, mnom, PHYS["mass_sig"], float(raw["mass"]["low"]),
                          float(raw["mass"]["high"]), n)
        R = _clip_norm(rng, Rnom, PHYS["radius_sig"], float(raw["radius"]["low"]),
                       float(raw["radius"]["high"]), n)
        cd = cd_nom * (1 + PHYS["cd_rel"] * rng.standard_normal(n))
        clf = 1 + PHYS["cl_rel"] * rng.standard_normal(n)
        S = rng.uniform(*PHYS["S_range"], n) if spin else np.zeros(n)
    else:
        mass, R, cd, clf = np.full(n, mnom), np.full(n, Rnom), np.full(n, cd_nom), np.ones(n)
        S = np.full(n, 1.0597 if spin else 0.0)      # hood_nominal S (PREDICTED)
    c1 = c1n * clf
    clmax = cln * clf
    # ---- HIVE pose
    if tilt_fixed is not None:
        tilt = np.full(n, float(tilt_fixed))
    elif hive:
        tilt = _clip_norm(rng, 30.0, PHYS["tilt_sig"], fz.TILT_BOUNDS[0], fz.TILT_BOUNDS[1], n)
    else:
        tilt = np.full(n, 30.0)
    if hive:
        pz = _clip_norm(rng, 1.11633, PHYS["pivot_sig"], 1.09093, 1.14173, n)
        hx = PHYS["hive_x_sig"] * rng.standard_normal(n)
    else:
        pz, hx = np.full(n, 1.11633), np.zeros(n)
    wind = np.zeros((n, 3))
    if wsig > 0:
        wind[:, 0:2] = wsig * rng.standard_normal((n, 2))
    # ---- integrate
    vel0 = np.stack([v * np.cos(th) * np.cos(psi), v * np.cos(th) * np.sin(psi),
                     v * np.sin(th)], axis=1)
    pos0 = np.stack([x0, y0, z0], axis=1)
    w0 = backspin_axis(vel0) * (S * v / R)[:, None]
    tr = integrate3d(pos0, vel0, w0, dict(rho=rho, mass=mass, radius=R, Cd=cd, c1=c1,
                                          clmax=clmax, k=kk), wind=wind)
    P = tr["P"]
    fav = aim["side"] == "fav"
    xg = -X_GATE if fav else X_GATE
    counts: dict = {}
    clean = np.zeros(n, bool)
    ygate = np.full(n, np.nan)
    for i in range(n):
        x = P[i, :, 0].astype(float) - hx[i]
        y = P[i, :, 1].astype(float)
        z = P[i, :, 2].astype(float)
        j = np.nonzero((x[:-1] < xg) & (x[1:] >= xg))[0]
        if j.size:
            j0 = int(j[-1])
            f = (xg - x[j0]) / max(x[j0 + 1] - x[j0], 1e-12)
            yg = y[j0] + f * (y[j0 + 1] - y[j0])
        else:
            yg = y[-1]
        ygate[i] = yg
        if abs(yg) > CELL_HALF - R[i]:
            res = "hit:side_wall" if j.size else "miss"
        else:
            hvi = hv.Hive.from_json("pose_pos", tilt_deg=float(tilt[i]), pivot_z=float(pz[i]),
                                    lateral_offset=float(abs(yg)), ball_radius=float(R[i]))
            if fav:
                hvi = hvi.mirrored()
            keep = (x > -0.8) & (z > 0.3)
            if keep.sum() < 2:
                res = "miss"
            else:
                a, b = int(np.argmax(keep)), len(keep) - int(np.argmax(keep[::-1]))
                res = hvi.classify_path(np.c_[x[a:b], z[a:b]])["result"]
        counts[res] = counts.get(res, 0) + 1
        clean[i] = res == "clean"
    kc = int(clean.sum())
    lo, hi = wilson(kc, n)
    out = dict(n=n, k_clean=kc, p=kc / n, lo=lo, hi=hi, outcomes=counts,
               ygate_sd=float(np.nanstd(ygate)))
    if return_paths:
        out["paths"] = P
        out["clean_mask"] = clean
    return out


# =========================================================================== moving robot / hit chance (PM-016)
# research/MISSING_EFFECTS.md build-next 2a, 2b. Python twin of viz/explorer/solver.js frameFor / launch3 /
# fastShot3D / hitChance (tests/test_move.py checks them against tests/js_move_check.js --dump).
#: ASSUMED launch scatter of the hit-chance readout = ERR_SETS nominal (speed, elevation, heading)
HC_SIG = {"sig_v_rel": ERR_SETS["nominal"]["sig_v_rel"], "sig_th": ERR_SETS["nominal"]["sig_th"],
          "sig_psi": ERR_SETS["nominal"]["sig_psi"]}
HC_NOTE = "model probability under ASSUMED launch scatter (not a measured repeatability)"
_M32 = 0xFFFFFFFF


def _imul(a: int, b: int) -> int:
    return (a * b) & _M32


def mulberry32_normals(seed: int, n: int) -> np.ndarray:
    """physics.js normals(seed, n): mulberry32 uniforms, Box-Muller with both normals of a pair used
    (u1 = 1 - r(), u2 = r(); cos first). Same numbers as the browser (to libm rounding)."""
    a = int(seed) & _M32
    out = np.empty(n)

    def r() -> float:
        nonlocal a
        a = (a + 0x6D2B79F5) & _M32
        t = a
        t = _imul(t ^ (t >> 15), t | 1)
        t ^= (t + _imul(t ^ (t >> 7), t | 61)) & _M32
        return ((t ^ (t >> 14)) & _M32) / 4294967296.0

    for i in range(0, n, 2):
        u1 = 1.0 - r()
        u2 = r()
        m = math.sqrt(-2.0 * math.log(u1))
        out[i] = m * math.cos(2.0 * math.pi * u2)
        if i + 1 < n:
            out[i + 1] = m * math.sin(2.0 * math.pi * u2)
    return out


def launch_state(F: dict, v, theta_deg, S: float, R: float, h: float, dpsi=0.0) -> dict:
    """solver.js launch3 for arrays of shots in the cell frame (x toward the HIVE, release at (-d, s0, h)).
    F = the moving-robot frame (keys d, s0, ux, uy, nx, ny, vrx, vry, wz [rad/s], d0 [deg], lead).
    Ball launch velocity = shooter-relative exit velocity (speed v, exit angle theta + d0) + robot velocity
    (vrx, vry). Lead on: the shooter turns so the ball ground track still points along u; a shot whose
    sideways robot speed exceeds v cos(theta + d0) is infeasible (ok False). dpsi (rad) rotates the shooter
    direction (heading scatter). Spin: backspin S v / R about the horizontal axis normal to the shooter
    direction plus the robot yaw rate wz (S = 0: no spin at all, the no-spin twin)."""
    v = np.atleast_1d(np.asarray(v, float))
    th = np.broadcast_to(np.asarray(theta_deg, float), v.shape)
    dpsi = np.broadcast_to(np.asarray(dpsi, float), v.shape)
    te = np.radians(th + F.get("d0", 0.0))
    vh, vz = v * np.cos(te), v * np.sin(te)
    ux, uy, nx, ny = F["ux"], F["uy"], F["nx"], F["ny"]
    rn = F["vrx"] * nx + F["vry"] * ny
    if F.get("lead", True):
        ok = vh >= abs(rn)
        a = np.sqrt(np.maximum(vh * vh - rn * rn, 0.0))
        ex, ey = a * ux - rn * nx, a * uy - rn * ny
    else:
        ok = np.ones(v.shape, bool)
        ex, ey = vh * ux, vh * uy
    c, s = np.cos(dpsi), np.sin(dpsi)
    ex, ey = c * ex - s * ey, s * ex + c * ey
    eh = np.sqrt(ex * ex + ey * ey)
    N = v.shape[0]
    x0 = np.column_stack([np.full(N, -F["d"]), np.full(N, F["s0"]), np.full(N, float(h))])
    v0 = np.column_stack([ex + F["vrx"], ey + F["vry"], vz])
    if S != 0:
        w = S * v / R
        w0 = np.column_stack([w * ey / eh, -w * ex / eh, np.full(N, F.get("wz", 0.0))])
    else:
        w0 = np.zeros((N, 3))
    return {"x0": x0, "v0": v0, "w0": w0, "ok": ok}


def _mc_cell(aim: dict, n: int, seed: int, err, cell, frame: dict, prm3: dict, draws, return_paths: bool) -> dict:
    E = dict(HC_SIG, **(ERR_SETS[err] if isinstance(err, str) else err))
    Z = np.asarray(draws, float).reshape(n, 3) if draws is not None else mulberry32_normals(seed, 3 * n).reshape(n, 3)
    v = aim["v"] * (1.0 + E["sig_v_rel"] * Z[:, 0])
    th = aim["theta"] + E["sig_th"] * Z[:, 1]
    dpsi = np.radians(E["sig_psi"] * Z[:, 2])
    R = float(prm3["radius"])
    h = float(aim["h"])
    L = launch_state(frame, v, th, float(aim.get("S", 0.0)), R, h, dpsi)
    w3 = prm3.get("wind3")
    wind = None if w3 is None else np.tile(np.asarray(w3, float), (n, 1))
    zs = float(aim["z_stop"]) + h
    tr = integrate3d(L["x0"], L["v0"], L["w0"], prm3, wind=wind, t_max=3.0, z_stop=zs, eps_v=1e-6,
                     dtype=np.float64)
    P, V = tr["P"], tr["V"]
    counts: dict = {}
    clean = np.zeros(n, bool)
    below = (P[:, 1:, 2] < zs) & (V[:, 1:, 2] < 0)
    stop = np.where(below.any(axis=1), np.argmax(below, axis=1) + 2, P.shape[1])
    ok = np.nonzero(L["ok"])[0]
    res_ok = dict(zip(ok.tolist(), c3d.classify_paths3d(   # one batched call (= classify_path3d per shot)
        [(P[i, :stop[i], 0], P[i, :stop[i], 1], P[i, :stop[i], 2]) for i in ok], cell, R)))
    for i in range(n):
        res = res_ok.get(i, "infeasible")
        counts[res] = counts.get(res, 0) + 1
        clean[i] = res == "clean"
    kc = int(clean.sum())
    lo, hi = wilson(kc, n)
    out = dict(n=n, k_clean=kc, p=kc / n, lo=lo, hi=hi, outcomes=counts, clean_mask=clean)
    if return_paths:
        out["paths"] = P
    return out


def mc_cell_counts(aims: list, draws, err, cell, frame: dict, prm3: dict) -> list:
    """k_clean of _mc_cell for several aims (same S, h, z_stop; one prm3) with the same draws, integrated and
    classified in one batch: per shot the same arithmetic as one _mc_cell call per aim, so the same counts."""
    E = dict(HC_SIG, **(ERR_SETS[err] if isinstance(err, str) else err))
    Z = np.asarray(draws, float).reshape(-1, 3)
    n, m = len(Z), len(aims)
    if n == 0 or m == 0:
        return [0] * m
    v = np.concatenate([a["v"] * (1.0 + E["sig_v_rel"] * Z[:, 0]) for a in aims])
    th = np.concatenate([a["theta"] + E["sig_th"] * Z[:, 1] for a in aims])
    dpsi = np.tile(np.radians(E["sig_psi"] * Z[:, 2]), m)
    R, h = float(prm3["radius"]), float(aims[0]["h"])
    L = launch_state(frame, v, th, float(aims[0].get("S", 0.0)), R, h, dpsi)
    w3 = prm3.get("wind3")
    wind = None if w3 is None else np.tile(np.asarray(w3, float), (n * m, 1))
    zs = float(aims[0]["z_stop"]) + h
    tr = integrate3d(L["x0"], L["v0"], L["w0"], prm3, wind=wind, t_max=3.0, z_stop=zs, eps_v=1e-6,
                     dtype=np.float64)
    P, V = tr["P"], tr["V"]
    below = (P[:, 1:, 2] < zs) & (V[:, 1:, 2] < 0)
    stop = np.where(below.any(axis=1), np.argmax(below, axis=1) + 2, P.shape[1])
    ok = np.nonzero(L["ok"])[0]
    res = c3d.classify_paths3d([(P[i, :stop[i], 0], P[i, :stop[i], 1], P[i, :stop[i], 2]) for i in ok], cell, R)
    clean = np.zeros(n * m, bool)
    clean[ok] = np.array([r == "clean" for r in res], bool)
    return [int(clean[j * n:(j + 1) * n].sum()) for j in range(m)]


def hit_chance(cell, frame: dict, aim: dict, sets: dict, n: int = 1000, seed: int = 20261031,
               sig: Optional[dict] = None, twin_aim: Optional[dict] = None) -> dict:
    """Chance it goes in (solver.js hitChance): Monte Carlo of the 3D path on the 3D cell at one setting
    aim = dict(v, theta, S, h, z_stop) with ASSUMED launch scatter sig (default HC_SIG = ERR_SETS nominal).
    sets = {name: integrate3d params} (e.g. Cl low / nominal / high); every set and the no-spin twin use the
    same draws (mulberry32_normals(seed, 3 n)). The twin (S = 0) runs once, at twin_aim (its own recommended
    setting) or else at aim. Counts with a Wilson 95 % interval. A model probability under assumed scatter,
    NOT a measured repeatability (HANDOFF 5)."""
    err = dict(HC_SIG, **(sig or {}))
    Z = mulberry32_normals(seed, 3 * n)
    res = {"n": n, "seed": seed, "sig": err, "note": HC_NOTE, "sets": []}
    for name, prm3 in sets.items():
        r = mc_shots(aim, n=n, err=err, cell=cell, frame=frame, prm3=prm3, draws=Z)
        res["sets"].append({"name": name, "k": r["k_clean"], "n": n, "p": r["p"], "lo": r["lo"], "hi": r["hi"]})
    if float(aim.get("S", 0.0)) != 0.0 and sets:
        ta = dict(aim, **(twin_aim or {}))
        ta["S"] = 0.0
        p0 = dict(next(iter(sets.values())), c1=0.0, cl_table=None, cl_rev=0.0)
        r = mc_shots(ta, n=n, err=err, cell=cell, frame=frame, prm3=p0, draws=Z)
        res["twin"] = {"name": "no-spin twin", "k": r["k_clean"], "n": n, "p": r["p"], "lo": r["lo"], "hi": r["hi"],
                       "v": ta["v"], "theta": ta["theta"]}
    return res


#: best-chance search defaults (solver.js BC): stage-1 shots, stage-2 shots, final shots, kept after stage 1
BC = {"n1": 64, "n2": 400, "n": 1000, "k2": 5}


def best_chance(cell, frame: dict, base_aim: dict, sets: dict, candidates: list, n1: int = BC["n1"],
                n2: int = BC["n2"], n: int = BC["n"], k2: int = BC["k2"], seed: int = 20261031,
                sig: Optional[dict] = None) -> dict:
    """Best chance (PM-017; solver.js bestChance stages 1 to 4 on a given candidate list).

    base_aim = dict(S, h, z_stop); sets = {name: integrate3d params} (equal weight, ASSUMED);
    candidates = [dict(v, theta, from)] (the browser picks them from the clean grid; this replays the search).
    1. every candidate: n1 shots per set on the search draws mulberry32_normals(seed + 1, 3 n2) (common random
       numbers); keep those whose pooled Wilson upper bound reaches the best lower bound, at most k2 by mean.
    2. the kept ones extended to n2 shots on the same draws; winner = highest mean (ties: lower v, lower theta).
    3. the winner on fresh draws mulberry32_normals(seed, 3 n), per set with a Wilson 95 % interval.
    4. at the winner, on the nominal set (or Cl_table / the only set), one scatter source at a time.
    A model probability under ASSUMED scatter, NOT a measured repeatability (HANDOFF 5)."""
    err = dict(HC_SIG, **(sig or {}))
    names = list(sets)
    nS = len(names)
    Zs = mulberry32_normals(seed + 1, 3 * n2).reshape(n2, 3)
    n1 = min(n1, n2)

    def count(c, prm3, Z, e=None):
        if len(Z) == 0:
            return 0
        aim = dict(base_aim, v=c["v"], theta=c["theta"])
        return mc_shots(aim, n=len(Z), err=e or err, cell=cell, frame=frame, prm3=prm3, draws=Z)["k_clean"]

    def pooled(c, m):
        k = sum(c["k"])
        lo, hi = wilson(k, m * nS)
        c.update(mean=k / (m * nS), lo=lo, hi=hi)

    def order(c):
        return (-c["mean"], c["v"], c["theta"])

    C = [{"v": float(c["v"]), "theta": float(c["theta"]), "from": c.get("from", "given")} for c in candidates]
    for c in C:
        c["k"] = [count(c, sets[nm], Zs[:n1]) for nm in names]
        pooled(c, n1)
    stage1 = [dict(v=c["v"], theta=c["theta"], k=list(c["k"]), mean=c["mean"]) for c in C]
    best_lo = max(c["lo"] for c in C)
    keep = sorted([c for c in C if c["hi"] >= best_lo], key=order)[:k2]
    for c in keep:
        c["k"] = [k0 + count(c, sets[nm], Zs[n1:n2]) for k0, nm in zip(c["k"], names)]
        pooled(c, n2)
    keep.sort(key=order)
    w = keep[0]
    Z = mulberry32_normals(seed, 3 * n).reshape(n, 3)
    rows = []
    for nm in names:
        k = count(w, sets[nm], Z)
        lo, hi = wilson(k, n)
        rows.append({"name": nm, "k": k, "n": n, "p": k / n, "lo": lo, "hi": hi})
    ib = next((i for i, r in enumerate(rows) if r["name"] in ("nominal", "Cl_table")), 0)
    parts = []
    for src, e in (("speed", {"sig_v_rel": err["sig_v_rel"], "sig_th": 0.0, "sig_psi": 0.0}),
                   ("angle", {"sig_v_rel": 0.0, "sig_th": err["sig_th"], "sig_psi": 0.0}),
                   ("heading", {"sig_v_rel": 0.0, "sig_th": 0.0, "sig_psi": err["sig_psi"]})):
        k = count(w, sets[names[ib]], Z, e)
        lo, hi = wilson(k, n)
        parts.append({"source": src, "k": k, "n": n, "p": k / n, "lo": lo, "hi": hi})
    act = [p for p, e in zip(parts, ("sig_v_rel", "sig_th", "sig_psi")) if err[e]]
    dom = min(act, key=lambda p: p["p"])["source"] if act else None
    return {"v": w["v"], "theta": w["theta"], "from": w["from"], "sets": rows,
            "mean": sum(r["p"] for r in rows) / len(rows), "stage1": stage1,
            "stage2": [dict(v=c["v"], theta=c["theta"], k=list(c["k"]), mean=c["mean"]) for c in keep],
            "breakdown": {"set": names[ib], "parts": parts, "dominant": dom}, "sig": err, "note": HC_NOTE}


# =========================================================================== clean masks
_GEOM_CACHE: dict = {}


def s_eff(psi_deg: float) -> float:
    """ASSUMED effective lateral offset (m) of the section at azimuth psi (see module doc)."""
    return float(min(0.3 * math.tan(math.radians(psi_deg)), 0.2))


def _geom(side: str, offset: float) -> fz.Geometry:
    key = (side, round(offset, 4))
    if key not in _GEOM_CACHE:
        _GEOM_CACHE[key] = fz.Geometry.make(favorable=(side == "fav"), lateral_offset=offset)
    return _GEOM_CACHE[key]


def map_combos(psis=PSI_BINS) -> list:
    """(psi, offset, label) combos: primary s_eff(psi) section and centre-section sensitivity."""
    out = []
    for p in psis:
        out.append((p, round(s_eff(p), 4), "seff"))
        if p > 0:
            out.append((p, 0.0, "centre"))
    return out


def clean_masks(case_key: str, side: str, combos: list, h: float = H_MAP,
                block: int = 500, verbose: bool = False) -> dict:
    """Clean masks (nd, nv, nth) bool for each (psi, offset, label) combo of one case/side.

    Paths are integrated once (feasibility.integrate_batch) and the in-plane projection for
    azimuth psi is obtained by scaling X and VX by cos(psi)."""
    gr = GRIDS[side]
    V, TH = np.meshgrid(gr["v"], gr["th"], indexing="ij")
    V, TH = V.ravel(), TH.ravel()
    ntot = V.size
    case = fz.case_by_key(case_key)
    prm = fz.case_params(case)
    nd = len(D_GRID)
    out = {c: np.zeros((nd, ntot), bool) for c in combos}
    t0 = time.time()
    for b0 in range(0, ntot, block):
        b1 = min(ntot, b0 + block)
        fam = fz.integrate_batch(V[b0:b1], TH[b0:b1], case["S"], prm, z_stop=0.4)
        mono = np.all(np.diff(fam["X"], axis=1) >= 0, axis=1)
        for c in combos:
            psi, off, _ = c
            cs = np.float32(math.cos(math.radians(psi)))
            fs = {"X": fam["X"] * cs, "Z": fam["Z"], "VX": fam["VX"] * cs, "VZ": fam["VZ"],
                  "mono": mono}
            # small path blocks: feasibility.evaluate_gate sizes its candidate chunks from the
            # SHORTEST window in the chunk, so its peak memory scales with the block size
            # (reported to the lead; feasibility.py is read-only here).
            cand = fz.evaluate_gate(fs, _geom(side, off), h, D_GRID[0] - 0.02,
                                    D_GRID[-1] + 0.02, chunk_elems=2_000_000)
            out[c][:, b0:b1] = fz.grid_from_candidates(cand, b1 - b0, D_GRID)[0]
        if verbose:
            print(f"  {case_key} {side} {b1}/{ntot} {time.time() - t0:.0f}s", flush=True)
    nv, nth = len(gr["v"]), len(gr["th"])
    return {c: m.reshape(nd, nv, nth) for c, m in out.items()}


def smooth_prob(mask: np.ndarray, side: str, err: str = "nominal") -> np.ndarray:
    """P(clean | aim at grid cell) for Gaussian release errors in (d, v, elevation).

    The relative speed error is applied piecewise (sigma_v = sig_v_rel * v at 3 reference
    speeds, each row taking the nearest)."""
    gr = GRIDS[side]
    E = ERR_SETS[err]
    dv = float(gr["v"][1] - gr["v"][0])
    dth = float(gr["th"][1] - gr["th"][0])
    dd = float(D_GRID[1] - D_GRID[0])
    f = mask.astype(np.float32)
    refs = np.array([3.5, 6.0, 8.5])
    out = np.zeros_like(f)
    pick = np.argmin(np.abs(gr["v"][:, None] - refs[None, :]), axis=1)
    for j, vr in enumerate(refs):
        rows = pick == j
        if not rows.any():
            continue
        sm = gaussian_filter(f, sigma=(E["sig_d"] / dd, E["sig_v_rel"] * vr / dv,
                                       E["sig_th"] / dth), mode="constant", truncate=3.0)
        out[:, rows, :] = sm[:, rows, :]
    return out


def best_over_hw(prob: np.ndarray, side: str, v_cap: float) -> dict:
    """Per d: max probability over v <= v_cap and all elevations, with the argmax aim."""
    gr = GRIDS[side]
    vm = gr["v"] <= v_cap + 1e-9
    nd = prob.shape[0]
    P = np.zeros(nd)
    bv = np.full(nd, np.nan)
    bt = np.full(nd, np.nan)
    if vm.any():
        sub = prob[:, vm, :].reshape(nd, -1)
        j = np.argmax(sub, axis=1)
        P = sub[np.arange(nd), j].astype(float)
        nth = len(gr["th"])
        bv = gr["v"][vm][j // nth]
        bt = gr["th"][j % nth]
    return dict(P=P, v=bv, th=bt)


def hw_caps(env: Optional[dict] = None) -> dict:
    cur = launcher_curves(env)
    return {"hood": cur[HOOD_KEY]["v_cap"], "roller": cur[ROLLER_KEY]["v_cap"]}


def _map_job(job) -> dict:
    """Worker: all combos and caps for one (case, side). Each finished job is cached on its
    own so that an interrupted run resumes."""
    ck, side, combos, caps, cache = job
    jp = os.path.join(cache, f"robust_map_job_{ck}_{side}.npy")
    if os.path.exists(jp):
        return np.load(jp, allow_pickle=True).item()
    t0 = time.time()
    masks = clean_masks(ck, side, combos)
    res: dict = {}
    aim = None
    for c, m in masks.items():
        pr = smooth_prob(m, side)
        for capk, cap in caps.items():
            res[(ck, side, c[0], c[2], capk)] = best_over_hw(pr, side, cap)
        if c[0] == 0.0:
            aim = pr.astype(np.float16)      # psi = 0 smoothed probability for aim selection
    out = dict(res=res, aim=aim, key=(ck, side), sec=time.time() - t0)
    np.save(jp, np.array(out, dtype=object), allow_pickle=True)
    return out


def compute_map_tables(cache: str, verbose: bool = True, workers: int = 4) -> dict:
    """Run (or load from cache) the P(d) tables for every case/side/combo/hardware cap."""
    path = os.path.join(cache, "robust_map_tables.npz")
    if os.path.exists(path):
        z = np.load(path, allow_pickle=True)
        return z["tables"].item()
    os.makedirs(cache, exist_ok=True)
    caps = hw_caps()
    caps["uncapped"] = 11.0
    combos = map_combos()
    tables: dict = {"caps": caps, "combos": combos, "d": D_GRID, "aim_masks": {}}
    jobs = [(ck, side, combos, caps, cache) for ck in MAP_CASES for side in ("unfav", "fav")]
    if workers > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=workers) as ex:
            outs = ex.map(_map_job, jobs)
            for o in outs:
                tables.update(o["res"])
                tables["aim_masks"][o["key"]] = o["aim"]
                if verbose:
                    print(f"map {o['key']} done {o['sec']:.0f}s", flush=True)
    else:
        for j in jobs:
            o = _map_job(j)
            tables.update(o["res"])
            tables["aim_masks"][o["key"]] = o["aim"]
            if verbose:
                print(f"map {o['key']} done {o['sec']:.0f}s", flush=True)
    np.savez_compressed(path, tables=np.array(tables, dtype=object))
    return tables


# =========================================================================== field map
def field_grid(step: float = 0.05):
    """Symmetric release grid (src/field_geom.py; x = 0 and y = 0 are grid lines). legal = the
    default 18 x 18 in robot fits at some heading with the release at its centre (ASSUMED)."""
    xs, ys, X, Y = fg.field_grid(step, WALL_MARGIN)
    legal = fg.chassis_ok(X, Y)
    return xs, ys, X, Y, legal


def lateral_factor(L: np.ndarray, err: str = "nominal", w_lat: float = W_LAT["primary"],
                   drift_sd: float = 0.0) -> np.ndarray:
    """P(|e_y| < w_lat), e_y ~ N(0, sqrt((L sig_psi)^2 + sig_y^2 + drift_sd^2))."""
    E = ERR_SETS[err]
    s = np.sqrt((L * math.radians(E["sig_psi"])) ** 2 + E["sig_y"] ** 2 + drift_sd ** 2)
    return erf(w_lat / (math.sqrt(2.0) * s))


def wind_drift_sd(wind_sig: float = PHYS["wind_sig"]) -> float:
    """derived: lateral gate drift SD from a constant crosswind of SD wind_sig, using one
    representative steep shot (h 0.737, v 8.6, elevation 83.25, S1 Cl nominal; long hang
    time, so this is an upper-side estimate for the flatter favourable shots)."""
    raw = _aero_raw()
    s = raw["Cl"]["sets"]["nominal"]
    th = math.radians(83.25)
    v0 = np.array([[8.6 * math.cos(th), 0.0, 8.6 * math.sin(th)]] * 2)
    p0 = np.array([[-0.9, 0.0, 0.737]] * 2)
    w0 = backspin_axis(v0) * (1.06 * 8.6 / float(raw["radius"]["value"]))
    wind = np.array([[0.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    tr = integrate3d(p0, v0, w0, dict(rho=float(raw["rho"]["value"]),
                                      mass=float(raw["mass"]["value"]),
                                      radius=float(raw["radius"]["value"]),
                                      Cd=float(raw["Cd"]["nominal"]), c1=float(s["c1"]),
                                      clmax=float(s["Cl_max"]),
                                      k=float(raw["spin_decay_k"]["nominal"])), wind=wind)
    P = tr["P"]
    # lateral offset when the ball descends through the gate-centre height (z 1.51 m)
    j = int(np.argmax((P[1, :, 2] < 1.51) & (tr["V"][1, :, 2] < 0)))
    return float(abs(P[1, j, 1] - P[0, j, 1])) * wind_sig


def position_prob(tables: dict, case: str, cap: str, pose: str, label: str = "seff",
                  err: str = "nominal", w_lat: float = W_LAT["primary"],
                  drift_sd: float = 0.0, step: float = 0.05) -> dict:
    """P(clean) over the field for one launcher/spin configuration and HIVE pose."""
    xs, ys, X, Y, legal = field_grid(step)
    d = np.abs(X)
    # pose_pos: favourable side = +x (shooter at x > 0 faces the mouth); pose_neg mirrored
    fav = (X > 0) if pose == "pose_pos" else (X < 0)
    P = np.zeros(X.shape)
    evaluated = np.zeros(X.shape, bool)
    for side in ("unfav", "fav"):
        sel = (fav if side == "fav" else ~fav) & legal & (d >= X_MIN_EVAL)
        Lh = d + X_GATE if side == "unfav" else np.maximum(d - X_GATE, 1e-3)
        psi = np.degrees(np.arctan2(np.abs(Y), Lh))
        evaluated |= sel & (psi <= PSI_MAX + 1e-9)
        # P(d) for each psi bin, then linear interpolation in psi
        Pb = np.stack([np.interp(d, D_GRID, tables[(case, side, p, label if p > 0 else "seff",
                                                       cap)]["P"], left=0.0, right=0.0)
                       for p in PSI_BINS], axis=0)
        pb = np.array(PSI_BINS)
        idx = np.clip(np.searchsorted(pb, psi, side="right") - 1, 0, len(pb) - 2)
        f = np.clip((psi - pb[idx]) / (pb[idx + 1] - pb[idx]), 0, 1)
        Pk = np.take_along_axis(Pb, idx[None], 0)[0] * (1 - f) + \
            np.take_along_axis(Pb, (idx + 1)[None], 0)[0] * f
        Pk = np.where(psi <= PSI_MAX + 1e-9, Pk, 0.0)
        L = np.hypot(Lh, Y)
        Pl = lateral_factor(L, err, w_lat, drift_sd)
        P = np.where(sel, Pk * Pl, P)
    # flag: straight line from the release point to the aim point crosses the other HIVE's plan box
    # (exact segment test, src/field_geom.py; not modelled as an obstacle). pose_neg aims at -X_GATE.
    other = fg.sight_blocked(X, Y, aim_x=X_GATE if pose == "pose_pos" else -X_GATE) & legal
    return dict(xs=xs, ys=ys, X=X, Y=Y, P=P, legal=legal, fav=fav, other=other,
                evaluated=evaluated)


MAP_CONFIGS = (
    # (label, case, cap, spin note)
    ("hood_spin_Clnominal", "S1_Clnominal", "hood", "hood S 1.03-1.27 ~ S1 (saturated)"),
    ("hood_spin_Cllow", "S1_Cllow", "hood", "hood, Cl low set"),
    ("hood_spin_Clhigh", "S1_Clhigh", "hood", "hood, Cl high set"),
    ("hood_nospin", "drag", "hood", "counterfactual S = 0 (hood cannot make it)"),
    ("roller_spin_Clnominal", "S1_Clnominal", "roller", "passive roller S 0.91-1.17 ~ S1"),
    ("roller_spin_Cllow", "S1_Cllow", "roller", "roller, Cl low set"),
    ("roller_spin_Clhigh", "S1_Clhigh", "roller", "roller, Cl high set"),
    ("roller_nospin", "drag", "roller", "counterfactual S = 0"),
)
THRESH = (0.5, 0.8, 0.9)
FRAC_FIELDS = (["config", "case", "hardware", "v_cap", "pose", "section", "w_lat", "err",
                "legal_area_m2", "max_P", "max_P_unfav", "max_P_fav"]
               + [f"frac_ge_{int(t * 100)}" for t in THRESH]
               + [f"frac_unfav_ge_{int(t * 100)}" for t in THRESH]
               + [f"frac_fav_ge_{int(t * 100)}" for t in THRESH]
               + [f"frac_ge_{int(t * 100)}_excl_otherhive" for t in THRESH]
               + ["frac_unevaluated_near", "frac_unevaluated_psi_gt_max"]
               + [f"frac_fav_evaluated_ge_{int(t * 100)}" for t in THRESH]
               + [f"frac_unfav_evaluated_ge_{int(t * 100)}" for t in THRESH]
               + ["note"])


def map_fraction_rows(tables: dict, drift: float, step: float = 0.05) -> tuple:
    rows = []
    maps = {}
    caps = tables["caps"]
    for lab, case, cap, note in MAP_CONFIGS:
        for pose in ("pose_pos", "pose_neg"):
            for section in ("seff", "centre"):
                for wk, wl in W_LAT.items():
                    for err in ("nominal",):
                        if section == "centre" and wk != "primary":
                            continue
                        m = position_prob(tables, case, cap, pose, section, err, wl, drift, step)
                        if section == "seff" and wk == "primary":
                            maps[(lab, pose)] = m
                        lg = m["legal"]
                        A = lg.sum()
                        un = lg & ~m["fav"]
                        fv = lg & m["fav"]
                        r = dict(config=lab, case=case, hardware=cap, v_cap=round(caps[cap], 3),
                                 pose=pose, section=section, w_lat=round(wl, 4), err=err,
                                 legal_area_m2=round(A * step * step, 3),
                                 max_P=round(float(m["P"][lg].max()), 4),
                                 max_P_unfav=round(float(m["P"][un].max()), 4),
                                 max_P_fav=round(float(m["P"][fv].max()), 4), note=note)
                        ev = m["evaluated"]
                        near = lg & (np.abs(m["X"]) < X_MIN_EVAL)
                        r["frac_unevaluated_near"] = round(float(near.sum() / A), 4)
                        r["frac_unevaluated_psi_gt_max"] = round(
                            float((lg & ~near & ~ev).sum() / A), 4)
                        for t in THRESH:
                            q = int(t * 100)
                            for sn, sm in (("fav", fv & ev), ("unfav", un & ev)):
                                r[f"frac_{sn}_evaluated_ge_{q}"] = round(
                                    float((m["P"][sm] >= t).mean()) if sm.any() else 0.0, 4)
                            r[f"frac_ge_{q}"] = round(float((m["P"][lg] >= t).mean()), 4)
                            r[f"frac_unfav_ge_{q}"] = round(float((m["P"][un] >= t).mean()), 4)
                            r[f"frac_fav_ge_{q}"] = round(float((m["P"][fv] >= t).mean()), 4)
                            ok = lg & ~m["other"]
                            r[f"frac_ge_{q}_excl_otherhive"] = round(
                                float(((m["P"] >= t) & ok).sum() / A), 4)
                        rows.append(r)
    return rows, maps


PD_FIELDS = ["case", "side", "psi_deg", "section", "hardware", "v_cap", "d", "P_kinematic",
             "v_best", "theta_best"]


def pd_rows(tables: dict) -> list:
    rows = []
    for ck in MAP_CASES:
        for side in ("unfav", "fav"):
            for psi, off, lab in tables["combos"]:
                for capk, cap in tables["caps"].items():
                    b = tables[(ck, side, psi, lab, capk)]
                    for i, dd in enumerate(D_GRID):
                        if round(dd * 100) % 5:
                            continue
                        rows.append(dict(case=ck, side=side, psi_deg=psi, section=lab,
                                         hardware=capk, v_cap=round(cap, 3), d=float(dd),
                                         P_kinematic=round(float(b["P"][i]), 4),
                                         v_best=None if not np.isfinite(b["v"][i])
                                         else float(b["v"][i]),
                                         theta_best=None if not np.isfinite(b["th"][i])
                                         else float(b["th"][i])))
    return rows


# =========================================================================== MC driver
def select_aim(tables: dict, case: str, side: str, cap: str, d_fixed: Optional[float] = None
               ) -> dict:
    """Aim maximising the smoothed psi = 0 clean probability (nominal release errors)."""
    pr = tables["aim_masks"][(case, side)].astype(np.float32)
    gr = GRIDS[side]
    vm = gr["v"] <= tables["caps"][cap] + 1e-9
    sub = np.where(vm[None, :, None], pr, -1.0)
    if d_fixed is not None:
        i = int(np.argmin(np.abs(D_GRID - d_fixed)))
        sub = sub[i:i + 1]
        j = np.unravel_index(int(np.argmax(sub)), sub.shape)
        idd = i
    else:
        j = np.unravel_index(int(np.argmax(sub)), sub.shape)
        idd = j[0]
    c = fz.case_by_key(case)
    return dict(side=side, h=H_MAP, d=float(D_GRID[idd]), v=float(gr["v"][j[1]]),
                theta=float(gr["th"][j[2]]), S=c["S"], Cl=c["Cl"],
                launcher=HOOD_KEY if cap == "hood" else ROLLER_KEY, hardware=cap,
                case=case, P_smoothed=float(sub[(0,) + j[1:]] if d_fixed is not None
                                            else sub[j]))


MC_FIELDS = ["aim", "case", "side", "hardware", "h", "d", "v", "theta", "S_aim", "Cl_aim",
             "P_smoothed_kinematic", "scenario", "n", "k_clean", "p_clean", "wilson_lo",
             "wilson_hi", "ygate_sd_m", "top_outcomes"]


def _mc_job(job) -> dict:
    an, aim, sn, kw, n, seed = job
    t0 = time.time()
    r = mc_shots(aim, n=n, seed=seed, **kw)
    top = sorted(r["outcomes"].items(), key=lambda kv: -kv[1])[:4]
    return dict(aim=an, case=aim["case"], side=aim["side"], hardware=aim["hardware"],
                h=aim["h"], d=aim["d"], v=aim["v"], theta=aim["theta"], S_aim=aim["S"],
                Cl_aim=aim["Cl"] or "none", P_smoothed_kinematic=round(aim["P_smoothed"], 4),
                scenario=sn, n=r["n"], k_clean=r["k_clean"], p_clean=round(r["p"], 4),
                wilson_lo=round(r["lo"], 4), wilson_hi=round(r["hi"], 4),
                ygate_sd_m=round(r["ygate_sd"], 4),
                top_outcomes="; ".join(f"{a}:{b}" for a, b in top), sec=time.time() - t0)


def mc_aims(tables: dict) -> dict:
    return {
        "unfav_best_hood_spin": select_aim(tables, "S1_Clnominal", "unfav", "hood"),
        "fav_best_hood_spin": select_aim(tables, "S1_Clnominal", "fav", "hood"),
        "fav_best_roller_spin": select_aim(tables, "S1_Clnominal", "fav", "roller"),
        "unfav_d1.15_hood_spin": select_aim(tables, "S1_Clnominal", "unfav", "hood", 1.15),
        "fav_d1.55_hood_spin": select_aim(tables, "S1_Clnominal", "fav", "hood", 1.55),
        "fav_d0.80_hood_spin": select_aim(tables, "S1_Clnominal", "fav", "hood", 0.80),
        "unfav_best_hood_nospin": select_aim(tables, "drag", "unfav", "hood"),
        "fav_best_hood_nospin": select_aim(tables, "drag", "fav", "hood"),
    }


def run_mc(tables: dict, n: int = 1500, verbose: bool = True, workers: int = 6) -> list:
    aims = mc_aims(tables)
    sc = mc_scenarios()
    jobs = []
    for an, aim in aims.items():
        if aim["P_smoothed"] <= 0:
            names = ["nominal"]
        elif an in ("unfav_best_hood_spin", "fav_best_hood_spin"):
            names = list(sc)
        elif aim["S"] == 0:
            names = ["nominal", "release_error_only"]
        else:
            names = ["nominal", "release_error_only", "loose_release", "Cl_low_transfer",
                     "Cl_high_transfer", "Cl_floor_transfer", "nospin_twin",
                     "sag_rapid_fire_0to50pct_drop"]
        if "floor" not in _aero_raw()["Cl"]["sets"]:
            names = [x for x in names if x != "Cl_floor_transfer"]
        for k, sn in enumerate(names):
            jobs.append((an, aim, sn, sc[sn], n, 1000 + 17 * k))
        # retuned aims for the Cl bounds (spinning hood best aims only)
        if an in ("unfav_best_hood_spin", "fav_best_hood_spin"):
            for cl in ("low", "high"):
                a2 = select_aim(tables, f"S1_Cl{cl}", aim["side"], "hood")
                jobs.append((an + f"_retuned_Cl{cl}", a2, f"Cl_{cl}_retuned", {}, n, 77))
    rows = []
    if workers > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=workers) as ex:
            for r in ex.map(_mc_job, jobs):
                rows.append(r)
                if verbose:
                    print(f"MC {r['aim']} {r['scenario']}: p={r['p_clean']:.3f} "
                          f"[{r['wilson_lo']:.3f},{r['wilson_hi']:.3f}] {r['sec']:.0f}s",
                          flush=True)
    else:
        for j in jobs:
            rows.append(_mc_job(j))
    return rows


# =========================================================================== figures
_C = {"blue": "#2a78d6", "orange": "#eb6834", "aqua": "#1baf7a", "yellow": "#eda100",
      "violet": "#6250d6", "red": "#d03b3b", "ink": "#0b0b0b", "ink2": "#52514e",
      "muted": "#898781", "grid": "#e1e0d9", "base": "#c3c2b7", "surface": "#fcfcfb"}


def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"figure.facecolor": _C["surface"], "axes.facecolor": _C["surface"],
                         "axes.edgecolor": _C["base"], "axes.labelcolor": _C["ink2"],
                         "xtick.color": _C["muted"], "ytick.color": _C["muted"],
                         "text.color": _C["ink"], "font.size": 9, "axes.titlesize": 10,
                         "axes.spines.top": False, "axes.spines.right": False})
    return plt


def fig_req_v_by_d(rows: list, path: str, h: float = 0.737) -> None:
    plt = _plt()
    cur = launcher_curves()
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
    for ax, gk, title in ((axs[0], "unfav_t30", "Unfavourable side (mouth faces away)"),
                          (axs[1], "fav_t30", "Favourable side (mouth faces shooter)")):
        for case, col, off, lab in (("drag", _C["muted"], -0.012, "no spin (S 0, counterfactual)"),
                                    ("S1_Clnominal", _C["blue"], 0.0, "backspin S1, Cl nominal"),
                                    ("S1_Cllow", _C["aqua"], 0.012, "backspin S1, Cl low"),
                                    ("S1_Clhigh", _C["violet"], 0.024, "backspin S1, Cl high")):
            rr = [r for r in rows if r["launcher"] == HOOD_KEY and r["case"] == case and
                  r["geometry"] == gk and abs(r["h"] - h) < 1e-6]
            for i, r in enumerate(rr):
                ax.plot([r["d"] + off] * 2, [r["v_req_min"], r["v_req_max"]], color=col, lw=2.2,
                        solid_capstyle="butt", label=lab if i == 0 else None)
        for k, ls, lab in ((HOOD_KEY, "-", "hood nominal cap"),
                           ("hood_slick_short", "--", "hood PTFE 45 deg wrap cap"),
                           ("hood_soft_ball", ":", "hood soft-ball cap"),
                           (ROLLER_KEY, "-", "passive roller cap")):
            col = _C["red"] if k.startswith("roller") else _C["orange"]
            ax.axhline(cur[k]["v_cap"], color=col, ls=ls, lw=1.2)
            ax.text(1.77, cur[k]["v_cap"] + 0.06, f"{lab} {cur[k]['v_cap']:.2f}", ha="right",
                    fontsize=7, color=col)
        ax.set_title(title)
        ax.set_xlabel("in-plane release distance d from pivot plane (m)")
        ax.grid(color=_C["grid"], lw=0.6)
        ax.set_xlim(0.5, 1.8)
    axs[0].set_ylabel("required exit speed (m/s): extent of the clean window")
    axs[0].legend(loc="lower left", fontsize=7, frameon=False)
    fig.suptitle(f"Required vs achievable exit speed, release height {h} m (PREDICTED; "
                 "bars = min-max v of clean cells, window is sparse)", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def fig_req_v_spin(rows: list, path: str, h: float = 0.737) -> None:
    plt = _plt()
    cur = launcher_curves()
    aero = _aero_raw()
    R = float(aero["radius"]["value"])
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
    for ax, gk, title in ((axs[0], "unfav_t30", "Unfavourable side"),
                          (axs[1], "fav_t30", "Favourable side")):
        rr = [r for r in rows if r["launcher"] == HOOD_KEY and r["case"] == "S1_Clnominal"
              and r["geometry"] == gk and abs(r["h"] - h) < 1e-6]
        if rr:
            v0 = min(r["v_req_min"] for r in rr)
            v1 = max(r["v_req_max"] for r in rr)
            vv = np.linspace(v0, v1, 50)
            ssat = s_sat("nominal", aero)
            ax.fill_between(vv, ssat * vv / R * RPM, 2.0 * vv / R * RPM, color=_C["blue"],
                            alpha=0.15, lw=0,
                            label=f"required, backspin S {ssat:.2f}-2 (Cl saturated, equivalent)")
        r0 = [r for r in rows if r["launcher"] == HOOD_KEY and r["case"] == "drag" and
              r["geometry"] == gk and abs(r["h"] - h) < 1e-6]
        if r0:
            ax.plot([min(r["v_req_min"] for r in r0), max(r["v_req_max"] for r in r0)], [0, 0],
                    color=_C["muted"], lw=4, label="required, no spin (S 0)")
        for k, col, ls in ((HOOD_KEY, _C["orange"], "-"), ("hood_slick_short", _C["orange"], "--"),
                           ("hood_soft_ball", _C["orange"], ":"),
                           ("hood_stiff_ball_8mm", _C["yellow"], "-"),
                           (ROLLER_KEY, _C["red"], "-"), ("roller_heavy_rest", _C["red"], "--")):
            c = cur[k]
            ax.plot(c["v"], c["spin"], ls=ls, color=col, marker="o", ms=2.5, lw=1.2, label=k)
        ax.set_title(title)
        ax.set_xlabel("exit speed v (m/s)")
        ax.grid(color=_C["grid"], lw=0.6)
    axs[0].set_ylabel("backspin (rpm)")
    axs[0].legend(fontsize=6.5, frameon=False, loc="upper left")
    fig.suptitle(f"Required vs achievable (v, spin), release height {h} m (PREDICTED launcher "
                 "curves, wheel rpm 1000-6000)", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def _draw_field(ax, m: dict, title: str, pose: str) -> Any:
    from matplotlib.colors import ListedColormap, BoundaryNorm
    cols = ["#f3f2ee", "#d9e6f5", "#9cc2ea", "#4f93d8", "#1a5fb0"]
    cmap = ListedColormap(cols)
    norm = BoundaryNorm([0, 0.2, 0.5, 0.8, 0.9, 1.0001], cmap.N)
    P = np.where(m["legal"], m["P"], np.nan)
    st = m["xs"][1] - m["xs"][0]
    ext = (m["xs"][0] - st / 2, m["xs"][-1] + st / 2, m["ys"][0] - st / 2, m["ys"][-1] + st / 2)
    im = ax.imshow(P, origin="lower", extent=ext, cmap=cmap, norm=norm, interpolation="nearest")
    ax.add_patch(__import__("matplotlib.patches", fromlist=["Rectangle"]).Rectangle(
        (-BASE_X, BASE_Y[0]), 2 * BASE_X, BASE_Y[1] - BASE_Y[0], fill=False, ec=_C["ink2"],
        lw=0.8, hatch="////"))
    ax.plot([-0.45, 0.45], [0, 0], color=_C["ink"], lw=0.6)
    ax.add_patch(__import__("matplotlib.patches", fromlist=["Rectangle"]).Rectangle(
        (0.25 if pose == "pose_pos" else -0.55, -CELL_HALF), 0.30, 2 * CELL_HALF,
        fill=False, ec=_C["orange"], lw=1.2))
    ax.axhspan(OTHER_HIVE_Y[0], OTHER_HIVE_Y[1], xmin=0.38, xmax=0.62, color=_C["yellow"],
               alpha=0.25, lw=0)
    ax.set_xlim(-X_WALL, X_WALL)
    ax.set_ylim(Y_WALL[0], Y_WALL[1])
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=8)
    ax.tick_params(labelsize=7)
    return im


def fig_maps(maps: dict, path_main: str, path_cfg: str) -> None:
    plt = _plt()
    fig, axs = plt.subplots(1, 2, figsize=(9.5, 5.2))
    for ax, pose in zip(axs, ("pose_pos", "pose_neg")):
        im = _draw_field(ax, maps[("hood_spin_Clnominal", pose)],
                         f"{pose}: hood + backspin (S~1), Cl nominal", pose)
        ax.set_xlabel("x across tipping plane (m); + = audience side")
    axs[0].set_ylabel("y along pivot axis from red CELL centre (m)")
    cb = fig.colorbar(im, ax=axs, shrink=0.75, ticks=[0, 0.2, 0.5, 0.8, 0.9, 1.0])
    cb.set_label("PREDICTED P(clean entry), nominal release errors")
    fig.suptitle("Field feasibility map, red HIVE, release h 0.737 m (PREDICTED; orange box = up "
                 "CELL; hatched = A-frame base; yellow = other HIVE cell band)", fontsize=8.5)
    fig.savefig(path_main, dpi=140, bbox_inches="tight")
    plt.close(fig)
    labs = [c[0] for c in MAP_CONFIGS]
    fig, axs = plt.subplots(2, 4, figsize=(14, 7.6))
    for ax, lab in zip(axs.ravel(), labs):
        im = _draw_field(ax, maps[(lab, "pose_pos")], f"{lab} (pose_pos)", "pose_pos")
    cb = fig.colorbar(im, ax=axs, shrink=0.6, ticks=[0, 0.2, 0.5, 0.8, 0.9, 1.0])
    cb.set_label("PREDICTED P(clean entry)")
    fig.suptitle("Field map by launcher and spin (pose_pos; pose_neg is the x-mirror). "
                 "'nospin' = S 0 counterfactual, not reachable by either launcher", fontsize=9)
    fig.savefig(path_cfg, dpi=130, bbox_inches="tight")
    plt.close(fig)


def fig_pd(tables: dict, path: str) -> None:
    plt = _plt()
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    cmap = plt.get_cmap("viridis")
    for ax, side in zip(axs, ("unfav", "fav")):
        for i, p in enumerate(PSI_BINS):
            b = tables[("S1_Clnominal", side, p, "seff", "hood")]
            ax.plot(D_GRID, b["P"], color=cmap(i / (len(PSI_BINS) - 1)), lw=1.3,
                    label=f"psi {p:g} deg")
        b = tables[("S1_Clnominal", side, 0.0, "seff", "roller")]
        ax.plot(D_GRID, b["P"], color=_C["red"], ls="--", lw=1.3, label="roller cap, psi 0")
        b = tables[("drag", side, 0.0, "seff", "hood")]
        ax.plot(D_GRID, b["P"], color=_C["muted"], ls=":", lw=1.3, label="no spin, hood, psi 0")
        ax.set_title(f"{side}: best kinematic P(clean) vs d (hood, S1 Cl nominal)")
        ax.set_xlabel("in-plane distance d (m)")
        ax.grid(color=_C["grid"], lw=0.6)
    axs[0].set_ylabel("P(clean) under nominal release errors (no lateral factor)")
    axs[1].legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


# =========================================================================== main
def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cache", default=None, help="default <temp>/pm001_robustness_cache_<aero file name>")
    ap.add_argument("--aero-path", default=fl.LIT_PARAMS_PATH,
                    help="aero/ball parameter file (default research/params_lit.json)")
    ap.add_argument("--n", type=int, default=1500, help="Monte Carlo shots per scenario")
    ap.add_argument("--steps", default="req,map,mc")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    fl.set_aero_path(a.aero_path)      # before any worker pool starts (children inherit it)
    global PROV_HDR
    PROV_HDR += f"\n# AERO: {fl.aero_tag()}.json"
    a.cache = a.cache or os.path.join(tempfile.gettempdir(), "pm001_robustness_cache_" + fl.aero_tag())
    steps = set(a.steps.split(","))
    os.makedirs(FIGS, exist_ok=True)
    if "req" in steps:
        mp = os.path.join(DATA, fl.aero_tag(), "clean_feasibility_map.csv")   # feasibility.py output
        rows = req_vs_ach_rows(mp if os.path.exists(mp) else None)
        print(f"req_vs_ach: window map {mp if os.path.exists(mp) else 'data/clean_feasibility_map.csv'}")
        main2 = (HOOD_KEY, ROLLER_KEY)
        _write_csv(os.path.join(DATA, "req_vs_ach_rows.csv"),
                   [r for r in rows if r["launcher"] in main2], REQ_FIELDS,
                   PROV_HDR + "\n# One row per (launcher hood_nominal / roller_nominal_rest, aero "
                   "case, geometry, h, d) with a clean window; all 7 launcher configs are in "
                   "req_vs_ach_summary.csv. Clean window on the UNCAPPED v grid (clean_feasibility_map.csv v_cap 11). "
                   "S_equivalent: launcher S and required S both >= S_sat = Cl_max/c1 "
                   "(derived) or S_req inside the launcher S band. rpm_gap_ideal = speed gap / "
                   "hood_ideal slope (derived; more rpm does NOT help a grip-capped launcher).")
        summ = req_vs_ach_summary(rows)
        _write_csv(os.path.join(DATA, "req_vs_ach_summary.csv"), summ, SUM_FIELDS)
        fig_req_v_by_d(rows, os.path.join(FIGS, "req_vs_ach_v_by_d.png"))
        fig_req_v_spin(rows, os.path.join(FIGS, "req_vs_ach_v_spin.png"))
        print(f"req_vs_ach: {len(rows)} rows")
    if "map" in steps or "mc" in steps:
        tables = compute_map_tables(a.cache, workers=a.workers)
    if "map" in steps:
        drift = wind_drift_sd()
        frows, maps = map_fraction_rows(tables, drift)
        _write_csv(os.path.join(DATA, "robust_map_fractions.csv"), frows, FRAC_FIELDS,
                   PROV_HDR + f"\n# Field = red-HIVE frame, release points on a 0.05 m grid, "
                   f"{WALL_MARGIN} m from walls, robot footprint (18 x 18 in, any heading) clear of walls and A-frame base; |x| < {X_MIN_EVAL} "
                   f"counted as P = 0. h = {H_MAP} m. Lateral factor: sig_psi, sig_y from err "
                   f"set, wind drift SD {drift:.4f} m (derived). section seff = roof drop at "
                   "s_eff(psi) (assumed), centre = centre section. Threshold fractions are of "
                   "the legal area (unfav/fav columns: of that side's legal area). "
                   "frac_unevaluated_*: share of the legal area NOT evaluated (|x| < "
                   f"{X_MIN_EVAL}, or azimuth > {PSI_MAX} deg) and counted as P = 0; "
                   "*_evaluated_ge_*: fraction of that side's evaluated positions only.")
        _write_csv(os.path.join(DATA, "robust_map_Pd.csv"), pd_rows(tables), PD_FIELDS,
                   PROV_HDR + "\n# P_kinematic = max over hardware-allowed (v, elevation) of "
                   "the clean mask convolved with nominal release errors (d, v, elevation); "
                   "no lateral factor, no aero/HIVE scatter (see robust_mc.csv).")
        fig_maps(maps, os.path.join(FIGS, "map_field_hood.png"),
                 os.path.join(FIGS, "map_field_configs.png"))
        fig_pd(tables, os.path.join(FIGS, "map_P_vs_d.png"))
        print("map done")
    if "mc" in steps:
        rows = run_mc(tables, n=a.n, workers=a.workers)
        _write_csv(os.path.join(DATA, "robust_mc.csv"), rows, MC_FIELDS,
                   PROV_HDR + "\n# Monte Carlo, exact per-shot classification; Wilson 95 % "
                   "interval. Scenarios: src/robustness.py mc_scenarios(); defaults ERR_SETS "
                   "nominal + PHYS. 'transfer' = aim tuned for the nominal aero set, flown "
                   "with another set; 'retuned' = aim re-optimised for that set.")
        print("mc done")


if __name__ == "__main__":
    main()
