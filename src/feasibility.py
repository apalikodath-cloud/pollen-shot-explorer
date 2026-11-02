"""Clean (air-only) HIVE entry feasibility sweeps (HANDOFF 3 Q1-Q3, 4B, 4E channel 1, Phase 2).

Writes data/clean_*.csv and figures/clean_*.png (see ``main``). Every output number is
PREDICTED from the uncalibrated aero bounds in data/aero_params.json and the CAD-derived
geometry in data/hive_geometry.json.

Method (all SI)
---------------
1. Free flight. A vectorised fixed-step RK4 integrator (``integrate_batch``) solves the same
   2D equations as src/flight.py (pure backspin keeps the motion in the vertical plane):
       m dv/dt = m g - 0.5 rho Cd A |v| v + 0.5 rho Cl(S) A |v| (-vz, vx) sgn(w)
       S = |w| R / |v|,  Cl = min(c1 S, Cl_max),  w(t) = w0 exp(-k t)
   It is checked against flight.simulate (tests/test_hive.py) and every reported
   representative shot is re-run with flight.simulate + hive.classify.
2. Translation invariance (no wind): a launch (v, elevation, S) gives one path SHAPE; the
   release point only translates it. So each path is integrated once and, for each release
   height h, every path sample whose centre would sit on the mouth "gate" (the inside-polygon
   edge on the mouth plane) while moving inward defines exactly one release distance d at
   which the ball enters there. The earlier part of that translated path is then checked
   against the inflated HIVE (clearance raster, 1 mm cells). Consecutive clean gate samples
   give a continuous clean interval of d for that launch.
3. Shot frame: the shooter fires toward +x from x_r = -d. Unfavourable side = mouth faces
   away from the shooter (pose_pos HIVE as is, shooter on the neg side); favourable = mouth
   faces the shooter (pose_neg geometry = mirrored pose_pos). pose_neg results are the exact
   mirror of pose_pos (checked numerically in ``check_mirror``).
"""
from __future__ import annotations

import csv
import json
import math
import os
import sys
import tempfile
import time
from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src import flight as fl  # type: ignore
    from src import hive as hv  # type: ignore
    from src import air as air  # type: ignore
    from src import cell3d as c3  # type: ignore
else:
    from . import flight as fl
    from . import hive as hv
    from . import air
    from . import cell3d as c3

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(_ROOT, "data")
FIGS = os.path.join(_ROOT, "figures")
G = fl.G_STANDARD
# Air density of every sweep (PM-019): still air 20 C / 101.325 kPa / dry = 1.20410 kg/m^3 (derived,
# src/air.py), the live solver's default (viz/explorer/solver.js). The params JSON files keep their
# rounded 1.20 (literature); aero_case(rho="json") returns that value instead.
SWEEP_RHO = air.STILL_AIR_RHO
# Clean-entry classifier of the precomputed sweeps (PM-019): "cell3d" = the 3D cell of src/cell3d.py
# (side walls, pentagon roof), the live solver's default model; "section" = the old 2D section model.
SWEEP_CELL = "cell3d"


# --------------------------------------------------------------------------- aero cases
def aero_case(name: str, Cd: Any = "nominal", Cl: Any = None, k: Any = "nominal",
              path: Optional[str] = None, rho: Any = "sweep") -> dict:
    """Flat params dict from data/aero_params.json. Cd/Cl/k: 'low'|'nominal'|'high' or value.
    Cl=None -> no Magnus. name='vacuum' -> rho = 0 (no aero at all).
    rho: "sweep" (default) = SWEEP_RHO 1.2041 (derived still air), "json" = the file's value, or a number."""
    with open(path or fl.AERO_PARAMS_PATH, encoding="utf-8") as fh:
        raw = json.load(fh)
    rho_v = (SWEEP_RHO if rho == "sweep" else float(raw["rho"]["value"]) if rho == "json" else float(rho))
    p = {"name": name, "rho": rho_v, "mass": float(raw["mass"]["value"]),
         "radius": float(raw["radius"]["value"]), "g": G, "nu": float(raw["nu"]["value"])}
    p["Cd"] = float(raw["Cd"][Cd]) if isinstance(Cd, str) else float(Cd)
    if Cl is None:
        p["Cl"] = None
    elif isinstance(Cl, str):
        s = raw["Cl"]["sets"][Cl]
        p["Cl"] = (float(s["c1"]), float(s["Cl_max"]))
    else:
        p["Cl"] = tuple(Cl)
    p["spin_decay_k"] = float(raw["spin_decay_k"][k]) if isinstance(k, str) else float(k)
    if name == "vacuum":
        p["rho"] = 0.0
        p["Cl"] = None
    p["labels"] = {"Cd": Cd, "Cl": Cl, "k": k}
    return p


# --------------------------------------------------------------------------- batch integrator
def integrate_batch(v: np.ndarray, theta_deg: np.ndarray, S0: float, prm: dict,
                    dt: float = 2e-3, t_max: float = 3.0, z_stop: float = -0.8):
    """Vectorised RK4 for launches (v, theta) from the origin toward +x with exit spin
    parameter S0 (= w0 R / v0; > 0 backspin, < 0 topspin). Returns dict of float32 arrays
    X, Z, VX, VZ with shape (N, T) and t (T,). Integration stops once every path is below
    z_stop and descending."""
    v = np.asarray(v, float).ravel()
    th = np.radians(np.asarray(theta_deg, float).ravel())
    N = v.size
    rho, m, R = prm["rho"], prm["mass"], prm["radius"]
    A = math.pi * R * R
    q = 0.5 * rho * A / m
    cd = prm["Cd"]
    cl = prm.get("Cl")
    k = prm.get("spin_decay_k", 0.0) or 0.0
    w0 = S0 * v / R                       # signed spin magnitude (rad/s)
    sgn = np.sign(w0)
    aw0 = np.abs(w0)
    use_m = cl is not None and S0 != 0.0 and rho > 0.0
    if use_m:
        c1, clmax = float(cl[0]), float(cl[1])

    def acc(t, vx, vz):
        sp = np.sqrt(vx * vx + vz * vz)
        ax = -q * cd * sp * vx
        az = -q * cd * sp * vz - G
        if use_m:
            w = aw0 * math.exp(-k * t)
            S = w * R / np.sqrt(sp * sp + 1e-12)
            Cl = np.minimum(c1 * S, clmax)
            f = q * Cl * sp * sgn
            ax = ax - f * vz
            az = az + f * vx
        return ax, az

    if air.has_ext(prm):
        # optional terms (src/air.py; physics.js aeroExt is the line-for-line JS copy): Cd(Re) model, spin drag
        # dCd min(S/S_sat, 1), constant draft w = (along-shot, vertical); drag, Magnus and S use v_rel = v - w
        wx, wz = (float(c) for c in (prm.get("wind") or (0.0, 0.0)))
        nu = float(prm.get("nu", fl.NU_AIR_DEFAULT))
        dcd = float(prm.get("dcd_spin", 0.0) or 0.0)
        ssat = float(prm.get("s_sat", air.S_SAT_DEFAULT))
        spin = S0 != 0.0 and rho > 0.0
        if use_m is False:
            c1, clmax = 0.0, 0.0
        # lift options (air.cl_of: user Cl(S) table, reverse-Magnus blend) and effective mass eps (2d, 2e)
        use_m = spin and (cl is not None or air.lift_on(prm))
        ie = 1.0 / (1.0 + float(prm.get("eps_mass", 0.0) or 0.0))

        def acc(t, vx, vz):  # noqa: F811
            ux = vx - wx
            uz = vz - wz
            sp = np.sqrt(ux * ux + uz * uz)
            re = sp * (2.0 * R) / nu
            cde = air.cd_base(prm, re)
            S = 0.0
            if spin:
                w = aw0 * math.exp(-k * t)
                S = w * R / np.sqrt(sp * sp + 1e-12)
                if dcd != 0.0:
                    cde = cde + dcd * np.minimum(S / ssat, 1.0)
            ax = -q * cde * sp * ux
            az = -q * cde * sp * uz - G
            if use_m:
                Cl = air.cl_of(prm, S, re, (c1, clmax))
                f = q * Cl * sp * sgn
                ax = ax - f * uz
                az = az + f * ux
            if ie != 1.0:
                ax = ax * ie
                az = az * ie
            return ax, az

    nT = int(math.ceil(t_max / dt)) + 1
    X = np.zeros((N, nT), np.float32)
    Z = np.zeros((N, nT), np.float32)
    VX = np.zeros((N, nT), np.float32)
    VZ = np.zeros((N, nT), np.float32)
    x = np.zeros(N)
    z = np.zeros(N)
    vx = v * np.cos(th)
    vz = v * np.sin(th)
    X[:, 0], Z[:, 0], VX[:, 0], VZ[:, 0] = x, z, vx, vz
    t = 0.0
    last = nT - 1
    for n in range(1, nT):
        a1x, a1z = acc(t, vx, vz)
        a2x, a2z = acc(t + dt / 2, vx + dt / 2 * a1x, vz + dt / 2 * a1z)
        a3x, a3z = acc(t + dt / 2, vx + dt / 2 * a2x, vz + dt / 2 * a2z)
        a4x, a4z = acc(t + dt, vx + dt * a3x, vz + dt * a3z)
        x = x + dt * (vx + dt / 6 * (a1x + a2x + a3x))
        z = z + dt * (vz + dt / 6 * (a1z + a2z + a3z))
        vx = vx + dt / 6 * (a1x + 2 * a2x + 2 * a3x + a4x)
        vz = vz + dt / 6 * (a1z + 2 * a2z + 2 * a3z + a4z)
        t += dt
        X[:, n], Z[:, n], VX[:, n], VZ[:, n] = x, z, vx, vz
        if n % 25 == 0 and np.all((z < z_stop) & (vz < 0)):
            last = n
            break
    tt = np.arange(last + 1) * dt
    return {"X": X[:, :last + 1], "Z": Z[:, :last + 1], "VX": VX[:, :last + 1],
            "VZ": VZ[:, :last + 1], "t": tt, "dt": dt}


# --------------------------------------------------------------------------- gate evaluation
X_GATE = 0.401   # shot-frame x of the up-cell gate centre seen from either side (viz/explorer/solver.js X_GATE)
RASTER3D_CACHE = os.path.join(tempfile.gettempdir(), "pollen_raster3d")
_RASTER3D_VERSION = 1


def section_dict(h: "hv.Hive") -> dict:
    """The s = 0 section of a Hive in the form src/cell3d.build_cell (and export_field sections) use."""
    return dict(names=list(h.names), P0=np.asarray(h.P0, float).tolist(),
                P1=np.asarray(h.P1, float).tolist(), inside=np.asarray(h.inside, float).tolist())


def _cell_box(h: "hv.Hive", cell) -> tuple:
    pts = [h.P0, h.P1, h.inside]
    for f in cell.faces:
        if f.V is not None:
            pts.append(f.V[:, [0, 2]])
    allp = np.vstack(pts)
    m = h.R + 0.01
    return (allp[:, 0].min() - m, allp[:, 0].max() + m, allp[:, 1].min() - m, allp[:, 1].max() + m)


def cell_raster(h: "hv.Hive", cell, psi_deg: float, aim_x: float, res: float = 1e-3, s0: float = 0.0,
                cache: Optional[str] = RASTER3D_CACHE) -> "hv.CSpaceRaster":
    """Exact 3D clearance field on the ruled surface of one oblique shot plane (PM-019).

    For a bearing psi the ball centre at shot-frame (x, z) sits at lateral offset
    s = s0 + (aim_x - x) tan(psi) (src/cell3d.py classify_oblique3d; s0 = a fixed lateral offset), so for a fixed psi the 3D clearance
    (exact point distance to the nearest cell3d face - R) is a function of (x, z) only and the 2D
    raster pipeline (evaluate_gate) applies unchanged. inside = cell3d.inside3d. idx indexes the
    cell faces (names = face names). Cached on disk by content hash (cache=None: no cache)."""
    import hashlib
    box = _cell_box(h, cell)
    tp = math.tan(math.radians(psi_deg))
    key = hashlib.sha1()
    for f in cell.faces:
        key.update(f.name.encode())
        key.update(np.asarray(f.V if f.V is not None else f.ext, float).round(9).tobytes())
    key.update(np.asarray(cell.inside, float).round(9).tobytes())
    key.update(np.array([tp, aim_x, s0, res, h.R, cell.half, cell.wall_t, cell.k, _RASTER3D_VERSION,
                         *box], float).round(12).tobytes())
    path = os.path.join(cache, key.hexdigest()[:20] + ".npz") if cache else None
    names = [f.name for f in cell.faces]
    if path and os.path.exists(path):
        try:
            with np.load(path) as z:
                return hv.CSpaceRaster(x0=float(z["x0"]), z0=float(z["z0"]), res=float(z["res"]),
                                       clr=z["clr"], idx=z["idx"], inside=z["inside"], names=names)
        except Exception:          # torn or foreign file: rebuild
            pass
    xmin, xmax, zmin, zmax = box
    nx = int(math.ceil((xmax - xmin) / res))
    nz = int(math.ceil((zmax - zmin) / res))
    xs = xmin + (np.arange(nx) + 0.5) * res
    clr = np.empty((nz, nx), np.float32)
    idx = np.empty((nz, nx), np.int16)
    ins = np.empty((nz, nx), bool)
    step = max(1, 100000 // max(nx, 1))
    for r0 in range(0, nz, step):
        r1 = min(nz, r0 + step)
        zs = zmin + (np.arange(r0, r1) + 0.5) * res
        X, Z = np.meshgrid(xs, zs)
        x, z = X.ravel(), Z.ravel()
        P = np.column_stack([x, s0 + (aim_x - x) * tp, z])
        D = np.full(len(x), np.inf)
        J = np.zeros(len(x), np.int16)
        for j, f in enumerate(cell.faces):
            dj = c3.seg_face(f, P, P)
            b = dj < D
            D = np.where(b, dj, D)
            J[b] = j
        clr[r0:r1] = (D - h.R).reshape(r1 - r0, nx)
        idx[r0:r1] = J.reshape(r1 - r0, nx)
        ins[r0:r1] = c3.inside3d(cell, P[:, 0], P[:, 1], P[:, 2], h.R).reshape(r1 - r0, nx)
    r = hv.CSpaceRaster(x0=xmin, z0=zmin, res=res, clr=clr, idx=idx, inside=ins, names=names)
    if path:
        os.makedirs(cache, exist_ok=True)
        tmp = f"{path[:-4]}.{os.getpid()}.tmp.npz"
        np.savez(tmp, x0=xmin, z0=zmin, res=res, clr=clr, idx=idx, inside=ins)
        os.replace(tmp, path)
    return r


def cell_gate(h: "hv.Hive", cell, psi_deg: float, aim_x: float, s0: float = 0.0, n: int = 20001) -> np.ndarray:
    """Ball-centre entry gate of the 3D cell on one oblique plane: the part of the section gate
    (inside-polygon edge on the mouth plane) whose points lie in cell3d.inside3d at
    s = s0 + (aim_x - x) tan(psi), as [low end, high end]; NaN (2, 2) if no part does (no clean entry)."""
    A, B = h.gate
    t = np.linspace(0.0, 1.0, n)
    pts = A[None, :] + t[:, None] * (B - A)[None, :] - 1e-9 * h.normal_out[None, :]
    s = s0 + (aim_x - pts[:, 0]) * math.tan(math.radians(psi_deg))
    ok = c3.inside3d(cell, pts[:, 0], s, pts[:, 1], h.R)
    if not ok.any():
        return np.full((2, 2), np.nan)
    i0, i1 = int(np.argmax(ok)), int(n - 1 - np.argmax(ok[::-1]))
    if not ok[i0:i1 + 1].all():
        raise ValueError("3D gate is not one interval")
    g = np.array([A + t[i0] * (B - A), A + t[i1] * (B - A)])
    return g[np.argsort(g[:, 1])]


@dataclass
class Geometry:
    """Shot-frame HIVE (shooter at x = -d firing +x) plus its clearance raster.

    model "section" = the 2D HIVE section (hive.Hive.raster, gate = hive.gate). model "cell3d" =
    the 3D cell of src/cell3d.py built from the s = 0 section (side walls, pentagon roof), seen on
    the oblique plane of bearing psi (lateral offset s = (aim_x - x) tan psi, aim_x = +X_GATE
    unfavourable, -X_GATE favourable as in solver.js pose()); psi = 0 is the straight shot (s = 0)."""
    key: str
    hive: hv.Hive
    raster: hv.CSpaceRaster
    favorable: bool
    tilt: float
    model: str = "section"
    gate: Optional[np.ndarray] = None     # None = hive.gate
    cell: Any = None
    psi: float = 0.0
    aim_x: float = 0.0

    @classmethod
    def make(cls, favorable: bool, tilt: Optional[float] = None, res: float = 1e-3,
             pivot_z: Optional[float] = None, lateral_offset: float = 0.0,
             include_projected: bool = False, cell: Optional[str] = None, psi: float = 0.0):
        # unfavourable = pose_pos as is (shooter on neg side); favourable = pose_pos mirrored.
        # cell: None / "section" = the 2D section model (default, unchanged for every caller);
        # "cell3d" = the 3D cell (the sweeps pass cell=SWEEP_CELL). lateral_offset: section model = the
        # s_eff section (roof lowered); cell3d = a fixed lateral offset s0 of the ball path in the 3D
        # cell (s = s0 + (aim_x - x) tan psi).
        model = "section" if cell is None else cell
        if model not in ("section", "cell3d"):
            raise ValueError(f"unknown cell model {model!r}")
        kw = {}
        if tilt is not None:
            kw["tilt_deg"] = tilt
        if pivot_z is not None:
            kw["pivot_z"] = pivot_z
        if lateral_offset and model == "section":
            kw["lateral_offset"] = lateral_offset
        if include_projected:
            kw["include_projected"] = True
        h = hv.Hive.from_json("pose_pos", **kw)
        if favorable:
            h = h.mirrored()
        key = f"{'fav' if favorable else 'unfav'}_t{h.tilt_deg:g}"
        if pivot_z is not None:
            key += f"_zp{pivot_z:.4f}"
        if lateral_offset:
            key += f"_s{lateral_offset:g}"
        if include_projected:
            key += "_legs"
        if model == "section":
            if psi:
                raise ValueError("section model: psi enters through lateral_offset (s_eff)")
            return cls(key=key, hive=h, raster=h.raster(res), favorable=favorable, tilt=h.tilt_deg)
        if psi:
            key += f"_psi{psi:g}"
        c = c3.build_cell(section_dict(h))
        aim = -X_GATE if favorable else X_GATE
        s0 = float(lateral_offset)
        return cls(key=key, hive=h, raster=cell_raster(h, c, psi, aim, res, s0), favorable=favorable,
                   tilt=h.tilt_deg, model="cell3d", gate=cell_gate(h, c, psi, aim, s0), cell=c,
                   psi=float(psi), aim_x=aim)


@dataclass
class SweepGrid:
    v: np.ndarray = field(default_factory=lambda: np.round(np.arange(2.0, 11.0001, 0.1), 3))
    theta: np.ndarray = field(default_factory=lambda: np.round(np.arange(5.0, 89.7501, 0.25), 3))
    h: np.ndarray = field(default_factory=lambda: np.array([0.20, 0.35, 0.50, 0.65, 0.737]))
    d: np.ndarray = field(default_factory=lambda: np.round(np.arange(0.55, 1.7501, 0.05), 3))


def _vec_searchsorted(X: np.ndarray, ii: np.ndarray, kk: np.ndarray, target: np.ndarray):
    """First j in [0, k] with X[i, j] >= target (rows non-decreasing); vectorised bisection."""
    lo = np.zeros(ii.size, np.int64)
    hi = kk.astype(np.int64).copy()
    tgt = target.astype(np.float32)
    while True:
        act = lo < hi
        if not act.any():
            break
        mid = (lo + hi) // 2
        less = X[ii, mid] < tgt
        lo = np.where(act & less, mid + 1, lo)
        hi = np.where(act & ~less, mid, hi)
    return lo


def evaluate_gate(fam: dict, geom: Geometry, h: float, d_lo: float, d_hi: float,
                  chunk_elems: int = 20_000_000):
    """All gate crossings of the family translated to release height h.

    Returns dict of 1D arrays over candidates: i (path index), k (sample index), d (release
    distance), clean (bool), margin (min clearance before entry, m; clean ones), hit (obstacle
    index of first contact, -1 if clean), ang (descent angle at the gate, deg, + falling),
    sg (fraction along the gate, 0 = low end).
    """
    X, Z, VX, VZ = fam["X"], fam["Z"], fam["VX"], fam["VZ"]
    hiv = geom.hive
    A, B = hiv.gate if geom.gate is None else geom.gate
    if not np.all(np.isfinite([A, B])):
        return None                       # 3D cell: no part of the mouth is enterable on this plane
    n = hiv.normal_out
    Zw = Z + np.float32(h)
    band = (Zw >= A[1]) & (Zw <= B[1]) & ((VX * n[0] + VZ * n[1]) < 0)
    ii, kk = np.nonzero(band)
    if ii.size == 0:
        return None
    zc = Zw[ii, kk].astype(float)
    sg = (zc - A[1]) / (B[1] - A[1])
    xg = A[0] + sg * (B[0] - A[0])
    xr = xg - X[ii, kk].astype(float)
    d = -xr
    keep = (d >= d_lo) & (d <= d_hi)
    ii, kk, d, xr, sg = ii[keep], kk[keep], d[keep], xr[keep], sg[keep]
    nc = ii.size
    if nc == 0:
        return None
    ang = np.degrees(np.arctan2(-VZ[ii, kk], VX[ii, kk]))
    r = geom.raster
    nz, nx = r.clr.shape
    bx0 = r.x0
    bx1 = r.x0 + nx * r.res
    # window start: first sample whose translated x is inside the raster box. The bisection
    # needs X non-decreasing; paths whose vx reverses (strong backspin, steep launch) are
    # checked from their first sample instead.
    mono = fam.get("mono")
    if mono is None:
        mono = np.all(np.diff(X, axis=1) >= 0, axis=1)
        fam["mono"] = mono
    j0 = _vec_searchsorted(X, ii, kk, bx0 - xr)
    j0 = np.where(mono[ii], j0, 0)
    L = (kk - j0 + 1).clip(min=1)
    clean = np.zeros(nc, bool)
    margin = np.full(nc, np.nan)
    hit = np.full(nc, -1, np.int64)
    order = np.argsort(L)
    pos = 0
    while pos < nc:
        Lmax = int(L[order[min(nc - 1, pos)]])
        cnt = max(1, chunk_elems // max(Lmax, 1))
        sel = order[pos:pos + cnt]
        Lmax = int(L[sel].max())
        off = np.arange(Lmax)
        J = j0[sel, None] + off[None, :]
        valid = J <= kk[sel, None]
        Jc = np.minimum(J, kk[sel, None])
        xs = X[ii[sel, None], Jc].astype(np.float64) + xr[sel, None]
        zs = Z[ii[sel, None], Jc].astype(np.float64) + h
        ix = np.floor((xs - r.x0) / r.res).astype(np.int64)
        iz = np.floor((zs - r.z0) / r.res).astype(np.int64)
        ok = valid & (ix >= 0) & (ix < nx) & (iz >= 0) & (iz < nz)
        c = np.where(ok, r.clr[np.clip(iz, 0, nz - 1), np.clip(ix, 0, nx - 1)], np.inf)
        neg = c < 0
        anyneg = neg.any(axis=1)
        clean[sel] = ~anyneg
        margin[sel] = np.where(anyneg, np.nan, c.min(axis=1))
        first = np.argmax(neg, axis=1)
        hj = r.idx[np.clip(iz[np.arange(len(sel)), first], 0, nz - 1),
                   np.clip(ix[np.arange(len(sel)), first], 0, nx - 1)]
        hit[sel] = np.where(anyneg, hj, -1)
        pos += len(sel)
    return {"i": ii, "k": kk, "d": d, "clean": clean, "margin": margin, "hit": hit,
            "ang": ang, "sg": sg}


def grid_from_candidates(cand: Optional[dict], n_traj: int, d_grid: np.ndarray):
    """Project candidates onto the d grid. Returns (clean bool (nd, n_traj),
    margin float32 (nd, n_traj) NaN where not clean, ang float32 (nd, n_traj),
    crossing bool (nd, n_traj): the translated path does reach the gate at that d)."""
    nd = len(d_grid)
    clean = np.zeros((nd, n_traj), bool)
    cross = np.zeros((nd, n_traj), bool)
    hit = np.full((nd, n_traj), -2, np.int16)
    margin = np.full((nd, n_traj), np.nan, np.float32)
    ang = np.full((nd, n_traj), np.nan, np.float32)
    if cand is None:
        return clean, margin, ang, cross, hit
    i, k, d = cand["i"], cand["k"], cand["d"]
    # consecutive candidates on the same path (k, k+1) form a continuous d-interval
    o = np.lexsort((k, i))
    i, k, d = i[o], k[o], d[o]
    cl, mg, an, ht = cand["clean"][o], cand["margin"][o], cand["ang"][o], cand["hit"][o]
    pair = (i[1:] == i[:-1]) & (k[1:] == k[:-1] + 1)
    a = np.nonzero(pair)[0]
    lo = np.minimum(d[a], d[a + 1])
    hi = np.maximum(d[a], d[a + 1])
    dg = np.asarray(d_grid, float)          # any sorted grid
    g0 = np.searchsorted(dg, lo - 1e-9, side="left").astype(np.int64)
    g1 = (np.searchsorted(dg, hi + 1e-9, side="right") - 1).astype(np.int64)
    span = (g1 - g0 + 1).clip(min=0)
    rep = np.repeat(np.arange(a.size), span)
    if rep.size == 0:
        return clean, margin, ang, cross, hit
    gidx = g0[rep] + (np.arange(rep.size) - np.repeat(np.cumsum(span) - span, span))
    okg = (gidx >= 0) & (gidx < nd)
    rep, gidx = rep[okg], gidx[okg]
    ai = a[rep]
    tr = i[ai]
    both = cl[ai] & cl[ai + 1]
    cross[gidx, tr] = True
    clean[gidx[both], tr[both]] = True
    m = np.fmin(mg[ai], mg[ai + 1]).astype(np.float32)
    # several crossings may map to one cell; keep the best margin
    mm = margin[gidx[both], tr[both]]
    margin[gidx[both], tr[both]] = np.fmax(mm, m[both])
    ang[gidx, tr] = 0.5 * (an[ai] + an[ai + 1])
    hh = np.where(both, -1, np.where(ht[ai] >= 0, ht[ai], ht[ai + 1]))
    # do not overwrite a clean mark with a hit from another crossing of the same path
    cur = hit[gidx, tr]
    hit[gidx, tr] = np.where(cur == -1, -1, hh).astype(np.int16)
    return clean, margin, ang, cross, hit


def run_family(prm: dict, S0: float, grid: SweepGrid, geoms: list, block: int = 4000,
               dt: float = 2e-3, t_max: float = 3.0, verbose: bool = False,
               chunk_elems: int = 20_000_000) -> dict:
    """Integrate the (v, theta) family for one aero case and evaluate every geometry.

    Returns {geom.key: {"clean": (nh, nd, nv, nth) bool, "margin", "ang", "cross", "hit"},
             "_paths": {"rev", "apex_z", "apex_x", "apex_vx", "vx_min"} each (nv, nth)}.
    apex_* are relative to the release point; rev = vx < 0 somewhere above release height."""
    V, TH = np.meshgrid(grid.v, grid.theta, indexing="ij")
    vflat, tflat = V.ravel(), TH.ravel()
    nv, nth = len(grid.v), len(grid.theta)
    N = vflat.size
    nh, nd = len(grid.h), len(grid.d)
    out = {}
    for gm in geoms:
        out[gm.key] = {"clean": np.zeros((nh, nd, N), bool),
                       "margin": np.full((nh, nd, N), np.nan, np.float32),
                       "ang": np.full((nh, nd, N), np.nan, np.float32),
                       "cross": np.zeros((nh, nd, N), bool),
                       "hit": np.full((nh, nd, N), -2, np.int16)}
    paths = {"rev": np.zeros(N, bool), "apex_z": np.full(N, np.nan, np.float32),
             "apex_x": np.full(N, np.nan, np.float32), "apex_vx": np.full(N, np.nan, np.float32),
             "vx_min": np.full(N, np.nan, np.float32)}
    d_lo, d_hi = grid.d[0] - 0.06, grid.d[-1] + 0.06
    for b0 in range(0, N, block):
        b1 = min(N, b0 + block)
        t0 = time.time()
        fam = integrate_batch(vflat[b0:b1], tflat[b0:b1], S0, prm, dt=dt, t_max=t_max)
        # path diagnostics (4B): apex sample, and vx reversal while the ball is above the
        # release height (the only part of the flight that can reach the HIVE mouth)
        Z, VX = fam["Z"], fam["VX"]
        ia = np.argmax(Z, axis=1)
        r = np.arange(b1 - b0)
        paths["apex_z"][b0:b1] = Z[r, ia]
        paths["apex_x"][b0:b1] = fam["X"][r, ia]
        paths["apex_vx"][b0:b1] = VX[r, ia]
        up = Z >= 0.0
        vxm = np.where(up, VX, np.inf).min(axis=1)
        paths["vx_min"][b0:b1] = vxm
        paths["rev"][b0:b1] = vxm < 0.0
        t1 = time.time()
        for gm in geoms:
            for ih, h in enumerate(grid.h):
                cand = evaluate_gate(fam, gm, float(h), d_lo, d_hi, chunk_elems=chunk_elems)
                c, m, a, x, ht = grid_from_candidates(cand, b1 - b0, grid.d)
                o = out[gm.key]
                o["clean"][ih, :, b0:b1] = c
                o["margin"][ih, :, b0:b1] = m
                o["ang"][ih, :, b0:b1] = a
                o["cross"][ih, :, b0:b1] = x
                o["hit"][ih, :, b0:b1] = ht
        if verbose:
            print(f"  block {b0}-{b1}: integrate {t1 - t0:.1f}s, gates {time.time() - t1:.1f}s",
                  flush=True)
    for key in out:
        for f in out[key]:
            out[key][f] = out[key][f].reshape(nh, nd, nv, nth)
    out["_paths"] = {k: a.reshape(nv, nth) for k, a in paths.items()}
    return out


# =========================================================================== scenario driver
HOOD_V_MAX = 8.9          # m/s, PREDICTED grip-limited hood cap (docs/04_launcher.md)
S_REALISTIC = (1.0, 1.3)  # PREDICTED realistic exit spin parameter band (docs/04_launcher.md)
ROBUST_CELLS = 3          # ASSUMED robustness test: a clean 3 x 3 block (0.3 m/s x 0.75 deg)
SPIN_LEVELS = (0.5, 1.0, 1.5, 2.0)
CL_SETS = ("low", "nominal", "high")
# HIVE tilt bounds. TILT_BOUNDS / TILT_BOUNDS_WIDE = derived exact solve of the checklist lip height
# (data/hive_geometry.json, PM-015: 28.80-31.77, wide 25.90-34.83). PM-019 re-ran the precomputed
# sweeps at these bounds with the 3D cell (SWEEP_CELL) and rho SWEEP_RHO: data/clean_*.csv,
# data/spec_*.csv, data/_spec_cache, viz/explorer/data (explorer + field).
# SWEEP_TILT / SWEEP_TILT_WIDE = the OLD bounds 28.5-31.5 (wide 25.5-34.5): only src/contact.py's
# shipped data/contact_launch_sweep_t*.csv still use them (contact sweeps not re-run in PM-019).
_TILT_JSON = hv.load_geometry()["poses"]["pose_pos"]["tilt_deg"]
TILT_BOUNDS = (float(_TILT_JSON["low"]), float(_TILT_JSON["high"]))
TILT_BOUNDS_WIDE = (float(_TILT_JSON["low_wide"]), float(_TILT_JSON["high_wide"]))
SWEEP_TILT = (28.5, 31.5)
SWEEP_TILT_WIDE = (25.5, 34.5)


def geom_key(favorable: bool, tilt: float = 30.0) -> str:
    """Result key of a sweep geometry, e.g. unfav_t28.8 (same format as analyse())."""
    return f"{'fav' if favorable else 'unfav'}_t{tilt:g}"


SWEEP_UNFAV_KEYS = (geom_key(False), geom_key(False, TILT_BOUNDS[0]), geom_key(False, TILT_BOUNDS[1]))
_C = dict(cell=SWEEP_CELL)
CORE_GEOMS = [dict(favorable=False, **_C), dict(favorable=False, tilt=TILT_BOUNDS[0], **_C),
              dict(favorable=False, tilt=TILT_BOUNDS[1], **_C), dict(favorable=True, **_C)]
WIDE_GEOMS = [dict(favorable=False, tilt=TILT_BOUNDS_WIDE[0], **_C),
              dict(favorable=False, tilt=TILT_BOUNDS_WIDE[1], **_C),
              dict(favorable=True, tilt=TILT_BOUNDS[0], **_C), dict(favorable=True, tilt=TILT_BOUNDS[1], **_C),
              dict(favorable=False, include_projected=True, **_C),
              dict(favorable=False, lateral_offset=0.10, **_C)]   # cell3d: straight path 0.10 m off the cell centre line
WIDE_CASES = ("vacuum", "drag", "S1_Clnominal")


def scenario_cases() -> list:
    """Aero cases (Cd/Cl/k bounds from data/aero_params.json, all ASSUMED)."""
    C = [dict(key="vacuum", S=0.0, Cl=None, Cd="nominal", k="nominal", role="baseline"),
         dict(key="drag", S=0.0, Cl=None, Cd="nominal", k="nominal", role="baseline"),
         dict(key="drag_CdLow", S=0.0, Cl=None, Cd="low", k="nominal", role="sensitivity"),
         dict(key="drag_CdHigh", S=0.0, Cl=None, Cd="high", k="nominal", role="sensitivity")]
    for S in SPIN_LEVELS:
        for cl in CL_SETS:
            C.append(dict(key=f"S{S:g}_Cl{cl}", S=S, Cl=cl, Cd="nominal", k="nominal",
                          role="backspin"))
    C.append(dict(key="S1_Clhigh_CdHigh_kHigh", S=1.0, Cl="high", Cd="high", k="high",
                  role="sensitivity"))
    C.append(dict(key="S1_Clnominal_kHigh", S=1.0, Cl="nominal", Cd="nominal", k="high",
                  role="sensitivity"))
    C.append(dict(key="S2_Clhigh_kLow", S=2.0, Cl="high", Cd="nominal", k="low",
                  role="sensitivity"))
    C.append(dict(key="topspin_S1_Clnominal", S=-1.0, Cl="nominal", Cd="nominal", k="nominal",
                  role="exploratory topspin (out of scope)"))
    return C


def case_by_key(key: str) -> dict:
    return next(c for c in scenario_cases() if c["key"] == key)


def case_params(case: dict) -> dict:
    return aero_case("vacuum" if case["key"] == "vacuum" else case["key"],
                     Cd=case["Cd"], Cl=case["Cl"], k=case["k"])


def _worker(job):
    case, specs, cache, chunk = job
    path = os.path.join(cache, f"{case['key']}.npz")
    if os.path.exists(path):
        return case["key"], 0.0, "cached"
    t0 = time.time()
    grid = SweepGrid()
    geoms = [Geometry.make(**sp) for sp in specs]
    res = run_family(case_params(case), case["S"], grid, geoms, chunk_elems=chunk)
    arrs = {}
    for gk, d in res.items():
        for f, a in d.items():
            if f != "cross":
                arrs[f"{gk}__{f}"] = a
    tmp = path[:-4] + ".tmp.npz"
    np.savez_compressed(tmp, **arrs)
    os.replace(tmp, path)
    return case["key"], round(time.time() - t0, 1), "done"


def run_all(cache: str, workers: int = 4, chunk: int = 5_000_000) -> None:
    os.makedirs(cache, exist_ok=True)
    jobs = []
    for c in scenario_cases():
        specs = list(CORE_GEOMS) + (list(WIDE_GEOMS) if c["key"] in WIDE_CASES else [])
        jobs.append((c, specs, cache, chunk))
    jobs.sort(key=lambda j: -len(j[1]))
    if workers <= 1:
        for j in jobs:
            print(_worker(j), flush=True)
        return
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for r in ex.map(_worker, jobs):
            print(r, flush=True)


def load_case(cache: str, key: str) -> dict:
    z = np.load(os.path.join(cache, f"{key}.npz"))
    out: dict = {}
    for name in z.files:
        g, f = name.split("__")
        out.setdefault(g, {})[f] = z[name]
    return out


# =========================================================================== window metrics
def _max_run(c: np.ndarray, axis: int) -> np.ndarray:
    """Longest run of True along ``axis`` (vectorised over the other axes)."""
    c = np.moveaxis(c, axis, -1)
    cur = np.zeros(c.shape[:-1], np.int32)
    best = np.zeros_like(cur)
    for j in range(c.shape[-1]):
        cur = np.where(c[..., j], cur + 1, 0)
        best = np.maximum(best, cur)
    return best


def _max_square(c: np.ndarray) -> np.ndarray:
    """Side (cells) of the largest all-True k x k block in the last two axes."""
    S = np.zeros(c.shape[:-2] + (c.shape[-2] + 1, c.shape[-1] + 1), np.int32)
    S[..., 1:, 1:] = c.astype(np.int32).cumsum(-2).cumsum(-1)
    best = np.zeros(c.shape[:-2], np.int32)
    k = 1
    while k <= min(c.shape[-2:]):
        w = S[..., k:, k:] - S[..., :-k, k:] - S[..., k:, :-k] + S[..., :-k, :-k]
        has = (w == k * k).any(axis=(-1, -2))
        if not has.any():
            break
        best = np.where(has, k, best)
        k += 1
    return best


def _vmask(grid: SweepGrid, vcap: Optional[float]) -> np.ndarray:
    return np.ones(len(grid.v), bool) if vcap is None else grid.v <= vcap + 1e-9


def window_rows(case: dict, gkey: str, arr: dict, grid: SweepGrid, names: list,
                vcap: Optional[float]) -> list:
    """One row per (h, d) summarising the clean (v, theta) window."""
    vm = _vmask(grid, vcap)
    c = arr["clean"][:, :, vm, :]
    mg, an, ht = arr["margin"][:, :, vm, :], arr["ang"][:, :, vm, :], arr["hit"][:, :, vm, :]
    vv = grid.v[vm]
    n = c.sum(axis=(-1, -2))
    thr, vr, sq = _max_run(c, -1).max(-1), _max_run(c, -2).max(-1), _max_square(c)
    rows = []
    for ih, h in enumerate(grid.h):
        for idd, d in enumerate(grid.d):
            cc = c[ih, idd]
            r = dict(case=case["key"], role=case["role"], S=case["S"], Cl=case["Cl"] or "none",
                     Cd=case["Cd"], k=case["k"], geometry=gkey, h=float(h), d=float(d),
                     v_cap=("11.0" if vcap is None else f"{vcap:g}"), n_clean=int(n[ih, idd]))
            if r["n_clean"]:
                iv, it = np.nonzero(cc)
                m, a = mg[ih, idd][cc], an[ih, idd][cc]
                r.update(v_min=round(float(vv[iv].min()), 2), v_max=round(float(vv[iv].max()), 2),
                         theta_min=float(grid.theta[it].min()),
                         theta_max=float(grid.theta[it].max()),
                         max_theta_run_deg=float(thr[ih, idd]) * 0.25,
                         max_v_run=round(float(vr[ih, idd]) * 0.1, 2),
                         max_square_cells=int(sq[ih, idd]),
                         best_margin_mm=round(1e3 * float(np.nanmax(m)), 1),
                         descent_min_deg=round(float(np.nanmin(a)), 1),
                         descent_max_deg=round(float(np.nanmax(a)), 1), blocked_by="")
                if case["S"]:
                    rpm = abs(case["S"]) * vv[iv] / 0.0355 * 60 / (2 * math.pi)
                    r.update(rpm_min=round(float(rpm.min())), rpm_max=round(float(rpm.max())))
            else:
                r["max_square_cells"] = 0
                hits = ht[ih, idd][ht[ih, idd] >= 0]
                if hits.size:
                    u, cnt = np.unique(hits, return_counts=True)
                    o = np.argsort(-cnt)[:2]
                    r["blocked_by"] = "; ".join(
                        f"{names[int(u[j])]} {100 * cnt[j] / hits.size:.0f}%" for j in o)
                else:
                    r["blocked_by"] = "no gate crossing"
            rows.append(r)
    return rows


MAP_FIELDS = ["case", "role", "S", "Cl", "Cd", "k", "geometry", "h", "d", "v_cap", "n_clean",
              "v_min", "v_max", "theta_min", "theta_max", "max_theta_run_deg", "max_v_run",
              "max_square_cells", "best_margin_mm", "descent_min_deg", "descent_max_deg",
              "rpm_min", "rpm_max", "blocked_by"]


def _write_csv(path: str, rows: list, fields: list, header: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        for line in header.strip().splitlines():
            f.write("# " + line.strip() + "\n")
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


# =========================================================================== Q3 tables
def required_spin_rows(cache: str, grid: SweepGrid, gkeys: list, vcaps=(None, HOOD_V_MAX)):
    """Minimum backspin S (re-optimised v, theta) per unfavourable (h, d), per Cl set."""
    base = load_case(cache, "drag")
    spin = {(S, cl): load_case(cache, f"S{S:g}_Cl{cl}") for S in SPIN_LEVELS for cl in CL_SETS}
    rows = []
    for gk in gkeys:
        for vcap in vcaps:
            vm = _vmask(grid, vcap)
            vv = grid.v[vm]
            b = base[gk]["clean"][:, :, vm, :]
            bn, bs = b.sum(axis=(-1, -2)), _max_square(b)
            sn = {key: a[gk]["clean"][:, :, vm, :] for key, a in spin.items()}
            sq = {key: _max_square(c) for key, c in sn.items()}
            for cl in CL_SETS:
                for ih, h in enumerate(grid.h):
                    for idd, d in enumerate(grid.d):
                        r = dict(geometry=gk, v_cap=("11.0" if vcap is None else f"{vcap:g}"),
                                 Cl=cl, h=float(h), d=float(d), base_n_clean=int(bn[ih, idd]),
                                 base_max_square=int(bs[ih, idd]))
                        smin = None
                        for S in SPIN_LEVELS:
                            if sn[(S, cl)][ih, idd].any():
                                smin = S
                                break
                        if bn[ih, idd]:
                            r["S_min_any"] = "0 (feasible without spin)"
                        elif smin is None:
                            r["S_min_any"] = "none within S<=2"
                        else:
                            cc = sn[(smin, cl)][ih, idd]
                            iv, it = np.nonzero(cc)
                            rpm = smin * vv[iv] / 0.0355 * 60 / (2 * math.pi)
                            r.update(S_min_any=smin, rpm_min=round(float(rpm.min())),
                                     rpm_max=round(float(rpm.max())),
                                     v_min=float(vv[iv].min()), v_max=float(vv[iv].max()),
                                     theta_min=float(grid.theta[it].min()),
                                     theta_max=float(grid.theta[it].max()),
                                     n_clean_at_S_min=int(cc.sum()))
                        rob = "0 (robust without spin)" if bs[ih, idd] >= ROBUST_CELLS else None
                        if rob is None:
                            for S in SPIN_LEVELS:
                                if sq[(S, cl)][ih, idd] >= ROBUST_CELLS:
                                    rob = S
                                    break
                        r["S_min_robust"] = "none within S<=2" if rob is None else rob
                        r["best_max_square_any_S"] = int(max(sq[(S, cl)][ih, idd]
                                                             for S in SPIN_LEVELS))
                        rows.append(r)
    return rows


REQ_FIELDS = ["geometry", "v_cap", "Cl", "h", "d", "base_n_clean", "base_max_square",
              "S_min_any", "rpm_min", "rpm_max", "v_min", "v_max", "theta_min", "theta_max",
              "n_clean_at_S_min", "S_min_robust", "best_max_square_any_S"]


def controlled_rows(cache: str, grid: SweepGrid, gkeys: list, case_keys: list):
    """Same (v, theta) launch with and without spin (no re-optimisation)."""
    base = load_case(cache, "drag")
    rows = []
    for ck in case_keys:
        case = case_by_key(ck)
        a = load_case(cache, ck)
        for gk in gkeys:
            b, s = base[gk]["clean"], a[gk]["clean"]
            bsq, ssq = _max_square(b), _max_square(s)
            dang = a[gk]["ang"] - base[gk]["ang"]
            for ih, h in enumerate(grid.h):
                for idd, d in enumerate(grid.d):
                    bb, ss = b[ih, idd], s[ih, idd]
                    kept = int((bb & ss).sum())
                    da = dang[ih, idd][bb]
                    rows.append(dict(case=ck, S=case["S"], Cl=case["Cl"], k=case["k"],
                                     Cd=case["Cd"], geometry=gk, h=float(h), d=float(d),
                                     n_nospin=int(bb.sum()), n_spin=int(ss.sum()), kept=kept,
                                     lost=int(bb.sum()) - kept, gained=int(ss.sum()) - kept,
                                     max_square_nospin=int(bsq[ih, idd]),
                                     max_square_spin=int(ssq[ih, idd]),
                                     mean_d_descent_deg=(round(float(np.nanmean(da)), 2)
                                                         if np.isfinite(da).any() else "")))
    return rows


CTRL_FIELDS = ["case", "S", "Cl", "k", "Cd", "geometry", "h", "d", "n_nospin", "n_spin",
               "kept", "lost", "gained", "max_square_nospin", "max_square_spin",
               "mean_d_descent_deg"]


# =========================================================================== 4B apex / hook audit
def _shot(h, d, v, th):
    t = math.radians(th)
    return np.array([-d, 0.0, h]), np.array([v * math.cos(t), 0.0, v * math.sin(t)])


_EXACT_GEOM: dict = {}


def _classify_exact(traj, favorable: bool, model: Optional[str] = None, **hk):
    """Exact classification of one simulated (straight, centred) shot in the sweep's cell model.

    model "section": hive.classify_detail (shot frame: shooter on the neg side of pose_pos ->
    unfavourable; on the neg side of pose_neg (= mirrored pose_pos) -> favourable).
    model "cell3d" (default = SWEEP_CELL): cell3d.classify_path3d on the shot-frame path (lateral
    s = traj y = 0), mapped onto the same keys (result clean / hit:<face> / miss, min_clearance,
    entry_angle_deg)."""
    model = SWEEP_CELL if model is None else model
    if model == "section" or hk:
        return hv.classify_detail(traj, "pose_neg" if favorable else "pose_pos", "neg", **hk)
    if favorable not in _EXACT_GEOM:
        _EXACT_GEOM[favorable] = Geometry.make(favorable=favorable, cell="cell3d")
    g = _EXACT_GEOM[favorable]
    P = np.asarray(traj.pos if hasattr(traj, "pos") else traj, float)
    r = c3.classify_path3d(P[:, 0], P[:, 1], P[:, 2], g.cell, g.hive.R)
    res = r["result"] if r["result"] != "hit" else f"hit:{r['hit']}"
    return dict(result=res, hit=r["hit"], min_clearance=r["min_clear"], entry_angle_deg=r["entry_angle"])


def best_cell(arr: dict, grid: SweepGrid, ih: int, idd: int, vcap=HOOD_V_MAX):
    vm = _vmask(grid, vcap)
    m = np.where(arr["clean"][ih, idd] & vm[:, None], arr["margin"][ih, idd], np.nan)
    if not np.isfinite(m).any():
        return None
    iv, it = np.unravel_index(np.nanargmax(m), m.shape)
    return float(grid.v[iv]), float(grid.theta[it]), float(m[iv, it])


def apex_audit(cache: str, grid: SweepGrid, shots=((0.737, 0.75), (0.737, 1.15),
                                                    (0.35, 1.55))):
    """Representative unfavourable shots re-run with flight.simulate (RK45, rtol 1e-9)."""
    base = load_case(cache, "drag")["unfav_t30"]
    spin_cases = ["S1_Clnominal", "S1_Clhigh", "S2_Clhigh_kLow", "topspin_S1_Clnominal"]
    rows, trajs = [], []
    for (h, d) in shots:
        ih = int(np.argmin(np.abs(grid.h - h)))
        idd = int(np.argmin(np.abs(grid.d - d)))
        bc = best_cell(base, grid, ih, idd)
        sources = [("drag-optimal", bc)]
        s1 = load_case(cache, "S1_Clnominal")["unfav_t30"]
        sources.append(("S1-nominal-optimal", best_cell(s1, grid, ih, idd)))
        for label, cell in sources:
            if cell is None:
                continue
            v, th, _ = cell
            x0, v0 = _shot(h, d, v, th)
            for ck in spin_cases:
                case = case_by_key(ck)
                prm = case_params(case)
                w = case["S"] * v / prm["radius"]
                cmp_ = fl.compare_spin(x0, v0, w, prm, t_max=3.0, dt_max=1e-3)
                ts, tn = cmp_["traj_spin"], cmp_["traj_nospin"]
                cs, cn = _classify_exact(ts, False), _classify_exact(tn, False)
                a_s, a_n = ts.apex(), tn.apex()
                vxmin = float(ts.vel[ts.pos[:, 2] >= h, 0].min())
                ms = cmp_["max_abs_dz_s"] or {}
                row = dict(shot=f"h{h:g}_d{d:g}_{label}", h=h, d=d, v=v, theta=th, spin_case=ck,
                           S=case["S"], Cl=case["Cl"], k=case["k"],
                           omega0_rpm=round(abs(w) * 60 / (2 * math.pi)),
                           result_nospin=cn["result"], result_spin=cs["result"],
                           min_clear_nospin_mm=round(1e3 * cn["min_clearance"], 1),
                           min_clear_spin_mm=round(1e3 * cs["min_clearance"], 1),
                           entry_angle_nospin=(round(cn["entry_angle_deg"], 1)
                                               if cn["entry_angle_deg"] is not None else ""),
                           entry_angle_spin=(round(cs["entry_angle_deg"], 1)
                                             if cs["entry_angle_deg"] is not None else ""),
                           apex_t_nospin=round(a_n["t"], 3), apex_x_nospin=round(a_n["x"], 3),
                           apex_z_nospin=round(a_n["z"], 3), apex_vx_nospin=round(a_n["vx"], 3),
                           apex_t_spin=round(a_s["t"], 3), apex_x_spin=round(a_s["x"], 3),
                           apex_z_spin=round(a_s["z"], 3), apex_vx_spin=round(a_s["vx"], 3),
                           apex_vz_spin=round(a_s["vz"], 6), apex_S_spin=round(a_s["S"], 3),
                           apex_rpm_spin=round(a_s["spin_rpm"]),
                           apex_aMx_spin=round(float(a_s["a_M"][0]), 3),
                           apex_aMz_spin=round(float(a_s["a_M"][2]), 3),
                           apex_dx=round(cmp_["apex"]["dx"], 4), apex_dz=round(cmp_["apex"]["dz"], 4),
                           max_abs_dz_at_same_x_mm=round(1e3 * ms.get("value", float("nan")), 1),
                           x_of_max_dz=round(ms.get("x", float("nan")), 3),
                           max_abs_dx_same_t_mm=round(1e3 * cmp_["max_abs_dx_t"]["value"], 1),
                           t_of_max_dx=round(cmp_["max_abs_dx_t"]["t"], 3),
                           vx_min_spin_above_release=round(vxmin, 3),
                           reversal_spin=cmp_["reversal"]["spin"],
                           reversal_nospin=cmp_["reversal"]["nospin"])
                rows.append(row)
                if ck in ("S1_Clnominal", "S2_Clhigh_kLow") and label == "drag-optimal":
                    trajs.append((row["shot"], ck, tn, ts))
    return rows, trajs


def reversal_scan(cache: str, grid: SweepGrid):
    """Explicit hook test over the whole (v, theta) grid: does vx reverse above release height?"""
    rows = []
    for c in scenario_cases():
        if not c["S"]:
            continue
        p = load_case(cache, c["key"])["_paths"]
        rev = p["rev"]
        un = load_case(cache, c["key"])["unfav_t30"]["clean"].any(axis=(0, 1))
        for v in (3.0, 5.0, 7.0, 8.9, 11.0):
            iv = int(np.argmin(np.abs(grid.v - v)))
            r = rev[iv]
            ith80 = int(np.argmin(np.abs(grid.theta - 80.0)))
            rows.append(dict(case=c["key"], S=c["S"], Cl=c["Cl"], k=c["k"], v=float(grid.v[iv]),
                             theta_min_reversal=(float(grid.theta[r].min()) if r.any()
                                                 else "none <= 89.75"),
                             apex_vx_at_theta80=round(float(p["apex_vx"][iv, ith80]), 3),
                             vx_min_at_theta80=round(float(p["vx_min"][iv, ith80]), 3),
                             grid_fraction_reversing=round(float(rev.mean()), 4),
                             unfav_clean_launches_reversing=int((un & rev).sum()),
                             unfav_clean_launches=int(un.sum())))
    return rows


# =========================================================================== fine tolerance
FINE_CASES = ("drag", "S1_Clnominal", "S1_Clhigh", "S2_Clhigh")


def fine_tolerance(cases=FINE_CASES, h=(0.35, 0.737), d=(0.80, 1.15, 1.55)) -> list:
    """5x finer local grid (v step 0.02 m/s, elevation step 0.05 deg; same 0.1:0.25 aspect as
    the main grid, so max_square_cells k means a block of 0.02k m/s x 0.05k deg)."""
    grid = SweepGrid(v=np.round(np.arange(4.0, 10.0001, 0.02), 4),
                     theta=np.round(np.arange(66.0, 89.951, 0.05), 4),
                     h=np.array(h, float), d=np.array(d, float))
    geoms = [Geometry.make(favorable=False, cell=SWEEP_CELL), Geometry.make(favorable=True, cell=SWEEP_CELL)]
    rows = []
    for ck in cases:
        case = case_by_key(ck)
        res = run_family(case_params(case), case["S"], grid, geoms, chunk_elems=5_000_000)
        for gk in ("unfav_t30", "fav_t30"):
            c = res[gk]["clean"]
            thr, vr, sq = _max_run(c, -1).max(-1), _max_run(c, -2).max(-1), _max_square(c)
            for ih, hh in enumerate(grid.h):
                for idd, dd in enumerate(grid.d):
                    cc = c[ih, idd]
                    r = dict(case=ck, S=case["S"], Cl=case["Cl"] or "none", geometry=gk,
                             h=float(hh), d=float(dd), n_clean=int(cc.sum()),
                             area_mps_deg=round(float(cc.sum()) * 0.02 * 0.05, 4),
                             max_theta_run_deg=round(float(thr[ih, idd]) * 0.05, 2),
                             max_v_run_mps=round(float(vr[ih, idd]) * 0.02, 2),
                             max_square_cells=int(sq[ih, idd]),
                             block_v_mps=round(float(sq[ih, idd]) * 0.02, 2),
                             block_theta_deg=round(float(sq[ih, idd]) * 0.05, 2))
                    if cc.any():
                        iv, it = np.nonzero(cc)
                        r.update(v_min=float(grid.v[iv].min()), v_max=float(grid.v[iv].max()),
                                 theta_min=float(grid.theta[it].min()),
                                 theta_max=float(grid.theta[it].max()))
                    rows.append(r)
    return rows


# =========================================================================== cross-checks
def crosscheck(cache: str, grid: SweepGrid, cases=("drag", "S1_Clnominal"),
               hd=((0.737, 0.75), (0.737, 1.15), (0.35, 1.55)), n_neg: int = 25, seed: int = 1):
    """Raster/gate method vs exact flight.simulate + hive.classify on the same cells."""
    rng = np.random.default_rng(seed)
    rows = []
    for ck in cases:
        case = case_by_key(ck)
        prm = case_params(case)
        arr = load_case(cache, ck)["unfav_t30"]
        for (h, d) in hd:
            ih = int(np.argmin(np.abs(grid.h - h)))
            idd = int(np.argmin(np.abs(grid.d - d)))
            c = arr["clean"][ih, idd]
            pos = np.argwhere(c)
            # negatives: grid neighbours of clean cells that are not clean (hardest cases)
            nb = set()
            for iv, it in pos:
                for dv in (-1, 0, 1):
                    for dt_ in (-1, 0, 1):
                        a, b_ = iv + dv, it + dt_
                        if 0 <= a < c.shape[0] and 0 <= b_ < c.shape[1] and not c[a, b_]:
                            nb.add((a, b_))
            nb = sorted(nb)
            if len(nb) > n_neg:
                nb = [nb[i] for i in rng.choice(len(nb), n_neg, replace=False)]
            for (iv, it), want in [(tuple(p_), True) for p_ in pos] + [(q, False) for q in nb]:
                v, th = float(grid.v[iv]), float(grid.theta[it])
                x0, v0 = _shot(h, d, v, th)
                w = fl.backspin_omega(v0, case["S"] * v / prm["radius"]) if case["S"] else np.zeros(3)
                tr = fl.simulate(x0, v0, w, prm, t_max=3.0, dt_max=1e-3)
                cd = _classify_exact(tr, False)
                rows.append(dict(case=ck, h=h, d=d, v=v, theta=th, grid_clean=want,
                                 exact=cd["result"], agree=(cd["result"] == "clean") == want,
                                 exact_min_clear_mm=round(1e3 * cd["min_clearance"], 2),
                                 grid_margin_mm=(round(1e3 * float(arr["margin"][ih, idd, iv, it]), 2)
                                                 if want else "")))
    return rows


def _side_free(result: str) -> str:
    """Static frame parts are named by WORLD side (..._pos / ..._neg); a mirror swaps them."""
    for suf in ("_pos", "_neg"):
        if result.startswith("hit:frame_") and result.endswith(suf):
            return result[:-len(suf)] + "_<side>"
    return result


def check_mirror(n: int = 40, seed: int = 2):
    """pose_neg results must be the exact mirror of pose_pos results (both sides)."""
    rng = np.random.default_rng(seed)
    prm = case_params(case_by_key("drag"))
    agree = 0
    tot = 0
    for _ in range(n):
        h = rng.uniform(0.2, 0.737)
        d = rng.uniform(0.6, 1.7)
        v = rng.uniform(5.0, 9.0)
        th = rng.uniform(55.0, 88.0)
        x0, v0 = _shot(h, d, v, th)
        tr = fl.simulate(x0, v0, np.zeros(3), prm, t_max=3.0, dt_max=2e-3)
        P = tr.pos.copy()
        P[:, 0] *= -1.0                                    # same shot from the +x side
        a = hv.classify_detail(tr.pos, "pose_pos", "neg")["result"]      # unfavourable
        b = hv.classify_detail(P, "pose_neg", "pos")["result"]           # unfavourable mirror
        c = hv.classify_detail(tr.pos, "pose_neg", "neg")["result"]      # favourable
        e = hv.classify_detail(P, "pose_pos", "pos")["result"]           # favourable mirror
        f = hv.classify_detail(tr.pos, "pose_pos", "pos", frame="shot")["result"]
        a, b, c, e, f = (_side_free(r) for r in (a, b, c, e, f))
        agree += int(a == b) + int(c == e) + int(c == f)
        tot += 3
    return agree, tot


# =========================================================================== figures
_C = {"blue": "#2a78d6", "orange": "#eb6834", "aqua": "#1baf7a", "yellow": "#eda100",
      "violet": "#6250d6", "ink": "#0b0b0b", "ink2": "#52514e", "muted": "#898781",
      "grid": "#e1e0d9", "base": "#c3c2b7", "surface": "#fcfcfb"}


def _style(plt):
    plt.rcParams.update({"figure.facecolor": _C["surface"], "axes.facecolor": _C["surface"],
                         "axes.edgecolor": _C["base"], "axes.labelcolor": _C["ink2"],
                         "xtick.color": _C["muted"], "ytick.color": _C["muted"],
                         "text.color": _C["ink"], "font.size": 9, "axes.titlesize": 10,
                         "axes.spines.top": False, "axes.spines.right": False})


def fig_maps(cache: str, grid: SweepGrid, path: str):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap, BoundaryNorm
    _style(plt)
    panels = [("drag", "unfav_t30", None, "Unfavourable, drag only (v<=11)"),
              ("vacuum", "unfav_t30", None, "Unfavourable, vacuum (v<=11)"),
              ("drag", "unfav_t30", HOOD_V_MAX, "Unfavourable, drag only, v<=8.9"),
              ("S1_Clnominal", "unfav_t30", HOOD_V_MAX, "Unfavourable, S=1 Cl nominal, v<=8.9"),
              ("S2_Clhigh", "unfav_t30", HOOD_V_MAX, "Unfavourable, S=2 Cl high, v<=8.9"),
              ("drag", "fav_t30", HOOD_V_MAX, "Favourable, drag only, v<=8.9")]
    ramp = ["#e1e0d9", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
    bounds = [-0.5, 0.5, 1.5, 2.5, 3.5, 5.5, 8.5, 12.5, 100]
    cmap, norm = ListedColormap(ramp), BoundaryNorm(bounds, len(ramp))
    fig, axs = plt.subplots(2, 3, figsize=(13, 6.2), constrained_layout=True)
    for ax, (ck, gk, vcap, title) in zip(axs.ravel(), panels):
        a = load_case(cache, ck)[gk]["clean"][:, :, _vmask(grid, vcap), :]
        sq = _max_square(a)
        ax.imshow(sq, origin="lower", aspect="auto", cmap=cmap, norm=norm,
                  extent=(grid.d[0] - 0.025, grid.d[-1] + 0.025, -0.5, len(grid.h) - 0.5))
        for ih in range(len(grid.h)):
            for idd, d in enumerate(grid.d):
                val = int(sq[ih, idd])
                ax.text(d, ih, "x" if val == 0 else str(val), ha="center", va="center",
                        fontsize=6.5, color=("#ffffff" if val >= 6 else _C["ink2"]))
        ax.set_yticks(range(len(grid.h)), [f"{h:.3g}" for h in grid.h])
        ax.set_xlabel("release distance d from HIVE pivot plane (m)")
        ax.set_ylabel("release height h (m)")
        ax.set_title(title, loc="left")
    fig.suptitle("Largest clean k x k block in the (v, elevation) grid (cell = 0.1 m/s x 0.25 deg); "
                 "x = no clean launch. PREDICTED, tilt 30 deg, Cd nominal", fontsize=10, x=0.01,
                 ha="left")
    fig.savefig(path, dpi=130)
    plt.close(fig)


def fig_windows(cache: str, grid: SweepGrid, path: str, h=0.737, ds=(0.75, 1.15, 1.55)):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    from matplotlib.patches import Patch
    _style(plt)
    cols = [("S1_Clnominal", "S=1, Cl nominal"), ("S1_Clhigh", "S=1, Cl high"),
            ("S2_Clhigh", "S=2, Cl high")]
    base = load_case(cache, "drag")["unfav_t30"]["clean"]
    sp = {ck: load_case(cache, ck)["unfav_t30"]["clean"] for ck, _ in cols}
    ih = int(np.argmin(np.abs(grid.h - h)))
    cmap = ListedColormap([_C["surface"], _C["muted"], _C["blue"], _C["orange"]])
    fig, axs = plt.subplots(len(ds), len(cols), figsize=(12, 9), constrained_layout=True,
                            sharex=True, sharey=True)
    th_lo = 60.0
    jt = grid.theta >= th_lo
    for r, d in enumerate(ds):
        idd = int(np.argmin(np.abs(grid.d - d)))
        b = base[ih, idd][:, jt]
        for c_, (ck, lab) in enumerate(cols):
            s = sp[ck][ih, idd][:, jt]
            code = np.zeros(b.shape, int)
            code[b & s] = 2
            code[b & ~s] = 1
            code[~b & s] = 3
            ax = axs[r, c_]
            ax.imshow(code.T, origin="lower", aspect="auto", cmap=cmap, vmin=0, vmax=3,
                      interpolation="nearest",
                      extent=(grid.v[0] - 0.05, grid.v[-1] + 0.05, th_lo - 0.125,
                              grid.theta[-1] + 0.125))
            ax.axvline(HOOD_V_MAX, color=_C["ink2"], lw=0.8, ls="--")
            ax.set_title(f"d = {grid.d[idd]:.2f} m, {lab}", loc="left")
            if r == len(ds) - 1:
                ax.set_xlabel("launch speed v (m/s)")
            if c_ == 0:
                ax.set_ylabel("elevation (deg)")
    fig.legend(handles=[Patch(color=_C["blue"], label="clean with and without spin"),
                        Patch(color=_C["muted"], label="clean without spin only (lost)"),
                        Patch(color=_C["orange"], label="clean with spin only (gained)")],
               loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.03), frameon=False)
    fig.suptitle(f"Same (v, elevation) with and without backspin, unfavourable side, h = {h} m, "
                 "tilt 30, Cd nominal (PREDICTED). Dashed: hood cap 8.9 m/s", x=0.01, ha="left",
                 fontsize=10)
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)


def fig_spin_trend(cache: str, grid: SweepGrid, path: str):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    _style(plt)
    vm = _vmask(grid, HOOD_V_MAX)
    fig, axs = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    colors = {"low": _C["aqua"], "nominal": _C["blue"], "high": _C["orange"]}
    for ax, gk, ttl in [(axs[0], "unfav_t30", "Unfavourable side"),
                        (axs[1], "fav_t30", "Favourable side")]:
        b = load_case(cache, "drag")[gk]["clean"][:, :, vm, :]
        bt = b.sum() / b[..., 0, 0].size
        for cl in CL_SETS:
            ys = [bt]
            for S in SPIN_LEVELS:
                a = load_case(cache, f"S{S:g}_Cl{cl}")[gk]["clean"][:, :, vm, :]
                ys.append(a.sum() / a[..., 0, 0].size)
            ax.plot((0,) + SPIN_LEVELS, ys, "-o", color=colors[cl], lw=2, ms=6,
                    label=f"Cl {cl}")
        ax.axvspan(*S_REALISTIC, color=_C["grid"], alpha=0.6, lw=0)
        ax.set_xlabel("exit spin parameter S (backspin)")
        ax.set_ylabel("mean clean (v, elev) cells per (h, d)")
        ax.set_title(ttl, loc="left")
        ax.grid(axis="y", color=_C["grid"], lw=0.6)
        ax.set_ylim(bottom=0)
    axs[0].legend(frameon=False)
    fig.suptitle("Size of the clean launch window vs backspin (v<=8.9, tilt 30, Cd nominal, "
                 "PREDICTED). Grey band: realistic S 1.0-1.3", x=0.01, ha="left", fontsize=10)
    fig.savefig(path, dpi=130)
    plt.close(fig)


def _descent_cut(tr, z_end: float = 1.0) -> int:
    """Index after which a plotted path is dropped: first descending sample below z_end."""
    ia = int(np.argmax(tr.z))
    below = np.nonzero(tr.z[ia:] < z_end)[0]
    return ia + int(below[0]) + 1 if below.size else len(tr.z)


def fig_trajectories(trajs: list, path: str):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    _style(plt)
    hvv = hv.Hive.from_json("pose_pos")
    fig, axs = plt.subplots(1, 2, figsize=(13, 5.6), constrained_layout=True)
    for ax, zoom in [(axs[0], False), (axs[1], True)]:
        for p0, p1, nm in zip(hvv.P0, hvv.P1, hvv.names):
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=_C["ink2"], lw=1.6,
                    solid_capstyle="round")
        poly = np.vstack([hvv.inside, hvv.inside[:1]])
        ax.fill(poly[:, 0], poly[:, 1], color=_C["aqua"], alpha=0.25, lw=0)
        g = hvv.gate
        ax.plot(g[:, 0], g[:, 1], color=_C["aqua"], lw=2)
        seen = set()
        for shot, ck, tn, ts in trajs:
            if ck != "S2_Clhigh_kLow" and ck != "S1_Clnominal":
                continue
            if shot not in seen:
                kn = _descent_cut(tn)
                ax.plot(tn.x[:kn], tn.z[:kn], color=_C["ink"], lw=1.2,
                        label="no spin" if not seen else None)
                a = tn.apex()
                ax.plot(a["x"], a["z"], "o", color=_C["ink"], ms=5)
                seen.add(shot)
            col = _C["blue"] if ck == "S1_Clnominal" else _C["orange"]
            lab = ("S=1, Cl nominal" if ck == "S1_Clnominal" else "S=2, Cl high, k low")
            ks = _descent_cut(ts)
            ax.plot(ts.x[:ks], ts.z[:ks], color=col, lw=1.2, ls="--",
                    label=lab if (ck, 1) not in seen else None)
            seen.add((ck, 1))
            a = ts.apex()
            ax.plot(a["x"], a["z"], "o", color=col, ms=5)
        ax.set_aspect("equal")
        ax.grid(color=_C["grid"], lw=0.5)
        ax.set_xlabel("x (m), HIVE frame, shooter on -x")
        ax.set_ylabel("z (m)")
        if zoom:
            ax.set_xlim(-0.25, 0.75)
            ax.set_ylim(1.05, 2.25)
            ax.set_title("Zoom at the mouth (gate = green edge)", loc="left")
        else:
            ax.set_xlim(-1.8, 1.2)
            ax.set_ylim(0.0, 4.3)
            ax.set_title("Drag-optimal unfavourable shots re-run with backspin at the same v, elev" +
                         chr(10) +
                         "(dots = apex; paths drawn to z = 1.0 m on descent, through obstacles)",
                         loc="left")
    axs[0].legend(frameon=False, loc="lower right")
    fig.savefig(path, dpi=130)
    plt.close(fig)


# =========================================================================== analysis driver
def analyse(cache: str, figs: bool = True) -> dict:
    grid = SweepGrid()
    t0 = time.time()
    specs = list(CORE_GEOMS) + list(WIDE_GEOMS)
    names = {}
    for sp in specs:
        g_ = Geometry.make(**sp)          # blocker names = the raster's names (cell3d: face names)
        names[g_.key] = list(g_.raster.names)
    hdr = """PREDICTED (uncalibrated aero bounds """ + fl.aero_tag() + """.json = ASSUMED; HIVE geometry data/hive_geometry.json = CAD-derived/confirmed tilt 30, bounds derived).
Shot frame: shooter fires +x from x = -d at height h (ball centre). unfav = mouth faces away from shooter (pose_pos, side neg / pose_neg, side pos). fav = mouth faces shooter.
Grid: v 2.0-11.0 step 0.1 m/s; elevation 5-89.75 step 0.25 deg; clean = ball centre enters the inside polygon before any obstacle contact (2D section, centred shot).
v_cap 8.9 = PREDICTED hood grip cap (docs/04_launcher.md). max_square_cells = largest all-clean k x k block (k*0.1 m/s by k*0.25 deg). Raster 1 mm, dt 2 ms: clearance error <= ~2.5 mm."""
    if SWEEP_CELL == "cell3d":
        hdr = hdr.replace("(2D section, centred shot).",
                          "(3D cell of src/cell3d.py built from the s = 0 section, centred straight shot; "
                          "rho %.4f kg/m^3 derived; PM-019)." % SWEEP_RHO)
    rows = []
    for c in scenario_cases():
        a = load_case(cache, c["key"])
        for gk, arr in a.items():
            if gk.startswith("_"):
                continue
            for vcap in (None, HOOD_V_MAX):
                rows += window_rows(c, gk, arr, grid, names[gk], vcap)
    _write_csv(os.path.join(DATA, "clean_feasibility_map.csv"), rows, MAP_FIELDS, hdr)
    unf = list(SWEEP_UNFAV_KEYS)
    req = required_spin_rows(cache, grid, unf)
    _write_csv(os.path.join(DATA, "clean_required_spin.csv"), req, REQ_FIELDS,
               hdr + "\nQ3: S_min_any = smallest backspin S in {0.5,1,1.5,2} (launch v, elevation "
               "re-optimised) giving >= 1 clean launch where drag-only (Cd nominal) gives none. "
               f"S_min_robust: smallest S giving a clean {ROBUST_CELLS}x{ROBUST_CELLS} block "
               "(ASSUMED robustness criterion). rpm = S v / R * 60 / 2pi at launch.")
    ctrl_cases = [c["key"] for c in scenario_cases() if c["S"]]
    ctrl = controlled_rows(cache, grid, unf + ["fav_t30"], ctrl_cases)
    _write_csv(os.path.join(DATA, "clean_spin_controlled.csv"), ctrl, CTRL_FIELDS,
               hdr + "\nControlled comparison: identical (v, elevation, h, d) launched with and "
               "without spin (no re-optimisation). kept/lost/gained count grid cells. "
               "mean_d_descent_deg = mean change of descent angle at the gate (spin - no spin) "
               "over the no-spin clean cells; negative = shallower.")
    aud, trajs = apex_audit(cache, grid)
    _write_csv(os.path.join(DATA, "clean_apex_audit.csv"), aud, list(aud[0].keys()),
               "PREDICTED. 4B apex/hook audit: representative unfavourable shots (tilt 30) re-run "
               "with flight.simulate (RK45 rtol 1e-9) and flight.compare_spin; exact "
               f"classification in the sweep cell model ({SWEEP_CELL}). apex_* in m, m/s, s; a_M = Magnus acceleration (m/s^2) at apex. "
               "max_abs_dz_at_same_x = largest height difference spin - no spin at equal "
               "downrange; reversal = vx changes sign at any time.")
    rev = reversal_scan(cache, grid)
    _write_csv(os.path.join(DATA, "clean_hook_scan.csv"), rev, list(rev[0].keys()),
               "PREDICTED. Explicit horizontal-reversal test over the whole launch grid (from the "
               "batch integrator): reversal = vx < 0 at any sample above release height. "
               "theta_min_reversal = lowest elevation on the grid at that v that reverses.")
    xc = crosscheck(cache, grid)
    _write_csv(os.path.join(DATA, "clean_crosscheck.csv"), xc, list(xc[0].keys()),
               "Method check: gate/raster sweep vs exact flight.simulate + exact classification in "
               f"the same cell model ({SWEEP_CELL}) on the same (h, d, v, elevation); negatives = "
               "non-clean neighbours of clean cells.")
    ft = fine_tolerance()
    _write_csv(os.path.join(DATA, "clean_fine_tolerance.csv"), ft, list(ft[0].keys()) +
               [k for k in ("v_min", "v_max", "theta_min", "theta_max") if k not in ft[0]],
               "PREDICTED. Local fine grid (v 4-10 step 0.02 m/s, elevation 66-89.95 step 0.05 "
               "deg), tilt 30, Cd nominal. area = clean area in the (v, elevation) plane (m/s x "
               "deg). block_* = largest all-clean block with the same 0.1:0.25 aspect as the main "
               "grid. max_*_run = longest clean interval at a fixed other variable.")
    ma, mt = check_mirror()
    if figs:
        fig_maps(cache, grid, os.path.join(FIGS, "clean_feasibility_maps.png"))
        fig_windows(cache, grid, os.path.join(FIGS, "clean_spin_windows.png"))
        fig_spin_trend(cache, grid, os.path.join(FIGS, "clean_window_vs_spin.png"))
        fig_trajectories(trajs, os.path.join(FIGS, "clean_apex_paths.png"))
    summ = {"mirror_agree": [ma, mt],
            "crosscheck_agree": [int(sum(r["agree"] for r in xc)), len(xc)],
            "crosscheck_disagree": [r for r in xc if not r["agree"]],
            "seconds": round(time.time() - t0, 1)}
    with open(os.path.join(cache, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summ, f, indent=1, default=str)
    return summ


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cache", default=None,
                    help="directory for the per-case sweep arrays (npz); default <temp>/pollen_clean_cache_<aero file name>")
    ap.add_argument("--aero-path", default=fl.LIT_PARAMS_PATH,
                    help="aero/ball parameter file (default research/params_lit.json)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--stage", choices=("run", "analyse", "all"), default="all")
    ap.add_argument("--no-figs", action="store_true", help="skip figures/clean_*.png")
    a = ap.parse_args(argv)
    fl.set_aero_path(a.aero_path)      # before any worker pool starts (children inherit it)
    global DATA, FIGS
    if fl.aero_tag() != "aero_params":  # keep the first-pass outputs (docs/03) beside the new ones
        DATA = os.path.join(_ROOT, "data", fl.aero_tag())
        FIGS = os.path.join(_ROOT, "figures", fl.aero_tag())
        os.makedirs(DATA, exist_ok=True)
        os.makedirs(FIGS, exist_ok=True)
    a.cache = a.cache or os.path.join(__import__("tempfile").gettempdir(), "pollen_clean_cache_" + fl.aero_tag())
    if a.stage in ("run", "all"):
        run_all(a.cache, workers=a.workers)
    if a.stage in ("analyse", "all"):
        print(json.dumps(analyse(a.cache, figs=not a.no_figs), indent=1, default=str))


if __name__ == "__main__":
    main()
