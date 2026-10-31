# Fact-check: sweep_pollen (POLLEN / ResisDent ball data and BIOBUZZ shooter observations)

Task PM-001 · checker agent · 2026-10-30 · checks `research/sweeps/sweep_pollen.md`

**CHECK: 9 confirmed / 7 corrected / 0 dropped (1 sub-claim dropped) / 12 added**

Method: I re-opened every source myself. For the AndyMark drawing and STEP, I downloaded both files and rendered the PDF. I parsed the STEP with my own script for sphere radii, cylinder radii, the 26 hole axes, latitudes and spacing, and I recomputed every derived number. Chief Delphi posts were read raw with `/raw/<topic>/<post>`. For GitHub calculators I read the README, the physics docs and the source. For the manual, I extracted the text of the archived §9 PDF. AndyMark product data came from the page and from its Shopify variant JSON.

## Verdict on the extraction
The extraction is good overall: there is no invented number, and every derived value reproduces. The errors are in **attribution and context**, not arithmetic:
1. The manual copy at the archive URL is **TU06** (PDF modified 2026-10-22), not TU04. The 2.8 in / "may vary in size" text is in **§9.8**, and the 2.79 in seat is in **§9.7**.
2. The **63° launch, top counter-roller and 0.25 in compression are FTC 37246 StuyTide**, not 37245 StuyPoofs. 37246 also states that it has not yet found a gearing that scores consistently.
3. FTC 17134's "topspin spins into the hive" comes from a **drill-powered prototype that did not reach the HIVE** (its own words). In a later post the same team says its **backspin shooter "shows great potential"**. The extraction presented 17134 as clean evidence against backspin, which overstates it.
4. Escape Velocity's post says only "Ri3D (which has a fixed solid hood)". "Single flywheel" is an inference. Its bins (27 + 15 = 42) do not add up to the 43 shots.
5. Community calculators differ more than the summary said. Advik123 uses Cd = 0.5 and I = 2/3 mR². Infinity Tech uses Cd = 0.47, has **no Magnus force**, and uses v = ½ v_surface with no η. tunapro defaults to I = 0.4 mR² (solid sphere). Quantum-Igniters uses vacuum ballistics with v_exit = v_surface (two wheels).
6. The "Plex lists 2.9 in" claim cites no URL and I could not find it, so I dropped it.
7. On the StarterBot, 23414 added flywheel weights "to get the pollen moving through the flywheel faster", but it does not report that this helped.

## Data point verification

| # | Quantity | Status | Notes from re-check |
|---|---|---|---|
| 1 | OD 2.8 in, ±0.1 in | CORRECTED | Print shows Ø2.8, and the one-place tolerance is ±0.1. That part is confirmed. "Plex lists 2.9 in" is dropped (no URL, not found). |
| 2 | Wall 0.07 in ±0.01; STEP R 1.40/1.33 in | CONFIRMED | Print ".07" on Section A-A, two-place ±0.01. STEP: SPHERICAL_SURFACE radii 1.40 and 1.33, units INCH, centred at the origin. |
| 3 | 26 holes, Ø0.4 (print) vs Ø0.44 (STEP); 2 / 8@±49° / 16@±15.6°; spacing 33–41° | CONFIRMED | 52 CYLINDRICAL_SURFACE entities, r = 0.2200 in (26 holes × 2 faces). The 26 unique radial axes have the polar axis on the CAD **Y** axis: 2 at ±90°, 8 at ±49.1°, 16 at ±15.6°. Nearest-neighbour spacing is 33.3–40.9°. Ø0.44 is within the print's ±0.1 one-place tolerance, so it is not strictly a contradiction. |
| 4 | Two hemispheres; "HEMISPHERE TIMING NOT REQUIRED" | CONFIRMED | The note's leader points to the equatorial seam in the main view (not the Section A-A view). |
| 5 | Catalogue mass 0.055 lb = 24.9 g | CONFIRMED (caveat) | The page lists "Diameter: 2.8 in., 3.6 in." and "Weight: 0.055 lbs., 0.091 lbs" without saying which is which. Pairing by order is consistent: the NECTAR variant ships at 41.28 g = 0.091 lb. See added point A1 for the shipping weight. |
| 6 | Nominal CAD mass 20.5–21.9 g; 24.9 g needs a wall of about 0.08–0.085 in | CONFIRMED | Shell volume 1.639 in³ minus 26 cylinders through 0.07 in: 20.5–22.0 g at ρ = 0.92–0.95 g/cc. A wall of 0.079–0.085 in gives 24.9 g. |
| 7 | I/(mR²) = 0.634 | CONFIRMED | 0.4·(R⁵−r⁵)/((R³−r³)R²) = 0.6344. |
| 8 | Open area 13.3% / 16.2% | CONFIRMED | 26·(1−cos(asin(d/2R)))/2 = 0.1333 and 0.1615. |
| 9 | Manual size text and FLOWER seat | CORRECTED | Archive PDF footer reads "Version: TU06" (pp. 63–73 of 173), not TU04. POLLEN text is in **§9.8**: "approximately 2.8 in. (7.1 cm) Gopher ResisDent polyethylene balls", and "POLLEN and NECTAR are not perfectly spherical and may vary in size". The 2.79 in figure is the **§9.7 FLOWER lower-ring hole** "for POLLEN to sit in". |
| 10 | Bounce-out 19/43 = 44.2%, bins 15/27 and 9/15, R² 0.281, CI 30–60% | CORRECTED (minor) | Numbers match post #12 (2026-09-27) verbatim. Corrections: (a) the post says "Ri3D (which has a fixed solid hood)", so "single flywheel" is inferred. (b) The bins sum to 42, not 43. (c) Wilson 95% CIs: total 30.4–58.9%, 0–3 bin 28–63%, 4–7 bin 20–64%. The bin difference is not significant. (d) The team says the Ri3D test "confidently" answers that backspin must be mitigated, and considers an underhand shooter to get topspin. |
| 11 | Tip times 4.76 s (8 POLLEN) and 2.78 s (2N+5P) | CONFIRMED | Post #12. The team says 2N5P "shouldn't tip; our hive may need some more calibration". |
| 12 | Spin vs retention (qualitative) | CORRECTED | 17134 #4: the prototype "was drill-powered and thus did not reach the hive", yet the team concluded topspin "will spin into the hive instead of out of it". 17134 #6: tested side, backspin and frontspin shooters, and says "the backspin shooter (for both pollen and nectar) shows great potential". 12527/16095 #2 ("backspin can significantly hurt scoring performance") is confirmed. 37245 in 525071 #10 ("zero spin to limit the bounce-outs") is confirmed. 37244 in #12 ("two sets of wheels, to minimize spin ... avoid bounceouts") is confirmed. 14343 adding powered counter-rollers is confirmed. |
| 13 | Launch parameters | CORRECTED | 17134 #8: 60° straight-line shot with topspin, and 74° parabolic. Confirmed. **63° with a top counter-roller and 0.25 in compression is 37246 StuyTide (525071 #1)**, not 37245. 37246 adds "we haven't found a working gearing for this system yet that scores consistently". |
| 14 | StarterBot behaviour and 1165 ticks/s = 2496 RPM | CORRECTED (minor) | 523925 #4: "shot straight up into the ceiling". They "cut the 2 zip ties holding up the top of the shooter's curved plastic piece" and changed power from 1 to 0.75. Added flywheel weights "to get the pollen moving through the flywheel faster", with no outcome reported. L/R wiggle was fixed with foam. Re-centring the off-centre flywheel "helped our robot shoot straighter". Code: LAUNCHER_TARGET_VELOCITY = 1165 "// 2496 RPM" (28 ticks/rev) appears in the Teleop **and** both Auto files on the starter-bot branch. Wheel diameter is still not found (searched). |
| 15 | FUEL v_t 10.16 m/s, stated Cd 0.45; recomputed 0.88 | CONFIRMED | 154587 #14 (17gecklerm for Team 4926, 2017-01-10). AndyMark am-3376 page: "Weight: 0.156 lbs." = 70.76 g, 5 in. Recomputed Cd = 0.882 at ρ = 1.204 (about 0.91 at ρ = 1.17). |
| 16 | JamesCH95 spin quote | CONFIRMED | 154587 #13, 2017-01-08, verbatim. |
| 17 | Community calculator assumptions | CORRECTED | Advik123: Cd 0.5, Cl = min(0.35, 0.6S), I = 2/3 mR², ω = v_exit/r, COR 0.45/0.5/0.55, μ 0.3/0.4, v_exit = η·v_s/2. Infinity Tech: Cd 0.47, ρ 1.225, **no spin lift**, v₀ = ½ wheel tangential speed with no η, m 25 g. tunapro: Cl = min(liftMax, liftSlope·S) editable, I = 0.4 mR² default, contact-impulse launcher; its "ReCalc reference" (7.585 m/s, 1700→1426 RPM) is fitted to a calculator, not measured. Quantum-Igniters: vacuum ballistics, v_exit = v_surface (two flywheels), target 60 in. |

## Added data the extraction missed
- **A1** AndyMark Shopify variant JSON lists POLLEN at **27.2155 g (0.06 lb)** and NECTAR at 41.28 g. The FUEL am-3376 variant is listed at 85 g against a spec of 0.156 lb (70.8 g). These are shipping or listing weights, so treat the POLLEN mass as about 25–27 g until weighed. [R1 metadata]
- **A2** Manual TU06 §9.6: CELL opening about 20 × 14 in, depth 12 in, HIVE pivot axis 43.95 in, CELLS about 18.8 in apart, 40 POLLEN per match. [R1]
- **A3** 17134 #8: "the way a pollen would enter the shooter and first interact with the flywheel had a massive difference in how the shot went". The team narrowed the entrance for control. [R4]
- **A4** 37247 (525071 #1) gets no spin from "two wheels spinning at the same rate". It found 54° gives "the greatest margin of error" and that the feed method "can cause great variation". [R4]
- **A5** 37246 (525071 #1): intake compression 0.45 in worked best, and shooter compression 0.25 in "worked really well". [R3]
- **A6** 37245 (525071 #10): the zero-spin prototype ran 1 of 2 motors because 2 overshot. The StarterBot RPM is "too high, and it consistently misses the shots". [R4]
- **A7** 14343 #27 (2026-10-19): iteration 1 was a direct-driven 3D-printed + silicone flywheel with back counter-rollers. Iteration 3 shot POLLEN and NECTAR at "similar RPMs" but at different flywheel positions. PDSV control recovery was about 0.1–0.3 s (not measured). [R4]
- **A8** 23414 #3: the DECODE-season hooded shooter "was able to shoot pollen fine" with foam added, but jammed on NECTAR. [R4]
- **A9** 154587 #8 (2017 FUEL): "pretty stable when tossed but they lose velocity rapidly and eventually just want to drop out of the air". This is qualitative support for high Cd. [R4]
- **A10** 154962 #2 (2017 FUEL): Team 639, with an 8 in rubber-treaded single wheel, got L/R spread within half a foot, but "front to back is all over the place". In 154962 #9, the "1717 shot had no spin" video is of a two-wheel shooter in an **earlier game with a different ball**, so it is not FUEL data. [R4]
- **A11** The Advik123 README says that with the flywheel **above** the ball and a ramp **below**, the ball gets **topspin**. Backspin needs the wheel below and the hood above. The user's mechanism must put the hood on the correct side. [R5 kinematics, physically correct]
- **A12** Infinity Tech hardcodes HIVE plate tilt 30° and bottom edge Z = 53.5 in. These numbers are **not verified** against official CAD. Do not reuse them. [R5]

## Status of other "also checked" claims
- The Gopher ResisDent page gives no dimensions or mass and says "three sizes". Confirmed. It also contradicts itself ("rigid polyethylene" versus "weighted foam balls").
- "Design surface speed ≈ 2× ball speed": confirmed as the theory claim in 155126 #2 (Zook) and #3 (Nathan_Streeter). It is not data.
- Reddit was not attempted.

## Reliability summary
There is still no measured POLLEN Cd, Cl(S), COR, μ, stiffness, exit speed or exit spin anywhere. The strongest quantitative field result is 19/43 bounce-outs on one team's fixed-solid-hood Ri3D robot (n = 43, CI 30–59%, spin unmeasured). The qualitative team evidence against backspin is weaker than the extraction implied: one of the "topspin" conclusions came from a test that never reached the HIVE, and that same team calls its backspin shooter promising.
