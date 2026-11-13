# Head A on the robot turret: fit and size check

Status 2026-11-08: Head A (Concept A) is mounted on the turret of the robot in the Onshape document
"19705 2026-27 Ri3D.step", in a separate fit assembly in the POLLEN shooter document. The robot document was not
changed. The fit was checked two ways:

- a box model over every turret angle at α 5, 15 and 25;
- Onshape interference detection at α 5, 15 and 25, each at three turret angles.

Robot dimensions are measured from the CAD views (±3 mm). Motor and servo sizes are placeholders (TBD).

## 1. Short answer

1. **The head fits on the turret with no clash.**
   - The turret can swing the head ±101° from straight over the intake. The robot's own shooter swings about ±104°
     (same box model).
   - Set the turret's soft limit to **±96°**. Inside it every gap to the robot is at least 9.2 mm.
   - Onshape finds **0 contacts** between the head and the robot at 0° and ±101°, at α 5, 15 and 25.
2. **Expanded size (18 × 24 in in plan, 29 in tall): fits** at every turret angle in the travel and at every α.
   - The tightest plan margin is 8.4 mm.
   - The height margin is at least 255.8 mm.
3. **Start size (18 in cube): fits in plan, but the head is too tall.**
   - Plan: park the turret anywhere from −101° to −30° or from +38° to +101°. The best park is −46°, with 37.1 mm
     spare. Parked straight over the intake (0°) the robot is 13.0 mm too long.
   - Height: the head top is **15.7 mm too high** at α 15 (16.7 at α 5, 23.6 at α 25). Fix it by lowering the turret
     plate at least 16 mm, or by making the head that much lower, and starting at α 15 (section 5).
4. **The feed is not solved yet (TBD).** The robot brings the ball up through the turret centre. The head's feed was
   built for a ramp coming from behind. A riser has to lift the ball about 67 mm above the turret plate and set it on
   the head's chute at the turret axis (section 6).

## 2. The robot

Robot numbers are in the robot assembly's frame: mm, Z up, field floor at Z −6. The intake is at −X and the two rear
arms are at +X.

| Item | Value | Note |
|---|---|---|
| Turret axis | X −54.5, Y 0 | centre of the rotating plate |
| Turret plate top | Z 238.2 | the head sits on it |
| Fixed plate under it | top Z 228, Ø108 hole | the ball comes up through the hole |
| Ball path | X −77 to −22.5, Y ±38 | straight up through the turret centre |
| Length (X) | −336.8 (intake out) to 138.4: 475.2 | |
| Length at the start | −232 to 138.4: 370.4 | intake folded to X −232 (assumed, TBD) |
| Width (Y) | ±164: 328 | |
| Top | Z 435.4, which is 441.4 above the floor | slides retracted |
| Rear arms (two leaning slides) | \|Y\| 80 to 99, 18 mm wide in X, leaning 9° toward +X | measured, ±3 mm, slides retracted |
| Rear arm inner edge | X 37.1 at Z 241.9, X 67.6 at Z 434.1 | measured, ±3 mm |
| Rear arm top bracket | reaches X 106, above Z 409 | measured, ±3 mm |
| Side-plate peaks | Z 241.9 (3.7 mm above the turret plate), X 23.3 to 50, \|Y\| 100 to 104 | measured, ±3 mm |

Size rules (`docs/01_hive_geometry.md`, robot size):

| Configuration | Plan | Height | Height limit in robot Z |
|---|---|---|---|
| Start | 18 × 18 in (457.2 mm) | 18 in | Z 451.2 |
| Expanded | 18 × 24 in (457.2 × 609.6 mm) | 29 in (736.6 mm) | Z 730.6 |

With the intake out the robot is 475.2 mm long, so the 24 in side runs along X.

**Turret angle.** 0° means the head shoots straight out over the intake (−X). Looking out over the intake:

- −90° shoots to the right (+Y);
- +90° shoots to the left (−Y).

This is the Revolute 1 angle in the fit assembly. The scripts and CSVs also use ψ = turret angle + 180°, the shooting
direction measured from +X.

## 3. Mount

| Item | Value |
|---|---|
| Turret axis on the head | head x −95, y 0: on the centre line, 95 mm behind the main axle F |
| Height | frame side plate bottoms (head z −142) on the turret plate, no adapter |
| Main axle F at turret 0° | X −149.5, Y 0, Z 380.2 |
| Back of the head | ramp stub 15 mm instead of 60 |

**Why the back is shortened.** With the 60 mm ramp stub, the frame plates and the feed floor reach 230 mm behind F,
and the back of the head runs into the rear arms. The widest clear travel is then 114° (best mount x −125). On the
turret the ball comes up from below (section 6), so the ramp stub is not needed. A new configuration input,
`ramp_stub_cfg`, shortens it to 15 mm:

- the frame then ends at x −187;
- the feed floor ends at about x −177;
- every mount from x −100 to −85 then gets 202° of travel.

**Why x −95.** Moving the axis forward, toward F, gives more plan margin but less gap to the arms. x −95 gives the
largest gap to the arms (9.2 mm) and still leaves 8.4 mm of plan margin (section 8).

**What was added in Onshape** (POLLEN shooter document):

- **Head A (Concept A) Part Studio:**
  - a configuration input `ramp_stub_cfg`, default 60 (unchanged); the variable `ramp_stub_L` now reads it;
  - a mate connector feature "Turret mount MC (x -95, z -142 frame bottom)" on the +Z frame side plate;
  - a suppressed "POLLEN turret fit 1" feature, which prints the part boxes for the box model;
  - its Feature Studio "POLLEN turret fit FS" (the code is also in `checks/eval_turret_fit.fs`).
- **Bot fit (Ri3D turret) assembly** (new tab):
  - the robot assembly, inserted from its document and fixed;
  - its own shooter ("shooter <1>"), hidden in this assembly only;
  - 58 Head A instances at α 15 and `ramp_stub_cfg` 15, grouped (Group 1);
  - "Mate connector 1" on the assembly origin, moved to the turret axis (X −54.536, Y 0, Z 238.2) and turned 180°
    about Z;
  - "Revolute 1" from that connector to the Turret mount MC, limits −101° to +101°.

## 4. Turret travel

Gaps are from the box model, the smallest over α 5, 15 and 25. The gap is measured in plan to the rear arms or the
side-plate peaks, wherever they overlap the head part in height. The expanded margin is the smallest of
(609.6 − length, 457.2 − width) for robot plus head. Every turret angle is in
`checks/turret_fit_sweep_2026-11-08.csv`.

| Turret | Gap to the robot (mm) | Closest pair | Expanded margin (mm) |
|---|---|---|---|
| ±102 | overlap | frame side plate on a side-plate peak | |
| −101 (limit) | 0.9 | +Z frame side plate to side-plate peak +Y | 8.5 |
| −99 | 4.9 | same | 8.4 |
| −96 (soft limit) | 10.8 | same | 8.8 |
| −90 | 22.1 | same | 12.0 |
| −84 | 16.9 | +Z frame side plate to side-plate peak −Y | 8.8 |
| −45 | 14.1 | main motor envelope (TBD) to arm +Y | 35.1 |
| −37 | **9.2** (smallest inside ±96) | main motor envelope (TBD) to arm +Y | 50.6 |
| 0 (over the intake) | 24.3 | −Z frame side plate to arm −Y | 129.2 |
| +45 | 36.0 | gate servo envelope to arm −Y | 62.4 |
| +84 | 10.8 | gate servo envelope to arm +Y | 8.8 |
| +90 | 12.8 | gate servo envelope to arm +Y | 12.0 |
| +96 (soft limit) | 10.8 | −Z frame side plate to side-plate peak −Y | 8.8 |
| +101 (limit) | 0.9 | −Z frame side plate to side-plate peak −Y | 8.5 |

Every listed gap is set at α 5.

- Past ±101° the bottoms of the frame side plates run into the side-plate peaks, which stand 3.7 mm above the turret
  plate. A few degrees further on, the head reaches the arms.
- There is a second clear pocket, pointing straight back over the arms (turret 170° to 190°). The turret cannot get
  there without passing through the arms.
- How the turret is stopped (a limit in the turret code, a hard stop, or both) is TBD.
- Whether the turret drive can swing the head's mass was not checked (TBD).

## 5. Size check

### Expanded

**Fits** at every turret angle in the travel and at α 5, 15 and 25.

- In plan the head reaches past the robot's sides near ±90°. The tightest margin is 8.4 mm at about −100°: robot
  plus head is 448.8 mm wide of the 457.2 mm allowed.
- In height the head top is at most Z 474.8 (α 25), 255.8 mm under the 29 in limit.

### Start, plan

Intake folded to X −232 (assumed), head at α 15:

| Turret | Start plan margin (mm) | Limited by |
|---|---|---|
| −101 | 12.4 | width |
| −90 | 15.9 | width |
| −60 | 24.0 | width |
| −46 | **37.1 (best)** | length and width almost equal (418.1 × 420.1) |
| −30 | 1.5 | length |
| −10 | −16.7 (does not fit) | length |
| 0 | −13.0 (does not fit) | length (470.2) |
| +30 | −4.9 (does not fit) | length |
| +38 | 0.6 | length |
| +58 | 34.1 (best on this side) | |
| +90 | 15.9 | width |
| +101 | 12.4 | width |

It fits from −101° to −30° and from +38° to +101°. It does not fit from −29° to +37°.

### Start, height

The head is **too tall at every α**:

| α | Head top | Above the floor | Over the 18 in limit |
|---|---|---|---|
| 5 | Z 467.9 | 473.9 mm | 16.7 mm |
| 15 | Z 466.9 | 472.9 mm | **15.7 mm** |
| 25 | Z 474.8 | 480.8 mm | 23.6 mm |

The turret plate leaves 213.0 mm under the start limit, but the head is 228.7 mm tall at α 15 (head z −142 to
+86.7). The robot alone, with its slides retracted, is 15.8 mm under the limit.

**Fixes** (pick one or mix them; all TBD):

1. **Lower the turret plate by at least 16 mm.** This is a robot change. Rerun the travel check afterwards: the arms
   lean closer to the turret lower down, and the side-plate peaks would stand higher above the plate.
2. **Make the head lower** (a head change):
   - Cut the frame side plate bottoms from head z −142 to −136, level with the feed floor. The head then sits 6 mm
     lower.
   - Bring every part at α 15 down to head z 77 or lower. These parts are above it now:

     | Part (α 15) | Top (head z) |
     |---|---|
     | Head side plate +Z | 86.7 |
     | Hard stop for α 25 (on the frame) | 85.9 |
     | Head side plate −Z | 81.8 |
     | Angle gear sector | 81.7 |
     | Frame side plates ±Z | 80.0 |
     | Angle pinion | 79.8 |
     | Angle servo envelope | 77.2 |

   - With the frame bottoms at −136, the box model gives the same ±101° travel. The smallest gap inside ±96° drops
     from 9.2 to 8.4 mm.
3. **Start with the head at α 15.** It is the lowest of the three; α 25 is 8 mm higher.

A mix also works, for example cutting the frame bottoms (6 mm) and lowering the plate 10 mm.

## 6. Feed handoff (TBD)

On the turret the ball arrives from below, straight up through the turret centre (the Ø108 hole). The head's feed
was built for a ramp coming from behind ([ramp_feed.md](ramp_feed.md)): crest, 35° chute, then rails around the main
wheel. At this mount the turret axis lies between the crest top and the rails:

| Point | Where |
|---|---|
| Chute rail-edge line, over the turret axis | Z 298.7, 60.5 mm above the turret plate |
| Crest top | 36.0 mm behind the axis |
| Where the chute meets the rails | 25.4 mm ahead of the axis |
| Ball resting on the chute rails, centred over the axis: centre | 100.5 / 102.1 / 103.7 mm above the plate (smallest / nominal / largest ball) |
| Same ball: bottom | 66.2 / 66.6 / 66.9 mm above the plate |

So the ball has to be lifted to about 67 mm above the turret plate, at the turret axis, and set on the chute. From
there it rolls onto the rails as in ramp_feed.md. Not modelled yet (TBD):

- a vertical entry about Ø76 through the feed floor at the axis. It fits between the frame side plates, whose inner
  faces are at ±49.4;
- a riser that lifts the ball about 67 mm above the plate. Where it goes (in the turret or on the head) and the height
  at which the robot delivers the ball are TBD.

The crest and the ramp stub are then not needed. Whether the crest gate stays, as the one-ball-at-a-time gate, is TBD.

## 7. Onshape check

Fit assembly "Bot fit (Ri3D turret)". Onshape's interference detection uses exact geometry. Settings:

- Head A at α 5, 15 and 25 (all 58 head instances changed together), with `ramp_stub_cfg` 15.
- All 246 visible instances: 188 from the robot and 58 from the head.
- The robot's own hidden shooter left out.

| α | Turret | Contacts | Robot–robot | Head–head | Head–robot |
|---|---|---|---|---|---|
| 5 | 0 | 650 | 634 | 16 | **0** |
| 5 | −101 | 650 | 634 | 16 | **0** |
| 5 | +101 | 650 | 634 | 16 | **0** |
| 15 | 0 | 650 | 634 | 16 | **0** |
| 15 | −101 | 650 | 634 | 16 | **0** |
| 15 | +101 | 650 | 634 | 16 | **0** |
| 25 | 0 | 650 | 634 | 16 | **0** |
| 25 | −101 | 650 | 634 | 16 | **0** |
| 25 | +101 | 650 | 634 | 16 | **0** |

- **Robot–robot:** overlaps inside the imported robot, the same 634 in every run. They were not examined, and they
  do not involve the head.
- **Head–head:** all 16 involve a REF body (the see-through ball envelopes, the exit corridor and the nip ball). These
  overlap on purpose, and 7 of the 16 are between two REF bodies. No real head parts touch, as in the Part Studio
  check (ramp_feed.md section 7).
- **Hidden instances:** interference detection checks them too. Left in, the robot's hidden shooter gave about 96
  false hits.
- **Angle α:** the counts are the same at α 5, 15 and 25. The parts that sit lower at α 5 or 25 (section 9, caveat 5)
  do not touch the robot at these three turret angles.

Results are in `checks/turret_fit_onshape_2026-11-08.csv`.

**How to see it move:**

1. Open the POLLEN shooter document and click the **Bot fit (Ri3D turret)** tab at the bottom.
2. In the list on the left, open **Mates** and right-click **Revolute 1** (the turret).
3. Choose a motion:
   - **Animate** with the range −101° to 101° swings the head through the travel.
   - **Apply limit position**, then **Min** or **Max**, jumps to −101° or +101°.
   - **Reset** puts the head back at 0°, over the intake.
4. Click an empty part of the graphics area, then press Shift+5 for the top view, Shift+1 for the front view or Shift+7
   for isometric.

**How to rerun the interference check:**

1. Open **Interference detection** from the icons at the lower right of the graphics area.
2. With its selection box active, expand the robot instance in the instance list.
   - Click the robot's first item.
   - Scroll to the bottom and Shift-click the last head instance. This selects everything.
3. Click **shooter <1>** (inside the robot) once to take it out of the selection.
4. Read the result list. A row with one head part and one robot part is a clash.

**How to check another α:**

1. In the instance list, right-click a Head A instance and choose **Select instances with same configuration**. All 58
   head instances are selected.
2. Right-click one of them again and choose **Change configuration...**.
3. Type the new alpha, press Tab and click **Generate**. The part list takes about 2 minutes.
4. Click ✓. Hover over any head instance to see its alpha.
5. Rerun the interference check. Set alpha back to 15 afterwards.

## 8. Other mounts

All of these are on the head's centre line (y 0), with the back shortened and no adapter. Every mount from x −100 to
−85 gives the same ±101° travel; the side-plate peaks set its ends, at 0.9 mm.

| Mount (head x) | Smallest gap to the arms (mm) | Expanded margin (mm) | Start plan margin at −90° / +90° / 0° (mm) |
|---|---|---|---|
| −100 | 9.0 at −101° | 3.5 | 10.9 / 10.9 / −18.0 |
| **−95 (chosen)** | 9.2 at −37° | 8.4 | 15.9 / 15.9 / −13.0 |
| −92.5 | 7.9 at +85° | 10.9 | 18.4 / 18.4 / −10.5 |
| −90 | 6.3 at +15° | 13.3 | 20.9 / 20.9 / −8.0 |
| −85 | 2.4 at −69° | 18.3 | 25.9 / 25.9 / −3.0 |

The gap column is to the arms only, without the side-plate peaks.

- **With the full 60 mm ramp stub:** at most 114° of travel (mount x −125).
- **A 4 mm adapter plate under the head:** it lifts the frame plates over the side-plate peaks, so the travel grows to
  ±108°. But the arms then come within 0.9 mm at the ends, and the head gets 4 mm taller, which makes the start height
  worse. Not used.

## 9. Method and caveats

**Box model.**

- The "POLLEN turret fit" FeatureScript prints a box for every head part except the REF bodies, at α 5, 15 and 25:
  `checks/turret_fit/tf_a5.txt`, `tf_a15.txt` and `tf_a25.txt`. The motor and servo envelopes count as parts.
- The boxes were captured with the 60 mm ramp stub. The scripts shorten the back in code: frame x ≥ −190, feed floor
  x ≥ −175.
- Every head part is extruded along the wheel axle, so its plan outline is exactly its box. In height the box is
  conservative.
- The scripts turn the boxes about the turret axis in 1° steps. At each step they measure:
  - the plan gap to the arms and the side-plate peaks, wherever the heights overlap;
  - the plan size of robot plus head.

**Caveats.**

1. The arms and the side-plate peaks are measured from the views (±3 mm), with the slides retracted. Whether anything
   comes closer with the slides extended is TBD.
2. The folded intake position for the start (X −232) is assumed (TBD).
3. Motor and servo sizes are placeholder envelopes (TBD). The main motor envelope sets the 9.2 mm gap at −37°.
4. The box model checks only the arms and the side-plate peaks. Onshape checks everything, but only at α 5, 15 and 25,
   each at 0° and ±101°.
5. Some parts sit lower at α 5 or 25 than at α 15. Onshape found no contacts for them at 0° and ±101° (section 7).
   Between those turret angles they were checked only against the arms and the side-plate peaks (box model):

   | α | Part | How much lower | Lowest point |
   |---|---|---|---|
   | 5 | hood (head x −22.8 to 112.2) | 4.2 mm | Z 253.5 |
   | 5 | angle gear sector | 5.5 mm | Z 381.9 |
   | 25 | counter-roller guard | 23 to 31 mm | Z 283.6 |
   | 25 | radial adjuster screws | 23 to 31 mm | Z 292.5 |
   | 25 | counter-roller | 23 to 31 mm | Z 295.6 |
   | 25 | counter-roller carriers | 23 to 31 mm | Z 297.2 |

   The α 25 rows are the counter-roller end, at head x 101 to 186. In the α 15 front view the head front sits well
   above the intake; the intake's top strut is at about Z 231 (a rough reading from the view).
6. "Mate connector 1" sits at fixed assembly coordinates; it is not attached to the robot's turret part. If the robot
   moves, or the robot document changes, the head does not follow. The robot's own turret is not linked to Revolute 1.
7. The REF bodies are left out of the box model. Onshape includes them, and they cause the 16 head–head contacts.
8. The 634 contacts inside the robot were not examined.
9. In Onshape the feed floor ends at about x −177; the box model cuts it at −175. The 2 mm do not matter:
   - that corner stays within 96 mm of the turret axis, and the arms are at least 121.6 mm away;
   - the floor (Z 244.2 and up) is above the side-plate peaks (Z 241.9).

## 10. Files and rerun

| File | What it is |
|---|---|
| `checks/turret_fit/fit.py` | robot numbers and the box loader |
| `checks/turret_fit/arms.py` | arm and side-plate model; also the robot's own shooter range |
| `checks/turret_fit/scan.py` | mount-point scan, full and shortened back |
| `checks/turret_fit/margins.py` | the chosen mount: travel, gaps, plan margins, feed numbers, height |
| `checks/turret_fit/margins_out.txt` | output of margins.py |
| `checks/turret_fit/arm_only.py` | gap to the arms only, and the 4 mm adapter |
| `checks/turret_fit/mounts.py` | mount comparison (section 8) |
| `checks/turret_fit/sweep_csv.py` | writes the 1° sweep CSV |
| `checks/turret_fit/plan.py` | early plan-only check (not used for the numbers here) |
| `checks/turret_fit/tf_a5.txt`, `tf_a15.txt`, `tf_a25.txt` | part boxes from the FeatureScript |
| `checks/eval_turret_fit.fs` | the "POLLEN turret fit" FeatureScript |
| `checks/turret_fit_sweep_2026-11-08.csv` | box-model sweep, every degree; column definitions in the header |
| `checks/turret_fit_onshape_2026-11-08.csv` | Onshape interference results |

Rerun with Python 3 (standard library only), from `checks/turret_fit`:

```
python margins.py > margins_out.txt
python mounts.py
python arm_only.py
python sweep_csv.py ../turret_fit_sweep_2026-11-08.csv
```

**After a head change, capture new boxes:**

1. In the "Head A (Concept A)" Part Studio, unsuppress "POLLEN turret fit 1".
2. Set α to 5 and copy the TF lines from the FeatureScript console into `tf_a5.txt`.
3. Repeat for α 15 and α 25.
4. Suppress the feature again; it is slow.

`scan.py` shortens the back by part index (the frame plates and the feed floor, indices 21, 24 and 42), so check
those indices after any part is added or removed.

## 11. Undo

In Onshape (POLLEN shooter document), in this order:

1. Delete the **Bot fit (Ri3D turret)** tab: right-click the tab and choose Delete. The robot document is not
   affected.
2. In the "Head A (Concept A)" Part Studio, delete the "Turret mount MC (x -95, z -142 frame bottom)" feature. Do this
   after step 1, because the fit assembly uses it.
3. Delete the suppressed "POLLEN turret fit 1" feature.
4. Set `ramp_stub_L` back to 60 mm, then delete the configuration input `ramp_stub_cfg`.
5. Delete the **POLLEN turret fit FS** tab. Do this after step 3, because that feature uses it.

The α 5 and 25 checks set the head instances back to α 15 afterwards, so they leave nothing to undo.

In the repo, revert the two commits that added and then updated this file.
