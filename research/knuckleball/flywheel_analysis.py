"""Flywheel launch envelope for the knuckleball study (72 vs 98 mm wheels, 3000-8000 rpm).

usage: python -B research/knuckleball/flywheel_analysis.py [out.json]

Uses the repo's contact model (src/launcher.py, PREDICTED; contact stiffness and friction are ASSUMED, see
docs/04_launcher.md). Configurations:
  hood  : one powered wheel + fixed concentric hood (wrap 90 deg), compression 4 mm and 8 mm.
  dual  : two opposing powered wheels of the same size. Modelled as launcher.Roller with the second wheel's radius,
          inertia and speed, bearing drag 0 and the same friction as the main wheel. Speed ratios 1.00 / 0.95 / 0.90 /
          0.80 (second wheel / first wheel).
Each row: ball exit speed v, spin, S = omega R / v, Re = rho v D / mu, wheel rpm drop, energy transfer efficiency
(ball KE gain / (wheel KE loss + motor work)), slip at exit, the motor recovery time to restore the drop, and the
rim hoop stress of a thin ring rho_rim (omega R)^2.
"""
import json
import math
import os
import sys
from dataclasses import replace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
import launcher as L  # noqa: E402

RHO_AIR, MU_AIR = 1.204, 1.81e-5        # ASSUMED 20 C sea-level air
BALL = L.Ball(mass=0.02495, radius=0.03556, kI=0.63)   # mass AndyMark 0.055 lb; R and kI from CAD
D_BALL = 2 * BALL.radius
RHO_TREAD = 1200.0                      # ASSUMED TPU/urethane tread density, kg/m^3

# wheel sets (radius, inertia).  Inertia = wheel (0.6 m R^2, ASSUMED distribution) + optional goBILDA steel flywheel
# (published: 60 mm 551 g cm^2, 82 mm 1651 g cm^2).  Wheel masses: Gecko 72 mm 52 g, Gecko 96 mm 105 g (vendor pages).
WHEELS = {
    "72mm": {"R": 0.036, "I_bare": 0.6 * 0.052 * 0.036 ** 2, "I_fly": 0.6 * 0.052 * 0.036 ** 2 + 5.51e-5},
    "98mm": {"R": 0.049, "I_bare": 0.6 * 0.105 * 0.049 ** 2, "I_fly": 0.6 * 0.105 * 0.049 ** 2 + 1.651e-4},
}
RPMS = [3000, 4000, 5000, 6000, 7000, 8000]
GEARS = {"direct": 1.0, "overdrive_1.5": 1.0 / 1.5}   # motor rev / wheel rev
MOTOR = dict(free_rpm=6000.0, stall_torque=0.144)     # goBILDA 5203 1:1 (vendor)


def motor_for(rpm, n_motors):
    """Pick the gearing: direct if the wheel speed is below 85 % of free speed, else 1.5x overdrive."""
    for name, g in GEARS.items():
        if rpm <= 0.85 * MOTOR["free_rpm"] / g:
            return name, L.Motor(free_rpm=MOTOR["free_rpm"], stall_torque=MOTOR["stall_torque"] * n_motors, gear=g)
    return None, None


def row(cfg, wheel_key, rpm, inertia_kind, res, wheel, motor_name, motor, extra):
    v = res.v_exit
    e = res.energy
    inp = e["wheel_ke_loss"] + e["motor_work"] + extra.get("second_ke_loss", 0.0)
    rec = {}
    if motor is not None:
        for n in (1, 2):
            m = replace(motor, stall_torque=MOTOR["stall_torque"] * n * 1.0)
            rec["recovery_s_%dmotor" % n] = L.recovery_time(res.rpm_drop, rpm, wheel, m)
    vs = math.pi * 2 * wheel.radius * rpm / 60
    return dict(cfg=cfg, wheel=wheel_key, inertia=inertia_kind, rpm=rpm, v_surface=vs, v_exit=v,
                spin_rpm=res.spin_rpm, S=res.S, Re=RHO_AIR * v * D_BALL / MU_AIR, v_over_vs=v / vs,
                rpm_drop=res.rpm_drop, eff=(e["ball_ke_gain"] / inp if inp > 0 else float("nan")),
                slip_w=res.slip_w_exit, slip_t=res.slip_t_exit, exited=res.exited,
                lost_contact=res.lost_wheel_contact, gearing=motor_name,
                hoop_MPa=RHO_TREAD * vs ** 2 / 1e6, **rec, **extra)


def main():
    rows = []
    for wk, w in WHEELS.items():
        for ik in ("I_fly", "I_bare"):
            for rpm in RPMS:
                mname, motor = motor_for(rpm, 1)
                wheel = L.Wheel(radius=w["R"], inertia=w[ik], motor=motor)
                for delta in (0.004, 0.008):
                    c = L.Contact(delta=delta)
                    res = L.hood_model(rpm, BALL, wheel, c, wrap_deg=90.0)
                    rows.append(row("hood_d%dmm" % round(delta * 1e3), wk, rpm, ik, res, wheel, mname, motor, {}))
                for ratio in (1.0, 0.95, 0.9, 0.8):
                    c = L.Contact(delta=0.004, mu_top=0.8)
                    om2 = rpm * ratio * L.RPM2RAD
                    top = L.Roller(radius=w["R"], inertia=w[ik], omega0=om2, tau_coulomb=0.0, c_visc=0.0)
                    res = L.roller_model(rpm, BALL, wheel, c, top)
                    loss2 = 0.5 * w[ik] * (om2 ** 2 - res.roller_omega_exit ** 2)
                    rows.append(row("dual_r%.2f" % ratio, wk, rpm, ik, res, wheel, mname, motor,
                                    {"ratio": ratio, "second_ke_loss": loss2,
                                     "S_ideal": (1 - ratio) / (1 + ratio)}))
    print("%-10s %-5s %-6s %5s %5s %6s %7s %6s %6s %6s %5s %6s %6s" % (
        "cfg", "wheel", "I", "rpm", "vs", "v", "spinrpm", "S", "Re/1e3", "drop", "eff", "rec1", "rec2"))
    for r in rows:
        print("%-10s %-5s %-6s %5d %5.1f %6.2f %7.0f %6.3f %6.1f %6.0f %5.2f %6.3f %6.3f" % (
            r["cfg"], r["wheel"], r["inertia"], r["rpm"], r["v_surface"], r["v_exit"], r["spin_rpm"], r["S"],
            r["Re"] / 1e3, r["rpm_drop"], r["eff"], r.get("recovery_s_1motor", float("nan")),
            r.get("recovery_s_2motor", float("nan"))))
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        with open(sys.argv[1], "w") as fh:
            json.dump(rows, fh, indent=1)


if __name__ == "__main__":
    main()


def needed_speed(x, h, theta_deg, cd=0.62, m=0.02495, D=0.07112, g=9.81, dt=1e-4):
    """Launch speed that reaches horizontal distance x at height h above the launch point (with quadratic drag,
    Cd ~0.62 from the CFD, PREDICTED; no lift, i.e. the no-spin twin). Bisection on v."""
    k = 0.5 * RHO_AIR * cd * math.pi * D * D / 4 / m
    th = math.radians(theta_deg)

    def height_at_x(v):
        vx, vz, px, pz, t = v * math.cos(th), v * math.sin(th), 0.0, 0.0, 0.0
        while px < x:
            sp = math.hypot(vx, vz)
            vx -= k * sp * vx * dt
            vz -= (g + k * sp * vz) * dt
            px += vx * dt
            pz += vz * dt
            t += dt
            if t > 5 or (vz < 0 and pz < h - 2):
                return -1e9, t
        return pz, t

    lo, hi = 1.0, 30.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if height_at_x(mid)[0] < h:
            lo = mid
        else:
            hi = mid
    return hi, height_at_x(hi)[1]


def needed_table():
    print("\nneeded launch speed (no-spin twin, Cd 0.62), target height above launch h, launch angle 45/55/65 deg")
    for x in (1.0, 2.0, 3.0, 4.0):
        for h in (0.7, 1.0):
            cells = []
            for a in (45, 55, 65):
                v, t = needed_speed(x, h, a)
                cells.append("%2d deg: %5.2f m/s t=%.2f s Re=%5.0f" % (a, v, t, RHO_AIR * v * D_BALL / MU_AIR))
            print("x=%.0f m h=%.1f m | %s" % (x, h, " | ".join(cells)))


if __name__ == "__main__" and "--needed" in sys.argv:
    needed_table()
