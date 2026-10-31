# Emond, Sun & Swartz (2024): Pickleball Flight Dynamics

source_id: `emond2024`. Deep-read for PM-001 (FTC BIOBUZZ POLLEN backspin/Magnus shooter). Read on 2026-10-30.

## Citation

Emond, K., Sun, W., & Swartz, T. B. (2024). *Pickleball Flight Dynamics* (Spanish title on Crossref: "Dinámica de vuelo en pickleball"). *International Journal of Racket Sports Science*, 6(2). Published online 2024-12-30. DOI: [10.30827/ijrss.32618](https://doi.org/10.30827/ijrss.32618). License: CC BY 4.0 (Crossref metadata).
Preprints: arXiv:2409.19000v1 [physics.soc-ph], 19 Sep 2024 (the only arXiv version), and SportRxiv DOI 10.51224/SRXIV.456 (posted 2024-09-23). Code: https://github.com/0Strategist0/Pickleball (branches `main` and `paper-plots`).
Affiliations: Simon Fraser University. Emond is a physics undergraduate, Sun is in mathematics and Swartz is in statistics.

## Access level and versions read

| Version | Status | Notes |
|---|---|---|
| Journal version of record (revistaseug.ugr.es) | **Not read** | Every journal URL, including the PDF galleys `/article/download/32618/28534` and `/29355` and the UGR repository record digibug 10481/102323, returned an "Anubis" bot-check page. I did not bypass it. The Chrome extension was not connected. |
| arXiv 2409.19000v1 (15 pp.) | **Full text read** | This is the main source for this note. Page numbers below are arXiv pages. |
| SFU draft (sfu.ca/~tswartz/papers/emond.pdf, 12 pp., created 2024-09-06) | Full text read | An earlier draft. The appendix is still a placeholder ("Probably we refer to a github page…") and it has the same Table 1. |
| GitHub code (`pickleball_solving.py`, `pickleball_plotting.py`, paper-plots `pickleball.py`, `pickleball_fiiting.py`, `ball.csv`) | Read | Confirms the constants and corrects typos in the printed equations (see below). |

Crossref links the journal abstract. It matches the arXiv abstract in content. **I could not check whether the version of record changed any numbers.** I reproduced the arXiv Table 1 and Fig. 3 numerically (see "Independent reproduction"), so the arXiv model and numbers are internally consistent.

## Review status

- The journal version (IJRSS) is a peer-reviewed open-access journal article. The arXiv and SportRxiv versions are unreviewed preprints.
- **There is no original experimental data in the paper.** It is a pure simulation study. The authors say they "could not find any experimental measurements of Cd for pickleballs" (arXiv p.14). They took Cd from a wiffle-ball wind-tunnel study (Rossmann & Rau 2007) and did not measure it.
- **No lift, spin, Magnus force or spin decay is modelled.** The authors write "In our model, we ignore the impact of spin." (arXiv p.5)
- The `paper-plots` branch of the repository holds an unpublished drop-test file (`ball.csv`) and a drag-fit script. The paper never mentions or uses them. They are unreviewed and their provenance is unknown. See the data section.

## Method

1. A 2D point-mass projectile with gravity and quadratic drag with a **constant** Cd. Wind is horizontal and constant, and enters only through the relative velocity.
2. Integration uses SciPy `solve_ivp` (explicit Runge–Kutta 5(4), Dormand–Prince).
3. The "optimal drive" condition: for a given (x0, y0, θ, w), solve for the launch speed v0 and the bounce time t_b so that the ball lands exactly on the far endline (x = 44 ft, y = 0). The code uses `fsolve` on the x position of the ground-hit event.
4. Time to the opponent: solve x(t) = z0 for t. The output metric is D_w = t_w − t_{−w}, the extra time a with-wind drive takes to reach the opponent compared with an into-wind drive.
5. Inputs: x0 ∈ (0, 15) ft, y0 ∈ (1, 3) ft, θ ∈ (10°, 30°), z0 ∈ (29, 44) ft, |w| ∈ (10, 20) mph. Only drive shots are covered. Lobs and drop shots are excluded.

## Equations (as intended; printed typos noted)

Symbols: m is ball mass (kg). ρ is air density (kg/m³). A = πR² is the cross-sectional area (m²). C_d is the drag coefficient (–). **v** = (ẋ, ẏ) is the ball velocity (m/s). w is the horizontal wind velocity (m/s; positive means a tailwind for the hitter). g is gravitational acceleration (m/s²). U is the airspeed (m/s). D is the ball diameter (m). μ is the dynamic viscosity of air (Pa·s). θ is the launch angle (rad). v0 is the launch speed (m/s). (x0, y0) is the launch point (m).

- Eq. (5), drag: **F**_d = −½ ρ C_d A (**v** − (w,0)) |**v** − (w,0)|  [N]
- Eq. (6), Reynolds number: Re = ρ U D / μ  [–]
- Eq. (7), equations of motion:
  - m ẍ = −½ ρ C_d A (ẋ − w) √((ẋ − w)² + ẏ²)
  - m ÿ = −m g − ½ ρ C_d A ẏ √((ẋ − w)² + ẏ²)
  - (x, y)(0) = (x0, y0), (ẋ, ẏ)(0) = (v0 cos θ, v0 sin θ)
- The code works with the per-unit-mass constant k = ρ C_d A / (2m)  [1/m], so that ẍ = −k (ẋ−w)|**v**_rel| and ÿ = −g − k ẏ |**v**_rel|.
- Eq. (3), optimal drive: y(t_b) = 0 and x(t_b) = 44 ft, solved for (t_b, v0).
- Eq. (4), arrival time: x(t) = z0, solved for t.
- Speed: v = √(ẋ² + ẏ²).

**Typos in the printed arXiv eq. (7), corrected by the code (`derivatives()` in `pickleball_solving.py`):**
1. The ÿ equation is printed as "m ÿ = −g − …". The code uses ÿ = −g − k ẏ|**v**_rel|, so the gravity term is m g.
2. The ÿ equation's drag term is printed with (ẏ − w). The code uses ẏ. Wind is horizontal only.
3. The text gives "g … 9.18 m/s²". The code uses `GRAVITY = 9.81`, and my reproduction with 9.81 matches the published Table 1.

There are no lift, spin-decay or contact equations in the source.

## Numeric data points

Each point is marked as one of: **Assumed** (an input the authors chose), **Model output** (simulation), **Digitized** (read by eye from a figure, about ±0.5 mph or ±0.3 ft), **Repo** (GitHub only, not in the paper) or **My calc** (my own calculation from their model, not in the source).

| # | Quantity | Value | Conditions | Where | Type |
|---|---|---|---|---|---|
| 1 | Drag coefficient C_d | 0.6 (constant) | All Re. Taken from wiffle-ball data (Rossmann & Rau 2007) "treating the pickleball as a forward-facing wiffleball" | arXiv p.14, Appendix | Assumed (borrowed) |
| 2 | Possible C_d range | "could in principle vary by roughly ±0.5" | Authors' statement. Only the sign of D_w was checked; no values were tabulated | arXiv p.15 | Assumed |
| 3 | Reynolds number of the problem | Re ≈ 2.5×10⁴ | Not stated which speed. With D = 0.074 m and ρ = 1.2 this is v ≈ 5 m/s. For the drives actually simulated (11–19 m/s) Re ≈ 5.6×10⁴ to 9.3×10⁴ (my calc) | arXiv p.14 | Stated |
| 4 | C_d is roughly constant above | Re ≳ 10³ (holes "expected" to lower this threshold) | Argued from the smooth-sphere curve in Munson et al.; not measured | arXiv p.13–14 | Assumed |
| 5 | Gravity g | 9.81 m/s² (printed as 9.18, a typo) | — | arXiv p.15; code | Assumed |
| 6 | Air density ρ | 1.2 kg/m³ | — | arXiv p.15 | Assumed |
| 7 | Area A | π(37 mm)² = 4.30×10⁻³ m² (radius 37 mm, diameter 74 mm) | — | arXiv p.15; code | Assumed |
| 8 | Mass m | 24 g | — | arXiv p.15 | Assumed |
| 9 | Drag constant k = ρC_dA/(2m) | 0.0645 1/m. Terminal speed √(g/k) = 12.3 m/s | Derived from 1, 5–8 | Code prints it; value is my calc | My calc |
| 10 | Fastest pickleball shots | "roughly 60 mph" (26.8 m/s) | No source cited | arXiv p.4 | Assumed |
| 11 | Launch speed v0, w = 0 | ≈31.7 mph (14.2 m/s); I reproduce 31.8 mph | x0 = 11 ft, y0 = 3 ft, θ = 20°, lands at 44 ft | Fig. 3 (p.9) | Digitized / model output |
| 12 | v0, w = −10 mph (headwind) | ≈42 mph (18.8 m/s); I reproduce 42.0 | same | Fig. 3 | Digitized / model output |
| 13 | v0, w = +10 mph | ≈27 mph (12.1 m/s); I reproduce 27.0 | same | Fig. 3 | Digitized / model output |
| 14 | v0, w = +15 mph | ≈25.7 mph (11.5 m/s); I reproduce 25.8 | same | Fig. 3 | Digitized / model output |
| 15 | Common speed at x = 27 ft | ≈24 mph for all four winds | same | arXiv p.8 text; Fig. 3 | Model output |
| 16 | Minimum speed, w = 0 | ≈19 mph near x ≈ 40 ft | same | Fig. 3 | Digitized |
| 17 | Minimum speed, w = −10 mph | ≈13.8 mph near x ≈ 40 ft | same | Fig. 3 | Digitized |
| 18 | Apex, w = −10 / 0 / +10 / +15 mph | ≈7.3 / 6.0 / 5.3 / 5.3 ft (my reproduction: 7.52 / 6.12 / 5.53 / 5.40 ft at x = 30.4 / 26.5 / 24.6 / 24.2 ft) | same | Fig. 2 (p.8) | Digitized / my calc |
| 19 | D10, D15, D20 (s), x0 = 0, z0 = 29 ft | 0.097, 0.200, 0.346 | θ = 20°, y0 = 3 ft | Table 1 (p.10) | Model output |
| 20 | D10, D15, D20 (s), x0 = 0, z0 = 33 | 0.056, 0.166, 0.348 | same | Table 1 | Model output |
| 21 | D10, D15, D20 (s), x0 = 0, z0 = 44 | −0.302, −0.490, 0.089 | same (the sign flip at D20 is not discussed) | Table 1 | Model output |
| 22 | D10, D15, D20 (s), x0 = 11, z0 = 29 | 0.082, 0.150, 0.242 (my reproduction: 0.082, 0.151, 0.243) | same | Table 1 | Model output |
| 23 | D10, D15, D20 (s), x0 = 11, z0 = 33 | 0.058, 0.133, 0.255 | same | Table 1 | Model output |
| 24 | D10, D15, D20 (s), x0 = 11, z0 = 44 | −0.230, −0.375, −0.568 | same | Table 1 | Model output |
| 25 | D10, D15, D20 (s), x0 = 15, z0 = 29 | 0.075, 0.131, 0.203 | same | Table 1 | Model output |
| 26 | D10, D15, D20 (s), x0 = 15, z0 = 33 | 0.059, 0.124, 0.223 | same | Table 1 | Model output |
| 27 | D10, D15, D20 (s), x0 = 15, z0 = 44 | −0.203, −0.332, −0.505 | same | Table 1 | Model output |
| 28 | Sensitivity of D_w to θ and y0 | "not greatly sensitive to minor modifications" (no numbers). The SFU draft has an author note: "We need to verify the sensitivity comment" | — | arXiv p.10; SFU draft p.11 | Claim only |
| 29 | Sensitivity of D_w to C_d | Magnitudes "could be significantly different". All signs were preserved | C_d varied over an unstated set | arXiv p.15 | Claim only |
| 30 | Drop test: 21 heights × 3 trials (63 points), h = 0.178 to 4.272 m, t = 0.15 to 1.28 s | Least-squares quadratic-drag fit (my calc): k = 0.20 1/m (implied C_d ≈ 1.9), RMS residual 0.070 s, against 0.102 s for vacuum fall. The trial scatter is ±0.1 s, which looks like hand timing. **Physically implausible and not used in the paper.** | Unknown ball, release method and timing method | GitHub `paper-plots/ball.csv` and `pickleball_fiiting.py` | Repo (unpublished) |

### Independent reproduction (my calc)

I re-implemented eq. (7) with the stated constants and g = 9.81, using RK4 with dt = 2×10⁻⁴ s and bisection on v0. It reproduces Table 1 row (x0 = 11, z0 = 29) to within 0.001 s and the Fig. 3 launch speeds to within 0.1 mph. This confirms the model as written in the code is the model the paper used. The scripts are in my session scratchpad, not in the repo: `emond_repro.py`, `emond_calc.py` and `emond_sens.py`.

## Applicability to POLLEN

**What transfers:**
- The **drag-only ODE structure** with wind as a relative velocity is the drag-plus-gravity baseline in HANDOFF §4A. It is a standard form that is correct for a constant C_d.
- The **workflow** transfers. Pose the shot as a two-point boundary value problem: given the launch point and angle, solve for v0 to hit a target point, then evaluate a downstream metric. PM-001 needs the same inverse solve, with targets at the CELL mouth corridor instead of an endline.
- The ball class is close. A pickleball is 74 mm and 24 g; POLLEN is 71 mm and about 25 g. Both are hollow, perforated polyethylene balls. Mass per area is similar, so the drag constants are similar. My calc: POLLEN with C_d = 0.6 gives k = 0.058 1/m and a terminal speed of 13.0 m/s, against 0.0645 1/m and 12.3 m/s here.

**What does not transfer:**
- **There is no spin, lift or Magnus force,** which is the core of PM-001. This paper gives no C_l(S), no spin decay and nothing about the backspin hypothesis.
- **C_d = 0.6 is not a pickleball measurement, let alone a POLLEN measurement.** It is borrowed from a wiffle ball, which has 8 elongated slots on one hemisphere in a "forward-facing" orientation. POLLEN has a different hole pattern and size and a non-spherical shape. HANDOFF §5 forbids treating pickleball coefficients as POLLEN measurements; this value is one step further removed, a wiffle-ball coefficient treated as a pickleball one. Later free-flight work cited in the literature (Lindsey 2025) reportedly finds lower pickleball C_d values. This note does not verify that; see the Lindsey note.
- The **Reynolds number claim** (Re ≈ 2.5×10⁴) does not match the drives they simulated (Re ≈ 6–9×10⁴). It does fall inside the PM-001 range of 1×10⁴ to 5×10⁴, but no data backs the constant-C_d assumption there.
- The **±0.5 C_d uncertainty** is a statement, not a measured bound.
- The flight regime differs. They model shallow (20°), fast (11–19 m/s) drives over 10 m. PM-001 shots are high-arc, 2–10 m/s, with the apex inside a few metres. Drag shapes the descent geometry more in a lob, relatively speaking.
- The drop-test data in the repository is not usable for POLLEN or pickleball calibration (implied C_d ≈ 1.9, timing noise of about ±0.1 s).

## Implications for the PM-001 models

1. **Use eq. (7) only as the "gravity + drag" baseline** (HANDOFF §4A, baseline 2), with C_d as an uncertain parameter, not a fixed 0.6. Write the drag constant as k = ρC_dA/(2m) and carry wind as **v**_rel. Adding Magnus: append +k_L |**v**_rel|² **n**_M with k_L = ρC_lA/(2m). This source gives nothing for C_l.
2. **C_d prior for POLLEN:** sweep about 0.3 to 0.7, with 0.45 to 0.6 as the central band, until POLLEN is measured. Do not cite this paper as evidence for 0.6. Cite it only as "a model assumption borrowed from wiffle-ball data". Rossmann & Rau 2007 is the primary data source to check.
3. **C_d uncertainty is the same order of magnitude as the Magnus effect.** My calc, using the corrected eq. (7) and POLLEN constants (m = 0.025 kg, R = 0.0355 m, ρ = 1.225), launched from z = 0.4 m, with the crossing on descent of z = 1.12 m (an illustrative height only):

   | v0, θ | C_d = 0 | 0.3 | 0.45 | 0.6 | 1.1 |
   |---|---|---|---|---|---|
   | 7 m/s, 60°: x at crossing (m) / descent angle | 3.86 / 53.7° | 3.44 / 55.3° | 3.26 / 55.9° | 3.10 / 56.4° | 2.68 / 57.8° |
   | 8 m/s, 55° | 5.58 / 49.5° | 4.82 / 51.9° | 4.52 / 52.9° | 4.26 / 53.7° | 3.59 / 55.6° |
   | 6 m/s, 70° | 2.06 / 64.0° | 1.89 / 64.7° | 1.81 / 65.0° | 1.74 / 65.2° | 1.55 / 65.8° |

   Over C_d = 0.3 to 0.6 the crossing point moves 0.15 to 0.56 m and the descent angle moves about 0.5° to 2°. A lift of C_l ≈ 0.2 gives only about 5% g at 5 m/s (HANDOFF §4A), so **a Magnus-assisted entry cannot be claimed before C_d is measured.** The trajectory shift from spin must be compared with the C_d band, and with the spread across ball-to-ball variation. These launch states are illustrative only, not proposed shots.
4. **Measure C_d for POLLEN directly.** The repository drop data shows the pitfalls. Hand-timed drops under 4.3 m cannot resolve C_d: the drag effect on fall time at 4.3 m is about 0.04 s, against ±0.1 s timing noise. Use high-speed video of a horizontal or lofted no-spin launch, at least 240 fps, over at least 2 m of flight, and fit k as in eq. (7). Separately, fit C_l from backspin launches, keeping the same C_d fit.
5. **Wind:** FTC play is indoors, so wind is about 0, apart from HVAC. Keep w in the model only for the robustness study (HANDOFF §3 q6, ±0.5 to 1 m/s drafts). This paper's headwind-versus-tailwind result does not otherwise matter to PM-001.
6. **Solver pattern to reuse:** an event-terminated integration (a ground or target-plane crossing), plus a root-find on launch speed. Inverse targeting for the CELL corridor should follow this pattern, but find roots on (v0, θ, ω) with the collision geometry, not just on the endline.

## Caveats

- I did not read the journal version of record (blocked by a bot check). The numbers come from arXiv v1 and the code. My exact reproduction of Table 1 and Fig. 3 supports the claim that they match the paper. Any later typo fixes in the journal version (for example g = 9.18) are unverified.
- The figure values marked "Digitized" were read by eye and are cross-checked by my reproduction.
- The repository data (`ball.csv`) has unknown provenance and was never peer-reviewed or published.
