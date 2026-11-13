# Head A on the Ri3D turret: clearance to the two rear arms only (the side-plate peaks left out), and the usable
# turret run for a mount point, with or without an adapter plate of thickness t under the head.
# Run: python arm_only.py  (prints the run and clearances for a few mounts, t = 0 and t = 4 mm)
from fit import PLATE_TOP_Z
from arms import arm_rects
from margins import zmin_all, head_parts, corners, poly_dist, rect_poly, arm_clear, exp_margin, start_margin


def arm_only_clear(a, psi, t=0.0):
    """(distance, label) from the head (alpha 5, 15, 25) to the arms only, turret angle psi, axis at head point a."""
    zmin = zmin_all()
    best = (1e9, None)
    for al in (5, 15, 25):
        for (i, name, b) in head_parts(al):
            Z0 = PLATE_TOP_Z + t + (b[4] - zmin)
            Z1 = PLATE_TOP_Z + t + (b[5] - zmin)
            for (oname, r) in arm_rects(Z0, Z1):
                if not oname.startswith("arm"):
                    continue
                d = poly_dist(corners(b, a, psi), rect_poly(r))
                if d < best[0]:
                    best = (d, f"{name[:30]} (alpha {al}) vs {oname}")
    return best


def usable_run(a, t=0.0):
    """widest run of turret angles around psi 180 with no overlap with the arms or side-plate peaks and within the
    expanded size limit. Returns (lo, hi) in psi degrees; lo may be < 0 and hi > 359 when the run wraps."""
    ok = {psi for psi in range(360) if arm_clear(a, psi, t=t)[0] > 0 and exp_margin(a, psi)[0] >= 0}
    lo = 180
    while (lo - 1) % 360 in ok and lo - 1 > -180:
        lo -= 1
    hi = 180
    while (hi + 1) % 360 in ok and hi + 1 < 540:
        hi += 1
    return lo, hi


def main():
    for ax in (-95.0, -90.0, -85.0):
        a = (ax, 0.0)
        for t in (0.0, 4.0):
            lo, hi = usable_run(a, t)
            dd = min((arm_only_clear(a, p % 360, t) + (p,) for p in range(lo, hi + 1)), key=lambda r: r[0])
            mm = min(exp_margin(a, p % 360)[0] for p in range(lo, hi + 1))
            print(f"a_x {ax} t {t}: run psi {lo}..{hi} ({hi - lo} deg, turret {lo - 180:+d}..{hi - 180:+d}); "
                  f"min arm-only clearance {dd[0]:.1f} at psi {dd[2]} ({dd[1]}); min expanded margin {mm:.1f}; "
                  f"clearance incl. side-plate peaks at the ends {arm_clear(a, lo % 360, t=t)[0]:.1f} / {arm_clear(a, hi % 360, t=t)[0]:.1f}")
        print("   start park psi 90 / 270 / 180 / 0 (alpha 15, intake folded):",
              [start_margin(a, p)[0] for p in (90, 270, 180, 0)])


if __name__ == "__main__":
    main()
