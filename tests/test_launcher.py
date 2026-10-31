"""Unit tests for src/launcher.py (single 98 mm flywheel + hood / passive roller)."""
import json
import math
import os
import random
import shutil
import subprocess
import sys
import unittest
from dataclasses import replace

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))

import launcher as L  # noqa: E402

RIGID = dict(lam_radius=0.0, c_rr=0.0, centripetal=False)


class IdealRelations(unittest.TestCase):
    def test_hood_ideal_formula(self):
        v, w = L.hood_ideal(3000.0)
        om = 3000.0 * 2 * math.pi / 60
        self.assertAlmostEqual(v, 0.049 * om / 2, places=12)
        self.assertAlmostEqual(w, v / 0.0355, places=9)
        self.assertAlmostEqual(w * 0.0355 / v, 1.0, places=12)

    def test_ideal_limit_reproduced_by_contact_model(self):
        """mu large, rigid radius, huge flywheel, long hood -> v = R_w Omega/2, S = 1."""
        c = L.Contact(mu_wheel=3.0, mu_top=3.0, delta=0.004, k_n=2e4, **RIGID)
        w = L.Wheel(inertia=10.0)
        r = L.hood_model(3000.0, L.Ball(), w, c, wrap_deg=150.0, v_in=0.0)
        v_id, w_id = L.hood_ideal(r.wheel_rpm_exit)
        self.assertTrue(r.exited)
        self.assertAlmostEqual(r.v_exit / v_id, 1.0, delta=1e-3)
        self.assertAlmostEqual(r.S, 1.0, delta=1e-3)
        self.assertLess(r.rpm_drop, 0.1)

    def test_brettle_rpm_drop(self):
        """Finite flywheel, rolling at exit: Omega_i/Omega_f = 1 + (1+kI) m R_w^2 / (4 I_w)."""
        b = L.Ball()
        w = L.Wheel(inertia=1e-4)
        c = L.Contact(mu_wheel=3.0, mu_top=3.0, delta=0.004, k_n=2e4, **RIGID)
        r = L.hood_model(4000.0, b, w, c, wrap_deg=150.0, v_in=0.0)
        expected = 1 + (1 + b.kI) * b.mass * w.radius ** 2 / (4 * w.inertia)
        self.assertAlmostEqual(L.brettle_ratio(b, w), expected, places=12)
        self.assertAlmostEqual(r.wheel_rpm0 / r.wheel_rpm_exit, expected, delta=2e-4)

    def test_brettle_with_compression_radius_and_feed(self):
        b = L.Ball()
        w = L.Wheel(inertia=1e-4)
        c = L.Contact(mu_wheel=3.0, mu_top=3.0, delta=0.006, k_n=2e4, lam_radius=1.0, c_rr=0.0,
                      centripetal=False)
        r_c = L.effective_radius(b, c)
        r = L.hood_model(3000.0, b, w, c, wrap_deg=150.0, v_in=0.7)
        om_f = L.brettle_omega_f(3000.0 * L.RPM2RAD, b, w, r_c, v_in=0.7)
        self.assertAlmostEqual(r.wheel_rpm_exit * L.RPM2RAD / om_f, 1.0, delta=2e-4)
        self.assertAlmostEqual(r.S, b.radius / r_c, delta=1e-3)   # compression -> S > 1
        self.assertAlmostEqual(r.v_exit, w.radius * om_f / 2, delta=5e-3)


class FrictionLimits(unittest.TestCase):
    def test_zero_wheel_friction_gives_no_launch(self):
        """No wheel friction: the wheel cannot do work; the ball only rolls on the hood with KE <= feed KE."""
        b = L.Ball()
        c = L.Contact(mu_wheel=0.0, mu_top=0.5, c_rr=0.0)
        r = L.hood_model(4000.0, b, L.Wheel(), c, v_in=0.5, t_max=0.05)
        self.assertAlmostEqual(r.rpm_drop, 0.0, delta=1e-9)
        self.assertLessEqual(r.v_exit, 0.5 + 1e-12)
        ke = 0.5 * b.mass * r.v_exit ** 2 + 0.5 * b.inertia * r.spin ** 2
        self.assertLessEqual(ke, 0.5 * b.mass * 0.25 + 1e-12)

    def test_all_friction_zero(self):
        c = L.Contact(mu_wheel=0.0, mu_top=0.0, c_rr=0.0)
        r = L.hood_model(4000.0, L.Ball(), L.Wheel(), c, v_in=1.0)
        self.assertAlmostEqual(r.spin, 0.0, places=12)
        self.assertAlmostEqual(r.v_exit, 1.0, places=12)

    def test_frictionless_hood_gives_S_equal_m_rc_Rb_over_Ib(self):
        """Only wheel friction acts: m dv = F dt, I_b ds = r_c F dt -> S = m r_c R_b / I_b (> 1 for kI < 1)."""
        b = L.Ball()
        c = L.Contact(mu_top=0.0, c_rr=0.0, lam_radius=1.0)
        r = L.hood_model(5000.0, b, L.Wheel(), c, wrap_deg=20.0, v_in=0.0)
        self.assertGreater(r.slip_w_exit, 0.0)  # still slipping: pure single-contact regime
        self.assertAlmostEqual(r.S, L.frictionless_top_limit(b, L.effective_radius(b, c)), delta=1e-6)
        self.assertGreater(r.S, 1.0)

    def test_hood_S_bounds(self):
        """Fixed hood from a slow feed: 1 <= S*(r_c/R_b) <= R_b r_c m / I_b (rolling ... frictionless top)."""
        b = L.Ball()
        for mu_t in (0.0, 0.05, 0.2, 0.6, 1.0):
            for wrap in (20.0, 45.0, 90.0):
                c = L.Contact(mu_top=mu_t, c_rr=0.0)
                r_c = L.effective_radius(b, c)
                r = L.hood_model(3000.0, b, L.Wheel(), c, wrap_deg=wrap, v_in=0.0, dt=2e-5)
                self.assertGreaterEqual(r.S, b.radius / r_c - 1e-6)
                self.assertLessEqual(r.S, L.frictionless_top_limit(b, r_c) + 1e-6)

    def test_grip_limited_speed_independent_of_rpm(self):
        """Wheel slipping through the whole contact: Coulomb force is RPM independent -> same exit state."""
        a = L.hood_model(5000.0)
        b = L.hood_model(6000.0)
        self.assertGreater(a.slip_w_exit, 0.0)
        self.assertAlmostEqual(a.v_exit, b.v_exit, places=9)
        self.assertLess(a.v_exit, L.hood_ideal(a.wheel_rpm_exit)[0])

    def test_centripetal_unloading_flag(self):
        """N_w = N0 - m v^2/(2 rho): a soft ball entering fast lifts off the wheel."""
        c = L.Contact(k_n=500.0)
        r = L.hood_model(6000.0, L.Ball(), L.Wheel(), c, wrap_deg=150.0, v_in=5.0)
        self.assertTrue(r.lost_wheel_contact)
        r2 = L.hood_model(6000.0, L.Ball(), L.Wheel(), L.Contact(), wrap_deg=150.0, v_in=0.5)
        self.assertFalse(r2.lost_wheel_contact)


class Conservation(unittest.TestCase):
    def test_energy_ledger_closes(self):
        for top in (L.Hood(), L.Roller()):
            for motor in (None, L.Motor()):
                r = L.simulate_shot(3500.0, L.Ball(), L.Wheel(motor=motor), L.Contact(mu_top=0.6), top)
                E = r.energy
                scale = E["wheel_ke_loss"] + abs(E["motor_work"])
                self.assertLess(abs(E["balance_residual"]), 1e-9 * scale + 1e-12)
                for k in ("friction_wheel", "friction_top"):
                    self.assertGreaterEqual(E[k], -1e-9)
                self.assertLess(E["ball_ke_gain"], E["wheel_ke_loss"] + E["motor_work"])

    def test_hood_efficiency_below_half(self):
        """Brettle: a hooded shot from rest transfers < 50 % of the wheel KE lost."""
        r = L.hood_model(3000.0, L.Ball(), L.Wheel(), L.Contact(**RIGID), v_in=0.0)
        self.assertLess(r.energy["ball_ke_gain"] / r.energy["wheel_ke_loss"], 0.5)

    def test_generalised_momentum_roller(self):
        """No motor/drag/hysteresis: impulses J_w = -I_w dOm/R_w, J_t = -I_t dOm_t/R_t give two invariants."""
        b, w = L.Ball(), L.Wheel()
        c = L.Contact(mu_top=0.8, c_rr=0.0)
        rol = L.Roller(inertia=1e-5, omega0=30.0, tau_coulomb=0.0, c_visc=0.0)
        v_in = 0.5
        r = L.roller_model(3000.0, b, w, c, rol, v_in=v_in)
        r_c = L.effective_radius(b, c)
        dv, ds = r.v_exit - v_in, r.spin
        dOm = (r.wheel_rpm_exit - r.wheel_rpm0) * L.RPM2RAD
        dOmt = r.roller_omega_exit - rol.omega0
        lin = b.mass * dv + w.inertia * dOm / w.radius + rol.inertia * dOmt / rol.radius
        ang = b.inertia * ds / r_c + w.inertia * dOm / w.radius - rol.inertia * dOmt / rol.radius
        scale = b.mass * r.v_exit
        self.assertLess(abs(lin), 1e-9 * scale + 1e-12)
        self.assertLess(abs(ang), 1e-9 * scale + 1e-12)

    def test_generalised_momentum_hood(self):
        b, w = L.Ball(), L.Wheel()
        c = L.Contact(mu_top=0.3, c_rr=0.0)
        r = L.hood_model(3000.0, b, w, c, v_in=0.5)
        r_c = L.effective_radius(b, c)
        dOm = (r.wheel_rpm_exit - r.wheel_rpm0) * L.RPM2RAD
        val = b.mass * (r.v_exit - 0.5) + b.inertia * r.spin / r_c + 2 * w.inertia * dOm / w.radius
        self.assertLess(abs(val), 1e-9)


class PassiveRoller(unittest.TestCase):
    def test_heavy_roller_rolling_state(self):
        """Huge roller inertia pre-spun forward acts as a moving surface: v=(u_w+u_t)/2, S<1."""
        b = L.Ball()
        c = L.Contact(mu_wheel=3.0, mu_top=3.0, delta=0.008, k_n=2e4, **RIGID)
        rol = L.Roller(inertia=100.0, omega0=100.0, tau_coulomb=0.0, c_visc=0.0)
        w = L.Wheel(inertia=100.0)
        r = L.roller_model(3000.0, b, w, c, rol, v_in=0.05)
        v, s, S = L.roller_rolling_state(w.radius * 3000 * L.RPM2RAD, rol.radius * 100.0, b.radius, b.radius)
        self.assertAlmostEqual(r.v_exit, v, delta=1e-3 * v)
        self.assertAlmostEqual(r.S, S, delta=2e-3)
        self.assertLess(r.S, 1.0)

    def test_heavy_roller_at_rest_matches_fixed_surface(self):
        b = L.Ball()
        c = L.Contact(mu_wheel=3.0, mu_top=3.0, delta=0.008, k_n=2e4, **RIGID)
        r = L.roller_model(3000.0, b, L.Wheel(inertia=100.0), c,
                           L.Roller(inertia=100.0, tau_coulomb=0.0, c_visc=0.0), v_in=0.05)
        self.assertAlmostEqual(r.S, 1.0, delta=2e-3)

    def test_massless_roller_equals_frictionless_top(self):
        b = L.Ball()
        c = L.Contact(mu_top=0.8, c_rr=0.0)
        r = L.roller_model(3000.0, b, L.Wheel(), c, L.Roller(inertia=1e-11, tau_coulomb=0.0, c_visc=0.0),
                           v_in=0.05)
        # from feed v_in with no spin: s r_c = (m r_c^2/I_b)(v - v_in)  ->  S = limit * (v - v_in)/v
        expected = L.frictionless_top_limit(b, L.effective_radius(b, c)) * (r.v_exit - 0.05) / r.v_exit
        self.assertAlmostEqual(r.S, expected, delta=2e-3)

    def test_passive_roller_dragged_backward_from_slow_feed(self):
        """kI < 1: the ball's top point moves backward, so a passive roller is spun with the flywheel's sense."""
        r = L.roller_model(3000.0, L.Ball(), L.Wheel(), L.Contact(mu_top=0.8), L.Roller(), v_in=0.05)
        self.assertLess(r.roller_omega_exit, 0.0)
        self.assertGreater(r.S, 1.0)

    def test_roller_coast_stops_with_coulomb_drag(self):
        rol = L.Roller(inertia=1e-5, tau_coulomb=5e-4, c_visc=0.0)
        self.assertLess(abs(L.roller_coast(-10.0, rol, 1.0)), 1e-3)
        self.assertAlmostEqual(L.roller_coast(-10.0, replace(rol, tau_coulomb=0.0), 1.0), -10.0)


class Solver(unittest.TestCase):
    def test_lcp_complementarity_random(self):
        rng = random.Random(1)
        for _ in range(500):
            a = rng.uniform(0.1, 5.0)
            d = rng.uniform(0.1, 5.0)
            off = rng.uniform(-0.95, 0.95) * math.sqrt(a * d)
            A = ((a, off), (off, d))
            rhs = (rng.uniform(-5, 5), rng.uniform(-5, 5))
            lim = (rng.uniform(0, 3), rng.uniform(0, 3))
            F = L._solve_friction(A, rhs, lim, (True, True))
            res = (rhs[0] - a * F[0] - off * F[1], rhs[1] - off * F[0] - d * F[1])
            for i in range(2):
                self.assertLessEqual(abs(F[i]), lim[i] * (1 + 1e-9) + 1e-12)
                if abs(F[i]) < lim[i] * (1 - 1e-9):
                    self.assertAlmostEqual(res[i], 0.0, delta=1e-9)
                else:
                    self.assertGreaterEqual(res[i] * math.copysign(1, F[i]), -1e-9)


class Envelope(unittest.TestCase):
    def test_run_config_schema(self):
        cfg = L.configurations()
        for name in ("hood_nominal", "roller_nominal_rest"):
            rows = L.run_config(name, cfg[name], rpms=[2000, 4000])
            for row in rows:
                for k in ("wheel_rpm", "v_exit", "spin_rpm", "S", "rpm_drop"):
                    self.assertIn(k, row)
                self.assertGreater(row["v_exit"], 0)
                self.assertGreater(row["S"], 0)

    def test_recovery_time(self):
        w, m = L.Wheel(), L.Motor()
        t = L.recovery_time(200.0, 3000.0, w, m)
        self.assertGreater(t, 0.0)
        self.assertLess(t, 1.0)
        self.assertTrue(math.isinf(L.recovery_time(200.0, 6000.0, w, m)))


class DroopReadout(unittest.TestCase):
    """PM-022: closed-form per-shot droop / recovery readout (launcher.droop_readout) against the contact model
    (hood_model) and against its JS twin (viz/explorer/solver.js droopReadout via tests/js_droop_check.js)."""
    TOL = 0.03   # stated tolerance on the drop vs hood_model; measured on RPM_GRID: +0.9 % to -1.5 % (2026-10-31)

    def test_matches_hood_model_on_rpm_grid(self):
        worst = 0.0
        for rpm in L.RPM_GRID:
            r = L.hood_model(float(rpm))
            d = L.droop_readout(rpm, r.v_exit, r.S)
            err = d["drop_rpm"] / r.rpm_drop - 1.0
            worst = max(worst, abs(err))
            self.assertLess(abs(err), self.TOL, f"{rpm} rpm: closed form {d['drop_rpm']:.1f} vs hood_model {r.rpm_drop:.1f}")
            self.assertAlmostEqual(d["drop_pct"], 100.0 * d["drop_rpm"] / rpm, places=12)
            # contact-time estimate wrap rho / v: never longer than the contact model's, at most 40 % shorter on this grid
            self.assertLessEqual(d["contact_s"], 1.01 * r.contact_time)
            self.assertGreater(d["contact_s"], 0.6 * r.contact_time)
        self.assertLess(worst, 0.02)   # a drift past 2 % should be looked at before the tolerance is touched

    def test_inertia_and_wrap_variants(self):
        """Page inertia range (Advanced clamp 5e-5..1e-3 kg m^2) x the ASSUMED wrap bracket 60-120 deg, 2000-6000 rpm (the
        answer band): measured -1.7 % to +2.1 % (2026-10-31), asserted within TOL. Stated limit, not asserted: below
        2000 rpm a light wheel reads high (1000 rpm: +5 % at 1e-4, +30 % at 5e-5 kg m^2, wrap 90)."""
        for wrap in (60.0, 90.0, 120.0):
            for iw in (5e-5, 1e-4, 5e-4, 1e-3):
                for rpm in (2000, 3000, 4500, 6000):
                    kw = dict(wheel=L.Wheel(inertia=iw), wrap_deg=wrap)
                    r = L.hood_model(float(rpm), **kw)
                    d = L.droop_readout(rpm, r.v_exit, r.S, **kw)
                    self.assertLess(abs(d["drop_rpm"] / r.rpm_drop - 1.0), self.TOL, f"I_w {iw} wrap {wrap} {rpm} rpm")

    def test_impulse_term_is_brettle(self):
        """Rigid radius, no hysteresis, no feed speed, rolling exit: the closed form is Brettle's relation."""
        b, w, c = L.Ball(), L.Wheel(), L.Contact(**RIGID)
        om_i = 3000.0 * L.RPM2RAD
        om_f = L.brettle_omega_f(om_i, b, w)
        d = L.droop_readout(3000.0, w.radius * om_f / 2.0, 1.0, ball=b, wheel=w, contact=c, v_in=0.0)
        self.assertAlmostEqual(d["drop_rpm"], (om_i - om_f) * L.RAD2RPM, places=9)
        self.assertEqual(d["hysteresis_rpm"], 0.0)

    def test_recovery_is_recovery_time(self):
        w = L.Wheel()
        for m in (L.Motor(), L.Motor(voltage_frac=11.0 / 12.0), L.Motor(stall_torque=0.105)):
            for rpm in (2000.0, 3000.0, 4500.0):
                d = L.droop_readout(rpm, 6.5, 1.0, wheel=w, motor=m)
                self.assertEqual(d["recovery_s"], L.recovery_time(d["drop_rpm"], rpm, w, m))
                self.assertGreater(d["recovery_s"], 0.0)
                self.assertAlmostEqual(d["min_interval_s"], d["contact_s"] + d["recovery_s"], places=12)
                self.assertFalse(d["above_free"])
        top = L.droop_readout(6000.0, 8.9, 1.0)   # at the 12 V free speed: never recovers
        self.assertTrue(math.isinf(top["recovery_s"]) and math.isinf(top["min_interval_s"]) and top["above_free"])
        sag = L.droop_readout(5800.0, 8.9, 1.0, motor=L.Motor(voltage_frac=11.0 / 12.0))   # free speed 5500 rpm at 11 V
        self.assertTrue(math.isinf(sag["recovery_s"]) and sag["above_free"])
        self.assertAlmostEqual(sag["free_rpm_loaded"], 5500.0, places=6)

    def test_no_spin_twin(self):
        """The no-spin twin (S = 0) takes no spin from the wheel: smaller drop at the same exit speed, same rolling loss."""
        a, b = L.droop_readout(3000.0, 6.5, 1.0), L.droop_readout(3000.0, 6.5, 0.0)
        self.assertLess(b["drop_rpm"], a["drop_rpm"])
        self.assertEqual(b["hysteresis_rpm"], a["hysteresis_rpm"])
        self.assertLess(b["recovery_s"], a["recovery_s"])

    def test_js_twin_matches_python(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node not installed")
        motors = {"gobilda": L.PARAMS["motor_gobilda_5203_1to1"], "revhd": L.PARAMS["motor_rev_hdhex_bare"]}
        cases, py = [], []
        for name, mp in motors.items():
            for volts in (11.0, 12.0, 13.2):
                for iw in (1e-4, 2.65e-4, 5e-4):
                    for rpm, v, S in ((1500.0, 3.2, 1.0), (2911.0, 6.27, 1.0), (2878.0, 6.2, 0.0), (4200.0, 8.6, 0.6), (5800.0, 8.9, 1.0)):
                        cases.append({"rpm": rpm, "v": v, "S": S, "o": {"motor": name, "Iw": iw, "volts": volts}})
                        m = L.Motor(free_rpm=mp["free_rpm"], stall_torque=mp["stall_torque"], voltage_frac=volts / 12.0)
                        py.append(L.droop_readout(rpm, v, S, wheel=L.Wheel(inertia=iw), motor=m))
        r = subprocess.run([node, os.path.join(HERE, "js_droop_check.js")], input=json.dumps({"cases": cases}),
                           capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        js = json.loads(r.stdout.strip().splitlines()[-1])
        keys = {"drop_rpm": "dropRpm", "drop_pct": "dropPct", "impulse_rpm": "impulseRpm", "hysteresis_rpm": "hystRpm",
                "contact_s": "contactS", "recovery_s": "recoverS", "min_interval_s": "minIntervalS", "free_rpm_loaded": "freeRpmLoaded"}
        worst, n_inf = 0.0, 0
        for c, p, j in zip(cases, py, js["out"]):
            self.assertEqual(p["above_free"], j["aboveFree"], c)
            for pk, jk in keys.items():
                if math.isinf(p[pk]):
                    self.assertIsNone(j[jk], (c, pk))   # JSON has no Infinity: the JS twin's Infinity prints as null
                    n_inf += 1
                    continue
                worst = max(worst, abs(j[jk] - p[pk]) / max(abs(p[pk]), 1e-12))
        self.assertGreater(n_inf, 0)   # the set includes rpm above the free speed at 11 V
        self.assertLessEqual(worst, 0.01)
        # the JS defaults are the launcher defaults (twin constants stay aligned)
        D, b, w, c = js["defaults"], L.Ball(), L.Wheel(), L.Contact()
        for jk, val in (("m", b.mass), ("Rb", b.radius), ("kI", b.kI), ("Rw", w.radius), ("Iw", w.inertia), ("delta", c.delta),
                        ("kn", c.k_n), ("lam", c.lam_radius), ("crr", c.c_rr), ("wrapDeg", L.PARAMS["wrap_deg"]["value"]),
                        ("vIn", L.PARAMS["v_in"]["value"])):
            self.assertEqual(D[jk], val, jk)
        for name, mp in motors.items():
            self.assertEqual((D["motors"][name]["freeRpm"], D["motors"][name]["stall"]), (mp["free_rpm"], mp["stall_torque"]))


if __name__ == "__main__":
    unittest.main()
