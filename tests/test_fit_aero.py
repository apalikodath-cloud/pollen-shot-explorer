"""PM-018 measurement kit: src/fit_aero.py and viz/measure/measure.js against viz/explorer/physics.js.

Synthetic tracks come from physics.js integrate (the explorer's flight model) with click noise added; both fitters must
get back the known Cd and Cl within their own stated error, agree with each other, and say when a shot cannot set a
parameter. The truths used here (v 7 m/s, 55 deg, Cd 0.5, Cl = min(0.35 S, 0.25), S0 1) are ASSUMED synthetic values,
not POLLEN measurements.
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
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from src import fit_aero as fa  # noqa: E402

MEASURE_JS = os.path.join(ROOT, "viz", "measure", "measure.js").replace("\\", "/")

# Reads one JSON job list on stdin, runs each job with measure.js (which calls physics.js), prints JSON results.
NODE_RUNNER = r"""
const M = require(process.argv[1]);
let buf = "";
process.stdin.on("data", d => buf += d);
process.stdin.on("end", () => {
  const out = JSON.parse(buf).map(job => {
    if (job.op === "synth") { const s = M.synth(job.truth, job.o); return { t: s.t, x: s.x, z: s.z }; }
    if (job.op === "sim") { const a = job.a; const s = M.simulate(a.t, a.x0, a.z0, a.vx0, a.vz0, a.Cd, a.lift, a.lp, a.spin, a.p);
                            return { x: Array.from(s.x), z: Array.from(s.z) }; }
    if (job.op === "fitA") { const f = M.fitNoSpin(job.track, job.opts || {});
                             return { value: f.value, sd: f.sd, sd_total: f.sd_total, flags: f.flags, rms_m: f.rms_m, v0: f.v0 }; }
    if (job.op === "fitB") { const f = M.fitLift(job.track, job.opts);
                             return { value: f.value, sd: f.sd, sd_total: f.sd_total, flags: f.flags, S0: f.S0,
                                      lift_detected: f.lift_detected, twin_dmax: f.twin_dmax, table: f.table }; }
    if (job.op === "csv") return { text: M.toCSV(job.meta, job.rows) };
    throw new Error("unknown op " + job.op);
  });
  process.stdout.write(JSON.stringify(out));
});
"""

TRUTH = {"v": 7.0, "thDeg": 55.0, "x0": 0.3, "z0": 0.35, "Cd": 0.5}
TRUTH_B = dict(TRUTH, lift="capped", lp=[0.35, 0.25], S0=1.0)      # explorer nominal lift (ASSUMED)
TRACK_OPTS = {"fps": 240, "frames": 170, "step": 2, "sigma": 0.004}  # 85 clicks, 4 mm noise per coordinate


def _node():
    node = shutil.which("node")
    if not node:
        raise unittest.SkipTest("node not installed")
    return node


def _run(jobs):
    res = subprocess.run([_node(), "-e", NODE_RUNNER, MEASURE_JS], input=json.dumps(jobs), capture_output=True,
                         text=True, timeout=600)
    if res.returncode != 0:
        raise AssertionError(res.stderr)
    return json.loads(res.stdout)


def _synth(truth, seed, **kw):
    return {"op": "synth", "truth": truth, "o": dict(TRACK_OPTS, seed=seed, **kw)}


class TestSameFlightModel(unittest.TestCase):
    def test_python_simulate_matches_physics_js(self):
        t = list(np.linspace(0.0, 0.7, 57))
        cases = [
            dict(Cd=0.5, lift=None, lp=[], spin=None),
            dict(Cd=0.33, lift="single", lp=[0.2], spin={"S0": 1.0}),
            dict(Cd=0.9, lift="linear", lp=[0.3], spin={"S0": 0.6}),
            dict(Cd=0.5, lift="capped", lp=[0.35, 0.25], spin={"S0": 1.0}),
            dict(Cd=0.5, lift="capped", lp=[0.35, 0.25], spin={"rpm": 2400.0}),
            dict(Cd=0.5, lift="single", lp=[0.2], spin={"rpm": -1500.0}, p={"k": 0.5, "rho": 1.1}),
        ]
        jobs = [{"op": "sim", "a": dict(c, t=t, x0=0.1, z0=0.4, vx0=4.0, vz0=5.7, p=c.get("p"))} for c in cases]
        for c, js in zip(cases, _run(jobs)):
            x, z = fa.simulate(t, 0.1, 0.4, 4.0, 5.7, c["Cd"], c["lift"], c["lp"], c["spin"], c.get("p"))
            self.assertLess(float(np.max(np.abs(x - np.array(js["x"])))), 1e-9, c)
            self.assertLess(float(np.max(np.abs(z - np.array(js["z"])))), 1e-9, c)


class TestRecovery(unittest.TestCase):
    """Fits of noisy physics.js tracks: the known truth must sit inside the stated error."""

    @classmethod
    def setUpClass(cls):
        cls.seeds = list(range(1, 21))
        jobs = [_synth(TRUTH, s) for s in cls.seeds] + [_synth(TRUTH_B, 100 + s) for s in cls.seeds]
        tr = _run(jobs)
        cls.A, cls.B = tr[:len(cls.seeds)], tr[len(cls.seeds):]
        cls.pyA = [fa.fit_nospin(a["t"], a["x"], a["z"]) for a in cls.A]
        cls.pyB = [fa.fit_lift(b["t"], b["x"], b["z"], ra["value"]["Cd"], ra["sd"]["Cd"], lift="single",
                               spin={"S0": 1.0}) for b, ra in zip(cls.B, cls.pyA)]
        js = _run([{"op": "fitA", "track": a} for a in cls.A])
        cls.jsA = js
        cls.jsB = _run([{"op": "fitB", "track": b, "opts": {"cd": ra["value"]["Cd"], "cdSd": ra["sd"]["Cd"],
                                                             "lift": "single", "spin": {"S0": 1.0}}}
                        for b, ra in zip(cls.B, js)])

    def _coverage(self, fits, nm, truth, sd_key):
        z = [(f["value"][nm] - truth) / f[sd_key][nm] for f in fits]
        inside = sum(abs(v) < 1.96 for v in z) / len(z)
        return z, inside

    def test_python_cd_within_stated_error(self):
        z, inside = self._coverage(self.pyA, "Cd", 0.5, "sd")
        self.assertTrue(all(abs(v) < 3.5 for v in z), z)
        self.assertGreaterEqual(inside, 0.8, z)          # 95 % intervals: at least 16 of 20 cover the truth
        self.assertLess(abs(float(np.mean(z))), 0.6, z)  # no bias beyond noise

    def test_python_cl_within_stated_error(self):
        # S >= 1 along the whole track, so min(0.35 S, 0.25) is 0.25 everywhere: one Cl is the right model
        z, inside = self._coverage(self.pyB, "Cl", 0.25, "sd_total")
        self.assertTrue(all(abs(v) < 3.5 for v in z), z)
        self.assertGreaterEqual(inside, 0.8, z)
        self.assertTrue(all(f["lift_detected"] for f in self.pyB))

    def test_js_recovers_the_same(self):
        zA, inA = self._coverage(self.jsA, "Cd", 0.5, "sd")
        zB, inB = self._coverage(self.jsB, "Cl", 0.25, "sd_total")
        self.assertGreaterEqual(inA, 0.8, zA)
        self.assertGreaterEqual(inB, 0.8, zB)

    def test_js_and_python_agree(self):
        for py, js in zip(self.pyA, self.jsA):
            self.assertAlmostEqual(py["value"]["Cd"], js["value"]["Cd"], delta=0.02 * py["sd"]["Cd"])
            self.assertAlmostEqual(py["sd"]["Cd"], js["sd"]["Cd"], delta=0.02 * py["sd"]["Cd"])
            self.assertAlmostEqual(py["rms_m"], js["rms_m"], delta=1e-6)
        for py, js in zip(self.pyB, self.jsB):
            self.assertAlmostEqual(py["value"]["Cl"], js["value"]["Cl"], delta=0.05 * py["sd"]["Cl"])
            self.assertAlmostEqual(py["sd_total"]["Cl"], js["sd_total"]["Cl"], delta=0.05 * py["sd_total"]["Cl"])
            self.assertEqual(py["table"], js["table"])

    def test_noiseless_track_is_exact(self):
        a = _run([_synth(TRUTH, 1, sigma=0.0)])[0]
        r = fa.fit_nospin(a["t"], a["x"], a["z"])
        self.assertAlmostEqual(r["value"]["Cd"], 0.5, places=6)
        self.assertAlmostEqual(r["v0"], 7.0, places=5)
        self.assertAlmostEqual(r["theta_deg"], 55.0, places=4)


class TestIdentifiability(unittest.TestCase):
    """The fitter must say when the data cannot set a parameter, not print a number as if it could."""

    @classmethod
    def setUpClass(cls):
        cls.A, cls.B = _run([_synth(TRUTH, 7), _synth(TRUTH_B, 8)])
        cls.ra = fa.fit_nospin(cls.A["t"], cls.A["x"], cls.A["z"])
        cls.cd, cls.cd_sd = cls.ra["value"]["Cd"], cls.ra["sd"]["Cd"]

    def test_single_cl_cannot_set_spin(self):
        r = fa.fit_lift(self.B["t"], self.B["x"], self.B["z"], self.cd, self.cd_sd, lift="single",
                        spin={"S0": 1.0}, fit_spin=True)
        self.assertTrue(any("does not depend on S0" in f for f in r["flags"]), r["flags"])

    def test_slope_with_cap_active_everywhere_is_flagged(self):
        r = fa.fit_lift(self.B["t"], self.B["x"], self.B["z"], self.cd, self.cd_sd, lift="capped",
                        spin={"S0": 1.0})
        self.assertTrue(any("does not depend on c1" in f for f in r["flags"]), r["flags"])
        self.assertAlmostEqual(r["value"]["Cl_max"], 0.25, delta=3 * r["sd_total"]["Cl_max"])

    def test_linear_slope_and_spin_not_separable(self):
        r = fa.fit_lift(self.B["t"], self.B["x"], self.B["z"], self.cd, self.cd_sd, lift="linear",
                        spin={"S0": 1.0}, fit_spin=True)
        self.assertTrue(any("c1" in f and "S0" in f for f in r["flags"]), r["flags"])

    def test_no_spin_shot_shows_no_lift(self):
        # the twin itself: fitting lift on the no-spin track must not report lift (95 % interval includes 0)
        r = fa.fit_lift(self.A["t"], self.A["x"], self.A["z"], self.cd, self.cd_sd, lift="single", spin={"S0": 1.0})
        self.assertFalse(r["lift_detected"], (r["value"]["Cl"], r["sd_total"]["Cl"]))
        self.assertTrue(r["twin_dmax"] < 0.03)

    def test_clean_fit_has_no_flags(self):
        self.assertEqual(self.ra["flags"], [])

    def test_bootstrap_agrees_with_jacobian(self):
        r = fa.fit_nospin(self.A["t"], self.A["x"], self.A["z"], boot=60)
        self.assertGreater(r["boot"]["Cd"]["sd"], 0.6 * r["sd"]["Cd"])
        self.assertLess(r["boot"]["Cd"]["sd"], 1.6 * r["sd"]["Cd"])


def _scaled(tr, k):
    return {"t": tr["t"], "x": [v * k for v in tr["x"]], "z": [v * k for v in tr["z"]]}


class TestScale(unittest.TestCase):
    """A wrong length scale biases Cd and Cl; shot A's gravity check must find it (derived, synthetic)."""

    K = 1.01   # video lengths 1 % too long, i.e. the clicked bar was 1 % short (synthetic)

    @classmethod
    def setUpClass(cls):
        A, B = _run([_synth(TRUTH, 11), _synth(TRUTH_B, 12)])
        cls.A, cls.B = _scaled(A, cls.K), _scaled(B, cls.K)
        cls.g = fa.fit_nospin(cls.A["t"], cls.A["x"], cls.A["z"], fit_scale=True)
        cls.js = _run([{"op": "fitA", "track": cls.A, "opts": {"fitScale": True}}])[0]

    def test_gravity_check_finds_the_scale(self):
        v, sd = self.g["value"]["len_scale"], self.g["sd"]["len_scale"]
        self.assertLess(abs(v - self.K), 3.5 * sd, (v, sd))
        self.assertLess(sd, 0.005)
        self.assertEqual(self.g["flags"], [])
        self.assertLess(abs(self.g["value"]["Cd"] - TRUTH["Cd"]), 3.5 * self.g["sd"]["Cd"])

    def test_unchecked_scale_biases_cd(self):
        r = fa.fit_nospin(self.A["t"], self.A["x"], self.A["z"])
        self.assertGreater(r["value"]["Cd"] - self.g["value"]["Cd"], 0.01)

    def test_lift_with_gravity_scale_recovers(self):
        ls, lsd = self.g["value"]["len_scale"], self.g["sd"]["len_scale"]
        r = fa.fit_lift(self.B["t"], self.B["x"], self.B["z"], self.g["value"]["Cd"], self.g["sd"]["Cd"],
                        lift="capped", spin={"S0": 1.0}, len_scale=ls, len_scale_sd=lsd)
        self.assertLess(abs(r["value"]["Cl_max"] - 0.25), 3.5 * r["sd_total"]["Cl_max"])

    def test_drop_far_from_origin_has_no_false_flag(self):
        # a drop from 4 m (synthetic): the scale is about the first tracked point, so z0 must not trade off against it
        t = np.arange(0, 0.95, 1 / 240)
        x, z = fa.simulate(t, 0.5, 4.2, 0.0, -0.01, 0.5)
        r = fa.fit_nospin(t, x * self.K, z * self.K, fit_scale=True)
        self.assertFalse(any("cannot separate" in f for f in r["flags"]), r["flags"])
        self.assertAlmostEqual(r["value"]["len_scale"], self.K, places=6)
        self.assertAlmostEqual(r["value"]["Cd"], 0.5, places=5)

    def test_js_gravity_check_agrees(self):
        for nm in ("len_scale", "Cd"):
            self.assertAlmostEqual(self.js["value"][nm], self.g["value"][nm], delta=0.05 * self.g["sd"][nm])
            self.assertAlmostEqual(self.js["sd"][nm], self.g["sd"][nm], delta=0.05 * self.g["sd"][nm])


class TestCsv(unittest.TestCase):
    def test_measure_csv_round_trip_and_report(self):
        A, B = _run([_synth(TRUTH, 3), _synth(TRUTH_B, 4)])
        rows = []
        for name, tr in (("A", A), ("B", B)):
            for i, (t, x, z) in enumerate(zip(tr["t"], tr["x"], tr["z"])):
                rows.append({"shot": name, "frame": 2 * i + 5, "t": t, "x": -x, "z": z, "px": 0, "py": 0})
        meta = {"m_per_px": 0.004, "level_deg": 0, "A.wheel_rpm": 5000, "B.S0": 1, "k": 0.03}
        text = _run([{"op": "csv", "meta": meta, "rows": rows}])[0]["text"]
        d = fa.parse_csv(text)
        self.assertEqual(sorted(d["shots"]), ["A", "B"])
        self.assertEqual(d["shots"]["A"]["meta"]["wheel_rpm"], "5000")
        self.assertAlmostEqual(d["shots"]["B"]["t"][0], 0.0)
        rep = fa.report(d)
        self.assertIn("Cd = ", rep)
        self.assertIn("no-spin twin", rep)
        self.assertIn("v/u = ", rep)
        self.assertIn("lift detected", rep)
        # x mirrored (ball flying toward -x) must give the same Cd as the original track
        ra = fa.fit_nospin(A["t"], A["x"], A["z"])
        rm = fa.fit_nospin(d["shots"]["A"]["t"], d["shots"]["A"]["x"], d["shots"]["A"]["z"])
        self.assertAlmostEqual(ra["value"]["Cd"], rm["value"]["Cd"], delta=0.01 * ra["sd"]["Cd"])

    def test_report_follows_page_spin_source(self):
        # the page keeps a typed ball rpm but writes B.S0 when its spin source is the ideal hood: use S0, as the page
        B = _run([_synth(TRUTH_B, 5)])[0]
        rows = [{"shot": "B", "frame": i, "t": t, "x": x, "z": z, "px": 0, "py": 0}
                for i, (t, x, z) in enumerate(zip(B["t"], B["x"], B["z"]))]
        base = {"m_per_px": 0.004, "B.ball_rpm": 9000}
        for meta, want in ((dict(base, **{"B.S0": 1}), "ASSUMED S0"), (base, "ball rpm, user")):
            text = _run([{"op": "csv", "meta": meta, "rows": rows}])[0]["text"]
            self.assertIn(want, fa.report(fa.parse_csv(text)))

    def test_rows_without_scale_are_skipped(self):
        text = "# m_per_px=\nshot,frame,t_s,x_m,z_m,x_px,y_px\nA,0,0.000000,NaN,NaN,10,20\nA,1,0.004,0.1,0.2,11,19\n"
        d = fa.parse_csv(text)
        self.assertEqual(len(d["shots"]["A"]["t"]), 1)


if __name__ == "__main__":
    unittest.main()
