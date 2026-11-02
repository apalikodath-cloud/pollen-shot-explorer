"""Venue air and optional drag / draft models for the planar shot (research/MISSING_EFFECTS.md build-next 1, 2, 4, 6).

Everything here is an OPTION. With the defaults the planar model is unchanged except that the still-air
reference state is now written down: 20 C, 101.325 kPa, dry air gives rho = 1.2041 kg/m^3 (derived below) instead
of the rounded 1.20 in research/params_lit.json (about 1 mm at the reference shot, derived in MISSING_EFFECTS.md
section 4 item 8). viz/explorer/physics.js carries a line-for-line copy (airState, cdOf, aeroExt); the two are
cross-checked by tests/test_air.py against tests/js_air_check.js.

Labels (HANDOFF section 5):
- air_density: formulas CONFIRMED (sources below); the venue inputs (temperature, pressure, RH) are user inputs.
- Cd models: 'const' = the ASSUMED literature Cd (params file). 'morrison' = smooth-sphere correlation (Morrison 2013,
  263000 in both places), a reference curve only, NOT a POLLEN fact. 'blend' = what-if partial drag crisis
  Cd_sub -> Cd_post between Re1 and Re2 (ASSUMED shape and values until the T1 drop/video test).
- spin drag: Cd += dCd * min(S / S_sat, 1), dCd 0 / 0.08 / 0.18 and S_sat 0.6 ASSUMED (tennis and smooth-sphere data,
  research/effects/aero.md E3). The no-spin twin has S = 0, so it never gets this term.
- draft (wind): constant per shot in the shot plane, w = (along-shot, vertical) m/s, user input. Drag, Magnus and S use
  v_rel = v - w (HANDOFF 4A, src/flight.py does the same in 3D).
- grip_limited: HOOD_V_MAX 8.9 m/s is PREDICTED (docs/04_launcher.md); a shot above it is flagged, not removed.
"""
from __future__ import annotations

import math

import numpy as np

# --------------------------------------------------------------------------- air state
#: dry-air gas constant J/(kg K) (CIPM-2007 simplified form, Picard et al. 2008, Metrologia 45, 149)
R_DRY = 287.06
#: sea-level standard pressure, Pa (US Standard Atmosphere 1976)
P0 = 101325.0
#: still-air reference state (derived): 20 C, 101.325 kPa, RH 0
STILL_AIR = {"t_c": 20.0, "p_pa": P0, "rh": 0.0}


def pressure_from_altitude(alt_m: float) -> float:
    """Pa. p = 101325 (1 - 2.25577e-5 h)^5.25588 (US Standard Atmosphere, NASA-TM-X-74335). Prefer a logged
    station pressure when one exists."""
    return P0 * (1.0 - 2.25577e-5 * alt_m) ** 5.25588


def vapour_pressure(t_c: float, rh: float) -> float:
    """Pa, rh in 0..1. Magnus form e_s = 611.2 exp(17.62 t / (243.12 + t)) (WMO-No. 8 2018 annex 4.B)."""
    return rh * 611.2 * math.exp(17.62 * t_c / (243.12 + t_c))


def air_density(t_c: float = 20.0, p_pa: float = P0, rh: float = 0.0) -> float:
    """kg/m^3. rho = (p - 0.378 e) / (R_d T) (simplified CIPM-2007)."""
    T = t_c + 273.15
    return (p_pa - 0.378 * vapour_pressure(t_c, rh)) / (R_DRY * T)


def air_viscosity(t_c: float = 20.0) -> float:
    """Pa s, Sutherland: mu = 1.716e-5 (T/273.15)^1.5 (273.15 + 110.4) / (T + 110.4)."""
    T = t_c + 273.15
    return 1.716e-5 * (T / 273.15) ** 1.5 * (273.15 + 110.4) / (T + 110.4)


def air_state(t_c: float = 20.0, p_pa: float = P0, rh: float = 0.0) -> dict:
    """{'rho', 'nu', 'mu', ...} for a venue. Default = the still-air reference (rho 1.2041 kg/m^3, nu 1.506e-5 m^2/s; derived)."""
    rho = air_density(t_c, p_pa, rh)
    mu = air_viscosity(t_c)
    return {"rho": rho, "mu": mu, "nu": mu / rho, "t_c": t_c, "p_pa": p_pa, "rh": rh}


STILL_AIR_RHO = air_density(**STILL_AIR)          # 1.20410 kg/m^3 (derived)

# --------------------------------------------------------------------------- drag models
CD_MODELS = ("const", "morrison", "blend")
#: what-if partial crisis (aero.md E2): 0.48 -> 0.33 between Re 3e4 and 5e4; Cd_sub defaults to the params Cd
BLEND_DEFAULT = {"cd_post": 0.33, "re1": 3.0e4, "re2": 5.0e4}
SPIN_DRAG_SETS = (0.0, 0.08, 0.18)
S_SAT_DEFAULT = 0.6


def morrison_cd(re: float) -> float:
    """Smooth-sphere Cd(Re) (float or array), Morrison 2013 eq. 4 with 263000 in both places (reference curve, not POLLEN)."""
    re = np.maximum(re, 1e-6)
    a = re / 5.0
    b = re / 263000.0
    c = re / 1.0e6
    return (24.0 / re + 2.6 * a / (1.0 + a ** 1.52) + 0.411 * b ** -7.94 / (1.0 + b ** -8.0)
            + 0.25 * c / (1.0 + c))


def smoothstep(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def cd_base(prm: dict, re: float) -> float:
    """Cd without the spin term for prm['cd_model'] (default 'const' = prm['Cd'])."""
    model = prm.get("cd_model", "const") or "const"
    if model == "const":
        return prm["Cd"]
    if model == "morrison":
        return morrison_cd(re)
    if model == "blend":
        sub = prm.get("cd_sub", prm["Cd"])
        post = prm.get("cd_post", BLEND_DEFAULT["cd_post"])
        r1 = prm.get("re1", BLEND_DEFAULT["re1"])
        r2 = prm.get("re2", BLEND_DEFAULT["re2"])
        return sub + (post - sub) * smoothstep((re - r1) / (r2 - r1))
    raise ValueError("unknown cd_model %r" % model)


# --------------------------------------------------------------------------- lift options (MISSING_EFFECTS.md 2d)
#: reverse-Magnus region (ASSUMED, Kim 2014 / Kray 2012 smooth-sphere data; not a POLLEN measurement):
#: Cl blends toward -cl_rev when Re < 4.6e4 AND S < 0.5 (10 % smoothstep ramps on both edges)
REV_RE = 4.6e4
REV_S = 0.5


def cl_table_of(table, S):
    """User Cl(S) points (S ascending): linear between points, flat after the last point, straight to (0, 0)
    before the first point when it is at S > 0. Works on floats and arrays."""
    t = np.asarray(table, dtype=float).reshape(-1, 2)
    s, c = t[:, 0], t[:, 1]
    if s[0] > 0:
        s, c = np.concatenate(([0.0], s)), np.concatenate(([0.0], c))
    out = np.interp(np.maximum(S, 0.0), s, c)
    return float(out) if np.ndim(out) == 0 else out


def cl_of(prm: dict, S, re, cl=None):
    """Lift coefficient at spin ratio S and Reynolds number re (float or array): prm['cl_table'] if given, else
    min(c1 S, clmax) from prm['Cl'] = (c1, clmax) (or the given cl), then the optional reverse-Magnus blend
    (prm['cl_rev'], default 0 = off). Same as physics.js clOf."""
    tab = prm.get("cl_table")
    if tab is not None and len(tab):
        out = cl_table_of(tab, S)
    else:
        c1, clmax = cl if cl is not None else prm["Cl"]
        out = np.minimum(c1 * S, clmax)
    cr = float(prm.get("cl_rev", 0.0) or 0.0)
    if cr != 0.0:
        r0 = float(prm.get("re_rev", REV_RE) or REV_RE)
        s0 = float(prm.get("s_rev", REV_S) or REV_S)
        b = smoothstep((r0 - re) / (0.1 * r0)) * smoothstep((s0 - S) / (0.1 * s0))
        out = (1.0 - b) * out - b * cr * np.minimum(S / 0.1, 1.0)
    return out


def lift_on(prm: dict) -> bool:
    c = prm.get("Cl") or (0.0, 0.0)
    tab = prm.get("cl_table")
    return c[0] > 0 or (tab is not None and len(tab) > 0) or float(prm.get("cl_rev", 0.0) or 0.0) != 0.0


# --------------------------------------------------------------------------- effective (added) mass (2e)
def eps_from_phi(phi: float, rho: float, mass: float, radius: float) -> float:
    """Added-mass ratio eps = (0.5 + phi) rho V / m (phi 0..1 ASSUMED unsteady-wake extra; 0.5 = potential-flow
    sphere). dv/dt = (F_aero/m + g) / (1 + eps); no separate buoyancy term. About 0.0045 to 0.0135 for POLLEN."""
    return (0.5 + phi) * rho * (4.0 / 3.0) * math.pi * radius ** 3 / mass


def has_ext(prm: dict) -> bool:
    """True when any optional term is on (else the plain constant-Cd still-air path is used)."""
    w = prm.get("wind") or (0.0, 0.0)
    tab = prm.get("cl_table")
    return ((prm.get("cd_model", "const") or "const") != "const" or float(prm.get("dcd_spin", 0.0) or 0.0) != 0.0
            or float(w[0]) != 0.0 or float(w[1]) != 0.0 or (tab is not None and len(tab) > 0)
            or float(prm.get("cl_rev", 0.0) or 0.0) != 0.0 or float(prm.get("eps_mass", 0.0) or 0.0) != 0.0)


# --------------------------------------------------------------------------- grip-limited flag
#: PREDICTED grip-limited hood exit-speed cap (docs/04_launcher.md; same value as feasibility.HOOD_V_MAX)
HOOD_V_MAX = 8.9


def grip_limited(v: float, vmax: float = HOOD_V_MAX) -> bool:
    """True when the required exit speed is above the PREDICTED hood cap: v/u and S there are uncertain, and a
    'possible' answer must not rest on such a shot (MISSING_EFFECTS.md build-next 6)."""
    return v > vmax + 1e-9
