# Sakai et al. (2016): Aerodynamics of a Spinning Table Tennis Ball ~Lift Crisis~

source_id: `sakai2016` | task PM-001 | read 2026-10-30

## Citation
Sakai, W. (酒井 道), Miyazaki, T. (宮嵜 武), Komatsu, T. (小松 竜郎), Takahashi, N. (高橋 直也), Himeno, R. (姫野 龍太郎).
"卓球ボールの空力特性 ～リフトクライシス～ / Aerodynamics of a Spinning Table Tennis Ball ~Lift Crisis~".
*Proceedings of the JSME Annual Meeting 2016* (日本機械学会 2016年度年次大会講演論文集, No.16-1), Fukuoka, 11–14 Sep 2016, paper J2340102, 5 pp.
DOI: https://doi.org/10.1299/jsmemecj.2016.J2340102 (J-STAGE, released 2017-06-19, ISSN 2424-2667).
Affiliations: Univ. of Electro-Communications (Sakai, Miyazaki, Komatsu); Tokyo Denki Univ. (Takahashi); RIKEN (Himeno).
Note: the PDF romanises the first author as **Wataru** SAKAI. The J-STAGE metadata, as summarised by the fetch tool, showed a different romanisation. Use the PDF.

## Access
**Full text.** The free PDF was downloaded from J-STAGE (https://www.jstage.jst.go.jp/article/jsmemecj/2016/0/2016_J2340102/_pdf/-char/ja) and all 5 pages were read. The body is in Japanese and the abstract and figure/table captions are in English. Figures 7 and 8 were rendered at 300 dpi and read by eye. No digitising software was used.

## Review status
**Conference proceedings (JSME Annual Meeting lecture paper).** This is a short extended-abstract format. It is not a peer-reviewed journal article and was presumably not refereed in full. The data are original experimental measurements. The physical interpretation (boundary-layer transition) is stated as a hypothesis ("考えられる" = "it is thought that"). It is not demonstrated with flow visualisation.

## Ball and method
- **Ball:** Nittaku Premium 3-Star (ITTF official, smooth celluloid-type plastic, unperforated). Diameter 39.8 mm. The paper prints "3.98×10⁻⁵ m", an obvious typo for 3.98×10⁻² m. Mass 2.74 g, and "standard deviation 0.20×10⁻⁶ m" (sphericity/diameter, highly spherical). The introduction uses the rounded values r = 2 cm, m = 2.7 g. A black cross was painted on the ball to read the spin from video (Fig. 1).
- **Spin type:** **backspin only** for all lift data.
- **Launcher:** "Chiquita", a 3-rotor machine built with JISS and Sunaga Kaihatsu. Each rotor reaches about 80 rps (≈4800 rpm) and can be reversed, which gives independent speed and spin. Rotor diameter and contact geometry are not given.
- **Method A, front view (CD and CLZ):** 4 light sheets (L1–L4) and a polycarbonate impact board were spaced 0.685 m apart along a table-tennis table. A high-speed camera (Phantom) filmed the ball crossing each sheet and its board impact. The ball-centre coordinates were read from the video. **CD and CLZ were found by fitting a numerically integrated theoretical trajectory to the measured points** (details in Tanaka et al. 2014, *Nagare* 33(2):37-45, in Japanese).
  - Improvements over Tanaka et al.:
    - laser line generators (Muratec KDS Super-Ray ATL) for L2–L4, which cut the sheet width from about 1 cm to 2 mm;
    - a new Phantom Miro LC310 camera: 3000 fps for Re = 3–6×10⁴ and 4500 fps for Re = 7–9×10⁴ (previously 1901 fps);
    - an ITTF-certified flat table (Nittaku NT-3200);
    - more digitised points per shot: 30 → 50 for Re = 3–5×10⁴ and 20 → 40 for Re > 5×10⁴.
- **Method B, side view (CD only):** 3 Phantom cameras. Camera 1 sat 0.1 m from the launcher and camera 2 sat 0.1 m before the acrylic board, and each was calibrated in length at its own station. CD came from the speed decay between cameras 1 and 2. Camera 3 measured the miss distance. This method assumes zero lift, so it was applied only to non-spinning balls and to the Re = 9×10⁴, SP = 0.48 case where CLZ ≈ 0 (method in Miyazaki et al. 2013, *Sports Eng.* 16:43-54).
- **Range covered:** 3.0×10⁴ < Re < 9.0×10⁴ and 0 < SP < 1.0. Fig. 8 has a few points up to SP ≈ 1.14. The data are grouped in 7 Re bins: 3, 4, 5, 6, 7, 8 and 9 ×10⁴.
- **Not reported:**
  - air temperature, density or viscosity;
  - spin decay;
  - the trajectory-fit equations (deferred to Tanaka 2014);
  - lateral or side-force coefficient;
  - any surface-roughness data.

## Equations
**The paper writes no equations.** The symbols Re, SP, CD and CLZ are used without being defined. Below are the standard definitions consistent with the paper's usage and with its trajectory-fit method. They are **inferred, not quoted.**

| # | Equation | Symbols (SI) | Status |
|---|---|---|---|
| E1 | Re = U d / ν | U ball airspeed [m/s]; d diameter [m]; ν kinematic viscosity of air [m²/s] | standard; implied |
| E2 | SP = ω r / U | ω spin rate [rad/s]; r = d/2 radius [m] | standard; implied (the paper calls SP the "dimensionless rotation rate", 無次元回転数) |
| E3 | F_D = ½ ρ U² A C_D, opposite to the velocity | ρ air density [kg/m³]; A = π r² [m²]; F_D drag [N] | standard form; implied by the trajectory fit |
| E4 | F_LZ = ½ ρ U² A C_LZ, vertical (z) component of the lift/Magnus force, upward positive for backspin | C_LZ vertical lift coefficient [–] | implied; the subscript Z indicates the vertical component only |
| E5 | m dU/dt = m g + F_D + F_L (2D, constant C_D and C_LZ per shot), integrated numerically and least-squares fitted to the video positions | m ball mass [kg]; g gravity [m/s²] | the method is described in words; the equation form is inferred |
| E6 | Side-view drag (no lift): m dU/dt = −½ ρ A C_D U², so C_D = (2m / (ρ A Δs)) · ln(U₁/U₂) over a path length Δs | U₁, U₂ speeds at cameras 1 and 2 [m/s]; Δs distance [m] | **my reconstruction** of the speed-decay method; the paper only says "from the difference between cameras 1 and 2". Gravity's along-path component is neglected in this form. |
| E7 | Lift-crisis zone ≡ SP_max(Re) < SP < SP_min(Re) | SP_max is where C_LZ peaks; SP_min is where C_LZ has its local minimum | defined in words in §4 |

Derived scaling, **not in the source** (added for the PM-001 comparison):
- Aerodynamic acceleration per unit coefficient: a = ½ ρ U² (A/m) C.
- A/m is 0.459 m²/kg for the TT ball (A = 1.257×10⁻³ m², m = 2.74 g) and 0.158 m²/kg for POLLEN (A = 3.959×10⁻³ m², m ≈ 25 g). The ratio is **0.345**.
- At the same U and C, POLLEN gets about 1/3 of the TT ball's Magnus acceleration.

## Numeric data points
Abbreviations: T = table value, exactly as printed. F = read by eye from the 300-dpi figure (uncertainty about ±0.01–0.02 in coefficient and ±0.03 in SP). S = stated in the text. "Tanaka" = Tanaka et al. 2014, reproduced in this paper for comparison.

### Primary measurements (this study)
| Quantity | Value | Conditions | Where | Type |
|---|---|---|---|---|
| C_D | 0.419 (S.D. 0.009) | Re 4.0×10⁴, SP 1.0, n = 24, front view | Table 1 | T |
| C_LZ | 0.322 (S.D. 0.010) | Re 4.0×10⁴, SP 1.0, n = 24, front view | Table 1 | T |
| C_D | 0.324 (S.D. 0.012) | Re 9.0×10⁴, SP 0.5, n = 31, front view | Table 1 | T |
| C_LZ | −0.005 (S.D. 0.018) | Re 9.0×10⁴, SP 0.5, n = 31; the authors say the negative value is within error | Table 1, §3.2.2 | T |
| C_D | 0.421 (S.D. 0.008), n = 33 | Re 4.0×10⁴, SP 0.0, front view | Table 2 | T |
| C_D | 0.421 (S.D. 0.018), n = 30 | Re 4.0×10⁴, SP 0.0, side view | Table 2 | T |
| C_D | 0.354 (S.D. 0.017), n = 29 | Re 9.0×10⁴, SP 0.48, front view | Table 2 | T |
| C_D | 0.358 (S.D. 0.016), n = 50 | Re 9.0×10⁴, SP 0.48, side view | Table 2 | T |
| Lift almost vanishes | C_LZ ≈ 0 | Re 9.0×10⁴, SP 0.5 | Abstract, §3.1.1 | S |
| Negative Magnus | **not observed** in the range measured | 3×10⁴ < Re < 9×10⁴, 0 < SP < 1.0, backspin | §3.2.2, §5 | S |
| Rotor max speed | ≈80 rps per rotor | launcher | §2.1.2 | S |
| Gate spacing | 0.685 m | front-view rig | §2.1.3 | S |
| Frame rate | 3000 fps (Re 3–6×10⁴); 4500 fps (Re 7–9×10⁴) | camera | §2.2.2 | S |
| Ball | d 39.8 mm, m 2.74 g | Nittaku Premium 3-Star | §2.1.1 | S |

### Comparison values (Tanaka et al. 2014, reprinted)
| Quantity | Value | Conditions | Where |
|---|---|---|---|
| C_D / C_LZ | 0.480 (0.008) / 0.306 (0.014) | Re 4×10⁴, SP 1.0, n = 28 | Table 1 |
| C_D / C_LZ | 0.398 (0.011) / 0.028 (0.032) | Re 9×10⁴, SP 0.5, n = 30 | Table 1 |
| C_D front / side | 0.456 (0.008, n = 28) / 0.444 (0.021, n = 25) | Re 4×10⁴, SP 0 | Table 2 |

The earlier C_D values were 6–23 % higher than this study's. The authors attribute this to measurement error that the new rig removed. C_LZ agreed between the two studies.

### Qualitative laws (§3.2, stated for both C_D and C_LZ)
1. At low SP, the coefficient rises roughly linearly with SP and **does not depend on Re**.
2. At SP_max it peaks, then falls sharply to a local minimum at SP_min.
3. Above SP_min it rises again, again roughly linearly and independent of Re.
4. As Re increases, the peak value, the minimum value, SP_max and SP_min all **decrease**.
5. The scatter (S.D. of C_LZ) "increases drastically" inside the valley. The authors read this as a "lift crisis", attributed to turbulent transition of the boundary layer.

### C_LZ envelope per Re bin, read from Fig. 8 (type F, backspin)
| Re (×10⁴) | U for TT ball, m/s* | Low-SP slope dC_LZ/dSP | C_LZ peak (at SP) | C_LZ valley min (at SP) | C_LZ at SP ≈ 0.85–1.0 |
|---|---|---|---|---|---|
| 3 | 11.3 | ≈0.8–0.9 for SP < 0.2 (common to all Re) | ≈0.29 (0.55) | ≈0.20–0.22 (0.80–0.85), shallow | ≈0.25 (0.88) → 0.30 (1.02) |
| 4 | 15.1 | as above | ≈0.27 (0.45–0.50) | ≈0.13–0.17 (0.60–0.70) | ≈0.32 (1.0) (Table 1: 0.322) |
| 5 | 18.9 | as above | ≈0.25 (0.45) | ≈0.10–0.12 (0.60–0.65) | ≈0.25 (0.87), 0.32 (0.95) |
| 6 | 22.6 | as above | ≈0.22 (0.38–0.40) | ≈0.08 (0.60) | ≈0.30 (0.88) |
| 7 | 26.4 | as above | ≈0.21 (0.35–0.45) | ≈0.06–0.07 (0.55) | ≈0.30 (0.87), 0.36 (1.06–1.14) |
| 8 | 30.2 | as above | ≈0.20 (0.30–0.37) | ≈0.01–0.03 (0.55) | ≈0.32 (0.80), 0.345 (0.89) |
| 9 | 34.0 | as above | ≈0.17 (0.30–0.35) | ≈0.00 (0.50) (Table 1: −0.005) | ≈0.28 (0.77), 0.32 (0.95) |

At SP ≈ 0–0.05, all bins scatter between C_LZ ≈ −0.04 and +0.04. At SP ≈ 0.1, C_LZ ≈ 0.05–0.12. At SP ≈ 0.2, C_LZ ≈ 0.14–0.18. Above about SP 0.85, all Re bins collapse onto one rising branch, C_LZ ≈ 0.25–0.36.
*U = Re·ν/d with ν = 1.51×10⁻⁵ m²/s (assumed 20 °C; the paper gives no air properties) and d = 0.0398 m.

### C_D envelope per Re bin, read from Fig. 7 (type F)
| Re (×10⁴) | C_D at SP ≈ 0–0.3 | C_D peak (at SP) | C_D valley min (at SP) | C_D at SP ≈ 1.0 |
|---|---|---|---|---|
| 3 | 0.39–0.43 | ≈0.49 (0.50–0.55) | ≈0.40 (0.85–0.90), shallow | ≈0.41–0.42 |
| 4 | 0.41–0.44 (0.421 at SP 0, T) | ≈0.51 (0.48–0.55) | ≈0.35 (0.78–0.80) | ≈0.42 (0.419 at SP 1.0, T) |
| 5 | 0.40–0.44 | ≈0.49 (0.47) | ≈0.35 (0.80) | ≈0.40 (0.95) |
| 6 | 0.42–0.45 | ≈0.51 (0.45) | ≈0.33–0.35 (0.70–0.80) | ≈0.43 (1.06) |
| 7 | 0.40–0.44 | ≈0.46 (0.45) | ≈0.27 (0.70) | ≈0.41–0.46 (1.04–1.14) |
| 8 | 0.41–0.44 | ≈0.46 (0.38) | ≈0.27 (0.65) | ≈0.37 (0.90) |
| 9 | 0.41–0.43 | ≈0.43 (0.35) | ≈0.26 (0.59) (0.324 at SP 0.5, T) | ≈0.38 (1.04) |

The drag valley sits at a slightly higher SP than the lift valley at the same Re, and it is deeper at high Re. Drag reduction and lift reduction appear together, the classic signature of a drag crisis.

### Prior literature quoted in the introduction (secondary; not verified here)
| Claim | Value | Source cited |
|---|---|---|
| Negative-Magnus region, water tank | 6×10⁴ < Re < 5.0×10⁵, 0 < SP < 0.6 | Taneda 1957 |
| Negative Magnus confirmed | spinning ball dropped in a wind tunnel | Briggs 1959 |
| LES negative lift | Re 2.0×10⁵, SP 0.2, C_L = −0.25 | Muto et al. 2012, *Phys. Fluids* 24:014102 |
| Wind tunnel, narrower negative region than Taneda | 6×10⁴ < Re < 1.8×10⁵, 0 < SP < 1.8 | Kim et al. 2014, *JFM* 754:R2 |
| 44 mm "large ball" wind tunnel reproduces Taneda's region | — | Konishi et al. 2013 |
| Flight test: no negative Magnus | 2.0×10⁴ < Re < 9.0×10⁴, 0 < SP < 1.0 | Tanaka et al. 2014 |
| Table tennis play range | Re ≤ 1.0×10⁵, SP ≤ 2 | intro |

## Applicability to POLLEN
**POLLEN regime (derived):**
- d = 0.071 m and ν = 1.51×10⁻⁵ m²/s give Re ≈ 4.7×10³ per m/s. So v = 2–10 m/s maps to **Re ≈ 0.94–4.7×10⁴**.
- Sakai's measured range (Re ≥ 3×10⁴) overlaps POLLEN only for **v ≳ 6.4 m/s**, i.e. near launch and on the fast part of the descent.
- **The apex region (v ≈ 2–5 m/s, Re ≈ 1–2.4×10⁴) is outside the measured range.** Any C_L there must be extrapolated or measured.
- Ideal hood kinematics (HANDOFF §4C) give S_exit ≈ 1. As v drops toward the apex, S = ωR/v rises above 1, which is beyond the measured SP range (≤ 1.14).

**What transfers (as physics, not as numbers):**
1. **C_L(S) can be strongly non-monotonic** at Re 4–9×10⁴ for a light hollow sphere. Peak, valley and recovery all shift with Re. This is direct experimental evidence against a monotonic saturating C_L(S) as the only model form, and against "more spin = more lift" (HANDOFF §5).
2. In the POLLEN-overlap bins (Re 3–5×10⁴), the smooth-ball valley is **shallow at 3×10⁴** and moderate at 4–5×10⁴:
   - Re 4×10⁴: C_L falls from ≈0.27 to ≈0.15.
   - Re 5×10⁴: C_L falls from ≈0.25 to ≈0.11.
   - The valley lies at SP ≈ 0.6–0.85.
   - **At SP ≈ 1 every Re bin is back on the upper branch, C_L ≈ 0.30–0.33.** A POLLEN shot near S ≈ 1 would sit past the valley *if* smooth-ball behaviour applied.
3. Drag depends on spin. C_D runs from ≈0.42 at SP 0 to ≈0.49–0.51 at the pre-crisis peak and back to ≈0.42 at SP 1 (Re 3–4×10⁴). A constant-C_D model is defensible only near SP ≈ 0 or ≈ 1 at low Re.
4. Shot-to-shot C_L scatter grows inside a crisis zone. Repeatability, which matters most for the PM-001 success metric, could be worst at intermediate spin.
5. The **method** transfers directly: video trajectory fitting with constant per-shot C_D and C_L, a non-spinning side-view drag cross-check, about 25–50 shots per condition, and 3000+ fps. It gave S.D. ≈ 0.01 on C_D and C_L for a ball 9× lighter than POLLEN.

**What does not transfer:**
- **Surface:** the TT ball is smooth and unperforated. POLLEN is perforated (holes allow through-flow, base bleed and pressure leakage) and slightly non-spherical. The lift crisis is attributed to boundary-layer transition, and transition is exactly what holes and roughness change. Perforations could:
  - (a) trip transition earlier, moving a crisis down into the POLLEN Re range;
  - (b) suppress the crisis altogether;
  - (c) add asymmetric jet effects, as seen with wiffle balls.
  This paper cannot tell which. **No Sakai coefficient may be used as a POLLEN measurement.**
- **Mass loading:** POLLEN's A/m is 0.345× the TT ball's. With the same C_L and v, POLLEN's Magnus acceleration is about 1/3 as large. Examples, with ρ = 1.225:
  - v = 8 m/s, C_L = 0.32: a_M ≈ **2.0 m/s² (0.20 g)**.
  - v = 3 m/s near the apex, with C_L assumed 0.35: a_M ≈ **0.31 m/s² (0.03 g)**.
  - Drag at v = 8 m/s, C_D 0.42: ≈ 2.6 m/s².
  The table-tennis intuition that aerodynamics "overcomes gravity" (§1 of the paper) **does not carry over** to POLLEN.
- **Range gaps:** there is no data for S > 1.14, for Re < 3×10⁴, on spin decay, or on any side force.
- **Peer-review status:** these are conference proceedings, not a refereed journal paper.

## Implications for the PM-001 models
1. **Aero model form (4A).**
   - Implement C_L(Re, S) as a pluggable lookup, not only a monotonic saturating curve.
   - Include a "smooth-sphere crisis" scenario built from the Fig. 8 envelope:
     - linear slope ≈0.85 up to the peak;
     - peak and valley SP values shifting down with Re;
     - the upper branch ≈ 0.30–0.35 at S ≈ 1.
   - Run it as one bound of the uncertainty band, labelled "smooth TT ball, Sakai 2016, not POLLEN".
   - Run a monotonic curve as the other bound.
2. **Make C_D a function of S** in the sensitivity runs. Use a band of 0.40–0.51 for S ≤ 1 at Re 3–5×10⁴ from this source. Do not fix C_D at the S = 0 value for spinning shots.
3. **Apex extrapolation flag.** Re < 3×10⁴ and S > 1.1 are out of range for this source. The simulator should record when a trajectory leaves the calibrated (Re, S) envelope, and report the fraction of flight time and the apex state outside it.
4. **Avoid the valley in the design.** If POLLEN shows any crisis, choose launch states that keep S above S_min along the whole flight. With a near-S ≈ 1 hood launch, S rises toward the apex, which is favourable. Shots with weaker spin are most at risk, for example a slipping passive roller giving S ≈ 0.4–0.8, because they may cross the valley with large scatter.
5. **Sign test.** Negative Magnus was not seen for Re ≤ 9×10⁴ (smooth ball). Literature negative-lift regions start at Re ≳ 6×10⁴, above POLLEN's range. Keep a C_L < 0 check only as a robustness case, because perforations could shift the transition.
6. **Calibration plan for the prototype.** Copy the method:
   - film ≥ 240 fps, preferably ≥ 1000 fps, in two orthogonal views;
   - paint a cross on the POLLEN ball to read spin;
   - fit constant C_D and C_L per shot by integrating the PM-001 ODE;
   - run a zero-spin side-view drag check;
   - take about 25–30 shots per (v, ω) cell;
   - include cells at S ≈ 0.3, 0.5, 0.7, 1.0 and 1.5 at v ≈ 4, 6 and 8 m/s, to search for a POLLEN-specific crisis inside its own Re range.
7. **Scale expectation.** Even at the source's best C_L (≈0.33), POLLEN's Magnus acceleration is ≲ 0.2 g at launch speeds and ≲ 0.05 g near the apex. Spin-induced path changes will come mainly from the high-speed part of the flight, not from an apex "hook".

## Caveats
- The figure values are eyeballed from a scanned scatter plot: about ±0.01–0.02 in coefficient and ±0.03 in SP. Only the Table 1–2 values are exact.
- Re, SP and C_LZ are not defined explicitly in the paper. The standard definitions are assumed, and SP is assumed to equal ωr/U.
- Air properties are unreported, so converting Re to speed uses an assumed ν.
- C_LZ is the vertical component only. It equals the full lift only if the spin axis is horizontal and perpendicular to the flight, which the backspin set-up approximates.
- The ball diameter is printed as 3.98×10⁻⁵ m in §2.1.1, an obvious typo for 3.98×10⁻² m.
- The boundary-layer-transition explanation is an untested hypothesis in the source.
- The source is a 5-page conference paper, and the trajectory-fit equations are in a Japanese-language companion paper (Tanaka 2014) that was not read here.
