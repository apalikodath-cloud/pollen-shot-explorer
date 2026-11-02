#!/usr/bin/env python3
"""Add a 3D velocity volume to an existing flow bundle (for GPU particle tracers in flow.html).

  python make_vol.py <bundle_dir> --series "<fields>/<run>_f*.json" [--ds 2]

For every frame listed in the bundle's manifest (frames.t_star) it reads the matching snapshot,
and writes vol/fNNN.vgz: a gzip of int8 RGBA voxels, x fastest, on a grid coarsened ds times:
  R, G, B = ux, uy, uz / vel_scale * 127 (free-stream U units, block mean over ds^3 cells)
  A       = sign(streamwise vorticity) * sqrt(max(Q, 0)) / q_scale * 127, Q in (U/D)^2 from the
            full-resolution field, block mean (the vortex-core strength).
Solid cells have zero velocity. With a time mean in the bundle (manifest.mean) it also writes
vol/mean.vgz from the mean of the same frames. The manifest gets a "vol" section.
PREDICTED: CFD model output, not a measurement.
"""
import argparse, glob, gzip, json, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_flow import load_blocks  # noqa: E402

VEL_SCALE = 2.0      # |u_i| / U clipped at this
Q_SCALE = 16.0       # sqrt(Q) in U/D mapped to 127 (about the 99.5th percentile in the fluid)


def read(path):
    meta, blk = load_blocks(path)
    u = [np.nan_to_num(np.array(blk[k], dtype=np.float32), nan=0.0, posinf=0.0, neginf=0.0) for k in ('ux', 'uy', 'uz')]
    sol = np.asarray(blk['solid']) > 0
    for c in u:
        c[sol] = 0
    return meta, u, sol


def q_signed(u, dx):
    """sign(omega_x) sqrt(max(Q,0)) on the full grid; arrays are (z, y, x)."""
    g = [np.gradient(c, dx) for c in u]          # g[i][j] = d u_i / d x_(z,y,x)[j]
    J = [[g[i][2 - j] for j in range(3)] for i in range(3)]   # J[i][j] = d u_i / d x_j with x_j in (x, y, z)
    Q = np.zeros_like(u[0])
    for i in range(3):
        for j in range(3):
            Q -= 0.5 * J[i][j] * J[j][i]
    wx = J[2][1] - J[1][2]
    return np.sign(wx) * np.sqrt(np.maximum(Q, 0))


def coarsen(u, s, ds):
    nz, ny, nx = u[0].shape
    cz, cy, cx = nz // ds, ny // ds, nx // ds
    def blocks(a):
        return a[:cz * ds, :cy * ds, :cx * ds].reshape(cz, ds, cy, ds, cx, ds).transpose(0, 2, 4, 1, 3, 5).reshape(cz, cy, cx, ds ** 3)
    out = np.empty((cz, cy, cx, 4), np.int8)
    for k in range(3):
        out[..., k] = np.clip(np.round(blocks(u[k]).mean(-1) / VEL_SCALE * 127), -127, 127)
    out[..., 3] = np.clip(np.round(blocks(s).mean(-1) / Q_SCALE * 127), -127, 127)
    return out


def write(path, vox):
    with gzip.open(path, 'wb', compresslevel=6) as f:
        f.write(vox.tobytes())
    return os.path.getsize(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('bundle')
    ap.add_argument('--series', required=True)
    ap.add_argument('--ds', type=int, default=2)
    a = ap.parse_args()
    mp = os.path.join(a.bundle, 'manifest.json')
    man = json.load(open(mp))
    want = man['frames']['t_star'] if man.get('frames') else [man.get('t_star')]
    paths = {}
    for p in glob.glob(a.series):
        if p.endswith('.json') and 'solid_fine' not in p:
            paths[round(float(json.load(open(p)).get('t_star', -1)), 4)] = p
    sel = [paths.get(round(float(t), 4)) for t in want]
    if any(p is None for p in sel):
        sys.exit(f'missing snapshots for t* {[t for t, p in zip(want, sel) if p is None]}')
    os.makedirs(os.path.join(a.bundle, 'vol'), exist_ok=True)
    urls, total, acc, n = [], 0, None, 0
    for i, p in enumerate(sel):
        meta, u, sol = read(p)
        vox = coarsen(u, q_signed(u, meta['dx_D']), a.ds)
        name = f'vol/f{i:03d}.vgz'
        total += write(os.path.join(a.bundle, name), vox)
        urls.append(name)
        if man.get('mean'):
            acc = [c.astype(np.float64) for c in u] if acc is None else [x + c for x, c in zip(acc, u)]
            n += 1
        print(name, os.path.basename(p), flush=True)
    vol = {
        'size': [int(x) for x in vox.shape[2::-1]],      # nx, ny, nz
        'origin': (np.array(meta['origin_D']) + 0.5 * (a.ds - 1) * meta['dx_D']).tolist(),
        'dx': meta['dx_D'] * a.ds, 'vel_scale': VEL_SCALE, 'q_scale': Q_SCALE,
        'format': 'gzip int8 RGBA, x fastest: velocity (U) and signed sqrt(Q) (U/D)',
        'frames': urls, 't_star': [float(t) for t in want], 'mean': None,
        'note': 'PREDICTED (CFD model output). Velocity coarsened %dx for particle tracers.' % a.ds,
    }
    if acc is not None and n > 1:
        mu = [(x / n).astype(np.float32) for x in acc]
        vox = coarsen(mu, q_signed(mu, meta['dx_D']), a.ds)
        total += write(os.path.join(a.bundle, 'vol/mean.vgz'), vox)
        vol['mean'] = 'vol/mean.vgz'
    man['vol'] = vol
    json.dump(man, open(mp, 'w'), indent=1)
    print(f'{a.bundle}: {len(urls)} frames, {total / 1e6:.1f} MB')


if __name__ == '__main__':
    main()
