# Fact-check: sweep_launch (flywheel/hood launcher topic sweep)

Checker: independent re-read, 2026-10-30. The extraction under check is `research/sweeps/sweep_launch.md` (same content as the JSON handed to the checker).

Sources the checker re-opened, with full text extracted locally using pdftotext:
- drane2018: MDPI PDF.
- dittrich2023: arXiv 2210.06048 v3 PDF, including the appendix Tables II and VI-VIII.
- basyiruddin2025: journal PDF at journal.uitm.edu.my, article 5666, file 3016.
- **Ponnusamy 2015**: ARPN JEAS 10(1). Read directly; the extractor only had it second-hand.
- cheng2026: IOP PDF.
- nathan2008: arXiv physics/0605041 PDF.
- vaziri2008: PMC2430338 HTML.
- couturier2022: arXiv 2111.09710 v2 PDF.
- sakai2017: J-STAGE English abstract page only. The full text is free but in Japanese and was not read.
- The two Chief Delphi threads (topics 374445 and 121186).
- The WPILib "Tuning a Flywheel Velocity Controller" page.

## Verdict

The numbers are almost all transcribed correctly. The problems are in interpretation.

**Problem 1: the claimed "measured eta_v about 0.41-0.59" is not supported.**
- Neither ratio compares measured speed with a no-slip kinematic prediction.
- basyiruddin2025's "theoretical 100 km/h" is a design target, and it already contains a x2 "safety factor" on roller rpm. True no-slip at the rated 7000 rpm would be about 198 km/h.
- Ponnusamy's 43.29 m/s comes from motor power divided by force (v = P/F), not from wheel kinematics. In that machine the ball also rode loose in a 44 mm barrel.
- None of the sources therefore gives a usable slip factor.

**Problem 2: several mechanism descriptions are wrong.**
- cheng2026 treats the ball as rigid. The Hertz law is for the PU wheel, and the paper never says "hollow".
- The basyiruddin2025 roller gap is 15 cm for a 13 cm ball. That is 20 mm of clearance, not about 2 mm. The authors propose closing it by 1-2 **cm**; Ponnusamy is the source that proposed 1-2 mm.
- The takraw ball's "perforated woven shell" construction is not stated in basyiruddin2025.

**Problem 3: some forum and docs claims are embellished.**
- UHMW was never mentioned in the hood-compression thread.
- "Bang-bang recovers fastest" is not stated on the WPILib page.
- The unit "V/(rpm)" for kV is invented; the page gives no unit.

**Good news:** the Reissner stiffness formula marked "from memory" is recoverable from couturier2022 as its zero-pressure limit, so it is now verified.

CHECK: 12 confirmed / 8 corrected / 0 dropped / 13 added

## Equations

| Extracted equation | Status |
|---|---|
| Fixed hood: v_b = u_w/2, w_b = v_b/r_b, S = 1 | **Not from any source in this sweep.** It is standard no-slip kinematics (it is Brettle's Eqs. 4-5, checked separately). Keep it, labelled as theory. |
| Two-wheel: v = (u1+u2)/2, w r_b = (u1-u2)/2 | **Confirmed in words** by nathan2008 (ATEC: "speed of the ball is determined by the average tangential speed of the two wheels and the spin is determined by the difference"). basyiruddin2025 Eq. 2 gives v = (v1+v2)/2. |
| "A roller with u2 > u1 gives topspin" | Sign-convention theory, not a source claim. |
| Slip model v = eta_v u_w/2, w = eta_w v/r_b with "measured eta_v 0.41-0.59" | **Corrected.** The model form is the extractor's own proposal, which is fine. The 0.41-0.59 range is **not** a measured slip factor (see the Verdict). Use it only as "launchers often fall well short of naive predictions". |
| Shell: linear N(delta) for delta of order t; Reissner K = 4 E t^2 / (R sqrt(3(1-nu^2))) "from memory" | **Upgraded to verified, with caveats.** See the couturier2022 derivation below. The softening F ~ delta^0.5 (Pogorelov) law is **still unverified**: neither vaziri2008 nor couturier2022 states it. |
| WPILib feedforward V = kS sgn(w) + kV w + kA dw/dt | **Corrected.** The tuning page does not print this equation. It says the plant uses "the same equation used by WPILib's SimpleMotorFeedforward" and links elsewhere. The form is the standard SimpleMotorFeedforward and is fine as a label. |
| Per-shot drop dw/w ~ E_ball/(I_w w^2), efficiency at most 50% (Pedersen) | **Corrected.** The 50% maximum total efficiency is confirmed in the Pedersen and Brettle checks (theory). The scaling dw/w ~ E/(I w^2) is the extractor's approximation. Use Brettle's exact result instead: w_wi/w_wf = 1 + (m_p + I_p/r_p^2) r_w^2 / (4 I_w). |
| POLLEN CALC: 0.002566 m/s per rpm; 3000 rpm gives 7.7 m/s and 2070 rpm spin | **Recomputed and correct.** (2π × 0.049/60)/2 = 0.0025656. 3000 × 49/(2 × 35.5) = 2070 rpm. 6-8 m/s needs 2339-3118 rpm with no slip, and 4252-5669 rpm at eta_v = 0.55. |

**couturier2022 derivation of the Reissner limit:**
- Eq. 22 defines τ = h / ([12(1-ν²)]^½ R). Eq. 29 is F = E h k1 τ w0.
- The text states that k1 → 8 for small dimensionless pressure p̂ = pR/(Eh).
- Substituting gives K = 8 E h² / (√(12(1-ν²)) R) = 4 E h² / (√(3(1-ν²)) R), which is exactly the extractor's formula.
- The authors check this against Audoly & Pomeau's p = 0 curve: slope 1.39 × 2π = 8.75, vs k1 = 8.

**Caveats on that result:**
- It is for a closed, continuous shell and holds at lowest order in contact size.
- The authors say the numerics match "for small displacements when the pressure is high enough".
- POLLEN's perforations will lower K by an unknown amount.

## Data points: verdicts

| # | Source | Extracted claim | Verdict | Detail |
|---|---|---|---|---|
| 1 | drane2018 | 1600 rpm: 18.3±0.4 m/s, 754±80 rpm, S≈0.16 | confirmed | Table 1, yellow ball. The column header reads "Wheel: 1600 ± 2 rpm". §2.2.3 indicates the dial refers to the lower wheel. S recomputed: 0.156 with R = 36.06 mm. |
| 2 | drane2018 | 2400 rpm: 33.1±0.3 m/s, 1633±46 rpm; EOL 1727 rpm | confirmed | Yellow EOL is 1727±80 at 33.1±0.4 m/s. Orange EOL is 1727±70 at 33.2±0.1. |
| 3 | drane2018 | S range 0.11-0.19 (CALC) | confirmed | Arithmetic is right. EOL radii are slightly smaller (8.82 and 8.59 in circumference), which changes S by less than 0.01. The x1.81 speed vs x1.50 rpm "dial changes ratio" explanation is speculation; falling slip at higher speed would fit equally well. |
| 4 | dittrich2023 | Robo-Pong 2050: 10.7 m/s / 106.7 s⁻¹, S≈1.25 if rev/s | corrected (interpretation) | The Table VIII values are right. The paper confirms "single wheel launch unit". However, S = 1.25 exceeds the no-slip maximum of 1 for one wheel against a fixed surface. That itself shows the max spin and max speed came from different shots. Table II says max speed is the "average speed in first 0.5 s", max spin is the "initial spin", and the paper says "Ball speeds and ball spins have been recorded independently of each other". **Do not form S from Table VIII.** The unit is printed as "s⁻¹" throughout and is never defined. |
| 5 | dittrich2023 | TTmatic 303A: 9.8 m/s / 64.0 s⁻¹ | confirmed | The paper describes it as "a single wheel and a manually exchangeable slide". The same S caveat as row 4 applies. |
| 6 | dittrich2023 | AIMY MN5008: 15.4 m/s / 192.0 s⁻¹ | confirmed | Three Butterfly hard-foam wheels at 120°. The MN4004 version reaches 10.8 m/s, with no spin value. |
| 7 | dittrich2023 | Pinch sweep std (m): 35.3: 0.032/0.031 … 38.6: 0.024/0.024; optimum squeeze 2.6-3.6 mm (6.5-9% of D) | corrected | The values match Table VI. However: (a) the Table VI header says "[mm]" while the values are clearly metres (a paper typo); (b) the main text says "increased pinching results in lower deviation", which contradicts the table and the appendix ("small and high pinching results in slightly increased deviations"; "differences … are small"); (c) "pinching diameter" is the inscribed circle of **three** foam wheels, so per-wheel indentation is (40 − d)/2 and the wheel absorbs part of it; (d) the optimum band is the extractor's CALC; 35.8 and 37.0 mm are within noise of the best. Treat it as a weak interior optimum, not a quantitative design rule. |
| 8 | dittrich2023 | Ramp 0.01 s: std x 0.040 m vs about 0.023 m for 0.5 s or more; 3 s settle | confirmed | Table VII: 0.0402 at 0.01 s and 0.0211-0.0247 m for 0.5-8 s and continuous. The "three seconds" delay is recommended in §IV-D. |
| 9 | basyiruddin2025 | 59.4 vs 100 km/h (eta_v≈0.59); deficit 34.6 → 40.6 km/h; ball 180 g, R 6.5 cm; two 15 cm EVA rollers to 7000 rpm; gap 15 cm (no squeeze); 480 fps | corrected | 59.4 km/h, the 34.6 and 40.6 km/h deficits, 180 g, R 6.5 cm, EVA Ø15 cm × 11.5 cm wide, 7000 rpm maximum and 480 fps (Casio EX-ZR70, Kinovea) are all confirmed. Corrections: (a) the "theoretical" value is 100 km/h at 100% by design. Eqs. 3-5 give 3537.6 rpm for 100 km/h, doubled to about 7075 rpm as a motor "safety factor". No-slip at the rated 7000 rpm is ω r = 733 rad/s × 0.075 m ≈ 55 m/s ≈ 198 km/h (CALC). Roller speed under load was never measured, so **no slip factor can be derived** (it could be anywhere from about 0.3 to 0.6); (b) the 15 cm gap vs the 13 cm ball is about 20 mm of **clearance**, not about 2 mm; (c) the authors suggest reducing the gap by "1-2 cm"; (d) the ball construction (woven, perforated) is not described in the paper; (e) only "the highest recorded speed" per setting was analysed, with the trial count unreported; (f) the 70% theory and measured values are figure readings; (g) the paper has a unit error, Ff = μmg = "353.16 N" for a 0.18 kg ball (it should be 0.353 N). |
| 10 | basyiruddin2025 (quoting Ponnusamy 2015) | 17.806 / 43.29 m/s, eta_v≈0.41 | corrected | **Now read directly** (ARPN JEAS 10(1):293-296, 2015). The numbers are confirmed. However, 43.29 m/s is v = P/F per motor (2.762 W / 0.1279 N) × 2 motors, so it is **not a no-slip kinematic prediction**. The measured 17.806 m/s is the mean of 5 distance/time shots with times of 0.08-0.17 s (crude). The ball ran in a 44 mm barrel for a 40 mm ball, with "loss contact" blamed. Ponnusamy is the one who suggests "1-2 mm" gap reduction. **Not usable as eta_v.** |
| 11 | cheng2026 | Modified Hertz exponent 1.5, critical compression 4.2 mm, R_eff 24.7 mm; Stribeck μs 0.5, μk 0.4; PU E 5e7 Pa, ν 0.48 | corrected | The numbers are as printed (Eq. 2: nonlinear coefficient 0.2, critical compression 4.2 mm, index 1.5, R_eff 24.7 mm; Eq. 5: μs 0.5, μk 0.4; Table 1: E = 5×10⁷ Pa, ν = 0.48). Corrections: (a) the **ball is modelled as a rigid body** (assumption 1), and Hertz describes the PU **wheel** deformation; (b) the ball is a "plastic ball" with E = 1.5 GPa and ν = 0.3, and "hollow" is not stated; (c) internal inconsistencies: ν_PU is 0.5 in the Eq. 3 text but 0.48 in Table 1; "Dynamic/static friction 0.5/0.6" in Table 2 vs μk 0.4 / μs 0.5 in the text; yield is printed as "4.5×10⁷ MPa"; and R_eff 24.7 mm exceeds the 21 mm ball radius, which is impossible for convex-convex contact. Wheel diameter is not given. |
| 12 | cheng2026 | FE exit speed 16.6-16.9 m/s at 6000 rpm | confirmed | These are the mesh-study rows of Table 3: 16.876 (coarse, 2 mm), 16.628 (medium), 16.724 m/s (fine). It is one configuration, not a range over spacings. |
| 13 | cheng2026 | 97 mm best (mean, consistency, maximum in 90% of tests); 95 mm failed; 96-99 mm at 5000/6000/7000 rpm, at least 25 shots | confirmed | 95 mm failed **in both** FE (stress above yield, jamming) and experiment ("failed to successfully launch the projectile"). Measured velocities exist only in Figs. 7-9. |
| 14 | sakai2017 | 42.5 m/s, >5000 rpm, 40 mm (140 mm gyro) | confirmed (abstract) | The citation needs completing: Sakai S. & Kitade Y., "Development of launch mechanism in ball shooting machine with four rollers", Trans. JSME 83(856):17-00225, doi:10.1299/transjsme.17-00225. Accuracy is "within the diameter of one table tennis ball" for no-spin, top and side spin, and under 140 mm for gyro. The full text is free on J-STAGE (Japanese) and unread. |
| 15 | nathan2008 | ATEC two-wheel; 50-110 mph, 1500-4500 rpm, S 0.1-0.6; CL≈0.20 at S 0.15-0.30 | confirmed | From the arXiv text ("tightly clustered around 0.20"). It covers 22 pitches at Re (1.1-2.4)×10⁵. Citation caveat: what was read is the arXiv preprint (Nathan, Hopkins, Chong, Kaczmarski; submitted to ISEA 2006). The AJP 76:119 (2008) single-author version was confirmed only through a secondary citation, and its content may differ. |
| 16 | vaziri2008 | Linear until delta is of order t; t/R = 0.005 localizes at Z/R≈0.076 with about 30% stiffness drop | confirmed | PNAS 105(23):7913-7918. Fig. 1F caption: "Z′ ∼ 0.076 … ∼30% reduction in the apparent stiffness", with Z′ = Z/R. Note that this is FE **point** indentation of a clamped 120° spherical cap. |
| 17 | couturier2022 | Small-compression shell is a linear spring independent of probe shape | corrected | The conclusion confirms it "independently of the probe geometry", but at **lowest order in contact size**, and numerics agree "when the pressure is high enough". The p → 0 limit (k1 → 8) reproduces Reissner (see Equations). The arXiv page lists no journal ref, so the EPJ E publication is unverified here. |
| 18 | cd_hoodcomp2020 | 2-2.5 in on 4 in wheels, 7 in foam ball; logged speeds "much lower" than calculated; PTFE/UHMW hood | corrected | The thread is dated 24 Jan 2020. The original poster ran two 4 in wheels at 2.5 in compression, tapering about 0.25 in at exit. A responder called 2 in the "sweet spot". "Much lower speeds than … calculated using theory" was **another responder's** experience, not the OP's logs. **UHMW is never mentioned.** PTFE was suggested **to raise exit velocity** ("non-powered surfaces as slick as possible"), with no μ measured. The ball diameter (7 in Power Cell) is game knowledge, not stated in the thread. |
| 19 | cd_ballcomp2012 | Within-ball 2.6-12.5% at 1.25 in compression; between-ball larger | confirmed | Posted 3 Apr 2012, with a 10 lb load cell. The 2.6-12.5% figure is the **run-to-run repeatability** of 5 balls × 5 passes, which includes sensor and orientation noise; it is not intrinsic stiffness variation. The load cell saturated on the hardest balls. The between-ball spread is not quantified. |
| 20 | wpilib_flywheel | Feedforward only: slow; feedforward + P or bang-bang: fast; simulation kV = 0.0075 | corrected | Feedforward only "takes a while to recover after the ball is introduced". Combined feedforward + feedback "recovers very quickly". **The bang-bang section does not discuss ball recovery**; it claims only "fast convergence to the setpoint", for slowly accelerating mechanisms. kV = 0.0075 is given **with no units**. |

## Data the extractor missed (added)

1. **drane2018 methods.**
   - Wheel speed was tracked at 1000-2000 fps.
   - Exit was filmed at 2000-3000 fps.
   - Long-range spin and location were filmed at 500 fps, with 10 balls per type and the target at 15.3 m.
   - Speed was measured by light gates 0.3 m from the wheels.
   - The lower wheel runs faster than the top wheel, which produces backspin.
2. **drane2018 wear.**
   - End-of-life (EOL) balls are estimated at more than 100,000 cycles, which is cited as reducing foam stiffness by more than 20%.
   - Mass falls by 10% (orange) and 6% (yellow).
   - Pitching consistency decreased with wear.
3. **dittrich2023 Table VII, full ramp series** (std x, m):

   | Ramp | 0.01 s | 0.05 s | 0.10 s | 0.5 s | 1 s | 2 s | 3 s | 8 s | continuous |
   |---|---|---|---|---|---|---|---|---|---|
   | std x | 0.0402 | 0.0400 | 0.0436 (worst) | 0.0211 | 0.0243 | 0.0243 | 0.0234 | 0.0247 | 0.0231 |

4. **dittrich2023 measurement definitions.**
   - Table II defines max speed as the "average speed in first 0.5 s" and max spin as the "initial spin".
   - Spin was measured at 960 fps.
   - Trajectories were tracked at 200 Hz.
5. **dittrich2023 Fig. 4.** The norm of landing-point std is 0.007-0.042 m across the four launchers and four targets.
6. **basyiruddin2025 Table 1 and Eqs. 1-5.**
   - Roller radius 7.5 cm.
   - Assumed roller μ = 0.2 and motor safety factor 2.0.
   - 3537.6 rpm computed for 100 km/h, doubled to about 7075 rpm.
   - The no-slip speed at 7000 rpm is about 198 km/h (CALC).
7. **Ponnusamy 2015, read directly.**
   - Motor FK-130SH-17102: 11452 rpm, 2.303 mN·m.
   - Five shots measured by distance/time.
   - Barrel 44 mm for a 40 mm ball; the authors expect higher speed with a 41-42 mm barrel.
8. **cheng2026 simulation inputs.**
   - Table 2: initial load 5 N, 6000 rpm.
   - Ball E = 1.5 GPa, ν = 0.3, treated as rigid.
   - PU density 1.03 g/cm³.
   - Generalized Maxwell / standard-linear-solid viscoelastic wheel, with a strain-rate-dependent modulus (Eq. 4).
9. **couturier2022 Reissner limit.** Eqs. 22 and 25 with k1 → 8 give K = 4 E h² / (R √(3(1-ν²))), checked against an unpressurized curve (slope 8.75 vs 8).
10. **vaziri2008 scope.**
    - FE in ABAQUS, E = 1 GPa.
    - t/R studied over 0.0005-0.01 under **point** load.
    - The 3-vertex mode is reversible with no hysteresis; modes with more vertices are hysteretic.
11. **nathan2008.** 22 pitches; Re = 1.1-2.4 × 10⁵.
12. **wpilib_flywheel.**
    - The ball is simulated as a load acting for "one quarter of a wheel rotation" at about 5 s.
    - kS is omitted in the simulations.
    - kA is not needed unless the setpoint changes.
13. **cd_hoodcomp2020.**
    - Two Falcon 500 motors at 90%, direct drive 1:1.
    - The OP's shooter hits reliably at about 32 ft, with a "lob".
    - The OP's 2.5 in compression tapers about 0.25 in toward the exit.

## Effect on the extractor's model implications

- **Implication 1 (slip factors).** Keep the eta_v/eta_w model form. The literature cited here provides **no measured eta_v** for any launcher, so the prior [0.45, 1.0] with a nominal of 0.7 is an engineering guess and must be labelled that way. The one quasi-quantitative compression-speed curve is the unreviewed tennis-ball plot in the Pedersen thread, covered in `research/papers/pedersen2026.md`.
- **Implication 2 (compression).** The dittrich2023 optimum is weak, comes from a three-wheel hard-foam pinch, and the paper contradicts itself on it. The cheng2026 stall margin is real: 2 mm less centre distance (about 1 mm more indentation per side) caused jamming. That applies to a rigid ball on PU wheels, not to a shell.
- **Implication 3 (shell contact).** Reissner's linear stiffness is now source-backed for a closed shell. Pogorelov softening is still unverified, and perforations are unmodelled. A measured N(δ) on POLLEN is still required.
- **Implication 4 (hood friction).** This is theory, not a finding from these sources. FRC practice (cd_hoodcomp2020) recommends a slick hood **for exit speed**, which supports a speed vs spin trade-off in hood material.
- **Implication 5 (passive roller reduces spin).** This is theory only in this sweep.
- **Implication 6 (recovery).**
  - Use Brettle's exact wheel-speed ratio, not the E/(I w²) scaling.
  - Do not cite WPILib for bang-bang recovery.
  - The dittrich2023 ramp effect is about motors not yet at speed (0.5 s threshold), not about recovery after a shot.
- **Implication 7 (ball variation).** The "up to about 12% within a ball" figure is measurement repeatability, not stiffness spread.

## Review status (checked)

| Source | Status | Notes |
|---|---|---|
| drane2018 | peer-reviewed conference (ISEA 2018, MDPI Proceedings, CC-BY) | |
| dittrich2023 | peer-reviewed conference (ICRA 2023) | The arXiv page says "Accepted for ICRA 2023". The IEEE DOI was not re-verified. |
| basyiruddin2025 | peer-reviewed regional journal (MJSSR, UiTM) | Weak methods and a unit error. |
| Ponnusamy 2015 | ARPN JEAS | A low-tier journal; the method is crude. |
| cheng2026 | peer-reviewed conference series (J. Phys. Conf. Ser., MEIMM 2026) | Several internal inconsistencies. |
| nathan2008 | arXiv preprint read; AJP 2008 version exists | |
| vaziri2008 | peer-reviewed (PNAS) | |
| couturier2022 | arXiv v2 read | The journal version is unverified. |
| sakai2017 | peer-reviewed journal | Abstract only. |
| Chief Delphi threads, WPILib docs | unreviewed | |
