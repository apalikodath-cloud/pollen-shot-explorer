import math
from fit import *

data = {al: load(al) for al in (5, 15, 25)}

def h_shift(h, a, t_deg):
    # exact FS support function (5 deg samples) shifted to axis point a; linear interp in angle
    t = t_deg % 360
    k = int(t // 5); f = (t - 5 * k) / 5
    v = h[k % 72] * (1 - f) + h[(k + 1) % 72] * f
    c, s = math.cos(math.radians(t_deg)), math.sin(math.radians(t_deg))
    return v - (a[0] * c + a[1] * s)

def ext(h, a, psi):
    xmax = T[0] + h_shift(h, a, -psi)
    xmin = T[0] - h_shift(h, a, 180 - psi)
    ymax = T[1] + h_shift(h, a, 90 - psi)
    ymin = T[1] - h_shift(h, a, 270 - psi)
    return xmin, xmax, ymin, ymax

def spans(e, rx):
    X = max(e[1], rx[1]) - min(e[0], rx[0])
    Y = max(e[3], ROBOT_Y[1]) - min(e[2], ROBOT_Y[0])
    return X, Y

hs = {al: data[al][1] for al in (5, 15, 25)}
# envelope over alpha: max of support functions
henv = [max(hs[al][k] for al in hs) for k in range(72)]

def rmax_h(h, a):
    return max(h_shift(h, a, t) for t in range(0, 360, 1))

# minimax centre (smallest swing radius)
best = None
for ax in [x * 0.5 for x in range(-200, 101)]:
    for ay in [y * 0.5 for y in range(-60, 61)]:
        r = rmax_h(henv, (ax, ay))
        if best is None or r < best[0]:
            best = (r, ax, ay)
print("minimax axis point (head coords) a =", best[1:], "R =", round(best[0], 1))

mounts = {
    "F over axis (0,0)": (0.0, 0.0),
    "minimax centre": (best[1], best[2]),
    "crest over axis (-131,0)": (-131.0, 0.0),
    "ramp-stub entry over axis (-204.5,0)": (-204.5, 0.0),
}
for name, a in mounts.items():
    R = rmax_h(henv, a)
    print(f"\n== {name}: a={a}  swing radius R={R:.1f}  (slides at {math.hypot(SLIDES[0][0]-T[0], SLIDES[0][1]-T[1]):.1f} from axis)")
    # start: parking psi for which both spans fit (alpha 15 park; also any alpha)
    for park_al in (15, 5, 25):
        ok = []
        bestm = None
        for psi in range(0, 360):
            e = ext(hs[park_al], a, psi)
            X, Y = spans(e, ROBOT_X_FOLDED)
            m = min(START - X, START - Y)
            if bestm is None or m > bestm[0]:
                bestm = (m, psi, X, Y)
            if m >= 0:
                ok.append(psi)
        print(f"   start (intake folded, park alpha {park_al}): best psi {bestm[1]} margin {bestm[0]:.1f} (X {bestm[2]:.1f}, Y {bestm[3]:.1f}); OK psi count {len(ok)}"
              + (f" range {ok[0]}..{ok[-1]}" if ok else ""))
    # expanded: all psi, all alpha (envelope), deployed intake
    bad = []
    worst = None
    for psi in range(0, 360):
        e = ext(henv, a, psi)
        X, Y = spans(e, ROBOT_X_DEPLOYED)
        m = min(EXP_L - X, EXP_W - Y)
        if worst is None or m < worst[0]:
            worst = (m, psi, X, Y)
        if m < 0:
            bad.append(psi)
    print(f"   expanded (all alpha, intake out): worst psi {worst[1]} margin {worst[0]:.1f} (X {worst[2]:.1f} <= {EXP_L:.1f}, Y {worst[3]:.1f} <= {EXP_W:.1f}); bad psi count {len(bad)}")
    if bad:
        # compress ranges
        rs = []; s = bad[0]; p = bad[0]
        for v in bad[1:]:
            if v != p + 1:
                rs.append((s, p)); s = v
            p = v
        rs.append((s, p)); print("      bad psi ranges:", rs)
