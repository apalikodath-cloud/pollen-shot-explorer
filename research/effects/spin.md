# Spin effects: what the POLLEN shot model may be missing

Lens: **spin**. Written 2026-10-30 for PM-001 (FTC POLLEN, backspin/Magnus shooter).
Scope: spin-decay law, spin-axis tilt (sidespin), gyro spin, exit-direction skew, CG offset / wobble,
non-sphericity / diameter / compression, hood vs passive-roller exit (v/u, S, slip), holes under the
contact patch, and published FRC/FTC/VEX shooter measurements.

Labels (HANDOFF §5): **CONFIRMED** (CAD/manual/measured source), **user**, **ASSUMED**, **derived**
(arithmetic from labelled inputs), **PREDICTED** (model output). Pickleball and other-ball numbers are
**analogues, not POLLEN facts**. No repeatability claim is made anywhere here: every shot number is
one deterministic model run.

## 0. Default case and how the numbers were made

| Item | Value | Label |
|---|---|---|
| Side / distance / release height | unfavourable (far) side, d = 1.0 m from HIVE pivot plane, h = 0.737 m | user/task default |
| HIVE mouth (pose_pos) lower lip / upper lip (x, z) | (0.49073, 1.35654) / (0.31204, 1.66603) m; mouth line 357.4 mm | CONFIRMED (CAD) |
| Lateral cell slack at floor | cell 0.508 m, ball R 0.0355 m → about ±218 mm (less near the roof) | CONFIRMED inputs, derived slack |
| Aero set | rho 1.2, m 24.95 g, R 35.5 mm, Cd 0.5, Cl = min(0.35 S, 0.25), k 0.03 /s | ASSUMED (params_lit nominal) |
| Backspin aim (S = 1) | v 9.0 m/s, elevation 80.7°, 2421 ball rpm | PREDICTED (data/spec_nominal.csv) |
| **No-spin twin** | v 8.9 m/s, elevation 83.1° | PREDICTED (data/spec_nominal.csv) |
| Wheel rpm for the backspin aim (98 mm wheel) | 3508 / 4176 / 5847 rpm at v/u = 0.50 / 0.42 / 0.30 | derived (v/u is grade C, ASSUMED) |

Base runs (PREDICTED, nominal aero):

| Run | Result | s on mouth (mm from upper lip) | min clearance | crossing t | apex z |
|---|---|---|---|---|---|
| Backspin S = 1, 9.0 m/s, 80.7° | clean | 225.9 | 48.1 mm | 1.579 s | 4.18 m |
| No-spin twin, 8.9 m/s, 83.1° | clean | 213.0 | 48.2 mm | 1.554 s | 4.105 m |
| No spin at the backspin aim (9.0, 80.7°) | miss | 1559 | - | - | - |

Sensitivities at the backspin aim (PREDICTED): about **+450 mm along the mouth per +1 m/s** (+22.5 mm per
+0.05 m/s) and about **-550 mm per +1° elevation** (+0.5° hits the outer roof). The no-spin twin has
similar slopes. These slopes are the yardstick for every effect below.

Tool: a scratch 3D RK4 script (dt 1 ms) in the session scratchpad, **not in the repo**, plus
`src/launcher.py` for the exit model. Treat the shot numbers as indicative model outputs, not tests.
Note that the ball is moving at the apex in every run (horizontal velocity is non-zero); nothing here
treats it as stationary.

---

## 1. Spin-decay law (torque vs S and Re, not a constant k)

**What it is.** Air friction and pressure on the surface exert a torque that slows the spin. The
current model uses `dω/dt = -k ω` with constant k. The literature says the torque depends on the
surface speed, on the flight speed and on roughness, so k is not constant.

**Best numbers and sources.**

| Law | Numbers | Applies to | Label |
|---|---|---|---|
| Golf (Smits & Smith; Tavares et al.), as summarised by A. Nathan, "spindown" note | `I dω/dt = -R ρ A C_M v²`, `C_M = β S`, β ≈ 0.010-0.012; equivalently `dω/dt = -λ ω v` with λ ≈ 2.0-2.5e-5 per m | golf, Re 9.6e4-2.5e5, S ≤ 0.27 | CONFIRMED for golf, analogue for POLLEN |
| Ito & Kamijima 2025, smooth 40 mm sphere LES, DOI 10.11308/tjsst.17.25 (see `research/papers/ito2025.md`) | torque nearly independent of V at fixed ω, about ω^1.6-1.7; fit C_m ≈ 0.0131 SP^1.73; normalisation ambiguous by ×2 | smooth sphere, Re 6.6e3-5.3e4 | CONFIRMED (CFD), analogue |
| James & Haake 2008, Engineering of Sport 7 vol 2 pp 165-170 | decay linear in (initial spin × speed); constant is ball-specific, set mostly by moment of inertia, also roughness and boundary-layer regime | several sports balls | CONFIRMED (qualitative) |
| Haake et al. 2007 (tennis) | tennis-ball spin decay "over six times" golf | felt-covered ball | CONFIRMED, analogue |
| `research/params_lit.json` spin_decay_k | 0.005 / 0.03 / 0.15 /s (low/nom/high); β-model 0.009/0.02/0.05 | sweep range | ASSUMED (COMPLETENESS suggests grade D) |

Scaled to POLLEN at ω0 = 254 rad/s (2421 rpm), I ≈ 1.98e-5 kg m²:

| Estimate | Torque | k_eff = T/(Iω) | Label |
|---|---|---|---|
| Ito smooth-sphere scaling, both normalisations | 5.6e-5 to 1.1e-4 N m | 0.011-0.022 /s | derived |
| Rotating-disk boundary-layer analogue, C_M = 3.87/√Re_ω, Re_ω ≈ 21 340 | 5.9e-5 N m | ≈ 0.012 /s | derived from an ASSUMED analogue |
| Holes as "paddles": T ≈ 26 · ½ρ(ωR)² · Cd_eff · A_hole · R, A_hole 8.8e-5 m² | - | ≈ 0.08 /s (Cd_eff 0.1), ≈ 0.24 /s (Cd_eff 0.3) | derived from ASSUMED Cd_eff |
| Interior air (≈ 0.19 g) | negligible inertia | - | derived |

Reading: a smooth sphere gives k of about 0.01-0.02 /s. The 26 holes could raise this by roughly ×4-×20.
The paddle estimate is crude. **Measure it, don't pick it.**

**Size for this shot (PREDICTED).**

| Decay setting | Spin retained at mouth | Change in s |
|---|---|---|
| k = 0 / 0.005 / 0.03 / 0.15 / 0.25 /s | 1.0 / 0.992 / 0.954 / 0.789 / 0.674 | 0.0 mm for all |
| k = 0.5 /s | 0.454 | -0.9 mm |
| β-model 0.009 / 0.02 / 0.05 | 0.983 / 0.962 / 0.908 | 0 mm |
| Power law T = K ω^1.65, T(254) = 5.6e-5 / 1.1e-4 / 5.5e-4 N m | 0.983 / 0.966 / 0.849 | 0 mm |
| Unsaturated test lift law Cl = 0.15 S (cap 0.40), k 0 → 0.03 → 0.15 → 0.25 | - | s 498.5 → 499.3 → 503.5 → 508.2 mm (≈ 10 mm over the range; this aim misses under that law) |

Why it is zero in the nominal set: Cl = min(0.35 S, 0.25) saturates at S ≥ 0.714. S starts at 1 and
*rises* during the climb because v falls faster than ω. Losing even half the spin keeps S above the knee.
**Spin decay matters only as far as dCl/dS above S ≈ 0.7 is non-zero, and that slope is unknown for
POLLEN.** The same saturation hides S itself: sweeping S0 from 0.9 to 1.6 changes s by 0 mm (PREDICTED).
This is not evidence that "more spin is always better" or that spin doesn't matter. It is a property of
an ASSUMED lift law.

**In the model now?** Partly. There is constant-k exponential decay (`src/flight.py _make_rhs`), plus a
β option in params_lit. There is no ω-power law and no roughness/hole term.

**How to add it.**
```
I dω/dt = -T(ω, v),   T = K ω^n + β' R ρ A S v² R      (n ≈ 1.6-1.7; K and β' fitted on POLLEN)
```
Keep k as the fallback. Also sweep the Cl law with a non-zero slope above S = 0.7 (e.g. Cl = 0.15 S capped
0.40, or Ito's tabulated C_L(S, Re)) so that decay has something to act on.

**How to measure on real POLLEN.**
- T3 spin-down: spin a ball on a light drill-axle or air-bearing mount to 2000-3000 rpm, then let it coast
  while a 240-480 fps phone films a marked ball. Fit ω(t) for n and K. The bearing friction must be
  measured on a solid dummy of the same mass and subtracted.
- In flight: film the marked ball at two stations (exit and about 1.5 m up) and get ω1/ω2 over a known Δt.
  This also captures the v-dependent part.

---

## 2. Spin-axis tilt: sidespin from roll misalignment

**What it is.** If the wheel-hood contact chord is rolled by ε about the launch direction (wheel axle
not level, hood twisted, ball riding off-centre), the spin axis tilts by ε. Some of the Magnus force then
points sideways.

**Kinematics (derived).** With no slip at two opposite contacts, ω × (2R n) = u_surface. So the spin axis
is perpendicular to both n (contact line) and u. A roll ε of n about v0 rolls the spin axis by ε, which
gives a sidespin fraction of sin ε. Nathan (SABR 2018) describes spin efficiency as transverse/total
spin. A tilted backspin axis is still fully transverse, so Magnus magnitude is unchanged and only its
direction turns.

**Size for this shot (PREDICTED, nominal aero; lateral y at the mouth plane):**

| Tilt ε | 2° | 5° | 10° | 20° |
|---|---|---|---|---|
| Lateral y | 19 mm | 47 mm | 94 mm | 186 mm |
| Change in s | ≈ 0 | +5 mm | +21 mm | +82 mm (clearance 9 mm) |

That is about **9.4 mm sideways per degree** of tilt. The lateral slack is about ±218 mm at the floor
(CONFIRMED geometry, derived slack) and narrower near the roof. A tilt of a few degrees is tolerable, but
20° uses most of the margin. The no-spin twin has no tilt effect by construction; its lateral error
comes only from the exit direction (section 4).

**In the model now?** No. The flight model is planar, and the spin axis is fixed perpendicular to the
shot plane.

**How to add it.** Use a 3D state with an ω vector:
```
F_M = ½ ρ A Cl(S⊥) v² · (ω × v)/|ω × v|,   S⊥ = |ω × v| R / v²
ω0 = ω0 · (cos ε · ŷ_back + sin ε · ẑ_side)     (rotation of the backspin axis about v0)
```
Assume the ω direction is constant in flight unless measured otherwise (see section 5 on precession).

**How to measure.**
- Put a stripe (equator line) on the ball and film the exit with an overhead or oblique camera at
  240+ fps. The stripe plane gives the spin axis, read to about ±2-3°.
- Statically, check that the wheel axle is level against the hood with a digital angle gauge. Also check
  that the ball's contact track is centred on the hood width, using chalk or marker transfer on the hood.

---

## 3. Gyro spin, and the Cl(S) convention in the code

**What it is.** Gyro spin is the spin component along the velocity (a "bullet" spin). It produces no
Magnus force (Nathan, SABR 2018: gyrospin gives no movement). It appears when the wheel axle is skewed
(yawed) relative to the exit direction. Sakai & Kitade 2017 (four-roller machine, J-STAGE, see
EXTRA_SOURCES #25) observed more lateral scatter on gyro shots (CONFIRMED, analogue machine).

**Size for this shot (PREDICTED):**

| Gyro angle | 3° | 10° | 30° |
|---|---|---|---|
| Lateral y | 1.8 mm | 6.2 mm | 19.8 mm (s -3.3 mm) |

About **0.6 mm per degree**: small. It is small because the transverse part falls only as cos γ
and Cl is saturated.

**Code issue (derived from reading `src/flight.py _aero`).** The 3D path computes S from the total |ω|,
not from the transverse component. With gyro spin present this overcounts S and the Magnus force.
- While Cl is saturated (the nominal set) the results are identical. The scratch runs confirm
  identical outputs with both conventions.
- Under any unsaturated lift law it would bias the result.
- Fix: `S⊥ = |ω × v| R / v²` and the force direction `unit(ω × v)`. Add a unit test where pure gyro
  spin (ω ∥ v) gives zero lift.

**How to measure.** The same striped-ball camera as section 2, but the view must be along the flight
path: a camera behind or under the shooter looking up the trajectory. A gyro component shows as a stripe
spinning in the image plane.

---

## 4. Exit-direction skew: the largest lateral term found

**What it is.** If the wheel axle is skewed by γ about the contact normal, the surface speed at the
contact is rotated by γ, so the ball leaves rotated sideways by up to γ. This is an upper bound: side
rails or hood walls can redirect it. The same skew also creates the gyro component of section 3, but
the direction error is far larger than the gyro force effect.

**Size for this shot (PREDICTED):**

| Exit yaw | 0.25° | 1.0° |
|---|---|---|
| Lateral y, backspin | 52.8 mm | 211 mm |
| Lateral y, no-spin twin | - | 206 mm |

About **210 mm per degree**, against about ±218 mm of slack.
- A 1° exit skew therefore uses the whole margin.
- By contrast, a robot heading error about the vertical axis moves the lateral landing point only by
  about v · cos(80.7°) · t ≈ 40 mm per degree (derived), because the shot is near-vertical.
- Exit-direction yaw is about the launch axis frame, so it maps almost one-to-one into lateral position.

**In the model now?** No (planar).

**How to add it.** Rotate v0 by γ about the contact normal n before integrating. Also rotate ω0
consistently, which gives the gyro fraction sin γ:
```
v0' = Rot(n, γ) v0,   ω0' = Rot(n, γ) ω0
```

**How to measure.**
- Statically: sight along the axle with a straightedge against the hood centreline, aiming for γ < 0.25°
  (about 0.4 mm over 100 mm).
- Dynamically: an overhead camera, or a target sheet 1-2 m up, to get the lateral exit angle.
- Do several shots, but do not quote a spread from one shot (HANDOFF §5).

---

## 5. Mass / CG offset (wobble)

**What it is.** A moulded perforated shell can have uneven wall thickness, which puts the centre of mass
a distance e from the geometric centre.

**Effects (derived):**
- **Torque in the launcher.** The squeeze forces pass through the geometric centre, so they make no
  torque about it. About the CG the inertial term e × m·a (m·a ≈ 9.6 N during the launch) changes spin by
  at most about 1-3 % for e of a few tenths of a mm. In full no-slip rolling it vanishes, because the
  kinematics fix both v and ω.
- **Position wobble.** In flight the geometric centre orbits the CG at radius e, which is sub-mm.
- **Precession.** The aerodynamic torque about the CG is about 3.6e-5 N m (derived for an assumed
  e ≈ 0.5 mm). Against L = Iω ≈ 5e-3 kg m²/s it gives at most about 0.5° of axis drift over the flight,
  and it averages out as the ball spins. Small next to section 2.

**In the model now?** No. **Add?** Not needed unless measured e > 1 mm. Then add the precession term
`dL/dt = r_CG × F_aero` to the 3D state.

**How to measure.**
- Float the ball in water with a few holes taped, or roll it slowly down a shallow incline and see
  whether it settles to the same face every time.
- Spin it on two knife-edges or a fine axle at several orientations and check for a preferred rest
  position. A preferred face means e is significant.
- Weigh at least 10 balls (0.01 g scale) to see the mass range. params_lit: 24.95 g nominal, 23.5-27.5 g
  range (ASSUMED/literature).

---

## 6. Non-sphericity, diameter and compression variation

**What it is.**
- Ball diameter, out-of-round and stiffness change the squeeze δ between wheel and hood. That changes
  the contact radius `r_c = R_b - λδ/2` (src/launcher.py) and the normal force, i.e. grip.
- In flight, out-of-round adds a small aerodynamic asymmetry ("knuckle" side force) that the model does
  not have.

**Analogue numbers (CONFIRMED for pickleball, NOT POLLEN):** USA Pickleball Equipment Standards Manual
(2021), 2.D.3:
- diameter 2.87-2.97 in
- out-of-round "shall not be greater than +/-0.020 inch (0.51 mm)"
- weight 22.1-26.5 g
- bounce 30-34 in from 78 in

POLLEN's own tolerances are unknown.

**Size for this shot (PREDICTED, `src/launcher.py hood_nominal`, ASSUMED contact parameters; δ 3.5 / 4.0
/ 4.5 mm, i.e. ±0.5 mm about the pickleball out-of-round analogue):**

| Wheel rpm | Regime | v_exit | Spin |
|---|---|---|---|
| 3000 | rolling | 7.005 / 6.996 / 6.988 m/s | S 1.052 / 1.060 / 1.068; 1981 / 1994 / 2006 rpm |
| 3500 | rolling | 8.177 / 8.169 / 8.161 m/s (±0.01 m/s ≈ ±4 mm on the mouth) | 2313 / 2328 / 2343 rpm (±0.65 %) |
| 4000 | partly slipping (wheel slip 2.17 / 0.95 / 0.0) | 8.356 / 8.909 / 9.332 m/s | - |
| 4500 | grip-limited | 8.356 / 8.909 / 9.422 m/s (about ±0.5 m/s ≈ ±230 mm on the mouth) | - |

- **Rolling regime:** diameter and squeeze variation are small, well inside the ±0.05 m/s window the
  default case needs (PREDICTED twin window: ±0.05 m/s, ±0.1°).
- **Grip-limited regime:** they dominate and are far outside that window. `hood_slick` behaves nearly the
  same as `hood_nominal` (PREDICTED).
- Practical reading: **stay in the rolling regime** (enough squeeze and grip for the rpm used). The
  default aim (v 9.0 m/s) sits above HOOD_V_MAX 8.9 m/s in the current launcher table, so it is near or
  in the slipping regime. That is a concern to verify, not a conclusion.

**In the model now?** Partly. `src/launcher.py` has squeeze δ, contact radius and slip, and configs
`hood_soft_ball` / `hood_stiff_ball_8mm`. There is no per-ball δ distribution and no out-of-round aero term.

**How to add it.** Sample δ = δ0 + Δd/2 per shot from the measured diameter distribution, and stiffness
from the measured compression, then run `hood_model`. Report v_exit and spin as distributions (no-spin
twin alongside).

**How to measure.**
- Calipers on 3 orthogonal axes per ball (avoiding holes), on at least 10 balls. Report max-min per ball
  and the spread of the mean.
- Compression: force at 3-5 mm squeeze between plates (a kitchen scale under a screw press works).
- Run each ball 3-5 times through the shooter with light gates or 240 fps video at fixed rpm.

---

## 7. Single flywheel + fixed hood vs passive roller: v/u, spin ratio, slip, compression

**What it is.** The exit speed and spin depend on how the second surface (fixed hood or free/passive
roller) moves and on whether the ball rolls or slips.

**Best numbers and sources.**

| Source | Finding | Label |
|---|---|---|
| Pedersen 2026, FRC 449 whitepaper (`pedersen2026` in repo) | `V_bf = (r_w1 + G r_w2)/2 · ω_w1f`, `ω_bf = (r_w1 - G r_w2)/(2 r_b) · ω_w1f`. Fixed hood: r_w2 term = 0, so v = u/2 and ω = u/(2r_b) (S = 1 at exit for rigid no-slip). The paper says "no slip at exit" is not empirically validated. | CONFIRMED (theory), ASSUMED for POLLEN |
| Sakai & Kitade 2017, four-roller pitching machine | measured v_B = 0.481 · v_Rx | CONFIRMED, analogue (different machine) |
| Drane et al. 2018, Proceedings 2(6):203, DOI 10.3390/proceedings2060203 | high-speed video 2000-3000 fps plus light gates on batting-cage balls in a pitching machine | CONFIRMED method only; numbers **not read** (403 on full text) |
| params_lit `v_over_surface_speed` | 0.30 / 0.42 / 0.50 | ASSUMED (grade C) |
| params_lit S_exit_hood / S_exit_passive_roller | 1.0 / 1.06 / 1.6 and 1.0 / 1.15 / 1.67 | ASSUMED |

**HANDOFF §5:** v_exit = u_wheel/2 is the rigid no-slip limit, **not a universal rule**. Squeeze
(r_c < R_b), hood friction, wrap angle and slip all lower v/u. The 0.30-0.50 range spans a 1.7× wheel-rpm
range for the same aim (3508-5847 rpm, derived).

**Size for this shot (PREDICTED, `src/launcher.py`):**
- `hood_nominal` rolling: S ≈ 1.05-1.07 at the exit; v/u at 3500 rpm ≈ 8.17 / (π·0.098·3500/60) ≈ 0.455
  (derived).
- `roller_nominal_rest` (passive roller from rest): it slips at every rpm from 3000 to 4500. v is limited
  by grip to 4.56-5.48 m/s and S is 1.10-1.11.
- This model's passive roller cannot reach the 9.0 m/s aim. That is a model result under ASSUMED roller
  inertia and friction, not a hardware fact.

**In the model now?** Yes: `hood_model`, `roller_model` and the configs listed in `launcher.configurations()`.
The exit model does not yet feed tilt, skew or a per-ball δ into the 3D flight model.

**How to measure.**
- A 240-480 fps side view of the exit, with a marked ball and a scale in frame, gives v_exit and ω
  directly. Light gates give v.
- A tachometer (optical, reflective tape) gives the wheel rpm before and during the shot, which shows
  wheel droop.
- Compute v/u and S per shot over at least 3 rpm settings.
- Look for slip: S well above the rolling value, or v that stops rising with rpm.
- Chief Delphi thread 448624 gives the same advice (empirical, phone slow-motion plus a scale).

---

## 8. Holes under the contact patch

**What it is.** POLLEN has 26 holes of about 0.40-0.44 in (params_lit, 13-16 % open area, ASSUMED/CAD).
During one launch the wheel and hood contact tracks cross about 2-4.5 holes (derived from the track length
over the contact arc and the hole spacing). Each crossing briefly lowers the contact area and stiffness.
Shot-to-shot grip and the exit v/S then depend on ball orientation. Combined with the paddle torque of
section 1, holes are also the main reason POLLEN decay could exceed smooth-sphere values.

**Size.** Unknown; there is no source. In the rolling regime grip changes have little effect, because
kinematics set v and ω. In the slipping regime they act like the δ sweep of section 6 (up to tenths of a
m/s, PREDICTED order).

**In the model now?** No. **How to add it.** Use an orientation-dependent friction coefficient
μ(θ) = μ0(1 - a·[hole under contact]) sampled per shot. a must come from measurement.

**How to measure.** Feed balls in a fixed orientation versus a random orientation (marked pole) and
compare the spread of v and spin from the exit video.

---

## 9. Published FRC / FTC / VEX shooter measurements

| Source | What it has | Label |
|---|---|---|
| Pedersen 2026 (FRC 449) | theory; explicitly unvalidated no-slip assumption | CONFIRMED theory |
| Chief Delphi 374445, "Hood Compression" (2020 Power Cells) | discussion only; the hood was suspected of drag; **no measured exit speed or spin** | CONFIRMED absence |
| Chief Delphi 448624 | no data; advice to measure empirically (phone slow-mo plus a scale) | CONFIRMED absence |
| Searches for single-wheel hooded shooter spin data (FRC/FTC/VEX) | **none found** | finding of this review |

Conclusion: the robotics literature does not give POLLEN v/u, S or slip. The two-camera exit test of
section 7 is the only route.

---

## 10. Ranking for this shot (PREDICTED, nominal aero, default case)

| Effect | Size at default case | In model? | Priority |
|---|---|---|---|
| Exit-direction skew (axle yaw) | about 210 mm lateral per degree; 1° ≈ whole slack | no | **high**: check alignment first |
| Slip / grip-limited exit (diameter, squeeze, holes) | up to about ±0.5 m/s ≈ ±230 mm along the mouth when slipping; about ±4 mm when rolling | partly | **high**: confirm the regime by measurement |
| Spin-axis tilt (roll) | about 9.4 mm lateral per degree | no | medium |
| Lift slope above S ≈ 0.7 (controls whether S and decay matter at all) | 0 mm under nominal; about 10 mm decay effect under a test unsaturated law | ASSUMED law | medium: measure Cl(S) |
| Spin decay law | 0 mm (nominal); spin retained 0.45-1.0 over k 0-0.5 /s | constant k only | low until Cl(S) is known |
| Gyro spin | about 0.6 mm per degree | no (and code S uses total ω) | low; fix S⊥ anyway |
| CG offset / wobble / precession | sub-mm; ≤ about 0.5° axis drift | no | low |

Every row is a model output or derivation under ASSUMED parameters, with the no-spin twin given where it
applies (sections 0 and 4). None is a measured POLLEN fact.

## 11. Minimal measurement set that resolves most of this

1. **Alignment (static):** axle level and yaw against the hood centreline, with an angle gauge and a
   straightedge. Covers sections 2 and 4.
2. **Ball batch:** at least 10 balls, 3-axis calipers, 0.01 g mass, squeeze-force test. Covers section 6.
3. **Exit video:** 240-480 fps side view plus an overhead view, striped/marked ball, 3 rpm settings, a
   tachometer on the wheel. Gives v/u, S, slip, axis tilt and gyro. Covers sections 2, 3 and 7.
4. **Spin-down (T3):** marked ball on a light axle with dummy-friction subtraction. Covers section 1.
5. **Two-station flight video:** gives Cl(S), Cd and in-flight decay, at v ≈ 3, 6, 9 m/s and S ≈ 0.3,
   0.7, 1.0, 1.5 (Ito-derived plan in `research/papers/ito2025.md`). Covers sections 1 and 10.

## Sources

- Ito K., Kamijima K. (2025). Trans. JSST 17(1):25-31. DOI 10.11308/tjsst.17.25. Notes:
  `research/papers/ito2025.md`.
- Nathan A. M., golf spin-down note (Smits & Smith; Tavares et al. data), and "spin efficiency" (SABR
  2018). http://baseball.physics.illinois.edu/
- James D. M., Haake S. J. (2008). "The spin decay of sports balls in flight." The Engineering of Sport 7,
  vol 2, pp 165-170 (Springer). Abstract via sponet.de.
- Haake S. J., Chadwick S. G., Dignall R. J., Goodwill S. R., Rose P. (2007). Engineering tennis: slowing
  the game down. Sports Engineering 10 (tennis spin decay vs golf).
- Pedersen (2026), FRC Team 449 shooter whitepaper (`pedersen2026` in repo sources).
- Sakai, Kitade (2017), four-roller ball machine, J-STAGE (EXTRA_SOURCES #25).
- Drane P., et al. (2018). "A Study of the Interaction between Batting Cage Baseballs and Pitching
  Machine." Proceedings 2(6):203. DOI 10.3390/proceedings2060203 (full text not read).
- USA Pickleball (2021). Equipment Standards Manual, section 2.D.3 (analogue only).
- Chief Delphi threads 374445 ("Hood Compression") and 448624. https://www.chiefdelphi.com/
- Not used: Dennis et al. 1980 rotating-sphere torque constants (could not verify the coefficients;
  equations behind images).
