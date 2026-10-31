# Mehta (1985): Aerodynamics of sports balls

source_id: `mehta1985` (source #14 in RESEARCH_PAPERS.md). Companion context used here: `chadwick2003thesis` (open Sheffield PhD thesis that describes what Mehta 1985 did) and `cross_notes` (Rod Cross, "Sports ball aerodynamics", unreviewed teaching notes). Neither companion is the Mehta paper. Every row below says which source it came from.
Read: 2026-10-30, research agent for PM-001.

## 1. Citation, access, review status

| Field | Value |
|---|---|
| Citation | R. D. Mehta, "Aerodynamics of sports balls", *Annual Review of Fluid Mechanics* **17**, 151–189 (1985). DOI 10.1146/annurev.fl.17.010185.001055 |
| Index record | NASA NTRS 19850049027 (AIAA accession 85A31178). NTRS files it as "Conference Proceedings", affiliation NASA Ames Research Center (Aerodynamics Research Branch) and Stanford University. `disseminated: METADATA_ONLY`, `downloadsAvailable: false`, `technicalReviewType: NONE` (that NTRS field refers to NASA internal review, not to the journal). |
| Review status | **Peer-reviewed review article** (Annual Reviews journal). It is a review of earlier wind-tunnel and flight work on cricket balls, baseballs and golf balls, not a new primary data set. Crossref: 236 citations; Semantic Scholar: 304. |
| Method type | Review. Per the NTRS abstract: smoke-tracer wind-tunnel visualisation and pressure-tap measurements (summarised, partly the author's own cricket-ball work). |
| Access | **Abstract only.** Publisher full text returned HTTP 403 (three URLs). Unpaywall: `is_oa=false`, `oa_status=closed`. Semantic Scholar: `openAccessPdf.status=CLOSED`. NTRS has metadata only. Two web searches found no repository or author copy. |
| Consequence | No figure, table or equation of the paper was seen. **Abstract only: no numbers from Mehta 1985 are reported or used here.** The indexer abstract contains two lift-coefficient maxima (golf, baseball); they are quoted verbatim in §2 only as evidence of what was read. They are not entered in §5, and must not be used as POLLEN or design values. |

URLs tried:
- https://ntrs.nasa.gov/api/citations/19850049027 (JSON metadata + abstract; no download)
- https://ntrs.nasa.gov/citations/19850049027 (search hit; same record)
- https://api.crossref.org/works/10.1146/annurev.fl.17.010185.001055 (metadata, no abstract, 0 deposited references)
- https://api.unpaywall.org/v2/10.1146/annurev.fl.17.010185.001055 (closed)
- https://api.semanticscholar.org/graph/v1/paper/DOI:10.1146/annurev.fl.17.010185.001055 (closed)
- https://www.annualreviews.org/doi/pdf/10.1146/annurev.fl.17.010185.001055 (403)
- https://www.annualreviews.org/doi/10.1146/annurev.fl.17.010185.001055 (403)
- https://www.annualreviews.org/content/journals/10.1146/annurev.fl.17.010185.001055 (403)
- https://www.physics.usyd.edu.au/~cross/TRAJECTORIES/Sports%20Balls.pdf (open; **Rod Cross notes, not Mehta**; used as `cross_notes`)
- https://etheses.whiterose.ac.uk/12839/1/397496.pdf (open; Chadwick 2003 thesis, OCR, 331 pp.; used as `chadwick2003thesis` for its description of Mehta 1985)
- Web searches (2): "Mehta 1985 Aerodynamics of sports balls … pdf"; "Ann. Rev. Fluid Mech. 1985. 17 Mehta sports balls". Hits were citing papers (arXiv 1710.02784, Clanet 2015 review, EPJ Conf 2018), not the paper.

**Action for the lead:** anyone with Annual Reviews access can fill §5 "TBD" rows (Cl vs spin parameter curves, Cd vs Re curves, critical-Re values per ball) from the PDF. Mehta's later open or semi-open reviews (Mehta & Pallis 2001; Mehta 2008 CISM chapter) were not retrieved and are not this source.

## 2. What the paper reports (NTRS/AIAA indexer abstract, verbatim)

> "Research data on the aerodynamic behavior of baseballs and cricket and golf balls are summarized. Cricket balls and baseballs are roughly the same size and mass but have different stitch patterns. Both are thrown to follow paths that avoid a batter's swing, paths that can curve if aerodynamic forces on the balls' surfaces are asymmetric. Smoke tracer wind tunnel tests and pressure taps have revealed that the unbalanced side forces are induced by tripping the boundary layer on the seam side and producing turbulence. More particularly, the greater pressures are perpendicular to the seam plane and only appear when the balls travel at velocities high enough so that the roughness length matches the seam heigh. The side forces, once tripped, will increase with spin velocity up to a cut-off point. The enhanced lift coefficient is produced by the Magnus effect. The more complex stitching on a baseball permits greater variations in the flight path curve and, in the case of a knuckleball, the unsteady flow effects. For golf balls, the dimples trip the boundary layer and the high spin rate produces a lift coefficient maximum of 0.5, compared to a baseball's maximum of 0.3. Thus, a golf ball travels far enough for gravitational forces to become important."

This is an indexer's abstract (AIAA/NTRS), not the author's. Its wording is loose (e.g. "seam heigh", "greater pressures are perpendicular to the seam plane").

Findings visible in the abstract (graded):
1. **Side force on seamed balls comes from asymmetric boundary-layer transition.** A seam trips the boundary layer on one side; that side separates later; the wake is deflected and a side force results. Seen with smoke tracers and pressure taps. *Peer-reviewed finding (review of experiments).*
2. **The tripping only works above a speed threshold** where the surface feature is large enough relative to the boundary layer ("roughness length matches the seam height"). *Peer-reviewed finding, qualitative.*
3. **Side force grows with spin "up to a cut-off point".** That is, the spin effect saturates or stops growing. The abstract gives no shape. *Peer-reviewed finding, qualitative.*
4. **Lift from spin is the Magnus effect, and its maximum differs by surface (dimpled golf vs stitched baseball).** Surface treatment changes the attainable lift. *Peer-reviewed finding, qualitative (numbers withheld, see §1).*
5. **Unsteady, orientation-dependent forces on low-spin seamed balls (knuckleball).** *Peer-reviewed finding, qualitative.*

## 3. What the paper did (secondary description only)

From `chadwick2003thesis` (Sheffield PhD, open; its literature review describes Mehta 1985). **Secondary, not checked against the paper:**
- Mehta (1985) used the pressure-coefficient (Cp) distribution around the equator of a cricket ball, with the seam angled to the flow, to show why the ball swings: at low speed both sides had equal pressure; as Re rose, the seam side pressure dropped and the ball deflected toward the seam (thesis §2.7.1, p. 46).
- Mehta (1985) used smoke injected into the separated region behind a cricket ball to confirm the Cp result: laminar separation on the smooth side, turbulent separation on the seam side, deflected wake (thesis §2.7.2, p. 47).
- Chadwick's own trajectory model "is similar to that used by Mehta (1985)" (thesis §4, p. 79), i.e. Mehta 1985 includes a drag-plus-lift trajectory integration.
- Chadwick's literature review (attributed there to Mehta & Pallis 2001, **not** to Mehta 1985) gives the four-stage Cd-vs-Re picture for a sphere (subcritical laminar separation; critical regime with separation bubble and minimum Cd; supercritical; transcritical where Cd depends on roughness only), and describes **reverse (negative) Magnus**: the advancing side goes critical first, its separation moves rearward, and the side force switches sign "over a very limited Reynolds number range" (thesis §2.3.5, pp. 15–17). *Theory / review, secondary.*

## 4. Equations

The paper's own equations were not visible. The standard definitions below are the ones the companions state; they are the same as PM-001 HANDOFF §4.

| # | Equation | Symbols / units | Source |
|---|---|---|---|
| E1 | F_D = ½ ρ C_D A v² | ρ air density [kg/m³], A = πR² [m²], v speed relative to air [m/s] | cross_notes eq. (1) |
| E2 | F_L = ½ ρ C_L A v², acting perpendicular to v | "lift" includes any transverse force (Magnus, seam, one-sided roughness) | cross_notes eq. (2) |
| E3 | Re = ρ D v / μ = D v / ν | D diameter [m]; ν kinematic viscosity [m²/s] | cross_notes p. 2 |
| E4 | S = R ω / v (spin parameter) | ω [rad/s]; dimensionless | standard; HANDOFF §4 |

### 4.1 Reynolds-number regime for POLLEN (**derived here, not from Mehta**)

Inputs: D = 0.071 m (POLLEN, from HANDOFF), ν = 1.5×10⁻⁵ m²/s (PM-001 default, `src/flight.py`, assumed air near 20 °C) and ν = 1.6×10⁻⁵ m²/s (assumed warmer gym air, sensitivity only).

| v [m/s] | Re (ν = 1.5e-5) | Re (ν = 1.6e-5) |
|---|---|---|
| 2 | 9.5×10³ | 8.9×10³ |
| 3 | 1.4×10⁴ | 1.3×10⁴ |
| 5 | 2.4×10⁴ | 2.2×10⁴ |
| 7 | 3.3×10⁴ | 3.1×10⁴ |
| 10 | 4.7×10⁴ | 4.4×10⁴ |

So Re ≈ 4.7×10³ · v [s/m], **≈ 1×10⁴ to 5×10⁴** over the shot (derived; matches the cross2017 and ito2025 notes).

Spin needed for a given S (derived, R = 0.0355 m):

| v [m/s] | S = 0.5 | S = 1 | S = 2 |
|---|---|---|---|
| 2 | 28 rad/s (269 rpm) | 56 rad/s (538 rpm) | 113 rad/s (1076 rpm) |
| 5 | 70 rad/s (672 rpm) | 141 rad/s (1345 rpm) | 282 rad/s (2690 rpm) |
| 10 | 141 rad/s (1345 rpm) | 282 rad/s (2690 rpm) | 563 rad/s (5380 rpm) |

A fixed ω gives a **rising S as the ball slows toward apex** (S ∝ 1/v). With the ideal hood result S_exit ≈ 1 (HANDOFF §4C), S near apex is S_exit × (v_launch / v_apex), if spin decay is small (derived; e.g. 4–10 m/s launch and 2 m/s at apex gives 2–5×).

### 4.2 Where the drag crisis sits relative to POLLEN (**derived, using thresholds from an unreviewed source**)

`cross_notes` (p. 2, unreviewed) states the boundary layer on a smooth sphere becomes turbulent for Re > 3×10⁵, and on rough or dimpled surfaces it can become turbulent for Re > 4×10⁴. For a 71 mm ball those Re values correspond to about **63 m/s** (smooth) and **8.5 m/s** (rough or dimpled) (derived, ν = 1.5e-5).

Reading: a smooth 71 mm ball at 2–10 m/s is far subcritical. A rough or tripped surface could approach a transitional regime only at the fast end of the shot (launch, not apex). Whether POLLEN's holes act as "trips" is unknown. No source in this note measured that.

## 5. Data table

| Quantity | Value | Conditions | Where | source_id |
|---|---|---|---|---|
| Cause of seam side force | asymmetric boundary-layer tripping, seen with smoke and pressure taps | cricket ball, baseball; wind tunnel | abstract | mehta1985 |
| Speed threshold for seam effect | exists ("only appear when … velocities high enough") | as above | abstract | mehta1985 |
| Side force vs spin | increases "up to a cut-off point" (saturation; shape not given) | seamed balls | abstract | mehta1985 |
| Max C_L golf vs baseball | **withheld (abstract only)**; golf > baseball | dimpled vs stitched | abstract | mehta1985 |
| C_L(S), C_D(Re) curves, critical Re per ball, spin rates | TBD (paywalled) | n/a | body, figures | mehta1985 |
| Method: equatorial Cp + smoke visualisation on cricket ball | described | seam angled to flow | thesis §2.7, pp. 46–47 | chadwick2003thesis (secondary) |
| Reverse Magnus mechanism | advancing side goes critical first; force reverses over a narrow Re band | sphere, literature | thesis §2.3.5, pp. 16–17 | chadwick2003thesis (secondary, attributed there to Mehta & Pallis 2001) |
| Smooth-sphere transition | Re > 3×10⁵ | literature summary | p. 2 | cross_notes (unreviewed) |
| Rough/dimpled transition | can occur for Re > 4×10⁴ | literature summary | p. 2 | cross_notes (unreviewed) |
| POLLEN Re band | ≈ 9×10³ to 4.7×10⁴ | 2–10 m/s, D = 71 mm, ν = 1.5–1.6e-5 | §4.1 | derived |
| Speed at Re = 4×10⁴ / 3×10⁵ | 8.5 m/s / 63 m/s | D = 71 mm, ν = 1.5e-5 | §4.2 | derived |

## 6. Applicability to POLLEN

**Transfers (qualitatively):**
- **Transverse force = asymmetric separation.** Magnus lift, seam swing and one-sided roughness are the same mechanism: one side separates later, the wake is deflected. A perforated shell has a non-uniform surface (holes, flat lands, possible mould seam). It can therefore generate orientation-dependent transverse force even at low spin, and the effect can change with orientation as it spins. *Peer-reviewed finding (mechanism) → POLLEN by analogy (theory).*
- **The effect of spin saturates.** "Increase with spin velocity up to a cut-off point" supports the PM-001 rule: do not assume C_L ∝ S without limit. HANDOFF §5 already forbids "more backspin always improves entry". *Peer-reviewed finding, qualitative.*
- **Surface treatment changes attainable lift.** Golf dimples vs baseball stitches change the maximum C_L. POLLEN's perforation pattern will set its own C_L(S); it has to be measured. *Peer-reviewed finding, qualitative.*
- **Reverse Magnus is tied to transition.** The reverse-Magnus band sits where one side goes turbulent and the other stays laminar. *Theory (secondary).* For a smooth 71 mm ball at Re ≤ 5×10⁴ that band is not expected; for a tripped or perforated surface it cannot be ruled out near the launch speed (§4.2). Ito 2025 (separate note) reports C_L dips at Re 4–5×10⁴ for a 40 mm table-tennis ball, which is the same Re band. Treat a C_L dip or sign change in the POLLEN band as **possible, untested**.

**Does not transfer:**
- Any coefficient value for golf balls, baseballs or cricket balls. They are solid, seamed or dimpled, heavier and flown at much higher Re. POLLEN is a ~25 g perforated hollow PE shell at Re ≈ 1–5×10⁴.
- The "speed threshold" for seam tripping. It depends on seam height vs boundary-layer thickness at a given Re. POLLEN hole edges are a different geometry.
- Mehta's flow regime. His balls mostly fly near or above transition; POLLEN is subcritical. Smooth-sphere subcritical behaviour (laminar separation, roughly constant C_D) is the closer starting point, but perforations add internal flow (see rossmann2007).

## 7. What it means for the PM-001 model and test plan

1. **Flight model (HANDOFF §4A):** keep C_L as a function C_L(Re, S) with saturation, and allow a dip or sign change in the sweep. Do not encode a single slope. Use Ito 2025, Cross 2017 and pickleball fits as **shape priors only**.
2. **Orientation term:** add a zero-spin, orientation-dependent transverse force (random sign, magnitude a free parameter) to the Monte Carlo as a scatter source. Mehta's knuckleball point and Cross's string-loop result (cross2017 note) both say surface asymmetry matters at low spin.
3. **Regime flag:** log Re along each trajectory. Flag any segment with Re > 4×10⁴ (v > ≈ 8.5 m/s) as "possible transitional regime for a rough/perforated surface; coefficients unvalidated".
4. **Test plan:** measure C_L and C_D for POLLEN itself across S ≈ 0–2 at 3–10 m/s (video flight tracking as in Steyn 2025 / Cross & Lindsey 2013, or a spinning-ball rig). Include two ball orientations (hole pattern aligned vs rotated relative to the spin axis) to see whether perforation layout changes C_L. Look explicitly for a C_L plateau and for any sign reversal at the fast end.
5. **Do not** cite Mehta 1985 for any number. Cite it for the mechanism (asymmetric separation), the spin-saturation statement and the surface-dependence statement.

## 8. Caveats

- Abstract only, and that abstract was written by an indexer. The paper's own conclusions on spin saturation, critical Re and surface effects could be more specific than the abstract suggests, or could differ.
- The Chadwick thesis is OCR text and a secondary description. The four-regime and reverse-Magnus passages are attributed there to Mehta & Pallis (2001), not to Mehta (1985).
- The transition thresholds in §4.2 come from unreviewed teaching notes, and are generic (smooth vs rough). They are not POLLEN measurements.
- All Re and spin tables are this note's calculations with an assumed ν.
