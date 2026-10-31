# Cross (2005): Bounce of a spinning ball near normal incidence

source_id: `cross2005`

## Citation
R. Cross, "Bounce of a spinning ball near normal incidence," *American Journal of Physics* **73**(10), 914–920 (October 2005). DOI: 10.1119/1.2008299. Received 23 Feb 2005; accepted 4 Jul 2005. Author: Physics Department, University of Sydney.

## Access level
**Full text.** The publisher page (https://pubs.aip.org/ajp/article/73/10/914/1042412/) is paywalled and shows only the abstract. The full 7-page article (pp. 914–920) is on the author's university directory: https://www.physics.usyd.edu.au/~cross/PUBLICATIONS/31.%20Spin.pdf. I read it in full with pdftotext. Some Greek letters (alpha, omega, theta) and some ± and ≈/</> glyphs were lost in extraction. I rebuilt equations 3, 4, 8 and 9 and checked them numerically against the coefficients printed in the paper (see "Equations"). A few table cells could not be recovered and are marked.

## Review status
Peer-reviewed journal (American Journal of Physics, AAPT). It is a teaching-physics journal, but the paper presents original experimental measurements.

## Method
- **Ball:** new tennis ball, outer radius R = 33 mm, wall about 6 mm, alpha = I/(mR²) = 0.55 (the paper's value).
- **Experiment A (floor, no spin):** hand-thrown without spin at 3–15° from the normal and 5.60–6.03 m/s, onto a smooth wood floor or P800 emery paper taped to the floor. 9 bounces per surface.
- **Experiment B (floor, with spin):** spin imparted by brushing the ball upward with a racquet. The ball then fell within 2° of vertical, with ω1 = 61–116 rad/s backspin and v1 = 5.13–6.78 m/s. 9 bounces per surface.
- **Experiment C (racquet):** the spinning ball fell back onto the strings of a hand-held 334 g racquet (string tension about 250 N, estimated). About 80 impacts filmed; the 39 "best" analysed (incidence within 10° of normal, near string centre). The racquet was tilted ±10° to give effective backspin or topspin incidence. Data were transformed to the frame of the racquet at rest and horizontal.
- **Measurement:** JVC DVL9600 video at 100 frames/s with 2 ms exposure. A pen line and dot on the ball gave its orientation. 3–5 frames before and after the bounce; linear fit for horizontal position, quadratic fit (g = 9.8 m/s²) for vertical. Velocities and spin each within 2%. Main error: the seam makes the ball non-spherical, so it can bounce up to 1° off vertical even with no spin. For this reason the no-spin e_x within 3° of normal could not be measured reliably.
- **Model:** a rigid-body impulse model with two restitution coefficients (normal e_y and tangential e_x, both defined at the contact point), plus conservation of angular momentum about the contact point. The paper gives a qualitative grip–slip description but does not include a time-resolved contact model.

## Equations
Sign conventions follow Fig. 1 of the paper. The x axis is tangent to the surface, in the direction of incident horizontal motion. y is the surface normal. ω > 0 is **topspin**, meaning the bottom of the ball moves backward relative to the centre, so the contact-point tangential velocity is v_x − Rω. Subscripts 1 and 2 mean immediately before and immediately after impact. Units are SI: v in m/s, ω in rad/s, R in m, m in kg, I in kg·m².

| # | Equation | Meaning |
|---|---|---|
| (1a) | e_y = v_y2 / v_y1 (magnitudes) | Normal COR (centre-of-mass velocity; the surface is assumed not to recoil) |
| (1b) | e_x = −(v_x2 − Rω2)/(v_x1 − Rω1) | **Tangential COR** of the contact point. e_x > 0: contact-point slip reverses (elastic tangential recoil). e_x = 0: the ball exits rolling (Brody model). e_x = 1: Garwin superball. e_x < 0: the ball exits still slipping in the original direction. Physically −1 < e_x ≤ 1. |
| (2) | I ω1 + m R v_x1 = I ω2 + m R v_x2, with I = α m R² | Angular momentum about the contact point is conserved, assuming the normal force acts through the CM (the paper tests this; see below) |
| — | F = −m dv_x/dt, F R = I dω/dt ⇒ ∫F dt = m(v_x1 − v_x2) = (I/R)(ω2 − ω1) | Friction impulse F on the ball (positive = backward). The same relation holds if the surface recoils, but e_x then becomes an "apparent" e_x. |
| (3) | v_x2/v_x1 = (1 − α e_x)/(1 + α) + [α(1 + e_x)/(1 + α)] · (Rω1/v_x1) | Rebound tangential velocity |
| (4) | ω2/ω1 = (α − e_x)/(1 + α) + [(1 + e_x)/(1 + α)] · (v_x1/(Rω1)) | Rebound spin |
| (5) | v_y2 = (1 + e_A) v_R + e_A v_y1 | Ball dropped at speed v_y1 onto a racquet moving up at v_R. e_A = apparent COR = v_y2/v_y1 with v_R = 0 (ignores racquet recoil). |
| (6) | v_x2/v_x1 = 0.648 + 0.300 Rω1/v_x1 | **Empirical** linear fit to 39 racquet bounces (Fig. 5) |
| (7) | ω2/ω1 = 0.400 + 0.583 v_x1/(Rω1) | **Empirical** fit to the same 39 bounces (Fig. 6) |
| (8),(9) | Eqs. 3–4 with α = 0.55, e_x = −0.11 give 0.684 + 0.316 Rω1/v_x1 and 0.426 + 0.574 v_x1/(Rω1) | Close match to (6)–(7), which supports the model in Eqs. 1–2 at these low speeds |

Moment-of-inertia factors given in the paper: solid sphere α = 2/5, thin shell α = 2/3, tennis ball (6 mm wall, R = 33 mm) α = 0.55.

**Limiting cases** stated in the paper (solid ball, normal incidence, v_x1 = 0):
- e_x = 1: v_x2 = 4Rω1/7 and ω2 = −3ω1/7 (spin reverses). The ball exits with v_x2 = −4Rω2/3, sliding.
- e_x = 0: v_x2 = 2Rω1/7 and ω2 = 2ω1/7. The ball exits rolling, v_x2 = Rω2.
- A real solid ball should give v_x2 ≈ 3Rω1/7.

From Eq. 4 at v_x1 = 0, spin reverses when e_x > α. The paper says "about 0.4, as for a superball", which is the solid-ball value of α. *Lead's note: for POLLEN, α ≈ 0.63, so reversal needs e_x > ~0.63.*

**Numerical checks I ran:**
- Eqs. 3–4 as rebuilt reproduce the paper's coefficients: 0.684, 0.316, 0.426 and 0.574.
- They reproduce all four limiting cases above.
- They reproduce Fig. 3: v_x2/v_x1 = 0.574 and Rω2 = 1.348 v_x2 for α = 0.55, e_x = 0.2, no incident spin.

**Qualitative grip–slip mechanism (Sec. III, Figs. 2–3):**
1. The ball slides first, and friction acts against the slip.
2. When v_x = Rω the contact point stops and the ball grips, held by static friction under the large normal force.
3. Elastic tangential strain builds up, with Rω > v_x during the grip.
4. When the normal force falls, grip releases. The contact point slides backward and friction reverses, so the ball exits with e_x > 0 or, if a second grip and reversal occurs, with e_x < 0.
5. The contact patch is in reality partly slipping and partly gripping (Maw et al. 1976; Stronge 2000).

Grip occurs for incidence within about 45° of the normal. Above roughly 50–75° the ball slides throughout, e_x ≈ 0 or less, and the sliding friction coefficient μ sets the result instead (cited to Cross 2003, Sports Eng.). Within the grip regime, μ "does not enter directly" into Eqs. 3–4.

**Qualitative rules (Sec. II):**
- Backspin (ω1 < 0) reduces both the forward rebound velocity and the forward spin.
- Topspin increases both.
- With no spin at oblique incidence, a higher e_x gives more forward spin.
- With spin at normal incidence, a higher e_x gives less forward spin.

## Numeric data points
| Quantity | Value | Conditions | Where |
|---|---|---|---|
| α (tennis ball) | 0.55 | R = 33 mm, wall 6 mm | Sec. II, p. 915 |
| α solid / thin shell | 0.4 / 0.667 | theory | Sec. II |
| Impact duration | ~5 ms | tennis ball, oblique, floor | Fig. 3 caption |
| Fig. 3 illustrative | v_x2/v_x1 = 0.574; Rω2 = 1.348 v_x2 | e_x = 0.2, no spin, model | Fig. 3 caption |
| μ_sliding wood | 0.4 ± 0.1 | tennis ball, smooth wood floor, previous experiments | Sec. IV.A |
| μ_sliding P800 | 0.85 ± 0.05 | tennis ball on P800 emery paper | Sec. IV.A |
| No-spin throws | 3–15° from normal, 5.60–6.03 m/s | 9 bounces per surface | Sec. IV.A |
| Spin throws (floor) | ω1 = 61–116 rad/s, v1 = 5.13–6.78 m/s, ≤2° from vertical | 9 per surface | Sec. IV.A |
| Measurement accuracy | v and ω within 2%; seam gives up to 1° random bounce angle | 100 fps, 2 ms exposure | Sec. IV.A |
| Spin-case bounce angle | ~10° from vertical | spinning ball, near-normal | Sec. IV.A |
| v_x2/v_x1 (no spin) | wood 0.35 ± 0.05; P800 0.51 ± 0.02 | 10–13° incidence, ~5.7 m/s | Sec. V |
| Rω2/v_x1 (no spin) | wood 0.66 ± 0.05; P800 0.65 ± 0.04 | same | Sec. V |
| S2 = Rω2/v_x2 (no spin) | wood 1.91 ± 0.28; P800 1.27 ± 0.09 ("overspinning") | same | Sec. V, Table I |
| ω2/ω1 (spin, near-normal) | wood 0.29 ± 0.03; P800 0.30 ± 0.04 | within 3° of normal, backspin | Sec. V |
| Near-normal spin case | v_y1 ≈ 6.0 m/s, v_x1 ≈ 0.15 m/s, ω1 ≈ −80 rad/s (backspin) | floor | Sec. V |
| Backward rebound | v_x2 ≈ −1.1 m/s (wood), ≈ −0.95 m/s (P800) | same | Sec. V |
| Table I, P800 no spin | v1 5.70 ± 0.12; θ1 13 ± 3°; e_y 0.79 ± 0.007; e_x 0.13 ± 0.05; S2 1.27 ± 0.09 | 9 bounces; ω1 cell reads "1" (glyph lost; text says thrown "without spin", so ≈0) | Table I |
| Table I, wood no spin | v1 5.76 ± 0.14; θ1 10 ± 4°; e_y 0.79 ± 0.009; e_x 0.32 ± 0.07; S2 1.91 ± 0.28 | 9 bounces | Table I |
| Table I, wood spin | v1 6.09 ± 0.44; θ1 2 ± 0.5°; ω1 −61 to −116; e_y 0.77 ± 0.008; e_x 0.08 ± 0.04; S2 0.79 ± 0.08 | 9 bounces | Table I |
| Table I, P800 spin | v1 5.93 ± 0.46; θ1 1 ± 0.5°; ω1 −65 to −90; e_y 0.78 ± 0.011; e_x 0.055 ± 0.04; S2 0.84 ± 0.11 | 9 bounces | Table I |
| Summary e_x floor | spinning ≈ 0.07 vs non-spinning ≈ 0.2 | Conclusion | Sec. IX |
| Racquet | 334 g hand-held; string tension ~250 N (estimated); racquet moving up ~0.8 m/s | 39 of ~80 impacts | Sec. IV.B |
| Racquet tilt | up to 10°; topspin-equivalent case bounced up to ~40° from vertical | | Sec. IV.B |
| Table II racquet | v1 4.14–6.98 m/s; θ1 −6 to 12°; ω1 −44 to −131 rad/s; e_A 0.42 ± 0.04; e_x −0.11 ± 0.06 | 39 bounces, racquet frame | Table II, Sec. VI |
| e_A range | 0.35 (6 cm toward tip) to 0.52 (6 cm toward handle) | | Sec. VI |
| Backward bounce | v_x2 < 0 for θ1 = 0–7° with backspin; sometimes at larger θ1 if spin high | racquet | Sec. VI |
| Fit Eq. 6 | slope 0.300, intercept 0.648 | 39 bounces | Fig. 5 |
| Fit Eq. 7 | slope 0.583, intercept 0.400 | 39 bounces | Fig. 6 |
| e_x corrected for racquet recoil | ≈ −0.02 (vs apparent −0.11) | momentum estimate | Sec. VII |
| Goodwill & Haake data (cited) | e_x ≈ +0.05 (0–0.1) | 40° incidence, 20–30 m/s, spin +50 to −500 rad/s, head-clamped | Sec. VII |
| Prior e_x trend (cited) | max ~0.2 at 50° incidence; ≈0 at ~75° (slides throughout) | tennis and golf balls | Sec. VII |
| Grip threshold | grip if incidence within ~45° of normal | tennis ball | Sec. II, VI |
| Fig. 7 example | ball 15 m/s, 400 rad/s; racquet 20 m/s, rising 30°, tilt 5°; e_y = 0.42 | model illustration | Fig. 7 |

**Consistency flag (my check, not stated in the paper):**
- For the no-spin floor rows, Eq. 2 with α = 0.55 predicts α Rω2/v_x1 + v_x2/v_x1 = 1. The measured values give 0.71 (wood) and 0.87 (P800). So at 10–13° incidence, angular momentum about the contact point was **not** conserved under the "normal force through CM" assumption, or the incident spin was not truly zero.
- The near-normal spinning rows are roughly consistent with the model. Predicted v_x2 is about −0.92 m/s versus −1.1 measured on wood, and predicted ω2/ω1 is 0.26 versus 0.29.
- The racquet data (Eqs. 6–9) fit well.
- Cross himself says the floor results need "further theoretical work."

## Applicability to POLLEN
Classification of what transfers:
- **Transfers (peer-reviewed theory and method):** the two-coefficient (e_y, e_x) impulse model, Eqs. 1–4. It is ball-agnostic once α, e_y and e_x are known. So is the measurement method: video at ≥100 fps, a marked ball, and fits for v and ω before and after impact.
- **Does NOT transfer (tennis-specific data):** every e_y, e_x and μ value above. A tennis ball is a pressurised rubber core with a felt cover and a 6 mm wall. POLLEN is a ~1.7–1.8 mm hollow, perforated, rigid-ish polyethylene shell with holes and a non-spherical shape. Its e_y, e_x, μ, contact time and grip threshold are **unknown** and must be measured. No POLLEN values are given here, and I have filled none from memory.
- **POLLEN α (theoretical estimate):** for m = 25 g, R = 35.5 mm and a polyethylene shell (ρ ≈ 920–960 kg/m³) with holes ignored, the equivalent uniform-shell thickness is about 1.75 mm and α ≈ 0.635, close to the thin-shell 2/3. Uniform perforation barely changes α. *Assumption: verify with a mass or bifilar-pendulum test.*
- **Shape:** perforations and lack of sphericity act like Cross's seam problem (up to 1° random bounce error for a nearly spherical tennis ball), but are probably larger for POLLEN. Expect a scatter term in rebound direction that depends on hole and contact location.
- **Spin case is relevant:** the strong-spin, near-normal case is the most relevant to a backspinning POLLEN hitting the HIVE rim or interior. Cross shows that a spinning ball hit at normal incidence rebounds at a substantial angle (~10° for a tennis ball with S1 ≈ 0.44, i.e. Rω1 ≈ 2.6 m/s at v ≈ 6 m/s). It also keeps 29–30% of its spin, in the same direction.
- **Illustrative POLLEN numbers (Eq. 3 at v_x1 = 0; α = 0.62–0.66; e_x ∈ [−0.1, 0.3] as a sensitivity bracket, not measured):**
  - Rω1 = 2 m/s gives a tangential rebound kick of 0.69–1.03 m/s.
  - Rω1 = 5 m/s gives a kick of 1.7–2.6 m/s.
  - ω2/ω1 ranges from 0.20 to 0.46.
  - If POLLEN keeps S ≈ 0.5–1 up to impact, the spin-induced tangential kick is comparable to e_y·v_n for any plausible e_y. So **spin-dependent rim/interior redirection (Hypothesis B) is a first-order effect, not a small correction**, provided the ball grips.
  - This depends on the unmeasured e_x, on the grip-regime validity of the model, and on how much spin survives flight.
- **Direction of the spin kick (theory, derived from Eq. 2/3, not stated by Cross for HIVE geometry):** the tangential impulse on the ball opposes the contact-point velocity from spin, ω × r_c. For a backspinning ball moving toward +x (bottom surface moving forward, front moving up, top moving back, rear moving down):
  - Floor or bottom contact: kicked backward, toward the shooter. This is Cross's "bounced backward" result.
  - Far wall or far lip, facing the shooter (front-lower contact): kicked downward and back, i.e. **into** the CELL. Favourable.
  - Near lip, hit with the lower-rear of the ball: kicked back and up, i.e. **away from** the CELL. Unfavourable, a bounce-out risk.
  - Conclusion: backspin is not monotonically helpful. It helps far-side contacts and hurts near-lip contacts. This matches HANDOFF §5, "Do not claim more backspin always improves entry."
- **Moving or compliant HIVE:** the HIVE pivots and may have compliant panels. Cross's racquet case shows that a recoiling or compliant target lowers the apparent e_y (0.42 vs 0.79 on the floor) and can make the apparent e_x negative (−0.11). Panel compliance should be measured, not assumed rigid. The HIVE is much heavier than 25 g, so whole-body recoil is probably negligible, but local panel flex may not be.

## Implications for the PM-001 models
1. **Contact model (src collision module; lead to implement):**
   - Resolve each rim, wall or floor contact in the local frame: n = unit vector from the contact point to the ball centre (for an edge, the closest point on the edge); t = tangential slip direction.
   - Use the e_n, e_t (= Cross e_y, e_x) impulse model:
     - J_n = m(1 + e_n) v_n1
     - u1 = v_t1 − (ω × R n_c)·t, the contact-point slip, with n_c = −n
     - Grip-regime tangential impulse: J_t,grip = m α(1 + e_t)/(1 + α) · u1
     - Then v_t2 = v_t1 − J_t/m and ω2 = ω1 + (R n_c × (−J_t t))/(α m R²) in vector form. This reproduces Cross Eqs. 3–4 exactly in 2D.
   - **Add a Coulomb cap** (standard Brody/Cross-2002/Stronge extension, *not* in this paper): if |J_t,grip| > μ J_n, use J_t = μ J_n · sign(u1). This represents sliding throughout, which Cross says governs incidence beyond about 45–75°. It makes rim grazes μ-limited and near-normal hits e_t-limited.
   - Unit-test it against Cross's limits: solid ball, e_t = 1 gives v_x2 = 4Rω1/7; e_t = 0 gives 2Rω1/7. Also check Eqs. 8–9 at α = 0.55, e_t = −0.11.
2. **Parameters and uncertainty:**
   - α_POLLEN ≈ 0.635 (assumption).
   - e_n, e_t and μ are unknown, so sweep them. Suggested bracket: e_t ∈ [−0.15, 0.4]; e_n and μ to come from the POLLEN-specific sources or tests, not from tennis.
   - Report scoring probability as a function of (e_n, e_t, μ). Tennis numbers are labelled "tennis, Cross 2005" only as a sanity anchor.
3. **Spin at impact matters:** the redirection scales with Rω at contact. The free-flight model must carry spin to the HIVE (spin decay k_spin), and the collision outcome should be plotted against S_impact. Cross's backspin data also show spin falls to about 30% per near-normal bounce. Repeated interior contacts therefore lose spin quickly, so the "spin assist" mostly acts at the **first** contact.
4. **Scatter term:** add a random rebound-direction perturbation of order 1–3° or more (POLLEN holes and asphericity; Cross had up to 1° from a tennis seam). Calibrate it from drop tests.
5. **Launcher analogy (weak, labelled as analogy):** Cross's grip-then-release "overspinning" exit (S2 = 1.3–1.9 > 1) shows that tangential elasticity can make exit spin differ from rolling (S = 1). In the hood or flywheel contact, S_exit ≈ 1 should be treated as a nominal value with ± uncertainty, not a constraint. The hood contact is a long rolling and sliding contact, not a single impact, so do not reuse e_x values there.
6. **Prototype tests suggested by this paper's method:**
   - (a) Drop POLLEN at 4–7 m/s with no spin onto HIVE panel material to get e_n.
   - (b) Oblique no-spin throws at 10–60° to get e_t(θ) and the grip-to-slide transition, and hence μ.
   - (c) Spinning, near-normal drops, with spin from the actual flywheel and hood, to get ω2/ω1 and the rebound angle. Fit Eqs. 3–4 to get α_eff and e_t, as Cross did in Figs. 5–6.
   - (d) Repeat on a rim or edge sample and on the actual pivoting HIVE to capture compliance and apparent COR.
   - Use ≥240 fps if possible: POLLEN spin rates (~100–300 rad/s) exceed Cross's 61–131 rad/s, so 100 fps risks 180° orientation ambiguity. Mark the ball with a line and a dot, and fit 3–5 frames each side.
