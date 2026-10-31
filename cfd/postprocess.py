"""PM-012: statistics, gate checks and model conversion for runs of the own LBM-LES solver (cfd/lbm/pm012_lbm.cpp).

Standard-library Python only; run it isolated, paths as arguments:
  python -I cfd/postprocess.py summary <run.csv> [<run.csv> ...] [--t0 15] [--json]
  python -I cfd/postprocess.py grid <coarse.csv> <fine.csv> [--t0 15]
  python -I cfd/postprocess.py v1 <run.csv> [--box F] [--t0 15]        V1 verdict (binding acceptance, cfd/README.md)
  python -I cfd/postprocess.py v2 <spin.csv> <twin_S0.csv> [--t0 15]   V2 verdict (twin lateral force carried as a +- term)
  python -I cfd/postprocess.py match <a.csv> <b.csv> [--t0 15]         Cd/Cl/CM agreement (STL sphere vs analytic, revox pair)
  python -I cfd/postprocess.py --selftest

CSV coefficients (pm012_lbm.cpp) use the body diameter D in cells: A = pi (D/2)^2, q = 0.5 u^2 A (lattice units),
  Cd = Fx/q, Cy = Fy/q, Cl = Fz/q (spin about +y, backspin lift along +z), CM = -Ty/(q R).
For body=stl, D is mapped to the CAD outer diameter Dmm (71.12 mm), so R_cfd = Dmm/2.

Statistics over the window t0 <= t* <= end (cfd/README.md, "Averaging and uncertainty"):
  rows are averaged into 0.1 t* bins; T_int = the largest of (autocorrelation summed to its first zero crossing) and
  (batch-means estimates with 5, 10 and 20 t* batches, each needing >= 4 batches); batches are max(2 T_int, 5 t*)
  long; u_win = standard deviation of the batch means (window-to-window spread, the reported uncertainty; not divided
  by sqrt(nb)); ci95 = t95 x se of the window mean, for information only; trend = least-squares slope over the whole
  window x window length, trend_se from a regression of the batch means.
  A coefficient is stationary when there are >= 4 batches and the trend is not both significant at 95 %
  (|trend| > t95(nb-2) trend_se) and larger than TREND_TOL.
  Lateral force: L = |(<Cl>, <Cy>)| over the window, and per 5 t* block.
Model convention (src/feasibility.py, viz/explorer/physics.js): F = 0.5 rho C A |v|^2 with A = pi R^2, R = 0.0355 m,
S = |w| R / |v|, w(t) = w0 exp(-k t). Hence
  Cd_model = Cd_cfd (R_cfd/R_model)^2, Cl_model likewise, S_model = S_cfd R_model/R_cfd,
  k = T/(I w) = CM 0.5 rho v pi R_cfd^4 / (I S_cfd)  [1/s], with v = Re nu / (2 R_cfd).
Air: still dry air 20 C, 101.325 kPa (src/air.py): rho 1.2041 kg/m^3, mu 1.8133e-5 Pa s (Sutherland), nu 1.5060e-5.
I = 1.98e-5 kg m^2 (research/params_lit.json I_b, grade B). Every CFD number is PREDICTED
(labels: docs/08_shooter_spec.md lines 5-6).
"""
import argparse
import csv
import json
import math
import os
import random
import sys
import tempfile

RHO = 1.2041          # kg/m^3, derived (src/air.py STILL_AIR_RHO)
NU = 1.5060e-5        # m^2/s, derived (Sutherland mu / rho)
R_MODEL = 0.0355      # m, model radius (params_lit radius)
I_BALL = 1.98e-5      # kg m^2, params_lit I_b (grade B)
COEFS = ("Cd", "Cy", "Cl", "CM")
NAN = float("nan")

# Averaging rules (ASSUMED modelling choices, set 2026-10-31 after review; README "Averaging and uncertainty")
BIN_T = 0.1           # t*, rows are averaged into bins this long
MIN_BATCH_T = 5.0     # t*, a batch is never shorter than about one shedding period (St about 0.2)
MIN_BATCHES = 4       # fewer batches give no usable trend or spread
BLOCK_T = 5.0         # t*, block length of the lateral-force table
TREND_TOL = {"Cd": 0.02, "Cy": 0.02, "Cl": 0.02, "CM": 0.002}    # largest allowed significant |fitted change across the window|
BM_LENGTHS = (5.0, 10.0, 20.0)  # t*, batch lengths of the batch-means T_int estimates
MATCH_FLOOR = {"Cd": 0.01, "Cy": 0.01, "Cl": 0.01, "CM": 0.001}  # smallest agreement tolerance in `match`

# Binding acceptance (cfd/README.md "Acceptance"). The bands were pre-registered at 09:32 on 2026-10-31 (commit 208142e),
# before any run; the u_win, stationarity and twin-lateral conditions were added after the review.
V1_BAND = (0.43, 0.50)   # box-corrected Cd, smooth sphere, Re 33057, S 0
V1_HALF = 0.035          # u_win(Cd) must not exceed half the band width
V2_BAND = (0.22, 0.33)   # Cl, smooth sphere, Re 33057, S 0.5
V2_HALF = 0.055          # u_win(Cl) + twin lateral magnitude must not exceed half the band width
T_MIN = 150.0            # t*, every V1 and V2 run is at least this long (window t* 15 to the end)


T95 = ((30, 2.04), (20, 2.09), (15, 2.13), (12, 2.18), (10, 2.23), (8, 2.31), (6, 2.45), (5, 2.57), (4, 2.78),
       (3, 3.18), (2, 4.30), (1, 12.71))


def t95(dof):
    """Two-sided 95 % Student t quantile, rounded towards the next smaller tabulated dof (conservative)."""
    if dof > 30:
        return 1.96
    for d, t in T95:
        if dof >= d:
            return t
    return NAN


def cd_ref(re):
    """Brown & Lawler (2003) Eq. 19, smooth sphere drag (literature reference, ASSUMED as the V1 reference)."""
    return 24.0 / re * (1.0 + 0.150 * re ** 0.681) + 0.407 / (1.0 + 8710.0 / re)


def read_run(path):
    meta, rows = {}, []
    with open(path, newline="") as fh:
        lines = fh.read().splitlines()
    data = [l for l in lines if l and not l.startswith("#")]
    for l in lines:
        if l.startswith("#"):
            for tok in l[1:].split():
                if "=" in tok:
                    k, _, v = tok.partition("=")
                    meta[k.strip(",;")] = v.strip(",;")
    for r in csv.DictReader(data):
        try:
            rows.append({k: float(v) for k, v in r.items()})
        except (TypeError, ValueError):  # a run still writing its last line
            continue
    return meta, rows


def fnum(meta, key, default=None):
    try:
        return float(meta[key])
    except (KeyError, ValueError):
        return default


def mean(v):
    return sum(v) / len(v)


def binned(rows, key, t0, t1=None, dt=BIN_T):
    """Means of `key` (and of t*) over consecutive bins of dt for t0 <= t* <= t1."""
    ts, xs, cur, st, sx, c = [], [], None, 0.0, 0.0, 0
    for r in rows:
        t = r["tstar"]
        if t < t0 or (t1 is not None and t > t1):
            continue
        b = int((t - t0) // dt)
        if cur is not None and b != cur and c:
            ts.append(st / c)
            xs.append(sx / c)
            st, sx, c = 0.0, 0.0, 0
        cur = b
        st += t
        sx += r[key]
        c += 1
    if c:
        ts.append(st / c)
        xs.append(sx / c)
    return ts, xs


def integral_time(x, dt):
    """Autocorrelation of a binned series summed (trapezoid) up to its first zero crossing, in t*."""
    n = len(x)
    m = mean(x)
    v = [a - m for a in x]
    c0 = sum(a * a for a in v) / n
    if c0 <= (1e-12 * max(1.0, abs(m))) ** 2:  # constant series (float rounding only)
        return 0.0
    t = 0.5 * dt
    for k in range(1, n // 2):
        ck = sum(v[i] * v[i + k] for i in range(n - k)) / n
        if ck <= 0.0:
            break
        t += dt * ck / c0
    return t


def integral_time_batches(x, dt, length=MIN_BATCH_T):
    """T_int from the variance of batch means: var(mean over L) = var(x) 2 T_int / L (needs >= 4 batches)."""
    m = max(1, int(round(length / dt)))
    nb = len(x) // m
    if nb < MIN_BATCHES:
        return NAN
    bm = [mean(x[i * m:(i + 1) * m]) for i in range(nb)]
    mb, mx = mean(bm), mean(x)
    vb = sum((a - mb) ** 2 for a in bm) / (nb - 1)
    vx = sum((a - mx) ** 2 for a in x) / (len(x) - 1)
    return 0.5 * m * dt * vb / vx if vx > (1e-12 * max(1.0, abs(mx))) ** 2 else 0.0


def window_stats(rows, key, t0, t1=None):
    ts, x = binned(rows, key, t0, t1)
    n = len(x)
    out = {"n_bins": n, "mean": NAN, "std": NAN, "tint": NAN, "tint_acf": NAN, "tint_bm": NAN, "batch_t": NAN, "nb": 0,
           "batch_means": [], "u_win": NAN, "range_win": NAN, "se": NAN, "ci95": NAN, "trend": NAN, "trend_se": NAN,
           "trend_tol": TREND_TOL.get(key, NAN), "trend_significant": None, "trend_pass": False, "drift": NAN}
    if n < 20:
        return out
    dt = (ts[-1] - ts[0]) / (n - 1)
    w = ts[-1] - ts[0] + dt
    m = mean(x)
    ta = integral_time(x, dt)
    tbs = [t for t in (integral_time_batches(x, dt, L) for L in BM_LENGTHS) if t == t]
    tb = max(tbs) if tbs else NAN
    tint = max([ta] + tbs)
    lb = max(2.0 * tint, MIN_BATCH_T)
    nb = int(w // lb)
    h = n // 2
    out.update({"mean": m, "std": math.sqrt(sum((a - m) ** 2 for a in x) / (n - 1)), "tint": tint, "tint_acf": ta,
                "tint_bm": tb, "batch_t": lb, "nb": nb, "drift": mean(x[h:]) - mean(x[:h])})
    tm = mean(ts)
    sxx = sum((t - tm) ** 2 for t in ts)
    out["trend"] = sum((t - tm) * (a - m) for t, a in zip(ts, x)) / sxx * w  # fitted change across the window
    if nb >= 2:
        per = n // nb
        skip = n - per * nb  # leftover bins are dropped at the start (nearest the transient)
        bt = [mean(ts[skip + i * per:skip + (i + 1) * per]) for i in range(nb)]
        bm = [mean(x[skip + i * per:skip + (i + 1) * per]) for i in range(nb)]
        mb = mean(bm)
        sdw = math.sqrt(sum((v - mb) ** 2 for v in bm) / (nb - 1))
        out.update({"batch_means": bm, "u_win": sdw, "range_win": max(bm) - min(bm), "se": sdw / math.sqrt(nb),
                    "ci95": t95(nb - 1) * sdw / math.sqrt(nb)})
        if nb >= 3:
            btm = mean(bt)
            sbb = sum((t - btm) ** 2 for t in bt)
            sl = sum((t - btm) * (v - mb) for t, v in zip(bt, bm)) / sbb
            res = [v - mb - sl * (t - btm) for t, v in zip(bt, bm)]
            out["trend_se"] = math.sqrt(sum(r * r for r in res) / (nb - 2) / sbb) * w
    ts_ = out["trend_se"]
    sig = ts_ == ts_ and abs(out["trend"]) > t95(nb - 2) * ts_
    out["trend_significant"] = sig
    out["trend_pass"] = nb >= MIN_BATCHES and not (sig and abs(out["trend"]) > out["trend_tol"])
    return out


def lateral(rows, t0, t1=None, block=BLOCK_T):
    """Mean lateral force |(<Cl>, <Cy>)| over the window and over each complete block of `block` t*."""
    sel = [r for r in rows if r["tstar"] >= t0 and (t1 is None or r["tstar"] <= t1)]
    if not sel:
        return {"t0": t0, "t1": NAN, "Cl": NAN, "Cy": NAN, "L": NAN, "L_blocks": [], "L_block_min": NAN, "L_block_max": NAN}
    cl, cy = mean([r["Cl"] for r in sel]), mean([r["Cy"] for r in sel])
    tend = sel[-1]["tstar"]
    groups = {}
    for r in sel:
        groups.setdefault(int((r["tstar"] - t0) // block), []).append(r)
    lb = [math.hypot(mean([r["Cl"] for r in g]), mean([r["Cy"] for r in g]))
          for k, g in sorted(groups.items()) if t0 + (k + 1) * block <= tend + 0.5 * block]
    return {"t0": t0, "t1": tend, "Cl": cl, "Cy": cy, "L": math.hypot(cl, cy), "L_blocks": lb,
            "L_block_min": min(lb) if lb else NAN, "L_block_max": max(lb) if lb else NAN}


def summarise(path, t0, t1=None):
    meta, rows = read_run(path)
    out = {"file": os.path.basename(path), "body": meta.get("body"), "D": fnum(meta, "D"), "Re": fnum(meta, "Re"),
           "S": fnum(meta, "S", 0.0), "u": fnum(meta, "u"), "N": meta.get("N"), "tau": fnum(meta, "tau"),
           "coll": meta.get("coll"), "prec": meta.get("prec"), "revox": fnum(meta, "revox"),
           "solid_over_ref": fnum(meta, "solid_over_reference_volume"), "runtime_s": fnum(meta, "runtime_s"),
           "MLUPs": fnum(meta, "MLUPs"), "finished": "runtime_s" in meta,
           "t_end": rows[-1]["tstar"] if rows else None, "t0": t0}
    if out["u"] is not None:
        out["Mach"] = out["u"] * math.sqrt(3.0)
    if meta.get("body") == "rotstokes":
        body, stokes = fnum(meta, "body_Ty"), fnum(meta, "stokes_Ty(R_nominal)")
        out["rotstokes"] = {"body_over_stokes": body / stokes if body and stokes else None,
                            "cube_over_body": {k: fnum(meta, k) / body for k in meta
                                               if k.startswith("cube_") and body and fnum(meta, k) is not None}}
        return out
    for k in COEFS:
        out[k] = window_stats(rows, k, t0, t1)
    out["lateral"] = lateral(rows, t0, t1)
    dmm = fnum(meta, "Dmm", 0.0)
    if meta.get("body") == "stl" and dmm and out["Re"]:
        r_cfd = 0.5e-3 * dmm
        v = out["Re"] * NU / (2.0 * r_cfd)
        f = (r_cfd / R_MODEL) ** 2
        conv = {"v_mps": v, "R_cfd_m": r_cfd, "area_factor": f,
                "Cd_model": out["Cd"]["mean"] * f, "Cd_model_u_win": out["Cd"]["u_win"] * f,
                "Cl_model": out["Cl"]["mean"] * f, "Cl_model_u_win": out["Cl"]["u_win"] * f,
                "S_model": out["S"] * R_MODEL / r_cfd}
        if out["S"] > 0.0:
            kf = 0.5 * RHO * v * math.pi * r_cfd ** 4 / (I_BALL * out["S"])
            conv["k_per_s"] = out["CM"]["mean"] * kf
            conv["k_u_win"] = out["CM"]["u_win"] * kf
        out["model"] = conv
    return out


def grid(coarse, fine, t0):
    a, b = summarise(coarse, t0), summarise(fine, t0)
    r = b["D"] / a["D"]
    res = {"coarse": a["file"], "fine": b["file"], "r": r}
    for k in COEFS:
        fc, ff = a[k]["mean"], b[k]["mean"]
        d = {"coarse": fc, "fine": ff, "change": ff - fc, "rel_change": (ff - fc) / ff if ff else NAN,
             "u_win_coarse": a[k]["u_win"], "u_win_fine": b[k]["u_win"]}
        for p in (1, 2):  # Richardson with an assumed order (staircase walls ~1, LBM bulk 2); Fs = 3 for two grids
            d["extrap_p%d" % p] = ff + (ff - fc) / (r ** p - 1.0)
            d["GCI_p%d" % p] = 3.0 * abs(d["rel_change"]) / (r ** p - 1.0)
        res[k] = d
    return res


def gate_length(s):
    """A gate run has finished and reached T 150 (half a t* of slack for the last CSV row)."""
    return bool(s.get("finished")) and (s.get("t_end") or 0.0) >= T_MIN - 0.5


def v1_verdict(s, box=1.0):
    """V1: box-corrected Cd in 0.43-0.50 (pre-registered), stationary, u_win <= 0.035, finished run of T >= 150."""
    c = s["Cd"]
    cd, u = c["mean"] * box, c["u_win"] * box
    ref = cd_ref(s["Re"]) if s.get("Re") else NAN
    checks = {"Cd_in_0.43_0.50": V1_BAND[0] <= cd <= V1_BAND[1], "stationary": bool(c["trend_pass"]),
              "u_win_le_0.035": u <= V1_HALF, "T_ge_150": gate_length(s)}
    return {"file": s["file"], "Cd": c["mean"], "box_factor": box, "Cd_box_corrected": cd, "u_win": u, "nb": c["nb"],
            "batch_t": c["batch_t"], "trend": c["trend"], "Cd_ref": ref, "error_rel": cd / ref - 1.0 if ref == ref else NAN,
            "lateral_L": s["lateral"]["L"], "checks": checks, "pass": all(checks.values())}


def v2_verdict(spin, twin_rows, t0):
    """V2: Cl in 0.22-0.33 (pre-registered), stationary, u_win(Cl) + |lateral of the S 0 twin, same window| <= 0.055,
    finished run of T >= 150."""
    c = spin["Cl"]
    lat = lateral(twin_rows, t0, spin["t_end"])
    u_tot = c["u_win"] + lat["L"]
    checks = {"Cl_in_0.22_0.33": V2_BAND[0] <= c["mean"] <= V2_BAND[1], "stationary": bool(c["trend_pass"]),
              "twin_covers_window": lat["t1"] >= spin["t_end"] - 1.0, "u_total_le_0.055": u_tot <= V2_HALF,
              "T_ge_150": gate_length(spin)}
    return {"file": spin["file"], "Cl": c["mean"], "u_win": c["u_win"], "twin_lateral_L": lat["L"],
            "twin_window": [lat["t0"], lat["t1"]], "u_total": u_tot, "nb": c["nb"], "trend": c["trend"],
            "Cd": spin["Cd"]["mean"], "CM": spin["CM"]["mean"], "checks": checks, "pass": all(checks.values())}


def match(a, b):
    """Agreement of two runs in Cd, Cl and CM: both stationary and |difference| <= max(t95 sqrt(se_a^2 + se_b^2), floor)."""
    out = {"a": a["file"], "b": b["file"]}
    for k in ("Cd", "Cl", "CM"):
        x, y = a[k], b[k]
        us = t95(min(x["nb"], y["nb"]) - 1) * math.sqrt(x["se"] ** 2 + y["se"] ** 2)
        tol = NAN if us != us else max(us, MATCH_FLOOR[k])
        d = x["mean"] - y["mean"]
        out[k] = {"a": x["mean"], "b": y["mean"], "diff": d, "tol": tol,
                  "ok": abs(d) <= tol and bool(x["trend_pass"]) and bool(y["trend_pass"])}
    out["pass"] = all(out[k]["ok"] for k in ("Cd", "Cl", "CM"))
    return out


def fmt(s):
    lines = ["%s  body=%s D=%s Re=%s S=%s coll=%s prec=%s Mach=%.3f tau=%s solid/ref=%s runtime_s=%s MLUPs=%s window t*=%s..%s%s"
             % (s["file"], s["body"], s["D"], s["Re"], s["S"], s.get("coll"), s.get("prec"), s.get("Mach", NAN), s["tau"],
                s["solid_over_ref"], s["runtime_s"], s["MLUPs"], s["t0"], s["t_end"], "" if s.get("finished") else " (running)")]
    if "rotstokes" in s:
        lines.append("  rotstokes: body/Stokes torque %s; cube/body %s" % (s["rotstokes"]["body_over_stokes"], s["rotstokes"]["cube_over_body"]))
        return "\n".join(lines)
    for k in COEFS:
        w = s[k]
        lines.append("  %-2s mean %+.4f  u_win %.4f (nb %d x %.1f t*, T_int %.1f t*; ci95 %.4f)  trend %+.4f (tol %.3f, %s)"
                     % (k, w["mean"], w["u_win"], w["nb"], w["batch_t"], w["tint"], w["ci95"], w["trend"], w["trend_tol"],
                        "stationary" if w["trend_pass"] else "NOT stationary"))
    la = s["lateral"]
    lines.append("  lateral: mean (Cl, Cy) (%+.4f, %+.4f), |L| %.4f; %g t* blocks |L| %.3f-%.3f"
                 % (la["Cl"], la["Cy"], la["L"], BLOCK_T, la["L_block_min"], la["L_block_max"]))
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


def ar1(seed, n, dt, tau, sd):
    """AR(1) noise with integral time tau (t*) and standard deviation sd, deterministic for a seed."""
    g, a = random.Random(seed), math.exp(-dt / tau)
    b, x, out = math.sqrt(1.0 - a * a) * sd, 0.0, []
    for _ in range(n):
        x = a * x + b * g.gauss(0.0, 1.0)
        out.append(x)
    return out


def selftest():
    fails, done = [], []

    def check(name, got, want, tol):
        done.append(name)
        if not abs(got - want) <= tol:
            fails.append("%s: got %r want %r" % (name, got, want))

    def truth(name, cond):
        done.append(name)
        if not cond:
            fails.append(name)

    def series(path, header, t_end, cd, cl, cy=None, cm=None, dt=0.02):
        n = int(round(t_end / dt)) + 1
        cy = cy or [0.0] * n
        cm = cm or [0.01] * n
        write_csv(path, header, [(i, i * dt, 0, 0, 0, 0, 0, 0, cd[i], cy[i], cl[i], cm[i]) for i in range(n)])

    hdr = "# PM-012 pm012_lbm run; body=sphere stl= D=94 Re=33057 u=0.05 S=%s N=564x376x376 coll=bgk\n# runtime_s=1 MLUPs=1\n"
    with tempfile.TemporaryDirectory() as td:
        rows = []
        for i in range(0, 4001):  # t* 0..40, transient decays before t* 15, shedding period 5 t*
            t = i * 0.01
            cd = 0.46 + 0.02 * math.sin(2 * math.pi * t / 5.0) + 0.5 * math.exp(-t)
            cl = 0.27 + 0.03 * math.sin(2 * math.pi * t / 5.0)
            rows.append((i, t, 0, 0, 0, 0, 0, 0, cd, 0.0, cl, 0.02))
        sph = os.path.join(td, "sphere.csv")
        write_csv(sph, "# PM-012 pm012_lbm run; body=sphere stl= D=48 Re=30000 u=0.05 S=0.5 omega=0.001 nu=8e-05 tau=0.50024 N=384x240x240\n"
                       "# solid_cells=57856 solid_over_reference_volume=0.999 A_ref=pi*(D/2)^2=1809.56 cells;\n", rows)
        s = summarise(sph, 15.0)
        check("sphere Cd mean", s["Cd"]["mean"], 0.46, 1e-3)
        check("sphere Cl mean", s["Cl"]["mean"], 0.27, 1e-3)
        check("sphere Mach", s["Mach"], 0.05 * math.sqrt(3), 1e-12)
        check("sphere solid/ref", s["solid_over_ref"], 0.999, 1e-12)
        truth("periodic signal: batches of at least 5 t*", s["Cd"]["batch_t"] >= 5.0 and s["Cd"]["nb"] == 5)
        truth("periodic signal stationary", s["Cd"]["trend_pass"] and s["Cl"]["trend_pass"])
        if "model" in s:
            fails.append("sphere run must not get a model conversion")
        stl = os.path.join(td, "pollen.csv")
        write_csv(stl, "# PM-012 pm012_lbm run; body=stl stl=x.stl D=94 Re=33057.4 u=0.05 S=0.5 omega=0.0005 nu=0.000142 tau=0.5004 N=564x376x376 Dmm=71.12\n", rows)
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
        write_csv(c, "# PM-012 pm012_lbm run; body=sphere D=48 Re=30000 u=0.05 S=0\n", [(i, i * 0.01, 0, 0, 0, 0, 0, 0, 0.50, 0, 0, 0) for i in range(4001)])
        write_csv(f, "# PM-012 pm012_lbm run; body=sphere D=96 Re=30000 u=0.05 S=0\n", [(i, i * 0.01, 0, 0, 0, 0, 0, 0, 0.47, 0, 0, 0) for i in range(4001)])
        g = grid(c, f, 15.0)
        check("grid r", g["r"], 2.0, 1e-12)
        check("grid extrap p2", g["Cd"]["extrap_p2"], 0.46, 1e-9)
        check("grid extrap p1", g["Cd"]["extrap_p1"], 0.44, 1e-9)
        check("grid GCI p1", g["Cd"]["GCI_p1"], 3.0 * 0.03 / 0.47, 1e-9)
        rs = os.path.join(td, "rot.csv")
        write_csv(rs, "# PM-012 pm012_lbm run; body=rotstokes stl= D=32 Re=30000 u=0 S=0 omega=0.0003125 nu=0.2 tau=1.1 N=128x128x128\n"
                      "# rotstokes body_Ty=-0.21 stokes_Ty(R_nominal)=-0.2 cube_24.5_Ty=-0.2079\n", rows[:100])
        q = summarise(rs, 0.0)
        check("rotstokes body/stokes", q["rotstokes"]["body_over_stokes"], 1.05, 1e-9)
        check("rotstokes cube/body", q["rotstokes"]["cube_over_body"]["cube_24.5_Ty"], 0.99, 1e-9)

        # averaging rules: a long stationary run (T 150, AR(1) noise with T_int 3 t*) passes
        n150 = 7501
        e = ar1(1, n150, 0.02, 3.0, 0.03)
        st = os.path.join(td, "stationary.csv")
        series(st, hdr % 0, 150.0, [0.46 + a for a in e], [0.0 + a for a in ar1(2, n150, 0.02, 3.0, 0.03)])
        a = summarise(st, 15.0)
        truth("AR(1) T_int 3 t* estimated within 1.5-6", 1.5 <= a["Cd"]["tint"] <= 6.0)
        truth("T 150 stationary run: >= 4 batches of >= 2 T_int", a["Cd"]["nb"] >= MIN_BATCHES and a["Cd"]["batch_t"] >= 2.0 * a["Cd"]["tint"])
        truth("T 150 stationary run passes the trend test", a["Cd"]["trend_pass"])
        check("T 150 stationary mean", a["Cd"]["mean"], 0.46, 0.01)
        truth("u_win (window-to-window s.d.) exceeds the se of the window mean", a["Cd"]["u_win"] > a["Cd"]["se"] > 0.0)
        check("t95 at 4 dof", t95(4), 2.78, 1e-9)
        # a drifting run (+0.043 across t* 15-55, the size seen in v1_bgk_d64) with small noise fails
        n55 = 2751
        e = ar1(3, n55, 0.02, 3.0, 0.005)
        dr = os.path.join(td, "drift.csv")
        series(dr, hdr % 0, 55.0, [0.50 + 0.043 * max(0.0, i * 0.02 - 15.0) / 40.0 + e[i] for i in range(n55)], [0.0] * n55)
        d = summarise(dr, 15.0)
        check("trend of a +0.043 ramp", d["Cd"]["trend"], 0.043, 0.02)
        truth("a +0.043 ramp is not stationary", not d["Cd"]["trend_pass"])
        # a 15 t* window holds fewer than 4 batches of 5 t*: never stationary, whatever the trend
        sh = os.path.join(td, "short.csv")
        n30 = 1501
        series(sh, hdr % 0, 30.0, [0.46 + a for a in ar1(4, n30, 0.02, 1.0, 0.005)], [0.0] * n30)
        w = summarise(sh, 15.0)
        truth("15 t* window: fewer than 4 batches, not stationary", w["Cd"]["nb"] < MIN_BATCHES and not w["Cd"]["trend_pass"])
        # slower fluctuations (T_int 10 t*) in a T 150 run: finite-window estimators run low (README), but the
        # estimate must still exceed 4 t* and the batches must be >= 2 x the estimate
        sl = os.path.join(td, "slow.csv")
        series(sl, hdr % 0, 150.0, [0.46 + a for a in ar1(8, n150, 0.02, 10.0, 0.01)], [0.0] * n150)
        w = summarise(sl, 15.0)
        truth("AR(1) T_int 10 t*: estimate >= 4 t*", w["Cd"]["tint"] >= 4.0)
        truth("slow run: batches >= 2 x T_int estimate and >= 4 batches",
              w["Cd"]["batch_t"] >= 2.0 * w["Cd"]["tint"] and w["Cd"]["nb"] >= MIN_BATCHES)
        # lateral force of a no-spin twin: mean (Cl, Cy) = (-0.12, 0.05) gives |L| 0.13
        tw = os.path.join(td, "twin.csv")
        series(tw, hdr % 0, 150.0, [0.46] * n150, [-0.12 + a for a in ar1(5, n150, 0.02, 2.0, 0.01)], cy=[0.05] * n150)
        tl = summarise(tw, 15.0)["lateral"]
        check("twin lateral |L|", tl["L"], 0.13, 0.005)
        truth("twin lateral 5 t* blocks", len(tl["L_blocks"]) == 27 and tl["L_block_min"] > 0.11)
        # V2: Cl 0.27 passes with a quiet twin and fails when the twin carries |L| 0.13
        sp = os.path.join(td, "spin.csv")
        series(sp, hdr % 0.5, 150.0, [0.49] * n150, [0.27 + a for a in ar1(6, n150, 0.02, 2.0, 0.01)])
        quiet = os.path.join(td, "quiet.csv")
        series(quiet, hdr % 0, 150.0, [0.46] * n150, [a for a in ar1(7, n150, 0.02, 2.0, 0.01)])
        ss = summarise(sp, 15.0)
        truth("V2 passes with a quiet twin", v2_verdict(ss, read_run(quiet)[1], 15.0)["pass"])
        vb = v2_verdict(ss, read_run(tw)[1], 15.0)
        truth("V2 fails when the twin |L| 0.13 is carried as +-", not vb["pass"] and not vb["checks"]["u_total_le_0.055"])
        short = os.path.join(td, "short_twin.csv")
        series(short, hdr % 0, 55.0, [0.46] * n55, [0.0] * n55)
        truth("V2 fails when the twin does not cover the window", not v2_verdict(ss, read_run(short)[1], 15.0)["checks"]["twin_covers_window"])
        # V1: binding band 0.43-0.50 on the box-corrected Cd
        v1 = v1_verdict(a)
        truth("V1 passes at Cd 0.46", v1["pass"])
        truth("V1 fails at Cd 0.46 x box 1.1 = 0.506", not v1_verdict(a, 1.1)["pass"])
        check("Brown & Lawler Cd at Re 33057", cd_ref(33057.0), 0.4531, 1e-4)
        # run length: a T 55 run inside the band is not a gate run
        s55 = os.path.join(td, "t55.csv")
        series(s55, hdr % 0, 55.0, [0.46 + a for a in ar1(9, n55, 0.02, 1.0, 0.003)], [0.0] * n55)
        v55 = v1_verdict(summarise(s55, 15.0))
        truth("V1 fails a T 55 run inside the band (run length)", not v55["pass"] and not v55["checks"]["T_ge_150"]
              and v55["checks"]["Cd_in_0.43_0.50"])
        # match: STL sphere vs analytic sphere, revox pair
        b1 = os.path.join(td, "b1.csv")
        b2 = os.path.join(td, "b2.csv")
        series(b1, hdr % 0.5, 150.0, [0.465] * n150, [0.275] * n150)
        series(b2, hdr % 0.5, 150.0, [0.515] * n150, [0.275] * n150)
        truth("match: equal runs agree", match(ss, ss)["pass"])
        truth("match: Cd 0.465 vs 0.515 disagree", not match(summarise(b1, 15.0), summarise(b2, 15.0))["Cd"]["ok"])
    if fails:
        print("SELFTEST FAILED:\n  " + "\n  ".join(fails))
        return 1
    print("selftest ok (%d checks)" % len(done))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", choices=["summary", "grid", "v1", "v2", "match"])
    ap.add_argument("files", nargs="*")
    ap.add_argument("--t0", type=float, default=15.0, help="start of the averaging window in t* (default 15)")
    ap.add_argument("--t1", type=float, default=None, help="end of the averaging window in t* (default: end of run)")
    ap.add_argument("--box", type=float, default=1.0, help="v1: box-correction factor applied to Cd")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.cmd == "summary" and a.files:
        for p in a.files:
            s = summarise(p, a.t0, a.t1)
            print(json.dumps(s) if a.json else fmt(s))
        return 0
    if a.cmd == "grid" and len(a.files) == 2:
        print(json.dumps(grid(a.files[0], a.files[1], a.t0), indent=1))
        return 0
    if a.cmd == "v1" and len(a.files) == 1:
        print(json.dumps(v1_verdict(summarise(a.files[0], a.t0, a.t1), a.box), indent=1))
        return 0
    if a.cmd == "v2" and len(a.files) == 2:
        print(json.dumps(v2_verdict(summarise(a.files[0], a.t0, a.t1), read_run(a.files[1])[1], a.t0), indent=1))
        return 0
    if a.cmd == "match" and len(a.files) == 2:
        print(json.dumps(match(summarise(a.files[0], a.t0, a.t1), summarise(a.files[1], a.t0, a.t1)), indent=1))
        return 0
    ap.print_usage()
    return 2


if __name__ == "__main__":
    sys.exit(main())
