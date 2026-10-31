# 02 — POLLEN aerodynamics: literature bounds (HANDOFF §4A)

Status: every aerodynamic coefficient here is **assumed (literature-bounded)**. None of it is a POLLEN measurement. The machine-readable values are in `research/params_lit.json`, the default for new runs, and this file explains where they come from. `data/aero_params.json` is the legacy first-pass set (Cd 0.35 / 0.48 / 0.65, Cl low 0.15 / 0.10, k 0.01 / 0.05 / 0.30 s⁻¹, no floor set). Written 2026-10-30; sets updated to `research/params_lit.json` 2026-10-31.

Provenance labels: **confirmed** (official source), **derived** (computed, with the formula given, or read from a cited figure), **assumed**, **user**.

## 1. What POLLEN physically is

| Quantity | Value | Label / source |
|---|---|---|
| Description | ~2.8 in (7.1 cm) Gopher ResisDent polyethylene ball, am-5851_yellow, "not perfectly spherical and may vary in size" | confirmed: Manual TU07 §9.8 |
| Mass | 0.055 lb = 24.95 g (bounds 23.5–27.5 g) | confirmed: AndyMark spec. Bounds are assumed; high bound raised 26.5 → 27.5 g to cover the 27.2 g vendor listing weight (research/params_lit.json). data/aero_params.json still holds 26.5 g |
| Outer radius | 35.5 mm nominal (CAD 1.40 in = 35.56 mm; bounds 35.0–36.0 mm) | confirmed: manual + AndyMark CAD. Bounds are assumed |
| Wall | 0.07 in = 1.78 mm (CAD inner sphere R 1.33 in) | confirmed: AndyMark STEP + layout print |
| Holes | 26 through-holes, Ø0.44 in = 11.2 mm (print reads ".4 (26)") | confirmed: STEP (26 circles, r = 0.22 in) |
| Open area | ≈16% of the surface; d_hole/D ≈ 0.157 | derived |
| CAD mass at HDPE density (950 kg/m³) | ≈21.2 g, lower than the 24.95 g spec | derived. Real balls are thicker or heavier than the CAD. The implied uniform wall is ≈2.1 mm |

For geometry, POLLEN is closest to an **indoor 26-hole pickleball** (74 mm, 22–26.5 g, 26 large holes) and to a floorball. It is not like a wiffle ball, which has 8 slots on one hemisphere only.

### Moment of inertia I_b (derived)
I took a Monte-Carlo integral of the CAD solid: a 1.40/1.33 in shell minus the 26 holes.
- Principal values of I/(mR²) are 0.627, 0.638 and 0.638. The tensor is near-isotropic, and the centre-of-mass offset is under 0.1 mm.
- Thick-shell formula 0.4·(Ro⁵−Ri⁵)/(Ro³−Ri³)/Ro²:
  - 0.634 for a 1.78 mm wall
  - 0.629 for a 2.1 mm wall
  - 0.614 for a 3.0 mm wall
- Thin-shell 2/3 is an upper bound. The solid-sphere value 2/5 does not apply.
- **I_b = 1.98e-5 kg·m²** nominal (α 0.630, m 24.95 g, R 35.5 mm).
  - Low bound 1.73e-5 (α 0.60, 23.5 g, 35.0 mm).
  - High bound 2.38e-5 (α 2/3, 27.5 g, 36.0 mm; derived). With the old 26.5 g bound it was 2.29e-5.

## 2. Reynolds number and drag crisis (derived)
Re = vD/ν, with D = 0.071 m and ν = 1.5e-5 m²/s:

| v (m/s) | 2 | 3 | 5 | 7 | 9 | 10 |
|---|---|---|---|---|---|---|
| Re | 9.5e3 | 1.4e4 | 2.4e4 | 3.3e4 | 4.3e4 | 4.7e4 |

- **Smooth sphere:** this is the subcritical regime, where Cd ≈ 0.4–0.5 and is nearly flat with Re. The drag crisis sits at about 2–4e5 for smooth spheres and about 5e4–1e5 for dimpled golf balls, so a classic crisis is **not expected** for POLLEN's flight speeds.
- **Caveat about the holes:** outdoor 40-hole pickleballs have Cd ≈ 0.30–0.33 at Re ≈ 5e4. That is below the smooth subcritical value and hints that perforations can alter the boundary layer. Indoor 26-hole balls, the closest analogue, sit at Cd ≈ 0.45, consistent with ordinary subcritical drag.
- **Reverse Magnus:** in smooth-sphere and golf-ball data, inverse Magnus appears only near the drag crisis and only at **S < ~0.5–0.6**.
  - Sources: Taneda Re 6e4–5e5; Maccoll 4.6e4–1.1e5; Davies 9e4; Kim et al. 2014; Muto et al. 2012. At Re = 1e4 the LES gives ordinary positive lift.
  - Free-flight pickleball backspin at v0 ≈ 6.0–11.5 m/s (derived: fitted data span Re 2.95e4–5.67e4 read from Lindsey Fig. 8, v = Re·ν/D with D 0.074 m; the launcher range is stated as 5–13 m/s) and S ≤ 0.37 (derived: read from Lindsey Figs. 13–14) gave positive Cl ≈ 0.2 (Lindsey 2025). Of that, the S-dependent part is only ≈ 0.02 S; the ≈ 0.17 offset is ambiguous (research/LITERATURE_SYNTHESIS.md §4.3).
  - Free-flight table-tennis tests reportedly found no negative Magnus for backspin, although wind-tunnel tests show a "lift crisis".
- **Verdict on reverse Magnus:** unlikely for POLLEN at S ≥ 0.5, but **not excluded**, and there is no POLLEN-specific evidence either way. `research/params_lit.json` carries a pessimistic floor set (c1 0.02, Cl_max 0.04; §4) in place of the earlier informal Cl = 0 floor. A negative Cl is outside the bounded sets.
- **Without spin:** perforated balls can feel orientation-dependent side forces (the wiffle "trapped vortex", Rossmann & Rau 2007). This is a scatter source for low-spin shots.

## 3. Drag coefficient (constant; assumed, literature-bounded)
**Cd: low 0.33 / nominal 0.50 / high 0.90.**

| Source | Ball / regime | Cd | Transferable? |
|---|---|---|---|
| Lindsey 2025 (free flight, 86 shots across both ball types, v0 ≈ 6.0–11.5 m/s) | indoor 26-hole pickleball | 0.45 (SD 0.09) | **Best analogue**: same hole count, similar size and mass. Web article, not peer reviewed |
| Lindsey 2025 | outdoor 40-hole pickleball | 0.33 (SD 0.08) | Partly: smaller holes. Sets the low bound |
| Steyn et al. 2025 (6 shots, Re 4.7–6.1e4) | outdoor 40-hole | 0.30 ± 0.02, no Re or S trend | Partly: small sample, smaller holes |
| Emond, Sun & Swartz 2024 | assumed from wiffle (Rossmann & Rau 2007) | 0.6 | Weak: the wiffle hole pattern differs. 0.6 is one Wiffle orientation; the full range is 0.36–1.05 by orientation and Re, rising toward about 1 at the lowest Re (§4). Supports the high bound |
| Muto et al. 2012 LES, Re 1e4 | smooth sphere | ~0.47 (S 0.2), 0.66 (S 1.0) | Regime analogue. **Spin raises Cd**, so high-S shots lean toward the high bound |
| Tandjono et al. 2020 (numerical, Re 1e5) | floorball, 10 / 13 mm holes | 0.58 / 0.72 | Low weight. Says bigger holes add drag |
| Lindsey 2025, hole-modification control ball (8–10 shots, 6.2–8.25 m/s, shorter path) | 26-hole pickleball | 0.59–0.985 (fit 0.65–0.82) | Same ball type, but the values are not comparable with the main fit. Supports the high bound |
| 2017 FRC FUEL drop test (forum; Cd recomputed) | 5 in perforated ball | 0.88 | Weak (grade D). Supports the high bound |

The high bound 0.90 allows for a spinning, perforated ball at Re ≤ 5e4 reaching 0.8–0.9 (Lindsey control ball, Wiffle at low Re, Muto 0.66 at S = 1, FUEL 0.88; research/LITERATURE_SYNTHESIS.md §3).

Terminal speed v_t = √(2·m·g / (ρ·Cd·A)) is ≈14.35 m/s at the nominal Cd 0.50, 17.7 m/s at Cd 0.33 and 10.7 m/s at Cd 0.90 (derived; ρ 1.20, m 24.95 g, A as in §5). The drag deceleration a_D/g = (v/v_t)² is (derived):

| v (m/s) | 3 | 5 | 7 | 9 |
|---|---|---|---|---|
| a_D/g, Cd 0.33 | 0.03 | 0.08 | 0.16 | 0.26 |
| a_D/g, Cd 0.50 (nominal) | 0.04 | 0.12 | 0.24 | 0.39 |
| a_D/g, Cd 0.90 | 0.08 | 0.22 | 0.43 | 0.71 |

So drag is larger than the nominal Magnus force at every speed (compare §5). In sensitivity runs, pair the high Cl set with the higher Cd values.

## 4. Lift coefficient, Cl = min(c1·S, Cl_max), with S = ωR/|v_rel|
For context, an ideal hood (HANDOFF §4C) gives S_exit ≈ 1. As the ball slows near the apex, S rises, so the model must hold to S ≈ 2. That is why every set is capped. The low, nominal and high sets reach their caps by S ≈ 0.5–0.75; the floor set's slope runs on to S = 2.0 before its cap (derived: S_sat = Cl_max/c1).

| Set | c1 | Cl_max | Cap reached at S | Basis |
|---|---|---|---|---|
| floor | 0.02 | 0.04 | 2.00 | Lindsey backspin fit \|Cl\| ≈ 0.173 + 0.02·S (S ≤ 0.37): if the 0.17 offset is not spin lift (the source cannot tell), the Magnus part is only ≈ 0.02·S. Also stands for "holes vent the lift away". Replaces the earlier informal Cl = 0 floor |
| low | 0.20 | 0.15 | 0.75 | Steyn 0.195·S fit (40-hole, S ≤ 0.3); cap = deepest smooth-sphere lift-crisis trough in POLLEN's Re band (Ito & Kamijima 0.153–0.207; Sakai valleys 0.09–0.21) |
| nominal | 0.35 | 0.25 | 0.71 | Pickleball backspin Cl ≈ 0.2, nearly flat in S (Lindsey 2025); smooth sphere 0.17 at S 0.2 and 0.30 at S 1.0 (Muto 2012 at Re 1e4, matches Tsuji et al.) |
| high | 0.80 | 0.40 | 0.50 | Smooth-sphere initial slope ≈0.8; subcritical saturation 0.30–0.37 for S 1–12 (Muto; Zhou et al. 2022; Ruchayosyothin et al. 2022); baseball SHS fit 0.09 + 0.6·S = 0.39 at S 0.5 |

Why each source does or does not transfer:

- **Pickleball (Steyn, Lindsey)**
  - Transfers: same material class, similar size, mass and Re.
  - Does not transfer: pickleball S ≤ ~0.3–0.5, whereas POLLEN shots reach S ≈ 1–2. Steyn has 6 shots with large scatter and a figure inconsistent with its own fit. Lindsey's backspin Cl is nearly S-independent, which suggests early saturation.
  - HANDOFF §5: these are not POLLEN measurements.
- **Smooth rotating sphere (Muto LES, Tsuji, Zhou, RSM)**
  - Transfers: correct Re and S range, and it is the only source family that covers S ≈ 1 and above.
  - Does not transfer: no holes. Air through the holes and the internal cavity may vent the pressure difference (lower Cl) or change separation (either sign).
- **Baseball / tennis (SHS, Nathan; Cross & Lindsey)**
  - Transfers: only the shape of Cl(S), which rises roughly linearly and then flattens.
  - Does not transfer: Re > 6e4–1e5, and seams or felt instead of holes.
- **Wiffle (Rossmann & Rau)**
  - Transfers: the qualitative warning that holes create asymmetric forces.
  - Does not transfer: one-sided slots, measured non-spinning. Full text read (research/checks/rossmann2007.md): Cd 0.36–1.05 by orientation and Re; the 0.6 used by Emond et al. is one (β = 90°) orientation.

## 5. Scale check: Magnus acceleration / g (derived)
Inputs: ρ 1.20, A = π·0.0355² = 3.959e-3 m², m 24.95 g; a_M/g = ρ·Cl·A·v² / (2·m·g). The HANDOFF check (5 m/s, Cl 0.20, ρ 1.225 → 0.485 m/s²) is reproduced. The no-spin twin (S = 0) has Cl = 0, so its Magnus term is 0 at every speed.

| v (m/s) | floor S=0.5 | floor S=1 | floor S=2 | low S=0.5 | low S=1 | low S=2 | nom S=0.5 | nom S=1 | nom S=2 | high S=0.5 | high S=1 | high S=2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 0.001 | 0.002 | 0.003 | 0.009 | 0.013 | 0.013 | 0.015 | 0.022 | 0.022 | 0.035 | 0.035 | 0.035 |
| 5 | 0.002 | 0.005 | 0.010 | 0.024 | 0.036 | 0.036 | 0.042 | 0.061 | 0.061 | 0.097 | 0.097 | 0.097 |
| 7 | 0.005 | 0.010 | 0.019 | 0.048 | 0.071 | 0.071 | 0.083 | 0.119 | 0.119 | 0.190 | 0.190 | 0.190 |
| 9 | 0.008 | 0.016 | 0.031 | 0.079 | 0.118 | 0.118 | 0.138 | 0.197 | 0.197 | 0.315 | 0.315 | 0.315 |

Reading the table:
- Near the apex the speed is typically 2–4 m/s, where Magnus is only **≈1–6% of g**, even with the high set. The meaningful spin curvature happens on the faster parts of the path, at roughly 6–9 m/s, where it is 5–30% of g (about 1–3% with the floor set at S 1–2).
- In this capped model, extra spin changes nothing once S exceeds S_sat: about 0.5–0.75 for the low, nominal and high sets, but 2.0 for the floor set (model statement, not a measurement). This supports HANDOFF §5's warning not to claim that more backspin always helps.

## 6. Spin decay (derived / assumed)
- **Model:** dω/dt = −k·ω.
- **Physics:** the Tavares torque model with C_M = β·S (as summarized by Nathan) gives k = π·ρ·β·R²·|v| / (α·m) = **0.30·β·v** for POLLEN. So k scales with speed; a constant k is a bounding simplification.
- **Golf-ball data:** β = 0.010–0.012 (Smits & Smith 1994; Tavares et al. 1999), which gives k = 0.009–0.033 /s over 3–9 m/s.
- **Why POLLEN decays faster:** its M/R² is 19.8 kg/m² against 101 for a golf ball, so at the same β and v it spins down about 5× faster.
- **Unmeasured:** holes may act as paddles, and β for a perforated shell has never been measured.
- **Range: k low 0.005 / nominal 0.03 / high 0.15 s⁻¹** (`research/params_lit.json`). The nominal is β 0.02 at |v| ≈ 5 m/s; the low and high are the extremes β 0.009 at |v| ≈ 1.8 m/s and β 0.05 at |v| ≈ 9.9 m/s (derived: |v| = k/(0.302·β)). β up to 0.05 for the paddle effect of the holes is a guess.
- **Effect over a ~1.2 s flight:** about 0.6%, 3.5% and 16.5% spin loss for the low, nominal and high bounds (derived: 1 − e^(−1.2·k)). Spin decay is second-order next to the Cl uncertainty.

## 7. Open questions / what to measure first (Phase 4)
1. **Cd:** side-on high-speed video of non-spinning drops or throws at 3–9 m/s. Fit Cd per ball across at least 5 balls.
2. **Cl(S):**
   - Run backspin shots with marked balls (three great circles) at S ≈ 0.3, 0.7, 1.0 and 1.5.
   - Fit c1 and Cl_max, and explicitly test the sign at low S (reverse-Magnus check).
3. **k:** count spin early and late in the same flight.
4. **Mass, wall thickness and I_b:** weigh at least 10 balls and measure wall thickness at the holes. A rolling-incline test gives α directly: the incline acceleration is g·sinθ/(1+α).
5. **Knuckle side-force scatter** at low spin. Repeat shots and record the lateral dispersion.

## Sources
1. FIRST, BIOBUZZ Competition Manual TU07, §9.8. https://ftc-resources.firstinspires.org/ftc/game/cm-html/BIOBUZZ%20Competition%20Manual%20-%20TU07.htm
2. AndyMark, BIOBUZZ scoring elements (spec, am-5851_yellow Pollen.STEP, layout print). https://andymark.com/products/biobuzz-scoring-elements?variant=47194281148588
3. Lindsey, C. (2025-05-12). The Physics of Pickleball Aerodynamics and Trajectories: A Revised Model of Lift and Drag. https://twu.tennis-warehouse.com/learning_center/pickleball/pickleball_aerodynamics.php
4. Steyn, D. et al. (2025). Executing a Successful Third Shot Drop in Pickleball. SportRxiv preprint https://sportrxiv.org/index.php/server/preprint/download/499/1073/997 ; IJSSC https://doi.org/10.1177/17479541251365200
5. Emond, Sun & Swartz (2024). Pickleball Flight Dynamics. https://doi.org/10.30827/ijrss.32618 (arXiv 2409.19000)
6. Rossmann & Rau (2007). An experimental study of Wiffle ball aerodynamics. Am. J. Phys. https://doi.org/10.1119/1.2787013 (full text read later from the Lafayette repository PDF; research/checks/rossmann2007.md)
7. Muto, Tsubokura & Oshima (2012). Negative Magnus lift on a rotating sphere at around the critical Reynolds number. Phys. Fluids 24, 014102. https://doi.org/10.1063/1.3673571
8. Kim, Choi, Park & Yoo (2014). Inverse Magnus effect on a rotating sphere: when and why. JFM 754 R2. https://cambridge.org/core/journals/journal-of-fluid-mechanics/article/inverse-magnus-effect-on-a-rotating-sphere-when-and-why/0E9FEF2880AA45C8B12587374C6F10EE
9. Nathan, A.M. The effect of spin on the flight of a baseball (SHS lift fit). https://arxiv.org/abs/physics/0605041
10. Cross & Lindsey (2013). Tennis ball drag and lift. https://twu.tennis-warehouse.com/learning_center/aerodynamics2.php
11. Nathan, A.M. The Spin Decay of a Baseball (Smits & Smith; Tavares golf data). https://baseball.physics.illinois.edu/spindown-rev1.pdf
12. Tandjono et al. (2020). On the aerodynamics drag of floorball. AIP Conf. Proc. 2227, 020021. https://doi.org/10.1063/5.0000928
13. Ruchayosyothin et al. (2022), JRAME (abstract only). https://doi.nrct.go.th/ListDoi/listDetail/10.14456%2Fjrame.2022.5 ; Zhou et al. (2022) water-tank limit Cl ≈ 0.37 (abstract-level, via search summary).
14. Ito & Kamijima (2025). CFD of a spinning smooth sphere. Trans. JSST 17(1):25–31 (J-STAGE).
15. Sakai et al. (2016). Aerodynamics of a spinning table-tennis ball: lift crisis (JSME annual meeting, J-STAGE); Miyazaki et al. (2017), same campaign.
16. Chief Delphi thread 154587 (2017 FRC FUEL terminal velocity; Cd recomputed 0.88 in research/checks/sweep_pollen.md). https://www.chiefdelphi.com/t/154587
