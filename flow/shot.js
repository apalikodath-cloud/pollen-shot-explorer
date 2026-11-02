// Shot flow scene ("3D flow"): the explorer's shot path (physics.js integrate3D through solver.js shot()) with the CFD
// drawn around the ball as a general solution. At every moment of the flight the two library cases that bracket the
// ball's local spin ratio S(t) are crossfaded (each at the library speed nearest the ball's), the flow is rotated so
// the CFD free stream meets the ball as the air does, and speeds are coloured in m/s at the ball's local speed.
// The library is whatever flows/index.json lists; nothing here is tied to particular cases.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RunView, esc, cssVar, env, turbo } from './flowview.js';

THREE.Object3D.DEFAULT_UP.set(0, 0, 1);
const $ = (id) => document.getElementById(id);
const params = new URLSearchParams(location.search);
const BASE = (params.get('flows') || 'flows').replace(/\/+$/, '');
const FIELD_URL = params.get('field') || '../data/field/index.json';
const EMBED = params.get('embed') === '1';
const PS = window.PollenSolver, C = PS.constants;
const IN = 0.0254, D_M = 0.07112, R_M = D_M / 2;
const COL = { main: 0xf4c430, twin: 0xa9b4bf };   // explorer: POLLEN yellow for the backspin shot, grey for the twin
const SPIN_CAP = 2;       // drawn ball spin, revolutions per second of screen time at most (the real spin is far too fast to see)
const MAX_VIEWS = 6;      // loaded CFD cases kept per ball
if (EMBED) document.documentElement.classList.add('embed');

// ------------------------------------------------------------ renderer, camera
const canvas = $('gl');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, powerPreference: 'high-performance' });
const DPR = env.DPR;
renderer.setPixelRatio(DPR);
const camera = new THREE.PerspectiveCamera(40, 1, 0.01, 60);
camera.up.set(0, 0, 1);
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = false; controls.minDistance = 0.12; controls.maxDistance = 14; controls.zoomSpeed = 1.1;
const OVER = { pos: new THREE.Vector3(-3.9, -3.3, 2.4), tgt: new THREE.Vector3(0.1, 0.3, 0.8) };
camera.position.copy(OVER.pos); controls.target.copy(OVER.tgt);

const scene = new THREE.Scene();
scene.add(new THREE.HemisphereLight(0xffffff, 0x556070, 1.1));
const key = new THREE.DirectionalLight(0xffffff, 2.2); key.position.set(-2, -3, 5); scene.add(key);
scene.add(new THREE.DirectionalLight(0xbcd0ff, 0.6).translateX(2).translateY(2).translateZ(-1));
let BG = new THREE.Color(cssVar('--bg') || '#0b1015');

// ------------------------------------------------------------ field, HIVE
const line = (pts, color, op = 1) => new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts.map((p) => new THREE.Vector3(...p))), new THREE.LineBasicMaterial({ color, transparent: op < 1, opacity: op }));
function buildField(meta) {
  const g = new THREE.Group(); scene.add(g);
  const yc = (C.Y_LO + C.Y_HI) / 2, W = 2 * C.X_WALL, H = C.Y_HI - C.Y_LO;
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(W, H), new THREE.MeshStandardMaterial({ color: 0x59606c, roughness: 0.95 }));
  floor.position.set(0, yc, -0.001); g.add(floor);
  const grid = new THREE.GridHelper(Math.max(W, H), Math.round(Math.max(W, H) / 0.6096), 0x8a93a3, 0x7a8394);
  grid.rotation.x = Math.PI / 2; grid.position.set(0, yc, 0); grid.material.transparent = true; grid.material.opacity = 0.35; g.add(grid);
  const rect = (x0, x1, y0, y1, z, col, op) => g.add(line([[x0, y0, z], [x1, y0, z], [x1, y1, z], [x0, y1, z], [x0, y0, z]], col, op));
  rect(-C.X_WALL, C.X_WALL, C.Y_LO, C.Y_HI, 0.004, 0xe8ecf2);
  rect(-C.X_WALL, C.X_WALL, C.Y_LO, C.Y_HI, 0.3, 0xe8ecf2, 0.35);
  rect(-C.BASE_HX, C.BASE_HX, C.BASE_CY - C.BASE_HY, C.BASE_CY + C.BASE_HY, 0.006, 0xd4a017);      // A-frame base (CONFIRMED)
  rect(-C.OTHER_HIVE_X, C.OTHER_HIVE_X, C.OTHER_HIVE_Y[0], C.OTHER_HIVE_Y[1], 0.006, 0x9aa3b2, 0.7);  // other HIVE (ASSUMED box)
  // HIVE up/down cells: the s = 0 section (CONFIRMED CAD) extruded to the 3D-cell side walls
  const sec = meta.sections && (meta.sections['unfav_s0'] || meta.sections[Object.keys(meta.sections)[0]]);
  if (sec) {
    const sw = 0.254, pos = [], lp = [];
    sec.P0.forEach((a, i) => {
      const b = sec.P1[i];
      pos.push(a[0], -sw, a[1], b[0], -sw, b[1], a[0], sw, a[1], b[0], -sw, b[1], b[0], sw, b[1], a[0], sw, a[1]);
      for (const y of [-sw, sw]) lp.push(a[0], y, a[1], b[0], y, b[1]);
    });
    const gg = new THREE.BufferGeometry(); gg.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.add(new THREE.Mesh(gg, new THREE.MeshBasicMaterial({ color: 0xd4a017, transparent: true, opacity: 0.3, side: THREE.DoubleSide, depthWrite: false })));
    const lg = new THREE.BufferGeometry(); lg.setAttribute('position', new THREE.Float32BufferAttribute(lp, 3));
    g.add(new THREE.LineSegments(lg, new THREE.LineBasicMaterial({ color: 0xf2c94c })));
  }
}

// ------------------------------------------------------------ robot
// U.q: the explorer's full query (air, drag, wind, robot, lift, ...) when it drives this page; null = local defaults
const U = { x: -1.0, y: 0.2, hd: 0, h: 0.737, v: 6.5, th: 75, S: 1.0, tSim: 0, play: false, lastLegal: null,
  avg: params.get('avg') !== '0', q: null, vleg: 10 };
const robot = new THREE.Group();
{
  const L = 18 * IN;
  const body = new THREE.Mesh(new THREE.BoxGeometry(L, L, 0.22), new THREE.MeshStandardMaterial({ color: 0x2f6fdd, roughness: 0.6 }));
  body.position.z = 0.13; robot.add(body); robot.userData.body = body;
  const nose = new THREE.Mesh(new THREE.ConeGeometry(0.05, 0.12, 12), new THREE.MeshStandardMaterial({ color: 0xffd23f }));
  nose.rotation.z = -Math.PI / 2; nose.position.set(L / 2 + 0.02, 0, 0.13); robot.add(nose);
  const tur = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.3, 14), new THREE.MeshStandardMaterial({ color: 0x1b3f86 }));
  tur.rotation.x = Math.PI / 2; tur.position.z = 0.34; robot.add(tur);
  scene.add(robot);
}
const relMark = new THREE.Mesh(new THREE.SphereGeometry(0.012, 8, 6), new THREE.MeshBasicMaterial({ color: 0xffffff }));
scene.add(relMark);

let META = null;
const ZERO_MOVE = { along: 0, across: 0, wz: 0, d0: 0, lead: true };   // a (zero) move block selects the 3D path (physics.js integrate3D)
function nearestCase(S) {
  let best = null;
  for (const c of META.cases) {
    const d = Math.abs(c.S - S) + (c.var === 'nominal' ? 0 : 1e-3);
    if (!best || d < best.d) best = { d, c };
  }
  return best.c;
}
function qNow() {
  if (U.q) {
    const q = Object.assign({}, U.q, { x: U.x, y: U.y, h: U.h, S: U.S, meta: META._q });
    q.robot = Object.assign({}, U.q.robot || {}, { heading: U.hd });
    if (!q.move) q.move = ZERO_MOVE;
    if (!q.params) q.params = nearestCase(U.S).params;
    return q;
  }
  return { x: U.x, y: U.y, h: U.h, S: U.S, vu: 0.42, params: nearestCase(U.S).params, meta: META._q, air: { tC: 20, altM: 0, rh: 0 },
    drag: { model: 'const', spin: 0 }, wind: { along: 0, up: 0, side: 0 }, move: ZERO_MOVE,
    robot: { length: 18 * IN, width: 18 * IN, offset: [0, 0], heading: U.hd } };
}

// ------------------------------------------------------------ shot paths
// path record: positions, velocity (central difference), local speed ratio S(t) = S0 v0 exp(-k t) / |v|
function makePath(p, S0, k, w0) {
  const n = p.n, dt = p.dt, vx = new Float32Array(n), vy = new Float32Array(n), vz = new Float32Array(n), sp = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    const a = Math.max(0, i - 1), b = Math.min(n - 1, i + 1), d = (b - a) * dt || dt;
    vx[i] = (p.x[b] - p.x[a]) / d; vy[i] = (p.y[b] - p.y[a]) / d; vz[i] = (p.z[b] - p.z[a]) / d;
    sp[i] = Math.hypot(vx[i], vy[i], vz[i]);
  }
  const h0 = Math.hypot(vx[0], vy[0]) || 1, axis = new THREE.Vector3(vy[0] / h0, -vx[0] / h0, 0);  // backspin axis, fixed
  const v0 = sp[0];
  return { p, n, dt, T: (n - 1) * dt, vx, vy, vz, sp, axis, S0, k, v0, w0,
    Sloc: (i, t) => S0 * v0 * Math.exp(-k * t) / Math.max(sp[i], 0.05) };
}
const PATHS = { main: null, twin: null, verdict: null };
const pathLines = { main: null, twin: null };
// legend top in m/s: a round number at or above x
const RUNGS = [1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50];
const niceCeil = (x) => RUNGS.find((r) => r >= x - 1e-9) || Math.ceil(x / 10) * 10;
function rebuildShot() {
  const q = qNow();
  const pose = PS.pose(U.x, U.y, META._q, { robot: q.robot });
  if (!pose.ok && !U.q) { $('sgNote').textContent = 'robot would overlap a wall or the HIVE base'; return false; }
  const r = PS.shot(q, U.v, U.th);
  const k = q.params.k || 0;
  const w0 = isFinite(r.ballSpinRpm) && r.ballSpinRpm > 0 ? r.ballSpinRpm * Math.PI / 30 : U.S * U.v / R_M;
  PATHS.main = makePath(r.path, U.S, k, U.S > 0 ? w0 : 0); PATHS.twin = makePath(r.twin.path, 0, k, 0);
  PATHS.verdict = r;
  for (const k_ of ['main', 'twin']) {
    if (pathLines[k_]) { scene.remove(pathLines[k_]); pathLines[k_].geometry.dispose(); }
    const P = PATHS[k_], pts = [];
    for (let i = 0; i < P.n; i += 4) pts.push(new THREE.Vector3(P.p.x[i], P.p.y[i], P.p.z[i]));
    const l = new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({ color: COL[k_] }));
    pathLines[k_] = l; scene.add(l);
  }
  U.lastLegal = { x: U.x, y: U.y, hd: U.hd };
  $('sgNote').textContent = '';
  const T = Math.max(PATHS.main.T, PATHS.twin.T); $('tSlide').max = String(T);
  U.tSim = Math.min(U.tSim, T);
  // colour scale follows the ball: 0 to a round number at about 1.5x its current air speed, the fastest air near it (see render)
  U.vleg = niceCeil(1.5 * Math.max(0.5, PATHS.main.v0, PATHS.twin.v0));
  drawLegend();
  updateReadout(); updateSummary(); applyOffsets(); need = true;
  return true;
}
function updateRobot() {
  robot.position.set(U.x, U.y, 0); robot.rotation.z = U.hd * Math.PI / 180;
  robot.userData.body.material.color.set(U.lastLegal && U.lastLegal.x === U.x && U.lastLegal.y === U.y ? 0x2f6fdd : 0xd33b3b);
  relMark.position.set(U.x, U.y, U.h);
  $('rx').value = U.x; $('ry').value = U.y; $('rh').value = U.hd; $('rz').value = U.h;
  $('rxo').textContent = U.x.toFixed(2); $('ryo').textContent = U.y.toFixed(2); $('rho').textContent = Math.round(U.hd) + '°'; $('rzo').textContent = U.h.toFixed(2);
}
const fmtS = (s) => (+s).toFixed(2).replace(/\.?0+$/, '') || '0';
function updateShotUi() {
  $('sv').value = U.v; $('sth').value = U.th; $('svo').textContent = U.v.toFixed(2) + ' m/s'; $('stho').textContent = U.th.toFixed(1) + '°';
  const sel = $('sS');
  if (![...sel.options].some((o) => +o.value === U.S)) sel.insertAdjacentHTML('beforeend', `<option value="${U.S}">Backspin S ${fmtS(U.S)}</option>`);
  const o = [...sel.options].find((o_) => +o_.value === U.S); if (o) sel.value = o.value;
}
function updateSummary() {
  $('sumRobot').textContent = `x ${U.x.toFixed(2)} m, y ${U.y.toFixed(2)} m, heading ${Math.round(U.hd)}°, release ${U.h.toFixed(2)} m`;
  $('sumShot').textContent = `${U.v.toFixed(2)} m/s at ${U.th.toFixed(1)}°, ${U.S > 0 ? 'backspin S ' + fmtS(U.S) : 'no spin'}`;
}
const cell = (c) => c ? `${c.result}${c.minClear != null && isFinite(c.minClear) ? ' (min clearance ' + (Math.round(c.minClear * 1000) || 0) + ' mm)' : ''}` : '-';
function updateReadout() {
  const r = PATHS.verdict; if (!r) return;
  const tw = r.twin, same = U.S === 0;
  const ea = (c) => (c && c.entryAngle != null && isFinite(c.entryAngle) ? c.entryAngle.toFixed(0) + '°' : '-');
  $('read').innerHTML = `<table><tr><th></th><th class="c1">${same ? 'No spin' : 'Backspin S ' + fmtS(U.S)}</th>${same ? '' : '<th class="c2">No-spin twin</th>'}</tr>
  <tr><th>Result</th><td>${esc(cell(r.cls))}</td>${same ? '' : `<td>${esc(cell(tw.cls))}</td>`}</tr>
  <tr><th>Entry angle</th><td>${ea(r.cls)}</td>${same ? '' : `<td>${ea(tw.cls)}</td>`}</tr>
  <tr><th>Flight time</th><td>${PATHS.main.T.toFixed(2)} s</td>${same ? '' : `<td>${PATHS.twin.T.toFixed(2)} s</td>`}</tr>
  <tr><th>Wheel</th><td colspan="2">${r.rpm.toFixed(0)} rpm, ball spin ${r.ballSpinRpm.toFixed(0)} rpm</td></tr></table>
  <div class="mute">PREDICTED (model output); drag, Cd and Magnus coefficients ASSUMED</div>`;
}

// ------------------------------------------------------------ CFD library
let RUNS = [], LEVELS = [];
const isAnim = (r) => (r.n_frames || 0) >= 10;
function buildLibrary(runs) {
  RUNS = runs;
  LEVELS = [...new Set(RUNS.map((r) => Math.round(r.S * 1000) / 1000))].sort((a, b) => a - b);
}
// the case drawn at one spin level: nearest speed (log), the time mean when Averaged is on, long series only when asked
function caseScore(r, speed) {
  return Math.abs(Math.log(speed / r.speed_mps)) + (U.avg && !r.mean ? 0.5 : 0) + (isAnim(r) !== $('lAnimCase').checked ? 0.05 : 0);
}
function pickAt(s, level, speed) {
  const cand = RUNS.filter((r) => Math.abs(r.S - level) < 1e-3);
  if (!cand.length) return null;
  let best = cand[0];
  for (const r of cand) if (caseScore(r, speed) < caseScore(best, speed)) best = r;
  const cur = cand.find((r) => r.id === s.cur.get(level));
  if (cur && caseScore(cur, speed) <= caseScore(best, speed) + 0.08) best = cur;   // hysteresis: no flicker at a tie
  s.cur.set(level, best.id);
  return best;
}
// targets: the two cases bracketing the local spin ratio, linear weights in S; clamped to the library range
function targets(s, speed, Sl) {
  const lv = s.k === 'twin' ? LEVELS.filter((L) => L === 0) : LEVELS;
  if (!lv.length) return { list: [], clamp: null, Sc: Sl };
  const lo = lv[0], hi = lv[lv.length - 1], Sc = Math.min(hi, Math.max(lo, Sl));
  const clamp = Sl < lo - 0.005 ? 'low' : Sl > hi + 0.005 ? 'high' : null;
  let a = lo, b = hi;
  for (const L of lv) if (L <= Sc + 1e-9) a = L;
  for (let i = lv.length - 1; i >= 0; i--) if (lv[i] >= Sc - 1e-9) b = lv[i];
  const w = b > a ? (Sc - a) / (b - a) : 0;
  const ra = pickAt(s, a, speed), rb = b !== a ? pickAt(s, b, speed) : null;
  const list = [];
  if (ra && (1 - w > 0.002 || !rb)) list.push({ r: ra, w: rb ? 1 - w : 1, S: a });
  if (rb && w > 0.002) list.push({ r: rb, w: ra ? w : 1, S: b });
  return { list, clamp, Sc, lo, hi };
}

// ------------------------------------------------------------ flow slots (one per ball): cached RunViews, crossfaded
const slots = {};
const MAN = new Map();   // manifest cache by url
for (const k of ['main', 'twin']) {
  const g = new THREE.Group(); g.matrixAutoUpdate = false; scene.add(g);
  const ball = new THREE.Mesh(new THREE.SphereGeometry(0.5, 28, 18),
    new THREE.MeshStandardMaterial({ color: COL[k], roughness: 0.55, metalness: 0.05, side: THREE.DoubleSide }));
  ball.matrixAutoUpdate = false; scene.add(ball);
  slots[k] = { k, group: g, ball, views: new Map(), cur: new Map(), T: { list: [] }, speed: 0, Sl: 0, tFlow: 0, spinF: 1 };
}
let ballGeomSet = false, loading = 0;
function disposeObj(o) {
  o.traverse((c) => { c.geometry?.dispose(); const ms = Array.isArray(c.material) ? c.material : c.material ? [c.material] : []; for (const m of ms) { m.map?.dispose(); m.dispose(); } });
}
function setLoad() { $('load').textContent = loading ? `Loading CFD (${loading})...` : ''; }
function viewFor(s, entry) {
  const key = `${entry.id}|${U.avg ? 'mean' : 'inst'}`;
  let o = s.views.get(key);
  if (!o) {
    o = { key, entry, avg: U.avg, view: null, w: 0, g: new THREE.Group(), failed: false, used: 0, fadeW: -1, cs: -1, lastUpd: 0 };
    s.group.add(o.g); s.views.set(key, o);
    loadView(s, o);
  }
  o.used = performance.now();
  return o;
}
async function loadView(s, o) {
  loading++; setLoad();
  try {
    const url = `${BASE}/${o.entry.path}`, dir = url.slice(0, url.lastIndexOf('/'));
    if (!MAN.has(url)) MAN.set(url, fetch(url).then((r) => { if (!r.ok) throw new Error(r.status + ' ' + url); return r.json(); }));
    const m = await MAN.get(url);
    const v = new RunView(m, dir, { mean: o.avg }); await v.load();
    if (o.dead) { v.dispose(); loading--; setLoad(); return; }
    for (const c of v.scene.children.filter((c) => !c.isLight)) { v.scene.remove(c); o.g.add(c); }
    v.body.visible = false;                      // the spinning ball below stands in for the CFD body
    v.streams.material.uniforms.uRes.value.set(innerWidth * DPR, innerHeight * DPR);
    o.view = v;
    if (!ballGeomSet) {                           // the CFD ball surface, holes and all, for both drawn balls
      ballGeomSet = true;
      const bg = v.body.geometry.clone();
      for (const k of ['main', 'twin']) { slots[k].ball.geometry.dispose(); slots[k].ball.geometry = bg; }
    }
    layersTo(o); updateCaps();
  } catch (e) { console.error(e); o.failed = true; $('load').textContent = 'CFD load failed: ' + e.message; }
  loading--; if (!o.failed) setLoad();
}
function evict(s, o) {
  o.dead = true; s.views.delete(o.key); s.group.remove(o.g); disposeObj(o.g);
  if (o.view) for (const sl of o.view.slices) { for (const t of Object.values(sl.tex)) t.dispose(); sl.ftex?.dispose(); }
}
const ST = () => ({ stream: $('lStream').checked, vortex: $('lVortex').checked, q: +$('qLevel').value, planes: [$('lY').checked, $('lZ').checked],
  field: $('sField').value, cont: $('lCont').checked, sop: +$('sOp').value });
function layersTo(o, s = ST()) {
  const v = o.view; if (!v) return;
  v.streams.visible = s.stream; v.streams.material.uniforms.uWidth.value = 1.3 * DPR; v.streams.material.uniforms.uAnim.value = 1;
  v.vortex.forEach((m, i) => { m.visible = s.vortex && i === Math.min(s.q, v.vortex.length - 1); });
  v.slices.forEach((sl, i) => {
    sl.group.visible = !!s.planes[i];
    sl.mat.map = v.fr ? sl.ftex : sl.tex[s.field]; sl.mat.needsUpdate = true;
    sl.lines.speed.visible = s.cont && s.field === 'speed'; sl.lines.vort.visible = s.cont && s.field === 'vort';
  });
  o.fadeW = -1; v.dirty = true;
}
function applyLayers() { const s = ST(); for (const k in slots) for (const o of slots[k].views.values()) layersTo(o, s); need = true; }

// per frame: weights eased toward the targets; only loaded targets count, so nothing pops while a case loads
function updateSlot(s, show, dtS, tMs, st) {
  const T = s.T, want = new Map();
  if (show) for (const t of T.list) want.set(viewFor(s, t.r).key, t.w);
  let sumL = 0;
  for (const [k_, w] of want) { const o = s.views.get(k_); if (o.view) sumL += w; }
  const ease = Math.min(1, dtS * 5);
  for (const o of [...s.views.values()]) {
    const goal = !show ? 0 : sumL > 0 ? (o.view && want.has(o.key) ? want.get(o.key) / sumL : 0) : o.w;
    o.w += (goal - o.w) * ease; if (Math.abs(goal - o.w) < 0.003) o.w = goal;
    const v = o.view;
    o.g.visible = !!v && o.w > 0.01;
    if (!v || !o.g.visible) continue;
    if (Math.abs(o.w - o.fadeW) > 0.004) { v.setFade(o.w, st.sop); o.fadeW = o.w; }
    // m/s colour: the bundle stores |u| / (speed_range[1] U); the ball's air speed sets U, the legend sets the top
    const c = (v.m.speed_range?.[1] || 1.5) * s.speed / U.vleg;
    if (Math.abs(c - o.cs) > 0.015 * c) { v.setColorScale(c); o.cs = c; }
    v.streams.material.uniforms.uTime.value = tMs / 1000;
    if (v.fr) {
      const n = v.fr.n;
      let ft = 0;
      if (n > 1) {   // instantaneous series: ping-pong through the saved frames, about 2 t* per second while playing
        const ts = v.fr.info.t_star || [], dts = ts.length === n ? Math.max(1e-3, (ts[n - 1] - ts[0]) / (n - 1)) : 1;
        const ph = s.tFlow * Math.min(12, 2 / dts), per = 2 * (n - 1), x = ph % per;
        ft = x <= n - 1 ? x : per - x;
      }
      if (v.dirty || (n > 1 && Math.abs(ft - v.curT) > 0.02 && tMs - o.lastUpd > 40)) { v.setTime(ft, st); o.lastUpd = tMs; }
    }
  }
  // keep a few recent cases ready, drop the rest
  if (s.views.size > MAX_VIEWS) {
    const idle = [...s.views.values()].filter((o) => o.w === 0 && !want.has(o.key)).sort((a, b) => a.used - b.used);
    while (s.views.size > MAX_VIEWS && idle.length) evict(s, idle.shift());
  }
}

// ------------------------------------------------------------ captions, legend
const fmt = (x) => (+x).toFixed(2).replace(/\.?0+$/, '');
const caseName = (r) => `S ${fmt(r.S)} @ ${fmt(r.speed_mps)} m/s`;
function caption(k) {
  const s = slots[k], T = s.T, P = PATHS[k];
  if (!P) return '';
  const nm = k === 'main' ? (U.S === 0 ? 'No-spin shot' : `Backspin shot, S ${fmtS(U.S)} at launch`) : 'No-spin twin';
  const parts = [];
  if (!T.list.length) parts.push(k === 'twin' && RUNS.length ? 'no no-spin CFD case in the library' : 'no CFD cases in the library');
  else {
    const shown = T.list.map((t) => `${caseName(t.r)}${T.list.length > 1 ? ' (' + Math.round(t.w * 100) + '%)' : ''}`);
    parts.push(`general solution, ${T.list.length > 1 ? 'blended from CFD cases ' + shown.join(' + ') : 'from CFD case ' + shown[0]}`);
  }
  parts.push(`ball now ${s.speed.toFixed(1)} m/s` + (k === 'main' && U.S > 0 ? `, local S ${s.Sl.toFixed(2)}` : ''));
  if (T.clamp) parts.push(`local S outside the CFD library (S ${fmt(T.lo)} to ${fmt(T.hi)}): drawn at S ${fmt(T.Sc)}`);
  const vs = [...s.views.values()].filter((o) => o.view && o.w > 0.01).map((o) => o.view);
  const syn = vs.some((v) => v.m.synthetic);
  const out = parts.map(esc);
  out.push(`<span class="${syn ? 'syn' : 'pred'}">${syn ? 'SYNTHETIC TEST FIELD - not CFD' : 'PREDICTED'}</span>`);
  if (vs.length) {
    const mv = vs.find((v) => v.mean);
    if (mv) out.push(esc(`time mean of ${mv.m.mean.n_avg} frames`));
    else out.push(U.avg ? 'instantaneous (no time mean saved for this case)' : 'instantaneous wake');
  }
  if (k === 'main' && U.S > 0) {
    out.push('CFD includes the spinning holes');
    if (s.spinF < 0.999) out.push(esc(`ball spin drawn ${Math.round(1 / s.spinF)}x slower than real`));
  }
  const ori = T.list[0]?.r.orientation || vs[0]?.m.orientation || 'btw';
  out.push(esc(`hole orientation ${ori} ASSUMED`));
  return `<b>${esc(nm)}</b>${out.join(' | ')}`;
}
function updateCaps() {
  $('capM').innerHTML = caption('main');
  $('capT').innerHTML = U.S === 0 ? '' : caption('twin');
  const syn = Object.values(slots).some((s) => [...s.views.values()].some((o) => o.view?.m.synthetic && o.w > 0.01));
  $('banner').style.display = syn ? 'block' : 'none';
  $('banner').textContent = 'SYNTHETIC TEST FIELD — not CFD';
}
function drawLegend() {
  const cv = $('lgBar'), ctx = cv.getContext('2d'), W = cv.width, H = cv.height;
  for (let i = 0; i < W; i++) { const c = turbo(i / (W - 1)).map((x) => Math.round(x * 255)); ctx.fillStyle = `rgb(${c})`; ctx.fillRect(i, 0, 1, H); }
  const V = U.vleg;
  $('lgTicks').innerHTML = [0, V / 2, V].map((x) => `<span>${fmt(x)}</span>`).join('');
  const mc = $('mlgBar'), mx = mc.getContext('2d');
  mx.drawImage(cv, 0, 0, mc.width, mc.height); $('mhi').textContent = fmt(V);
}

// ------------------------------------------------------------ per-frame placement
const MB = new THREE.Matrix4(), MR = new THREE.Matrix4(), MS = new THREE.Matrix4(), V3 = new THREE.Vector3();
const X = new THREE.Vector3(), Y = new THREE.Vector3(), Z = new THREE.Vector3();
let offVec = new THREE.Vector3();
function applyOffsets() {
  const a = PATHS.twin?.axis || new THREE.Vector3(0, 1, 0), o = +$('dOff').value;
  offVec = a.clone().multiplyScalar(o); $('dOffo').textContent = o.toFixed(2) + ' m';
  if (pathLines.twin) pathLines.twin.position.copy(offVec);
}
// ball-frame basis at path index i: CFD +x = air relative to the ball (against its velocity), CFD y = spin axis, z = x cross y
function basis(P, i, sc, out) {
  X.set(-P.vx[i], -P.vy[i], -P.vz[i]).normalize();
  Y.copy(P.axis); Y.addScaledVector(X, -Y.dot(X)); if (Y.lengthSq() < 1e-9) Y.set(0, 1, 0).addScaledVector(X, -X.y); Y.normalize();
  Z.crossVectors(X, Y);
  return out.makeBasis(X.multiplyScalar(sc), Y.multiplyScalar(sc), Z.multiplyScalar(sc));
}
function place(k, P, tSim, show) {
  const s = slots[k];
  const i = Math.min(P.n - 1, Math.round(tSim / P.dt)), t = i * P.dt;
  const pos = V3.set(P.p.x[i], P.p.y[i], P.p.z[i]);
  if (k === 'twin') pos.add(offVec);
  s.speed = P.sp[i]; s.Sl = P.Sloc(i, t);
  s.T = targets(s, s.speed, s.Sl);
  s.ball.visible = show;
  s.group.visible = show && (k === 'main' || $('dTwinFlow').checked);
  const sc = D_M * +$('dMag').value;
  basis(P, i, sc, MB); MB.setPosition(pos);
  s.group.matrix.copy(MB); s.group.matrixWorldNeedsUpdate = true;
  // the drawn ball turns about the (fixed) backspin axis: launch attitude, then phi(t) = w0 (1 - e^-kt) / k;
  // positive rotation about the CFD +y axis is backspin (top surface moving back against the flight)
  const w0 = P.w0, tsp = +$('tSpd').value;
  s.spinF = w0 > 0 ? Math.min(1, (SPIN_CAP * 2 * Math.PI) / (w0 * tsp)) : 1;
  const phi = w0 > 0 ? s.spinF * (P.k > 1e-6 ? w0 * (1 - Math.exp(-P.k * t)) / P.k : w0 * t) : 0;
  basis(P, 0, sc, MS);
  MR.makeRotationAxis(P.axis, phi).multiply(MS).setPosition(pos);
  s.ball.matrix.copy(MR); s.ball.matrixWorldNeedsUpdate = true;
  return pos.clone();
}

// ------------------------------------------------------------ interaction
let need = true, dragging = false;
const ray = new THREE.Raycaster(), plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0), hit = new THREE.Vector3();
function ndc(ev) { const r = canvas.getBoundingClientRect(); return new THREE.Vector2(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1); }
canvas.addEventListener('pointerdown', (ev) => {
  if (EMBED) return;   // the explorer's Robot tab places the robot
  ray.setFromCamera(ndc(ev), camera);
  if (ray.intersectObject(robot, true).length) { dragging = true; controls.enabled = false; canvas.setPointerCapture(ev.pointerId); ev.preventDefault(); }
});
canvas.addEventListener('pointermove', (ev) => {
  if (!dragging) return;
  ray.setFromCamera(ndc(ev), camera);
  if (!ray.ray.intersectPlane(plane, hit)) return;
  moveRobot(Math.round(hit.x * 100) / 100, Math.round(hit.y * 100) / 100);
});
const endDrag = () => { if (dragging) { dragging = false; controls.enabled = true; } };
canvas.addEventListener('pointerup', endDrag); canvas.addEventListener('pointercancel', endDrag);
let pending = false;
function moveRobot(x, y, hd) {
  const nx = Math.max(-C.X_WALL, Math.min(C.X_WALL, x)), ny = Math.max(C.Y_LO, Math.min(C.Y_HI, y)), nh = hd === undefined ? U.hd : hd;
  const ok = PS.pose(nx, ny, META._q, { robot: { length: 18 * IN, width: 18 * IN, offset: [0, 0], heading: nh } }).ok;
  if (!ok) return;     // keep the last legal pose
  U.x = nx; U.y = ny; U.hd = nh;
  if (!pending) { pending = true; requestAnimationFrame(() => { pending = false; rebuildShot(); updateRobot(); }); }
}
for (const id of ['rx', 'ry', 'rh']) $(id).addEventListener('input', () => moveRobot(+$('rx').value, +$('ry').value, +$('rh').value));
$('rz').addEventListener('input', () => { U.h = +$('rz').value; rebuildShot(); updateRobot(); });
$('sv').addEventListener('input', () => { U.v = +$('sv').value; updateShotUi(); rebuildShot(); });
$('sth').addEventListener('input', () => { U.th = +$('sth').value; updateShotUi(); rebuildShot(); });
$('sS').addEventListener('change', () => { U.S = +$('sS').value; updateShotUi(); rebuildShot(); updateCaps(); });
for (const id of ['lStream', 'lVortex', 'qLevel', 'lY', 'lZ', 'sField', 'lCont', 'sOp']) $(id).addEventListener('input', applyLayers);
for (const id of ['dTwinFlow', 'dMag', 'dMode']) $(id).addEventListener('input', () => { need = true; });
$('dOff').addEventListener('input', () => { applyOffsets(); need = true; });
$('lAnimCase').addEventListener('change', () => { for (const k in slots) slots[k].cur.clear(); });
function setAvg(on) {
  U.avg = on;
  for (const b of document.querySelectorAll('#vMode button')) b.setAttribute('aria-pressed', String((b.dataset.m === 'avg') === on));
  for (const k in slots) slots[k].cur.clear();
  updateCaps();
}
for (const b of document.querySelectorAll('#vMode button')) b.addEventListener('click', () => setAvg(b.dataset.m === 'avg'));
// phone layout: the panel folds to one line ("Shot and layers")
function setPanel(open) { $('panel').classList.toggle('open', open); $('panelSum').setAttribute('aria-expanded', String(open)); }
$('panelSum').addEventListener('click', () => setPanel(!$('panel').classList.contains('open')));
$('panelSum').addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setPanel(!$('panel').classList.contains('open')); } });
function setPlay(on) { U.play = on; $('tPlay').textContent = on ? 'Pause' : 'Play'; $('tPlay').setAttribute('aria-pressed', String(on)); }
$('tPlay').onclick = () => { if (!U.play && PATHS.main && U.tSim >= Math.max(PATHS.main.T, PATHS.twin.T) - 1e-3) U.tSim = 0; setPlay(!U.play); };
$('tSlide').addEventListener('input', () => { U.tSim = +$('tSlide').value; });
$('cOver').onclick = () => { $('cMode').value = 'free'; camera.position.copy(OVER.pos); controls.target.copy(OVER.tgt); };
$('cMode').addEventListener('change', () => { if ($('cMode').value !== 'free') followInit = true; });
let followInit = true;
$('bSuggest').onclick = () => {
  $('sgNote').textContent = 'solving...';
  setTimeout(() => {
    const q = qNow();
    const r = PS.solve(q);
    if (!r.pose || r.pose.ok === false) { $('sgNote').textContent = 'no legal pose'; return; }
    let s = r.mostForgiving; if (s && s.gripLimited && r.minRpm) s = r.minRpm;
    if (!s) { $('sgNote').textContent = 'no clean setting found here (PREDICTED)'; return; }
    U.v = s.v; U.th = s.theta; updateShotUi(); rebuildShot(); U.tSim = 0;
    $('sgNote').textContent = 'PREDICTED clean setting' + (s.gripLimited ? ' (grip-limited)' : '');
  }, 20);
};
function resize() {
  const w = innerWidth, h = innerHeight; renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
  for (const k in slots) for (const o of slots[k].views.values()) o.view?.streams.material.uniforms.uRes.value.set(w * DPR, h * DPR);
  need = true;
}
addEventListener('resize', resize);
// theme: follows the explorer's saved choice (same storage key), live when the explorer switches it
function retheme() {
  BG = new THREE.Color(cssVar('--bg') || '#0b1015');
  for (const k in slots) for (const o of slots[k].views.values()) if (o.view) { o.view.applyTheme(); o.fadeW = -1; }
}
addEventListener('storage', (e) => {
  if (e.key !== 'pollen-theme') return;
  if (e.newValue === 'light' || e.newValue === 'dark') document.documentElement.dataset.theme = e.newValue; else delete document.documentElement.dataset.theme;
  retheme();
});
matchMedia('(prefers-color-scheme: light)').addEventListener?.('change', retheme);

// the explorer (same origin) sends its current shot: {type: 'pollen-shot', x, y, hd, h, v, th, S, q}
let pendingMsg = null;
function applyShot(d) {
  if (!META) { pendingMsg = d; return; }
  if (d.q && typeof d.q === 'object') U.q = d.q;
  for (const k_ of ['x', 'y', 'hd', 'h', 'v', 'th', 'S']) if (d[k_] !== null && d[k_] !== undefined && isFinite(d[k_])) U[k_] = +d[k_];
  updateShotUi();
  if (rebuildShot()) updateRobot();
  if (d.reset) { U.tSim = 0; followInit = true; }
  updateCaps();
}
addEventListener('message', (ev) => {
  if (ev.origin !== location.origin) return;
  const d = ev.data;
  if (d && d.type === 'pollen-shot') applyShot(d);
  if (d && d.type === 'pollen-flow-visible') VISIBLE = !!d.on;   // the explorer hides this tab: stop drawing until it is shown again
});

// ------------------------------------------------------------ loop
let lastT = 0, capT = 0, VISIBLE = true;
function render(t) {
  requestAnimationFrame(render);
  if (!VISIBLE) { lastT = t; return; }
  const dtS = Math.min(0.1, Math.max(0, (t - lastT) / 1000)); lastT = t;
  if (!PATHS.main) return;
  const T = Math.max(PATHS.main.T, PATHS.twin.T);
  if (U.play) {
    U.tSim += dtS * +$('tSpd').value;
    for (const k in slots) slots[k].tFlow += dtS;
    if (U.tSim > T) { if ($('tLoop').checked) U.tSim = 0; else { U.tSim = T; setPlay(false); } }
  }
  $('tSlide').value = String(U.tSim);
  const mode = $('dMode').value;
  const showMain = mode === 'both' || U.S === 0;
  const showTwin = (mode === 'both' && U.S !== 0) || mode === 'twin';
  const pm = place('main', PATHS.main, U.tSim, showMain);
  const pt = place('twin', PATHS.twin, U.tSim, showTwin);
  const st = ST();
  // speed colours scale with the ball's local speed so the flow pattern stays visible from launch to apex;
  // a step up happens at once, a step down only once the speed is well inside the lower rung (no flicker)
  const vNow = Math.max(showMain ? slots.main.speed : 0, showTwin ? slots.twin.speed : 0);
  if (vNow > 0) {
    const up = niceCeil(1.5 * vNow), down = niceCeil(1.5 * 1.15 * vNow);
    const tg = up > U.vleg ? up : down < U.vleg ? down : U.vleg;
    if (tg !== U.vleg) { U.vleg = tg; drawLegend(); }
  }
  updateSlot(slots.main, showMain, dtS, t, st);
  updateSlot(slots.twin, showTwin && $('dTwinFlow').checked, dtS, t, st);
  $('tLab').textContent = `flight ${U.tSim.toFixed(2)} s of ${T.toFixed(2)} s | ball ${slots[showMain ? 'main' : 'twin'].speed.toFixed(1)} m/s | PREDICTED path`;
  if (t - capT > 200) { capT = t; updateCaps(); }
  const fol = $('cMode').value;
  if (fol !== 'free') {
    const tgt = fol === 'follow' && showMain ? pm : pt;
    if (followInit) { camera.position.copy(tgt).add(new THREE.Vector3(-0.28, -0.42, 0.2)); controls.target.copy(tgt); followInit = false; }
    else { V3.copy(tgt).sub(controls.target); camera.position.add(V3); controls.target.copy(tgt); }
  }
  controls.update();
  renderer.setClearColor(BG, 1);
  renderer.render(scene, camera);
}

// ------------------------------------------------------------ boot
async function boot() {
  resize();
  try {
    const fi = await (await fetch(FIELD_URL)).json();
    META = fi;
    META._q = { grid: fi.grid, sections: fi.sections, frame: fi.frame, field_grid: fi.field_grid, cases: fi.cases.map((c) => ({ S: c.S, var: c.var, params: c.params })) };
  } catch (e) { $('load').textContent = 'Field data not found. Build the explorer data first.'; return; }
  buildField(META);
  const Ss = [...new Set(META.cases.map((c) => c.S))].sort((a, b) => a - b);
  $('sS').innerHTML = Ss.map((s) => `<option value="${s}">${s === 0 ? 'No spin' : 'Backspin S ' + fmtS(s)}</option>`).join('');
  if (!Ss.includes(U.S)) U.S = Ss[Ss.length - 1];
  try {
    const idx = await (await fetch(`${BASE}/index.json`)).json();
    buildLibrary((idx.runs || []).map((r) => {
      const sp = r.speed_mps ?? parseFloat((/([0-9.]+)\s*m\/s/.exec(r.label || '') || [])[1]);
      const S = r.S ?? parseFloat((/\bS\s*([0-9.]+)/.exec(r.label || '') || [])[1] || 0);
      return Object.assign({}, r, { speed_mps: sp, S: isFinite(S) ? S : 0 });
    }).filter((r) => isFinite(r.speed_mps) && r.speed_mps > 0));
  } catch (e) { buildLibrary([]); }
  if (!RUNS.length) $('load').textContent = 'No CFD cases in the flow library yet.';
  $('libNote').textContent = RUNS.length ? `CFD library: ${RUNS.length} cases, spin S ${LEVELS.map(fmt).join(', ')}; ` +
    `${[...new Set(RUNS.map((r) => +r.speed_mps))].sort((a, b) => a - b).map(fmt).join(', ')} m/s.` : '';
  for (const p of ['x', 'y', 'v', 'th', 'S', 'hd', 'h']) if (params.get(p) !== null && params.get(p) !== '' && isFinite(+params.get(p))) U[p] = +params.get(p);
  updateShotUi();
  if (params.get('hidepanel')) $('panel').style.display = 'none';
  if (!rebuildShot()) { U.x = -1.0; U.y = 0.2; U.hd = 0; rebuildShot(); }
  updateRobot();
  if (!EMBED && !params.get('v') && !params.get('x')) $('bSuggest').click();
  if (params.get('cam')) $('cMode').value = params.get('cam');
  if (params.get('mag')) $('dMag').value = params.get('mag');
  if (params.get('off')) { $('dOff').value = params.get('off'); applyOffsets(); }
  if (params.get('plane')) { $('lY').checked = params.get('plane').includes('a'); $('lZ').checked = params.get('plane').includes('b'); }
  if (params.get('anim')) $('lAnimCase').checked = true;
  if (params.get('spd')) $('tSpd').value = params.get('spd');
  setAvg(U.avg); applyLayers();
  if (params.get('t')) U.tSim = +params.get('t');
  if (params.get('play')) setPlay(true);
  if (params.get('free')) $('cMode').value = 'free';
  if (pendingMsg) { const d = pendingMsg; pendingMsg = null; applyShot(d); }
  if (window.parent !== window) try { window.parent.postMessage({ type: 'pollen-flow-ready' }, location.origin); } catch (_) { /* not same origin */ }
  requestAnimationFrame(render);
}
boot().catch((e) => { console.error(e); $('load').textContent = 'Failed: ' + e.message; });
