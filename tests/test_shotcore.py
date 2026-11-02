"""viz/measure/shotcore.js (shot-lab maths core): fits, battery-sag compensation, interpolation, shoot-on-the-move
virtual target, lip clearance, Wilson interval and the generated Java. Runs under node; skipped if node is missing.
The Java is compiled with javac when it is on PATH."""
import json
import os
import shutil
import subprocess
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CORE_JS = os.path.join(os.path.dirname(HERE), "viz", "measure", "shotcore.js").replace("\\", "/")

NODE_RUNNER = r"""
const C = require(process.argv[1]);
let s = 99;
const rnd = () => { s = (s * 1103515245 + 12345) & 0x7fffffff; return s / 0x7fffffff; };
const gauss = () => Math.sqrt(-2 * Math.log(1 - rnd())) * Math.cos(2 * Math.PI * rnd());
const out = {};
out.linExact = C.linfit([1, 2, 3, 4, 5], [3, 5, 7, 9, 11]);
const xs = [], ys = [];
for (let i = 0; i < 60; i++) { const x = i / 6; xs.push(x); ys.push(-1.5 * x + 4 + 0.3 * gauss()); }
out.linNoisy = C.linfit(xs, ys);
out.prop = C.propfit([1, 2, 3], [2, 4, 6]);
const u = (rpm) => Math.PI * 0.098 * rpm / 60;
const shots = [];
for (let r = 2000; r <= 5000; r += 500) shots.push({ rpm: r, v: 0.42 * u(r) });
shots.push({ rpm: 3000, v: 0 }, { rpm: -1, v: 3 }, { rpm: null, v: 3 });
out.transfer = C.transferFit(shots);
// telemetry: steady plateaus rpm = 480 * power * volts - 50 joined by fast spin-up ramps
const rows = [], ramp = [];
let t = 0;
[[0.5, 12.6], [0.7, 12.2], [0.9, 11.8], [0.6, 12.4]].forEach(([pw, v], k) => {
  const rpm = 480 * pw * v - 50;
  if (k) { const prev = rows[rows.length - 1].rpm; for (let j = 1; j <= 4; j++) { t += 0.02; ramp.push(rows.length); rows.push({ t, rpm: prev + (rpm - prev) * j / 5, volts: v, power: pw }); } }
  for (let j = 0; j < 40; j++) { t += 0.02; rows.push({ t, rpm: rpm + 3 * gauss(), volts: v + 0.005 * gauss(), power: pw }); }
});
rows.push({ t: t + 0.02, rpm: 10, volts: 12, power: 0.01 });
out.sag = C.sagFit(rows); out.ramp = ramp; out.nrows = rows.length;
const fit = { a: 480, b: -50 };
out.comp = C.compPower(3000, 12.5, fit); out.compBack = 480 * out.comp.power * 12.5 - 50;
out.compLow = C.compPower(6000, 11, fit); out.compNeg = C.compPower(-200, 12, fit); out.compBad = C.compPower(3000, 12, { a: -5, b: 0 });
out.interp = [C.interp1([0, 1, 2], [0, 2, 4], -1), C.interp1([0, 1, 2], [0, 2, 4], 9), C.interp1([0, 1, 2], [0, 2, 4], 0.25),
  C.interp1([0, 1, 2], [0, NaN, 4], 1.5), C.interp1([0, 1], [NaN, null], 0.5)];
const cx = [-2, -1, 0, 0.5, 1, 2, 3], cy = cx.map((x) => 1 - 2 * x + 0.5 * x * x - 0.25 * x * x * x);
out.poly = C.polyfit(cx, cy, 3); out.polyval = C.polyval([1, -2, 0.5, -0.25], 1.7);
out.sotm0 = C.sotm({ target: [4, 1], pos: [1, 1], vel: [0, 0], tof: (d) => d / 10 });
out.sotm1 = C.sotm({ target: [4, 1], pos: [0, 0], vel: [1, 0], tof: () => 1 });
const tg = [3, 2], ps = [0.5, -0.5], vl = [0.8, -0.6], lat = 0.05;
const r3 = C.sotm({ target: tg, pos: ps, vel: vl, lat, tof: (d) => d / 10 });
const P = [ps[0] + vl[0] * lat, ps[1] + vl[1] * lat], tf = Math.hypot(r3.virt[0] - P[0], r3.virt[1] - P[1]) / 10;
out.sotm2 = r3; out.sotm2res = Math.hypot(tg[0] - r3.virt[0] - vl[0] * tf, tg[1] - r3.virt[1] - vl[1] * tf);
out.heading = Math.atan2(r3.virt[1] - P[1], r3.virt[0] - P[0]);
const path = { x: [-1, 0, 1, 2, 3], z: [0.1, 0.1, 0.1, 0.1, -0.5] };
out.lip = C.lipClearance(path, [[-0.5, 0], [2.5, 0]], 0.03);
out.lipUpto = C.lipClearance({ x: [-3, -2, 0], z: [0.1, 0.1, 0.1] }, [[-0.5, 0], [2.5, 0]], 0.03, 1);
out.seg = [C.segDist(0, 1, -1, 0, 1, 0), C.segDist(3, 0, -1, 0, 1, 0)];
out.ke = C.entryKE(0.025, 3, 4);
out.rob = C.robustness([1, 1, 1, 1, 1, 1, 1, 1, 0, 0].map(Boolean));
out.java = { table: C.javaTable("ShotTable", [0.8, 1.2, 1.6, 100000], { rpm: [3990, 4300, 4700, 5000], hood_deg: [81.2, 80.1, 79, 78], tof: [0.61, 0.66, 0.7, 0.75] }),
  sag: C.javaSag(fit), sotm: C.javaSotm() };
console.log(JSON.stringify(out));
"""


def _node():
    node = shutil.which("node")
    if not node:
        raise unittest.SkipTest("node not installed")
    return node


class TestShotCore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run([_node(), "-e", NODE_RUNNER, CORE_JS], capture_output=True, text=True, timeout=60)
        if p.returncode:
            raise AssertionError(p.stderr)
        cls.r = json.loads(p.stdout)

    def test_linfit_and_propfit(self):
        e = self.r["linExact"]
        self.assertAlmostEqual(e["a"], 2, places=12)
        self.assertAlmostEqual(e["b"], 1, places=12)
        self.assertAlmostEqual(e["r2"], 1, places=12)
        self.assertLess(e["seA"], 1e-9)
        n = self.r["linNoisy"]
        self.assertLess(abs(n["a"] + 1.5), 3 * n["seA"])
        self.assertLess(abs(n["b"] - 4), 3 * n["seB"])
        self.assertAlmostEqual(self.r["prop"]["k"], 2, places=12)

    def test_transfer_fit_skips_bad_shots(self):
        tr = self.r["transfer"]
        self.assertAlmostEqual(tr["vu"]["k"], 0.42, places=9)
        self.assertEqual(tr["n"], 7)
        self.assertAlmostEqual(tr["lin"]["b"], 0, places=9)

    def test_sag_fit_drops_ramps(self):
        sg = self.r["sag"]
        self.assertLess(abs(sg["a"] / 480 - 1), 0.01)
        self.assertLess(abs(sg["b"] + 50), 25)
        used = set(sg["used"])
        self.assertFalse(used & set(self.r["ramp"]), "spin-up ramp rows must not be used")
        self.assertNotIn(self.r["nrows"] - 1, used)   # power below 0.05
        self.assertGreaterEqual(sg["n"], 150)

    def test_comp_power(self):
        self.assertAlmostEqual(self.r["compBack"], 3000, places=9)
        self.assertFalse(self.r["comp"]["clipped"])
        self.assertTrue(self.r["compLow"]["clipped"])
        self.assertEqual(self.r["compLow"]["power"], 1)
        self.assertTrue(self.r["compNeg"]["clipped"])
        self.assertEqual(self.r["compNeg"]["power"], 0)
        self.assertTrue(self.r["compBad"]["clipped"])        # a <= 0: no usable fit, no fake power
        self.assertIsNone(self.r["compBad"]["power"])

    def test_interp_and_poly(self):
        i = self.r["interp"]
        self.assertEqual(i[0], 0)
        self.assertEqual(i[1], 4)
        self.assertAlmostEqual(i[2], 0.5)
        self.assertAlmostEqual(i[3], 3)
        self.assertIsNone(i[4])   # NaN -> null in JSON
        for v, x in zip(self.r["poly"], [1, -2, 0.5, -0.25]):
            self.assertAlmostEqual(v, x, places=8)
        self.assertAlmostEqual(self.r["polyval"], 1 - 3.4 + 0.5 * 2.89 - 0.25 * 4.913, places=12)

    def test_sotm(self):
        s0 = self.r["sotm0"]
        self.assertEqual(s0["virt"], [4, 1])
        self.assertTrue(s0["converged"])
        self.assertAlmostEqual(s0["heading"], 0)
        s1 = self.r["sotm1"]
        self.assertAlmostEqual(s1["virt"][0], 3, places=12)
        self.assertAlmostEqual(s1["virt"][1], 1, places=12)
        self.assertTrue(s1["converged"])
        self.assertTrue(self.r["sotm2"]["converged"])
        self.assertLess(self.r["sotm2res"], 1e-6)
        self.assertAlmostEqual(self.r["sotm2"]["heading"], self.r["heading"], places=12)

    def test_lip_geometry(self):
        self.assertAlmostEqual(self.r["lip"], 0.07, places=12)
        # upto=1: only (-3, .1) and (-2, .1) count; the point over the lip (index 2) is ignored
        self.assertAlmostEqual(self.r["lipUpto"], (1.5 ** 2 + 0.1 ** 2) ** 0.5 - 0.03, places=12)
        self.assertAlmostEqual(self.r["seg"][0], 1)
        self.assertAlmostEqual(self.r["seg"][1], 2)
        self.assertAlmostEqual(self.r["ke"], 0.3125)

    def test_wilson(self):
        rb = self.r["rob"]
        self.assertAlmostEqual(rb["p"], 0.8)
        self.assertEqual(rb["n"], 10)
        self.assertAlmostEqual(rb["lo"], 0.4902, places=3)
        self.assertAlmostEqual(rb["hi"], 0.9433, places=3)

    def test_java(self):
        j = self.r["java"]
        self.assertIn("MODEL PREDICTIONS", j["table"])
        self.assertIn("HOOD_DEG", j["table"])
        self.assertIn("100000", j["table"])
        for s in j.values():
            self.assertEqual(s.count("{"), s.count("}"))
        javac = shutil.which("javac")
        if not javac:
            self.skipTest("javac not on PATH")
        d = tempfile.mkdtemp(prefix="shotcore_java_")
        try:
            with open(os.path.join(d, "ShotTable.java"), "w") as f:
                f.write(j["table"])
            with open(os.path.join(d, "Shooter.java"), "w") as f:
                f.write("public final class Shooter {\n" + j["sag"] + j["sotm"] + "}\n")
            p = subprocess.run([javac, "-d", d, os.path.join(d, "ShotTable.java"), os.path.join(d, "Shooter.java")],
                               capture_output=True, text=True, timeout=120)
            self.assertEqual(p.returncode, 0, p.stderr)
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
