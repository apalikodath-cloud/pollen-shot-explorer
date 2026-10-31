# PM-001 literature synthesis: backspin on POLLEN

Written 2026-10-30 by the PM-001 synthesis agent. It draws on the fact-check reports in `research/checks/`. It compares them with the values the model uses now:
- `data/aero_params.json`
- `data/launch_envelope.json`
- `src/flight.py`, `src/launcher.py` and `src/contact.py`
- `docs/02_aero.md` and `docs/04_launcher.md`
- `crosscheck/empirical/EVIDENCE.md`

The machine-readable ranges are in `research/params_lit.json`. `src/flight.load_params(path=...)` loads that file directly; this was checked for low, nominal, high and floor.

**Bottom line**
- No published measurement of POLLEN aerodynamics, spin decay, COR, friction or stiffness exists. Every coefficient below is a proxy or a bound.
- The largest unknown is the backspin lift of a ball with 26 holes at S ≈ 1–1.7 and Re 1e4–5e4. The evidence allows anything from about 0.02·S (essentially no Magnus lift) to 0.30–0.40 (the smooth-sphere value).
- The drag coefficient Cd is also uncertain, from 0.33 to 0.90. That changes the entry angle by about as much as the lift range does.

---

## 1. Grades

| Grade | Meaning |
|---|---|
| **A** | Peer-reviewed original measurement that transfers to POLLEN (same physics and regime) |
| **B** | Peer-reviewed, but a different ball or regime, or a model or theory only |
| **C** | Preprint, unreviewed web article or technical note, vendor data, or forum data with numbers |
| **D** | Anecdote, observation, or an assumption with no source |

No evidence about POLLEN aerodynamics reaches grade A. Only the Cross bounce papers are grade A, and they measure tennis balls. They are grade A for the *form* of the impact model, not for POLLEN's coefficient values.

## 2. Evidence table

### 2a. POLLEN-specific data (kept separate from proxies)

| What | Value | Source | Grade |
|---|---|---|---|
| Diameter | about 2.8 in (7.1 cm); "not perfectly spherical, may vary" | FIRST manual TU06/TU07 §9.8 | C |
| Mass | 0.055 lb = 24.95 g (spec). Listing weight 27.2 g. CAD shell at PE density 20.5–22 g | AndyMark page, Shopify JSON, STEP | C / D / C |
| Geometry | R 35.5 mm, wall 1.78 mm, 26 holes Ø 0.40–0.44 in, open area 13–16 % | AndyMark STEP and print | C |
| α = I/(mR²) | 0.627–0.638 from CAD; thick-shell formula gives 0.634 | derived from the STEP | C (derived) |
| HIVE CELL | about 20 × 14 in opening, 12 in deep, upward-facing; pivot height 43.95 in | manual §9.6 | C |
| Bounce-outs, fixed solid hood | 19 of 43 (44 %, 95 % CI 30–59 %). Spin was not measured and distance was not stated. The bins sum to 42, not 43 | FTC 14343 Chief Delphi thread | D |
| "Topspin is better" (17134) | The test never reached the HIVE. The same team later calls its backspin shooter promising | forum | D |
| Team settings | 37246: 63° launch, 0.25 in squeeze. 37245: aims for zero spin to limit bounce-outs | forum | D |
| Wheel/hood orientation | The wheel must be below and the hood above to get backspin | forum (Advik123) | D |

**Not found:** any POLLEN Cd, Cl, spin-decay, COR, friction, N(δ) or spin-rate measurement.

### 2b. Aerodynamic proxies

| Source | Ball and regime | Key numbers | Grade | Caveats |
|---|---|---|---|---|
| Lindsey 2025 (TWU) | 26- and 40-hole pickleballs in free flight, 6.0–11.5 m/s, Re 2.95e4–5.67e4, S ≤ 0.37 | **Drag:** indoor 26-hole Cd 0.45 (SD 0.09); outdoor 40-hole Cd 0.33. Hole-modification control ball: Cd 0.59–0.985 (fit 0.65–0.82). Taping the holes cut Cd to about 0.43. **Lift:** backspin \|Cl\| ≈ 0.173 + 0.02 S; topspin 0.24 + 0.44 S | **C** | Unreviewed. Ball mass is not given and no data were released. Both worked examples are topspin. The 0.17 offset may not be Magnus lift, which leaves a Magnus slope of only about 0.02 |
| Steyn et al. 2025 | Outdoor 40-hole ball, 6 shots, Re 4.7–6.1e4, S 0.03–0.3 | Cd 0.30 ± 0.02; Cl = 0.195 S (fit through the origin, large scatter) | **B** | Only the preprint was read, not the version of record. The lift sign in its Eq. 3 is wrong; its Fig. 1 caption disagrees with Eq. 6 |
| Van Wyk, Smith, Lyu 2026 | Pickleball lab tests (method per Lyu et al. 2025, not described in the paper), Re 7.7e4–1.4e5, S 0.30–0.56 | Cl ≈ 0.0124 + 0.466 S; Cd ≈ 0.40 | **B** | Short conference paper, manufacturer-funded. Its Re is above POLLEN's |
| Rossmann & Rau 2007 | Wiffle ball, wind tunnel, not spinning | Cd 0.36–1.05 depending on orientation and Re, rising toward about 1 at low Re. Non-Magnus side Cl from −0.15 to +0.145, changing sign near Re 5.5e4 | **B** | The holes are one-sided slots, which POLLEN does not have. **Full text read**; Cd 0.6 is the β = 90° orientation |
| Emond, Sun, Swartz 2024 | Pickleball simulation | Cd 0.6 borrowed from Rossmann; no lift | B (no new data) | Not evidence for Cd |
| Muto et al. 2012 | Smooth sphere LES; Re 1e4, 2e5, 1.14e6 | At Re 1e4: Cl 0.167 (Γ 0.2) and 0.301 (Γ 1.0); Cd 0.474 and 0.661. Negative lift at Re 2e5, Γ 0.1–0.5 | B | The authors say their subcritical Cd disagrees with experiment, and Γ is defined ambiguously |
| Ito & Kamijima 2025 | Smooth sphere CFD, Re 6.6e3–5.3e4 | Lift-crisis dip (table below). Cd 0.45–0.62. C_M = (3/8) Cl/S | B | Numerical only |
| Sakai 2016 / Miyazaki 2017 | Table-tennis ball, wind tunnel | Re 3e4: peak 0.29 at SP 0.55, valley 0.21 at SP 0.72–0.85. Re 4e4: valley 0.15–0.17. Re 5e4: valley 0.09–0.12. Upper branch 0.30–0.33 at SP 1.0 | **C** | Non-refereed proceedings |
| Conti 2026 | Table-tennis fits from match video (40 mm smooth ball, Re ≈ 5e3–4.6e4) | Equivalent Cl 0.08–0.41 at v ≥ 3.5 m/s (derived: CL = (8/3)·C_M·Sp from the published tables; the 2 m/s row is noisy). Cl rises to 0.24–0.29 at Sp 0.5, then dips at Sp 0.75–1.0, and **the dip deepens with Re**: 0.25 (Re 2.0e4, Sp 1.0), 0.23 (2.8e4, Sp 0.75), 0.20 (3.6e4, Sp 0.75), 0.17 (4.5e4, Sp 0.75); it recovers to 0.35–0.41 at Sp 1.5 (all derived) | C | Preprint. C_M ≥ 0 by construction, so the fit cannot show a sign change. The 3.6e4 and 4.5e4 rows (POLLEN Re at about 7.6–9.5 m/s) are in research/checks/sweep_aero.md, not in the sweep |
| Cross 2012 (AJP) | Polystyrene balls, 7–28 m/s | Cl 0.15 (S 0.37), 0.23–0.24 (0.5), 0.31 (0.8), peak 0.33 (0.95–1.1), 0.30 (1.45). Cd 0.24 at 28 m/s up to 0.40 at 7 m/s. One ball had Cl < 0 at 9–14 m/s. No measurable spin decay | B | Smooth ball, but the closest S range to POLLEN's |
| Cross & Lindsey 2017 (EJP) | — | Abstract only, no numbers used | B | Paywall |
| Kim et al. 2014; Maccoll; Taneda | Smooth spheres | Negative Magnus only at Re ≳ 4.6e4 and S < 0.6, mostly 1e5–2e5 | B | Kim's ranges are known only from snippets and secondary quotes |
| Vilumbrales 2024 | Rough spheres, wind tunnel | Re_c = 75000·exp(−431 k/d) + 49600; Cl max 0.35–0.40 | C | Preprint |
| Sareen 2024 | Spinning sphere | Sudden drop in Cl and Cd at a critical rotation for 1e3 < Re ≲ 5e4 | B | Abstract only |
| Nathan (spin-down note) | Golf / baseball | β = 0.009–0.012 in C_M = β S | B | Different ball |
| FUEL drop test (FRC 2017) | 5 in perforated ball | Recomputed Cd 0.88 | D | Forum |
| Team 254 (2017) | Perforated FRC ball | The ball veers depending on hole orientation | D | Observation |

Ito & Kamijima lift-crisis values (B):

| Re | C_L peak (S) | C_L trough (S) |
|---|---|---|
| 26 500 | 0.318 (0.565) | 0.207 (0.942) |
| 40 000 | 0.288 (0.503) | 0.183 (0.880) |
| 46 500 | 0.280 (0.538) | 0.165 (0.862) |
| 53 000 | 0.271 (0.471) | 0.153 (0.848) |
| 6 600–13 000 | dips only 0.06–0.07 | |

### 2c. Launcher sources

| Source | Content | Grade |
|---|---|---|
| Brettle (Carlmont notebook) | Hood with a single wheel and rigid rolling: v = ω_wf r_w / 2, S = 1. Includes flywheel speed drop and efficiency η | C (theory) |
| Pedersen 2026 (FRC 449) | General two-surface no-slip model. Corrects Brettle's hood impulse. Frictionless hood gives S = 1/k. ReCalc effectively halves I_w. Forum note: measured KE is about 56 % of ideal for tennis balls | C (theory, plus forum data) |
| Chief Delphi 394940 and others | Exit speed / surface speed ≈ 0.30–0.45 on other balls | C |
| Couturier, Vella, Boudaoud 2022 | Shell indentation; Reissner linear limit K = 4Et²/(R√(3(1−ν²))) per contact, valid for δ ≲ t | B (theory) |
| Van Wyk 2026 | Pickleball dynamic stiffness 87.6 kN/m (within-ball CoV 18 %) and flat-plate COR 0.20 (CoV 7.5 %), both at 26.8 m/s | B (different ball, higher speed) |

**No published spin measurement exists for any single-wheel hooded shooter.**

### 2d. Impact and capture sources

| Source | Content | Grade |
|---|---|---|
| Cross 2005, AJP 73 | Bounce near normal incidence: e_x model, spin retained (Eqs. below) | **A** (tennis) |
| Cross 2002, AJP 70 (grip–slip; horizontal COR) | Tennis e_x 0.10–0.24; superball 0.49–0.76. In-bounce friction μ_A is about 3× below quasi-static μ_S at 45°. Real tennis-ball α = 0.55 | **A** (tennis) |
| Allen, Haake, Goodwill 2010 | μ matters only when the ball slides throughout the impact | B (abstract only) |
| Okubo & Hubbard 2004; Hubbard 2005 | Backspin helps capture on long rolling rim contacts; about +10 % makes | B / C (basketball) |
| Antali 2021 | Rim outcomes can be unpredictable | B (theory) |
| Tebbe 2020 | Trajectory fitting classified medium and high backspin correctly only 58–60 % of the time | B |

---

## 3. Model inputs: ranges and comparison with PM-001

"Inside" means the PM-001 value lies within the evidence range. "Optimistic" means it favours the backspin idea or underestimates losses. "Pessimistic" means the opposite.

| Input | Low / nominal / high (literature) | Grade | PM-001 now | Verdict |
|---|---|---|---|---|
| **Cd** | 0.33 / 0.50 / 0.90; optional spin term +0–0.15·min(S/0.6, 1) | C | 0.35 / 0.48 / 0.65 | Nominal inside. **High is optimistic**: a spinning, perforated ball at Re ≤ 5e4 can reach 0.8–0.9 (Lindsey control ball, Wiffle at low Re, Muto 0.66 at S = 1, FUEL 0.88) |
| **Cl(S)**, linear-capped (c1, cap) | **floor 0.02/0.04**; low 0.20/0.15; nominal 0.35/0.25; high 0.80/0.40 | floor C, others B | low 0.15/0.10, nominal 0.35/0.25, high 0.80/0.40; Cl = 0 floor mentioned only in text | Nominal and high inside. **PM-001's low is not the worst case**: the floor set (Lindsey Magnus-only reading) is much lower. The high set is generous for a perforated ball |
| Cl lift-crisis dip | Table in `params_lit.json` (`Cl.dip_variant`): Cl 0.29 at S 0.5 → 0.18 at S 0.88 → 0.30 at S 1.1 | B | Not modelled | Missing. It matters mainly when exit S is about 0.85–0.95. With the hood (S ≈ 1.0–1.3) the ball starts just past the trough, and S rises in flight (1.06 → 1.5–1.7), so the effect is small for the PM-001 hood case |
| Reverse Magnus | Low probability at POLLEN Re | B | Text only, "run Cl = 0" | Inside. It cannot be excluded, because perforated-ball lift data stop at S ≈ 0.56 in backspin (Van Wyk) and S ≈ 0.65 in topspin (Lindsey, unreviewed) |
| Non-Magnus hole force | Cl-equivalent 0 / 0.03 / 0.15, random direction | B (Wiffle) / D | Not modelled | Missing. It adds scatter, not bias: at S ≈ 1 the ball turns 30–50 rev/s, so the force averages out |
| **Spin decay k** | Preferred form k = 0.30 β \|v\|, β 0.009 / 0.02 / 0.05. Constant k 0.005 / 0.03 / 0.15 s⁻¹: the nominal is β 0.02 at \|v\| ≈ 5 m/s; the low and high are β 0.009 at ≈ 2 m/s and β 0.05 at ≈ 10 m/s | B | 0.01 / 0.05 / 0.30 (constant) | Nominal inside. **High is pessimistic** beyond any evidence. Second-order: a 1.2 s flight loses 0.6 % / 3.5 % / 17 % of its spin |
| **I_b, α** | α 0.60 / 0.63 / 0.667; mass 23.5 / 24.95 / 27.5 g | B / C | α same; mass high 26.5 g; launcher k_I low 0.55 | Mass high bound slightly low (listing weight 27.2 g). k_I 0.55 is pessimistic but harmless |
| **μ_wheel** | 0.5 / 0.8 / 1.2 | D | same | Inside, but unsourced |
| **μ_hood** | 0.05 / 0.3 / 1.0 | D | same | Inside. Use the sliding in-contact μ, which Cross found is about 3× below the static value |
| **N(δ)** | Reissner initial slope per contact 45–270 kN/m (E 0.2–1.2 GPa, *E range from memory, unverified*), i.e. 22–135 kN/m across the diameter, valid up to δ ≈ t = 1.8 mm. Beyond that, buckling and a plateau of unknown height. N(4 mm) 6 / 25 / 150 N | B (form) / D (values) | Linear k_n 1.5 / 4 / 10 N/mm, so N(4 mm) 6–40 N | **The form is wrong** (it should be nonlinear) and the high end is probably low. This changes the grip-limited top speed and how much the flywheel slows; it barely changes S |
| Exit speed / surface speed | 0.30 / 0.42 / 0.50 | C | about 0.46–0.47 below the grip limit | Optimistic side |
| Energy knockdown vs rigid model | 0.55 / 0.8 / 1.0 | C | Not modelled (c_rr covers part of it) | Missing. Apply when comparing with tests |
| **S at exit, hood** | 1.0 / 1.06 / 1.6 | B (theory) | 1.03–1.27 at 3000 rpm | Inside. Values above about 1.3 need μ_hood < 0.1 |
| S at exit, passive roller | 1.0 / 1.15 / 1.67 | B (theory) | 0.91–1.24 | Inside. S < 1 occurs only transiently |
| **COR e_n vs speed** | 0.30 / 0.50 / 0.75 at 3–8 m/s | D | E_GRID 0.3–0.8 | Inside. Van Wyk's 0.20 at 26.8 m/s is a lower-bound proxy (polymer-shell COR rises at low speed). Pickleball drop-spec COR of about 0.62–0.66 is *from memory, unverified* |
| **Tangential e_t (e_x)** | −0.1 / 0.05 / 0.25 | A (tennis) | default 0, variant 0.3 | Default inside. **The 0.3 variant is optimistic**: it exceeds every hollow-ball value |
| **Impact μ** | 0.2 / 0.4 / 0.8 | D | MU_GRID 0.2–0.8 | Inside |

## 4. Equations to adopt

### 4.1 Launcher: Brettle versus Pedersen

**Brettle** (hood with one wheel, rigid ball, rolling without slip on both surfaces). Here k_p = I_p/(m_p r_p²) and k_w = I_w/(m_w r_w²).

```
v_exit = omega_wf * r_w / 2          S_exit = omega_b R / v = 1
omega_wi / omega_wf = 1 + (1 + k_p)/(4 k_w) * m_p / m_w
eta = [2 + (1 + k_p)/(4 k_w) * m_p / m_w]^-1
```

**Pedersen** (general form, which contains Brettle). The model has two surfaces, and the second surface turns at ω_w2 = G·ω_w1; G = 0 is a fixed hood. The no-slip conditions are:

```
omega_w1 r_w1 = V_b + R omega_b
omega_w2 r_w2 = V_b - R omega_b
=> S_exit = (r_w1 - G r_w2) / (r_w1 + G r_w2)       (G = 0: S = 1)
```

Results:
- The hood's friction impulse on the ball points forward, H_h = m V (1 − k)/2 with k = α, and it lowers spin.
- With a frictionless hood, S = 1/k = 1/α ≈ 1.5–1.67 and V = u·k/(1+k).
- A free roller gives an S between 1 and 1/k.
- Starting from rest: V_bf = (r_w ω_wi / 2) / [1 + m_b r_w² (1 + k)/(4 I_w)].

**Difference from `src/launcher.py`.** src/ is more general than either paper. It is a 2×2 box LCP for Coulomb stick/slip with linear N(δ) and centripetal unloading, and it reproduces S ≈ 1.06 for the hood case. Neither paper checks the no-slip assumption, which needs |H_h| ≤ μ_hood·N.

Recommendations:
1. Keep src/. Add unit tests that recover Pedersen's rigid limits: S = 1 for a gripping hood, S = 1/α for a frictionless hood, and the V_bf flywheel drop.
2. Report the hood no-slip check explicitly.
3. Replace linear N(δ) with a piecewise law: a Reissner ramp, then a plateau.
4. Add an energy-knockdown factor (0.55–1.0) when comparing exit speed with tests.

### 4.2 Impact: Cross grip/slip

Cross 2005 (grade A for the form). R is the ball radius, α = I/(mR²), e_x is the horizontal COR of the contact point, and subscripts 1 and 2 mean before and after the bounce:

```
v_x2 / v_x1     = (1 - alpha e_x)/(1 + alpha) + alpha (1 + e_x)/(1 + alpha) * R omega_1 / v_x1
omega_2/omega_1 = (alpha - e_x)/(1 + alpha) + (1 + e_x)/(1 + alpha) * v_x1 / (R omega_1)
```

- e_x ≈ 0–0.2 when the ball grips (maximum about 0.2 near 50°), about 0.06 near normal incidence on a heavy rigid surface, and below 0 when the ball slides throughout.
- In a normal impact with backspin, spin retained = α/(1+α) − e_x/(1+α): 0.388 at e_x = 0 and 0.266 at e_x = 0.2.

**Difference from `src/contact.py`.** There is no conflict. src/ uses the Walton/Brach impulse model:
- normal impulse P_n = −(1+e)·m·v_cn;
- stick impulse P_t* = −(1+e_t)·m_t·v_ct, with m_t = mα/(1+α);
- Coulomb cap |P_t| ≤ μP_n.

When the contact sticks this is algebraically identical to Cross with e_t = e_x. The slip branch gives the sliding-throughout case, which Cross reports as e_x < 0. Two recommended changes:
- narrow the e_t grid to −0.1…0.25 and drop 0.3 as a headline case;
- use an in-bounce μ, not a quasi-static one.

### 4.3 Aerodynamics: Lindsey's revised lift model

Lindsey fits lift as an offset plus a slope, |Cl| = a + b·S, separately for backspin (a 0.173, b 0.02, S ≤ 0.37) and topspin (a 0.24, b 0.44). The fit itself reports magnitudes only; the signs come from the spin direction. The source cannot say whether the 0.17 backspin offset is spin lift or a non-Magnus force: there is no non-spinning control in the fit, and both worked examples are topspin.

**Difference from `src/flight.py`.** src/ uses Cl = min(c1·S, Cl_max), which has no offset and vanishes at S = 0. Do not adopt Lindsey's offset as Magnus lift:
- applied to backspin, it would add about 0.17 Cl of upward force even with no spin;
- extrapolated from S ≤ 0.37 to S ≈ 1.5, it is not supported.

Adopt it only as two bounds:
- the **floor** set (c1 0.02, cap 0.04), the Magnus-only reading;
- the existing nominal (0.35/0.25), which roughly matches the offset-as-lift reading at S ≈ 1 (0.17 + 0.02 ≈ 0.19–0.20).

The lift-crisis table (`Cl.dip_variant`) is a separate structural variant. src/ cannot read it now; it would need an `interp` branch in the Cl function.

## 5. Errors found in current PM-001 docs and data (for the owning agents to fix)

1. `aero_params.json` and `docs/02_aero.md` cite Lindsey as covering "5–13 m/s" with "positive backspin Cl ≈ 0.2, weak S dependence". **Correct:** 6.0–11.5 m/s and S ≤ 0.37. The Magnus slope is only about 0.02 and the offset is ambiguous.
2. Rossmann & Rau is described as "full text not retrieved" with Cd 0.6 "forward-facing". **Correct:** the full text was read. Cd ranges from 0.36 to 1.05, and 0.6 is the β = 90° orientation.
3. Kim 2014's Re/S window comes from snippets only; mark it as such.
4. `crosscheck/empirical/EVIDENCE.md` row 19 labels Lindsey as "Emond/Sun/Swartz 2024" with grade A. **Correct:** Lindsey 2025, grade C (unreviewed web article).
5. `02_aero` says free-flight table-tennis tests show no negative Magnus. Conti 2026 (preprint) shows a Re-dependent dip in Cl, to about 0.17 at Re 4.5e4 (derived), though not a sign change (its model cannot produce one).
6. Muto's Γ definition is ambiguous, and its subcritical Cd is unreliable by the authors' own account. Do not use 0.474/0.661 as anchors.
7. The mass high bound of 26.5 g is below the 27.2 g listing weight.
8. Haron et al. COR numbers could not be verified (blocked by a captcha); keep them out.

## 6. Sensitivity (computed, not quoted)

I ran a 2D point-mass model with a scratchpad script (ρ 1.20, m 24.95 g, R 35.5 mm, exit S 1.06, k 0.03 s⁻¹, spin rising in flight to S ≈ 1.5–1.7). Because the script is not saved in the repo, treat these numbers as indicative.

**Fixed launch, 7 m/s at 50°: apex rise over the no-lift path**

| Cl set | Cd 0.45 | Cd 0.85 |
|---|---|---|
| floor | +0.8 cm | +0.7 cm |
| low | +4.5 cm | +3.8 cm |
| nominal | +7.5 cm | +6.3 cm |
| high | +12.1 cm | +10.1 cm |
| smooth dip | +9.5 cm | +7.9 cm |

- At the same downrange point the descent angle changes by less than 1°.
- Changing Cd from 0.45 to 0.85 shortens the range by about 46 cm. Drag matters more than lift at a fixed launch.

**Same target (3.0 m downrange, 1.0 m up): entry angle below horizontal**

| Case | floor | low | nominal | high | dip |
|---|---|---|---|---|---|
| Cd 0.45, 50° launch | 31.6° | 32.7° | 33.6° | 35.0° | 34.1° |
| Cd 0.45, 65° launch | 59.7° | 60.8° | 61.7° | 63.1° | 62.2° |
| Cd 0.85, 50° launch | 35.0° | 36.3° | 37.2° | 38.7° | 37.8° |
| Cd 0.85, 65° launch | 62.6° | 63.8° | 64.7° | 66.0° | 65.2° |

What these tables show:
- When the shot is aimed at the same target, backspin *steepens* the entry, by up to about 3.4° from floor to high. The trajectory has to arc higher to carry the lift.
- Moving Cd across its range shifts the entry angle by about the same amount (3–3.5°).
- The launch angle the team chooses changes the entry angle by about 28°, far more than either.
- Magnus lift therefore cannot rescue a shot on its own. Its main lever is how the ball behaves after impact, not the flight path.

## 7. What would change the verdict

1. **Effective backspin Cl of POLLEN at S 0.8–1.7.** This is the dominant open question.
   - If Cl ≲ 0.05 (the floor), Magnus does nothing useful in flight.
   - If Cl ≈ 0.25–0.35, the apex is 7–12 cm higher and entry is about 2–3° steeper, a small but real effect.
   - **Cheapest decisive test:** film side-on at 240–480 fps with a scale grid and a marked ball, n ≥ 10 shots per setting. Fire the same shooter with the wheel *below* (backspin) and *above* (topspin) at the same rpm.
     - Half the difference in fitted vertical acceleration gives Cl; the mean gives Cd.
     - Fit noise σ_a ≈ 0.02 m/s² resolves even the floor case (about 0.05 m/s² at 5 m/s).
   - Count spin directly from the marked ball. Do not infer it from the fit: Tebbe got only 58–60 % correct classification that way.
2. **Cd at S ≈ 1.** This is comparable in effect to Cl. Measure it in the same filming, with drop tests from about 3–4 m as a check, and with a taped-holes ball to isolate the effect of the holes.
3. **Measured exit S.** Every launcher source is theory. If a real hood gives S well above 1.3, the hood is slipping. If it gives S below 1, the wheel/hood geometry is not what the model assumes. A single wheel locks S at about 1, so the same machine cannot provide a no-spin control. The wheel-above versus wheel-below comparison is the control.
4. **Bounce behaviour in the HIVE CELL**, which is likely the larger lever:
   - the COR e_n of POLLEN on the HIVE surface at 3–8 m/s (drop test);
   - the sliding μ (incline);
   - e_x (an angled bounce filmed at high speed).
   - Rule of thumb: if e_n ≲ 0.4 and e_x ≈ 0, bounce-outs are rare whatever the spin. If e_n ≳ 0.6, backspin's 27–39 % spin retention and the reversed horizontal kick become decisive.
   - The only POLLEN bounce-out figure is a D-grade 44 % with unknown spin.
5. **N(δ) of the shell** on a plate, up to 8 mm. This sets the grip limit and the flywheel drain, not S. Measure it if the speed at the grip limit matters.
6. **Spin decay β.** This is second-order. It matters only if β ≳ 0.1, which no evidence suggests.

## 8. Recommended parameter changes (all in `research/params_lit.json`)

- Cd: high 0.65 → **0.90**; nominal 0.48 → 0.50; low 0.35 → 0.33.
- Cl: add a **floor** set (0.02 S, cap 0.04); low (0.15/0.10) → **0.20/0.15**; keep nominal and high; add the lift-crisis `dip_variant` table.
- Spin decay: 0.01/0.05/0.30 → **0.005/0.03/0.15** s⁻¹, or better, the β model with β 0.009/0.02/0.05.
- Mass high bound: 26.5 g → **27.5 g**, and I_b high → 2.36e-5.
- Launcher:
  - N(δ) linear → **piecewise Reissner plus plateau**; widen N(4 mm) to 6–150 N;
  - add the hood no-slip check;
  - add the energy-knockdown factor 0.55–1.0;
  - use exit speed / surface speed 0.30–0.50 for comparisons with tests.
- Contact: e_t grid → **−0.1 / 0.05 / 0.25** (drop 0.3); e_n 0.30–0.75; μ unchanged.
