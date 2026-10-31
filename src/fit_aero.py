"""Fit POLLEN drag and spin lift from a tracked side-view video (PM-018 measurement kit).

Same flight equations as viz/explorer/physics.js ``integrate`` (planar, fixed-step RK4, constant Cd, Magnus lift
with exponential spin decay) and the same fitting steps as viz/measure/measure.js:

    a = -q Cd |v| v - g z_hat + q Cl(S) |v| sgn(w0) (-vz, vx),   q = rho pi R^2 / (2 m)
    S(t) = |w0| exp(-k t) R / |v|,   Cl = Cl (single) | c1 S (linear) | min(c1 S, Cl_max) (capped)

Twin test (docs/MEASURE.md): shot A has no spin and sets (x0, z0, vx0, vz0, Cd); shot B is the backspin shot with the
same settings, Cd is held at A's value and B sets (x0, z0, vx0, vz0, lift [, S0]). Uncertainty: Jacobian (Gauss-Newton
covariance, isotropic pixel noise) and an optional residual bootstrap; B's lift error also carries A's Cd error.
Every fitted number is *derived* (a fit to the user's video); the spin decay k is ASSUMED unless measured (T3).

CLI:  python -B -m src.fit_aero track.csv [--lift single|linear|capped] [--boot 200] [--scale clicked|gravity]
      [--k 0.03]
The CSV is the text measure.html exports (columns shot,frame,t_s,x_m,z_m,...; '# key=value' header lines).
"""
from __future__ import annotations

import argparse
import math
import random
import sys
from typing import Dict, List, Optional, Sequence

import numpy as np

G = 9.80665
# ball and air defaults (labels): mass 24.95 g AndyMark nominal (user/vendor), radius 35.5 mm official nominal,
# rho 1.204 kg/m^3 = 20 C dry sea level (derived), spin decay k 0.03 1/s (ASSUMED, explorer default).
DEFAULTS = {"rho": 1.204, "mass": 0.02495, "radius": 0.0355, "k": 0.03, "g": G}
WHEEL_R = 0.049          # m, the 98 mm flywheel (user)
CORR_FLAG = 0.995        # |correlation| above this: the track cannot separate the pair
CORR_NOTE = 0.9          # a weakly set parameter names its partner above this |correlation|
REL_FLAG = 0.5           # 95 % half-width above 50 % of the value: weakly set


# ---------------------------------------------------------------- flight model (mirror of physics.js integrate)
def _cl(lift: str, lp: Sequence[float], S: float) -> float:
    if lift == "single":
        return lp[0]
    if lift == "linear":
        return lp[0] * S
    return min(lp[0] * S, lp[1]) if lp[0] > 0 else 0.0   # capped: physics.js turns lift off when c1 <= 0


def simulate(t_eval: Sequence[float], x0: float, z0: float, vx0: float, vz0: float, Cd: float,
             lift: Optional[str] = None, lp: Sequence[float] = (), spin: Optional[Dict] = None,
             p: Optional[Dict] = None, dt: float = 1e-3):
    """Positions (x, z) at t_eval (s, from the first tracked frame). spin = {'S0': s} (w0 = S0 v0 / R, as in
    physics.js) or {'rpm': n} (w0 = 2 pi n / 60, + = backspin on a ball moving toward +x)."""
    p = {**DEFAULTS, **(p or {})}
    R, g, k = p["radius"], p["g"], p["k"]
    q = 0.5 * p["rho"] * math.pi * R * R / p["mass"]
    v0 = math.hypot(vx0, vz0)
    w0 = 0.0
    if spin:
        w0 = spin["rpm"] * 2 * math.pi / 60 if "rpm" in spin else spin["S0"] * v0 / R
    useM = lift is not None and w0 != 0 and p["rho"] > 0
    sgn, aw0 = math.copysign(1.0, w0), abs(w0)

    def acc(t, vx, vz):
        sp = math.sqrt(vx * vx + vz * vz)
        ax, az = -q * Cd * sp * vx, -q * Cd * sp * vz - g
        if useM:
            S = aw0 * math.exp(-k * t) * R / math.sqrt(sp * sp + 1e-12)
            f = q * _cl(lift, lp, S) * sp * sgn
            ax -= f * vz
            az += f * vx
        return ax, az

    t_eval = np.asarray(t_eval, float)
    tmax = float(t_eval.max()) if t_eval.size else 0.0
    n = int(math.ceil(tmax / dt)) + 2
    X = np.empty(n); Z = np.empty(n); VX = np.empty(n); VZ = np.empty(n)
    x, z, vx, vz, t = 0.0, 0.0, vx0, vz0, 0.0
    X[0], Z[0], VX[0], VZ[0] = x, z, vx, vz
    h2 = dt / 2
    for i in range(1, n):
        a1 = acc(t, vx, vz)
        a2 = acc(t + h2, vx + h2 * a1[0], vz + h2 * a1[1])
        a3 = acc(t + h2, vx + h2 * a2[0], vz + h2 * a2[1])
        a4 = acc(t + dt, vx + dt * a3[0], vz + dt * a3[1])
        x += dt * (vx + dt / 6 * (a1[0] + a2[0] + a3[0]))
        z += dt * (vz + dt / 6 * (a1[1] + a2[1] + a3[1]))
        vx += dt / 6 * (a1[0] + 2 * a2[0] + 2 * a3[0] + a4[0])
        vz += dt / 6 * (a1[1] + 2 * a2[1] + 2 * a3[1] + a4[1])
        t += dt
        X[i], Z[i], VX[i], VZ[i] = x, z, vx, vz
    # cubic Hermite between RK4 nodes (positions + velocities), same as measure.js
    j = np.clip(np.floor(t_eval / dt).astype(int), 0, n - 2)
    s = t_eval / dt - j
    h00 = 2 * s ** 3 - 3 * s ** 2 + 1; h10 = s ** 3 - 2 * s ** 2 + s; h01 = -2 * s ** 3 + 3 * s ** 2; h11 = s ** 3 - s ** 2
    xs = h00 * X[j] + h10 * dt * VX[j] + h01 * X[j + 1] + h11 * dt * VX[j + 1]
    zs = h00 * Z[j] + h10 * dt * VZ[j] + h01 * Z[j + 1] + h11 * dt * VZ[j + 1]
    return x0 + xs, z0 + zs


# ---------------------------------------------------------------- generic Levenberg-Marquardt + uncertainty
def _lm(resid, theta0, scale, max_iter=60):
    th = np.array(theta0, float)
    r = resid(th)
    cost = float(r @ r)
    lam = 1e-3
    rel = 1.0
    for _ in range(max_iter):
        J = _jac(resid, th, r, scale)
        A = J.T @ J
        gvec = J.T @ r
        improved = False
        for _ in range(12):
            M = A + lam * np.diag(np.maximum(np.diag(A), 1e-30))
            try:
                d = -np.linalg.solve(M, gvec)
            except np.linalg.LinAlgError:
                lam *= 10
                continue
            r2 = resid(th + d)
            c2 = float(r2 @ r2)
            if c2 < cost:
                rel = (cost - c2) / max(cost, 1e-300)
                th, r, cost = th + d, r2, c2
                lam = max(lam / 5, 1e-9)
                improved = True
                break
            lam *= 8
        if not improved or rel < 1e-12:
            break
    J = _jac(resid, th, r, scale)
    return th, r, J


def _jac(resid, th, r, scale):
    J = np.empty((r.size, th.size))
    for i in range(th.size):
        h = 1e-6 * max(abs(th[i]), scale[i])
        tp = th.copy(); tp[i] += h
        J[:, i] = (resid(tp) - r) / h
    return J


def _uncertainty(names, th, r, J):
    n, m = r.size, th.size
    dof = max(n - m, 1)
    s2 = float(r @ r) / dof
    A = J.T @ J
    d = np.sqrt(np.maximum(np.diag(A), 1e-300))
    An = A / np.outer(d, d)
    zero = [names[i] for i in range(m) if np.diag(A)[i] < 1e-24]
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):   # a zero-dependence column is ~1e300
        try:
            Ainv = np.linalg.inv(An + 1e-12 * np.eye(m)) / np.outer(d, d)
        except np.linalg.LinAlgError:
            Ainv = np.linalg.pinv(An) / np.outer(d, d)
        cov = s2 * Ainv
        sd = np.sqrt(np.maximum(np.nan_to_num(np.diag(cov), nan=np.inf), 0))
        corr = np.nan_to_num(cov / np.outer(np.maximum(sd, 1e-300), np.maximum(sd, 1e-300)), nan=0.0,
                             posinf=0.0, neginf=0.0)
    flags = []
    for nm in zero:
        flags.append(f"the track does not depend on {nm} at all: it cannot be fitted from this shot")
    for i in range(m):
        for j in range(i + 1, m):
            if abs(corr[i, j]) > CORR_FLAG and names[i] not in zero and names[j] not in zero:
                flags.append(f"cannot separate {names[i]} and {names[j]} (correlation {corr[i, j]:+.3f}): "
                             "this track only sets a combination of the two")
    return {"sd": sd, "cov": cov, "corr": corr, "rms": math.sqrt(float(r @ r) / n), "dof": dof, "flags": flags, "zero": zero}


def _guess(t, x, z):
    t = np.asarray(t); n = min(len(t), 15)
    px = np.polyfit(t[:n], x[:n], 2 if n >= 4 else 1)
    pz = np.polyfit(t[:n], z[:n], 2 if n >= 4 else 1)
    return [float(np.polyval(px, 0)), float(np.polyval(pz, 0)), float(np.polyval(np.polyder(px), 0)),
            float(np.polyval(np.polyder(pz), 0))]


def orient(x):
    """Mirror x so the ball travels toward +x (physics frame). Returns (x, sign)."""
    x = np.asarray(x, float)
    sgn = 1.0 if x[-1] >= x[0] else -1.0
    return x * sgn, sgn


# ---------------------------------------------------------------- the two fits
def fit_nospin(t, x, z, p=None, boot=0, seed=20261031, fit_cd=True, cd=0.5, fit_scale=False, len_scale_sd=0.0):
    """Shot A (no spin): fit x0, z0, vx0, vz0, Cd. Returns a result dict (numbers are derived).

    fit_scale=True also fits len_scale = (video metres) / (true metres), the gravity check: g is known, so a free fall
    sets the length scale independently of the clicked scale bar (correlation with Cd about -0.4 on a 0.7 s track).
    The scale multiplies the displacement from the first tracked point, not the frame coordinates: the same family of
    paths as scaling about the frame origin (x0, z0 absorb the offset), but x0, z0 no longer trade off against the
    scale, so a ball far from the frame origin (a drop from 4 m) does not raise a false 'cannot separate' flag.
    A 1 % scale error moves Cd by about 4 % and a single Cl by about 19 % (derived, docs/MEASURE.md), so the scale is
    the main systematic error of this kit. Without fit_scale, len_scale_sd (relative error of the clicked scale) is
    carried into Cd by refitting at scale 1 +/- len_scale_sd and adding in quadrature (sd_total)."""
    t = np.asarray(t, float); x, _ = orient(x); z = np.asarray(z, float)
    names = ["x0", "z0", "vx0", "vz0"] + (["Cd"] if fit_cd else []) + (["len_scale"] if fit_scale else [])

    def model(th):
        xm, zm = simulate(t, th[0], th[1], th[2], th[3], th[4] if fit_cd else cd, p=p)
        if fit_scale:   # scale the flight about its first tracked point; x0, z0 are then video metres (see docstring)
            xm, zm = th[0] + th[-1] * (xm - th[0]), th[1] + th[-1] * (zm - th[1])
        return xm, zm

    def resid_for(xd, zd):
        def f(th):
            xm, zm = model(th)
            return np.concatenate([xm - xd, zm - zd])
        return f

    th0 = _guess(t, x, z) + ([cd] if fit_cd else []) + ([1.0] if fit_scale else [])
    scale = [0.1, 0.1, 1.0, 1.0] + ([0.1] if fit_cd else []) + ([0.01] if fit_scale else [])
    th, r, J = _lm(resid_for(x, z), th0, scale)
    out = _pack(names, th, r, J)
    out["sd_total"] = dict(out["sd"])
    if len_scale_sd > 0 and not fit_scale:
        dl = [_lm(resid_for(x / (1 + g * len_scale_sd), z / (1 + g * len_scale_sd)), th, scale)[0] - th
              for g in (1, -1)]
        part = (np.abs(dl[0]) + np.abs(dl[1])) / 2
        out["sd_scale_part"] = {nm: float(part[i]) for i, nm in enumerate(names)}
        out["sd_total"] = {nm: float(math.hypot(out["sd"][nm], part[i])) for i, nm in enumerate(names)}
    if boot:
        out["boot"] = _bootstrap(resid_for, model, th, r, scale, names, boot, seed)
    out["v0"] = math.hypot(th[2], th[3]); out["theta_deg"] = math.degrees(math.atan2(th[3], th[2]))
    return out


def fit_lift(t, x, z, cd, cd_sd=0.0, lift="single", spin=None, fit_spin=False, p=None, boot=0,
             seed=20261031, cl0=None, len_scale=1.0, len_scale_sd=0.0):
    """Shot B (backspin, same settings as A): Cd held at A's value; fit x0, z0, vx0, vz0, lift params [, S0].

    spin: {'rpm': n} measured ball spin (user) or {'S0': s} (e.g. 1.0 ideal hood, ASSUMED). fit_spin=True frees S0
    (start at spin['S0'] or 1); a single Cl never depends on S0 and c1 only through c1*S0, so that case is flagged.
    The lift error includes A's Cd error (refit at Cd +/- cd_sd, added in quadrature). len_scale (from shot A's
    gravity check, same camera and scale) divides the clicked positions; its error is carried the same way."""
    t = np.asarray(t, float); x, _ = orient(x); z = np.asarray(z, float)
    lnames = {"single": ["Cl"], "linear": ["c1"], "capped": ["c1", "Cl_max"]}[lift]
    names = ["x0", "z0", "vx0", "vz0"] + lnames + (["S0"] if fit_spin else [])
    nl = len(lnames)
    spin = dict(spin or {"S0": 1.0})

    def model_cd(cdv):
        def model(th):
            sp = {"S0": th[4 + nl]} if fit_spin else spin
            return simulate(t, th[0], th[1], th[2], th[3], cdv, lift, th[4:4 + nl], sp, p)
        return model

    def resid_for_cd(cdv, sv=len_scale):
        m = model_cd(cdv)

        def rf(xd, zd):
            xs, zs = xd / sv, zd / sv

            def f(th):
                xm, zm = m(th)
                return np.concatenate([xm - xs, zm - zs])
            return f
        return rf

    if cl0 is None:
        cl0 = {"single": [0.15], "linear": [0.2], "capped": [0.4, 0.25]}[lift]
    th0 = _guess(t, x, z) + list(cl0) + ([spin.get("S0", 1.0)] if fit_spin else [])
    scale = [0.1, 0.1, 1.0, 1.0] + [0.1] * nl + ([0.5] if fit_spin else [])
    th, r, J = _lm(resid_for_cd(cd)(x, z), th0, scale)
    out = _pack(names, th, r, J)
    # carry A's Cd error into the lift numbers
    out["cd_used"] = cd
    out["len_scale_used"] = len_scale
    if cd_sd > 0 or len_scale_sd > 0:
        parts = {}
        for key, args in (("cd", [(cd + g * cd_sd, len_scale) for g in (1, -1)] if cd_sd > 0 else []),
                          ("len_scale", [(cd, len_scale + g * len_scale_sd) for g in (1, -1)]
                           if len_scale_sd > 0 else [])):
            if args:
                dl = [_lm(resid_for_cd(*a)(x, z), th, scale)[0] - th for a in args]
                parts[key] = (np.abs(dl[0]) + np.abs(dl[1])) / 2
        tot = np.sqrt(np.array([out["sd"][nm] for nm in names]) ** 2 + sum(v ** 2 for v in parts.values()))
        out["sd_cd_part"] = {nm: float(parts["cd"][i]) if "cd" in parts else 0.0 for i, nm in enumerate(names)}
        out["sd_scale_part"] = {nm: float(parts["len_scale"][i]) if "len_scale" in parts else 0.0
                                for i, nm in enumerate(names)}
        out["sd_total"] = {nm: float(tot[i]) for i, nm in enumerate(names)}
        weak = _weak_flags(names, out["value"], out["sd_total"], out["corr"], " (with A's Cd and scale error)",
                            skip=out["zero"])
        out["flags"] = [f for f in out["flags"] if "weakly set" not in f] + weak
    else:
        out["sd_total"] = dict(out["sd"])
    if boot:
        out["boot"] = _bootstrap(None, None, th, r, scale, names, boot, seed,
                                 cd_mode=(resid_for_cd, model_cd, cd, cd_sd, len_scale, len_scale_sd))
    v0 = math.hypot(th[2], th[3])
    out["v0"] = v0; out["theta_deg"] = math.degrees(math.atan2(th[3], th[2]))
    # spin along the tracked part and the matching explorer table points
    if fit_spin:
        S0 = th[4 + nl]
    elif "rpm" in spin:
        S0 = spin["rpm"] * 2 * math.pi / 60 * {**DEFAULTS, **(p or {})}["radius"] / v0 if v0 > 0 else 0.0
    else:
        S0 = spin["S0"]
    out["S0"] = S0
    out["S_range"] = _s_range(t, th, cd, S0, p)
    # no-spin twin: same release point, velocity and Cd, no lift
    xt, zt = simulate(t, th[0], th[1], th[2], th[3], cd, p=p)
    xb, zb = simulate(t, th[0], th[1], th[2], th[3], cd, lift, th[4:4 + nl],
                      {"S0": S0}, p)
    out["twin_dz_end"] = float(zb[-1] - zt[-1])
    out["twin_dx_end"] = float(xb[-1] - xt[-1])
    out["twin_dmax"] = float(np.max(np.hypot(xb - xt, zb - zt)))
    out["table"] = _table(lift, th[4:4 + nl], out["S_range"])
    out["lift_detected"] = _detected(out, lnames[0])
    return out


def _s_range(t, th, cd, S0, p):
    """S at the first and last tracked frame along the no-spin-twin speed (k ASSUMED)."""
    pp = {**DEFAULTS, **(p or {})}
    R = pp["radius"]
    v0 = math.hypot(th[2], th[3])
    w0 = S0 * v0 / R
    # speeds from finite differences of the twin path (lift barely changes |v|)
    tt = np.array([t[0], t[0] + 1e-3, t[-1] - 1e-3, t[-1]])
    xs, zs = simulate(tt, th[0], th[1], th[2], th[3], cd, p=p)
    va = math.hypot(xs[1] - xs[0], zs[1] - zs[0]) / 1e-3
    vb = math.hypot(xs[3] - xs[2], zs[3] - zs[2]) / 1e-3
    Sa = abs(w0) * math.exp(-pp["k"] * t[0]) * R / max(va, 1e-9)
    Sb = abs(w0) * math.exp(-pp["k"] * t[-1]) * R / max(vb, 1e-9)
    return (min(Sa, Sb), max(Sa, Sb))


def _table(lift, lp, srange):
    s0, s1 = srange
    if lift == "single":
        return f"{(s0 + s1) / 2:.2f}:{lp[0]:.3f}"
    if lift == "linear":
        return f"0:0, {s1:.2f}:{lp[0] * s1:.3f}"
    knee = lp[1] / lp[0] if lp[0] > 0 else s1
    return f"0:0, {knee:.2f}:{lp[1]:.3f}"


def _detected(out, nm):
    sd = out["sd_total"][nm]
    lo, hi = out["value"][nm] - 1.96 * sd, out["value"][nm] + 1.96 * sd
    return not (lo <= 0 <= hi)


def _weak_flags(names, val, sd, corr, note="", skip=()):
    out = []
    for i, nm in enumerate(names):
        if i < 4 or nm in skip or 1.96 * sd[nm] <= REL_FLAG * abs(val[nm]):
            continue
        msg = (f"{nm} is weakly set by this track{note}: 95 % half-width {1.96 * sd[nm]:.3g} "
               f"is over half its value {val[nm]:.3g}")
        j = max((k for k in range(len(names)) if k != i), key=lambda k: abs(corr[i][k]))
        if abs(corr[i][j]) > CORR_NOTE:
            msg += f", mostly because it trades off against {names[j]} (correlation {corr[i][j]:+.3f})"
        out.append(msg)
    return out


def _pack(names, th, r, J):
    u = _uncertainty(names, th, r, J)
    val = {nm: float(th[i]) for i, nm in enumerate(names)}
    sd = {nm: float(u["sd"][i]) for i, nm in enumerate(names)}
    ci = {nm: (val[nm] - 1.96 * sd[nm], val[nm] + 1.96 * sd[nm]) for nm in names}
    flags = list(u["flags"]) + _weak_flags(names, val, sd, u["corr"], skip=u["zero"])
    return {"names": names, "value": val, "sd": sd, "ci95": ci, "rms_m": u["rms"], "n": r.size // 2,
            "corr": u["corr"].tolist(), "flags": flags, "theta": th, "zero": u["zero"]}


def _bootstrap(resid_for, model, th, r, scale, names, nboot, seed, cd_mode=None):
    """Residual bootstrap: resample (dx, dz) residual pairs onto the fitted path and refit. With cd_mode, each
    replicate also draws Cd ~ N(Cd_A, sd_A) and len_scale ~ N(s_A, sd_s) (normal approximation of A's error)."""
    rng = random.Random(seed)
    n = r.size // 2
    rx, rz = r[:n].copy(), r[n:].copy()
    if cd_mode:
        rf_cd, model_cd, cd, cd_sd, ls, ls_sd = cd_mode
        xm, zm = model_cd(cd)(th)
        xm, zm = xm * ls, zm * ls
    else:
        xm, zm = model(th)
    draws = []
    for _ in range(nboot):
        idx = [rng.randrange(n) for _ in range(n)]
        xd = xm + rx[idx]; zd = zm + rz[idx]
        if cd_mode:
            cdv = cd + (rng.gauss(0, 1) * cd_sd if cd_sd > 0 else 0.0)
            sv = ls + (rng.gauss(0, 1) * ls_sd if ls_sd > 0 else 0.0)
            f = rf_cd(cdv, sv)(xd, zd)
        else:
            f = resid_for(xd, zd)
        tb, _, _ = _lm(f, th, scale, max_iter=25)
        draws.append(tb)
    D = np.array(draws)
    return {nm: {"sd": float(D[:, i].std(ddof=1)), "ci95": (float(np.percentile(D[:, i], 2.5)),
                                                             float(np.percentile(D[:, i], 97.5)))}
            for i, nm in enumerate(names)} | {"n": nboot}


# ---------------------------------------------------------------- CSV (measure.html export) and report
def parse_csv(text: str):
    """Returns {'meta': {...}, 'shots': {name: {'t','x','z','meta'}}}."""
    meta: Dict[str, str] = {}
    shots: Dict[str, Dict] = {}
    cols = None
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            body = line[1:].strip()
            if "=" in body:
                k, v = body.split("=", 1)
                meta[k.strip()] = v.strip()
            continue
        parts = [s.strip() for s in line.split(",")]
        if cols is None:
            cols = parts
            continue
        row = dict(zip(cols, parts))
        if _num(row.get("x_m")) is None or _num(row.get("z_m")) is None or _num(row.get("t_s")) is None:
            continue   # no scale yet (measure.html writes NaN) or an empty cell
        sh = shots.setdefault(row.get("shot", "A"), {"t": [], "x": [], "z": []})
        sh["t"].append(float(row["t_s"])); sh["x"].append(float(row["x_m"])); sh["z"].append(float(row["z_m"]))
    for nm, sh in shots.items():
        o = np.argsort(sh["t"])
        t = np.array(sh["t"])[o]
        sh["t"] = t - t[0]; sh["x"] = np.array(sh["x"])[o]; sh["z"] = np.array(sh["z"])[o]
        sh["meta"] = {k.split(".", 1)[1]: v for k, v in meta.items() if k.startswith(nm + ".")}
    return {"meta": {k: v for k, v in meta.items() if "." not in k}, "shots": shots}


def _num(s):
    try:
        v = float(s)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def _fmt(res, nm, digits=3):
    v = res["value"][nm]
    sd = res.get("sd_total", res["sd"])[nm]
    s = f"{nm} = {v:.{digits}f} +/- {1.96 * sd:.{digits}f} (95 %, Jacobian)"
    if "boot" in res:
        b = res["boot"][nm]["ci95"]
        s += f"; bootstrap 95 % {b[0]:.{digits}f} .. {b[1]:.{digits}f}"
    return s


CLICK_PX = 0.5   # px, ASSUMED click error at each end of the scale bar


def _clicked_scale_sd(meta):
    """Relative error of the clicked scale from its length in pixels (cal_px = 'x1 y1 x2 y2'), or None."""
    v = [_num(u) for u in str(meta.get("cal_px", "")).split()]
    if len(v) < 4 or any(u is None for u in v[:4]):
        return None
    L = math.hypot(v[2] - v[0], v[3] - v[1])
    return math.sqrt(2) * CLICK_PX / L if L > 0 else None


def report(data, lift="single", boot=0, p=None, scale="clicked"):
    """Text report. scale='clicked' keeps the clicked scale (its click error is carried) and shows the gravity check;
    scale='gravity' uses shot A's gravity-checked scale for both shots."""
    lines = ["POLLEN aero fit (numbers are derived: fits to the user's video; k ASSUMED unless measured)"]
    shots = data["shots"]
    sd_click = _clicked_scale_sd(data["meta"])
    A = shots.get("A")
    resA, chk = None, None
    if A is not None and len(A["t"]) >= 6:
        chk = fit_nospin(A["t"], A["x"], A["z"], p=p, fit_scale=True, boot=boot if scale == "gravity" else 0)
        resA = chk if scale == "gravity" else fit_nospin(A["t"], A["x"], A["z"], p=p, boot=boot,
                                                         len_scale_sd=sd_click or 0.0)
        lines.append(f"Shot A (no spin, the twin): {resA['n']} points, rms residual {resA['rms_m'] * 1000:.1f} mm")
        lines.append(f"  v0 = {resA['v0']:.2f} m/s, angle {resA['theta_deg']:.1f} deg (derived)")
        lines.append("  " + _fmt(resA, "Cd"))
        s_, sd_s = chk["value"]["len_scale"], chk["sd"]["len_scale"]
        lines.append(f"  gravity check: video length / true length = {s_:.4f} +/- {1.96 * sd_s:.4f} (95 %, derived); "
                     + (f"clicked scale error +/- {1.96 * sd_click * 100:.2f} % (ASSUMED {CLICK_PX} px clicks)"
                        if sd_click else "clicked scale error unknown (no cal_px)")
                     + f"; scale used: {scale}")
        if abs(s_ - 1) > 1.96 * math.hypot(sd_s, sd_click or 0.0):
            lines.append(f"  ! the clicked scale and gravity disagree by {(s_ - 1) * 100:+.2f} %: check that the scale "
                         "bar is in the flight plane, or the no-spin ball still had spin")
        wr = _num(A["meta"].get("wheel_rpm"))
        if wr:
            lines.append(f"  v/u = {resA['v0'] / (wr * 2 * math.pi / 60 * WHEEL_R):.3f} (derived, wheel {wr:.0f} rpm user)")
        lines += ["  ! " + f for f in resA["flags"]]
    B = shots.get("B")
    if B is not None and len(B["t"]) >= 6:
        if resA is None:
            lines.append("Shot B has no shot A twin: Cd held at 0.5 (ASSUMED); lift numbers are not usable alone.")
        cd = resA["value"]["Cd"] if resA else 0.5
        cd_sd = resA["sd"]["Cd"] if resA else 0.0
        if scale == "gravity" and chk:
            ls, ls_sd = chk["value"]["len_scale"], chk["sd"]["len_scale"]
        else:
            ls, ls_sd = 1.0, sd_click or 0.0
        # measure.html writes B.S0 only when its spin source is not "ball rpm" (it may still keep a typed ball_rpm):
        # follow the page, so the offline fit uses the same spin as the page did
        s0 = _num(B["meta"].get("S0"))
        rpm = None if s0 is not None else _num(B["meta"].get("ball_rpm"))
        spin = {"rpm": rpm} if rpm else {"S0": s0 if s0 is not None else 1.0}
        resB = fit_lift(B["t"], B["x"], B["z"], cd, cd_sd, lift=lift, spin=spin, p=p, boot=boot,
                        len_scale=ls, len_scale_sd=ls_sd)
        lines.append(f"Shot B (backspin, Cd held at A's {cd:.3f}, scale x{1 / ls:.4f}): {resB['n']} points, "
                     f"rms {resB['rms_m'] * 1000:.1f} mm")
        lines.append(f"  v0 = {resB['v0']:.2f} m/s, angle {resB['theta_deg']:.1f} deg (derived)")
        lines.append(f"  spin: S0 = {resB['S0']:.2f} ({'ball rpm, user' if rpm else 'ASSUMED S0'}), "
                     f"S along the track {resB['S_range'][0]:.2f} .. {resB['S_range'][1]:.2f} (derived, k ASSUMED)")
        for nm in resB["names"][4:]:
            lines.append("  " + _fmt(resB, nm) + " (includes A's Cd error and the scale error)")
        lines.append(f"  no-spin twin (same launch, same Cd): lift moves the ball {resB['twin_dmax'] * 1000:.0f} mm by "
                     f"the last frame (height {resB['twin_dz_end'] * 1000:+.0f} mm), noise rms {resB['rms_m'] * 1000:.1f} mm")
        lines.append("  lift " + ("detected (95 % interval excludes 0)" if resB["lift_detected"]
                                  else "NOT detected (95 % interval includes 0)"))
        lines.append(f"  explorer lift table S:Cl -> {resB['table']}")
        lines += ["  ! " + f for f in resB["flags"]]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("csv")
    ap.add_argument("--lift", choices=["single", "linear", "capped"], default="single")
    ap.add_argument("--boot", type=int, default=0)
    ap.add_argument("--scale", choices=["clicked", "gravity"], default="clicked",
                    help="length scale: the clicked bar (default) or shot A's gravity check")
    ap.add_argument("--k", type=float, default=None, help="spin decay 1/s (ASSUMED 0.03)")
    ap.add_argument("--rho", type=float, default=None)
    ap.add_argument("--mass", type=float, default=None, help="kg")
    ap.add_argument("--radius", type=float, default=None, help="m")
    a = ap.parse_args(argv)
    with open(a.csv, encoding="utf-8") as fh:
        data = parse_csv(fh.read())
    p = {}
    for key in ("rho", "mass", "radius", "k"):
        v = getattr(a, key)
        if v is None:
            v = _num(data["meta"].get(key))
        if v is not None:
            p[key] = v
    print(report(data, lift=a.lift, boot=a.boot, p=p, scale=a.scale))
    return 0


if __name__ == "__main__":
    sys.exit(main())
