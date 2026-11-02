# RESEARCH PAPERS & TECHNICAL SOURCES — FTC BIOBUZZ POLLEN MAGNUS-EFFECT SHOOTER

**Source handoff for a second AI engineering agent**  
**Research cutoff:** October 30, 2026  
**Scope:** POLLEN ONLY; 98 mm single powered flywheel, with either stationary curved hood or passive upper roller. The user wants to use significant backspin to bend a high-arcing POLLEN shot into the **upward-facing CELL of the tipping BIOBUZZ HIVE from the unfavorable side**, possibly also leveraging spin-dependent impacts with the opening/rim. This is **not** a generic third-shot-drop pickleball problem, and the user does **not** want a second powered flywheel as the baseline design.

**Read the companion `HANDOFF.md` for full project context.** This is a source bibliography and research mandate, not proof of feasibility.

## READ FIRST — Directly useful to this concept

1. **Crawford Lindsey (2025), “The Physics of Pickleball Aerodynamics and Trajectories: A Revised Model of Lift and Drag.”** Independent experimental technical study, **not identified as peer-reviewed journal article**. https://twu.tennis-warehouse.com/learning_center/pickleball/pickleball_aerodynamics.php  
   **Use:** 86 measured indoor/outdoor pickleball free-flight trajectories, spin-dependent effective lift and drag, apparent asymmetry between topspin/backspin, including reported weak dependence of backspin lift on spin. Reported mean CD ~0.45 for a 26-hole ball and ~0.33 for a 40-hole ball within test settings. **Caution:** these are not FTC POLLEN constants. Spin and translational speed were coupled in the pendulum launcher. The author's proposed explanation involving gravity's effect on boundary-layer flow is a *hypothesis*, not an established mechanism; investigate alternative explanations and uncertainty.

2. **D.G. Steyn et al., “Executing a successful third shot drop in pickleball.”** Peer-reviewed research article; online Aug 12, 2025; journal issue June 2026. https://doi.org/10.1177/17479541251365200 ; preprint https://arxiv.org/abs/2501.00163  
   **Use:** explicit 2D drag/lift trajectory equations and a methodology for estimating coefficients from video; measured about **CD = 0.30 ± 0.02** and empirical **CL = 0.195 S**, with spin parameter **S = ω R / |v|**, for the tested outdoor pickleball regime (about S 0.03–0.3). **Critical:** their third-shot-drop conclusion that spin is secondary applies to *that specific low-angle scenario*, not necessarily to HIVE entry. Do not extrapolate their fitted CL relationship to very high S or directly to POLLEN.

3. **Jenn Rossmann & Andrew Rau (2007), “An experimental study of Wiffle ball aerodynamics.”** *American Journal of Physics* 75, 1099–1105. https://doi.org/10.1119/1.2787013  
   **Use:** experimental effects of perforations, ball orientation, internal airflow, and lift/drag, including curvature even in the absence of spin. **Caution:** Wiffle ball perforation geometry is very different from POLLEN.

4. **Dean Brettle, “Flywheel Shooter Analysis.”** Robotics mathematical technical note / executable Jupyter derivation (not peer-reviewed). https://docs.carlmontrobotics.org/jupyter_notebooks/files/FlywheelShooter.html  
   **Use:** single-powered-flywheel + fixed hood: impulse balance, wheel speed drop, ball translation/spin, rolling/no-slip approximations. Critical ideal result **v_exit = (ω_w,final R_w)/2**, and **ω_ball = v_exit/R_ball** for rolling against a stationary hood. **Do not** confuse initial wheel RPM with final wheel RPM, or rigid rolling constraints with a real compression/slip prediction.

5. **Rafi Pedersen (2026), “Flywheel Shot Analysis: Correction and Extension.”** Team 449 technical whitepaper (not peer-reviewed). https://www.chiefdelphi.com/t/flywheel-shot-analysis-correction-and-extension/520270 ; linked PDF https://robot.mbhs.edu/r/2026wp_flywheel_pdf ; team resource listing https://robot.mbhs.edu/resources  
   **Use:** corrects assumptions in older shooter calculators; extends the analysis to single flywheel + hood, two flywheels, and a **compound hood-plus-roller** arrangement. Very pertinent to user's optional upper roller. **Caution:** author acknowledges ideal no-slip/no-compression/instantaneous event, and that powered-motor intervention during contact is omitted. The short-link PDF may be inaccessible on some browsers; the forum explains the content.

6. **Collin Van Wyk, Lloyd Smith & Bin Lyu (2026), “Characterization of Pickleball Ball Mechanical Behaviour.”** International Sports Engineering Association conference proceeding, May 22, 2026. https://doi.org/10.7273/000008181 ; repository https://rex.libraries.wsu.edu/esploro/outputs/conferenceProceeding/Characterization-of-Pickleball-Ball-Mechanical-Behaviour/99901374808601842  
   **Use:** retrieve PDF for ball material / impact / deformation behavior relevant to hood compression and collisions. **Caution:** available catalog entry confirms the paper, but do not claim numerical results until inspecting the actual PDF. POLLEN material may differ.

## Additional flight / Magnus / perforated-ball literature

7. **Kye Emond, Weiran Sun & Tim B. Swartz (2024), “Pickleball Flight Dynamics.”** Peer-reviewed *International Journal of Racket Sports Science* 6(2), 1–8. https://doi.org/10.30827/ijrss.32618 ; full author PDF https://www.sfu.ca/~tswartz/papers/emond.pdf  
   **Use:** trajectory integration, quadratic drag, wind considerations. **IMPORTANT: omits aerodynamic Magnus lift** and assumes **CD = 0.6** based on Wiffle-ball analogy, so not sufficient for the hypothesized backspin-induced turn.

8. **Isaac Creer (2023), “Computational Fluid Dynamics Analysis of Pickleballs.”** BYU–Idaho BSc senior thesis (not peer-reviewed journal). https://brightspotcdn.byui.edu/f5/ef/bfdce4934c0c97c93cee95c8d33e/isaac-creerf23.pdf  
   **Use:** 0-, 26-, and 40-hole CFD setup, OpenFOAM meshing methodology and failure analysis. **Important:** the thesis itself says mesh errors prevented reliable drag coefficient determination. Do not treat its numerical output as validated.

9. **Wataru Sakai et al. (2016), “Aerodynamics of a Spinning Table Tennis Ball — Lift Crisis.”** JSME conference proceeding. https://doi.org/10.1299/jsmemecj.2016.J2340102  
   **Use:** experimental CL is **not necessarily monotonic** with spin parameter; a lift-collapse regime was observed in their table-tennis ball experiments. Relevant warning against assuming more RPM => proportionally more Magnus force.

10. **Kenichi Ito & Kei Kamijima (2025), “Estimation of Aerodynamic Properties of a Spinning Table Tennis Ball Using Computational Fluid Dynamics Analysis.”** Journal paper. https://doi.org/10.11308/tjsst.17.25  
    **Use:** CFD investigation of drag, lift, Magnus force, and fluid torque across translational velocities **2.5–20 m/s**, and various spin rates. Methodological analogue for POLLEN; not directly transferable coefficients.

11. **Rod Cross & Crawford Lindsey (2017), “Measurements of drag and lift on smooth balls in flight.”** *European Journal of Physics* 38, 044002. https://doi.org/10.1088/1361-6404/aa6e44  
    **Use:** flight-measurement method and nonmonotonic/occasionally reversed Magnus behavior depending on ball properties. Not perforated POLLEN data.

12. **Rod Cross & Crawford Lindsey (2013), “Measurements of drag and lift on tennis balls in flight.”** *Sports Engineering*. https://doi.org/10.1007/s12283-013-0144-9  
    **Use:** video-based flight coefficient estimation and distinction between in-flight and wind tunnel results.

13. **Ping Wang et al. (2018 online / 2019 issue), “Studies and simulations on the flight trajectories of spinning table tennis ball via high-speed camera vision tracking system.”** Journal research article. https://doi.org/10.1177/1754337118815021  
    **Use:** 3-camera tracking, reconstructing ball spin and trajectory, validated flight modeling. Excellent reference for measurement rig.

14. **R. D. Mehta (1985), “Aerodynamics of sports balls.”** NASA indexed conference review. https://ntrs.nasa.gov/search.jsp?R=19850049027  
    **Use:** background on Magnus effect, Reynolds-number dependence, separation, and surface pattern effects.

15. **S. R. Goodwill, S. B. Chin & S. J. Haake (2004), “Aerodynamics of spinning and non-spinning tennis balls.”** *Journal of Wind Engineering and Industrial Aerodynamics*. https://doi.org/10.1016/j.jweia.2004.05.004  
    **Use:** how spin and surface properties affect drag/lift; comparison only.

16. **Y. Isomura et al. (2016), “Aerodynamic Model of Spinning Table Tennis Ball.”** JACC conference proceeding. https://doi.org/10.11511/jacc.59.0_621  
    **Use:** computational methodology for spin-dependent coefficients for table-tennis robot trajectory modeling.

## Launch, friction, ball compression, and impact

17. **Krzysztof Wójcicki, Kazimierz Puciłowski & Zbigniew Kulesza (2011), “Mathematical Analysis for a New Tennis Ball Launcher.”** *Acta Mechanica et Automatica* vol. 5, issue 4. Full-issue PDF https://pbc.biaman.pl/Content/14776/PDF/AM%20vol.5%20no%204.pdf ; alternative hosted paper https://yadda.icm.edu.pl/baztech/download/import/contents/BPB2-0062-0016-httpwww_actawm_pb_edu_plvol5no4wojcickikuleszapucilowskien2010085.pdf  
    **Use:** roller contact geometry, ball deformation, friction and drive power, plus numerical trajectories. **Caution:** two-wheel tennis setup, not direct single-wheel POLLEN coefficient source; PDF hosts may rate-limit or fail.

18. **Rod Cross (2005), “Bounce of a spinning ball near normal incidence.”** *American Journal of Physics*. https://doi.org/10.1119/1.2008299  
    **Use:** why a spinning ball can rebound off a surface in an unexpected direction; relevant to CELL lip/rim contact and spin transfer.

19. **Rod Cross (2010), “Impact of a ball on a surface with tangential compliance.”** *American Journal of Physics*. https://doi.org/10.1119/1.3313455  
    **Use:** effect of tangential surface deformation / friction impulses and transient grip on rebound spin.

20. **T. Allen, S. Haake & S. Goodwill (2010), “Effect of friction on tennis ball impacts.”** Journal article. https://doi.org/10.1243/17543371JSET66  
    **Use:** sliding, grip, overspin, restitution and impact modeling. Transfer mechanics qualitatively; material differs.

21. **Hamid Ghaednia, Ozdes Cermik & Dan B. Marghitu (2015), “Experimental and theoretical study of the oblique impact of a tennis ball with a racket.”** Journal article. https://doi.org/10.1177/1754337114567490  
    **Use:** high-speed filmed compression–restitution phases, contact force and effective friction. Analogue for the hood/rim model.

22. **Shinobu Sakai, Juhachi Oda & Yuichiro Kitagawa (2006), “An Effect of a Baseball having Seam under Roller type Pitching Machine.”** JSME conference proceeding. https://doi.org/10.1299/jsmesports.2006.0_120  
    **Use:** finite-element ball/wheel launch interaction followed by CFD-based flight predictions. Particularly useful *methodological pipeline* from shooter mechanics to aerodynamics.

23. **Shinobu Sakai, Juhachi Oda & Kengo Kawata (2006), “Throw Simulation of a Pitching Machine and the Accuracy Evaluation.”** JSME conference proceeding. https://doi.org/10.1299/jsmemecjo.2006.7.0_125  
    **Use:** roller-launch finite element simulation validated by high-speed camera measurement of exit velocity and spin.

24. **Yufan Wu, Steve Park & Julian Wu (2022), “MEMS 411: Design of a Wiffle Ball Pitching Machine.”** Washington University engineering class final report (not peer-reviewed). https://repository.library.washu.edu/mems411/197/  
    **Use:** build/test precedent demonstrating Magnus trajectories on a perforated ball; their *two*-wheel launcher is not the proposed architecture.

25. **Shinobu Sakai & Yuya Kitade (2017), “Development of launch mechanism in ball shooting machine with four rollers.”** JSME journal article. https://doi.org/10.1299/transjsme.17-00225  
    **Use:** independent spin-axis control as background/alternative reference only. Do **not** change the baseline to a multi-powered-wheel design.

## Primary game specification (not a paper)

- **FIRST 2026–27 BIOBUZZ competition manual, TU07, updated Oct. 29, 2026:** https://ftc-resources.firstinspires.org/ftc/game. Verify HIVE tilt, CELL mouth, rim geometry, field obstructions, legal robot constraints, and coordinates in current official diagrams before any claims of all-field feasibility. Photograph or measure a real HIVE if CAD/field drawings cannot be acquired.

## Required instructions for the next AI agent

**Goal:** Decide quantitatively whether a POLLEN ball launched by a **single 98 mm powered flywheel with stationary curved hood or one optional freely spinning top roller** can generate a backspinning trajectory that enters the currently upward-facing HIVE CELL from either side, and whether a rim-assisted mechanism enlarges the feasible region. Do **not** conflate HIVE with a conventional horizontal basketball hoop, or assume the trajectory is purely ballistic.

1. **Start with geometry:** map actual collision volumes of the HIVE and its two stable orientations, and the ball's finite radius. The goal is entry/retention, not merely reaching a target coordinate.
2. **Use realistic 2D/3D flight ODEs:** `dr/dt = v`, `dv/dt = g + F_D/m + F_M/m`; with `F_D = -(1/2) rho A C_D(Re,S) |v_rel| v_rel`, and Magnus direction set by the spin axis and relative-air velocity. Evolve `dω/dt` if spin decay matters. Use an experimentally plausible range of `C_D` and `C_L`, not a single unvalidated pickleball curve over all spin parameters.
3. **Correct the apex misconception:** `v_z = 0` at a conventional apex, but `v_x` can be nonzero. Spin does not release a new impulse at the apex. Magnus force depends on relative-air speed, spin state, and coefficient regime. Any claimed sudden curl/return must emerge from integrated forces, not a switch at the apex.
4. **Test feasibility systematically:** sample legal shooter heights, field positions, HIVE orientations, launch angles, exit speeds, and spin rates. Detect rim collisions with finite-radius geometry and model tangential / normal restitution and friction. Map successful no-rim and rim-assisted outcomes separately.
5. **Couple launcher and trajectory models:** quantify flywheel speed, wheel inertia, ball compression, normal forces, contact time, slip, coefficient of friction and motor speed drop. Compare fixed hood vs *passive, freely spinning* roller (roller inertia/bearing drag matter). A passive roller may be spun up by the ball, changing grip and imparted spin; a stationary hood and passive roller are NOT equivalent.
6. **Make uncertainty explicit:** manufacturer specs and measured actual POLLEN mass, hole pattern, wall thickness, stiffness, moment of inertia, contact friction; drag/lift law and spin decay; HIVE CAD and ball–rim friction. Do not silently transfer pickleball/table-tennis coefficients to POLLEN.
7. **Propose experiment:** side and overhead high-speed camera with visible ball fiducial; track center x/z and rotations before/after apex, compare matched nonspinning and backspinning shots at the same exit speed & angle, measure rim impacts; obtain error bars. Use slow-motion for launch and impact diagnostics.
8. **Return:** source-backed conclusions, equations with defined signs/units, model assumptions, feasible region, shooter RPM and spin requirements (or impossible bound), and build/test recommendation, labeling ideal results versus measured results.

**Do not assert 'shoot from anywhere on the field' without a full collision and control feasibility map.** The user's observations are that some balls both curved in flight and entered via spin-assisted rim contact; treat those as observations to reproduce and explain, not as proof of a specific mechanism.

**Research limitations:** This is a curated set of 25 relevant works and official sources identified through web research, not a claim to contain every paper ever published on ball aerodynamics or machines. Source dates and links were checked as of the cutoff; access to some PDF hosts may vary.

## Addendum 2026-10-31: sources added by the six effects lenses

Collected from `research/effects/*.md` for `research/MISSING_EFFECTS.md`. Access: **full** = full text read, **abstract**, **secondary** = via another source or repo note, **not read**. None of these give POLLEN coefficients; ball and sphere values from them are analogues only.

### Aerodynamics (aero, numerics lenses)

26. **B. Darbois Texier, C. Cohen, D. Quéré & C. Clanet (2016), "Physics of knuckleballs."** *New J. Phys.* 18, 073027. https://doi.org/10.1088/1367-2630/18/7/073027  
    Knuckle side force and its wavelength; used for the knuckle bracket. Access: full.
27. **F. A. Morrison (2013), "Data correlation for drag coefficient for sphere."** Michigan Tech course handout. https://pages.mtu.edu/~fmorriso/cm310/DataCorrelationsforExaminations2013.pdf  
    Smooth-sphere Cd(Re) fit; use the constant 263000 in both places. Access: full.
28. **T. Kray (2008), dissertation, Univ. Siegen**, https://dspace.ub.uni-siegen.de/handle/ubsi/404 ; **T. Kray, J. Franke & W. Frank (2012)**, *J. Wind Eng. Ind. Aerodyn.* 110.  
    Negative Magnus effect on spinning spheres. Access: thesis record and abstract.
29. **J. Kim, H. Choi, H. Park & J. Y. Yoo (2014), "Inverse Magnus effect on a rotating sphere: when and why."** *J. Fluid Mech.* 754, R2. https://doi.org/10.1017/jfm.2014.428  
    Access: abstract and secondary review. The aero and numerics lenses quote different Re ranges, and the abstract gives neither (flagged in MISSING_EFFECTS.md).
30. **Zhou et al. (2022)**, *Water* 14, 2593. https://doi.org/10.3390/w14172593 . Cited by the aero lens for the lift-crisis and reverse-lift regime.
31. **A. Sareen, K. Hourigan & M. C. Thompson (2024)**, *Int. J. Heat Fluid Flow* 109, 109501. Access: highlights only (PDF unreachable).
32. **P. W. Bearman & J. K. Harvey (1976), "Golf ball aerodynamics."** *Aeronautical Quarterly* 27, 112–122. Access: secondary.
33. **E. Achenbach (1974)**, *J. Fluid Mech.* 65, 113–125. Cited for the direction of roughness effects only; values not retrieved.
34. **Team 254 (2017), Technical binder, pp. 15–16.** https://media.team254.com/2017/09/964207d8-technicalBinder2017.pdf (team document, not peer-reviewed).
35. **K. Muto, M. Tsubokura & N. Oshima (2012)**, LES of a rotating sphere, *Phys. Fluids* 24, 014102. https://doi.org/10.1063/1.3673571 . Smooth sphere at Re 1e4.
36. **G. Constantinescu & K. Squires (2004)**, DES of sphere flow, *Phys. Fluids* 16(5), 1449–1466. https://doi.org/10.1063/1.1688325 (with their 2003 companion paper).
37. **S. Yun, D. Kim & H. Choi (2006)**, LES of sphere flow at Re 3700 and 1e4, *Phys. Fluids* 18.
38. **M. Geier, A. Pasquali & M. Schönherr (2017)**, cumulant LBM, *J. Comput. Phys.* 348, 889–898. https://doi.org/10.1016/j.jcp.2017.07.004
39. **I. Rodríguez et al. (2011)**, DNS of sphere flow at Re 3700, *J. Fluid Mech.* 679, 262–287. https://doi.org/10.1017/jfm.2011.136
40. **E. K. W. Poon et al. (2014)**, rotating-sphere DNS (Re ≤ 1000), *J. Fluid Mech.* 759, 751–781. https://doi.org/10.1017/jfm.2014.570
41. **C. E. Smith, N. Beratlis, E. Balaras, K. Squires & M. Tsunoda (2010)**, golf-ball DNS, *Int. J. Heat Fluid Flow*. Cited for the 1e8–1e9 grid-point cost.

### Environment (env lens)

42. **NASA-TM-X-74335, U.S. Standard Atmosphere 1976.** https://ntrs.nasa.gov/citations/19770009539 . Pressure vs altitude.
43. **A. Picard, R. S. Davis, M. Gläser & K. Fujii (2008), "Revised formula for the density of moist air (CIPM-2007)."** *Metrologia* 45, 149. https://doi.org/10.1088/0026-1394/45/2/004
44. **A. M. Nathan, Denver air-density note.** http://baseball.physics.illinois.edu/ (about 82 % of sea-level density).
45. **FTC event USCOCMP 2026 (Colorado Championship, Golden, CO).** https://ftc-events.firstinspires.org/2026/USCOCMP ; Golden elevation 1730 m from Britannica.
46. **BWF (2019), *Specifications for International Standard Facilities* V1.1, sections 6.3–6.4.** Indoor air-speed limits and the hot-wire survey method.
47. **S. Lestinen et al. (2016)**, arena air speeds, *Int. J. Ventilation* 15(2), 151. https://doi.org/10.1080/14733315.2016.1203622
48. **Stathopoulou et al. (2005)**, jet-ventilated arena, AIVC conference. https://www.aivc.org/sites/default/files/members_area/medias/pdf/Conf/2005/2005053_Stathopoulou.pdf
49. **ASHRAE Standard 55-2013, addenda b and d.** Draft and elevated air-speed limits (ashrae.org).
50. **P. Raftery et al. (2019)**, ceiling-fan air speeds, *Building and Environment*. https://doi.org/10.1016/j.buildenv.2019.03.040 ; data https://doi.org/10.17632/yk4jksgjdc.1
51. **Maxey–Riley equation extended to high Re**, arXiv:2006.16577. Added-mass coefficient 0.5 for a sphere.
52. **R. Willetts & C. G. Murray (1981)**, sphere lift and drag near a wall, *J. Fluid Mech.* 105, 487. https://doi.org/10.1017/S0022112081003303
53. **MDPI *Fluids* 6(6), 211 (2021).** https://www2.mdpi.com/2311-5521/6/6/211 . Near-wall forces on a cylinder (not a sphere).
54. **Pickleball Science (July 2024)**, temperature test of a Franklin X-40 pickleball at −1, 23 and 49 °C (web article; a pickleball, not POLLEN).

### Launch and spin (launch, spin lenses)

55. **M. Norris, S. Breen, R. Anderson & I. Kenny (2012)**, reliability of the Sports Tutor Tennis Cube, 30th ISBS Conference, pp. 381–384. https://ojs.ub.uni-konstanz.de/cpa/article/view/5397 . Access: full.
56. **A. Dittrich et al. (2023), "AIMY."** IEEE ICRA. https://doi.org/10.1109/ICRA48891.2023.10160336 ; arXiv:2210.06048. Access: secondary (`research/sweeps/sweep_launch.md`).
57. **P. Drane et al. (2018), "A Study of the Interaction between Batting Cage Baseballs and Pitching Machine."** *Proceedings* 2(6), 203. https://doi.org/10.3390/proceedings2060203 . Access: not read (method only).
58. **USA Pickleball (2021), *Equipment Standards Manual*, sections 2.D.3–2.D.8.** Copy: https://www.pickleball.ph/uploads/1/2/5/9/125919777/-_official_equipment_standards_manual.pdf (pickleball analogue).
59. **ASTM F1888-09**, compression-displacement of baseballs and softballs. https://store.astm.org/f1888-09.html . Access: not read.
60. **REV Robotics, *DECODE 2025-26 Programming Tips & Tricks*** (previous season). https://docs.revrobotics.com/ftc-kickoff-concepts/decode-2025-26/programming-tips-and-tricks . Used only for the feed-loop tick rate.
61. **goBILDA 5203 Yellow Jacket motor and Pinpoint odometry computer** (vendor pages, vendor claims).
62. **Team 254, FRC-2022-Public README**, https://github.com/Team254/FRC-2022-Public/blob/main/README.md ; **Chief Delphi FRC 971 2016 thread**, https://www.chiefdelphi.com/forums/showthread.php?p=1590553 (forum).
63. **D. M. James & S. J. Haake (2008), "The spin decay of sports balls in flight."** *The Engineering of Sport 7*, vol. 2, 165–170. Access: abstract.
64. **S. J. Haake, S. G. Chadwick, R. J. Dignall, S. R. Goodwill & P. Rose (2007), "Engineering tennis: slowing the game down."** *Sports Engineering* 10.
65. **A. M. Nathan, golf spin-down note and "spin efficiency" (SABR 2018).** http://baseball.physics.illinois.edu/
66. **Chief Delphi threads 374445 ("Hood Compression") and 448624.** https://www.chiefdelphi.com/ (forum).

### Target and contact (target lens)

67. **FIRST, BIOBUZZ Competition Manual TU07.** https://ftc-resources.firstinspires.org/ftc/game/cm-html/BIOBUZZ%20Competition%20Manual%20-%20TU07.htm . Rim-in and TIP rules.
68. **FIRST field documents 2026-27:** Field Acceptance Checklist Rev 26-27.2 (https://ftc-resources.firstinspires.org/ftc/archive/2027/field/field-check), Event Field Setup Guide V1.0, Initial Field Element Assembly Guide V1.0, Field Mitigation Guide 26-27.1.
69. **AndyMark BIOBUZZ scoring elements listing.** https://andymark.com/products/biobuzz-scoring-elements?variant=47194281148588
70. **IPF Equipment Standards Manual 2023 v1.2.** https://theipf.org/assets/userdocs/IPF_Equipment_Standards_Manual2023v1.2.pdf (pickleball analogue).
71. **R. Cross (2014), "Oblique bounce of a rubber ball."** *Exp. Mech.* 54, 1523–1536. https://doi.org/10.1007/s11340-014-9938-3 . Access: abstract. Also R. Cross, bounce notes: https://www.physics.usyd.edu.au/~cross/BOUNCE.htm
72. **Marzouk (2012), LDPE/PC friction.** *Tribologia* 5/2012. https://yadda.icm.edu.pl/baztech/element/bwmeta1.element.baztech-ea3f2d11-04a1-4d71-995a-58472f840ac4 . Access: abstract.

### Numerics and test methods (numerics lens)

73. **E. Hairer, S. P. Nørsett & G. Wanner, *Solving Ordinary Differential Equations I*.** Springer 1993. https://doi.org/10.1007/978-3-540-78862-1 ; and the SciPy `solve_ivp` documentation.
74. **S. Redon, A. Kheddar & S. Coquillart (2002)**, continuous collision detection, *Comput. Graph. Forum* 21(3), 279–287. https://doi.org/10.1111/1467-8659.t01-1-00587
75. **L. F. Shampine & S. Thompson (1991), "Reliable solution of special event location problems for ODEs."** *ACM TOMS* 17(1), 11–25.
76. **C. J. Roy & W. L. Oberkampf (2011)**, aleatory and epistemic uncertainty in verification and validation, *CMAME* 200, 2131–2144.
77. **E. B. Wilson (1927)**, binomial score interval, *JASA* 22, 209–212. https://doi.org/10.1080/01621459.1927.10502953
78. **I. M. Sobol (2001)**, global sensitivity indices, *Math. Comput. Simul.* 55, 271–280. https://doi.org/10.1016/S0378-4754(00)00270-6 ; **A. Saltelli et al. (2008), *Global Sensitivity Analysis: The Primer*,** Wiley.
79. **C. E. Brennen (1982), "A review of added mass and fluid inertial forces."** NCEL CR 82.010.
80. **R. Cross & C. Lindsey (2014)**, tennis-ball drag from two-station video, *Sports Eng.* 17, 89–96. https://doi.org/10.1007/s12283-013-0141-9 (tennis values, not POLLEN).
81. **Tracker video analysis tool** (Open Source Physics), https://opensourcephysics.github.io/tracker-website/ ; and **A. M. Nathan**, baseball lift from motion capture, arXiv:physics/0605041.
