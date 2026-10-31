"""PM-016 options (research/MISSING_EFFECTS.md build-next 2a-2f) in Python against the browser copy:
shooting on the move (robustness.launch_state / integrate3d / cell3d.classify_path3d vs solver.js launch3 /
path3D / physics.js classifyPath3D), the hit-chance Monte Carlo (robustness.hit_chance / mc_shots(cell=...) vs
solver.js hitChance, same seeded normals), plus unit checks of gyro-correct S, the Cl table, reverse Magnus and
effective mass in src/flight.py, src/air.py and src/feasibility.py.

Every number here is model output (PREDICTED) or an ASSUMED option value, not a POLLEN measurement.
"""
import json
import math
import os
import shutil
import subprocess
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from src import air, cell3d, feasibility as fz, flight as fl, robustness as rb  # noqa: E402

SCRIPT = os.path.join(HERE, "js_move_check.js")
_DUMP = {}


def _node():
    node = shutil.which("node")
    if not node:
        raise unittest.SkipTest("node not installed")
    return node


def _dump():
    if "d" not in _DUMP:
        r = subprocess.run([_node(), SCRIPT, "--dump"], capture_output=True, text=True, timeout=900)
        if r.returncode == 77:
            raise unittest.SkipTest("field data missing: " + r.stdout.strip()[-200:])
        if r.returncode != 0:
            raise AssertionError(r.stderr[-2000:])
        _DUMP["d"] = json.loads(r.stdout)
    return _DUMP["d"]


def _wind(p3, n):
    w = p3.get("wind3")
    return None if w is None else np.tile(np.asarray(w, float), (n, 1))


class TestMoveJs(unittest.TestCase):
    def test_normals_match(self):
        d = _dump()
        py = rb.mulberry32_normals(20261031, 31)
        np.testing.assert_allclose(py, d["normals"], rtol=0, atol=1e-14)

    def test_launch_path_classify_match(self):
        d = _dump()
        cells = {}
        n_shots = n_clean = n_inf = 0
        for c in d["cases"]:
            key = (c["side"], c["ridge"], c["wallT"])
            if key not in cells:
                cells[key] = cell3d.build_cell(d["sections"][c["side"]], ridge=c["ridge"], wall_t=c["wallT"])
            cell, F, p3, R, h = cells[key], c["F"], c["p3"], c["R"], c["h"]
            zs = c["zStop"] + h
            for s in c["shots"]:
                n_shots += 1
                L = rb.launch_state(F, s["v"], s["th"], c["S"], R, h, s["dpsi"])
                msg = "case %s S %s v %.3f th %.3f" % (c["side"], c["S"], s["v"], s["th"])
                if s["launch"] is None:
                    self.assertFalse(bool(L["ok"][0]), msg)
                    self.assertEqual(s["code"], 5, msg)
                    n_inf += 1
                    continue
                self.assertTrue(bool(L["ok"][0]), msg)
                for k, a in (("x0", L["x0"][0]), ("v0", L["v0"][0]), ("w0", L["w0"][0])):
                    want = np.array(s["launch"][k], float)
                    if k == "x0":
                        want = np.array([want[0], want[1], h])
                    np.testing.assert_allclose(a, want, rtol=0, atol=1e-12, err_msg=msg + " " + k)
                tr = rb.integrate3d(L["x0"], L["v0"], L["w0"], p3, wind=_wind(p3, 1), t_max=3.0, z_stop=zs,
                                    dtype=np.float64)
                Pp, Vv = tr["P"][0], tr["V"][0]
                for i, x, y, z, vx, vy, vz in s["pts"]:
                    got = np.r_[Pp[i], Vv[i]]
                    np.testing.assert_allclose(got, [x, y, z, vx, vy, vz], rtol=1e-9, atol=1e-11,
                                               err_msg=msg + " step %d" % i)
                e = s["n"]
                r = cell3d.classify_path3d(Pp[:e, 0], Pp[:e, 1], Pp[:e, 2], cell, R)
                self.assertEqual(r["result"], s["cls"]["result"], msg)
                self.assertEqual(r["i"], s["cls"]["i"], msg)
                if s["cls"]["minClear"] is not None and math.isfinite(r["min_clear"]):
                    self.assertAlmostEqual(r["min_clear"], s["cls"]["minClear"], delta=1e-8, msg=msg)
                want = {1: "clean", 2: "hit"}.get(s["code"], "miss")
                self.assertEqual(r["result"], want, msg)
                n_clean += r["result"] == "clean"
        self.assertGreaterEqual(n_shots, 50)
        self.assertGreaterEqual(n_clean, 10)

    def test_hit_chance_counts_match(self):
        d = _dump()
        n_sets = 0
        for c in d["cases"]:
            cell = cell3d.build_cell(d["sections"][c["side"]], ridge=c["ridge"], wall_t=c["wallT"])
            hc = c["hc"]
            aim = {"v": hc["v"], "theta": hc["theta"], "S": c["S"], "h": c["h"], "z_stop": c["zStop"]}
            sig = {"sig_v_rel": hc["sig"]["sv"], "sig_th": hc["sig"]["sth"], "sig_psi": hc["sig"]["spsi"]}
            tw = hc["twin"]
            py = rb.hit_chance(cell, c["F"], aim, hc["setParams"], n=hc["n"], seed=hc["seed"], sig=sig,
                               twin_aim={"v": tw["v"], "theta": tw["theta"]} if tw else None)
            for js, p in zip(hc["sets"], py["sets"]):
                self.assertEqual(js["name"], p["name"])
                self.assertEqual(p["k"], js["k"], "%s %s S %s" % (c["side"], js["name"], c["S"]))
                self.assertAlmostEqual(p["lo"], js["lo"], places=12)
                self.assertAlmostEqual(p["hi"], js["hi"], places=12)
                n_sets += 1
            if tw:
                self.assertEqual(py["twin"]["k"], tw["k"])
            else:
                self.assertNotIn("twin", py)
        self.assertGreaterEqual(n_sets, 15)

    def test_node_checks(self):
        r = subprocess.run([_node(), SCRIPT], capture_output=True, text=True, timeout=900)
        if r.returncode == 77:
            self.skipTest("field data missing")
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])


BASE = {"rho": 1.2041, "mass": 0.02495, "radius": 0.0355, "Cd": 0.5, "Cl": (0.35, 0.25), "spin_decay_k": 0.0}


class TestOptionsPy(unittest.TestCase):
    def test_gyro_s_pure_backspin_unchanged(self):
        v = np.array([3.0, 0.0, 6.0])
        w = fl.backspin_omega(v, 0.3 * np.linalg.norm(v) / BASE["radius"])
        a = fl.aero_forces(v, w, BASE)
        b = fl.aero_forces(v, w, dict(BASE, s_perp=True))
        self.assertAlmostEqual(a["S"], b["S"], places=12)
        np.testing.assert_allclose(a["F_magnus"], b["F_magnus"], rtol=1e-12)
        ta = fl.simulate([0, 0, 0.5], v, w, BASE, t_max=0.6, z_ground=None)
        tb = fl.simulate([0, 0, 0.5], v, w, dict(BASE, s_perp=True), t_max=0.6, z_ground=None)
        np.testing.assert_allclose(ta.pos[-1], tb.pos[-1], atol=1e-9)

    def test_gyro_s_tilted_axis_smaller(self):
        v = np.array([3.0, 0.0, 6.0])
        w = fl.backspin_omega(v, 0.3 * np.linalg.norm(v) / BASE["radius"]) + np.array([0.0, 0.0, 40.0])
        a = fl.aero_forces(v, w, BASE)
        b = fl.aero_forces(v, w, dict(BASE, s_perp=True))
        self.assertLess(b["S"], a["S"])
        self.assertLess(np.linalg.norm(b["F_magnus"]), np.linalg.norm(a["F_magnus"]))

    def test_effective_mass_scales_gravity(self):
        vac = dict(BASE, rho=0.0, Cl=None)
        ta = fl.simulate([0, 0, 2.0], [0, 0, 0], [0, 0, 0], vac, t_max=0.5, z_ground=None)
        tb = fl.simulate([0, 0, 2.0], [0, 0, 0], [0, 0, 0], dict(vac, eps_mass=0.01), t_max=0.5, z_ground=None)
        self.assertAlmostEqual((2.0 - tb.pos[-1][2]) * 1.01, 2.0 - ta.pos[-1][2], places=9)
        eps, eps1 = air.eps_from_phi(0.0, 1.2041, 0.02495, 0.0355), air.eps_from_phi(1.0, 1.2041, 0.02495, 0.0355)
        self.assertAlmostEqual(eps, 0.00452, delta=5e-5)
        self.assertAlmostEqual(eps1, 0.01357, delta=5e-5)

    def test_cl_table_and_reverse(self):
        t = [[0.5, 0.2], [1.5, 0.35]]
        self.assertAlmostEqual(air.cl_table_of(t, 0.25), 0.1)       # straight to (0, 0) before the first point
        self.assertAlmostEqual(air.cl_table_of(t, 1.0), 0.275)
        self.assertAlmostEqual(air.cl_table_of(t, 3.0), 0.35)       # flat after the last point
        p = {"Cl": (0.35, 0.25)}
        self.assertEqual(air.cl_of(p, 0.3, 2e4), min(0.35 * 0.3, 0.25))
        self.assertLess(air.cl_of(dict(p, cl_rev=0.1), 0.3, 2e4), 0.0)       # reverse region
        self.assertEqual(air.cl_of(dict(p, cl_rev=0.1), 0.3, 6e4), air.cl_of(p, 0.3, 6e4))
        self.assertEqual(air.cl_of(dict(p, cl_rev=0.1), 0.8, 2e4), air.cl_of(p, 0.8, 2e4))
        # flight.py uses the same function
        prep = fl._prepare(dict(BASE, cl_table=t, cl_rev=0.1))
        for S, re in ((0.3, 2e4), (0.3, 6e4), (1.0, 3e4)):
            self.assertAlmostEqual(prep.cl_fn(S, re), float(air.cl_of({"cl_table": t, "cl_rev": 0.1}, S, re)), places=12)

    def test_options_off_identical(self):
        v, th = np.array([6.0, 8.0]), np.array([73.5, 80.0])
        prm = dict(BASE)
        a = fz.integrate_batch(v, th, 1.0, prm)
        b = fz.integrate_batch(v, th, 1.0, dict(prm, cl_table=None, cl_rev=0.0, eps_mass=0.0))
        for k in ("X", "Z", "VX", "VZ"):
            np.testing.assert_array_equal(a[k], b[k])
        p3 = {"rho": 1.2041, "mass": 0.02495, "radius": 0.0355, "Cd": 0.5, "c1": 0.35, "clmax": 0.25, "k": 0.03}
        x0, v0 = np.array([[0.0, 0.0, 0.5]]), np.array([[3.0, 0.0, 6.0]])
        w0 = rb.backspin_axis(v0) * 150.0
        a = rb.integrate3d(x0, v0, w0, p3, dtype=np.float64)
        b = rb.integrate3d(x0, v0, w0, dict(p3, cl_rev=0.0, eps_mass=0.0, cl_table=None), dtype=np.float64)
        np.testing.assert_array_equal(a["P"], b["P"])
        c = rb.integrate3d(x0, v0, w0, dict(p3, s_perp=True), dtype=np.float64)   # pure backspin
        np.testing.assert_allclose(a["P"], c["P"], atol=1e-9)


if __name__ == "__main__":
    unittest.main()
