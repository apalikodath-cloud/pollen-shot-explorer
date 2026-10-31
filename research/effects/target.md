# Target-side effects: what happens at and inside the HIVE CELL

Lens: "target". This file lists the physics at the HIVE that the shot model may be missing or may be handling too simply.
Default case: far side, 1 m from the HIVE pivot plane, release 0.737 m, wheel about 2800-4700 rpm (98 mm), v about
6-10 m/s, launch 74-81 deg, backspin S about 1 (all user/ASSUMED shot inputs from the task).

Labels (HANDOFF section 5): **CONFIRMED** (official document or CAD), **user**, **ASSUMED**, **derived** (arithmetic on
labelled inputs), **PREDICTED** (output of this repo's model). Pickleball and other-ball numbers are **proxies**, not
POLLEN facts. Every backspin result here has its no-spin twin next to it. Nothing here shows repeatability.

## 0. Game and rules correction

The task text says "FTC DECODE / 2025-26". That is wrong for this project. The game is **BIOBUZZ 2026-27** (HANDOFF
section 1; Competition Manual TU07). The manual excerpts read for this file do not mention DECODE. All rules below come from
BIOBUZZ.

Scoring and HIVE rules (CONFIRMED, Competition Manual TU07,
https://ftc-resources.firstinspires.org/ftc/game/cm-html/BIOBUZZ%20Competition%20Manual%20-%20TU07.htm):

- Section 10.5.1: "At the end of the MATCH, any POLLEN and/or NECTAR left in an upward-facing CELL will earn points".
- Section 10.5: assessment of CELL contents happens "after all SCORING ELEMENTS and ROBOTS have come to rest".
  So a **rim-in or rattle-in counts** if the ball stays. A clean entry that bounces back out does not count.
- Section 10.5(A): "Assessment of HIVE TIPS occurs throughout the MATCH". Section 10.5.1 defines a TIP as the HIVE moving to its other
  stable state, with the damper beginning "to contact the frame". It also says "LAUNCHING into the upward-facing CELL is the only
  allowed way to earn a HIVE TIP" and "The HIVES are designed to be bi-stable".
- G409: "A ROBOT may not catch or deflect a SCORING ELEMENT released by a TIPPED HIVE". A tip **dumps** the old
  up CELL. The new up CELL starts empty.
- G417: "ROBOTS may not manipulate the motion of the HIVE in any way other than by LAUNCHING". Shots that swing
  the HIVE are LAUNCHING. Any plan that relies on moving the HIVE on purpose should go to the official Q&A first
  (interpretation, not a ruling).

Consequence for the model (derived): "scored" = **retained at rest, or contributing to a TIP**. Retention over the
full rattle is the right metric, and docs/05 already uses it. Counting a mouth crossing would not be enough.

## 1. What the HIVE CELL is made of (CONFIRMED unless labelled)

Sources: Initial Field Element Assembly Guide V1.0 (https://ftc-resources.firstinspires.org/ftc/archive/2027/field/initialfieldguide),
Event Field Setup Guide V1.0 (https://ftc-resources.firstinspires.org/ftc/archive/2027/field/eventfieldguide),
Field Acceptance Checklist Rev 26-27.2 (https://ftc-resources.firstinspires.org/ftc/archive/2027/field/field-check).

| part | what | label |
|---|---|---|
| Hive Bottom Skin am-5870 | flat 11.625 x 34.75 in, bent into the floor plus both side walls (20 + 2 x 7.61 = 35.2 in, derived) | CONFIRMED size; bend derived |
| Hive Top Skin am-5869 | 11.625 x 23.4 in, the two roof slopes | CONFIRMED |
| Back Skin am-5871 | closes the CELL back | CONFIRMED |
| skin material | "clear plastic", "protective film off both sides". The polymer is **not named**. Polycarbonate is ASSUMED | CONFIRMED / ASSUMED |
| Goal Rib am-5866 | "molded" rib with hex pockets; skins "bend"/"snap" into its grooves. It forms the rounded mouth lip | CONFIRMED |
| Churro Lite am-3666 + cable ties | cable ties with "heads inside the Cell", 6 per CELL at the churros | CONFIRMED |
| pivot | am-4457 8 mm flanged ball bearings, stepped axle am-5881 | CONFIRMED |
| stops | Linear Damper am-1762 press-fit in Damper Holder am-5864 | CONFIRMED |
| ballast | #10 washers (am-1523) on a 10-32 x 2 in screw "at the end of each Cell nearest its opening" | CONFIRMED |

Provenance flag: `data/hive_geometry.json` (the `up_floor` and related prov strings) calls the bottom skin "am-5888". The
assembly guide calls the Hive Bottom Skin **am-5870**. The geometry is unaffected. Check the part name in the STEP before fixing
the string, because the CAD and the guide may use different numbers.

POLLEN: 2.8 in diameter, 0.055 lb (24.9 g). NECTAR: 3.6 in, 0.091 lb (41 g). The pairing comes from the AndyMark listing
(https://andymark.com/products/biobuzz-scoring-elements?variant=47194281148588), which lists "2.8 in., 3.6 in." and
"0.055 lbs., 0.091 lbs" without saying which goes with which. Sizes CONFIRMED, pairing derived. The listing gives no material
and no hole data.

## 2. Summary table

Sizes are at the default case unless noted. "Model" = the current repo (src/contact.py, src/hive.py, viz/explorer).

| # | effect | size on this shot | in model? | priority |
|---|---|---|---|---|
| 2.1 | POLLEN-on-skin/rib normal COR e (and its speed dependence) | S1 retained cells 50-151 across e 0.3-0.8; S0 twin 154-179 (PREDICTED, docs/05 3.3) | yes, swept, e unknown | **highest** |
| 2.2 | sliding friction mu, tangential e_t | mu "much less than e"; e_t, I_b within +-7 mm (PREDICTED) | yes, swept | medium |
| 2.3 | rim-in at the far lip | far-rim band 30 mm (S0) to 55 mm (S1) of extra width (PREDICTED) | yes (2D) | understood |
| 2.4 | skin panel compliance (thin clear skins vs stiff rib) | unknown; it lowers e on skin centres compared with the rib | no (one e everywhere) | medium |
| 2.5 | HIVE swing on impact | e change about 1%; lip moves about 0.1 mm during contact, up to about 9 mm over a 0.1 s rattle (derived) | no | low for first contact |
| 2.6 | real tilt and lip-height variation | lip 53.5 +- 0.5 in = +-12.7 mm = +-1.5 deg; counts move 20-25% (PREDICTED) | bounds only | medium |
| 2.7 | balls and NECTAR already in the CELL | 0 to about 7 POLLEN, plus 3 NECTAR at match start; head-on hit leaves about 25% of the normal speed | no | **high** (unmodelled) |
| 2.8 | 3D pentagon roof and side walls | -6.6 to -6.8 mm gate even on the centre line; -0.646 mm per mm of lateral offset (derived) | no (2D, linear roof drop) | **high** for oblique shots |
| 2.9 | cable-tie heads, holes, seams | unknown local deflections | no | low; inspect |
| 2.10 | TIP during a volley | the target turns over; the next ball meets a different CELL | no | high for rapid fire |

## 2.1 Normal COR e of POLLEN on the HIVE (skin and rib)

**What.** The fraction of normal speed kept in a bounce, e = -v_n'/v_n. It sets how far a floor or back-wall bounce
throws the ball back toward the mouth.

**Best numbers.** None measured for POLLEN on the HIVE (status: unknown, grade D in research/COMPLETENESS.md).
- Proxy (pickleball, not POLLEN): USA Pickleball / IPF equipment standards, dropped from 78 in onto granite, rebound
  30-34 in. That gives e = sqrt(30/78)..sqrt(34/78) = 0.62-0.66 (derived) at about 6.2 m/s, on a rigid surface.
  Sources: https://theipf.org/assets/userdocs/IPF_Equipment_Standards_Manual2023v1.2.pdf ;
  https://www.pickleball.ph/uploads/1/2/5/9/125919777/-_official_equipment_standards_manual.pdf
- Proxy: pickleball COR 0.20 at 26.8 m/s against a paddle-speed impact (van Wyk; see LITERATURE_SYNTHESIS.md).
  Hollow PE balls lose e quickly with speed.
- Proxy (hollow shell, no holes): table-tennis ball normal COR about 0.88, contact about 0.68 ms (Eur J Phys report via
  R. Cross, https://www.physics.usyd.edu.au/~cross/BOUNCE.htm). This is an upper reference for a thin hollow shell only.
- Repo sweep: e 0.3-0.8 (ASSUMED range). The arrival normal speeds at the CELL are about 2-5 m/s (PREDICTED), lower
  than the proxy test speeds, so e on the HIVE could sit above the 6 m/s pickleball value.

**Size on this shot (PREDICTED, docs/05 3.3, h 0.737, d 0.90, mean over mu):**

| e | S0 (no spin) retained cells | S1 nom retained cells |
|---|---|---|
| 0.3 | 179 | 151 |
| 0.45 | 165 | 66 |
| 0.6 | 156 | 50 |
| 0.8 | 154 | 89 |

The no-spin result barely depends on e (+-8%). The backspin result changes 3x and is not monotonic. **e is the
number that decides whether S about 1 costs a lot or a little.** More spin is not better at any e in this table.

**In model.** Yes. src/contact.py: P_n = -(1+e) m v_cn, with one e for every surface.

**How to add speed dependence.** Replace the constant with e(v_n) = e_0 / (1 + (v_n / v_*)^p), fitted to drop data.
Alternatively, use a table lookup from the measured drops. Keep the 0.3-0.8 sweep until the data exist.

**How to measure on real POLLEN.**
1. Get a flat offcut of the same clear skin (or a spare am-5870). Clamp it on a rigid block, then repeat with it
   clamped only at the edges like the real CELL.
2. Drop POLLEN from 0.2, 0.5 and 1.3 m (v = 2.0, 3.1, 5.0 m/s, derived from v = sqrt(2gh)). Film at 240 fps or faster
   beside a ruler.
3. e = sqrt(h_rebound / h_drop), or use the speeds from the video. n >= 10 per height, per surface (skin centre, rib lip,
   back skin).
4. Repeat on a field HIVE CELL floor if one is available. This is research/COMPLETENESS.md test T5.

## 2.2 Friction mu and tangential restitution e_t

**What.** In an oblique hit the contact patch either slides (Coulomb, |P_t| = mu P_n) or grips. When it grips, it can
spring back (e_t > 0). This is what turns backspin into a "kick".

**Best numbers.**
- LDPE on PC, dry, pin-on-ring, mu about 0.17 initial and 0.166 after 1800 s (Marzouk, Tribologia 5/2012, abstract only;
  https://yadda.icm.edu.pl/baztech/element/bwmeta1.element.baztech-ea3f2d11-04a1-4d71-995a-58472f840ac4). This is a
  material-pair proxy. POLLEN's polymer is not confirmed as LDPE, and the skins are not confirmed as PC.
- Cross R. (2014), "Oblique bounce of a rubber ball", Exp Mech 54:1523-1536, DOI 10.1007/s11340-014-9938-3 (abstract):
  a hollow ball showed much higher sliding friction than a superball, gripped at all angles tested, and the friction
  force reversed once or twice during contact. The lesson is that **steady sliding mu from a tribometer can understate
  bounce grip**. Cross 2002 (in LITERATURE_SYNTHESIS.md) also reports in-bounce mu about 3x below static for other
  balls. Together these mean that the sign of the error is not known in advance.
- Repo sweep: mu 0.2-0.8, e_t 0 (0.3 spot check). Both ASSUMED.

**Size (PREDICTED, docs/05).** Retention changes much less with mu than with e. I_b and e_t move results by about
+-7 mm. First contacts at the far rim stick in 100% of S0 cases vs 86% at S1. At the near rim, 90% (S0) vs 63% (S1).

**In model.** Yes (Cross 2005 stick/slip law, m_t = m alpha/(1+alpha), alpha 0.63).

**How to measure.**
1. Static mu: tilt a skin offcut until a non-rolling POLLEN (two balls glued together) slides; mu_s = tan(theta).
2. Bounce mu and e_t: throw POLLEN with no spin at about 45 deg onto the skin and film the bounce at 240 fps or faster
   with a marked ball. Read the spin after the bounce, omega'. If the ball rolls out, it gripped. If it slides, the
   sliding branch gives mu = |delta v_t| / ((1+e) v_n).

## 2.3 Rim-in contacts that still score

**What.** A ball that clips the lower (far) lip of the up CELL can still drop in and stay. Section 10.5 counts it if it is at rest
inside. Backspin acts differently at each rim (docs/05 table 1.2, PREDICTED):
- At the **far rim** (lower lip), a backspin "check" pushes the ball into the CELL.
- At the **near rim** (roof end), the kick goes around the roof corner, away from the mouth.
- On the **floor** after a clean entry, the kick drives the ball to the back-wall/roof corner, and it can rebound out.

**Size (PREDICTED, docs/05, e 0.6, mu 0.4, v_i 5 m/s, Part A):**
- Retained width: S0 183 mm (clean 143) vs S1 76 mm (clean 17, 128 mm of clean entries bounced out) vs S2 38 mm.
- The far-rim contact band is 30 mm at S0 and 55 mm at S1.
- Near-miss rescue (cells within 0.1 m/s / 0.5 deg of a clean entry): S0 4.5-6.7%, S1 9-12%.
- Retained fraction by first-contact zone: far rim S0 0.36 / S1 0.60 / S2 0.40; floor S0 1.00 / S1 0.086 / S2 0;
  near rim 0.028 / 0.015 / 0.003.
- Net: backspin gains on rim clips and loses more on clean entries. S1 >= S0 in only 2 of 80 (h, d, e, mu) combinations,
  both ties at e 0.3.

**In model.** Yes, in the 2D centre section. It has one e and one mu for every surface, a static HIVE, an empty CELL, and no 3D roof.

**How to add.** Already present. The next steps are surface-specific e and mu (rib vs skin) and the missing effects below.

**How to measure.** Use replica CELL test T6 (COMPLETENESS.md), n >= 30 per aim point. Aim deliberately at the far lip,
at +-20 mm steps across it, and log retained / out at rest. Do it with low spin and with high spin (twin runs).

## 2.4 Skin panel compliance

**What.** The skins are thin clear plastic held at the edges by the rib grooves. Where the ball hits a skin away from
a rib, the panel deflects and rings. Some of the energy goes into the panel. So e (and maybe the grip) on the skin
centre is lower than on the rib or a rigid block. The mouth lip is the moulded rib, which is stiffer.

**Numbers.** Skin thickness and polymer are not given (unknown). No measurement exists. A rough mass ratio is the only
estimate: POLLEN 25 g against a skin area of a few hundred cm^2 at about 1 mm thick (ASSUMED, about 30-60 g of panel
taking part, derived). That ratio is not small. The loss could be a large fraction of the bounce energy, but its size
is unknown.

**Size on this shot.** Floor and back-wall bounces happen on skins, so this matters most for bounce-outs after a clean
entry, which is the zone where S1 loses most. A lower effective e on the floor and back skin reduces bounce-outs
(see 2.1: S1 at e 0.3 keeps 151 cells vs 50 at e 0.6, PREDICTED; S0 twin 179 vs 156).

**In model.** No. One e for all surfaces.

**How to add.** Give contact.py a surface tag: e_rib and mu_rib for the lip segments, and e_skin(v) for the floor, back
and roof. Optionally use a two-mass model, ball plus panel effective mass m_p with stiffness k_p, for the panel.

**How to measure.** Repeat the 2.1 drop test with the skin clamped only at its edges like the CELL, at the floor centre
and near a rib. The difference between the two is the compliance effect.

## 2.5 HIVE swing when hit

**What.** The HIVE rotates on ball bearings and rests on a damper. A ball impulse on the lip or floor gives the HIVE a
small angular velocity. This changes the bounce and moves the lip during a rattle. Field Acceptance 2.2 says the HIVE
"experiences continuous, smooth movement when moved by hand" (CONFIRMED low friction). Check 2.7 says the dampers
"prevent HIVES from 'bouncing' after a tip".

**Numbers (derived from ASSUMED HIVE inertia):**
- Lip lever arm from the pivot: r = sqrt(0.4907^2 + 0.2402^2) = 0.546 m (derived from CONFIRMED CAD points).
- HIVE inertia I_H about 0.5-1 kg m^2 (ASSUMED; roughly 2 kg per CELL of skins, rib, tube and ballast).
- Effective mass at the lip M_eff = I_H / r^2 = 1.7-3.4 kg (derived). m / M_eff is about 0.01.
- Ball angular impulse about m (1+e) v_n r_perp, about 0.025 x 1.6 x 4 x 0.5 = 0.08-0.1 N m s (derived, v_n about 4 m/s ASSUMED).
  This gives omega_H about 0.1-0.2 rad/s and HIVE kinetic energy about 0.005-0.01 J.

**Size on this shot (derived).**
- Effective e on the HIVE drops by about m/M_eff, about 1%. That is negligible next to the e uncertainty in 2.1.
- During the contact (about 1 ms) the lip moves about 0.17 x 0.546 x 0.001 = 0.1 mm. This is negligible.
- Over a rattle of about 0.1 s before the next bounce, about 0.017 rad = 1 deg if the damper does not stop it. At the lip
  that is 8.6 mm vertical (r cos, derived: 0.4907 m x 1 deg) or 9.5 mm of arc. This can matter for **second and later
  bounces** near the lip. The damper probably cuts it, but that is not measured.
- Relation to tipping (derived, rough): the tip threshold torque is about 7.5 POLLEN at the back wall,
  T_tip about 7.5 x 0.02495 x 9.81 x 0.177 = 0.33 N m (lever arm 0.177 m ASSUMED for balls resting at the back skin).
  One impact gives about 10% of the rough energy barrier to the other state (about 0.09 J, derived). The field checks
  require "Tossed In" calibration (Event Field Setup Guide 12.3, "Necessary") but treat "Gently Placed" only as
  "Preferred". So the **arrival impulse matters near the threshold** (CONFIRMED by the calibration procedure). The
  8th tossed ball tips the HIVE (Field Acceptance 2.5-2.6: 7 POLLEN no tip; toss the 8th, tip).

**In model.** No. The HIVE is fixed.

**How to add.** Add one rotational DOF with a stop:
I_H theta_dd = sum(r_i x F_i) + tau_gravity(theta, contents) - c theta_d,
plus a one-sided spring-damper at the stop. Apply each ball impulse P to both bodies:
ball dv = P/m; HIVE d omega = (r x P)/I_H. Equivalently, replace m by the reduced mass
m* = 1 / (1/m + r_perp^2 / I_H) in P_n = -(1+e) m* v_rel,n.

**How to measure.**
1. Film the lip side-on at 240 fps or faster while tossing single POLLEN in. Read the lip deflection and how long it
   lasts.
2. I_H: hang known masses at the lip and time the motion after release. Or weigh one CELL and use a CAD estimate.
3. Count tossed POLLEN to tip on the field HIVE several times. Expected 8 (CONFIRMED calibration target), but "Some
   variation in Hive operation is expected" (Field Mitigation Guide 26-27.1).

## 2.6 Real tilt and lip height

**What.** The up CELL tilt is 30 deg (CONFIRMED, CAD and manual figures) when it rests on its damper. The real HIVE
differs. Field Acceptance 1.13: the lip must sit at 53.5 +- 0.50 in "When upright (opposite damper is fully depressed)".
Dampers compress, and the Event Field Setup Guide says CELLs may be "tweaked" by hand during calibration.

**Numbers (derived).** 53.5 in = 1.3589 m against the model's lower lip at 1.3565 m (2.4 mm apart, a good check). The
+-0.5 in tolerance is +-12.7 mm, about +-1.5 deg at 8.6 mm/deg. That matches the repo's 28.5-31.5 deg bound.

**Size (PREDICTED, docs/05 3.5, d 0.90).** S0 143 / 156 / 186 retained cells at 28.5 / 30 / 31.5 deg; S1 twin 42 / 53 / 53.
So counts move by 20-25%, and S0 > S1 at every tilt.

**In model.** As bounds only (tilt sweep), not as a per-match random variable.

**How to add.** Draw the tilt per trial from N(30, 0.5) deg, clipped to 28.5-31.5 (ASSUMED spread), when computing
P_tight / P_loose.

**How to measure.** Measure the lip height on any field you can reach (tape from the tile). That gives the tilt directly.

## 2.7 Balls and NECTAR already in the CELL

**What.** The CELL is rarely empty. It starts with 3 NECTAR (data/hive_geometry.json note; Field Acceptance 2.3-2.4: 3
NECTAR + 2 POLLEN no tip, toss 1 more, tip). Up to 7 POLLEN sit in it before the 8th tips it (CONFIRMED calibration).
After a TIP the new up CELL is empty and the old contents spill (G409). Resting balls gather at the back-skin corner.
Seven POLLEN side by side take 7 x 71 = 497 mm of the 508 mm (20 in) floor width (derived), so one row fills the back.

**Numbers (derived).**
- An equal-mass head-on hit with e_bb about 0.5 (ASSUMED) leaves the incoming ball (1 - e_bb)/2 = 25% of its normal
  speed. The struck ball takes (1 + e_bb)/2 = 75%.
- An incoming POLLEN hitting a resting NECTAR (41 g vs 25 g): the incoming ball keeps
  (m1 - e m2)/(m1 + m2) = (25 - 0.5 x 41)/66 = +0.07 of its normal speed (derived). Almost all of it is absorbed.
- Resting balls sit in the back-wall corner, at u about 0.169-0.24 m from the pivot (derived from the CAD frame).

**Size on this shot.** Not computed. Direction (reasoned, not simulated): resting balls absorb the floor/back-wall
rebound that drives most S1 bounce-outs (2.3: 128 mm of clean S1 entries lost; S0 twin loses far less). So a partly
filled CELL **probably reduces bounce-outs**, especially for backspin shots. But a struck resting ball can be knocked
out over the lower lip. And the pile raises the effective floor near the back.

**In model.** No (docs/05 states no NECTAR in the section).

**How to add.** Add N resting discs (2D) or spheres (3D) at the back corner as extra bodies. Ball-ball impulse:
P = -(1 + e_bb) m_red (v_rel . n) n with m_red = m1 m2/(m1 + m2), plus the same stick/slip tangential law. Integrate the
struck balls too, and count retention for all of them at rest.

**How to measure.** In the replica CELL (T6), run the same aim set with 0, 3 NECTAR, 3 NECTAR + 3 POLLEN, and 6 POLLEN
already inside. Log retained at rest for the shot ball **and** for anything knocked out.

## 2.8 3D CELL: pentagon roof and side walls

**What.** The mouth is a pentagon, not the 2D slot of the section model. Its size is 20 in wide, 14.07 in tall at the
centre and 7.61 in at the side walls (CONFIRMED, docs/01). The roof is two slopes meeting at a ridge, with slope s about
0.646 from the manual numbers or 0.639 from hive.py (h0 = 0.3556) (derived).

**Numbers (derived).**
- A sphere under a sloped roof touches it when its centre is R sqrt(1 + s^2) below the roof line, not R.
  With R = 35.6 mm, that is 42.2-42.4 mm, so 6.6-6.8 mm more clearance is lost than the 2D section assumes.
  This holds **on the centre line too**, because the ridge has a slope on each side.
- The ball-centre gate across the mouth in the section is 0.286 m in 2D. In 3D it is about 0.2797 - 0.646 |y| m, where y is
  the lateral offset of the ball centre from the CELL centre plane.
- Side walls bound |y| <= 0.254 - R = 0.2185 m.
- Off-centre, the near rim moves by +0.5 Delta in x and -0.866 Delta in z, with Delta = 0.646 |y|. The mouth normal does
  not change, so the entry window narrows from the near-rim side.
- The unfavourable side needs a descent of more than 60 deg; the ball fits at more than about 71.5 deg (docs/01). Each mm
  of gate lost raises that minimum.

**Size on this shot.**
- On the centre line: -6.7 mm of gate (derived), about 2-4% of the PREDICTED 183 mm (S0) / 76 mm (S1) retained width.
  This is small but systematic, and in the optimistic direction for the current model.
- A lateral aim error of +-20 mm costs another 13 mm of gate (derived). At |y| 0.1 m the gate is 0.215 m, 25% less than
  in 2D.
- Oblique shots (heading psi off the CELL axis) travel sideways inside the 0.305 m deep CELL and can reach a side wall.
  The JS solver uses s_eff(psi) = min(0.3 tan psi, 0.2) and flags psiWall 35.57 deg as "not modelled".

**In model.** Partly. hive.py `_roof_drop` lowers the roof linearly with lateral offset but ignores the sloped-roof
sphere clearance (it uses R, not R sqrt(1+s^2)) and the side walls. JS: the s_eff heuristic only.

**How to add.**
1. Quick fix: in `_roof_drop` and the JS gate, use R sqrt(1 + s^2) for clearance under a sloped roof, and clamp
   |y| <= 0.254 - R.
2. Full fix: 3D sphere-vs-plane contact for floor, back, both roof planes and both side walls (the planes are flat
   skins, so this is exact). Rim edges (the moulded lip) become sphere-vs-segment contacts with a normal along the
   line from the closest point on the edge to the centre.

**How to measure.** In the replica CELL, roll or drop POLLEN in at y = 0, 0.1 and 0.2 m and find the deepest roof
contact. Use T6 aim sets at lateral offsets too.

## 2.9 Cable-tie heads, holes and seams

**What.** Cable-tie heads sit inside the CELL (6 per CELL, CONFIRMED). The skins snap into rib grooves, which can leave
seams. If POLLEN has holes (unknown: AndyMark does not say), a hole edge can catch a sharp edge and change spin or
direction.

**Numbers.** Head height is unknown (about 4-6 mm for common ties, ASSUMED). The broad moulded rib makes hole-catching on
the lip unlikely (reasoned, not measured).

**Size.** Unknown and local. A ball that rolls over a tie head gets a random deflection. This adds scatter to the rattle,
not a bias.

**In model.** No (contact.py line 73 states no hole-catching).

**How to add.** Only if tests show it matters: small bumps at the measured tie locations, or extra scatter on
the floor contact.

**How to measure.** Photograph the inside of a field or replica CELL with a scale and mark tie locations. Check POLLEN
for holes and seam lines.

## 2.10 TIP during a volley

**What.** The 8th POLLEN (or the matching mix with NECTAR) tips the HIVE (CONFIRMED calibration). If several balls are in
flight, the ones after the tipping ball arrive at a HIVE that is moving or has already flipped. The old up CELL dumps its contents
(G409). The new up CELL is the other one, with its mouth on the other side.

**Size.** Unknown. It depends on the tip duration (not measured) and the shot spacing. A tip that takes about 0.5 s
(ASSUMED) is longer than the gap between balls in a fast volley.

**In model.** No.

**How to add.** In a match-level sim, track the CELL count and switch the target after the tipping ball comes to rest,
or treat in-flight balls as misses while the HIVE moves.

**How to measure.** Film a tip at 240 fps: time from the tipping ball's arrival to damper contact. Repeat several times.

## 3. What to do first (ranked)

1. Measure e of POLLEN on the clear skin and on the rib at 2-5 m/s (2.1, 2.4). This decides the size of the spin
   penalty (S1 50-151 cells vs S0 154-179, PREDICTED).
2. Add resting balls / NECTAR to the CELL sim (2.7). It is unmodelled and probably changes S1 bounce-outs the most.
3. Fix the 3D roof clearance R sqrt(1+s^2) and the side-wall clamp (2.8). This is cheap and removes a systematic
   +6.7 mm optimism.
4. Add the tilt as a random variable (2.6), then the HIVE DOF if lip-swing video shows more than a few mm (2.5).

## Sources

- BIOBUZZ Competition Manual TU07: https://ftc-resources.firstinspires.org/ftc/game/cm-html/BIOBUZZ%20Competition%20Manual%20-%20TU07.htm
- Field Acceptance Checklist Rev 26-27.2: https://ftc-resources.firstinspires.org/ftc/archive/2027/field/field-check
- Event Field Setup Guide V1.0: https://ftc-resources.firstinspires.org/ftc/archive/2027/field/eventfieldguide
- Initial Field Element Assembly Guide V1.0: https://ftc-resources.firstinspires.org/ftc/archive/2027/field/initialfieldguide
- Field Mitigation Guide 26-27.1 (via the FTC field resources pages above)
- AndyMark BIOBUZZ scoring elements: https://andymark.com/products/biobuzz-scoring-elements?variant=47194281148588
- IPF Equipment Standards Manual 2023 v1.2: https://theipf.org/assets/userdocs/IPF_Equipment_Standards_Manual2023v1.2.pdf
- USA Pickleball equipment standards (copy): https://www.pickleball.ph/uploads/1/2/5/9/125919777/-_official_equipment_standards_manual.pdf
- Cross R. (2014) Oblique bounce of a rubber ball. Exp Mech 54:1523-1536. DOI 10.1007/s11340-014-9938-3 (abstract only)
- Cross R. bounce notes: https://www.physics.usyd.edu.au/~cross/BOUNCE.htm
- Marzouk, LDPE/PC friction, Tribologia 5/2012: https://yadda.icm.edu.pl/baztech/element/bwmeta1.element.baztech-ea3f2d11-04a1-4d71-995a-58472f840ac4 (abstract only)
- Repo: docs/01_hive_geometry.md, docs/05_contact.md, src/contact.py, src/hive.py, viz/explorer/physics.js and solver.js,
  research/COMPLETENESS.md, research/LITERATURE_SYNTHESIS.md
