# Aerodynamic hypotheses for a "sudden break" of a BioBuzz ball

Status: analysis note, 2026-11-05. Labels:
- [Lit] published result (details and DOIs in `LITERATURE_REVIEW.md`);
- [P] prediction of the repo CFD (not validated against a real POLLEN);
- [D] derived by hand here;
- [A] assumption.

The ball is POLLEN unless stated. NECTAR has no CFD and no known mass (§4).

## 0. Yardstick: how big must a force be to matter?

Constant lateral force coefficient C, flight path length L, ball mass m, frontal area A [D]:

    y = C ρ A L² / (4 m)

- POLLEN: ρ = 1.204 kg/m³, A = 3.973e-3 m², m = 24.95 g, so ρA/(4m) = 0.0479 m⁻¹.
- At L = 3 m: **y = 0.431 m × C**.
  - C = 0.01 gives 4.3 mm; C = 0.05 gives 2.2 cm; C = 0.2 gives 8.6 cm.
- The deflection for a given C does not depend on speed (the time in flight falls as the force rises).
- 3 m is 42 ball diameters, so one flight lasts **42 D/U** whatever the speed.

A fluctuating force averages out. For a sinusoid at frequency f, the path amplitude is a/(2πf)². Example [D]:
- vortex shedding at St 0.19, U = 7 m/s: f = 18.7 Hz;
- C = 0.02 gives a = 0.094 m/s² and an amplitude of **7 µm**.

Only slow force changes (periods of at least about 10 D/U) can move the ball visibly.

Reference, not a knuckle: Magnus lift at S = 0.25 to 1 has Cl 0.15 to 0.36 [P], giving **6.5 to 15 cm** at 3 m, smooth and repeatable.

Reynolds number in the FTC range [D]: Re = ρUD/μ = 4731 × U. Launch speeds of 4.5 to 9 m/s give **Re 2.1e4 to 4.3e4**. Drag slows the ball by about 16 % over 3 m (velocity decay length 2m/(ρACd) = 17 m at Cd 0.6).

## 1. Three kinds of "break"

| Kind | Meaning | Example |
|---|---|---|
| **Discontinuous** | the force jumps between states in a time much shorter than the flight (< 1 D/U) and stays there | bistable wake flip, sudden separation switch |
| **Rapid but continuous** | the force changes over 1 to 10 D/U | wake azimuth wander, separation moving as the ball turns |
| **Perceptually discontinuous** | the force is smooth (or constant), but the path looks like it breaks late | constant side force: y ∝ t², so half of the total deflection happens in the last 29 % of the flight |

For a robot shot only the landing point matters; nobody has to track the ball. A perceptual break has no game value, and a smooth curve does the same job.

## 2. The nine mechanisms

Ranking criterion: strength of the evidence that the mechanism produces a lateral deflection of at least 5 cm at 3 m for POLLEN at Re 2e4 to 5e4.

### Rank 1 — H2 + H3: orientation-dependent steady side force (asymmetric separation and flow redistribution through the holes)

- **Evidence.**
  - Wiffle balls, which have holes on one hemisphere, show CL 0.1 to 0.6 depending on orientation [Lit, Rossmann & Rau 2007].
  - Seam-shifted wakes give steady, repeatable baseball deflections [Lit, Smith & Smith 2021].
  - Pickleball hole layouts change the landing spread [Lit, Lin et al. 2026].
  - POLLEN CFD at S = 0 [P]: the mean lift-direction coefficient is 0.046 at the "btw" orientation and 0.016 to 0.017 at "hf" and "o3". The spread between orientations is about **0.03**.
  - In CFD the hole walls carry 2 % and the inner surface 7 % of the fluctuating side force; the mean side force comes mostly from the outer surface [P].
- **Key difference from a Wiffle ball.** POLLEN has 26 holes spread over the whole shell, not one perforated hemisphere [CAD]. That symmetry is why its orientation forces are about 10× weaker than the Wiffle values.
- **Size.** C about 0.01 to 0.05, i.e. **0.4 to 2 cm** at 3 m [D from P].
- **Kind.** Steady if the ball does not turn. Rapid-but-continuous if it turns slowly (the pattern turns by θ = S L / R: S = 0.01 to 0.05 gives about 50 to 240° over 3 m [D]).
- **Testable prediction.** At S = 0, side-by-side launches with the ball held at fixed orientations give mean lateral offsets differing by 1 to 2 cm at 3 m, consistent per orientation.
- **Measurement needed.**
  - Orientation-indexed launch tests: at least 20 shots per orientation, with high-speed video at the target plane.
  - Or a wind-tunnel 3-component balance at 5 to 9 m/s with the ball fixed at 6 orientations.

### Rank 2 — H1: wake switching and asymmetric vortex shedding

- **Evidence.**
  - The subcritical sphere wake sheds at St 0.18 to 0.2, and the shedding plane wanders irregularly [Lit: Sakamoto & Haniu 1990; Constantinescu & Squires 2004; Grandemange 2014].
  - The azimuth decorrelates over about 8 D/U [Lit, Rigas 2015].
  - True bistable switching takes 10² to 10³ D/U [Lit: Grandemange 2013; Rigas 2014].
  - Large knuckle forces in baseball and soccer appear only near the drag crisis, Re 1.5e5 to 3.6e5 [Lit: Borg & Morrissey 2014; Hong & Asai 2014]. That is 4 to 10× above POLLEN.
  - POLLEN CFD [P]:
    - sd of the lateral coefficient is about 0.02;
    - increments are Gaussian (kurtosis about 0), so there are no jumps;
    - the path break is under 1 mm, and the fluctuating part alone gives a 3 m miss of p95 0.3 to 1 cm (S = 0 to 0.1, both grids).
  - A sealed smooth sphere in the same code has **3× the fluctuation** (sd 0.066) [P].
- **Size.** About **1 cm** of random wander at 3 m (p95), with no repeatable direction.
- **Kind.** Rapid but continuous. The switching time (≥ 100 D/U) is longer than a flight (42 D/U), so a flight sees at most part of one state.
- **Testable prediction.** No-spin launches with random orientation scatter laterally by about 1 cm (1σ ≈ 0.5 cm) at 3 m beyond the launcher's own scatter. The scatter does not grow with launch speed.
- **Measurement needed.** At least 50 no-spin shots, with the launcher's own dispersion measured separately using a sealed (taped) ball.

### Rank 3 — H8: coupled internal and external vortex dynamics

- **Evidence.**
  - Internal through-flow is about 25 % of U in Wiffle balls [Lit, Rossmann & Rau].
  - POLLEN CFD [P]: cavity mean speed 0.29 U; hole flux up to 0.58 U × hole area.
  - The inner-surface share of the fluctuating force rises from 7 % at S = 0 to 19 % at S = 0.5 [P].
  - Porous bodies with open area below 20 % still shed vortices [Lit, Cicolin 2024]. POLLEN's open area is 13 to 16 % [D].
- **Size.** No sign of lock-in or amplification. Open vs sealed CFD suggests the coupling **reduces** the side-force fluctuation [P].
- **Kind.** Continuous.
- **Testable prediction.** Taping the holes increases the no-spin lateral scatter, by up to about 3× in force sd [P].
- **Measurement needed.** Paired open/taped ball shots, the same as for H1.

### Rank 4 — H6: Reynolds-number-dependent transitions

- **Evidence.**
  - Smooth-sphere drag crisis at Re ≈ 3.7e5 [Lit, Achenbach 1972]. Roughness lowers it, but not to 5e4 for k/D of order 1e-2 [Lit, Achenbach 1974].
  - Wiffle: separation-dominated below Re 3e4, internal flow dominant above 4e4. Lift sign flip near Re 5.5e4 at a single orientation (β = 345°). No early drag crisis [Lit, Rossmann & Rau].
  - POLLEN CFD [P]: Cd 0.59 to 0.61 at S = 0 for Re 20k, 33k and 47k. No crisis, no jump.
- **Size.** None found inside Re 2e4 to 4.7e4. A Wiffle-like flip near 5.5e4 would need about 11.6 m/s, above the useful FTC range (`FLYWHEEL_ANALYSIS.md`).
- **Kind.** If present, rapid but continuous (Re falls only 16 % over 3 m).
- **Testable prediction.** Drag coefficient from time-of-flight at 4.5, 6, 7.5 and 9 m/s is flat within ±5 %.
- **Measurement needed.** Speed-gate or video drag measurement at 4 speeds. CFD Re sweep at S = 0.05 (queued).

### Rank 5 — H7: negative or reversed Magnus effect

- **Evidence.**
  - For smooth spheres, inverse Magnus is tied to the drag crisis [Lit, Kim et al. 2014; Muto 2012]. A weak inverse effect was reported near Re 4.6e4 only for spin ratio Γ < 0.4 (reported via Muto 2012; primary source not read).
  - Pickleball tunnel data show near-zero-spin lift of −0.24 (topspin) / +0.17 (backspin) [Lit, Lindsey 2025, not peer reviewed]. That is more likely an orientation effect than spin.
  - POLLEN CFD [P]:
    - for S ≥ 0.25, Cl is positive and monotonic (0.15 to 0.46) at all three Re;
    - for S 0.02 to 0.05, Cl is 0.025 to 0.036, less than the S = 0 orientation offset. No reversal.
- **Size.** None found.
- **Kind.** If present, it would be continuous. Spin decays only about 1.4 % per metre [P], so S hardly changes in flight.
- **Testable prediction.** Backspin launches at S 0.05 to 0.25 deflect upward (normal Magnus), never downward.
- **Measurement needed.** Spin-rate measurement (high-speed video of a marked ball) plus vertical drop at 3 m.

### Rank 6 — H5: aerodynamic torque and orientation change

- **Evidence.** CFD torque coefficients are small. Integrating them with the ball's inertia (I = 1.99e-5 kg m², k_I = 0.63), a ball launched without spin turns **0.8° (p95 1.0°) over 3 m** [P].
- **Size.** The hole orientation is effectively frozen in flight. Aerodynamic torque cannot create a mid-flight change of the orientation force.
- **Kind.** Continuous, negligible.
- **Testable prediction.** A marked no-spin ball shows less than 5° of rotation in high-speed video over 3 m (most of that comes from the launcher's residual spin).
- **Measurement needed.** Video of marked balls.

### Rank 7 — H4: internal cavity pressure oscillations

- **Evidence and estimate [D].**
  - Helmholtz resonance f = (c/2π) × sqrt(S_h / (V L_eff)), with:
    - inner radius 33.8 mm, so V = 1.62e-4 m³;
    - 26 holes of about 10.6 mm diameter, so S_h = 2.29e-3 m²;
    - L_eff = wall + end corrections ≈ 1.8 + 9 mm = 10.8 mm.
  - Result: f ≈ **2.0 kHz**, about 100× the shedding frequency of 11 to 27 Hz.
  - A uniform cavity pressure on a closed shell gives zero net force. Only the hole-area asymmetry would act, and per the arithmetic in §0 a force at 2 kHz moves the ball by nanometres.
- **Size.** Zero for the path.
- **Kind.** Continuous, path-irrelevant.
- **Testable prediction.** A microphone inside a POLLEN in a wind tunnel shows no tonal peak between 5 and 200 Hz linked to lateral force.

### Rank 8 — H9: compressibility in local flow structures

- **Estimate [D].**
  - Flight Mach number 0.013 to 0.026.
  - Local peak speeds at most about 2U (Ma < 0.06); hole jets at most 0.6U.
  - Density change about Ma²/2 < 0.2 %.
- **CFD note.** The lattice Mach number (0.087 at u = 0.05) is a numerical artefact, not physics. The queued Mach study (u = 0.025, 0.05, 0.1) checks that the results do not depend on it.
- **Size.** Zero.
- **Kind.** Not applicable.
- **Related: fluid–structure interaction.**
  - Dynamic pressure ½ρU² is 12 to 49 Pa at 4.5 to 9 m/s. A 1.8 mm plastic shell does not deform measurably at that load [D, A: shell modulus at least 1 GPa].
  - No FSI study of perforated sports balls was found [Lit search].

### Rank 9 (lowest) — none distinct

H2 and H3 are combined at rank 1 because the CFD cannot separate "separation-line shift caused by the holes" from "flow redistribution through the holes". Both are steady, orientation-tied forces. The force split (outer surface vs hole walls) attributes most of the force to the outer surface [P]. That points to separation asymmetry (H2) more than to through-flow momentum (H3).

## 3. Ranking table

| Rank | Mechanism | Size at 3 m (POLLEN, Re 2e4 to 5e4) | Kind | Evidence | Label |
|---|---|---|---|---|---|
| 1 | H2+H3 orientation force | 0.4 to 2 cm, steady | steady / rapid-continuous if turning | Wiffle, SSW, CFD | Lit + P |
| 2 | H1 wake wander | about 1 cm, random | rapid-continuous | sphere-wake literature, CFD | Lit + P |
| 3 | H8 internal–external coupling | damps H1 (open vs sealed 3×) | continuous | CFD, Wiffle internal flow | P |
| 4 | H6 Re transition | none in range | (rapid-continuous) | CFD Re sweep, Wiffle | Lit + P |
| 5 | H7 reverse Magnus | none found | (continuous) | CFD S sweep | P |
| 6 | H5 torque / orientation change | 1° turn per flight | continuous | CFD torque | P |
| 7 | H4 cavity resonance | 0 (2 kHz) | — | estimate | D |
| 8 | H9 compressibility / FSI | 0 | — | estimate | D |
| — | Magnus curve (reference) | 6.5 to 15 cm | continuous, repeatable | CFD, pickleball, Muto | Lit + P |

**No mechanism gives a genuinely discontinuous force for POLLEN in the FTC speed range** [P]. The largest controllable effect is Magnus lift. The largest uncontrolled effects are the orientation offset (rank 1) and the wake wander (rank 2), at about 1 cm each. Any "late break" of a constant-force path is perceptual (y ∝ t²).

## 4. NECTAR

NECTAR (about 91 mm [manual]; mass not published) has no CFD.

- At the same speed its Re is 1.28× POLLEN's: 2.7e4 to 5.5e4 for 4.5 to 9 m/s [D]. The upper end touches the Re ≈ 5.5e4 where a Wiffle ball showed a sign flip at one orientation [Lit].
- Deflection per C scales as A/m, so NECTAR could move more or less than POLLEN; **its mass must be measured first**.
- Its hole layout must come from a CAD or a physical part before any of the rankings above transfer.

## 5. What would change this ranking

- A bimodal side-force state in the 1000 D/U CFD records (CFD_TEST_PLAN §4.3), or more than 5 % of flight-length ensemble members above 5 cm (§4.4). Either would move H1 up to "discontinuous".
- A grid-converged CFD with orientation forces above 0.1, or an orientation test with offsets above 4 cm. Either would make orientation control worth building.
- A drag step in the speed sweep, which would revive H6.
