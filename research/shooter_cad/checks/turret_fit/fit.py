# Turret fit math for Head A (Concept A) on the 19705 Ri3D robot turret.
# Inputs: tf_a5/15/25.txt (per-part boxes from the "POLLEN turret fit" FeatureScript, head frame, mm).
# Head frame: x downrange, y = world plan axis (perpendicular to x), z up, F = origin.
# Every head part is extruded along y, so its plan (x-y) footprint is exactly its x-y box.
import math, os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
IN = 25.4

# ---- robot (assembly frame, mm, Z up) ----
FLOOR_Z = -6.0
PLATE_TOP_Z = 238.2            # rotating turret base plate top
T = (-54.536, 0.0)             # turret axis
ROBOT_X_DEPLOYED = (-336.8, 138.4)
ROBOT_X_FOLDED = (-232.0, 138.4)
ROBOT_Y = (-164.0, 164.0)
ROBOT_TOP_Z = 435.4            # rear slide arm top
SLIDES = [(68.4, 100.0), (68.4, -100.0)]
START = 18 * IN                # 457.2
EXP_W, EXP_L, EXP_H = 18 * IN, 24 * IN, 29 * IN
START_TOP_Z = FLOOR_Z + START  # 451.2
EXP_TOP_Z = FLOOR_Z + EXP_H    # 730.6


def load(alpha):
    parts = []
    with open(os.path.join(HERE, f"tf_a{alpha}.txt"), encoding="utf-8") as f:
        for ln in f:
            ln = ln.rstrip("\n")
            if ln.startswith("TF box"):
                box = [float(v) for v in ln.split()[2:]]
            elif ln.startswith("TF h"):
                h = [float(v) for v in ln.split()[2:]]
            elif "|" in ln and not ln.startswith("TF"):
                left, nums = ln.split("|")
                i, name = left.split(" ", 1)
                parts.append((int(i), name.strip(), [float(v) for v in nums.split()]))
    return box, h, parts


def support(parts, t_deg, a=(0.0, 0.0)):
    """max over all parts of (p - a).u(t) in plan; parts = list of boxes."""
    c, s = math.cos(math.radians(t_deg)), math.sin(math.radians(t_deg))
    best = -1e9
    for b in parts:
        x = b[1] if c >= 0 else b[0]
        y = b[3] if s >= 0 else b[2]
        best = max(best, (x - a[0]) * c + (y - a[1]) * s)
    return best


def plan_extents(boxes, a, psi):
    """robot-frame X/Y extents of the head (axis at head point a) rotated by psi about the turret axis."""
    xmax = T[0] + support(boxes, -psi, a)
    xmin = T[0] - support(boxes, 180 - psi, a)
    ymax = T[1] + support(boxes, 90 - psi, a)
    ymin = T[1] - support(boxes, 270 - psi, a)
    return xmin, xmax, ymin, ymax


def rmax(boxes, a):
    """farthest plan distance of the head from the turret axis (corner-exact for boxes)."""
    r = 0.0
    for b in boxes:
        for x in (b[0], b[1]):
            for y in (b[2], b[3]):
                r = max(r, math.hypot(x - a[0], y - a[1]))
    return r


def reach_toward(boxes, a, psi, P, halfw=0.0):
    """True if the head (rotated psi, axis at head point a) covers plan point P (robot frame) grown by halfw."""
    # transform P into head coords
    dx, dy = P[0] - T[0], P[1] - T[1]
    c, s = math.cos(math.radians(psi)), math.sin(math.radians(psi))
    hx = a[0] + dx * c + dy * s
    hy = a[1] - dx * s + dy * c
    for b in boxes:
        if b[0] - halfw <= hx <= b[1] + halfw and b[2] - halfw <= hy <= b[3] + halfw:
            return True
    return False


def main():
    data = {al: load(al) for al in (5, 15, 25)}
    # sanity: support from boxes vs FeatureScript h
    for al, (box, h, parts) in data.items():
        boxes = [p[2] for p in parts]
        err = max(abs(support(boxes, 5 * k) - h[k]) for k in range(72))
        print(f"alpha {al}: box {box}  max |h_boxes - h_FS| = {err:.2f} mm  parts {len(parts)}")
    # top / bottom contributors
    for al, (box, h, parts) in data.items():
        tops = sorted(parts, key=lambda p: -p[2][5])[:6]
        bots = sorted(parts, key=lambda p: p[2][4])[:4]
        print(f"\nalpha {al} top setters: " + "; ".join(f"{p[1]} {p[2][5]}" for p in tops))
        print(f"alpha {al} bottom setters: " + "; ".join(f"{p[1]} {p[2][4]}" for p in bots))
    zmin = min(d[0][4] for d in data.values())
    zmax = {al: d[0][5] for al, d in data.items()}
    print("\n==== HEIGHT (head lowest point sits on the turret plate + adapter t) ====")
    for al in (5, 15, 25):
        Hh = zmax[al] - zmin
        top0 = PLATE_TOP_Z + Hh
        print(f"alpha {al}: head height {Hh:.1f}; top Z with t=0: {top0:.1f} = {top0 - FLOOR_Z:.1f} above floor "
              f"({(top0 - FLOOR_Z) / IN:.2f} in); over start by {top0 - START_TOP_Z:.1f}; expanded margin {EXP_TOP_Z - top0:.1f}")
    print(f"room above plate for the start: {START_TOP_Z - PLATE_TOP_Z:.1f} mm (incl. adapter)")
    return data


if __name__ == "__main__":
    main()
