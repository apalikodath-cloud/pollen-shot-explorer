# Fact-check: Pedersen (2026), "Flywheel Shot Analysis: Correction and Extension"

source_id: `pedersen2026` · Task PM-001 · Independent check on 2026-10-30 · Extraction checked: `research/papers/pedersen2026.md`

**CHECK: 12 confirmed / 2 corrected / 0 dropped / 8 added** (data points). All extracted equations are confirmed. The derived equations are relabelled as derived. The POLLEN numbers were recomputed and agree, except for one rounding correction (implication 5).

## Sources I re-opened myself

- I re-fetched the forum thread from `https://www.chiefdelphi.com/t/520270.json` and read all 6 posts:
  - #1 rafi, 2026-05-06 20:23Z
  - #2 jtrv (with an image)
  - #3 jamzDoge ("fire")
  - #4 U6C3H9 (no content)
  - #5 Alex_Y
  - #6 rafi, 2026-05-07 15:07Z (with the plot)
- The whitepaper PDF came from `robot.mbhs.edu/r/2026wp_flywheel_pdf`, which returns a 301 redirect to `/media/whitepapers/2026/flywheel-calculations-latest.pdf` (12 pages, 302,985 bytes). I read all 12 pages as rendered images.
  - The PDF metadata gives CreationDate = ModDate = 2026-05-06 16:58 EDT.
  - The server's Last-Modified header is 2026-06-26. The "latest" file may therefore have been re-uploaded after the forum post, but its internal date is still May 2026.
- I exported the Google Sheet `1LD30xVo…` as xlsx and parsed every formula and cached value in all 4 tabs.
- I viewed both forum images:
  - The image in #2 is only a crop of PDF page 11, the H_w + H_h = m_b ΔV_b check. It contains no data.
  - The image in #6 is the compression plot.
- To cross-check Brettle I used the sibling check `research/checks/brettle.md`. The Brettle HTML was too long for WebFetch, so I did not re-read it directly.

## Review status: confirmed

The status "unreviewed web article" is correct. The source is a forum post plus a self-published LaTeX whitepaper. The post says Dean Brettle helped review it, which is informal review, not peer review. The whitepaper contains no experimental data. Its conclusion (p.6) says: "whether the 'no slip at exit' condition is realistic has not been empirically validated".

## Equations: all confirmed, with labels added

| # | Equation | Verdict |
|---|---|---|
| 1 | No-slip conditions ω_w1 r_w1 = V_b + r_b ω_b and ω_w2 r_w2 = V_b − r_b ω_b; ω_w2 = Gω_w1; ω_b > 0 is backspin | Confirmed, PDF p.2–3 (§2.1 item 8, §2.2: "negative value for ω_b, where the ball has top spin") |
| 2 | Eq (1) and Eq (2) | Confirmed, p.3 |
| 3 | Eq (3), Eq (4) and Eq (5) | Confirmed, p.3–4 |
| 4 | I_w = I_w1 + G² I_w2 | **Not stated in this form in the PDF.** The PDF defines I_w as the "total virtual moment of inertia at the first flywheel's axis" (§2.1 item 9) and gives the example I_s + 2.5² I_f (App. A.1). The explicit form is in the sheet, 'Double Flywheel' B11 `=B8+B9*B10^2`. |
| 5 | Closed-form ω_w1f, V_bf, ω_bf (boxed). The box also gives ω_w2f = Gω_w1f, which the extractor omitted. | Confirmed, p.5 |
| 6 | S_exit = (r_w1 − G r_w2)/(r_w1 + G r_w2) | Derived, correctly, from (1) and (2). Not printed in the source. S is negative (topspin) when G r_w2 > r_w1. |
| 7 | App. A: L_b,w, Eqs (6)–(10), H_h points forward | Confirmed, p.7–8. "Perhaps counterintuitively … the hood pushes the ball forwards" (p.7). |
| 8 | Hooded ω_wf, V_bf, ω_bf (boxed) | Confirmed, p.10. The sheet uses the same formula in 'Single Flywheel' D13. |
| 9 | From rest: V_bf = (r_w ω_wi/2)/[1 + m_b r_w²(1+k)/(4I_w)]; η_tot = 1/(2+a); η_lin → 1/(2(1+k)) | **Derived by the extractor**, not printed. The derivation is correct: substituting I_w = k_w m_w r_w² gives Brettle's ratio and efficiency. At k = 1, 0.4 and 0 it reproduces the §2.5 table values 25.0%, 35.71% and 50%. |
| 10 | ReCalc as coded: V = ω r_w · 20I_w / (7m_b(2r_w)² + 40I_w); E_loss = 0.7 m_b V² | Confirmed, sheet 'Recalc Comparison' columns M and N. This is **Pedersen's transcription** of ReCalc; ReCalc's own code was not checked. The constants 7 and 0.7 hard-code k = 0.4 (solid sphere). The reduction to (ωr_w/2)/(1 + 0.7 m_b r_w²/I_w), i.e. "halves I_w", is confirmed numerically, see A3. |
| 11 | Compound: run the hood stage, then pass its result to the roller stage as the initial condition | Confirmed, §2.4 p.5. The sheet passes the full system I_w (22.7 lbm·in²) to the hood stage as well. |
| 12 | Frictionless hood gives S = 1/k and V = u·k/(1+k) | **Extractor's derivation; I verified it by algebra.** With H_h = 0: mV = H and I_b ω/r_b = H, so r_b ω = V/k. With wheel no-slip, V(1 + 1/k) = u. S = 1/k for any I_w; V = u·k/(1+k) needs I_w → ∞. |
| 13 | Passive free roller, 6×6 impulse model | **Extractor's derivation, not in the source.** I solved it independently with r_b = 0.0355, r_w = 0.049, r2 = 0.0254, k = 2/3, I_w = 5e-4, 4000 rpm, ball from rest. See the table after this one. |

Results of my independent solve for row 13:

| I2 (kg·m²) | V (m/s) | S |
|---|---|---|
| 1e-6 | 8.086 | 1.422 |
| 1e-5 | 8.995 | 1.175 |
| 1e-4 | 9.652 | 1.026 |
| 1e-2 | 9.772 | 1.000 |

Shot-to-shot drift with I2 = 1e-5, no bearing drag and the roller keeping its spin between shots: S = 1.175, 1.295, 1.373, 1.422, 1.453. This rises toward 1/k = 1.5. All of these match the extractor's numbers.

## Data points

### Confirmed (12)

1. **§2.5 table, p.6, single wheel.** Linear efficiency 25.0% (hollow cylinder), 35.71% (solid sphere), 50.0% (dense core). Total efficiency 50.0% for all three.
2. **§2.5 table, single wheel.** Total efficiency 50.0% for all projectiles.
3. **§2.5 table, double.** 50.0% for all projectiles. Linear efficiency equals total efficiency when r_w1 = G r_w2 (table note).
4. **'Single Flywheel' tab.** Wheel 5940 → 5210.53 rpm (622.04 → 545.65 rad/s). V = 13.859 m/s (45.470 ft/s). Spin 184.65 rad/s (1763.3 rpm). Inputs: r_b 0.075057 m, m_b 0.22680 kg, I_b = 2/5·m·r², r_w 0.0508 m, I_w 5 lbm·in² (1.4632e-3 kg·m²).
5. **Same tab.** Flywheel loss 65.258 J, ball linear energy 21.782 J, ball total energy 30.495 J, η_lin 33.38%, η_tot 46.73%.
6. **Same tab.** H_w = 2.2003 N·s, H_h = 0.94298 N·s (positive, i.e. forward), m_b ΔV = 3.1433 N·s.
7. **'Double Flywheel' tab.** V 6.2429 m/s, spin 11.882 rad/s (113.47 rpm, backspin), wheel 1 150 → 140.449 rad/s, η_lin 47.96%, η_tot 48.36%. Inputs: r_w1 2 in, r_w2 0.5 in, I_w1 20 and I_w2 0.3 lbm·in², G = 3.
8. **'Compound Flywheel' tab.** After the hood stage: V 3.6960 m/s, spin 49.243 rad/s (S = 1). Final: V 6.3030 m/s, spin 11.997 rad/s, η_lin 56.68%, η_tot 57.14%.
9. **Exit speed at 5940 rpm.** Pedersen 13.859 / 14.766 / 15.265 / 15.528 m/s against ReCalc 12.344 / 13.859 / 14.766 / 15.265 m/s, for MOI 5 / 10 / 20 / 40 lbm·in². These are cached values in sheet row 104 and are plotted on PDF p.12. The plot itself has no data labels.
10. **Energy loss at 5940 rpm.** Pedersen 65.26 / 71.65 / 75.29 / 77.23 J against ReCalc 24.19 / 30.49 / 34.61 / 37.00 J, from the same row and plot.
11. **Compression plot (#6).** The "~1.6" annotation is handwritten in red at the extrapolated dotted trend line at 0 mm.
12. **56% ratio.** rafi's text says "~1.6J … instead of ~0.9J" and "about 56%" (0.9/1.6 = 0.5625).

I also checked the compound table values independently, by a hand impulse derivation with I_w → ∞ and r_w1 = G r_w2:

| Projectile | Stage-1 loss | Stage-2 loss | Total loss | Ball KE | Efficiency |
|---|---|---|---|---|---|
| k = 0 | 0.25 m u² | 0.5 m u² | 0.75 m u² | 0.5 m u² | 66.7% |
| k = 0.4 | | | 0.85 m u² | 0.5 m u² | 58.8% |
| k = 1 | | | 1.0 m u² | 0.5 m u² | 50% |

These match the table.

### Corrected (2)

- **Compound efficiency qualifier.** The extractor wrote "50.0 / 58.8 / 66.7% (at r_w1 = G r_w2)". The table notes say: "For Double and Compound, both efficiencies match when r_w1 = G r_w2" and "Compound efficiencies are maximized in Dense Core when r_w1 = G r_w2". The table gives one number per cell and does not say whether it is linear or total efficiency, except via these notes. My hand check above shows that at r_w1 = G r_w2 all three values are reached, with exit S = 0.
- **Y-axis of the compression plot.** The axis reads "ENERGY TRANSFERED (J)" and the plot title is "Impact of compression on energy transfer to a projectile". It is rafi's text, not the plot, that calls this "linear kinetic energy". The setup is described only as "a small tennis ball flywheel launcher" by a GryphonRobotics student.
  - The values are confirmed by eye to ±0.01 J: 0 mm 0.00, 1 mm 0.39, 2 mm 0.84, 3 mm 0.90, 4 mm 0.74, 5 mm 0.60, 6 mm 0.51, 7 mm 0.43, 8 mm 0.34.
  - Error bars are on x only, about ±0.1–0.15 mm. There are none on y.
  - "Compression" is not defined; it may mean diametral interference.

### Dropped (0)

None.

### Added (8)

- **A1. Single-wheel tab, extra values.** Initial flywheel energy 283.08 J. Angular momentum about the wheel centre goes 0.9102 → 1.0996 kg·m²/s. The change, 0.18946, equals H_h(r_w + 2r_b), which is the sheet's own consistency check (D29–D35).
- **A2. ReCalc final wheel speed (energy-based column L), sheet row 104.** ReCalc gives 594.87 / 605.05 / 612.45 / 616.93 rad/s against Pedersen's 545.65 / 581.34 / 601.00 / 611.34 rad/s, for MOI 5 / 10 / 20 / 40, starting from 622.04 rad/s. ReCalc's velocity formula alone would imply a wheel speed of 2V/r_w = 486 rad/s at MOI 5, so ReCalc is internally inconsistent. This resolves the extractor's caveat about Brettle vs Pedersen: Brettle's claim that 846 overpredicts the speed drop by 2× concerns the velocity/ratio formula, while Pedersen's claim that ReCalc underestimates energy drain concerns the 100%-transfer energy column. Both hold.
- **A3. ReCalc at MOI 2X equals Pedersen at MOI X, exactly.** ReCalc V at MOI 10 is 13.8594, equal to Pedersen's V at MOI 5. ReCalc E_loss at MOI 10 is 30.4945 J, equal to Pedersen's ball total KE at MOI 5. This confirms "effectively cut the flywheel inertia in half" (App. B p.11).
- **A4. Compound tab, intermediate values.** Wheel 1 drops 150 → 145.51 rad/s in the hood stage. Hood-stage impulses: H_w 0.5868, H_h 0.2515 N·s. Roller-stage impulses: H_w 0.1688, H_h 0.4224 N·s. The roller stage cuts the spin from 49.24 to 12.00 rad/s.
- **A5. Exit S in the double and compound examples is 0.143.** This is derived from the sheet values (11.997 × 0.075057 / 6.303 = 0.1429) and equals (2 − 1.5)/(2 + 1.5). In other words, the paper's geared "hood roller" example is a low-backspin configuration.
- **A6. Qualitative claim, PDF §3 p.6, no numbers given.** "passing the ball into the shooter with initial velocity doesn't significantly increase the exit velocity, but drastically increases the efficiency of the shot, particularly for double flywheel shooters." Also on p.6: both the single and double shooters have a maximum efficiency of 50% "starting from rest".
- **A7. Reply #6, rafi's interpretation, qualitative.** The left zone of the plot is where the ball "still slips when it exits the shooter". The right-zone losses are "mostly driven by geometry, not the mechanical work to compress the ball". rafi expects no slip and no compression to be the "most significant" errors in the model.
- **A8. Reply #5, Alex_Y, qualitative.** The motors add energy during the shot, limited by controller bandwidth, discretisation, filtering lag and CAN latency, which could be "collapsed into a single bandwidth variable". "Even a few ms of recovery while shooting will significantly change the shot behavior". Low-inertia shooters work for this reason.

## Other corrections to the extraction text

- **ball_and_method.** The FRC 2026 "fuel" ball is not stated to be a solid sphere. The sheet *assumes* I_b = 2/5·m·r² (B5 `=2/5*B4*B3^2`, giving 1.746 lbm·in² = 5.111e-4 kg·m²) for a 5.91 in, 0.5 lbm ball. The paper never describes the fuel's construction.
- **Model implication 5.** The per-shot drain at 10 m/s is "at least about 2× ball KE". With m = 25 g, the ball's KE is 2.08 J for k = 2/3 and 1.75 J for k = 0.4. At I_w = 5e-4, η_tot = 0.488, so the drain is about **3.6–4.3 J**, not "4–5 J".
- **POLLEN numbers.** These were recomputed and agree:
  - Inertia factor: 0.667–0.704, 0.800–0.826, 0.909–0.922, 0.952–0.960 and 0.976–0.979 for k = 2/3 to 0.4.
  - At 2000 rpm: wheel drops to 1904.7 rpm, V = 4.887 m/s, spin 1314.5 rpm.
  - At 4000 rpm: wheel drops to 3809.4 rpm, V = 9.774 m/s, spin 2629 rpm.
  - 269 rpm per m/s; 818–4093 rpm for 2–10 m/s.
  - All of these use HANDOFF's R_b = 0.0355 m, which is nominal and unmeasured.
- **Phrase "under 5%".** At I_w = 5e-4 and k = 2/3 the drop is 4.8%, so the claim only just holds.

## Missing physics worth stating, and limits of the check

- The no-slip-at-hood condition needs |H_h| ≤ μ·(normal impulse). Neither the paper nor the sheet computes normal impulses, so the friction needed for "S = 1" is never checked.
- The source contains nothing on aerodynamics, perforated balls, hollow shells, compression laws or POLLEN.
- I did not re-run Brettle's notebook. The Brettle equivalence rests on algebra plus `checks/brettle.md`.
- I did not check ReCalc's own source code.
- The tennis-ball setup is unknown: ball mass, wheel, rpm and measurement method are all unreported.
