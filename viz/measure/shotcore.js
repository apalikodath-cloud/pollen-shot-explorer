(function (root, factory) {
  "use strict";
  if (typeof module !== "undefined" && module.exports) module.exports = factory();
  else root.PollenShotCore = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  var WHEEL_D = 0.098;
  function finite(v) { return typeof v === "number" && isFinite(v); }
  function pairs(xs, ys) {
    var out = [];
    for (var i = 0; i < Math.min(xs.length, ys.length); i++) if (finite(xs[i]) && finite(ys[i])) out.push([xs[i], ys[i]]);
    return out;
  }
  function linfit(xs, ys) {
    var p = pairs(xs, ys), n = p.length, sx = 0, sy = 0;
    for (var i = 0; i < n; i++) { sx += p[i][0]; sy += p[i][1]; }
    var mx = sx / n, my = sy / n, sxx = 0, sxy = 0, syy = 0;
    for (i = 0; i < n; i++) { var dx = p[i][0] - mx, dy = p[i][1] - my; sxx += dx * dx; sxy += dx * dy; syy += dy * dy; }
    var a = sxy / sxx, b = my - a * mx, sse = 0;
    for (i = 0; i < n; i++) { var e = p[i][1] - (a * p[i][0] + b); sse += e * e; }
    var s2 = n > 2 ? sse / (n - 2) : NaN;
    return { a: a, b: b, seA: n > 2 ? Math.sqrt(s2 / sxx) : NaN, seB: n > 2 ? Math.sqrt(s2 * (1 / n + mx * mx / sxx)) : NaN,
      r2: syy ? 1 - sse / syy : (sse === 0 ? 1 : NaN), n: n, rmse: Math.sqrt(sse / n) };
  }
  function propfit(xs, ys) {
    var p = pairs(xs, ys), n = p.length, xx = 0, xy = 0;
    for (var i = 0; i < n; i++) { xx += p[i][0] * p[i][0]; xy += p[i][0] * p[i][1]; }
    var k = xy / xx, sse = 0;
    for (i = 0; i < n; i++) { var e = p[i][1] - k * p[i][0]; sse += e * e; }
    return { k: k, seK: n > 1 ? Math.sqrt((sse / (n - 1)) / xx) : NaN, n: n, rmse: Math.sqrt(sse / n) };
  }
  function transferFit(shots) {
    var u = [], v = [];
    shots.forEach(function (s) { if (s && finite(s.rpm) && finite(s.v) && s.rpm > 0 && s.v > 0) { u.push(Math.PI * WHEEL_D * s.rpm / 60); v.push(s.v); } });
    var q = propfit(u, v), l = linfit(u, v);
    return { vu: { k: q.k, seK: q.seK }, lin: l, n: u.length };
  }
  function sagFit(rows, opts) {
    opts = opts || {}; var maxSlope = opts.maxSlope === undefined ? 400 : opts.maxSlope;
    var order = rows.map(function (r, i) { return { r: r, i: i }; }).filter(function (x) { return finite(x.r.t); }).sort(function (a, b) { return a.r.t - b.r.t; });
    var xs = [], ys = [], used = [];
    order.forEach(function (x, j) {
      var r = x.r, slope = 0;
      if (order.length > 1) {
        var lo = order[Math.max(0, j - 1)].r, hi = order[Math.min(order.length - 1, j + 1)].r;
        slope = (hi.rpm - lo.rpm) / (hi.t - lo.t);
      }
      if (finite(r.rpm) && finite(r.volts) && finite(r.power) && finite(slope) && Math.abs(slope) <= maxSlope && r.power > 0.05) { xs.push(r.power * r.volts); ys.push(r.rpm); used.push(x.i); }
    });
    var f = linfit(xs, ys);
    return { a: f.a, b: f.b, seA: f.seA, r2: f.r2, n: f.n, used: used };
  }
  function compPower(target, volts, fit) {
    if (!(fit.a > 0) || !(volts > 0)) return { power: NaN, clipped: true };   // no usable fit: say so, never a fake number
    var power = (target - fit.b) / (fit.a * volts), clipped = power > 1 || power < 0;
    return { power: Math.max(0, Math.min(1, power)), clipped: clipped };
  }
  function interp1(xs, ys, x) {
    var p = []; for (var i = 0; i < Math.min(xs.length, ys.length); i++) if (finite(xs[i]) && finite(ys[i])) p.push([xs[i], ys[i]]);
    if (!p.length) return NaN;
    if (x <= p[0][0]) return p[0][1]; if (x >= p[p.length - 1][0]) return p[p.length - 1][1];
    for (i = 1; i < p.length; i++) if (x <= p[i][0]) { var t = (x - p[i - 1][0]) / (p[i][0] - p[i - 1][0]); return p[i - 1][1] + t * (p[i][1] - p[i - 1][1]); }
    return p[p.length - 1][1];
  }
  function polyfit(xs, ys, deg) {
    var p = pairs(xs, ys), n = deg + 1, a = [], i, j, k;
    for (i = 0; i < n; i++) { a[i] = []; for (j = 0; j <= n; j++) { var sum = 0; for (k = 0; k < p.length; k++) sum += j === n ? Math.pow(p[k][0], i) * p[k][1] : Math.pow(p[k][0], i + j); a[i][j] = sum; } }
    for (i = 0; i < n; i++) { var pivot = i; for (j = i + 1; j < n; j++) if (Math.abs(a[j][i]) > Math.abs(a[pivot][i])) pivot = j; if (Math.abs(a[pivot][i]) < 1e-14) return a.map(function () { return NaN; }); var row = a[i]; a[i] = a[pivot]; a[pivot] = row; for (j = i + 1; j < n; j++) { var q = a[j][i] / a[i][i]; for (k = i; k <= n; k++) a[j][k] -= q * a[i][k]; } }
    var c = new Array(n); for (i = n - 1; i >= 0; i--) { var z = a[i][n]; for (j = i + 1; j < n; j++) z -= a[i][j] * c[j]; c[i] = z / a[i][i]; } return c;
  }
  function polyval(c, x) { var y = 0; for (var i = c.length - 1; i >= 0; i--) y = y * x + c[i]; return y; }
  function sotm(o) {
    var target = o.target, pos = o.pos, vel = o.vel, lat = o.lat === undefined ? 0 : o.lat, max = o.iters === undefined ? 12 : o.iters, tol = o.tol === undefined ? 1e-4 : o.tol;
    var pp = [pos[0] + vel[0] * lat, pos[1] + vel[1] * lat], virt = [target[0], target[1]], converged = false, count = 0;
    for (; count < max; count++) { var d = Math.hypot(virt[0] - pp[0], virt[1] - pp[1]), tof = o.tof(d), next = [target[0] - vel[0] * tof, target[1] - vel[1] * tof]; if (Math.hypot(next[0] - virt[0], next[1] - virt[1]) < tol) { virt = next; converged = true; count++; break; } virt = next; }
    var dist = Math.hypot(virt[0] - pp[0], virt[1] - pp[1]); return { virt: virt, dist: dist, tof: o.tof(dist), heading: Math.atan2(virt[1] - pp[1], virt[0] - pp[0]), iters: count, converged: converged };
  }
  function segDist(px, py, ax, ay, bx, by) { var dx = bx - ax, dy = by - ay, q = dx * dx + dy * dy, t = q ? ((px - ax) * dx + (py - ay) * dy) / q : 0; t = Math.max(0, Math.min(1, t)); return Math.hypot(px - (ax + t * dx), py - (ay + t * dy)); }
  function lipClearance(path, seg, R, upto) { var n = Math.min(path.x.length, path.z.length, upto === undefined ? Infinity : upto + 1), best = Infinity; for (var i = 0; i < n; i++) best = Math.min(best, segDist(path.x[i], path.z[i], seg[0][0], seg[0][1], seg[1][0], seg[1][1]) - R); return best; }
  function entryKE(m, vx, vz) { return 0.5 * m * (vx * vx + vz * vz); }
  function robustness(results) { var n = results.length, yes = results.filter(Boolean).length, p = yes / n, z = 1.96, d = 1 + z * z / n, c = (p + z * z / (2 * n)) / d, h = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d; return { p: p, n: n, lo: c - h, hi: c + h }; }
  // up to 6 significant digits; trailing zeros only trimmed after a decimal point (100000 stays 100000)
  function fmt(x) {
    var s = Number(x).toPrecision(6), m = s.split('e');
    if (m[0].indexOf('.') >= 0) m[0] = m[0].replace(/0+$/, '').replace(/\.$/, '');
    return m.join('e');
  }
  function javaTable(name, xs, cols) { var s = '// Generated by the POLLEN shot lab. Values are MODEL PREDICTIONS unless you measured them.\npublic final class ' + name + ' {\n  static final double[] X = {' + xs.map(fmt).join(', ') + '};\n'; Object.keys(cols).forEach(function (k) { s += '  static final double[] ' + k.toUpperCase().replace(/[^A-Z0-9]+/g, '_') + ' = {' + cols[k].map(fmt).join(', ') + '};\n'; }); return s + '  static double lookup(double[] ys, double x) { if (x <= X[0]) return ys[0]; if (x >= X[X.length - 1]) return ys[ys.length - 1]; for (int i = 1; i < X.length; i++) if (x <= X[i]) { double t = (x - X[i - 1]) / (X[i] - X[i - 1]); return ys[i - 1] + t * (ys[i] - ys[i - 1]); } return ys[ys.length - 1]; }\n}\n'; }
  function javaSag(fit) { return '// Fitted from your telemetry: rpm = a*(power*volts) + b\nstatic double compPower(double targetRpm, double volts) { if (volts <= 0.0) return 0.0; double power = (targetRpm - ' + fmt(fit.b) + ') / (' + fmt(fit.a) + ' * volts); return Math.max(0.0, Math.min(1.0, power)); }\n'; }
  function javaSotm() { return '// Shoot-on-the-move virtual target.\n// Supply tofAt(dist), for example ShotTable.lookup(ShotTable.TOF, dist).\nstatic double tofAt(double dist) { return ShotTable.lookup(ShotTable.TOF, dist); }\nstatic double[] virtualTarget(double tx, double ty, double px, double py, double vx, double vy, double lat) { double ax = px + vx * lat, ay = py + vy * lat, x = tx, y = ty; for (int i = 0; i < 12; i++) { double d = Math.hypot(x - ax, y - ay), t = tofAt(d), nx = tx - vx * t, ny = ty - vy * t; if (Math.hypot(nx - x, ny - y) < 1e-4) { x = nx; y = ny; break; } x = nx; y = ny; } return new double[] {x, y}; }\n'; }
  return { linfit: linfit, propfit: propfit, transferFit: transferFit, sagFit: sagFit, compPower: compPower, interp1: interp1, polyfit: polyfit, polyval: polyval, sotm: sotm, segDist: segDist, lipClearance: lipClearance, entryKE: entryKE, robustness: robustness, javaTable: javaTable, javaSag: javaSag, javaSotm: javaSotm };
});
