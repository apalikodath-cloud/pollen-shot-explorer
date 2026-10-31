// helper for tests/test_field.py: reads {p, S, R, trajs:[{v,th,psi}], shots:[{v,th,psi,d,h,sec,cell3d,aimX}], secs}
// from stdin when called with --stdin, prints {traj:[{X,Y,Z}...], cls:[bool...]} using viz/explorer/physics.js.
// shot.cell3d false/absent: section model, classifyOblique on secs[sec] (the s_eff section);
// shot.cell3d true: 3D cell (PM-013/PM-019), classifyOblique3D on buildCell3D(secs[sec]) (secs[sec] = s = 0 section)
// Run standalone (node tests/js_oblique_check.js, no --stdin; stdin is not read): self-check of integrateOblique (the psi path is the
// psi = 0 path with X scaled by cos psi, Y = X sin psi, mirrored in Y for -psi); exit 0 = pass, 1 = fail.
"use strict";
const fs = require("fs"), path = require("path");
const P = require(path.join(__dirname, "..", "viz", "explorer", "physics.js"));
const raw = process.argv.includes("--stdin") ? fs.readFileSync(0, "utf8") : "";

if (!raw.trim()) {
  // PREDICTED model self-consistency only; params ASSUMED (literature-style nominal values)
  const p = { rho: 1.2041, mass: 0.02495, radius: 0.0355, Cd: 0.5, c1: 0.35, clmax: 0.25, k: 0.03, g: 9.80665 };
  let err = 0, n = 0;
  for (const [v, th, psi] of [[8.0, 77.0, 30.0], [6.0, 70.0, 45.0], [9.5, 80.0, 60.0]]) {
    const b = P.integrateOblique(v, th, 0, 1.0, p, 2e-3, 1.2, -9);
    const a = P.integrateOblique(v, th, psi, 1.0, p, 2e-3, 1.2, -9), m = P.integrateOblique(v, th, -psi, 1.0, p, 2e-3, 1.2, -9);
    const c = Math.cos(psi * Math.PI / 180), s = Math.sin(psi * Math.PI / 180);
    if (a.n !== b.n || m.n !== b.n) { err = Infinity; continue; }
    for (let i = 0; i < b.n; i++, n++) {
      err = Math.max(err, Math.abs(a.X[i] - b.X[i] * c), Math.abs(a.Y[i] - b.X[i] * s), Math.abs(a.Z[i] - b.Z[i]),
                     Math.abs(m.X[i] - a.X[i]), Math.abs(m.Y[i] + a.Y[i]), Math.abs(m.Z[i] - a.Z[i]));
    }
  }
  const ok = err < 1e-12 && n > 100;
  console.log((ok ? "PASS" : "FAIL") + " integrateOblique projection and +-psi mirror  " + n + " samples, max error " + err.toExponential(2) + " m");
  console.log(JSON.stringify({ failed: ok ? 0 : 1, checks: 1 }));
  process.exit(ok ? 0 : 1);
}

const inp = JSON.parse(raw);
const out = { traj: [], cls: [] }, cells = {};
for (const t of inp.trajs) {
  const r = P.integrateOblique(t.v, t.th, t.psi, inp.S, inp.p, 2e-3, 1.2, -9);
  const n = Math.min(r.n, 601), pick = [];
  for (let i = 0; i < n; i += 100) pick.push([r.X[i], r.Y[i], r.Z[i]]);
  out.traj.push(pick);
}
for (const s of inp.shots) {
  const r = P.integrateOblique(s.v, s.th, s.psi, inp.S, inp.p, 2e-3, 3.0, 0.4 - 0.0);
  let c;
  if (s.cell3d) {
    const cell = cells[s.sec] || (cells[s.sec] = P.buildCell3D(inp.secs[s.sec]));
    c = P.classifyOblique3D(r, cell, s.d, s.h, inp.R, s.aimX, s.psi);
  } else c = P.classifyOblique(r, inp.secs[s.sec], s.d, s.h, inp.R);
  out.cls.push(c.result === "clean");
}
process.stdout.write(JSON.stringify(out));
