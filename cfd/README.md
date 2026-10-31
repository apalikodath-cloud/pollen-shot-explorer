# PM-012 CFD: POLLEN in still room air (own GPU LBM-LES)

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
- The old line "Labels follow HANDOFF section 5" is replaced by the pointer above.
- Commit IDs in this file (208142e, 28f95b1, ca68597) are from the development history before this repo was
  published; they are not in this repo's history.
- Inputs keep their own labels (table "Inputs"). Run times and speeds are read from the run logs (derived).

## Status (2026-10-31 12:55)

- **Not released.** No CFD number may replace an ASSUMED value in the model. `cfd_aero.json` records the same
  status and holds no POLLEN values.
- **Every run used route (b)**, the LBM-LES solver written for PM-012 in `cfd/lbm/`. FluidX3D (route a) was never
  built or run (section "Not used" at the end).
- **V0** (sphere spinning in still fluid, Stokes torque) passes: 1.026 x analytic.
- **V1** (smooth sphere, Re 33057, S 0) **fails** at every grid and setting tried so far. The only gate-length run
  (BGK, D 48, T 150) gives a box-corrected Cd of 0.545 against the band 0.43-0.50. The lowest box-corrected Cd is
  0.497 (BGK, D 94, stationary): inside the band, but T 55 < 150, so it does not pass, and its box correction is
  ASSUMED for BGK. A gate-length run at D 94 or on the refined grid is needed before V1 can pass.
- **CM and k (spin decay): not usable: torque check pending.** The spinning runs give CM near 0 (D 48) or a CM with the sign of a
  driving torque (D 96). The torque axis, sign and normalisation are being checked; no CM or k from this folder may be
  used, quoted or matched until that check is done.
- **STL-sphere check** (D 48, S 0.5) **fails**: the STL sphere gives Cd +0.067 and Cl +0.101 above the analytic
  sphere (PREDICTED). The **revox check** is PENDING (torque fix): every spinning case waits for the spin-torque fix.
- Every spinning result here (V2, STL path, revox, POLLEN) is a solver diagnostic until the torque check is done. V2
  cannot release anything while V1 fails.
- Runs with local grid refinement (option `lv=` 2 or more) are described in "Local grid refinement". The same
  binding rule applies to them, including T >= 150.

## Acceptance (binding)

This is the only acceptance rule. Its bands are the ones pre-registered at 09:32 on 2026-10-31, before any run
(commit 208142e: V1d "Box-corrected Cd in 0.43-0.50", V2 "Cl in 0.22-0.33"). The review added the averaging,
lateral-force and STL conditions. `postprocess.py v1`, `v2` and `match` apply it.

| Gate | Passes only when |
|---|---|
| V1: smooth sphere, Re 33057, S 0 | box-corrected Cd is in 0.43-0.50, the Cd window is stationary, and u_win(Cd) <= 0.035 (half the band). Reference: Brown & Lawler (2003) Eq. 19 gives 0.453 at Re 33057 (derived). |
| V2: smooth sphere, Re 33057, S 0.5 | Cl is in 0.22-0.33, the Cl window is stationary, the S 0 twin covers the same window, and u_win(Cl) + L_twin <= 0.055 (half the band). |
| Run length | every V1 and V2 run is at least T 150 (window t* 15 to the end). |
| One configuration | V1 and V2 pass with the same collision, Cs, precision, grid and box. POLLEN runs use exactly that configuration. |
| STL path | an STL sphere (`lbm/sphere_stl.py`) spinning at S 0.5 matches the analytic sphere in Cd, Cl and CM at the release grid. |
| revox | one POLLEN spin case run at two `revox` values matches in Cd, Cl and CM. |

- **Match** (`postprocess.py match`): both runs are stationary, and |difference| <= max(t95 sqrt(se_a^2 + se_b^2),
  floor). Floors (ASSUMED): Cd 0.01, Cl 0.01, CM 0.001.
- **Band on POLLEN numbers**, once released. Cd, CM and k are reported as X +- (b |X| + u_win). Cl is reported as
  X +- (b |X| + u_win + L_twin). Here b = max(|V1 error|, |V2 error|, |grid change|), where:
  - V1 error = box-corrected Cd / 0.453 - 1;
  - V2 error = Cl / 0.275 - 1 (0.275 is the band centre);
  - grid change = the relative change between the two finest grids.

  So the band is never smaller than the V1 error.

### Withdrawn: the "30 % gate"

- **What:** "Cd within 30 % of 0.4532", printed as "30 % gate 0.317-0.589".
- **When and who:** the AI coding agent that built the solver wrote it into this README in commit 28f95b1 at 10:18
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

**Solver** (`lbm/pm012_lbm.cpp` host, `lbm/pm012_lbm.cl` kernels, built with `lbm/build.cmd`, run on the RTX 3060):
- D3Q19 with two lattices and pull streaming. Storage is FP16 (`prec=fp32` is optional).
- Collision: BGK (`coll=bgk`) for every current V1, V2 and POLLEN line. The default, `coll=reg` (regularized), gave
  Cd 0.68-0.71 at Re 33057 and is not used for gates.
- Smagorinsky LES with Cs 0.1 everywhere. The diagnosis knobs `bulk`, `csn` and `taun` stay off.
- Walls: halfway bounce-back with the moving-wall (Ladd) term, u_w = w x (x - c). Spin is about +y, so backspin lift
  points along +z.
- Force and torque: momentum exchange over the wall links. Each CSV row averages every step since the previous row
  (`favg=1`). The row length is even, so a force that alternates every step cancels inside each row. The log footer
  reports that alternation as `p2_*`.
- Boundaries: equilibrium inflow (u = 0.05, lattice Mach 0.087) on the inlet and the four side faces. Pressure outlet
  (`outlet=p`).
- Start: uniform flow plus noise of 1e-3 u from a fixed hash (`pert=1e-3`). There is no seed key, so seeds cannot be
  varied. Long runs (T >= 150) are used instead.
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

**Coefficients:** q = 0.5 u^2 pi R^2 with R = D/2 in cells. Cd = Fx/q, Cy = Fy/q, Cl = Fz/q, CM = -Ty/(q R).

**Numerical regime** (derived):
- nu = u D/Re. At D 94 and Re 33057, tau = 0.50043, so the run is stable only with the LES.
- The laminar boundary layer is about D/sqrt(Re) = 0.0055 D, about 0.5 cell at D 94. **The wall layer is not
  resolved.** This is an under-resolved LES with staircase walls, so separation and transition are not reliable.
  That is why the smooth-sphere gates set the band.

**Builds** (outside the repo, in `%PM012_CFD_ROOT%\pm012_lbm\bin`):

| Build | Source | Runs |
|---|---|---|
| before 10:07, no `favg` (instantaneous samples) | not committed | rotstokes_test, re100_d24_big, re100_d32, v1_d48 |
| 10:14, `pm012_lbm_1014.exe` | committed 4 minutes later in 28f95b1 (not re-checked against the binary) | v1_d48_favg, v1d_box8, v1d_cs17, v1d_bgk, v1d_fp32, v1_bgk_d64 |
| 10:32, `pm012_lbm.exe` | ca68597: even row length, diagnosis knobs (off by default) | v1_reg_d64, v1_bgk_d80, v1_bgk_d94 and every later run |

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
  on the finest level only. The finest box must hold the whole shell and the hollow inside (default margin
  0.7 D upstream, 1.5 D downstream, 0.7 D sideways; each coarser refined level adds 0.5 / 1.0 / 0.4 D).

**Options.** `lv=1` (uniform, the old behaviour) to 4; `fb=up,down,side` finest box; `gb=up,down,side` growth per
coarser level; `plan=1` prints per-level cells and memory, cells across a hole and across the wall, and
`need_mib=` for a queue, then exits without the GPU; `body=none` (uniform-flow check) and `body=masstest` (closed box,
total mass) are checks. `lv=3 D=192` (box 6x4x4 D) needs about 4.3 GB in FP16 (derived, solver plan):

| Level | D | Cells | Memory (FP16) |
|---|---|---|---|
| L0 | 48 | 288x192x192 = 10.6 M | 780 MiB |
| L1 | 96 | 356x212x212 = 16.0 M | 1175 MiB |
| L2 | 192 | 424x272x272 = 31.4 M | 2304 MiB |

The finest D 192 gives 27.5-30.2 cells across a hole and 4.8 across the wall (derived; D 94 uniform gave 13-15 and
2.35). A uniform D 192 grid would need about 680 M cells, which does not fit. `lv=3 D=96` uses 0.54 GB.

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
| Uniform flow, no body, lv 3 D 64, BGK | FP16 noise max \|u - U\|/U 4.5e-4 = same as the uniform grid (4.6-5.2e-4); FP32, no noise: max \|u - U\|/U 9.2e-6 and \|rho - 1\| 1.5e-6 at t* 12 on every level | no growth at the interfaces |
| Uniform flow, no body, regularized collision, Re 3e4 | lv 3 FP32 grows: 8.6e-4 (t* 3), 3.3e-2 (t* 6), 3.9e-2 (t* 12), first at the upstream face of the finest box. The **uniform** grid does the same (D 16: 3.9e-3 at t* 12, 3.95e-2 at t* 24; D 32: 3.9e-2 at t* 12; also with Cs 0); stable at u 0.02 (6e-7) and at Re 3000 (7.6e-6) | **fails**; see below |
| Old uniform runs (`lv=1`) with the new code | 192 CSV rows: forces and Cd, Cy, Cl bit-identical; torques differ by at most 1.2e-7 (lattice units; summation order of the force split) | same as before |
| V0 rotating sphere, Stokes torque, lv 2 D 32 FP32 | 1.0286 x analytic; uniform grid 1.0264 (+0.2 %) | 0.97-1.10 |
| Sphere Re 100, lv 2 D 32 FP32 | Cd 1.2013; uniform grid 1.1890 (+1.0 %) | within a few % of the uniform grid |
| Diagnostics unit check: closed smooth sphere, S 0.5, lv 2 D 32, `holes=` given | hole flux 0, cavity 0 cells, inner and hole-wall force 0, outer part = total (Cd 0.654) | exactly that |
| Diagnostics, spinning POLLEN STL (hole facing the flow), S 0.5, lv 2 D 96, t* 3 (smoke test) | STL volume ratio 1.0005, odd rays 0; 371,848 cavity cells; hole fluxes non-zero; at t* 3 Cd split outer / inner / hole walls 0.567 / 0.067 / 0.065, sum = total to 1e-6 | runs; not a result |
| **V1** smooth sphere Re 33057, S 0, lv 3 D 96, BGK FP16, box 6x4x4, T 55, mean t* 15-55 | Cd 0.553 (se 0.004, half-window drift -0.011); Cl -0.004, Cy -0.023 | Binding V1 (section "Acceptance"): box-corrected Cd 0.540 (x 0.976), +19 % against 0.453, outside 0.43-0.50, and T 55 < 150: **fail**. (The "30 %" band first used here is withdrawn.) Uniform BGK D 80 same box: Cd 0.539, Cl 0.104 |
| **V2** smooth sphere Re 33057, S 0.5, same grid | Cl 0.220 (se 0.007, drift +0.012), Cd 0.510, CM not usable (torque check pending); S 0 twin above: Cl -0.004, Cd 0.553 | Binding V2: Cl 0.2197 is just below 0.22, and T 55 < 150: **fail**. Twin lateral L 0.024, u_win(Cl) + L 0.034 <= 0.055. CM: not usable: torque check pending |

All numbers in this table are PREDICTED (own solver; smooth sphere: validation only, not POLLEN). The V1 and V2
grid study continues at finest D 192 (lv 3, queued); D 384 does not fit in 12 GB (lv 4: 31 GiB with these boxes,
15 GiB even with tight boxes).

**Collision: BGK for production.** The regularized collision (`coll=reg`) is unstable in plain uniform flow at
tau close to 0.5 with u 0.05 (table above), on the uniform grid as well as the refined one, with or without the
Smagorinsky term. That fits its high sphere Cd (0.67-0.70 against 0.54-0.56 for BGK). All refined and production runs
use `coll=bgk`.

No POLLEN number from the refined solver exists yet. Queued after V1 and V2 at D 192 (same configuration, refined
lv 3 D 192 BGK): POLLEN hole facing the flow and between holes at S 0 and S 0.5; 8 random orientations at S 0 and 4
of them at S 1.0 (7 m/s); between holes at S 0 and S 1.0 at 4 and 10 m/s. Every spin case has its no-spin twin and a
smooth-sphere twin on the same grid. Estimated cost (derived): about 3 h per case at D 192 on the RTX 3060, more
for spinning POLLEN (re-voxelisation).

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

- Gate runs are at least T 150, a 135 t* window. Length replaces seeds (fixed noise hash).
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
- A single-window twin Cl is never subtracted from a spinning Cl.
- Every backspin result is shown next to its S 0 twin.

## Validation results (PREDICTED; verdicts under the binding rule)

At Re 33057, POLLEN flies at 7 m/s (derived). Unless noted: box 6 x 4 x 4 D, FP16, Cs 0.1, T 55 (window t* 15-55),
so no run in this table is gate length. "vs 0.453" is the box-corrected Cd against Brown & Lawler.

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

- Box factor 0.976 = Cd(8 x 6 x 6) / Cd(6 x 4 x 4) for the regularized D 48 pair (PREDICTED). Using it for BGK and
  for finer grids is ASSUMED. The pre-registered box study (8 x 5 x 5 and 10 x 7 x 7) was not run.
- Grid series, BGK (T 55): D 48 0.563, D 64 0.533 (not stationary), D 80 0.539, D 94 0.509. The change between the
  two finest grids (D 80 to D 94) is -0.030 (-5.9 %); from D 48 to D 94 it is -0.054 (-9.6 %). Cd is not grid
  converged.
- The collision model moves Cd more than the grid does: at D 48 and D 64, BGK gives a Cd 0.13-0.15 lower than
  regularized.

Other checks:

| ID | Case | Result (PREDICTED) | Reference | Verdict |
|---|---|---|---|---|
| V0 | sphere spinning in still fluid, Stokes regime (Re_rot 0.4), D 32, FP32, cube of side 4 D | torque 1.026 x Stokes | 0.97-1.10: Stokes torque 8 pi mu R^3 w, raised 1.003-1.016x by the box (derived) | pass (cube-flux check not run) |
| Re 100 | sphere, regularized, T 30: D 24 (box 12 x 10 x 10, FP16) / D 32 (box 8 x 6 x 6, FP32) | Cd 1.171 / 1.189 | 1.073 (Brown & Lawler Eq. 19, derived) | +9 % / +11 %, no gate. Earlier text used 1.087, whose source was not recorded. |
| V2 | sphere at S 0.5, D 48, BGK, T 150 (g48_v2_S0.5_T150), twin g48_v1_S0_T150 | Cl 0.252 +- 0.018 (trend +0.027: not stationary), Cd 0.547 +- 0.013 (not stationary). S 0 twin, same window t* 15-150: Cl -0.028, Cy -0.003, L_twin 0.029 (5 t* blocks 0.033-0.214), Cd 0.559. u_win(Cl) + L_twin 0.047 <= 0.055. CM: not usable: torque check pending | Cl 0.22-0.33 (pre-registered). Cl about 0.29 at SP 0.55 (Sakai et al. 2016, Fig. 8, Re 3e4 bin, by eye); 0.26 at Re 3.6e4, Sp 0.5 (Conti et al. 2026, unreviewed preprint); Cd about 0.49 near SP 0.5 (Sakai, Fig. 7) | **fail**: Cl is in the band, but the Cl window is not stationary. A spinning run, so a solver diagnostic until the torque check is done |
| STL path, S 0 | STL sphere vs analytic sphere at S 0, D 48, BGK, T 150 (g48_v1stl_S0_T150 vs g48_v1_S0_T150): tests the STL path without spin | queued (12:30) | match in Cd and Cl | pending |
| STL path | STL sphere vs analytic sphere, S 0.5, D 48, BGK, T 150 (g48_v2stl_S0.5_T150 vs g48_v2_S0.5_T150) | STL: Cd 0.614 +- 0.010, Cl 0.354 +- 0.017 (both stationary). Analytic: Cd 0.547 +- 0.013, Cl 0.252 +- 0.018 (neither stationary: trend +0.026 / +0.027). Difference: Cd +0.067, Cl +0.101. CM: not usable: torque check pending. S 0 twin: see the V2 row | match in Cd, Cl and CM (tolerance 0.01 here) | **fail**: both differences are far above the tolerance, and the analytic run is not stationary. Both runs spin, so this is a solver diagnostic until the torque check is done |
| revox | POLLEN "between holes", S 1.0, D 64, BGK, T 150, revox 1 vs 2 | not run in this round: every spinning case waits for the spin-torque fix (revox 1 held since 12:10) | match in Cd, Cl and CM | **PENDING (torque fix)** |
| V3 (optional) | spinning sphere, Re 1e4, Gamma 0 / 0.2 / 1.0, D 48, 8 x 5 x 5 | not run | Muto et al. 2012 LES, Table I: Cl 0.167 (s.d. 0.029) at Gamma 0.2, 0.301 (s.d. 0.096) at Gamma 1.0 | none |

Kim et al. 2014 (inverse Magnus, Re 6e4-2.6e5) is above this Re range, so it is context only.

**Deviation from the review (STL path).** The review asked for the STL-sphere check at D 94. It runs at D 48:
- at 11:23 the uniform D 94 runs were put on hold, because local grid refinement (`lv=`) replaces that path;
- one D 94 run of T 150 would take about 4-5 hours on the shared card (PREDICTED from the D 94 T 55 run).

The D 48 pair tests the STL path itself: voxelizer, rotation, re-voxelization and moving wall. A match at the release
grid stays a release condition. The smooth twins of the POLLEN lines (`t_*` in `queue/held.txt`) now use the STL
sphere, so they share the POLLEN voxelization path.

## Runs in the queue (times PREDICTED)

| Run | What | Started | Ends about |
|---|---|---|---|
| g48_v1stl_S0_T150 | STL path at S 0, STL sphere, D 48, BGK, T 150 | 12:53 | 13:20 |
| g64_p_S1.0_between_revox1_T150 | revox check, POLLEN, D 64, S 1.0, revox 1 | held until the spin-torque fix | |

Finished since 11:50: v1_bgk_d94, g48_v2_S0.5_T150, g48_v2stl_S0.5_T150, g48_v1_S0_T150 and
g64_p_S1.0_between_revox2_T150 (its revox 1 partner is held, so it is not reported).

## GPU queue

- The queue scripts are not in this repo; they live with the runs, outside it. `runner.sh front|back [name]`
  pops the first or last line of `todo.txt` (`<id> <pm012_lbm.exe args>`). It starts the case only when the free GPU memory covers the estimate plus 1 GiB, and
  writes `runs/<id>.csv` and `.log`.
- `add.sh [--front]` adds lines under the same lock (`mkdir queue/.lock`). Lines on hold sit in
  `held.txt`.
- The queue lives outside the repo (`%PM012_CFD_ROOT%\pm012_lbm\queue`). An extra lane there (`runner_igpu.sh`, not in
  the repo) runs small lines without `platform=` on the onboard Radeon. Lines with `platform=0` stay on the RTX 3060.
- Speed (derived, run logs): one D 48 FP16 case alone ran at 3195 MLUPs. When three cases shared the card, each ran
  at about 1270-1510 MLUPs.

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
| Model R, A | 0.0355 m, A = pi R^2 | CONFIRMED: `src/flight.py` (radius), `src/feasibility.py` (A) |
| Re = v D/nu | 4722 per m/s: 14,170 at 3 m/s, 33,057 at 7 m/s, 51,950 at 11 m/s | derived |
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
400 MiB.

| D (cells) | dx (mm) | Wall (cells) | Hole (cells) | Cells, box 6 x 4 x 4 D | Estimate | Use |
|---|---|---|---|---|---|---|
| 48 | 1.482 | 1.20, **leaks** | 6.9-7.5 | 10.6 M | 1179 MiB | sphere gates, STL-sphere check |
| 64 | 1.111 | 1.60 | 9.1-10.1 | 25.2 M | 2248 MiB | grid series, revox check |
| 80 | 0.889 | 2.0 | 11.4-12.6 | 49.2 M | 4009 MiB | grid series |
| 94 | 0.757 | 2.35 | 13.4-14.8 | 79.7 M | 6255 MiB | grid series, planned POLLEN grid |

**Leak criterion** (flat wall, cell-centre voxelization). A fluid-fluid D3Q19 link, at most sqrt(2) dx long, can cross
a wall of thickness t only if sqrt(2) dx > t. With t = 1.778 mm:

| D | sqrt(2) dx | Result |
|---|---|---|
| 57 or more | 1.765 mm or less | no tunnelling |
| 64 | 1.572 mm | no tunnelling |
| 94 | 1.070 mm | no tunnelling |
| 48 | 2.10 mm | leaks: no POLLEN runs at D 48 |

In the 6 x 4 x 4 box the solid blockage is 4.9 %.

## Converting to the model's convention

The model uses A = pi R^2 with R = 0.0355 m, S = |w|R/|v| and w(t) = w0 exp(-k t). The CFD uses the CAD R_cfd of
35.56 mm. `postprocess.py` converts every `body=stl` run (derived formulas):
- **Drag and lift:** Cd_model = Cd_cfd (R_cfd/R)^2 = 1.0034 Cd_cfd. Cl converts the same way.
- **Spin ratio:** S_model = 0.9983 S_cfd.
- **Spin decay:** k = T/(I w) = CM 0.5 rho v pi R_cfd^4 / (I S). At 7 m/s that is about 1.07 CM/S per second. CM and k: not usable: torque check pending.

## Rerun (Git Bash, from the repo root, with PM012_CFD_ROOT set to a folder outside the repo)

Build the solver from a Windows prompt with `cfd\lbm\build.cmd` (MSVC x64; output in
`%PM012_CFD_ROOT%\pm012_lbm\bin`). Run `pm012_lbm.exe` with no arguments for the key=value list. Then:

```bash
python -I cfd/lbm/sphere_stl.py $PM012_CFD_ROOT/sphere_stl/sphere_71p12.stl   # prints the volume for svol=
R=$PM012_CFD_ROOT/pm012_lbm/runs
$PM012_CFD_ROOT/pm012_lbm/bin/pm012_lbm.exe body=sphere D=48 Re=33057 S=0.5 T=150 coll=bgk out=$R/g48_v2_S0.5_T150.csv
python -I cfd/postprocess.py summary $R/g48_v2_S0.5_T150.csv
python -I cfd/postprocess.py v1 $R/g48_v1_S0_T150.csv --box 0.976
python -I cfd/postprocess.py v2 $R/g48_v2_S0.5_T150.csv $R/g48_v1_S0_T150.csv
python -I cfd/postprocess.py match $R/g48_v2stl_S0.5_T150.csv $R/g48_v2_S0.5_T150.csv
python -I cfd/postprocess.py --selftest
```

`cfd/lbm/stl_holes.py` finds the 26 hole axes of the POLLEN STL and gives the rx/ry/rz values for "hole facing the
flow" and "between holes". To recreate the POLLEN STL:
`$PM012_CFD_ROOT/venv/Scripts/python.exe -I cfd/step_to_stl.py <STEP> <out.stl>`.

## Open risks

- V1 fails and the cause is not known. The collision model moves Cd far more than the grid does, and the wall layer
  is not resolved.
- The S 0 sphere keeps a lateral force of up to 0.13 over 40 t* (PREDICTED). Through L_twin it may also make V2 fail.
- The box factor comes from one regularized D 48 pair.
- The STL sphere and the analytic sphere disagree at D 48, S 0.5 (Cd +0.067, Cl +0.101, PREDICTED). The cause is
  not known; the spin-torque check may bear on it. Until it is found, no STL-path result can be trusted.
- No D 94 run of gate length is queued, and the D 94 STL-sphere check is not run (on hold since 11:23: local grid
  refinement replaces the uniform D 94 path).
- The T_int estimates run low for slow signals ("Averaging and uncertainty").
- The cost of re-voxelizing every step (S 1.5) is not measured.
- The STEP download URL was not recorded. Its hash is recorded above.

## Files

| File | Purpose |
|---|---|
| `lbm/pm012_lbm.cpp`, `lbm/pm012_lbm.cl` | Own LBM-LES solver (route b): host and OpenCL kernels. |
| `lbm/build.cmd` | MSVC build of the solver, output outside the repo. |
| `lbm/stl_holes.py` | Finds the 26 hole axes and the two orientations. |
| `lbm/sphere_stl.py` | Writes the STL sphere for the STL-path check and the smooth twins. |
| `postprocess.py` | Statistics, gate checks (`v1`, `v2`, `match`), grid comparison and model conversion. Has `--selftest`. |
| `cfd_aero.json` | Release status and gate verdicts. Holds no POLLEN values while the gates fail. |
| `step_to_stl.py` | STEP to STL conversion and mesh check. |
| `.gitignore` | Keeps STL, STEP, VTK, binaries and logs out of git. |
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
     the firm's paid work.
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
  lift crisis. JSME Annual Meeting, J2340102, doi 10.1299/jsmemecj.2016.J2340102 (notes: `research/papers/sakai2016.md`).
- Conti et al. (2026) arXiv:2606.28805v2, unreviewed preprint (checked in `research/checks/sweep_aero.md`).
- Muto M., Tsubokura M., Oshima N. (2012) Negative Magnus lift on a rotating sphere at around the critical Reynolds
  number. *Phys. Fluids* 24:014102, doi 10.1063/1.3673571.
- Kim J., Choi H., Park H., Yoo J.Y. (2014) Inverse Magnus effect on a rotating sphere: when and why. *J. Fluid Mech.*
  754:R2, doi 10.1017/jfm.2014.428.
- Ladd A.J.C. (1994) Numerical simulations of particulate suspensions via a discretized Boltzmann equation, Part 1.
  *J. Fluid Mech.* 271:285-309.
- Krueger T. et al. (2017) *The Lattice Boltzmann Method: Principles and Practice.* Springer.
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
