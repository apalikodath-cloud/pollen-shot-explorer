#!/usr/bin/env python3
"""Turn a solver snapshot into a compact web bundle for flow.html.

  python make_flow.py <snapshot.json> [--fine <solid_fine.json>] -o <outdir> [--label "..."]

Writes streamlines.bin, vortex.bin, body.bin, slices.bin, slice_*.png and manifest.json.
All binaries are little-endian typed arrays described by manifest.json (name, dtype,
offset in bytes, length in elements). Lengths are in units of the body diameter D, with
the origin at the body centre.
"""
import argparse, glob, json, os, re, sys, time
import numpy as np
from scipy import ndimage as ndi
from skimage import measure
from PIL import Image
import matplotlib
matplotlib.use('Agg')
from matplotlib import colormaps

PRED = 'PREDICTED (CFD model output, not a measurement)'
SYN = 'SYNTHETIC TEST FIELD - not CFD'


# ---------------------------------------------------------------- io
def load_blocks(meta_path):
    meta = json.load(open(meta_path))
    binp = os.path.splitext(meta_path)[0] + '.bin'
    shape = (meta['nz'], meta['ny'], meta['nx'])
    out = {}
    for b in meta['blocks']:
        out[b['name']] = np.memmap(binp, dtype=np.dtype(b['dtype']), mode='r', offset=b['offset'],
                                   shape=shape)
    return meta, out


class Writer:
    """Collects typed arrays into one file and records their offsets."""
    def __init__(self, path):
        self.path, self.f, self.pos, self.arrays = path, open(path, 'wb'), 0, []

    def add(self, name, arr):
        arr = np.ascontiguousarray(arr)
        pad = (-self.pos) % 4
        self.f.write(b'\0' * pad)
        self.pos += pad
        self.arrays.append({'name': name, 'dtype': arr.dtype.name, 'offset': self.pos, 'length': int(arr.size)})
        b = arr.tobytes()
        self.f.write(b)
        self.pos += len(b)

    def close(self):
        self.f.close()
        return {'url': os.path.basename(self.path), 'bytes': self.pos, 'arrays': self.arrays}


def quant(p, lo, hi):
    return np.clip(np.round((p - lo) / (hi - lo) * 65535), 0, 65535).astype(np.uint16)


# ---------------------------------------------------------------- field
class Field:
    def __init__(self, meta, blk):
        self.meta = meta
        self.dx = meta['dx_D']
        self.org = np.array(meta['origin_D'], float)
        self.shape = (meta['nz'], meta['ny'], meta['nx'])
        self.u = [np.nan_to_num(np.array(blk[k], dtype=np.float32), nan=0.0, posinf=0.0, neginf=0.0) for k in ('ux', 'uy', 'uz')]
        self.solid = np.asarray(blk['solid']) > 0
        for c in self.u:
            c[self.solid] = 0
        self.speed = np.sqrt(sum(c * c for c in self.u))
        self.hi = self.org + self.dx * (np.array(self.shape[::-1]) - 1)

    def idx(self, p):  # world (x,y,z) -> array coords (k,j,i), shape (3,N)
        g = (p - self.org) / self.dx
        return np.stack([g[:, 2], g[:, 1], g[:, 0]])

    def vel(self, p):
        c = self.idx(p)
        return np.stack([ndi.map_coordinates(a, c, order=1, mode='nearest') for a in self.u], 1)

    def inside(self, p):
        return np.all((p >= self.org + 1.5 * self.dx) & (p <= self.hi - 1.5 * self.dx), 1)

    def is_solid(self, p):
        c = np.round(self.idx(p)).astype(int)
        c = np.clip(c, 0, np.array(self.shape)[:, None] - 1)
        return self.solid[c[0], c[1], c[2]]


def integrate(F, seeds, sign, ds, nmax, vmin):
    """Advance all seeds together with RK4 on unit-speed arclength."""
    n = len(seeds)
    P = np.zeros((nmax + 1, n, 3), np.float32)
    S = np.zeros((nmax + 1, n), np.float32)
    alive = np.ones(n, bool)
    cnt = np.zeros(n, int)
    p = seeds.astype(np.float64).copy()
    alive &= F.inside(p) & ~F.is_solid(p)

    def f(q):
        v = F.vel(q) * sign
        s = np.linalg.norm(v, axis=1)
        return v / np.maximum(s, 1e-9)[:, None], s

    for it in range(nmax + 1):
        k1, s1 = f(p)
        P[it, alive] = p[alive]
        S[it, alive] = s1[alive]
        cnt[alive] += 1
        alive &= s1 > vmin
        if not alive.any() or it == nmax:
            break
        k2, _ = f(p + 0.5 * ds * k1)
        k3, _ = f(p + 0.5 * ds * k2)
        k4, _ = f(p + ds * k3)
        p = p + ds / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        alive &= F.inside(p) & ~F.is_solid(p)
    return [(P[:cnt[i], i], S[:cnt[i], i]) for i in range(n)]


def make_seeds(F, rng, n_up, n_wake, n_hole, x_up=None):
    if x_up is None:  # just inside the upstream face of the box, at most 1.2 D upstream of the body
        x_up = max(F.org[0] + 0.15, -1.2)
    half = min(abs(F.org[1]), F.hi[1], abs(F.org[2]), F.hi[2]) - 0.05
    rmax = min(0.8, half)
    k = np.arange(n_up) + 0.5
    r = 0.2 + (rmax - 0.2) * (k / n_up) ** 0.8  # rings that wrap the body (r 0.2 .. box edge)
    th = k * np.pi * (3 - np.sqrt(5))
    up = np.stack([np.full(n_up, x_up), r * np.cos(th), r * np.sin(th)], 1)
    wake = np.stack([rng.uniform(0.45, min(1.2, F.hi[0] - 0.2), n_wake),
                     rng.normal(0, 0.22, n_wake), rng.normal(0, 0.22, n_wake)], 1)
    hole = np.stack([rng.uniform(-0.45, 0.45, n_hole), rng.normal(0, 0.06, n_hole),
                     rng.normal(0, 0.06, n_hole)], 1)
    both = np.concatenate([wake, hole, hole[:n_hole // 2, [1, 0, 2]], hole[:n_hole // 2, [1, 2, 0]]])
    return up, both


def streamlines(F, args, rng):
    ds = F.dx
    nmax = int(round((F.hi[0] - F.org[0]) * 1.6 / ds))
    up, both = make_seeds(F, rng, args.n_up, args.n_wake, args.n_hole)
    ok = lambda s: ~F.is_solid(s) & F.inside(s)
    n0, m0 = len(up), len(both)
    up, both = up[ok(up)], both[ok(both)]
    if len(up) < 0.9 * n0 or len(both) < 0.5 * m0:
        print(f'WARNING: seeds dropped (upstream {n0 - len(up)}/{n0}, wake/hole {m0 - len(both)}/{m0}); check the box bounds', file=sys.stderr)
    if not len(up) and not len(both):
        return []
    lines = list(integrate(F, up, 1.0, ds, nmax, 0.02))
    fw = integrate(F, both, 1.0, ds, nmax, 0.02)
    bw = integrate(F, both, -1.0, ds, nmax, 0.02)
    for (Pf, Sf), (Pb, Sb) in zip(fw, bw):
        lines.append((np.concatenate([Pb[::-1], Pf[1:]]), np.concatenate([Sb[::-1], Sf[1:]])))
    step = max(1, args.every)
    out = []
    for P, S in lines:  # the far wake is turbulent spaghetti: cut every line at --line-xmax
        over = np.nonzero(P[:, 0] > args.line_xmax)[0]
        if len(over):
            P, S = P[:over[0]], S[:over[0]]
        if len(P) >= 8:
            out.append((P[::step], S[::step]))
    return out


# ---------------------------------------------------------------- vortex
def decimate(v, f, max_faces, h):
    """Vertex clustering until the face count fits."""
    cs = h * 0.5
    while len(f) > max_faces:
        key = np.floor((v - v.min(0)) / cs).astype(np.int64)
        kk = key[:, 0] * 1000003 + key[:, 1] * 1009 + key[:, 2]
        uk, inv = np.unique(kk, return_inverse=True)
        nv = np.zeros((len(uk), 3))
        np.add.at(nv, inv, v)
        nv /= np.bincount(inv)[:, None]
        nf = inv[f]
        nf = nf[(nf[:, 0] != nf[:, 1]) & (nf[:, 1] != nf[:, 2]) & (nf[:, 0] != nf[:, 2])]
        v, f = nv, nf
        cs *= 1.25
    return v, f


def vortex(F, args):
    st = args.stride
    sl = (slice(None, None, st),) * 3
    u = [c[sl] for c in F.u]
    sol = F.solid[sl]
    h = F.dx * st
    G = [[np.gradient(u[i], h, axis=2 - j) for j in range(3)] for i in range(3)]  # du_i/dx_j
    S2 = np.zeros(sol.shape, np.float32)
    W2 = np.zeros_like(S2)
    for i in range(3):
        for j in range(3):
            S2 += (0.5 * (G[i][j] + G[j][i])) ** 2
            W2 += (0.5 * (G[i][j] - G[j][i])) ** 2
    Q = 0.5 * (W2 - S2)
    wx = G[2][1] - G[1][2]
    wy = G[0][2] - G[2][0]
    wz = G[1][0] - G[0][1]
    fd = np.array(F.meta.get('flow_dir', [1, 0, 0]), float)
    wstream = ndi.gaussian_filter(wx * fd[0] + wy * fd[1] + wz * fd[2], 0.8)
    near = ndi.binary_dilation(sol, iterations=3)
    Q = ndi.gaussian_filter(Q, 0.8)
    Q[near] = 0
    for ax in range(3):
        for s in (slice(0, 2), slice(-2, None)):
            idx = [slice(None)] * 3
            idx[ax] = s
            Q[tuple(idx)] = 0
    qpos = Q[Q > 0]
    if qpos.size == 0:
        return [], [], 1.0
    # levels in body units (U/D)^2, so they do not depend on how intense a particular snapshot is
    levels = [float(q) for q in args.q_levels]
    print('Q 99.9 pct', float(np.percentile(qpos, 99.9)), 'levels', levels, file=sys.stderr)
    xs = F.org[0] + h * np.arange(Q.shape[2])
    Q[:, :, xs > args.vortex_xmax] = 0
    wmax = float(np.percentile(np.abs(wstream[~near]), 99.5)) or 1.0
    meshes = []
    for lv in levels:
        try:
            v, f, _, _ = measure.marching_cubes(Q, lv, spacing=(h, h, h))
        except (ValueError, RuntimeError):
            meshes.append(None)
            continue
        v = v[:, ::-1] + F.org  # (k,j,i) -> (x,y,z)
        f = f[:, ::-1].copy()
        v, f = decimate(v, f, args.max_faces, h)
        c = np.stack([(v[:, 2] - F.org[2]) / h, (v[:, 1] - F.org[1]) / h, (v[:, 0] - F.org[0]) / h])
        w = ndi.map_coordinates(wstream, c, order=1, mode='nearest')
        meshes.append((v, f, np.clip(np.round(w / wmax * 127), -127, 127).astype(np.int8)))
    return levels, meshes, wmax


# ---------------------------------------------------------------- slices
def nice_levels(lo, hi, n):
    raw = (hi - lo) / n
    mag = 10 ** np.floor(np.log10(raw))
    step = min((1, 2, 2.5, 5, 10), key=lambda s: abs(s * mag - raw)) * mag
    return np.arange(np.ceil(lo / step) * step, hi + 1e-9, step)


def slice_plane(F, normal_axis, outdir, up, vmax):
    fa = int(np.argmax(np.abs(F.meta.get('flow_dir', [1, 0, 0]))))
    ia = [a for a in range(3) if a not in (fa, normal_axis)][0]  # vertical in-plane axis
    n = F.shape[::-1]
    pick = int(np.clip(round((0 - F.org[normal_axis]) / F.dx), 0, n[normal_axis] - 1))

    def cut(a):  # returns 2D [vertical, flow]
        sl = [slice(None)] * 3
        sl[2 - normal_axis] = pick
        s = a[tuple(sl)]
        rem = [2 - ax for ax in (0, 1, 2) if ax != 2 - normal_axis]  # world axes of s's dims
        return s if rem == [ia, fa] else s.T

    u = [cut(c) for c in F.u]
    sol = cut(F.solid)
    spd = np.sqrt(sum(c * c for c in u))
    sign = 1.0 if (fa, ia, normal_axis) in ((0, 1, 2), (1, 2, 0), (2, 0, 1)) else -1.0
    vort = sign * (np.gradient(u[ia], F.dx, axis=1) - np.gradient(u[fa], F.dx, axis=0))
    vort = ndi.gaussian_filter(vort, 0.7)
    zk = dict(grid_mode=True, mode='nearest')
    spd_u = ndi.zoom(spd.astype(np.float32), up, order=3, **zk)
    vort_u = ndi.zoom(vort.astype(np.float32), up, order=3, **zk)
    sol_u = ndi.zoom(sol.astype(np.float32), up, order=1, **zk) > 0.5
    fl = vort_u[~ndi.binary_dilation(sol_u, iterations=3)]
    wlim = float(np.percentile(np.abs(fl), 99.5)) if fl.size else 0.0
    wlim = wlim or 5.0
    ext_f = (float(F.org[fa] - F.dx / 2), float(F.hi[fa] + F.dx / 2))
    ext_v = (float(F.org[ia] - F.dx / 2), float(F.hi[ia] + F.dx / 2))
    tag = 'xyz'[normal_axis] + '0'
    for nm, arr, cmap, lo, hi in (('speed', spd_u, 'turbo', 0, vmax), ('vort', vort_u, 'RdBu_r', -wlim, wlim)):
        rgba = (colormaps[cmap](np.clip((arr - lo) / (hi - lo), 0, 1)) * 255).astype(np.uint8)
        rgba[sol_u, 3] = 0
        Image.fromarray(np.ascontiguousarray(rgba[::-1]), 'RGBA').save(
            os.path.join(outdir, f'slice_{tag}_{nm}.png'), optimize=True)
    info = {'tag': tag, 'normal_axis': 'xyz'[normal_axis], 'flow_axis': 'xyz'[fa], 'vert_axis': 'xyz'[ia],
            'extent_flow': ext_f, 'extent_vert': ext_v, 'speed_png': f'slice_{tag}_speed.png',
            'vort_png': f'slice_{tag}_vort.png', 'size': list(spd_u.shape[::-1]), 'vort_range': [-wlim, wlim]}
    segs = {}
    cu = 2  # extra smooth upsampling so contour lines are not polygonal
    sm = {'speed': ndi.zoom(ndi.gaussian_filter(spd_u, 0.6), cu, order=3, **zk),
          'vort': ndi.zoom(ndi.gaussian_filter(vort_u, 1.0), cu, order=3, **zk)}
    levs = {'speed': nice_levels(0.1, vmax, 14), 'vort': nice_levels(-wlim, wlim, 10)}
    mask = ndi.zoom(ndi.binary_dilation(sol_u, iterations=2).astype(np.float32), cu, order=0, **zk) > 0.5
    H, W = sm['speed'].shape
    for nm in ('speed', 'vort'):
        out, lid = [], []
        for li, lv in enumerate(levs[nm]):
            if nm == 'vort' and abs(lv) < 1e-9:
                continue
            a = np.where(mask, lv - 1e9 if lv > 0 else lv + 1e9, sm[nm])
            for c in measure.find_contours(a, lv):
                c = measure.approximate_polygon(c, 0.25)
                if len(c) < 2:
                    continue
                vv = ext_v[0] + (c[:, 0] + 0.5) / H * (ext_v[1] - ext_v[0])
                ff = ext_f[0] + (c[:, 1] + 0.5) / W * (ext_f[1] - ext_f[0])
                pts = np.stack([ff, vv], 1)
                out.append(np.concatenate([pts[:-1], pts[1:]], 1))
                lid.append(np.full(len(pts) - 1, li, np.uint8))
        segs[nm] = (np.concatenate(out).astype(np.float32) if out else np.zeros((0, 4), np.float32),
                    np.concatenate(lid) if lid else np.zeros(0, np.uint8))
    info['levels'] = {k: [float(x) for x in v] for k, v in levs.items()}
    return info, segs



# ---------------------------------------------------------------- time series
def plane_fields(F, normal_axis):
    """In-plane flow/vertical velocity, vorticity and solid mask on the snapshot grid ([vertical, flow])."""
    fa = int(np.argmax(np.abs(F.meta.get('flow_dir', [1, 0, 0]))))
    ia = [a for a in range(3) if a not in (fa, normal_axis)][0]
    n = F.shape[::-1]
    pick = int(np.clip(round((0 - F.org[normal_axis]) / F.dx), 0, n[normal_axis] - 1))
    rem = [2 - ax for ax in (0, 1, 2) if ax != 2 - normal_axis]

    def cut(a):
        sl = [slice(None)] * 3
        sl[2 - normal_axis] = pick
        s = a[tuple(sl)]
        return s if rem == [ia, fa] else s.T
    uf, uv = cut(F.u[fa]), cut(F.u[ia])
    sign = 1.0 if (fa, ia, normal_axis) in ((0, 1, 2), (1, 2, 0), (2, 0, 1)) else -1.0
    vort = ndi.gaussian_filter(sign * (np.gradient(uv, F.dx, axis=1) - np.gradient(uf, F.dx, axis=0)), 0.7)
    return uf, uv, vort, cut(F.solid), cut(F.speed)


def write_frames(paths, normals, sinfo, vmax, outdir):
    """Compact per-frame slice fields: uint8 speed, int8 vorticity, int8 in-plane velocity (first plane only)."""
    w = Writer(os.path.join(outdir, 'frames.bin'))
    tstars, size = [], None
    wl = [si['vort_range'][1] for si in sinfo]
    for n, p in enumerate(paths):
        meta, blk = load_blocks(p)
        F = Field(meta, blk)
        tstars.append(float(meta.get('t_star', n)))
        for pi, nax in enumerate(normals):
            uf, uv, vort, sol, spd = plane_fields(F, nax)
            tag = sinfo[pi]['tag']
            size = list(uf.shape[::-1])
            if n == 0:
                w.add(f'sol_{tag}', sol.astype(np.uint8))
            w.add(f'f{n}_{tag}_s', np.clip(np.round(spd / vmax * 255), 0, 255).astype(np.uint8))
            w.add(f'f{n}_{tag}_w', np.clip(np.round(vort / wl[pi] * 127), -127, 127).astype(np.int8))
            if pi == 0:
                w.add(f'f{n}_{tag}_u', np.clip(np.round(uf / vmax * 127), -127, 127).astype(np.int8))
                w.add(f'f{n}_{tag}_v', np.clip(np.round(uv / vmax * 127), -127, 127).astype(np.int8))
        print(f'frame {n + 1}/{len(paths)} t*={tstars[-1]:g}', file=sys.stderr)
    info = w.close()
    return info, {'n': len(paths), 't_star': tstars, 'size': size, 'vel_plane': sinfo[0]['tag'],
                  'vel_scale': vmax, 'vort_scale': wl}

# ---------------------------------------------------------------- body
def body(meta_fine, blk_fine, F, body_faces=45000):
    if blk_fine is not None:
        m = np.asarray(blk_fine['solid']) > 0
        dx = meta_fine['dx_D']
        org = np.array(meta_fine['origin_D'], float)
    else:
        m, dx, org = F.solid, F.dx, F.org
    m = np.pad(m, 2).astype(np.float32)
    org = org - 2 * dx
    sm = ndi.gaussian_filter(m, 1.0)  # light blur removes voxel terracing, keeps the thin shell
    v, f, _, _ = measure.marching_cubes(sm, 0.3, spacing=(dx, dx, dx))
    v, f = decimate(v, f, body_faces, dx)
    g = np.stack(np.gradient(sm), 0)
    nrm = -np.stack([ndi.map_coordinates(g[a], (v / dx).T, order=1) for a in range(3)], 1)[:, ::-1]
    nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-9)
    v = v[:, ::-1] + org
    return v.astype(np.float32), np.ascontiguousarray(f).astype(np.uint32), np.round(nrm * 127).astype(np.int8)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('snapshot')
    ap.add_argument('--fine')
    ap.add_argument('-o', '--out', required=True)
    ap.add_argument('--label', default='')
    ap.add_argument('--n-up', type=int, default=500, dest='n_up')
    ap.add_argument('--n-wake', type=int, default=160, dest='n_wake')
    ap.add_argument('--n-hole', type=int, default=90, dest='n_hole')
    ap.add_argument('--line-xmax', type=float, default=1.2, dest='line_xmax', help='cut streamlines downstream of this x/D')
    ap.add_argument('--every', type=int, default=2, help='keep every Nth integration step (1 cell each)')
    ap.add_argument('--stride', type=int, default=2, help='grid stride for the Q-criterion')
    ap.add_argument('--q-levels', type=float, nargs='+', default=[4.0, 12.0, 30.0], dest='q_levels', help='Q iso-levels in (U/D)^2')
    ap.add_argument('--vortex-xmax', type=float, default=1.3, dest='vortex_xmax', help='clip vortex surfaces downstream of this x/D')
    ap.add_argument('--max-faces', type=int, default=60000, dest='max_faces')
    ap.add_argument('--body-faces', type=int, default=45000, dest='body_faces')
    ap.add_argument('--slice-up', type=int, default=2, dest='slice_up')
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--series', help='glob of snapshot .json files (time series); the positional snapshot is the reference frame for the static layers')
    ap.add_argument('--u-mps', type=float, dest='u_mps', help='free-stream speed in m/s (default: parsed from the label)')
    ap.add_argument('--frame-step', type=int, default=1, dest='frame_step', help='series: keep every Nth complete frame')
    ap.add_argument('--orientation', default='btw', help='orientation tag stored in the manifest (ASSUMED)')
    ap.add_argument('--add-index', dest='add_index', help='index.json to add or update with this bundle (id, label, path, speed_mps, S, orientation)')
    ap.add_argument('--d-mm', type=float, default=71.12, dest='d_mm', help='body diameter in mm')
    a = ap.parse_args()
    t0 = time.time()
    os.makedirs(a.out, exist_ok=True)
    rng = np.random.default_rng(a.seed)
    meta, blk = load_blocks(a.snapshot)
    F = Field(meta, blk)
    run_args = meta.get('args')  # solver writes its command line as a string; the test generator writes a dict
    synthetic = bool(meta.get('synthetic') or (isinstance(run_args, dict) and run_args.get('synthetic')))
    fm = fb = None
    if a.fine:
        fm, fb = load_blocks(a.fine)
    else:
        print('WARNING: no --fine solid mask; the coarse mask can lose a 1-2 cell shell. Pass <base>_solid_fine.json.', file=sys.stderr)
    vmax = float(max(1.5, min(2.5, np.percentile(F.speed[~F.solid], 99.9))))
    lo, hi = F.org.astype(np.float64), F.hi.astype(np.float64)
    files = {}

    L = streamlines(F, a, rng)
    w = Writer(os.path.join(a.out, 'streamlines.bin'))
    cnt = np.array([len(P) for P, _ in L], np.uint32)
    allp = np.concatenate([P for P, _ in L]) if L else np.zeros((0, 3), np.float32)
    alls = np.concatenate([S for _, S in L]) if L else np.zeros(0, np.float32)
    w.add('counts', cnt)
    w.add('pos', quant(allp, lo, hi))
    w.add('speed', np.clip(alls / vmax * 255, 0, 255).astype(np.uint8))
    files['streamlines'] = w.close()
    files['streamlines'].update(n_lines=len(L), n_verts=int(cnt.sum()))
    print('streamlines', len(L), int(cnt.sum()), f'{time.time()-t0:.0f}s')

    levels, meshes, wmax = vortex(F, a)
    w = Writer(os.path.join(a.out, 'vortex.bin'))
    vinfo = []
    for i, m in enumerate(meshes):
        if m is None:
            continue
        v, f, om = m
        w.add(f'pos{i}', quant(v, lo, hi))
        w.add(f'omega{i}', om)
        w.add(f'idx{i}', f.astype(np.uint32))
        vinfo.append({'level': levels[i], 'index': i, 'n_verts': len(v), 'n_faces': len(f)})
    files['vortex'] = w.close()
    print('vortex', [(x['n_verts'], x['n_faces']) for x in vinfo], f'{time.time()-t0:.0f}s')

    fa = int(np.argmax(np.abs(meta.get('flow_dir', [1, 0, 0]))))
    spin = np.array(meta.get('omega_axis') or [0, 0, 0], float)
    sax = int(np.argmax(np.abs(spin)))
    if np.linalg.norm(spin) > 0 and sax != fa:
        third = [x for x in range(3) if x not in (fa, sax)][0]
        normals = [sax, third]  # normal to the spin axis (Magnus deflection visible) first, then the plane holding flow and spin axis
    else:
        normals = [x for x in range(3) if x != fa][:2]
    w = Writer(os.path.join(a.out, 'slices.bin'))
    sinfo = []
    for nax in normals:
        info, segs = slice_plane(F, nax, a.out, a.slice_up, vmax)
        for nm in ('speed', 'vort'):
            w.add(f"{info['tag']}_{nm}_seg", segs[nm][0])
            w.add(f"{info['tag']}_{nm}_lvl", segs[nm][1])
        sinfo.append(info)
    files['slices'] = w.close()
    print('slices', [s['tag'] for s in sinfo], f'{time.time()-t0:.0f}s')

    frames = None
    if a.series:
        paths = sorted(glob.glob(a.series), key=lambda p: float(json.load(open(p)).get('t_star', 0)))
        paths = [p for p in paths if p.endswith('.json') and 'solid_fine' not in p]
        full = []
        for p in paths:   # drop frames whose .bin is short (interrupted copy)
            m = json.load(open(p))
            need = max(b['offset'] + int(np.prod((m['nz'], m['ny'], m['nx']))) * np.dtype(b['dtype']).itemsize for b in m['blocks'])
            have = os.path.getsize(os.path.splitext(p)[0] + '.bin') if os.path.exists(os.path.splitext(p)[0] + '.bin') else 0
            if have >= need:
                full.append(p)
            else:
                print('SKIP short frame', os.path.basename(p), have, '<', need)
        paths = full[::max(1, a.frame_step)]
        if len(paths) > 1:
            files['frames'], frames = write_frames(paths, normals, sinfo, vmax, a.out)
            print('frames', len(paths), f'{time.time()-t0:.0f}s')

    bv, bf, bn = body(fm, fb, F, a.body_faces)
    w = Writer(os.path.join(a.out, 'body.bin'))
    w.add('pos', bv)
    w.add('normal', bn)
    w.add('idx', bf)
    files['body'] = w.close()
    files['body'].update(n_verts=len(bv), n_faces=len(bf), fine=bool(fb))

    run_id = os.path.basename(os.path.abspath(a.out))
    label = a.label or f"Re {meta.get('Re', 0):.3g}, S {meta.get('S', 0):g}"
    manifest = {
        'version': 1, 'id': run_id, 'label': label, 'synthetic': synthetic,
        'status': SYN if synthetic else PRED,
        'units': 'lengths in body diameters D, origin at body centre; speed in free-stream U',
        't_star': meta.get('t_star'), 'Re': meta.get('Re'), 'S': meta.get('S'),
        'orientation': a.orientation, 'omega_axis': meta.get('omega_axis'), 'flow_dir': meta.get('flow_dir', [1, 0, 0]),
        'grid': {'nx': meta['nx'], 'ny': meta['ny'], 'nz': meta['nz'], 'dx_D': F.dx,
                 'D_cells': meta.get('D_cells', round(1 / F.dx))},
        'bounds': {'lo': lo.tolist(), 'hi': hi.tolist()},
        'speed_range': [0, vmax], 'vort_range': sinfo[0]['vort_range'], 'streamwise_vort_scale': wmax,
        'colormaps': {'speed': 'turbo', 'vorticity': 'RdBu_r'},
        'frames': frames, 'D_mm': a.d_mm, 'U_mps': a.u_mps or (float(re.search(r'([0-9.]+)\s*m/s', label).group(1)) if re.search(r'([0-9.]+)\s*m/s', label) else None),
        'vortex_levels': vinfo, 'slices': sinfo, 'files': files,
    }
    manifest['speed_mps'] = manifest['U_mps']
    json.dump(manifest, open(os.path.join(a.out, 'manifest.json'), 'w'), indent=1)
    if a.add_index:
        ip = a.add_index
        idx = json.load(open(ip)) if os.path.exists(ip) else {'runs': []}
        rel = os.path.relpath(os.path.join(a.out, 'manifest.json'), os.path.dirname(os.path.abspath(ip))).replace(os.sep, '/')
        ent = {'id': run_id, 'label': label, 'path': rel, 'speed_mps': manifest['U_mps'], 'S': manifest['S'],
               'orientation': a.orientation, 'series': bool(frames), 'n_frames': frames['n'] if frames else 0}
        idx['runs'] = [r for r in idx['runs'] if r.get('id') != run_id] + [ent]
        json.dump(idx, open(ip, 'w'), indent=1)
        print('index', ip, len(idx['runs']), 'runs')
    tot = sum(os.path.getsize(os.path.join(a.out, f)) for f in os.listdir(a.out))
    print(f'bundle {a.out}: {tot/1e6:.2f} MB, {time.time()-t0:.0f}s')


if __name__ == '__main__':
    main()
