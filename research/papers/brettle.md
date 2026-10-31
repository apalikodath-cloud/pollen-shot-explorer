# Brettle — Flywheel Shooter Analysis (deep read for PM-001)

source_id: `brettle`

## Citation
Dean Brettle (Mentor, Carlmont Robotics, FRC Team 199 "Deep Blue"), *Flywheel Shooter Analysis*, Jupyter notebook / web page.
- Web page (read): https://docs.carlmontrobotics.org/jupyter_notebooks/files/FlywheelShooter.html
- Mirror: https://deepbluerobotics.github.io/jupyter_notebooks/files/FlywheelShooter.html
- Source notebook (read, incl. SymPy code): https://github.com/DeepBlueRobotics/jupyter_notebooks/blob/master/FlywheelShooter.ipynb
- Dates: GitHub commit history for the notebook runs from 2023-06-12 to 2023-07-19 (84 commits touching the file; last message "Improved explanation of why rolling is good.").
- Acknowledged reviewer: David Giandomenico (FRC Team 846), informal draft review.

## Access level
Full text. The web page and the source `.ipynb` were downloaded on 2026-10-30. All equations below were taken from the rendered LaTeX in the page and checked against the SymPy source cells.

## Review status
Unreviewed web article (a FIRST Robotics mentor's technical note). It was not peer reviewed; one person from another team gave informal feedback. It contains **no experimental data**. It is a closed-form analytical (impulse-momentum) model only, and every number in it is symbolic or a textbook shape factor. A separate 2026 Chief Delphi post by Pedersen ("Flywheel shot analysis: correction and extension") responds to this line of work. This file does not cover it.

## Method
Rigid-body impulse–momentum analysis of **one powered flywheel + a fixed (stationary) hood**, with the projectile entering at rest:
- The wheel (radius r_w, inertia I_w) starts at ω_wi. The projectile (r_p, m_p, I_p) starts with v = 0 and ω = 0.
- While the projectile is in the shooter, the wheel gives it a tangential impulse J_w (and receives an equal and opposite one). The hood gives an impulse J_h on the opposite side of the ball, defined as positive *opposite* to J_w.
- At exit the ball **rolls without slipping on both the wheel and the hood**. This closes the system: 5 equations, 5 unknowns (ω_wi, ω_wf, ω_p, J_w, J_h). The system is solved symbolically in SymPy.
- The model does not resolve anything about the contact process itself: no normal force, friction coefficient, contact time, contact path or compression. Only the exit state is constrained.
- An energy-efficiency expression is then derived, and the wheel-speed-drop result is compared with the widely used FRC 846 (2012) analysis.

## Assumptions (as stated in the source, paraphrased)
1. At exit the projectile rolls, not slips, against the hood.
2. At exit the projectile rolls, not slips, against the wheel (equal surface speeds).
3. No other forces or torques act on the projectile or the wheel. In particular, the motor does **not** add energy while the ball is in contact: the dwell time is assumed too short for the speed control loop to respond.
4. The shooter is mounted to a very massive, stiff structure, so the axle and hood do not move (no recoil or "kick").
5. The projectile, wheel and hood are rigid bodies, so the projectile is **not compressed**.
Units: SI throughout. Angular velocities are in rad/s, not RPM.

## Equations (verbatim from the source, with symbol definitions)
Symbols: r_w is the wheel radius [m]. r_p is the projectile radius [m]. m_p and m_w are the projectile and wheel masses [kg]. I_p and I_w are the projectile and wheel moments of inertia about their own axes [kg m²]. v_p is the projectile exit speed [m/s]. ω_wi and ω_wf are the wheel angular speeds before and after the shot [rad/s]. ω_p is the projectile exit spin [rad/s]. J_w is the tangential impulse magnitude at the wheel contact [N s]. J_h is the tangential impulse magnitude at the hood contact [N s], positive opposite to J_w. k_p and k_w are dimensionless shape factors (I = k m r²). E is kinetic energy [J]. η is mechanical efficiency [-].

Momentum balances:
- (Eq. 1, projectile linear momentum) `m_p v_p = J_w − J_h`
- (Eq. 2, projectile angular momentum) `I_p ω_p = J_h r_p + J_w r_p`
- (Eq. 3, wheel angular momentum) `I_w ω_wi − I_w ω_wf = J_w r_w`

Exit kinematic (rolling) constraints:
- (Eq. 4, rolling on hood and wheel: ball centre moves at half the wheel surface speed) `v_p = ω_wf r_w / 2`
- (Eq. 5, rolling on the stationary hood) `v_p = ω_p r_p`

Solutions:
- Final wheel speed: `ω_wf = 2 v_p / r_w`
- Projectile spin: `ω_p = v_p / r_p`. This gives spin parameter **S = ω_p r_p / v_p = 1 exactly**, independent of all inertias.
- Wheel impulse: `J_w = v_p (I_p + m_p r_p²) / (2 r_p²)`
- Initial wheel speed: `ω_wi = v_p (I_p r_w² + 4 I_w r_p² + m_p r_p² r_w²) / (2 I_w r_p² r_w)`
- Wheel velocity ratio: `ω_wi/ω_wf = 1 + (m_p + I_p/r_p²) · r_w²/(4 I_w)`
- Shape factors: `I_p = k_p m_p r_p²`, `I_w = k_w m_w r_w²`
- `ω_wi = (1 + (1+k_p)/(4 k_w) · m_p/m_w) · 2 v_p / r_w`
- `ω_wi/ω_wf = 1 + (1+k_p)/(4 k_w) · m_p/m_w`
- Solid cylinder wheel (k_w = 1/2) with a solid sphere ball (k_p = 2/5): `ω_wi = (1 + (7/10) m_p/m_w) · 2 v_p/r_w` and `ω_wi/ω_wf = 1 + (7/10) m_p/m_w`

Comparison with prior work (FRC 846, 2012 white paper, as restated by Brettle):
- `ω_wi/ω_wf = 1 + (1+k_p)/(2 k_w) · m_p/m_w`. The denominator has 2 where Brettle has 4. Brettle's model therefore predicts **half** the wheel-speed loss (ω_wi − ω_wf). Brettle says 846's derivation is invalid because it converts angular momentum to linear momentum by dividing by radius.

Energy and efficiency:
- `E_p = m_p v_p²/2 + I_p ω_p²/2`, `E_wi = I_w ω_wi²/2`, `E_wf = I_w ω_wf²/2`
- `η = E_p / (E_wi − E_wf)`, which simplifies to `η = ω_wf / (ω_wf + ω_wi)`
- `1/η = 1 + ω_wi/ω_wf = 2 + (1+k_p)/(4 k_w) · m_p/m_w`
- `η = (2 + (1+k_p)/(4 k_w) · m_p/m_w)^(−1)`, **so η < 50% always** (the wheel must slow down). The remaining energy is lost to sliding friction before rolling is reached.

Derived here, not stated by Brettle (follows directly from Eqs. 1, 2 and 5):
- `J_h = J_w − m_p v_p = (m_p v_p/2)(k_p − 1)`. For any k_p < 1, J_h is **negative**: hood friction acts *forward* on the ball, increasing v and reducing ω until rolling is reached. The wheel alone would over-spin the ball (ω r_p/v = 1/k_p > 1). The hood's job in this model is to trade excess spin for speed. With a hollow-shell ball (k_p = 2/3), the hood must supply |J_h| = m_p v_p/6. With k_p = 1 it supplies nothing.
- The model gives no normal-force or friction-coefficient condition. The minimum μ or hood pressure needed to *reach* rolling before exit is not covered (see "Discussion" limitation 1).

## Stated limitations / Discussion section (paraphrased)
1. **Slipping at exit.** If the ball is still slipping at exit, exit speed is set by friction forces, which "do not depend on the speed of the wheel". v_p then cannot be controlled by ω_wi and varies with ball-to-ball friction and wear. Recommendation: design so the ball rolls on exit even in the worst-case friction.
2. **In-shot speed compensation.** If the motor can restore wheel speed during contact, the model overestimates the speed loss. Partial or variable compensation causes variation in ω_wf and hence v_p. A suggested mitigation is to coast the wheel (coast mode, setpoint 0) during the shot.
3. **Shooter recoil ("kick").** v_p is relative to the shooter. A shooter that is not rigidly mounted lowers ground-relative speed, so it needs a higher ω_wi. Compensate empirically or stiffen the mount.
4. **Compression.** (a) Compression raises the effective k_p toward a hollow cylinder (k_p = 1, "the highest possible"), which raises the velocity ratio. (b) Work spent compressing the ball is not fully returned (hysteresis, slow rebound). Both effects slow the wheel more than the model predicts, so a higher ω_wi is needed. Variation in compression, for example from ball size or shape variation, shows up directly as exit-speed variation. Less compression helps, but it needs a longer contact path (a larger shooter) to still reach rolling. If compression cannot be made consistent, "mechanisms other than a flywheel shooter might be more appropriate."
5. Future work listed, not done: a second wheel on the hood side, a non-zero initial ball velocity or spin, a geared separate flywheel, and design trade-offs (weight, size, spin-up and recovery time).

## Numeric data points
The source contains **no measured data**. Its only numbers are textbook shape factors and the 2 vs 4 coefficient. Rows marked "derived for POLLEN" are this agent's evaluations of Brettle's equations, not values from the source.

| # | Quantity | Value | Conditions | Where in source |
|---|---|---|---|---|
| 1 | Shape factor, solid cylinder wheel | k_w = 1/2 | textbook | "Moment of inertia" paragraph and the cylinder/sphere special case |
| 2 | Shape factor, solid sphere ball | k_p = 2/5 | textbook | same |
| 3 | Shape factor, hollow cylinder (upper bound for a compressed ball) | k_p = 1 | textbook; "highest possible k_p" | Discussion, compression paragraph |
| 4 | Combined factor (1+k_p)/(4k_w) | 7/10 | k_w = 1/2, k_p = 2/5 | "Initial wheel rotational velocity with cylindrical wheel and spherical ball" |
| 5 | Exit spin parameter | S = 1 | rolling on a fixed hood | Eq. 5 / "Projectile rotational velocity" |
| 6 | Exit speed as a fraction of the final wheel surface speed | 1/2 | rolling at both contacts | Eq. 4 |
| 7 | Speed-loss coefficient denominator: Brettle vs FRC 846 | 4 vs 2 (Brettle predicts half the loss) | rigid, no compensation | "Comparison with earlier work" |
| 8 | Efficiency upper bound | η < 0.5 | any parameters | "Efficiency" |
| 9 | Derived for POLLEN: ω_wf, ω_p for v_p = 2, 4, 5, 6, 7, 8, 10 m/s | ω_wf = 82, 163, 204, 245, 286, 327, 408 rad/s (780, 1559, 1949, 2339, 2728, 3118, 3898 RPM). ω_p = 56, 113, 141, 169, 197, 225, 282 rad/s (538, 1076, 1345, 1614, 1883, 2152, 2690 RPM) | r_w = 0.049 m, r_p = 0.0355 m, rigid, rolling at exit | this file (Eqs. 4, 5) |
| 10 | Derived for POLLEN: velocity ratio ω_wi/ω_wf (wheel speed drop %, η) | k_p = 2/3: m_w = 0.05 kg gives 1.417 (29.4%, 0.414); 0.1 kg gives 1.208 (17.2%, 0.453); 0.2 kg gives 1.104 (9.4%, 0.475); 0.4 kg gives 1.052 (4.9%, 0.487) | m_p = 0.025 kg, k_w = 1/2 (solid-disc wheel, no reflected motor or gearbox inertia) | this file |
| 11 | Derived for POLLEN: same, k_p = 2/5 and k_p = 1 | k_p = 0.4: 1.350 / 1.175 / 1.088 / 1.044. k_p = 1: 1.500 / 1.250 / 1.125 / 1.063 (for m_w = 0.05 / 0.1 / 0.2 / 0.4 kg) | as above | this file |
| 12 | Derived for POLLEN: ratio from total wheel-side inertia I_w | I_w = 5e-5, 1e-4, 2e-4, 5e-4, 1e-3 kg m² gives 1.500, 1.250, 1.125, 1.050, 1.025 (drop 33, 20, 11, 4.8, 2.4%) | k_p = 2/3, r_w = 0.049 m | this file |
| 13 | Derived for POLLEN: impulses and ball KE at v_p = 5 m/s | k_p = 2/3: J_w = 0.104 N s, J_h = −0.021 N s (forward), E_p = 0.52 J (E_rot/E_trans = k_p). k_p = 2/5: J_w = 0.0875, J_h = −0.0375, E_p = 0.44 J | m_p = 0.025 kg, r_p = 0.0355 m | this file |
| 14 | FRC 846 ratio for comparison | k_p = 2/3, m_w = 0.1 kg gives 1.417 (vs Brettle 1.208) | k_w = 1/2 | this file, using the 846 formula as restated in the source |

## Applicability to POLLEN
What transfers:
- The **kinematic exit relations (Eqs. 4, 5)** are pure rolling geometry and do not depend on the ball's material. If the 71 mm POLLEN really rolls without slip on both the 98 mm wheel and a fixed hood at exit, then v ≈ ω_wf r_w/2 and **S ≈ 1** follow from the geometry. This matches HANDOFF §4C. In Brettle's geometry the wheel is under the ball and the hood above it, which gives **backspin** (the bottom surface moves forward relative to the centre). That is the sign PM-001 needs.
- The **wheel-speed-drop and efficiency structure** transfers as a first-order bound. POLLEN is light (25 g) relative to a typical FTC wheel stack, so the predicted drop is modest when the wheel-side inertia is ≥ about 2e-4 kg m² (≤ about 11%). With a light single wheel and no added flywheel mass it can reach 20–30%. That matters for shot-to-shot repeatability.
- The **conceptual limitations** apply strongly to POLLEN. They concern slip at exit, compression hysteresis (the 4 mm nominal), size and shape variation, and recoil on an FTC drivetrain.

What does not transfer, and why:
- **Rigid, uncompressed ball (assumption 5).** POLLEN is a soft, perforated polyethylene shell squeezed about 4 mm. Brettle himself says compression raises the effective k_p and adds hysteretic wheel slowdown. Neither is quantified.
- **k_p for POLLEN is unknown.** A thin hollow shell gives k_p = 2/3. Perforations remove mass, plausibly from all over the shell, so k_p stays near 2/3 but depends on the hole pattern. Brettle's worked example uses 2/5 (solid sphere), which is wrong for POLLEN. Measure it (bifilar or trifilar pendulum, or roll-down-incline timing).
- **No friction model.** Whether POLLEN actually reaches rolling before exit depends on μ (wheel tread on PE, hood material on PE), normal load from compression, and contact-path length. None of these are in the model. If POLLEN is still slipping at exit, S ≠ 1 and v is not set by RPM (Brettle's limitation 1). On a slippery hood S can be **> 1**: the wheel alone tends to give ω r_p/v = 1/k_p ≈ 1.5 for a hollow shell, and the forward hood friction is what brings it back down to 1. So a low-friction hood could *raise* backspin above S = 1 at the cost of exit speed. **This is a potentially useful lever for PM-001, but it is my inference from the equations, not a claim in the source.**
- **Fixed hood only.** A passive upper roller (HANDOFF §4D) is listed only as future work ("a second shooter wheel on the hood"). Rolling on a free roller with roller surface speed u_r changes Eq. 5 to v − ω r_p = u_r (sign as appropriate). With a forward-moving roller surface, **S < 1**, so a passive roller tends to *reduce* backspin compared with a fixed hood. This also needs its own derivation, with roller inertia and bearing drag.
- **Single-wheel inertia only.** In FTC, the motor rotor and gearbox reflected inertia (I_motor·G²) and any added flywheel mass belong in I_w. The m_w and k_w form hides this, so use the I_w form.
- **No exit angle, contact path or hood curvature.** The model is a lumped exit-state model. It does not give exit direction.

## Implications for the PM-001 models
1. **Launcher model, baseline (ideal):** implement Brettle's closed form as the "ideal rolling, rigid" launcher. Use v = ω_wf r_w/2, ω = v/r_b (S = 1, backspin), ω_wi from the I_w form with I_w = I_wheel + I_hub + G²I_rotor, ω_wf/ω_wi from the ratio, and η from the formula. Report the ideal-case RPM map: v = 2–10 m/s needs **ω_wf ≈ 780–3900 RPM** at the wheel and gives **ω_ball ≈ 540–2690 RPM**. ω_wi is higher by the ratio (≈ 1.05–1.4 depending on wheel-side inertia).
2. **Do not treat S = 1 as a measurement.** It is an output of the rolling assumption. Bracket it in the trajectory sweeps, e.g. S ∈ [0.6, 1.5]. Add a slip-regime model that integrates Coulomb friction at both contacts along the contact path, with a compression-dependent normal load N(δ). It should report whether rolling is reached before exit. The slip model must reduce to Brettle when rolling is reached.
3. **Hood-friction lever:** the derived J_h < 0 result means hood friction *removes* spin. Include hood μ as a design variable. A low-μ hood (e.g. PTFE or UHMW strip) may raise exit S toward 1/k_p ≈ 1.5 but lowers v and makes v depend on friction (repeatability risk). Test it on a prototype rather than assuming it.
4. **Passive roller:** derive a separate model (Eq. 5 replaced by a rolling-on-moving-surface condition, plus the roller's angular momentum balance with bearing drag). The kinematic expectation is S < 1 for a roller that spins up, so a fixed hood is the default backspin-maximising choice under the rolling assumption.
5. **Compression correction:** follow Brettle's guidance and use k_p,eff ∈ [2/3, 1] plus a hysteresis energy loss term. Calibrate the RPM→(v, ω) map empirically (high-speed video of ball centre and a marked stripe). Expect real ω_wi above the rigid prediction for a given v.
6. **Repeatability budget:** wheel speed drop percent sets the minimum shot interval and recovery requirements. Add I_w as a sweep variable. Increase it, with a flywheel mass or gearing, if the drop is over about 10%.
7. **Energy bound for sizing:** E_wheel needed ≥ E_ball/η, with η < 0.5. For POLLEN at 5 m/s, E_ball ≈ 0.52 J (k_p = 2/3), so ≥ about 1.1 J must come from the wheel's stored energy per shot. That is small for FTC motors. Speed, not energy, is the constraint.

## Caveats
- Unreviewed analytical note with no experimental validation. The key S = 1 and v = u_wheel/2 results are assumption-driven (HANDOFF §5 already warns not to treat v = u/2 as universal).
- The FRC 846 comparison was not independently checked against the 846 white paper. It is as restated by Brettle.
- All POLLEN numbers above were computed by this agent from Brettle's equations, using HANDOFF nominal values (m = 0.025 kg, r_b = 0.0355 m, r_w = 0.049 m) and assumed k_p and wheel mass/inertia. None are measurements.
- Wheel mass and inertia for the actual 98 mm wheel are unknown, so the speed-drop numbers are a sweep, not a prediction.
