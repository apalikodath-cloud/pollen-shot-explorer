#!/usr/bin/env python
"""Generate viz/shots.json (side-view shot trajectories for the videos and the web replay).

Two backends, chosen automatically (``--mode auto``):

* REAL ("predicted"): used when src/flight.py, src/hive.py, data/hive_geometry.json and
  data/aero_params.json all exist and import cleanly. Each case is integrated with
  ``flight.simulate`` (drag + Magnus + spin decay, params from data/aero_params.json at the
  case's ``aero_set``) and classified with ``hive.classify_detail`` (CAD-derived HIVE).
  Output is PREDICTED with UNCALIBRATED aero; nothing here is a measurement.
* DEMO: self-contained fixed-step RK4 + a deliberately fake placeholder HIVE. Every output
  carries meta.source = "demo" and the renderer stamps
  "DEMO — placeholder geometry, not results" on every frame.

Usage (from the repo root):
    python viz/make_shots.py                              # auto backend, default cases
    python viz/make_shots.py --cases my_cases.json        # your own case list
    python viz/make_shots.py --mode demo                  # force DEMO -> viz/demo/shots.json
    python viz/make_shots.py --sweep-map viz/out/map.csv  # also a coarse release-point sweep

Case file: {"cases": [ {id, title, pose: "pose_pos"|"pose_neg",
    side: "favorable"|"unfavorable" (or shooter side "neg"|"pos"),
    release: [x, z]  (HIVE frame, m; x sign must match the side)  OR  distance + release_z,
    v (m/s), elev_deg, and spin as S (omega R / v at release) OR spin_rpm (+ = backspin),
    aero_set: "low"|"nominal"|"high" (optional, default nominal), t_max (optional)} ]}
See viz/shots.schema.md for the output format.

The flight is cut at the FIRST solid contact (no bounce model here; contact.py is separate),
or after the ball centre has been inside the CELL for 0.3 s / touches the cell interior,
or at the field wall / tile.
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import json
import math
import os
import sys

sys.dont_write_bytecode = True  # never drop __pycache__ into src/ (owned by another team)

import numpy as np

VIZ = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(VIZ)
DT_OUT = 0.002          # s, output sampling interval (500 Hz)
CLEAN_HOLD = 0.30       # s, max time kept after the ball centre enters the CELL
X_WALL_DEFAULT = 1.8009 # m, perimeter wall inner face from field centre line (CAD, see hive_geometry.json field)


# =========================================================================== helpers
def _r(a, nd):
    return [round(float(v), nd) for v in np.asarray(a, float).ravel()]


def _seg_point_dist(p, a, b):
    ab = b - a
    ap = p - a
    den = np.sum(ab * ab, axis=-1)
    t = np.where(den > 0, np.sum(ap * ab, axis=-1) / np.where(den > 0, den, 1.0), 0.0)
    t = np.clip(t, 0.0, 1.0)
    q = a + t[..., None] * ab
    return np.sqrt(np.sum((p - q) ** 2, axis=-1))


def _in_convex(pts, poly):
    poly = np.asarray(poly, float)
    s = []
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        s.append((b[0] - a[0]) * (pts[..., 1] - a[1]) - (b[1] - a[1]) * (pts[..., 0] - a[0]))
    S = np.stack(s, -1)
    return np.all(S >= -1e-12, -1) | np.all(S <= 1e-12, -1)


def _crossing(c, k):
    """Fraction in [0,1] between samples k-1 and k where c crosses 0 (linear)."""
    if k <= 0:
        return 0.0
    a, b = c[k - 1], c[k]
    return float(np.clip(a / (a - b), 0.0, 1.0)) if a != b else 1.0


# =========================================================================== REAL backend
class RealBackend:
    source = "predicted"

    def __init__(self, aero_path=None):
        if ROOT not in sys.path:
            sys.path.insert(0, ROOT)
        from src import flight, hive  # noqa: F401  (import errors -> caller falls back)
        self.flight = flight
        self.hive = hive
        self.geom = hive.load_geometry()
        self.R = float(self.geom["ball_radius"]["value"])
        self.x_wall = float(self.geom.get("field", {}).get("in_plane_extent", {}).get("x_inner_wall", X_WALL_DEFAULT))
        self.aero_path = aero_path  # None = data/aero_params.json; research/params_lit.json for new runs
        self._params = {}

    geometry_status = ("CAD-derived HIVE section from data/hive_geometry.json (official field CAD + "
                       "Manual TU07 9.6; nominal 30 deg tilt, see that file for bounds/open questions)")

    def params(self, aero_set):
        if aero_set not in self._params:
            self._params[aero_set] = self.flight.default_params(aero_set, path=self.aero_path)
        return self._params[aero_set]

    def favorable_side(self, pose):
        return self.geom["poses"][pose]["favorable_side"]

    def hive_payload(self, pose):
        P = self.geom["poses"][pose]
        segs, projected, static = [], [], []
        for ob in P["obstacles"]:
            segs.append([*_r(ob["p0"], 5), *_r(ob["p1"], 5), ob["name"]])
            if ob.get("projected"):
                projected.append(ob["name"])
            if ob.get("body") == "frame_static":
                static.append(ob["name"])
        m = P["mouth"]
        return {
            "pose": pose,
            "tilt_deg": float(P["tilt_deg"]["value"]),
            "pivot": [0.0, float(self.geom["pivot"]["z"])],
            "segments": segs,
            "mouth": [*_r(m["p0"], 5), *_r(m["p1"], 5)],
            "inside": [_r(p, 5) for p in P["inside"]],
            "up_cell": [s[4] for s in segs if s[4].startswith("up_")],
            "projected": projected,
            "static": static,
            "favorable_side": P["favorable_side"],
            "x_wall": self.x_wall,
            "status": "CAD-derived (confirmed nominal tilt 30 deg; see data/hive_geometry.json)",
        }

    def collision(self, pose):
        hv = self.hive.get_hive(pose, mirror=False)
        names = list(hv.names)

        def clear(pts):
            c, j = hv.clearance(pts)
            return c, j
        return clear, hv.is_inside, names

    def simulate(self, pose, shooter_side, x0, z0, vx, vz, spin_rad_s, aero_set, t_max):
        fl = self.flight
        p = self.params(aero_set)
        v0 = np.array([vx, 0.0, vz])
        w0 = fl.backspin_omega(v0, spin_rad_s) if spin_rad_s != 0 else np.zeros(3)
        tr = fl.simulate([x0, 0.0, z0], v0, w0, p, t_max=t_max, dt_max=1e-3, z_ground=self.R)
        det = self.hive.classify_detail(tr, pose, shooter_side, frame="hive")
        tg = np.arange(0.0, tr.t[-1], DT_OUT)
        if tg[-1] < tr.t[-1]:
            tg = np.append(tg, tr.t[-1])
        Y = np.asarray(tr.sol(tg)) if tr.sol is not None else np.array(
            [np.interp(tg, tr.t, c) for c in np.hstack([tr.pos, tr.vel, tr.omega]).T])
        FM = np.zeros((len(tg), 2))
        FD = np.zeros((len(tg), 2))
        S = np.zeros(len(tg))
        for i in range(len(tg)):
            f = fl.aero_forces(Y[3:6, i], Y[6:9, i], p)
            FM[i] = f["F_magnus"][[0, 2]]
            FD[i] = f["F_drag"][[0, 2]]
            S[i] = f["S"]
        apex = tr.apex()
        return {
            "t": tg, "x": Y[0], "z": Y[2], "vx": Y[3], "vz": Y[5], "wy": Y[7],
            "FM": FM, "FD": FD, "S": S, "outcome": det["result"],
            "entry_angle_deg": det.get("entry_angle_deg"), "min_clearance": det.get("min_clearance"),
            "reversal": bool(fl.horizontal_reversal(tr)),
            "apex": None if apex is None else {
                "t": apex["t"], "x": apex["x"], "z": apex["z"], "vx": apex["vx"], "vz": apex["vz"],
                "spin_rpm": apex["spin_rpm"], "S": apex["S"],
                "F_M": [float(apex["F_M"][0]), float(apex["F_M"][2])]},
            "mass": float(p["mass"]),
            "aero_desc": f"Cd={p['Cd']}, Cl=min(c1*S,Cl_max) with (c1,Cl_max)={tuple(p['Cl']) if p.get('Cl') is not None else None}, "
                         f"spin decay k={p.get('spin_decay_k', 0)} 1/s",
        }

    def outcome_only(self, pose, shooter_side, x0, z0, vx, vz, spin_rad_s, aero_set):
        fl = self.flight
        p = self.params(aero_set)
        v0 = np.array([vx, 0.0, vz])
        w0 = fl.backspin_omega(v0, spin_rad_s) if spin_rad_s != 0 else np.zeros(3)
        tr = fl.simulate([x0, 0.0, z0], v0, w0, p, t_max=3.0, dt_max=5e-3, z_ground=self.R,
                         rtol=1e-7, atol=1e-9, dense=False)
        return self.hive.classify(tr, pose, shooter_side, frame="hive")


# =========================================================================== DEMO backend
class DemoBackend:
    """Self-contained stand-in. Geometry and coefficients are FAKE placeholders."""
    source = "demo"
    geometry_status = "PLACEHOLDER geometry (invented tilted box cups, NOT the official HIVE)"
    R = 0.0355
    x_wall = X_WALL_DEFAULT
    PIVOT_Z = 1.10     # placeholder
    TILT = 30.0        # placeholder
    AERO = {"low": (0.40, 0.15, 0.10, 0.01), "nominal": (0.50, 0.35, 0.25, 0.05),
            "high": (0.60, 0.80, 0.40, 0.30)}   # (Cd, c1, Cl_max, k) placeholders
    RHO, MASS = 1.225, 0.025

    def favorable_side(self, pose):
        return "pos" if pose == "pose_pos" else "neg"

    def _segments(self, pose):
        sp = 1.0 if pose == "pose_pos" else -1.0
        t = math.radians(self.TILT)
        segs = []

        def cup(prefix, tilt, side_sign):
            c, s = math.cos(tilt), math.sin(tilt)

            def w(u, v):
                return [side_sign * (u * c - v * s), self.PIVOT_Z + u * s + v * c]
            pts = {"floor": (w(0.08, 0.0), w(0.42, 0.0)), "back_wall": (w(0.08, 0.0), w(0.08, 0.30)),
                   "roof": (w(0.08, 0.30), w(0.36, 0.30))}
            for k, (a, b) in pts.items():
                segs.append([*_r(a, 5), *_r(b, 5), f"{prefix}_{k}"])
            return w
        wu = cup("up", t, sp)
        cup("down", -t, -sp)
        segs.append([0.0, 0.0, 0.0, self.PIVOT_Z - 0.05, "post"])
        mouth = [*_r(wu(0.42, 0.0), 5), *_r(wu(0.36, 0.30), 5)]
        R = self.R
        inside = [_r(wu(0.08 + R, R), 5), _r(wu(0.40, R), 5), _r(wu(0.36, 0.30 - R), 5), _r(wu(0.08 + R, 0.30 - R), 5)]
        return segs, mouth, inside

    def hive_payload(self, pose):
        segs, mouth, inside = self._segments(pose)
        return {"pose": pose, "tilt_deg": self.TILT, "pivot": [0.0, self.PIVOT_Z], "segments": segs,
                "mouth": mouth, "inside": inside, "up_cell": [s[4] for s in segs if s[4].startswith("up_")],
                "projected": [], "static": ["post"], "favorable_side": self.favorable_side(pose),
                "x_wall": self.x_wall, "status": "PLACEHOLDER (demo)"}

    def collision(self, pose):
        segs, mouth, inside = self._segments(pose)
        P0 = np.array([[s[0], s[1]] for s in segs])
        P1 = np.array([[s[2], s[3]] for s in segs])
        names = [s[4] for s in segs]
        R = self.R

        def clear(pts):
            pts = np.asarray(pts, float)
            D = _seg_point_dist(pts[..., None, :], P0, P1)
            j = np.argmin(D, -1)
            return np.take_along_axis(D, j[..., None], -1)[..., 0] - R, j
        return clear, (lambda pts: _in_convex(np.asarray(pts, float), inside)), names

    def _rk4(self, x0, z0, vx, vz, wy, aero_set, t_max, dt=5e-4):
        Cd, c1, clmax, k = self.AERO[aero_set]
        q = 0.5 * self.RHO * math.pi * self.R ** 2 / self.MASS

        def f(s):
            x, z, ux, uz, w = s
            v = math.hypot(ux, uz)
            S = abs(w) * self.R / max(v, 1e-6)
            cl = min(c1 * S, clmax)
            sg = 0.0 if w == 0 else math.copysign(1.0, w)
            ax = -q * Cd * v * ux + q * cl * v * sg * uz
            az = -9.80665 - q * Cd * v * uz - q * cl * v * sg * ux
            return np.array([ux, uz, ax, az, -k * w])
        s = np.array([x0, z0, vx, vz, wy], float)
        out = [s.copy()]
        n = int(t_max / dt)
        for _ in range(n):
            k1 = f(s); k2 = f(s + 0.5 * dt * k1); k3 = f(s + 0.5 * dt * k2); k4 = f(s + dt * k3)
            s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
            out.append(s.copy())
            if s[1] < self.R:
                break
        A = np.array(out)
        t = np.arange(len(A)) * dt
        return t, A, (Cd, c1, clmax, k, q)

    def _classify(self, pose, x, z):
        clear, inside, names = self.collision(pose)
        pts = np.column_stack([x, z])
        c, j = clear(pts)
        ins = inside(pts)
        kh = np.nonzero(c < 0)[0]
        ki = np.nonzero(ins)[0]
        if kh.size and (not ki.size or kh[0] < ki[0]):
            return f"hit:{names[j[kh[0]]]}"
        return "clean" if ki.size else "miss"

    def simulate(self, pose, shooter_side, x0, z0, vx, vz, spin_rad_s, aero_set, t_max):
        wy = -math.copysign(spin_rad_s, vx)  # backspin: +x travel -> omega along -y
        t, A, (Cd, c1, clmax, k, q) = self._rk4(x0, z0, vx, vz, wy, aero_set, t_max)
        step = int(round(DT_OUT / (t[1] - t[0])))
        idx = np.arange(0, len(t), step)
        if idx[-1] != len(t) - 1:
            idx = np.append(idx, len(t) - 1)
        t, A = t[idx], A[idx]
        x, z, ux, uz, w = A.T
        v = np.hypot(ux, uz)
        S = np.abs(w) * self.R / np.maximum(v, 1e-6)
        cl = np.minimum(c1 * S, clmax)
        sg = np.sign(w)
        FM = self.MASS * np.column_stack([q * cl * v * sg * uz, -q * cl * v * sg * ux])
        FD = self.MASS * np.column_stack([-q * Cd * v * ux, -q * Cd * v * uz])
        out = self._classify(pose, x, z)
        ia = np.nonzero((uz[:-1] > 0) & (uz[1:] <= 0))[0]
        apex = None
        if ia.size:
            i = int(ia[0])
            apex = {"t": t[i], "x": x[i], "z": z[i], "vx": ux[i], "vz": uz[i],
                    "spin_rpm": abs(w[i]) * 60 / (2 * math.pi), "S": S[i], "F_M": FM[i].tolist()}
        return {"t": t, "x": x, "z": z, "vx": ux, "vz": uz, "wy": w, "FM": FM, "FD": FD, "S": S,
                "outcome": out, "entry_angle_deg": None, "min_clearance": None,
                "reversal": bool(np.any(np.sign(ux) * np.sign(vx) < 0)), "apex": apex,
                "mass": self.MASS,
                "aero_desc": f"DEMO placeholders Cd={Cd}, Cl=min({c1}*S,{clmax}), k={k} 1/s"}

    def outcome_only(self, pose, shooter_side, x0, z0, vx, vz, spin_rad_s, aero_set):
        wy = -math.copysign(spin_rad_s, vx)
        t, A, _ = self._rk4(x0, z0, vx, vz, wy, aero_set, 3.0, dt=2e-3)
        return self._classify(pose, A[:, 0], A[:, 1])


DEMO_CASES = [
    {"id": "D1_unfav_spin", "title": "DEMO: unfavourable side, backspin vs no spin", "pose": "pose_pos",
     "side": "unfavorable", "release": [-1.2, 0.40], "v": 7.0, "elev_deg": 75, "S": 1.0, "aero_set": "high"},
    {"id": "D2_fav_spin", "title": "DEMO: favourable side lob", "pose": "pose_pos", "side": "favorable",
     "release": [1.4, 0.40], "v": 6.5, "elev_deg": 51, "S": 1.0, "aero_set": "high"},
    {"id": "D3_other_pose", "title": "DEMO: other HIVE pose", "pose": "pose_neg", "side": "unfavorable",
     "release": [1.2, 0.40], "v": 7.0, "elev_deg": 78, "S": 1.0, "aero_set": "high"},
]


# =========================================================================== shared pipeline
def resolve_case(case, be):
    pose = case["pose"]
    fav = be.favorable_side(pose)
    other = "pos" if fav == "neg" else "neg"
    side = case.get("side", "unfavorable")
    if side in ("neg", "pos"):
        shooter = side
        side_label = "favorable" if side == fav else "unfavorable"
    elif side in ("favorable", "unfavorable"):
        shooter = fav if side == "favorable" else other
        side_label = side
    else:
        raise ValueError(f"case {case.get('id')}: side must be favorable/unfavorable/neg/pos")
    sgn = -1.0 if shooter == "neg" else 1.0   # shooter x sign; fires toward -sgn
    if "release" in case:
        x0, z0 = float(case["release"][0]), float(case["release"][1])
        if x0 * sgn <= 0:
            raise ValueError(f"case {case.get('id')}: release x={x0} is not on the {shooter} side")
    else:
        x0, z0 = sgn * abs(float(case["distance"])), float(case.get("release_z", 0.40))
    v = float(case["v"])
    el = float(case["elev_deg"])
    R = be.R
    if "spin_rpm" in case:
        spin = float(case["spin_rpm"]) * 2 * math.pi / 60
    else:
        spin = float(case.get("S", 0.0)) * v / R
    vx, vz = -sgn * v * math.cos(math.radians(el)), v * math.sin(math.radians(el))
    return dict(pose=pose, shooter=shooter, side=side_label, x0=x0, z0=z0, v=v, el=el, spin=spin,
                S=spin * R / v, vx=vx, vz=vz, aero_set=case.get("aero_set", "nominal"),
                t_max=float(case.get("t_max", 3.0)))


def truncate(sim, outcome, collision, x_wall, R):
    """Cut the sampled flight at the first contact / CELL retention / wall (linear refine)."""
    clear, inside, names = collision
    pts = np.column_stack([sim["x"], sim["z"]])
    c, _ = clear(pts)
    ins = inside(pts)
    n = len(pts)
    end, frac, note = n - 1, 1.0, "flight ends at tile height (ball centre at z = R)"
    if outcome.startswith("hit"):
        k = np.nonzero(c < 0)[0]
        if k.size:
            end, frac = int(k[0]), _crossing(c, int(k[0]))
        note = f"stops at first contact with {outcome[4:]} (no bounce model)"
    elif outcome == "clean":
        ki = np.nonzero(ins)[0]
        if ki.size:
            k0 = int(ki[0])
            kc = np.nonzero(c[k0:] < 0)[0]
            kmax = min(n - 1, k0 + int(round(CLEAN_HOLD / DT_OUT)))
            if kc.size and k0 + kc[0] <= kmax:
                end, frac = k0 + int(kc[0]), _crossing(c, k0 + int(kc[0]))
                note = "inside CELL; stops at first interior contact (retention ASSUMED, no bounce model)"
            else:
                end, frac = kmax, 1.0
                note = "inside CELL; shown for 0.3 s after entry (retention ASSUMED)"
    else:
        kw = np.nonzero(np.abs(sim["x"]) > x_wall - R)[0]
        if kw.size:
            end, frac = int(kw[0]), 1.0
            note = "reaches the field perimeter wall"
    out = {}
    for key, arr in sim.items():
        if isinstance(arr, np.ndarray) and arr.shape[:1] == (n,):
            a = arr[: end + 1].copy()
            if end >= 1 and frac < 1.0:
                a[-1] = arr[end - 1] + frac * (arr[end] - arr[end - 1])
            out[key] = a
        else:
            out[key] = arr
    out["end_note"] = note
    return out


def spin_angle(t, wy):
    """CCW rotation angle (rad) of the ball as seen in the x-z view (x right, z up, y into page).
    omega along -y is CCW in this view, so angle = -integral(omega_y dt)."""
    a = np.zeros_like(t)
    a[1:] = -np.cumsum(0.5 * (wy[1:] + wy[:-1]) * np.diff(t))
    return a


def _reversed(vx):
    """True if the horizontal velocity changes sign during the drawn flight (mid-air reversal)."""
    vx = np.asarray(vx, float)
    return bool(len(vx) > 1 and np.any(np.sign(vx[1:]) * np.sign(vx[0]) < 0))


def build_shot(case, be):
    rc = resolve_case(case, be)
    col = be.collision(rc["pose"])
    sim = be.simulate(rc["pose"], rc["shooter"], rc["x0"], rc["z0"], rc["vx"], rc["vz"], rc["spin"],
                      rc["aero_set"], rc["t_max"])
    tw = be.simulate(rc["pose"], rc["shooter"], rc["x0"], rc["z0"], rc["vx"], rc["vz"], 0.0,
                     rc["aero_set"], rc["t_max"])
    s = truncate(sim, sim["outcome"], col, be.x_wall, be.R)
    w = truncate(tw, tw["outcome"], col, be.x_wall, be.R)
    rpm = np.abs(s["wy"]) * 60 / (2 * math.pi)
    apex = sim["apex"]
    if apex is not None:
        apex = {k: (round(float(v), 5) if not isinstance(v, (list, tuple)) else _r(v, 6)) for k, v in apex.items()}
    shot = {
        "id": case.get("id", f"shot{id(case)}"),
        "title": case.get("title", ""),
        "pose": rc["pose"],
        "side": rc["side"],
        "shooter_side": rc["shooter"],
        "release": [round(rc["x0"], 4), round(rc["z0"], 4)],
        "v": round(rc["v"], 4),
        "elev_deg": round(rc["el"], 3),
        "spin_rpm": round(rc["spin"] * 60 / (2 * math.pi), 1),
        "S": round(rc["S"], 4),
        "aero_set": rc["aero_set"],
        "aero_desc": sim["aero_desc"],
        "mass": sim["mass"],
        "radius": be.R,
        "outcome": sim["outcome"],
        "end_note": s["end_note"],
        "entry_angle_deg": None if sim["entry_angle_deg"] is None else round(sim["entry_angle_deg"], 2),
        "min_clearance": None if sim["min_clearance"] is None else round(sim["min_clearance"], 5),
        # reversal judged only over the drawn (truncated) flight; full-integration flag kept for reference
        "horizontal_reversal": _reversed(s["vx"]),
        "horizontal_reversal_untruncated": sim["reversal"],
        "apex": apex,
        "apex_reached": bool(apex is not None and apex["t"] <= float(s["t"][-1]) + 1e-9),
        "t": _r(s["t"], 4), "x": _r(s["x"], 5), "z": _r(s["z"], 5),
        "vx": _r(s["vx"], 4), "vz": _r(s["vz"], 4),
        "spin_angle": _r(spin_angle(s["t"], s["wy"]), 4),
        "spin_rpm_t": _r(rpm, 1), "S_t": _r(s["S"], 4),
        "FMx": _r(s["FM"][:, 0], 6), "FMz": _r(s["FM"][:, 1], 6),
        "FDx": _r(s["FD"][:, 0], 6), "FDz": _r(s["FD"][:, 1], 6),
        "twin_no_spin": {"t": _r(w["t"], 4), "x": _r(w["x"], 5), "z": _r(w["z"], 5),
                         "outcome": tw["outcome"], "end_note": w["end_note"],
                         "horizontal_reversal": _reversed(w["vx"])},
    }
    return shot


def load_backend(mode, aero_path=None):
    if mode in ("auto", "real"):
        need = [os.path.join(ROOT, p) for p in ("src/flight.py", "src/hive.py",
                                                 "data/hive_geometry.json", "data/aero_params.json")]
        missing = [p for p in need if not os.path.exists(p)]
        if not missing:
            try:
                return RealBackend(aero_path)
            except Exception as exc:  # module mid-edit by another agent, etc.
                if mode == "real":
                    raise
                print(f"[make_shots] real backend failed to import ({exc!r}); using DEMO", file=sys.stderr)
        elif mode == "real":
            raise FileNotFoundError(f"real backend missing: {missing}")
        else:
            print(f"[make_shots] missing {missing}; using DEMO", file=sys.stderr)
    return DemoBackend()


def sweep_map(be, path, pose, side, release_z, distances, elevs, speeds, S_list, aero_set):
    """Coarse release-point sweep -> CSV (one row per launch). For the field-map still only;
    the real feasibility analysis is src/feasibility.py."""
    rows = []
    for d in distances:
        for z0 in release_z:
            for v in speeds:
                for el in elevs:
                    for S in S_list:
                        case = {"pose": pose, "side": side, "distance": d, "release_z": z0, "v": v,
                                "elev_deg": el, "S": S, "aero_set": aero_set}
                        rc = resolve_case(case, be)
                        out = be.outcome_only(rc["pose"], rc["shooter"], rc["x0"], rc["z0"], rc["vx"],
                                              rc["vz"], rc["spin"], aero_set)
                        rows.append({"source": be.source, "pose": pose, "side": rc["side"],
                                     "release_x": round(rc["x0"], 4), "release_z": z0, "v": v,
                                     "elev_deg": el, "S": S, "spin_rpm": round(rc["spin"] * 30 / math.pi, 1),
                                     "aero_set": aero_set, "outcome": out})
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)
    print(f"[make_shots] wrote {path} ({len(rows)} rows)")


def _frange(spec):
    a, b, s = (float(x) for x in spec.split(":"))
    return [round(v, 6) for v in np.arange(a, b + 1e-9, s)]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cases", help="JSON case file (default: viz/cases_default.json, or built-in DEMO cases)")
    ap.add_argument("--mode", choices=["auto", "real", "demo"], default="auto")
    ap.add_argument("--out", help="output shots JSON (default viz/shots.json; DEMO: viz/demo/shots.json)")
    ap.add_argument("--sweep-map", metavar="CSV", help="also write a coarse release-point sweep CSV")
    ap.add_argument("--sweep-pose", default="pose_pos")
    ap.add_argument("--sweep-side", default="unfavorable")
    ap.add_argument("--sweep-z", default="0.25:0.65:0.2", help="release heights a:b:step (m, ASSUMED)")
    ap.add_argument("--sweep-d", default="0.6:1.7:0.1", help="distances from pivot a:b:step (m)")
    ap.add_argument("--sweep-elev", default="44:88:4")
    ap.add_argument("--sweep-v", default="6:9:0.5")
    ap.add_argument("--sweep-S", default="0,1")
    ap.add_argument("--sweep-aero", default="nominal")
    ap.add_argument("--aero-path", help="aero params JSON for the real backend (default data/aero_params.json; "
                    "research/params_lit.json = literature-graded set used by src/shooter_spec.py)")
    a = ap.parse_args(argv)

    be = load_backend(a.mode, a.aero_path and os.path.abspath(a.aero_path))
    demo = be.source == "demo"
    if a.cases:
        with open(a.cases, encoding="utf-8") as fh:
            raw = json.load(fh)
        cases = raw["cases"] if isinstance(raw, dict) else raw
    elif demo:
        cases = DEMO_CASES
    else:
        with open(os.path.join(VIZ, "cases_default.json"), encoding="utf-8") as fh:
            cases = json.load(fh)["cases"]
    out = a.out or os.path.join(VIZ, "demo" if demo else "", "shots.json")

    shots = []
    for c in cases:
        sh = build_shot(c, be)
        shots.append(sh)
        print(f"[make_shots] {sh['id']}: {sh['side']} {sh['pose']} v={sh['v']} el={sh['elev_deg']} "
              f"spin={sh['spin_rpm']} rpm (S={sh['S']}) -> {sh['outcome']}; no-spin twin -> "
              f"{sh['twin_no_spin']['outcome']}")
    poses = sorted({s["pose"] for s in shots} | {"pose_pos", "pose_neg"})
    hives = {p: be.hive_payload(p) for p in poses}
    first = shots[0]["pose"] if shots else "pose_pos"
    sets = sorted({s["aero_set"] for s in shots})
    doc = {
        "meta": {
            "source": be.source,
            "aero_set": sets[0] if len(sets) == 1 else sets,
            "geometry_status": be.geometry_status,
            "generated": _dt.datetime.now().isoformat(timespec="seconds"),
            "generator": "viz/make_shots.py (" + ("DEMO RK4 + placeholder HIVE" if demo else
                                                  "src/flight.simulate + src/hive.classify_detail") + ")",
            "units": "SI: m, s, m/s, N, rad; spin_rpm in rev/min; HIVE frame (x tipping plane, z up)",
            "notes": ("DEMO — placeholder geometry, not results. Invented HIVE and coefficients; for "
                      "checking the video pipeline only." if demo else
                      "PREDICTED, uncalibrated aero: Cd/Cl/spin-decay are literature-bounded assumptions "
                      f"({os.path.relpath(a.aero_path, ROOT) if a.aero_path else 'data/aero_params.json'}), "
                      "not POLLEN measurements. Geometry is CAD-derived. Release "
                      "heights in the default cases are ASSUMED. Flight is cut at the first solid contact "
                      "(no bounce/rim model); 'clean' means the ball centre reached the CELL interior "
                      "polygon without touching anything; retention after entry is ASSUMED."),
            "labels": {"trajectories": "demo" if demo else "predicted",
                       "geometry": "demo-placeholder" if demo else "derived from confirmed CAD/manual",
                       "release_points_and_launch_states": "assumed (chosen cases)",
                       "aero_coefficients": "demo-placeholder" if demo else "assumed, uncalibrated bounds"},
            "dt_out": DT_OUT,
        },
        "hive": hives[first],
        "hives": hives,
        "shots": shots,
    }
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, separators=(",", ":"))
    print(f"[make_shots] wrote {out} ({os.path.getsize(out) / 1e6:.2f} MB, source={be.source})")

    if a.sweep_map:
        sweep_map(be, a.sweep_map, a.sweep_pose, a.sweep_side, _frange(a.sweep_z), _frange(a.sweep_d),
                  _frange(a.sweep_elev), _frange(a.sweep_v), [float(s) for s in a.sweep_S.split(",")],
                  a.sweep_aero)
    return 0


if __name__ == "__main__":
    sys.exit(main())
