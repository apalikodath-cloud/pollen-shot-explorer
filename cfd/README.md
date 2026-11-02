# PM-012 CFD: POLLEN in still room air (own GPU LBM-LES)

> **Update (2026-11-02).** The current state is in "Status (2026-11-02)" and "POLLEN results" below. The later
> sections are the validation notebook from 2026-10-31, with dated notes where a result came in after it. The flight
> model still uses the ASSUMED literature aero (`cfd_aero.json` stays "not released").

The coach asked to "add fluid sims of standard room temp static air so it's more accurate". Today the model's drag
(Cd 0.48, range 0.35-0.65), Magnus lift (Cl = min(c1 S, Cl_max)) and spin decay are ASSUMED literature values
(`data/aero_params.json`, sources in `research/params_lit.json`). This folder holds a GPU CFD setup meant to give
PREDICTED values for POLLEN itself. Nothing from it may be used until the smooth-sphere gates below pass.

## Labels

The labels are defined in `docs/08_shooter_spec.md` lines 5-6: PREDICTED (model output), ASSUMED (a modelling
choice), USER (given by the team), CONFIRMED (from official CAD), derived (computed from CONFIRMED / USER inputs).

- **Every CFD output in this folder is PREDICTED.** That covers Cd, Cl, Cy, CM, k, u_win, trends, box factors, grid
  changes, lateral forces and errors against a reference. They come from our own solver, which has not passed
  validation.
- Earlier text called them "derived": the heading "Checks so far (derived, own solver ...)" in this README and the
  message of commit ca68597 ("README: Re 33057 diagnosis table (all derived)"). That label was wrong. Read every CFD
  number in those commits as PREDICTED.
- Commit IDs 208142e, 28f95b1 and ca68597 are from the development history before this repo was published; they
  are not in this repo's history. The later IDs in this file (44ce149, 34ad763, fe50df2, fc22cd5, 5e8dd38, 2dd78dd,
  b686e2d) are in it.
- Inputs keep their own labels (table "Inputs"). Run times and speeds are read from the run logs (derived).

## Status (2026-11-02)

- **Not released.** No CFD number may replace an ASSUMED value in the model. `cfd_aero.json` records the same
  status and holds no POLLEN values. The explorer's CFD tab (`viz/explorer/cfd_runs.json`) shows the POLLEN runs as
  PREDICTED solver output, each backspin case beside its no-spin twin.
- **Solver.** Every run used route (b), the LBM-LES solver written for PM-012 in `cfd/lbm/`. FluidX3D (route a) was
  never built or run (section "Not used"). The build that produced the POLLEN results is in this repo (merge commit
  b686e2d). Since the status of 2026-10-31 14:20 it adds:
  - `wall=ibb`: interpolated bounce-back with the exact wall distance of every link (section "Method");
  - `body=pollen`: an analytic POLLEN shell with 26 holes, built from the CAD dimensions instead of the STL;
  - `dump=`: velocity-field snapshots for the flow viewer (`viz/flow/`);
  - the queue scripts in `cfd/lbm/queue/` (section "GPU queue").
- **Gates with `wall=ibb`** (smooth sphere, lv 3, BGK, FP16, Cs 0.1, T 150; section "Validation results"):
  - V1 at D 128: box-corrected Cd 0.4425, -2.3 % against 0.453, window stationary: **pass**.
  - V2 at D 128: Cl 0.362 is above the band 0.22-0.33: **fail**. At D 192, Cl 0.270 is inside the band, but no D 192
    S 0 sphere run exists, so V1 and V2 are **not decided** there.
  - Torque gate: CM 0.0084 (D 128) and 0.0088 (D 192), above 0.0047-0.0079: **fail** at both. CM and k stay unusable.
  - So no grid has passed V1 and V2 together, and the release rule ("Acceptance") is not met.
- **POLLEN runs finished: 24**, all `body=pollen`, `wall=ibb`, lv 3, BGK, FP16, T 150, each a single run:
  - between holes (`btw`), D 128: S 0, 0.25, 0.5, 0.75 and 1.0 at Re 20000, 33057 and 47224, plus S 1.5 at
    Re 33057 (16 runs);
  - hole facing the flow (`hf`), D 128, Re 33057: S 0, 0.25, 0.5 and 1.0 (4 runs);
  - a third orientation (`o3`), D 128, Re 33057: S 0 and 0.5 (2 runs);
  - between holes, D 192, Re 33057: S 0 and 0.5 (2 runs).
- **Not finished:**
  - D 192, between holes, Re 33057, S 1.0: parked to stay inside the cloud GPU budget. At lv 3 it needs about
    23.7 GiB (solver plan), so it needs a GPU with more than 16 GB.
  - A D 64 POLLEN S 0.5 run on the onboard GPU was stopped at t* 20. It is not in the results.
  - The revox check for `body=pollen` has not run.
- **Queue:** empty (section "Queue (2026-11-02)").

### Earlier results with halfway bounce-back (`wall=hbb`)

These led to `wall=ibb`. Details are in "Validation results" and "Finest-box bias".
- **V0** (sphere spinning in still fluid, Stokes torque) passes: 1.026 x analytic. It is not a production check: it
  runs at Stokes Re (Re_rot 0.4), FP32, regularized collision and tau 1.1, while the production runs use BGK, FP16,
  tau 0.5001-0.5010 and Re 20000-47224.
- **V1** failed at every grid and setting. Uniform D 48 at T 150 gave box-corrected Cd 0.545 and 0.542 (two noise
  seeds), uniform D 94 at T 150 gave 0.507 (window not stationary), and lv 3 D 128 gave 0.504 (stationary, above
  0.50). The band is 0.43-0.50.
- **V2** at uniform D 48 fails: Cl 0.252 is in the band, but its window and the seed-0 twin's window are not
  stationary, and u_win(Cl) + L_twin is 0.073 > 0.055. V2 at lv 3 D 128 was not run with `wall=hbb`.
- **Torque.** At uniform D 48 the smooth sphere at S 0.5 gives CM +0.00004 (a diagnostic, section "Torque gate"). A
  sphere spinning in still fluid gets a torque with the wrong sign (it drives the spin) at D 64, 128 and 192
  ("Validation results"). `wall=ibb` gives the right sign.
- **STL path.** The STL sphere at S 0.5 gives Cd +0.067 and Cl +0.101 above the analytic sphere (D 48): **fail**. At
  S 0 it matches in Cd (**pass**; the rule was written after the run, so it is not blind). Its static torque is
  F_STL = 0.00365. The published POLLEN runs use the analytic `body=pollen`, not the STL.
- **Finest box.** The first default finest box biased Cd, Cl and CM. The box A/B at D 128 with the adopted box
  fb 1.5 / 2.5 / 1.5 passed at S 0 and S 0.5 ("Finest-box bias").

## POLLEN results (PREDICTED, not released)

Solver output for the analytic POLLEN body: `body=pollen`, `wall=ibb`, lv 3, BGK, FP16, Cs 0.1, u 0.05, default `fb`
and `gb`, box 6 x 4 x 4 D, T 150. **Every number in this section is PREDICTED.** Each case is a single run. No run was
repeated, so nothing here says how well a number repeats. The gates have not passed ("Status"), so none of these
values may replace an ASSUMED value in the flight model.

- Means are plain means of the CSV rows over t* 15-150 (`viz/explorer/export_cfd.py`; the same values are in
  `viz/explorer/cfd_runs.json`). They are in the CFD convention (R_cfd 35.56 mm), not converted ("Converting").
- Window spread u_win (`postprocess.py summary`) over these runs: Cd 0.005-0.013, Cl 0.011-0.023, CM 0.0003-0.0008.
  Every window passes the stationarity test except the Cl window of the Re 20000 S 0 twin.
- Spin is backspin about +y, so Cl > 0 is upward lift. S = omega R / U.
- **CM is not usable**: the torque gate fails with `wall=ibb` (section "Torque gate"). No spin decay k may be
  derived from these CM values.
- The orientation of the holes against the flow is ASSUMED (three choices below). How POLLEN is oriented in a real
  shot is not known.
- Each backspin row sits under its no-spin twin (S 0, in bold). The twin is not subtracted (section "Lateral force of
  the no-spin twin").

### Between holes, D 128, by Reynolds number

Speeds are derived from Re = v D / nu (4722 per m/s, table "Inputs").

**Re 20000 (about 4.2 m/s)**

| S | Cd | Cl | CM |
|---|---|---|---|
| **0 (twin)** | **0.6101** | **0.0468** | **0.00029** |
| 0.25 | 0.6391 | 0.1531 | 0.02026 |
| 0.5 | 0.6454 | 0.2494 | 0.04496 |
| 0.75 | 0.6557 | 0.3127 | 0.06513 |
| 1.0 | 0.6499 | 0.3477 | 0.08458 |

**Re 33057 (7 m/s)**

| S | Cd | Cl | CM |
|---|---|---|---|
| **0 (twin)** | **0.5935** | **0.0464** | **0.00008** |
| 0.25 | 0.6249 | 0.1501 | 0.01995 |
| 0.5 | 0.6332 | 0.2508 | 0.04468 |
| 0.75 | 0.6489 | 0.3064 | 0.06456 |
| 1.0 | 0.6425 | 0.3575 | 0.08397 |
| 1.5 | 0.6460 | 0.4203 | 0.13873 |

**Re 47224 (about 10 m/s)**

| S | Cd | Cl | CM |
|---|---|---|---|
| **0 (twin)** | **0.5871** | **0.0481** | **-0.00021** |
| 0.25 | 0.6197 | 0.1430 | 0.01981 |
| 0.5 | 0.6272 | 0.2496 | 0.04461 |
| 0.75 | 0.6467 | 0.3216 | 0.06500 |
| 1.0 | 0.6438 | 0.3559 | 0.08425 |

### Orientation, D 128, Re 33057

Angles rx, ry, rz in degrees (ASSUMED), applied about x, then y, then z, as for `body=stl`.

| Orientation (rx, ry, rz) | S | Cd | Cl | CM |
|---|---|---|---|---|
| between holes, `btw` (0, 135.114, -138.843) | **0 (twin)** | **0.5935** | **0.0464** | **0.00008** |
| | 0.25 | 0.6249 | 0.1501 | 0.01995 |
| | 0.5 | 0.6332 | 0.2508 | 0.04468 |
| | 1.0 | 0.6425 | 0.3575 | 0.08397 |
| hole facing the flow, `hf` (0, -169.287, 164.412) | **0 (twin)** | **0.6112** | **0.0164** | **-0.00139** |
| | 0.25 | 0.6326 | 0.1530 | 0.01983 |
| | 0.5 | 0.6367 | 0.2514 | 0.04575 |
| | 1.0 | 0.6456 | 0.3556 | 0.08476 |
| third orientation, `o3` (0, 45, 30) | **0 (twin)** | **0.5955** | **0.0151** | **-0.00050** |
| | 0.5 | 0.6374 | 0.2536 | 0.04531 |

### Grid: D 128 against D 192 (between holes, Re 33057)

| S | Finest D | Cd | Cl | CM |
|---|---|---|---|---|
| **0 (twin)** | 128 | **0.5935** | **0.0464** | **0.00008** |
| **0 (twin)** | 192 | **0.5801** | **0.0415** | **0.00049** |
| 0.5 | 128 | 0.6332 | 0.2508 | 0.04468 |
| 0.5 | 192 | 0.6188 | 0.2071 | 0.04070 |
| change from D 128 to D 192, S 0.5 | | -2.3 % | -17.4 % | -8.9 % |

- The D 192 twin diverged at step 240 (t* 0.05) when it started with noise (seeds 0 and 1, `pert=1e-3`). It was
  rerun with `pert=0`, so it starts without noise, unlike its S 0.5 partner (`pert=1e-3`).
- Drag changes by about 2 % between the grids. **Lift is not grid-converged**: Cl at S 0.5 drops 17 %. The smooth
  sphere does the same (Cl 0.362 at D 128, 0.270 at D 192; "Validation results").

### Reading (PREDICTED, derived from the tables)

- In every series Cl rises with S, by smaller steps at higher S: about 0.15 at S 0.25, 0.25 at S 0.5 and 0.35 at
  S 1.0 at all three Re, and 0.42 at S 1.5 (Re 33057).
- Cd rises with spin too: from 0.59-0.61 at S 0 to 0.64-0.66 at S 0.75, then stays about level. Spin adds drag as
  well as lift. These runs do not show that more spin is always better for a shot; that depends on the whole flight.
- Going from Re 20000 to 47224 lowers the S 0 Cd by about 4 % (0.610 to 0.587). At the same S, Cl differs by at most
  0.016 between the three Re, about the size of the window spread.
- Orientation at Re 33057 moves the S 0 Cd by up to 0.018 (0.594, 0.611, 0.596) and Cl by at most 0.003 at the same
  S above 0.
- The S 0 twins carry a lift of their own, Cl 0.015-0.048. The ball with its holes is not symmetric, and the wake
  swings slowly (section "Lateral force of the no-spin twin").
- POLLEN CM at S 0.5 is about 0.045, about five times the smooth sphere's 0.0084 on the same grid. CM is not usable
  (above).

## Acceptance (binding)

This is the only acceptance rule. Its bands are the ones pre-registered at 09:32 on 2026-10-31, before any run
(commit 208142e: V1d "Box-corrected Cd in 0.43-0.50", V2 "Cl in 0.22-0.33"). The review added the averaging,
lateral-force and STL conditions. The torque gate, the S 0 STL rule and the twin-stationarity condition of V2 were
added at 13:47 after the second review, before their evaluation. `postprocess.py v1`, `v2`, `torque`, `stl0`
and `match` apply it.

| Gate | Passes only when |
|---|---|
| V1: smooth sphere, Re 33057, S 0 | box-corrected Cd is in 0.43-0.50, the Cd window is stationary, and u_win(Cd) <= 0.035 (half the band). Reference: Brown & Lawler (2003) Eq. 19 gives 0.453 at Re 33057 (derived). |
| V2: smooth sphere, Re 33057, S 0.5 | Cl is in 0.22-0.33, the Cl window is stationary, the S 0 twin covers the same window and its Cl window over it is stationary, and u_win(Cl) + L_twin <= 0.055 (half the band). With twins of more than one noise seed, every twin meets these conditions and L_twin is the largest of them. |
| Run length | every V1 and V2 run is at least T 150 (window t* 15 to the end). |
| One configuration | V1 and V2 pass with the same collision, Cs, precision, grid and box. POLLEN runs use exactly that configuration. |
| STL path | an STL sphere (`lbm/sphere_stl.py`) spinning at S 0.5 matches the analytic sphere in Cd, Cl and CM at the release grid. |
| STL path, S 0 | an STL sphere and the analytic sphere at S 0, same grid and settings, T >= 150: both Cd windows are stationary and \|Cd difference\| <= max(t95 sqrt(se_a^2 + se_b^2), 0.01). CM, Cy, Cl and L are reported, not gated. \|CM\| of the STL run is the static torque floor F_STL. |
| Torque: smooth sphere, Re 33057, S 0.5 | CM is in 0.0047-0.0079 (reference 0.0063 +- 25 %), the CM window is stationary, and u_win(CM) <= 0.0016 (half the band), in a run with BGK, FP16, Cs 0.1, u 0.05 and T >= 150 on the release grid and box. Section "Torque gate". |
| revox | one POLLEN spin case run at two `revox` values matches in Cd, Cl and CM. |

- **Match** (`postprocess.py match`): both runs are stationary, and |difference| <= max(t95 sqrt(se_a^2 + se_b^2),
  floor). Floors (ASSUMED): Cd 0.01, Cl 0.01, CM 0.001.
- **Band on POLLEN numbers**, once released. Cd is reported as X +- (b |X| + u_win). Cl is reported as
  X +- (b |X| + u_win + L_twin). Here b = max(|V1 error|, |V2 error|, |grid change|), where:
  - V1 error = box-corrected Cd / 0.453 - 1;
  - V2 error = Cl / 0.275 - 1 (0.275 is the band centre);
  - grid change = the relative change between the two finest grids.

  So the band is never smaller than the V1 error.
- **Band on CM and k**, once the torque gate passes: X +- (e_M |X| + u_win), with e_M = max(|CM_gate / 0.0063 - 1|,
  0.25) from the torque gate run, not from b. Every POLLEN CM and k comes through the STL path, so the half-width is
  never smaller than F_STL for CM and F_STL x kf for k (kf = k / CM, section "Converting").

*Note 2026-11-02 (added; the rules above are unchanged).* The STL-path rows and the F_STL floor were written when
POLLEN was to run through the STL. The published POLLEN runs use the analytic `body=pollen` with `wall=ibb`, which
the solver refuses for STL bodies. Whether the STL-path conditions apply to `body=pollen` has not been decided.
Nothing is released either way.

### Torque gate (pre-registered 2026-10-31 13:47)

**Why.** V0 checks the torque sign and normalisation, not the production configuration (Status). The review found
(PREDICTED): the smooth sphere at S 0.5 gives CM +0.0000 (u_win 0.0012) at uniform D 48, T 150; -0.0004 at D 48,
T 55; about +0.0012 at uniform D 64; +0.0020 (u_win 0.0006) at refined D 64 with the new finest box. A laminar
estimate gives 0.003-0.006. The wall layer is thin: D / sqrt(Re) is 0.26 cells at D 48 and 0.53 at D 96. The
moving-wall term, Ty and the CM formula were re-derived and found correct.

*Note 2026-10-31 (added after pre-registration; the text above is unchanged):* the +0.0020 (u_win 0.0006) at refined D 64
came from the run with finest box fb 1.2 / 2.5 / 1.2 (ab_r64l3_S0.5_fb1.2), not from the adopted box. The same case with the
adopted box fb 1.5 / 2.5 / 1.5 (ab_r64l3_S0.5_fb1.5) gives CM +0.0017 (u_win 0.0010), t* 15-40 (PREDICTED). The pass band
0.0047-0.0079 is unchanged.

**Case.** Smooth analytic sphere (`body=sphere`), Re 33057, S 0.5, BGK, FP16, Cs 0.1, u 0.05 (tau 0.50022 at D 48,
0.50029 at D 64, 0.50044 at D 96), T >= 150, window t* 15 to the end, on the release grid and box (the grid, `lv`,
`fb`, `gb` and box on which V1 and V2 pass). The V2 run is this case when it runs on the release grid.

**Reference: CM_ref = 0.0063 (derived).**
- Ito & Kamijima (2025), Table 5: LES (Fluent, Smagorinsky-Lilly, y+ < 1) of a spinning 40 mm table-tennis ball.
  Cm 2.17e-3 at SP 0.377 and 3.99e-3 at SP 0.565 (10 m/s, Re 26558); Cm 1.95e-3 at SP 0.377 and 3.00e-3 at SP
  0.503 (15 m/s, Re 39837). SP = |w| a / |v| is our S.
- Linear in SP to 0.5: Cm 3.36e-3 (Re 26558) and 2.98e-3 (Re 39837). Linear in Re to 33057: Cm 3.17e-3 (linear in
  log Re: 0.2 % higher).
- Their torque is T = -Cm pi a^3 rho |v|^2 (Ito & Kamijima 2022, eq. 4; ASSUMED to hold in the 2025 paper, which
  cites it). Ours is CM = -Ty / (q R) with q = 0.5 rho v^2 pi R^2, so CM = 2 Cm = 0.0063.
- Cross-check: Ito & Kamijima (2022), Table 4 (COMSOL k-epsilon, rough ball): Cm about 2.45e-3 at Re 26557 and
  2.14e-3 at Re 53115 for SP 0.5, so CM 0.0047 at Re 33057 (-25 %).

**Pass** (`postprocess.py torque`): the case above, CM in 0.0047-0.0079 (+-25 %, ASSUMED: the spread between the
two published values), the CM window stationary, and u_win(CM) <= 0.0016 (half the band).

**Use.**
- e_M = max(|CM_gate / 0.0063 - 1|, 0.25) sets the band on CM and k ("Band on CM and k" above).
- STL floor: F_STL = |CM| of the STL sphere at S 0 (its static torque bias; rule "STL path, S 0").
- If the gate fails, no CM or k is released, quoted or matched.

**Not blind.** The reference and the band come from the two papers only, but the review's D 48 and D 64 values
above were known when this was written. With a wall layer under one cell at every grid that fits on the card, the
gate may fail at all of them (PREDICTED); then CM and k stay unreleased.

**Diagnostic, not the gate** (`postprocess.py torque` on g48_v2_S0.5_T150, evaluated 14:09). Uniform D 48 is not
the release grid. CM +0.00004 +- 0.0012 (26 batches; trend -0.0021 over the window, above the 0.002 tolerance: not
stationary), -99 % from the reference (PREDICTED). It meets the configuration, run-length and u_win conditions and
fails the band and stationarity. The gate itself has not run: no release grid exists while V1 fails.

*Result 2026-11-01 (`wall=ibb`; added after pre-registration, the rule above is unchanged).* The gate case was run
with `wall=ibb` at lv 3 D 128 and lv 3 D 192 (v2_ibb_d128_S0.5 and v2_ibb_d192_S0.5; BGK, FP16, Cs 0.1, u 0.05,
T 150): CM 0.0084 +- 0.0004 and 0.0088 +- 0.0005, both windows stationary, both above 0.0047-0.0079 (PREDICTED).
**Fail** at both grids. Neither grid is a release grid (V2 fails at D 128 and is not decided at D 192), but both
runs miss the band. CM and k stay unreleased.

### Withdrawn: the "30 % gate"

- **What:** "Cd within 30 % of 0.4532", printed as "30 % gate 0.317-0.589".
- **When and who:** it was written into this README while the solver was being built, in commit 28f95b1 at 10:18
  on 2026-10-31 ("fails the 30 % gate"). That was 11 minutes after the first D 48 run (10:07, Cd 0.699, +54 %) had
  failed the pre-registered band. It was not in the task brief or in the pre-registered table. Commit ca68597 (10:32)
  then called the BGK run (Cd 0.563, +24 %) "inside the gate".
- **Why:** no reason was written down. It was a relaxation made after a failing result. A +-30 % band is also about as
  wide as the ASSUMED range the model already uses (Cd 0.35-0.65), so passing it would add nothing.
- **Now:** withdrawn, together with "inside the gate". Notes outside the repo (`queue/ANALYSIS.md`, the header of
  `queue/held.txt`) may still mention it. This section overrides them.

## Route

| Option | Status | Why |
|---|---|---|
| (b) own LBM-LES (OpenCL), `cfd/lbm/` | **used for every run** | Written from scratch for PM-012. It contains no FluidX3D code. |
| (a) FluidX3D | **not used so far** | The coding environment's permission check refused the build, so it was never built or run. Its files stay (section "Not used"). A FluidX3D build as an independent cross-check has been proposed; this row changes if it is run. |

## Method (route b, as run)

**Solver** (`lbm/pm012_lbm.cpp` host, `lbm/pm012_lbm.cl` kernels, built with `lbm/build.cmd`; run on an RTX 3060 12 GB
and on cloud GPUs, A100 40 GB and V100 16 GB):
- D3Q19 with two lattices and pull streaming. Storage is FP16 (`prec=fp32` is optional).
- Collision: BGK (`coll=bgk`) for every current V1, V2 and POLLEN line. The default, `coll=reg` (regularized), gave
  Cd 0.68-0.71 at Re 33057 and is not used for gates.
- Smagorinsky LES with Cs 0.1 everywhere. The diagnosis knobs `bulk`, `csn` and `taun` stay off.
- Walls (`wall=`). Spin is about +y, so backspin lift points along +z.
  - `wall=hbb` (default): halfway bounce-back on the voxel staircase, with the moving-wall (Ladd) term,
    u_w = w x (x - c). Every run before 2026-10-31 17:07 (commit 34ad763) used it.
  - `wall=ibb`: interpolated bounce-back (Bouzidi, Firdaouss and Lallemand 2001) with the exact wall distance q of
    each link, both the q < 1/2 and the q >= 1/2 branch, and the moving-wall term taken at the wall point. Where the
    q < 1/2 branch has no plain fluid cell behind the link, that link falls back to moving bounce-back. The force
    uses the Galilean-invariant momentum exchange of Wen et al. (2014) on each link. Only for the analytic bodies
    (`body=sphere`, `rotstokes`, `pollen`, `rotpollen`); the solver refuses it for `body=stl` and `body=none`. Every
    POLLEN result and every `*_ibb_*` gate run uses it.
- Force and torque: momentum exchange over the wall links. Each CSV row averages every step since the previous row
  (`favg=1`). The row length is even, so a force that alternates every step cancels inside each row. The log footer
  reports that alternation as `p2_*`.
- Boundaries: equilibrium inflow (u = 0.05, lattice Mach 0.087) on the inlet and the four side faces. Pressure outlet
  (`outlet=p`).
- Start: uniform flow plus noise of 1e-3 u from a hash of the cell index (`pert=1e-3`). `seed=` (default 0) shifts
  that hash, so the start noise can be varied. Every run in this README used seed 0 (no queue line sets `seed=`),
  except the second S 0 twin g48_v1_S0_T150_seed104729 (seed 104729). The CSV header does not record the seed; a run
  with another seed keeps its command line in a `.cmd.txt` file next to its CSV. An earlier version of this README
  said there was no seed key; the key was added to the solver in commit 44ce149. The seed-104729 run used a
  development build, not a committed one (its CSV header shows the default fb=1.2,2.5,1.2, which acts only with `lv`
  2 or more). With seed 0 that build gave the forces and Cd, Cy, Cl of g48_v1_S0_T150 bit for bit over the first 14
  CSV rows (t* 0.28); the torques differed by at most 6e-8 (lattice units).
  The POLLEN runs used seed 0 and `pert=1e-3`, except the D 192 S 0 twin (`pert=0`, section "POLLEN results").
- Box 6 x 4 x 4 D (8 x 6 x 6 D for the box check). Body centre 2 D from the inlet (`xc=2`).
- Run length T in t* = D/U, with about 50 CSV rows per t*.

**Bodies:**
- `body=sphere`: the sphere is voxelized analytically at D cells.
- `body=stl`: a binary STL in mm is scaled by D/Dmm and rotated by rx, ry, rz (about x, then y, then z) about the STL
  origin. So the STL must be centred on its origin; the log prints its bounding-box centre.
  - A host occupancy grid with `ref=4` voxels per cell is built once.
  - A spinning STL is re-voxelized every `revox` steps. The default is floor(0.1/(S u)), so the wall moves at most
    0.1 cell between updates: every 4 steps at S 0.5, 2 at S 1.0 and 1 at S 1.5.
  - `svol` only feeds the volume check in the log.
- `body=pollen`: an analytic POLLEN built from the CAD dimensions, not from the STL. Outer sphere R = D/2 (CAD
  35.56 mm), inner sphere 33.782 mm, and 26 radial cylindrical holes of radius 5.588 mm (0.220 in). The hole axes are
  fixed in the CAD frame: one on each pole (CAD +y and -y), and a ring of 4 and a ring of 8 on each side. No chamfers
  or fillets. Exact material volume 22,299.17 mm^3 (derived; the STL gives 22,312.36). `rx`, `ry`, `rz` turn it as
  for `body=stl`.
  - With `wall=ibb` the wall distance q of every wall link is computed on the GPU from the exact shape after every
    geometry update (every `revox` steps when spinning). A root within 1e-5 of a link end counts, with q clamped into
    (0, 1]; tangent double roots are skipped. The force of a step is taken before that step's geometry update
    (commit fc22cd5).
  - Below D 64 the solver warns that `wall=ibb` POLLEN leaks: the shell is under sqrt(2) cells thick.
  - The CSV header records `wall=` and a `# pollen R_cells=...` line with the CAD sizes.
  - Without `holes=`, the hole and cavity diagnostics use the built-in POLLEN hole axes.
- `body=rotpollen`: the same POLLEN spinning in still fluid (the `rotstokes` setup).
- `pball=1` (with `body=pollen` or `rotpollen`): a debug check. It builds a solid ball through the POLLEN code path,
  with no holes and no cavity, and must match `body=sphere`.

**Field dump** (`dump=`; off by default, and the CSV does not change):
- `dump=t1,t2,...`: the t* values at which the velocity field is written. It needs a body.
- `dumpstride=` (default 2): keep every n-th finest-level cell in each direction.
- `dumpbox=x0,x1,y0,y1,z0,z1`: the box in D from the body centre, clipped to the finest level. The default is the
  whole finest level.
- Output next to the CSV: `<out base>_f<t*>.bin` (float32 ux, uy, uz as u/U, then a uint8 solid mask) with a `.json`
  sidecar (t*, grid size, dx and origin in D, flow direction, lattice U, Re, S, spin axis, D, the run arguments). At
  the first dump the solver also writes a fine solid mask, `<out base>_solid_fine.bin` and `.json` (stride 1, box
  +-0.6 D).
- `viz/flow/make_flow.py` turns the dumps into the flow viewer's data (`viz/flow/README.md`). The viewer data came
  from short separate runs to t* 22 with dumps at t* 20, 21 and 22, not from the result runs.

**Coefficients:** q = 0.5 u^2 pi R^2 with R = D/2 in cells. Cd = Fx/q, Cy = Fy/q, Cl = Fz/q, CM = -Ty/(q R).

**Numerical regime** (derived):
- nu = u D/Re. At D 94 and Re 33057, tau = 0.50043, so the run is stable only with the LES.
- The laminar boundary layer is about D/sqrt(Re) = 0.0055 D: about 0.5 cell at D 94, 0.70 at D 128 and 1.06 at
  D 192. **The wall layer is not resolved.** This is an under-resolved LES (with staircase walls under
  `wall=hbb`), so separation and transition are not reliable. That is why the smooth-sphere gates set the band.

**Builds** (outside the repo, in `%PM012_CFD_ROOT%\pm012_lbm\bin`):

| Build | Source | Runs |
|---|---|---|
| before 10:07, no `favg` (instantaneous samples) | not committed | rotstokes_test, re100_d24_big, re100_d32, v1_d48 |
| 10:14, `pm012_lbm_1014.exe` | committed 4 minutes later in 28f95b1 (not re-checked against the binary) | v1_d48_favg, v1d_box8, v1d_cs17, v1d_bgk, v1d_fp32, v1_bgk_d64 |
| 10:32, `pm012_lbm.exe` | ca68597: even row length, diagnosis knobs (off by default) | v1_reg_d64, v1_bgk_d80, v1_bgk_d94 and every later `wall=hbb` run |
| 2026-10-31 17:07 | 34ad763: `wall=ibb` for the analytic sphere and `rotstokes` | the first smooth-sphere `*_ibb_*` runs; CSV headers from this build do not record `wall=` |
| 2026-10-31 19:20-19:32 | fe50df2: `body=pollen` with exact q; fc22cd5: robust q roots, force before the geometry update | the `p_ibb_*` POLLEN runs (this build or a later one; the later commits do not change the CSV) |
| 2026-11-01 15:47 | 5e8dd38: `dump=` (off by default); queue scripts added in 2dd78dd; both merged in b686e2d on 2026-11-02 | the flow-viewer dump runs |

## Local grid refinement (`lv=`)

Everything away from the ball is still room-temperature air in uniform flow, so the solver now puts fine cells only
around the ball. Own code in `cfd/lbm/`, following the published method of Rohde et al. (2006).
`lv=1` (the default) is the old uniform grid.

**Method.**
- Nested boxes, refinement factor 2 per level, cell-centred (a coarse cell holds 2x2x2 fine cells). `D` is the
  finest level's cells per diameter; level l has D / 2^(L-1-l).
- Acoustic scaling: the same lattice u on every level, nu_l = u D_l / Re, so tau differs per level. The Smagorinsky
  model runs on each level with its own tau.
- Sub-cycling: a level takes two steps per parent step (recursive: child step, coalescence, child step, own step).
- Coupling: the volumetric, mass-conserving scheme of Rohde et al. (2006). Populations that a fine interface cell
  pulls from outside its box come from the parent cell they lie in (uniform explosion); after its first sub-step the
  fine level is summed back into the covered parent cells (coalescence). No non-equilibrium rescaling.
- The body, the moving-wall term, the STL re-voxelisation of a spinning ball and the momentum-exchange force all live
  on the finest level only. The finest box must hold the whole shell and the hollow inside, with room to spare.
- Box size: `fb` (finest box) and `gb` (added per coarser refined level) are **half widths measured from the body
  centre**, upstream / downstream / lateral. The gap between the ball's surface and the next coarser level is
  therefore fb - 0.5 D. Default since the 2026-10-31 review: fb 1.5 / 2.5 / 1.5 D (gap 1.0 / 2.0 / 1.0 D) and
  gb 0.25 / 1.0 / 0.25 D. The first default, fb 0.7 / 1.5 / 0.7 D, left a gap of only 0.2 / 1.0 / 0.2 D and biased
  Cd, Cl and CM; fb 1.2 sideways (gap 0.7 D) still raised the S 0 Cd by 5-9 % (section "Finest-box bias" below).
  `plan=1` prints the gaps.

**Options.** `lv=1` (uniform, the old behaviour) to 4; `fb=up,down,side` finest box; `gb=up,down,side` growth per
coarser level; `plan=1` prints per-level cells and memory, cells across a hole and across the wall, the gaps and
`need_mib=` for a queue, then exits without the GPU; `body=none` (uniform-flow check) and `body=masstest` (closed box,
total mass) are checks. The production grid is `lv=3 D=128` in the 6x4x4 D box with the default `fb` and `gb`; it
needs 7077 MiB in FP16 (derived, solver plan):

| Level | D | Cells | Box (D) | Memory (FP16) |
|---|---|---|---|---|
| L0 | 32 | 192x128x128 = 3.15 M | 6.00 x 4.00 x 4.00 (domain) | 231 MiB |
| L1 | 64 | 336x224x224 = 16.9 M | 5.25 x 3.50 x 3.50 | 1238 MiB |
| L2 | 128 | 512x384x384 = 75.5 M | 4.00 x 3.00 x 3.00 | 5544 MiB |

The finest D 128 gives 18.4-20.2 cells across a hole and 3.2 across the wall (derived; D 94 uniform gave 13-15 and
2.35). With the default box, `lv=3` needs 941 MiB at D 64, 3023 at D 96, 7077 at D 128, 10049 at D 144, 13761 at
D 160 and 23733 at D 192 (more than a 16 GB card holds; the D 192 runs used a 40 GB A100). D 128 is also the finest D at which the uniform reference for the box A/B still
fits: 8553 MiB in a reduced 4.5 x 3.5 x 3.5 D domain (a uniform D 128 grid in the full box needs 14848 MiB). Cost
(derived): 2.17e11 cell updates per t*, about 7 h for T 150 and 2.6 h for T 55 at 1300 MLUPs (about 11 h and 4 h at
800 MLUPs on the shared card).
Measured T 150 times of the POLLEN runs (derived, run logs): D 128 about 45-50 min on an A100 40 GB, 75-95 min on a
V100 16 GB and 2.9-3.8 h on the RTX 3060; D 192 about 3.5-3.7 h on an A100 40 GB.

**Hole and cavity diagnostics** (`holes=<file from stl_holes.py>`, sphere or STL). New `# dg ...` lines after every
CSV row and a `# dg_avg ...` footer (t* >= 15); the existing keys are unchanged.
- Through-hole flow: for each of the 26 holes, the mass flux through a disc at mid-wall, normal to the hole axis,
  radius = hole radius (`hole_mm=11.2`, `wall_mm=1.778`), axes rotated by the current spin angle. Positive = out of
  the cavity; normalised by rho u pi r_h^2. Keys: `dg_hole_net_out`, `dg_hole_abs` (sum of |flux|), `dg_hole_top3`,
  `dg_avg_hole_mean` (26 values).
- Cavity (fluid cells with r < R_inner - 1 cell): `dg_cav_umean` (mean |u|/U), `dg_cav_vortD` (mean |curl u| D/U),
  `dg_cav_Lratio` (air angular momentum about the spin axis / solid-body value, rho omega r_perp^2 summed over the
  same cells).
- Force split over the wall links, by the fluid cell p of each link (cells; a fluid cell is never inside the wall):
  hole walls = R_inner - 1 < |p| < R + 1 and within r_hole + 1 cell of a hole axis (axes at the current spin angle);
  the other links are outer surface (|p| >= mid-wall radius) or inner surface. Keys `dg_Cd_out`, `dg_Cy_out`,
  `dg_Cl_out`, `dg_CM_out`, then `_in` and `_hole`; the three parts add up to the total. A smooth sphere has no hole
  walls. A split by link radius alone (outer r >= R - 1.5, inner r <= R_inner + 1.5) was tried first and left the
  hole walls empty: the wall is only 2.4 cells thick at D 96, so the two bands overlap. The hole-wall part includes a
  rim of about 1 cell on the outer and inner surface around each hole.

**Checks of the refinement** (PREDICTED: own solver output; RTX 3060 shared with other runs):

| Check | Result | Target |
|---|---|---|
| Total mass, closed box, lv 2 D 32 and lv 3 D 64, FP32 | relative change 2.2e-9 and -1.5e-9 (largest 3.5e-9) | round-off |
| Uniform flow, no body, lv 3 D 64, BGK (max \|u - u_in\| in lattice units, then as a fraction of u_in = 0.05) | FP16 noise: 4.5e-4 = 0.9 % of u_in, the same as the uniform grid (4.6-5.2e-4 = 0.9-1.0 %); FP32, no noise: 9.2e-6 = 1.8e-4 of u_in, and \|rho - 1\| 1.5e-6, at t* 12 on every level | no growth at the interfaces |
| Uniform flow, no body, regularized collision, Re 3e4 (max \|u - u_in\|, lattice units; u_in 0.05 unless noted) | lv 3 FP32 grows: 8.6e-4 = 1.7 % of u_in (t* 3), 3.3e-2 = 0.66 u_in (t* 6), 3.9e-2 = 0.78 u_in (t* 12), first at the upstream face of the finest box. The **uniform** grid does the same (D 16: 3.9e-3 = 7.8 % at t* 12, 3.95e-2 = 0.79 u_in at t* 24; D 32: 3.9e-2 = 0.78 u_in at t* 12; also with Cs 0); stable at u_in 0.02 (6.4e-7 = 3.2e-5 of u_in) and at Re 3000 (7.6e-6 = 1.5e-4 of u_in) | **fails**; see below |
| Old uniform runs (`lv=1`) with the new code | 192 CSV rows: forces and Cd, Cy, Cl bit-identical; torques differ by at most 1.2e-7 (lattice units; summation order of the force split) | same as before |
| V0 rotating sphere, Stokes torque, lv 2 D 32 FP32 | 1.0286 x analytic; uniform grid 1.0264 (+0.2 %) | 0.97-1.10 |
| Sphere Re 100, lv 2 D 32 FP32 | Cd 1.2013; uniform grid 1.1890 (+1.0 %) | within a few % of the uniform grid |
| Diagnostics unit check: closed smooth sphere, S 0.5, lv 2 D 32, `holes=` given | hole flux 0, cavity 0 cells, inner and hole-wall force 0, outer part = total (Cd 0.654) | exactly that |
| Diagnostics, spinning POLLEN STL (hole facing the flow), S 0.5, lv 2 D 96, t* 3 (smoke test) | STL volume ratio 1.0005, odd rays 0; 371,848 cavity cells; hole fluxes non-zero; at t* 3 Cd split outer / inner / hole walls 0.567 / 0.067 / 0.065, sum = total to 1e-6 | runs; not a result |
| **V1** (superseded: box-biased) smooth sphere Re 33057, S 0, lv 3 D 96, BGK FP16, box 6x4x4, **old finest box** fb 0.7 / 1.5 / 0.7, T 55, mean t* 15-55 | Cd 0.553 (se 0.004, half-window drift -0.011); Cl -0.004, Cy -0.023 | Binding V1 (section "Acceptance"): box-corrected Cd 0.540 (x 0.976), +19 % against 0.453, outside 0.43-0.50, and T 55 < 150: **fail**. (The "30 %" band first used here is withdrawn.) Uniform BGK D 80 same box: Cd 0.539, Cl 0.104. **Box-biased** (section "Finest-box bias"): superseded until the rerun with the new box |
| **V2** (superseded: box-biased) smooth sphere Re 33057, S 0.5, same grid and old box | Cl 0.220 (se 0.007, drift +0.012), Cd 0.510, CM -0.014 (not usable, see the last column); S 0 twin above: Cl -0.004, Cd 0.553 | Binding V2: Cl 0.2197 is just below 0.22, and T 55 < 150: **fail**. Twin lateral L 0.024, u_win(Cl) + L 0.034 <= 0.055. CM < 0 means the air would spin the ball up, which is unphysical; the spin-decay formula would turn it into a negative k. The sign comes from the old box (section "Finest-box bias"). **Box-biased**: superseded until the rerun with the new box |

All numbers in this table are PREDICTED (own solver; smooth sphere: validation only, not POLLEN). V1 was rerun at
lv 3 D 128 with the new box and T 150 after the D 128 box A/B runs: with `wall=hbb` it fails, with `wall=ibb` it
passes. V2 with `wall=ibb` fails there (section "Validation results"). D 192 at lv 3 needs 23.2 GiB, so it ran only
on a 40 GB cloud GPU.

**Collision: BGK for production.** The regularized collision (`coll=reg`) is unstable in plain uniform flow at
tau close to 0.5 with u 0.05 (table above), on the uniform grid as well as the refined one, with or without the
Smagorinsky term. That fits its high sphere Cd (0.67-0.70 against 0.54-0.56 for BGK). All refined and production runs
use `coll=bgk`.

**POLLEN production runs.** The plan of 2026-10-31 held every POLLEN case until the D 128 box A/B, V1 and V2 passed
at lv 3 D 128. The box A/B passed and V1 passed with `wall=ibb`, but V2 did not. The POLLEN runs were made anyway, in
the V1 configuration (lv 3 D 128, BGK, FP16, Cs 0.1, default `fb` and `gb`, `wall=ibb`, T 150), as PREDICTED solver
output; nothing from them is released. They differ from the held plan: the analytic `body=pollen` instead of the
STL; three set orientations instead of two plus 8 random ones; S 0 to 1.5; Re 20000, 33057 and 47224; T 150 instead
of T 55. The smooth-sphere reference is the V1 and V2 pair on the same grid. Section "POLLEN results" lists them.

### Finest-box bias (PREDICTED)

The body force lives on the finest level only, but the flow next to the ball still feels where the coarse level
starts. The review compared the refined grid with the uniform grid at the same finest D and found that the first
default box (fb 0.7 / 1.5 / 0.7, gap 0.2 D upstream and sideways) biased all three coefficients: at D 32, lv 2,
S 0.5, t* 15-40, uniform / old box / wide box (fb 1.5 / 3.5 / 1.5, a 5 x 3 x 3 D finest box; not the adopted
1.5 / 2.5 / 1.5) gave Cd 0.601 / 0.613 / 0.604 (PREDICTED), Cl 0.284 / 0.176 / 0.278 and CM +0.0013 / -0.0173 /
+0.0008. The same three at S 0 gave Cd 0.5685 / 0.7132 / 0.5701 (PREDICTED), so the +25 % old-box Cd bias is an S 0
result (+2 % at S 0.5, inside the Cd window uncertainty); at S 0.5 the old box shows in Cl and CM. The V1 and V2 rows
above used that box, and the V2 CM of -0.014 (CM < 0, unphysical) is the same effect. The review re-derived the moving-wall term, the torque Ty and the CM formula and found them correct.

Box A/B: refined minus uniform at the same finest D, same 6x4x4 D domain and settings (BGK, FP16, Re 33057), T 40,
window t* 15-40, judged with `postprocess.py match` (both windows stationary and |difference| <= max(t95
sqrt(se_a^2 + se_b^2), floor)). Uniform references: D 64 runs of T 55 (S 0) and T 40 (S 0.5), D 48 runs of T 150,
all read over t* 15-40.

| Finest D, levels | fb up / down / side (gap to the surface, D) | S | dCd (tol) | dCl (tol) | dCM (tol) | Match |
|---|---|---|---|---|---|---|
| 64, lv 3 | 1.2 / 2.5 / 1.2 (0.7 / 2.0 / 0.7) | 0 | +0.028 (0.014) | +0.082 (0.090) | -0.0011 (0.0026) | **no**: Cd |
| 64, lv 3 | 1.2 / 2.5 / 1.2 | 0.5 | +0.007 (0.013) | +0.001 (0.026) | -0.0003 (0.0015) | **no**: refined Cd window not stationary |
| 64, lv 3 | 1.5 / 2.5 / 1.5 (1.0 / 2.0 / 1.0) | 0 | +0.007 (0.015) | +0.014 (0.113) | 0.0000 (0.0015) | yes |
| 64, lv 3 | 1.5 / 2.5 / 1.5 | 0.5 | +0.004 (0.012) | -0.005 (0.030) | -0.0006 (0.0018) | yes |
| 48, lv 2 | 1.2 / 2.5 / 1.2 | 0 | +0.034 (0.020) | +0.106 (0.055) | -0.0014 (0.0013) | **no**: all three |
| 48, lv 2 | 1.2 / 2.5 / 1.2 | 0.5 | +0.003 (0.026) | -0.037 (0.033) | +0.0004 (0.0025) | **no**: Cl |
| 48, lv 2 | 1.2 / 3.5 / 1.2 | 0 | +0.050 (0.026) | +0.158 (0.045) | -0.0032 (0.0013) | **no**: all three |
| 48, lv 2 | 1.5 / 2.5 / 1.5 | 0 | -0.0003 (0.017) | +0.165 (0.068) | -0.0039 (0.0016) | **no**: Cl and CM |
| 48, lv 2 | 1.5 / 2.5 / 1.5 | 0.5 | +0.012 (0.023) | -0.006 (0.030) | -0.0005 (0.0022) | yes |
| 48, lv 2 | 1.5 / 3.5 / 1.5 | 0 | -0.002 (0.029) | +0.0001 (0.064) | -0.0006 (0.0021) | yes |
| 48, lv 2 | 1.5 / 3.5 / 1.5 | 0.5 | +0.008 (0.021) | +0.007 (0.032) | +0.0001 (0.0021) | yes |

Reading (PREDICTED, derived from the table):
- The sideways gap sets the drag: with 0.7 D the S 0 Cd is 5-9 % high at both D, and a longer wake box does not help
  (1.2 / 3.5 / 1.2 is worse). A gap of 1.0 D matches Cd in every pair.
- At S 0 the lateral force and the torque of a smooth sphere average to zero; over 25 t* they follow the wake's slow
  side-to-side swing, so they are the most sensitive part of the test. At D 48 (lv 2: the coarse level behind the box
  is D 24) the 2.5 D box missed Cl and CM at S 0 over t* 15-40, but two uniform runs that differ only in the start
  noise miss each other by more, and the refined run matches the seed-104729 run in all three (table below). At D 64
  (lv 3) the 2.5 D box matched all three at S 0 and S 0.5.
- New default: fb 1.5 / 2.5 / 1.5, gb 0.25 / 1.0 / 0.25. A 3.5 D wake box is not used: at D 128 its uniform A/B
  reference needs 10440 MiB even in the smallest domain that holds it, which is the whole card, and lv 3 with it
  needs 8522 MiB.

Start noise and a longer window, D 48, lv 2, fb 1.5 / 2.5 / 1.5, runs of T 150 (the uniform S 0 reference also with a
second start-noise seed: g48_v1_S0_T150_seed104729). Difference = first named minus second named:

| Pair, D 48 | S | Window t* | dCd (tol) | dCl (tol) | dCM (tol) | Match |
|---|---|---|---|---|---|---|
| uniform seed 104729 - uniform seed 0 | 0 | 15-40 | +0.001 (0.024) | +0.202 (0.053) | -0.0044 (0.0013) | **no**: Cl and CM |
| refined - uniform seed 104729 | 0 | 15-40 | -0.001 (0.020) | -0.038 (0.061) | +0.0005 (0.0012) | yes |
| refined - uniform seed 0 | 0 | 15-150 | -0.005 (0.010) | +0.035 (0.255) | -0.0007 (0.0037) | **no**: uniform Cl window not stationary |
| refined - uniform seed 104729 | 0 | 15-150 | -0.0015 (0.010) | -0.048 (0.125) | +0.0009 (0.0021) | **no**: uniform CM window not stationary |
| uniform seed 104729 - uniform seed 0 | 0 | 15-150 | -0.003 (0.010) | +0.083 (0.262) | -0.0016 (0.0034) | **no**: windows not stationary |
| refined - uniform | 0.5 | 15-150 | -0.004 (0.010) | -0.002 (0.010) | +0.0001 (0.0010) | **no**: uniform windows not stationary |

Over t* 15-150 every refined-minus-uniform difference is inside its tolerance at S 0 and S 0.5; the rule says no only
because some uniform windows fail the trend test (the refined windows pass it). Over 25 t* at S 0 (D 48) the uniform grid
does not match itself in Cl and CM, so a single-seed S 0 pair cannot show a box bias in Cl or CM.

**Binding check at the production finest D (rule set before any D 128 result; result below).** The same A/B at finest
D 128, refined lv 2 against uniform, in a reduced 4.5 x 3.5 x 3.5 D domain (centre 1.75 D from the inlet; uniform
8553 MiB, refined 6669 MiB), at S 0.5 and S 0, T 40, window t* 15-40. Cd at S 0 and Cd, Cl and CM at S 0.5 must match
by the rule. At S 0, Cl and CM pass if they match, or if |refined - uniform| is no larger than the difference between
two uniform runs that differ only in the start noise (seed 0 and seed 104729, both queued). V1 and V2 at lv 3 D 128
(T 150) are queued behind it and count only if both pairs pass. If a pair fails on a difference, the box is widened and
the production plan is redone; if it fails only because a window is not stationary, it does not pass, and that pair is
rerun longer (T 150) before the box is changed.

This check tests the finest-box edge (fb 1.5 / 2.5 / 1.5), not the second lv 3 interface.

*Pinned 2026-10-31, before any D 128 result CSV existed (ab_*128* runs not yet started).* S 0 comparison at D 128 (PREDICTED
when run): the uniform run is ab_u128_S0_dom4.5 (seed 0). The seed spread is |ab_u128_S0_dom4.5_seed104729 -
ab_u128_S0_dom4.5| per coefficient (Cd, Cl, CM), each a mean over t* 15-40. The seed-spread route needs stationary windows:
both uniform windows must pass the stationarity (trend) test, otherwise the S 0 pair is "not decided", not "pass".

*Result (`wall=hbb`, T 40, window t* 15-40; PREDICTED).* Both D 128 pairs match by the rule, so the box
fb 1.5 / 2.5 / 1.5 stays for the production grid. The A/B was not repeated with `wall=ibb`.

| Pair, finest D 128, domain 4.5 x 3.5 x 3.5 D | S | dCd (tol) | dCl (tol) | dCM (tol) | Match |
|---|---|---|---|---|---|
| refined lv 2 - uniform | 0.5 | -0.0014 (0.0145) | +0.0058 (0.049) | +0.00006 (0.001) | yes |
| refined lv 2 - uniform | 0 | -0.0027 (0.0103) | -0.0077 (0.051) | +0.0002 (0.001) | yes |

## Averaging and uncertainty (`postprocess.py`)

Each coefficient is averaged over the window from t* 15 to the end of the run:
1. The rows are averaged into 0.1 t* bins.
2. Integral time T_int is the larger of two estimates:
   - the autocorrelation summed up to its first zero crossing;
   - batch-means estimates with 5, 10 and 20 t* batches, each used only when it has at least 4 batches.
3. Batches are max(2 T_int, 5 t*) long. Fewer than 4 batches means the window is not stationary.
4. **u_win**, the standard deviation of the batch means, is the window-to-window spread. It is the uncertainty quoted
   with every CFD number. The 95 % interval of the whole-window mean (t95 u_win / sqrt(nb)) is printed for information
   only.
5. **Trend** is the least-squares slope over the whole window times the window length. Its standard error comes from
   a regression of the batch means.
6. **Stationary** means at least 4 batches, and not (trend significant at 95 % and |trend| above the tolerance).
   Tolerances (ASSUMED): Cd, Cy and Cl 0.02; CM 0.002.

- Gate runs are at least T 150, a 135 t* window. The start noise can be varied with `seed=` (Method). Only the S 0
  twin has a second seed; the seed-to-seed spread of every other number is not known. No POLLEN run was repeated.
- **Known bias.** Both T_int estimators run low for slow signals in a finite window. For AR(1) noise with T_int 10 t*
  in a 135 t* window, the median estimate is about 6 t* (synthetic test, PREDICTED). This makes the rule stricter, not
  looser:
  - shorter batches give a larger u_win;
  - correlated batch means give a smaller trend standard error, so more trends count as significant.
- `postprocess.py --selftest` checks these rules on synthetic series.

## Lateral force of the no-spin twin

A smooth sphere without spin should have a mean lateral force of zero. Our S 0 runs show |(<Cl>, <Cy>)| of 0.02-0.13
over t* 15-55 (PREDICTED; BGK: 0.130 at D 48, 0.080 at D 64, 0.120 at D 80). So:
- L_twin = |(<Cl>, <Cy>)| of the S 0 twin over the same window as the spinning run. `postprocess.py` also prints it
  for each 5 t* block.
- L_twin is a +- term on V2 (the gate condition above) and on every POLLEN Cl.
- Two noise seeds of the D 48, T 150 twin, t* 15-150 (PREDICTED): L 0.0285 (seed 0) and 0.0546 (seed 104729);
  Cl -0.028 (window not stationary) and +0.055 (window stationary). L_twin for V2 is the larger, 0.0546. One pair of
  seeds is not a seed-to-seed spread.
- A single-window twin Cl is never subtracted from a spinning Cl.
- Every backspin result is shown next to its S 0 twin.

## Validation results (PREDICTED; verdicts under the binding rule)

At Re 33057, POLLEN flies at 7 m/s (derived). Unless noted: box 6 x 4 x 4 D, FP16, Cs 0.1, T 55 (window t* 15-55),
so only the rows marked T 150 are gate length. "vs 0.453" is the box-corrected Cd against Brown & Lawler.

| Run | Setting | Cd +- u_win | Trend (stationary?) | Box-corrected Cd | vs 0.453 | L (this S 0 run) | V1 |
|---|---|---|---|---|---|---|---|
| v1_d48 | D 48, regularized, favg 0 | 0.699 +- 0.010 | +0.003 (yes) | 0.682 | +51 % | 0.032 | fail |
| v1_d48_favg | D 48, regularized | 0.698 +- 0.012 | +0.002 (yes) | 0.682 | +50 % | 0.032 | fail |
| v1d_box8 | D 48, regularized, box 8 x 6 x 6 | 0.682 +- 0.006 | -0.016 (yes) | gives the box factor 0.976 | +50 % (raw) | 0.033 | fail |
| v1d_cs17 | D 48, regularized, Cs 0.17 | 0.621 +- 0.004 | -0.011 (yes; Cl not) | 0.606 | +34 % | 0.036 | fail |
| v1d_fp32 | D 48, regularized, FP32 | 0.706 +- 0.015 | -0.042 (no) | 0.689 | +52 % | 0.018 | fail |
| v1d_bgk | D 48, BGK | 0.563 +- 0.007 | -0.004 (yes) | 0.549 | +21 % | 0.130 | fail |
| v1_reg_d64 | D 64, regularized | 0.680 +- 0.009 | +0.016 (yes) | 0.664 | +47 % | 0.050 | fail |
| v1_bgk_d64 | D 64, BGK | 0.533 +- 0.015 | +0.043 (no: 3 batches) | 0.521 | +15 % | 0.080 | fail |
| v1_bgk_d80 | D 80, BGK | 0.539 +- 0.012 | +0.025 (yes: not significant) | 0.526 | +16 % | 0.120 | fail |
| v1_bgk_d94 | D 94, BGK | 0.509 +- 0.010 | +0.002 (yes) | 0.497 | +10 % | 0.071 | fail: in band, but T 55 < 150 |
| g48_v1_S0_T150 | D 48, BGK, **T 150** (window t* 15-150) | 0.559 +- 0.010 | -0.006 (yes; Cl not) | 0.545 | +20 % | 0.028 | fail |
| g48_v1_S0_T150_seed104729 | the same, noise seed 104729 | 0.556 +- 0.012 | -0.013 (yes) | 0.542 | +20 % | 0.055 | fail |
| v1_bgk_d94_T150 | D 94, BGK, **T 150** | 0.519 | +0.021 (no) | 0.507 +- 0.014 | +12 % | 0.057 | fail: not stationary, above the band |
| v1_ref_d128 | lv 3, finest D 128, BGK, `wall=hbb`, **T 150** | 0.516 | +0.011 (yes) | 0.504 +- 0.011 | +11 % | 0.015 | fail: above the band |
| v1_ibb_d128 | lv 3, finest D 128, BGK, **`wall=ibb`**, **T 150** | 0.453 | +0.006 (yes; 16 batches) | 0.4425 +- 0.012 | -2.3 % | 0.042 | **pass** |

- Box factor 0.976 = Cd(8 x 6 x 6) / Cd(6 x 4 x 4) for the regularized D 48 pair (PREDICTED). Using it for BGK and
  for finer grids is ASSUMED. The pre-registered box study (8 x 5 x 5 and 10 x 7 x 7) was not run.
- Noise seeds 0 and 104729 at D 48, T 150 give Cd 0.5587 and 0.5556 (PREDICTED). One pair of seeds is not a
  seed-to-seed spread.
- Grid series, BGK (T 55): D 48 0.563, D 64 0.533 (not stationary), D 80 0.539, D 94 0.509. The change between the
  two finest grids (D 80 to D 94) is -0.030 (-5.9 %); from D 48 to D 94 it is -0.054 (-9.6 %). Cd is not grid
  converged.
- The collision model moves Cd more than the grid does: at D 48 and D 64, BGK gives a Cd 0.13-0.15 lower than
  regularized.
- In the last three rows u_win is given with the box-corrected Cd.
- The `wall=ibb` V1 pass uses the ASSUMED box factor 0.976, but the raw Cd 0.4534 is inside the band as well. At lv 3
  D 128 the wall model moves Cd more than any grid change: `wall=ibb` gives a raw Cd 0.063 lower than `wall=hbb`
  (0.453 against 0.516).

Other checks:

| ID | Case | Result (PREDICTED) | Reference | Verdict |
|---|---|---|---|---|
| V0 | sphere spinning in still fluid, Stokes regime (Re_rot 0.4), D 32, FP32, cube of side 4 D | torque 1.026 x Stokes | 0.97-1.10: Stokes torque 8 pi mu R^3 w, raised 1.003-1.016x by the box (derived) | pass (cube-flux check not run) |
| Re 100 | sphere, regularized, T 30: D 24 (box 12 x 10 x 10, FP16) / D 32 (box 8 x 6 x 6, FP32) | Cd 1.171 / 1.189 | 1.073 (Brown & Lawler Eq. 19, derived) | +9 % / +11 %, no gate. Earlier text used 1.087, whose source was not recorded. |
| V2 | sphere at S 0.5, D 48, BGK, T 150 (g48_v2_S0.5_T150); S 0 twins g48_v1_S0_T150 (seed 0) and g48_v1_S0_T150_seed104729 (seed 104729) | Cl 0.252 +- 0.018 (trend +0.027: not stationary), Cd 0.547 +- 0.013 (not stationary). S 0 twins over the same window t* 15-150. Seed 0: Cl -0.028 +- 0.092 (3 batches, trend +0.255: not stationary), Cy -0.003, L 0.0285 (5 t* blocks 0.033-0.214), Cd 0.559. Seed 104729: Cl +0.055 +- 0.059 (4 batches, trend -0.143, not significant at 95 %: stationary), Cy +0.003, L 0.0546 (5 t* blocks 0.035-0.184), Cd 0.556. L_twin 0.0546 (the larger). u_win(Cl) + L_twin 0.073 > 0.055. CM: not usable: torque gate not passed | Cl 0.22-0.33 (pre-registered). Cl about 0.29 at SP 0.55 (Sakai et al. 2016, Fig. 8, Re 3e4 bin, by eye); 0.26 at Re 3.6e4, Sp 0.5 (Conti et al. 2026, unreviewed preprint); Cd about 0.49 near SP 0.5 (Sakai, Fig. 7) | **fail**: Cl is in the band, but the Cl window is not stationary, the twin Cl window is not stationary (seed 0) and u_win(Cl) + L_twin is above 0.055. A spinning run, so a solver diagnostic until the torque gate passes |
| STL path, S 0 | STL sphere vs analytic sphere at S 0, D 48, BGK, T 150 (g48_v1stl_S0_T150 vs g48_v1_S0_T150): tests the STL path without spin | Cd: STL 0.5586 +- 0.0116 (16 batches), analytic 0.5587 +- 0.0103 (26 batches), both stationary; difference -0.0001, tolerance 0.010. Reported, not gated (STL / analytic): CM +0.0037 +- 0.0009 (trend +0.0022: not stationary) / +0.0006 +- 0.0019 (stationary); Cy -0.063 / -0.003; Cl +0.024 (stationary) / -0.028 (not stationary); L 0.067 / 0.028. F_STL = 0.00365 | rule "STL path, S 0" (Cd match; CM, Cy, Cl and L reported). It replaces the 12:55 text "match in Cd and Cl". It was written after the run had finished and after its Cd and CM had appeared in the analysis notes and the review, so it is not blind | **pass** (Cd). Under the 12:55 text it would fail: the analytic Cl window is not stationary. F_STL 0.00365 is 58 % of the torque reference 0.0063 |
| STL path | STL sphere vs analytic sphere, S 0.5, D 48, BGK, T 150 (g48_v2stl_S0.5_T150 vs g48_v2_S0.5_T150) | STL: Cd 0.614 +- 0.010, Cl 0.354 +- 0.017 (both stationary). Analytic: Cd 0.547 +- 0.013, Cl 0.252 +- 0.018 (neither stationary: trend +0.026 / +0.027). Difference: Cd +0.067, Cl +0.101. CM: not usable: torque gate not passed. S 0 twin: see the V2 row | match in Cd, Cl and CM (tolerance 0.01 here) | **fail**: both differences are far above the tolerance, and the analytic run is not stationary. Both runs spin, so this is a solver diagnostic until the torque gate passes |
| revox | POLLEN "between holes", S 1.0, D 64, BGK, T 150, revox 1 vs 2 | not run in this round: every spinning case waits for the torque gate (revox 1 held since 12:10) | match in Cd, Cl and CM | **PENDING (torque gate)** |
| V3 (optional) | spinning sphere, Re 1e4, Gamma 0 / 0.2 / 1.0, D 48, 8 x 5 x 5 | not run | Muto et al. 2012 LES, Table I: Cl 0.167 (s.d. 0.029) at Gamma 0.2, 0.301 (s.d. 0.096) at Gamma 1.0 | none |

Kim et al. 2014 (inverse Magnus, Re 6e4-2.6e5) is above this Re range, so it is context only.

**Deviation from the review (STL path).** The review asked for the STL-sphere check at D 94. It runs at D 48:
- at 11:23 the uniform D 94 runs were put on hold, because local grid refinement (`lv=`) replaces that path;
- one D 94 run of T 150 would take about 4-5 hours on the shared card (PREDICTED from the D 94 T 55 run).

The D 48 pair tests the STL path itself: voxelizer, rotation, re-voxelization and moving wall. A match at the release
grid stays a release condition. The smooth twins of the POLLEN lines (`t_*` in `queue/held.txt`) were set to use
the STL sphere, so they would share the POLLEN voxelization path. Those held lines were not run.

### Gates with `wall=ibb` (PREDICTED; verdicts under the binding rule)

Smooth analytic sphere, Re 33057, lv 3, BGK, FP16, Cs 0.1, u 0.05, default `fb` and `gb`, T 150, window t* 15-150.

| Gate | Run(s) | Result | Verdict |
|---|---|---|---|
| V1, D 128 | v1_ibb_d128 | box-corrected Cd 0.4425 +- 0.0122 (raw 0.4534), 16 batches, trend +0.006 (stationary), L 0.042 | **pass** |
| V2, D 128 | v2_ibb_d128_S0.5, twin v1_ibb_d128 | Cl 0.362 +- 0.021, Cd 0.548; the twin's Cl window is not stationary; u_win(Cl) + L_twin 0.063 > 0.055 | **fail**: Cl above 0.22-0.33, twin not stationary, spread too large |
| V2, D 192 | v2_ibb_d192_S0.5 | Cl 0.270 +- 0.027, Cd 0.526, stationary, in the band | **not decided**: no D 192 S 0 sphere run exists (the twin, and V1 at D 192) |
| Torque | v2_ibb_d128_S0.5, v2_ibb_d192_S0.5 | CM 0.0084 +- 0.0004 (D 128) and 0.0088 +- 0.0005 (D 192), both stationary | **fail**: above 0.0047-0.0079 |

**Spin torque in still fluid** (`body=rotstokes`, wall Reynolds number omega R^2 / nu = 8264, wall speed 0.025,
BGK, FP32, about 4 turns). Ty_lam is a laminar spin-boundary-layer estimate (derived). The criteria were set before
these five runs finished (one earlier D 32 test run gave +3.29): the torque must resist the spin at every D, move
toward Ty_lam as D grows, and land in 0.8-1.2 x Ty_lam at the finest D.

| Finest D, levels | Ty / Ty_lam, `wall=ibb` |
|---|---|
| 32, lv 1 | +3.29 |
| 64, lv 1 | +1.99 |
| 64, lv 2 | +1.99 |
| 128, lv 2 | +1.38 |
| 192, lv 2 | +1.19 |

Positive means the torque resists the spin. `wall=ibb` **passes**, narrowly: 1.19 at D 192 is just inside 0.8-1.2.
With `wall=hbb` the same sweep gives -0.62 (D 64), -0.43 (D 128) and -0.25 (D 192): the wrong sign at every D, as if
the air drove the spin. That is why `wall=ibb` replaced it for the analytic bodies.

## Queue (2026-11-02)

Nothing is queued or running. The cloud GPUs were released on 2026-11-01.
- Parked: POLLEN between holes, D 192, Re 33057, S 1.0, to stay inside the cloud GPU budget. It needs about 23.7 GiB
  at lv 3 (solver plan), so a GPU with more than 16 GB.
- Not run: the revox check for `body=pollen`; a D 192 S 0 smooth-sphere run (V1 at D 192 and the V2 twin there).
- The older `wall=hbb` lines that were waiting (v2_ref_d128_S0.5 and the STL revox check
  g64_p_S1.0_between_revox1_T150) were not run: `wall=ibb` and `body=pollen` replaced that path.

## GPU queue (`cfd/lbm/queue/`)

- `runner.sh front|back [name]`, with `PM012_CFD_ROOT` set, pops the first (`front`) or last (`back`) line of
  `pm012_lbm/queue/todo.txt`. A line is `<case_id> <pm012_lbm.exe args>`; blank lines and `#` lines are skipped. The
  runner adds `out=` and writes `pm012_lbm/runs/<case_id>.csv` and `.log`. It keeps going until it is stopped.
- GPU gate: the runner asks the solver for its memory plan (`plan=1`, which counts every grid level and the field
  dump). If that fails it falls back to int(Lx D) x int(Ly D) x int(Lz D) cells x 77 B (FP16; 153 B for FP32) +
  400 MiB, with a 4 x 4 x 4 D box for `rotstokes`. A case starts only when `nvidia-smi` reports free memory of at
  least that estimate plus 1024 MiB. A case that could never fit (over 92 % of the card, or over the card minus
  1024 MiB) goes straight to `failed.txt` instead of waiting forever.
- The runner keeps the lock until the new process prints its `PM-012 ... N=` line (180 s at most), so a second
  runner sees the memory already taken.
- A case goes to `done.txt` only when it exits with 0 and its CSV has a `# runtime_s=` line; otherwise to
  `failed.txt`. Both lines carry the exit code.
- `add.sh "<id> <args>" ...` appends lines under the same lock (`mkdir queue/.lock`); `add.sh --front` puts them
  first. Lines on hold were kept by hand in `held.txt`, which the scripts do not read.
- `PM012_QUEUE`, `PM012_RUNS` and `PM012_EXE` override the queue folder, the runs folder and the solver path.
- Speed (derived, run logs): one D 48 FP16 case alone ran at 3195 MLUPs on the RTX 3060. When three cases shared
  that card, each ran at about 1270-1510 MLUPs. POLLEN T 150 times per GPU are in "Local grid refinement".

## Inputs

| Quantity | Value | Label and source |
|---|---|---|
| Air | still, dry, 20 C, 101.325 kPa | USER (task) |
| rho | 1.2041 kg/m^3 | derived: p/(R_d T), R_d 287.06 J/(kg K) (CIPM-2007, Picard et al. 2008, *Metrologia* 45:149); `src/air.py` |
| mu | 1.8133e-5 Pa s | derived: Sutherland (U.S. Standard Atmosphere 1976 form, S 110.4 K); `src/air.py`. Textbook value 1.81e-5. |
| nu | 1.506e-5 m^2/s | derived: mu/rho |
| POLLEN outer diameter (CFD) | 71.12 mm (R 35.56 mm) | CONFIRMED: CAD, outer vertex radius of the STL |
| Wall | 1.778 mm | CONFIRMED: CAD, vertex radii 33.782-35.56 mm |
| Holes | 26, 0.40-0.44 in (10.2-11.2 mm) | CONFIRMED: 26 from the STL (genus 25); 0.44 in from the STEP, 0.40 in from the print (`research/params_lit.json` geometry_from_cad, grade C) |
| POLLEN in `body=pollen` | R 35.56 mm, inner R 33.782 mm, 26 holes of radius 5.588 mm (0.220 in); volume 22,299.17 mm^3 | sizes CONFIRMED (CAD); the shape without chamfers or fillets is ASSUMED; volume derived |
| Model R, A | 0.0355 m, A = pi R^2 | CONFIRMED: `src/flight.py` (radius), `src/feasibility.py` (A) |
| Re = v D/nu | 4722 per m/s: 14,170 at 3 m/s, 33,057 at 7 m/s, 51,950 at 11 m/s; Re 20,000 is 4.24 m/s and 47,224 is 10.0 m/s | derived |
| I (spin decay) | 1.98e-5 kg m^2 (1.73e-5 to 2.29e-5) | derived: `data/aero_params.json` I_b |

The CAD is the public AndyMark am-5851 STEP: 175,070 bytes, sha256 `3876dea7...5f445`. It is stored in
`$PM012_CFD_ROOT\dl_am5851_step` and not in git. Its exact download URL was not recorded; the product page is
andymark.com/products/biobuzz-scoring-elements.

`step_to_stl.py` (gmsh, MeshSizeMax 1.2 mm) produced `$PM012_CFD_ROOT\pollen_stl\pollen_mm.stl` (3.2 MB, not in git).
The mesh check gives:
- 64,098 triangles;
- watertight and consistently oriented;
- genus 25 (26 through-holes);
- enclosed material volume 22,312.36 mm^3;
- polar holes on CAD +y, which is also the default spin axis;
- bounding-box centre at the origin (solver log).

`lbm/sphere_stl.py` writes the STL sphere: an icosphere of 71.12 mm, level 5, 20,480 triangles, centred on the
origin, volume 188,251.71 mm^3 (0.99946 of the exact sphere; derived).

## Resolution and GPU memory (derived)

The queue estimate is 77 B per cell for FP16 (two lattices of 19 values, plus flags; FP32 153 B), plus
400 MiB. It is for the uniform grid; for `lv` 2 or more, `plan=1` gives the memory.

| D (cells) | dx (mm) | Wall (cells) | Hole (cells) | Cells, box 6 x 4 x 4 D | Estimate | Use |
|---|---|---|---|---|---|---|
| 48 | 1.482 | 1.20, **leaks** | 6.9-7.5 | 10.6 M | 1179 MiB | sphere gates, STL-sphere check |
| 64 | 1.111 | 1.60 | 9.1-10.1 | 25.2 M | 2248 MiB | grid series, revox check |
| 80 | 0.889 | 2.0 | 11.4-12.6 | 49.2 M | 4009 MiB | grid series |
| 94 | 0.757 | 2.35 | 13.4-14.8 | 79.7 M | 6255 MiB | grid series |
| 128 | 0.556 | 3.2 | 18.4-20.2 | finest level of lv 3 | 7077 MiB (`plan=1`, lv 3) | POLLEN production grid |
| 192 | 0.370 | 4.8 | 27.5-30.2 | finest level of lv 3 | 23733 MiB (`plan=1`, lv 3) | grid check (D 128 against D 192) |

**Leak criterion** (flat wall, cell-centre voxelization). A fluid-fluid D3Q19 link, at most sqrt(2) dx long, can cross
a wall of thickness t only if sqrt(2) dx > t. With t = 1.778 mm:

| D | sqrt(2) dx | Result |
|---|---|---|
| 57 or more | 1.765 mm or less | no tunnelling |
| 64 | 1.572 mm | no tunnelling |
| 94 | 1.070 mm | no tunnelling |
| 128 | 0.786 mm | no tunnelling |
| 192 | 0.524 mm | no tunnelling |
| 48 | 2.10 mm | leaks: no POLLEN runs at D 48 |

In the 6 x 4 x 4 box the solid blockage is 4.9 %. With `wall=ibb` and `body=pollen` the solver prints a leak warning
below D 64.

## Converting to the model's convention

The model uses A = pi R^2 with R = 0.0355 m, S = |w|R/|v| and w(t) = w0 exp(-k t). The CFD uses the CAD R_cfd of
35.56 mm. `postprocess.py` converts every `body=stl` run (derived formulas):
- **Drag and lift:** Cd_model = Cd_cfd (R_cfd/R)^2 = 1.0034 Cd_cfd. Cl converts the same way.
- **Spin ratio:** S_model = 0.9983 S_cfd.
- **Spin decay:** k = T/(I w) = CM 0.5 rho v pi R_cfd^4 / (I S). At 7 m/s that is about 1.07 CM/S per second.
  A physical result has CM > 0 (the air slows the spin, k > 0). CM < 0 would mean the air spins the ball up, which
  cannot happen for a ball flying through still air; such a run must be treated as a numerical problem and its CM not
  converted to k (the formula would give a negative k; `postprocess.py` does not check the sign). CM and k: not usable
  until the torque gate passes; then the band is X +- (e_M |X| + u_win), never narrower than F_STL for CM and
  F_STL x kf for k, where kf = 0.5 rho v pi R_cfd^4 / (I S).

`body=pollen` has the same R_cfd, so the same factors apply, but `postprocess.py` does not convert it. The values in
"POLLEN results" and `viz/explorer/cfd_runs.json` are unconverted CFD values.

## Rerun (Git Bash, from the repo root, with PM012_CFD_ROOT set to a folder outside the repo)

Build the solver from a Windows prompt with `cfd\lbm\build.cmd` (MSVC x64; output in
`%PM012_CFD_ROOT%\pm012_lbm\bin`). Run `pm012_lbm.exe` with no arguments for the key=value list. Smooth-sphere
checks with `wall=hbb` at D 48:

```bash
python -I cfd/lbm/sphere_stl.py $PM012_CFD_ROOT/sphere_stl/sphere_71p12.stl   # prints the volume for svol=
R=$PM012_CFD_ROOT/pm012_lbm/runs
$PM012_CFD_ROOT/pm012_lbm/bin/pm012_lbm.exe body=sphere D=48 Re=33057 S=0.5 T=150 coll=bgk out=$R/g48_v2_S0.5_T150.csv
python -I cfd/postprocess.py summary $R/g48_v2_S0.5_T150.csv
python -I cfd/postprocess.py v1 $R/g48_v1_S0_T150.csv --box 0.976
$PM012_CFD_ROOT/pm012_lbm/bin/pm012_lbm.exe body=sphere D=48 Re=33057 S=0 T=150 coll=bgk seed=104729 out=$R/g48_v1_S0_T150_seed104729.csv
python -I cfd/postprocess.py v2 $R/g48_v2_S0.5_T150.csv $R/g48_v1_S0_T150.csv $R/g48_v1_S0_T150_seed104729.csv
python -I cfd/postprocess.py match $R/g48_v2stl_S0.5_T150.csv $R/g48_v2_S0.5_T150.csv
python -I cfd/postprocess.py stl0 $R/g48_v1stl_S0_T150.csv $R/g48_v1_S0_T150.csv
python -I cfd/postprocess.py torque $R/g48_v2_S0.5_T150.csv    # a diagnostic: D 48 is not the release grid
python -I cfd/postprocess.py --selftest
```

POLLEN with `wall=ibb`, as in the published runs: one backspin case and its no-spin twin. The solver writes its
settings into the CSV header, for the first case `body=pollen stl= D=128 Re=20000 u=0.05 S=0.75 ... revox=2 rx=0
ry=135.114 rz=-138.843 ... prec=fp16 coll=bgk Cs=0.1 ... outlet=p pert=0.001 Lx=6 Ly=4 Lz=4 xc=2 lv=3
fb=1.5,2.5,1.5 gb=0.25,1,0.25 wall=ibb device=...`.

```bash
R=$PM012_CFD_ROOT/pm012_lbm/runs
X=$PM012_CFD_ROOT/pm012_lbm/bin/pm012_lbm.exe
P="body=pollen D=128 lv=3 T=150 coll=bgk fb=1.5,2.5,1.5 gb=0.25,1.0,0.25 wall=ibb rx=0 ry=135.114 rz=-138.843"
$X $P Re=20000 S=0.75 out=$R/p_ibb_d128_btw_Re20k_S0.75.csv
$X $P Re=20000 S=0 out=$R/p_ibb_d128_btw_Re20k_S0.csv
python -I cfd/postprocess.py summary $R/p_ibb_d128_btw_Re20k_S0.75.csv
$X body=pollen D=192 lv=3 Re=33057 wall=ibb plan=1     # memory per level, then exit (no GPU)
# field dumps for viz/flow (a short run)
$X body=pollen D=128 lv=3 Re=33057 S=0.5 T=22 coll=bgk wall=ibb rx=0 ry=135.114 rz=-138.843 dump=20,21,22 out=$R/v_d128_btw_S0.5.csv
# the same cases through the queue (the runner adds out=)
cfd/lbm/queue/add.sh "p_ibb_d128_btw_S0.5 $P Re=33057 S=0.5" "p_ibb_d128_btw_S0 $P Re=33057 S=0"
cfd/lbm/queue/runner.sh front
# explorer data: means over t* 15-150 of every finished p_ibb_* run
python -I viz/explorer/export_cfd.py $R
```

`cfd/lbm/stl_holes.py` finds the 26 hole axes of the POLLEN STL and gives the rx/ry/rz values for "hole facing the
flow" and "between holes". To recreate the POLLEN STL:
`$PM012_CFD_ROOT/venv/Scripts/python.exe -I cfd/step_to_stl.py <STEP> <out.stl>`.

## Open risks

- No configuration has passed V1 and V2 together. With `wall=ibb`, V1 passes at D 128 but V2 fails there (Cl 0.362
  above 0.33). At D 192 neither is decided (no S 0 sphere run).
- **Lift is not grid-converged.** From D 128 to D 192, Cl at S 0.5 drops 17 % for POLLEN and 25 % for the smooth
  sphere (PREDICTED). Cd moves about 2 %.
- The torque gate fails with `wall=ibb` (CM 0.0084-0.0088 against 0.0047-0.0079). With `wall=hbb` the spin torque
  had the wrong sign. CM and k are not usable.
- The wall layer is not resolved (D / sqrt(Re) is 0.70 cells at D 128 and 1.06 at D 192, Re 33057). The spin torque
  and the lift depend on it.
- Every POLLEN number is a single run. Only the D 48 S 0 sphere twin has a second noise seed; no number has a
  seed-to-seed spread.
- The D 192 POLLEN twin started without noise (`pert=0`), unlike its S 0.5 partner.
- How the holes face the flow in a real shot is not known. The three orientations are ASSUMED.
- `body=pollen` has no chamfers or fillets. Its volume is 0.06 % below the STL's (22,299.17 against
  22,312.36 mm^3).
- The revox check for `body=pollen` has not run.
- The S 0 runs keep a lateral force: up to 0.13 for the smooth sphere over 40 t*, and Cl 0.015-0.048 for the POLLEN
  twins (PREDICTED).
- The V1 pass uses the box factor 0.976 from one regularized D 48 pair (ASSUMED for BGK and finer grids). The raw Cd
  is inside the band as well.
- The STL sphere and the analytic sphere disagree at D 48, S 0.5 (Cd +0.067, Cl +0.101, PREDICTED). The cause is
  not known. The POLLEN results do not use the STL path.
- The T_int estimates run low for slow signals ("Averaging and uncertainty").
- The torque reference is one LES study (Ito & Kamijima 2025) of a 40 mm ball, read off a table and interpolated;
  its Cm definition is ASSUMED to be the one in their 2022 paper. The +-25 % band is the spread to one k-epsilon
  study.
- The STEP download URL was not recorded. Its hash is recorded above.

## Files

| File | Purpose |
|---|---|
| `lbm/pm012_lbm.cpp`, `lbm/pm012_lbm.cl` | Own LBM-LES solver (route b): host and OpenCL kernels. |
| `lbm/build.cmd` | MSVC build of the solver, output outside the repo. |
| `lbm/stl_holes.py` | Finds the 26 hole axes and the two orientations. |
| `lbm/sphere_stl.py` | Writes the STL sphere for the STL-path check and the smooth twins. |
| `lbm/queue/runner.sh`, `lbm/queue/add.sh` | GPU case queue (section "GPU queue"). |
| `postprocess.py` | Statistics, gate checks (`v1`, `v2`, `torque`, `stl0`, `match`), grid comparison and model conversion. Has `--selftest`. |
| `cfd_aero.json` | Release status and gate verdicts, last updated 2026-10-31 14:09 (before `wall=ibb`). Holds no POLLEN values while the gates fail. |
| `step_to_stl.py` | STEP to STL conversion and mesh check. |
| `.gitignore` | Keeps STL, STEP, VTK, binaries and logs out of git. |
| `../viz/explorer/export_cfd.py`, `../viz/explorer/cfd_runs.json` | Exports the finished `p_ibb_*` runs (means over t* 15-150) for the explorer's CFD tab. |
| `../viz/flow/` | Flow viewer for the `dump=` fields (`make_flow.py`). |
| `fluidx3d/*`, `run_cases.sh` | Route (a), not used (below). |

## Not used: FluidX3D (route a)

None of the results in this folder come from FluidX3D. This section is kept for the record.

- **Clone:** `$PM012_CFD_ROOT\FluidX3D` (https://github.com/ProjectPhysX/FluidX3D), pinned at commit
  `b85d64ee39a72687d163d42806c9a0ccdaed6d3c`. It is never copied into this repo.
- **Build:** planned with VS 18 MSBuild, Release x64, toolset v145 (the project file asks for v142, which VS 2019
  BuildTools also provides). The coding environment's permission check refused it, so it was never built or run.
- **Prepared, unused files:**
  - `fluidx3d/setup.cpp`: the cases, as altered FluidX3D source;
  - `fluidx3d/prepare_fluidx3d.py`: pins the commit, sets the defines, applies a force patch and copies setup.cpp.
    The patch sums only links to fluid cells, each contributing (2 f_i - 6 w_i c_i.u_w) c_i (Ladd 1994; Krueger
    et al. 2017);
  - `run_cases.sh`: build and case list (`build`, `validate`, `muto`, `pollen7`, `production`), with output to
    `cfd/results/`.
- **Planned setup:** D3Q19 SRT, Esoteric-Pull in-place streaming, FP16C storage, Smagorinsky (`SUBGRID`),
  equilibrium on all six faces. Its run-time estimates came from the FluidX3D benchmark for the RTX 3060 (3566
  MLUPs) and were never measured.

### FluidX3D licence (read 2026-10-31 from the clone's LICENSE.md; verbatim copy in `fluidx3d/LICENSE-FluidX3D.md`)

The altered source `fluidx3d/setup.cpp` is still in this repo, so these terms still apply. Copyright (c) 2022-2026
Dr. Moritz Lehmann. Each term says how this project complies.

1. **Use.** Allowed only for public research, education or personal use.
   - This is an FTC student-team (education) project.
   - **No commercial use.** That includes paid services whose value comes from FluidX3D, so it must not be used for
     any paid work.
2. **Origin.** The origin must not be misrepresented, and altered source must be plainly marked.
   - `fluidx3d/setup.cpp` is headed "ALTERED FluidX3D SOURCE".
   - The kernel patch lines carry "PM-012 patch".
3. **No military use.**
4. **No training of AI models** on FluidX3D source.
5. **Publishing.** If results or binaries from an altered version are published, the altered source must be
   published too.
   - Our alterations are `fluidx3d/setup.cpp` and the patch in `fluidx3d/prepare_fluidx3d.py`.
   - No FluidX3D results exist, so nothing has been published from it.
6. **Citation.** Scientific publications that use FluidX3D must cite:
   - Lehmann, *Computation* 10:92 (2022), doi 10.3390/computation10060092;
   - Lehmann et al., *Phys. Rev. E* 106:015308 (2022).
7. **Notice.** The licence notice must stay in source distributions. That is why the verbatim copy is kept here.

## References

- Brown P.P., Lawler D.F. (2003) Sphere drag and settling velocity revisited. *J. Environ. Eng.* 129(3):222-231,
  doi 10.1061/(ASCE)0733-9372(2003)129:3(222). Eq. 19: Cd = 24/Re (1 + 0.150 Re^0.681) + 0.407/(1 + 8710/Re).
- Sakai W., Miyazaki T., Komatsu T., Takahashi N., Himeno R. (2016) Aerodynamics of a spinning table tennis ball:
  lift crisis. JSME Annual Meeting, J2340102, doi 10.1299/jsmemecj.2016.J2340102.
- Conti et al. (2026) arXiv:2606.28805v2, unreviewed preprint.
- Muto M., Tsubokura M., Oshima N. (2012) Negative Magnus lift on a rotating sphere at around the critical Reynolds
  number. *Phys. Fluids* 24:014102, doi 10.1063/1.3673571.
- Kim J., Choi H., Park H., Yoo J.Y. (2014) Inverse Magnus effect on a rotating sphere: when and why. *J. Fluid Mech.*
  754:R2, doi 10.1017/jfm.2014.428.
- Ito K., Kamijima K. (2025) Estimation of aerodynamic properties of a spinning table tennis ball using computational
  fluid dynamics analysis. *Transactions of the Japan Society for Simulation Technology* 17(1):25-31 (in Japanese;
  Table 5: Cm; Table 1: SP).
- Ito K., Kamijima K. (2022) Three-dimensional flight trajectory simulation of a table tennis ball using the
  aerodynamic coefficient calculated by CFD analysis. *Transactions of the Japan Society for Simulation Technology*
  14(1):36-42 (in Japanese; eq. 4: torque definition; Table 4: Cm).
- Ladd A.J.C. (1994) Numerical simulations of particulate suspensions via a discretized Boltzmann equation, Part 1.
  *J. Fluid Mech.* 271:285-309.
- Krueger T. et al. (2017) *The Lattice Boltzmann Method: Principles and Practice.* Springer.
- Bouzidi M., Firdaouss M., Lallemand P. (2001) Momentum transfer of a Boltzmann-lattice fluid with boundaries.
  *Phys. Fluids* 13:3452-3459, doi 10.1063/1.1399290.
- Wen B., Zhang C., Tu Y., Wang C., Fang H. (2014) Galilean invariant fluid-solid interfacial dynamics in lattice
  Boltzmann simulations. *J. Comput. Phys.* 266:161-170, doi 10.1016/j.jcp.2014.02.018.
- Rohde M., Kandhai D., Derksen J.J., Van den Akker H.E.A. (2006) A generic, mass conservative local grid refinement
  technique for lattice-Boltzmann schemes. *Int. J. Numer. Meth. Fluids* 51:439-468, doi 10.1002/fld.1140.
- Latt J., Chopard B. (2006) Lattice Boltzmann method with regularized pre-collision distribution functions.
  *Math. Comput. Simul.* 72:165-168.
- Hou S., Sterling J., Chen S., Doolen G.D. (1996) A lattice Boltzmann subgrid model for high Reynolds number flows.
  *Fields Inst. Commun.* 6:151-166.
- Smagorinsky J. (1963) *Mon. Weather Rev.* 91:99-164.
- Celik I.B. et al. (2008) *J. Fluids Eng.* 130:078001 (GCI).
- Lehmann M. (2022) *Computation* 10:92.
- Lehmann M. et al. (2022) *Phys. Rev. E* 106:015308.
