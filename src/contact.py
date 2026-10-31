"""Spin-assisted contact entry (hypothesis B): rigid-ball impact with the HIVE section.

HANDOFF section 0 hypothesis (B), section 3 Q5, section 4E channel 2; contract: docs/INTERFACES.md
("src/contact.py"). Uses src/hive.py (geometry) and src/flight.py (aero parameters) READ-ONLY.

Every output of this module is PREDICTED. Restitution e, friction mu and tangential restitution e_t
for POLLEN on the HIVE are ASSUMED (no measurement exists); aerodynamics are the ASSUMED bounds of
the aero file given by --aero-path (default research/params_lit.json; data/aero_params.json was the
first-pass set); geometry is the CAD-derived 2D centre-plane section (docs/01_hive_geometry.md).

Frame and sign convention (2D, tipping plane)
---------------------------------------------
Shot frame of flight.py / hive.py: x horizontal toward the target, z up, spin w = omega_y.
The ball is fired toward +x; BACKSPIN on a +x-moving ball is w < 0 (omega along -y, so
omega x v points +z; flight.backspin_omega). Unfavourable side = Hive pose_pos seen from the
'neg' side (no mirroring needed: shot frame == HIVE frame).

Impact model (derived; Walton / Brach rigid-body impulse model, as in Cross 2005 / Allen 2010)
------------------------------------------------------------------------------------------------
Contact normal n = unit(ball centre - closest point on the obstacle segment), so flat faces and
edges/corners (segment end points) are handled the same way. Contact tangent t = y_hat x n =
(n_z, -n_x). Contact-point position r = -R n, and omega x r = -R w t, so the contact-point
velocity is
    v_cn = v.n            (< 0 = approaching)
    v_ct = v.t - R w      (slip velocity)
Impulse P = P_n n + P_t t applied at the contact point:
    m dv = P,    I dw = (r x P)_y = -R P_t       (n x t = y_hat)
    P_n  = -(1 + e) m v_cn
    stick (grip) impulse   P_t* = -(1 + e_t) m_t v_ct,   m_t = m alpha/(1 + alpha),  alpha = I/(m R^2)
    if |P_t*| <= mu P_n : P_t = P_t*   ("stick": slip ends at rolling for e_t = 0, reverses for e_t > 0)
    else                : P_t = -mu P_n sign(v_ct)   ("slip": Coulomb sliding throughout)
Energy change dE = P_n (v_cn + v_cn')/2 + P_t (v_ct + v_ct')/2 <= 0 for 0 <= e <= 1, 0 <= e_t <= 1
(the normal and tangential problems decouple for a sphere). mu = 0 -> P_t = 0 -> spin unchanged.

Spin-induced tangential kick (derived)
--------------------------------------
Spin enters only through v_ct = v.t - R w. Backspin on a +x ball (w < 0) adds +R|w| along t, so
relative to the same impact without spin the friction impulse changes by a NON-POSITIVE amount
along t: the extra velocity kick is along  k = -t = (-n_z, n_x)  (n rotated +90 deg), magnitude
between 0 (both cases sliding the same way: identical outcome) and m_t R |w| / m.
  * far rim (lower lip) caught by the ball's lower-front surface on the way in: n ~ (-sin c, cos c)
    -> k = (-cos c, -sin c): back toward the shooter and DOWN = INTO the CELL ("check" effect);
  * near rim (roof end / upper-lip corner) struck from above/behind (shot slightly short):
    n ~ (-sin a, cos a) -> same k = (-x, down), i.e. backward around the corner (k.t_fwd < 0 with
    t_fwd = (cos a, sin a) the "over the edge" direction): the ball is held back over the ROOF,
    AWAY from the mouth, which lies on the far (+x) side of that corner.
Unit-tested in tests/test_contact.py on the real lip corners; the sweep also records the measured
inward velocity change at every first contact.

Flight between contacts
-----------------------
Vectorised fixed-step RK4 (dt 1 ms default) with the flight.py force model: drag
-0.5 rho Cd A |v| v, Magnus 0.5 rho Cl(S) A |v|^2 unit(omega x v), Cl = min(c1 S, Cl_max), S
regularised as in flight.py, spin decay dw/dt = -k w. Cross-checked against flight.simulate.
Contact detection: penetration (distance < R) at the end of a step -> bisection of the contact
fraction along the step chord -> impulse -> the rest of the step is re-integrated. Resting / rolling
contact emerges from repeated micro-impulses (approach speed < V_REST uses e = 0), which reproduces the
rolling-down-an-incline acceleration g sin(theta)/(1 + alpha) (unit test).

Outcome (per ball)
------------------
  retained_clean    entered the CELL with no prior contact and ended TRAPPED;
  retained_contact  >= 1 contact before entering the CELL and ended TRAPPED;
  bounced_out       entered the CELL but left again (not trapped);
  blocked           touched the HIVE, never entered;
  miss              never touched the HIVE, never entered;
  timeout           still unresolved at t_max (counted as not retained).
TRAPPED (derived, conservative): ball centre in the CELL (behind the mouth plane, inside the walls)
AND total mechanical energy  z + |v|^2/(2g) + I w^2/(2 m g) < z_barrier, where z_barrier is the lowest
ball-centre height at which the centre can cross the mouth plane (the gate's low end, ball resting on
the lower lip). Drag only removes energy and the impacts are dissipative, so a trapped ball can
never leave. ASSUMED: rigid fixed HIVE (it rests on its damper stop), 2D centre plane, no preloaded
NECTAR in the section, no hole-catching on the perforated shell.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import time
from dataclasses import dataclass, field
from typing import Any, Optional, Sequence

import numpy as np

from src import flight as fl
from src import hive as hv

__all__ = ["ContactParams", "ContactGeometry", "impact", "impact_batch", "spin_kick_direction",
           "simulate_batch", "simulate_one", "free_flight", "aero_case", "OUTCOMES",
           "incidence_states", "launch_states", "ball_props"]

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = fl.G_STANDARD
OUTCOMES = ("retained_clean", "retained_contact", "bounced_out", "blocked", "miss", "timeout")
O_RC, O_RK, O_BO, O_BL, O_MI, O_TO = range(6)
#: assumed: approach speeds below this are treated as resting contact (e = 0), m/s.
V_REST = 0.05
#: assumed: contacts with approach speed above this count as a "bounce" in the statistics, m/s.
V_BOUNCE = 0.10
ZONES = ("near_rim", "far_rim", "interior", "external")


# --------------------------------------------------------------------------- parameters
@dataclass
class ContactParams:
    """Impact parameters. All ASSUMED (no POLLEN-on-HIVE measurement exists)."""
    e: float = 0.5        # normal coefficient of restitution
    mu: float = 0.4       # Coulomb friction coefficient
    e_t: float = 0.0      # tangential restitution in the grip regime (0 = ends at rolling)


def ball_props(which: str = "value") -> dict:
    """Nominal mass and radius with I_b = alpha m R^2, alpha = I_b.alpha_I_over_mR2[which]
    from the active aero file (flight.AERO_PARAMS_PATH; 'value' 0.63 | 'low' 0.60 | 'high' 0.667). The inertia bound is
    applied through alpha (the quantity that enters the impact law), mass/radius held nominal."""
    with open(fl.AERO_PARAMS_PATH, encoding="utf-8") as fh:
        raw = json.load(fh)
    m = float(raw["mass"]["value"])
    R = float(raw["radius"]["value"])
    a = float(raw["I_b"]["alpha_I_over_mR2"][which])
    return {"mass": m, "radius": R, "I_b": a * m * R * R, "alpha": a,
            "prov": f"mass/radius from {fl.aero_tag()}.json (AndyMark spec); alpha derived ({which})"}


def aero_case(Cl: Any = "nominal", Cd: Any = "nominal", k: Any = "nominal") -> dict:
    """Flat aero dict for the RK4 core. Cl: 'low'|'nominal'|'high'|None(=no Magnus)|(c1, Cl_max)."""
    which = {"Cd": Cd if isinstance(Cd, str) else "nominal",
             "Cl": Cl if isinstance(Cl, str) else "nominal",
             "spin_decay_k": k if isinstance(k, str) else "nominal"}
    p = fl.load_params(which=which)
    out = {"rho": p["rho"], "mass": p["mass"], "radius": p["radius"],
           "Cd": float(Cd) if not isinstance(Cd, str) else float(p["Cd"]),
           "k": float(k) if not isinstance(k, str) else float(p["spin_decay_k"]),
           "g": p.get("g", G), "eps_v": 1e-6}
    if Cl is None:
        out["c1"], out["Clmax"] = 0.0, 0.0
    elif isinstance(Cl, str):
        out["c1"], out["Clmax"] = p["Cl"]
    else:
        out["c1"], out["Clmax"] = float(Cl[0]), float(Cl[1])
    return out


# --------------------------------------------------------------------------- impact law
def impact(v: Sequence[float], w: float, n: Sequence[float], m: float, R: float, I: float,
           e: float, mu: float, e_t: float = 0.0) -> tuple[np.ndarray, float, dict]:
    """Single rigid-sphere impact on a fixed surface with unit normal n (pointing to the ball).

    v = (vx, vz), w = omega_y. Returns (v', w', info) with info keys P_n, P_t, regime, v_cn, v_ct.
    No impulse if the contact is separating (v.n >= 0).
    """
    V, W, info = impact_batch(np.asarray(v, float)[None], np.array([float(w)]),
                              np.asarray(n, float)[None], m, R, I, e, mu, e_t)
    return V[0], float(W[0]), {k: (val[0] if isinstance(val, np.ndarray) else val)
                               for k, val in info.items()}


def impact_batch(v: np.ndarray, w: np.ndarray, n: np.ndarray, m: float, R: float, I: float,
                 e: Any, mu: Any, e_t: Any = 0.0) -> tuple[np.ndarray, np.ndarray, dict]:
    """Vectorised ``impact``: v (N,2), w (N,), n (N,2); e, mu, e_t scalars or (N,)."""
    v = np.asarray(v, float)
    w = np.asarray(w, float)
    n = np.asarray(n, float)
    e = np.broadcast_to(np.asarray(e, float), w.shape)
    mu = np.broadcast_to(np.asarray(mu, float), w.shape)
    e_t = np.broadcast_to(np.asarray(e_t, float), w.shape)
    t = np.stack([n[:, 1], -n[:, 0]], axis=1)
    v_cn = np.sum(v * n, axis=1)
    v_ct = np.sum(v * t, axis=1) - R * w
    alpha = I / (m * R * R)
    m_t = m * alpha / (1.0 + alpha)
    app = v_cn < 0.0
    P_n = np.where(app, -(1.0 + e) * m * v_cn, 0.0)
    P_star = -(1.0 + e_t) * m_t * v_ct
    stick = np.abs(P_star) <= mu * P_n
    P_t = np.where(stick, P_star, -mu * P_n * np.sign(v_ct))
    P_t = np.where(app, P_t, 0.0)
    v2 = v + (P_n[:, None] * n + P_t[:, None] * t) / m
    w2 = w - R * P_t / I
    regime = np.where(~app, "none", np.where(stick, "stick", "slip"))
    return v2, w2, {"P_n": P_n, "P_t": P_t, "regime": regime, "v_cn": v_cn, "v_ct": v_ct}


def spin_kick_direction(n: Sequence[float]) -> np.ndarray:
    """Direction of the extra velocity kick that BACKSPIN (w < 0, +x travel) adds at a contact
    with normal n, relative to the same impact without spin: k = -t = (-n_z, n_x) (derived)."""
    n = np.asarray(n, float)
    return np.array([-n[1], n[0]])


# --------------------------------------------------------------------------- geometry
def _offset_convex(poly: np.ndarray, dist: np.ndarray) -> np.ndarray:
    """Offset each edge i (poly[i] -> poly[i+1]) of a convex polygon outward by dist[i]."""
    k = len(poly)
    c = poly.mean(axis=0)
    lines = []
    for i in range(k):
        a, b = poly[i], poly[(i + 1) % k]
        d = b - a
        nrm = np.array([d[1], -d[0]]) / np.linalg.norm(d)
        if np.dot(nrm, a - c) < 0:
            nrm = -nrm
        lines.append((a + dist[i] * nrm, d))
    out = []
    for i in range(k):
        p1, d1 = lines[i - 1]
        p2, d2 = lines[i]
        A = np.array([d1, -d2]).T
        s = np.linalg.solve(A, p2 - p1)
        out.append(p1 + s[0] * d1)
    return np.array(out)


@dataclass
class ContactGeometry:
    """Segments + CELL region + trapping barrier for one Hive (shot frame)."""
    hive: hv.Hive
    A: np.ndarray
    B: np.ndarray
    names: list
    R: float
    cell_poly: np.ndarray        # ball-centre region counted as "in the CELL" (walls offset by ~R)
    z_barrier: float             # lowest centre height for crossing the mouth plane
    near_rim: int                # index of the near-rim segment (upper lip)
    far_rim: int                 # index of the far-rim segment (lower lip)
    bbox: tuple
    zone_of_seg: np.ndarray = field(default=None)

    @classmethod
    def from_hive(cls, h: hv.Hive) -> "ContactGeometry":
        R = h.R
        names = list(h.names)
        ins = np.asarray(h.inside, float)
        # identify the mouth edge of the inside polygon (both vertices on the mouth plane)
        dplane = np.abs((ins - h.mouth[0]) @ h.normal_out)
        k = len(ins)
        on_mouth = set(np.argsort(dplane)[:2].tolist())     # same rule as Hive.gate
        dist = np.empty(k)
        for i in range(k):
            on = i in on_mouth and (i + 1) % k in on_mouth
            dist[i] = 0.0 if on else (R - 1e-3)
        cell = _offset_convex(ins, dist)
        gate = h.gate
        z_bar = float(min(gate[0][1], gate[1][1]))
        near = names.index("up_upper_lip")
        far = names.index("up_lower_lip")
        allp = np.vstack([h.P0, h.P1])
        bbox = (allp[:, 0].min() - R - 0.02, allp[:, 0].max() + R + 0.02,
                allp[:, 1].min() - R - 0.02, allp[:, 1].max() + R + 0.02)
        return cls(hive=h, A=h.P0.copy(), B=h.P1.copy(), names=names, R=R, cell_poly=cell,
                   z_barrier=z_bar, near_rim=near, far_rim=far, bbox=bbox)

    @classmethod
    def unfavourable(cls, tilt_deg: Optional[float] = None, include_projected: bool = False,
                     lateral_offset: float = 0.0, ball_radius: Optional[float] = None
                     ) -> "ContactGeometry":
        """pose_pos seen from the 'neg' side (shot fired +x; shot frame == HIVE frame)."""
        kw = {}
        if tilt_deg is not None:
            kw["tilt_deg"] = tilt_deg
        if lateral_offset:
            kw["lateral_offset"] = lateral_offset
        if ball_radius is not None:
            kw["ball_radius"] = ball_radius
        h = hv.Hive.from_json("pose_pos", include_projected=include_projected, **kw)
        return cls.from_hive(h)

    @classmethod
    def favourable(cls, **kw) -> "ContactGeometry":
        """pose_pos seen from the 'pos' side, mirrored into the shot frame."""
        h = hv.Hive.from_json("pose_pos", **kw).mirrored()
        return cls.from_hive(h)

    # ---- queries
    def nearest(self, p: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """(distance, segment index, closest point) for centre points p (N, 2)."""
        p = np.asarray(p, float)
        ab = self.B - self.A                                   # (M,2)
        ap = p[:, None, :] - self.A[None]                      # (N,M,2)
        den = np.sum(ab * ab, axis=1)
        tt = np.clip(np.sum(ap * ab[None], axis=2) / den[None], 0.0, 1.0)
        q = self.A[None] + tt[..., None] * ab[None]
        d2 = np.sum((p[:, None, :] - q) ** 2, axis=2)
        j = np.argmin(d2, axis=1)
        r = np.arange(len(p))
        return np.sqrt(d2[r, j]), j, q[r, j]

    def in_bbox(self, p: np.ndarray) -> np.ndarray:
        x0, x1, z0, z1 = self.bbox
        return (p[:, 0] > x0) & (p[:, 0] < x1) & (p[:, 1] > z0) & (p[:, 1] < z1)

    def in_cell(self, p: np.ndarray) -> np.ndarray:
        return hv._points_in_convex(np.asarray(p, float), self.cell_poly)

    def zone(self, j: np.ndarray, q: np.ndarray, p: np.ndarray) -> np.ndarray:
        """Contact zone code (index into ZONES) from segment j, contact point q, centre p."""
        j = np.asarray(j)
        dn = hv.seg_point_dist(q, self.A[self.near_rim], self.B[self.near_rim])
        df = hv.seg_point_dist(q, self.A[self.far_rim], self.B[self.far_rim])
        z = np.full(len(j), 3, dtype=np.int8)
        incell = self.in_cell(p)
        interior_names = {"up_roof_inner", "up_floor", "up_back_wall", "up_tube_top_gap"}
        is_int = np.array([self.names[int(i)] in interior_names for i in j], dtype=bool) & incell
        z[is_int] = 2
        z[dn < 2e-3] = 0
        z[df < 2e-3] = 1
        return z


# --------------------------------------------------------------------------- flight core
def _acc(ap: dict, vx, vz, w):
    """Aero + gravity acceleration (2D) and spin rate, vectorised. Matches flight._aero."""
    R = ap["radius"]
    q = 0.5 * ap["rho"] * math.pi * R * R / ap["mass"]
    v2 = vx * vx + vz * vz
    vm = np.sqrt(v2)
    ax = -q * ap["Cd"] * vm * vx
    az = -q * ap["Cd"] * vm * vz - ap["g"]
    if ap["c1"] != 0.0 or ap["Clmax"] != 0.0:
        aw = np.abs(w)
        S = aw * R / np.sqrt(v2 + ap["eps_v"] ** 2)
        cl = np.minimum(ap["c1"] * S, ap["Clmax"])
        # omega x v = w (vz, -vx); flight.py: F_M = q Cl |v|^2 (omega x v)/sqrt(|omega x v|^2 + (eps |w|)^2)
        #           = q Cl |v|^2 sign(w) (vz, -vx) / sqrt(|v|^2 + eps^2)
        km = q * cl * v2 * np.sign(w) / np.sqrt(v2 + ap["eps_v"] ** 2)
        ax = ax + km * vz
        az = az - km * vx
    dw = -ap["k"] * w
    return ax, az, dw


def _rk4(ap: dict, Y: np.ndarray, dt) -> np.ndarray:
    """One RK4 step of Y = [x, z, vx, vz, w] (N,5); dt scalar or (N,)."""
    dt = np.asarray(dt, float)
    if dt.ndim == 1:
        dt = dt[:, None]

    def f(Y):
        ax, az, dw = _acc(ap, Y[:, 2], Y[:, 3], Y[:, 4])
        return np.stack([Y[:, 2], Y[:, 3], ax, az, dw], axis=1)

    k1 = f(Y)
    k2 = f(Y + 0.5 * dt * k1)
    k3 = f(Y + 0.5 * dt * k2)
    k4 = f(Y + dt * k3)
    return Y + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)


def free_flight(ap: dict, Y0: np.ndarray, t: float, dt: float = 1e-3) -> np.ndarray:
    """Integrate (forward, or backward for t < 0) without any contact."""
    Y = np.array(Y0, float, ndmin=2)
    n = max(1, int(math.ceil(abs(t) / dt)))
    h = t / n
    for _ in range(n):
        Y = _rk4(ap, Y, h)
    return Y


# --------------------------------------------------------------------------- simulation
def simulate_batch(Y0: np.ndarray, geom: ContactGeometry, ap: dict, cp: Any,
                   I_b: float, *, dt: float = 1e-3, t_max: float = 3.5,
                   z_stop: float = 0.70, stop_on_event: bool = False,
                   zero_spin_at_first_event: bool = False, max_iter: int = 8,
                   record_path: bool = False) -> dict:
    """Simulate N balls Y0 (N,5) = [x, z, vx, vz, w] with contacts.

    cp: ContactParams, or dict of arrays {'e','mu','e_t'} of shape (N,).
    stop_on_event: stop each ball at the START of the step in which its first event (first
      contact or first entry into the CELL) happens; returns that state in 'Y_event' (pre-roll for
      re-running with different contact parameters).
    zero_spin_at_first_event: set w = 0 at the start of the run (used for the 'airborne Magnus only'
      decomposition when restarting from a stage-1 event state).
    """
    Y = np.array(Y0, float, ndmin=2).copy()
    N = len(Y)
    m, R = ap["mass"], geom.R
    if isinstance(cp, ContactParams):
        E = np.full(N, cp.e)
        MU = np.full(N, cp.mu)
        ET = np.full(N, cp.e_t)
    else:
        E = np.broadcast_to(np.asarray(cp["e"], float), (N,)).copy()
        MU = np.broadcast_to(np.asarray(cp["mu"], float), (N,)).copy()
        ET = np.broadcast_to(np.asarray(cp.get("e_t", 0.0), float), (N,)).copy()
    if zero_spin_at_first_event:
        Y[:, 4] = 0.0
    out = {
        "outcome": np.full(N, -1, np.int8),
        "entered": np.zeros(N, bool),
        "clean_entry": np.zeros(N, bool),
        "n_contacts": np.zeros(N, np.int32),
        "n_bounces": np.zeros(N, np.int32),
        "first_seg": np.full(N, -1, np.int16),
        "first_zone": np.full(N, -1, np.int8),
        "first_vn": np.full(N, np.nan),
        "first_vt": np.full(N, np.nan),
        "first_S": np.full(N, np.nan),
        "first_regime": np.full(N, -1, np.int8),    # 0 slip, 1 stick
        "first_dv_in": np.full(N, np.nan),          # post-impact velocity change along -normal_out
        "first_normal": np.full((N, 2), np.nan),
        "first_point": np.full((N, 2), np.nan),
        "zones_mask": np.zeros(N, np.int16),        # bit z for zone z touched before entry
        "external_before_entry": np.zeros(N, bool),
        "t_end": np.full(N, np.nan),
        "Y_end": np.full((N, 5), np.nan),
        "Y_event": np.full((N, 5), np.nan),
        "event": np.full(N, -1, np.int8),           # stop_on_event: 0 contact, 1 entry, 2 none
    }
    d_in = -geom.hive.normal_out
    if record_path:
        paths = [[Y[i, :2].copy()] for i in range(N)]
    active = np.ones(N, bool)
    # balls that start penetrating are flagged blocked immediately (invalid start)
    d0, _, _ = geom.nearest(Y[:, :2])
    bad = d0 < R - 1e-6
    out["outcome"][bad] = O_BL
    out["t_end"][bad] = 0.0
    active &= ~bad
    t = 0.0
    nsteps = int(math.ceil(t_max / dt))
    I = I_b

    def _book(gi, jc, qc, pos, wc, vv, nvec, vcn, v2, info):
        """Contact statistics: first-contact record, impulse / bounce counts, zones before entry."""
        approaching = vcn < 0
        firstc = approaching & (out["n_contacts"][gi] == 0)
        if np.any(firstc):
            gf = gi[firstc]
            out["first_seg"][gf] = jc[firstc]
            out["first_zone"][gf] = geom.zone(jc[firstc], qc[firstc], pos[firstc])
            out["first_vn"][gf] = vcn[firstc]
            tv = np.stack([nvec[firstc, 1], -nvec[firstc, 0]], axis=1)
            out["first_vt"][gf] = np.sum(vv[firstc] * tv, axis=1)
            sp = np.sqrt(np.sum(vv[firstc] ** 2, axis=1))
            out["first_S"][gf] = wc[firstc] * R / np.maximum(sp, 1e-9)
            out["first_regime"][gf] = (info["regime"][firstc] == "stick").astype(np.int8)
            out["first_dv_in"][gf] = (v2[firstc] - vv[firstc]) @ d_in
            out["first_normal"][gf] = nvec[firstc]
            out["first_point"][gf] = qc[firstc]
        if np.any(approaching):
            ga = gi[approaching]
            out["n_contacts"][ga] += 1
            out["n_bounces"][ga] += (-vcn[approaching] > V_BOUNCE).astype(np.int32)
            notin = ~out["entered"][ga]
            zz = geom.zone(jc[approaching], qc[approaching], pos[approaching])
            out["zones_mask"][ga[notin]] |= (1 << zz[notin]).astype(np.int16)
            out["external_before_entry"][ga[notin & (zz == 3)]] = True
    for step in range(nsteps):
        idx = np.nonzero(active)[0]
        if idx.size == 0:
            break
        Ya = Y[idx]
        Yn = _rk4(ap, Ya, dt)
        # ---------------- contacts (iterate on the subset that penetrates)
        sub = np.nonzero(geom.in_bbox(Yn[:, :2]) | geom.in_bbox(Ya[:, :2]))[0]
        frac_done = np.zeros(len(idx))          # fraction of the step already consumed
        Ystart = Ya.copy()
        stop_ev = np.zeros(len(idx), bool)
        for it in range(max_iter):
            if sub.size == 0:
                break
            d, j, q = geom.nearest(Yn[sub, :2])
            pen = d < R - 1e-7
            if not np.any(pen):
                break
            s = sub[pen]
            if stop_on_event:
                first = out["n_contacts"][idx[s]] == 0
                if np.any(first):
                    stop_ev[s[first]] = True
                    s = s[~first]
                if s.size == 0:
                    sub = s
                    break
            # slow (resting / rolling) contacts: project the centre out to distance R and apply a
            # perfectly plastic (e = 0) impulse WITH Coulomb friction, no bisection (cheap and
            # reproduces rolling / sliding on an incline, see tests)
            dq, jq, qq = d[pen], j[pen], q[pen]
            if stop_on_event:
                dq, jq, qq = geom.nearest(Yn[s, :2])
            nq = (Yn[s, :2] - qq) / np.maximum(dq, 1e-12)[:, None]
            slow = np.sum(Yn[s, 2:4] * nq, axis=1) > -V_REST
            if np.any(slow):
                ss = s[slow]
                gi = idx[ss]
                pos = qq[slow] + R * nq[slow]
                vv = Yn[ss, 2:4].copy()
                vcn = np.sum(vv * nq[slow], axis=1)
                v2, w2, info = impact_batch(vv, Yn[ss, 4], nq[slow], m, R, I, 0.0, MU[gi], 0.0)
                _book(gi, jq[slow], qq[slow], pos, Yn[ss, 4], vv, nq[slow], vcn, v2, info)
                appr = vcn < 0
                Yn[ss, 0:2] = pos
                Yn[ss, 2:4] = np.where(appr[:, None], v2, vv)
                Yn[ss, 4] = np.where(appr, w2, Yn[ss, 4])
                s = s[~slow]
                if s.size == 0:
                    sub = s
                    break
            P0 = Ystart[s]
            P1 = Yn[s]
            lo = np.zeros(len(s))
            hi = np.ones(len(s))
            for _ in range(22):
                mid = 0.5 * (lo + hi)
                pm = P0[:, :2] + mid[:, None] * (P1[:, :2] - P0[:, :2])
                dm, _, _ = geom.nearest(pm)
                pen_m = dm < R
                hi = np.where(pen_m, mid, hi)
                lo = np.where(pen_m, lo, mid)
            f = lo
            Yc = P0 + f[:, None] * (P1 - P0)
            dc, jc, qc = geom.nearest(Yc[:, :2])
            nvec = (Yc[:, :2] - qc) / np.maximum(dc, 1e-12)[:, None]
            vv = Yc[:, 2:4].copy()
            vcn = np.sum(vv * nvec, axis=1)
            gi = idx[s]
            e_eff = np.where(-vcn < V_REST, 0.0, E[gi])
            v2, w2, info = impact_batch(vv, Yc[:, 4], nvec, m, R, I, e_eff, MU[gi], ET[gi])
            _book(gi, jc, qc, Yc[:, :2], Yc[:, 4], vv, nvec, vcn, v2, info)
            approaching = vcn < 0
            Yc[:, 2:4] = np.where(approaching[:, None], v2, vv)
            Yc[:, 4] = np.where(approaching, w2, Yc[:, 4])
            # re-integrate the remaining part of the step
            rem = (1.0 - f) * (1.0 - frac_done[s]) * dt
            frac_done[s] = frac_done[s] + (1.0 - frac_done[s]) * f
            Ystart[s] = Yc
            Yn[s] = _rk4(ap, Yc, rem)
            sub = s
        else:
            # still penetrating after max_iter: project out with a plastic frictional impulse
            if sub.size:
                d, j, q = geom.nearest(Yn[sub, :2])
                pen = d < R - 1e-7
                s = sub[pen]
                if s.size:
                    nvec = (Yn[s, :2] - q[pen]) / np.maximum(d[pen], 1e-12)[:, None]
                    Yn[s, :2] = q[pen] + R * nvec
                    gi = idx[s]
                    v2, w2, _ = impact_batch(Yn[s, 2:4], Yn[s, 4], nvec, m, R, I, 0.0, MU[gi], 0.0)
                    Yn[s, 2:4] = v2
                    Yn[s, 4] = w2
        if stop_on_event and np.any(stop_ev):
            gs = idx[stop_ev]
            out["Y_event"][gs] = Ya[stop_ev]
            out["event"][gs] = 0
            out["t_end"][gs] = t
            active[gs] = False
        Y[idx] = np.where(stop_ev[:, None], Ya, Yn)
        t += dt
        live = ~stop_ev
        if record_path:
            for k in np.nonzero(live)[0]:
                paths[idx[k]].append(Yn[k, :2].copy())
        # ---------------- entry / trapping / termination
        Yl = Yn
        incell = geom.in_cell(Yl[:, :2]) & live
        newin = incell & ~out["entered"][idx]
        if np.any(newin):
            gn = idx[newin]
            out["clean_entry"][gn] = out["n_contacts"][gn] == 0
            out["entered"][gn] = True
            if stop_on_event:
                ce = newin & (out["n_contacts"][idx] == 0)
                gs = idx[ce]
                out["Y_event"][gs] = Ya[ce]
                out["event"][gs] = 1
                out["t_end"][gs] = t - dt
                out["entered"][gs] = False      # stage 2 re-detects the entry
                out["clean_entry"][gs] = False
                active[gs] = False
                incell = incell & ~ce
                live = live & ~ce
        Etot = Yl[:, 1] + (Yl[:, 2] ** 2 + Yl[:, 3] ** 2) / (2 * G) + I * Yl[:, 4] ** 2 / (2 * m * G)
        trapped = incell & (Etot < geom.z_barrier - 1e-4) & live
        if np.any(trapped):
            gt = idx[trapped]
            out["outcome"][gt] = np.where(out["clean_entry"][gt], O_RC, O_RK)
            out["t_end"][gt] = t
            active[gt] = False
        # a ball outside the CELL whose total energy is below the gate's low end can never cross
        # the mouth plane again (same argument as TRAPPED, mirrored) -> resolved now
        locked_out = ~incell & (Etot < geom.z_barrier - 1e-4)
        gone = live & ~trapped & (((Yl[:, 1] < z_stop) & (Yl[:, 3] < 0)) | locked_out |
                                  (np.abs(Yl[:, 0]) > 3.0) | (Yl[:, 1] < 0.0))
        if np.any(gone):
            gg = idx[gone]
            ent = out["entered"][gg]
            hit = out["n_contacts"][gg] > 0
            out["outcome"][gg] = np.where(ent, O_BO, np.where(hit, O_BL, O_MI))
            out["t_end"][gg] = t
            active[gg] = False
    rem = np.nonzero(active)[0]
    # unresolved at t_max: entered-but-not-trapped -> timeout; never entered but touched the HIVE
    # (e.g. resting on the outer roof or the pivot plate) -> blocked; untouched -> miss
    out["outcome"][rem] = np.where(out["entered"][rem], O_TO, np.where(
        out["n_contacts"][rem] > 0, O_BL, O_MI))
    out["t_end"][rem] = t
    if stop_on_event:
        out["event"][(out["event"] < 0)] = 2
    out["Y_end"] = Y
    if record_path:
        out["paths"] = [np.array(p) for p in paths]
    return out


def simulate_one(x0, v0, w0, geom: Optional[ContactGeometry] = None, ap: Optional[dict] = None,
                 cp: Optional[ContactParams] = None, I_b: Optional[float] = None, **kw) -> dict:
    """Convenience single-ball run; returns scalars plus 'outcome_name' and 'path'."""
    geom = geom or ContactGeometry.unfavourable()
    ap = ap or aero_case()
    cp = cp or ContactParams()
    I_b = I_b if I_b is not None else ball_props()["I_b"]
    Y0 = np.array([[x0[0], x0[1], v0[0], v0[1], w0]], float)
    o = simulate_batch(Y0, geom, ap, cp, I_b, record_path=True, **kw)
    res = {k: (v[0] if isinstance(v, np.ndarray) else v) for k, v in o.items() if k != "paths"}
    res["path"] = o["paths"][0]
    res["outcome_name"] = OUTCOMES[int(res["outcome"])]
    return res


# --------------------------------------------------------------------------- state builders
def launch_states(h: float, d: float, v: np.ndarray, theta_deg: np.ndarray, S0: float,
                  R: float) -> np.ndarray:
    """Launch states from (x=-d, z=h) toward +x. S0 > 0 = backspin (w = -S0 v/R)."""
    th = np.radians(theta_deg)
    Y = np.empty((len(v), 5))
    Y[:, 0] = -d
    Y[:, 1] = h
    Y[:, 2] = v * np.cos(th)
    Y[:, 3] = v * np.sin(th)
    Y[:, 4] = -S0 * v / R
    return Y


def incidence_states(geom: ContactGeometry, ap: dict, s: np.ndarray, phi_deg: np.ndarray,
                     v_i: np.ndarray, S_i: np.ndarray, t_back: float = 0.10) -> np.ndarray:
    """Pre-impact states whose FREE path would cross the mouth plane at gate coordinate s
    (m, from the gate's low end toward its high end) with descent angle phi (deg below horizontal,
    moving +x), speed v_i and spin parameter S_i (> 0 backspin). Built by integrating the free
    flight (same aero) backward for t_back seconds from the crossing state."""
    g0, g1 = geom.hive.gate[0], geom.hive.gate[1]
    gd = (g1 - g0) / np.linalg.norm(g1 - g0)
    C = g0[None] + s[:, None] * gd[None]
    ph = np.radians(phi_deg)
    Y = np.empty((len(s), 5))
    Y[:, 0:2] = C
    Y[:, 2] = v_i * np.cos(ph)
    Y[:, 3] = -v_i * np.sin(ph)
    Y[:, 4] = -S_i * v_i / geom.R
    return free_flight(ap, Y, -t_back, dt=1e-3)


# --------------------------------------------------------------------------- sweeps (CLI)
E_GRID = (0.3, 0.45, 0.6, 0.8)
MU_GRID = (0.2, 0.4, 0.6, 0.8)
S_GRID = (0.0, 0.5, 1.0, 1.5, 2.0)


def _gauss_best(ind: np.ndarray, sig_cells: tuple) -> float:
    from scipy.ndimage import gaussian_filter
    if ind.size == 0:
        return 0.0
    g = gaussian_filter(ind.astype(float), sigma=sig_cells, mode="constant", cval=0.0)
    return float(g.max())


def _max_square(c: np.ndarray) -> int:
    """Largest all-True k x k block in a 2D bool array."""
    if c.size == 0:
        return 0
    D = np.zeros((c.shape[0] + 1, c.shape[1] + 1), int)
    best = 0
    for i in range(c.shape[0]):
        for j in range(c.shape[1]):
            if c[i, j]:
                D[i + 1, j + 1] = 1 + min(D[i, j], D[i + 1, j], D[i, j + 1])
                best = max(best, D[i + 1, j + 1])
    return best


def _runs(mask: np.ndarray, step: float) -> tuple[float, float]:
    """(total true length, longest contiguous true run) along a 1D grid with spacing step."""
    tot = float(mask.sum()) * step
    best = cur = 0
    for b in mask:
        cur = cur + 1 if b else 0
        best = max(best, cur)
    return tot, best * step


def _write_csv(path: str, header_lines: list, fields: list, rows: list) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        for h in header_lines:
            fh.write("# " + h + "\n")
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})


def run_incidence(out_dir: str, fast: bool = False) -> list:
    """Part A: local incidence sweep at the unfavourable-side mouth (predicted)."""
    geom = ContactGeometry.unfavourable()
    bp = ball_props()
    ds = 0.005 if not fast else 0.02
    s_grid = np.round(np.arange(-0.10, 0.45 + 1e-9, ds), 4)
    phi_grid = np.arange(60.0, 88.01, 2.0) if not fast else np.array([66.0, 76.0, 86.0])
    rows = []
    variants = []
    for S in S_GRID:
        for e in E_GRID:
            for mu in MU_GRID:
                variants.append(dict(tag="main", S=S, e=e, mu=mu, v_i=5.0, Cl="nominal", e_t=0.0,
                                     Ib="value"))
    for S in (0.0, 1.0):
        for v_i in (3.5, 6.5):
            variants.append(dict(tag="speed", S=S, e=0.6, mu=0.4, v_i=v_i, Cl="nominal",
                                 e_t=0.0, Ib="value"))
        for e_t in (0.3,):
            variants.append(dict(tag="e_t", S=S, e=0.6, mu=0.4, v_i=5.0, Cl="nominal", e_t=e_t,
                                 Ib="value"))
        for Ib in ("low", "high"):
            variants.append(dict(tag="I_b", S=S, e=0.6, mu=0.4, v_i=5.0, Cl="nominal", e_t=0.0,
                                 Ib=Ib))
        for cl in ("low", "high", None):
            variants.append(dict(tag="Cl", S=S, e=0.6, mu=0.4, v_i=5.0, Cl=cl, e_t=0.0, Ib="value"))
    variants.append(dict(tag="topspin_exploratory", S=-1.0, e=0.6, mu=0.4, v_i=5.0, Cl="nominal",
                         e_t=0.0, Ib="value"))
    if fast:
        variants = variants[:6]
    # group by (v_i, Cl, Ib) to batch all (S, e, mu, e_t) together
    groups: dict = {}
    for k, vdef in enumerate(variants):
        groups.setdefault((vdef["v_i"], str(vdef["Cl"]), vdef["Ib"]), []).append(k)
    res_by_var = {}
    for (v_i, cl, Ib), ks in groups.items():
        ap = aero_case(Cl=None if cl == "None" else cl)
        I = ball_props(Ib)["I_b"]
        SS, PP, VV, EE, MM, TT, KK = [], [], [], [], [], [], []
        for k in ks:
            vd = variants[k]
            PHI, SG = np.meshgrid(phi_grid, s_grid, indexing="ij")
            n = PHI.size
            SS.append(SG.ravel()); PP.append(PHI.ravel())
            VV.append(np.full(n, vd["S"])); EE.append(np.full(n, vd["e"]))
            MM.append(np.full(n, vd["mu"])); TT.append(np.full(n, vd["e_t"])); KK.append(np.full(n, k))
        s_all = np.concatenate(SS); phi_all = np.concatenate(PP); S_all = np.concatenate(VV)
        Y0 = incidence_states(geom, ap, s_all, phi_all, np.full(len(s_all), v_i), S_all)
        e_all, mu_all, et_all = np.concatenate(EE), np.concatenate(MM), np.concatenate(TT)
        chunk = 12000  # bounded memory per batch
        parts = []
        for i0 in range(0, len(s_all), chunk):
            sl = slice(i0, i0 + chunk)
            parts.append(simulate_batch(Y0[sl], geom, ap, {"e": e_all[sl], "mu": mu_all[sl],
                                                           "e_t": et_all[sl]}, I, t_max=2.0))
            print(f"  A v_i={v_i} Cl={cl} Ib={Ib}: {min(i0 + chunk, len(s_all))}/{len(s_all)}", flush=True)
        n_sl = [len(p["outcome"]) for p in parts]
        o = {key: (np.concatenate([p[key] for p in parts])
                   if all(isinstance(p[key], np.ndarray) and p[key].ndim >= 1 and len(p[key]) == m
                          for p, m in zip(parts, n_sl)) else parts[0][key])
             for key in parts[0]}
        kk = np.concatenate(KK)
        for k in ks:
            sel = kk == k
            res_by_var[k] = {key: (val[sel] if isinstance(val, np.ndarray) and len(val) == len(kk)
                                   else val) for key, val in o.items()}
            res_by_var[k]["s"] = s_all[sel]
            res_by_var[k]["phi"] = phi_all[sel]
    for k, vd in enumerate(variants):
        r = res_by_var[k]
        for phi in phi_grid:
            sel = r["phi"] == phi
            oc = r["outcome"][sel]
            ret = (oc == O_RC) | (oc == O_RK)
            rc = oc == O_RC
            rk = oc == O_RK
            sv = r["s"][sel]
            fz = r["first_zone"][sel]
            ext = r["external_before_entry"][sel]
            tot_ret, run_ret = _runs(ret, ds)
            tot_rc, _ = _runs(rc, ds)
            tot_rk, _ = _runs(rk, ds)
            # contact-assisted retention by first-contact zone
            w_zone = {z: float(np.sum(rk & (fz == zi))) * ds for zi, z in enumerate(ZONES)}
            w_rk_noext = float(np.sum(rk & ~ext)) * ds
            # clean entries that bounced out
            ce_bo = float(np.sum((oc == O_BO) & r["clean_entry"][sel])) * ds
            invalid = float(np.sum(r["t_end"][sel] == 0.0)) * ds
            # best retention probability for Gaussian aim scatter in s
            pb = {}
            for sig in (0.01, 0.02, 0.04):
                sc = sig / ds
                pb[sig] = _gauss_best(ret, (sc,))
            rows.append({
                "tag": vd["tag"], "S_pre": vd["S"], "e": vd["e"], "mu": vd["mu"], "e_t": vd["e_t"],
                "v_i": vd["v_i"], "Cl": str(vd["Cl"]), "I_b": vd["Ib"], "phi_deg": float(phi),
                "w_retained_m": tot_ret, "longest_retained_run_m": run_ret,
                "w_retained_clean_m": tot_rc, "w_retained_contact_m": tot_rk,
                "w_rk_near_rim_m": w_zone["near_rim"], "w_rk_far_rim_m": w_zone["far_rim"],
                "w_rk_interior_m": w_zone["interior"], "w_rk_external_m": w_zone["external"],
                "w_rk_without_external_m": w_rk_noext,
                "w_clean_entry_bounced_out_m": ce_bo, "w_invalid_start_m": invalid,
                "P_best_sig10mm": pb[0.01], "P_best_sig20mm": pb[0.02], "P_best_sig40mm": pb[0.04],
            })
    hdr = ["PREDICTED. Part A incidence sweep, unfavourable side (pose_pos from the neg side, tilt 30 deg confirmed),"
           " 2D centre plane. Ball state set at the mouth-plane crossing of its FREE path: gate coordinate s"
           f" (m, from the gate low end, grid {s_grid[0]}..{s_grid[-1]} step {ds}), descent angle phi, speed v_i,"
           " pre-impact spin S_pre = |w|R/v (>0 backspin), then integrated backward 0.10 s and run forward with contacts.",
           "e, mu, e_t ASSUMED (no POLLEN-on-HIVE measurement). Aero = " + fl.aero_tag() + ".json bounds (ASSUMED). I_b derived.",
           "w_* = total width of s (m) giving the outcome; clean gate width for comparison ~0.286 m. P_best_sigX = best"
           " achievable retention probability for Gaussian aim scatter sigma_s = X along the gate (assumed scatter).",
           "w_rk_<zone> = retained after >=1 contact, by FIRST-contact zone. external = roof top / outer faces"
           " (G417 bank-shot risk, see docs/05_contact.md). w_invalid_start = free path started inside an obstacle."]
    _write_csv(os.path.join(out_dir, "contact_incidence_sweep.csv"), hdr, list(rows[0].keys()), rows)
    return rows, res_by_var, variants, s_grid, phi_grid


# ---- Part B: full launches
HD_CASES = ((0.737, 0.65), (0.737, 0.70), (0.737, 0.75), (0.737, 0.90), (0.737, 1.15),
            (0.35, 0.75), (0.35, 0.90), (0.35, 1.15))
FLIGHT_CASES = {
    # key: (S0, Cl for flight+contact phase, zero spin at first event, no-Magnus throughout)
    "S0": dict(S=0.0, Cl=None),
    "S0.5_nom": dict(S=0.5, Cl="nominal"),
    "S1_low": dict(S=1.0, Cl="low"),
    "S1_nom": dict(S=1.0, Cl="nominal"),
    "S1_high": dict(S=1.0, Cl="high"),
    "S2_nom": dict(S=2.0, Cl="nominal"),
    "S1_nom_airOnly": dict(S=1.0, Cl="nominal", zero=True),
    "S1_collOnly": dict(S=1.0, Cl=None),
}



def _launch_grid(fast: bool):
    dv, dth = 0.05, 0.25
    v_grid = np.round(np.arange(5.0, 9.5 + 1e-9, dv), 3) if not fast else np.arange(6.0, 8.0, 0.2)
    # lower edge 60 deg: at 66 deg the S0 retained windows touched the grid edge (review 2026-10-30 #7)
    th_grid = np.round(np.arange(60.0, 89.75 + 1e-9, dth), 3) if not fast else np.arange(72.0, 86.0, 1.0)
    return np.meshgrid(v_grid, th_grid, indexing="ij")


def _launch_job(job) -> str:
    """One Part-B job: stage 1 (flight to the first HIVE event, contact law irrelevant) and
    stage 2 (replicated over the (e, mu) grid from the stage-1 event state). Writes cfile."""
    h, d, fk, tilt, tag, eg, mg, cfile, fast = job
    t0 = time.time()
    fc = FLIGHT_CASES[fk]
    geom = ContactGeometry.unfavourable(tilt_deg=tilt)
    bp = ball_props()
    V, TH = _launch_grid(fast)
    ap = aero_case(Cl=fc["Cl"])
    Y0 = launch_states(h, d, V.ravel(), TH.ravel(), fc["S"], bp["radius"])
    st1 = simulate_batch(Y0, geom, ap, ContactParams(), bp["I_b"], stop_on_event=True, t_max=3.5)
    cand = np.nonzero(st1["event"] < 2)[0]
    n_e, n_m = len(eg), len(mg)
    outc = np.empty((n_e, n_m, V.size), np.int8)
    ce = np.zeros((n_e, n_m, V.size), bool)
    fzn = np.full((n_e, n_m, V.size), -1, np.int8)
    ext = np.zeros((n_e, n_m, V.size), bool)
    dvin = np.full((n_e, n_m, V.size), np.nan, np.float32)
    nb = np.zeros((n_e, n_m, V.size), np.int16)
    outc[:] = st1["outcome"][None, None]
    if cand.size:
        EE, MM = np.meshgrid(np.array(eg), np.array(mg), indexing="ij")
        Yc = np.repeat(st1["Y_event"][cand][None], EE.size, axis=0).reshape(-1, 5)
        ee = np.repeat(EE.ravel(), cand.size)
        mm = np.repeat(MM.ravel(), cand.size)
        keys = ("outcome", "clean_entry", "first_zone", "external_before_entry", "first_dv_in", "n_bounces")
        parts = []
        for i0 in range(0, len(ee), 8000):  # bounded memory per batch
            sl = slice(i0, i0 + 8000)
            p = simulate_batch(Yc[sl], geom, ap, {"e": ee[sl], "mu": mm[sl]}, bp["I_b"], t_max=2.5,
                               zero_spin_at_first_event=fc.get("zero", False))
            parts.append({k: p[k] for k in keys})
            del p
        st2 = {k: np.concatenate([p[k] for p in parts]) for k in keys}
        sh = (n_e, n_m, cand.size)
        outc[:, :, cand] = st2["outcome"].reshape(sh)
        ce[:, :, cand] = st2["clean_entry"].reshape(sh)
        fzn[:, :, cand] = st2["first_zone"].reshape(sh)
        ext[:, :, cand] = st2["external_before_entry"].reshape(sh)
        dvin[:, :, cand] = st2["first_dv_in"].reshape(sh)
        nb[:, :, cand] = np.minimum(st2["n_bounces"], 32000).reshape(sh)
    tmp = cfile[:-4] + ".tmp.npz"
    np.savez_compressed(tmp, outcome=outc, clean_entry=ce, first_zone=fzn, ext=ext,
                        first_dv_in=dvin, n_bounces=nb, event=st1["event"],
                        v=V.ravel(), theta=TH.ravel(), e=np.array(eg), mu=np.array(mg))
    os.replace(tmp, cfile)  # atomic: a crashed job never leaves a partial cache file
    return f"  B {tag} h={h} d={d} {fk}: {cand.size} candidates, {time.time() - t0:.1f}s"


def run_launch(out_dir: str, cache: str, fast: bool = False, hd_cases=HD_CASES,
               flight_cases=None, tilt: Optional[float] = None, tag: str = "t30",
               eg=E_GRID, mg=MU_GRID, workers: int = 10) -> list:
    """Part B: (v, elevation) launch grids, two-stage (flight to first event, then contacts).
    Each (h, d, flight case) is one job (run in parallel processes) cached as an .npz."""
    flight_cases = flight_cases or list(FLIGHT_CASES)
    geom = ContactGeometry.unfavourable(tilt_deg=tilt)
    bp = ball_props()
    dv, dth = 0.05, 0.25
    V, TH = _launch_grid(fast)
    v_grid, th_grid = V[:, 0], TH[0]
    rows = []
    os.makedirs(cache, exist_ok=True)
    jobs = []
    for (h, d) in hd_cases:
        for fk in flight_cases:
            cfile = os.path.join(cache, f"B_{tag}_{h}_{d}_{fk}.npz")
            if fast or not os.path.exists(cfile):
                jobs.append((h, d, fk, tilt, tag, tuple(eg), tuple(mg), cfile, fast))
    if jobs:
        if workers > 1 and len(jobs) > 1:
            from concurrent.futures import ProcessPoolExecutor
            with ProcessPoolExecutor(max_workers=min(workers, len(jobs))) as ex:
                for msg in ex.map(_launch_job, jobs):
                    print(msg, flush=True)
        else:
            for jb in jobs:
                print(_launch_job(jb), flush=True)
    for (h, d) in hd_cases:
        for fk in flight_cases:
            cfile = os.path.join(cache, f"B_{tag}_{h}_{d}_{fk}.npz")
            z = np.load(cfile)
            outc = z["outcome"].reshape(len(eg), len(mg), *V.shape)
            extra = {k: z[k].reshape(len(eg), len(mg), *V.shape) for k in
                     ("clean_entry", "first_zone", "ext")}
            for ie, e in enumerate(eg):
                for im, mu in enumerate(mg):
                    oc = outc[ie, im]
                    ret = (oc == O_RC) | (oc == O_RK)
                    for vcap in (8.9, 9.5):
                        vm = (V[:, 0] <= vcap + 1e-9)
                        r = ret[vm]
                        o2 = oc[vm]
                        exb = extra["ext"][ie, im][vm]
                        rows.append({
                            "geometry": f"unfav_{tag}", "h": h, "d": d, "case": fk, "e": e, "mu": mu,
                            "v_cap": vcap,
                            "n_retained": int(r.sum()),
                            "n_retained_clean": int((o2 == O_RC).sum()),
                            "n_retained_contact": int((o2 == O_RK).sum()),
                            "n_retained_contact_no_external": int(((o2 == O_RK) & ~exb).sum()),
                            "n_clean_entry_bounced_out": int(((o2 == O_BO) &
                                                              extra["clean_entry"][ie, im][vm]).sum()),
                            "n_bounced_out": int((o2 == O_BO).sum()),
                            "n_timeout": int((o2 == OUTCOMES.index("timeout")).sum()),
                            "theta_min_at_grid_edge": bool(r.any() and TH[vm][r].min() <= th_grid[0] + 1e-9),
                            "max_square_cells": _max_square(r),
                            "P_best_tight": _gauss_best(r, (0.05 / dv, 0.25 / dth)),
                            "P_best_loose": _gauss_best(r, (0.15 / dv, 0.75 / dth)),
                            "v_min": float(V[vm][r].min()) if r.any() else float("nan"),
                            "v_max": float(V[vm][r].max()) if r.any() else float("nan"),
                            "theta_min": float(TH[vm][r].min()) if r.any() else float("nan"),
                            "theta_max": float(TH[vm][r].max()) if r.any() else float("nan"),
                        })
    hdr = [f"PREDICTED. Part B full-launch sweep, unfavourable side, geometry {tag}. Shooter at x=-d, ball-centre"
           f" height h, fires +x; v {v_grid[0]}..{v_grid[-1]} step {dv} m/s, elevation {th_grid[0]}..{th_grid[-1]}"
           f" step {dth} deg; launch S0 > 0 = backspin (w=-S0 v/R).",
           "case: S0 no spin; S<x>_<Cl> spin with Magnus (Cl set); S1_nom_airOnly = Magnus flight but spin set to 0 at"
           " the first HIVE event (airborne contribution only); S1_collOnly = spin carried into contacts but Cl=0 throughout"
           " (collision contribution only). e, mu ASSUMED; aero ASSUMED bounds; 2D centre plane.",
           "n_* = number of (v, elevation) cells (0.05 m/s x 0.25 deg). P_best_tight / loose = best retention probability"
           " over aim point for Gaussian launcher scatter sigma_v 0.05 / 0.15 m/s, sigma_elev 0.25 / 0.75 deg (ASSUMED"
           " scatter levels; distance scatter not included). max_square = largest all-retained k x k block."
           " n_timeout = unresolved at t_max (not retained). theta_min_at_grid_edge = the retained window reaches the"
           " lowest elevation of the grid (count is then a lower bound)."
           f" Aero file {fl.aero_tag()}.json."]
    _write_csv(os.path.join(out_dir, f"contact_launch_sweep_{tag}.csv"), hdr, list(rows[0].keys()), rows)
    return rows


# --------------------------------------------------------------------------- report (figures, summaries)
_COL = {"blue": "#2a78d6", "orange": "#eb6834", "aqua": "#1baf7a", "yellow": "#eda100",
        "magenta": "#e87ba4", "green": "#008300", "violet": "#6250d6", "red": "#e34948",
        "ink": "#1f2328", "muted": "#6e7781", "grid": "#d8dee4", "bg": "#ffffff"}
#: outcome colours (index = outcome code): clean, contact, bounced out, blocked, miss, timeout
_OCOL = ["#2a78d6", "#1baf7a", "#eb6834", "#c9d1d9", "#ffffff", "#6250d6"]


def _near_miss(clean: np.ndarray, k: int = 2) -> np.ndarray:
    """Cells within k grid cells (Chebyshev) of a clean cell that are not clean themselves."""
    from scipy.ndimage import binary_dilation
    return binary_dilation(clean, structure=np.ones((2 * k + 1, 2 * k + 1), bool)) & ~clean


def _load_case(cache, tag, h, d, fk):
    z = np.load(os.path.join(cache, f"B_{tag}_{h}_{d}_{fk}.npz"))
    V, TH = _launch_grid(False)
    ne, nm = len(z["e"]), len(z["mu"])
    return {k: (z[k].reshape(ne, nm, *V.shape) if z[k].ndim == 3 else z[k]) for k in z.files}, V, TH


def _outcome_legend(fig):
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(facecolor=_OCOL[i], label=OUTCOMES[i].replace("_", " "),
                              edgecolor=_COL["muted"], lw=0.5) for i in range(5)],
               loc="outside lower center", ncol=5, frameon=False)


def run_report(out_dir: str, fig_dir: str, cache: str) -> dict:
    """Controlled S0-vs-spin comparison, airborne/collision decomposition, kick statistics and
    figures. Needs data/contact_incidence_sweep.csv and the Part B cache."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    plt.rcParams.update({"font.size": 8, "axes.edgecolor": _COL["muted"], "axes.labelcolor": _COL["ink"],
                         "xtick.color": _COL["muted"], "ytick.color": _COL["muted"],
                         "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 1.5})
    summary: dict = {}
    geom = ContactGeometry.unfavourable()
    bp = ball_props()
    cmap = ListedColormap(_OCOL)
    # ---------------- (1) controlled first-contact kick statistics + incidence maps (nominal e, mu)
    ds = 0.005
    s_grid = np.round(np.arange(-0.10, 0.45 + 1e-9, ds), 4)
    phi_grid = np.arange(60.0, 88.01, 2.0)
    PHI, SG = np.meshgrid(phi_grid, s_grid, indexing="ij")
    ap = aero_case()
    maps, firsts = {}, {}
    for S in (0.0, 1.0, 2.0):
        Y0 = incidence_states(geom, ap, SG.ravel(), PHI.ravel(), np.full(SG.size, 5.0),
                              np.full(SG.size, S))
        o = simulate_batch(Y0, geom, ap, ContactParams(0.6, 0.4), bp["I_b"], t_max=2.0)
        maps[S] = o["outcome"].reshape(PHI.shape)
        firsts[S] = o
    kick_rows = []
    for S in (1.0, 2.0):
        a, b = firsts[0.0], firsts[S]
        for zi, zn in enumerate(ZONES):
            sel = (a["first_zone"] == zi) & (b["first_zone"] == zi) & (a["first_vn"] < -V_BOUNCE)
            if not np.any(sel):
                continue
            dd = b["first_dv_in"][sel] - a["first_dv_in"][sel]
            ret_a = np.isin(a["outcome"][sel], (O_RC, O_RK))
            ret_b = np.isin(b["outcome"][sel], (O_RC, O_RK))
            kick_rows.append({"S_pre": S, "zone": zn, "n_same_zone_contacts": int(sel.sum()),
                              "median_extra_dv_inward_mps": float(np.median(dd)),
                              "frac_extra_dv_inward_positive": float(np.mean(dd > 1e-6)),
                              "frac_extra_dv_inward_negative": float(np.mean(dd < -1e-6)),
                              "frac_stick_S0": float(np.mean(a["first_regime"][sel] == 1)),
                              "frac_stick_spin": float(np.mean(b["first_regime"][sel] == 1)),
                              "retained_frac_S0": float(ret_a.mean()),
                              "retained_frac_spin": float(ret_b.mean())})
    _write_csv(os.path.join(out_dir, "contact_kick_stats.csv"),
               ["PREDICTED. Controlled first-contact comparison at identical mouth-plane crossing states"
                " (s, phi grid of Part A, v_i 5 m/s) with pre-impact S = 0 vs S_pre (backspin); e 0.6, mu 0.4"
                " ASSUMED; nominal aero ASSUMED. Only balls whose FIRST contact is in the same zone in both runs"
                " with approach speed > 0.1 m/s.",
                "extra_dv_inward = (velocity change at first contact, spin run) - (same, no-spin run), projected"
                " on the CELL inward axis -normal_out = (-0.866, -0.5) (m/s). near_rim = upper lip / roof end, far_rim ="
                " lower lip, interior = inside the CELL, external = roof top / outer faces. retained_frac = final outcome.",
                "CAUTION near_rim / external: the derived backspin kick there is backward-and-down AROUND the roof corner,"
                " away from the mouth; it projects positively on the CELL axis but does not push the ball into the mouth."
                " Use retained_frac_* for the effect on scoring."],
               list(kick_rows[0].keys()), kick_rows)
    summary["kick"] = kick_rows
    gl = float(np.linalg.norm(geom.hive.gate[1] - geom.hive.gate[0]))
    fig, axs = plt.subplots(1, 3, figsize=(10.5, 3.8), sharey=True, layout="constrained")
    for ax, S in zip(axs, (0.0, 1.0, 2.0)):
        ax.imshow(maps[S], origin="lower", aspect="auto", cmap=cmap, vmin=-0.5, vmax=5.5,
                  extent=(s_grid[0] - ds / 2, s_grid[-1] + ds / 2, phi_grid[0] - 1, phi_grid[-1] + 1),
                  interpolation="nearest")
        for xg in (0.0, gl):
            ax.axvline(xg, color=_COL["ink"], lw=0.8, ls="--")
        ax.set_title(f"pre-impact backspin S = {S:g}", color=_COL["ink"])
        ax.set_xlabel(f"free-path crossing s along the gate (m)\n0 = far rim (lower lip), {gl:.3f} = near rim")
    axs[0].set_ylabel("descent angle at the mouth plane (deg)")
    _outcome_legend(fig)
    fig.suptitle("PREDICTED outcome at the unfavourable-side mouth, v 5 m/s, e 0.6, mu 0.4 (assumed)",
                 color=_COL["ink"])
    fig.savefig(os.path.join(fig_dir, "contact_incidence_maps.png"), dpi=150)
    plt.close(fig)
    # ---------------- (2) retention width vs spin from the Part A CSV
    with open(os.path.join(out_dir, "contact_incidence_sweep.csv"), encoding="utf-8") as fh:
        rowsA = list(csv.DictReader(r for r in fh if not r.startswith("#")))
    main_rows = [r for r in rowsA if r["tag"] == "main" and 64.0 <= float(r["phi_deg"]) <= 86.0]

    def agg(e=None, mu=None, key="w_retained_m"):
        out = []
        for S in S_GRID:
            v = [float(r[key]) for r in main_rows if float(r["S_pre"]) == S and
                 (e is None or float(r["e"]) == e) and (mu is None or float(r["mu"]) == mu)]
            out.append(np.mean(v))
        return np.array(out)
    fig, axs = plt.subplots(1, 3, figsize=(10.5, 3.4), layout="constrained")
    cols = [_COL["blue"], _COL["orange"], _COL["aqua"], _COL["yellow"]]
    for k, e in enumerate(E_GRID):
        axs[0].plot(S_GRID, 1000 * agg(e=e, mu=0.4), color=cols[k], marker="o", ms=4, label=f"e {e}")
        axs[1].plot(S_GRID, 1000 * agg(e=e, mu=0.4, key="w_retained_contact_m"), color=cols[k],
                    marker="o", ms=4, label=f"e {e}")
    for k, mu in enumerate(MU_GRID):
        axs[2].plot(S_GRID, 1000 * agg(e=0.6, mu=mu), color=cols[k], marker="o", ms=4, label=f"mu {mu}")
    axs[0].set_title("all retained (mu 0.4)")
    axs[1].set_title("retained after >= 1 contact (mu 0.4)")
    axs[2].set_title("all retained (e 0.6)")
    for ax in axs:
        ax.set_xlabel("pre-impact backspin S")
        ax.set_ylim(bottom=0)
        ax.grid(True, color=_COL["grid"], lw=0.5)
        ax.legend(frameon=False)
    axs[0].set_ylabel("retained width along the gate (mm),\nmean over descent 64-86 deg")
    fig.suptitle(f"PREDICTED retention width vs spin, v 5 m/s (geometric gate {1000 * gl:.0f} mm); e, mu assumed",
                 color=_COL["ink"])
    fig.savefig(os.path.join(fig_dir, "contact_retention_vs_spin.png"), dpi=150)
    plt.close(fig)
    # ---------------- (3) Part B controlled comparison + decomposition
    comp_rows = []
    for (h, d) in HD_CASES:
        if not os.path.exists(os.path.join(cache, f"B_t30_{h}_{d}_S0.npz")):
            continue
        base, V, TH = _load_case(cache, "t30", h, d, "S0")
        cases = {fk: _load_case(cache, "t30", h, d, fk)[0] for fk in FLIGHT_CASES
                 if os.path.exists(os.path.join(cache, f"B_t30_{h}_{d}_{fk}.npz"))}
        vm = V <= 8.9 + 1e-9
        for ie, e in enumerate(base["e"]):
            for im, mu in enumerate(base["mu"]):
                o0 = base["outcome"][ie, im]
                clean0 = (o0 == O_RC) & vm
                ret0 = np.isin(o0, (O_RC, O_RK)) & vm
                nm0 = _near_miss(clean0) & vm
                for fk, c in cases.items():
                    o = c["outcome"][ie, im]
                    clean = (o == O_RC) & vm
                    ret = np.isin(o, (O_RC, O_RK)) & vm
                    rk = (o == O_RK) & vm
                    ce = c["clean_entry"][ie, im] & vm
                    nm_own = _near_miss(ce | clean) & vm
                    comp_rows.append({
                        "h": h, "d": d, "e": float(e), "mu": float(mu), "case": fk,
                        "n_retained": int(ret.sum()), "n_retained_clean": int(clean.sum()),
                        "n_retained_contact": int(rk.sum()),
                        "n_retained_contact_external": int((rk & c["ext"][ie, im]).sum()),
                        "n_clean_entry": int(ce.sum()),
                        "n_clean_entry_bounced_out": int(((o == O_BO) & ce).sum()),
                        "kept_vs_S0": int((ret & ret0).sum()), "lost_vs_S0": int((~ret & ret0).sum()),
                        "gained_vs_S0": int((ret & ~ret0).sum()),
                        "n_near_miss_own": int(nm_own.sum()),
                        "P_retained_near_miss_own": float(ret[nm_own].mean()) if nm_own.any() else float("nan"),
                        "n_near_miss_S0_set": int(nm0.sum()),
                        "P_retained_in_S0_near_miss_set": float(ret[nm0].mean()) if nm0.any() else float("nan"),
                        "max_square_cells": _max_square(ret),
                        "P_best_tight": _gauss_best(ret, (1.0, 1.0)),
                        "P_best_loose": _gauss_best(ret, (3.0, 3.0)),
                    })
    if not comp_rows:
        print("report: no Part B cache found, skipping Part B summaries", flush=True)
        return summary
    _write_csv(os.path.join(out_dir, "contact_spin_comparison.csv"),
               ["PREDICTED. Part B controlled comparison at identical (v, elevation, h, d) cells, v <= 8.9 m/s"
                " (predicted hood cap), tilt 30, unfavourable side, 2D centre plane. e, mu ASSUMED; aero ASSUMED.",
                "kept/lost/gained_vs_S0 = retained cells compared with the no-spin launch (S0). near-miss set = cells"
                " within 2 grid cells (0.1 m/s / 0.5 deg) of a clean-entry cell that are not clean entries themselves;"
                " *_own uses the case's own clean-entry set, *_S0_set the S0 one (same cells for every case).",
                "S1_nom_airOnly: Magnus flight, spin zeroed at the first HIVE event (airborne contribution); S1_collOnly:"
                " no-Magnus flight (same path as S0), spin carried into the contacts (collision contribution)."
                " P_best_tight / loose = max of the Gaussian-smoothed retained indicator, sigma_v 0.05 / 0.15 m/s,"
                " sigma_elev 0.25 / 0.75 deg (ASSUMED scatter). Cells are 0.05 m/s x 0.25 deg."],
               list(comp_rows[0].keys()), comp_rows)
    summary["comp"] = comp_rows
    hd_have = sorted({(r["h"], r["d"]) for r in comp_rows})
    comps = {"airborne Magnus only": [], "collision spin only": [], "interaction": [], "full S1 (total)": []}
    dec = {}
    for (h, d) in hd_have:
        def n(fk):
            v = [r["n_retained"] for r in comp_rows if r["h"] == h and r["d"] == d and r["case"] == fk]
            return float(np.mean(v)) if v else float("nan")
        b0, full, air, coll = n("S0"), n("S1_nom"), n("S1_nom_airOnly"), n("S1_collOnly")
        comps["airborne Magnus only"].append(air - b0)
        comps["collision spin only"].append(coll - b0)
        comps["interaction"].append(full - air - coll + b0)
        comps["full S1 (total)"].append(full - b0)
        dec[(h, d)] = {"S0": b0, "full": full, "air": air, "coll": coll}
    summary["dec"] = dec
    fig, ax = plt.subplots(figsize=(9, 3.6), layout="constrained")
    x = np.arange(len(hd_have))
    wbar = 0.2
    bcols = [_COL["blue"], _COL["orange"], _COL["violet"], _COL["ink"]]
    for k, (lab, vals) in enumerate(comps.items()):
        ax.bar(x + (k - 1.5) * wbar, vals, width=wbar * 0.9, color=bcols[k], label=lab)
    ax.axhline(0, color=_COL["muted"], lw=0.8)
    ax.set_xticks(x, [f"h {h}\nd {d}" for h, d in hd_have])
    ax.set_ylabel("change in retained cells vs no spin\n(mean over e x mu grid)")
    ax.grid(True, axis="y", color=_COL["grid"], lw=0.5)
    ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.18))
    ax.set_title("PREDICTED decomposition of the S = 1 backspin effect on retention (unfavourable side, "
                 "v <= 8.9 m/s; cell = 0.05 m/s x 0.25 deg)", color=_COL["ink"])
    fig.savefig(os.path.join(fig_dir, "contact_decomposition.png"), dpi=150)
    plt.close(fig)
    h, d = 0.737, 0.90
    if (h, d) in hd_have:
        fig, axs = plt.subplots(1, 2, figsize=(10, 4.0), sharey=True, layout="constrained")
        for ax, fk in zip(axs, ("S0", "S1_nom")):
            c, V, TH = _load_case(cache, "t30", h, d, fk)
            ie = int(np.argmin(np.abs(c["e"] - 0.6)))
            im = int(np.argmin(np.abs(c["mu"] - 0.4)))
            o = c["outcome"][ie, im].astype(int)
            ax.imshow(o.T, origin="lower", aspect="auto", cmap=cmap, vmin=-0.5, vmax=5.5,
                      extent=(V[0, 0] - 0.025, V[-1, 0] + 0.025, TH[0, 0] - 0.125, TH[0, -1] + 0.125),
                      interpolation="nearest")
            ax.axvline(8.9, color=_COL["ink"], lw=0.8, ls="--")
            ax.set_ylim(68, 88)
            ax.set_xlabel("launch speed (m/s); dashed = 8.9 m/s predicted hood cap")
            ax.set_title({"S0": "no spin", "S1_nom": "backspin S = 1, nominal Cl"}[fk], color=_COL["ink"])
        axs[0].set_ylabel("elevation (deg)")
        _outcome_legend(fig)
        fig.suptitle(f"PREDICTED launch outcomes, h {h} m, d {d} m, e 0.6, mu 0.4 (assumed), unfavourable side",
                     color=_COL["ink"])
        fig.savefig(os.path.join(fig_dir, "contact_launch_windows.png"), dpi=150)
        plt.close(fig)
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stage", default="all", choices=("incidence", "launch", "tilt", "report", "all"))
    ap.add_argument("--cache", default=None, help="default .contact_cache_<aero file name>")
    ap.add_argument("--aero-path", default=fl.LIT_PARAMS_PATH,
                    help="aero/ball parameter file (default research/params_lit.json)")
    ap.add_argument("--fast", action="store_true")
    ap.add_argument("--workers", type=int, default=6, help="parallel processes for the launch stages")
    a = ap.parse_args(argv)
    fl.set_aero_path(a.aero_path)      # before any worker pool starts (children inherit it)
    a.cache = a.cache or os.path.join(_ROOT, ".contact_cache_" + fl.aero_tag())
    out_dir = os.path.join(_ROOT, "data")
    if a.stage in ("incidence", "all"):
        t0 = time.time()
        run_incidence(out_dir, fast=a.fast)
        print(f"incidence done {time.time()-t0:.0f}s", flush=True)
    if a.stage in ("launch", "all"):
        t0 = time.time()
        run_launch(out_dir, a.cache, fast=a.fast, workers=a.workers)
        print(f"launch done {time.time()-t0:.0f}s", flush=True)
    if a.stage in ("tilt", "all"):
        # old bounds of the shipped contact_launch_sweep_t*.csv (fz.SWEEP_TILT); derived bounds now
        # fz.TILT_BOUNDS 28.80 / 31.77, re-sweep deferred (PM-015)
        from src import feasibility as fz
        for tilt in fz.SWEEP_TILT:
            tag = f"t{tilt:g}"
            run_launch(out_dir, a.cache, fast=a.fast, hd_cases=((0.737, 0.75), (0.737, 0.90)),
                       flight_cases=["S0", "S1_nom"], tilt=tilt, tag=tag, eg=(0.45, 0.6), mg=(0.4, 0.6), workers=a.workers)
    if a.stage in ("report", "all"):
        run_report(out_dir, os.path.join(_ROOT, "figures"), a.cache)
        print("report done", flush=True)


if __name__ == "__main__":
    main()
