# Fact-check: cross2017 extraction (Cross & Lindsey 2017, EJP 38 044002)

Checker: independent fact-check agent, PM-001, 2026-10-30.
Extraction checked: research/papers/cross2017.md and its JSON (21 data points, 9 equations).

**CHECK: 17 confirmed / 3 corrected / 1 dropped / 11 added**

## 1. What I opened

| Source | Result |
|---|---|
| https://iopscience.iop.org/article/10.1088/1361-6404/aa6e44 (landing page) | Abstract and metadata reached. EJP 38(4) 044002; received 1 Mar 2017, revised 28 Mar, accepted 20 Apr, published 12 May 2017; Cross (Sydney), Lindsey (Tennis Warehouse). All match the extraction. |
| .../aa6e44/pdf | Login/purchase wall, as the extractor reported. The full text was **not** reached. |
| api.semanticscholar.org (DOI record) | openAccessPdf = the IOP PDF URL, status "BRONZE". Abstract and references are elided in the record. |
| fyysika.ee/?p=407361 (abstract repost, 12 May 2017) | Same abstract content. |
| ui.adsabs.harvard.edu | HTTP 405. |
| Cross 2012 AJP author PDF (physics.usyd.edu.au/~cross/PUBLICATIONS/58. Aerodynamics AJP.pdf) | **Full text read.** Text extracted with pdftotext. Pages 291, 293 and 294 were rendered to PNG, and Figs. 3, 6, 7, 8 and 9 were read directly. |
| twu.tennis-warehouse.com/learning_center/aerodynamics2.php | Read. Cross & Lindsey, 22 Dec 2013, unreviewed web article. |

Review status is correct. EJP (IOP) and Am. J. Phys. (AAPT) are both peer-reviewed. The TWU page is an unreviewed web article.

## 2. Row-by-row verdicts on the JSON data points

| # | Extracted row | Verdict | Notes |
|---|---|---|---|
| 1 | 6.4 m camera separation (2017 abstract) | CONFIRMED | |
| 2 | Magnus increases with spin, "ball A" | CONFIRMED (relabel) | The abstract does not name the balls. "A/B/C" are the extractor's labels, and they clash with Cross 2012 Table I, where Type A/B/C means smooth/loop seam/baseball seam. Use "ball (i)/(ii)/(iii)". |
| 3 | Rises to max then falls almost to zero, "ball B" | CONFIRMED (relabel) | |
| 4 | Negative at low spin, positive at high spin, "ball C" | CONFIRMED (relabel) | |
| 5 | Spin increased in flight for one ball | CONFIRMED | |
| 6 | "Cd, Cl numeric values: TBD" | DROPPED | This is a status note, not a data point. It is kept in the caveats. |
| 7 | Cd = 0.55 ± 0.05, 2.8–4.2 m/s, pendulum | CONFIRMED | Sec. V, text. Ball 1 is implied by context (the paragraph is about ball 1), not stated in the sentence. "Non-spinning" is implied by the pendulum set-up. The Re 1.9–2.8e4 range is computed and correct. |
| 8 | Cd ≈ 0.24 at 28 m/s → ≈ 0.40 at ≈ 7 m/s | CONFIRMED | Fig. 7a. The lowest-speed point is about 7.5 m/s. The text gives "7–28 m/s, Re 47 000 to 190 000" (Sec. VIII). |
| 9 | Cl vs S: 0.15 @0.37, 0.25 @0.5, 0.32 @0.8, plateau 0.33 @0.9–1.1, 0.30 @1.45 | CORRECTED (minor) | Re-read from Fig. 7b at 400 dpi: about 0.15 @ S 0.37; **about 0.23–0.24 @ S 0.5** (0.25 is reached at about S 0.53); **about 0.31 @ S 0.8**; peak about 0.33 @ S 0.95–1.1; about 0.30 @ S 1.42–1.45. The original values sit inside the extractor's stated ±0.02 read error, but they were biased high on the rising branch. |
| 10 | Generic Cl(S): 0 → 0.3 for S 0–0.4, then about 0.3 | CONFIRMED | Sec. V, citing refs 13 (Nathan 2008) and 14 (Goff & Carré 2009). Also confirmed: "For the polystyrene ball, CL continues to increase up to about S = 1." |
| 11 | n = 1.73, mg = 0.088 N, 5–28 m/s | CONFIRMED | Fig. 6b label and caption. |
| 12 | Fit unreliable below about 5 m/s | CONFIRMED | Sec. V. |
| 13 | Ball 4 Cl < 0 for 9 < v < 14; fit min ≈ −0.1 near 10.5–11; zero ≈ 14.5; +0.2 @7; +0.1 @17 | CORRECTED | The "9 < v < 14 m/s" statement is confirmed (text). Read from the Fig. 9 dashed fit: about +0.25 at 6.5 m/s; **about +0.15–0.2 at 7 m/s**; **first zero crossing about 8.2 m/s** (missing from the extraction); minimum about −0.11 at about 10.5–11 m/s; **second zero crossing about 14.2 m/s** (not 14.5); about +0.12 at 17 m/s. The Re 1.4–2.1e5 range is computed and correct. Path averages over the first 2 m are confirmed. |
| 14 | Ball 4 Cd ≈ 0.55 @6.5 → 0.3 @10 → 0.16 @16–17 | CONFIRMED | Fig. 9 solid fit: about 0.2 at 13 m/s, flattening at about 0.16. The paper does not use the words "drag crisis" for Fig. 9. It discusses BL transition in Sec. VIII. The extractor's label is a reasonable interpretation. |
| 15 | Fig. 8 throw: 10.8 m/s, 367 rpm, Rω = 4.4 m/s; Cl −0.08 → −0.21, Cd 0.40 → 0.31 over 8.8–11 m/s; a_z ≈ 12.5 m/s² down | CONFIRMED | Fig. 8 caption, Fig. 8b and Sec. V/VIII. Fig. 8b reads Cd 0.41 → 0.31 and Cl −0.07 → −0.22, within read error. Check: 2(1.88 − 1.59)/(0.215)² = 12.5 m/s². S ≈ 0.44 uses the Sec. VIII v = 10 m/s. Fit orders confirmed from the Fig. 8a labels: n = 2 for x(t), n = 3 for z(t). |
| 16 | Local Re 2.2e5 (14.4 m/s) and 8.5e4 (5.6 m/s) | CONFIRMED | Sec. VIII and Fig. 12. Laminar on the upper side (A), turbulent on the lower side (B). |
| 17 | C_S ≈ 0.22 at mean 6 m/s, ≈ 0 at mean 12 m/s, reverses above | CONFIRMED | Sec. VI. Recomputed from a = 3 m/s², m = 12.15 g, d = 98 mm: C_S = 0.22. Reversal: Sec. VI, plus Sec. VIII "wrong" direction at about 15 m/s, Re about 1e5. |
| 18 | Break 100 cm / 5 m (9 m/s, 475 rpm, 0.8 s, 3 m/s²); 90 cm for baseball seam (11.8 m/s, 474 rpm, 0.70 s) | CONFIRMED | Secs. VI–VII and the Fig. 11 caption (126 ms per rev = 474 rpm). |
| 19 | Spin constant over about 0.7 s (ball 3) | CONFIRMED | Sec. VII: "The spin remained constant during the transit to the target." Qualitative; spin resolution ±2%. |
| 20 | 300/120 fps, spin ±2%, impact ±1 cm, 1° = 9 cm at 5 m | CONFIRMED | Sec. III. |
| 21 | a_z ≈ +65, a_x ≈ −90 m/s² at launch; "ball climbed to ~4.2 m" | CORRECTED (wording) | The accelerations are confirmed (Sec. III). The text says "climb vertically to a height of about 4 m". Fig. 6a shows the apex at z ≈ 4.25 m above ground at x ≈ 9.5 m, t = 1.0 s, v = 3.5 m/s, from a launch height of about 2.05 m (dip to about 1.85 m at x ≈ 2 m). The net climb above launch is therefore about 2.2 m, not 4.2 m. |

### Equations
- Eqs. 1–4 are CONFIRMED. I re-derived Eqs. 3–4 from Eqs. 1–2, and the signs are correct.
- Eq. 5 is CONFIRMED for F_D and F_L only. F_S = ½ C_S ρ A v² is defined in the text after Eq. 5 ("analogously") and is not part of numbered Eq. 5. This is a minor citation fix.
- Re = ρvd/η = (6.7e4 s/m²) v d is CONFIRMED. The paper prints η = 1.81 × 10⁻⁵ "P". The extractor is right that this is a unit typo for Pa·s.
- S = Rω/v (Fig. 7 caption), F_D = k vⁿ (Fig. 6) and Δz = a_z(Δt)²/2 (Sec. V) are CONFIRMED.

### Method and other text claims in the md file
- The Fig. 3 launcher dimensions (1.5 m of 5 mm Al rod, 70 cm arm) are CONFIRMED. The 70 cm is from the Fig. 3 drawing.
- Wind tunnel: 45 cm long conical tube, 18 cm exit, anemometer 10 cm beyond the exit, 1.1 m V-thread pendulum. CONFIRMED.
- The 20% speed-drop criterion for quadratic versus higher-order fits and the 6th-order fit for Fig. 6 are CONFIRMED.
- The md says "the paper's refs 13–14" for the trajectory-fitting alternative. The text says "many authors (including those in Refs. 12–14)", with ref 14 (Goff & Carré) singled out. This is a minor fix.
- The TWU rig claims are CONFIRMED on the TWU page: cam 1 about 0.5 m in front of the launcher, cam 2 at 6.4 m, both 300 fps / 150 mm zoom / 1/5000 s; cam 3 at 120 fps for out-of-plane motion; a 60 cm board at several depths with a 2nd-order fit; ball centre digitised by both authors and averaged; "CD and CL from the change in speed and ball height between the two positions".
- The 2017 ball_and_method sentence "Cd and Cl came from the changes in speed and height between the two stations" could **not** be confirmed from the 2017 abstract text I could reach. The landing-page summary and the repost mention only "two cameras separated horizontally by 6.4 m". It is true of the TWU rig. Mark it as inference, not abstract content.
- The md's search-snippet claims (that Fig. 2 is a Cl overview, and the Taneda/Aoki citations) could not be checked. They stay unverified, as the extractor said.

### POLLEN arithmetic (extractor's own calculations, re-checked)
- Re = 4.76e3·v for d = 71 mm: OK.
- Ballistic length 2m/(ρACd) ≈ 20.6 m (Cd 0.5): OK. Cross ball 1 gives 3.7 m at Cd 0.5 or 4.6 m at Cd 0.4. Ball 4 gives 7.4–9.3 m. OK.
- Drag 3.1 m/s² and Magnus 2.5 m/s² at 8 m/s: OK.
- Apex a_M = 0.26 m/s² at 3 m/s with C_L 0.3: OK.
- m_A = 0.23 g: OK.
- σ(a) ≈ 0.012 m/s²: OK.
- "1% scale error → ΔC_L about 0.01 at 8 m/s" is closer to 0.016. Minor.
- "S ≳ 1 at Re ≲ 6.7e4": with ω = 2000 rpm, S = 1 at v ≈ 10.6 m/s, so Re ≈ 7.2e4. Minor.

## 3. Missed data points (added)

| # | Quantity | Value | Conditions | Where | source_id |
|---|---|---|---|---|---|
| A1 | Cl vs v, ball 1 | about 0.30 at 7.5 m/s, peak about 0.33 at about 9.5–10 m/s, about 0.15 at 28 m/s | 101 mm, 9.0 g polystyrene, 2000 rpm, single throw | Fig. 7a | cross2012ajp |
| A2 | Author caveat on ball 1 Cl(S) | "Rapid deceleration of the ball may have affected the aerodynamics in a way that is not commonly observed with heavier balls" | ball 1, where Cl keeps rising to S ≈ 1 | Sec. V | cross2012ajp |
| A3 | Spin regime split in Fig. 9 | 100–200 rpm (hand) below about 9.6 m/s; 350–600 rpm (launcher) above. Computed S ≈ 0.12–0.37 below the split and ≈ 0.3–0.7 above (R = 0.114 m). Cl sign change at about 8.2 m/s therefore coincides with a spin step, so speed (Re) and S effects are confounded | ball 4 | Fig. 9 annotation, Sec. V | cross2012ajp (S computed by checker) |
| A4 | Fig. 9 scatter | individual Cl points from about −0.20 (boxed = Fig. 8 throw, about 10.3 m/s) to +0.13; about ±0.1 about the fit. Cd points about ±0.05 about the fit | ball 4, one throw per point | Fig. 9 | cross2012ajp |
| A5 | Author's BL interpretation, ball 4 | below about 9 m/s Re too low for turbulent BL; above about 14 m/s "presumably turbulent on both sides", giving conventional Magnus | ball 4 | Sec. VIII | cross2012ajp |
| A6 | Surface roughness effect on Cd | polystyrene surface varies by about 0.5 mm over about 10 mm, so Cd drops well below 0.5 even at Re ≈ 1e5 (a smooth sphere stays at about 0.5) | balls 1–3 | Sec. VIII | cross2012ajp |
| A7 | Critical Re | smooth sphere Cd drops sharply at Re ≈ 3e5; roughness or a seam lowers critical Re by a factor of about 2–3 | literature (refs 3, 7) | Sec. IV | cross2012ajp |
| A8 | Re reference points | Re = 1e5 at 15 m/s (100 mm balls) and 6.6 m/s (228 mm) | Re = 6.7e4·v·d | Sec. IV | cross2012ajp |
| A9 | Wrong-way side force, ball 2 | curved in the "wrong" direction at about 15 m/s (31 mph), Re ≈ 1e5 | 98 mm loop-seam ball, backspin | Sec. VIII, Fig. 10 | cross2012ajp |
| A10 | Ball 4 extreme vertical accel | a_z ≈ −17 m/s² under some conditions (negative Magnus) | 228 mm, 92 g | Sec. III | cross2012ajp |
| A11 | Spin–speed coupling of the launcher | spin approximately proportional to launch speed, both by hand and with the lacrosse launcher; speed and spin not controlled separately | all balls | Sec. III | cross2012ajp |

Also noted, not added as a row: the TWU 2013 article says "shaved tennis balls and smooth balls" were tested on the same 6.4 m rig but "not reported in this paper". This modestly strengthens the inference that the 2017 smooth-ball study used that rig. It is still not confirmed.

## 4. Implications for the lead

- No 2017 numbers exist in the extraction, and none were invented. Good.
- All quantitative content is cross2012ajp, and it checks out against the full text and figures, apart from small figure-read corrections.
- Before using ball 1's "Cl keeps rising to S ≈ 1, ceiling 0.33" as a POLLEN bound, note two things. The author himself flags possible unsteady/deceleration effects (A2). The S axis of Fig. 7b is consistent with constant ω = 2000 rpm (Rω ≈ 10.6 m/s gives S 0.38 → 1.41 for v 28 → 7.5 m/s), so in-flight spin was probably assumed constant rather than tracked along the path. This is the checker's inference.
- Ball 4's negative-Magnus region is confounded with a spin-regime step (A3), and it sits at Re 1.4–2.1e5, well above POLLEN's Re (≤ 5e4).
