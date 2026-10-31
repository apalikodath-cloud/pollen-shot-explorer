"""Figures for the shooter design targets (reads data/spec_robust.csv, data/spec_nominal.csv).

    python -m src.spec_figs     # -> figures/spec_targets_h*.png, spec_tolerance.png, spec_hood_tol05.png
"""
from __future__ import annotations

import csv
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGS = os.path.join(ROOT, "figures")
SPIN_STYLE = {0.0: ("#777777", "no spin"), 0.5: ("#6aa3d8", "backspin S 0.5"),
              1.0: ("#1f5fa8", "backspin S 1.0"), 1.5: ("#0b2f66", "backspin S 1.5"),
              -1.0: ("#c46a1b", "topspin S 1.0 (exploratory)")}


def read(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(l for l in fh if not l.startswith("#"))]
    for r in rows:
        for k, v in r.items():
            try:
                r[k] = float(v)
            except (TypeError, ValueError):
                pass
    return rows


def fig_targets(rows, path, h=0.5, basis="robust: clean under all aero bounds and tilt 28.5-31.5 (old sweep bounds)"):
    fig, ax = plt.subplots(1, 3, figsize=(14, 4.2))
    for S, (col, lab) in SPIN_STYLE.items():
        rs = sorted((r for r in rows if r["S"] == S and abs(r["h_m"] - h) < 1e-6
                     and r["n_clean"] > 0 and r["target_v"] != ""), key=lambda r: r["d_m"])
        if not rs:
            continue
        d = [r["d_m"] for r in rs]
        ax[0].errorbar(d, [r["target_v"] for r in rs], yerr=[r["tol_v_pm"] for r in rs],
                       color=col, label=lab, marker="o", ms=3, capsize=2)
        ax[1].errorbar(d, [r["target_elev"] for r in rs], yerr=[r["tol_elev_pm"] for r in rs],
                       color=col, label=lab, marker="o", ms=3, capsize=2)
        ax[2].plot(d, [r["wheel_rpm_vu042"] for r in rs], color=col, label=lab, marker="o", ms=3)
    ax[0].set_ylabel("exit speed target (m/s), bar = tolerance")
    ax[1].set_ylabel("launch elevation target (deg), bar = tolerance")
    ax[2].set_ylabel("98 mm wheel rpm (v/u = 0.42)")
    for a in ax:
        a.set_xlabel("release distance to HIVE pivot plane d (m)")
        a.grid(alpha=0.3)
    ax[0].legend(fontsize=8)
    fig.suptitle(f"Shooter exit targets, unfavourable side, release height {h} m "
                 f"({basis}; PREDICTED)", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def fig_tolerance(rows, path, basis="robust"):
    hs = sorted({r["h_m"] for r in rows})
    fig, ax = plt.subplots(1, len(hs), figsize=(3.2 * len(hs), 3.6), sharey=True)
    for a, h in zip(ax, hs):
        for S, (col, lab) in SPIN_STYLE.items():
            rs = sorted((r for r in rows if r["S"] == S and abs(r["h_m"] - h) < 1e-6),
                        key=lambda r: r["d_m"])
            a.plot([r["d_m"] for r in rs],
                   [r["square_cells"] if r["n_clean"] > 0 and r["square_cells"] != "" else 0
                    for r in rs], color=col, label=lab, marker=".")
        a.set_title(f"h = {h} m", fontsize=9)
        a.set_xlabel("d (m)")
        a.grid(alpha=0.3)
    ax[0].set_ylabel(f"{basis} square side (cells of 0.05 m/s x 0.1 deg)")
    ax[0].legend(fontsize=7)
    fig.suptitle("How much exit error the shot tolerates (bigger = easier), unfavourable side, "
                 "PREDICTED", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def fig_hood(rows, path, tag="05", tol=0.5):
    """Fixed hood held to +/- tol deg: exit-speed window (bar) at the best elevation, per d."""
    hs = sorted({r["h_m"] for r in rows})
    fig, ax = plt.subplots(2, len(hs), figsize=(3.2 * len(hs), 6.4), sharex=True, sharey="row")
    for k, h in enumerate(hs):
        for S, (col, lab) in SPIN_STYLE.items():
            rs = sorted((r for r in rows if r["S"] == S and abs(r["h_m"] - h) < 1e-6
                         and r.get(f"hood{tag}_v", "") != ""), key=lambda r: r["d_m"])
            if not rs:
                continue
            d = [r["d_m"] for r in rs]
            ax[0, k].errorbar(d, [r[f"hood{tag}_v"] for r in rs],
                              yerr=[r[f"hood{tag}_tol_v_pm"] for r in rs],
                              color=col, label=lab, marker="o", ms=3, capsize=2)
            ax[1, k].plot(d, [r[f"hood{tag}_elev"] for r in rs], color=col, marker="o", ms=3)
        ax[0, k].set_title(f"h = {h} m", fontsize=9)
        ax[1, k].set_xlabel("d (m)")
        for a in ax[:, k]:
            a.grid(alpha=0.3)
    ax[0, 0].set_ylabel("exit speed (m/s), bar = +/- tolerance")
    ax[1, 0].set_ylabel("hood elevation (deg)")
    ax[0, 0].legend(fontsize=7)
    fig.suptitle(f"Fixed hood held to +/-{tol} deg: exit speed it must hold, unfavourable side, robust "
                 "(all aero bounds, tilt 28.5-31.5, old sweep bounds), PREDICTED", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def fig_windows(path, h=0.5, d=1.75, S=1.0):
    """Clean (v, elev) cells of each aero variant (tilt 30) and each tilt (nominal aero) at one
    release point: shows how far the unknown aero and tilt move the window."""
    import numpy as np
    from src import shooter_spec as ss
    g = ss.grid()
    ih = int(np.argmin(abs(g.h - h)))
    idd = int(np.argmin(abs(g.d - d)))
    conds = [(v, "unfav_t30") for v, *_ in ss.variants(S)] + [
        ("nominal", ss.UNFAV_KEYS[1]), ("nominal", ss.UNFAV_KEYS[2])]   # old sweep bounds (fz.SWEEP_TILT)
    cmap = plt.get_cmap("tab10")
    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    for k, (var, gk) in enumerate(conds):
        m = ss.load(S, var)[f"{gk}__clean"][ih, idd]
        vi, ti = np.nonzero(m)
        ax.scatter(g.theta[ti], g.v[vi], s=6, color=cmap(k), marker="s",
                   label=f"{var}, tilt {gk.split('_t')[1]}")
    ax.set_xlabel("launch elevation (deg)")
    ax.set_ylabel("exit speed (m/s)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7, markerscale=2)
    fig.suptitle(f"Clean-entry cells, unfavourable side, h {h} m, d {d} m, backspin S {S}\n"
                 "each colour is one aero/tilt case (PREDICTED)", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def main():
    rob = read("spec_robust.csv")
    if any(r["n_clean"] > 0 for r in rob):
        rows, basis = rob, "robust: clean under all aero bounds and tilt 28.5-31.5 (old sweep bounds)"
    else:   # no cell survives every aero bound and tilt; show nominal and say so
        rows = [r for r in read("spec_nominal.csv") if r["side"] == "unfavorable"]
        basis = "NOMINAL aero and tilt 30 only: no cell is clean under every aero bound"
    for h in (0.35, 0.5, 0.737):
        fig_targets(rows, os.path.join(FIGS, f"spec_targets_h{int(round(h * 1000))}.png"), h, basis)
    fig_tolerance(rows, os.path.join(FIGS, "spec_tolerance.png"), basis.split(":")[0])
    fig_hood(rob, os.path.join(FIGS, "spec_hood_tol05.png"))
    fig_windows(os.path.join(FIGS, "spec_windows_h500_d175.png"), 0.5, 1.75)
    fig_windows(os.path.join(FIGS, "spec_windows_h737_d075.png"), 0.737, 0.75)
    print("wrote figures/spec_targets_h*.png, spec_tolerance.png, spec_hood_tol05.png, "
          "spec_windows_*.png")


if __name__ == "__main__":
    main()
