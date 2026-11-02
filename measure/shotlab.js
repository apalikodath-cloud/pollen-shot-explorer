// POLLEN Shot Lab page: shot-log exit-speed fit, battery-sag compensation, rpm map, shoot-on-the-move and the
// near-lip hypothesis test. The solver runs in shotlab_worker.js; pure maths lives in shotcore.js.
(function () {
  "use strict";
  var FIELD_URL = "../data/field/index.json";
  var C = window.PollenShotCore, A = window.PollenAssist, PS = window.PollenSolver;
  var $ = function (id) { return document.getElementById(id); };
  var NS = "http://www.w3.org/2000/svg";
  var ST = { FI: null, meta: null, map: null, lip: null, fit: null, sag: null, tel: null, jobs: {}, nextId: 1, worker: null };
  var AERO = { nominal: "Nominal (literature middle)", Cl_low: "Low lift", Cl_high: "High lift", Cd_low: "Low drag", Cd_high: "High drag" };

  function loadJSON(k, d) { try { var s = localStorage.getItem(k); return s ? JSON.parse(s) : d; } catch (_) { return d; } }
  function saveJSON(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch (_) { return false; } }
  function num(id) { var v = parseFloat($(id).value); return isFinite(v) ? v : NaN; }
  function f(x, n) { return isFinite(x) ? Number(x).toFixed(n) : "–"; }
  function el(tag, attrs, parent) { var e = document.createElementNS(NS, tag); for (var k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; }
  function lab(t) { return '<span class="lab">' + t + "</span>"; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  // ---------- worker
  function worker() {
    if (ST.worker) return ST.worker;
    var w = new Worker("shotlab_worker.js");
    w.onmessage = function (e) {
      var m = e.data, j = ST.jobs[m.id]; if (!j) return;
      if (m.progress !== undefined) { if (j.onProgress) j.onProgress(m.progress); return; }
      delete ST.jobs[m.id];
      if (m.error) j.reject(new Error(m.error)); else j.resolve(m.result);
    };
    w.onerror = function (e) { Object.keys(ST.jobs).forEach(function (k) { ST.jobs[k].reject(new Error(e.message || "worker error")); delete ST.jobs[k]; }); };
    w.postMessage({ meta: ST.meta });
    ST.worker = w;
    return w;
  }
  function run(job, o, onProgress) {
    var id = ST.nextId++;
    return new Promise(function (resolve, reject) {
      ST.jobs[id] = { resolve: resolve, reject: reject, onProgress: onProgress };
      worker().postMessage({ id: id, job: job, q: query(), o: o });
    });
  }
  function caseFor(S, v) { return ST.FI.cases.find(function (c) { return c.S === S && c.var === v; }); }
  function query() {
    var S = +$("S").value, cs = caseFor(S, $("aero").value) || caseFor(S, "nominal");
    return { h: num("h"), S: S, vu: num("vu") > 0 ? num("vu") : 0.42, params: cs.params, air: { tC: 20, altM: 0, rh: 0 } };
  }

  // ---------- charts
  function axes(svg, W, H, m, xr, yr, xl, yl, nx, ny) {
    svg.innerHTML = "";
    // round tick steps (1, 2, 2.5, 5 x 10^k); the range snaps out to whole steps
    var sx = niceStep((xr[1] - xr[0]) / nx), sy = niceStep((yr[1] - yr[0]) / ny);
    xr = [Math.floor(xr[0] / sx + 1e-9) * sx, Math.ceil(xr[1] / sx - 1e-9) * sx]; yr = [Math.floor(yr[0] / sy + 1e-9) * sy, Math.ceil(yr[1] / sy - 1e-9) * sy];
    nx = Math.round((xr[1] - xr[0]) / sx); ny = Math.round((yr[1] - yr[0]) / sy);
    var X = function (x) { return m.l + (x - xr[0]) / (xr[1] - xr[0]) * (W - m.l - m.r); };
    var Y = function (y) { return H - m.b - (y - yr[0]) / (yr[1] - yr[0]) * (H - m.t - m.b); };
    for (var i = 0; i <= nx; i++) { var x = xr[0] + (xr[1] - xr[0]) * i / nx; el("line", { x1: X(x), x2: X(x), y1: m.t, y2: H - m.b, class: "grid" }, svg); el("text", { x: X(x), y: H - m.b + 14, class: "ax", "text-anchor": "middle" }, svg).textContent = +x.toFixed(6); }
    for (i = 0; i <= ny; i++) { var y = yr[0] + (yr[1] - yr[0]) * i / ny; el("line", { x1: m.l, x2: W - m.r, y1: Y(y), y2: Y(y), class: "grid" }, svg); el("text", { x: m.l - 6, y: Y(y) + 4, class: "ax", "text-anchor": "end" }, svg).textContent = +y.toFixed(6); }
    el("text", { x: (m.l + W - m.r) / 2, y: H - 4, class: "ax", "text-anchor": "middle" }, svg).textContent = xl;
    el("text", { x: 12, y: (m.t + H - m.b) / 2, class: "ax", "text-anchor": "middle", transform: "rotate(-90 12 " + (m.t + H - m.b) / 2 + ")" }, svg).textContent = yl;
    return { X: X, Y: Y };
  }
  function niceStep(raw) { var e = Math.pow(10, Math.floor(Math.log10(raw))), r = raw / e; return (r <= 1 ? 1 : r <= 2 ? 2 : r <= 2.5 ? 2.5 : r <= 5 ? 5 : 10) * e; }
  function range(a, pad) { var lo = Math.min.apply(null, a), hi = Math.max.apply(null, a), p = (hi - lo || Math.abs(hi) || 1) * (pad || 0.08); return [lo >= 0 ? Math.max(0, lo - p) : lo - p, hi + p]; }
  function tipOn(node, text) {
    node.addEventListener("mousemove", function (e) { var t = $("tip"); t.style.display = "block"; t.style.left = e.clientX + 12 + "px"; t.style.top = e.clientY + 12 + "px"; t.textContent = text; });
    node.addEventListener("mouseleave", function () { $("tip").style.display = "none"; });
  }

  // ---------- 1 exit-speed fit
  function shotLog() { return loadJSON(A.LOG_KEY, []); }
  function drawLog() {
    var log = shotLog(), usable = log.filter(function (s) { return s.wheel_rpm > 0 && s.v > 0; });
    var o = $("log-o"), svg = $("vu-chart");
    if (usable.length < 2) {
      ST.fit = null; $("vu-use").disabled = true; svg.innerHTML = "";
      o.innerHTML = log.length + " shot(s) in the log, " + usable.length + " with a wheel rpm. Log at least two shots with a wheel rpm on the Measure page (Results → Add to the Shot Lab log), import a log, or load the demo data.";
      return;
    }
    var tr = C.transferFit(usable.map(function (s) { return { rpm: s.wheel_rpm, v: s.v }; }));
    ST.fit = tr; $("vu-use").disabled = !(tr.vu.k > 0);
    var demo = usable.some(function (s) { return /demo/.test(s.source || ""); });
    o.innerHTML = '<span class="big">v/u = ' + f(tr.vu.k, 3) + " ± " + f(tr.vu.seK, 3) + "</span> " + lab("derived") + "<br>" + usable.length + " shots, line fit v = " + f(tr.lin.a, 3) + "·u " + (tr.lin.b < 0 ? "− " : "+ ") + f(Math.abs(tr.lin.b), 2) + " m/s (r² " + f(tr.lin.r2, 3) + "). ±: 1 standard error." + (demo ? " <b>Demo log: synthetic shots, not measurements.</b>" : "");
    var us = usable.map(function (s) { return Math.PI * A.WHEEL_D * s.wheel_rpm / 60; }), vs = usable.map(function (s) { return s.v; });
    var W = 560, H = 230, ax = axes(svg, W, H, { l: 48, r: 12, t: 10, b: 34 }, range(us.concat([0])), range(vs.concat([0])), "wheel surface speed u (m/s)", "exit speed v (m/s)", 5, 4);
    var xr = range(us.concat([0]));
    el("line", { x1: ax.X(Math.max(0, xr[0])), y1: ax.Y(tr.vu.k * Math.max(0, xr[0])), x2: ax.X(xr[1]), y2: ax.Y(tr.vu.k * xr[1]), stroke: "var(--cal)", "stroke-width": 2 }, svg);
    usable.forEach(function (s, i) { tipOn(el("circle", { cx: ax.X(us[i]), cy: ax.Y(vs[i]), r: 4.5, fill: "var(--pollen)" }, svg), "shot " + (s.shot || "?") + ": " + s.wheel_rpm + " rpm, v " + f(s.v, 2) + " m/s" + (s.volts ? ", " + s.volts + " V" : "")); });
  }
  function demoLog() {
    var s = 7, rnd = function () { s = (s * 1103515245 + 12345) & 0x7fffffff; return s / 0x7fffffff - 0.5; }, out = [];
    [2800, 3100, 3400, 3700, 4000, 4300].forEach(function (r, i) {
      out.push({ id: i + 1, shot: "demo" + (i + 1), kind: "A", v: +(0.405 * Math.PI * 0.098 * r / 60 * (1 + 0.03 * rnd())).toFixed(3), theta: 55, wheel_rpm: r, volts: 12.4, power: null, hood: null, cd: null, source: "demo (synthetic)", label: "derived" });
    });
    return out;
  }
  function importLog(text) {
    var t = text.trim(), rows = [];
    if (t[0] === "[") rows = JSON.parse(t);
    else {
      var p = A.parseTelemetry(t), cols = p.cols.map(function (c) { return c.toLowerCase(); });
      var iv = cols.findIndex(function (c) { return /^v(_|$)|exit|speed_m/.test(c); }), ir = cols.findIndex(function (c) { return /rpm/.test(c); });
      if (iv < 0 || ir < 0) throw new Error("need columns named like v (m/s) and wheel_rpm");
      rows = p.rows.map(function (r, i) { return { id: i + 1, shot: "csv" + (i + 1), v: r[iv], wheel_rpm: r[ir], source: "import", label: "user" }; });
    }
    return rows.filter(function (r) { return r && isFinite(r.v) && isFinite(r.wheel_rpm); });
  }

  // ---------- 2 battery sag
  function telRows() { var t = loadJSON(A.TEL_KEY, null); return t && t.rows ? t.rows : null; }
  function drawSag() {
    var rows = ST.tel || telRows(), o = $("tel-o");
    $("sag-java").hidden = $("sag-copy").hidden = true; $("sag-tbl").innerHTML = "";
    if (!rows || !rows.length) { ST.sag = null; o.textContent = "No robot log yet: send one from the Measure page (Robot telemetry → Send to the Shot Lab), import a CSV with time, wheel speed, battery volts and motor power columns, or load the demo data."; return; }
    if (!rows.some(function (r) { return isFinite(r.power) && r.power !== null; })) { ST.sag = null; o.textContent = rows.length + " rows, but no motor power column: the sag fit needs the commanded power (0 to 1) as well as volts and rpm."; return; }
    var fit = C.sagFit(rows.map(function (r) { return { t: r.t, rpm: r.rpm, volts: r.volts, power: r.power }; }));
    if (!(fit.n >= 10) || !isFinite(fit.a)) { ST.sag = null; o.textContent = "Only " + fit.n + " steady rows (rows with repeated time stamps are skipped): log a few seconds of the wheel held at speed."; return; }
    if (!(fit.a > 0)) { ST.sag = null; o.textContent = "The fit gives rpm falling as power·volts rises (a = " + f(fit.a, 1) + "): check the power and volts columns."; return; }
    ST.sag = fit;
    o.innerHTML = '<span class="big">rpm = ' + f(fit.a, 1) + "·(power·V) " + (fit.b < 0 ? "− " : "+ ") + f(Math.abs(fit.b), 0) + "</span> " + lab("derived") + "<br>" + fit.n + " steady rows of " + rows.length + ", a ± " + f(fit.seA, 1) + ", r² " + f(fit.r2, 4) + ".";
    var targets = ST.map ? ST.map.rows.filter(function (r) { return r.main; }).map(function (r) { return Math.round(r.main.rpm / 10) * 10; }) : [3000, 3500, 4000, 4500, 5000];
    targets = targets.filter(function (x, i) { return targets.indexOf(x) === i; }).slice(0, 9);
    var volts = [13.0, 12.5, 12.0, 11.5, 11.0];
    var h = "<table class='res'><tr><th>target rpm" + (ST.map ? " (map)" : "") + "</th>" + volts.map(function (v) { return "<th>power @ " + v.toFixed(1) + " V</th>"; }).join("") + "</tr>";
    targets.forEach(function (t) { h += "<tr><td>" + t + "</td>" + volts.map(function (v) { var c = C.compPower(t, v, fit); return "<td" + (c.clipped ? " style='color:var(--hit)'" : "") + ">" + f(c.power, 3) + (c.clipped ? " max" : "") + "</td>"; }).join("") + "</tr>"; });
    $("sag-tbl").innerHTML = h + "</table><div class='o'>Red “max”: the motor cannot hold that rpm at that voltage (power clipped to 1).</div>";
    $("sag-java").textContent = C.javaSag(fit); $("sag-java").hidden = $("sag-copy").hidden = false;
  }
  function importTel(text, units) {
    var p = A.parseTelemetry(text), roles = A.detectColumns(p.cols);
    if (roles.rpm < 0) throw new Error("no wheel-speed column found (name it like wheel_rpm or velocity)");
    var tel = A.buildTel(p, roles, units || { speed: $("tel-unit").value, tpr: num("tel-tpr") || 28, ratio: 1 });
    var rows = []; for (var i = 0; i < tel.t.length; i++) rows.push({ t: tel.t[i], rpm: tel.rpm[i], volts: tel.volts ? tel.volts[i] : null, power: tel.power ? tel.power[i] : null, target: tel.target ? tel.target[i] : null });
    return rows;
  }

  // ---------- 3 rpm map
  function mapOpts() {
    var d0 = num("d0"), d1 = num("d1"), st = num("dst"), ds = [];
    if (!(st > 0) || !(d1 >= d0)) return null;
    for (var i = 0, n = Math.min(40, Math.round((d1 - d0) / st)); i <= n; i++) ds.push(+(d0 + i * st).toFixed(3));
    return { ds: ds, mode: $("map-mode").value, theta: num("map-th"), vLo: 3, vHi: 14, vStep: 0.02 };
  }
  function buildMap() {
    var o = mapOpts(); if (!o) { $("map-p").textContent = "check the d range"; return Promise.resolve(); }
    $("map-run").disabled = true; $("map-p").innerHTML = "<progress max='1' value='0'></progress>";
    var t0 = performance.now();
    return run("map", o, function (p) { var b = $("map-p").querySelector("progress"); if (b) b.value = p; }).then(function (res) {
      res.mode = o.mode; res.theta = o.theta; ST.map = res;
      $("map-p").textContent = "done in " + ((performance.now() - t0) / 1000).toFixed(1) + " s";
      drawMap(); drawSag(); drawDroop(); $("sm-run").disabled = $("sm-check").disabled = false; sotmCompute();
    }).catch(function (e) { $("map-p").textContent = "error: " + e.message; }).then(function () { $("map-run").disabled = false; });
  }
  function good() { return ST.map ? ST.map.rows.filter(function (r) { return r.ok && r.main && isFinite(r.main.tof); }) : []; }
  function drawMap() {
    var M = ST.map, rows = M.rows, fixed = M.mode === "fixed", S = +$("S").value;
    var h = "<table class='res'><tr><th>d (m)</th><th>v (m/s)</th><th>exit °</th><th>wheel rpm</th><th>time of flight (s)</th><th>" + (fixed ? "± v (m/s)" : "± v / ± °") + "</th><th>twin rpm / exit °</th></tr>";
    rows.forEach(function (r) {
      if (!r.ok) { h += "<tr class='bad'><td>" + f(r.d, 2) + "</td><td colspan='6'>robot does not fit here (" + esc(r.status) + ")</td></tr>"; return; }
      if (!r.main) { h += "<tr class='bad'><td>" + f(r.d, 2) + "</td><td colspan='5'>no clean shot" + (fixed ? " at " + f(M.theta, 1) + "°" : "") + "</td><td>" + (r.twin ? f(r.twin.rpm, 0) + " / " + f(r.twin.theta, 1) : "none") + "</td></tr>"; return; }
      var m = r.main;
      h += "<tr><td>" + f(r.d, 2) + "</td><td>" + f(m.v, 2) + "</td><td>" + f(m.theta, 1) + "</td><td>" + f(m.rpm, 0) + "</td><td>" + f(m.tof, 3) + "</td><td>" + (fixed ? f(m.tol, 2) : f(m.tol, 2) + " / " + f(m.tolTheta, 2)) + "</td><td>" + (S === 0 ? "same (S = 0)" : r.twin ? f(r.twin.rpm, 0) + " / " + f(r.twin.theta, 1) : "no clean twin") + "</td></tr>";
    });
    $("map-tbl").innerHTML = h + "</table>";
    var g = good(), svg = $("map-chart");
    if (g.length < 2) { svg.innerHTML = ""; $("map-fit").textContent = "Fewer than two clean distances: widen the d range" + (fixed ? " or try another exit angle." : "."); $("map-java").hidden = $("map-copy").hidden = true; return; }
    var ds = g.map(function (r) { return r.d; }), rp = g.map(function (r) { return r.main.rpm; });
    var tw = rows.filter(function (r) { return r.ok && r.twin; });
    var deg = Math.min(2, g.length - 1), cf = C.polyfit(ds, rp, deg);
    if (!cf.every(isFinite)) cf = C.polyfit(ds, rp, deg = 1);
    var res = g.map(function (r, i) { return r.main.rpm - C.polyval(cf, ds[i]); }), rmse = Math.sqrt(res.reduce(function (a, b) { return a + b * b; }, 0) / res.length);
    $("map-fit").innerHTML = "Fit: rpm ≈ " + cf.map(function (c, i) { return f(c, i ? 1 : 0) + (i ? "·d" + (i > 1 ? "²" : "") : ""); }).join(" + ").replace(/\+ -/g, "− ") + " (rms " + f(rmse, 0) + " rpm over " + g.length + " points) " + lab("PREDICTED");
    var all = rp.concat(tw.map(function (r) { return r.twin.rpm; }));
    var ax = axes(svg, 560, 250, { l: 52, r: 12, t: 10, b: 34 }, range(ds.concat(tw.map(function (r) { return r.d; })), 0.04), range(all), "d (m)", "wheel rpm", 5, 4);
    var line = function (pts, attrs) { if (pts.length < 2) return; el("polyline", Object.assign({ points: pts.map(function (p) { return ax.X(p[0]) + "," + ax.Y(p[1]); }).join(" "), fill: "none" }, attrs), svg); };
    var fx = []; for (var i = 0; i <= 40; i++) { var x = ds[0] + (ds[ds.length - 1] - ds[0]) * i / 40; fx.push([x, C.polyval(cf, x)]); }
    line(fx, { stroke: "var(--cal)", "stroke-width": 1.5 });
    if (S !== 0) line(tw.map(function (r) { return [r.d, r.twin.rpm]; }), { stroke: "var(--twin)", "stroke-width": 2, "stroke-dasharray": "5 4" });
    line(g.map(function (r) { return [r.d, r.main.rpm]; }), { stroke: "var(--pollen)", "stroke-width": 2 });
    g.forEach(function (r) { tipOn(el("circle", { cx: ax.X(r.d), cy: ax.Y(r.main.rpm), r: 4, fill: "var(--pollen)" }, svg), "d " + r.d + " m: " + f(r.main.rpm, 0) + " rpm, " + f(r.main.theta, 1) + "°, tof " + f(r.main.tof, 2) + " s (PREDICTED)"); });
    var cols = { rpm: rp, exit_deg: g.map(function (r) { return r.main.theta; }), tof: g.map(function (r) { return r.main.tof; }) };
    $("map-java").textContent = C.javaTable("ShotTable", ds, cols).replace("// Generated by the POLLEN shot lab.", "// Generated by the POLLEN Shot Lab: S " + $("S").value + ", h " + $("h").value + " m, v/u " + query().vu + ", " + (fixed ? "fixed exit " + M.theta + " deg" : "most forgiving") + ". X = d (m).") +
      "// EXIT_DEG is the ball exit angle, not a servo position: map it to your hood with your own measurement.\n";
    $("map-java").hidden = $("map-copy").hidden = false;
  }

  // ---------- droop
  function drawDroop() {
    var g = good(); if (!g.length) { $("droop-tbl").innerHTML = "<div class='o'>Build the map first.</div>"; return; }
    var V = num("volts") || 12, S = +$("S").value;
    var h = "<table class='res'><tr><th>d (m)</th><th>wheel rpm</th><th>drop (rpm)</th><th>drop %</th><th>recover (s)</th></tr>";
    g.forEach(function (r) {
      var dr = PS.droopReadout(r.main.rpm, r.main.v, S, { volts: V });
      h += "<tr><td>" + f(r.d, 2) + "</td><td>" + f(r.main.rpm, 0) + "</td><td>" + f(dr.dropRpm, 0) + "</td><td>" + f(dr.dropPct, 1) + "</td><td>" + (isFinite(dr.recoverS) ? f(dr.recoverS, 2) : "never (above free speed at " + V + " V)") + "</td></tr>";
    });
    $("droop-tbl").innerHTML = h + "</table><div class='o'>PREDICTED at " + V.toFixed(1) + " V " + lab("user") + ". Compare the drop with the dips your robot log shows on the Measure page.</div>";
  }

  // ---------- 4 shoot on the move
  function tofAt(d) { var g = good(); return C.interp1(g.map(function (r) { return r.d; }), g.map(function (r) { return r.main.tof; }), d); }
  function setAt(d) {
    var g = good(), xs = g.map(function (r) { return r.d; });
    return { v: C.interp1(xs, g.map(function (r) { return r.main.v; }), d), theta: C.interp1(xs, g.map(function (r) { return r.main.theta; }), d) };
  }
  function sotmCompute() {
    var g = good(); if (g.length < 2) { $("sm-o").textContent = "Build a map with at least two clean distances first."; return null; }
    var d = num("sm-d"), along = num("sm-a") || 0, across = num("sm-c") || 0, lat = num("sm-l") || 0, c = g[0].Lh - g[0].d;
    // shot frame: x toward the aim point (Lh ahead), y to the left; the map is indexed by d = Lh - c
    var Lh = d + c, r = C.sotm({ target: [Lh, 0], pos: [0, 0], vel: [along, across], lat: lat, tof: function (dist) { return tofAt(dist - c); } });
    var dv = r.dist - c, lo = g[0].d, hi = g[g.length - 1].d, out = dv < lo || dv > hi;
    var comp = setAt(dv), plain = setAt(d);
    ST.sotm = { d: d, along: along, across: across, comp: comp, plain: plain };
    $("sm-o").innerHTML = "Virtual distance <span class='big'>" + f(dv, 3) + " m</span> " + lab("PREDICTED") + (out ? " <b style='color:var(--hit)'>outside the map (" + lo + "–" + hi + " m): values clamped</b>" : "") +
      "<br>turn " + f(r.heading * 180 / Math.PI, 1) + "° (positive = left), time of flight " + f(r.tof, 3) + " s, " + r.iters + " iterations" + (r.converged ? "" : " (not converged)") +
      "<br>shoot: " + f(PS.rpm(comp.v, query().vu), 0) + " rpm, exit " + f(comp.theta, 1) + "° (standing still at " + d + " m: " + f(PS.rpm(plain.v, query().vu), 0) + " rpm, " + f(plain.theta, 1) + "°)" +
      "<br>robot position predicted " + f(lat, 2) + " s ahead for latency " + lab("user");
    $("sm-java").textContent = C.javaSotm(); $("sm-java").hidden = false;
    return ST.sotm;
  }
  function sotmCheck() {
    var s = sotmCompute(); if (!s) return Promise.resolve();
    $("sm-check").disabled = true;
    return run("sotm", { d: s.d, along: s.along, across: s.across, comp: s.comp, plain: s.plain }).then(function (r) {
      var says = { clean: "clean (goes in, no rim touch)", hit: "touches the rim (counted as a miss)", miss: "misses the cell" };
      var name = function (x) { return says[x] || x; };
      var word = function (x) { return "<b style='color:var(--" + (x === "clean" ? "clean" : "hit") + ")'>" + name(x) + "</b>"; };
      $("sm-o").innerHTML += "<div class='twin'>3D model, robot moving (the solver turns the shooter so the ball's ground track points at the HIVE): " +
        "virtual-target setting " + word(r.comp.result) + ", standing-still setting " + word(r.plain.result) + " (standing still it is " + name(r.still) + "). " +
        "No-spin twin at the same settings: " + name(r.comp.twin) + " / " + name(r.plain.twin) + ". " + lab("PREDICTED") + " One shot each, no scatter.</div>";
    }).catch(function (e) { $("sm-o").innerHTML += "<div class='o'>error: " + esc(e.message) + "</div>"; }).then(function () { $("sm-check").disabled = false; });
  }

  // ---------- 5 near-lip hypothesis
  function runLip() {
    var o = { d: num("lip-d"), nearM: (num("lip-near") || 1) / 100, vHalf: 2.0, vStep: 0.05, thHalf: 6, thStep: 0.1, mcCells: 20, mcN: 400, mcN2: 1000 };
    $("lip-run").disabled = true; $("lip-p").innerHTML = "<progress max='1' value='0'></progress>";
    var t0 = performance.now();
    return run("lip", o, function (p) { var b = $("lip-p").querySelector("progress"); if (b) b.value = p; }).then(function (r) {
      ST.lip = r; $("lip-p").textContent = "done in " + ((performance.now() - t0) / 1000).toFixed(1) + " s"; drawLip(o);
    }).catch(function (e) { $("lip-p").textContent = "error: " + e.message; }).then(function () { $("lip-run").disabled = false; });
  }
  function rhoWord(rho) { var a = Math.abs(rho); return !isFinite(rho) ? "–" : a < 0.1 ? "none" : a < 0.3 ? "weak" : a < 0.5 ? "moderate" : "strong"; }
  function drawLip(o) {
    var r = ST.lip, svg = $("lip-chart");
    if (!r.ok) { svg.innerHTML = ""; $("lip-o").textContent = "No result: " + r.reason + "."; $("lip-picks").innerHTML = ""; $("lip-twin").hidden = true; return; }
    var nT = r.TH.length, pts = [];
    for (var c = 0; c < r.clean.length; c++) if (r.clean[c] && !r.edge[c]) pts.push({ x: r.clear[c] * 100, y: r.share[c] * 100, ke: r.keEntry[c], v: r.V[Math.floor(c / nT)], th: r.TH[c % nT] });
    var kes = pts.map(function (p) { return p.ke; }), k0 = Math.min.apply(null, kes), k1 = Math.max.apply(null, kes);
    var col = function (k) { var t = k1 > k0 ? (k - k0) / (k1 - k0) : 0.5, a = [61, 90, 128], b = [242, 201, 76]; return "rgb(" + a.map(function (x, i) { return Math.round(x + (b[i] - x) * t); }).join(",") + ")"; };
    var ax = axes(svg, 560, 300, { l: 52, r: 12, t: 10, b: 34 }, range(pts.map(function (p) { return p.x; }).concat([0]), 0.04), [0, 100], "closest approach to the lower lip before entry (cm)", "clean share under scatter (%)", 5, 5);
    el("rect", { x: ax.X(0), y: 10, width: Math.max(0, ax.X(o.nearM * 100) - ax.X(0)), height: 300 - 44, fill: "var(--level)", opacity: 0.12 }, svg);
    pts.forEach(function (p) { tipOn(el("circle", { cx: ax.X(p.x), cy: ax.Y(p.y), r: 3, fill: col(p.ke), opacity: 0.9 }, svg), "v " + f(p.v, 2) + " m/s, " + f(p.th, 1) + "°: lip " + f(p.x, 1) + " cm, share " + f(p.y, 0) + " %, KE " + f(p.ke, 2) + " J"); });
    var ring = function (p, colr) { if (p) el("circle", { cx: ax.X(p.clear * 100), cy: ax.Y(p.share * 100), r: 8, fill: "none", stroke: colr, "stroke-width": 2.5 }, svg); };
    ring(r.rule, "var(--hit)"); ring(r.robust, "var(--clean)");
    var pc = function (h) { return f(100 * h.p, 0) + " % (" + f(100 * h.lo, 0) + "–" + f(100 * h.hi, 0) + ")"; };
    $("lip-o").innerHTML = "d " + r.d + " m: " + r.nClean + " clean settings in the scan (" + r.nEdge + " too close to the scan edge left out), " + r.nNear + " pass within " + f(o.nearM * 100, 1) + " cm of the lower lip. " + lab("PREDICTED") +
      "<br>Rank correlation with robustness (Spearman ρ): lip clearance " + f(r.rhoClear.rho, 2) + " (" + rhoWord(r.rhoClear.rho) + ", n " + r.rhoClear.n + "), entry energy " + f(r.rhoKE.rho, 2) + " (" + rhoWord(r.rhoKE.rho) + ")" +
      "; 3D Monte Carlo on " + r.rhoMC.n + " shots across the clearance range: clearance ρ " + f(r.rhoMC.rho, 2) + " (" + rhoWord(r.rhoMC.rho) + ")." +
      "<br><b>" + verdict(r) + "</b>";
    var card = function (title, p, colr) {
      if (!p) return "<div><h4>" + title + "</h4><div class='o'>no clean shot qualifies</div></div>";
      return "<div style='border-color:" + colr + "'><h4>" + title + "</h4><div class='o'>" + f(p.rpm, 0) + " rpm (v " + f(p.v, 2) + " m/s), exit " + f(p.theta, 1) + "°<br>lip clearance " + f(p.clear * 100, 1) + " cm, entry energy " + f(p.keEntry, 2) + " J<br>clean share " + f(100 * p.share, 0) + " %<br>3D hit chance " + pc(p.hc) + ", n " + p.hc.n + "</div></div>";
    };
    $("lip-picks").innerHTML = card("Your rule: most energy within " + f(o.nearM * 100, 1) + " cm of the lip", r.rule, "var(--hit)") + card("Most forgiving setting in the scan", r.robust, "var(--clean)");
    var tw = (r.rule && r.rule.twin) || (r.robust && r.robust.twin);
    $("lip-twin").hidden = !tw;
    if (tw) $("lip-twin").innerHTML = "<b>No-spin twin</b> (no backspin, its own most forgiving setting " + f(tw.rpm, 0) + " rpm, " + f(tw.theta, 1) + "°): 3D hit chance " + pc(tw) + "; " + r.nTwinClean + " clean twin settings in the same scan. " + lab("PREDICTED");
  }
  function verdict(r) {
    if (!r.rule || !r.robust) return "Too few shots near the lip to compare.";
    var a = r.rule.hc, b = r.robust.hc, worse = a.hi < b.lo, same = !(a.hi < b.lo) && !(b.hi < a.lo);
    var rc = r.rhoClear.rho;
    var s = "In this local scan (one pose, ASSUMED scatter), lip clearance shows " + (Math.abs(rc) < 0.1 ? "no relation with" : rc > 0 ? "a positive relation with" : "a negative relation with") + " robustness";
    s += worse ? ", and your rule's pick is less forgiving than the most forgiving setting (the 95 % intervals do not overlap)." : same ? "; the two picks' intervals overlap, so this scan cannot separate them." : ", and your rule's pick is more forgiving here.";
    return s + " This tests only the model's flight and cell edges, not a real lip contact.";
  }

  // ---------- setup
  function fillCases() {
    var Ss = Array.from(new Set(ST.FI.cases.map(function (c) { return c.S; }))).sort(function (a, b) { return a - b; });
    $("S").innerHTML = Ss.map(function (s) { return "<option value='" + s + "'" + (s === 1 ? " selected" : "") + ">" + s + (s === 0 ? " (no spin)" : "") + "</option>"; }).join("");
    fillAero();
  }
  function fillAero() {
    var S = +$("S").value, keep = $("aero").value;
    var vs = ST.FI.cases.filter(function (c) { return c.S === S; }).map(function (c) { return c.var; });
    $("aero").innerHTML = vs.map(function (v) { return "<option value='" + v + "'>" + (AERO[v] || v) + "</option>"; }).join("");
    if (vs.indexOf(keep) >= 0) $("aero").value = keep;
  }
  function readFile(input, fn) {
    var file = input.files && input.files[0]; if (!file) return;
    var rd = new FileReader(); rd.onload = function () { try { fn(String(rd.result)); } catch (e) { fileError(input, e.message); } }; rd.readAsText(file);
  }
  function fileError(input, msg) { var o = input.id === "log-file" ? $("log-o") : $("tel-o"); o.textContent = "Could not read that file: " + msg; }
  function stale() { if (ST.map) { $("map-p").textContent = "settings changed: build the map again"; } }

  function init() {
    $("vu").addEventListener("change", function () { stale(); });
    ["h", "S", "aero"].forEach(function (id) { $(id).addEventListener("change", function () { if (id === "S") fillAero(); stale(); }); });
    $("volts").addEventListener("change", drawDroop);
    $("log-file").addEventListener("change", function () { readFile($("log-file"), function (t) { var rows = importLog(t); saveJSON(A.LOG_KEY, shotLog().concat(rows)); drawLog(); }); });
    $("log-clear").onclick = function () { saveJSON(A.LOG_KEY, []); drawLog(); };
    $("vu-use").onclick = function () { if (ST.fit) { $("vu").value = ST.fit.vu.k.toFixed(3); stale(); $("setup-note").dataset.vu = "derived"; } };
    $("tel-file").addEventListener("change", function () { readFile($("tel-file"), function (t) { ST.tel = importTel(t); drawSag(); }); });
    $("sag-copy").onclick = function () { navigator.clipboard && navigator.clipboard.writeText($("sag-java").textContent); };
    $("map-copy").onclick = function () { navigator.clipboard && navigator.clipboard.writeText($("map-java").textContent); };
    $("map-run").onclick = buildMap;
    $("sm-run").onclick = sotmCompute;
    $("sm-check").onclick = sotmCheck;
    $("lip-run").onclick = runLip;
    $("demo").onclick = function () {
      saveJSON(A.LOG_KEY, demoLog());
      ST.tel = importTel(A.demoTelemetry(), { speed: "rpm", ratio: 1 });
      drawLog(); drawSag();
    };
    drawLog(); drawSag();
    fetch(FIELD_URL).then(function (r) { if (!r.ok) throw new Error(FIELD_URL + " " + r.status); return r.json(); }).then(function (FI) {
      ST.FI = FI;
      ST.meta = { grid: FI.grid, sections: FI.sections, frame: FI.frame, field_grid: FI.field_grid, cases: FI.cases.map(function (c) { return { S: c.S, var: c.var, params: c.params }; }) };
      fillCases(); $("fi-o").textContent = "field model loaded (" + FI.cases.length + " aero cases)";
      if (/demo/.test(location.hash)) {
        $("demo").onclick();
        if (ST.fit) { $("vu").value = ST.fit.vu.k.toFixed(3); }
        buildMap().then(function () { if (/lip/.test(location.hash)) return runLip(); }).then(function () { if (/move/.test(location.hash)) return sotmCheck(); });
      }
    }).catch(function (e) { $("fi-o").textContent = "Could not load the field model (" + e.message + "): the map, shoot-on-the-move and lip cards need it."; ["map-run", "lip-run"].forEach(function (id) { $(id).disabled = true; }); });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
