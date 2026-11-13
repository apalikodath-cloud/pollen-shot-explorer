import math
from fit import load, T, ROBOT_X_DEPLOYED, ROBOT_X_FOLDED, ROBOT_Y, START, EXP_L, EXP_W, PLATE_TOP_Z
from arms import arm_rects, overlap, ranges

STEP = 2
PSIS = list(range(0, 360, STEP))

def variant(parts, trim_back=None, bottom=None):
    out = []
    for (i, name, b) in parts:
        b = list(b)
        if trim_back is not None and i in (21, 24, 42):   # frame plates + feed floor: ramp stub / extension removed
            b[0] = max(b[0], trim_back[0] if i in (21, 24) else trim_back[1])
        if bottom is not None:
            b[4] = max(b[4], bottom)
        out.append((i, name, b))
    return out

def plan_ext(parts, a, psi):
    c, s = math.cos(math.radians(psi)), math.sin(math.radians(psi))
    xs, ys = [], []
    for (_, _, b) in parts:
        for hx in (b[0], b[1]):
            for hy in (b[2], b[3]):
                dx, dy = hx - a[0], hy - a[1]
                xs.append(T[0] + dx * c - dy * s); ys.append(T[1] + dx * s + dy * c)
    return min(xs), max(xs), min(ys), max(ys)

def evaluate(a, trim_back=None, bottom=None, park_alpha=15):
    data = {al: variant(load(al)[2], trim_back, bottom) for al in (5, 15, 25)}
    zmin = min(b[4] for al in data for (_, _, b) in data[al])
    armhit = {p: False for p in PSIS}
    exp_bad = {p: False for p in PSIS}
    start_ok = {p: False for p in PSIS}
    for al, parts in data.items():
        for (i, name, b) in parts:
            Z0 = PLATE_TOP_Z + (b[4] - zmin); Z1 = PLATE_TOP_Z + (b[5] - zmin)
            rects = arm_rects(Z0, Z1)
            for p in PSIS:
                if armhit[p]:
                    continue
                for (_, r) in rects:
                    if overlap(b[:4], a, p, r):
                        armhit[p] = True; break
        for p in PSIS:
            x0, x1, y0, y1 = plan_ext(parts, a, p)
            X = max(x1, ROBOT_X_DEPLOYED[1]) - min(x0, ROBOT_X_DEPLOYED[0]); Y = max(y1, ROBOT_Y[1]) - min(y0, ROBOT_Y[0])
            if X > EXP_L or Y > EXP_W:
                exp_bad[p] = True
            if al == park_alpha:
                Xs = max(x1, ROBOT_X_FOLDED[1]) - min(x0, ROBOT_X_FOLDED[0])
                start_ok[p] = Xs <= START and Y <= START
    usable = [p for p in PSIS if not armhit[p] and not exp_bad[p]]
    park = [p for p in PSIS if not armhit[p] and start_ok[p]]
    return armhit, exp_bad, usable, park, zmin

def runs(ps):
    if not ps:
        return []
    rs = []; s = ps[0]; prev = ps[0]
    for v in ps[1:]:
        if v != prev + STEP:
            rs.append((s, prev)); s = v
        prev = v
    rs.append((s, prev))
    if len(rs) > 1 and rs[0][0] == 0 and rs[-1][1] == 360 - STEP:
        rs = [(rs[-1][0] - 360, rs[0][1])] + rs[1:-1]
    return rs

def widest(rs):
    return max((r[1] - r[0] + STEP for r in rs), default=0)

if __name__ == "__main__":
    import sys
    for label, tb in [("full head", None), ("back trimmed (ramp stub + frame extension off; frame x>=-190, floor x>=-175)", (-190.0, -175.0))]:
        print(f"\n##### {label}")
        best = None
        for ax in range(-160, 1, 5):
            armhit, exp_bad, usable, park, zmin = evaluate((float(ax), 0.0), tb)
            rs = runs(usable)
            w = widest(rs)
            print(f"a_x {ax:5d}: usable widest {w:3d} deg  ranges {rs}  start-park options {len(park)}")
            if best is None or w > best[0]:
                best = (w, ax, rs)
        print("best:", best)
