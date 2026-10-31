# Whole-field shot data (PM-005)

Producer: `viz/explorer/export_field.py` (`compute` is resumable, `finalize` writes the files).
Output: `viz/explorer/data/field/` (gitignored, regenerate). Tests: `tests/test_field.py`.
All numbers are **PREDICTED** clean-air-entry windows (model output, not a hit probability, no
repeatability claim). Aero is **ASSUMED** (literature, `research/params_lit.json`); HIVE section at tilt 30
is **CONFIRMED** (official CAD); the 3D cell built from it is PREDICTED geometry; the other-HIVE box as a blocker, the release offset, heights and
psi > 60 are **ASSUMED**. Field geometry (walls, A-frame base, robot footprint, other-HIVE box, grid) comes from
one place, `src/field_geom.py` (PM-015; JS twin in `solver.js`, see "Field geometry" below).
Every backspin case has its no-spin twin (S = 0) in the same files; more spin is not always better (Cl saturates).

## Model (since PM-019: 3D cell masks)

* Release at distance d = |x| from the HIVE pivot plane, aim at the gate centre; `psi = atan(|y| / Lh)`,
  `Lh = d + 0.401` (far side) or `max(d - 0.401, 1e-3)` (near side).
* The ball flies in the vertical plane of that bearing (spin axis = v x z, perpendicular to that plane).
  Its in-plane path is the 2D path with `X` and `VX` scaled by `cos(psi)` (exact with no wind and no
  sideways force). So the effective shot-axis distance is d, the flown ground range is `Lh/cos(psi)`.
* The masks are classified on the **3D cell** of `src/cell3d.py` (`CELL_MODEL = "cell3d"` in
  `export_field.py`, `index.cell_model`): side walls, pentagon roof and lips along the real oblique path, the
  same model as the live solver's default (`q.sideWalls` true; see "3D cell model" below). rho 1.2041 kg/m^3
  (derived, still air). Before PM-019 the masks used the 2D section at an ASSUMED lateral offset
  `s_eff = min(0.3 tan(psi), 0.2) m`; those sections are still exported (`index.sections`) for the page's
  `sideWalls:false` option only.
* robustness.py caps psi at 60 deg (`PSI_MAX`, ASSUMED infeasible beyond). This export goes to 75 deg in 5 deg
  bins; bins above 60 are an **extrapolation** (`grid.psi_max_model`).
* NOT modelled in this export: sideways Magnus or gyroscopic spin, wind or drafts, a moving robot, other
  robots, release-position and angle errors (no probabilities here; the live page's hit-chance option
  covers scatter at one setting), the other HIVE as an obstacle (only flagged, straight sight line), and
  rim-assisted entry. Tilt 30 only.

## index.json

`label`, `provenance` (name -> PREDICTED/ASSUMED/CONFIRMED text), `frame`, `grid`, `field_grid`, `integrator`,
`sections`, `cases`, `summary`.

* `frame`: x = shot axis, distance from the pivot plane (HIVEs at x = 0, centre-to-centre 0.6472 m, CAD); y along
  the pivot axis, up cell aimed at y = 0 (centre line y = 0.3236); far side = `unfav` = back side (x < 0 for
  pose_pos, gate is d + 0.401 away), near side = `fav` = mouth side (x > 0, mouth faces the shooter). Mirror x for
  pose_neg; for the blue HIVE also mirror y (point reflection about the field centre: x -> -x,
  y -> 0.6472 - y). The mouth and back sides swap on every tip of the HIVE.
* `grid`: `h` (5 release heights), `d` (0.55..1.75 step 0.05), `psi` (0..75 step 5), `v[side]`, `theta[side]`
  (far v 5..11 step 0.05, theta 60..89.8 step 0.2; near v 2..10 step 0.1, theta 20..89.5 step 0.5).
  Coarser than the 2D page grid (far theta 0.1, near 0.05/0.1 within 62..88); psi = 0 shots are a subset of the
  2D grid, so they compare point by point.
* `cases[]`: `{tag, S, var, files:{unfav|fav:{file, n, n_offsets, pos_file}}, params}`; `var` is `nominal`, or
  `Cl_low` / `Cl_high` (S > 0 only). `params` is the JS aero block (same as `data/index.json`).
  S in 0, 0.5, 1.0, 1.5. Tag example `Sp1.0_nominal`.
* `sections[key]`: key `"<side>_s<offset>"` with offset = `s_eff(psi)` formatted `%g` (e.g. `unfav_s0.2`):
  `names, P0, P1, inside, gate, normal` (same layout as `data/index.json` geoms) for
  `PollenPhysics.classifyOblique`.
* `summary[tag][side]`: flat lists, index `(ip*nH + ih)*nD + id`: `count` (clean cells), `k` (side of the largest
  all-clean k x k square in (v, theta) cells, 0 = none; tolerance = +-(k-1)/2 cells), `v`, `th` (centre of that
  square), `ang` (descent angle at the gate, 0.01 deg), `margin` (clearance, 0.1 mm) at that centre.
* `field_grid`: `step` 0.05, `xs`, `ys`, `nx`, `ny`, `status_codes`. Grid (PM-015): x = k 0.05 for |x| <= 1.70
  (symmetric about x = 0), y = k 0.05 inside the walls minus 0.10 (a row on the aim line y = 0): 69 x 68.
* `field_geom`: the constants the page uses (walls, base half-extents and centre, other-HIVE box, aim point,
  robot sizes), from `src/field_geom.py`.

## Mask files `mask_<side>_<tag>.b64.txt` (base64 of little-endian)

`u32 n | u32 off[nPsi*nH+1] | u32 idx[n] | u16 margin[n] | u16 ang[n]`.
Slice `s = ip*nH + ih` holds entries `off[s] .. off[s+1]` (sorted `idx`); `idx = id*nV*nTh + iv*nTh + ith`
(nV, nTh of that side; theta fastest). margin: 0.1 mm (clearance before entry); ang: 0.01 deg (descent at
the gate). Only clean cells are stored. Same layout idea as `data/*.b64.txt` of the 2D export.
Window for (side, h, S, psi, d) = decode slice, take `idx // (nV*nTh) == id`.

## Position files

* `pos_status.b64.txt`, arrays of shape (ny, nx), row = y, column = x, concatenated:
  `u8 status` (0 ok, 1 illegal: the 18 x 18 in chassis, release at its centre, fits at no heading of a 5 deg scan
  inside the walls and off the CONFIRMED A-frame base 38.95 x 49.46 in; 2 d outside table, 3 psi beyond 75+2.5;
  1 beats 2 beats 3),
  `u8 other` (exact segment test: the straight line from the release point to the aim point (0.401, 0) crosses
  the open other-HIVE box |x| < 0.6745, 0.3455 < y < 0.9495; derived box = CAD plan envelope + R, ASSUMED as a
  blocker; a high far-side ball can pass above it),
  `u8 fav` (x > 0), `i16 di` (nearest d index), `i16 pi` (nearest psi index), `u16 psi` (0.01 deg).
* `pos_<side>_<tag>.b64.txt`: per case, only positions of that side with status 0, shape (nH, ny, nx) each,
  concatenated in order: `u16 count`, `u8 k`, `u16 v` (0.01 m/s), `u16 th` (0.01 deg), `u16 ang` (0.01 deg),
  `u16 margin` (0.1 mm). 0 = none. Lookup is nearest d and psi bin (no interpolation; between bins the page may
  show the neighbouring bins). A position with `other = 1` still has a window (the model ignores the obstacle).

## JS (`viz/explorer/physics.js`)

`integrateOblique(v, thDeg, psiDeg, S0, p, dt, tMax, zStop)` returns `{X, Y, Z, VX, VY, VZ, n, dt}` (X = ground
range * cos(psi), Y = ground range * sin(psi); sign of psi = side of the aim line), `classifyOblique(path,
section, d, h, R)` (exact classifier on the section for `sEff(|psi|)`), `sEff(psi)`. Existing `integrate` and
`classify` are untouched. `tests/test_field.py` checks the trajectory against `robustness.integrate3d`
(< 1e-6 m) and 99 % classification agreement with the raster windows.

## Page notes

* `status` 0 also covers psi 60-75: the page must compare psi with `grid.psi_max_model` (60) and label those
  positions "extrapolated (ASSUMED)".
* In `summary` and `pos_*` files 0 means "none" for `v`, `th`, `ang`, `margin`; decide whether a window exists
  from `count` (or `k`), never from `margin`.

* `grid.psi_side_wall` (35.57 deg, PREDICTED straight-line estimate `atan((0.254 - 0.0355) / 0.30556)`, ball on the
  centre line) and `grid.side_wall_risk` (0/1 per psi bin; 1 if the bin's upper edge psi+2.5 exceeds it, so bins
  from 35 deg up). It is a near-side estimate; the far side is not checked. The page map tests each position's
  exact psi against 35.57 (not the bin edge). It is an informational flag only: since PM-019 the masks come
  from the 3D cell, which checks the side walls per shot (as the live solver's `shot().sideWall`).

* Size budget: near-side (`fav`) masks exist for `nominal` cases only. For `Cl_low`/`Cl_high` on the near side
  `files.fav.file` is `null`; use `summary` and the `pos_fav_*` file (counts and most forgiving shot) instead.
  Total generated size about 55 MB base64 (over the 40 MB target; the near side is large because its windows are wide).

## Live solver (`viz/explorer/solver.js`, PM-009)

Same model as above, computed in the browser for any continuous release point (x, y) and height h (not snapped
to the grids). Load after `physics.js` (worker: `importScripts("physics.js", "solver.js")`); `self.PollenSolver`.

* `pose(x, y, meta, {robot})`: side, d, Lh, signed psi (+ when y > 0), status `ok | illegal | psi_extrapolated |
  beyond_model` (export codes 1 -> illegal, 2/3 -> beyond_model; status 0 with psi > 60 -> psi_extrapolated),
  side-wall risk, other-HIVE flag (`sightBlocked`), aim point (0.401, 0), the turret bearing (field frame, deg,
  0 = +x, CCW) and `footprint` (`robot = {heading, length, width, offset: [fwd, left]}`; no heading = any heading
  of a 5 deg scan; illegal note "robot overlaps wall/HIVE base").
* `sectionFor(side, psi, meta)`: exported section, or linear interpolation in s_eff between the two neighbours
  (exact to the 1e-5 m rounding: hive.py lowers the roof linearly in |s|).
* `solve(q)`: coarse grid (v 2..16 step 0.1; theta 15..89.5 step 0.1 far / 0.25 near), then refinement:
  * `minRpm` / `minAngle`: the lowest clean v / hood angle the search found (search steps 0.01 m/s /
    0.025 deg). These are KNIFE EDGES: across the review sample the clearance there was 0 to 0.5 mm and the
    value moves with resolution, because the window edge carries about 0.1 deg of path-sampling (2 ms) noise.
    Each carries `margin` (clearance, m) and `entryAngle` at the point, `runLo..runHi` = the continuous
    clean run through it (sampled every 0.01 deg / 0.005 m/s, edges bisected; holes narrower than the
    sample step can still hide), the envelope `thetaLo..thetaHi` / `vLo..vHi` (outermost clean samples;
    NOT a clean interval) with `envelopeCleanFrac`, and `knifeEdge` (run narrower than the tolerance or
    clearance below it).
  * `minRpmTol` / `minAngleTol`: the lowest v whose continuous clean hood-angle run is at least
    `tol.theta` wide, and the lowest hood angle whose continuous clean speed run is at least `tol.v` wide,
    with clearance >= `tol.margin` at every sample (it can dip about 1 mm between samples). Default
    tolerance ASSUMED `{theta: 0.2 deg, v: 0.1 m/s, margin: 2 mm}`, overridable with `q.tol`. Found by
    search (first qualifying coarse column / row, then a fine scan below it): the lowest the search found,
    not a proven minimum. Runs are capped at about the needed width (`runCapped`).
  * `mostForgiving` (centre of the largest all-clean square) and `twin` (same solve with S = 0, c1 = 0). Fused integrate + classify fast path, bit-identical to
  `integrateOblique` + `classifyOblique`. Rows between the 0.5 deg pass-1 rows are evaluated only near shots
  that came within 0.12 m of the gate (`prune: false` turns this off; the tests show no clean cell lost).
  The release-relative integrator stop (0.4 m) is lowered for tall releases so it stays below the cell.
* PREDICTED windows, ASSUMED aero (drag and Magnus are included). Show every raw minimum with its clearance
  and run, labelled as a knife edge, next to the tolerant minimum. Tests: `tests/js_solver_check.js` (node), `tests/test_solver_js.py`.
* `q.sideWalls` (default `true`): 3D cell model below; `false` = the old section model (s_eff roof offset, side
  walls NOT modelled). The result carries `sideWalls`, `section` (model, ridge, wallT) and a model line in `notes`;
  `labels.side_walls` says which model ran. `q.ridge` (default true) and `q.wallT` override the 3D cell.

## Field geometry (PM-015, `src/field_geom.py`, JS twin in `solver.js`)

One set of functions for the export, `robustness.py`, the live solver and the page; `tests/test_field_geom.py`
checks the Python against dense references and against the JS through node (`tests/js_field_geom_check.js`).

| Item (research/GEOMETRY_AUDIT.md) | Now | Label | Status |
|---|---|---|---|
| Robot footprint (fix 2, rows 5, 9) | turned chassis (default 18 x 18 in, option 18 x 24 in) inside the walls and off the A-frame base, separating-axis test; release point inside too; `chassis_ok` / `footprint()` in pose, export, robustness, page clamp and drag | CONFIRMED sizes, ASSUMED 5 deg scan | fixed |
| A-frame keep-out (row 8) | the CONFIRMED base rectangle 38.95 x 49.46 in (the old +0.05 m box is gone); legs vs open mid-span not checked (U1) | CONFIRMED / UNVERIFIED | partly |
| Release offset (row 10) | option `offset` (forward, left) of the release point from the chassis centre, default 0 | ASSUMED | option added |
| Other-HIVE flag (fix 5, rows 28-30) | exact Liang-Barsky segment test from the release point to the aim point, one box everywhere | derived box, ASSUMED blocker | fixed |
| Grid (fix 8, row 6) | symmetric about x = 0, a row on y = 0, 69 x 68 | derived | fixed |
| HIVE tilt (fix 4, row 14) | 28.80-31.77 (wide 25.90-34.83) in `data/hive_geometry.json`, MC clip, page text | derived | geometry fixed; sweeps still at the old 28.5 / 31.5 (labelled, re-sweep deferred) |
| Sloped-roof clearance (fix 3, row 23) | the 3D cell (default) includes it; section model option `q.roofClear` / `Hive.from_json(roof_clearance=True)` lowers the roof by 0.00663 m, default OFF | derived | covered by the 3D cell |
| Side-wall flag (fix 6, row 27) | 3D: per shot from the path; page map: exact psi; wording "near-side estimate; far side not checked" | PREDICTED | fixed |
| Alliance (fix 7, row 32) | page red/blue toggle (mirror x and y), "mouth side (favourable)" / "back side (unfavourable)", sides swap on each tip | CONFIRMED rule | fixed |

Status counts of the regenerated `pos_status` (69 x 68): {0: 2262, 1: 1760, 2: 588, 3: 82}; 840 status-0 positions
carry the other-HIVE flag (old 69 x 69 grid: {0: 3180, 1: 567, 2: 882, 3: 132}). More positions are illegal
because the whole chassis must fit, not only the release point.

## Air, drag and draft options (2026-10-31, `physics.js` `airState` / `cdBase` / `aeroExt`, python `src/air.py`)

From research/MISSING_EFFECTS.md build-next 1, 2, 4 and 6. Every option is off by default except the air state.

* `q.air`: default still air 20 C, 101.325 kPa, dry: rho = 1.2041 kg/m^3, nu = 1.506e-5 m^2/s (derived:
  `rho = (p - 0.378 e) / (287.06 T)`, simplified CIPM-2007; `e = RH 611.2 exp(17.62 t / (243.12 + t))`; Sutherland
  viscosity). `{tC, pKPa | altM, rh}` = venue (user inputs; `altM` uses the US Standard Atmosphere pressure, a logged
  station pressure is better). `false` keeps `params.rho` as given: the exported masks and position files were made
  with the rounded 1.20 of `research/params_lit.json` (about 1 mm apart at the reference shot, derived).
* `q.drag.model`: `const` (default, params Cd, ASSUMED); `morrison` (smooth-sphere Cd(Re), Morrison 2013 with
  263000 in both places, about 0.40 in POLLEN's band: a reference curve, NOT a POLLEN fact); `blend` (what-if
  partial drag crisis Cd_sub -> 0.33 between Re 3e4 and 5e4 with smoothstep; ASSUMED until the T1 test).
  `q.drag.spin` = dCd (0 / 0.08 / 0.18 ASSUMED): `Cd += dCd min(S / 0.6, 1)`, backspin shot only (the twin has S = 0).
* `q.wind = {along, up}` m/s: constant draft in the shot plane (user); `side` (PM-016, below) adds a sideways part. Drag, Magnus and S use `v_rel = v - w`.
  The x-exit and apex shortcuts are switched off when a draft is set (a draft can push the ball back or up).
* Grip flag: `minRpm`, `minAngle` (by vLo), `minRpmTol`, `minAngleTol` and `mostForgiving` carry `gripLimited`
  when their exit speed is above the PREDICTED hood cap 8.9 m/s (docs/04_launcher.md); `gripCap = {v, rpm}`.
  A "possible" answer must not rest on a flagged shot.
* The twin always gets the same air, drag model and draft. Notes list the active options.
* Line-for-line Python copy: `src/feasibility.integrate_batch` reads the same keys (`cd_model`, `cd_sub`,
  `cd_post`, `re1`, `re2`, `dcd_spin`, `s_sat`, `wind`, `nu`). Cross-check: `tests/test_air.py` (JS vs Python
  trajectories for 9 option sets x 5 shots, to float32 storage precision) and `tests/js_air_check.js` (fused fast
  path == physics.js under random options on both cell models, options-off identity, twin, flags).
* Time: `morrison` costs about 3x (power functions at every RK4 stage); the others about 1.3-1.6x.

## Moving robot, hit chance and lift options (PM-016, `solver.js` `moveFor` / `launch3` / `fastShot3D` / `hitChance`, python `src/robustness.py`)

From research/MISSING_EFFECTS.md build-next 2a-2f. Every option is off (or 0) by default; with all off the answer
is unchanged (tests). Paper: Section 7, "Shooting on the move, hit chance and lift options".

* `q.move = {along, across, vx, vy, wz, d0, lead, rExit}` (user): robot speed toward the goal / to the left of
  the shot (m/s), field-frame speed (m/s), turn rate (deg/s), exit-angle offset `d0` (deg, ASSUMED 0), lead
  (default true), exit offset from the turn centre `[fwd, left]` m. Launch velocity = shooter velocity at
  (v, theta + d0) + robot velocity at the exit point (+ wz x r). Lead on: the shooter turns so the ball's ground
  track still points at the aim point; infeasible when the sideways robot speed exceeds v cos(theta + d0). Spin:
  backspin about the horizontal axis normal to the shooter direction, plus wz about z (twin: no backspin).
  Any `q.move` (even all zero) or a sideways draft uses the 3D flight on the 3D cell (at rest equal to the 3D
  cell model; a note says so when the section model was selected).
* `q.wind.side` (m/s, + = left of the shot): sideways draft; with `along` and `up` a full 3D draft vector.
* `res.moveSens` and `res.twin.moveSens` (when the 3D path is on): PREDICTED shift of the centre of the clean
  run per 0.1 m/s toward the goal and sideways (`dTheta`, `dV`, `dRpm`; `lost` when no clean run is left).
* `PollenSolver.hitChance(q, v, theta, {n = 1000, seed = 20261031, sig, sets, twinAt})`: Monte Carlo of the 3D
  path at one setting. ASSUMED launch scatter (1 sigma): speed 1.5 %, angle 0.40 deg, heading 0.50 deg
  (robustness.py ERR_SETS nominal). Aero sets Cl_low / nominal / Cl_high from `q.meta.cases` (one set named
  Cl_table when a user Cl(S) table is on, since the table replaces the lift of every set), the no-spin twin
  at `twinAt` (its own recommended setting) or the same setting; all use the same seeded normals. Returns
  `{sets: [{name, k, n, p, lo, hi}], twin, note}` with Wilson 95 % intervals. A model probability under ASSUMED
  scatter, NOT a measured repeatability. Python twin: `robustness.hit_chance` / `mc_shots(..., cell=...)`
  (same mulberry32 + Box-Muller normals, equal counts).
* `q.lift = {table, rev, gyro}`: `table` [[S, Cl], ...] user points (linear between points, straight from (0, 0)
  to the first, flat after the last); `rev` = Cl_rev 0..0.1 (ASSUMED; Kim et al. 2014 / Kray et al. 2012 smooth
  spheres, NOT POLLEN): when Re < 4.6e4 and S < 0.5 Cl blends to -Cl_rev min(S / 0.1, 1); `gyro` = gyro-correct
  S_perp = |w x v_rel| R / |v_rel|^2 on the 3D path (no change for pure backspin, tested). The page has the table
  and Cl_rev; `gyro` is on the page too since PM-017 (Advanced, "Gyro spin").
* `q.effMass = {phi}`: eps = (0.5 + phi) rho V / m, phi 0..1 ASSUMED (share of the air inside the ball that
  moves with it); dv/dt = (F_aero / m + g) / (1 + eps). POLLEN: eps 0.0045 (phi 0) to 0.0136 (phi 1), derived.
* Page: Advanced has "Robot moving" (toward, sideways, turn, d0, lead), the 3-part draft, "Spin lift options"
  and "Air carried with the ball"; the answer card has "Chance it goes in" (worker; main-thread fallback) and the
  per-0.1 m/s shift when the robot is moving. Hash: `#robot?move=along,across[,turn]`.
* Tests: `tests/js_move_check.js` (at rest == planar model, fused fast path == full 3D path, options-off
  identity, sensitivity present, no shot beyond the lead, hit chance reproducible / under 2 s / labelled, option
  effects), `tests/test_move.py` (Python vs JS launch states 1e-12, 3D paths 1e-9, classes, every
  Monte Carlo count; gyro, Cl table, reverse Magnus, effective mass), `tests/test_air.py`, `tests/js_air_check.js`.

Default spot (x -1.0, y 0.2, h 0.737, S 1.0; tolerant minimum, PREDICTED, ASSUMED aero; twin after the slash):

| option | clean pairs | tolerant min | twin |
|---|---|---|---|
| none (default) | 315 / 364 | 2784 rpm 73.30 deg | 2784 rpm 74.47 deg |
| moving, all 0 | 315 / 364 | same | same |
| 0.5 m/s toward | 317 / 362 | 2738 rpm 78.09 deg | 2719 rpm 79.01 deg |
| 0.3 m/s sideways, lead | 158 / 347 | 2812 rpm 73.41 deg | 2784 rpm 74.15 deg |
| 0.3 m/s sideways, no lead | 0 / 0 | none | none |
| turn 90 deg/s | 314 | 2793 rpm 73.42 deg | as default |
| d0 +1 deg | 315 / 364 | 2784 rpm 72.30 deg | 2784 rpm 73.47 deg |
| side draft 0.3 m/s | 219 / 241 | 2803 rpm 73.54 deg | 2793 rpm 74.61 deg |
| Cl table (0.5:0.2, 1.5:0.35) | 295 | 2803 rpm 73.25 deg | as default |
| Cl_rev 0.1 | 315 | 2784 rpm 73.30 deg (not active: S 1.0) | as default |
| phi 1 | 319 / 358 | 2765 rpm 73.34 deg | 2756 rpm 74.36 deg |

Hit chance at the recommended 2784 rpm, 73.30 deg (PREDICTED, ASSUMED scatter, n 1000): nominal 12.4 %
(10.5-14.6 %), Cl low 9.2 %, Cl high 7.4 %; twin at its own setting about 13 %, twin at the same setting 3.3 %.
Moving 0.5 m/s toward the goal shifts the hood angle about 1 deg per 0.1 m/s (PREDICTED). Solve time with the
3D path on: about 3-4 s in node (1.8 s default).

## Best chance, shot scatter and the chance layer (PM-017, `solver.js` `bestChance` / `hitChance` / split `solve`, python `src/robustness.py` `best_chance`)

Every chance here is a model probability (PREDICTED) under ASSUMED launch scatter and ASSUMED aero sets, 3D
flight. It is not a measured repeatability. Every backspin result is shown with its no-spin twin (S = 0).

* Launch scatter (ASSUMED, 1 sigma, independent normals): exit speed `sv` 1.5 % (relative), hood angle `sth`
  0.40 deg, aim left/right `spsi` 0.50 deg. `hitChance(q, v, theta, {sig})` and `bestChance(q, res, {sig})` take
  them. A source at 0 is off. The page sets them in Advanced, "Shot scatter" (speed %, angle deg, aim deg; hash
  `#robot?scatter=1.5,0.4,0.5`). Changing them does not re-solve the window: the workers keep their last grid and
  only run the search again.
* `bestChance(q, res, opts)`: two-stage search over the clean cells of the solved window (inside the PREDICTED
  grip limit 8.9 m/s when any clean cell is, else flagged `gripLimited`). Candidates: the clean cells ranked by a
  smoothed clean share (Gaussian over the grid with the speed and angle scatter as sigma), picked greedily at
  least one sigma apart, the best `k1` (24), plus the tolerant lowest-rpm / lowest-hood and most forgiving
  points. Stage 1 runs `n1` (64) shots per air set on each; those whose pooled Wilson upper bound reaches the
  best lower bound, at most `k2` (5), go to stage 2 with `n2` (400) shots; the winner (highest mean) is
  re-scored on `n` (1000) fresh shots per set (another seed, so the reported chance is not biased by the
  selection; Wilson 95 % range). Common random numbers: every candidate in a stage sees the same seeded normals
  (`P.normals`, prefix-stable). The score is the mean over the air sets, equal weight (Cl_low, nominal, Cl_high,
  or the user's Cl table as one set). Stage 4 (`breakdown`, off with `opts.breakdown === false`) runs one source
  at a time (the other two at 0) on the nominal (or Cl table) set; the lowest chance names the dominant source.
* `solve(q, onProgress, {part: "main" | "twin"})` solves one grid; the page runs the backspin grid and the twin
  grid in two Web Workers at once, then each worker searches its own grid. S = 0 with no Cl table: one worker
  (the twin is the same flight). Combined `solve(q)` is unchanged (tests check part == combined cell by cell).
* Answer card: the recommendation is the best-chance setting (its chance per air set with the 95 % range, the
  search stats, the twin's own best setting and chance, which scatter matters most for both), with the old
  lowest-rpm tolerant setting's chance beside it for comparison. Until the search is in, the tolerant setting is
  shown as provisional. Tiles: Best chance, Lowest rpm, Lowest hood, Most forgiving. The window chart marks the
  best chance (filled blue square) and the twin's best (hollow grey square).
* Advanced also has "Gyro spin" (`q.lift.gyro`, S_perp on the 3D path; no change for pure backspin).
* Field map "best hit chance" / "twin hit chance" colours: one spot per 0.3 m block (the legal cell nearest the
  block centre), a small search (`n1` 32, `n2` 128, `n` 300, `k1` 10, `k2` 3, field air set only, no breakdown,
  refine off, still air, 18 x 18 in robot), progressive in a pool of up to 3 Web Workers (coarse blocks first,
  then nearest the chosen spot), cached per height / S / air set / grip / scatter. The legend and caption say
  model probability under ASSUMED scatter. Hash: `#field?metric=chance`.
* Tests: `tests/js_chance_check.js` (parts == combined, S = 0 reuse, best >= the lowest-rpm setting for main and
  twin, grip limit, fresh draws == `hitChance`, reproducible, Wilson, breakdown, scatter inputs, moving, search
  time; wall-clock limits enforced only with `STRICT_TIMING=1`, reported otherwise), `tests/test_best_chance.py`
  (python replays the JS candidate lists, every stage count, the winner and the breakdown with the same seeds).

Default spot (x -1.0, y 0.2, h 0.737, S 1.0, grip 0.42 ASSUMED, nominal air, still; PREDICTED, ASSUMED scatter
1.5 % / 0.40 deg / 0.50 deg, n 1000 per set):

| | setting | Cl_low | nominal | Cl_high | mean | no-spin twin |
|---|---|---|---|---|---|---|
| before: lowest rpm with room for error | 2784 rpm (derived), 73.30 deg | 9.2 % | 12.4 % | 7.4 % | 9.7 % | 13.2 % at its own lowest rpm (2784 rpm, 74.47 deg) |
| after: best chance | 3062 rpm (derived), 76.2 deg (6.6 m/s) | 20.7 % | 29.5 % (27-32 %) | 6.4 % | 18.9 % | 37.5 % (35-41 %) at its own best, 3851 rpm, 82.1 deg (8.3 m/s) |

Which scatter matters most (one source at a time, nominal air): speed only 46.2 %, angle only 39.8 %, aim only
100 % -> hood angle; twin: speed 73.6 %, angle 44.3 %, aim 100 % -> hood angle. With speed scatter 3 % the best
chance moves to 3341 rpm, 78.0 deg (nominal 25.8 %), speed dominates; twin 3990 rpm, 82.6 deg, 29.0 %.
Moving 0.5 m/s toward and 0.3 m/s sideways (lead on): best 6.3 m/s, 79.5 deg; Cl_low 18.9 %, nominal 21.9 %,
Cl_high 7.0 %. Reading (derived): at this spot the twin's best chance is higher than with backspin (the twin
window reaches a steeper hood); more spin is not always better.

Speed (node, idle machine): combined solve 1.75-1.87 s -> backspin part 1.05 s and twin part 0.81 s in parallel
(wall about 1.05 s); moving: 1.72 s and 1.12 s (was about 2.7-2.9 s combined). The best-chance search adds
about 1.6 s (backspin) and 0.5 s (twin) after the answer shows. On a fully loaded shared machine (100 % CPU)
the same parts took 2.2 s in node and 7-10 s in headless Edge; the field chance layer took about 6 min for 80
blocks there.

## Flywheel droop readout (PM-022, `solver.js` `droopReadout` / `DROOP`, python `src/launcher.py` `droop_readout`)

A readout only (PREDICTED, closed form, no fitted factor): every shot is still solved at the set wheel speed, so
the window, the chance search and the field map do not change. The wheel coasts while the ball is squeezed
(fixed hood), then the motor at full power brings it back.

* Drop per shot: `I_w dOm = R_w m [(v - v_in) + kI S v R_b / r_c] / 2` (the impulse that gives the ball its speed
  and spin, generalised Brettle) `+ c_rr k_n delta rho T` (rolling loss), `r_c = R_b - lam delta / 2`,
  `rho = R_w + r_c`, contact time `T = wrap rho / v` (hood_model's is 0-60 % longer above 1000 rpm). Values =
  launcher PARAMS (`DROOP`): m, R_b CONFIRMED; R_w, delta user; kI, I_w, k_n, lam, c_rr, wrap 90 deg, v_in 0.5 m/s
  ASSUMED.
* Recovery = `recovery_time`: straight torque-speed line, free speed and stall torque times battery V / 12,
  `tau = I_w w_f / (gear stall V/12)`, `t = tau ln((w_f - w_start) / (w_f - w_set))`. Infinity when the set rpm is
  at or above the free speed at that voltage (the page says "never" with a warning). Minimum shot interval =
  contact + recovery (feed time not included).
* `droopReadout(wheelRpm, v, S, {motor, Iw, volts, ...})` returns `dropRpm, dropPct, impulseRpm, hystRpm,
  contactS, recoverS, minIntervalS, freeRpmLoaded, aboveFree` (python: `drop_rpm` ... `above_free`).
* Advanced, "Flywheel droop" (no re-solve, only the readout changes): motor goBILDA 5203 1:1 (default) or REV HD
  Hex bare (CONFIRMED datasheets at 12 V: 6000 rpm, 0.144 / 0.105 N m stall), wheel inertia 2.65e-4 kg m^2
  (ASSUMED: 98 mm wheel about 1.0e-4, a guess, + goBILDA 82 mm steel flywheel 1.65e-4 CONFIRMED; clamp 5e-5 to
  1e-3), battery 12 V (user; clamp 9 to 14). Not in the URL hash.
* Answer card: one line for the answer and one for the no-spin twin at its own setting (S = 0 takes no spin from
  the wheel); Details has the split, the contact time and the minimum interval. `body[data-robot-test]` has
  `droop=main:<rpm>rpm/d<drop>/<pct>%/rec<s>s/min<s>s,twin:...|same|none,set:<motor>/<I_w>/<V>` (`pending`
  until solved; `inf` when the motor cannot reach the rpm).
* Agreement with `hood_model` (`tests/test_launcher.py` `DroopReadout`, asserted within 3 %): RPM_GRID at the
  defaults +0.9 % (1000 rpm) to -1.5 % (4000-6000 rpm); I_w 5e-5 to 1e-3 x wrap 60-120 deg at 2000-6000 rpm
  -1.7 % to +2.1 %. Limit: below 2000 rpm a light wheel loses most of its speed, the ball slows before it leaves
  and T is overestimated, so the drop reads high (1000 rpm, wrap 90: +5 % at 1e-4, +30 % at 5e-5 kg m^2).
* JS = python: `tests/js_droop_check.js` (node, run by `test_js_twin_matches_python`, 90 cases, both motors, 11 /
  12 / 13.2 V, three inertias): max relative error 2e-16, Infinity cases agree; the JS constants are checked
  against launcher PARAMS.
* Not modelled: motor drive during contact, controller lag, current limit, motor rotor inertia (I_w only), battery
  sag under load, feed time, and the next shot leaving slower when it is fired before the wheel is back.

Default spot (x -1.0, y 0.2, defaults above; PREDICTED): answer 3062 rpm, 6.6 m/s, S 1.0: drop 251 rpm (8.2 %) =
spin and speed impulse 232 + rolling loss 19, contact about 20 ms, back to speed in 0.095 s, shots at least
0.114 s apart. No-spin twin 3851 rpm, 8.3 m/s: 187 rpm (4.9 %), 0.096 s, 0.112 s. At 9 V (the lowest input) the
free speed is 4500 rpm, so only settings above 4500 rpm get the warning. REV HD Hex, 1.0e-4 kg m^2, 11 V: 664 rpm
(21.7 %), 0.144 s.

## 3D cell model (PM-013, `physics.js` `buildCell3D` / `classifyOblique3D`, python `src/cell3d.py`)

Exact clean test of the ball-centre path (x, y, z) against the cell as 3D faces inflated by R = 0.0355 m
(faces, edges and corners: the clearance is the exact segment-to-polygon distance minus R).

* Geometry: the exported s = 0 section (`<side>_s0`) extruded across the cell; side walls at +-0.254 m
  (CONFIRMED, manual 20 in cell) with inner face, rim and outer face; wall thickness 0.0508 m (ASSUMED);
  pentagon roof: the ridge drops `ROOF_SLOPE * |s|` towards the side walls (derived from the opening profile
  0.3556 -> 0.19329 m over 0.254 m). Lateral path offset `s = (aimX - x) tan(psi)` (aim at the cell centre).
* Clean = the centre enters the cell interior (inside the gate) before any face is closer than R; first face hit
  is reported (`hit`), clearance before entry (`minClear`) and the entry angle as in the section model.
* psi = 0 with the ridge off reproduces `classifyOblique` on the s = 0 section bit for bit (result, step, hit,
  clearance, entry angle; tested on 2500 shots per side). The ridge on is stricter only (0 shots clean that the
  section calls not clean; a few clean section shots now graze the lower roof off the centre line).
* Fast path: per-step lower bounds per face (branch and bound), exact where it matters; equal to
  `classifyOblique3D` in class and clearance (to 1e-12 m) on 7000 tested shots. Python port equal to JS on 560
  random shots (result, step, clearance 1e-9, entry angle, hit face). Tests: `tests/js_cell3d_check.js`,
  `tests/test_cell3d.py`.
* Time: full solve + twin about 1.5-3 s in node (3-4x the section model; measured 2.7-6 s while the machine was
  loaded by other jobs).
* Clean-run sampling (`runLo..runHi`) now steps at a quarter of the step near the minimum: the 3D model has thin
  hit fringes (about 1.5 mm/s) beside knife-edge minima.

Clean (v, theta) cells, old section model vs 3D model (PREDICTED, ASSUMED aero, coarse grid without refinement,
d = 1.0 m, h = 0.5 m, S = 1.0 with its S = 0 twin in brackets; unfav psi 60 is not a legal pose at d = 1.0):

| psi deg | unfav old | unfav 3D | fav old | fav 3D |
|---|---|---|---|---|
| 0  | 306 (348) | 301 (346) | 645 (651) | 631 (634) |
| 10 | 257 (297) | 290 (339) | 573 (579) | 637 (633) |
| 20 | 212 (253) | 309 (347) | 500 (506) | 640 (647) |
| 30 | 167 (196) | 320 (363) | 427 (417) | 673 (670) |
| 40 | 164 (186) | 362 (401) | 420 (431) | 737 (748) |
| 50 | 195 (228) | 418 (464) | 503 (500) | 844 (855) |
| 60 | -         | -         | 628 (629) | 1007 (1024) |

Other poses (old -> 3D, twin in brackets): fav S1.0 d1.2 h0.5 psi45 627 (657) -> 1183 (1271); fav S0.5 d0.9
h0.3 psi55 401 (392) -> 655 (654); unfav S0 d1.4 h0.737 psi40 170 -> 364 (S = 0, it is its own twin); unfav
S1.5 d1.4 h0.3 psi20 174 (198) -> 246 (276).

Reading (derived): at psi = 0 the 3D cell is a little stricter (the pentagon roof is lower off the centre line).
With psi the old model shrank the window (one lower roof section) while the 3D path crosses the cell on a
diagonal: the opening it sees is longer and the roof is only low near the side walls, so the 3D windows grow.
The side wall itself only bites where the lateral drift reaches it. These larger windows are still optimistic in
one way: what happens AFTER entry is not modelled (see below).

Still NOT modelled (effects that could change the windows; none quantified here):
* post-entry contact: a ball that enters on a steep lateral diagonal can hit the inner side wall or back wall and
  rebound out; rim-in (a ball that touches the lip and still drops in) is counted as a hit (conservative).
* wall thickness and lip shape: 0.0508 m and the flat rim are ASSUMED (CAD or a measurement would settle them).
* launcher sidespin and exit skew (a spin axis tilted by robot turning, sideways drafts and robot motion are
  options now, PM-016), the churro rods, the other HIVE as an obstacle (flagged only), other robots, release-position and angle
  errors (no probabilities), ball-to-ball variation (no repeatability claims), aero coefficients (ASSUMED).
