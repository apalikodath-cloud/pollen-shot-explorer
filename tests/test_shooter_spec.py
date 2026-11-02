import math
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import shooter_spec as sp  # noqa: E402


class TestShooterSpec(unittest.TestCase):
    def test_best_square_finds_block(self):
        c = np.zeros((10, 12), bool)
        c[2:6, 3:8] = True          # 4 x 5 block -> largest square side 4
        k, i0, j0 = sp.best_square(c)
        self.assertEqual(k, 4)
        self.assertTrue(c[i0:i0 + k, j0:j0 + k].all())

    def test_best_square_empty(self):
        self.assertEqual(sp.best_square(np.zeros((4, 4), bool))[0], 0)

    def test_wheel_rpm(self):
        # v = u * ratio, u = pi D rpm / 60
        rpm = sp.wheel_rpm(6.0)
        for r, ratio in zip(rpm, sp.V_OVER_U):
            self.assertAlmostEqual(r, 6.0 / ratio / (math.pi * 0.098) * 60, delta=1)

    def test_longest_run(self):
        m = np.array([[0, 1, 1, 0, 1, 1, 1, 0], [0] * 8], bool)
        n, c = sp.longest_run(m)
        self.assertEqual(list(n), [3, 0])
        self.assertEqual(c[0], 5.0)
        self.assertTrue(np.isnan(c[1]))

    def test_spin_rpm(self):
        self.assertEqual(sp.spin_rpm(1.0, 0.0355 * 2 * math.pi), 60)

    def _grid(self, nv, nt):
        g = type("G", (), {})()
        g.v = np.round(5.0 + 0.05 * np.arange(nv), 3)
        g.theta = np.round(70.0 + 0.1 * np.arange(nt), 2)
        return g

    def test_fixed_elev_diagonal_band(self):
        # diagonal band, 3 v cells wide per elevation column, shifting 1 v cell per column
        nv, nt = 40, 20
        c = np.zeros((nv, nt), bool)
        for j in range(nt):
            c[j:j + 3, j] = True
        g = self._grid(nv, nt)
        e, lo, hi, _ = sp.fixed_elev(c, None, g, 0.0)          # exact elevation: full 3-cell run
        self.assertAlmostEqual(hi - lo, 0.10, places=6)
        e, lo, hi, _ = sp.fixed_elev(c, None, g, 0.1)          # +/-1 column: only the middle v cell
        self.assertAlmostEqual(hi - lo, 0.0, places=6)
        self.assertTrue(c[round((lo - 5.0) / 0.05), round((e - 70.0) / 0.1) - 1:
                          round((e - 70.0) / 0.1) + 2].all())
        self.assertIsNone(sp.fixed_elev(c, None, g, 0.2))       # +/-2 columns: band too thin

    def test_fixed_elev_prefers_wider_run(self):
        nv, nt = 30, 10
        c = np.zeros((nv, nt), bool)
        c[2:5, 3] = True
        c[10:20, 7] = True
        e, lo, hi, _ = sp.fixed_elev(c, None, self._grid(nv, nt), 0.0)
        self.assertAlmostEqual(e, 70.7, places=6)
        self.assertAlmostEqual(hi - lo, 0.45, places=6)


if __name__ == "__main__":
    unittest.main()
