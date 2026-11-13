# Turret rotation vs the robot's rear arms (two leaning slides) for Head A mount options.
# Arm geometry measured from the Front and Top views of the robot assembly (pixel scale 1.416 px/mm front,
# 1.827 px/mm top, checked against the robot's known X extent -336.8..138.4 and top Z 435.4): +-3 mm.
import math
from fit import load, T, PLATE_TOP_Z

ARM_Y = (80.0, 99.0)          # |Y| band of each arm
ARM_TILT = 0.1587             # dX/dZ (leans 9.0 deg toward +X going up)
ARM_X0, ARM_Z0 = 37.1, 241.9  # inner (-X) edge point
ARM_W = 18.0                  # X width of the arm
ARM_TOP = 434.1
BRACKET = (409.0, 106.0)      # above Z 409 the top bracket reaches X 106
SIDE_PEAK = dict(x=(23.3, 50.0), y=(100.0, 104.0), z=(PLATE_TOP_Z, 241.9))  # robot side plates poke 3.7 mm above the turret plate

def arm_rects(z0, z1):
    """plan rectangles (xmin,xmax,ymin,ymax) of obstacles that overlap robot Z band [z0,z1]."""
    out = []
    lo, hi = max(z0, -1e9), min(z1, ARM_TOP)
    if hi > lo:
        xl = ARM_X0 + ARM_TILT * (lo - ARM_Z0)
        xr = ARM_X0 + ARM_TILT * (hi - ARM_Z0) + ARM_W
        if hi >= BRACKET[0]:
            xr = max(xr, BRACKET[1])
        for s in (1, -1):
            ys = sorted((s * ARM_Y[0], s * ARM_Y[1]))
            out.append(("arm" + ("+Y" if s > 0 else "-Y"), (xl, xr, ys[0], ys[1])))
    if min(z1, SIDE_PEAK["z"][1]) > max(z0, SIDE_PEAK["z"][0]):
        for s in (1, -1):
            ys = sorted((s * SIDE_PEAK["y"][0], s * SIDE_PEAK["y"][1]))
            out.append(("sideplate" + ("+Y" if s > 0 else "-Y"), (SIDE_PEAK["x"][0], SIDE_PEAK["x"][1], ys[0], ys[1])))
    return out

def overlap(part, a, psi, rect):
    """SAT: head part box (head x0,x1,y0,y1) placed with head point a on the turret axis, rotated psi, vs robot rect."""
    x0, x1, y0, y1 = part
    c, s = math.cos(math.radians(psi)), math.sin(math.radians(psi))
    corners = []
    for hx in (x0, x1):
        for hy in (y0, y1):
            dx, dy = hx - a[0], hy - a[1]
            corners.append((T[0] + dx * c - dy * s, T[1] + dx * s + dy * c))
    rx0, rx1, ry0, ry1 = rect
    rc = [(rx0, ry0), (rx0, ry1), (rx1, ry0), (rx1, ry1)]
    for ax in ((1, 0), (0, 1), (c, s), (-s, c)):
        p1 = [p[0] * ax[0] + p[1] * ax[1] for p in corners]
        p2 = [p[0] * ax[0] + p[1] * ax[1] for p in rc]
        if max(p1) <= min(p2) or max(p2) <= min(p1):
            return False
    return True

def ranges(vals):
    if not vals:
        return []
    rs = []; s = vals[0]; p = vals[0]
    for v in vals[1:]:
        if v != p + 1:
            rs.append((s, p)); s = v
        p = v
    rs.append((s, p))
    if len(rs) > 1 and rs[0][0] == 0 and rs[-1][1] == 359:  # wrap
        rs = [(rs[-1][0] - 360, rs[0][1])] + rs[1:-1]
    return rs

def clear_ranges(hit):
    free = [p for p in range(360) if not hit[p]]
    return ranges(free)

def analyse(a, alphas=(5, 15, 25), t=0.0, zmin_head=-142.0, verbose=True, label=""):
    hit = {p: set() for p in range(360)}
    for al in alphas:
        box, h, parts = load(al)
        for (i, name, b) in parts:
            Z0 = PLATE_TOP_Z + t + (b[4] - zmin_head)
            Z1 = PLATE_TOP_Z + t + (b[5] - zmin_head)
            rects = arm_rects(Z0, Z1)
            if not rects:
                continue
            for psi in range(360):
                for (oname, r) in rects:
                    if overlap(b[:4], a, psi, r):
                        hit[psi].add((oname, name[:24]))
    if verbose:
        free = clear_ranges({p: bool(hit[p]) for p in hit})
        print(f"\n== {label} a={a}: clear psi ranges (deg, 0 = head shoots toward robot +X / the arms, 180 = over the intake): {free}")
        # which parts hit most often
        cnt = {}
        for p in hit:
            for (o, n) in hit[p]:
                cnt[(o.rstrip('+-Y'), n)] = cnt.get((o.rstrip('+-Y'), n), 0) + 1
        top = sorted(cnt.items(), key=lambda kv: -kv[1])[:10]
        print("   most frequent hits:", "; ".join(f"{k[1]} vs {k[0]} ({v} deg)" for k, v in top))
    return hit

if __name__ == "__main__":
    # original shooter, for comparison: footprint about X -194..43, Y -49..47 (Top view), Z 238..356
    orig = [(-194.0 - T[0], 43.0 - T[0], -49.0, 47.0)]
    hit = {}
    for phi in range(360):
        hs = set()
        for r in arm_rects(PLATE_TOP_Z, 356.0):
            for b in orig:
                if overlap(b, (0.0, 0.0), phi, r[1]):
                    hs.add(r[0])
        hit[phi] = bool(hs)
    print("original shooter (phi = rotation from its modelled pose): clear", clear_ranges(hit))
    for label, a in [("centred (minimax)", (-23.0, 0.0)), ("F over axis", (0.0, 0.0)), ("crest over axis", (-131.0, 0.0)), ("a=-90", (-90.0, 0.0))]:
        analyse(a, label=label)
