"""Knuckle evidence from the PM-012 CFD force records (all output PREDICTED; the solver is not released).

usage: python -B research/knuckleball/cfd_knuckle_stats.py <runs_dir> [out.json]

For every finished body=pollen run (T >= 100 D/u) it reports, from t* >= 30 on:
  - mean and std of Cd, Cy, Cl, CM and of the cross torques CTx, CTz (T / (q A R));
  - the spectral peak Strouhal number of Cy and Cl, and the share of Cy/Cl variance slower than 0.1 U/D;
  - "switch" metrics: the largest change of the 10 D/u running mean of the lateral coefficient over any 10 D/u,
    and the excess kurtosis of 1 D/u increments (Gaussian = 0; jumpy = large);
  - the share of the Cy / Cl fluctuation carried by the outer surface, the inner (cavity) surface and the hole walls
    (from the solver's '# dg' force split), and the cavity mean |u|/U;
  - the lateral miss of a ball flying a path of length L (2, 3, 4 m) at constant speed through a window of the record:
    y = (rho A / 2 m) * U^2 * double integral of C(t) dt^2. With t* = t U / D this is
    y = (rho A D^2 / 2 m) * double integral over t* of C, so it does not depend on U for a fixed path length.
    'dev' is the deviation from the best-fit parabola (constant force) over the window: the part of the path a
    constant side force cannot explain, i.e. the 'break'. Reported: median and 95th percentile over windows.
  - the quasi-steady rotation of a FREE ball (one-way: torque record -> angle), over the same path windows.
Constants: rho 1.204 kg/m^3 (20 C, sea level, ASSUMED room air), m 24.95 g (AndyMark spec), D 71.12 mm (CAD),
I = 0.63 m R^2 (CAD-derived k_I).
"""
import glob
import json
import math
import os
import re
import sys

import numpy as np

RHO, M, D = 1.204, 0.02495, 0.07112
R = D / 2
A = math.pi * R * R
KI = 0.63
K_Y = RHO * A * D * D / (2 * M)              # m per (C * t*^2)
K_TH = RHO * A * D * D / (2 * KI * M * R)    # rad per (CT * t*^2) with CT = T/(qAR); alpha = CT q A R / I
T0 = 30.0
PATHS = (2.0, 3.0, 4.0)

DG_KEYS = ("dg_Cy_out", "dg_Cy_in", "dg_Cy_hole", "dg_Cl_out", "dg_Cl_in", "dg_Cl_hole", "dg_cav_umean", "dg_hole_abs")


def read(f):
    hdr, rows, dg = {}, [], []
    with open(f) as fh:
        for ln in fh:
            if ln.startswith("# PM-012"):
                for k, v in re.findall(r"(\w+)=(\S+)", ln):
                    hdr.setdefault(k, v)
            elif ln.startswith("# dg "):
                d = dict(re.findall(r"(\w+)=(\S+)", ln))
                try:
                    dg.append([float(d["dg_tstar"])] + [float(d.get(k, "nan")) for k in DG_KEYS])
                except (KeyError, ValueError):
                    pass
            elif ln[0] not in "#s":
                p = ln.split(",")
                if len(p) == 12:
                    rows.append([float(x) for x in p])
    return hdr, np.array(rows), np.array(dg)


def running(x, w):
    if w < 2:
        return x.copy()
    return np.convolve(x, np.ones(w) / w, "valid")


def path_stats(t, c, L):
    """lateral miss and break of a ball on a path of length L through windows of the record c(t*)"""
    dt = float(np.median(np.diff(t)))
    tw = L / D                                   # path length in diameters = window length in t*
    n = int(round(tw / dt))
    if n < 20 or n >= len(c):
        return None
    starts = range(0, len(c) - n, max(1, n // 8))
    ys, devs = [], []
    tt = np.arange(n) * dt
    for s in starts:
        cc = c[s:s + n]
        v = np.cumsum(cc) * dt
        y = K_Y * np.cumsum(v) * dt
        fit = np.polyval(np.polyfit(tt, y, 2), tt)
        ys.append(abs(y[-1]))
        devs.append(np.max(np.abs(y - fit)))
    return {"miss_med_mm": 1e3 * float(np.median(ys)), "miss_p95_mm": 1e3 * float(np.percentile(ys, 95)),
            "break_med_mm": 1e3 * float(np.median(devs)), "break_p95_mm": 1e3 * float(np.percentile(devs, 95))}


def run_stats(f):
    hdr, a, dg = read(f)
    if a.size == 0 or a[-1, 1] < 100:
        return None
    a = a[a[:, 1] >= T0]
    t = a[:, 1]
    dt = float(np.median(np.diff(t)))
    q_lat = 0.5 * float(hdr["u"]) ** 2 * math.pi * (float(hdr["D"]) / 2) ** 2
    Rl = float(hdr["D"]) / 2
    ctx, ctz = a[:, 5] / (q_lat * Rl), a[:, 7] / (q_lat * Rl)
    cd, cy, cl, cm = a[:, 8], a[:, 9], a[:, 10], a[:, 11]
    S = float(hdr["S"])
    res = {"S": S, "Re": float(hdr["Re"]), "D": float(hdr["D"]), "orient": (hdr.get("rx"), hdr.get("ry"), hdr.get("rz")),
           "T": round(float(t[-1]), 1), "dt": dt}
    for k, x in (("Cd", cd), ("Cy", cy), ("Cl", cl), ("CM", cm), ("CTx", ctx), ("CTz", ctz)):
        res[k] = {"mean": float(x.mean()), "std": float(x.std())}
    for k, x in (("Cy", cy), ("Cl", cl)):
        y = x - x.mean()
        P = np.abs(np.fft.rfft(y * np.hanning(len(y)))) ** 2
        fr = np.fft.rfftfreq(len(y), dt)
        ok = fr >= 0.05
        res[k]["St_peak"] = float(fr[ok][np.argmax(P[ok])])
        res[k]["slow_frac"] = float(P[(fr > 0) & (fr < 0.1)].sum() / P[1:].sum())
        w = max(1, int(round(10 / dt)))
        m10 = running(x, w)
        res[k]["max_dmean10"] = float(np.max(np.abs(m10[w:] - m10[:-w]))) if len(m10) > w else float("nan")
        res[k]["sd_mean10"] = float(m10.std())
        k1 = max(1, int(round(1 / dt)))
        inc = x[k1:] - x[:-k1]
        res[k]["kurt_inc1"] = float(((inc - inc.mean()) ** 4).mean() / inc.var() ** 2 - 3)
    # lateral = the force normal to the flight direction that is NOT the steady Magnus lift: use Cy (along the spin
    # axis) and Cl - mean(Cl); both fluctuate.  Path stats on the raw Cy and on Cl - mean (the Magnus mean is a smooth
    # curve, kept separate).
    res["path"] = {}
    for L in PATHS:
        res["path"][str(L)] = {"Cy": path_stats(t, cy, L), "Cl_fluct": path_stats(t, cl - cl.mean(), L),
                               "Cy_fluct": path_stats(t, cy - cy.mean(), L)}
    # free-ball quasi-steady rotation (one-way) from the cross torques; CM (about the spin axis) is added only for
    # S = 0, because with spin it is the spin-damping torque (reported separately as the spin decay over the path).
    rot = {}
    axes = (cm, ctx, ctz) if S == 0 else (ctx, ctz)
    for L in PATHS:
        n = int(round((L / D) / dt))
        if n < len(cm):
            th = []
            for s in range(0, len(cm) - n, max(1, n // 8)):
                tot = 0.0
                for c in axes:
                    om = np.cumsum(c[s:s + n]) * dt
                    tot += (K_TH * np.sum(om) * dt) ** 2
                th.append(math.degrees(math.sqrt(tot)))
            rot[str(L)] = {"deg_med": float(np.median(th)), "deg_p95": float(np.percentile(th, 95))}
    res["free_rot"] = rot
    # spin decay over a path L: d(omega)/omega = CM rho A L / (2 S k_I m)   (omega = 2 S U / D, I = k_I m R^2)
    if S > 0:
        res["spin_decay_frac_per_m"] = float(cm.mean() * RHO * A / (2 * S * KI * M))
    if dg.size:
        g = dg[dg[:, 0] >= T0]
        if len(g) > 50 and np.isfinite(g[:, 1:7]).all():
            out = {}
            for lab, cols in (("Cy", (1, 2, 3)), ("Cl", (4, 5, 6))):
                parts = [g[:, c] - g[:, c].mean() for c in cols]
                tot = sum(parts)
                var = tot.var()
                # share of the fluctuation variance: covariance of each part with the total
                out[lab] = {nm: float((p * tot).mean() / var) if var > 0 else float("nan")
                            for nm, p in zip(("outer", "inner", "holewall"), parts)}
                out[lab + "_mean"] = {nm: float(g[:, c].mean()) for nm, c in zip(("outer", "inner", "holewall"), cols)}
            out["cav_umean"] = float(np.nanmean(g[:, 7]))
            out["hole_abs"] = float(np.nanmean(g[:, 8]))
            res["split"] = out
    return res


def main():
    runs = sys.argv[1]
    outp = sys.argv[2] if len(sys.argv) > 2 else None
    res = {}
    for f in sorted(glob.glob(os.path.join(runs, "*.csv"))):
        name = os.path.basename(f)[:-4]
        if not (name.startswith("p_") or name.startswith("v1_ibb") or name.startswith("v2_ibb")):
            continue
        try:
            r = run_stats(f)
        except Exception as e:  # noqa: BLE001 - report and continue
            print("skip", name, e, file=sys.stderr)
            continue
        if r:
            res[name] = r
    print("K_Y = %.4g m per (C t*^2); K_TH = %.4g rad per (CT t*^2)" % (K_Y, K_TH))
    hdr = "%-34s %5s %6s %7s %7s %7s %7s %6s %6s %6s %6s %7s %6s %6s %6s %6s %6s" % (
        "run", "S", "Re", "Cd", "Cy", "sdCy", "Cl", "sdCl", "St_y", "slowY", "kurtY", "dm10Y", "brk3", "brk95", "rot3", "miss95", "mmean")
    print(hdr)
    for n, r in res.items():
        p3 = r["path"]["3.0"]["Cy_fluct"] or {}
        print("%-34s %5.2f %6.0f %7.4f %7.4f %7.4f %7.4f %6.4f %6.3f %6.2f %6.2f %7.4f %6.1f %6.1f %6.1f %6.1f %6.1f" % (
            n[:34], r["S"], r["Re"], r["Cd"]["mean"], r["Cy"]["mean"], r["Cy"]["std"], r["Cl"]["mean"], r["Cl"]["std"],
            r["Cy"]["St_peak"], r["Cy"]["slow_frac"], r["Cy"]["kurt_inc1"], r["Cy"]["max_dmean10"],
            p3.get("break_med_mm", float("nan")), p3.get("break_p95_mm", float("nan")),
            r["free_rot"].get("3.0", {}).get("deg_med", float("nan")), p3.get("miss_p95_mm", float("nan")),
            1e3 * 0.5 * K_Y * abs(r["Cy"]["mean"]) * (3.0 / D) ** 2))
    if outp:
        with open(outp, "w") as fh:
            json.dump(res, fh, indent=1)


if __name__ == "__main__":
    main()
