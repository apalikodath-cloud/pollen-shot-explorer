"""PM-012: summarise FluidX3D runs written by cfd/fluidx3d/setup.cpp and convert them to the model's convention.

Standard-library Python only; run it isolated, paths as arguments:
  python -I cfd/postprocess.py summary <run.csv> [<run.csv> ...] [--t0 15] [--json]
  python -I cfd/postprocess.py grid <coarse.csv> <fine.csv> [--t0 15]
  python -I cfd/postprocess.py --selftest

CSV coefficients (setup.cpp) use the body diameter D in cells: A = pi (D/2)^2, q = 0.5 u^2 A (lattice units),
  Cd = Fx/q, Cy = Fy/q, Cl = Fz/q (spin about +y, backspin lift along +z), CM = -Ty/(q R).
For body=stl, D is mapped to the CAD outer diameter Dmm (71.12 mm), so R_cfd = Dmm/2.
Model convention (src/feasibility.py, viz/explorer/physics.js): F = 0.5 rho C A |v|^2 with A = pi R^2, R = 0.0355 m,
S = |w| R / |v|, w(t) = w0 exp(-k t). Hence
  Cd_model = Cd_cfd (R_cfd/R_model)^2, Cl_model likewise, S_model = S_cfd R_model/R_cfd,
  k = T/(I w) = CM 0.5 rho v pi R_cfd^4 / (I S_cfd)  [1/s], with v = Re nu / (2 R_cfd).
Air: still dry air 20 C, 101.325 kPa (src/air.py): rho 1.2041 kg/m^3, mu 1.8133e-5 Pa s (Sutherland), nu 1.5060e-5.
I = 1.98e-5 kg m^2 (research/params_lit.json I_b, grade B). Every converted number is PREDICTED (CFD).
"""
import argparse
import csv
import json
import math
import os
import re
import sys
import tempfile

RHO = 1.2041          # kg/m^3, derived (src/air.py STILL_AIR_RHO)
NU = 1.5060e-5        # m^2/s, derived (Sutherland mu / rho)
R_MODEL = 0.0355      # m, model radius (params_lit radius)
I_BALL = 1.98e-5      # kg m^2, params_lit I_b (grade B)
COEFS = ("Cd", "Cy", "Cl", "CM")


def read_run(path):
    meta, rows = {}, []
    with open(path, newline="") as fh:
        lines = fh.read().splitlines()
    data = [l for l in lines if l and not l.startswith("#")]
    for l in lines:
        if l.startswith("#"):
            body = l[1:].replace("PM-012 FluidX3D run;", "")
            for tok in body.split():
                if "=" in tok:
                    k, _, v = tok.partition("=")
                    meta[k.strip(",;")] = v.strip(",;")
    for r in csv.DictReader(data):
        rows.append({k: float(v) for k, v in r.items()})
    return meta, rows


def fnum(meta, key, default=None):
    try:
        return float(meta[key])
    except (KeyError, ValueError):
        return default


def window_stats(rows, key, t0, nb=8):
    x = [r[key] for r in rows if r["tstar"] >= t0]
    n = len(x)
    if n < 2 * nb:
        return {"n": n, "mean": float("nan"), "std": float("nan"), "se": float("nan"), "drift": float("nan")}
    m = sum(x) / n
    sd = math.sqrt(sum((v - m) ** 2 for v in x) / (n - 1))
    b = n // nb
    bm = [sum(x[i * b:(i + 1) * b]) / b for i in range(nb)]
    mb = sum(bm) / nb
    se = math.sqrt(sum((v - mb) ** 2 for v in bm) / (nb - 1) / nb)  # batch-means standard error
    h = n // 2
    drift = sum(x[h:]) / (n - h) - sum(x[:h]) / h  # second half minus first half
    return {"n": n, "mean": m, "std": sd, "se": se, "drift": drift}


def summarise(path, t0):
    meta, rows = read_run(path)
    out = {"file": os.path.basename(path), "body": meta.get("body"), "D": fnum(meta, "D"), "Re": fnum(meta, "Re"),
           "S": fnum(meta, "S", 0.0), "u": fnum(meta, "u"), "N": meta.get("N"), "tau": fnum(meta, "tau"),
           "solid_over_ref": fnum(meta, "solid_over_reference_volume"), "runtime_s": fnum(meta, "runtime_s"),
           "MLUPs": fnum(meta, "MLUPs"), "t_end": rows[-1]["tstar"] if rows else None, "t0": t0}
    if out["u"] is not None:
        out["Mach"] = out["u"] * math.sqrt(3.0)
    if meta.get("body") == "rotstokes":
        body, stokes = fnum(meta, "body_Ty"), fnum(meta, "stokes_Ty(R_nominal)")
        out["rotstokes"] = {"body_over_stokes": body / stokes if body and stokes else None,
                            "cube_over_body": {k: fnum(meta, k) / body for k in meta
                                               if k.startswith("cube_") and body and fnum(meta, k) is not None}}
        return out
    for k in COEFS:
        out[k] = window_stats(rows, k, t0)
    dmm = fnum(meta, "Dmm", 0.0)
    if meta.get("body") == "stl" and dmm and out["Re"]:
        r_cfd = 0.5e-3 * dmm
        v = out["Re"] * NU / (2.0 * r_cfd)
        f = (r_cfd / R_MODEL) ** 2
        conv = {"v_mps": v, "R_cfd_m": r_cfd, "area_factor": f,
                "Cd_model": out["Cd"]["mean"] * f, "Cl_model": out["Cl"]["mean"] * f,
                "S_model": out["S"] * R_MODEL / r_cfd}
        if out["S"] > 0.0:
            conv["k_per_s"] = out["CM"]["mean"] * 0.5 * RHO * v * math.pi * r_cfd ** 4 / (I_BALL * out["S"])
        out["model"] = conv
    return out


def grid(coarse, fine, t0):
    a, b = summarise(coarse, t0), summarise(fine, t0)
    r = b["D"] / a["D"]
    res = {"coarse": a["file"], "fine": b["file"], "r": r}
    for k in COEFS:
        fc, ff = a[k]["mean"], b[k]["mean"]
        d = {"coarse": fc, "fine": ff, "change": ff - fc, "rel_change": (ff - fc) / ff if ff else float("nan")}
        for p in (1, 2):  # Richardson with an assumed order (staircase walls ~1, LBM bulk 2); Fs = 3 for two grids
            d["extrap_p%d" % p] = ff + (ff - fc) / (r ** p - 1.0)
            d["GCI_p%d" % p] = 3.0 * abs(d["rel_change"]) / (r ** p - 1.0)
        res[k] = d
    return res


def fmt(s):
    lines = ["%s  body=%s D=%s Re=%s S=%s Mach=%.3f tau=%s solid/ref=%s runtime_s=%s MLUPs=%s window t*=%s..%s"
             % (s["file"], s["body"], s["D"], s["Re"], s["S"], s.get("Mach", float("nan")), s["tau"], s["solid_over_ref"],
                s["runtime_s"], s["MLUPs"], s["t0"], s["t_end"])]
    if "rotstokes" in s:
        lines.append("  rotstokes: body/Stokes torque %s; cube/body %s" % (s["rotstokes"]["body_over_stokes"], s["rotstokes"]["cube_over_body"]))
        return "\n".join(lines)
    for k in COEFS:
        w = s[k]
        lines.append("  %-2s mean %.4f  std %.4f  se %.4f  half-window drift %+.4f  (n %d)" % (k, w["mean"], w["std"], w["se"], w["drift"], w["n"]))
    if "model" in s:
        m = s["model"]
        lines.append("  model convention (PREDICTED): v %.3f m/s  Cd %.4f  Cl %.4f  S %.4f%s" % (
            m["v_mps"], m["Cd_model"], m["Cl_model"], m["S_model"], ("  k %.4f 1/s" % m["k_per_s"]) if "k_per_s" in m else ""))
    return "\n".join(lines)


def write_csv(path, header, rows):
    with open(path, "w", newline="") as fh:
        fh.write(header)
        fh.write("step,tstar,Fx,Fy,Fz,Tx,Ty,Tz,Cd,Cy,Cl,CM\n")
        for r in rows:
            fh.write(",".join("%.9g" % v for v in r) + "\n")


def selftest():
    fails, done = [], []

    def check(name, got, want, tol):
        done.append(name)
        if not abs(got - want) <= tol:
            fails.append("%s: got %r want %r" % (name, got, want))

    with tempfile.TemporaryDirectory() as td:
        rows = []
        for i in range(0, 4001):  # t* 0..40, transient decays before t* 15, shedding period 5 t*
            t = i * 0.01
            cd = 0.46 + 0.02 * math.sin(2 * math.pi * t / 5.0) + 0.5 * math.exp(-t)
            cl = 0.27 + 0.03 * math.sin(2 * math.pi * t / 5.0)
            rows.append((i, t, 0, 0, 0, 0, 0, 0, cd, 0.0, cl, 0.02))
        sph = os.path.join(td, "sphere.csv")
        write_csv(sph, "# PM-012 FluidX3D run; body=sphere stl= D=48 Re=30000 u=0.05 S=0.5 omega=0.001 nu=8e-05 tau=0.50024 N=384x240x240\n"
                       "# solid_cells=57856 solid_over_reference_volume=0.999 A_ref=pi*(D/2)^2=1809.56 cells;\n", rows)
        s = summarise(sph, 15.0)
        check("sphere Cd mean", s["Cd"]["mean"], 0.46, 1e-3)
        check("sphere Cl mean", s["Cl"]["mean"], 0.27, 1e-3)
        check("sphere Mach", s["Mach"], 0.05 * math.sqrt(3), 1e-12)
        check("sphere solid/ref", s["solid_over_ref"], 0.999, 1e-12)
        if "model" in s:
            fails.append("sphere run must not get a model conversion")
        stl = os.path.join(td, "pollen.csv")
        write_csv(stl, "# PM-012 FluidX3D run; body=stl stl=x.stl D=94 Re=33057.4 u=0.05 S=0.5 omega=0.0005 nu=0.000142 tau=0.5004 N=564x376x376 Dmm=71.12\n", rows)
        p = summarise(stl, 15.0)
        r = 0.03556
        v = 33057.4 * NU / 0.07112
        check("stl v", p["model"]["v_mps"], v, 1e-9)
        check("stl v ~7 m/s", p["model"]["v_mps"], 7.0, 0.01)
        check("stl Cd_model", p["model"]["Cd_model"], 0.46 * (r / 0.0355) ** 2, 2e-3)
        # k = T/(I w): T = CM q A R, q = 0.5 rho v^2, A = pi r^2, w = S v / r
        T = 0.02 * 0.5 * RHO * v * v * math.pi * r * r * r
        check("stl k", p["model"]["k_per_s"], T / (I_BALL * 0.5 * v / r), 1e-9)
        c = os.path.join(td, "coarse.csv")
        f = os.path.join(td, "fine.csv")
        write_csv(c, "# PM-012 FluidX3D run; body=sphere D=48 Re=30000 u=0.05 S=0\n", [(i, i * 0.01, 0, 0, 0, 0, 0, 0, 0.50, 0, 0, 0) for i in range(4001)])
        write_csv(f, "# PM-012 FluidX3D run; body=sphere D=96 Re=30000 u=0.05 S=0\n", [(i, i * 0.01, 0, 0, 0, 0, 0, 0, 0.47, 0, 0, 0) for i in range(4001)])
        g = grid(c, f, 15.0)
        check("grid r", g["r"], 2.0, 1e-12)
        check("grid extrap p2", g["Cd"]["extrap_p2"], 0.46, 1e-9)
        check("grid extrap p1", g["Cd"]["extrap_p1"], 0.44, 1e-9)
        check("grid GCI p1", g["Cd"]["GCI_p1"], 3.0 * 0.03 / 0.47, 1e-9)
        rs = os.path.join(td, "rot.csv")
        write_csv(rs, "# PM-012 FluidX3D run; body=rotstokes stl= D=32 Re=30000 u=0 S=0 omega=0.0003125 nu=0.2 tau=1.1 N=128x128x128\n"
                      "# rotstokes body_Ty=-0.21 stokes_Ty(R_nominal)=-0.2 cube_24.5_Ty=-0.2079\n", rows[:100])
        q = summarise(rs, 0.0)
        check("rotstokes body/stokes", q["rotstokes"]["body_over_stokes"], 1.05, 1e-9)
        check("rotstokes cube/body", q["rotstokes"]["cube_over_body"]["cube_24.5_Ty"], 0.99, 1e-9)
    if fails:
        print("SELFTEST FAILED:\n  " + "\n  ".join(fails))
        return 1
    print("selftest ok (%d checks)" % len(done))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", choices=["summary", "grid"])
    ap.add_argument("files", nargs="*")
    ap.add_argument("--t0", type=float, default=15.0, help="start of the averaging window in t* (default 15)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.cmd == "summary" and a.files:
        for p in a.files:
            s = summarise(p, a.t0)
            print(json.dumps(s) if a.json else fmt(s))
        return 0
    if a.cmd == "grid" and len(a.files) == 2:
        print(json.dumps(grid(a.files[0], a.files[1], a.t0), indent=1))
        return 0
    ap.print_usage()
    return 2


if __name__ == "__main__":
    sys.exit(main())
