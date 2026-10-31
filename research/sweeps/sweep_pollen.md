# Sweep: actual data on POLLEN / Gopher ResisDent balls and BIOBUZZ shooter observations

Task PM-001 · sweep agent · 2026-10-30 · file owner: this sweep only.

Scope: real data on the POLLEN ball itself (AndyMark am-5851_yellow, Gopher ResisDent polyethylene) and its predecessor (2017 FRC STEAMWORKS FUEL, 5 in Gopher ResisDent), plus measured or observed shooter behaviour from FTC BIOBUZZ teams. The 12 priority papers are covered by other agents and are not repeated here.

**Bottom line:** no one has published a measured POLLEN Cd, Cl, COR, friction coefficient, stiffness or exit spin, and no paper has measured them either. The only first-party data is AndyMark's drawing and CAD (geometry) and its catalogue mass. The only quantitative shooter-to-HIVE result is one team's bounce-out count. Several teams independently report that **backspin increases bounce-outs from the CELL**, and they are moving to topspin or zero spin. That directly challenges the user's hypothesis, and it has to be tested.

## Reliability labels
- **R1 (primary/official):** a vendor drawing, CAD, or the official manual. It gives nominal design values, not as-made measurements.
- **R2 (derived):** my own calculation from R1 data, with the method stated.
- **R3 (team test, unreviewed):** a forum or build-thread report of a real test, with a count or number.
- **R4 (team observation, qualitative):** an unreviewed forum post with no numbers.
- **R5 (assumption):** values in community calculators, with no measurement behind them.

## Sources

| id | Citation | URL | Review status | What it contributes |
|---|---|---|---|---|
| am5851_print | AndyMark, "POLLEN", drawing am-5851_yellow rev 1, P. Yeung, 9/11/2026 (SolidWorks PDF) | https://documents.andymark.com/bc64addc5b9b6e528cb96de4e498ffd2134eb656232d4f0e3c7f5c1ebd057b58/am-5851_yellow%20Pollen.pdf | Vendor drawing (R1) | Ø2.8 in OD, 0.07 in wall, **26 holes of Ø0.4 in**, polyethylene, two hemispheres with an equatorial seam, "HEMISPHERE TIMING NOT REQUIRED", tolerance table |
| am5851_step | AndyMark, am-5851_yellow Pollen.STEP (SolidWorks 2024, AP214, 2026-09-11) | https://documents.andymark.com/3876dea7b683c2085286da2899504555aab1a13720ab8c02c1d0107e1095f445/am-5851_yellow%20Pollen.STEP | Vendor CAD (R1). I parsed it myself (R2) | Outer R 1.40 in, inner R 1.33 in, **26 holes, cylinder radius 0.22 in (Ø0.44 in)**. Hole layout is from a cube family (2 polar, 8 at ±49°, 16 at ±15.6° latitude), with nearest-neighbour spacing 33–41° |
| am_se_page | AndyMark, "BIOBUZZ Scoring Elements" product page | https://andymark.com/products/biobuzz-scoring-elements | Vendor catalogue (R1) | Mass 0.055 lb (24.9 g) for POLLEN; NECTAR 3.6 in, 0.091 lb (41.3 g); links to the print and STEP |
| ftc_manual_s9 | FIRST, BIOBUZZ Competition Manual §9 ARENA (archived TU04 PDF; the lead has TU07) | https://ftc-resources.firstinspires.org/ftc/archive/2027/game/manual-09 | Official rules (R1) | "approximately 2.8 in. (7.1 cm) Gopher ResisDent polyethylene", "not perfectly spherical and may vary in size"; FLOWER seat ≈2.79 in. Gives no mass, stiffness or COR |
| ev14343_cd | FTC 14343 Escape Velocity, "BIOBUZZ Build Thread", Chief Delphi, posts #12 (2026-09-27) and #27 (2026-10-19) | https://www.chiefdelphi.com/t/ftc-14343-escape-velocity-biobuzz-build-thread/524080 | Unreviewed build thread (R3) | **Backspin test: a fixed solid-hood shooter kept 24 of 43 HIVE-landing shots, so the bounce-out rate was 44.2%.** Binned by POLLEN already in the CELL: 15/27 at 0–3 and 9/15 at 4–7. The team switched to powered counter-rollers. Tip timing: 8 POLLEN took 4.76 s from contact to a scored tip. Its tipping table (from video) lists the count combinations that tip |
| teams_spin_cd | Combined team reports: FTC 17134 Ghosttt (thread 523966, posts #4/#6/#8), FTC 12527/16095 (thread 525608 #2), FTC 37244-7 Stuy (thread 525071 #1/#10/#12), FTC 23414 Pinions (thread 523925 #3/#4), Chief Delphi, Sept–Oct 2026 | https://www.chiefdelphi.com/t/ftc-17134-ghosttt-build-thread-open-alliance-2026-27/523966 ; https://www.chiefdelphi.com/t/ftc-12527-16095-build-thread-2027-biobuzz/525608 ; https://www.chiefdelphi.com/t/stuy-ftc-37244-37245-37246-37247-build-blog-26-27/525071 ; https://www.chiefdelphi.com/t/ftc-23414-the-pinions-2026-2027-build-thread/523925 | Unreviewed build threads (R4, with a few R3 numbers) | Independent reports that backspin hurts CELL retention and that topspin or zero spin "spins into the hive". Exit angles tried: 60° and 74° (17134), 63° (37245). Shooter compression 0.25 in (37245). On the goBILDA single-flywheel + curved-hood StarterBot, POLLEN "shot straight up into the ceiling" until the hood was loosened and power cut to 0.75 (23414) |
| fuel2017_cd | Chief Delphi, "Terminal Velocity of the Fuel Balls" (2017-01-07 to 01-11), posts #13 (JamesCH95) and #14 (Team 4926) | https://www.chiefdelphi.com/t/terminal-velocity-of-the-fuel-balls/154587 | Unreviewed forum (R3/R4) | Predecessor ResisDent ball (5 in, 0.156 lb per AndyMark am-3376): a measured terminal velocity of **10.16 m/s** with a stated Cd of **0.45**. These two values do not agree; see the data notes. One team reports that spin "did not affect the balls like Wiffle balls", which they attribute to the uniform hole distribution |
| community_calcs | Community BIOBUZZ calculators: Advik123 FTC-BioBuzz-Shooter-Sim; Infinity Tech trajectory simulator; tunapro1234 ftc-biobuzz-shooter-calculator; Quantum-Igniters velocity calculator | https://github.com/Advik123/FTC-BioBuzz-Shooter-Sim ; https://trajectory.infinitytechrobotics.com/ ; https://github.com/tunapro1234/ftc-biobuzz-shooter-calculator ; https://github.com/Quantum-Igniters/FTC-BioBuzz-Velocity-Calculator | Unreviewed software (R5) | **None of them uses any measured POLLEN coefficient.** Typical assumptions are Cd 0.47–0.5, Cl = min(0.35, 0.6·S), I = 2/3 mR², COR 0.45–0.55 (placeholders), and v_exit = η·v_surface/2. They are useful only as a warning that the whole community runs on assumptions |

Also checked, with nothing quantitative: the Gopher Sport ResisDent page (no dimensions); the Plex listing (gives 2.9 in and 0.055 lb, which conflicts with 2.8 in); the FUN FTC content thread (no data); the goBILDA StarterBot guide page (no launcher specs). The StarterBot example code as copied by team 37244 sets the launcher at 1165 ticks/s, which is 2496 motor RPM. The wheel diameter was not found, so this value is not usable. Chief Delphi threads 155126 and 154962 (2017 FUEL shooters) contain only theory and anecdote: the "design surface speed ≈ 2× ball speed" rule of thumb for a single wheel with a fixed hood, and "1717's shot had no spin". Reddit search was blocked from this environment.

## Extracted data

### Geometry and mass (R1, R2)
- OD = 2.8 in (71.1 mm). On the print, one-place decimals carry ±0.1 in, so the drawing allows 2.7–2.9 in (68.6–73.7 mm). Plex lists 2.9 in. The manual says the balls "may vary in size". **Measure each ball.**
- Wall = 0.07 in (1.78 mm), two-place decimal, ±0.01 in. Inner radius in the STEP = 1.33 in.
- Holes: 26. The print says Ø0.4 in (±0.1 one-place), but the **STEP models Ø0.44 in** (11.2 mm). Open-area fraction (spherical caps) is **13.3% at Ø0.40 and 16.2% at Ø0.44** (R2).
- Construction: two moulded hemispheres with an equatorial seam. "Hemisphere timing not required" means the two halves' hole patterns can be rotated relative to each other, so **hole pattern and seam orientation vary from ball to ball**. This is a likely source of shot-to-shot scatter and of lateral force under spin.
- Mass: 0.055 lb (24.9 g), per the catalogue. From nominal CAD geometry with PE at 0.92–0.95 g/cm³, I get **20.5–21.9 g** (R2). To reach 24.9 g at 0.95 g/cm³ the wall would need to be about 0.08–0.085 in. That is at or just past the +0.01 in wall tolerance, before counting the seam flange. **Weigh real balls; expect roughly 21–26 g.**
- Moment of inertia, thick shell on nominal CAD: I/(mR²) = **0.634** (R2). Holes change this by less than 1%. The thin-shell value 2/3 is about 5% high. Use I = 0.634·m·R², or 0.62–0.67 as the uncertainty band.
- Areal loading m/A = 6.28 kg/m² (R = 35.56 mm, m = 24.95 g). Re = 0.95e4, 2.4e4 and 4.7e4 at 2, 5 and 10 m/s (ν = 1.5e-5 m²/s).

### Predecessor FUEL (2017 ResisDent 5 in) drag (R3, low reliability)
- Team 4926 drop test: v_t = 10.16 m/s, "Cd = 0.45". With AndyMark's mass (70.8 g) and D = 127 mm (m/A = 5.59 kg/m²), ρ = 1.204 and v_t = 10.16 give **Cd ≈ 0.88**. A Cd of 0.45 would need m ≈ 36 g. The two numbers are inconsistent, the method is unstated, and a gym-height drop may not reach terminal velocity. Treat this only as a sign that a ResisDent ball can have Cd well above the smooth-sphere 0.47, possibly near 0.9, which matches the trend Rossmann & Rau found for Wiffle balls at low Re (other agent).
- For scale, POLLEN terminal velocity would be 15.1, 14.3, 13.1, 11.3 and 10.1 m/s at Cd = 0.45, 0.5, 0.6, 0.8 and 1.0 (R2). A drop or terminal-velocity test on real POLLEN is cheap and discriminating, but it needs at least 240 fps and a tall drop.

### Spin effects on ResisDent balls (R4)
- JamesCH95 (2017): "We did specific testing to see if spin affected ball trajectory on the order of what a wiffle ball does, and these balls are not affected in the same way as wiffle balls... the uniform distribution of holes does not enable the very interesting aerodynamic effects". This is evidence against Wiffle-style asymmetric-hole curving. **It is not evidence of zero ordinary Magnus lift.** No numbers were given.

### BIOBUZZ CELL entry with spin (R3/R4) — key for the collision model
- ev14343: a fixed solid hood (single flywheel, so backspin) gave a **44.2% bounce-out** (19/43). The binned data hint that POLLEN already in the CELL damp bounce-outs: 44% bounce-out at 0–3 POLLEN and 40% at 4–7. The team calls the trend "junk" (R² = 0.28). The sample is small, so the 95% CI on the bounce-out rate is about 30–60%.
- 17134: drill-powered tests found that "top spin will work best... the game pieces will spin into the hive instead of out of it". Its V1 uses a 60° exit with topspin as a near-straight-line shot; 74° (parabolic) is still under test.
- 12527/16095: "backspin can significantly hurt scoring performance"; they are exploring frontspin.
- 37245 StuyPoofs: "shoots with zero spin to limit the bounce-outs"; 63° launch; counter-roller; compression 0.25 in (6.4 mm).
- 23414: on the goBILDA StarterBot (single flywheel + curved plastic hood), POLLEN went "straight up into the ceiling" at full power. Lowering the hood and running the motor at 0.75 power fixed it. Off-centre wheel contact gave left/right scatter, and adding flywheel mass helped.

## POLLEN applicability
- Geometry, mass, and inertia from am5851_print/step: applies directly to POLLEN. These are nominal values, not measurements, and the CAD and print disagree on hole diameter (0.40 vs 0.44 in).
- FUEL 2017: same ResisDent family, polyethylene, hollow with holes. But it is 1.8× the diameter, with different hole size and count, and Re is about 1.8× higher at the same speed. Use it only qualitatively.
- Team CELL-entry observations: same ball and same target, so they are the most relevant evidence for collisions. They do not cover the user's specific unfavourable-side geometry, and spin magnitude was never measured.

## Model implications for PM-001
1. Use m = 24.9 g as nominal with a 21–26 g band. Use R = 35.56 mm with a ±1.3 mm band, and I = 0.634·m·R² instead of 2/3·m·R².
2. Treat Cd as uncalibrated, with a band of roughly 0.45–0.9 for low Re (the FUEL drop data and the Wiffle trend both push the upper end up). Do not use a single smooth-sphere 0.47.
3. Add a ball-to-ball and orientation scatter term: hemisphere timing is random and holes are 11 mm on a 71 mm ball. Model it as a random lateral or side force under spin, and a ±few % Cd and Cl variation by orientation.
4. **The collision model must test the bounce-out mechanism.** Field evidence says backspin raises CELL bounce-out to about 44% with a fixed hood. Model the spin-dependent rebound off the CELL floor and back wall: with backspin, the tangential friction impulse on the floor drives the ball back toward the opening. Any trajectory gain from backspin must then be weighed against the retention loss. A feasible case needs entry geometry where backspin carries the ball inward (for example, striking the far wall) or keeps it there.
5. Single flywheel with a fixed hood: the StarterBot evidence shows exit angle is sensitive to hood position and wheel speed, and that off-centre contact causes lateral scatter. Include hood-contact angle and wheel-centring tolerance as parameters.

## Recommended measurements, all cheap
- Weigh at least 10 POLLEN on a 0.01 g scale. Caliper the OD across and along the seam, and the hole diameter and wall at the holes.
- Find COR by drop on the CELL floor material and the HIVE frame, using 240 fps video, at 1–5 m/s.
- Find the oblique-impact friction coefficient by spin-in vs spin-out on the CELL surface.
- Take a drop-tower or high-speed-video trajectory fit for Cd. Do backspin shots against a gridded wall at a known spin (marker dots on the ball, 240+ fps) to fit Cl(S). Repeat for several seam orientations.
- Repeat the 14343 retention test (n ≥ 50 per condition) with backspin, zero spin, and topspin at the same entry, on the user's real geometry.

## Caveats
- Every forum and build-thread item is unreviewed, and the teams' spin magnitudes, wheel speeds and hood geometry are mostly unknown.
- The FUEL Cd claim does not agree with itself.
- I could not open the CD video and Drive links, or Reddit. No team in these threads reported a measured POLLEN exit speed or spin.
