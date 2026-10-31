# Fact-check: Brettle, "Flywheel Shooter Analysis" (extraction id `brettle`)

Checker: independent re-read on 2026-10-30. Sources the checker re-opened:
- https://docs.carlmontrobotics.org/jupyter_notebooks/files/FlywheelShooter.html. This is the rendered page; all 26 displayed equations were extracted from its HTML.
- https://raw.githubusercontent.com/DeepBlueRobotics/jupyter_notebooks/master/FlywheelShooter.ipynb. These are the source cells; the content is identical.
- https://api.github.com/repos/DeepBlueRobotics/jupyter_notebooks/commits?path=FlywheelShooter.ipynb. 28 commits from 2023-06-12 to 2023-07-19, all by Dean Brettle.

The extraction under check is research/papers/brettle.md.

## Verdict
The extraction is accurate. Every source equation and every data point stated in the source matches the page verbatim. The derived POLLEN numbers are arithmetically correct (the checker recomputed them by hand). The problems are minor wording and attribution issues, and some useful source content was missed.

CHECK: 11 confirmed / 1 corrected / 0 dropped / 10 added

## Equations (all confirmed against the rendered page)
| Extracted | Source label | Status |
|---|---|---|
| m_p v_p = J_w - J_h | Equation 1 | confirmed |
| I_p w_p = (J_h + J_w) r_p | Equation 2 | confirmed |
| I_w (w_wi - w_wf) = J_w r_w | Equation 3 | confirmed |
| v_p = w_wf r_w / 2 | Equation 4. It assumes rolling on the hood AND on the wheel at exit. | confirmed |
| v_p = w_p r_p | Equation 5 | confirmed. "S = 1" is a valid re-expression, but the source never uses S. |
| w_wf = 2 v_p / r_w | Final wheel rotational velocity | confirmed |
| J_w = v_p (I_p + m_p r_p^2) / (2 r_p^2) | Impulse from the wheel | confirmed |
| w_wi = v_p (I_p r_w^2 + 4 I_w r_p^2 + m_p r_p^2 r_w^2) / (2 I_w r_p^2 r_w) | Initial wheel rotational velocity | confirmed |
| w_wi/w_wf = 1 + (m_p + I_p/r_p^2) r_w^2 / (4 I_w) | Wheel velocity ratio | confirmed |
| w_wi/w_wf = 1 + (1+k_p)/(4 k_w) * m_p/m_w ; w_wi = (same) * 2 v_p / r_w | ... with shape factors | confirmed |
| 1 + (7/10) m_p/m_w | cylindrical wheel and spherical ball | confirmed |
| 846: 1 + (1+k_p)/(2 k_w) * m_p/m_w | Wheel velocity ratio from Team 846's analysis | confirmed as restated by Brettle. The 846 PDF itself was not checked. |
| E_p = I_p w_p^2/2 + m_p v_p^2/2 ; eta = E_p/(E_wi - E_wf) = w_wf/(w_wf + w_wi) | Projectile Energy / Efficiency | confirmed. The source also shows 1/eta = 1 + w_wi/w_wf. |
| eta = (2 + (1+k_p)/(4 k_w) * m_p/m_w)^-1 | Efficiency in terms of shape factors | confirmed |
| J_h = (m_p v_p / 2)(k_p - 1) | not in the source | Correctly labelled "derived". Verified by hand from Eqs 1, 2 and 5. The extractor missed a source inconsistency: the SymPy code declares J_h `positive=True`, but the solution is negative for k_p < 1. The source never prints J_h, so it does not notice that the hood impulse actually points forward and removes excess spin. |

## Data points
**Confirmed (stated in the source):**
- k_w = 1/2 for a solid cylinder and k_p = 2/5 for a solid sphere (shape-factor paragraph).
- k_p = 1 for a hollow cylinder, "the highest possible k_p" (Discussion, compression paragraph).
- The coefficient 7/10.
- v_p / (w_wf r_w) = 1/2.
- w_p r_p / v_p = 1.
- Denominator 4 vs 2, i.e. "half as much wheel speed loss" as Team 846.
- eta < 50% (Efficiency section and Abstract).

**Corrected:**
- The k_p = 2/5 item is a symbolic special case ("Assuming a solid cylindrical shooter wheel ... and a solid spherical projectile gives:"), not a numeric worked example. The source contains no numeric example at all.

**Derived (the extracting agent's arithmetic, not source data).** The checker recomputed all of these and found them correct. They are kept, labelled as derived:
- Spin and speed map at r_w = 0.049 m and r_b = 0.0355 m: v = 2, 5, 10 m/s gives w_wf = 780, 1949, 3898 RPM and w_b = 538, 1345, 2690 RPM.
- Wheel mass sweep with k_p = 2/3, k_w = 1/2, m_p = 0.025 kg: m_w = 0.05, 0.1, 0.2, 0.4 kg gives ratio = 1.417, 1.208, 1.104, 1.052 and eta = 0.414, 0.453, 0.475, 0.487.
- Wheel inertia sweep: I_w from 5e-5 to 1e-3 kg m^2 gives ratio from 1.500 to 1.025.
- Impulses and energy at 5 m/s:
  - k_p = 2/3: J_w = 0.104 N s, J_h = -0.021 N s, E_p = 0.52 J.
  - k_p = 2/5: J_w = 0.0875 N s, J_h = -0.0375 N s, E_p = 0.44 J.

**Added (missed by the extractor):**
1. Units: the source states that all rotational velocities are in rad/s, not RPM (Preface). Every RPM figure is therefore a conversion.
2. The five assumptions:
   - The projectile enters with zero linear and zero angular velocity.
   - At exit it rolls without slipping on both the hood and the wheel.
   - No other forces or torques act, and the motor does not compensate during the shot.
   - The axle and hood are fixed.
   - All bodies are rigid, so there is no compression.
3. w_wi equals v_p times a constant that depends only on the physical properties of the wheel and ball, so the model is linear in v (text after the initial-wheel-velocity equation).
4. Slip at exit (Discussion paragraph 1): v_p is then set by friction and "can not be varied by changing w_wi", and it varies with wear and manufacturing. The source recommends designing for rolling at exit under worst-case friction.
5. In-shot speed compensation (Discussion paragraph 2): it needs a low-latency control loop and enough power. Partial compensation adds variation, and the source suggests putting the motor in "coast" mode during the shot.
6. Recoil (Discussion paragraph 3): the "kick" of a light shooter reduces the exit speed in the ground frame, so a higher wheel velocity ratio is needed.
7. Compression (Discussion paragraph 4):
   - It raises k_p toward 1.
   - Some friction work goes into deformation, and imperfect or slow spring-back means the wheel slows more than the model predicts.
   - Variability in compression changes the exit velocity.
   - Less compression needs a longer contact time, which means a physically larger shooter.
   - "Mechanisms other than a flywheel shooter might be more appropriate" if compression cannot be made consistent.
8. Future work listed by the source: (1) a second shooter wheel on the hood; (2) a nonzero initial linear or rotational projectile velocity; (3) a separate flywheel geared to the shooter wheel.
9. Critique of Team 846: their analysis divides angular momentum by radius to treat it as linear momentum, which is valid only for a point mass moving in a circle. The Chief Delphi flywheel spreadsheet and the reca.lc/flywheel calculator are both based on 846, so by Brettle's analysis they overpredict the wheel speed drop by 2x.
10. Figures and acknowledgement: the figures draw the hood as a 45-degree arc concentric with the wheel at radius r_w + 2 r_p, which is a zero-compression gap. The ball enters at theta = 0 and exits at theta = pi/4. The figures are illustrative only, with no dimensions. The source acknowledges a draft review by D. Giandomenico of FRC 846.

## Text-level corrections to the extraction
- **Passive roller.** The applicability text says "a passive roller is future work in the source". The source actually lists "a second shooter wheel on the hood" and does not say whether it is powered or passive. "A passive roller gives S < 1" is the extractor's own kinematic inference. It is plausible, because a hood-side surface that moves forward lowers the spin needed for no-slip, but it is unverified.
- **Shell shape factor.** "Hollow shell k ~ 2/3" is the thin-shell limit. A real PE shell with finite wall thickness has 2/5 < k < 2/3, and the perforations shift it further. Treat 2/3 as an upper-bound guess until I_b is measured, for example with a bifilar or trifilar pendulum.
- **Compression value.** "Squeezed about 4 mm" is a candidate value from HANDOFF, not a measurement (see the ball compression row in HANDOFF).
- **Energy bound.** Implication 7 says "needs at least about 1.1 J". The strict bound from eta < 0.5 is at least 1.04 J; about 1.1 J corresponds to eta of roughly 0.45-0.48. This is minor false precision.
- **Rolling radius.** With compression, the rolling radius at the contacts is smaller than the nominal r_p. Eq 5 with the nominal R therefore does not give exactly S = 1. This should be added to the caveats.
- **Spin direction.** The backspin sign is correct: with the wheel below and a fixed hood above, the wheel-side surface moves at 2v and the hood-side surface at 0, which is backspin. It is the extractor's inference, though. The source never names the spin direction, and the direction arrows in its figure are ambiguous.
- **Review status and date.** Confirmed as an unreviewed web technical note with one informal reviewer acknowledged, no data, and no peer review. The page itself is undated; 2023 comes from the commit history, which was verified. A mirror exists at deepbluerobotics.github.io/jupyter_notebooks/files/FlywheelShooter.html.
