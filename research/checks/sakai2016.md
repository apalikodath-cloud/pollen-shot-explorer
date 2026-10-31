# Fact-check: Sakai et al. (2016), "Aerodynamics of a Spinning Table Tennis Ball ~Lift Crisis~"

- **Checked against:** the full-text PDF downloaded on 2026-10-30 from https://www.jstage.jst.go.jp/article/jsmemecj/2016/0/2016_J2340102/_pdf/-char/ja (5 pages).
- **What I read:** the text (pdftotext) and the page renders. I also pulled the embedded Fig. 7 and Fig. 8 bitmaps at their native ~221 ppi (738x436 px) and read the figures from them.
- **Also checked:** the J-STAGE landing page, for the metadata.
- **Extraction under review:** research/papers/sakai2016.md.

**CHECK: 15 confirmed / 9 corrected / 0 dropped / 9 added**

## Bibliographic data and review status
- **Authors.** The PDF prints the authors as 酒井 道, 宮嵜 武, 小松 竜郎, 高橋 直也, 姫野 龍太郎, romanised as Wataru SAKAI, Takeshi MIYAZAKI, Tatsuro KOMATSU, Naoya TAKAHASHI, Ryutaro HIMENO. Confirmed.
- **Affiliations.** University of Electro-Communications (first three authors), Tokyo Denki University (Takahashi) and RIKEN (Himeno).
- **Venue.** JSME 2016 Annual Meeting, Fukuoka, 2016-09-11 to 14, proceedings No.16-1, paper J2340102. Confirmed.
- **J-STAGE metadata.** The landing page lists Japanese names only and gives no romanisation. The extractor's note that J-STAGE romanised the first author differently could not be reproduced. This is harmless.
- **Review status.** "Conference" is right, with one qualification. J-STAGE files it as 会議録・要旨集 (proceedings/abstract collection). These are non-refereed annual-meeting proceedings, not a peer-reviewed paper.

## Data points

| # | Item | Verdict | Notes |
|---|---|---|---|
| 1 | Table 1, present study, Re 4.0e4, SP 1.0: CD 0.419 [0.009], CLZ 0.322 [0.010], n = 24 | CONFIRMED | |
| 2 | Table 1, present study, Re 9.0e4: CD 0.324 [0.012], CLZ -0.005 [0.018], n = 31 | CORRECTED (condition) | Table 1 lists the SP as 0.5, but the §3.1.1 text calls the same case SP = 0.48. The values are confirmed. |
| 3 | Table 2, present study, Re 4.0e4, SP 0: front 0.421 [0.008] (33), side 0.421 [0.018] (30) | CONFIRMED | |
| 4 | Table 2, present study, Re 9.0e4, SP 0.48: front 0.354 [0.017] (29), side 0.358 [0.016] (50) | CONFIRMED | |
| 5 | Tanaka et al. (2014) values reprinted in Tables 1-2 | CONFIRMED, with additions | Sample sizes and S.D. added: Re 4e4, SP 1.0: CD 0.480 [0.008], CLZ 0.306 [0.014], n = 28. Re 9e4, SP 0.5: CD 0.398 [0.011], CLZ 0.028 [0.032], n = 30. Re 4e4, SP 0: front 0.456 [0.008] (28), side 0.444 [0.021] (25). Re 9e4, SP 0.48: "No data". |
| 6 | Negative Magnus not observed for 3e4 < Re < 9e4, 0 < SP < 1.0 | CONFIRMED (§3.2.2, §5) | The paper treats the slightly negative CLZ near Re 9e4, SP 0.50 as within error. |
| 7 | Trend: CDmax, CDmin, CLZmax, CLZmin, SPmax and SPmin all fall as Re rises; CLZ scatter grows in the valley | CONFIRMED | The trend is in §3.2.1-3.2.2. The scatter claim is in the abstract ("standard deviations of CLZ increase drastically"). |
| 8 | Fig. 8, low-SP slope "≈0.8-0.9, Re-independent" | CORRECTED (precision) | §3.2.2 says CLZ starts out rising in proportion to SP, independent of Re; that part is confirmed. Read from the figure: CLZ ≈ -0.03 to +0.04 at SP 0.03-0.05, ≈0.05-0.12 at SP 0.1 and ≈0.13-0.18 at SP 0.2. A secant through the origin gives ≈0.85, but a fit from the SP ≈ 0.04 zero crossing gives ≈1.0. Use a slope of 0.85-1.0. |
| 9 | Fig. 8, Re 3e4: peak ≈0.29 at SP 0.55, valley ≈0.20-0.22 at SP 0.80-0.85 | CONFIRMED (by eye) | The valley is ≈0.21-0.22, spread over SP 0.72-0.85. |
| 10 | Fig. 8, Re 4e4: peak ≈0.27 at SP 0.45-0.50, valley 0.13-0.17 at SP 0.60-0.70, ≈0.32 at SP 1.0 | CORRECTED (SP) | The magenta points reach ≈0.27 at SP ≈0.40-0.42 and stay ≈0.25-0.26 up to 0.50, so the peak is at SP 0.40-0.50. The valley is ≈0.15-0.17 at SP 0.63-0.70. The magenta and red markers are hard to tell apart there, so ±0.03. |
| 11 | Fig. 8, Re 5e4: peak ≈0.25 at SP 0.45, valley ≈0.10-0.12 at SP 0.60-0.65, 0.32 at SP 0.95 | CORRECTED (SP) | The green valley is ≈0.09-0.12 at SP 0.57-0.62. The other values are confirmed by eye. |
| 12 | Fig. 8, Re 6e4-9e4 peak / valley values | CONFIRMED (by eye, ±0.02) | Two refinements. At Re 7e4 the minimum is ≈0.075 at SP ≈0.58, not 0.06-0.07 at 0.55. At Re 9e4 the points scatter between -0.01 and +0.03 over SP 0.47-0.52, with error bars of about ±0.02. |
| 13 | Fig. 8 upper branch: CLZ ≈0.25-0.36 at SP 0.85-1.14, "all Re bins collapse" | CORRECTED | The §3.2.2 text does say the post-valley rise is Re-independent. The figure does not fully bear this out: Re 3e4 (black) lags at ≈0.22 at SP 0.85 and ≈0.30 at SP 1.0, while the other bins are at ≈0.27-0.31 at 0.85 and ≈0.32-0.33 at 1.0. The maximum is CLZ ≈0.36 at SP 1.14, a single Re 7e4 point. |
| 14 | Fig. 7, CD vs SP | CORRECTED (details) | See the corrected data points below for the detailed values. In short: CD is ≈0.39-0.46 for SP 0-0.3. The peaks are ≈0.48-0.52 (Re 3-6e4), but the Re 6e4 peak sits at SP 0.38-0.45, not 0.45-0.55. Re 7e4 peaks at ≈0.47 near SP 0.43. Valleys: ≈0.40 (Re 3e4, SP ≈0.88), ≈0.35-0.37 (Re 4e4, SP ≈0.78-0.80), ≈0.35-0.36 (Re 5e4, SP ≈0.88), ≈0.33-0.35 (Re 6e4, SP ≈0.75-0.80, missing from the extraction), ≈0.265 (Re 9e4, SP ≈0.59), ≈0.275 (Re 7e4 and 8e4, SP ≈0.66-0.71). CD is ≈0.38-0.43 at SP 1.0-1.07 and ≈0.46 at SP 1.14. |
| 15 | Launcher: 3 rotors, about 80 rps each, reversible | CONFIRMED (§2.1.2) | The extraction adds that speed and spin can be set independently. The source does not say that; it only says the launch envelope was greatly widened. The rotor diameter is not given, so no surface speed can be derived. |
| 16 | Ball: d printed as 3.98e-5 m (typo for 3.98e-2), m 2.74e-3 kg | CONFIRMED | |
| 17 | Cameras: Phantom Miro LC310 at 3000 fps (Re 3-6e4) and 4500 fps (Re 7-9e4) | CONFIRMED (§2.2.2) | The old rig ran at 1901 fps. |
| 18 | Front view: "4 light sheets (2 mm laser lines) and an impact board 0.685 m apart" | CORRECTED | The rig has 4 metal-halide slit lights (Nobbytech 963A002) and a polycarbonate board, spaced 0.685 m apart on the table. Laser line generators (Muratec KDS ATL) replaced only stations L2-L4, narrowing them from about 1 cm to 2 mm. Station L1 is not stated to have changed. |
| 19 | Fit points: 40-50 | CONFIRMED (§2.2.4) | 50 points for Re 3-5e4 (previously 30); 40 points for Re ≥ 5e4 (previously 20). |
| 20 | Side view: camera 1 at 0.1 m from the launcher, camera 2 at 0.1 m before the acrylic board, camera 3 for target miss; zero-lift cases only | CONFIRMED (§2.1.4, §3.1.2) | The method is in Miyazaki et al. (2013), Sports Eng. 16:43. The source says "non-spinning balls only", plus the Re 9e4, SP 0.48 case because CLZ ≈ 0 there. |
| 21 | Range: 3.0e4 < Re < 9.0e4, 0 < SP < 1.0 (a few points to 1.14), 7 Re bins | CONFIRMED | Seven legend entries, 3e4 to 9e4. The highest SP point is ≈1.14 (Re 7e4). |
| 22 | Prior literature: Taneda; Muto CL = -0.25 at Re 2e5, SP 0.2; Tanaka | CONFIRMED | Taneda's negative-Magnus region is 6e4 < Re < 5.0e5, 0 < SP < 0.6, from water-tank tests. Tanaka found none in flight for 2e4 < Re < 9e4, SP < 1. |
| 23 | Prior literature: "Kim 2014 negative region within 6e4 < Re < 1.8e5, SP < 1.8" | CORRECTED | That range is Kim's wind-tunnel test range. The source says only that Kim found a negative region narrower than Taneda's inside it. |
| 24 | Derived A/m: TT ball 0.459 m²/kg, POLLEN 0.158 m²/kg, ratio 0.345 | CORRECTED (arithmetic) | With d = 39.8 mm and m = 2.74 g, the TT ball's A/m is 1.244e-3 / 2.74e-3 = 0.454 m²/kg. The value 0.459 implies d = 40 mm. POLLEN (d 71 mm, ~25 g nominal): 3.959e-3 / 0.025 = 0.158 m²/kg. The ratio is 0.349 (≈0.35), not 0.345. Not in the source; derived. |

## Equations
- **No equations in the paper.** It contains no equations and does not define SP. It calls SP 無次元回転数, "dimensionless rotation rate".
- **Labelled correctly.** The extraction labels every key equation as inferred, which is right.
- **Side-view drag formula.** C_D = (2m/(ρ A Δs)) ln(U1/U2) is the extractor's reconstruction. The source points to Miyazaki et al. (2013) and was not checked against it.
- **Lift-crisis zone.** SP_max < SP < SP_min is confirmed as a definition in words in §4.
- **Re in m/s.** The Re-to-speed conversion with ν = 1.51e-5 is the extractor's assumption. The paper gives no air properties or temperature.

## Added data points (missed by the extractor)
1. **Internal inconsistency at Re 9e4.** Table 1 (SP 0.5, n = 31) gives front-view CD = 0.324 [0.012]. Table 2 (SP 0.48, n = 29) gives front-view CD = 0.354 [0.017]. These are different shot sets 0.02 apart in SP, inside the crisis zone, and they differ by about 2 S.D. Fig. 7 at Re 9e4 shows CD falling steeply there (≈0.35 at SP 0.48 to ≈0.27 at SP 0.59). This shows how sensitive the coefficients are to small spin changes inside the zone.
2. **Ball tolerance.** The diameter S.D. is 0.20e-6 m, given as evidence of high sphericity (§2.1.1). The ball carries a painted cross mark for reading spin from video (Fig. 1).
3. **Konishi et al. (2013).** In a wind tunnel, a 44 mm "large" TT ball almost completely reproduced Taneda's negative-Magnus region (§1, ref 5). This is relevant because a wind tunnel did find negative Magnus on a TT ball, while flight tests (Tanaka; this paper) at Re ≤ 9e4 did not.
4. **Briggs (1959).** Confirmed negative Magnus by dropping spinning balls in a wind tunnel (§1, ref 2).
5. **Stated play regime.** TT play is Re ≤ 1.0e5 and SP ≤ 2, and the aerodynamic forces exceed gravity there (§1). The radius is given as about 2 cm and the mass as 2.7 g.
6. **Method validation.** The improved front-view CD agrees with the side view, while Tanaka's rig did not (0.456 vs 0.444). The paper's CD values are lower than Tanaka's, which it credits to the improved accuracy. CLZ agrees with Tanaka.
7. **Old slit-light width.** The old slit lights were about 1 cm wide, and that width is named as a main error source. This is useful for designing a POLLEN rig.
8. **Fig. 8 near-zero spin.** At SP < 0.05, CLZ is ≈ -0.03 to +0.04. That is the measurement noise floor for lift at near-zero spin.
9. **Same table re-certified.** A Nittaku NT-3200 ITTF-certified table replaced a warped table that was used as the light-mount datum (§2.2.3). The figure numbering is duplicated: "Figure 7" is used both for the table photo and for the CD plot.

## Comments on the extractor's applicability and model sections
- **Arithmetic checks out.** The POLLEN Re map holds: 4.70e3 per m/s, so Re 3e4 is about 6.4 m/s. The Magnus acceleration examples also hold: 0.5·1.2·64·0.158·0.32 = 1.95 m/s², and 0.5·1.2·9·0.158·0.35 = 0.30 m/s².
- **Point (2) needs a qualifier.** "By S ≈ 1 every bin is back on the upper branch, Cl ≈ 0.30-0.33" is fine, but Re 3e4 (the bin closest to POLLEN) is at the low end, ≈0.30.
- **Lower SP bounds.** The model implication about a "smooth-sphere crisis" envelope should use the corrected peak and valley SPs above.
- **Cd band.** The band 0.40-0.51 for S ≤ 1 at Re 3-5e4 should be widened to 0.35-0.52, because the 4e4 and 5e4 valleys reach ≈0.35.
- **No other overclaim.** I found no invented values. Everything else in the applicability section is clearly labelled as inference.
