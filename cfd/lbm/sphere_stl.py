"""PM-012: smooth-sphere STL for the STL-path check (README "Release prerequisites").

Writes a binary STL of an icosphere centred on the origin (pm012_lbm rotates and scales the mesh about the STL
origin, so the ball centre must be the origin), outward-facing triangles, vertices on the sphere radius.
Standard-library Python only:
  python -I cfd/lbm/sphere_stl.py <out.stl> [--d 71.12] [--level 5]
Prints the triangle count and the mesh volume in mm^3 (pass it to pm012_lbm as svol=, which only feeds the
"volume/STL volume" diagnostic line). Level 5 = 20480 triangles; at D 94 cells the largest facet-to-sphere gap is
below 1e-3 cells.
"""
import argparse
import math
import struct


def icosphere(level):
    t = (1.0 + math.sqrt(5.0)) / 2.0
    verts = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),
             (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    verts = [tuple(c / math.sqrt(sum(a * a for a in v)) for c in v) for v in verts]
    faces = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6),
             (7, 1, 8), (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10),
             (8, 6, 7), (9, 8, 1)]
    for _ in range(level):
        cache, nf = {}, []

        def mid(i, j):
            key = (min(i, j), max(i, j))
            if key not in cache:
                a, b = verts[i], verts[j]
                m = [(a[k] + b[k]) * 0.5 for k in range(3)]
                n = math.sqrt(sum(c * c for c in m))
                verts.append(tuple(c / n for c in m))
                cache[key] = len(verts) - 1
            return cache[key]

        for a, b, c in faces:
            ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
            nf += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
        faces = nf
    return verts, faces


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out")
    ap.add_argument("--d", type=float, default=71.12, help="diameter in mm (default 71.12, the CAD outer diameter)")
    ap.add_argument("--level", type=int, default=5)
    a = ap.parse_args(argv)
    r = 0.5 * a.d
    verts, faces = icosphere(a.level)
    vol, flipped = 0.0, 0
    with open(a.out, "wb") as fh:
        fh.write(b"PM-012 smooth sphere icosphere".ljust(80, b" "))
        fh.write(struct.pack("<I", len(faces)))
        for f in faces:
            p = [[r * c for c in verts[i]] for i in f]
            u = [p[1][k] - p[0][k] for k in range(3)]
            w = [p[2][k] - p[0][k] for k in range(3)]
            n = [u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0]]
            if sum(n[k] * (p[0][k] + p[1][k] + p[2][k]) for k in range(3)) < 0.0:  # make it face outward
                p[1], p[2] = p[2], p[1]
                n = [-c for c in n]
                flipped += 1
            ln = math.sqrt(sum(c * c for c in n)) or 1.0
            vol += (p[0][0] * (p[1][1] * p[2][2] - p[1][2] * p[2][1]) - p[0][1] * (p[1][0] * p[2][2] - p[1][2] * p[2][0])
                    + p[0][2] * (p[1][0] * p[2][1] - p[1][1] * p[2][0])) / 6.0
            fh.write(struct.pack("<12fH", *[c / ln for c in n], *p[0], *p[1], *p[2], 0))
    exact = 4.0 / 3.0 * math.pi * r ** 3
    print("triangles %d  volume %.2f mm^3  (sphere %.2f, ratio %.6f)  flipped %d" % (len(faces), vol, exact, vol / exact, flipped))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
