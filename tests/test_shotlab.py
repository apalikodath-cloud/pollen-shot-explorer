"""viz/measure/shotlab_worker.js: pure helpers (longest clean run, Spearman, Gaussian clean share, lip clearance)
and small map / lip / shoot-on-the-move jobs on the shot model. Runs under node; skipped if node is missing.
The job tests need the field data (viz/explorer/data/field/index.json, built by build_site); skipped without it."""
import json
import os
import shutil
import subprocess
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
VIZ = os.path.join(os.path.dirname(HERE), "viz")
FIELD = os.path.join(VIZ, "explorer", "data", "field", "index.json")


def _p(path):
    return path.replace("\\", "/")


HELPERS = r"""
const [viz] = process.argv.slice(1);
const PS = require(viz + "/explorer/solver.js"), C = require(viz + "/measure/shotcore.js");
const L = require(viz + "/measure/shotlab_worker.js")(PS, C);
const out = {};
out.runs = [L.longestRun([0, 1, 1, 0, 1, 1, 1, 0]), L.longestRun([0, 0]), L.longestRun([1, 1, 1]), L.longestRun([1, 0, 1])];
out.sp = [L.spearman([1, 2, 3, 4], [10, 20, 30, 45]).rho, L.spearman([1, 2, 3, 4], [4, 3, 2, 1]).rho,
          L.spearman([1, 2], [1, 2]).n, L.spearman([1, 2, NaN, 3, 4], [1, 4, 9, 9, 16]).n];
// 41 x 41 grid, clean where v index < 20: an interior cell deep in the clean half -> share 1; a cell on the border -> about half
const V = [], TH = [], clean = new Uint8Array(41 * 41);
for (let i = 0; i < 41; i++) { V.push(8 + i * 0.05); TH.push(78 + i * 0.1); }
for (let iv = 0; iv < 41; iv++) for (let it = 0; it < 41; it++) clean[iv * 41 + it] = iv < 20 ? 1 : 0;
const G = L.gaussShare(clean, V, TH, 0.005, 0.4);
out.g = { deep: G.share[5 * 41 + 20], border: G.share[19 * 41 + 20], dirty: G.share[30 * 41 + 20],
          edgeMid: G.edge[5 * 41 + 20], edgeCorner: G.edge[0], edgeTheta: G.edge[5 * 41 + 0] };
// straight path along x at z = 0.1 past a segment from (0, 0) to (1, 0): clearance 0.1 - R, uniform speed 2 m/s
const n = 11, path = { n, dt: 0.05, x: [], y: [], z: [] };
for (let i = 0; i < n; i++) { path.x.push(-0.5 + i * 0.1); path.y.push(0); path.z.push(0.1); }
out.lip = L.lipInfo(path, [[0, 0], [1, 0]], 0.0355, n - 1, 0.025);
out.lipUpto = L.lipInfo(path, [[0, 0], [1, 0]], 0.0355, 2, 0.025);   // only the first 3 points (x <= -0.3)
console.log(JSON.stringify(out));
"""

JOBS = r"""
const [viz, field] = process.argv.slice(1);
const PS = require(viz + "/explorer/solver.js"), C = require(viz + "/measure/shotcore.js");
const L = require(viz + "/measure/shotlab_worker.js")(PS, C);
const FI = require(field);
L.handle({ meta: { grid: FI.grid, sections: FI.sections, frame: FI.frame, field_grid: FI.field_grid,
                   cases: FI.cases.map(c => ({ S: c.S, var: c.var, params: c.params })) } }, () => {});
const cs = FI.cases.find(c => c.S === 1 && c.var === "nominal");
const q = () => ({ h: 0.737, S: 1.0, vu: 0.42, params: cs.params, air: { tC: 20, altM: 0, rh: 0 } });
const run = (job, o) => new Promise(res => { const prog = []; L.handle({ id: 1, job, q: q(), o }, m => { if ("progress" in m) prog.push(m.progress); if (m.result || m.error) res(Object.assign(m, { prog })); }); });
(async () => {
  const out = {};
  out.free = await run("map", { ds: [0.6, 0.8], mode: "free" });
  out.fixed = await run("map", { ds: [0.8], mode: "fixed", theta: 78, vLo: 5, vHi: 9, vStep: 0.05 });
  const lip = await run("lip", { d: 0.8, nearM: 0.01, vHalf: 2.0, vStep: 0.05, thHalf: 6, thStep: 0.1, mcCells: 6, mcN: 150, mcN2: 300 });
  const r = lip.result;
  out.lip = lip.error ? { error: lip.error } : { ok: r.ok, nClean: r.nClean, nUsed: r.nUsed, nEdge: r.nEdge, nNear: r.nNear, nTwinClean: r.nTwinClean,
    rho: [r.rhoClear.rho, r.rhoKE.rho, r.rhoMC.rho], rule: r.rule, robust: r.robust, mcN: r.mc.length,
    minCleanClear: Math.min(...r.clear.filter((c, k) => r.clean[k] && Number.isFinite(c))),
    nGrid: r.V.length * r.TH.length, prog: lip.prog.slice(-1)[0] };
  out.bad = await run("lip", { d: 0.6, nearM: 0.01, vHalf: 1, vStep: 0.1, thHalf: 2, thStep: 0.5, mcCells: 2, mcN: 10, mcN2: 10 });
  const m8 = out.free.result.rows[1].main;
  out.sotm = await run("sotm", { d: 0.8, along: 0, across: 0, comp: { v: m8.v, theta: m8.theta }, plain: { v: m8.v, theta: m8.theta } });
  console.log(JSON.stringify(out));
})().catch(e => { console.error(e); process.exit(1); });
"""


def _node():
    node = shutil.which("node")
    if not node:
        raise unittest.SkipTest("node not installed")
    return node


def _run(script, *args, timeout=120):
    p = subprocess.run([_node(), "-e", script, *args], capture_output=True, text=True, timeout=timeout)
    if p.returncode:
        raise AssertionError(p.stderr)
    return json.loads(p.stdout)


class TestShotLabHelpers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = _run(HELPERS, _p(VIZ))

    def test_longest_run(self):
        self.assertEqual(self.r["runs"], [{"lo": 4, "hi": 6}, None, {"lo": 0, "hi": 2}, {"lo": 0, "hi": 0}])

    def test_spearman(self):
        up, down, n_short, n_nan = self.r["sp"]
        self.assertAlmostEqual(up, 1.0)
        self.assertAlmostEqual(down, -1.0)
        self.assertEqual(n_short, 2)          # under 3 pairs: no rho
        self.assertEqual(n_nan, 4)            # the NaN pair is dropped

    def test_gauss_share(self):
        g = self.r["g"]
        self.assertAlmostEqual(g["deep"], 1.0, places=6)
        self.assertGreater(g["border"], 0.4)  # last clean row: about half the weight is on dirty cells
        self.assertLess(g["border"], 0.75)
        self.assertIsNone(g["dirty"])         # dirty cells get no share (NaN)
        self.assertEqual((g["edgeMid"], g["edgeCorner"], g["edgeTheta"]), (0, 1, 1))

    def test_lip_info(self):
        lip, upto = self.r["lip"], self.r["lipUpto"]
        self.assertAlmostEqual(lip["clear"], 0.1 - 0.0355, places=9)
        self.assertAlmostEqual(lip["vLip"], 2.0, places=9)
        self.assertAlmostEqual(lip["keLip"], 0.5 * 0.025 * 4.0, places=9)
        self.assertAlmostEqual(upto["clear"], ((0.3 ** 2 + 0.1 ** 2) ** 0.5) - 0.0355, places=9)
        self.assertEqual(upto["j"], 2)


@unittest.skipUnless(os.path.exists(FIELD), "field data not built (run viz/explorer/build_site.py)")
class TestShotLabJobs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = _run(JOBS, _p(VIZ), _p(FIELD), timeout=300)

    def test_free_map(self):
        rows = self.r["free"]["result"]["rows"]
        self.assertFalse(rows[0]["ok"])                       # d 0.6 at h 0.737: the robot does not fit
        r = rows[1]
        self.assertTrue(r["ok"])
        self.assertAlmostEqual(r["Lh"], 0.8 + 0.401, places=3)
        m = r["main"]
        self.assertTrue(6.5 < m["v"] < 9.5 and 75 < m["theta"] < 86, m)
        self.assertTrue(1.0 < m["tof"] < 1.8, m)
        self.assertAlmostEqual(m["rpm"], m["v"] / 0.42 * 60 / (3.141592653589793 * 0.098), delta=1)
        self.assertGreaterEqual(m["tol"], 0.05)               # at least one clean 0.05 m/s step either side
        self.assertGreaterEqual(m["tolTheta"], 0.1)
        self.assertIsNotNone(r["twin"])                       # S = 1: a no-spin twin is reported
        self.assertEqual(self.r["free"]["prog"][-1], 1)

    def test_fixed_map(self):
        m = self.r["fixed"]["result"]["rows"][0]["main"]
        self.assertEqual(m["theta"], 78)
        self.assertTrue(5.5 < m["v"] < 8 and m["tol"] > 0, m)

    def test_lip_job(self):
        L = self.r["lip"]
        self.assertTrue(L.get("ok"), L)
        self.assertEqual(L["nGrid"], 81 * 121)
        self.assertEqual(L["nClean"], L["nUsed"] + L["nEdge"])
        self.assertGreater(L["nUsed"], 50)
        self.assertGreater(L["nTwinClean"], 50)
        self.assertGreaterEqual(L["minCleanClear"], 0)        # clearance measured up to cell entry: clean never negative
        for rho in L["rho"]:
            self.assertTrue(rho is None or -1 <= rho <= 1)
        self.assertEqual(L["mcN"], 6)
        rule, rob = L["rule"], L["robust"]
        self.assertLessEqual(rule["clear"], 0.01)
        self.assertGreaterEqual(rob["share"], rule["share"])  # robust pick = the largest share among used cells
        for p in (rule, rob):
            self.assertFalse(p["edge"])
            self.assertTrue(0 <= p["hc"]["lo"] <= p["hc"]["p"] <= p["hc"]["hi"] <= 1, p)
            self.assertIsNotNone(p["twin"])                   # every backspin pick carries its no-spin twin
        self.assertEqual(L["prog"], 1)

    def test_lip_job_illegal_pose(self):
        b = self.r["bad"]["result"]
        self.assertFalse(b["ok"])
        self.assertIn("pose", b["reason"])

    def test_sotm_standing_still(self):
        s = self.r["sotm"]["result"]
        self.assertEqual(s["still"], "clean")                 # the map's own setting, robot not moving
        self.assertEqual(s["comp"]["result"], "clean")
        self.assertIn(s["comp"]["twin"], ("clean", "hit", "miss"))


if __name__ == "__main__":
    unittest.main()
