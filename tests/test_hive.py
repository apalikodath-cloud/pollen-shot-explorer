"""Unit tests for src/hive.py (clean-entry classifier) and the src/feasibility.py sweep method.
Run from repo root:
    python -m unittest discover -s tests -v
All trajectories here are hand-built (straight lines, analytic parabolas) or short
flight.simulate runs; nothing depends on the cached sweep results.
"""
import math
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import feasibility as fz  # noqa: E402
from src import flight as fl  # noqa: E402
from src import hive as hv  # noqa: E402

G = fl.G_STANDARD


def _seg_key(p0, p1):
    a, b = tuple(np.round(p0, 4)), tuple(np.round(p1, 4))
    return (a, b) if a <= b else (b, a)


class TestDistances(unittest.TestCase):
    def test_point_segment(self):
        a, b = np.array([0.0, 0.0]), np.array([1.0, 0.0])
        self.assertAlmostEqual(float(hv.seg_point_dist(np.array([0.5, 0.3]), a, b)), 0.3)
        self.assertAlmostEqual(float(hv.seg_point_dist(np.array([2.0, 0.0]), a, b)), 1.0)
        self.assertAlmostEqual(float(hv.seg_point_dist(np.array([-3.0, 4.0]), a, b)), 5.0)

    def test_segment_segment(self):
        o = np.array([0.0, 0.0])
        x1 = np.array([1.0, 0.0])
        # crossing segments -> 0
        self.assertAlmostEqual(float(hv.seg_seg_dist(np.array([0.5, -1.0]), np.array([0.5, 1.0]),
                                                     o, x1)), 0.0)
        # parallel, offset 0.2
        self.assertAlmostEqual(float(hv.seg_seg_dist(np.array([0.0, 0.2]), np.array([1.0, 0.2]),
                                                     o, x1)), 0.2)
        # end-to-end gap
        self.assertAlmostEqual(float(hv.seg_seg_dist(np.array([1.3, 0.4]), np.array([2.0, 0.4]),
                                                     o, x1)), 0.5)


class TestGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.H = hv.Hive.from_json("pose_pos")

    def test_counts_and_gate(self):
        self.assertEqual(len(self.H.names), 25)
        self.assertEqual(len(hv.Hive.from_json("pose_pos", include_projected=True).names), 29)
        A, B = self.H.gate
        self.assertLess(A[1], B[1])
        # gate lies on the mouth plane
        for p in (A, B):
            self.assertAlmostEqual(float((p - self.H.mouth[0]) @ self.H.normal_out), 0.0, places=3)

    def test_pose_neg_is_mirror(self):
        M = self.H.mirrored()
        N = hv.Hive.from_json("pose_neg")
        km = sorted(_seg_key(a, b) for a, b in zip(M.P0, M.P1))
        kn = sorted(_seg_key(a, b) for a, b in zip(N.P0, N.P1))
        self.assertEqual(km, kn)
        np.testing.assert_allclose(np.sort(M.inside, axis=0), np.sort(N.inside, axis=0),
                                   atol=1e-4)

    def test_repose_nominal_matches_json(self):
        R = hv.Hive.from_json("pose_pos", tilt_deg=30.0 + 1e-9)
        a = sorted(_seg_key(p, q) for p, q, b in zip(self.H.P0, self.H.P1, self.H.body))
        b = sorted(_seg_key(p, q) for p, q, b_ in zip(R.P0, R.P1, R.body))
        self.assertEqual(len(a), len(b))
        for s, t in zip(a, b):
            self.assertLess(np.abs(np.array(s) - np.array(t)).max(), 2e-4)

    def test_raster_vs_exact(self):
        r = self.H.raster(2e-3)
        rng = np.random.default_rng(0)
        x = rng.uniform(r.x0, r.x0 + r.clr.shape[1] * r.res, 2000)
        z = rng.uniform(r.z0, r.z0 + r.clr.shape[0] * r.res, 2000)
        c_r, _ = r.lookup(x, z)
        c_e, _ = self.H.clearance(np.column_stack([x, z]))
        self.assertLessEqual(np.abs(c_r - c_e).max(), r.res / math.sqrt(2) + 1e-6)


class TestClassifyHandBuilt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.H = hv.Hive.from_json("pose_pos")
        cls.M = cls.H.gate.mean(axis=0)
        cls.n = cls.H.normal_out

    def test_straight_in_along_normal_is_clean(self):
        pts = np.array([self.M + s * self.n for s in np.linspace(0.6, -0.05, 60)])
        d = hv.classify_detail(pts, "pose_pos", "pos", frame="hive")
        self.assertEqual(d["result"], "clean")
        self.assertGreater(d["min_clearance"], 0.1)
        self.assertTrue(d["favorable"])

    def test_parabola_into_mouth_is_clean(self):
        ve = -3.0 * self.n                      # arrives at the gate centre moving inward
        t = np.linspace(-0.6, 0.02, 400)
        P = np.column_stack([self.M[0] + ve[0] * t, self.M[1] + ve[1] * t - 0.5 * G * t ** 2])
        self.assertEqual(hv.classify(P, "pose_pos", "pos", frame="hive"), "clean")

    def test_horizontal_line_hits_first_obstacle(self):
        L = np.column_stack([np.linspace(1.5, -1.5, 3001), np.full(3001, 1.0)])
        d = hv.classify_detail(L, "pose_pos", "pos", frame="hive")
        self.assertTrue(d["result"].startswith("hit:"))
        # independent check: first sample with point clearance < 0
        c, j = self.H.clearance(L)
        k = int(np.nonzero(c < 0)[0][0])
        self.assertEqual(d["hit"], self.H.names[int(j[k])])

    def test_parabola_from_wrong_side_hits(self):
        # same entry velocity but reversed horizontally: comes from the back of the up cell
        ve = np.array([3.0 * self.n[0], -3.0 * self.n[1]])
        t = np.linspace(-0.6, 0.02, 400)
        P = np.column_stack([self.M[0] + ve[0] * t, self.M[1] + ve[1] * t - 0.5 * G * t ** 2])
        r = hv.classify(P, "pose_pos", "neg", frame="hive")
        self.assertTrue(r.startswith("hit:"), r)

    def test_far_path_misses(self):
        L = np.column_stack([np.linspace(-1.75, -1.6, 10), np.full(10, 0.3)])
        self.assertEqual(hv.classify(L, "pose_pos", "neg", frame="hive"), "miss")

    def test_frames(self):
        # the clean straight path above is in the HIVE frame of a "pos"-side shooter (vx < 0)
        pts = np.array([self.M + s * self.n for s in np.linspace(0.6, -0.05, 60)])
        self.assertEqual(hv.classify(pts, "pose_pos", "pos"), "clean")            # auto: vx<0
        shot = pts * np.array([-1.0, 1.0])                                         # shot frame
        self.assertEqual(hv.classify(shot, "pose_pos", "pos"), "clean")           # auto: vx>0
        self.assertEqual(hv.classify(shot, "pose_pos", "pos", frame="shot"), "clean")
        self.assertNotEqual(hv.classify(shot, "pose_pos", "pos", frame="hive"), "clean")
        # pose_neg / neg side is the mirror image
        self.assertEqual(hv.classify(shot, "pose_neg", "neg"), "clean")


class TestSweepMethod(unittest.TestCase):
    def test_batch_rk4_matches_flight(self):
        for cl, S in ((None, 0.0), ("nominal", 1.0), ("high", 2.0)):
            prm = fz.aero_case("t", Cl=cl, k="high")
            for v, th in ((6.5, 78.0), (9.0, 45.0)):
                fam = fz.integrate_batch(np.array([v]), np.array([th]), S, prm, t_max=1.5,
                                         z_stop=-5)
                a = math.radians(th)
                v0 = np.array([v * math.cos(a), 0, v * math.sin(a)])
                w = fl.backspin_omega(v0, S * v / prm["radius"]) if S else np.zeros(3)
                tr = fl.simulate([0, 0, 0], v0, w, prm, t_max=1.5, z_ground=None)
                P = np.array([tr.sol(t)[[0, 2]] for t in fam["t"]])
                err = np.hypot(P[:, 0] - fam["X"][0], P[:, 1] - fam["Z"][0]).max()
                self.assertLess(err, 1e-5)

    def test_reversal_flag(self):
        g = fz.SweepGrid(v=np.array([7.0]), theta=np.array([60.0, 89.0]), h=np.array([0.5]),
                         d=np.array([1.0, 1.05]))
        geo = [fz.Geometry.make(favorable=False, res=2e-3)]
        r0 = fz.run_family(fz.aero_case("d"), 0.0, g, geo)
        r2 = fz.run_family(fz.aero_case("s", Cl="high", k="low"), 2.0, g, geo)
        self.assertFalse(r0["_paths"]["rev"].any())
        self.assertTrue(bool(r2["_paths"]["rev"][0, 1]))     # 89 deg with strong backspin
        self.assertFalse(bool(r2["_paths"]["rev"][0, 0]))    # 60 deg: no reversal

    def test_gate_sweep_agrees_with_exact_classify(self):
        g = fz.SweepGrid(v=np.round(np.arange(6.0, 9.01, 0.25), 3),
                         theta=np.round(np.arange(70.0, 88.01, 0.5), 3),
                         h=np.array([0.737]), d=np.array([1.0, 1.15]))
        prm = fz.aero_case("drag")
        geo = fz.Geometry.make(favorable=False)
        res = fz.run_family(prm, 0.0, g, [geo])["unfav_t30"]
        clean, margin = res["clean"][0], res["margin"][0]
        self.assertGreater(clean.sum(), 0)
        checked = 0
        for idd, d in enumerate(g.d):
            for iv, v in enumerate(g.v):
                for it, th in enumerate(g.theta):
                    x0, v0 = fz._shot(0.737, float(d), float(v), float(th))
                    if not clean[idd, iv, it] and (iv + it) % 4:
                        continue                       # subsample the non-clean cells
                    tr = fl.simulate(x0, v0, np.zeros(3), prm, t_max=2.0, dt_max=1e-3)
                    det = hv.classify_detail(tr, "pose_pos", "neg")
                    if abs(det["min_clearance"]) < 3e-3:
                        continue                       # within raster/time-step resolution
                    self.assertEqual(det["result"] == "clean", bool(clean[idd, iv, it]),
                                     (d, v, th, det["result"], det["min_clearance"]))
                    checked += 1
        self.assertGreater(checked, 50)

    def test_mirror_equivalence(self):
        a, n = fz.check_mirror(n=12)
        self.assertEqual(a, n)


if __name__ == "__main__":
    unittest.main()
