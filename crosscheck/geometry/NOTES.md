# Independent HIVE geometry: crosscheck notes (PM-001)

Scope: the geometry was sourced again from official FIRST/AndyMark material without reading
`data/hive_geometry.json` or `docs/01_hive_geometry.md`. Outputs in this folder:

- `hive_geometry_independent.json`: same schema as `docs/INTERFACES.md`, SI units. It also has extra keys (`cell_opening_profile`, `hive_layout`, `field`).
- `build_hive_geometry_independent.py` builds the JSON and the figure. Run it with `py -3.13 crosscheck/geometry/build_hive_geometry_independent.py`.
- `hive_section_independent.png`: both poses at the cell-centre plane.
- `cad_tools/step_parse.py`: the STEP AP242 assembly parser used to read the official CAD. It needs only regex and numpy.

Provenance labels: **confirmed** = official source quoted; **derived** = computed from confirmed/CAD numbers (formula given); **assumed** = modelling choice; **user** = from HANDOFF/user.

## Official CAD: where it is and whether it parsed

- Field resources page: https://ftc-resources.firstinspires.org/ftc/archive/2027/field
- Onshape field CAD (public document): https://cad.onshape.com/documents/a355e772e3d24813de7852ee/w/f106353168f1f92100b81259/e/95d1e1e442b4138cccaf2d73 (FLOWER scoring volume tab: `.../e/8f89b946e295be9c543faa08`).
- STEP download: https://ftc-resources.firstinspires.org/ftc/archive/2027/field/field-cad-step (zip, `field-cad-step.step`, 35 MB, AP242, field v26-27.2, Sep 15 2026).
- **Parsed: yes.** The parser walked the `am-5850 BIOBUZZ` assembly tree: NAUO → CONTEXT_DEPENDENT_SHAPE_REPRESENTATION → ITEM_DEFINED_TRANSFORMATION. That gave 993 part occurrences with world vertex clouds and circle features, in metres. CAD world: Y up, tile top at Y=0, field centre at X=Z=0. The pivot axes run along CAD X at Y = 43.950 in, Z = 0. The blue HIVE spans X 2.26..23.26 in and the red HIVE spans X -23.24..-2.24 in. Every HIVE part is rotated by exactly 30.000 deg about X.
- Mapping to the INTERFACES frame: x = CAD Z (the tipping plane), y = CAD X (the pivot axis), z = CAD Y (up).

## Source table

| # | Source (URL) | Exact quote / figure | Value used | Label |
|---|---|---|---|---|
| 1 | Competition Manual TU07, 9.6.1 Frame: https://ftc-resources.firstinspires.org/ftc/game/cm-html/BIOBUZZ%20Competition%20Manual%20-%20TU07.htm | "The Frame supports 2 pivots with their axis 43.95 in. (111.65 cm) above the TILES." Fig 9-8 shows the same value. | pivot z = 43.95 in = 1.11633 m (CAD 43.950 in) | confirmed |
| 2 | same, 9.6.1 | "The frame is 49.46 in. (125.65 cm) wide, and 38.95 in. (98.95 cm) deep at its base" | frame base 1.2563 m along y, 0.9893 m along x. CAD feet at ±24.73 in (y) and ±19.47 in (x) | confirmed |
| 3 | same, 9.6.2 | "two CELLS ... approximately 18.8 in. (47.8 cm) apart"; Fig 9-9: "18.84 in. (47.85 cm)", "12.04 in. (30.58 cm)", "42.91 in. (109.0 cm)" | Back Skin to Back Skin 18.84 in; cell depth 12.04 in; overall length 42.91 in. CAD gives 18.86, 12.02 and 42.91 in | confirmed |
| 4 | same, 9.6.2 + Fig 9-11 | "The opening of the CELL is approximately 20 in. (50.8 cm) wide by 14 in (35.6 cm) tall and 12 in. (30.5 cm) deep". Fig 9-11 also gives "7.61 in. (19.35 cm)" as the side-wall height | pentagonal opening: 20 in wide, 7.61 in at the walls, 14 in at the apex. CAD inner width 20.21 in, apex 14.0 in above the lip | confirmed |
| 5 | same, Fig 9-10 "HIVE and CELL Key Details" (image `..._files/image032.png`) | angle mark "30°"; "Top of HIVE Opening above TILES 65.6 in. (166.60 cm)"; "Bottom of HIVE Opening above TILES 53.5 in. (135.90 cm)"; "Bottom of HIVE above TILES 30.6 in. (77.70 cm)"; "HIVE Center to Center 25.5 in. (64.75 cm)" | tilt 30 deg. From CAD at 30 deg: 53.38 / 65.50 / 30.65 in; HIVE centres at ±12.758 in | confirmed (both the figure and the CAD) |
| 6 | Field Acceptance Checklist, rev 26-27.2, item 1.13: https://ftc-resources.firstinspires.org/ftc/archive/2027/field/field-check | "When upright (opposite damper is fully depressed), the bottom of each CELL opening is 53.5 ± 0.50 in. (135.90 ± 1.30 cm) above the tiles." | tilt bounds 28.88..31.86 deg; the checklist midpoint gives 30.36 deg | derived |
| 7 | Manual 10.5.x HIVE TIP + Fig 10-3 "HIVE damper and frame" | "the damper on the HIVE that was previously not contacting the frame begins to contact the frame". Fig 10-3 marks both a just-touching damper and a compressed damper as "YES Damper Contact" | the stops are the linear dampers (Blum 970A, am-5865 in CAD) on the hive hub contacting the A-Frame top corner / leg ends | confirmed |
| 8 | Manual 9.6 | "Each HIVE is on a pivot and can tip so that one of the CELLS is facing upwards at any given time. Each HIVE is bi-stable" | two poses, mirror images | confirmed |
| 9 | Manual 9.2 | "approximately 144 in. by 144 in. ... 36 interlocking soft foam TILES ... 24 in. by 24 in. by 0.59 in." | field half-width ≈ 1.83 m. CAD perimeter inner face at ±70.67 in (1.795 m) | confirmed / derived |
| 10 | Manual 9.6 | "The HIVE Structure is located in the center of the FIELD." | HIVE pivot plane at field centre. The pivots run toward the alliance walls, and the cells tip toward the audience and far walls | confirmed (CAD agrees) |
| 11 | Manual R105.A | "within a 18 in. (45.70 cm) by 24 in. (61.0 cm) by 29 in. (73.65 cm) tall sizing volume when fully expanded"; starting configuration "18 in. ... by 18 in. ... by 18 in. high" | robot max height 29 in = 0.7366 m (0.4572 m at the start) | confirmed |
| 12 | Manual G417 / G409 / LAUNCH definition | "ROBOTS may not manipulate the motion of the HIVE in any way other than by LAUNCHING SCORING ELEMENTS into an upward-facing CELL." G417 examples include "deliberately LAUNCHING ... into the external bottom, sides, or top faces of a CELL" | no LAUNCH zone was found in TU07. Shots may come from anywhere on the field, either side | confirmed (absence noted) |
| 13 | Manual 10.5.1 | "At the end of the MATCH, any POLLEN and/or NECTAR left in an upward-facing CELL will earn points" | `inside` = retained region | confirmed |
| 14 | Event Field Setup Guide V1.0 §11.1: https://ftc-resources.firstinspires.org/ftc/archive/2027/field/eventfieldguide | Red Hive "Audience" cell up, Blue Hive "Scoring" cell up; 3 NECTAR preloaded in each upward cell against the Back Skin | match-start state; the NECTAR is not modelled | confirmed |
| 15 | Initial Field Element Assembly Guide V1.0: https://ftc-resources.firstinspires.org/ftc/archive/2027/field/initialfieldguide | cell = 2 Goal Ribs + Top/Bottom/Back Skin + Base Tube + 2× 10.5 in Churro; Stepped Axle in Axle Pivot Cradles; Pivot Bearing Plates; Damper Holders + Linear Dampers | part identification | confirmed |
| 16 | Team Updates (game page https://ftc-resources.firstinspires.org/ftc/game) | latest is TU07 (Oct 29 2026). It changes only G304, G412 and G419 | no geometry change after TU07 | confirmed |
| 17 | Official STEP CAD (see above) | section dimensions in the table below | obstacles / mouth / inside | confirmed (CAD) + derived |

Community sources: none were needed. The official manual figures and CAD agree to within about 0.1 in.

## CAD section at the cell-centre plane (flat hive frame, inches; up cell z' < 0)

| Feature | Value | Notes |
|---|---|---|
| Mouth plane (outer face of outer Goal Rib) | z' = -21.456 | rib thickness 2.0 in (to -19.456) |
| Floor (Bottom Skin top) | y' = -1.488 | skin about 0.02 in thick |
| Lip (top of rib bottom bar) | y' = -1.50 | flush with the floor (no raised lip) |
| Lowest point of cell (rib bottom) | y' = -2.972 | |
| Back Skin inner / outer | z' = -9.438 / -9.418 | depth from mouth plane 12.02 in |
| Roof inner apex / rib outer apex | y' = 12.50 / 13.057 | 14.0 in above the lip |
| Side walls (inner) | x = 2.65 .. 22.87 in (CAD X) | the roof starts about 7.9 in above the floor at the walls |
| Hub (pivot brackets, damper holders, base tubes) | |z'| < 6.9, y' -2.71 .. 0.83 | pivot is 1.49 in above the floor plane |

World check at 30 deg: bottom of opening = 43.95 - 1.50 cos30 + 21.456 sin30 = 53.38 in. The manual gives 53.5 in. The other figure points come out as top of opening 65.50 in (manual 65.6), lowest point of the hive 30.65 in (manual 30.6), and roof outer apex 65.99 in.

## Tilt angle and what sets it

- Nominal 30 deg (**confirmed**: manual Fig 9-10 and the CAD).
- Bounds 28.88..31.86 deg (**derived**). Solved from checklist 1.13: h(θ) = 43.95 - 1.50 cos θ + 21.456 sin θ = 53.5 ± 0.5 in. The sensitivity is dh/dθ ≈ 0.34 in/deg.
- Physical stop: the hub carries two Blum 970A linear dampers in Pivot Damper Holders, at hive-local ±54 deg below the pivot. The lever arm is 3.57 in, and the plunger axis is within 11 deg of the rotation tangent. In each pose, one plunger tip bears on the A-Frame top corner / leg end of the frame. The second pose is the exact mirror.
- In the CAD both plungers show 0.49 in (12.5 mm) of exposed rod, and the contacting tip is about 0 in from the frame. So the CAD pose is first contact with the plunger extended. Fully depressing 0.49 in would add about 8 deg (about 38 deg, bottom of opening about 56 in). That is outside the checklist tolerance, so the real compressed travel or end stop must be smaller. This is an open question. Neither the CAD nor the manual gives a Blum 970A stroke figure.

## Favorable side

The upward CELL's mouth faces outward, away from the pivot, toward the side the cell is on. Its axis points 30 deg above horizontal, so the mouth plane sits 60 deg from horizontal. The cell floor slopes down toward the Back Skin, so a ball whose centre crosses the mouth ends up against the back and is retained.

- **pose_neg** (up cell on -x): favorable = **neg**. A shot from x<0 travelling +x enters through the mouth.
- **pose_pos**: favorable = **pos**. It is the mirror case.

A shot from the far side must clear the roof (outer apex 1.676 m at 30 deg). It then has to cross the mouth plane inward, which needs a descent steeper than 60 deg just beyond the roof's front edge. The handoff says the target is the HIVE CELL, not the FLOWER, and it is.

## Field context (CAD, inches, field centre origin)

- Alliance areas are outside the ±CAD-X walls (red at -X, blue at +X). Each HIVE sits on its own alliance's half along the pivot axis.
- Loading zones are along the alliance walls: 23 × 11 in, e.g. blue at X 59.1..70.1, Z 24.9..45.6.
- The four FLOWERS sit against the walls at (X,Z) = (23.4, 68.2), (68.2, -23.4), (-68.2, 23.4) and (-23.4, -68.2), with the top opening 21.5 in above the tiles.
- Robots may drive under the HIVE (manual G409 discussion). The A-Frame legs splay to Z ±19.07 at the floor.
- The cell that "points at" a FLOWER starts down (manual 10.3.1).

## Things not modelled

- The 3D roof shape: the 2D section is the most open, centre plane. `cell_opening_profile` gives the pentagon.
- Churro rods inside the roof corners, at y' about 6.0..6.4, near the side walls only. They are not in the centre plane.
- Preloaded NECTAR.
- Leg inclination along y.
- Part tolerances, skin sag and damper compliance.
