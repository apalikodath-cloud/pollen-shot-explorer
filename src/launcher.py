"""Single-powered-wheel POLLEN launch model (PM-001, HANDOFF 4C/4D, deliverable 6).

One powered 98 mm flywheel below the ball; on the other side either a FIXED curved
hood (concentric with the wheel) or ONE PASSIVE (unpowered) roller.  SI units,
angles in rad, speeds in rad/s internally; RPM only at the API edges.

Sign conventions (planar, x = direction of ball travel, z = away from the wheel):
  v        ball-centre speed along the contact path (+ forward)
  s        ball absolute angular velocity, + = BACKSPIN (bottom/wheel side of the ball
           moves forward relative to its centre, hood side moves backward)
  Omega    flywheel angular velocity, + = surface at the contact moves forward
  Omega_t  passive-roller angular velocity, + = surface at the contact moves forward
           (i.e. a "counter-rotating" roller; a roller dragged by a backspinning ball
           whose hood-side point moves backward gets Omega_t < 0)
  r_c      ball centre-to-contact distance (effective rolling radius) = R_b - lam*delta/2
Slip velocities (surface minus ball contact point):
  slip_w = R_w*Omega - (v + s*r_c),   slip_t = R_t*Omega_t - (v - s*r_c)   (hood: R_t*Omega_t = 0)
Equations of motion (F_w, F_t = friction forces ON THE BALL, + forward):
  m dv/dt          = F_w + F_t
  I_b ds/dt        = r_c (F_w - F_t) + M_rr,ball
  I_w dOmega/dt    = -R_w F_w + tau_motor(Omega) - M_rr,wheel
  I_t dOmega_t/dt  = -R_t F_t - tau_bearing(Omega_t) + M_rr,roller        (roller only)
Coulomb friction |F| <= mu N with exact stick/slip per step (2x2 box LCP, enumerated).
Every step is an impulse update with constant forces, so the discrete energy ledger
(work with mid-step velocities) closes to round-off; tests check it.

Provenance of every default is in PARAMS (confirmed / user / assumed / derived).
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field, replace, asdict
from typing import Optional

import numpy as np

RPM2RAD = 2.0 * math.pi / 60.0
RAD2RPM = 1.0 / RPM2RAD

# ---------------------------------------------------------------------------
# Parameters with provenance
# ---------------------------------------------------------------------------
PARAMS = {
    "ball_mass": {"value": 0.025, "low": 0.0245, "high": 0.0255, "units": "kg",
                  "prov": "user/confirmed via HANDOFF s1-2: AndyMark am-5851_yellow lists 0.055 lb = 24.95 g "
                          "(https://andymark.com/products/biobuzz-scoring-elements?variant=47194281148588); weigh samples"},
    "ball_radius": {"value": 0.0355, "units": "m",
                    "prov": "confirmed nominal 2.8 in / 71 mm diameter (HANDOFF s1, s2); pieces vary"},
    "ball_kI": {"value": 0.63, "low": 0.55, "high": 2.0 / 3.0, "units": "-",
                "prov": "derived/assumed: I_b = kI m R^2. Thin shell 2/3 is the upper bound for a sphere with "
                        "mass at the surface; uniform PE shell (rho~950 kg/m^3) holding 25 g at R=35.5 mm needs "
                        "t~1.7-2.4 mm (perforations) -> thick-shell formula kI=0.4(1-q^5)/(1-q^3), q=1-t/R, "
                        "gives 0.62-0.64; 0.55 covers ribs/thick bosses/non-sphericity. Uniform hole pattern does "
                        "not change kI. MEASURE (bifilar/trifilar pendulum)."},
    "wheel_radius": {"value": 0.049, "units": "m", "prov": "user: one 98 mm flywheel (HANDOFF s2)"},
    "wheel_inertia": {"value": 2.65e-4, "low": 0.5e-4, "high": 5.0e-4, "units": "kg m^2",
                      "prov": "assumed/derived: bare 98 mm wheel ~1.0e-4 (assumed: 50-250 g, k_w 0.4-0.8 -> "
                              "0.5e-4..4.8e-4) + one goBILDA steel flywheel 3628-0032-0082 (82 mm, 152 g, "
                              "1651 g cm^2 = 1.651e-4, confirmed https://www.gobilda.com/steel-flywheel-82mm-"
                              "diameter-152g-1651-g-cm/). Motor rotor inertia not published (bounded <~1e-5, "
                              "assumed, reflected x gear^2)."},
    "motor_gobilda_5203_1to1": {"free_rpm": 6000, "stall_torque": 0.144, "stall_current": 9.2,
                                "prov": "confirmed goBILDA 5203-2402-0001 page: 6000 rpm @12 V, 1.47 kg cm "
                                        "(=0.144 N m), 9.2 A stall "
                                        "(https://gobilda.com/5203-series-yellow-jacket-motor-1-1-ratio-24mm-"
                                        "length-8mm-rex-shaft-6000-rpm-3-3-5v-encoder); related 5202 tested "
                                        "free speed ~5400 rpm (vendor listing) -> real free speed lower"},
    "motor_rev_hdhex_bare": {"free_rpm": 6000, "stall_torque": 0.105, "stall_current": 8.5,
                             "prov": "confirmed REV docs HD Hex Motor: 6000 rpm, 0.105 N m, 8.5 A @12 V "
                                     "(https://docs.revrobotics.com/duo-build/motion/motors/hd-hex-motor); "
                                     "UltraPlanetary 5:1 (5.23:1) 1147 rpm 0.55 N m (same page)"},
    "mu_wheel": {"value": 0.8, "low": 0.5, "high": 1.2, "prov": "assumed: rubber/TPU tread on PE; MEASURE (incline/pull test)"},
    "mu_hood": {"value": 0.3, "low": 0.05, "high": 1.0,
                "prov": "assumed: PTFE/UHMW ~0.05-0.15, polycarbonate/acrylic/HDPE ~0.2-0.4, rubber/grip-tape "
                        "lined 0.6-1.0 against PE; MEASURE"},
    "delta": {"value": 0.004, "low": 0.002, "high": 0.008, "units": "m",
              "prov": "user candidate 4 mm diametral compression (HANDOFF s2); swept 2-8 mm"},
    "k_n": {"value": 4000.0, "low": 1500.0, "high": 10000.0, "units": "N/m",
            "prov": "assumed: linear diametral stiffness of a 71 mm hollow perforated PE ball (no source "
                    "found); N(4 mm) = 6-40 N. Real N(delta) is non-linear (shell buckling). MEASURE with "
                    "plates + scale at 2/4/6/8 mm."},
    "lam_radius": {"value": 1.0, "low": 0.0, "high": 1.0,
                   "prov": "assumed: r_c = R_b - lam*delta/2; lam=1 all squeeze in the ball split evenly, "
                           "lam=0 rigid-radius rolling (flattened patch)"},
    "c_rr": {"value": 0.02, "low": 0.0, "high": 0.06,
             "prov": "assumed: rolling-hysteresis lever arm / r_c (energy loss per metre = c_rr N); "
                     "Brettle notes the ball 'is not a perfect spring' -> extra wheel slow-down"},
    "wrap_deg": {"value": 90.0, "low": 45.0, "high": 150.0,
                 "prov": "assumed: hood wrap angle about the wheel axis; shooter CAD not provided (HANDOFF s2)"},
    "v_in": {"value": 0.5, "low": 0.2, "high": 1.5, "units": "m/s",
             "prov": "assumed: feed speed of the ball into the contact (indexer), no initial spin"},
    "roller_radius": {"value": 0.024, "low": 0.0125, "high": 0.050, "units": "m",
                      "prov": "assumed: 1-4 in class passive top roller"},
    "roller_inertia": {"value": 1.0e-5, "low": 1.0e-6, "high": 2.0e-4, "units": "kg m^2",
                       "prov": "assumed: 48 mm compliant wheel ~25-40 g + shaft ~ 0.7-1.5e-5; light 1e-6; "
                               "with an added flywheel up to ~2e-4"},
    "roller_tau_coulomb": {"value": 5e-4, "low": 0.0, "high": 3e-3, "units": "N m",
                           "prov": "assumed: two small sealed ball bearings + seals; MEASURE by spin-down"},
    "roller_c_visc": {"value": 1e-6, "low": 0.0, "high": 1e-5, "units": "N m s",
                      "prov": "assumed: viscous/air drag of roller"},
    "shot_interval": {"value": 0.5, "low": 0.25, "high": 1.5, "units": "s",
                      "prov": "assumed: time between consecutive shots (roller coasts with bearing drag)"},
}


# ---------------------------------------------------------------------------
# Configuration dataclasses
# ---------------------------------------------------------------------------
@dataclass
class Ball:
    mass: float = 0.025
    radius: float = 0.0355
    kI: float = 0.63

    @property
    def inertia(self) -> float:
        return self.kI * self.mass * self.radius ** 2


@dataclass
class Motor:
    """Linear DC-motor torque-speed line at the WHEEL shaft (gear = motor rev / wheel rev)."""
    free_rpm: float = 6000.0
    stall_torque: float = 0.144
    gear: float = 1.0
    voltage_frac: float = 1.0     # applied voltage / 12 V (battery sag lowers it)

    def torque(self, omega_wheel: float) -> float:
        w_free = self.free_rpm * RPM2RAD
        return self.gear * self.stall_torque * (self.voltage_frac - omega_wheel * self.gear / w_free)


@dataclass
class Wheel:
    radius: float = 0.049
    inertia: float = 2.65e-4
    motor: Optional[Motor] = None   # None = coast during contact (Brettle's assumption)


@dataclass
class Contact:
    mu_wheel: float = 0.8
    mu_top: float = 0.3
    delta: float = 0.004       # diametral compression at the nominal gap [m]
    k_n: float = 4000.0        # linear diametral stiffness [N/m]
    lam_radius: float = 1.0
    c_rr: float = 0.02
    centripetal: bool = True   # hood only: N_t - N_w = m v^2 / rho


@dataclass
class Hood:
    wrap_deg: float = 90.0     # concentric hood arc about the wheel axis

    kind: str = field(default="hood", init=False)


@dataclass
class Roller:
    radius: float = 0.024
    inertia: float = 1.0e-5
    omega0: float = 0.0        # rad/s, + = contact surface moves forward
    tau_coulomb: float = 5e-4
    c_visc: float = 1e-6

    kind: str = field(default="roller", init=False)

    def drag(self, om: float) -> float:
        """Bearing drag torque (opposes rotation), smooth near zero."""
        return self.tau_coulomb * math.tanh(om / 0.5) + self.c_visc * om


@dataclass
class ShotResult:
    v_exit: float
    spin: float               # rad/s, + backspin
    S: float                  # spin * R_b(nominal) / v_exit
    wheel_rpm0: float
    wheel_rpm_exit: float
    rpm_drop: float
    roller_omega_exit: float
    contact_time: float
    exited: bool              # False = ball stalled / never left the contact
    slip_w_exit: float        # m/s, surface - ball point
    slip_t_exit: float
    lost_wheel_contact: bool  # N_w hit zero somewhere (centripetal unloading)
    energy: dict

    @property
    def spin_rpm(self) -> float:
        return self.spin * RAD2RPM


# ---------------------------------------------------------------------------
# Ideal / closed-form relations
# ---------------------------------------------------------------------------
def hood_ideal(wheel_rpm_exit: float, R_w: float = 0.049, R_b: float = 0.0355):
    """No-slip, rigid, diametrically opposed contacts, fixed hood.
    Hood contact point at rest: v - s R_b = 0; wheel contact: v + s R_b = R_w Omega.
    -> v_exit = R_w Omega / 2, omega_exit = v_exit / R_b, S = 1.  Omega is the wheel speed AT EXIT."""
    om = wheel_rpm_exit * RPM2RAD
    v = R_w * om / 2.0
    return v, v / R_b


def effective_radius(ball: Ball, contact: Contact) -> float:
    return ball.radius - contact.lam_radius * contact.delta / 2.0


def brettle_ratio(ball: Ball, wheel: Wheel, r_c: Optional[float] = None) -> float:
    """Omega_i/Omega_f for a fixed hood, rolling at both contacts at exit, coasting wheel.
    Generalised Brettle (k_p -> kI (R_b/r_c)^2, v_in): impulses J_w + J_t = m (v - v_in),
    J_w - J_t = I_b s / r_c, v = s r_c = R_w Omega_f / 2, I_w (Omega_i - Omega_f) = R_w J_w.
    Returns the v_in = 0 ratio; with r_c = R_b this is Brettle's 1 + (1+k_p)/(4 k_w) m_p/m_w."""
    r_c = ball.radius if r_c is None else r_c
    m, I_b, R_w, I_w = ball.mass, ball.inertia, wheel.radius, wheel.inertia
    # J_w = [m (v - v_in) + I_b v / r_c^2] / 2,  v = R_w Om_f / 2
    # I_w (Om_i - Om_f) = R_w J_w  ->  Om_i = Om_f (1 + R_w^2 (m + I_b/r_c^2)/(4 I_w)) - R_w m v_in/(2 I_w)
    a = 1.0 + R_w ** 2 * (m + I_b / r_c ** 2) / (4.0 * I_w)
    return a  # v_in correction is applied in brettle_omega_f


def brettle_omega_f(omega_i: float, ball: Ball, wheel: Wheel, r_c: Optional[float] = None,
                    v_in: float = 0.0) -> float:
    a = brettle_ratio(ball, wheel, r_c)
    return (omega_i + wheel.radius * ball.mass * v_in / (2.0 * wheel.inertia)) / a


def frictionless_top_limit(ball: Ball, r_c: Optional[float] = None) -> float:
    """S when only the wheel contact applies friction and the ball starts at rest:
    m dv = F dt, I_b ds = r_c F dt -> s r_c / v = m r_c^2 / I_b; S = s R_b / v = m r_c R_b / I_b."""
    r_c = ball.radius if r_c is None else r_c
    return ball.mass * r_c * ball.radius / ball.inertia


def roller_rolling_state(u_w: float, u_t: float, r_c: float, R_b: float):
    """Rolling at both contacts with surface speeds u_w (wheel) and u_t (roller, + forward):
    v = (u_w + u_t)/2, s = (u_w - u_t)/(2 r_c), S = s R_b / v."""
    v = 0.5 * (u_w + u_t)
    s = (u_w - u_t) / (2.0 * r_c)
    return v, s, (s * R_b / v if v > 0 else float("nan"))


# ---------------------------------------------------------------------------
# Friction LCP (2 contacts) -- exact Coulomb stick/slip per step
# ---------------------------------------------------------------------------
def _solve_friction(A, rhs, lim, active):
    """Coulomb friction at 2 contacts for one implicit step.
    Post-step slip_i = dt*(rhs_i - sum_j A_ij F_j).  Each contact: stick (slip=0, |F|<=lim),
    slide+ (F=+lim, slip>=0) or slide- (F=-lim, slip<=0).  A is symmetric positive definite
    (A = J M^-1 J^T), so the box LCP has a unique solution; the 9 modes are enumerated."""
    a00, a01, a11 = A[0][0], A[0][1], A[1][1]
    r0, r1 = rhs
    l0, l1 = lim
    tol0 = 1e-12 * (1.0 + abs(r0))
    tol1 = 1e-12 * (1.0 + abs(r1))
    modes0 = (0, 1, -1) if active[0] else (0,)
    modes1 = (0, 1, -1) if active[1] else (0,)
    for m0 in modes0:
        for m1 in modes1:
            if not active[0]:
                F0 = 0.0
            if not active[1]:
                F1 = 0.0
            st0 = active[0] and m0 == 0
            st1 = active[1] and m1 == 0
            if m0 != 0:
                F0 = m0 * l0
            if m1 != 0:
                F1 = m1 * l1
            if st0 and st1:
                det = a00 * a11 - a01 * a01
                F0 = (r0 * a11 - a01 * r1) / det
                F1 = (a00 * r1 - a01 * r0) / det
            elif st0:
                F0 = (r0 - a01 * F1) / a00
            elif st1:
                F1 = (r1 - a01 * F0) / a11
            res0 = r0 - a00 * F0 - a01 * F1
            res1 = r1 - a01 * F0 - a11 * F1
            if st0 and abs(F0) > l0 * (1 + 1e-9) + 1e-12:
                continue
            if st1 and abs(F1) > l1 * (1 + 1e-9) + 1e-12:
                continue
            if m0 == 1 and res0 < -tol0 or m0 == -1 and res0 > tol0:
                continue
            if m1 == 1 and res1 < -tol1 or m1 == -1 and res1 > tol1:
                continue
            return F0, F1
    raise RuntimeError("friction LCP: no consistent mode (should not happen for SPD A)")


# ---------------------------------------------------------------------------
# Time-stepping contact model
# ---------------------------------------------------------------------------
def simulate_shot(wheel_rpm: float, ball: Ball = None, wheel: Wheel = None, contact: Contact = None,
                  top=None, v_in: float = 0.5, s_in: float = 0.0, dt: float = 1e-5,
                  t_max: float = 0.25, record: bool = False) -> ShotResult:
    ball = ball or Ball()
    wheel = wheel or Wheel()
    contact = contact or Contact()
    top = top or Hood()
    m, I_b, R_b = ball.mass, ball.inertia, ball.radius
    R_w, I_w = wheel.radius, wheel.inertia
    r_c = effective_radius(ball, contact)
    is_roller = isinstance(top, Roller)

    # contact path
    if is_roller:
        R_t, I_t = top.radius, top.inertia
        kappa = 1.0 / (R_w + R_b) + 1.0 / (R_t + R_b)          # gap curvature along the path
        x_half = math.sqrt(2.0 * contact.delta / kappa) if contact.delta > 0 else 0.0
        x0, x_end = -x_half, x_half
        rho = math.inf
        mu_t = contact.mu_top
    else:
        R_t, I_t = 1.0, math.inf
        rho = R_w + r_c
        x0, x_end = 0.0, math.radians(top.wrap_deg) * rho
        kappa = 0.0
        mu_t = contact.mu_top

    def normal0(x):
        if is_roller:
            d = contact.delta - 0.5 * kappa * x * x
            return contact.k_n * max(d, 0.0)
        return contact.k_n * contact.delta

    inv_m, b_r = 1.0 / m, r_c * r_c / I_b
    a_ww = R_w * R_w / I_w + inv_m + b_r
    a_tt = (R_t * R_t / I_t if is_roller else 0.0) + inv_m + b_r
    a_wt = inv_m - b_r
    A = ((a_ww, a_wt), (a_wt, a_tt))

    v, s, x, t = v_in, s_in, x0, 0.0
    Om = wheel_rpm * RPM2RAD
    Om0 = Om
    Omt = top.omega0 if is_roller else 0.0
    Omt0 = Omt
    E = {"motor_work": 0.0, "friction_wheel": 0.0, "friction_top": 0.0, "rolling_hyst": 0.0,
         "bearing": 0.0}
    lost = False
    hist = [] if record else None
    eps_rel = 1.0  # rad/s smoothing for rolling-hysteresis sign
    exited = False
    while t < t_max:
        N0 = normal0(x)
        if contact.centripetal and not is_roller:
            dN = 0.5 * m * v * v / rho
        else:
            dN = 0.0
        N_w = N0 - dN
        N_t = N0 + dN
        if N_w < 0.0:
            # ball rides on the hood only; hood carries the full centripetal load
            if N0 > 0:
                lost = True
            N_w = 0.0
            N_t = m * v * v / rho if not is_roller else N_t
        # rolling hysteresis moments (on the ball, CCW = backspin positive)
        e_w = contact.c_rr * r_c * N_w
        e_t = contact.c_rr * r_c * N_t
        rel_w = s + Om                  # ball spin relative to wheel (both expressed in the ball's sense)
        rel_t = s - (Omt if is_roller else 0.0)
        Mw_ball = -e_w * math.tanh(rel_w / eps_rel)
        Mt_ball = -e_t * math.tanh(rel_t / eps_rel)
        Mw_wheel = -Mw_ball             # reaction, in the ball's CCW sense; wheel CW sense -> -(...)
        Mt_roll = -Mt_ball
        tau_m = wheel.motor.torque(Om) if wheel.motor is not None else 0.0
        tau_d = top.drag(Omt) if is_roller else 0.0
        # known (force-free) accelerations
        dv0 = 0.0
        ds0 = (Mw_ball + Mt_ball) / I_b
        # wheel CW-positive: CCW moment Mw_wheel slows it -> -Mw_wheel ... careful sign:
        # relative rotation rel_w = s + Om > 0 -> Mw_ball < 0 (slows backspin) and the wheel
        # (CW positive) is also slowed: dOm += -|e_w| -> use -Mw_wheel (Mw_wheel>0 here).
        dOm0 = (tau_m - Mw_wheel) / I_w
        # roller (+ = contact surface forward = CCW for a roller above the ball): CCW reaction Mt_roll
        dOmt0 = ((-tau_d + Mt_roll) / I_t) if is_roller else 0.0
        slip_w = R_w * Om - (v + s * r_c)
        slip_t = (R_t * Omt if is_roller else 0.0) - (v - s * r_c)
        b_w = R_w * dOm0 - dv0 - r_c * ds0
        b_t = (R_t * dOmt0 if is_roller else 0.0) - dv0 + r_c * ds0
        rhs = (slip_w / dt + b_w, slip_t / dt + b_t)
        lim = (contact.mu_wheel * N_w, mu_t * N_t)
        active = (lim[0] > 0.0, lim[1] > 0.0)
        F_w, F_t = _solve_friction(A, rhs, lim, active)
        v1 = v + dt * (F_w + F_t) * inv_m
        s1 = s + dt * (r_c * (F_w - F_t) + Mw_ball + Mt_ball) / I_b
        Om1 = Om + dt * (-R_w * F_w + tau_m - Mw_wheel) / I_w
        Omt1 = Omt + dt * ((-R_t * F_t - tau_d + Mt_roll) / I_t) if is_roller else 0.0
        # energy ledger with mid-step velocities (exact for constant-force impulse steps)
        vm, sm, Omm, Omtm = 0.5 * (v + v1), 0.5 * (s + s1), 0.5 * (Om + Om1), 0.5 * (Omt + Omt1)
        E["motor_work"] += tau_m * Omm * dt
        E["friction_wheel"] += F_w * (R_w * Omm - vm - sm * r_c) * dt
        E["friction_top"] += F_t * ((R_t * Omtm if is_roller else 0.0) - vm + sm * r_c) * dt
        E["rolling_hyst"] += -(Mw_ball * (sm + Omm) + Mt_ball * (sm - (Omtm if is_roller else 0.0))) * dt
        E["bearing"] += tau_d * Omtm * dt
        x += vm * dt
        v, s, Om, Omt = v1, s1, Om1, Omt1
        t += dt
        if record:
            hist.append((t, x, v, s, Om, Omt, N_w, N_t, F_w, F_t))
        if x >= x_end:
            exited = True
            break
        if v <= 0.0 and t > 0.01:
            break
    ke_ball = 0.5 * m * v * v + 0.5 * I_b * s * s - (0.5 * m * v_in ** 2 + 0.5 * I_b * s_in ** 2)
    ke_wheel = 0.5 * I_w * (Om0 ** 2 - Om ** 2)
    ke_roll = 0.5 * I_t * (Omt ** 2 - Omt0 ** 2) if is_roller else 0.0
    E.update({"ball_ke_gain": ke_ball, "wheel_ke_loss": ke_wheel, "roller_ke_gain": ke_roll})
    E["balance_residual"] = (ke_wheel + E["motor_work"]) - (ke_ball + ke_roll + E["friction_wheel"]
                                                             + E["friction_top"] + E["rolling_hyst"]
                                                             + E["bearing"])
    slip_w = R_w * Om - (v + s * r_c)
    slip_t = (R_t * Omt if is_roller else 0.0) - (v - s * r_c)
    res = ShotResult(v_exit=v, spin=s, S=(s * R_b / v if v > 1e-9 else float("nan")),
                     wheel_rpm0=wheel_rpm, wheel_rpm_exit=Om * RAD2RPM, rpm_drop=(Om0 - Om) * RAD2RPM,
                     roller_omega_exit=Omt, contact_time=t, exited=exited,
                     slip_w_exit=slip_w, slip_t_exit=slip_t, lost_wheel_contact=lost, energy=E)
    if record:
        res.history = np.array(hist)
    return res


def hood_model(wheel_rpm, ball=None, wheel=None, contact=None, wrap_deg=90.0, **kw) -> ShotResult:
    return simulate_shot(wheel_rpm, ball, wheel, contact, Hood(wrap_deg=wrap_deg), **kw)


def roller_model(wheel_rpm, ball=None, wheel=None, contact=None, roller=None, **kw) -> ShotResult:
    return simulate_shot(wheel_rpm, ball, wheel, contact, roller or Roller(), **kw)


def roller_coast(omega: float, roller: Roller, t: float, dt: float = 1e-3) -> float:
    """Spin-down of the free roller between shots: I_t dOm/dt = -tau_bearing(Om)."""
    n = max(1, int(t / dt))
    h = t / n
    for _ in range(n):
        om_new = omega - h * roller.drag(omega) / roller.inertia
        if omega != 0 and np.sign(om_new) != np.sign(omega):
            return 0.0
        omega = om_new
    return omega


def roller_shot_sequence(wheel_rpm, n_shots=4, interval=0.5, ball=None, wheel=None, contact=None,
                         roller=None, recover_wheel=True, **kw):
    """Consecutive shots: roller keeps its exit speed, coasts for `interval`, next ball hits it.
    The wheel is assumed re-regulated to wheel_rpm between shots (recover_wheel)."""
    roller = replace(roller or Roller())
    out = []
    om = roller.omega0
    for _ in range(n_shots):
        r = replace(roller, omega0=om)
        res = roller_model(wheel_rpm, ball, wheel, contact, r, **kw)
        out.append(res)
        om = roller_coast(res.roller_omega_exit, r, interval)
    return out


def recovery_time(rpm_drop: float, wheel_rpm: float, wheel: Wheel, motor: Motor) -> float:
    """Time for the motor at full voltage to restore rpm_drop (linear torque-speed line, no current limit)."""
    w_f = motor.free_rpm * RPM2RAD / motor.gear * motor.voltage_frac
    w_target = wheel_rpm * RPM2RAD
    if w_target >= w_f:
        return math.inf
    w_start = w_target - rpm_drop * RPM2RAD
    # I dw/dt = T0 (1 - w/w_f) with T0 = gear*stall*vfrac -> tau = I w_f / T0
    T0 = motor.gear * motor.stall_torque * motor.voltage_frac
    tau = wheel.inertia * w_f / T0
    return tau * math.log((w_f - w_start) / (w_f - w_target))


def droop_readout(wheel_rpm: float, v_exit: float, S: float, ball: Ball = None, wheel: Wheel = None,
                  contact: Contact = None, motor: Motor = None, wrap_deg: float = 90.0, v_in: float = 0.5) -> dict:
    """Closed-form per-shot flywheel droop and recovery (PM-022 readout; JS twin droopReadout in viz/explorer/solver.js).
    Coasting wheel during contact, fixed hood, ball leaves with v_exit and S = s R_b / v (any slip state):
      impulse  (generalised Brettle, exact for the friction impulses): I_w dOm_1 = R_w m [(v - v_in) + kI S v R_b / r_c] / 2
      rolling hysteresis (wheel-side lever arm, as simulate_shot): I_w dOm_2 = c_rr k_n delta rho T, rho = R_w + r_c,
      contact time T ~ wrap rho / v (ball centre on the wrap arc at the exit speed; hood_model is 0-60 % longer above 1000 rpm).
    No fitted factor; tests/test_launcher.py states the agreement with hood_model over RPM_GRID (within about 1.5 %, PREDICTED;
    about 2 % at 2000-6000 rpm for I_w 5e-5..1e-3 and wrap 60-120 deg). Limit: below 2000 rpm a light wheel loses most of
    its speed, the ball slows before exit and T is overestimated, so the drop reads high (+30 % at 5e-5 kg m^2, 1000 rpm, wrap 90;
    larger at wider wrap). The wheel is assumed to coast during contact, so the drop is an upper bound if the motor drives.
    Not modelled: motor drive during contact, current limit, controller lag, motor rotor inertia (wheel.inertia only).
    recovery_s = recovery_time() (linear motor line at voltage_frac, inf when wheel_rpm >= the loaded free speed
    free_rpm voltage_frac / gear); min_interval_s = contact estimate + recovery (feed time not included)."""
    ball, wheel, contact, motor = ball or Ball(), wheel or Wheel(), contact or Contact(), motor or Motor()
    r_c = effective_radius(ball, contact)
    rho = wheel.radius + r_c
    v = max(float(v_exit), 1e-9)
    j_w = ball.mass * ((v - v_in) + ball.kI * S * v * ball.radius / r_c) / 2.0
    d_imp = wheel.radius * max(j_w, 0.0) / wheel.inertia
    t_c = math.radians(wrap_deg) * rho / v
    d_hys = contact.c_rr * contact.k_n * contact.delta * rho * t_c / wheel.inertia
    drop = (d_imp + d_hys) * RAD2RPM
    t_rec = recovery_time(drop, wheel_rpm, wheel, motor)
    return {"drop_rpm": drop, "drop_pct": 100.0 * drop / wheel_rpm if wheel_rpm > 0 else math.inf,
            "impulse_rpm": d_imp * RAD2RPM, "hysteresis_rpm": d_hys * RAD2RPM, "contact_s": t_c,
            "recovery_s": t_rec, "min_interval_s": t_c + t_rec,
            "free_rpm_loaded": motor.free_rpm / motor.gear * motor.voltage_frac,
            "above_free": wheel_rpm * RPM2RAD >= motor.free_rpm * RPM2RAD / motor.gear * motor.voltage_frac}


# ---------------------------------------------------------------------------
# Envelope generation
# ---------------------------------------------------------------------------
RPM_GRID = [1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000]


def _row(res: ShotResult, extra=None):
    d = {"wheel_rpm": res.wheel_rpm0, "v_exit": round(res.v_exit, 4), "spin_rpm": round(res.spin_rpm, 1),
         "S": round(res.S, 4), "rpm_drop": round(res.rpm_drop, 1),
         "exited": res.exited, "lost_wheel_contact": res.lost_wheel_contact,
         "slip_wheel_exit": round(res.slip_w_exit, 3), "slip_top_exit": round(res.slip_t_exit, 3),
         "contact_time_ms": round(res.contact_time * 1e3, 2),
         "sliding_loss_J": round(res.energy["friction_wheel"] + res.energy["friction_top"], 4),
         "top_sliding_loss_J": round(res.energy["friction_top"], 4)}
    if extra:
        d.update(extra)
    return d


def configurations():
    """Named configurations for the envelope (all 'predicted', uncalibrated)."""
    base_c = Contact()
    cfg = {
        "hood_nominal": dict(kind="hood", contact=base_c, wrap=90.0,
                             note="mu_w 0.8, mu_hood 0.3 (polycarbonate-like), delta 4 mm, k_n 4 N/mm, wrap 90 deg"),
        "hood_grippy": dict(kind="hood", contact=replace(base_c, mu_top=0.9), wrap=90.0,
                            note="rubber/grip-tape lined hood mu 0.9"),
        "hood_slick": dict(kind="hood", contact=replace(base_c, mu_top=0.08), wrap=90.0,
                           note="PTFE/UHMW hood mu 0.08"),
        "hood_slick_short": dict(kind="hood", contact=replace(base_c, mu_top=0.08), wrap=45.0,
                                 note="PTFE hood, 45 deg wrap"),
        "hood_soft_ball": dict(kind="hood", contact=replace(base_c, k_n=1500.0), wrap=90.0,
                               note="low stiffness bound k_n 1.5 N/mm (N(4mm)=6 N)"),
        "hood_stiff_ball_8mm": dict(kind="hood", contact=replace(base_c, k_n=10000.0, delta=0.008), wrap=90.0,
                                    note="high stiffness 10 N/mm and 8 mm squeeze (N=80 N)"),
        "roller_light_rest": dict(kind="roller", contact=replace(base_c, mu_top=0.8),
                                  roller=Roller(inertia=2e-6), note="light 48 mm roller (2e-6) from rest, mu_top 0.8"),
        "roller_nominal_rest": dict(kind="roller", contact=replace(base_c, mu_top=0.8),
                                    roller=Roller(), note="48 mm roller I=1e-5 from rest, mu_top 0.8"),
        "roller_heavy_rest": dict(kind="roller", contact=replace(base_c, mu_top=0.8),
                                  roller=Roller(inertia=2e-4), note="48 mm roller + flywheel I=2e-4 from rest"),
        "roller_nominal_steady": dict(kind="roller_seq", contact=replace(base_c, mu_top=0.8),
                                      roller=Roller(), note="I=1e-5, 4th shot of a 0.5 s-interval burst "
                                                            "(roller pre-spun by previous shots)"),
    }
    return cfg


def run_config(name, c, rpms=RPM_GRID, ball=None, wheel=None):
    ball = ball or Ball()
    wheel = wheel or Wheel()
    rows = []
    for rpm in rpms:
        if c["kind"] == "hood":
            r = hood_model(rpm, ball, wheel, c["contact"], wrap_deg=c["wrap"])
            rows.append(_row(r))
        elif c["kind"] == "roller":
            r = roller_model(rpm, ball, wheel, c["contact"], c["roller"])
            rows.append(_row(r, {"roller_exit_rpm": round(r.roller_omega_exit * RAD2RPM, 1)}))
        else:
            seq = roller_shot_sequence(rpm, 4, PARAMS["shot_interval"]["value"], ball, wheel,
                                       c["contact"], c["roller"])
            r = seq[-1]
            rows.append(_row(r, {"roller_exit_rpm": round(r.roller_omega_exit * RAD2RPM, 1),
                                 "S_by_shot": [round(q.S, 3) for q in seq],
                                 "v_by_shot": [round(q.v_exit, 3) for q in seq]}))
    return rows


def build_envelope(path=None):
    ball, wheel = Ball(), Wheel()
    env = {
        "units": {"v_exit": "m/s", "spin_rpm": "rev/min (+ = backspin)", "S": "omega*R_b/v (R_b nominal 0.0355 m)",
                  "rpm_drop": "flywheel rev/min lost during one shot (coasting wheel)"},
        "label": "predicted (uncalibrated model; no measurements exist yet)",
        "model": "src/launcher.py simulate_shot: planar 1-D contact path, Coulomb stick/slip at wheel and "
                 "top contact, linear N(delta), centripetal unloading of the wheel contact on a curved hood, "
                 "rolling hysteresis c_rr, coasting flywheel, passive roller with bearing drag",
        "common_assumptions": {k: PARAMS[k] for k in ("ball_mass", "ball_radius", "ball_kI", "wheel_radius",
                                                      "wheel_inertia", "mu_wheel", "mu_hood", "delta", "k_n",
                                                      "lam_radius", "c_rr", "wrap_deg", "v_in",
                                                      "roller_radius", "roller_inertia", "roller_tau_coulomb",
                                                      "roller_c_visc", "shot_interval")},
        "motors": {k: PARAMS[k] for k in ("motor_gobilda_5203_1to1", "motor_rev_hdhex_bare")},
        "configs": {},
    }
    # ideal
    rows = []
    for rpm in RPM_GRID:
        om_f = brettle_omega_f(rpm * RPM2RAD, ball, wheel)
        v, w = hood_ideal(om_f * RAD2RPM)
        rows.append({"wheel_rpm": rpm, "v_exit": round(v, 4), "spin_rpm": round(w * RAD2RPM, 1), "S": 1.0,
                     "rpm_drop": round(rpm - om_f * RAD2RPM, 1)})
    env["configs"]["hood_ideal_brettle"] = {
        "note": "derived: rigid, no slip at both contacts at exit, v_in=0, Brettle RPM drop with kI=0.63, "
                "I_w=2.65e-4; v=R_w*Omega_exit/2, omega=v/R_b, S=1",
        "points": rows}
    for name, c in configurations().items():
        env["configs"][name] = {"note": c["note"], "points": run_config(name, c, ball=ball, wheel=wheel)}
    # wheel recovery after one shot (hood_nominal drops), goBILDA 5203 1:1 at full voltage, linear motor line
    rec = []
    for p_ in env["configs"]["hood_nominal"]["points"]:
        for vf in (1.0, 11.5 / 12.0):
            tr = recovery_time(p_["rpm_drop"], p_["wheel_rpm"], wheel, Motor(voltage_frac=vf))
            rec.append({"wheel_rpm": p_["wheel_rpm"], "voltage_frac": round(vf, 3),
                        "recovery_s": (round(tr, 3) if math.isfinite(tr) else None)})
    env["recovery_hood_nominal"] = {
        "note": "derived: time for a goBILDA 5203 1:1 (6000 rpm, 0.144 N m @12 V, confirmed) at full voltage to "
                "restore the hood_nominal rpm_drop, I_w 2.65e-4, no current limit, no controller lag; "
                "inf = setpoint above the loaded free speed", "points": rec}
    # motor assist during contact (bounds): coast vs full voltage
    ma = []
    for rpm in (2000, 3000, 4000):
        r0 = hood_model(rpm, ball, wheel, Contact())
        r1 = hood_model(rpm, ball, replace(wheel, motor=Motor()), Contact())
        ma.append({"wheel_rpm": rpm, "v_coast": round(r0.v_exit, 3), "v_full_voltage": round(r1.v_exit, 3),
                   "drop_coast": round(r0.rpm_drop, 1), "drop_full_voltage": round(r1.rpm_drop, 1)})
    env["motor_assist_bounds"] = {"note": "hood_nominal; Brettle assumes coast; real velocity control lies between",
                                  "points": ma}
    # reachable S summary
    env["reachable_S_summary"] = reachable_S_summary()
    if path:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(env, f, indent=1)
    return env


def reachable_S_summary(rpm=3000.0):
    """Range of S over the assumed parameter boxes at one wheel speed (predicted)."""
    ball0 = Ball()
    out = {"wheel_rpm": rpm, "hood": {}, "roller": {}}
    Ss, vs = [], []
    for kI in (0.55, 0.63, 2 / 3):
        for mu_t in (0.05, 0.15, 0.3, 0.6, 1.0):
            for wrap in (45.0, 90.0, 150.0):
                for delta in (0.002, 0.004, 0.008):
                    for k_n in (1500.0, 4000.0, 10000.0):
                        c = Contact(mu_top=mu_t, delta=delta, k_n=k_n)
                        r = hood_model(rpm, replace(ball0, kI=kI), Wheel(), c, wrap_deg=wrap, dt=2e-5)
                        if r.exited:
                            Ss.append(r.S)
                            vs.append(r.v_exit)
    out["hood"] = {"S_min": round(min(Ss), 3), "S_max": round(max(Ss), 3), "v_min": round(min(vs), 3),
                   "v_max": round(max(vs), 3), "n_cases": len(Ss),
                   "box": "kI 0.55-0.667, mu_hood 0.05-1.0, wrap 45-150 deg, delta 2-8 mm, k_n 1.5-10 N/mm, "
                          "mu_w 0.8, c_rr 0.02, v_in 0.5"}
    Ss, vs = [], []
    for I_t in (1e-6, 1e-5, 1e-4, 2e-4):
        for tau_c in (0.0, 5e-4, 3e-3):
            for R_t in (0.0125, 0.024, 0.05):
                for delta in (0.004, 0.008):
                    c = Contact(mu_top=0.8, delta=delta)
                    rol = Roller(radius=R_t, inertia=I_t, omega0=0.0, tau_coulomb=tau_c)
                    seq = roller_shot_sequence(rpm, 3, PARAMS["shot_interval"]["value"], ball0, Wheel(), c,
                                               rol, dt=2e-5)
                    for r in seq:   # shot 1 = roller at rest, shots 2-3 = pre-spun by the previous shot
                        if r.exited:
                            Ss.append(r.S)
                            vs.append(r.v_exit)
    out["roller"] = {"S_min": round(min(Ss), 3), "S_max": round(max(Ss), 3), "v_min": round(min(vs), 3),
                     "v_max": round(max(vs), 3), "n_cases": len(Ss),
                     "box": "passive: I_t 1e-6..2e-4, R_t 12.5-50 mm, bearing 0..3e-3 N m, delta 4/8 mm, "
                            "mu_top 0.8, k_n 4 N/mm; shots 1-3 of a 0.5 s burst (rest, then pre-spun)"}
    # hypothetical: roller surface pre-spun FORWARD by something other than the ball (not passive)
    hyp = []
    for om0 in (100.0, 200.0, 400.0):
        r = roller_model(rpm, ball0, Wheel(), Contact(mu_top=0.8), Roller(omega0=om0, inertia=1e-4), dt=2e-5)
        hyp.append({"omega0_rad_s": om0, "S": round(r.S, 3), "v_exit": round(r.v_exit, 3)})
    out["roller_hypothetical_forward_prespin"] = {
        "note": "NOT achievable by a passive roller in this model (the ball drags it backward); shows that S<1 "
                "needs the top surface moving forward", "points": hyp}
    # fast feed: a ball entering with forward speed and no spin
    fast = []
    for v_in in (0.5, 2.0, 4.0):
        r = roller_model(rpm, ball0, Wheel(), Contact(mu_top=0.8), Roller(inertia=2e-6), v_in=v_in, dt=2e-5)
        fast.append({"v_in": v_in, "S": round(r.S, 3), "v_exit": round(r.v_exit, 3),
                     "roller_exit_rad_s": round(r.roller_omega_exit, 1)})
    out["roller_fast_feed"] = {"note": "light roller, ball fed with forward speed v_in and zero spin",
                               "points": fast}
    hf = []
    for wrap in (20.0, 45.0):
        for mu_t in (0.05, 0.1):
            for v_in in (3.0, 5.0):
                r = hood_model(rpm, ball0, Wheel(), Contact(mu_top=mu_t), wrap_deg=wrap, v_in=v_in, dt=2e-5)
                hf.append({"wrap_deg": wrap, "mu_hood": mu_t, "v_in": v_in, "S": round(r.S, 3),
                           "v_exit": round(r.v_exit, 3)})
    out["hood_fast_feed_short_slick"] = {
        "note": "S<1 from a fixed hood needs the ball to ENTER already moving (pre-accelerated, no spin) and leave "
                "before hood friction rolls it up (short wrap, low mu); not a recommended design, shows the limit",
        "points": hf}
    return out


# ---------------------------------------------------------------------------
# Figures (Agg backend; palette = dataviz reference categorical order)
# ---------------------------------------------------------------------------
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"


def _style(ax, xlabel, ylabel, title=None):
    ax.set_facecolor(SURF)
    ax.grid(True, color=GRID, lw=0.8)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.set_xlabel(xlabel, color=INK2, fontsize=9)
    ax.set_ylabel(ylabel, color=INK2, fontsize=9)
    if title:
        ax.set_title(title, color=INK, fontsize=10, loc="left")


def make_figures(root, env=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig_dir = os.path.join(root, "figures")
    os.makedirs(fig_dir, exist_ok=True)
    env = env or build_envelope()
    ball, wheel = Ball(), Wheel()
    out = []

    def save(fig, name):
        fig.patch.set_facecolor(SURF)
        fig.tight_layout()
        path = os.path.join(fig_dir, name)
        fig.savefig(path, dpi=140)
        plt.close(fig)
        out.append(path)

    # 1. envelope v, S, rpm drop vs wheel rpm
    names = ["hood_ideal_brettle", "hood_nominal", "hood_slick_short", "hood_soft_ball", "hood_stiff_ball_8mm",
             "roller_nominal_rest"]
    fig, axs = plt.subplots(1, 3, figsize=(13, 4))
    for i, n in enumerate(names):
        pts = env["configs"][n]["points"]
        x = [p["wheel_rpm"] for p in pts]
        kw = dict(color=SERIES[i], lw=2, marker="o", ms=3, label=n)
        axs[0].plot(x, [p["v_exit"] for p in pts], **kw)
        axs[1].plot(x, [p["S"] for p in pts], **kw)
        axs[2].plot(x, [p["rpm_drop"] for p in pts], **kw)
    _style(axs[0], "wheel rpm before shot", "exit speed v [m/s]", "Exit speed (predicted)")
    _style(axs[1], "wheel rpm before shot", "S = omega R_b / v", "Spin parameter at exit")
    _style(axs[2], "wheel rpm before shot", "flywheel rpm drop per shot", "RPM drop (coasting wheel)")
    axs[0].legend(fontsize=7, frameon=False)
    save(fig, "launcher_envelope_vs_rpm.png")

    # 2. compression sweep
    deltas = np.linspace(0.002, 0.008, 13)
    fig, axs = plt.subplots(1, 3, figsize=(13, 4))
    i = 0
    for kn in (1500.0, 4000.0, 10000.0):
        for rpm in (3000.0, 5000.0):
            rs = [hood_model(rpm, ball, wheel, Contact(delta=d, k_n=kn), dt=2e-5) for d in deltas]
            kw = dict(color=SERIES[i // 2], lw=2, label=f"k_n {kn / 1000:g} N/mm, {rpm:g} rpm",
                      ls="-" if rpm == 3000 else "--")
            axs[0].plot(deltas * 1e3, [r.v_exit for r in rs], **kw)
            axs[1].plot(deltas * 1e3, [r.S for r in rs], **kw)
            axs[2].plot(deltas * 1e3, [r.rpm_drop for r in rs], **kw)
            i += 1
    _style(axs[0], "diametral compression delta [mm]", "v_exit [m/s]", "Hood: exit speed vs compression")
    _style(axs[1], "diametral compression delta [mm]", "S", "S vs compression (r_c = R_b - delta/2)")
    _style(axs[2], "diametral compression delta [mm]", "rpm drop", "RPM drop vs compression")
    axs[0].legend(fontsize=7, frameon=False)
    save(fig, "launcher_compression_sweep.png")

    # 3. S vs hood friction, wraps, feed speed
    mus = np.linspace(0.0, 1.0, 21)
    fig, axs = plt.subplots(1, 2, figsize=(11, 4))
    i = 0
    for wrap in (20.0, 45.0, 90.0):
        for vin, ls in ((0.5, "-"), (4.0, "--")):
            rs = [hood_model(3000, ball, wheel, Contact(mu_top=mu), wrap_deg=wrap, v_in=vin, dt=2e-5) for mu in mus]
            kw = dict(color=SERIES[i // 2], lw=2, ls=ls, label=f"wrap {wrap:g} deg, feed {vin:g} m/s")
            axs[0].plot(mus, [r.S for r in rs], **kw)
            axs[1].plot(mus, [r.v_exit for r in rs], **kw)
            i += 1
    axs[0].axhline(1.0, color=INK2, lw=1, ls=":")
    axs[0].axhline(frictionless_top_limit(ball, effective_radius(ball, Contact())), color=INK2, lw=1, ls=":")
    _style(axs[0], "hood friction mu_hood", "S at exit", "Hood material sets S only for short contact (3000 rpm)")
    _style(axs[1], "hood friction mu_hood", "v_exit [m/s]", "Exit speed")
    axs[0].legend(fontsize=7, frameon=False)
    save(fig, "launcher_S_vs_hood_friction.png")

    # 4. passive roller: S vs inertia and shot sequence
    Is = np.logspace(-6.5, -3.3, 18)
    fig, axs = plt.subplots(1, 2, figsize=(11, 4))
    for i, R_t in enumerate((0.0125, 0.024, 0.05)):
        rs = [roller_model(3000, ball, wheel, Contact(mu_top=0.8), Roller(radius=R_t, inertia=I), dt=2e-5)
              for I in Is]
        axs[0].semilogx(Is, [r.S for r in rs], color=SERIES[i], lw=2, label=f"roller R_t {R_t * 1e3:g} mm, from rest")
    h = hood_model(3000, ball, wheel, Contact()).S
    axs[0].axhline(h, color=INK2, lw=1, ls=":", label=f"fixed hood (nominal) S={h:.3f}")
    _style(axs[0], "roller inertia I_t [kg m^2]", "S at exit", "Passive roller vs hood, 3000 rpm")
    axs[0].legend(fontsize=7, frameon=False)
    k = 0
    for tau, cv, lab in ((5e-4, 1e-6, "nominal bearings"), (0.0, 1e-7, "near-frictionless bearings")):
        for vin in (0.5, 3.0):
            seq = roller_shot_sequence(3000, 6, 0.5, ball, wheel, Contact(mu_top=0.8),
                                       Roller(inertia=1e-5, tau_coulomb=tau, c_visc=cv), v_in=vin, dt=2e-5)
            axs[1].plot(range(1, 7), [r.S for r in seq], color=SERIES[k], lw=2, marker="o", ms=4,
                        label=f"{lab}, feed {vin:g} m/s")
            k += 1
    _style(axs[1], "shot number (0.5 s apart)", "S at exit", "Roller pre-spun by earlier shots (I_t 1e-5)")
    axs[1].legend(fontsize=7, frameon=False)
    save(fig, "launcher_roller.png")

    # 5. achievable (v, spin) clouds
    fig, ax = plt.subplots(figsize=(7, 5))
    for i, (lab, gen) in enumerate((("fixed hood (parameter box)", "hood"),
                                    ("passive roller (parameter box)", "roller"))):
        V, W = [], []
        for rpm in RPM_GRID[::2]:
            if gen == "hood":
                for mu_t in (0.05, 0.3, 1.0):
                    for wrap in (45.0, 90.0, 150.0):
                        for d, kn in ((0.002, 4000.0), (0.004, 4000.0), (0.008, 10000.0), (0.004, 1500.0)):
                            r = hood_model(rpm, ball, wheel, Contact(mu_top=mu_t, delta=d, k_n=kn), wrap_deg=wrap,
                                           dt=2e-5)
                            V.append(r.v_exit)
                            W.append(r.spin_rpm)
            else:
                for I in (2e-6, 1e-5, 2e-4):
                    for R_t in (0.0125, 0.024, 0.05):
                        for d, kn in ((0.004, 4000.0), (0.008, 10000.0)):
                            r = roller_model(rpm, ball, wheel, Contact(mu_top=0.8, delta=d, k_n=kn),
                                             Roller(radius=R_t, inertia=I), dt=2e-5)
                            V.append(r.v_exit)
                            W.append(r.spin_rpm)
        ax.scatter(V, W, s=14, color=SERIES[i], alpha=0.7, edgecolors=SURF, linewidths=0.5, label=lab)
    vv = np.linspace(0, 15, 50)
    for S_, ls in ((1.0, ":"), (1.5, "--")):
        ax.plot(vv, S_ * vv / ball.radius * RAD2RPM, color=INK2, lw=1, ls=ls, label=f"S = {S_:g}")
    _style(ax, "v_exit [m/s]", "backspin [rpm]", "Achievable exit states, wheel 1000-6000 rpm (predicted)")
    ax.legend(fontsize=8, frameon=False)
    save(fig, "launcher_v_spin_map.png")
    return out


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env = build_envelope(os.path.join(root, "data", "launch_envelope.json"))
    print(json.dumps({k: env[k] for k in ("reachable_S_summary", "motor_assist_bounds")}, indent=1))
    print(json.dumps(env["recovery_hood_nominal"]["points"][::4], indent=0))
    for f in make_figures(root, env):
        print("wrote", f)
