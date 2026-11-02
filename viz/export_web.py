#!/usr/bin/env python
"""Export a compact web_data.json (and optionally a self-contained replay.html) from shots.json.

Usage (from the repo root):
    python viz/export_web.py                                   # viz/shots.json -> viz/web_data.json
    python viz/export_web.py viz/shots.json --html viz/replay.html
    python viz/export_web.py viz/demo/shots.json --out viz/demo/web_data.json --html viz/demo/replay.html

Compact format (integers only in the arrays):
  lengths in mm, times in ms, spin angle in mrad (cumulative CCW in the x-z view),
  velocities in mm/s, Magnus acceleration in mm/s^2, spin in rpm.
  Trajectories are downsampled to --dt-ms (default 10 ms) plus the exact last sample;
  the spin angle is cumulative, so linear interpolation between samples is exact enough
  for a canvas replay (redraw at any frame rate, rotate the marker by the interpolated angle).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

VIZ = os.path.dirname(os.path.abspath(__file__))


def _idx(t, dt):
    t = np.asarray(t, float)
    keep = [0]
    nxt = dt
    for i in range(1, len(t)):
        if t[i] >= nxt - 1e-9:
            keep.append(i)
            nxt = t[i] + dt
    if keep[-1] != len(t) - 1:
        keep.append(len(t) - 1)
    return np.array(keep)


def _mm(a, k=1000.0):
    return [int(round(float(v) * k)) for v in np.asarray(a, float)]


def export(doc, dt_ms=10.0):
    dt = dt_ms / 1000.0
    hives = {}
    for pose, hv in (doc.get("hives") or {doc["hive"]["pose"]: doc["hive"]}).items():
        names = [s[4] for s in hv["segments"]]
        hives[pose] = {
            "names": names,
            "seg": [_mm(s[:4]) for s in hv["segments"]],
            "up": [i for i, n in enumerate(names) if n in set(hv.get("up_cell", []))],
            "proj": [i for i, n in enumerate(names) if n in set(hv.get("projected", []))],
            "mouth": _mm(hv["mouth"]),
            "inside": [_mm(p) for p in hv.get("inside", [])],
            "pivot": _mm(hv.get("pivot", [0, 0])),
            "x_wall": int(round(1000 * float(hv.get("x_wall") or 1.8009))),
            "tilt_deg": hv.get("tilt_deg"),
            "favorable_side": hv.get("favorable_side"),
            "status": hv.get("status", ""),
        }
    shots = []
    for s in doc["shots"]:
        k = _idx(s["t"], dt)
        mass = float(s.get("mass", 0.025))
        A = lambda key, f=1000.0: _mm(np.asarray(s[key], float)[k], f)  # noqa: E731
        tw = s["twin_no_spin"]
        kt = _idx(tw["t"], dt)
        shots.append({
            "id": s["id"], "title": s.get("title", ""), "pose": s["pose"], "side": s["side"],
            "release": _mm(s["release"]), "v": s["v"], "elev_deg": s["elev_deg"], "spin_rpm": s["spin_rpm"],
            "S": s["S"], "aero_set": s.get("aero_set"), "outcome": s["outcome"], "end_note": s.get("end_note", ""),
            "entry_angle_deg": s.get("entry_angle_deg"), "horizontal_reversal": s.get("horizontal_reversal"), "apex_reached": s.get("apex_reached"),
            "apex": None if not s.get("apex") else {"t": int(round(1000 * s["apex"]["t"])),
                                                    "x": int(round(1000 * s["apex"]["x"])),
                                                    "z": int(round(1000 * s["apex"]["z"]))},
            "r": int(round(1000 * float(s.get("radius", 0.0355)) * 10)) / 10,
            "t": A("t"), "x": A("x"), "z": A("z"), "a": A("spin_angle"),
            "vx": A("vx"), "vz": A("vz"),
            "rpm": [int(round(v)) for v in np.asarray(s["spin_rpm_t"], float)[k]],
            "amx": _mm(np.asarray(s["FMx"], float)[k] / mass), "amz": _mm(np.asarray(s["FMz"], float)[k] / mass),
            "twin": {"t": _mm(np.asarray(tw["t"], float)[kt]), "x": _mm(np.asarray(tw["x"], float)[kt]),
                     "z": _mm(np.asarray(tw["z"], float)[kt]), "outcome": tw["outcome"]},
        })
    meta = dict(doc["meta"])
    meta["web_units"] = "mm, ms, mrad, mm/s, mm/s^2, rpm (integers)"
    meta["web_dt_ms"] = dt_ms
    meta["banner"] = ("DEMO — placeholder geometry, not results" if meta.get("source") == "demo"
                      else "PREDICTED, uncalibrated aero (not measured)")
    return {"meta": meta, "hives": hives, "shots": shots}


HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>POLLEN Shot Replay</title>
<style>
:root{--bg:#fff;--fg:#1d1d1d;--muted:#666;--line:#ddd;--hive:#3d3d3d;--cell:#0f7b6c;--cellfill:#bfe6df;--ball:#f5c400;--trail:#e07000;--twin:#8a8a8a;--banner:#b35c00;--demo:#c62828;--tile:#ececec}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#15171a;--fg:#e8e8e8;--muted:#a0a0a0;--line:#333;--hive:#c8c8c8;--cell:#3fc1a8;--cellfill:#1d4a42;--twin:#9a9a9a;--tile:#24272b}}
:root[data-theme="dark"]{--bg:#15171a;--fg:#e8e8e8;--muted:#a0a0a0;--line:#333;--hive:#c8c8c8;--cell:#3fc1a8;--cellfill:#1d4a42;--twin:#9a9a9a;--tile:#24272b}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.4 system-ui,sans-serif}
main{max-width:1100px;margin:0 auto;padding:12px 16px}
.banner{color:#fff;font-weight:700;padding:6px 10px;border-radius:4px;text-align:center}
.row{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:10px 0}
select,button,input{font:inherit}
canvas{width:100%;height:auto;border:1px solid var(--line);border-radius:4px;background:var(--bg)}
.hud{font-family:ui-monospace,Consolas,monospace;font-size:13px;white-space:pre-wrap;color:var(--fg)}
.note{color:var(--muted);font-size:12px}
</style></head><body><main>
<div id="banner" class="banner"></div>
<div class="row"><label>Shot <select id="sel"></select></label>
<button id="play">Pause</button><label>slow motion ×<input id="slow" type="number" min="1" max="100" value="15" style="width:4em"></label>
<input id="scrub" type="range" min="0" max="1000" value="0" style="flex:1;min-width:160px"></div>
<canvas id="cv" width="1600" height="900"></canvas>
<div class="hud" id="hud"></div>
<p class="note" id="note"></p>
</main>
<script>
const D = __DATA__;
const $ = id => document.getElementById(id);
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const demo = D.meta.source === "demo";
$("banner").textContent = D.meta.banner; $("banner").style.background = demo ? css("--demo") : css("--banner");
$("note").textContent = (D.meta.notes || "") + " Side view in the HIVE tipping plane; ball and HIVE to scale; the spin marker turns at the true spin rate slowed by the same factor as time.";
D.shots.forEach((s,i)=>{const o=document.createElement("option");o.value=i;o.textContent=s.id+" — "+s.title;$("sel").appendChild(o)});
let cur=0, t=0, playing=true, last=null;
function interp(T, A, tm){ if(tm<=T[0]) return A[0]; const n=T.length; if(tm>=T[n-1]) return A[n-1];
  let lo=0,hi=n-1; while(hi-lo>1){const m=(lo+hi)>>1; if(T[m]<=tm) lo=m; else hi=m;}
  const f=(tm-T[lo])/(T[hi]-T[lo]); return A[lo]+f*(A[hi]-A[lo]); }
function outText(o){return o==="clean"?"CLEAN ENTRY":o==="rim-assisted"?"RIM-ASSISTED ENTRY":o.startsWith("hit:")?"HITS "+o.slice(4):"MISS";}
function draw(){
  const s=D.shots[cur], H=D.hives[s.pose], cv=$("cv"), g=cv.getContext("2d");
  const tEnd=Math.max(s.t[s.t.length-1], s.twin.t[s.twin.t.length-1]);
  const xs=s.x.concat(s.twin.x, H.seg.flatMap(q=>[q[0],q[2]])), zs=s.z.concat(s.twin.z);
  let x0=Math.min(...xs)-450, x1=Math.max(...xs)+300, z1=Math.max(...zs)+250, z0=-80;
  const sc=Math.min(cv.width/(x1-x0), cv.height/(z1-z0)); const ox=(cv.width-(x1-x0)*sc)/2;
  const P=(x,z)=>[ox+(x-x0)*sc, cv.height-(z-z0)*sc];
  g.fillStyle=css("--bg"); g.fillRect(0,0,cv.width,cv.height);
  g.fillStyle=css("--tile"); const [,gy]=P(0,0); g.fillRect(0,gy,cv.width,cv.height-gy);
  if(H.inside.length){g.fillStyle=css("--cellfill"); g.beginPath(); H.inside.forEach((p,i)=>{const [a,b]=P(p[0],p[1]); i?g.lineTo(a,b):g.moveTo(a,b)}); g.closePath(); g.fill();}
  H.seg.forEach((q,i)=>{ const up=H.up.includes(i), pr=H.proj.includes(i);
    g.strokeStyle=up?css("--cell"):pr?css("--twin"):css("--hive"); g.lineWidth=up?6:pr?1.5:4; g.setLineDash(pr?[3,5]:[]); g.lineCap="round";
    g.beginPath(); g.moveTo(...P(q[0],q[1])); g.lineTo(...P(q[2],q[3])); g.stroke(); });
  g.setLineDash([]);
  const tm=Math.min(t,tEnd);
  function path(T,X,Z,col,dash){g.strokeStyle=col; g.lineWidth=3; g.setLineDash(dash); g.beginPath(); let k=0;
    for(let i=0;i<T.length && T[i]<=tm;i++){const [a,b]=P(X[i],Z[i]); k?g.lineTo(a,b):g.moveTo(a,b); k++;}
    const [a,b]=P(interp(T,X,tm),interp(T,Z,tm)); g.lineTo(a,b); g.stroke(); g.setLineDash([]);}
  path(s.twin.t,s.twin.x,s.twin.z,css("--twin"),[10,8]); path(s.t,s.x,s.z,css("--trail"),[]);
  const r=s.r*sc;
  const [wx,wz]=P(interp(s.twin.t,s.twin.x,tm),interp(s.twin.t,s.twin.z,tm));
  g.strokeStyle=css("--twin"); g.lineWidth=2; g.beginPath(); g.arc(wx,wz,r,0,7); g.stroke();
  const [bx,bz]=P(interp(s.t,s.x,tm),interp(s.t,s.z,tm)); const ang=interp(s.t,s.a,tm)/1000;
  g.fillStyle=css("--ball"); g.strokeStyle="#6b5300"; g.beginPath(); g.arc(bx,bz,Math.max(r,4),0,7); g.fill(); g.stroke();
  const ex=Math.cos(ang)*Math.max(r,4), ez=Math.sin(ang)*Math.max(r,4);
  g.beginPath(); g.moveTo(bx-ex,bz+ez); g.lineTo(bx+ex,bz-ez); g.stroke(); g.fillStyle="#c62828"; g.beginPath(); g.arc(bx+ex,bz-ez,2.5,0,7); g.fill();
  if(demo){g.save(); g.translate(cv.width/2,cv.height/2); g.rotate(-0.45); g.fillStyle="rgba(198,40,40,0.2)"; g.font="bold 64px system-ui"; g.textAlign="center"; g.fillText(D.meta.banner,0,0); g.restore();}
  const sp=Math.hypot(interp(s.t,s.vx,tm),interp(s.t,s.vz,tm))/1000, am=Math.hypot(interp(s.t,s.amx,tm),interp(s.t,s.amz,tm))/1000;
  const done=t>=s.t[s.t.length-1], tdone=t>=s.twin.t[s.twin.t.length-1];
  $("hud").textContent=`${s.id}: ${s.side} side, pose ${s.pose}, aero set ${s.aero_set}\nrelease x=${(s.release[0]/1000).toFixed(2)} m z=${(s.release[1]/1000).toFixed(2)} m (assumed)   v=${s.v} m/s   elev=${s.elev_deg}°   spin ${s.spin_rpm} rpm backspin (S=${s.S})\n`+
    `t=${(tm/1000).toFixed(3)} s   speed ${sp.toFixed(2)} m/s   spin ${Math.round(interp(s.t,s.rpm,tm))} rpm   Magnus accel ${am.toFixed(2)} m/s² (${(am/9.80665).toFixed(2)} g)   mid-air reversal: ${s.horizontal_reversal?"YES":"no"}\n`+
    `outcome: ${done?outText(s.outcome):"in flight…"}   ·   no-spin twin: ${tdone?outText(s.twin.outcome):"in flight…"}`;
  $("scrub").value=Math.round(1000*tm/tEnd);
}
function loop(ts){ const s=D.shots[cur]; const tEnd=Math.max(s.t[s.t.length-1], s.twin.t[s.twin.t.length-1]);
  if(playing && last!==null){ t+= (ts-last)/Math.max(1,+$("slow").value); if(t>tEnd+1500/Math.max(1,+$("slow").value)) t=0; }
  last=ts; draw(); requestAnimationFrame(loop); }
$("sel").onchange=e=>{cur=+e.target.value; t=0;};
$("play").onclick=()=>{playing=!playing; $("play").textContent=playing?"Pause":"Play";};
$("scrub").oninput=e=>{const s=D.shots[cur]; const tEnd=Math.max(s.t[s.t.length-1], s.twin.t[s.twin.t.length-1]); t=tEnd*e.target.value/1000; playing=false; $("play").textContent="Play";};
requestAnimationFrame(loop);
</script></body></html>
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("shots", nargs="?", default=os.path.join(VIZ, "shots.json"))
    ap.add_argument("--out", help="default: <shots dir>/web_data.json")
    ap.add_argument("--dt-ms", type=float, default=10.0)
    ap.add_argument("--html", help="also write a self-contained canvas replay page here")
    a = ap.parse_args(argv)
    with open(a.shots, encoding="utf-8") as fh:
        doc = json.load(fh)
    web = export(doc, a.dt_ms)
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.shots)), "web_data.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(web, fh, separators=(",", ":"), ensure_ascii=False)
    print(f"[export_web] wrote {out} ({os.path.getsize(out) / 1e3:.0f} kB, {len(web['shots'])} shots)")
    if a.html:
        page = HTML.replace("__DATA__", json.dumps(web, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/"))
        with open(a.html, "w", encoding="utf-8") as fh:
            fh.write(page)
        print(f"[export_web] wrote {a.html} ({os.path.getsize(a.html) / 1e3:.0f} kB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
