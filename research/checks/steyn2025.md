# Fact-check: Steyn et al. (2025) — Executing a successful third shot drop in pickleball

Checker: independent re-read of the source, 2026-10-30. This checks the extraction in `research/papers/steyn2025.md`.

## Sources re-opened
- The arXiv abstract page (https://arxiv.org/abs/2501.00163). Only v1 exists, submitted 2024-12-30.
- The arXiv TeX source (https://arxiv.org/src/2501.00163): main.tex, main.bbl and the 4 figure JPGs. I read every equation, caption and bullet verbatim and inspected every figure.
- The SportRxiv preprint PDF (https://sportrxiv.org/index.php/server/preprint/download/499/1073/997), dated 2025-01-02. It is identical in content to arXiv v1: same equations, the same misprints and the same captions.
- Crossref metadata (https://api.crossref.org/works/10.1177/17479541251365200):
  - Journal: IJSSC 21(3):1929-1935.
  - Published online 2025-08-12. Print issue June 2026.
  - Licence: CC BY 4.0.
  - The abstract deposited with the version of record (VoR) contains the same speed and angle ranges and the same "spin secondary" conclusion as the preprint.
- The SAGE version of record: HTML, PDF and full-xml all return 403 to curl and WebFetch. **Not read.**
- My re-implementation of their Eqs. (2)-(3) (explicit Euler, dt = 1e-4) is a scratchpad script, `chk/steyn_verify.py`.

## CHECK: 18 confirmed / 4 corrected / 1 dropped / 6 added

### Confirmed (18)
- Cd = 0.30 +/- 0.02, with no systematic trend with S or Re (App. A.2, Eq. 5).
- Cl = 0.195 S, forced through the origin, with large scatter (Eq. 6).
- Measured ranges for the 6 shots: initial Re 4.7e4-6.1e4 and S 0.03-0.3.
- Fig. 4 caption: 10.0 m/s, 31 deg, Re 5.4e4 -> 4.9e4, 5.9 s^-1, S 0.14, 1.42 s.
  - The conversions are correct: 5.9 rev/s = 354 rpm = 37.1 rad/s.
  - S = 2*pi*0.037125*5.9/10 = 0.138.
- Fig. 4 read from the figure:
  - First point at about (1.0, 1.2) m.
  - Apex about 2.33 m at x of about 4.5-4.6 m.
  - The curve reaches z = 0 at about 9.25 m.
  - 14 plotted points.
- Position error "not greater than twice the ball diameter". The extractor's conversion to about 0.15 m is correct.
- Camera: one frame every 0.008 s; every 10th frame used; "roughly 12 to 20 points" (elsewhere "10 to 20").
- Air constants as printed: rho = 1.29 kg/m^3 and "nu = 1.78 kg m^-1 s^-2".
  - The extractor's reading of mu = 1.78e-5 Pa s is CORROBORATED. With Re = 2 r rho u / mu, I get 5.38e4 at 10 m/s, matching the Fig. 4 caption's 5.4e4, and 6.46e4 at 12 m/s, matching the Fig. 1 caption's 6.4e4.
  - The printed formula Re = 2 u rho / nu also omits r.
- Fig. 1 landing points: about 10.37 / 9.25 / 8.4 m.
- Fig. 1 apex heights: about 1.68 / 1.55 / 1.44 m at x of about 4.8 / 4.1 / 3.6 m.
- About 8.7 m/s is the minimum speed to clear the net (Sec. 1.3).
- About 13.5 m/s is the speed above which the ball always lands beyond the kitchen line (Sec. 1.3).
- Drop windows (abstract, Sec. 1.3, Conclusions):
  - Down-the-line: 10.9-13 m/s at 15.5-22.5 deg.
  - Cross-court: 13.3-16 m/s at 12.5-18 deg.
- "Spin up to 15 s^-1 possible, limited by ball and paddle roughness" cites `pballspin` = C. Lindsey (2022), "Pickleball Spin - The Role of Surface Roughness in Spin Generation", twu.tennis-warehouse.com. That is an unreviewed web article. The authors also judge such rates "unlikely" for recreational players and say backspin this high will be "difficult to achieve".
- Fig. 1 contradicts the z-equation, as the extractor said. Under Eq. (2), positive Cl gives upward lift, yet the caption labels the longer green backspin curve "Cl = -0.12".
- The x-equation (Eq. 3) is printed with (Cd cos(theta) - Cl sin(theta)). For lift perpendicular to v it should be (Cd cos(theta) + Cl sin(theta)). The extractor's flag is correct.
- The forces are printed without the 1/2 (F = Cd rho A u^2), while Eqs. (2) and (3) include rho A / 2m.
- The introduction says Emond's Cd is 0.6; the appendix says Emond "assumed C_d = 0.0". Confirmed misprint.

### Corrected (4)
1. **Fig. 1 inputs.**
   - The caption gives Cd 0.30, 12 m/s, 20 deg, "10.0 s^-1", S 0.19, Cl +/-0.12 and Re 5.3-6.4e4.
   - z0 = 0.75 m is **not in the caption**. It comes from the Sec. 1.2 text (struck at x = 0, z = 0.75 m) and from the curve's start in the figure.
   - The caption does not say rev/s. That unit is inferred from S: 2*pi*0.037125*10/12 = 0.194.
   - The extractor's note that self-consistent Cl = 0.195 * 0.194 = 0.038 (not 0.12) is correct.
2. **"Max angle that clears the net with 10 rev/s spin: topspin 35 deg, backspin 33 deg."**
   - The text says exactly this, but it conflicts with Fig. 2. The non-K "top 10" and "back 10" net-clearing curves run all the way to 45 deg.
   - Only the K curves (landing on the kitchen line) end near 34 deg (top10K), 33 deg (zero K) and 32 deg (back10K).
   - The bullet most likely describes where the kitchen-line-landing solutions end, not net clearance. Quote it as stated, ambiguous and internally inconsistent.
3. **Fig. 2 at 45 deg.** The values check out against the figure: back10 about 8.65, zero about 8.85, top10 about 9.1 m/s. But these are the lower boundary curves, meaning the shot **just clears the net**. They are not "land at the net side of the kitchen".
4. **Spin vs speed equivalence.**
   - The source says the topspin-15 to backspin-10 variation produces a trajectory change "**less than** that produced by a speed variation of about 0.8 m/s" (down-the-line) and "roughly 1.0 m/s" (cross-court).
   - The extractor's "~ du 0.8" overstates the precision. It is an upper bound read off Fig. 3.

### Dropped (1)
- "Reviewer reproduction of Fig. 1 (10.30 / 9.19 / 8.31 m ...)". This is the extractor's own computation, not source data, so I removed it from data_points. I re-ran it, and the result is worth keeping as a caveat:
  - With the **printed (wrong-sign) Eq. 3** and Cl = +0.12 / 0 / -0.12:
    - Landing: 10.30 / 9.19 / 8.31 m.
    - Apex: 1.66 / 1.53 / 1.42 m.
  - With the **physically correct** Eq. 3:
    - Landing: 10.15 / 9.19 / 8.35 m.
  - The digitized Fig. 1 (about 10.37 / 9.25 / 8.4) is closer to the printed-equation run. Weak evidence suggests the authors **coded the wrong-sign x-equation**, which adds about 0.15 m of carry to backspin shots at Cl = 0.12.
  - With the self-consistent Cl = +/-0.038 and the correct equation, landing is 9.47 / 9.19 / 8.92 m, about a third of the plotted spin effect.

### Added (6)
1. The official ball limits used for the model ball: diameter 0.0730-0.0755 m, mass 0.0221-0.0265 kg. The model uses the averages, 0.07425 m and 0.0243 kg. Those averages are computed, not printed. (App. A, para. 1.)
2. Court geometry used in the model:
   - Baseline to net 6.71 m.
   - Net 0.86 m at the sidelines, 0.81 m at mid-court.
   - Kitchen 2.13 m.
   - Measured shots flew over a sideline, so the 0.86 m net applies.
   (Sec. 1.)
3. The authors assert "we will show that Re will be in the range 5x10^4 to 5x10^5, and will therefore treat a pickleball as if it were a solid, rough ball" (App. A, para. 3).
   - Their own data cover only 4.7-6.1e4.
   - They also concede that internal secondary flows through the holes are possible at low Re.
   - The solid-ball assumption is therefore unverified exactly in POLLEN's 1-5e4 range.
4. Spin was estimated by counting revolutions over roughly 5-10 frames, i.e. 0.04-0.08 s.
   - At 5.9 rev/s that is only 0.24-0.47 rev per window.
   - The authors attribute the large Cl scatter to spin-rate uncertainty.
   - They say Cl has "roughly the same linear dependence on S" as Fig. 3 of Cross & Lindsey (2017).
5. The Fig. 3 plotted extents are slightly wider than the stated ranges:
   - Down-the-line polygon about 15.4-23.2 deg, 10.8-12.8 m/s, with the topspin-15 line up to about 12.95 m/s.
   - Cross-court polygon about 12.4-18 deg, 13.4-16.05 m/s, with topspin-15 up to about 16.25 m/s.
   - The text ranges are rounded summaries.
6. Serve speed of 18-24 m/s to land near the back of the court. This cites Anon (2022), pickleballscience.org, an unreviewed web page. It is context only.

### Fig. 4 consistency check (re-run, confirms extractor's flag)
- My re-run starts from (1.0, 1.2) m at 10.0 m/s, 31 deg, Cd 0.30, Cl 0.027. It gives:
  - Apex 2.44 m at x about 4.9 m.
  - Landing x about 9.9 m.
  - Flight time 1.23 s from the first point.
- The plot shows apex about 2.33 m at x about 4.5 m and landing about 9.25 m.
- To match the plot you need u of about 9.4 m/s (apex 2.31 m at x 4.53 m, landing 9.15 m) or Cd of about 0.5-0.6 at 10 m/s.
- The 14 points at 0.08 s spacing span about 1.04 s. Even counting from a strike near x = 0, the time is about 1.2-1.35 s, not 1.42 s.
- The caption and the figure are not mutually consistent at the stated Cd. This weakens confidence in the +/-0.02 on Cd.

## Verdict on the extraction
- The extraction is accurate overall. No invented numbers were found.
- The physics flags all hold up: the x-equation sign, the Fig. 1 sign labels, the Fig. 1 Cl not matching the paper's own fit, the Re/viscosity misprint, and the Emond 0.0/0.6 inconsistency.
- Main fixes:
  - Label the 35/33 deg bullet as inconsistent with Fig. 2.
  - Reword the Fig. 2 45-deg values as net-clearing limits.
  - Restate the spin equivalence as an upper bound ("less than 0.8 / 1.0 m/s").
  - Remove the checker computation from the source data points.
- The review status is right: the journal VoR is peer-reviewed but unread. The two preprints read (arXiv v1 and SportRxiv) are identical. The VoR abstract matches the preprint's headline numbers, but changes to the body (equations, Cd/Cl) are unknown.

## PM-001 implications (unchanged from the extraction, with additions)
- Cd 0.30 is a pickleball prior valid only for Re 4.7-6.1e4.
- Cl = 0.195 S is valid only for S <= 0.3. Do not extrapolate it to S of about 1-2.
- Implement lift as perpendicular to v (omega x v). Do not copy Eq. 3.
- Do not use Fig. 1 as a validation target for spin effect size. Its Cl of +/-0.12 is about 3x the paper's own fit, and it may also include the wrong-sign x-term.
- The "spin is secondary" conclusion is specific to fast, flat drop shots (S <= 0.2). It is neither evidence for nor against high-S POLLEN lobs.
- Prototype calibration should improve on their weakest link, spin measurement: use a higher frame rate, count spin over at least 1 full revolution, and add a second camera view.
