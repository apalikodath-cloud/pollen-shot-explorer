"""PM-015 tests for research/GEOMETRY_AUDIT.md fixes: robot footprint (fix 2), exact other-HIVE flag (fix 5),
symmetric grid on the aim line (fix 8), HIVE tilt bounds (fix 4), sloped-roof clearance option (fix 3), and the
JS twins in viz/explorer/solver.js (run through node via tests/js_field_geom_check.js; skipped without node)."""
import json
import math
import os
import shutil
import subprocess
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))

import field_geom as fg  # noqa: E402
import feasibility as fz  # noqa: E402
from hive import Hive  # noqa: E402

IN = 0.0254


def _geom():
    with open(os.path.join(HERE, "..", "data", "hive_geometry.json"), encoding="utf-8") as f:
        return json.load(f)


class TestFootprint(unittest.TestCase):
    def test_base_and_walls(self):
        # CONFIRMED A-frame base 38.95 x 49.46 in, centred on the HIVE (y = 0.3236)
        self.assertAlmostEqual(fg.BASE_HALF_X, 38.95 / 2 * IN, places=9)
        self.assertAlmostEqual(fg.BASE_HALF_Y, 49.46 / 2 * IN, places=9)
        self.assertTrue(fg.chassis_ok(-1.0, 0.2))                 # default pose: legal
        self.assertFalse(fg.chassis_ok(0.70, 0.2))                # chassis overlaps the base side
        self.assertTrue(fg.chassis_ok(0.73, 0.2))                 # 0.4947 + 0.2286 = 0.7233 < 0.73
        self.assertTrue(fg.chassis_ok(1.57, 0.0))                 # 1.57 + 0.2286 = 1.7986 <= wall 1.8009
        self.assertFalse(fg.chassis_ok(1.58, 0.0))
        self.assertFalse(fg.chassis_ok(0.0, 0.3236))              # release point on the base

    def test_turned_chassis(self):
        h = fg.ROBOT_L / 2
        # at 45 deg the square reaches h * sqrt(2) along x: fails where 0 deg fits
        x = fg.X_WALL - h - 0.005
        self.assertTrue(fg.chassis_fits(x, 0.0, 0.0))
        self.assertFalse(fg.chassis_fits(x, 0.0, 45.0))
        self.assertTrue(fg.chassis_fits(fg.X_WALL - h * math.sqrt(2) - 1e-6, 0.0, 45.0))
        self.assertFalse(fg.chassis_fits(fg.X_WALL - h * math.sqrt(2) + 1e-6, 0.0, 45.0))
        # corner of the base: 45 deg chassis clears where the axis-aligned one overlaps
        bx, by = fg.BASE_HALF_X, fg.BASE_CY + fg.BASE_HALF_Y
        px, py = bx + 0.9 * h, by + 0.9 * h
        self.assertFalse(fg.chassis_fits(px, py, 0.0))
        d = (px - bx) + (py - by)                                  # distance along the diagonal times sqrt 2
        self.assertEqual(bool(fg.chassis_fits(px, py, 45.0)), d / math.sqrt(2) >= h - 1e-9)

    def test_expanded_and_offset(self):
        self.assertAlmostEqual(fg.ROBOT_L_EXPANDED, 24 * IN)
        # 0.73 fits the 18 x 18 chassis but not 24 in along x at heading 0; turned 90 deg it fits again
        self.assertTrue(fg.chassis_fits(0.73, 0.2, 0.0))
        self.assertFalse(fg.chassis_fits(0.73, 0.2, 0.0, length=fg.ROBOT_L_EXPANDED))
        self.assertTrue(fg.chassis_fits(0.73, 0.2, 90.0, length=fg.ROBOT_L_EXPANDED))
        # release offset: chassis centre = release - rot(heading) (fwd, left). Facing -x with the release
        # 0.1 m forward of the centre puts the centre at x = 0.80, clear of the base; facing +x puts it at 0.60
        self.assertFalse(fg.chassis_fits(0.70, 0.2, 0.0))
        self.assertTrue(fg.chassis_fits(0.70, 0.2, 180.0, offset=(0.1, 0.0)))
        self.assertFalse(fg.chassis_fits(0.70, 0.2, 0.0, offset=(0.1, 0.0)))
        self.assertTrue(fg.chassis_fits(0.70, 0.2, 0.0, offset=(-0.1, 0.0)))
        self.assertTrue(fg.chassis_fits(0.70, 0.2, 90.0, offset=(0.0, 0.1)))       # left of heading 90 = -x
        # any-heading scan with an offset covers 0..360
        self.assertTrue(fg.chassis_ok(0.70, 0.2, offset=(-0.1, 0.0)))
        # release point itself must stay off the base even with a long offset
        self.assertFalse(fg.chassis_ok(0.0, 0.3236, offset=(1.2, 0.0)))

    def test_default_legal_mask_vs_dense_corners(self):
        # vectorised SAT vs a dense corner/edge-sample reference on the export grid at heading 0 and 30
        _, _, X, Y = fg.field_grid()
        h = fg.ROBOT_L / 2
        for hd in (0.0, 30.0):
            got = fg.chassis_fits(X, Y, hd)
            c, s = math.cos(math.radians(hd)), math.sin(math.radians(hd))
            u = np.linspace(-h, h, 41)
            A, B = np.meshgrid(u, u)
            px = X[..., None] + c * A.ravel() - s * B.ravel()
            py = Y[..., None] + s * A.ravel() + c * B.ravel()
            inside = (np.abs(px) <= fg.X_WALL + 1e-9) & (py >= fg.Y_LO - 1e-9) & (py <= fg.Y_HI + 1e-9)
            on_base = (np.abs(px) < fg.BASE_HALF_X - 1e-9) & (np.abs(py - fg.BASE_CY) < fg.BASE_HALF_Y - 1e-9)
            # plus the base corners inside the chassis (a corner can poke in between samples)
            bc = [(sx * fg.BASE_HALF_X, fg.BASE_CY + sy * fg.BASE_HALF_Y) for sx in (-1, 1) for sy in (-1, 1)]
            poke = np.zeros(X.shape, bool)
            for bx, by in bc:
                u, v = (bx - X) * c + (by - Y) * s, -(bx - X) * s + (by - Y) * c
                poke |= (np.abs(u) < h - 1e-9) & (np.abs(v) < h - 1e-9)
            ref = inside.all(-1) & ~on_base.any(-1) & ~poke
            diff = got != ref
            self.assertEqual(int(diff.sum()), 0, (hd, X[diff][:5], Y[diff][:5]))


class TestSight(unittest.TestCase):
    def test_exact_vs_dense(self):
        _, _, X, Y = fg.field_grid()
        got = fg.sight_blocked(X, Y)
        t = np.linspace(0, 1, 4001)
        px = X[..., None] + (fg.X_GATE - X[..., None]) * t
        py = Y[..., None] + (0.0 - Y[..., None]) * t
        ref = ((np.abs(px) < fg.OTHER_HIVE_X) & (py > fg.OTHER_HIVE_Y[0]) & (py < fg.OTHER_HIVE_Y[1])).any(-1)
        self.assertEqual(int((got & ~ref).sum()), 0)    # exact never flags what the samples do not see
        self.assertLessEqual(int((ref & ~got).sum()), 0)
        self.assertTrue(got.any())

    def test_cases(self):
        self.assertTrue(fg.sight_blocked(-1.0, 1.5))
        self.assertFalse(fg.sight_blocked(-1.0, 0.2))
        self.assertFalse(fg.sight_blocked(-1.0, -1.0))          # below the aim line: never blocked
        self.assertFalse(fg.sight_blocked(1.0, 0.34))            # passes under the box
        # the old Y > 0.90 rule is gone: a point above 0.90 far out to the side is not blocked
        self.assertFalse(fg.sight_blocked(1.7, 0.95))


class TestGrid(unittest.TestCase):
    def test_symmetric_on_aim_line(self):
        xs, ys, X, Y = fg.field_grid()
        np.testing.assert_allclose(xs, -xs[::-1])
        self.assertTrue(np.isclose(xs, 0).any())
        self.assertTrue(np.isclose(ys, 0).any())
        np.testing.assert_allclose(np.diff(ys), fg.FIELD_STEP)
        self.assertLessEqual(xs.max(), fg.X_WALL - fg.WALL_MARGIN + 1e-9)
        self.assertGreaterEqual(ys.min(), fg.Y_LO + fg.WALL_MARGIN - 1e-9)
        self.assertLessEqual(ys.max(), fg.Y_HI + fg.WALL_MARGIN * 0 - fg.WALL_MARGIN + 1e-9)
        self.assertEqual((len(xs), len(ys)), (69, 68))
        # HIVE spacing consistent: field centre between the two HIVEs, walls symmetric about it
        self.assertAlmostEqual((fg.Y_LO + fg.Y_HI) / 2, fg.HIVE_HALF_SPACING)

    def test_robustness_and_export_use_it(self):
        import robustness as rb
        xs, ys, X, Y, legal = rb.field_grid(fg.FIELD_STEP)
        xs2, ys2, _, _ = fg.field_grid()
        np.testing.assert_array_equal(xs, xs2)
        np.testing.assert_array_equal(ys, ys2)
        np.testing.assert_array_equal(legal, fg.chassis_ok(X, Y))


class TestTiltAndRoof(unittest.TestCase):
    def test_tilt_bounds(self):
        self.assertEqual(fz.TILT_BOUNDS, (28.8, 31.77))
        self.assertEqual(fz.TILT_BOUNDS_WIDE, (25.9, 34.83))
        # sweeps keep the old bounds until the re-sweep (deferred, labelled)
        self.assertEqual(fz.SWEEP_TILT, (28.5, 31.5))

    def test_roof_clearance_option(self):
        g = _geom()
        drop = Hive.roof_clearance_drop(g, 0.0355)
        self.assertAlmostEqual(drop, 0.006629, places=5)
        a = Hive.from_json()
        b = Hive.from_json(roof_clearance=True)
        c = Hive.from_json(roof_clearance=False)
        np.testing.assert_array_equal(a.P0, c.P0)               # default unchanged
        roof = [i for i, n in enumerate(a.names) if n.endswith(("roof_outer", "upper_lip", "roof_inner"))]
        self.assertEqual(len(roof), 6)
        for i, n in enumerate(a.names):
            for P in ("P0", "P1"):
                d = float(np.linalg.norm(getattr(a, P)[i] - getattr(b, P)[i]))
                if i in roof:
                    self.assertAlmostEqual(d, drop, delta=2e-5, msg=n)    # json stores 5-decimal points
                elif not (n.endswith("back_wall") and P == "P1"):        # back wall top joins the roof
                    self.assertLess(d, 2e-5, n)


class TestJsTwin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.node = shutil.which("node")

    def run_js(self, q):
        if not self.node:
            self.skipTest("node not installed")
        r = subprocess.run([self.node, os.path.join(HERE, "js_field_geom_check.js")], input=json.dumps(q),
                           capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        return json.loads(r.stdout.strip().splitlines()[-1])

    def test_js_matches_python(self):
        rng = np.random.default_rng(15)
        pts = np.column_stack([rng.uniform(-1.9, 1.9, 400), rng.uniform(-1.6, 2.25, 400)])
        pts = np.vstack([pts, [[-1.0, 0.2], [0.70, 0.2], [0.73, 0.2], [1.57, 0.0], [1.58, 0.0], [0.0, 0.3236]]])
        variants = [dict(length=fg.ROBOT_L, width=fg.ROBOT_W, offset=[0.0, 0.0], heading=None),
                    dict(length=fg.ROBOT_L, width=fg.ROBOT_W, offset=[0.0, 0.0], heading=45.0),
                    dict(length=fg.ROBOT_L_EXPANDED, width=fg.ROBOT_W, offset=[0.0, 0.0], heading=None),
                    dict(length=fg.ROBOT_L, width=fg.ROBOT_W, offset=[0.08, -0.05], heading=None),
                    dict(length=fg.ROBOT_L, width=fg.ROBOT_W, offset=[0.08, -0.05], heading=200.0)]
        fcases = [dict(x=float(x), y=float(y), **v) for v in variants for x, y in pts]
        scases = [[float(x), float(y), fg.X_GATE, 0.0] for x, y in pts] + \
                 [[float(x), float(y), -fg.X_GATE, 0.0] for x, y in pts]
        js = self.run_js(dict(footprint=fcases, sight=scases))
        py_f = [bool(fg.chassis_ok(c["x"], c["y"], c["heading"], c["length"], c["width"], tuple(c["offset"])))
                for c in fcases]
        js_f = [f["ok"] for f in js["footprint"]]
        self.assertEqual(py_f, js_f)
        self.assertGreater(sum(py_f), 100)
        self.assertGreater(len(py_f) - sum(py_f), 100)
        py_s = [bool(fg.sight_blocked(*c)) for c in scases]
        self.assertEqual(py_s, js["sight"])
        self.assertTrue(any(py_s))
        k = js["constants"]
        for name, val in (("X_WALL", fg.X_WALL), ("BASE_HX", fg.BASE_HALF_X), ("BASE_HY", fg.BASE_HALF_Y),
                          ("BASE_CY", fg.BASE_CY), ("OTHER_HIVE_X", fg.OTHER_HIVE_X), ("X_GATE", fg.X_GATE),
                          ("ROBOT_L", fg.ROBOT_L), ("ROBOT_L_EXPANDED", fg.ROBOT_L_EXPANDED),
                          ("Y_LO", fg.Y_LO), ("Y_HI", fg.Y_HI)):
            self.assertAlmostEqual(k[name], val, places=9, msg=name)
        self.assertEqual(k["OTHER_HIVE_Y"], list(fg.OTHER_HIVE_Y))

    def test_js_roof_clearance(self):
        js = self.run_js({})
        g = _geom()
        self.assertAlmostEqual(js["roofDrop"], Hive.roof_clearance_drop(g, 0.0355), places=9)
        r = js["roofSection"]
        d = js["roofDrop"]
        self.assertTrue(r["cached"] and r["origUnchanged"])
        self.assertEqual(r["P0"][0], [0, 0])                        # floor unchanged
        self.assertEqual(r["P0"][4], [0.3, 0])                      # wall unchanged
        for i in (1, 2, 3):
            self.assertAlmostEqual(r["P0"][i][1], 1 - d, places=12)
        self.assertAlmostEqual(r["gate"][1][1], 0.9 - d, places=12)
        self.assertEqual(r["gate"][0], [0, 0.2])


if __name__ == "__main__":
    unittest.main()
