"""PM-012: find the hole axes of the POLLEN shell STL and suggest solver orientations.

Run isolated with the CFD venv (outside the repo), paths as arguments:
  python -I cfd/lbm/stl_holes.py <pollen_mm.stl> [--json out.json]

Method: the outer-surface triangles (centroid radius > R_out - wall/2) are binned by
direction; a fine Fibonacci set of test directions is scored by the angular distance to
the nearest outer-surface centroid. Directions far from any outer surface are hole
openings; they are clustered and each cluster's mean direction is a hole axis.
The solver applies R = Rz Ry Rx to the body (pm012_lbm.cpp), flow along +x, so a hole
"facing the flow" points to -x after rotation, and "between holes" puts -x at the
direction farthest from every hole axis.
"""
import argparse
import json
import math
import sys

import numpy as np


def load_stl(path):
    with open(path, "rb") as f:
        data = f.read()
    n = int.from_bytes(data[80:84], "little")
    if 84 + 50 * n == len(data):
        rec = np.frombuffer(data[84:], dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]), count=n)
        return rec["v"].astype(np.float64)
    tris, cur = [], []
    for line in data.decode("ascii", "replace").splitlines():
        t = line.split()
        if t and t[0] == "vertex":
            cur.append([float(t[1]), float(t[2]), float(t[3])])
            if len(cur) == 3:
                tris.append(cur)
                cur = []
    return np.array(tris, dtype=np.float64)


def fib(n):
    i = np.arange(n) + 0.5
    phi = np.arccos(1 - 2 * i / n)
    th = math.pi * (1 + 5 ** 0.5) * i
    return np.stack([np.cos(th) * np.sin(phi), np.sin(th) * np.sin(phi), np.cos(phi)], 1)


def rot(rx, ry, rz):
    a, b, c = (math.radians(v) for v in (rx, ry, rz))
    Rx = np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])
    Ry = np.array([[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]])
    Rz = np.array([[math.cos(c), -math.sin(c), 0], [math.sin(c), math.cos(c), 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def angles_to_minus_x(d):
    """rx=0, ry, rz such that Rz Ry d = (-1, 0, 0)."""
    # Ry(b) maps (dx, dz) to x' = cos(b) dx + sin(b) dz, z' = -sin(b) dx + cos(b) dz; z' = 0 for b = atan2(dz, dx)
    b = math.atan2(d[2], d[0])
    x1 = math.cos(b) * d[0] + math.sin(b) * d[2]
    ry = math.degrees(b)
    # then Rz(c) turns (x1, y1) at angle atan2(y1, x1) onto -x
    rz = 180.0 - math.degrees(math.atan2(d[1], x1))
    rz = (rz + 180.0) % 360.0 - 180.0
    return 0.0, ry, rz


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stl")
    ap.add_argument("--json")
    ap.add_argument("--ntest", type=int, default=40000)
    a = ap.parse_args()
    tri = load_stl(a.stl)
    v = tri.reshape(-1, 3)
    c = 0.5 * (v.min(0) + v.max(0))
    cen = tri.mean(1) - c
    r = np.linalg.norm(cen, axis=1)
    R = float(np.linalg.norm(v - c, axis=1).max())
    outer = cen[r > R - 0.9]
    od = outer / np.linalg.norm(outer, axis=1, keepdims=True)
    T = fib(a.ntest)
    best = np.full(len(T), -1.0)
    for i in range(0, len(od), 4000):
        best = np.maximum(best, (T @ od[i:i + 4000].T).max(1))
    gap = np.degrees(np.arccos(np.clip(best, -1, 1)))
    # outer-surface triangle spacing: typical gap on the shell; holes are far above it
    thr = max(4.0, float(np.percentile(gap, 50)) * 4)
    hole = T[gap > thr]
    # cluster greedily by angle
    axes = []
    left = hole.copy()
    while len(left):
        seed = left[np.argmax(left @ left.mean(0))] if False else left[0]
        m = left @ seed > math.cos(math.radians(12))
        for _ in range(5):
            mu = left[m].mean(0)
            mu /= np.linalg.norm(mu)
            m = left @ mu > math.cos(math.radians(12))
        axes.append((mu, int(m.sum())))
        left = left[~m]
    axes = [(u, n) for u, n in axes if n >= 5]
    A = np.array([u for u, _ in axes])
    # "between holes": test direction maximising the angle to the nearest hole axis
    far = np.degrees(np.arccos(np.clip((T @ A.T).max(1), -1, 1)))
    j = int(np.argmax(far))
    hole_dir = A[np.argmax(A @ np.array([-1.0, 0, 0]))]
    o_hole = angles_to_minus_x(hole_dir)
    o_betw = angles_to_minus_x(T[j])
    for name, (rx, ry, rz), d in (("hole", o_hole, hole_dir), ("between", o_betw, T[j])):
        out = rot(rx, ry, rz) @ d
        assert out[0] < -0.9999, (name, out)
    pair = A @ A.T
    np.fill_diagonal(pair, -1)
    nn = np.degrees(np.arccos(np.clip(pair.max(1), -1, 1)))
    res = {
        "stl": a.stl.replace("\\", "/").split("/")[-1],
        "triangles": int(len(tri)),
        "bbox_centre_mm": [round(float(x), 4) for x in c],
        "outer_radius_mm": round(R, 4),
        "outer_triangles": int(len(outer)),
        "gap_threshold_deg": round(thr, 3),
        "holes_found": len(A),
        "hole_axes": [[round(float(x), 4) for x in u] for u in A],
        "hole_test_dirs_per_hole": [n for _, n in axes],
        "nearest_neighbour_hole_angle_deg": {"min": round(float(nn.min()), 2), "mean": round(float(nn.mean()), 2), "max": round(float(nn.max()), 2)},
        "between_dir": [round(float(x), 4) for x in T[j]],
        "between_angle_to_nearest_hole_deg": round(float(far[j]), 2),
        "orientation_hole_facing_flow": {"rx": round(o_hole[0], 3), "ry": round(o_hole[1], 3), "rz": round(o_hole[2], 3)},
        "orientation_between_holes": {"rx": round(o_betw[0], 3), "ry": round(o_betw[1], 3), "rz": round(o_betw[2], 3)},
    }
    s = json.dumps(res, indent=1)
    print(s)
    if a.json:
        with open(a.json, "w") as f:
            f.write(s + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
