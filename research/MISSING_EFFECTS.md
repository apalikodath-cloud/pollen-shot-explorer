# PM-001 missing effects: ranked synthesis of the six effects lenses

Written 2026-10-31. Sources: `research/effects/aero.md`, `env.md`, `launch.md`, `numerics.md`, `spin.md`,
`target.md`. This file ranks every effect those lenses raised by how much it could change the three answers:

- **rpm**: the minimum wheel rpm for a clean far-side shot,
- **angle**: the hood angle that gives it,
- **possible**: whether a clean far-side shot exists at all (inside the hood's grip-limited speed cap),
- plus **scoring** (retention / TIP), which the clean-entry answer does not cover.

Labels follow HANDOFF section 5: CONFIRMED / user / ASSUMED / derived / PREDICTED. Every lens number is a model
output and is **PREDICTED** unless the lens marked it otherwise; numbers this file computed are **derived**. Nothing
here is a POLLEN measurement: zero POLLEN aero, contact or launcher coefficients exist yet. Pickleball, table-tennis
and smooth-sphere coefficients quoted below are not POLLEN facts.

## 0. How to read the sizes

- The lenses use two nominal aero sets, so their reference shots differ (section 4, item 3). Sizes are miss
  distances along the shot at the descending crossing of the mouth height (dx, mm) or aim changes (degrees).
- Clean band at a fixed speed: 0.21-0.43 deg of hood angle wide (PREDICTED, env.md, shots A/B/A0/B0); the aero
  reference shot R (7.5 m/s, 78.75 deg, 3480 rpm) has about +-30 mm of along-shot margin (PREDICTED, aero.md).
- Conversion (PREDICTED, aero.md at R): dx/dtheta = -145 mm per deg, dx/dv = +291 mm per m/s. numerics.md works in
  gate units s (s positive = shorter), ds/dtheta = +409 mm per deg, so |s| is about 2.8 x |dx| (derived).
- Rule of thumb (derived): an effect above about 30 mm flips clean to miss at a fixed aim; it is then an aim
  correction of dx/145 deg, which is a "re-aim" answer change, or a "possible" change if it pushes the required speed
  past the grip cap.
- No-spin twin: wherever a lens ran the twin it is given next to the backspin number. Where the lens did not run one,
  the row says "twin not run". At the aero reference launch the no-spin twin misses 259 mm long; its own clean twin
  needs 80.5 deg (PREDICTED, aero.md). Backspin does not make every effect smaller: a vertical draft moves the
  backspin shot about 2x its twin (env.md).

## 1. Ranked table

In model (updated 2026-10-31 after PM-013 to PM-019 and round 4): what the code holds now. "option" = off by default, so the
default answer is unchanged. The ranking and sizes are the original lens numbers.

Cost: low = under a day in code, medium = days or a bench test, high = new rig, 3D model or CFD.
Action: **model now** (safe in code without new data), **measure first** (code would only pick a number),
**ignore** (with the reason).

| # | Effect | Answers moved | Size (label) | In model | Cost | Action |
|---|---|---|---|---|---|---|
| 1 | Magnus lift level Cl(S): slope c1 and cap Clmax | rpm, angle, possible | Cl floor +233 mm, Cl high -163 mm at R (PREDICTED, aero); s -261 / +400 mm (PREDICTED, numerics). Tuning to a wrong Cl set drops P(clean) from 0.294 to 0.05-0.10 (PREDICTED, numerics); twin P 0.312 [0.296, 0.329] | partial: 3 fixed (c1, Clmax) sets + the 0/0 twin; user Cl(S) table option (PM-016, JS and Python, page Advanced); the hit chance and the best-chance search run Cl low / nominal / high (PM-017); measurement kit fits Cl from a backspin shot beside its no-spin twin (PM-018, `viz/measure`, `src/fit_aero.py`; no POLLEN data yet) | low to model, medium to measure | **measure first** (T1 video, wheel above vs below at equal rpm); keep the 3-set bracket; add a table option (build-next 9) |
| 2 | Cd level | angle, rpm | Cd 0.90: -164 mm; about -45 to -50 mm per 0.1 of Cd (PREDICTED, aero); s +497 (Cd 0.9) / -244 (Cd 0.33) (PREDICTED, numerics); twin not run | yes: constant Cd (default); options Cd(Re) `morrison` and `blend`, Re from the venue air (JS and Python, off by default); measurement kit fits Cd from a drop or a no-spin shot (PM-018; no POLLEN data yet) | low | **measure first** (T1, drop test); add the Re option now (build-next 4) |
| 3 | Grip-limited exit speed and slip (v/u, ball stiffness, squeeze) | possible, rpm | rolling regime: +-0.5 mm squeeze gives +-4 mm; grip-limited: +-230 mm (PREDICTED, spin). Stiffness 10 % gives about 5 % v = 140 mm (A) / 72 mm (B) (PREDICTED, launch). Cap HOOD_V_MAX = 8.9 m/s (PREDICTED, docs/04); spin.md's aim is 9.0 m/s, launch B 9.1 m/s and env B 10.1 m/s are past it | partial: grip-limited flag above the PREDICTED 8.9 m/s cap in the live solver and Python; the recommendation avoids flagged shots; v/u stays ASSUMED 0.42, no slip model | low (flag), medium (T2, T4) | **model now** as a flag (build-next 6); **measure** v/u and S at exit (T2) |
| 4 | Reverse Magnus and lift-crisis dip | possible, angle | worst case +309 mm, realistic about 0: needs v >= 9.7 m/s and S < 0.6 (PREDICTED, aero); dip -57 / +104 mm (PREDICTED, aero); twin has no Magnus term | option, off by default: Cl blends to -Cl_rev (0-0.1, ASSUMED) when Re < 4.6e4 and S < 0.5 (PM-016); the dip only through the Cd `blend` option | low (option), medium (data) | **measure first**; add an off-by-default option (build-next 9). The perforations may move the onset Re (section 4, item 2) |
| 5 | Exit-angle offset (hood angle is not exit angle) and exit scatter | angle | theta_exit = theta_hood + d0 + e; 0.1 deg costs 8 mm (A) / 21 mm (B) (derived, launch). d0 unknown; a decompression kick of "several deg" is not ruled out (derived bound, launch). Any d0 above about 0.2 deg moves the answer out of the 0.21-0.43 deg clean band (derived). Twin not run | input d0 (deg, default 0, ASSUMED) in the live solver (page: Robot moving); sig_th 0.40 deg (ASSUMED) in MC and the page hit chance, a page input since PM-017 (Advanced, "Shot scatter"; the dominant source at the default spot for backspin and twin, PREDICTED); d0 itself unmeasured | medium | **measure first** (T2 exit video, hood angle sweep) |
| 6 | Indoor drafts / wind, horizontal and vertical | angle, possible (bad venue) | along-shot 0.1 / 0.3 m/s: 0.13 / 0.43 deg, 34 / 104 mm (PREDICTED, env). Vertical 0.3 m/s: 0.43 deg backspin vs 0.23 deg twin (PREDICTED, env). 0.5 m/s: +74 / -84 mm (PREDICTED, aero). Wind +-135 mm in s (PREDICTED, numerics). Wind is the second-largest SRC after theta (PREDICTED, numerics) | option, off by default: constant 3D draft (along, up, side) in the live solver and Python; robustness.py horizontal sigma 0.30 m/s; precomputed maps and hit chance are still air | low | **model now** (build-next 2); log venue air speed |
| 7 | Altitude and air density | angle (re-aim per venue), rpm slightly | 1 / 2 km: 0.45 / 0.89 deg, 116 / 232 mm, required rpm about -1 % (PREDICTED, env). Golden, CO (rho 0.974): tolerant min rpm 2830 -> 2803, aim +0.30 deg; twin +0.20 deg (PREDICTED, env). rho 1.0: -230 mm in s (PREDICTED, numerics). Temperature 15-30 C and humidity: <= 0.19 deg, <= 47 mm (PREDICTED, env). rho 1.204 vs 1.20: about 1 mm (derived) | yes: venue air input (temperature, pressure or altitude, RH) in the live solver; default still air rho 1.2041 (derived); precomputed maps keep 1.20 | low | **model now**: venue rho input (build-next 1) |
| 8 | Flywheel recovery between shots, droop, battery | rpm (effective), angle for rapid fire | droop 8.5 % (PREDICTED, docs/04). 50 ticks/s feed gate about 107 rpm deficit: 109 mm (A) / 37 mm (B) (derived, launch). Battery 12.5 -> 11.5 V: -8 % free speed (derived) | readout (PM-022): per-shot drop, recovery and minimum shot interval for the answer and its no-spin twin, closed form (`src/launcher.py` droop_readout, `solver.js` droopReadout) within about 1.5 % of hood_model on its rpm grid (PREDICTED; about 2 % at 2000-6000 rpm over the page inertia range, reads high below 2000 rpm with a light wheel); motor, wheel inertia (ASSUMED) and battery V in Advanced. Shots are still solved at the set rpm; no controller lag, current limit or rotor inertia | low (readout, done), medium (encoder log) | readout **done** (build-next 11); **measure** bursts with encoder and voltage before droop enters the shot solve |
| 9 | Shooting while moving | angle, possible | robot speed adds 1:1: 0.1 m/s costs 89-135 mm (derived, launch). Twin not run | option, off by default: robot velocity (toward, sideways, field vx / vy), turn rate, lead, per-0.1 m/s sensitivity, twin too (PM-016, JS and Python 3D path) | low | **model now** as an input (build-next 11), or rule "shoot stationary" |
| 10 | Exit skew (axle roll) and heading | possible (lateral) | 210 mm lateral per deg of skew, twin 206 mm (PREDICTED, spin) against +-218 mm slack, so the axle must be aligned under about 0.25 deg (derived, spin). Heading about 40 mm/deg (PREDICTED, spin). Couples with item 13: a 1 deg skew also halves the in-plane gate (section 4, item 4) | partial: 3D flight and 3D cell exist (PM-013 / PM-016); hit chance scatters heading 0.50 deg (ASSUMED, page input since PM-017); no axle-roll skew input | medium (3D) | **measure first** (alignment check); 3D model later |
| 11 | Knuckle (random side force on a low-spin perforated ball) | angle, possible | Cs +-0.15: +-160 mm in plane, 223 mm lateral; Cs +-0.03: +-32 mm (PREDICTED, aero, wavelength about 5.4 m). Cs for POLLEN unknown | no | low (MC term), medium (data) | **measure first**: T1 shot scatter with and without spin |
| 12 | Balls and NECTAR already in the CELL; COR / retention; TIP during a volley | scoring (and clean entry if the mouth is blocked) | COR e 0.3-0.8: S1 retains 50-151 cells, S0 twin 154-179 (PREDICTED, docs/05). Resident balls: 0 to about 7 POLLEN plus 3 NECTAR; a head-on hit keeps about 25 % of normal speed (PREDICTED, target). TIP turns the target over mid-volley (CONFIRMED rule, BIOBUZZ manual 10.5) | COR swept 2D; resident balls and TIP no | medium to high | **measure first** (T5 drop tests on skin, rib, NECTAR); model resident balls after |
| 13 | 3D pentagon roof and side walls | possible (oblique shots), angle | -6.6 to -6.8 mm of gate on the centre line; gate about 0.2797 - 0.646 abs(y) m; side walls clamp abs(y) <= 0.2185 m (derived, target) | yes: 3D cell (side walls, pentagon roof, lips) is the live default since PM-013 (JS and src/cell3d.py); the precomputed field maps and side-view sweeps use it too since PM-019 (section model kept as an option) | low | **model now** (build-next 5) |
| 14 | Spin-raised drag | angle | -51 mm at R (PREDICTED, aero, dCd 0.08-0.18 ASSUMED from tennis/smooth-sphere data). The twin has S = 0, so this widens the spin-vs-twin gap | option, off by default: dCd 0 / 0.08 / 0.18 (ASSUMED), `Cd += dCd min(S / 0.6, 1)`, backspin shot only | low | **model now** as an option bracket (build-next 4) |
| 15 | Effective mass: added mass + carried internal air | angle (model-only aim) | epsilon = 0.45-1.35 %: +7.0 / +21.1 mm at R, twin T2 +7.0 / +21.1 mm; +7.7 / +23.0 mm at A and A0 (derived, this file's check). env: 0.03-0.28 deg, up to 23 mm (PREDICTED). Absorbed by any tuning to real shots | option, off by default: phi 0-1 (ASSUMED), eps 0.45-1.36 % (derived), no outer buoyancy term (PM-016) | low | **model now** (build-next 3) |
| 16 | HIVE tilt and lip-height tolerance | scoring, angle | lip 53.5 +- 0.5 in = 28.80-31.77 deg (exact solve, derived, PM-015; the earlier linear estimate was +-1.5 deg); retained counts move 20-25 % (PREDICTED, target, at the old +-1.5 deg) | bounds only: 28.80-31.77 deg exact (wide 25.90-34.83, derived, PM-015); precomputed sweeps re-run at 28.80 / 31.77 (PM-019), Side view buttons match (round 4) | low | **measure** the event HIVE; keep the bounds |
| 17 | Spin-axis tilt (sidespin) | possible (lateral) | 9.4 mm/deg (PREDICTED, spin); 5 deg: about 33 mm (aero), 11 / 49 mm at A / B (launch). Scales with flight time, not a conflict | partial: gyro-correct S_perp option (JS and Python; page control "Gyro spin" since PM-017); turn rate adds a vertical spin part; no axis-tilt input | medium (3D) | **measure first** (axis from video) |
| 18 | Robot-plate near-wall lift, flywheel air jet | angle | 0.04-0.23 deg; jet 0.2-0.8 % of v (PREDICTED, env) | no | low | define release at >= 2 D from the robot; **measure** with the T2 video. Ignore in code until then |
| 19 | Ball temperature (shell stiffness, then grip) | rpm via v/u | pickleball stiffness at 49 C is about half room value (CONFIRMED for a Franklin X-40 only, Pickleball Science 2024); POLLEN unknown | no | low (procedure) | store balls at venue temperature; log ball temperature next to every calibration |
| 20 | Release point moves with hood angle | angle (small) | 10 mm across 74-81 deg, 1:1 along the shot (derived, launch) | no, d fixed per pose (a fixed release offset on the chassis can be set, ASSUMED 0) | low | calibrate once (hood angle -> exit point) |
| 21 | Turret aim error | possible (lateral, small) | 0.5 deg costs 12-17 mm sideways (derived, launch) | sigma 0.5 deg (ASSUMED) in MC and the page hit chance; page input since PM-017 | low | keep |
| 22 | Vibration, chassis pitch | angle | no source with numbers; acts as an elevation error (launch) | via sig_th | medium | fold into item 5 measurement |
| 23 | Partial drag crisis (below full transition) | angle | 3-17 mm (PREDICTED, aero) | option: Cd `blend` (Cd_sub to 0.33 between Re 3e4 and 5e4, ASSUMED until T1) | low | covered by the Re option (build-next 4) |
| 24 | Morrison Cd(Re) smooth-sphere curve | angle | +39 mm (PREDICTED, aero) | option: Cd `morrison` (smooth-sphere reference curve, not POLLEN) | low | option only; it is a smooth-sphere curve, not POLLEN |
| 25 | Spin decay rate k | rpm only if Cl is below its cap | 0 mm while S stays above the cap (S >= 0.714) (PREDICTED, aero and spin); k smooth sphere 0.01-0.02 /s, holes may give 0.08-0.24 /s (ASSUMED, spin) | yes (k 0.03 or 0.05) | low | ignore at current sets; it matters if T1 shows an uncapped Cl(S) |
| 26 | Gyro spin component counted in S | rpm (small) | 0.6 mm/deg (PREDICTED, spin); flight.py uses total abs(omega) for S | option, off by default: gyro-correct S_perp (JS and Python 3D path; no change for pure backspin, tested) | low | **model now** (build-next 7), mostly for correctness |
| 27 | HIVE swing on impact | scoring | e change about 1 %; lip moves about 0.1 mm in contact (derived, target) | no | - | ignore: below first-contact resolution |
| 28 | CG offset / wobble | none measurable | sub-mm; <= about 0.5 deg axis drift (PREDICTED, spin) | no | - | ignore |
| 29 | Cable-tie heads, seams inside the CELL | scoring | unknown local deflections (target) | no | low | inspect a real CELL |
| 30 | Local g, Coriolis, weather pressure | angle (tiny) | g 9.78: -11 mm in s; Coriolis about 0.5 mm (PREDICTED, numerics); pressure +-1-3 %: <= 0.1 deg (PREDICTED, env) | partial: pressure through the venue air input; g and Coriolis no | - | ignore; pressure is covered by the venue rho input |
| 31 | Floor and HIVE-lip near-wall forces | none | < 1 mm (PREDICTED, env) | no | - | ignore |
| 32 | RK4 step error, contact detection | none | RK4 about 3 um; contact is already a swept capsule test with <= 5 um chord sag (PREDICTED, numerics) | yes | - | ignore; see build-next 8 |

Top four by answer change (derived from the table): the Cl level, Cd, the grip-limited speed regime, and the exit-angle
offset. All four need POLLEN data (T1, T2); code alone cannot settle them.

## 2. Build next (safe in code now, no new measurements)

Status 2026-10-31 (after round 4): items 1, 2, 3, 4, 5, 6, 7 and 9 are in code (options, off by default). 10 is in:
the hit chance at one setting (PM-016), a best-chance search that the page recommends, with the no-spin twin
searched on its own grid (PM-017), and a field-map chance layer for backspin and twin, one value per 0.3 m block
(PM-017). All are model probabilities under ASSUMED scatter, not a repeatability. 11 is in for robot velocity and
d0, and the droop readout is in (PM-022, a readout only: the shot solve still uses the set rpm); 8 is not done.

Each item is an option or input with the current behaviour as its default, so existing results do not change unless
it is switched on. Equations are as given by the cited source; the lens that proposed each is in brackets.

1. **Venue air density input** [env]. Default rho = 1.204 kg/m^3 (20 C, sea level, dry; derived from the formulas
   below), shown next to the old 1.20 (about 1 mm apart, derived).
   `p = 101325 (1 - 2.25577e-5 h)^5.25588` (h in m; US Standard Atmosphere, NASA-TM-X-74335);
   `e = RH * 611.2 * exp(17.62 t / (243.12 + t))` (Pa, t in C; Magnus form);
   `rho = (p - 0.378 e) / (R_d T)`, R_d = 287.06 J/(kg K), T in K (simplified CIPM-2007, Picard 2008);
   viscosity for Re: `mu = 1.716e-5 (T/273.15)^1.5 (383.55)/(T + 110.4)` (Sutherland).
   Prefer a logged station pressure over the altitude formula.
2. **Wind and relative air velocity in the live solver and maps** [env, aero, numerics]. `v_rel = v - w`;
   `F_D = -1/2 rho A Cd |v_rel| v_rel`; Magnus uses v_rel. flight.py already accepts wind; physics.js / solver.js do
   not. Add a vertical sigma to robustness.py next to the horizontal 0.30 m/s (ASSUMED values 0.1 and 0.3 m/s;
   indoor draft ranges from ASHRAE 55 and Lestinen 2016, not venue measurements).
3. **Effective mass option** [env]. `dv/dt = (F_aero / m + g) / (1 + eps)`, `eps = (0.5 + phi) rho V / m`,
   0.5 = sphere added-mass coefficient (quasi-steady Maxey-Riley form without the history term), phi = fraction of
   the inner air carried (0 to 1, ASSUMED). Do **not** add a buoyancy term for the outer volume: for a perforated
   shell it cancels against the weight of the inner air (section 4, item 1). Default eps = 0.
4. **Re-dependent and spin-dependent Cd options** [aero]. Smooth-sphere reference (Morrison 2013, with the
   corrected constant 263000 in both places):
   `Cd = 24/Re + 2.6 (Re/5)/(1 + (Re/5)^1.52) + 0.411 (Re/263000)^-7.94 / (1 + (Re/263000)^-8) + 0.25 (Re/1e6)/(1 + Re/1e6)`.
   POLLEN-ready blend: `Cd(Re) = Cd_sub + (Cd_post - Cd_sub) smoothstep((Re - Re1)/(Re2 - Re1))` with Cd_sub,
   Cd_post, Re1, Re2 as inputs (ASSUMED until T1). Spin drag: `Cd = Cd0(Re) + dCd min(S/S_sat, 1)`,
   dCd in {0, 0.08, 0.18}, S_sat 0.6 (ASSUMED, tennis and smooth-sphere data). flight.py already takes `cd_fn(Re, S)`;
   the JS solver needs the same hook.
5. **3D roof clearance and side walls** [target]. Roof clearance `R sqrt(1 + s^2)` instead of R in hive.py
   `_roof_drop`, with s the roof slope across the shot; gate `about 0.2797 - 0.646 |y|` m; reject `|y| > 0.2185` m.
6. **Grip-limited flag** [spin, launch]. Mark any result whose required exit speed is above HOOD_V_MAX = 8.9 m/s
   (PREDICTED, docs/04) as "grip-limited: v/u and spin uncertain", in the live solver and sweep tables. The answer
   "possible" must not rest on a flagged shot.
7. **Gyro-correct spin ratio** [spin]. `S_perp = |omega x v| R / |v|^2`,
   `F_M = 1/2 rho A Cl(S_perp) |v|^2 unit(omega x v)` in flight.py `_aero` (it now uses total |omega|). No change
   for a pure backspin axis.
8. **Exact contact event root (optional)** [numerics]. The swept capsule test already covers tunnelling. Optional:
   locate the contact time inside a step by a root of the cubic Hermite interpolant of the RK4 step
   (Shampine & Thompson 1991; event location as in scipy solve_ivp). Gain is micrometres; do it only if contact.py
   needs exact impact states.
9. **Cl table and reverse-Magnus option** [aero]. Cl from a user table Cl(S) (linear interpolation, flat beyond the
   last point to S = 3), plus an off-by-default reverse switch: smooth blend to `Cl = -Cl_rev` when Re < Re_rev and
   S < S_rev (Re_rev 4.6e4, S_rev 0.5, Cl_rev 0-0.1, ASSUMED from Kim 2014 and Kray 2012).
10. **Monte Carlo P(clean) map option** [numerics]. Outer loop over epistemic sets (Cd, Cl set, k), inner loop over
    shot scatter; report per cell the Wilson interval
    `(p + z^2/2n +- z sqrt(p(1-p)/n + z^2/4n^2)) / (1 + z^2/n)` (Wilson 1927). Use the shared mc_shots path in
    robustness.py; report the twin map beside the backspin map. This reports model probability under ASSUMED
    scatter, not a repeatability claim.
11. **Launch-state inputs** [launch]. Robot velocity: `v_launch = Rz(-psi)(v_ground - v_robot - omega_z z x r_exit)`;
    exit-angle offset `theta_exit = theta_hood + d0` with d0 = 0 default; a droop/recovery readout from
    `I_w dOmega/dt = tau_stall (V/12)(1 - Omega/Omega_free(V)) - tau_loss`.
    Done 2026-10-31 (PM-022) as a readout: per-shot drop = impulse (generalised Brettle, coasting wheel) + rolling
    hysteresis over the estimated contact time, recovery on the linear motor line with tau_loss = 0, no fitted factor.
    Still needed: an encoder and voltage log of real bursts (drop, recovery, controller lag, current limit).

Not in this list on purpose: knuckle side force, resident balls, a 3D spin-axis model and CFD. Each needs data or a
larger model first (numerics.md: LES/DES/LBM of a perforated spinning ball is about 1e8 cells; measure first).

## 3. Measure first (links to COMPLETENESS.md T0-T6)

Tool since PM-018: the measurement kit `viz/measure/measure.html` (linked from the explorer and published with the
site) with the protocol `docs/MEASURE.md` and the same fit in `src/fit_aero.py`. It covers T1 (drop test for Cd,
twin test A no spin / B backspin for Cd and Cl, gravity check of the length scale) and the video side of T2 (v/u
from wheel rpm, S from counted turns). Its accuracy figures are from synthetic `physics.js` tracks (derived); no
POLLEN ball has been measured yet. Shot scatter (items 5, 10, 11, 21) still needs about 20 shots at one setting.

- T1 (side video 240-480 fps, wheel above vs below, taped-hole ball): items 1, 2, 4, 11, 14, 25.
- T2 (exit video + encoder): items 3, 5, 8, 18, 20, 22.
- T0 / T4 (mass, diameter, squeeze): items 3, 15, 19.
- T5 / T6 (drop and CELL tests): items 12, 16, 29.
- Venue: air speed at robot height, temperature, RH, station pressure (items 6, 7).

## 4. Cross-lens checks: contradictions and how they resolve

1. **Buoyancy / effective mass (resolved).** aero.md lists "buoyancy +10 mm" and "added mass < 5 mm" as separate
   terms; numerics.md uses net weight `(m - rho V_out) g` with inertia x 1.0135; env.md uses inertia
   `m(1 + eps)` with net weight m g. For a perforated shell the inner air is at the outer hydrostatic pressure, so
   the outer-volume buoyancy is always balanced by the weight of the inner air (or acts on both faces of the shell);
   only the shell material volume is buoyed (negligible). env.md's form is the correct one. A check with a 2D RK4 at
   the params_lit nominal (derived, scratch): eps 0.45 % / 1.35 % gives +7.0 / +21.1 mm at R (twin T2 the same),
   +7.7 / +23.0 mm at A and A0, +6.9 / +20.7 mm at B. The numerics form gives +25 to +37 mm, so its "-70 mm in s"
   (twin -67) overstates by about 1.5-3x by counting buoyancy. aero's added-mass "< 5 mm" is slightly low (about
   7 mm at phi = 0).
2. **Kim 2014 reverse-Magnus ranges (flagged).** aero.md cites Re 0.6e5-1.8e5 with an onset near 4.6e4; numerics.md
   cites 0.6-2.6e5. The JFM abstract (read 2026-10-31) gives neither range, so the full text is needed. Both lenses
   agree the holes may lower the onset Re and that it cannot be ruled out without T1.
3. **Two nominal aero sets (explained, not a conflict).** aero.md uses `data/aero_params.json` (Cd 0.48, k 0.05);
   env, launch, numerics, spin and the explorer use `research/params_lit.json` (Cd 0.50, k 0.03, rho 1.20). That is
   why the reference shots differ (R 7.5 m/s / 78.75 deg vs A 6.1 m/s / 73.86 deg vs spin's 9.0 m/s / 80.7 deg).
   Sensitivities agree in size after converting s to dx (ratio about 2.8, derived). Future lenses should state which
   file they used.
4. **Lateral window (flagged).** spin.md and env.md use a +-218 mm lateral slack; aero.md and launch.md use W_LAT
   0.10 / 0.15 / 0.2185 m (0.15 primary, robustness.py). target.md shows the in-plane gate shrinks 0.646 mm per mm of
   lateral offset, so lateral and in-plane errors are not independent: a 1 deg exit skew (about 210 mm lateral)
   leaves a gate of about 0.2797 - 0.646 x 0.21 = 0.144 m, about half (derived). Any +-218 mm "within window"
   statement is optimistic until build-next 5 is in.
5. **Tilt per degree (not a conflict).** aero about 33 mm at 5 deg, spin 47 mm at 5 deg at 9 m/s, launch 11 / 49 mm
   at A / B. It scales with flight time and speed.
6. **Shots past the grip cap (flagged).** spin.md's aim (9.0 m/s), launch B (9.1 m/s) and env B (10.1 m/s) exceed
   HOOD_V_MAX 8.9 m/s. Their sensitivities are fine as model statements, but the hood probably cannot produce
   those exits with the assumed v/u and S. The live solver has no such limit (build-next 6).
7. **"Continuous collision detection" (already done).** The task suggested adding CCD; numerics.md shows contact is
   already a swept capsule test with <= 5 um chord sag. Only the optional exact event root remains (build-next 8).
8. **rho 1.204 vs 1.20 (resolved).** 0.3 %, about 1 mm (derived). Make rho a venue input with default 1.204 rather
   than treating the default change as a fix; altitude (item 7) is the effect that matters.
9. **Morrison constant (resolved).** aero.md notes the published handout mixes 263000 and another value; use 263000
   in both places (as in build-next 4).
