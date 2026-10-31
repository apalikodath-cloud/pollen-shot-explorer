"""HIVE collision geometry and clean (air-only) entry classification.

HANDOFF sections 3 (Q1-Q3), 4E channel 1; contract: docs/INTERFACES.md ("src/hive.py").

Frames
------
HIVE frame (INTERFACES): origin on the tile below the pivot axis, x horizontal in the
tipping plane (+x toward the AUDIENCE), z up, y along the pivot axis.
Shot frame (flight.py convention "x toward the target"): the shooter always fires toward +x.
  * shooter on the "neg" side (x < 0) fires toward +x  -> shot frame == HIVE frame;
  * shooter on the "pos" side (x > 0) fires toward -x  -> shot frame = HIVE frame mirrored
    (x -> -x). The solver mirrors the geometry instead of the trajectory.
  ``classify(..., frame="auto")`` decides from the launch direction: a "pos"-side trajectory
  whose initial vx > 0 is taken to be in the shot frame and is checked against the mirrored
  HIVE; one with vx < 0 is taken to be in the HIVE frame already.

Collision model (configuration space)
-------------------------------------
Every obstacle in data/hive_geometry.json is a solid 2D segment in the tipping-plane
section at the HIVE centre plane s = 0. The ball CENTRE collides with obstacle j when its
distance to segment j is < R (segment inflated by R, rounded end caps included because the
point-to-segment distance is used). ``clearance = distance - R``.

Outcome of a path (ordered in time along the polyline of ball-centre positions):
  "clean"       ball centre enters the ``inside`` polygon (behind the mouth plane, >= R
                from floor/roof/back wall) before any clearance < 0;
  "hit:<name>"  first contact with obstacle <name> (clearance < 0) before entry;
  "miss"        neither (e.g. lands on the field or flies past).
The inside criterion is ASSUMED (from the geometry file); bounce-outs belong to contact.py.

Legs flagged ``projected: true`` (A-frame legs drawn in projection; at s = 0 only their top
exists) are IGNORED by default (centred shots); ``include_projected=True`` treats them as
solid (conservative).

Re-posing: ``Hive(pose, tilt_deg=..., pivot_z=..., lateral_offset=...)`` rebuilds the rotating
body from ``body_local`` (cell-local u, w frame): x = s_pose*(u cos t - w sin t),
z = z_pivot + u sin t + w cos t. Static A-frame segments are taken from the pose's list.
``lateral_offset`` (|s| in m, s = 0 centre plane) lowers the roof segments by the pentagon
profile h(s) = 0.3556 - (0.3556 - 0.1933)|s|/0.254 (confirmed Fig 9-11) - a 2D proxy for an
off-centre shot; side walls are NOT modelled (3D work).
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from typing import Any, Optional, Sequence

import numpy as np

__all__ = ["GEOMETRY_PATH", "load_geometry", "Hive", "CSpaceRaster", "get_hive", "classify",
           "classify_detail", "is_favorable", "seg_point_dist", "seg_seg_dist"]

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEOMETRY_PATH = os.path.join(_ROOT, "data", "hive_geometry.json")

_GEOM_CACHE: dict[str, dict] = {}


def load_geometry(path: Optional[str] = None) -> dict:
    """Load (and cache) data/hive_geometry.json."""
    path = os.path.abspath(path or GEOMETRY_PATH)
    if path not in _GEOM_CACHE:
        with open(path, "r", encoding="utf-8") as fh:
            _GEOM_CACHE[path] = json.load(fh)
    return _GEOM_CACHE[path]


# --------------------------------------------------------------------------- distance kernels
def seg_point_dist(p: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Distance from points p (..., 2) to segments a->b (broadcastable (..., 2))."""
    ab = b - a
    ap = p - a
    den = np.sum(ab * ab, axis=-1)
    t = np.where(den > 0.0, np.sum(ap * ab, axis=-1) / np.where(den > 0.0, den, 1.0), 0.0)
    t = np.clip(t, 0.0, 1.0)
    q = a + t[..., None] * ab
    return np.sqrt(np.sum((p - q) ** 2, axis=-1))


def _cross2(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    return u[..., 0] * v[..., 1] - u[..., 1] * v[..., 0]


def seg_seg_dist(p0: np.ndarray, p1: np.ndarray, q0: np.ndarray, q1: np.ndarray) -> np.ndarray:
    """Exact minimum distance between 2D segments p0-p1 and q0-q1 (broadcast over leading dims)."""
    d = np.minimum.reduce([seg_point_dist(p0, q0, q1), seg_point_dist(p1, q0, q1),
                           seg_point_dist(q0, p0, p1), seg_point_dist(q1, p0, p1)])
    r = p1 - p0
    s = q1 - q0
    den = _cross2(r, s)
    qp = q0 - p0
    ok = np.abs(den) > 1e-15
    dd = np.where(ok, den, 1.0)
    t = _cross2(qp, s) / dd
    u = _cross2(qp, r) / dd
    inter = ok & (t >= 0.0) & (t <= 1.0) & (u >= 0.0) & (u <= 1.0)
    return np.where(inter, 0.0, d)


def _points_in_convex(pts: np.ndarray, poly: np.ndarray) -> np.ndarray:
    """Points (..., 2) strictly inside / on a convex polygon (either orientation)."""
    n = len(poly)
    signs = []
    for i in range(n):
        a = poly[i]
        b = poly[(i + 1) % n]
        signs.append(_cross2(b - a, pts - a))
    S = np.stack(signs, axis=-1)
    return np.all(S >= -1e-12, axis=-1) | np.all(S <= 1e-12, axis=-1)


# --------------------------------------------------------------------------- HIVE geometry
_ROOF_NAMES = ("up_roof_outer", "up_upper_lip", "up_roof_inner",
               "down_roof_outer", "down_upper_lip", "down_roof_inner")


@dataclass
class Hive:
    """Solid HIVE section for one pose in a given frame (see module docstring)."""
    pose: str
    names: list
    P0: np.ndarray            # (n, 2) segment starts (x, z)
    P1: np.ndarray            # (n, 2) segment ends
    body: list                # "hive_rotating" | "frame_static"
    mouth: np.ndarray         # (2, 2): [lower lip, upper lip]
    normal_out: np.ndarray    # (2,) outward mouth normal
    inside: np.ndarray        # (k, 2) convex polygon of retained ball-centre positions
    R: float
    tilt_deg: float
    pivot_z: float
    favorable_side: str
    mirrored_frame: bool = False
    lateral_offset: float = 0.0
    include_projected: bool = False

    # ---- construction
    @classmethod
    def from_json(cls, pose: str = "pose_pos", tilt_deg: Optional[float] = None,
                  pivot_z: Optional[float] = None, include_projected: bool = False,
                  lateral_offset: float = 0.0, ball_radius: Optional[float] = None,
                  path: Optional[str] = None, roof_clearance: bool = False) -> "Hive":
        """roof_clearance (default False = unchanged): a sphere under the laterally sloped pentagon
        roof (slope k = (h0 - h_wall) / half-width, about 32.6 deg) needs a vertical gap R sqrt(1 + k^2),
        not R. True lowers the roof segments and the inside top by R (sqrt(1 + k^2) - 1) = 0.00663 m
        (derived; research/GEOMETRY_AUDIT.md fix 3). It assumes a sharp roof apex (audit U3). The
        3D cell (src/cell3d.py, physics.js buildCell3D) already includes it; this option is for the
        section model only."""
        g = load_geometry(path)
        if pose not in g["poses"]:
            raise KeyError(f"unknown pose {pose!r}")
        P = g["poses"][pose]
        R = float(ball_radius if ball_radius is not None else g["ball_radius"]["value"])
        t_nom = float(P["tilt_deg"]["value"])
        z_nom = float(g["pivot"]["z"])
        tilt = t_nom if tilt_deg is None else float(tilt_deg)
        zp = z_nom if pivot_z is None else float(pivot_z)
        extra = cls.roof_clearance_drop(g, R) if roof_clearance else 0.0
        repose = (abs(tilt - t_nom) > 1e-12) or (abs(zp - z_nom) > 1e-12) or lateral_offset != 0.0 or extra > 0.0
        sp = 1.0 if pose == "pose_pos" else -1.0
        names, P0, P1, body = [], [], [], []
        if repose:
            bl = g["body_local"]
            t = math.radians(tilt)
            ct, st = math.cos(t), math.sin(t)
            dw = cls._roof_drop(g, lateral_offset)

            def world(uw):
                u, w = uw
                return [sp * (u * ct - w * st), zp + u * st + w * ct]

            for seg in bl["segments"]:
                a = list(seg["p0"])
                b = list(seg["p1"])
                if seg["name"] in _ROOF_NAMES:
                    a[1] -= dw + extra
                    b[1] -= dw + extra
                names.append(seg["name"])
                P0.append(world(a))
                P1.append(world(b))
                body.append("hive_rotating")
            for ob in P["obstacles"]:
                if ob.get("body") == "frame_static":
                    if ob.get("projected") and not include_projected:
                        continue
                    names.append(ob["name"])
                    P0.append(list(ob["p0"]))
                    P1.append(list(ob["p1"]))
                    body.append("frame_static")
            ml = bl["mouth_local"]
            m0 = list(ml["p0"])
            m1 = [ml["p1"][0], ml["p1"][1] - dw]
            mouth = np.array([world(m0), world(m1)])
            # inside polygon in cell-local coordinates: back wall + R .. mouth, floor + R .. roof - R
            segs = {s["name"]: s for s in bl["segments"]}
            u_back = segs["up_back_wall"]["p0"][0] + R
            u_mouth = ml["p0"][0]
            w_floor = segs["up_floor"]["p0"][1] + R
            w_roof = segs["up_roof_inner"]["p0"][1] - dw - extra - R
            inside = np.array([world([u_back, w_floor]), world([u_mouth, w_floor]),
                               world([u_mouth, w_roof]), world([u_back, w_roof])])
            normal = np.array([sp * ct, st])
        else:
            for ob in P["obstacles"]:
                if ob.get("projected") and not include_projected:
                    continue
                names.append(ob["name"])
                P0.append(list(ob["p0"]))
                P1.append(list(ob["p1"]))
                body.append(ob.get("body", "hive_rotating"))
            mouth = np.array([P["mouth"]["p0"], P["mouth"]["p1"]], dtype=float)
            normal = np.array(P["mouth"]["normal_out"], dtype=float)
            inside = np.array(P["inside"], dtype=float)
            if ball_radius is not None and abs(R - float(g["ball_radius"]["value"])) > 1e-12:
                # rebuild inside for a different R from body_local (same nominal pose)
                h = cls.from_json(pose, tilt_deg=t_nom + 1e-9, pivot_z=zp,
                                  include_projected=include_projected, ball_radius=R, path=path)
                inside = h.inside
        return cls(pose=pose, names=names, P0=np.array(P0, float), P1=np.array(P1, float),
                   body=body, mouth=mouth, normal_out=normal / np.linalg.norm(normal),
                   inside=inside, R=R, tilt_deg=tilt, pivot_z=zp,
                   favorable_side=P["favorable_side"], lateral_offset=float(lateral_offset),
                   include_projected=include_projected)

    @staticmethod
    def roof_clearance_drop(g: dict, R: float) -> float:
        """Extra roof lowering R (sqrt(1 + k^2) - 1) for a sphere under the sloped roof (derived)."""
        prof = g["y_extent"]["opening_profile"]
        k = (float(prof["height_above_floor_at_s0"]) - float(prof["height_above_floor_at_wall"]))             / float(prof["half_width"])
        return float(R) * (math.sqrt(1.0 + k * k) - 1.0)

    @staticmethod
    def _roof_drop(g: dict, lateral_offset: float) -> float:
        """Roof lowering (m) at lateral offset |s| from the pentagon profile (Fig 9-11)."""
        if lateral_offset == 0.0:
            return 0.0
        prof = g["y_extent"]["opening_profile"]
        h0 = float(prof["height_above_floor_at_s0"])
        hw = float(prof["height_above_floor_at_wall"])
        half = float(prof["half_width"])
        s = min(abs(float(lateral_offset)), half)
        return (h0 - hw) * s / half

    def mirrored(self) -> "Hive":
        """Same HIVE seen in the x -> -x mirrored frame (used for 'pos'-side shooters)."""
        M = np.array([-1.0, 1.0])
        return Hive(pose=self.pose, names=list(self.names), P0=self.P0 * M, P1=self.P1 * M,
                    body=list(self.body), mouth=self.mouth * M, normal_out=self.normal_out * M,
                    inside=self.inside * M, R=self.R, tilt_deg=self.tilt_deg,
                    pivot_z=self.pivot_z, favorable_side=self.favorable_side,
                    mirrored_frame=not self.mirrored_frame, lateral_offset=self.lateral_offset,
                    include_projected=self.include_projected)

    # ---- queries
    @property
    def gate(self) -> np.ndarray:
        """Ball-centre entry gate: the inside-polygon edge lying on the mouth plane (2, 2),
        ordered [low end, high end]."""
        d = (self.inside - self.mouth[0]) @ self.normal_out
        idx = np.argsort(np.abs(d))[:2]
        g = self.inside[idx]
        return g[np.argsort(g[:, 1])]

    def clearance(self, pts: Sequence) -> tuple[np.ndarray, np.ndarray]:
        """(distance - R, index of nearest obstacle) for ball-centre points (..., 2)."""
        p = np.asarray(pts, float)
        D = seg_point_dist(p[..., None, :], self.P0, self.P1)
        i = np.argmin(D, axis=-1)
        return np.take_along_axis(D, i[..., None], axis=-1)[..., 0] - self.R, i

    def is_inside(self, pts: Sequence) -> np.ndarray:
        return _points_in_convex(np.asarray(pts, float), self.inside)

    def classify_path(self, xz: np.ndarray, t: Optional[np.ndarray] = None) -> dict[str, Any]:
        """Classify a ball-centre polyline xz (N, 2) in THIS hive's frame. See classify_detail."""
        xz = np.asarray(xz, float)
        n = len(xz)
        out: dict[str, Any] = {"result": "miss", "hit": None, "i_event": None, "t_event": None,
                               "entry_point": None, "entry_angle_deg": None,
                               "min_clearance": None, "min_clearance_at": None}
        if n == 0:
            return out
        if n == 1:
            c, j = self.clearance(xz)
            out["min_clearance"] = float(c[0])
            if c[0] < 0:
                out.update(result=f"hit:{self.names[int(j[0])]}", hit=self.names[int(j[0])], i_event=0)
            elif self.is_inside(xz)[0]:
                out.update(result="clean", i_event=0)
            return out
        a = xz[:-1, None, :]
        b = xz[1:, None, :]
        D = seg_seg_dist(a, b, self.P0[None], self.P1[None])  # (n-1, nseg)
        segmin = D.min(axis=1) - self.R
        hit_rows = np.nonzero(segmin < 0.0)[0]
        ins = self.is_inside(xz)
        ins_idx = np.nonzero(ins)[0]
        i_hit = int(hit_rows[0]) if hit_rows.size else None          # path segment i -> i+1
        i_in = int(ins_idx[0]) if ins_idx.size else None             # point index
        if i_in == 0:
            i_hit_before = None
        else:
            i_hit_before = i_hit if (i_hit is not None and (i_in is None or i_hit <= i_in - 1)) else None
        if i_hit_before is not None:
            j = int(np.argmin(D[i_hit_before]))
            out.update(result=f"hit:{self.names[j]}", hit=self.names[j], i_event=i_hit_before)
            upto = i_hit_before + 1
        elif i_in is not None:
            out.update(result="clean", i_event=i_in, entry_point=xz[i_in].tolist())
            k = max(i_in, 1)
            v = xz[k] - xz[k - 1]
            out["entry_angle_deg"] = float(math.degrees(math.atan2(-v[1], abs(v[0]) + 1e-300)))
            upto = max(i_in, 1)
        else:
            upto = n - 1
        seg_c = segmin[:upto] if upto > 0 else segmin[:1]
        k = int(np.argmin(seg_c))
        out["min_clearance"] = float(seg_c[k])
        out["min_clearance_at"] = xz[k].tolist()
        if t is not None and out["i_event"] is not None:
            out["t_event"] = float(np.asarray(t)[out["i_event"]])
        return out

    def raster(self, res: float = 1e-3, box: Optional[Sequence[float]] = None) -> "CSpaceRaster":
        return CSpaceRaster.build(self, res=res, box=box)


# --------------------------------------------------------------------------- fast lookup
@dataclass
class CSpaceRaster:
    """Precomputed clearance field (distance - R) on a regular grid (cell centres).

    Nearest-cell lookup error in clearance <= res/sqrt(2) (distance is 1-Lipschitz).
    Outside the box: clearance = +inf (free), idx = -1.
    """
    x0: float
    z0: float
    res: float
    clr: np.ndarray       # (nz, nx) float32
    idx: np.ndarray       # (nz, nx) int16
    inside: np.ndarray    # (nz, nx) bool
    names: list

    @classmethod
    def build(cls, hive: Hive, res: float = 1e-3, box: Optional[Sequence[float]] = None):
        if box is None:
            allp = np.vstack([hive.P0, hive.P1, hive.inside])
            m = hive.R + 0.01
            box = (allp[:, 0].min() - m, allp[:, 0].max() + m,
                   allp[:, 1].min() - m, allp[:, 1].max() + m)
        xmin, xmax, zmin, zmax = box
        nx = int(math.ceil((xmax - xmin) / res))
        nz = int(math.ceil((zmax - zmin) / res))
        xs = xmin + (np.arange(nx) + 0.5) * res
        clr = np.empty((nz, nx), np.float32)
        idx = np.empty((nz, nx), np.int16)
        ins = np.empty((nz, nx), bool)
        step = max(1, 200000 // max(nx, 1))
        for r0 in range(0, nz, step):
            r1 = min(nz, r0 + step)
            zs = zmin + (np.arange(r0, r1) + 0.5) * res
            X, Z = np.meshgrid(xs, zs)
            pts = np.stack([X, Z], axis=-1)
            c, i = hive.clearance(pts)
            clr[r0:r1] = c
            idx[r0:r1] = i
            ins[r0:r1] = hive.is_inside(pts)
        return cls(x0=xmin, z0=zmin, res=res, clr=clr, idx=idx, inside=ins, names=list(hive.names))

    def lookup(self, x: np.ndarray, z: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        ix = np.floor((np.asarray(x) - self.x0) / self.res).astype(np.int64)
        iz = np.floor((np.asarray(z) - self.z0) / self.res).astype(np.int64)
        nz, nx = self.clr.shape
        ok = (ix >= 0) & (ix < nx) & (iz >= 0) & (iz < nz)
        ixc = np.clip(ix, 0, nx - 1)
        izc = np.clip(iz, 0, nz - 1)
        c = np.where(ok, self.clr[izc, ixc], np.float32(np.inf))
        j = np.where(ok, self.idx[izc, ixc], -1)
        return c, j


# --------------------------------------------------------------------------- public API
_HIVE_CACHE: dict = {}


def is_favorable(pose: str, side: str) -> bool:
    return load_geometry()["poses"][pose]["favorable_side"] == side


def get_hive(pose: str, side: Optional[str] = None, mirror: Optional[bool] = None,
             **kw) -> Hive:
    """Hive for ``pose``; mirrored (shot frame) when side == 'pos' (or mirror=True)."""
    if mirror is None:
        mirror = (side == "pos")
    key = (pose, bool(mirror), tuple(sorted(kw.items())))
    if key not in _HIVE_CACHE:
        h = Hive.from_json(pose, **kw)
        _HIVE_CACHE[key] = h.mirrored() if mirror else h
    return _HIVE_CACHE[key]


def _traj_xz(traj) -> tuple[np.ndarray, Optional[np.ndarray], Optional[np.ndarray]]:
    if hasattr(traj, "pos"):
        pos = np.asarray(traj.pos, float)
        vel = np.asarray(traj.vel, float) if hasattr(traj, "vel") else None
        t = np.asarray(traj.t, float) if hasattr(traj, "t") else None
        return pos[:, [0, 2]], vel, t
    arr = np.asarray(traj, float)
    if arr.ndim == 2 and arr.shape[1] == 3:
        return arr[:, [0, 2]], None, None
    return arr, None, None


def classify_detail(traj, pose: str, side: str, *, frame: str = "auto", **hive_kw) -> dict:
    """Detailed outcome for a trajectory (flight.Trajectory, (N,3) pos array or (N,2) xz).

    side: shooter side "neg" (fires +x) or "pos" (fires -x). frame: "auto" | "shot" | "hive".
    Returns dict(result, hit, i_event, t_event, entry_point, entry_angle_deg (descent angle,
    + = falling), min_clearance (m, before the event), min_clearance_at, favorable, mirrored).
    hive_kw: tilt_deg, pivot_z, include_projected, lateral_offset, ball_radius.
    """
    if side not in ("neg", "pos"):
        raise ValueError("side must be 'neg' or 'pos'")
    xz, vel, t = _traj_xz(traj)
    if frame == "hive":
        mirror = False
    elif frame == "shot":
        mirror = side == "pos"
    elif frame == "auto":
        if len(xz) >= 2:
            vx0 = float(vel[0, 0]) if vel is not None else float(xz[1, 0] - xz[0, 0])
        else:
            vx0 = 1.0
        mirror = (side == "pos" and vx0 > 0.0)
    else:
        raise ValueError("frame must be 'auto', 'shot' or 'hive'")
    hv = get_hive(pose, mirror=mirror, **hive_kw)
    out = hv.classify_path(xz, t)
    out["favorable"] = is_favorable(pose, side)
    out["mirrored"] = mirror
    return out


def classify(traj, pose: str, side: str, **kw) -> str:
    """'clean' | 'hit:<obstacle name>' | 'miss' (see module docstring)."""
    return classify_detail(traj, pose, side, **kw)["result"]
