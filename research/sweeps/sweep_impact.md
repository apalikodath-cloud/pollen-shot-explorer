# Sweep: oblique impacts of spinning balls, rim/lip contact, and trajectory reconstruction (PM-001)

Swept: 2026-10-30. Scope: sources the lead did not already have, outside the 12 priority papers.
The topic is oblique impacts of spinning hollow or plastic balls, rim/edge collisions and ball retention, and how to recover Cd, Cl and spin from video.
Status labels: **PR** = peer-reviewed journal; **CONF** = conference proceedings; **PRE** = preprint; **STD** = equipment standard.
Numbers are quoted from the full text I read unless they are marked *abstract only*, *secondary* or *derived here*.

## Sources

| id | Citation | URL | Status | Access | What it contributes |
|---|---|---|---|---|---|
| cross2002hcor | R. Cross, "Measurements of the horizontal coefficient of restitution for a superball and a tennis ball", Am. J. Phys. 70(5):482–489 (2002), doi:10.1119/1.1450571 | https://www.physics.usyd.edu.au/~cross/PUBLICATIONS/20.%20HorizCOR.PDF | PR | full text | Garwin and Brody bounce models extended to a hollow shell (α = 2/3). Gives closed forms for rebound vx, ω and rebound angle, the rolling threshold, and μ_s/μ_r/e_y measured on 3 surfaces. Uses a 100 fps video method. |
| cross2002grip | R. Cross, "Grip-slip behavior of a bouncing ball", Am. J. Phys. 70(11):1093–1102 (2002), doi:10.1119/1.1507792 | https://www.physics.usyd.edu.au/~cross/PUBLICATIONS/21.%20GripSlip.PDF | PR | full text | Force-plate measurements of N and F. Shows real balls grip (they do not roll) and the friction force reverses during contact. Gives e_x ≈ 0.1–0.2 when gripping and a normal-force offset D ≈ 2 mm. Tests the Maw–Barber–Fawcett (MBF) model against superball and golf ball data. |
| cross2010tang | R. Cross, "Impact of a ball on a surface with tangential compliance", Am. J. Phys. 78(7):716–720 (2010), doi:10.1119/1.3313455 | https://www.physics.usyd.edu.au/~cross/PUBLICATIONS/47.%20MoreSpin.pdf | PR | full text (skimmed) | Lumped model in which a ball grips a light, spring-mounted "cart" (the surface). Stored tangential energy is returned through static friction, which raises the rebound spin. This analogue applies both to a passive roller and to a compliant HIVE panel. |
| cross2012liftdrag | R. Cross, "Measuring the effects of lift and drag on projectile motion", Phys. Teach. 50(2):80–82 (2012), doi:10.1119/1.3677279 | https://www.physics.usyd.edu.au/~cross/PUBLICATIONS/57.%20LiftDrag.pdf | PR (education journal; author preprint read) | full text | Inverse dynamics: F_D and F_L are taken directly from the fitted x(t), y(t) of a light, strongly backspun body filmed at 30 fps, with spin measured at 300 fps. Reports that a **70 mm, 10 g plastic ball showed a less dramatic lift effect** than cups. |
| nathan2006spin | A.M. Nathan, J. Hopkins, L. Chong, H. Kaczmarski, "The effect of spin on the flight of a baseball", arXiv:physics/0605041 (2006); the conference paper is the precursor of Nathan, Am. J. Phys. 76:119 (2008) | https://arxiv.org/pdf/physics/0605041 | PRE / CONF (Engineering of Sport 6; I did not verify the proceedings pages) | full text | The canonical high-speed-video least-squares method: a 9-parameter fit of a single marker dot gives CM trajectory, ω, Cl and Cd. Shows that **Cl is well determined from vertical curvature and Cd poorly from horizontal curvature**. |
| tebbe2020spin | J. Tebbe, L. Klamt, Y. Gao, A. Zell, "Spin detection in robotic table tennis", ICRA 2020; arXiv:1905.07967v2 | https://arxiv.org/pdf/1905.07967 | CONF (IEEE ICRA; I read the arXiv v2 copy) | full text | Spin estimated from the trajectory alone by linear least squares on ω after polynomial-fitting position. Uses a light hollow ball (2.7 g, r = 20 mm). The Magnus fit is **independent of k_D**. A Kalman filter is the baseline. Gives bounce-point error with and without fitted spin. |
| okubo2004rim | H. Okubo, M. Hubbard, "Dynamics of basketball–rim interactions", Sports Eng. 7(1):15–29 (2004), doi:10.1007/BF02843970 | https://link.springer.com/article/10.1007/BF02843970 | PR | **abstract only** | Compliant-ball / toroidal-rim contact model with slip, no-slip and flight sub-models. Capture is "extremely sensitive" to contact position and **backspin**; "Backspin aids capture on long-rolling trajectories." |
| hubbard2005isb | M. Hubbard, "Spinning sports balls", ISB XXth Congress / ASB 29th Annual Meeting, Cleveland (2005), abstract 990 | https://media.isbweb.org/images/conf/2005/abstracts/0990.pdf | CONF abstract (unreviewed in the journal sense) | full text (1 page) | Summarises Okubo & Hubbard: backspin "can scrub more energy from the ball in shots that hit the rim", **increasing successful free throws by about 10%** with all else held constant. Basketball–rim impact ≈ 11 ms. |
| antali2021rim | M. Antali, V. Havas, S.J. Hogan, G. Stépán, "Nonlinear dynamics of a basketball rolling around the rim", Nonlinear Dyn. 104:3013–3037 (2021), doi:10.1007/s11071-021-06507-y (CC BY) | https://link.springer.com/content/pdf/10.1007/s11071-021-06507-y.pdf | PR | full text (skimmed) | Rigid sphere rolling on a rigid torus with Coulomb μ. Rolling without slip on top of a rim is possible only within **±arctan μ of the crest**. In/out outcome is very sensitive to the dissipation model. |
| haron2012cor | A. Haron, K.A. Ismail, "Coefficient of restitution of sports balls: a normal drop test", IOP Conf. Ser.: Mater. Sci. Eng. 36:012038 (2012), doi:10.1088/1757-899X/36/1/012038 | https://iopscience.iop.org/article/10.1088/1757-899X/36/1/012038/pdf | CONF (IOP proceedings, open access) | full text | Drop-test COR at 250 fps for golf, table tennis, hockey (71 mm plastic) and cricket balls on steel and wood. **The light hollow ball loses only 4.3% COR on the softer target, while the heavy balls lose 24–43%.** |

Searched but not obtained:
- Maw, Barber & Fawcett, Wear 38:101 (1976), doi:10.1016/0043-1648(76)90201-5, and J. Lubr. Technol. 103:74 (1981), doi:10.1115/1.3251617. Paywalled. I use them here only as described by cross2002grip.
- Cross, "Oblique bounce of a rubber ball", Exp. Mech. 54:1523–1536 (2014), doi:10.1007/s11340-014-9938-3. Abstract only. A **hollow** rubber ball gripped at all incidence angles and had much higher μ than a superball, with 1–2 friction-force reversals. e_x depends on μ and on the ratio of tangential to normal vibration frequency. No numbers were reachable.
- Okubo & Hubbard, J. Sports Sci. 24:1303 (2006). Abstract only (secondary). More backspin, lower inflation and underhand release give higher capture percentages.
- Silverberg, Tran & Adcock, J. Dyn. Syst. Meas. Control 125:531 (2003). Press coverage only: backspin "deadens" rim/board contact, with ~3 rev/s recommended. These figures are unverified.
- I found **no peer-reviewed oblique-impact study of a perforated polyethylene (wiffle, pickleball or POLLEN-type) ball**. The closest datum is the USA Pickleball equipment standard (STD, secondary copy): a 78 in drop on granite must rebound 30–34 in. That implies e ≈ √(30/78)…√(34/78) ≈ 0.62–0.66 (*derived here*; this ignores the top-of-ball measurement offset and drag). It is not POLLEN data.

## Key equations (2D impact on a locally flat surface; t = tangential, n = normal)

The notation is shared with the HANDOFF frame. α = I/(mR²): 2/5 for a solid sphere, 2/3 for a thin shell. POLLEN is a thin perforated shell, so α ≈ 2/3 is assumed, and it **must be measured** (bifilar or torsion pendulum).
Sign convention: ω_b > 0 is backspin relative to the approach direction, so at a floor or lip contact the contact-point slip is u = v_t + R ω_b.

1. Normal restitution: v_n2 = −e_y v_n1. Normal impulse J_n = m(1+e_y)|v_n1|.
2. Sliding throughout the impact (Brody; cross2002hcor Eqs. 11–13):
   v_t2 = v_t1 − μ(1+e_y)|v_n1|,  ω_b2 = ω_b1 − μ(1+e_y)|v_n1|/(αR).
3. Sliding stops (grip or roll) if μ(1+e_y)|v_n1|(1+1/α) ≥ v_t1 + R ω_b1. This is the rolling threshold of cross2002hcor Eq. 15 written for general α.
4. Grip with tangential restitution e_x (Garwin model generalised; cross2002hcor Eqs. 5 and 7; e_x = −u2/u1):
   v_t2 = [(1 − α e_x) v_t1 − α(1+e_x) R ω_b1]/(1+α).
   The rolling limit is e_x = 0, giving v_t2 = (v_t1 − α R ω_b1)/(1+α).
   For ω1 = 0, e_x = 1 and a shell: v_t2 = 0.2 v_t1 and R ω2/v_t2 = 6.
5. Impulse cap. Whatever the spin, |Δv_t| ≤ μ(1+e_y)|v_n1|. A sliding ball rebounds **backwards** only if μ > tan(θ_n)/(1+e_y), where θ_n is the incidence angle from the surface normal. Once the ball is sliding throughout, more backspin cannot change v_t2; it only changes the residual spin. (*derived from 2.*)
6. Normal-force offset D (cross2002grip): adds torque N·D, so the ball spins more than friction alone predicts. D ≈ 2 mm for a tennis ball.
7. Cross 2012 inverse dynamics, with θ the path angle and a_x, a_y from smoothed fits:
   F_D = −m(g sin θ + a_x cos θ + a_y sin θ),  F_L = m(g cos θ − a_x sin θ + a_y cos θ).
8. Nathan 2006 marker model: y(t) = y_cm(t) + A sin(ωt+φ), z(t) = z_cm(t) ± A cos(ωt+φ). y_cm and z_cm are integrated with constant Cd and Cl. Nine free parameters: 4 initial conditions, A, ω, φ, Cl, Cd.
9. Tebbe 2020: v̇ = −k_D|v|v + k_M ω×v − g ẑ, with k_D = ½C_D ρ A/m and k_M = ½C_M ρ A r/m.
   Position is fitted with a cubic P(t) per axis. Then k_M ω × Ṗ(t_i) = P̈(t_i) + k_D|Ṗ|Ṗ + g ẑ is stacked as M ω = a and solved by least squares for ω. Drag is parallel to v and drops out of the ⊥-to-v component.
10. Rim rolling (antali2021rim): a rolling steady motion without slip exists only for |φ₀ − π/2| < arctan μ near the rim crest. For μ = 1 this is 45°.
11. Acceleration noise of a quadratic fit (*derived here, Monte-Carlo checked*): σ_a ≈ 2σ_pos √(180/(N T⁴)).

## Data points (selected)

| source_id | quantity | value | conditions | where |
|---|---|---|---|---|
| cross2002hcor | e_y (vertical COR) | 0.77 ± 0.01 | tennis ball 57 g, R = 33 mm, drop 0.3–1.0 m, timber/emery/Rebound Ace | §VI |
| cross2002hcor | μ_s (sliding) | 0.23 ± 0.02 wood; 0.60 ± 0.03 Rebound Ace; 0.67 ± 0.03 emery | quasi-static drag of 4 balls in a box | §VI |
| cross2002hcor | μ_r (rolling) | 0.04 ± 0.005 | tennis balls under a 15 kg platform | §VI |
| cross2002hcor | e_x, spin vs rolling | e_x = 0.24 ± 0.03; spin 41% above rolling (Rω2/vx2 = 1.41) | emery, 25 cm drop onto an inclined platform | Table I / §VII |
| cross2002hcor | e_x range | 0.51 → 0.24 for the tennis ball; 0.76 for the superball | various incidence angles and surfaces | abstract |
| cross2002hcor | video method | 100 fps, 1/500 s exposure; horizontal speed ±2%, spin ±1%, vertical rebound speed ±3% | quadratic fit to ≥10 post-impact frames | §V |
| cross2002grip | e_x when gripping | 0.1–0.2 (tennis); ≈ 0.1 (golf) | low-speed oblique bounces | §IV / Fig. 9 |
| cross2002grip | normal-force offset D | ≈ 2 mm (tennis); < 0.5 mm (superball, golf) | from Table III fits | §IV |
| cross2002grip | e_y | 0.75 ± 0.02 tennis; 0.97 ± 0.03 superball; 0.90 ± 0.02 golf | ~4 m/s on granite (superball, golf) | text |
| cross2002grip | μ | golf on granite 0.18; tennis F/N ≈ 0.27 smooth, 0.7–1.0 emery | sliding-phase averages | text |
| cross2002grip | slide-throughout angle | golf slides throughout up to ≈ 40° incidence (model 39.9°); tennis on smooth surface (μ = 0.27) up to ≈ 35°, on emery (μ ≥ 0.7) only up to ≈ 15° | from horizontal, ω1 = 0 | text |
| cross2002grip | tangential vibration period | 5.2 ms (tennis); impact ≈ 6 ms | ball on a wood block | text |
| nathan2006spin | Cl vs S | Cl ≈ 0.20 (tightly clustered) for S = 0.15–0.30; agrees with SHS Cl = 0.09 + 0.6S for S < 0.3, falls below it for S > 0.5 | baseball, v = 50–110 mph, Re = 1.1–2.4×10⁵ | Fig. 3 |
| nathan2006spin | tracking precision | 10 cameras at 700 fps; single-dot rms 1.3 mm; fit rms 0.4 mm (y), 12.7 mm (z); 100–300 DOF per fit; g recovered to 1.5% | ~5 m of flight | §3 |
| cross2012liftdrag | C_D, C_L | both 1.2 ± 0.1 at 10 m/s | taped plastic cups (cylinder-like), 13.2 g, 5200 ± 100 rpm | text / Fig. 4 |
| cross2012liftdrag | force fits | F_D = 0.007v + 0.0047v² N; F_L = 0.063v − 0.089 N; F_L ∝ v approximately | same | Fig. 4 |
| cross2012liftdrag | spin decay | no significant decrease over the first 6 revs | cups, 300 fps | text |
| cross2012liftdrag | 70 mm plastic ball | "lift effect … less dramatic" (no numbers) | 70 mm, 10 g Christmas ball, hand/elastic launch | text |
| tebbe2020spin | assumed model constants | m = 2.7 g, r = 0.02 m, C_D = 0.4, C_M = 0.6, ρ = 1.29 | table tennis | §IV |
| tebbe2020spin | bounce-point error, fitted spin vs none | backspin low/med/high: 10.3/27.0/43.4 mm vs 36.8/125.8/170.8 mm | 10 trajectories per setting, ball machine | Table III |
| tebbe2020spin | spin-class clustering accuracy | trajectory fit 88.2% vs logo methods 79.6–86.7% | 50 trajectories × 9 settings | Table IV |
| hubbard2005isb | backspin benefit at rim | ≈ +10% successful free throws | basketball rim-contact simulations | abstract |
| hubbard2005isb | contact time | ≈ 11 ms ball–rim | basketball | abstract |
| okubo2004rim | sensitivity | capture "extremely sensitive" to rim contact position and backspin; backspin aids capture on long-rolling paths | model | abstract |
| antali2021rim | no-slip band on rim crest | ±arctan μ = ±45° for μ = 1.0 (small circular-velocity limit) | r = 0.12 m, rim minor radius 0.01 m, j = 2/3 | Eq. 56, Fig. 6, Table 1 |
| haron2012cor | COR on steel (1.3→1.7 m drops) | table tennis 0.809→0.779; hockey (71 mm, 162 g) 0.647→0.628; golf 0.897→0.889; cricket 0.615→0.606 | v ≈ 5.0–5.8 m/s, 250 fps, 3 drops per height | Table 3 |
| haron2012cor | COR on wood | table tennis 0.786→0.743; golf 0.681→0.666; hockey 0.398→0.378; cricket 0.356→0.350 | same | Table 4 |
| haron2012cor | COR drop going steel→wood | TT 4.3%, golf 24.5%, hockey 40.4%, cricket 42.5% | the paper attributes the trend to ball mass | text |

## What this means for POLLEN (derived here; not measured)

These worked examples use a 25 g, R = 35.5 mm shell with α = 2/3. The ball hits a horizontal surface at 5 m/s, 45° from the surface, so v_t = v_n = 3.54 m/s. I take e_y = 0.6 (pickleball-like guess) and e_x = 0.1 for the gripping case.

| μ | ω_b in (rad/s) [S_in] | mode | v_t2 (m/s) | ω after (rad/s; + = backspin) |
|---|---|---|---|---|
| 0.2 | 0 / 70 / 150 / 250 [0 / 0.5 / 1.06 / 1.77] | slide (all) | 2.40 (all) | −48 / +22 / +102 / +202 |
| 0.3 | 0 / 70 / 150 / 250 | grip / slide / slide / slide | 1.98 / 1.84 / 1.84 / 1.84 | −66 / −2 / +78 / +178 |
| 0.5 | 0 / 70 / 150 / 250 | grip / grip / slide / slide | 1.98 / 0.89 / 0.71 / 0.71 | −66 / −42 / +31 / +131 |
| 0.8 | 0 / 70 / 150 / 250 | grip / grip / grip / slide | 1.98 / 0.89 / −0.36 / −0.99 | −66 / −42 / −15 / +59 |

What follows from the table:
- Backspin changes a lip or floor rebound **only as much as μ allows**. On a slippery PE-on-plastic contact (μ ≲ 0.3), spin beyond S ≈ 0.5 adds nothing to v_t2. A "check-back" (reversal) needs μ ≳ 0.6 at 45°, or large spin while the ball grips. **μ for POLLEN on the actual HIVE surface is the controlling unknown** and must be measured.
- At a CELL lip the local normal points from the edge to the ball centre. The same relations apply in that rotated frame. For edge contacts the incidence angle to the local normal changes quickly with offset, which makes the outcome very sensitive to where the ball hits (cf. okubo2004rim, antali2021rim).
- Hubbard and Okubo's "backspin aids capture" comes from energy scrubbing during friction at the rim. Hypothesis (B) in the HANDOFF is the same mechanism. Its size depends on μ and contact duration, and the basketball result (~+10%) does not transfer quantitatively.
- Aero vs impact scale. At 5 m/s with Cl = 0.2, the Magnus acceleration is 0.49 m/s². The tangential velocity change in a single contact can be 1–2 m/s. So in a contact-assisted entry, the impact usually dominates the spin's effect on the path, provided μ is not tiny.

## Model implications for PM-001

1. **Contact model (src)**: implement a 2D rigid-shell impulse model.
   - Inputs: e_y(v_n), μ, e_x, α, and an optional offset D.
   - Logic: check the sliding test (Eq. 3); otherwise use the grip/e_x branch (Eq. 4). Apply it in the local normal frame for wall, floor and lip-edge contacts, with the edge treated as a cylinder of radius r_lip.
   - Defaults: α = 2/3 until measured. e_x ∈ [0, 0.2] (cross2002grip). μ swept over 0.15–0.8. e_y swept over 0.5–0.8, from a POLLEN drop test.
   - Repeated contacts are needed: a ball in a 305 mm-deep CELL can hit two or more surfaces.
   - Report outcomes as probabilities over the μ and e sweeps, not as single trajectories (okubo2004rim sensitivity).
2. **Retention criterion**: count a ball as scored when it ends inside the CELL volume after all contacts (rebound energy decays). Do not count first-contact direction. Track spin through every contact, because backspin flips to topspin after a gripping bounce (see the table).
3. **Passive roller / hood (launcher)**: cross2010tang's spring-cart model is a usable lumped template for a compliant hood or a light passive roller. Static friction returns stored tangential energy, so spin can **exceed** the rolling value. Calibrate this; it is not a design claim.
4. **Measurement and identification (tests)**:
   - (a) Drop test on the actual HIVE material to get e_y(v). Use ≥3 drops per height; Haron's protocol is adequate.
   - (b) Oblique bounce at 100–240 fps with a diametral line drawn on POLLEN (Cross method) to get μ (from sliding bounces at glancing angles, Eq. 2), e_x (from gripping bounces) and ω_out.
   - (c) Quasi-static μ: drag a box of POLLEN over the HIVE material (cross2002hcor).
   - (d) Flight identification: fit each trajectory with a Nathan- or Tebbe-style model holding Cd and Cl constant per shot. Get ω either from the marker phase (Nathan Eq. 8) or by least squares on the Magnus residual (Tebbe Eq. 9).
   - Expected precision at 240 fps over 0.5 s with σ_pos = 2 mm: σ_a ≈ 0.02 m/s². That is about 4% of the 0.49 m/s² Magnus acceleration, so Cl is resolvable to about ±0.01 per shot. Halving the window to 0.25 s gives σ_a ≈ 0.11 m/s². Fit over the longest visible arc.
   - Fitting caveats: drag on POLLEN is about 2.5× the Magnus term (Cd ≈ 0.5 vs Cl ≈ 0.2), so Cd is also identifiable, unlike in the baseball case. Low spin is the weak case, because the Magnus deviation becomes comparable to tracking noise (SpinDOE critique of Tebbe-style fitting; secondary).
5. **Perforation and asymmetry**: Tebbe found no single C_M that worked across spin types when the spin was measured independently. Expect POLLEN Cl to need its own per-spin calibration; do not borrow pickleball coefficients.

## Caveats

- Every measured impact datum here is for a tennis ball, superball, golf ball, baseball or basketball. There is none for a perforated PE ball. Holes and a thin wall will change the contact patch (Cross's buckled annulus for hollow balls), μ, e_x and the vibration-frequency ratio.
- Basketball rim results (okubo2004rim, antali2021rim, hubbard2005isb) are for a 0.6 kg compliant ball on a thin steel torus. They are qualitative support for spin-assisted capture only.
- Haron's table columns are misaligned in the PDF text layer. I matched rows using the paper's stated ordering (on steel golf > TT > hockey > cricket; on wood TT highest) and its quoted percentage drops.
- Every number in the "What this means for POLLEN" section is *derived here* from the textbook impulse relations with assumed μ and e. It is an illustration, not evidence.
