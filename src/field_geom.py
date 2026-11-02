"""Shared field geometry for the release-point tests (PM-015, research/GEOMETRY_AUDIT.md fixes 2, 5, 8).

One implementation of three things that used to be coded three different ways:

* ``chassis_ok``  - does the turned robot chassis fit: inside the field walls and not over the
  A-frame base rectangle? (audit fix 2)
* ``sight_blocked`` - does the straight line from the release point to the aim point cross the
  other HIVE's plan box? Exact segment-rectangle test (Liang-Barsky), no sampling. (audit fix 5)
* ``field_grid`` - the release grid: symmetric about x = 0 and with a row on the aim line y = 0.
  (audit fix 8)

The JavaScript twin is ``footprint`` / ``sightBlocked`` / the constants in viz/explorer/solver.js;
tests/test_field_geom.py runs both on the same points.

Frame (field frame, pose_pos, as in viz/explorer/FIELD_DATA.md): x = shot axis, HIVE pivot plane
at x = 0; y along the pivot axis, red HIVE centre at y = 0, field centre at y = +0.3236, the other
(blue) HIVE centre at y = +0.6472. All lengths in metres.
"""
from __future__ import annotations

import math

import numpy as np

IN = 0.0254
#: derived from the official field CAD (data/hive_geometry.json): inner wall |x| = 1.8009 m
X_WALL = 1.8009
#: CAD: red HIVE centre 0.3236 m from the field centre (HIVE c-c 0.6472 m; the audit keeps the CAD
#: value, research/GEOMETRY_AUDIT.md section 3 and U2)
HIVE_HALF_SPACING = 0.3236
Y_LO, Y_HI = -X_WALL + HIVE_HALF_SPACING, X_WALL + HIVE_HALF_SPACING
#: CONFIRMED (TU07 9.6.1): A-frame base 38.95 in (x) x 49.46 in (y), centred on the field centre
BASE_HALF_X = 38.95 / 2 * IN            # 0.494665
BASE_HALF_Y = 49.46 / 2 * IN            # 0.628142
BASE_CY = HIVE_HALF_SPACING
#: derived (audit fix 5): other HIVE plan box = CAD plan envelope |x| <= 0.639 at tilt 30 and CAD
#: body y 0.381-0.914, each grown by the ball radius 0.0355. ASSUMED as the blocking footprint
#: (a far-side ball can pass above it; not modelled).
OTHER_HIVE_X = 0.6745
OTHER_HIVE_Y = (0.3455, 0.9495)
#: derived: up-cell gate centre at tilt 30 (src/robustness.py X_GATE)
X_GATE = 0.401
#: CONFIRMED (R102): 18 x 18 in starting size; R105 lets a robot expand to 18 x 24 in
ROBOT_L = ROBOT_W = 18 * IN             # 0.4572
ROBOT_L_EXPANDED = 24 * IN              # 0.6096 (option)
#: ASSUMED: grid release points stay 0.10 m inside the wall; grid step 0.05 m
WALL_MARGIN = 0.10
FIELD_STEP = 0.05
#: ASSUMED: heading scan for "best heading" (any heading that fits counts)
HEADING_STEP = 5.0


def _rect_extent(hl, hw, c, s):
    """half-extents along field x and y of a rectangle (half-length hl along heading, hw across)."""
    ac, as_ = np.abs(c), np.abs(s)
    return hl * ac + hw * as_, hl * as_ + hw * ac


def chassis_fits(x, y, heading_deg, length=ROBOT_L, width=ROBOT_W, offset=(0.0, 0.0)):
    """Vectorised: True where the chassis (length along the heading, width across), whose
    release point is (x, y), lies inside the field walls and does not overlap the A-frame base.

    offset = (forward, left) of the release point from the chassis centre, in the chassis frame
    (ASSUMED default 0). Touching counts as fitting. Separating-axis test against the base."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    t = np.radians(np.asarray(heading_deg, float))
    c, s = np.cos(t), np.sin(t)
    fo, lo = float(offset[0]), float(offset[1])
    cx = x - (c * fo - s * lo)
    cy = y - (s * fo + c * lo)
    hl, hw = 0.5 * float(length), 0.5 * float(width)
    ex, ey = _rect_extent(hl, hw, c, s)
    eps = 1e-9
    walls = (np.abs(cx) + ex <= X_WALL + eps) & (cy - ey >= Y_LO - eps) & (cy + ey <= Y_HI + eps)
    dx, dy = cx, cy - BASE_CY
    a1 = np.abs(dx) < BASE_HALF_X + ex - eps
    a2 = np.abs(dy) < BASE_HALF_Y + ey - eps
    bu, bv = _rect_extent(BASE_HALF_X, BASE_HALF_Y, c, s)   # base extent on the chassis axes
    a3 = np.abs(dx * c + dy * s) < hl + bu - eps
    a4 = np.abs(-dx * s + dy * c) < hw + bv - eps
    overlap = a1 & a2 & a3 & a4
    # the release point itself must be inside the walls and off the base (a long offset)
    rp = (np.abs(x) <= X_WALL + eps) & (y >= Y_LO - eps) & (y <= Y_HI + eps) & \
        ~((np.abs(x) < BASE_HALF_X - eps) & (np.abs(y - BASE_CY) < BASE_HALF_Y - eps))
    return walls & ~overlap & rp


def chassis_ok(x, y, heading_deg=None, length=ROBOT_L, width=ROBOT_W, offset=(0.0, 0.0),
               step=HEADING_STEP):
    """chassis_fits at one heading, or (heading_deg None) at ANY heading of a scan with `step`
    degrees (0 .. 360, or 0 .. 180 / 0 .. 90 when the shape allows): returns a bool array."""
    if heading_deg is not None:
        return chassis_fits(x, y, heading_deg, length, width, offset)
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    sym = 360.0 if (offset[0] or offset[1]) else (90.0 if abs(length - width) < 1e-12 else 180.0)
    ok = np.zeros(np.broadcast(x, y).shape, bool)
    for h in np.arange(0.0, sym - 1e-9, step):
        ok |= chassis_fits(x, y, h, length, width, offset)
    return ok


def sight_blocked(x, y, aim_x=X_GATE, aim_y=0.0):
    """Vectorised exact test: the segment (x, y) -> (aim_x, aim_y) passes through the open
    other-HIVE box |x| < OTHER_HIVE_X, OTHER_HIVE_Y[0] < y < OTHER_HIVE_Y[1] (Liang-Barsky)."""
    x0 = np.asarray(x, float)
    y0 = np.asarray(y, float)
    x0, y0 = np.broadcast_arrays(x0, y0)
    dx = aim_x - x0
    dy = aim_y - y0
    t0 = np.zeros(x0.shape)
    t1 = np.ones(x0.shape)
    ok = np.ones(x0.shape, bool)
    for p, q in ((-dx, x0 + OTHER_HIVE_X), (dx, OTHER_HIVE_X - x0),
                 (-dy, y0 - OTHER_HIVE_Y[0]), (dy, OTHER_HIVE_Y[1] - y0)):
        par = np.abs(p) < 1e-15
        ok &= ~(par & (q <= 0.0))                      # parallel and outside (or on the edge)
        with np.errstate(divide="ignore", invalid="ignore"):
            r = np.where(par, 0.0, q / np.where(par, 1.0, p))
        ent = ~par & (p < 0)
        ext = ~par & (p > 0)
        t0 = np.where(ent, np.maximum(t0, r), t0)
        t1 = np.where(ext, np.minimum(t1, r), t1)
    return ok & (t1 - t0 > 1e-12)


def field_grid(step=FIELD_STEP, margin=WALL_MARGIN):
    """Release grid: x = k step for |x| <= X_WALL - margin, y = k step inside [Y_LO, Y_HI] minus
    margin (so x = 0 and y = 0 are grid lines). Returns xs, ys, X, Y (meshgrid, indexing xy)."""
    kx = int(math.floor((X_WALL - margin) / step + 1e-9))
    ky0 = int(math.ceil((Y_LO + margin) / step - 1e-9))
    ky1 = int(math.floor((Y_HI - margin) / step + 1e-9))
    xs = np.round(np.arange(-kx, kx + 1) * step, 4)
    ys = np.round(np.arange(ky0, ky1 + 1) * step, 4)
    X, Y = np.meshgrid(xs, ys, indexing="xy")
    return xs, ys, X, Y
