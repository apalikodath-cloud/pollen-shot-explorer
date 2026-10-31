# Launch-methods cross-check: wojcicki2011 and sakai2017 vs sweep_launch.md, plus the Sakai 2006 FE pair

Purpose: check what `research/sweeps/sweep_launch.md` says about RESEARCH_PAPERS #17 (`wojcicki2011`) and #25 (`sakai2017`, called `sakai_kitade2017` here) against the full texts. Then combine them with #22/#23 (see `sakai_oda2006.md`) into one evidence statement on how far v/u and S can depart from ideal for a wheel or roller launcher.

Read: 2026-10-30, research agent for PM-001. **This file does not edit sweep_launch.md**; another workflow owns it. The corrections below are for that owner to apply.

Labels:
- **text value**: printed in the text or a table.
- **figure reading**: read by eye from a plot. Approximate.
- **CALC**: derived here, not stated by the source.

Grades:
- **peer-reviewed finding**
- **theory**
- **unreviewed technical source** (includes conference proceedings)
- **observation** (team, forum or anecdote)

## 1. Access and URLs

| source_id | Citation | Access | Review status |
|---|---|---|---|
| sakai_kitade2017 (#25; `sakai2017` in the sweep) | Sakai & Kitade, table-tennis machine with launch rollers and gyro rollers, *Trans. JSME* (日本機械学会論文集) **83**(856), paper 17-00225 (2017). DOI 10.1299/transjsme.17-00225. Received 17 May 2017, revised 29 Aug, accepted 6 Nov, online 25 Dec 2017. Kanazawa University and Mitsubishi Pencil. Japanese, English abstract. | **Full text read** (14 pp.) | Peer-reviewed journal |
| wojcicki2011 (#17) | Wojcicki, Pucilowski, Kulesza, "Mathematical Analysis for a New Tennis Ball Launcher", *Acta Mechanica et Automatica* **5**(4), 110–117 (2011). Bialystok University of Technology. | **Full text read**, from the full-issue PDF (122 pp.; the paper is PDF pp. 107–114) | Journal article, mostly theory, with simple material bench tests |

URLs tried:
- https://doi.org/10.1299/transjsme.17-00225 → 200. Redirects to https://www.jstage.jst.go.jp/article/transjsme/83/856/83_17-00225/_article/-char/ja/
- https://www.jstage.jst.go.jp/article/transjsme/83/856/83_17-00225/_pdf → 200 (3.0 MB). J-STAGE marks it `citation_fulltext_world_readable`.
- https://pbc.biaman.pl/Content/14776/PDF/AM%20vol.5%20no%204.pdf → 200 (8.77 MB full issue). Podlaska Biblioteka Cyfrowa, Bialystok.
- https://yadda.icm.edu.pl/baztech/download/import/contents/BPB2-0062-0016-...pdf → 403 (bot check)
- http://www.actawm.pb.edu.pl/volume/vol5no4/wojcicki_kulesza_pucilowski_en_2010_085.pdf → 404
- https://pbc.biaman.pl/dlibra/publication/15880/edition/14776/content → 404

Downloads went to fresh folders under %TEMP%. They were read with pdftotext and as page images. Nothing was executed.

## 2. Corrections to sweep_launch.md

| # | sweep_launch.md says | Full text shows | Grade of the corrected claim |
|---|---|---|---|
| C1 | sakai2017: "English abstract only" (table row; §2.5; §6 "not read in full") | The full text is open on J-STAGE and was read. | n/a (access fact) |
| C2 | sakai2017: "landing within 40 mm (140 mm in gyro mode)" | These are **standard deviations** of landing position (Fig 7), not maximum scatter. No-, top- and side-spin balls have SD < 40 mm in both X and Z. Gyro has about 60 mm in X and about 140 mm in Z (figure reading). 40 balls, launched at v_Rx = 15 m/s. | peer-reviewed finding |
| C3 | sakai2017: "spin above 5000 rpm" | Table 1 (as extracted) lists 5500 rpm max top/back, 12000 rpm side and 8500 rpm gyro. The §4.3 text and the Conclusion give **7000 rpm** max top/back. The paper is **internally inconsistent** on top/back spin (5500 vs 7000). Max ball speed is 42.5 m/s (153 km/h) in both places. | peer-reviewed finding (with the inconsistency noted) |
| C4 | sakai2017 is not used for launcher efficiency | **The paper has a measured speed efficiency.** Fig 4: ball speed v_B is proportional to the mean roller circumferential speed v_Rx, swept from 0 to 40 m/s in 5 m/s steps with 5 balls per spin type. The fit is v_B = 0.481 v_Rx (figure annotation). The text says v_B is about 48% of v_Rx **because the ball slips on the rollers at launch**, and that the ratio does not depend on spin type (no, side, gyro). | peer-reviewed finding |
| C5 | wojcicki2011: "Poznan repository (blocked by browser verification) ... not read ... No data taken", pages 110-119 | The host is Podlaska Biblioteka Cyfrowa (Bialystok), and the full issue downloads directly. The pages are 110–117. | n/a (access fact) |
| C6 | (implied) wojcicki2011 is a launcher dynamics source | It contains **no measured exit speed or spin**. Launch kinematics are ideal no-slip (eqs 14–17). The measured items are ball E (two-plate test) and an inclined-plane "friction" test. | theory |
| C7 | n/a | Wojcicki's adopted μ = 2.05 is **not a Coulomb friction coefficient**. It is a tilt-angle traction from a half-ball pressed flat on a roller segment (Table 3 range 0.58–2.05). Do not copy it into mu_wheel. | peer-reviewed finding (journal), interpreted |
| C8 | §3 item 3: "Observed eta_v is 0.41-0.59 for gapped or lightly squeezed two-roller launchers" | sakai_kitade2017 adds a **peer-reviewed** datum, η_v ≈ 0.48. This one is **squeezed** (34 mm gap on a 40 mm ball, foam rollers), so the band is not limited to gapped launchers. | peer-reviewed finding |

## 3. What each source gives on v/u and S

### 3.1 sakai_kitade2017 (peer-reviewed; measured)

**Machine.**
- Two pairs of launch rollers: 124 mm OD, 28 mm wide.
- Gyro rollers: 88 mm OD, 28 mm wide.
- Roller material: porous soft polyurethane foam, with a smooth surface of radius R30 mm.
- Gap d = 34 mm for a 40 mm ball.
- Drive: 20 W DC shunt motors.
- Gyro crossing angle γ = 0° or ±45°.

**Ball.** Yamato TSP 40 mm training ball, φ39.87 ± 0.11 mm, 2.740 ± 0.016 g, 12 balls used. **Imaging:** Photron FASTCAM SA-5 at 2000 fps, 20 kHz shutter, about 3.00 px/mm. Stated accuracy is about 0.05 m/s and about 50 rpm. Conditions were 22 °C with no wind.

**Theory (stated, eqs 4–10).**
- v_B = Σv_i / n.
- Spin comes from contact-point speed differences.
- Gyro posture gives ω = v sinγ / r_B.
- Assumptions: no slip, no deformation, no gravity.

**Measured.**

| Quantity | Value | Conditions | Label |
|---|---|---|---|
| v_B / v_Rx | 0.481 (Fig 4 fit), "about 48%" (text) | v_Rx 0–40 m/s, 5 balls per point, no, side and gyro spin | figure annotation + text value |
| Accuracy-test mean ball speed | 7.61 m/s, SD 0.56 | v_Rx = 15 m/s, 40 balls | text value |
| v_B / v_Rx in the accuracy test | 0.507 | 7.61 / 15 | CALC |
| Fig 5 examples | knuckle 30.5 m/s, about 0 rpm; down/back spin 28.8 m/s, 3700 rpm; side 22.2 m/s, 12000 rpm; gyro 16.7 m/s, 5500 rpm | v_Rx **not stated** | text value (caption) |
| S = r ω / v for the Fig 5 examples (r = 0.02 m) | back 0.27; side 1.13; gyro 0.69 (gyro axis is along the flight path, so no Magnus lift) | as above | CALC |
| Accuracy-test spin settings | top: v1 = 1.5 v_Rx, v2 = 0.5 v_Rx; side: v3 = 1.5 v_Rx, v4 = 0.5 v_Rx; gyro: γ = 45° | launch height 990 mm, 130 mm behind the end line, θ = 13.5° | text value |
| Spin effect on landing | top spin lands about 250 mm short in X vs no spin; side spin shifts Z by about −150 mm; gyro range ≈ no spin | 40 balls | figure reading |
| Landing SD | < 40 mm X and Z for no, top and side spin (about 33/21, 23/15 and 34/21 mm); gyro about 60 mm X, about 140 mm Z | | figure reading |

**Range of the 0.481 fit.** It was fitted over v_Rx 0–40 m/s, which means ball speeds of roughly 0–19 m/s. The 30.5 m/s and 42.5 m/s shots imply mean roller speeds well above 40 m/s if the ratio held, but the paper does not state v_Rx for them. **The proportionality is documented only inside the swept range.** POLLEN's planned 5–15 m/s sits inside it.

**Gyro scatter.** The authors attribute the larger gyro scatter to unbalanced contact force on the crossed rollers.

### 3.2 wojcicki2011 (theory; no measured launch)

**Design brief.** 30–200 km/h, elevation −20° to 80°, spin 0–2000 rpm, launch height up to 3 m.

**Flight model.** Eqs 1–7: drag plus lift ∝ Cl·r³·ω×V, implemented in Simulink.
- Cd and Cl are secondary values taken from Alam 2007: Cd 0.55–0.85 and Cl 0.30–0.70 over 20–140 km/h and 0–3000 rpm.
- Spin decay is neglected. The paper cites video for this but shows no data.
- The text gives r = 0.333 m, evidently a typo for 0.0333. m = 0.058 kg.

**Launch conditions (stated).**
- Pull-in requires μ ≥ tan α, where α is the grab angle.
- Throw requires F_w ≤ 2T.
- Normal force from the material law: N = E s l / (2r).

**Measured material inputs.**
- E from a two-plate test, loads 0.55–5.5 kg: mean 3.63 MPa (range 2.83–4.50). A standardized-ball calculation gives 4.20 MPa, which was adopted. Axes differ by about 3%.
- "μ" from an inclined plane on polypropylene with a half ball pressed flat:

  | Surface | Contact length | Angles | μ |
  |---|---|---|---|
  | Plane | 0.008–0.035 m | 32–44° | 0.63–0.97 |
  | Roller segment | 0.005–0.035 m | 30–64° | 0.58–2.05 |

  μ = 2.05 was adopted.

**Kinematics (stated, no slip).**
- V = (V1 + V2) / 2 and r_l ω = (V2 − V1) / 2, with r_l the deformed-ball lever arm.
- Roller radius 0.1 m; roller axes 0.25 m apart.
- 200 km/h with no spin needs 5300 rpm.
- 200 km/h with 2000 rpm spin needs 5800 and 4800 rpm.
- CALC: those speeds imply r_l ≈ 0.025 m, consistent with a 0.05 m gap between rollers.

**Energy (stated).**
- I_r = ½ m_r r_r²; I_p = (2/3) m r² (thin shell).
- Rollers must run about 90 rpm faster (1.5% and 1.8%) to cover the ball's energy.
- P_d = 45 W for t_d = 1 s; start-up t_r = 35 s with 45 W motors.

**What it bounds.** Only the **ideal** v/u and S. It gives no efficiency.

### 3.3 sakai_oda_kitagawa2006 / sakai_oda_kawata2006 (conference; FE theory)

Details are in `sakai_oda2006.md`. The setup is a three-roller FE launch with rubber rollers, a viscoelastic baseball and μ 0.5.

| Quantity | Value | Label |
|---|---|---|
| v / mean surface speed | about 0.95–1.0 | CALC on figure reading |
| Spin / ideal no-slip spin | about 0.82–0.95 | CALC; upper estimate, because the undeformed radius was used |
| Validation | qualitative video frames only | text |

## 4. Combined bound on v/u and S for a wheel launcher (for the PM-001 model)

Definitions follow sweep_launch §3:
- v_exit = η_v · v_ideal, where v_ideal = mean surface speed. For a hood, v_ideal = u_w/2.
- ω_exit = η_w · v_exit / r_b for the hood.

| Evidence | η_v | Spin | Grade | Ball / roller |
|---|---|---|---|---|
| FE, μ 0.5, rubber rollers (sakai 2006) | about 0.95–1.0 | about 0.82–0.95 of ideal spin | theory (conference) | solid 72 mm baseball (mass not stated); stiff rubber |
| Ideal no-slip (wojcicki2011; sakai_kitade2017 eqs) | 1 | S = (u1 − u2)/(u1 + u2); hood S = 1 | theory | any |
| Measured, foam rollers, 6 mm squeeze (sakai_kitade2017) | 0.481 (fit); 0.507 (40-ball test) | Fig 5 S from 0.27 (back) to 1.13 (side) | peer-reviewed finding | 2.74 g, 40 mm hollow plastic shell |
| Measured, sepak takraw, near-zero squeeze (basyiruddin2025, from the sweep) | about 0.5–0.59 | not measured | per sweep | hollow woven ball |
| Ponnusamy 2015 (quoted second-hand in the sweep) | 0.41 | n/a | secondary, not read | table-tennis launcher |

**Conclusions.**
1. Models with Coulomb friction μ ≈ 0.5 and no loss mechanism beyond viscoelastic contact predict η_v near 1. **Measured** hollow-ball roller launchers sit at η_v ≈ 0.41–0.59. The peer-reviewed sakai_kitade2017 value is 0.48–0.51. That gap is the size of the unmodelled loss, which the authors attribute to launch slip.
   - Grade: peer-reviewed finding for the measured value; the comparison itself is CALC.
2. The sweep's η_v band 0.41–0.59 is **consistent** with the full text of sakai_kitade2017. Its lower default bound of η_v = 0.45 is supported.
3. **Unit tension with params_lit.json (flag only; that file is not edited here).** For a fixed hood, η_v = 0.48 means v/u_w = 0.24. params_lit `launcher.v_over_surface_speed` has low = 0.30. That range ("FRC ... 0.30-0.45 on other balls") is FRC/forum observation, and it is not clear whether it is quoted relative to u or to u/2. Its owner should state the reference speed. If measured roller-launcher efficiencies carry over to a hood, v/u could fall below 0.30.
   - Grade: CALC on a peer-reviewed number, but the transfer is a hypothesis.
4. **Spin vs speed slip may differ.** The measured S = 1.13 for the side-spin example exceeds the S an ideal no-slip spin pair would give at that ball speed if speed slip and spin slip were equal. v_Rx is not stated for Fig 5, so this cannot be computed exactly.
   - Qualitatively, a slipping roller launcher can lose more speed than spin. This is directionally consistent with params_lit S_exit_hood > 1.
   - Grade: peer-reviewed observation, qualitative only.
5. **Ball-to-ball posture matters.**
   - sakai 2006 (conference) found launch angle was the quantity most sensitive to seam posture, about 0.8° in FE.
   - sakai_kitade2017 (peer-reviewed) found gyro shots, with unbalanced contact, had a Z SD of about 140 mm vs about 15–21 mm for the others (figure readings).
   - Inference: contact asymmetry turns into direction scatter more than into speed scatter. POLLEN's hole pattern is a contact asymmetry. This is a hypothesis to test.

## 5. Transfer cautions to POLLEN

- None of these coefficients is a POLLEN fact. The sources cover:
  - a 2.74 g, 40 mm table-tennis shell
  - a 58 g felted tennis ball
  - a solid baseball

  POLLEN is a 71 mm, about 25 g, perforated polyethylene ball. The table-tennis η_v transfers only as an order-of-magnitude warning that measured efficiency can be about half of ideal.
- All the measured efficiencies come from **powered roller pairs or quads**. None is a fixed hood or a passive roller. A hood adds a sliding or rolling contact against a stationary surface, which the multi-roller data do not test.
- Wojcicki's E (3.6–4.2 MPa) and "μ" (0.58–2.05) are for a tennis ball and are not transferable. The "μ" is not Coulomb μ in any case.
- Foam rollers (sakai_kitade2017) vs a 98 mm flywheel with its tread compound: roller compliance changes the contact time and the slip, so η_v will differ.

## 6. What this means for the PM-001 model and test plan

1. **Baseline unchanged.** One powered 98 mm wheel with a fixed hood or a passive upper roller. Nothing here argues for multiple powered wheels.
2. **Model.**
   - Keep η_v and η_w as explicit factors, applied to the src/launcher.py output or calibrated into it.
   - Treat an LCP or FE result near η_v = 1 as the upper bound.
   - Carry η_v down to about 0.45 in sweeps until POLLEN is measured.
3. **The first launcher test measures η_v and η_w.** Recipe, adapted from sakai_kitade2017:
   - High-speed camera at ≥ 2000 fps with a short shutter.
   - At least about 3 px/mm over the first 100–200 mm of flight.
   - A marked ball, so spin can be read from mark rotation.
   - Their stated accuracy at this setup was about 0.05 m/s and about 50 rpm. That is ample for POLLEN, where S = 1 at 8 m/s is about 2150 rpm (CALC: ω = v / r_b = 8 / 0.0355).
4. **Sweep the wheel speed in steps and fit v_exit vs u_w** (Sakai's Fig 4 method). A straight line through the origin gives η_v. Curvature or an intercept shows slip changing with speed. Use at least 5 balls per step.
5. **Control and record ball orientation.** Feed POLLEN in fixed hole-pattern orientations and also at random. Report landing or entry SD per orientation, not single shots (HANDOFF §5).
6. **Report SD, not "within X mm".** sakai_kitade2017's "40 mm" is an SD. PM-001 CELL-entry statistics should use the same convention.
7. **FE-to-flight pipeline.** The sakai 2006 chain (launch FE → exit state → CFD forces → trajectory) is a methodology template only. It was never validated end-to-end in these sources. PM-001's trajectory model should be checked against measured entry points, not against another simulation.

## 7. Caveats

- The v_B = 0.481 v_Rx line is a figure annotation. The text gives "about 48%". The 0.507 accuracy-test ratio is a CALC from text values.
- The 5500 vs 7000 rpm top/back spin inconsistency in sakai_kitade2017 is unresolved. Do not quote either as a firm maximum.
- Table 1 of sakai_kitade2017 came out of the text extraction with its values offset by one row. The reading here (5500 top/back, 12000 side, 8500 gyro) agrees with the §4.3 sentence for side and gyro but not for top/back.
- All landing-SD values and the 250 mm and −150 mm shifts are figure readings.
- The Ponnusamy 0.41 value is second-hand and was not read.
