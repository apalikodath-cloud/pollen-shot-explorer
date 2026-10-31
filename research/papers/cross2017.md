# Cross & Lindsey (2017): Measurements of drag and lift on smooth balls in flight

source_id: `cross2017` (target paper). Companion source used for method and smooth-ball numbers: `cross2012ajp` (see §3).
Read: 2026-10-30, research agent for PM-001.

## 1. Citation, access, review status

| Field | Value |
|---|---|
| Citation | R. Cross and C. Lindsey, "Measurements of drag and lift on smooth balls in flight", *European Journal of Physics* **38**(4), 044002 (2017). DOI 10.1088/1361-6404/aa6e44 |
| Dates | Received 1 Mar 2017, revised 28 Mar 2017, accepted 20 Apr 2017, published 12 May 2017 (IOPscience landing page) |
| Affiliations | Cross: Univ. of Sydney (physics). Lindsey: Tennis Warehouse University, San Luis Obispo CA |
| Review status | Peer-reviewed journal (EJP, IOP Publishing). It is an education-physics journal, so the methods are made to be repeatable but the data sets are small. |
| Access | **Abstract only.** Unpaywall and Semantic Scholar list the publisher PDF as "bronze" OA, but on 2026-10-30 the IOPscience PDF URL returned the login/purchase page. ResearchGate returned 403. The author's site (physics.usyd.edu.au/~cross/PUBLICATIONS) stops at 2012 and has no copy. A direct download with curl was blocked in this session. |
| Consequence | No figure, table or equation of the 2017 paper was seen. **No Cd/Cl numbers from the 2017 paper are reported here.** I did not fill any in from memory. |

URLs tried: https://doi.org/10.1088/1361-6404/aa6e44, https://iopscience.iop.org/article/10.1088/1361-6404/aa6e44, .../pdf, https://api.unpaywall.org/v2/10.1088/1361-6404/aa6e44, api.semanticscholar.org (DOI record), https://www.researchgate.net/publication/316287031, https://www.physics.usyd.edu.au/~cross/PUBLICATIONS/ (index), physics.usyd.edu.au/~cross/AERODYNAMICS.htm and TRAJECTORIES/Trajectories.html.

**Action for the lead:** someone with library access, or a browser that can reach the bronze-OA PDF, should get the full text. Then fill in the "TBD" rows in §4 from Figs/Tables, especially Cl(S) for the three balls and their diameters and masses.

## 2. What the 2017 paper reports (from the abstract only, paraphrased)

- Drag and lift coefficients were measured for **three relatively smooth balls** launched in air.
- Method: the trajectory was filmed by **two cameras separated horizontally by 6.4 m**. Cd and Cl come from how the ball's speed and height change between the two camera stations.
- Spin was varied to find whether the Magnus force rises or falls with spin.
- Ball A: Magnus force **increased** with spin.
- Ball B: Magnus force **rose to a maximum, then fell almost to zero** as spin rose further.
- Ball C: Magnus force was **negative at low spin and positive at high spin** (reverse Magnus at low S).
- For one ball, **the spin increased during flight**.
- A ResearchGate figure listing, seen only as a search-engine snippet, shows Fig. 2 as an overview of typical Cl values for spinning balls. In that overview, rough balls have Cl rising monotonically with spin. Search-engine summaries also say the paper cites Taneda and Aoki et al. for the Magnus reversal on smooth spheres. These two points are **secondary and unverified**.

Not available (TBD): ball identities, diameters, masses, speed range, spin range, Re range, Cd values, Cl(S) curves, uncertainty bars, frame rates.

**Likely rig (inference, not from the 2017 text):** Cross & Lindsey's tennis-ball trajectory study on TWU (twu.tennis-warehouse.com/learning_center/aerodynamics2.php) used the same 6.4 m two-camera layout:
- camera 1 about 0.5 m in front of the launcher and camera 2 about 6.4 m downrange, both 300 fps with a 150 mm zoom, plus a third camera for out-of-plane motion;
- speed and height measured at each station, and Cd and Cl taken from the changes between them;
- depth/scale correction from a 60 cm board filmed at several depths, with a 2nd-order polynomial fit of apparent length against depth;
- the ball centre digitised independently by both authors and the results averaged.

The 2017 smooth-ball study very probably reused this rig. Treat that as plausible, not confirmed.

## 3. Companion source with full text: Cross (2012), the same group's method and smooth-ball data

R. Cross, "Aerodynamics in the classroom and at the ball park", *Am. J. Phys.* **80**(4), 289–297 (2012), DOI 10.1119/1.3680609. Peer-reviewed. **Full text read** (author copy: https://www.physics.usyd.edu.au/~cross/PUBLICATIONS/58.%20Aerodynamics%20AJP.pdf). source_id `cross2012ajp`.

This paper is a direct forerunner of the 2017 paper:
- it uses light, smooth, large balls with backspin;
- it measures Cd and Cl by filming the trajectory;
- it observed **negative Magnus on a smooth ball**.

It is the best available stand-in for the method and the smooth-ball bounds. Its numbers are **not** from the 2017 paper.

### 3.1 Method (cross2012ajp §III–IV)

- **Cameras:** Casio EX-F1 at 300 fps and Canon SX220HS at 120 fps, set at right angles. Camera A recorded the vertical x–z trajectory. Camera B recorded the horizontal launch angle, the spin and the target impact point.
- **Spin:** marks and lines drawn on the ball. Spin was measured to within 2% from rotation angle against time, or from the number of frames per fixed number of revolutions.
- **Launch:** by hand (low speed, low spin) or with a home-made lacrosse-type launcher (1.5 m long, 5 mm aluminium rod; arm about 70 cm). Spin and speed were **not** set separately: spin came out roughly proportional to launch speed. This is the same coupling as an ideal single-wheel shooter.
- **Data reduction (direct differentiation):**
  - Fit low-order polynomials to x(t) and z(t), then differentiate them to get v_x, v_z, a_x, a_z, with θ = atan(v_z/v_x) and g = 9.81 m/s².
  - Where the speed drop over the measured path was **< ~20%**, quadratic fits were used and gave path-averaged Cd and Cl.
  - Where the drop was > 20%, cubic or higher fits were used, so Cd and Cl could be resolved as functions of v within a single throw. One Fig. 6 throw used a 6th-order fit.
- **Stated limit:** this works only for light balls whose acceleration differs clearly from g. For heavy balls, small position errors make the inferred forces unreliable, and the alternative is to **fit numerically integrated trajectories** to the data (the paper's refs 13–14: Nathan 2008; Goff & Carré 2009).
- **Mass and buoyancy:** the true mass m equals the scale reading plus m_A, the mass of displaced air, because the scale reads m − m_A.
- **Below ~5 m/s:** for ball 1 the aerodynamic forces dropped below gravity and curve fitting stopped giving reliable Cd and Cl. Cd was then measured in a crude wind tunnel instead:
  - a fan in a 45 cm conical tube with an 18 cm exit, and an anemometer 10 cm beyond the exit;
  - the ball hung as a 1.1 m V-thread pendulum, with drag taken from the pendulum's deflection angle.
- **Side-force rig:** a vertical target 5 m from the launch point, made of 80 cm rubber mats with a 10 cm grid. Impact point measured to about 1 cm. Horizontal deflection was accurate only to about 9 cm, because a 1° error in launch angle moves the impact point 9 cm at 5 m.
- Data were taken outdoors only in still air; otherwise in a lecture theatre.

### 3.2 Equations (cross2012ajp Eqs. 1–5 and text)

Symbols:
- m: ball mass (kg); m_A: mass of displaced air (kg)
- a_x, a_z: horizontal and vertical acceleration (m/s²); g = 9.81 m/s²
- θ: velocity angle above horizontal (rad); v: speed (m/s)
- F_D, F_L: drag and lift (Magnus) force (N); F_B = m_A g: buoyancy (N)
- ρ: air density (kg/m³); A = πR² (m²); R: radius (m); d: diameter (m)
- ω: spin (rad/s); η: dynamic viscosity (Pa·s)
- C_D, C_L, C_S: drag, lift and side-force coefficients (dimensionless)

| # | Equation | Note |
|---|---|---|
| 1 | m a_x = −F_D cosθ − F_L sinθ | backspin, 2D x–z plane |
| 2 | m a_z = F_L cosθ − F_D sinθ − m g + m_A g | includes buoyancy |
| 3 | F_D = −[(m − m_A) g sinθ + m (a_x cosθ + a_z sinθ)] | inversion of Eqs. 1 and 2 |
| 4 | F_L = (m − m_A) g cosθ + m (a_z cosθ − a_x sinθ) | inversion of Eqs. 1 and 2 |
| 5 | F_D = ½ C_D ρ A v², F_L = ½ C_L ρ A v², F_S = ½ C_S ρ A v² | coefficient definitions |
| – | S = R ω / v | spin parameter (Fig. 7b axis) |
| – | Re = ρ v d / η = (6.7×10⁴ s/m²) v d | at η = 1.81×10⁻⁵ Pa·s (printed as "P" in the paper, a typo) and ρ = 1.21 kg/m³ |
| – | F_D = k vⁿ, best fit n = 1.73 (ball 1) | empirical; shows C_D is not constant |
| – | Δz = a_z (Δt)² / 2 | used to estimate the average a_z in the negative-Magnus throw |

Sign convention: F_L is perpendicular to v and points "up and back" for backspin when θ > 0. This matches the PM-001 convention n_M = unit(ω × v_rel) in HANDOFF §4A. A negative C_L means the force points opposite to the conventional Magnus direction.

### 3.3 Balls (cross2012ajp Table I)

| Ball | Type | Material | M (g) | D (mm) |
|---|---|---|---|---|
| 1 | smooth | polystyrene | 8.98 | 101 |
| 2 | smooth + circular string loop (1.5 mm string, offset b = 30 mm) | polystyrene | 12.15 | 98 |
| 3 | smooth + string baseball seam | polystyrene | 11.55 | 100 |
| 4 | smooth | hollow inflatable plastic (child's basketball) | 92 | 228 |

The polystyrene feels smooth, but its surface height varies locally by about 0.5 mm over about 10 mm (§VIII), so it is "slightly rough".

## 4. Data points

source_id `cross2017` rows are from the 2017 abstract only. `cross2012ajp` rows are from the companion paper and were read from text or figures. Values read off figures are approximate (±0.02 in coefficient, ±5% in speed).

| # | Quantity | Value | Conditions | Where | source_id |
|---|---|---|---|---|---|
| 1 | Camera separation | 6.4 m (horizontal) | two-camera in-flight method, 3 smooth balls | Abstract | cross2017 |
| 2 | Number of balls | 3 "relatively smooth" | — | Abstract | cross2017 |
| 3 | Magnus force against spin, ball A | increases monotonically | spin varied; speeds and Re TBD | Abstract | cross2017 |
| 4 | Magnus force against spin, ball B | rises to a maximum, then falls almost to 0 | as above | Abstract | cross2017 |
| 5 | Magnus force against spin, ball C | negative at low spin, positive at high spin | as above | Abstract | cross2017 |
| 6 | Spin during flight | increased for one ball | as above | Abstract | cross2017 |
| 7 | Cd, Cl numbers | TBD; full text not reached | — | Figs (not seen) | cross2017 |
| 8 | Launch speed and spin, ball 1 | 28 m/s, about 2000 rpm backspin | 101 mm, 9.0 g polystyrene, lacrosse launcher | Fig. 6a, §V | cross2012ajp |
| 9 | Peak climb, ball 1 | to z ≈ 4.2–4.3 m at x ≈ 9.5 m, t = 1.0 s, v = 3.5 m/s (launch z ≈ 2.0 m) | same throw | Fig. 6a | cross2012ajp |
| 10 | Initial accelerations, ball 1 | a_z ≈ +65 m/s², a_x ≈ −90 m/s² | start of launch at 28 m/s | §III | cross2012ajp |
| 11 | Drag power law, ball 1 | F_D = k vⁿ, n = 1.73; mg = 0.088 N | 5–28 m/s | Fig. 6b | cross2012ajp |
| 12 | Cd, ball 1 | about 0.24 at 28 m/s, rising to about 0.40 at about 7 m/s | 2000 rpm; Re ≈ 4.7×10⁴ to 1.9×10⁵ | Fig. 7a, §V, §VIII | cross2012ajp |
| 13 | Cl against v, ball 1 | about 0.30 at 7 m/s, peak about 0.33 at about 10 m/s, about 0.15 at 28 m/s | 2000 rpm | Fig. 7a | cross2012ajp |
| 14 | Cl against S, ball 1 | about 0.15 at S ≈ 0.37, rising to about 0.25 at S ≈ 0.5 and about 0.32 at S ≈ 0.8; plateau about 0.33 at S ≈ 0.9–1.1; about 0.30 at S ≈ 1.45 | same single throw | Fig. 7b | cross2012ajp |
| 15 | Generic Cl(S) statement | most balls: Cl rises from 0 to about 0.3 as S goes 0 → 0.4, then about constant at 0.3 for S > 0.4. Polystyrene ball 1: Cl keeps rising to about S = 1 | literature summary in the paper (refs 13, 14) plus ball 1 | §V | cross2012ajp |
| 16 | Lower validity of the trajectory fit | unreliable below about 5 m/s for ball 1 (forces < mg) | ball 1 | §V | cross2012ajp |
| 17 | Cd, non-spinning, wind tunnel | 0.55 ± 0.05 | 2.8 < v < 4.2 m/s, ball 1 (101 mm), Re ≈ 1.9×10⁴–2.8×10⁴ (computed) | §V | cross2012ajp |
| 18 | Smooth-sphere reference Cd | about 0.5 for subcritical Re; drops sharply near Re ≈ 3×10⁵ (smooth). A rough or tripped surface lowers the critical Re by 2–3× | literature | §IV, §VIII | cross2012ajp |
| 19 | Re for 100 mm ball | 1×10⁵ at 15 m/s; 228 mm ball: 1×10⁵ at 6.6 m/s | — | §IV | cross2012ajp |
| 20 | Spins, ball 4 | hand: ω ~ 100–200 rpm (low speed); launcher: ω ~ 350–600 rpm | 228 mm, 92 g | §V | cross2012ajp |
| 21 | Cl sign, ball 4 | **negative for about 9 < v < 14 m/s** with backspin | Re ≈ 1.4×10⁵–2.1×10⁵ | Fig. 9, §V, §VIII | cross2012ajp |
| 22 | Cl curve, ball 4 (dashed fit) | about +0.2 at 7 m/s → about −0.1 minimum at about 10.5–11 m/s → crosses 0 at about 14.5 m/s → about +0.1 at 17 m/s | spins: 100–200 rpm below about 9 m/s; 350–600 rpm above. Data scatter about ±0.1 | Fig. 9 | cross2012ajp |
| 23 | Cd curve, ball 4 | about 0.55 at 6.5 m/s → about 0.3 at 10 m/s → about 0.2 at 13 m/s → about 0.16 at 16–17 m/s (drag crisis) | as above; averages over the first 2 m of path | Fig. 9 | cross2012ajp |
| 24 | Example negative-Magnus throw | launch 10.8 m/s, 367 rpm backspin, Rω = 4.4 m/s, so S ≈ 0.44 at v = 10 m/s | ball 4 | Fig. 8, Fig. 12, §VIII | cross2012ajp |
| 25 | Coefficients in that throw | Cl from about −0.08 (8.8 m/s) to about −0.21 (11 m/s); Cd from about 0.40 to about 0.31 over the same range | n = 2 fit for x(t), n = 3 for z(t), 1/60 s points | Fig. 8b | cross2012ajp |
| 26 | Downward acceleration with backspin | a_z ≈ 12.5 m/s² downward (> g); z fell from 1.88 m (t = 0.085 s) to 1.59 m (t = 0.3 s) | same throw | §V | cross2012ajp |
| 27 | Another case | a_z ≈ −17 m/s² for ball 4 | "some conditions" | §III | cross2012ajp |
| 28 | Local Re at the ball surfaces | 2.2×10⁵ on the high-speed side (14.4 m/s) and 8.5×10⁴ on the low-speed side (5.6 m/s). Mechanism: turbulent separation on one side, laminar on the other | v = 10 m/s, Rω = 4.4 m/s | Fig. 12, §VIII | cross2012ajp |
| 29 | Side force from surface asymmetry (string loop), ball 2 | C_S ≈ 0.22 at an average 6 m/s → about 0 at an average 12 m/s; reverses sign above that | 98 mm, 12.15 g, backspin; Re ≈ 3.9×10⁴ at 6 m/s (computed) | §VI, Fig. 10 | cross2012ajp |
| 30 | Break, ball 2 | about 100 cm over 5 m (initial 9 m/s, about 475 rpm, 0.8 s, about 3 m/s² lateral); about 0 at 12 m/s (about 1425 rpm) | speed dropped about 45% over 5 m | §VI, Fig. 10 | cross2012ajp |
| 31 | Break, ball 3 (baseball seam) | up to 90 cm over 5 m; launch 10–12 m/s, 400–500 rpm, average 6–7 m/s. Example: 11.8 m/s, 474 rpm, 0.70 s, average 7.1 m/s, spin axis tilted about 10° | hand throw | §VII, Fig. 11 | cross2012ajp |
| 32 | Spin decay over 5 m | spin "remained constant" during transit | ball 3, about 0.7 s | §VII | cross2012ajp |
| 33 | Video and spin precision | 300 and 120 fps; spin within 2%; target impact within 1 cm; 1° launch error = 9 cm at 5 m | — | §III | cross2012ajp |

## 5. Applicability to POLLEN

POLLEN: d = 71 mm, m ≈ 25 g, perforated hollow PE, v ≈ 2–10 m/s. Using Cross's Re formula, **Re ≈ 4.75×10³ · v**, about 9.5×10³ at 2 m/s and 4.8×10⁴ at 10 m/s.

**What transfers**
- **Method (strongest transfer).** The two-station or polynomial-fit video method (Eqs. 1–5) is cheap, needs no wind tunnel, and applies directly. POLLEN fits it better than a baseball does.
  - A ballistic length L = 2m/(ρ A C_D) with C_D = 0.5 gives about 21 m for POLLEN, against about 4.6 m (ball 1) and about 9 m (ball 4).
  - POLLEN is therefore 2–4× "heavier" aerodynamically than Cross's balls, but much lighter than a tennis ball or baseball.
  - At 8 m/s: drag acceleration ≈ 3.1 m/s² (C_D 0.5) and Magnus acceleration ≈ 2.5 m/s² (C_L 0.2). That is 25–30% of g, enough to resolve by fitting (my calculation; see §6).
- **Smooth-ish sphere Cd in the POLLEN Re band.** Row 17: C_D = 0.55 ± 0.05 at Re ≈ 2–3×10⁴ (non-spinning, 101 mm polystyrene). Row 12: C_D ≈ 0.40 at Re ≈ 4.7×10⁴ with S ≈ 1.5. These are the only directly measured numbers here that fall inside the POLLEN Re band. Use them as smooth-sphere bounds, not as POLLEN values.
- **Cl(S) shape.** A plateau of about 0.3 for S > 0.4 in "most balls" (literature), or a rise to about 0.33 near S ≈ 1 (ball 1). Ball 1's Fig. 7b points at S ≳ 1 are at v ≲ 10 m/s, Re ≲ 6.7×10⁴, near the top of the POLLEN band, so they are the closest analogue. They give a ceiling of about 0.33 and **no further gain beyond S ≈ 1**: Cl drifts down to about 0.30 at S ≈ 1.45. This supports a C_L ceiling in PM-001 and argues against "more spin is always better".
- **The 2017 abstract adds non-monotonic Cl(S) for smooth balls.** One ball's Magnus collapses to about 0 after a maximum, and one ball reverses sign at low S. For smooth spheres, C_L(S) can therefore be non-monotonic and even negative. This is a qualitative bound only, since the Re and S where it happens are unknown without the full text.
- **Spin can increase in flight** (2017 abstract) or stay constant over about 0.7 s (row 32). A pure exponential decay model with a fixed k_spin may be wrong in sign for smooth balls. Measure it.
- **Surface asymmetry gives side force at POLLEN-like Re** (row 29: C_S ≈ 0.22 at Re ≈ 3.9×10⁴). A string loop on one side gave a lateral force about 1/3 g. POLLEN's perforation pattern and out-of-roundness are surface asymmetries. They could produce orientation-dependent side and lift forces (a knuckle effect) at low spin, and they become a shot-to-shot scatter source. In Cross's data the effect faded as speed and spin rose.

**What does not transfer**
- **Reverse Magnus regime.** The measured negative Cl (ball 4) occurred at Re ≈ 1.4–2.1×10⁵, near the drag crisis. One side of the ball was turbulent and the other laminar (row 28). POLLEN at 2–10 m/s is at Re ≤ 5×10⁴, 3–4× below. For a smooth 71 mm ball the near-critical mechanism is therefore unlikely.
  - However, perforations and a rough or holed surface can trip the boundary layer and lower the critical Re (row 18: by 2–3×). The low-Re "lift crisis" seen for table-tennis balls (see the sakai2016 and ito2025 files) is in a range that **does** overlap POLLEN.
  - So: smooth-ball reverse Magnus is "unlikely but not excluded" for POLLEN. PM-001 should keep a C_L < 0 branch at low S as an uncertainty case until POLLEN is measured.
- **The balls are solid or sealed, not perforated.** Through-holes allow flow into and through the shell, add base-bleed and drag, and may weaken or alter Magnus lift (cf. Rossmann & Rau wiffle-ball work). Nothing in Cross's data covers this. The Cd and Cl here are smooth-sphere bounds only.
- **Buoyancy is negligible for POLLEN.** m_A = ρ·(4/3)πR³ ≈ 0.23 g against 25 g (about 0.9%). The perforated shell's internal air partly co-moves. Include it as a 1% correction or drop it.

## 6. Implications for the PM-001 models

1. **Aero model (src aero):**
   - Default bounds for a smooth sphere at Re 1–5×10⁴: C_D ∈ [0.40, 0.60]. Use 0.50–0.55 nominal at S ≈ 0, and allow C_D to rise with S. Ball 1's C_D was about 0.40 at S ≈ 1.5 and Re 4.7×10⁴. Spin effects on C_D are not separable in that throw.
   - C_L(S) envelope: lower curve C_L = 0 or slightly negative (−0.1) for S ≲ 0.3, reflecting the 2017 ball C sign reversal; nominal curve rising to about 0.3 by S ≈ 0.4–1; ceiling 0.33. Beyond S ≈ 1, flat or slightly falling. Add a "collapse" variant (C_L → about 0 at high S) per the 2017 ball B for sensitivity runs.
   - Label all of these as smooth-sphere bounds, **not POLLEN values**.
2. **Spin model:** replace a fixed-sign exponential decay with dω/dt = −k_spin·ω, k_spin ∈ [−small, +k_max]. Allow k ≈ 0 (constant spin over about 1 s, row 32) as the baseline, and treat spin-up in flight as an unknown to measure. This matters little over a ≤1.5 s flight unless |k| > about 0.3 s⁻¹.
3. **Side-force term:** add an optional F_S = ½ ρ A C_S v² with a random orientation-dependent C_S, so perforation asymmetry can be included in robustness and Monte-Carlo runs. Bound |C_S| ≤ 0.2 at low spin (row 29, an extreme case with a 1.5 mm string loop), decaying with S. Measure it for POLLEN; do not assume it is 0.
4. **Launcher coupling note:** Cross's lacrosse launcher, like an ideal single-wheel shooter, ties spin to speed (S roughly constant). His ball 1 ran at S ≈ 0.37 at 28 m/s and S ≈ 1.5 near apex speeds. For a single-wheel POLLEN shooter with S_exit ≈ 1 (HANDOFF §4C), S **rises** further near the apex as v drops while ω stays roughly constant. The useful C_L there is capped (about 0.3), and Magnus force ∝ C_L v² **falls** at the apex. This shows quantitatively why "spin hooks at the apex" cannot be a strong effect: at v_apex ≈ 3 m/s and C_L = 0.3, a_M ≈ 0.5·1.225·0.3·3.96×10⁻³·9/0.025 ≈ 0.26 m/s² (≈ 2.7% g). This is my calculation from smooth-sphere bounds.
5. **Calibration template for real POLLEN (testing recommendation):**
   - **Rig:** one 240+ fps camera viewing the x–z plane square-on, at ≥ 5 m standoff to limit perspective error. Use a second camera or mirror for out-of-plane drift and spin (two cameras at 90°, as in Cross 2012). Calibrate scale with a board at several depths (Cross & Lindsey tennis rig). Mark the ball with a contrasting stripe for spin, read by counting frames per revolution, as Cross did (±2%).
   - **Reduction:** use Cross's Eqs. 3–4 with polynomial fits in windows where the speed changes by < 20% (quadratic). As a primary method, use Cross's recommended alternative for heavier balls: fit an integrated ODE trajectory (this repo's free-flight model) with parameters C_D, C_L(S) and optionally k_spin, by least squares on all frames.
   - **Precision estimate (mine):** for a quadratic fit over T = 0.6 s with N = 144 frames and 2 mm position noise, σ(a) ≈ 2σ·√(180/(N T⁴)) ≈ 0.012 m/s². Random error is negligible, and systematic scale, lens and depth error dominates: a 1% scale error is about 0.1 m/s², about ΔC_L 0.01 at 8 m/s. Expect C_L resolution of about ±0.02–0.03 per throw at 6–10 m/s. It degrades as 1/v², so low-speed or apex windows (< 4 m/s) are poorly resolved. Cross saw the same thing below 5 m/s for a 9 g ball.
   - **Test matrix:** S = 0 (hand-dropped or no-spin push) for C_D; then the shooter at 3–4 RPM settings giving S_exit ≈ 0.3–1.5. Use ≥ 5 throws per setting, since Cross's scatter was about ±0.1 in C_L from shot to shot (Fig. 9). Repeat with the ball rotated to different perforation orientations relative to the spin axis to expose any C_S or C_L orientation dependence. Explicitly check the sign of C_L at low S (reverse Magnus).
   - **Low-speed C_D:** add a pendulum-in-airflow check (Cross's fan and 1.1 m V-thread pendulum, or a car-window or box-fan rig with an anemometer) for v ≈ 3–5 m/s, where trajectory fits are weak.
6. **Uncertainty bookkeeping:** until POLLEN data exist, carry C_L ∈ [−0.1, 0.35] and C_D ∈ [0.40, 0.65] (perforation may raise C_D above smooth-sphere values) as the bounding box in trajectory sensitivity runs. Report which conclusions survive across the box.

## 7. Caveats

- The 2017 paper's own numbers were **not** accessed. Every quantitative claim in §4–6 comes from the 2012 companion paper, from my own calculations, or from the abstract. A full-text read of the 2017 paper should replace or extend rows 3–7.
- The Cross 2012 coefficient values were read off figure images and are approximate.
- Ball 1's Cl(S) comes from a **single throw** in which v and S co-vary, so S and Re effects are confounded. Ball 4's points are path averages over the first 2 m, with large scatter.
- The polystyrene balls are "slightly rough" (0.5 mm relief), not truly smooth.
- Neither paper studies perforated balls or Re < 1.9×10⁴ in flight.
