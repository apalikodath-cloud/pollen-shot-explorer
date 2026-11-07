# Feasibility report: a knuckleball shooter for BioBuzz POLLEN and NECTAR

Status: final report of the knuckleball research task, 2026-11-05. It draws on the five companion notes:
- `LITERATURE_REVIEW.md`: what the published work shows, with DOIs and verification labels;
- `AERODYNAMIC_HYPOTHESES.md`: nine candidate mechanisms, ranked;
- `FLYWHEEL_ANALYSIS.md`: 72 mm vs 98 mm wheels, spin control, contact regimes;
- `CFD_TEST_PLAN.md`: CFD results so far and the runs still needed;
- `GPU_OPTIMIZATION.md`: how to make those runs cheaper.

Labels used here:
- **[Lit]** published result;
- **[V]** vendor or game-manual figure;
- **[P]** prediction of the repo CFD or contact model, **not validated** against a real ball or launcher;
- **[D]** derived by hand from the other labels;
- **[A]** assumption;
- **[M]** measured.

**There are no [M] numbers for POLLEN or NECTAR flight yet.** Every conclusion below is a prediction that the tests in §6 can confirm or overturn.

## 1. Answer

**Question.** Can an FTC shooter with a 72 mm or 98 mm flywheel realistically and repeatably produce a sudden-breaking knuckleball with NECTAR or POLLEN?

**Short answer: no, not a useful one.**

### 1.1 Why not

1. **The regime is wrong [Lit].** Large, erratic knuckle forces need the drag crisis. Baseballs knuckle at Re ≈ 1.5e5 to 1.8e5 and soccer balls at Re ≈ 2.5e5 to 3.6e5. A POLLEN shot that can score is launched at 4.5 to 9 m/s, so Re = 2.1e4 to 4.3e4 [D]. That is 4 to 10 times too low. At these Re the sphere wake is subcritical: it sheds at St ≈ 0.2, and the shedding plane wanders slowly and smoothly.
2. **The forces are small [P].** At zero spin the POLLEN CFD gives:
   - a random side-force coefficient with sd ≈ 0.02 (0.029 on the finer grid);
   - Gaussian increments (kurtosis ≈ 0), so no jumps;
   - a random (fluctuating-part) miss at 3 m of p95 ≈ 0.3 to 1 cm across the low-spin runs, and 1.0 cm on the finer grid;
   - a steady, orientation-dependent side coefficient of 0.016 to 0.046, which is **0.7 to 2 cm** at 3 m.

   The CELL opening is 50.8 cm wide [V].
3. **The holes damp the knuckle [P].** A sealed smooth sphere in the same solver fluctuates 3 times more (sd 0.066, p95 miss 3.8 cm). POLLEN's 26 holes over the whole shell spread and weaken the wake asymmetry. A Wiffle ball, by contrast, has holes on one hemisphere only and shows CL 0.1 to 0.6 by orientation [Lit].
4. **No sudden break exists to exploit [Lit, P].**
   - Even big-league knuckleballs fit smooth curves to within about 1 cm [Lit, Nathan 2012]. Their "break" is pitch-to-pitch unpredictability, not a jump in mid-flight.
   - True wake switching takes 10² to 10³ D/U [Lit], while a 3 m flight is 42 D/U [D].
   - The "late break" a viewer sees comes from y ∝ t²: half of a constant-force deflection happens in the last 29 % of the flight [D].
5. **Higher speed does not help [D, P].** For a fixed path length, the deflection y = CρAL²/(4m) does not depend on speed. The coefficients change little between Re 2.0e4 and 4.7e4 [P].

### 1.2 What does work

A **Magnus curve**: S = 0.25 to 1 gives Cl = 0.15 to 0.36 [P], so **6.6 to 15 cm** at 3 m. It is smooth and predictable from the launch spin. It looks "late" for the same t² reason.

### 1.3 Orientation control

**Not necessary, and impractical in a match.**
- It would buy at most 0.7 to 2 cm at 3 m [P].
- A wheel launcher takes the ball in at a random orientation [A].
- It becomes worth building only if the orientation tests in §6 measure mean offsets of more than about 4 cm at 3 m (§4.4).

### 1.4 Confidence

**Medium for POLLEN, low for NECTAR.** The main uncertainties:
- the CFD fluctuation statistics are not converged. The D64 to D192 validation runs (`CFD_TEST_PLAN.md` §4.1.1) show that:
  - the mean forces converge: Cd within 2.2 % between D128 and D192, extrapolated Cd ≈ 0.56 at S = 0 [P];
  - sd Cy and the fluctuating miss scatter by ±50 % between grids, lattice Mach numbers and collision models, with no trend. This is most likely the sampling error of single 135 D/U records;
  - across all 12 low-spin (S ≤ 0.05) validation runs, sd Cy stays within 0.017 to 0.035 and the fluctuating 3 m miss p95 within 3 to 12.5 mm [P]. That bound is what the answer rests on, and it does not change it;
  - Magnus lift at S = 0.5 is still about 18 % lower at D192 than at D128;
- the CFD ball is held at fixed spin and does not rotate freely;
- no launcher or flight has been measured;
- NECTAR's mass and hole layout are unknown.

## 2. Low-spin knuckle vs high-spin break

| | Low-spin "knuckle" | High-spin break (Magnus curve) |
|---|---|---|
| Spin parameter S = ωR/U | ≤ about 0.04 | 0.25 to 1 |
| Spin at 7 m/s [D] | ≤ 75 rpm | 470 to 1880 rpm |
| Hole pattern turns over 3 m (θ = S L / R) [D] | ≤ about 190° (S 0.04); 24° at S 0.005 | many turns |
| Dominant force | steady orientation force C 0.016 to 0.046 plus random wake wander sd about 0.02 to 0.03 [P] | Magnus lift Cl 0.15 to 0.36 [P] |
| 3 m deflection | 0.7 to 2 cm steady + about 0.3 to 1 cm random (p95) [D from P] | 6.6 to 15 cm, along a fixed direction [D from P] |
| Direction | set by the hole pattern, so random unless orientation is indexed | set by the spin axis, so chosen by the wheel layout |
| Kind of "break" | rapid but continuous (§1 of `AERODYNAMIC_HYPOTHESES.md`), sub-centimetre path wobble | perceptual: smooth, constant curvature |
| Repeatability | predicted poor in direction, small in size; **not measured** | predicted good if spin is controlled; **not measured** |
| Game value | none: well inside the CELL | real: can bend a shot round an obstacle or change the entry angle |

**Where the knuckle window ends.** The window is set where the spin-driven lift overtakes the orientation force:
- the CFD at the "btw" orientation [P] gives Cl = 0.046 at S = 0, 0.025 at S = 0.02, 0.036 at S = 0.05, and 0.152 at S = 0.25;
- the published pickleball slope, Cl = 0.195 S [Lit, Steyn et al.], is not a POLLEN fact; it gives 0.008 at S = 0.04;
- both put the crossover between S ≈ 0.04 and 0.1.

The S = 0.1 run (finished after the first draft) gives Cl = 0.060 [P], already above the largest orientation force at S = 0 (0.046). The crossover is therefore between S ≈ 0.05 and 0.1, and spin dominates from S ≈ 0.1 up.

## 3. Launch-condition analysis

### 3.1 Speed

**Inputs.**
- Re = 4731 × U, with U in m/s [D].
- Flight time over 3 m with drag: t = (λ/U)(e^{L/λ} − 1). Here λ = 2m/(ρACd) ≈ 17 m, so t = 3.28 m / U [D].

| Launch speed | Re | Time to 3 m | Spin at S = 0.005 / 0.04 / 0.25 / 0.5 / 1 |
|---|---|---|---|
| 4.5 m/s | 21 300 | 0.73 s | 6 / 48 / 302 / 604 / 1208 rpm |
| 7 m/s | 33 100 | 0.47 s | 9 / 75 / 470 / 940 / 1880 rpm |
| 9 m/s | 42 600 | 0.36 s | 12 / 97 / 604 / 1208 / 2417 rpm |

**What speed changes.**
- Scoring shots need 4.5 to 9 m/s [D, `FLYWHEEL_ANALYSIS.md` §2].
- Within that band:
  - Cd changes from 0.611 (Re 2.0e4) to 0.594 (3.3e4) and 0.587 (4.7e4) [P], a 4 % fall;
  - the deflection per metre of path does not depend on speed (§1.1, item 5);
  - a faster shot flattens the arc, which shrinks the effective CELL opening and raises the impact speed [D].
- **Choose the lowest speed that makes the shot.**

### 3.2 Spin and spin axis

- The Magnus force is perpendicular to both the spin axis and the velocity.
- On a wheel launcher, the spin axis is parallel to the wheel axles [D]:
  - **vertical axles** give side spin, so the shot curves left or right;
  - **horizontal axles** give back- or top-spin, so the shot rises or dips.
- A hood shooter always gives backspin, at S ≈ 1.06 to 1.20 in the contact model [P]. That is a rising Magnus shot, **never a knuckle**.
- A dual-wheel shooter gives S = (R_b / r_c) × (1 − r) / (1 + r), with r the exit-speed ratio [P]:
  - |S| ≤ 0.04 needs the two wheels' **exit** surface speeds within about 6 to 7 %;
  - |S| ≤ 0.005, a pattern that stays nearly still (24° over 3 m), needs them within about 1 %;
  - unequal wheel inertia alone gives S = 0.05 (98 mm) to 0.087 (72 mm) even with matched set-points [P], because the wheels droop differently during the 5 to 15 ms contact.
- Gyro-spin, with the axis along the flight path, would average the orientation force without adding Magnus lift. A two-wheel launcher cannot produce it [D].

### 3.3 Orientation

- POLLEN has 26 holes over the whole shell [CAD]. The CFD gives:
  - 0.046 for the "btw" orientation and 0.016 to 0.017 for "hf" and "o3" [P];
  - a spread of about 0.03 between orientations, or **1.3 cm** at 3 m [D].
- The literature agrees that the hole layout matters at the centimetre level:
  - pickleball hole patterns change the 95 % landing ellipse by 29 % at Re ≈ 6.8e4 [Lit, Lin et al. 2026];
  - pickleball and Wiffle coefficients are **not** POLLEN facts.
- **Verdict:**
  - **not necessary** for any shot;
  - **beneficial** only if it is measured to give a steady offset of more than about 4 cm at 3 m;
  - **impractical** in a match, because an intake that indexes a 26-hole pattern adds a mechanism and cycle time for about 1 cm.

### 3.4 Sensitivity

| Quantity | How the 3 m deflection responds | Label |
|---|---|---|
| Path length L | ∝ L² | [D] |
| Launch speed (fixed L) | none to first order | [D, P] |
| Spin S below about 0.04 | small; the pattern turns, which partly averages the orientation force | [P] |
| Spin S from 0.25 to 1 | Cl rises 0.152 → 0.357, so about 6.6 → 15.4 cm | [P] |
| Ball mass | ∝ 1/m (a 10 % heavier ball deflects 9 % less) | [D] |
| Grid resolution (CFD) | D128 → D192 raises sd Cy by 50 % and lowers Cl at S = 0.5 by 18 % | [P] |
| Wheel droop mismatch | adds S of 0.05 to 0.09 when inertia differs by 2× | [P] |

### 3.5 Repeatability

The task asks whether a knuckleball can be thrown **repeatably**. No shot is claimed repeatable until the tests in §6 measure it.

**Predicted [P]:**
- **Low-spin shot.** The direction of the random part changes from shot to shot by definition. The steady part depends on the uncontrolled orientation. The size of both stays below about 2 cm.
- **Magnus shot.** Repeatable to the extent that exit spin is repeatable.
  - The contact model ties spin to the grip regime; in the friction-limited regime spin varies with tread wear and ball surface.
  - With a hood, ±10 % spin gives about ±1 cm at S ≈ 1 [D].
  - Shot-to-shot wheel droop is the main source of scatter, and it is larger for 72 mm wheels (§4).

### 3.6 Force reversals and thresholds

**None found in the POLLEN range.**
- **Drag.** Cd falls smoothly from 0.611 to 0.587 between Re 2.0e4 and 4.7e4, with no crisis [P]. The smooth-sphere crisis is at Re ≈ 3.7e5 [Lit, Achenbach].
- **Lift sign.** Lift stays positive and rises monotonically from S = 0.25 to 2 [P]. The low-spin values (0.046, 0.025, 0.036 at S = 0, 0.02, 0.05) are dominated by orientation.
- **Inverse Magnus.** It has been reported only near the drag crisis, plus weakly near Re 4.6e4 at low spin [Lit, Maccoll via Muto 2012]. It is marginal for the fastest, lowest-spin POLLEN shots, and it is not seen in the CFD.
- **Wiffle sign flip.** A Wiffle ball flipped sign near Re 5.5e4 at one orientation [Lit, Rossmann & Rau 2007].
  - This is above the POLLEN range.
  - NECTAR's fastest shots reach about 5.5e4 [D], so it is the one threshold worth testing with NECTAR.

## 4. 72 mm vs 98 mm flywheel

**Recommendation: 98 mm.** Use goBILDA 96 mm Gecko or Hogback wheels with the 82 mm steel flywheel, **identical on both wheels** if two wheels are used.

| Criterion | 72 mm + 60 mm flywheel | 98 mm + 82 mm flywheel | Source |
|---|---|---|---|
| rpm for the needed speed | 1.36× higher | lower: hood about 2000 to 4000 rpm, dual 1100 to 2100 rpm | [D] |
| Stored energy at 4000 rpm | 8.8 J | 37 J | [D] |
| rpm drop per shot at about 8 to 9 m/s | 500 to 540 | 180 to 250 | [P] |
| Recovery, 1 motor | 0.04 s | 0.08 to 0.16 s | [P] |
| Spin from a 2× inertia mismatch (dual) | S 0.087 | S 0.050 | [P] |
| Hoop stress at 8000 rpm, soft tread | 1.1 MPa | 2.0 MPa (not needed: 4000 rpm is enough) | [D] |

**Why 98 mm wins.**
- The shot needs only modest surface speed, so direct drive at 1100 to 4000 rpm suffices.
- Its larger stored energy gives smaller per-shot droop, which is the main source of spin and speed scatter.
- It is less sensitive to mismatched wheels when a low spin is the goal.

**When 72 mm is the better choice.** Only in a rapid-fire design that values recovery time over per-shot consistency.

**Neither size enables a knuckleball.** Wheel size changes the scatter, not the aerodynamics.

**Recommended configurations** (if a "breaking" shot is wanted at all):
1. **Scoring shot.** Single 98 mm wheel and a fixed hood, giving backspin at S ≈ 1 [P].
   - This is the HANDOFF scope.
   - The Magnus lift is steady and should be included in the aim model, not fought.
2. **Curving shot.** Two 98 mm wheels with **vertical** axles and a speed ratio set for S ≈ 0.25 to 0.5.
   - This gives a side curve of about 7 to 11 cm at 3 m [P].
   - The speed ratio is the control knob.
   - Use the lowest launch speed that makes the shot.
3. **Low-spin shot (for testing only).** Two matched 98 mm wheels with r = 1 at exit.
   - This is the twin of every spin shot: the no-spin path.
   - Expect a drag-only path with up to about 2 cm of combined steady offset and random wander.

## 5. NECTAR

- **Size and Re.** About 91 mm [V], so Re is 1.28 times POLLEN's at the same speed: 2.7e4 to 5.5e4 for 4.5 to 9 m/s [D].
- **Mass and holes.** Not published. The hole layout is unknown [V: the manual says only "with holes"].
- **No CFD.** The POLLEN predictions do not transfer until the mass and hole layout are known.

**What can be said.**
- The deflection per unit C scales as A/m. With A = 6.5e-3 m², NECTAR moves more than POLLEN per C only if its mass is below about 41 g [D: 24.95 g × 6.5 / 3.97].
- The fastest NECTAR shots touch Re ≈ 5.5e4, where a Wiffle ball reversed its side force [Lit].
  - That is the only place in this whole study where a force reversal is plausible.
  - It is untested.

## 6. Testable predictions and the measurements needed

### 6.1 Predictions

Each prediction is stated so that a test can fail it.

| # | Prediction [P/D] | Test | Overturned if |
|---|---|---|---|
| T1 | No-spin, random-orientation POLLEN shots scatter laterally by an extra sd ≤ 0.5 to 1 cm at 3 m beyond the launcher's own scatter | 50 shots with S < 0.005 vs 50 taped (sealed) shots; target-plane video | extra sd > 2 cm, or a bimodal landing pattern |
| T2 | The no-spin lateral scatter does not grow with launch speed between 4.5 and 9 m/s | T1 at 3 speeds | scatter grows by > 50 % |
| T3 | At fixed orientations, mean lateral offsets differ by 0.7 to 2 cm at 3 m | ≥ 20 shots at each of 3 orientations (btw / hf / o3), S < 0.005 | spread > 4 cm, which would make orientation control worthwhile |
| T4 | A taped (sealed) POLLEN wanders more than an open one: about 3× the side-force fluctuation | T1 with taped vs open balls | taped ≤ open (tape roughness also changes the wake: note it) |
| T5 | Video residuals from a smooth (drag + constant side force) fit stay at the camera noise level; no jumps | 240 fps or faster, two views, Nathan-style rms residual | rms residual > 2× the taped-ball value with outliers |
| T6 | Cd = 0.59 to 0.61, nearly flat over 4.5 to 9 m/s | speed decay from two-view video over 3 m | Cd varies > 15 % or shows a step |
| T7 | A Magnus side curve at S ≈ 0.25 / 0.5 / 1 gives about 6.6 / 9 to 11 / 13 to 15 cm at 3 m relative to the no-spin twin | dual wheels, vertical axles, measured spin | outside ±40 % (the CFD is not converged) |
| T8 | Dual-wheel exit spin follows S ≈ (1 − r)/2 × R_b/r_c, so |S| ≤ 0.005 needs exit speeds within about 1 % | speed-ratio sweep 0.95 to 1.05, 20 shots each | |S| scatter at r = 1 > 0.02 |

### 6.2 Measurements needed

In priority order:
1. **Ball properties.** POLLEN and NECTAR mass (10 balls each), diameters in 3 axes, and hole count, sizes and layout on the real parts.
2. **POLLEN contact properties.** Diametral stiffness (load–displacement, 0 to 15 mm) and the tread–ball and hood–ball friction coefficients. These decide the contact regime (`FLYWHEEL_ANALYSIS.md` §4).
3. **Launch.** Exit speed and spin with spin axis: 240 fps video with a marked ball, 20 shots per setting, reporting mean and sd. Plus the wheel rpm trace through a shot (≥ 1 kHz encoder).
4. **Flight.**
   - Lateral scatter at 3 m: no-spin open, no-spin taped, and indexed orientations (T1 to T4).
   - Speed decay (T6) and two-view trajectory residuals (T5).
5. **NECTAR.** All of the above. Plus the Re ≈ 5.5e4 orientation test for a side-force reversal.
6. **CFD still to run** (`CFD_TEST_PLAN.md` §4):
   - the seed-spread, sealed-sphere and lateral-blockage validation runs (grid, Mach, FP32 and collision-model runs are done: `CFD_TEST_PLAN.md` §4.1.1);
   - long 1000 D/U runs for wake switching;
   - ensembles started from t = 0 with flight-length statistics;
   - the free-rotation option.
   - The decision rules in `CFD_TEST_PLAN.md` §7 were written before these results. A discontinuous knuckle is declared only if a bimodal state with jumps > 0.1 in C **and** > 5 cm deviations in ≥ 5 % of flights both appear.

## 7. What would change this answer

- **T1 or T3 fail high.** If measured scatter or orientation offsets exceed about 4 cm at 3 m, the CFD is under-predicting. Orientation indexing would then be worth a design study.
- **Free-rotation CFD shows a coupling instability.** If the ball's own torque spins it up from S ≈ 0 into a state with a large side force, a low-spin launch could produce a real "break". The CFD predicts only about 0.8° of free rotation over 3 m at S = 0, so this is unlikely.
- **NECTAR is light, or its holes are on one side.** Either would let it behave more like a Wiffle ball. NECTAR would then need its own CFD and tests.
- **The rules change.** A rule allowing longer shots (L ≫ 4 m) would scale every deflection as L².

## Sources

Literature: every paper cited with [Lit] is listed with DOI, access level and verification label in `LITERATURE_REVIEW.md`. Where a summary row and a detailed entry differ, the entry governs.

Game manual and products (read 2026-11-05):

1. **FIRST Tech Challenge BIOBUZZ Competition Manual, Team Update 07 (2026-10-29).**
   - URL: https://ftc-resources.firstinspires.org/ftc/game/cm-html/BIOBUZZ%20Competition%20Manual%20-%20TU07.htm
   - Used for: §9.8 scoring elements (POLLEN about 2.8 in, NECTAR about 3.6 in, "plastic ball with holes", no mass given); CELL opening about 20 × 14 × 12 in; HIVE pivot 43.95 in; rules R102, R105, R201, R501, R503, R801, G405, G406, G417, G418.
   - The glossary definition of LAUNCH was not read.
   - Game resources index: https://ftc-resources.firstinspires.org/ftc/game
2. **goBILDA 5203 Yellow Jacket, 1:1 (6000 rpm).** 12 V, 9.2 A stall, 1.47 kg·cm stall torque.
   - https://www.gobilda.com/5203-series-yellow-jacket-motor-1-1-ratio-24mm-length-8mm-rex-shaft-6000-rpm-3-3-5v-encoder/
3. **goBILDA 5203 Yellow Jacket, 3.7:1 (1620 rpm).**
   - https://www.gobilda.com/5203-series-yellow-jacket-planetary-gear-motor-3-7-1-ratio-1620-rpm-3-3-5v-encoder/
4. **REV HD Hex Motor, REV-41-1291.** 6000 rpm, 0.105 N·m, 8.5 A.
   - https://www.revrobotics.com/REV-41-1291
5. **goBILDA steel flywheel, 82 mm.** 152 g, 1651 g·cm² in the spec table; the page title says 840 g·cm², a conflict.
   - https://www.gobilda.com/steel-flywheel-82mm-diameter-152g-840-g-cm
6. **goBILDA steel flywheel, 60 mm.** 115 g, 551 g·cm².
   - https://www.gobilda.com/steel-flywheel-60mm-diameter-115g-551-g-cm/
7. **goBILDA GripForce Gecko wheels.**
   - 72 mm, 52 g, 30A: https://www.gobilda.com/gripforce-gecko-wheel-14mm-bore-72mm-diameter/
   - 96 mm, 105 g, 30A: https://www.gobilda.com/gripforce-gecko-wheel-14mm-bore-96mm-diameter/
8. **goBILDA Hogback traction wheels, 50A.**
   - 72 mm, 55 g: https://www.gobilda.com/hogback-traction-wheel-72mm-diameter-50a-durometer/
   - 96 mm, 82 g: https://www.gobilda.com/hogback-traction-wheel-96mm-diameter-50a-durometer/
9. **AndyMark BIOBUZZ scoring elements page.** Could not be read (HTTP 429), so the ball mass is taken from the repo HANDOFF record of the AndyMark listing.
   - https://andymark.com/products/biobuzz-scoring-elements

No vendor page read publishes wheel or motor rotor inertia. Those values in `FLYWHEEL_ANALYSIS.md` are [A].
