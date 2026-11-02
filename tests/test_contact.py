"""Unit tests for src/contact.py (spin-assisted contact entry, hypothesis B)."""
import math
import os
import sys
import types
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import contact as ct  # noqa: E402
from src import flight as fl  # noqa: E402

BP = ct.ball_props()
M, R, I, ALPHA = BP["mass"], BP["radius"], BP["I_b"], BP["alpha"]


def energy(v, w):
    v = np.asarray(v, float)
    return 0.5 * M * float(v @ v) + 0.5 * I * w * w


def plane_geometry(theta_deg, length=4.0):
    """ContactGeometry with one long incline through (0, 2), descending toward +x."""
    th = math.radians(theta_deg)
    d = np.array([math.cos(th), -math.sin(th)])
    O = np.array([0.0, 2.0])               # well above every termination height
    A = np.array([O - 0.5 * length * d])
    B = np.array([O + 0.5 * length * d])
    hive = types.SimpleNamespace(normal_out=np.array([0.0, 1.0]))
    far = np.array([[50.0, 50.0], [51.0, 50.0], [51.0, 51.0], [50.0, 51.0]])
    g = ct.ContactGeometry(hive=hive, A=A, B=B, names=["incline"], R=R, cell_poly=far,
                           z_barrier=-1e9, near_rim=0, far_rim=0,
                           bbox=(-10.0, 10.0, -10.0, 10.0))
    return g, d, np.array([math.sin(th), math.cos(th)])


class TestImpactLaw(unittest.TestCase):
    def test_energy_never_increases_random(self):
        rng = np.random.default_rng(1)
        for _ in range(4000):
            a = rng.uniform(0, 2 * math.pi)
            n = np.array([math.cos(a), math.sin(a)])
            v = rng.normal(0, 4, 2)
            w = rng.normal(0, 300)
            e, mu, e_t = rng.uniform(0, 1), rng.uniform(0, 1.5), rng.uniform(0, 1)
            v2, w2, info = ct.impact(v, w, n, M, R, I, e, mu, e_t)
            self.assertLessEqual(energy(v2, w2), energy(v, w) * (1 + 1e-12) + 1e-15)

    def test_energy_never_increases_batch_and_regimes(self):
        rng = np.random.default_rng(2)
        N = 20000
        a = rng.uniform(0, 2 * math.pi, N)
        n = np.stack([np.cos(a), np.sin(a)], 1)
        v = rng.normal(0, 4, (N, 2))
        w = rng.normal(0, 300, N)
        e = rng.uniform(0.3, 0.8, N)
        mu = rng.uniform(0.2, 0.8, N)
        v2, w2, info = ct.impact_batch(v, w, n, M, R, I, e, mu)
        E0 = 0.5 * M * np.sum(v * v, 1) + 0.5 * I * w * w
        E1 = 0.5 * M * np.sum(v2 * v2, 1) + 0.5 * I * w2 * w2
        self.assertTrue(np.all(E1 <= E0 * (1 + 1e-12) + 1e-15))
        reg = info["regime"]
        self.assertGreater(np.sum(reg == "stick"), 100)
        self.assertGreater(np.sum(reg == "slip"), 100)
        # restitution: normal velocity after = -e * before for approaching contacts
        app = np.sum(v * n, 1) < 0
        vn2 = np.sum(v2 * n, 1)
        np.testing.assert_allclose(vn2[app], -e[app] * np.sum(v * n, 1)[app], atol=1e-12)
        # separating contacts unchanged
        np.testing.assert_array_equal(v2[~app], v[~app])

    def test_mu_zero_leaves_spin_unchanged(self):
        rng = np.random.default_rng(3)
        for _ in range(500):
            a = rng.uniform(0, 2 * math.pi)
            n = np.array([math.cos(a), math.sin(a)])
            v = rng.normal(0, 4, 2)
            w = rng.normal(0, 300)
            v2, w2, info = ct.impact(v, w, n, M, R, I, rng.uniform(0, 1), 0.0)
            self.assertEqual(w2, w)
            # and the tangential velocity is unchanged
            t = np.array([n[1], -n[0]])
            self.assertAlmostEqual(float(v2 @ t), float(v @ t), places=12)

    def test_rolling_contact_limit(self):
        n = np.array([0.0, 1.0])            # floor, tangent t = (1, 0)
        vx = 2.0
        # already rolling (+x on a floor is w = +vx/R): no tangential impulse at any mu
        for mu in (0.1, 0.5, 2.0):
            v2, w2, info = ct.impact([vx, -0.5], vx / R, n, M, R, I, 0.5, mu)
            self.assertAlmostEqual(info["P_t"], 0.0, places=14)
            self.assertAlmostEqual(v2[0], vx, places=12)
            self.assertAlmostEqual(w2, vx / R, places=9)
        # non-spinning ball that grips (high mu, e_t = 0): ends exactly at rolling,
        # v_t' = v_t / (1 + alpha)  (5/7 for a solid sphere; here alpha = 0.63)
        v2, w2, info = ct.impact([vx, -1.0], 0.0, n, M, R, I, 0.5, 5.0)
        self.assertEqual(info["regime"], "stick")
        self.assertAlmostEqual(v2[0], vx / (1 + ALPHA), places=12)
        self.assertAlmostEqual(v2[0] - R * w2, 0.0, places=12)
        # solid-sphere check of the same formula
        Is = 0.4 * M * R * R
        v2s, w2s, _ = ct.impact([vx, -1.0], 0.0, n, M, R, Is, 0.5, 5.0)
        self.assertAlmostEqual(v2s[0], vx * 5.0 / 7.0, places=12)
        # low mu: slides through, |slip| reduced but sign kept, Coulomb impulse = mu P_n
        v2, w2, info = ct.impact([vx, -1.0], 0.0, n, M, R, I, 0.5, 0.05)
        self.assertEqual(info["regime"], "slip")
        self.assertAlmostEqual(abs(info["P_t"]), 0.05 * info["P_n"], places=14)
        self.assertGreater(v2[0] - R * w2, 0.0)

    def test_incline_rolling_and_sliding(self):
        """Resting contact by micro-impulses: rolling a = g sin(th)/(1+alpha); mu=0: g sin(th)."""
        th = 15.0
        geom, d, n = plane_geometry(th)
        ap = ct.aero_case(Cl=None, Cd=0.0)
        T = 0.4
        for mu, a_exp in ((0.8, ct.G * math.sin(math.radians(th)) / (1 + ALPHA)),
                          (0.0, ct.G * math.sin(math.radians(th)))):
            p0 = np.array([0.0, 2.0]) + (R + 1e-5) * n
            Y0 = np.array([[p0[0], p0[1], 0.0, 0.0, 0.0]])
            o = ct.simulate_batch(Y0, geom, ap, ct.ContactParams(e=0.5, mu=mu), I, t_max=T,
                                  z_stop=-100.0)
            Y = o["Y_end"][0]
            s = float((Y[:2] - p0) @ d)
            a_meas = 2 * s / T ** 2
            self.assertAlmostEqual(a_meas / a_exp, 1.0, delta=0.03, msg=f"mu={mu}")
            if mu > 0:
                # rolling: contact-point slip ~ 0 (w = +v/R along the slope)
                vt = float(Y[2:4] @ d)
                self.assertAlmostEqual((vt - R * Y[4]) / max(vt, 1e-9), 0.0, delta=0.05)
            else:
                self.assertEqual(Y[4], 0.0)


class TestSpinKickSign(unittest.TestCase):
    """Sign of the spin-induced tangential kick at each rim, on the real lip corners."""

    @classmethod
    def setUpClass(cls):
        cls.geom = ct.ContactGeometry.unfavourable()
        cls.d_in = -cls.geom.hive.normal_out

    def _kick(self, corner, n, phi=75.0, v=5.0, S=1.0, mu=0.6, e=0.6):
        vel = np.array([v * math.cos(math.radians(phi)), -v * math.sin(math.radians(phi))])
        c = np.asarray(corner) + R * n
        dist, j, q = self.geom.nearest(c[None])
        v0, w0, i0 = ct.impact(vel, 0.0, n, M, R, I, e, mu)
        v1, w1, i1 = ct.impact(vel, -S * v / R, n, M, R, I, e, mu)
        return v1 - v0, j[0], q[0], i0, i1

    def test_far_rim_backspin_kicks_into_cell(self):
        g = self.geom
        corner = g.A[g.far_rim] if g.A[g.far_rim][1] > g.B[g.far_rim][1] else g.B[g.far_rim]
        # the corner's normal cone spans the floor normal (c = 30 deg) to the lip face normal (c = -60)
        for c_deg in (-20.0, 0.0, 15.0, 29.0):
            c = math.radians(c_deg)
            n = np.array([-math.sin(c), math.cos(c)])
            dv, j, q, i0, i1 = self._kick(corner, n)
            self.assertLess(np.linalg.norm(q - corner), 1e-4)
            self.assertGreater(float(dv @ self.d_in), 0.0, msg=f"c={c_deg}")
            # direction is exactly the derived k = (-n_z, n_x)
            k = ct.spin_kick_direction(n)
            self.assertAlmostEqual(float(dv @ k) / np.linalg.norm(dv), 1.0, places=9)
        # at c = 30 deg (centre on the gate's low end) the kick is along the CELL axis itself
        n30 = np.array([-0.5, math.sqrt(3) / 2])
        np.testing.assert_allclose(ct.spin_kick_direction(n30), self.d_in, atol=2e-4)

    def test_near_rim_backspin_kicks_away_from_mouth(self):
        g = self.geom
        A, B = g.A[g.near_rim], g.B[g.near_rim]
        corner = A if A[1] > B[1] else B          # top/outer corner of the roof end
        for a_deg in (10.0, 25.0, 40.0):
            a = math.radians(a_deg)
            n = np.array([-math.sin(a), math.cos(a)])
            t_fwd = np.array([math.cos(a), math.sin(a)])    # "over the edge" toward the mouth side
            dv, j, q, i0, i1 = self._kick(corner, n)
            self.assertLess(float(dv @ t_fwd), 0.0, msg=f"a={a_deg}")
            self.assertLess(dv[0], 0.0)             # held back toward the shooter / over the roof
        # the mouth is on the +x side of the near-rim corner
        self.assertGreater(float(np.mean(g.hive.gate[:, 0])), corner[0])

    def test_no_kick_when_both_slide_same_way(self):
        # glancing fast contact at low mu: both cases slide in the same direction -> identical
        n = np.array([-math.sin(math.radians(60)), math.cos(math.radians(60))])
        vel = np.array([5.0 * math.cos(math.radians(80)), -5.0 * math.sin(math.radians(80))])
        v0, w0, i0 = ct.impact(vel, 0.0, n, M, R, I, 0.6, 0.05)
        v1, w1, i1 = ct.impact(vel, -1.0 * 5.0 / R, n, M, R, I, 0.6, 0.05)
        self.assertEqual(i0["regime"], "slip")
        self.assertEqual(i1["regime"], "slip")
        if np.sign(i0["v_ct"]) == np.sign(i1["v_ct"]):
            np.testing.assert_allclose(v1, v0, atol=1e-12)


class TestFlightAndOutcome(unittest.TestCase):
    def test_rk4_matches_flight_simulate(self):
        p = fl.load_params(which="nominal")
        ap = ct.aero_case("nominal", "nominal", "nominal")
        v, th, S = 7.0, 78.0, 1.0
        v0 = np.array([v * math.cos(math.radians(th)), 0.0, v * math.sin(math.radians(th))])
        w = -S * v / R
        T = 0.8
        tr = fl.simulate([-0.8, 0.0, 0.737], v0, [0.0, w, 0.0], p, t_max=T, z_ground=None)
        Y = ct.free_flight(ap, np.array([-0.8, 0.737, v0[0], v0[2], w]), T, dt=1e-3)[0]
        self.assertAlmostEqual(Y[0], tr.pos[-1, 0], delta=2e-6)
        self.assertAlmostEqual(Y[1], tr.pos[-1, 2], delta=2e-6)
        self.assertAlmostEqual(Y[4], tr.omega[-1, 1], delta=1e-6 * abs(w))

    def test_backward_then_forward_free_flight(self):
        ap = ct.aero_case("high")
        Y = np.array([[0.4, 1.5, 1.0, -4.5, -120.0]])
        Yb = ct.free_flight(ap, Y, -0.1)
        Yf = ct.free_flight(ap, Yb, 0.1)
        np.testing.assert_allclose(Yf, Y, atol=1e-8)

    def test_full_sim_energy_non_increasing(self):
        geom = ct.ContactGeometry.unfavourable()
        ap = ct.aero_case(Cl=None, Cd=0.0)
        rng = np.random.default_rng(5)
        N = 300
        s = rng.uniform(-0.08, 0.4, N)
        phi = rng.uniform(62, 88, N)
        Y0 = ct.incidence_states(geom, ap, s, phi, np.full(N, 5.0), rng.uniform(0, 2, N))
        o = ct.simulate_batch(Y0, geom, ap, ct.ContactParams(e=0.8, mu=0.6), I, t_max=1.0)

        def E(Y):
            return Y[:, 1] + (Y[:, 2] ** 2 + Y[:, 3] ** 2) / (2 * ct.G) + I * Y[:, 4] ** 2 / (2 * M * ct.G)
        ok = o["t_end"] > 0
        self.assertTrue(np.all(E(o["Y_end"][ok]) <= E(Y0[ok]) + 1e-6))
        self.assertGreater(int(np.sum(o["n_contacts"] > 0)), 50)

    def test_trapped_and_outcomes(self):
        geom = ct.ContactGeometry.unfavourable()
        ap = ct.aero_case()
        c = np.mean(geom.hive.inside, axis=0)
        # at rest inside the CELL: trapped immediately, counted as clean (no contact)
        r = ct.simulate_one(c, (0.0, 0.0), 0.0, geom=geom, ap=ap)
        self.assertEqual(r["outcome_name"], "retained_clean")
        # ball thrown hard out of the CELL along the mouth normal: leaves, not retained
        vout = 6.0 * geom.hive.normal_out
        r = ct.simulate_one(c, vout, 0.0, geom=geom, ap=ap)
        self.assertEqual(r["outcome_name"], "bounced_out")
        # ball far from the HIVE: miss
        r = ct.simulate_one((-1.0, 1.0), (0.0, 1.0), 0.0, geom=geom, ap=ap)
        self.assertEqual(r["outcome_name"], "miss")
        # barrier = gate low end, conservative versus the lower-lip crest
        self.assertAlmostEqual(geom.z_barrier, float(geom.hive.gate[0][1]), places=12)
        lip = max(geom.A[geom.far_rim][1], geom.B[geom.far_rim][1]) + R
        self.assertLessEqual(geom.z_barrier, lip + 1e-9)

    def test_landing_on_roof_is_blocked_or_bounces(self):
        geom = ct.ContactGeometry.unfavourable()
        ap = ct.aero_case()
        # dropped onto the outer roof well behind the near rim: never enters
        A, B = geom.A[geom.near_rim], geom.B[geom.near_rim]
        corner = A if A[1] > B[1] else B
        r = ct.simulate_one((corner[0] - 0.12, corner[1] + 0.3), (0.0, -1.0), 0.0, geom=geom, ap=ap)
        self.assertIn(r["outcome_name"], ("blocked",))
        self.assertGreater(r["n_contacts"], 0)
        self.assertEqual(ct.ZONES[r["first_zone"]], "external")


if __name__ == "__main__":
    unittest.main()
