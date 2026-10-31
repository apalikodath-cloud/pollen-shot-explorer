#!/usr/bin/env python
"""Render side-view shot videos (MP4 + GIF) and an optional field-map still from shots.json.

Usage (from the repo root):
    python viz/render_video.py viz/shots.json                      # all shots -> viz/out/
    python viz/render_video.py viz/shots.json --ids U1_pospose_unfav_high --slowmo 20
    python viz/render_video.py viz/shots.json --map viz/out/map.csv --map-only
    python viz/render_video.py viz/demo/shots.json --out-dir viz/demo/out

Per shot it writes <out>/<id>.mp4 (if an ffmpeg is found: imageio-ffmpeg, then PATH),
<out>/<id>.gif (always, Pillow) and two check stills <id>_apex.png / <id>_end.png.

What every frame shows: tile line and perimeter-wall position, the HIVE section in the
shot's pose (upward CELL highlighted, its scored region shaded, projected A-frame legs
dotted), a schematic robot at the release point, the backspinning ball (true size, with a
rotating marker line turning at the TRUE spin rate slowed by the same factor as time),
the no-spin twin (same v, angle, release) as a grey ghost, velocity and Magnus-acceleration
arrows, a follow-cam close-up, and a HUD. Predicted shots carry 'PREDICTED, uncalibrated
aero'; DEMO shots carry 'DEMO — placeholder geometry, not results' on every frame.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import shutil
import subprocess
import sys

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, Rectangle, Polygon  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from PIL import Image  # noqa: E402

VIZ = os.path.dirname(os.path.abspath(__file__))

C = {
    "bg": "#ffffff", "tile": "#9e9e9e", "tile_fill": "#ececec", "hive": "#3d3d3d", "proj": "#9a9a9a",
    "cell": "#0f7b6c", "cell_fill": "#bfe6df", "ball": "#f5c400", "ball_edge": "#6b5300",
    "trail": "#e07000", "twin": "#8a8a8a", "vel": "#1f5fbf", "mag": "#c2185b", "hit": "#d32f2f",
    "clean": "#0f7b6c", "robot": "#5b6b82", "text": "#1d1d1d", "pred": "#b35c00", "demo": "#c62828",
}
K_V = 0.06     # m of arrow per m/s
K_A = 0.25     # m of arrow per m/s^2
SLOWMO_CHOICES = [4, 5, 8, 10, 12, 15, 20, 25, 30, 40, 50]
DEMO_TEXT = "DEMO — placeholder geometry, not results"
PRED_TEXT = "PREDICTED, uncalibrated aero (not measured)"


# =========================================================================== ffmpeg
def find_ffmpeg():
    try:
        import imageio_ffmpeg  # type: ignore
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and os.path.exists(exe):
            matplotlib.rcParams["animation.ffmpeg_path"] = exe
            return exe
    except Exception:
        pass
    return shutil.which("ffmpeg")


class Mp4Sink:
    def __init__(self, exe, path, w, h, fps, crf=23):
        self.p = subprocess.Popen(
            [exe, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
             "-r", str(fps), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", str(crf),
             "-preset", "medium", "-movflags", "+faststart", path],
            stdin=subprocess.PIPE)

    def write(self, rgb):
        self.p.stdin.write(np.ascontiguousarray(rgb).tobytes())

    def close(self):
        self.p.stdin.close()
        self.p.wait()


# =========================================================================== data helpers
def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def hive_for(doc, pose):
    hv = doc.get("hives", {}).get(pose)
    if hv is None:
        hv = doc["hive"]
    return hv


class Track:
    """Interpolated state along one stored trajectory."""

    def __init__(self, d, keys):
        self.t = np.asarray(d["t"], float)
        self.a = {k: np.asarray(d[k], float) for k in keys if k in d}
        self.t_end = float(self.t[-1])

    def at(self, t):
        tc = min(max(t, 0.0), self.t_end)
        return {k: float(np.interp(tc, self.t, v)) for k, v in self.a.items()}

    def upto(self, t, k):
        n = int(np.searchsorted(self.t, min(t, self.t_end), side="right"))
        return self.a[k][:max(n, 1)]


def choose_slowmo(shot, fps):
    a = np.asarray(shot.get("spin_angle", [0.0]), float)
    t = np.asarray(shot["t"], float)
    if len(a) < 2:
        return 10
    wmax = float(np.max(np.abs(np.diff(a) / np.maximum(np.diff(t), 1e-9))))
    for s in SLOWMO_CHOICES:
        if wmax / (fps * s) <= math.radians(30):
            return s
    return SLOWMO_CHOICES[-1]


def outcome_text(o):
    if o == "clean":
        return "CLEAN ENTRY"
    if o == "rim-assisted":
        return "RIM-ASSISTED ENTRY"
    if o.startswith("hit:"):
        return "HITS " + o[4:]
    return "MISS"


def outcome_color(o):
    return C["clean"] if o in ("clean", "rim-assisted") else (C["hit"] if o.startswith("hit") else C["twin"])


# =========================================================================== drawing
def draw_hive(ax, hv, lw_scale=1.0, label=True):
    up = set(hv.get("up_cell", []))
    proj = set(hv.get("projected", []))
    if hv.get("inside"):
        ax.add_patch(Polygon(hv["inside"], closed=True, fc=C["cell_fill"], ec="none", alpha=0.8, zorder=1))
    for x0, z0, x1, z1, name in hv["segments"]:
        if name in proj:
            ax.plot([x0, x1], [z0, z1], ls=(0, (1, 2)), color=C["proj"], lw=1.0 * lw_scale, zorder=2)
        elif name in up:
            ax.plot([x0, x1], [z0, z1], color=C["cell"], lw=3.2 * lw_scale, solid_capstyle="round", zorder=3)
        else:
            ax.plot([x0, x1], [z0, z1], color=C["hive"], lw=2.2 * lw_scale, solid_capstyle="round", zorder=3)
    m = hv["mouth"]
    ax.plot([m[0], m[2]], [m[1], m[3]], color=C["cell"], lw=1.2 * lw_scale, ls="--", zorder=2)
    px, pz = hv.get("pivot", [0, None])
    if pz is not None:
        ax.plot([px], [pz], "o", ms=4 * lw_scale, color=C["hive"], zorder=4)
    if label:
        cx, cz = (m[0] + m[2]) / 2, (m[1] + m[3]) / 2
        mx = np.mean([p[0] for p in hv["inside"]]) if hv.get("inside") else cx
        dx = 1 if cx >= mx else -1
        ax.annotate("upward CELL\nmouth", (cx, cz), xytext=(cx + 0.22 * dx, cz + 0.28), fontsize=8,
                    color=C["cell"], ha="center", arrowprops=dict(arrowstyle="-", color=C["cell"], lw=0.8),
                    zorder=6)


def draw_field(ax, hv, xlim):
    ax.add_patch(Rectangle((xlim[0] - 1, -0.5), (xlim[1] - xlim[0]) + 2, 0.5, fc=C["tile_fill"], ec="none", zorder=0))
    ax.axhline(0.0, color=C["tile"], lw=1.5, zorder=1)
    xw = hv.get("x_wall")
    if xw:
        for s in (-1, 1):
            if xlim[0] <= s * xw <= xlim[1]:
                ax.plot([s * xw, s * xw], [0, 0.30], color=C["tile"], lw=4, zorder=1)
                ax.text(s * xw, 0.33, "wall", ha="center", fontsize=7, color=C["tile"])


def draw_robot(ax, shot):
    x0, z0 = shot["release"]
    sgn = -1.0 if x0 < 0 else 1.0     # robot sits on the far side of the release point
    w = 0.457                          # 18 in start-cube width (Manual R102, confirmed)
    left = x0 if sgn > 0 else x0 - w
    xw = (shot.get("_x_wall") or 0.0)
    if xw:                             # keep the schematic inside the perimeter wall
        left = min(left, xw - w) if sgn > 0 else max(left, -xw)
    h = max(z0 - 0.06, 0.05)
    ax.add_patch(Rectangle((left, 0.0), w, h, fc="#dfe4ea", ec=C["robot"], lw=1.2, zorder=2))
    e = math.radians(shot["elev_deg"])
    d = -sgn
    ax.plot([x0 - d * 0.12 * math.cos(e), x0], [z0 - 0.12 * math.sin(e), z0], color=C["robot"], lw=3, zorder=3)
    ax.text(left + w / 2, h / 2, "robot\n(schematic)", ha="center", va="center", fontsize=7, color=C["robot"], zorder=3)


def fit_limits(xr, zr, box_aspect):
    """Expand (xr, zr) so data aspect == box_aspect (height/width) with equal axis scaling."""
    x0, x1 = xr
    z0, z1 = zr
    w, h = x1 - x0, z1 - z0
    if h / w < box_aspect:
        nh = w * box_aspect
        return (x0, x1), (z0, z0 + nh)
    nw = h / box_aspect
    cx = (x0 + x1) / 2
    return (cx - nw / 2, cx + nw / 2), (z0, z1)


class ShotScene:
    def __init__(self, doc, shot, fps, slowmo, size=(12.8, 7.2), dpi=100):
        self.doc, self.shot, self.fps, self.slowmo = doc, shot, fps, slowmo
        self.demo = doc["meta"].get("source") == "demo"
        self.hv = hive_for(doc, shot["pose"])
        self.R = float(shot.get("radius", 0.0355))
        self.mass = float(shot.get("mass", 0.025))
        self.trk = Track(shot, ["x", "z", "vx", "vz", "spin_angle", "spin_rpm_t", "S_t", "FMx", "FMz", "FDx", "FDz"])
        self.twin = Track(shot["twin_no_spin"], ["x", "z"])
        self.t_end = max(self.trk.t_end, self.twin.t_end)
        self.fig = plt.figure(figsize=size, dpi=dpi, facecolor=C["bg"])
        self._build()

    # ---- static layout
    def _build(self):
        sh, hv, fig = self.shot, self.hv, self.fig
        ax = fig.add_axes([0.035, 0.10, 0.63, 0.78])
        self.ax = ax
        xs = np.concatenate([sh["x"], sh["twin_no_spin"]["x"], [p[0] for p in hv["inside"]],
                             [s[0] for s in hv["segments"]], [s[2] for s in hv["segments"]]])
        zs = np.concatenate([sh["z"], sh["twin_no_spin"]["z"], [s[1] for s in hv["segments"]]])
        x0, x1 = float(xs.min()) - 0.45, float(xs.max()) + 0.3
        if sh["release"][0] < 0:
            x0 = min(x0, sh["release"][0] - 0.6)
        else:
            x1 = max(x1, sh["release"][0] + 0.6)
        bb = ax.get_position()
        W, H = fig.get_size_inches()
        xl, zl = fit_limits((x0, x1), (-0.08, float(zs.max()) + 0.25), (bb.height * H) / (bb.width * W))
        ax.set_xlim(*xl)
        ax.set_ylim(*zl)
        ax.set_aspect("equal")
        ax.set_xlabel("x (m) — horizontal, HIVE tipping plane (0 = below pivot)", fontsize=8)
        ax.set_ylabel("z (m) above tiles", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.grid(True, color="#f0f0f0", lw=0.6, zorder=0)
        for s in ax.spines.values():
            s.set_color("#cccccc")
        draw_field(ax, hv, xl)
        draw_hive(ax, hv)
        draw_robot(ax, dict(sh, _x_wall=hv.get("x_wall")))
        # full paths, very faint, so the viewer sees where both will go
        ax.plot(sh["twin_no_spin"]["x"], sh["twin_no_spin"]["z"], color=C["twin"], lw=0.6, alpha=0.25, ls="--", zorder=4)
        # dynamic artists
        self.twin_line, = ax.plot([], [], color=C["twin"], lw=1.6, ls="--", zorder=5)
        self.twin_ball = Circle((0, 0), self.R, fc="none", ec=C["twin"], lw=1.2, zorder=6)
        ax.add_patch(self.twin_ball)
        self.trail, = ax.plot([], [], color=C["trail"], lw=2.0, zorder=7)
        self.ball = Circle((0, 0), self.R, fc=C["ball"], ec=C["ball_edge"], lw=1.0, zorder=9)
        ax.add_patch(self.ball)
        self.mark, = ax.plot([], [], color=C["ball_edge"], lw=1.4, zorder=10)
        self.dot, = ax.plot([], [], "o", ms=2.5, color="#c62828", zorder=11)
        self.q = ax.quiver([0, 0], [0, 0], [0, 0], [0, 0], color=[C["vel"], C["mag"]], angles="xy",
                           scale_units="xy", scale=1, width=0.0032, headwidth=4, headlength=5, zorder=12)
        box = dict(fc="white", ec="none", alpha=0.85, pad=1.5)
        self.ev_spin = ax.text(0, 0, "", fontsize=9, fontweight="bold", zorder=14, ha="center", bbox=box)
        self.ev_twin = ax.text(0, 0, "", fontsize=8, color="#555555", zorder=14, ha="center", bbox=box)
        self.hit_mark, = ax.plot([], [], "x", ms=12, mew=2.5, color=C["hit"], zorder=13)
        self.twin_mark, = ax.plot([], [], "x", ms=9, mew=1.8, color=C["twin"], zorder=13)
        if self.demo:
            ax.text(0.5, 0.5, DEMO_TEXT, transform=ax.transAxes, fontsize=26, color=C["demo"], alpha=0.22,
                    rotation=28, ha="center", va="center", fontweight="bold", zorder=20)
        # legend
        handles = [Line2D([], [], color=C["trail"], lw=2, label=f"backspin ball ({sh['spin_rpm']:.0f} rpm at release)"),
                   Line2D([], [], color=C["twin"], lw=1.6, ls="--", label="no-spin twin (same v, angle, release)"),
                   Line2D([], [], color=C["cell"], lw=3, label="upward CELL (shaded = scored ball-centre zone)"),
                   Line2D([], [], color=C["hive"], lw=2, label="other HIVE / frame parts"),
                   Line2D([], [], color=C["vel"], lw=2, label=f"velocity ({K_V} m per m/s)"),
                   Line2D([], [], color=C["mag"], lw=2, label=f"Magnus accel ({K_A} m per m/s²; g = {9.81 * K_A:.2f} m)")]
        if self.hv.get("projected"):
            handles.append(Line2D([], [], color=C["proj"], lw=1, ls=(0, (1, 2)), label="A-frame legs (projected, not in this plane)"))
        ax.legend(handles=handles, loc="upper left", fontsize=7, framealpha=0.92)

        # banner + title
        if self.demo:
            fig.text(0.5, 0.965, DEMO_TEXT, ha="center", va="center", fontsize=15, color="white", fontweight="bold",
                     bbox=dict(fc=C["demo"], ec="none", pad=4))
        else:
            fig.text(0.5, 0.965, PRED_TEXT + f"  ·  aero set: {sh.get('aero_set', '?')}", ha="center", va="center",
                     fontsize=13, color="white", fontweight="bold", bbox=dict(fc=C["pred"], ec="none", pad=4))
        fig.text(0.035, 0.915, f"{sh['id']}: {sh.get('title', '')}", fontsize=11, color=C["text"], fontweight="bold")
        fig.text(0.035, 0.025,
                 f"Side view, HIVE pose {sh['pose']} ({self.hv.get('status', '')}). Ball and HIVE to scale. "
                 f"Spin marker turns at the TRUE rate, slowed ×{self.slowmo} with time. "
                 "Flights stop at first contact (no bounce model).", fontsize=7, color="#555555")

        # follow-cam close-up
        self.zax = fig.add_axes([0.69, 0.50, 0.29, 0.38])
        self.zax.set_aspect("equal")
        self.zax.set_xticks([])
        self.zax.set_yticks([])
        self.zax.set_facecolor("#fbfbfb")
        self.zax.set_title("follow-cam close-up (0.5 m window, true scale)", fontsize=8)
        draw_field(self.zax, hv, (-3, 3))
        draw_hive(self.zax, hv, lw_scale=1.6, label=False)
        self.z_twin_line, = self.zax.plot([], [], color=C["twin"], lw=1.6, ls="--", zorder=5)
        self.z_twin = Circle((0, 0), self.R, fc="none", ec=C["twin"], lw=1.5, zorder=6)
        self.zax.add_patch(self.z_twin)
        self.z_trail, = self.zax.plot([], [], color=C["trail"], lw=2.4, zorder=7)
        self.z_ball = Circle((0, 0), self.R, fc=C["ball"], ec=C["ball_edge"], lw=1.5, zorder=9)
        self.zax.add_patch(self.z_ball)
        self.z_mark, = self.zax.plot([], [], color=C["ball_edge"], lw=2.5, zorder=10)
        self.z_dot, = self.zax.plot([], [], "o", ms=6, color="#c62828", zorder=11)
        self.z_q = self.zax.quiver([0, 0], [0, 0], [0, 0], [0, 0], color=[C["vel"], C["mag"]], angles="xy",
                                   scale_units="xy", scale=1, width=0.012, zorder=12)
        if self.demo:
            self.zax.text(0.5, 0.5, "DEMO", transform=self.zax.transAxes, fontsize=34, color=C["demo"], alpha=0.2,
                          ha="center", va="center", rotation=28, fontweight="bold", zorder=20)

        # HUD
        self.hud_static = fig.text(0.69, 0.455, self._static_hud(), fontsize=8, family="monospace", va="top",
                                   color=C["text"])
        self.hud = fig.text(0.69, 0.27, "", fontsize=8.5, family="monospace", va="top", color=C["text"])
        self.hud_out = fig.text(0.69, 0.115, "", fontsize=10, va="top", fontweight="bold")
        self.hud_twin = fig.text(0.69, 0.075, "", fontsize=8.5, va="top", color=C["twin"])

    def _static_hud(self):
        sh = self.shot
        x0, z0 = sh["release"]
        lines = [f"pose {sh['pose']}  ·  {sh['side']} side",
                 f"release x={x0:+.2f} m  z={z0:.2f} m (assumed)",
                 f"launch  v={sh['v']:.2f} m/s  elev={sh['elev_deg']:.1f}°",
                 f"spin    {sh['spin_rpm']:.0f} rpm backspin  S={sh['S']:.2f}",
                 f"aero    {sh.get('aero_set', '?')}: " + _wrap(sh.get('aero_desc', ''), 38, 8)]
        return "\n".join(lines)

    # ---- per-frame update
    def update(self, t, phase="fly"):
        s = self.trk.at(t)
        x, z = s["x"], s["z"]
        ang = s.get("spin_angle", 0.0)
        R = self.R
        ex, ez = R * math.cos(ang), R * math.sin(ang)
        self.ball.center = (x, z)
        self.mark.set_data([x - ex, x + ex], [z - ez, z + ez])
        self.dot.set_data([x + ex], [z + ez])
        self.trail.set_data(self.trk.upto(t, "x"), self.trk.upto(t, "z"))
        w = self.twin.at(t)
        self.twin_ball.center = (w["x"], w["z"])
        self.twin_line.set_data(self.twin.upto(t, "x"), self.twin.upto(t, "z"))
        flying = t < self.trk.t_end
        vx, vz = (s["vx"], s["vz"]) if flying else (0.0, 0.0)
        ax_m, az_m = (s["FMx"] / self.mass, s["FMz"] / self.mass) if flying else (0.0, 0.0)
        self.q.set_offsets([[x, z], [x, z]])
        self.q.set_UVC([vx * K_V, ax_m * K_A], [vz * K_V, az_m * K_A])
        # close-up
        half = 0.25
        self.zax.set_xlim(x - half, x + half)
        self.zax.set_ylim(z - half, z + half)
        self.z_ball.center = (x, z)
        self.z_mark.set_data([x - ex, x + ex], [z - ez, z + ez])
        self.z_dot.set_data([x + ex], [z + ez])
        self.z_trail.set_data(self.trk.upto(t, "x"), self.trk.upto(t, "z"))
        self.z_twin.center = (w["x"], w["z"])
        self.z_twin_line.set_data(self.twin.upto(t, "x"), self.twin.upto(t, "z"))
        kz = 0.4  # close-up arrows: shorter so they stay in the window
        self.z_q.set_offsets([[x, z], [x, z]])
        self.z_q.set_UVC([vx * K_V * kz, ax_m * K_A * kz], [vz * K_V * kz, az_m * K_A * kz])
        # events
        sh = self.shot
        if not flying:
            o = sh["outcome"]
            tw_end = self.twin.at(self.twin.t_end)
            near = abs(tw_end["x"] - x) < 0.5 and abs(tw_end["z"] - z) < 0.4
            self.ev_spin.set_position((x, z + (0.40 if near else 0.12)))
            self.ev_spin.set_text(outcome_text(o))
            self.ev_spin.set_color(outcome_color(o))
            if o.startswith("hit"):
                self.hit_mark.set_data([x], [z])
        else:
            self.ev_spin.set_text("")
            self.hit_mark.set_data([], [])
        if t >= self.twin.t_end:
            o = sh["twin_no_spin"]["outcome"]
            self.ev_twin.set_position((w["x"], w["z"] + (0.12 if w["z"] < 0.5 else 0.22)))
            self.ev_twin.set_text("no spin: " + outcome_text(o))
            if o.startswith("hit"):
                self.twin_mark.set_data([w["x"]], [w["z"]])
        else:
            self.ev_twin.set_text("")
            self.twin_mark.set_data([], [])
        # HUD
        sp = math.hypot(s["vx"], s["vz"])
        am = math.hypot(s["FMx"], s["FMz"]) / self.mass
        ap = sh.get("apex") or {}
        hud = [f"t = {min(t, self.t_end):6.3f} s   slow motion ×{self.slowmo}",
               f"speed {sp:5.2f} m/s   spin {s.get('spin_rpm_t', 0):5.0f} rpm",
               f"S = {s.get('S_t', 0):4.2f}   Magnus {am:4.2f} m/s² ({am / 9.80665:4.2f} g)",
               (f"apex z = {ap.get('z', float('nan')):.2f} m at t = {ap.get('t', float('nan')):.2f} s"
                if ap.get("t", 0.0) <= self.trk.t_end + 1e-9 else "apex: not reached before the flight ends")
               if ap else "apex: none",
               f"mid-air horizontal reversal: {'YES' if sh.get('horizontal_reversal') else 'no'}"]
        self.hud.set_text("\n".join(hud))
        if not flying:
            o = sh["outcome"]
            ea = sh.get("entry_angle_deg")
            extra = "" if o != "clean" or ea is None else (f" ({ea:.0f}° descent)" if ea >= 0 else
                                                           f" (still rising, {-ea:.0f}° up)")
            self.hud_out.set_text("outcome: " + outcome_text(o) + extra)
            self.hud_out.set_color(outcome_color(o))
        else:
            self.hud_out.set_text("outcome: in flight…")
            self.hud_out.set_color(C["text"])
        tw = sh["twin_no_spin"]["outcome"]
        self.hud_twin.set_text("no-spin twin: " + (outcome_text(tw) if t >= self.twin.t_end else "in flight…"))

    def rgb(self):
        self.fig.canvas.draw()
        return np.asarray(self.fig.canvas.buffer_rgba())[..., :3].copy()


def _wrap(s, width, indent):
    words, lines, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return ("\n" + " " * indent).join(lines)


# =========================================================================== rendering
def render_shot(doc, shot, out_dir, fps=30, slowmo=None, gif_every=2, gif_width=800, ffmpeg=None,
                intro=0.6, outro=2.5, crf=23):
    slow = slowmo or choose_slowmo(shot, fps)
    sc = ShotScene(doc, shot, fps, slow)
    dt = 1.0 / (fps * slow)
    n_fly = int(math.ceil(sc.t_end / dt)) + 1
    n_in, n_out = int(intro * fps), int(outro * fps)
    times = [0.0] * n_in + [min(i * dt, sc.t_end) for i in range(n_fly)] + [sc.t_end + 1e-6] * n_out
    os.makedirs(out_dir, exist_ok=True)
    sid = shot["id"]
    W, H = (np.array(sc.fig.get_size_inches()) * sc.fig.dpi).astype(int)
    mp4 = None
    if ffmpeg:
        mp4 = Mp4Sink(ffmpeg, os.path.join(out_dir, f"{sid}.mp4"), W, H, fps, crf)
    gif_frames = []
    t_apex = (shot.get("apex") or {}).get("t")
    i_apex = None if t_apex is None else n_in + int(round(t_apex / dt))
    pal = None
    for i, t in enumerate(times):
        sc.update(t)
        img = sc.rgb()
        if mp4:
            mp4.write(img)
        if i == i_apex:
            Image.fromarray(img).save(os.path.join(out_dir, f"{sid}_apex.png"))
        if i % gif_every == 0 or i == len(times) - 1:
            im = Image.fromarray(img)
            gh = int(round(H * gif_width / W))
            im = im.resize((gif_width, gh), Image.LANCZOS)
            if pal is None:
                pal = im.quantize(colors=96, method=Image.Quantize.MEDIANCUT)
            gif_frames.append(im.quantize(palette=pal, dither=Image.Dither.NONE))
    Image.fromarray(img).save(os.path.join(out_dir, f"{sid}_end.png"))
    if mp4:
        mp4.close()
    gpath = os.path.join(out_dir, f"{sid}.gif")
    dur = int(round(1000 * gif_every / fps))
    durs = [dur] * len(gif_frames)
    durs[-1] = 2500
    gif_frames[0].save(gpath, save_all=True, append_images=gif_frames[1:], duration=durs, loop=0,
                       optimize=False, disposal=1)
    plt.close(sc.fig)
    res = {"id": sid, "slowmo": slow, "frames": len(times), "video_s": round(len(times) / fps, 1),
           "gif": gpath, "gif_MB": round(os.path.getsize(gpath) / 1e6, 2)}
    if mp4:
        p = os.path.join(out_dir, f"{sid}.mp4")
        res.update(mp4=p, mp4_MB=round(os.path.getsize(p) / 1e6, 2))
    return res


# =========================================================================== field map still
def _col(cols, names):
    low = {c.lower(): c for c in cols}
    for n in names:
        if n.lower() in low:
            return low[n.lower()]
    return None


def _read_csv(path):
    """csv.DictReader that skips '#' comment lines (src/feasibility.py writes a '# ...' header)."""
    with open(path, newline="", encoding="utf-8") as fh:
        lines = [ln for ln in fh if ln.strip() and not ln.lstrip().startswith("#")]
    return list(csv.DictReader(lines))


def _ok(v):
    v = str(v).strip().lower()
    return v in ("clean", "1", "true", "yes", "ok", "rim-assisted") or v.startswith("clean")


def render_map(doc, csv_path, out_png, pose=None, xcol=None, zcol=None, valcol=None, side=None, facet=None,
               filters=None, max_panels=4):
    """Field-map still: one marker per release point, the HIVE section, and the shots.json paths.

    Two CSV kinds are understood (columns auto-detected, override with xcol/zcol/valcol/facet):
      * per-launch rows (viz/make_shots.py --sweep-map): value = outcome string; colour = fraction
        of the swept launches at that release point that enter clean.
      * per-release-point summary rows (src/feasibility.py data/clean_feasibility_map.csv:
        h, d, n_clean, case, geometry, v_cap, ...): value = a number (default n_clean, the count
        of clean (v, elevation) grid cells); colour = that number (mean if several rows coincide).
    filters: {column: value} keeps only matching rows. For a 'geometry' column (unfav_t30 /
    fav_t30 ...) the default keeps the nominal-tilt rows of the requested side (unfavourable if
    none); for 'v_cap' the default keeps the lowest cap (the hood-limited one). Distances (d) from
    a file with a 'geometry' column are drawn in the shot frame of src/feasibility.py: shooter on
    the -x side at x = -d (unfavourable -> pose_pos, favourable -> pose_neg)."""
    rows = _read_csv(csv_path)
    if not rows:
        raise ValueError(f"{csv_path} is empty")
    cols = list(rows[0].keys())
    filters = dict(filters or {})
    gcol = _col(cols, ["geometry"])
    if gcol and gcol not in filters:
        gvals = sorted({r[gcol] for r in rows})
        want = "fav" if side == "favorable" else "unfav"
        pick = sorted([g for g in gvals if g.startswith(want + "_")], key=lambda g: (g != f"{want}_t30", g))
        if pick:
            filters[gcol] = pick[0]
    vcol = _col(cols, ["v_cap"])
    if vcol and vcol not in filters:
        caps = sorted({r[vcol] for r in rows}, key=lambda v: float(v) if _isnum(v) else 1e9)
        if caps:
            filters[vcol] = caps[0]
    for k, v in filters.items():
        if k not in cols:
            raise ValueError(f"filter column {k!r} not in {cols}")
        rows = [r for r in rows if str(r[k]) == str(v)]
    if not rows:
        raise ValueError(f"no rows left after filters {filters}")
    if gcol and side is None:
        side = "favorable" if str(rows[0][gcol]).startswith("fav") else "unfavorable"
    xcol = xcol or _col(cols, ["release_x", "x0", "x", "d", "distance"])
    zcol = zcol or _col(cols, ["release_z", "z0", "z", "h", "release_h", "height"])
    valcol = valcol or _col(cols, ["outcome", "result", "n_clean", "clean", "feasible", "ok"])
    if not facet:
        for cand in (["case"], ["S", "S0", "spin_S", "spin_rpm"]):
            c = _col(cols, cand)
            if c and len({r[c] for r in rows}) > 1:
                facet = c
                break
    if not (xcol and zcol and valcol):
        raise ValueError(f"cannot find x/z/value columns in {cols}; pass --map-x/--map-z/--map-value")
    numeric = all(_isnum(r[valcol]) for r in rows) and not all(str(r[valcol]).strip() in ("0", "1") for r in rows)
    pcol = _col(cols, ["pose"])
    is_dist = xcol.lower() in ("d", "distance")
    if is_dist and gcol and not pcol:
        pose = pose or ("pose_neg" if side == "favorable" else "pose_pos")
    pose = pose or (rows[0][pcol] if pcol else doc["shots"][0]["pose"] if doc.get("shots") else "pose_pos")
    if pcol:
        rows = [r for r in rows if r[pcol] == pose] or rows
    hv = hive_for(doc, pose)
    sgn = None
    if is_dist:
        if gcol:
            sgn = -1.0                       # src/feasibility.py shot frame: shooter at x = -d
        else:
            fav = hv.get("favorable_side", "pos")
            sh = side or "unfavorable"
            shooter = fav if sh == "favorable" else ("neg" if fav == "pos" else "pos")
            sgn = -1.0 if shooter == "neg" else 1.0

    groups = {}
    for r in rows:
        f = r.get(facet, "all") if facet else "all"
        xv = float(r[xcol])
        key = (round(sgn * abs(xv) if sgn is not None else xv, 4), round(float(r[zcol]), 4))
        g = groups.setdefault(f, {}).setdefault(key, [0.0, 0])
        g[0] += float(r[valcol]) if numeric else _ok(r[valcol])
        g[1] += 1
    order = sorted(groups, key=lambda s: (0, float(s), "") if _isnum(s) else (1, 0.0, str(s)))
    if len(order) > max_panels:
        print(f"[render] map: {len(order)} values of {facet!r}; showing the first {max_panels} "
              f"({', '.join(order[:max_panels])}); pick others with --map-filter {facet}=...", file=sys.stderr)
    facets = order[:max_panels]
    demo = doc["meta"].get("source") == "demo" or any(r.get("source") == "demo" for r in rows[:5])
    allx = [k[0] for f in facets for k in groups[f]]
    xl = (min(allx + [-0.3]) - 0.4, max(allx + [0.8]) + 0.4)
    allz = [k[1] for f in facets for k in groups[f]]
    vals = [v[0] / v[1] for f in facets for v in groups[f].values()]
    vmax_all = max(max(vals), 1.0) if numeric else max(0.02, max(vals))
    yl = (-0.08, max(1.9, max(allz) + 0.3))
    pw = 9.0
    ph = max(2.8, pw * 0.8 * (yl[1] - yl[0]) / (xl[1] - xl[0]) + 0.9)
    fh = ph * len(facets) + 0.9
    fig, axs = plt.subplots(len(facets), 1, figsize=(pw, fh), dpi=110, squeeze=False)
    fig.subplots_adjust(top=1 - 1.0 / fh, bottom=0.55 / fh, hspace=0.35, left=0.07, right=0.97)
    msize = 42 if len(allx) / max(len(facets), 1) < 120 else 14
    for ax, f in zip(axs[:, 0], facets):
        draw_field(ax, hv, xl)
        draw_hive(ax, hv, label=False)
        for s in doc.get("shots", []):
            if s["pose"] == pose:
                ax.plot(s["x"], s["z"], color=C["trail"], lw=0.9, alpha=0.7)
                ax.plot(s["twin_no_spin"]["x"], s["twin_no_spin"]["z"], color=C["twin"], lw=0.7, ls="--", alpha=0.6)
        pts = np.array([[k[0], k[1], v[0] / v[1], v[1]] for k, v in groups[f].items()])
        sc = ax.scatter(pts[:, 0], pts[:, 1], c=pts[:, 2], cmap="Greens", vmin=0, vmax=vmax_all,
                        s=msize, edgecolors="#555555", linewidths=0.4, zorder=8)
        none = pts[:, 2] == 0
        ax.scatter(pts[none, 0], pts[none, 1], marker="x", s=msize * 0.4, color="#999999", zorder=9)
        lab = f"{facet} = {f}" if facet else ""
        what = f"value = {valcol}" if numeric else f"n = {int(pts[0, 3])} launches per release point"
        ax.set_title(f"pose {pose}   {lab}   ({what}; x = none clean)", fontsize=9)
        ax.set_aspect("equal")
        ax.set_xlim(*xl)
        ax.set_ylim(*yl)
        ax.set_xlabel("x (m)" + ("   (release at x = -d: shot frame of src/feasibility.py)" if gcol and is_dist else ""),
                      fontsize=8)
        ax.set_ylabel("z (m)", fontsize=8)
        ax.tick_params(labelsize=7)
        fig.colorbar(sc, ax=ax, shrink=0.85, pad=0.02,
                     label=(valcol if numeric else "fraction of launches\nthat enter clean"))
        if demo:
            ax.text(0.5, 0.5, DEMO_TEXT, transform=ax.transAxes, fontsize=16, color=C["demo"], alpha=0.25,
                    rotation=28, ha="center", va="center", fontweight="bold", zorder=20)
    banner = DEMO_TEXT if demo else PRED_TEXT + " — field map"
    fig.suptitle(banner, color="white", fontweight="bold", fontsize=11,
                 bbox=dict(fc=C["demo"] if demo else C["pred"], ec="none", pad=4))
    flt = ", ".join(f"{k}={v}" for k, v in filters.items())
    fig.text(0.01, 0.01, f"source: {os.path.basename(csv_path)}; x={xcol}, z={zcol}, value={valcol}"
             + (f"; filters: {flt}" if flt else ""), fontsize=7, color="#555555")
    os.makedirs(os.path.dirname(os.path.abspath(out_png)), exist_ok=True)
    fig.savefig(out_png, facecolor="white")
    plt.close(fig)
    return out_png


def _isnum(s):
    try:
        float(s)
        return True
    except (TypeError, ValueError):
        return False


# =========================================================================== CLI
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("shots", nargs="?", default=os.path.join(VIZ, "shots.json"))
    ap.add_argument("--out-dir", help="default: <shots dir>/out")
    ap.add_argument("--ids", nargs="*", help="only these shot ids")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--slowmo", type=float, help="slow-motion factor (default: auto, spin marker <= 30 deg/frame)")
    ap.add_argument("--gif-every", type=int, default=2, help="keep every Nth frame in the GIF (default 2 -> 15 fps)")
    ap.add_argument("--gif-width", type=int, default=800)
    ap.add_argument("--no-mp4", action="store_true")
    ap.add_argument("--map", help="map CSV for the combined field-map still")
    ap.add_argument("--map-only", action="store_true")
    ap.add_argument("--map-pose")
    ap.add_argument("--map-side", choices=["favorable", "unfavorable"])
    ap.add_argument("--map-x")
    ap.add_argument("--map-z")
    ap.add_argument("--map-value")
    ap.add_argument("--map-facet")
    ap.add_argument("--map-filter", action="append", default=[], metavar="COL=VALUE",
                    help="keep only map rows with COL == VALUE (repeatable), e.g. case=S1_Clnominal")
    ap.add_argument("--map-name", default="field_map.png", help="output file name inside --out-dir")
    a = ap.parse_args(argv)

    doc = load(a.shots)
    out_dir = a.out_dir or os.path.join(os.path.dirname(os.path.abspath(a.shots)), "out")
    results = []
    if not a.map_only:
        ff = None if a.no_mp4 else find_ffmpeg()
        if not a.no_mp4 and not ff:
            print("[render] no ffmpeg found (pip install --user imageio-ffmpeg); writing GIF only", file=sys.stderr)
        for s in doc["shots"]:
            if a.ids and s["id"] not in a.ids:
                continue
            r = render_shot(doc, s, out_dir, fps=a.fps, slowmo=int(a.slowmo) if a.slowmo else None,
                            gif_every=a.gif_every, gif_width=a.gif_width, ffmpeg=ff)
            print(f"[render] {r}")
            results.append(r)
    if a.map:
        flt = dict(f.split("=", 1) for f in a.map_filter)
        p = render_map(doc, a.map, os.path.join(out_dir, a.map_name), pose=a.map_pose, xcol=a.map_x,
                       zcol=a.map_z, valcol=a.map_value, side=a.map_side, facet=a.map_facet, filters=flt)
        print(f"[render] field map -> {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
