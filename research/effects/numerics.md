# Numerics lens: integrator, contact detection, uncertainty, sensitivity, CFD, cheap tests

Written 2026-10-30 for PM-001 (research only; no code changed).

**Labels** (HANDOFF §5):
- **CONFIRMED**: from a cited source.
- **user**: the user said it.
- **ASSUMED**: a modelling choice.
- **derived**: arithmetic on labelled inputs.
- **PREDICTED**: model output.

Every PREDICTED number below is a model output under ASSUMED parameters. None of them is a fact about the real POLLEN. Pickleball, Wiffle, tennis and smooth-sphere coefficients are cited only as context, never as POLLEN values. Each backspin result has its no-spin twin beside it.

## 0. Default case used everywhere below

- **Geometry:**
  - Unfavourable (far) side, `pose_pos` HIVE seen from neg, tilt 30°.
  - Release is 1.0 m from the HIVE pivot plane at h = 0.737 m (user/HANDOFF).
  - The gate is the HIVE opening segment, 286.4 mm long (derived from `src/hive.py`).
  - s = the position along the gate where the ball crosses it.
- **Aero:** `research/params_lit.json` nominal (ASSUMED):
  - Cd 0.5;
  - Cl = min(0.35·S, 0.25);
  - k 0.03 1/s;
  - ρ 1.2 kg/m³, m 24.95 g, R 35.5 mm.
- **Spin case:** S = 1 (ASSUMED). It is saturated: the Cl cap is reached at S_sat = 0.25/0.35 = 0.71 (derived).
- **Clean windows** (PREDICTED, grid 0.1 m/s × 0.1°, RK4 dt 2 ms, same classifier as `hive.classify_path`):

| v (m/s) | θ window, backspin S=1 | θ window, no-spin twin |
|---|---|---|
| 7.0 | 77.4–77.8° | 79.0–79.4° |
| 9.0 | 80.6–80.9° | 83.1–83.4° |
| full scan | v 5.8–10.0, 172 clean cells, window 0.2–0.4° wide | 187 clean cells |

- **Effect of backspin:** in this model it moves the window about 1.6–2.5° lower in launch angle (PREDICTED). It does not widen the window. No claim is made that more spin is better.
- **Representative shots** (PREDICTED):
  - Spin: v 7.0, θ 77.6°. Clearance 23.5 mm, gate s 118.0 mm.
  - Twin: v 7.0, θ 79.2°. Clearance 26.1 mm, s 116.8 mm.
- **Wheel speed:** v 7 m/s ≈ 3250 wheel rpm on a 98 mm wheel, if v/u_rim ≈ 0.42 (derived from an ASSUMED ratio, which is not measured).
- **Local gradients at these shots** (PREDICTED):

| Gradient | Spin | Twin |
|---|---|---|
| ds/dθ (mm per degree) | 409 | 389 |
| ds/dv (mm per m/s) | −1106 | −1219 |

A 1° hood error moves the crossing about 0.4 m, more than the whole gate.

Method: scratchpad scripts. They are vectorised float64 RK4/DOP853 copies of the repo ODE and are not committed. Re-running them needs only numpy and scipy, which are already used by the repo.

---

## 1. RK4 step convergence

**What.** The batch scan (`feasibility.integrate_batch`) and the explorer (`solver.js fastShot`, `physics.js`) use fixed-step RK4 at dt = 2 ms. `flight.simulate` uses scipy RK45 with rtol 1e-9 and max_step 1 ms.

**Numbers** (PREDICTED): error against a DOP853 reference (rtol 1e-13) at the representative shots.

| dt | Clearance error, spin | Gate-s error, spin | Clearance error, twin | Gate-s error, twin |
|---|---|---|---|---|
| 8 ms | 11 µm | 19 µm | 17.6 µm | 51 µm |
| 4 ms | 3.4 µm | 8 µm | 1.0 µm | 8.7 µm |
| **2 ms (current)** | **0.3 µm** | **2.6 µm** | **0.5 µm** | **3.2 µm** |
| 1 ms | 0.14 µm | 0.13 µm | 0.2 µm | 0.5 µm |

- Storing the batch in float32 adds ≤ 0.2 µm (PREDICTED).
- The Cl = min(c1·S, Clmax) kink and the |v| near the apex take away RK4's formal 4th order locally. The error stays at the µm level because the speed never drops below 1.1 m/s on these shots (derived), so |v| never reaches 0. The ball is moving at the apex.

**Size for this shot.** Numerical error ≈ 3 µm in s, compared with a clean band of about 80–160 mm in s (0.2–0.4° × 409 mm/deg, derived). That is about 1e-5 of the window (derived). **The integrator is not a limitation.**

**In model?** Yes.

**Action.** None needed. Optional: a regression test asserting that dt 2 ms and dt 1 ms agree to within 10 µm at one fixed shot.

Sources:
- Hairer, Nørsett & Wanner, *Solving ODEs I*, Springer 1993, doi 10.1007/978-3-540-78862-1 (DOP853, order and step control).
- scipy `solve_ivp` documentation, https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html

## 2. Wall-contact event detection ("2 ms sampling misses grazing contacts")

**What.** The worry is that discrete sampling can step over a thin wall, or a graze shorter than one step. Physics engines handle this with continuous collision detection (CCD). CCD sweeps the moving shape between samples and finds the first time of contact. See Redon, Kheddar & Coquillart 2002, *Comput. Graph. Forum* 21(3):279–287, doi 10.1111/1467-8659.t01-1-00587. The ODE equivalent is root-finding on an event function g(t) = dist − R; see Shampine & Thompson 1991, *ACM TOMS* 17(1):11–25, "Reliable solution of special event location problems for ODEs".

**Finding** (derived from code reading).
- The repo is **already a swept test**. `hive.classify_path` computes the exact segment-to-segment distance between each 2 ms chord of the path and each HIVE wall segment, then compares it with R. That is CCD with a capsule of radius R swept along the polyline. The JS `fastShot` does the same.
- A wall cannot be stepped over. Even at 20.7 mm of travel per step (10.4 m/s × 2 ms, derived), a chord that crosses a wall has distance 0.
- **Residual error 1: chord sag.** The true path bows away from the straight chord by at most |a|·dt²/8. Here that is ≤ 4.9 µm (derived, |a| ≤ about 9.8 m/s²).
  - A real graze is missed only if the true clearance lies within 5 µm of R.
  - That is three orders of magnitude below the ±0.25 mm radius tolerance (ASSUMED, `robustness.PHYS`).
- **Residual error 2: polygon entry.** "Clean" is declared when a *sample point* is inside the scoring polygon.
  - Grazing the polygon corner between samples (less than one step of path inside it, ≤ 21 mm) would read as "not yet clean".
  - Contact is still checked on later segments, so this never turns a hit into a clean shot. It can only make the clean/miss boundary slightly conservative, by under 1 step.

**Size for this shot.** ≤ 5 µm of clearance (derived). Negligible.

**In model?** Yes, as a swept capsule.

**How to make it exact** (optional, cheap):
- **Event root on contact.** In each step where min dist < R + h_sag, solve g(t) = |p(t) − q_wall| − R = 0. Use the RK4 dense output (cubic Hermite on p and v at the step ends) and bisect: about 20 Hermite evaluations per flagged step.
- **Polygon entry.** Use a segment–polygon intersection on each chord instead of a point-in-polygon test on samples.

**How to measure.** Not measurable. It is a pure numerical property, and the test is dt-halving (§1).

## 3. Uncertainty propagation: hit-probability maps instead of binary windows

**What.** Push the launch scatter (aleatory) and the uncertain aero coefficients (epistemic) through the ODE to get P(clean | aim) instead of a yes/no window. Roy & Oberkampf 2011 separate these two kinds of uncertainty: *CMAME* 200:2131–2144, doi 10.1016/j.cma.2011.03.016. Intervals use Wilson 1927, *JASA* 22:209–212, doi 10.1080/01621459.1927.10502953.

**Existing code** (derived from code reading).
- `src/robustness.py` already has this:
  - `mc_shots` is a 3D vectorised RK4 with per-shot mass, R, Cd ±5 %, Cl ±10 %, S ~ U(1.03, 1.27), wind σ 0.3 m/s, release errors, and HIVE tilt/pivot/x scatter (all σ ASSUMED).
  - Wilson intervals.
  - A field map.
  - A no-spin twin scenario.
  - Output in `data/robust_mc.csv`.
- **The live explorer shows only binary windows plus tolerant and knife-edge minima.**

**Numbers** (PREDICTED, N = 3000, nominal ERR + PHYS, nominal aero, aim at the representative shots above):

| | Backspin S≈1 | No-spin twin |
|---|---|---|
| P(clean) [95 % Wilson] | 0.294 [0.278, 0.311] | 0.312 [0.296, 0.329] |
| SD of gate crossing s | 237 mm | 232 mm |
| Outcomes, spin case (n = 3000) | clean 883, roof/outer 998, floor 513, miss 378, lower lip 119, upper lip 109 | — |

- The SD of s (237 mm) is about 2–3 times the clean band in s, so **at the ASSUMED scatter, about 30 % is the ceiling for any single aim**. These are model probabilities for the ASSUMED σ, not a repeatability claim about a real robot.
- `data/robust_mc.csv` (best hood aim, d 0.81) shows the same pattern:
  - nominal P 0.303 [0.281, 0.327];
  - Cl_low_transfer 0.097;
  - Cl_high_transfer 0.054.
- So a plan tuned under the wrong Cl loses about two thirds of its hit rate (PREDICTED).

**How to add to the explorer** (recommendation for the page owner; this agent did not edit `page.html`):
1. For each (v, θ) cell, draw N ≈ 200 shots with launch scatter only:
   - P̂ = hits/N;
   - colour = P̂;
   - show the Wilson interval on hover.
   - Cost: about 200 × the binary scan, which is fine in a Web Worker for a 40 × 40 grid.
2. **Nested (two-loop) MC**, the Roy–Oberkampf approach. The outer loop samples or lists the epistemic sets (Cd ∈ {0.33, 0.5, 0.9}; Cl ∈ {floor, low, nominal, high}). The inner loop samples launch scatter. Report the *band* of P maps, as min/max across the outer loop, not one blended P. Blending treats "we don't know Cd" as if it were random shot-to-shot noise, and that is wrong. Calibration removes epistemic error once; shot noise never goes away.

**How to measure the inputs.**
- σ(v) and σ(θ): T1/T2 video of 20 or more shots at one setting (COMPLETENESS T1/T2).
- Wind: the venue is indoor, so wind σ 0.3 m/s is ASSUMED. It stands for HVAC drafts. A pocket anemometer at the field would replace it.

## 4. Sensitivity analysis: which parameter matters most

**What.** Rank the inputs by how much of the scatter in the gate crossing s they cause.
- **Local:** one-at-a-time (OAT) derivatives.
- **Global, regression:** standardised regression coefficients (SRC) on the MC sample.
- **Global, variance-based:** Sobol indices. See Sobol 2001, *Math. Comput. Simul.* 55:271–280, doi 10.1016/S0378-4754(00)00270-6, and Saltelli et al., *Global Sensitivity Analysis: The Primer*, Wiley 2008, doi 10.1002/9780470725184.

**OAT results** (PREDICTED; Δs at the gate, spin representative shot; hood-equivalent = Δs ÷ 409 mm/deg):

| Perturbation (label of the input) | Δs, backspin | Δs, twin | Outcome flip? |
|---|---|---|---|
| θ +0.1° (ASSUMED step) | +41 mm | +39 mm | — |
| v +1 % (ASSUMED) | −77 mm (≈ −0.19°) | −85 mm | — |
| Cd 0.33 (params_lit low) | −244 mm | −252 mm | floor hit |
| Cd 0.9 (params_lit high) | +497 mm (≈ 1.2°) | +520 mm | roof hit |
| ρ 1.0 / 1.25 (params_lit range) | −230 / +55 mm | similar | hit / — |
| mass 23.5 / 27.5 g (params_lit range) | +82 / −126 mm | similar | lip hit / floor hit |
| R ±0.5 mm (aero only) | ±38 mm | similar | — |
| wind 0.3 m/s head / tail (ASSUMED) | +138 / −133 mm (±0.33°) | ±130 mm | hits |
| Cl set low / high (params_lit) | −261 / +400 mm | n/a (twin has Cl = 0) | floor / roof hit |
| Cl set floor | miss | n/a | miss |
| Cl cap +10 % | +66 mm | n/a | — |
| S 1.03 or 1.27 | **0 mm** | n/a | — |
| k 0.005 … 0.15 1/s, or k = 0.30·β·\|v\| with β 0.02–0.05 | **0 mm** | n/a | — |
| g 9.78 instead of 9.80665 (§5) | −11 mm | similar | — |
| carried air + added mass (§5) | −70 mm | −67 mm | — |

**SRC ranking** (PREDICTED, from the N = 3000 MC):
- Spin: θ +0.66, wind −0.55, v −0.49, d +0.34, Cl factor +0.27, Cd factor +0.15, HIVE x +0.14, mass −0.11, R +0.08, tilt −0.05; h, pivot and S ≈ 0.
- Twin: θ, v, wind, d, Cd.
- Caveat: the SRC² values sum to about 1.2 while R² ≈ 0.995. The sample is restricted to shots that cross the gate, so the inputs are slightly correlated. **Use the SRC as a ranking, not as variance shares.**
- Binned first-order indices on the *clean* yes/no indicator come out ≤ 0.03 for every input. The clean band is non-monotone and its scatter comes from interactions between inputs. Use s as the response, not the yes/no indicator.

**Conclusions** (PREDICTED, at the ASSUMED σ):
1. **Hood-angle repeatability dominates.** σθ 0.4° alone spreads s by about 160 mm, wider than the clean band.
2. Wind/draft, v repeatability and stand-off d come next.
3. The epistemic aero uncertainty (Cd 0.33–0.9, Cl sets) shifts the window by 0.6–1.2°. It is the largest *bias*, but it is removable with one calibration session.
4. **Spin magnitude and spin decay do not matter at all while Cl stays capped** (S ≥ 0.71). The Cl(S) cap is ASSUMED: real Cl may keep rising past S ≈ 0.7, or may fall, as in inverse Magnus (§6). So this result is a model-form artefact until Cl(S) is measured. It must not be read as "spin does not matter". It also must not be read as "more spin is better".

**How to add Sobol properly.** Use the Saltelli/Jansen estimator with N(p + 2) runs (p ≈ 14 inputs, N ≈ 4096, about 66 k shots). That takes a few seconds with the vectorised RK4. Apply it to s, with a separate index set for each epistemic aero case.

## 5. Small model-form terms not in the ODE

Each row is in mm at the gate for the representative shots, PREDICTED unless labelled otherwise.

| Effect | Equation to add | Numbers | Size: spin / twin | In model? | Measure? |
|---|---|---|---|---|---|
| Buoyancy + carried internal air + added mass | m_eff·dv/dt = −(m − ρV_out)·g ẑ + F_aero. Inertia m_eff = m + m_air,in + C_m·ρV with C_m = 0.5 (potential flow). V_out is the outer-sphere volume because the shell carries its internal air. | V = 1.87e-4 m³; ρV ≈ 0.225 g (derived). The added-mass coefficient 0.5 is for steady potential flow, so it is approximate for an unsteady wake (CONFIRMED textbook value, e.g. Brennen 1982, "A review of added mass and fluid inertial forces", NCEL CR 82.010). Inertia factor ×1.0135 in total (derived). | −70 / −67 mm (≈ −0.17°); added mass alone −24 mm | No | No direct test. It is absorbed into the fitted Cd when the fit uses the real ball. |
| Local g | g(lat, alt) from the WGS84 normal-gravity formula | Venue g ≈ 9.78–9.83 (CONFIRMED range for Earth's surface); repo uses 9.80665 (ASSUMED) | 9.78 gives −11 mm | Constant g only | Look it up for the venue. |
| Coriolis | a = −2 Ω × v, Ω = 7.29e-5 rad/s | ≈ 1.0e-3 m/s² (derived) | ≈ 0.5 mm over 1 s flight | No | Not needed. |
| Air density at the venue | ρ = p/(R_d T)·(1 − 0.378 e/p) | params_lit 1.0–1.25 (ASSUMED range) | ρ 1.0 gives −230 mm and a hit | Fixed ρ | Barometer + thermometer on the day. Then Cd·ρ, not Cd alone, is what the shot depends on. |
| Spin-decay form k ∝ \|v\| vs constant k | dω/dt = −β·(ρπR⁴/I)… (params_lit β model) | β 0.009–0.05 (ASSUMED) | 0 mm while Cl is capped | Constant k (JS: exp(−kt)) | T3 spin-down video. Low priority. |

- Buoyancy, internal air and added mass together are about −70 mm. That is roughly a third of the clean band, so it is **worth one line in the ODE**. It also moves the meaning of any fitted Cd.
- The other three terms are below 15 mm and can be ignored.

## 6. How credible CFD would be (Re 5e3–4.7e4, 1.8 mm perforated shell)

**Regime** (derived): Re = 2Rv/ν with ν 1.5e-5 m²/s.

| Speed | 1.1 m/s (apex) | 3 m/s | 7 m/s | 10 m/s |
|---|---|---|---|---|
| Re | 5.2e3 | 1.4e4 | 3.3e4 | 4.7e4 |

- This whole range is **subcritical** for a smooth sphere: the laminar boundary layer separates and the wake is turbulent. The drag crisis is near 2–3e5.
- The holes and the shell edges add disturbances of their own. Perforated balls cannot be assumed to behave like smooth spheres. Rossmann 2007 measured Wiffle Cd 0.36–1.05 (CONFIRMED for the Wiffle ball; not a POLLEN value; see LITERATURE_SYNTHESIS).

**Method credibility:**

| Method | Credible here? | Evidence (CONFIRMED) |
|---|---|---|
| Steady RANS | **No** for Cl and spin; at best a rough Cd | Constantinescu & Squires (AIAA J 2003, Re 1e4): URANS captures the shedding frequency, but its amplitude is "much reduced" relative to LES/DES. The subcritical wake is unsteady, and its separation point sets both Cd and Cl. |
| DES / hybrid | Yes for Cd, Cl and St with ≥ 3 meshes | Constantinescu & Squires 2004, *Phys. Fluids* 16(5):1449–1466, doi 10.1063/1.1688325 |
| LES | Yes; the standard tool for spinning spheres at Re 1e4 | Muto, Tsubokura & Oshima 2012, *Phys. Fluids* 24:014102, doi 10.1063/1.3673571. Rotating sphere at Re 1e4 (smooth): Cl 0.167 at Γ 0.2, 0.301 at Γ 1.0. Yun, Kim & Choi 2006, *Phys. Fluids* 18 (2006) (Re 3700, 1e4). |
| LBM (cumulant, LES-like) | Yes, given GPU code and validation on a smooth sphere first | Geier, Pasquali & Schönherr 2017, *J. Comput. Phys.* 348:889–898, doi 10.1016/j.jcp.2017.07.004 (sphere up to Re 1e6, including the drag crisis) |
| DNS | Feasible only at the low end (Re ≲ 1e4) | Rodríguez et al. 2011, *JFM* 679:262–287, doi 10.1017/jfm.2011.136 (Re 3700, St 0.215). Poon et al. 2014, *JFM* 759:751–781, doi 10.1017/jfm.2014.570 (rotating sphere, Re ≤ 1000). Golf-ball DNS (Smith, Beratlis, Balaras, Squires & Tsunoda 2010, *Int. J. Heat Fluid Flow*) needed about 1e8–1e9 points. |

**Why POLLEN is harder than a smooth sphere** (derived from geometry plus the sources):
- The shell is about 1.8 mm thick (CAD reading, params_lit: 1.78 mm). Hole diameter is not recorded in the repo; about 10 mm is ASSUMED here.
  - Resolving the flow *through* the holes, and the jets that issue from the inner cavity, needs at least 10 cells across each hole lip.
  - That means cells of roughly 0.2 mm, against a 71 mm ball, plus a wake of about 10 D.
  - So about 1e8 cells for LES (derived order of magnitude).
- It also needs a rotating frame or a moving mesh, plus several spin ratios, and each run must be converged in time (at least 20 shedding cycles).
- Inverse Magnus is possible: Cl < 0 near transition was seen on smooth spheres in a wind tunnel at Re 0.6–2.6e5. See Kim, Choi, Park & Yoo 2014, *JFM* 754:R2, doi 10.1017/jfm.2014.428. Holes could trigger transition locally at much lower Re. **This is why S ≥ 0.71 giving a capped Cl is only ASSUMED.**
- **Validation data:** there are **no published POLLEN Cd or Cl measurements** (derived from the literature search; see LITERATURE_SYNTHESIS).
  - Closest: Lindsey 2025, a 26-hole pickleball, Cd about 0.45 (taped holes Cd about 0.43).
  - Creer 2023: pickleball CFD that the authors themselves declare invalid.
  - Ito & Kamijima 2025: CFD of a perforated ball at Re 6.6e3–5.3e4.
  - **None of these are POLLEN facts.**

**Verdict.** **Measure first, CFD later** (as in EXTRA_SOURCES §4.8). One afternoon of video (§7) pins Cd to about ±5 % and the sign and size of Cl, which already beats any unvalidated CFD. Use CFD only to interpolate Cl(S, Re) after the video data exist. If it is done:
1. Use LES or cumulant LBM, never steady RANS.
2. Pass the six acceptance checks in EXTRA_SOURCES §4.8:
   - a smooth sphere reproduces textbook Cd;
   - a grid study with at least 3 meshes;
   - domain/blockage sensitivity is reported;
   - the non-spinning POLLEN result is compared with measured Cd before any spinning run is trusted.

## 7. Cheap experiments to measure Cd, Cl and k on real POLLEN

Signal size compared with what video can resolve (derived):

| Quantity | At 7 m/s | At 1.5 m/s |
|---|---|---|
| Drag acceleration (Cd 0.5) | 2.33 m/s² | 0.11 m/s² |
| Magnus acceleration (Cl 0.25) | 1.17 m/s² | 0.05 m/s² |

Fit precision for a quadratic fit to the track with σ_pos 2 mm (derived, least squares):

| Camera | Track length | σ(acceleration) |
|---|---|---|
| 240 fps | 0.3 s | 0.070 m/s² |
| 240 fps | 0.6 s | 0.012 m/s² |
| 120 fps | 0.6 s | 0.018 m/s² |
| 960 fps | 0.2 s | 0.097 m/s² |

So **240 fps over at least 0.3 s on the fast part of the flight measures Cd to about ±3 % and Cl to about ±6 % per shot**. Near the apex the signal is about 20 times smaller, so near-apex Cl needs about 10 or more shots averaged (derived).

| Test | What it gives | Numbers for this ball (derived/PREDICTED) | Kit | Source for the method |
|---|---|---|---|---|
| **T1 shot video** (side-on, perpendicular, scale bar in the flight plane) | Cd·ρ, Cl at the shot's real (v, S), launch σ | see fit table above | Phone at 240 fps on a tripod, Tracker autotracker | Cross & Lindsey 2014, *Sports Eng.* 17:89–96, doi 10.1007/s12283-013-0141-9 (tennis Cd 0.507 ± 0.024 with two stations 6.4 m apart; a tennis value, not POLLEN). Tracker: https://opensourcephysics.github.io/tracker-website/ |
| **Drop test, no spin** | Cd from the fall-time deficit | Terminal velocity v_t = 14.35 m/s (Cd 0.5). 3 m drop: 0.801 s vs 0.782 s in vacuum, z deficit 146 mm. Cd 0.6 instead of 0.5 adds +3.8 ms and 26.6 mm. 2 m drop: −64 mm; 4 m drop: −260 mm | Stairwell or balcony at 3–4 m, 240 fps phone, release by a paper-clip trigger | Standard terminal-velocity fit |
| **Spinning drop** (spin about a horizontal axis, e.g. off a spinning wheel edge) | Sign and size of Cl at low Re, which is the inverse-Magnus check | Lateral deflection at 3 m, ω 200 rad/s: 70 mm (Cl nominal), 42 mm (low), 9 mm (floor), 112 mm (high). At 4 m: 124 / 74 / 14 / 198 mm | Same, plus a camera on the deflection plane | — |
| **Ball spin from video** | S at release, decay k | At v 10, S 1, the ball spins at about 2690 rpm (45 rev/s), which gives 5.3 frames per revolution at 240 fps. That is enough with a marker stripe; use 960 fps slow motion for the first 0.2 s. | Marker-pen stripe on the ball | Nathan et al. arXiv physics/0605041 (motion capture at 700 fps; Cl linear in S for a baseball, not POLLEN) |
| **Wheel rpm** | The rpm the shooter actually delivers, and the v/u ratio when combined with T1 | 2800–4700 rpm wheel range (user) | FTC SDK `DcMotorEx.getVelocity()` from the motor encoder, logged per shot; or a photo/laser tachometer with reflective tape | FTC SDK documentation |
| **Radar / speed gun** | Exit v only | — | A cheap radar gun reads speed, **not spin**. It is useful for σ(v). | — |
| **Spin-down (T3)** | k | Low priority: 0 mm effect while Cl is capped (§4) | Spin the ball on the wheel, release it into a free fall, film the marker | COMPLETENESS T3 |

**Order** (cheapest first, largest effect first):
1. Weigh the ball and record ρ on the day.
2. No-spin drop test (Cd).
3. T1 shot video, 20 shots (Cd, Cl, σθ, σv).
4. Spinning drop (sign of Cl at low Re).
5. Wheel rpm logging.
6. Spin-down (only if Cl turns out not to be capped).

## 8. What to change in the model (summary)

| # | Change | Why | Size (PREDICTED) |
|---|---|---|---|
| 1 | Show P-maps (Wilson) in the explorer, with nested MC for the epistemic bands | Binary windows hide that P ≤ about 0.3 at the ASSUMED σ | P 0.29 spin / 0.31 twin |
| 2 | Add buoyancy, internal air and added mass (m_eff, net weight) | Larger than every term except the main inputs | −70 / −67 mm |
| 3 | Measure Cd and Cl(S) before any CFD; drop the S-saturation assumption once data exist | Largest bias; S and k are invisible while Cl is capped | 0.6–1.2° shift in the window |
| 4 | Keep RK4 at dt 2 ms; add a dt-halving regression test | Error about 3 µm | — |
| 5 | Optional: event root for exact contact; segment–polygon entry test | Closes the ≤ 5 µm sag and the one-step entry gap | ≤ 5 µm |
| 6 | Sobol indices on s for each epistemic aero case | SRC sums are not variance shares | — |
