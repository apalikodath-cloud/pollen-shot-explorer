# Allen, Haake & Goodwill (2010): Effect of friction on tennis ball impacts

source_id: `allen2010` (the target paper). Companion source: `allen2009thesis`, the first author's open-access PhD thesis from the same group, written just before the paper. It shares the FE ball and string-bed models and has its own friction study (§3). The thesis is **not** the 2010 paper. Every row below says which of the two it came from.
Read: 2026-10-30, research agent for PM-001.

## 1. Citation, access, review status

| Field | Value |
|---|---|
| Citation | T. Allen, S. Haake and S. Goodwill, "Effect of friction on tennis ball impacts", *Proc. IMechE Part P: J. Sports Engineering and Technology* **224**(3), 229–236 (2010). DOI 10.1243/17543371JSET66 |
| Dates (Crossref) | Online 14 May 2010; issue dated 1 Sep 2010 |
| Affiliation | Centre for Sport and Exercise Science / Sports Engineering Research Group, Sheffield Hallam University, UK |
| Review status | Peer-reviewed journal (SHURA record type "PeerReviewed"). Semantic Scholar shows 25 citations. |
| Method type | **Finite-element (FE) simulation only** (Ansys/LS-DYNA). The paper is a parametric FE study and contains no new experiments. The models it uses were validated against experiments in earlier work by the same group (thesis; Allen et al. TST 2007 and Engineering of Sport 7, 2008). |
| Access | **Abstract only.** SAGE full text is paywalled (WebFetch got HTTP 403). Unpaywall reports `is_oa=false`, `oa_status=closed`, no repository copy. Semantic Scholar reports `openAccessPdf.status=CLOSED`. The SHURA record (shura.shu.ac.uk/2149) has the abstract only. Searches found no ResearchGate, academia.edu or CORE copy. A direct scrape of the SAGE page was refused by this session's permission policy and was not attempted again. |
| Consequence | No figure, table or equation from the 2010 paper was seen. **No numbers from the 2010 paper are reported here.** None were filled in from memory. The numbers in §4 come from the open companion thesis and are labelled with that source. |

URLs tried: https://doi.org/10.1243/17543371JSET66 → https://journals.sagepub.com/doi/10.1243/17543371JSET66 (403), https://shura.shu.ac.uk/2149/ (record and abstract metadata; no PDF), https://api.unpaywall.org/v2/10.1243/17543371JSET66, https://api.semanticscholar.org/graph/v1/paper/DOI:10.1243/17543371JSET66, https://api.crossref.org/works/10.1243/17543371JSET66 (partial reference list), https://shura.shu.ac.uk/3215/2/10701264.pdf (companion thesis, **full text, 291 pp., OCR**), https://shura.shu.ac.uk/5518/ (Allen et al. spin-ratio follow-up, abstract only).

**Action for the lead:** to get the friction-sweep curves, someone with SAGE or IMechE library access needs the PDF. Those curves are rebound velocity, angle and spin against COF, plus the time histories of the slide, overspin and roll phases. With the PDF, fill the "TBD" rows in §4.3.

## 2. What the 2010 paper reports (abstract, verbatim from the SHURA and SAGE metadata)

> "There are currently no restrictions on the coefficient of friction of tennis courts or strings. The aim of this paper was to determine the effect of friction on tennis ball impacts. Finite element models were used to determine the effect of friction for oblique spinning impacts both between a tennis ball and a rigid surface and between a tennis ball and the string bed of a freely suspended racket. The results showed that during an oblique impact a tennis ball can behave in any of the following ways: first, it can slide, second, it can slide and then 'overspin', or, third, it can slide, overspin, and then converge towards rolling. The ball will slide throughout the majority of impacts on the court during play. Therefore, the rebound topspin of the ball will increase with increasing court friction and the horizontal rebound velocity will decrease. The ball will roll off the string bed for the majority of groundstrokes and the rebound properties will effectively be independent of string-bed friction."

Keywords: friction, tennis ball, impacts, finite element models.

Findings (peer-reviewed conclusions, but **no numbers were visible**):
1. **Three impact regimes.** (a) Sliding throughout. (b) Sliding, then overspin: the contact point reverses slip because tangential compliance stores and releases energy. (c) Sliding, then overspin, then convergence to rolling. Rolling here means v_t = Rω at the contact.
2. **Court (rigid surface) impacts mostly slide throughout.** So friction directly sets the outcome. Higher μ gives more rebound topspin (in tennis sign convention, spin pushed toward rolling) and a lower horizontal rebound speed.
3. **String-bed impacts on a freely suspended racket mostly reach rolling.** The rebound is then nearly independent of μ.
4. Implied general rule: **μ matters only while the contact is sliding.** Once grip (rolling) is reached, extra friction adds almost nothing. Tangential compliance can then push the ball past rolling (overspin).

Crossref reference list (partial; it shows the context): Brody 1988 (TennisPro; slow courts); Allen, Goodwill & Haake, TST 2007 (ball FE validation); Goodwill et al., TST 2007 (spin in elite match play); Kelley et al. 2008, Eng. of Sport 7 (Wimbledon spin data); Allen et al. 2008, ANSYS UK conference (head-clamped racket FE); Allen et al. 2008, Eng. of Sport 7 (string-bed FE validation); Choppin et al. 2008, Eng. of Sport 7 (Wimbledon ball and racket kinematics). Several other entries have no metadata in Crossref.

## 3. Method (as far as it can be reconstructed)

From the abstract: FE models of (i) a ball against a rigid surface and (ii) a ball against the string bed of a **freely suspended** racket. Oblique, **spinning** inbound conditions. COF is varied while the other inputs stay fixed.

From the companion thesis (Allen 2009, same author, same models). This is **context, not confirmed to be identical to the 2010 runs**:
- Ball: pressurised tennis ball in Ansys/LS-DYNA 10.0. Rubber core uses MAT_OGDEN_RUBBER plus viscoelastic terms. Felt uses MAT_LOW-DENSITY_FOAM. Internal pressure is an airbag pressure-volume curve (AIRBAG_SIMPLE_PRESSURE_VOLUME). Total mass 5.92×10⁻² kg; felt mass 1.67×10⁻² kg (thesis §3.3, p. 68).
- Rigid surface: MAT_RIGID with 18 000 bricks; CONTACT_AUTOMATIC_SURFACE_TO_SURFACE with SOFT = 1; time-step scale 0.5; hourglass coefficient 0.15. **Ball-to-rigid-surface COF = 0.62**, chosen to represent a smooth Rebound Ace hard court (cited to Brody et al. 2002) (thesis p. 69).
- String bed: individual strings modelled. Ball-to-string COF = 0.4 (chosen in the sweep, §4.2). String-to-string COF = 0.1. String E = 7.2 GN m⁻² ("Hammer" method) (thesis §4.3–4.4, pp. 106–110).
- Validation (thesis): impacts filmed with two synchronised Phantom v4.2 high-speed cameras and analysed in 3D. Light gates and a force plate were used for normal impacts.
- Friction law in LS-DYNA: Coulomb, μ times the contact normal force, applied node by node. Here "slide" and "roll" are emergent outcomes of a **deformable** body. They are not states imposed by a rigid-body rule.

## 4. Equations

### 4.1 Equations stated in the open sources

| # | Equation | Symbols / units | Source |
|---|---|---|---|
| E1 | SPR = 100 (1 − μ) | SPR = surface pace rating (dimensionless, ITF). μ = ball–surface COF (dimensionless) | thesis §2.2.4, p. 13 (cites Capel-Davies) |
| E2 | Rolling (grip) condition at the contact: v_t = R ω | v_t = ball COM velocity tangential to the surface [m/s]. R = ball radius [m]. ω = angular velocity [rad/s], with its sign set so that rolling makes the contact-point slip zero | thesis §2.2.4 and §8.4 ("overspinning ... faster rotation than that associated with rolling") |
| E3 | Spin ratio SR = R ω / v_t (inbound SR_in, outbound SR_out) | dimensionless. SR = 1 means rolling, SR > 1 means overspin | Allen et al. 2012 follow-up abstract (SHURA 5518): "the product of the ball's angular velocity and radius divided by the centre of mass velocity tangential to the surface". FE validated for SR_in ∈ [−1, 1] |
| E4 | Coulomb friction F_f ≤ μ N, directed against contact slip | N = normal force [N] | used throughout. Thesis §4.4 warns: "any analytical model that assumes a simple, linear relationship between a friction and vertical reaction force is invalid", because the measured horizontal force (friction plus string reaction) changes sign during contact |

**The 2010 paper's own equations were not visible.** As an FE paper, its main content is probably plots rather than closed-form models. That is an inference and is unverified.

### 4.2 Rigid-body impulse model that matches the paper's regimes (**derived here, not from Allen 2010**)

This is the standard Brody (1984) and Cross (2002) type model. The thesis reviews it in §2.6.1. Use it as the PM-001 collision baseline and add tangential compliance on top.

Contact frame: n = surface normal (out of surface), t = tangent along the inbound tangential motion. The ball has mass m [kg], radius R [m], and moment of inertia I = α m R². α = 2/5 for a solid sphere and 2/3 for a thin shell; POLLEN is perforated, so measure or compute it (likely 0.55–0.67, an assumption). The inbound normal speed is v_n > 0 toward the surface, the inbound tangential speed is v_t, and the spin is ω. Sign: ω > 0 is the rolling sense for motion along +t (topspin relative to this surface).

- Contact-point slip speed: u₀ = v_t − R ω  [m/s]. A ball with **backspin** relative to the surface has ω < 0, so u₀ = v_t + R|ω| and the slip is **larger**.
- Normal impulse: J_n = m (1 + e_n) v_n. e_n is the normal COR, to be measured for POLLEN on each HIVE material.
- Grip-limit (critical) friction:
  **μ_c = α u₀ / [(1 + α)(1 + e_n) v_n]**
- **Slides throughout (μ < μ_c)**, regime (a) in the paper:
  v_t' = v_t − μ (1 + e_n) v_n
  ω' = ω + μ (1 + e_n) v_n / (α R)
  Both changes are linear in μ. This is the paper's court finding: horizontal rebound speed falls with μ, and spin moves toward rolling with μ.
- **Reaches rolling (μ ≥ μ_c)**, regime (c) without the overspin:
  v_t' = (v_t + α R ω)/(1 + α), ω' = v_t'/R. **Independent of μ.** This is the paper's string-bed finding.
- **Overspin (tangential compliance)**, regime (b): replace "slip → 0" with a tangential restitution e_t ∈ [−1, 1], u' = −e_t u₀ while the impulse stays within the friction cone. Then:
  v_t' = v_t − α (1 + e_t) u₀/(1 + α)
  R ω' = R ω + (1 + e_t) u₀/(1 + α)
  e_t > 0 gives spin beyond rolling. The thesis and Allen 2010 attribute this to felt shear and forward ball deformation. POLLEN has no felt, so its e_t must be measured.
- **Tangential reversal criterion (rolling branch):** v_t' < 0 when α R |ω_back| > v_t, i.e. SR_back > 1/α. That is ≈ 1.5 for a thin shell and 2.5 for a solid sphere. In the sliding branch, v_t' < 0 needs μ(1 + e_n) v_n > v_t.

### 4.3 Worked numbers for a POLLEN-like ball (**assumption-driven illustration, not data**)

Inputs: speed 5 m/s, 45° incidence on a horizontal face, so v_t = v_n = 3.54 m/s. Backspin with S = Rω/|v| = 1, so R|ω| = 5 m/s and u₀ = 8.54 m/s. R = 0.0355 m.

| α | e_n | μ_c (critical) |
|---|---|---|
| 0.667 | 0.3 / 0.5 / 0.7 | 0.743 / 0.644 / 0.568 |
| 0.600 | 0.3 / 0.5 / 0.7 | 0.696 / 0.604 / 0.533 |
| 0.400 | 0.3 / 0.5 / 0.7 | 0.531 / 0.460 / 0.406 |

So with plausible plastic-on-plastic or plastic-on-wood μ ≈ 0.2–0.5 (an assumption, not measured), **a backspinning POLLEN striking the HIVE will most likely slide throughout contact**. That is the same regime the paper reports for tennis-on-court. In that regime the rebound depends directly and linearly on μ and e_n. For example, at μ = 0.3, e_n = 0.5, α = 2/3: v_t' = 3.54 − 1.59 = 1.95 m/s, and R|ω| falls from 5.0 to 2.6 m/s (backspin retained, reduced).

## 5. Data table

Only rows marked `allen2010` come from the target paper. Those rows are qualitative because only the abstract was readable. Rows marked `allen2009thesis` come from the open thesis. Rows marked `derived` are this note's calculations.

| Quantity | Value | Conditions | Where | source_id |
|---|---|---|---|---|
| Impact regimes | slide / slide→overspin / slide→overspin→converge to roll | FE, oblique spinning tennis-ball impacts, rigid surface and freely suspended racket | Abstract | allen2010 |
| Court impact regime in play | "slide throughout the majority of impacts" | FE, rigid surface, play-representative conditions (values not seen) | Abstract | allen2010 |
| d(rebound topspin)/dμ (court) | > 0 (sign only) | sliding regime | Abstract | allen2010 |
| d(horizontal rebound speed)/dμ (court) | < 0 (sign only) | sliding regime | Abstract | allen2010 |
| String-bed groundstrokes regime | roll off the string bed; rebound ≈ independent of μ | FE, freely suspended racket | Abstract | allen2010 |
| COF sweep values, inbound v/angle/spin, rebound curves | TBD (paywalled) | n/a | body, figures | allen2010 |
| Ball–rigid-surface COF used in FE | 0.62 | represents smooth Rebound Ace hard court (cites Brody et al. 2002) | thesis §3.3.1, p. 69 | allen2009thesis |
| Ball–string COF chosen | 0.4 | string-bed FE; tested 0.2, 0.4, 0.6 | thesis §4.4.2–4.4.3, pp. 108–110 | allen2009thesis |
| Effect of ball–string COF 0.4 → 0.6 | "only a minor effect" on rebound v, angle, spin | 30 m/s, 40°, inbound backspin 0–~600 rad/s; E = 7.2 GN m⁻² | thesis Fig. 4.12, p. 108 | allen2009thesis |
| Effect of ball–string COF 0.4 → 0.2 | more pronounced; COF 0.2 **over-predicts rebound spin** vs experiment | same | thesis Fig. 4.12, p. 108 | allen2009thesis |
| Optimum friction for spin | "there is an optimum value of ball to string friction for obtaining maximum rebound spin" (higher μ → faster grip → stronger overspin reversal → lower final spin) | 30 m/s, 40°, 200 rad/s backspin | thesis Fig. 4.13, pp. 108–109 | allen2009thesis |
| Horizontal force sign reversal time | ≈ 2.85 ms (just after mid-contact), reverses again ≈ 4.2 ms | string bed, 30 m/s, 40°, 200 rad/s backspin | thesis Fig. 4.11, p. 107 | allen2009thesis |
| String-to-string COF effect | no significant effect for 0.01–0.3; 0.1 used | 30 m/s, 40°, backspin 0–600 rad/s | thesis Fig. 4.14, pp. 109–110 | allen2009thesis |
| Ball–string sliding COF (Cross 2000b) | 0.27–0.42 (sliding), 0.05 (rolling) | 5 strings; quasi-static drag with up to 10 kg load (method criticised as traction, not friction) | thesis §2.3.3, p. 19 (secondary) | allen2009thesis |
| Felt–string COF (Cross et al. 2000) | mostly 0.15–0.18; range 0.11–0.36 | string wrapped twice on felt-covered 60 mm pipe, 0.15 kg mass | thesis §2.3.3, p. 19 (secondary) | allen2009thesis |
| Ball–string time-averaged sliding COF (Cross 2003) | 0.43 ± 0.02 | hand-thrown, low speed, 25° to string plane, accelerometer on frame | thesis §2.3.4, p. 21 (secondary) | allen2009thesis |
| COR, ball on rigid surface (2.54 m drop) | ≈ 0.74 (vs 0.75–0.8 head-clamped racket) | tennis ball | thesis §2.3.4, p. 20 (cites Brody et al. 2002) | allen2009thesis |
| Contact time, string bed | ≈ 5 ms | tennis | thesis p. 20 (secondary) | allen2009thesis |
| Oblique vs normal impact, ball volume | ≈ 10% smaller volume in oblique impact → higher pressure, higher vertical COR | FE (Goodwill et al. 2005) | thesis §2.6.1, p. 40 (secondary) | allen2009thesis |
| Rolling onset vs incidence (Capel-Davies 2007) | no rolling phase for incidence up to 25°; horizontal COR ∝ incidence angle; SPR independent of v_t 11–31 m/s and angle 11–25° | tennis on court surfaces | thesis §2.6.1, p. 38 (secondary) | allen2009thesis |
| Tennis ball internal pressure | 76 kPa | measured (Goodwill et al. 2005) | thesis p. 40 (secondary) | allen2009thesis |
| Critical μ_c for POLLEN-like ball | 0.41–0.74 | 5 m/s, 45°, S = 1 backspin; α ∈ {0.4, 0.6, 0.667}; e_n ∈ {0.3, 0.5, 0.7} | this note §4.3 | derived |
| Tangential reversal threshold (rolling branch) | SR_back > 1/α ≈ 1.5 (shell) to 2.5 (solid) | rigid-body impulse model | this note §4.2 | derived |

## 6. Applicability to POLLEN

**Transfers (qualitatively, from peer-reviewed FE):**
- The **regime logic**: slide, overspin, roll. Friction controls the rebound only while the contact slides. For a backspinning POLLEN hitting the HIVE rim or interior, backspin **increases** the inbound slip u₀, so sliding throughout is **more** likely. That makes the rebound strongly μ-dependent, the same way tennis-on-court is.
- The **sign of the friction effects** in the sliding regime. Higher μ removes more tangential velocity and moves spin further toward rolling. For backspin, that means more backspin destroyed and a larger "check" of forward motion. With enough μ(1 + e_n)v_n, or with SR > 1/α when grip is reached, the tangential velocity can **reverse**. That is a physical mechanism for hypothesis (B) in HANDOFF §0: a rim or interior contact that redirects a backspinning ball back into the CELL.
- An **optimum μ for spin** exists when overspin happens (thesis string-bed result). On the launcher side, more friction is not always more spin at the flywheel or hood contact either.
- The warning that a single-valued "friction ∝ normal force" analytical model can misrepresent compliant-ball impacts. The horizontal force changes sign mid-contact.

**Does not transfer:**
- All numeric μ, COR and contact-time values. They are for a **pressurised rubber core with felt** (59 g, ~67 mm) on courts or strings at 20–35 m/s. POLLEN is a ~25 g perforated polyethylene shell at 2–10 m/s on HIVE plastic, wood or metal. The tennis overspin mechanism relies on felt shear and core buckling; POLLEN shell flexing and its holes are a different mechanism. **Do not use 0.62 or 0.4 as POLLEN μ.**
- The FE material models (Ogden rubber, foam felt, airbag). A perforated PE shell does not hold internal pressure.
- The impact speed range (much higher in tennis). Rate-dependent COR and contact times will differ.

## 7. Implications for the PM-001 models

1. **Contact model (HANDOFF §4E):** implement the §4.2 rigid-body impulse model with three branches (slide / grip / compliance with e_t). Parameters: μ (per HIVE surface), e_n(v_n), e_t, α_POLLEN. Run unit tests on these: (i) μ = 0 leaves v_t and ω unchanged; (ii) μ ≥ μ_c gives v_t' = Rω'; (iii) in the sliding branch, Δv_t is linear in μ; (iv) the reversal criterion.
2. **Classify every simulated HIVE contact** by regime (slide / grip / overspin) and log μ_c. If most contacts are "slide", the scoring map is directly sensitive to μ. Then measuring POLLEN-on-HIVE μ becomes **mandatory**, not optional.
3. **Spin sign at contact matters.** Backspin relative to the direction of travel is not the same as backspin relative to the struck surface. On a sidewall or a tilted lip, the contact frame rotates, so the same ball spin can be "topspin-like" relative to the face. Compute u₀ in the contact frame for each surface.
4. **Launcher (HANDOFF §4C/4D):** the flywheel–ball and hood–ball contacts are long, sustained contacts, not impulsive bounces. Still, the same regime question applies: does the ball reach rolling on the wheel and the hood? If it slides throughout (μ low, contact short), exit spin depends linearly on μ and contact time. If it grips, exit spin is set by kinematics (S_exit ≈ 1 ideal). An optimum, rather than a monotonic, μ effect is possible if the shell flexes (overspin). Measure the exit (v, ω) map rather than trusting either limit.
5. **Uncertainty bounds:** sweep μ ∈ [0.1, 0.7], e_n ∈ [0.3, 0.8], e_t ∈ [−0.2, 0.4] and α ∈ [0.5, 0.67] in the collision Monte Carlo. All four are assumptions until measured.
6. **Tests to run on the prototype** (cheap and decisive):
   - Inclined-plane static or kinetic μ for POLLEN on each HIVE material (tilt the plate until the ball slides with its spin locked, or drag it with a force gauge at a few loads).
   - Drop tests for e_n at 2–8 m/s.
   - Oblique spin-bounce tests filmed at ≥ 240 fps against a HIVE-material plate. Vary incidence (30–70°) and backspin (from the actual shooter). Measure v_t', ω' and fit the slide / grip / e_t branches. Check directly whether the tangential velocity reverses, which is the mechanism for hypothesis (B).
7. **Do not** cite Allen 2010 for any number. Cite it only for the qualitative regime structure and the sign of the μ effects.

## 8. Caveats

- Abstract only for the target paper. The quantitative content (COF sweep ranges, inbound conditions, magnitudes) is unknown.
- The thesis is a companion, not the paper. Its friction sweep is for a head-clamped or string-bed model, not the freely suspended racket or rigid-surface sweep in the 2010 paper. The thesis text is OCR; numbers were checked against context, but figure-axis values were not readable, so none were taken from figures.
- Most secondary values in §5 (Cross 2000, 2003; Brody 2002; Capel-Davies 2007; Goodwill 2005) are quoted as the thesis reports them and were not checked against their primary sources.
- §4.2–4.3 are this note's own derivation and calculation. They are standard rigid-body mechanics, labelled as derived, and are not results from Allen 2010.
