# 05 - Spin-assisted contact entry, hypothesis (B) (HANDOFF §3 Q5, §4E channel 2)

Code: `src/contact.py` (impact law, contact flight, sweeps, report), `tests/test_contact.py`.
Data: `data/contact_incidence_sweep.csv`, `data/contact_launch_sweep_t30.csv`, `data/contact_launch_sweep_t28.5.csv`,
`data/contact_launch_sweep_t31.5.csv`, `data/contact_kick_stats.csv`, `data/contact_spin_comparison.csv`.
Figures: `figures/contact_incidence_maps.png`, `figures/contact_retention_vs_spin.png`,
`figures/contact_decomposition.png`, `figures/contact_launch_windows.png`.
Reproduce: `python -m src.contact --stage all --cache <dir>`. Stages are `incidence`, `launch`, `tilt` and `report`.
The launch stage runs 64 parallel jobs and takes tens of minutes. Tests: `python -m unittest discover -s tests -v`.

Scope: this file covers hypothesis (B) of HANDOFF §0: the ball touches the rim or the inside of the **upward-facing
CELL of the HIVE** and still stays in. It is kept separate from hypothesis (A), clean air-only entry, which is in
docs/03_clean_entry.md. Where this file uses (A) numbers, it says so.

Provenance labels: **confirmed** (official source), **derived** (computed, formula given), **assumed**,
**predicted** (output of this model), **user**. Every retention number here is **predicted**. It depends on:
- assumed contact coefficients e, mu and e_t (POLLEN on the HIVE skin has never been measured);
- assumed aerodynamics (data/aero_params.json, docs/02_aero.md);
- the CAD-derived 2D centre-plane section (docs/01_hive_geometry.md; the 30 deg tilt is confirmed).

Pickleball literature values are **not** POLLEN data. They only set the sweep ranges. Written 2026-10-30.

## 1. Method

### 1.1 Frame, geometry and sides

- I use the 2D centre-plane section from `hive.py` (docs/01 §3) **read-only**. Tilt is 30 deg (confirmed).
- **Unfavourable side**: the HIVE in **pose_pos**, shot from the 'neg' side. The shooter stands at x = -d and fires toward +x.
  - The up CELL's mouth faces normal_out = (0.866, 0.5) (derived).
  - So a ball can only cross the mouth inward while it is descending at more than 60 deg below horizontal.
  - Every number in this file is for this side. The favourable side is far easier for hypothesis (A) (docs/03), and I did not sweep it here.
- In the shot frame, **backspin on a +x ball is w < 0**, matching `flight.backspin_omega`. Spin ratio is S = |w| R / |v|.
- Landmarks (derived from data/hive_geometry.json):

| Landmark | Segment | Position |
|---|---|---|
| Far rim | `up_lower_lip`, gate low end | (0.473, 1.387) m |
| Near rim | `up_upper_lip` / roof end, gate high end | (0.330, 1.635) m |
| Gate (ball-centre mouth line) | — | 0.286 m long |

- The CELL **floor rises toward the mouth** at 30 deg. Its low corner is at the back wall.

### 1.2 Impact law (derived)

Rigid sphere on a fixed rigid segment or edge. The full derivation is in the `src/contact.py` docstring.

**Contact frame and velocities:**
- n = unit(ball centre - closest point on the segment). This handles flat faces and corners (segment end points) the same way.
- t = (n_z, -n_x).
- Normal approach velocity: v_cn = v.n (m/s).
- Contact-point slip: v_ct = v.t - R w (m/s).

**Impulses:**
- Normal: P_n = -(1+e) m v_cn (N s).
- Stick candidate: P_t* = -(1+e_t) m_t v_ct, with m_t = m alpha/(1+alpha) and alpha = I_b/(m R^2).
- If |P_t*| <= mu P_n the contact sticks and P_t = P_t*. Otherwise it slips: P_t = -mu P_n sgn(v_ct) (Coulomb).

**State update:** m dv = P_n n + P_t t and I_b dw = -R P_t.

**Parameters:**

| Parameter | Value | Source |
|---|---|---|
| m | 24.95 g | confirmed (aero_params.json, AndyMark spec) |
| R | 35.5 mm | confirmed (Manual TU07 9.8) |
| alpha | 0.63, bounds 0.60-0.667 | derived (aero_params.json `I_b`) |
| e | swept 0.3-0.8 | assumed |
| mu | swept 0.2-0.8 | assumed |
| e_t | 0, spot check 0.3 | assumed |

**Properties (unit-tested):**
- Energy never increases.
- mu = 0 leaves spin unchanged.
- The stick regime ends exactly at rolling: v_ct' = 0, so a sliding ball leaves a flat surface with v/(1+alpha) when spin starts at 0. For a solid sphere this is the textbook 5/7.
- A ball released on an incline reproduces rolling acceleration g sin(theta)/(1+alpha), within 3 %.

**Backspin kick sign (derived, unit-tested on the real lip corners).** Spin enters only through v_ct. Compared with the same impact without spin, backspin changes the velocity along **k = (-n_z, n_x)**. The size of that change is between 0 and m_t R|w|/m. It is zero when both cases slide the same way.

| Contact | Normal n | Backspin kick k | Effect |
|---|---|---|---|
| Far rim (lower lip), ball's lower-front surface on the way in | (-sin c, cos c), c in the corner cone -60..30 deg | (-cos c, -sin c): back toward the shooter and down; equal to the CELL inward axis at c = 30 | "check": pushes the ball **into** the CELL |
| Near rim (roof end), struck from above or behind (shot slightly long) | (-sin a, cos a) | backward-and-down **around the roof corner** | holds the ball over the ROOF, **away** from the mouth, which is on the +x side of that corner |
| CELL floor after a clean entry | floor normal | along the inward axis, toward the back wall | drives the ball into the back-wall/roof corner, where it can rebound out through the mouth |

### 1.3 Flight between contacts and termination

**Flight.**
- Vectorised RK4, dt = 1 ms.
- The force model is identical to `flight.py`: drag, Magnus Cl = min(c1 S, Cl_max), and spin decay dw/dt = -k w. Aero sets come from aero_params.json (assumed).
- Cross-checked against `flight.simulate`: they agree to 2e-6 m (unit test).

**Contacts.**
- Contact detection: penetration at the end of a step, then a 22-step bisection on the chord, then the impulse, then the rest of the step is re-integrated.
- Approach speeds below 0.05 m/s (assumed) are treated as resting contact: the ball is projected out and given a plastic (e = 0) frictional impulse.

**Outcomes.**
- **retained_clean**: entered the CELL with no earlier contact and ended trapped. Later contacts inside the CELL are allowed.
- **retained_contact**: at least one contact before entering, then trapped.
- **bounced_out**: entered, then left.
- **blocked**: touched the HIVE but never entered.
- **miss**.
- **timeout**: counted as not retained.

**Trapped (derived, conservative).**
- Definition: the centre is inside the CELL polygon AND the total energy z + v^2/(2g) + I w^2/(2 m g) is below z_barrier = 1.387 m. z_barrier is the gate low end; the true lip crest is 1.392 m.
- Drag and the impacts only remove energy, so a trapped ball can never leave.
- Counting spin energy as available for climbing makes the criterion stricter.
- First-contact zone (2 mm tolerance):
  - near_rim (upper lip);
  - far_rim (lower lip);
  - interior;
  - external (roof top, outer faces).

### 1.4 Sweeps

**Part A, local incidence (`contact_incidence_sweep.csv`).**
- The free path's mouth-plane crossing is fixed by:
  - gate coordinate s: -0.10..0.45 m, step 5 mm, where s = 0 is the far rim and 0.286 is the near rim;
  - descent angle phi: 60-88 deg, step 2;
  - speed v_i = 5 m/s (spot checks at 3.5 and 6.5).
- Pre-impact S is 0, 0.5, 1, 1.5 or 2, with S = 0 as the control.
- The state is integrated back 0.10 s and run forward.
- Because the crossing state is the same for every S, Part A isolates the **collision-spin** effect. The Cl variants change almost nothing (table 2.1).
- Grid: full e x mu grid (4 x 4). Spot checks:
  - e_t = 0.3;
  - I_b bounds;
  - Cl low/high/none;
  - topspin S = -1, exploratory.

**Part B, full launches (`contact_launch_sweep_t30.csv`, `contact_spin_comparison.csv`).**
- Launch grid: v 5-9.5 m/s step 0.05, elevation 66-89.75 deg step 0.25.
- (h, d) cases:
  - h 0.737 m with d 0.65 / 0.70 / 0.75 / 0.90 / 1.15 m;
  - h 0.35 m with d 0.75 / 0.90 / 1.15 m.
  - h 0.737 m is the 29 in height cap, docs/01 §6.
- Flight cases:
  - S0;
  - S0.5_nom;
  - S1 with Cl low, nominal or high;
  - S2_nom;
  - S1_nom_airOnly: Magnus flight, spin set to 0 at the first HIVE event;
  - S1_collOnly: no Magnus, so the same path as S0, with the spin carried into the contacts.
- Method: stage 1 flies to the first HIVE event. Stage 2 repeats each event over the full e x mu grid.
- Statistics use v <= 8.9 m/s, the predicted hood cap (docs/04).
- Tilt bounds 28.5 / 31.5 deg are checked for (0.737, 0.75) and (0.737, 0.90), cases S0 and S1_nom.

## 2. Part A: contact at the mouth for a fixed incidence (predicted)

### 2.1 Retention widths, v_i 5 m/s, mean over descent 64-86 deg

Widths are measured along the gate in mm, out of a geometric gate of 286 mm. The grid step is 5 mm, so a 1-cell
feature is 5 mm. Column meanings:
- **retained**: all retained.
- **clean**: retained, with no contact before entry.
- **contact**: retained after at least one contact before entry.
- **far / near rim**: the contact width split by first-contact zone.
- **CE bounced out**: clean entries that bounced back out.
- **P20**: best retention probability for a Gaussian aim scatter of sigma 20 mm along the gate. The scatter is assumed.

| case (e 0.6, mu 0.4 unless stated) | retained | clean | contact | far rim | near rim | CE bounced out | P20 |
|---|---|---|---|---|---|---|---|
| S 0 (control) | 183 | 143 | 39 | 30 | 9 | 0 | 0.89 |
| S 0.5 | 185 | 132 | 54 | 47 | 7 | 13 | 0.86 |
| S 1 | 76 | 17 | 59 | 55 | 5 | 128 | 0.72 |
| S 1.5 | 50 | 0 | 50 | 46 | 4 | 145 | 0.67 |
| S 2 | 38 | 0 | 38 | 38 | 1 | 145 | 0.57 |
| S 1, Cl none / low / high (airborne Magnus switched) | 79 / 79 / 75 | 18 / 18 / 16 | 61 / 61 / 59 | 55 | 6 / 6 / 5 | 125-130 | 0.71-0.73 |
| S 1, I_b low / high | 83 / 70 | 22 / 10 | 61 / 60 | 56 | 5 / 3 | 123 / 135 | 0.72 |
| S 0 / S 1, e_t 0.3 | 189 / 58 | 143 / 0 | 45 / 58 | 30 / 54 | 16 / 3 | 0 / 145 | 0.92 / 0.73 |
| S 0 / S 1, v_i 3.5 m/s | 210 / 161 | 135 / 62 | 75 / 99 | 60 / 88 | 15 / 10 | 0 / 74 | 0.99 / 0.99 |
| S 0 / S 1, v_i 6.5 m/s | 174 / 59 | 148 / 4 | 27 / 55 | 23 / 50 | 4 / 5 | 0 / 145 | 0.86 / 0.71 |
| topspin S = -1 (exploratory) | 68 | 54 | 13 | 6 | 7 | 87 | 0.51 |

Total retained width (mm) over the full e x mu grid, mean over 64-86 deg. Each cell is `retained / clean / contact`.

| S \ e | mu | e 0.3 | e 0.45 | e 0.6 | e 0.8 |
|---|---|---|---|---|---|
| 0 | any (0.2-0.8 give the same widths within 2 mm) | 203/143/60 | 199/143/55 | 182/143/39 | 171-173/143/28 |
| 0.5 | 0.4 | 227/145/82 | 220/145/75 | 185/132/54 | 180/144/36 |
| 1 | 0.2 | 223/145/78 | 122/40/82 | 73/13/60 | 87/49/38 |
| 1 | 0.8 | 248/145/103 | 130/44/86 | 81/18/64 | 119/69/50 |
| 2 | 0.4 | 81/6/75 | 58/0/58 | 38/0/38 | 35/0/35 |

Findings (all **predicted**):

1. **Where contact retention happens.** At S = 0 it is almost entirely at the far rim (lower lip). There, a ball whose free
   path would cross just short of the gate low end (s about -30..0 mm) clips the lip and drops in. This band joins the clean
   window, so it **widens the clean window on its low side**. It is not a separate target. Near-rim retention exists only as
   isolated 5-15 mm cells at s about 0.27-0.33 m: a lucky deflection, not an aim point. No retained ball touched the roof
   top or the outer faces first (w_rk_external = 0 in every case).
2. **When contact retention is reliable.** The far-rim band is 30-60 mm wide at S = 0. It is wider at low e (60 mm at e 0.3,
   28 mm at e 0.8) and at low speed (75 mm at 3.5 m/s, 27 mm at 6.5 m/s). This is below a plausible aim scatter. So contact
   is reliable only **as a margin next to a clean window**, at descent of 68 deg or more. At 64-66 deg, where no clean window
   exists, only 15-40 mm patches remain (P20 0.29-0.68). Contact alone is not a reliable scoring mode on this side.
3. **Backspin vs no spin, collision part only.** Part A fixes the free-path crossing, so this is the collision-spin effect.
   Backspin S = 1 roughly **doubles the far-rim contact band** (30 to 55 mm, e 0.6). It also turns **most clean entries
   into bounce-outs** (128 of 143 mm of clean width lost). The floor contact's backspin kick (table 1.2) drives the ball into
   the back-wall/roof corner, and it rebounds out of the mouth. Net retained width falls from 183 to 76 mm, and P20 from 0.89
   to 0.72. S = 0.5 is roughly neutral (185 mm). S of 1.5-2 is worse again (38-50 mm).
   - **More backspin does not always help.** It helps only at e = 0.3 (S 1: 223-248 mm vs 203 mm at S 0) and at
     shallow descent (68-72 deg, S 1: 130-200 mm vs 70-185 mm at S 0).
   - Topspin is also worse than none.
4. Retention is not sensitive to I_b (±7 mm) or e_t. The airborne Cl set changes almost nothing in Part A (±4 mm). This is
   by design: the crossing state is fixed, which confirms that Part A isolates the collision contribution.

`data/contact_kick_stats.csv` (controlled first contact, identical crossings, e 0.6, mu 0.4) quantifies the mechanism:

| first-contact zone (same zone in both runs) | n | stick frac S0 / S1 | retained frac S0 / S1 / S2 | reading |
|---|---|---|---|---|
| far rim (lower lip) | 240 | 1.00 / 0.86 | 0.36 / 0.60 / 0.40 | backspin "check" helps at S 1, less at S 2 |
| interior (floor, after a clean entry) | 384 | 1.00 / 1.00 | 1.00 / 0.086 / 0 | backspin floor kick throws the ball out |
| near rim (roof end) | 755 | 0.90 / 0.63 | 0.028 / 0.015 / 0.003 | kick is around the roof corner, away from the mouth |
| external (roof top, outer faces) | 265 | 1.00 / 1.00 | 0 / 0 / 0 | never retained |

- The median extra velocity change on the CELL inward axis is +1.7 to +1.9 m/s at S 1 in every zone (derived from
  the impulses, predicted values). At the near rim and on external faces this projection is **misleading**: the kick goes
  around the roof corner, not into the mouth (CSV header CAUTION). Use the retained fractions.
- Net (predicted): backspin buys about +0.24 retained fraction on far-rim clips. It costs about -0.91 on clean entries that
  touch the floor. Clean entries are more numerous on this side, so the net effect is negative.

## 3. Part B: full launches (predicted)

Cells are 0.05 m/s x 0.25 deg, v <= 8.9 m/s (predicted hood cap, docs/04). Counts are retained cells, mean over the
4 x 4 e x mu grid (e and mu assumed). `P_tight` / `P_loose` = best retention probability under an assumed Gaussian launch
scatter (sigma 0.05 m/s x 0.25 deg / 0.15 m/s x 0.75 deg). The hood shooter of docs/04 gives S of about 1.06 at every RPM
(predicted), so **S1_nom is the case that matters for a hood shooter**.

### 3.1 Retained cells by case

| h, d (m) | S0 | S0.5 | S1 nom (low / high Cl) | S2 | S1 airOnly | S1 collOnly |
|---|---|---|---|---|---|---|
| 0.737, 0.90 | 164 (127 clean / 37 contact) | 146 | 89 (89 / 88) | 60 | 154 | 91 |
| 0.737, 0.75 | 125 | - | 43 (50 / 34) | - | 99 | 53 |
| 0.737, 1.15 | 131 | - | 74 (76 / 73) | - | 124 | 77 |
| 0.35, 0.90 | 117 | - | 61 (63 / 59) | - | 109 | 65 |
| 0.35, 1.15 | 99 | - | 57 (64 / 63) | - | 94 | 56 |
| 0.737, 0.65 / 0.70; 0.35, 0.75 | about 0-3 | - | about 0-1 | - | - | - |

- At (0.737, 0.90), S1 nom splits as 24 clean / 65 contact cells. 13 of the contact cells touched an **external face before
  entry**. 92 S1 clean-entry cells bounced out.
- P_tight / P_loose at (0.737, 0.90): S0 0.80 / 0.31; S0.5 0.80 / 0.33; S1 nom 0.69 / 0.24; S2 0.55 / 0.19.
  At (0.737, 0.75): S0 0.81 vs S1 nom 0.56 (tight).
- Magnus moves the whole window (figures/contact_launch_windows.png: the band sits about 2 deg lower at the same
  speed). So cell-by-cell overlap with S0 (`kept_vs_S0`) is near zero and says nothing. **Compare counts and
  probabilities, not individual cells.**
- **S1 nom >= S0 in only 2 of 80 (h, d, e, mu) combinations**, both at e 0.3, mu 0.2, and both within a few cells (a tie).

### 3.2 Near-miss rescue

The near-miss set holds cells within 2 grid cells (0.1 m/s / 0.5 deg) of a clean-entry cell that are not clean entries
themselves. Fraction of that case's own near-miss set that is still retained (predicted):
- S0: 4.5-6.7 %;
- S0.5: 9-11 %;
- S1 nom: 9-12 %;
- S1 collOnly: 9-12 %.

Backspin collisions roughly **double the rescue of near misses**. This is the real "check" effect at the far rim. But the
same spin loses most clean entries, so the total is lower.

### 3.3 Dependence on e (h 0.737, d 0.90, mean over mu)

| e | S0 cells / P_tight | S1 nom cells / P_tight | S1 airOnly cells |
|---|---|---|---|
| 0.3 | 179 / 0.81 | 151 / 0.85 | 166 |
| 0.45 | 165 | 66 / 0.65 | - |
| 0.6 | 156 / 0.79 | 50 / 0.48 | 150 |
| 0.8 | 154 / 0.79 | 89 / 0.79 | - |

- The spin penalty is **non-monotonic in e**. It is smallest at e 0.3 and largest at e 0.45-0.6, with partial recovery at e 0.8.
  Likely mechanism (interpretation, not separately tested): at e 0.3 the floor rebound is too weak to reach the mouth; at
  e 0.8 the ball makes more contacts inside the CELL, which strip the backspin before the floor kick. mu changes the counts much less than e does.
- Only at e 0.3 does S1 reach the S0 tight probability (0.85 vs 0.81, within noise). This is why e for POLLEN on the HIVE
  skin is the most important unmeasured number here.

### 3.4 Decomposition: airborne Magnus vs collision spin (figures/contact_decomposition.png)

Change in retained cells vs S0, mean over e x mu. interaction = full - air - coll (each as a change vs S0).

| h, d | airborne Magnus only | collision spin only | interaction | full S1 nom |
|---|---|---|---|---|
| 0.737, 0.90 | -10 | -73 | +8 | -75 |
| 0.737, 0.75 | -26 | -72 | +16 | -82 |
| 0.737, 1.15 | -7 | -54 | +4 | -57 |
| 0.35, 0.90 | -8 | -52 | +4 | -56 |
| 0.35, 1.15 | -5 | -43 | +6 | -42 |

- **Collision spin dominates** (predicted): about 90-100 % of the loss.
- The airborne Magnus part is small and negative on this side. Lift makes the descent shallower, and the mouth needs more
  than 60 deg of descent. It is largest at the shortest working distance (0.75 m: -26).
- The interaction is small and positive: a Magnus-shifted path meets the lip at a slightly different spot.

### 3.5 Tilt bounds (h 0.737, e 0.6, mu 0.4)

| d | case | 28.5 deg | 30 deg | 31.5 deg |
|---|---|---|---|---|
| 0.75 | S0 | 107 | 121 | 151 |
| 0.75 | S1 nom | 18 | 19 | 18 |
| 0.90 | S0 | 143 | 156 | 186 |
| 0.90 | S1 nom | 42 | 53 | 53 |

Absolute counts move by up to 20-25 % with tilt. S0 > S1 nom holds at every tilt, so the conclusion is **robust to the
±1.5 deg tilt bound**.

## 4. Answers (all predicted; e, mu, Cl assumed)

**When does contact reliably produce retention?**
- Only as a **far-rim margin next to a clean window**. This is the band where the free path would cross just short of the
  lower lip: 30-60 mm in Part A, at descent of 68 deg or more.
- It is more reliable with lower e, lower speed and steeper descent.
- Near-rim and roof contacts are not reliable (retained fraction 0.03 or less). Contact from the outer faces or roof top
  never retained a ball in Part A.
- With no clean window (descent 64-66 deg, or d 0.65-0.70 m at h 0.737), contact alone gives only small patches. It is
  not a scoring mode to aim for.

**Backspin vs no spin, retention probability (unfavourable side, best aim):**
- Part A (P20, e 0.6): S0 0.89, S0.5 0.86, S1 0.72, S2 0.57.
- Part B (P_tight, h 0.737, d 0.90): S0 0.80, S0.5 0.80, S1 nom 0.69, S2 0.55.
- Over the e x mu grid at (0.737, 0.90), the S1 nom tight probability ranges from about 0.48 (e 0.6) to 0.85 (e 0.3); S0
  ranges 0.79-0.81.
- **More backspin does not always help.** On this side, at the predicted hood spin S of about 1, backspin lowers retention
  except at low e (about 0.3), where it ties. A moderate S of about 0.5 is neutral.
- One shot cannot show repeatability. These are model probabilities under an assumed scatter.

**Airborne Magnus vs collision spin:** collision spin is the main effect: -43 to -73 cells vs -5 to -26 for airborne
Magnus (table 3.4). The collision effect has two opposite parts. It helps at the far rim (near-miss rescue doubles), and it
hurts on the CELL floor (clean entries bounce out). The floor part wins.

## 5. G417 note (docs/01_hive_geometry.md §6)

- docs/01 §6 reads G417 as follows:
  - (C) deliberately launching POLLEN into the HIVE's external bottom, sides or top is likely STRATEGIC: MAJOR FOUL plus
    YELLOW CARD.
  - (H) a genuine miss is not.
- Implication for hypothesis (B): **rim contact during a real scoring attempt is fine**. A **planned bank shot** off the
  roof or outer faces is a G417 risk.
- That plan would not score anyway. Part A external-first retention is 0. In Part B, about 20 % of S1 nom contact-retained
  cells (13 of 65 at 0.737, 0.90) touched an external face before entry. Do not aim for those cells. Treat them as luck
  inside a scatter that is centred on the clean or far-rim window.
- Open: whether a deliberate far-rim graze, where the rim is part of the CELL mouth, counts under (C) or (H). This needs a
  Q&A ruling (user / GDC).

## 6. Assumptions, limits and open questions

- **e, mu and e_t for POLLEN on the HIVE skin are unmeasured** (assumed sweeps). e is the most important input (3.3). A
  drop and spin-bounce test on a real HIVE panel would settle the sign of the S1 effect.
- e is taken as independent of speed. Real foam/plastic balls usually lose e at higher impact speed (not modelled).
- The 3 preloaded NECTAR against the back skin are not modelled. They could absorb back-wall rebounds and reduce the
  backspin floor penalty.
- 2D centre-plane section only. Off-centre entries, side walls, 3D spin axes and sidespin are not modelled.
- The ball's perforations could catch on edges (not modelled; the ball is a rigid smooth sphere).
- The HIVE is rigid and fixed. Panel compliance and HIVE motion are not modelled.
- The trapped criterion is conservative (barrier at the gate low end, spin energy counted). A few slow balls that are
  counted as not retained would in fact settle.
- Pickleball coefficients only set sweep ranges. They are **not** POLLEN data.
- Only the unfavourable side was swept. The favourable side (docs/03) has a far larger clean window, and contact there is
  not studied.
- These are deterministic model sweeps under an assumed scatter. **Repeatability cannot be inferred from one shot.** Any
  field test needs many shots per setting.
- No bug was found in `src/hive.py` or `src/flight.py` (used read-only).
