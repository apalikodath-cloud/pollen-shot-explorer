# Head A on the Ri3D turret: compare mount points along the head's centre line (a = (a_x, 0), back trimmed, t = 0).
# Run: python mounts.py
from margins import exp_margin, start_margin
from arm_only import arm_only_clear, usable_run


def main():
    for ax in (-100.0, -95.0, -92.5, -90.0, -85.0):
        a = (ax, 0.0)
        lo, hi = usable_run(a)
        dd = min((arm_only_clear(a, p % 360) + (p,) for p in range(lo, hi + 1)), key=lambda r: r[0])
        mm = min((exp_margin(a, p % 360)[0], p) for p in range(lo, hi + 1))
        parks = [start_margin(a, p)[0] for p in (90, 270, 180, 0)]
        print(f"a_x {ax}: run psi {lo}..{hi} ({hi - lo} deg); arm-only min {dd[0]:.1f} at psi {dd[2]} ({dd[1]}); "
              f"expanded min {mm[0]:.1f} at psi {mm[1]}; start park margins psi 90/270/180/0 {parks}")


if __name__ == "__main__":
    main()
