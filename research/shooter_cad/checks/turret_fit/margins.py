# Exact margins for the recommended mounts (back trimmed), plus the riser-to-chute handoff numbers.
import math
from fit import load, T, PLATE_TOP_Z, ROBOT_X_DEPLOYED, ROBOT_X_FOLDED, ROBOT_Y, START, EXP_L, EXP_W, START_TOP_Z, EXP_TOP_Z
from arms import arm_rects
from scan import variant, plan_ext

TRIM = (-190.0, -175.0)


def corners(b, a, psi):
    c, s = math.cos(math.radians(psi)), math.sin(math.radians(psi))
    out = []
    for hx, hy in ((b[0], b[2]), (b[1], b[2]), (b[1], b[3]), (b[0], b[3])):
        dx, dy = hx - a[0], hy - a[1]
        out.append((T[0] + dx * c - dy * s, T[1] + dx * s + dy * c))
    return out


def seg_pt(p, q, r):
    dx, dy = q[0] - p[0], q[1] - p[1]
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((r[0] - p[0]) * dx + (r[1] - p[1]) * dy) / L2))
    return math.hypot(p[0] + t * dx - r[0], p[1] + t * dy - r[1])


def sat_overlap(P, Q):
    for poly in (P, Q):
        n = len(poly)
        for i in range(n):
            ex, ey = poly[(i + 1) % n][0] - poly[i][0], poly[(i + 1) % n][1] - poly[i][1]
            ax = (-ey, ex)
            p1 = [v[0] * ax[0] + v[1] * ax[1] for v in P]
            p2 = [v[0] * ax[0] + v[1] * ax[1] for v in Q]
            if max(p1) <= min(p2) or max(p2) <= min(p1):
                return False
    return True


def poly_dist(P, Q):
    if sat_overlap(P, Q):
        return 0.0
    d = 1e9
    for A, B in ((P, Q), (Q, P)):
        for i in range(len(A)):
            for r in B:
                d = min(d, seg_pt(A[i], A[(i + 1) % len(A)], r))
    return d


def rect_poly(r):
    x0, x1, y0, y1 = r
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


_cache = {}


def head_parts(al, trim=TRIM, bottom=None):
    k = (al, trim, bottom)
    if k not in _cache:
        _cache[k] = variant(load(al)[2], trim, bottom)
    return _cache[k]


def zmin_all(trim=TRIM, bottom=None):
    return min(b[4] for al in (5, 15, 25) for (_, _, b) in head_parts(al, trim, bottom))


def arm_clear(a, psi, trim=TRIM, bottom=None, t=0.0):
    zmin = zmin_all(trim, bottom)
    best = (1e9, None)
    for al in (5, 15, 25):
        for (i, name, b) in head_parts(al, trim, bottom):
            Z0 = PLATE_TOP_Z + t + (b[4] - zmin)
            Z1 = PLATE_TOP_Z + t + (b[5] - zmin)
            for (oname, r) in arm_rects(Z0, Z1):
                d = poly_dist(corners(b, a, psi), rect_poly(r))
                if d < best[0]:
                    best = (d, f"{name[:40]} (alpha {al}) vs {oname}")
    return best


def exp_margin(a, psi, trim=TRIM, bottom=None):
    worst = (1e9, None)
    for al in (5, 15, 25):
        x0, x1, y0, y1 = plan_ext(head_parts(al, trim, bottom), a, psi)
        X = max(x1, ROBOT_X_DEPLOYED[1]) - min(x0, ROBOT_X_DEPLOYED[0])
        Y = max(y1, ROBOT_Y[1]) - min(y0, ROBOT_Y[0])
        m = min(EXP_L - X, EXP_W - Y)
        if m < worst[0]:
            worst = (m, (al, round(X, 1), round(Y, 1)))
    return worst


def start_margin(a, psi, al=15, trim=TRIM, bottom=None):
    x0, x1, y0, y1 = plan_ext(head_parts(al, trim, bottom), a, psi)
    X = max(x1, ROBOT_X_FOLDED[1]) - min(x0, ROBOT_X_FOLDED[0])
    Y = max(y1, ROBOT_Y[1]) - min(y0, ROBOT_Y[0])
    return round(min(START - X, START - Y), 1), round(X, 1), round(Y, 1), (round(x0, 1), round(x1, 1), round(y0, 1), round(y1, 1))


def main():
    for ax in (-95.0, -90.0):
        a = (ax, 0.0)
        print(f"\n######## mount a = ({ax}, 0), back trimmed (frame x >= {TRIM[0]}, feed floor x >= {TRIM[1]})")
        rows = []
        for psi in range(0, 360):
            d, who = arm_clear(a, psi)
            m, info = exp_margin(a, psi)
            rows.append((psi, d, who, m, info))
        ok = {r[0] for r in rows if r[1] > 0 and r[3] >= 0}
        lo = 180
        while (lo - 1) % 360 in ok and lo - 1 > -180:
            lo -= 1
        hi = 180
        while (hi + 1) % 360 in ok and hi + 1 < 540:
            hi += 1
        print(f"usable run around 180: psi {lo}..{hi} ({hi - lo} deg = +-{(hi - lo) / 2:.0f} about over-the-intake)")
        run = [rows[p % 360] for p in range(lo, hi + 1)]
        dmin = min(run, key=lambda r: r[1])
        mmin = min(run, key=lambda r: r[3])
        print(f"   min arm clearance inside the run: {dmin[1]:.1f} mm at psi {dmin[0]} ({dmin[2]})")
        for p in (lo, lo + 5, 90, 135, 180, 225, 270, hi - 5, hi, hi + 1, lo - 1):
            r = rows[p % 360]
            print(f"   psi {p:4d}: arm clearance {r[1]:7.1f} ({r[2]}); expanded margin {r[3]:6.1f} {r[4]}")
        print(f"   min expanded margin inside the run: {mmin[3]:.1f} at psi {mmin[0]} {mmin[4]}")
        other = sorted(p for p in ok if not any((p - q) % 360 == 0 for q in range(lo, hi + 1)))
        print("   other usable psi (outside the main run):", other)
        for p in (90, 270, 180, 0):
            print(f"   start park psi {p} (alpha 15, intake folded): margin, X span, Y span, extents = {start_margin(a, p)}")
    # ---- handoff numbers (feed floor fixed to the frame; head 2D sketch (x, z); model defaults)
    Rm, Dnom, Dmin, Dmax, delta, thk, g = 48.0, 71.12, 68.58, 73.66, 4.5, 5.0, 10.0
    Rh = Rm + Dnom - delta
    hD = lambda r: math.sqrt(r * r - g * g)
    Rrail = max(Rh + thk + 1, Rm + Dmax / 2 + hD(Dmax / 2) + 1)
    beta, phiR, Rcr, Lch, Lr = -35.0, 20.0, 50.0, 40.0, 60.0
    d2r = math.pi / 180
    pol = lambda r, th: (r * math.cos(th * d2r), r * math.sin(th * d2r))
    dB = (math.cos(beta * d2r), math.sin(beta * d2r))
    nB = (-dB[1], dB[0])
    dR = (math.cos(phiR * d2r), math.sin(phiR * d2r))
    nR = (-dR[1], dR[0])
    Tm = pol(Rrail, beta - 90)
    Pce = (Tm[0] - dB[0] * Lch, Tm[1] - dB[1] * Lch)
    Ccr = (Pce[0] - nB[0] * Rcr, Pce[1] - nB[1] * Rcr)
    Pcs = (Ccr[0] + nR[0] * Rcr, Ccr[1] + nR[1] * Rcr)
    Prs = (Pcs[0] - dR[0] * Lr, Pcs[1] - dR[1] * Lr)
    f = lambda p: f"({p[0]:.1f}, {p[1]:.1f})"
    print(f"\nfeed points (head x, z): rails meet T {f(Tm)}, chute start Pce {f(Pce)}, crest centre {f(Ccr)}, crest top ({Ccr[0]:.1f}, {Ccr[1] + Rcr:.1f}),"
          f" ramp-stub end Pcs {f(Pcs)}, ramp-stub start Prs {f(Prs)}; Rrail {Rrail:.2f}")
    zmin = zmin_all()
    print("head zmin (trimmed, all alpha):", zmin)
    for ax in (-95.0, -90.0):
        s = (ax - Pce[0]) / dB[0]
        zf = Pce[1] + dB[1] * s
        print(f"a_x {ax}: chute rail-edge line at head z {zf:.1f} = robot Z {PLATE_TOP_Z + zf - zmin:.1f} ({zf - zmin:.1f} above the plate top);"
              f" crest top {ax - Ccr[0]:.1f} mm uphill of the axis; chute meets the rails {Tm[0] - ax:.1f} mm downhill")
        for nm, D in (("D_min", Dmin), ("D_nom", Dnom), ("D_max", Dmax)):
            r = D / 2
            zc = Pce[1] + (hD(r) - (ax - Pce[0]) * nB[0]) / nB[1]
            print(f"   {nm}: ball centred on the axis column resting on the chute rails: centre head z {zc:.1f} = robot Z {PLATE_TOP_Z + zc - zmin:.1f}"
                  f" ({zc - zmin:.1f} above the plate top), ball bottom {zc - r - zmin:.1f} above the plate top")
    print(f"\nheight: start top limit Z {START_TOP_Z}, expanded top limit Z {EXP_TOP_Z}, room above plate {START_TOP_Z - PLATE_TOP_Z:.1f}")
    for al in (5, 15, 25):
        ps = head_parts(al)
        zmax = max(b[5] for (_, _, b) in ps)
        top = PLATE_TOP_Z + zmax - zmin
        print(f"   alpha {al}: head top Z {top:.1f} -> over start by {top - START_TOP_Z:.1f}; expanded margin {EXP_TOP_Z - top:.1f}")


if __name__ == "__main__":
    main()
