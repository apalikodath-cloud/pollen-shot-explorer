import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RunView, loadArrays, esc, cssVar, turbo, rdbu, env } from './flowview.js';

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

let views = [null, null];
// ---- transport (time series)
const T = { t: 0, play: false, fps: 8, last: 0, shown: -1, lastUpd: 0 };
const frameViews = () => views.filter((v, i) => v && v.fr && (i === 0 || ($('cmp').checked && views[1])));
function tCount() { const fv = frameViews(); return fv.length ? Math.min(...fv.map((v) => v.fr.n)) : 0; }
function updateTransport() {
  const n = tCount();
  $('tbar').style.display = n > 1 ? '' : 'none';
  if (n > 1) $('tSlide').max = String(n - 1);
  const v = frameViews()[0]; if (!v) return;
  const fr = v.fr.info, ts = fr.t_star, t = Math.min(n - 1, T.t);
  const a = Math.floor(t), b = Math.min(ts.length - 1, a + 1), tt = ts[a] + (ts[b] - ts[a]) * (t - a);
  const U = v.m.U_mps, D = v.m.D_mm;
  const ms = U && D ? ` = ${(tt * D / U).toFixed(1)} ms of flow` : '';
  $('tLab').textContent = `t* ${tt.toFixed(2)}${ms} | PREDICTED`;
}
$('tPlay').onclick = () => { T.play = !T.play; $('tPlay').textContent = T.play ? 'Pause' : 'Play'; need = true; };
$('tSlide').addEventListener('input', () => { T.t = +$('tSlide').value; need = true; });

const loadTok = [0, 0];
let need = true, tween = null;
controls.addEventListener('change', () => { need = true; });
const state = () => ({
  stream: $('lStream').checked, anim: $('lAnim').checked, vortex: $('lVortex').checked, q: +$('qLevel').value,
  body: $('lBody').checked, planes: [$('lY').checked, $('lZ').checked], field: $('sField').value, cont: $('lCont').checked,
  sop: +$('sOp').value, width: +$('wStream').value,
});

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
  drawLegend(s);
  need = true;
}

function drawLegend(s) {
  const v = views.find(Boolean);
  const el = $('legend');
  if (!v) { el.style.display = 'none'; return; }
  el.style.display = '';
  const m = v.m, showVort = s.field === 'vort' && s.planes.some(Boolean);
  const act = m.slices.find((_, i) => s.planes[i]) || m.slices[0];
  const vr = (act && act.vort_range ? act.vort_range[1] : m.vort_range[1]);
  const rows = [];
  rows.push({ title: 'Streamlines: speed |u|/U', lo: '0', hi: m.speed_range[1].toFixed(1), f: (t) => turbo(t) });
  if (s.planes.some(Boolean) && !showVort) rows.push({ title: 'Slice: speed |u|/U', lo: '0', hi: m.speed_range[1].toFixed(1), f: (t) => turbo(t) });
  if (showVort) rows.push({ title: 'Slice: vorticity (U/D)', lo: (-vr).toFixed(1), hi: '+' + vr.toFixed(1), f: (t) => rdbu(t * 2 - 1) });
  if (s.vortex) rows.push({ title: 'Vortex cores: streamwise vorticity sign', lo: 'against', hi: 'with flow', f: (t) => rdbu(t * 2 - 1) });
  el.innerHTML = rows.map((r, i) => `<div>${esc(r.title)}</div><canvas data-i="${i}" width="200" height="12"></canvas><div class="lab"><span>${r.lo}</span><span>${r.hi}</span></div>`).join('');
  el.querySelectorAll('canvas').forEach((c) => {
    const r = rows[+c.dataset.i], x = c.getContext('2d');
    for (let i = 0; i < 200; i++) { const [R, G, B] = r.f(i / 199); x.fillStyle = `rgb(${R * 255 | 0},${G * 255 | 0},${B * 255 | 0})`; x.fillRect(i, 0, 1, 12); }
  });
}

async function loadRun(entry, slot) {
  $('load').textContent = 'Loading ' + entry.label + '...';
  const url = `${BASE}/${entry.path}`;
  const dir = url.slice(0, url.lastIndexOf('/'));
  const m = await (await fetch(url)).json();
  const tok = (loadTok[slot] = (loadTok[slot] || 0) + 1);
  const v = new RunView(m, dir);
  await v.load();
  if (tok !== loadTok[slot]) { v.dispose(); return; }
  const old = views[slot];
  views[slot] = v;
  if (old) old.dispose();
  v.streams.material.uniforms.uRes.value.set(innerWidth * DPR, innerHeight * DPR);
  $('load').textContent = '';
  const sl = views[0].m.slices;
  if (slot === 0) { $('nA').textContent = sl[0] ? `Plane ${sl[0].tag.replace('0', '=0')}` : '-'; $('nB').textContent = sl[1] ? `Plane ${sl[1].tag.replace('0', '=0')}` : '-'; }
  applyLayers(); updateChrome(); T.shown = -1; updateTransport();
}

function updateChrome() {
  const cmp = $('cmp').checked && views[1];
  $('capA').innerHTML = views[0] ? views[0].caption() : '';
  $('capB').innerHTML = cmp ? views[1].caption() : '';
  $('capB').style.display = cmp ? '' : 'none';
  if (!cmp) $('capA').style.maxWidth = '70vw'; else $('capA').style.maxWidth = '';
  const syn = views.some((v, i) => v && (i === 0 || cmp) && v.m.synthetic);
  const b = $('banner');
  b.style.display = syn ? 'block' : 'none';
  b.textContent = 'SYNTHETIC TEST FIELD — not CFD';
  $('capB').style.left = 'auto';
  if (window.innerWidth > 700) $('capB').style.left = (innerWidth / 2 + 8) + 'px';
  if (window.innerWidth > 700 && cmp) $('capA').style.left = '308px';
  else if (window.innerWidth > 700) $('capA').style.left = '308px';
  need = true;
}

function resize() {
  const w = innerWidth, h = innerHeight;
  renderer.setSize(w, h, false);
  for (const v of views) v?.streams.material.uniforms.uRes.value.set(w * DPR, h * DPR);
  updateChrome(); need = true;
}
addEventListener('resize', resize);
matchMedia('(prefers-color-scheme: dark)').addEventListener?.('change', () => { views.forEach((v) => v?.applyTheme()); need = true; });

function setView(pos, tgt) { tween = { t0: performance.now(), p0: camera.position.clone(), g0: controls.target.clone(), p1: pos, g1: tgt }; }
function focusOn(pt) {
  const dir = camera.position.clone().sub(controls.target);
  const d = Math.max(controls.minDistance * 1.5, Math.min(dir.length() * 0.45, 0.6));
  setView(pt.clone().add(dir.normalize().multiplyScalar(d)), pt.clone());
}
$('bReset').onclick = () => setView(HOME.pos.clone(), HOME.tgt.clone());
$('bBody').onclick = () => setView(new THREE.Vector3(0.9, 0.7, 2.0), new THREE.Vector3(0.1, 0, 0));
$('bWake').onclick = () => setView(new THREE.Vector3(2.6, 1.0, 2.8), new THREE.Vector3(1.0, 0, 0));

const ray = new THREE.Raycaster();
function onDbl(ev) {
  const r = canvas.getBoundingClientRect();
  const cmp = $('cmp').checked && views[1];
  const hx = (ev.clientX - r.left) / r.width;
  const slot = cmp && hx > 0.5 ? 1 : 0;
  const v = views[slot]; if (!v) return;
  const ndcx = cmp ? ((hx * 2) % 1) * 2 - 1 : hx * 2 - 1;
  ray.setFromCamera(new THREE.Vector2(ndcx, -((ev.clientY - r.top) / r.height) * 2 + 1), camera);
  const objs = [v.body, ...v.vortex.filter((m) => m.visible), ...v.slices.filter((o) => o.group.visible).map((o) => o.mesh)].filter((o) => o.visible !== false);
  const hit = ray.intersectObjects(objs, false)[0];
  if (hit) focusOn(hit.point);
}
canvas.addEventListener('dblclick', onDbl);
let lastTap = 0;
canvas.addEventListener('pointerup', (e) => { if (e.pointerType === 'touch') { const n = performance.now(); if (n - lastTap < 300) onDbl(e); lastTap = n; } });

for (const id of ['lStream', 'wStream', 'lAnim', 'lVortex', 'qLevel', 'lBody', 'lY', 'lZ', 'sField', 'lCont', 'sOp', 'lPart']) $(id).addEventListener('input', applyLayers);
$('cmp').addEventListener('change', () => { updateChrome(); T.shown = -1; updateTransport(); });

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
  if (nfr > 1) {
    if (T.play) {
      T.t += dtS * T.fps * +$('tSpd').value;
      if (T.t > nfr - 1) { if ($('tLoop').checked) T.t = 0; else { T.t = nfr - 1; T.play = false; $('tPlay').textContent = 'Play'; } }
      $('tSlide').value = String(T.t);
    }
    const st = state();
    if ((T.t !== T.shown || frameViews().some((v) => v.dirty)) && t - T.lastUpd > 30) {
      for (const v of frameViews()) v.setTime(Math.min(T.t, v.fr.n - 1), st);
      T.shown = T.t; T.lastUpd = t; updateTransport(); need = true;
    }
    if ($('lPart').checked) { for (const v of frameViews()) v.stepParticles(dtS, true); ticking = true; }
    else for (const v of frameViews()) v.stepParticles(0, false);
  }
  const animating = ($('lAnim').checked && $('lStream').checked) || ticking || T.play;
  controls.update();
  if (!need && !animating) return;
  need = false;
  const W = innerWidth, H = innerHeight;
  const cmp = $('cmp').checked && views[1];
  const bg = new THREE.Color(cssVar('--bg') || '#0a0e16');
  renderer.setScissorTest(false); renderer.setClearColor(bg, 1); renderer.clear();
  renderer.setScissorTest(true);
  const list = cmp ? [views[0], views[1]] : [views[0]];
  list.forEach((v, i) => {
    if (!v) return;
    const w = cmp ? W / 2 : W;
    const x = i * w;
    renderer.setViewport(x, 0, w, H); renderer.setScissor(x, 0, w, H);
    camera.aspect = w / H; camera.updateProjectionMatrix();
    v.streams.material.uniforms.uTime.value = t / 1000;
    v.scene.background = null;
    v.key.position.copy(camera.position).add(new THREE.Vector3(0.4, 1, 0.2));
    v.key.target.position.copy(controls.target);
    renderer.render(v.scene, camera);
  });
}

async function boot() {
  resize();
  let idx = null;
  try { idx = await (await fetch(`${BASE}/index.json`)).json(); } catch (e) { idx = null; }
  const runs = (idx && idx.runs) || [];
  if (!runs.length) { $('empty').style.display = 'flex'; $('panel').style.display = 'none'; $('legend').style.display = 'none'; $('hint').style.display = 'none'; render(0); return; }
  for (const sel of [$('runA'), $('runB')]) sel.innerHTML = runs.map((r, i) => `<option value="${i}">${esc(r.label || r.id)}</option>`).join('');
  $('runB').value = String(Math.min(1, runs.length - 1));
  if (runs.length < 2) { $('cmp').disabled = true; $('runB').disabled = true; }
  $('runA').onchange = () => loadRun(runs[+$('runA').value], 0).catch(fail);
  $('runB').onchange = () => loadRun(runs[+$('runB').value], 1).catch(fail);
  $('cmp').addEventListener('change', async () => { if ($('cmp').checked && !views[1]) await loadRun(runs[+$('runB').value], 1).catch(fail); updateChrome(); });
  if (innerWidth < 700) $('panel').open = false;
  if (params.get('hidepanel')) $('panel').style.display = 'none';
  await loadRun(runs[0], 0).catch(fail);
  if (params.get('cmp') && runs.length > 1) { $('cmp').checked = true; await loadRun(runs[1], 1).catch(fail); updateChrome(); }
  if (params.get('view') === 'body') $('bBody').click();
  if (params.get('view') === 'wake') $('bWake').click();
  if (params.get('view') === 'zoom') setView(new THREE.Vector3(1.0, 0.5, 1.5), new THREE.Vector3(0.35, 0, 0.1));
  if (params.get('plane')) { $('lY').checked = params.get('plane').includes('a'); $('lZ').checked = params.get('plane').includes('b'); }
  if (params.get('field')) $('sField').value = params.get('field');
  if (params.get('nostream')) $('lStream').checked = false;
  if (params.get('noanim')) $('lAnim').checked = false;
  if (params.get('t')) { T.t = +params.get('t'); $('tSlide').value = String(T.t); }
  if (params.get('play')) $('tPlay').click();
  if (params.get('nopart')) $('lPart').checked = false;
  if (params.get('q') === '0') $('lVortex').checked = false;
  applyLayers();
  render(0);
}
function fail(e) { console.error(e); $('load').textContent = 'Load failed: ' + e.message; }
boot().catch(fail);
