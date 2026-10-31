# steyn2025 — Steyn et al., "Executing a Successful Third Shot Drop in Pickleball"

## Citation
- Steyn, D. G., Mithrush, T., Koentges, C., Andrews, S., Plourde, A. *Executing a successful third shot drop in pickleball.*
  - Journal version: *International Journal of Sports Science & Coaching* **21**(3):1929–1935, published online 2025-08-12, https://doi.org/10.1177/17479541251365200. It is CC BY 4.0 open access. The volume, issue, pages, date and licence come from Crossref metadata.
  - Preprint: arXiv:2501.00163v1 (submitted 2024-12-30; physics.soc-ph, cross-listed to physics.flu-dyn). CC BY-NC-SA 4.0. https://arxiv.org/abs/2501.00163. A SportRxiv copy dated 2025-01-02 also exists.
- Affiliations: UBC Earth, Ocean & Atmospheric Sciences (Steyn), Jericho Hill Pickleball School (all authors), and Carleton Economics (Plourde). The study was self-funded.

## Access level and review status
- **I read the full text of the arXiv v1 preprint.** I worked from the author TeX source (`main.tex`), the bibliography and all four figure images in the arXiv source tarball, so every equation and number below is quoted from the source.
- **I could not read the journal version (VoR).** The SAGE page returned HTTP 403. A direct PDF fetch was blocked by this environment's bot-check policy, and I did not try to get around that block. The Crossref abstract of the VoR has the same wording and numbers as the arXiv abstract. **I have not checked whether peer review changed the equations, coefficients or figures.** Any corrections in the VoR, especially to the sign and Cl issues in the "Internal inconsistencies" section below, are unknown.
- **Review status: mixed.** The journal version is peer-reviewed. The content I read is the unreviewed preprint.

## What the paper is
This is a coaching-oriented study. It uses a 2D point-mass trajectory model with constant Cd and lift Cl = f(S). The authors calibrated it by **single-camera video of six real shots with a 40-hole Selkirk outdoor pickleball**. They then ran the model in "exploratory mode" to map the speed/angle/spin combinations that land a third-shot drop in the kitchen.

The original experimental content is small: **6 filmed trajectories**, which give **Cd = 0.30 ± 0.02** and **Cl = 0.195 S**. Everything else in the paper is model output.

## Method (experimental)
- **Ball:** 40-hole Selkirk outdoor pickleball. The model uses mid-range official ball properties: diameter (0.0730 + 0.0755)/2 = 0.07425 m and mass (0.0221 + 0.0265)/2 = 0.0243 kg.
- **Camera set-up:** one camera at net height. Each ball was hit directly above a court sideline so that its ground projection was known.
  - Vertical scale came from the net height. Horizontal scale came from the baseline, net and kitchen lines.
  - The x coordinate was recovered with "Menelaus' projection theorem".
- **Frame rate:** one frame every 0.008 s (125 fps). Every 10th frame was digitized, so points are about 0.08 s apart and each trajectory has about 12–20 points.
- **Initial conditions:**
  - Initial speed and angle came from the first two digitized points. The model was initialized at the first digitized point, not at paddle contact.
  - Spin rate came from three orthogonal great circles drawn on the ball. Revolutions were counted over roughly every 5–10 frames.
- **Fit:** Cd and Cl were fitted per trajectory by minimizing the deviation between model and digitized points. The authors do not state the objective function or the optimizer.
- **Error statements:**
  - Position error is "not greater than twice the ball diameter". This is large: about 0.15 m on trajectories about 9 m long.
  - The authors argue that random errors average out over 10–20 points, so Cd and Cl errors "should be very small". There is no formal uncertainty propagation.
  - They say the error from the ball not flying exactly above the sideline is "extremely difficult to precisely quantify".
  - They attribute the large scatter in Cl to uncertainty in measured spin.
- **No wind tunnel, no CFD and no force measurement.** The authors themselves recommend wind-tunnel confirmation, and they say the dependence on hole count "remains open".

## Method (numerical)
- 2D (x horizontal, z vertical), point mass, spin axis horizontal and perpendicular to flight. There is no spin decay. Spin enters only through Cl(S), using the initial spin.
- **Explicit (forward) Euler** time stepping. **The time step is not stated.**
- The lift sign is set by the user: + for one spin sense and − for the other.
- The authors say the model is "essentially the same" as Emond et al. (2024), with a different numerical implementation.

## Equations (verbatim in meaning; symbols and units added)

**E1. Newton's 2nd law**

a = (F_drag + F_lift + F_gravity)/m

**E2. Force magnitudes as printed**

F_drag = Cd ρ_a A u² and F_lift = Cl ρ_a A u²

- Cd and Cl are dimensionless. ρ_a is air density [kg m⁻³]. A = πr² is frontal area [m²]. u is ball speed [m s⁻¹].
- **The ½ is missing in the printed force formula.** E3 and E4 do include it (ρA/2m), so the model effectively uses the standard ½ρCAu².

**E3. Vertical**

d²z/dt² = −(ρ_a A / 2m)(v_x² + v_z²)(Cd sinθ − Cl cosθ) − g

**E4. Horizontal (as printed)**

d²x/dt² = −(ρ_a A / 2m)(v_x² + v_z²)(Cd cosθ − Cl sinθ)

- θ is the instantaneous flight-path angle [rad], θ = atan2(v_z, v_x). v_x and v_z are velocity components [m s⁻¹]. The text mislabels them as "v_x and v_y". m is mass [kg] and g is 9.81 m s⁻².
- **Sign issue:** in E4 the lift contributes +Cl sinθ. For lift perpendicular to velocity with an upward z component (+Cl cosθ in E3), the x component should be **−Cl sinθ**, so the bracket should read (Cd cosθ **+** Cl sinθ).
  - As printed, the lift vector Cl(sinθ, cosθ) is not perpendicular to the velocity (cosθ, sinθ); their dot product is sin2θ.
  - This is either a typo or a real code error. My reproduction under "Internal inconsistencies" cannot tell which, because the two versions differ by only about 0.1 m in range for their shots.

**E5. Dimensional analysis (after Bearman & Harvey 1976)**

Cl, Cd = F(Re, S)

**E6. Reynolds number as printed**

Re = 2uρ_a/ν_a, with ρ_a = 1.29 kg m⁻³ and "ν_a = 1.78 kg m⁻¹ s⁻²"

- **This is printed wrongly:** the radius is missing and the viscosity units and magnitude are wrong. The intended form is Re = 2 r u ρ_a / μ_a with μ_a = 1.78×10⁻⁵ kg m⁻¹ s⁻¹.
- With the intended form, the quoted Re values check out: u = 12 m/s gives 6.46×10⁴ and u = 10 m/s gives 5.38×10⁴, which match the captions.

**E7. Spin parameter**

S = 2π r n / u

- n is the spin rate in **revolutions per second** (written "s⁻¹" in the paper). r is the ball radius [m] and u is speed [m s⁻¹].
- This is the same S = ωR/v used in PM-001, with ω = 2πn.
- Check: n = 10 rev/s, u = 12 m/s and r = 0.0371 m give S = 0.194, which matches the caption's "0.19".

**E8. Fitted drag**

Cd = 0.30 ± 0.02. It is constant: there was "no systematic dependence on S and Re" over the measured range.

**E9. Fitted lift**

Cl = 0.195 S. This is a linear fit forced through the origin, with "large scatter". The authors say it is "roughly the same linear dependence" as in Fig. 3 of Cross & Lindsey (2017).

## Numeric data points

"Fig." numbers follow arXiv v1: Fig. 1 = modelled_shots, Fig. 2 = Angle_spd, Fig. 3 = Angle_spd3, Fig. 4 = Mod_Meas. Values marked *(read from figure)* were digitized by eye from the arXiv figure images and are good to about ±0.05–0.1 m or ±0.1 m/s.

| # | Quantity | Value | Conditions | Where |
|---|---|---|---|---|
| 1 | Measured trajectories | 6 | 40-hole Selkirk outdoor ball; single camera at 125 fps; every 10th frame used | App. A.2 |
| 2 | Drag coefficient (measured fit) | **0.30 ± 0.02**, no trend with S or Re | 4.7×10⁴ < Re₀ < 6.1×10⁴; 0.03 < S < 0.3 | App. A.2, eq. Cd |
| 3 | Lift coefficient (measured fit) | **Cl = 0.195 S** (through origin, large scatter) | same ranges as row 2 | App. A.2, eq. Cl |
| 4 | Initial Re range (measured shots) | 4.7×10⁴ – 6.1×10⁴ | 6 shots | App. A.2 |
| 5 | S range (measured shots) | 0.03 – 0.3 | 6 shots | App. A.2 |
| 6 | Example measured shot: initial speed | 10.0 m/s | first digitized point at about (1.0 m, 1.2 m) *(read from figure)* | Fig. 4 caption |
| 7 | Example measured shot: initial angle | 31° | as row 6 | Fig. 4 caption |
| 8 | Example measured shot: spin | 5.9 rev/s (≈ 354 rpm, 37 rad/s); S = 0.14 | as row 6 | Fig. 4 caption |
| 9 | Example measured shot: Re | 5.4×10⁴ → 4.9×10⁴ during flight | as row 6 | Fig. 4 caption |
| 10 | Example measured shot: time of flight | 1.42 s | as row 6 | Fig. 4 caption |
| 11 | Example measured shot: apex / landing | apex ≈ 2.33 m at x ≈ 4.6 m; lands x ≈ 9.2 m *(read from figure)* | as row 6 | Fig. 4 |
| 12 | Position measurement error | ≤ 2 ball diameters (≈ 0.15 m) | per-frame digitization | App. A.2 |
| 13 | Ball diameter / mass (model) | 0.07425 m / 0.0243 kg (mid-range official) | official range 0.0730–0.0755 m, 0.0221–0.0265 kg | App. A |
| 14 | Air density / viscosity | 1.29 kg m⁻³ / 1.78×10⁻⁵ kg m⁻¹ s⁻¹ (printed with wrong magnitude and units) | — | App. A.2, E6 |
| 15 | Fig. 1 modelled shots: inputs | Cd = 0.30, u₀ = 12 m/s, θ₀ = 20°, z₀ = 0.75 m, n = 10 rev/s, S = 0.19, **Cl = ±0.12**, Re 5.3–6.4×10⁴ | model only | Fig. 1 caption |
| 16 | Fig. 1 landing x: backspin / none / topspin | ≈ 10.35 / 9.25 / 8.4 m *(read from figure)* | row 15 | Fig. 1 |
| 17 | Fig. 1 apex height: back / none / top | ≈ 1.68 / 1.55 / 1.44 m at x ≈ 4.8 / 4.1 / 3.6 m *(read from figure)* | row 15 | Fig. 1 |
| 18 | Minimum speed to clear the net from the baseline | ≈ 8.7 m/s | z₀ = 0.75 m, x₀ = 0, down-the-line | Sec. 1.3 bullets / Fig. 2 |
| 19 | Speed above which the ball always lands beyond the kitchen line | ≈ 13.5 m/s | same | Sec. 1.3 / Fig. 2 |
| 20 | Maximum angle that clears the net, ±10 rev/s spin | topspin 35°, backspin 33° (as stated) | same | Sec. 1.3 bullets |
| 21 | Fig. 2 speed at 45° to just land in the kitchen: back10 / zero / top10 | ≈ 8.65 / 8.85 / 9.1 m/s *(read from figure)* | same | Fig. 2 |
| 22 | Successful down-the-line 3rd-shot drop | u₀ 10.9–13 m/s, θ₀ 15.5–22.5° | lands in back ¼ of kitchen and barely clears the net; spin −10…+15 rev/s | Abstract, Sec. 1.3, Fig. 3 |
| 23 | Successful cross-court 3rd-shot drop | u₀ 13.3–16 m/s, θ₀ 12.5–18° | same | Abstract, Sec. 1.3, Fig. 3 |
| 24 | Spin effect expressed as an equivalent speed change | topspin 15 → backspin 10 rev/s ≈ the effect of Δu ≈ 0.8 m/s (down-the-line) or ≈ 1.0 m/s (cross-court) | model; drop-shot window | Sec. 1.3 bullet 3 |
| 25 | Plausible maximum player spin | up to 15 rev/s (900 rpm), citing Lindsey (2022), an **unreviewed web article**; authors assume 15 rev/s backspin is hard to achieve | — | Sec. 1.3 |
| 26 | Hole count | 26 (indoor) to 40 (outdoor) | — | Sec. 1 |

## Internal inconsistencies (checks I ran)
I wrote a re-implementation of E3/E4 with forward Euler (dt = 1e-4 s) using the paper's r, m and ρ: a scratch script (`steyn_check.py`, not kept in this repo). It produced these results:

1. **Fig. 1 uses |Cl| = 0.12, which does not follow from the paper's own Cl = 0.195 S.** At S = 0.19, E9 gives Cl = 0.037.
   - My model with |Cl| = 0.12 reproduces Fig. 1: landing 10.30 / 9.19 / 8.31 m, apex 1.66 / 1.53 / 1.42 m.
   - With the self-consistent Cl = 0.037, landing is 9.50 / 9.19 / 8.90 m. That is a spin effect of only about ±0.3 m, roughly 3× smaller than the figure suggests.
   - **So Fig. 1's "strong spin effect" overstates the paper's own fitted lift by a factor of about 3.** It is not stated whether Figs. 2 and 3 use E9 or a fixed Cl.
2. **Fig. 1's sign labels conflict with E3.** The caption says backspin is Cl = −0.12, but in E3 a positive Cl gives upward lift. The longer green "backspin" trajectory is the one with upward lift. The physics in the figure is right (backspin → longer and higher); the sign labels in the caption are inverted relative to the equations.
3. **The E4 lift sign is wrong as printed** (see the E4 notes). Fig. 1 differs between the printed and corrected versions by only about 0.15 m in range, so the figure cannot settle which version was coded.
4. **The Fig. 4 caption parameters do not exactly reproduce the plotted fit.** With u₀ = 10 m/s, 31°, start at (1.0, 1.2) m, Cd = 0.30 and Cl = 0.027, my run gives apex 2.45 m and landing x ≈ 9.9 m with a flight time of 1.23 s. The plot shows apex ≈ 2.33 m and landing ≈ 9.2 m.
   - u₀ ≈ 9.4 m/s, or Cd ≈ 0.5–0.6 at 10 m/s, would match the plot.
   - The stated 1.42 s flight time also does not fit the roughly 14 plotted points at 0.08 s spacing, which span about 1.04 s.
   - My start point and landing were read by eye, so treat this as a warning sign, not proof of an error.
5. **Smaller errors:**
   - Appendix: "Emond assumed Cd = 0.0" conflicts with the introduction's (correct) Cd = 0.6.
   - Appendix: "Re will be in the range 5×10⁴ to 5×10⁵", but the measured shots only reach 6.1×10⁴.
   - The text says "v_y" where it means v_z.

## Applicability to POLLEN
- **What transfers:**
  - The geometry is close. POLLEN is 71 mm and about 25 g; the pickleball is 74 mm and 24.3 g.
  - The ballistic factor ρA/(2m) is similar: 0.115 m⁻¹ for the paper's ball against about 0.097 m⁻¹ for POLLEN (ρ = 1.225, R = 35.5 mm, m = 25 g).
  - The 2D model form, the definitions of S and Re, and the camera-fit method are all reusable for POLLEN calibration.
  - Cd = 0.30 ± 0.02 is a **measured value for a perforated plastic ball of almost the same size**. It is a reasonable prior, but it is not a POLLEN value.
- **What does not transfer, or only weakly:**
  1. **Reynolds number.** POLLEN at 2–10 m/s has Re ≈ 1.0×10⁴ – 4.8×10⁴, using Re = ρvD/μ = 1.225·v·0.071/1.81e-5 ≈ 4.8×10³·v. The paper's data cover only 4.7–6.1×10⁴, which overlaps only the top of the POLLEN range (about 10 m/s). Nothing below Re ≈ 4.7×10⁴ was measured, and that is where the authors themselves expect internal or secondary flows through the holes to matter.
  2. **Spin parameter.** The paper's data cover S = 0.03–0.3. A single 98 mm flywheel with a hood ideally gives S ≈ 1 at exit (HANDOFF §4C), and S rises further near the apex as speed drops. **Cl = 0.195 S is fitted only for S ≤ 0.3.** Extrapolating it linearly to S ≈ 1–2 (Cl ≈ 0.2–0.4) is not supported by this paper. Smooth-ball and tennis data generally show Cl saturating at high S, but that comes from other sources and is not checked here.
  3. **Holes.** POLLEN (Gopher ResisDent polyethylene) has a different hole count, hole size and pattern, and possibly a different shell roughness. The authors say the dependence on hole count is open.
  4. **Spin magnitudes.** The paper's spins are 5.9–15 rev/s (350–900 rpm). A flywheel shooter at v ≈ 6 m/s with S ≈ 1 gives ω ≈ 169 rad/s ≈ 1600 rpm, about 2–4.5× higher than anything this paper measured or modelled.
  5. **Spin decay** is not modelled, so the paper gives nothing on whether spin is still high at the apex.
  6. **Trajectory regime.** Their shots are fast and flat (12 m/s, 20°, about 1 s of flight). The POLLEN HIVE shot is a slower, high lob. Their "spin is secondary" conclusion is specific to a drop shot with a landing window about 0.5 m long. It should **not** be quoted as evidence for or against the POLLEN concept. The relative Magnus effect scales with Cl(S)·k·v²/g and must be recomputed for the POLLEN regime.
- **Scale comparison:**
  - Their Fig. 1 lift acceleration at Cl = 0.12 and 12 m/s is about 2.0 m/s² (0.2 g). With their own E9 (Cl = 0.037) it is about 0.6 m/s².
  - For POLLEN at 6 m/s with Cl = 0.2 it is about 0.70 m/s² (0.07 g), and at 4 m/s about 0.31 m/s².
  - Over a 2–3 m lob, the absolute deflection will be modest. In their own self-consistent model, a spin of S ≈ 0.19 moved the landing point by about ±0.3 m over roughly 9 m.

## Implications for the PM-001 models
1. **Aero priors:**
   - Use Cd = 0.30 (±0.02 as reported) as one bracket of the POLLEN drag sensitivity range, labelled "40-hole pickleball, Re 4.7–6.1×10⁴, video fit, preprint".
   - Bracket it on the high side with the wiffle-ball Cd ≈ 0.6 used by Emond et al. (2024).
   - Do not treat 0.30 as valid below Re ≈ 4.7×10⁴.
2. **Lift prior:**
   - Treat Cl = 0.195 S as a low-S slope prior only (S ≤ 0.3).
   - For S > 0.3, use a saturating parametric Cl(S) with an explicit ceiling, as the HANDOFF requires, plus a sensitivity sweep. Flag any result that depends on Cl at S > 0.3 as "extrapolated beyond steyn2025 data".
   - The HANDOFF scale check uses Cl = 0.20 at S ≈ 1. That equals E9 extrapolated to S ≈ 1, which is *not* measured.
3. **Do not copy E4's sign.**
   - Implement lift as F_M ∝ unit(ω × v_rel) (HANDOFF §4A).
   - Unit-test that backspin gives upward lift on a horizontal ball, rearward lift during ascent and forward lift during descent.
   - Add a regression test that F_lift · v = 0.
4. **Define spin units carefully:** n in rev/s against ω in rad/s. Steyn's "s⁻¹" means rev/s, so S = 2πrn/u.
5. **Numerics:** the paper's explicit Euler with an unstated time step is not adequate as a reference. Use RK45/RK4 with an event-located apex and HIVE-plane crossing. The Fig. 1 reproduction (landing about 10.3 / 9.19 / 8.3 m) can serve as a cross-check test case: Cd 0.30, ρ 1.29, r 0.037125 m, m 0.0243 kg, 12 m/s, 20°, z₀ 0.75 m, Cl = +0.12 / 0 / −0.12.
6. **Calibration protocol to reuse for real POLLEN shots from the prototype:**
   - Single camera with the trajectory over a known line and a reference height, at ≥125 fps.
   - Painted orthogonal great circles for spin.
   - Fit Cd and Cl per shot.
   - Improve on the paper by:
     - using every frame, not every 10th;
     - adding a second camera or a perpendicular view to check out-of-plane error;
     - propagating uncertainty (bootstrap over points);
     - fitting spin decay;
     - covering S up to about 1.5 and Re down to about 1×10⁴.
7. **Do not cite "spin is of secondary importance" for PM-001.** It is a conclusion for an S ≤ 0.3 drop-shot window. The PM-001 question has S ≈ 1, a lower speed, a high arc and an entry-corridor criterion, so it must be evaluated with the coupled model.

## Caveats
- I read only the arXiv v1 preprint. The peer-reviewed version (IJSSC 2025) may differ.
- The experimental base is 6 shots with one ball type, one camera and no stated uncertainty propagation. The Cl fit has large scatter and is forced through the origin.
- Figure-read values are by eye.
- My reproduction checks are my own numerical work, not results from the source.
