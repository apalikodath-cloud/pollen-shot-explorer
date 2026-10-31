# Creer (2023): Computational Fluid Dynamics Analysis of Pickleballs

source_id: `creer2023` (source #8 in RESEARCH_PAPERS.md). No companion source was used. Every number below is from the thesis PDF (84 pp., full text) unless a row says **derived here** or **read from figure**.
Read: 2026-10-30, research agent for PM-001.

## 1. Citation, access, review status

| Field | Value |
|---|---|
| Citation | Isaac Creer, *Computational Fluid Dynamics Analysis of Pickleballs*, BSc senior thesis, Department of Physics, Brigham Young University–Idaho, December 2023. Advisor Kevin Kelley. |
| Dates | Title page "December 2023". PDF created 13 Dec 2023 (LaTeX/pdfTeX). |
| Review status | **Undergraduate senior thesis, not peer-reviewed.** The approval page says it "has been reviewed by the research committee, senior thesis coordinator, and department chair and has been found to be satisfactory". That is departmental approval, not journal review. Graded: **unreviewed technical source**. Its numerical outputs are **self-declared invalid** (see §2). |
| Method type | Steady RANS CFD (OpenFOAM simpleFoam, k-ε) of fixed, **non-spinning** 0-, 26- and 40-hole balls. Plus an unfinished Euler-method flight/spin script. **No experiment.** |
| Access | **Full text read** (pdftotext; Chapter 4 figures rendered and inspected; Appendix A code read). |

URLs tried:
- https://brightspotcdn.byui.edu/f5/ef/bfdce4934c0c97c93cee95c8d33e/isaac-creerf23.pdf (200, application/pdf, 725 314 bytes, 84 pp.; saved to `%TEMP%\pm001_creer_H7SB\creer.pdf`, not executed)

## 2. What the thesis reports

Abstract (verbatim): "This paper describes the first attempt at a model to show a pickleball's flight characteristics. The model used OpenFOAM's SIMPLE foam solver to calculate the drag coefficient. OpenFOAM could not calculate the drag coefficient accurately due to errors in the mesh generation of this model. This model opens the door to creating a better model to predict a pickleball's flight characteristics. […]"

Findings, graded:
1. **No valid drag coefficient was obtained** for any ball. "There should never be a negative part of the drag coefficient." The pressure-drag component came out negative for all three balls. Total C_D "tends towards zero, which is wrong" as speed rises. *Grade: author's own failure statement (unreviewed). This is the only robust result.*
2. **The author attributes the error to mesh generation**, specifically "the scaling issue". A rescaled-mesh rerun "ran successfully and gave more reliable results" but "crashed after 276 time steps". The author suspected a memory leak. No numbers from the rerun are reported. *Grade: unreviewed; unverified.*
3. **The 26- and 40-hole balls gave "roughly the same" total drag coefficients** (Fig. 4.7). Since the author calls the whole output invalid, **this is not evidence** that hole count does not matter. *Grade: invalid CFD output; do not use.*
4. **Spin and flight path were not done**: "Both cannot be done due to time and inaccuracy of the drag coefficient calculation." *Grade: stated.*
5. **The 26-hole mesh had unevenly spaced holes** (Fig. 4.3), which the author calls "the first sign of a problem with the mesh generation". *Grade: stated observation.*
6. **Future work proposed:** a dynamic mesh, wind-tunnel experimental data, checks for OpenFOAM process errors, then spin and flight-path prediction. *Grade: stated.*
7. **Physics framing (Ch. 2):** the thesis drops conventional lift as negligible "due to the design of a pickleball" and keeps drag plus a Magnus force F_M = S₀ω u, with S₀ described as "the average drag of the ball over its area". *Grade: theory, loosely defined. No coefficient or source data back it. Not usable.*

## 3. Method (as stated in text and Appendix A)

- **Solver:** OpenFOAM (the thesis mentions openfoam2304 and openfoam2306), `simpleFoam` (steady, incompressible SIMPLE). Turbulence: RAS `kEpsilon` with wall functions (`epsilonWallFunction`, `kqRWallFunction`, `nutkWallFunction`). ν = 1.5e-05. 400 iterations per case. Each case took about 30 s (0 holes), 50 s (26 holes) and 65 s (40 holes) on the author's computer. "Converged at around 400 time steps", with no residual levels reported.
- **Inflow conditions:** "from 3 m/s up to 30 m/s", 1 atm, 23 °C, 50 % humidity (the solver is incompressible, so the last two have no effect). "I ran 30 tests" for the 0-hole ball.
- **Boundary conditions (Appendix A.1.1):** inlet fixed velocity `Uinlet (5 0 0)`, outlet `totalPressure` p0 = 0, ball `noSlip`. k_inlet = 1.5 (comment: I = 0.1) and ε_inlet = 0.03 (comment: L = 10). **No rotating-wall or MRF condition exists anywhere** (a text search for rotatingWall, MRF, dynamicMesh or pimple found nothing), so **no spinning case was ever simulated.**
- **Geometry and mesh:** balls drawn in Onshape and exported to STL, then `surfaceFeatureExtract`, `blockMesh` and `snappyHexMesh`. Original background box: x −7 to 3, y −7 to 2, z 0 to 7, with 25 × 20 × 10 cells, surface refinement level (3 3), `locationInMesh (1 1 1)`. Updated box (Appendix A.4): ±0.2 in x, y and z, with 25 × 25 × 10 cells, the bottom face a `wall` ("ground"), the side and top faces `symmetry`, surface level (3 3), refinement-box level 2, and `locationInMesh (0 0 0)`. `addLayers off` in both, so **no boundary-layer prism cells.**
- **Force coefficients:** OpenFOAM `forceCoeffs`, with `rhoInf 100000`, `liftDir (0 1 0)`, `dragDir (1 0 0)`, and `lRef 1`, `Aref 1` in the appendix dictionaries. `magUInf` is 10.0 in the original controlDict and 5.0 in the updated one. The text calls rhoInf "the pressure" and magUInf "the airspeed".
- **Flight script (Appendix A.3, unfinished):** Euler integration with dt = 0.01 s, v0 = 20 m/s at 45°, g = 9.8, ρ coded as 1.00 (commented "kg/m^2"), m = 0.02651 kg ("26.51g"), d = 0.0730 m. Drag is coded as −C·A·ρ·v·|v|/m (no ½). The Magnus term is coded as (0.25/|ω_y|)·ω_y·v, a fixed 0.25 factor times velocity with the sign of spin, not a lift-coefficient model. The spin assignment includes 2000 and 2π/60 (rpm to rad/s), but the expression is garbled in the extracted text. C is looked up by speed from the invalid CFD table.

## 4. Equations

### 4.1 As stated (theory, textbook)
- Drag: F_D = ½ ρ C_D A u² (eq. 2.11); C_D = 2F_D/(ρAu²) (eq. 2.12); C_D = c_friction + c_pressure (eq. 2.13). The pressure and friction parts are surface integrals of (p − p₀)(n̂·î) and τ_w(t̂·î) (eqs. 2.14–2.15, cited to Hoerner 1965; the extraction garbled the symbols).
- Magnus: F_M = S₀ ω u (eq. 2.7, cited to Giordano & Nakanishi). The thesis gives no value or measurement of S₀.
- Re = ρDu/η (eq. 2.10; symbols garbled in the extraction).

### 4.2 Diagnostic reading of the invalid output (**derived here; hypothesis, not the author's**)
Total C_D read by eye from Fig. 4.7 for the 0-hole ball: about 8 at 3 m/s, about 4.5 at 4 m/s, about 2.9 at 5 m/s, about 0.75 at 10 m/s. The product C_D·U² is then about 72, 72, 72 and 75 (m²/s²). In other words, **C_D ∝ 1/U²: the computed force did not change with the nominal speed.** That pattern is what you get if the inlet velocity stayed fixed (the base case's `Uinlet (5 0 0)`) while only the normalising speed changed between runs. The thesis does not describe how the speed was varied, so this is a hypothesis. Separately, `Aref 1` (m²) against a ball frontal area of order 4 × 10⁻³ m² (π·0.0365², **derived here**), together with the unresolved STL-unit "scaling issue", means even the absolute level is undefined. Either way, **no number in Ch. 4 has physical meaning.**

## 5. Data table

| Quantity | Value | Label / grade |
|---|---|---|
| Balls simulated | 0, 26 and 40 holes; non-spinning | stated |
| Speed range | 3–30 m/s | stated |
| Iterations per case | 400 | stated |
| Run time per case | ~30 s / ~50 s / ~65 s (0 / 26 / 40 holes) | stated |
| ν | 1.5 × 10⁻⁵ m²/s | stated (transportProperties) |
| Turbulence model | RAS k-ε with wall functions | stated (appendix) |
| Inlet U (base case) | (5 0 0) m/s | stated (appendix) |
| forceCoeffs Aref, lRef | 1, 1 | stated (appendix) |
| rhoInf | 100000 | stated (appendix) |
| magUInf | 10.0 (original), 5.0 (updated) | stated (appendix) |
| Rerun after mesh rescale | crashed after 276 time steps | stated |
| Sample forceCoeffs printout (Table 3.1) | e.g. "Cd: 0.160193" total | stated, but it is **an example printout with no case identified**; not a result |
| 0-hole total C_D vs speed (Fig. 4.2/4.7) | ~8 at 3 m/s, decaying toward ~0 by 30 m/s | **read from figure**; author-declared invalid |
| 40-hole friction / pressure C_D at 3 m/s (Fig. 4.6) | about +57 / about −48 | **read from figure**; author-declared invalid |
| C_D·U² for the 0-hole ball, 3–10 m/s | ~72–75 m²/s² (roughly constant) | **derived here** (§4.2) |
| Ball mass, diameter in flight script | 0.02651 kg, 0.0730 m | stated (appendix code); not a measured POLLEN property |
| Any valid C_D, C_L, Magnus or spin-decay value | **none** | stated |

## 6. Applicability to POLLEN

**Transfers (qualitatively):**
- **A cautionary case study.** Perforated-ball CFD is easy to set up and easy to get badly wrong. The listed failure modes are exactly the ones a POLLEN CFD would face: STL units and scaling, `locationInMesh` choice, snapping of many small holes, no near-wall layers, steady RANS on a bluff body, wrong reference area or velocity, and a domain too small for the wake (the updated box puts the boundaries 0.2 m from the centre, about 2.7 ball diameters, **derived here**).
- **The decomposition idea** (pressure plus friction drag, via `forceCoeffs`) is standard and fine. It needs the reference area set to πr² of the real ball, magUInf set equal to the real inlet speed, and a check that the pressure component is positive for a bluff body.
- **Hole count and geometry are real inputs** for pickleballs (the thesis quotes the USA Pickleball rulebook range of 26 to 40 holes, and calls 26-hole balls typical indoor and 40-hole balls typical outdoor). POLLEN's own hole pattern must be measured from the STEP model or real balls. This thesis gives no basis for saying it does or does not matter.

**Does not transfer:**
- **Every number in Chapter 4.** The author says they are invalid, and §4.2 shows they do not even scale like a force.
- **The "lift negligible" assumption.** It is asserted, not tested. It conflicts with the project's whole premise (a spin-driven Magnus force). It also conflicts with the spin-free side forces reported for perforated Wiffle balls (Rossmann & Rau, peer-reviewed; see that note).
- **The flight script's Magnus term** (fixed 0.25 factor) and its ρ = 1.00 are placeholders and must not be reused.
- **Ball properties** (26.51 g, 73 mm) are for a pickleball in the script, not POLLEN.

## 7. What it means for the PM-001 model and test plan

1. **Cite Creer 2023 for nothing quantitative.** Use it only as evidence that a student-level perforated-ball CFD did not produce a usable C_D, let alone C_L(S) or spin decay.
2. **CFD vs measurement for POLLEN: measure.** A spin-resolved POLLEN CFD would need everything Creer lacked: correct scaling and reference values, layered near-wall mesh, the internal cavity connected through all holes, rotating-wall boundary conditions or a rotating mesh, unsteady scale-resolving turbulence, several hole orientations, and a torque output for spin decay. It would then still need a flight test to validate it. The flight test alone (side plus overhead high-speed video, fiducial ball, matched spin/no-spin shots, trajectory least-squares fit as in isomura2016 eqs. 8–9) gives the trajectory-level C_D, C_L(S) and decay rate the PM-001 model actually uses, at the true Re, S and hole pattern.
3. **If CFD is attempted later** (optional; for example to explain a measured hole-orientation scatter), set these acceptance checks before believing any output:
   (a) A smooth closed sphere at the same Re must reproduce textbook smooth-sphere C_D within a stated tolerance.
   (b) C_D·U² must not be constant across the speed sweep.
   (c) Pressure drag must be positive.
   (d) A grid-convergence study must be reported (at least 3 meshes).
   (e) The domain-size and blockage sensitivity must be reported.
   (f) Results must be compared with the measured POLLEN nonspinning C_D before any spinning run is trusted.
4. **Model consequence:** none for the coefficient values. The project's C_D and C_L placeholders stay placeholders until POLLEN is measured.

## 8. Caveats

- Text was extracted with pdftotext. Equation symbols in Ch. 2 and some appendix code are garbled (Greek letters, operators). Only clearly legible values are reported.
- Figure values were read by eye from small plots and are approximate. They are reported only to support the §4.2 diagnosis, never as data.
- §4.2 is this note's own hypothesis about the failure. The thesis attributes the error to mesh scaling and does not discuss inlet speed or Aref.
- This is the December 2023 version. The thesis promises "an updated case with the successful run", but no updated version was searched for or found in this session.
