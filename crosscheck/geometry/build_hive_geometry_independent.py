"""Independent HIVE geometry (crosscheck, PM-001).

Builds crosscheck/geometry/hive_geometry_independent.json (schema of docs/INTERFACES.md)
and hive_section_independent.png from numbers extracted from the OFFICIAL sources:
  * BIOBUZZ Competition Manual (TU07 HTML), section 9.6, Figures 9-8..9-11, 10-3
  * Field Acceptance Checklist (rev 26-27.2) item 1.13
  * Official field CAD, STEP export v26-27.2 (parsed with cad_tools/step_parse.py)
It does NOT read data/hive_geometry.json or docs/01_hive_geometry.md.

Frames
  CAD world (inches): Y up, pivot axes along CAD X at Y=43.950, Z=0.  Tipping plane = CAD Y-Z.
  "flat" hive frame (inches): the hive rotated back to level (Rx(-30 deg) about the pivot);
      z' = along the cell axis in the tipping plane, y' = hive "up". Up-cell at z'<0.
  INTERFACES HIVE frame (metres): x = CAD Z, y = CAD X, z = CAD Y (right-handed).
Run:  py -3.13 crosscheck/geometry/build_hive_geometry_independent.py
"""
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
IN = 0.0254  # m per inch (exact)

CAD = ("official field CAD STEP v26-27.2 (https://ftc-resources.firstinspires.org/ftc/archive/2027/field/"
       "field-cad-step), parsed with crosscheck/geometry/cad_tools/step_parse.py")
CM = "https://ftc-resources.firstinspires.org/ftc/game/cm-html/BIOBUZZ%20Competition%20Manual%20-%20TU07.htm"
CHK = "https://ftc-resources.firstinspires.org/ftc/archive/2027/field/field-check"

# ---------------------------------------------------------------- inputs (inches)
PIVOT_Z = 43.95          # confirmed: CM 9.6.1 + Fig 9-8 "43.95 in. (111.65 cm)"; CAD 43.950
BALL_R = 0.0355          # m, from INTERFACES / HANDOFF (POLLEN 2.8 in dia -> 1.40 in radius)
r_in = BALL_R / IN

# flat-frame section of the UP cell at the cell centre plane (CAD, see NOTES.md)
Z_MOUTH = -21.456        # outer face of outer Goal Rib (mouth plane)
Z_RIB_IN = -19.456       # inner face of outer Goal Rib
Z_BACK_IN = -9.438       # inside face of Back Skin
Z_BACK_OUT = -9.418      # outside face of Back Skin
Y_FLOOR = -1.488         # Bottom Skin top surface
Y_LIP_TOP = -1.50        # top of Goal Rib bottom bar (lip), ~flush with floor
Y_UNDER = -2.972         # bottom of Goal Rib bottom bar (lowest point of cell)
Y_ROOF_IN = 12.50        # inner apex of roof at cell centre (lip top + 14.0 in, Fig 9-11; CAD 12.45-12.70)
Y_ROOF_OUT = 13.057      # outer apex of Goal Rib

TILT_NOM = 30.0          # confirmed: CM Fig 9-10 "30 deg"; CAD every HIVE part rotated 30.000 deg
CHECK_BOTTOM = 53.5      # confirmed: checklist 1.13, +/-0.50 in, "upright (opposite damper fully depressed)"
CHECK_TOL = 0.5

# hub (hive-fixed, flat frame) convex hulls, CAD
HUB = {
    "pivot_bracket": [[6.51, -1.75], [1.21, 0.83], [-1.21, 0.83], [-6.51, -1.75], [-6.89, -2.32],
                      [-6.39, -2.71], [6.39, -2.71], [6.89, -2.32]],
    "damper_holder_a": [[4.15, -1.76], [3.96, -0.51], [3.33, -0.61], [2.71, -0.72], [2.56, -0.95],
                        [2.52, -2.0], [2.93, -2.34], [3.97, -1.98]],
    "damper_holder_b": [[-4.15, -1.76], [-3.96, -0.51], [-3.33, -0.61], [-2.71, -0.72], [-2.56, -0.95],
                        [-2.52, -2.0], [-2.93, -2.34], [-3.97, -1.98]],
    "base_tube_up_to_hub": [[-9.418, -2.71], [-4.71, -2.71], [-4.71, -1.71], [-9.418, -1.71]],
    "base_tube_down_to_hub": [[9.418, -2.71], [4.71, -2.71], [4.71, -1.71], [9.418, -1.71]],
}
# frame (world-fixed, CAD (Z, Y) inches) convex hulls
FRAME = {
    "frame_top_corner": [[-0.43, 43.96], [-1.52, 39.88], [-0.81, 39.49], [0.81, 39.49], [1.49, 39.8],
                         [1.52, 39.88], [0.43, 43.96], [-0.02, 44.21]],
    "frame_top_bar": [[-0.5, 40.95], [0.5, 40.95], [0.5, 41.95], [-0.5, 41.95]],
    "frame_acm_panel_a": [[-1.66, 40.02], [-4.28, 34.12], [-4.18, 34.07], [-1.55, 39.97]],
    "frame_acm_panel_b": [[1.66, 40.02], [4.28, 34.12], [4.18, 34.07], [1.55, 39.97]],
    "frame_leg_a": [[-0.91, 41.4], [-19.07, 0.62], [-18.15, 0.22], [0.0, 40.99]],
    "frame_leg_b": [[0.0, 40.99], [18.15, 0.22], [19.07, 0.62], [0.91, 41.4]],
}
FRAME_NOTE = {
    "frame_leg_a": "3D: leg slopes along y (pivot axis) from y=24.3 in at the foot to 12.3 in at the top; it lies "
                   "in the cell-centre plane only near the apex. Included as its full projection (conservative).",
}
FRAME_NOTE["frame_leg_b"] = FRAME_NOTE["frame_leg_a"]
for k in ("frame_acm_panel_a", "frame_acm_panel_b", "frame_top_bar"):
    FRAME_NOTE[k] = "spans y = -15.1..15.1 in (top bar -12..12 in), i.e. crosses both HIVE centre planes"


def cell_segments(sign):
    """Up cell (sign=-1, z'<0) or down cell (sign=+1) as named flat-frame segments."""
    def P(z, y):  # inputs are given for the up cell (z'<0); mirror z' for the down cell
        return (z if sign < 0 else -z, y)
    pre = "up" if sign < 0 else "down"
    segs = [
        ("lip_front", P(Z_MOUTH, Y_UNDER), P(Z_MOUTH, Y_LIP_TOP)),
        ("lip_top", P(Z_MOUTH, Y_LIP_TOP), P(Z_RIB_IN, Y_LIP_TOP)),
        ("floor", P(Z_RIB_IN, Y_FLOOR), P(Z_BACK_IN, Y_FLOOR)),
        ("back_skin_inner", P(Z_BACK_IN, Y_FLOOR), P(Z_BACK_IN, Y_ROOF_IN)),
        ("roof_inner", P(Z_BACK_IN, Y_ROOF_IN), P(Z_MOUTH, Y_ROOF_IN)),
        ("roof_lip_front", P(Z_MOUTH, Y_ROOF_IN), P(Z_MOUTH, Y_ROOF_OUT)),
        ("roof_outer", P(Z_MOUTH, Y_ROOF_OUT), P(Z_BACK_OUT, Y_ROOF_OUT)),
        ("back_outer", P(Z_BACK_OUT, Y_ROOF_OUT), P(Z_BACK_OUT, Y_UNDER)),
        ("underside", P(Z_BACK_OUT, Y_UNDER), P(Z_MOUTH, Y_UNDER)),
    ]
    return [(pre + "_cell_" + n, a, b) for n, a, b in segs]


def poly_segments(name, pts):
    return [(f"{name}_{i}", tuple(pts[i]), tuple(pts[(i + 1) % len(pts)])) for i in range(len(pts))]


def flat_to_world(p, tilt_deg):
    """flat (z', y') inches -> INTERFACES pose_neg (x, z) metres."""
    t = math.radians(tilt_deg)
    zf, yf = p
    x = math.sin(t) * yf + math.cos(t) * zf
    z = PIVOT_Z + math.cos(t) * yf - math.sin(t) * zf
    return [round(x * IN, 5), round(z * IN, 5)]


def bottom_of_opening(tilt_deg):
    return flat_to_world((Z_MOUTH, Y_LIP_TOP), tilt_deg)[1] / IN


def solve_tilt(h):
    lo, hi = 0.0, 60.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if bottom_of_opening(mid) < h:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


TILT_LO = solve_tilt(CHECK_BOTTOM - CHECK_TOL)
TILT_HI = solve_tilt(CHECK_BOTTOM + CHECK_TOL)
TILT_CHECK_MID = solve_tilt(CHECK_BOTTOM)


def build_pose(mirror):
    t = TILT_NOM
    sx = -1.0 if mirror else 1.0
    def W(p):
        x, z = flat_to_world(p, t)
        return [round(sx * x, 5), z]
    def F(p):  # frame point CAD (Z, Y) inches -> world; frame is symmetric so mirror is harmless
        return [round(sx * p[0] * IN, 5), round(p[1] * IN, 5)]
    obs = []
    for n, a, b in cell_segments(-1) + cell_segments(+1):
        obs.append({"name": n, "p0": W(a), "p1": W(b), "prov": "confirmed+derived: " + CAD +
                    "; dims cross-checked vs CM Fig 9-9/9-11; rotated by tilt_deg.value about pivot"})
    for k, pts in HUB.items():
        for n, a, b in poly_segments("hub_" + k, pts):
            obs.append({"name": n, "p0": W(a), "p1": W(b), "prov": "derived: convex hull of CAD part (" + CAD + ")"})
    for k, pts in FRAME.items():
        for n, a, b in poly_segments(k, pts):
            d = {"name": n, "p0": F(a), "p1": F(b), "prov": "derived: convex hull of CAD frame part, fixed in world (" + CAD + ")"}
            if k in FRAME_NOTE:
                d["note"] = FRAME_NOTE[k]
            obs.append(d)
    mouth = {"p0": W((Z_MOUTH, Y_LIP_TOP)), "p1": W((Z_MOUTH, Y_ROOF_IN)),
             "prov": "derived: mouth plane = outer face of the outer Goal Rib; p0 = lip top, p1 = inner roof apex (cell centre plane)"}
    inside = [W((Z_MOUTH, Y_FLOOR + r_in)), W((Z_BACK_IN - r_in, Y_FLOOR + r_in)),
              W((Z_BACK_IN - r_in, Y_ROOF_IN - r_in)), W((Z_MOUTH, Y_ROOF_IN - r_in))]
    side = "pos" if mirror else "neg"
    reason = ("The upward CELL sits on the %s side and its mouth faces OUTWARD, away from the pivot: outward normal "
              "points %sx and 30 deg above horizontal (mouth plane 60 deg from horizontal; floor slopes down toward the "
              "Back Skin so a ball that crosses the mouth rolls in). From the %s side a ball moving toward the pivot "
              "enters directly. From the other side the ball must clear the roof (outer apex ~1.69 m) and then cross "
              "the mouth plane inward, which needs a descent steeper than 60 deg below horizontal just beyond the roof "
              "front edge." % ("+x" if mirror else "-x", "+" if mirror else "-", "+x" if mirror else "-x"))
    return {
        "tilt_deg": {"value": TILT_NOM, "low": round(TILT_LO, 2), "high": round(TILT_HI, 2),
                     "prov": ("confirmed value: CM Fig 9-10 '30 deg' (" + CM + ") and CAD (all HIVE parts at 30.000 deg). "
                              "low/high derived from Field Acceptance Checklist 1.13 'bottom of each CELL opening is "
                              "53.5 +/- 0.50 in above the tiles' (" + CHK + ") solved for tilt with the CAD lip point "
                              "(z'=%.3f, y'=%.2f in) and pivot 43.95 in; checklist midpoint gives %.2f deg."
                              % (Z_MOUTH, Y_LIP_TOP, TILT_CHECK_MID))},
        "obstacles": obs,
        "mouth": mouth,
        "inside": inside,
        "inside_prov": "derived: cell interior at the centre plane deflated by ball_radius on floor, roof and Back "
                       "Skin; mouth edge = mouth plane (ball centre past the mouth plane and in this box = retained). "
                       "Off-centre planes have a lower roof (see cell_opening_profile).",
        "favorable_side": side,
        "reason": reason,
    }


def main():
    out = {
        "units": "m",
        "source_note": "INDEPENDENT crosscheck; not derived from data/hive_geometry.json. See crosscheck/geometry/NOTES.md.",
        "ball_radius": {"value": BALL_R, "prov": "user/HANDOFF: POLLEN 2.8 in dia (AndyMark am-5851); not re-measured here"},
        "pivot": {"x": 0.0, "z": round(PIVOT_Z * IN, 5),
                  "prov": "confirmed: CM 9.6.1 'Frame supports 2 pivots with their axis 43.95 in. (111.65 cm) above the TILES' "
                          "(" + CM + "); CAD pivot bracket origin at 43.950 in. 43.95 in = 1.11633 m (manual's 111.65 cm is rounded)."},
        "poses": {"pose_neg": build_pose(False), "pose_pos": build_pose(True)},
        "y_extent": {"cell_width": 0.508, "low": 0.508, "high": round(20.21 * IN, 4),
                     "prov": "confirmed: CM 9.6.2 + Fig 9-11 opening 'approximately 20 in. (50.8 cm) wide'; CAD inner width "
                             "between Goal Rib side walls 20.21 in (x 2.65..22.87 in)"},
        "cell_opening_profile": {
            "frame": "mouth plane coordinates: u along pivot axis from cell centre, v up from lip top (m)",
            "polygon": [[-0.254, 0.0], [0.254, 0.0], [0.254, round(7.61 * IN, 4)], [0.0, round(14.0 * IN, 4)],
                        [-0.254, round(7.61 * IN, 4)]],
            "prov": "confirmed: CM Fig 9-11 (20 in wide, 7.61 in side-wall height, 14 in at apex); CAD agrees "
                    "(side wall 7.9-8.0 in to roof start, apex 14.0 in)"},
        "cell_depth": {"value": round(12.04 * IN, 4), "prov": "confirmed: CM Fig 9-9 '12.04 in (30.58 cm)'; CAD mouth plane to "
                       "Back Skin inner face 12.02 in"},
        "hive_layout": {
            "cell_back_to_back": {"value": round(18.84 * IN, 4), "prov": "confirmed: CM Fig 9-9 '18.84 in (47.85 cm)' between Back Skins; CAD 18.86 in"},
            "hive_overall_length": {"value": round(42.91 * IN, 4), "prov": "confirmed: CM Fig 9-9 '42.91 in (109.0 cm)'; CAD 42.91 in"},
            "red_blue_hive_centre_spacing_along_y": {"value": round(25.5 * IN, 4), "prov": "confirmed: CM Fig 9-10 '25.5 in (64.75 cm)'; CAD +/-12.758 in"},
            "top_of_opening_above_tiles": {"value": round(65.6 * IN, 4), "prov": "confirmed: CM Fig 9-10 '65.6 in (166.60 cm)'"},
            "bottom_of_opening_above_tiles": {"value": round(53.5 * IN, 4), "low": round(53.0 * IN, 4), "high": round(54.0 * IN, 4),
                                              "prov": "confirmed: CM Fig 9-10 53.5 in (135.90 cm); checklist 1.13 +/-0.50 in"},
            "bottom_of_hive_above_tiles": {"value": round(30.6 * IN, 4), "prov": "confirmed: CM Fig 9-10 '30.6 in (77.70 cm)'"},
            "frame_base": {"width_along_y": round(49.46 * IN, 4), "depth_along_x": round(38.95 * IN, 4),
                           "prov": "confirmed: CM 9.6.1/Fig 9-8 (49.46 in wide, 38.95 in deep at base)"},
        },
        "field": {
            "hive_location": "HIVE Structure at the centre of the FIELD (CM 9.6); pivot axes run toward the two ALLIANCE "
                             "walls; red HIVE on the red-alliance half (y<0 in CAD terms), blue on the blue half; CELLS tip "
                             "toward the audience and far walls (x in this frame).",
            "inner_wall_x": {"value": round(70.67 * IN, 4), "prov": "derived: CAD perimeter glass inner face at +/-70.67 in from field centre; CM 9.2 'approximately 144 in. by 144 in.'"},
            "robot_height_limit": {"value": round(29 * IN, 4), "start_config": round(18 * IN, 4),
                                   "prov": "confirmed: CM R105.A 18 x 24 x 29 in tall expansion volume after start; starting "
                                           "configuration 18 x 18 x 18 in"},
            "shooting_area": "No LAUNCH zone restriction found in the TU07 manual: LAUNCHING into the upward-facing CELL is "
                             "allowed from anywhere on the FIELD (G417 forbids other HIVE interaction; G409 no catching from a "
                             "TIPPED HIVE).",
        },
        "open_questions": [
            "Damper state at rest: CAD shows both Blum 970A plungers fully extended (0.49 in exposed) with the contacting "
            "tip touching the A-Frame at 30.000 deg, i.e. first contact. Full plunger travel would add up to ~8 deg "
            "(lever 3.57 in), which the checklist (53.5 +/- 0.5 in when the damper is fully depressed) does not allow. "
            "Real stroke/end stop unverified; tilt bounds here come from the checklist only.",
            "2D section is the cell-centre plane (most open). The roof drops to 7.61 in above the lip at the side walls "
            "(+/-10 in along y); a 3D check should use cell_opening_profile.",
            "Three NECTAR are preloaded against the Back Skin of each upward CELL at match start (Event Field Setup Guide "
            "11.1); not modelled as obstacles.",
            "A-Frame legs are 3D-inclined along y; included as full projections (conservative).",
            "Lip/roof thicknesses are from CAD; plastic part tolerances and skin sag are not published.",
        ],
    }
    path = os.path.join(HERE, "hive_geometry_independent.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("wrote", path)
    print("tilt from checklist: lo %.2f mid %.2f hi %.2f deg" % (TILT_LO, TILT_CHECK_MID, TILT_HI))
    for t in (TILT_LO, TILT_NOM, TILT_HI):
        print(" tilt %.2f: bottom of opening %.2f in, top of opening %.2f in, bottom of hive %.2f in, outer apex %.2f in" % (
            t, bottom_of_opening(t), flat_to_world((Z_MOUTH, Y_ROOF_IN), t)[1] / IN,
            flat_to_world((-Z_MOUTH, Y_UNDER), t)[1] / IN, flat_to_world((Z_MOUTH, Y_ROOF_OUT), t)[1] / IN))
    pn = out["poses"]["pose_neg"]
    print("pose_neg mouth", pn["mouth"]["p0"], pn["mouth"]["p1"])
    print("pose_neg inside", pn["inside"])
    plot(out)


def plot(out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(13, 6.5))
    for ax, key in zip(axs, ("pose_neg", "pose_pos")):
        p = out["poses"][key]
        for o in p["obstacles"]:
            c = "#1f5fa8" if "cell" in o["name"] else ("#777777" if o["name"].startswith("frame") else "#b5651d")
            ax.plot([o["p0"][0], o["p1"][0]], [o["p0"][1], o["p1"][1]], color=c, lw=1.2)
        m = p["mouth"]
        ax.plot([m["p0"][0], m["p1"][0]], [m["p0"][1], m["p1"][1]], "g--", lw=2, label="mouth")
        ins = np.array(p["inside"] + [p["inside"][0]])
        ax.fill(ins[:, 0], ins[:, 1], color="g", alpha=0.15, label="inside (ball centre)")
        ax.plot([0], [out["pivot"]["z"]], "k+", ms=12)
        ax.axhline(0, color="k", lw=0.8)
        ax.set_aspect("equal"); ax.set_xlim(-0.8, 0.8); ax.set_ylim(-0.02, 1.8)
        ax.set_title("%s (tilt %.0f deg, favorable side: %s)" % (key, p["tilt_deg"]["value"], p["favorable_side"]))
        ax.set_xlabel("x [m] (tipping plane)"); ax.set_ylabel("z [m] above tiles"); ax.grid(alpha=0.3)
        ax.legend(loc="lower right", fontsize=8)
    fig.suptitle("Independent HIVE section from official CAD + manual (cell-centre plane)")
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "hive_section_independent.png"), dpi=110)


if __name__ == "__main__":
    main()
