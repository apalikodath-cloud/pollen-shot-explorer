# CFD test plan: does a POLLEN ball knuckle?

Status: plan and interim results, 2026-11-05. Labels as in `GPU_OPTIMIZATION.md`:
- [C] read from the code;
- [M] measured on hardware (here: what the solver produced, not a physical measurement);
- [P] predicted (all CFD force results are predictions about the real ball until a wind-tunnel or flight test confirms them);
- [D] derived;
- [Lit] literature.

**No CFD number in this note is a validated fact about the real ball.**

Solver: `cfd/lbm/pm012_lbm.cpp` and `pm012_lbm.cl` (lattice Boltzmann, D3Q19, GPU, OpenCL).
Statistics script: `research/knuckleball/cfd_knuckle_stats.py`, output `data/cfd_knuckle_stats.json`.

## 1. What the code can and cannot do [C]

| Capability | Status | Option |
|---|---|---|
| Open POLLEN (analytic shell, cavity, 26 holes from the CAD) | yes | `body=pollen` |
| Sealed ball, same outer surface (no holes, no cavity) | yes (debug) | `body=pollen pball=1` |
| Smooth sealed sphere | yes | `body=sphere` |
| POLLEN as a CAD STL | yes | `body=stl stl=... Dmm=71.12` |
| Static orientation | yes | `rx, ry, rz` in degrees |
| Prescribed spin about +y, any rate | yes | `S = ωR/U` |
| **Free rotation (torque-driven ω(t))** | **no** | design in §6 |
| **Spin axis other than +y relative to the flow** | only by choosing the inflow frame (spin is always about +y; flow +x) | |
| Time-resolved forces and torques | yes, one csv row per `every` steps; `favg=1` averages each row over all steps | default |
| Force split: outer surface / inner surface / hole walls | yes, `# dg` lines | `holes=`, `wall_mm`, `hole_mm` |
| Net flux through each of the 26 holes, cavity mean speed, cavity vorticity, cavity angular momentum | yes, `# dg` lines | as above |
| Velocity field snapshots (finest level, strided box) | yes; Q and vorticity are computed in post-processing | `dump=t1,t2,... dumpstride dumpbox` |
| **Pressure field / surface Cp** | **no**: snapshots hold velocity and flags only; density (p = c_s²ρ) is not written | small change: add ρ to `dump_field` |
| Wall treatment | halfway or interpolated bounce-back | `wall=hbb|ibb` |
| Collision | BGK or regularised; Smagorinsky LES | `coll`, `Cs` |
| Precision | FP16 storage (scaled) or FP32 | `prec` |
| Grid refinement | 1 to 4 nested levels, 2:1 | `lv, fb, gb` |
| Initial disturbance and ensemble | random perturbation, hash seed | `pert, seed` |
| Per-kernel GPU timing | yes (added 2026-11-05) | `prof=1` |
| Compressibility | weakly compressible LBM; lattice Mach Ma = u√3 (u = 0.05 gives Ma 0.087). The real flight Mach number is 0.013 to 0.026 | `u` |
| Fluid–structure interaction | none (rigid shell) | see `AERODYNAMIC_HYPOTHESES.md` H8 |

## 2. Results so far (D128, 3 levels, BGK, IBB, FP16, 150 D/U, statistics over t* ≥ 15) [P]

Notation:
- Cy = side force coefficient, Cl = lift (Magnus direction) coefficient; sd = standard deviation of the row-averaged series.
- Break: largest deviation of the path from the best-fit constant-force path within a 3 m flight window.
- Miss: size of the sideways (Cy) offset at 3 m from the force-free path, p95 over flight windows. It **includes the mean Cy**, so it mixes the steady orientation force with the random wander. The fluctuating part alone (Cy or Cl) has p95 3 to 10 mm in the low-spin D128 runs and 10 mm at D192 (`data/cfd_knuckle_stats.json`, keys `Cy_fluct` and `Cl_fluct`).

| Case | S | Cd | Cl mean | sd Cy | sd Cl | Break p95 at 3 m | Miss p95 at 3 m |
|---|---|---|---|---|---|---|---|
| POLLEN btw, Re 33k | 0 | 0.594 | 0.046 | 0.019 | 0.019 | 0.31 mm | 12.3 mm |
| POLLEN btw | 0.02 | 0.605 | 0.025 | 0.027 | 0.032 | 0.50 mm | 13.1 mm |
| POLLEN btw | 0.05 | 0.611 | 0.036 | 0.031 | 0.025 | 0.78 mm | 9.4 mm |
| POLLEN btw | 0.1 | 0.614 | 0.060 | 0.033 | 0.024 | 0.36 mm | 4.0 mm |
| POLLEN btw | 0.25 | 0.624 | 0.152 | 0.024 | 0.022 | 0.41 mm | 3.3 mm |
| POLLEN btw | 0.5 | 0.633 | 0.251 | 0.028 | 0.039 | 0.20 mm | 4.0 mm |
| POLLEN btw | 1.0 | 0.642 | 0.357 | 0.042 | 0.059 | 0.52 mm | 6.8 mm |
| POLLEN btw | 2.0 | 0.671 | 0.464 | 0.056 | 0.078 | 0.46 mm | 7.7 mm |
| POLLEN hf / o3 orientations | 0 | 0.611 / 0.596 | 0.016 / 0.017 | 0.018 / 0.023 | 0.018 / 0.030 | 0.21 / 0.46 mm | 8.1 / 10.2 mm |
| POLLEN btw, Re 20k / 47k | 0 | 0.611 / 0.587 | 0.048 / 0.046 | 0.022 / 0.021 | 0.020 / 0.021 | 0.43 / 0.40 mm | 10.8 / 10.0 mm |
| POLLEN btw, D192 | 0 | 0.581 | 0.040 | 0.029 | 0.018 | 1.11 mm | 13.6 mm |
| POLLEN btw, D192 | 0.5 | 0.619 | 0.207 | 0.035 | 0.039 | 0.58 mm | 13.1 mm |
| **Sealed smooth sphere**, D128 | 0 | 0.452 | 0.022 | **0.066** | **0.083** | 1.74 mm | **38.3 mm** |
| Sealed smooth sphere, D128 / D192 | 0.5 | 0.548 / 0.526 | 0.364 / 0.272 | 0.039 / 0.048 | 0.044 / 0.052 | 0.70 / 1.37 mm | 7.4 / 12.1 mm |
| POLLEN btw, D48, 2 levels, 120 D/U | 0 | 0.637 | 0.005 | 0.020 | 0.016 | 0.63 mm | 14.2 mm |

Notes:
- The sealed-sphere rows were run on a different GPU with an older build of the same code. The comparison is indicative.
- The kurtosis of the force increments is near 0 (−0.5 to +0.8) in every case: no jumps, Gaussian-like fluctuations.

What these say (interpretation, [P]):
1. At S = 0 the random lateral force of the open POLLEN has sd about 0.02 in Cy. This is about **3× less** than the sealed smooth sphere at the same Re and grid.
   - The holes and the internal through-flow seem to **damp** the wake-driven side force rather than create it.
   - The flux through the holes is up to 0.58 of U times the hole area; the mean cavity speed is 0.29 U.
2. A wake-driven "knuckle" path over 3 m bends by less than 1 mm against a smooth path and spreads by about 1 cm.
3. Magnus lift is well resolved (Cl from 0.15 at S = 0.25 to 0.46 at S = 2) and steady.
4. D128 → D192 changes Cl at S = 0.5 by −18 % and the S = 0 fluctuation by +50 %. The D64 to D192 study (§4.1.1) shows that mean Cd and Cl converge (extrapolated Cd ≈ 0.56 at S = 0), while the fluctuation statistics scatter by ±50 % with no grid trend. That scatter is most likely the sampling error of one 135 D/U record; the seed and ensemble runs (§4.1, §4.4) will measure it.

## 3. Questions the runs must answer

| # | Question | Decides |
|---|---|---|
| Q1 | Is there a lateral-force *state switch* (bistable or sign-reversing) for POLLEN at Re 2e4 to 5e4, S ≤ 0.1? | Whether a true discontinuous break exists (H1, H2) |
| Q2 | Does the hole orientation give a steady, repeatable side force at S = 0, and how large? | Whether orientation control is needed or useful (H3) |
| Q3 | How does very slow spin (S 0 to 0.1) change the lateral force with time? | Knuckle spin window (H4) |
| Q4 | Do the holes damp or amplify lateral fluctuations compared with a sealed ball? | Open vs sealed (H5) |
| Q5 | What happens during the first 0 to 15 D/U after launch, before the wake is developed? | Real flights last 30 to 55 D/U; the statistics above skip t* < 15 |
| Q6 | Does free rotation (torque-driven spin) change any of Q1 to Q3? | Prescribed vs free spin (H6) |
| Q7 | Are the answers independent of grid, Mach number, precision and collision model? | Validity of everything above |

## 4. Run matrix

All runs use the production geometry and settings unless a column says otherwise:
- POLLEN analytic body, D128, 3 levels;
- fb 1.5, 2.5, 1.5; gb 0.25, 1, 0.25;
- BGK, IBB, FP16, u = 0.05, Re 33057;
- default sampling;
- 150 D/U, statistics over t* ≥ 15.

"Queued" means it is in the run queue now.

### 4.1 Numerical validation (Q7, first priority)

| Run | Change | Purpose | Status |
|---|---|---|---|
| p_grid_d64_btw_S0, p_grid_d96_btw_S0 (+ existing D128, D192) | D = 64 / 96 / 128 / 192 | grid convergence at S = 0 | done (§4.1.1) |
| p_grid_d64_btw_S0.05, p_grid_d96_btw_S0.05 | same at S = 0.05 | grid convergence in the knuckle window | done (§4.1.1) |
| p_mach_d64_btw_S0_u0.1, p_mach_d64_btw_S0_u0.025, p_mach_d96_btw_S0_u0.025 | u = 0.1 / 0.05 / 0.025 | lattice Mach study. At fixed D and Re, dt ∝ u, so this is also the **time-step study** (acoustic scaling) | done (§4.1.1) |
| p_fp32_d64_btw_S0 | FP32 storage | precision | done (§4.1.1) |
| p_reg_d64_btw_S0 | regularised collision | collision model | done (§4.1.1) |
| p_ibb_d128_btw_S0.05_seed1 | seed 1 | seed-to-seed spread of the statistics | queued |
| p_sph_d128_S0.05 | sealed smooth sphere | literature check of the sphere wake (St 0.18 to 0.2 [Lit]) and open-vs-sealed at the same S | running |
| p_box_d128_btw_S0_lat2 | fb lateral 2.0 | lateral blockage (the code notes that 0.7 and 1.2 biased forces) | queued |

Acceptance (all [A], chosen before seeing the results):
- mean Cd within 3 %;
- mean Cl within 0.02 absolute;
- sd Cy and sd Cl within 20 %;
- shedding Strouhal peak within 10 %;
- 3 m miss p95 within 30 %.

The extrapolated (Richardson) value from D64, D96 and D128 is reported if the order is between 1 and 3. Otherwise "not converged" is reported with the spread.

### 4.1.1 Validation results (2026-11-05) [P]

All runs: POLLEN btw, Re 33057, 3 levels, 150 D/U, statistics over t* ≥ 15, one record (seed 0) each. "Fluct. miss" is the p95 at 3 m of the fluctuating part only (key `Cy_fluct` in `data/cfd_knuckle_stats.json`); it excludes the mean side force. Every number is a CFD prediction.

**Grid, S = 0** (BGK, IBB, FP16, u = 0.05)

| D | Cd | Cl mean | sd Cy | sd Cl | Fluct. miss p95 at 3 m |
|---|---|---|---|---|---|
| 64 | 0.640 | 0.030 | 0.023 | 0.020 | 5.5 mm |
| 96 | 0.608 | 0.035 | 0.027 | 0.025 | 7.5 mm |
| 128 | 0.594 | 0.046 | 0.019 | 0.019 | 3.0 mm |
| 192 | 0.581 | 0.040 | 0.029 | 0.018 | 10.4 mm |

**Grid, S = 0.05**

| D | Cd | Cl mean | sd Cy | sd Cl | Fluct. miss p95 at 3 m |
|---|---|---|---|---|---|
| 64 | 0.650 | 0.029 | 0.030 | 0.028 | 9.5 mm |
| 96 | 0.629 | 0.037 | 0.035 | 0.029 | 8.7 mm |
| 128 | 0.611 | 0.036 | 0.031 | 0.025 | 6.0 mm |

**Lattice Mach / time step, collision model, precision** (each against the u = 0.05 BGK FP16 run at the same D)

| Run | Cd | Cl mean | sd Cy | sd Cl | Fluct. miss p95 |
|---|---|---|---|---|---|
| D64 u = 0.025 / 0.05 / 0.1 | 0.645 / 0.640 / 0.645 | 0.030 / 0.030 / 0.027 | 0.019 / 0.023 / 0.017 | 0.018 / 0.020 / 0.016 | 3.6 / 5.5 / 4.6 mm |
| D96 u = 0.025 / 0.05 | 0.611 / 0.608 | 0.052 / 0.035 | 0.026 / 0.027 | 0.018 / 0.025 | 5.7 / 7.5 mm |
| D64 FP32 vs FP16 | 0.644 vs 0.640 | 0.031 vs 0.030 | 0.025 vs 0.023 | 0.018 vs 0.020 | 4.9 vs 5.5 mm |
| D64 regularised vs BGK | 0.642 vs 0.640 | 0.018 vs 0.030 | 0.033 vs 0.023 | 0.023 vs 0.020 | 12.5 vs 5.5 mm |

**Against the acceptance criteria above**

| Criterion | Grid S = 0 (D128 → D192) | Grid S = 0.05 (D96 → D128) | Mach (D64, D96) | FP32 | Regularised |
|---|---|---|---|---|---|
| Cd within 3 % | pass (2.2 %) | pass (2.8 %) | pass (≤ 0.8 %) | pass (0.6 %) | pass (0.2 %) |
| Cl within 0.02 | pass (0.006) | pass (0.001) | pass (≤ 0.017) | pass (0.001) | pass (0.012) |
| sd Cy, sd Cl within 20 % | **fail** for sd Cy (+53 %); sd Cl pass (−6 %) | pass (−12 %, −13 %) | **fail** (sd Cy −16 % / −27 % at D64; sd Cl −27 % at D96) | pass (+7 %, −8 %) | **fail** (sd Cy +41 %) |
| Strouhal peak within 10 % | **fail** (0.175 vs 0.133) | pass (−10 %, borderline) | **fail** (D64 u = 0.1, D96) | **fail** | **fail** (+16 %) |
| Fluct. miss p95 within 30 % | **fail** (3.0 vs 10.4 mm) | **fail** (−31 %) | **fail** at D64 | pass (−11 %) | **fail** (+127 %) |

What this says:
1. **Mean forces converge.** Cd falls monotonically with D. The observed order is 1.26 to 1.35 for each of the triples D64/96/128, D96/128/192 and D64/128/192. The Richardson-extrapolated Cd at S = 0 is **0.56** (0.561 to 0.564 across the three triples). At S = 0.05 the three-grid ratio (1.21) gives no order in 1 to 3, so it is reported as **not converged, spread 0.611 to 0.650**; the D96 → D128 step is still inside 3 %. Mean Cl stays between 0.03 and 0.05 at every resolution.
2. **Fluctuation statistics do not converge in a single record, and do not trend with grid.** sd Cy at S = 0 goes 0.023, 0.027, 0.019, 0.029 for D64 to D192, and the fluctuating miss p95 goes 5.5, 7.5, 3.0, 10.4 mm. Changing only u, the collision model or the storage precision moves these numbers by similar amounts (sd Cy −27 % to +41 %). The likely cause is sampling error: one 135 D/U window holds only about 15 to 20 decorrelation times of the wake azimuth (about 8 D/U [Lit, Rigas 2014]), which gives a standard error of about 15 to 20 % on an sd and more on a p95 (my estimate). The seed run `p_ibb_d128_btw_S0.05_seed1` and the 32-run ensemble (§4.4) will measure this spread directly.
3. **The Strouhal peak is not a usable metric on 135 D/U records.** The picked peak jumps between 0.05 and 0.19 between runs that differ only in u or precision. It should be read from the long records (§4.3).
4. **FP16 storage is adequate.** FP32 changes every statistic by less than the acceptance tolerances, except the Strouhal peak (see 3).
5. **The collision model matters for the fluctuations at D64.** The regularised operator keeps Cd but gives 41 % more sd Cy and 2.3× the fluctuating miss. D64 is the coarsest grid; this comparison should be repeated at D128 before choosing an operator.
6. **For the knuckle question the bounds are what matters.** Across all 12 runs in this section, sd Cy stays within 0.017 to 0.035 and the fluctuating miss p95 at 3 m within 3 to 12.5 mm. That is 1.2 cm at most against a 50.8 cm opening, so none of the decisions in §7 change.

### 4.2 Mechanism runs (Q1 to Q4)

| Set | Runs | Purpose |
|---|---|---|
| Low-spin sweep | S = 0, 0.01, 0.02, 0.05, 0.1 (0.02, 0.05, 0.1 done) at btw | knuckle window: does slow rotation of the hole pattern drive a slowly changing side force? |
| Orientation | S = 0 at btw, hf, o3 (done), o4, o5 (queued), plus 6 more random orientations | steady side force vs orientation (Q2); max/min over orientations |
| Open vs sealed | for S = 0 and 0.05: `body=pollen`, `pball=1` (same outer shell, no holes), `body=sphere` | isolate the hole effect (Q4) |
| Reynolds | Re 20k, 33k, 47k at S = 0 and 0.05 (S = 0 done) | Re sensitivity inside the shooter range |
| Seeds | 4 seeds at S = 0 and 0.05 | spread of statistics |

### 4.3 Long records for switching (Q1)

- Wake switching in sphere wakes appears on a time scale of 10² to 10³ D/U [Lit].
- 150 D/U is too short to see it, and the 1000 D/U the literature needs for converged statistics costs 21 h at D128 (`GPU_OPTIMIZATION.md` §6).

Plan:
- **p_long_d64_S0**: D64, 3 levels, 1000 D/U (about 1.4 h if MLUPs hold [D]). Output: force series, Cy–Cz phase-plane histogram (bimodal = bistable), dwell-time distribution.
- **p_long_d64_S0_sealed**: the same with `pball=1`.
- If a bimodal state appears, repeat at D96 for 500 D/U.

### 4.4 Flight-length ensembles from launch (Q5)

Real flights start with a wake that is not yet developed: the ball leaves the shooter into still air, and 3 m at 7 m/s is about 42 D/U [D]. The statistics above (t* ≥ 15) leave this start-up out.

Plan:
- 16 runs of 55 D/U at D96, seeds 0 to 15, S = 0 and S = 0.05 (32 runs, about 12 h at D96: about 24 s per D/U [D]).
- Statistic: the distribution of lateral deviation at 3 m **from t* = 0**, compared with the developed-wake estimate.
- This is the most direct CFD answer to "how much does a no-spin POLLEN wander in one flight".

### 4.5 Free rotation check (Q6)

Post-processing integration of the measured torque already exists (`free_rot` in the stats JSON):
- at S = 0, the hole pattern turns 0.8° (p95 1.0°) over 3 m [P];
- the ball's inertia (k_I = 0.63) is large compared with the aerodynamic torques.

Prescribed spin is therefore adequate for the knuckle question [D]. The coupled option (§6) is a check, not a prerequisite.

## 5. What every run records

Per csv row (default about 50 rows per D/U), [C]:
- t*;
- Fx, Fy, Fz;
- Tx, Ty, Tz;
- Cd, Cy, Cl, CM.

Per row `# dg` line:
- the flux through each of the 26 holes;
- the force split (outer, inner, hole walls);
- cavity mean |u|/U;
- cavity vorticity;
- cavity angular momentum.

Footer:
- averages over t* ≥ 15;
- the period-2 check;
- the `# runtime_s` line;
- `# prof` lines with `prof=1`.

Field snapshots (`dump`): in 2 of the mechanism runs (S = 0 btw and o3), at 8 times 0.5 D/U apart. They are used for Q-criterion and vorticity iso-surfaces and for the wake angle.

**Add before running these:** ρ in `dump_field`, so pressure fields and surface Cp are available.

Post-processing outputs (`cfd_knuckle_stats.py`):
- mean/sd of the coefficients;
- spectrum peak (Strouhal);
- slow-power fraction (below St 0.05);
- kurtosis of increments (jump test);
- 10-D/U window means;
- path break and miss at 2, 3 and 4 m;
- free-rotation angle;
- spin decay;
- force split.

## 6. Design: free rotation option (not implemented)

```
free=1  I=<kg m^2>  m=<kg>  (with Dmm, U, rho from Re)  integrates  I dω/dt = T  each row, with ω about any axis
```

1. Keep ω as a 3-vector in body units; convert each row's torque to physical units with ρ U² D³ / 2.
2. Update the orientation quaternion each finest step (the wall velocity ω × r is already a kernel argument for +y; it becomes a 3-vector).
3. Re-voxelise when the surface has moved 0.1 cell (existing `revox` logic). For `wall=ibb` recompute q on the GPU (already done at every revox).

Validation:
- a sealed sphere with free=1 must stay at ω ≈ 0 at S = 0;
- `rotpollen` spin-down must match the prescribed-torque integration.

Cost: about 150 lines; no new kernels except a 3-vector wall velocity.

## 7. Decision rules (written before the results)

- **A real discontinuous knuckle exists** only if both:
  - Q1 finds a bimodal Cy/Cz state with dwell times of 5 to 50 D/U and a jump between states larger than 0.1 in C;
  - the flight-length ensemble (4.4) shows deviations above 5 cm at 3 m in at least 5 % of flights.
- **Orientation control is useful** if the orientation-induced steady side force is above 0.03 in Cy with seed-to-seed spread below half of that.
  - Then the steady part is predictable: 1 cm at 3 m for each 0.02 of C [D].
- **Otherwise:** report that the no-spin POLLEN path is a smooth drag path with about 1 cm random wander at 3 m, and that a Magnus curve (S 0.25 to 1) is the only practical "breaking" shot.
