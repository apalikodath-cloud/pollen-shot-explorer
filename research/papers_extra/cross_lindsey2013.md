# Cross & Lindsey (2013/2014): Measurements of drag and lift on tennis balls in flight

source_id: `cross_lindsey2013` (RESEARCH_PAPERS.md source #12), the target paper.
Companion source: `cross_lindsey_twu`. This is the authors' own open web write-up of the same experiment on the Tennis Warehouse University site. The page credits both Cross and Lindsey and says: "The results of this experiment also appear in a separate paper in the Journal of Sports Engineering". It is **not** the peer-reviewed paper and has no review status. Every row below says which of the two it came from.
Read: 2026-10-30, research agent for PM-001 (papers_extra workflow).

## 1. Citation, access, review status

| Field | Value |
|---|---|
| Citation | R. Cross and C. Lindsey, "Measurements of drag and lift on tennis balls in flight", *Sports Engineering* **17**(2), 89–96 (2014). DOI 10.1007/s12283-013-0144-9 |
| Dates (Crossref) | Online 7 Nov 2013; issue dated June 2014 |
| Review status | Peer-reviewed journal (Springer *Sports Engineering*, ISEA journal). Semantic Scholar lists 1 citation, which is surely an undercount. |
| Method type | Free-flight experiment. Balls are fired from a ball machine and filmed at two stations 6.4 m apart. C_D and C_L come from the change in speed and height between the stations. |
| Access, paper | **Abstract only.** Unpaywall: `is_oa=false`, `oa_status=closed`. Semantic Scholar: CLOSED, and the abstract is elided by the publisher. Crossref has no abstract. The Springer landing page (reached through the idp.springer.com cookie redirect) showed the abstract and preview only. That page text came through a summarising fetch tool with a quote-length limit, so the abstract was **not seen as one continuous verbatim block**. |
| Access, companion | **Full web text** of the TWU page (`cross_lindsey_twu`), read three times with targeted prompts. It also came through the summarising fetch tool. Numbers below are those the tool relayed, and each was asked for explicitly. Figures and plots were not seen. |
| Consequence | Per the abstract-only rule, **no numbers are attributed to the peer-reviewed paper itself.** Numbers in §5 are labelled `cross_lindsey_twu` (unreviewed technical source, same authors, same experiment). Where the paper's abstract and the TWU page disagree, §8 records it without quoting the abstract's figure. |

URLs tried:
- https://api.unpaywall.org/v2/10.1007/s12283-013-0144-9 (closed)
- https://api.crossref.org/works/10.1007/s12283-013-0144-9 (no abstract)
- https://api.semanticscholar.org/graph/v1/paper/DOI:10.1007/s12283-013-0144-9 (abstract elided)
- https://link.springer.com/article/10.1007/s12283-013-0144-9 (303 to idp.springer.com/authorize, then 302 back with `?error=cookies_not_supported...`; the final page showed the abstract and preview only)
- A curl download of the Springer page with a cookie jar was **refused by this session's permission classifier** and was not tried again.
- https://twu.tennis-warehouse.com/learning_center/aerodynamics2.php (companion, full text)
- https://www.physics.usyd.edu.au/~cross/TRAJECTORIES/ (Cross's directory; no file named for this paper; "Sports Balls.pdf" not opened)
- Web search for the paper title plus "pdf" found no OA PDF.

**Action for the lead:** someone with Springer access should get the PDF. It is needed to confirm the C_D/C_L algebra and the per-shot scatter plots against S. The TWU page gives neither the closed-form reduction nor the fit coefficients.

## 2. What the sources report

### 2.1 Peer-reviewed paper (abstract only; qualitative content)
- Two video cameras measured ball velocity and height at two positions a fixed distance apart. Balls were fired with topspin or backspin.
- "Significant shot-to-shot variations were found in both the drag and lift coefficients."
- The average drag coefficient was "independent of ball speed or spin". The abstract says it was lower than typical wind-tunnel values.
- Lift increased with spin on average, but "significant lift was observed even at very low spin". The authors attribute this to a force from asymmetries in the ball surface and flow, which they compare to a baseball knuckleball.

Grade: **peer-reviewed finding** (qualitative only).

### 2.2 Companion TWU page (unreviewed technical source)
- Launcher: a Tennis Tutor ball machine. Speed and spin were measured just after launch and again 6.4 m downrange. The launch angle was re-set after each speed or spin change so that the ball stayed in both camera views.
- Cameras 1 and 2 ran at 300 fps, shutter 1/5000 s, 150 mm zoom, with a field of view of about 80 cm × 60 cm. Camera 3 ran at 120 fps (139 mm zoom, shutter 1/250 to 1/2000 s) and watched out-of-plane (z) motion.
- Spin: "All balls were marked with perpendicular equatorial lines to determine spin". The spin axis was set parallel to the camera line of sight. The formula for spin from the lines, the number of frames used and the spin uncertainty are **not stated**.
- Speed: each author digitised the ball centres at x = 0 and x = 6.4 m separately, with different methods, and the two were averaged. Speed came from two ball centres taken "an equal number of video frames to either side of the y-axis". The relayed text gives those centres as about 400 mm apart horizontally and about 40 mm vertically. The software is described only as "motion analysis software", and the text does not say whether tracking was manual or automatic.
- C_D and C_L: "calculated ... from the change in speed and ball height between the two positions", using F_D = ½C_DρAv², F_L = ½C_LρAv² and F_g = mg. The algebra is not given.
- Calibration:
  - A 60 cm board was filmed in the trajectory plane and at several depths in front of and behind it. A second-order polynomial of seen length against depth gives the scale correction.
  - Lens distortion was checked on a 1 cm grid.
  - The horizontal reference came from a water level (a U-tube) marked on the back wall, with the camera cross-hairs aligned to it.
  - The frame rate was measured.
  - Parallax was checked and needed no correction.
  - The stated goal was position accuracy of "1% or better". The page warns that "Drag and lift coefficients are very sensitive to small errors in position measurement".
- Results for new balls: C_D did not vary significantly with velocity or spin. C_L rose "almost linearly" with S. Quadratic best fits were drawn, but no coefficients are given. Shot-to-shot scatter was attributed mainly to fuzz orientation ("random fuzz and flow asymmetries").
- Against wind tunnels: C_D and C_L were lower than in sting-mounted tunnel tests and similar to ball-drop tunnel tests. Non-spinning C_D fell at low Re, the opposite of most tunnel results. A "fuzz ramp" explanation is offered and labelled speculative.
- The authors' own recommendations: others should repeat the measurements; test smooth balls with added fuzz; use a launcher that "could independently vary the speed and spin of the ball".

## 3. Method summary (what to copy)

| Element | Cross & Lindsey (TWU) | Grade |
|---|---|---|
| Measurement idea | Two short high-speed views a known distance apart; ΔC from Δspeed and Δheight | unreviewed technical source (the paper's abstract confirms two cameras at two positions) |
| Spin | Perpendicular equatorial lines drawn on the ball; spin axis aligned with the camera line of sight | unreviewed technical source |
| Frame rate / shutter | 300 fps, 1/5000 s (main); 120 fps (out-of-plane camera) | unreviewed technical source |
| Scale | 60 cm board at several depths, quadratic depth correction | unreviewed technical source |
| Horizontal | Water-level line on the wall | unreviewed technical source |
| Digitising | Two independent digitisers, averaged | unreviewed technical source |
| Checks | Frame rate measured; lens distortion grid; parallax angle | unreviewed technical source |

## 4. Equations

| # | Equation | Symbols | Source / grade |
|---|---|---|---|
| E1 | F_D = ½ C_D ρ A v² | ρ air density [kg/m³], A = πR² [m²], v speed [m/s] | TWU page / theory (standard) |
| E2 | F_L = ½ C_L ρ A v², perpendicular to v | same | TWU page / theory |
| E3 | S = r ω / v | r ball radius [m], ω [rad/s] | TWU page / theory |
| E4 | Re = v D / ν, ν = 1.5×10⁻⁵ m²/s at 20 °C | D diameter [m] | TWU page / theory |
| E5 | Equations of motion fitted in this note (§7): a = −(ρA/2m)·v·(C_D **v** − C_L **n̂×v**) − g ẑ | m mass, n̂ spin-axis unit vector | derived here (standard) |

## 5. Data table

| Quantity | Value | Conditions | Where | source_id / grade |
|---|---|---|---|---|
| Station spacing | 6.4 m | two cameras, one near launch and one downrange | TWU text | cross_lindsey_twu / unreviewed |
| Main camera frame rate, shutter | 300 fps, 1/5000 s | 150 mm zoom, field ≈ 80 × 60 cm | TWU text | cross_lindsey_twu / unreviewed |
| Measured actual frame rate | 299.7–300.1 fps | camera check | TWU text | cross_lindsey_twu / unreviewed |
| Out-of-plane camera | 120 fps, 1/250–1/2000 s | 139 mm zoom | TWU text | cross_lindsey_twu / unreviewed |
| Launch speed | 14–30 m/s | Tennis Tutor machine | TWU text | cross_lindsey_twu / unreviewed |
| Spin | −2400 to 2500 rpm | backspin to topspin | TWU text | cross_lindsey_twu / unreviewed |
| Spin parameter range | S = 0.14–0.53 | TWU Table 1b row for this study | TWU text | cross_lindsey_twu / unreviewed |
| Shots (new balls) | 128 | — | TWU text | cross_lindsey_twu / unreviewed |
| Mean C_D (new balls) | 0.507, SD 0.024; range 0.453–0.567 | "did not vary significantly with velocity or spin" | TWU text | cross_lindsey_twu / unreviewed |
| C_L | 0.1–0.3, ≈ linear in S; non-zero at very low S | new balls; S 0.14–0.53 | TWU Table 1b and text | cross_lindsey_twu / unreviewed |
| Air properties used | ρ = 1.21 kg/m³; ν = 1.5×10⁻⁵ m²/s at 20 °C | humidity not reported | TWU text | cross_lindsey_twu / unreviewed |
| Ball (tennis, not POLLEN) | 58.03 g, 65.68 mm mean; A = 0.0034 m² | Penn ATP Extra Duty | TWU text | cross_lindsey_twu / unreviewed |
| Position accuracy goal | ≤ 1 % | — | TWU text | cross_lindsey_twu / unreviewed |
| Level-error example | 0.1° over 8 m gives ≈ 14 mm at the far end | laser-level discussion | TWU text | cross_lindsey_twu / unreviewed |
| Lens distortion | 0.21 % (rows), 0.109 % (columns) at 93 mm zoom | 1 cm grid at 520 mm | TWU text | cross_lindsey_twu / unreviewed |
| Uncertainty of C_L, confidence intervals | not stated | — | — | — |
| Fit coefficients C_D(S), C_L(S) | not stated (quadratic fits shown only as lines) | — | — | — |
| POLLEN fit-precision estimates | see §7.3 | assumption-driven | this note | derived |

## 6. Applicability to POLLEN

**Transfers (qualitatively):**
- **In-flight fitting works, and it can disagree with tunnel data.** Free-flight C_D and C_L for a fuzzy ball were lower than sting-mounted tunnel values. For POLLEN, with no tunnel data at all, this is an argument for in-flight fitting on the real ball and real launcher.
- **Shot-to-shot scatter is real and comes from the ball's surface asymmetry**: fuzz orientation for tennis. POLLEN's hole pattern is a strong, fixed asymmetry. Expect the orientation of the hole pattern relative to the spin axis to change C_L and to cause side forces. **Report C_L as a distribution over many shots**, not one fitted value. That is also what hypothesis testing needs (HANDOFF §5: no repeatability from one shot).
- **Lift at near-zero spin**, from surface asymmetry, has been observed. POLLEN may show a knuckle-type lateral or vertical force at low spin. The overhead camera must look for it, and the flight model needs a stochastic side-force term.
- **Coupled speed and spin from the launcher** was a stated limitation, and our flywheel + hood couples them too. Plan launcher settings that change S at roughly constant speed: for example, vary hood compression or a passive-roller preload at fixed wheel speed. Then C_L(S) is not confounded with Re.
- **Calibration discipline**: depth-dependent scale, a true horizontal, measured frame rate and lens distortion. Our derived sensitivity (§7.3) shows these, not random digitising noise, dominate the error.

**Does not transfer:**
- All coefficients. C_D ≈ 0.5 and C_L 0.1–0.3 are for a **felt-covered, sealed, pressurised** 66 mm, 58 g ball at 14–30 m/s. POLLEN is a perforated 71 mm, ~25 g shell, probably at well under 10 m/s, so Re and S are different and the surface is different. Perforated balls can show reduced or reversed Magnus lift (RESEARCH_PAPERS.md #3, #11). **Do not use 0.507 or the C_L range as POLLEN priors** except as very loose sanity bounds.
- Station spacing. 6.4 m is longer than a whole POLLEN shot to the HIVE. Use a full-trajectory fit instead (§7).

## 7. Concrete recommendations for the POLLEN test rig

### 7.1 Cameras and lighting
- **Side camera**: line of sight perpendicular to the flight plane and **parallel to the intended spin axis**, as in Cross & Lindsey. Frame the whole arc from hood exit to the CELL plane, or use two side cameras with overlapping frames if one cannot cover it. Phone slow-motion at ≥ 240 fps is acceptable (see §7.3).
- **Overhead camera**: looks down at the flight plane and measures lateral drift (side force, spin-axis tilt). It plays the role of Cross & Lindsey's out-of-plane camera.
- **Exposure**: bright continuous light, not flickering LED PWM, so the shutter can be short. Derived: at 6 m/s, 1/2000 s gives 3 mm of blur and 1/5000 s gives 1.2 mm. Aim for ≤ 1/2000 s.
- **Sync**: put an LED or a clap visible to both cameras at the start of each take. Measure each camera's real frame rate by filming a running stopwatch or LED blinker over ≥ 10 s, as Cross & Lindsey did for their frame-rate check.

### 7.2 Fiducials
- **On the ball**: draw two perpendicular great circles in **different colours**, plus one dot. Cross & Lindsey used "perpendicular equatorial lines". Same-colour lines repeat every 90° and can alias. Different colours plus a dot remove the ambiguity. Optionally record hole-pattern orientation by numbering the holes near the dot.
- **Frames per revolution (derived)**: ω = S·v/R. At v = 6 m/s and R = 0.0355 m, S = 0.5 gives ≈ 84 rad/s ≈ 13 rev/s, and S = 1 gives ≈ 27 rev/s. At 240 fps that is ≈ 18 or ≈ 9 frames per revolution. Keep ≥ 8 frames per revolution: rotation per frame must stay under half the pattern's repeat angle to avoid aliasing. Measure spin at **both ends** of the flight to get spin decay; Cross & Lindsey measured at both stations.
- **In the scene**:
  - a scale bar (≥ 60 cm) filmed in the flight plane and at ±10–20 cm depth, for a depth-scale correction as Cross & Lindsey did;
  - a printed checkerboard for lens distortion;
  - a plumb line or water-level mark for true vertical and horizontal;
  - fixed fiducials on the HIVE mock-up, so the CELL plane is located in the same image coordinates.

### 7.3 Fitting C_D and C_L from video (derived; assumption-driven illustration)
Use a **full-trajectory least-squares fit**, not Cross & Lindsey's two-station Δv method. Over a short POLLEN shot, the drag-induced speed loss is only a few percent per metre, so a two-station Δv is fragile. Free parameters: x₀, z₀, v_x0, v_z0, C_D, C_L. Use E5 with constant coefficients, then repeat with C_L(S) and spin decay once spin is measured.

Linearised (Fisher) precision estimate, computed in this session in plain Python. Inputs: R = 0.0355 m, m = 0.025 kg, ρ = 1.2 kg/m³, **placeholder** C_D = 0.45 and C_L = 0.20 (these are assumptions, not POLLEN data), launch at 60°, independent Gaussian position noise σ on each coordinate:

| v₀ [m/s] | fps | window [s] | σ_pos [mm] | sd(C_D) | sd(C_L) |
|---|---|---|---|---|---|
| 6 | 240 | 0.5 | 1 | 0.007 | 0.007 |
| 6 | 240 | 0.25 | 1 | 0.025 | 0.025 |
| 6 | 120 | 0.5 | 1 | 0.009 | 0.009 |
| 6 | 240 | 0.5 | 3 | 0.020 | 0.020 |
| 6 | 60 | 0.5 | 3 | 0.039 | 0.039 |
| 6 | 240 | 0.8 | 2 | 0.006 | 0.006 |
| 8 (55°) | 240 | 0.5 | 1 | 0.003 | 0.003 |

The C_D and C_L estimates are nearly uncorrelated (r ≈ 0.004 in the first case).

**Systematic errors dominate** (same model, g fixed, noise-free data distorted then refitted):
- 1 % scale error: C_D bias +0.041, C_L bias −0.047.
- 0.1° level error: about −0.008 on each.
- 0.1 % frame-rate error: about ±0.009 on each.

So:
1. Track the **longest window** you can (≥ 0.5 s, i.e. most of the arc). Window length matters more than frame rate above ~120 fps.
2. **Get scale right to ≤ 0.2 %.** As a built-in check, refit with **g free**: a fitted g off by x % flags an x % scale or frame-rate error.
3. Level to ≤ 0.1°, and use the measured fps, not the nominal one.
4. Automate centroid tracking (sub-pixel circle fit). Have a second person, or a second method, hand-digitise a few shots and compare. Cross & Lindsey averaged two digitisers.
5. Fit side-force C_Y from the overhead view in the same way.

### 7.4 Shot plan
- ≥ 20 shots per launcher setting (HANDOFF §5). Record wheel rpm, hood compression, ball ID and hole-pattern orientation for every shot.
- Include **zero-spin or low-spin control shots** (hand toss or a no-hood setting) to measure knuckle-type forces.
- Vary S at fixed speed wherever possible (see §6) to separate S from Re.
- Report C_D, C_L and C_Y as means with shot-to-shot SDs, plus each fit's own uncertainty. Feed the distributions, not the means, into the PM-001 Monte Carlo of HIVE entry.

## 8. Caveats

- Paper: abstract only, and even that was seen through a summarising fetch. No paper figure, table, equation or per-shot data was seen.
- Companion page: the content was relayed by a summarising fetch tool with short quotes. Numbers were requested explicitly and cross-checked over three reads, but the plots were not seen.
- One relayed sentence was ambiguous: "Cameras 1 and 2 were about 0.5 m apart". It most likely means camera-to-path distance and is **not used**.
- **Discrepancy:** the lower end of the launch-speed range differs by 1 m/s between the paper's abstract and the TWU page. The TWU value is used and labelled as such.
- TWU Table 1b also lists "34-67 mph" for this study, while its Table 1a row says "34-54 mph". This is unreconciled and only matters for tennis.
- §6–7 are this note's interpretation. The §7.3 numbers are this note's own calculation with placeholder coefficients. They size the rig and are not POLLEN results. The script is in the session scratchpad and was not saved to the repo.
