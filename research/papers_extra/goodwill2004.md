# Goodwill, Chin & Haake (2004): Aerodynamics of spinning and non-spinning tennis balls

source_id: `goodwill2004` (source #15 in RESEARCH_PAPERS.md). Companion sources, **not the paper**: `goodwill_haake2004wear` (same group's conference paper on wear, abstract only), `haake2007roughness` (same group's roughness review, abstract only), `chadwick2003thesis` (open Sheffield PhD thesis from the same group, OCR), `cross_lindsey2013web` (Cross & Lindsey review table on Tennis Warehouse University, unreviewed web page). Every row below says which source it came from.
Read: 2026-10-30, research agent for PM-001.

## 1. Citation, access, review status

| Field | Value |
|---|---|
| Citation | S. R. Goodwill, S. B. Chin and S. J. Haake, "Aerodynamics of spinning and non-spinning tennis balls", *Journal of Wind Engineering and Industrial Aerodynamics* **92**(11), 935–958 (2004). DOI 10.1016/j.jweia.2004.05.004 |
| Dates | Online 7 Jul 2004 (Unpaywall); issue Sep 2004 (Crossref) |
| Affiliation | Department of Mechanical Engineering, University of Sheffield, UK |
| Review status | **Peer-reviewed journal** (SHURA record `refereed: TRUE`). Crossref: 39 citations; Semantic Scholar: 59. |
| Method type | **Wind tunnel, experimental.** Phase 1: drag of non-spinning new and used balls. Phase 2: drag and lift of spinning balls held between two horizontal shafts in the working section. Plus trajectory plots. |
| Access | **Abstract only.** ScienceDirect returned HTTP 403. Unpaywall: `is_oa=false`, `oa_status=closed`. Semantic Scholar: CLOSED, abstract elided. SHURA record 634 has the abstract only (`full_text_status: none`). |
| Consequence | **No result numbers from the paper were seen.** The abstract states the test **conditions** (Re range, speed range, maximum spin rate); these are quoted in §2 and used in §5 only to define the tested regime. No C_D or C_L values from the paper were seen. A secondary review table quotes ranges attributed to this paper; they are in §5, marked secondary and ambiguous. |

URLs tried:
- https://api.crossref.org/works/10.1016/j.jweia.2004.05.004 (metadata, no abstract)
- https://api.unpaywall.org/v2/10.1016/j.jweia.2004.05.004 (closed)
- https://api.semanticscholar.org/graph/v1/paper/DOI:10.1016/j.jweia.2004.05.004 (closed, abstract elided)
- https://www.sciencedirect.com/science/article/pii/S0167610504000984 (403)
- https://shura.shu.ac.uk/634/ and https://shura.shu.ac.uk/cgi/export/eprint/634/JSON/shu-eprint-634.js (**abstract, verbatim source for §2**)
- https://search.isc.ac/Inventory/10/11866.htm (index listing; search snippet only)
- https://shura.shu.ac.uk/cgi/export/eprint/2234/JSON/shu-eprint-2234.js (wear conference paper, abstract)
- https://shura.shu.ac.uk/cgi/export/eprint/635/JSON/shu-eprint-635.js (2007 roughness paper, abstract)
- https://twu.tennis-warehouse.com/learning_center/aerodynamics2.php (Cross & Lindsey 2013 web review; Table 1a/1b)
- https://etheses.whiterose.ac.uk/12839/1/397496.pdf (Chadwick 2003 thesis, full text, OCR, 331 pp.)
- Web searches (2): paper title + abstract terms; Goodwill thesis at White Rose. No open full text of the paper was found.

**Action for the lead:** with Elsevier access, fill the "TBD" rows in §5 (C_D vs Re per ball, C_L and C_D vs S at each tunnel speed, worn vs new).

## 2. What the paper reports (abstract, verbatim from SHURA)

> "The aerodynamic properties of a tennis ball are obtained using wind tunnel measurements. In the first phase of this study, the drag coefficient of a variety of new and used non-spinning tennis balls was measured. The measurements were conducted in the Reynolds number range of 85×10³<Re<250×10³, which corresponds to a velocity range of 20<U<60 ms−1 (45<U<135 mph). The data for the new tennis balls revealed that all balls have similar drag coefficients, within the repeatability of the experiment. However, it was shown that a heavily worn ball exhibits a significant decrease in drag coefficient. A simple trajectory plot was used to illustrate the significance of this drop in CD, on a typical tennis stroke. It was shown that if the drag coefficient of the worn ball was reduced even further, then the ball would travel faster through the air, and give the receiver a significantly shorter time to react to the shot.
>
> In the second phase of this study, the drag and lift coefficients of new and used spinning tennis balls was measured. This testing was conducted by placing the ball inside the working section of the wind tunnel, held between two horizontal shafts. The ball was spun at rates up to 2750 rpm, which is representative of a typical top spin shot hit by a professional player. The data showed that the lift coefficient for all the new balls was identical. However, the lift coefficient was generally lower for the heavily worn ball compared with the new ball. A trajectory plot was calculated to illustrate the effect of the lower drag and lift coefficients of the worn ball, compared to the new ball. It was shown that the lift coefficient value has little effect on the reaction time of the receiver. It was also shown that a lower lift coefficient reduces the window of opportunity for the server because the player is less able to utilise the spin to control the shot to ensure that the ball both clears the net and also lands in the service box. This highlights the fact that it may not be in the manufacturers interest to produce a 'faster' tennis ball with a lower drag coefficient, because the ball may also have a lower lift coefficient, thus reducing the players ability to play certain strokes."

Findings (graded):
1. **New balls of different brands: same C_D and same C_L** within experimental repeatability. *Peer-reviewed finding.*
2. **Heavy wear lowers C_D significantly, and lowers C_L.** Surface (nap) condition controls both forces. *Peer-reviewed finding.*
3. **A lower C_L narrows the usable shot window** (net clearance plus landing in the box), even though it hardly changes flight time. Lift matters for *where* the ball lands, not for how fast it arrives. *Peer-reviewed finding (by trajectory simulation).*
4. **Spinning tests used a shaft-mounted ball**, i.e. a supported ball, not free flight. *Method fact.*
5. The abstract says nothing about saturation of C_L with S, negative Magnus or a drag crisis. Those questions cannot be answered from this source as read.

## 3. Method (as far as it can be reconstructed)

From the abstract: wind tunnel; non-spinning balls (new and used) for drag; spinning balls (new and used) for drag and lift, held between two horizontal shafts; spin up to the stated maximum; trajectory simulation.

From companions (**context, not confirmed to be this paper's set-up**):
- `goodwill_haake2004wear` abstract: spinning balls on "a wind tunnel with a dedicated force balance", same maximum spin; C_D and C_L of worn balls "generally lower"; heavily worn balls give a receiver 1.5% less reaction time.
- `chadwick2003thesis` (same Sheffield group, one year earlier): the tennis nap adds drag beyond a rough sphere ("fuzz drag", pressure drag on the fibres, citing Mehta & Pallis 2001); nap fibres flatten as wind speed rises; a shaved-nap ball's C_D fell to about 0.4 at Re ≈ 70 000 and stayed there (thesis §7, p. 182); in its spinning flow-visualisation tests "there was no sign of a negative Magnus effect over the speed and spin rates tested" (thesis §8.4.3, p. 214).

## 4. Equations

The paper's own equations were not visible. Standard definitions (same as PM-001 HANDOFF §4): F_D = ½ ρ C_D A v², F_L = ½ ρ C_L A v², Re = v D / ν, S = R ω / v.

### 4.1 Regime comparison with POLLEN (**derived here, not from the paper**)

- **Goodwill tunnel:** Re 8.5×10⁴ to 2.5×10⁵ at 20–60 m/s (abstract). The implied D/ν ratio is ≈ 4.2×10³ s/m (derived from those two pairs), consistent with a ~64 mm ball at ν ≈ 1.5×10⁻⁵ m²/s.
- **POLLEN:** Re ≈ 9×10³ to 4.7×10⁴ at 2–10 m/s (D = 71 mm, ν = 1.5–1.6×10⁻⁵ m²/s, assumed; see mehta1985 §4.1). **POLLEN's whole Re band lies below Goodwill's lowest tested Re.** POLLEN would need v ≈ 18 m/s to reach Re = 8.5×10⁴ (derived).
- **Spin parameter covered by Goodwill (derived, assumed tennis radius 32.7–34.3 mm, not seen in the source):** 2750 rpm = 288 rad/s gives S ≈ 0.47–0.49 at 20 m/s and S ≈ 0.16 at 60 m/s. So the paper's maximum S is roughly ≤ 0.5.
- **POLLEN shooter:** ideal hood gives S_exit ≈ 1 (HANDOFF §4C), and S rises as the ball slows (S ∝ 1/v at fixed ω). **POLLEN's operating S (≈ 1 at launch, more near apex) is above anything Goodwill tested.**

Result: this paper covers neither POLLEN's Re nor its S range. Its value is qualitative.

## 5. Data table

Only rows marked `goodwill2004` come from the target paper (abstract). Rows marked `cross_lindsey2013web` are a secondary web table quoting the paper. Rows marked `derived` are this note's calculations.

| Quantity | Value | Conditions | Where | source_id |
|---|---|---|---|---|
| Re range, non-spinning tests | 85×10³ < Re < 250×10³ | 20–60 m/s | abstract | goodwill2004 |
| Max spin, spinning tests | 2750 rpm | ball held between two horizontal shafts | abstract | goodwill2004 |
| C_D across new brands | similar (within repeatability) | non-spinning | abstract | goodwill2004 |
| C_D, heavily worn vs new | significantly lower | non-spinning | abstract | goodwill2004 |
| C_L across new brands | identical | spinning | abstract | goodwill2004 |
| C_L, heavily worn vs new | generally lower | spinning | abstract | goodwill2004 |
| C_D(Re), C_L(S), C_D(S) values; any C_L saturation or sign change | TBD (paywalled) | n/a | body, figures | goodwill2004 |
| C_D, non-spinning (secondary) | 0.6–0.66 | "Wind Tunnel", velocity 40–135 mph | Table 1a | cross_lindsey2013web |
| Spinning row (secondary, **ambiguous**) | cells "0.65–0.69" and "0.05–0.25" appear under the Spin (rpm) and Spin Ratio columns; the C_D and C_L cells are empty. The values look shifted (they read like C_D and C_L ranges) but the page does not say so. **Do not use.** | velocity 40–135 mph | Table 1b | cross_lindsey2013web |
| Conclusions the web review draws from all tennis wind-tunnel work | no drag crisis at playing speeds; C_D rises slightly with spin; C_L rises with S "but less so as velocity increases"; C_D and C_L independent of brand; nap orientation matters | multiple studies, not this paper alone | text under Table 1 | cross_lindsey2013web |
| Wind tunnel vs free flight (tennis) | free-flight C_D and C_L were lower than all conventional (sting-mounted) wind-tunnel results; drop-through-tunnel results were similar to free flight | Cross & Lindsey 2013 trajectories | text | cross_lindsey2013web |
| Worn-ball reaction time | 1.5% less | trajectory plot | abstract | goodwill_haake2004wear |
| Tennis spin decay vs golf | over six times golf, attributed to nap skin friction | review | abstract | haake2007roughness |
| Negative Magnus in tennis-ball spin tests | not seen over speeds and spins tested | Sheffield tunnel flow visualisation | thesis p. 214 | chadwick2003thesis |
| POLLEN Re band | ≈ 9×10³ to 4.7×10⁴ | 2–10 m/s | §4.1 | derived |
| Max S in Goodwill tests | ≈ 0.16–0.49 | 2750 rpm, 20–60 m/s, assumed tennis R | §4.1 | derived |

## 6. Applicability to POLLEN

**Transfers (qualitatively):**
- **Surface condition changes C_L and C_D together.** Wear lowered both. For POLLEN, scuffs, flattening, hole-edge damage or dirt could shift C_L between new and used balls. Match-ball variation is a real scatter source. *Peer-reviewed finding → POLLEN by analogy.*
- **Lift sets the landing window more than flight time.** This is the exact PM-001 question. A small change in C_L changes where the ball comes down, not when. Entry into a CELL is a landing-window problem, so C_L uncertainty must be carried into the scoring map. *Peer-reviewed finding (trajectory simulation) → transfers as logic.*
- **Supported-ball tunnel tests vs free flight.** The paper's spinning data come from a shaft-mounted ball. The secondary review reports that sting- or shaft-mounted tests gave higher C_D and C_L than free flight. For PM-001, coefficients should come from free-flight measurement of POLLEN. A mounted test is a fallback only. *Unreviewed technical source (for the comparison).*
- **Spin decay is surface-dependent** (tennis nap ≫ golf, `haake2007roughness`). POLLEN's perforations may pump air and add spin-down torque. Spin decay over a 1–2 s high arc can be significant. Measure it. *Peer-reviewed (abstract) → POLLEN unknown.*

**Does not transfer:**
- Any C_D or C_L number. The tennis ball is a felt-covered, pressurised, much heavier ball tested at Re 8.5×10⁴–2.5×10⁵ and S ≤ ~0.5. POLLEN is a 25 g perforated PE shell at Re 1–5×10⁴ and S ≈ 1 or more. Both Re and S are outside the tested range. **Do not use the 0.6-ish C_D or any C_L from tennis as POLLEN values.**
- "Fuzz drag" and nap effects. POLLEN has no nap. Its perforations are a different surface: they allow through-flow (see rossmann2007), which tennis balls do not have.
- The absence of negative Magnus in tennis tests. It applies to a felt-covered ball. Cross's notes (unreviewed) say tennis-ball flow "is always turbulent since the surface is quite rough"; Chadwick's thesis says the flow in its tests was "either always fully laminar or fully turbulent". A smoother perforated shell at low Re can behave differently. Ito 2025 found C_L dips for a smooth 40 mm ball in the same Re band as POLLEN.
- Saturation or nonlinearity of C_L vs S. The abstract is silent, and the tested S range is too low to show it anyway.

## 7. What it means for the PM-001 model and test plan

1. **Flight model (HANDOFF §4A):** do not anchor C_L(S) on tennis data. At best, tennis supports the sign (backspin gives upward lift in the S ≤ 0.5 range on a rough ball) and a sub-linear rise with speed. POLLEN needs its own C_L(Re, S) in S ≈ 0.5–3.
2. **Monte Carlo:** add a ball-to-ball C_L and C_D spread (new vs worn ball) and a per-ball surface factor. Re-run the scoring map with ±20–30% C_L spread (an **assumption**, not from this paper) to see whether the backspin advantage survives.
3. **Test plan:**
   - Free-flight tracking of POLLEN from the actual shooter at several wheel speeds (v, ω measured at exit). Fit C_D and C_L per segment. That covers the real (Re, S) band.
   - Repeat with **new and scuffed POLLEN** to measure the wear effect directly.
   - Measure spin decay over the arc (high-speed video of a marked ball at launch and near apex).
   - If a spinning-ball rig is used, compare it with free flight on a few shots before trusting it (supported vs free-flight bias).
4. **Do not** cite Goodwill 2004 for any number. Cite it for: brand-independence of new-ball coefficients, the wear effect on both C_D and C_L, the landing-window role of C_L, and the shaft-mounted method.

## 8. Caveats

- Abstract only for the target paper. The paper may contain C_L-vs-S curves showing saturation, low-speed anomalies or orientation effects that the abstract does not mention.
- The Cross & Lindsey table cites this paper with inconsistent reference numbers ([6] in the table, [7] in the reference list) and its spinning row has shifted cells. Treat it as a pointer, not data.
- Companion abstracts and the Chadwick thesis are from the same group but are not this paper. The thesis text is OCR.
- §4.1 numbers are this note's calculations with an assumed ν and an assumed tennis-ball radius.
