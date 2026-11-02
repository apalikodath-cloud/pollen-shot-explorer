"""Unit tests for src/flight.py (free-flight solver). Run from repo root:
    python -m unittest discover -s tests -v
"""
import json
import math
import os
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import flight as fl  # noqa: E402

G = fl.G_STANDARD
BASE = {"rho": 1.225, "mass": 0.025, "radius": 0.0355, "Cd": 0.5, "Cl": (0.25, 0.4),
        "spin_decay_k": 0.0}
VACUUM = {"rho": 0.0, "mass": 0.025, "radius": 0.0355, "Cd": 0.5, "Cl": None,
          "spin_decay_k": 0.0}


def launch(speed, elev_deg, sign=+1):
    a = math.radians(elev_deg)
    return np.array([sign * speed * math.cos(a), 0.0, speed * math.sin(a)])


def analytic(h, v0):
    vx, vz = v0[0], v0[2]
    t_apex = vz / G
    x_apex = vx * t_apex
    z_apex = h + vz * vz / (2 * G)
    t_land = (vz + math.sqrt(vz * vz + 2 * G * h)) / G
    return x_apex, z_apex, t_apex, vx * t_land, t_land


def mech_energy(tr, m=0.025):
    return 0.5 * m * np.sum(tr.vel ** 2, axis=1) + m * G * tr.pos[:, 2]


class TestVacuum(unittest.TestCase):
    def test_vacuum_matches_analytic(self):
        for (speed, elev, sign, h) in [(6.0, 60.0, +1, 0.30), (8.0, 35.0, +1, 0.45),
                                       (5.0, 75.0, -1, 0.25)]:
            v0 = launch(speed, elev, sign)
            tr = fl.simulate([0, 0, h], v0, fl.backspin_omega(v0, 400.0), VACUUM)
            xa, za, ta, xr, tl = analytic(h, v0)
            ap = tr.apex()
            self.assertEqual(tr.termination, "ground")
            self.assertAlmostEqual(ap["x"], xa, delta=1e-6)
            self.assertAlmostEqual(ap["z"], za, delta=1e-6)
            self.assertAlmostEqual(ap["t"], ta, delta=1e-7)
            self.assertAlmostEqual(tr.pos[-1, 0], xr, delta=1e-6)
            self.assertAlmostEqual(tr.pos[-1, 2], 0.0, delta=1e-9)
            self.assertAlmostEqual(tr.t[-1], tl, delta=1e-7)
            self.assertAlmostEqual(tr.pos[-1, 1], 0.0, delta=1e-12)

    def test_cd_zero_equals_vacuum(self):
        v0 = launch(7.0, 55.0)
        p = dict(BASE, Cd=0.0, Cl=None)
        a = fl.simulate([0, 0, 0.3], v0, [0, 0, 0], p)
        b = fl.simulate([0, 0, 0.3], v0, [0, 0, 0], VACUUM)
        np.testing.assert_allclose(a.t, b.t, atol=1e-12)
        np.testing.assert_allclose(a.pos, b.pos, atol=1e-12)
        xa, za, ta, xr, tl = analytic(0.3, v0)
        self.assertAlmostEqual(a.pos[-1, 0], xr, delta=1e-6)
        self.assertAlmostEqual(a.apex()["z"], za, delta=1e-6)


class TestSigns(unittest.TestCase):
    def test_backspin_vector(self):
        np.testing.assert_allclose(fl.backspin_omega([1, 0, 0], 10.0), [0, -10, 0], atol=1e-12)
        np.testing.assert_allclose(fl.backspin_omega([-1, 0, 0], 10.0), [0, 10, 0], atol=1e-12)
        np.testing.assert_allclose(fl.backspin_omega([3, 0, 4], 10.0), [0, -10, 0], atol=1e-12)
        with self.assertRaises(ValueError):
            fl.backspin_omega([0, 0, 1], 10.0)

    def test_backspin_lift_up_both_directions(self):
        for sign in (+1, -1):
            v = np.array([sign * 5.0, 0.0, 0.0])
            f = fl.aero_forces(v, fl.backspin_omega(v, 200.0), BASE)
            fm = f["F_magnus"]
            self.assertGreater(fm[2], 0.0)
            self.assertAlmostEqual(fm[0], 0.0, delta=1e-15)
            self.assertAlmostEqual(fm[1], 0.0, delta=1e-15)
            # drag opposes motion
            self.assertLess(f["F_drag"][0] * sign, 0.0)
        # topspin pushes down
        v = np.array([5.0, 0, 0])
        self.assertLess(fl.aero_forces(v, fl.backspin_omega(v, -200.0), BASE)["F_magnus"][2], 0)

    def test_ascent_rearward_descent_forward(self):
        for sign in (+1, -1):
            w = fl.backspin_omega([sign, 0, 0], 250.0)
            up = fl.aero_forces([sign * 5.0, 0, 3.0], w, BASE)["F_magnus"]
            dn = fl.aero_forces([sign * 5.0, 0, -3.0], w, BASE)["F_magnus"]
            self.assertLess(up[0] * sign, 0.0)      # rearward on ascent
            self.assertGreater(dn[0] * sign, 0.0)   # forward on descent
            self.assertGreater(up[2], 0.0)
            self.assertGreater(dn[2], 0.0)
            # Magnus perpendicular to velocity
            self.assertAlmostEqual(float(np.dot(up, [sign * 5.0, 0, 3.0])), 0.0, delta=1e-14)

    def test_along_trajectory_rearward_then_forward(self):
        for sign in (+1, -1):
            v0 = launch(6.0, 65.0, sign)
            tr = fl.simulate([0, 0, 0.3], v0, fl.backspin_omega(v0, 300.0), BASE)
            ta = tr.apex()["t"]
            for i in range(0, len(tr.t), 25):
                fm = tr.magnus_force(i)
                if tr.t[i] < ta - 1e-3:
                    self.assertLess(fm[0] * sign, 0.0)
                elif tr.t[i] > ta + 1e-3:
                    self.assertGreater(fm[0] * sign, 0.0)

    def test_scale_check_handoff(self):
        # HANDOFF 4A: 5 m/s, Cl=0.20 -> Magnus accel ~0.49 m/s^2
        p = dict(BASE, Cl=lambda S: 0.20)
        v = np.array([5.0, 0, 0])
        a = fl.aero_forces(v, fl.backspin_omega(v, 100.0), p)["F_magnus"][2] / 0.025
        self.assertAlmostEqual(a, 0.485, delta=0.01)


class TestRegularization(unittest.TestCase):
    def test_zero_speed_forces_vanish(self):
        w = np.array([0.0, -500.0, 0.0])
        f = fl.aero_forces([0, 0, 0], w, BASE)
        self.assertTrue(np.all(np.isfinite(f["F_magnus"])) and np.all(np.isfinite(f["F_drag"])))
        self.assertEqual(float(np.abs(f["F_magnus"]).sum() + np.abs(f["F_drag"]).sum()), 0.0)
        self.assertTrue(math.isfinite(f["S"]))
        prev = None
        for vm in [1.0, 1e-2, 1e-4, 1e-6, 1e-8, 1e-10, 1e-12]:
            ff = fl.aero_forces([vm, 0, 0], w, BASE)
            tot = np.linalg.norm(ff["F_magnus"]) + np.linalg.norm(ff["F_drag"])
            self.assertTrue(math.isfinite(tot))
            self.assertLessEqual(tot, 0.5 * 1.225 * math.pi * 0.0355 ** 2 * (0.5 + 0.4) * vm * vm * 1.0001)
            if prev is not None:
                self.assertLess(tot, prev)
            prev = tot

    def test_unbounded_cl_still_vanishes(self):
        p = dict(BASE, Cl=lambda S: 0.25 * S)  # no cap: grows like S ~ 1/|v|
        w = np.array([0.0, -500.0, 0.0])
        mags = [np.linalg.norm(fl.aero_forces([vm, 0, 0], w, p)["F_magnus"])
                for vm in [1e-2, 1e-4, 1e-6, 0.0]]
        self.assertTrue(all(math.isfinite(m) for m in mags))
        self.assertEqual(mags[-1], 0.0)
        self.assertLess(mags[2], mags[0])

    def test_drop_from_rest_with_spin(self):
        tr = fl.simulate([0, 0, 1.0], [0, 0, 0], [0, -800.0, 0], BASE, wind=(0, 0, 0))
        for arr in (tr.pos, tr.vel, tr.omega):
            self.assertTrue(np.all(np.isfinite(arr)))
        self.assertEqual(tr.termination, "ground")
        ap = tr.apex()  # vz0 = 0 then falling: apex is the launch point itself
        self.assertTrue(ap is None or ap["t"] == 0.0)
        self.assertTrue(math.isfinite(ap["S"]) and ap["F_M_mag"] == 0.0)

    def test_wind_equal_velocity_no_aero(self):
        f = fl.aero_forces([3.0, 0, 1.0], [0, -300, 0], BASE, wind=[3.0, 0, 1.0])
        self.assertEqual(float(np.abs(f["F_drag"]).sum() + np.abs(f["F_magnus"]).sum()), 0.0)


class TestSpinDecayEnergy(unittest.TestCase):
    def test_spin_decay_exponential(self):
        k = 0.8
        w0 = np.array([0.0, -400.0, 0.0])
        tr = fl.simulate([0, 0, 0.3], launch(6, 60), w0, dict(BASE, spin_decay_k=k))
        expected = w0[None, :] * np.exp(-k * tr.t)[:, None]
        np.testing.assert_allclose(tr.omega, expected, rtol=1e-7, atol=1e-9)
        tr0 = fl.simulate([0, 0, 0.3], launch(6, 60), w0, BASE)
        np.testing.assert_allclose(tr0.omega, np.tile(w0, (len(tr0.t), 1)), atol=1e-12)

    def test_energy_monotone_with_drag(self):
        v0 = launch(7.0, 60.0)
        for spin in (0.0, 400.0):
            tr = fl.simulate([0, 0, 0.3], v0, fl.backspin_omega(v0, spin) if spin else [0, 0, 0],
                             BASE)
            E = mech_energy(tr)
            self.assertTrue(np.all(np.diff(E) <= 1e-12), "mechanical energy increased")
            self.assertLess(E[-1], E[0])
        # Magnus does no work in still air
        tr = fl.simulate([0, 0, 0.3], v0, fl.backspin_omega(v0, 400.0), BASE)
        for i in range(0, len(tr.t), 50):
            self.assertAlmostEqual(float(np.dot(tr.magnus_force(i), tr.vel[i])), 0.0, delta=1e-13)
        # more drag -> more energy lost by the same time
        t_cmp = 0.8
        Es = []
        for cd in (0.0, 0.3, 0.6, 1.0):
            tr = fl.simulate([0, 0, 0.3], v0, [0, 0, 0], dict(BASE, Cd=cd, Cl=None))
            s = tr.state_at(t_cmp)
            Es.append(0.5 * 0.025 * s["speed"] ** 2 + 0.025 * G * s["z"])
        self.assertTrue(all(a > b for a, b in zip(Es, Es[1:])))


class TestApexReversal(unittest.TestCase):
    def test_apex_oblique(self):
        for p, spin in ((VACUUM, 0.0), (BASE, 0.0), (BASE, 400.0)):
            v0 = launch(6.5, 62.0)
            tr = fl.simulate([0, 0, 0.3], v0, fl.backspin_omega(v0, spin) if spin else [0, 0, 0], p)
            ap = tr.apex()
            self.assertIsNotNone(ap)
            self.assertAlmostEqual(ap["vz"], 0.0, delta=1e-8)
            self.assertGreater(ap["vx"], 0.5)
            self.assertGreater(ap["speed"], 0.5)   # ball is NOT stationary at apex
            for key in ("x", "z", "vx", "vz", "omega", "S", "F_M", "F_M_mag", "a_M"):
                self.assertIn(key, ap)
            if spin:
                self.assertGreater(ap["F_M"][2], 0.0)   # backspin lift is upward at apex
                self.assertAlmostEqual(ap["F_M"][0], 0.0, delta=1e-12)  # no "hook" at apex
        tr = fl.simulate([0, 0, 0.3], launch(6.5, 62.0), [0, 0, 0], VACUUM)
        self.assertAlmostEqual(tr.apex()["vx"], 6.5 * math.cos(math.radians(62.0)), delta=1e-9)

    def test_no_reversal_for_normal_shots(self):
        for sign in (+1, -1):
            for elev in (30.0, 60.0, 80.0):
                v0 = launch(7.0, elev, sign)
                for p, spin in ((VACUUM, 0.0), (BASE, 0.0), (BASE, 500.0)):
                    w = fl.backspin_omega(v0, spin) if spin else [0, 0, 0]
                    tr = fl.simulate([0, 0, 0.3], v0, w, p)
                    self.assertFalse(fl.horizontal_reversal(tr))
                    self.assertFalse(tr.horizontal_reversal())

    def test_reversal_detector_fires(self):
        # strong headwind blows a slow ball backwards: genuine reversal
        v0 = launch(3.0, 70.0)
        tr = fl.simulate([0, 0, 0.3], v0, [0, 0, 0], BASE, wind=(-12.0, 0, 0))
        self.assertTrue(fl.horizontal_reversal(tr))


class TestStopsAndParams(unittest.TestCase):
    def test_plane_stop(self):
        v0 = launch(7.0, 50.0)
        tr = fl.simulate([0, 0, 0.3], v0, [0, 0, 0], BASE,
                         stop=fl.plane_event((1.5, 0, 0), (1, 0, 0), direction=+1))
        self.assertEqual(tr.termination, "stop0")
        self.assertAlmostEqual(tr.pos[-1, 0], 1.5, delta=1e-9)
        self.assertEqual(len(tr.events["stop0"]), 1)

    def test_t_max(self):
        tr = fl.simulate([0, 0, 0.3], launch(7.0, 70.0), [0, 0, 0], BASE, t_max=0.2)
        self.assertEqual(tr.termination, "t_max")
        self.assertAlmostEqual(tr.t[-1], 0.2, delta=1e-12)

    def test_callable_cd_cl(self):
        v0 = launch(6.0, 60.0)
        w = fl.backspin_omega(v0, 300.0)
        a = fl.simulate([0, 0, 0.3], v0, w, BASE)
        b = fl.simulate([0, 0, 0.3], v0, w, dict(BASE, Cd=lambda Re: 0.5,
                                                 Cl=lambda S, Re: min(0.25 * S, 0.4)))
        np.testing.assert_allclose(a.pos[-1], b.pos[-1], atol=1e-9)
        c = fl.simulate([0, 0, 0.3], v0, w, dict(BASE, Cl={"c1": 0.25, "Cl_max": 0.4}))
        np.testing.assert_allclose(a.pos[-1], c.pos[-1], atol=1e-12)

    def test_load_params_json(self):
        raw = {"rho": {"value": 1.2, "prov": "assumed"}, "mass": {"value": 0.0249, "prov": "x"},
               "radius": {"value": 0.0356, "prov": "x"},
               "I_b": {"value": 1.5e-5, "low": 1e-5, "high": 2.1e-5, "prov": "x"},
               "Cd": {"low": 0.4, "nominal": 0.5, "high": 0.7, "prov": "assumed"},
               "Cl": {"model": "linear_capped", "formula": "Cl = min(c1*S, Cl_max)",
                      "sets": {"low": {"c1": 0.1, "Cl_max": 0.2},
                               "nominal": {"c1": 0.2, "Cl_max": 0.3},
                               "high": {"c1": 0.3, "Cl_max": 0.4}}, "prov": "assumed"},
               "spin_decay_k": {"low": 0.0, "nominal": 0.5, "high": 2.0, "units": "1/s",
                                "prov": "assumed"}}
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "aero_params.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(raw, fh)
            p = fl.load_params(path, "high")
            self.assertEqual((p["Cd"], p["Cl"], p["spin_decay_k"]), (0.7, (0.3, 0.4), 2.0))
            self.assertEqual(p["rho"], 1.2)
            p2 = fl.load_params(path, {"Cd": "low"})
            self.assertEqual((p2["Cd"], p2["Cl"], p2["spin_decay_k"]), (0.4, (0.2, 0.3), 0.5))
            p3 = fl.default_params(path=path)
            self.assertEqual(p3["Cd"], 0.5)
            tr = fl.simulate([0, 0, 0.3], launch(6, 60), [0, -300, 0], p3)
            self.assertEqual(tr.termination, "ground")
        pf = fl.default_params(path=os.path.join(tempfile.gettempdir(), "no_such_aero.json"))
        self.assertEqual(pf["mass"], 0.025)
        self.assertEqual(pf["Cl"], (0.25, 0.4))
        self.assertIn("PLACEHOLDER", pf["prov"]["Cl"])


class TestCompareSpin(unittest.TestCase):
    def test_zero_spin_no_difference(self):
        c = fl.compare_spin([0, 0, 0.3], launch(6, 60), 0.0, BASE)
        self.assertEqual(c["max_abs_dpos_t"]["abs"], 0.0)
        self.assertEqual(c["max_abs_dz_s"]["abs"], 0.0)
        self.assertEqual(c["apex"]["dz"], 0.0)

    def test_backspin_differences(self):
        for sign in (+1, -1):
            v0 = launch(6.0, 60.0, sign)
            c = fl.compare_spin([0, 0, 0.3], v0, 400.0, BASE)
            self.assertGreater(c["apex"]["dz"], 0.0)   # backspin raises the apex
            self.assertGreater(c["max_abs_dpos_t"]["abs"], 0.0)
            self.assertTrue(c["downrange_monotone"])
            self.assertFalse(c["reversal"]["spin"])
            self.assertEqual(len(c["t"]), len(c["dz_t"]))
            self.assertEqual(len(c["s"]), len(c["dz_s"]))
            self.assertTrue(np.all(np.sign(c["x"][1:]) == sign))
            # equal-time vacuum check: Magnus is the only difference -> zero in vacuum
            cv = fl.compare_spin([0, 0, 0.3], v0, 400.0, dict(VACUUM, Cl=(0.25, 0.4)))
            self.assertLess(cv["max_abs_dpos_t"]["abs"], 1e-12)


if __name__ == "__main__":
    unittest.main()
