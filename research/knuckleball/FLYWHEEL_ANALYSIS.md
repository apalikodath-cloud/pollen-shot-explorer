# Flywheel analysis: 72 mm vs 98 mm wheels for a POLLEN knuckleball

Status: analysis note, 2026-11-05. Every number has a label:
- **[V]** vendor or manual figure (source in `FEASIBILITY_REPORT.md` §Sources);
- **[A]** assumption;
- **[D]** derived by hand from [V] and [A];
- **[P]** predicted by the repo contact model (`src/launcher.py`, not validated against a real launcher);
- **[M]** measured.

There are no [M] launcher numbers. No one has measured a POLLEN launch yet.

Scripts:
- `flywheel_analysis.py` prints the full table (`data/flywheel.json`).
- `flywheel_analysis.py --needed` prints the required launch speeds.

## 1. Inputs

| Quantity | Value | Label |
|---|---|---|
| POLLEN diameter, radius | 71.12 mm, 35.56 mm | [V] CAD of the AndyMark part, manual says "about 2.8 in" |
| POLLEN mass | 24.95 g (0.055 lb) | [V] AndyMark listing as recorded in the repo HANDOFF; the 2026 manual gives no mass |
| POLLEN moment of inertia | I = k_I m R², k_I = 0.63, giving 1.99e-5 kg m² | [D] from CAD shell (0.627 to 0.638) |
| NECTAR | about 3.6 in (91 mm); mass unknown | [V] manual; mass **not found** |
| Air | ρ = 1.204 kg/m³, μ = 1.81e-5 Pa s | [A] 20 °C, sea level |
| Motor | goBILDA 5203 1:1: 6000 rpm free, 0.144 N m stall, 9.2 A stall at 12 V | [V] |
| Motor (alt.) | REV HD Hex bare (REV-41-1291): 6000 rpm, 0.105 N m, 8.5 A | [V] |
| Wheel masses | Gecko 72 mm 52 g, Gecko 96 mm 105 g | [V] (no wheel inertia published) |
| Wheel inertia | 0.6 m R² (tread-heavy wheel) | [A] |
| Flywheels | goBILDA steel 60 mm 551 g cm², 82 mm 1651 g cm² | [V] (the 82 mm product has a conflicting 840 g cm² title) |
| Contact | μ_wheel 0.8, μ_hood 0.3, k_n 4000 to 40000 N/m, compression δ 4 to 12 mm | [A] **POLLEN stiffness and friction are not measured** |

The "98 mm" wheel is modelled with a 49 mm radius. The goBILDA 96 mm wheels are 1 mm smaller in radius; the difference is 2 % in surface speed.

## 2. Surface speed, ideal exit speed and Reynolds number

Surface speed: v_s = π D N / 60 [D].

Examples:
- 98 mm at 5000 rpm: v_s = π × 0.098 × 5000 / 60 = 25.66 m/s.
- 72 mm at 5000 rpm: v_s = π × 0.072 × 5000 / 60 = 18.85 m/s.

Ideal ball speed [D]:
- **single wheel + fixed hood:** v = v_s / 2. The ball rolls on the hood, so its centre moves at half the surface speed.
- **two opposing wheels:** v = (v_s1 + v_s2) / 2.

The "90 %" columns multiply these by 0.9. That factor is an **optimistic illustration only**, not a measured transfer efficiency.

Reynolds number: Re = ρ v D / μ = 1.204 × v × 0.07112 / 1.81e-5 = 4731 × v [D], with v in m/s.

| rpm | v_s 72 mm (m/s) | v_s 98 mm (m/s) | hood, 90 %: 72 / 98 (m/s) | dual equal, 90 %: 72 / 98 (m/s) | Re of hood 98 mm (90 %) |
|---|---|---|---|---|---|
| 3000 | 11.31 | 15.39 | 5.09 / 6.93 | 10.2 / 13.9 | 32 800 |
| 4000 | 15.08 | 20.53 | 6.79 / 9.24 | 13.6 / 18.5 | 43 700 |
| 5000 | 18.85 | 25.66 | 8.48 / 11.55 | 17.0 / 23.1 | 54 600 |
| 6000 | 22.62 | 30.79 | 10.18 / 13.86 | 20.4 / 27.7 | 65 600 |
| 7000 | 26.39 | 35.92 | 11.88 / 16.16 | 23.8 / 32.3 | 76 500 |
| 8000 | 30.16 | 41.05 | 13.57 / 18.47 | 27.1 / 36.9 | 87 400 |

### What speed does a scoring shot need?

The CELL opening is about 50.8 × 35.6 cm and the HIVE pivot is 111.65 cm above the tiles [V]. The robot launch height, the distance and the CELL height during play are [A].

The table below is a no-spin twin: drag only, with Cd 0.62 [P] from the CFD, and no lift.

| Horizontal distance | Rise to target | 45° | 55° | 65° |
|---|---|---|---|---|
| 1 m | 0.7 m | 5.9 m/s | 4.7 m/s | 4.5 m/s |
| 2 m | 1.0 m | 6.6 m/s | 6.0 m/s | 6.2 m/s |
| 3 m | 1.0 m | 7.2 m/s | 7.0 m/s | 7.5 m/s |
| 4 m | 1.0 m | 8.0 m/s | 8.0 m/s | 8.8 m/s |

- Flight times are 0.3 to 1.3 s [D].
- Scoring shots therefore need **v ≈ 4.5 to 9 m/s, i.e. Re ≈ 21 000 to 42 000** [D]. This is the range the CFD covers (Re 20 000, 33 057 and 47 224).
- **3000 to 8000 rpm is more than any of these shots needs.**
  - A 98 mm hood shooter needs about 2000 to 4000 rpm.
  - Two equal 98 mm wheels need about 1100 to 2100 rpm.
  - Higher speed is not better. It flattens the arc, which shrinks the effective CELL opening and raises the impact speed. As section 6 shows, it also gives the air no more time to deflect the ball.

## 3. Torque, gearing and recovery

**Gearing.** More motors on one wheel add torque, but they do **not** raise the free speed. Two 6000 rpm motors still top out at 6000 rpm at 12 V [D].
- In practice, about 85 % of free speed under load and battery sag is a reasonable ceiling [A]. That is about 5100 rpm direct.
  - A retailer page lists the sibling 5202 at 5400 rpm "tested" [V, unverified snippet].
- To reach 7000 to 8000 rpm, the wheel must be geared up, for example with a 1.5:1 belt overdrive. That divides wheel torque by 1.5 and multiplies the recovery time constant by 2.25 (τ = I ω_f / T₀) [D].
- The rules allow motors "with or without the provided gearbox, and/or with any other compatible gearbox" (R501), and up to 8 motors (R503) [V].

**Model results [P].** Single motor, wheel coasting except for motor torque during the contact, hood wrap 90°, k_n 4000 N/m, δ 4 mm. Recovery times are for 1 and 2 motors.

| Wheel + flywheel | rpm | Ball v (m/s) | rpm drop | Recovery, 1 motor | Recovery, 2 motors |
|---|---|---|---|---|---|
| 98 mm + 82 mm steel flywheel (I ≈ 4.2e-4 kg m²) | 3000 | 7.2 | 180 | 0.08 s | 0.04 s |
| same | 4000 | 8.9 | 251 | 0.16 s | 0.08 s |
| same | 6000 (overdrive) | 8.9 | 264 | 0.26 s | 0.13 s |
| 72 mm + 60 mm flywheel (I ≈ 1.0e-4 kg m²) | 4000 | 8.2 | 500 to 540 | 0.04 s | 0.02 s |

These are first-order results. They ignore the motor current limit and battery sag.

Per shot, the ball takes about 1.0 J of translational energy at 9 m/s, plus 0.7 J of spin energy for a hood shot at about 2500 rpm of spin [D]. The wheel's stored energy at 4000 rpm is ½ × 4.2e-4 × 419² = 37 J for the 98 mm set and 8.8 J for the 72 mm set [D].
- The 72 mm set loses a larger fraction of its speed per shot. That droop is the main shot-to-shot spin and speed scatter source when shots come quickly.

## 4. The contact model shows two regimes, and the spin depends on which one you are in

The repo model integrates Coulomb friction on both contacts, a linear normal stiffness and rolling hysteresis. Sweeping the **unmeasured** POLLEN contact stiffness k_n and compression δ shows two regimes [P]:

1. **Friction-limited (low k_n δ, short contact).** The ball leaves while both contacts are still sliding.
   - Exit speed is set by μ N t_contact, not by rpm. Example: k_n 4000 N/m, δ 4 mm gives 7.11 m/s for every rpm from 3000 to 8000 with two wheels, and 8.92 m/s with a hood from 4000 rpm up.
   - **With two wheels, spin is then 0 whatever the speed ratio**, because both sliding friction forces equal μN.
   - In this regime speed and spin depend on tread wear, ball surface and compression, which are uncontrolled from shot to shot. This is the regime a knuckle shooter must avoid, even though it happens to give zero spin.
2. **Grip (k_n δ ≳ 80 N per contact here).** The ball reaches rolling on the wheel(s) before it leaves.
   - Dual wheels: S = (R_b/r_c) × (1 − r)/(1 + r), where r = v_s2 / v_s1 and r_c is the compressed contact radius. Model values: r 0.8 gives S 0.127 to 0.135; r 0.9 gives S 0.060 to 0.064.
   - Hood: S = 1.06 at δ 4 mm, 1.13 at δ 8 mm, 1.20 at δ 12 mm. A hood shooter always throws a high-spin ball (S ≈ 1). **It cannot throw a knuckleball.**

Whether a real POLLEN launch is in regime 1 or 2 is **unknown until k_n, μ and δ are measured**. Section 9 lists the measurements needed.

## 5. Spin control for a low-spin launch with dual opposing wheels (grip regime) [P]

Model case: 98 mm wheels with 82 mm flywheels, 1600 rpm, about 7.4 m/s; the 72 mm case at 2200 rpm gives the same S.

| Change from a matched pair | S | Spin |
|---|---|---|
| speed ratio 0.995 | 0.003 | 0.6 rad/s |
| 0.99 | 0.006 | 1.2 rad/s |
| 0.98 | 0.012 | 2.4 rad/s |
| 0.95 | 0.030 | 6.0 rad/s |
| top-wheel friction 0.4 instead of 0.8 (grip still reached) | 0.000 | 0 |
| **top-wheel inertia halved** | **0.050 (98 mm) / 0.087 (72 mm)** | 10 to 17 rad/s |

Conclusions [D from P]:
- S is set by the wheel speeds **at the moment the ball leaves**, not by the set-points.
  - Unequal inertia or unequal motor torque makes the two wheels droop differently during the 5 to 15 ms contact. That gives spin even with perfectly matched set-points.
  - Equal wheels, flywheels and motors matter more than the velocity controller.
- To keep |S| < 0.005 the exit speeds must match within about 1 %. That bound comes from |S| ≈ |1 − r| / 2.
  - S < 0.005 means the ball turns less than about 40° (the spacing between holes) during a 0.7 s flight at 7 m/s: ω = 2 S v / D ≈ 1 rad/s.
  - |S| < 0.02 needs a match within about 4 %. But S = 0.02 already turns the ball through about 160° in that flight, so the hole pattern facing the flow changes during the flight.
- The spin axis is parallel to the wheel axles. Mount the axles vertically to throw a side-spin curve, or horizontally for back- or top-spin. Hole orientation at launch is not controlled by a wheel launcher, because the ball enters in a random orientation [A].
  - Section 6 explains why that matters less than expected.

**Repeatability is not claimed.** It needs the shot-to-shot measurements in section 9.

## 6. How much can the air move a POLLEN in an FTC flight? [D, P]

For a constant lateral coefficient C over a path of length L, the deflection is

y = C ρ A L² / (4 m),

where A = π R² = 3.973e-3 m². For POLLEN, ρA/(4m) = 1.204 × 3.973e-3 / (4 × 0.02495) = 0.0479 /m.

| Lateral coefficient | What produces it | y over 2 m | y over 3 m | y over 4 m |
|---|---|---|---|---|
| 0.01 | knuckle-scale wake force [P] | 1.9 mm | 4.3 mm | 7.7 mm |
| 0.05 | largest mean orientation force at S = 0 [P] | 9.6 mm | 22 mm | 38 mm |
| 0.15 | Magnus, S = 0.25 [P] | 29 mm | 65 mm | 115 mm |
| 0.36 | Magnus, S = 1 [P] (likely over-predicted, see the CFD validation) | 69 mm | 155 mm | 276 mm |

- **The deflection does not depend on launch speed for a given path length**, as long as C does not change with Re. Between Re 20 000 and 47 000 it changes little in the CFD [P]. Faster launches do not buy more break.
- A 4 cm shift is about 8 % of the 50.8 cm CELL width. That is negligible for scoring and hard to see by eye at 3 m.

## 7. Single vs dual wheels, and fixed vs adjustable hood

| Option | Spin | Knuckle possible? | Notes |
|---|---|---|---|
| One wheel + fixed hood (current scope) | S ≈ 1 to 1.2 backspin [P] | **no** | the HANDOFF scope; strong, steady Magnus lift; a high-spin "breaking" ball is the realistic use |
| One wheel + adjustable hood angle | S ≈ 1 still; changes launch angle, not spin | no | the hood angle sets the arc; spin is set by the rolling condition |
| One wheel + adjustable hood friction (low-μ hood insert) | S drops from about 1 towards 0.5 only if the ball slides on the hood [P, approximate] | no | slip is uncontrolled, so scatter goes up |
| Two equal powered wheels | S ≈ 0 when the ball grips, matched within 1 % at exit | **marginally**: see section 6, the effect is about 1 to 4 cm | needs equal inertia and torque; outside the HANDOFF single-wheel scope, analysed only because the task asked |
| Two wheels, unequal speeds | S = (1−r)/(1+r) × R_b/r_c | n/a | gives a tunable spin rate and axis; the best route to a predictable *curving* shot |

## 8. Stresses and legality

**Rim hoop stress** of a thin ring: σ = ρ v_s² [D].
- TPU or rubber tread, ρ ≈ 1200 kg/m³ [A]:
  - 98 mm at 8000 rpm: 1200 × 41.05² = 2.0 MPa;
  - 98 mm at 5000 rpm: 0.79 MPa;
  - 72 mm at 8000 rpm: 1.09 MPa.
- Soft 30A to 50A treads have tensile strengths of a few MPa [A]. At 8000 rpm a 98 mm soft tread is within a factor of about 2 of failure if it were a free ring. Bonding to the hub reduces this.
  - Expect visible radial growth of soft treads above about 6000 rpm. Measure the diameter at speed before trusting v_s.
- Steel flywheel, 82 mm at 8000 rpm: 7850 × 34.3² = 9.3 MPa, negligible for steel [D].

**Legality [V]:**
- R501: legal motors, with gearbox changes allowed.
- R503: at most 8 motors.
- R102 / R105: starting size 18 in cube, expanded limit 18 × 24 × 29 in tall.
- R801: no pneumatics or high-speed airflow.
- G417: affect the HIVE only by LAUNCHING into the upward-facing CELL.
- No launch speed cap was found in the rules that were read.
- Not read: the definition of "LAUNCH" in the last part of the manual.
- **Dual-wheel shooters, flywheels and overdrive belts are legal as far as the rules that were read show.**

## 9. Measurements needed before any number above becomes [M]

1. POLLEN mass (scale, 10 balls), diameter in 3 axes, and the hole count and pattern on the real part.
   - For NECTAR: mass, diameter, holes.
2. Diametral stiffness k_n and its loss with compression: a load-displacement test from 0 to 15 mm.
3. Tread–ball and hood–ball friction coefficients: an incline test.
4. Wheel diameter at speed: strobe or high-speed video at 3000 and 6000 rpm.
5. Exit speed and spin vs rpm: 240 fps video with a marker on the ball, 20 shots per setting.
   - Report the mean and sd of v and ω, and the spin axis.
6. Wheel rpm trace through a shot (encoder at ≥ 1 kHz): the droop and recovery.
7. Dual-wheel exit spin vs speed ratio 0.95 to 1.05: tests the predicted 1 % tolerance.
