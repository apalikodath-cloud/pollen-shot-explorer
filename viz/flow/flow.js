import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RunView, esc, cssVar, turbo, rdbu, env } from './flowview.js';

const $ = (id) => document.getElementById(id);
const params = new URLSearchParams(location.search);
const BASE = (params.get('flows') || 'flows').replace(/\/+$/, '');

// ------------------------------------------------------------ app
const canvas = $('gl');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, powerPreference: 'high-performance' });
const DPR = env.DPR;
renderer.setPixelRatio(DPR);
const camera = new THREE.PerspectiveCamera(40, 1, 0.003, 60);
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true; controls.dampingFactor = 0.09;
controls.minDistance = 0.05; controls.maxDistance = 14;
controls.zoomToCursor = true; controls.zoomSpeed = 1.2;
env.target = () => controls.target;
const HOME = { pos: new THREE.Vector3(1.2, 1.1, 5.4), tgt: new THREE.Vector3(0.7, 0, 0) };
camera.position.copy(HOME.pos); controls.target.copy(HOME.tgt);

let RUNS = [];
let views = [null, null];
const MAN = new Map();     // manifest cache by path
const MODE = { avg: params.get('avg') === '1' };
const fmt = (x) => (Math.abs(x - Math.round(x)) < 1e-6 ? String(Math.round(x)) : String(+x.toFixed(2)));
const niceCeil = (x) => { const s = [2, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30]; return s.find((v) => v >= x - 1e-9) || Math.ceil(x / 10) * 10; };

// ---- transport (time series)
const T = { t: 0, play: false, fps: 8, last: 0, shown: -1, lastUpd: 0 };
const shown = () => views.filter((v, i) => v && (i === 0 || ($('cmp').checked && views[1])));
const frameViews = () => shown().filter((v) => v.fr);
function tCount() { const fv = frameViews(); return fv.length ? Math.min(...fv.map((v) => v.fr.n)) : 0; }
function updateTransport() {
  const n = tCount();
  $('tbar').style.display = n > 1 ? '' : 'none';
  document.body.classList.toggle('series', n > 1);
  if (n > 1) $('tSlide').max = String(n - 1);
  const v = frameViews()[0]; if (!v || n < 2) return;
  const fr = v.fr.info, ts = fr.t_star, t = Math.min(n - 1, T.t);
  const a = Math.floor(t), b = Math.min(ts.length - 1, a + 1), tt = ts[a] + (ts[b] - ts[a]) * (t - a);
  const U = v.m.U_mps, D = v.m.D_mm;
  const ms = U && D ? ` = ${(tt * D / U).toFixed(1)} ms of flow` : '';
  $('tLab').textContent = `frame ${Math.round(t) + 1} of ${n} | t* ${tt.toFixed(2)}${ms} | PREDICTED`;
}
function setPlay(on) { T.play = on; $('tPlay').textContent = on ? 'Pause' : 'Play'; need = true; }
$('tPlay').onclick = () => setPlay(!T.play);
$('tSlide').addEventListener('input', () => { T.t = +$('tSlide').value; need = true; });

const loadTok = [0, 0];
let need = true, tween = null;
controls.addEventListener('change', () => { need = true; });
const state = () => ({
  stream: $('lStream').checked, anim: $('lAnim').checked, vortex: $('lVortex').checked, q: +$('qLevel').value,
  body: $('lBody').checked, planes: [$('lY').checked, $('lZ').checked], field: $('sField').value, cont: $('lCont').checked,
  sop: +$('sOp').value, width: +$('wStream').value,
});

// speed colours in m/s on one scale for both sides: a view's colour scale is speed_range[1] U / Vmax
function colourScale() {
  const vs = shown();
  const ok = vs.length && vs.every((v) => v.fr && v.m.U_mps > 0);
  if (!ok) { for (const v of vs) v.setColorScale(1); return null; }
  const vmax = niceCeil(Math.max(...vs.map((v) => v.m.speed_range[1] * v.m.U_mps)));
  for (const v of vs) v.setColorScale((v.m.speed_range[1] * v.m.U_mps) / vmax);
  return vmax;
}

function applyLayers() {
  const s = state();
  for (const v of views) {
    if (!v) continue;
    v.streams.visible = s.stream;
    v.streams.material.uniforms.uWidth.value = s.width * DPR;
    v.streams.material.uniforms.uAnim.value = s.anim ? 1 : 0;
    v.body.visible = s.body;
    v.vortex.forEach((m, i) => { m.visible = s.vortex && i === Math.min(s.q, v.vortex.length - 1); });
    v.slices.forEach((o, i) => {
      o.group.visible = !!s.planes[i];
      o.mat.map = v.fr ? o.ftex : o.tex[s.field]; o.mat.opacity = s.sop; o.mat.needsUpdate = true;
      o.lines.speed.visible = s.cont && s.field === 'speed';
      o.lines.vort.visible = s.cont && s.field === 'vort';
    });
  }
  for (const v of views) if (v && v.fr) v.dirty = true;
  drawLegend(s, colourScale());
  need = true;
}

function drawLegend(s, vmax) {
  const v = views.find(Boolean);
  const el = $('legend');
  if (!v) { el.style.display = 'none'; return; }
  el.style.display = '';
  const m = v.m, showVort = s.field === 'vort' && s.planes.some(Boolean);
  const act = v.sinfo.find((_, i) => s.planes[i]) || v.sinfo[0];
  const vr = (act && act.vort_range ? act.vort_range[1] : m.vort_range[1]);
  const rows = [];
  const spd = vmax ? { lo: '0', mid: fmt(vmax / 2), hi: fmt(vmax) } : { lo: '0', hi: m.speed_range[1].toFixed(1) };
  const what = (s.stream && s.planes.some(Boolean) && !showVort) ? 'Streamlines and slice' : s.planes.some(Boolean) && !showVort ? 'Slice' : 'Streamlines';
  if (s.stream || (s.planes.some(Boolean) && !showVort)) rows.push({ title: `${what}: air speed relative to the ball ${vmax ? '(m/s)' : '(|u|/U)'}`, ...spd, f: (t) => turbo(t) });
  if (showVort) rows.push({ title: 'Slice: vorticity (U/D)', lo: (-vr).toFixed(1), hi: '+' + vr.toFixed(1), f: (t) => rdbu(t * 2 - 1) });
  if (s.vortex) rows.push({ title: 'Vortex cores: turning sense along the flow', lo: 'against', hi: 'with flow', f: (t) => rdbu(t * 2 - 1) });
  el.innerHTML = rows.map((r, i) => `<div class="lr"><div>${esc(r.title)}</div><canvas data-i="${i}" width="200" height="10"></canvas><div class="lab"><span>${esc(r.lo)}</span>${r.mid ? `<span>${esc(r.mid)}</span>` : ''}<span>${esc(r.hi)}</span></div></div>`).join('');
  el.querySelectorAll('canvas').forEach((c) => {
    const r = rows[+c.dataset.i], x = c.getContext('2d');
    for (let i = 0; i < 200; i++) { const [R, G, B] = r.f(i / 199); x.fillStyle = `rgb(${R * 255 | 0},${G * 255 | 0},${B * 255 | 0})`; x.fillRect(i, 0, 1, 10); }
  });
}

const planeName = (sl) => (sl ? `(plane ${sl.tag.replace('0', ' = 0')})` : '');
async function loadRun(entry, slot) {
  $('load').textContent = 'Loading ' + (entry.label || entry.id) + '...';
  const url = `${BASE}/${entry.path}`;
  const dir = url.slice(0, url.lastIndexOf('/'));
  const tok = (loadTok[slot] = (loadTok[slot] || 0) + 1);
  let m = MAN.get(url);
  if (!m) { m = await (await fetch(url)).json(); MAN.set(url, m); }
  const v = new RunView(m, dir, { mean: MODE.avg });
  await v.load();
  if (tok !== loadTok[slot]) { v.dispose(); return; }
  const old = views[slot];
  views[slot] = v;
  if (old) old.dispose();
  v.streams.material.uniforms.uRes.value.set(innerWidth * DPR, innerHeight * DPR);
  v.applyTheme();
  $('load').textContent = '';
  if (slot === 0) { $('nA').textContent = planeName(v.sinfo[0]); $('nB').textContent = planeName(v.sinfo[1]); }
  applyLayers(); updateChrome(); T.shown = -1; updateTransport();
}

function updateChrome() {
  const cmp = $('cmp').checked && views[1];
  const side = (i) => (cmp ? `<i>${i ? 'right' : 'left'}</i>` : '');
  $('capA').innerHTML = views[0] ? side(0) + views[0].caption() : '';
  $('capB').innerHTML = cmp ? side(1) + views[1].caption() : '';
  $('capB').style.display = cmp ? '' : 'none';
  const syn = views.some((v, i) => v && (i === 0 || cmp) && v.m.synthetic);
  const b = $('banner');
  b.style.display = syn ? 'block' : 'none';
  b.textContent = 'SYNTHETIC TEST FIELD — not CFD';
  need = true;
}

function resize() {
  const w = innerWidth, h = innerHeight;
  renderer.setSize(w, h, false);
  for (const v of views) v?.streams.material.uniforms.uRes.value.set(w * DPR, h * DPR);
  updateChrome(); need = true;
}
addEventListener('resize', resize);
const retheme = () => { views.forEach((v) => v?.applyTheme()); need = true; };
matchMedia('(prefers-color-scheme: light)').addEventListener?.('change', retheme);
addEventListener('storage', (e) => {
  if (e.key !== 'pollen-theme') return;
  if (e.newValue === 'light' || e.newValue === 'dark') document.documentElement.dataset.theme = e.newValue; else delete document.documentElement.dataset.theme;
  retheme();
});

function setView(pos, tgt) { tween = { t0: performance.now(), p0: camera.position.clone(), g0: controls.target.clone(), p1: pos, g1: tgt }; }
function focusOn(pt) {
  const dir = camera.position.clone().sub(controls.target);
  const d = Math.max(controls.minDistance * 1.5, Math.min(dir.length() * 0.45, 0.6));
  setView(pt.clone().add(dir.normalize().multiplyScalar(d)), pt.clone());
}
$('bReset').onclick = () => setView(HOME.pos.clone(), HOME.tgt.clone());
$('bBody').onclick = () => setView(new THREE.Vector3(0.9, 0.7, 2.0), new THREE.Vector3(0.1, 0, 0));
$('bWake').onclick = () => setView(new THREE.Vector3(2.6, 1.0, 2.8), new THREE.Vector3(1.0, 0, 0));

// drawing area per view: on a wide screen the views start right of the panel, side by side when comparing
function viewports() {
  const W = innerWidth, cmp = $('cmp').checked && views[1];
  const x0 = W > 700 && $('panel').style.display !== 'none' ? Math.min(332, W * 0.3) : 0;
  const w = (W - x0) / (cmp ? 2 : 1);
  return cmp ? [[x0, w], [x0 + w, w]] : [[x0, w]];
}
const ray = new THREE.Raycaster();
function onDbl(ev) {
  const r = canvas.getBoundingClientRect();
  const px = ev.clientX - r.left, vp = viewports();
  const slot = vp.length > 1 && px >= vp[1][0] ? 1 : 0;
  const v = views[slot]; if (!v) return;
  const [x, w] = vp[slot];
  camera.aspect = w / r.height; camera.updateProjectionMatrix();
  ray.setFromCamera(new THREE.Vector2(((px - x) / w) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1), camera);
  const objs = [v.body, ...v.vortex.filter((m) => m.visible), ...v.slices.filter((o) => o.group.visible).map((o) => o.mesh)].filter((o) => o.visible !== false);
  const hit = ray.intersectObjects(objs, false)[0];
  if (hit) focusOn(hit.point);
}
canvas.addEventListener('dblclick', onDbl);
let lastTap = 0;
canvas.addEventListener('pointerup', (e) => { if (e.pointerType === 'touch') { const n = performance.now(); if (n - lastTap < 300) onDbl(e); lastTap = n; } });

for (const id of ['lStream', 'wStream', 'lAnim', 'lVortex', 'qLevel', 'lBody', 'lY', 'lZ', 'sField', 'lCont', 'sOp', 'lPart']) $(id).addEventListener('input', applyLayers);

// Averaged / Instant: rebuild the shown views from the cached manifests
async function setMode(avg) {
  MODE.avg = avg;
  for (const b of document.querySelectorAll('#vMode button')) b.setAttribute('aria-pressed', String((b.dataset.m === 'avg') === avg));
  if (!RUNS.length) return;
  setPlay(false);
  await loadRun(RUNS[+$('runA').value], 0).catch(fail);
  if (views[1]) await loadRun(RUNS[+$('runB').value], 1).catch(fail);
}
for (const b of document.querySelectorAll('#vMode button')) b.addEventListener('click', () => { if ((b.dataset.m === 'avg') !== MODE.avg) setMode(b.dataset.m === 'avg'); });

// phone layout: the panel folds to one line
function setPanel(open) { $('panel').classList.toggle('open', open); $('panelSum').setAttribute('aria-expanded', String(open)); }
$('panelSum').addEventListener('click', () => setPanel(!$('panel').classList.contains('open')));
$('panelSum').addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setPanel(!$('panel').classList.contains('open')); } });

function render(t) {
  requestAnimationFrame(render);
  if (tween) {
    const k = Math.min(1, (t - tween.t0) / 600), e = k * k * (3 - 2 * k);
    camera.position.lerpVectors(tween.p0, tween.p1, e); controls.target.lerpVectors(tween.g0, tween.g1, e);
    if (k >= 1) tween = null; need = true;
  }
  const dtS = Math.min(0.1, Math.max(0, (t - T.last) / 1000)); T.last = t;
  const nfr = tCount();
  let ticking = false;
  const st = state();
  if (nfr > 1) {
    if (T.play) {
      T.t += dtS * T.fps * +$('tSpd').value;
      if (T.t > nfr - 1) { if ($('tLoop').checked) T.t = 0; else { T.t = nfr - 1; setPlay(false); } }
      $('tSlide').value = String(T.t);
    }
    if ((T.t !== T.shown || frameViews().some((v) => v.dirty)) && t - T.lastUpd > 30) {
      for (const v of frameViews()) v.setTime(Math.min(T.t, v.fr.n - 1), st);
      T.shown = T.t; T.lastUpd = t; updateTransport(); need = true;
    }
    if ($('lPart').checked) { for (const v of frameViews()) v.stepParticles(dtS, true); ticking = true; }
    else for (const v of frameViews()) v.stepParticles(0, false);
  } else {
    // one stored field per slice (time mean or single snapshot): recolour when layers or colours change
    for (const v of frameViews()) if (v.dirty) { v.setTime(0, st); need = true; }
  }
  const animating = ($('lAnim').checked && $('lStream').checked) || ticking || T.play;
  controls.update();
  if (!need && !animating) return;
  need = false;
  const H = innerHeight, vp = viewports();
  const bg = new THREE.Color(cssVar('--bg') || '#0b1015');
  renderer.setScissorTest(false); renderer.setClearColor(bg, 1); renderer.clear();
  renderer.setScissorTest(true);
  vp.forEach(([x, w], i) => {
    const v = views[i];
    if (!v) return;
    renderer.setViewport(x, 0, w, H); renderer.setScissor(x, 0, w, H);
    camera.aspect = w / H; camera.updateProjectionMatrix();
    v.streams.material.uniforms.uTime.value = t / 1000;
    v.scene.background = null;
    v.key.position.copy(camera.position).add(new THREE.Vector3(0.4, 1, 0.2));
    v.key.target.position.copy(controls.target);
    renderer.render(v.scene, camera);
  });
}

// the no-spin case at the same speed (same kind of series when there is one)
function twinOf(i) {
  const r = RUNS[i];
  if (!(r.S > 0)) return -1;
  let best = -1, bs = Infinity;
  RUNS.forEach((c, j) => {
    if (c.S > 0 || !(Math.abs(c.speed_mps - r.speed_mps) < 1e-6)) return;
    const sc = Math.abs((c.n_frames || 0) - (r.n_frames || 0)) + (c.orientation === r.orientation ? 0 : 1000);
    if (sc < bs) { bs = sc; best = j; }
  });
  return best;
}
async function pickA(i) {
  $('runA').value = String(i);
  const tw = twinOf(i);
  const jobs = [loadRun(RUNS[i], 0)];
  if (tw >= 0) { $('runB').value = String(tw); $('cmp').checked = true; jobs.push(loadRun(RUNS[tw], 1)); }
  await Promise.all(jobs);
  updateChrome(); applyLayers(); T.shown = -1; updateTransport();
}

async function boot() {
  resize();
  let idx = null;
  try { idx = await (await fetch(`${BASE}/index.json`)).json(); } catch (e) { idx = null; }
  RUNS = ((idx && idx.runs) || []).map((r) => {
    const sp = r.speed_mps ?? parseFloat((/([0-9.]+)\s*m\/s/.exec(r.label || '') || [])[1]);
    const S = r.S ?? parseFloat((/\bS\s*([0-9.]+)/.exec(r.label || '') || [])[1] || 0);
    return Object.assign({}, r, { speed_mps: sp, S: isFinite(S) ? S : 0 });
  });
  if (!RUNS.length) { $('empty').style.display = 'flex'; $('panel').style.display = 'none'; $('legend').style.display = 'none'; $('hint').style.display = 'none'; render(0); return; }
  for (const sel of [$('runA'), $('runB')]) sel.innerHTML = RUNS.map((r, i) => `<option value="${i}">${esc(r.label || r.id)}</option>`).join('');
  $('runB').value = String(Math.min(1, RUNS.length - 1));
  if (RUNS.length < 2) { $('cmp').disabled = true; $('runB').disabled = true; }
  $('runA').onchange = () => pickA(+$('runA').value).catch(fail);
  $('runB').onchange = () => { if ($('cmp').checked) loadRun(RUNS[+$('runB').value], 1).catch(fail); };
  $('cmp').addEventListener('change', async () => {
    if ($('cmp').checked && !views[1]) await loadRun(RUNS[+$('runB').value], 1).catch(fail);
    updateChrome(); applyLayers(); T.shown = -1; updateTransport();
  });
  for (const b of document.querySelectorAll('#vMode button')) b.setAttribute('aria-pressed', String((b.dataset.m === 'avg') === MODE.avg));
  if (params.get('hidepanel')) $('panel').style.display = 'none';
  if (params.get('plane')) { $('lY').checked = params.get('plane').includes('a'); $('lZ').checked = params.get('plane').includes('b'); }
  if (params.get('field')) $('sField').value = params.get('field');
  if (params.get('nostream')) $('lStream').checked = false;
  if (params.get('noanim')) $('lAnim').checked = false;
  if (params.get('nopart')) $('lPart').checked = false;
  if (params.get('q') === '0') $('lVortex').checked = false;
  const want = params.get('run'), i0 = Math.max(0, RUNS.findIndex((r) => r.id === want));
  await pickA(i0).catch(fail);
  if (params.get('cmp') && RUNS.length > 1 && !views[1]) {
    $('runB').value = String(i0 === 1 ? 0 : 1); $('cmp').checked = true;
    await loadRun(RUNS[+$('runB').value], 1).catch(fail); updateChrome();
  }
  if (params.get('view') === 'body') $('bBody').click();
  if (params.get('view') === 'wake') $('bWake').click();
  if (params.get('view') === 'zoom') setView(new THREE.Vector3(1.0, 0.5, 1.5), new THREE.Vector3(0.35, 0, 0.1));
  if (params.get('t')) { T.t = +params.get('t'); $('tSlide').value = String(T.t); }
  if (params.get('play')) setPlay(true);
  applyLayers();
  render(0);
}
function fail(e) { console.error(e); $('load').textContent = 'Load failed: ' + e.message; }
boot().catch(fail);
