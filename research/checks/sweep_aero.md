# Fact-check: sweep_aero (Magnus, drag and spin decay of light / hollow / perforated balls)

PM-001 · checker agent · 2026-10-30
Extraction under review: research/sweeps/sweep_aero.md (8-source topic sweep).

**CHECK: 15 confirmed / 4 corrected / 0 dropped / 9 added**
Two corrections also apply to equations and text in the sweep body (not counted as data points): the spin-decay formula there uses R³ where it should be R², and the source for the "Tavares C_M = 0.012 S" figure is upgraded from "patents only".

## What I re-opened

| id | What I opened | Access achieved |
|---|---|---|
| muto2012 | Hokkaido author-repository PDF, 17 pp. I read the text and rendered pp. 014102-5, -7 and -9 to read Table I, Fig. 7 and Fig. 8 directly. | full text |
| conti2026 | arXiv HTML v2 (1 Jul 2026). Sec. III-A, III-B (Tables I–III, Eqs. 1–5) and IV-A read in full. I recomputed every CL value from Tables II–III. | full text |
| vilumbrales2024 | arXiv PDF v1. Text, Eqs. 1–2, Figs 2–4. The arXiv abstract page shows v1 only, with no journal-ref. | full text |
| sareen2024 | Monash Research Portal record. | abstract only (paraphrased by the fetch tool, plus one verbatim sentence) |
| kim2014 | Cambridge Core landing page, plus the APS-DFD 2011 abstract page, which is truncated. | abstract only |
| miyazaki2017 | UEC press release and an abstract search snippet. IOP blocked by a bot wall, ADS returned 405, ResearchGate 403. | abstract (snippet) only |
| james2008 | SPONET record. | abstract only |
| briggs1959 | Search results only (APS News; Kharlamov 2007). | secondary only |
| Tavares (secondary) | McBeath, Nathan, Bahill & Baldwin, "Paradoxical pop-ups: Why are they hard to catch?", arXiv:0803.4357 (2008), §II-E, read in full. | full text of the secondary source |

## Bibliographic data and review status

| id | Verdict | Notes |
|---|---|---|
| muto2012 | CONFIRMED | Phys. Fluids 24, 014102 (2012). Peer-reviewed, LES (numerical, not experiment). |
| conti2026 | CONFIRMED, minor fix | arXiv:2606.28805v2, cs.RO, 1 Jul 2026. Unreviewed preprint. There are 7 authors (Conti, Yang, Sigrist, Miele, Saraiji, Dürr, Takahashi), so the "et al." in the sweep is unnecessary. ν = 1.506e-5 m²/s at 20 °C; Re = 2vr/ν. |
| sareen2024 | CONFIRMED | Sareen, Hourigan, Thompson. IJHFF 109, 109501 (Oct 2024). Peer-reviewed experiment. |
| kim2014 | CONFIRMED | Jooha Kim, Haecheon Choi, Hyungmin Park, Jung Yul Yoo. JFM 754, R2 (2014). Peer-reviewed (JFM Rapids). |
| miyazaki2017 | CORRECTED (independence) | Authors: T. Miyazaki, W. Sakai, T. Komatsu, N. Takahashi, R. Himeno (from the search snippet). This is the **same group, launcher type, ball type and Re/SP range as Sakai et al. 2016**, which is priority paper #8. It is very probably the journal version of the same measurement campaign. **It is not an independent measurement**, contrary to the sweep's "This is a different measurement from Sakai 2016". Peer-reviewed (Eur. J. Phys.). |
| vilumbrales2024 | CONFIRMED | arXiv:2407.01748 v1 only, with no journal reference as of today. Unreviewed preprint. Wind-tunnel experiment. |
| briggs1959 | CONFIRMED | Am. J. Phys. 27, 589–596 (1959), per APS News and the MaRDI catalogue. Secondary access only. |
| james2008 | CONFIRMED | James D., Haake S. The Engineering of Sport 7, Vol. 2, Springer (Paris), pp. 165–170 (2008). Conference proceedings. |

## Data points

| # | Item (source) | Verdict | Notes |
|---|---|---|---|
| 1 | CL 0.167 (s.d. 0.029), Re 1e4, Γ 0.2 (muto2012) | CONFIRMED | Table I, p. 014102-9, read from the rendered page. The table labels it CLz, but the text (p. 014102-6) defines CL from the y-direction force. That is a labelling inconsistency only. |
| 2 | CL 0.301 (s.d. 0.096), Re 1e4, Γ 1.0 (muto2012) | CONFIRMED | Table I. |
| 3 | CD at Re 1e4: Γ 0 printed 0.046 (Fig. 8 ≈0.45); Γ 0.2 0.474; Γ 1.0 0.661 (muto2012) | CONFIRMED | The rendered Table I prints 0.046 (s.d. 0.016). Fig. 8 (p. 014102-7) shows the open circle at Γ = 0 at ≈0.45, so the typo reading is right. |
| 4 | CL −0.250 (s.d. 0.041) at Re 2e5, Γ 0.2; +0.212 at Γ 1.0 (muto2012) | CONFIRMED | Table I. |
| 5 | Re windows for negative Magnus: Taneda 6e4–5e5, Maccoll 4.6e4–1.1e5, Davies 9e4 (muto2012) | CONFIRMED | Sec. II, p. 014102-2. The Γ < 0.6 limit is given there for all prior experiments together. The intro (p. 014102-1) adds that Taneda's diagram puts it "only in the neighborhood of" Re 2.5e5. |
| 6 | Downstream-moving-side separation at 93°, +6° vs no spin; upstream side unchanged; Re 1e4, Γ 0.2 (muto2012) | CONFIRMED | p. 014102-8, with Fig. 9. The no-spin separation at Re 1e4 is 87° (p. 014102-5). |
| 7 | Equivalent CL at v 3.5 m/s: 0.08/0.18/0.29/0.33/0.31/0.32/0.36 (conti2026) | CONFIRMED | Recomputed from Table II/III with Eq. 5 and CL = (8/3)·C_M·Sp. I get 0.078/0.175/0.285/0.331/0.313/0.319/0.362. The conversion follows from Eq. 2 with V = 4/3 πr³ and A = πr²: CL = C_M·(4/3 πr³·vω)/(½πr²v²) = (8/3)C_M·rω/v. |
| 8 | Equivalent CL at 7.5 m/s: 0.09/0.20/0.29/0.29/0.25/0.36/0.39 (conti2026) | CONFIRMED | Recomputed: 0.091/0.197/0.293/0.290/0.252/0.364/0.393. |
| 9 | Equivalent CL at 10.5 m/s: 0.09/0.19/0.27/0.23/0.26/0.41/0.39 (conti2026) | CONFIRMED | Recomputed: 0.091/0.192/0.270/0.232/0.259/0.413/0.391. |
| 10 | CD breakpoints at 2.5/7.5/12.5/17.5 m/s (conti2026) | CONFIRMED | Table I, Sec. III-B1. Every breakpoint and value matches. Reference Re values: 6,640; 19,920; 33,201; 46,481. The authors add that at low speed the CD estimates have high variance, and that the data concentrate in the ridge and trough regions with little data at high speed. |
| 11 | Fit quality: median 3D RMSE 8.1 mm vs 15.8 (Nakashima) and 9.7 (Dürr); 277 matches; ~58,000 segments (conti2026) | CORRECTED (location and wording) | The numbers are right. The RMSE result is in **Sec. IV-A / Fig. 4**, not Sec. III-B. The dataset (Sec. III-A) is "277 games" and "almost 58,000 flight trajectories". Trajectories with fit RMSE > 20 mm were excluded before fitting. |
| 12 | Sudden drop in CL and CD at a critical rotation ratio, then recovery; 1e3 < Re ≲ 5e4 (sareen2024) | CONFIRMED (abstract) | Verbatim: "A relatively sudden drop was observed in both the lift and drag coefficients at a 'critical' rotation rate." The record describes the recovery as partial. The critical value, the size of the drop and any sign change are not in the abstract. |
| 13 | Inverse-Magnus mechanism; APS 2011 precursor Re ≈ 0.6–2.6e5, spin ratio 0–0.5 (kim2014) | CORRECTED (provenance) | The mechanism matches the JFM abstract: the boundary layer on the side moving against the flow turns turbulent, separation is delayed, and lift turns negative. The JFM abstract gives **no** numeric Re or spin range. The APS-DFD 2011 page is truncated and shows no range; the 0.6–2.6e5 / 0–0.5 figures appear only in a search snippet. The snippet also says the tests were in the "subcritical" regime, so inverse Magnus appeared below the smooth-sphere drag crisis. The Sakai 2016 check (research/checks/sakai2016.md, item 23) reports Kim's test range as 6e4 < Re < 1.8e5, SP < 1.8. The two ranges conflict, so treat both as unverified. |
| 14 | Deep CL valley around SP 0.5; lift almost vanishes at Re 9.0e4, 0.48 < SP < 0.5; Re 3.0–9.0e4, SP 0–1.0 (miyazaki2017) | CORRECTED (independence; values confirmed) | Every number matches the abstract text quoted in search results, and the ball is the Nittaku 3-Star Premium. **Correction:** this is the Sakai 2016 group and campaign, not a separate measurement. The sweep's implication #2 counts it as a third independent source for a CL dip. It is not: only Sakai/Miyazaki (one campaign), Sareen 2024 and Conti 2026 are independent. |
| 15 | CLmax 0.40 at Re 1e5 (k/d 0.003); 0.35 at Re 7e4 (k/d 0.006); ≈80% of drag; CD ≈0.5, insensitive to k/d (vilumbrales2024) | CONFIRMED | Sec. 3.1, Fig. 2. **Note:** the paper attaches "approximately 80% of the drag" to the Re 7e4 case. With CD ≈ 0.5, CL 0.35 is ≈70%; 80% matches the 0.40 case. This inconsistency is the paper's own. Turbulence intensity is stated as Ti = 1.8%. |
| 16 | Re_c = 75000·exp(−431 k/d) + 49600; never below ≈5e4 for k/d ≤ 0.01 (vilumbrales2024) | CONFIRMED | Eq. 1. At k/d = 0.01, Eq. 1 gives 50,600, and its asymptote is 49,600. **Note:** Eq. 1 only roughly matches the examples in the text: 110,000 vs 100,000 stated for k/d 0.0005, and 81,000 vs ≈75,000 stated for k/d 0.002. Eq. 2 at k/d 0.003 gives 0.394, consistent with 0.40. |
| 17 | Smooth ball deflected opposite to baseballs, qualitative (briggs1959) | CONFIRMED (secondary) | Kharlamov 2007, as quoted in search results. The baseball result in the same paper: curve proportional to spin and to speed², for spins up to 1800 rpm and speeds up to 150 ft/s. |
| 18 | dω/dt linear in ω0·v0, ball-specific constant; inertia dominates, then roughness and boundary-layer regime (james2008) | CONFIRMED (abstract) | Verbatim: "a strong linear relationship between spin decay and the product of initial spin and speed". Balls tested: tennis, worn tennis, football, oversize tennis; two high-speed cameras, in a sports hall. |
| 19 | POLLEN spin loss over 1.2 s: 2–3% for k = 0.012, 4–9% for k = 0.03, 8–16% for k = 0.06 (attributed to james2008) | CORRECTED | Recomputed with τ = I/(ρ·A·R²·k·v), R = 35.5 mm, ρ = 1.2, I = 1.7–2.1e-5, v = 4–7. Results: k = 0.012 → **1.6–3.5%**; k = 0.03 → 4.0–8.5%; k = 0.06 → 7.9–16.3%; **k = 0.1 → 12.8–25.6%**. The sweep recommends k ∈ [0.01, 0.1] but then states the loss tops out at "about 16%". The upper end of its own band gives up to about 26%. **Attribution:** this is the extractor's derived calculation using the Tavares torque form. It is not a james2008 data point, and james2008 does not give the constant. I = 1.7–2.1e-5 corresponds to 0.54–0.67·mR², which brackets a thin shell (2/3·mR² = 2.10e-5). |

## Equations

| Equation | Verdict | Notes |
|---|---|---|
| muto2012: Γ = D_p·ω/U0 vs "ratio of circumferential velocity to incoming flow velocity" | CONFIRMED (ambiguity is real) | Both the formula and the wording are on p. 014102-2. Indirect evidence favours the wording (Γ = S): (a) Sakai 2016 cites Muto's case as "SP 0.2"; (b) CL 0.167 at Γ 0.2 gives CL/S ≈ 0.84 if Γ = S, matching the low-S slopes of Sakai (0.85–1.0) and Conti (0.83–1.02). If Γ = 2S, CL/S ≈ 1.67. This is inference, not resolution. |
| conti2026 Eq. 2 and Eq. 5, C_M ≥ 0 | CONFIRMED | Eq. 5 is linear for ω ≤ ω_b and quadratic above it. The two branches are nearly continuous at ω_b (mismatch ≤ 0.022 in C_M). Outside the tabulated range the function is clipped. |
| conti2026: CL = (8/3)·C_M·Sp | CONFIRMED | Derived above. This is the extractor's conversion, not printed in the paper. |
| vilumbrales2024 Eqs. 1–2 | CONFIRMED | Transcribed exactly. |
| Tavares spin decay, I·dω/dt = −R·ρ·A·C_M·v², C_M = β·S | CONFIRMED, source upgraded | No longer "patents only". McBeath et al. 2008 (arXiv:0803.4357, §II-E) gives the form with C_M = βRω/v and I = 0.4MR². It reports **β ≈ 0.012 (Tavares; τ = 20 s at 100 mph)** and **β ≈ 0.009 (Smits & Smith)**, both for golf balls. Primary source: Tavares, Shannon & Melvin, Science and Golf III (1999), pp. 464–472, which I have not seen. |
| key_equations: dω/dt = −(ρ·A·R²·k·v/I)·ω | CONFIRMED | Dimensionally correct. **But the sweep body (Implications §4 and model_implications item 4) writes I·dω/dt = −ρ·A·R³·k·ω·v. R³ is wrong:** it has an extra length and gives a torque in N·m². It should be R². The percentages in the sweep were computed correctly with R², so only the printed formula needs fixing. |
| CL_dip(S) Gaussian notch | n/a | The extractor's own proposal, correctly labelled. It is not from any source. |

## Added data points (missed by the extractor)

1. **muto2012, Fig. 7 (by eye, ±0.02).** At the critical Re 2e5 the LES lift stays negative across a band of Γ, not just at 0.2: CL ≈ −0.19 at Γ 0.1, −0.25 at 0.2 and **−0.24 at 0.5**. It turns positive at about +0.14 at Γ 0.8 and +0.21 at 1.0. Negative lift therefore spans at least Γ 0.1–0.5 in the critical regime.
2. **muto2012, Table I and p. 014102-7.**
   - At Re 1e4, Γ 1.0, the side force CLy is 0.064 (s.d. 0.052), and the lift s.d. is 0.096 (≈⅓ of the mean). The flow is markedly unsteady at high spin.
   - The authors themselves say their subcritical CD "disagreement … with previous experimental results … is quite substantial". This weakens using Muto's CD rise (0.45 → 0.66) as a quantitative CD(S) law.
3. **conti2026, rows not extracted (my recomputation from Tables II–III).** These two rows lie inside the POLLEN Re range, and the dip is deeper there:

   | v (m/s) | Re | CL at Sp 0.1 / 0.25 / 0.5 / 0.75 / 1.0 / 1.5 |
   |---|---|---|
   | 13.5 | 3.6e4 | 0.09 / 0.19 / 0.26 / **0.20** / 0.29 / 0.35 |
   | 17.0 | 4.5e4 | 0.09 / 0.18 / 0.24 / **0.17** / 0.23 / 0.37 |

   POLLEN reaches Re 3.6e4–4.5e4 at about 7.6–9.5 m/s, which is launch speed. The dip deepens with Re, which is consistent with Sakai/Miyazaki.
4. **conti2026, low-spin slope.** For ω → 0, C_M → s = 0.31–0.383 (v ≥ 3.5 m/s), so CL ≈ (8/3)·s·Sp ≈ **0.83–1.02·Sp**. At v = 2.0 m/s the fitted s = 0.08, which gives CL ≈ 0.21·Sp. This outlier is consistent with the authors' remark that low-speed estimates have high variance.
5. **conti2026, a clipping artefact.** At 13.5 m/s and Sp 2 (ω = 1350 rad/s), the quadratic gives C_M < 0, which is clipped to 0, so CL = 0. This is outside the data, not physics. Do not sample the Conti model at Sp ≈ 2 for v ≥ 13.5 m/s.
6. **conti2026, a model assumption.** The coefficients are fitted per trajectory and indexed by a force-averaged v_eff (Eqs. 3–4). No in-flight spin decay is modelled, so any spin decay is absorbed into the fitted C_M.
7. **vilumbrales2024, sensitivity of lift to a separation asymmetry (§3.2, Fig. 4).**
   - At Re 7e4, k/d 0.003: CL ≈ 0.2 with a separation-angle difference of only ≈5° (±3° PIV error).
   - Dimple geometry: d_d/d = 0.087, 148 dimples on one hemisphere, 55.6% coverage.
   - So a few degrees of left/right separation asymmetry is enough for CL ≈ 0.2. This is relevant to any hole-pattern asymmetry on POLLEN, but it was measured at Re ≥ 7e4.
8. **New source: Sudarsana, Singh, Sareen, arXiv:2607.03878 (4 Jul 2026).** Preprint, wall-resolved LES, abstract only. At Re 1e5 with k/d 0.004–0.008 on one side:
   - the smooth side separates laminar at ≈80°;
   - the dimpled side separates at ≈105–125°, unevenly;
   - lift is amplified by a counter-rotating streamwise vortex pair (sidewash).

   This explains the mechanism of the vilumbrales2024 data. No CL values are given in the abstract.
9. **Tavares/Smits spin-decay constants, golf (via McBeath et al. 2008).** β ≈ 0.012 (Tavares) and ≈ 0.009 (Smits & Smith). The paper also notes Adair's suggested τ ≈ 5 s, which it says "does not seem to be based on any experimental data".

## Other notes on the sweep body (not counted)

- **Wiffle snippet arithmetic.** q at 40 mph = ½·1.2·17.88² = 192 Pa, not 196. CL ≈ 0.24 stands. The 74 mm diameter is an assumption, and the whole item remains unverified.
- **Model-implications item 1.** The CL slope band 0.55–1.2·S for S ≤ 0.5 is wider than the sources support at low S. Conti, Sakai, and Muto (if Γ = S) give 0.83–1.0·S near S → 0, falling to ≈0.54–0.58·S at S = 0.5 (CL 0.27–0.29). The 1.2 upper end is supported only by the Γ = 2S reading of Muto.
- **Negative-Magnus statement.** "Documented only at Re of about 4.6e4–2e5" is fair for spheres in wind tunnels. Two qualifications:
  - Kim 2011 calls its range "subcritical".
  - Free-flight table-tennis data (Sakai/Miyazaki; Conti, whose model cannot go negative) show near-zero lift at Re 9e4, SP ≈ 0.5, but not a reliable sign reversal.
