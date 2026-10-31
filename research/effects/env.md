# Environment effects on the POLLEN shot (research lens "env")

Written 2026-10-30. Scope: air density (temperature, altitude, humidity, weather), indoor drafts and fans, the air that moves with the ball, and surfaces near the ball (robot body, flywheel air, floor, HIVE lips). Other lenses own the launcher, contact and aerodynamic-coefficient questions. Where an env effect crosses into them, this file says so and stops.

**Labels (HANDOFF §5):**
- **[CONFIRMED]** means the cited source says it. It is never a POLLEN measurement.
- **[user]** means the user supplied it.
- **[ASSUMED]** means our choice, with no source.
- **[derived]** means my own arithmetic from labelled inputs.
- **[PREDICTED]** means output of the repo model (viz/explorer/solver.js and physics.js) or of my planar RK4. My RK4 is physics.js `integrate` with wind and effective mass added; with both at zero it matches physics.js to 0 m.

None of these numbers is a measurement on POLLEN. Pickleball and other-ball values are not POLLEN facts.

---

## 0. Bottom line

1. **The required wheel rpm is nearly unchanged by venue air. The aim is not.** [PREDICTED] At the default pose, going from ρ 1.20 to Golden, CO (ρ ≈ 0.974) moves the tolerant minimum from 2830 to 2803 rpm (−1 %). It moves the needed launch angle by +0.30°, but the clean angle band at a fixed speed is only 0.21–0.30° wide.
   - A shot tuned at sea level therefore misses at 1–2 km unless it is re-aimed or the solver is given the venue ρ.
   - The no-spin twin needs a smaller re-aim: +0.20° for the knife-edge twin.
2. **Drafts are probably the largest environmental error.** [PREDICTED] A steady 0.1 m/s along-shot draft shifts the needed angle by 0.11–0.13° at the default pose: about half of the clean band. A 0.3 m/s draft shifts it by 0.31–0.43°, which empties the band. Venue evidence:
   - The strictest sports-hall spec (BWF) allows 0.2 m/s. [CONFIRMED]
   - A measured arena seating zone ran 0.06–0.36 m/s. [CONFIRMED]
   - FTC venues have no published limit that I found. [ASSUMED: not exhaustively searched]
3. **Vertical drafts matter about twice as much for the backspin shot as for its no-spin twin.** [PREDICTED] Robustness Monte Carlo samples horizontal wind only. It should also sample a vertical component.
4. **Smaller unmodelled effects.** [derived / PREDICTED] These are constant biases that empirical tuning absorbs, but a model-only aim would carry them:
   - effective mass (added mass plus the air held inside the shell), up to 0.28°;
   - near-wall lift from robot plates, 0.04–0.23°;
   - the flywheel's own air jet, 0.2–0.8 % of exit speed.
5. **The floor and HIVE lips are negligible.** [derived] The floor is 10 diameters away. The near-wall time at a lip changes position by less than 1 mm.

---

## 1. Default case used for every estimate

**Pose.** The robot-view defaults in page.html: x −1.0 m, y 0.2 m. That gives d 1.000 m from the HIVE pivot plane on the unfavourable side and bearing ψ 8.1°. Release h 0.737 m [user/default]. S 1.0 at release, v/u 0.42 [ASSUMED page default]. Nominal aero:

| Parameter | Value | Label |
|---|---|---|
| ρ | 1.20 | params_lit.json, grade D |
| m | 24.95 g | |
| R | 35.5 mm | |
| Cd | 0.5 | ASSUMED |
| Cl | min(0.35 S, 0.25) | ASSUMED |
| k | 0.03 /s | ASSUMED |

**Reference height.** z_ref = 1.432 m, the mid-height of the inside polygon of that section [derived from CAD sections in data/field]. "Δx" below is the shift of the ball centre where it crosses z_ref on the way down.

The solver gave these four shots [PREDICTED]. All are clean in still air.

| Shot | v (m/s) | θ (°) | wheel rpm (v/u 0.42) | Clean θ band at fixed v (0.01° scan) | Band width at z_ref | Time to z_ref |
|---|---|---|---|---|---|---|
| **A**, S 1, tolerant minimum | 6.10 | 73.86 | 2830 | 73.75–73.99 (0.24°) | 20.8 mm | 1.02 s |
| **B**, S 1, most forgiving | 10.1 | 81.3 | 4686 | 81.16–81.46 (0.30°) | 74.7 mm | 1.77 s |
| **A0**, no-spin twin, tolerant minimum | 6.06 | 74.83 | 2812 | 74.72–74.96 (0.24°) | 20.0 mm | 1.00 s |
| **B0**, no-spin twin, most forgiving | 7.0 | 78.9 | 3248 | 78.80–79.23 (0.43°) | 52.5 mm | 1.21 s |

Sensitivity to exit speed [PREDICTED]: +0.05 m/s moves the ball +22.8 mm (A), +4.9 mm (B), +24.6 mm (A0) and +19.4 mm (B0) at z_ref.

Each effect below is given as Δx at z_ref and as the shift of the centre of the clean θ band, at fixed v.

---

## 2. Air density: temperature, altitude, humidity, weather

**What it is.** Drag and Magnus accelerations are both ∝ ρ/m. In the model, ρ enters only through q = ρA/(2m) = 0.0952 /m at ρ 1.20 [derived]. Nathan: "they both are proportional to the density of the air" [CONFIRMED, baseball.physics.illinois.edu/Denver.html]. A venue with ρ 18 % lower is therefore aerodynamically the same as a ball 22 % heavier, with gravity unchanged.

**Formulas used** [derived]:
- Pressure, ISA / US Standard Atmosphere 1976: p = 101325 (1 − 2.25577e-5 h)^5.25588 Pa (NASA-TM-X-74335, https://ntrs.nasa.gov/citations/19770009539).
- Moist-air density: ρ = (p − 0.378 e)/(R_d T), with R_d 287.06 J/(kg K), e = RH·e_s(T) and e_s = 611.2 exp(17.62 t/(243.12 + t)) Pa (Magnus form). This is a simplification of CIPM-2007 (Picard et al. 2008, Metrologia 45:149, doi:10.1088/0026-1394/45/2/004), well inside 0.5 %.
- Viscosity, Sutherland: μ = 1.716e-5 (T/273.15)^1.5 (383.55)/(T + 110.4).

| Venue air | p (kPa) | ρ (kg/m³) | vs 1.204 | ν (m²/s) | Re at 8 m/s |
|---|---|---|---|---|---|
| 20 °C dry, sea level (scope standard) | 101.33 | 1.204 | 0 | 1.51e-5 | 37 700 |
| 15 °C dry, sea level (ISA) | 101.33 | 1.225 | +1.7 % | 1.46e-5 | 38 900 |
| 30 °C dry | 101.33 | 1.164 | −3.3 % | 1.60e-5 | 35 500 |
| 30 °C, 100 % RH | 101.33 | 1.146 | −4.8 % | 1.62e-5 | 35 000 |
| 1000 m, 20 °C, 40 % RH | 89.87 | 1.064 | −11.6 % | 1.71e-5 | 33 300 |
| Denver 1609 m, 20 °C, 30 % RH | 83.43 | 0.988 | −17.9 % | 1.84e-5 | 31 000 |
| **Golden, CO 1730 m, 20 °C, 30 % RH** | 82.20 | 0.974 | −19.1 % | 1.86e-5 | 30 500 |
| 2000 m, 20 °C, 30 % RH | 79.50 | 0.942 | −21.8 % | 1.93e-5 | 29 500 |

All rows are [derived].

Checks on the table:
- Denver at 82 % of sea-level density matches Nathan's "about 82% of that at sea level" [CONFIRMED].
- The 2026–27 Colorado FTC Championship is at the Colorado School of Mines, Golden, CO, on 13 Feb 2027 [CONFIRMED, https://ftc-events.firstinspires.org/2026/USCOCMP]. Golden's elevation is 1730 m [CONFIRMED, Britannica]. So 1–2 km FTC events are real.
- Day-to-day weather moves station pressure by about ±1–3 kPa, i.e. ±1–3 % in ρ [ASSUMED typical synoptic range].

**Effect on this shot** [PREDICTED]. The base case uses ρ 1.20. Each cell is Δx at z_ref / θ-band centre shift; "→ hit" or "→ miss" is the outcome if the un-re-aimed shot is fired.

| ρ | A | B | A0 | B0 |
|---|---|---|---|---|
| 1.225 (15 °C) | −6 mm / −0.06° | −21 / −0.09° | −4 / −0.05° | −5 / −0.04° |
| 1.164 (30 °C dry) | +9 / +0.10° | +31 / +0.12° | +6 / +0.07° | +7 / +0.06° |
| 1.145 (30 °C, 100 % RH) | +13 / +0.17° → hit | +47 / +0.19° → hit | +9 / +0.10° | +11 / +0.09° |
| 1.068 (≈1 km) | +32 / +0.38° → hit | +116 / +0.45° → miss | +21 / +0.25° → hit | +25 / +0.21° → hit |
| 1.005 (≈1.5 km) | +48 / +0.55° → hit | +175 / +0.67° → miss | +31 / +0.37° → hit | +38 / +0.30° → hit |
| 0.945 (≈2 km) | +63 / +0.71° → hit | +232 / +0.89° → miss | +41 / +0.49° → hit | +50 / +0.40° → hit |

Re-running the full live solver at this pose with only ρ changed [PREDICTED]:

| ρ | Tolerant min rpm | θ there | Knife-edge min rpm | Clean cells |
|---|---|---|---|---|
| 1.20 | 2830 | 73.86° | 2695 | 283 |
| 1.164 | 2830 | 73.96° | 2699 | 283 |
| 1.064 | 2812 | 74.02° | 2685 | 279 |
| **0.974 (Golden)** | 2803 | 74.16° | 2677 | 279 |
| 0.913 | 2793 | 74.21° | 2670 | 280 |

The no-spin twin's knife-edge minimum goes from 2690 to 2674 rpm, and its clean-cell count from 324 to 314 (at 0.974).

In short, altitude barely changes how fast to spin the wheel. It does change where to aim, by more than the clean band is wide.

Two further points on density:
- **Spin decay.** Spin decay in air is ∝ ρ, through the β model in params_lit.json. Scaling the nominal k = 0.03 /s by ρ made no visible difference to the solver output [PREDICTED, pose x −1.0, y 0]. The decay is too small at the nominal k for this to matter. It would matter at k_high = 0.15.
- **Indirect Re effect, not modelled.** Re at 8 m/s falls from about 38k to about 30k at Golden [derived]. Table-tennis-ball data put the Cl "valley" between Re 3e4 and 5e4, and it moves with Re there: 0.21 at 3e4 versus 0.09–0.12 at 5e4 (Sakai 2016 / Miyazaki 2017, grade C, LITERATURE_SYNTHESIS.md). If POLLEN behaves like that, which is unknown, the Cl change at altitude could be as large as the ρ change itself, in either direction. The model's Cd and Cl have no Re dependence.

**In the model now?**
- The Python solvers take ρ as a parameter. params_lit.json fixes it at 1.20 (low 1.0, high 1.25, grade D), and robustness.py never varies it.
- The JS solver uses the exported case ρ 1.20, with no user input.
- Humidity and temperature are absent. The ρ effect on spin decay is present only in the β form. The Re effect is absent.

**How to add.** Add a venue panel (T, RH, p or elevation) that computes ρ with the formulas above and passes it as `params.rho`. Nothing else in physics.js or solver.js changes, because both use p.rho. Optionally scale k by ρ/1.2. In robustness.py, add ρ as a per-event (not per-shot) parameter and report windows per venue class: sea level, 1 km, 2 km.

**How to measure on real POLLEN.**
- Log venue temperature, RH and station (absolute, not sea-level-corrected) pressure at robot height with any barometric logger or a phone barometer. Compute ρ to about ±0.5 % [derived from ±1 hPa, ±0.5 °C, ±5 % RH, ASSUMED sensor class].
- Check that the ρ correction works: fire one fixed setting n ≥ 10 times at home and again at the venue, film side-on, and compare the mean descent-height crossing with the solver re-run at each ρ.

---

## 3. Indoor drafts, HVAC and fans

**What it is.** The model uses v_rel = v − u_wind in drag, Magnus and S (HANDOFF §4A). A steady draft u along the shot pushes the ball by roughly ½ q Cd |v| u t² for short flights [derived, small-u linearisation]. The push grows with flight time squared, so longer and slower lobs drift more.

**Typical air speeds:**

| Setting | Air speed | Label |
|---|---|---|
| BWF international badminton spec (strictest sports-hall rule found) | "air flow should not exceed 0.2 m/s over the Field of Play" | CONFIRMED |
| Malmö 13 000-seat arena, measured in the lower seating zone | "The corresponding air-speed level was 0.06-0.36 m/s." | CONFIRMED |
| Jet-ventilated arena, CFD | 0.9–1.5 m/s near upper seats | CONFIRMED (simulation, not measurement) |
| ASHRAE 55 still-air or draft limit | 0.2 m/s | CONFIRMED (via 55-2013 addendum b) |
| ASHRAE 55 cap on elevated air speed with occupant control | 0.8 m/s | CONFIRMED (via 55-2013 addendum d) |
| Ceiling and HVLS fans | Designed to give occupied-zone air speeds above the 0.2 m/s still-air level; scale with fan diameter and airflow | CONFIRMED (qualitative) |
| Pit or stand pedestal fans aimed across a field | 1–5 m/s within a few metres | ASSUMED; no source found |

Sources for the table:
- **BWF:** *Specifications for International Standard Facilities* V1.1, 14 Oct 2019, §6.3–6.4. The same section says airflow is to be checked with a hot-wire anemometer at 3, 6 and 9 m, at ≥ 8 points per court. https://www.badmintonpanam.org/wp-content/uploads/2023/01/3.3.4-Specs-for-Int_l-Standard-Facilities-14-October-2019-V1.1.pdf
- **Malmö arena:** Lestinen et al. 2016, Int. J. Ventilation 15(2):151, doi:10.1080/14733315.2016.1203622.
- **Jet-ventilated arena:** Stathopoulou et al., AIVC 2005, https://www.aivc.org/sites/default/files/members_area/medias/pdf/Conf/2005/2005053_Stathopoulou.pdf
- **ASHRAE 55:** 55-2013 addendum b and addendum d, ashrae.org.
- **Fans:** Raftery et al. 2019, Building and Environment, doi:10.1016/j.buildenv.2019.03.040; data at doi:10.17632/yk4jksgjdc.1.

A badminton shuttle has m/A ≈ 1.5 kg/m²; POLLEN has 6.3 kg/m² [derived]. POLLEN is about 4× less sensitive per unit air speed, but its clean window is only millimetres wide.

**Effect on this shot** [PREDICTED]. Steady draft, constant over the flight. "Tail" means along the shot, toward the HIVE. Cells are Δx at z_ref / θ-band centre shift.

| Draft | A | B | A0 | B0 |
|---|---|---|---|---|
| tail 0.1 m/s | +10 mm / +0.11° → hit | +34 / +0.13° | +10 / +0.12° → hit | +14 / +0.12° → hit |
| tail 0.3 | +27 / +0.31° | +99 / +0.39° | +28 / +0.33° | +40 / +0.33° |
| head 0.3 | −30 / −0.35° | −104 / −0.43° | −31 / −0.37° | −43 / −0.35° |
| tail / head 0.5 | +44 / −52 | +162 / −176 | +46 / −52 | +65 / −73 |
| tail / head 1.0 | +81 / −113 (≈ ±1.1–1.3°) | +314 / −369 (+1.23 / −1.53°) | +85 / −112 | +124 / −155 |
| tail / head 2.0 | +139 / −260 (+1.5 / −3.1°) | +604 / −806 (+2.4 / −3.5°) | +153 / −251 | +234 / −344 |
| updraft 0.1 | +12 / +0.14° | +34 / +0.13° | +6 / +0.08° | +6 / +0.06° |
| updraft / downdraft 0.3 | +36 / −37 (±0.43°) | +103 / −101 (±0.42°) | +18 / −19 (±0.23°) | +19 / −20 (±0.16°) |
| downdraft 1.0 | −128 / −1.57° | −331 / −1.40° | −65 / −0.86° | −68 / −0.59° |

Crosswind, as lateral drift at z_ref [PREDICTED, 3D RK4 with the spin axis horizontal; Magnus gets no lateral term from a crosswind]:

| Crosswind | A | B | A0 | B0 |
|---|---|---|---|---|
| 0.1 m/s | 8 mm | 32 mm | 8 mm | 12 mm |
| 0.3 m/s | 24 mm | 95 mm | 23 mm | 36 mm |
| 1.0 m/s | 82 mm | 321 mm | 79 mm | 123 mm |

The CELL's lateral acceptance is |y| < 218 mm for the ball centre [derived, 254 − 35.5 mm]. robustness.py uses W_LAT 0.15 m primary [ASSUMED]. Crosswind is therefore less critical than along-shot wind, because the knife edge is in θ.

How to read these results:
- **0.1 m/s is enough to matter.** A steady 0.1 m/s along-shot draft is about half of A's 0.24° band. It turned A, A0 and B0 into floor hits when fired un-re-aimed, because those shots sat near one edge of the band.
- **A vertical draft hits the backspin shot about twice as hard as its twin** (A vs A0, B vs B0). A vertical u rotates v_rel, so the Magnus vector, which is ⟂ v_rel, gains a horizontal component.
- **Shift relative to band width**, for 0.3 m/s tail: A 1.3, B 1.3, A0 1.4, B0 0.75 [derived from the tables]. At this pose, the most forgiving no-spin shot (B0) is the least draft-sensitive relative to its own window. B's long 1.77 s flight costs it most of the advantage of its wider band. This is one pose and one aero set, and it is not a claim that less spin is better in general.

**In the model now?**
- flight.py `simulate` accepts constant or callable wind. robustness.py samples constant horizontal wind with σ 0.30 m/s per component per shot (`PHYS["wind_sig"]`, ASSUMED). That σ is consistent with the 0.06–0.36 m/s arena data and above the 0.2 m/s BWF cap.
- Missing: vertical wind, spatial structure (a jet that the ball crosses for only part of its path), and wind in the live JS solver and feasibility maps, which are still-air only.

**How to add:**
- In physics.js `acc()` and solver.js `fastShot`, replace (vx, vz) by (vx − u_h, vz − u_z) inside the drag and Magnus terms (3 lines each). Pass u_h = u·(cos of the angle between the wind and the bearing) and u_z. Default 0.
- In robustness.py, add a vertical σ, e.g. 0.1–0.2 m/s [ASSUMED]. Optionally add a jet model u(x, z) = u_0 exp(−((z − z_j)/b)²) for a fan at height z_j with half-width b [ASSUMED form].
- Flights last ≤ 2 s. A constant-per-shot draft is adequate unless gusts change faster than about 1 s [ASSUMED].

**How to measure on real POLLEN:**
1. Follow the BWF method, adapted: use a hot-wire or ultrasonic anemometer, not a vane, because vane meters are unreliable below about 0.3–0.5 m/s [ASSUMED]. Measure at 0.7, 1.5, 2.5 and 3.5 m along the planned shot line (the apex of shot B reaches about 4.5 m), at ≥ 8 points. Record HVAC on and off and doors open and shut, at 1 Hz for 5 min, and report the mean and SD per component.
2. A cheap proxy: time soap bubbles or a smoke pen across 1 m.
3. Ball test that separates wind from ρ: fire one setting n ≥ 10 times in direction +x, then rotate the robot 180° and fire n ≥ 10 times toward a mirrored target. Half the difference in mean landing is the along-shot draft effect. The mean of the two is the ρ and bias effect.
4. At the event, re-aim using the practice-field drift, and note that the field's air may differ from the practice field's.

---

## 4. The air that moves with the ball (effective mass)

**What it is.** An accelerating sphere drags an added mass C_a ρ V with it, with C_a = 0.5 for a sphere in potential flow [CONFIRMED as the standard value; e.g. the Maxey–Riley extension to high Re, arXiv:2006.16577].

POLLEN is also a perforated shell: the 187 cm³ of air inside (about 0.225 g) is partly carried along. Buoyancy on the full volume cancels the weight of that internal air, but its inertia remains.

The net effect is a_gravity+aero = F/(m + m_added + φ m_int), so effective g and the aero accelerations fall by ε = (0.5 ρV + φ ρV)/m:
- ε = 0.45 % with no internal air carried (φ = 0);
- ε = 1.35 % with all of it carried (φ = 1).

[derived: V = 4/3 π R³; m 24.95 g; φ unknown, ASSUMED 0–1.] The Basset history force is negligible at Re about 1e4 or more [CONFIRMED qualitatively in the same source].

**Effect** [PREDICTED]. Cells are Δx at z_ref / θ-band centre shift.

| ε | A | B | A0 | B0 |
|---|---|---|---|---|
| 0.45 % | +7.5 / +0.09° | +6.8 / +0.03° | +7.5 / +0.10° | +7.2 / +0.06° |
| 1.35 % | +23 / +0.27° → hit | +21 / +0.08° | +23 / +0.28° → hit | +22 / +0.18° → hit |

This is a fixed bias, the same at every venue. It is absorbed by empirical tuning or by a video fit of Cd and Cl with g fixed, but a pure-model aim carries it.

**In the model now?** No.

**How to add.** Divide every acceleration (gravity, drag and Magnus) by (1 + ε). Use ε 0.0045 nominal with a 0.0135 bound. This is one constant in `acc()`.

**How to measure.** It is not cheaply separable from Cd and Cl. In the video fits (COMPLETENESS T1), fit g_eff as a free parameter on a taped-hole ball and on an open ball. The difference bounds φ. Alternatively, accept it as part of the calibration offset and label it so.

---

## 5. Surfaces near the ball: robot body, flywheel air, floor, HIVE lips

**What it is.** A sphere within a fraction of a diameter of a wall feels extra lift and drag. Willetts & Murray 1981 (JFM 105:487, doi:10.1017/S0022112081003303, Re 3000–50 000) found: "wall effects were found to dominate all dependencies other than that on Reynolds number" for gaps below 0.25 D, with persistent lift for gaps below 0.02 D and between 0.1 and 0.2 D [CONFIRMED, abstract]. The abstract gives no Cl values. For a cylinder at G/D 0.25 the repulsive Cl is about 0.75 (Fluids 6(6):211, https://www2.mdpi.com/2311-5521/6/6/211) [CONFIRMED; cylinder, not sphere].

For the sphere I use ΔCl 0.1–0.3 [ASSUMED].

**Estimate for a robot plate after the hood.** For a near-wall run of length L, the transverse impulse per unit mass is q ΔCl v² (L/v), so

Δθ ≈ q ΔCl L, independent of v [derived].

With L = 1–2 D (0.07–0.14 m), Δθ = 0.04–0.23°. The corresponding drag change is Δv/v ≈ q ΔCd L ≤ 0.4 % [derived, ΔCd ≤ 0.3 ASSUMED]. The upper end is as large as the whole clean band, but it is fixed for a given robot.

**The flywheel's air jet.**
- Rim speed is π·0.098·rpm/60 = 14.5 m/s at 2830 rpm and 24.0 m/s at 4686 rpm [derived].
- The wheel pumps air out of the exit gap. If the ball leaves inside a co-moving jet of u_j 2–5 m/s [ASSUMED] for 0.1 m, drag over that stretch falls, and v rises by about 0.2–0.8 % [derived: Δv/v ≈ q Cd L (2u_j/v)].
- That is up to about 0.05 m/s, worth up to about +23 mm at shot A [PREDICTED via the speed sensitivity in §1].

**The floor.** Release is 0.737 m = 10.4 D above the tiles [derived]. That is far outside the 0.25 D wall zone, so the floor has no effect.

**HIVE lips.** The tightest clean pass is about 10 mm = 0.14 D (shot A's margin) [PREDICTED]. That is inside the Willetts band, but only for about 0.05 m of path. Δθ ≈ 0.0952·0.3·0.05 ≈ 0.08° acting about 0.1 m before entry moves the ball about 0.1 mm [derived]. Negligible.

**In the model now?** No. Free flight starts at the release point with (v, θ, S), and contact.py handles only touching contacts.

**How to add.** Do not model it. Define the release state as the state measured at ≥ 2 D (0.15 m) from every robot surface, and fit the launcher map to that. If a model is wanted anyway, add a fixed Δθ_body and Δv_jet to the launcher output.

**How to measure:**
- Film the first 0.4 m of flight at ≥ 240 fps, side-on with a scale grid. Compare angle and speed fitted over 0–0.05 m against 0.15–0.35 m from the exit. Anything beyond gravity plus drag is the body and jet effect.
- With the wheel at speed and no ball, put an anemometer at the exit at 0, 5 and 10 cm to measure u_j.
- Repeat with a temporary cover over any plate within 0.25 D of the path.

---

## 6. Temperature and the ball itself (cross-lens: launcher and contact)

Polyethylene stiffness depends strongly on temperature. Pickleball Science, July 2024, tested a Franklin X-40 (a pickleball, not POLLEN) at −1, 23 and 49 °C. Stiffness at 49 °C was "roughly one-half of its stiffness at room temperature", and about one third of the −1 °C value [CONFIRMED, https://pickleballscience.org/?p=5412].

Over 23–49 °C that is about −2.6 %/°C [derived, log-linear]. If POLLEN's PE behaves similarly [ASSUMED], an 18–28 °C spread between gyms and pits is roughly ±13 % stiffness. That changes compression force at the 4 mm squeeze, hence grip v/u, spin transfer and rim restitution.

This belongs to the launcher and contact lenses. The env action is to store balls at venue temperature and to log ball temperature next to every calibration. Air humidity may also change wheel and hood friction [ASSUMED; no source found].

---

## 7. Coverage summary

| Effect | Size at the default case (worst of A, B, A0, B0) | In the model now | Priority |
|---|---|---|---|
| Steady along-shot draft 0.1 / 0.3 m/s | 0.13° / 0.43°; 34 / 104 mm | robustness.py only (horizontal σ 0.30); not in the JS solver or maps | **High** |
| Vertical draft 0.3 m/s | 0.43° (backspin), 0.23° (twin) | No | **High** |
| Altitude 1 / 2 km | 0.45° / 0.89°; 116 / 232 mm; required rpm −1 % | ρ fixed at 1.20 | **High at mountain events**; re-aim |
| Temperature 15–30 °C, humidity | ≤ 0.19°; ≤ 47 mm | No | Medium; log it |
| Re change with ρ (via Cl(Re)) | Unknown; possibly as large as the ρ effect | No | Medium; measure |
| Crosswind 0.3 m/s | 24–95 mm lateral, within a ±218 mm acceptance | robustness.py | Low–medium |
| Effective mass (added + internal air) | 0.03–0.28°; up to 23 mm | No | Medium for model-only aim; absorbed by tuning |
| Robot plate near-wall lift, flywheel jet | 0.04–0.23°; ≤ 0.8 % v | No | Medium; define release at ≥ 2 D |
| Floor, HIVE-lip near-wall forces, buoyancy | < 1 mm | No | Ignore |
| Weather pressure ±1–3 % | ≤ 0.1° | No | Low; included if ρ is logged |

All sizes are [PREDICTED] or [derived] from §§2–5.

## 8. Reproducing these numbers

The scratch scripts are not in the repo; per the task, only this file is committed.

**Density sweep.** Call `PollenSolver.solve({x:-1.0, y:0.2, h:0.737, S:1.0, vu:0.42, params, meta})` with `params` the `Sp1.0_nominal` case from viz/explorer/data/field/index.json and only `rho` changed.

**Draft and effective-mass rows.** Use a copy of physics.js `integrate` in which `acc()` uses (vx − u_h, vz − u_z) in the drag and Magnus terms and multiplies both components by 1/(1 + ε). Then:
- X is scaled by cos ψ, as in integrateOblique;
- classification uses physics.js `classify` on the `unfav_s0.0262~unfav_s0.0529` interpolated section from `solver._context`;
- the clean band is a θ scan at 0.01° steps with v fixed;
- Δx is taken at the descending crossing of z = 1.432 m.

**Crosswind.** A 3D RK4 with the same q, Cd and Cl, the spin axis along y, and wind along y; ψ is ignored.
