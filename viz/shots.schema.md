# viz/shots.json: format (version 1)

`viz/make_shots.py` writes this file. `viz/render_video.py` (MP4, GIF and PNG stills) and
`viz/export_web.py` (web_data.json and replay.html) read it. Everything is in SI units (m, s,
m/s, N, rad), except that spin is also given in rpm, as noted. The view is a 2-D side view in
the HIVE tipping plane.

## Provenance labels used below

| label | meaning |
|---|---|
| **confirmed** | taken from an official source; the source and URL are in `data/hive_geometry.json` or `data/aero_params.json` |
| **user** | stated by the user (HANDOFF.md section 2) |
| **assumed** | chosen by us with no measurement behind it (release heights, aero bounds, retention after entry) |
| **derived** | computed from confirmed or user inputs (S = omega R / v, rpm, the HIVE section polygon) |
| **predicted** | output of the uncalibrated simulation: every trajectory, outcome and apex in this file |
| **DEMO** | placeholder geometry and physics, not results (`meta.source == "demo"`) |

No field in this file is a measurement.

## Frame (HIVE frame)

- `x` is horizontal in the HIVE tipping plane. `x = 0` is directly below the pivot. `z` is the
  height above the tiles, pointing up.
- `pose_pos` means the upward-facing CELL leans to `+x`. `pose_neg` is its exact mirror. The
  field `favorable_side` (`"pos"` or `"neg"`) gives the side whose shooter faces the CELL mouth.
- A shot fired from the `-x` side travels toward `+x`, and the reverse.
- Spin is pure backspin about the y axis. `spin_angle` is the angle of the marker drawn on the
  ball, measured counter-clockwise in the x-z view, so backspin while moving `+x` turns
  counter-clockwise. In formula form, `spin_angle = -integral(omega_y dt)`.
- Note the frame difference with `src/feasibility.py`. Its CSVs use a shot frame in which the
  shooter is always at `x = -d`, `h` is the release height, unfavourable means `pose_pos`, and
  favourable means `pose_neg`. `render_video.py --map` converts `d` to that frame.

## Top level

```
{ "meta": {...}, "hive": {...}, "hives": {"pose_pos": {...}, "pose_neg": {...}}, "shots": [ {...}, ... ] }
```

`hive` is a copy of `hives[<pose of the first shot>]`, kept for single-pose readers.

### meta

| key | type | meaning |
|---|---|---|
| `source` | `"predicted"` or `"demo"` | Which backend produced the file. Renderers stamp `PREDICTED, uncalibrated aero (not measured)` or `DEMO — placeholder geometry, not results` on every frame. |
| `aero_set` | list of str | The aero bounds used by the shots (`low` / `nominal` / `high` from `data/aero_params.json`). **assumed** |
| `geometry_status` | str | The provenance of the HIVE section. |
| `generated` | ISO time | Local time the file was written. |
| `generator` | str | The script, plus the src functions it called. |
| `units` | str | The units, in words. |
| `notes` | str | Caveats, which every viewer should keep. |
| `labels` | {str: str} | The provenance label for each kind of number. |
| `dt_out` | float, s | The sample step of the shot arrays (0.002 s, resampled from dense output). |

### hives.<pose>

| key | type | meaning |
|---|---|---|
| `pose` | str | `pose_pos` or `pose_neg`. |
| `tilt_deg` | float | The CELL tilt. Nominal 30° is **confirmed** (TU07 Fig 9-10 plus CAD). The bounds are in `data/hive_geometry.json`. |
| `pivot` | [x, z] | The pivot point. `z = 1.11633 m` is **confirmed** (TU07 9.6.1). |
| `segments` | [[x0, z0, x1, z1, name], ...] | The solid section edges, **derived** from CAD. The ball centre may not come within R of these. |
| `mouth` | [x0, z0, x1, z1] | The mouth line of the upward CELL. |
| `inside` | [[x, z], ...] | The polygon of the scored ball-centre zone (the shaded area). |
| `up_cell` | [name, ...] | The segment names that belong to the upward CELL. These are drawn in green. |
| `projected` | [name, ...] | Segments that are not in this plane (A-frame legs). They are drawn dotted. |
| `static` | [name, ...] | Frame parts that do not tip. |
| `favorable_side` | `"pos"` or `"neg"` | The side whose shooter faces the mouth. |
| `x_wall` | float, m | The inner face of the perimeter wall (±1.8009 m, CAD). |
| `status` | str | Provenance text. In DEMO files this reads `PLACEHOLDER`. |

### shots[i]

| key | type | label | meaning |
|---|---|---|---|
| `id`, `title` | str | | Used in file names and headings. |
| `pose` | str | | Which HIVE pose. |
| `side` | `favorable` / `unfavorable` | | The shooter side relative to the CELL mouth. |
| `shooter_side` | `neg` / `pos` | | The side of x the shooter fires from. |
| `release` | [x, z] m | **assumed** | The ball-centre release point. |
| `v` | m/s | **assumed** (chosen case) | The launch speed. |
| `elev_deg` | deg | **assumed** | The launch elevation. |
| `spin_rpm` | rpm | **derived** from S | The backspin at release. |
| `S` | - | **assumed** / derived | The spin parameter omega R / v at release. S = 1 is the ideal no-slip hood (HANDOFF 4C). |
| `aero_set` | str | **assumed** | One of `low`, `nominal` or `high`, from `data/aero_params.json`. |
| `aero_desc` | str | | Cd, Cl law and spin decay, in words. |
| `mass`, `radius` | kg, m | confirmed/derived (see `data/aero_params.json`) | The ball properties used. |
| `outcome` | str | **predicted** | One of `clean`, `hit:<segment name>` or `miss`. The value `rim-assisted` is reserved and not produced yet (see README). |
| `end_note` | str | | Why the drawn flight stops. |
| `entry_angle_deg` | float or null | **predicted** | The angle at mouth crossing, from `hive.classify_detail`. **+ means falling, - means still rising.** |
| `min_clearance` | m or null | **predicted** | The smallest ball-surface clearance before the event. |
| `horizontal_reversal` | bool | **predicted** | True if vx changes sign during the drawn (truncated) flight. That would be a true mid-air hook. |
| `horizontal_reversal_untruncated` | bool | | The same test over the full integration, which runs past contact. Kept for reference only. |
| `apex` | {t, x, z, vx, vz, spin_rpm, S, F_M:[x, z]} or null | **predicted** | The apex of the full integration. |
| `apex_reached` | bool | | False if the apex lies after the drawn flight ends, for example when the ball enters while still rising. |
| `t`, `x`, `z`, `vx`, `vz` | arrays | **predicted** | The ball-centre state, sampled every `dt_out` and cut at the end event. |
| `spin_angle` | array, rad | **predicted** | The cumulative marker angle (see Frame). |
| `spin_rpm_t`, `S_t` | arrays | **predicted** | The spin and S along the flight, with spin decay included. |
| `FMx`, `FMz` | arrays, N | **predicted** | The Magnus force. |
| `FDx`, `FDz` | arrays, N | **predicted** | The drag force. |
| `twin_no_spin` | {t, x, z, outcome, end_note, horizontal_reversal} | **predicted** | The same release, v and elevation with spin = 0, cut the same way. |

### How the drawn flight is cut

1. The sampled flight is cut in one of three ways:
   - **hit**: at the first solid contact, refined linearly. There is no bounce or rim model here.
   - **clean**: when the ball centre is inside the CELL polygon and has touched nothing. The flight is drawn
     until its first interior contact or until 0.3 s after entry. Retention is **assumed**.
   - **miss**: at the perimeter wall or at tile height (ball centre at z = R).
2. The outcome itself comes from `src/hive.classify_detail` on the full trajectory, using the
   CAD-derived and radius-inflated HIVE. The DEMO backend uses its own placeholder classifier.

## web_data.json (from export_web.py)

`web_data.json` is a compact copy of the same data, with only integers in its arrays and samples every 10 ms by default:

- lengths and positions in mm;
- times in ms;
- `a` (spin angle) in mrad;
- velocities in mm/s;
- `amx` and `amz` (Magnus acceleration) in mm/s²;
- `rpm` as an integer.

Each hive keeps the keys `names`, `seg` (in mm), `up` and `proj` (index lists), `mouth`, `inside`, `pivot`, `x_wall`, `tilt_deg`, `favorable_side` and `status`. `meta.banner` holds the label text that the page must show.
