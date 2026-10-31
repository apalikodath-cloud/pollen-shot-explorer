"""3D HIVE cell clean-entry test (PM-013), python port of viz/explorer/physics.js
buildCell3D / inside3D / classifyOblique3D (the reference classifier, no pruning).

The s = 0 section of one side (export_field.py sections "<side>_s0": names, P0, P1, inside, gate in the
shot frame x, z) is extruded across the lateral coordinate s (= y): the cell parts over |s| <= half + wallT,
the pivot plates and frame without limit. With ridge = True (default) the roof outer, upper lip, roof inner
and back-wall top drop by slope * |s| along the cell w axis (floor -> roof), as hive.py lowers the roof
linearly in |s| (two planar halves meeting at s = 0). Side walls (inner face at s = +-half, front rim,
outer face at s = +-(half + wallT)) close each cell.

Ball path: a planar path (integrateOblique X, Z) in the vertical plane of bearing psi; at shot-frame x the
lateral offset is s = (aimX - x) * tan(psi) (aimX = shot-frame x of the gate centre = Lh - d).
Clean = the ball centre enters the 3D inside region (section inside polygon, |s| <= half - R, below the
roof planes offset by R along their normal) before any contact (distance from the path step to a face
below R). Post-entry contact with the walls (rim-in, settling, rebound out) is not modelled.

Numbers: half 0.254 m (manual 20 in opening) CONFIRMED; slope derived from the opening profile
(14 in -> 7.61 in at the walls); wallT 0.0508 m (2 in) ASSUMED. Outputs are PREDICTED.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

ROOF_SLOPE = (0.3556 - 0.19329) / 0.254
CELL_HALF = 0.254
WALL_T = 0.0508
ROOF_PARTS = ("roof_outer", "upper_lip", "roof_inner", "back_wall")


@dataclass
class Face:
    name: str
    V: np.ndarray | None          # (n, 3) vertices (x, s, z), counter-clockwise about the normal
    ext: tuple | None             # (ax, az, bx, bz, s0, s1) for a section segment extruded over s
    n: np.ndarray | None = None   # unit normal
    c: float = 0.0
    M: np.ndarray | None = None   # (n, 4) per edge: in-plane inward normal (n x e) and offset


@dataclass
class Cell3D:
    faces: list
    inside: np.ndarray            # (m, 2) section inside polygon (x, z)
    half: float
    wall_t: float
    slope: float
    ridge: bool
    k: float
    kn: float
    w0: tuple
    w: tuple
    bb: tuple                     # classify skip box (x0, x1, z0, z1) of the section
    names: list = field(default_factory=list)


def make_face(name, V=None, ext=None):
    f = Face(name, None, ext)
    if ext is not None and math.isfinite(ext[4]) and math.isfinite(ext[5]):
        ax, az, bx, bz, s0, s1 = ext
        V = [[ax, s0, az], [bx, s0, bz], [bx, s1, bz], [ax, s1, az]]
    if V is not None:
        A = np.asarray(V, dtype=float)
        Q = np.roll(A, -1, axis=0)
        nx = np.sum((A[:, 1] - Q[:, 1]) * (A[:, 2] + Q[:, 2]))
        ny = np.sum((A[:, 2] - Q[:, 2]) * (A[:, 0] + Q[:, 0]))
        nz = np.sum((A[:, 0] - Q[:, 0]) * (A[:, 1] + Q[:, 1]))
        nrm = np.array([nx, ny, nz]) / math.sqrt(nx * nx + ny * ny + nz * nz)
        E = Q - A
        Mv = np.cross(np.broadcast_to(nrm, E.shape), E)
        f.V, f.n, f.c = A, nrm, float(nrm @ A[0])
        f.M = np.column_stack([Mv, np.sum(Mv * A, axis=1)])
    return f


def build_cell(sec, ridge=True, half=CELL_HALF, wall_t=WALL_T, slope=ROOF_SLOPE):
    """sec: dict with names, P0, P1, inside (the s = 0 section of one side)."""
    names, P0, P1 = list(sec["names"]), sec["P0"], sec["P1"]
    HT, k = half + wall_t, (slope if ridge else 0.0)
    idx = {nm: j for j, nm in enumerate(names)}
    wdir = {}
    for pre in ("up", "down"):
        j = idx.get(pre + "_back_wall")
        if j is None:
            continue
        dx, dz = P1[j][0] - P0[j][0], P1[j][1] - P0[j][1]
        L = math.hypot(dx, dz)
        wdir[pre] = (dx / L, dz / L)

    def v3(p, s, drop, W):
        return [p[0] - drop * W[0], s, p[1] - drop * W[1]]

    faces = []
    for j, nm in enumerate(names):
        a, b = P0[j], P1[j]
        pre = "up" if nm.startswith("up_") else "down" if nm.startswith("down_") else None
        part = nm[len(pre) + 1:] if pre else None
        if pre is None or pre not in wdir:
            faces.append(make_face(nm, ext=(a[0], a[1], b[0], b[1], -math.inf, math.inf)))
        elif not ridge or part not in ROOF_PARTS:
            faces.append(make_face(nm, ext=(a[0], a[1], b[0], b[1], -HT, HT)))
        else:
            W, dr = wdir[pre], k * HT
            if part == "back_wall":
                faces.append(make_face(nm, [v3(a, -HT, 0, W), v3(a, HT, 0, W), v3(b, HT, dr, W),
                                            v3(b, 0, 0, W), v3(b, -HT, dr, W)]))
            else:
                faces.append(make_face(nm, [v3(a, 0, 0, W), v3(b, 0, 0, W), v3(b, HT, dr, W), v3(a, HT, dr, W)]))
                faces.append(make_face(nm, [v3(a, 0, 0, W), v3(b, 0, 0, W), v3(b, -HT, dr, W), v3(a, -HT, dr, W)]))
    for pre in ("up", "down"):
        jo, ju = idx.get(pre + "_roof_outer"), idx.get(pre + "_underside")
        if pre not in wdir or jo is None or ju is None:
            continue
        W, C1, C2, C3 = wdir[pre], P0[jo], P1[jo], P0[ju]
        C4 = [C3[0] + C1[0] - C2[0], C3[1] + C1[1] - C2[1]]
        for sg in (1, -1):
            tag = "_pos" if sg > 0 else "_neg"
            sH, sT, dH, dT = sg * half, sg * HT, k * half, k * HT
            faces.append(make_face(pre + "_side_wall" + tag,
                                   [v3(C4, sH, 0, W), v3(C3, sH, 0, W), v3(C2, sH, dH, W), v3(C1, sH, dH, W)]))
            faces.append(make_face(pre + "_side_wall_rim" + tag,
                                   [v3(C3, sH, 0, W), v3(C3, sT, 0, W), v3(C2, sT, dT, W), v3(C2, sH, dH, W)]))
            faces.append(make_face(pre + "_side_wall_outer" + tag,
                                   [v3(C4, sT, 0, W), v3(C3, sT, 0, W), v3(C2, sT, dT, W), v3(C1, sT, dT, W)]))
    xs = [p[0] for p in P0] + [p[0] for p in P1] + [q[0] for q in sec["inside"]]
    zs = [p[1] for p in P0] + [p[1] for p in P1] + [q[1] for q in sec["inside"]]
    ri, wu = P0[idx["up_roof_inner"]], wdir["up"]
    return Cell3D(faces, np.asarray(sec["inside"], dtype=float), half, wall_t, slope, ridge, k,
                  math.sqrt(1 + k * k), (ri[0], ri[1]), wu, (min(xs), max(xs), min(zs), max(zs)), names)


# ---------------------------------------------------------------- vectorized geometry (over path steps)

def _seg_point2(px, pz, ax, az, bx, bz):
    abx, abz = bx - ax, bz - az
    den = abx * abx + abz * abz
    with np.errstate(invalid="ignore", divide="ignore"):
        t = np.where(den > 0, ((px - ax) * abx + (pz - az) * abz) / np.where(den > 0, den, 1.0), 0.0)
    t = np.clip(t, 0.0, 1.0)
    return np.hypot(px - (ax + t * abx), pz - (az + t * abz))


def seg_seg2(p0x, p0z, p1x, p1z, q0x, q0z, q1x, q1z):
    """2D segment distance (physics.js segSeg), arrays over the p segments; q a fixed segment."""
    rx, rz, sx, sz = p1x - p0x, p1z - p0z, q1x - q0x, q1z - q0z
    den = rx * sz - rz * sx
    ok = np.abs(den) > 1e-15
    dd = np.where(ok, den, 1.0)
    qpx, qpz = q0x - p0x, q0z - p0z
    t = (qpx * sz - qpz * sx) / dd
    u = (qpx * rz - qpz * rx) / dd
    cross = ok & (t >= 0) & (t <= 1) & (u >= 0) & (u <= 1)
    d = np.minimum.reduce([_seg_point2(p0x, p0z, q0x, q0z, q1x, q1z), _seg_point2(p1x, p1z, q0x, q0z, q1x, q1z),
                           _seg_point2(q0x, q0z, p0x, p0z, p1x, p1z), _seg_point2(q1x, q1z, p0x, p0z, p1x, p1z)])
    return np.where(cross, 0.0, d)


def seg_seg3(P0, P1, q0, q1):
    """3D segment distance (Ericson 5.1.9), P0, P1: (m, 3) arrays; q0, q1: (3,) one segment."""
    d1 = P1 - P0
    d2 = np.asarray(q1, float) - np.asarray(q0, float)
    r = P0 - np.asarray(q0, float)
    a = np.einsum("ij,ij->i", d1, d1)
    e = float(d2 @ d2)
    f = r @ d2
    c = np.einsum("ij,ij->i", d1, r)
    b = d1 @ d2
    EPS = 1e-300
    with np.errstate(invalid="ignore", divide="ignore"):
        den = a * e - b * b
        s = np.where(den > 0, np.clip((b * f - c * e) / np.where(den > 0, den, 1.0), 0, 1), 0.0)
        t = (b * s + f) / e
        lo, hi = t < 0, t > 1
        sa = np.where(a > EPS, a, 1.0)
        s = np.where(lo, np.clip(-c / sa, 0, 1), np.where(hi, np.clip((b - c) / sa, 0, 1), s))
        t = np.clip(t, 0, 1)
        # degenerate path step (a == 0): closest point of q to P0
        tq = np.clip(f / e, 0, 1)
        s = np.where(a <= EPS, 0.0, s)
        t = np.where(a <= EPS, tq, t)
    D = r + d1 * s[:, None] - np.outer(t, d2)
    return np.sqrt(np.einsum("ij,ij->i", D, D))


def _in_face(f, X):
    return np.all(X @ f.M[:, :3].T - f.M[:, 3] >= -1e-12, axis=1)


def seg_face(f, A, B):
    """Exact distance from each path step A[i]-B[i] ((m, 3), coordinates x, s, z) to face f."""
    if f.V is None:   # unbounded extrusion of a section segment: the 2D distance
        ax, az, bx, bz = f.ext[:4]
        return seg_seg2(A[:, 0], A[:, 2], B[:, 0], B[:, 2], ax, az, bx, bz)
    da, db = A @ f.n - f.c, B @ f.n - f.c
    out = np.full(len(A), np.inf)
    crossing = ((da <= 0) & (db >= 0)) | ((da >= 0) & (db <= 0))
    with np.errstate(invalid="ignore", divide="ignore"):
        t = np.where(da != db, da / np.where(da != db, da - db, 1.0), 0.0)
    Xc = A + t[:, None] * (B - A)
    hit = crossing & (da != db) & _in_face(f, Xc)
    flat = crossing & (da == db) & (_in_face(f, A) | _in_face(f, B))
    inA = _in_face(f, A - da[:, None] * f.n)
    inB = _in_face(f, B - db[:, None] * f.n)
    out = np.where(inA, np.abs(da), out)
    out = np.where(inB, np.minimum(out, np.abs(db)), out)
    nv = len(f.V)
    for i in range(nv):
        out = np.minimum(out, seg_seg3(A, B, f.V[i], f.V[(i + 1) % nv]))
    return np.where(hit | flat, 0.0, out)


def _inside_convex(px, pz, poly):
    pos = np.ones(len(px), bool)
    neg = np.ones(len(px), bool)
    m = len(poly)
    for i in range(m):
        a, b = poly[i], poly[(i + 1) % m]
        c = (b[0] - a[0]) * (pz - a[1]) - (b[1] - a[1]) * (px - a[0])
        pos &= ~(c < -1e-12)
        neg &= ~(c > 1e-12)
    return pos | neg


def inside3d(cell, x, s, z, R):
    """Ball centre (arrays x, s, z) inside the 3D inside region (radius R)."""
    x, s, z = np.atleast_1d(x).astype(float), np.atleast_1d(s).astype(float), np.atleast_1d(z).astype(float)
    ok = _inside_convex(x, z, cell.inside) & (np.abs(s) <= cell.half - R)
    if cell.k > 0:
        w = (x - cell.w0[0]) * cell.w[0] + (z - cell.w0[1]) * cell.w[1]
        ok &= ~(w > -cell.k * np.abs(s) - R * cell.kn)
    return ok


def step_dist(cell, A, B):
    """(min distance over faces, index of the first closest face) per step."""
    D = np.vstack([seg_face(f, A, B) for f in cell.faces])
    j = np.argmin(D, axis=0)
    return D[j, np.arange(D.shape[1])], j


def classify_oblique3d(X, Z, cell, d, h, R, aim_x, psi_deg):
    """physics.js classifyOblique3D. X, Z: the in-plane path (integrateOblique X, Z). Returns a dict
    result (clean / hit / miss), i, hit (face name), min_clear, s, entry_angle."""
    X, Z = np.asarray(X, float), np.asarray(Z, float)
    n = len(X)
    tp = math.tan(math.radians(psi_deg))
    m = R + 0.2
    x0, x1, z0, z1 = cell.bb
    ax, az, bx, bz = X[:-1] - d, Z[:-1] + h, X[1:] - d, Z[1:] + h
    inbox = ~((np.maximum(ax, bx) < x0 - m) | (np.minimum(ax, bx) > x1 + m) |
              (np.maximum(az, bz) < z0 - m) | (np.minimum(az, bz) > z1 + m))
    ii = np.nonzero(inbox)[0]
    ay, by = (aim_x - ax) * tp, (aim_x - bx) * tp
    min_c = math.inf
    if len(ii):
        ins = inside3d(cell, ax[ii], ay[ii], az[ii], R) & (ii > 0)
        A = np.column_stack([ax[ii], ay[ii], az[ii]])
        B = np.column_stack([bx[ii], by[ii], bz[ii]])
        best, jf = step_dist(cell, A, B)
        clear = best - R
        k_in = int(np.argmax(ins)) if ins.any() else len(ii)
        hits = clear < 0
        k_hit = int(np.argmax(hits)) if hits.any() else len(ii)
        if k_in <= k_hit and k_in < len(ii):
            i = int(ii[k_in])
            if k_in:
                min_c = float(np.min(clear[:k_in]))
            vx, vz = X[i] - X[i - 1], Z[i] - Z[i - 1]
            return {"result": "clean", "i": i, "hit": None, "min_clear": min_c, "s": float(ay[i]),
                    "entry_angle": math.degrees(math.atan2(-vz, abs(vx) + 1e-300))}
        if k_hit < len(ii):
            i = int(ii[k_hit])
            min_c = float(np.min(clear[:k_hit + 1]))
            return {"result": "hit", "i": i, "hit": cell.faces[int(jf[k_hit])].name, "min_clear": min_c,
                    "s": float(ay[i]), "entry_angle": None}
        min_c = float(np.min(clear))
    lx, lz = X[-1] - d, Z[-1] + h
    if inside3d(cell, lx, (aim_x - lx) * tp, lz, R)[0]:
        return {"result": "clean", "i": n - 1, "hit": None, "min_clear": min_c, "s": None, "entry_angle": None}
    return {"result": "miss", "i": n - 1, "hit": None, "min_clear": min_c, "s": None, "entry_angle": None}


def classify_path3d(X, S, Z, cell, R):
    """physics.js classifyPath3D: classify_oblique3d on a path already in the cell frame (x, lateral s and z
    absolute, e.g. robustness.integrate3d on the moving-robot launch of robustness.launch_state). Same result dict."""
    X, S, Z = np.asarray(X, float), np.asarray(S, float), np.asarray(Z, float)
    n = len(X)
    m = R + 0.2
    x0, x1, z0, z1 = cell.bb
    ax, ay, az, bx, by, bz = X[:-1], S[:-1], Z[:-1], X[1:], S[1:], Z[1:]
    inbox = ~((np.maximum(ax, bx) < x0 - m) | (np.minimum(ax, bx) > x1 + m) |
              (np.maximum(az, bz) < z0 - m) | (np.minimum(az, bz) > z1 + m))
    ii = np.nonzero(inbox)[0]
    min_c = math.inf
    if len(ii):
        ins = inside3d(cell, ax[ii], ay[ii], az[ii], R) & (ii > 0)
        A = np.column_stack([ax[ii], ay[ii], az[ii]])
        B = np.column_stack([bx[ii], by[ii], bz[ii]])
        best, jf = step_dist(cell, A, B)
        clear = best - R
        k_in = int(np.argmax(ins)) if ins.any() else len(ii)
        hits = clear < 0
        k_hit = int(np.argmax(hits)) if hits.any() else len(ii)
        if k_in <= k_hit and k_in < len(ii):
            i = int(ii[k_in])
            if k_in:
                min_c = float(np.min(clear[:k_in]))
            vx, vz = X[i] - X[i - 1], Z[i] - Z[i - 1]
            return {"result": "clean", "i": i, "hit": None, "min_clear": min_c, "s": float(ay[i]),
                    "entry_angle": math.degrees(math.atan2(-vz, abs(vx) + 1e-300))}
        if k_hit < len(ii):
            i = int(ii[k_hit])
            min_c = float(np.min(clear[:k_hit + 1]))
            return {"result": "hit", "i": i, "hit": cell.faces[int(jf[k_hit])].name, "min_clear": min_c,
                    "s": float(ay[i]), "entry_angle": None}
        min_c = float(np.min(clear))
    if inside3d(cell, X[-1], S[-1], Z[-1], R)[0]:
        return {"result": "clean", "i": n - 1, "hit": None, "min_clear": min_c, "s": None, "entry_angle": None}
    return {"result": "miss", "i": n - 1, "hit": None, "min_clear": min_c, "s": None, "entry_angle": None}
