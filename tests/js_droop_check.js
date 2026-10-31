// JS side of tests/test_launcher.py DroopReadout (PM-022): reads {cases:[{rpm, v, S, o}]} as JSON on stdin and prints one
// JSON line {out:[droopReadout(rpm, v, S, o)...], defaults: DROOP} from viz/explorer/solver.js (closed-form flywheel droop
// and recovery, twin of src/launcher.py droop_readout). Infinity is printed as null. No field data needed.
// Run: node tests/js_droop_check.js < cases.json
"use strict";
const path = require("path");
const S = require(path.join(__dirname, "..", "viz", "explorer", "solver.js"));

let buf = "";
process.stdin.on("data", function (d) { buf += d; });
process.stdin.on("end", function () {
  const q = JSON.parse(buf || "{}");
  const out = (q.cases || []).map(function (c) { return S.droopReadout(c.rpm, c.v, c.S, c.o); });
  process.stdout.write(JSON.stringify({ out: out, defaults: S.DROOP }) + "\n");
});
