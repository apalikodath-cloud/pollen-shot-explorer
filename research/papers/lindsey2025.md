# Lindsey (2025) — The Physics of Pickleball Aerodynamics and Trajectories: A Revised Model of Lift and Drag

source_id: `lindsey2025` · PM-001 literature study · read 2026-10-30

## Citation
Lindsey, C. (2025, May 12). *The Physics of Pickleball Aerodynamics and Trajectories: A Revised Model of Lift and Drag.* Tennis Warehouse University / Pickleball University, Tennis Warehouse, San Luis Obispo, CA.
https://twu.tennis-warehouse.com/learning_center/pickleball/pickleball_aerodynamics.php
Companion lay summary (same author, same date): "What Makes a Pickleball Fly the Way It Does?" https://twu.tennis-warehouse.com/learning_center/pickleball/pickleball_aerodynamics_light.php

## Access and review status
- **Access: full text.** I read the full HTML text and the 11 figure images (Figures 6–15, the latter downloaded and inspected). The article has no tables. No raw data, code or supplementary files are published.
- **Review status: unreviewed web article.** It is a single-author technical note on a retailer's education site, with no journal, peer review, DOI or data release. The acknowledgements say ChatGPT-4 (April 2025) was used for "text editing, summarization, and concept refinement".
- **Evidence classes used below:**
  - **[EXP]** experimental measurement reported in the text.
  - **[FIG]** a value I read from a figure image (about ±0.01–0.02 in coefficient, ±0.002 N in force, ±0.01 in S).
  - **[DER]** a value I derived from the article's numbers.
  - **[HYP]** the author's hypothesis.
  - **[CRIT]** my assessment.

## Method (as reported)
- **Balls.** Indoor balls had 26 large holes and outdoor balls had 40 small holes. Brand, mass and measured diameter are **not stated**. Appendix A.1 uses r = 0.037 m (D ≈ 74 mm). Ball mass appears only as the symbol m.
- **Launcher.** A custom bungee-powered pendulum (Fig. 6) strikes the ball. Spin is set by striking above or below centre, and speed by arm height and bungee stretch. Launch speeds were 5–13 m/s (Sec. 3.1). Data in Fig. 8 actually span v0 ≈ 6.0–11.6 m/s.
- **Spin–speed coupling (Sec. 3.4).** An off-centre strike splits energy between translation and rotation, so high-spin shots had lower v0 and Re. The author states that **S and Re are confounded** and could not be fully decoupled.
- **Cameras.** Two synchronized high-speed cameras ran at **300 fps**. The side camera, about 1 m from launch, measured v0, θ and ω. The downrange camera covered about 5 m of flight. Video was digitized with Tracker to (t, x, y).
- **Inversion.** A custom Python RK4 simulator started from the measured (v0, θ, ω). An optimizer fitted **one constant C_D and one constant C_L per trajectory** by minimizing the sum of squared position errors (SSE).
- **Sample.** 86 trajectories were fitted, with a mean endpoint error of 15 mm.
- **Robustness checks.** The author ran subsampling, penalty functions, bound and solver changes, smoothing and residual monitoring, and reports that none changed the trends.
- **Noise sources named by the author (Sec. 3.3).** Digitization noise, especially near the apex, and "flow instability due to hole geometry".
- **Supplementary prototype study (Sec. 4.1.2).** Three large-hole balls were tested: a balloon inflated inside, tape over every hole, and an unmodified control. Each had 8–10 trajectories over a **shorter flight path**. The author says absolute C_D differs from the main runs and only relative ranking is meaningful.
- **Not reported:**
  - spin decay;
  - spin-axis tilt;
  - ambient temperature and air density as measured (ρ = 1.21 kg/m³ is assumed);
  - the camera scale-calibration method;
  - the per-shot table of (v0, θ, ω, C_D, C_L);
  - the regression coefficients for C_L vs S.

## Equations (verbatim form, with symbols and units)
| # | Equation | Symbols / units | Where |
|---|---|---|---|
| 1 | F_D = 0.5 C_D ρ A v² | F_D drag force [N]; C_D [-]; ρ air density, taken as 1.21 kg/m³; A cross-sectional area [m²]; v speed relative to air [m/s] | Sec. 1.1, eq. (1) |
| 2 | F_L = 0.5 C_L ρ A v² | F_L lift force [N], perpendicular to velocity; C_L [-]. Sign convention: topspin → C_L < 0 (downward), backspin → C_L > 0 | Sec. 1.1, eq. (2); Sec. 5.3 |
| 3 | Re = v D / μ | D ball diameter [m]; μ is used for **kinematic** viscosity, ≈1.5×10⁻⁵ m²/s at 20 °C (the conventional symbol is ν) | Sec. 1.2, eq. (3) |
| 4 | C_D = F_D / (0.5 ρ A v²) | rearranged (1) | Sec. 4.1.4 |
| 5 | S = R ω / v0 | S spin number [-]; R radius [m]; ω spin [rad/s]; **v0 = launch speed**, so S is evaluated at launch only and not along the path | Sec. 4.2.3 |
| 6 | C_L,measured = C_L,Magnus + C_L,gravity + C_L,internal | the "three-component lift model" [HYP]. C_L,gravity is a spin-independent downward bias; C_L,internal is attributed to flow through the holes. **None of the terms has a functional form or numeric value.** | Sec. 5.1 |
| 7 | a_g(θ) = g cos θ | tangential gravity component on air moving around the front of the ball; θ is measured from the stagnation point; g = 9.8 m/s² | App. A.1, eq. (1) |
| 8 | Δt = s / v, s = (π/2) r | air transit time over the front quarter arc; r = 0.037 m → s ≈ 0.0581 m; v ≈ 10 m/s → Δt ≈ 0.00581 s | App. A.2, eq. (2) |
| 9 | Δv_top ≈ −g·0.64·Δt ≈ −0.0365 m/s; Δv_bottom ≈ +0.0365 m/s | 0.64 is the "average gravity component over the arc" (≈ 2/π) | App. A.2, eqs. (3)–(4) |
| 10 | C_L baseline correction: fit \|C_L\| = a + b·S separately for topspin and backspin, and take C_L,Magnus ≈ \|C_L\| − a | **The values of a and b are not printed in the text.** The only values are the fitted lines drawn in Fig. 13, which I read below. | Sec. 5.3.1 |

Implicit equation of motion used by the simulator (not written out in the article): m dv/dt = m g + F_D + F_L, integrated with RK4, using constant C_D and C_L per shot.

## Data points (all source_id = lindsey2025)
| Quantity | Value | Conditions | Where | Class |
|---|---|---|---|---|
| N trajectories fitted | 86 | indoor and outdoor balls, mixed spin | Sec. 3.2, Abstract | EXP |
| Mean endpoint error of fits | 15 mm | all 86 | Sec. 3.2 | EXP |
| Launch speed range | 5–13 m/s (11–29 mph) | pendulum launcher | Sec. 3.1 | EXP |
| Launch speed / Re actually plotted | v0 ≈ 6.0–11.6 m/s; Re ≈ 2.95×10⁴–5.7×10⁴ | Fig. 8 x-axis, D ≈ 0.074 m | Fig. 8 | FIG |
| Air density | 1.21 kg/m³ | assumed | Sec. 1.1 | EXP (assumed) |
| Kinematic viscosity | 1.5×10⁻⁵ m²/s | 20 °C | Sec. 1.2 | EXP (assumed) |
| Ball radius | 0.037 m | used in appendix | App. A.1 | EXP (nominal) |
| Camera frame rate | 300 fps | both cameras | Sec. 3.1 | EXP |
| C_D, indoor 26 large holes | mean 0.45; SD 0.092; SE 0.013 | v0 ≈ 6–11.6 m/s, all spins | Sec. 4.1.1; Fig. 8 | EXP |
| C_D, outdoor 40 small holes | mean 0.33; SD 0.083 (0.082 in Fig. 8 label); SE 0.014 | same | Sec. 4.1.1; Fig. 8 | EXP |
| C_D scatter range, large holes | ≈0.245–0.71 | per-shot | Fig. 8 | FIG |
| C_D scatter range, small holes | ≈0.185–0.55 | per-shot | Fig. 8 | FIG |
| C_D vs v0 trend, large holes | fit ≈0.435 (Re 3.0×10⁴) → ≈0.465 (Re 5.6×10⁴); R = 0.072 | essentially flat | Fig. 8 | FIG |
| C_D vs v0 trend, small holes | fit ≈0.32 → ≈0.335; R = 0.035 | essentially flat | Fig. 8 | FIG |
| Regime statement | "supercritical", no drag crisis; C_D constant or rising slightly with v | v0 ≈ 6–11.6 m/s | Sec. 4.1.3 | EXP + interpretation |
| Drag force range | ≈0.02–0.146 N | all shots | Fig. 10 | FIG |
| F_D vs Re fit, large holes | ≈0.02 N at Re 2.85×10⁴ → ≈0.133 N at 6.0×10⁴; R = 0.814 | linear fit | Fig. 10 | FIG |
| F_D vs Re fit, small holes | ≈0.02 N at Re 3.25×10⁴ → ≈0.105 N at 6.0×10⁴; R = 0.717 | linear fit | Fig. 10 | FIG |
| C_D vs F_D correlation | R = 0.563 (large), 0.679 (small) | partly circular, since C_D = F_D/q | Fig. 11 | FIG/CRIT |
| C_D, unmodified control (short path) | ≈0.61–0.98; quadratic fit ≈0.82 at 6.3 m/s → ≈0.655 at 7.8 m/s → ≈0.67 at 8.25 m/s; R = 0.54 | large-hole ball, v0 ≈ 6.2–8.3 m/s, 8–10 shots, shorter path; **absolute values not comparable** with Fig. 8 | Fig. 9 | FIG |
| C_D, taped holes (short path) | ≈0.35–0.81; fit ≈0.81 at 6.2 m/s → ≈0.43 at 8.1 m/s; R = 0.91 | same | Fig. 9 | FIG |
| C_D, balloon inside (short path) | ≈0.35–0.55; fit ≈0.56 at 6.3 m/s → ≈0.40 at 7.9 m/s; R = 0.84 | same | Fig. 9 | FIG |
| Effect of blocking internal flow | balloon gave the lowest C_D and both modifications reduced C_D variability; tape "modestly increased drag" relative to the balloon (roughness) | relative ranking only | Sec. 4.1.2 | EXP |
| \|C_L\| vs S, topspin (fitted line) | \|C_L\| ≈ 0.24 + 0.44·S; R = 0.650 | S ≈ 0–0.65; both ball types | Fig. 13 | FIG |
| \|C_L\| vs S, backspin (fitted line) | \|C_L\| ≈ 0.175 + 0.02·S; R = 0.042 | S ≈ 0–0.37; both ball types | Fig. 13 | FIG |
| Backspin \|C_L\| scatter | ≈0.01–0.36; most points 0.08–0.27; visual SD ≈0.07–0.08 | S ≈ 0–0.37 | Fig. 13 | FIG (my estimate) |
| Topspin \|C_L\| scatter | ≈0.13–0.62 | S ≈ 0–0.65 | Fig. 13 | FIG |
| Backspin C_L baseline (text) | "≈ 0.2" (nearly flat with S) | backspin | Sec. 4.2.3 | EXP |
| Low-spin C_L, topspin | ≈ −0.24 | near-zero spin | Sec. 5.3 | EXP |
| Low-spin C_L, backspin | ≈ +0.17 | near-zero spin | Sec. 5.3 | EXP |
| Near-zero-S clusters (boxed) | S ≈ 0: one cluster C_L ≈ +0.08 to +0.25 (both ball types); another C_L ≈ −0.15 to −0.42 (mostly large-hole) | signed S, where negative S is backspin | Fig. 14 | FIG |
| Signed C_L vs signed S, single line | C_L ≈ −0.05 − 1.0·S_signed (S_signed < 0 is backspin); R = 0.83 | all balls; the line mainly bridges the two sign clusters | Fig. 14 | FIG |
| \|F_L\| vs S, topspin | \|F_L\| ≈ 0.052 + 0.026·S N; R = 0.38; range ≈0.024–0.084 N | — | Fig. 12 | FIG |
| \|F_L\| vs S, backspin | \|F_L\| ≈ 0.043 − 0.057·S N; R = 0.52; range ≈0.001–0.061 N | the decrease with S reflects the S–v0 coupling (high spin means low v0) | Fig. 12 | FIG |
| Example fit, Fig. 7a image | v0 = 10.72 m/s, ω = 60.40 rad/s (≈577 rpm), θ = 147.34° (≈32.7° elevation, leftward), S = 0.21, SSE = 0.0098, endpoint error 0.0156 m, **C_D = 0.4361, C_L = −0.5763**; about 3.2 m range and 1.0 m rise | the caption says "large-hole ball with backspin", **but negative C_L means topspin under the article's own convention** | Fig. 7a | FIG |
| Example fit, Fig. 7b image | v0 = 10.16 m/s, ω = −39.60 rad/s (≈378 rpm), θ = 161.42° (≈18.6° elevation), S = 0.14, SSE = 0.0043, endpoint error 0.0011 m, **C_D = 0.4785, C_L = +0.4773**; apex ≈0.345 m at ≈1.9 m, range ≈3.4 m | the caption says "small-hole ball with topspin", **but positive C_L means backspin**. C_L = 0.477 at S = 0.14 is above every backspin point in Fig. 13 (max ≈0.36). | Fig. 7b | FIG |
| Max S tested | backspin ≈0.37; topspin ≈0.65 | — | Figs. 13–14 | FIG |
| Implied max spin rate | backspin ≈ 0.37·v0/R ≈ 60–110 rad/s (≈570–1050 rpm) for v0 = 6–11 m/s; **spin rates are not reported directly** | — | — | DER |
| Gravity-flow estimate | Δv_top = −0.0365 m/s, Δv_bottom = +0.0365 m/s, difference 7.4 cm/s ("07.4 cm/s" typo; rounded to 0.07 m/s in A.4) | v = 10 m/s, r = 0.037 m | App. A.2, A.4 | HYP |
| Prior work quoted: Steyn et al. 2025 | C_D ≈ 0.30 ± 0.02; C_L ≈ 0.195·S | 6 outdoor-ball trajectories | Sec. 2 | secondary |
| Prior work quoted: Emond et al. 2024 | fixed C_D = 0.6, no lift | simulation | Sec. 2 | secondary |

Reverse Magnus and drag crisis:
- The article never mentions a **reverse Magnus effect**.
- It explicitly rules out a drag crisis in its range (Sec. 4.1.3).
- **No backspin shot in Fig. 13/14 has a negative (downward) C_L.** The minimum is about +0.01 at S ≈ 0.32. That one point is consistent with a near-zero or locally reversed Magnus response, but it is a single shot.
- The real low-S anomaly is a **sign-dependent jump of about ±0.2 in C_L as S → 0**, which classical Magnus theory forbids.

## Critical assessment [CRIT]
1. **The gravity-flow mechanism is not physically sound as stated.** In a constant-density, incompressible fluid with no free surface, gravity is balanced exactly by the hydrostatic pressure gradient. Writing p* = p + ρgz removes g from the Navier–Stokes equations, so the velocity field and the separation lines do not depend on g. The only effect of gravity on the air is buoyancy on the body: ρ_air V g ≈ 2.5 mN for a 74 mm ball, about 1 % of its weight. Appendix A ignores the hydrostatic pressure gradient, and its 3.7 cm/s "deceleration" is an artefact of that omission. **C_L,gravity should not be modelled as physics.** The author also flags the idea as a hypothesis that needs CFD, wind-tunnel and flow-visualization tests.
2. **More plausible sources of the anomalies:**
   - **S–Re confounding.** The author admits this in Sec. 3.4.
   - **One constant C_L per shot while S varies along the path.** S = Rω/v0 is evaluated at launch only, and spin decay is ignored.
   - **Poor spin measurement at low ω.** At 300 fps over about 1 m of side-camera view, a shot spinning at a few rad/s turns only a fraction of a revolution in view. Near-zero-S points may be mislabelled in sign or magnitude.
   - **Spin-axis tilt or gyrospin** from an off-centre pendulum strike.
   - **Hole-orientation-dependent lift**, as reported for wiffle balls by Rossmann & Rau (2007). That would add an orientation-dependent "non-Magnus" force with either sign.
   - **Unstated mass, ρ and scale calibration.** A uniform downward bias can come from a mass error of 1 g (ΔC_L ≈ 0.06 at 8 m/s) or a 2 % pixel-scale error (ΔC_L ≈ 0.03). These explain a small common offset (about −0.03 mean in Fig. 14) but not the ±0.2 split.
3. **Internal inconsistencies:**
   - Figure 7a/7b captions contradict the sign of the fitted C_L.
   - The 7b example (C_L = 0.477, backspin) does not appear in Fig. 13.
   - The text says "persistent downward lift across all trajectories" (Sec. 5), and the companion page says "little or no spin still curved downward". Yet low-spin backspin shots show C_L ≈ +0.17 (upward).
   - The backspin baseline is given as "≈0.2" (Sec. 4.2.3) and "+0.17" (Sec. 5.3).
4. **The robust content** is the C_D statistics per hole pattern and the empirical observation that **backspin effective C_L sits at about 0.17–0.19, with wide scatter and almost no S-dependence over S = 0–0.37 at v0 = 6–11.6 m/s.** This is weak but useful bounding evidence. It is not a validated lift law.

## Applicability to POLLEN
**Transfers (with care):**
- **Geometry and mass are very close.** POLLEN is about 71 mm and 25 g; a pickleball is about 74 mm and, from memory and unverified, 22–26.5 g by USA Pickleball spec. Both are hollow, perforated, thin-shell plastic balls in the same Re band.
  - POLLEN at 2–10 m/s has Re ≈ 0.95×10⁴–4.7×10⁴.
  - Lindsey's data cover Re ≈ 3.0×10⁴–5.7×10⁴, so they overlap only POLLEN's **upper** speed range, i.e. the launch and early-flight segment.
- **C_D level and scatter.** The article shows that hole pattern changes mean C_D by about 35 % (0.33 vs 0.45). It also shows that perforated balls have **large shot-to-shot C_D scatter (SD ≈ 0.08–0.09, about 20–25 %)**, with internal through-flow implicated (Sec. 4.1.2). POLLEN's hole count, size and pattern are not documented in the handoff and must be counted and measured. A prior of C_D ≈ 0.33–0.45 nominal, with a per-shot σ of about 0.09, is a reasonable uncalibrated band.
- **Backspin lift is weak and saturating at moderate S.** An effective C_L of about 0.17–0.19, roughly flat for S ≲ 0.4, is the only free-flight perforated-ball backspin data at these Re. It is consistent with Steyn's C_L ≈ 0.195·S near S ≈ 1, but the two disagree strongly at S ≈ 0.2–0.4 (Steyn gives 0.04–0.08 there).

**Does not transfer:**
- **Low-speed apex regime.** At v ≈ 2–5 m/s, Re ≈ 1–2.5×10⁴, and nothing below about 6 m/s was measured. The "supercritical, no drag crisis" claim is untested there.
- **High spin parameter.** PM-001 hood kinematics give S_exit ≈ 1, and S grows further near the apex as v falls. Lindsey's backspin data stop at S ≈ 0.37.
- **Spin decay**, which is not measured.
- **The three-component model's gravity term** (see the critique above).
- **Topspin results** (out of scope).
- **Fitted C_L values as point properties.** They are per-shot effective constants averaged over a path in which S changes.
- **Brand, hole-pattern and material specifics**, because POLLEN (Gopher ResisDent polyethylene) is not a pickleball and is "not perfectly spherical" per the manual.

## Implications for the PM-001 models
**1. Aero model, C_D.** Use constant C_D, labelled uncalibrated, with a nominal value of 0.40 and a sensitivity band of 0.30–0.50.
- Add per-shot Monte Carlo scatter σ_CD ≈ 0.09 to represent perforated-ball flow instability.
- Do not use Emond's 0.6 as a nominal value. It is an assumption, not a measurement, and is plausible only as a pessimistic upper bound. Fig. 9's short-path values of 0.6–0.98 suggest method bias, not physics.

**2. Aero model, C_L(S) for backspin.** Run a family of laws rather than one. Every candidate must satisfy C_L(0) = 0, so the model has no sign-discontinuity (per handoff §4A regularization).
- (a) **Steyn linear:** C_L = 0.195·S, capped near 0.25–0.3.
- (b) **Lindsey-like saturating:** C_L = 0.18·tanh(S/0.08). This reproduces a flat value of about 0.18 for S ≳ 0.15.
- (c) **Pessimistic:** C_L = 0.10·tanh(S/0.2). This is the lower envelope of the Fig. 13 scatter.
- (d) **Optimistic:** C_L up to about 0.35, the top of the backspin scatter. One example shot reached 0.48 but is unverified.
- Add per-shot scatter σ_CL ≈ 0.07–0.08.

Key consequence: if Lindsey's flat behaviour holds, **extra backspin beyond S ≈ 0.2 buys almost no additional lift.** The flywheel does not need maximum spin. It needs enough spin to reach the plateau, which also supports handoff §5's "more backspin is not always better".

**3. Magnitude check for POLLEN.** Lift acceleration is a_L = (ρA/2m)·C_L·v² = 0.0970·C_L·v² [m/s²], using A = 3.96×10⁻³ m², m = 0.025 kg and ρ = 1.225 kg/m³. With C_L = 0.18:

| v [m/s] | a_L [m/s²] | fraction of g |
|---|---|---|
| 10 | 1.75 | 18 % |
| 8 | 1.12 | 11 % |
| 3 | 0.16 | 1.6 % |

For comparison, drag at 8 m/s with C_D = 0.45 gives 2.8 m/s². **Most of the Magnus-induced path change accrues in the fast early segment, not at the apex.** At the apex, v is low, so the force is small even though S is large. The solver should report the integrated displacement difference versus the no-spin case along the whole path, not only at the apex (handoff §4B).

**4. Do not implement C_L,gravity or C_L,internal as separate physical terms.** If prototype data show a sign-dependent offset, fit it as an empirical bias with its own uncertainty. Include buoyancy (about 2.25 mN, 0.9 % of POLLEN weight) only if precision warrants it.

**5. Launcher model.** Lindsey's pendulum couples S and v0, and so does a single flywheel with a fixed hood (S_exit ≈ 1 by kinematics). PM-001 calibration therefore also needs a deliberate way to vary S at fixed v0, such as different hood gaps or surfaces, or a passive roller with a brake. Otherwise C_L(S) and C_D(Re) cannot be separated, which is the limitation Lindsey acknowledges.

**6. Calibration protocol (Phase 4).** Adopt and improve Lindsey's inverse method: a side camera for exit state plus downrange tracking, RK4 forward model, and SSE fit (15 mm endpoint residual is achievable). Improvements:
- Use a higher frame rate (≥ 480–1000 fps) and a **marked ball** with a stripe or dots so ω is resolved near S ≈ 0. Measure spin both at exit and late in flight to get k_spin.
- **Weigh each ball**, measure ρ (temperature and pressure), and calibrate pixel scale in both cameras.
- Fit C_L as a function (for example the parameter of tanh or linear) across many shots, rather than one constant per shot. Report CIs.
- Track hole orientation at launch, or randomize it and treat it as noise.
- Include low-speed shots (v ≈ 2–5 m/s) to cover the apex Re that Lindsey did not test.
- Run a taped or ball-in-ball POLLEN comparison to estimate how much internal flow drives C_D scatter.

**7. Feasibility framing.** With effective backspin C_L of about 0.1–0.2 and lift of about 2–18 % g during the fast part of the flight, backspin will measurably **flatten and lengthen** the trajectory: a higher apex, a later and shallower descent. It cannot produce a mid-air horizontal reversal. Whether that is enough to clear the unfavorable-side HIVE geometry must come from the inverse solver, using the C_L family in item 2 and the scatter in items 1–2 as uncertainty bounds.
