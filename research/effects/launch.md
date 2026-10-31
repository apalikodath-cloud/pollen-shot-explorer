# Launch and robot effects on the POLLEN shot (research lens "launch")

Written 2026-10-30 for PM-001. Scope: flywheel speed droop and recovery, contact time and ball compression, exit-angle
scatter, release point, shooting while moving, turret aim error, vibration, and measured shot-to-shot scatter of real
ball launchers. Aerodynamic coefficients (Cd, Cl, spin decay) belong to the aero lens and are only touched here where
they change a launch sensitivity.

Labels follow HANDOFF section 5: **CONFIRMED** (official, vendor or primary source, but a source about another ball is
still not a POLLEN fact), **user**, **ASSUMED**, **derived** (my arithmetic from labelled inputs), **PREDICTED** (model
output). No number here is a POLLEN measurement. Nothing here is a repeatability claim. Pickleball, tennis and
table-tennis numbers are context only, never POLLEN coefficients.

## 0. Default case and how the sizes were computed

Default case (task): unfavourable (far) side, release 1.00 m from the HIVE pivot plane on the shot line (psi = 0),
release height 0.737 m (ASSUMED robot limit, as in `src/robustness.py`), red HIVE tilt 30 deg (CAD, as in the solver),
nominal ASSUMED aero (Cd 0.50, Cl = min(0.35 S, 0.25), k = 0.03 1/s), S = 1 (derived ideal hood value), grip v/u = 0.42
(ASSUMED, explorer default), so 1 wheel rpm = 2.155e-3 m/s of exit speed (derived).

Two reference shots were taken from the live solver (`viz/explorer/solver.js`, run under node on 2026-10-30). Both are
**PREDICTED** clean air-only entries for this model only:

| Shot | v (m/s) | elevation (deg) | wheel rpm (derived) | clean hood-angle run at that v | clean speed run at that angle | min clearance | time to mid-mouth height |
|---|---|---|---|---|---|---|---|
| A, `minRpmTol` (tolerant minimum) | 6.02 | 73.61 | 2793 | 73.498-73.747 (0.25 deg) | 5.998-6.038 m/s (0.04 m/s, about 19 rpm) | 10.3 mm | 0.98 s |
| B, `mostForgiving` | 9.10 | 80.80 | 4222 | 80.615-81.015 (0.40 deg) | 8.835-9.330 m/s (0.50 m/s, about 230 rpm) | 44.4 mm | 1.59 s |

No-spin twins (same solver, S = 0, c1 = 0, PREDICTED): at the same (v, elevation) both twins **miss**. The twin crosses
the mid-mouth height 94 mm (A) and 523 mm (B) farther along x than the backspin shot. The twin's own tolerant minimum
is 5.98 m/s at 74.53 deg (2775 rpm, clearance 9.6 mm) and its most forgiving shot is 10.8 m/s at 85.0 deg (5011 rpm,
clearance 48 mm). These are model outputs; they do not show that more spin is better.

**Sensitivity method (derived).** `src/flight.simulate` (repo code) integrated the two reference shots in 3D and
recorded where the ball centre crosses z = 1.51 m on the way down (the mid-height of the CELL mouth, derived from the
lips at z 1.357 and 1.666 m in `data/hive_geometry.json`). Each effect was applied alone. "dx" is the along-shot shift
at that height; "dy" is the sideways shift. The usable in-plane window is roughly **+/-10 mm for A** and **+/-40 mm for
B** (derived: run width times the dx-per-unit sensitivity below, both ways agree). The lateral half-width is ASSUMED
0.10-0.2185 m (primary 0.15 m, `W_LAT` in `src/robustness.py`).

| One-at-a-time change (derived) | A dx (mm) | A twin dx | B dx (mm) | B twin dx |
|---|---|---|---|---|
| exit speed +0.1 m/s (about +46 wheel rpm) | +47 | +54 | +16 | +36 |
| elevation +0.1 deg | -8.3 | -7.8 | -21 | -20 |
| release height +5 mm | +1.8 | +1.9 | +0.7 | +0.8 |
| release point +10 mm along the shot | +10 | +10 | +10 | +10 |
| robot velocity +0.1 m/s along the shot | +89 | +87 | +133 | +130 |
| robot velocity +0.1 m/s sideways (dy) | +90 | +89 | +135 | +133 |
| turret yaw +0.5 deg (dy) | +12 | +13 | +12 | +17 |
| spin axis tilted 5 deg about the velocity (dy) | -11 | n/a | -49 | n/a |
| spin axis tilted 10 deg (dy) | -22 | n/a | -98 | n/a |
| S +0.1 with the nominal capped Cl | 0 | n/a | 0 | n/a |
| S +0.1 if Cl were not capped (Cl_max 1.0, bound only) | -19 | n/a | -101 | n/a |

Two things follow before any single effect is discussed:
1. At A, speed is the sensitive axis: the whole clean speed run is about **19 wheel rpm** wide. At B, elevation is the
   sensitive axis: the whole clean run is **0.40 deg** wide, and B tolerates about 230 rpm. (PREDICTED, nominal aero.)
2. With the nominal cap, S between about 0.71 and 1.3 gives the same lift, so spin scatter costs nothing *in the model*.
   That is an artefact of the ASSUMED cap. If real POLLEN lift keeps rising with S, spin scatter matters a lot at B.

## 1. Error budget at a glance

| # | Effect | Best size found (label) | Shift at A / B (derived) | In current model? | Priority to measure |
|---|---|---|---|---|---|
| 1 | Flywheel droop during the shot | 8.5 % of rpm (273 rpm at 3000) with I_w 2.65e-4 kg m^2 (PREDICTED, `docs/04_launcher.md`) | systematic; absorbed by calibration if it is repeatable | launcher model yes; live solver no (fixed v/u) | high |
| 2 | Incomplete recovery between shots | ideal 0.10 s at 3000 rpm, 0.24 s at 4500 (derived, no controller lag); a 50 ticks/s feed gate is about 107 rpm (derived from REV DECODE guide) | 10 rpm costs 10 mm (A) or 3.4 mm (B); a 107 rpm deficit costs about 109 mm (A) or 37 mm (B) | no | high |
| 3 | Battery sag | 12.5 to 11.5 V is -8 % motor free speed (derived, linear DC motor) | only recovery time if closed-loop; 8 % of v if open-loop power | recovery table only | medium |
| 4 | Contact time and ball compression | contact 15-37 ms (PREDICTED); pickleball compression limit < 43 lbf at 0.25 in, i.e. < 30 N/mm secant (CONFIRMED for pickleballs only) | in the grip-limited regime v scales about as sqrt(k_n): 10 % stiffness spread gives about 5 % v, i.e. about 140 mm (A) or 72 mm (B) | launcher model yes; scatter no | high |
| 5 | Exit-angle offset and scatter | tennis machine release angle SD 3.98 deg (CONFIRMED, Norris 2012, other machine); decompression kick bound up to several deg (derived) | 0.1 deg costs 8 mm (A) or 21 mm (B) | sig_th 0.40 deg in Monte Carlo (ASSUMED); offset no | high |
| 6 | Release point moves with hood angle | rho dtheta = 10 mm across 74-81 deg (derived) | 1:1 along the shot | no (d is fixed per pose) | low (calibrate once) |
| 7 | Shooting while moving | robot speed adds to ball velocity 1:1 (derived) | 0.1 m/s costs 89-135 mm | no | high if shooting on the move |
| 8 | Turret aim error | 0.5 deg costs 12-17 mm sideways (derived) | small against a +/-150 mm lateral window (ASSUMED) | sig_psi 0.5 deg (ASSUMED) | low |
| 9 | Spin-axis tilt (gyro component) | Sakai & Kitade: gyro shots had landing SD about 140 mm vs 15-40 mm (CONFIRMED, table tennis machine) | 5 deg tilt costs 11 mm (A) or 49 mm (B) sideways | no | medium |
| 10 | Vibration, chassis pitch, gyroscopic torque | no source with numbers | acts as an elevation error: 0.1 deg = 8/21 mm | no | medium |
| 11 | Ball-to-ball mass and diameter | pickleball out-of-round limit +/-0.51 mm (CONFIRMED, pickleball spec) | +/-0.5 mm diameter is +/-12 % compression at 4 mm | mass/radius scatter in MC; compression link no | medium |

A root-sum-square with the repo's own **ASSUMED** nominal error set (sig_v 1.5 %, sig_th 0.40 deg) gives about
43 mm (speed) and 33 mm (angle) at A, and 22 mm and 84 mm at B (1 sigma, derived). Both exceed the PREDICTED windows
(+/-10 and +/-40 mm). So under the repo's own assumptions this shot needs tighter-than-nominal control. That statement
depends entirely on ASSUMED error sizes and ASSUMED aero; it is not a hit-rate prediction.

## 2. Effects one by one

### 2.1 Flywheel speed droop during the shot
- **What it is.** The ball takes energy from the wheel while it is in contact. The wheel leaves the shot slower than it
  started. Ideal rolling exit uses the *exit* wheel speed, v = R_w Omega_exit / 2 (Brettle; `docs/04_launcher.md` 1.2).
- **Numbers.**
  - Generalised Brettle ratio (derived, `docs/04_launcher.md` 3.2):
    `Omega_i / Omega_f = 1 + R_w^2 (m + I_b / r_c^2) / (4 I_w) - R_w m v_in / (2 I_w Omega_f)`.
  - I_w 2.65e-4 kg m^2 (ASSUMED wheel plus CONFIRMED goBILDA steel flywheel 1.651e-4 kg m^2): ratio 1.092, about 8.5 %.
    Bare wheel (1e-4): about 20 % (derived).
  - Launcher model, hood nominal: drop 273 rpm at 3000 rpm and 344 rpm at 4000 (PREDICTED, `data/launch_envelope.json`).
    The stiff-ball, 8 mm case drops 347-503 rpm at 3000-5000 rpm (PREDICTED).
  - Brettle's Discussion says that because the ball is not a perfect spring the wheel slows more than predicted, and
    that this is usually compensated empirically (CONFIRMED as a statement, no number; see `docs/04_launcher.md` 1.2).
- **Effect on this shot.** A repeatable droop is a calibration offset: v/u absorbs it. What matters is the *variation*
  in droop. Droop is proportional to ball mass. A +/-4 % mass spread (ASSUMED) changes v by about 0.3 %, i.e.
  9 mm at A and 3 mm at B (derived).
- **In the model?** The launcher model includes it. The live solver does not: it maps rpm to v with one fixed v/u, so
  its "rpm" means "the rpm that gives this v", not the set point.
- **How to add it.** In the solver's rpm readout, use `rpm_set = rpm_exit * ratio(m, I_b, I_w, r_c)` and say which one
  is shown. Add the mass spread to the Monte Carlo through the ratio.
- **How to measure on POLLEN.** Log the flywheel encoder velocity in a fast loop (bulk reads) while feeding one ball.
  The drop is the minimum minus the pre-shot value. Repeat with 20 balls of known mass and plot drop against mass.

### 2.2 Recovery between shots (motor curve, controller, feed gate)
- **What it is.** After each shot the motor must refill the wheel. If the next ball is fed before the wheel is back,
  that ball leaves slower.
- **Numbers.**
  - goBILDA 5203 1:1: "6,000 RPM" free and "1.47 kg.cm" stall torque at 12 V, 9.2 A stall, encoder "28 PPR at the
    output shaft" (CONFIRMED, goBILDA product page). A related model's tested free speed is about 5400 rpm (CONFIRMED in
    `docs/04_launcher.md`).
  - Ideal recovery at full voltage, no current limit, no controller lag: 0.101 s at 3000 rpm, 0.183 s at 4000, 0.238 s
    at 4500, 0.342 s at 5000, 0.605 s at 5500 (derived, `data/launch_envelope.json` `recovery_hood_nominal`). Near
    4700 rpm the motor runs at 87 % of the tested free speed, so recovery is slow and sensitive to voltage.
  - REV's DECODE programming guide feeds when the flywheel is "at least 50 ticks below" target and allows "100 ticks
    above"; it also warns that the first ball is "stronger than those that follow" (CONFIRMED, REV docs; no magnitudes).
    With 28 counts per motor revolution at 1:1, 50 ticks/s is 107 rpm and 100 ticks/s is 214 rpm (derived; assumes the
    counts the SDK reports are 28 per revolution, as in REV's own sample code).
  - Dittrich et al. 2023 (AIMY, table tennis): landing-point SD rose from about 0.023 m to 0.040 m when wheel ramp-up
    time fell below 0.5 s (CONFIRMED, peer-reviewed; another ball, already in `research/sweeps/sweep_launch.md`).
  - Chief Delphi, Pedersen thread: "Even a few ms of recovery while shooting will significantly change the shot
    behavior" (forum opinion, no data).
- **Effect on this shot.** 10 wheel rpm moves the entry 10 mm at A and 3.4 mm at B (derived). A 107 rpm feed gate
  moves it about 109 mm at A and 37 mm at B. **At A the whole clean speed run is about 19 rpm wide, so a generic
  FTC-style feed gate is about 5 times too loose** (derived from PREDICTED windows).
- **In the model?** No. `sig_v_rel` in `src/robustness.py` is a lumped ASSUMED 1.5 %.
- **How to add it.** Per shot k in a burst:
  `I_w dOmega/dt = tau_stall (V/12) (1 - Omega / Omega_free(V)) - tau_loss` with `Omega_free(V) = Omega_free,12 V/12`,
  under the team's real controller (P plus feedforward, saturating at full voltage). Fire when the feed rule allows,
  take `Omega_k` at that instant, apply the droop ratio, and convert to v. Then sample the feed-gate residual in the
  Monte Carlo instead of a fixed 1.5 %.
- **How to measure.** Bursts of 5 balls at the planned feed interval. Log encoder velocity, battery voltage and the
  feed time stamp at the fastest available loop rate. Report per-shot rpm at feed, drop, and recovery time to within
  10 rpm. Compare shot 1 with shots 2-5, since REV reports a first-shot difference.

### 2.3 Battery sag
- **What it is.** A DC motor's free speed and stall torque scale with voltage. FTC robots also draw drive current while
  shooting.
- **Numbers.** 12.5 V to 11.5 V lowers free speed by 8 % (derived). The recovery table above already contains a
  0.958 voltage case: 0.109 s instead of 0.101 s at 3000 rpm, 0.281 s instead of 0.238 s at 4500 (derived).
- **Effect.** With closed-loop speed control and headroom, sag only lengthens recovery. With an open-loop power command,
  v falls with voltage: 8 % of v is about 230 mm at A (derived), which is far outside the window.
- **In the model?** Only in the recovery table.
- **How to add it.** Make V a per-match random input to the recovery model. Use velocity control with
  voltage-compensated feedforward (`kV * omega / V_battery`).
- **How to measure.** Log battery voltage at every shot. Repeat one burst on a full and a tired battery.

### 2.4 Contact time and ball compression
- **What it is.** The ball is squeezed between wheel and hood and rolls along the hood for tens of milliseconds. The
  squeeze sets the normal load, hence grip, hysteresis loss, the contact radius r_c (S = R_b / r_c) and droop.
- **Numbers.**
  - Contact time 24.6 ms (3000 rpm) and 23.2 ms (4000 and above) for the nominal hood; 37 ms for the soft ball;
    about 14-20 ms for the stiff ball at 8 mm over 3000-4700 rpm (PREDICTED, `data/launch_envelope.json`). A rough check is 2L/v with L = 131 mm of 90 deg hood: 29-44 ms at 6-9 m/s (derived).
    Brettle and Pedersen both assume an instant event (CONFIRMED from the sources).
  - Compression: 4 mm is a user candidate (HANDOFF). k_n 4 N/mm is ASSUMED with no source.
  - USA Pickleball Equipment Standards Manual (2021) 2.D.6: a ball "shall yield an average compression test result of
    <43 LBF" under ASTM F1888-09 (CONFIRMED for approved pickleballs). The ASTM method compresses between flat plates to
    0.25 in (6.35 mm) according to a secondary description of the method (not checked against the paywalled standard). Secant stiffness < 191 N / 6.35 mm = 30 N/mm (derived). POLLEN is a different ball, so this only
    shows that 1.5-10 N/mm is not absurd for a hollow PE ball; it is not a POLLEN value.
  - Chief Delphi "Ball Compression Data" (2012, foam FRC balls, load cell): spread of 2.6-12.5 % within one ball and
    more between balls (forum data, already in `sweep_launch.md`).
  - FRC 971 (2016): "As you increase compression, there is a compression level where the spread shrinks, and then
    starts to increase" (forum, no numbers). Dittrich 2023 found an interior best pinch, about 6.5-9 % of diameter,
    with more scatter beyond it (CONFIRMED, another ball; via `sweep_launch.md`).
- **Effect on this shot.**
  - Rolling regime: v follows wheel speed, S = R_b / r_c = 1.06-1.13 for the hood configs (PREDICTED, `data/launch_envelope.json`). Stiffness spread then mainly changes droop
    (a few rpm, so a few mm at A).
  - Grip-limited regime (the wheel slips at exit): the model's nominal hood saturates at 8.91 m/s for 4000 rpm and
    above, and the 1.5 N/mm ball saturates at 5.45 m/s (PREDICTED). The ratio 1.63 equals sqrt(4/1.5) = 1.63, so v
    scales about as sqrt(k_n delta) there (derived). **Shot B (9.1 m/s) sits at or above the nominal saturation, so B
    is predicted to be grip-limited unless compression or grip is raised.** In that regime a 10 % stiffness spread is
    about 5 % of v: about 0.45 m/s, i.e. 72 mm at B (derived), well outside +/-40 mm.
- **In the model?** The launcher model includes stick/slip and compression. Ball-to-ball stiffness scatter does not
  reach the trajectory Monte Carlo.
- **How to add it.** Sample k_n (and diameter, 2.11) per ball. Run `src/launcher.simulate_shot` per sample, or fit
  `v = min(v_roll(Omega), c sqrt(mu k_n delta))` to the envelope and use that. Flag any setting where the wheel slips
  at exit.
- **How to measure.** N(delta) of 20 POLLEN between flat plates to 8 mm, in two orientations (90 deg apart, as the
  pickleball test does), with a force gauge and dial indicator. Contact time: 960 fps side-on video of the hood, or two
  break-beams at hood entry and exit. Wheel slip at exit: compare measured v with R_w Omega_exit / 2 from the encoder.

### 2.5 Exit-angle offset and scatter
- **What it is.** The commanded hood angle is not the ball's exit elevation. Causes: where contact ends on a curved
  hood, release of stored compression on the last contact, hood and mount flex, ball shape and hole position at
  release.
- **Numbers.**
  - Norris, Breen, Anderson & Kenny 2012 (ISBS proceedings, two-wheel tennis machine, 96 trials, 400 Hz 3D motion
    capture): speed 18.9 +/- 0.89 m/s; "Angle of release over the 96 trials was 8.98 +/- 3.98 deg" (CONFIRMED; that
    machine drops balls in by gravity and the balls were taped, which the authors say may have cut grip). This is an
    upper example of what an uncontrolled machine does, not a POLLEN value.
  - Sakai & Kitade 2017 (four-roller table tennis machine, 40 balls): landing SD under 40 mm for no, top and side spin
    (CONFIRMED, figure reading, already in `research/papers_extra/launch_methods_check.md`).
  - Decompression kick (derived bound): stored energy 0.5 k_n delta^2 = 0.032 J at 4 N/mm and 4 mm. If a fraction eta
    of it becomes velocity normal to the hood at release, `v_n = sqrt(2 eta E / m) = 1.6 sqrt(eta)` m/s. With eta
    unknown in 0-0.5, the angle offset atan(v_n / v) can reach several degrees at 6 m/s. It is likely much smaller
    because the gap opens gradually at the hood end. **This is a hypothesis to test, not a result.** Its *variation*
    is what matters: 10 % of a 2 deg offset is 0.2 deg, i.e. 17 mm at A and 42 mm at B (derived).
- **Effect.** 0.1 deg moves the entry 8.3 mm at A and 21 mm at B (derived). B's whole clean run is 0.40 deg.
- **In the model?** Scatter only: ASSUMED sig_th 0.40 deg nominal, 0.15 tight. No offset, and no link to compression.
- **How to add it.** `theta_exit = theta_hood + d0(v, delta) + e`, with e ~ N(0, sig_th) per shot and d0 fitted from
  video. Feed the solver theta_exit, and report hood angle = theta_exit - d0.
- **How to measure.** Side-on video at 240 fps or more with a grid, n >= 20 per setting. Fit a line to the first
  5-10 frames after exit. Report the mean offset from the hood setting and the SD.

### 2.6 Release point height and offset from the turret
- **What it is.** The solver puts the release at a fixed point. On a concentric hood, the ball centre at exit sits at
  radius rho = R_w + r_c from the wheel axis, perpendicular to the exit direction. Changing the hood angle moves that
  point.
- **Numbers.** rho is about 0.0845 m (derived: 0.049 + 0.0355). Going from 74 to 81 deg moves the exit point by
  rho * 0.122 rad = 10 mm (derived). The exit point also sits some distance from the turret axis (unknown; no CAD).
- **Effect.** +10 mm along the shot moves the entry +10 mm; +5 mm of height moves it under 2 mm (derived). It is
  systematic, so a one-time calibration removes it.
- **In the model?** No. ASSUMED sig_h 5 mm is in the Monte Carlo.
- **How to add it.** `p_exit = p_turret + Rz(psi) [r_mount + rho (-sin theta, 0, cos theta)]` (for a wheel below and
  behind the ball; adjust the sign to the CAD). Compute d and h from p_exit for every candidate theta.
- **How to measure.** From the exit-angle video, read the ball centre at the first free frame for each hood setting.

### 2.7 Shooting while the robot moves
- **What it is.** The ball leaves with the launcher's velocity plus the robot's:
  `v_ground = Rz(psi) v_launch + v_robot + omega_z z_hat x r_exit`. Air is still, so drag and S use v_ground.
- **Numbers.**
  - 0.1 m/s along the shot moves the entry 89 mm (A) or 133 mm (B); 0.1 m/s sideways moves it 90-135 mm (derived).
    That is v_robot times the flight time (0.98 s and 1.59 s), slightly reduced by drag.
  - To stay inside the in-plane window, the residual (uncompensated) velocity error must be under about 0.011 m/s at A
    and 0.03 m/s at B (derived).
  - A yaw rate of 1 rad/s with the exit 0.15 m from the robot centre (ASSUMED) adds 0.15 m/s sideways: 135-200 mm
    (derived). The same yaw tilts the spin axis by only about omega_z / omega_ball = 1/170 rad, about 0.3 deg
    (derived, negligible).
  - Practice: Team 254 (2022) "calculates a feedforward based on its tangential and radial velocity about the goal"
    (CONFIRMED, team README). An FTC DECODE codebase aims at a virtual goal `goal - robotVelocity * tof`, iterated
    10 times with a hand-fitted time of flight and a 0.8 multiplier (CONFIRMED by reading the code, see
    `research/papers_extra/cuberobot_decode.md`). Neither reports accuracy.
- **In the model?** No. All solver results assume a stationary robot.
- **How to add it.** Solve the stationary shot in the ground frame, then command `v_launch = Rz(-psi)(v_ground -
  v_robot - omega_z z_hat x r_exit)`. That changes the commanded speed, elevation and yaw together. Because the windows
  are this narrow, iterate the HIVE-relative pose to the release instant (latency) rather than using a lookup table.
- **How to measure.** Drive past at constant logged speeds (0, 0.1, 0.2, 0.3 m/s) and film the entry plane. Fit the
  shift against v_robot * t_f. Also log odometry velocity noise while driving straight, since that sets the residual.

### 2.8 Turret aiming error
- **What it is.** Yaw error of the shot line relative to the CELL centre plane.
- **Numbers.** 0.5 deg moves the entry sideways 12 mm (A), 12-17 mm (B, twin 17) (derived, about L tan(e) with
  L = 1.4 m). The goBILDA Pinpoint is advertised with about 0.002 % heading error after tuning and about 1500 Hz updates
  (vendor claim, no test method given). No published FTC AprilTag or Limelight heading-accuracy figure was found.
- **Effect.** Small against the ASSUMED +/-150 mm lateral window. It matters only when it adds to spin-axis tilt (2.9)
  or sideways robot motion (2.7).
- **In the model?** Yes, as ASSUMED sig_psi 0.5 deg.
- **How to measure.** Aim at a far target line with a laser on the turret; log the turret encoder; repeat 20 times.

### 2.9 Spin-axis tilt (sidespin component)
- **What it is.** If the ball contacts the wheel off its centre line, or the hood or wheel is crowned or worn, the spin
  axis is not horizontal. Magnus force follows omega x v, so a tilt beta turns part of the lift sideways (about
  F_M sin beta).
- **Numbers.** 5 deg moves the entry 11 mm (A) or 49 mm (B) sideways; 10 deg gives 22 or 98 mm (derived, nominal capped
  Cl). B flies longer and more of its path is lift-dominated. Sakai & Kitade 2017 report gyro-mode landing SD of
  about 60 mm (X) and 140 mm (Z) against under 40 mm otherwise, and attribute it to unbalanced roller contact
  (CONFIRMED, table tennis machine).
- **In the model?** No. The planar solver has a horizontal axis by construction; the 3D integrator in `src/flight.py`
  accepts any omega vector.
- **How to add it.** `omega = S v / R [cos beta e_back + sin beta e_up']`, with e_up' the unit vector perpendicular to
  both v and e_back; sample beta ~ N(0, sig_beta) in the Monte Carlo. This is pure-backspin-first scope (HANDOFF 4B):
  report it as a scatter term, never as a design substitute.
- **How to measure.** Mark a great circle on the ball and film the release from behind and from the side at 960 fps;
  the axis tilt is the angle of the marked circle's pole.

### 2.10 Vibration, chassis pitch and gyroscopic torque
- **What it is.** Anything that moves the hood angle at the instant of release acts as an elevation error.
- **Numbers.**
  - Wheel imbalance excites the frame at the wheel frequency: 2800-4700 rpm is 47-78 Hz (derived). With contact lasting
    15-37 ms (PREDICTED), the ball sees about 1-3 cycles, so part of it averages out (derived).
  - Flywheel angular momentum is I_w Omega = 0.083 N m s at 3000 rpm and 0.13 N m s at 4700 (derived, I_w 2.65e-4).
    Slewing the turret at 3 rad/s (ASSUMED) needs 0.25-0.39 N m of pitch torque on the shooter mount (derived). A
    compliant hood or servo will deflect under it.
  - Braking or accelerating pitches the chassis on its wheels and frame. No measured value was found.
  - No source with measured vibration-induced launch scatter was found for FRC or FTC shooters.
- **Effect.** 0.1 deg of hood motion costs 8 mm (A) or 21 mm (B) (derived).
- **In the model?** No (only inside the lumped ASSUMED sig_th).
- **How to measure.** Tape a phone or IMU to the hood. Record with the wheel at speed and the robot still, then while
  braking and while the turret slews. Report the hood-angle SD at the feed instant. Log the Control Hub IMU pitch at
  each shot.

### 2.11 Ball-to-ball shape, mass and diameter
- **What it is.** POLLEN "dimensions vary by piece" and the ball is not perfectly spherical (HANDOFF, CONFIRMED by the
  manual). With a fixed hood gap, compression is delta = D_ball - gap, so diameter error goes straight into delta.
- **Numbers.** USA Pickleball allows "+/-0.020 inch (0.51 mm)" out-of-round and 22.1-26.5 g (CONFIRMED, pickleballs
  only). +/-0.5 mm of diameter is +/-12 % of a 4 mm squeeze (derived). In the grip-limited regime that is about +/-6 %
  of v (derived from 2.4).
- **In the model?** Mass and radius scatter are in the Monte Carlo (ASSUMED); the link to compression is not.
- **How to add it.** Sample D per ball; set delta = D - gap; run 2.4.
- **How to measure.** Caliper 20 balls across three axes; weigh them; keep ball IDs for every shot.

## 3. Measured shot-to-shot scatter of real launchers (context, not POLLEN)

| Source | Machine and ball | Scatter reported | Label |
|---|---|---|---|
| Norris et al. 2012, ISBS 30 | two-wheel tennis machine, 5 taped balls, 96 shots | v 18.9 +/- 0.89 m/s (CV 4.7 %, derived); release angle 8.98 +/- 3.98 deg; landing CV 8.3 % lateral, 18.4 % vertical | CONFIRMED (conference paper) |
| Dittrich et al. 2023, ICRA (AIMY) | 3-wheel and single-wheel table tennis launchers | landing SD 7-42 mm; std x 40 mm with a 0.01 s ramp-up vs about 23 mm at 0.5 s or more; best scatter at an interior pinch | CONFIRMED (peer-reviewed; in `sweep_launch.md`) |
| Sakai & Kitade 2017, Trans. JSME | four-roller table tennis machine | landing SD < 40 mm, gyro about 140 mm | CONFIRMED (figure reading; in `launch_methods_check.md`) |
| Drane et al. 2018, ISEA | two-wheel pitching machine, foam baseballs | new balls: v 18.3-33.1 m/s +/- 0.3-0.4 m/s; spin +/- 46-80 rpm (as tabulated); worn balls scatter more | CONFIRMED (in `sweep_launch.md`) |
| FRC / FTC teams | flywheel-and-hood shooters | no published SD found; only qualitative reports (971 compression sweet spot, REV first-shot effect) | forum / docs |

No FRC or FTC source with a measured exit-speed or exit-angle SD was found in this pass. Treat the repo's
ASSUMED error sets as guesses until POLLEN data exist.

## 4. What to add to the model, in order

1. **Feed-gate and recovery residual (2.2)**: replace the fixed 1.5 % speed spread with a per-shot rpm-at-feed draw from
   the motor and controller model. This is the largest unmodelled term at A.
2. **Grip-limited flag and stiffness scatter (2.4, 2.11)**: mark solver results whose v needs a slipping exit, and
   propagate k_n and diameter spread into v.
3. **Robot velocity (2.7)**: add v_robot and omega_z to the solver input; solve in the ground frame.
4. **Exit-angle offset and release point (2.5, 2.6)**: map hood angle to (theta_exit, d, h).
5. **Spin-axis tilt (2.9)** as a scatter term in the 3D Monte Carlo.
6. Keep every new result next to its no-spin twin, and keep the labels.

## 5. Sources

- Brettle, D., *Flywheel Shooter Analysis*, https://docs.carlmontrobotics.org/jupyter_notebooks/files/FlywheelShooter.html (unreviewed; already in repo).
- Pedersen, R. (2026), *Flywheel Shot Analysis: Correction and Extension*, https://www.chiefdelphi.com/t/flywheel-shot-analysis-correction-and-extension/520270 (unreviewed; thread read 2026-10-30).
- Norris, M., Breen, S., Anderson, R., Kenny, I. (2012). A study to investigate the reliability and consistency of the Sports Tutor Tennis Cube velocity, trajectory and landing points. 30th ISBS Conference, Melbourne, pp. 381-384. https://ojs.ub.uni-konstanz.de/cpa/article/view/5397 (full text read).
- Dittrich, A. et al. (2023). AIMY. IEEE ICRA. doi:10.1109/ICRA48891.2023.10160336; arXiv:2210.06048 (via `research/sweeps/sweep_launch.md`).
- Sakai, S., Kitade, Y. (2017). Trans. JSME 83(856), 17-00225 (via `research/papers_extra/launch_methods_check.md`).
- Drane, P. et al. (2018). Proceedings 2(6), 203. doi:10.3390/proceedings2060203 (via `sweep_launch.md`).
- USA Pickleball (2021). *Equipment Standards Manual*, sections 2.D.3-2.D.8. Copy read: https://www.pickleball.ph/uploads/1/2/5/9/125919777/-_official_equipment_standards_manual.pdf
- ASTM F1888-09, *Standard Test Method for Compression-Displacement of Baseballs and Softballs*, https://store.astm.org/f1888-09.html (not read; the 0.25 in displacement comes from a secondary description and is unverified).
- REV Robotics, *DECODE 2025-26 Programming Tips & Tricks*, https://docs.revrobotics.com/ftc-kickoff-concepts/decode-2025-26/programming-tips-and-tricks
- goBILDA 5203 Yellow Jacket 1:1, https://gobilda.com/5203-series-yellow-jacket-motor-1-1-ratio-24mm-length-8mm-rex-shaft-6000-rpm-3-3-5v-encoder
- goBILDA Pinpoint Odometry Computer, https://gobilda.com/pinpoint-odometry-computer-imu-sensor-fusion-for-2-wheel-odometry (vendor claims).
- Team 254, *FRC-2022-Public* README, https://github.com/Team254/FRC-2022-Public/blob/main/README.md
- Chief Delphi, FRC 971 2016 release thread, https://www.chiefdelphi.com/forums/showthread.php?p=1590553 (forum).
- Repo: `docs/04_launcher.md`, `data/launch_envelope.json`, `src/robustness.py`, `viz/explorer/solver.js`,
  `research/sweeps/sweep_launch.md`, `research/papers_extra/launch_methods_check.md`, `research/papers_extra/cuberobot_decode.md`.

Searched without a usable result: measured FRC/FTC exit-speed or exit-angle SD; measured FTC AprilTag/Limelight heading
error; measured shooter vibration; contact time of a hollow ball in a wheel launcher.
