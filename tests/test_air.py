"""Venue air and optional drag / draft terms (src/air.py, src/feasibility.integrate_batch) against the JS copy in
viz/explorer/physics.js (tests/js_air_check.js --dump), plus the node solver checks (tests/js_air_check.js).

Values checked here are derived (formulas), not POLLEN measurements.
"""
import json
import os
import shutil
import subprocess
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from src import air, feasibility as fz  # noqa: E402

SCRIPT = os.path.join(HERE, "js_air_check.js")


def _node():
    node = shutil.which("node")
    if not node:
        raise unittest.SkipTest("node not installed")
    return node


class TestAirState(unittest.TestCase):
    def test_still_air_reference(self):
        st = air.air_state()
        self.assertAlmostEqual(st["rho"], 101325.0 / (287.06 * 293.15), places=10)
        self.assertAlmostEqual(st["rho"], 1.2041, places=4)
        self.assertAlmostEqual(st["mu"], 1.813e-5, delta=0.005e-5)     # Sutherland at 20 C
        self.assertAlmostEqual(st["nu"], 1.506e-5, delta=0.002e-5)

    def test_density_trends(self):
        self.assertLess(air.air_density(30.0), air.air_density(20.0))
        self.assertLess(air.air_density(20.0, rh=0.8), air.air_density(20.0))   # moist air is lighter
        self.assertAlmostEqual(air.pressure_from_altitude(0.0), 101325.0)
        self.assertAlmostEqual(air.pressure_from_altitude(1600.0) / 1000.0, 83.5, delta=0.2)

    def test_morrison_shape(self):
        # flat about 0.4 in POLLEN's band, crisis drop past 2.6e5 (smooth sphere; reference curve only)
        self.assertAlmostEqual(float(air.morrison_cd(3.55e4)), 0.3996, delta=1e-3)
        self.assertGreater(float(air.morrison_cd(1e5)), float(air.morrison_cd(5e5)) + 0.15)

    def test_blend_and_ext(self):
        p = {"Cd": 0.5, "cd_model": "blend"}
        self.assertEqual(air.cd_base(p, 1e4), 0.5)
        self.assertAlmostEqual(air.cd_base(p, 1e5), 0.33)
        self.assertAlmostEqual(air.cd_base(p, 4e4), 0.415)
        self.assertFalse(air.has_ext({"Cd": 0.5}))
        self.assertFalse(air.has_ext({"Cd": 0.5, "cd_model": "const", "dcd_spin": 0, "wind": (0, 0)}))
        self.assertTrue(air.has_ext({"Cd": 0.5, "wind": (0.0, 0.1)}))

    def test_grip_flag(self):
        self.assertTrue(air.grip_limited(9.0))
        self.assertFalse(air.grip_limited(8.9))
        self.assertEqual(air.HOOD_V_MAX, fz.HOOD_V_MAX)

    def test_options_off_identical(self):
        prm = {"rho": 1.2, "mass": 0.02495, "radius": 0.0355, "Cd": 0.5, "Cl": (0.35, 0.25), "spin_decay_k": 0.03}
        a = fz.integrate_batch(np.array([6.0, 8.0]), np.array([73.5, 80.0]), 1.0, prm)
        b = fz.integrate_batch(np.array([6.0, 8.0]), np.array([73.5, 80.0]), 1.0,
                               dict(prm, cd_model="const", dcd_spin=0.0, wind=(0.0, 0.0)))
        for k in ("X", "Z", "VX", "VZ"):
            np.testing.assert_array_equal(a[k], b[k])

    def test_tail_draft_carries_farther(self):
        prm = {"rho": 1.2041, "mass": 0.02495, "radius": 0.0355, "Cd": 0.5, "Cl": None, "spin_decay_k": 0.0}
        a = fz.integrate_batch(np.array([7.0]), np.array([60.0]), 0.0, prm)
        b = fz.integrate_batch(np.array([7.0]), np.array([60.0]), 0.0, dict(prm, wind=(0.3, 0.0)))
        n = min(a["X"].shape[1], b["X"].shape[1]) - 1
        self.assertGreater(b["X"][0, n], a["X"][0, n])


class TestAirJs(unittest.TestCase):
    def test_python_matches_js(self):
        node = _node()
        r = subprocess.run([node, SCRIPT, "--dump"], capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        data = json.loads(r.stdout)
        for js, args in zip(data["air"], [(), (30.0, 85000.0, 0.6), (15.0, air.pressure_from_altitude(1600.0), 0.3)]):
            py = air.air_state(*args)
            for k in ("rho", "mu", "nu"):
                self.assertAlmostEqual(js[k] / py[k], 1.0, places=12)
        for re, cd in data["morrison"]:
            self.assertAlmostEqual(float(air.morrison_cd(re)), cd, places=12)
        self.assertGreaterEqual(len(data["traj"]), 65)
        for t in data["traj"]:
            p = t["p"]
            prm = {"rho": p["rho"], "mass": p["mass"], "radius": p["radius"], "Cd": p["Cd"],
                   "Cl": (p["c1"], p["clmax"]) if p["c1"] > 0 else None, "spin_decay_k": p["k"], "nu": p["nu"]}
            for k in ("cd_model", "cd_sub", "cd_post", "re1", "re2", "dcd_spin", "cl_table", "cl_rev", "re_rev", "s_rev",
                      "eps_mass"):
                if k in p:
                    prm[k] = p[k]
            if "wind" in p:
                prm["wind"] = tuple(p["wind"])
            o = fz.integrate_batch(np.array([t["v"]]), np.array([t["th"]]), t["S"], prm)
            for i, x, z, vx, vz in t["pts"]:
                got = (o["X"][0, i], o["Z"][0, i], o["VX"][0, i], o["VZ"][0, i])
                for g, w in zip(got, (x, z, vx, vz)):          # Python stores float32
                    self.assertAlmostEqual(float(g), w, delta=2e-6 * max(1.0, abs(w)),
                                           msg="%s v %s th %s S %s step %d" % (t["case"], t["v"], t["th"], t["S"], i))

    def test_node_solver_checks(self):
        node = _node()
        r = subprocess.run([node, SCRIPT], capture_output=True, text=True, timeout=900)
        if r.returncode == 77:
            self.skipTest("field data missing: " + r.stdout.strip()[-200:])
        self.assertEqual(r.returncode, 0, r.stdout[-4000:] + r.stderr[-2000:])
        self.assertIn('"failed":0', r.stdout.strip().splitlines()[-1])


if __name__ == "__main__":
    unittest.main()
