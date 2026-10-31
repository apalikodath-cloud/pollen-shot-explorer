# AI ENGINEERING HANDOFF — POLLEN Magnus-Effect Reverse-Side HIVE Shooter

(Copied verbatim from the user's handoff, 2026-10-30.)

Project: FIRST Tech Challenge 2026–2027, BIOBUZZ™ presented by RTX
Team context: FTC Team 207, Critical Mass
Prepared: October 30, 2026
Status: Research / physics feasibility / early prototype concept; NOT an experimentally validated shooter design
Current scope: POLLEN ONLY; one powered 98 mm flywheel; a fixed hood or optionally an unpowered upper roller. Do not redesign this as a dual-powered-flywheel shooter without explicit permission.

## 0. Read this first — the user's actual idea
The user wants to score POLLEN into the upward-facing CELL of the center HIVE regardless of which stable position the HIVE is tipped into, preferably without driving around to the normally favorable shooting side.

This is NOT just a conventional lob shot. The user says the unfavorable-side HIVE geometry blocks or greatly constrains a normal gravity-only arc. Their proposed solution is to launch POLLEN on a high, strongly backspinning trajectory whose flight path is noticeably reshaped by aerodynamic spin effects near and after the apex, potentially creating the extra clearance and entry direction needed to reach the tilted CELL. They report observing both:
1. A ball's airborne path apparently changing in a beneficial way when backspinning.
2. A spinning ball contacting the HIVE edge/interior and then being redirected into the CELL.

Keep these as two separate hypotheses: (A) an air-only Magnus-assisted entry and (B) a Magnus-assisted flight followed by a spin-dependent rim/interior collision. Do not assume either is already quantitatively proven. The user's observations are real experimental reports, but the relative contributions are unmeasured.

The user describes the conceptual mechanism as: launch in an arc → near the top of the arc the ball has little upward/downward velocity → substantial retained backspin bends the subsequent trajectory enough to enter the HIVE from the unfavorable side. Investigate this concept rigorously; do not dismiss it just because its informal explanation of the apex is imprecise.

### Crucial physics clarification
At the apex of an ordinary projectile path, vertical velocity is zero, not total speed; the ball usually retains horizontal speed. Spin itself does not impart a new translational impulse or cause a sudden hook at the apex. The aerodynamic Magnus force depends on spin and relative airspeed throughout flight. For backspin in a 2D vertical plane, the lift direction is approximately perpendicular to the velocity: upward for horizontal motion; during ascent it also has a rearward component, and during descent a forward component. It usually counteracts downward acceleration. Therefore, whether it enables the desired HIVE entry is an inverse-trajectory and collision-clearance calculation, not something to assert from intuition.

If the user's desired 'hook' means horizontal reversal in mid-air, test for it explicitly; do not confuse reduced horizontal progress, altered apex, different descent path, and rim-induced changes with genuine reversal. Check other possible effects (e.g., sidespin) only after evaluating pure backspin within scope.

## 1. Official game context — verified on October 30, 2026
Authority: Official BIOBUZZ competition manual, TU07 (updated October 29, 2026), especially §§9.6, 9.8, 10.5.1, and rule G417. Use the current game resources page to check later Team Updates.
- The center HIVE structure holds separate alliance HIVES. Each alliance HIVE comprises two CELLS and rotates between two stable tipped positions. Only one CELL faces upward at a time.
- Teams LAUNCH POLLEN or NECTAR into the upward-facing CELL to make a HIVE tip. This is the permitted way to trigger a tip; the robot must not otherwise manipulate the HIVE (G417).
- CELL opening: approximately 20 in (50.8 cm) wide × 14 in (35.6 cm) tall. CELL depth: approximately 12 in (30.5 cm). Use official drawings/CAD for the orientation, lip, actual surfaces, and center-of-ball clearance, not just these dimensions.
- HIVE frame pivot axes: about 43.95 in (111.65 cm) above tiles. CELLS: approximately 18.8 in (47.8 cm) apart per official diagram; verify precise datum in CAD.
- POLLEN are approximately 2.8 in (7.1 cm) diameter, yellow Gopher ResisDent™ polyethylene, perforated and not perfectly spherical; dimensions vary by piece.
- The user's target is the HIVE/CELL, not the FLOWER or GARDEN. Preserve the HIVE flipping scenario in all diagrams and simulations.

Official scoring-element vendor: AndyMark BIOBUZZ scoring elements, SKU am-5851_yellow. AndyMark lists the 2.8 in POLLEN at 0.055 lb, approximately 24.95 g; use ~0.025 kg for first-pass work, then weigh actual balls. The AndyMark product page links a POLLEN STEP model and a layout print.

Do not hardcode unverified HIVE tilt angle or CELL lip geometry. Previous chat contained approximate tilt/height numbers which were not independently established by the latest manual text. Get official HIVE CAD or measure the actual field element before using precise entry-angle claims.

## 2. Fixed scope and known user-provided dimensions
| Item | Current value / policy | Confidence |
|---|---|---|
| Projectile | POLLEN only | Fixed scope |
| Nominal ball diameter | 71 mm; radius 35.5 mm | Official nominal; actual variation |
| Ball mass | ~25 g | AndyMark nominal; measure samples |
| Ball shape | Hollow perforated polyethylene, not perfectly spherical | Official / physical description |
| Powered shooter wheel | ONE 98 mm diameter flywheel (radius 49 mm) | User-specified proposed wheel |
| Upper contact | Fixed curved hood or one passive/unpowered roller | User's permitted options |
| Ball compression | 4 mm previously discussed as a candidate/working value | User context; not experimentally optimized |
| Launch angle | Adjustable is a reasonable candidate; exact range not chosen | Concept, not final CAD |
| Shooter CAD | Not yet provided | Unknown geometry |
| Real exit speed | Unknown | Must measure |
| Real exit spin | Unknown | Must measure |
| Air drag/lift for actual POLLEN | Unknown | Must calibrate or bound |
| Ability to score from all field locations | Not established | Research objective |

The proposed one-powered-wheel constraint matters. A dual-powered-wheel system may independently tune spin and speed, but it is not the requested mechanism. A free-spinning top roller is not the same thing as a stationary hood: its angular acceleration, inertia, and bearing friction can substantially change spin transfer. Investigate both alternatives fairly, without assuming a passive roller always creates the required backspin.

## 3. What needs to be answered
Primary research question: Does a physically achievable combination of POLLEN launch velocity, backspin, launch elevation, launch position, and HIVE orientation allow reliable entry into the upward-facing HIVE CELL from the otherwise unfavorable side using one powered 98 mm flywheel with a fixed hood or passive upper roller?

Subquestions:
1. With no spin, which locations and release angles permit clear entry into each HIVE orientation? Determine the genuinely geometry-blocked region instead of assuming all reverse-side shots are impossible.
2. With realistic backspin and drag, how much can the trajectory change at the apex, by the time it reaches the HIVE, and within the collision-free opening corridor?
3. What minimum spin / dimensionless spin parameter is needed for a previously infeasible shot to become geometrically feasible, at each distance and launch height? If there is no feasible spin within realistic physics, report it.
4. Can the single-powered-wheel shooter actually impart that spin while still providing the required translation speed? Include wheel RPM drop and slip.
5. If clear, air-only entry is infeasible, can legal rim/interior contacts reliably cause an entry? Under what incidence angles, friction, restitution and pre-impact spin conditions?
6. How robust are the proposed shots to ball-to-ball variation, aim errors, battery sag, wind, and HIVE orientation/position tolerances?
7. What fraction of legal robot shooting locations are feasible under realistic hardware limits? "Anywhere on the field" is a goal to map, not a result to presume.

Success metric: successful upward-facing CELL entries and ultimately tips, not maximum flywheel RPM, apex height, backspin RPM, or just touching the HIVE.

## 4. Physical models to implement
### 4A. Free-flight: 2D first, 3D second
SI units. World x horizontal toward the target, z upward, y sideways. v_rel = v - v_wind:
- m dv/dt = m g + F_drag + F_Magnus
- F_drag = -0.5 rho Cd(Re,...) A |v_rel| v_rel
- F_Magnus = 0.5 rho Cl(Re,S,...) A |v_rel|^2 n_M, n_M = unit(omega × v_rel)
- A = pi R^2, S = |omega| R / max(|v_rel|, eps)
Sign convention: backspin on a forward-moving ball gives upward F_Magnus; unit-test it. As |v_rel|→0 both forces → 0 (regularize; no fictitious force from S singularity).
Optional spin decay d(omega)/dt = -k_spin omega. Constant Cd + parametric Cl(S) acceptable for sensitivity but labeled uncalibrated; add Cl ceilings; perforated POLLEN ≠ pickleball.
Scale check: m 0.025 kg, R 0.0355 m, rho 1.225; at 5 m/s and Cl=0.20, Magnus accel ≈ 0.49 m/s² (~5% g).
Baselines: vacuum; gravity+drag; +backspin; +contact. Compare same exit speed/angle with and without spin; also optimize all launch variables.

### 4B. Apex and the "spin hook"
Locate apex (v_z=0); record (x,z,vx,vz,omega,S,F_M). Pure backspin gives upward lift at apex, not a turn. Compare spin-induced changes across the whole approach (max difference may not be at apex). 3D spin-axis tilt / sidespin only after the 2D backspin baseline; never silently substitute sidespin.

### 4C. Single flywheel + stationary hood — ideal kinematics
R_w=0.049, R_b≈0.0355. No-slip at both contacts, symmetric: v_exit ≈ R_w Ω_w,exit / 2, |ω_ball| ≈ v_exit/R_b ⇒ S_exit≈1. Raising RPM raises both speed and spin. Full model: flywheel inertia, RPM drop, torque, bearing loss; ball I_b (hollow shell, not 2/5 mR²); N(δ) compression law, contact path, μ, contact time, hysteresis; 4 mm nominal vs variable compression; exit-angle effects; empirical RPM→(v,spin) map. Reference: Dean Brettle, Flywheel Shooter Analysis.

### 4D. Single flywheel + passive upper roller
I_top dΩ_top/dt = torque_from_ball − bearing_drag. Compare initial roller speed, inertia, bearing resistance, material, diameter. Free roller can spin up and reduce spin differential vs a fixed hood. Do not treat it as a driven wheel. Deliver evidence-based hood-vs-roller comparison in achievable (v, ω), consistency, losses, ball damage.

### 4E. HIVE geometry and scoring collision mechanics
Use official HIVE/CELL CAD where possible. Model both stable orientations, mouth plane and lip, sidewalls, rim thickness, floor, exterior obstructions, central frame; finite ball radius (configuration-space inflation); robot/shooter interference.
Two success channels: (1) clean air-only entry; (2) spin-assisted contact entry via permitted rim/interior impact (restitution + Coulomb friction, spin change, bounce-outs, repeated contacts). Recheck legality vs manual/Team Updates/Q&A; the robot may not actuate the HIVE (G417).

## 5. Do NOT repeat these earlier mistakes
- Do not reinterpret the task as shooting into a FLOWER. Target = pivoting center HIVE, upward-facing CELL.
- Do not replace the idea with "just launch high and drop it in." Test whether spin curvature matters quantitatively.
- No dual-powered flywheel as default.
- Do not assert the ball is stationary at apex (only v_z≈0).
- Do not say rotational inertia turns into directional travel at apex.
- Do not claim more backspin always improves entry.
- Do not treat pickleball coefficients as POLLEN measurements.
- Do not treat v_exit=u_wheel/2 as universal.
- Do not reuse earlier speculative shot numbers (70° / 6.72 m/s / 2 m) as proven.
- Do not claim 30° HIVE tilt or a precise entry angle unless confirmed from official CAD/diagram.
- Do not infer repeatability from one successful shot.

## 6. Recommended workflow
Phase 1 lock HIVE geometry (official CAD; frame; favorable/unfavorable sides; no-spin drag-only reachability).
Phase 2 inverse ballistic/Magnus solver (ODE, Cd, Cl(Re,S), spin decay, wind; search [v, elev, spin, release]; plots; feasibility maps for both HIVE states, clean vs rim-assisted; predicted vs validated labels).
Phase 3 single-flywheel launch envelope (hood, then passive roller); compare required vs achievable; quantify any gap; prototype adjustable gap, elevation, feeding, ball markings.
Phase 4 empirical validation (slow-mo side-on, spin RPM, motor RPM, battery, outcomes; multiple balls, distances, both orientations; fit Cd/Cl/decay, e/μ; CIs).
Phase 5 decide hood vs roller; feasible subset of locations if not "anywhere".

## 7. Deliverables
1. Feasibility verdict with quantified physics and explicit confidence/unknowns.
2. Derivations with units.
3. HIVE cross-section and entry corridor, both tip states, sourced.
4. Reproducible Python trajectory solver: no spin, backspin, impact-assisted.
5. Required spin-vs-speed-vs-range table; 2D/3D feasibility maps.
6. One-powered-wheel launch model; hood vs passive roller; RPM, compression, achievable spin.
7. Prototype test matrix and procedure with pass/fail criteria.
8. Clear answer on "score from anywhere"; feasible region and limiting physics.
Immediate next action: official HIVE geometry → minimum trajectory change required from the unfavorable side. Do not optimize compression/RPM before knowing the required exit state.

## 8. Sources (not proof of POLLEN properties)
1. FIRST BIOBUZZ Competition Manual TU07 (2026-10-29): https://ftc-resources.firstinspires.org/ftc/game/cm-html/BIOBUZZ%20Competition%20Manual%20-%20TU07.htm
2. FIRST game resources: https://ftc-resources.firstinspires.org/ftc/game
3. AndyMark BIOBUZZ scoring elements: https://andymark.com/products/biobuzz-scoring-elements?variant=47194281148588
4. Dean Brettle, Flywheel Shooter Analysis: https://docs.carlmontrobotics.org/jupyter_notebooks/files/FlywheelShooter.html
5. Emond, Sun & Swartz (2024), Pickleball Flight Dynamics, IJRSS: https://doi.org/10.30827/ijrss.32618
6. Steyn et al. (2025), Third Shot Drop in Pickleball, IJSSC: https://doi.org/10.1177/17479541251365200
7. Van Wyk, Smith & Lyu (2026), Pickleball Ball Mechanical Behaviour, ISEA: https://doi.org/10.7273/000008181

Bottom line: the Magnus-assisted reverse-side HIVE shot is a testable hypothesis, not a solved mechanism.
