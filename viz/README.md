# viz/: shot videos, field map and web replay

The web pages have their own folders and notes: `explorer/` (the 3D explorer and the site build, see
`explorer/HOSTING.md` and `explorer/FIELD_DATA.md`), `flow/` (CFD flow pages, `flow/README.md`) and `measure/`
(measurement kit, `measure/README.md`). This file covers the rest of `viz/`.

This folder holds side-view animations of a backspinning POLLEN ball flying toward the
**upward-facing HIVE CELL**, each with a no-spin twin launched at the same speed, angle and
release point. Nothing in here is measured:

- Real-backend output is **PREDICTED with uncalibrated aero** (Cd, Cl and spin decay are
  literature-bounded assumptions from `data/aero_params.json`).
- DEMO output uses **placeholder geometry**.

Every frame carries one of these two labels. The file format is in `viz/shots.schema.md`.

Only `viz/` is written. The scripts import `src/flight.py` and `src/hive.py` read-only, set
`sys.dont_write_bytecode`, and never write into `src/`, `data/`, `docs/`, `figures/` or `tests/`.

## Requirements

You need Python 3.13 with numpy, scipy, matplotlib and Pillow. The MP4 encoder comes from
imageio-ffmpeg:

```
python -m pip install --user imageio-ffmpeg
```

Without it the GIF and PNG outputs are still written, and you get a warning. Run every
command below from the repo root.

## Regenerate everything (real backend, once src/ and data/ change)

```
python viz/make_shots.py                                   # -> viz/shots.json (backend: auto -> real)
python viz/make_shots.py --sweep-map viz/out/map_sweep.csv # same, plus a coarse release-point sweep
python viz/render_video.py viz/shots.json --map viz/out/map_sweep.csv
python viz/export_web.py viz/shots.json --html viz/replay.html
```

These commands produce:

- `viz/out/<id>.mp4`: H.264, 1280x720, 30 fps.
- `viz/out/<id>.gif`: 800 px wide, about 15 fps (a copy of the MP4; not committed, see `.gitignore`).
- `viz/out/<id>_apex.png` and `viz/out/<id>_end.png`: stills.
- `viz/out/field_map.png`.
- `viz/web_data.json` and `viz/replay.html`: a self-contained canvas replay with a shot
  selector, play/pause, a slow-motion control and a scrubber.

**Render sequentially.** Do not run two `render_video.py` processes at the same time. One run
crashed with `OSError: [Errno 22]` on the ffmpeg pipe while another render was running, and
the same shot rendered fine when run alone.

### Your own shot list

```
python viz/make_shots.py --cases my_cases.json --out viz/shots.json
```

The default list is `viz/cases_default.json`. Each case takes these fields:

- `id`, `title`, `pose` (`pose_pos` / `pose_neg`).
- `side`: `favorable` / `unfavorable`, or the shooter side `neg` / `pos`.
- `release: [x, z]` in the HIVE frame, in metres. You can instead give `distance` + `release_z`.
- `v` (m/s) and `elev_deg`.
- Spin as either `S` (omega R / v) or `spin_rpm` (+ = backspin).
- `aero_set`: `low`, `nominal` or `high`.

### Field map from the feasibility analysis

`src/feasibility.py` writes `data/clean_feasibility_map.csv`, one row per
(h, d) with columns `case, role, S, Cl, Cd, k, geometry, h, d, v_cap, n_clean, ...` and `#`
comment lines at the top. `render_video.py` reads this format directly:

```
python viz/render_video.py viz/shots.json --map data/clean_feasibility_map.csv --map-only --map-name feas_unfav.png
python viz/render_video.py viz/shots.json --map data/clean_feasibility_map.csv --map-only --map-side favorable --map-name feas_fav.png
python viz/render_video.py viz/shots.json --map data/clean_feasibility_map.csv --map-only --map-filter case=S1_Clnominal --map-filter v_cap=11.0
```

The defaults for that file:

- **Rows kept:** `geometry = unfav_t30` (or `fav_t30` with `--map-side favorable`), and the
  lowest `v_cap` (the hood-limited one).
- **Panels:** one per `case`, with up to 4 panels. Pick others with `--map-filter case=...`.
- **Colour:** `n_clean`, the number of clean (v, elevation) grid cells.
- **x axis:** the release point is drawn at x = -d, which is the feasibility shot frame. Its HIVE is `pose_pos` when unfavourable and `pose_neg` when favourable.

Any other CSV works if you name its columns: `--map-x`, `--map-z`, `--map-value` (an
outcome string or a number) and `--map-facet`. The parser was tested on a synthetic file
with this column layout, not on real output, because the real CSV did not exist yet when
this was written. If the real column names differ, use those flags.

### Spin-dependent rim-assisted entries (not implemented yet)

`outcome` is currently `clean`, `hit:<segment>` or `miss`. The flight is drawn up to the first
contact, and these videos have no bounce model. The bounce study lives in `src/contact.py`
(`docs/05_contact.md`) and is not wired into the videos. Wiring it in would mean:

1. `make_shots.truncate()` continues the drawn path through the contact sequence.
2. `outcome = "rim-assisted"` is written. Renderers already colour and label it as an entry, and
   the map counts it as entered.
3. The banner keeps `PREDICTED`.

None of this is wired yet.

## DEMO run (no src/ or data/ needed)

```
python viz/make_shots.py --mode demo --sweep-map viz/demo/out/map_sweep.csv   # -> viz/demo/shots.json
python viz/render_video.py viz/demo/shots.json --map viz/demo/out/map_sweep.csv
python viz/export_web.py viz/demo/shots.json --html viz/demo/replay.html
```

DEMO uses a fake tilted-box HIVE and its own RK4 integrator. Every frame, still, map and web
page shows **"DEMO — placeholder geometry, not results"**. Do not quote any DEMO number.

## What a frame shows

- Tiles and the perimeter wall.
- The HIVE section in the shot's pose. The upward CELL is green, its scored ball-centre zone is
  shaded, and the A-frame legs are dotted because they are projected into this plane.
- A schematic robot, 18 in wide (R102).
- The ball at true size. Its marker line turns at the **true spin rate slowed by the same factor
  as time**, and the slow-motion factor is chosen automatically so the marker turns at most 30° per frame.
- The no-spin twin, drawn as a grey ghost.
- Velocity arrows (0.06 m per m/s) and Magnus-acceleration arrows (0.25 m per m/s²; g is
  drawn at the same scale for comparison).
- A follow-cam inset 0.5 m wide.
- A HUD with:
  - t, the slow-motion factor, speed, spin rpm and S;
  - the Magnus acceleration in m/s² and in g;
  - the apex (or "not reached before the flight ends");
  - "mid-air horizontal reversal: yes/no";
  - the outcome with the entry angle (descent, or "still rising");
  - the twin outcome.

## Current default cases (all PREDICTED, uncalibrated, not optimised)

These videos were made with the 2D HIVE section model (`src/hive.py`) and `data/aero_params.json`. The
explorer now judges shots against the 3D CELL (`src/cell3d.py`) with the aero in `research/params_lit.json`,
so use the explorer, not these videos, for current numbers. Release height 0.40 m is assumed, and S = 1 is the ideal hood. Whether the launcher can deliver
these exact (v, S) pairs is not checked here.

| id | pose / side | release, v, elev | aero | spin shot | no-spin twin |
|---|---|---|---|---|---|
| U1_pospose_unfav_high | pose_pos, unfavourable | (-1.2, 0.40), 8.0 m/s, 76° | high (optimistic) | clean (77° descent) | miss |
| U2_pospose_unfav_nominal | pose_pos, unfavourable | (-1.0, 0.40), 7.5 m/s, 80° | nominal | hit up_roof_outer | clean |
| F1_pospose_fav_nominal | pose_pos, favourable | (+1.4, 0.40), 6.5 m/s, 55° | nominal | clean, still rising 36° | hit up_lower_lip |
| U3_negpose_unfav_high | pose_neg, unfavourable | mirror of U1 | high | clean | miss |

The cases were picked to show the spin effect in both directions. **U2 shows backspin
making a shot worse**, so they are not evidence that more backspin always helps. None of the
shots shows a mid-air horizontal reversal. Each one is a single deterministic trajectory and
says nothing about repeatability.

## Files

| file | what |
|---|---|
| `make_shots.py` | Builds `shots.json`. Real backend (src.flight + src.hive), DEMO fallback, optional sweep CSV. |
| `cases_default.json` | The default real cases. |
| `render_video.py` | MP4 + GIF + apex/end PNGs per shot, plus the field-map still. |
| `export_web.py` | `web_data.json` (integer arrays) plus the optional `replay.html`. |
| `shots.schema.md` | The data format and provenance labels. |
| `shots.json`, `web_data.json`, `replay.html`, `out/` | The current PREDICTED outputs. |
| `demo/` | The DEMO outputs, which use placeholder geometry. |
| `hero_search.py`, `hero/` | The far-side backspin shot `HERO_backspin_d175` and its no-spin twin `TWIN_nospin_d175` (cases, `shots.json`, videos; see `docs/08_shooter_spec.md`). |
| `explorer/`, `flow/`, `measure/` | The web pages; see the notes at the top of this file. |
