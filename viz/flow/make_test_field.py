#!/usr/bin/env python3
"""Generate a SYNTHETIC snapshot (not CFD) in the solver snapshot contract format.

Sphere with three orthogonal bores + potential flow + a few synthetic wake vortices.
Use only to exercise make_flow.py and the viewer. Never present the output as CFD.

  python make_test_field.py -o <outdir> [--name test] [--spin]
"""
import argparse, json, os
import numpy as np


def ring_velocity(P, centre, radius, gamma, sigma, nseg=48):
    """Biot-Savart velocity of a vortex ring about the x axis (smoothed core)."""
    th = np.linspace(0, 2 * np.pi, nseg, endpoint=False)
    th2 = th + 2 * np.pi / nseg
    def pts(t):
        return np.stack([np.full_like(t, centre[0]), centre[1] + radius * np.cos(t),
                         centre[2] + radius * np.sin(t)], 1)
    return polyline_velocity(P, pts(th), pts(th2), gamma, sigma)


def polyline_velocity(P, A, B, gamma, sigma):
    out = np.zeros_like(P)
    dl = B - A
    mid = 0.5 * (A + B)
    for s in range(0, len(P), 60000):
        p = P[s:s + 60000]
        r = p[:, None, :] - mid[None]
        r2 = (r ** 2).sum(-1) + 1e-9
        k = (1 - np.exp(-r2 / sigma ** 2)) / (4 * np.pi * r2 ** 1.5)
        out[s:s + 60000] = gamma * (np.cross(dl[None], r) * k[..., None]).sum(1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-o', '--out', required=True)
    ap.add_argument('--name', default='test')
    ap.add_argument('--spin', action='store_true', help='add a backspin-like wake asymmetry')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    dx = 1 / 32
    nx, ny, nz = 160, 96, 96
    org = np.array([-1.8, -(ny - 1) * dx / 2, -(nz - 1) * dx / 2])
    x = org[0] + dx * np.arange(nx); y = org[1] + dx * np.arange(ny); z = org[2] + dx * np.arange(nz)
    Z, Y, X = np.meshgrid(z, y, x, indexing='ij')  # arrays [k,j,i]
    P = np.stack([X, Y, Z], -1).reshape(-1, 3).astype(np.float64)

    R = 0.5
    def solid_mask(Pp, hole_r=0.13, inner=0.40):
        r = np.linalg.norm(Pp, axis=-1)
        shell = (r < R) & (r > inner)
        hole = np.zeros(r.shape, bool)
        for ax in range(3):
            o = [i for i in range(3) if i != ax]
            hole |= (Pp[..., o[0]] ** 2 + Pp[..., o[1]] ** 2) < hole_r ** 2
        return shell & ~hole

    r = np.linalg.norm(P, axis=1)
    rs = np.maximum(r, R)
    u = np.zeros_like(P)
    u[:, 0] = 1 + R ** 3 / (2 * rs ** 3)
    u -= (3 * R ** 3 / (2 * rs ** 5))[:, None] * P[:, 0:1] * P
    # wake vortices: two rings and a hairpin, shed behind the ball
    sh = 0.25 if a.spin else 0.0
    u += ring_velocity(P, (0.9, 0.0, 0.0), 0.38, 0.35, 0.09)
    u += ring_velocity(P, (1.6, 0.0, sh), 0.45, -0.25, 0.11)
    A = np.array([[0.7, -0.3, 0.0], [0.9, -0.28, 0.0], [1.2, -0.2, 0.0], [1.5, 0.0, 0.0],
                  [1.2, 0.2, 0.0], [0.9, 0.28, 0.0], [0.7, 0.3, 0.0]])
    A = A + np.array([0, 0, sh])
    u += polyline_velocity(P, A[:-1], A[1:], 0.18, 0.07)
    # through-flow in the bore along x
    inside = r < R
    bore = inside & ((P[:, 1] ** 2 + P[:, 2] ** 2) < 0.13 ** 2)
    u[inside & ~bore] = 0.05
    u[bore] = (0.55, 0, 0)
    solid = solid_mask(P)
    u[solid] = 0
    # normalise by upstream value (potential flow tends to 1)
    u = u.astype(np.float32)
    ux = u[:, 0].reshape(nz, ny, nx); uy = u[:, 1].reshape(nz, ny, nx); uz = u[:, 2].reshape(nz, ny, nx)
    sd = solid.reshape(nz, ny, nx).astype(np.uint8)
    base = os.path.join(a.out, a.name + '_f0')
    blocks, off = [], 0
    with open(base + '.bin', 'wb') as f:
        for nm, arr in (('ux', ux), ('uy', uy), ('uz', uz), ('solid', sd)):
            blocks.append({'name': nm, 'dtype': str(arr.dtype), 'offset': off})
            b = np.ascontiguousarray(arr).tobytes(); f.write(b); off += len(b)
    meta = {'t_star': 12.0, 'nx': nx, 'ny': ny, 'nz': nz, 'dx_D': dx, 'origin_D': org.tolist(),
            'flow_dir': [1, 0, 0], 'U_lattice': 0.05, 'Re': 1.0e5, 'S': 0.3 if a.spin else 0.0,
            'omega_axis': [0, 1, 0], 'D_cells': 32, 'args': {'synthetic': True}, 'synthetic': True,
            'blocks': blocks}
    json.dump(meta, open(base + '.json', 'w'), indent=1)
    # fine solid mask: half-width 0.6 D at 1/64 D
    fdx = 1 / 64; n = int(round(1.2 / fdx)) + 1
    c = -0.6 + fdx * np.arange(n)
    Zf, Yf, Xf = np.meshgrid(c, c, c, indexing='ij')
    sf = solid_mask(np.stack([Xf, Yf, Zf], -1)).astype(np.uint8)
    fb = os.path.join(a.out, a.name + '_f0_solid_fine')
    open(fb + '.bin', 'wb').write(sf.tobytes())
    json.dump({'t_star': 12.0, 'nx': n, 'ny': n, 'nz': n, 'dx_D': fdx, 'origin_D': [-0.6] * 3,
               'flow_dir': [1, 0, 0], 'blocks': [{'name': 'solid', 'dtype': 'uint8', 'offset': 0}],
               'synthetic': True}, open(fb + '.json', 'w'), indent=1)
    print('wrote', base + '.json', 'and', fb + '.json')


if __name__ == '__main__':
    main()
