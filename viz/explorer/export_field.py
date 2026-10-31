"""Whole-field clean windows for the 3D shot explorer (PM-005; 3D cell + rho 1.2041 since PM-019).

The shot is a planar flight in the vertical plane through the release point and the aim point
(spin axis perpendicular to that plane, no sideways Magnus), projected on the HIVE shot axis by
scaling X and VX by cos(psi).  Clean classification (PM-019) uses the 3D cell of src/cell3d.py
(side walls + pentagon roof, built from the tilt-30 s = 0 section) seen on that oblique plane:
src/feasibility.py Geometry.make(cell="cell3d", psi=psi), the same model the live solver
(solver.js, default sideWalls) uses; air density rho = 1.2041 kg/m^3 (feasibility.SWEEP_RHO).
The old section model (roof lowered at s_eff(psi) = min(0.3 tan psi, 0.2) m, no side walls) is
only kept for the exported s_eff sections that the page's sideWalls:false option reads.

    python -B viz/explorer/export_field.py compute [--workers 3] [--cl-bounds]   # resumable
    python -B viz/explorer/export_field.py finalize [--cl-bounds]                # index + masks
    python -B viz/explorer/export_field.py bench                                 # timing only

Writes only new files under viz/explorer/data/field/ (gitignored).
"""
from __future__ import annotations

import base64
import json
import math
import os
import sys
import time

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
from src import feasibility as fz  # noqa: E402
from src import shooter_spec as ss  # noqa: E402

OUT = os.path.join(HERE, "data", "field")
WORK = os.path.join(OUT, "_work")

# ----------------------------------------------------------------------------- grids
H_LIST = (0.20, 0.35, 0.50, 0.65, 0.737)
D_GRID = np.round(np.arange(0.55, 1.7501, 0.05), 3)           # 25 values, pivot-plane distance
PSI_STEP = 5.0
PSI_MAX_MODEL = 60.0           # robustness.PSI_MAX: beyond it the existing map assumes infeasible
PSI_MAX_EXPORT = 75.0          # extrapolation, flagged in the index
PSI_BINS = np.arange(0.0, PSI_MAX_EXPORT + 1e-9, PSI_STEP)
SIDE_GRID = {                  # coarser than the 2D page grid (v 0.05 / th 0.1) on purpose, logged
    "unfav": dict(v=np.round(np.arange(5.0, 11.0001, 0.05), 3),
                  th=np.round(np.arange(60.0, 89.8001, 0.2), 3)),
    "fav": dict(v=np.round(np.arange(2.0, 10.0001, 0.1), 3),
                th=np.round(np.arange(20.0, 89.5001, 0.5), 3)),
}
# field grid and release-point tests: src/field_geom.py (shared with robustness.py and, as a JS
# twin, viz/explorer/solver.js). x = shot axis (distance from HIVE pivot plane)
from src import field_geom as fg  # noqa: E402
X_WALL, Y_LO, Y_HI = fg.X_WALL, fg.Y_LO, fg.Y_HI
WALL_MARGIN, X_MIN_EVAL = fg.WALL_MARGIN, 0.55
BASE_X, BASE_Y = fg.BASE_HALF_X, (fg.BASE_CY - fg.BASE_HALF_Y, fg.BASE_CY + fg.BASE_HALF_Y)
OTHER_HIVE_X, OTHER_HIVE_Y = fg.OTHER_HIVE_X, fg.OTHER_HIVE_Y
X_GATE = fg.X_GATE
CELL_DEPTH, CELL_HALF, R_BALL = 0.30556, 0.254, 0.0355
# straight-line side-wall estimate (DERIVED, PREDICTED): a ball entering on the cell centre line moves
# depth*tan(psi) sideways across the cell depth; it must stay within |y| < half-width - R = 0.2185 m
PSI_SIDE_WALL = math.degrees(math.atan((CELL_HALF - R_BALL) / CELL_DEPTH))
FIELD_STEP = fg.FIELD_STEP


def s_eff(psi_deg):
    return float(min(0.3 * math.tan(math.radians(abs(psi_deg))), 0.2))


def case_list(cl_bounds):
    out = [(S, "nominal") for S in (0.0, 0.5, 1.0, 1.5)]
    if cl_bounds:
        out += [(S, v) for S in (0.5, 1.0, 1.5) for v in ("Cl_low", "Cl_high")]
    return out


def case_tag(S, var):
    return ss.tag(S, var).replace("+", "p").replace("-", "m")


_GEOM = {}
_SEC = {}
# Clean-entry model used by window_block: "cell3d" (PM-019 default, = the live solver with side walls) or
# "section" (pre-PM-019: 2D section at the lateral offset s_eff(psi); kept for section-model comparisons).
CELL_MODEL = "cell3d"


def cell_geom(side, psi):
    """3D-cell geometry on the oblique plane of bearing psi (PM-019; raster cached on disk)."""
    key = (side, float(psi))
    if key not in _GEOM:
        _GEOM[key] = fz.Geometry.make(favorable=(side == "fav"), cell="cell3d", psi=float(psi))
    return _GEOM[key]


def section_for(side, off):
    """Section-model HIVE at lateral offset off (the exported s_eff sections; CELL_MODEL "section")."""
    key = (side, round(off, 4))
    if key not in _SEC:
        _SEC[key] = fz.Geometry.make(favorable=(side == "fav"), lateral_offset=round(off, 4), cell="section")
    return _SEC[key]


def geom_for(side, off):
    """Pre-PM-019 name: section-model HIVE at lateral offset off (same as section_for)."""
    return section_for(side, off)


def window_geom(side, psi):
    """The geometry window_block classifies against for bearing psi, per CELL_MODEL."""
    return cell_geom(side, psi) if CELL_MODEL == "cell3d" else section_for(side, s_eff(psi))


def _prebuild(args):
    side, psi = args
    cell_geom(side, psi)
    return side, psi


def aero(S, var):
    _, Cd, Cl, k = next(v for v in ss.variants(S) if v[0] == var)
    return fz.aero_case(ss.tag(S, var), Cd=Cd, Cl=None if S == 0.0 else Cl, k=k, path=ss.LIT)


# ----------------------------------------------------------------------------- compute
def window_block(fam, side, psi, h):
    """clean/margin/ang (nd, nb) for one block of paths, bearing psi (deg), release height h."""
    cs = np.float32(math.cos(math.radians(psi)))
    fs = {"X": fam["X"] * cs, "Z": fam["Z"], "VX": fam["VX"] * cs, "VZ": fam["VZ"],
          "mono": fam["mono"]}
    cand = fz.evaluate_gate(fs, window_geom(side, psi), h, D_GRID[0] - 0.02,
                            D_GRID[-1] + 0.02, chunk_elems=2_000_000)
    cl, mg, an, _, _ = fz.grid_from_candidates(cand, fam["X"].shape[0], D_GRID)
    return cl, mg, an


def job(args):
    side, S, var, workdir, block = args
    path = os.path.join(workdir, f"{side}_{case_tag(S, var)}.npz")
    if os.path.exists(path):
        return path, 0.0
    t0 = time.time()
    gr = SIDE_GRID[side]
    V, TH = np.meshgrid(gr["v"], gr["th"], indexing="ij")
    V, TH = V.ravel(), TH.ravel()
    ntraj = V.size
    prm = aero(S, var)
    keys = [(ip, ih) for ip in range(len(PSI_BINS)) for ih in range(len(H_LIST))]
    acc = {k: ([], [], []) for k in keys}
    for b0 in range(0, ntraj, block):
        b1 = min(ntraj, b0 + block)
        fam = fz.integrate_batch(V[b0:b1], TH[b0:b1], S, prm, z_stop=0.4)
        fam["mono"] = np.all(np.diff(fam["X"], axis=1) >= 0, axis=1)
        for ip, psi in enumerate(PSI_BINS):
            for ih, h in enumerate(H_LIST):
                cl, mg, an = window_block(fam, side, psi, h)
                dd, jj = np.nonzero(cl)
                if dd.size:
                    a = acc[(ip, ih)]
                    a[0].append((dd * ntraj + b0 + jj).astype(np.uint32))
                    a[1].append(np.clip(np.round(mg[dd, jj] * 1e4), 0, 65535).astype(np.uint16))
                    a[2].append(np.clip(np.round(an[dd, jj] * 100), 0, 65535).astype(np.uint16))
        print(f"  {side} {case_tag(S, var)} {b1}/{ntraj} {time.time() - t0:.0f}s", flush=True)
    idx, mar, ang, off = [], [], [], [0]
    for k in keys:
        a = acc[k]
        n = 0
        if a[0]:
            i = np.concatenate(a[0])
            o = np.argsort(i)
            idx.append(i[o]); mar.append(np.concatenate(a[1])[o]); ang.append(np.concatenate(a[2])[o])
            n = i.size
        off.append(off[-1] + n)
    tmp = path + ".tmp.npz"
    np.savez_compressed(tmp, idx=np.concatenate(idx) if idx else np.zeros(0, np.uint32),
                        mar=np.concatenate(mar) if mar else np.zeros(0, np.uint16),
                        ang=np.concatenate(ang) if ang else np.zeros(0, np.uint16),
                        off=np.array(off, np.int64))
    os.replace(tmp, path)
    return path, time.time() - t0


def cmd_compute(workers, cl_bounds, block=1500):
    os.makedirs(WORK, exist_ok=True)
    jobs = [(side, S, var, WORK, block) for S, var in case_list(cl_bounds)
            for side in ("unfav", "fav")]
    t0 = time.time()
    if workers > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=workers) as ex:
            # build the 3D-cell rasters once (disk cache) before the jobs read them
            for side, psi in ex.map(_prebuild, [(sd, float(ps)) for sd in ("unfav", "fav") for ps in PSI_BINS]):
                pass
            print(f"rasters ready {time.time() - t0:.0f}s", flush=True)
            for p, dt in ex.map(job, jobs):
                print(f"done {os.path.basename(p)} {dt:.0f}s (total {time.time() - t0:.0f}s)", flush=True)
    else:
        for j in jobs:
            p, dt = job(j)
            print(f"done {os.path.basename(p)} {dt:.0f}s", flush=True)


def cmd_bench():
    side, S, var = "unfav", 1.0, "nominal"
    gr = SIDE_GRID[side]
    V, TH = np.meshgrid(gr["v"], gr["th"], indexing="ij")
    V, TH = V.ravel()[:1500], TH.ravel()[:1500]
    t0 = time.time()
    fam = fz.integrate_batch(V, TH, S, aero(S, var), z_stop=0.4)
    fam["mono"] = np.all(np.diff(fam["X"], axis=1) >= 0, axis=1)
    print("integrate", time.time() - t0, fam["X"].shape)
    t0 = time.time()
    for psi in (0.0, 30.0, 60.0):
        for h in H_LIST:
            window_block(fam, side, psi, h)
    print("15 evals", time.time() - t0)


# ----------------------------------------------------------------------------- finalize
def field_positions():
    # symmetric grid: x = k 0.05 for |x| <= 1.70, y = k 0.05 (a row on the aim line y = 0)
    xs, ys, X, Y = fg.field_grid(FIELD_STEP, WALL_MARGIN)
    # legal = the default robot (18 x 18 in, CONFIRMED R102) fits at SOME heading with the release
    # point at the chassis centre (offset 0, ASSUMED): inside the walls and off the A-frame base
    legal = fg.chassis_ok(X, Y)
    d = np.abs(X)
    fav = X > 0                    # pose_pos: favourable (mouth-facing) side is +x
    Lh = np.where(fav, np.maximum(d - X_GATE, 1e-3), d + X_GATE)
    psi = np.degrees(np.arctan2(np.abs(Y), Lh))
    # straight line from (x, y) to the aim point (X_GATE, 0) crosses the other HIVE plan box
    # (|x| < 0.6745, y 0.3455-0.9495, derived; ASSUMED as blocking): exact segment test
    other = fg.sight_blocked(X, Y)
    status = np.zeros(X.shape, np.uint8)       # 0 ok, 1 illegal (robot footprint), 2 d outside table,
    status[psi > PSI_MAX_EXPORT + PSI_STEP / 2] = 3   # 3 psi beyond export max (2 wins if both)
    status[d < D_GRID[0] - 0.025 - 1e-9] = 2   # 2 d outside table
    status[d > D_GRID[-1] + 0.025 + 1e-9] = 2
    status[~legal] = 1
    di = np.clip(np.round((d - D_GRID[0]) / 0.05), 0, len(D_GRID) - 1).astype(np.int16)
    pi = np.clip(np.round(psi / PSI_STEP), 0, len(PSI_BINS) - 1).astype(np.int16)
    return dict(xs=xs, ys=ys, X=X, Y=Y, legal=legal, fav=fav, other=other, status=status,
                di=di, pi=pi, psi=psi)


def load_job(side, S, var):
    with np.load(os.path.join(WORK, f"{side}_{case_tag(S, var)}.npz")) as z:
        return z["idx"], z["mar"], z["ang"], z["off"]


def summarize(side, S, var):
    """summary arrays (npsi, nh, nd): count, k, v, th, ang(0.01deg), margin(0.1mm); k=0 empty."""
    gr = SIDE_GRID[side]
    nv, nth = len(gr["v"]), len(gr["th"])
    ntraj = nv * nth
    idx, mar, ang, off = load_job(side, S, var)
    shp = (len(PSI_BINS), len(H_LIST), len(D_GRID))
    cnt = np.zeros(shp, np.uint32); kk = np.zeros(shp, np.uint8)
    vv = np.zeros(shp, np.float32); tt = np.zeros(shp, np.float32)
    aa = np.zeros(shp, np.uint16); mm = np.zeros(shp, np.uint16)
    for ip in range(shp[0]):
        for ih in range(shp[1]):
            s, e = off[ip * shp[1] + ih], off[ip * shp[1] + ih + 1]
            if e == s:
                continue
            i = idx[s:e].astype(np.int64)
            for dd in np.unique(i // ntraj):
                sel = (i // ntraj) == dd
                loc = i[sel] % ntraj
                m = np.zeros((nv, nth), bool)
                m[loc // nth, loc % nth] = True
                k, i0, j0 = ss.best_square(m)
                cnt[ip, ih, dd] = loc.size
                if k:
                    ci, cj = i0 + k // 2, j0 + k // 2
                    kk[ip, ih, dd] = k
                    vv[ip, ih, dd] = gr["v"][ci]; tt[ip, ih, dd] = gr["th"][cj]
                    q = np.flatnonzero(loc == ci * nth + cj)
                    if q.size:
                        aa[ip, ih, dd] = ang[s:e][sel][q[0]]; mm[ip, ih, dd] = mar[s:e][sel][q[0]]
    return dict(count=cnt, k=kk, v=vv, th=tt, ang=aa, margin=mm)


def b64_write(path, raw):
    with open(path, "w") as fh:
        fh.write(base64.b64encode(raw).decode())


def _params(S, var):
    import export_explorer as ee
    return ee.case_params(S, var)


def cmd_finalize(cl_bounds):
    pos = field_positions()
    cases = [(S, v) for S, v in case_list(cl_bounds)
             if all(os.path.exists(os.path.join(WORK, f"{s}_{case_tag(S, v)}.npz")) for s in ("unfav", "fav"))]
    summary, case_meta, nbytes = {}, [], 0
    ny, nx = pos["X"].shape
    for S, var in cases:
        tag = case_tag(S, var)
        files, summ = {}, {}
        for side in ("unfav", "fav"):
            idx, mar, ang, off = load_job(side, S, var)
            raw = np.array([idx.size], "<u4").tobytes() + off.astype("<u4").tobytes() \
                + idx.astype("<u4").tobytes() + mar.astype("<u2").tobytes() + ang.astype("<u2").tobytes()
            name = f"mask_{side}_{tag}.b64.txt"
            if side == "fav" and var != "nominal":
                # size budget: near-side Cl_low/Cl_high masks are left out (summary + pos files stay)
                files[side] = dict(file=None, n=int(idx.size), n_offsets=int(off.size),
                                   note="mask omitted (size budget); use summary and pos file")
            else:
                b64_write(os.path.join(OUT, name), raw)
                nbytes += os.path.getsize(os.path.join(OUT, name))
                files[side] = dict(file=name, n=int(idx.size), n_offsets=int(off.size))
            sm = summarize(side, S, var)
            summ[side] = {k: (v.ravel().tolist() if k not in ("v", "th") else np.round(v.ravel(), 3).tolist())
                          for k, v in sm.items()}
            ok = (pos["status"] == 0) & (pos["fav"] == (side == "fav"))
            arrs = []
            for key, dt, scale in (("count", "<u2", 1), ("k", "u1", 1), ("v", "<u2", 100),
                                   ("th", "<u2", 100), ("ang", "<u2", 1), ("margin", "<u2", 1)):
                a = np.zeros((len(H_LIST), ny, nx), np.float64)
                for ih in range(len(H_LIST)):
                    vals = sm[key][pos["pi"], ih, pos["di"]].astype(np.float64)
                    a[ih] = np.where(ok, vals, 0)
                arrs.append(np.clip(np.round(a * scale), 0, 65535).astype(dt).tobytes())
            pname = f"pos_{side}_{tag}.b64.txt"
            b64_write(os.path.join(OUT, pname), b"".join(arrs))
            nbytes += os.path.getsize(os.path.join(OUT, pname))
            files[side]["pos_file"] = pname
        summary[tag] = summ
        case_meta.append(dict(tag=tag, S=S, var=var, files=files, params=_params(S, var)))
    sections = {}
    for side in ("unfav", "fav"):
        for psi in PSI_BINS:
            off = round(s_eff(psi), 4)
            key = f"{side}_s{off:g}"
            if key not in sections:
                h = section_for(side, off).hive
                sections[key] = dict(names=list(h.names), P0=np.round(h.P0, 5).tolist(),
                                     P1=np.round(h.P1, 5).tolist(), inside=np.round(h.inside, 5).tolist(),
                                     gate=np.round(h.gate, 5).tolist(), normal=np.round(h.normal_out, 6).tolist())
    raw = (pos["status"].astype("u1").tobytes() + pos["other"].astype("u1").tobytes()
           + pos["fav"].astype("u1").tobytes() + pos["di"].astype("<i2").tobytes()
           + pos["pi"].astype("<i2").tobytes() + np.round(pos["psi"] * 100).astype("<u2").tobytes())
    b64_write(os.path.join(OUT, "pos_status.b64.txt"), raw)
    index = dict(
        label="PREDICTED: whole-field oblique clean windows, 3D cell model (src/cell3d.py, side walls + "
              "pentagon roof, the live solver's default) with literature aero (research/params_lit.json, "
              "ASSUMED, not POLLEN measurements) at rho 1.2041 kg/m^3 (derived, still air). Window = clean "
              "air-only entry, not a hit probability; no repeatability claim.",
        format_version=2,
        cell_model=CELL_MODEL,
        rho=round(float(fz.SWEEP_RHO), 4),
        provenance=dict(window="PREDICTED", aero="ASSUMED (literature, research/params_lit.json)",
                        cell_model="PREDICTED geometry model: 3D cell of src/cell3d.py from the CONFIRMED tilt-30 "
                                   "section (PM-019; before PM-019 this export used the section model with s_eff)",
                        rho="derived 1.2041 kg/m^3 (src/air.py STILL_AIR_RHO; was 1.20 before PM-019)",
                        hive_section_tilt30="CONFIRMED (official CAD, Manual TU07)",
                        tilt_bounds="derived",
                        s_eff="ASSUMED; sections only (page option sideWalls:false), not used for the masks",
                        psi_gt_60="ASSUMED extrapolation: robustness.py treats psi > 60 as infeasible",
                        other_hive_footprint="derived box, ASSUMED as blocking (straight sight line, no flight height)",
                        robot_footprint="18 x 18 in CONFIRMED (R102); release at the chassis centre ASSUMED; any heading",
                        tilt_bounds_now="derived 28.80-31.77 deg (wide 25.90-34.83), data/hive_geometry.json; this export is tilt 30 only",
                        release_heights="ASSUMED (robot height limit R105)"),
        frame=dict(x="field x = shot axis: distance from the HIVE pivot plane (x = 0); d = |x|",
                   y="along the pivot axis; up-cell aim point at y = 0 (red HIVE centre); the other alliance "
                     "HIVE plan box (grown by R) is |x| < %.4f, y %.4f-%.4f; field inner wall |x| = 1.8009, y in [%.4f, %.4f]"
                     % (OTHER_HIVE_X, OTHER_HIVE_Y[0], OTHER_HIVE_Y[1], Y_LO, Y_HI),
                   far_side="unfav (far / unfavourable): x < 0 for pose_pos; gate centre is d + %.3f m away "
                            "horizontally" % X_GATE,
                   near_side="fav (near / favourable): x > 0 for pose_pos, mouth faces the shooter; gate centre "
                             "d - %.3f m away horizontally" % X_GATE,
                   pose="pose_pos (red up cell on +x). For pose_neg mirror x -> -x; for the blue HIVE also mirror y "
                        "(y -> 0.6472 - y). The mouth (favourable) and back (unfavourable) sides swap each time the HIVE tips.",
                   hives="both HIVEs hang from one A-frame at the field centre, centre-to-centre 0.6472 m (CAD); "
                         "A-frame base |x| < %.6f, y in [%.6f, %.6f] (38.95 x 49.46 in, CONFIRMED)" % (BASE_X, BASE_Y[0], BASE_Y[1]),
                   psi="psi = atan(|y| / Lh), Lh = d + 0.401 (far) or max(d - 0.401, 1e-3) (near); "
                       "symmetric in sign(y)"),
        grid=dict(h=list(H_LIST), d=D_GRID.tolist(), psi=PSI_BINS.tolist(), psi_max_model=PSI_MAX_MODEL,
                  psi_max_export=PSI_MAX_EXPORT,
                  psi_side_wall=round(PSI_SIDE_WALL, 2),
                  psi_side_wall_how="PREDICTED straight-line estimate: atan((0.254 - 0.0355) / 0.30556) with cell half-width 0.254, ball radius 0.0355, cell depth 0.30556 (all CONFIRMED/derived, hive_geometry.json); ball enters on the centre line, no lateral roof profile; near-side estimate; far side not checked (it depends on entry angle and height, 32-82 deg, research/GEOMETRY_AUDIT.md fix 6). The masks in this export (PM-019) and the live solver (solver.js, default sideWalls) model the side walls in 3D (PM-013), so this estimate is informational only (FIELD_DATA.md, 3D cell model)",
                  side_wall_risk=[int(p + PSI_STEP / 2 > PSI_SIDE_WALL) for p in PSI_BINS],
                  v={s: SIDE_GRID[s]["v"].tolist() for s in SIDE_GRID},
                  theta={s: SIDE_GRID[s]["th"].tolist() for s in SIDE_GRID},
                  order="mask file = u32 n | u32 off[nPsi*nH+1] | u32 idx[n] | u16 margin[n] | u16 ang[n]; slice "
                        "(ip*nH+ih) = entries off[s]..off[s+1]; idx = id*nV*nTh + iv*nTh + ith (sorted)",
                  coarsened="v/theta steps: far 0.05/0.2 (page 2D grid 0.05/0.1); near 0.1/0.5; d step 0.05; "
                            "psi step 5 deg"),
        field_grid=dict(step=FIELD_STEP, xs=pos["xs"].tolist(), ys=pos["ys"].tolist(), nx=nx, ny=ny,
                        pos_status="pos_status.b64.txt",
                        status_codes={"0": "ok", "1": "illegal (robot footprint: 18 x 18 in chassis, any heading, release at its "
                                                   "centre, crosses a wall or the A-frame base)", "2": "d outside table",
                                      "3": "psi beyond export max"}),
        field_geom=dict(x_wall=X_WALL, y_lo=round(Y_LO, 6), y_hi=round(Y_HI, 6), base_half_x=round(BASE_X, 6),
                        base_half_y=round(fg.BASE_HALF_Y, 6), base_cy=fg.BASE_CY, other_hive_x=OTHER_HIVE_X,
                        other_hive_y=list(OTHER_HIVE_Y), x_gate=X_GATE, robot_l=fg.ROBOT_L, robot_w=fg.ROBOT_W,
                        robot_l_expanded=fg.ROBOT_L_EXPANDED, source="src/field_geom.py (JS twin in solver.js)"),
        integrator=dict(method="RK4 fixed step", dt=2e-3, z_stop=0.4,
                        frame="planar flight in the vertical plane of the bearing; X, VX scaled by cos(psi)"),
        sections=sections, cases=case_meta, summary=summary,
        file_formats="see viz/explorer/FIELD_DATA.md")
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, separators=(",", ":"))
    print("wrote", OUT, "mask+pos bytes", nbytes, "index bytes", os.path.getsize(os.path.join(OUT, "index.json")))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["compute", "finalize", "bench"])
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--cl-bounds", action="store_true")
    a = ap.parse_args()
    if a.cmd == "bench":
        cmd_bench()
    elif a.cmd == "compute":
        cmd_compute(a.workers, a.cl_bounds)
    else:
        cmd_finalize(a.cl_bounds)
