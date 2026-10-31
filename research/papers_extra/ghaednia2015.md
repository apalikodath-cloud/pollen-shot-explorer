# Ghaednia, Cermik & Marghitu (2015): Oblique impact of a tennis ball with a racket

source_id: `ghaednia2015` (the target paper, source #21 in RESEARCH_PAPERS.md). Companion source: `cermik2017diss`, the second author's open Auburn PhD dissertation. Its Chapter 3, "Impact of a hollow ball with a flexible flat", reports the same experiment and model with the same advisor (Marghitu), and the dissertation cites the 2015 paper as its ref. [24]. The dissertation is **not** the 2015 paper. Every row below says which of the two it came from.
Read: 2026-10-30, research agent for PM-001 (source #21 task).

## 1. Citation, access, review status

| Field | Value |
|---|---|
| Citation | H. Ghaednia, O. Cermik and D. B. Marghitu, "Experimental and theoretical study of the oblique impact of a tennis ball with a racket", *Proc. IMechE Part P: J. Sports Engineering and Technology* **229**(3), 149–158 (2015). DOI 10.1177/1754337114567490 |
| Dates (Crossref) | Online 26 Jan 2015; issue Sep 2015. 28 references. |
| Affiliation | Department of Mechanical Engineering, Auburn University, AL, USA |
| Review status | Peer-reviewed journal article (Crossref type journal-article). Crossref shows 6 citations and Semantic Scholar 18. |
| Method type | Experiment (drop tests filmed at 10,000 fps onto a clamped racket) plus a lumped spring–damper contact model. The model is fitted to the normal-impact data and compared with the oblique-impact data. |
| Access, paper | **Abstract only.** SAGE returns HTTP 403 for both doi.org and journals.sagepub.com. Unpaywall reports `is_oa=false`, `oa_status=closed`, and no repository copy. Semantic Scholar reports `openAccessPdf.status=CLOSED`, and the publisher withholds the abstract from it. The abstract text below comes from the Crossref record. |
| Access, companion | **Full text.** Cermik, O., *Experimental and Theoretical Analysis of the Impact with Solid and Flexible Surfaces*, PhD dissertation, Auburn University, 2017 (hdl 10415/5668; embargo ended 2019-05-06). Chapter 3 (pp. 34–67) and §2.4.1 (pp. 23–29) were read as text, and the figure pages (pp. 29, 36–37, 53–55, 66) were rendered as images. |
| Consequence | No figure, table or equation from the 2015 paper itself was seen. The numbers in §5 come from the dissertation, labelled `cermik2017diss`. Its results may differ from the paper's in detail (for example a different subset of drops, or re-fitted k and b). |

URLs tried:
- https://doi.org/10.1177/1754337114567490 → https://journals.sagepub.com/doi/10.1177/1754337114567490 (403, also with a browser user-agent)
- https://api.crossref.org/works/10.1177/1754337114567490 (metadata, abstract, reference DOIs)
- https://api.unpaywall.org/v2/10.1177/1754337114567490 (closed)
- https://api.semanticscholar.org/graph/v1/paper/DOI:10.1177/1754337114567490 (closed; abstract elided)
- WebSearch (2 queries; no free copy of the paper found)
- https://etd.auburn.edu/discover?query=Ghaednia and https://etd.auburn.edu/discover?query=Cermik (the second found the companion)
- https://etd.auburn.edu/handle/10415/5668?show=full (dissertation record)
- https://etd.auburn.edu/bitstream/handle/10415/5668/Cermik_Dissertation_May_2017.pdf?sequence=2&isAllowed=y (**full text**, 128 pp., downloaded to a fresh %TEMP% folder and converted to text only; nothing was executed)
- https://etd.auburn.edu/handle/10415/5931 (Ghaednia's own dissertation is on elastic–plastic **metal** impacts, so it is not the tennis study; record only)

## 2. What the 2015 paper reports (abstract, verbatim from Crossref)

> "The normal and the oblique impact of a tennis ball with a racket has been studied. An accurate setup has been built in order to provide consistent initial conditions for the impacts. Experiments have been done for a wide range of impact angles and initial velocities. The motion of the ball before, during and after the impact has been recorded using a high-speed camera with 10,000 frames per second. The impact has been divided into two phases, compression and restitution. An expression for the contact force has been provided. The coefficient of restitution and effective coefficient of friction have been analyzed experimentally. For low impact velocities, the coefficient of restitution is constant at different impact angles. The effective coefficient of friction changes as a function of the impact angle. The contact force expression has been determined for the compression and the restitution phases using the experimental data from normal impact experiments. The simulation and experimental results are compared and verified for the normal and the oblique impacts."

Findings stated in the abstract (peer-reviewed; **no numbers were visible in the paper**):
1. The impact is split into a **compression** phase and a **restitution** phase, with a contact-force expression for each phase. **[peer-reviewed finding]**
2. **At low impact speeds, the COR does not depend on impact angle.** **[peer-reviewed finding]**
3. **The "effective coefficient of friction" changes with impact angle.** **[peer-reviewed finding]** §4 argues that this is the signature of a ball that reaches grip. It does not mean the material friction changes.
4. The contact law was fitted to **normal** impacts and then predicts the **oblique** impacts. **[peer-reviewed finding]**

Crossref references include Cross 2002 (horizontal COR, 10.1119/1.1450571), Cross 2002 (grip–slip, 10.1119/1.1507792), Allen et al. 2010 (10.1243/17543371JSET66), Goodwill & Haake, Dignall & Haake 2000, Brody et al. 2002, Goldsmith 2001, and the Hough-transform paper (10.1145/359863.359882). Cross 2010 (tangential compliance) is **not** in the list.

## 3. Method (from the companion dissertation, Ch. 3 and §2.4)

**[observation of method; companion, unreviewed]**
- Ball: tennis ball, D = 67 mm, m = 56.7 g. It was dropped from rest by a robotic arm from 0.025–1.031 m, so the **inbound spin is zero**. At least 3 drops were made per height.
- Surface: a tennis racket fixed in a stringing device and clamped to a table (a clamped racket, not freely suspended). The racket angle β to the horizontal was set with a tripod to ±1°. Five angles were used: β = 0, 15, 30, 45 and 57°. Because the ball falls vertically, **β is the incidence angle measured from the surface normal**. (Cross 2010 measures θ1 from the surface, so the two conventions differ.)
- Speeds: five initial speeds per angle in 0.5–4.5 m/s. More than 110 impacts were analysed.
- Imaging: 10,000 fps at 512 × 512 px, lit by four 1000 W projectors. The centroid comes from a Hough transform, which works even when the racket frame hides part of the ball. Rotation comes from digital image correlation (DIC) on a speckle pattern (§2.4.1). Pre- and post-impact velocities come from 100 frames on each side of the impact.
- Contact model (Eqs. 3.6–3.10), rigid-ball equations of motion in the contact frame:
  - Compression: **P = k δ − b δ̇** (Kelvin–Voigt). It ends when the contact-point normal velocity is zero, at maximum indentation δ_m and force P_m.
  - Restitution: **P = k δ**. The unloading is taken as fully elastic, and damping is dropped "as it has been proved in contact mechanics field".
  - Friction: **F_f = μ P**, opposing the contact-point tangential velocity, so the ball **slides throughout**. μ is the "kinetic coefficient of friction", and in the simulation it is set to the experimental **effective** μ for each angle.
  - Equations: m a_C = G + T and I_C α = r_CE × T, with gravity included.
- Effective friction (Eq. 3.12): **μ_eff = m[v_Cx(t_f) − v_Cx(t_0)] / m[v_Cy(t_f) − v_Cy(t_0)]**, the ratio of the tangential to the normal impulse taken from the centre-of-mass velocities. The dissertation calls it "the average friction throughout the impact".
- COR: Newtonian, e = |v_n,out / v_n,in| at the contact point.

## 4. Equations and how to read them for PM-001

| # | Equation | Symbols / units | Source |
|---|---|---|---|
| G1 | P = k δ − b δ̇ (compression); P = k δ (restitution) | P normal force [N]; δ indentation [m]; k [N/m]; b [N·s/m] | cermik2017diss Eqs. 3.6 and 3.10 |
| G2 | F_f = μ P, opposing contact slip | μ kinetic friction [–] | cermik2017diss Eq. 3.8 |
| G3 | μ_eff = Δv_t / Δv_n (impulse ratio, CM velocities) | [–] | cermik2017diss Eq. 3.12 |
| G4 | e = |v_E(t_f)·j / v_E(t_0)·j| | [–] | cermik2017diss Eq. 3.11 |

**Derived reinterpretation (this note, not the authors'): μ_eff in G3 is an impulse ratio. It equals the material Coulomb μ only if the ball slides for the whole contact.** **[theory, derived here]**
For a rigid ball with zero inbound spin that **reaches rolling** at release (Brody/Cross grip branch, as in allen2010.md §4.2), the impulse ratio is set by kinematics, not by μ:

  μ_eff,grip = [α / ((1 + α)(1 + e))] · (v_t / v_n) = [α / ((1 + α)(1 + e))] · tan β

With the dissertation's mean e = 0.88, this gives **0.189 tan β** for α = 0.55 (the tennis-ball value Cross 2010 uses) and **0.213 tan β** for α = 2/3 (thin shell). The dissertation's Fig. 3.24 plots μ_eff against tan β as a near-straight line. Its averages, read from the figure (±0.01), are ≈ 0.045, 0.115, 0.21 and 0.325 at tan β = 0.27, 0.58, 1.0 and 1.54, which is ≈ 0.17–0.21 × tan β. **That is the grip prediction.** Checking the reported velocities directly (dissertation §3.2.2 and §3.3.2):

| β | v_t in → out (local, m/s), as reported | μ_eff from these (derived) | rolling-exit v_t for α = 0.55 / 0.667 (derived) |
|---|---|---|---|
| 15° | −0.57 → −0.39 | 0.037 | 0.37 / 0.34 |
| 30° | −1.80 → −0.94 | 0.137 | 1.16 / 1.08 |
| 45° | −2.50 → −1.43 | 0.207 | 1.61 / 1.50 |
| 57° | −3.20 → −1.91 | 0.297 | 2.06 / 1.92 |
| 45° (§3.3.2 case) | −2.68 → −1.68 | 0.179 | 1.73 / 1.61 |
| 57° (§3.3.2 case) | −2.61 → −1.55 | 0.319 | 1.68 / 1.57 |

The measured exit tangential speeds sit at or a little below the rolling value. That fits a ball that **grips and then rolls, or slightly overspins (e_x ≥ 0)**. It does not fit a ball that slides throughout with a fixed μ. The authors read the trend differently: "When the impact angle increases the ball stays in sliding regime for a longer period, which increases the coefficient of friction." Their reading has a consequence. A sliding-throughout model fed the **same** μ_eff that was measured from Δv_t reproduces Δv_t by construction, so the reported < 10% agreement on tangential velocity is **not independent evidence** for the friction model. The normal-direction agreement does test the k–b law.

Corollary (derived): if the ball gripped at every angle, then the true Coulomb μ for tennis ball on strings is **at least** the largest μ_eff observed, ≈ 0.3 at β = 57°. Cross 2010 uses μ = 0.4 for "a tennis ball sliding on smooth tennis strings", which is consistent with that.

## 5. Data table

Rows marked `ghaednia2015` are from the abstract only. Rows marked `cermik2017diss` are from the open companion. Rows marked `derived` are this note's arithmetic.

| Quantity | Value | Conditions | Where | source_id | Grade |
|---|---|---|---|---|---|
| Impact phases | compression, then restitution; contact-force expression per phase | tennis ball on racket | abstract | ghaednia2015 | peer-reviewed finding |
| COR vs impact angle | constant at low impact speed | "wide range" of angles and speeds (values not seen) | abstract | ghaednia2015 | peer-reviewed finding |
| Effective μ vs impact angle | "changes as a function of the impact angle" | same | abstract | ghaednia2015 | peer-reviewed finding |
| Frame rate | 10,000 fps | high-speed camera | abstract; diss. §3.2.1 (512 × 512 px) | ghaednia2015 / cermik2017diss | observation (method) |
| Ball | D 67 mm, m 56.7 g, dropped from rest (zero inbound spin) | clamped racket | diss. §3.2, §2.4 | cermik2017diss | observation |
| Angles / speeds | β = 0, 15, 30, 45, 57°; normal speed 0.5–4.5 m/s; ≥ 3 repeats; > 110 impacts | | diss. §3.2, §3.5 | cermik2017diss | observation |
| COR, average | e = 0.88 | all angles, 0.5–4.5 m/s | diss. §3.2.3 text | cermik2017diss | unreviewed technical source |
| COR scatter | ≈ 0.84–0.93 (read from Fig. 3.21) | per drop | diss. Fig. 3.21 | cermik2017diss | unreviewed technical source |
| μ_eff by angle (averages, read from Fig. 3.24 ±0.01) | ≈ 0.045 (15°), 0.115 (30°), 0.21 (45°), 0.325 (57°) | zero inbound spin; about constant with speed at each angle (Fig. 3.23) | diss. Figs. 3.23–3.24 | cermik2017diss | unreviewed technical source |
| μ_eff vs speed | "constant for each angle" over the low-speed range | 0.5–4.5 m/s | diss. §3.2.4 | cermik2017diss | unreviewed technical source |
| Contact stiffness, damping (ball + strings) | k = 13 385 N/m, b = 5.36 N·s/m (mean of 15 normal impacts; one case 12 526 N/m and 6.85 N·s/m) | fit by grid search over k 0–30 000 N/m and b 0–20 N·s/m, minimising the sum of displacement and exit-velocity errors | diss. §3.3.1 | cermik2017diss | unreviewed technical source |
| Model vs experiment, oblique | exit-velocity error < 10% for all cases; e.g. 15°: 5.4% normal, 6.7% tangential; 57°: 7.3% normal, < 1% tangential | k and b from the normal impacts; μ_eff per angle | diss. §3.3.2 | cermik2017diss | unreviewed (tangential part partly circular, §4) |
| Damped restitution phase | worse: at 15° the error rises 5.4% → 19.8% (normal) and 6.7% → 10.1% (tangential); predicts too low a COR (Fig. 3.38) | same | diss. §3.4 | cermik2017diss | unreviewed technical source |
| Simulated compression time | compression ends ≈ 3.1 ms | β = 15°, 2 m/s, model | diss. §3.1.3 | cermik2017diss | theory (fitted model) |
| Measured contact timeline | impact starts 4 ms, restitution starts 7 ms, ends 10 ms (≈ 3 ms compression + 3 ms restitution) | β = 45°, inbound (3.2, −3.2) m/s, DIC | diss. §2.4.1 | cermik2017diss | observation |
| Max indentation (centre travel) | 7.9 mm (normal, 3.26 m/s); 4.3–6.9 mm (oblique cases) | ball + string-bed together | diss. §3.2.2 | cermik2017diss | observation |
| Measured spin during contact | denoised ω rises from ≈ 0 to ≈ 5 rad/s (read from Fig. 2.13) | β = 45° case | diss. Fig. 2.13 | cermik2017diss | observation; **suspect** (see §8) |
| Linear-spring contact time | π√(m/k) ≈ 6.5 ms | m 56.7 g, k 13 385 N/m, no damping | this note | derived | theory |
| Grip impulse ratio | 0.189 tan β (α 0.55) / 0.213 tan β (α 2/3), e = 0.88 | zero inbound spin, rigid-ball grip branch | this note §4 | derived | theory |
| Lower bound on Coulomb μ, ball on string | ≳ 0.3 | if grip was reached at 57° | this note §4 | derived | theory |

## 6. Transfer cautions to POLLEN

**Transfers qualitatively:**
- **"Effective μ" from bounce data is not Coulomb μ unless the ball slid throughout.** **[theory, derived]** This is the most useful lesson for PM-001. If POLLEN bounce tests are reduced with Eq. 3.12, the result grows with tan(incidence) whenever the ball grips. Fitting src/contact.py's μ to those values would make μ wrongly angle-dependent and **underestimate** the true μ at glancing angles.
- **COR independent of angle at low speed.** **[peer-reviewed finding, tennis]** A constant e per surface, as in src/contact.py, is a reasonable first model for a hollow ball at a few m/s. The tested normal speeds (0.5–4.5 m/s) overlap the 2–10 m/s POLLEN contact range. POLLEN still needs its own e(v_n) from drop tests.
- **Compression/restitution split with a Kelvin–Voigt loading law and elastic unloading** fitted the tennis data better than a symmetric damper. **[unreviewed technical source]** This is a usable template if a time-resolved POLLEN contact model is needed, for example for the hood squeeze in src/launcher.py, which already carries a normal stiffness k_n and compression δ. The fitted k and b do **not** transfer.
- **The 10,000 fps + Hough + DIC method** is a good recipe for measuring POLLEN contact durations and rim impacts. **[observation, method]** The team's likely 240–960 fps camera will not resolve the ≈ 3 ms compression phase, so it can measure only in/out states.

**Does not transfer:**
- All numbers: e = 0.88, μ_eff, k, b, contact times. They describe a 57 g felt-covered pressurised rubber ball on a **clamped string bed**, where the string bed supplies most of the compliance. POLLEN is a ~25 g perforated polyethylene shell. The HIVE is presumably a rigid moulded or plastic structure; its materials are not identified (research/COMPLETENESS.md).
- The stiffness and damping represent ball plus strings in series. On a rigid HIVE lip, the ball's own shell stiffness sets the contact time.
- Zero inbound spin only. The study says nothing direct about **backspin**, which is the PM-001 case. Backspin raises the inbound slip and widens the range where the ball slides throughout (see cross2010_check.md, Eq. 7).

## 7. Implications for the PM-001 models and test plan

1. **src/contact.py structure is right; keep μ as a true Coulomb limit.** The slip/stick impulse law (P_t* grip impulse capped at μ P_n) predicts μ_eff ∝ tan β in the grip regime and μ_eff = μ in the slide regime. That is exactly the pattern that explains these data. No code change is implied. **[theory]**
2. **Add a unit test (proposal, not done here: src/ is owned by another workflow).** With zero inbound spin, e = 0.88, α = 0.55 and μ = 0.4, the impulse ratio from `impact()` should equal 0.189 tan β up to the grip limit. That reproduces the tennis Fig. 3.24 trend qualitatively as a model sanity check, not as POLLEN data.
3. **Test-plan rule for POLLEN μ (T-series bounce tests).** Measure Δv_t/Δv_n at several incidences with and without backspin, then plot μ_eff against tan(incidence). Points on a line through the origin with slope α/((1+α)(1+e)) mean grip; read **α** from that slope as a check. A plateau at large tan(incidence) (glancing) is the **Coulomb μ**. Report μ only from the plateau. This replaces a single-angle "effective μ" measurement.
4. **Hood.** This study gives no hood data. The transferable point is the compression/restitution split: in the launcher the hood contact is a sustained, compressed rolling contact and not an impact. So the hood's μ matters only where the ball slips against it (launcher.py's slip_t). The tennis μ_eff values must not be used as μ_hood.
5. **Rim / lip contact time.** Tennis on strings takes ≈ 6 ms in total (measured, 45°) with ≈ 3 ms of compression. A POLLEN shell on a rigid lip is likely shorter, but that is unmeasured. The time matters only if a time-resolved contact or Cross-type compliance model is used. The impulse model in contact.py is instantaneous.

## 8. Caveats

- **Abstract only for the target paper.** Every number comes from the companion dissertation, which is unreviewed in the journal sense and was written 2 years later. The paper may report different fitted k and b, or different subsets.
- Some numbers were read off figures (COR scatter, μ_eff averages, spin) at ±0.01, or ±1 rad/s for spin. Text-stated numbers (e = 0.88, k, b, velocities, errors) were copied directly.
- **The spin data look inconsistent.** Fig. 2.13 shows ≈ 5 rad/s after a 45° impact whose tangential exit speed is near 2 m/s. A rolling exit would need tens of rad/s (≈ 2/0.0335 ≈ 60 rad/s, derived). The DIC rotation is probably under-resolved; the dissertation itself notes noise "due to low resolution". Do not use these spin values. They also show why POLLEN spin tests need a high-contrast diametral line or fiducials and enough pixels across the ball.
- The impact timelines in dissertation §3.2.2 (for example 0.0092 → 0.017 s for the normal case) are inconsistent with the 3 + 3 ms timeline in §2.4.1. The "impact" window in §3.2.2 probably includes tracking margin, so §5 does not quote it as a contact time.
- §4's grip reinterpretation is this note's own reading (**theory, derived**). It is not stated by the authors. It depends on α for a tennis ball (0.55 per Cross 2010, secondary) and on e = 0.88.
