"""viz/measure/assist.js pure helpers: telemetry parsing, column roles, time units, launch-dip detection and the
pre-launch readout. Runs under node; skipped if node is missing."""
import json
import os
import shutil
import subprocess
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ASSIST_JS = os.path.join(os.path.dirname(HERE), "viz", "measure", "assist.js").replace("\\", "/")

NODE_RUNNER = r"""
const A = require(process.argv[1]);
const out = {};
// header + comment + blank + bad row; semicolons win the delimiter vote
out.p1 = A.parseTelemetry("# robot log\n time ; wheel_rpm ; vbat \n\n0;100;12.5\n10;110;12.4\nfoo;bar;baz\n20;;12.3\n");
out.p2 = A.parseTelemetry("0\t1\t2\n1\t2\t3\n");            // no header -> col1..col3
out.p3 = A.parseTelemetry("");
out.roles = A.detectColumns(["time_ms", "target_rpm", "wheel_rpm", "battery_v", "power", "hood_pos"]);
out.roles2 = A.detectColumns(["t", "flywheel_vel_tps", "voltage", "servo"]);
out.roles3 = A.detectColumns(["a", "b"]);
out.sec = [A.toSeconds([1000, 1020, 1040], "time_ms"), A.toSeconds([5, 25, 45], "x"), A.toSeconds([0, 2e7, 4e7], "x"),
  A.toSeconds([3.0, 3.02, 3.04], "t")];
const parsed = A.parseTelemetry(A.demoTelemetry());
const roles = A.detectColumns(parsed.cols);
const tel = A.buildTel(parsed, roles, { speed: "rpm", ratio: 1 });
out.demoCols = parsed.cols; out.demoN = tel.t.length; out.demoT = [tel.t[0], tel.t[1], tel.t[tel.t.length - 1]];
out.dips = A.findDips(tel.t, tel.rpm);
out.read = out.dips.map(function (e) { return A.launchReadout(tel, e); });
// tps conversion with a gear ratio; rows out of time order are sorted; a row without speed is dropped
const pt = A.parseTelemetry("t,vel_tps\n0.04,560\n0.00,280\n0.02,\n0.06,0\n");
out.tps = A.buildTel(pt, A.detectColumns(pt.cols), { speed: "tps", tpr: 28, ratio: 2 });
// a clean step with no dip -> no events; one sharp 10 % dip -> one event at the fall
const t = [], flat = [], dip = [];
for (let k = 0; k < 200; k++) { t.push(k * 0.01); flat.push(3000); dip.push(k >= 100 && k < 120 ? 2700 : 3000); }
out.noDip = A.findDips(t, flat);
out.oneDip = A.findDips(t, dip);
out.median = [A.median([3, 1, 2]), A.median([4, 1, 3, 2]), A.median([NaN, 5])];
console.log(JSON.stringify(out));
"""


def _node():
    node = shutil.which("node")
    if not node:
        raise unittest.SkipTest("node not installed")
    return node


class TestAssist(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run([_node(), "-e", NODE_RUNNER, ASSIST_JS], capture_output=True, text=True, timeout=60)
        if p.returncode:
            raise AssertionError(p.stderr)
        cls.r = json.loads(p.stdout)

    def test_parse(self):
        p1 = self.r["p1"]
        self.assertEqual(p1["cols"], ["time", "wheel_rpm", "vbat"])
        self.assertEqual(len(p1["rows"]), 3)               # "foo;bar;baz" dropped
        self.assertEqual(p1["rows"][0], [0, 100, 12.5])
        self.assertIsNone(p1["rows"][2][1])               # empty cell -> NaN (null in JSON)
        self.assertEqual(self.r["p2"]["cols"], ["col1", "col2", "col3"])
        self.assertEqual(len(self.r["p2"]["rows"]), 2)
        self.assertEqual(self.r["p3"], {"cols": [], "rows": []})

    def test_roles(self):
        self.assertEqual(self.r["roles"], {"time": 0, "target": 1, "rpm": 2, "volts": 3, "power": 4, "hood": 5})
        r2 = self.r["roles2"]
        self.assertEqual((r2["time"], r2["rpm"], r2["volts"], r2["hood"], r2["power"], r2["target"]), (0, 1, 2, 3, -1, -1))
        self.assertEqual(self.r["roles3"]["time"], 0)   # falls back to the first column
        self.assertEqual(self.r["roles3"]["rpm"], -1)

    def test_time_units(self):
        for got, want in zip(self.r["sec"], [[0, 0.02, 0.04]] * 4):
            for g, w in zip(got, want):
                self.assertAlmostEqual(g, w, places=9)

    def test_demo_dips(self):
        self.assertEqual(self.r["demoCols"], ["time_ms", "target_rpm", "wheel_rpm", "battery_v", "power"])
        self.assertEqual(self.r["demoN"], 251)
        self.assertAlmostEqual(self.r["demoT"][1], 0.02)
        self.assertAlmostEqual(self.r["demoT"][2], 5.0)
        dips = self.r["dips"]
        self.assertEqual(len(dips), 2)
        for e, L in zip(dips, [1.2, 3.4]):
            self.assertLessEqual(abs(e["t"] - L), 0.041)       # launch within two samples
            self.assertGreater(e["drop"], 0.06)
            self.assertLess(e["drop"], 0.14)
            self.assertGreater(e["recover"], 0.1)
        for rd in self.r["read"]:
            self.assertLess(abs(rd["rpm"] / 3250 - 1), 0.02)    # wheel near target before the launch
            self.assertEqual(rd["target"], 3250)
            self.assertGreater(rd["volts"], 12.0)
            self.assertLess(rd["volts"], 12.3)

    def test_build_tel(self):
        tp = self.r["tps"]
        for g, w in zip(tp["t"], [0, 0.04, 0.06]):
            self.assertAlmostEqual(g, w, places=12)
        self.assertEqual(tp["rpm"], [280 / 28 * 60 * 2, 560 / 28 * 60 * 2, 0])
        self.assertIsNone(tp["volts"])

    def test_dip_detection_edges(self):
        self.assertEqual(self.r["noDip"], [])
        one = self.r["oneDip"]
        self.assertEqual(len(one), 1)
        self.assertAlmostEqual(one[0]["t"], 1.0)
        self.assertAlmostEqual(one[0]["drop"], 0.1)
        self.assertAlmostEqual(one[0]["recover"], 0.2)
        self.assertEqual(self.r["median"], [2, 2.5, 5])


if __name__ == "__main__":
    unittest.main()
