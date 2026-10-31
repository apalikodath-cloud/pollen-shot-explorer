# 01 - HIVE geometry (PM-001, deliverable 3)

Data file: `data/hive_geometry.json` (schema: `docs/INTERFACES.md`; extra keys are additive).
Figures: `figures/hive_section_pose_pos.png`, `figures/hive_section_pose_neg.png` (drawn from the JSON).

The target is the **upward-facing CELL of the pivoting centre HIVE**, not a FLOWER.

Provenance labels: **confirmed** (official source), **derived** (computed from confirmed values), **assumed** (modelling choice). No value is reused from earlier chats.

## 1. Sources

| # | Source | Version | URL | Used for |
|---|---|---|---|---|
| M | BIOBUZZ Competition Manual | TU07 | https://ftc-resources.firstinspires.org/ftc/game/cm-html/BIOBUZZ%20Competition%20Manual%20-%20TU07.htm | 9.1 tolerances, 9.3 zones, 9.6 HIVE dimensions (Figs 9-9, 9-10, 9-11), 9.8 POLLEN size, 10.3.1 start pose, 10.5.1 TIP, G409/G416/G417, R102/R105 |
| C | Official field CAD, STEP AP242 (`am-5850 BIOBUZZ`) | 2026-27 archive | https://ftc-resources.firstinspires.org/ftc/archive/2027/field/field-cad-step | full 3D geometry: the cell section, pivot hardware, A-frame, field position |
| K | Field Acceptance Checklist | Rev 26-27.2 | https://ftc-resources.firstinspires.org/ftc/archive/2027/field/field-check | 1.13 lip height 53.5 +- 0.5 in; 1.8 foot position; 2.3-2.6 TIP calibration |
| S | Event Field Setup Guide | V1.0 | https://ftc-resources.firstinspires.org/ftc/archive/2027/field/eventfieldguide | 11.1 start pose and the 3 preloaded NECTAR; 12 calibration and the ballast washers |
| A | Initial Field Element Assembly Guide | 2026-27 | https://ftc-resources.firstinspires.org/ftc/archive/2027/field/initialfieldguide | 7.x pivot/cell assembly ("built flat") |

Manual 9.1 says the 3D CAD is the official representation and that manual dimensions are nominal +- 1 in. I parsed the STEP myself (assembly tree, placements and vertices). Every CAD number below is a part extent in the frames defined in section 2. The Onshape version needs a sign-in and was not used.

## 2. Frames

- **CAD frame:** X runs along the red(-)/blue(+) alliance axis, which is also the pivot axis direction. Y is up, with the tile top at Y = 0. Z runs audience(+)/scoring(-). The origin is the field centre.
- **HIVE frame** (INTERFACES): x = Z_cad (positive toward the **audience** side), z = Y_cad, y = X_cad - X_hive. Red HIVE centre X = -12.74 in; blue X = +12.74 in (centre-to-centre 25.5 in, matching Fig 9-10).
- **Cell-local frame** (in `body_local`):
  - u runs along the cell axis, outward toward the up-cell mouth, with its origin on the pivot axis.
  - w is perpendicular to u, toward the cell roof.
  - s is lateral; s = 0 is the HIVE centre plane.
  - World position: x = ±(u cos t - w sin t), z = z_pivot + u sin t + w cos t.

## 3. Cross-section (centre plane s = 0, tipping plane)

The HIVE is one rigid beam carrying two box-shaped CELLS, one at each end, on a central pivot. Both roofs point the same way (+w), so the body is mirror-symmetric about the plane u = 0. At rest it sits on a damper stop with its axis **30 deg** from horizontal. One cell points up and outward; the other points down and outward.

| Item | Value (in) | Value (m) | Label |
|---|---|---|---|
| Pivot axis height | 43.95 | 1.1163 | confirmed M 9.6.1 and C |
| Tilt at rest | 30 deg | - | confirmed M Fig 9-10 (labelled 30 deg) and C (base tube axis measured 30.0 deg) |
| Tilt bounds | 28.80-31.77 deg (wide: 25.90-34.83); precomputed sweeps still use the old 28.5-31.5 (wide 25.5-34.5) | - | derived (section 5) |
| Back wall (back skin) | u = 9.43 | 0.2395 | confirmed C |
| Mouth plane (outer rib face) | u = 21.46 | 0.5451 | confirmed C |
| Cell depth | 12.03 | 0.3056 | derived C (M: "approx 12 in") |
| Floor (top of bottom skin) | w = -1.47 | -0.0373 | confirmed C |
| Roof underside at pentagon peak | w = 12.60 | 0.3200 | confirmed C |
| Roof top (rib tops; skin 12.70) | w = 13.12 | 0.3332 | confirmed C |
| Underside (rib bottom bars; tube -2.71) | w = -2.97 | -0.0754 | confirmed C |
| Opening height at centre | 14.07 (M: 14) | 0.3574 | confirmed C and M Fig 9-11 |
| Opening width | 20 | 0.508 | confirmed M 9.6.2, Fig 9-11 |
| Opening height at side walls (shoulder) | 7.61 | 0.1933 | confirmed M Fig 9-11 |
| Gap between the two cells along the beam | 18.84 | 0.4785 | confirmed M Fig 9-9 |
| Pivot bearing plates | u +-6.89, w -2.71..0.87 | - | confirmed C (am-5873; dampers am-5865 sit inside) |

World key points in pose_pos at tilt 30 deg (derived, then checked against official numbers):

| Point | x (m) | z (m) | z (in) | Official check |
|---|---|---|---|---|
| Lower lip (mouth p0) | 0.4907 | 1.3565 | 53.41 | K 1.13: 53.5 +- 0.5 in; M Fig 9-10: 53.5 in |
| Upper lip (mouth p1) | 0.3120 | 1.6660 | 65.59 | M Fig 9-10: 65.6 in |
| Roof top at the mouth (highest point) | 0.3054 | 1.6775 | 66.04 | CAD overall max 66.02 in |
| Roof top at the back wall | 0.0408 | 1.5247 | 60.03 | - |
| Lowest point (down cell) | -0.4343 | 0.7785 | 30.65 | M Fig 9-10: "bottom of HIVE" 30.6 in |

**Mouth:** the mouth line is 0.3574 m long. Its outward normal is (+-cos 30, sin 30): the mouth faces outward, 30 deg above horizontal.

**Static A-frame** (does not rotate; the same in both poses):
- **Top corner / axle cradle:** |x| <= 0.039 m, z 1.003-1.125 m.
- **ACM logo panels:** run along the legs from (+-0.039, 1.017) to (+-0.109, 0.865) m. They span lateral X_cad -15..15 in.
- **Legs:** about 1 in tubes from (+-0.013, 1.043) to (+-0.471, 0.013) m. The legs also slant laterally, from s = -11.5 in at the foot to +0.5 in at the top. In the s = 0 plane only their top exists, so they are flagged `projected: true`.
- **Foot bars:** x = +-0.495 m.

**Obstacles** are solid, uninflated segments: 16 cell segments, 4 pivot-plate segments and 9 frame segments per pose. The pose_neg list is the exact mirror (x -> -x) of pose_pos.

**inside:** the set of ball-centre positions behind the mouth plane that are at least R from the floor, roof and back wall (derived geometry plus an assumed criterion). The floor slopes 30 deg down toward the back wall, so a ball that comes to rest inside rolls back and is retained. Bounce-outs are left to contact.py.

## 4. Favourable / unfavourable shooting side

Entry requires v . n < 0, where n is the mouth's outward normal. In pose_pos, n = (cos 30, sin 30). Let phi be the ball's descent angle (positive = falling).

- **Favourable = the side the up cell is on** (pose_pos -> "pos", pose_neg -> "neg"). A ball moving toward the pivot enters at any phi from +90 deg (falling vertically) to -60 deg (rising at up to 60 deg).
  - Projected mouth width = 0.3574 cos(phi - 30 deg).
  - Best case: descending at 30 deg sees the full 0.357 m. The ball-centre window is then about 0.357 - 2R = 0.286 m.
- **Unfavourable = the opposite side.** The roof hides the mouth.
  - The ball centre must pass above about 1.713 m (66.04 in + R) over the roof.
  - It must then descend steeper than 60 deg. Geometrically the ball only fits at more than about 71.5 deg (60 + asin(2R/0.357)).
  - Projected mouth width = 0.3574 sin(phi - 60 deg).
  - A vertical drop has a ball-centre window of only 0.108 m (|x| 0.347-0.455 m).

These derivations assume the nominal 30 deg tilt. Section 5 gives the sensitivity.

## 5. Tilt bounds (derived)

- **Nominal:** 30 deg (confirmed twice).
- **Sensitivity:** the lower-lip height changes by dz/dt = u cos t - w sin t = 19.32 in/rad = 0.337 in/deg.
- **Checklist bound:** K 1.13 allows 53.5 +- 0.5 in. With the pivot at its nominal height, the exact solve gives **[28.80, 31.77] deg** (derived, PM-015; the earlier +-1.5 deg -> [28.5, 31.5] was a linear estimate, still used by the precomputed sweeps and labelled "old bound" there; re-sweep deferred).
- **Wide bound:** if the pivot height is also off by the manual's general +-1 in, the bound becomes **[25.90, 34.83] deg** (`low_wide` / `high_wide`, derived; old linear estimate [25.5, 34.5]).

Real fields can differ further: S 12.1 lets field staff "tweak" a cell by hand during calibration, and the dampers compress. The JSON's `body_local` lets hive.py re-pose the body at any tilt.

## 6. Field position, legal shooting region, robot size, HIVE rules

- **Position:**
  - Both HIVES hang from one A-frame at the field centre. Their pivot axes are collinear along the alliance-to-alliance axis.
  - Red sits 0.324 m toward the red wall and blue 0.324 m toward blue.
  - The tipping plane is the audience-scoring axis, so in-plane shots come from the audience side (+x) or the scoring side (-x).
  - The inner perimeter wall is 1.801 m from x = 0 (C). The base frame is 49.46 x 38.95 in (M 9.6.1).
- **Start pose:**
  - The red HIVE starts with its audience cell up, which is **pose_pos**. The blue HIVE starts with its scoring-side cell up, which is **pose_neg**. Sources: S 11.1; M 10.3.1, "the CELL which points at a FLOWER is tilted down"; and the CAD as delivered.
  - Each up cell starts with 3 NECTAR resting against the back skin, on the perimeter side.
  - Every TIP flips the pose.
- **Legal shooting region:** I found **no launch zone, launch line or LAUNCH no-go area** in TU07. 9.3 defines only ALLIANCE AREA, LOADING ZONE and GARDEN, so a ROBOT may LAUNCH from anywhere on the FIELD.
  - G417 still applies: no contact with or meddling with the HIVE.
  - G409: a robot may not catch or deflect elements spilled by a TIPPED HIVE until they touch something else.
  - T405 J: no LAUNCHING during calibration time.
- **Robot size (M 12 R102, R105, G416):**
  - The starting configuration must fit an 18 in cube.
  - Once expanded, the robot must always fit 18 x 24 in x **29 in (0.7366 m) tall**, measured from the field surface.
  - The release height is therefore at most about 0.737 m for the ball centre (assumed: the ball is still within the sizing volume while in the mechanism).
  - The down cell's lowest point is 0.778 m above the tiles.
- **HIVE rules (M 10.5.1, G417):**
  - LAUNCHING into the upward CELL is the only allowed way to cause a TIP.
  - Likely STRATEGIC (MAJOR FOUL + YELLOW CARD):
    - (C) deliberately LAUNCHING into the external bottom, sides or top of a CELL;
    - (D) LAUNCHING at an opponent's HIVE to impede its TIP;
    - (E) contacting a HIVE directly or through a controlled element.
  - Not STRATEGIC (H): a genuine attempt at the up CELL that misses and hits the cell's bottom, sides or top.
  - Design consequence: rim contact during a scoring attempt is fine, but a **planned bank shot off the roof or outer faces is a G417 risk**.
- **TIP calibration (K 2.3-2.6, S 12):**
  - 3 NECTAR + 2 POLLEN does not tip; one more tossed POLLEN tips it.
  - 7 POLLEN does not tip; the 8th tossed POLLEN tips it.

## 7. Confirmed vs assumed (summary)

- **Confirmed:**
  - pivot height; 30 deg tilt
  - cell opening, depth and the cell spacing along the beam
  - lip heights
  - the lowest point
  - the HIVE centre spacing and field position
  - the start pose
  - POLLEN diameter (approximately 2.8 in)
  - robot height
  - the G417 / G409 wording
  - the absence of a launch zone in TU07
- **Derived:**
  - the world coordinates of every segment
  - the mouth normal
  - the entry-angle windows
  - the tilt bounds
  - the inside polygon
- **Assumed / simplified:**
  - The roof outer is drawn at rib-top height and the underside at rib-bottom height. Both are envelopes, accurate to within 11 mm.
  - The inside criterion.
  - The release height limit.
  - The 2D centre-plane section is the best case; off-centre, the pentagonal roof is lower.
  - Leg segments are projected.

## 8. Open questions

These are also listed in the JSON:
- The actual tilt on real fields.
- 3D and off-centre shots: the pentagon roof drops to 0.193 m at the walls.
- How hive.py should treat the projected leg segments.
- Where the ballast-washer screw "nearest the opening" sits.
- Whether G417 C or H applies to an intentional rim graze. Ask on the official Q&A forum.
- Whether later Team Updates add a launch zone.
- The effect of the 3 preloaded NECTAR.
- The POLLEN size tolerance.

How the deliverables were generated: `build_hive_geometry.py` and `plot_hive_section.py` were one-off working scripts and are not in this repository. `crosscheck/geometry/build_hive_geometry_independent.py` is an independent rebuild of the same geometry.
