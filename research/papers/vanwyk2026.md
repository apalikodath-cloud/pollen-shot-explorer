# vanwyk2026 — Characterization of Pickleball Ball Mechanical Behaviour

## Citation
Collin Van Wyk, Lloyd Smith, Bin Lyu (Washington State University). "Characterization of Pickleball Ball Mechanical Behaviour." ISEA 2026 – The Engineering of Sport 16, Washington State University, Pullman WA, USA, 1–4 June 2026. Washington State University Research Exchange, record dated 2026-05-22. DOI: https://doi.org/10.7273/000008181

- Landing page: https://rex.libraries.wsu.edu/esploro/outputs/conferenceProceeding/99901374808601842
- PDF used: https://rex.libraries.wsu.edu/view/pdfCoverPage?instCode=01ALLIANCE_WSU&filePid=13462260490001842&download=true

## Access level
**Full text.** I read the whole 5-page PDF (4 pages of text and figures plus 1 page of references). It is a short extended abstract. It has 5 figures, 1 equation and no tables. Numbers marked "digitized" below were read by eye from the plotted figures. They are approximate (about ±5 lb or ±0.01 in on Fig. 4, about ±0.005 on Fig. 5) and do not appear as numbers in the text.

## Review status
**Conference paper (ISEA 2026 extended abstract).** The document does not say how it was reviewed. It is not a full archival journal paper, so treat it as a conference / lightly reviewed source. **Funding:** Selkirk Sport, a pickleball equipment manufacturer, acknowledged on p.4. **Ball identity:** the paper says only "an approved Pickleball [3]" and, in Fig. 5, "an outdoor Pickleball". It gives no brand, model or material.

## Method (as stated)
1. **Rigid-plate impact test (Fig. 1)**, following ASTM F2845-22 (the dynamic stiffness / CCOR method for baseballs and softballs, ref [2]):
   - A cannon fires the ball at **60 mph ± 1 mph (26.8 ± 0.45 m/s)**.
   - Two light gates measure the inbound speed.
   - The ball hits a flat steel plate mounted on a rigid wall through a load-cell array (**three 500 lb load cells**).
   - Further light gates measure the rebound speed and angle.
2. **Sample:** 12 balls. Each ball was struck at 4 locations along the seam/centerline, 90° apart, with 3 "good shots" per location, giving 12 good shots per ball and **n = 144** impacts. A shot counted as "good" if the rebound angle was within ±10° of the inbound path, both horizontally and vertically.
3. **Force–displacement curve:** the wall force divided by ball mass gives acceleration. Integrating that twice gives displacement. The result is centre-of-mass displacement under the dynamic impact, not a quasi-static compression test.
4. **High-speed imaging (Fig. 3)** of the deformation and the recovery of the spherical shape.
5. **Aerodynamics (Fig. 5):** "methods described in" Lyu, Smith, Elliott & Kensrud (2025), *Proc IMechE Part P* 239(2):235–241. This paper does not describe the method. Backspin was **2250 ± 250 rpm** at speeds of 35–65 mph.

## Equations
1. **Eq. (1), from the paper:** energy dissipated in a rigid-plate impact

   `de = 1 − COR²`

   - `de`: fraction of the incoming translational kinetic energy that is dissipated (dimensionless)
   - `COR = v_out / v_in` (dimensionless)
   - With COR ≈ 0.2, de ≈ 0.96. The paper states "pickleballs lose about 96% of their energy".

2. **Acceleration and displacement, described in words in the paper (not numbered):**

   `a(t) = F(t)/m`, `x(t) = ∫∫ a dt dt`

   - `F`: wall force [N]
   - `m`: ball mass [kg]
   - `x`: displacement [m]

3. **Dynamic stiffness DS.** The paper does not give the formula. It cites ASTM F2845. The ASTM linear-spring definition is believed to be `DS = (1/m)·(F_peak / v_in)²` [N/m]. That formula is **from memory, unverified** and does not come from this paper. Below I check it for consistency only.

No other equations appear. The paper gives no N(δ) law, no Hertz or shell model, no COR(v) law, no temperature model and no Cd(Re) or Cl(S) formula.

## Data points (source_id = vanwyk2026)

| # | Quantity | Value | Conditions | Where |
|---|---|---|---|---|
| 1 | Impact speed | 60 mph ± 1 mph (26.8 m/s) | rigid steel plate, normal impact | p.1 Methods |
| 2 | Sample size | 12 balls × 12 good shots = 144 | 4 seam/centerline sites, 3 shots each | p.1; Fig. 2 caption |
| 3 | Hole count (outdoor ball) | 40 | USA Pickleball standard, cited [3] | p.2 Results |
| 4 | Diameter | 2.87–2.97 in (72.9–75.4 mm) | spec range [3] | p.2 |
| 5 | Mass | 0.78–0.935 oz (22.1–26.5 g) | spec range [3] | p.2 |
| 6 | COR (mean) | ≈ 0.20 | 60 mph, rigid plate, n = 144 | p.2 text; Fig. 2 top |
| 7 | COR range (histogram) | ≈ 0.165–0.255 (digitized); mode bin 0.200 (25 counts) | same | Fig. 2 top |
| 8 | COR CoV, within one ball | 7.5% (baseball 1.2%) | same | p.2 |
| 9 | COR CoV, between balls | 3.6% (12-ball supply; baseball 0.6%, 9-ball supply) | same | p.2 |
| 10 | Comparison COR | baseball ≈ 0.5, tennis ≈ 0.75 | cited [5] | p.2 |
| 11 | Dynamic stiffness (mean) | 500 lb/in (87.6 kN/m) | 60 mph, ASTM F2845-style | p.2; Fig. 2 bottom |
| 12 | DS range (histogram) | ≈ 225–775 lb/in (39–136 kN/m), digitized; bulk 375–675 lb/in | same | Fig. 2 bottom |
| 13 | DS CoV, within one ball | 18% (baseball < 2%) | same | p.2 |
| 14 | DS CoV, between balls | 5.3% (baseball 8.0%) | same | p.2 |
| 15 | Maximum deformation | ≈ 0.4 in (10 mm), "~1/4 of its radius" | 60 mph impact | p.3 text; Fig. 3, Fig. 4 |
| 16 | Shape recovery time | ≈ 3 ms after impact; ball leaves visibly flattened | 60 mph | p.3; Fig. 3 |
| 17 | Contact duration | ≈ 1.5 ms | 60 mph | p.3 |
| 18 | Fatigue / repeat-impact drift | "little evidence of change after 200 impacts" in COR / temporal response | 60 mph, repeated | p.3 |
| 19 | Temperature effect | Qualitative only: "did not show evidence of warming effects when impacted repeatedly, without a rest period." No temperatures measured or reported. | repeated 60 mph impacts | p.3 |
| 20 | Peak force (one shot) | ≈ 335 lbf (1490 N) at x ≈ 0.40 in (digitized) | 60 mph, one example impact | Fig. 4 |
| 21 | F–x loading branch (digitized, in → lbf) | 0→0; 0.025→30; 0.05→88; 0.075→115; 0.10→135; 0.125→147; 0.15→148 (plateau); 0.175→160; 0.20→185; 0.225→205; 0.25→218; 0.275→225; 0.30→262; 0.325→300; 0.35→318; 0.375→310; 0.40→335; max x ≈ 0.415 | same shot; COM displacement from double integration | Fig. 4 |
| 22 | F–x unloading branch (digitized) | drops almost vertically from ≈ 0.415 in to < 75 lbf, then oscillates 0–65 lbf, reaching F = 0 at x ≈ 0.20 in (residual set ≈ 0.2 in at separation) | same | Fig. 4 |
| 23 | Hysteresis | "large hysteresis … significant energy dissipation, low COR … may contribute to low repeatability" | same | p.3 |
| 24 | Cd vs speed | ≈ 0.40–0.41 at every speed (digitized: 35→0.403, 40→0.409, 45→0.408, 50→0.409, 55→0.404, 60→0.408, 65→0.408 mph); text gives "0.4, relatively constant" | outdoor ball, backspin 2250 ± 250 rpm, 35–65 mph | p.3 text; Fig. 5 |
| 25 | Cl vs speed (digitized mean, [error-bar range]) | 35 mph: 0.278 [~0.185–0.37]; 40: 0.23 [0.15–0.31]; 45: 0.227 [0.16–0.295]; 55: 0.16 [0.095–0.228]; 60: 0.17 [0.112–0.232]; 65: 0.158 [0.075–0.242]; no lift point at 50 mph; dotted trend ≈ 0.262 (35 mph) → 0.147 (65 mph) | same | Fig. 5 |
| 26 | Comparison Cd | tennis / wiffle 0.6, baseball 0.3 | cited [6] Rossmann & Rau | p.3 |
| 27 | Comparison Cl | wiffle 0.35, tennis 0.3, baseball 0.25 | cited [6] | p.3–4 |
| 28 | Mass ratios | pickleball ≈ 20% of baseball, ≈ 50% of tennis, ≈ 125% of wiffle | text | p.4 |
| 29 | Carry sensitivity to Cl (model result) | 40 mph, 5° launch, 2000 rpm backspin: mean Cl, Cd → 28 ft (8.5 m) carry; Cl at the Fig. 5 upper bound → 35 ft (10.7 m). Launch height not stated. | trajectory simulation, not measured | p.4 Discussion |
| 30 | Flight times | 40 mph: 0.26 s over 14 ft; 1 s over 44 ft | stated in text | p.4 |

### Derived by this agent (not in the paper; for cross-checks)

Constants used: 1 lbf = 4.448 N, 1 in = 25.4 mm, m = 25.5 g (spec midpoint), R = 37.1 mm (2.92 in), ρ = 1.2 kg/m³, μ = 1.81e-5 Pa·s.

| Quantity | Value | Basis |
|---|---|---|
| Spin parameter S = ωR/v at 2250 rpm | 35 mph 0.56; 40: 0.49; 45: 0.43; 50: 0.39; 55: 0.36; 60: 0.33; 65: 0.30 (±11% from the ±250 rpm spread) | conversion |
| Reynolds number Re = ρvD/μ, Fig. 5 range | 7.7e4 (35 mph) to 1.43e5 (65 mph) | conversion |
| Fit of Fig. 5 Cl against S | Cl ≈ 0.011 + 0.47·S (least squares over 6 points); through the origin, Cl ≈ 0.49·S; valid only for S ≈ 0.30–0.56 | my fit |
| Kinetic energy at 60 mph | 9.2 J (25.5 g) | ½mv² |
| Area under digitized loading branch | ≈ 9.0 J | trapezoid on row 21; agrees with KE to within ~2%, so the digitization is self-consistent |
| Area under digitized unloading branch | ≈ 1.0 J, giving e_equiv = √(1.0/9.0) ≈ 0.33 | coarse, because the unloading branch is noisy; the paper's COR 0.2 implies ≈ 0.37 J returned |
| Linear spring with k = DS = 87.6 kN/m at 26.8 m/s | F_pk = v√(km) ≈ 1270 N (285 lbf); x_max = v√(m/k) ≈ 14.5 mm; contact time π√(m/k) ≈ 1.7 ms | linear-spring check; measured values are 1490 N, 10 mm and 1.5 ms |
| DS implied by the Fig. 4 shot (F_pk 335 lbf), using the ASTM formula (unverified) | ≈ 121 kN/m (690 lb/in) | within the Fig. 2 histogram tail; a stiffer-than-mean shot |
| Secant stiffness F/x along the loading branch | 0.025 in: 210 kN/m; 0.075 in: 270 kN/m; 0.125 in: 206 kN/m; 0.175 in: 160 kN/m; 0.275 in: 143 kN/m; 0.375 in: 145 kN/m | digitized |
| Power-law fit of the loading branch, 1.3–10 mm | F ≈ 2.59e4 · δ^0.64 (F in N, δ in m) | log-log least squares |
| **F at δ = 4 mm (0.157 in)** | linear DS: **350 N** (287–413 N with the ±18% shot CoV); Fig. 4 interpolation: **≈ 670 N**; power law: ≈ 760 N | dynamic 60 mph pickleball values |
| Magnus area-to-mass ratio A/m | pickleball 0.177 m²/kg; POLLEN 0.158 m²/kg | similar aerodynamic sensitivity |

## Applicability to POLLEN

**What transfers, qualitatively:**
- **Same class of object.** Both are hollow, perforated, thin-shell plastic balls of similar size (72.9–75.4 mm vs 71 mm) and mass (22–26.5 g vs ~25 g). A/m is within about 11%.
- **Low COR and large hysteresis (e ≈ 0.2 at 27 m/s).** These are probably generic to perforated thin plastic shells: the holes and thin wall allow local shell buckling and flattening. A residual flattening that recovers over about 3 ms is plausible for POLLEN too.
- **Shell-type F–δ behaviour.** The loading curve is not Hertzian (the fitted exponent is about 0.64, not 1.5). It looks roughly linear at small δ and then has a plateau (snap-through or buckling) near 2.5–3.8 mm. That plateau falls exactly around the 4 mm working compression in the HANDOFF. If POLLEN behaves the same way, normal force near 4 mm would be insensitive to δ, which could make compression *more* repeatable, with hysteresis losses concentrated there. Caveat: in a dynamic double-integrated signal the plateau could also be load-cell or structural ringing, and the paper does not say which.
- **High scatter.** Within-ball DS CoV is 18% and COR CoV is 7.5%, depending on impact site relative to the seam and holes. Expect POLLEN, which the manual describes as "not perfectly spherical", to show similar or larger orientation-dependent scatter in flywheel grip and in rim bounces. Budget for it in uncertainty bands.
- **Drag almost independent of speed.** Cd ≈ 0.40 across Re 7.7e4–1.4e5 at S 0.3–0.56. This supports a constant-Cd first pass. It is consistent in sign with Rossmann & Rau's ordering for perforated balls.
- **Lift rises with S.** The pickleball points scale roughly as Cl ≈ 0.47–0.49·S over S 0.30–0.56. That is a reasonable slope prior for POLLEN at moderate S.

**What does NOT transfer:**
- **Speed regime and stiffness.** The 60 mph (26.8 m/s) impact speed is 3–10× POLLEN shooter and rim speeds of 2–10 m/s. COR for balls generally rises at lower impact speed (general knowledge, not from this paper), so e ≈ 0.2 is probably a **lower bound** for POLLEN rim hits at a few m/s. The paper gives **no COR(v)**.
- **Stiffness values.** DS comes from high-rate impact. Polyethylene is rate-sensitive, so quasi-static or rolling-squeeze stiffness in a flywheel gap will be lower (direction from general polymer behaviour; magnitude unknown). POLLEN (Gopher ResisDent PE) material, wall thickness and hole pattern are unknown and may differ a lot from a tournament outdoor pickleball. **Do not use 87.6 kN/m or the Fig. 4 curve as POLLEN's N(δ).**
- **Aerodynamic range.** The data cover Re 7.7e4–1.4e5 and S 0.30–0.56. POLLEN flies at Re about 9.4e3–4.7e4 (2–10 m/s) and S up to about 2. That is roughly a factor of 2–8 lower in Re and up to about 4× higher in S. Extrapolating Cl ≈ 0.48·S to S = 1–2 is **not supported**; Cl normally saturates. Hole count and pattern also differ: pickleball 40 holes, POLLEN unknown.
- **Temperature.** Only "no warming observed" under rapid repeated impacts. There is no temperature-dependent data at all, so a temperature model cannot be derived from this source.
- **COR test conditions.** Normal impact only, on a rigid steel plate. There is no oblique, friction or spin-change data, so it gives nothing for μ or for the tangential coefficient at the HIVE rim.

## Implications for the PM-001 models

1. **Launcher N(δ) law (4C/4D).**
   - This paper gives no quasi-static law. Implement N(δ) as a pluggable function with three bracketing cases:
     - (a) linear `N = k·δ` with `k` as a POLLEN measured parameter;
     - (b) piecewise linear-then-plateau (shell buckling), following the Fig. 4 shape;
     - (c) the dynamic pickleball upper bound: N(4 mm) ≈ 350 N (from DS) to ≈ 670 N (from Fig. 4), labelled "pickleball, 60 mph impact, upper bound, not POLLEN".
   - Those upper-bound forces are large. With μ ≈ 0.5 they imply 175–335 N of available traction, far more than the ball needs. In practice spin transfer will probably be limited by slip kinematics and wheel inertia, not by N, unless POLLEN is far softer.
   - **Required measurement:** a quasi-static compression test on 5–10 POLLEN balls, pressing between flat plates to 2, 4 and 6 mm at several orientations relative to the holes, with a kitchen scale or force gauge and calipers. Repeat at a faster rate if possible. Record the loading and unloading curves to get k and hysteresis.

2. **Hysteresis and rolling loss in the launcher.**
   - The paper shows only about 4–11% elastic energy return in a full compression cycle at high rate (e² = 0.04 from COR; ≈ 0.11 from my digitization).
   - In a hood shooter the ball rolls through a compressed gap, so the hysteresis acts as rolling resistance. That opposes ball rotation and translation and drains flywheel energy.
   - Model it as a rolling-resistance torque `M_rr = N·a_h`. Here `a_h` is the eccentricity of the hysteretic pressure centre, a fitted parameter, or the product of a loss factor and the contact half-width.
   - Expect exit speed and spin below the ideal kinematics. Fit against high-speed video.

3. **Shape recovery.** The ball exits flattened and needs about 3 ms to recover; at 10 m/s that is about 3 cm of flight. This is negligible for aerodynamics but relevant to the effective rolling radius at exit (ω_ball·R_eff ≠ ω_ball·R). Keep R_eff as an uncertain parameter, about 0.9–1.0 R.

4. **Collision model (4E).**
   - Use a spring-dashpot normal contact with damping ratio set by e. For e = 0.2: ζ = −ln e / √(π² + ln² e) ≈ 0.456. That is standard linear-dashpot theory, not from this paper.
   - Treat e as speed-dependent and uncertain: e ∈ [0.2, ~0.5] for 2–10 m/s until POLLEN drop tests exist. The 0.5 upper value is a placeholder, not from any source. Run the sensitivity at both ends.
   - Very low e means rim hits kill most of the normal velocity, which favours "drop-in after rim contact" scenarios. That makes the outcome more sensitive to friction and spin (tangential impulse) than to normal rebound.
   - Add ball-to-ball and orientation scatter: CoV(e) about 8% per impact.

5. **Aerodynamics (4A).**
   - Defaults: Cd_0 = 0.40 (pickleball, flagged), with a sensitivity band of 0.35–0.6 because of the Re shift and Rossmann & Rau's wiffle value.
   - Cl(S) prior: slope about 0.47 per unit S for S ≤ 0.6. Above that, add a ceiling (e.g. Cl_max 0.3–0.4, the wiffle value cited at 0.35) instead of extrapolating linearly.
   - The authors' own trajectory example shows carry changing by **25% (28 → 35 ft)** across the Cl error band. Cl uncertainty must therefore be a first-class axis in the feasibility maps. This supports the HANDOFF instruction to label pickleball coefficients uncalibrated.

6. **Repeatability budget.** For the robustness study (question 6), propagate per-shot scatter in contact stiffness (pickleball CoV 18% in DS) and COR (7.5%) as at least the minimum POLLEN variability, until measured.

## Gaps in this source vs the questions asked
- **Force–compression curve:** dynamic only, one shot, 60 mph. No quasi-static curve.
- **Stiffness:** a mean and distribution only (DS).
- **COR vs speed:** NOT reported; only 60 mph.
- **Hysteresis:** shown qualitatively in Fig. 4 for one shot. No loss factor is given.
- **Temperature:** NOT measured; a single qualitative "no warming" statement.
- **N(δ) for 4 mm:** NOT given. The values above are my digitization and conversions of high-rate pickleball data.
