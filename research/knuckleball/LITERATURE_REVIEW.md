# Literature review: knuckling, sphere wakes and perforated balls, applied to BioBuzz POLLEN

Status: review note, 2026-11-05. Searches covered work published up to November 2026.

**Scope.** The nine topics of the task:
- Wiffle and perforated balls;
- pickleball;
- the baseball knuckleball and seam-shifted wakes;
- the soccer knuckleball and volleyball float serve;
- vortex shedding, wake switching and asymmetric separation;
- internal flow through perforated shells;
- torque and spin-axis behaviour;
- Reynolds-number transitions;
- fluid–structure interaction and compressibility.

**Target case.** POLLEN:
- 71.12 mm, 24.95 g;
- 1.78 mm wall;
- 26 round holes of about 10.2 to 11.2 mm, about 13 to 16 % open area;
- launched at 4.5 to 9 m/s, so Re = 2.1e4 to 4.3e4 (Re = ρUD/μ = 4731 U with U in m/s);
- spin parameter S = ωR/U from 0 to 2.

**Verification labels** (used in every entry):

| Label | Meaning |
|---|---|
| DOI verified | DOI resolved on doi.org, Crossref, OpenAlex or the publisher page; title and authors match |
| Full text | the whole paper was read |
| Abstract only | only numbers stated in the abstract are used |
| Metadata only | title, authors and venue confirmed; nothing about the content is used |
| Secondary | numbers quoted from a paper that was read, about a paper that was not |
| UNVERIFIED | could not be confirmed; listed for completeness and kept out of the conclusions |
| (my calculation) / (my estimate) | computed in this review from stated inputs, not taken from a paper |
| (fig.) | value read off a figure |

Some papers appear in both parts below: Rossmann & Rau, the pickleball papers, Darbois Texier et al., and Asai & Kamemoto.
- Part A reads them for **knuckle behaviour**.
- Part B reads them for **wake physics and Reynolds-number regime**.

## Summary table: what transfers to POLLEN

| Source (DOI) | Ball / body | Re | Key finding | Applicability to POLLEN |
|---|---|---|---|---|
| Watts & Sawyer 1975 (10.1119/1.10020) | baseball, wind tunnel | not available (abstract only) | lateral force depends on seam angle; knuckle needs < 1 rev per flight | principle only (low spin); baseball Re is several times higher |
| Borg & Morrissey 2014 (10.1119/1.4885341) | baseball, static seam angles | 1.6e5 | CL up to about 0.25; SD up to 0.5 vs angle | no seams; Re 4 to 8× higher |
| Nathan 2012 (10.1016/j.proeng.2012.04.021) | MLB pitch tracking | 1.5e5 to 1.8e5 (66 to 80 mph, my calculation) | knuckle paths are smooth (rms residual 0.33 in vs 0.30 in) | "break" is unpredictability, not jumps |
| Smith & Smith 2021 (10.1177/1754337120961609) | seam-shifted wake, thrown pitches with PIV | about 2e5 (90 mph, my calculation) | steady, repeatable deflection from separation asymmetry | analogue of the hole-orientation force |
| Issakhanian 2025 (10.1007/s44245-025-00111-9) | rotating fastball, URANS | not in abstract | about 20 % lift variation in rotation | static tests overstate |
| Darbois Texier et al. 2016 (10.1088/1367-2630/18/7/073027) | many balls, model | 1e5 to 4e5 | zigzag length λ = 2πD sqrt(4ρ_b/(3ρ)) | POLLEN λ ≈ 5.4 m; δ ≈ 4 mm at 3 m (my calculation) |
| Hong & Asai 2014 (10.1038/srep05068) | soccer, tunnel and kicks | 2.5e5 to 3.6e5 | side-force SD 0.6 to 3 N at about 2.5 Hz | regime not reached |
| Yamagata et al. 2013 (10.4236/jfcmv.2013.13011) | soccer | near crisis | sign change of the side force near the crisis | regime not reached |
| Reiser et al. 2020 (10.3389/fspor.2020.559277) | volleyball float serve tracking | about 3e5 | residuals 1.4 to 3 cm; anticipation errors 0.2 to 0.5 m | perception vs physics |
| Rossmann & Rau 2007 (10.1119/1.2787013) | Wiffle ball (holes on one half) | 2e4 to 2e5 | CL 0.1 to 0.6 by orientation; internal flow about 25 % U; sign flip near 5.5e4; no early crisis | closest analogue, but POLLEN holes cover the whole shell |
| Steyn et al. (arXiv 2501.00163) | pickleball | 4.7e4 to 6.1e4 | Cd about 0.30; Cl = 0.195 S | different ball; Magnus slope only |
| Emond et al. 2024 (10.30827/ijrss.32618) | pickleball trajectories | about 5e4 | Cd about 0.6 assumed | weak |
| Lin et al. 2026 (10.1007/s12283-026-00577-0) | pickleball, 36 vs 40 holes | about 6.8e4 (my estimate) | hole layout changes the 95 % landing ellipse by 29 % | hole pattern matters at cm level |
| Lindsey 2025 (Tennis Warehouse University, not peer reviewed) | pickleball free flight, 5 to 13 m/s | 2.5e4 to 6.4e4 (my calculation) | Cd 0.45 (26 holes), 0.33 (40 holes); near-zero-spin CL −0.24 / +0.17 | orientation offsets possible |
| Sakamoto & Haniu 1990 (10.1115/1.2909415) | sphere | 800 to 3.7e5 | St 0.19 to 0.2; shedding plane wanders | POLLEN shedding 11 to 27 Hz |
| Norman & McKeon 2011 (10.1007/s00348-011-1161-8) | sphere | subcritical to supercritical (8e4 to 5e5 per Part A) | statistics need ≥ 1000 D/U | a flight is 30 to 55 D/U |
| Norman, Kerrigan & McKeon 2011 (10.1017/S0022112011000164) | sphere + moving 1 %-D element | not in abstract | 1 %-D feature gives lateral force about equal to drag within 4 D/U | holes can pin the wake |
| Grandemange 2013/2014 (10.1017/jfm.2013.83; 10.1007/s00348-014-1838-x) | Ahmed body 9.2e4 (2013); sphere 1.9e4 (2014) | bistable wake, switching about 10³ D/U; symmetry breaking pins it | switching slower than a flight |
| Rigas 2014/2015 (10.1017/jfm.2014.449; 10.1017/jfm.2015.390) | axisymmetric body | about 2e5 | azimuth decorrelates in about 8 D/U | wake wander rate |
| Achenbach 1972/1974 (10.1017/S0022112072000874; 10.1017/S0022112074001285) | smooth and rough spheres | up to 6e6 | crisis at 3.7e5; roughness lowers it | crisis far above POLLEN Re |
| Muto et al. 2012 (10.1063/1.3673571) | rotating sphere LES | 1e4 to 2e5 | CL +0.17 to +0.30 at 1e4; inverse Magnus only near the crisis | normal Magnus expected |
| Kim et al. 2014 (10.1017/jfm.2014.428) | rotating sphere | not in abstract (UNVERIFIED) | inverse Magnus near the critical Re | not in POLLEN range |
| Cicolin et al. 2024 (10.1017/jfm.2024.300) | porous plates | 1.5e4 to 7e4 | shedding persists below porosity 0.2 | POLLEN at 13 to 16 % still sheds |
| Ingard 1953 (10.1121/1.1907235) | Helmholtz resonators | — | end corrections | cavity resonance about 2 kHz (my estimate) |
| Lehmann 2022 (10.1103/PhysRevE.106.015308; 10.3390/computation10060092) | LBM numerics | — | FP16 storage accuracy; Esoteric-Pull | used in `GPU_OPTIMIZATION.md` |

The rows summarise the detailed entries below. Where a row and an entry differ, the entry and its verification label govern.

**Gaps found.**
- No paper measures knuckle (unsteady side) forces of any ball at Re 2e4 to 5e4.
- No unsteady side-force data exist for perforated balls with holes over the whole shell.
- No FSI study exists for hollow perforated sports balls.

The POLLEN conclusions therefore rest on the sphere-wake literature plus this repo's CFD, which is a prediction (see `CFD_TEST_PLAN.md`).

---

# Part A. Knuckle behaviour of sports balls

### 1. Baseball

#### 1.1 Watts & Sawyer 1975

- **Citation**: R. G. Watts and E. Sawyer, "Aerodynamics of a knuckleball", American Journal of Physics 43(11), 960-963 (1975).
- **DOI and verification**: 10.1119/1.10020. Verified via Crossref; the title, authors and venue match. The abstract was also read on the lida.sport-iat.de record.
- **Access**: abstract only. The publisher PDF I could reach is a scanned image with no text layer. The numbers below marked "secondary" are quoted from Nathan 2012 and Darbois Texier 2016, which I read in full.
- **Conditions**: wind tunnel, regulation baseball, lateral force measured as a function of seam orientation; non-spinning and slowly rotating ball. Speed, Re and sampling rate were not available to me.
- **Key numbers**
  - Abstract: the force is lift-like and caused by an asymmetric seam (stitch) position. It changes as the ball rotates slowly.
  - Abstract: on a non-spinning ball, separation can alternate in front of and behind the stitches. This shifts the wake and gives an alternating force.
  - Abstract: a 2D trajectory analysis gives deflections of more than a foot.
  - Abstract, quoted: "An effective knuckleball should be thrown so that it rotates substantially less than once."
  - Secondary (Nathan 2012): the lateral force varies roughly as sin(4 theta) in the four-seam orientation, repeating every 90 degrees, and its peak grows as v^2.
  - Secondary (Nathan 2012): the peak force is about half the ball's weight at 65 mph.
  - Secondary (Nathan 2012): the ideal pitch makes "no more than half a revolution" between pitcher and batter. Zero spin gives a constant force and a smooth curve, not a knuckle.
  - Secondary (Darbois Texier 2016): F_L,0 is about 0.4 N at U = 20.7 m/s. One full zigzag over 18.4 m needs a rotation rate of about 1.8 rad/s and gives a deviation of about 0.06 m.
- **Limitations**:
  - Quasi-steady assumption: the force is taken as a function of instantaneous orientation, measured on a static, mounted ball.
  - A comment by Weaver (1976, DOI 10.1119/1.10267, metadata only) exists.
- **Applicability to the perforated 71 mm ball**:
  - The mechanism needs one dominant raised feature, such as a seam, that moves relative to the separation line as the ball turns slowly.
  - The perforated ball has 26 recessed holes spread over its surface instead of a seam. Whether a hole near the separation line acts like a stitch is not addressed by this work.

#### 1.2 Watts & Ferrer 1987

- **Citation**: R. G. Watts and R. Ferrer, "The lateral force on a spinning sphere: Aerodynamics of a curveball", American Journal of Physics 55(1), 40-44 (1987).
- **DOI and verification**: 10.1119/1.14969. Verified via Crossref.
- **Access**: metadata only. I could not read the content.
- **Conditions and key numbers**: none read.
- **Applicability**: the title places it in the spinning (Magnus) regime, which is relevant to the backspin case (S = 0.5-2), not to the knuckle case. Nothing from it is used below.

#### 1.3 Borg & Morrissey 2014

- **Citation**: J. P. Borg and M. P. Morrissey, "Aerodynamics of the knuckleball pitch: Experimental measurements on slowly rotating baseballs", American Journal of Physics 82(10), 921-927 (2014).
- **DOI and verification**: 10.1119/1.4885341. Verified via Crossref.
- **Access**: full text.
- **Conditions**
  - Tunnel: closed-loop, 2 ft x 2 ft test section (0.372 m^2), turbulence about 0.25 %.
  - Balls: Rawlings MLB, D = 74 mm, seam height 0.722 mm; more than 20 balls used.
  - Speed range considered: 22-38 m/s (Re 1.0-1.8 x 10^5). The main measurements were at Re 1.6 x 10^5.
  - Rig: two-axis force balance with a motor turning the ball at 50 rpm (0.83 Hz); angle known to within plus or minus 0.15 degrees.
  - Sampling: 2000 Hz over 300 rotations, repeated 9 times and ensemble-averaged. Vortex shedding at St 0.2 is about 84 Hz at 31 m/s. The uncertainty in CL is about 0.001.
  - The authors note that half a rotation over 18.4 m corresponds to about 50 rpm for a real pitch.
- **Key numbers**
  - The separation angle varies from 88 to 122 degrees over one rotation (mean 107 degrees). A smooth sphere separates at about 81-82 degrees.
  - Four-seam (4S): a four-period waveform, maximum CL about 0.25, lateral force about zero. The mean CL is about 0.03 when spinning.
  - 4S scatter: the standard deviation of CL is 0.07-0.17 when not spinning and just over 0.2 when spinning. The largest fluctuations occur where the lift changes sign.
  - Two-seam (2S): more structure, with the lift anti-symmetric about 180 degrees and a small lateral force.
  - 2S scatter: the standard deviation is 0.1-0.5 when not spinning and just over 0.5 when spinning, with "significant occurrences where the lift changes sign". The 2S pitch window is 120-300 degrees.
  - Free rotation, 4S: below Re 1.5 x 10^5 the ball settles with a seam at stagnation.
  - Free rotation, 4S: above Re 1.5 x 10^5 it spins up from 50 to about 100 rpm, reaching about 180 rpm above Re 2 x 10^5.
  - Free rotation, 2S: the ball settles at 90 or 270 degrees and oscillates at about 1 Hz with an amplitude of plus or minus 45 degrees, for Re 1.9-4.6 x 10^5.
  - The shear-stress torque is 3.92 x 10^-3 N m, enough to induce about 46 rpm over 0.4 s. The aerodynamic torque on a slowly rotating ball is therefore not negligible.
  - The authors explain a pitch "falling off the table" as the lift changing sign during flight.
- **Limitations stated**:
  - The balls were not mudded.
  - The pedestal mount disturbs the wake.
  - Ensemble averaging hides individual events.
  - A leftward break seen in real pitches is not explained.
- **Applicability to the perforated 71 mm ball**:
  - This is the best quantitative picture of seam-switching: a CL change of order 0.25-0.5 tied to seam angle, with large cycle-to-cycle scatter.
  - It was measured at Re 1.6 x 10^5, three to eight times the target Re, with a raised seam about 1 % of D.
  - The perforated ball's features are holes, not raised seams. Its Re lies below the 1.5 x 10^5 threshold where the authors saw seam effects change character.

#### 1.4 Morrissey 2009 (MS thesis)

- **Citation**: M. P. Morrissey, "The aerodynamics of the knuckleball", MS thesis, Marquette University (2009).
- **Source and access**: epublications.marquette.edu/theses_open/8. Abstract only; the PDF returned 403.
- **Content read**: two-seam ball at 50 rpm studied with a force balance, flow visualisation and hot film. No numbers read beyond those in Borg & Morrissey 2014.
- **Applicability**: background to 1.3 only.

#### 1.5 Nathan 2012

- **Citation**: A. M. Nathan, "Analysis of knuckleball trajectories", Procedia Engineering 34, 116-121 (2012), 9th Conference of the International Sports Engineering Association.
- **DOI and verification**: 10.1016/j.proeng.2012.04.021. Verified via Crossref.
- **Access**: full text.
- **Conditions**
  - Data: PITCHf/x game data from two 60 Hz cameras, about 20 images per camera per pitch, tracked over y = 7-45 ft.
  - Sample: four games in 2011. The detailed game had 278 pitches, 77 of them knuckleballs by one pitcher.
  - Movement statistics: about 2200 and 2600 knuckleballs from two pitchers in the 2010 season.
  - Spin was not measured.
- **Key numbers**
  - Method: each pitch was fitted with a 9-parameter model (drag, constant lift and side force, gravity), and the rms residual was used as a smoothness test.
  - rms residual: knuckleballs 0.326 in, normal pitches 0.295 in (SD about 0.04 in for both). An example knuckleball at 77 mph had an rms of 0.388 in and a maximum residual of 0.5 in.
  - Conclusion: knuckleballs are "as smooth as normal pitches" to within about 0.5 in. No sudden jumps were resolved.
  - Movement is random in both size and direction.
  - Speeds: one pitcher at 66-67 mph; the other in two bands, 73-75 and 75-80 mph. The maximum movement falls as speed rises.
  - Darbois Texier 2016 cite this work for lateral deviations of less than 1.2 cm (0.17 D) relative to a smooth curve.
- **Interpretation**:
  - The impression of erratic flight comes from random, pitch-to-pitch movement.
  - A sudden change in direction would need enormous forces.
  - The system is chaotic in its initial conditions.
- **Limitations**:
  - 60 Hz tracking and the fit model cannot resolve features shorter than about 0.5 in or about 1/60 s.
  - Spin is unknown.
  - A popular version (Baseball Prospectus, 31 Jan 2012) is qualitative only.
- **Applicability to the perforated 71 mm ball**:
  - This is direct evidence for item (d): even the best-known knuckleballs have smooth paths, and the "break" is random movement relative to expectation.
  - The perforated ball would need a measurable random force at all before this question matters.

#### 1.6 Seam-shifted wake (Utah State / B. L. Smith group)

**1.6a Smith & Smith 2021**

- **Citation**: B. L. Smith and A. W. Smith, "Using baseball seams to alter a pitch direction: The seam shifted wake", Proc. IMechE Part P: J. Sports Engineering and Technology 235(1), 21-28 (2021).
- **DOI and verification**: 10.1177/1754337120961609. Verified via Crossref.
- **Access**: abstract only.
- **Conditions**: PIV on seam orientations that give asymmetric boundary-layer separation. Pitches were thrown about 55 ft at about 90 mph with about 1200 rpm on a vertical spin axis, and tracked with a Rapsodo unit.
- **Key numbers (abstract)**:
  - The deflection is significant and repeatable.
  - Larger seams give more deflection.
  - The abstract I read gave no force coefficient.
- **Applicability**:
  - This shows that a fixed surface asymmetry can steer a spinning ball steadily, not erratically.
  - For a perforated ball, the analogue would be a hole pattern that sits asymmetrically relative to the spin axis. No such data exist for perforated balls.

**1.6b Smith, Garrett, Dufour & Francis 2024**

- **Citation**: "How seams alter boundary layer separation points on baseballs", Experiments in Fluids (2024).
- **DOI**: 10.1007/s00348-023-03751-3.
- **Access**: metadata only (OpenAlex). Not used in the conclusions.

**1.6c Garrett & Smith 2022 (dataset)**

- **Citation**: "Seam Shifted Wake in the Magnus and non-Magnus Directions", USU dataset, digitalcommons.usu.edu/all_datasets/191.
- **Access**: snippet only, UNVERIFIED. The snippet says SSW varies with Re for non-rotating balls. Not used in the conclusions.

**1.6d A. W. Smith 2020 USU thesis**

- **DOI**: 10.26076/e0c9-675d.
- **Access**: metadata only.

#### 1.7 Issakhanian 2025

- **Citation**: E. Issakhanian, "Numerical investigation of the aerodynamic force variations during rotation of a pitched baseball", Discover Mechanical Engineering (2025).
- **DOI and verification**: 10.1007/s44245-025-00111-9. Verified via the Semantic Scholar record (title and author match).
- **Access**: abstract only.
- **Conditions**: CFD (URANS, realizable k-epsilon) on a rotating four-seam fastball.
- **Key numbers (abstract)**:
  - Through one rotation, lift varies by about 20 % and drag by about 10 % from the mean.
  - Both are much smaller than the variations found in static-orientation studies.
- **Limitations**: RANS-type turbulence model; a fastball, not a knuckleball.
- **Applicability**: a caution that static, mounted-ball tests (the basis of 1.1 and part of 1.3) may overstate how much the force changes on a rotating ball.

#### 1.8 Other baseball and cricket items

- **Mizota, Kuba & Okajima 1995**: "Erratic Behaviour of Knuckleball", DOI 10.5359/jawe.1995.15. Metadata only.
- **Higuchi & Kiura 2012**: J. Fluids Struct. 32, 65-77. Cited in Borg & Morrissey 2014; I did not verify the DOI. Not used.
- **Shah & Mittal 2023**:
  - Citation: "Is a baseball like knuckleball possible in cricket?", Flow (Cambridge), DOI 10.1017/flo.2023.12. Verified via OpenAlex and DOAJ metadata.
  - Content not read (the publisher host failed). A snippet says the cricket usage of "knuckleball" is a misnomer and that a baseball-like model is proposed. UNVERIFIED; not used.

---

### 2. Unified model across balls

#### 2.1 Darbois Texier, Cohen, Quéré & Clanet 2016

- **Citation**: B. Darbois Texier, C. Cohen, D. Quéré and C. Clanet, "Physics of knuckleballs", New Journal of Physics 18, 073027 (2016).
- **DOI and verification**: 10.1088/1367-2630/18/7/073027. Verified on the IOP page (CC BY).
- **Access**: full text.

**Experiment**

- Launcher: a kicking machine, 0-16 m/s.
- Ball: a beach ball, D = 20 cm, M = 120 g, density ratio rho_b/rho of about 24.
- Spin: less than 0.1 rotation per flight (omega < 0.5 rad/s).
- Tracking: two cameras at 1000 Hz.
- Result: lateral deviations of 0.1-0.4 D, with a zigzag over about 7 m. The model gives about 0.3 D over about 8 m.

**Model**

- The unsteady lift is taken from smooth-sphere lift spectra (Norman & McKeon, Re 8 x 10^4 to 5 x 10^5), applied with random phases.
- The smooth-sphere lift spectrum has three parts:
  - white noise at St < 0.1;
  - a shedding peak at St of about 0.2;
  - power-law decay above St of about 0.3.
- Shedding at St 0.2 is too fast to move a ball with a density ratio of 46-570. The low-frequency part is what deflects the ball.
- Zigzag length: lambda = 2 pi D sqrt(4 rho_b / (3 rho)).
- Deviation: delta / D = C~L (x / lambda)^2, where C~L is the rms of the unsteady lift coefficient.
- The lift variance peaks near Re 3 x 10^5 (the drag crisis). A 30 cm sphere wake-angle test showed the wake asymmetry rising sharply near Re 3 x 10^5.

**Table 2 (as printed)**

| Ball | D | rho_b/rho | lambda | L_shot/lambda | delta_max/D | t/tau |
|---|---|---|---|---|---|---|
| Baseball | 7.0 cm | 672 | 13.1 m | 1.4 | 0.8 | 0.24 |
| Volleyball | 21 cm | 36 | 9.1 m | 2.0 | 2.5 | 0.33 |
| Soccer | 21 cm | 78 | 13.5 m | 2.2 | 1.7 | 0.70 |
| Table tennis | 4 cm | 62 | 2.3 m | 1.2 | 0.5 | 0.07 |

- Drag-crisis speed windows given: soccer 15-25 m/s, volleyball 16-18 m/s, baseball 30-35 m/s.
- Criteria for a knuckle effect: L_shot / lambda > 1, delta_max / D > 1, very low spin, and a launch speed inside the drag-crisis window.

**Limitations stated**

- The model uses smooth-sphere spectra and random phases.
- It agrees with experiment only qualitatively.
- It cannot predict when the zigzags occur.

**Applicability to the perforated 71 mm ball: the most useful framework.** My calculation, using the paper's formula:

- Effective ball density = 0.025 kg / (pi x 0.071^3 / 6 = 1.874 x 10^-4 m^3), which is about 133 kg/m^3. That gives rho_b/rho of about 111.
- lambda = 2 pi x 0.071 x sqrt(4 x 111 / 3), which is about 5.4 m. As a check, the same formula reproduces the paper's 13.1 m for the baseball.
- For a 3 m shot, L/lambda is about 0.55, below the criterion of 1.
- (x/lambda)^2 is about 0.31, so delta is about 0.31 x C~L x 71 mm.
- Even with C~L = 0.2 (borrowed from the baseball scatter in 1.3, an assumption), delta is about 4 mm.
- Re 2-4.7 x 10^4 is far below the drag crisis of any ball in this table.
- Whether the perforation and the internal air change the effective density ratio is not addressed. Air flowing through the holes may move with the shell.

---

### 3. Soccer

#### 3.1 Hong & Asai 2014

- **Citation**: S. Hong and T. Asai, "Effect of panel shape of soccer ball on its flight characteristics", Scientific Reports 4, 5068 (2014).
- **DOI and verification**: 10.1038/srep05068, PMC4038026. Verified via Crossref and Europe PMC.
- **Access**: full text (Europe PMC).
- **Conditions**
  - Tunnel: 1.5 x 1.5 m outlet, turbulence of 0.1 % or less, 7-35 m/s.
  - Balance: six-component sting balance. The sampling rate is not stated.
  - Balls: Brazuca, Cafusa, Jabulani, Teamgeist 2 and Vantaggio, each tested in two orientations (A and B).
  - Kick robot: 30 m/s, under one rotation, goal 25 m away, 20 kicks per ball per orientation, filmed at 300 fps.
- **Key numbers**
  - Critical Re by ball: Brazuca 2.2-2.5 x 10^5; Cafusa 2.4-2.9 x 10^5; Jabulani 3.3-3.6 x 10^5; Teamgeist 2.8-3.0 x 10^5; conventional ball 2.5-2.8 x 10^5.
  - Force SDs at 20 m/s (side / lift): Cafusa B 2.2 / 2.1 N; Jabulani B 2.0 / 3.1 N; Teamgeist about 0.6-0.9 N.
  - The force SDs grew by 103-380 % from 20 to 30 m/s.
  - An FFT of the low-frequency force peaks near 2.5 Hz. My calculation: St = fD/U is about 2.5 x 0.22 / 25, which is about 0.02, inside the white-noise band of 2.1.
  - The SD of the impact point was 0.13-0.68 m.
  - Correlations: horizontal impact SD vs side-force SD, r = 0.62; panel-bond length vs force growth, r = 0.64.
- **Limitations**:
  - One launch condition, n = 20 kicks, five balls.
  - The reference-area formula is stated inconsistently.
- **Applicability**:
  - Surface geometry, here panel seams, shifts the critical Re and changes the size of the unsteady force by a factor of 2-3.
  - All the effects were measured at Re 10^5 and above.

#### 3.2 Asai & Kamemoto 2011

- **Citation**: T. Asai and K. Kamemoto, "Flow structure of knuckling effect in footballs", Journal of Fluids and Structures 27(5-6), 727-733 (2011).
- **DOI and verification**: 10.1016/j.jfluidstructs.2011.03.016. Verified via Crossref. The task listed it as Procedia Eng.; the journal of record is JFS.
- **Access**: content NOT read (the repository was under maintenance and the abstract was not shown).
- **Content**: a snippet says the low-spin kicks were below about 12.56 rad/s. UNVERIFIED; excluded from the conclusions.

#### 3.3 Hong, Chung, Nakayama & Asai 2010

- **Citation**: S. Hong, C. Chung, M. Nakayama and T. Asai, "Unsteady aerodynamic force on a knuckleball in soccer", Procedia Engineering 2(2), 2455-2460 (2010). The volume and pages are as indexed and were not checked against the PDF.
- **DOI and verification**: 10.1016/j.proeng.2010.04.015. Verified via Semantic Scholar and OpenAlex.
- **Access**: abstract only.
- **Conditions**: smoke (titanium tetrachloride) visualisation of a non-spinning kicked ball.
- **Key numbers (abstract)**:
  - Peak vortex-induced lift is about 2.0 N.
  - The mean frequency of the lift variation is about 3.5 Hz.
  - The correlation with the vortex oscillation frequency is r = 0.83.
- **Applicability**: an unsteady force at a few Hz is linked to large-scale wake vortex motion. Same Re regime as 3.1.

#### 3.4 Murakami, Seo, Kondoh & Iwai 2012

- **Citation**: "Wind tunnel measurement and flow visualisation of soccer ball knuckle effect", Sports Engineering (2012). Related: Murakami et al. 2010, Procedia Eng., DOI 10.1016/j.proeng.2010.04.017.
- **DOI**: 10.1007/s12283-012-0085-8.
- **Access**: metadata only (closed). A search snippet says it focused on slow unsteady force variations in the supercritical regime. UNVERIFIED; not used.

#### 3.5 Hiratsuka, Ito, Miyasaka & Konno 2020

- **Citation**: Proc. IMechE Part P (2020).
- **DOI**: 10.1177/1754337119898355.
- **Access**: abstract only; no numbers in it.
- **Content (abstract)**:
  - Stereo PIV shows the knuckle force comes from a jet flow induced by wake vortices.
  - The volume of the panel grooves sets the critical Re and the fluttering.
- **Applicability**: recessed surface features (grooves) control the effect. Holes are recessed features too, but these data are at Re 10^5 and above.

#### 3.6 Goff, Hobson, Asai & Hong 2016

- **Citation**: J. E. Goff, C. M. Hobson, T. Asai and S. Hong, "Wind-tunnel Experiments and Trajectory Analyses for Five Nonspinning Soccer Balls", Procedia Engineering (2016).
- **DOI**: 10.1016/j.proeng.2016.06.185.
- **Access**: abstract only.
- **Conditions**: the same five balls in two orientations, about 7-35 m/s.
- **Key numbers (abstract)**: leaving out the side and lift forces changes the range and the lateral deflection by more than 10 %. The authors call the results preliminary.

#### 3.7 Goff et al. 2017

- **Citation**: "Creating drag and lift curves from soccer trajectories", European Journal of Physics (2017).
- **DOI**: 10.1088/1361-6404/aa6fcd.
- **Access**: metadata only. Not used.

#### 3.8 Yamagata, Nagasawa, Fujisawa & Asai 2013

- **Citation**: T. Yamagata, Y. Nagasawa, N. Fujisawa and T. Asai, "Evaluation of Flight Trajectory and Unsteady Fluid Forces on Kicked Non-Spinning Soccer Ball by Digital Image Analysis", Journal of Flow Control, Measurement & Visualization 1, 87-92 (2013). The page numbers are taken from the PDF.
- **DOI**: 10.4236/jfcmv.2013.13011.
- **Access**: full text (open access).
- **Conditions**:
  - Gymnasium, free flight.
  - Two cameras at 250 Hz covering a 10 x 2 x 4 m volume, 12.5 m from the kicker.
  - Non-spinning motion confirmed from the images.
  - Re 3.0-3.5 x 10^5.
- **Key numbers**:
  - The S-shaped path coincides with a large drop in Cd at x = 15-18 m and with Cs changing sign.
  - On kicks without an S-shape, Cs keeps a negative sign throughout.
  - The authors attribute this to supercritical flow and large-scale vortex shedding.
- **Limitations**: wind-tunnel and free-flight results are hard to compare.
- **Applicability**: free-flight evidence that a force reversal (a switch) can occur within a few metres, but only near the drag crisis.

#### 3.9 Liu, Liang & Cho 2025

- **Citation**: "A polynomial regression model for predicting knuckleball movements in soccer free-kick", Proc. IMechE Part P (2025).
- **DOI**: 10.1177/17543371241311676.
- **Access**: metadata only. Not used.

#### 3.10 Carre (Goff/Carre)

- No Carre paper specifically on knuckling was found and verified in this search. The Goff papers are listed above.

---

### 4. Volleyball float serve

#### 4.1 Reiser, Zentgraf, Kindermann & Künzell 2020

- **Citation**: "An Approach to Quantify the Float Effect of Float Serves in Indoor and Beach Volleyball", Frontiers in Sports and Active Living 2, 559277 (2020).
- **DOI**: 10.3389/fspor.2020.559277.
- **Access**: full text (open access).
- **Conditions**:
  - Five cameras at 100 Hz with a 10 Hz low-pass filter.
  - 94 beach serves and 92 indoor serves.
  - Spin not measured.
  - Release speed 17.79 plus or minus 0.99 m/s (indoor) and 15.15 plus or minus 0.85 m/s (beach).
- **Key numbers**:
  - Mean residual from a quadratic fit: vertical 2.70 cm (beach) and 3.04 cm (indoor); horizontal 1.46 cm and 1.44 cm.
  - Anticipation error (predicted vs actual landing point), beach / indoor: vertical 0.39 / 0.52 m; horizontal 0.17 / 0.26 m.
  - Maximum anticipation error: 1.50 m vertical, 0.99 m horizontal.
  - Release speed explains little: r^2 < 0.033 for the horizontal error.
  - Objective measures explain only part of the subjective "float" ratings.
- **Limitations**: the filter and the 100 Hz rate smooth out short events; spin is unknown.
- **Applicability**:
  - Supports item (d): path residuals of a few cm, measured against a simple fit, add up to tens of cm of landing-point surprise.
  - Perception is only partly explained by the measured deviation.

#### 4.2 Hong & Asai 2026

- **Citation**: "Orientation-dependent aerodynamic response of the Mikasa V200W volleyball under fixed wind-tunnel conditions", Proc. IMechE Part P (published 2026-10-12).
- **DOI**: 10.1177/17543371261495640.
- **Access**: abstract only (Semantic Scholar).
- **Conditions**: six orientations, 7-35 m/s. The float-relevant range is 14-20 m/s (Re 1.9-2.7 x 10^5).
- **Key numbers (abstract)**:
  - Cd,min = 0.150 at 19 m/s (Face B), against 0.177 at 21 m/s (Face A).
  - The lateral-force descriptors vary more between records than drag does.
  - Orientation is not aerodynamically neutral.
- **Applicability**: orientation sets the critical speed. Again, Re is 10^5 and above.

#### 4.3 Other volleyball items (metadata only, not used)

- Hong et al. 2020, Applied Sciences 10, 3256, DOI 10.3390/app10093256.
- Hong, Asai & Weon 2019, Applied Sciences, DOI 10.3390/app9194007.
- Tamaru et al. 2021, Applied Sciences, DOI 10.3390/app11199269.
- Asai et al. 2010, Procedia Eng., DOI 10.1016/j.proeng.2010.04.021.
- Laios et al. 2026, Journal of Human Sport and Exercise, DOI 10.55860/cr051k36 ("Optimal serve distance for greater ball flight deviation").

---

### 5. Spheres and perforated balls (closest analogues)

#### 5.1 Rossmann & Rau 2007 (Wiffle ball)

- **Citation**: J. S. Rossmann and A. Rau, "An experimental study of Wiffle ball aerodynamics", American Journal of Physics 75(12), 1099-1105 (2007).
- **DOI and verification**: 10.1119/1.2787013. Verified via Crossref.
- **Access**: content not read directly.
- **What I could confirm**:
  - Emond et al. 2024 (5.2, read) use a Cd of about 0.6 "treating the pickleball as a forward-facing wiffleball", based on this paper.
  - Press coverage, not read in the original and so UNVERIFIED, describes holes on one hemisphere, a "trapped vortex" effect, and internal versus external flow balancing at 40-60 mph.
- **Applicability**:
  - The Wiffle ball curves because its holes are deliberately on one side.
  - The perforated 71 mm ball has holes spread evenly, so it has no built-in asymmetry of that kind.

#### 5.2 Emond, Sun & Swartz 2024 (pickleball)

- **Citation**: K. Emond, W. Sun and T. B. Swartz, "Pickleball flight dynamics", arXiv:2409.19000 (submitted 19 Sep 2024). Also Int. J. Racket Sports Science, DOI 10.30827/ijrss.32618 (metadata only); preprint DOI 10.51224/srxiv.456.
- **Access**: full text (arXiv HTML).
- **Content**:
  - A trajectory model that ignores spin and assumes a constant Cd of about 0.6 (from 5.1).
  - It quotes the uncertainty in Cd as "roughly +/-0.5 in certain conditions".
  - It states the model's Re as 2.5 x 10^4 or more, close to the target range.
  - It argues qualitatively that holes lower the Re at which Cd levels off.
  - No measurements of lift, side force or unsteady forces.
- **Applicability**: this is the nearest ball (a perforated plastic sphere of about 74 mm), but it offers no knuckle data.

#### 5.3 Lyu, L. Smith & N. Smith 2026 (pickleball)

- **Citation**: B. Lyu, L. Smith and N. Smith, "Aerodynamics and Trajectory Simulation of Pickleballs", ISEA Conference 2026, Washington State University.
- **DOI and verification**: 10.7273/000008164. Resolved to the WSU repository; the title and authors match.
- **Access**: metadata only. The landing page has no abstract or numbers, and the full text is a .docx download I did not read.
- **Applicability**: the most likely source of measured pickleball drag and lift data. Worth reading before any design decision.

#### 5.4 Steyn et al. 2025

- **Content**: a search snippet reports a free-flight pickleball Cd of about 0.30 plus or minus 0.02 (six outdoor trajectories).
- **Access**: snippet only when Part A was written; UNVERIFIED here. Part B §5.3 later identified and read it (arXiv:2501.00163), and that entry governs. It conflicts with the 0.6 in 5.2, so the Cd of a perforated ball is uncertain.

#### 5.5 Other sphere items (metadata only, not used)

- Manzanares-Bercial et al. 2022, "Unsteady aerodynamic lateral force on a sphere under a uniform incoming flow", J. Wind Eng. Ind. Aerodyn. 231, 105205, DOI 10.1016/j.jweia.2022.105205.
- Sudarsana, Vilumbrales-García & Sareen 2024, "On the lift generation over a sphere using asymmetric roughness", Physics of Fluids, DOI 10.1063/5.0241948.

---

### 6. Answers to the four questions

**(a) Rotation threshold**

- Under one rotation per flight (Watts & Sawyer abstract), and ideally no more than about half a rotation (via Nathan).
- About 50 rpm over 18.4 m for a baseball (Borg & Morrissey).
- Under 0.1 rotation for the beach ball (Darbois Texier).
- My calculation for the perforated ball: revolutions per flight n = S L / (pi D). For L = 3 m, n is about 13.4 S.
  - Half a revolution needs S of about 0.04 or less.
  - S = 0.25 gives about 3.4 revolutions, which is well outside every knuckle regime reported.

**(b) Abrupt or smooth**

- The force vs orientation is sharp, with sign changes at critical seam angles (Borg & Morrissey).
- Measured paths are smooth to about 0.3-0.5 in rms at 60 Hz (Nathan), and to a few cm at 100 Hz (Reiser).
- Time scales:
  - Force variations at about 2.5-3.5 Hz (Hong & Asai 2014; Hong et al. 2010).
  - About 1 Hz oscillation in free rotation (Borg & Morrissey).
  - Zigzag time lambda/U of about 0.5 s or more, compared with a convective time D/U of about 10 ms.

**(c) Reynolds number**

- The effect peaks in or near the drag crisis: Re about 1.5-3.6 x 10^5 across the balls (Darbois Texier; Hong & Asai; Borg; Yamagata).
- No source covers knuckle forces at Re 2-5 x 10^4.

**(d) Perception**

- Nathan shows knuckleball paths are as smooth as other pitches; the "dance" is random movement from pitch to pitch.
- Reiser shows anticipation errors of 0.2-0.5 m arising from cm-level residuals, and ratings only partly explained by the measured deviation.

---

### 7. Synthesis (10 lines)

1. Knuckle behaviour in every ball studied needs very low spin: under about 0.5-1 revolution per flight (baseball, about 50 rpm; beach ball under 0.1 revolution). For the perforated ball over 3 m, that means S of about 0.04 or less; S = 0.25 gives about 3.4 revolutions (my calculation).
2. The measured knuckle forces are large only near the drag crisis, at Re 1.5-3.6 x 10^5. The perforated ball at 4-10 m/s sits at Re 2-4.7 x 10^4, 3-15 times lower, where no sports-ball knuckle data exist.
3. Seam-angle switching changes CL by up to about 0.25 (four-seam) and with an SD up to about 0.5 (two-seam) at Re 1.6 x 10^5 (Borg & Morrissey). Rotating-ball CFD finds only about 20 % lift variation (Issakhanian), so static tests may overstate the effect.
4. Soccer balls show side-force SDs of about 0.6-3 N at 20 m/s, varying at about 2.5-3.5 Hz (St about 0.02), and impact scatter of 0.13-0.68 m over 25 m.
5. Darbois Texier's model gives a zigzag length lambda = 2 pi D sqrt(4 rho_b / (3 rho)). For the perforated ball (rho_b/rho about 111), lambda is about 5.4 m (my calculation), so a 3-4 m shot covers well under one wavelength (criterion: more than 1).
6. The predicted deviation, delta of about C~L (x/lambda)^2 D, comes to only about 4 mm at 3 m, even with an assumed C~L of 0.2 (my calculation). A visible knuckle would need a C~L several times larger than any value measured on a sphere.
7. Trajectories are smooth, not jumpy: about 0.33 in rms for knuckleballs against 0.30 in for other pitches (Nathan), and 1.4-3 cm residuals for float serves (Reiser). A "sudden break" is mostly surprise relative to expectation.
8. Perforation is a different mechanism from seams. Asymmetric holes (Wiffle ball) produce a steady curve, while evenly spread holes have no fixed asymmetry. Pickleball Cd is quoted from about 0.3 to about 0.6 (one value UNVERIFIED), and no unsteady side-force data for perforated balls were found.
9. On the evidence found, a true aerodynamic knuckle is unlikely for this ball at 4-10 m/s. Any erratic motion would more likely come from launch scatter, small spin, or hole-orientation effects. All of these are unmeasured and should be tested directly (high-speed video, more than 200 fps, repeated launches).
10. Backspin (S 0.5-2) works in the Magnus regime, where the force is steady. That regime is the controllable option; knuckle-type unpredictability is not supported by the literature at this Re.

---

# Part B. Sphere wakes, perforated shells and Reynolds-number regime

### Topic 1. Subcritical smooth-sphere wake: Strouhal number, modes and unsteady side forces

#### 1.1 Sakamoto & Haniu (1990)

**Citation:** Sakamoto, H., Haniu, H. (1990). A study on vortex shedding from spheres in a uniform flow. *J. Fluids Eng.* 112(4), 386-392.

**DOI:** 10.1115/1.2909415 (verified on Crossref).

**Access:** full text, a scanned PDF hosted at pages.mtu.edu.

**Conditions:**
- Hot-wire measurements in a 30 x 30 cm wind tunnel.
- Dye visualisation in a water channel.
- Sphere diameters 20, 30, 40 and 60 mm.
- Re from 300 to 4e4.
- Free-stream turbulence below 0.2 %.
- Sphere held by a 3 mm rod from the rear.

**Key numbers:**
- **Low-frequency (large-scale shedding) mode:** St rises with Re, then stays constant at 0.19-0.195 for Re > 2e4.
- **Regime IV:** spans 6e3 < Re < 3.7e5.
- **High-frequency (shear-layer) mode:** coexists with the low mode for 800 < Re < 1.5e4. The paper notes that Kim & Durbin give 8e2 < Re < 6e4 for this range. No clear high-mode peak was found above 1.5e4.
- **Wake rotation:** Table 1 records "irregular rotation of the plane containing the wake" from Re of about 800 up to 3.7e5. The text says the point where large-scale vortices are shed "rotates slowly and irregularly" (Fig. 10c, four hot-wires).
- **Rotation time scale:** not given.

**Limitations:**
- Rear support rod.
- Smooth sphere, not spinning.

**Applicability to the ball:** this is the most direct match. It covers Re up to 4e4, which is our range. Expect St of about 0.19 and a shedding plane that wanders irregularly.

#### 1.2 Achenbach (1974a)

**Citation:** Achenbach, E. (1974). Vortex shedding from spheres. *J. Fluid Mech.* 62(2), 209-221.

**DOI:** 10.1017/S0022112074000644 (verified on Crossref).

**Access:** abstract only.

**Conditions:** Re from 400 to 5e6.

**Key numbers:**
- Lower critical Re is 6e3.
- Strong periodic wake fluctuations occur from 6e3 to 3e5.
- No periodic shedding was detected above 3.7e5.
- A phase shift between hot-wires placed on a ring at 75 deg shows that "the vortex separation point rotates around the sphere".

**Limitations:**
- The abstract gives no St value. The St of 0.19 attributed to this paper comes second-hand, cited by Sakamoto & Haniu.

**Applicability to the ball:** confirms that our Re range sits inside the regime of periodic shedding with a rotating separation point.

#### 1.3 Taneda (1978)

**Citation:** Taneda, S. (1978). Visual observations of the flow past a sphere at Reynolds numbers between 10^4 and 10^6. *J. Fluid Mech.* 85(1), 187-192.

**DOI:** 10.1017/S0022112078000580 (verified on Crossref).

**Access:** abstract only.

**Conditions:**
- Re from 1e4 to 1e6.
- Oil-flow, smoke and tuft-grid visualisation.

**Key numbers:**
- For 1e4 < Re < 3.8e5, the wake performs a "progressive wave motion".
- For 3.8e5 to 1e6, the wake forms a pair of streamwise vortices.

**Limitations:** qualitative visualisation only.

**Applicability to the ball:** our Re is in the progressive-wave (helical-like) regime.

#### 1.4 Kim & Durbin (1988)

**Citation:** Kim, K. J., Durbin, P. A. (1988). Observations of the frequencies in a sphere wake and of drag increase by acoustic excitation. *Phys. Fluids* 31(11), 3260-3265.

**DOI:** 10.1063/1.866937 (verified on Crossref).

**Access:** abstract only.

**Conditions:** Re from 500 to 60,000.

**Key numbers:**
- Both the vortex-shedding frequency and the shear-layer instability-wave frequency were measured.
- Acoustic forcing near the shear-layer frequency shortens the recirculation region and raises drag.

**Limitations:** the abstract gives no numeric St values.

**Applicability to the ball:** shows that the wake is receptive to periodic forcing. This is relevant if the cavity or the holes inject unsteady flow.

#### 1.5 Norman & McKeon (2011)

**Citation:** Norman, A. K., McKeon, B. J. (2011). Unsteady force measurements in sphere flow from subcritical to supercritical Reynolds numbers. *Exp. Fluids* 51(5), 1439-1453.

**DOI:** 10.1007/s00348-011-1161-8 (verified on Crossref; Caltech record x4tex-ztr68).

**Access:** abstract only.

**Conditions:**
- Re from 5e4 to 5e5.
- Force balance plus PIV.

**Key numbers:**
- Subcritical lateral-force spectra peak at St of about 0.18. Supercritical spectra have no peak.
- Converged second- and higher-order moments need "at least one thousand dimensionless time units".
- Low-frequency fluctuations explain the apparent mean side force reported by earlier CFD.
- Wake shape is negatively correlated with lateral force.
- A wake structure convects at about 61 % of U.

**Limitations:**
- The lowest Re (5e4) is just above our range.
- Magnitudes of the force coefficients are not in the abstract.

**Applicability to the ball:**
- A flight lasts only about 30-60 D/U, far shorter than the 1000 D/U needed for converged statistics.
- So any single throw sees a random, non-zero "mean" side force. This is the physical basis for knuckle-like scatter.

#### 1.6 Constantinescu & Squires (2004)

**Citation:** Constantinescu, G., Squires, K. (2004). Numerical investigations of flow over a sphere in the subcritical and supercritical regimes. *Phys. Fluids* 16(5), 1449-1466.

**DOI:** 10.1063/1.1688325 (verified on OpenAlex and the university Pure record).

**Access:** abstract only.

**Conditions:** detached-eddy simulation (DES), Re from 1e4 to 1e6.

**Key numbers:**
- **Subcritical:** St of about 0.195, plus a higher Kelvin-Helmholtz (shear-layer) frequency. The wake is helical-like, with hairpin vortices shed at different azimuths.
- **Supercritical:** regular shedding at roughly the same azimuth, with St of about 1.3.

**Limitations:** numerical; smooth sphere.

**Applicability to the ball:** consistent with St of about 0.19 and random shedding azimuth at Re 1e4.

#### 1.7 Rodriguez, Borell, Lehmkuhl, Perez Segarra & Oliva (2011)

**Citation:** Rodriguez, I., Borell, R., Lehmkuhl, O., Perez Segarra, C. D., Oliva, A. (2011). Direct numerical simulation of the flow over a sphere at Re = 3700. *J. Fluid Mech.* 679, 263-287.

**DOI:** 10.1017/jfm.2011.136 (verified on Crossref).

**Access:** abstract only.

**Key numbers:**
- St = 0.215.
- Vortices are shed at random azimuthal locations, giving a helical-like wake.

**Limitations:**
- Re is 5-10 times below our range.
- A low-frequency "bubble pumping" St of about 0.004 appears only in a search snippet: UNVERIFIED.

**Applicability to the ball:** qualitative support for random-azimuth shedding.

#### 1.8 Yun, Kim & Choi (2006)

**Citation:** Yun, G., Kim, D., Choi, H. (2006). Vortical structures behind a sphere at subcritical Reynolds numbers. *Phys. Fluids* 18, 015102.

**DOI:** 10.1063/1.2166454 (verified on Crossref).

**Access:** abstract only.

**Conditions:** large-eddy simulation (LES) at Re 3700 and 1e4.

**Key numbers:**
- A large-scale waviness appears whose plane "changes quasirandomly in time".
- The waviness is stronger at Re 1e4.

**Limitations:** an St of 0.18 at Re 1e4 seen in a related table is UNVERIFIED for this paper.

**Applicability to the ball:** the wake plane drifts randomly at Re 1e4, just below our lower bound.

#### 1.9 Norman, Kerrigan & McKeon (2011)

**Citation:** Norman, A. K., Kerrigan, E. C., McKeon, B. J. (2011). The effect of small-amplitude time-dependent changes to the surface morphology of a sphere. *J. Fluid Mech.* 675, 268-296.

**DOI:** 10.1017/S0022112011000164 (verified on OpenAlex and the Cambridge page).

**Access:** abstract only. Re is not stated in the abstract.

**Conditions:** a roughness element of 1 % of D is moved azimuthally just upstream of laminar separation, at rates up to the shedding frequency.

**Key numbers:**
- The lateral force responds strongly after about tU/D = 4.
- The lateral force can be as large as the drag.
- The forcing produces a counter-rotating helical vortex pair.
- Oscillating the element, or shaping its path, can produce a mean lateral force.

**Limitations:**
- Re is unknown from the abstract.
- The element is tiny compared with our holes.

**Applicability to the ball:**
- High. A surface feature only 1 % of D, moved slowly, steers the side force within about 4 D/U.
- The ball's holes are about 16 % of D. As the ball rotates slowly, they will move the separation line and the side force with them.

#### 1.10 Mueller, Ehrenfried, Bell & Wagner (2019)

**Citation:** Mueller, M., Ehrenfried, K., Bell, J., Wagner, C. (2019). Identification of wake bistability analyzing the side forces on a sphere. 9th European Postgraduate Fluid Dynamics Conference, Ilmenau.

**Identifier:** DLR elib 128041; no DOI.

**Access:** abstract only.

**Key numbers:**
- Re from 6.25e4 to 3.65e5.
- Transient bistable effects appear below 10 Hz in the side-force spectra.

**Limitations:**
- Conference abstract.
- No magnitudes or D/U scaling given.

**Applicability to the ball:** weak; only says that bistable low-frequency side forces exist on spheres.

---

### Topic 2. Wake symmetry breaking, bistability and wake-plane rotation

#### 2.1 Grandemange, Gohlke & Cadot (2014)

**Citation:** Grandemange, M., Gohlke, M., Cadot, O. (2014). Statistical axisymmetry of the turbulent sphere wake. *Exp. Fluids* 55, 1838.

**DOI:** 10.1007/s00348-014-1838-x (verified on Crossref).

**Access:** abstract only.

**Conditions:** sphere at Re 1.9e4, held from upstream.

**Key numbers:**
- Global mode at St = 0.19.
- The wake is axisymmetric on average only because it visits all azimuths equally.
- Breaking the axisymmetry creates preferred wake orientations that repeat with the same periodicity as the perturbation.

**Limitations:** no switching time scale in the abstract.

**Applicability to the ball:**
- Directly relevant, at our lowest Re.
- A 26-hole pattern is a symmetry-breaking perturbation, so the wake should lock into a few preferred orientations fixed to the ball rather than wander freely.

#### 2.2 Grandemange, Gohlke & Cadot (2013)

**Citation:** Grandemange, M., Gohlke, M., Cadot, O. (2013). Turbulent wake past a three-dimensional blunt body. Part 1. Global modes and bi-stability. *J. Fluid Mech.* 722, 51-84.

**DOI:** 10.1017/jfm.2013.83 (verified on Crossref). An open-access copy exists at HAL (hal-01161562).

**Access:** abstract only.

**Conditions:** Ahmed-type body at Re 9.2e4.

**Key numbers:**
- Bistable switching on a long time scale T_l of about 10^3 H/U.
- Short time scale T_s of about 5 H/U, with St of about 0.17.

**Limitations:** the body is not a sphere; H is the body height.

**Applicability to the ball:** gives the order of magnitude of bistable switching, about 1000 body-lengths. A throw lasts only about 50 D/U, so a whole flight usually sees no switch.

#### 2.3 Rigas, Oxlade, Morgans & Morrison (2014)

**Citation:** Rigas, G., Oxlade, A. R., Morgans, A. S., Morrison, J. F. (2014). Low-dimensional dynamics of a turbulent axisymmetric wake. *J. Fluid Mech.* 755, R5.

**DOI:** 10.1017/jfm.2014.449 (verified on Crossref).

**Access:** abstract only.

**Conditions:**
- Blunt axisymmetric body at Re of about 2e5.
- Proper orthogonal decomposition (POD) of base pressure.

**Key numbers:**
- Shedding is in the m = +/-1 azimuthal modes.
- A slow rotation of the symmetry plane restores axisymmetry on average.
- Rotation time scale divided by shedding time scale is of order 100.

**Limitations:**
- Blunt-base body, not a sphere.
- An St of about 0.002 for this motion appears only in a search snippet: UNVERIFIED.

**Applicability to the ball:** with a shedding period of about 5 D/U, the plane rotates on about 500 D/U. That is much longer than a flight.

#### 2.4 Rigas, Morgans, Brackston & Morrison (2015)

**Citation:** Rigas, G., Morgans, A. S., Brackston, R. D., Morrison, J. F. (2015). Diffusive dynamics and stochastic models of turbulent axisymmetric wakes. *J. Fluid Mech.* 778, R2.

**DOI:** 10.1017/jfm.2015.390 (verified on Crossref).

**Access:** full text (open access, CC-BY).

**Conditions:**
- Body: D = 196.5 mm, L/D = 6.48, blunt base.
- U = 15 m/s; Re_D = 1.88e5.
- 64 base pressure taps sampled at 225 Hz; 19,200 s of data.

**Key numbers:**
- Centre of pressure: mean radius about 0.033 D (fig.).
- Radial mean-square displacement (MSD) saturates at about 0.05 s, i.e. about 3.8 D/U.
- Azimuthal MSD grows linearly, which is free diffusion: about 1 rad^2 at 0.1 s (about 7.6 D/U) and about 10 rad^2 at 1 s (fig.; D/U = 0.0131 s).
- Wake orientation is uniformly distributed.
- The dynamics are modelled with a Langevin equation.

**Limitations:** blunt-base body at higher Re than ours.

**Applicability to the ball:**
- The diffusion estimate means the side-force direction decorrelates (about 1 rad) within about 8 D/U, which is about 0.06-0.14 s at 4-10 m/s.
- A 2-4 m flight covers 30-55 D/U, so it sees several direction changes.
- This is the free-diffusion limit. A hole pattern that pins the wake (2.1) would slow the decorrelation.

---

### Topic 3. Drag crisis, roughness and holes

#### 3.1 Achenbach (1972)

**Citation:** Achenbach, E. (1972). Experiments on the flow past spheres at very high Reynolds numbers. *J. Fluid Mech.* 54(3), 565-575.

**DOI:** 10.1017/S0022112072000874 (verified on Crossref).

**Access:** abstract only.

**Conditions:**
- Smooth sphere, Re from 5e4 to 6e6.
- Turbulence about 0.45 %.
- Measurements of drag, pressure distribution and skin friction.

**Key numbers:** no specific crisis Re appears in the abstract. The crisis near 3-3.7e5 comes from 1.2 and 1.3 above.

**Applicability to the ball:** our Re is about ten times below the smooth-sphere drag crisis.

#### 3.2 Achenbach (1974b)

**Citation:** Achenbach, E. (1974). The effects of surface roughness and tunnel blockage on the flow past spheres. *J. Fluid Mech.* 65(1), 113-125.

**DOI:** 10.1017/S0022112074001285 (verified on Crossref).

**Access:** abstract only.

**Conditions:** five surface roughnesses, Re from 5e4 to 6e6.

**Key numbers:**
- Greater roughness lowers the critical Re.
- Transcritical CD rises with roughness to a maximum of about 0.4.
- Subcritical St is the same as for a smooth sphere at every roughness.

**Applicability to the ball:** surface features do not change subcritical St. Whether 11 mm holes trigger an early crisis is answered by the Wiffle data (5.1): they do not.

---

### Topic 4. Rotating spheres and the inverse Magnus effect

#### 4.1 Muto, Tsubokura & Oshima (2012)

**Citation:** Muto, M., Tsubokura, M., Oshima, N. (2012). Negative Magnus lift on a rotating sphere at around the critical Reynolds number. *Phys. Fluids* 24, 014102.

**DOI:** 10.1063/1.3673571 (verified on Crossref).

**Access:** full text (Hokkaido University eprints).

**Conditions:**
- LES at Re 1.0e4, 2.0e5 and 1.14e6.
- Spin parameter Gamma = D omega / U = 2S. Simulated Gamma = 0.2 and 1; Fig. 7 also shows 0.1, 0.5 and 0.8.

**Key numbers:**
- **Re 1e4, non-rotating:** CD about 0.45.
- **Re 1e4, rotating:** CL about +0.17 at Gamma 0.2 and about +0.30 at Gamma 1. CD about 0.47 and 0.66 (fig.). Lift is positive at every spin.
- **Re 2e5:** CL about -0.2 to -0.25 for Gamma 0.1-0.5, i.e. inverse Magnus.
- **Experiments cited by the paper:**
  - Negative lift for Re 6e4-5e5 (Taneda), 4.6e4-1.1e5 (Maccoll) and 9e4 (Davies).
  - Taneda's diagram shows negative lift only near Re 2.5e5, with Gamma < 0.6.
  - The Maccoll and Davies curves dip to about -0.05 to -0.1 near Gamma 0.2 and cross zero near Gamma 0.35-0.4 (fig.).

**Limitations:**
- Only three Re values.
- The Re 1e4 case is laminar.
- The experimental values were re-read from a figure.

**Applicability to the ball:**
- At Re 1e4 normal Magnus lift holds for all spins.
- At about 4.6e4, the top of our range, older experiments show a weak negative lift for S below about 0.2 (Gamma below 0.4).
- So weak inverse Magnus is possible at the fastest launches with slow spin, and absent otherwise. This is for a smooth sphere; holes are untested.

#### 4.2 Kim, Choi, Park & Yoo (2014)

**Citation:** Kim, J., Choi, H., Park, H., Yoo, J. Y. (2014). Inverse Magnus effect on a rotating sphere: when and why. *J. Fluid Mech.* 754, R2.

**DOI:** 10.1017/jfm.2014.428 (verified on Crossref and Semantic Scholar).

**Access:** abstract only.

**Key numbers:**
- Mechanism: the boundary layer on the side moving against the flow becomes turbulent while the other side stays laminar, so separation becomes asymmetric the "wrong" way.
- The paper gives empirical separation formulae in terms of Re and spin ratio.
- The precise Re and spin range is not in the abstract and is UNVERIFIED. A related APS DFD 2011 abstract by the group gives Re 0.6e5-2.6e5 and spin ratio 0-0.5.

**Applicability to the ball:** inverse Magnus needs transition on one side only. That is plausible only near our upper Re, or if the holes trip the boundary layer.

#### 4.3 Kray, Franke & Frank (2012)

**Citation:** Kray, T., Franke, J., Frank, W. (2012). Magnus effect on a rotating sphere at high Reynolds numbers. *J. Wind Eng. Ind. Aerodyn.* 110, 1-9.

**DOI:** 10.1016/j.jweia.2012.07.005 (verified on Crossref and Semantic Scholar).

**Access:** no abstract obtained (publisher refused access).

**Key numbers:** the conference version says negative Magnus occurs over a "wide range" of Re and spin. The exact ranges are UNVERIFIED.

**Applicability to the ball:** none stated; not used.

#### 4.4 Poon, Ooi, Giacobello, Iaccarino & Chung (2014)

**Citation:** Poon, E. K. W., Ooi, A. S. H., Giacobello, M., Iaccarino, G., Chung, D. (2014). Flow past a transversely rotating sphere at Reynolds numbers above the laminar regime. *J. Fluid Mech.* 759, 751-781.

**DOI:** 10.1017/jfm.2014.570 (verified on Crossref).

**Access:** abstract only.

**Conditions:**
- DNS at Re 500-1000.
- Omega* (surface speed / U, equal to S) from 0 to 1.20.

**Key numbers:**
- A new "shear-layer stable foci" regime appears at Re 500 with Omega* = 1.00, and at Re 640-1000 with Omega* >= 0.80.
- Rotation increases the size of force oscillations and lowers their frequency.

**Limitations:** Re far below ours.

**Applicability to the ball:** qualitative only. At S of about 1 or more, rotation reorganises the wake.

---

### Topic 5. Wiffle balls, pickleballs and knuckleballs

#### 5.1 Rossmann & Rau (2007)

**Citation:** Rossmann, J. S., Rau, A. (2007). An experimental study of Wiffle ball aerodynamics. *Am. J. Phys.* 75(12), 1099-1105.

**DOI:** 10.1119/1.2787013 (verified on Crossref).

**Access:** full text (Lafayette Digital Repository).

**Conditions:**
- **Ball:** 7.2 cm, 20 g, with eight 3/4 in oblong holes on one hemisphere.
- **Tunnel:** 12 x 12 in open circuit, strain-gauge sting balance. The sting is about 0.1 d in diameter and 2.5 d long.
- **Ball state:** not spinning.
- **Re:** 2e4-2e5 (10-100 mph).
- **Uncertainty:** about 5-10 %.

**Key numbers:**
- **Drag:**
  - CD is about 1 at the lowest speeds and falls to about 0.4-0.6, depending on orientation, for Re >= 1.4e5.
  - There is no early drag crisis.
- **Lift versus hole orientation beta:**
  - For |beta| <= 45 deg, lift points away from the holes. At larger beta it points toward them.
  - At Re 1e5: CL is about +0.36 at beta = -20 deg and about -0.6 at beta = +34 deg (fig.).
  - beta = 0 is the transition, "often said to produce a random knuckleball".
- **Lift versus Re at fixed orientation:**
  - At beta = 90 deg, CL is 0.44 at Re 7.5e4 and 0.25 at 1.8e5.
  - At beta = 345 deg, CL changes sign at Re of about 5.5e4: about -0.13 to -0.15 at Re 2-3e4, about +0.14 at 7e4.
- **Forces versus weight:**
  - Lift/weight up to about +/-6.
  - Lateral force/weight up to about 10.
  - Drag/weight about 1.5-9.5 for Re 7e4-1.8e5.
- **Internal flow:**
  - About 25 % of U at 0.4 d. At 0.35 d: 0.21-0.25.
  - 0.03-0.05 at 0.18 d.
  - 0.28-0.36 at 0.53 d.
  - Internal turbulence 7-8 %.
- **Mechanism by Re:**
  - Asymmetric boundary-layer separation dominates for Re < 3e4.
  - Internal through-flow dominates for Re > 4e4.

**Limitations:**
- The holes are on one side only. The 26-hole ball is roughly isotropic.
- Non-spinning, with sting interference.

**Applicability to the ball:**
- This is the closest measured analogue: same size, 20 g vs 25 g, and it covers our Re.
- Holes create a body-fixed CL of order 0.1-0.6, and its sign depends on hole orientation and on Re.
- Our Re (1.9e4-4.7e4) straddles the 3e4-5.5e4 band where the mechanism and the lift sign change.
- A ball with evenly spread holes should have a much smaller net asymmetry than this one-sided Wiffle ball. That is an expectation, not a measurement.

#### 5.2 Lindsey (2025), Tennis Warehouse University

**Citation:** Lindsey, C. (2025, 12 May). Pickleball aerodynamics. Tennis Warehouse University web article (twu.tennis-warehouse.com/learning_center/pickleball/pickleball_aerodynamics.php).

**Verification:** not peer-reviewed. The full page was read.

**Conditions:**
- Bungee pendulum launcher.
- Two cameras at 300 fps.
- Trajectory fit with fourth-order Runge-Kutta (RK4).
- 86 trajectories at 5-13 m/s.

**Key numbers:**
- **26-hole indoor ball** (large holes): CD about 0.45 (SD 0.092).
- **40-hole outdoor ball:** CD about 0.33 (SD 0.083).
- **Lift near zero spin:**
  - Topspin: CL about -0.24.
  - Backspin: CL about +0.17.
- **Lift versus spin:** topspin lift grows strongly with S, while backspin lift stays near 0.2.
- **Knuckling:** not discussed.

**Limitations:**
- Not peer-reviewed.
- Large scatter.

**Applicability to the ball:**
- The 26-hole indoor ball is the same class as ours, and CD of about 0.45 is the best estimate available.
- The reported non-zero CL at near-zero spin suggests a hole-induced or orientation-dependent lift of about 0.2.

#### 5.3 Steyn, Mithrush, Koentges, Andrews & Plourde (2024)

**Citation:** Steyn, A., Mithrush, T., Koentges, D., Andrews, A., Plourde, F. (2024). Executing a successful third shot drop in pickleball. arXiv:2501.00163 (posted 30 Dec 2024).

**Verification:** arXiv ID resolved. Full text read.

**Conditions:**
- 40-hole ball.
- Six shots filmed with one camera.
- Re 4.7e4-6.1e4.

**Key numbers:**
- Cd = 0.30 +/- 0.02.
- Cl = 0.195 S for 0.03 < S < 0.3.

**Limitations:**
- Very small sample.
- Not peer-reviewed.

**Applicability to the ball:** positive Magnus lift at small S, at the top of our Re range, for a perforated ball. No inverse Magnus was seen.

#### 5.4 Emond, Sun & Swartz (2024)

**Citation:** Emond, ?, Sun, ?, Swartz, T. (2024). Pickleball flight dynamics. arXiv:2409.19000.

**DOI:** 10.48550/arXiv.2409.19000 (arXiv DOI resolved).

**Access:** abstract only. Author initials were not confirmed.

**Key numbers:** trajectory modelling; playing against the wind is often preferable.

**Limitations:**
- A journal version in the International Journal of Racket Sports Science 6(2) is UNVERIFIED.
- The assumed Cd is quoted inconsistently by other authors.

**Applicability to the ball:** low.

#### 5.5 Lin, Huang, Chen & Zheng (2026)

**Citation:** Lin, Huang, Chen, Zheng (2026). Landing dispersion of 36- and 40-hole pickleballs. *Sports Engineering* 29.

**DOI:** 10.1007/s12283-026-00577-0 (verified on Crossref; published 28 Oct 2026).

**Preprint:** Research Square, DOI 10.21203/rs.3.rs-10389714/v1 (30 Jul 2026, CC-BY).

**Access:** preprint read, pages 1-6.

**Conditions:**
- **Balls:** linear low-density polyethylene (LLDPE), 73.2 mm, 24.5 g, wall 1.55 mm, holes 7.10 mm.
- **Porosity:** 7.98 % for the 40-hole ball, 7.18 % for the 36-hole ball (truncated-icosahedron layout).
- **Launches:** 120 per ball at 50.0 +/- 0.2 km/h, 0 deg launch angle, 1.0 m height.
- **Setting:** outdoors, wind at most 2 m/s.
- **Measurement:** stereo cameras at 300 fps.
- **Re:** about 6.8e4 (my estimate).

**Key numbers:**

| Measure | 40-hole | 36-hole |
| --- | --- | --- |
| SD in X | 37.64 cm | 47.51 cm |
| 95 % landing ellipse | 22,411 cm^2 (29.3 % smaller) | 31,707 cm^2 |
| Ellipse eigenvalue ratio | 1.95 | 2.81 |

**Limitations:**
- Only landing points were measured, not forces.
- Done outdoors.

**Applicability to the ball:**
- Direct evidence that hole layout changes flight-to-flight scatter in near-identical balls at Re just above ours.
- It does not separate random wake forces from launch variation.

#### 5.6 Texier, Cohen, Quere & Clanet (2016)

**Citation:** Texier, B. D., Cohen, C., Quere, D., Clanet, C. (2016). Physics of knuckleballs. *New J. Phys.* 18, 073027.

**DOI:** 10.1088/1367-2630/18/7/073027 (verified on Crossref).

**Access:** full text (open access).

**Conditions:**
- Beach ball: D = 20 cm, 120 g, rho_b/rho = 24.
- Speeds 0-16 m/s; spin omega < 0.5 rad/s.
- Zigzags of 0.1-0.4 D over about 7 m.

**Key numbers:**
- **Zigzag wavelength:** lambda = 2 pi D sqrt(4 rho_b / (3 rho)).
- **When knuckles matter in a game:** only if L_shot/lambda > 1 and delta_max/D > 1.
- **Peak effect:** near the drag crisis (Re about 3e5).
- **Deviation size:** delta scales with 1/(rho_b/rho).
- **Table-tennis row** (Re listed as 3e4): lambda = 2.3 m, L_shot/lambda = 1.2, delta_max/D = 0.5.

**Limitations:** order-of-magnitude scaling only.

**Applicability to the ball (my estimate):**
- rho_b is about 133 kg/m^3 (25 g over the enclosed volume), so rho_b/rho is about 111.
- That gives lambda of about 5.4 m. For a 2-4 m shot, L_shot/lambda is about 0.4-0.7, below the threshold of 1.
- The ball's density ratio is close to table tennis (rho_b/rho about 70, my estimate), and table tennis gives delta_max/D of about 0.5.
- So expect lateral wobble of order 0.1-0.5 D (about 1-4 cm), not a dramatic break, unless the holes add a body-fixed lift (5.1).

#### 5.7 Asai & Kamemoto (2011): UNVERIFIED

**Citation:** Asai, T., Kamemoto, K. (2011). Flow structure of knuckling effect in footballs. *J. Fluids Struct.* 27, 727-733.

**Status:**
- The DOI was not verified, and the open-access copy returned 503.
- A search snippet mentions non-axisymmetric vortex loops and a rotating separation point.

**Use:** not used in the conclusions.

---

### Topic 6. Porous and permeable bodies, bleed, and Helmholtz resonance

#### 6.1 Cicolin, Chellini, Usherwood, Ganapathisubramani & Castro (2024)

**Citation:** Cicolin, M. M., Chellini, S., Usherwood, B., Ganapathisubramani, B., Castro, I. P. (2024). Vortex shedding behind porous flat plates normal to the flow. *J. Fluid Mech.* 985, A40.

**DOI:** 10.1017/jfm.2024.300 (verified on Crossref).

**Access:** abstract read (the paper is open access).

**Conditions:** Re from 15,000 to 70,000.

**Key numbers:**
- Plates with porosity beta < 0.2 shed Karman vortices.
- Plates with beta > 0.3 do not.
- Shedding is intermittent for beta between 0.2 and 0.3.
- These thresholds do not depend on Re.

**Limitations:**
- These are flat plates, not spheres, and the analogy to a sphere is untested.

**Applicability to the ball:**
- The ball's open area of 13-16 % is below 0.2, so normal shedding is expected.
- Bleed through the holes should weaken, but not suppress, the wake.

#### 6.2 Porous spheres

**Status:** no peer-reviewed porous- or perforated-sphere wake paper was verified.

Leads seen only in search results (UNVERIFIED, not used):
- Cummins et al. (2017), on porous discs or spheres.
- Seol, Kim & Kim (2024), on porous square cylinders, *J. Fluid Mech.* 985, A29.

#### 6.3 Ingard (1953) and a Helmholtz estimate for the ball

**Citation:** Ingard, U. (1953). On the theory and design of acoustic resonators. *J. Acoust. Soc. Am.* 25(6), 1037-1061.

**DOI:** 10.1121/1.1907235 (verified on Crossref).

**Access:** content not read. Cited here as the standard reference for neck end corrections.

**Lumped formula (standard textbook form):** f_H = (c / 2 pi) * sqrt( n A / (V L_eff) ), with L_eff = t + about 1.7 a. Here n is the number of holes, A the area of one hole, V the cavity volume, t the wall thickness and a the hole radius.

**Estimate for the ball (my estimate):**

| Quantity | Value |
| --- | --- |
| Cavity volume V | about 1.62e-4 m^3 (inner radius 33.8 mm) |
| Area per hole A | 9.85e-5 m^2 |
| Total hole area nA | 2.56e-3 m^2 |
| Effective neck length L_eff | about 11.3 mm |
| Helmholtz frequency f_H | about 2 kHz |

**Caveats:**
- kD is about 2.6, so the cavity is not acoustically compact.
- The holes interact with each other.
- The lumped model is therefore only order-of-magnitude.

**Comparison with shedding:** wake shedding is at 0.19 U/D, about 11-27 Hz for 4-10 m/s. That is about 100 times below f_H, so cavity resonance should not couple to the wake.

---

### Topic 7. Thin-shell fluid-structure interaction

No study was found of fluid-structure interaction or shell deformation for a hollow perforated plastic ball in flight. One search returned only shock-loaded or buckling shell papers.

My estimate: dynamic pressure at 10 m/s is about 60 Pa, which is negligible for a 1.78 mm polyethylene shell. Aeroelastic effects are therefore not expected.

---

### Synthesis (applies to the 71 mm perforated ball at Re 1.9e4-4.7e4, S 0-2)

1. **Regime:** Re of 1.9e4-4.7e4 is subcritical, about 7-15 times below the smooth-sphere drag crisis (3-3.7e5; Achenbach, Taneda). The Wiffle ball shows no early crisis up to 2e5 (Rossmann & Rau).
2. **Shedding frequency:** the large-scale mode has St of 0.19-0.195 (Sakamoto & Haniu; Grandemange 2014 at Re 1.9e4; Constantinescu & Squires), which gives 11-27 Hz at 4-10 m/s. Lateral-force spectra peak at St of about 0.18 (Norman & McKeon).
3. **Random side force:** the shedding plane rotates irregularly at every Re in our range (Sakamoto & Haniu; Achenbach; Yun et al.). Side-force statistics need at least 1000 D/U to converge (Norman & McKeon), but a 2-4 m flight lasts only 30-55 D/U. Each throw therefore samples a random, non-zero "mean" side force.
4. **How fast the side force changes direction:**
   - Free-diffusion limit: azimuth decorrelates by about 1 rad^2 in about 8 D/U (Rigas 2015, blunt body).
   - Slow-rotation and bistable limit: about 100 shedding periods, or about 10^3 D/U (Rigas 2014; Grandemange 2013).
   - So within one flight the direction either drifts several times or stays essentially fixed. The ball sits between these limits.
5. **Hole pattern pins the wake:** a symmetry-breaking perturbation gives the sphere wake preferred, body-fixed orientations (Grandemange 2014). A 1 % D surface element can drive a lateral force as large as the drag within about 4 D/U (Norman, Kerrigan & McKeon). Holes of about 16 % D should therefore dominate wake orientation.
6. **Body-fixed lift from holes:**
   - Perforated balls show orientation-dependent CL of 0.1-0.6 (Rossmann & Rau).
   - The sign flips at the hole-alignment angle beta = 0, and with Re near 5.5e4.
   - The controlling mechanism shifts from boundary-layer separation (below 3e4) to internal through-flow (above 4e4), which is exactly our range.
   - The 26-hole ball has less net asymmetry, but slow tumbling sweeps its residual body-fixed lift around.
7. **Drag:** CD is about 0.45 for 26-hole pickleballs (Lindsey 2025) and about 0.45 for a smooth sphere at Re 1e4 (Muto). Spin of Gamma = 1 raises CD to about 0.66 (Muto).
8. **Magnus lift:** normal Magnus lift is expected for S above about 0.03: Cl = 0.195 S at Re 4.7e4-6.1e4 (Steyn), and CL of +0.17 to +0.30 for Gamma 0.2-1 at Re 1e4 (Muto). Weak inverse Magnus (CL about -0.05 to -0.1) has been reported only near Re 4.6e4 with Gamma below about 0.4 (Maccoll, via Muto). It is therefore marginal and only at the fastest, low-spin shots.
9. **Knuckle size:** Texier scaling with rho_b/rho of about 111 gives lambda of about 5.4 m and L_shot/lambda of 0.4-0.7. The density ratio is similar to table tennis, which gives delta_max/D of about 0.5. Expect random lateral deviation of a few cm, not a dramatic break. A 36- vs 40-hole layout changed the landing-ellipse area by 29 % (Lin 2026).
10. **Effects that can be neglected:**
    - Porosity of 13-16 % is below the 0.2 shedding-suppression threshold (Cicolin, flat-plate analogy), so the wake still sheds.
    - Cavity Helmholtz resonance at about 2 kHz is about 100 times above shedding (my estimate), so they are decoupled.
    - Shell deformation is negligible at about 60 Pa dynamic pressure (my estimate; no FSI literature found).
    - A non-spinning or slowly tumbling launch maximises knuckle-type behaviour; S above about 0.1 replaces it with deterministic Magnus curvature.
