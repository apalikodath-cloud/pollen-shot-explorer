// Shared flow-bundle renderer: RunView (streamlines, Q surfaces, body, contour slices, time series).
// Used by flow.js (viewer) and shot.js (shot scene).
// new RunView(manifest, dir, { mean: true }) draws the bundle's time-mean layer set (manifest.mean)
// when it has one; otherwise the instantaneous layers. setColorScale() rescales the speed colours
// (streamlines and slices) and setFade() crossfades a whole run in or out.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

export const env = { DPR: Math.min(window.devicePixelRatio || 1, 2), target: () => new THREE.Vector3() };
export const cssVar = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();

// ------------------------------------------------------------ colour maps
export function turbo(t) { // Google's polynomial approximation of turbo
  t = Math.min(1, Math.max(0, t));
  const r = 0.13572138 + t * (4.6153926 + t * (-42.66032258 + t * (132.13108234 + t * (-152.94239396 + t * 59.28637943))));
  const g = 0.09140261 + t * (2.19418839 + t * (4.84296658 + t * (-14.18503333 + t * (4.27729857 + t * 2.82956604))));
  const b = 0.1066733 + t * (12.64194608 + t * (-60.58204836 + t * (110.36276771 + t * (-89.90310912 + t * 27.34824973))));
  return [Math.min(1, Math.max(0, r)), Math.min(1, Math.max(0, g)), Math.min(1, Math.max(0, b))];
}
export function rdbu(v) { // v in [-1,1]; negative blue, positive red
  const lerp = (a, b, t) => a.map((x, i) => (x + (b[i] - x) * t) / 255);
  const B = [33, 102, 172], W = [240, 240, 240], R = [178, 24, 43];
  return v < 0 ? lerp(W, B, Math.min(1, -v)) : lerp(W, R, Math.min(1, v));
}
export const TURBO_GLSL = `
vec3 turbo(float t){ t=clamp(t,0.,1.);
 float r=0.13572138+t*(4.6153926+t*(-42.66032258+t*(132.13108234+t*(-152.94239396+t*59.28637943))));
 float g=0.09140261+t*(2.19418839+t*(4.84296658+t*(-14.18503333+t*(4.27729857+t*2.82956604))));
 float b=0.1066733+t*(12.64194608+t*(-60.58204836+t*(110.36276771+t*(-89.90310912+t*27.34824973))));
 return clamp(vec3(r,g,b),0.,1.);}`;

// ------------------------------------------------------------ data helpers
const DT = { uint8: Uint8Array, int8: Int8Array, uint16: Uint16Array, int16: Int16Array, uint32: Uint32Array, float32: Float32Array };
export async function loadArrays(dir, entry) {
  const buf = await (await fetch(`${dir}/${entry.url}`)).arrayBuffer();
  const out = {};
  for (const a of entry.arrays) out[a.name] = new DT[a.dtype](buf, a.offset, a.length);
  return out;
}
const dequant = (u16, lo, hi) => {
  const o = new Float32Array(u16.length);
  for (let i = 0; i < u16.length; i += 3) for (let k = 0; k < 3; k++) o[i + k] = lo[k] + (u16[i + k] / 65535) * (hi[k] - lo[k]);
  return o;
};
const AX = { x: 0, y: 1, z: 2 };

// ------------------------------------------------------------ fat, animated streamlines
function makeStreamlines(m, arr) {
  const lo = m.bounds.lo, hi = m.bounds.hi;
  const pos = dequant(arr.pos, lo, hi);
  const counts = arr.counts, spd = arr.speed;
  let nseg = 0;
  for (const c of counts) nseg += Math.max(0, c - 1);
  const A = new Float32Array(nseg * 3), B = new Float32Array(nseg * 3), D = new Float32Array(nseg * 4);
  let v = 0, s = 0;
  for (const c of counts) {
    let arc = 0;
    for (let i = 0; i < c - 1; i++, s++) {
      const p = (v + i) * 3, q = p + 3;
      const dl = Math.hypot(pos[q] - pos[p], pos[q + 1] - pos[p + 1], pos[q + 2] - pos[p + 2]);
      A.set(pos.subarray(p, p + 3), s * 3); B.set(pos.subarray(q, q + 3), s * 3);
      D[s * 4] = spd[v + i] / 255; D[s * 4 + 1] = spd[v + i + 1] / 255; D[s * 4 + 2] = arc; D[s * 4 + 3] = arc + dl;
      arc += dl;
    }
    v += c;
  }
  const g = new THREE.InstancedBufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array([0, -1, 0, 0, 1, 0, 1, -1, 0, 1, 1, 0]), 3));
  g.setIndex([0, 2, 1, 1, 2, 3]);
  g.setAttribute('iStart', new THREE.InstancedBufferAttribute(A, 3));
  g.setAttribute('iEnd', new THREE.InstancedBufferAttribute(B, 3));
  g.setAttribute('iData', new THREE.InstancedBufferAttribute(D, 4));
  g.instanceCount = nseg;
  const mat = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false,
    uniforms: { uRes: { value: new THREE.Vector2(1, 1) }, uWidth: { value: 1.8 }, uTime: { value: 0 }, uAnim: { value: 1 }, uOpacity: { value: 0.72 }, uScale: { value: 1 } },
    vertexShader: `
      attribute vec3 iStart; attribute vec3 iEnd; attribute vec4 iData;
      uniform vec2 uRes; uniform float uWidth;
      varying float vSpeed; varying float vArc; varying float vSide;
      void main(){
        vec4 va = modelViewMatrix*vec4(iStart,1.), vb = modelViewMatrix*vec4(iEnd,1.);
        float n = 0.004;
        if (va.z > -n && vb.z > -n) { gl_Position = vec4(2.,2.,2.,1.); return; }
        float ta = 0., tb = 1.;
        if (va.z > -n) ta = (va.z+n)/(va.z-vb.z);
        if (vb.z > -n) tb = 1. - (vb.z+n)/(vb.z-va.z);
        vec4 wa = mix(va,vb,ta), wb = mix(va,vb,tb);
        vec4 ca = projectionMatrix*wa, cb = projectionMatrix*wb;
        vec2 na = ca.xy/ca.w, nb = cb.xy/cb.w;
        vec2 d = (nb-na)*uRes; float L = length(d);
        d = L > 1e-6 ? d/L : vec2(1.,0.);
        vec2 nrm = vec2(-d.y, d.x);
        float e = position.x;
        vec4 c = mix(ca, cb, e);
        c.xy += nrm * position.y * (uWidth/uRes) * c.w;
        gl_Position = c;
        float tt = mix(ta, tb, e);
        vSpeed = mix(iData.x, iData.y, tt); vArc = mix(iData.z, iData.w, tt); vSide = position.y;
      }`,
    fragmentShader: `
      uniform float uTime; uniform float uAnim; uniform float uOpacity; uniform float uScale;
      varying float vSpeed; varying float vArc; varying float vSide;
      ${TURBO_GLSL}
      void main(){
        vec3 col = turbo(vSpeed * uScale);
        float a = uOpacity * (1. - smoothstep(0.55, 1.0, abs(vSide)));
        if (uAnim > 0.5) {
          float ph = fract(vArc/0.32 - uTime*0.9);
          float dash = smoothstep(0.0,0.08,ph) * (1.-smoothstep(0.22,0.4,ph));
          a *= mix(0.22, 1.0, dash);
          col = mix(col, vec3(1.), 0.35*dash);
        }
        gl_FragColor = vec4(col, a);
      }`,
  });
  const mesh = new THREE.Mesh(g, mat);
  mesh.frustumCulled = false;
  mesh.renderOrder = 2;
  return mesh;
}

// ------------------------------------------------------------ one run
export class RunView {
  constructor(manifest, dir, opts = {}) {
    this.m = manifest; this.dir = dir;
    this.mean = !!(opts.mean && manifest.mean);   // time-mean layer set (falls back to instantaneous)
    this.src = this.mean ? manifest.mean : manifest;
    this.sinfo = this.src.slices; this.cscale = 1; this.fade = 1;
    this.scene = new THREE.Scene();
    this.scene.add(new THREE.HemisphereLight(0xffffff, 0x556070, 1.1));
    this.key = new THREE.DirectionalLight(0xffffff, 2.2);
    this.scene.add(this.key);
    this.fill = new THREE.DirectionalLight(0xbcd0ff, 0.6);
    this.fill.position.set(-1, -1, -1);
    this.scene.add(this.fill);
    this.slices = []; this.vortex = [];
  }

  async load() {
    const m = this.m, src = this.src, f = src.files;
    const [sl, vx, sc, bd] = await Promise.all([f.streamlines, f.vortex, f.slices, m.files.body].map((e) => loadArrays(this.dir, e)));
    const lo = m.bounds.lo, hi = m.bounds.hi;
    this.streams = makeStreamlines(m, sl);
    this.scene.add(this.streams);

    const bg = new THREE.BufferGeometry();
    bg.setAttribute('position', new THREE.BufferAttribute(bd.pos.slice(), 3));
    const nrm = new Float32Array(bd.normal.length);
    for (let i = 0; i < nrm.length; i++) nrm[i] = bd.normal[i] / 127;
    bg.setAttribute('normal', new THREE.BufferAttribute(nrm, 3));
    bg.setIndex(new THREE.BufferAttribute(bd.idx.slice(), 1));
    this.body = new THREE.Mesh(bg, new THREE.MeshStandardMaterial({ color: 0xaeb4bd, roughness: 0.5, metalness: 0.15, side: THREE.DoubleSide }));
    this.scene.add(this.body);

    for (const lv of src.vortex_levels) {
      const g = new THREE.BufferGeometry();
      g.setAttribute('position', new THREE.BufferAttribute(dequant(vx['pos' + lv.index], lo, hi), 3));
      const om = vx['omega' + lv.index], col = new Float32Array(om.length * 3);
      for (let i = 0; i < om.length; i++) col.set(rdbu(om[i] / 127), i * 3);
      g.setAttribute('color', new THREE.BufferAttribute(col, 3));
      g.setIndex(new THREE.BufferAttribute(vx['idx' + lv.index].slice(), 1));
      g.computeVertexNormals();
      const mesh = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.35, metalness: 0, transparent: true, opacity: 0.88, side: THREE.DoubleSide }));
      mesh.visible = false; mesh.renderOrder = 1;
      this.scene.add(mesh); this.vortex.push(mesh);
    }

    this.contourMats = [];
    const loader = new THREE.TextureLoader();
    const aniso = 8;
    for (const s of src.slices) {
      const o = { info: s, group: new THREE.Group(), tex: {}, mat: null, lines: {} };
      const [f0, f1] = s.extent_flow, [v0, v1] = s.extent_vert;
      const fa = AX[s.flow_axis], va = AX[s.vert_axis], na = AX[s.normal_axis];
      const P = (f_, v_) => { const p = [0, 0, 0]; p[fa] = f_; p[va] = v_; p[na] = 0; return p; };
      const g = new THREE.BufferGeometry();
      g.setAttribute('position', new THREE.BufferAttribute(new Float32Array([...P(f0, v1), ...P(f1, v1), ...P(f0, v0), ...P(f1, v0)]), 3));
      g.setAttribute('uv', new THREE.BufferAttribute(new Float32Array([0, 1, 1, 1, 0, 0, 1, 0]), 2));
      g.setIndex([0, 2, 1, 1, 2, 3]);
      for (const [k, url] of [['speed', s.speed_png], ['vort', s.vort_png]]) {
        const t = await loader.loadAsync(`${this.dir}/${url}`);
        t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = aniso; t.generateMipmaps = true;
        t.minFilter = THREE.LinearMipmapLinearFilter; o.tex[k] = t;
      }
      o.mat = new THREE.MeshBasicMaterial({ map: o.tex.speed, transparent: true, opacity: 0.85, side: THREE.DoubleSide, depthWrite: false, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1 });
      o.mesh = new THREE.Mesh(g, o.mat); o.mesh.renderOrder = 0;
      o.group.add(o.mesh);
      for (const k of ['speed', 'vort']) {
        const seg = sc[`${s.tag}_${k}_seg`], lvl = sc[`${s.tag}_${k}_lvl`];
        const n = lvl.length, pos = new Float32Array(n * 6), col = new Float32Array(n * 6);
        const levels = s.levels[k];
        for (let i = 0; i < n; i++) {
          pos.set(P(seg[i * 4], seg[i * 4 + 1]), i * 6); pos.set(P(seg[i * 4 + 2], seg[i * 4 + 3]), i * 6 + 3);
          const c = k === 'vort' ? (levels[lvl[i]] < 0 ? [0.15, 0.4, 0.85] : [0.8, 0.12, 0.12]) : [1, 1, 1];
          col.set(c, i * 6); col.set(c, i * 6 + 3);
        }
        const lg = new THREE.BufferGeometry();
        lg.setAttribute('position', new THREE.BufferAttribute(pos, 3));
        lg.setAttribute('color', new THREE.BufferAttribute(col, 3));
        const lm = new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, opacity: 0.8, depthWrite: false });
        lm.userData.k = k;
        this.contourMats.push(lm);
        const ls = new THREE.LineSegments(lg, lm);
        ls.renderOrder = 0.5; ls.visible = k === 'speed';
        o.lines[k] = ls; o.group.add(ls);
      }
      this.scene.add(o.group); this.slices.push(o);
    }
    if (!this.mean && m.frames) await this.loadFrames();
    else if (src.slices.length && src.slices.every((s) => s.field_size && sc[s.tag + '_s'])) {
      // one stored field per slice (the time mean, or a single snapshot): drawn like a one-frame series
      const A = {};
      for (const s of src.slices) { A['sol_' + s.tag] = sc[s.tag + '_sol']; A[`f0_${s.tag}_s`] = sc[s.tag + '_s']; A[`f0_${s.tag}_w`] = sc[s.tag + '_w']; }
      this.initFrames(A, { n: 1, t_star: this.mean ? src.t_star : [m.t_star], size: src.slices[0].field_size, vel_plane: null,
        vel_scale: m.speed_range[1], vort_scale: src.slices.map((s) => s.vort_range[1]) });
    }
    this.applyTheme();
  }

  // speed colours x c (streamlines and slices); 1 = the bundle's own |u|/U scale
  setColorScale(c) {
    if (Math.abs(c - this.cscale) < 1e-4) return;
    this.cscale = c; this.streams.material.uniforms.uScale.value = c; this.dirty = true;
  }

  // crossfade weight w in [0,1]: alpha' = 1 - (1 - alpha)^w, so two runs with weights w and 1 - w
  // together cover the same as one run at full weight (no dip in the middle of a blend)
  setFade(w, sop) {
    this.fade = w;
    const a = (base) => 1 - Math.pow(1 - Math.min(base, 0.995), Math.max(0, w));
    this.streams.material.uniforms.uOpacity.value = a(0.72);
    for (const m of this.vortex) m.material.opacity = a(0.88);
    for (const o of this.slices) o.mat.opacity = a(sop ?? 0.85);
    for (const lm of this.contourMats) lm.opacity = a(lm.userData.base ?? 0.75);
  }


  // ---- time series: per-frame slice fields, colours and contours computed here
  async loadFrames() {
    const m = this.m;
    this.initFrames(await loadArrays(this.dir, m.files.frames), m.frames);
  }

  initFrames(A, fr) {
    const W = fr.size[0], H = fr.size[1];
    this.fr = { A, n: fr.n, W, H, info: fr };
    this.dirty = true; this.curT = 0;
    this.lutS = new Uint8Array(256 * 3); this.lutW = new Uint8Array(255 * 3);
    for (let i = 0; i < 256; i++) this.lutS.set(turbo(i / 255).map((c) => Math.round(c * 255)), i * 3);
    for (let i = 0; i < 255; i++) this.lutW.set(rdbu((i - 127) / 127).map((c) => Math.round(c * 255)), i * 3);
    this.tmp = new Float32Array(W * H); this.tmp2 = new Float32Array(W * H);
    const MAXSEG = 60000;
    this.slices.forEach((o, si) => {
      const tag = o.info.tag;
      o.si = si; o.sol = A['sol_' + tag];
      o.solD = new Uint8Array(W * H);
      for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) {
        let hit = 0;
        for (let dj = -1; dj <= 1 && !hit; dj++) for (let di = -1; di <= 1; di++) {
          const jj = j + dj, ii = i + di;
          if (jj >= 0 && jj < H && ii >= 0 && ii < W && o.sol[jj * W + ii]) { hit = 1; break; }
        }
        o.solD[j * W + i] = hit;
      }
      o.fS = new Float32Array(W * H); o.fW = new Float32Array(W * H);
      o.rgba = new Uint8Array(W * H * 4);
      o.ftex = new THREE.DataTexture(o.rgba, W, H, THREE.RGBAFormat);
      o.ftex.magFilter = THREE.LinearFilter; o.ftex.minFilter = THREE.LinearFilter;
      o.ftex.colorSpace = THREE.SRGBColorSpace; o.ftex.needsUpdate = true;
      o.mat.map = o.ftex; o.mat.needsUpdate = true;
      o.hasVel = tag === fr.vel_plane;
      if (o.hasVel) { o.fU = new Float32Array(W * H); o.fV = new Float32Array(W * H); }
      for (const k of ['speed', 'vort']) {
        const lg = new THREE.BufferGeometry();
        lg.setAttribute('position', new THREE.BufferAttribute(new Float32Array(MAXSEG * 6), 3).setUsage(THREE.DynamicDrawUsage));
        lg.setAttribute('color', new THREE.BufferAttribute(new Float32Array(MAXSEG * 6), 3).setUsage(THREE.DynamicDrawUsage));
        lg.setDrawRange(0, 0);
        o.lines[k].geometry.dispose(); o.lines[k].geometry = lg; o.lines[k].frustumCulled = false;
      }
      if (o.hasVel) this.initParticles(o);
    });
  }

  initParticles(o) {
    const N = 1800, [f0, f1] = o.info.extent_flow, [v0, v1] = o.info.extent_vert;
    const p = { N, x: new Float32Array(N), y: new Float32Array(N), age: new Float32Array(N), life: new Float32Array(N) };
    for (let i = 0; i < N; i++) { p.x[i] = f0 + Math.random() * (f1 - f0); p.y[i] = v0 + Math.random() * (v1 - v0); p.age[i] = 0; p.life[i] = 2 + Math.random() * 5; }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(N * 3), 3).setUsage(THREE.DynamicDrawUsage));
    g.setAttribute('color', new THREE.BufferAttribute(new Float32Array(N * 3), 3).setUsage(THREE.DynamicDrawUsage));
    p.pts = new THREE.Points(g, new THREE.PointsMaterial({ size: 2.8 * env.DPR, sizeAttenuation: false, vertexColors: true, transparent: true, opacity: 0.95, depthWrite: false }));
    p.pts.frustumCulled = false; p.pts.renderOrder = 3; p.pts.visible = false;
    this.scene.add(p.pts);
    o.part = p;
  }

  stepParticles(dt, on) {
    for (const o of this.slices) {
      const p = o.part; if (!p) continue;
      p.pts.visible = on && o.group.visible;
      if (!p.pts.visible) continue;
      const fr = this.fr, W = fr.W, H = fr.H, vs = fr.info.vel_scale / 127;
      const [f0, f1] = o.info.extent_flow, [v0, v1] = o.info.extent_vert;
      const df = (f1 - f0) / W, dv = (v1 - v0) / H;
      const fa = AX[o.info.flow_axis], va = AX[o.info.vert_axis];
      const pos = p.pts.geometry.attributes.position.array, col = p.pts.geometry.attributes.color.array;
      const bil = (arr, gx, gy) => {
        gx = Math.min(W - 1.001, Math.max(0, gx)); gy = Math.min(H - 1.001, Math.max(0, gy));
        const i = gx | 0, j = gy | 0, fx = gx - i, fy = gy - j, k = j * W + i;
        return (arr[k] * (1 - fx) + arr[k + 1] * fx) * (1 - fy) + (arr[k + W] * (1 - fx) + arr[k + W + 1] * fx) * fy;
      };
      for (let n = 0; n < p.N; n++) {
        const gx = (p.x[n] - f0) / df - 0.5, gy = (p.y[n] - v0) / dv - 0.5;
        let respawn = p.age[n] > p.life[n] || gx < 0 || gx > W - 1 || gy < 0 || gy > H - 1;
        let u = 0, v = 0;
        if (!respawn) {
          if (o.sol[Math.round(gy) * W + Math.round(gx)]) respawn = true;
          else { u = bil(o.fU, gx, gy) * vs; v = bil(o.fV, gx, gy) * vs; }
        }
        if (respawn) {
          p.x[n] = f0 + Math.random() * 0.12; p.y[n] = v0 + Math.random() * (v1 - v0); p.age[n] = 0; p.life[n] = 3 + Math.random() * 5;
          u = 1; v = 0;
        } else { p.x[n] += u * 0.55 * dt; p.y[n] += v * 0.55 * dt; p.age[n] += dt; }
        const q = [0, 0, 0]; q[fa] = p.x[n]; q[va] = p.y[n];
        pos[n * 3] = q[0]; pos[n * 3 + 1] = q[1]; pos[n * 3 + 2] = q[2];
        const sp = Math.min(1, Math.hypot(u, v) / (fr.info.vel_scale * 0.9));
        const c = turbo(0.12 + 0.8 * sp);
        col[n * 3] = c[0]; col[n * 3 + 1] = c[1]; col[n * 3 + 2] = c[2];
      }
      p.pts.geometry.attributes.position.needsUpdate = true; p.pts.geometry.attributes.color.needsUpdate = true;
    }
  }

  blur(src, passes) {
    const { W, H } = this.fr;
    let a = src;
    for (let p = 0; p < passes; p++) {
      const b = a === this.tmp ? this.tmp2 : this.tmp;
      for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) {
        let s = 0, c = 0;
        for (let dj = -1; dj <= 1; dj++) {
          const jj = j + dj; if (jj < 0 || jj >= H) continue;
          for (let di = -1; di <= 1; di++) { const ii = i + di; if (ii < 0 || ii >= W) continue; s += a[jj * W + ii]; c++; }
        }
        b[j * W + i] = s / c;
      }
      a = b;
    }
    return a;
  }

  contours(o, field, F) {
    const { W, H } = this.fr, g = o.lines[field].geometry;
    const pos = g.attributes.position.array, col = g.attributes.color.array;
    const info = o.info, fa = AX[info.flow_axis], va = AX[info.vert_axis];
    const [f0, f1] = info.extent_flow, [v0, v1] = info.extent_vert;
    const df = (f1 - f0) / W, dv = (v1 - v0) / H;
    const scale = field === 'speed' ? 255 / this.fr.info.vel_scale : 127 / this.fr.info.vort_scale[o.si];
    const max = pos.length / 6;
    let n = 0;
    const TAB = [[], [3, 0], [0, 1], [3, 1], [1, 2], [3, 0, 1, 2], [0, 2], [3, 2], [2, 3], [0, 2], [0, 1, 2, 3], [1, 2], [1, 3], [0, 1], [3, 0], []];
    for (const level of info.levels[field]) {
      if (field === 'vort' && Math.abs(level) < 1e-9) continue;
      const L = level * scale;
      const rgb = field === 'vort' ? (level < 0 ? [0.15, 0.4, 0.85] : [0.8, 0.12, 0.12]) : [1, 1, 1];
      for (let j = 0; j < H - 1; j++) for (let i = 0; i < W - 1; i++) {
        const k = j * W + i;
        if (o.solD[k] || o.solD[k + 1] || o.solD[k + W] || o.solD[k + W + 1]) continue;
        const a = F[k], b = F[k + 1], c = F[k + W + 1], d = F[k + W];
        const idx = (a > L ? 1 : 0) | (b > L ? 2 : 0) | (c > L ? 4 : 0) | (d > L ? 8 : 0);
        const segs = TAB[idx];
        for (let s = 0; s < segs.length; s += 2) {
          if (n >= max) break;
          for (let e = 0; e < 2; e++) {
            let x, y;
            switch (segs[s + e]) {
              case 0: x = i + (L - a) / (b - a); y = j; break;
              case 1: x = i + 1; y = j + (L - b) / (c - b); break;
              case 2: x = i + (L - d) / (c - d); y = j + 1; break;
              default: x = i; y = j + (L - a) / (d - a);
            }
            const q = [0, 0, 0]; q[fa] = f0 + (x + 0.5) * df; q[va] = v0 + (y + 0.5) * dv;
            const o6 = n * 6 + e * 3;
            pos[o6] = q[0]; pos[o6 + 1] = q[1]; pos[o6 + 2] = q[2];
            col[o6] = rgb[0]; col[o6 + 1] = rgb[1]; col[o6 + 2] = rgb[2];
          }
          n++;
        }
      }
    }
    g.setDrawRange(0, n * 2);
    g.attributes.position.needsUpdate = true; g.attributes.color.needsUpdate = true;
  }

  setTime(t, s) {
    const fr = this.fr; if (!fr) return;
    const n = fr.n, a = Math.min(n - 1, Math.max(0, Math.floor(t))), b = Math.min(n - 1, a + 1), f = Math.min(1, Math.max(0, t - a));
    this.curT = t; this.dirty = false;
    const { W, H, A } = fr, N = W * H;
    this.slices.forEach((o, i) => {
      if (!s.planes[i]) return;
      const tag = o.info.tag, key = (sfx) => [A[`f${a}_${tag}_${sfx}`], A[`f${b}_${tag}_${sfx}`]];
      const vort = s.field === 'vort';
      const [xa, xb] = key(vort ? 'w' : 's');
      const F = vort ? o.fW : o.fS;
      for (let k = 0; k < N; k++) F[k] = xa[k] + (xb[k] - xa[k]) * f;
      const lut = vort ? this.lutW : this.lutS, lo = vort ? -127 : 0, hi = vort ? 127 : 255, off = vort ? 127 : 0;
      const cs = vort ? 1 : this.cscale;
      for (let k = 0; k < N; k++) {
        const ix = Math.round(Math.min(hi, Math.max(lo, F[k] * cs))) + off;
        o.rgba[k * 4] = lut[ix * 3]; o.rgba[k * 4 + 1] = lut[ix * 3 + 1]; o.rgba[k * 4 + 2] = lut[ix * 3 + 2];
        o.rgba[k * 4 + 3] = o.sol[k] ? 0 : 255;
      }
      o.ftex.needsUpdate = true;
      if (o.hasVel) {
        const [ua, ub] = key('u'), [va, vb] = key('v');
        for (let k = 0; k < N; k++) { o.fU[k] = ua[k] + (ub[k] - ua[k]) * f; o.fV[k] = va[k] + (vb[k] - va[k]) * f; }
      }
      if (s.cont) this.contours(o, s.field, this.blur(F, vort ? 2 : 1));
    });
  }

  applyTheme() {
    const dark = cssVar('--contour').startsWith('#f');
    for (const lm of this.contourMats) {
      if (lm.userData.k === 'speed') lm.color.set(dark ? 0xffffff : 0x10151f);
      lm.userData.base = dark ? 0.75 : 0.7;
      lm.opacity = lm.userData.base;
    }
  }

  dispose() {
    this.scene.traverse((o) => {
      o.geometry?.dispose();
      const ms = Array.isArray(o.material) ? o.material : o.material ? [o.material] : [];
      for (const m of ms) { m.map?.dispose(); m.dispose(); }
    });
    for (const o of this.slices) for (const t of Object.values(o.tex)) t.dispose();
    this.scene.clear();
  }

  update(camera) { this.key.position.copy(camera.position).sub(env.target()).normalize().add(new THREE.Vector3(0.3, 0.6, 0)).normalize(); }

  caption() {
    const m = this.m, g = m.grid;
    const parts = [];
    if (m.Re != null) parts.push('Re ' + Number(m.Re).toPrecision(3));
    if (m.S != null) parts.push('S ' + m.S);
    if (this.mean) parts.push(`time mean of ${m.mean.n_avg} frames`);
    else if (m.t_star != null && !m.frames) parts.push('t* ' + m.t_star);
    const saved = Math.round(1 / g.dx_D);
    parts.push(`grid ${g.nx}x${g.ny}x${g.nz}, ` + (g.D_cells && g.D_cells !== saved ? `solver ${g.D_cells} cells/D, saved ${saved} cells/D` : `${saved} cells/D`));
    if (m.orientation) parts.push(`hole orientation ${m.orientation} ASSUMED`);
    return `<b>${esc(m.label)}</b>${esc(parts.join(' | '))}<br><span class="${m.synthetic ? 'syn' : 'pred'}">${esc(m.status)}</span>`;
  }
}
export const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
