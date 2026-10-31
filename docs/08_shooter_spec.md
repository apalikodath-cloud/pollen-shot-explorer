# 08: Shooter design targets (what to CAD to)

Every number in this document is a model prediction unless it is marked otherwise.

Labels used: PREDICTED (model output), ASSUMED (a modelling choice), USER (given by the team),
CONFIRMED (from official CAD), derived (computed from CONFIRMED / USER inputs).

Sources:
- Model: `src/shooter_spec.py` and `src/spec_figs.py`. Data: `data/spec_*.csv`. Figures: `figures/spec_*.png`.
- Aero: literature-graded ranges in `research/params_lit.json`. Nothing about POLLEN has been measured.
- Model setup (PM-019 re-sweep, the same as the live solver in `viz/explorer/`): clean entry is judged against
  the 3D CELL of `src/cell3d.py` (side walls + pentagon roof, built from the CONFIRMED tilt-30 section), air
  density 1.2041 kg/m^3 (derived, still air), HIVE tilt 30° (CONFIRMED) with the derived tipped bounds
  28.80° / 31.77°. Before PM-019 the tables came from the 2D section model at rho 1.20 and tilts 28.5 / 31.5;
  the same raster pipeline agrees with an exact 3D classification on 533 of 537 cross-checked cells
  (`data/clean_crosscheck.csv`, docs/03 §1.7), and every disagreement is on the safe side (sweep says not
  clean, exact says clean; PREDICTED, model vs model).
- `figures/spec_*.png` were not re-drawn in PM-019; they still show the pre-PM-019 section-model sweep.

## 1. Headline

The question is whether the ball can drop into the upward CELL from the unfavourable side **without touching
anything first** (clean entry, hypothesis A).

**It can, but only as a precision shot.**
- **The window is a long diagonal band.** At each release point, the shots that go in form a band in
  exit-speed / launch-elevation space (see `figures/spec_windows_*.png`).
- **Along the band it is wide.** Many speed and angle pairs work (for example 6.5–10.5 m/s at 80–86° at
  h 0.737, d 0.75, or 7–10.5 m/s at 72–82° at h 0.5, d 1.75, no spin; 10.5 m/s is the top of the search grid).
  PREDICTED.
- **Across the band it is narrow.** At the most forgiving spot (h 0.737, d 0.75) the median width is about
  0.3–0.55 m/s at a fixed angle, or 0.3–0.5° at a fixed speed, over all aero cases and spins 0–1.5
  (0.15–0.2 m/s at d 0.8). PREDICTED.
- **Unknown aero moves the band.** Changing Cd, Cl or spin decay within their literature ranges moves the band
  by up to about 1.4 m/s at a fixed angle (81°, backspin S 1; about 0.65 m/s without spin), or about 2° at a
  fixed speed (8 m/s, S 1; about 1.45° without spin). That is more than the band's own width. PREDICTED.
- **No fixed shot works for every case.** No single (speed, angle) is clean under every aero case at once
  (`data/spec_robust.csv` has 0 robust cells).
- **So the shooter must be tuned on the field, then hold that tune precisely.**
- **HIVE tilt matters much less.** Moving the tilt between the derived bounds 28.80° and 31.77° shifts the band
  centre by at most about 0.1 m/s at a fixed angle, or 0.1° at a fixed speed (h 0.737, d 0.75; PREDICTED). It
  mostly moves the band's low-speed end: 335 / 378 / 437 clean cells at tilt 28.80 / 30 / 31.77, no spin.

## 2. Backspin: what it does here

- **It is not required for clean entry.** No-spin windows exist at the same release points.
- **It moves the band.** At the same hood angle, backspin S 0.5–1.0 needs about 0.7–1.0 m/s more exit speed
  (81° at h 0.737, d 0.75; 75.6° at h 0.5, d 1.75). At the same speed, it needs about 1.8–2.3° less elevation.
  PREDICTED.
- **It trades one tolerance for another** (h 0.737, d 0.75, nominal aero, PREDICTED). It makes the speed window
  at a fixed angle wider (median 0.35–0.425 m/s with S 0.5–1 vs 0.30 m/s no-spin twin). It makes the angle
  window at a fixed speed narrower (0.4° vs 0.5° no-spin twin). Its largest all-clean square is one cell larger
  (4×4 cells = ±0.075 m/s × ±0.15° with S 0.5–1, vs 3×3 = ±0.05 m/s × ±0.1° for the no-spin twin). It also
  has fewer clean cells in total (300 at S 0.5, 292 at S 1, vs 378 no-spin twin). It is not a free gain, and
  it does not help on its own against the unknown aero (0 robust cells either way).
- **S 1.0 and S 1.5 give identical results in this model.** This is ASSUMED behaviour of the lift law: lift
  stops growing at Cl_max = 0.25 once S is about 0.7 or more (nominal literature c1 = 0.35). Above that, extra
  spin changes nothing here. This is a model limit, not a measured fact.

## 3. CAD card (PREDICTED; the unfavourable side)

| Item | Target | Why |
|---|---|---|
| Release height (ball centre) | as high as the robot allows; 0.65–0.737 m | Higher release = wider windows. 0.737 m is the ASSUMED R105 height limit (docs/01). |
| Release distance d | 0.75–0.85 m from the HIVE pivot plane | Most forgiving zone. Without spin d ≤ 0.70 m is blocked at h ≥ 0.35 m (d ≤ 0.75 m at h 0.2). Far shots (d 1.2–1.75 m) work but the band is about 3× thinner. |
| Hood / launch elevation | about 81° (no spin; the fixed-hood fit at h 0.737, d 0.75 is 80.9°), about 80.5–81.5° (backspin S 0.5–1, band centre at 7.5–8 m/s) | Centre of the band at that spot. |
| Elevation adjustment | ±2° (shims or a lead-screw stop) | Lets you re-centre after the real Cd, Cl and spin are known. |
| Exit-speed range | 6.5–9.1 m/s, closed-loop wheel speed | At 81° it covers every aero case and tilt for spin 0–1 except Cl high with backspin, whose band ends at 80.6° (at 80.5° it needs 8.7–10.5 m/s). |
| 98 mm wheel rpm for 6.5–9.0 m/s | 3020–4180 rpm at v/u 0.42; 4220–5850 at v/u 0.30; 5070–7020 at v/u 0.25; 2530–3510 at v/u 0.50 | v/u (exit speed ÷ wheel surface speed) is unknown, grade C. Size the motor for the 0.25 case. |
| Exit spin if backspin is used | S 0.5–1.0 = about 900–2400 rpm on the ball at 6.5–9 m/s | Optional (§2). |
| **Shot-to-shot repeatability after tuning** | **no spin: exit speed ±0.05 m/s (about ±0.6 %) and elevation ±0.1° together** (backspin S 0.5–1: ±0.075 m/s and ±0.15°) | This is the real requirement. It is the largest clean square at the best spot (h 0.737, d 0.75; d 0.8 gives the same): 3×3 cells of 0.05 m/s × 0.1° without spin, 4×4 with backspin. Nominal aero, tilt 30. PREDICTED; before PM-019 the no-spin square was 4×4. |

Fixed hood held only to ±0.2° (no spin, every aero case × tilt 28.80/30/31.77): the per-case speed window at
the best spot shrinks to a single 0.05 m/s grid cell (hood 80.9°, speed tuned per case over 6.7–7.4 m/s;
`data/spec_tunable.csv`). With backspin no hood angle works for every case even at ±0.2°. At ±0.5° no hood
angle works with or without spin. **Angle repeatability matters as much as speed repeatability.**

## 4. The far-side demo shot (video)

`viz/hero/`: HERO_backspin_d175 and its no-spin twin TWIN_nospin_d175.

| Input | Value |
|---|---|
| Release distance d | 1.75 m |
| Release height h | 0.5 m |
| Exit speed | 8.45 m/s |
| Elevation | 75.6° |
| Backspin | S 1.0, 2273 rpm |
| Aero | nominal literature |

Results (re-checked in the PM-019 sweep cache, 3D cell, rho 1.2041; the video in `viz/hero/` itself was
rendered before PM-019):
- **Backspin shot:** the grid cell at 8.45 m/s, 75.6° is clean, with about 76° descent and 24 mm clearance.
  PREDICTED.
- **No-spin twin, same launch:** not clean. This is not "backspin is better". At that release point the no-spin
  band lies about 2.25° higher (8.45 m/s needs about 77.85° without spin); a no-spin shot at its own angle also
  enters (§2).
- **Tolerance:** the largest all-clean square at this point is 2×2 cells, about ±0.025 m/s × ±0.05°, with or
  without spin (before PM-019: about ±0.05 m/s × ±0.1°). It is a demonstration, not a design point.
- **Repeatability:** it is one simulated shot, so no repeatability claim.

## 5. Measure these first (they set where the band is)

1. **Shot-to-shot exit speed and elevation scatter** of the prototype. Use high-speed video at 240 fps or
   more, 20+ shots. If the scatter is larger than §3, clean entry will not be reliable. Then the contact /
   rim-bounce route (hypothesis B, docs/05) has to carry the design.
2. **v/u:** measured exit speed ÷ wheel surface speed at 3–4 wheel speeds.
3. **Exit spin S:** mark the ball and count frames per turn.
4. **Cd and spin lift of POLLEN:** a drop test, plus flight video at two spin rates. Cd 0.33 vs 0.9 and
   Cl low vs high are the largest band shifts (about 1.5–2° at a fixed speed, PREDICTED).
5. **The real HIVE tilt** on the field element (CONFIRMED CAD value: 30°).

## 6. Files

| File | What it holds |
|---|---|
| `data/spec_nominal.csv` | Per (side, S, h, d): largest clean square under nominal aero, tilt 30. |
| `data/spec_robust.csv` | Same, but clean under every aero case × tilt 28.80/30/31.77. Empty on the unfavourable side. |
| `data/spec_tunable.csv` | Fixed hood held to ±0.2 / ±0.5°, speed tuned per case: hood angle, the speed range to cover, and the tolerance. |
| `figures/spec_windows_h737_d075.png`, `spec_windows_h500_d175.png` | The clean bands for each aero/tilt case. This is the key picture. Not re-drawn in PM-019 (pre-PM-019 section model). |
| `figures/spec_targets_h*.png`, `spec_tolerance.png` | Nominal-aero targets vs d. These fall back to nominal because the robust set is empty. |

Reproduce:

```
python -B -m src.shooter_spec                  # 27 aero x spin jobs; about 1 h with 8 workers (PM-019, 3D cell)
python -B -m src.shooter_spec --extract-only   # CSVs from cache
python -B -m src.spec_figs
```
