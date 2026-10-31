"""Independent check of the whole-field shot export (PM-008).

Standalone (not a unittest). Does NOT import export_field.py. Decodes the files from
viz/explorer/FIELD_DATA.md only, re-classifies sampled cells with src/robustness.integrate3d +
an exact polyline classifier (a different path from the exporter's integrate_batch + raster),
recomputes position geometry, and runs sanity checks. Clean model (--model, default = index.json
cell_model, "cell3d" since PM-019): "cell3d" = src/cell3d.py classify_path3d on the real 3D path (lateral
offset in the cell = release offset Lh tan(psi) minus the path's y); "section" = hive.classify_path on the
section at s_eff(psi) (the pre-PM-019 export).

    python -B tests/check_field_export.py [--src final|work] [--model cell3d|section] [--ncell 300] [--npos 200] [--seed 1]

Numbers printed are PREDICTED model output comparisons (not measurements).
"""
import argparse
import base64
import json
import math
import os
import sys

import numpy as np

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src import cell3d as c3  # noqa: E402
from src import feasibility as fz  # noqa: E402
from src import hive as hv  # noqa: E402
from src import robustness as rb  # noqa: E402
from src import shooter_spec as ss  # noqa: E402

OUT = os.path.join(ROOT, "viz", "explorer", "data", "field")
WORK = os.path.join(OUT, "_work")

# ---- grids, straight from FIELD_DATA.md ("grid" section)
H = (0.20, 0.35, 0.50, 0.65, 0.737)
DG = np.round(np.arange(0.55, 1.7501, 0.05), 3)
PSI = np.arange(0.0, 75.0 + 1e-9, 5.0)
VG = {"unfav": np.round(np.arange(5.0, 11.0001, 0.05), 3), "fav": np.round(np.arange(2.0, 10.0001, 0.1), 3)}
TG = {"unfav": np.round(np.arange(60.0, 89.8001, 0.2), 3), "fav": np.round(np.arange(20.0, 89.5001, 0.5), 3)}
SPINS = (0.0, 0.5, 1.0, 1.5)
# field geometry, typed in from FIELD_DATA.md / research/GEOMETRY_AUDIT.md (not imported from src/field_geom.py)
X_WALL, YC = 1.8009, 0.3236
BASE_HX, BASE_HY = 38.95 / 2 * 0.0254, 49.46 / 2 * 0.0254          # CONFIRMED A-frame base, centred on y = YC
OTHER_X, OTHER_Y, X_GATE = 0.6745, (0.3455, 0.9495), 0.401          # derived other-HIVE box, aim point
ROBOT = 18 * 0.0254                                                 # CONFIRMED 18 x 18 in chassis, release at its centre
NH, NP, ND = len(H), len(PSI), len(DG)

FAILS = []
MODEL = "cell3d"        # clean model the masks are checked against (main(): --model or index.json cell_model)


def report(name, ok, msg=""):
    print(("PASS " if ok else "FAIL ") + name + (" - " + msg if msg else ""), flush=True)
    if not ok:
        FAILS.append(name)


def tag(S):
    return f"Sp{S:.1f}_nominal"


def s_eff(psi):
    return min(0.3 * math.tan(math.radians(psi)), 0.2)


# ------------------------------------------------------------------ decoding (doc only)
def read_b64(path):
    with open(path) as fh:
        return base64.b64decode(fh.read())


def decode_mask(raw):
    n = int(np.frombuffer(raw, "<u4", 1, 0)[0])
    off = np.frombuffer(raw, "<u4", NP * NH + 1, 4).astype(np.int64)
    p = 4 + 4 * (NP * NH + 1)
    idx = np.frombuffer(raw, "<u4", n, p).astype(np.int64)
    mar = np.frombuffer(raw, "<u2", n, p + 4 * n)
    ang = np.frombuffer(raw, "<u2", n, p + 6 * n)
    assert off[-1] == n and len(raw) == p + 8 * n, "mask size mismatch vs doc layout"
    return idx, mar, ang, off


def load_masks(src, S, side):
    if src == "work":
        with np.load(os.path.join(WORK, f"{side}_{tag(S)}.npz")) as z:
            return z["idx"].astype(np.int64), z["mar"], z["ang"], z["off"].astype(np.int64)
    return decode_mask(read_b64(os.path.join(OUT, f"mask_{side}_{tag(S)}.b64.txt")))


def slice_grid(M, side, ip, ih):
    """bool (nd, nv, nth) from a decoded mask slice."""
    idx, _, _, off = M
    s = ip * NH + ih
    ii = idx[off[s]:off[s + 1]]
    nv, nt = len(VG[side]), len(TG[side])
    g = np.zeros(ND * nv * nt, bool)
    g[ii] = True
    return g.reshape(ND, nv, nt)


def best_k(m):
    """Largest all-True square side (own DP implementation)."""
    nv, nt = m.shape
    dp = np.zeros((nv + 1, nt + 1), np.int32)
    for i in range(1, nv + 1):
        for j in range(1, nt + 1):
            if m[i - 1, j - 1]:
                dp[i, j] = 1 + min(dp[i - 1, j], dp[i, j - 1], dp[i - 1, j - 1])
    return int(dp.max())


def square_ok(m, ci, cj, k):
    a, b = ci - k // 2, cj - k // 2
    return a >= 0 and b >= 0 and a + k <= m.shape[0] and b + k <= m.shape[1] and m[a:a + k, b:b + k].all()


# ------------------------------------------------------------------ independent re-classifier
_HV = {}


def hive_for(side, off):
    key = (side, round(off, 4))
    if key not in _HV:
        h = hv.Hive.from_json("pose_pos", lateral_offset=round(off, 4)) if off else hv.Hive.from_json("pose_pos")
        _HV[key] = h.mirrored() if side == "fav" else h
    return _HV[key]


_CELL = {}


def cell_for(side):
    """3D cell (src/cell3d.py) built from the s = 0 section of that side."""
    if side not in _CELL:
        h = hive_for(side, 0.0)
        _CELL[side] = c3.build_cell(dict(names=list(h.names), P0=np.asarray(h.P0, float).tolist(),
                                         P1=np.asarray(h.P1, float).tolist(),
                                         inside=np.asarray(h.inside, float).tolist()))
    return _CELL[side]


def aero(S):
    return fz.aero_case(tag(S), Cd="nominal", Cl=None if S == 0 else "nominal", k="nominal", path=ss.LIT)


def reclassify(cells):
    """cells: list of (side, h, S, psi, d, v, th). Exact polyline classification of the 3D
    flight in the vertical plane at bearing psi; shooter at x=-d (shot frame). MODEL "cell3d": 3D cell, the
    ball's lateral offset in the cell is s = Lh tan(psi) - y (aim at the gate centre, x = +-X_GATE);
    MODEL "section": section at s_eff(psi)."""
    res = [None] * len(cells)
    by = {}
    for n, c in enumerate(cells):
        by.setdefault(c[2], []).append(n)
    for S, ns in by.items():
        prm = aero(S)
        v = np.array([cells[n][5] for n in ns])
        th = np.radians([cells[n][6] for n in ns])
        ps = np.radians([cells[n][3] for n in ns])
        hh = np.array([cells[n][1] for n in ns])
        vel0 = np.stack([v * np.cos(th) * np.cos(ps), v * np.cos(th) * np.sin(ps), v * np.sin(th)], 1)
        pos0 = np.stack([np.zeros_like(v), np.zeros_like(v), hh], 1)
        w0 = rb.backspin_axis(vel0) * (S * v / prm["radius"])[:, None]
        q = dict(rho=prm["rho"], mass=prm["mass"], radius=prm["radius"], Cd=prm["Cd"],
                 c1=prm["Cl"][0] if prm["Cl"] else 0.0, clmax=prm["Cl"][1] if prm["Cl"] else 0.0,
                 k=prm["spin_decay_k"])
        P = rb.integrate3d(pos0, vel0, w0, q, dt=1e-3, z_stop=0.4)["P"].astype(float)
        for r, n in enumerate(ns):
            side, h, _, psi, d, _, _ = cells[n]
            x, z = P[r, :, 0] - d, P[r, :, 2]
            keep = (x > -0.8) & (z > 0.3)
            if keep.sum() < 2:
                res[n] = "miss"
                continue
            a, b = int(np.argmax(keep)), len(keep) - int(np.argmax(keep[::-1]))
            if MODEL == "cell3d":
                lh = d + X_GATE if side == "unfav" else max(d - X_GATE, 1e-3)
                sl = lh * math.tan(math.radians(psi)) - P[r, :, 1]
                res[n] = c3.classify_path3d(x[a:b], sl[a:b], z[a:b], cell_for(side), 0.0355)["result"]
            else:
                res[n] = hive_for(side, s_eff(abs(psi))).classify_path(np.c_[x[a:b], z[a:b]])["result"]
    return res


# ------------------------------------------------------------------ checks
def check_cells(src, M, ncell, rng):
    """Stratified sample: 1/3 inside windows, 1/3 within 2 cells of an edge, 1/3 anywhere."""
    print("\n== 1/2. cell re-classification (independent integrate3d + exact classifier, model " + MODEL + ") ==")
    cells, want, kind, nbr = [], [], [], []
    tries = 0
    while len(cells) < ncell and tries < 20000:
        tries += 1
        side = ("unfav", "fav")[len(cells) % 2]
        S = SPINS[int(rng.integers(len(SPINS)))]
        ip, ih = int(rng.integers(NP)), int(rng.integers(NH))
        g = slice_grid(M[(side, S)], side, ip, ih)
        mode = len(cells) % 3
        if mode == 2:
            idd, iv, it = int(rng.integers(ND)), int(rng.integers(g.shape[1])), int(rng.integers(g.shape[2]))
        else:
            ds = np.flatnonzero(g.any(axis=(1, 2)))
            if not ds.size:
                continue
            idd = int(rng.choice(ds))
            pts = np.argwhere(g[idd])
            iv, it = pts[int(rng.integers(len(pts)))]
            if mode == 1:                                  # step off by 1-2 cells (edge region)
                iv = int(np.clip(iv + rng.integers(-2, 3), 0, g.shape[1] - 1))
                it = int(np.clip(it + rng.integers(-2, 3), 0, g.shape[2] - 1))
        sl = g[idd]
        i0, i1 = max(iv - 1, 0), min(iv + 2, sl.shape[0])
        j0, j1 = max(it - 1, 0), min(it + 2, sl.shape[1])
        edge = bool((sl[i0:i1, j0:j1] != sl[iv, it]).any())
        cells.append((side, H[ih], S, float(PSI[ip]), float(DG[idd]), float(VG[side][iv]), float(TG[side][it])))
        want.append(bool(sl[iv, it])); nbr.append(edge); kind.append(mode)
    got = np.array([r == "clean" for r in reclassify(cells)])
    want, nbr, kind = np.array(want), np.array(nbr), np.array(kind)
    agree = got == want
    print(f"cells {len(cells)}: agreement {agree.mean():.3f} (CONFIRMED by re-run)")
    for m, nm in ((0, "mask-clean seeds"), (1, "near-edge seeds"), (2, "random cells")):
        s = kind == m
        print(f"  {nm}: n={s.sum()} agree={agree[s].mean():.3f}")
    dis = ~agree
    print(f"  disagreements {dis.sum()}: on window edge (neighbour differs) {int((dis & nbr).sum())}, "
          f"interior/not-edge {int((dis & ~nbr).sum())}")
    print(f"  mask-clean but recheck not clean: {int((want & ~got).sum())}; mask-not-clean but recheck clean: {int((~want & got).sum())}")
    for n in np.flatnonzero(dis & ~nbr)[:12]:
        print("   NOT-EDGE disagreement:", cells[n], "mask", want[n])
    for S in SPINS:
        s = np.array([c[2] == S for c in cells])
        if s.any():
            print(f"  S={S}: n={s.sum()} agree={agree[s].mean():.3f}")
    hi = np.array([c[3] > 60 for c in cells])
    if hi.any():
        print(f"  psi>60 (extrapolated): n={hi.sum()} agree={agree[hi].mean():.3f}")
    report("cells: non-edge disagreement <= 2%", (dis & ~nbr).sum() <= 0.02 * len(cells),
           f"{int((dis & ~nbr).sum())} non-edge")
    # mirror in y: -psi (3D path to the other side of the aim line) must give the same class
    sub = [i for i in range(len(cells)) if cells[i][3] > 0][:80]
    neg = [(c[0], c[1], c[2], -c[3], c[4], c[5], c[6]) for c in (cells[i] for i in sub)]
    # -psi 3D path is the y mirror; the section uses |psi| and the 3D cell is symmetric in s, so the class must be
    # identical. The signed -psi goes in (integrate3d flies to -y; cell3d: s = Lh tan(-psi) - y), so in the 3D-cell
    # model this exercises the mirrored path and the cell's s symmetry, not the same inputs twice.
    rneg = reclassify(neg)
    rpos = reclassify([cells[i] for i in sub])
    report("mirror (+psi vs -psi flight, 80 cells)", rneg == rpos)


def check_positions(src, M, npos, rng):
    print("\n== 3. field positions ==")
    xs, ys, X, Y, _ = rb.field_grid(0.05)
    ny, nx = X.shape
    # own grid rule: symmetric about x = 0, a row on the aim line y = 0, 0.10 m inside the walls
    report("grid symmetric about x = 0", np.allclose(xs, -xs[::-1]) and np.any(np.isclose(xs, 0.0)))
    report("grid has the aim line y = 0", np.any(np.isclose(ys, 0.0)) and np.allclose(np.diff(ys), 0.05))
    report("grid inside walls - 0.10", xs.max() <= X_WALL - 0.1 + 1e-9 and ys.min() >= -X_WALL + YC + 0.1 - 1e-9 and ys.max() <= X_WALL + YC - 0.1 + 1e-9)
    legal = np.vectorize(own_legal)(X, Y)
    raw = read_b64(os.path.join(OUT, "pos_status.b64.txt"))
    n = ny * nx
    st = np.frombuffer(raw, "u1", n, 0).reshape(ny, nx)
    ot = np.frombuffer(raw, "u1", n, n).reshape(ny, nx)
    fv = np.frombuffer(raw, "u1", n, 2 * n).reshape(ny, nx)
    di = np.frombuffer(raw, "<i2", n, 3 * n).reshape(ny, nx)
    pi = np.frombuffer(raw, "<i2", n, 5 * n).reshape(ny, nx)
    pp = np.frombuffer(raw, "<u2", n, 7 * n).reshape(ny, nx)
    report("pos_status size", len(raw) == 9 * n, f"{len(raw)} vs {9 * n}")
    d = np.abs(X)
    fav = X > 0
    Lh = np.where(fav, np.maximum(d - X_GATE, 1e-3), d + X_GATE)
    psi = np.degrees(np.arctan2(np.abs(Y), Lh))
    bad = {"fav": 0, "di": 0, "pi": 0, "psi": 0, "status": 0, "other": 0}
    allp = [(a, b) for a in range(ny) for b in range(nx)]
    pick = [allp[i] for i in rng.choice(len(allp), npos, replace=False)]
    for a, b in pick:
        e_di = int(np.clip(round((d[a, b] - 0.55) / 0.05), 0, ND - 1))
        e_pi = int(np.clip(round(psi[a, b] / 5.0), 0, NP - 1))
        e_st = 1 if not legal[a, b] else (2 if (d[a, b] < 0.525 - 1e-9 or d[a, b] > 1.775 + 1e-9) else (3 if psi[a, b] > 77.5 else 0))
        # other-HIVE crossing by exact segment/rectangle test (slab method)
        e_ot = int(seg_hits_rect(X[a, b], Y[a, b]))
        bad["fav"] += int(fv[a, b] != fav[a, b]); bad["di"] += int(di[a, b] != e_di)
        bad["pi"] += int(pi[a, b] != e_pi); bad["psi"] += int(abs(int(pp[a, b]) - round(psi[a, b] * 100)) > 1)
        bad["status"] += int(st[a, b] != e_st); bad["other"] += int(ot[a, b] != e_ot)
    print(f"  {npos} sampled positions, mismatches vs own recompute: {bad}")
    report("pos_status vs recompute (sampled)", sum(bad.values()) == 0)
    # whole-grid recheck of cheap fields
    full_st = np.where(~legal, 1, np.where((d < 0.525 - 1e-9) | (d > 1.775 + 1e-9), 2, np.where(psi > 77.5, 3, 0)))
    report("status whole grid", (full_st == st).all(), f"{int((full_st != st).sum())} cells differ")
    report("fav flag whole grid", (fv.astype(bool) == fav).all())
    full_ot = np.vectorize(seg_hits_rect)(X, Y)
    nd_ = int((full_ot != ot.astype(bool)).sum())
    report("other-HIVE flag whole grid (own exact test)", nd_ == 0, f"{nd_} cells differ of {n} (grid sampled line vs exact)")
    print(f"  status counts: " + str({int(k): int((st == k).sum()) for k in np.unique(st)}))
    # summaries vs masks
    tot = bad_cnt = bad_k = bad_sq = bad_ill = 0
    for S in SPINS:
        for side in ("unfav", "fav"):
            raw = read_b64(os.path.join(OUT, f"pos_{side}_{tag(S)}.b64.txt"))
            sz = NH * n
            cnt = np.frombuffer(raw, "<u2", sz, 0).reshape(NH, ny, nx)
            k_ = np.frombuffer(raw, "u1", sz, 2 * sz).reshape(NH, ny, nx)
            v_ = np.frombuffer(raw, "<u2", sz, 3 * sz).reshape(NH, ny, nx)
            t_ = np.frombuffer(raw, "<u2", sz, 5 * sz).reshape(NH, ny, nx)
            if len(raw) != 11 * sz:
                report(f"pos_{side}_{tag(S)} size", False, f"{len(raw)} vs {11 * sz}")
                continue
            wrong_side = (fv.astype(bool) != (side == "fav")) | (st != 0)
            bad_ill += int((cnt[:, wrong_side] != 0).sum() + (k_[:, wrong_side] != 0).sum())
            cache = {}
            ok_pos = [(a, b) for a, b in pick if not wrong_side[a, b]]
            for a, b in ok_pos:
                for ih in range(NH):
                    key = (int(pi[a, b]), ih)
                    if key not in cache:
                        cache[key] = slice_grid(M[(side, S)], side, key[0], ih)
                    m = cache[key][int(di[a, b])]
                    tot += 1
                    ec = int(m.sum())
                    if int(cnt[ih, a, b]) != min(ec, 65535):
                        bad_cnt += 1
                    ek = best_k(m) if ec else 0
                    if int(k_[ih, a, b]) != ek:
                        bad_k += 1
                    elif ek:
                        vv, tt = v_[ih, a, b] / 100.0, t_[ih, a, b] / 100.0
                        ci, cj = int(np.argmin(abs(VG[side] - vv))), int(np.argmin(abs(TG[side] - tt)))
                        if abs(VG[side][ci] - vv) > 0.006 or abs(TG[side][cj] - tt) > 0.006 or not square_ok(m, ci, cj, ek):
                            bad_sq += 1
    print(f"  summary checks over {tot} (pos,h,case,side) bins: count mismatches {bad_cnt}, k mismatches {bad_k}, "
          f"best-square centre not a valid all-clean kxk square {bad_sq}, nonzero in illegal/other-side {bad_ill}")
    report("pos summaries match masks", bad_cnt + bad_k + bad_sq + bad_ill == 0)


def _seg_cross(p1, p2, q1, q2):
    """proper or touching intersection of two closed segments (orientation test)."""
    def o(a, b, c):
        v = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        return 0 if abs(v) < 1e-12 else (1 if v > 0 else -1)
    d1, d2, d3, d4 = o(q1, q2, p1), o(q1, q2, p2), o(p1, p2, q1), o(p1, p2, q2)
    return d1 * d2 < 0 and d3 * d4 < 0


def own_legal(x, y, step=5.0):
    """Own footprint rule (independent of src/field_geom.py): some heading in a 5 deg scan puts all four
    chassis corners inside the walls and the chassis does not overlap the base (corner-in-polygon or
    edge crossing)."""
    h = ROBOT / 2
    base = [(-BASE_HX, YC - BASE_HY), (BASE_HX, YC - BASE_HY), (BASE_HX, YC + BASE_HY), (-BASE_HX, YC + BASE_HY)]
    if abs(x) < BASE_HX and abs(y - YC) < BASE_HY:
        return False
    for hd in np.arange(0.0, 90.0, step):
        c, s = math.cos(math.radians(hd)), math.sin(math.radians(hd))
        cor = [(x + c * a - s * b, y + s * a + c * b) for a, b in ((h, h), (-h, h), (-h, -h), (h, -h))]
        if any(abs(px) > X_WALL + 1e-9 or py < -X_WALL + YC - 1e-9 or py > X_WALL + YC + 1e-9 for px, py in cor):
            continue
        if any(abs(px) < BASE_HX - 1e-9 and abs(py - YC) < BASE_HY - 1e-9 for px, py in cor):
            continue
        if any(abs((bx - x) * c + (by - y) * s) < h - 1e-9 and abs(-(bx - x) * s + (by - y) * c) < h - 1e-9 for bx, by in base):
            continue
        if any(_seg_cross(cor[i], cor[(i + 1) % 4], base[j], base[(j + 1) % 4]) for i in range(4) for j in range(4)):
            continue
        return True
    return False


def seg_hits_rect(x, y):
    """Does the segment (x, y) -> aim point (X_GATE, 0) cross the open box |px| < 0.6745,
    0.3455 < py < 0.9495? exact slab test."""
    lo, hi = 0.0, 1.0
    for p0, p, a, b in ((x, X_GATE - x, -OTHER_X, OTHER_X), (y, -y, OTHER_Y[0], OTHER_Y[1])):
        if abs(p) < 1e-12:
            if not (a < p0 < b):
                return False
            continue
        t0, t1 = sorted(((a - p0) / p, (b - p0) / p))
        lo, hi = max(lo, t0), min(hi, t1)
        if lo >= hi:
            return False
    return True


def check_sanity(src, M):
    print("\n== 4. sanity ==")
    nan_bad = 0
    for (side, S), m in M.items():
        idx, mar, ang, off = m
        nv, nt = len(VG[side]), len(TG[side])
        if len(idx) and (idx.max() >= ND * nv * nt):
            report(f"idx range {side} {S}", False)
        if (np.diff(off) < 0).any():
            nan_bad += 1
        for s in range(NP * NH):
            seg = idx[off[s]:off[s + 1]]
            if len(seg) > 1 and (np.diff(seg) <= 0).any():
                nan_bad += 1
    report("mask idx sorted/unique/in range, offsets monotone", nan_bad == 0)
    # psi = 0 vs 2D spec cache
    g = ss.grid()
    for S in SPINS:
        try:
            z = ss.load(S, "nominal")
        except Exception as e:  # noqa
            print("  no 2D cache for", S, e)
            continue
        for side, gk in (("unfav", "unfav_t30"), ("fav", "fav_t30")):
            tot = agree = fp = fn = 0
            vs, ths = VG[side], TG[side]
            iv = np.array([int(np.argmin(abs(g.v - v))) for v in vs]); okv = np.abs(g.v[iv] - vs) < 1e-6
            it = np.array([int(np.argmin(abs(g.theta - t))) for t in ths]); okt = np.abs(g.theta[it] - ths) < 1e-6
            if not okv.any() or not okt.any():
                print(f"  S={S} {side}: 2D grid does not overlap"); continue
            for ih in range(NH):
                grid0 = slice_grid(M[(side, S)], side, 0, ih)
                for idd, d_ in enumerate(DG):
                    j = np.flatnonzero(np.isclose(g.d, d_))
                    if not j.size:
                        continue
                    ref = z[gk + "__clean"][ih, j[0]][np.ix_(iv[okv], it[okt])]
                    mine = grid0[idd][np.ix_(okv, okt)]
                    tot += ref.size; agree += int((ref == mine).sum())
                    fp += int((mine & ~ref).sum()); fn += int((~mine & ref).sum())
            report(f"psi=0 vs 2D S={S} {side}", tot > 0 and agree / tot >= 0.999,
                   f"agree {agree}/{tot}={agree / max(tot, 1):.5f}, export-only {fp}, 2D-only {fn}")
    # S=0 twin presence and coverage
    ok = all(os.path.exists(os.path.join(OUT if src == "final" else WORK,
                                         (f"mask_{s}_{tag(0.0)}.b64.txt" if src == "final" else f"{s}_{tag(0.0)}.npz")))
             for s in ("unfav", "fav"))
    report("S=0 files exist for both sides", ok)
    for side in ("unfav", "fav"):
        base = sum(len(M[(side, 0.0)][0][M[(side, 0.0)][3][s]:M[(side, 0.0)][3][s + 1]]) > 0 for s in range(NP * NH))
        for S in SPINS[1:]:
            lost = 0; both = 0
            for s in range(NP * NH):
                a = M[(side, S)][3]; b = M[(side, 0.0)][3]
                ds = np.unique(M[(side, S)][0][a[s]:a[s + 1]] // (len(VG[side]) * len(TG[side])))
                d0 = np.unique(M[(side, 0.0)][0][b[s]:b[s + 1]] // (len(VG[side]) * len(TG[side])))
                lost += len(np.setdiff1d(ds, d0)); both += len(ds)
            print(f"  {side} S={S}: (psi,h,d) bins with a spin window but NO S=0 window: {lost}/{both} "
                  f"(informational; twin = file exists, not 'same window')")


def check_doc_vs_code():
    print("\n== 5. doc vs code ==")
    report("s_eff same as robustness.s_eff", all(abs(s_eff(p) - rb.s_eff(p)) < 1e-12 for p in PSI))
    report("PSI_MAX is 60 in code (doc: cap, export extrapolates)", rb.PSI_MAX == 60.0)
    # cos(psi) scaling vs true 3D path in vertical plane, incl. gate crossing y offset
    prm = aero(1.0)
    v, th, psi = 8.0, 77.0, 60.0
    t, p = math.radians(th), math.radians(psi)
    v0 = np.array([[v * math.cos(t) * math.cos(p), v * math.cos(t) * math.sin(p), v * math.sin(t)]])
    q = dict(rho=prm["rho"], mass=prm["mass"], radius=prm["radius"], Cd=prm["Cd"], c1=prm["Cl"][0],
             clmax=prm["Cl"][1], k=prm["spin_decay_k"])
    P = rb.integrate3d(np.zeros((1, 3)), v0, rb.backspin_axis(v0) * (v / prm["radius"]), q, dt=2e-3, z_stop=-9, t_max=1.0)["P"][0]
    fam = fz.integrate_batch(np.array([v]), np.array([th]), 1.0, prm, z_stop=-9, t_max=1.0)
    n = min(len(P), fam["X"].shape[1])
    err = np.abs(P[:n, 0] - fam["X"][0, :n] * math.cos(p)).max()
    print(f"  cos(psi) projection max error vs 3D path (psi 60, CONFIRMED): {err:.2e} m")
    report("cos(psi) scaling holds for 3D flight (no wind, planar)", err < 5e-3)
    # lateral y at gate: the doc says ball can hit side wall from psi ~40-50; quantify
    for psi_ in (30, 40, 50, 60, 75):
        # ball from entry plane to gate travels depth along x of 0.306 m; lateral = depth*tan(psi)
        lat = 0.306 * math.tan(math.radians(psi_))
        print(f"  psi {psi_}: lateral run over 0.306 m cell depth = {lat:.3f} m vs half-width 0.254-0.0355 = {0.254 - 0.0355:.3f} m"
              + ("  -> side-wall hit likely (" + ("modelled by the 3D cell export" if MODEL == "cell3d" else "ignored by the section export") + ")"
                 if lat > 0.2185 else ""))
    cut = math.degrees(math.atan(0.2185 / 0.306))
    print(f"  side-wall limit by simple geometry: psi > {cut:.1f} deg (PREDICTED, straight line, ball centre)")
    print(f"  s_eff cap 0.2 m reached at psi {math.degrees(math.atan(0.2 / 0.3)):.1f}; code half-width limit "
          f"CELL_HALF-R = {rb.CELL_HALF - 0.0355:.4f}")
    print("  NOTE aim line y=0 is the UP cell; other HIVE centre 0.6472 away; field ys are on the 0.05 grid through y = 0 (exact +-y pairs near the aim line).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", choices=["final", "work"], default=None)
    ap.add_argument("--ncell", type=int, default=300)
    ap.add_argument("--npos", type=int, default=200)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--model", choices=["cell3d", "section"], default=None,
                    help="clean model to re-classify with (default: index.json cell_model, else cell3d)")
    a = ap.parse_args()
    src = a.src or ("final" if os.path.exists(os.path.join(OUT, "index.json")) else "work")
    model = a.model
    if model is None and os.path.exists(os.path.join(OUT, "index.json")):
        with open(os.path.join(OUT, "index.json"), encoding="utf8") as fh:
            model = json.load(fh).get("cell_model")
    globals()["MODEL"] = model or "cell3d"
    print("source:", src, "model:", MODEL)
    rng = np.random.default_rng(a.seed)
    M = {}
    for S in SPINS:
        for side in ("unfav", "fav"):
            try:
                M[(side, S)] = load_masks(src, S, side)
            except FileNotFoundError:
                print("  missing", side, S)
    SP = tuple(s for s in SPINS if ("unfav", s) in M and ("fav", s) in M)
    globals()["SPINS"] = SP
    if src == "final":
        idx = json.load(open(os.path.join(OUT, "index.json")))
        g = idx["grid"]
        report("index grid h/d/psi match doc", np.allclose(g["h"], H) and np.allclose(g["d"], DG) and np.allclose(g["psi"], PSI))
        for side in ("unfav", "fav"):
            report(f"index v/theta {side} match doc", np.allclose(g["v"][side], VG[side]) and np.allclose(g["theta"][side], TG[side]))
        print("  index.grid keys:", sorted(g.keys()), "psi_max_model:", g.get("psi_max_model"))
    check_cells(src, M, a.ncell, rng)
    if src == "final":
        check_positions(src, M, a.npos, rng)
    else:
        print("\n(positions skipped: final files not written yet)")
    check_sanity(src, M)
    check_doc_vs_code()
    print("\nFAILED:" if FAILS else "\nALL CHECKS PASSED", FAILS or "")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
