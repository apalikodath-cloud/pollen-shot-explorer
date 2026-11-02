"""Export the shooter-spec clean windows for the 3D shot explorer (viz/explorer/index.html).

Reads data/_spec_cache/*.npz (written by src/shooter_spec.py; PREDICTED, literature aero from
research/params_lit.json; since PM-019 classified with the 3D cell of src/cell3d.py at rho 1.2041,
tilts 28.80 / 30 / 31.77) and the shot-frame HIVE from src/feasibility.py. Writes:

    viz/explorer/data/index.json        grid, HIVE segments per geometry, aero params per case
    viz/explorer/data/<S>_<var>_<geom>.bin   clean cells only (sparse); .b64.txt = base64 copy the page loads

.bin layout (little endian): uint32 n | uint32 idx[n] (flat index into h, d, v, theta) |
uint16 margin[n] (0.1 mm, clearance before entry) | uint16 ang[n] (0.01 deg, descent at gate).

    python -B viz/explorer/export_explorer.py
"""
from __future__ import annotations

import base64
import json
import os
import sys

import numpy as np

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from src import feasibility as fz  # noqa: E402
from src import shooter_spec as ss  # noqa: E402

OUT = os.path.join(ROOT, "viz", "explorer", "data")
# keys of the precomputed shooter_spec cache (PM-019): derived tilt bounds fz.TILT_BOUNDS (28.80 / 31.77)
# and the CAD tilt 30; the masks use the 3D cell (fz.SWEEP_CELL). The exported HIVE segments stay the
# s = 0 section the page draws (the 3D cell is built from it); gate3d = the 3D-cell entry gate.
FORMAT_VERSION = 2      # 1 = PM-005..PM-015 (section model, rho 1.20, tilts 28.5 / 30 / 31.5)
GEOM_KEYS = {fz.geom_key(False): dict(favorable=False),
             fz.geom_key(False, fz.TILT_BOUNDS[0]): dict(favorable=False, tilt=fz.TILT_BOUNDS[0]),
             fz.geom_key(False, fz.TILT_BOUNDS[1]): dict(favorable=False, tilt=fz.TILT_BOUNDS[1]),
             fz.geom_key(True): dict(favorable=True)}


def case_params(S, var):
    _, Cd, Cl, k = next(v for v in ss.variants(S) if v[0] == var)
    p = fz.aero_case(ss.tag(S, var), Cd=Cd, Cl=None if S == 0.0 else Cl, k=k, path=ss.LIT)
    return dict(rho=p["rho"], mass=p["mass"], radius=p["radius"], Cd=p["Cd"],
                c1=p["Cl"][0] if p["Cl"] else 0.0, clmax=p["Cl"][1] if p["Cl"] else 0.0,
                k=p["spin_decay_k"], g=fz.G, labels=dict(Cd=Cd, Cl=Cl if S else None, k=k))


def write_bin(path, clean, margin, ang):
    idx = np.flatnonzero(clean).astype("<u4")
    m = np.clip(np.round(margin.ravel()[idx] * 1e4), 0, 65535).astype("<u2")
    a = np.clip(np.round(ang.ravel()[idx] * 100), 0, 65535).astype("<u2")
    with open(path, "wb") as fh:
        fh.write(np.array([idx.size], "<u4").tobytes())
        fh.write(idx.tobytes())
        fh.write(m.tobytes())
        fh.write(a.tobytes())
    with open(path, "rb") as fh, open(path[:-4] + ".b64.txt", "w") as out:
        out.write(base64.b64encode(fh.read()).decode())    # the page fetches this copy (artifacts serve no raw binary)
    return int(idx.size)


def main():
    os.makedirs(OUT, exist_ok=True)
    g = ss.grid()
    geoms = {}
    for key, kw in GEOM_KEYS.items():
        gm = fz.Geometry.make(cell=fz.SWEEP_CELL, **kw)
        h = gm.hive
        geoms[key] = dict(names=list(h.names), P0=np.round(h.P0, 5).tolist(),
                          P1=np.round(h.P1, 5).tolist(), body=list(h.body),
                          inside=np.round(h.inside, 5).tolist(),
                          normal=np.round(h.normal_out, 6).tolist(),
                          gate=np.round(h.gate, 5).tolist(), tilt=h.tilt_deg,
                          gate3d=np.round(gm.gate if gm.gate is not None else h.gate, 5).tolist())
    cases = []
    for S in ss.SPINS:
        for var, *_ in ss.variants(S):
            z = ss.load(S, var)
            files = {}
            for gk in GEOM_KEYS:
                if var != "nominal" and gk != "unfav_t30":
                    continue          # aero variants: unfavourable tilt 30 only (keeps the page light)
                name = f"{ss.tag(S, var)}_{gk}.bin".replace("+", "p").replace("-", "m")
                n = write_bin(os.path.join(OUT, name), z[f"{gk}__clean"], z[f"{gk}__margin"],
                              z[f"{gk}__ang"])
                files[gk] = dict(file=name, n=n)
            cases.append(dict(S=S, var=var, params=case_params(S, var), files=files))
            print(ss.tag(S, var), {k: v["n"] for k, v in files.items()}, flush=True)
    index = dict(
        label="PREDICTED: src/shooter_spec.py clean windows, 3D cell model (src/cell3d.py, straight shot), "
              "literature aero research/params_lit.json (not POLLEN measurements) at rho 1.2041 kg/m^3 "
              "(derived); HIVE from official CAD (tilt 30 CONFIRMED; 28.80 / 31.77 derived tipped bounds)",
        format_version=FORMAT_VERSION,
        cell_model=fz.SWEEP_CELL,
        rho=round(float(fz.SWEEP_RHO), 4),
        tilt_options=[{"key": f"{t:g}", "tilt": t, "label": lab} for t, lab in
                      ((fz.TILT_BOUNDS[0], "derived bound"), (30.0, "CAD, CONFIRMED"),
                       (fz.TILT_BOUNDS[1], "derived bound"))],
        model_stamp=ss.MODEL_STAMP,
        grid=dict(h=g.h.tolist(), d=g.d.tolist(), v=g.v.tolist(), theta=g.theta.tolist(),
                  order="h,d,v,theta"),
        integrator=dict(method="RK4 fixed step", dt=2e-3, frame="shot frame: release at x=-d, z=h, "
                        "fires toward +x; HIVE pivot plane x=0"),
        ball_radius=0.0355, wheel_d=ss.WHEEL_D, v_over_u=list(ss.V_OVER_U),
        geoms=geoms, cases=cases)
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, separators=(",", ":"))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
