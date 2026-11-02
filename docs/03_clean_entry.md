# 03 - Clean air-only entry: no spin, drag, backspin (HANDOFF §3 Q1-Q3, §4B)

Code: `src/hive.py` (section classifier), `src/cell3d.py` (3D cell), `src/feasibility.py` (sweep, analysis,
figures), `tests/test_hive.py`.
Data: `data/clean_feasibility_map.csv`, `clean_required_spin.csv`, `clean_spin_controlled.csv`,
`clean_apex_audit.csv`, `clean_hook_scan.csv`, `clean_fine_tolerance.csv`, `clean_crosscheck.csv`.
Figures: `figures/clean_feasibility_maps.png`, `clean_spin_windows.png`, `clean_window_vs_spin.png`,
`clean_apex_paths.png` (the figures were not re-drawn in PM-019; they still show the pre-PM-019 section-model
sweep).
Reproduce: `python -m src.feasibility --stage all --cache <dir>` (PM-019, 3D cell: about 85 min on 3-4 workers,
then about 8 min of analysis; `--stage analyse --no-figs` skips the figures).

Scope: this is channel (1) of HANDOFF §4E, **clean air-only entry** into the upward-facing CELL of the centre
HIVE. That is hypothesis (A) of HANDOFF §0. Hypothesis (B), entry assisted by a contact with the rim or the
interior, is **not** covered here. Every "hit" below is a first contact, and it may still bounce in.

Provenance labels: **confirmed** (official source), **derived** (computed, formula given), **assumed**,
**predicted** (output of this model), **user**. Every feasibility number in this file is **predicted**. The
model uses assumed aerodynamics (`data/aero_params.json`, docs/02_aero.md: no POLLEN measurements exist yet)
and the CAD-derived HIVE geometry (docs/01_hive_geometry.md, tilt 30 deg confirmed). Written 2026-10-30;
all tables re-swept 2026-10-31 (PM-019) with the 3D cell, air density 1.2041 kg/m^3 and the derived tilt
bounds 28.80 / 31.77 deg, the same setup as the live solver in `viz/explorer/`. Before PM-019 the tables came
from the 2D section model at rho 1.20 and tilts 28.5 / 31.5; most numbers moved by a few percent and no
conclusion changed.

## 1. Method

### 1.1 Geometry and the clean-entry test

- `hive.py` loads the 2D section from `data/hive_geometry.json`: 25 obstacle segments, plus 4 projected legs
  as an option.
- The ball is a point at its centre. The obstacles are inflated by R = 35.5 mm (configuration space).
- **Clean** means the ball centre crosses the gate, which is the inside-polygon edge on the mouth plane. It must
  cross moving inward, and it must not have touched any obstacle earlier.
- **hit:<name>** means the first obstacle touched. **miss** means the ball never reached the gate or an obstacle.
- The exact classifier checks each path segment against each obstacle segment. The sweep uses a 1 mm
  clearance raster of the same geometry.
- **3D cell (PM-019, used for every table below).** The section above is the 2D model. The sweep now judges
  clean entry against the 3D CELL of `src/cell3d.py`: side walls plus the pentagon roof, built from the
  confirmed tilt-30 section. A shot at bearing psi runs on the oblique ruled surface
  s = s0 + (aim_x - x)·tan(psi), with aim_x = +0.401 m on the unfavourable side and -0.401 m on the
  favourable side. The clearance raster is built on that surface (1 mm). The in-plane shots of this file have
  psi = 0, so the 3D cell matters through the side walls and roof shape at the aim line, and through s0 for
  the offset case (§2.3). Name changes: first-contact names are the 3D cell's face names where they differ.

### 1.2 Shot frame and the two sides

- The shooter fires in +x from x = -d at ball-centre height h. Here d is the horizontal distance to the HIVE
  pivot plane.
- **unfav**: the mouth faces away from the shooter. This is pose_pos seen from the neg side, or its mirror,
  pose_neg seen from the pos side.
- **fav**: the mirror case, where the mouth faces the shooter.
- A unit test checks that pose_neg is the exact mirror of pose_pos. The exact classifier gives mirror-symmetric
  results in all 120 of 120 checks: 40 random drag shots, each checked 3 ways (`check_mirror`, after removing the world-side names of the frame parts).

### 1.3 Sweep grid (assumed)

| Variable | Range | Step |
|---|---|---|
| v | 2.0 to 11.0 m/s | 0.1 |
| Elevation | 5 to 89.75 deg | 0.25 |
| h | 0.2, 0.35, 0.5, 0.65, 0.737 m | — |
| d | 0.55 to 1.75 m | 0.05 |

- The h = 0.737 m upper value is assumed from the R105 robot-height limit.
- Results are reported both unrestricted (v ≤ 11) and with the **predicted hood grip cap v ≤ 8.9 m/s**
  (docs/04_launcher.md).

### 1.4 Aerodynamic cases (assumed bounds, docs/02_aero.md)

- Vacuum.
- Drag only, with Cd 0.35 / 0.48 / 0.65.
- Backspin at S = 0.5, 1, 1.5, 2, crossed with three Cl sets: Cl = min(c1·S, Cl_max), with (c1, Cl_max) of
  low (0.15, 0.10), nominal (0.35, 0.25) and high (0.8, 0.4).
- Spin decay k of 0.05 /s, with 0.01 and 0.30 as bounds.
- Two corner cases: (S1, Cl high, Cd high, k high) and (S2, Cl high, k low).
- One **exploratory** topspin case (S = -1, Cl nominal). It is labelled as such and is outside the backspin
  baseline.

### 1.5 Geometry cases

- Tilt 30 deg (confirmed).
- Tilt 28.80 / 31.77 deg (derived bounds, the exact solve of docs/01 section 5). These are run for every
  aero case.
- Run for vacuum, drag and S1-nominal only:
  - tilt 25.90 / 34.83 deg (derived wide bounds);
  - the favourable side at 28.80 / 31.77 deg;
  - the projected legs (in the 3D cell they are added as faces of unlimited lateral extent, the same as
    the section's other non-cell parts; they sit below almost every path, so only a few cells change);
  - a shot path offset 0.10 m laterally (parallel) from the HIVE centre plane (s0 = 0.10 m in the 3D cell).

### 1.6 Integration and gate search

- Integration uses vectorised RK4 at dt = 2 ms. It matches `flight.simulate` within 1e-5 m (unit test).
- Drag and Magnus do not depend on position, so each (v, elevation, S) path is integrated once and then
  translated to every (h, d).
- For each gate sample, this gives the release distance d at which the path passes that point. The path before
  that point is checked against the raster. Clean samples form d-intervals, which are then sampled onto the d
  grid.

### 1.7 Accuracy (derived)

- Clearance error is at most about 2.5 mm: raster 0.71 mm, plus a chord sagitta of about 1.75 mm at 11 m/s with
  dt 2 ms.
- **Cross-check.** I re-ran 537 grid cells with the exact RK45 integrator (rtol 1e-9) and the exact 3D-cell
  classifier. These were every clean cell plus sampled non-clean neighbours, at 3 (h, d) points, for drag and
  S1-nominal (`clean_crosscheck.csv`).
- 533 of 537 agree (derived). All 4 disagreements are conservative: the grid says not clean and the exact
  check says clean. Three have exact clearance of 0.8 to 3.9 mm, which is inside the resolution. One has
  9.5 mm (drag, h 0.737, d 1.15, 9.9 m/s, 83.5 deg), most likely a d-sampling edge (not checked further).
  Before PM-019 it was 547 of 552.
- So the windows below are slightly **under**-estimated, never over-estimated.

### 1.8 Window metrics

For each (h, d), I report:
- n_clean, the number of clean (v, elevation) cells;
- the v and elevation ranges;
- the descent angle at the gate;
- best_margin, the largest clearance of any clean path;
- **max_square**, the largest all-clean k × k block of cells (0.1 m/s × 0.25 deg each).

max_square is the tolerance that matters, because a real launcher must hit v and elevation at the same time.

## 2. Q1: no spin. Where is clean entry possible?

### 2.1 Unfavourable side, drag only, v ≤ 8.9 m/s, tilt 30 (predicted)

Values are n_clean cells per (h, d), from `clean_feasibility_map.csv`.

| h \ d (m) | 0.65 | 0.70 | 0.75 | 0.80 | 0.90 | 1.00 | 1.15 | 1.30 | 1.55 | 1.75 |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.20  | 0 | 0 | 0  | 11 | 38 | 37 | 33 | 27 | 22 | 13 |
| 0.35  | 0 | 0 | 0  | 26 | 46 | 41 | 35 | 31 | 24 | 20 |
| 0.50  | 0 | 0 | 9  | 43 | 49 | 45 | 36 | 35 | 25 | 24 |
| 0.65  | 0 | 0 | 33 | 57 | 55 | 50 | 44 | 38 | 30 | 22 |
| 0.737 | 0 | 0 | 51 | 64 | 59 | 56 | 49 | 45 | 30 | 31 |

- **max_square is 1 or 2 everywhere on the unfavourable side.** No clean block is larger than 0.2 m/s ×
  0.5 deg.
- The best clearance margin is 7 to 59 mm.
- Without the speed cap (v ≤ 11), d = 0.75 m opens at every h. At h = 0.2 this needs v ≥ 10.5 m/s.

**The clean windows are thin diagonal bands:**

| Quantity | Range |
|---|---|
| Elevation | 71.25 to 84.5 deg |
| Descent at the gate | 68.4 to 84.6 deg |
| v | slowest clean v 5.6 to 8.4 m/s (depends on h, d), up to the cap |

This is consistent with docs/01_hive_geometry.md, which says the ball must clear about 1.713 m over the up-cell
roof and then drop steeply. The straight-line estimate there is > 71.5 deg. The curved path at the gate allows
slightly less.

**Geometry-blocked region (Q1).**
- For **d ≤ 0.70 m**, no launch is clean at any h, any v ≤ 11 or any elevation. This holds in drag and with
  every backspin case.
- In vacuum, only 7 cells open, at h = 0.737 and d = 0.70.
- First contacts in that region (drag, v ≤ 11):
  - `down_roof_inner`: 45 to 100 % of gate-reaching launches;
  - `down_lower_lip`, `down_upper_lip`, `down_back_wall` and `down_roof_outer`: the rest.
- In words: close in, the down-cell structure on the shooter side shadows the mouth.
- For **d ≥ 0.75 to 0.80 m**, a clean window exists, but it is narrow.
- So reverse-side shots are **not** all impossible. The blocked region is a band about 0.7 m deep in front of
  the pivot plane.

### 2.2 Favourable side, for comparison (drag, v ≤ 8.9)

- Clean entry is possible from d ≥ 0.60 m.
- There are 110 to 1693 clean cells per (h, d), and max_square is 4 to 14. That is blocks up to 1.4 m/s ×
  3.5 deg.
- Elevations run from 32.75 to 89.25 deg.

Per (h, d) cell, **the favourable side has about 4 to 7 times more tolerance in each of v and elevation**, and
about 10 to 50 times more clean area.

### 2.3 Sensitivity: unfavourable, drag, v ≤ 8.9, sum of n_clean over all 125 (h, d) cells

| Case | Total cells | Change vs nominal | Note |
|---|---|---|---|
| tilt 30, Cd nominal | 3640 | — | baseline |
| tilt 28.80 | 3130 | -14 % | |
| tilt 31.77 | 4351 | +20 % | |
| tilt 25.90 (wide) | 2055 | -44 % | |
| tilt 34.83 (wide) | 5757 | +58 % | |
| Cd low / high | 3591 / 3534 | — | |
| Vacuum | 3635 | — | |
| With legs | 3633 | -0.2 % | essentially identical; the legs are below almost every path (§1.5) |
| Path offset s0 = 0.10 m | 2488 | -32 % | **d = 0.70 opens** (13 to 27 cells at h ≥ 0.65), and h 0.2 to 0.35 open at d = 0.75; windows further out shrink |

- With tilt 25.90 and 34.83, the minimum d stays at 0.75 to 0.80.
- The 0.10 m offset is now a real 3D case: a path parallel to the centre plane, 0.10 m to the side, judged
  against the 3D cell. Before PM-019 it was a 2D section cut 0.10 m off-centre (2546 cells, d 0.70 opened with
  17 to 29 cells). Aim error as a random 3D scatter is still not swept here (docs/06 section 2 does it with the
  older section model).

## 3. Q2/Q3: backspin. Does it make an infeasible shot feasible?

### 3.1 Q3 answer: minimum spin per (d, h) (`clean_required_spin.csv`)

For every (h, d) where drag-only gives **no** clean launch, the answer is **"none within S ≤ 2"**. This holds:
- for all three Cl sets;
- for tilt 28.80, 30 and 31.77;
- with and without the 8.9 m/s cap.

That is 20 (h, d) cells uncapped and 22 capped, per geometry and Cl set. In those cells v and elevation were
re-optimised freely over the grid.

The robustness test asks for a clean 3 × 3 block (0.3 m/s × 0.75 deg, assumed). **No S** reaches it anywhere
on the unfavourable side. Drag-only does not reach it either.

### 3.2 Required spin vs speed vs range (re-optimised windows, unfavourable, tilt 30, v ≤ 8.9, predicted)

| h (m) | d (m) | vacuum n | drag n | drag v (m/s) | drag elev (deg) | drag descent (deg) | S=1 nom n | S=1 v | S=1 elev | S=1 rpm | S=1 descent | S=1 Cl-high n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.35 | 0.75 | 7 | 0 | – | – | – | 0 | – | – | – | – | 0 |
| 0.35 | 0.80 | 34 | 26 | 7.6-8.9 | 81.75-84.0 | 80.0-83.6 | 9 | 8.4-8.9 | 81.0-81.5 | 2260-2394 | 81.5-82.3 | 0 |
| 0.35 | 0.90 | 39 | 46 | 6.3-8.9 | 76.0-83.5 | 69.8-83.0 | 41 | 6.5-8.9 | 75.75-81.0 | 1748-2394 | 71.7-81.8 | 41 |
| 0.35 | 1.15 | 30 | 35 | 6.7-8.9 | 75.5-82.25 | 70.6-81.6 | 32 | 6.6-8.9 | 73.5-79.75 | 1775-2394 | 69.4-80.4 | 31 |
| 0.35 | 1.55 | 24 | 24 | 7.1-8.9 | 73.75-80.0 | 69.5-79.4 | 21 | 7.4-8.9 | 73.5-77.5 | 1991-2394 | 71.7-78.1 | 18 |
| 0.35 | 1.75 | 18 | 20 | 7.3-8.9 | 73.0-79.0 | 69.1-78.3 | 15 | 7.5-8.9 | 72.25-76.5 | 2017-2394 | 70.5-77.0 | 13 |
| 0.737 | 0.75 | 51 | 51 | 6.5-8.9 | 80.0-84.5 | 77.9-84.6 | 36 | 7.1-8.9 | 79.75-82.0 | 1910-2394 | 79.8-82.9 | 25 |
| 0.737 | 0.80 | 59 | 64 | 5.6-8.9 | 74.75-84.25 | 70.2-84.3 | 61 | 5.6-8.9 | 73.75-81.75 | 1506-2394 | 69.9-82.7 | 56 |
| 0.737 | 0.90 | 57 | 59 | 5.7-8.9 | 74.0-83.75 | 69.8-83.8 | 54 | 5.7-8.9 | 73.0-81.25 | 1533-2394 | 69.4-82.2 | 52 |
| 0.737 | 1.15 | 46 | 49 | 6.1-8.9 | 73.5-82.5 | 70.3-82.6 | 40 | 6.2-8.9 | 73.0-80.0 | 1668-2394 | 70.6-81.0 | 42 |
| 0.737 | 1.55 | 37 | 30 | 6.6-8.9 | 72.25-80.5 | 69.7-80.6 | 28 | 6.5-8.9 | 70.25-78.0 | 1748-2394 | 68.5-79.1 | 21 |
| 0.737 | 1.75 | 29 | 31 | 6.9-8.9 | 72.0-79.5 | 70.3-79.7 | 24 | 6.8-8.9 | 70.0-77.0 | 1829-2394 | 68.8-78.1 | 22 |

Notes on the table:
- rpm is the ball spin at launch: rpm = S·v/R·60/2π (derived).
- The ranges are envelopes of a thin diagonal band, not rectangles. See §5 for the real tolerances.
- The full grid for every h, d, case and geometry is in `clean_feasibility_map.csv`.

### 3.3 Totals over all 125 (h, d) cells (unfavourable, tilt 30, v ≤ 8.9)

| Case | (h, d) cells feasible | Total clean cells | Mean max_square |
|---|---|---|---|
| vacuum | 104 | 3635 | 1.05 |
| drag (no-spin twin) | 103 | 3640 | 1.25 |
| S0.5 Cl low / nom / high | 102 / 101 / 99 | 3417 / 3206 / 2976 | 1.23-1.31 |
| S1 Cl low / nom / high | 102 / 101 / 99 | 3451 / 3197 / 2976 | 1.25-1.31 |
| S1.5 and S2 (any Cl) | same as S1 | same as S1 | same as S1 |
| S1 Cl high, Cd high, k high | 99 | 2920 | 1.32 |
| S2 Cl high, k low | 99 | 2976 | 1.31 |
| *topspin S1 Cl nom (exploratory)* | *106* | *4003* | *1.24* |

**Every backspin case shrinks the unfavourable window** compared with its no-spin twin (drag-only), by 5 to
20 % of the clean cells. The shrinkage grows with Cl. The minimum distance either stays at d = 0.75 or moves
out to 0.80 to 0.85 at low h (v ≤ 8.9). **More backspin does not help.**

Why S ≥ 1 cases are identical:
- The assumed Cl law saturates at S = Cl_max/c1, which is 0.67, 0.71 and 0.50 for the low, nominal and high
  sets.
- Above that, the Magnus force is ½ρ·Cl_max·A·v². That is independent of spin rate. The ball's S also rises as
  it slows: S at the apex is 6 to 117.
- So in this model, extra spin above S ≈ 0.7 changes nothing.
- The spread between the Cl sets (Cl_max 0.10 to 0.40) is the real uncertainty band.
- If POLLEN's Cl keeps rising with S (docs/02_aero.md cites subcritical saturation at 0.30 to 0.37), the "high"
  set is the bound. It is still the worst case for the unfavourable side.

On the favourable side, backspin also shrinks the window, but less: 1 % for Cl low and 4 % for Cl high in total
cells (96069 no-spin twin vs 95102 / 91940). Mean max_square falls from 7.47 to 7.12 to 7.36.

### 3.4 Controlled comparison: same (v, elevation, h, d), with and without spin (`clean_spin_controlled.csv`)

- **Unfavourable side: kept = 0 for every backspin case except Cl low,** which keeps 10 to 21 of the 20543
  clean no-spin-twin cells (0.1 % or less). So almost no clean drag-only launch stays clean when spin is added
  at the same v and elevation. (The pre-PM-019 text said 0 for every case; its own data had 7 to 20 for Cl
  low.)
- Every gained cell sits at a different (v, elevation). Spin moves the narrow band rather than widening it.
- A crew that tunes a shot without spin and then adds spin (or the reverse) will miss.
- Favourable side: 51 to 81 % of the cells are kept.

Mechanism (predicted, `clean_apex_audit.csv`, exact RK45, same v and elevation):
- The spin path reaches its apex 0.19 to 0.40 m **short** of the no-spin twin's apex, and 25 to 91 mm higher.
- By the end of the flight it is 0.41 to 0.79 m short in x at equal time.
- The drag-optimal shots then hit `pivot_plate_top`, `down_back_wall` or `up_back_wall`. The
  S1-nominal-optimal shots go clean, but they sit at an elevation 1.75 to 2.75 deg lower than the drag-optimal
  shots (with Cl high and S2 / k low they hit `up_roof_outer`).
- In the re-optimised windows, the steepest achievable descent at the gate falls by 1.2 to 1.7 deg with backspin.
  For example, at h 0.737 and d 0.75 it goes from 84.6 to 82.9 deg.
- The unfavourable side needs a steep descent, so this flattening is what costs window.

## 4. §4B apex and "spin hook" audit (predicted, `clean_apex_audit.csv`, `clean_hook_scan.csv`)

### 4.1 Representative shots

Three representative shots: (h 0.737, d 0.75), (0.737, 1.15) and (0.35, 1.55). Each was run with its
drag-optimal cell and its S1-nominal-optimal cell, and re-run with S1 nominal, S1 high, S2 high + k low, and
topspin.

| Quantity | No spin | Backspin (S1-S2) |
|---|---|---|
| Apex time | 0.76-0.79 s | 0.77-0.81 s |
| Apex height above floor | 3.29-4.00 m | 3.35-4.08 m |
| **Horizontal speed at apex** | **0.77-1.68 m/s** | **0.15-1.32 m/s** |
| Spin at apex | — | 2170-4700 rpm; S 6-117 |
| Magnus acceleration at apex | — | **0.001-0.047 m/s² up, about 0 horizontal** (vs g = 9.81) |

- The ball is **never stationary at the apex**. It keeps 0.15 to 1.7 m/s of horizontal speed.
- **The Magnus force is about zero at the apex**, because it scales with v². A spin rate that is large relative
  to the airspeed (large S) gives no force there, since Cl is capped.
- The Magnus acceleration is largest at launch. At v = 8.6 m/s it is 1.76 m/s² for Cl 0.25 and 2.8 m/s² for
  Cl 0.40. The formula is a = ½ρ·Cl·A·v²/m, derived.
- During the ascent it points rearward and up. During the descent it points forward and up, which flattens the
  path.

Where the difference with and without spin is largest:
- It is **not at the apex**. The x-difference at equal time grows monotonically through the flight. It is
  largest at the end of the evaluated window, near the gate (t ≈ 1.5 to 1.6 s, 0.4 to 0.8 m).
- At equal downrange x, the height difference on the near-vertical descent is metres. That is an artefact of
  comparing two near-vertical curves. Equal-time dx is the meaningful number.

### 4.2 Horizontal reversal, tested explicitly

Test: vx < 0 at any time above the release height, over the whole (v, elevation) grid.

- Reversal **does occur**, but only at near-vertical elevations. For v = 8.9 m/s:

| Case | Reversal from |
|---|---|
| S1 Cl nominal | elevation ≥ 87.0 deg |
| S1-2 Cl high | ≥ 85.0 deg |
| S2 Cl high k low | ≥ 85.0 deg |
| Cl low | ≥ 88.75 deg |

- At 5 m/s the thresholds are 88.25 to 89.75 deg.
- **None of the 1218 to 1276 unique clean unfavourable launches reverses**, for any backspin case. The clean
  windows sit at elevation ≤ 84.5 deg, below every reversal threshold.
- A backspinning ball that does reverse goes almost straight up and drifts back toward the shooter. It does not
  enter the unfavourable mouth.
- The "hook" the user observed (HANDOFF §0) is better explained by reduced horizontal progress, a higher and
  shorter apex, and rim contact (hypothesis B) than by an air-only reversal into the cell.

## 5. Tolerance: is any unfavourable shot repeatable? (predicted, `clean_fine_tolerance.csv`)

The fine grid uses v steps of 0.02 m/s and elevation steps of 0.05 deg, at tilt 30 with Cd nominal.

Values are the clean area in (v, elevation), the largest all-clean block, and the longest clean run along each
axis. The fine grid is not speed-capped (v ≤ 10). Favourable values are lower bounds, because the windows are
cut by the grid edges at elevation 66 deg and v 10.

| Case | Side | h (m) | d (m) | Area (m/s·deg) | Block v × elev | Longest elev run (deg) | Longest v run (m/s) |
|---|---|---|---|---|---|---|---|
| drag (no-spin twin) | unfav | 0.737 | 0.80 | 2.07 | 0.14 m/s × 0.35 deg | 0.55 | 0.46 |
| drag (no-spin twin) | unfav | 0.737 | 1.15 | 1.60 | 0.12 × 0.30 | 0.50 | 0.34 |
| drag (no-spin twin) | unfav | 0.737 | 1.55 | 1.20 | 0.10 × 0.25 | 0.40 | 0.28 |
| drag (no-spin twin) | unfav | 0.35 | 0.80 | 1.09 | 0.14 × 0.35 | 0.50 | 0.44 |
| drag (no-spin twin) | unfav | 0.35 | 1.55 | 0.94 | 0.10 × 0.25 | 0.40 | 0.24 |
| S1 Cl nom | unfav | 0.737 | 0.80 | 1.92 | 0.14 × 0.35 | 0.55 | 0.86 |
| S1 Cl nom | unfav | 0.737 | 1.55 | 1.07 | 0.10 × 0.25 | 0.40 | 0.34 |
| S1-2 Cl high | unfav | 0.737 | 0.80 | 1.80 | 0.14 × 0.35 | 0.50 | 1.48 |
| S1-2 Cl high | unfav | 0.35 | 0.80 | **0** | – | – | – |
| S1-2 Cl high | unfav | 0.737 | 1.55 | 0.95 | 0.10 × 0.25 | 0.35 | 0.42 |
| drag | fav | 0.737 | 0.80 | ≥ 12.1 | ≥ 0.58 × 1.45 | ≥ 11.7 | ≥ 1.68 |
| drag | fav | 0.737 | 1.15 | ≥ 13.3 | ≥ 0.64 × 1.60 | ≥ 11.7 | ≥ 1.00 |
| drag | fav | 0.737 | 1.55 | ≥ 9.8 | ≥ 0.46 × 1.15 | ≥ 7.3 | ≥ 0.72 |

The full list is in `clean_fine_tolerance.csv`.

What spin does to the window here:
- Against the no-spin twin it reduces the clean area by 7 to 21 % at h 0.737 (Cl nominal to high), by 46 %
  at h 0.35, d 0.80 with Cl nominal and by 100 % there with Cl high.
- It **does not change the simultaneous block**: 0.10 to 0.14 m/s × 0.25 to 0.35 deg.
- It tilts the band, so the longest run at a fixed elevation grows from 0.46 to as much as 1.48 m/s. That
  makes the unfavourable shot slightly less sensitive to speed alone when the elevation is held exactly. It
  does not loosen the joint tolerance.
- The unfavourable block is about 4 times smaller than the favourable one on each axis. In area, the
  unfavourable side has 6 to 8 times less.

**Distance tolerance at a fixed launch (v, elevation), d step 0.005 m.** This sub-study was not re-run in
PM-019; its numbers are from the pre-PM-019 section model.

| Side | h (m) | Longest clean d-span | Median d-span |
|---|---|---|---|
| Unfavourable | 0.737 | 0.095 m | 0.055 m |
| Unfavourable | 0.35 | 0.090 m | 0.045 m |
| Favourable | both | ≥ 0.21-0.26 m | 0.15 m |

- Unfavourable, h 0.737: the longest span is at v 8.6 m/s, elevation 83.25 deg, d 0.86 to 0.955. Spans are
  measured over 926 launches.
- The favourable figures are limited by the grid.
- S1 nominal gives 0.085 m and 0.045 to 0.050 m on the unfavourable side.

**Required repeatability (derived).** Suppose a ±2σ scatter must fit inside the best unfavourable clean block
of about 0.14 m/s × 0.35 deg. Then the launcher needs all of these at once:
- σ_v ≲ 0.035 m/s;
- σ_elevation ≲ 0.09 deg;
- σ_d ≲ 0.02 m.

That is about 0.4 % speed repeatability at 8.6 m/s. Scatter from ball-to-ball variation (mass ±6 %, assumed),
battery sag and wheel-speed recovery has not been measured. **Measured shot scatter is the deciding unknown.**

## 6. Conclusion

1. **Clean air-only entry from the unfavourable side is geometrically possible without any spin** (predicted),
   for release distance d ≥ 0.75 to 0.80 m from the pivot plane (3D cell, PM-019). Requirements:
   - elevation about 71 to 84.5 deg;
   - v about 5.6 to 8.9 m/s;
   - descent at the gate 68 to 85 deg.

   It is **blocked for d ≤ 0.70 m** at every height, speed and spin tested, by the down-cell roof and lips.
2. **The window is very narrow**, about 0.1 to 0.14 m/s × 0.25 to 0.35 deg, with ±0.03 to 0.05 m in distance.
   That is 4 to 7 times tighter per axis than the favourable side. It also gets narrower as d grows.
3. **Backspin does not open the blocked region, and it slightly shrinks the open window** (5 to 20 % fewer
   clean launches than the no-spin twin). This holds for every S from 0.5 to 2 and every Cl set and tilt bound tested. It also moves
   the window, so a no-spin tune never transfers. Q3 answer: **"none within S ≤ 2"** for every infeasible
   (d, h).
4. Apex audit:
   - the ball keeps horizontal speed at the apex;
   - the Magnus force there is about zero;
   - the largest spin effect is near the gate, not at the apex;
   - horizontal reversal happens only for elevations ≥ 85 to 89.75 deg, never on a clean unfavourable path.

**Confidence**
- **Medium-high** on the qualitative result: backspin does not help clean entry on the unfavourable side. The
  sign of the Magnus effect on the descent angle is robust to the Cl, Cd and decay bounds and to tilt.
- **Medium** on the blocked-region boundary (d ≈ 0.70 to 0.80 m, ±0.05 m). It is sensitive to tilt and to the
  3D section.
- **Low** on whether the unfavourable window is usable in practice. That depends on shot scatter, which has not
  been measured.

**Dominant uncertainties, in order**
1. Real launcher repeatability in v, elevation and spin (unmeasured).
2. POLLEN Cl(S) and Cd for a perforated ball (assumed, no measurements). A Cl that rises with S, or a
   reverse-Magnus sign at low S, would change the spin results, though not the no-spin ones.
3. Lateral aim. The sweep now uses the 3D cell, and a 0.10 m parallel aim offset already moves the boundary
   to d = 0.70 (at h ≥ 0.65). Random 3D aim scatter with the 3D cell has not been swept (docs/06 section 2 is
   still the section model).
4. HIVE tilt and position tolerances (the derived bounds 28.80 / 31.77 deg change the window by -14 / +20 %,
   the wide bounds 25.90 / 34.83 deg by -44 / +58 %).
5. Rim contact and bounce-in (hypothesis B) are not modelled here and may add real entries.

**Exploratory, outside the backspin baseline:** topspin S = 1 nominal enlarges the unfavourable window by 10 %
against the no-spin twin and opens d = 0.70 (7 to 36 cells per h, v ≤ 11). That is because it steepens the descent. A single powered wheel above
the ball would produce topspin. This is labelled exploratory and not evaluated further.
