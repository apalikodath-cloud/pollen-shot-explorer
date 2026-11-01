// Shot flow scene: the explorer's shot path (physics.js integrate3D through solver.js shot()) with the
// nearest CFD case drawn around the ball, rotated so the CFD free stream meets the ball as the air does.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RunView, esc, cssVar, env } from './flowview.js';

THREE.Object3D.DEFAULT_UP.set(0, 0, 1);
const $ = (id) => document.getElementById(id);
const params = new URLSearchParams(location.search);
const BASE = (params.get('flows') || 'flows').replace(/\/+$/, '');
const FIELD_URL = params.get('field') || '../explorer/data/field/index.json';
const PS = window.PollenSolver, C = PS.constants;
const IN = 0.0254, D_M = 0.07112;
const SPIN_COL = 0xff8c1a, TWIN_COL = 0x5aa7ff;

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
  const gate = new THREE.Mesh(new THREE.SphereGeometry(0.03, 12, 8), new THREE.MeshBasicMaterial({ color: 0x2ecc71 }));
  gate.position.set(C.X_GATE, 0, 1.5); g.add(gate); gate.visible = false;
}

// ------------------------------------------------------------ robot
const U = { x: -1.0, y: 0.2, hd: 0, h: 0.737, v: 6.5, th: 75, S: 1.0, tSim: 0, play: false, lastLegal: null };
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

function qNow(metaQ) {
  const cs = META.cases.find((c) => c.S === U.S && c.var === 'nominal') || META.cases.find((c) => c.S === U.S) || META.cases[0];
  return { x: U.x, y: U.y, h: U.h, S: U.S, vu: 0.42, params: cs.params, meta: metaQ, air: { tC: 20, altM: 0, rh: 0 },
    drag: { model: 'const', spin: 0 }, wind: { along: 0, up: 0, side: 0 },
    // a (zero) move block selects the 3D path, i.e. physics.js integrate3D
    move: { along: 0, across: 0, wz: 0, d0: 0, lead: true },
    robot: { length: 18 * IN, width: 18 * IN, offset: [0, 0], heading: U.hd } };
}
let META = null;

// ------------------------------------------------------------ shot paths
// path record: positions, velocity (central difference), local speed ratio S(t) = S0 v0 exp(-k t) / |v|
function makePath(p, S0, k, col) {
  const n = p.n, dt = p.dt, vx = new Float32Array(n), vy = new Float32Array(n), vz = new Float32Array(n), sp = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    const a = Math.max(0, i - 1), b = Math.min(n - 1, i + 1), d = (b - a) * dt || dt;
    vx[i] = (p.x[b] - p.x[a]) / d; vy[i] = (p.y[b] - p.y[a]) / d; vz[i] = (p.z[b] - p.z[a]) / d;
    sp[i] = Math.hypot(vx[i], vy[i], vz[i]);
  }
  const h0 = Math.hypot(vx[0], vy[0]) || 1, axis = new THREE.Vector3(vy[0] / h0, -vx[0] / h0, 0);  // backspin axis, fixed
  const v0 = sp[0];
  return { p, n, dt, T: (n - 1) * dt, vx, vy, vz, sp, axis, S0, k, v0, col,
    Sloc: (i, t) => S0 * v0 * Math.exp(-k * t) / Math.max(sp[i], 0.05) };
}
const PATHS = { main: null, twin: null, verdict: null };
const pathLines = { main: null, twin: null };
function rebuildShot() {
  const q = qNow(META._q);
  const pose = PS.pose(U.x, U.y, META._q, { robot: q.robot });
  if (!pose.ok) { $('sgNote').textContent = 'robot would overlap a wall or the HIVE base'; return false; }
  const r = PS.shot(q, U.v, U.th);
  const k = q.params.k || 0;
  PATHS.main = makePath(r.path, U.S, k); PATHS.twin = makePath(r.twin.path, 0, k);
  PATHS.verdict = r;
  for (const key_ of ['main', 'twin']) {
    if (pathLines[key_]) { scene.remove(pathLines[key_]); pathLines[key_].geometry.dispose(); }
    const P = PATHS[key_], pts = [];
    for (let i = 0; i < P.n; i += 4) pts.push(new THREE.Vector3(P.p.x[i], P.p.y[i], P.p.z[i]));
    const l = new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({ color: key_ === 'main' ? SPIN_COL : TWIN_COL }));
    pathLines[key_] = l; scene.add(l);
  }
  U.lastLegal = { x: U.x, y: U.y, hd: U.hd };
  $('sgNote').textContent = '';
  const T = Math.max(PATHS.main.T, PATHS.twin.T); $('tSlide').max = String(T);
  U.tSim = Math.min(U.tSim, T);
  updateReadout(); applyOffsets(); need = true;
  return true;
}
function updateRobot() {
  robot.position.set(U.x, U.y, 0); robot.rotation.z = U.hd * Math.PI / 180;
  robot.userData.body.material.color.set(U.lastLegal && U.lastLegal.x === U.x && U.lastLegal.y === U.y ? 0x2f6fdd : 0xd33b3b);
  relMark.position.set(U.x, U.y, U.h);
  $('rx').value = U.x; $('ry').value = U.y; $('rh').value = U.hd; $('rz').value = U.h;
  $('rxo').textContent = U.x.toFixed(2); $('ryo').textContent = U.y.toFixed(2); $('rho').textContent = U.hd + '°'; $('rzo').textContent = U.h.toFixed(2);
}
function updateShotUi() {
  $('sv').value = U.v; $('sth').value = U.th; $('svo').textContent = U.v.toFixed(2) + ' m/s'; $('stho').textContent = U.th.toFixed(1) + '°'; $('sS').value = String(U.S);
}
const cell = (c) => c ? `${c.result}${c.minClear != null && isFinite(c.minClear) ? ' (min clearance ' + (c.minClear * 1000).toFixed(0) + ' mm)' : ''}` : '-';
function updateReadout() {
  const r = PATHS.verdict; if (!r) return;
  const tw = r.twin, same = U.S === 0;
  const ea = (c) => (c && c.entryAngle != null && isFinite(c.entryAngle) ? c.entryAngle.toFixed(0) + '°' : '-');
  $('read').innerHTML = `<table><tr><th></th><th class="c1">${same ? 'No spin' : 'Backspin S ' + U.S}</th>${same ? '' : '<th class="c2">No-spin twin</th>'}</tr>
  <tr><th>Result</th><td>${esc(cell(r.cls))}</td>${same ? '' : `<td>${esc(cell(tw.cls))}</td>`}</tr>
  <tr><th>Entry angle</th><td>${ea(r.cls)}</td>${same ? '' : `<td>${ea(tw.cls)}</td>`}</tr>
  <tr><th>Flight time</th><td>${PATHS.main.T.toFixed(2)} s</td>${same ? '' : `<td>${PATHS.twin.T.toFixed(2)} s</td>`}</tr>
  <tr><th>Wheel</th><td colspan="2">${r.rpm.toFixed(0)} rpm, ball spin ${r.ballSpinRpm.toFixed(0)} rpm</td></tr></table>
  <div style="color:var(--mute);margin-top:3px">PREDICTED (model output); drag, Cd and Magnus coefficients ASSUMED</div>`;
}

// ------------------------------------------------------------ flow slots
let RUNS = [];
const tok = { main: 0, twin: 0 };
const slots = {};
for (const k of ['main', 'twin']) {
  const g = new THREE.Group(); g.matrixAutoUpdate = false; g.visible = false; scene.add(g);
  const ball = new THREE.Mesh(new THREE.SphereGeometry(D_M / 2, 20, 14), new THREE.MeshStandardMaterial({ color: k === 'main' ? SPIN_COL : TWIN_COL, roughness: 0.5 }));
  scene.add(ball);
  slots[k] = { k, group: g, ball, view: null, entry: null, loading: false, off: 0, last: null, tFlow: 0, lastUpd: 0 };
}
function disposeObj(o) {
  o.traverse((c) => { c.geometry?.dispose(); const ms = Array.isArray(c.material) ? c.material : c.material ? [c.material] : []; for (const m of ms) { m.map?.dispose(); m.dispose(); } });
}
async function setCase(slot, entry) {
  if (slot.loading) return;
  slot.loading = true; $('load').textContent = 'Loading ' + (entry.label || entry.id) + '...';
  try {
    const url = `${BASE}/${entry.path}`, dir = url.slice(0, url.lastIndexOf('/'));
    const m = await (await fetch(url)).json();
    const v = new RunView(m, dir); await v.load();
    const kids = v.scene.children.filter((c) => !c.isLight);
    for (const c of kids) { v.scene.remove(c); slot.group.add(c); }
    for (const c of [...slot.group.children]) if (!kids.includes(c)) { slot.group.remove(c); disposeObj(c); }
    slot.view = v; slot.entry = entry; slot.tFlow = 0;
    v.streams.material.uniforms.uRes.value.set(innerWidth * DPR, innerHeight * DPR);
    slot.ball.visible = false;
    applyLayers(); updateCaps();
  } catch (e) { console.error(e); $('load').textContent = 'Load failed: ' + e.message; }
  slot.loading = false; if (!slot.loading) $('load').textContent = '';
}
const ST = () => ({ stream: $('lStream').checked, vortex: $('lVortex').checked, q: +$('qLevel').value, planes: [$('lY').checked, $('lZ').checked],
  field: $('sField').value, cont: $('lCont').checked, sop: +$('sOp').value });
function applyLayers() {
  const s = ST();
  for (const k of ['main', 'twin']) {
    const v = slots[k].view; if (!v) continue;
    v.streams.visible = s.stream; v.streams.material.uniforms.uWidth.value = 1.3 * DPR; v.streams.material.uniforms.uAnim.value = 1;
    v.body.visible = true;
    v.vortex.forEach((m, i) => { m.visible = s.vortex && i === Math.min(s.q, v.vortex.length - 1); });
    v.slices.forEach((o, i) => {
      o.group.visible = !!s.planes[i];
      o.mat.map = v.fr ? o.ftex : o.tex[s.field]; o.mat.opacity = s.sop; o.mat.needsUpdate = true;
      o.lines.speed.visible = s.cont && s.field === 'speed'; o.lines.vort.visible = s.cont && s.field === 'vort';
    });
    if (v.fr) v.dirty = true;
  }
  need = true;
}
// nearest case: local speed (log) and local spin ratio; animated series preferred only when asked
function pick(speed, S, wantS0) {
  const prefAnim = $('lAnimCase').checked;
  let best = null, bd = 1e9;
  for (const r of RUNS) {
    const Sc = wantS0 ? 0 : r.S;
    if (wantS0 && Math.abs(r.S) > 1e-6) continue;
    const anim = (r.n_frames || 0) >= 10;
    const d = Math.pow(Math.log(speed / r.speed_mps) / 0.3, 2) + Math.pow((S - Sc) / 0.25, 2) + (anim === prefAnim ? 0 : 0.05);
    if (d < bd) { bd = d; best = r; }
  }
  return best;
}
const fmt = (x) => (+x).toFixed(2).replace(/\.?0+$/, '');
function caption(k, speed, S) {
  const s = slots[k]; if (!s.entry) return '';
  const e = s.entry, m = s.view.m;
  const nm = k === 'main' ? (U.S === 0 ? 'No-spin shot' : `Backspin shot (S ${U.S})`) : 'No-spin twin';
  return `<b>${esc(nm)}</b>nearest CFD case ${fmt(e.speed_mps)} m/s S${fmt(e.S)} (ball now ${speed.toFixed(1)} m/s, S${S.toFixed(2)}) | ` +
    `<span class="${m.synthetic ? 'syn' : 'pred'}">${m.synthetic ? 'SYNTHETIC TEST FIELD - not CFD' : 'PREDICTED'}</span> | ball-frame flow | orientation ${esc(e.orientation || m.orientation || 'btw')} ASSUMED`;
}
let capNow = { main: [0, 0], twin: [0, 0] };
function updateCaps() {
  for (const k of ['main', 'twin']) $(k === 'main' ? 'capM' : 'capT').innerHTML = (k === 'twin' && U.S === 0) ? '' : caption(k, ...capNow[k]);
  $('banner').style.display = ['main', 'twin'].some((k) => slots[k].view?.m.synthetic) ? 'block' : 'none';
  $('banner').textContent = 'SYNTHETIC TEST FIELD — not CFD';
}

// ------------------------------------------------------------ per-frame placement
const MB = new THREE.Matrix4(), V3 = new THREE.Vector3(), X = new THREE.Vector3(), Y = new THREE.Vector3(), Z = new THREE.Vector3();
let offVec = new THREE.Vector3();
function applyOffsets() {
  const a = PATHS.twin?.axis || new THREE.Vector3(0, 1, 0), o = +$('dOff').value;
  offVec = a.clone().multiplyScalar(o); $('dOffo').textContent = o.toFixed(2) + ' m';
  if (pathLines.twin) pathLines.twin.position.copy(offVec);
}
function place(k, P, tSim, show) {
  const s = slots[k];
  const i = Math.min(P.n - 1, Math.round(tSim / P.dt)), t = i * P.dt;
  const pos = V3.set(P.p.x[i], P.p.y[i], P.p.z[i]);
  if (k === 'twin') pos.add(offVec);
  const speed = P.sp[i], Sl = P.Sloc(i, t);
  capNow[k] = [speed, Sl];
  s.ball.position.copy(pos); s.ball.visible = show && !s.view;
  s.group.visible = show && !!s.view && (k === 'main' || $('dTwinFlow').checked);
  if (!show) { s.ball.visible = false; return pos.clone(); }
  // choose / switch the CFD case with a little hysteresis
  const want = pick(speed, Sl, k === 'twin');
  if (want && (!s.entry || (s.entry.id !== want.id && !s.loading && (s.last == null || performance.now() - s.last > 400)))) {
    if (!s.entry || pickScore(want, speed, Sl, k) + 0.1 < pickScore(s.entry, speed, Sl, k)) { s.last = performance.now(); setCase(s, want).then(() => updateCaps()); }
  }
  // basis: CFD +x = air relative to the ball (against the ball's velocity), CFD y = spin axis, z = x cross y
  X.set(-P.vx[i], -P.vy[i], -P.vz[i]).normalize();
  Y.copy(P.axis); Y.addScaledVector(X, -Y.dot(X)); if (Y.lengthSq() < 1e-9) Y.set(0, 1, 0).addScaledVector(X, -X.y); Y.normalize();
  Z.crossVectors(X, Y);
  const sc = D_M * +$('dMag').value;
  MB.makeBasis(X.multiplyScalar(sc), Y.multiplyScalar(sc), Z.multiplyScalar(sc)); MB.setPosition(pos);
  s.group.matrix.copy(MB); s.group.matrixWorldNeedsUpdate = true;
  return pos.clone();
}
function pickScore(r, speed, S, k) {
  const Sc = k === 'twin' ? 0 : r.S;
  return Math.pow(Math.log(speed / r.speed_mps) / 0.3, 2) + Math.pow((S - Sc) / 0.25, 2);
}

// ------------------------------------------------------------ interaction
let need = true, dragging = false;
const ray = new THREE.Raycaster(), plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0), hit = new THREE.Vector3();
function ndc(ev) { const r = canvas.getBoundingClientRect(); return new THREE.Vector2(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1); }
canvas.addEventListener('pointerdown', (ev) => {
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
for (const id of ['lStream', 'lVortex', 'qLevel', 'lY', 'lZ', 'sField', 'lCont', 'sOp', 'dTwinFlow']) $(id).addEventListener('input', applyLayers);
$('dOff').addEventListener('input', () => { applyOffsets(); need = true; });
$('dMode').addEventListener('change', () => { need = true; });
$('lAnimCase').addEventListener('change', () => { for (const k of ['main', 'twin']) slots[k].last = null; });
$('tPlay').onclick = () => { U.play = !U.play; $('tPlay').textContent = U.play ? 'Pause' : 'Play'; };
$('tSlide').addEventListener('input', () => { U.tSim = +$('tSlide').value; });
$('cOver').onclick = () => { $('cMode').value = 'free'; camera.position.copy(OVER.pos); controls.target.copy(OVER.tgt); };
$('cMode').addEventListener('change', () => { if ($('cMode').value !== 'free') followInit = true; });
let followInit = true;
$('bSuggest').onclick = () => {
  $('sgNote').textContent = 'solving...';
  setTimeout(() => {
    const q = qNow(META._q);
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
  for (const k of ['main', 'twin']) slots[k].view?.streams.material.uniforms.uRes.value.set(w * DPR, h * DPR);
  need = true;
}
addEventListener('resize', resize);

// ------------------------------------------------------------ loop
let lastT = 0;
function render(t) {
  requestAnimationFrame(render);
  const dtS = Math.min(0.1, Math.max(0, (t - lastT) / 1000)); lastT = t;
  if (!PATHS.main) return;
  const T = Math.max(PATHS.main.T, PATHS.twin.T);
  if (U.play) {
    U.tSim += dtS * +$('tSpd').value;
    if (U.tSim > T) { if ($('tLoop').checked) U.tSim = 0; else { U.tSim = T; U.play = false; $('tPlay').textContent = 'Play'; } }
  }
  $('tSlide').value = String(U.tSim);
  const both = $('dMode').value === 'both' && U.S !== 0;
  const showMain = $('dMode').value === 'both' || U.S === 0;
  const pm = place('main', PATHS.main, U.tSim, showMain);
  const pt = place('twin', PATHS.twin, U.tSim, both || $('dMode').value === 'twin');
  $('tLab').textContent = `flight t = ${U.tSim.toFixed(2)} s of ${T.toFixed(2)} s | PREDICTED path`;
  for (const k of ['main', 'twin']) {
    const s = slots[k], v = s.view; if (!v) continue;
    v.streams.material.uniforms.uTime.value = t / 1000;
    if (v.fr && s.group.visible) {
      s.tFlow += dtS * 8; const n = v.fr.n, ft = s.tFlow % n;
      if (t - s.lastUpd > 33) { v.setTime(ft, ST()); s.lastUpd = t; }
      v.stepParticles(dtS, false);
    }
  }
  updateCapsThrottled(t);
  const fol = $('cMode').value;
  if (fol !== 'free') {
    const tgt = fol === 'follow' && showMain ? pm : pt;
    if (followInit) { camera.position.copy(tgt).add(new THREE.Vector3(-0.28, -0.42, 0.2)); controls.target.copy(tgt); followInit = false; }
    else { V3.copy(tgt).sub(controls.target); camera.position.add(V3); controls.target.copy(tgt); }
  }
  controls.update();
  renderer.setClearColor(new THREE.Color(cssVar('--bg') || '#0a0e16'), 1);
  renderer.render(scene, camera);
}
let capT = 0;
function updateCapsThrottled(t) { if (t - capT > 150) { capT = t; updateCaps(); } }

// ------------------------------------------------------------ boot
async function boot() {
  resize();
  try {
    const fi = await (await fetch(FIELD_URL)).json();
    META = fi;
    META._q = { grid: fi.grid, sections: fi.sections, frame: fi.frame, field_grid: fi.field_grid, cases: fi.cases.map((c) => ({ S: c.S, var: c.var, params: c.params })) };
  } catch (e) { $('load').textContent = 'Field data not found (' + FIELD_URL + '). Build the explorer data first.'; return; }
  buildField(META);
  const Ss = [...new Set(META.cases.map((c) => c.S))].sort((a, b) => a - b);
  $('sS').innerHTML = Ss.map((s) => `<option value="${s}">${s === 0 ? 'S 0 (no spin)' : 'S ' + s + ' (backspin)'}</option>`).join('');
  if (!Ss.includes(U.S)) U.S = Ss[Ss.length - 1];
  try {
    const idx = await (await fetch(`${BASE}/index.json`)).json();
    RUNS = (idx.runs || []).map((r) => {
      const sp = r.speed_mps ?? parseFloat((/([0-9.]+)\s*m\/s/.exec(r.label || '') || [])[1]);
      const S = r.S ?? parseFloat((/\bS\s*([0-9.]+)/.exec(r.label || '') || [])[1] || 0);
      return Object.assign({}, r, { speed_mps: sp, S: isFinite(S) ? S : 0 });
    }).filter((r) => isFinite(r.speed_mps));
  } catch (e) { RUNS = []; }
  if (!RUNS.length) $('load').textContent = 'No CFD cases found in ' + BASE + '/index.json';
  if (params.get('x')) { U.x = +params.get('x'); U.y = +params.get('y') || U.y; }
  if (params.get('v')) U.v = +params.get('v');
  if (params.get('th')) U.th = +params.get('th');
  if (params.get('S')) U.S = +params.get('S');
  if (params.get('hd')) U.hd = +params.get('hd');
  updateShotUi();
  if (innerWidth < 700) $('panel').open = false;
  if (params.get('hidepanel')) $('panel').style.display = 'none';
  if (!rebuildShot()) { U.x = -1.0; U.y = 0.2; U.hd = 0; rebuildShot(); }
  updateRobot();
  if (!params.get('v') && !params.get('x')) $('bSuggest').click();
  if (params.get('cam')) $('cMode').value = params.get('cam');
  if (params.get('mag')) $('dMag').value = params.get('mag');
  if (params.get('off')) { $('dOff').value = params.get('off'); applyOffsets(); }
  if (params.get('plane')) { $('lY').checked = params.get('plane').includes('a'); $('lZ').checked = params.get('plane').includes('b'); }
  if (params.get('anim')) $('lAnimCase').checked = true;
  if (params.get('t')) U.tSim = +params.get('t');
  if (params.get('play')) $('tPlay').click();
  if (params.get('free')) { $('cMode').value = 'free'; }
  requestAnimationFrame(render);
}
boot().catch((e) => { console.error(e); $('load').textContent = 'Failed: ' + e.message; });
