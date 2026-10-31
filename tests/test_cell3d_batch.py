"""Batched hit-chance kernels (speed only) give the same answers as the per-shot reference.

cell3d.classify_paths3d (all shots in one call, faces pruned by bounding box) vs cell3d.classify_path3d per shot,
and robustness.mc_cell_counts (several aims in one integration) vs one robustness.mc_shots call per aim, on the
page's default pose (live-solver plan, node). Exact equality: the batch must not change a single shot.
"""
import os
import shutil
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from src import cell3d as c3d  # noqa: E402
from src import robustness as rb  # noqa: E402
from src import spin_vs_twin as sv  # noqa: E402

_P = {}


def _plan():
    if not shutil.which("node"):
        raise unittest.SkipTest("node not installed")
    if not os.path.exists(sv.FIELD_INDEX):
        raise unittest.SkipTest("field data missing")
    if "p" not in _P:
        job = {"x": -1.0, "y": 0.2, "h": 0.737, "vu": 0.42, "kind": "robust", "S": 1.0, "id": "robust"}
        _P["p"] = sv.node_plans([job])[0]
    return _P["p"]


class TestBatchSameAsPerShot(unittest.TestCase):
    def setUp(self):
        self.p = _plan()
        self.assertTrue(self.p["candidates"])
        self.cell, self.F = sv.cell_for(self.p["secKey"]), self.p["F"]
        self.base = {"S": float(self.p["S"]), "h": float(self.p["h"]), "z_stop": float(self.p["zStop"])}
        # wider scatter than the page so clean, hit and miss shots all appear
        self.err = dict(rb.HC_SIG, sig_v_rel=0.04, sig_th=1.5, sig_psi=2.0)
        self.Z = rb.mulberry32_normals(7, 3 * 120).reshape(120, 3)

    def test_counts_and_paths(self):
        cands = self.p["candidates"][:6]
        for nm, prm3 in self.p["sets"].items():
            aims = [dict(self.base, v=c["v"], theta=c["theta"]) for c in cands]
            batch = rb.mc_cell_counts(aims, self.Z, self.err, self.cell, self.F, prm3)
            ref = [rb.mc_shots(a, n=len(self.Z), err=self.err, cell=self.cell, frame=self.F, prm3=prm3,
                               draws=self.Z)["k_clean"] for a in aims]
            self.assertEqual(batch, ref, nm)

    def test_classify_each_shot(self):
        c = self.p["candidates"][0]
        prm3 = next(iter(self.p["sets"].values()))
        r = rb.mc_shots(dict(self.base, v=c["v"], theta=c["theta"]), n=len(self.Z), err=self.err, cell=self.cell,
                        frame=self.F, prm3=prm3, draws=self.Z, return_paths=True)
        P, R = r["paths"], float(prm3["radius"])
        paths = [(P[i, :, 0], P[i, :, 1], P[i, :, 2]) for i in range(len(P))]
        ref = [c3d.classify_path3d(x, s, z, self.cell, R)["result"] for x, s, z in paths]
        self.assertEqual(c3d.classify_paths3d(paths, self.cell, R), ref)
        self.assertGreater(len(set(ref)), 1, "want a mix of outcomes")


if __name__ == "__main__":
    unittest.main()
