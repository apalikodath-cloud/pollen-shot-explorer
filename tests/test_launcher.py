"""Unit tests for src/launcher.py (single 98 mm flywheel + hood / passive roller)."""
import math
import os
import random
import sys
import unittest
from dataclasses import replace

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

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


if __name__ == "__main__":
    unittest.main()
