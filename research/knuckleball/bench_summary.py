"""Summarise the solver benchmark runs (bench_*.csv) written with prof=1.

Usage: python -B bench_summary.py <runs_dir> [out.json]

For each bench_<name>.csv it reads the "# runtime_s" line and the "# prof" lines and prints
wall time, finest-equivalent MLUPs, and the GPU time share per kernel (summed over levels).
Runs without prof lines (bench_noprof) show only the runtime line.
"""
import glob
import json
import os
import re
import sys


def parse(path):
    out = {"kernels": {}}
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not line.startswith("#"):
                continue
            kv = dict(re.findall(r"(\w+)=([^\s]+)", line))
            if line.startswith("# runtime_s"):
                out["runtime_s"] = float(kv["runtime_s"])
                out["steps"] = int(kv["steps"])
                out["MLUPs"] = float(kv["MLUPs"])
                out["finest_MLUPs"] = float(kv["finest_equivalent_MLUPs"])
            elif line.startswith("# prof kernel="):
                k = out["kernels"].setdefault(kv["kernel"], {"gpu_ms": 0.0, "calls": 0})
                k["gpu_ms"] += float(kv["gpu_ms"])
                k["calls"] += int(kv["calls"])
            elif line.startswith("# prof total_gpu_s"):
                out["total_gpu_s"] = float(kv["total_gpu_s"])
    tot = out.get("total_gpu_s")
    if tot:
        for k in out["kernels"].values():
            k["share"] = k["gpu_ms"] / 1e3 / tot
    return out


def main():
    runs = sys.argv[1]
    res = {}
    for f in sorted(glob.glob(os.path.join(runs, "bench_*.csv"))):
        res[os.path.basename(f)[:-4]] = parse(f)
    base = res.get("bench_noprof", {}).get("finest_MLUPs")
    print("%-14s %8s %10s %7s  %s" % ("bench", "wall_s", "fineMLUPs", "vs_base", "GPU share: stream_collide / body_force / coalesce / geo_q"))
    for n, r in res.items():
        if "finest_MLUPs" not in r:
            print("%-14s (no runtime line)" % n)
            continue
        ks = r["kernels"]
        sh = " / ".join("%.3f" % ks.get(k, {}).get("share", float("nan")) for k in ("stream_collide", "body_force", "coalesce", "geo_q"))
        rel = r["finest_MLUPs"] / base if base else float("nan")
        print("%-14s %8.1f %10.1f %7.3f  %s" % (n, r["runtime_s"], r["finest_MLUPs"], rel, sh if ks else "-"))
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w") as fh:
            json.dump(res, fh, indent=1)


if __name__ == "__main__":
    main()
