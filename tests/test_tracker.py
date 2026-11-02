"""viz/measure/tracker.js (automatic ball tracker core) on synthetic frames: a yellow disk on a parabola over a
textured, noisy background. Checks accuracy, a full occlusion, a blue distractor ball, reverse tracking, predict and
refine. Runs under node; skipped if node is missing."""
import json
import os
import shutil
import statistics
import subprocess
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TRACKER_JS = os.path.join(os.path.dirname(HERE), "viz", "measure", "tracker.js").replace("\\", "/")

NODE_RUNNER = r"""
const T = require(process.argv[1]);
const W = 160, H = 120, N = 45, R = 6;
const truth = (f) => [10 + 3.2 * f, 100 - 4 * f + 0.09 * f * f];
function rng(s) { return () => { s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
// coverage of pixel (x, y) by a disk of radius r at (cx, cy), 4x4 supersampled (soft 1 px edge)
function cover(x, y, cx, cy, r) {
  if (Math.abs(x + 0.5 - cx) > r + 1 || Math.abs(y + 0.5 - cy) > r + 1) return 0;
  let k = 0; for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) if (Math.hypot(x + (i + 0.5) / 4 - cx, y + (j + 0.5) / 4 - cy) <= r) k++;
  return k / 16;
}
function frames(o) {
  const rnd = rng(12345), out = [];
  for (let f = 0; f < N; f++) {
    const d = new Uint8ClampedArray(W * H * 4), p = truth(f), q = o.distractor ? [150 - 3.0 * f, 30 + 1.6 * f] : null;
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const i = (y * W + x) * 4, n = (rnd() + rnd() + rnd() - 1.5) * 6;
      let g = 110 + x * 0.12 + y * 0.08 + n;
      if ((x > 55 && x < 70 && y > 30 && y < 42) || (x > 120 && x < 135 && y > 75 && y < 88)) g -= 35;
      let c = [g, g + 2, g + 4];
      const mix = (col, a) => { c = c.map((v, k) => col[k] * a + v * (1 - a)); };
      mix([235, 200, 40], cover(x, y, p[0], p[1], R));
      if (q) mix([40, 90, 230], cover(x, y, q[0], q[1], R));
      if (o.occlude && f >= 20 && f <= 21 && Math.abs(x + 0.5 - p[0]) < 9 && Math.abs(y + 0.5 - p[1]) < 9) c = [128, 128, 128];
      d[i] = c[0]; d[i + 1] = c[1]; d[i + 2] = c[2]; d[i + 3] = 255;
    }
    out.push({ data: d, w: W, h: H });
  }
  return out;
}
function errs(res) { return res.pts.map((p) => ({ f: p.f, e: Math.hypot(p.px - truth(p.f)[0], p.py - truth(p.f)[1]) })); }
async function run() {
  const out = {};
  const clean = frames({}), t0 = Date.now();
  const a = await T.track((i) => clean[i], { start: 0, end: N - 1, seed: truth(0), r: R });
  out.clean = { n: a.pts.length, stopped: a.stopped, errs: errs(a), ms: Date.now() - t0 };
  const occ = frames({ occlude: true });
  const b = await T.track((i) => Promise.resolve(occ[i]), { start: 0, end: N - 1, seed: truth(0), r: R });
  out.occ = { n: b.pts.length, stopped: b.stopped, errs: errs(b), frames: b.pts.map((p) => p.f) };
  const dis = frames({ distractor: true });
  const c = await T.track((i) => dis[i], { start: 0, end: N - 1, seed: truth(0), r: R });
  out.dis = { n: c.pts.length, stopped: c.stopped, errs: errs(c) };
  const d = await T.track((i) => clean[i], { start: N - 1, end: 0, step: -1, seed: truth(N - 1), r: R });
  out.rev = { n: d.pts.length, stopped: d.stopped, errs: errs(d) };
  const quad = (f) => 2 + 0.5 * f - 0.25 * f * f;
  out.pred = T.predict([{ f: 1, px: quad(1), py: -quad(1) }, { f: 3, px: quad(3), py: -quad(3) }, { f: 4, px: quad(4), py: -quad(4) }], 7);
  out.predTrue = quad(7);
  const pts = [0, 1, 2, 3, 4, 5].map((f) => ({ f, px: f * f, py: 2 * f, conf: f === 2 ? 0.2 : 0.9 }));
  pts[2].px += 5;
  out.ref = T.refine(pts);
  console.log(JSON.stringify(out));
}
run().catch((e) => { console.error(e.stack); process.exit(1); });
"""


def _node():
    node = shutil.which("node")
    if not node:
        raise unittest.SkipTest("node not installed")
    return node


class TestTracker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = subprocess.run([_node(), "-e", NODE_RUNNER, TRACKER_JS], capture_output=True, text=True, timeout=60)
        if p.returncode:
            raise AssertionError(p.stderr)
        cls.r = json.loads(p.stdout)

    def test_clean_track_is_subpixel(self):
        c = self.r["clean"]
        e = [x["e"] for x in c["errs"]]
        self.assertGreaterEqual(c["n"], 40)
        self.assertIn(c["stopped"], ("end", "left the frame"))
        self.assertLess(statistics.median(e), 0.25)
        self.assertLess(max(e), 0.8)
        self.assertLess(c["ms"], 2000)

    def test_full_occlusion_is_skipped_not_guessed(self):
        o = self.r["occ"]
        self.assertNotIn(20, o["frames"])
        self.assertNotIn(21, o["frames"])
        self.assertGreaterEqual(o["n"], 38)
        self.assertLess(max(x["e"] for x in o["errs"] if x["f"] >= 22), 1.0)

    def test_distractor_ball_is_ignored(self):
        d = self.r["dis"]
        self.assertGreaterEqual(d["n"], 40)
        self.assertLess(max(x["e"] for x in d["errs"]), 1.0)

    def test_reverse_direction(self):
        v = self.r["rev"]
        self.assertGreaterEqual(v["n"], 40)
        self.assertLess(max(x["e"] for x in v["errs"]), 0.8)

    def test_predict_exact_on_quadratic(self):
        self.assertAlmostEqual(self.r["pred"][0], self.r["predTrue"], places=9)
        self.assertAlmostEqual(self.r["pred"][1], -self.r["predTrue"], places=9)

    def test_refine_only_touches_low_confidence(self):
        ref = self.r["ref"]
        for f in (0, 1, 3, 4, 5):
            self.assertEqual(ref[f]["px"], f * f)
            self.assertNotIn("smoothed", ref[f])
        self.assertTrue(ref[2]["smoothed"])
        self.assertAlmostEqual(ref[2]["px"], 4.0, places=6)


if __name__ == "__main__":
    unittest.main()
