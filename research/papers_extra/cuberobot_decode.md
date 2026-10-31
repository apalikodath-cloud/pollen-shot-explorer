# FTC team code, DECODE 2025-26 (kleongf/FTC_Decode and kleongf/Decode): what the "live aero simulation" really is

source_id: `cuberobot_decode`
Read: 2026-10-30, research agent for PM-001. I re-verified the lead's earlier findings by shallow-cloning both repositories into a temp folder outside the project. The code was read with grep and cat only; nothing was built or run.

## 1. Citation, access, review status

| Field | Value |
|---|---|
| Source | GitHub repositories by `kleongf`: **FTC_Decode** (README: "An archived snapshot of DECODE-season FTC robot software built on SDK 11.0 and Pedro Pathing 2.1"), HEAD `6aa84a87eaa09c862eb707c4f604191bbcedb1d1`, commit date 2026-08-18. **Decode** (older season code), HEAD `205af900f9f64b267cc908b785247512d7187086`, commit date 2026-08-18. |
| Team attribution | The lead attributes this code to FTC team 23641 "Cuberobot". **I did not verify that here.** Neither repo's README or code contains "23641" or "Cuberobot". |
| Review status | **Observation / unreviewed.** It is team robot code with no paper, no measurement report and no data files. |
| Access | Full source (public GitHub). |
| Game ball reference | FTC DECODE Competition Manual glossary (archived manual-16) and Team Update 09 (6 Nov 2025), §9.9. Both PDFs were read in full text with pdftotext. |

URLs tried:
- https://github.com/kleongf/FTC_Decode (git clone --depth 1: OK)
- https://github.com/kleongf/Decode (git clone --depth 1: OK)
- https://ftc-resources.firstinspires.org/ftc/archive/2026/game/manual-16 (glossary PDF: OK)
- https://ftc-resources.firstinspires.org/ftc/archive/2026/game/tu-09 (Team Update 09 PDF: OK)
- https://andymark.com/products/am-3376a (HTTP 429, twice)
- https://andymark.com/products/am-3376a.json and https://www.andymark.com/products/am-3376a.js (404)
- Web searches for the ARTIFACT mass: no official mass found

## 2. What the code actually contains

**The user's belief that they "simulated live with aero" is not supported by the code.** A grep of both repositories for magnus, drag, aero, air resist and lift coef finds no aerodynamic model in FTC_Decode. The only hit in the older Decode repo is a comment on a lumped speed factor (see below). Neither repo contains a flight integrator, a lift or drag coefficient, or a spin model.

### 2.1 Final robot (FTC_Decode, `decode2026/`)

- **Aiming is a hand-tuned lookup table** (`constants/ShootingConstants.java`, static block). Each `addData(distance_in, hoodAngle, wheelSpeed, turretOffset)` row is interpolated by a `LUT` class. There are 14 rows, from 28 in to 158 in:
  - wheel speed **1140 at 28 in up to 2140 at 158 in**. The source writes the far entries as sums, e.g. `2070+30+40`. That looks like trims added by hand on top of earlier tuned values.
  - hood angle **31° at 28 in up to 55° at 158 in**. The top three rows are written `Math.toRadians(56-1)`, so the effective value is 55°, not 56°. The pitch servo is mapped linearly between `PITCH_I = 31°` and `PITCH_F = 57°` (`TorqueShooterConstants`). The code does not say whether this "pitch" is the ball launch angle or a hood mechanism angle.
  - turret offset −1° to −3°, plus separate blue and red offset tables. One comment reads "need to tune red offset but i lazy".
  - row comments: `// tof: 1.5` on the 158 in row, and `// 19 frames` and `// 18 frames` on the 58 in and 38 in rows. These look like video-frame time-of-flight counts. The frame rate is not given.
- **Wheel speed units are encoder ticks per second.** `TorqueShooter.update()` compares `wantedVelocity` with `shooterMotor.getVelocity()`, which the FTC SDK reports in ticks/s. `kOmega = 12 / 2800d` with the comment "back emf, volts ticks^-1 s^-1" means 12 V ↔ 2800 ticks/s. If the encoder has 28 ticks/rev on the motor shaft, which the older repo assumes (`/ 28.0`), that is 6000 rpm, consistent with a 6000 rpm-class motor. On the same assumption, the LUT maximum of 2140 ticks/s ≈ 4590 rpm at the motor shaft. **The gearing and the flywheel diameter of the final robot are unknown.** Neither appears in FTC_Decode.
- **Two shooter motors** (`shooterMotor`, `shooterMotor2`, the second one reversed) get the same power command. Feedback uses only the first encoder. The code does not show whether they drive one flywheel or two wheels.
- **Time of flight (TOF) is used only for shoot-on-the-move lead** (`util/decodeutil/SOTMUtil.java`). It builds a virtual goal, `goal − robotVelocity × tof`, and iterates 10 times. Two fits are defined:
  - `tofFunction = 0.0031·d + 0.46` (s, d in inches). **It is defined but not called anywhere in this snapshot.** It gives 0.95 s at 158 in and 0.55 s at 28 in.
  - `tofFunctionTele = 0.0000205515·d² − 0.00134458·d + 0.683101`. This is the one actually used in both SOTMUtil call sites. It gives 0.98 s at 158 in and 0.66 s at 28 in.
  - Either result is multiplied by `tofMultiplier`. The default is 0.8, with the comment "0.9 was good from far, prob need to retune tof function or quadratic". Autonomous routines overwrite it with 0.35, 0.7 or 0.94.
  - **Neither fit matches the "tof: 1.5" comment at 158 in.** Both give about 0.95–0.98 s. Either the comment is in other units (frames?) or the fits changed later. This cannot be resolved from the code.
- The lead's figure of "hood 31–56°" should read **31–55° effective** (written as 56−1). The other figures in the lead's summary check out.

### 2.2 Older code (Decode, `util/misc/`)

- **`SOTM.java`** is a drag-free minimum-speed projectile solver: `g = 386.2205` in/s², shooter height `zi = 12` in, goal height `zf = 48` in, `flywheelRadius = 1.5` in. It returns the turret angle, the pitch and `v / flywheelRadius`. There is no drag, lift or spin term. (It also looks buggy: TOF is computed as `dz / (v·cosθ)` instead of the horizontal distance, and `distEff` is computed from the uncorrected dx, dy. That is an observation; it was not tested.)
- **`SOTM2.java`** uses a 72 mm wheel (`radius = 0.036`), **ball radius `0.06223` m (2.45 in)** and `speedCoefficient = 0.7 // accounts for compression and stuff idk`. Its `calculateAngle` is a drag-free closed form with g = 9.81.
- **`SOTM3.java`** uses the same 72 mm wheel and `speedCoefficient = 0.5` with the comment "accounts for compression, rotation, air resistance, etc. not all rotation is converted into linear motion". The ball speed is taken as ticks/s × 2π/28 × r_wheel × 0.5. It has a pitch LUT and a wheel speed LUT (1290–2230 ticks/s over 38–148 in).
- The **only** mention of "air resistance" anywhere is that lumped constant 0.5. It is a fudge factor, not a model.

## 3. Numbers with labels

| Quantity | Value | Kind | File |
|---|---|---|---|
| LUT distance range | 28–158 in | tuned table | FTC_Decode ShootingConstants |
| LUT wheel speed | 1140–2140 ticks/s | tuned table | same |
| LUT hood or pitch | 31°–55° effective (servo map 31°–57°) | tuned table / servo limits | ShootingConstants, TorqueShooterConstants |
| Back-EMF constant | 12/2800 V per tick/s | stated constant | TorqueShooterConstants |
| Linear TOF fit (unused) | 0.0031·d + 0.46 s | empirical fit | ShootingConstants |
| Quadratic TOF fit (used) | 2.05515e-5·d² − 1.34458e-3·d + 0.683101 s | empirical fit | ShootingConstants |
| TOF multiplier | 0.8 default; 0.35/0.7/0.94 in autos | hand trim | ShootingConstants, opmode/comp/* |
| Gravity in old solver | 386.2205 in/s² | constant | Decode SOTM.java |
| Old wheel size | 1.5 in radius (SOTM); 72 mm diameter (SOTM2/3) | earlier design values; final robot unknown | Decode |
| Old speed coefficient | 0.7 (SOTM2), 0.5 (SOTM3) | lumped empirical | Decode |
| Spin rate, C_L, C_D | **none** | n/a | n/a |

**DECODE ARTIFACT (official):** "ARTIFACTS are 5 in. (12.70 cm) nominal Gopher ResisDent™ polypropylene balls in purple (am-3376a_purple) and green (am-3376a_green)". "ARTIFACTS are not perfectly spherical and may vary in size … specified to be 4.9 in +/- 0.25 in. (12.45 cm +/- 0.65 cm) in diameter at the mold seam" (Team Update 09, §9.9). The glossary also defines the ARTIFACT as a "5 in. (12.70 cm) nominal Gopher ResisDent™ polypropylene ball". **I found no official mass. Mass is unknown.** The older code's ball radius of 2.45 in equals half the 4.9 in seam diameter.

## 4. Grading

| Claim | Grade |
|---|---|
| The team aimed using tuned LUTs plus empirical TOF fits | observation (code read directly) |
| The team modelled aerodynamics or Magnus live | **not supported.** No such code exists in either repo. |
| The 0.5–0.7 speed coefficient captures "compression, rotation, air resistance" | team comment (anecdote), not measured |
| Any spin data | none present |

## 5. What this does and does not tell us

**Does tell us (observation-grade):**
- An FTC team shooting a large hollow plastic ball built its competition aiming **without any aero or Magnus model**. The code contains no scoring-accuracy data, so how well it worked is not known from this source. They tuned distance → (hood, wheel speed) by hand and lumped everything unmodelled (drag, spin lift, slip, compression) into the table and into fudge factors (speedCoefficient, tofMultiplier). This is evidence that teams **tune around** unmodelled drag and spin rather than model it. It is not evidence that drag and spin are negligible.
- The repeated retuning (sums like `2070+30+40`, TOF multipliers from 0.35 to 0.94, "prob need to retune") shows that an empirical map drifts. A physics model that keeps the right structure would help with interpolation and with shoot-on-the-move.
- A hood-angle range of about 31–55° plus a 1:2 spread in wheel speed was enough to cover 28–158 in for their goal. That says nothing about a high-backspin lob into a tilted CELL.

**Does not tell us:**
- No spin rate, spin direction, C_L, C_D or exit speed. It cannot calibrate or validate any part of the PM-001 flight model.
- It is a **different ball**: DECODE ARTIFACT, about 4.9–5 in (≈ 124–127 mm), polypropylene, mass unknown. POLLEN is 71 mm, about 25 g, polyethylene. Ball size, surface, hole pattern and mass per area all differ, so even qualitative drag and lift magnitudes do not carry over. The Reynolds number and spin parameter at the same wheel speed will differ.
- It is a **different target geometry**: an open goal at a fixed height, not an upward-facing CELL in a tilted HIVE seen from the unfavourable side. Their trajectories were tuned for direct entry, not for a Magnus-shaped or rim-redirected entry.
- The final wheel diameter, gearing and wheel layout (one wheel or two) are unknown. Their wheel speeds cannot be converted to surface speed.

## 6. Implications for the PM-001 model and test plan

1. **Do not cite this as an aero simulation precedent.** Cite it only as an observation that FTC shooters commonly work from empirical LUTs.
2. **Use the same LUT idea as the practical fallback and as a validation layer.** After the physics model predicts (hood or roller setting, wheel speed) for each robot position, build a measured LUT on the real robot and compare. Large, systematic residuals that grow with spin would be indirect evidence of Magnus effects that the model under- or over-predicts.
3. **Log what they did not log:** ball exit speed and spin (≥ 240 fps video), wheel speed before and after each shot, and time of flight from frame counts *with the frame rate recorded*. Their frame-count comments with no fps attached are the failure to avoid.
4. **A lumped "speed coefficient" is not acceptable for PM-001.** HANDOFF §5 forbids treating v_exit = u_wheel/2 as universal. Model the contact (slip, hood or roller friction) and measure the exit (v, ω) map instead of folding drag and spin into one number.
5. **Shoot-on-the-move TOF lead** (virtual goal = goal − v_robot·tof) is a reusable idea if the TOF comes from our drag-plus-Magnus integrator rather than from a hand fit. It is out of scope for the current static unfavourable-side shot.
