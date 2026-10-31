"""PM-021 backspin vs the no-spin twin (src/spin_vs_twin.py).

The Python Monte Carlo search (search = solver.js bestChance stages 1 to 3 through robustness.mc_shots) is checked
against the browser's own bestChance at the page's default pose (x -1.0, y 0.2, h 0.737 m, S 1.0, still air): the
Python chance of every lift set and of the no-spin twin must sit inside the JS Wilson 95 % interval, and the winner
setting must be the same. Smaller shot counts than the page (the Python port integrates every shot in numpy).

Every number is model output (PREDICTED) under ASSUMED launch scatter and ASSUMED aero: a model probability, not a
measured repeatability.
"""
import os
import shutil
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from src import spin_vs_twin as sv  # noqa: E402

SMALL = {"n1": 24, "n2": 72, "n": 300, "k2": 3}
DEFAULT = {"x": -1.0, "y": 0.2, "h": 0.737, "vu": 0.42, "js": True, "opts": SMALL}
_PLANS = {}


def _plans():
    if not shutil.which("node"):
        raise unittest.SkipTest("node not installed")
    if not os.path.exists(sv.FIELD_INDEX):
        raise unittest.SkipTest("field data missing")
    if "p" not in _PLANS:
        jobs = [dict(DEFAULT, kind="twin", id="twin"), dict(DEFAULT, kind="robust", S=1.0, id="robust"),
                dict(DEFAULT, kind="set", S=1.0, set="Cl_high", id="set")]
        _PLANS["p"] = {p["id"]: p for p in sv.node_plans(jobs)}
    return _PLANS["p"]


class TestDefaultPoseVsJs(unittest.TestCase):
    def _check(self, key):
        p = _plans()[key]
        self.assertEqual(p["status"], "ok")
        self.assertTrue(p["candidates"], key + ": no candidates")
        py = sv.search(p, **SMALL)
        js = p["js"]
        self.assertEqual((py["v"], py["theta"]), (js["v"], js["theta"]), key + " winner setting")
        self.assertEqual([r["name"] for r in py["sets"]], [r["name"] for r in js["sets"]])
        for a, b in zip(py["sets"], js["sets"]):
            self.assertEqual(a["n"], b["n"])
            self.assertTrue(b["lo"] - 1e-12 <= a["p"] <= b["hi"] + 1e-12,
                            f"{key} {a['name']}: python {a['p']:.3f} outside JS Wilson [{b['lo']:.3f}, {b['hi']:.3f}]")
        return py

    def test_robust_backspin(self):
        py = self._check("robust")
        self.assertEqual([r["name"] for r in py["sets"]], ["Cl_low", "nominal", "Cl_high"])

    def test_twin(self):
        py = self._check("twin")
        self.assertEqual([r["name"] for r in py["sets"]], ["no-spin twin"])

    def test_tuned_one_set(self):
        py = self._check("set")
        self.assertEqual([r["name"] for r in py["sets"]], ["Cl_high"])

    def test_grip_limit(self):
        for key, p in _plans().items():
            self.assertTrue(p["inCap"], key)
            self.assertTrue(all(c["v"] <= 8.9 + 1e-9 for c in p["candidates"]), key + ": candidate above the grip cap")


class TestTables(unittest.TestCase):
    def test_verdict(self):
        a = {"n": 1000, "lo": 0.30, "hi": 0.36}
        b = {"n": 1000, "lo": 0.10, "hi": 0.14}
        self.assertEqual(sv.verdict(a, b), "spin")
        self.assertEqual(sv.verdict(b, a), "twin")
        self.assertEqual(sv.verdict(a, {"n": 1000, "lo": 0.33, "hi": 0.40}), "unclear")
        z = {"n": 0, "lo": 0.0, "hi": 0.0}
        self.assertEqual(sv.verdict(z, z), "neither")
        self.assertEqual(sv.verdict(z, b), "twin")

    def test_saturation_check_keys(self):
        # the S 1.5 -> S 1.0 pairing swaps only the S field (x = 1.55 m also contains "|1.5")
        def rec(S, k):
            return {"S": S, "result": "ok", "v": 7.0, "theta": 70.0, "sets": [{"k": k}]}
        R = {"robust|1.55|0.4|0.5|1.5": rec(1.5, 10), "robust|1.55|0.4|0.5|1.0": rec(1.0, 10),
             "set|-1.55|1.2|0.35|1.5|Cl_low": rec(1.5, 4), "set|-1.55|1.2|0.35|1.0|Cl_low": rec(1.0, 5)}
        self.assertEqual(sv.saturation_check(R), (2, 1))

    def test_csv_labelled(self):
        if not os.path.exists(sv.CSV_OUT):
            self.skipTest("data/spin_vs_twin.csv not written yet")
        with open(sv.CSV_OUT, encoding="utf-8") as fh:
            head = fh.readline()
        self.assertIn("PREDICTED", head)
        self.assertIn("ASSUMED", head)
        self.assertIn("not a measured repeatability", head)
        rows = sv.read_csv()
        self.assertTrue(rows)
        for r in rows:
            if r["spin_n"]:
                self.assertLessEqual(float(r["spin_v"]), 8.9 + 1e-9)
                self.assertTrue(r["spin_lo"] <= r["spin_p"] <= r["spin_hi"])
            if r["twin_n"]:
                self.assertLessEqual(float(r["twin_v"]), 8.9 + 1e-9)
            self.assertIn(r["mode"], ("robust", "tuned"))


if __name__ == "__main__":
    unittest.main()
