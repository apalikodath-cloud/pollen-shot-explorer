// Node checks for viz/explorer/solver.js (PM-009). Run: node tests/js_solver_check.js
// Exit 0 = all checks pass, 1 = a check failed, 77 = field data missing (gitignored; regenerate with
// viz/explorer/export_field.py). Prints one line per check and a JSON summary as the last line.
"use strict";
const fs = require("fs"), path = require("path");
const EX = path.join(__dirname, "..", "viz", "explorer");
const FIELD = path.join(EX, "data", "field");
const P = require(path.join(EX, "physics.js"));
const Sv = require(path.join(EX, "solver.js"));

if (!fs.existsSync(path.join(FIELD, "index.json"))) { console.log("SKIP field data missing"); process.exit(77); }
const meta = JSON.parse(fs.readFileSync(path.join(FIELD, "index.json"), "utf8"));
const G = meta.grid, nH = G.h.length, nPsi = G.psi.length, nD = G.d.length;
const summary = {}; let failed = 0;
function check(name, ok, info) {
  console.log((ok ? "PASS " : "FAIL ") + name + (info ? "  " + info : ""));
  summary[name] = { ok: !!ok, info: info || "" };
  if (!ok) failed++;
}
let seed = 20261030;
function rnd() { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; }
function pick(a) { return a[Math.floor(rnd() * a.length)]; }

// ---- mask decoding (FIELD_DATA.md): u32 n | u32 off[nPsi*nH+1] | u32 idx[n] | u16 margin[n] | u16 ang[n]
const maskCache = {};
function mask(side, tag) {
  const key = side + "_" + tag;
  if (maskCache[key]) return maskCache[key];
  const f = path.join(FIELD, "mask_" + key + ".b64.txt");
  if (!fs.existsSync(f)) { console.log("SKIP missing " + f); process.exit(77); }
  const buf = Buffer.from(fs.readFileSync(f, "utf8"), "base64");
  const dv = new DataView(buf.buffer, buf.byteOffset, buf.byteLength);
  const n = dv.getUint32(0, true), no = nPsi * nH + 1;
  const off = new Uint32Array(no), idx = new Uint32Array(n);
  for (let i = 0; i < no; i++) off[i] = dv.getUint32(4 + 4 * i, true);
  const b = 4 + 4 * no;
  for (let i = 0; i < n; i++) idx[i] = dv.getUint32(b + 4 * i, true);
  return (maskCache[key] = { off: off, idx: idx });
}
// clean set for one (side, tag, psi index, h index, d index) as a Uint8Array over (iv, ith)
function window(side, tag, ip, ih, id) {
  const m = mask(side, tag), nV = G.v[side].length, nTh = G.theta[side].length, per = nV * nTh;
  const s = ip * nH + ih, out = new Uint8Array(per);
  for (let k = m.off[s]; k < m.off[s + 1]; k++) {
    const i = m.idx[k];
    if (Math.floor(i / per) === id) out[i % per] = 1;
  }
  return out;
}
function caseOf(S) { return meta.cases.find(c => c.S === S && c.var === "nominal"); }
function poseXY(side, d, psiDeg) {
  const Lh = side === "fav" ? Math.max(d - 0.401, 1e-3) : d + 0.401;
  return [side === "fav" ? d : -d, Lh * Math.tan(psiDeg * Math.PI / 180)];
}

// ---------------------------------------------------------------- (0) fast path == physics.js
{
  let n = 0, bad = 0, badM = 0;
  const out = [0, 0, 0, 0];
  for (let k = 0; k < 1500; k++) {
    const c = caseOf(pick([0, 0.5, 1.0, 1.5])), side = k % 2 ? "fav" : "unfav";
    const psi = (rnd() * 75) * (rnd() < 0.5 ? -1 : 1), h = 0.1 + rnd() * 0.7, d = 0.5 + rnd() * 1.3;
    const v = side === "unfav" ? 5 + rnd() * 6 : 2 + rnd() * 9, th = side === "unfav" ? 55 + rnd() * 34.8 : 15 + rnd() * 74.5;
    const sec = Sv.sectionFor(side, psi, meta), pr = Sv._prepSection(sec), zs = Sv._zStopFor(h, pr);
    const p = rnd() < 0.2 ? Object.assign({}, c.params, { c1: 0 }) : c.params;
    const path_ = P.integrateOblique(v, th, psi, c.S, p, 2e-3, 3.0, zs);
    const cl = P.classifyOblique(path_, sec, d, h, p.radius);
    const f = Sv._fastShot(v, th, Math.cos(Math.abs(psi) * Math.PI / 180), c.S, p, pr, d, h, zs, out);
    n++;
    if ((cl.result === "clean") !== (f === 1)) bad++;
    else if (f === 1 && (Math.abs(cl.minClear - out[0]) > 1e-12 ||
             (cl.entryAngle !== null && Math.abs(cl.entryAngle - out[1]) > 1e-9))) badM++;
  }
  check("fast_path_equals_physics_js", bad === 0 && badM === 0, `${n} shots, class disagree ${bad}, margin/entry disagree ${badM}`);
}

// ---------------------------------------------------------------- (1) live vs precomputed masks
{
  const RASTER_ERR = 2.5e-3;
  let n = 0, agree = 0, interior = 0, resolution = 0, clean = 0;
  const out = [0, 0, 0, 0], perSide = { unfav: 0, fav: 0 }, Ss = new Set(), psis = new Set();
  for (let blk = 0; blk < 64; blk++) {
    const side = blk % 2 ? "fav" : "unfav", S = [0, 0.5, 1.0, 1.5][(blk >> 1) % 4];
    const tag = caseOf(S).tag, ip = [0, 2, 4, 6, 8, 10, 12, 14][(blk >> 3) % 8];
    const ih = Math.floor(rnd() * nH), id = Math.floor(rnd() * nD);
    const w = window(side, tag, ip, ih, id);
    const V = G.v[side], TH = G.theta[side], nTh = TH.length, nV = V.length;
    const cl = [], nc = [];
    for (let i = 0; i < w.length; i++) {
      if (w[i]) cl.push(i);
      else {
        // non-clean cells within 3 cells of the window (where disagreements would show)
        const iv = Math.floor(i / nTh), it = i % nTh;
        let near = false;
        for (let a = -3; a <= 3 && !near; a++) for (let b = -3; b <= 3 && !near; b++) {
          const jv = iv + a, jt = it + b;
          if (jv >= 0 && jv < nV && jt >= 0 && jt < nTh && w[jv * nTh + jt]) near = true;
        }
        if (near) nc.push(i);
      }
    }
    if (!cl.length) continue;
    const c = caseOf(S), psi = G.psi[ip], h = G.h[ih], d = G.d[id];
    // the exported masks use the 3D cell since PM-019 (index.json cell_model): compare with the live 3D-cell
    // context (sideWalls default) at the export's own params (rho as exported, no q.air)
    const [px, py] = poseXY(side, d, psi);
    const ctx = Sv._context({ x: px, y: py, h: h, S: S, params: c.params, meta: meta });
    const cells = [];
    for (let k = 0; k < 6; k++) cells.push(pick(cl));
    for (let k = 0; k < 6 && nc.length; k++) cells.push(pick(nc));
    for (const i of cells) {
      const iv = Math.floor(i / nTh), it = i % nTh;
      const live = Sv._shotCtx(ctx, V[iv], TH[it], S, c.params, h, out) === 1;
      const ref = w[i] === 1;
      n++; perSide[side]++; Ss.add(S); psis.add(psi); if (ref) clean++;
      if (live === ref) { agree++; continue; }
      // interior = all 4 neighbours (v +-1, theta +-1) carry the same mask value
      let inner = iv > 0 && iv < nV - 1 && it > 0 && it < nTh - 1;
      if (inner) for (const j of [i - nTh, i + nTh, i - 1, i + 1]) if (w[j] !== w[i]) inner = false;
      if (!inner) continue;
      // an interior cell can still be a knife edge below the mask's resolution (raster 1 mm, point samples every
      // 2 ms: clearance error <= ~2.5 mm, src/feasibility.py): explained only when the exact classifier
      // (physics.js classifyOblique3D, the twin of src/cell3d.py) agrees with the live result and its clearance
      // (clean) or penetration (hit) is within that bound; anything else is a real disagreement
      const pth = P.integrateOblique(V[iv], TH[it], ctx.ps.psi, S, c.params, 2e-3, 3.0, ctx.zStop);
      const ex = Sv._classifyCtx(ctx, pth, h, c.params.radius);
      const tag2 = `${side} ${tag} psi ${psi} h ${h} d ${d} v ${V[iv]} th ${TH[it]} mask ${ref} live ${live}, exact ${ex.result} clearance ${(1000 * ex.minClear).toFixed(2)} mm`;
      if ((ex.result === "clean") === live && Math.abs(ex.minClear) <= RASTER_ERR) {
        resolution++; console.log("  knife edge below the mask resolution (explained)", tag2);
      } else { interior++; console.log("  interior disagreement", tag2); }
    }
  }
  const frac = agree / n;
  check("live_vs_mask_agreement", n >= 300 && frac >= 0.98 && interior === 0,
        `${agree}/${n} = ${(100 * frac).toFixed(2)} % (clean ${clean}), interior disagreements ${interior} (+ ${resolution} knife edges below the mask resolution), ` +
        `per side ${JSON.stringify(perSide)}, S ${[...Ss].join("/")}, psi ${[...psis].join("/")}`);
}

// ---------------------------------------------------------------- (2) minRpm / minAngle vs mask
const timings = [];
{
  const cases = [["unfav", 1.0, 4, 1, 12], ["unfav", 0.0, 0, 4, 8], ["fav", 0.5, 6, 2, 10], ["fav", 1.5, 2, 0, 16],
                 ["unfav", 0.5, 8, 3, 18]];
  const msgs = []; let ok = true;
  for (const [side, S, ip, ih, id] of cases) {
    const c = caseOf(S), w = window(side, c.tag, ip, ih, id);
    const V = G.v[side], TH = G.theta[side], nTh = TH.length;
    let mv = Infinity, mt = Infinity;
    for (let i = 0; i < w.length; i++) if (w[i]) { mv = Math.min(mv, V[Math.floor(i / nTh)]); mt = Math.min(mt, TH[i % nTh]); }
    const [x, y] = poseXY(side, G.d[id], G.psi[ip]);
    // the exported masks use the 3D cell since PM-019: compare with the live default (sideWalls true, 3D cell)
    // air: false = keep the export's params rho so the live solve and the masks share one air state
    const q = { x: x, y: y, h: G.h[ih], S: S, vu: 0.5, params: c.params, meta: meta, sideWalls: true, air: false,
                vRange: [V[0], V[V.length - 1]], thRange: [TH[0], TH[nTh - 1]] };
    const r = Sv.solve(q);
    timings.push(r.ms);
    const stV = V[1] - V[0], stT = TH[1] - TH[0];
    const tag = `${side} S${S} psi${G.psi[ip]} h${G.h[ih]} d${G.d[id]}`;
    if (!isFinite(mv)) { const good = r.count === 0 || r.minRpm !== null; msgs.push(`${tag}: mask empty, live count ${r.count}`); ok = ok && good; continue; }
    if (!r.minRpm || !r.minAngle) { ok = false; msgs.push(`${tag}: live found nothing, mask min v ${mv}`); continue; }
    // within one grid step; a live minimum below that must be a real clean shot (an island narrower
    // than the export grid), confirmed by physics.js
    function confirm(v, th) {
      const ctx = Sv._context(q);
      const pth = P.integrateOblique(v, th, ctx.ps.psi, S, c.params, 2e-3, 3.0, ctx.zStop);
      return Sv._classifyCtx(ctx, pth, G.h[ih], c.params.radius).result === "clean";
    }
    const dV = r.minRpm.v - mv, dT = r.minAngle.theta - mt;
    const how = function (dd, st, v, th) {
      if (Math.abs(dd) <= st + 1e-6) return "within one step";
      if (dd < 0 && confirm(v, th)) return "below the export grid, confirmed clean by physics.js";
      return "BAD";
    };
    const hV = how(dV, stV, r.minRpm.v, r.minRpm.theta), hT = how(dT, stT, r.minAngle.v, r.minAngle.theta);
    ok = ok && hV !== "BAD" && hT !== "BAD";
    msgs.push(`${tag}: v live ${r.minRpm.v.toFixed(3)} mask ${mv} (${hV}), theta live ${r.minAngle.theta.toFixed(3)} mask ${mt} (${hT}), ${r.ms.toFixed(0)} ms`);
  }
  check("min_rpm_min_angle_vs_mask", ok, "\n    " + msgs.join("\n    "));
}

// ---------------------------------------------------------------- (3) twin
{
  const c = caseOf(1.0), [x, y] = poseXY("unfav", 1.2, 15);
  const r = Sv.solve({ x: x, y: y, h: 0.5, S: 1.0, vu: 0.5, params: c.params, meta: meta });
  timings.push(r.ms);
  const t = r.twin;
  const okT = t && t.S === 0 && t.params.c1 === 0 && t.grid && t.isTwin === true && c.params.c1 > 0;
  let diff = 0; for (let i = 0; i < r.grid.clean.length; i++) if (r.grid.clean[i] !== t.grid.clean[i]) diff++;
  const c0 = caseOf(0.0), r0 = Sv.solve({ x: x, y: y, h: 0.5, S: 0, vu: 0.5, params: c0.params, meta: meta });
  let same = 0; for (let i = 0; i < r0.grid.clean.length; i++) if (r0.grid.clean[i] === r0.twin.grid.clean[i]) same++;
  const sh = Sv.shot({ x: x, y: y, h: 0.5, S: 1.0, vu: 0.5, params: c.params, meta: meta }, 7.5, 76);
  const okShot = sh.twin && sh.twin.S === 0 && sh.path.n > 10 && sh.twin.path.n > 10;
  check("twin_always_present_S0", okT && diff > 0 && same === r0.grid.clean.length && okShot,
        `twin S ${t && t.S}, twin c1 ${t && t.params.c1}, cells differing from S=1 ${diff}, S=0 twin identical ${same === r0.grid.clean.length}, shot() twin ${!!okShot}`);
}

// ---------------------------------------------------------------- (4) pose vs pos_status
{
  const fg = meta.field_grid, nx = fg.nx, ny = fg.ny, N = nx * ny;
  const buf = Buffer.from(fs.readFileSync(path.join(FIELD, "pos_status.b64.txt"), "utf8"), "base64");
  const dv = new DataView(buf.buffer, buf.byteOffset, buf.byteLength);
  const st = i => dv.getUint8(i), oth = i => dv.getUint8(N + i), fav = i => dv.getUint8(2 * N + i);
  const di = i => dv.getInt16(3 * N + 2 * i, true), psi = i => dv.getUint16(7 * N + 2 * i, true);
  let n = 0, bad = 0; const badMsg = [];
  for (let iy = 0; iy < ny; iy++) for (let ix = 0; ix < nx; ix++) {
    const i = iy * nx + ix, x = fg.xs[ix], y = fg.ys[iy], p = Sv.pose(x, y, meta);
    const s = st(i);
    const want = s === 1 ? "illegal" : (s === 2 || s === 3) ? "beyond_model" : null;
    let ok = want ? p.status === want
                  : (p.status === (Math.abs(p.psi) > G.psi_max_model ? "psi_extrapolated" : "ok"));
    ok = ok && Math.abs(Math.round(Math.abs(p.psi) * 100) - psi(i)) <= 1;
    ok = ok && ((p.side === "fav") === (fav(i) === 1)) && (p.otherHive === (oth(i) === 1));
    if (s === 0) {
      const id = Math.min(nD - 1, Math.max(0, Math.round((p.d - G.d[0]) / 0.05)));
      ok = ok && id === di(i);
      ok = ok && p.sideWallRisk === (Math.abs(p.psi) >= G.psi_side_wall);
    }
    n++;
    if (!ok) { bad++; if (badMsg.length < 5) badMsg.push(`(${x},${y}) export st ${s} psi ${psi(i)} di ${di(i)} -> ${p.status} ${p.psi.toFixed(2)} d ${p.d.toFixed(3)}`); }
  }
  check("pose_matches_pos_status", bad === 0, `${n - bad}/${n} grid positions` + (badMsg.length ? "; " + badMsg.join("; ") : ""));
  // continuous pose: not snapped
  const a = Sv.pose(-1.2345, 0.4321, meta);
  const okC = Math.abs(a.d - 1.2345) < 1e-12 && Math.abs(a.Lh - 1.6355) < 1e-12 &&
              Math.abs(Math.tan(a.psi * Math.PI / 180) - 0.4321 / 1.6355) < 1e-12 &&
              Math.abs(a.bearingDeg - Math.atan2(-0.4321, 0.401 + 1.2345) * 180 / Math.PI) < 1e-9;
  check("pose_continuous", okC, `d ${a.d} psi ${a.psi.toFixed(4)} bearing ${a.bearingDeg.toFixed(3)}`);
}

// ---------------------------------------------------------------- (5) sections, pruning, shot()
{
  // exact match returns the exported section; interpolating at a bin from its two neighbours
  // reproduces the exported section (roof drop is linear in s)
  let errMax = 0;
  for (const side of ["unfav", "fav"]) {
    const e = Sv.sectionFor(side, 20, meta);
    if (e.how !== "exported") errMax = Infinity;
    const keys = Object.keys(meta.sections).filter(k => k.startsWith(side + "_s"))
      .map(k => [parseFloat(k.split("_s")[1]), k]).sort((a, b) => a[0] - b[0]);
    for (let j = 1; j < keys.length - 1; j++) {
      const a = meta.sections[keys[j - 1][1]], b = meta.sections[keys[j + 1][1]], m = meta.sections[keys[j][1]];
      const t = (keys[j][0] - keys[j - 1][0]) / (keys[j + 1][0] - keys[j - 1][0]);
      for (const f of ["P0", "P1", "inside", "gate"]) for (let i = 0; i < m[f].length; i++) for (let k = 0; k < 2; k++)
        errMax = Math.max(errMax, Math.abs(a[f][i][k] + t * (b[f][i][k] - a[f][i][k]) - m[f][i][k]));
    }
  }
  const mid = Sv.sectionFor("unfav", 12.5, meta);
  check("section_interpolation_exact", errMax < 5e-5 && /interpolated/.test(mid.how), `max leave-one-out error ${errMax.toExponential(2)} m`);

  // pruned coarse grid loses no clean cell vs the unpruned grid
  let lost = 0, tot = 0;
  for (const [side, S, d, psi, h] of [["unfav", 1.0, 1.3, 25, 0.35], ["fav", 0.5, 1.1, 40, 0.6], ["unfav", 0.0, 0.8, 50, 0.737]]) {
    const c = caseOf(S), [x, y] = poseXY(side, d, psi);
    const q = { x: x, y: y, h: h, S: S, vu: 0.5, params: c.params, meta: meta, refine: false };
    const a = Sv.solve(q), b = Sv.solve(Object.assign({}, q, { prune: false }));
    for (const [ga, gb] of [[a.grid, b.grid], [a.twin.grid, b.twin.grid]])
      for (let i = 0; i < gb.clean.length; i++) { tot += gb.clean[i]; if (gb.clean[i] && !ga.clean[i]) lost++; }
  }
  check("pruning_loses_nothing", lost === 0 && tot > 100, `lost ${lost} of ${tot} clean cells`);

  // shot(): starts at the release point, heads along the bearing, same class as the fast path
  const c = caseOf(1.0), q = { x: -1.1, y: 0.7, h: 0.45, S: 1.0, vu: 0.5, params: c.params, meta: meta };
  const r = Sv.solve(q), mf = r.mostForgiving || r.minRpm;
  const sh = Sv.shot(q, mf.v, mf.theta), pth = sh.path, ps = r.pose;
  const j = Math.min(pth.n - 1, 50);
  const ang = Math.atan2(pth.y[j] - q.y, pth.x[j] - q.x) * 180 / Math.PI;
  const ctx = Sv._context(q), out = [0, 0, 0, 0];
  const fc = Sv._shotCtx(ctx, mf.v, mf.theta, 1.0, c.params, q.h, out);
  const okS = Math.abs(pth.x[0] - q.x) < 1e-12 && Math.abs(pth.y[0] - q.y) < 1e-12 && Math.abs(pth.z[0] - q.h) < 1e-12 &&
              Math.abs(ang - ps.bearingDeg) < 1e-6 && (sh.cls.result === "clean") === (fc === 1) && sh.cls.result === "clean";
  check("shot_field_mapping", okS, `bearing ${ps.bearingDeg.toFixed(3)} path heading ${ang.toFixed(3)}, class ${sh.cls.result}, rpm ${sh.rpm.toFixed(0)}`);
  const okR = Math.abs(Sv.vFromRpm(Sv.rpm(7.3, 0.55), 0.55) - 7.3) < 1e-12 &&
              Math.abs(Sv.rpm(7.3, 0.5) - 7.3 / 0.5 / (Math.PI * 0.098) * 60) < 1e-9;
  check("rpm_helpers", okR, `rpm(7.3 m/s, v/u 0.5) = ${Sv.rpm(7.3, 0.5).toFixed(1)}`);
}

// ---------------------------------------------------------------- (5b) minima: clearance, runs, tolerant minima
// Review of 59588d2: the raw minima are knife edges (clearance 0-0.4 mm) and the old spans were envelopes
// with hits inside. Now each minimum carries its clearance + entry angle, a continuous clean run (every
// sample clean per physics.js), the envelope with its clean fraction, and a tolerant minimum.
{
  const msgs = []; let ok = true;
  for (const [x, y, h, S] of [[-0.7135, 1.2442, 0.632, 0], [1.0312, 1.5602, 0.335, 1], [-1.432, 0.6084, 0.268, 1.5]]) {
    const c = caseOf(S), q = { x: x, y: y, h: h, S: S, vu: 0.5, params: c.params, meta: meta, air: false };
    const r = Sv.solve(q), ctx = Sv._context(q), tol = r.tol;
    timings.push(r.ms);
    const cls = (v, th) => Sv._classifyCtx(ctx, P.integrateOblique(v, th, ctx.ps.psi, S, c.params, 2e-3, 3.0, ctx.zStop), h, c.params.radius);
    const m = r.minRpm, a = r.minAngle, mt = r.minRpmTol, at = r.minAngleTol;
    let holes = 0, tolBad = 0;
    for (let t = m.runLo; t <= m.runHi + 1e-9; t += 0.01) if (cls(m.v, t).result !== "clean") holes++;
    for (let v = a.runLo; v <= a.runHi + 1e-9; v += 0.005) if (cls(v, a.theta).result !== "clean") holes++;
    if (mt) for (let t = mt.thetaLo; t <= mt.thetaHi + 1e-9; t += 0.01) { const k = cls(mt.v, t); if (k.result !== "clean" || k.minClear < tol.margin - 1.5e-3) tolBad++; }
    if (at) for (let v = at.vLo; v <= at.vHi + 1e-9; v += 0.005) { const k = cls(v, at.theta); if (k.result !== "clean" || k.minClear < tol.margin - 1.5e-3) tolBad++; }
    const fields = isFinite(m.margin) && isFinite(m.entryAngle) && isFinite(a.margin) && typeof m.knifeEdge === "boolean" &&
                   m.envelopeCleanFrac > 0 && m.envelopeCleanFrac <= 1 && m.runLo <= m.theta + 1e-9 && m.runHi >= m.theta - 1e-9;
    const tolOk = !!mt && !!at && mt.v >= m.v - 1e-9 && at.theta >= a.theta - 1e-9 && mt.run >= tol.theta - 1e-9 && at.run >= tol.v - 1e-9 &&
                  mt.margin >= tol.margin && at.margin >= tol.margin;
    // the failing case from the review: minRpm 5.99 m/s with 0.003 mm clearance must be flagged a knife edge
    // (3D cell model, PM-013: the minimum there moves to 5.84 m/s, 1.5 mm clearance but a 0.05 deg run: still a knife edge)
    const knifeOk = !(x === -0.7135) || (m.knifeEdge && (m.margin < 1e-3 || m.run < tol.theta));
    ok = ok && holes === 0 && tolBad === 0 && fields && tolOk && knifeOk;
    msgs.push(`(${x},${y}) S${S}: minRpm ${m.v.toFixed(3)} clr ${(m.margin * 1000).toFixed(2)} mm run ${m.run.toFixed(3)} deg knife ${m.knifeEdge}; ` +
              `tol ${mt ? mt.v.toFixed(2) + " m/s run " + mt.run.toFixed(2) + " deg clr " + (mt.margin * 1000).toFixed(1) + " mm" : "none"}; ` +
              `minAngleTol ${at ? at.theta.toFixed(2) : "none"}; holes ${holes}, tol samples bad ${tolBad}`);
  }
  check("minima_clearance_runs_tolerant", ok, "\n    " + msgs.join("\n    "));
}

// ---------------------------------------------------------------- (6) timing over the field
{
  const c = caseOf(1.0), ts = [];
  for (const [x, y, h] of [[-1.5, 0.2, 0.737], [-0.9, -0.9, 0.3], [1.3, 0.4, 0.5], [0.8, 1.6, 0.65], [-1.7, 1.9, 0.2]]) {
    const r = Sv.solve({ x: x, y: y, h: h, S: 1.0, vu: 0.5, params: c.params, meta: meta });
    ts.push(r.ms); timings.push(r.ms);
  }
  const mx = Math.max(...timings), mean = timings.reduce((a, b) => a + b, 0) / timings.length;
  // wall-clock limit fails only with STRICT_TIMING=1: on a shared, loaded machine it is reported, not enforced
  const strict = process.env.STRICT_TIMING === "1", tOk = mx < 10000;
  check("timing", !strict || tOk, `full solve + twin: mean ${mean.toFixed(0)} ms, max ${mx.toFixed(0)} ms over ${timings.length} solves (target about 2000 ms; ` +
        `max under 10 s: ${tOk ? "yes" : "NO, " + (strict ? "enforced" : "reported only; STRICT_TIMING=1 enforces")})`);
  summary.timing_ms = { mean: Math.round(mean), max: Math.round(mx) };
}

console.log(JSON.stringify({ failed: failed, checks: Object.keys(summary).length - 1, timing_ms: summary.timing_ms }));
process.exit(failed ? 1 : 0);
