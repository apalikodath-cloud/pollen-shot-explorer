# Fact-check: lindsey2025 (Lindsey 2025, "The Physics of Pickleball Aerodynamics and Trajectories")

Checked 2026-10-30 against the live page and its figure JPEGs, downloaded and inspected directly:
- https://twu.tennis-warehouse.com/learning_center/pickleball/pickleball_aerodynamics.php (full text, read in full, including the appendix and HTML comments)
- https://twu.tennis-warehouse.com/learning_center/pickleball/trajectory/trajectory_images/{All_CdvReBigSmall, variations_Cd_v0, All_FdvRe, All_CdvFd, All_FlvSvBackTop, All_AbsClvSBackTop, All_ClvSignedS2, simulation1, simulation2}.jpg
- https://twu.tennis-warehouse.com/learning_center/pickleball/pickleball_aerodynamics_light.php (the lay companion page)

Checked extraction: research/papers/lindsey2025.md (I did not edit it).

**CHECK: 12 confirmed / 5 corrected / 0 dropped / 7 added.**

## Review status and citation
- **Unreviewed web article: confirmed.** It is a Tennis Warehouse "Pickleball University" page with no journal and no DOI.
- **Byline and date:** "Crawford Lindsey, Tennis Warehouse, San Luis Obispo, CA, 93401, May 12, 2025". There is one name on the byline, but the acknowledgements say "The authors" and disclose ChatGPT-4 (April 2025) for editing, summarization and "concept refinement".
- **Data and code:** none released.
- **Section numbering:** Section 4.2 jumps to 4.2.2; there is no 4.2.1.

## Equations
| Extracted | Verdict |
|---|---|
| F_D = 0.5 C_D ρ A v², with ρ = 1.21 (Sec 1.1 eq 1) | Confirmed |
| F_L = 0.5 C_L ρ A v² (Sec 1.1 eq 2); topspin gives a downward force and backspin an upward one | Confirmed. The text says "perpendicular" only in Sec 5.1.1. |
| Re = vD/μ, with μ called the kinematic viscosity, 1.5e-5 m²/s at 20 °C (Sec 1.2 eq 3) | Confirmed. The Fig 8 dual axis implies D = 0.074 m. |
| S = Rω/v0 at launch (Sec 4.2.3) | Confirmed. The figure boxes label it "S1". |
| C_L,measured = C_L,Magnus + C_L,gravity + C_L,internal (Sec 5.1), with no functional forms given | Confirmed |
| \|C_L\| = a + bS fitted separately for each spin direction, with the intercept as "baseline" (Sec 5.3.1); coefficients read from Fig 13 | Confirmed. Topspin is about 0.24 + 0.44 S (R = 0.650) and backspin about 0.173 + 0.02 S (R = 0.042). The fitted lines are plotted for S = 0 to 0.7. |
| Appendix: a_g = g cos θ, s = (π/2) r = 0.0581 m, Δt = 0.00581 s, 0.64 g mean, Δv = ±0.0365 m/s | Confirmed. The arithmetic checks out, and 0.64 is about 2/π = 0.637. The page prints "≈ 07.4 cm/s", a typo for 7.4 cm/s. |
| Implicit simulator: m dv/dt = mg + F_D + F_L with RK4 and constant C_D and C_L | This is implied, not written. **Caution:** my reconstruction of Fig 7 (see Fig 7a and 7b in the table below) indicates that the sign of the C_L the simulator prints is **not** "positive = upward force". |

## Data points
| # | Item | Verdict | Notes |
|---|---|---|---|
| 1 | C_D, large holes: mean 0.45, SD 0.092, SE 0.013 (Sec 4.1.1); scatter about 0.245–0.71 (Fig 8) | Confirmed | |
| 2 | C_D, small holes: mean 0.33, SD 0.083 in the text and 0.082 on Fig 8, SE 0.014; scatter about 0.187–0.55 | Confirmed | |
| 3 | Fig 8 trend: large holes about 0.433 → 0.465 (R = 0.072); small holes about 0.32 → 0.333 (R = 0.035) | Confirmed (±0.01) | The data span Re ≈ 29,500–56,700, which is v0 ≈ **6.0–11.5** m/s rather than 11.6. |
| 4 | Fig 9 hole modifications | **Corrected** | **Control** (labelled "Normal"): points run about 0.59–0.985, not 0.61. Its fit is a U-shaped quadratic, 0.82 at 6.3, minimum about 0.655 near 7.8, then 0.67 at 8.25 m/s, **R = 0.54**. **Taped:** 0.355–0.81; fit 0.81 at 6.2 → 0.43 at 8.15, **R = 0.91**. **Balloon:** 0.35–0.55; fit 0.56 at 6.3 → about 0.40 at 7.9–8.15, **R = 0.84**. The axis is "Velocity (v0)", 6.15–8.25 m/s. The text attributes a "modest" drag increase to tape roughness, but above 7.8 m/s the taped and balloon points overlap (about 0.35–0.47). |
| 5 | Backspin \|C_L\| ≈ 0.175 + 0.02 S, R = 0.042; scatter 0.01–0.357; S up to about 0.365 | Confirmed | The text (Sec 4.2.3) says "≈ 0.2". |
| 6 | Topspin \|C_L\| ≈ 0.24 + 0.44 S, R = 0.650 | Confirmed | Scatter is about 0.125–0.625; the extraction said 0.13–0.62. S goes up to 0.655. |
| 7 | Low-spin C_L: topspin −0.24, backspin +0.17 (Sec 5.3) | Confirmed | |
| 8 | Fig 14 signed fit and boxed clusters | **Corrected** | The line C_L ≈ −0.05 − 1.0·S_signed (R = 0.83) is confirmed. The **upper (backspin) box** holds C_L +0.08 to +0.25 and is **mixed**, about half small-hole (blue) and half large-hole (red). The **lower (topspin) box** holds −0.15 to −0.42 and is **entirely large-hole**. "Mostly large holes" is therefore true only of the lower box. |
| 9 | \|F_L\| vs S (Fig 12): topspin 0.052 + 0.026 S (R = 0.38), range 0.024–0.084 N; backspin 0.043 − 0.057 S (R = 0.52), range 0.001–0.061 N | Confirmed | "Falls with S because of the S–v0 coupling" is the extractor's interpretation, not a statement in the source. It is plausible because F_L ∝ C_L v². |
| 10 | F_D 0.02–0.146 N; fits for large holes 0.02 at Re 2.85e4 → 0.133 at 6e4 (R = 0.814) and small holes 0.02 at about 3.25e4 → 0.105 at 6e4 (R = 0.717) | Confirmed | The 0.146 N maximum is a **small-hole** point. A linear F_D(Re) fit is non-physical (F_D ∝ v²). |
| 11 | Fig 7a: v0 10.72, ω 60.40 rad/s (576.8 rpm), θ 147.34°, S1 0.21, SSE 0.0098, endpoint error 0.0156 m, C_D 0.4361, C_L −0.5763 | **Corrected** (interpretation) | All the numbers are confirmed, and S = 0.037·60.4/10.72 = 0.208 checks. However, θ = 147.34° means a **leftward launch at 32.7° elevation**. The track covers only the rising part: (0, 0) to about (−3.2, 1.0) m. In my reconstruction (m = 20–30 g, ρ = 1.21, r = 0.037) a no-lift path reaches about 1.34–1.37 m at x = −3.18 m and is still climbing, while C_L = −0.576 applied **downward** reproduces the roughly 1.0 m flattening. The shot is therefore physically **topspin**, so the conclusion that the caption ("backspin") is wrong survives. But the sign of C_L is not, by itself, proof of spin direction (see the next row). |
| 12 | Fig 7b: v0 10.16, ω −39.60 (378.2 rpm), θ 161.42°, S1 0.14, C_D 0.4785, C_L +0.4773, SSE 0.0043, endpoint error 0.0011 m | **Corrected** | The numbers are confirmed, and S = 0.144 checks. The extractor's claim that "positive C_L indicates backspin" is **contradicted**. Observed: launch leftward at 18.6°, apex 0.345 m at x ≈ −1.95 m, track ending at (−3.38, **0.18**) m. A ball with no lift would peak at about 0.47–0.49 m. An **upward** 0.477 C_L gives a path still rising at about 0.75 m at x = −3.38. A **downward** 0.477 gives an apex of 0.339–0.348 m at x = −2.0 to −2.05 and y = 0.16–0.19 m at −3.38, which matches the observed track. So 7b is **topspin**, consistent with its caption, and the printed C_L sign is evidently tied to the ω or travel-direction convention. "Range ≈ 3.4 m" is the tracked horizontal extent, not the landing range. Drop the statement that this "C_L 0.477 exceeds every backspin point in Fig 13": it is a topspin point. |
| 13 | 86 trajectories, mean endpoint error 15 mm (Sec 3.2) | Confirmed | |
| 14 | Maximum S tested and implied ω | **Corrected** (precision) | Backspin \|S\| reaches about 0.37–0.375 (Fig 14 −0.375; Fig 13 0.365) and topspin about 0.655. The implied backspin ω for the highest-S shot is somewhere in 0.37·(6.0–11.5)/0.037 ≈ **60–115 rad/s (570–1100 rpm)**. That is a bound, not a value: because of the S–v0 coupling, the high-S shots probably sit at the low v0 end. The source reports no rpm except the two Fig 7 examples. |
| 15 | Constants: ρ 1.21, ν 1.5e-5, r 0.037, g 9.8, 300 fps | Confirmed | Ball mass m is defined in Sec 1.1 but **never given a value**. 300 fps is the camera rate, not a constant. |
| 16 | Appendix numbers: ±0.0365 m/s, 7.4 cm/s, rounded to 0.07 m/s | Confirmed | See the typo noted under Equations. |
| 17 | Prior work as cited: Steyn, C_D ≈ 0.30 ± 0.02 and C_L ≈ 0.195·S from 6 outdoor trajectories; Emond, fixed C_D = 0.6 with no lift | Confirmed as **secondary** citations | Verify against the primary papers. |

## Added (missed by the extractor)
- **A1 (Fig 11):** C_D vs F_D has R = 0.563 for large holes and 0.679 for small holes, with a positive slope. This is largely self-correlation, since F_D is computed from C_D and v.
- **A2 (Fig 14 ball-type split):** small-hole backspin shots reach only |S| ≈ 0.2. Every backspin point with |S| > 0.2 is a large-hole ball, so the Fig 13 backspin data above S ≈ 0.2 come from one ball type.
- **A3 (Fig 13 counts, my approximate count, ±3):** about 39 backspin and about 47 topspin shots. The source gives no split.
- **A4 (Sec 4.1.3):** the author's interpretation is that the flow is "supercritical", with no drag crisis in Re 3–5.7e4 and C_D flat or slightly rising. This is an interpretation, not a measurement.
- **A5 (Sec 5.2):** the author speculates, with no data, that at higher speed and spin backspin would regain a C_L–S dependence.
- **A6 (lay page):** it says "over 80 full trajectories" and claims "even balls launched straight and flat with no spin still bent downward". That contradicts the main paper's own Fig 14 upper box (S ≈ 0, C_L +0.08 to +0.25) and its Sec 5.3 (+0.17). The lay page also says backspin shows "diminishing returns". This is a popular summary, not data.
- **A7 (my Fig 7 reconstruction, not in the source):** both example shots need a net **downward** lift. A no-lift path gives apex or height about 0.36 m (7a) and 0.13 m (7b) above what was observed, and this does not depend on mass over 20–30 g. Neither published example is a backspin shot.

## Corrections to the extractor's interpretive text
- **Backspin model family.** Under the author's own baseline decomposition, the backspin Magnus part is C_L,Magnus = |C_L| − a ≈ **0.02·S**, which is about 0.007 at S = 0.37, essentially zero. The source cannot tell apart:
  - (i) a real lift plateau of about 0.17 reached by S ≈ 0.03; and
  - (ii) an offset of about 0.17 of unknown origin plus almost no Magnus lift.

  The extractor's family (b), 0.18·tanh(S/0.08), treats the whole offset as spin lift, which is option (i). The pessimistic option should include C_L(S) ≈ 0 to 0.02·S. At S ≈ 0, the shots labelled backspin still read +0.08 to +0.25 and the ones labelled topspin −0.15 to −0.42. The label itself therefore carries the sign, which points to under-measured spin at 300 fps, or to an effect that is not Magnus. Either way, the evidence is weak for a spin-proportional backspin lift.
- **POLLEN scale factor.** 0.5ρA/m = 0.0960 for ρ = 1.21, r = 0.0355 m and m = 24.95 g (the AndyMark nominal in HANDOFF). The extractor's 0.0970 needs ρ ≈ 1.225. The difference is negligible: at C_L 0.18 and 10 m/s it gives 1.73 vs 1.75 m/s².
- **Buoyancy:** about 2.2 mN, 0.9 % of the weight. Confirmed.
- **"Spin decay ignored":** the source does not say so. With one constant C_L per shot, ω(t) plays no part in the fit. The source lists time-resolved spin tracking as future work.
- **"Pickleball 74 mm, 22–26.5 g (USA Pickleball)":** not from this source. Keep the label "from memory, unverified".
