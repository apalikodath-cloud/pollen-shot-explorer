# Fact-check: Van Wyk, Smith & Lyu (2026), Characterization of Pickleball Ball Mechanical Behaviour

- Checker: independent re-read of the full text. PDF from the WSU Research Exchange, 5 pages: 4 pages of content and 1 page of references. Checked 2026-10-30.
- Sources re-opened:
  - https://doi.org/10.7273/000008181 (302 redirect to the next link)
  - https://rex.libraries.wsu.edu/esploro/outputs/conferenceProceeding/99901374808601842
  - The PDF download linked in the extraction
  - https://events.wsu.edu/isea2026/call-for-papers/ (review process)
  - https://ssl.wsu.edu/?p=177 (WSU Sports Science Lab page with the dynamic stiffness (DS) derivation)
- Method:
  - Text extracted with pdftotext.
  - Figures rendered at 400 dpi and digitized by pixel, with axes calibrated from the gridlines. Accuracy is about +/-0.002 on Cl/Cd, +/-3 lbf and +/-0.003 in.
  - Fig. 5 markers and error-bar caps were found by colour and dark-pixel detection.
  - Fig. 4 loading and unloading envelopes were traced, and their areas computed by trapezoid integration.

## CHECK: 19 confirmed / 9 corrected / 0 dropped / 9 added

### Confirmed (within digitizing tolerance)

1. **Citation.** Authors, title, conference (ISEA 2026, The Engineering of Sport 16, WSU Pullman, 1-4 June 2026), DOI and the Selkirk Sport funding are all correct. The repository lists the date as 2026-05-22.
2. **Eq. 1, de = 1 - COR^2.** Verbatim. The paper says pickleballs "lose about 96% of their energy".
3. **a = F/m, integrated twice to give x.** Stated in words on p.3.
4. **Test setup.** 60 +/- 1 mph, two light gates in, three 500 lb load cells, flat steel plate on a rigid wall, 12 balls x 4 sites at 90 deg along the seam/centreline x 3 good shots = 144.
5. **COR mean ~0.20.** p.2 text; Fig. 2 top (mode bin 0.200 holds 25 impacts).
6. **COR histogram range.** Nonzero bins run from 0.165 to 0.255 (a single outlier at 0.255). The bin-edge convention is not stated.
7. **COR CoV.** Within ball 7.5% (baseball 1.2%); between balls 3.6% (9-ball baseball supply 0.6%). Both p.2.
8. **DS mean.** 500 lb/in = 87.6 kN/m (p.2).
9. **DS histogram range.** Nonzero bins run from 225 to 775 lb/in (single outliers at both ends). The bulk is 300-675.
10. **DS CoV.** Within ball 18% (baseball under 2%); between balls 5.3% (baseball 8.0%).
11. **Deformation and contact.** Deformation "approximately 0.4 in or ~1/4 of its radius", p.3. Impact duration about 1.5 ms (p.3). Shape recovery about 3 ms, with the ball retaining a flattened surface (p.3).
12. **Durability and temperature.** COR shows "little evidence of change after 200 impacts", and there is "no evidence of warming". Both are qualitative, p.3.
13. **Fig. 4 peak force.** Re-digitized at 337 lbf (1.50 kN) at x = 0.398 in. Maximum x = 0.416 in.
14. **Fig. 4 loading branch.** Every point matches within +/-5 lbf except x = 0.05 in (see correction 6). Re-digitized:

    | x (in) | F (lbf) |
    |---|---|
    | 0.025 | 33 |
    | 0.075 | 113 |
    | 0.10 | 135 |
    | 0.125 | 147 |
    | 0.15 | 147 |
    | 0.175 | 158 |
    | 0.20 | 185 |
    | 0.225 | 209 |
    | 0.25 | 220 |
    | 0.275 | 228 |
    | 0.30 | 268 |
    | 0.325 | 304 |
    | 0.35 | 319 |
    | 0.375 | 309 |
    | 0.40 | 335 |

15. **Fig. 5 Cd.** Re-digitized:

    | Speed (mph) | Cd |
    |---|---|
    | 35 | 0.402 |
    | 40 | 0.409 |
    | 45 | 0.409 |
    | 50 | 0.410 |
    | 55 | 0.404 |
    | 60 | 0.410 |
    | 65 | 0.408 |

    The text gives Cd as "0.4", relatively constant.
16. **Fig. 5 Cl means and error bars.** Re-digitized:

    | Speed (mph) | Cl mean | Error bar |
    |---|---|---|
    | 35 | 0.278 | 0.185-0.372 |
    | 40 | 0.230 | 0.148-0.311 |
    | 45 | 0.227 | 0.161-0.293 |
    | 55 | 0.161 | 0.092-0.230 |
    | 60 | 0.171 | 0.110-0.232 |
    | 65 | 0.158 | 0.074-0.243 |

    The dotted trend line runs from about 0.263 to 0.147.
17. **Carry simulation.** A ball hit at 5 deg, 40 mph and 2000 rpm backspin carries 28 ft with the average coefficients and 35 ft with Cl at the upper bound (p.4). The model, launch height and Cd used are not given.
18. **Derived S and Re.** S = 0.559 to 0.301 and Re = 7.7e4 to 1.43e5, with R = 37.1 mm, 2250 rpm and nu = 1.51e-5.
19. **Derived quantities.**
    - Cl fit: refit gives Cl = 0.0124 + 0.466*S. Residual standard errors are +/-0.024 on the intercept and +/-0.057 on the slope.
    - Forces at 4 mm: 350 N from the linear DS, about 660-670 N interpolated from Fig. 4, and 756 N from the power law.
    - Energy: the loading-branch area is 9.20 J. Incoming KE is 9.17 J at m = 25.5 g. The unloading area is 0.94 J.

### Corrected

1. **Review status.**
   - It is not an unreviewed extended abstract. ISEA 2026 asks for a "two to six page paper", and the call for papers says "The Microsoft CMT service was used for managing the peer-reviewing process". The repository lists the item as a conference proceeding.
   - Correct status: a short peer-reviewed conference paper, with light conference review and not journal review. It is funded by a manufacturer.
   - It runs to 4 pages of content plus 1 page of references.
2. **DS formula.**
   - It is not in the paper, as the extractor said. It is now confirmed from a secondary, unreviewed source: the WSU SSL web page (Smith's lab).
   - The page gives k = F_peak^2 / (m * v_in^2). This is the same as (1/m)(F_peak/v_in)^2. It comes from treating the ball as a linear spring, with 1/2 m v^2 = 1/2 k x^2 and F = k x.
   - The ASTM F2845 text itself was not seen.
   - F2845 specifies a **cylindrical** impact surface, measuring the "cylindrical COR". This paper used a **flat** plate. So its COR and DS are flat-plate variants "in the style of" F2845, not F2845 values.
3. **Ball identity.**
   - The impact test used "an approved Pickleball [3]". The paper does not say it was an outdoor ball or that it had 40 holes.
   - "Outdoor pickleballs typically have 40 holes" is a general statement, and the USAP spec is cited for it.
   - Only the Fig. 5 caption says "outdoor Pickleball". The paper does not say whether the impact and aero tests used the same ball model.
   - The test-ball mass is not given. 25.5 g is an assumption.
4. **Where the comparison numbers come from.**
   - The Cd comparison (tennis/wiffle 0.6, baseball 0.3) carries the citation [6] (Rossmann & Rau).
   - The Cl comparison (wiffle 0.35, tennis 0.3, baseball 0.25) has **no citation** in the text.
5. **Locations.** Fig. 5 is on p.4, while the Cd/Cl text is on pp.3-4. Eq. 1 and the carry simulation are on p.4.
6. **Fig. 4 at x = 0.05 in.** The force is about 80 lbf, not 88.
7. **Unloading branch.**
   - Confirmed: a near-vertical drop at x ~ 0.40-0.416 to about 60 lbf, then oscillation. Local peaks are about 65 lbf (0.297 in), 55 (0.32), 47 (0.365) and 42 (0.245). Troughs are about 10 lbf (0.35 in) and 15 (0.265). F reaches 0 at x ~ 0.20 in.
   - The "residual ~0.2 in" reading is the extractor's interpretation. The 0.2 in is the integrated centre-of-mass displacement when force ends, and the paper does not call it residual set.
8. **Plateau location.**
   - The first force plateau (about 147 lbf) sits at x ~ 0.12-0.16 in, which is **3.0-4.1 mm**, not 2.5-3.8 mm.
   - A second shoulder appears near 0.25-0.27 in (about 220 lbf), and there is a dip at 0.35-0.38 in.
   - The paper does not attribute these features to buckling. "Buckling" is the extractor's interpretation, and the features may also be ringing.
9. **Energy check.**
   - The unloading/loading ratio is 0.102, so e_equiv = sqrt(0.102) ~ 0.32. Rebound KE at COR 0.20 would be only 0.37 J, against 0.94 J under the unloading curve.
   - So the Fig. 4 unloading curve is **not** energy-consistent with COR 0.2. The cause may be ringing, integration drift, or this shot being unrepresentative.
   - The extractor's 0.33 is confirmed, but this inconsistency was not flagged.

### Dropped
None. Every extracted number can be traced to the text or figures, or is a reproducible derivation.

### Added (missed by the extractor)

1. **"Good shot" criterion.** The rebound must be within +/-10 deg horizontally and vertically of the inbound path. Rebound speed and angle come from further light gates (p.1). Non-normal rebounds were discarded, so off-axis scatter is under-represented.
2. **No Cl point at 50 mph.** Fig. 5 shows drag at 7 speeds but lift at only 6. Cd has **no error bars**. The paper does not define the Cl error bars (SD, range or CI). They are symmetric at +/-0.061 to +/-0.093, which is +/-30-53% of the mean.
   - If the bars are 1-sigma uncertainties of each mean, a weighted fit gives Cl = 0.013 (+/-0.15) + 0.47 (+/-0.36)*S. The slope is then barely different from zero.
   - The +/-250 rpm spin spread moves each point by +/-11% in S (S range 0.27-0.62).
3. **Mass comparison (p.4).** Pickleball mass is about 20% of a baseball, about 50% of a tennis ball and about 125% of a wiffle ball. The authors use this to argue that aero effects matter more for pickleball.
4. **COR comparison (p.2).** Baseball about 0.5 and tennis about 0.75, citing [5]. That source is a school physics journal (ISB Journal of Physics), which is weak.
5. **Purpose of the holes (p.3).** The holes are "intended to increase drag and movement from ball spin [6]". This is an attributed statement, not a measurement.
6. **DS implied by the Fig. 4 shot.**
   - With k = F^2/(m v^2), F = 337 lbf, v = 26.8 m/s and m = 25.5 g, k ~ 700 lb/in. This is a stiff, upper-tail shot (the mean is 500).
   - Conversely, the mean DS implies a mean peak force of about 285 lbf (1.27 kN).
   - A linear spring at 500 lb/in would compress 0.57 in, against the 0.4 in measured. This is consistent with the concave (softening, then stiffening) loading curve.
7. **Secant stiffness to peak in Fig. 4.** About 847 lb/in (148 kN/m). It differs from DS because the loading curve is not linear.
8. **Reaction-time figures (p.4).** At 40 mph a ball takes 0.26 s to cover 14 ft and 1 s to cover 44 ft. These are not relevant to POLLEN; listed for completeness only.
9. **A/m check.** About 0.178 m^2/kg for pickleball (74.2 mm, 24.3 g) and 0.158 for POLLEN (71 mm, 25 g), consistent with the extractor.

### Comments on the extractor's POLLEN implications

- The extractor's spring-dashpot zeta = 0.456 for e = 0.2 checks out: zeta = -ln e / sqrt(pi^2 + ln^2 e).
- Cl ~ 0.47*S should carry a slope uncertainty of at least +/-0.06 (residual-based), and up to +/-0.36 if the bars are 1-sigma uncertainties of the means. Treat it as a weak prior.
- The data cover S 0.27-0.62 only. Extrapolating to S of about 2 is unsupported.
- All impact data come from one speed (26.8 m/s) on a flat rigid plate at normal incidence. The paper reports no friction, oblique-impact or spin data.
