# Fact-check: Emond, Sun & Swartz (2024), "Pickleball Flight Dynamics" (extraction id `emond2024`)

Checker: independent re-read on 2026-10-30. The extraction under check is research/papers/emond2024.md.

Sources the checker re-opened:
- https://arxiv.org/pdf/2409.19000 (arXiv:2409.19000v1, 19 Sep 2024, 15 pages). Full text, read in full.
- https://www.sfu.ca/~tswartz/papers/emond.pdf (earlier SFU draft, 12 pages, no appendix). Diffed against the arXiv text.
- https://api.crossref.org/works/10.30827/ijrss.32618 (journal metadata).
- GitHub 0Strategist0/Pickleball: main/pickleball_solving.py, main/pickleball_plotting.py, paper-plots/pickleball.py, paper-plots/ball.csv, paper-plots/pickleball_fiiting.py.
- Version of record: revistaseug.ugr.es (article page and both PDF download links) and digibug.ugr.es all returned an Anubis "Access Denied" bot-check page. They were not bypassed, so the journal text is **not verified**.

Own reproduction: an independent Python reimplementation of eq.7 with the authors' constants (rtol 1e-10). A second run mirrors the authors' fsolve logic (guess 10.08 m/s, default solve_ivp tolerances).

## Verdict
The extraction is accurate and unusually careful. Every Table 1 number, constant, equation typo and page location matches the arXiv v1 text. The figure values match an independent reproduction.

Corrections:
- One Table 1 entry is not reproducible: x0 = 0, z0 = 44, D20 = +0.089 s. The authors' own code logic gives -0.733 s.
- The extractor's Reynolds-number range was computed from launch speed, not air-relative speed.
- The figure-digitized launch speeds carry false precision.
- The text's "about 24 mph at 27 ft" is about 1-2 mph above what the model produces.
- The drop-test scatter is about 0.06 s SD, not plus or minus 0.1 s.

The extraction missed these important items:
- The authors' own 60 mph speed cap is violated by several Table 1 headwind cases, which need up to about 101 mph.
- The unsourced claim that the ball "compresses only negligibly".
- A text-versus-table contradiction.
- Unsupported claims in the appendix about Cd.

CHECK: 10 confirmed / 5 corrected / 0 dropped / 10 added

## Bibliographic / review status
- Crossref: journal-article in International Journal of Racket Sports Science, vol 6, issue 2, published online 2024-12-30, CC BY 4.0, 9 references. The Crossref title field is Spanish ("Dinamica de vuelo en pickleball"), and so is the deposited abstract. Crossref gives no page range. A search-engine snippet says pp. 1-8, which is unverified. A digibug repository record (seen only in search results) dates it 2025-01-11.
- IJRSS states a double-blind, two-reviewer peer-review policy. This comes from search-result snippets of the journal's editorial-policy page, which is also behind Anubis. The extractor's review_status is correct: the paper is peer-reviewed, but the content actually checked is the unreviewed arXiv v1 preprint. Any changes made in review are unknown.
- The SFU draft and arXiv v1 have an identical Table 1, including the anomalous +0.089. The draft has no appendix (no Cd, no eq.5-7). It also carries the authors' note "We need to verify the sensitivity comment ... related to theta and y0".

## Equations

| Extracted | Source | Status |
|---|---|---|
| F_d = -1/2 rho Cd A (v-(w,0))\|v-(w,0)\| | eq.5, p.13 | confirmed |
| Re = rho U D / mu | eq.6, p.13 | confirmed. mu is never given a numeric value. |
| m x'' = -1/2 rho Cd A (x'-w) sqrt((x'-w)^2 + y'^2) | eq.7a, p.15 | confirmed |
| m y'' = -m g - 1/2 rho Cd A y' sqrt(...) | eq.7b, p.15 | confirmed as a correction. The printed text reads "-g" and "(y'(t) - w)". The code (`vy_derivative = -gravity - drag_coef*vy*sqrt(...)`) confirms both are typos. |
| k = rho Cd A/(2m) = 0.0645 1/m; v_t = 12.3 m/s | code DRAG_COEF | confirmed: k = 0.064513 1/m, v_t = 12.33 m/s, A = 4.3008e-3 m^2 |
| y(t_b) = 0, x(t_b) = 44 ft; x(t) = z0; D_w = t_w - t_(-w) | eq.3 p.6, eq.4 p.6, p.10 | confirmed |
| ICs (x0, y0), (v0 cos theta, v0 sin theta) | eq.7, p.15 | confirmed |

## Data points: confirmed (10)
1. **Cd = 0.6, constant.** p.14: "treating the pickleball as a forward-facing wiffleball and using the experimental results found by Rossmann et al. [8] ... a constant Cd of approximately 0.6". Confirmed.
2. **Cd variation of plus or minus 0.5.** p.15: "could in principle vary by roughly +/-0.5 in certain conditions"; "signs ... preserved"; magnitudes "could be significantly different". No numbers are given. Confirmed.
4. **g, rho, A, m.** p.15: "g ... 9.18 m/s2" (typo; code uses 9.81), rho = 1.2 kg/m^3, A = pi(37 mm)^2, m = 24 g. Confirmed.
5. **k = 0.0645 1/m, v_t = 12.3 m/s.** Derived, confirmed.
6. **Fastest shots about 60 mph.** p.4: "roughly 60 mph" (the SFU draft says "only 60mph"). Unsourced. Confirmed.
9. **Minimum speed along the path.** The reproduction gives 19.0 mph at x = 39.6 ft (w = 0) and 13.9 mph at x = 40.4 ft (w = -10 mph). Confirmed.
10. **Apex heights.** The reproduction gives 7.52 / 6.12 / 5.53 / 5.40 ft for w = -10/0/+10/+15 mph, at x = 30.4 / 26.6 / 24.6 / 24.2 ft. Confirmed.
12. **Table 1, x0 = 11 rows.** The values match p.10 verbatim. The reproduction gives 0.082 / 0.151 / 0.243; 0.058 / 0.134 / 0.255; -0.230 / -0.375 / -0.568. Confirmed.
13. **Table 1, x0 = 15 rows.** The values match p.10 verbatim. The reproduction gives 0.075 / 0.132 / 0.204; 0.059 / 0.124 / 0.224; -0.203 / -0.332 / -0.505. Confirmed.
15. **POLLEN Cd sensitivity (the extractor's own calculation).** The checker recomputed it. At 7 m/s and 60 deg the crossing is 3.86 / 3.43 / 3.26 / 3.10 / 2.68 m and the angle is 53.65 / 55.26 / 55.89 / 56.44 / 57.75 deg. At 8 m/s and 55 deg the crossing is 5.58 / 4.82 / 4.52 / 4.26 / 3.59 m. Confirmed; the only difference is 3.43 against 3.44 at Cd 0.3. This is not from the source.

## Data points: corrected (5)
3. **Reynolds number.** The source statement "Re ~ 2.5e4" (p.14) is confirmed. The extractor's own "simulated drives at 11-19 m/s are about 5.6e4-9.3e4" is wrong: it uses ground-frame launch speed and ignores the wind. With mu = 1.81e-5, D = 0.074 m and air-relative speed, the checker's numbers are:
   - Fig. 2/3 runs span Re of about 1.8e4 (w = +15 mph, late flight) to 1.1e5 (w = -10 mph, launch).
   - Table 1 headwind cases reach a launch-plus-wind speed of about 54 m/s, so Re is about 2.6e5.
   - The stated 2.5e4 is therefore at the low end, not representative.
7. **Fig. 3 launch speeds.** "42 / 31.7 / 27 / 25.7 mph (digitized)" has false precision for figure reads. Use the reproduction instead: 41.98 / 31.79 / 27.05 / 25.80 mph = 18.77 / 14.21 / 12.09 / 11.53 m/s (my calc). The paper only states the ordering: v0 is greatest against the wind (p.8).
8. **Speed at x = 27 ft.** The text (p.8) says "approximately 24 mph" for all four winds. The reproduction gives 22.3 / 21.6 / 22.8 / 23.2 mph. The convergence claim holds, but the level is about 1-2 mph lower than stated.
11. **Table 1, x0 = 0 rows.** All nine values are transcribed correctly from p.10. However, the entry **z0 = 44, D20 = +0.089 s is not reproducible**:
    - The independent solver and a replica of the authors' fsolve logic (guess 10.08 m/s) both give **-0.733 s** (t_b = 1.090 s with the wind, 1.822 s against it). The other eight entries in this block reproduce to within 0.001 s.
    - The entry also breaks the column trend (-0.302, -0.490, then +0.089).
    - Treat it as an error in the paper.
14. **Repo drop test.** The checker confirms the fitted k = 0.201 +/- 0.024 1/m (implied Cd 1.87 for a 24 g, 37 mm ball), RMS 0.070 s against 0.102 s in vacuum, 63 points (21 heights x 3 trials) and h = 0.178-4.272 m. Correction: the trial scatter is a mean per-height SD of **0.064 s**, not about plus or minus 0.1 s. Fall-time sensitivity is confirmed: 0.933 s in vacuum against 0.977 s at k = 0.0645 for h = 4.272 m, a difference of 0.043 s. The data are unpublished, with unknown ball and timing method (the 0.01 s resolution suggests a hand stopwatch). The data are unusable.

## Data points: added (10)
- A. **Stated input ranges (pp.3-4):**
  - x0 in (0, 15) ft, y0 in (1, 3) ft, theta in (10, 30) deg ("larger than 30 either represents a lob shot or a mishit"), z0 in (29, 44) ft, |w| in (10, 20) mph.
  - Winds under 10 mph are called "largely inconsequential" from personal experience.
  - The SFU draft had y0 in (0, 7) ft and theta in (0, 30) deg.
- B. **Ball compression claim (p.4):** "the ball is hard and compresses only negligibly". This is an unsourced assertion used to justify the 60 mph cap. Do not use it as evidence on POLLEN compression; that question needs Van Wyk 2026 or POLLEN measurements.
- C. **Launch speeds exceed the paper's own cap (my calc).** Optimal-drive v0 against the wind at theta = 20 deg, y0 = 3 ft:

  | x0 (ft) | -10 mph | -15 mph | -20 mph |
  |---|---|---|---|
  | 0 | 57.3 mph | 72.8 mph | 100.9 mph |
  | 11 | 42.0 mph | 51.6 mph | 68.2 mph |
  | 15 | 37.0 mph | 44.9 mph | 58.4 mph |

  Three Table 1 columns therefore rest on launch speeds above the 60 mph maximum the paper states on p.4. The paper never mentions this.
- D. **Sensitivity to theta and y0 (my calc).** p.10 claims Table 1 is "not greatly sensitive to minor modifications" of theta and y0. The SFU draft flags this as unverified. The paper-plots code has a sweep over y0 in {2, 3, 4} ft and theta in {10, 20, 30} deg, but no results are published. Re-running that sweep:
  - All signs are preserved.
  - Magnitudes vary 3-5x. For example, at x0 = 11, z0 = 29, D20 ranges 0.103-0.442 s; at x0 = 0, z0 = 44, D20 ranges -1.491 to -0.310 s.
  - So the claim holds only for signs.
- E. **Descent angle at landing (my calc; the paper is qualitative only).** For the Fig. 2 runs the descent angle is 60.0 / 38.6 / 30.3 / 28.4 deg below horizontal for w = -10 / 0 / +10 / +15 mph. The paper says (p.7) that against the wind the ball is "moving more in a downward vertical direction than horizontally". This matters for PM-001: with a 20 deg launch and drag alone, the descent steepens from 39 to 60 deg only through about 4.5 m/s of extra relative airspeed.
- F. **Unsupported validation claim (p.15):** Cd = 0.6 "seems to produce pickleball trajectories and velocities similar to what is often measured". No measurement or reference is given. The Discussion (p.11) concedes the results still need checking "against video taken from pickleball matches".
- G. **Questionable physics claims in the appendix (pp.13-14):**
  - "Cd roughly proportional to Re^-1 for low Reynolds numbers" is true only in the Stokes regime, Re < ~1.
  - "we expect the holes in a pickleball to reduce the Reynolds number required to produce a roughly constant Cd to a value even lower than 10^3" is speculation, with no data.
  - Fig. 4 is a smooth-sphere and smooth-cylinder curve copied from Munson et al.
- H. **Text contradicts Table 1 (p.11).** The text says D_w increases with w for x0 = 15, z0 = 29, and "this same phenomenon is observed in all situations in Table 1 whenever z0 = 44 feet". In the z0 = 44 rows, D_w becomes more negative as w grows (for example -0.203, -0.332, -0.505). Only |D_w| grows, and the x0 = 0 row flips sign through the anomalous entry.
- I. **Solver details (p.15 and code):** solve_ivp RK45 with default tolerances; fsolve on (x - 44, y). The code uses a terminal ground event, with initial guesses of 10.0 m/s (main) and 10.08 m/s (paper-plots).
- J. **Spin is explicitly excluded (p.5):** "In our model, we ignore the impact of spin." There is no lift term and no spin decay. The extractor stated this but did not list it as a data point.

## Text-level corrections to the extraction
- Caveats: "SFU draft notes the theta/y0 sensitivity claim was unverified". This is true of the draft. The paper-plots code later contains a sweep, so the authors probably checked it before arXiv, but published no numbers. See item D.
- pollen_applicability: "Re about 2.5e4 ... inconsistent with their own simulated speeds" stands, but the correct span is about 1.8e4-2.6e5 (item 3).
- model_implications point 3: the checker verified the band "Cd 0.3-0.6 moves the 1.12 m crossing 0.15-0.56 m, 0.5-2 deg" only at 7 m/s (0.33 m, 1.2 deg) and 8 m/s (0.56 m, 1.7 deg). The 0.15 m lower bound (presumably 6 m/s) was not rechecked.
- The page locations given by the extractor are correct for arXiv v1: Fig. 2 p.8, Fig. 3 p.9, Table 1 p.10, Appendix pp.12-15.

## Bottom line for PM-001
- This is a peer-reviewed but simulation-only, spin-free, drag-only paper with a borrowed wiffle-ball Cd.
- Use it only for the baseline ODE structure (eq.7 corrected) and the shoot-and-root-find workflow.
- It provides no Magnus, Cl, spin-decay, compression or collision data.
- Its numbers are internally reproducible except Table 1 (x0 = 0, z0 = 44, D20).
- Keep Cd as a swept parameter (0.3-0.7) until POLLEN Cd is measured by high-speed video.
