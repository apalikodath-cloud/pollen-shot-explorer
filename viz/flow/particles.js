// GPU flow effects for a RunView whose bundle has a 3D velocity volume (manifest.vol, see make_vol.py):
//  - tracer particles advected through the CFD velocity on the GPU (RK2, two frames blended in time),
//    seeded upstream, all around the ball surface and in the wake, drawn as fading comet trails;
//  - a ray-marched vortex volume (signed sqrt of the Q-criterion, red / blue by the streamwise turning sense);
//  - lift pairs: timelines (a vertical rake of tracers released together upstream) with one tracer above and one
//    below the ball linked, and the time difference when they pass 1 D behind the ball.
// Everything here is drawn from CFD output: PREDICTED, not measured. Tracers are massless (they follow the air).
import * as THREE from 'three';
import { TURBO_GLSL } from './flowview.js';

const HASH = `float hash(vec2 p){ vec3 p3 = fract(vec3(p.xyx)*0.1031); p3 += dot(p3, p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }`;
const PREC = `precision highp float; precision highp sampler3D; precision highp sampler2DArray;`;
const K = 40;   // history depth (trail samples)

export function fxSupported(renderer) {
  return renderer.capabilities.isWebGL2 && renderer.extensions.has('EXT_color_buffer_float');
}

async function loadVgz(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url}: ${r.status}`);
  const ds = r.body.pipeThrough(new DecompressionStream('gzip'));
  return new Int8Array(await new Response(ds).arrayBuffer());
}

function volTex(arr, size) {
  const t = new THREE.Data3DTexture(arr, size[0], size[1], size[2]);
  t.format = THREE.RGBAFormat; t.type = THREE.ByteType; t.internalFormat = 'RGBA8_SNORM';
  t.minFilter = t.magFilter = THREE.LinearFilter;
  t.wrapS = t.wrapT = t.wrapR = THREE.ClampToEdgeWrapping;
  t.unpackAlignment = 1; t.needsUpdate = true;
  return t;
}

// screen-space fat segments (timelines, pair links); capacity fixed, filled each frame
class FatSegs {
  constructor(cap, width) {
    const g = new THREE.InstancedBufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array([0, -1, 0, 0, 1, 0, 1, -1, 0, 1, 1, 0]), 3));
    g.setIndex([0, 2, 1, 1, 2, 3]);
    this.a = new Float32Array(cap * 3); this.b = new Float32Array(cap * 3); this.ca = new Float32Array(cap * 4); this.cb = new Float32Array(cap * 4);
    for (const [n, arr, k] of [['iA', this.a, 3], ['iB', this.b, 3], ['iCA', this.ca, 4], ['iCB', this.cb, 4]]) {
      g.setAttribute(n, new THREE.InstancedBufferAttribute(arr, k).setUsage(THREE.DynamicDrawUsage));
    }
    g.instanceCount = 0;
    this.cap = cap; this.n = 0;
    this.mat = new THREE.ShaderMaterial({
      transparent: true, depthWrite: false,
      uniforms: { uRes: { value: new THREE.Vector2(1, 1) }, uWidth: { value: width } },
      vertexShader: `
        attribute vec3 iA; attribute vec3 iB; attribute vec4 iCA; attribute vec4 iCB;
        uniform vec2 uRes; uniform float uWidth; varying vec4 vC; varying float vS;
        void main(){
          vec4 ca = projectionMatrix*modelViewMatrix*vec4(iA,1.), cb = projectionMatrix*modelViewMatrix*vec4(iB,1.);
          if (ca.w <= 0.001 || cb.w <= 0.001) { gl_Position = vec4(2.,2.,2.,1.); return; }
          vec2 d = (cb.xy/cb.w - ca.xy/ca.w)*uRes; float L = length(d); d = L > 1e-6 ? d/L : vec2(1.,0.);
          vec4 c = mix(ca, cb, position.x);
          c.xy += vec2(-d.y, d.x) * position.y * (uWidth/uRes) * c.w;
          gl_Position = c; vC = mix(iCA, iCB, position.x); vS = position.y;
        }`,
      fragmentShader: `varying vec4 vC; varying float vS;
        void main(){ gl_FragColor = vec4(vC.rgb, vC.a*(1.-smoothstep(0.5,1.,abs(vS)))); }`,
    });
    this.mesh = new THREE.Mesh(g, this.mat); this.mesh.frustumCulled = false;
    this.g = g;
  }
  begin() { this.n = 0; }
  push(p, q, c0, c1) {
    if (this.n >= this.cap) return;
    const i = this.n++;
    this.a.set(p, i * 3); this.b.set(q, i * 3); this.ca.set(c0, i * 4); this.cb.set(c1 || c0, i * 4);
  }
  end() {
    this.g.instanceCount = this.n;
    for (const n of ['iA', 'iB', 'iCA', 'iCB']) this.g.attributes[n].needsUpdate = true;
  }
}

// round dots with per-dot colour and size (pixels)
class Dots {
  constructor(cap) {
    const g = new THREE.BufferGeometry();
    this.p = new Float32Array(cap * 3); this.c = new Float32Array(cap * 4); this.s = new Float32Array(cap);
    g.setAttribute('position', new THREE.BufferAttribute(this.p, 3).setUsage(THREE.DynamicDrawUsage));
    g.setAttribute('col', new THREE.BufferAttribute(this.c, 4).setUsage(THREE.DynamicDrawUsage));
    g.setAttribute('sz', new THREE.BufferAttribute(this.s, 1).setUsage(THREE.DynamicDrawUsage));
    g.setDrawRange(0, 0);
    this.mat = new THREE.ShaderMaterial({
      transparent: true, depthWrite: false, uniforms: { uDpr: { value: 1 } },
      vertexShader: `attribute vec4 col; attribute float sz; uniform float uDpr; varying vec4 vC;
        void main(){ gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); gl_PointSize = sz*uDpr; vC = col; }`,
      fragmentShader: `varying vec4 vC;
        void main(){ vec2 q = gl_PointCoord*2.-1.; float r = dot(q,q); if (r > 1.) discard;
          float ring = smoothstep(0.55, 0.75, r); gl_FragColor = vec4(mix(vC.rgb, vec3(1.), 0.35*(1.-ring)) * (1.-0.45*ring), vC.a*(1.-smoothstep(0.85,1.,r))); }`,
    });
    this.pts = new THREE.Points(g, this.mat); this.pts.frustumCulled = false;
    this.g = g; this.cap = cap; this.n = 0;
  }
  begin() { this.n = 0; }
  push(p, c, s) { if (this.n >= this.cap) return; const i = this.n++; this.p.set(p, i * 3); this.c.set(c, i * 4); this.s[i] = s; }
  end() { this.g.setDrawRange(0, this.n); for (const n of ['position', 'col', 'sz']) this.g.attributes[n].needsUpdate = true; }
}

const TOP = [1.0, 0.55, 0.22], BOT = [0.25, 0.65, 1.0];

export class FlowFX {
  // view: a loaded RunView whose manifest has .vol; quality: particle texture side (64, 128 or 256)
  constructor(renderer, view, quality = 128) {
    this.r = renderer; this.v = view; this.m = view.m; this.vi = view.m.vol;
    this.W = quality; this.N = quality * quality;
    this.frames = []; this.cpu = []; this.mean = null; this.meanCpu = null;
    this.head = 0; this.seed = 0; this.inited = false; this.clock = 0; this.dark = true;
    this.lines = []; this.nextRelease = 0; this.pairs = []; this.dead = false;
    const vi = this.vi, sz = vi.size;
    this.org = new THREE.Vector3(...vi.origin).subScalar(0.5 * vi.dx);
    this.span = new THREE.Vector3(sz[0] * vi.dx, sz[1] * vi.dx, sz[2] * vi.dx);
    this.lo = new THREE.Vector3(...this.m.bounds.lo); this.hi = new THREE.Vector3(...this.m.bounds.hi);
    this.group = new THREE.Group();
    view.scene.add(this.group);
    this.buildSim(); this.buildTrails(); this.buildVolume();
    this.tl = new FatSegs(4000, 3.2); this.tl.mesh.renderOrder = 7;
    this.dots = new Dots(600); this.dots.pts.renderOrder = 8;
    this.group.add(this.tl.mesh, this.dots.pts);
  }

  // mean: load only the time-mean volume (falls back to frame 0); otherwise frame 0 first, the rest in the background
  async load(mean) {
    const vi = this.vi, dir = this.v.dir;
    this.useMean = !!(mean && vi.mean);
    if (this.useMean) {
      const cpu = await loadVgz(`${dir}/${vi.mean}`);
      if (this.dead) return;
      this.meanCpu = cpu;
      this.mean = volTex(cpu, vi.size);
    } else {
      await this.loadFrame(0);
      (async () => { for (let i = 1; i < vi.frames.length && !this.dead; i++) await this.loadFrame(i).catch(() => {}); })();
    }
  }
  async loadFrame(i) {
    const a = await loadVgz(`${this.v.dir}/${this.vi.frames[i]}`);
    if (this.dead) return;
    this.cpu[i] = a; this.frames[i] = volTex(a, this.vi.size);
  }
  get nLoaded() { return this.useMean ? 1 : this.frames.filter(Boolean).length; }

  // the two loaded volumes around fractional frame t and the blend weight
  pick(t) {
    if (this.useMean || !this.frames.length) return [this.mean || this.frames[0], this.mean || this.frames[0], 0, this.meanCpu || this.cpu[0], this.meanCpu || this.cpu[0]];
    const n = this.vi.frames.length, a = Math.min(n - 1, Math.max(0, Math.floor(t))), b = Math.min(n - 1, a + 1);
    let ia = a; while (ia > 0 && !this.frames[ia]) ia--;
    let ib = b; while (ib < n - 1 && !this.frames[ib]) ib++;
    if (!this.frames[ib]) ib = ia;
    const f = ia === ib ? 0 : Math.min(1, Math.max(0, (t - ia) / (ib - ia)));
    return [this.frames[ia], this.frames[ib], f, this.cpu[ia], this.cpu[ib]];
  }

  // ---------------------------------------------------------------- GPU particles
  buildSim() {
    const W = this.W, opt = { type: THREE.FloatType, format: THREE.RGBAFormat, minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter, depthBuffer: false, stencilBuffer: false };
    this.pos = [new THREE.WebGLRenderTarget(W, W, opt), new THREE.WebGLRenderTarget(W, W, opt)];
    this.hist = new THREE.WebGLArrayRenderTarget(W, W, K, opt);
    Object.assign(this.hist.texture, { type: THREE.FloatType, minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter });
    this.cur = 0;
    this.quadCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    this.quadScene = new THREE.Scene();
    const vs = `varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }`;
    this.simMat = new THREE.ShaderMaterial({
      uniforms: {
        uPos: { value: null }, uA: { value: null }, uB: { value: null }, uMix: { value: 0 }, uDt: { value: 0 }, uSeed: { value: 0 }, uInit: { value: 1 },
        uVs: { value: this.vi.vel_scale }, uOrg: { value: this.org }, uSpan: { value: this.span }, uLo: { value: this.lo }, uHi: { value: this.hi },
        uSpawn: { value: new THREE.Vector2(0.42, 0.85) },
      },
      vertexShader: vs,
      fragmentShader: `${PREC}
        uniform sampler2D uPos; uniform sampler3D uA; uniform sampler3D uB;
        uniform float uMix, uDt, uSeed, uInit, uVs; uniform vec3 uOrg, uSpan, uLo, uHi; uniform vec2 uSpawn;
        varying vec2 vUv;
        ${HASH}
        vec3 vel(vec3 p){ vec3 t = (p-uOrg)/uSpan; return mix(texture(uA,t).xyz, texture(uB,t).xyz, uMix)*uVs; }
        void main(){
          vec4 P = texture2D(uPos, vUv);
          float life = 2.2 + 4.5*hash(vUv*913.7);
          float age = mod(P.w, 100.), tag = floor(P.w/100.);
          vec3 p = P.xyz;
          bool re = uInit > .5 || age > life || any(lessThan(p, uLo+0.015)) || any(greaterThan(p, uHi-0.015));
          if (!re) {
            vec3 k1 = vel(p);
            if (dot(k1,k1) < 0.0009 && dot(p,p) < 0.42) re = true;   // stuck on or inside the ball
            else { vec3 k2 = vel(p + 0.5*uDt*k1); p += uDt*k2; age += uDt; }
          }
          if (re) {
            float r0 = hash(vUv*517.3 + uSeed), r1 = hash(vUv*231.9 + uSeed*1.37), r2 = hash(vUv*77.1 + uSeed*2.11), r3 = hash(vUv*391.3 + uSeed*0.73);
            if (r0 < uSpawn.x) p = vec3(uLo.x + 0.02 + 0.12*r3, mix(-0.74, 0.74, r1), mix(-0.74, 0.74, r2));        // upstream
            else if (r0 < uSpawn.y) {                                                                            // all over the ball
              float z = 2.*r1-1., ph = 6.2831853*r2, s = sqrt(1.-z*z);
              p = vec3(s*cos(ph), s*sin(ph), z) * (0.515 + 0.07*r3);
            } else p = vec3(mix(0.25, 1.7, r1), mix(-0.55, 0.55, r2), mix(-0.55, 0.55, r3));                     // wake
            age = uInit > .5 ? life*hash(vUv*45.3) : 0.;
            tag = p.z > 0. ? 1. : 0.;
          }
          gl_FragColor = vec4(p, tag*100. + age);
        }`,
    });
    this.copyMat = new THREE.ShaderMaterial({ uniforms: { uPos: { value: null } }, vertexShader: vs,
      fragmentShader: `uniform sampler2D uPos; varying vec2 vUv; void main(){ gl_FragColor = texture2D(uPos, vUv); }` });
    this.quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), this.simMat);
    this.quadScene.add(this.quad);
  }

  pass(mat, target, layer = 0) {
    this.quad.material = mat;
    this.r.setRenderTarget(target, layer);
    this.r.render(this.quadScene, this.quadCam);
  }

  record() {
    this.head = (this.head + 1) % K;
    this.copyMat.uniforms.uPos.value = this.pos[this.cur].texture;
    this.pass(this.copyMat, this.hist, this.head);
  }

  // advance dt (t* units) through the field at fractional frame t; s: viewer state (tracers on/off, trail length ...)
  step(dt, t, s) {
    const [A, B, f, ca, cb] = this.pick(t);
    if (!A) return;
    const r = this.r, prevT = r.getRenderTarget(), sc = r.getScissorTest();
    r.setScissorTest(false);
    const u = this.simMat.uniforms;
    u.uA.value = A; u.uB.value = B; u.uMix.value = f;
    this.vol.material.uniforms.uA.value = A; this.vol.material.uniforms.uB.value = B; this.vol.material.uniforms.uMix.value = f;
    for (const m of [this.trail.material, this.heads.material]) { m.uniforms.uA.value = A; m.uniforms.uB.value = B; m.uniforms.uMix.value = f; }
    if (s.tracers) {
      if (!this.inited) {
        u.uInit.value = 1; u.uDt.value = 0; u.uPos.value = this.pos[this.cur].texture;
        this.pass(this.simMat, this.pos[1 - this.cur]); this.cur = 1 - this.cur;
        u.uInit.value = 0;
        for (let k = 0; k < K; k++) this.record();
        this.inited = true;
      }
      const nsub = Math.min(6, Math.max(1, Math.ceil(dt / 0.02)));
      for (let i = 0; i < nsub; i++) {
        u.uDt.value = dt / nsub; u.uSeed.value = (this.seed = (this.seed + 0.6180339) % 97);
        u.uPos.value = this.pos[this.cur].texture;
        this.pass(this.simMat, this.pos[1 - this.cur]); this.cur = 1 - this.cur;
      }
      if (dt > 0) this.record();
      const tu = this.trail.material.uniforms;
      tu.uPos.value = this.pos[this.cur].texture; tu.uHead.value = this.head; tu.uLen.value = Math.max(2, Math.min(K, s.trail));
      this.heads.material.uniforms.uPos.value = this.pos[this.cur].texture;
    }
    r.setRenderTarget(prevT); r.setScissorTest(sc);
    this.trail.visible = this.heads.visible = !!s.tracers;
    this.vol.visible = !!s.vvol;
    this.vol.material.uniforms.uTh.value = s.vth;
    for (const m of [this.trail.material, this.heads.material]) m.uniforms.uMode.value = s.pcol;
    this.stepLines(dt, ca, cb, f, !!s.pairs);
  }

  buildTrails() {
    const W = this.W, N = this.N;
    const g = new THREE.InstancedBufferGeometry();
    const aK = new Float32Array(K * 2), aSide = new Float32Array(K * 2), idx = [];
    for (let k = 0; k < K; k++) { aK[2 * k] = aK[2 * k + 1] = k; aSide[2 * k] = -1; aSide[2 * k + 1] = 1; }
    for (let k = 0; k < K - 1; k++) { const a = 2 * k; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); }
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(K * 2 * 3), 3));
    g.setAttribute('aK', new THREE.BufferAttribute(aK, 1));
    g.setAttribute('aSide', new THREE.BufferAttribute(aSide, 1));
    g.setIndex(idx);
    const uv = new Float32Array(N * 2);
    for (let j = 0; j < W; j++) for (let i = 0; i < W; i++) { uv[(j * W + i) * 2] = (i + 0.5) / W; uv[(j * W + i) * 2 + 1] = (j + 0.5) / W; }
    g.setAttribute('aUv', new THREE.InstancedBufferAttribute(uv, 2));
    g.instanceCount = N;
    const common = {
      uA: { value: null }, uB: { value: null }, uMix: { value: 0 }, uVs: { value: this.vi.vel_scale }, uOrg: { value: this.org }, uSpan: { value: this.span },
      uMode: { value: 0 }, uDark: { value: 1 }, uSmax: { value: 1.6 },
    };
    // colour of a tracer at p: 0 speed (turbo), 1 where it started (above / below the ball centre), 2 vortex turning sense
    const COLOR = `${TURBO_GLSL}
      vec3 tracerColor(vec3 p, float tag){
        vec3 t = (p-uOrg)/uSpan;
        vec4 a = mix(texture(uA,t), texture(uB,t), uMix);
        if (uMode < 0.5) return turbo(0.08 + 0.9*length(a.xyz)*uVs/uSmax);
        if (uMode < 1.5) return tag > 0.5 ? vec3(${TOP.join(',')}) : vec3(${BOT.join(',')});
        float q = a.w*1.8; vec3 grey = uDark > .5 ? vec3(.62,.64,.68) : vec3(.42,.44,.48);
        return q > 0. ? mix(grey, vec3(1.,.28,.22), clamp(q,0.,1.)) : mix(grey, vec3(.25,.55,1.), clamp(-q,0.,1.));
      }`;
    this.trail = new THREE.Mesh(g, new THREE.ShaderMaterial({
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
      uniforms: Object.assign({ uHist: { value: this.hist.texture }, uPos: { value: null }, uHead: { value: 0 }, uLen: { value: 24 },
        uRes: { value: new THREE.Vector2(1, 1) }, uWidth: { value: 1.6 }, uAlpha: { value: 0.75 } }, common),
      vertexShader: `${PREC}
        uniform sampler2DArray uHist; uniform sampler3D uA; uniform sampler3D uB;
        uniform float uMix, uVs, uMode, uDark, uSmax, uHead, uLen, uWidth, uAlpha; uniform vec3 uOrg, uSpan; uniform vec2 uRes;
        attribute float aK; attribute float aSide; attribute vec2 aUv;
        varying vec4 vC; varying float vV; varying float vS;
        ${COLOR}
        vec4 hist(float k){ return texture(uHist, vec3(aUv, mod(uHead - k + ${K}., ${K}.))); }
        bool ok(vec4 h, float cur, float tag){ return mod(h.w,100.) <= cur + 1e-4 && abs(floor(h.w/100.) - tag) < .5; }
        void main(){
          vV = 0.; vS = aSide; vC = vec4(0.);
          if (aK > uLen - 1.) { gl_Position = vec4(2.,2.,2.,1.); return; }
          vec4 h0 = hist(0.); float cur = mod(h0.w,100.), tag = floor(h0.w/100.);
          vec4 hk = hist(aK);
          float kn = aK < uLen - 1.5 ? aK + 1. : aK - 1.;
          vec4 hn = hist(kn);
          if (!ok(hn, cur, tag) && aK > 0.5) hn = hist(aK - 1.);
          vec4 ca = projectionMatrix*modelViewMatrix*vec4(hk.xyz,1.), cb = projectionMatrix*modelViewMatrix*vec4(hn.xyz,1.);
          if (ca.w <= 0.001) { gl_Position = vec4(2.,2.,2.,1.); return; }
          vec2 d = (cb.xy/max(cb.w,1e-3) - ca.xy/ca.w)*uRes; float L = length(d); d = L > 1e-6 ? d/L : vec2(1.,0.);
          float tt = aK/(uLen-1.);
          float w = uWidth*(1. - 0.8*tt);
          ca.xy += vec2(-d.y, d.x) * aSide * (w/uRes) * ca.w;
          gl_Position = ca;
          vV = ok(hk, cur, tag) ? 1. : 0.;
          vec3 col = tracerColor(hk.xyz, tag);
          float a = uAlpha * pow(1. - tt, 1.4) * smoothstep(0., 0.45, cur);
          vC = vec4(col, a);
        }`,
      fragmentShader: `varying vec4 vC; varying float vV; varying float vS;
        void main(){ if (vV < 0.999) discard; gl_FragColor = vec4(vC.rgb, vC.a*(1.-smoothstep(0.4,1.,abs(vS)))); }`,
    }));
    this.trail.frustumCulled = false; this.trail.renderOrder = 5;
    // bright heads
    const hg = new THREE.BufferGeometry();
    hg.setAttribute('position', new THREE.BufferAttribute(new Float32Array(N * 3), 3));
    hg.setAttribute('aUv', new THREE.BufferAttribute(uv, 2));
    this.heads = new THREE.Points(hg, new THREE.ShaderMaterial({
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
      uniforms: Object.assign({ uPos: { value: null }, uSize: { value: 2.6 } }, common),
      vertexShader: `${PREC}
        uniform sampler2D uPos; uniform sampler3D uA; uniform sampler3D uB;
        uniform float uMix, uVs, uMode, uDark, uSmax, uSize; uniform vec3 uOrg, uSpan;
        attribute vec2 aUv; varying vec4 vC;
        ${COLOR}
        void main(){
          vec4 P = texture2D(uPos, aUv); float age = mod(P.w,100.), tag = floor(P.w/100.);
          vec4 mv = modelViewMatrix*vec4(P.xyz,1.);
          gl_Position = projectionMatrix*mv;
          gl_PointSize = clamp(uSize*3./max(-mv.z,0.05), 1.2, uSize*1.5);
          vC = vec4(mix(tracerColor(P.xyz, tag), vec3(1.), uDark*0.15), 0.8*smoothstep(0., 0.45, age));
        }`,
      fragmentShader: `varying vec4 vC;
        void main(){ vec2 q = gl_PointCoord*2.-1.; float r = dot(q,q); if (r > 1.) discard; gl_FragColor = vec4(vC.rgb, vC.a*(1.-r)*(1.-r)); }`,
    }));
    this.heads.frustumCulled = false; this.heads.renderOrder = 6;
    this.group.add(this.trail, this.heads);
  }

  // ---------------------------------------------------------------- vortex volume (ray marched)
  buildVolume() {
    const lo = this.lo, hi = this.hi;
    const g = new THREE.BoxGeometry(hi.x - lo.x, hi.y - lo.y, hi.z - lo.z);
    g.translate((hi.x + lo.x) / 2, (hi.y + lo.y) / 2, (hi.z + lo.z) / 2);
    this.vol = new THREE.Mesh(g, new THREE.ShaderMaterial({
      transparent: true, depthWrite: false, depthTest: false, side: THREE.BackSide, premultipliedAlpha: true,
      uniforms: { uA: { value: null }, uB: { value: null }, uMix: { value: 0 }, uOrg: { value: this.org }, uSpan: { value: this.span },
        uLo: { value: lo }, uHi: { value: hi }, uTh: { value: 0.22 }, uDens: { value: 0.45 }, uDark: { value: 1 }, uTime: { value: 0 } },
      vertexShader: `varying vec3 vW; void main(){ vW = (modelMatrix*vec4(position,1.)).xyz; gl_Position = projectionMatrix*viewMatrix*vec4(vW,1.); }`,
      fragmentShader: `${PREC}
        uniform sampler3D uA; uniform sampler3D uB; uniform float uMix, uTh, uDens, uDark, uTime; uniform vec3 uOrg, uSpan, uLo, uHi;
        varying vec3 vW;
        ${HASH}
        void main(){
          vec3 ro = cameraPosition, rd = normalize(vW - ro);
          vec3 inv = 1./rd, t0 = (uLo-ro)*inv, t1 = (uHi-ro)*inv;
          vec3 tn = min(t0,t1), tf = max(t0,t1);
          float a = max(max(max(tn.x,tn.y),tn.z), 0.), b = min(min(tf.x,tf.y),tf.z);
          float bb = dot(ro,rd), cc = dot(ro,ro) - 0.25, disc = bb*bb - cc;           // the ball (r = 0.5 D) hides what is behind it
          if (disc > 0.) { float ts = -bb - sqrt(disc); if (ts > 0.) b = min(b, ts); }
          if (b <= a) discard;
          float ds = 0.017; float t = a + ds*hash(gl_FragCoord.xy + uTime);
          vec3 C = vec3(0.); float A = 0.;
          vec3 red = uDark > .5 ? vec3(1.,.32,.22) : vec3(.78,.1,.08), blue = uDark > .5 ? vec3(.28,.6,1.) : vec3(.08,.3,.78);
          for (int i = 0; i < 400; i++) {
            if (t > b || A > 0.97) break;
            vec3 p = ro + rd*t, tc = (p-uOrg)/uSpan;
            float q = mix(texture(uA,tc).w, texture(uB,tc).w, uMix);
            // near the wall the Q estimate is spoiled by the zero velocity set inside the solid: fade it out
            float d = smoothstep(uTh, uTh*2.2, abs(q)) * smoothstep(0.54, 0.6, length(p));
            if (d > 0.002) {
              vec3 col = (q > 0. ? red : blue) * (0.75 + 0.6*d);
              float al = 1. - exp(-d*uDens*ds*38.);
              C += (1.-A)*al*col; A += (1.-A)*al;
            }
            t += ds;
          }
          if (A < 0.004) discard;
          gl_FragColor = vec4(C, A);
        }`,
    }));
    this.vol.frustumCulled = false; this.vol.renderOrder = 4;
    this.group.add(this.vol);
  }

  // ---------------------------------------------------------------- lift pairs / timelines (CPU, same field)
  sampleCPU(a, b, f, x, y, z, out) {
    const vi = this.vi, [nx, ny, nz] = vi.size, o = vi.origin, dx = vi.dx, vs = vi.vel_scale / 127;
    let gx = (x - o[0]) / dx, gy = (y - o[1]) / dx, gz = (z - o[2]) / dx;
    gx = Math.min(nx - 1.001, Math.max(0, gx)); gy = Math.min(ny - 1.001, Math.max(0, gy)); gz = Math.min(nz - 1.001, Math.max(0, gz));
    const i = gx | 0, j = gy | 0, k = gz | 0, fx = gx - i, fy = gy - j, fz = gz - k;
    for (let c = 0; c < 3; c++) {
      let s = 0;
      for (let dz = 0; dz < 2; dz++) for (let dy = 0; dy < 2; dy++) for (let dxx = 0; dxx < 2; dxx++) {
        const w = (dxx ? fx : 1 - fx) * (dy ? fy : 1 - fy) * (dz ? fz : 1 - fz);
        const n = (((k + dz) * ny + (j + dy)) * nx + (i + dxx)) * 4 + c;
        s += w * (a[n] + (b[n] - a[n]) * f);
      }
      out[c] = s * vs;
    }
    return out;
  }

  // drop the timelines in flight (the frame time jumped); the pair results already recorded stay
  resetLines() { this.lines.length = 0; this.nextRelease = this.clock; }

  stepLines(dt, ca, cb, f, on) {
    this.tl.mesh.visible = this.dots.pts.visible = on;
    if (!on || !ca) { this.lines.length = 0; return; }
    this.clock += dt;
    const NZ = 37, z0 = -0.72, dz = 0.04, iTop = 33, iBot = 3, XC = 1.0;
    if (this.clock >= this.nextRelease) {
      this.nextRelease = this.clock + 1.6;
      const pts = [];
      for (let i = 0; i < NZ; i++) pts.push([-0.68, 0, z0 + i * dz]);
      this.lines.push({ pts, age: 0, tTop: null, tBot: null });
    }
    const v1 = [0, 0, 0], v2 = [0, 0, 0];
    const nsub = Math.max(1, Math.ceil(dt / 0.02)), h = dt / nsub;
    for (const L of this.lines) {
      for (let s = 0; s < nsub; s++) {
        for (const p of L.pts) {
          this.sampleCPU(ca, cb, f, p[0], p[1], p[2], v1);
          this.sampleCPU(ca, cb, f, p[0] + 0.5 * h * v1[0], p[1] + 0.5 * h * v1[1], p[2] + 0.5 * h * v1[2], v2);
          p[0] += h * v2[0]; p[1] += h * v2[1]; p[2] += h * v2[2];
        }
        L.age += h;
        if (L.tTop == null && L.pts[iTop][0] >= XC) L.tTop = L.age;
        if (L.tBot == null && L.pts[iBot][0] >= XC) L.tBot = L.age;
      }
      if (L.tTop != null && L.tBot != null && !L.done) {
        L.done = true;
        this.pairs.push(L.tBot - L.tTop);
        if (this.pairs.length > 8) this.pairs.shift();
      }
    }
    // a timeline fades out as its pair nears the end of the CFD box (the field is not known beyond it)
    const xEnd = this.hi.x - 0.05, xFade = xEnd - 0.4;
    this.lines = this.lines.filter((L) => L.age < 7 && Math.min(L.pts[iTop][0], L.pts[iBot][0]) < xEnd);
    // draw
    const ink = this.dark ? [1, 1, 1] : [0.13, 0.15, 0.17];
    this.tl.begin(); this.dots.begin();
    for (const L of this.lines) {
      const xe = Math.min(L.pts[iTop][0], L.pts[iBot][0]);
      const fade = Math.min(1, L.age / 0.3) * Math.max(0, Math.min(1, (L.age < 6.2 ? 1 : (7 - L.age) / 0.8), 1 - (xe - xFade) / (xEnd - xFade)));
      for (let i = 0; i < NZ - 1; i++) {
        const t0 = i / (NZ - 1), t1 = (i + 1) / (NZ - 1);
        const c = (t) => { const w = Math.abs(t - 0.5) * 2, base = t > 0.5 ? TOP : BOT; return [...base.map((x, k) => ink[k] + (x - ink[k]) * Math.min(1, 0.35 + w)), 0.9 * fade]; };
        this.tl.push(L.pts[i], L.pts[i + 1], c(t0), c(t1));
      }
      const P = L.pts[iTop], Q = L.pts[iBot];
      this.tl.push(P, Q, [...ink, 0.55 * fade]);
      for (let i = 0; i < NZ; i += 3) this.dots.push(L.pts[i], [...(i > NZ / 2 ? TOP : BOT), 0.85 * fade], 5);
      this.dots.push(P, [...TOP, fade], 13); this.dots.push(Q, [...BOT, fade], 13);
    }
    this.tl.end(); this.dots.end();
  }

  // average time by which the top tracer of a pair beats the bottom one to 1 D behind the ball (t*), or null
  pairLead() {
    if (!this.pairs.length) return null;
    return { n: this.pairs.length, dt: this.pairs.reduce((a, b) => a + b, 0) / this.pairs.length };
  }

  setRes(w, h, dpr) {
    this.trail.material.uniforms.uRes.value.set(w, h);
    this.tl.mat.uniforms.uRes.value.set(w, h);
    this.dots.mat.uniforms.uDpr.value = dpr;
    this.heads.material.uniforms.uSize.value = 2.4 * dpr;
    this.trail.material.uniforms.uWidth.value = 1.7 * dpr;
    this.tl.mat.uniforms.uWidth.value = 3.2 * dpr;
  }

  applyTheme(dark) {
    this.dark = dark;
    const bl = dark ? THREE.AdditiveBlending : THREE.NormalBlending;
    for (const m of [this.trail.material, this.heads.material]) { m.blending = bl; m.uniforms.uDark.value = dark ? 1 : 0; m.needsUpdate = true; }
    this.trail.material.uniforms.uAlpha.value = dark ? 0.7 : 0.85;
    this.vol.material.uniforms.uDark.value = dark ? 1 : 0;
  }

  dispose() {
    this.dead = true;
    this.group.parent?.remove(this.group);
    this.group.traverse((o) => { o.geometry?.dispose(); o.material?.dispose(); });
    for (const t of [...this.frames, this.mean]) t?.dispose();
    for (const rt of [...this.pos, this.hist]) rt.dispose();
    for (const m of [this.simMat, this.copyMat]) m.dispose();
    this.quad.geometry.dispose();
  }
}
