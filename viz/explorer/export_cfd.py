"""Export finished POLLEN CFD runs (lattice-Boltzmann, PREDICTED) to a compact JSON for the explorer's CFD view.

Usage:  python viz/explorer/export_cfd.py RUNS_DIR [-o viz/explorer/cfd_runs.json]

RUNS_DIR is the folder of run CSVs (no default; its path is never written into the output).
Only runs whose id starts with p_ibb_ and whose CSV holds a '# runtime_s=' line (finished) are exported.
CSV: '#' lines are metadata; data rows are comma separated; 1-based columns 2 tstar, 9 Cd, 10 Cy, 11 Cl, 12 CM.
Means use the window 15 <= t* <= 150. Rerun to pick up runs that finish later.
"""
import argparse, json, math, re, sys
from pathlib import Path

WIN = (15.0, 150.0)
ID_RE = re.compile(r"^p_ibb_d(\d+)_(btw|hf|o3)(?:_Re(\d+)k)?_S([0-9.]+)$")
RE_DEFAULT = 33057
BIN = 1.0   # t* bin width for the downsampled history


def parse(path):
    m = ID_RE.match(path.stem)
    if not m:
        return None
    meta, rows, done = {}, [], False
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("#"):
                if line.startswith("# runtime_s="):
                    v = line.split("=", 1)[1].split()
                    if v and math.isfinite(float(v[0])):   # empty or malformed value: run counts as unfinished
                        done = True
                        meta["runtime_s"] = float(v[0])
                elif "body=" in line and "D=" in line and "meta" not in meta:
                    meta["meta"] = 1
                    for k, v in re.findall(r"\b(D|Re|S)=([0-9.eE+-]+)", line):
                        meta.setdefault(k, float(v))
                continue
            p = line.strip().split(",")
            if len(p) < 12:
                continue
            try:
                row = (float(p[1]), float(p[8]), float(p[10]), float(p[11]), float(p[9]))
            except ValueError:
                continue   # header row
            if all(math.isfinite(x) for x in row):   # NaN / inf never reach the JSON
                rows.append(row)
    if not done or not rows:
        return None
    D = int(m.group(1)); S = float(m.group(4))
    tag = int(m.group(3)) if m.group(3) else None
    Re_tag = {20: 20000, 47: 47224}.get(tag, RE_DEFAULT) if tag is not None else RE_DEFAULT
    if tag is not None and tag not in (20, 47):
        Re_tag = tag * 1000
    Re = meta.get("Re")
    if Re is None or not math.isfinite(Re) or abs(Re - Re_tag) > 0.02 * Re_tag:
        print(f"warn {path.stem}: header Re={Re} vs id tag {Re_tag}; using the tag", file=sys.stderr)
        Re = Re_tag
    Re = int(round(Re))
    sel = [r for r in rows if WIN[0] <= r[0] <= WIN[1]]
    if not sel:
        return None
    n = len(sel)
    mean = lambda i: sum(r[i] for r in sel) / n
    # downsample: mean of each BIN-wide t* bin over the whole run
    bins = {}
    for r in rows:
        bins.setdefault(int(r[0] // BIN), []).append(r)
    t, cd, cl = [], [], []
    for b in sorted(bins):
        g = bins[b]
        t.append(round(sum(x[0] for x in g) / len(g), 2))
        cd.append(round(sum(x[1] for x in g) / len(g), 4))
        cl.append(round(sum(x[2] for x in g) / len(g), 4))
    return {"id": path.stem, "D": D, "orient": m.group(2), "Re": Re, "S": S,
            "Cd": round(mean(1), 4), "Cy": round(mean(4), 4), "Cl": round(mean(2), 4), "CM": round(mean(3), 5),
            "n": n, "t_end": round(rows[-1][0], 1), "runtime_s": round(meta.get("runtime_s", 0)),
            "series": {"t": t, "Cd": cd, "Cl": cl}}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("runs_dir", type=Path)
    ap.add_argument("-o", "--out", type=Path, default=Path(__file__).parent / "cfd_runs.json")
    a = ap.parse_args()
    runs = []
    for p in sorted(a.runs_dir.glob("p_ibb_*.csv")):
        try:
            r = parse(p)
        except Exception as e:   # one bad CSV skips that run only
            print("skip", p.stem, f"({type(e).__name__}: {e})", file=sys.stderr)
            continue
        if r:
            runs.append(r)
        else:
            print("skip", p.stem, file=sys.stderr)
    runs.sort(key=lambda r: (r["D"], r["orient"], r["Re"], r["S"]))
    out = {"label": "PREDICTED", "window": list(WIN),
           "method": "D3Q19 lattice-Boltzmann LES, analytic POLLEN geometry with 26 holes, interpolated bounce-back walls",
           "runs": runs}
    a.out.write_text(json.dumps(out, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"wrote {a.out} ({a.out.stat().st_size/1e3:.0f} kB, {len(runs)} runs)")
    for r in runs:
        print(f"{r['id']:34s} Cd {r['Cd']:.4f} Cl {r['Cl']:.4f} CM {r['CM']:.5f}")


if __name__ == "__main__":
    main()
