"""Tests for viz/explorer/export_field.py (whole-field oblique windows) and the JS oblique port."""
import json
import math
import os
import shutil
import subprocess
import sys
import unittest

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "viz", "explorer"))
from src import feasibility as fz  # noqa: E402
from src import robustness as rb  # noqa: E402
from src import shooter_spec as ss  # noqa: E402
import export_field as ef  # noqa: E402

SPEC_NOM = os.path.join(ss.CACHE, "S+1.0_nominal.npz")


def _fam(v, th, S=1.0, var="nominal"):
    fam = fz.integrate_batch(np.asarray(v, float), np.asarray(th, float), S, ef.aero(S, var), z_stop=0.4)
    fam["mono"] = np.all(np.diff(fam["X"], axis=1) >= 0, axis=1)
    return fam


class TestPsiZero(unittest.TestCase):
    @unittest.skipUnless(os.path.exists(SPEC_NOM), "data/_spec_cache missing")
    def test_psi0_reproduces_2d_windows(self):
        # same shots (subset of the 2D spec grid), psi = 0, compared with data/_spec_cache
        z = ss.load(1.0, "nominal")
        g = ss.grid()
        for side, gk in (("unfav", "unfav_t30"), ("fav", "fav_t30")):
            vs = np.round(np.arange(6.5, 8.5001, 0.05), 3) if side == "unfav" else np.round(np.arange(5.0, 7.0001, 0.1), 3)
            ths = np.round(np.arange(70.0, 86.0001, 0.2), 3) if side == "unfav" else np.round(np.arange(66.0, 86.0001, 0.5), 3)
            V, TH = np.meshgrid(vs, ths, indexing="ij")
            fam = _fam(V.ravel(), TH.ravel())
            tot = agree = 0
            ref_clean = 0
            for ih in (0, 4):
                cl, _, _ = ef.window_block(fam, side, 0.0, ef.H_LIST[ih])
                for idd, d in enumerate(ef.D_GRID):
                    j = np.flatnonzero(np.isclose(g.d, d))
                    if not j.size:
                        continue
                    iv = np.array([np.argmin(abs(g.v - v)) for v in V.ravel()])
                    it = np.array([np.argmin(abs(g.theta - t)) for t in TH.ravel()])
                    ref = z[gk + "__clean"][ih, j[0], iv, it]
                    mine = cl[idd]
                    tot += ref.size
                    agree += int((ref == mine).sum())
                    ref_clean += int(ref.sum())
            self.assertGreater(ref_clean, 50, side)
            self.assertGreaterEqual(agree / tot, 0.999, f"{side} {agree}/{tot}")


class TestMirror(unittest.TestCase):
    def test_mirror_symmetry_in_psi(self):
        # +psi and -psi give the same windows (model depends on |psi|) and mirrored 3D paths
        fam = _fam([7.5, 8.0, 7.0], [76.0, 78.0, 74.0])
        a = ef.window_block(fam, "unfav", 30.0, 0.737)[0]
        b = ef.window_block(fam, "unfav", -30.0, 0.737)[0]
        np.testing.assert_array_equal(a, b)
        self.assertEqual(ef.s_eff(-30.0), ef.s_eff(30.0))
        prm = ef.aero(1.0, "nominal")
        pp = []
        for psi in (30.0, -30.0):
            th, ps = math.radians(77.0), math.radians(psi)
            v0 = np.array([[8.0 * math.cos(th) * math.cos(ps), 8.0 * math.cos(th) * math.sin(ps), 8.0 * math.sin(th)]])
            w0 = rb.backspin_axis(v0) * (1.0 * 8.0 / prm["radius"])
            q = dict(rho=prm["rho"], mass=prm["mass"], radius=prm["radius"], Cd=prm["Cd"], c1=prm["Cl"][0],
                     clmax=prm["Cl"][1], k=prm["spin_decay_k"])
            pp.append(rb.integrate3d(np.zeros((1, 3)), v0, w0, q, dt=2e-3, t_max=1.0, z_stop=-9)["P"][0])
        np.testing.assert_allclose(pp[0][:, 0], pp[1][:, 0], atol=1e-6)
        np.testing.assert_allclose(pp[0][:, 1], -pp[1][:, 1], atol=1e-6)
        np.testing.assert_allclose(pp[0][:, 2], pp[1][:, 2], atol=1e-6)

    def test_cos_projection_matches_3d_path(self):
        # the in-plane flight scaled by cos(psi) is the x component of the 3D path (spin axis from v x z)
        prm = ef.aero(1.0, "nominal")
        v, th, psi = 8.0, 77.0, 40.0
        fam = fz.integrate_batch(np.array([v]), np.array([th]), 1.0, prm, z_stop=-9, t_max=1.0)
        t_, ps = math.radians(th), math.radians(psi)
        v0 = np.array([[v * math.cos(t_) * math.cos(ps), v * math.cos(t_) * math.sin(ps), v * math.sin(t_)]])
        w0 = rb.backspin_axis(v0) * (1.0 * v / prm["radius"])
        q = dict(rho=prm["rho"], mass=prm["mass"], radius=prm["radius"], Cd=prm["Cd"], c1=prm["Cl"][0],
                 clmax=prm["Cl"][1], k=prm["spin_decay_k"])
        P = rb.integrate3d(np.zeros((1, 3)), v0, w0, q, dt=2e-3, t_max=1.0, z_stop=-9)["P"][0]
        n = min(len(P), fam["X"].shape[1])
        np.testing.assert_allclose(P[:n, 0], fam["X"][0, :n] * math.cos(ps), atol=2e-4)
        np.testing.assert_allclose(P[:n, 2], fam["Z"][0, :n], atol=2e-4)


class TestLegalMask(unittest.TestCase):
    def test_illegal_positions_excluded(self):
        pos = ef.field_positions()
        xs, ys, _, _, legal = rb.field_grid(ef.FIELD_STEP)
        np.testing.assert_array_equal(pos["legal"], legal)
        self.assertTrue((pos["status"][~legal] == 1).all())
        self.assertTrue(((pos["status"] == 0) <= legal).all())
        self.assertTrue((pos["status"] == 0).any())
        # A-frame base centre is illegal; a point on the near side in the open is legal
        ix, iy = int(np.argmin(abs(pos["xs"] - 0.0))), int(np.argmin(abs(pos["ys"] - 0.3236)))
        self.assertEqual(pos["status"][iy, ix], 1)
        # sight line to the up cell crosses the other HIVE from (0.0, 1.6) region
        iy2 = int(np.argmin(abs(pos["ys"] - 1.6)))
        self.assertTrue(pos["other"][iy2, ix])

    @unittest.skipUnless(os.path.exists(os.path.join(ef.OUT, "pos_status.b64.txt")), "field data not generated")
    def test_exported_positions_zero_in_illegal(self):
        import base64
        idx = json.load(open(os.path.join(ef.OUT, "index.json")))
        pos = ef.field_positions()
        ny, nx = pos["X"].shape
        c = idx["cases"][0]
        for side in ("unfav", "fav"):
            raw = np.frombuffer(base64.b64decode(open(os.path.join(ef.OUT, c["files"][side]["pos_file"])).read()), "u1")
            n = len(ef.H_LIST) * ny * nx
            cnt = np.frombuffer(raw[: 2 * n].tobytes(), "<u2").reshape(len(ef.H_LIST), ny, nx)
            self.assertTrue((cnt[:, pos["status"] != 0] == 0).all())


@unittest.skipUnless(shutil.which("node"), "node not installed")
class TestJsPort(unittest.TestCase):
    def _run(self, payload):
        r = subprocess.run(["node", os.path.join(ROOT, "tests", "js_oblique_check.js"), "--stdin"],
                           input=json.dumps(payload), capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def test_js_trajectory_and_classification(self):
        # JS exact classifiers vs the Python raster windows (export_field.window_block), unfav side, both models:
        # 3D cell (classifyOblique3D, CELL_MODEL "cell3d", the PM-019 export) and the section model
        # (classifyOblique on the s_eff section, CELL_MODEL "section", still used by the page's sideWalls:false)
        S, var = 1.0, "nominal"
        prm = ef.aero(S, var)
        pj = dict(rho=prm["rho"], mass=prm["mass"], radius=prm["radius"], Cd=prm["Cd"], c1=prm["Cl"][0],
                  clmax=prm["Cl"][1], k=prm["spin_decay_k"], g=fz.G)
        secs = {}
        for side in ("unfav", "fav"):
            for psi in (0.0, 20.0, 40.0, 60.0):
                key = f"{side}_{ef.s_eff(psi):.4f}"
                h = ef.section_for(side, ef.s_eff(psi)).hive
                secs[key] = dict(names=list(h.names), P0=h.P0.tolist(), P1=h.P1.tolist(), inside=h.inside.tolist())
        secs["unfav_cell3d"] = fz.section_dict(ef.cell_geom("unfav", 0.0).hive)
        rng = np.random.default_rng(5)
        trajs = [dict(v=float(v), th=float(t), psi=float(p)) for v, t, p in
                 ((8.0, 77.0, 30.0), (6.0, 70.0, -45.0), (9.5, 80.0, 60.0))]
        N = 3000
        V = rng.uniform(6.0, 10.0, N); TH = rng.uniform(68.0, 86.0, N)
        fam = _fam(V, TH, S, var)
        shots, ref, model = [], [], []
        old = ef.CELL_MODEL
        try:
            for cm in ("cell3d", "section"):
                ef.CELL_MODEL = cm
                for psi in (0.0, 20.0, 40.0, 60.0):
                    g = ef.window_geom("unfav", psi)
                    for h in (0.35, 0.737):
                        cl, _, _ = ef.window_block(fam, "unfav", psi, h)
                        for _ in range(40):
                            idd, j = int(rng.integers(len(ef.D_GRID))), int(rng.integers(N))
                            # prefer clean-ish picks: half the draws come from existing clean cells
                            if _ % 2 == 0:
                                cc = np.argwhere(cl)
                                if len(cc):
                                    idd, j = (int(x) for x in cc[rng.integers(len(cc))])
                            sh = dict(v=float(V[j]), th=float(TH[j]), psi=psi, d=float(ef.D_GRID[idd]), h=h)
                            if cm == "cell3d":
                                sh.update(sec="unfav_cell3d", cell3d=True, aimX=float(g.aim_x))
                            else:
                                sh.update(sec=f"unfav_{ef.s_eff(psi):.4f}")
                            shots.append(sh)
                            ref.append(bool(cl[idd, j]))
                            model.append(cm)
        finally:
            ef.CELL_MODEL = old
        out = self._run(dict(p=pj, S=S, R=prm["radius"], trajs=trajs, shots=shots, secs=secs))
        for cm in ("cell3d", "section"):
            pr = [(a, b) for a, b, m in zip(out["cls"], ref, model) if m == cm]
            agree = sum(a == b for a, b in pr)
            self.assertGreater(sum(b for _, b in pr), 20, cm)
            self.assertGreaterEqual(agree / len(pr), 0.99, f"{cm} {agree}/{len(pr)}")
        # trajectory vs float64 3D integrator (robustness.integrate3d), < 1e-6 m
        for t, js in zip(trajs, out["traj"]):
            th, ps = math.radians(t["th"]), math.radians(t["psi"])
            v0 = np.array([[t["v"] * math.cos(th) * math.cos(ps), t["v"] * math.cos(th) * math.sin(ps),
                            t["v"] * math.sin(th)]])
            w0 = rb.backspin_axis(v0) * (S * t["v"] / prm["radius"])
            q = {k: pj[k] for k in ("rho", "mass", "radius", "Cd", "c1", "clmax", "k")}
            P = rb.integrate3d(np.zeros((1, 3)), v0, w0, q, dt=2e-3, t_max=1.2, z_stop=-9)["P"][0].astype(float)
            # float32 storage in integrate3d: compare at float32 resolution of the stored values
            for m, row in enumerate(js):
                self.assertLess(np.abs(np.array(row) - P[100 * m]).max(), 1e-6 + 6e-8 * np.abs(P[100 * m]).max())


if __name__ == "__main__":
    unittest.main()
