"""PM-017 best chance in Python against the browser copy: src/robustness.py best_chance replays the two-stage
search of viz/explorer/solver.js bestChance on the same candidate list with the same seeded draws (tests/
js_chance_check.js --dump), so the stage counts, the winner, the final counts and the one-source-at-a-time
breakdown must match exactly.

Every number here is model output (PREDICTED) under ASSUMED launch scatter and ASSUMED aero sets: a model
probability, not a measured repeatability.
"""
import json
import os
import shutil
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from src import cell3d, robustness as rb  # noqa: E402

SCRIPT = os.path.join(HERE, "js_chance_check.js")
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


class TestBestChanceJs(unittest.TestCase):
    def test_search_replay_matches(self):
        d = _dump()
        self.assertGreaterEqual(len(d["cases"]), 4)
        for c in d["cases"]:
            cell = cell3d.build_cell(d["sections"][c["side"]], ridge=c["ridge"], wall_t=c["wallT"])
            o = c["opts"]
            sig = {"sig_v_rel": c["sig"]["sv"], "sig_th": c["sig"]["sth"], "sig_psi": c["sig"]["spsi"]}
            py = rb.best_chance(cell, c["F"], {"S": c["S"], "h": c["h"], "z_stop": c["zStop"]}, c["setParams"],
                                c["candidates"], n1=o["n1"], n2=o["n2"], n=o["n"], k2=o["k2"], seed=c["seed"], sig=sig)
            tag = c["tag"]
            self.assertEqual([s["k"] for s in py["stage1"]], [s["k"] for s in c["stage1"]], tag + " stage 1")
            self.assertEqual([(s["v"], s["theta"], s["k"]) for s in py["stage2"]],
                             [(s["v"], s["theta"], s["k"]) for s in c["stage2"]], tag + " stage 2")
            self.assertEqual((py["v"], py["theta"]), (c["v"], c["theta"]), tag + " winner")
            for js, p in zip(c["sets"], py["sets"]):
                self.assertEqual(js["name"], p["name"])
                self.assertEqual(p["k"], js["k"], tag + " " + js["name"])
                self.assertAlmostEqual(p["lo"], js["lo"], places=12)
                self.assertAlmostEqual(p["hi"], js["hi"], places=12)
            self.assertEqual(py["breakdown"]["set"], c["breakdown"]["set"])
            self.assertEqual([p["k"] for p in py["breakdown"]["parts"]], [p["k"] for p in c["breakdown"]["parts"]], tag)
            self.assertEqual(py["breakdown"]["dominant"], c["breakdown"]["dominant"], tag)

    def test_node_checks(self):
        r = subprocess.run([_node(), SCRIPT], capture_output=True, text=True, timeout=900)
        if r.returncode == 77:
            self.skipTest("field data missing")
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])


if __name__ == "__main__":
    unittest.main()
