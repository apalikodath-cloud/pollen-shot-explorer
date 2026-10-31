# Cross (2010): Impact of a ball on a surface with tangential compliance (full read + check of sweep_impact.md)

source_id: `cross2010tang` (same id as research/sweeps/sweep_impact.md and research/checks/sweep_impact.md; source #19 in RESEARCH_PAPERS.md).
Read: 2026-10-30, research agent for PM-001 (source #19 task). This note covers the full paper. It does not rely on the earlier skim.

## 1. Citation, access, review status

| Field | Value |
|---|---|
| Citation | R. Cross, "Impact of a ball on a surface with tangential compliance", *American Journal of Physics* **78**(7), 716–720 (July 2010). DOI 10.1119/1.3313455 |
| Dates | Received 8 Sep 2009; accepted 20 Jan 2010 (from the paper) |
| Affiliation | Physics Department, University of Sydney |
| Review status | Peer-reviewed journal article |
| Method type | **Theory only.** It is a lumped analytical/numerical model (a ball on a spring-mounted "cart") with no new experiments. The experimental statements in it are cited from other work. So its *results* are graded **theory** (peer-reviewed). They are not peer-reviewed experimental findings. |
| Access | **Full text** (author's PDF, 5 pp.). All pages were read as text, and pp. 2–4 (equations, Figs. 1–4) were rendered as images to check the Greek symbols and the inequalities. |

URLs tried:
- https://www.physics.usyd.edu.au/~cross/PUBLICATIONS/47.%20MoreSpin.pdf (HTTP 200, full text; downloaded to a fresh %TEMP% folder and converted to text and images only; nothing was executed)
- https://doi.org/10.1119/1.3313455 → pubs.aip.org (HTTP 403)

## 2. What the paper reports

Question: can a surface that is compliant **along** the contact (tangentially) make a ball leave with **more** spin than the rolling value? Strings that slide sideways and snap back (the polyester-string topspin anecdote) motivate the question. **[theory, peer-reviewed]**

Findings (the model's own results, graded **theory**):
1. If a surface is rigid or heavy in the tangential direction, an oblique ball either slides throughout or grips and then rolls. Its exit spin cannot exceed the rolling value (rω2 ≈ v_x2). This is the heavy-cart limit.
2. If the surface is a **light** mass on a tangential spring, the ball grips it, drags it, stores spring energy, and gets that energy back as extra spin through **static** friction while the spring returns. Exit spin can then **exceed** the rolling value, and the tangential COR e_x approaches 1.
3. The extra spin is largest when the cart mass is small compared with the ball and when the spring's period is about matched to the impact duration, so that the cart returns before the ball leaves.
4. **Incoming backspin reduces exit spin compared with zero incoming spin, for θ1 < 60°** (θ1 measured from the surface). At larger θ1, backspin can give more exit spin on a light cart, because the ball slides longer and loads the spring further (this depends on k).
5. Extra spin comes with **lower** exit tangential speed, so the rebound leaves **closer to the normal**.
6. After grip, the friction force can drop almost to zero (heavy cart), stay large (light cart, stiff spring), or **reverse and re-slide late in the contact** (light cart, k = 40 kN/m).

Context that is cited, not shown, in the paper (**secondary**; grade as in the original sources):
- On deformable surfaces e_y can exceed 1 in oblique impact (Louge & Adams; Kuninaka & Hayakawa).
- A ball can grip on a hard surface for incidence up to about 50° from the normal (from Cross's earlier grip–slip work).
- Friction can reverse direction more than once during a single contact (Cross 2002 grip–slip).

## 3. Method

- The ball is a rigid sphere (mass m, radius r, I_cm = α m r²) with normal force N = N0 sin(πt/T) over a fixed contact time T, N0 = π m v_y1 / T, and e_y = 1 in the worked cases.
- The surface is a cart of mass M on a tangential spring of stiffness k. While the contact point slides relative to the cart, friction is kinetic (μN). When the relative speed reaches zero, the ball and cart move together under static friction F_s, provided |F_s| ≤ μN. Otherwise the contact re-slides.
- The equations are integrated numerically, and the slide-throughout threshold is found in closed form.

## 4. Equations (as printed, checked against rendered pages)

| # | Equation | Meaning | Source |
|---|---|---|---|
| C1 | v_x = v_x1 − (μ N0 T / (π m))(1 − cos πt/T) | sliding phase, ball tangential speed | Eq. 1 |
| C2 | ω = ω1 + (μ N0 T r / (π I_cm))(1 − cos πt/T) | sliding phase, spin | Eq. 2 |
| C3 | M d²X/dt² = μ N0 sin(πt/T) − kX | cart during sliding | Eq. 3 |
| C4 | −F_s/m − F_s r²/I_cm = (F_s − kX)/M | grip condition (contact points share acceleration) | Eq. 4 |
| C5 | F_s = m k X / [M (1 + m/M + m r²/I_cm)] | static friction during grip | Eq. 5 |
| C6 | d²X/dt² = −k X / [M + m α/(1+α)] | grip phase: an oscillator with effective mass M + mα/(1+α) | Eq. 6 |
| C7 | tan θ1 = (1 − rω1/v_x1) / [2μ(1 + 1/α)] | slide-throughout threshold (slides for smaller θ1) | Eq. 7 |
| C8 | ω2 = ω1 + 2 μ v1 sin θ1 / (α r) | exit spin if sliding throughout | Eq. 8 |

Angle convention: θ1 is measured **from the surface** (90° = normal incidence). Ghaednia/Cermik's β and allen2010's angles are measured from the normal, so convert before comparing.

**Link to src/contact.py (derived here, theory):** contact.py's stick test |P_t*| ≤ μ P_n with P_t* = −(1+e_t) m_t v_ct and m_t = m α/(1+α) reduces **exactly** to C7 when e_t = 0 and e = 1, because the normal impulse is then 2 m v_y1. For general e the factor 2 becomes (1+e). So contact.py's grip/slide boundary is Cross's heavy-cart boundary. The code is consistent with this paper's rigid limit, and C8 is its slide branch.

Check (derived): with μ = 0.4 and α = 0.55, C7 gives θ1 = 23.9° for ω1 = 0, which matches the paper. For ω1 = −100 rad/s at v1 = 10 m/s, recomputing C7 gives ≈ 31.6° against the paper's 31.0°. The small gap is probably rounding or the paper's handling of v_x1, and it does not matter here. A spot check of N0 is consistent with the quoted 109 N at t = 1.7 ms (≈ 0.4 × 310 N × sin(π·1.7/5)).

## 5. Data table (all model outputs = theory; no POLLEN values)

Model inputs as stated: m = 57 g, r = 33 mm, v1 = 10 m/s, μ = 0.4 ("typical for a tennis ball sliding on smooth tennis strings"), α = 0.55, T = 5 ms, e_y = 1, ω1 = 0 or −100 rad/s.

| Quantity | Value | Conditions | Where | source_id |
|---|---|---|---|---|
| Exit spin, slide-throughout branch | ω2 = ω1 + 440.8 sin θ1 (rad/s) | stated inputs | §III text | cross2010tang |
| Slide-throughout range | θ1 < 23.9° | ω1 = 0, k = 40 kN/m (heavy-cart threshold) | §III, Fig. 2 | cross2010tang |
| Slide-throughout range, softer spring | up to 26.6° | ω1 = 0, k = 15 kN/m, M = 10 g | §III, Fig. 2 | cross2010tang |
| Slide-throughout range with backspin | θ1 < 31.0° | ω1 = −100 rad/s | §III, Fig. 2 | cross2010tang |
| Max exit spin, heavy cart | 178.6 rad/s at θ1 = 23.9°; falls at larger θ1; zero at normal incidence | M = 10 kg, ω1 = 0 | §III, Fig. 2 | cross2010tang |
| Heavy cart at θ1 = 60° | slides 2.25 ms, then grips; friction then drops almost to zero; rω2/v_x2 = 0.992 (rolling) | M = 10 kg | §III, Fig. 3 | cross2010tang |
| Light cart, stiff spring, 60° | cart reaches 3.2 m/s at 1.7 ms, grip; friction falls from 109 N to 90 N; max cart travel 4.4 mm at 2.3 ms; **re-slides near the end** | M = 10 g, k = 40 kN/m | §III, Fig. 3 | cross2010tang |
| Light cart, soft spring, 60° | cart reaches 5.0 m/s at 1.34 ms, grip; max travel 7.7 mm at 3.1 ms; force reaches zero at the end as the cart returns | M = 10 g, k = 15 kN/m | §III, Fig. 3 | cross2010tang |
| Exit spin and e_x vs cart mass, 60° | 162.8 rad/s, e_x = 0.62 (M = 10 g); 216 rad/s (1.0 g); 223 rad/s, e_x = 0.99 (0.1 g) | k = 15 kN/m | §III | cross2010tang |
| Backspin effect | backspin gives less exit spin than ω1 = 0 for θ1 < 60°; at θ1 > 60° it can give more on the 10 g cart, depending on k | ω1 = −100 vs 0 | §III, Fig. 4 | cross2010tang |

## 6. Applicability to POLLEN

**Transfers qualitatively (theory):**
- **A rigid or heavy surface cannot give over-rolling spin.** A HIVE CELL lip or panel that is stiff and massive in the tangential direction, compared with a ~25 g ball over a few-ms contact, is the heavy-cart case. Its rebound is bounded by slide-throughout or grip-then-roll, which is exactly what contact.py with e_t ≈ 0 models.
- **Incoming backspin widens the slide-throughout range** (C7: the numerator grows by r|ω1|/v_x1). This agrees with allen2010.md's note that strongly backspinning POLLEN will mostly **slide** on HIVE contacts, so μ, not e_t, controls the rebound there.
- **Backspin lowers exit spin at shallow-to-moderate angles.** More inbound backspin is not automatically more useful after a contact. This is consistent with the HANDOFF rule "more backspin is not always better".
- **Spin enhancement steers the rebound toward the normal.** For a HIVE CELL entry this could help (steeper drop into the CELL) or hurt (bounce back out), depending on the lip geometry. It is not a design claim.

**Does not transfer:**
- None of the numbers do. They are a 57 g tennis ball, μ = 0.4, T = 5 ms, v1 = 10 m/s, and carts of chosen mass and stiffness. POLLEN's mass, α (≈ 0.63 in contact.py, shell 0.667), μ against HIVE plastic, and contact time are unmeasured.
- The paper treats the ball as tangentially rigid. A thin perforated PE shell may have its own tangential compliance, which the paper explicitly leaves out. That ball-side compliance is the only plausible source of e_t > 0 against a rigid HIVE.

## 7. Check of research/sweeps/sweep_impact.md against the full text

What the sweep got **right**:
- The paper is peer reviewed, AJP 78(7):716–720, and the spring-cart description is accurate (line 14).
- "Spin can exceed the rolling value. Calibrate this; it is not a design claim" (line 112) is a correct reading, and the hedge is appropriate.
- research/checks/sweep_impact.md item 13 copied the Fig. 3 numbers (0.992; 162.8 rad/s, e_x = 0.62; 216; 223, e_x = 0.99) correctly.

What it **missed** or **overstated**:
1. **The conditions for enhancement were omitted.** Over-rolling spin needs (a) a tangential mass that is **small compared with the ball** (10 g → 0.1 g against 57 g), (b) a restoring **spring** whose period is about matched to the contact time, and (c) the surface **returning** before the ball leaves. A rigid or heavy HIVE panel meets none of these, and that is the heavy-cart case. Line 14's "applies ... to a compliant HIVE panel" holds only for a panel that is light and springy *tangentially* over a few ms. That panel is unidentified (the HIVE material is not identified, per research/COMPLETENESS.md).
2. **The passive-roller analogy is overstated (inference, theory).** A free-spinning passive roller is a cart **with no spring** (k ≈ 0), with effective tangential mass I_roller/R_roller². With no restoring force it cannot store and return tangential energy, so the paper's enhancement does not happen. A light roller mostly **reduces slip and the friction impulse**, so it pushes the ball toward *less* spin change, not more. A spring-loaded or detented roller would be needed to match the model. The sweep's "usable lumped template for ... a light passive roller" should be read as "template for a roller with a torsional spring or brake", not for a free roller. In the launcher, the passive upper roller is a sustained, driven contact (launcher.py slip_t = R_t·Ω_t − (v − s·r_c)), which is outside this impact model altogether.
3. **The backspin result was not carried.** For θ1 < 60° (from the surface), inbound backspin gives *less* exit spin and a *larger* slide-throughout range (31.0° vs 23.9° in the worked case). PM-001 deals with backspinning POLLEN, so this is the more relevant result. Its practical message is "expect sliding, so μ matters", not "expect enhancement".
4. **e_t / e_x ranges were mixed up.** The model's e_x = 0.62–0.99 applies only to the light-cart cases. The sweep keeps measured rigid-surface e_x ∈ [0, 0.2] (cross2002grip) as the default, which is right. contact.py's sweep variant e_t = 0.3 should be labelled an **upper bound representing some unidentified tangential compliance**, not justified by cross2010tang for a rigid HIVE.
5. **Late re-slip was not mentioned.** In the 10 g / 40 kN/m case the contact grips and then **re-slides near the end**. contact.py's single-impulse law (one slide-or-stick decision per contact) cannot represent that. This is a known structural limit, not a bug, and it matters only if a compliant surface is modelled.
6. **e_y > 1 on deformable surfaces** (secondary, cited in the paper's introduction) was not noted. contact.py caps e at 1 for its energy bound, which is fine for a stiff HIVE. A soft liner could break that cap only in oblique impact, so it is not a concern for the default model.
7. **The grade should be tightened.** The sweep lists the paper as "PR" without noting that it is pure model calculation. Its results are **peer-reviewed theory**, not measured behaviour of any real surface, and should be graded that way in params_lit.json and LITERATURE_SYNTHESIS.md (both owned by another workflow, so this is a recommendation only).
8. **Rebound direction was not mentioned.** Enhanced spin comes with lower v_x2, so the ball leaves nearer the normal. Any "compliant HIVE helps" argument has to include the changed exit angle, not just the spin.

Answer to research/COMPLETENESS.md line 28 ("fold Cross 2010 into contact.py's compliant-panel option, or drop it explicitly"): **keep it as a documented limit, not a default.** With e_t = 0, contact.py already reproduces Cross's heavy-cart threshold (C7). A compliant-panel option should be added only if a real HIVE or hood surface is shown to be light and springy tangentially. If one is, model it as a cart oscillator (C3–C6), not by raising e_t.

## 8. Implications for the PM-001 models, hood and test plan

1. **contact.py (no change implied; src/ is owned by another workflow).** Keep e_t ∈ [0, 0.2] for HIVE contacts. Treat e_t = 0.3 as a sensitivity upper bound. Add a regression test (proposal) that with e = 1 and e_t = 0 the stick/slide boundary equals C7 (≈ 23.9° from the surface for μ = 0.4, α = 0.55). That pins the code to a published closed form. **[theory]**
2. **Backspin and HIVE contacts.** Use C7 with POLLEN's μ, α and e (factor 1+e instead of 2) to map which CELL-lip contacts slide throughout for the expected backspin. For those contacts, the outcome depends on μ alone, which makes measuring POLLEN-on-HIVE-plastic μ (the glancing plateau; see ghaednia2015.md §7.3) the priority over e_t. **[theory]**
3. **Hood.** A rigid stationary hood is the heavy cart: hood compliance adds no spin beyond what the wheel/hood slip produces. A tangentially compliant hood liner could return energy only if it springs back **within** the ball's dwell on it. The launcher contact is a sustained squeeze over the wrap angle, not a few-ms impact, so this transfers only as a qualitative caution. Do not tune mu_hood or the liner on the basis of Cross 2010. **[theory, inference]**
4. **Passive upper roller.** Do not cite Cross 2010 for spin enhancement from a free roller (see §7 item 2). Its effect belongs in launcher.py's roller slip model. **[inference]**
5. **Test plan.** In POLLEN bounce tests on HIVE plastic, measure e_x = −(v_x2 − rω2)/(v_x1 − rω1) at several incidences with zero spin and with backspin. If e_x stays ≈ 0–0.2, the heavy-cart model holds. If e_x is clearly > 0.3 on a rigid HIVE, the ball shell itself supplies tangential compliance, which needs a separate model. **[test proposal]**

## 9. Caveats

- The paper is pure theory with chosen parameters, and its spring–cart is an idealisation of strings. The author notes that inter-string friction (which behaves like a heavier cart) would reduce the effect and that a chain of masses would be a refinement.
- My recomputation of the ω1 = −100 threshold (31.6° vs the printed 31.0°) is derived and minor.
- Fig. 2 and Fig. 4 curves were read only for the values stated in the text. No numbers were read off the curves.
- The passive-roller and hood conclusions in §7–§8 are this note's inferences from the model's structure, not statements from the paper.
