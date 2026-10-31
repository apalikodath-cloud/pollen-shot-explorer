"""xflight.py - BLIND independent POLLEN free-flight model (HANDOFF section 4A).

Written for cross-validation of the main solver (src/flight.py) WITHOUT reading
src/ or docs/. Independence is the point: different integrator (fixed-step
classical RK4 with step-halving convergence control, no scipy.solve_ivp),
equations re-derived here from HANDOFF section 4A only.

Coordinates (right-handed, SI):
    x  horizontal, toward the target
    y  horizontal, sideways (y = z cross x, i.e. to the LEFT when facing +x)
    z  vertical, up
State s = [x, y, z, vx, vy, vz].

Equations of motion (v_rel = v - v_wind):
    m dv/dt = m g_vec + F_D + F_M
    g_vec   = (0, 0, -g)
    F_D     = -0.5 rho Cd A |v_rel| v_rel
    F_M     =  0.5 rho Cl A |v_rel|^2 unit(omega x v_rel)
    A       = pi R^2
    S(t)    = |omega(t)| R / max(|v_rel|, eps_v)
    Cl      = min(c1 * S, Cl_max)
    omega(t)= omega0 * exp(-k_spin t) * spin_axis      (analytic decay)
    omega0  = S0 * |v_rel(0)| / R                       (S0 = release spin parameter)

Backspin sign derivation (asserted in backspin_axis_check()):
    Ball moves +x. Backspin = the TOP of the ball (r = +R z_hat) moves
    BACKWARD (-x) relative to the centre. Surface velocity = omega x r.
    Need omega x z_hat = -x_hat.  Since y_hat x z_hat = +x_hat, omega must be
    along -y_hat.  So BACKSPIN AXIS = (0, -1, 0).
    Magnus direction: (-y_hat) x (+x_hat) = -(y_hat x x_hat) = -(-z_hat) = +z_hat
    -> upward lift on a forward-moving backspinning ball, as HANDOFF 4A requires.
    In the x-z plane the backspin Magnus direction is v rotated +90 deg:
    (vx, vz) -> (-vz, vx): rearward during ascent, forward during descent.

Regularisation: Cl is capped, so F_M <= 0.5 rho Cl_max A |v|^2 -> 0 as |v|->0;
F_D -> 0 likewise. If |omega x v_rel| == 0 the Magnus term is set to zero.

Labels: every output of this file is PREDICTED (model output). Parameter
labels are recorded in reference_cases.json["meta"]["parameters"].
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BACKSPIN_AXIS = np.array([0.0, -1.0, 0.0])


# --------------------------------------------------------------------------- #
# Parameters
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Params:
    m: float = 0.025          # kg   user/HANDOFF (AndyMark nominal 0.055 lb ~ 24.95 g)
    R: float = 0.0355         # m    HANDOFF official nominal 71 mm diameter
    rho: float = 1.225        # kg/m3 assumed (ISA sea-level standard air)
    Cd: float = 0.5           # -    ASSUMED PLACEHOLDER, uncalibrated
    c1: float = 0.3           # -    ASSUMED PLACEHOLDER, Cl = c1*S, uncalibrated
    Cl_max: float = 0.35      # -    ASSUMED PLACEHOLDER ceiling, uncalibrated
    k_spin: float = 0.0       # 1/s  ASSUMED PLACEHOLDER spin decay rate
    g: float = 9.81           # m/s2 assumed (match the main solver's g!)
    wind: tuple = (0.0, 0.0, 0.0)  # m/s, world frame
    eps_v: float = 1e-6       # m/s  speed floor in S

    @property
    def A(self) -> float:
        return math.pi * self.R * self.R


@dataclass(frozen=True)
class Launch:
    v0: float                 # m/s  release speed (ground frame)
    elev_deg: float           # deg  release elevation above horizontal, in x-z plane
    S0: float                 # -    release spin parameter |omega0| R / |v_rel(0)|
    z0: float = 0.3           # m    release height of ball CENTRE
    x0: float = 0.0
    spin_axis: tuple = (0.0, -1.0, 0.0)   # unit vector; default = backspin


# --------------------------------------------------------------------------- #
# Physics
# --------------------------------------------------------------------------- #
def omega0_mag(p: Params, L: Launch) -> float:
    e = math.radians(L.elev_deg)
    v = np.array([L.v0 * math.cos(e), 0.0, L.v0 * math.sin(e)])
    vrel = v - np.asarray(p.wind, float)
    return L.S0 * max(float(np.linalg.norm(vrel)), p.eps_v) / p.R


def accel(t: float, s: np.ndarray, p: Params, w0: float, axis: np.ndarray) -> np.ndarray:
    """Acceleration (3,) at time t, state s (6,)."""
    vrel = s[3:6] - np.asarray(p.wind, float)
    sp = math.sqrt(vrel[0] ** 2 + vrel[1] ** 2 + vrel[2] ** 2)
    a = np.array([0.0, 0.0, -p.g])
    q = 0.5 * p.rho * p.A / p.m
    a -= q * p.Cd * sp * vrel
    if w0 != 0.0:
        wmag = w0 * math.exp(-p.k_spin * t)
        omega = wmag * axis
        S = abs(wmag) * p.R / max(sp, p.eps_v)
        Cl = min(p.c1 * S, p.Cl_max)
        c = np.cross(omega, vrel)
        nc = math.sqrt(c[0] ** 2 + c[1] ** 2 + c[2] ** 2)
        if nc > 0.0:
            a += q * Cl * sp * sp * (c / nc)
    return a


def magnus_info(t, s, p, w0, axis):
    vrel = s[3:6] - np.asarray(p.wind, float)
    sp = float(np.linalg.norm(vrel))
    wmag = w0 * math.exp(-p.k_spin * t)
    S = abs(wmag) * p.R / max(sp, p.eps_v)
    Cl = min(p.c1 * S, p.Cl_max) if w0 != 0.0 else 0.0
    FM = 0.5 * p.rho * Cl * p.A * sp * sp if w0 != 0.0 else 0.0
    return dict(omega=wmag, S=S, Cl=Cl, F_M=FM, a_M=FM / p.m)


# --------------------------------------------------------------------------- #
# Fixed-step RK4
# --------------------------------------------------------------------------- #
def rk4_run(p: Params, L: Launch, dt: float, z_stop: float = 0.0, t_max: float = 10.0):
    """Integrate until descending through z_stop (centre height) or t_max.

    Returns t (N,), S (N,6), Acc (N,3). Steps are exactly dt so a run with dt/2
    shares every other node with a run at dt.
    """
    axis = np.asarray(L.spin_axis, float)
    axis = axis / np.linalg.norm(axis)
    w0 = omega0_mag(p, L)
    e = math.radians(L.elev_deg)
    s = np.array([L.x0, 0.0, L.z0, L.v0 * math.cos(e), 0.0, L.v0 * math.sin(e)])

    def f(t, s):
        return np.concatenate((s[3:6], accel(t, s, p, w0, axis)))

    nmax = int(math.ceil(t_max / dt)) + 1
    T = np.empty(nmax)
    X = np.empty((nmax, 6))
    Ac = np.empty((nmax, 3))
    t = 0.0
    T[0] = t
    X[0] = s
    Ac[0] = accel(t, s, p, w0, axis)
    n = 1
    while n < nmax:
        k1 = f(t, s)
        k2 = f(t + 0.5 * dt, s + 0.5 * dt * k1)
        k3 = f(t + 0.5 * dt, s + 0.5 * dt * k2)
        k4 = f(t + dt, s + dt * k3)
        s = s + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        t = n * dt
        T[n] = t
        X[n] = s
        Ac[n] = accel(t, s, p, w0, axis)
        n += 1
        if s[5] < 0.0 and s[2] < z_stop:
            break
    return T[:n], X[:n], Ac[:n], w0, axis


def converged_run(p: Params, L: Launch, dt0: float = 2e-3, tol: float = 1e-8,
                  max_halvings: int = 10, z_stop: float = 0.0):
    """Step-halving: halve dt until max position change at shared nodes < tol (m)."""
    prev = rk4_run(p, L, dt0, z_stop)
    dt = dt0
    for _ in range(max_halvings):
        dt /= 2.0
        cur = rk4_run(p, L, dt, z_stop)
        Tp, Xp = prev[0], prev[1]
        Xc = cur[1][::2]
        n = min(len(Xp), len(Xc))
        err = float(np.max(np.abs(Xc[:n, :3] - Xp[:n, :3])))
        if err < tol:
            return cur, dt, err
        prev = cur
    raise RuntimeError(f"RK4 did not converge to {tol} m (last err {err:.3e}, dt {dt})")


# --------------------------------------------------------------------------- #
# Cubic Hermite dense output + event location
# --------------------------------------------------------------------------- #
def _herm(y0, y1, d0, d1, h, u):
    u2, u3 = u * u, u * u * u
    return ((2 * u3 - 3 * u2 + 1) * y0 + (u3 - 2 * u2 + u) * h * d0
            + (-2 * u3 + 3 * u2) * y1 + (u3 - u2) * h * d1)


def _bisect(fn, a, b, it=80):
    fa = fn(a)
    for _ in range(it):
        mid = 0.5 * (a + b)
        fm = fn(mid)
        if (fm > 0) == (fa > 0):
            a, fa = mid, fm
        else:
            b = mid
    return 0.5 * (a + b)


def interp_state(T, X, Ac, i, u):
    """State (x,z,vx,vz) at fraction u of step i via Hermite (pos uses vel, vel uses acc)."""
    h = T[i + 1] - T[i]
    out = {}
    out["t"] = T[i] + u * h
    out["x"] = _herm(X[i, 0], X[i + 1, 0], X[i, 3], X[i + 1, 3], h, u)
    out["z"] = _herm(X[i, 2], X[i + 1, 2], X[i, 5], X[i + 1, 5], h, u)
    out["vx"] = _herm(X[i, 3], X[i + 1, 3], Ac[i, 0], Ac[i + 1, 0], h, u)
    out["vz"] = _herm(X[i, 5], X[i + 1, 5], Ac[i, 2], Ac[i + 1, 2], h, u)
    return out


def find_apex(T, X, Ac):
    vz = X[:, 5]
    idx = np.nonzero((vz[:-1] > 0) & (vz[1:] <= 0))[0]
    if len(idx) == 0:
        return None
    i = int(idx[0])
    h = T[i + 1] - T[i]
    u = _bisect(lambda u: _herm(X[i, 5], X[i + 1, 5], Ac[i, 2], Ac[i + 1, 2], h, u), 0.0, 1.0)
    return interp_state(T, X, Ac, i, u), i, u


def find_descending_crossing(T, X, Ac, zc):
    z = X[:, 2]
    idx = np.nonzero((z[:-1] >= zc) & (z[1:] < zc) & (X[1:, 5] < 0))[0]
    if len(idx) == 0:
        return None
    i = int(idx[-1])           # last descending crossing
    h = T[i + 1] - T[i]
    u = _bisect(lambda u: _herm(X[i, 2], X[i + 1, 2], X[i, 5], X[i + 1, 5], h, u) - zc, 0.0, 1.0)
    return interp_state(T, X, Ac, i, u)


def dense(T, X, Ac, sub=8):
    """Resample (t, x, z) at sub points per step using Hermite."""
    u = np.arange(sub) / sub
    ts, xs, zs = [], [], []
    for i in range(len(T) - 1):
        h = T[i + 1] - T[i]
        ts.append(T[i] + u * h)
        xs.append(_herm(X[i, 0], X[i + 1, 0], X[i, 3], X[i + 1, 3], h, u))
        zs.append(_herm(X[i, 2], X[i + 1, 2], X[i, 5], X[i + 1, 5], h, u))
    ts.append([T[-1]]); xs.append([X[-1, 0]]); zs.append([X[-1, 2]])
    return np.concatenate(ts), np.concatenate(xs), np.concatenate(zs)


# --------------------------------------------------------------------------- #
# Case evaluation
# --------------------------------------------------------------------------- #
def simulate(p: Params, L: Launch):
    (T, X, Ac, w0, axis), dt, err = converged_run(p, L, z_stop=-0.05)
    ap = find_apex(T, X, Ac)
    out = {"dt_final_s": dt, "halving_err_m": err, "omega0_rad_s": w0,
           "omega0_rpm": w0 * 60 / (2 * math.pi)}
    if ap is not None:
        a, i, u = ap
        s_ap = np.array([a["x"], 0.0, a["z"], a["vx"], 0.0, a["vz"]])
        mi = magnus_info(a["t"], s_ap, p, w0, axis)
        out["apex"] = {"t": a["t"], "x": a["x"], "z": a["z"], "vx": a["vx"],
                       "omega_rad_s": mi["omega"], "S": mi["S"], "Cl": mi["Cl"],
                       "F_M_N": mi["F_M"], "a_M_m_s2": mi["a_M"]}
    else:
        out["apex"] = None
    for key, zc in (("z1p0", 1.0), ("z0p3", L.z0), ("ground_R", p.R)):
        c = find_descending_crossing(T, X, Ac, zc)
        out[key] = None if c is None else {"t": c["t"], "x": c["x"], "vx": c["vx"], "vz": c["vz"]}
    out["flight_time_s"] = out["z0p3"]["t"] if out["z0p3"] else None
    # horizontal reversal test (HANDOFF 0): min vx over flight up to return to z0
    tend = out["flight_time_s"] if out["flight_time_s"] else T[-1]
    m = T <= tend
    out["min_vx_m_s"] = float(np.min(X[m, 3]))
    out["horizontal_reversal"] = bool(out["min_vx_m_s"] < 0.0)
    return out, (T, X, Ac)


def twin_difference(trajA, trajB, tendA, tendB):
    """max |dz| spin (A) vs no-spin (B): at equal x and at equal t, over common range
    up to each trajectory's return to release height."""
    tA, xA, zA = dense(*trajA)
    tB, xB, zB = dense(*trajB)
    mA, mB = tA <= tendA, tB <= tendB
    tA, xA, zA = tA[mA], xA[mA], zA[mA]
    tB, xB, zB = tB[mB], xB[mB], zB[mB]
    res = {}
    # equal x (requires monotonic x on both)
    if np.all(np.diff(xA) > 0) and np.all(np.diff(xB) > 0):
        xmax = min(xA[-1], xB[-1])
        k = xA <= xmax
        dz = zA[k] - np.interp(xA[k], xB, zB)
        j = int(np.argmax(np.abs(dz)))
        res["equal_x"] = {"max_abs_dz_m": float(abs(dz[j])), "signed_dz_m": float(dz[j]),
                          "x_m": float(xA[k][j]), "z_spin_m": float(zA[k][j]),
                          "t_spin_s": float(tA[k][j]), "common_x_max_m": float(xmax),
                          "at_end_of_common_range": bool(j == int(np.sum(k)) - 1)}
    else:
        res["equal_x"] = None
    tmax = min(tA[-1], tB[-1])
    k = tA <= tmax
    dz = zA[k] - np.interp(tA[k], tB, zB)
    j = int(np.argmax(np.abs(dz)))
    res["equal_t"] = {"max_abs_dz_m": float(abs(dz[j])), "signed_dz_m": float(dz[j]),
                      "t_s": float(tA[k][j]), "x_spin_m": float(xA[k][j]),
                      "z_spin_m": float(zA[k][j]), "common_t_max_s": float(tmax)}
    return res


# --------------------------------------------------------------------------- #
# Reference cases
# --------------------------------------------------------------------------- #
LAUNCH_STATES = [(3.0, 80.0), (5.0, 55.0), (7.5, 70.0), (10.0, 30.0)]
# (S0, k_spin). With the placeholder c1/Cl_max, Cl saturates for S >= Cl_max/c1 = 1.167, and S
# grows as the ball slows, so (2, 0.5) would duplicate (2, 0) exactly; (0.5, 0.5) tests decay instead.
SPIN_CONFIGS = [(0.0, 0.0), (0.5, 0.0), (1.0, 0.0), (2.0, 0.0), (0.5, 0.5), (1.0, 0.5)]


def _round(o, nd=7):
    if isinstance(o, float):
        return round(o, nd)
    if isinstance(o, dict):
        return {k: _round(v, nd) for k, v in o.items()}
    if isinstance(o, list):
        return [_round(v, nd) for v in o]
    return o


def build_cases(g: float = 9.81):
    base = Params(g=g)
    cases = []
    runs = {}
    cid = 0
    for (v0, el) in LAUNCH_STATES:
        for (S0, k) in SPIN_CONFIGS:
            cid += 1
            p = Params(g=g, k_spin=k)
            L = Launch(v0=v0, elev_deg=el, S0=S0)
            out, traj = simulate(p, L)
            name = f"PM001-{cid:02d}"
            runs[name] = (out, traj)
            cases.append({"id": name, "twin_id": None,
                          "inputs": {"v0_m_s": v0, "elev_deg": el, "S0": S0, "k_spin_1_s": k,
                                     "z0_m": L.z0, "x0_m": L.x0,
                                     "spin_axis": list(L.spin_axis), "wind_m_s": list(p.wind)},
                          "outputs": out})
    # twins: no-spin case of same launch state
    for c in cases:
        i = c["inputs"]
        twin = next(d for d in cases if d["inputs"]["v0_m_s"] == i["v0_m_s"]
                    and d["inputs"]["elev_deg"] == i["elev_deg"] and d["inputs"]["S0"] == 0.0)
        c["twin_id"] = twin["id"]
        if c is twin:
            c["outputs"]["spin_vs_nospin"] = {"note": "this IS the no-spin twin; dz == 0"}
            continue
        oA, tA = runs[c["id"]]
        oB, tB = runs[twin["id"]]
        d = twin_difference(tA, tB, oA["flight_time_s"], oB["flight_time_s"])
        if oA["z1p0"] and oB["z1p0"]:
            d["dx_at_z1p0_m"] = oA["z1p0"]["x"] - oB["z1p0"]["x"]
        else:
            d["dx_at_z1p0_m"] = None
        d["dx_at_z0p3_m"] = oA["z0p3"]["x"] - oB["z0p3"]["x"]
        d["dz_apex_m"] = oA["apex"]["z"] - oB["apex"]["z"]
        c["outputs"]["spin_vs_nospin"] = d
    meta = {
        "task": "PM-001 crosscheck/solver blind reference cases",
        "generated": "2026-10-30",
        "generator": "crosscheck/solver/xflight.py --write-cases (fixed-step RK4, step halving to 1e-8 m, Hermite events)",
        "label_all_outputs": "predicted (model output under ASSUMED placeholder aerodynamics; not POLLEN measurements)",
        "parameters": {
            "m_kg": [base.m, "user/HANDOFF s1-2 (AndyMark nominal 0.055 lb ~ 24.95 g, first-pass 0.025); not re-verified here"],
            "R_m": [base.R, "user/HANDOFF s2 (official nominal 71 mm diameter)"],
            "rho_kg_m3": [base.rho, "assumed (ISA sea-level standard air)"],
            "Cd": [base.Cd, "ASSUMED PLACEHOLDER, constant, uncalibrated; perforated POLLEN != pickleball"],
            "c1": [base.c1, "ASSUMED PLACEHOLDER, Cl = min(c1*S, Cl_max), uncalibrated"],
            "Cl_max": [base.Cl_max, "ASSUMED PLACEHOLDER ceiling, uncalibrated"],
            "k_spin_1_s": ["0 or 0.5 per case", "ASSUMED PLACEHOLDER spin decay omega0*exp(-k t)"],
            "g_m_s2": [g, "assumed; MUST match the main solver (rerun with --g if it uses 9.80665)"],
            "wind_m_s": [[0.0, 0.0, 0.0], "assumed still air for all 24 cases"],
            "eps_v_m_s": [base.eps_v, "regularisation floor in S"],
        },
        "conventions": {
            "frame": "x toward target, y = z cross x (left), z up; release at x=0 in the x-z plane",
            "z_is": "height of ball CENTRE above tiles",
            "S0": "release spin parameter |omega0| R / |v_rel(0)|; S(t) recomputed in flight from decayed omega and current |v_rel|",
            "backspin_axis": "(0,-1,0); derived: top surface moves -x  =>  omega x z_hat = -x_hat  =>  omega || -y_hat; Magnus (-y) x (+x) = +z (up)",
            "apex": "first vz: + -> 0 crossing (Hermite on vz)",
            "z1p0 / z0p3": "LAST DESCENDING crossing of z = 1.0 m / z = release height 0.3 m; null if never reached",
            "ground_R": "descending crossing of z = R (ball bottom touches tiles); extra, for reference",
            "flight_time_s": "time of return to release height z0 = 0.3 m (NOT ground)",
            "spin_vs_nospin.equal_x": "max |z_spin(x) - z_nospin(x)| over x in [0, min of the two z0p3 x's]",
            "spin_vs_nospin.equal_t": "max |z_spin(t) - z_nospin(t)| over t in [0, min of the two flight times]",
            "signed_dz": "spin minus no-spin (positive = spin case higher)",
            "horizontal_reversal": "true if vx < 0 anywhere before return to z0 (HANDOFF s0 explicit test)",
        },
        "design": "4 launch states x 6 spin configs: (S0,k) = (0,0),(0.5,0),(1,0),(2,0),(0.5,0.5),(1,0.5). S0=0 is the no-spin twin of each launch state.",
    }
    return {"meta": meta, "cases": _round(cases)}


# --------------------------------------------------------------------------- #
# Self tests (independent of src/)
# --------------------------------------------------------------------------- #
def backspin_axis_check():
    xh, yh, zh = np.eye(3)
    surf_top = np.cross(BACKSPIN_AXIS, zh)           # surface velocity at top / (|w| R)
    assert np.allclose(surf_top, -xh), surf_top      # top moves backward => backspin
    lift = np.cross(BACKSPIN_AXIS, xh)
    assert np.allclose(lift, zh), lift               # Magnus on +x motion is +z (up)
    # and in the accel() implementation:
    p = Params(Cd=0.0, g=0.0)
    a = accel(0.0, np.array([0, 0, 0, 5.0, 0, 0]), p, 100.0, BACKSPIN_AXIS)
    assert a[2] > 0 and abs(a[0]) < 1e-12, a
    # ascent: rearward; descent: forward component
    a_up = accel(0.0, np.array([0, 0, 0, 3.0, 0, 3.0]), p, 100.0, BACKSPIN_AXIS)
    a_dn = accel(0.0, np.array([0, 0, 0, 3.0, 0, -3.0]), p, 100.0, BACKSPIN_AXIS)
    assert a_up[0] < 0 and a_dn[0] > 0 and a_up[2] > 0 and a_dn[2] > 0
    # HANDOFF scale check: 5 m/s, Cl = 0.20 -> ~0.49 m/s2
    pc = Params(Cd=0.0, g=0.0, c1=1.0, Cl_max=0.20)
    a = accel(0.0, np.array([0, 0, 0, 5.0, 0, 0]), pc, 1e4, BACKSPIN_AXIS)
    assert abs(a[2] - 0.4851) < 2e-3, a
    return True


def selftest(verbose=True):
    res = {}
    res["backspin_sign"] = backspin_axis_check()
    # regularisation at v = 0
    p = Params()
    a = accel(0.0, np.zeros(6), p, 500.0, BACKSPIN_AXIS)
    assert np.allclose(a, [0, 0, -p.g]), a
    res["v0_regularisation"] = True
    # vacuum vs closed form
    pv = Params(Cd=0.0, c1=0.0)
    L = Launch(v0=7.0, elev_deg=60.0, S0=1.0)
    out, _ = simulate(pv, L)
    vx, vz = 7 * math.cos(math.radians(60)), 7 * math.sin(math.radians(60))
    ta = vz / pv.g
    tf = 2 * vz / pv.g
    e1 = abs(out["apex"]["t"] - ta) + abs(out["apex"]["z"] - (0.3 + vz * vz / (2 * pv.g)))
    e2 = abs(out["z0p3"]["x"] - vx * tf) + abs(out["flight_time_s"] - tf)
    assert e1 < 1e-9 and e2 < 1e-9, (e1, e2)
    res["vacuum_closed_form_err"] = max(e1, e2)
    # drag-only vertical shot: apex height h = (m/2c) ln(1 + c v0^2 / (m g)), c = 0.5 rho Cd A
    pd = Params(c1=0.0)
    L = Launch(v0=9.0, elev_deg=90.0, S0=0.0)
    out, _ = simulate(pd, L)
    c = 0.5 * pd.rho * pd.Cd * pd.A
    h = pd.m / (2 * c) * math.log(1 + c * 81 / (pd.m * pd.g))
    tap = math.sqrt(pd.m / (pd.g * c)) * math.atan(9.0 * math.sqrt(c / (pd.m * pd.g)))
    e3 = abs(out["apex"]["z"] - 0.3 - h) + abs(out["apex"]["t"] - tap)
    assert e3 < 1e-8, e3
    res["drag_vertical_closed_form_err"] = e3
    # independent integrator sanity (scipy DOP853, tight tol) on one spin+decay case
    try:
        from scipy.integrate import solve_ivp
        p = Params(k_spin=0.5)
        L = Launch(v0=7.5, elev_deg=70.0, S0=2.0)
        out, (T, X, Ac) = simulate(p, L)
        w0 = omega0_mag(p, L)
        sol = solve_ivp(lambda t, s: np.concatenate((s[3:6], accel(t, s, p, w0, BACKSPIN_AXIS))),
                        (0, T[-1]), X[0], method="DOP853", rtol=1e-12, atol=1e-13, t_eval=T)
        e4 = float(np.max(np.abs(sol.y[:3].T - X[:, :3])))
        assert e4 < 1e-7, e4
        res["dop853_vs_rk4_max_pos_err_m"] = e4
    except ImportError:
        res["dop853_vs_rk4_max_pos_err_m"] = "scipy unavailable"
    if verbose:
        for k, v in res.items():
            print(f"  {k}: {v}")
        print("SELFTEST PASS")
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--write-cases", action="store_true")
    ap.add_argument("--g", type=float, default=9.81)
    ap.add_argument("--out", default=str(HERE / "reference_cases.json"))
    a = ap.parse_args(argv)
    if a.selftest or not a.write_cases:
        selftest()
    if a.write_cases:
        data = build_cases(g=a.g)
        data["meta"]["selftest"] = _round(selftest(verbose=False))
        Path(a.out).write_text(json.dumps(data, indent=1), encoding="utf-8")
        print(f"wrote {a.out} ({len(data['cases'])} cases)")


if __name__ == "__main__":
    main()
