# Fact-check: cross2005 (Cross, "Bounce of a spinning ball near normal incidence", Am. J. Phys. 73(10) 914-920, 2005)

Checker: independent re-read, 2026-10-30. Source re-opened: the author-hosted PDF of the published AJP version
(https://www.physics.usyd.edu.au/~cross/PUBLICATIONS/31.%20Spin.pdf, 7 pages, has the AJP page numbers and copyright line).
Text was extracted with pdftotext. Greek letters and the symbols < > ≈ ± were partly lost, so equations were rebuilt and
checked numerically against the printed coefficients (Eqs. 8-9 and Fig. 3).

**CHECK: 18 confirmed / 3 corrected / 0 dropped / 13 added**

- Citation, dates (received 23 Feb 2005, accepted 4 Jul 2005), DOI and review status (peer-reviewed journal, AJP) are confirmed.
- All key equations (1a, 1b, 2-9) and the limiting cases are confirmed. Recomputed with α = 0.55:
  - e_x = -0.11 gives 0.6842 / 0.3158 / 0.4258 / 0.5742, matching Eqs. 8-9.
  - Fig. 3 (e_x = 0.2): v_x2/v_x1 = 0.574 and Rω2/v_x2 = 1.349 (printed 1.348).
  - Solid-ball limits: 4/7, -3/7, 2/7 and 2/7.

## Corrections
1. **Impact duration, ~5 ms (Fig. 3 caption).** The caption describes the model illustration of a tennis ball hitting "a surface" obliquely. It does not say "floor", and the 5 ms is "typically about", not a measured value.
2. **Conditions for the no-spin floor ratios (Sec. V).**
   - "10-13 deg" are the Table I mean incidence angles (13±3° on P800, 10±4° on wood).
   - The actual throws spanned 3-15° at 5.60-6.03 m/s (Sec. IV.A).
3. **e_x versus incidence (Sec. II, Sec. VII).** At about 75° incidence the paper gives **e_x < 0**, not "~0". The inequality glyph is lost in the PDF text, but the meaning is clear from two passages:
   - Sec. VII: "as the angle decreases, e_x increases until the ball commences to grip, at which point e_x becomes positive".
   - Sec. II: "a ball can slide throughout the whole bounce period, in which case e_x [<] 0".
   - For a no-spin oblique ball that slides throughout, the contact point still slides forward at exit, so e_x is negative.
   - Max 0.2 at 50° and grip within about 45° of the normal are confirmed. Cross also notes that e_x had not been measured below 40° before this paper.

Minor wording clarifications (counted as confirmed):
- Eq. 1b: "e_x < 0 = still slipping forward" holds when the incident contact slip is forward. In general, e_x < 0 means the contact-point slip keeps its incident sign.
- Goodwill & Haake e_x ≈ +0.05 (range 0 to 0.1): Cross inferred this from their data. G&H did not evaluate e_x themselves.
- Racquet bounce angle (Sec. IV.B):
  - Racquet tilted so the ball arrived with backspin in the racquet frame: almost vertical bounce.
  - Tilted so it arrived with topspin: up to about 40° from vertical.
  - The spin direction itself was unchanged.

## Added (missed by extractor)
- A1 (Sec. IV.A): e_x could not be measured reliably for no-spin balls within 3° of the normal, because seam asphericity gives up to 1° random bounce angle. With spin, the about 10° rebound made that error minor.
- A2 (Sec. VI):
  - On the racquet, at 0-7° incidence with backspin, the ball bounced backward (v_x2 < 0).
  - At larger angles it mostly bounced forward, but sometimes backward at high spin.
  - S2 = Rω2/v_x2 is "of no real value" with backspin, because v_x2 can approach 0. Use e_x instead.
- A3 (Sec. VI): The agreement of Eqs. 6-7 with Eqs. 8-9 is taken to justify the "normal force through the CM" assumption, "at least for the low speed bounces in the present experiment".
- A4 (Sec. VI): Eqs. 3-5 describe the bounce up to about 45° from the normal. At larger angles the ball may slide throughout, and sliding friction sets spin and angle (ref. 7).
- A5 (Sec. II and Sec. V):
  - μ does not enter Eqs. 3-4. At small incidence, bounce parameters should be insensitive to μ.
  - The experiments agree: there was no significant difference in spin between wood (μ ≈ 0.4) and P800 (μ ≈ 0.85), and only a minor difference in v_x2.
- A6 (Sec. IX): Surface friction affects tangential ball speed more strongly than rebound spin.
- A7 (Sec. II):
  - In the e_x = 1 limit, a solid ball exits with v_x2 = -4Rω2/3 (sliding).
  - A real solid ball at normal incidence should bounce forward at v_x2 ≈ 3Rω1/7 (≈ inferred, glyph lost) with reduced spin.
  - Rebound velocity and angle depend weakly on e_x but strongly on incident spin. Spin direction after the bounce cannot be predicted without e_x.
- A8 (Sec. VII): e_x falls to about 0.06 for near-normal impacts on a rigid, very heavy surface, and to about -0.1 on hand-held strings.
- A9 (Sec. IV.B, citing ref. 4): e_A is around 0.4 for most racquets near the string centre.
- A10 (Sec. VII): Proposed mechanism for negative e_x on a hand-held (lighter, compliant) surface.
  - The lower normal force means an earlier release of grip, and possibly a second grip after the friction force reverses.
  - This is directly relevant to a pivoting or compliant HIVE.
- A11 (Sec. V): Regimes on the floor.
  - No-spin: the ball slides forward, grips, then slides backward at the end ("overspinning", Rω2 > v_x2).
  - Spin case: "underspinning", with smaller e_x.
- A12 (Sec. II, qualitative):
  - Backspin reduces both v_x2 and ω2; topspin increases both.
  - With no spin and constant e_x, v_x2/v_x1 does not depend on incidence angle.
  - With no spin, spin after the bounce falls as incidence falls, reaching 0 at the normal.
- A13 (Sec. VIII, Fig. 7, model calculation, not data):
  - Inputs: ball at 15 m/s with 400 rad/s, racquet at 20 m/s, e_y = 0.42, Eqs. 6-7.
  - The racquet must rise about 30° to the horizontal to reverse the spin. A 5° forward tilt alone was not enough.

## Internal inconsistencies in the paper (checker notes)
- Spin-case incidence is "up to 2° from vertical" in Sec. IV.A but "within 3°" in Sec. V. Table I gives 2±0.5° and 1±0.5°.
- The racquet selection criterion is "within 10° of the normal" (Sec. IV.B), yet Table II lists θ1 from -6 to 12°, possibly after the coordinate rotation.
- The Table I ω1 cell for the no-spin rows is unreadable in the extraction. The text says "without spin".
- Racquet v1 (4.14-6.98 m/s) is in the racquet frame.

## Extractor's own checks, verified
- No-spin floor data against Eq. 2:
  - α·Rω2/v_x1 + v_x2/v_x1 = 0.713 (wood) and 0.8675 (P800), versus 1.
  - The table values are self-consistent: implied e_x = 0.31 / 0.14 and S2 = 1.89 / 1.27, matching Table I.
  - So the shortfall is a genuine feature of the data, not a misread.
- Spin case, Eq. 3 with v_x1 = 0.15 m/s and ω1 = -80 rad/s:
  - Wood: predicted v_x2 = -0.92 m/s (measured about -1.1), ω2/ω1 = 0.264 (measured 0.29).
  - P800: predicted -0.89 m/s (measured about -0.95), 0.281 (measured 0.30).
- POLLEN figures:
  - α = 0.635 checks out (R = 35.5 mm, t = 1.75 mm). The shell volume is 26.4 cm³, about 25 g at PE density 0.95.
  - Kick factor α(1+e_x)/(1+α) = 0.34-0.52.
  - Spin retained = 0.20-0.46 for α 0.62-0.66 and e_x -0.1 to 0.3.
  - These are the lead's own arithmetic, not from the paper.

Data points, equations and implications are in the structured return.
