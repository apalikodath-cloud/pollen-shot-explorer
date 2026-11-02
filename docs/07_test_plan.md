# 07: Prototype test plan (what to measure, and how to judge it)

This is HANDOFF deliverable 7. Every model number used here is PREDICTED (docs/08, docs/05, docs/06). The pass/fail
lines are ASSUMED criteria derived from those predictions. Nothing has been measured on POLLEN yet.

Order matters. Tests 1–4 fix the numbers the model guesses at, so run them before tuning field shots (tests 6–7).

## Equipment

- High-speed video, at least 240 fps, side-on and square to the shot plane. Put a scale board (marked every 5 cm)
  in the plane.
- A second camera behind the shooter, to check sideways aim (azimuth).
- A wheel-speed readout: the motor encoder, logged at 50 Hz or faster.
- Battery voltage logged with the wheel speed.
- A scale reading 0.01 g, and calipers.
- At least 10 POLLEN balls. Mark each one with a stripe all the way round (for spin) and a number.
- The HIVE, or a full-size replica of the CELL mouth, roof and back wall, tilted 30° with the mouth facing away
  from the shooter (the unfavourable side).

## Test 1: Ball properties (feeds the mass and radius bounds)

1. Weigh every ball and measure its diameter at 3 orientations.
2. Record the mean and the range.
- **Pass:** mass is inside 23.5–27.5 g and diameter inside 70–72 mm (the ASSUMED model bounds, research/params_lit.json).
- **Otherwise:** send the numbers back; the model bounds are changed and the sweeps re-run.

## Test 2: Exit state of the shooter (v/u, elevation, spin)

1. Set 3–4 wheel speeds that cover 6.5–9.0 m/s (docs/08 CAD card).
2. Fire 20 shots at each speed.
3. From the side video, measure over the first 0.1 s of flight:
   - exit speed v (from 5 or more frames);
   - elevation;
   - spin (count frames per stripe turn), giving S = ωR/v.
4. Log wheel speed just before and just after each shot.

Report the following for each wheel speed:
- v/u, the mean exit speed divided by the wheel surface speed (π × 0.098 m × rpm / 60);
- the mean and SD of v, of elevation and of S;
- the wheel rpm drop per shot.

- **Use:** v/u replaces the 0.25–0.50 range on the CAD card, and the measured S replaces S 0.5–1.

## Test 3: Repeatability (THE gate for clean entry)

Use the same data as Test 2, at the speed nearest the planned shot. Fire 30 shots if possible.

| Result | Exit speed SD | Elevation SD | Meaning |
|---|---|---|---|
| **Pass** | ≤ 0.04 m/s | ≤ 0.075° | About 95 % of shots fall inside the ±0.075 m/s × ±0.15° clean square (docs/08 §3). |
| **Marginal** | ≤ 0.08 m/s | ≤ 0.15° | Clean entry works on some shots only; field-test to get a real rate. |
| **Fail** | larger | larger | Clean entry (hypothesis A) cannot carry the design. Test the rim-bounce route (hypothesis B, docs/05) next. |

Also report:
- the speed change over the first 3 shots of rapid fire, which shows rpm sag;
- the speed change from a full battery to a battery at 12.0 V.

Either effect alone can use up the whole speed tolerance. Closed-loop wheel speed is assumed (docs/08).

## Test 4: Flight aerodynamics (Cd and spin lift)

1. Fire 10 shots at each of 2 spin levels from the same exit speed and elevation (about 8 m/s, 75°):
   - the shooter's normal spin;
   - the lowest spin you can get, for example a slick hood strip or a hand toss for the drag-only reference.
2. Track the whole flight on the side video, up to and past the apex.
3. Fit Cd from the low-spin paths and Cl from the spin paths (`src/flight.py` gives the model path for any Cd and Cl).

- **Use:** this pins where the clean band sits. Today the unknown Cd and spin lift move it by about 1 m/s or 2°
  (docs/08 §1), which is more than the band is wide.
- **Watch for:**
  - spin lift lower than the 'low' set, which would mean the holes vent the lift (the 'floor' set);
  - a sideways curve on spinning shots, which would point to a non-Magnus hole force.

## Test 5: Rim contact (e and μ)

Drop balls onto a HIVE wall sample (same material) at 3 angles. Film side-on, with and without spin.

- Measure the normal speed ratio e and the spin change.
- Fit μ from the spin change.
- **Use:** docs/05 retention depends mostly on e. The model grid is ASSUMED e 0.3–0.8 and μ 0.2–0.8.

## Test 6: Tuning on the HIVE (unfavourable side)

1. Put the release point at d 0.75–0.85 m from the HIVE pivot plane and at the highest legal release height
   (docs/08 card).
2. Set the hood to the card angle: about 81° with no spin, or 80–80.5° with backspin.
3. Sweep wheel speed in 0.05 m/s steps until shots drop in clean, without touching the HIVE. Then find both edges
   of the band.
4. If no speed works, move the hood 0.5° and repeat. The ±2° adjustment range is for this.
5. Set the shot at the centre of the band.

- **Log:** the band edges in speed, at each hood angle tried.
- **Pass:** a band 0.15 m/s wide or wider at one hood angle. That is the model's PREDICTED 0.15–0.5 m/s.

## Test 7: Scoring rate and its no-spin twin

1. Fire 30 shots at the tuned setting from Test 6. Give each shot an outcome:
   - clean entry, stays in;
   - touches, stays in;
   - bounces out;
   - blocked by roof or wall;
   - misses long.
2. Repeat with the shooter's lowest-spin setup, re-tuned to its own band (the no-spin twin). Report both side by side.
3. Report each rate with a 95 % Wilson interval. 30 shots give about ±0.17 at p = 0.5.

- **Pass:** the team decides the target rate. A useful rule: the lower end of the 95 % interval is above the rate
  you need in a match.
- **Do not:** claim a rate from fewer than 20 shots, or from one good shot.

## Test 8 (optional): The far-side demo shot

Try the video shot: d 1.75 m, h 0.5 m, 8.45 m/s, 75.6°, S 1.0. The model's window there is only about ±0.05 m/s
× ±0.1°, so expect a low rate. It is a demonstration, not a design point (docs/08 §4).

## What to send back

- A CSV with one row per shot: test, ball number, wheel rpm before and after, battery V, v, elevation, S, outcome.
- The raw videos.

The model is then re-run with the measured v/u, S, Cd, Cl, e and μ, giving new targets and a new predicted rate
to compare with Test 7.
