import math
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import flight as fl  # noqa: E402
from src import robustness as rb  # noqa: E402

PRM = dict(rho=1.2, mass=0.025, radius=0.0355, Cd=0.5, c1=0.35, clmax=0.25, k=0.03)


def launch(v, th_deg, psi_deg=0.0, S=1.0, n=1):
    th, psi = math.radians(th_deg), math.radians(psi_deg)
    v0 = np.array([[v * math.cos(th) * math.cos(psi), v * math.cos(th) * math.sin(psi),
                    v * math.sin(th)]] * n)
    w0 = rb.backspin_axis(v0) * (S * v / PRM["radius"])
    return np.zeros((n, 3)) + [0.0, 0.0, 0.5], v0, w0


class TestIntegrate3d(unittest.TestCase):
    def test_matches_flight_simulate(self):
        # same drag + capped Magnus + spin decay as the reference adaptive integrator
        p0, v0, w0 = launch(8.0, 75.0, S=1.0)
        tr = rb.integrate3d(p0, v0, w0, PRM, dt=1e-3, t_max=1.2, z_stop=-1.0)
        ref = fl.simulate(p0[0], v0[0], w0[0],
                          dict(rho=PRM["rho"], mass=PRM["mass"], radius=PRM["radius"],
                               Cd=PRM["Cd"], Cl=(PRM["c1"], PRM["clmax"]),
                               spin_decay_k=PRM["k"]), t_max=1.2, z_ground=None)
        for t in (0.3, 0.8, 1.2):
            i = int(round(t / 1e-3))
            j = int(np.argmin(abs(ref.t - t)))
            self.assertLess(abs(ref.t[j] - t), 1e-3)
            np.testing.assert_allclose(tr["P"][0, i], ref.pos[j], atol=2e-3)

    def test_backspin_lifts(self):
        p0, v0, w0 = launch(8.0, 70.0, S=1.0)
        spin = rb.integrate3d(p0, v0, w0, PRM, t_max=0.6, z_stop=-1.0)
        flat = rb.integrate3d(p0, v0, w0 * 0.0, PRM, t_max=0.6, z_stop=-1.0)
        self.assertGreater(spin["P"][0, -1, 2], flat["P"][0, -1, 2] + 0.01)
        # backspin on a +x shot also pulls it back (lift is perpendicular to v, tilted toward -x)
        self.assertLess(spin["P"][0, -1, 0], flat["P"][0, -1, 0])

    def test_cos_psi_projection(self):
        # no wind: the 3D path at azimuth psi, projected on x, is the psi = 0 path with its
        # horizontal coordinate scaled by cos(psi); height is unchanged (docs/06 field map)
        for psi in (15.0, 35.0):
            p0, v0, w0 = launch(8.0, 75.0, 0.0, S=1.0, n=2)
            q0, u0, s0 = launch(8.0, 75.0, psi, S=1.0)
            p0[1], v0[1], w0[1] = q0[0], u0[0], s0[0]
            tr = rb.integrate3d(p0, v0, w0, PRM, t_max=1.0, z_stop=-1.0)
            P = tr["P"].astype(float)
            c = math.cos(math.radians(psi))
            np.testing.assert_allclose(P[1, :, 0], P[0, :, 0] * c, atol=1e-5)
            np.testing.assert_allclose(P[1, :, 1], P[0, :, 0] * math.sin(math.radians(psi)),
                                       atol=1e-5)
            np.testing.assert_allclose(P[1, :, 2], P[0, :, 2], atol=1e-5)


class TestHelpers(unittest.TestCase):
    def test_backspin_axis(self):
        ax = rb.backspin_axis(np.array([[1.0, 0.0, 1.0], [-2.0, 0.0, 0.5]]))
        np.testing.assert_allclose(ax, [[0, -1, 0], [0, 1, 0]], atol=1e-12)

    def test_wilson(self):
        lo, hi = rb.wilson(0, 10)
        self.assertEqual(lo, 0.0)
        self.assertAlmostEqual(hi, 0.2775, places=3)
        lo, hi = rb.wilson(5, 10)
        self.assertAlmostEqual(lo + hi, 1.0, places=9)
        self.assertEqual(rb.wilson(0, 0), (0.0, 1.0))

    def test_scenarios_have_nospin_twin(self):
        sc = rb.mc_scenarios()
        self.assertEqual(sc["nospin_twin"], {"Cl": "none"})
        self.assertEqual(sc["Cl_floor_transfer"], {"Cl": "floor"})


class TestAeroPath(unittest.TestCase):
    def test_set_aero_path(self):
        old, env = fl.AERO_PARAMS_PATH, os.environ.get("PM001_AERO_PATH")
        try:
            fl.set_aero_path(fl.LIT_PARAMS_PATH)
            self.assertEqual(fl.aero_tag(), "params_lit")
            self.assertEqual(os.environ["PM001_AERO_PATH"], fl.AERO_PARAMS_PATH)
            self.assertIn("floor", rb._aero_raw()["Cl"]["sets"])
            self.assertAlmostEqual(fl.load_params(which="high")["Cd"], 0.9)
        finally:
            fl.AERO_PARAMS_PATH = old
            if env is None:
                os.environ.pop("PM001_AERO_PATH", None)
            else:
                os.environ["PM001_AERO_PATH"] = env


if __name__ == "__main__":
    unittest.main()
