# Pedersen (2026), "Flywheel Shot Analysis: Correction and Extension"

source_id: `pedersen2026` · Task PM-001 · Deep read on 2026-10-30

## Citation

Pedersen, R. (FRC Team 449, The Blair Robot Project), *Flywheel Shot Analysis: Correction and Extension*. A 12-page LaTeX whitepaper dated May 2026 (PDF creation date 2026-05-06), announced on Chief Delphi in the thread "Flywheel Shot Analysis: Correction and Extension" (topic 520270, opened 2026-05-06T20:23Z, 6 posts).

- Thread: https://www.chiefdelphi.com/t/flywheel-shot-analysis-correction-and-extension/520270 (raw JSON: `/t/520270.json`)
- Whitepaper: https://robot.mbhs.edu/r/2026wp_flywheel_pdf, which redirects to `/media/whitepapers/2026/flywheel-calculations-latest.pdf`
- Companion calculator: https://robot.mbhs.edu/r/2026wp_flywheel_calc, which redirects to the Google Sheet `1LD30xVodJzua0Uc1uFVSXg-W978eXS2AsCauSe3inzQ`. It has 4 tabs: Single Flywheel, Double Flywheel, Compound Flywheel and Recalc Comparison.
- Predecessor: Brettle, D. (FRC 199), *Flywheel Shooter Analysis* (July 2023), https://docs.carlmontrobotics.org/jupyter_notebooks/files/FlywheelShooter.html. Discussed in CD thread 439111.

## Access level

**Full text.** I read every post in the thread from the Discourse JSON. I downloaded the whitepaper PDF, extracted its text with `pdftotext`, and checked the equation boxes against page renders. I exported the spreadsheet to xlsx and read all formulas and default values. I also viewed both images posted in the replies.

## Review status

**Unreviewed.** This is a forum post plus a self-published whitepaper. The author says Dean Brettle reviewed it informally, which is not peer review. The derivation is analytic and contains **no experimental data**. The only measurement anywhere in the thread is an unattributed student plot posted in reply #6 (described below). Its setup is undocumented.

## What it corrects, and what it does not

- **It corrects FRC 846's 2012 "Shooter Calculations Document" and the calculators derived from it (ReCalc, juliacalc).** Those calculators treat the shot as a closed flywheel–ball system that conserves angular momentum, with an inelastic sharing of momentum (and, in ReCalc, 100% energy transfer). That is wrong because the **hood applies an external impulse** to the ball. Pedersen also says the old conservation statement was "incorrectly set up."
- **It does not correct Brettle.** Brettle found the error first. Pedersen's single-flywheel result is stated to reduce exactly to Brettle's when the ball's initial velocity is zero. I checked this algebraically: with I_w = k_w m_w r_w², Pedersen's ω_wi/ω_wf = 1 + r_w² m_b (1+k)/(4 I_w), which equals Brettle's 1 + (1+k_p) m_p/(4 k_w m_w). Brettle's efficiency (2 + (1+k_p)m_p/(4k_w m_w))⁻¹ also matches Pedersen's total efficiency. My numbers agree to 3 significant figures (table P-1).
- **What it adds** to Brettle's framework. All four items are things Brettle listed as future work:
  1. The ball's initial linear velocity V_bi and spin ω_bi (feeder effects).
  2. A **double-flywheel or hood-roller** model in which the two wheels are **mechanically geared** at a fixed speed ratio G.
  3. A **compound** model: a fixed-hood section followed by a geared hood-roller section, solved sequentially.
  4. A maximum-efficiency table, and a comparison against ReCalc.
- **What it does NOT model.** The task brief expected these, but they are absent: slip, compression, hood friction coefficient, contact time, hysteresis, and motor torque during the shot. The paper assumes **no slip at exit**, **negligible compression** and **rigid bodies**. Its conclusion says these assumptions are unvalidated and "may have a significant impact." In reply #6 the author says slip and compression are likely the most important omissions, and that modelling them needs a time-domain friction analysis that he has not done. Ball inertia is included, through I_b as a free parameter.

## Method

The model is a rigid-body impulse–momentum analysis. Only the **end state** is constrained: no slip at either contact when the ball exits. No time history is modelled. The unknowns are the exit speed V_bf, exit spin ω_bf, final wheel speeds, and the two contact impulses H_w (wheel) and H_h (hood or roller). The equations are:

- linear impulse on the ball,
- angular impulse on the ball about its own centre,
- angular impulse on the flywheel system,
- for the fixed hood, the ball's angular momentum about the flywheel axle, with the hood contact at lever arm r_w + 2r_b (a hood concentric with the wheel),
- the two no-slip kinematic conditions.

The final momentum balance H_w + H_h = m_b ΔV_b serves as the consistency check.

## Symbols and units (SI)

| Symbol | Meaning | Unit |
|---|---|---|
| r_b, m_b, I_b | Ball radius, mass, moment of inertia about the centre. I_b = k m_b r_b², with k = 2/5 for a solid sphere, 2/3 for a thin shell, 1 for a "hollow cylinder" (worst case) | m, kg, kg·m² |
| r_w, r_w1, r_w2 | Flywheel radius; main wheel and hood-roller radii | m |
| I_w | Total "virtual" MOI of the flywheel system, referred to the main wheel axis. Includes geared inertia wheels: I_w = I_s + n² I_f for an n:1 speed-up. For the double model it includes the roller: I_w = I_w1 + G² I_w2 (spreadsheet) | kg·m² |
| ω_wi, ω_wf (ω_w1i, ω_w1f, ω_w2f) | Initial and final wheel angular speeds | rad/s |
| G | Fixed speed ratio of roller to main wheel, ω_w2 = G ω_w1 (geared, counter-rotating so that both contact surfaces drive the ball forward) | – |
| V_bi, V_bf | Ball linear speed before and after, perpendicular to the radius to the wheel centre | m/s |
| ω_bi, ω_bf | Ball spin before and after. Positive means **backspin** (CW in the figures; the wheel is CCW-positive) | rad/s |
| H_w, H_h | Total linear impulse from the wheel and from the hood or roller, positive in the shot direction | N·s |
| V_w | Wheel surface speed, r_w ω_w | m/s |

## Equations

### Double flywheel / geared hood roller (§2.3)

No slip at exit (assumption 1):

- ω_w1 r_w1 = V_b + r_b ω_b
- ω_w2 r_w2 = V_b − r_b ω_b

These give:

- (1) V_b = ω_w1 (r_w1 + G r_w2)/2
- (2) r_b ω_b = ω_w1 (r_w1 − G r_w2)/2

Impulse balances:

- (3) m_b (V_bf − V_bi) = H_w + H_h
- (4) I_b (ω_bf − ω_bi)/r_b = H_w − H_h
- (5) I_w ω_w1f − I_w ω_w1i = −H_w r_w1 − G H_h r_w2

The roller's torque is reflected through the gear ratio −G.

**Result (red box, p.5):**

ω_w1f = [4 I_w ω_w1i + 2(r_w1 − G r_w2)(I_b/r_b) ω_bi + 2(r_w1 + G r_w2) m_b V_bi] / [4 I_w + (r_w1 − G r_w2)² I_b/r_b² + (r_w1 + G r_w2)² m_b]

V_bf = (r_w1 + G r_w2) ω_w1f / 2  ·  ω_bf = (r_w1 − G r_w2) ω_w1f /(2 r_b)  ·  ω_w2f = G ω_w1f

Exit spin parameter (this follows directly from the boxed result): **S = r_b ω_bf / V_bf = (r_w1 − G r_w2)/(r_w1 + G r_w2)**. This is ≤ 1 for any G ≥ 0, and becomes topspin when G r_w2 > r_w1.

Setting G = 0 recovers the single-flywheel hooded formula below.

### Single flywheel + fixed hood (Appendix A)

Ball angular momentum about the flywheel centre: L_b,w = m_b V_b (r_w + r_b) − I_b ω_b.

- (6) ΔL_b,w = H_w r_w + H_h (r_w + 2 r_b)
- No slip at exit: V_w = V_b + ω_b r_b at the wheel, and 0 = V_b − ω_b r_b at the hood. This gives (7) V_b = ω_b r_b and (8) V_w = 2V_b.
- (9) ω_bf = ω_bi + r_b (H_w − H_h)/I_b
- (10) ω_wf = ω_wi − r_w H_w / I_w

The paper notes that the hood impulse H_h points **forward**, in the shot direction. The hood pushes the ball forward to stop its spin "slipping out."

**Result (red box, p.10):**

- ω_wf = [4 I_w r_b² ω_wi + 2 I_b r_w r_b ω_bi + 2 m_b r_w r_b² V_bi] / [4 I_w r_b² + I_b r_w² + m_b r_w² r_b²]
- V_bf = [2 I_w r_w r_b² ω_wi + I_b r_w² r_b ω_bi + m_b r_w² r_b² V_bi] / [4 I_w r_b² + I_b r_w² + m_b r_w² r_b²] = r_w ω_wf / 2
- ω_bf = [2 I_w r_w r_b ω_wi + I_b r_w² ω_bi + m_b r_w² r_b V_bi] / [4 I_w r_b² + I_b r_w² + m_b r_w² r_b²] = V_bf / r_b

Consequences for a ball starting at rest (my algebra from the boxed result):

- V_bf = (r_w ω_wi /2) / [1 + m_b r_w² (1+k)/(4 I_w)]
- **S_exit = 1 exactly**, independent of RPM, I_w and I_b
- Linear efficiency → 1/(2(1+k)) and total efficiency → 1/2 as I_w → ∞. The other ≥ 50% is dissipated: rigid-body inelastic "collision" losses, effectively the friction work needed to remove slip.

Spreadsheet energy definitions: E_flywheel = ½ I_w ω², E_ball,lin = ½ m_b V², E_ball,tot = E_ball,lin + ½ I_b ω_b². η_lin = ΔE_ball,lin/ΔE_fly and η_tot = ΔE_ball,tot/ΔE_fly.

### Compound flywheel (§2.4)

Apply the single-flywheel (fixed hood) formula first, then feed its outputs (V_bm, ω_bm, ω_wm) in as the initial conditions of the double/geared formula. There is no single closed form.

### ReCalc as coded in the Comparison tab (Pedersen's representation of the old method)

- V_recalc = ω r_w · 20 I_w / (7 m_b (2r_w)² + 40 I_w) = (ω r_w/2)/(1 + 0.7 m_b r_w²/I_w)
- E_loss,recalc = 0.7 m_b V² (100% transfer, solid sphere)

Compared with Pedersen's (ω r_w/2)/(1 + 0.35 m_b r_w²/I_w) for k = 2/5, ReCalc effectively halves I_w. The spreadsheet confirms this exactly: ReCalc at MOI 10 equals Pedersen at MOI 5 (13.86 m/s).

### Thread replies, as equations or claims

- **Alex_Y (#5):** motor power keeps flowing during the shot (controller bandwidth, loop discretisation, filter lag, CAN latency), which could be collapsed into one bandwidth parameter. "Even a few ms of recovery while shooting will significantly change the shot behavior." This is qualitative, with no data.
- **Pedersen (#6):** the main real-world losses are slip (too little normal force) versus compression (too much: "wasteful" friction and deformation). "No shooter ever lives close to the idealized no-compression state."

## Numeric data points

The whitepaper has no experimental data. All its numbers are model outputs for an FRC 2026 "fuel" ball. The only measured data is the reply-#6 tennis-ball plot.

| # | Quantity | Value | Conditions | Where | Type |
|---|---|---|---|---|---|
| 1 | Max linear efficiency, single wheel + hood | 25.0% (hollow cylinder, k=1); 35.71% (solid sphere); 50.0% (dense core, k→0) | Rigid, no slip, I_w→∞, ball starts at rest | PDF §2.5 table, p.6 | Theory |
| 2 | Max total efficiency, single | 50.0% for every projectile | Same | p.6 | Theory |
| 3 | Max efficiency, double (geared roller) | 50.0% for every projectile (linear = total when r_w1 = G r_w2, i.e. zero spin) | Same | p.6 | Theory |
| 4 | Max efficiency, compound | 50.0% (hollow cyl), 58.8% (solid sphere), 66.7% (dense core, at r_w1 = G r_w2) | Same | p.6 | Theory |
| 5 | Single-wheel example: exit speed | 13.86 m/s (45.47 ft/s) | Ball 5.91 in dia (r 0.0751 m), 0.5 lbm (0.2268 kg), solid sphere; wheel r 2 in (0.0508 m); I_w 5 lbm·in² (1.463e-3 kg·m²); 5940 rpm; starting at rest | Sheet "Single Flywheel" B14/D14 | Model |
| 6 | Same: exit spin / final wheel speed | 1763 rpm (184.7 rad/s) / 5210.5 rpm (12.3% drop) | Same | Sheet D13, D15 | Model |
| 7 | Same: energies | Flywheel loss 65.26 J; ball linear 21.78 J; ball total 30.49 J; η_lin 33.4%; η_tot 46.7% | Same | Sheet D19–D27 | Model |
| 8 | Same: impulses | H_w 2.200 N·s, H_h 0.943 N·s (forward), m_bΔV 3.143 N·s | Same | Sheet D33–D38 | Model |
| 9 | Double-wheel example | V 6.243 m/s; spin 11.88 rad/s (113.5 rpm, backspin); wheel 1 from 150 to 140.45 rad/s; η_lin 47.96%, η_tot 48.36% | Same ball; r_w1 2 in, r_w2 0.5 in, I_w1 20, I_w2 0.3 lbm·in², G = 3 (I_w = 22.7 lbm·in²); ω_w1i 150 rad/s | Sheet "Double Flywheel" D17–D33 | Model |
| 10 | Compound example | After the hood stage: V 3.696 m/s, spin 49.24 rad/s (S = 1). Final: V 6.303 m/s, spin 12.00 rad/s; η_lin 56.7%, η_tot 57.1% | Same as #9 with a fixed-hood stage first | Sheet "Compound Flywheel" D17–D36 | Model |
| 11 | Pedersen vs ReCalc exit speed at 5940 rpm | Pedersen 13.86 / 14.77 / 15.27 / 15.53 m/s vs ReCalc 12.34 / 13.86 / 14.77 / 15.27 m/s | MOI 5 / 10 / 20 / 40 lbm·in²; fuel ball as #5 | Appendix B plot 1, p.12; values recomputed from the sheet formulas | Model |
| 12 | Pedersen vs ReCalc flywheel energy loss at 5940 rpm | Pedersen 65.3 / 71.7 / 75.3 / 77.2 J vs ReCalc 24.2 / 30.5 / 34.6 / 37.0 J | Same | Appendix B plot 2, p.12; recomputed | Model |
| 13 | Tennis-ball launcher: linear KE vs compression | 0 mm: 0.00 J; 1: 0.39; 2: 0.84; **3: 0.90 (peak)**; 4: 0.74; 5: 0.60; 6: 0.51; 7: 0.43; 8: 0.34 J. Horizontal error bars about ±0.1–0.2 mm | "Small tennis ball flywheel launcher" by an FRC GryphonRobotics student. Wheel size, RPM, single or double wheel, hood material, ball mass and method of measuring speed are all **unreported** | Reply #6 image (6dab37e3…png). Values read off the plot, ±0.01 J | **Experimental, unreviewed, setup unknown** |
| 14 | Extrapolated zero-compression KE | ≈1.6 J (hand-drawn extrapolation of the falling branch to 0 mm) | Same | Reply #6 text and plot annotation | Guess by the author |
| 15 | Real / ideal KE ratio | ≈0.9/1.6 ≈ **56%** of the no-slip, no-compression calculator's linear KE | Same | Reply #6 text | Inference |
| 16 | Interpretation of the plot | Below ~2–3 mm, the ball still slips at exit. Above that, loss grows with compression, "mostly driven by geometry, not the mechanical work to compress the ball" | Same | Reply #6 text | Opinion |

## Applicability to POLLEN

**Transfers directly (pure kinematics and momentum, independent of the ball):**

- The fixed-hood, no-slip structure. A POLLEN ball leaving a 98 mm wheel with a fixed hood, and rolling on the hood at exit, has **S = r_bω_b/V = 1 exactly** and V = r_w ω_wf/2. The HANDOFF §4C ideal case is the G = 0 limit of this paper.
- The wheel-inertia correction. For POLLEN (r_w = 0.049 m, m_b = 0.025 kg, k = 0.4–0.67), the factor is V/(r_wω_wi/2) = 1/(1 + m_b r_w²(1+k)/(4I_w)):

  | I_w (kg·m²) | 5e-5 | 1e-4 | 2.5e-4 | 5e-4 | 1e-3 |
  |---|---|---|---|---|---|
  | k = 0.4 | 0.70 | 0.83 | 0.92 | 0.96 | 0.98 |
  | k = 2/3 | 0.67 | 0.80 | 0.91 | 0.95 | 0.98 |

  Because the ball is light (25 g versus 227 g for FRC fuel), per-shot RPM drop is small once I_w ≳ 2.5e-4 kg·m².
- The geared-roller insight: S = (r_w1 − G r_w2)/(r_w1 + G r_w2) ≤ 1. **Any roller whose contact surface moves forward reduces backspin below a fixed hood's.**

**Table P-1: Pedersen model applied to POLLEN.** My computation, not source data. Start from rest; 98 mm wheel.

| k | I_w (kg·m²) | Wheel rpm in → out | V (m/s) | Spin (rpm) | S | η_lin / η_tot |
|---|---|---|---|---|---|---|
| 2/3 | 1e-4 | 2000→1600 | 4.10 | 1104 | 1.00 | 0.27 / 0.44 |
| 2/3 | 1e-4 | 4000→3200 | 8.21 | 2208 | 1.00 | 0.27 / 0.44 |
| 2/3 | 5e-4 | 2000→1905 | 4.89 | 1315 | 1.00 | 0.29 / 0.49 |
| 2/3 | 5e-4 | 4000→3809 | 9.77 | 2629 | 1.00 | 0.29 / 0.49 |
| 2/3 | 5e-4 | 6000→5714 | 14.66 | 3944 | 1.00 | 0.29 / 0.49 |
| 0.4 | 5e-4 | 4000→3839 | 9.85 | 2649 | 1.00 | 0.35 / 0.49 |

The ideal no-slip exit speed for the PM-001 range of 2–10 m/s needs only about 800–4100 wheel rpm with a high-inertia wheel. Spin follows rigidly as ω_b = V/r_b ≈ 269 rpm per m/s (V/0.0355 m converted to rpm).

**Does NOT transfer:**

- **Every number in the whitepaper and sheet** is for FRC 2026 fuel (0.227 kg, 150 mm, solid sphere). They show the structure only.
- **No slip, no compression, rigid body.** POLLEN is a perforated hollow polyethylene shell. Hole edges and a thin wall mean the contact stiffness, friction and hysteresis are unknown. The 4 mm working compression in HANDOFF §2 is outside this model entirely.
- **The tennis-ball plot.** Its setup is unknown, and a tennis ball (felt cover, pressurised rubber core) is a different contact than a smooth or perforated PE shell. Treat it only as **qualitative evidence**:
  - there is an optimal compression, and it is sharp;
  - below it the ball slips (KE collapses: 0.39 J at 1 mm against 0.90 J at 3 mm);
  - above it, efficiency falls about 15–20% per mm;
  - the real exit KE may be only about 50–60% of the ideal calculator's.

  For POLLEN, this means exit speed could be roughly √0.56 ≈ 0.75 of the ideal V. **The effect on spin is unknown**: slip at the hood can leave S < 1, while frictional limits at the wheel can push S toward 1/k (see below).
- **The double/geared model is not our passive roller.** Pedersen's "hood roller" is mechanically coupled at a fixed ratio G. HANDOFF §4D's unpowered free roller is a different boundary condition.

## Implications for the PM-001 models

1. **Launcher baseline (fixed hood).** Implement Pedersen's Appendix-A box as `launcher_ideal_hood(I_w, ω_wi, r_w, r_b, m_b, I_b, V_bi, ω_bi)`, including the V_bi and ω_bi feeder terms. Unit-test it against these values:
   - the sheet's fuel example: 5940 rpm → 5210.5 rpm, 13.859 m/s;
   - Brettle's ratio ω_wi/ω_wf = 1 + (1+k)m_b r_w²/(4I_w);
   - S = 1.

   Label it the "rigid, no-slip upper bound on V at S = 1," not a prediction.
2. **Upper bound on spin from a fixed hood, and a hood-friction lever.** This is my derivation from the same impulse equations and has not been verified by any source. Under rigid Coulomb contact, with the ball starting at rest:
   - A frictionless hood (H_h tangential = 0) drives the ball toward **S = 1/k**: about 1.5 for a thin shell, 1.5–1.8 for a thick perforated shell. Exit speed is then V = u·k/(1+k) (≈ 0.4 u for k = 2/3), where u = r_w ω_wf is the wheel surface speed.
   - A high-friction hood that reaches rolling gives S = 1 and V = u/2.

   So **hood friction trades exit speed against spin.** Plausibly S_exit ∈ [~1, 1/k] for a fixed hood if the wheel contact does not slip. S > 1/k is not reachable. Spin depends on hood material, so model μ_hood as a parameter and measure it.
3. **The passive free roller differs in sign from the HANDOFF §4D intuition.** This is my derivation, solving the 6×6 impulse system with no slip at both contacts, roller inertia I₂ and radius r₂, an un-geared roller, and the roller starting at rest. With backspin, the ball's top surface moves **backward** (V − r_bω_b < 0 whenever S > 1). A free roller is therefore driven **backward**, and its inertia then pushes the ball forward. Results:
   - I₂ → 0 behaves like a frictionless hood: S → 1/k.
   - I₂ → ∞ behaves like a fixed high-friction hood: S → 1.
   - Example: I_w = 5e-4, 4000 rpm, k = 2/3, r₂ = 25.4 mm.
     - I₂ = 1e-6 → V 8.09 m/s, S 1.42
     - I₂ = 1e-5 → 9.00 m/s, S 1.18
     - I₂ = 1e-4 → 9.65 m/s, S 1.03
     - Fixed hood → 9.77 m/s, S 1.00

   **A passive roller cannot give less spin than S = 1 unless it is pre-spun forward. It gives more spin and less speed than a sticky fixed hood.** It also adds **shot-to-shot drift**: if the roller keeps its backward spin between rapid shots, S drifts from 1.18 to 1.42 over four shots with I₂ = 1e-5 and no bearing drag. Bearing drag and the time between shots set the reset. Verify this before relying on it.
4. **Slip and compression are first-order.** Add a time-domain contact model with these elements:
   - a normal force N(δ) from the measured compression of the POLLEN shell;
   - Coulomb friction at the wheel and at the hood or roller;
   - integration along the contact arc;
   - motor torque with a bandwidth or latency term, as suggested by Alex_Y.

   Calibrate it with a **compression sweep**, for example 1–8 mm in 1 mm steps (the tennis data suggests a sharp optimum near 4% of diameter, about 3 mm for 67 mm). At each step, measure V and spin with high-speed video. Carry an efficiency knockdown of about 0.5–1.0 on KE (V factor 0.7–1.0) as uncertainty until measured.
5. **Spin and speed are coupled for a single wheel with a fixed hood.** No-slip theory gives S ≈ 1 at every RPM. The only independent levers are:
   - hood friction or a passive roller (S from 1 up to about 1/k),
   - compression and slip (lowers both V and S),
   - feeder pre-spin ω_bi (enters through the I_b ω_bi terms),
   - the effective contact radius under compression (r_b − δ_h raises the apparent S slightly, e.g. 35.5/33.5 ≈ 1.06 for 2 mm at the hood).

   The feasibility study should therefore scan S_exit within about [0.7, 1.6], not treat it as a free parameter up to 2. S > 1/k needs a counter-driven top wheel, which is out of scope.
6. **Flywheel sizing.** Use Pedersen's energy drain, at least twice the ball's KE (η_tot ≤ 50%), for RPM recovery. Do not use ReCalc's 100% assumption. For POLLEN at 10 m/s the ball's KE is only about 1.25 J linear + 0.8 J spin, so drain per shot is about 4–5 J. The I_w choice is driven by keeping per-shot RPM drop under about 2–5% for consistency (I_w ≳ 5e-4 kg·m²), not by energy.
7. **Measure I_b for POLLEN.** It enters both the S = 1/k frictionless-hood limit and the inertia factor. Use a bifilar or trifilar pendulum, or compute it from wall thickness and hole pattern in the AndyMark STEP model. Do not use 2/5 m r².

## Caveats

- This source is unreviewed, purely theoretical, and has no validation against data. Its author states that "no slip at exit" has never been empirically validated.
- My checks used the PDF and sheet as downloaded on 2026-10-30. The "latest" PDF link may change.
- Implications 2, 3 and Table P-1 are **my own derivations and calculations** using Pedersen's framework, for the lead to verify. They are not claims made by Pedersen.
- The tennis plot values were read by eye from a PNG. The experiment's ball, wheel, speed and measurement method are unknown, so it is anecdotal.
- A possible apparent tension, to reconcile with the Brettle note: Brettle says his model predicts *half* the wheel-speed loss of 846's formula, while Pedersen says ReCalc *underestimates* energy drain. They compare against different predecessor formulas (846's original versus ReCalc's coded version), so this is not necessarily a contradiction.
