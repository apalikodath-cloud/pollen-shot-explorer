# Isomura, Hayakawa, Asai & Ariizumi (2016): Aerodynamic Model of Spinning Table Tennis Ball

source_id: `isomura2016` (source #16 in RESEARCH_PAPERS.md). No companion source was used. Every number below is from the paper's own PDF (4 pages, Japanese with an English abstract) unless a row says **derived here**.
Read: 2026-10-30, research agent for PM-001.

## 1. Citation, access, review status

| Field | Value |
|---|---|
| Citation | 磯村優樹, 早川義一, 浅井徹, 有泉亮, 「スピンをしながら飛翔する卓球ボールの空力モデルについて」 / Y. Isomura, Y. Hayakawa, T. Asai and R. Ariizumi, "Aerodynamic Model of Spinning Table Tennis Ball", *Proceedings of the 59th Japan Joint Automatic Control Conference* (自動制御連合講演会講演論文集), paper ThD6-4, pp. 621–624 (2016). DOI 10.11511/jacc.59.0_621 |
| Dates | Conference 10–12 Nov 2016, Kitakyushu (printed on p. 621). J-STAGE online 1 Feb 2017. |
| Affiliation | Nagoya University (Isomura, Asai, Ariizumi); Aichi Institute of Technology (Hayakawa) |
| Review status | **Conference proceedings (講演論文集). No evidence of peer review was found.** The J-STAGE record does not mark it as refereed. Graded here as an **unreviewed technical source** for its CFD output, and as **theory** for the equation forms it restates. |
| Method type | **CFD only** (commercial code PHOENICS, CHAM-Japan): a fixed spinning ball in a virtual wind tunnel, then least-squares polynomial fits with AIC order selection. The experimental validation is **only proposed** (§4 of the paper). The paper says so: 「本論文ではその検証方法を述べるだけとなる」 ("this paper only describes the verification method"). |
| Access | **Full text read.** The J-STAGE PDF is open. poppler could not decode the Japanese fonts (missing Adobe-Japan1 CMap), so the PDF was re-extracted and the pages rendered with PyMuPDF. All four pages, every table, and Figs. 6–9 were inspected as images. |
| Language | Japanese body text; this note's translations are the research agent's own. |

URLs tried:
- https://doi.org/10.11511/jacc.59.0_621 → https://www.jstage.jst.go.jp/article/jacc/59/0/59_621/_article/-char/ja/ (200; metadata and Japanese abstract)
- https://www.jstage.jst.go.jp/article/jacc/59/0/59_621/_pdf/-char/ja (200; **full PDF, 4 pp.**; saved to `%TEMP%\pm001_isomura_gVOk\iso.pdf`, not executed)
- https://api.crossref.org/works/10.11511/jacc.59.0_621 (404, "Resource not found")
- https://nagoya.repo.nii.ac.jp/records/12565 (503; a related Nonomura/Nakashima/Hayakawa coefficient-identification paper found by search; **not read**)
- Web searches (2), in English and Japanese, for an experimental follow-up by the same authors. **None was found**, so the CFD fits remain unvalidated as far as this search could tell.

## 2. What the paper reports

English abstract (verbatim): "We propose an academic model of spinning table tennis ball. The object of this study is the realization of table tennis robot. It is complex to analyze drag coefficient and lift coefficient of table tennis ball. To analyze this movement, we use Computational Fluid Dynamics software calculation." Key words: Table tennis ball, Sp parameter.

Findings, translated and graded:
1. **Working hypothesis (stated as a hypothesis, 予想):** over the speed and spin ranges of normal table-tennis rallies, C_D and the lift coefficient C_M can be approximated as functions of the spin parameter Sp alone. *Grade: theory / assumption.*
2. **Re independence of C_D is argued from a smooth-sphere handbook curve** (JSME handbook C_D–Re plot, their Fig. 2), not from their own data: for ball speeds 0.5–10 m/s they compute Re between 1.323×10³ and 26.46×10³ and read C_D as Re-independent there. *Grade: theory (textbook smooth sphere).*
3. **The CFD shows C_D rising with Sp, and C_M falling with Sp.** Runs with different (V_x, ω_y) pairs that share the same Sp collapse roughly onto one curve. The authors read that as support for an Sp-only model. *Grade: unreviewed technical source (CFD, not validated).*
4. **At Sp = 0.1, C_M scatters widely.** The authors list numerical error from the small ω_y, Re effects and "other fluid-dynamic factors" as candidate causes, and say the cause is **not identified**. *Grade: unreviewed technical source.*
5. **AIC model selection over N = 56 CFD points picks a degree-2 polynomial for C_D and a degree-4 polynomial for C_M** (Table 3). *Grade: unreviewed technical source.*
6. **Conclusion (§5):** C_D and C_M can be approximated "with fairly good accuracy" by degree-2 and degree-4 polynomials in Sp. Experimental verification is future work. *Grade: unreviewed technical source; the authors themselves call it unverified.*
7. **Proposed validation:** fit the polynomial coefficients to 150 fps three-dimensional trajectories, optionally with 900 fps spin measurement (eqs. 8 and 9). *Grade: method only; no results.*

## 3. Method (as stated)

- **Code:** PHOENICS (3D thermo-fluid analysis software). The paper does **not** state the turbulence model, whether the solution is steady or unsteady, how the spin was imposed (for example a rotating-wall boundary condition), the convergence criteria, or the time-step.
- **Domain:** a box L_x × L_y × L_z = 0.5 × 0.25 × 0.25 m. Inlet at x = 0, outlet at x = L_x, the other faces solid walls. Ball fixed at x_b = 0.125 m, y = 0.125 m, z = 0.125 m (the paper prints "xy" and "xz" for y_b and z_b, an evident typo). Air enters at V_x along x. The ball spins about y at a constant ω_y rad/s.
- **Mesh:** the box is split into 125 sub-blocks. Each block uses one of 8 Cartesian spacings (Table 1). Every spacing is 0.005 or 0.001 along each axis, so the finest cells are 0.001 × 0.001 × 0.001 (units m by context). Domain size and mesh were chosen by refining "from coarse to fine until the result converged" and then keeping "the coarsest mesh that seemed sufficiently converged", and the smallest box free of wall effects. **No grid-convergence numbers are given.**
- **Forces:** 「圧力分布から…流体力 (F_x, F_y, F_z) を求めている」: the forces were computed **from the surface pressure distribution**. Viscous shear stress is not mentioned. F_y ≈ 0 was confirmed. C_D comes from F_x and C_M from F_z.
- **Run matrix:** target Sp* from 0.1 to 2.0 in steps of 0.1, made in two ways: fix V_x = 3 or 5 m/s and set ω_y; or fix ω_y = 100 or 300 rad/s and set V_x. Table 2 lists a subset (reproduced in §5).
- **Fit:** least squares on polynomials f_k(Sp), with error variance σ_e = (1/N) Σ|C_Di − f_k(Sp_i)|² and AIC = N ln σ_e + 2k, minimised over coefficients and degree k (eqs. 4–7).
- **Spin decay / aerodynamic torque:** **not modelled.** Eq. (1) is written for a constant spin ω. No torque coefficient is computed.
- **Ball geometry:** smooth sphere, r = 0.02 m. No seam, logo or roughness is mentioned.

## 4. Equations

### 4.1 As printed in the paper (theory; restated from their ref. 5, Okada et al. 2008)

Eq. (1), copied as printed:

  p̈(t) = −g + C_D (ρ/m) r² S_b ‖ṗ(t)‖ ṗ(t) + C_M (ρ/m) V_b ω × ṗ(t)

with g := [0 0 g]ᵀ, S_b := ½πr², V_b := (4/3)πr³, m the ball mass, ρ the air density, and r the ball radius.

**Caution, our reading:** as printed, the drag term has a "+" sign and a factor r²S_b with units of m⁴, so it is dimensionally wrong. The intended form is presumably −C_D (ρ/m) S_b ‖ṗ‖ ṗ, possibly with the sign absorbed into C_D. That would still be half the usual ½ρA convention unless S_b already carries the ½. The paper itself has S_b = ½πr². **Do not copy eq. (1) literally.** The C_D values in Table 3 are only meaningful under whatever normalisation PHOENICS post-processing used, and the paper does not state it.

Eq. (2): Re := 2r‖ṗ‖/ν, with ν = μ/ρ.

Eq. (3): Sp := r ‖ω − (ωᵀṗ/‖ṗ‖)(ṗ/‖ṗ‖)‖ / ‖ṗ‖ = r ‖ω × ṗ‖ / ‖ṗ‖². This is the spin component **perpendicular to the velocity**, made non-dimensional. It equals the usual S = rω/v when ω ⊥ v. This is the right definition for a 3D model with off-axis spin.

Eqs. (8)–(9), the proposed trajectory-fit identification: minimise Σ_k (1/n_k) Σ_i ‖p_i(a, x₀⁽ᵏ⁾, ω⁽ᵏ⁾) − p_i⁽ᵏ⁾‖² over the coefficient vector a = (a_D2, a_D1, a_D0, a_M4, …, a_M0). With eq. (9), when spin is not measured, the per-trial spins W = {ω⁽ᵏ⁾} are also free parameters.

### 4.2 Converting C_M to a conventional C_L (**derived here, not in the paper**)

Their Magnus term is F_M = C_M ρ V_b (ω × v), a "per unit spin" coefficient. The conventional lift is F_L = ½ρ(πr²) C_L v². For ω ⊥ v:

  C_L = C_M V_b ω v / (½ πr² v²) = (8/3) C_M (rω/v) = **(8/3) · Sp · C_M(Sp)**

So a C_M that **falls** with Sp can still mean a C_L that **rises** with Sp, only more slowly. Any comparison of this paper with Steyn (C_L = 0.195 S) or with Lindsey must use this conversion, otherwise the trend is misread.

## 5. Data table

| Quantity | Value | Label / grade |
|---|---|---|
| Ball radius used | r = 0.02 m | stated |
| Rally speed range considered | ‖ṗ‖ ∈ [0.5, 10] m/s | stated |
| Kinematic viscosity used | ν = 1.512 × 10⁻⁵ m²/s (1 atm, 20 °C) | stated |
| Re range claimed | [1.323, 26.46] × 10³ | stated (from the speed range above) |
| CFD domain | 0.5 × 0.25 × 0.25 m; ball at (0.125, 0.125, 0.125) m | stated |
| Cell spacings | 0.005 or 0.001 per axis, 8 combinations (Table 1) | stated |
| Sp sweep | 0.1 < Sp < 2.0, step 0.1 | stated |
| Table 2, V_x = 3 m/s | Sp* 0.1/0.5/1.0/1.5/2.0 → ω_y 15/75/150/225/300 rad/s | stated |
| Table 2, V_x = 5 m/s | ω_y 25/125/250/375/500 rad/s | stated |
| Table 2, ω_y = 100 rad/s | V_x 20/4/2/1.33/1 m/s | stated |
| Table 2, ω_y = 300 rad/s | V_x 60/12/6/4/3 m/s | stated |
| Pressure-field example (Fig. 5) | V_x = 3 m/s, ω_y = 62.8 rad/s | stated |
| Number of CFD points fitted | N = 56 | stated |
| C_D(Sp) fit (Table 3) | C_D = −0.0747 Sp² + 0.3591 Sp + 0.3682 | stated; CFD, unvalidated |
| C_M(Sp) fit (Table 3) | C_M = 0.2313 Sp⁴ − 1.2055 Sp³ + 2.2813 Sp² − 1.9501 Sp + 0.8254 | stated; CFD, unvalidated |
| C_D range in Fig. 6 | about 0.4 at Sp ≈ 0.1, rising to about 0.75–0.9 at Sp = 2 | **read from figure by eye**, approximate |
| C_M scatter at Sp = 0.1 (Fig. 7) | V_x = 5 series about 0.9; V_x = 3 series about 0.4 | **read from figure by eye**, approximate |
| Fit evaluated: C_D at Sp = 0.1 / 0.5 / 1.0 / 2.0 | 0.403 / 0.529 / 0.653 / 0.788 | **derived here** from Table 3 |
| Fit evaluated: C_M at Sp = 0.1 / 0.5 / 1.0 / 2.0 | 0.652 / 0.284 / 0.182 / 0.107 | **derived here** from Table 3 |
| Equivalent C_L = (8/3)·Sp·C_M at Sp = 0.1 / 0.25 / 0.5 / 1.0 / 1.5 / 2.0 | 0.174 / 0.308 / 0.379 / 0.486 / 0.542 / 0.572 | **derived here** (§4.2); inherits every limitation of the CFD |
| Re actually spanned by the run matrix | V_x from 1 to 60 m/s with r = 0.02 m and their ν gives about 2.6 × 10³ to 1.6 × 10⁵ | **derived here**. This is well beyond the 26.46 × 10³ upper end used to justify Re independence, yet the collapse is still claimed. |
| Tunnel blockage (ball frontal area / tunnel section) | about 2 % | **derived here** |
| Validation data | **none** | stated (future work) |
| Spin-decay / torque coefficient | **none** | not modelled |

## 6. Applicability to POLLEN

**Transfers (qualitatively):**
- **The coefficient form.** Writing C_D(S) and C_L(S) (or C_M(S)) as low-order functions of the perpendicular spin parameter S = r‖ω×v‖/‖v‖², with the order picked by an information criterion rather than by eye, is a sound, cheap structure for POLLEN. It is also more general than the project's current constant C_D plus linear-capped C_L.
- **The structural warning that C_D may depend on spin.** Here CFD (unvalidated) shows C_D roughly doubling between Sp ≈ 0.1 and 2. Whether or not those magnitudes are right, a POLLEN model that holds C_D fixed while sweeping spin may understate the cost of backspin: more drag means less horizontal reach. That direction matters for the unfavourable-side entry question.
- **C_L rises sublinearly with S** after the §4.2 conversion. That is qualitatively consistent with the "do not assume more RPM gives proportionally more Magnus force" warning in HANDOFF §5.
- **The identification method (eqs. 8–9)** transfers directly. Fit a few C_D/C_L polynomial coefficients to filmed POLLEN trajectories. Measured spin per shot (eq. 8) is best. Per-shot spin as a nuisance parameter (eq. 9) is the fallback when spin cannot be read, though it is less well conditioned because spin and C_L trade off.
- **The S regime overlaps.** A rolling-hood launch ideally gives S ≈ 1 at exit (Brettle, unreviewed technical source), and S grows as the ball slows near the apex if spin is retained. Their sweep (0.1–2) brackets that. The Re regimes also overlap: POLLEN (2r = 0.071 m, ν ≈ 1.5 × 10⁻⁵) at 3–9 m/s gives Re ≈ 1.4–4.3 × 10⁴ (**derived here**), the same order as their claimed table-tennis range.

**Does not transfer:**
- **Every coefficient value.** These are for a **smooth, closed, 40 mm table-tennis ball** (radius 0.02 m stated; the mass is not stated in this paper), from unvalidated pressure-only CFD. POLLEN is a 71 mm, ~25 g, **perforated** polyethylene shell that is not perfectly spherical. Flow through the holes, internal circulation and hole orientation (Rossmann & Rau's Wiffle results) are absent from a smooth-sphere CFD. **Do not put 0.3682, 0.3591, −0.0747 or the C_M quartic into POLLEN parameters.**
- **The Re-independence argument.** It rests on a smooth-sphere textbook curve. Perforations and roughness move or remove the drag crisis, and table-tennis experiments (sakai2016 in this repo) report non-monotonic lift ("lift crisis") in parts of this space. The unexplained C_M scatter at Sp = 0.1 sits in exactly the low-spin region where such effects are reported. Do not assume POLLEN is Re-independent.
- **Spin decay.** The paper holds ω constant. It offers nothing for dω/dt, which HANDOFF §4 says the model must carry for high-arc shots where spin has time to decay.
- **Quartic extrapolation.** The C_M quartic has no physical meaning outside 0.1 ≤ Sp ≤ 2. At Sp → 0 it returns C_M = 0.8254, which is harmless only because C_L = (8/3)·Sp·C_M → 0. Never extrapolate it.

## 7. What it means for the PM-001 model and test plan

1. **Model form (src/flight.py is owned by another workflow; recommendation only):** add an optional C_D(S) = d0 + d1·S (+ d2·S²) branch alongside the constant C_D, and keep C_L(S) monotone-saturating rather than linear-capped. Then sweep d1 ≥ 0 as a sensitivity. **Use no Isomura numbers as POLLEN defaults.** At most, cite the paper as the reason d1 > 0 is plausible (unreviewed, CFD-only).
2. **Use the S definition of eq. (3)** (the perpendicular component), not |ω|r/|v|. It already handles a tilted spin axis from an imperfect hood contact.
3. **Identification plan:** adopt the eq. (8)/(9) least-squares trajectory fit with an AIC (or BIC) choice of polynomial order for POLLEN. Use matched nonspinning and backspinning shots at the same exit speed and angle, and side plus overhead cameras. Spin should be read from a fiducial, as their 900 fps pattern-tracking method does. Fit C_D(S), C_L(S) **and** an exponential spin-decay constant together, because eq. (1) alone cannot see decay. Report coefficient covariances, because C_L and spin trade off.
4. **Is a POLLEN CFD study worth doing instead of measuring? No, not first.** This paper is a well-organised CFD campaign on the *easiest* possible case (smooth closed sphere, fixed spin axis). Even so, it (a) left the turbulence model, spin boundary condition and grid-convergence evidence unstated, (b) appears to use pressure-only forces, (c) shows unexplained scatter at low Sp, and (d) never validated against flight. A credible POLLEN CFD would need all of that plus perforations, internal flow, hole-orientation averaging, unsteady (DES/LES-class) wake resolution and a torque output, and then a validation flight test anyway. A one-day camera test with a fiducial ball gives the trajectory-level C_D, C_L and decay directly at the real Re, S and hole pattern. **Measure first. Treat CFD at most as a later, optional explanation tool,** for example to study hole-orientation sensitivity once measured coefficients exist to validate against.

## 8. Caveats

- The translation from Japanese is the research agent's own. Key sentences quoted in Japanese above can be checked.
- Fig. 6 and Fig. 7 values were read by eye from 4-page proceedings figures. Only the Table 3 coefficients are exact.
- Eq. (1) as printed appears to contain typos (drag sign, r²S_b). The normalisation behind the Table 3 C_D values is therefore uncertain even for table-tennis use.
- The paper does not say whether viscous shear is included in the force integration. The text says forces were obtained from the pressure distribution. If shear was omitted, C_D is biased low by an amount this paper does not let us estimate.
- No follow-up validation paper by these authors was found. That does not prove none exists (Nagoya repository record 12565 was unavailable, HTTP 503).
