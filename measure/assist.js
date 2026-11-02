/* POLLEN Measure assist: automatic ball tracking, robot telemetry import and the shot log for the Shot Lab.
   The pure helpers (telemetry parsing, launch-dip detection) run under node for the tests; the page part hooks
   into measure.js through window.PollenMeasureUI (S.api, S.onDraw, S.onSeed). Nothing leaves the browser: the
   shot log and telemetry are kept in this browser's localStorage only. */
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else {
    root.PollenAssist = api;
    if (typeof document !== "undefined") {
      const go = function () { if (root.PollenMeasureUI && document.getElementById("auto-bar")) api.ui(root.PollenMeasureUI); };
      if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", go); else go();
    }
  }
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  const WHEEL_D = 0.098, LOG_KEY = "pollen.shotlog.v1", TEL_KEY = "pollen.telemetry.v1";

  // ---- telemetry text -> columns
  function parseTelemetry(text) {
    const lines = String(text || "").split(/\r?\n/).map(function (l) { return l.trim(); })
      .filter(function (l) { return l && !/^(#|\/\/)/.test(l); });
    if (!lines.length) return { cols: [], rows: [] };
    const cnt = function (ch) { return lines[0].split(ch).length - 1; };
    const delim = [",", "\t", ";", "|"].reduce(function (b, ch) { return cnt(ch) > cnt(b) ? ch : b; }, ",");
    const split = function (l) { return l.split(delim).map(function (s) { return s.trim().replace(/^"|"$/g, ""); }); };
    let cols = null; const rows = [];
    lines.forEach(function (l) {
      const f = split(l);
      const nums = f.map(function (s) { return s === "" ? NaN : Number(s); });
      if (!cols && nums.some(function (v, i) { return !isFinite(v) && f[i] !== ""; })) { cols = f; return; }
      if (nums.filter(isFinite).length >= 2) rows.push(nums);
    });
    const n = rows.reduce(function (m, r) { return Math.max(m, r.length); }, 0);
    if (!cols) cols = Array.from({ length: n }, function (_, i) { return "col" + (i + 1); });
    return { cols: cols, rows: rows };
  }

  const ROLE_RX = {
    time: /^(t|time|timestamp|time_?s|time_?ms|sec|secs|seconds|ms|millis|elapsed|runtime)\b/i,
    target: /target|set ?point|goal|command(ed)?_?(rpm|vel)/i,
    rpm: /rpm|vel|velocity|speed|tps|ticks/i,
    volts: /volt|vbat|batt|voltage|^v$/i,
    power: /power|duty|output|^pwr|^cmd$/i,
    hood: /hood|servo|pitch|angle/i
  };
  function detectColumns(cols) {
    const out = { time: -1, target: -1, rpm: -1, volts: -1, power: -1, hood: -1 }, used = {};
    ["time", "target", "volts", "power", "hood", "rpm"].forEach(function (role) {
      for (let i = 0; i < cols.length; i++) if (!used[i] && ROLE_RX[role].test(cols[i])) { out[role] = i; used[i] = 1; break; }
    });
    if (out.time < 0 && cols.length) out.time = 0;
    return out;
  }

  // time column -> seconds from the first row (ms / ns guessed from the name or the step)
  function toSeconds(t, name) {
    const v = t.filter(isFinite);
    if (v.length < 2) return t.slice();
    // rows may be out of order: step = median |difference|, zero = the earliest time
    const d = []; for (let i = 1; i < v.length; i++) d.push(Math.abs(v[i] - v[i - 1]));
    d.sort(function (a, b) { return a - b; });
    const md = d[d.length >> 1], t0 = Math.min.apply(null, v);
    let k = 1;
    if (/ns|nano/i.test(name || "") || md > 1e5) k = 1e-9;
    else if (/ms|milli/i.test(name || "") || md > 2) k = 1e-3;
    return t.map(function (x) { return (x - t0) * k; });
  }

  function median(a) {
    const s = a.filter(isFinite).sort(function (x, y) { return x - y; });
    if (!s.length) return NaN;
    const m = s.length >> 1;
    return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
  }
  function between(t, a, b) { const o = []; for (let i = 0; i < t.length; i++) if (t[i] >= a && t[i] < b) o.push(i); return o; }

  // launch events: the wheel speed falls when a ball goes through. An event is a run of samples more than
  // minDrop below the running peak of the previous 0.15 s; launch = steepest fall just before its minimum.
  function findDips(t, rpm, opts) {
    opts = opts || {};
    const minDrop = opts.minDrop || 0.03, n = t.length, ev = [];
    let i = 0;
    const peakBefore = function (k) { let m = -Infinity; for (let j = k - 1; j >= 0 && t[k] - t[j] <= 0.15; j--) if (rpm[j] > m) m = rpm[j]; return m; };
    while (i < n) {
      const pk = peakBefore(i);
      if (isFinite(pk) && pk > 0 && (pk - rpm[i]) / pk > minDrop) {
        const s = i; let mi = i;
        while (i < n && rpm[i] < pk * (1 - minDrop * 0.5)) { if (rpm[i] < rpm[mi]) mi = i; i++; }
        let li = s, best = 0;   // steepest descent between the event start (minus 50 ms) and the minimum
        for (let k = Math.max(1, s - 1); k <= mi; k++) {
          if (t[s] - t[k] > 0.05) continue;
          const sl = (rpm[k] - rpm[k - 1]) / Math.max(t[k] - t[k - 1], 1e-6);
          if (sl < best) { best = sl; li = k; }
        }
        const pre = median(between(t, t[s] - 0.2, t[s] - 0.02).map(function (k) { return rpm[k]; }));
        const ref = isFinite(pre) ? pre : pk;
        let rec = NaN;
        for (let k = mi; k < n; k++) if (rpm[k] >= ref * 0.98) { rec = t[k] - t[li]; break; }
        ev.push({ i: li, t: t[li], tMin: t[mi], pre: ref, min: rpm[mi], drop: (ref - rpm[mi]) / ref, recover: rec, s: s });
      } else i++;
    }
    return ev;
  }

  // values over the steady window just before a launch (median), for the shot log
  function launchReadout(tel, ev) {
    const idx = between(tel.t, ev.t - 0.2, ev.t - 0.02);
    const at = function (arr) { return arr ? median(idx.map(function (k) { return arr[k]; })) : NaN; };
    return { rpm: at(tel.rpm), target: at(tel.target), volts: at(tel.volts), power: at(tel.power), hood: at(tel.hood),
      drop: ev.drop, recover: ev.recover, t: ev.t };
  }

  // parsed columns + chosen roles/units -> {t, rpm, target, volts, power, hood} arrays (wheel rpm)
  function buildTel(parsed, roles, units) {
    const col = function (k) { return k >= 0 ? parsed.rows.map(function (r) { return r[k]; }) : null; };
    const conv = function (a) {
      if (!a) return null;
      const g = units.ratio > 0 ? units.ratio : 1;
      return a.map(function (v) { return (units.speed === "tps" ? v / (units.tpr || 28) * 60 : v) * g; });
    };
    const t = toSeconds(col(roles.time) || parsed.rows.map(function (_, i) { return i * 0.02; }), parsed.cols[roles.time]);
    const out = { t: t, rpm: conv(col(roles.rpm)), target: conv(col(roles.target)), volts: col(roles.volts), power: col(roles.power), hood: col(roles.hood) };
    // drop rows without a time or a speed, keep order by time
    const keep = []; for (let i = 0; i < t.length; i++) if (isFinite(t[i]) && (!out.rpm || isFinite(out.rpm[i]))) keep.push(i);
    keep.sort(function (a, b) { return t[a] - t[b]; });
    Object.keys(out).forEach(function (k) { if (out[k]) out[k] = keep.map(function (i) { return out[k][i]; }); });
    return out;
  }

  // synthetic telemetry for the demo: 50 Hz, a wheel held near targetRpm with battery sag and two launch dips
  function demoTelemetry(o) {
    o = o || {};
    const target = o.rpm || 3250, launches = o.launches || [1.2, 3.4], rows = ["time_ms,target_rpm,wheel_rpm,battery_v,power"];
    let s = 12345;
    const rnd = function () { s = (s * 1103515245 + 12345) & 0x7fffffff; return s / 0x7fffffff - 0.5; };
    for (let k = 0; k <= 250; k++) {
      const t = k * 0.02;
      let rpm = target * (1 - Math.exp(-(t + 0.6) / 0.25)), v = 12.55 - 0.35 * (rpm / target), dip = 0;
      launches.forEach(function (L) { if (t >= L) dip += 0.13 * Math.exp(-(t - L) / 0.12) * Math.min(1, (t - L) / 0.03 + 0.2); });
      rpm *= 1 - dip; v -= 0.9 * dip;
      const pw = Math.min(1, (target + 50) / (480 * v));
      rows.push([Math.round(t * 1000), target, (rpm + 12 * rnd()).toFixed(1), (v + 0.01 * rnd()).toFixed(3), pw.toFixed(3)].join(","));
    }
    return rows.join("\n");
  }

  function loadJSON(key, dflt) { try { const s = localStorage.getItem(key); return s ? JSON.parse(s) : dflt; } catch (_) { return dflt; } }
  function saveJSON(key, v) { try { localStorage.setItem(key, JSON.stringify(v)); return true; } catch (_) { return false; } }

  // ================= page =================
  function ui(S) {
    const $ = function (id) { return document.getElementById(id); };
    const A = S.api, T = self.PollenTracker;
    const esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
    const f1 = function (v, d) { return isFinite(v) ? Number(v).toFixed(d) : "-"; };

    // ---------- auto-track
    let job = null, undo = null;
    function frameGetter(sh, k) {
      const W = Math.max(1, Math.round(sh.w * k)), H = Math.max(1, Math.round(sh.h * k));
      const c = document.createElement("canvas"); c.width = W; c.height = H;
      const g = c.getContext("2d", { willReadFrequently: true });
      const grab = function () { const d = g.getImageData(0, 0, W, H); return { data: d.data, w: W, h: H }; };
      const src = sh.src;
      if (src.kind === "demo") return function (f) { g.setTransform(k, 0, 0, k, 0, 0); src.draw(g, f); g.setTransform(1, 0, 0, 1, 0, 0); return grab(); };
      if (src.kind === "images") return function (f) {
        const img = src.imgs[f];
        if (!img) return null;
        return new Promise(function (res) {
          const go = function () { g.drawImage(img, 0, 0, W, H); res(grab()); };
          if (img.complete && img.naturalWidth) go(); else { img.onload = go; img.onerror = function () { res(null); }; }
        });
      };
      // video: a second element, so the page's own frame view is left alone
      const v = document.createElement("video");
      v.muted = true; v.playsInline = true; v.preload = "auto"; v.src = src.el.currentSrc || src.el.src;
      const ready = new Promise(function (res) { if (v.readyState >= 1) res(); else v.onloadedmetadata = function () { res(); }; });
      return async function (f) {
        await ready;
        const tt = Math.min((f + 0.5) / sh.fileFps, Math.max(0, v.duration - 1e-3));
        await new Promise(function (res) {
          const done = function () { v.removeEventListener("seeked", done); res(); };
          v.addEventListener("seeked", done);
          try { v.currentTime = tt; } catch (_) { res(); }
          setTimeout(done, 1500);
        });
        g.drawImage(v, 0, 0, W, H);
        return grab();
      };
    }
    async function bestRadius(get, f, seed, bgFrames) {
      // no scale: try a few radii and keep the one the blob agrees with
      const fr = await get(f), bg = T.background(bgFrames), col = T.colourAt(fr, seed[0], seed[1], 4);
      let best = null;
      [3, 5, 8, 12, 18, 26].forEach(function (r) {
        const b = T.findBall(fr, bg, { cx: seed[0], cy: seed[1], win: 3 * r, r: r, col: col });
        if (b && (!best || b.conf > best.conf)) best = b;
      });
      return best ? Math.max(2, best.r) : 6;
    }
    async function autoTrack(seedFull) {
      const sh = A.cur(), T0 = performance.now();
      if (!sh.src || !sh.nFrames) { A.setStatus("Load a video, image sequence or the demo first."); return; }
      let k = Math.min(1, 640 / sh.w), get = frameGetter(sh, k), seed = [seedFull[0] * k, seedFull[1] * k];
      const f0 = S.frame;
      const mpp = A.mPerPx(), dir = $("autodir").value;
      job = { stop: false };
      $("autotrack").disabled = true; $("autostop").disabled = false;
      const say = function (m) { $("auto-o").textContent = m; };
      try {
        let r;
        if (mpp) r = A.ballP().radius / mpp * k;
        else {
          const idx = []; for (let i = 0; i < 9; i++) idx.push(Math.round((sh.nFrames - 1) * i / 8));
          const bgf = []; for (const i of idx) { const fr = await get(i); if (fr) bgf.push(fr); }
          r = await bestRadius(get, f0, seed, bgf);
        }
        // frames are shrunk for speed, but a ball under 8 px radius is mostly anti-aliased edge: track at a larger scale
        if (r < 8 && k < 1) {
          const k2 = Math.min(1, k * 8 / r);
          r *= k2 / k; seed = [seedFull[0] * k2, seedFull[1] * k2]; k = k2; get = frameGetter(sh, k);
        }
        const runs = [], spans = [];
        if (dir !== "back") spans.push([f0, sh.nFrames - 1, 1]);
        if (dir !== "fwd") spans.push([f0, 0, -1]);
        for (let s = 0; s < spans.length && !job.stop; s++) {
          const sp = spans[s];
          const res = await T.track(get, { start: sp[0], end: sp[1], step: sp[2], seed: seed, r: r,
            shouldStop: function () { return job.stop; },
            onProgress: function (q) { say((sp[2] > 0 ? "forward " : "backward ") + Math.round(q * 100) + " % …"); } });
          runs.push(res);
        }
        const all = {}; runs.forEach(function (res) { res.pts.forEach(function (p) { all[p.f] = p; }); });
        const pts = T.refine(Object.keys(all).map(Number).sort(function (a, b) { return a - b; }).map(function (f) { return all[f]; }));
        if (pts.length < 3) { say("Tracker lost the ball at once (" + runs.map(function (x) { return x.stopped; }).join(", ") + "). Click nearer its centre, or set the scale so the size is known."); return; }
        undo = { shot: S.shot, pts: Object.assign({}, sh.pts), conf: Object.assign({}, sh.conf) };
        sh.pts = {}; sh.conf = {};
        let low = 0;
        pts.forEach(function (p) { sh.pts[p.f] = [p.px / k, p.py / k]; sh.conf[p.f] = p.conf; if (p.conf < 0.5) low++; });
        sh.fit = null;
        $("autoundo").disabled = false;
        say(pts.length + " points, frames " + pts[0].f + "–" + pts[pts.length - 1].f + " (" + runs.map(function (x) { return x.stopped; }).join(" / ") + "), " + low + " low-confidence in amber, " +
          ((performance.now() - T0) / 1000).toFixed(1) + " s. Ball radius " + (r / k).toFixed(1) + " px" + (mpp ? " (from the scale)" : " (estimated: set the scale for better)") + ". Check the points before fitting.");
        A.refresh();
      } catch (e) { say("Auto-track failed: " + e.message); }
      finally { job = null; $("autotrack").disabled = false; $("autostop").disabled = true; }
    }
    S.onSeed = function (f) { autoTrack(f); };
    $("autotrack").onclick = function () {
      if (!A.cur().src) { A.setStatus("Load a video, image sequence or the demo first."); return; }
      A.setMode("seed"); $("auto-o").textContent = "Click the ball once on this frame.";
    };
    $("autostop").onclick = function () { if (job) job.stop = true; };
    $("autoundo").onclick = function () {
      if (!undo) return;
      const sh = S.shots[undo.shot]; sh.pts = undo.pts; sh.conf = undo.conf; sh.fit = null; undo = null;
      $("autoundo").disabled = true; $("auto-o").textContent = "Auto-track undone."; A.refresh();
    };

    // ---------- telemetry
    const TS = { parsed: null, tel: null, offset: 0, events: [] };
    const ROLES = ["time", "rpm", "target", "volts", "power", "hood"];
    function roleSelects() {
      const det = detectColumns(TS.parsed.cols);
      ROLES.forEach(function (role) {
        const sel = $("tc-" + role);
        sel.innerHTML = '<option value="-1">(none)</option>' + TS.parsed.cols.map(function (c, i) { return '<option value="' + i + '">' + esc(c) + "</option>"; }).join("");
        sel.value = String(det[role]);
      });
      const rn = TS.parsed.cols[det.rpm] || "";
      $("tel-speed").value = /tps|tick/i.test(rn) ? "tps" : "rpm";
    }
    function rebuild() {
      if (!TS.parsed) return;
      const roles = {}; ROLES.forEach(function (r) { roles[r] = +$("tc-" + r).value; });
      TS.tel = buildTel(TS.parsed, roles, { speed: $("tel-speed").value, tpr: +$("tel-tpr").value || 28, ratio: +$("tel-ratio").value || 1 });
      TS.events = TS.tel.rpm ? findDips(TS.tel.t, TS.tel.rpm) : [];
      telDraw();
    }
    function loadTelText(text, name) {
      TS.parsed = parseTelemetry(text);
      if (!TS.parsed.rows.length) { $("tel-o").textContent = "No numeric rows found in " + name + "."; return; }
      roleSelects(); rebuild();
      $("tel-o").textContent = name + ": " + TS.parsed.rows.length + " rows, " + TS.parsed.cols.length + " columns, " + TS.events.length + " launch dip(s) found. Check the column choices.";
      $("tel-main").hidden = false;
    }
    function launchTime() {   // video time of the first tracked frame of this shot, else the current frame
      const sh = A.cur(), fr = Object.keys(sh.pts).map(Number).sort(function (a, b) { return a - b; });
      return (fr.length ? fr[0] : S.frame) / sh.fps;
    }
    function nearestEvent(tTel) {
      let best = null;
      TS.events.forEach(function (e) { if (!best || Math.abs(e.t - tTel) < Math.abs(best.t - tTel)) best = e; });
      return best;
    }
    function telDraw() {
      const svg = $("tel-chart"), tel = TS.tel;
      if (!tel || !tel.rpm) { svg.innerHTML = ""; $("tel-read").innerHTML = ""; return; }
      const W = 640, H = 200, L = 46, Rm = 46, Tp = 10, B = 24, t = tel.t, n = t.length;
      const t0 = t[0], t1 = t[n - 1] || 1;
      const rr = tel.rpm.concat(tel.target || []).filter(isFinite), r0 = Math.min.apply(null, rr), r1 = Math.max.apply(null, rr);
      const X = function (v) { return L + (v - t0) / (t1 - t0 || 1) * (W - L - Rm); };
      const Y = function (v) { return Tp + (1 - (v - r0) / (r1 - r0 || 1)) * (H - Tp - B); };
      const vv = (tel.volts || []).filter(isFinite), v0 = vv.length ? Math.min.apply(null, vv) : 0, v1 = vv.length ? Math.max.apply(null, vv) : 1;
      const YV = function (v) { return Tp + (1 - (v - v0) / (v1 - v0 || 1)) * (H - Tp - B); };
      const line = function (a, fy) { let d = ""; for (let i = 0; i < n; i++) if (isFinite(a[i])) d += (d ? "L" : "M") + X(t[i]).toFixed(1) + " " + fy(a[i]).toFixed(1); return d; };
      let h = "";
      for (let k = 0; k <= 4; k++) { const y = Tp + k * (H - Tp - B) / 4; h += '<line class="grid" x1="' + L + '" x2="' + (W - Rm) + '" y1="' + y + '" y2="' + y + '"/>'; }
      h += '<text class="ax" x="' + (L - 4) + '" y="' + (Tp + 4) + '" text-anchor="end">' + r1.toFixed(0) + '</text><text class="ax" x="' + (L - 4) + '" y="' + (H - B) + '" text-anchor="end">' + r0.toFixed(0) + "</text>";
      h += '<text class="ax" x="' + L + '" y="' + (H - 6) + '">' + t0.toFixed(1) + ' s</text><text class="ax" x="' + (W - Rm) + '" y="' + (H - 6) + '" text-anchor="end">' + t1.toFixed(1) + " s</text>";
      if (tel.volts && vv.length) {
        h += '<path d="' + line(tel.volts, YV) + '" fill="none" stroke="var(--cal)" stroke-width="1.2" opacity=".8"/>';
        h += '<text class="ax" x="' + (W - Rm + 4) + '" y="' + (Tp + 4) + '" fill="var(--cal)">' + v1.toFixed(2) + ' V</text><text class="ax" x="' + (W - Rm + 4) + '" y="' + (H - B) + '">' + v0.toFixed(2) + " V</text>";
      }
      if (tel.target) h += '<path d="' + line(tel.target, Y) + '" fill="none" stroke="var(--twin)" stroke-width="1" stroke-dasharray="4 4"/>';
      h += '<path d="' + line(tel.rpm, Y) + '" fill="none" stroke="var(--pollen)" stroke-width="1.6"/>';
      TS.events.forEach(function (e) { h += '<line x1="' + X(e.t) + '" x2="' + X(e.t) + '" y1="' + Tp + '" y2="' + (H - B) + '" stroke="var(--hit)" stroke-width="1" stroke-dasharray="2 3"/>'; });
      const tc = S.frame / A.cur().fps + TS.offset;
      if (tc >= t0 && tc <= t1) h += '<line x1="' + X(tc) + '" x2="' + X(tc) + '" y1="' + Tp + '" y2="' + (H - B) + '" stroke="var(--fg)" stroke-width="1.5"/>';
      svg.setAttribute("viewBox", "0 0 " + W + " " + H);
      svg.innerHTML = h;
      const e = nearestEvent(launchTime() + TS.offset);
      if (!e) { $("tel-read").innerHTML = '<p class="hint">No launch dip found (no drop of 3 % or more in the wheel speed).</p>'; return; }
      const r = launchReadout(TS.tel, e);
      TS.read = r;
      $("tel-read").innerHTML = '<table class="res"><tbody>' +
        "<tr><td>Wheel speed before launch</td><td>" + f1(r.rpm, 0) + ' rpm</td><td><span class="lab">user</span></td></tr>' +
        (isFinite(r.target) ? "<tr><td>Target speed</td><td>" + f1(r.target, 0) + ' rpm</td><td><span class="lab">user</span></td></tr>' : "") +
        (isFinite(r.volts) ? "<tr><td>Battery before launch</td><td>" + f1(r.volts, 2) + ' V</td><td><span class="lab">user</span></td></tr>' : "") +
        (isFinite(r.power) ? "<tr><td>Motor command</td><td>" + f1(r.power, 3) + '</td><td><span class="lab">user</span></td></tr>' : "") +
        "<tr><td>Speed drop at launch</td><td>" + f1(r.drop * 100, 1) + ' %</td><td><span class="lab">derived</span></td></tr>' +
        "<tr><td>Back within 2 % after</td><td>" + (isFinite(r.recover) ? f1(r.recover * 1000, 0) + " ms" : "not in the log") + '</td><td><span class="lab">derived</span></td></tr>' +
        "<tr><td>Launch in the log at</td><td>" + f1(r.t, 3) + " s (video " + f1(r.t - TS.offset, 3) + ' s)</td><td><span class="lab">derived</span></td></tr></tbody></table>';
    }
    S.onDraw = function () { if (TS.tel) telDraw(); };
    $("tel-file").onchange = function (e) {
      const f = e.target.files && e.target.files[0]; if (!f) return;
      const rd = new FileReader(); rd.onload = function () { loadTelText(rd.result, f.name); }; rd.readAsText(f); e.target.value = "";
    };
    $("tel-demo").onclick = function () { loadTelText(demoTelemetry(), "synthetic demo log (ASSUMED, not a robot)"); };
    ROLES.forEach(function (r) { $("tc-" + r).onchange = rebuild; });
    ["tel-speed", "tel-tpr", "tel-ratio"].forEach(function (id) { $(id).onchange = rebuild; });
    $("tel-off").onchange = function () { TS.offset = parseFloat($("tel-off").value) || 0; telDraw(); };
    $("tel-sync").onclick = function () {
      if (!TS.events.length) { $("tel-o").textContent = "No launch dip to sync on."; return; }
      const e = TS.events.reduce(function (b, x) { return x.drop > b.drop ? x : b; }, TS.events[0]);
      TS.offset = e.t - launchTime(); $("tel-off").value = TS.offset.toFixed(3);
      $("tel-o").textContent = "Synced: the deepest dip (" + f1(e.drop * 100, 1) + " %, log " + f1(e.t, 3) + " s) is put at the first tracked frame of shot " + S.shot + ". Check it by stepping frames.";
      telDraw();
    };
    $("tel-use").onclick = function () {
      const r = TS.read, sh = A.cur(); if (!r) return;
      sh.meta.wheel_rpm = isFinite(r.rpm) ? r.rpm.toFixed(0) : sh.meta.wheel_rpm;
      sh.meta.volts = isFinite(r.volts) ? r.volts.toFixed(2) : ""; sh.meta.power = isFinite(r.power) ? r.power.toFixed(3) : "";
      sh.meta.hood = isFinite(r.hood) ? String(r.hood) : ""; sh.meta.target_rpm = isFinite(r.target) ? r.target.toFixed(0) : "";
      $("wrpm").value = sh.meta.wheel_rpm || "";
      $("tel-o").textContent = "Shot " + S.shot + ": wheel " + (sh.meta.wheel_rpm || "-") + " rpm" + (sh.meta.volts ? ", battery " + sh.meta.volts + " V" : "") + " from the log (user).";
      A.refresh();
    };
    $("tel-send").onclick = function () {
      const tel = TS.tel; if (!tel || !tel.rpm) return;
      const step = Math.max(1, Math.ceil(tel.t.length / 6000)), rows = [];
      for (let i = 0; i < tel.t.length; i += step) rows.push({ t: tel.t[i], rpm: tel.rpm[i], volts: tel.volts ? tel.volts[i] : null, power: tel.power ? tel.power[i] : null, target: tel.target ? tel.target[i] : null });
      $("tel-o").textContent = saveJSON(TEL_KEY, { saved: new Date().toISOString(), rows: rows }) ? rows.length + " telemetry rows saved for the Shot Lab (this browser only)." : "This browser blocked local storage: use the Shot Lab's own import.";
    };

    // ---------- shot log
    function logShot() {
      const sh = A.cur(), fit = sh.fit;
      if (!fit) { $("log-o").textContent = "Fit shot " + S.shot + " first."; return; }
      const log = loadJSON(LOG_KEY, []), num = function (s) { const v = parseFloat(s); return isFinite(v) ? v : null; };
      log.push({ id: Date.now(), shot: S.shot, kind: sh.kind, v: +fit.v0.toFixed(3), theta: +fit.theta_deg.toFixed(2),
        wheel_rpm: num(sh.meta.wheel_rpm), volts: num(sh.meta.volts), power: num(sh.meta.power), hood: num(sh.meta.hood),
        cd: S.shots.A.fit ? +S.shots.A.fit.value.Cd.toFixed(3) : null, source: sh.name || "", label: "derived" });
      $("log-o").textContent = saveJSON(LOG_KEY, log) ? "Shot " + S.shot + " added: v " + fit.v0.toFixed(2) + " m/s, " + fit.theta_deg.toFixed(1) + "°" +
        (num(sh.meta.wheel_rpm) ? ", wheel " + sh.meta.wheel_rpm + " rpm" : " (no wheel rpm: the exit-speed fit needs one)") + ". The log has " + log.length + " shot(s)." : "This browser blocked local storage.";
    }
    $("log-add").onclick = logShot;
    if (/auto/.test(location.hash)) setTimeout(function () {   // check hook: #demo-auto tracks shot A from frame 60
      const p = S.shots.A.pts[60]; if (!p) return;
      A.gotoFrame(60);
      autoTrack(p).then(function () { if (/check/.test(location.hash)) $("fitA").click(); });   // #demo-auto-check also fits A
    }, 300);
    if (/tel/.test(location.hash)) setTimeout(function () { $("tel-demo").onclick(); $("tel-sync").onclick(); }, 400);
  }

  return { parseTelemetry: parseTelemetry, detectColumns: detectColumns, toSeconds: toSeconds, findDips: findDips,
    launchReadout: launchReadout, buildTel: buildTel, demoTelemetry: demoTelemetry, median: median, ui: ui,
    LOG_KEY: LOG_KEY, TEL_KEY: TEL_KEY, WHEEL_D: WHEEL_D };
});
