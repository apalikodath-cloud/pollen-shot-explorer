# EXTRA_SOURCES: coverage merge for the 25 sources in RESEARCH_PAPERS.md (PM-001)

Merged 2026-10-30 by the PM-001 research merger. This file merges three sets of notes:
- `research/papers/*`, `research/checks/*` and `research/sweeps/*`, which belong to another workflow;
- the newer reader notes in `research/papers_extra/*`.

It edits nothing else. Parameter changes below are **proposals only**: `research/params_lit.json`, `research/LITERATURE_SYNTHESIS.md`, `src/`, `data/` and `docs/` belong to another workflow.

Study question, for context. Can one powered 98 mm flywheel, with a fixed hood or a passive upper roller, give POLLEN enough backspin or Magnus curvature to enter the upward-facing CELL of the tilted HIVE from the unfavourable side? A spin-dependent rim contact would also count. POLLEN is 71 mm, about 25 g, and a hollow perforated PE ball.

**Grades used**
- **PR**: peer-reviewed finding.
- **TH**: theory. This includes peer-reviewed theory and numerical models.
- **UN**: unreviewed technical source. This includes conference proceedings, theses, web articles and CFD with no validation.
- **OB**: observation. This includes team, forum, anecdote and student-demo material.

Grading follows the claim, not the venue. For example, a peer-reviewed paper can contain only theory.

**Number rule.** Every number below appears in the cited reader note, and that note took it from the source text, a source table or a source figure. Derived values are marked **CALC**. For abstract-only sources, no numbers are given except values printed in the abstract itself, and those are marked as abstract text. **No pickleball, table-tennis, tennis, baseball or Wiffle coefficient here is a POLLEN fact.**

URLs tried are recorded in each reader note (section 1 of each `papers_extra/*.md` note, and the access section of each `papers/*.md` note). This merge did no new downloads.

---

## 1. Coverage table (all 25)

**Column key**
- **Where**: `P` = `research/papers/<id>.md`, `C` = `research/checks/<id>.md`, `S` = `research/sweeps/<file>`, `X` = `research/papers_extra/<file>`.
- **Access**: what was actually read of the **target** source. Companions are listed separately.

| # | Short cite | Where covered | Access (target source) | Grade of what is used |
|---|---|---|---|---|
| 1 | Lindsey 2025, pickleball aero (TWU) | P lindsey2025, C lindsey2025 | Full text (HTML + figures) | UN |
| 2 | Steyn et al. 2025, third-shot drop | P steyn2025, C steyn2025 | Preprint full text (arXiv v1). **Journal VoR not read.** | PR (venue); content checked on the preprint |
| 3 | Rossmann & Rau 2007, Wiffle aero | P rossmann2007, C rossmann2007, S sweep_aero | Full text (C rossmann2007: Lafayette repository PDF, 12 figures digitised; P rossmann2007 §2 predates it) | PR (full text) |
| 4 | Brettle, flywheel shooter notebook | P brettle, C brettle, S sweep_launch | Full text + .ipynb source | TH (unreviewed) |
| 5 | Pedersen 2026, flywheel shot analysis | P pedersen2026, C pedersen2026, S sweep_launch | Full text (thread, PDF, spreadsheet) | TH (unreviewed); one forum datum OB |
| 6 | Van Wyk, Smith & Lyu 2026, pickleball mechanics | P vanwyk2026, C vanwyk2026 | Full text (5 pp. extended abstract) | PR (short conference, manufacturer-funded) |
| 7 | Emond, Sun & Swartz 2024 | P emond2024, C emond2024 | Full text (arXiv v1 + SFU draft) | PR simulation (no lift; Cd borrowed) |
| 8 | Creer 2023, pickleball CFD thesis | X creer2023 | Full text (84 pp.) | UN; **numerical output self-declared invalid** |
| 9 | Sakai et al. 2016, table-tennis lift crisis | P sakai2016, C sakai2016, S sweep_aero | Full text (5 pp.; figures read by eye) | UN (non-refereed proceedings) |
| 10 | Ito & Kamijima 2025, spinning-sphere CFD | P ito2025, C ito2025, S sweep_aero | Full text | TH (peer-reviewed numerical) |
| 11 | Cross & Lindsey 2017, smooth balls in flight | P cross2017, C cross2017 | **Abstract only**; companion Cross 2012 AJP in full | PR (qualitative, abstract) |
| 12 | Cross & Lindsey 2013/2014, tennis balls in flight | X cross_lindsey2013 | **Abstract only**, seen through a summarising fetch. Companion TWU page (same authors) read in full. | PR (abstract, qualitative); UN for companion numbers |
| 13 | Wang et al. 2018/2019, 3-camera table-tennis tracking | X wang2018 | **Abstract only** (SAGE 403, closed OA) | PR (qualitative, abstract) |
| 14 | Mehta 1985, Aerodynamics of sports balls | X mehta1985 | **Abstract only**; NTRS metadata only; Chadwick 2003 thesis used for a secondary description | PR review (qualitative, abstract) |
| 15 | Goodwill, Chin & Haake 2004, tennis-ball aero | X goodwill2004 | **Abstract only**. Companions: Haake 2007 and Goodwill & Haake 2004 wear (abstracts); Chadwick 2003 thesis (full OCR). | PR (abstract) |
| 16 | Isomura et al. 2016, spinning table-tennis model | X isomura2016 | Full text (4 pp.; all tables and Figs 6–9 as images) | UN (CFD, no validation); TH for equation forms |
| 17 | Wójcicki, Puciłowski & Kulesza 2011, tennis launcher | X launch_methods_check | Full text (full-issue PDF, pbc.biaman.pl). **Corrects sweep_launch, which said "not read".** | TH (no measured launch); bench material tests only |
| 18 | Cross 2005, spinning ball near normal incidence | P cross2005, C cross2005, S sweep_impact | Full text (author PDF) | PR |
| 19 | Cross 2010, tangential compliance | X cross2010_check, S sweep_impact | Full text (author PDF, 5 pp.) | TH (peer-reviewed model; no measurement of a real surface) |
| 20 | Allen, Haake & Goodwill 2010, friction in tennis impacts | P allen2010, C allen2010, S sweep_impact | **Abstract only**; companion Allen thesis (full OCR) | PR (abstract) |
| 21 | Ghaednia, Cermik & Marghitu 2015, oblique impact on racket | X ghaednia2015 | **Abstract only** (Crossref abstract). Companion Cermik 2017 dissertation in full. | PR (abstract); UN for dissertation numbers |
| 22 | Sakai, Oda & Kitagawa 2006, seam + roller machine | X sakai_oda2006, X launch_methods_check | Full text (5 pp.) | UN (conference); FE/CFD results are TH |
| 23 | Sakai, Oda & Kawata 2006, throw simulation accuracy | X sakai_oda2006 | Full text (2 pp.) | UN (conference); validation is qualitative only |
| 24 | Wu, Park & Wu 2022, MEMS 411 Wiffle pitcher | X wu_mems411_2022 | Full text (37 pp., Internet Archive snapshot; live repository behind Cloudflare) | OB (student demo, naked eye); the rpm figure is flawed TH |
| 25 | Sakai & Kitade 2017, four-roller ball machine | X launch_methods_check | Full text (14 pp., J-STAGE). **Corrects sweep_launch, which said "abstract only".** | PR |

**Extra item (not in RESEARCH_PAPERS.md).** `X cuberobot_decode` covers the FTC DECODE team code (kleongf/FTC_Decode and kleongf/Decode). It is OB. Full source read.

**Counts.** All 25 have a note.
- Full text of the target: 16 (#1, 4–10, 16–19, 22–25).
- Preprint only: 1 (#2).
- Abstract only: 8 (#3, 11, 12, 13, 14, 15, 20, 21).
- Not retrieved at all: none.

---

## 2. What the extra sources add or change

### 2.1 Peer-reviewed findings

- **#25 Sakai & Kitade 2017. Measured launcher speed efficiency (PR).**
  - Ball speed is proportional to the mean roller circumferential speed over 0–40 m/s. The fit annotation is v_B = 0.481·v_Rx; the text says "about 48%" and attributes the loss to slip at launch.
  - The ratio does not depend on spin type.
  - The 40-ball accuracy test gives 7.61 m/s at v_Rx = 15 m/s, a ratio of 0.507 (CALC).
  - The machine is **squeezed**: 34 mm gap on a 40 mm ball, with foam rollers. So the measured η_v ≈ 0.5 band is not limited to gapped launchers.
  - Landing "40 mm" is a **standard deviation**, not a maximum.
  - Gyro shots, which have unbalanced roller contact, scattered more laterally. The authors attribute this to contact-force imbalance.
  - Transfer: only as a warning that a measured efficiency can be about half of ideal. This is a multi-roller launcher with a 2.74 g, 40 mm shell, not a hood.
- **#12 Cross & Lindsey 2013 (PR, abstract only).**
  - Free-flight Cd and Cl can differ from tunnel values.
  - Shot-to-shot scatter comes from surface asymmetry.
  - "Significant lift was observed even at very low spin", which the authors liken to a knuckleball.
  - Transfer: POLLEN's hole pattern is a fixed asymmetry. Expect a knuckle-type force at low S and a per-shot distribution of Cl. Report Cl as a distribution, not a single value.
- **#13 Wang et al. 2018 (PR, abstract only).**
  - Three synchronised high-speed cameras can reconstruct both the 3D trajectory and the spin of a small ball.
  - A drag + Magnus model reproduced the reconstructed trajectories for topspin, backspin, side spin and mixed spin.
  - The accuracy metric is undefined in the abstract, so no figure is carried.
- **#14 Mehta 1985 (PR review, abstract only, indexer abstract).**
  - Lift depends on spin, Re and surface, and the abstract refers to a "cut-off point".
  - Qualitative support for a Cl(S) that **saturates** rather than growing linearly.
  - No numbers are used.
- **#15 Goodwill et al. 2004 (PR, abstract only).**
  - Lift and drag depend on ball surface condition (new versus worn).
  - A lower Cl narrows the usable shot window even though it barely changes flight time. Lift sets *where* the ball arrives.
  - Companion Haake 2007 (abstract): tennis spin decay is "over six times" golf, attributed to nap skin friction. This is qualitative support that surface texture can dominate spin decay.
  - POLLEN's whole Re band (about 9×10³ to 4.7×10⁴, CALC in the note) lies below Goodwill's tested range.
- **#21 Ghaednia et al. 2015 (PR, abstract only).**
  - At low impact speed, e is constant across impact angle.
  - The effective friction coefficient changes with impact angle.
  - The companion dissertation (UN) shows exit tangential speeds at or just below the rolling value. That is a grip-then-roll signature, not slide-throughout with a fixed μ. The authors' "μ rises with angle" reading is therefore an impulse-ratio effect.
  - Consequence: μ_eff, the impulse ratio, is not the Coulomb μ. Read Coulomb μ only from the glancing-incidence plateau.
- **#3 Rossmann & Rau 2007 (PR, full text via C rossmann2007; P rossmann2007 was abstract only).** Perforated balls can show orientation-dependent forces without spin.

### 2.2 Theory

- **#19 Cross 2010 (peer-reviewed theory, full text).**
  - On a surface that is heavy or rigid in the tangential direction, the ball cannot leave with more than the rolling spin. Over-rolling spin (e_x near 1) needs a **light, springy** surface.
  - Incoming backspin widens the slide-throughout range. The criterion is tan θ1 < (1 − rω1/v_x1)/[2μ(1+1/α)], with (1+e) in place of 2 for e < 1.
  - With e_t = 0 and e = 1, `src/contact.py`'s stick test reduces exactly to this boundary (CALC in the note).
  - For a backspinning POLLEN on a stiff HIVE lip, μ controls the rebound, not e_t.
  - sweep_impact over-read this paper. It supports neither a compliant-HIVE default nor e_t = 0.3 for a rigid HIVE.
- **#17 Wójcicki et al. 2011 (theory, full text).**
  - Kinematics are ideal no-slip only. There is no measured exit speed or spin.
  - Its adopted "μ = 2.05" is a tilt-angle traction from a half-ball pressed flat on a roller segment. **It is not a Coulomb μ.**
- **#22/#23 Sakai & Oda 2006 FE (theory in a conference source).**
  - Coulomb μ 0.5 with viscoelastic contact gives η_v about 0.95–1.0 of ideal and spin about 0.82–0.95 of ideal (CALC on figure readings).
  - A no-slip or FE model is therefore an **upper bound**. The about 0.5 measured in #25 shows the size of the unmodelled loss.
  - Launch angle was the quantity most sensitive to ball posture (about 0.8° in FE, figure reading).
- **#16 Isomura 2016, equation forms (TH).**
  - Gives a Cd(Sp) polynomial and a Magnus-coefficient form, with C_L = (8/3)·Sp·C_M.
  - Gives a trajectory least-squares identification (eqs 8–9), with optional free per-shot spin and AIC order selection. This is a usable fitting recipe.

### 2.3 Unreviewed technical sources

- **#16 Isomura 2016 CFD output (UN, unvalidated).**
  - Cd roughly doubles between Sp ≈ 0.1 and 2.
  - The derived equivalent C_L rises and flattens: 0.486 at Sp 1 and 0.572 at Sp 2 (CALC in the note).
  - Validation was only proposed. The forces are pressure-only, and eq. (1) has typos. The run matrix spans Re far beyond the range used to argue Re independence.
  - Use it only as a **shape** argument: Cd may rise with S, and Cl saturates. Do not use it for magnitudes.
- **#8 Creer 2023 (UN).**
  - The author states no valid drag coefficient was obtained. The pressure drag came out negative.
  - The "26- and 40-hole similar" result is not evidence.
  - The only value is six acceptance checks for any future POLLEN CFD (see §4.7).
- **#12 TWU companion (UN).**
  - Gives the method details: 6.4 m two-station spacing, perpendicular equatorial lines, depth-dependent scale bar, two independent digitisers, and a frame-rate check against a stopwatch.
  - Tennis C_D 0.507 (SD 0.024) and C_L 0.1–0.3 at S 0.14–0.53, for a felt ball at 14–30 m/s. **Not POLLEN priors.**
- **#21 Cermik 2017 dissertation (UN).**
  - 10,000 fps (also stated in the paper abstract) at 512 × 512 px.
  - Ball centroid by Hough transform, which works with partial occlusion. Rotation by DIC on a speckle pattern.
  - 100 frames either side of impact for pre- and post-impact velocity.

### 2.4 Observations

- **#24 Wu et al. 2022 (OB).**
  - A **two-powered-wheel** differential pitcher with 35A wheels produced backspin, topspin and no-spin Wiffle pitches whose difference was "recorded by naked eye".
  - No spin, curvature or lift was measured.
  - "5044 rpm" is a model output that uses the **ball** radius and assumes ω_ball = ω_wheel. It is not a measurement.
  - The architecture is out of scope (HANDOFF §5) and is no reason to change the baseline.
- **cuberobot_decode (OB).**
  - The code has **no aero or Magnus model**. Aiming uses a hand-tuned LUT (distance → hood angle, wheel speed) plus empirical time-of-flight fits and fudge factors (speedCoefficient 0.5–0.7).
  - The team attribution was not verified.
  - It shows teams tune around drag and spin. It does not show those effects are negligible.
  - The TOF comments give frame counts with no frame rate, which is the logging failure to avoid.
- **#25 / #22 posture (PR / UN).** Contact asymmetry shows up more as direction scatter than as speed scatter. POLLEN's hole pattern is a contact asymmetry. This is a **hypothesis to test** (feed-orientation test, §4.6).

### 2.5 Net effect on the study question

1. Nothing new changes the baseline (one powered 98 mm wheel plus a hood or passive roller), and nothing argues for a dual-powered default.
2. The extra sources **widen** uncertainty in two directions that matter for unfavourable-side entry:
   - Cd may rise with S (#16, UN shape only). That penalises high backspin.
   - Measured launcher efficiency can be about half of ideal (#25, PR on a different launcher). That lowers exit speed for a given wheel speed.
   Both support the HANDOFF §5 rule that more backspin does not always improve entry.
3. For rim-assisted entry, the extra sources make **μ (sliding)**, not e_t, the controlling contact parameter for backspinning POLLEN on a stiff HIVE lip (#19 theory, #21 PR plus companion).
4. No extra source contains a POLLEN measurement. Everything here is a structure or method input.

---

## 3. Proposed parameter deltas against `research/params_lit.json` (proposals only; not applied)

| Param | Current (params_lit) | Proposed delta | Source and grade | Band effect |
|---|---|---|---|---|
| **Cd** spin term | optional Cd0 + dCd·min(S/0.6, 1), dCd 0–0.15 | Add a sweep variant with **no saturation at S = 0.6**: Cd = Cd0 + d1·S, d1 ≥ 0, swept until Cd at S ~1–2 reaches about 2× Cd0 as a stress case. Keep the current form as the default. | #16 Isomura CFD (UN, shape only: "roughly doubling" from Sp 0.1 to 2) | **Widens** upward (more drag at high backspin) |
| **Cd** per-shot scatter | constant per run | Carry Cd as a per-shot distribution in Monte Carlo, not one value per run. Width to be set from POLLEN shots (no number transfers). | #12 Cross & Lindsey (PR abstract; UN companion) | **Widens** (adds a scatter term) |
| **Cd** ball condition | none | Add a new-vs-scuffed ball factor as an open item, to be measured. | #15 Goodwill (PR abstract, qualitative) | **Widens** (adds a condition axis) |
| **Cl(S)** shape | linear_capped, valid_S_range 0–2 | Add a **monotone saturating** form, e.g. Cl = Cl_max·tanh(c1·S/Cl_max), as an alternative to the hard cap. Extend valid_S_range to about 3 with a flat continuation, because near-apex S reaches about 2.5–2.9 per COMPLETENESS.md. Keep dip_variant and negative_magnus. Use Isomura's equivalent C_L (0.486 at Sp 1, CALC) **only** as an upper shape bound, never as a set. | #14 Mehta (PR abstract, qualitative "cut-off"); #16 (UN shape) | Shape change; **widens** the S range covered |
| **Cl** at very low S | non_magnus_hole_force 0/0.03/0.15 | Make the low-S knuckle force explicitly **stochastic per shot** (random direction normal to v, fixed per shot), including in the lift plane. Magnitude stays on the current non_magnus_hole_force range. | #12 (PR abstract: "significant lift ... at very low spin"); #3 (PR abstract) | **Widens** (direction randomised) |
| **Cl** Re flag | Re note only | Flag trajectory segments with Re > about 4×10⁴ as inside the smooth-sphere transitional band, where the dip variant should be active in sensitivity runs. | consistent with existing Re_range_note; #14 (PR, Re dependence, qualitative) | No numeric change; clarifies |
| **spin_decay** | k 0.005/0.03/0.15, β 0.009/0.02/0.05, **grade B** | **Regrade to D** for POLLEN. Add a note that surface texture can multiply decay several-fold (tennis vs golf "over six times"). Consider raising β high, or adding a surface-dependent multiplier, until measured. No new number for POLLEN. | Haake 2007 via #15 companion (PR abstract); COMPLETENESS.md | **Widens** (higher plausible decay) |
| **I_b / α** | 1.98e-5 (1.73e-5 to 2.36e-5); α 0.6/0.63/0.667 | No change. Add an **independent α check**: in grip-regime bounces, μ_eff vs tan(incidence) has slope α/((1+α)(1+e)). | #21 companion (UN), theory (CALC in the note) | None (adds a cross-check) |
| **e_n** | 0.3/0.5/0.75, grade D | No number change. Model it as **constant per surface across impact angle** at low speed, which is supported. | #21 (PR abstract) | **Narrows** the model form (removes angle dependence) |
| **e_t** | −0.1/0.05/0.25, **grade A** | Keep a [0, 0.2] default for rigid HIVE contacts. Label 0.3 as an upper-bound sensitivity for unidentified ball-shell tangential compliance only. **Regrade to B** for POLLEN, because the tennis values are A but the transfer is a judgement. | #19 (TH); COMPLETENESS.md | Grade **narrows**; range unchanged |
| **mu_impact** | 0.2/0.4/0.8, grade D | No number change. Define it as the **Coulomb μ read from the glancing plateau**, not a single-angle impulse ratio. Mark it as the **priority** contact parameter for backspinning POLLEN, because backspin widens the slide-throughout range. | #19 (TH); #21 (PR abstract + UN companion) | Clarifies definition; priority raised |
| **launcher.v_over_surface_speed** | 0.30/0.42/0.50, grade C | State the reference speed: u_w, or the mean surface speed u_w/2 for a hood. If it is u_w, the #25 η_v ≈ 0.48–0.51 (relative to mean surface speed) maps to v/u_w ≈ 0.24–0.25 (CALC) for a hood. Propose lowering `low` toward **0.24–0.25** in sensitivity runs until POLLEN is measured. FE/no-slip (≈0.95–1.0 of ideal, i.e. 0.5 of u_w) stays the upper bound. | #25 (PR, different launcher; transfer is hypothesis); #22/#23 (UN/TH) | **Widens** downward |
| **launcher.S_exit_hood / S_exit_passive_roller** | 1.0/1.06/1.6; 1.0/1.15/1.67 | No change. Note that the FE spin fraction (about 0.82–0.95 of ideal) is an upper estimate. #25 Fig 5 S values (0.27–1.13, CALC) are **not transferable** (different machine, v_Rx unstated). Spin slip and speed slip may differ, which is directionally consistent with S_exit > 1. | #22/#23 (UN/TH); #25 (PR, qualitative only) | None |
| **launcher.mu_wheel** | 0.5/0.8/1.2, grade D | **Do not** import Wójcicki's 2.05 (or 0.58–2.05): it is not a Coulomb μ. Stays unsourced D. | #17 (TH/bench, interpreted) | None (prevents a wrong widening) |
| **launcher.energy_knockdown_vs_rigid** | 0.55/0.8/1.0 | No change. | — | None |

**Consistency issues inside `research/` (for the owning workflow; not fixed here)**
- RESOLVED 2026-10-30: `params_lit.json` lists `rossmann2007` as "full text read" and that is correct: checks/rossmann2007.md records the later full-text read (Wiffle Cd 0.36-1.05 from its Fig 3). `papers/rossmann2007.md` §2 ("abstract only") predates that read.
- `params_lit.json` and sweep_impact grade Cross 2010 as a measured or PR result. It should be **peer-reviewed theory**.
- `sweeps/sweep_launch.md`: #25 was **not** abstract only, and #17 was **not** blocked. Its "within 40 mm" for #25 should read "SD < 40 mm".
- `COMPLETENESS.md` lists #13, #16, #21 and #24 as unread, and #8, #12, #14, #15, #17, #19, #22, #23 and #25 as partial. All now have notes in `papers_extra/`, with access levels as in §1.

---

## 4. Test-plan additions

These come from Wang 2018, Cross & Lindsey 2013 and Ghaednia 2015, plus #25, #15, #8 and #24. They extend COMPLETENESS.md T0–T6.

Where a number is **derived** for POLLEN in a reader note, it is marked CALC. Those numbers are design choices, not source values.

### 4.1 Camera rig
- **Side camera.** Line of sight perpendicular to the flight plane and parallel to the intended spin axis (#12 companion).
- **Overhead camera** for lateral drift and spin-axis tilt.
- **Optional third oblique camera** to recover the spin-axis tilt directly (#13 used three).
- Treat lateral curvature in the overhead view as evidence of a tilted spin axis. Fit a side-force C_Y as a free parameter.

### 4.2 Fiducials and scene calibration
- **Ball marking.** Two perpendicular great circles in **different colours**, plus one dot, to avoid 90° aliasing. Number the holes near the dot so hole-pattern orientation is recorded.
- **Scene items.**
  - A scale bar of at least 60 cm, filmed in the flight plane and at ±10–20 cm depth. The depth-scale correction follows #12.
  - A checkerboard for lens distortion.
  - A plumb or level reference.
  - Fixed fiducials on the HIVE mock-up.
- **Sync and frame rate.** Use an LED or clap visible to all cameras. Measure the true fps against a stopwatch or LED blinker over at least 10 s (#12 companion).

### 4.3 Frame rates and exposure
- Flight: at least 240 fps (phone slow-motion is acceptable). Keep at least 8 frames per revolution (CALC: at 6 m/s, S = 1 gives about 9 frames per revolution at 240 fps).
- Shutter at most 1/2000 s (CALC: about 3 mm blur at 6 m/s).
- Use continuous lighting, not PWM LED.
- Window length matters more than fps above about 120 fps (CALC). Track at least 0.5 s, i.e. most of the arc.

### 4.4 Fitting method
- Full-trajectory least squares, not two-station Δv.
  - Free parameters: x0, z0, v_x0, v_z0, Cd, Cl, and C_Y from the overhead view.
  - Fit forms per #16 eqs 8–9, with per-shot spin free if spin is not measured.
  - Choose the Cd(S) and Cl(S) order by AIC/BIC.
- **Systematic errors dominate** (CALC in the cross_lindsey2013 note):
  - get scale right to ≤ 0.2 %;
  - level to ≤ 0.1°;
  - use the measured fps;
  - refit with **g free** as a scale/fps check.
- Use an automated sub-pixel centroid, and have a second digitiser or method hand-check a few shots (#12 averaged two digitisers).
- Measure spin at **both ends** of the flight to get decay.

### 4.5 Shot plan and acceptance metric
- At least 20 shots per launcher setting (HANDOFF §5). Record wheel rpm, hood compression or roller preload, ball ID and hole orientation for every shot.
- Include **zero- or low-spin control shots** (#12 knuckle effect).
- Vary S at fixed speed (hood compression or roller preload at fixed wheel speed) to separate S from Re.
- Use **matched spin vs no-spin pairs** at the same exit speed and angle.
- Model acceptance (#13 approach):
  - simulate each shot from its measured initial state;
  - report the **miss distance in mm at the CELL plane** plus the arrival angle, as median and worst case over 20 or more shots.
- Feed per-shot distributions of Cd, Cl and C_Y into the Monte Carlo, not just their means.
- Report SDs, not "within X mm" (#25 convention).

### 4.6 Launcher characterisation (#25 recipe)
- Log the wheel speed from the encoder before and after each shot.
- Image the exit at at least 2000 fps with a short shutter and about 3 px/mm over the first 100–200 mm. #25 stated about 0.05 m/s and about 50 rpm accuracy with that setup.
- Sweep the wheel speed in steps, at least 5 balls per step. Fit v_exit against u_w **through the origin** to get η_v. Curvature or an intercept means slip changes with speed. Get η_w the same way from spin.
- **Feed-orientation test.** Fixed hole-pattern orientations versus random, at least 10 per orientation. Report the direction SD per orientation (#22, #25 posture or asymmetry effect).
- Record the wheel material and durometer and the hood material (#24 lesson: an uncalibrated spin knob gave no usable rpm).
- Test new versus scuffed balls (#15).

### 4.7 Impact filming (HIVE lip and rim, hood)
- Ideal: about 10,000 fps (#21). Use a Hough-transform centroid, which tolerates occlusion by the HIVE lip, and DIC or high-contrast marks for rotation, with about 100 frames either side of contact (#21 companion).
- A 240–960 fps camera will **not** resolve a compression phase of about 3 ms. Use it for in/out states only.
- Bounce tests on HIVE plastic at several incidences, **with and without backspin**:
  - plot μ_eff = Δv_t/Δv_n against tan(incidence);
  - a line through the origin means grip, and α can be read from its slope as a check;
  - read the **Coulomb μ from the glancing plateau** only.
- Measure e_x = −(v_x2 − rω2)/(v_x1 − rω1).
  - If e_x is about 0–0.2, the heavy-cart, e_t ≈ 0 model holds.
  - If e_x is clearly above 0.3 on a rigid HIVE, the shell has tangential compliance that needs its own model (#19).
- Proposed `src/contact.py` regression test, for the owning workflow: with e = 1 and e_t = 0, the stick/slide boundary must equal Cross 2010's closed form (#19).

### 4.8 Measure first, CFD later
If POLLEN CFD is ever attempted, apply #8's six acceptance checks before trusting any output:
1. A smooth sphere reproduces textbook Cd.
2. Cd·U² is not constant across the speed sweep.
3. Pressure drag is positive.
4. A grid-convergence study with at least 3 meshes is reported.
5. Domain-size and blockage sensitivity is reported.
6. The result is compared with measured POLLEN non-spinning Cd before any spinning run is trusted.

---

## 5. Conflicts between RESEARCH_PAPERS.md descriptions and the sources

| # | RESEARCH_PAPERS.md says | Source actually shows | Grade of the correction |
|---|---|---|---|
| 23 | "roller-launch finite element simulation **validated by high-speed camera measurement of exit velocity and spin**" | The validation is a **qualitative visual comparison** of FE frames against high-speed video frames. No measured exit speed or spin values are reported. | UN (conference; full text read) |
| 22 | "finite-element ... followed by CFD-based flight predictions. Particularly useful methodological pipeline" | The FE → exit state → CFD forces → trajectory chain exists, but **no trajectory-vs-measurement comparison** is reported, so the pipeline is not validated end-to-end. The CFD (k-ε RANS) is not validated against tunnel data. It is a template only. | UN/TH |
| 14 | "NASA indexed **conference** review" | It is a journal review in the *Annual Review of Fluid Mechanics*. NTRS files it as conference proceedings but holds **metadata only** (no full text). | access/venue fact |
| 24 | "build/test precedent **demonstrating Magnus trajectories** on a perforated ball" | Curvature was judged only "by naked eye". **No spin, curvature or lift was measured.** The abstract's "5044 rpm" is a flawed model output (ball radius, ω_ball = ω_wheel), not a measurement. | OB |
| 16 | "**computational methodology** for spin-dependent coefficients" | CFD only. Validation is **only proposed** (the paper says it only describes the verification method). Forces are pressure-only, eq. (1) has typos, and the Re span exceeds the range used to argue Re independence. Methodology yes; validated coefficients no. | UN |
| 17 | Hosts listed as the full-issue PDF plus a yadda "alternative hosted paper"; "friction ... drive power" | yadda returned **403** (bot check). The pbc.biaman.pl full issue works, and the paper is on pp. 110–117. Its "μ = 2.05" is a tilt-angle traction, **not a Coulomb friction coefficient**. There is no measured exit speed or spin. | TH (access fact) |
| 13 | "validated flight modeling. Excellent reference for measurement rig" | The abstract supports a 3-camera trajectory and spin reconstruction plus model agreement. The **accuracy metric is undefined** in the abstract, and the rig details (fps, spin method) are **paywalled and unseen**. It can be cited only qualitatively. | PR (abstract only) |
| 25 | "independent spin-axis control as background" (correct). Elsewhere, sweep_launch says "abstract only" and "within 40 mm". | Full text is open. "40 mm" is an **SD**. Top/back max spin is **internally inconsistent** (5500 rpm in Table 1 vs 7000 rpm in the text). It contains a measured η_v ≈ 0.48. | PR |
| 8 | "the thesis itself says mesh errors prevented reliable drag coefficient determination" | **Consistent.** The author says no valid Cd was obtained, and the pressure drag came out negative. No conflict. The "26 ≈ 40 holes" output is not evidence either. | UN |
| 12 | "video-based flight coefficient estimation and distinction between in-flight and wind tunnel results" | Consistent with the abstract. Note that the open TWU companion's launch-speed lower end differs by 1 m/s from the paper abstract. The paper body is unseen. | PR abstract / UN companion |
| 19 | "effect of tangential surface deformation ... transient grip on rebound spin" | Consistent, but it is **model calculation only**: a light spring-cart surface. Over-rolling spin needs a light, springy surface, so a rigid HIVE lip is the heavy-cart case. This is a downstream over-read in sweep_impact, not a RESEARCH_PAPERS error. | TH |
| 21 | "high-speed filmed compression–restitution phases, contact force and effective friction" | Consistent. Caveat: the "effective friction rises with angle" trend is an impulse-ratio (grip) signature, not a changing Coulomb μ, and the model's tangential agreement is not independent evidence. | PR abstract / UN companion |

**Other note (not a RESEARCH_PAPERS.md entry).** The belief that the FTC DECODE team "simulated live with aero" is **not supported** by its code (cuberobot_decode, OB). No aero, Magnus or spin model exists in either repository.

**HANDOFF §5 compliance of this file**
- Target is the HIVE.
- No dual-powered default (#24 is explicitly out of scope).
- No apex-impulse claim.
- No "more backspin always helps": §2.5 says the opposite risk widened.
- No pickleball or tennis coefficient is used as POLLEN.
- v_exit = u/2 is treated as an ideal bound only.
- 70°/6.72 m/s/2 m is not used.
- No 30° tilt is claimed.
- Repeatability: at least 20 shots per setting.
