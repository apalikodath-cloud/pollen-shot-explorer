"""Side-view diagram of the ramp feed into the tilting Head A, plus the handoff numbers for ramp_feed.md.

Geometry mirrors pollen_head_A.fs defaults (brief frame: F = main wheel axle = head pivot at the origin,
x downrange, y up, alpha = exit angle from vertical, counter-roller centre at angle -alpha).
Usage: python feed_diagram.py <out_png>
"""
import sys
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, FancyArrowPatch

d2r = np.pi / 180


def pol(r, th):
    th = np.asarray(th, dtype=float) * d2r
    r = np.asarray(r, dtype=float)
    return np.stack([r * np.cos(th), r * np.sin(th)], axis=-1)


# ---- model defaults (brief values + pollen_head_A.fs feed defaults)
Rm, Rc = 48.0, 25.4
Dnom, Dmin, Dmax = 71.12, 68.58, 73.66
delta = 4.5
Rh = Rm + Dnom - delta            # hood inner radius 114.62
thk = 5.0                         # hood thickness
hood_arc = 60.0
C = Rm + Rc + Dnom - delta        # 140.02
dEnd = 15.249                     # hood end before the nip line (model value)
thEndL = -dEnd
thStartL = thEndL - hood_arc
lead = 20.0                       # tongue lead arc
thEL = thStartL - lead
beta, phiR = -35.0, 20.0          # chute angle, robot ramp angle
g = 10.0                          # slot half-width (ball rides on two rail edges)
Rcr, Lch, Lr = 50.0, 40.0, 60.0   # crest radius, chute length, ramp stub length
hD = lambda r: np.sqrt(r * r - g * g)
sag = lambda r: r - hD(r)
Rrail = max(Rh + thk + 1, Rm + Dmax / 2 + hD(Dmax / 2) + 1)
sagMax = max(sag(Dmin / 2), sag(Dmax / 2))
Rte = Rrail + sagMax + 0.5
span = Rte - Rh
thT = beta - 90
thFe = -92.77                     # rail end in the model (3 deg past the latest lift)

dB = np.array([np.cos(beta * d2r), np.sin(beta * d2r)])
nB = np.array([-dB[1], dB[0]])
dR = np.array([np.cos(phiR * d2r), np.sin(phiR * d2r)])
nR = np.array([-dR[1], dR[0]])
T = pol(Rrail, thT)
Pce = T - dB * Lch
Ccr = Pce - nB * Rcr
Pcs = Ccr + nR * Rcr
Prs = Pcs - dR * Lr


def smooth(t):
    return 3 * t * t - 2 * t ** 3


def sInv(s):
    return 0.5 - np.sin(np.arcsin(1 - 2 * s) / 3)


def r_t(t):
    return Rte - span * smooth(np.clip(t, 0, 1))


def handoff(D, alpha):
    """Global angles (deg) where the tongue lifts the ball 0.5 mm off the rails and where the wheel grips it."""
    r = D / 2
    t_lift = sInv(min(1.0, (Rte - (Rrail + sag(r) - 0.5)) / span))
    t_grip = sInv(min(1.0, (Rte - (Rm + D)) / span))
    return thEL - alpha + lead * t_lift, thEL - alpha + lead * t_grip


def centre_path(D, alpha, n=200):
    """Ball-centre path: ramp, crest, chute, rails, tongue, hood, nip (list of segments)."""
    r = D / 2
    h = hD(r)
    segs = {}
    s = np.linspace(0, 1, n)[:, None]
    segs["ramp"] = Prs + dR * Lr * s + nR * h
    a = np.linspace(phiR + 90, beta + 90, n)
    segs["crest"] = Ccr + pol(Rcr + h, a)
    segs["chute"] = Pce + dB * Lch * s + nB * h
    thL, thG = handoff(D, alpha)
    th0 = thEL - alpha                         # tongue entry, global
    # rails until the tongue meets the ball bottom
    t_meet = sInv(min(1.0, (Rte - (Rrail + sag(r))) / span))
    th_meet = th0 + lead * t_meet
    segs["rails"] = pol(Rrail - h, np.linspace(thT, th_meet, n))
    tt = np.linspace(t_meet, 1, n)
    rt = r_t(tt)
    rho = np.where(rt - r > Rm + r, rt - r, (Rm + rt) / 2)
    segs["tongue"] = pol(rho, th0 + lead * tt)
    rHood = (Rm + Rh) / 2
    segs["hood"] = pol(rHood, np.linspace(thStartL - alpha, -alpha, n))
    return segs, thL, thG


def band(ax, r0, r1, a0, a1, **kw):
    a = np.linspace(a0, a1, 120)
    pts = np.vstack([pol(r0, a), pol(r1, a[::-1])])
    ax.add_patch(Polygon(pts, closed=True, **kw))


TEAL, ORANGE, BLUE, BALL, WHEEL = "#2f9e9e", "#e8861a", "#3466c9", "#f2c300", "#222222"


def panel(ax, alpha):
    D = Dnom
    r = D / 2
    segs, thL, thG = centre_path(D, alpha)
    # fixed: floor running surface (ramp, crest, chute, rails)
    fl = np.vstack([Prs + dR * Lr * np.linspace(0, 1, 50)[:, None],
                    Ccr + pol(Rcr, np.linspace(phiR + 90, beta + 90, 80)),
                    Pce + dB * Lch * np.linspace(0, 1, 30)[:, None],
                    pol(Rrail, np.linspace(thT, thFe, 60))])
    ax.plot(fl[:, 0], fl[:, 1], color=TEAL, lw=5, solid_capstyle="butt", zorder=3)
    # moving with the head: tongue (lead-in) and hood
    tt = np.linspace(0, 1, 80)
    tg = pol(r_t(tt), thEL - alpha + lead * tt)
    ax.plot(tg[:, 0], tg[:, 1], color=ORANGE, lw=3, zorder=4)
    band(ax, Rh, Rh + thk, thStartL - alpha, thEndL - alpha, facecolor=ORANGE, edgecolor="none", zorder=4)
    # wheels
    ax.add_patch(Circle((0, 0), Rm, facecolor=WHEEL, edgecolor="none", zorder=2))
    ax.add_patch(Circle((0, 0), 4, facecolor="white", zorder=6))
    cc = pol(C, -alpha)
    ax.add_patch(Circle(tuple(cc), Rc, facecolor="#777777", edgecolor=BLUE, lw=2.5, zorder=2))
    # ball-centre path
    for k, p in segs.items():
        ax.plot(p[:, 0], p[:, 1], ls=(0, (4, 3)), color="#7a6200", lw=1.2, zorder=5)
    # exit line
    t = np.array([np.sin(alpha * d2r), np.cos(alpha * d2r)])
    pn = pol((Rm + Rh) / 2, -alpha)
    ax.add_patch(FancyArrowPatch(tuple(pn), tuple(pn + t * 120), arrowstyle="-|>", mutation_scale=18,
                                 color="#2a8a3a", lw=2, zorder=6))
    # balls: on the ramp, on the rails just before the lift, gripped at the hood, at the nip
    p_ramp = Prs + dR * Lr * 0.35 + nR * hD(r)
    p_lift = pol(Rrail - hD(r), thL - 4)
    p_grip = pol(Rm + r, thG)
    for p, a in ((p_ramp, 0.9), (p_lift, 0.75), (pn, 0.9)):
        ax.add_patch(Circle(tuple(p), r, facecolor=BALL, edgecolor="#8a6d00", lw=1, alpha=a, zorder=1))
    ax.plot(*pol(Rrail - hD(r), thL), "o", color="black", ms=5, zorder=7)
    ax.plot(*p_grip, "s", color="red", ms=6, zorder=7)
    # labels
    kw = dict(fontsize=8.5, zorder=8)
    ax.annotate("robot ramp\n(assumed 20° up)", xy=tuple(Prs + dR * 15), xytext=(-262, -150), ha="center",
                arrowprops=dict(arrowstyle="-", color="0.4"), **kw)
    ax.annotate("crest R50:\nhighest point", xy=(Ccr[0], Ccr[1] + Rcr), xytext=(-195, 25), ha="center",
                arrowprops=dict(arrowstyle="-", color="0.4"), **kw)
    ax.annotate("chute 35° down", xy=tuple(Pce + dB * 20), xytext=(-150, -178), ha="center",
                arrowprops=dict(arrowstyle="-", color="0.4"), **kw)
    ax.annotate("fixed rails under the wheel\n(the tongue passes through the slot)", xy=tuple(pol(Rrail, -105)),
                xytext=(10, -185), ha="center", arrowprops=dict(arrowstyle="-", color="0.4"), **kw)
    ax.annotate("tongue on the head\nlifts ball off rails (●)", xy=tuple(pol(r_t(0.3), thEL - alpha + 6)),
                xytext=(160, -168), ha="center", arrowprops=dict(arrowstyle="-", color="0.4"), **kw)
    ax.annotate("wheel grips (■)", xy=tuple(p_grip), xytext=(190, -128), ha="center",
                arrowprops=dict(arrowstyle="-", color="red"), **kw)
    ax.annotate("hood (tilts)", xy=tuple(pol(Rh + thk, thStartL - alpha + 40)), xytext=(215, -75), ha="center",
                arrowprops=dict(arrowstyle="-", color="0.4"), **kw)
    ax.annotate("counter-roller\n(tilts)", xy=tuple(cc + pol(Rc, 20)), xytext=(215, 20), ha="center",
                arrowprops=dict(arrowstyle="-", color="0.4"), **kw)
    ax.text(pn[0] + t[0] * 125 + 6, pn[1] + t[1] * 125, f"exit, α = {alpha:g}°\nfrom vertical", fontsize=8.5,
            va="center", color="#2a8a3a")
    ax.text(0, 58, "F: wheel axle\n= head pivot", ha="center", va="bottom", fontsize=8)
    ax.set_title(f"α = {alpha:g}°", fontsize=12)
    ax.set_xlim(-300, 250)
    ax.set_ylim(-200, 175)
    ax.set_aspect("equal")
    ax.axis("off")


def numbers():
    rows = []
    for D in (Dmin, Dnom, Dmax):
        r = D / 2
        y_crest = Ccr[1] + Rcr + hD(r)          # ball centre at the crest top
        for alpha in (5, 15, 25):
            segs, thL, thG = centre_path(D, alpha, n=2000)
            y_grip = (Rm + r) * np.sin(thG * d2r)
            pre = np.vstack([segs["rails"], segs["tongue"]])
            pre_ang = np.degrees(np.arctan2(pre[:, 1], pre[:, 0]))
            before = pre[pre_ang <= thG + 1e-9]
            y_low = before[:, 1].min()
            drop = y_crest - y_grip
            v_solid = np.sqrt(2 * 9.81 * drop / 1000 / 1.4)
            v_shell = np.sqrt(2 * 9.81 * drop / 1000 / (1 + 2 / 3))
            rows.append((D, alpha, thL, thG, y_grip - y_low, drop, v_shell, v_solid))
    return rows


if __name__ == "__main__":
    out = sys.argv[1]
    fig, axs = plt.subplots(1, 2, figsize=(14, 5.6))
    for ax, a in zip(axs, (5, 25)):
        panel(ax, a)
    fig.suptitle("Ramp feed into the tilting head (side view, ball D 71.12 mm). Teal = fixed to the robot. "
                 "Orange/blue = tilts with the head about F.", fontsize=11)
    fig.text(0.5, 0.015, "Dashed line = ball-centre path. The tongue always meets the ball at the same place on "
             "the head, so the wheel grips it at the same point on the head at every α. Placeholder geometry; "
             "the real ramp angle and height are TBD.", ha="center", fontsize=8.5, color="0.3")
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    fig.savefig(out, dpi=130)
    print("Rrail", round(Rrail, 3), "Rte", round(Rte, 3), "crest top floor y", round(Ccr[1] + Rcr, 2))
    print("D alpha liftDeg gripDeg climbToGrip_mm dropCrestToGrip_mm v_shell v_solid")
    for row in numbers():
        print(" ".join(f"{x:.2f}" for x in row))
