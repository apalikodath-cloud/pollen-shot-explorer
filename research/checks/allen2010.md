# Fact-check: Allen, Haake & Goodwill (2010), "Effect of friction on tennis ball impacts"

- **Extraction under review:** research/papers/allen2010.md, plus the JSON extraction sent to the lead.
- **Checked on:** 2026-10-30, by an independent PM-001 fact-check agent.
- **What I re-opened:**
  - Crossref API record for 10.1243/17543371JSET66 (metadata and the full 23-entry reference list).
  - SHURA eprint 2149 (abstract and metadata).
  - Unpaywall and Semantic Scholar records.
  - SAGE landing page (HTTP 403 again).
  - A web search for an open copy. None was found.
  - Companion thesis T.B. Allen (2009), SHURA 3215, https://shura.shu.ac.uk/3215/2/10701264.pdf: 291 PDF pages, pdftotext of the OCR layer. Printed page = PDF page - 24.
  - SHURA eprint 5518, the spin-ratio follow-up (abstract and metadata).

**CHECK: 28 confirmed / 3 corrected / 0 dropped / 11 added**

What the tally counts:
- **31 items checked:** 21 JSON data points and 10 key equations.
- **Confirmed (28):** 20 data rows and 8 equations.
- **Corrected (3):** data row 19, plus equations E2 and E3.
- **Not in the tally:** 4 more corrections to method and metadata statements, listed in the next two sections. They cover the validation claim, the section number of the friction study, the ball diameter and the reference-list description.

## Bibliographic data, access, review status
- **Citation.** Authors T Allen, S Haake, S Goodwill; Proc. IMechE Part P 224(3), 229-236; online 2010-05-14; print issue 2010-09-01. All confirmed from Crossref.
- **Review status.** "Peer-reviewed journal" is confirmed. SHURA lists DC.type "PeerReviewed", and IMechE Part P is a refereed journal.
- **Thesis status.** Not journal-reviewed, which is correct. It is an examined PhD thesis, not an unreviewed document.
- **Access.** "Abstract only" is confirmed:
  - SAGE returns 403.
  - Unpaywall: is_oa=false, oa_status=closed, has_repository_copy=false.
  - Semantic Scholar: openAccessPdf CLOSED, and the abstract is elided by the publisher.
  - SHURA 2149 holds metadata and abstract only, with no PDF.
- **Citation count.** Semantic Scholar's 25 citations is confirmed. Crossref's is-referenced-by-count is 10. Both are now recorded.
- **CORRECTED (minor): reference list.** The note calls the Crossref reference list "partial" and says "several other entries have no metadata". In fact Crossref has all **23** references; 18 of them carry DOIs or structured fields (e.g., 10.1119/1.2341635, 10.1119/1.1507792, 10.1119/1.1450571, 10.1007/s12283-009-0032-5). Only the unstructured ones (Brody 1988 TennisPro, the TST 2007 and ANSYS UK papers, the LS-DYNA manual, Brody 2002) lack DOIs. This does not affect the data.
- **Abstract text.** Matches the SHURA abstract verbatim.

## Method statements
- **CORRECTED: validation claim.** The extraction says "the FE models were validated earlier by the same group against twin high-speed-camera experiments, reported in the thesis". This is only partly true.
  - The thesis validates the **ball** model against **perpendicular** rigid-surface impacts only: light gates, force plate and a Phantom v4.2 camera, about 5-30 m/s (§3.4, p. 69 ff.).
  - It validates **oblique spinning** impacts only against a **head-clamped racket** (BOLA, Phantom cameras; §4.4, 20-30 m/s, 20-60 deg, 0-600 rad/s backspin) and a **freely suspended racket** (two synchronised Phantom v4.2 cameras; §5.3-5.4, about 18 m/s at 24 deg and 28 m/s at 23 deg).
  - No oblique **rigid-surface** validation appears in the thesis; text search of pp. 69-87 finds no oblique case.
  - So the paper's court (rigid-surface) friction conclusions rest on validation outside the thesis: Goodwill et al. 2005 (no-spin oblique, about 15 m/s and 30 deg, p. 41) and Allen et al. TST 2007 (ref 5 of the paper, not seen).
  - This weakens the "validated" label for exactly the regime most relevant to POLLEN-on-HIVE.
- **CORRECTED: section of the thesis friction study.** The note says the thesis "has its own friction study (§3)". The ball-string and string-string COF sweeps are in **§4.4.2-4.4.3 (pp. 107-110)**. §3 only fixes the rigid-surface COF at 0.62.
- **CORRECTED (minor): ball size.** The note's §6 gives the tennis ball as "~67 mm". The FE ball is **66 mm** external diameter at the start of the transient (ITF limits 65.41-68.58 mm), thesis p. 66. Mass 5.92e-2 kg and felt 1.67e-2 kg are confirmed (p. 68).
- **Confirmed as stated:**
  - FE settings (thesis p. 69): MAT_RIGID with 18 000 bricks, CONTACT_AUTOMATIC_SURFACE_TO_SURFACE with SOFT=1, time-step scale 0.5, hourglass 0.15.
  - Materials: Ogden rubber, low-density foam felt, AIRBAG_SIMPLE_PRESSURE_VOLUME (pp. 68-69).
  - Software: Ansys/LS-DYNA 10.0 (thesis). The 2010 paper cites the LS-DYNA v970 keyword manual (Crossref ref 21).

## Data points

| # | Item | Verdict | Notes |
|---|---|---|---|
| 1 | Three oblique regimes: slide / slide then overspin / slide, overspin, converge to roll | CONFIRMED | Abstract, verbatim. |
| 2 | Court: slides throughout the majority of impacts during play | CONFIRMED | Abstract. Inbound conditions are not visible. |
| 3 | d(rebound topspin)/dmu > 0 on court | CONFIRMED | Abstract: "rebound topspin ... will increase with increasing court friction". |
| 4 | d(horizontal rebound v)/dmu < 0 on court | CONFIRMED | Abstract. |
| 5 | String bed: ball rolls off; rebound effectively independent of string-bed mu | CONFIRMED | Abstract says "for the majority of groundstrokes". The thesis mechanism is in §5.4.4 (added row A3). |
| 6 | COF sweep values and magnitudes: TBD | CONFIRMED (unavailable) | The paywall is re-confirmed. No numbers exist to check. |
| 7 | Ball-rigid-surface COF 0.62, smooth Rebound Ace, Brody et al. 2002 | CONFIRMED | §3.3.1, p. 69. Caveat: this is the value used in the thesis's ch.3 ball model, which was validated on perpendicular impacts. The value(s) swept in the 2010 paper are unknown. |
| 8 | Ball-string COF 0.4 adopted; 0.2/0.4/0.6 tested | CONFIRMED | §4.4.2 p. 108 and §4.4.3 p. 110. On p. 110 the thesis justifies 0.4 as "within the range of 0.27-0.42 found by Cross (2000b)". |
| 9 | COF 0.4 to 0.6: "only a minor effect" | CONFIRMED | p. 108, Fig. 4.12, 30 m/s, 40 deg, E = 7.2 GN/m2 (Hammer). The text adds that both models agree well with experiment. |
| 10 | COF 0.4 to 0.2: more pronounced; 0.2 over-predicts rebound spin | CONFIRMED | p. 108. |
| 11 | An optimum ball-string mu exists for maximum rebound spin | CONFIRMED | pp. 108-109, Fig. 4.13, 30 m/s, 40 deg, 200 rad/s backspin. Missing detail: the high-mu spin curve drops below the low-mu curve at **about 3.5 ms**. The text attributes this to overspinning in the second half of the impact. |
| 12 | Horizontal force reverses at about 2.85 ms ("just after the midpoint") and again at about 4.2 ms | CONFIRMED | p. 107, Fig. 4.11. Here the "horizontal force" is friction **plus** the string-bed horizontal reaction. The OCR'd caption reads "backspin of 200 m-s-1", a source typo for rad/s. |
| 13 | String-string COF 0.01-0.3: no significant effect; 0.1 kept | CONFIRMED | Text p. 109, Fig. 4.14 caption p. 110. 30 m/s, 40 deg, backspin 0-600 rad/s, impacts at the GSC. |
| 14 | Cross 2000b: sliding 0.27-0.42, rolling 0.05; 5 strings; up to 10 kg drag | CONFIRMED (secondary) | §2.3.3 p. 19. The thesis criticises the method: it measured "a traction force rather than a friction force". |
| 15 | Cross et al. 2000 felt-string COF mostly 0.15-0.18 (0.11-0.36) | CONFIRMED (secondary) | p. 19. Method detail: a 1 m string wrapped twice round a 60 mm felt-covered pipe, with 0.15 kg lifted at an undeclared constant speed. |
| 16 | Cross 2003: time-averaged sliding COF 0.43 +/- 0.02 at 25 deg to the string plane | CONFIRMED (secondary) | §2.3.4 p. 21. The racket sat on two rollers and the force came from a piezo accelerometer on the frame. Balls were hand-thrown at low speed. The signal was noisy from frame vibration. |
| 17 | COR on rigid surface about 0.74, vs 0.75-0.8 for a head-clamped racket, 2.54 m drop | CONFIRMED (secondary) | §2.3.4 p. 20 (Brody et al. 2002). |
| 18 | Capel-Davies 2007: no rolling phase up to 25 deg incidence; horizontal COR proportional to incidence; SPR independent of v_t 11-31 m/s and angle 11-25 deg | CONFIRMED (secondary) | §2.6.1 p. 38. The SPR there was **computed with Brody's (1984) rigid-body model**, and the zero-spin impacts are implied by the follow-on text: "a tennis ball with no inbound spin". |
| 19 | Goodwill 2005: oblique impacts give about 10% smaller volume and higher vertical COR (FE) | CORRECTED (attribution) | p. 40. The **higher vertical COR in oblique impacts is an experimental finding**. FE was used to **explain** it: friction gives an unbalanced horizontal force, the ball deforms forward, volume falls about 10% vs a normal impact, internal pressure rises. |
| 20 | Derived mu_c 0.41-0.74 for a POLLEN-like ball | CONFIRMED (recomputed) | All 9 table cells reproduce to 3 dp. Example: alpha = 2/3, e_n = 0.5 gives 0.4 x 8.536 / (1.3 x 3.536) = 0.644. This is an assumption-driven illustration, correctly labelled as derived. |
| 21 | Derived sliding example: v_t 3.54 to 1.95 m/s; R*omega 5.0 to 2.6 m/s | CONFIRMED (recomputed) | The impulse ratio is 0.3 x 1.5 x 3.536 = 1.591 m/s; dividing by alpha gives 2.386 m/s, so R*omega' = 2.614 m/s. mu = 0.3 < mu_c = 0.644, so the sliding branch is valid. Derived. |

Note-only rows that are not in the JSON were also checked:
- "Contact time about 5 ms, string bed" (p. 20, secondary): confirmed.
- "Internal pressure 76 kPa" (p. 40, measured by Goodwill et al. 2005): confirmed.

## Key equations

| # | Equation | Verdict | Notes |
|---|---|---|---|
| E1 | Rolling condition v_t = R*omega | CONFIRMED (in words) | p. 13 (§2.2.4, "surface tangential velocity of the ball equals its horizontal velocity") and §8.4.2 p. 211 ("Overspinning is defined as ... faster rotation than that associated with rolling"). The thesis states no symbolic equation. |
| E2 | SR = R*omega/v_t; SR = 1 rolling, SR > 1 overspin; validated for SR_in in [-1, 1] | CORRECTED | The definition and the [-1, 1] range are verbatim from the SHURA 5518 abstract. That paper is Allen, Haake & Goodwill, "Spin generation during an oblique impact of a compliant ball on a non-compliant surface", Proc. IMechE P **226** (2012), DOI 10.1177/1754337111430444. The abstract does **not** state "SR = 1 rolling, SR > 1 overspin". That reading follows from the definition, so it is an inference and is now labelled as one. |
| E3 | SPR = 100(1 - mu) "(ITF, thesis p. 13)"; note E1 says "cites Capel-Davies" | CORRECTED (attribution) | p. 13 attributes the definition to **Downing (2007c)**, in a temperature study on acrylic and carpet. It does not mention the ITF or Capel-Davies. Capel-Davies (p. 38) used Brody's rigid model to compute SPR. Here mu is the COF backed out from rebound kinematics with that model, not a tribometer value. |
| E4 | Coulomb plus the warning that a linear friction/normal model is invalid | CONFIRMED | The quote is verbatim from §4.4.2, p. 107, and refers to the string-bed impact. |
| E5-E10 | Rigid-body impulse model: u0, J_n, I = alpha*m*R^2, mu_c, sliding branch, grip branch, e_t branch, reversal at SR_back > 1/alpha | CONFIRMED (re-derived; not from the source) | Re-derived independently. Every expression, the sign convention (omega > 0 in the rolling sense; friction raises omega and lowers v_t) and the 1/alpha = 1.5 / 2.5 thresholds check out. Two cautions. (a) The reversal SR is defined on the surface-tangential v_t, not on the flight S = omega*R/|v|. In the worked case, S = 1 at 45 deg gives SR = 1.41, which is below 1.5, so no reversal in the grip branch. (b) Tangential velocity can also reverse in the **sliding** branch whenever mu(1+e_n)v_n > v_t, while slip stays positive. The note states this, and it is correct. The thesis (§2.6.1, pp. 38-39) and Goodwill & Haake 2004a (p. 42) say rigid-body models **under-predict** rebound spin for felt-covered balls. Treat these as a baseline only. |

## Added data points (missed by the extractor)

| # | Quantity | Value | Conditions | Where | source_id |
|---|---|---|---|---|---|
| A1 | Effect of ball mass and stiffness on maximum outbound SR | Lower ball mass and higher stiffness **increase** the maximum outbound SR. At constant SR_in, outbound SR still depends on inbound speed and angle. | FE tennis ball on a non-compliant surface, SR_in -1 to 1 | abstract, SHURA 5518 (2012 follow-up) | allen2012 |
| A2 | When the ball overspins on a string bed | It overspins during the impact **except** when a high inbound angle (60 deg) combines with backspin > 400 rad/s | head-clamped validation: 0-600 rad/s backspin, 20-30 m/s, 20-60 deg | thesis §4.4.4 p. 111 | allen2009thesis |
| A3 | Freely suspended racket time history, the basis of the paper's "rolls off the string bed" finding | The horizontal force opposes motion first (backspin decreases), reverses at about mid-impact (overspin), then converges to zero, so the ball rolls off | FE, 28 m/s, 23 deg, 200 rad/s backspin, centre impact | thesis §5.4.4 pp. 154-155, Fig. 5.18 | allen2009thesis |
| A4 | FE accuracy for backspin | FE under-predicts rebound spin for inbound backspin above about 200 rad/s. Measurement uncertainty in spin is about 20 rad/s | freely suspended racket, about 18-28 m/s, 23-24 deg | thesis §5.4.5 p. 155 | allen2009thesis |
| A5 | Trend of rebound spin with inbound backspin | Rebound spin decreases as inbound backspin increases and increases with inbound angle. Both model and experiment turn non-linear above about 350 rad/s backspin at 60 deg | head-clamped racket, 20-30 m/s | thesis §4.4.2 pp. 104-105, Fig. 4.10 | allen2009thesis |
| A6 | Rigid-surface overspin with no inbound spin (Goodwill et al. 2005, secondary) | Experiment: oblique no-spin impacts rebound with spin greater than rolling. FE attributes this to a lag before the friction force reverses, caused by felt shear | rigid surface, Fig. 2.14 at 15 m/s, 30 deg, no initial spin | thesis §2.6.1 p. 41 | allen2009thesis |
| A7 | Brody (1984) rigid-body model (secondary) | Low incidence: slides throughout. High incidence: slides, then rolls. The COF needed to start rolling **falls as incidence rises** (constant COR). Valid for about a 1 m drop, deformation < 10% of diameter | rigid ball, constant COR | thesis §2.6.1 p. 38 | allen2009thesis |
| A8 | Critical ball-string sliding COF (Cross 2000b model, secondary) | 0.3. Below it, rebound angle and range drop significantly | analytical model, 10 m/s, centre impact, not validated | thesis §2.6.2 p. 42 | allen2009thesis |
| A9 | Mechanism of friction reversal on a rigid surface (secondary) | The contact flattens and friction reverses if rotational speed exceeds horizontal speed. At large load the wall buckles into an annulus, which slides until it grips. It then vibrates horizontally and slips backward, giving spin above rolling | tennis ball on rigid surface | thesis §2.2.4 p. 13 (Cross 1999, 2002; Haake et al. 2003b) | allen2009thesis |
| A10 | FE ball geometry and pressure | 66 mm external diameter. Initial pressure 85 kPa assigned at relative volume 1.05; the measured ball pressure is 76 kPa | FE ball model | thesis §3.3 p. 66 (85 kPa); p. 40 (76 kPa) | allen2009thesis |
| A11 | Crossref citation count, as a cross-check of review footprint | 10 (vs Semantic Scholar 25) | metadata | Crossref API | allen2010 |

## Verdict on the extraction
- **Honest about access.** The extraction is careful and honest about access. Every number it gives comes from the open thesis, correctly attributed. No 2010-paper numbers were invented or filled from memory. I re-tried SAGE and searched for an open copy; neither turned up anything, so abstract-only stands.
- **Main substantive correction.** The thesis validation does **not** cover oblique spinning impacts on a rigid surface. The paper's court-friction conclusions, which are the ones most relevant to POLLEN-on-HIVE, depend on validation not visible to us: Goodwill 2005, no spin; TST 2007, unseen.
- **Other corrections are attribution-level:**
  - SPR comes from Downing (2007c).
  - The SR = 1 / SR > 1 reading is an inference, not stated.
  - The Goodwill 2005 COR finding was experimental; the FE only explained it.
  - The friction study is in §4.4, not §3.
  - The FE ball is 66 mm, not about 67 mm.
- **Derived numbers.** Every derived equation and number was re-derived and reproduces.
- **For POLLEN, three additions matter:**
  - A1: lighter, stiffer balls reach higher outbound SR. POLLEN is 25 g and stiffer per unit mass than tennis, so this argues toward stronger spin effects at rebound. The direction is qualitative only.
  - A7: the COF needed for grip falls as incidence steepens. Near-vertical HIVE entry is therefore more likely to reach grip than a grazing rim hit.
  - A4: FE and rigid models under-predict rebound spin at high backspin. Measure rather than trust either.
