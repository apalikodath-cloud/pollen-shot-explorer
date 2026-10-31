# PM-001 geometry audit: field, HIVE and CELL

Date: 2026-10-31. Three lenses (field, HIVE, cell). Each had one auditor and one skeptic who re-derived the numbers.
This file only reports. No code was changed by the audit. PM-015 applied the fixes: see section 5 and the Status column.

Labels: CONFIRMED = read in Competition Manual TU07, or in the official CAD via `data/hive_geometry.json`.
derived = computed from CONFIRMED values. ASSUMED = our choice. PREDICTED = model output.
Line numbers are approximate. Other agents were editing `physics.js` and `solver.js` during the audit (PM-013 3D cell classifier).

Scratch scripts and logs were kept outside the repo (not published).

## Earlier `field_check.log` FAIL: resolved

- **423-cell status mismatch:** gone. It came from a 2-vs-3 ordering difference, fixed in commit 64a8537 and in the checker. The shipped `pos_status.b64.txt` now matches the code exactly. Counts: {0: 3180, 1: 567, 2: 882, 3: 132}.
- **6 other-HIVE cells:** still differ. The cause is the 201-point line sampling. Fix 5 below removes them.

## 1. Geometry table

Py = `src/*.py` and `viz/explorer/export_field.py`. JS = `viz/explorer/solver.js`, `physics.js` and `page.html`.

| # | Quantity | Python | JS | Official value (source) | Label | Status |
|---|---|---|---|---|---|---|
| 1 | Frame: x = shot axis, y = pivot axis, red HIVE at y = 0, blue at +y | same | same (page flips y in `W`; `OTHER_Y = -0.6472` is consistent) | CAD | CONFIRMED | OK |
| 2 | Field inner half-width | 1.8009 m | 1.8009 m | about 144 in, CAD official ±1 in (9.1, 9.2). CAD parse A 70.90 in; parse B 70.67 in (1.795 m) | CAD | UNVERIFIED |
| 3 | Field y range | −1.4773 to 2.1245 | same | derived from rows 2 and 4 | derived | OK |
| 4 | Red HIVE offset from the field centre (half spacing) | 0.3236 m | 0.3236 m | Fig 9-10 25.5 in c-c (0.6477). CAD 12.74 in (0.3236) or 12.758 in (0.3241) | CAD | UNVERIFIED |
| 5 | Release grid wall margin | 0.10 m | `pose()` uses 0 (bare wall) | none | ASSUMED | FIXED PM-015 (legality = chassis fit in both; grid margin 0.10 only places grid points) |
| 6 | Release grid | x −1.7009 to 1.6991; nearest row to y = 0 is 0.0227 | uses the export | none | derived | FIXED PM-015 (symmetric, row on y = 0) |
| 7 | A-frame base half-extents | 0.4945 × 0.628 | same | 38.95 × 49.46 in, giving 0.4947 × 0.6281 (9.6.1) | CONFIRMED | OK (0.2 mm) |
| 8 | A-frame keep-out box (base + 0.05 m) | yes | `pose()` yes; page clamp no | legs and feet only; mid-span may be open (CAD) | ASSUMED | UNVERIFIED (PM-015: box = CONFIRMED base, no +0.05; U1 open) |
| 9 | Robot footprint | not checked | page `RHALF` 0.2285, axis-aligned, walls only | 18 × 18 in at start, may expand to 18 × 24 × 29 in (R102, R105) | CONFIRMED | FIXED PM-015 (turned chassis vs walls and base, 18 x 24 option) |
| 10 | Release point relative to robot | centre | centre | team design | ASSUMED | UNVERIFIED (PM-015: offset option, default 0) |
| 11 | Release height | 0.737 m (29 in) | 0.737 | a held ball's centre is ≤ 0.7011 if it must stay inside the size limit | ASSUMED | UNVERIFIED |
| 12 | Pivot height | 1.11633 m | from export | 43.95 in (9.6.1) | CONFIRMED | OK |
| 13 | Tilt, nominal | 30° | 30° | CAD | CONFIRMED | OK |
| 14 | Tilt bounds | 28.5–31.5 (wide 25.5–34.5) | page buttons 28.5 / 31.5 | checklist K1.13 lip 53.5 ± 0.5 in gives 28.80–31.77 (wide, pivot ±1 in: 25.90–34.83) | derived | FIXED PM-015 in geometry, MC clip, page; sweeps deferred (old bounds, labelled) |
| 15 | Lower lip height at 30° | 53.41 in | same | 53.5 ± 0.5 in (K1.13) | CONFIRMED | OK |
| 16 | Upper lip height at 30° | 65.59 in | same | 65.6 in (Fig 9-10) | CONFIRMED | OK |
| 17 | Lowest HIVE point | 30.65 in | same | 30.6 in | CONFIRMED | OK |
| 18 | Cell opening width | 0.508 m (half 0.254) | same | about 20 in (9.6.2); CAD inner 20.21 in | CONFIRMED | OK |
| 19 | Cell opening height | profile h0 0.3556; section 0.35738 (mixed in `hive.py _roof_drop`) | from export | about 14 in (9.6.2); CAD parse B roof 12.50 in, giving 14.00 in | CAD | WRONG, deferred (needs U2 CAD re-parse) |
| 20 | Side-wall (shoulder) height | 0.1933 m | same | Fig 9-11 | CONFIRMED | OK |
| 21 | Cell depth | 0.30556 m | same | about 12 in (9.6.2) | CAD | OK |
| 22 | Roof profile h(s) = 0.3556 − 0.1623·\|s\|/0.254 | `hive.py` | `physics.js` | Fig 9-11 pentagon | CONFIRMED | OK |
| 23 | Ball clearance under the sloped roof | R = 0.0355 | R | R/cos 32.6° = 0.0421 (6.6 mm more) | derived | SUPERSEDED by 3D cell; section option default OFF (PM-015) |
| 24 | Ball radius | 0.0355 m | 0.0355 | about 2.8 in / 7.1 cm (9.8) | CONFIRMED | OK |
| 25 | Gate centre `X_GATE` | 0.401 (fixed) | 0.401 (fixed) | 0.40138 at 30°, s = 0. It moves with tilt (0.369–0.431) and with s (up to 0.433) | derived | WRONG (minor), deferred; 3D cell default |
| 26 | Oblique section offset s_eff = min(0.3 tan ψ, 0.2), applied to the whole section | yes | `physics.js sEff` | the ball is at s ≈ 0 at the gate; offset varies along the path | ASSUMED | SUPERSEDED by 3D cell (exported masks still s_eff, labelled) |
| 27 | Side-wall angle ψ limit | 35.57° | 35.57°; page map tests bin + 2.5 | depends on entry angle and height: 32–82° | PREDICTED | FIXED PM-015 (3D per shot, map exact psi, wording) |
| 28 | Other-HIVE footprint | \|x\| < 0.4945, y 0.39–0.90 (`robustness.py:86` calls it "confirmed") | same | CAD body y 0.381–0.914, plan x −0.639 to +0.510 at 30° (envelope ±0.639); plus R | ASSUMED | FIXED PM-015 (0.6745, 0.3455-0.9495) |
| 29 | Other-HIVE sight-line target | (0, 0) | (0, 0) (`aim` is set but unused) | `FIELD_DATA.md:63`: the aim point (0.401, 0) | derived | FIXED PM-015 (aim point) |
| 30 | Other-HIVE test method | 201 samples; `robustness.py:787` uses `Y > 0.90` | 201 samples | exact segment test | none | FIXED PM-015 (exact, one function) |
| 31 | Unfav/fav mapping (pose_pos = red start, fav = x > 0) | `feasibility.py` `Geometry.make` | same | 10.3.1 | CONFIRMED | OK |
| 32 | Blue alliance / pose_neg mirror on the page | n/a | missing | 9.5: red alliance area on the left from the audience | CONFIRMED | FIXED PM-015 (red/blue toggle) |
| 33 | Status order 1 > 2 > 3 | yes | 2 and 3 both map to beyond_model | `FIELD_DATA.md:62` | none | OK |
| 34 | d table maximum | 1.75 | same | largest release d is 1.7009 | derived | OK (last row unused) |
| 35 | FLOWERS on the perimeter wall | not modelled | not modelled | 4, top opening about 4 in, about 21.5 in high (9.7); positions not in the text | CONFIRMED | UNVERIFIED |
| 36 | Python vs JS sections and constants | — | — | match to ≤ 5e-6 m | derived | OK |

**Counts: 17 OK, 13 WRONG, 6 UNVERIFIED (36 rows).**

After PM-015 (Status column updated): 9 rows FIXED, 2 SUPERSEDED by the PM-013 3D cell, 2 still WRONG (deferred: rows 19, 25), 6 UNVERIFIED.

## 2. Confirmed bugs, ranked

### A. These change the answer (the shot windows)

**1. The s_eff section model is too pessimistic at oblique angles. This is the biggest error.**
- One roof drop at s_eff = min(0.3 tan ψ, 0.2) is applied to the whole section. But the aimed ball is near s = 0 at the lips, where clean or hit is decided.
- Clean counts (PREDICTED, h 0.737, S = 1): the exact per-point offset gives 1.2–2.6× more than s_eff, for example unfav ψ 40, d 1.5: 65 → 169. The two agree at ψ 0.
- `robustness.mc_shots` uses \|y at gate\| instead, so it does not match the maps.
- **Fix:** test each path point against the section at its own offset, s(x) = \|x − x_aim\|·tan ψ, clamped at 0.2565:
  - `src/hive.py` (classify and `_roof_drop` callers)
  - `viz/explorer/physics.js` (`sEff`, `classifyOblique`)
  - `src/robustness.py` (`s_eff`, about line 558, and `mc_shots`, about lines 505–550)
  - then re-export with `export_field.py`
- Or adopt the PM-013 3D cell classifier once it has been reviewed. It is unverified.

**2. Robot position legality is not enforced consistently.**
- `solver.js pose()` accepts \|x\| ≤ 1.8009, the bare wall, but the export grid stops 0.10 m in. 114 of 404 on-wall poses come back ok.
- The page's `rClamp` (`page.html` about lines 1403–1408) ignores heading. At 45° a chassis corner is 0.095 m into the wall.
- Nothing checks the chassis against the A-frame. The 18 in size can grow to 18 × 24 in (R105.A).
- **Fix:**
  - `solver.js pose()`: `inField = |x| <= X_WALL - 0.10 && y >= Y_LO + 0.10 && y <= Y_HI - 0.10`, so it matches `WALL_MARGIN`.
  - Add team parameters: robot length and width (default 0.457 × 0.457, option 0.457 × 0.610), heading, and the release offset from the robot centre (default 0, ASSUMED).
  - In `pose()`, `export_field.field_positions` and `rClamp`, mark a pose illegal when the rotated chassis rectangle crosses a wall. For a square of half-size a at heading θ, the half-extent is a(\|cos θ\| + \|sin θ\|).
  - Keep the A-frame box until the CAD check in U1 below, and label it ASSUMED.

**3. The ball clearance under the sloped roof is 6.6 mm short.**
- A sphere under a 32.6° roof needs R/cos α = 0.0421 m of vertical gap, not 0.0355. This applies at every s (if the apex is a sharp bend, see U3), on the inner roof, the upper lip and the outer roof that far-side balls clear.
- It cuts clean counts by 1–5% (for example psi 0: 59 → 56).
- **Fix:** in `src/hive.py` (inside polygon and roof segments, about lines 190–228) and in `physics.js`, lower the roof by an extra R(1/cos α − 1) = 0.00663 m wherever the roof is sloped.

**4. The tilt bounds are not the exact solve of the checklist.**
- **Fix:** new values are low 28.80, high 31.77, low_wide 25.90, high_wide 34.83. Apply them in:
  - `data/hive_geometry.json` `poses.*.tilt_deg` (lines 24–27 and 460–463)
  - `src/feasibility.py` `CORE_GEOMS` / `WIDE_GEOMS` (lines 398–401)
  - `src/robustness.py:493` `_clip_norm(..., 28.5, 31.5, ...)`
  - `src/contact.py:1239`
  - `viz/explorer/export_explorer.py:30` keys
  - `page.html:2048` buttons
  - `docs/01_hive_geometry.md` lines 40 and 95–96
- Then re-export. The effect is about 0.3° (about 2.5 mm at the lip).

### B. These change a flag shown next to the answer

**5. The other-HIVE flag uses the wrong line, the wrong box and three different rules.**
- An exact test to the aim point changes 553 status-0 cells. On the near side, 445 flags are false; on the far side, 108 blocked cells are missed.
- **Fix:** write one shared function, `sight_blocked(x, y)`, as an exact segment-against-rectangle test (Liang–Barsky) from (x, y) to (X_GATE, 0).
  - Box: \|x\| < 0.6745, y 0.3455–0.9495. That is the ±0.639 plan envelope plus R, and CAD body y 0.381–0.914 plus R.
  - Use it in `export_field.py` (about lines 193–198), `solver.js` (about lines 56–63) and `robustness.py:787` (replacing `Y > 0.90`).
  - Change the `robustness.py:86` label to ASSUMED/derived.
  - Later: test the 3D flight against the other HIVE's height profile. Far-side balls pass above it.

**6. The side-wall flag uses one angle and a bin edge on the page.**
- The page map (`page.html` about line 1127) flags 168 extra cells with ψ 32.5–35.6 because it tests the bin edge.
- The real limit depends on the entry angle and the entry height in the mouth (32–82°). So 35.57° is not conservative for low, shallow near-side entries, and too strict on the far side.
- **Fix:**
  - On the page, test the exact ψ (`ps.psi`), not `bin + 2.5`.
  - In `solver.js` / `export_field.py`, compute the flag per shot by checking \|y(x)\| < 0.2185 along the path inside the cell, or let the 3D classifier decide.
  - Reword `FIELD_DATA.md:23,85` and `solver.js:84`: "near-side estimate; far side not checked", not "window optimistic".

### C. Interpretation and small items

**7. The page does not show alliance or pose.**
- **Fix:**
  - Rename the labels to "mouth side (fav)" and "back side (unfav)".
  - Add a red/blue toggle that mirrors x and y. For blue, the other HIVE and Y_LO/Y_HI swap sides.
  - State that the sides swap on every tip.
  - In `FIELD_DATA.md:35`, change "Mirror x for pose_neg" to "mirror x; for the blue HIVE also mirror y".

**8. The release grid is asymmetric.**
- **Fix:** in `export_field.py:185–186` (and `robustness.py:719`), use `xs = k·0.05` for \|x\| ≤ 1.70 and `ys = 0 ± k·0.05`, clipped to the walls minus 0.10. Or have the page snap to the exact ψ.

**9. `X_GATE` is held fixed.**
- **Fix:** take the gate centre from the section in use (`h.gate`) for the aim point and ψ. This goes away with fix 1.

**10. Two values for the opening height are mixed (table row 19).**
- **Fix:** after U2 below, set `up_roof_inner` / `down_roof_inner` w in `data/hive_geometry.json` to the rechecked CAD value (0.3175 if parse B is right), so the section and the profile h0 agree. Then re-export.

**11. Wording.**
- `FIELD_DATA.md:33` and the `export_field.py:330` text say 0.6477. The code uses 0.6472. Keep the code value and fix the text (see U2).

## 3. Refuted or not a bug (no change)

- **HIVE spacing:** the auditor's fix to 0.32385 is wrong. The CAD is the official model.
- **The 637 "chassis through wall" cells:** these assume the release point is at the robot centre. A shooter on the robot's edge can release 0.10 m from the wall. It is covered by the release-offset parameter in fix 2.
- **Page `OTHER_Y` sign:** consistent with the page's flipped y.
- **G417 foul risk:** an accidental bump is not a foul (example H). The limit is physical.
- **pose_pos / fav mapping, heights, opening width, Python-vs-JS geometry:** all match.
- **Near side behind the aim plane:** always illegal or beyond_model, never ok.

## 4. UNSURE items and how to settle them

| # | Item | How to settle |
|---|---|---|
| U1 | A-frame keep-out: is the mid-span of the base open to a robot? Do the foot bars at x = ±0.495 run along y? | Read the leg and foot-bar solids in the official CAD at heights 0–0.74 m. Replace the box with their footprints (plus robot half-size). |
| U2 | Two CAD parses disagree: wall 70.90 vs 70.67 in; HIVE half-spacing 12.74 vs 12.758 in; floor −1.470 vs −1.50 in; roof inner 12.60 vs 12.50 in | Re-parse the STEP once with one script, measure the inner faces directly, and record the result in `data/hive_geometry.json` with its source. Then apply fix 10 and set rows 2 and 4. |
| U3 | Is the pentagon roof apex sharp? This decides whether the 6.6 mm applies at s = 0. | Look at the roof apex in the CAD section (a fillet radius above about 40 mm removes it at s = 0). |
| U4 | Release offset and real footprint after expansion | Ask the team: where the ball leaves the robot relative to the chassis centre, and the expanded size. |
| U5 | Release height 0.737 m vs a held ball inside the size limit (0.7011) | Check R105 wording with the team or the Q&A. Run both heights until then. |
| U6 | POLLEN size variation ("may vary in size") | The sentence was not found by the skeptic. Search TU07 again. If present, add a ±R sweep. |
| U7 | FLOWER positions on the perimeter wall | Read them from the field CAD. Low impact (wall-hugging spots only). |
| U8 | PM-013 3D cell classifier in `physics.js` | Review it against fix 1 and fix 3 before using it as the side-wall and s_eff fix. |

## 5. PM-015 fix status (2026-10-31)

The PM-013 3D cell model (default in the live solver) is the authority where it covers an item.
Shared code: `src/field_geom.py` (Python) and its twin in `viz/explorer/solver.js`; tests `tests/test_field_geom.py`
(dense references and a node cross-check), `tests/check_field_export.py` (own implementation).

| Fix | Status | What was done / why not |
|---|---|---|
| 1 s_eff section model | superseded by 3D cell | the 3D cell offsets every path point. The exported masks stay section-model and are labelled so. |
| 2 robot legality | fixed | one footprint function (turned chassis vs walls and the CONFIRMED base 38.95 x 49.46 in, optional 18 x 24 in, release offset default 0 ASSUMED) in `solver.pose()`, `export_field.field_positions`, `robustness.field_grid`, page clamp and drag; page shows "robot overlaps wall/HIVE base". |
| 3 sloped-roof clearance | superseded by 3D cell | the 3D cell includes it. The section model has an option (`Hive.from_json(roof_clearance=True)`, `q.roofClear`) that lowers the roof 0.00663 m, default OFF. At the default pose: section clean cells 290 -> 278 (twin 331 -> 320). |
| 4 tilt bounds | fixed, sweeps deferred | 28.80-31.77 (wide 25.90-34.83) in `data/hive_geometry.json`, `feasibility.TILT_BOUNDS`, the MC clip, page text. The precomputed sweeps (feasibility, shooter_spec, contact, explorer export) keep 28.5 / 31.5 via `SWEEP_TILT`, labelled "old bound": the re-sweep takes hours (shooter_spec alone 27 runs of 10-14 min). |
| 5 other-HIVE flag | fixed | exact Liang-Barsky test from the release point to the aim point against the 0.6745 / 0.3455-0.9495 box, one function in Python and JS; 201-point sampling and the Y > 0.90 rule removed. |
| 6 side-wall flag | fixed | 3D cell: per shot from the path (`shot().sideWall`); page map: exact psi; wording "near-side estimate; far side not checked". |
| 7 alliance | fixed | page red/blue toggle (mirror x and y), "mouth side (favourable)" / "back side (unfavourable)", note that the sides swap on each tip. The 3D scene is not mirrored. |
| 8 grid | fixed | x symmetric about 0, a row on y = 0 (69 x 68). |
| 9 X_GATE fixed | deferred | goes away with the 3D cell; the section model keeps 0.401. |
| 10 opening height | deferred | needs the U2 CAD re-parse. |
| 11 wording 0.6477 | fixed | text says 0.6472 (CAD). |

Open: U1-U8 unchanged. HIVE half-spacing stays 0.3236 (CAD), not 0.32385. The field data under
`viz/explorer/data/` is gitignored; it was regenerated locally (status counts {0: 2262, 1: 1760, 2: 588, 3: 82}).
