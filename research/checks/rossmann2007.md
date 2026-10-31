# Fact-check: Rossmann & Rau (2007), "An experimental study of Wiffle ball aerodynamics"

- **Checked against:** the FULL TEXT, 7 pages, Am. J. Phys. 75(12) 1099-1105, read 2026-10-30. The extractor recorded "abstract only", but the Lafayette Digital Repository serves the publisher PDF as a *Public* file, and plain HTTP download raised no CAPTCHA:
  - record page: https://ldr.lafayette.edu/concern/publications/r781wg377
  - file: https://ldr.lafayette.edu/downloads/vm40xr92f (`Rossmann-AmericanJournalofPhysics-vol75-2007.pdf`, 542 kB)
- **What I read:** the text (pdftotext), the page renders, and all 12 embedded figure bitmaps at native 300 ppi. All figure values below were read by eye from those bitmaps, ±1 marker width.
- **Also re-checked:**
  - Crossref, Unpaywall and the AIP landing page (metadata and abstract).
  - Emond et al. arXiv 2409.19000 (PDF, Appendix 7).
  - Lindsey TWU page.
  - Lafayette news 2008 and 2010, Deseret 2010, PopSci 2014.
  - SlideServe student deck.
- **Extraction under review:** research/papers/rossmann2007.md.

**CHECK: 3 confirmed / 4 corrected / 1 dropped / 17 added**

## Bibliographic data and review status
- **Bibliographic data.** Authors Jenn Rossmann and Andrew Rau, Mech. Eng., Lafayette College. Received 21 Dec 2006, accepted 28 Aug 2007. Pages 1099-1105. Crossref online date 2007-11-20. Repository handle 10385/1741. All CONFIRMED.
- **Review status.** "Peer-reviewed journal (pedagogical/undergraduate-research paper)" is CONFIRMED.
- **Quality caveats from the full text:**
  - The co-author was an undergraduate (EXCEL scholar).
  - No figure has error bars, and no repeat runs are shown.
  - The number of balls tested is not stated.
  - There is no blockage correction. The ball is about 4.4 % of the 12 in x 12 in section.
  - The claimed "lift and drag within 10 %, generally 5 %" is contradicted by internal inconsistencies between figures (see A8 and A10).
- **Access level.** Must change from "abstract only" to "full text".

## Ball and method: what the paper actually says (p.1099-1100)
- **Ball:** "A Wiffle ball is 7.2 cm in diameter and weighs 20 g." It has "Eight 3/4 in. oblong holes affect half the surface area ... the other hemisphere is uninterrupted."
  - The extractor's 73 mm [M] is WRONG: use 72 mm and 20 g.
- **Tunnel:** a subsonic 12 in x 12 in open-circuit tunnel. Wind speeds were 10-100 mph, which the paper gives as Re 2e4 to 2e5. Free-stream turbulence was ≤1 %.
  - The extractor says the tunnel range is unknown. That is WRONG: it is known, and it overlaps POLLEN's Re range at 2e4-5e4.
- **Instruments:**
  - An Aerolab strain-gauge sting balance measured the normal and axial forces.
  - "A student-designed instrument capable of measuring forces on a spinning ball" is cited (refs 14 and 15). However, **no spinning-ball data are reported.**
  - Stings were about 0.1d in diameter and 2.5d long, mounted from the side, bottom and rear. The paper says sting placement had minimal influence.
  - Velocity came from a Pitot-static probe, recalibrated before each trial, accurate to within 5 %.
  - Internal flow was measured with a Dwyer PFH hot-wire with a 0.2 s response. That response is too slow for real turbulence, so the reported 7-8 % internal "turbulence" is a lower bound.
- **Angles (Fig. 2):**
  - α = angle of attack (flow vs horizontal).
  - θ = angle from the horizontal to the perforation axis.
  - **β = α + θ = angle between the oncoming flow and the perforation axis.**
  - β = 0 means the holes face upstream. β = 90° means zero AoA with the holes on top. β = 180° means the holes face downstream.
- **Spin:** none measured. The paper says it "may be interesting to include the effects of this spin in future studies." The paper contains no Magnus data for perforated balls. CONFIRMED.

## Equations

| Extractor item | Verdict | Notes |
|---|---|---|
| E1 Re = ρUD/μ | CONFIRMED, now from the paper | The paper's Eq. (1) is Re = ρVd/μ, where V is the free-stream velocity and d the ball diameter. It is no longer only from the student deck. |
| E2 C_D = 2F_D/(ρU²A) | CONFIRMED | Paper Eq. (3): C_{L,D} = F_{L,D} / ((1/2)ρV²A), where A is the frontal area. |
| E3 C_L = 2F_L/(ρU²A) | CONFIRMED | Same Eq. (3). |
| E4 C = C(θ, Re), with θ the hole orientation relative to the flow | CORRECTED (symbol) | In the paper, the flow-relative hole angle is **β**. θ is the angle from the horizontal to the perforation axis, and β = α + θ. Write C_L(β, Re) and C_D(β, Re). |
| E5 F_hole = ½ρAU²C_h ê_h | Extractor's assumption, correctly labelled [A] | Nothing in the paper. |
| ADDED Eq. (2) | from the paper | F_L = F_N cos α − F_A sin α; F_D = F_A cos α + F_N sin α. This converts sting normal and axial force to lift and drag. |
| ADDED spin number | from the paper (p.1100) | Sn = πdω/V, "the ratio of ball rotation speed to bulk air speed". The units of ω are not stated. Sn equals S = ωR/V only if ω is in rev/s. |

## Extractor data points

| # | Item | Verdict | Notes |
|---|---|---|---|
| 1 | C_D ≈ 0.6, "forward-facing Wiffle ball (holes upstream)", Emond App. 7 p.14 | CORRECTED | **Emond's text:** Emond p.14 (Appendix 7, ref [8]) does say: "treating the pickleball as a forward-facing wiffleball ... a constant Cd of approximately 0.6", used at Re ≈ 2.5e4. **"(holes upstream)":** this is the extractor's gloss, not Emond's wording, and **the paper contradicts it**. Holes upstream is β = 0 (Fig. 3), where C_D falls from 0.77 at Re 6e4 to 0.36-0.51 for Re 7.4e4-1.65e5. **Where 0.6 belongs:** it matches β = 90 (holes on top: 0.58-0.63 for Re 8.6e4-1.5e5) and β = 180 at Re ≥ 1.35e5. **Re coverage:** Fig. 3 has no C_D data below Re 4.6e4, so Emond's 0.6 at Re 2.5e4 is an extrapolation. Cite it as "Emond's assumed value", not as a Rossmann measurement. |
| 2 | Non-zero normal force on a non-spinning ball, depending on orientation and Re | CONFIRMED | Abstract, and §III.B-C with Figs. 6-10. Numbers were available after all; see A6-A10. |
| 3 | Normal force = 0 when holes are symmetric about the flow axis (student deck) | CORRECTED | **The deck:** slide 19 only says lift occurs "if the holes ... were not symmetrically distributed". "Zero when symmetric" is an inference. **The paper:** better evidence is in the paper itself. Fig. 6 (Re 1e5) plots C_L = 0.00 at β = 0, but C_L = +0.22 at β = −5° and −0.165 at β = +5°: a near-discontinuity. The authors call β = 0 the orientation "often said to produce a random knuckleball". So zero holds only exactly on axis. |
| 4 | C_D decreases with Re, "roughly exponential", no values (deck) | CORRECTED | **The deck:** it does say "decrease exponentially". **The paper:** it gives values (§III.A): C_D decreases "from a maximum near 1 at the lowest airspeeds tested to approximately 0.4-0.6 at higher Reynolds numbers, depending on the ball orientation". §V gives "approximately 0.4 to 0.6" for Re > 1.4e5 and notes that a smooth sphere is 0.5. See A3-A5 for the figure values. |
| 5 | Lift up to ~0.2 N at ~40 mph (2003 APS-DFD abstract) | DROPPED | Still unverifiable: no APS or ADS page was found. It is not in the 2007 paper. (It is plausible: Fig. 7 gives L/W ≈ 1, about 0.2 N, near Re 9e4, which is about 42 mph. But do not cite it.) |
| 6 | Wiffle game pitch speed 60-80 mph (27-36 m/s), Re ~1.3-1.7e5 | CORRECTED (context) | **The press figure:** Lafayette news 2010 does say "hurled between 60 and 80 miles an hour". The Re arithmetic also holds with the paper's d = 72 mm. **The paper disagrees:** it says "Typical Wiffle ball pitches are expected to be concentrated in the low end of this regime [2e4-2e5]" and "air speeds (up to 45 mph) are of particular interest". **Consequence:** the extractor's framing "Wiffle play is at Re ~1e5, 3-15x POLLEN; tunnel range unknown" is wrong. The tested range includes Re 2e4-5e4, which is POLLEN's 4-10 m/s band. |
| 7 | 8 oblong slots on one hemisphere | CONFIRMED, now from the paper | p.1099: "Eight 3/4 in. oblong holes ... half the surface area ... other hemisphere is uninterrupted." |
| 8 | POLLEN Re 9.6e3 / 2.4e4 / 4.8e4 at 2 / 5 / 10 m/s | CONFIRMED (arithmetic) | With ρ 1.225, μ 1.81e-5 and D 0.071: 9,610 / 24,026 / 48,052. |

Other arithmetic in the extraction, re-run:
- **Drag deceleration at 5 m/s** (m = 0.025, A = 3.959e-3): 0.727 m/s² for C_D 0.3 and 1.455 m/s² for C_D 0.6. Confirmed.
- **Magnus acceleration at C_L 0.2:** 0.485 m/s². Confirmed.
- **C_h 0.05 / 0.1:** 0.121 / 0.242 m/s². Confirmed.
- **S = 1 at 5 m/s:** ω = 140.8 rad/s = 1345 rpm, 22.4 rev/s. Confirmed.

Narrative claims in the extraction, re-checked:
- **"The dominant force depends on speed; internal flow dominates at higher speed" (said to be press only).** The paper itself says this in §V, as the authors' interpretation, not a direct measurement: "The asymmetric boundary layer separation appears to be dominant at lower velocities (Re < 3×10⁴), while the internal flow results in a flow that can be directed opposite the holes for Re > 4×10⁴. In the range of airspeeds between these thresholds, nuances such as ball scuffing may be decisive." The provenance should be upgraded from [S-press] to [P].
- **Lindsey TWU quote.** "vortex formation and lift direction depended strongly on hole orientation" is CONFIRMED verbatim. Note that the paper never measured vortex formation directly. It only infers a trapped vortex.
- **Student deck turbulence values** (0.3 / 0.5 / 6 %), and the fact that the deck names no institution: CONFIRMED.
- **Tunnel location.** "Tunnel in the Acopian basement" is CONFIRMED in Lafayette news 2010, and Lafayette news 2008 says Rau used the College's tunnel. The paper does not name the tunnel's location, and it acknowledges Harvey Mudd College.

## Added data points (missed: the extractor never read the full text)
1. **A1. Ball.** d = 7.2 cm, m = 20 g, eight 3/4 in oblong holes on one hemisphere (p.1099). For POLLEN comparison, d/m and W = 0.196 N.
2. **A2. Test envelope and uncertainty.**
   - Speeds 10-100 mph; the paper gives Re 2e4-2e5. My own conversion: 4.5-44.7 m/s with d = 72 mm, ρ 1.2, μ 1.8e-5.
   - Free-stream turbulence ≤1 %. Stings 0.1d x 2.5d.
   - Velocity within 5 %. Lift and drag "within 10% and generally to within 5%" (§IV).
3. **A3. Fig. 3, C_D, β = 0 (holes upstream):** 0.765 @ Re 6.0e4; 0.51 @ 7.4e4; 0.49 @ 8.6e4; 0.48 @ 9.6e4; 0.43 @ 1.10e5; 0.41 @ 1.21e5; 0.38 @ 1.34e5; 0.375 @ 1.46e5 and 1.57e5; 0.355 @ 1.65e5. This tracks the Gonzalez (1968) non-spinning baseball, which is 0.40-0.55 over the same range.
4. **A4. Fig. 3, C_D, β = 90 (holes on top):** 0.80 @ 7.4e4; 0.60 @ 8.6e4; 0.61 @ 9.6e4; 0.58 @ 1.05e5; 0.605 @ 1.15e5; 0.63 @ 1.21e5; 0.58 @ 1.28e5; 0.60 @ 1.37e5; 0.585 @ 1.46e5; 0.555-0.575 @ 1.54-1.60e5; 0.55 @ 1.66-1.74e5; 0.53 @ 1.81e5.
5. **A5. Fig. 3, C_D, β = 180 (holes downstream):** **1.05 @ Re 4.6e4** (the lowest-Re drag point in the paper); 0.93 @ 8.2e4; 0.80 @ 9.9e4; 0.665 @ 1.17e5; 0.60 @ 1.35e5; 0.545 @ 1.53e5; 0.55 @ 1.72e5; 0.565 @ 1.89e5.
6. **A6. Fig. 4a, drag/weight.**
   - β = 90: D/W ≈ 2.5 @ 7.4e4, 3.6 @ 1.05e5, 5.2 @ 1.21e5, 9.55 @ 1.74e5.
   - β = 270: D/W ≈ 1.6 @ 6.9e4, 3.2 @ 1.05e5, 8.6 @ 1.76e5.
   - My conversion with ρ 1.2, μ 1.8e-5 and W 0.196 N gives C_D ≈ 0.61-0.66 for β = 90, consistent with Fig. 3. β = 270 gives C_D ≈ 0.51-0.61, the same family.
   - The text says little dependence on orientation between holes on top and holes on the side.
7. **A7. Fig. 6, C_L vs β at Re = 1e5:** β −20: +0.36; −15: +0.29; −10: +0.235; −5: +0.22; 0: 0.00; +5: −0.165; +10: −0.23; +15.5: −0.305; +21: −0.43; +25: −0.47; +30: −0.54; +34: −0.605.
   - For |β| ≤ 45° the lift points AWAY from the holes.
   - Note that |C_L| up to 0.6 exceeds the "maximum ... 0.35-0.4" quoted in the text.
8. **A8. Fig. 7, lift/weight vs Re, β = 20 and β = 340.**
   - β = 340: L/W +0.48 @ 7.3e4; 1.03 @ 9.1e4; 1.2 @ 1.08e5; 2.5 @ 1.26e5; 3.0 @ 1.44e5; 5.1 @ 1.62e5; 6.4 @ 1.79e5.
   - β = 20: −0.72 @ 8.2e4; −1.03 @ 1.0e5; −2.07 @ 1.18e5; −1.85 @ 1.36e5; −3.67 @ 1.54e5; −4.77 @ 1.71e5; −5.22 @ 1.90e5.
   - **Internal inconsistency:** converted to coefficients with my assumed air properties, Fig. 7 gives |C_L| ≈ 0.17-0.37. At Re 1e5 that is ≈ 0.19, but Fig. 6 gives ≈ 0.36-0.41 at the same β = ±20° and Re. That is a **factor of about 2 between figures**, much larger than the stated 10 %.
9. **A9. Fig. 8, C_L vs Re at β = 90 (holes on top; lift toward the holes):** 0.437 @ 7.4e4; 0.382 @ 8.6e4; 0.349 @ 9.6e4; 0.364 @ 1.05e5; 0.333 @ 1.15e5; 0.327 @ 1.21e5; 0.315 @ 1.28e5; 0.32 @ 1.37e5 and 1.46e5; 0.302 @ 1.54e5; 0.296 @ 1.60e5; 0.276 @ 1.66e5; 0.263 @ 1.74e5; 0.254 @ 1.81e5.
   - In the figure, C_L *decreases* with Re.
   - The text says the "maximum values ... 0.35-0.4 would be achieved by a baseball at a spin number of approximately 0.5" (Watts & Ferrer). That is a peer-reviewed statement that a hole-asymmetry force can match a Magnus C_L at S ≈ 0.5.
10. **A10. Fig. 10, lateral force/weight, holes at ±90° azimuth.**
    - Holes +L: 0.45 @ Re 5.3e4; 1.1 @ 8.4e4 and 9.8e4; 2.7 @ 1.06e5; 3.4 @ 1.19e5; 4.1 @ 1.29e5; 5.65 @ 1.42e5; 6.1 @ 1.58e5; 3.8 @ 1.75e5; 4.7 @ 1.93e5; 9.5 @ 2.13e5; 10.2 @ 2.22e5.
    - Holes −L: −1.6 @ 8.3e4; −3.4 @ 9.8e4 and 1.05e5; −3.85 @ 1.16e5; −4.3 @ 1.28e5; −3.4 @ 1.42e5; −4.75 @ 1.58e5; −3.6 @ 1.78e5; −4.75 @ 1.92e5; −2.25 @ 2.12e5.
    - The force always points toward the holes.
    - **Converted:** C_side ≈ +0.22 to +0.52 for +L and −0.09 to −0.66 for −L. Mirror-image configurations differ by up to 3x at the same Re (≈ +0.22 vs −0.66 @ 9.8e4), and both differ from the β = 90 lift in Fig. 8 (0.35), which should be the same configuration rotated.
    - The lowest point, C_side ≈ 0.30 at Re 5.3e4 (≈ 11 m/s), is in or near the POLLEN regime.
11. **A11. Fig. 9, C_L vs Re at β = 345°.** This is the ONLY lift data in the POLLEN Re band.
    - Values: −0.13 @ 2.0e4; −0.15 @ 2.75e4; −0.11 @ 3.8e4; −0.10 @ 4.1e4; −0.12 @ 4.4e4; −0.093 @ 5.0e4; −0.005 @ 5.5e4; +0.05 @ 5.9e4; +0.12 @ 6.2e4; +0.145 @ 6.8e4; +0.14 @ 7.05e4.
    - The sign change is at Re ≈ 5.5e4. Below it, the lift points toward the holes, which is the reverse of the high-Re behaviour. It was "observed for some but not all orientations" and not at β = 15°.
12. **A12. Fig. 11, internal air speed at 0.4d, β = 90.** Pairs are free-stream → inside, in m/s: 3.0 → 0.77; 5.3 → 1.12; 7.2 → 1.53; 9.1 → 2.04; 11.0 → 2.57; 12.7 → 3.03; 14.2 → 3.51; 16.5 → 4.04; 18.3 → 4.62.
    - The ratio is 0.21-0.26, which the text gives as "about 25%".
    - **This covers 3-18 m/s, i.e. POLLEN's whole speed range.**
13. **A13. Fig. 12, Vin/Vfs at three depths, β = 90, Re 1.4e4-9e4.**
    - 0.18d: 0.03-0.046.
    - 0.35d: 0.21-0.25 (dips to 0.21 at Re 2.4-3.3e4, then rises).
    - 0.53d: 0.28-0.36 (minimum 0.285 at Re 3.3e4).
    - The internal flow is strongly position-dependent.
14. **A14. Internal turbulence.** About 7-8 % inside the ball versus ≤1 % in the free stream. The authors note this "may have been due to reversing flow or some unsteady flow phenomena" (§III.D).
15. **A15. Regime thresholds (§V, authors' interpretation).**
    - External asymmetric separation dominates at Re < 3e4.
    - Internal flow drives the force opposite the holes at Re > 4e4.
    - Between the two, scuffing "may be decisive".
    - The authors attribute both the larger C_D and the force to a likely trapped internal vortex, citing Rossow 1978 and Katta & Roquemore 1998, which they did not measure. They also say the internal flow "appears to be the cause of an effective spin on the ball".
16. **A16. Fig. 5, fog visualisation at Re = 4e4.**
    - (a) shows the symmetric layout. (b) shows upward wake deflection with an asymmetric hole position, i.e. downward lift.
    - Minor inconsistency: the text cites Fig. 5 as illustrating the ">30 mph" behaviour, but Re 4e4 is ≈ 8.3 m/s ≈ 19 mph.
17. **A17. Holes downstream (90° < β < 270°).** The correlation between lift and hole orientation was "much weaker" than with the holes upstream, which the authors attribute to separated wake flow (§III.B). The paper also states that potential-flow models "yielded results in good agreement", but gives no model and no numbers.

## Impact on the extractor's model implications
- **Drag band [0.30, 0.60] is too narrow.** This is the only peer-reviewed perforated-ball C_D data, and it **rises toward ~0.8-1.05 at the lowest tested Re (4.6-6e4)**. The authors describe a "maximum near 1 at the lowest airspeeds". POLLEN flies at Re 1e4-5e4, below or at the bottom of the measured range.
  - Recommendation: sweep C_D over [0.30, 1.0] until POLLEN is measured.
  - At 5 m/s, C_D = 1.0 gives 2.42 m/s² drag deceleration, about 5x the 0.49 m/s² Magnus acceleration at C_L = 0.2.
  - Caveat: the Wiffle hole area and layout differ from POLLEN's, so this is an analogy and not a POLLEN value.
- **Hole-force sensitivity C_h ∈ {0, 0.05, 0.1}.** In the POLLEN Re band, a one-sided-hole Wiffle shows |C_L| 0.09-0.15 (Fig. 9) and C_side ≈ 0.3 at Re 5.3e4 (Fig. 10).
  - For POLLEN's more uniform hole pattern, 0-0.05 remains a reasonable *assumed* nominal.
  - Add 0.15 as a bounding case.
  - Allow the **sign to depend on Re**. Fig. 9 reverses near Re 5.5e4, and a decelerating ball can cross such a point mid-flight.
- **Internal throughflow.** The internal flow is *measured* at about 20-35 % of free stream for 3-18 m/s (Figs. 11-12), not hypothetical. This supports flagging extra drag and a possible change in C_L(S) for a spinning perforated POLLEN. The spin-pumping effect itself remains untested.
- **Measurement repeatability.** Figs. 6, 7, 8 and 10 disagree with each other by 2-3x on comparable configurations. Treat every Wiffle lift or side coefficient as an order-of-magnitude value (factor about 2), whatever the stated ±10 %.
- **POLLEN rig design.** The paper's method gives a template: a sting of 0.1d x 2.5d, side, bottom and rear sting positions to check interference, and Pitot recalibration before each run. It also gives a warning: at POLLEN speeds the forces are 0.01-0.1 N, so the balance resolution has to be designed for that.
