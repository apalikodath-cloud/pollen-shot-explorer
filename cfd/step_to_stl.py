"""PM-012: convert the public AndyMark am-5851 POLLEN STEP to a binary STL (mm) for FluidX3D, then check it.

Run with the CFD venv (outside the repo), isolated, paths as arguments:
  $PM012_CFD_ROOT/venv/Scripts/python.exe -I cfd/step_to_stl.py <in.STEP> <out.stl> [--size-mm 1.2] [--curv 36]
Prints one JSON line: triangles, bounding box, watertight/orientation checks, Euler characteristic and
genus (a shell with 26 through-holes is a closed surface of genus 25), area, enclosed volume, vertex radii.
"""
import argparse
import json
import sys

import numpy as np


def read_binary_stl(path):
    raw = open(path, "rb").read()
    n = int(np.frombuffer(raw, dtype="<u4", count=1, offset=80)[0])
    if len(raw) != 84 + 50 * n:
        raise SystemExit("not a binary STL: %s" % path)
    rec = np.dtype([("nrm", "<f4", 3), ("v", "<f4", (3, 3)), ("attr", "<u2")])
    return np.frombuffer(raw, dtype=rec, count=n, offset=84)["v"].astype(np.float64)


def check_mesh(tri):
    # merge vertices on a 1e-5 mm grid
    key = np.round(tri.reshape(-1, 3) * 1e5).astype(np.int64)
    uniq, inv = np.unique(key, axis=0, return_inverse=True)
    f = inv.reshape(-1, 3)
    degenerate = int(np.sum((f[:, 0] == f[:, 1]) | (f[:, 1] == f[:, 2]) | (f[:, 0] == f[:, 2])))
    directed = np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]])
    und = np.sort(directed, axis=1)
    _, ecount = np.unique(und, axis=0, return_counts=True)
    _, dcount = np.unique(directed, axis=0, return_counts=True)
    V, E, F = len(uniq), len(ecount), len(f)
    chi = V - E + F
    p0, p1, p2 = tri[:, 0], tri[:, 1], tri[:, 2]
    cr = np.cross(p1 - p0, p2 - p0)
    area = 0.5 * np.linalg.norm(cr, axis=1).sum()
    vol = np.einsum("ij,ij->i", p0, np.cross(p1, p2)).sum() / 6.0
    r = np.linalg.norm(tri.reshape(-1, 3), axis=1)
    return {
        "triangles": F, "vertices": V, "edges": E, "degenerate_triangles": degenerate,
        "edges_not_shared_by_2": int(np.sum(ecount != 2)),
        "directed_edges_repeated": int(np.sum(dcount > 1)),
        "watertight": bool(np.all(ecount == 2)),
        "consistently_oriented": bool(np.all(dcount == 1)),
        "euler_characteristic": int(chi), "genus_if_connected": (2 - chi) / 2,
        "area_mm2": round(float(area), 2), "enclosed_volume_mm3": round(float(vol), 2),
        "bbox_min_mm": [round(float(x), 4) for x in tri.reshape(-1, 3).min(axis=0)],
        "bbox_max_mm": [round(float(x), 4) for x in tri.reshape(-1, 3).max(axis=0)],
        "vertex_radius_min_mm": round(float(r.min()), 4), "vertex_radius_max_mm": round(float(r.max()), 4),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step")
    ap.add_argument("stl")
    ap.add_argument("--size-mm", type=float, default=1.2, help="max triangle edge length (mm)")
    ap.add_argument("--curv", type=float, default=36.0, help="elements per 2*pi of curvature radius")
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args()
    if not a.check_only:
        import gmsh
        gmsh.initialize(argv=[], readConfigFiles=False)
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.option.setString("Geometry.OCCTargetUnit", "MM")
            gmsh.model.occ.importShapes(a.step)
            gmsh.model.occ.synchronize()
            gmsh.option.setNumber("Mesh.MeshSizeMax", a.size_mm)
            gmsh.option.setNumber("Mesh.MeshSizeMin", a.size_mm / 8.0)
            gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", a.curv)
            gmsh.option.setNumber("Mesh.Binary", 1)
            gmsh.model.mesh.generate(2)
            gmsh.write(a.stl)
            n_surf = len(gmsh.model.getEntities(2))
        finally:
            gmsh.finalize()
    else:
        n_surf = None
    out = {"stl": a.stl, "cad_surfaces": n_surf, "size_mm": a.size_mm, "curv": a.curv}
    out.update(check_mesh(read_binary_stl(a.stl)))
    print(json.dumps(out))
    return 0 if out["watertight"] and out["consistently_oriented"] else 1


if __name__ == "__main__":
    sys.exit(main())
