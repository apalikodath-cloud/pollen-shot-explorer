# Aerodynamic effects on the POLLEN shot (research lens "aero")

Written 2026-10-30 for PM-001. Scope: aerodynamics of perforated and smooth spheres at Re 1e4-6e4 and spin ratio
S 0-1.5. It covers drag against Re and spin, the drag crisis, reverse Magnus, changes in lift sign and size with S,
unsteady side forces ("knuckling") on non-spinning holed balls, hole count, size and orientation, and Cd(Re) fits
that can go into code. It also covers some small air effects that the model leaves out: wind and drafts, air density,
buoyancy and added mass, and spin-axis tilt.

Robot and launch effects (wheel droop, release point, exit scatter) are in `research/effects/launch.md`. The source
tables and grades are in `research/LITERATURE_SYNTHESIS.md` and `research/params_lit.json`, and this file does not
repeat them.

Labels follow HANDOFF section 5:
- **CONFIRMED**: a primary source. A source about another ball is still not a POLLEN fact.
- **user**: a value the user gave.
- **ASSUMED**: an assumption.
- **derived**: my own arithmetic from labelled inputs.
- **PREDICTED**: model output.

No number here is a POLLEN measurement, and nothing here claims the shot repeats. Pickleball, Wiffle,
table-tennis and smooth-sphere numbers are context only. They are not POLLEN coefficients.

## 0. Default case, method and reference shots

**Case (task).**
- Release on the unfavourable (far) side, 1.00 m from the HIVE pivot plane, at height 0.737 m. Pose `pose_pos`, side
  `neg`, tilt 30 deg (CAD).
- Backspin S = 1 at exit.
- Wheel: 98 mm, with grip v/u = 0.42 (ASSUMED, explorer default). So 1 m/s of exit speed = 464 wheel rpm (derived).
- Air: rho 1.20 kg/m^3 (ASSUMED).
- Ball: m 24.95 g, R 35.5 mm, giving A = 3.96e-3 m^2 (derived). kinematic viscosity nu = 1.5e-5 m^2/s (ASSUMED).
- Re = vD/nu = 4730 x v (derived). So 6-10 m/s gives Re 2.8e4-4.7e4 (derived).

**Method.**
- A scratch planar RK4 (dt 2 ms) uses the same equations as `viz/explorer/solver.js`, with Cd(Re,S), Cl(S,Re), wind and
  an extra normal force made pluggable. It is not committed.
- Classification uses the repo's `src/hive.classify_detail(..., "pose_pos", "neg", frame="hive")`.
- Nominal aero is `data/aero_params.json`: Cd 0.48, Cl = min(0.35 S, 0.25), k 0.05 1/s.
- `launch.md` uses the `params_lit.json` nominal (Cd 0.50, k 0.03). So its reference shots differ, but the sensitivities
  agree in size.
- "dx" is the change in where the ball centre crosses z = 1.51 m on the way down, along the shot axis. 1.51 m is the
  mid-mouth height (derived from the lips at 1.357 and 1.666 m). + means farther (deeper).
- Each effect is applied alone.

**Reference shots (all PREDICTED, this model only).**

| Shot | v (m/s) | elev (deg) | wheel rpm (derived) | result | min clearance | apex z | horizontal speed at apex | S at apex | Re at launch / apex | time to z 1.51 |
|---|---|---|---|---|---|---|---|---|---|---|
| R, backspin S = 1 | 7.50 | 78.75 | 3480 | clean | 40.6 mm | 3.22 m | 1.02 m/s | 7.1 | 35,500 / 4,800 | 1.30 s |
| T1, no-spin twin, same launch | 7.50 | 78.75 | 3480 | **miss** (long by 259 mm) | 169 mm | 3.19 m | 1.29 m/s | 0 | 35,500 / 6,100 | 1.29 s |
| T2, no-spin twin, own clean cell | 7.50 | 80.50 | 3480 | clean | 44.7 mm | 3.22 m | 1.10 m/s | 0 | 35,500 / 5,200 | 1.30 s |

On the coarse grid (v step 0.25 m/s, elev step 0.25 deg), the clean cells were:
- S = 1: 28 cells, best clearance 52 mm at 8.75 m/s / 80.5 deg (PREDICTED).
- S = 0: 30 cells, best clearance 61 mm at 8.5 m/s / 82.5 deg (PREDICTED).

Backspin moves the clean band about 1.5-2 deg lower in elevation at the same speed. It does not make the shot easier
here.

**Sensitivities at R (derived from PREDICTED runs):**
- dx/dv = +291 mm per m/s, or 0.63 mm per wheel rpm.
- dx/d(elev) = -145 mm per deg.
- The in-plane margin around R is roughly -35 to +30 mm. Shifts of +/-32 mm stay clean on one side and hit on the other.

So any effect worth more than about 30 mm along x, about 0.1 m/s (50 rpm), or about 0.2 deg is enough to move a
tuned shot out of the window. Most effects below are bigger than that, so the real ball must be measured.

## 1. Ranking on this shot

Shifts are PREDICTED at R and use the effect values listed. "Eq. rpm" is the wheel-rpm change that would put the ball
back at the same x (derived).

| # | Effect | Value used (label) | dx at R | Eq. rpm | Result at R | In model? |
|---|---|---|---|---|---|---|
| E4 | Magnus size: Cl floor vs nominal | min(0.02 S, 0.04) (params_lit, B) | +233 mm | +372 | miss | Yes, as a range |
| E6 | Reverse Magnus (worst case, all flight) | Cl = -0.05 | +309 mm | +493 | miss | No (text only) |
| E4 | Magnus size: Cl high | min(0.8 S, 0.4) | -163 mm | -259 | hit roof | Yes, as a range |
| E1 | Drag level: Cd 0.90 | Wiffle/FRC upper end (B/D) | -164 mm | -261 | hit roof | Yes, as a range |
| E8 | Knuckle in-plane force +/-0.15 | Cl-equivalent (params_lit high) | -163 / +157 mm | -/+255 | hit / miss | No |
| E8 | Knuckle sideways (no-spin), C_s 0.15 | constant / wavelength-5.4 m sine | 223 / 136 mm sideways | n/a | outside lateral half-width 0.15 m (ASSUMED) | No |
| E5 | Lift-crisis dip table | `dip_variant` x1.0 / x0.5 | -57 / +104 mm | -92 / +166 | hit / miss | No |
| E10 | Wind 0.5 m/s along the shot | tail / head | +74 / -84 mm | +118 / -135 | hit / hit | No |
| E1 | Drag level: Cd 0.33 / 0.65 | 40-hole pickleball low end / params_lit high | +71 / -72 mm | +113 / -114 | hit / hit | Yes, as a range |
| E3 | Spin-raised drag | +0.12 for S >= 0.6 | -51 mm | -82 | hit | No |
| E2 | Smooth-sphere Cd(Re) (Morrison 2013) | Cd 0.39-0.40 in band | +39 mm | +62 | hit floor | No (constant Cd) |
| E8 | Knuckle in-plane force +/-0.03 | params_lit nominal | -/+32 mm | -/+51 | clean / hit | No |
| E10 | Spin-axis tilt 5 deg (sideways Magnus) | 0.25 x sin 5 deg = 0.022 | about 33 mm sideways | n/a | inside lateral half-width | No |
| E10 | Air density 1.13 instead of 1.20 (warm, high site) | same as Cd x 0.94 | +13 mm | +20 | clean | No |
| E10 | Buoyancy | 0.90 % of weight | +10 mm | +16 | clean | No |
| E2 | Partial drag crisis (Cd 0.48 -> 0.33 between Re 3e4 and 5e4) | what-if | +3 mm at R; +11 to +17 mm at 8.75-9.75 m/s | +5 to +27 | clean | No |
| E7 | Spin decay k from 0.005 to 0.30 1/s | params_lit range | 0 mm (k 1.0: -3 mm) | 0 | clean | Yes |
| E10 | Added mass | 0.45 % inertia | under 5 mm (derived scale) | - | - | No |

Twins at T2 (S = 0, PREDICTED):
- Cd 0.33 / 0.65 / 0.90 gives +80 / -80 / -181 mm.
- Knuckle +/-0.03 gives -32 / +31 mm. Knuckle +/-0.15 gives -159 / +154 mm.
- Wind tail / head gives +74 / -82 mm.
- Buoyancy gives +12 mm.

Drag and wind move a no-spin ball about as much as a spinning one, or slightly more. The large entries that only apply
with spin are the Cl entries: floor, high, dip and reverse.

## 2. The effects

### E1. Drag level of a perforated ball (subcritical)

**What it is.** Pressure drag when separation is laminar. For a smooth sphere Cd is almost flat at Re 1e3-2e5. Holes
let air vent through the shell and can change separation, so a holed ball can have more or less drag than a smooth one.

**Best numbers.**
- Smooth sphere: Cd about 0.445 for 1e3 <= Re <= 2.6e5 (CONFIRMED, Morrison 2013 handout,
  https://pages.mtu.edu/~fmorriso/cm310/DataCorrelationsforExaminations2013.pdf).
- Stationary-sphere subcritical Cd about 0.52 (CONFIRMED, Kim et al. 2014 abstract, https://doi.org/10.1017/jfm.2014.428).
- 26-hole indoor pickleball in free flight: 0.45 (SD 0.09). Taping the holes gives about 0.43, and a modified control
  ball reads 0.59-0.985 (CONFIRMED for that ball, Lindsey 2025, grade C).
- 40-hole outdoor pickleball: 0.30 +/- 0.02 (Steyn 2025, n = 6) and 0.33 (Lindsey).
- Wiffle: 0.36-1.05 depending on orientation and Re, rising towards about 1 at the lowest Re (CONFIRMED,
  Rossmann & Rau 2007, https://doi.org/10.1119/1.2787013).
- 2017 FRC FUEL drop test: about 0.88 (D).

POLLEN range in use: 0.33 / 0.50 / 0.90 (params_lit, ASSUMED from these).

**Size on this shot.** Each +0.1 of Cd is about -45 to -50 mm at R, or about -75 rpm (PREDICTED, derived from the
0.33 / 0.65 / 0.90 runs). This is the largest single uncertainty for which the model already has a range.

**In model?** Yes, as a constant Cd.

**How to add Re dependence.** See E2.

**How to measure on POLLEN.**
1. Fire a no-spin ball straight up. Use equal wheel speeds, or toss it with a hand launcher.
2. Film it at 240 fps or more next to a measured scale. Fit the launch speed from the first 0.1 s of track, then fit
   the apex height h.
3. With drag, h = ln(1 + Q Cd v^2 / g) / (2 Q Cd), where Q = rho A / (2m) = 0.0952 1/m (derived).
   - At v 7.5 m/s, Cd 0.48 gives h 2.55 m and Cd 0.58 gives 2.49 m (derived), so 0.1 of Cd is about 55 mm of apex.
   - The launch speed must be known to about 0.3 % (dh/dv is about 0.68 m per m/s, derived), so fit v and Cd together
     from the whole track.
4. Do it at 2-3 speeds (Re 3e4-4.5e4) and in at least 2 ball orientations.

A plain drop test is weak. The terminal speed is about 14.6 m/s (derived, Cd 0.48), so a 3 m drop loses only a few
percent of its speed to drag.

### E2. Re dependence and the drag crisis

**What it is.** At a critical Re the boundary layer turns turbulent before it separates. The wake shrinks and Cd falls
sharply (the drag crisis). Roughness, dimples and holes move that critical Re lower.

**Best numbers.**
- Smooth sphere: the crisis is near Re 3e5 (CONFIRMED, Morrison 2013).
- Correlation that can go into code (CONFIRMED form, Morrison 2013 eq. 4):

  `Cd = 24/Re + 2.6 (Re/5)/(1 + (Re/5)^1.52) + 0.411 (Re/263000)^-7.94 / (1 + (Re/263000)^-8) + 0.25 (Re/1e6)/(1 + Re/1e6)`

  - The handout prints 236,000 in the third denominator. With that value the formula gives Cd about 0.90 at Re 3.5e4,
    which disagrees with the handout's own flat 0.445. Use 263,000 in both places (derived check). It then gives 0.39-0.41
    over Re 5e3-1e5 (derived).
- Dimples and roughness lower the critical Re to about 4e4-1e5 (Bearman & Harvey 1976, Aeronautical Quarterly
  27:112-122, secondary). Roughness generally lowers it (Achenbach 1974, JFM 65:113, values not retrieved).
- Vilumbrales 2024: Re_c >= 49,600 for roughness k/d <= 0.01 (B, https://arxiv.org/abs/2407.01748).
- POLLEN's hole edge is wall depth / D = 1.78 / 71, about 0.025 (derived). That is beyond Vilumbrales' fitted range,
  so a lowered Re_c near the top of the shot band (4e4-5e4) cannot be ruled out (ASSUMED).
- The low 0.30-0.33 of the 40-hole pickleball at Re 4.7e4-6.1e4 hints at partial crisis behaviour in a holed ball
  (ASSUMED inference; pickleball is not POLLEN).

**Size on this shot.**
- Morrison smooth Cd(Re) instead of 0.48 gives +39 mm at R and +43 mm at 8.75-9.75 m/s. That turns those cells from
  clean to hitting the floor (PREDICTED). Almost all of this is the level (0.40 vs 0.48), not the Re shape.
- A what-if partial crisis (0.48 below Re 3e4, falling to 0.33 above 5e4) gives only +3 mm at R. At 8.75-9.75 m/s it
  gives +11 to +17 mm (PREDICTED), because only the first 0.1-0.2 s of flight is above Re 3e4.
- Apex Re is only about 5e3, so most of the flight is well subcritical (PREDICTED).

**In model?** No. Cd is constant.

**How to add.** Use `Cd(Re) = Cd_sub + (Cd_post - Cd_sub) * smoothstep((Re - Re1)/(Re2 - Re1))`, with Cd_sub fitted
(E1), and Cd_post and Re1/Re2 fitted from E1 tests at 2-3 speeds. Re is computed from |v_rel| at every RK4 stage.

**How to measure.** The E1 apex fit at 6, 8 and 10 m/s. If Cd at 10 m/s is lower than at 6 m/s by more than the fit
error, there is Re dependence.

### E3. Spin-dependent drag

**What it is.** Rotation thickens the retreating-side wake, and that usually raises Cd.

**Best numbers.**
- Muto LES: Cd 0.474 at S 0.2 and 0.661 at S 1.0 (B; the authors flag disagreement in the subcritical range,
  https://doi.org/10.1063/1.3673571).
- Ito CFD: 0.45-0.62 (B).
- Zhou et al. 2022: spin raises Cd for spin ratio < 10, at Re 610-3472 (CONFIRMED for that range,
  https://doi.org/10.3390/w14172593).

**Size on this shot.** +0.12 for S >= 0.6 gives -51 mm, which hits (PREDICTED). Along this flight S rises from 1 to
about 7 (PREDICTED), so any spin-drag term is fully on for the whole flight.

**In model?** No.

**How to add.** `Cd = Cd0(Re) + dCd * min(S / S_sat, 1)`, with dCd 0 / 0.08 / 0.18 (ASSUMED range from Muto/Ito) and
S_sat about 0.6.

**How to measure.**
1. Repeat the vertical E1 test with a backspin hood (S about 1, measured by video of a marked ball).
2. For a straight-up shot, Magnus is horizontal. So the apex-height difference against the no-spin twin gives dCd
   alone: about 55 mm of apex per 0.1 (derived).

### E4. Magnus lift size and saturation

**What it is.** Backspin gives a force normal to v, Cl(S). For smooth spheres Cl rises with S and then levels off.
On holed balls lift can be much weaker, because vented flow and asymmetric separation fight the rotation-driven
asymmetry.

**Best numbers.**
- params_lit Cl sets: floor min(0.02 S, 0.04), low (0.20, 0.15), nominal (0.35, 0.25), high (0.8, 0.4) (B).
- Plateau values for smooth spheres: about 0.33 for a polystyrene ball (Cross 2012) and 0.35-0.40 (Vilumbrales).
- Smooth-sphere CFD limit about 0.37 for spin ratio 1-12 (CONFIRMED, Zhou 2022).
- Pickleball: Van Wyk 0.0124 + 0.466 S, giving 0.27 at S 0.56 (B); Steyn 0.195 S for S <= 0.3 (B).
- Cross & Lindsey 2017 report significant lift at very low spin for a pickleball (CONFIRMED for that ball,
  https://doi.org/10.1088/1361-6404/aa6e44).

**Size on this shot.**
- floor gives +233 mm, which misses. low gives +106 mm, which misses. high gives -163 mm, which hits the roof
  (PREDICTED).
- Raising only the cap to 0.33 gives -86 mm.
- The no-spin twin at the same launch lands 259 mm farther (PREDICTED).

At this shot, backspin mainly pulls the ball back towards the shooter on the way up. Lift is normal to v and v is
nearly vertical, so the force acts in -x. It does not "float" the ball, and more spin is not always better here. More
Cl just moves the clean band to a lower elevation.

**In model?** Yes, as capped linear. Above S 0.71 the cap holds, so every S >= 1 shot behaves the same (see
docs/03_clean_entry.md).

**How to add.** Nothing new, but fit c1 and Cl_max to the real ball. A table form is in E5.

**How to measure. This is the most valuable POLLEN test.**
1. Use the same wheel speeds and hood angle, with S = 1 (hood) against S = 0 (equal wheels).
2. Film both shots from the side and measure the x where each crosses z 1.51 m on the way down.
3. Read the predicted spin-minus-twin difference:

| Cl set | Predicted difference |
|---|---|
| floor | 26 mm (derived) |
| nominal | 259 mm |
| high | about 420 mm (derived) |

4. Measure exit S from a marked ball at 480 fps or more.
5. Do it at 2 speeds to separate Cl from Cd.

### E5. Lift crisis, Cl sign and size changes with S and Re

**What it is.** In POLLEN's Re band (2.7e4-5.3e4), smooth spheres show a lift crisis. Cl rises with S, dips near
S 0.75-0.9, then recovers. The dip deepens as Re rises.

**Best numbers.**
- Ito & Kamijima 2025 CFD table (B) and Sakai/Miyazaki wind tunnel valleys of 0.09-0.21 (B), as listed in
  `params_lit.json` `Cl.dip_variant`: Cl 0.29 at S 0.5, 0.18 at S 0.88, 0.30 at S 1.1.
- Conti 2026 match fits: the dip reaches about 0.17 at Re 4.5e4 (derived, C).
- Sareen 2024: lift tracks the advancing-side separation angle, and the shear-layer instability at low Re "may mean"
  inverse Magnus appears below their tested range (CONFIRMED wording, highlights only, IJHFF 109:109501).

**Size on this shot.**
- dip x1.0 gives -57 mm, which hits. dip x0.5 (a venting guess) gives +104 mm, which misses (PREDICTED).
- S starts at 1 and climbs past 1.1 within about 0.1 s (PREDICTED). So the trough matters only if the real exit S is
  0.75-0.95. Below about 0.6, the S ramp crosses the trough early in flight.

**In model?** No. src cannot read the table (LITERATURE_SYNTHESIS section 4).

**How to add.** `Cl = scale(Re) * interp(S, S_pts, Cl_pts)`, with scale 0.5-1.0, and optionally a second table at
Re 2e4 blended linearly with Re.

**How to measure.** Run the E4 spin-against-twin test at three hood settings (exit S about 0.5, 0.85 and 1.2). A
smaller Delta x at S 0.85 than at both 0.5 and 1.2 shows the trough.

### E6. Reverse (negative) Magnus

**What it is.** Near the critical Re, the advancing side goes turbulent first and separates later. The net force then
reverses, so backspin pushes the ball down and forward.

**Best numbers.**
- Smooth sphere: mainly at Re 1.25e5-4.5e5 with rotation under 10 Hz; soccer ball at 9.6e4-2.48e5 (CONFIRMED,
  Kray 2008 thesis, https://dspace.ub.uni-siegen.de/handle/ubsi/404). A negative Magnus effect over a wide range of
  Re and S is in Kray, Franke & Frank 2012, J. Wind Eng. Ind. Aerodyn. 110.
- Kim 2014: inverse Magnus at Re >= about 4.6e4 only for small S (< about 0.6), mostly 1e5-2e5 (B). The tests covered
  0.6e5 < Re < 1.8e5, 0 < S < 2 (secondary review). Mechanism: https://doi.org/10.1017/jfm.2014.428.
- Muto 2012: LES at 2e5 (B).
- Wiffle: side Cl changes sign near Re 5.5e4 with one-sided slots (CONFIRMED for Wiffle, Rossmann & Rau 2007).

POLLEN needs Re >= 4.6e4, which means v >= 9.7 m/s (derived), and S < 0.6. With the S = 1 hood both conditions are
never true at once. S only rises as the ball slows (PREDICTED).

**Size on this shot.** Worst case, Cl = -0.05 for the whole flight, gives +309 mm, which misses (PREDICTED). Realistic
case at the default S = 1: about 0 mm. It matters only for a low-spin shot near 10 m/s, and then only for the first
0.05-0.1 s (derived).

**In model?** No. The text only says "run Cl = 0".

**How to add.** `if Re > Re_rev and S < S_rev: Cl = -Cl_rev`, with Re_rev 4.6e4, S_rev 0.5 and Cl_rev 0-0.1
(ASSUMED). Use a smooth blend to avoid RK4 chatter.

**How to measure.** A low-spin (S about 0.3) against no-spin pair at 10 m/s. If the low-spin ball lands farther than
its twin, lift is negative.

### E7. Spin decay

**What it is.** A viscous torque slows the spin, so dw/dt = -k w.

**Best numbers.** params_lit range: k 0.005 / 0.03 / 0.15 1/s. That is 0.6 % / 3.5 % / 17 % spin loss over 1.2 s
(derived, B). Golf-like beta and Ito C_M scaling give 0.011-0.023 1/s (B).

**Size on this shot.**
- 0 mm for k from 0.005 to 0.30 1/s, and -3 mm at k 1.0 (PREDICTED). S starts at 1, already above the cap (0.71), and
  rises as v falls, so Cl stays on its cap.
- With exit S 0.5: +0.6 mm (k 0.05), +2.9 mm (0.3) and +9.7 mm (1.0) (PREDICTED).

**In model?** Yes. It is low priority for this shot. It would matter only with an uncapped, still-rising Cl(S).

**How to measure.** Count the rotation of a marked ball near launch and near the mouth in the same video. The
difference over 1.3 s gives k.

### E8. Knuckling and unsteady side forces (non-spinning holed ball)

**What it is.** A ball with little or no spin has an asymmetric wake that wanders. Holes or seams fix an asymmetric
separation, which gives a steady or slowly changing side force. With spin, the force direction rotates once per
revolution and largely averages out.

**Best numbers.**
- Darbois Texier, Cohen, Quéré, Clanet 2016, "Physics of knuckleballs", New J. Phys. 18:073027
  (https://doi.org/10.1088/1367-2630/18/7/073027), all CONFIRMED for their balls:
  - zigzag wavelength `lambda = 2 pi D sqrt(4 rho_b / (3 rho))`;
  - lift fluctuations are largest near the drag crisis;
  - "knuckleballs occur for balls without seams";
  - their test balls turned "less than a tenth of a rotation".
- For POLLEN: rho_b = m / (pi D^3 / 6) = 133 kg/m^3 (derived), so lambda is about 5.4 m (derived). The flight path to
  the mouth is about 4.5 m (PREDICTED), so L/lambda is about 0.8. That is within one zigzag, where the sideways
  deviation grows about as (x/D)^2.
- Wiffle steady side Cl is -0.15 to +0.145 depending on hole orientation and Re (CONFIRMED for Wiffle).
- params_lit `non_magnus_hole_force`: 0 / 0.03 / 0.15 Cl-equivalent (B).
- Team 254 2017 (FRC FUEL, a holed ball):
  - "Despite no dead spots, lack of spin produced inaccuracy";
  - an early test "incorrectly suggested ball spin was bad", and later prototypes "showed spin was good"
    (CONFIRMED quotes, https://media.team254.com/2017/09/964207d8-technicalBinder2017.pdf, pp. 15-16).

  This is an FRC ball and a different shot, so these are not POLLEN numbers.

**Size on this shot (PREDICTED).**
- In-plane, with S = 1 at R: +/-0.03 gives -/+32 mm (clean / hit), and +/-0.15 gives -/+160 mm.
- In-plane, no-spin twin T2: about the same, -32 / +31 and -159 / +154 mm.
- Sideways (out of plane), no-spin, with C_s 0.03 / 0.15 held constant: 45 / 223 mm.
- The same with a random-phase sine at wavelength 5.4 m: up to 27 / 136 mm.
- The lateral half-width is 0.10-0.2185 m (ASSUMED, `W_LAT`), so C_s near 0.15 alone could cause a miss.
- For the spinning ball the per-revolution average should be near 0. There is no POLLEN number for the leftover part,
  and it should not be used as a repeatability claim.

**In model?** No.

**How to add.**
- Shot-to-shot random force for the no-spin case: `a_n = Q |v|^2 C_s e_perp(phi)`, with C_s drawn per shot from
  [0, C_s_max] and phi uniform. Option: modulate by sin(2 pi s / lambda + phase) along the path length s.
- With spin, scale C_s by `1 / (1 + (omega tau)^2)` (ASSUMED, tau about 0.05 s) so that it averages out.
- The output should be a scatter band, not a single trajectory.

**How to measure.**
1. Fire 20 or more no-spin shots and 20 or more S = 1 shots at the same setting.
2. Film from behind (lateral) and from the side (along).
3. Compare the spreads, and log ball orientation at launch (holes marked).
4. Record the spread values. Do not turn them into a repeatability claim before the user approves.

### E9. Hole count, size and orientation

**What it is.**
- More, smaller and uniform holes behave more like a rough smooth sphere.
- Few, large or one-sided holes (Wiffle) give steady side forces and orientation-dependent Cd.
- Hole edges act as trips that can bring the crisis forward (E2).

**Best numbers.**
- Wiffle (8 oblong holes on one hemisphere): Cd 0.36-1.05 and side Cl +/-0.15 by orientation (CONFIRMED for Wiffle).
- 26-hole indoor pickleball Cd about 0.45 against 40-hole outdoor 0.30-0.33 (C/B).
- A 36-hole pickleball preprint (Research Square, 2025-26) reports less dispersion than 40 holes. Only the title and a
  search snippet were read, so it is not used.
- Team 254 blamed hole orientation for veer and used spin against it (CONFIRMED quote, above).
- POLLEN has 26 near-uniform holes (CAD/manual). That is closer to the indoor pickleball than to Wiffle (ASSUMED), so a
  side force smaller than Wiffle's is expected (params_lit note).

**Size on this shot.** It enters through E1, E2 and E8. The Wiffle-like upper end (Cd 0.90, C_s 0.15) gives -164 mm
in-plane and up to 223 mm sideways (PREDICTED).

**In model?** No, except through the Cd range.

**How to add.** Make Cd and C_s depend on launch orientation (holes facing the flow, or a web between holes), drawn
per shot.

**How to measure.** Repeat E1 and E8 with the ball loaded hole-forward against web-forward, using an indexed loading
mark.

### E10. Other small air effects the model leaves out

- **Wind and drafts (HVAC, venue doors, other robots' fans).**
  - Air moving 0.5 m/s along the shot gives +74 mm (tail) / -84 mm (head) at R, about 120-135 rpm equivalent
    (PREDICTED). The no-spin twin is the same.
  - 0.5 m/s is ASSUMED, a typical indoor draft and not measured.
  - Add it by using `v_rel = v - w_air` in the drag and lift terms (the scratch model did this).
  - Measure with a handheld anemometer at the shooting spot and at 2-3 m height during practice.
- **Air density.**
  - rho changes about 1 % per 3 deg C and about 1 % per 100 m of altitude (standard atmosphere, derived).
  - rho 1.13 gives +13 mm (PREDICTED).
  - Add rho as an input. Measure with a thermometer and the venue altitude.
- **Buoyancy.** rho V g / (m g) = 0.90 % of weight (derived), giving +10 mm (PREDICTED). Add `g_eff = g (1 - rho V / m)`.
- **Added mass.** 0.5 rho V / m = 0.45 % (derived). It slightly slows all accelerations, a few mm at most (derived
  scale). Add `m_eff = m + 0.5 rho V` in the drag and lift terms only.
- **Spin-axis tilt.**
  - If the hood or wheels give the ball a tilted spin axis, part of the Magnus force goes sideways:
    `C_side = Cl sin(tilt)`.
  - 5 deg tilt gives C_side 0.022 and about 33 mm sideways (derived from the E8 lateral run, scaled linearly).
  - Not modelled in the planar solver. In `src/flight.py` 3D it is just a tilted omega vector.
  - Measure the axis by filming a ball with a painted equator from behind.
- **Unsteady history (Basset) force.** Expected to be negligible for a gas-borne ball with rho_b / rho about 110
  (ASSUMED from the usual particle-dynamics scaling). It is not quantified here.

## 3. What this changes for the model (suggestions, not done)

1. Measure Cd (E1) and the spin-against-twin Delta x (E4) on real POLLEN before tuning shots. Together they span about
   -165 to +310 mm at R, against a window of about +/-30 mm (PREDICTED).
2. Add wind / v_rel, rho, and the buoyancy g_eff as inputs. They are cheap, and wind alone is about 80 mm per 0.5 m/s.
3. Add Cl as a table with a Re-blend (E5) and an optional reverse-Magnus switch (E6). Keep the floor set as the
   pessimistic case.
4. Add a per-shot stochastic side force (E8), at least for the no-spin twin, and report a scatter band.
5. Leave spin decay as is for S >= 1 shots (E7, PREDICTED 0 mm).
6. Use the Morrison correlation only as a shape check, with 263,000 in both places. Its level (0.40) is below the
   pickleball and Wiffle data for holed balls.

## 4. Sources added by this lens

The rest of the sources are in `params_lit.json`.

- Darbois Texier B., Cohen C., Quéré D., Clanet C. (2016) Physics of knuckleballs. New J. Phys. 18:073027.
  https://doi.org/10.1088/1367-2630/18/7/073027
- Morrison F.A. (2013) Data correlation for drag coefficient for sphere (MTU course handout).
  https://pages.mtu.edu/~fmorriso/cm310/DataCorrelationsforExaminations2013.pdf
- Kray T. (2008) Dissertation, Univ. Siegen. https://dspace.ub.uni-siegen.de/handle/ubsi/404 ; Kray T., Franke J.,
  Frank W. (2012) J. Wind Eng. Ind. Aerodyn. 110 (abstract only).
- Kim J., Choi H., Park H., Yoo J.Y. (2014) Inverse Magnus effect on a rotating sphere: when and why. JFM 754 R2.
  https://doi.org/10.1017/jfm.2014.428 (abstract and secondary review).
- Zhou et al. (2022) Water 14:2593. https://doi.org/10.3390/w14172593
- Sareen, Hourigan, Thompson (2024) Int. J. Heat Fluid Flow 109:109501 (highlights only; PDF unreachable).
- Bearman P.W., Harvey J.K. (1976) Golf ball aerodynamics. Aeronautical Quarterly 27:112-122 (secondary).
- Achenbach E. (1974) JFM 65:113-125 (cited for direction only; values not retrieved).
- Team 254 (2017) Technical binder, pp. 15-16. https://media.team254.com/2017/09/964207d8-technicalBinder2017.pdf

Not read, and not used: the Lyu/Smith/Smith ISEA 2026 pickleball trajectory paper (metadata only), the 36-hole
pickleball preprint (title only), and the Sareen and Kharlamov PDFs (connection refused).
