"""Runs tests/js_solver_check.js (live shot solver, viz/explorer/solver.js) under node.

Skips when node is not installed or the gitignored field data (viz/explorer/data/field) is missing.
"""
import os
import shutil
import subprocess
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "js_solver_check.js")


class TestSolverJs(unittest.TestCase):
    def test_solver_js(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node not installed")
        r = subprocess.run([node, SCRIPT], capture_output=True, text=True, timeout=900)
        if r.returncode == 77:
            self.skipTest("field data missing: " + r.stdout.strip()[-200:])
        self.assertEqual(r.returncode, 0, r.stdout[-4000:] + r.stderr[-2000:])
        self.assertIn('"failed":0', r.stdout.strip().splitlines()[-1])


if __name__ == "__main__":
    unittest.main()
