"""Export the PM-012 CFD force records and wake profiles the explorer's flight model uses (all PREDICTED).

usage: python export_unsteady.py RUNS_DIR      (writes data/unsteady.json, and data/wake.json when wake runs exist)

data/unsteady.json  side / lift force records of the D128 POLLEN runs at Re 33k (every hole orientation and spin S
  that has a finished run): Cy(t) and Cl(t) minus the run mean, from t* = 30 (start-up left out) on a dtau = 0.25 D/u
  grid (block means of the CSV rows). The explorer adds them to a shot as the shedding buzz and the slow drift
  (knuckle switching at low spin): random start and, at S 0, a random roll about the flight direction.
data/wake.json      wake of the ball along its own path (runs p_wake_*): mean air velocity on the path line behind the
  ball, ground frame, as a fraction of the ball speed: ud along the flight (the air follows the ball), un across it
  in the lift direction (+ = up for backspin), from the field dumps (time mean of every dump), with a power-law fit of
  the far part for extrapolation beyond the CFD box.
"""
import glob, json, math, os, re, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DT, T0 = 0.25, 30.0
NAME = re.compile(r"^p_ibb_d128_(btw|hf|o\d)_S([0-9.]+)$")


def read_csv(f):
    rows, hdr = [], {}
    with open(f) as fh:
        for ln in fh:
            if ln.startswith("# PM-012"):
                hdr = dict(kv.split("=", 1) for kv in ln[2:].split() if "=" in kv)
            if ln[0] in "#s":
                continue
            p = ln.split(",")
            if len(p) == 12:
                rows.append([float(p[1]), float(p[9]), float(p[10])])
    return hdr, np.array(rows)


def records(runs):
    out = []
    for f in sorted(glob.glob(os.path.join(runs, "p_ibb_d128_*.csv"))):
        name = os.path.basename(f)[:-4]
        m = NAME.match(name)
        if not m:
            continue
        txt = open(f).read()
        if "# runtime_s=" not in txt:
            continue                                     # still running
        hdr, a = read_csv(f)
        if len(a) == 0 or abs(float(hdr.get("Re", 0)) - 33057) > 1:
            continue
        a = a[a[:, 0] >= T0]
        if len(a) < 100:
            continue
        edges = np.arange(a[0, 0], a[-1, 0] + 1e-9, DT)
        idx = np.digitize(a[:, 0], edges) - 1
        cy = np.array([a[idx == i, 1].mean() for i in range(len(edges) - 1) if np.any(idx == i)])
        cl = np.array([a[idx == i, 2].mean() for i in range(len(edges) - 1) if np.any(idx == i)])
        out.append({"name": name, "orient": m.group(1), "S": float(m.group(2)),
                    "mean": [round(float(cy.mean()), 4), round(float(cl.mean()), 4)],
                    "sd": [round(float(cy.std()), 4), round(float(cl.std()), 4)],
                    "cy": [round(float(x), 4) for x in cy - cy.mean()],
                    "cl": [round(float(x), 4) for x in cl - cl.mean()]})
    return out


def wake_profiles(runs):
    """time-mean ground-frame air velocity on the path line (y = z = 0 behind the ball) from the field dumps
    (pm012_lbm dump_field: blocks ux, uy, uz, float32, x fastest, ball frame, fraction of U)"""
    out = []
    for f in sorted(glob.glob(os.path.join(runs, "p_wake_*.csv"))):
        name = os.path.basename(f)[:-4]
        if "# runtime_s=" not in open(f).read():
            continue
        acc, n, meta = None, 0, None
        for j in sorted(glob.glob(os.path.join(runs, name + "_f*.json"))):
            meta = json.load(open(j))
            nx, ny, nz = meta["nx"], meta["ny"], meta["nz"]
            v = np.fromfile(j[:-5] + ".bin", dtype=np.float32, count=3 * nx * ny * nz).reshape(3, nz, ny, nx)
            acc = v.astype(np.float64) if acc is None else acc + v
            n += 1
        if not n:
            continue
        acc /= n
        dx, o = meta["dx_D"], meta["origin_D"]
        X = o[0] + dx * np.arange(nx); Y = o[1] + dx * np.arange(ny); Z = o[2] + dx * np.arange(nz)
        jy, kz = int(np.argmin(np.abs(Y))), int(np.argmin(np.abs(Z)))
        keep = X >= 0.75                                   # behind the ball surface and its holes
        ud = 1.0 - acc[0, kz, jy, :]; un = acc[2, kz, jy, :]
        # wake centre (largest deficit in the cross-section) and its depth, for the notes
        zc = [float(Z[np.unravel_index(np.argmax(1.0 - acc[0, :, :, i]), (nz, ny))[0]]) for i in range(nx)]
        xs, uds, uns = X[keep], ud[keep], un[keep]
        far = xs >= max(4.0, xs[-1] / 2)                   # power-law fit of the far part: ud = a x^-p
        pw = -np.polyfit(np.log(xs[far]), np.log(np.clip(uds[far], 1e-4, None)), 1)[0]
        step = max(1, int(round(0.5 / dx)))                # every 0.5 D
        out.append({"name": name, "S": float(re.search(r"_S([0-9.]+)$", name).group(1)), "dumps": n,
                    "x": [round(float(x), 3) for x in xs[::step]], "ud": [round(float(x), 4) for x in uds[::step]],
                    "un": [round(float(x), 4) for x in uns[::step]], "zc": [round(zc[i], 3) for i in np.where(keep)[0][::step]],
                    "pw": round(float(pw), 3)})
    return out


def main():
    runs = sys.argv[1]
    recs = records(runs)
    d = os.path.join(HERE, "data")
    doc = {"what": "PM-012 CFD side (Cy) and lift (Cl) force records about the run mean, PREDICTED; POLLEN D128, Re 33k",
           "dtau": DT, "t0": T0, "runs": recs}
    json.dump(doc, open(os.path.join(d, "unsteady.json"), "w"), separators=(",", ":"))
    print("unsteady.json: %d records (%s)" % (len(recs), ", ".join("%s" % r["name"][11:] for r in recs)))
    wk = wake_profiles(runs)
    if wk:
        best = {}                                          # one run per spin: the longest wake box
        for r in wk:
            if r["S"] not in best or r["x"][-1] > best[r["S"]]["x"][-1]:
                best[r["S"]] = r
        prof = [best[k] for k in sorted(best)]
        json.dump({"what": "PM-012 CFD wake of POLLEN on its own path, ground frame, fraction of ball speed; PREDICTED "
                           "inside the CFD box, power-law fit beyond (ASSUMED form)", "runs": prof},
                  open(os.path.join(d, "wake.json"), "w"), separators=(",", ":"))
        print("wake.json: %d runs" % len(prof))


if __name__ == "__main__":
    main()
