# MEASURE: filming POLLEN to get Cd, Cl and the exit state (PM-018)

Nothing about POLLEN's flight has been measured yet (research/COMPLETENESS.md §1, last row). The three inputs that
matter most are:

- spin lift Cl(S)
- drag Cd
- exit speed and grip, v/u

(research/MISSING_EFFECTS.md §3, tests T1 and T2.) This page explains how to measure them with one phone camera
and the kit in `viz/measure/`:

- `measure.html`: click the ball frame by frame; it runs the fit in the page.
- `src/fit_aero.py`: the same fit offline, from the page's CSV.

Labels follow HANDOFF §5:

- **user**: typed in or measured by you
- **ASSUMED**: a default nobody has measured
- **derived**: computed here, from synthetic `physics.js` tracks unless stated otherwise
- **PREDICTED**: a model path

No number on this page is a POLLEN measurement. Literature or pickleball coefficients are not POLLEN facts either.

## 1. What you need

- A camera that films **240 fps** or faster. Phone slow motion works.
- A **scale bar of 1 m or more**, such as a metre stick or a taped board with marks, placed **in the flight plane**.
- A plumb line or a level, and two bright lights. A plain, dark backdrop behind the flight helps the clicking.
- At least 10 POLLEN balls. Weigh them (0.01 g) and measure the diameter (calipers, 3 axes); this is T0. Draw a
  stripe all the way round each ball so spin can be counted.
- The shooter, with a wheel-speed readout (tachometer or encoder log).
- A thermometer and the venue altitude, for the air density. The explorer's Venue air box gives ρ; type it into
  the page.

## 2. Camera set-up

1. **Square to the flight plane.** Place the camera on a tripod 4–6 m from the flight line, with the lens axis
   perpendicular to the plane. If the camera is turned by an angle a, horizontal lengths shrink by cos a: 8°
   already costs 1 % (derived).
2. **Scale bar in the flight plane.** Hold the bar or board where the ball flies, along the flight line. A bar
   that sits d in front of or behind the plane, with the camera D away, gives a scale error of d/D. For example,
   5 cm at 5 m is 1 % (derived).
3. **Why the scale matters most.** The scale is the largest error in the whole method. A +1 % scale error moves
   the fitted Cd from 0.50 to 0.52 (+4 %) and a single Cl from 0.25 to 0.20 (−19 %). These are derived values
   from a synthetic 7 m/s, 55° track. By contrast, a +4 % error in Cd alone leaves Cl at 0.250. Section 5 has the
   gravity check that catches a bad scale.
4. **Framing.** Use the 1× lens, not ultra-wide, and keep the whole flight in the middle 80 % of the frame.
   Lens distortion is not modelled. The more frames of flight you get, the better: aim for 0.7 s or more.
5. **Shutter and light.** Use 1/1000 s or faster. At 7 m/s a 1/1000 s exposure smears the ball over 7 mm
   (derived). That needs bright, even light from the camera side. Avoid flicker from mains LEDs if the clip
   shows banding.
6. **Level.** Film a plumb line or a level edge once. The page's Level tool takes two clicks on a line that should
   be horizontal. Without it, the image rows are taken as level.
7. **Frame rate.** Write down the **capture** rate. Phone slow motion often stores 240 fps capture as a 30 fps
   file; the page asks for both and times every frame by the capture rate.

## 3. The tests

### 3a. Drop test: Cd with no launcher and no spin

Drop a ball from rest, from as high as you safely can, in front of the scale bar. Track the fall.

- **Settles:** Cd at zero spin, with nothing from the shooter mixed in (T1, Cd row).
- **How well:** with one drop at 240 fps and 4 mm click noise on every frame (derived), the 95 % error on Cd is
  about ±0.008 from 4 m, ±0.026 from 2.5 m and ±0.085 from 1.5 m. Short drops barely show drag.
- **Limit:** a drop does check the scale against gravity (sd about 0.3 % from 4 m, derived), but on a drop the
  scale trades off against Cd (correlation about +0.97, derived): freeing the scale widens the 95 % Cd error from
  ±0.008 to about ±0.033 at 4 m. Shot A (3b) separates the two much better (correlation about −0.44), so do the
  gravity check on shot A and fit the drop on the clicked bar.

### 3b. Twin test: Cl from a backspin shot beside its no-spin twin

Use the same hood angle, the same wheel rpm, the same camera and the same scale.

- **Shot A, no spin (the twin).** A no-spin ball from the shooter: a flat-feed or two-wheel set-up, or an
  underhand throw at the same speed and angle if the shooter cannot fire without spin. Fit A gives v0, the launch
  angle, Cd and the gravity check of the scale.
- **Shot B, backspin.** The normal hood shot. Fit B holds A's Cd and fits launch plus Cl. The page draws the
  no-spin twin path (same launch, same Cd, no lift) dashed beside it, and prints how far lift moved the ball by
  the last tracked frame.
- **Settles:** Cl over the range of S that this shot covers (T1, Cl row). It also shows whether lift is
  detected at all: the 95 % interval either excludes 0 or does not.
- **Order:** film n ≥ 10 of each, alternated A, B, A, B, so that drift in the shooter, battery or air shows up in
  both.
- **Also film** (COMPLETENESS T1):
  - wheel-above topspin at the same rpm, entered as a negative ball rpm (spin source: ball rpm)
  - 60–70° lobs, which reach the high S near the apex
  - a taped-hole ball, as the control for the holes

### 3c. Exit speed and grip, v/u

Log the wheel rpm for each shot (user) and type it into the page.

- The page computes the wheel surface speed u = rpm · 2π/60 · 0.049 m, using the 98 mm wheel (user), and
  v/u = v0 / u.
- v0 is the speed at the first tracked frame. Start tracking as close to the hood exit as the frame allows.
- **Settles:** the grip v/u at this rpm (T2). Repeat at 3–4 rpm settings to cover 6.5–9 m/s
  (docs/07_test_plan.md, Test 2).

### 3d. Spin from the video

Count the stripe on the ball near the exit. If one full turn takes F frames, the ball rpm is 60 · fps / F.

- For precision, count N turns over F frames: rpm = 60 · fps · N / F. Being off by ±1 frame is a relative error
  of 1/F.
- At 2000 rpm and 240 fps one turn is 7.2 frames, so counting 3 turns over about 22 frames gives about ±5 %
  (derived). Below about 3 frames per turn the count can alias. Above 4800 rpm at 240 fps, film faster.
- Type the ball rpm, or the frames per turn, into panel 3. Then choose "Ball rpm from video (user)" for shot B.
  S0 = ωR / v0 at release is derived from it.
- Without a spin count the page uses S0 = 1.0, the ideal hood (ASSUMED). In that case only the product of the
  lift slope and the spin is measured, not Cl(S) itself.
- **Settles:** S_exit for the hood at this rpm (T2).

## 4. How much data each result needs

The table below shows the error for one shot pair, using a synthetic 7 m/s, 55° shot with Cd 0.50 and Cl 0.25
(all derived, ASSUMED truth). It assumes about one click every 2 frames.

| Set-up | sd of Cd | sd of Cl | No-spin twin separation at the last frame |
|---|---|---|---|
| 240 fps, 4 mm click noise, 0.7 s tracked | 0.0084 | 0.0098 | 148 mm |
| 120 fps (same noise, same 0.7 s) | 0.0117 | 0.0130 | 148 mm |
| 60 fps | 0.0158 | 0.0191 | 148 mm |
| 240 fps, 2 mm noise | 0.0042 | 0.0049 | 148 mm |
| 240 fps, 8 mm noise | 0.0168 | 0.0196 | 148 mm |
| 240 fps, only 0.4 s tracked | 0.0237 | 0.0253 | 64 mm |

Reading the table:

- **The length of track matters most.** Track the whole flight you can see.
- **Clicking error halves with careful clicks.** The loupe (Z) helps.
- **The 0.5 px clicks on the scale bar add to these values.** The page carries that click error into Cd and Cl.
  On a 1 m bar 250 px long it is ±0.55 % (95 %, ASSUMED 0.5 px per end).
- **Spin decay hardly matters here.** The spin decay k is ASSUMED to be 0.03 1/s. A 10× faster decay (true 0.3,
  fitted 0.03) left a single fitted Cl unchanged at 0.25 (derived) over 0.7 s. T3, the spin-down test, measures k.
- **Cl(S) needs several spin settings.** One shot sets one Cl over its S range, and the page flags "cannot
  separate" when asked for more. A slope and a cap, or a slope and S0, need several spin settings.

These are synthetic values. **They make no claim about how repeatable the real shooter is.** Report the real
spread between your throws as measured (Test 3 in docs/07_test_plan.md is the repeatability test).

## 5. Gravity check of the scale

Shot A has no lift, so its sag is set only by gravity (9.81 m/s²) and drag. Fit A also fits a length scale,
video metres / true metres. On a 240 fps, 4 mm-noise shot it is separable, with sd about 0.2–0.3 % and
correlation with Cd about −0.44 (derived).

- **If it agrees** with 1.000 within the errors, the clicked bar is good.
- **If it disagrees,** the page says so in red. Either the bar was out of the flight plane or the camera was not
  square, or the "no-spin" ball had some spin. Check the bar first.
- **The "Length scale" select** chooses which scale is used:
  - "Clicked scale bar" (default) carries the bar's click error.
  - "Gravity check from shot A" uses A's fitted scale for both shots and carries its error into B.
- **Example (derived, ± is 1 sd):** on a track with a +1 % scale error, the gravity-checked fit gave scale
  1.009 ± 0.003, Cd 0.502 and Cl 0.246 ± 0.018. The truth (ASSUMED) was 0.50 and 0.25. With the clicked scale the
  same track gave Cd 0.523 and Cl 0.201 ± 0.018. The no-spin twin is shot A of the same pair.
- **Caution:** use gravity mode only when shot A truly has no spin. Spin on A would be read as a scale error.

## 6. Running the fit

1. Open `viz/measure/measure.html`; see viz/measure/README.md for how to serve it. "Load demo" shows the
   workflow on a synthetic track.
2. Shot A: load the video, set the fps, click the scale bar ends, then click the ball on every frame or every 2nd
   frame. Press **Fit A**.
3. Shot B: switch to B, load its video and track it. Set the spin source and the lift model ("One Cl over this
   shot" unless you have several spin settings). Press **Fit B**.
4. Read the flags. "Cannot separate X and Y" and "X is weakly set" mean that number is not measured by this track.
   Do not copy it into the explorer.
5. Press **Copy** under Track data and keep the CSV with the clip. Offline, the Python fit is:

```
python -B -m src.fit_aero track.csv --lift single --boot 200
python -B -m src.fit_aero track.csv --scale gravity
```

The CSV starts with `#` lines holding the scale, level, ball, air and spin settings (user or ASSUMED). The columns
are `shot,frame,t_s,x_m,z_m,x_px,y_px`, with x and z levelled, scaled, and z up.

**Combining throws.** Fit each throw on its own. Give the mean, and the spread between throws (sd and n),
**next to** the per-throw error from the page. If the spread is much larger than the page's error, the shots
differ (feed, battery, ball). That spread is a finding to report, not something to average away.

## 7. Entering the results in the explorer

All of these are in **Advanced settings** (viz/explorer).

- **Spin lift:** go to *Spin lift options → Lift table S:Cl* and enter `S:Cl` pairs, for example
  `1.26:0.258, 1.9:0.30`.
  - Each twin-test pair gives one point. The page prints the pair to paste: the middle S of the tracked part, and
    the fitted Cl.
  - The explorer draws straight lines between the points and holds the last value flat. Below the first point it
    runs linearly down to (0, 0).
  - Label these numbers as measured (user) in your notes, and keep the no-spin twin result beside each one.
- **Drag:** go to *Air model* and pick the nearest preset: Low drag (Cd 0.33), Nominal (0.5) or High drag (0.9).
  The explorer has **no free Cd box** yet (open item). A lift table you enter replaces the preset's lift.
- **Grip v/u:** pick the nearest of 0.25, 0.30, 0.42 and 0.50. There is no free v/u box yet (open item).
- **Venue air:** enter the temperature, altitude and humidity of the venue where you filmed.

## 8. What each test settles, and what it does not

| Test | Settles | Rows (COMPLETENESS / MISSING_EFFECTS) |
|---|---|---|
| T0 weigh and measure | mass and diameter for the fit (user) | mass, radius bounds |
| Drop (3a) | Cd at zero spin, no launcher | T1 (Cd); MISSING_EFFECTS §3 |
| Twin A + B (3b) | Cl over the shot's S range, lift detected or not, Cd at launch speed, scale check | T1; Magnus row, perforation row |
| Lobs, topspin, taped-hole ball | Cl at high S near the apex, the topspin sign, the effect of the holes | T1; near-apex row |
| Wheel rpm + video (3c, 3d) | v/u and S_exit at each rpm | T2; max backspin row, friction row |

**Not settled by this kit:**

- spin decay k (T3, the spin-down test)
- the squeeze curve N(δ) (T4)
- rim bounce e and μ (T5)
- entry rates into the CELL (T6)
- the repeatability of the shooter (docs/07_test_plan.md Test 3)

One shot pair is one measurement.
