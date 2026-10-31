# Rossmann & Rau (2007): An Experimental Study of Wiffle Ball Aerodynamics

source_id: `rossmann2007`. Task: PM-001 (POLLEN backspin/Magnus shooter). Literature agent note, 2026-10-30.

## 1. Citation

Jenn (Stroud) Rossmann and Andrew Rau, "An experimental study of Wiffle ball aerodynamics,"
*American Journal of Physics* 75(12), 1099–1105 (December 2007). DOI 10.1119/1.2787013.
Received 21 Dec 2006, accepted 28 Aug 2007. Both authors were in the Department of Mechanical Engineering, Lafayette College, Easton PA.
Repository record: Lafayette handle 10385/1741.

## 2. Access level: abstract only (full text NOT read)

What I tried, in order:

| Route | Result |
|---|---|
| doi.org → pubs.aip.org article page | Paywalled ($40 pay-per-view). Only the metadata, abstract and reference list are visible. No figures, no equations, no numbers. |
| Unpaywall / OpenAlex / Semantic Scholar | `is_oa: false`, `oa_status: closed`, no repository copy indexed |
| ldr.lafayette.edu (new Lafayette repository), handle 10385/1741 | An AWS-WAF human-verification CAPTCHA blocks it. I did not try to bypass it. |
| Wayback snapshot of old dspace.lafayette.edu/handle/10385/1741 (2018-04-28) | Reachable. It confirms a repository PDF existed (`Rossmann-AmericanJournalofPhysics-vol75-2007.pdf`), but the PDF itself was never archived (404). |
| ResearchGate (publication 228655071 and figure page "Orientation of Wiffle ball for wind tunnel experiments") | HTTP 403 |
| Claude-in-Chrome (real browser, to pass the CAPTCHA) | Extension not connected |

**Consequence: this file contains no numeric results from the paper itself.** Everything below is labelled by provenance:
- **[P-abs]** from the paper's own abstract or metadata (verified)
- **[S-x]** from a secondary source that cites or describes the work (verified that the secondary source says it, not that the paper says it)
- **[R]** a related but different work by the same group
- **[A]** my own analysis or assumption for PM-001
- **[M]** from memory, unverified

**Recommended follow-up:** a human opens https://ldr.lafayette.edu/handle/10385/1741 in a browser (one CAPTCHA) or uses a library AJP login, then re-extracts the figures (C_D vs Re, C_L vs orientation). The paper is short (7 pages), so this is cheap.

## 3. Review status

The paper is peer-reviewed (American Journal of Physics, AAPT). It is a pedagogical or undergraduate-research paper, not a high-precision aerodynamic data set. The abstract frames it as "an accessible way to introduce" boundary-layer topics [P-abs]. Expect a single university wind tunnel, a static sting-mounted ball, and modest accuracy.

The secondary sources used here have mixed status:
- Emond et al. (arXiv 2409.19000): a preprint. Its journal version is IJRSS 2024.
- Lindsey (TWU pickleball page): an unreviewed web article.
- Popular Science (2014), Deseret News (2010), Lafayette news (2008, 2010): press articles.
- SlideServe deck by Jemmott, Logan and Utvich (advisor Rossmann): an unreviewed student presentation, likely an earlier Harvey Mudd project.

## 4. Ball and method

- **Ball:** a standard Wiffle ball. It is a hollow plastic sphere. One hemisphere has eight oblong slots and the other hemisphere is solid [S-Deseret: "eight oblong holes"]. Diameter is about 73 mm (2.875 in) [M]. It is not given in any source I could read.
- **Method:** wind tunnel force measurement of lift and drag on a **non-spinning** ball. They varied (i) Reynolds number (air speed) and (ii) ball orientation relative to the flow [P-abs; S-Lafayette news 2008]. Press accounts say the balls were skewered (sting or rod mount) and held at different angles while airspeed was varied [S-web search summary of press]. The tunnel was in the basement of Lafayette's Acopian Engineering Center [S-Lafayette 2010].
- **Mechanisms the authors consider** [P-abs]: (1) asymmetric external flow, meaning boundary-layer separation and transition differ between the slotted and solid hemispheres; (2) flow inside the ball through the slots. The abstract associates both with curve **without pitcher-imparted spin**.
- **Spin:** none. All the evidence is for static, non-rotating orientations. The paper provides **no Magnus or spin data**.

## 5. Equations

The paper's own equations could not be read. The definitions below are the standard ones that this work and the related Rossmann-advised student deck [R] use. They are given so that the PM-001 model can use consistent symbols.

| # | Equation | Symbols (SI) | Provenance |
|---|---|---|---|
| E1 | Re = ρ U D / μ | ρ air density [kg/m³]; U free-stream speed relative to the ball [m/s]; D ball diameter [m]; μ dynamic viscosity [Pa·s] | [R] SlideServe deck; standard |
| E2 | C_D = 2 F_D / (ρ U² A) | F_D drag force along the flow [N]; A = πD²/4 frontal area [m²] | [R]; standard |
| E3 | C_L = 2 F_L / (ρ U² A) | F_L force normal to the flow [N]. For a Wiffle ball this is an orientation-induced side or lift force, not a Magnus force. | [R]; standard |
| E4 | C_L = C_L(θ, Re), C_D = C_D(θ, Re) | θ = orientation of the hole hemisphere relative to the flow (tilt angle) | [P-abs] functional dependence only; [S-SlideServe] "lift magnitude depends on tilt angle" |
| E5 | F_hole = ½ ρ A U² C_h(θ, Re) · ê_h(θ) | Proposed PM-001 term for a non-spinning or slowly spinning perforated ball. ê_h is the unit normal to U in the plane containing U and the hole-asymmetry axis. | [A] |

Qualitative relations reported second-hand (no numbers):
- C_D decreases with Re, described as roughly exponential [S-SlideServe, R]. This is from the earlier student study, not necessarily the 2007 paper.
- The lift (normal force) is zero when the holes are symmetric about the horizontal (flow) axis. It is non-zero when they are asymmetric [S-SlideServe, R].
- Lindsey (TWU) says vortex formation and lift direction "depended strongly on hole orientation" [S-Lindsey].
- Press accounts say the dominant force (external or internal) depends on pitch speed, with internal flow dominating at higher speed [S-PopSci, S-Deseret]. **This was not verified against the paper's data.**

## 6. Data points

There are no numeric data points from the paper itself (abstract only). The table lists every number that I could tie to this work. Each value is labelled by where it comes from.

| quantity | value | conditions | where | provenance |
|---|---|---|---|---|
| C_D, forward-facing Wiffle ball (holes facing upstream) | ≈ 0.6 (constant) | Used by Emond et al. as a pickleball proxy at Re ≈ 2.5×10⁴. The Re range in Rossmann & Rau is unknown. | Emond et al. arXiv 2409.19000, Appendix 7 (p. 14), citing [8] = Rossmann & Rau | [S-Emond], secondary reading of the paper's data |
| Normal (lift) force when hole pattern is symmetric about the flow axis | 0 | static ball, any speed | SlideServe deck, Wiffle conclusions | [R] |
| Lift magnitude | depends on tilt angle θ (no values) | static ball | SlideServe deck | [R] |
| C_D trend | decreases with Re (described as ~exponential) | static ball | SlideServe deck | [R] |
| Lift up to ~0.2 N at ~40 mph (~18 m/s) | 0.2 N | earlier 2003 APS-DFD abstract (Utvich, Jemmott, Logan, Rossmann) | only as summarised by a search engine; the ADS page was not readable | [R], unverified. Do not use. |
| Typical Wiffle game pitch speed | 60–80 mph (27–36 m/s) | game context, not test conditions | Lafayette news 2010 | [S] |
| Number of slots | 8 oblong, on one hemisphere | standard Wiffle ball | Deseret 2010 | [S] |
| Tunnel turbulence intensity (student tunnel) | 0.3 %, 0.5 %, 6 % at different settings | the earlier student study's tunnel, perhaps a different tunnel from Lafayette's | SlideServe deck | [R] |

Derived scale numbers for comparison [A]:
- With ρ = 1.225 kg/m³, μ = 1.81×10⁻⁵ Pa·s and D = 0.071 m, POLLEN Re = 9.6×10³, 2.4×10⁴ and 4.8×10⁴ at 2, 5 and 10 m/s.
- A Wiffle ball (D ≈ 0.073 m [M]) at game speeds of 27–36 m/s has Re ≈ 1.3–1.7×10⁵. Game play is therefore 3–15× higher in Re than POLLEN. Whether the 2007 tunnel tests reach down to Re ~ 10⁴ is **unknown**.

## 7. Applicability to POLLEN

**What transfers (qualitatively):**
1. **Perforations can produce a non-Magnus normal force on a non-spinning ball.** The size and direction of this force depend on orientation relative to the flow. Two mechanisms are involved: asymmetric external separation, and internal throughflow. This is the main finding [P-abs]. It is the only peer-reviewed evidence in the PM-001 bibliography that hole-induced forces exist without spin.
2. **Hollow perforated balls have internal flow.** Air enters and leaves through the holes. That adds drag and can add a normal force that a sealed-sphere model (pickleball Cd/Cl correlations, Magnus theory) does not capture.
3. **Order of magnitude for drag.** Emond's secondary reading of the forward-facing Wiffle ball gives C_D ≈ 0.6. That is about double the free-flight pickleball value quoted by Lindsey (C_D ≈ 0.30 ± 0.02, from a different source). A perforated, hollow, possibly non-spherical POLLEN could sit anywhere in this range or outside it.

**What does NOT transfer:**
1. **Hole symmetry.** A Wiffle ball's large one-sided asymmetry (8 slots on one hemisphere, solid on the other) is the cause of its spin-free curve. Per the HANDOFF, POLLEN is a Gopher ResisDent perforated ball. Its hole layout must be checked on a real ball or in the AndyMark STEP file [A]. If the holes are roughly uniformly distributed, the hole-induced net normal force should be **much smaller** than a Wiffle ball's and should **fluctuate with orientation** rather than point one way. It is not zero: real POLLEN are "not perfectly spherical" and the hole pattern is discrete, so a small orientation-dependent C_h(θ) remains.
2. **Spin.** Rossmann & Rau measured static balls. They give **no information about Magnus lift on a perforated ball**. Holes on a spinning hollow ball could act as a centrifugal pump: air is drawn into the interior and thrown out at the equator. That could change the effective C_L(S) and might even reduce it compared with a sealed ball. This is a hypothesis [A] and is untested by this source.
3. **Reynolds regime.** Wiffle play is at Re ~ 10⁵. POLLEN is at Re ~ 10⁴–5×10⁴. Separation and transition behaviour may differ, so the speed at which internal flow dominates (a press claim) cannot be mapped onto POLLEN.
4. **Size and mass.** The size is similar (about 71 mm vs about 73 mm [M]), but POLLEN mass, wall thickness, hole size and open-area fraction are different and unmeasured. The internal-flow contribution scales with open-area fraction, which is unknown for both balls.

**Peer-reviewed vs other evidence:** the only peer-reviewed, verified content used here is the abstract: forces depend on Re and orientation, and both external asymmetry and internal flow are associated with curve without spin. The C_D ≈ 0.6 value is a preprint's secondary reading. The "lift zero when symmetric" and "C_D falls with Re" statements come from an unreviewed student deck from the same advisor. The speed-dominance claims come from press only.

## 8. Implications for the PM-001 models

1. **Aero model, drag.** Do not fix C_D at the pickleball value. Until POLLEN is measured, carry **C_D ∈ [0.30, 0.60]** as the uncertainty band. The lower end is the pickleball free-flight value (Lindsey/TWU, secondary). The upper end is the forward-facing Wiffle value (Emond reading Rossmann & Rau, secondary). Sweep it in the trajectory sensitivity runs. At 5 m/s with m = 0.025 kg and A = 3.96×10⁻³ m², drag deceleration is 0.73–1.46 m/s². That uncertainty is larger than the expected Magnus acceleration (about 0.49 m/s² at C_L = 0.2).
2. **Aero model, a non-Magnus orientation force (new term E5).** Add an optional hole-asymmetry force F_hole = ½ρAU²C_h with:
   - a random direction in the plane normal to U, fixed per shot for a non-spinning or slowly spinning ball;
   - for a spinning ball, rotation of its direction with the ball's orientation, which averages toward zero over each revolution.

   **C_h for POLLEN is unknown.** For sensitivity, use C_h ∈ {0, 0.05, 0.1} [A, not from the source]. At 5 m/s these give 0, 0.12 and 0.24 m/s², which is comparable to the Magnus effect being studied. Label it "uncalibrated, from Wiffle analogy". Monte Carlo the direction.
3. **Spin averaging argument [A].** At S = 1 and v = 5 m/s, ω ≈ 141 rad/s (about 1345 rpm), so the ball turns about 20 times in a 1 s flight. Any fixed-in-body hole force then averages out to a small residual plus a ripple. So:
   - **High-backspin shots are probably less sensitive to hole asymmetry than zero-spin shots.**
   - **The zero-spin control shot is the noisy one.** POLLEN may "knuckle" (drift erratically) at very low spin, as Wiffle balls do.

   Test plan consequence: the no-spin baseline needs more repetitions, and its scatter must not be attributed to Magnus.
4. **Magnus model.** This source gives no C_L(S) for perforated balls. Keep C_L(S) parametric with a ceiling, as the HANDOFF requires. Add a flag noting that internal throughflow may reduce C_L compared with a sealed sphere (centrifugal pumping hypothesis [A]). Calibrate it only from POLLEN tests.
5. **Calibration test design (prototype).** Use the method from this paper's design: a static POLLEN on a thin sting in an airflow, at several orientations θ (holes centred upstream vs a web between holes centred upstream) and speeds of 2–10 m/s. This would measure C_D(θ, Re) and C_h(θ, Re) directly.

   If no tunnel is available, there are two cheaper substitutes:
   - Drop tests or low-spin hand launches filmed at 240 fps, comparing the lateral scatter of zero-spin and backspin shots.
   - A fan-plus-scale rig. This is crude but enough to bound C_h to within about 0.05.
6. **Collision model.** No direct implication: the source contains no impact data.
7. **Docs and claims hygiene.** Cite Rossmann & Rau only for the qualitative claim that perforated hollow balls show orientation-dependent forces without spin. **Do not cite it for any POLLEN coefficient.** Cite the C_D ≈ 0.6 value as "Emond et al. reading of Rossmann & Rau", not as a POLLEN or pickleball measurement.

## 9. URLs used

- https://doi.org/10.1119/1.2787013 → https://pubs.aip.org/ajp/article/75/12/1099/899025/An-experimental-study-of-Wiffle-ball-aerodynamics (abstract and metadata)
- https://api.unpaywall.org/v2/10.1119/1.2787013, https://api.openalex.org/works/doi:10.1119/1.2787013, https://api.semanticscholar.org/graph/v1/paper/DOI:10.1119/1.2787013 (OA status: closed)
- http://web.archive.org/web/20180428053843/https://dspace.lafayette.edu/handle/10385/1741 (repository record, abstract, citation)
- https://ldr.lafayette.edu/concern/publications/r781wg377 (CAPTCHA-blocked)
- https://arxiv.org/pdf/2409.19000 (Emond et al.: C_D ≈ 0.6, Appendix 7)
- https://twu.tennis-warehouse.com/learning_center/pickleball/pickleball_aerodynamics.php (Lindsey: orientation-dependent lift direction)
- https://www.slideserve.com/ellie/wind-tunnel-experiments-investigating-the-aerodynamics-of-sports-balls-powerpoint-ppt-presentation (related student deck, Rossmann advisor)
- https://news.lafayette.edu/2008/01/04/andrew-rau-08-and-professor-jennifer-rossmann-publish-in-national-physics-journal/
- https://news.lafayette.edu/2010/08/19/jenn-rossmann-wiffle-ball/
- https://www.popsci.com/article/technology/how-it-works-wiffle-ball-pitch/
- https://www.deseret.com/2010/11/8/20151334/the-weird-science-of-the-wiffle-ball
