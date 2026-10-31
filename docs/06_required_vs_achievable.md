# 06 - Required vs achievable, Monte Carlo robustness, "score from anywhere" map (HANDOFF §3 Q4, Q6, Q7)

Code: `src/robustness.py`. Phase 3 step 9; deliverables 5 and 8.
Data: `data/req_vs_ach_rows.csv`, `data/req_vs_ach_summary.csv`, `data/robust_map_fractions.csv`,
`data/robust_map_Pd.csv`, `data/robust_mc.csv`.
Figures: `figures/req_vs_ach_v_by_d.png`, `figures/req_vs_ach_v_spin.png`, `figures/map_field_hood.png`,
`figures/map_field_configs.png`, `figures/map_P_vs_d.png`.
Reproduce: `python -m src.robustness --steps req,map,mc --workers 3 --n 1500`. The map tables took about
25 min on 3 workers (16 jobs of 3.5-13.5 min each). They are cached per job in `<tmp>/pm001_robustness_cache/`
(`robust_map_job_*.npy`, then `robust_map_tables.npz`), so an interrupted run resumes. The Monte Carlo (n = 1500
shots per scenario, 62 scenario rows) then takes about 4 min on 4 workers. Memory per map worker grows with
`block` (default 500). On a 16 GB machine shared with other jobs, 6 workers failed with an allocation error
and 3 workers with `OPENBLAS_NUM_THREADS=1` succeeded (see section 5).

Provenance labels follow docs/INTERFACES.md: **confirmed**, **user**, **assumed**, **derived**, **predicted**.
**Every probability, gap and fraction in this file is predicted.** It is a model output built from:

- assumed aerodynamics (`data/aero_params.json`, docs/02_aero.md; no POLLEN measurement exists);
- the CAD-derived HIVE geometry (docs/01; tilt 30 deg confirmed, derived tipped bounds 28.80-31.77 deg). Section 1 uses the
  PM-019 re-sweep: the 3D CELL (`src/cell3d.py`) at air density 1.2041 kg/m^3, the same model as the live
  solver in `viz/explorer/`. Sections 2 and 3 (Monte Carlo and the field map) were made before PM-019 with
  the 2D section model, rho 1.20 and tilt bounds 28.5-31.5 deg, and have not been re-run;
- the predicted launcher envelope (`data/launch_envelope.json`, docs/04);
- assumed release-error and disturbance sets (section 2.1).

Nothing here has been checked against a real shot. The channel is **clean air-only entry** (hypothesis A of
HANDOFF §0, as in docs/03). Rim-assisted entry (hypothesis B) is not credited, so where it works in reality
these numbers are pessimistic. Written 2026-10-30.

**Summary (all predicted):**

- **Q4, required vs achievable.** The binding gap is **exit speed, not spin**. Both launchers spin the ball
  past Cl saturation, so the spin requirement is met wherever the speed is.
  - The hood (cap 8.91 m/s) reaches every clean window on both sides.
  - The passive roller (cap 5.03 m/s) reaches every favourable-side window. It is **0.57-2.07 m/s short on
    the whole unfavourable side** at h 0.737, S 1, Cl nominal (0.50-2.56 m/s across the three roller variants
    and the Cl bounds; PM-019 3D cell).
- **Q6, robustness.** The best unfavourable-side aim (d 0.81 m, v 7.25 m/s, elevation 79.7 deg, hood) scores
  **p = 0.30 [0.28, 0.33]** at nominal errors (Wilson 95 %, n = 1500). It drops to 0.05-0.10 if the real Cl
  differs from the tuned one, and to 0.11 in 1 m/s wind. The best favourable-side aim (d 0.74, v 4.3, 81 deg)
  scores **0.996 [0.991, 0.998]**, 0.84 with loose release errors, and stays ≥ 0.98 under every other
  disturbance tried.
- **Q7, "score from anywhere".** **Not plausible** with clean entry.
  - **Hood:** about 26 % of the legal floor area reaches ≥ 50 % predicted clean-entry probability.
  - **Roller:** about 23 %.
  - In both cases every such position is on the favourable (mouth-facing) half. No unfavourable-side
    position reaches 50 % for any configuration, with or without spin.

## 1. Required vs achievable (Q4)

### 1.1 Method

- **Required sets.** These come from `data/clean_feasibility_map.csv` (docs/03). For each aero case, geometry
  (unfav at tilt 28.80 / 30 / 31.77, fav at tilt 30; PM-019 3D cell), release height h and distance d, the clean window gives:
  - the range of required exit speed v and elevation;
  - the required spin, in rpm = S·v/R·60/2π.

  Only the `v_cap = 11` rows are used. Vacuum, topspin and the Cd/k variants are left out of the overlay
  (they stay in docs/03).
- **Achievable sets** (predicted, `data/launch_envelope.json`) come from 7 configurations:

  | Configuration | Predicted v cap (m/s) |
  |---|---|
  | hood_nominal | 8.91 |
  | hood_slick_short | 7.34 |
  | hood_soft_ball | 5.45 |
  | hood_stiff_ball_8mm | 13.88 |
  | roller_nominal_rest | 5.03 |
  | roller_heavy_rest | 5.11 |
  | roller_light_rest | 4.95 |

  Each configuration gives the v cap over wheel rpm 1000-6000, the exit spin and the S band. Hood S is
  1.03-1.27 and passive-roller S is 0.91-1.17.
- **Spin equivalence (derived).** Cl = min(c1·S, Cl_max) saturates at S_sat = Cl_max/c1:

  | Cl set | S_sat |
  |---|---|
  | nominal | 0.714 |
  | low | 0.667 |
  | high | 0.50 |

  A launcher S at or above S_sat therefore gives exactly the same lift as any required S at or above S_sat
  (`S_equivalent`). The **S = 0 "no spin" case cannot be produced by either launcher**, so it is a
  counterfactual. Below S_sat, a launcher that spins *more* than required lands on a different trajectory.
  The S = 0.5 / Cl-low rows show this as `spin_gap`. This is one concrete case where more spin does not help
  and only changes the shot.
- **Status per row:**
  - **reachable**: the v window overlaps [v_min, v_cap] and S is equivalent;
  - **speed_gap**: the cap is below the slowest clean v. The gap is given in m/s and as `rpm_gap_ideal`,
    the extra wheel rpm on the predicted hood_ideal slope of 2.35e-3 m/s per rpm (derived);
  - **spin_gap**: S is not equivalent. `S_gap` is the S difference.

  `spin_rpm_gap` is the launcher spin at the required v minus the minimum required spin.

### 1.2 Results (predicted, h = 0.737 m, backspin S = 1 / Cl nominal unless stated; PM-019 3D cell, rho 1.2041)

See `figures/req_vs_ach_v_by_d.png` (the required v extent per d against the launcher caps) and
`figures/req_vs_ach_v_spin.png` (the required (v, spin) region against the launcher (v, spin) curves). The
full table is `data/req_vs_ach_rows.csv` and the per-launcher summary is `data/req_vs_ach_summary.csv`.

**Required sets, unfavourable side (mouth faces away), tilt 30:**

- A clean window exists only for d ≥ 0.75 m (21 of the 25 d steps from 0.55 to 1.75).
- The slowest clean shot needs:

  | d (m) | Slowest clean v (m/s) |
  |---|---|
  | 0.75 | 7.1 |
  | 0.80 | 5.6 |
  | 1.20 | 6.1 |
  | 1.70 | 6.8 |

- Elevation is 70-82.5 deg.
- The window is **sparse**: 46-91 clean (v, elevation) cells per d on the 0.1 m/s × 0.25 deg grid.
- At tilt 28.80 the minimum v changes by -0.2 to +0.5 m/s per d (median +0.1). At 31.77 it changes by
  -0.4 to +0.1 m/s (median -0.1).
- No-spin twin (S = 0, drag only, counterfactual): the minimum v is similar, 5.6-6.9 m/s.

**Required sets, favourable side (mouth faces the shooter):**

- A window exists for d ≥ 0.60 m.
- The minimum v is 3.7-4.7 m/s.
- Elevation runs from 30-85 deg at d = 1.75 down to 85-87 deg at d = 0.60.
- The window has 270-2110 clean cells per d, so it is 5-40 times larger than on the unfavourable side.

**Overlay (predicted):**

| Launcher (predicted cap) | Unfav, S1 Cl nominal | Fav, S1 Cl nominal | No-spin case |
|---|---|---|---|
| hood_nominal (8.91 m/s, S 1.06) | reachable at all 21 d (0.75-1.75). Wheel rpm at the slowest clean v is 2410-3040, with 90-115 rpm more spin than S = 1 needs (irrelevant, Cl saturated) | reachable, all 24 d | **spin_gap**: S = 0 cannot be made (S_gap 1.06) |
| hood_slick_short (7.34), hood_stiff_ball_8mm (13.88) | reachable, all 21 d | reachable | spin_gap |
| hood_soft_ball (5.45) | **speed_gap** at all 21 d: 0.15-1.65 m/s (Cl low 0.15-1.45; Cl high 0.25-2.05) | reachable | spin_gap |
| roller_nominal_rest (5.03, S 0.97-1.11) | **speed_gap** at all 21 d: **0.57 m/s at d 0.80, 0.67-0.77 at d 0.85-1.0, 1.07-1.17 at d 1.15-1.25, 1.67-1.77 at d 1.6-1.75, 2.07 at d 0.75**. In wheel-rpm terms on the hood_ideal slope that is +240 to +880 rpm. Across the Cl bounds the gap is 0.57-2.47 m/s | reachable, all 24 d | spin_gap |
| roller_heavy_rest (5.11) / roller_light_rest (4.95) | speed_gap 0.50-2.00 / 0.66-2.16 m/s | reachable | spin_gap |

Reading the table:

- The **spin requirement is met by both launchers** for every backspin case with S ≥ S_sat. The model has no
  required-spin gap for the backspin cases at S ≥ S_sat. The binding gap is **exit speed**.
- On the unfavourable side the passive roller is about 0.6-2 m/s short. The hood has a margin of about
  2-3 m/s above the slowest clean shot.
- The passive roller's cap is grip- and rest-limited (docs/04), not rpm-limited. The rpm gap is therefore
  only an equivalent figure: adding wheel rpm does not lift the roller cap in the model.
- A no-spin shot is not a launcher option at all. Getting one would need a different mechanism, for example
  a dual-wheel launcher, which HANDOFF §5 excludes here.
- Spin below saturation is a different case. With the Cl-low set and a required S = 0.5, the hood's S ≈ 1.06
  gives a *different* trajectory (spin_gap, S_gap 0.56). Its own window (the S1 Cl-low row) is still reachable,
  so the extra spin moves the window rather than enlarging it.
- Release height matters on the unfavourable side. At h = 0.2-0.35 the first clean d moves out to 0.85 m
  (summary csv).
- These are window *extents*. They say nothing about how well a shot can stay inside a 46-91-cell window.
  Section 2 covers that.

## 2. Monte Carlo robustness (Q6)

**Model note:** sections 2 and 3 are pre-PM-019 (2D section model, rho 1.20, tilt bounds 28.5 / 31.5 deg).
`src/robustness.py` MC and map were not re-run in PM-019, so their numbers do not yet reflect the 3D cell.

### 2.1 Error and disturbance model (all assumed)

There is **no measured repeatability** for any FTC launcher with this ball. HANDOFF §5 says one shot does not
show repeatability. Every spread below is therefore an assumption, chosen as plausible for a closed-loop
flywheel shooter, and it is varied in the scenarios.

**Release errors** (Gaussian, per shot; `ERR_SETS`):

| Set | σ_v / v | σ elevation | σ azimuth | σ d | σ y (lateral) |
|---|---|---|---|---|---|
| tight | 0.5 % | 0.15 deg | 0.25 deg | 10 mm | 10 mm |
| **nominal** | **1.5 %** | **0.40 deg** | **0.50 deg** | **25 mm** | **25 mm** |
| loose | 3.0 % | 0.80 deg | 1.00 deg | 50 mm | 50 mm |

**Physical scatter** (per shot; `PHYS`):

- Release height: σ 5 mm.
- Ball mass: σ 0.5 g, clipped to the assumed 23.5-26.5 g bounds of aero_params.
- Ball radius: σ 0.25 mm, clipped to 35.0-36.0 mm.
- Cd: ±5 % (1σ) ball to ball. Cl: ±10 % (1σ) ball to ball.
- Spin: S uniform over the predicted hood band 1.03-1.27.
- Wind: constant per shot, σ 0.30 m/s per horizontal component (indoor drafts and HVAC; the venue condition
  is unknown).
- HIVE tilt: σ 0.75 deg, clipped to the derived bounds (28.5-31.5 when the numbers below were made; the code now clips at 28.80-31.77, not re-run).
- Pivot height: σ 5 mm, clipped to 1.091-1.142 m.
- HIVE placement along x: σ 10 mm.

**Scenarios** (each changes one thing from "nominal"):

- **release_error_only**: no physical scatter, no wind, nominal HIVE.
- **tight_release** and **loose_release**.
- **no_wind** and **wind_1.0**: wind σ 1.0 m/s per component.
- **hive_tilt_28.5_fixed** and **hive_tilt_31.5_fixed**.
- **sag_open_loop_0to4pct**: every shot loses 0-4 % of exit speed, uniform. This models battery sag with no
  speed loop.
- **sag_rapid_fire_0to50pct_drop**: the wheel has recovered only partway from the previous shot. The rpm
  deficit is uniform from 0 to 50 % of the predicted per-shot rpm drop (docs/04), converted to exit speed
  with the predicted dv/drpm.
- **Cl_low_transfer / Cl_high_transfer, Cd_low/high_transfer, k_high_transfer**: the aim is tuned for the
  nominal aero, but the true ball follows the bound. This is model error with no re-tuning on the field.
- **Cl_low_retuned / Cl_high_retuned**: the aim is re-selected for the bound. This is the best case after
  calibration on the field.

**Engine:**

- A vectorised 3D RK4 integrator, dt = 2 ms.
- Same equations as `flight.simulate`: drag and Magnus on v_rel = v - wind, with exponential spin decay.
- A unit test checks it against `flight.simulate` with wind and spin. Agreement is better than 1e-4 m (it was
  1.2e-7 m on the reference run).
- Each shot is classified **exactly**:
  - A per-shot `hive.Hive` is built (tilt, pivot height, ball radius, and the pentagon roof drop at that
    shot's lateral offset at the gate), mirrored for the favourable side.
  - The shot is classified with `Hive.classify_path` on its in-plane path.
  - If the lateral offset at the gate exceeds 0.254 - R = 0.2185 m (derived), the shot is a side-wall hit.

**Aims:**

- An aim is the (d, v, elevation) cell with the highest smoothed clean probability from the map tables
  (section 3.1), using the nominal release errors at ψ = 0 and h = 0.737 m. It is limited to v at or below
  the hardware cap.
- n = 1500 shots per scenario. The 95 % interval is Wilson's.

### 2.2 Results

Full table: `data/robust_mc.csv`. It has the aim, k/n, p, the Wilson 95 % interval, the standard deviation of
the lateral offset at the gate, and the top four outcomes per scenario. All values are predicted, with
n = 1500 per row.

**Aims** (from the smoothed map tables, h = 0.737 m, hood unless stated):

| Aim | Side | d (m) | v (m/s) | Elevation (deg) | Smoothed P_kin |
|---|---|---|---|---|---|
| unfav_best_hood_spin | unfav | 0.81 | 7.25 | 79.7 | 0.41 |
| unfav_d1.15_hood_spin (mid-field) | unfav | 1.15 | 8.35 | 79.3 | 0.34 |
| fav_best_hood_spin | fav | 0.74 | 4.30 | 81.0 | 1.00 |
| fav_best_roller_spin | fav | 0.74 | 4.30 | 81.0 | 1.00 (same aim; 4.3 m/s is under both caps) |
| fav_d0.80_hood_spin | fav | 0.80 | 4.10 | 77.25 | 1.00 |
| fav_d1.55_hood_spin (far, flatter) | fav | 1.55 | 4.65 | 56.25 | 1.00 |

The roller has no unfavourable-side aim, because no clean cell exists at v ≤ 5.03 m/s there.

**Best unfavourable-side aim (unfav_best_hood_spin), p_clean with Wilson 95 %:**

| Scenario | p | 95 % interval | Main failure modes |
|---|---|---|---|
| nominal | **0.303** | [0.281, 0.327] | roof outer face 545, clean 455, floor 214, miss 153 |
| tight_release | 0.411 | [0.386, 0.436] | roof outer, floor |
| loose_release | 0.157 | [0.139, 0.176] | roof outer 653, miss 281 |
| release_error_only | 0.362 | [0.338, 0.387] | roof outer, floor |
| no_wind | 0.348 | [0.324, 0.373] | |
| wind_1.0 (σ 1 m/s) | 0.111 | [0.096, 0.128] | 162 side-wall hits; lateral sd at gate 0.16 m |
| hive_tilt_28.5_fixed | 0.247 | [0.226, 0.269] | |
| hive_tilt_31.5_fixed | 0.316 | [0.293, 0.340] | |
| sag_open_loop_0to4pct | 0.241 | [0.220, 0.264] | roof outer 835 (short shots) |
| sag_rapid_fire_0to50pct_drop | 0.237 | [0.217, 0.260] | roof outer 889 |
| Cl_low_transfer | **0.097** | [0.083, 0.113] | miss 977 (shot falls short of the mouth) |
| Cl_high_transfer | **0.054** | [0.044, 0.067] | roof outer 1338 |
| Cd_low_transfer | 0.281 | [0.259, 0.305] | |
| Cd_high_transfer | 0.207 | [0.187, 0.228] | |
| k_high_transfer | 0.293 | [0.270, 0.316] | |
| Cl_low_retuned | 0.325 | [0.301, 0.349] | |
| Cl_high_retuned | 0.269 | [0.248, 0.292] | |
| no spin (S = 0, counterfactual), nominal | 0.317 | [0.294, 0.341] | |
| no spin, release_error_only | 0.411 | [0.387, 0.436] | |

The mid-field unfavourable aim (d 1.15) is worse:

| Scenario | p | 95 % interval |
|---|---|---|
| nominal | 0.220 | [0.200, 0.242] |
| release_error_only | 0.331 | [0.307, 0.355] |
| loose_release | 0.123 | [0.107, 0.140] |
| Cl_low_transfer | 0.042 | [0.033, 0.053] |
| Cl_high_transfer | 0.027 | [0.020, 0.036] |
| sag_rapid_fire | 0.176 | [0.158, 0.196] |

**Best favourable-side aim (fav_best_hood_spin):**

| Scenario | p | 95 % interval |
|---|---|---|
| nominal | **0.996** | [0.991, 0.998] |
| tight_release | 1.000 | [0.997, 1.000] |
| loose_release | **0.842** | [0.823, 0.860] |
| release_error_only / no_wind | 0.995 / 0.996 | [0.990, 0.998] / [0.991, 0.998] |
| wind_1.0 | 0.987 | [0.980, 0.991] |
| hive_tilt_28.5 / 31.5 fixed | 0.989 / 0.996 | [0.982, 0.993] / [0.991, 0.998] |
| sag_open_loop / sag_rapid_fire | 0.993 / 0.985 | [0.987, 0.996] / [0.977, 0.990] |
| Cl low / high transfer | 0.994 / 0.996 | [0.989, 0.997] / [0.991, 0.998] |
| Cd low / high, k high transfer | 0.995 / 0.994 / 0.995 | all within [0.989, 0.997] |
| Cl low / high retuned | 0.999 / 0.999 | [0.996, 1.000] / [0.995, 1.000] |
| no spin (counterfactual), nominal | 0.994 | [0.989, 0.997] |

The other favourable-side aims:

| Aim | Scenario | p | 95 % interval |
|---|---|---|---|
| fav_best_roller_spin | nominal | 0.996 | [0.991, 0.998] |
| | loose_release | 0.842 | [0.823, 0.860] |
| | sag_rapid_fire | 0.991 | [0.985, 0.995] |
| fav_d0.80_hood_spin | nominal | 0.998 | [0.994, 0.999] |
| | loose_release | 0.897 | [0.881, 0.912] |
| | sag_rapid_fire | 0.987 | [0.980, 0.992] |
| fav_d1.55_hood_spin | nominal | 0.997 | [0.993, 0.999] |
| | loose_release | 0.885 | [0.868, 0.901] |
| | Cl_low_transfer | 0.979 | [0.970, 0.985] |
| | **sag_rapid_fire** | **0.768** | [0.746, 0.789], floor 230, lower lip 118 |

**Reading the Monte Carlo (predicted):**

- **Unfavourable side: fragile.** The best aim makes about 3 of 10 shots at nominal errors. Even with tight
  errors (0.5 % speed, 0.15 deg) it reaches only about 4 of 10. The window is a thin band between the roof
  outer face (too high or too fast) and the floor/miss (too low or too slow), and the nominal release errors
  are already as wide as that band.
- **Aero model error is the largest single risk on the unfavourable side.** If the real Cl is at the low or
  high bound and the aim is not re-tuned, p falls to 0.05-0.10. Re-tuning on the field recovers 0.27-0.33.
  This number therefore depends on field calibration, and that cannot be inferred from one shot (HANDOFF §5).
- **Wind and speed sag matter on the unfavourable side.** 1 m/s wind (σ) cuts p to 0.11. A 0-4 % open-loop
  sag or a partly recovered wheel cuts it to about 0.24.
- **Favourable side: robust.** It stays ≥ 0.98 under every single disturbance except loose release errors
  (0.84-0.90). The exception is the flatter long shot at d 1.55: rapid fire (0-50 % of the per-shot rpm drop
  not recovered) cuts it to 0.77. Wait for wheel recovery on far favourable shots.
- **Spin.** The no-spin counterfactual scores the same as or slightly higher than the spun shot (0.317 vs
  0.303 unfav; 0.994 vs 0.996 fav). More spin does not improve clean entry in this model. The launchers'
  spin is simply a by-product that, being past Cl saturation, does no harm once the aim is tuned for it.

## 3. Field feasibility map: can it "score from anywhere"? (Q7)

### 3.1 Method

**Field frame (red-HIVE frame).**

- x is the tipping-plane axis. The inner field wall is at |x| = 1.8009 m (CAD-derived).
- y runs along the pivot axis. The field spans y from -1.477 to 2.125 m, because the red HIVE centre sits
  0.324 m toward red (derived from hive_geometry.json).
- **Legal release points** (assumed): the robot must be at least 0.10 m inside the wall, and points within
  0.05 m of the A-frame base (|x| < 0.49, y from -0.30 to 0.95, confirmed TU07 9.6 plus CAD) are excluded.
  This gives 10.49 m² of legal area at 0.05 m resolution (derived). Of that, 8.11 m² has |x| ≥ 0.55 m.
- There is **no launch zone** in TU07, so the whole field counts.
- Points with |x| < 0.55 m sit under or next to the HIVE. They are outside the swept d range and count as P = 0.
- The other alliance's HIVE cells (y 0.39-0.90) block part of the sight lines. They are **not modelled**.
  The fractions are also given with every point at y > 0.90 removed (`_excl_otherhive`), as a lower check.

**Per release point:**

- d = |x| is the in-plane distance from the pivot plane. The side is favourable when the shooter is on the
  mouth side of the pose.
- The shooter aims at the gate centre with azimuth ψ = atan(|y| / (d ± x_gate)), where x_gate = 0.401 m
  (derived).
- The in-plane projection of an oblique shot is the 2D path with its horizontal coordinate scaled by cos ψ.
  This is exact for obstacles extruded along y with no wind, and a unit test checks it.
- The pentagon roof drops toward the CELL side walls. The section is taken at an **assumed** effective lateral
  offset s_eff = min(0.3·tan ψ, 0.2) m. The centre section (offset 0) is run as a sensitivity case.
- The clean mask on (d, v, elevation) is computed for ψ in 0-60 deg in 10-deg steps, then convolved with the
  nominal release-error Gaussian (σ_d, σ_v, σ_elevation). σ_v is relative, applied piecewise at 3.5, 6 and
  8.5 m/s.
- P_kin(d, ψ) is the **maximum over v ≤ hardware cap and over all elevations** of that smoothed probability.
  This means the robot is assumed to pick the best aim for its position.
- Lateral factor: erf(w_lat / (√2·σ_lat)), where σ_lat² = (L·σ_ψ)² + σ_y² + σ_drift².
  - L is the horizontal range to the gate.
  - σ_drift is the lateral drift from the nominal wind σ of 0.30 m/s. One representative steep shot
    (v 8.6 m/s, elevation 83 deg) drifts 0.205 m per 1 m/s of crosswind (derived), so σ_drift = 0.062 m.
  - w_lat is the **assumed** usable half-width at the gate: primary 0.15 m, bounds 0.10 and 0.2185 m. The
    upper bound is the CELL half-width minus R. The roof drop makes the edges of the opening less usable.
- P(position) = P_kin · lateral factor. Beyond ψ = 60 deg it is set to 0, because oblique entry through the
  side of the 0.508 m opening is not represented in 2D.

**Configurations:**

- Hardware: hood (v ≤ 8.91 m/s) or passive roller (v ≤ 5.03 m/s), both predicted.
- Aero: backspin S1 (equivalent to the launchers' S of 1.03-1.27, since Cl is saturated) with the Cl low,
  nominal and high sets; or no spin (S = 0, counterfactual).
- Both poses: pose_pos and pose_neg (mirror).
- Thresholds: P ≥ 50 / 80 / 90 %.

### 3.2 Results

Full table: `data/robust_map_fractions.csv` (64 rows: 8 configurations × 2 poses × 3 w_lat values plus the
centre-section case). P(d) curves: `data/robust_map_Pd.csv`. Figures:

- `figures/map_field_hood.png`: the field P map, hood, Cl nominal, both poses;
- `figures/map_field_configs.png`: hood and roller × spin and no spin;
- `figures/map_P_vs_d.png`: P_kin against d per ψ, both sides.

**Field accounting** (derived, both poses):

| Part of the legal area | Share |
|---|---|
| Total legal area | 10.49 m² |
| Near / under the HIVE, \|x\| < 0.55 m (not evaluated, P = 0) | 22.7 % |
| Oblique, ψ > 60 deg (not evaluated, P = 0) | 12.3 % |
| Evaluated | about 65 % |

**Fractions of the whole legal area with predicted P ≥ X** (pose_pos, s_eff section, w_lat 0.15 m, nominal
errors; pose_neg is within 1 percentage point):

| Configuration | ≥ 50 % | ≥ 80 % | ≥ 90 % | Unfav half ≥ 50 % | Fav half ≥ 50 / 80 / 90 % | Max P unfav |
|---|---|---|---|---|---|---|
| hood, backspin, Cl nominal | **26.1 %** | 25.8 % | 25.4 % | **0 %** | 52.7 / 52.0 / 51.4 % | 0.39 |
| hood, backspin, Cl low | 26.1 % | 25.8 % | 25.4 % | 0 % | 52.7 / 52.0 / 51.4 % | 0.40 |
| hood, backspin, Cl high | 26.1 % | 25.8 % | 25.4 % | 0 % | 52.7 / 52.0 / 51.3 % | 0.37 |
| hood, no spin (counterfactual) | 26.1 % | 25.8 % | 25.4 % | 0 % | 52.7 / 52.0 / 51.4 % | 0.41 |
| roller, backspin, Cl nominal | **23.3 %** | 21.0 % | 19.6 % | **0 %** | 47.0 / 42.4 / 39.6 % | 0 (no clean v ≤ cap) |
| roller, backspin, Cl low / high | 23.1 / 23.3 % | 20.9 / 21.3 % | 19.5 / 19.8 % | 0 % | 46.7-47.2 / 42.2-43.1 / 39.4-39.9 % | 0 |
| roller, no spin (counterfactual) | 22.9 % | 20.7 % | 19.4 % | 0 % | 46.2 / 41.8 / 39.2 % | 0 |

**The same fractions as a share of the *evaluated* favourable-side area** (that is, where the model can
answer at all):

| Hardware | ≥ 50 % | ≥ 80 % | ≥ 90 % |
|---|---|---|---|
| hood | 99-100 % | 98-99 % | 97 % |
| roller | 87-89 % | 79-81 % | 74-76 % |

The roller loses the far and oblique favourable positions: a longer horizontal range needs more than its
5.03 m/s cap.

**Sensitivity (predicted):**

- **Usable gate half-width w_lat** (assumed):
  - At w_lat 0.10 m, no position reaches 90 %. The lateral factor caps at 0.867, because σ_lat is set by the
    assumed wind drift (0.062 m) plus σ_y (0.025 m) even at short range.
  - The ≥ 50 % and ≥ 80 % fractions barely change: hood 26.1 / 25.4 %, roller 22.8 / 19.5 %.
  - At w_lat 0.2185 m (the full CELL half-width minus R), the maximum is 0.999 and the fractions match the
    0.15 m case to within 0.3 percentage points.
- **Roof section.** With the centre section (no roof drop for oblique shots, optimistic), the hood's
  unfavourable maximum rises to 0.57. Then 2.0-2.8 % of the unfavourable half reaches ≥ 50 % (but none ≥ 80 %),
  and the hood total becomes 27.1-27.5 %. The roller's unfavourable side stays at 0.
- **Other alliance's HIVE.** Dropping every point at y > 0.90 m as possibly blocked gives a lower check of
  about 20.9 % (hood) and 20.5 % (roller) of the whole legal area at ≥ 50 %.
- **Unfavourable P(d) at ψ = 0** (hood, kinematic only, before the lateral factor):
  - It peaks at 0.41 at d 0.81 m (v 7.25, elevation 79.7) and falls to about 0.27 at d 1.7 m.
  - It is about 0.2 at ψ = 30-40 deg.
- **Favourable P_kin** is about 1.0 for d = 0.70-1.75 m and falls off below d 0.65 m. The drop at d > 1.75 m
  in `map_P_vs_d.png` is a grid-edge artefact beyond the legal maximum d of 1.70 m.

## 4. Plain answer

**"Score from anywhere" is not plausible (predicted).** This holds with either launcher, with or without spin,
for clean air-only entry.

What the model predicts:

- **The favourable (mouth-facing) half is a reliable scoring zone for the hood.** Nearly every evaluated
  position there is ≥ 90 %. That is about 26 % of the whole legal floor area, or about 21 % if positions that
  the other HIVE may block are dropped. The passive roller covers less of it (about 23 %, ≥ 50 %), because its
  speed cap cuts off the far and oblique favourable positions.
- **The unfavourable half is a low-percentage zone for the hood and a no-score zone for the roller.**
  - The best hood shot there is about 0.30 [0.28, 0.33] per shot at nominal errors, and about 0.41 with very
    tight errors.
  - It drops to 0.05-0.10 if the real lift coefficient differs from the tuned one.
  - No unfavourable position reaches 50 % in the main model.
- **About 35 % of the legal area is not evaluated** (under or next to the HIVE, or at ψ > 60 deg). It is
  counted as P = 0. Treat that as "not shown", not as "shown impossible". Whether clean entry works there is not
  shown either way.

**Which physics limits it:**

1. **Entry geometry on the unfavourable side.** The shot must clear the roof outer face and then drop into a
   mouth that faces away, so only a steep (70-82.5 deg), fast (5.6-7.1 m/s minimum) band works. That band is
   46-91 grid cells wide per d, against 270-2110 on the favourable side (PM-019 3D cell). This is a geometry limit, and no
   amount of spin removes it.
2. **Exit-speed cap.** The roller's grip- and rest-limited cap (about 5.0 m/s, predicted) is below the slowest
   clean unfavourable shot at every d. Spin is not the gap.
3. **Repeatability against a thin window.** Release errors of 1.5 % in speed and 0.4 deg in elevation already
   span the unfavourable band. Battery sag and rapid fire add speed error, which hurts long flat favourable shots
   too (d 1.55: 0.77 under rapid fire).
4. **Aerodynamic model error.** Cl and Cd are assumed, not measured. A ±Cl error moves the unfavourable
   aim out of its window, so field calibration is needed before any unfavourable shot is planned.
5. **Lateral scatter (wind drift).** A 0.3 m/s draft gives about 6 cm of lateral spread at the gate on a steep
   shot. That alone caps P below 0.87 if only ±0.10 m of the 0.508 m opening is usable, and 1 m/s drafts
   produce side-wall hits.

More spin is not a lever here. Both launchers already exceed Cl saturation, and the no-spin counterfactual
scores the same or slightly better.

## 5. Limits and open questions

- **Nothing is measured.**
  - The aerodynamics (Cd, Cl slope and saturation, spin decay) are assumed.
  - The launcher caps are predicted.
  - The release-error sets are assumed.
  - No real shot has been compared with any number here. Repeatability cannot be inferred from one shot.
    It needs about 100 shots per aim to narrow a Wilson interval to about ±0.1 (derived, p near 0.5).
- **Clean entry only.** Rim- or lip-assisted entries (hypothesis B) are not credited. If they work in reality,
  every probability here is a lower bound for "scores", but not for "enters cleanly".
- **Assumed map parameters.**
  - The roof section offset s_eff = min(0.3·tan ψ, 0.2) m. The centre section is the optimistic bound.
  - The usable half-width w_lat: 0.15 m, bounded by 0.10 and 0.2185 m.
  - The cut-off ψ ≤ 60 deg.
  - The near-HIVE exclusion |x| < 0.55 m.
  - The legal-position margins (0.10 m from the wall, 0.05 m from the A-frame).
  - The wind σ of 0.30 m/s. The venue condition is unknown.
- **Unevaluated regions.** Oblique entry beyond ψ = 60 deg (through the side of the opening) and positions
  under or next to the HIVE are not modelled. They are set to P = 0, which is about 35 % of the legal area.
- **Other HIVE.** Its blocking of sight lines is not modelled, only bounded by the y > 0.90 m exclusion.
- **The map uses nominal errors only.** Tight and loose errors are covered only by the Monte Carlo at selected
  aims. The map's lateral factor is a Gaussian approximation. The Monte Carlo is the exact per-shot check, and
  it agrees within the assumptions: 0.30 MC against 0.39 map at the unfavourable aim (the MC adds physical
  scatter), and 0.996 against 0.976.
- **Release height.** The map and the Monte Carlo use h = 0.737 m. Lower release heights shift the first clean
  unfavourable d out to 0.85 m (section 1.2).
- **Bug reported, not edited (owner: feasibility module).** `src/feasibility.py` `evaluate_gate` sizes its
  chunks as `chunk_elems // L` using the window length of the *first* (shortest) candidate in the sorted batch.
  Longer-window candidates in the same chunk can then far exceed `chunk_elems`. For example, a
  (221303, 471) float64 array, 795 MiB, raised ArrayMemoryError on the first map run. This module works around
  it with `block=500` and `chunk_elems=2e6` in `clean_masks`. The results are unaffected. A fix would size
  each chunk by the longest L it contains.

**Open questions:**

1. Measured Cd and Cl(S) for the POLLEN ball. A pickleball is not a valid proxy.
2. Measured release repeatability (σ_v, σ_elevation) of the chosen launcher over many shots.
3. Venue air movement.
4. Whether rim-assisted entry is legal and reliable, which would change the unfavourable-side answer.
5. A 3D model of oblique entry and of the other HIVE.
