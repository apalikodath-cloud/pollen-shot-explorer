# Sweep: flywheel / hood ball launchers (launch-side physics)

Sweep id: `sweep_launch`. Written 2026-10-30. Scope: pitching and ball-throwing machines (single- vs two-wheel spin control), FRC/FTC shooters other than Brettle and Pedersen, contact mechanics of compressed hollow balls in launchers (slip, contact time, hood friction), passive roller vs fixed hood, and flywheel energy recovery.

The 12 priority papers are not repeated here. Note that the MBHS PDF found in this sweep is Pedersen 2026, which another agent already covers.

Evidence labels used below:
- **PR**: peer-reviewed journal or conference proceedings, full text read.
- **PR-abs**: peer-reviewed, but only the abstract or secondary descriptions were read.
- **UNREV**: forum post, documentation or web page.
- **CALC**: my own arithmetic from the source data. It is not a claim the source makes.

## 1. Sources

| id | Citation | URL used | Review status | Access | What it contributes |
|---|---|---|---|---|---|
| drane2018 | Drane P., Dhavale A., Hansen R., Kelley J., Burke J. "A Study of the Interaction between Batting Cage Baseballs and Pitching Machine." Proceedings 2018, 2(6), 203 (ISEA 2018). doi:10.3390/proceedings2060203 | https://mdpi-res.com/d_attachment/proceedings/proceedings-02-00203/article_deploy/proceedings-02-00203.pdf | PR (conference proceedings, CC-BY) | full text | Measured exit speed and spin vs wheel rpm on a two-wheel machine with foam balls. Shows how low S is on a typical two-wheel machine, and how wear reduces consistency. |
| dittrich2023 | Dittrich A., Schneider J., Guist S., Schölkopf B., Büchler D. "AIMY: An Open-source Table Tennis Ball Launcher for Versatile and High-fidelity Trajectory Generation." IEEE ICRA 2023. doi:10.1109/ICRA48891.2023.10160336; arXiv:2210.06048 | https://arxiv.org/abs/2210.06048 | PR (conference) | full text (arXiv) | Benchmarks three-wheel and single-wheel commercial launchers on speed, spin and repeatability. Includes a ball-pinching (compression) sweep and a wheel ramp-up time study. Reports that friction and slip made an analytic launch model inadequate. |
| basyiruddin2025 | Basyiruddin et al. "Modeling and Ball Speed Validation of a New Sepaktakraw Ball Launcher." Malaysian J. Sport Sci. & Recreation 21(1):1-9, 2025. doi:10.24191/mjssr.v21i1.5666 | https://doi.org/10.24191/mjssr.v21i1.5666 (journal PDF) | PR (regional journal, weak methods) | full text | Hollow, perforated woven ball on two EVA rollers. Measured speed was about 59% of the no-slip prediction, and the gap grew with rpm. Quotes a table tennis launcher (Ponnusamy 2015) reaching only about 41% of theory. |
| cheng2026 | Cheng, Yang, Sun, Li. "Research on mechanical properties of the launching mechanism of the RoboMaster." J. Phys.: Conf. Ser. 3312, 012016 (2026). doi:10.1088/1742-6596/3312/1/012016 | https://iopscience.iop.org/article/10.1088/1742-6596/3312/1/012016 (OA PDF) | PR (conference series; light review) | full text | Dual polyurethane friction wheels on a 42 mm hollow plastic ball. Combines a modified Hertz contact, Stribeck friction and FE. Sweeps wheel spacing experimentally and finds an interior optimum; over-compression stops the launch. |
| sakai2017 | Sakai S. & Kitade Y. Four-roller (2 launch + 2 gyro) table tennis machine. Trans. JSME 83(856), 17-00225 (2017). Japanese. | J-STAGE (free full text, Japanese, 14 pp.) | PR | This sweep saw only the English abstract; the full text was later read (research/papers_extra/launch_methods_check.md) | Reports that roller machines can reach very high spin (>5000 rpm on a 40 mm ball; the full text gives 5500 or 7000 rpm top/back and is internally inconsistent) with a landing-position **standard deviation** under 40 mm (confirmed, figure reading). It also measures v_B ≈ 0.48 v_Rx (confirmed). |
| nathan2008 | Nathan A.M. "The effect of spin on the flight of a baseball." Am. J. Phys. 76:119 (2008); arXiv:physics/0605041 | https://arxiv.org/abs/physics/0605041 | PR | full text | Uses a two-wheel ATEC machine as the launcher and states its kinematics (speed from the wheel-speed mean, spin from the difference). Covers S 0.1-0.6. Mostly aerodynamics, which the aero sweep owns. |
| vaziri2008 | Vaziri A., Mahadevan L. "Localized and extended deformations of elastic shells." PNAS 105:7913-7918 (2008). | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2430338/ | PR | full text (FE study) | Thin-shell indentation is linear only while deflection is of order the wall thickness. Beyond that the response becomes nonlinear, and stiffness drops when the deformation localizes. This supports not using Hertz for the POLLEN shell. |
| couturier2022 | Couturier E., Vella D., Boudaoud A. "Compression of a pressurized spherical shell by a spherical or flat probe." Eur. Phys. J. E (2022); arXiv:2111.09710 | https://arxiv.org/abs/2111.09710 | PR | full text (arXiv v2) | At small compression a shell behaves as a linear spring independent of probe shape (flat plate, i.e. wheel or hood, vs sphere). Mainly about pressurized cells. POLLEN is perforated, so p=0 and only the bending/stretching (Reissner) limit applies. |
| pauchard1998 | Pauchard L., Rica S. "Contact and compression of elastic spherical shells: the physics of a 'ping-pong' ball." Phil. Mag. B 78(2):225-233 (1998). | secondary descriptions only | PR-abs | not read | Reports a flattening phase, then sudden buckling with a dimple, under plate compression of a ping-pong ball. No numbers taken. |
| wojcicki2011 | Wojcicki et al., tennis ball launcher dynamics, Acta Mech. Autom. 5(4):110-119 (2011). | Poznan repository (blocked by browser verification) | PR-abs | not read | Listed only so it is not re-searched. No data taken. |
| luo2025 | Luo et al., Frontiers in Mechanical Engineering 11:1707301 (2025). Launcher optimization by simulation, NN and GA. | frontiersin.org | PR | skimmed | Excluded: simulation only, with no launcher experiments. |
| cd_hoodcomp2020 | Chief Delphi thread "Hood Compression" (2020). | chiefdelphi.com | UNREV (forum) | read | FRC practice: about 2-2.5 in of compression on 4 in wheels with a 7 in foam ball. Logged exit speed was "much lower" than calculated. PTFE was suggested for the hood, with no friction coefficient measured. |
| cd_ballcomp2012 | Chief Delphi thread "Ball Compression Data" (2012). | chiefdelphi.com | UNREV (forum) | read | A load cell measured peak force at 1.25 in compression across a batch of foam balls. Spread within one ball was 2.6-12.5%, and spread between balls was larger. Several teams sensed ball compression to adjust shot speed. |
| wpilib_flywheel | WPILib docs, "Tuning a Flywheel Velocity Controller." | docs.wpilib.org | UNREV (official docs) | read | With feedforward only, the flywheel "takes a while to recover after the ball is introduced". Adding P feedback recovers quickly, and bang-bang control is fastest. No numeric recovery time is given. |

## 2. Data extracted

### 2.1 drane2018: two-wheel pitching machine, foam batting-cage balls (Table 1)

Ball: polyurethane foam baseball, circumference 8.92 in (R about 36.1 mm, very close to POLLEN's 35.5 mm). Mass 5.14 oz (yellow, about 146 g) and 4.80 oz (orange, about 136 g). COR 0.486, vs 0.545 for a collegiate baseball. The paper does not give wheel diameter or the upper/lower wheel speed ratio.

| Lower wheel rpm | Ball | Exit speed (m/s) | Spin (rpm) | S = wR/v (CALC) |
|---|---|---|---|---|
| 1600 | yellow new | 18.3 +/- 0.4 | 754 +/- 80 | 0.156 |
| 1800 | yellow new | 21.9 +/- 0.3 | 701 +/- 52 | 0.121 |
| 2400 | yellow new | 33.1 +/- 0.3 | 1633 +/- 46 | 0.186 |
| 1600 / 1800 / 2400 | orange new | 18.3 / 21.9 / 33.1 | 794 / 767 / 1573 | 0.16 / 0.13 / 0.18 |
| 1600 / 1800 / 2400 | yellow end-of-life | 18.4 / 22.8 / 33.1 | 667 / 665 / 1727 | 0.14 / 0.11 / 0.19 |
| 1600 / 1800 / 2400 | orange end-of-life | 18.8 / 22.3 / 33.2 | 775 / 745 / 1727 | 0.16 / 0.13 / 0.19 |

Other findings:
- Ball orientation (seam) had no measurable effect on exit speed.
- Higher speed gave more consistent pitches and more backspin.
- End-of-life balls had larger scatter.
- High-speed video was taken at 1000-3000 fps.
- CALC: exit speed rose x1.81 while lower-wheel rpm rose x1.50. So the machine's dial probably changes the wheel ratio as well, and slip cannot be backed out from this data.

### 2.2 dittrich2023: AIMY and commercial table tennis launchers (40 mm, 2.7 g ball)

Table VIII, maxima. Speed and spin were measured separately, not on the same shot.

| Launcher | Wheels | Max speed (m/s) | Max topspin (paper's unit "s^-1") |
|---|---|---|---|
| Professional human | - | 16.8 | 113.9 |
| TTmatic 303A | single wheel + slide | 9.8 | 64.0 |
| Donic Robo-Pong 2050 | single wheel | 10.7 | 106.7 |
| AIMY (MN4004 motors) | 3 wheels at 120 deg | 10.8 | - |
| AIMY (MN5008 motors) | 3 wheels at 120 deg | 15.4 | 192.0 |

Unit ambiguity (CALC): the spin is given in "s^-1". If that means rev/s, the single-wheel machines reach S = wR/v of about 0.82 (TTmatic, 64 rev/s at 9.8 m/s) and 1.25 (Robo-Pong). If it means rad/s, S is about 0.13-0.20. The magnitude and the human value (114 rev/s is about 6800 rpm, plausible for elite topspin) suggest rev/s. On that reading, single-wheel machines with a fixed backplate reach S of order 1, which matches the ideal hooded-wheel kinematics. Treat this as unconfirmed. The paper also does not give the speed at which max spin was reached.

Table VI, pinch sweep (ball squeeze between wheels, 40 mm ball). Landing-point standard deviation:

| Pinch diameter (mm) | Squeeze (mm, CALC) | std x (m) | std y (m) |
|---|---|---|---|
| 35.3 | 4.7 | 0.0319 | 0.0306 |
| 35.8 | 4.2 | 0.0193 | 0.0266 |
| 36.4 | 3.6 | 0.0191 | 0.0217 |
| 37.0 | 3.0 | 0.0197 | 0.0248 |
| 37.4 | 2.6 | 0.0187 | 0.0221 |
| 38.6 | 1.4 | 0.0236 | 0.0243 |

- There is a broad optimum around 2.6-3.6 mm of squeeze, about 6.5-9% of diameter. Too much squeeze is the worst case. The "squeeze" column is diameter minus pinch diameter, not per-side compression.
- Wheels are Butterfly hard foam. A "compliant body and roughened surface reduces slip."
- Ramp-up below 0.5 s increases scatter: with a 0.01 s ramp, std x is 0.040 m, vs about 0.023 m for ramps of 0.5 s or more. The authors recommend a 3 s settle for non-continuous operation.
- Landing scatter across the launchers tested was 0.007-0.042 m.
- Spin was measured from marked balls filmed at 960 fps.
- The authors used a learned (NN) model because the analytic wheel model did not capture "friction and slip in the launch unit."

### 2.3 basyiruddin2025: sepak takraw launcher (hollow perforated woven ball)

Setup:
- Ball: 180 g, R 6.5 cm, hollow woven synthetic rattan (perforated shell, like POLLEN).
- Two EVA rollers, 15 cm diameter, maximum 7000 rpm.
- Roller gap 15 cm. That is about 2 mm more than the ball diameter, so there is essentially no nominal squeeze.
- Speed was measured with 480 fps video in Kinovea.

| Setting | Theory v = (v1+v2)/2 (km/h) | Measured (km/h) | Ratio (CALC) |
|---|---|---|---|
| 70% | about 70 | about 35 | about 0.5 |
| 100% | 100 | 59.4 | 0.59 |

- The deficit grew from 34.6 km/h at 70% to 40.6 km/h at 100%.
- The authors suggest closing the gap by 1-2 mm to increase grip.
- Quoted from Ponnusamy 2015 (not read): a table tennis launcher measured 17.806 m/s vs 43.29 m/s theoretical, a ratio of 0.41.

### 2.4 cheng2026: RoboMaster dual friction wheels, 42 mm hollow plastic ball

Model parameters:
- Modified Hertz contact with nonlinear coefficient 0.2, critical compression 4.2 mm, exponent 1.5 and R_eff 24.7 mm.
- Stribeck friction with mu_s = 0.5 and mu_k = 0.4.
- PU wheel E = 5e7 Pa, nu = 0.48.

Results:
- FE predicted 16.6-16.9 m/s at 6000 rpm.
- Experiments ran at 5000, 6000 and 7000 rpm, with at least 25 shots per wheel spacing.
- At 95 mm spacing the ball failed to launch (overload, so over-compression stalls).
- 97 mm spacing gave the highest mean speed and the best consistency, and was the best spacing in 90% of tests. Spacings from 96 to 99 mm were tested.
- Numeric velocities appear only in figures and were not digitized.

### 2.5 sakai2017 (abstract here; full text read in research/papers_extra/launch_methods_check.md)

Four-roller machine (2 launch + 2 gyro) for a 40 mm ball. Maximum speed 42.5 m/s, spin above 5000 rpm (confirmed). Landing position: standard deviation under 40 mm in X and Z for no, top and side spin, and about 60 mm X / 140 mm Z in gyro mode, over 40 balls at v_Rx = 15 m/s (confirmed, figure reading of Fig 7 in the full text). The 40 mm is an SD, not a mean offset or a maximum scatter. This sweep first took the numbers from the English abstract.

### 2.6 nathan2008

On the ATEC two-wheel machine, exit speed is the mean of the two wheel tangential speeds and spin comes from their difference. The data covered 50-110 mph, 1500-4500 rpm and S 0.1-0.6. CL was about 0.20 for S 0.15-0.30. The launch kinematics are stated as the operating principle, not as a validated slip model.

### 2.7 Hollow-shell contact (vaziri2008, couturier2022, pauchard1998)

- vaziri2008 (FE): the shell responds linearly only while indentation is of order the wall thickness t. After that it is nonlinear. For t/R = 0.005, deformation localizes (three vertices) at Z/R of about 0.076, and stiffness drops by about 30%.
- couturier2022: at small compression, a pressurized shell is a linear spring whose stiffness does not depend on probe shape (point, sphere or plate). The closed form needs the pressure. POLLEN is perforated, so its internal pressure is about 0, which leaves the unpressurized (Reissner) limit.
- Unpressurized point-load stiffness is K = 4 E t^2 / (R sqrt(3(1-nu^2))) (Reissner). This is from memory and not verified from a source read in this sweep. Large-deflection (Pogorelov) behavior is F ~ delta^(1/2), also from memory and secondary sources.
- pauchard1998 (secondary only): under a plate, the ball first flattens and then suddenly buckles into an inverted dimple.

### 2.8 FRC/FTC practice (unreviewed)

- cd_hoodcomp2020: teams used about 2-2.5 in of compression on 4 in wheels, about 29-36% of a 7 in foam ball's diameter. "2 in" was called the sweet spot. Logged exit speeds were "much lower" than calculated. PTFE or UHMW was suggested for the hood, with no friction coefficient given.
- cd_ballcomp2012: peak force at 1.25 in of compression varied 2.6-12.5% within one ball and more between balls. Teams 2169, 1625, 525 and 1218 used compression sensing to adjust shot speed.
- wpilib_flywheel: feedforward is V = kS sgn(w) + kV w + kA dw/dt. Feedforward alone recovers slowly after a ball passes, and feedforward plus P (or bang-bang) recovers fast. The simulation example uses kV = 0.0075 V/(rpm). No recovery-time numbers are given.

## 3. Key equations

1. Ideal no-slip hooded single wheel (fixed hood):
   - v_b = u_w / 2 and w_b = v_b / r_b, so S_exit = 1. This is backspin, with the ball rolling on a stationary hood.
2. Ideal two-wheel (or wheel plus driven roller) launcher:
   - v_b = (u1 + u2) / 2 and w_b r_b = (u1 - u2) / 2 (nathan2008, basyiruddin2025).
   - S_exit = (u1 - u2) / (u1 + u2).
   - A passive or geared upper roller turning at surface speed u2 = G u1 lowers spin, and gives topspin if u2 > u1 (consistent with Pedersen's hood-roller result; not repeated here).
3. Measured efficiency factors (my framing; the sources give the ratios):
   - v_exit = eta_v * u_w / 2 and w_exit = eta_w * v_exit / r_b.
   - Observed eta_v is 0.41-0.59 for gapped or lightly squeezed two-roller launchers (basyiruddin2025, Ponnusamy via basyiruddin2025).
   - FRC "much lower than calculated" is qualitative.
   - No source gives a measured eta_w for a fixed-hood single wheel. The dittrich2023 single-wheel data suggest S of about 0.8-1.25 if the units are rev/s.
4. Compression optimum: there is an interior optimum in squeeze for both speed and scatter.
   - Too little squeeze lets the ball slip and gives low, variable speed.
   - Too much squeeze stalls the launch (cheng2026 at 95 mm), increases scatter (dittrich2023 at 4.7 mm on 40 mm) and loses energy.
5. Contact law for the POLLEN shell: N(delta) is linear (Reissner) for delta of order t, then follows a softening, buckling branch (F ~ delta^0.5). It is not Hertz F ~ delta^1.5, which cheng2026 assumes for a thicker ball.
6. Flywheel feedforward: V = kS sgn(w) + kV w + kA dw/dt. Shot-to-shot speed drop is roughly dw/w = (energy given to the ball) / (I_w w^2), with energy-transfer efficiency at most 50% (Pedersen; not repeated).

## 4. POLLEN applicability

What transfers:
- The kinematic laws. v = (u1+u2)/2, and v = u/2 with S = 1 for a hood, depend only on rolling without slip, not on ball type.
- The qualitative and semi-quantitative facts:
  - Real launchers deliver about 40-60% of the no-slip speed when grip is marginal.
  - There is a compression optimum.
  - Ramp-up and recovery time matter for repeatability.
  - Single-wheel machines with a fixed plate or slide can produce large spin (S of order 1).
- The basyiruddin2025 ball is the closest analogue: a hollow, perforated, low-stiffness shell. drane2018's ball radius (36.1 mm) is almost identical to POLLEN's 35.5 mm.

What does not transfer:
- Masses differ: 136-180 g (foam baseball, takraw) and 2.7 g (table tennis) vs about 25 g for POLLEN. Wheel inertia ratios therefore differ, which changes per-shot speed drop and energy efficiency.
- Contact stiffness: foam baseballs are solid foam (Hertz-like), and ping-pong balls are thin closed celluloid or ABS shells. POLLEN is a perforated PE shell whose N(delta) must be measured.
- Friction coefficients (cheng2026 PU-on-plastic mu 0.4-0.5, EVA, hard foam) are not POLLEN-on-wheel or POLLEN-on-hood values.
- drane2018 S values (0.12-0.19) come from a two-wheel machine with a small speed difference, not a fixed hood. They show how hard the hood geometry has to work to approach S = 1. They are not a POLLEN prediction.
- Reynolds number has no bearing on the launch itself.

CALC for the POLLEN wheel (R_w = 0.049 m, r_b = 0.0355 m), no-slip fixed hood:

| Wheel rpm | Surface speed u_w (m/s) | Ideal v_exit (m/s) | Ideal ball spin (rpm) | v_exit at eta_v = 0.55 (m/s) |
|---|---|---|---|---|
| 2000 | 10.3 | 5.1 | 1380 | 2.8 |
| 3000 | 15.4 | 7.7 | 2070 | 4.2 |
| 4000 | 20.5 | 10.3 | 2760 | 5.6 |
| 5000 | 25.7 | 12.8 | 3450 | 7.1 |
| 6000 | 30.8 | 15.4 | 4140 | 8.5 |

So a 6-8 m/s shot needs about 2350-3100 wheel rpm with no slip, and about 4300-5700 rpm if eta_v is about 0.55. The required range roughly doubles between those cases, so measuring eta_v is the first launcher test.

## 5. Model implications for PM-001

1. **Replace the ideal launch with slip factors.** Use v_exit = eta_v u_w/2 and w = eta_w v_exit/r_b.
   - Defaults: eta_v in [0.45, 1.0], centered at about 0.7 for an optimal squeeze; eta_w in [0.5, 1.0].
   - Treat S_exit = 1 as an upper bound, not the nominal value.
   - Propagate both factors as uncertainty in the trajectory Monte Carlo.
2. **Treat compression as a design variable with an interior optimum.** Sweep it in tests (for example 2, 3, 4, 5, 6 mm), recording v, w and scatter.
   - In dittrich2023 the best scatter came at about 6.5-9% of diameter squeeze. For a 71 mm ball, that suggests 4.6-6.4 mm total, so the 4 mm candidate is plausible but possibly light. This is an analogy, not a prediction.
   - In cheng2026, 2 mm less spacing than the optimum caused launch failure. So keep a stall margin.
3. **Do not use Hertz for the POLLEN contact.** Use a measured N(delta), or a linear-then-softening shell law. The normal force sets the friction available to the hood and wheel, and so sets eta_v and eta_w.
4. **Hood friction is a backspin lever.** A slippery hood (PTFE or UHMW, as FRC teams use) lets the ball slide rather than roll, which lowers spin. Model hood friction mu_h explicitly, and do not assume rolling on the hood. An eta_w below 1 is the expected result of low mu_h.
5. **A passive upper roller is a spin reducer.** A free roller ends up near the ball's surface speed and partly cancels hood-induced backspin. Choose a fixed, grippy hood if maximizing backspin is the goal. A geared roller is a spin-trim knob.
6. **Model flywheel recovery and ramp time.**
   - Per-shot wheel speed drop is energy-limited; use Pedersen's efficiency at most 50% with the POLLEN mass of about 25 g against the actual wheel inertia.
   - Use feedforward plus feedback or bang-bang control.
   - Include a recovery-time term in the cycle model. dittrich2023 saw scatter rise with ramp time below 0.5 s.
7. **Expect ball-to-ball variation.** FRC load-cell data shows within-ball stiffness spread up to about 12% and larger spread between balls, and drane2018 showed worn balls are less consistent. Measure several POLLEN balls, new and worn.

## 6. Caveats

- dittrich2023 spin units are ambiguous (rev/s vs rad/s), and max speed and max spin were not measured on the same shot.
- drane2018 does not give wheel diameter or wheel speed ratio, so its data cannot calibrate slip. It is only evidence of the S range on a two-wheel machine.
- basyiruddin2025 has thin methodology (single-camera Kinovea, few trials, the 70% theory value read from text). The Ponnusamy 2015 ratio is second-hand.
- cheng2026 velocity numbers are in figures only. Its contact law (modified Hertz) is a model choice, not a validated shell law.
- pauchard1998 was not read in full. sakai2017 and wojcicki2011 were not read by this sweep but were later read in full (research/papers_extra/launch_methods_check.md). The Reissner and Pogorelov formulas above are from memory and unverified.
- Forum sources are practitioner reports with no controlled measurement.
- None of the sources measures a fixed-hood single wheel launching a perforated polyethylene shell. The POLLEN launcher's eta_v, eta_w and compression optimum must be measured directly.
