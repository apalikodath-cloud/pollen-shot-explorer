# PM-001 empirical cross-check: what does one powered wheel deliver in exit speed and backspin?

Compiled 2026-10-30. Machine-readable rows are in `crosscheck/empirical/evidence.json` (27 rows).
S = |omega| R_ball / v (HANDOFF section 4). Units are SI. Every number carries a label:
**confirmed** (stated in the cited source), **user** (HANDOFF), **assumed**, **derived** (computed here), **predicted** (model output).

## 0. Bottom line

1. **Nobody has published a measured spin rate for an FRC, FTC or VEX single-wheel hooded shooter.** I searched team binders, Chief Delphi, FTC BIOBUZZ threads and repos, and GitHub. The common claim that S is about 1 is a no-slip derivation (Pedersen 2026; Brettle; CD posts). Even the derivation's author says it is not validated.
2. **Exit speed is measured, but only roughly.** v/u (exit speed over wheel surface speed) is about 0.30 to 0.45 (confirmed; forum posts with eyeballed video and guesses; CD 394940). The ideal is 0.5. Several sources independently say that **speed and spin are locked together for a single wheel**: Newgy Robo-Pong (confirmed), Team 254 2017, and CD 384788.
3. **Rigid-contact kinematics bound S from below at about 1 for a wheel plus a non-driven far surface** (derived, section 3). This holds whether that surface is a stationary hood or a free passive roller. Wheel slip lowers v but not S. Hood slipperiness and roller lightness push S **up**, toward 1/k ≈ 1.5 to 1.7, where k = I/(mR²) ≈ 0.60 to 0.667 for a hollow shell (assumed). A passive roller therefore does not reduce backspin. It adds backspin relative to a grippy hood.
4. **Realistic S at exit for one 98 mm wheel + POLLEN** (predicted; the bands are not measured):

| Configuration | S band | Central guess | v/u band |
|---|---|---|---|
| Fixed hood, grippy (rubber, foam, grip tape), 4 mm compression | 0.9 – 1.3 | 1.0 – 1.15 | 0.30 – 0.50 |
| Fixed hood, slick (PTFE, polished aluminium) | 1.1 – 1.6 | about 1.3 | 0.30 – 0.45 |
| Passive (free) roller in place of hood | 1.0 – 1.6 | 1.15 – 1.3 (10–25 g effective roller mass) | 0.33 – 0.47 |
| One motor with a belt-linked top roller (not "passive") | about 0 – 1, set by the surface-speed ratio | — | up to about 1.0 |
| Two powered wheels (context only; not the requested mechanism) | 0.1 – 0.6 measured on baseballs (Nathan 2006, confirmed) | — | about 1.0 |

   The 0.9 floor allows for spin decay between exit and the measurement point, and for the fact that POLLEN is neither perfectly spherical nor rigid (HANDOFF section 0). **Confidence is low.** No row in the table is a spin measurement of this mechanism. One slow-motion test session would replace every band above (protocol in section 6).

## 1. Evidence table

Reliability grades: A = peer-reviewed measurement; B = primary team document with test outcomes; C = forum post with rough numbers; D = anecdote, snippet or unretrieved; T = theory only.
"—" means not reported.

| # | Source | Ball | Wheel dia (m) | Config | Measured v (m/s) | Measured spin | S | Method | Rel. |
|---|---|---|---|---|---|---|---|---|---|
| 1 | [Pedersen / FRC 449 2026](https://robot.mbhs.edu/media/whitepapers/2026/flywheel-calculations-latest.pdf) | generic | — | 1 wheel + hood; hood roller with ratio G | u/2 (predicted) | ωR = u/2 (predicted) | 1.0 (predicted) | analytic no-slip; author: not validated | T |
| 2 | [Brettle, Flywheel Shooter Analysis](https://docs.carlmontrobotics.org/jupyter_notebooks/files/FlywheelShooter.html) | generic | — | 1 wheel + hood | u/2 (predicted) | v/R (predicted) | 1.0 (predicted) | analytic | T |
| 3 | [Team 254 2017 binder pp.16–17](https://media.team254.com/2017/09/964207d8-technicalBinder2017.pdf) | 2017 FUEL: 5 in ResisDent wiffle, about 74 g | 0.1016 (confirmed) | twin backspin flywheels, fixed hood 14°, 12.7 mm compression, 3500 rpm | — (ideal at most 9.3, derived) | — (if S=1: 147 rad/s, derived) | — | accuracy: 15 fuel/s at 85% | B |
| 4 | Team 254 2017 blog ([search summary](https://www.team254.com/category/frc/2017-frc-build-season/?order=asc)) | 2017 FUEL | — | single flywheel + hood; then reversed for front spin | — | — | — | qualitative: veer depends on hole orientation | D |
| 5 | [CD 154962](https://www.chiefdelphi.com/t/how-spin-affects-fuel-trajectory/154962) | 2017 FUEL | 0.2032 (Team 639) | flywheel shooters | — | — | — | lateral scatter about 0.15 m; range inconsistent | D |
| 6 | [CD 370303](https://www.chiefdelphi.com/t/infinite-recharge-ballistics/370303) | 2020 POWER CELL, 7 in foam | 0.1016 (example input) | single-wheel hooded (general) | — | — | — | video: horizontal deceleration 16–19 m/s² (confirmed, rough) | C |
| 7 | [CD 374134](https://www.chiefdelphi.com/t/has-anyone-tested-a-cell-shooter-with-topspin-instead-of-backspin/374134) | 2020 POWER CELL | — | 2 flywheels, 27% speed delta | — | — | — | qualitative: backspin flatter and more consistent; topspin more bounce-outs | D |
| 8 | [CD 374445](https://www.chiefdelphi.com/t/hood-compression/374445) | 2020 POWER CELL | 0.1016 | wheel + hood, 64 mm compression | — (range about 9.75 m, derived) | — (asked, unanswered) | — | range test; current logs gave "much lower speeds" than theory | C |
| 9 | [CD 394940](https://www.chiefdelphi.com/t/determine-flywheel-velocity-for-ball-exit-velocity/394940) | POWER CELL (assumed) | — | wheel + PTFE hood | about 9.1 vs surface 21.3 (confirmed, eyeballed) → v/u ≈ 0.43 | — | — | slow-motion video; others: 0.30 "standard", 0.20–0.45 guess | C |
| 10 | [CD 400745](https://www.chiefdelphi.com/t/how-to-reduce-backspin-while-still-maintaining-accuracy/400745) | 2022 CARGO, 9.5 in | — | hooded single wheel | — | — | 1 (predicted, no-slip) | qualitative: backspin caused Upper Hub bounce-out | D |
| 11 | [CD p=1179875 (Holley)](https://www.chiefdelphi.com/forums/showthread.php?p=1179875) | 2012 foam basketball | 0.1524 | 1 wheel + aluminium hood, 51 mm compression, 4000 rpm | — (surface 31.9, derived) | — | — | strobe tachometer on wheel; "backspin was key" | B |
| 12 | [CD p=1157392 (Team 525)](https://www.chiefdelphi.com/forums/showthread.php?p=1157392) | 2012 foam basketball | 0.1524 | 1 Colson + adjustable hood, about 50 mm compression | — | — | — | load cell measured each ball's squish | B |
| 13 | [CD 384788](https://www.chiefdelphi.com/t/2-wheel-hooded-shooters/384788) | POWER CELL | 0.1016 + 0.0508 top, same 1:1 belt | 1 wheel + hood vs belt-linked top wheel | — | — | — | qualitative: single wheel gives "all back spin" | D |
| 14 | [CD 509433](https://www.chiefdelphi.com/t/tracking-the-path-of-a-ball-leaving-a-flywheel/509433) | 7 in ball | — | flywheel + flat back | — | "definitely backspin" | — | none; claim: skidding raises v and lowers spin | D |
| 15 | Team 254 2026 blog ([search summary](https://www.team254.com/?p=12143)) | 2026 REBUILT FUEL | — | backspin vs topspin prototypes | — | — | — | qualitative; backspin preferred | D |
| 16 | [Newgy Robo-Pong 2040 FAQ](https://www.megaspin.net/store/extra/robopong-2040-faq.asp) | 40 mm table-tennis ball | — | 1 wheel + stationary friction block | 4.5–33.5 (confirmed spec) | not published | — | manufacturer: speed and spin only proportional; no "floaters" | B |
| 17 | [Nathan et al. 2006](https://arxiv.org/pdf/physics/0605041) | baseball | — | **2-wheel** machine | 22–49 (confirmed) | 157–471 rad/s (confirmed) | 0.1–0.6 (confirmed) | 700 fps motion capture | A |
| 18 | [Drane et al. 2018](https://www.mdpi.com/2504-3900/2/6/203/pdf) | foam cage balls | — | wheel ratio vs v and spin | not retrieved (HTTP 403) | not retrieved | — | light gates + high-speed video | D |
| 19 | [Pickleball, Lindsey 2025 (TWU web article)](https://twu.tennis-warehouse.com/learning_center/pickleball/pickleball_aerodynamics.php) | perforated hollow, D 0.074 | — | pendulum strike | 6.0–11.5 (confirmed: fitted data span, Re 2.95e4–5.67e4; launcher range stated as 5–13) | rpm not reported | backspin ≤ 0.37, topspin ≤ 0.65 (confirmed, figure reading) | 300 fps fit: Cd 0.45 / 0.33, backspin \|Cl\| ≈ 0.173 + 0.02 S (confirmed, figure reading) | C† |
| 20 | [Kim, Choi, Park JFM 2014](https://cambridge.org/core/journals/journal-of-fluid-mechanics/article/inverse-magnus-effect-on-a-rotating-sphere-when-and-why/0E9FEF2880AA45C8B12587374C6F10EE) | smooth sphere | — | wind tunnel | — | — | 0–0.5 | inverse Magnus at Re 0.6–2.6e5 | A |
| 21 | Rossmann & Rau 2007 AJP ([coverage](https://news.lafayette.edu/2008/01/04/andrew-rau-08-and-professor-jennifer-rossmann-publish-in-national-physics-journal/)) | Wiffle ball | — | wind tunnel | — | — | — | side force depends on hole orientation | A* |
| 22 | [FTC 14343, CD 524080](https://www.chiefdelphi.com/t/ftc-14343-escape-velocity-biobuzz-build-thread/524080) | **POLLEN** | — | Ri3D fixed solid hood | — | — | — | 19/43 bounce-out (44.18%, confirmed) | D |
| 23 | [REV Robotics video](https://www.youtube.com/watch?v=SCXx9jgLQh0) | **POLLEN** | — | backspin shot | not retrieved | not retrieved | — | video | D |
| 24 | [Red Beard Pandas video](https://www.youtube.com/watch?v=KgGD0N0FKNM) | **POLLEN** | — | not retrieved | — | — | — | video | D |
| 25 | [CyberCoyotes #21](https://github.com/CyberCoyotes/2026-2027-BIOBUZZ/issues/21), #7, #43 | **POLLEN** | 0.1016 + 0.051 powered hood wheel | **2 motors**; hood/flywheel rpm ratio 2.0 | — | — (tables blank) | — (about 0 by design, derived) | planned striped-ball video | D |
| 26 | [Advik123 sim](https://github.com/Advik123/FTC-BioBuzz-Shooter-Sim) | POLLEN (model) | — | simulator | — | — | — | assumed Cd 0.5, Cl = min(0.35, 0.6 S) | T |
| 27 | Pitching-machine patents US7806788, RE30703 | baseball/softball | 0.23–0.46 | 1 wheel + fixed pad/rail | — | — | — | patent text: one wheel always spins the ball | D |

*A\*: peer-reviewed, but only secondary coverage was read.*

*†: row 19 is an unreviewed single-author web article with its own measurements (no peer review, no data released), graded C. It was previously mislabelled "Emond/Sun/Swartz 2024", grade A. Emond et al. 2024 is a different paper: a pure simulation with an assumed Cd 0.6 and no lift (research/papers/emond2024.md).*

## 2. What the qualitative evidence agrees on

- **The spin direction follows the geometry** (confirmed; patents, CD 384788, Newgy). The surface on the far side of the ball from the wheel is the slow side. Wheel below with hood above gives backspin. Wheel above with hood below gives topspin.
- **Backspin flattens the trajectory and is usually more consistent than topspin** (CD 374134, 400745; Team 254 2017 and 2026; 2012 Holley). The same backspin also **causes bounce-out from a horizontal or rimmed goal** (2022 CARGO; 2020 3322 for topspin; FTC 14343 with POLLEN: 44% of balls that reached the HIVE bounced out). This is the key tension for BIOBUZZ.
- **Perforated balls veer depending on hole orientation** (Team 254 2017 snippet; Rossmann & Rau; CD 154962). More spin did not cure the veer for 254. In the end they still chose backspin with proper compression. The repeatability scatter from hole orientation is real and is not captured by any Cd/Cl constant.
- **Compression is the main tuning knob, and ball-to-ball variation matters.** Team 525 measured the squish of every ball with a load cell. Values in use: 12.7 mm on a 127 mm FUEL (10%), 51 mm on an 8 in basketball (25%), and 51–64 mm on a 7 in POWER CELL. The HANDOFF 4 mm on a 71 mm POLLEN is 5.6% of diameter (derived), well below these and close to the low end. Expect more wheel slip and lower v/u than FRC teams saw.
- **Slip is large in practice.** The best FRC estimate of v/u is 0.30 to 0.45. Teams that compared calculator predictions with current logs saw "much lower speeds" than theory.

## 3. Derived kinematic bounds (why S does not go below about 1 without a driven second surface)

Model (derived): a rigid ball sits between a wheel (surface speed u) and a far-side surface that is not driven. The ball starts from rest. Coulomb friction acts at both contacts. k = I/(mR²).

- Ball rolls on the far surface (grippy hood, or a very heavy roller): v = ωR, so **S = 1**. If the wheel does not slip, v = u/2; if it slips, v < u/2.
- No tangential force at the far surface (frictionless hood, or a massless free roller): the wheel impulse gives Δv = J/m and Δ(ωR) = J/(km), so **S = 1/k**. If the wheel does not slip at exit, v = k/(1+k)·u.
- In between, hood friction acts forward on a ball whose far-side surface runs backward. It always drives S toward 1 from above. **It never drives S below 1.** A phase with only hood contact also relaxes S to 1 (rolling). A phase with only wheel contact pushes S up.
- Compression lowers the effective rolling radius at the hood: S ≈ R/(R − δ). For 2–4 mm, S ≈ 1.06–1.13 (derived).

A numerical sweep (derived) used a 25 g ball, μ_wheel 0.8, normal force 10–60 N and contact time 4–10 ms:

| Far surface | k = 0.667 | k = 0.60 |
|---|---|---|
| hood μ = 0 | S = 1.50 | S = 1.67 |
| hood μ = 0.05 | S = 1.12 – 1.33 | S = 1.22 – 1.47 |
| hood μ = 0.1 | S = 1.00 – 1.18 | S = 1.00 – 1.30 |
| hood μ ≥ 0.2 | S = 1.00 – 1.01 | S = 1.00 – 1.03 |
| free roller, effective mass J/r² = 0 / 2 / 5 / 10 / 25 / 100 g | 1.50 / 1.40 / 1.31 / 1.23 / 1.13 / 1.04 | 1.67 / 1.53 / 1.40 / 1.29 / 1.15 / 1.05 |
| free roller, 10 g, still turning backward from the previous shot (−0.2u) | — | S = 1.56 (k = 0.62) |

In the sweep v/u ranged from 0.06 (weak grip, short contact) to 0.50. **The FRC-observed 0.30–0.45 is compatible with S = 1.** Wheel slip alone does not tell you the spin.

Consequences:

- A PTFE hood, which FRC posters suggest for more exit speed, should **raise** S and lower v, unless the wheel was the slipping contact. Weldingrod1 (CD 509433) says skidding lowers spin. That is not reproduced for skid at the hood. It may refer to a different geometry.
- The 2017 idea (CD 154962) that a roller arc removes backspin is not supported by this model. A free roller removes the hood's friction, and that friction was what held S down at 1.
- **S < 1 needs the far surface driven forward.** Options are a powered counter-roller (dual-powered; not the HANDOFF default), or a top roller **belt-linked to the same motor** (CD 384788 describes 4 in + 2 in on one 1:1 belt). Linked roller kinematics (predicted, Pedersen with ratio G): ωR_b = (u − u_top)/2 and v = (u + u_top)/2. This is a one-motor way to tune S anywhere from about 0 to 1. Flagged for the lead.

## 4. Magnus behaviour of perforated hollow balls (what sign to expect for POLLEN)

- POLLEN Re = vD/ν ≈ 2.4e4 at 5 m/s and 5.7e4 at 12 m/s (derived; D = 0.071 m, ν = 1.5e-5 m²/s). The inverse Magnus window for smooth spheres in Kim et al. (Re 0.6–2.6e5, S ≤ 0.5) lies above this range (derived). In any case, perforations remove the smooth-sphere transition behaviour.
- The closest measured analog is the **pickleball**: perforated hollow plastic, D 0.074 m, Re 2.95e4–5.67e4 (confirmed: fitted data span, v0 ≈ 6.0–11.5 m/s; Lindsey 2025, an unreviewed web article). Backspin produced **positive lift Cl ≈ 0.2, nearly flat with S** over S ≤ 0.37 (confirmed); the fit is |Cl| ≈ 0.173 + 0.02 S, and the source cannot say whether the 0.17 offset is Magnus lift. No reverse Magnus for backspin was reported. Cd was 0.33–0.45 with no drag crisis (confirmed). HANDOFF section 5 forbids using these as POLLEN coefficients. They do support **normal-sign Magnus lift with backspin, plausibly saturating near Cl 0.2 at S ≈ 1**, as a hypothesis to test.
- Wiffle-type asymmetric perforation produces orientation-dependent side force even without spin (Rossmann & Rau). POLLEN hole symmetry is not verified here. Treat lateral scatter as a repeatability term, not as noise to fit away.
- FRC POWER CELL foam: posters reported Magnus as "definitely non-negligible" and a horizontal deceleration of 16–19 m/s² (confirmed, rough). This is a different ball and is not transferable.

## 5. BIOBUZZ POLLEN reveals (anecdotal)

- **FTC 14343 Escape Velocity** (CD 524080, 2026-09-27): Ri3D fixed-solid-hood shooter. Of 43 balls that reached the HIVE, 19 bounced out (44.18%, confirmed). The subgroup counts (27 + 15 = 42) do not reconcile. Distance, HIVE side and orientation are not stated. The team blames backspin and plans powered counter-rollers. This is the only POLLEN outcome data found, and it is one session.
- **CyberCoyotes** (GitHub #21/#7/#43, October 2026): a 4 in flywheel plus a 2 in hood wheel on a **second motor**, with a 2.0 rpm ratio as "best so far". By design that gives near-equal surface speeds, so near-zero spin (derived). A spin video was planned but no spin or speed was recorded. The flywheel reached only 1080 of 1300 rpm because the belt was over-tight and the supply sagged to 9.5–10 V. This is a reminder that the wheel rpm under load is not the setpoint.
- **REV Robotics**, "Pollinate the Hive With This Backspin Technique!", and **Red Beard Pandas**, "Propelling Pollen and Nectar": these are video-only and I could not retrieve their content. The REV snippet favours backspin over a lob.
- Simulators (Advik123 and others) contain assumed coefficients only, no data.

## 6. Recommended measurement (replaces the bands in section 0)

- **Camera:** side-on, perpendicular to the shot plane, about 1 m away, with a scale grid in the plane. **Use 480 fps or more; 240 fps is the minimum.** At v = 8 m/s and S = 1 to 1.5, POLLEN spins at 36–54 rev/s (derived). That is about 4–7 frames per revolution at 240 fps, and you need at least 2 frames per revolution plus margin.
- **Ball:** mark a full great-circle stripe plus a dot. Log the hole orientation at load if possible.
- **Spin measurement:** measure v and ω over the first 0.1–0.2 m after exit, and again about 1 m downstream to check spin decay. Record wheel rpm under load from the encoder, not from the setpoint.
- **Sweep:** cover hood material (grippy vs PTFE), compression (2, 4, 6 mm), passive roller vs hood, and 3 rpm levels, with at least 10 shots per cell. Report the mean and spread of v/u and S. One shot proves nothing (HANDOFF).

## 7. Open leads

- Drane et al. 2018 (MDPI Proc. 2(6):203): measured spin vs wheel-speed ratio on foam balls; returned HTTP 403. Get the PDF manually.
- The REV and Red Beard Pandas videos need a human to watch them. Slow-motion clips could give a first S estimate.
- Rules: a search snippet suggests TU07 penalises launches that strike the CELL's external faces. The lead should check TU07 sections 10–11 before relying on bank shots or "rim-roll" shots. This is outside my scope and unverified.
- POLLEN wall thickness and hole pattern set k and the orientation effects. Measure the ball mass distribution, or section a ball.
