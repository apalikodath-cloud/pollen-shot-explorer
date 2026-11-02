// JS side of tests/test_field_geom.py (PM-015, research/GEOMETRY_AUDIT.md fixes 2, 3, 5, 8): prints one JSON line
// with viz/explorer/solver.js footprint(), sightBlocked(), roofClearDrop() and roofClearSection() results for the
// cases given on stdin (JSON). No field data needed. Run: node tests/js_field_geom_check.js < cases.json
"use strict";
const path = require("path");
const S = require(path.join(__dirname, "..", "viz", "explorer", "solver.js"));

let buf = "";
process.stdin.on("data", function (d) { buf += d; });
process.stdin.on("end", function () {
  const q = JSON.parse(buf || "{}");
  const out = { constants: S.constants, footprint: [], sight: [], roofDrop: S.roofClearDrop(0.0355) };
  for (const c of q.footprint || []) {
    const robot = { length: c.length, width: c.width, offset: c.offset };
    if (c.heading !== null && c.heading !== undefined) robot.heading = c.heading;
    const f = S.footprint(c.x, c.y, robot);
    out.footprint.push({ ok: f.ok, wall: f.wall, base: f.base, release: f.release, heading: f.heading });
  }
  for (const c of q.sight || []) out.sight.push(S.sightBlocked(c[0], c[1], c[2], c[3]));
  // synthetic section: roof segments must move down by the drop along the wall axis, the rest must not move
  const sec = { names: ["a_floor", "b_roof_outer", "c_upper_lip", "d_roof_inner", "e_wall"], normal: [1, 0],
                P0: [[0, 0], [0, 1], [0.1, 1], [0.2, 1], [0.3, 0]], P1: [[1, 0], [1, 1], [0.2, 1], [0.3, 1], [0.3, 1]],
                inside: [[0, 0], [1, 0], [1, 1], [0, 1]], gate: [[0, 0.2], [0, 0.9]], key: "syn", how: "synthetic" };
  const r = S.roofClearSection(sec, 0.0355);
  out.roofSection = { P0: r.P0, P1: r.P1, inside: r.inside, gate: r.gate, key: r.key, roofDrop: r.roofDrop,
                      cached: S.roofClearSection(sec, 0.0355) === r, origUnchanged: sec.P0[1][1] === 1 };
  process.stdout.write(JSON.stringify(out) + "\n");
});
