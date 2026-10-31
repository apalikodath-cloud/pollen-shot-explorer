"""Free-flight solver for POLLEN with drag, Magnus lift, spin decay and wind.

HANDOFF section 4A / 4B; API contract: docs/INTERFACES.md ("src/flight.py").

Frame: x horizontal toward the target, y sideways, z up (SI units: m, s, kg, rad).
2D shots use y = 0 and omega along +/-y.

Equations of motion (v_rel = v - v_wind):
    m dv/dt = m g + F_drag + F_Magnus
    F_drag   = -0.5 rho Cd A |v_rel| v_rel
    F_Magnus =  0.5 rho Cl A |v_rel|^2 n_M,   n_M = unit(omega x v_rel)
    A = pi R^2,  S = |omega| R / |v_rel|,  Re = |v_rel| 2R / nu
    d omega/dt = -k_spin omega           (optional exponential spin decay)

Regularisation (no fictitious force as |v_rel| -> 0):
    S   = |omega| R / sqrt(|v_rel|^2 + eps_v^2)
    n_M = (omega x v_rel) / sqrt(|omega x v_rel|^2 + (eps_v |omega|)^2)
Both aero forces carry a |v_rel|^2 factor (Cl is bounded or grows at most like S),
so they vanish smoothly at |v_rel| = 0. eps_v defaults to 1e-6 m/s, which changes
nothing measurable for |v_rel| >~ 1e-3 m/s.

Backspin convention (unit-tested): ball moving +x, backspin omega points -y, so
omega x v points +z. ``backspin_omega(v_dir, spin)`` builds this vector for any
non-vertical direction.

All default aerodynamic coefficients are UNCALIBRATED placeholders (perforated
POLLEN is not a pickleball). See ``FALLBACK_PROVENANCE``.
"""
from __future__ import annotations

import inspect
import json
import math
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Sequence

import numpy as np
from scipy.integrate import solve_ivp

if __package__ in (None, ""):
    import air  # type: ignore
else:
    from . import air

__all__ = [
    "G_STANDARD", "NU_AIR_DEFAULT", "FALLBACK_PARAMS", "FALLBACK_PROVENANCE",
    "AERO_PARAMS_PATH", "LIT_PARAMS_PATH", "set_aero_path", "aero_tag", "load_params", "default_params", "cl_linear_capped",
    "backspin_omega", "aero_forces", "simulate", "Trajectory", "plane_event",
    "horizontal_reversal", "compare_spin",
]

# --------------------------------------------------------------------------- constants
#: confirmed: standard acceleration of gravity, 9.80665 m/s^2 (3rd CGPM 1901; NIST SP 330
#: https://physics.nist.gov/cuu/Constants/ "standard acceleration of gravity").
G_STANDARD = 9.80665
#: assumed: kinematic viscosity of air near 20 C, ~1.5e-5 m^2/s (derived mu/rho with
#: mu ~1.81e-5 Pa s, rho 1.204-1.225 kg/m^3 gives 1.48e-5..1.50e-5). Used only for Re.
NU_AIR_DEFAULT = 1.5e-5
#: assumed numerical regularisation speed for |v_rel| -> 0 (m/s).
EPS_V_DEFAULT = 1e-6

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#: Shared aerodynamic parameter file (written by another agent; see INTERFACES.md).
#: PM001_AERO_PATH (set by ``set_aero_path``) overrides it; spawned worker processes inherit
#: the environment, so a pool started after ``set_aero_path`` reads the same file.
AERO_PARAMS_PATH = os.environ.get("PM001_AERO_PATH") or os.path.join(_ROOT, "data", "aero_params.json")
#: Literature-graded ranges (research synthesis 2026-10-30); the default for new runs (DECISIONS).
LIT_PARAMS_PATH = os.path.join(_ROOT, "research", "params_lit.json")


def set_aero_path(path: str) -> str:
    """Point every later aero read (this process and child processes) at ``path``."""
    global AERO_PARAMS_PATH
    AERO_PARAMS_PATH = os.path.abspath(path)
    os.environ["PM001_AERO_PATH"] = AERO_PARAMS_PATH
    return AERO_PARAMS_PATH


def aero_tag() -> str:
    """Short name of the active aero file, for cache directories ('params_lit', 'aero_params')."""
    return os.path.splitext(os.path.basename(AERO_PARAMS_PATH))[0]

#: Fallback nominal parameters when data/aero_params.json is absent (HANDOFF 4A nominal).
FALLBACK_PARAMS: dict[str, Any] = {
    "rho": 1.2041,           # kg/m^3, still air 20 C / 101.325 kPa / dry (derived, src/air.py)
    "mass": 0.025,           # kg
    "radius": 0.0355,        # m
    "Cd": 0.5,               # -
    "Cl": (0.25, 0.4),       # (c1, Cl_max): Cl = min(c1*S, Cl_max)
    "spin_decay_k": 0.0,     # 1/s
    "g": G_STANDARD,
    "nu": NU_AIR_DEFAULT,
}

FALLBACK_PROVENANCE: dict[str, str] = {
    "rho": "derived: still air 20 C, 101.325 kPa, dry -> 1.2041 kg/m^3 (src/air.py, simplified CIPM-2007; "
           "was ISA 15 C 1.225); venue air density varies ~1.15-1.23 with altitude/temperature (src/air.py "
           "air_state).",
    "mass": "user/confirmed-vendor: HANDOFF section 1 cites AndyMark am-5851_yellow at 0.055 lb "
            "(~24.95 g); 0.025 kg first-pass value; weigh real balls.",
    "radius": "confirmed nominal: 2.8 in (7.1 cm) diameter per BIOBUZZ manual TU07 / HANDOFF "
              "section 1-2 (0.0355 m); actual pieces vary and are not perfectly spherical.",
    "Cd": "assumed PLACEHOLDER: 0.5 (HANDOFF 4A nominal); uncalibrated for perforated POLLEN.",
    "Cl": "assumed PLACEHOLDER: Cl = min(0.25*S, 0.4). c1=0.25 is the task-brief placeholder; "
          "Cl_max=0.4 is an arbitrary ceiling (no POLLEN source). Uncalibrated; pickleball "
          "data are not POLLEN measurements.",
    "spin_decay_k": "assumed PLACEHOLDER: 0 1/s (no decay). This is the OPTIMISTIC bound for "
                    "spin effects; real decay is unmeasured.",
    "g": "confirmed: standard gravity 9.80665 m/s^2 (CGPM 1901 / NIST).",
    "nu": "assumed: 1.5e-5 m^2/s air near 20 C.",
}


# --------------------------------------------------------------------------- parameters
def cl_linear_capped(c1: float, cl_max: float) -> Callable[[float], float]:
    """Return Cl(S) = min(c1*S, Cl_max) for S >= 0 (labelled uncalibrated)."""
    c1 = float(c1)
    cl_max = float(cl_max)

    def cl(S: float) -> float:
        v = c1 * S
        return v if v < cl_max else cl_max

    cl.c1 = c1  # type: ignore[attr-defined]
    cl.cl_max = cl_max  # type: ignore[attr-defined]
    return cl


def _pick(entry: Any, which: str) -> Any:
    """Pick a value from an aero_params.json entry ({value}, {nominal/low/high} or scalar)."""
    if not isinstance(entry, dict):
        return entry
    if which in entry and entry[which] is not None:
        return entry[which]
    for key in ("value", "nominal"):
        if key in entry and entry[key] is not None:
            return entry[key]
    raise KeyError(f"no '{which}'/'value'/'nominal' in entry {entry!r}")


def load_params(path: Optional[str] = None, which: Any = "nominal") -> dict[str, Any]:
    """Load a flat ``params`` dict from data/aero_params.json (INTERFACES.md layout).

    which: "low" | "nominal" | "high" applied to Cd, Cl set and spin_decay_k, or a dict
    such as {"Cd": "high", "Cl": "low", "spin_decay_k": "nominal"}.
    Missing file -> FileNotFoundError (use ``default_params`` for the fallback).
    The returned dict carries "prov" (per-key provenance strings) and "source".
    """
    path = path or AERO_PARAMS_PATH
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    sel = {"Cd": which, "Cl": which, "spin_decay_k": which} if isinstance(which, str) else {
        "Cd": "nominal", "Cl": "nominal", "spin_decay_k": "nominal", **which}

    p: dict[str, Any] = {"g": G_STANDARD, "nu": NU_AIR_DEFAULT}
    prov: dict[str, str] = {}
    for key in ("rho", "mass", "radius"):
        p[key] = float(_pick(raw[key], "value"))
        prov[key] = str(raw[key].get("prov", "")) if isinstance(raw[key], dict) else ""
    p["Cd"] = float(_pick(raw["Cd"], sel["Cd"]))
    prov["Cd"] = f"{sel['Cd']}: " + str(raw["Cd"].get("prov", "") if isinstance(raw["Cd"], dict) else "")
    cl = raw.get("Cl")
    if cl is None:
        p["Cl"] = None
    elif isinstance(cl, dict) and "sets" in cl:
        s = cl["sets"][sel["Cl"]]
        p["Cl"] = (float(s["c1"]), float(s["Cl_max"]))
        prov["Cl"] = f"{sel['Cl']}: " + str(cl.get("prov", ""))
    elif isinstance(cl, dict) and "c1" in cl:
        p["Cl"] = (float(cl["c1"]), float(cl["Cl_max"]))
        prov["Cl"] = str(cl.get("prov", ""))
    else:
        p["Cl"] = float(_pick(cl, sel["Cl"]))
    if "spin_decay_k" in raw:
        p["spin_decay_k"] = float(_pick(raw["spin_decay_k"], sel["spin_decay_k"]))
        sk = raw["spin_decay_k"]
        prov["spin_decay_k"] = f"{sel['spin_decay_k']}: " + str(sk.get("prov", "") if isinstance(sk, dict) else "")
    else:
        p["spin_decay_k"] = 0.0
        prov["spin_decay_k"] = FALLBACK_PROVENANCE["spin_decay_k"]
    if "I_b" in raw:
        p["I_b"] = float(_pick(raw["I_b"], "value"))
        prov["I_b"] = str(raw["I_b"].get("prov", "")) if isinstance(raw["I_b"], dict) else ""
    for key in ("nu", "g"):
        if key in raw:
            p[key] = float(_pick(raw[key], "value"))
    p["prov"] = prov
    p["source"] = os.path.abspath(path)
    return p


def default_params(which: Any = "nominal", path: Optional[str] = None) -> dict[str, Any]:
    """data/aero_params.json if present (and parseable), else the HANDOFF fallback nominal."""
    path = path or AERO_PARAMS_PATH
    if os.path.exists(path):
        try:
            return load_params(path, which)
        except (KeyError, ValueError, TypeError, json.JSONDecodeError):
            pass
    p = dict(FALLBACK_PARAMS)
    p["prov"] = dict(FALLBACK_PROVENANCE)
    p["source"] = "fallback (HANDOFF 4A nominal placeholders)"
    return p


def _n_positional(fn: Callable) -> int:
    try:
        sig = inspect.signature(fn)
    except (TypeError, ValueError):
        return 1
    n = 0
    for prm in sig.parameters.values():
        if prm.kind == prm.VAR_POSITIONAL:
            return 99
        if prm.kind in (prm.POSITIONAL_ONLY, prm.POSITIONAL_OR_KEYWORD):
            n += 1
    return n


@dataclass
class _Prep:
    rho: float
    mass: float
    radius: float
    area: float
    g: float
    nu: float
    eps_v: float
    k_spin: float
    cd_const: Optional[float]
    cd_fn: Optional[Callable[[float, float], float]]
    cl_fn: Optional[Callable[[float, float], float]]
    s_perp: bool = False       # gyro-correct spin ratio S_perp = |w x v| R / |v|^2 (MISSING_EFFECTS.md 2c)
    inv_eps: float = 1.0       # 1 / (1 + eps_mass), effective (added) mass (2e)


def _prepare(params: dict[str, Any]) -> _Prep:
    for key in ("rho", "mass", "radius", "Cd"):
        if key not in params:
            raise KeyError(f"params missing required key '{key}'")
    R = float(params["radius"])
    cd = params["Cd"]
    cd_const = cd_fn = None
    if callable(cd):
        if _n_positional(cd) >= 2:
            cd_fn = lambda Re, S, f=cd: float(f(Re, S))  # noqa: E731
        else:
            cd_fn = lambda Re, S, f=cd: float(f(Re))  # noqa: E731
    else:
        cd_const = float(cd)
    cl = params.get("Cl")
    cl_fn = None
    if cl is None:
        cl_fn = None
    elif callable(cl):
        if _n_positional(cl) >= 2:
            cl_fn = lambda S, Re, f=cl: float(f(S, Re))  # noqa: E731
        else:
            cl_fn = lambda S, Re, f=cl: float(f(S))  # noqa: E731
    elif isinstance(cl, dict):
        f = cl_linear_capped(cl["c1"], cl["Cl_max"])
        cl_fn = lambda S, Re, f=f: f(S)  # noqa: E731
    elif isinstance(cl, (tuple, list)) and len(cl) == 2:
        f = cl_linear_capped(cl[0], cl[1])
        cl_fn = lambda S, Re, f=f: f(S)  # noqa: E731
    else:
        c = float(cl)
        cl_fn = None if c == 0.0 else (lambda S, Re, c=c: c)
    # optional lift terms (src/air.py cl_of; default off): user Cl(S) table replaces Cl, reverse-Magnus blend
    tab = params.get("cl_table")
    if tab is not None and len(tab):
        tab = [tuple(map(float, r)) for r in tab]
        cl_fn = lambda S, Re, t=tab: float(air.cl_table_of(t, S))  # noqa: E731
    cl_rev = float(params.get("cl_rev", 0.0) or 0.0)
    if cl_rev != 0.0:
        base = cl_fn
        rp = {"cl_rev": cl_rev, "re_rev": params.get("re_rev") or air.REV_RE, "s_rev": params.get("s_rev") or air.REV_S}
        # same blend as air.cl_of: (1 - b) Cl - b cl_rev min(S/0.1, 1), b = ramps below Re_rev and S_rev
        def cl_fn(S, Re, base=base, rp=rp):  # noqa: E306
            b0 = 0.0 if base is None else base(S, Re)
            r0, s0 = float(rp["re_rev"]), float(rp["s_rev"])
            b = float(air.smoothstep((r0 - Re) / (0.1 * r0)) * air.smoothstep((s0 - S) / (0.1 * s0)))
            return (1.0 - b) * b0 - b * rp["cl_rev"] * min(S / 0.1, 1.0)
    eps_mass = float(params.get("eps_mass", 0.0) or 0.0)
    return _Prep(
        rho=float(params["rho"]), mass=float(params["mass"]), radius=R, area=math.pi * R * R,
        g=float(params.get("g", G_STANDARD)), nu=float(params.get("nu", NU_AIR_DEFAULT)),
        eps_v=float(params.get("eps_v", EPS_V_DEFAULT)),
        k_spin=float(params.get("spin_decay_k", 0.0) or 0.0),
        cd_const=cd_const, cd_fn=cd_fn, cl_fn=cl_fn, s_perp=bool(params.get("s_perp", False)),
        inv_eps=1.0 / (1.0 + eps_mass))


# --------------------------------------------------------------------------- physics core
def backspin_omega(v_dir: Sequence[float], spin_rad_s: float) -> np.ndarray:
    """Backspin vector for a ball travelling along ``v_dir``.

    omega = spin * unit(v_dir x z_hat): horizontal axis perpendicular to the vertical
    plane of motion, oriented so omega x v has a +z component. +x travel -> -y axis;
    -x travel -> +y axis. Negative ``spin_rad_s`` gives topspin. Raises for vertical v_dir.
    """
    v = np.asarray(v_dir, dtype=float)
    axis = np.cross(v, np.array([0.0, 0.0, 1.0]))
    n = np.linalg.norm(axis)
    if n < 1e-12 * max(np.linalg.norm(v), 1e-300):
        raise ValueError("backspin axis undefined for a vertical (or zero) direction")
    return float(spin_rad_s) * axis / n


def _aero(p: _Prep, vx: float, vy: float, vz: float, wx: float, wy: float, wz: float):
    """Return (Fdx, Fdy, Fdz, Fmx, Fmy, Fmz, S, Re, Cd, Cl) for relative velocity v."""
    v2 = vx * vx + vy * vy + vz * vz
    vmag = math.sqrt(v2)
    q = 0.5 * p.rho * p.area
    Re = vmag * 2.0 * p.radius / p.nu
    wmag = math.sqrt(wx * wx + wy * wy + wz * wz)
    if p.s_perp:   # gyro-correct: only the spin component perpendicular to v makes lift (= S for pure backspin)
        cx = wy * vz - wz * vy
        cy = wz * vx - wx * vz
        cz = wx * vy - wy * vx
        S = math.sqrt(cx * cx + cy * cy + cz * cz) * p.radius / (v2 + p.eps_v * p.eps_v)
    else:
        S = wmag * p.radius / math.sqrt(v2 + p.eps_v * p.eps_v)
    cd = p.cd_const if p.cd_fn is None else p.cd_fn(Re, S)
    kd = -q * cd * vmag
    fdx, fdy, fdz = kd * vx, kd * vy, kd * vz
    fmx = fmy = fmz = 0.0
    cl = 0.0
    if p.cl_fn is not None and wmag > 0.0 and v2 > 0.0:
        cl = p.cl_fn(S, Re)
        cx = wy * vz - wz * vy
        cy = wz * vx - wx * vz
        cz = wx * vy - wy * vx
        den = math.sqrt(cx * cx + cy * cy + cz * cz + (p.eps_v * wmag) ** 2)
        if den > 0.0:
            km = q * cl * v2 / den
            fmx, fmy, fmz = km * cx, km * cy, km * cz
    return fdx, fdy, fdz, fmx, fmy, fmz, S, Re, cd, cl


def _wind_fn(wind):
    if callable(wind):
        return lambda t, pos: np.asarray(wind(t, pos), dtype=float)
    w = np.asarray(wind, dtype=float).reshape(3)
    return lambda t, pos: w


def aero_forces(vel: Sequence[float], omega: Sequence[float], params: dict[str, Any],
                wind: Sequence[float] = (0.0, 0.0, 0.0)) -> dict[str, Any]:
    """Aerodynamic forces (N) on the ball for absolute velocity ``vel`` and spin ``omega``.

    Returns {"F_drag", "F_magnus" (3-arrays), "S", "Re", "Cd", "Cl", "v_rel"}.
    """
    p = params if isinstance(params, _Prep) else _prepare(params)
    vr = np.asarray(vel, dtype=float) - np.asarray(wind, dtype=float)
    w = np.asarray(omega, dtype=float)
    r = _aero(p, vr[0], vr[1], vr[2], w[0], w[1], w[2])
    return {"F_drag": np.array(r[0:3]), "F_magnus": np.array(r[3:6]), "S": r[6], "Re": r[7],
            "Cd": r[8], "Cl": r[9], "v_rel": vr}


def _make_rhs(p: _Prep, wind_fn, wind_const: Optional[np.ndarray]):
    inv_m = 1.0 / p.mass
    g = p.g
    k = p.k_spin
    ie = p.inv_eps            # effective mass: dv/dt = (F/m + g) / (1 + eps), no separate buoyancy term

    def rhs(t, y):
        if wind_const is None:
            w = wind_fn(t, y[0:3])
            ux, uy, uz = float(w[0]), float(w[1]), float(w[2])
        else:
            ux, uy, uz = wind_const
        vx, vy, vz = y[3], y[4], y[5]
        wx, wy, wz = y[6], y[7], y[8]
        f = _aero(p, vx - ux, vy - uy, vz - uz, wx, wy, wz)
        return [vx, vy, vz,
                (f[0] + f[3]) * inv_m * ie, (f[1] + f[4]) * inv_m * ie, ((f[2] + f[5]) * inv_m - g) * ie,
                -k * wx, -k * wy, -k * wz]

    return rhs


# --------------------------------------------------------------------------- events
def plane_event(point: Sequence[float], normal: Sequence[float], direction: int = 0,
                terminal: bool = True) -> Callable:
    """Stop event for the ball centre crossing a plane: (pos - point) . normal = 0.

    direction +1: crossing toward +normal; -1: toward -normal; 0: either.
    Example: plane_event((1.2, 0, 0), (1, 0, 0), +1) stops at x = 1.2 travelling +x.
    """
    p0 = np.asarray(point, dtype=float)
    n = np.asarray(normal, dtype=float)

    def ev(t, state):
        return float(np.dot(np.asarray(state[0:3]) - p0, n))

    ev.terminal = terminal  # type: ignore[attr-defined]
    ev.direction = direction  # type: ignore[attr-defined]
    return ev


def _wrap_event(fn: Callable, default_terminal: bool = True) -> Callable:
    def ev(t, y):
        return float(fn(t, y))

    ev.terminal = bool(getattr(fn, "terminal", default_terminal))
    ev.direction = float(getattr(fn, "direction", 0))
    return ev


# --------------------------------------------------------------------------- trajectory
@dataclass
class Trajectory:
    """Integrated free-flight path. Arrays: t (N,), pos/vel/omega (N, 3).

    events: {"apex": [...], "ground": [...], "stop0": [...], ...}; each item is a dict
    with t, pos, vel, omega. termination: "ground" | "stopK" | "t_max" | "failed: ...".
    """
    t: np.ndarray
    pos: np.ndarray
    vel: np.ndarray
    omega: np.ndarray
    params: dict[str, Any]
    wind: Any
    events: dict[str, list] = field(default_factory=dict)
    termination: str = ""
    sol: Any = None
    _p: Any = None

    # ---- basic accessors
    @property
    def x(self) -> np.ndarray:
        return self.pos[:, 0]

    @property
    def z(self) -> np.ndarray:
        return self.pos[:, 2]

    @property
    def speed(self) -> np.ndarray:
        return np.linalg.norm(self.vel, axis=1)

    def _wind_at(self, t, pos) -> np.ndarray:
        return np.asarray(_wind_fn(self.wind)(t, pos), dtype=float)

    def _forces_state(self, t, pos, vel, omega) -> dict[str, Any]:
        return aero_forces(vel, omega, self._p, self._wind_at(t, pos))

    def forces(self, i: int) -> dict[str, Any]:
        """Aero force breakdown at sample i (see ``aero_forces``)."""
        return self._forces_state(self.t[i], self.pos[i], self.vel[i], self.omega[i])

    def magnus_force(self, i: int) -> np.ndarray:
        """Magnus force vector (N) at sample i."""
        return self.forces(i)["F_magnus"]

    def drag_force(self, i: int) -> np.ndarray:
        """Drag force vector (N) at sample i."""
        return self.forces(i)["F_drag"]

    def state_at(self, t: float) -> dict[str, Any]:
        """Dense-output state at time t (within the integrated span)."""
        y = self.sol(t) if self.sol is not None else np.array(
            [np.interp(t, self.t, c) for c in np.hstack([self.pos, self.vel, self.omega]).T])
        return self._describe(float(t), y[0:3], y[3:6], y[6:9])

    def _describe(self, t, pos, vel, omega) -> dict[str, Any]:
        f = self._forces_state(t, pos, vel, omega)
        pos = np.asarray(pos, float)
        vel = np.asarray(vel, float)
        omega = np.asarray(omega, float)
        return {
            "t": t, "pos": pos, "vel": vel, "omega": omega,
            "x": float(pos[0]), "y": float(pos[1]), "z": float(pos[2]),
            "vx": float(vel[0]), "vy": float(vel[1]), "vz": float(vel[2]),
            "speed": float(np.linalg.norm(vel)), "omega_mag": float(np.linalg.norm(omega)),
            "spin_rpm": float(np.linalg.norm(omega) * 60.0 / (2.0 * math.pi)),
            "S": f["S"], "Re": f["Re"], "Cd": f["Cd"], "Cl": f["Cl"],
            "F_M": f["F_magnus"], "F_D": f["F_drag"],
            "F_M_mag": float(np.linalg.norm(f["F_magnus"])),
            "a_M": f["F_magnus"] / self._p.mass,
        }

    def apex(self) -> Optional[dict[str, Any]]:
        """State at the first vz: + -> - crossing (vz ~ 0; vx generally nonzero), or None.

        Keys: t, pos, vel, omega, x, y, z, vx, vy, vz, speed, omega_mag, spin_rpm, S, Re,
        Cd, Cl, F_M (vector N), F_D, F_M_mag, a_M (Magnus acceleration vector m/s^2).
        """
        ev = self.events.get("apex") or []
        if not ev:
            return None
        e = ev[0]
        return self._describe(e["t"], e["pos"], e["vel"], e["omega"])

    def horizontal_reversal(self, tol: float = 1e-9) -> bool:
        """True iff the horizontal velocity ever reverses relative to its initial direction."""
        return horizontal_reversal(self, tol=tol)

    def downrange(self) -> np.ndarray:
        """Signed horizontal distance along the initial horizontal direction of travel."""
        h = _initial_horizontal_dir(self.vel[0])
        return (self.pos[:, 0:2] - self.pos[0, 0:2]) @ h

    def end_state(self) -> dict[str, Any]:
        return self._describe(self.t[-1], self.pos[-1], self.vel[-1], self.omega[-1])


def _initial_horizontal_dir(v0) -> np.ndarray:
    h = np.asarray(v0, float)[0:2]
    n = np.linalg.norm(h)
    if n == 0.0:
        return np.array([1.0, 0.0])
    return h / n


def horizontal_reversal(traj: Trajectory, tol: float = 1e-9) -> bool:
    """Does the horizontal velocity ever change sign w.r.t. the launch direction?

    Projects (vx, vy) on the initial horizontal direction of travel and reports True only
    if that component drops below -tol (genuine mid-air reversal). Reduced horizontal
    progress, a different apex or a steep descent are NOT reversal.
    """
    h = _initial_horizontal_dir(traj.vel[0])
    along = traj.vel[:, 0:2] @ h
    if np.any(along < -tol):
        return True
    # also check event states (apex/stop) which may lie between samples
    for evs in traj.events.values():
        for e in evs:
            if float(np.dot(np.asarray(e["vel"])[0:2], h)) < -tol:
                return True
    return False


# --------------------------------------------------------------------------- solver
def simulate(x0: Sequence[float], v0: Sequence[float], omega0: Sequence[float],
             params: dict[str, Any], wind: Any = (0.0, 0.0, 0.0), t_max: float = 3.0,
             dt_max: float = 1e-3, stop: Any = None, *, z_ground: Optional[float] = 0.0,
             method: str = "RK45", rtol: float = 1e-9, atol: float = 1e-11,
             dense: bool = True) -> Trajectory:
    """Integrate free flight from position x0 with velocity v0 and spin omega0 (3-vectors).

    params: dict with rho, mass, radius, Cd (float or callable Cd(Re) / Cd(Re, S)),
        Cl (callable Cl(S) / Cl(S, Re), (c1, Cl_max) linear_capped, {"c1","Cl_max"},
        a constant, or None for no Magnus), spin_decay_k (1/s, default 0), optional g, nu,
        eps_v. Extra keys (prov, source, I_b) are ignored.
    wind: constant 3-vector (m/s) or callable wind(t, pos) -> 3-vector.
    stop: optional event callable f(t, state9) -> float (state = pos, vel, omega) or a list
        of them; honours .terminal (default True) and .direction attributes. See
        ``plane_event``.
    z_ground: terminal event when z crosses this height downward (None disables).
    Integrates with scipy solve_ivp (``method`` RK45 or DOP853), max_step = dt_max.
    """
    p = _prepare(params)
    x0 = np.asarray(x0, dtype=float).reshape(3)
    v0 = np.asarray(v0, dtype=float).reshape(3)
    w0 = np.asarray(omega0, dtype=float).reshape(3)
    if callable(wind):
        rhs = _make_rhs(p, _wind_fn(wind), None)
    else:
        wc = np.asarray(wind, dtype=float).reshape(3)
        rhs = _make_rhs(p, None, (float(wc[0]), float(wc[1]), float(wc[2])))

    def ev_apex(t, y):
        return y[5]

    ev_apex.terminal = False
    ev_apex.direction = -1.0
    events = [ev_apex]
    names = ["apex"]
    if z_ground is not None:
        zg = float(z_ground)

        def ev_ground(t, y):
            return y[2] - zg

        ev_ground.terminal = True
        ev_ground.direction = -1.0
        events.append(ev_ground)
        names.append("ground")
    if stop is not None:
        stops = stop if isinstance(stop, (list, tuple)) else [stop]
        for k, fn in enumerate(stops):
            events.append(_wrap_event(fn))
            names.append(f"stop{k}")

    y0 = np.concatenate([x0, v0, w0])
    sol = solve_ivp(rhs, (0.0, float(t_max)), y0, method=method, events=events,
                    max_step=float(dt_max), rtol=rtol, atol=atol, dense_output=dense)
    ev_out: dict[str, list] = {}
    for name, te, ye in zip(names, sol.t_events, sol.y_events):
        ev_out[name] = [{"t": float(tt), "pos": yy[0:3].copy(), "vel": yy[3:6].copy(),
                         "omega": yy[6:9].copy()} for tt, yy in zip(te, ye)]
    if sol.status == 1:
        term = "t_max"
        for name, ev in zip(names, events):
            if getattr(ev, "terminal", False) and ev_out[name] and \
                    abs(ev_out[name][-1]["t"] - sol.t[-1]) <= 1e-12 * max(1.0, sol.t[-1]):
                term = name
                break
    elif sol.status == 0:
        term = "t_max"
    else:
        term = f"failed: {sol.message}"
    Y = sol.y.T
    return Trajectory(t=sol.t.copy(), pos=Y[:, 0:3].copy(), vel=Y[:, 3:6].copy(),
                      omega=Y[:, 6:9].copy(), params=params, wind=wind, events=ev_out,
                      termination=term, sol=sol.sol, _p=p)


# --------------------------------------------------------------------------- spin comparison
def _spin_vector(v0, spin) -> np.ndarray:
    if np.ndim(spin) == 0:
        if float(spin) == 0.0:
            return np.zeros(3)
        return backspin_omega(v0, float(spin))
    return np.asarray(spin, dtype=float).reshape(3)


def _monotone_prefix(s: np.ndarray) -> int:
    """Length of the leading strictly increasing part of s."""
    d = np.diff(s)
    bad = np.nonzero(d <= 0.0)[0]
    return len(s) if bad.size == 0 else int(bad[0]) + 1


def compare_spin(x0: Sequence[float], v0: Sequence[float], spin: Any, params: dict[str, Any],
                 n_grid: int = 400, **sim_kwargs) -> dict[str, Any]:
    """With-spin minus without-spin differences along the path (same x0, v0, params).

    spin: scalar backspin rate (rad/s; >0 backspin about ``backspin_omega(v0, .)``,
          <0 topspin) or an explicit 3-vector omega0.
    sim_kwargs: forwarded to ``simulate`` (wind, t_max, dt_max, stop, z_ground, ...).

    Returns dict:
      traj_spin, traj_nospin
      t, dx_t, dy_t, dz_t        : position differences at equal time (common time span)
      s, x, dz_s, dx_s           : at equal downrange distance s along the launch direction
                                   (x = absolute x of the grid); dz_s = z_spin(s) - z_nospin(s)
      apex: {"spin", "nospin" (apex dicts or None), "dx", "dz", "dt", "ds"}
      max_abs_dz_t / max_abs_dx_t / max_abs_dpos_t : {"value", "t", "x_spin", "z_spin"}
      max_abs_dz_s : {"value", "s", "x"}
      end: {"dx", "dz", "dt", "ds"} at termination
      reversal: {"spin": bool, "nospin": bool}
      downrange_monotone: bool (False if x-grid comparison was truncated by reversal)
    """
    v0a = np.asarray(v0, float)
    w = _spin_vector(v0a, spin)
    ts = simulate(x0, v0a, w, params, **sim_kwargs)
    tn = simulate(x0, v0a, np.zeros(3), params, **sim_kwargs)
    out: dict[str, Any] = {"traj_spin": ts, "traj_nospin": tn, "omega0": w}

    # ---- equal-time comparison
    t_end = min(ts.t[-1], tn.t[-1])
    tg = np.linspace(0.0, t_end, n_grid)
    ps = np.array([ts.sol(t)[0:3] for t in tg]) if ts.sol is not None else np.column_stack(
        [np.interp(tg, ts.t, ts.pos[:, k]) for k in range(3)])
    pn = np.array([tn.sol(t)[0:3] for t in tg]) if tn.sol is not None else np.column_stack(
        [np.interp(tg, tn.t, tn.pos[:, k]) for k in range(3)])
    d = ps - pn
    out.update(t=tg, dx_t=d[:, 0], dy_t=d[:, 1], dz_t=d[:, 2])

    def _mx(arr):
        i = int(np.argmax(np.abs(arr)))
        return {"value": float(arr[i]), "abs": float(abs(arr[i])), "t": float(tg[i]),
                "x_spin": float(ps[i, 0]), "z_spin": float(ps[i, 2])}

    out["max_abs_dx_t"] = _mx(d[:, 0])
    out["max_abs_dz_t"] = _mx(d[:, 2])
    out["max_abs_dpos_t"] = _mx(np.linalg.norm(d, axis=1))

    # ---- equal-downrange comparison
    h = _initial_horizontal_dir(v0a)
    ss = (ts.pos[:, 0:2] - ts.pos[0, 0:2]) @ h
    sn = (tn.pos[:, 0:2] - tn.pos[0, 0:2]) @ h
    ks, kn = _monotone_prefix(ss), _monotone_prefix(sn)
    monotone = ks == len(ss) and kn == len(sn)
    s_hi = min(ss[ks - 1], sn[kn - 1])
    if s_hi > 0.0 and ks >= 2 and kn >= 2:
        sg = np.linspace(0.0, s_hi, n_grid)
        zs = np.interp(sg, ss[:ks], ts.pos[:ks, 2])
        zn = np.interp(sg, sn[:kn], tn.pos[:kn, 2])
        dz_s = zs - zn
        i = int(np.argmax(np.abs(dz_s)))
        out.update(s=sg, x=float(np.asarray(x0, float)[0]) + sg * h[0], dz_s=dz_s)
        out["max_abs_dz_s"] = {"value": float(dz_s[i]), "abs": float(abs(dz_s[i])),
                               "s": float(sg[i]), "x": float(out["x"][i])}
    else:
        out.update(s=np.zeros(0), x=np.zeros(0), dz_s=np.zeros(0))
        out["max_abs_dz_s"] = None
    out["downrange_monotone"] = bool(monotone)

    # ---- apex and end
    a_s, a_n = ts.apex(), tn.apex()
    ap: dict[str, Any] = {"spin": a_s, "nospin": a_n}
    if a_s is not None and a_n is not None:
        ap.update(dx=float(a_s["x"] - a_n["x"]), dz=float(a_s["z"] - a_n["z"]),
                  dt=float(a_s["t"] - a_n["t"]),
                  ds=float((a_s["pos"][0:2] - a_n["pos"][0:2]) @ h))
    out["apex"] = ap
    out["end"] = {"dx": float(ts.pos[-1, 0] - tn.pos[-1, 0]),
                  "dz": float(ts.pos[-1, 2] - tn.pos[-1, 2]),
                  "dt": float(ts.t[-1] - tn.t[-1]),
                  "ds": float((ts.pos[-1, 0:2] - tn.pos[-1, 0:2]) @ h),
                  "termination": (ts.termination, tn.termination)}
    out["reversal"] = {"spin": horizontal_reversal(ts), "nospin": horizontal_reversal(tn)}
    return out
