# Sakai, Oda and co-authors (2006): three-roller pitching machine, FE launch, CFD flight

source_ids:
- `sakai_oda_kitagawa2006` (RESEARCH_PAPERS #22). An FE launch study plus a CFD flight-force study plus a throwing test.
- `sakai_oda_kawata2006` (RESEARCH_PAPERS #23). A 2-page companion that uses the same FE model and compares it with high-speed video.

Read: 2026-10-30, research agent for PM-001. Both papers are in Japanese with English titles and abstracts. Both full texts were read from J-STAGE.

Labels used below:
- **text value**: the number is printed in the paper text or a table.
- **figure reading**: read by eye from a plot. Approximate, about ±5% of full scale.
- **CALC**: derived here from the paper's own inputs. It is not a claim the paper makes.

## 1. Citation, access, review status

| Field | #22 `sakai_oda_kitagawa2006` | #23 `sakai_oda_kawata2006` |
|---|---|---|
| Citation | Sakai, Oda, Kitagawa, "A23 ローラ式ピッチングマシンにおけるボール縫い目の影響 / An Effect of a Baseball having Seam under Roller type Pitching Machine", *Proc. JSME Joint Symposium 2006: Sports Engineering / Human Dynamics* (No.06-35), Kanazawa, 9–11 Nov 2006, pp. 120–124. DOI 10.1299/jsmesports.2006.0_120 | Sakai, Oda, Kawata, "3829 ピッチングマシンの投球シミュレーションとその精度評価 / Throw Simulation of a Pitching Machine and the Accuracy Evaluation", *Proc. JSME Annual Meeting 2006* vol. 7 (No.06-1), Kumamoto, 18–22 Sep 2006, pp. 125–126. DOI 10.1299/jsmemecjo.2006.7.0_125 |
| Dates | Published 2006-11-08; on J-STAGE 2017-08-01 | Published 2006-09-15 |
| Affiliation | Kanazawa University | Kanazawa University and PFU Ltd. |
| Review status | **Conference proceedings (JSME symposium). Not journal peer review.** Treat as an unreviewed technical source with academic authorship. | Same: **conference proceedings**, 2-page extended abstract. |
| Method type | FE launch simulation (viscoelastic ball, rubber rollers), CFD (ANSYS CFX) of the flying ball, and a throwing-accuracy test with a real machine | The same FE launch simulation, compared **visually** with high-speed video frames |
| Access | **Full text read** (5 pp. PDF). J-STAGE marks it `citation_fulltext_world_readable`. | **Full text read** (2 pp. PDF). Same J-STAGE marking. |

URLs tried (all returned HTTP 200):
- https://doi.org/10.1299/jsmesports.2006.0_120, which redirects to https://www.jstage.jst.go.jp/article/jsmesports/2006/0/2006_120/_article/-char/ja/
- https://www.jstage.jst.go.jp/article/jsmesports/2006/0/2006_120/_pdf (1.54 MB)
- https://doi.org/10.1299/jsmemecjo.2006.7.0_125, which redirects to https://www.jstage.jst.go.jp/article/jsmemecjo/2006.7/0/2006.7_125/_article/-char/ja/
- https://www.jstage.jst.go.jp/article/jsmemecjo/2006.7/0/2006.7_125/_pdf (414 KB)

Downloads were saved to a fresh folder under %TEMP% and read as text and images only. Nothing downloaded was executed.

**Correction to RESEARCH_PAPERS.md.** It describes #23 as "validated by high-speed camera measurement of exit velocity and spin". That is overstated:
- #23 places FE frames next to video frames, both at 3 ms per frame, and says the velocity and spin behaviour "agree well".
- It prints **no measured exit speed, no measured spin and no error metric**.
- The validation is qualitative only.

## 2. What the papers report

**#22 (`sakai_oda_kitagawa2006`)**
1. **Machine.** A 3-roller pitching machine:
   - Rubber rollers sit at 120° to each other. Each has its own motor under neural-network control.
   - Throw type comes from different roller speeds.
   - The aim is to reproduce many pitch types.
2. **Question.** Does the seam of a hard baseball change launch speed, spin, launch angle, flight forces and accuracy? Cases are no seam, 2-seam and 4-seam.
3. **Throwing test (observation by the authors).** At 1700/1400/1400 min⁻¹, 10 balls each were thrown in 2-seam, 4-seam and random orientation at a target 16.5 m away. 4-seam and random orientation scattered more, mostly left–right. 2-seam was the most accurate.
4. **FE conclusion.** Exit speed and spin are barely affected by seam or posture. The **vertical launch angle is** affected.
5. **CFD conclusion.** Drag is barely affected by seam orientation. Lift rises with spin and is slightly larger for 4-seam.
6. **Overall conclusion.** Launch-angle scatter from ball posture dominates throwing accuracy, more than in-flight force differences. The authors recommend feeding balls in 2-seam orientation.

**#23 (`sakai_oda_kawata2006`)**
1. The same FE model, materials, roller-speed cases and launch results as #22. Its Figs 5–7 are the same data as #22 Figs 8–10.
2. FE frames vs high-speed video for Case 2 with a no-seam model. The text says they "agree well", with no numbers.
3. There is no CFD and no target test. The "accuracy evaluation" in the title is this visual check plus the seam-posture launch-angle result.

## 3. Method

**FE launch (both papers, LS-DYNA class explicit FE).**
- Rollers:
  - Rubber tire, 320 mm OD, 20 mm wall.
  - Mounted on a 280 mm OD aluminium flange, modelled as rigid.
- Ball:
  - 72 mm diameter baseball.
  - Viscoelastic solid, 19,200 elements.
  - Seam modelled in the seam cases.
- Inputs:
  - The ball enters at V0 = 0.03 m/s, essentially fed at rest.
  - Ball–rubber Coulomb μ = 0.5.
  - The analysis runs for 0.1 s.
- Exit speed, spin and launch angle are read from the ball's motion after release.

**CFD (#22 only).**
- Solver: ANSYS CFX, steady RANS, k-ε turbulence, no-slip wall.
- Mesh: tetrahedra of about 4 mm, about 170k elements, in a 200×200×300 box. The unit is not printed; mm is presumed.
- Flow: 25 m/s inflow at 1 atm and 293 K.
- Spin: ω = 0 and 1800 min⁻¹, applied to 4-seam and 2-seam balls.
- Output: force components on the ball.

**Throwing test (#22).** Indoors, with a target 16.5 m away measuring 0.75 m wide × 1.25 m tall. 10 balls per orientation.

## 4. Equations

**Stated in the papers.** None in closed form. The launch is solved numerically by FE, and the forces by CFD.

**Derived here (CALC, not stated by the authors).** These are the ideal no-slip, rigid-ball kinematics for an n-roller launcher. They are the same law Sakai & Kitade 2017 state as eqs (4)–(6) (see launch_methods_check.md):
- v_ideal = mean of the roller surface speeds = (2π R_r/60) × mean(N_i), with R_r = 0.16 m.
- The ideal spin vector satisfies r_b ω × n_i = u_i − v at each contact i. For three contacts at 120°, the spin is set by the departures of each roller speed from the mean.

## 5. Data

| Quantity | Value | Conditions | Where | Label | source_id |
|---|---|---|---|---|---|
| Machine size | 1.6 m tall, 0.7 m wide | 3-roller machine | #22 §2 | text value | sakai_oda_kitagawa2006 |
| Roller tire | 320 mm OD, 20 mm wall, on a 280 mm rigid Al flange | FE and machine | #22 §3, #23 §2 | text value | both |
| Ball diameter | 72 mm | hard baseball | #22 §3 | text value | sakai_oda_kitagawa2006 |
| FE ball mesh | 19,200 elements | with seam | #22 §3 | text value | sakai_oda_kitagawa2006 |
| Rubber | ρ 1000 kg/m³, E 100 MPa, ν 0.45 | Table 1 | #22, #23 | text value | both |
| Ball (viscoelastic) | ρ 835 kg/m³, G0 46.15 MPa, G∞ 8.85 MPa, K 100 MPa, β 7000 s⁻¹ | Table 1 | #22, #23 | text value | both |
| Ball–rubber friction | μ = 0.5 | FE input | #22, #23 | text value | both |
| Initial ball speed | V0 = 0.03 m/s | FE input | #22, #23 | text value | both |
| Analysis time | 0.1 s | FE | #22, #23 | text value | both |
| Roller speeds, Case 1 (knuckle) | 1500 / 1500 / 1500 min⁻¹ | Table 2 | #22, #23 | text value | both |
| Roller speeds, Case 2 (fastball) | 1700 / 1400 / 1400 min⁻¹ | Table 2 | #22, #23 | text value | both |
| Roller speeds, Case 3 (curve) | 1325 / 1750 / 1425 min⁻¹ | Table 2 | #22, #23 | text value | both |
| FE exit speed | about 24–25 m/s in every case and seam state ("almost constant") | Cases 1–3 | #22 Fig 8, #23 Fig 5 | figure reading | both |
| FE spin, Case 1 | about 0 (4-seam about 20 min⁻¹) | | #22 Fig 9 | figure reading | sakai_oda_kitagawa2006 |
| FE spin, Case 2 | no seam about 730, 2-seam about 600, 4-seam about 720 min⁻¹ | | #22 Fig 9 | figure reading | sakai_oda_kitagawa2006 |
| FE spin, Case 3 | no seam about 1080, 2-seam about 840, 4-seam about 900 min⁻¹ | | #22 Fig 9 | figure reading | sakai_oda_kitagawa2006 |
| FE vertical launch angle, Case 1 | no seam +0.2°, 4-seam −0.57° (difference about 0.8°) | | #22 Fig 10 text, #23 Fig 7 text | text value | both |
| Same, 2-seam | within about 0.2° of no seam | | #22, #23 text | text value | both |
| CFD drag Fz | about 0.21 N (4-seam, ω 0), about 0.21 N (4-seam, 1800 min⁻¹), about 0.19 N (2-seam, 1800 min⁻¹) | 25 m/s | #22 Fig 14 | figure reading | sakai_oda_kitagawa2006 |
| CFD lift Fy | about 0, about 0.05 N, about 0.045 N (same order as above) | 25 m/s | #22 Fig 14 | figure reading | sakai_oda_kitagawa2006 |
| Throwing test | 10 balls each, 2-seam, 4-seam and random; target 16.5 m, 0.75 × 1.25 m | 1700/1400/1400 | #22 §5 | text value | sakai_oda_kitagawa2006 |
| Mean roller surface speed | 25.13 m/s for every case (mean N = 1500 min⁻¹, R = 0.16 m) | Cases 1–3 | from Table 2 | CALC | both |
| FE v / mean surface speed | about 0.95–1.0 | Cases 1–3 | Fig 8 ÷ CALC above | CALC on figure reading | both |
| Ideal no-slip spin, Case 2 | r ω = 3.35 m/s, so about 889 rpm at r = 0.036 m; FE no-seam about 730, ratio about 0.82 | rigid ball, no deformation | CALC | CALC on figure reading | sakai_oda_kitagawa2006 |
| Ideal no-slip spin, Case 3 | \|r ω\| = 4.30 m/s, so about 1141 rpm at r = 0.036 m; FE no-seam about 1080, ratio about 0.95 | rigid ball | CALC | CALC on figure reading | sakai_oda_kitagawa2006 |
| Spin ratio of the FE fastball | S = r ω / v ≈ 0.036 × 76.4 rad/s / 24.5 ≈ 0.11 | Case 2, no seam | CALC | CALC on figure reading | sakai_oda_kitagawa2006 |

Notes on the CALC rows:
- The ideal-spin CALC uses the undeformed ball radius. A squeezed ball has a smaller effective contact radius (Wojcicki's r_l), which raises the ideal spin. The 0.82–0.95 ratios are therefore upper estimates of spin efficiency.
- The paper does not state the roller gap or the squeeze.

## 6. Applicability to POLLEN

**Transfers (qualitatively)**
- *Theory/model; conference source.* Under Coulomb friction (μ 0.5), an FE model with a deformable viscoelastic ball and rubber rollers puts exit speed close to the ideal mean surface speed. Spin comes out somewhat below the ideal no-slip spin. So FE does not, by itself, predict the large speed deficits seen in measured launchers (see launch_methods_check.md).
- *Conference finding, then observation.* Ball orientation at the feed changes the launch angle more than the speed or spin. That orientation-driven angle scatter, not the aerodynamics, dominated accuracy for a seamed ball. **POLLEN is perforated with a hole pattern, so it is not axisymmetric in contact either.** Its feed orientation may set the launch angle the same way. This is a hypothesis to test, not a POLLEN fact.
- *Methodology.* The pipeline is FE launch → exit state (v, ω, θ) → CFD forces → trajectory. It is a template for PM-001, with the project's LCP launcher model (src/launcher.py) in the FE role. The paper does not report a trajectory-vs-measurement comparison, so the pipeline itself is **not validated** in these sources.

**Does not transfer**
- All material constants: a solid baseball (ρ 835 kg/m³, G 46/8.9 MPa) and E 100 MPa rubber. POLLEN is a hollow, perforated polyethylene shell of about 25 g, and its contact law is a shell law (see sweep_launch §2.7).
- The three-roller geometry. Every roller is powered, so the ideal v is the mean speed, not u/2. PM-001 is a single powered wheel with a stationary hood or a passive roller. The hood acts as a zero-speed surface, which halves ideal v and fixes S = 1 at no slip.
- The speed regime (about 25 m/s vs about 5–15 m/s planned for POLLEN) and the 320 mm rollers vs the 98 mm wheel.
- The CFD forces. A seamed baseball at 25 m/s is not a perforated ball. The k-ε RANS steady model is not validated in this paper against any wind-tunnel data. Do not use these forces for POLLEN lift or drag.
- The FE spin magnitudes. These are moderate-spin fastball cases with S about 0.1. PM-001 needs a hood launch with S about 1.

## 7. Implications for PM-001 models and tests

1. **No change to the baseline.** Keep one powered 98 mm wheel. These papers give no reason to move to multiple powered wheels, and HANDOFF §5 forbids it anyway.
2. **The model's speed efficiency.** A deformable-ball FE model with μ 0.5 gives v ≈ 0.95–1.0 of ideal (CALC on a figure reading). A slip-free or nearly slip-free model is therefore the **upper** bound. src/launcher.py should not be expected to reproduce measured η_v below 0.6 unless it includes the loss mechanisms. Those include:
   - roller compliance
   - feed-in slip
   - contact-time limits
   - hysteresis

   Keep η_v as a measured input (sweep_launch §5).
3. **Spin efficiency.** FE spin was about 0.82–0.95 of ideal (CALC, upper estimate). For the hood case this supports an η_w band whose upper part is near 1, consistent with the sweep default η_w ∈ [0.5, 1.0]. It is not a POLLEN measurement.
4. **Test plan: ball orientation.** Mark POLLEN and feed it in at least two fixed orientations (for example hole-pattern axis vertical vs horizontal), plus random orientation. Compare launch-angle SD before attributing scatter to aerodynamics or wheel-speed droop. One shot per orientation proves nothing (HANDOFF §5). Use at least 10 per orientation, as #22 did.
5. **Test plan: exit-state measurement.** The authors' 3 ms-per-frame video comparison was too coarse to quantify spin. Use the higher-rate recipe in launch_methods_check.md §4.

## 8. Caveats

- Both are conference proceedings. The FE model's validation is a visual frame comparison (#23) with no numbers. Grade the FE results as **theory (numerical model), conference source**.
- All launch-state numbers except the launch angles are figure readings, about ±5% of full scale.
- The FE contact friction (μ 0.5) is an assumed input. The papers do not give a measured μ for ball on rubber.
- The CFD box unit is not printed, and the mesh-independence study is not shown.
- The throwing-test result is a short observation (10 balls per orientation). No SD or landing coordinates are tabulated in the text.
