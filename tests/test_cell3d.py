"""3D HIVE cell model (PM-013): src/cell3d.py against viz/explorer/physics.js classifyOblique3D, and the
node checks in tests/js_cell3d_check.js (psi = 0 identity, ridge stricter only, fused fast path, timing).

The cross-check takes >= 500 random shots (random side, d, signed psi 0..60, height, spin, ridge on/off,
wall thickness; clean and non-clean found by a coarse scan) with the exact JS path and compares result,
step index, hit face and minimum clearance. Skips when node or the gitignored field data is missing.
"""
import base64
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
from src import cell3d  # noqa: E402

SCRIPT = os.path.join(HERE, "js_cell3d_check.js")


def _node():
    node = shutil.which("node")
    if not node:
        raise unittest.SkipTest("node not installed")
    return node


class TestCell3dGeometry(unittest.TestCase):
    def test_seg_face_matches_sampling(self):
        rng = np.random.default_rng(5)
        f = cell3d.make_face("t", [[0, 0, 0], [1, 0, 0.2], [1, 1, 0.5], [0, 1, 0.3]])
        A = rng.uniform(-1, 2, (200, 3))
        B = A + rng.uniform(-0.3, 0.3, (200, 3))
        d = cell3d.seg_face(f, A, B)
        u, v = np.meshgrid(np.linspace(0, 1, 41), np.linspace(0, 1, 41))
        Q = np.column_stack([u.ravel(), v.ravel(), 0.2 * u.ravel() + 0.3 * v.ravel()])
        t = np.linspace(0, 1, 101)
        for i in range(len(A)):
            S = A[i] + t[:, None] * (B[i] - A[i])
            bf = np.min(np.sqrt(((S[:, None, :] - Q[None, :, :]) ** 2).sum(-1)))
            self.assertLessEqual(d[i], bf + 1e-9)       # exact distance never above a sampled one
            self.assertLess(bf - d[i], 0.03)            # and close to it (sampling step)


class TestCell3dJs(unittest.TestCase):
    def test_python_matches_js(self):
        node = _node()
        r = subprocess.run([node, SCRIPT, "--dump", "560"], capture_output=True, text=True, timeout=900)
        if r.returncode == 77:
            self.skipTest("field data missing: " + r.stdout.strip()[-200:])
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        data = json.loads(r.stdout)
        shots = data["shots"]
        self.assertGreaterEqual(len(shots), 500)
        cells = {}
        n_clean = n_hit = n_miss = 0
        for k, s in enumerate(shots):
            key = (s["side"], s["ridge"], s["wallT"])
            if key not in cells:
                cells[key] = cell3d.build_cell(data["sections"][s["side"]], ridge=s["ridge"], wall_t=s["wallT"])
            cell = cells[key]
            X = np.frombuffer(base64.b64decode(s["X"]), dtype="<f8")
            Z = np.frombuffer(base64.b64decode(s["Z"]), dtype="<f8")
            py = cell3d.classify_oblique3d(X, Z, cell, s["d"], s["h"], s["R"], s["aimX"], s["psi"])
            js = s["js"]
            msg = "shot %d %s" % (k, {q: s[q] for q in ("side", "d", "h", "psi", "v", "th", "S", "ridge", "wallT")})
            self.assertEqual(py["result"], js["result"], msg)
            self.assertEqual(py["i"], js["i"], msg)
            if js["minClear"] is None or not math.isfinite(py["min_clear"]):
                self.assertEqual(js["minClear"] is None, not math.isfinite(py["min_clear"]), msg)
            else:
                self.assertAlmostEqual(py["min_clear"], js["minClear"], delta=1e-9, msg=msg)
            if js["result"] == "hit":
                n_hit += 1
                if py["hit"] != js["hit"]:   # only a tie on a shared edge may name the other face
                    # (the two ridge halves of a roof part share one name)
                    i = js["i"]
                    tp = math.tan(math.radians(s["psi"]))
                    a = np.array([[X[i] - s["d"], (s["aimX"] - X[i] + s["d"]) * tp, Z[i] + s["h"]]])
                    b = np.array([[X[i + 1] - s["d"], (s["aimX"] - X[i + 1] + s["d"]) * tp, Z[i + 1] + s["h"]]])
                    dj = min(cell3d.seg_face(f, a, b)[0] for f in cell.faces if f.name == js["hit"])
                    dp = min(cell3d.seg_face(f, a, b)[0] for f in cell.faces if f.name == py["hit"])
                    self.assertAlmostEqual(dj, dp, delta=1e-12, msg=msg)
            elif js["result"] == "clean":
                n_clean += 1
                if js["entryAngle"] is not None:
                    self.assertAlmostEqual(py["entry_angle"], js["entryAngle"], delta=1e-9, msg=msg)
            else:
                n_miss += 1
        self.assertGreater(n_clean, 100)
        self.assertGreater(n_hit, 100)

    def test_js_checks(self):
        node = _node()
        r = subprocess.run([node, SCRIPT], capture_output=True, text=True, timeout=900)
        if r.returncode == 77:
            self.skipTest("field data missing: " + r.stdout.strip()[-200:])
        self.assertEqual(r.returncode, 0, r.stdout[-4000:] + r.stderr[-2000:])
        self.assertIn('"failed":0', r.stdout.strip().splitlines()[-1])


if __name__ == "__main__":
    unittest.main()
