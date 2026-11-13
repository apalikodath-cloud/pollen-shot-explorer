# Head A on the Ri3D turret: per-degree sweep of the chosen mount (a = (-95, 0), back trimmed, no adapter) as CSV.
# Run: python sweep_csv.py ../turret_fit_sweep_2026-11-08.csv
import csv
import sys
from margins import arm_clear, exp_margin, start_margin
from arm_only import arm_only_clear

A = (-95.0, 0.0)
TRAVEL = (79, 281)   # usable run found by margins.py / arm_only.py for this mount

HEADER = [
    "# Head A (Concept A) on the 19705 Ri3D robot turret: box-model sweep over the turret angle, run 2026-11-08",
    "# Tool: checks/turret_fit/sweep_csv.py (box model, see turret_fit.md section 9). Mount: turret axis at head point x -95, y 0 (95 mm behind the main axle F, on the centre line); frame plate bottoms (head z -142) on the turret plate (no adapter); back trimmed (frame x >= -190, feed floor x >= -175).",
    "# Units mm and degrees. psi = direction the head shoots in robot coordinates (0 = +X toward the rear arms, 90 = +Y, 180 = over the intake). turret_deg = psi - 180 = the Revolute 1 angle in the Onshape fit assembly.",
    "# in_travel = 1 inside the usable run psi 79..281 (turret -101..+101).",
    "# clearance_mm = smallest plan gap from any head part (alpha 5, 15 and 25) to the rear arms or the side-plate peaks at overlapping heights; 0 = overlap. arm_only_mm = the same for the arms alone. Robot arm and side-plate positions are measured from views, +-3 mm. Part names are cut to 30 characters.",
    "# expanded_margin_mm = smallest of (609.6 - X span, 457.2 - Y span) of robot (intake out, X -336.8..138.4, Y +-164) plus head, worst alpha. start_margin_mm = smallest of (457.2 - X span, 457.2 - Y span) with the intake folded (X -232..138.4) and the head at alpha 15; plan only (the head is too tall for the start, see turret_fit.md section 5).",
]
COLS = ["psi_deg", "turret_deg", "in_travel", "clearance_mm", "clearance_pair", "arm_only_mm", "arm_only_pair",
        "expanded_margin_mm", "expanded_worst_alpha", "expanded_X_mm", "expanded_Y_mm",
        "start_margin_mm", "start_X_mm", "start_Y_mm"]


def rows():
    for psi in range(360):
        d, who = arm_clear(A, psi)
        da, whoa = arm_only_clear(A, psi)
        m, (al, X, Y) = exp_margin(A, psi)
        sm, sX, sY, _ = start_margin(A, psi)
        turret = psi - 180
        yield [psi, turret, int(TRAVEL[0] <= psi <= TRAVEL[1]), round(d, 1), who, round(da, 1), whoa,
               round(m, 1), al, X, Y, sm, sX, sY]


def main(path=None):
    f = open(path, "w", newline="", encoding="utf-8") if path else sys.stdout
    try:
        for ln in HEADER:
            f.write(ln + "\n")
        w = csv.writer(f, lineterminator="\n")
        w.writerow(COLS)
        for r in rows():
            w.writerow(r)
    finally:
        if path:
            f.close()


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
