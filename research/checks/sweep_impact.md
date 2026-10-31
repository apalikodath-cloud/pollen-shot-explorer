# Fact-check: sweep_impact (oblique impacts, rim capture, trajectory reconstruction)

Checker: independent re-read on 2026-10-30. Target file: `research/sweeps/sweep_impact.md`.

How I checked:
- I re-downloaded each reachable source and extracted the text with pdftotext (layout and raw modes). Greek letters and the symbols ±, <, > are partly lost in the text layer.
- I checked every value against the printed text or table. Where a sign or glyph was lost, I rebuilt the equation and checked it numerically.
- I re-ran the derived POLLEN bounce table and the fit-noise Monte Carlo myself.

**CHECK: 16 confirmed / 5 corrected / 2 dropped / 16 added**

## Source access and review status

| id | Status | What I re-opened |
|---|---|---|
| cross2002hcor | Peer reviewed: AJP 70(5):482–489. Crossref confirms the metadata. | Author-hosted PDF of the AJP pages, full text. |
| cross2002grip | Peer reviewed: AJP 70(11):1093–1102. Crossref confirms. | Author PDF, full text. |
| cross2010tang | Peer reviewed: AJP 78(7):716–720. Crossref confirms. | Author PDF, full text. |
| cross2012liftdrag | Phys. Teach. 50(2):80–82. Crossref confirms. Education journal; it is editor- and referee-reviewed, but not a research journal. | The author preprint. It has no journal pagination. |
| nathan2006spin | Conference paper (Engineering of Sport 6) on arXiv. The text itself says the multi-dot results "will be reported at the conference". | arXiv PDF. The proceedings pages were not checked. |
| tebbe2020spin | IEEE ICRA 2020, pp. 9694–9700. Crossref confirms the DOI 10.1109/ICRA40945.2020.9196536. | arXiv v2 (16 Oct 2019). |
| okubo2004rim | Peer reviewed: Sports Eng. 7(1):15–29 (2004). Crossref confirms. | Only the Springer abstract, which I re-read verbatim. The extractor's quotes match it. |
| hubbard2005isb | ISB/ASB 2005 conference abstract, not peer-reviewed in the journal sense. | Full text, 1 page plus references. |
| antali2021rim | Peer reviewed: Nonlinear Dyn. 104:3013–3037 (2021), CC BY. | Full text. |
| haron2012cor | IOP Conf. Ser. MSE 36:012038 (2012). Crossref confirms the metadata. | **Not re-openable.** The IOP site returns a Radware bot-manager captcha to curl and to WebFetch. Unpaywall lists only the IOP copy, and Crossref and Semantic Scholar have no abstract. I did not try to get around the captcha, so **none of Haron's numbers are verified by this check**. |
| cross2014 (Exp. Mech. 54(9):1523–1536) | Peer reviewed. | Springer abstract re-read. The extractor's paraphrase is accurate. |

## Corrections (5)

1. **cross2002hcor, video accuracy (§V).** The extractor wrote "quadratic fit ≥10 frames" as if it applied to all three numbers. It does not:
   - The **horizontal** speed (±2%) came from a **linear** fit.
   - Spin was good to ±1%.
   - Only the **vertical rebound** speed (±3%) used a quadratic fit to at least 10 post-impact points.
   - The incident vertical speed agreed with √(2gh) to within 2%.
2. **cross2002grip, e_x when gripping.**
   - The tennis value (e_x 0.10–0.17 in Table III, "typically between 0.1 and 0.2") comes from the force-plate bounces at about 3 m/s. It is in **§VI and Table III, not §IV**.
   - The golf value (e_x ≈ 0.1) comes from **hand-thrown video bounces at about 4 m/s on a polished granite slab** (§VII), not from the force plate.
3. **cross2002grip, slide-throughout angles.**
   - The tennis limits (about 35° on the smooth surface with μ = 0.27, about 15° on emery with μ ≥ 0.7) are **model predictions**. They come from Eq. 7 with D = 0 and ω1 = 0, i.e. tan θ1 < 0.19/μ. The paper calls them "consistent with" Figs. 2 and 3; they were not measured directly. Location: §VI.
   - The golf ball's ≈ 40° is observed, and the model gives 39.9° (§VII).
   - Angles are measured from the horizontal (the surface).
4. **nathan2006spin, "Cd scatter 0.35–0.6".** The text gives no such numbers. Fig. 4 shows only an axis from 0 to 0.8, and the authors call their C_D "considerably less precis[e]" and "speculative": it is "nearly completely masked by the large linear term". I **removed the Cd range**. The C_L findings are confirmed: C_L ≈ 0.20, tightly clustered for S = 0.15–0.30, and below SHS for S > 0.5.
5. **cross2012liftdrag, C_D = C_L = 1.2 ± 0.1.** The value is confirmed at v = 10 m/s, but the conditions need qualifying:
   - The forces come from the Fig. 2(a) trajectory. Its spin **was not measured**.
   - The 5200 ± 100 rpm was measured on "a similar shot" (Fig. 2b).
   - Positions were filmed at 30 fps and smoothed with **6th-order polynomials**.
   - The reference area A for the cups is not stated.
   - Treat this as a demonstration value, not a coefficient.

## Dropped (2)

- **haron2012cor COR on steel** (TT 0.809→0.779, hockey 0.647→0.628, golf 0.897→0.889, cricket 0.615→0.606).
- **haron2012cor COR loss from steel to wood** (4.3%, 24.5%, 40.4%, 42.5%).
- Reason for both: the source was unreachable, so I could not verify them (see above). The extractor itself flagged that the table columns were misaligned in the text layer. Keep these numbers out of any model until someone re-reads the PDF by hand. The same applies to the Table 4 (wood) values, the "71 mm, 162 g" hockey ball, and the claim that light shells are insensitive to target compliance.

## Confirmed (16), with minor notes

- **cross2002hcor**
  - e_y = 0.77 ± 0.01 for drop heights of 0.3–1.0 m on all three surfaces, with m = 57 g and R = 33 mm (§VI).
  - μ_s from dragging a box of 4 balls with a total mass of 7.5 kg: 0.23 ± 0.02 on wood, 0.60 ± 0.03 on Rebound Ace, 0.67 ± 0.03 on emery.
  - μ_R = 0.04 ± 0.005 under a 15 kg platform.
  - e_x = 0.24 ± 0.03 (Table I: emery, θ1 = 20° from the surface, 25 cm drop). The spin was 41% above the rolling value (Rω2/vx2 = 1.41 ± 0.05).
  - The e_x range of 0.51→0.24 and the superball e_x of 0.76 are in the abstract. The superball value comes from a hand-thrown bounce on a wood floor, 15.9° from the vertical (§VIII), not from the inclined plate.
- **cross2002grip**
  - Offset D ≈ 2 mm for tennis (Table III, §VI); §IV gives D ≈ R/10. D < 0.5 mm for the superball and the golf ball (§VII).
  - e_y: tennis 0.75 ± 0.02, superball 0.97 ± 0.03, golf 0.90 ± 0.02.
  - Friction: tennis F/N = 0.27 ± 0.03 on the smooth surface, μ = 0.7–1.0 on emery, golf 0.18.
- **nathan2006spin, tracking.** 10 Eagle-4 cameras at 700 fps with a 1/2000 s shutter. Single-dot rms 1.3 mm. Fit rms 0.4 mm in y (vertical) and 12.7 mm in z (horizontal, along the flight). 100–300 degrees of freedom per fit, ~5 m track, g recovered to within 1.5%.
- **cross2012liftdrag, 70 mm ball.** The 70 mm, 10 g plastic Christmas ball is described as "less dramatic", with no numbers given. The text does not say how it was launched, so the sweep's "hand/elastic launch" is an inference.
- **tebbe2020spin**
  - Table III, backspin low/medium/high, fitted spin vs. none: 10.28/27.02/43.37 mm vs. 36.78/125.76/170.75 mm. 10 trajectories per setting, 90 in total. The no-spin baseline is a Kalman filter.
  - Table IV clustering accuracy: trajectory fitting 88.2% overall vs. 79.6% / 85.3% / 86.7% for the other methods. 50 trajectories × 9 settings.
- **hubbard2005isb.** Backspin "can scrub more energy … and can aid in capture, increasing the number of successful shots by about 10%, all other conditions held constant". The "11 ms basketball-rim impacts" is confirmed.
- **okubo2004rim.** The abstract says: "extremely sensitive to initial conditions, especially rim contact position and backspin angular velocity. Backspin aids capture on long rolling trajectories." Verbatim match.
- **antali2021rim.** Eq. 56 and Fig. 6 confirmed: in the small circular-velocity limit, |φ0 − π/2| < arctan μ, which is 45° for μ = 1. Table 1 defaults: r = 0.12 m, a = 0.01 m, R = 0.225 m, m = 0.6 kg, j = 2/3, μ = 1.0.
- **Derived POLLEN bounce table.** I reproduced it exactly with the stated inputs: 25 g, R 35.5 mm, α 2/3, 5 m/s at 45°, e_y 0.6, e_x 0.1, slide test first and then the grip branch. The only difference is rounding: the residual spin at μ 0.5 and ω 150 rad/s comes out at 30 rad/s, against 31 in the sweep. In every grip case I also checked that the tangential impulse stays within the cap |Δv_t| ≤ μ(1+e_y)|v_n|.
- **Derived fit noise.** My Monte Carlo (quadratic fit, 4000 trials) gave σ_a = 0.019 m/s² at 240 fps over 0.5 s, against 0.0195 from the formula. Over 0.25 s it gave 0.105 m/s², against 0.110 from the formula. The Magnus acceleration at 5 m/s with C_L = 0.2 is 0.475 m/s² (ρ = 1.2) to 0.49 m/s² (ρ = 1.225).

## Equations

All 10 equations are confirmed. Notes:
- **Brody sliding.** Cross's Eq. 13 carries a thin-wall factor R/R1². The sweep's form assumes R1 = R.
- **Grip threshold.** Cross's Eq. 15 is only for ω1 = 0 (and R1 ≠ R). The extractor's version, generalised to α and ω_b, is algebra derived here. I checked it and it is correct.
- **Garwin/e_x branch.**
  - Cross writes it with topspin positive. The extractor's sign flip to ω_b (backspin positive) is correct: a ball already rolling with e_x = 0 keeps v_t, and ω1 = 0 with e_x = 1 gives 0.2 v_t1 for a shell.
  - In grip2002, e_x is defined relative to the moving block's speed V (Eq. 8).
- **Tebbe.** The paper prints k_D = −½C_D ρA/m next to v̇ = −k_D|v|v, which is a sign typo. Use k_D > 0. Other details:
  - Each axis is fitted with a cubic polynomial, and ω is assumed constant over the flight.
  - The paper does state that the fit for ω does not depend on k_D. This holds because the drag term is parallel to v while ω×v is perpendicular to it.
- **Antali.** For large circular velocity the band moves to |φ0| < arctan μ, on the inner side of the rim. The ±arctan μ crest band applies only to slow rolling.
- **Impulse cap, backward-rebound condition, and noise formula.** All three are derived here; they are not taken from the sources.

## Added (16): important data the extractor missed

1. **hcor §V.** Tennis-ball impact lasted about 4 ms. At 100 fps, impact details could not be resolved.
2. **hcor §III, and Table I of the grip paper.** Wall thickness lowers I by about 17% (R = 33 mm, R1 = 30 mm), giving an effective **α = 0.55 for a real tennis ball, not 2/3**. POLLEN's α depends on its wall thickness and holes, so it must be measured.
3. **hcor Table II (h = 60 cm).** e_x by surface and angle:
   - Wood: 0.51 at 20°, 0.11 at 45°.
   - Emery: 0.18 at 20°, about 0.01 at 45° (the sign is lost in the text layer).
   - Rebound Ace: 0.18 at 20°, 0.03 at 45°.
   - At 45°, μ_A is only 0.18–0.20 on emery and Rebound Ace, against μ_S of 0.60–0.67. The ball gripped early, so the quasi-static μ_S overstates the impulse that actually occurs.
4. **hcor §VIII.**
   - Superball on a wood floor: μ_static = 0.52 ± 0.04.
   - Tennis balls on the same floor: 0.15 ± 0.02, against 0.23 on the platform. μ depends on the surface finish even for nominally similar "wood".
   - Superball e_y = 0.86 in that bounce.
5. **grip Table II.** When gripping, the ball spins faster than rolling:
   - Rω2/v_x = 1.11–1.30 for tennis.
   - 1.90 for the superball, 1.32 for the baseball, 1.27 for the basketball.
   - Table III e_x: baseball 0.21, superball 0.49, basketball 0.09.
6. **grip §VII.** The superball never slid, even at 12° from the horizontal. The model says it would slide only below 18.1° if μ = 1.
7. **grip §IV.** RΔ∫F dt fell short of the measured change in angular momentum by 30–40%, but only by 3% for the superball. This is the evidence for the offset D.
8. **grip §V.** A tennis ball's tangential oscillation period is 5.2 ms, against an impact time of about 6 ms. That allows a little more than one tangential cycle per bounce.
9. **nathan §3.**
   - 22 pitches, spin 1500–4500 rpm, S = 0.1–0.6, Re = 1.1–2.4 × 10⁵.
   - A single dot about 150° off the spin axis was tracked. The spin axis was assumed, not measured.
10. **tebbe Table IV.**
    - **Trajectory fitting classified medium and high backspin correctly only 58% and 60% of the time.** The authors say these "trajectories were not different enough".
    - Camera: 380 Hz. Ball model constants: C_D = 0.4, C_M = 0.6, m = 2.7 g, r = 20 mm, ρ = 1.29.
    - The logo-based methods needed a spin-type-dependent C_M.
11. **okubo2004 abstract.**
    - "General initial conditions almost always involve slip of the ball on the rim."
    - The ball can pass with its centre "significantly below the rim plane before rising and ultimately escaping". This is relevant to retention in a deep CELL.
12. **antali Fig. 11.** With several types of dissipation present, "the outcome of the long-time motion ('in' or 'out') can be unpredictable".
13. **cross2010tang §III (model output, not a measurement).** Inputs: tennis ball at 10 m/s, μ = 0.4, T = 5 ms, e_y = 1 assumed, θ1 = 60°, ω1 = −100 rad/s.
    - 10 kg cart: the ball rolls (rω2/v_x2 = 0.992).
    - 10 g cart with k = 1.5×10⁴ N/m: 162.8 rad/s, e_x = 0.62.
    - 1 g cart: 216 rad/s. 0.1 g cart: 223 rad/s, e_x = 0.99.
    - Spin rises most when the cart-spring period matches the impact time.
14. **cross2014 Exp. Mech. abstract.** A hollow rubber ball had much higher μ than a superball, gripped at **all** angles, and showed 1–2 friction-force reversals. e_x depends on μ and on the ratio of tangential to normal vibration frequency. Qualitative only.
15. **cross2012 text.** "No significant decrease in spin … during the first six revolutions". The cups were still spinning fast at landing and bounced back about halfway toward the launch point.
16. **cross2002hcor Table I.** The emery bounce at θ1 = 20° had e_y = 0.79 ± 0.05 and μ_A = 0.64 ± 0.05, matching μ_S = 0.67 because the ball slid. When the ball slides, μ_A gives a direct in-bounce friction measurement.

## Issues with the extractor's conclusions

- **Implication 4 compares a Δv (1–2 m/s from one contact) with an acceleration (0.49 m/s²).** The comparison should be Δv to Δv: over 0.5–1 s of flight, Magnus adds about 0.25–0.5 m/s. The conclusion that contact dominates when μ is not small still holds, but it needs to be stated in matching units.
- **α = 2/3 is not a safe default.** Real hollow balls with finite walls come out lower (tennis 0.55). Sweep α over 0.55–0.67 until it is measured.
- **Grip branch.** The model's grip branch with e_x > 0 must still enforce |Δv_t| ≤ μ(1+e_y)|v_n|. The slide/grip test uses the rolling limit (e_x = 0), so v_t2 is discontinuous at the threshold (see μ = 0.3 in the table). Add the cap check in code.
- **Use μ_A, not μ_S.** Quasi-static μ_S overstated the effective in-bounce friction at 45° by about 3× (addition 3). Calibrate μ from sliding-bounce μ_A at glancing incidence, not from a box drag alone.
- **Tebbe's 58%/60% result bears directly on the test plan.** Trajectory fitting alone may not resolve POLLEN backspin levels at high S. Spin should be measured directly, with a marker line and high-fps video near launch, and not only inferred from the fit.
- **Haron-based hints are unverified.** This includes "light shells insensitive to target compliance".
