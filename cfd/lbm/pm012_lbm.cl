// PM-012 (FTC POLLEN Magnus project): OpenCL C 1.2 kernels of the own D3Q19 lattice Boltzmann LES solver.
// Written for this project (no third-party source); host program: pm012_lbm.cpp. Method: Krueger et al. 2017,
// "The Lattice Boltzmann Method" (D3Q19, BGK, halfway bounce-back, moving wall, momentum exchange); Ladd 1994
// (moving-wall term); Hou et al. 1996 (Smagorinsky in LBM); Latt & Chopard 2006 (regularized collision).
//
// Storage: two lattices (pull scheme), one buffer per direction, shifted populations g_i = f_i - w_i.
// FP16: IEEE half storage scaled by 2^15 (all arithmetic in float). Compile-time constants from the host:
// NX, NY, NZ, NCELLS, WG (work-group size of body_force), optional FP16 and REG (regularized collision; else BGK).
// Lattice units: dx = dt = 1, cs^2 = 1/3, rho0 = 1. Spin is about +y: wall velocity u_w = om e_y x (r - c).

#define F_SOLID 1u
#define F_EQ 2u    // fixed equilibrium cell (inlet, sides): rho = 1, u = inflow, never updated
#define F_OUT 4u   // pressure outlet cell: rho = 1, u copied from the cell upstream
#define F_NEAR 8u  // fluid cell with at least one solid neighbour
#define F_NEW 16u  // scratch bit of the geometry update

#ifdef FP16
typedef half fs;
#define LD(p, i) (vload_half((size_t)(i), (p)) * 3.0517578125e-5f)
#define ST(p, i, v) vstore_half_rte((v) * 32768.0f, (size_t)(i), (p))
#else
typedef float fs;
#define LD(p, i) ((p)[(i)])
#define ST(p, i, v) ((p)[(i)] = (v))
#endif

#define FARG(p) global fs* p##0, global fs* p##1, global fs* p##2, global fs* p##3, global fs* p##4, global fs* p##5, \
	global fs* p##6, global fs* p##7, global fs* p##8, global fs* p##9, global fs* p##10, global fs* p##11, global fs* p##12, \
	global fs* p##13, global fs* p##14, global fs* p##15, global fs* p##16, global fs* p##17, global fs* p##18
#define FLIST(p) { p##0, p##1, p##2, p##3, p##4, p##5, p##6, p##7, p##8, p##9, p##10, p##11, p##12, p##13, p##14, p##15, \
	p##16, p##17, p##18 }

// D3Q19: 0 rest; 1..6 axes; 7..18 diagonals. opposite(i) = i+1 for odd i, i-1 for even i > 0.
constant int CX[19] = { 0, 1, -1, 0, 0, 0, 0, 1, -1, 1, -1, 0, 0, 1, -1, 1, -1, 0, 0 };
constant int CY[19] = { 0, 0, 0, 1, -1, 0, 0, 1, -1, 0, 0, 1, -1, -1, 1, 0, 0, 1, -1 };
constant int CZ[19] = { 0, 0, 0, 0, 0, 1, -1, 0, 0, 1, -1, 1, -1, 0, 0, -1, 1, -1, 1 };
constant int OPP[19] = { 0, 2, 1, 4, 3, 6, 5, 8, 7, 10, 9, 12, 11, 14, 13, 16, 15, 18, 17 };
constant float W[19] = { 1.0f/3.0f, 1.0f/18.0f, 1.0f/18.0f, 1.0f/18.0f, 1.0f/18.0f, 1.0f/18.0f, 1.0f/18.0f,
	1.0f/36.0f, 1.0f/36.0f, 1.0f/36.0f, 1.0f/36.0f, 1.0f/36.0f, 1.0f/36.0f,
	1.0f/36.0f, 1.0f/36.0f, 1.0f/36.0f, 1.0f/36.0f, 1.0f/36.0f, 1.0f/36.0f };

#define OFS(i) (CX[i] + (int)NX * CY[i] + (int)(NX * NY) * CZ[i])

// shifted equilibrium g_eq = f_eq - w_i, second order; d = rho - 1
inline float geq(const int i, const float d, const float rho, const float ux, const float uy, const float uz, const float usq) {
	const float cu = (float)CX[i] * ux + (float)CY[i] * uy + (float)CZ[i] * uz;
	return W[i] * (d + rho * (3.0f * cu + 4.5f * cu * cu - 1.5f * usq));
}

// one time step for every fluid and outlet cell: pull-stream from lattice a, collide, store in lattice b
kernel void stream_collide(FARG(a), FARG(b), global const uchar* restrict flags, const float om, const float ccx,
		const float ccy, const float ccz, const float tau0, const float csm) {
	const uint n = get_global_id(0);
	if (n >= NCELLS) return;
	const uint fl = flags[n];
	if (fl & (F_SOLID | F_EQ)) return;
	global fs* A[19] = FLIST(a);
	global fs* B[19] = FLIST(b);
	if (fl & F_OUT) { // rho = 1, u of the upstream cell (its post-collision moments at time t)
		float d = 0.0f, jx = 0.0f, jy = 0.0f, jz = 0.0f;
#pragma unroll
		for (int i = 0; i < 19; i++) {
			const float v = LD(A[i], n - 1u);
			d += v; jx += (float)CX[i] * v; jy += (float)CY[i] * v; jz += (float)CZ[i] * v;
		}
		const float ir = 1.0f / (1.0f + d), ux = jx * ir, uy = jy * ir, uz = jz * ir, usq = ux * ux + uy * uy + uz * uz;
#pragma unroll
		for (int i = 0; i < 19; i++) ST(B[i], n, geq(i, 0.0f, 1.0f, ux, uy, uz, usq));
		return;
	}
	const int x = (int)(n % NX), z = (int)(n / (NX * NY));
	float g[19];
#pragma unroll
	for (int i = 0; i < 19; i++) g[i] = LD(A[i], (uint)((int)n - OFS(i))); // f_i(x, t+1) = f*_i(x - c_i, t)
	if (fl & F_NEAR) { // halfway bounce-back with the moving-wall term: f_i = f*_opp(i)(x) + 6 w_i (c_i . u_w)
#pragma unroll
		for (int i = 1; i < 19; i++) {
			if (flags[(uint)((int)n - OFS(i))] & F_SOLID) {
				const float rx = (float)x - 0.5f * (float)CX[i] - ccx, rz = (float)z - 0.5f * (float)CZ[i] - ccz; // link midpoint
				g[i] = LD(A[OPP[i]], n) + 6.0f * W[i] * om * ((float)CX[i] * rz - (float)CZ[i] * rx);
			}
		}
	}
	float d = 0.0f, jx = 0.0f, jy = 0.0f, jz = 0.0f;
#pragma unroll
	for (int i = 0; i < 19; i++) { d += g[i]; jx += (float)CX[i] * g[i]; jy += (float)CY[i] * g[i]; jz += (float)CZ[i] * g[i]; }
	const float rho = 1.0f + d, ir = 1.0f / rho;
	const float ux = jx * ir, uy = jy * ir, uz = jz * ir, usq = ux * ux + uy * uy + uz * uz;
	float ge[19];
	float pxx = 0.0f, pyy = 0.0f, pzz = 0.0f, pxy = 0.0f, pxz = 0.0f, pyz = 0.0f; // non-equilibrium momentum flux
#pragma unroll
	for (int i = 0; i < 19; i++) {
		ge[i] = geq(i, d, rho, ux, uy, uz, usq);
		const float fn = g[i] - ge[i];
		const float cx = (float)CX[i], cy = (float)CY[i], cz = (float)CZ[i];
		pxx += cx * cx * fn; pyy += cy * cy * fn; pzz += cz * cz * fn;
		pxy += cx * cy * fn; pxz += cx * cz * fn; pyz += cy * cz * fn;
	}
	const float qn = sqrt(pxx * pxx + pyy * pyy + pzz * pzz + 2.0f * (pxy * pxy + pxz * pxz + pyz * pyz));
#ifdef CSMN // Smagorinsky constant of the wall cells (F_NEAR) set apart, as csm = 18 sqrt(2) Cs^2
	const float cs_ = (fl & F_NEAR) ? (float)(CSMN) : csm;
#else
	const float cs_ = csm;
#endif
	float tau = 0.5f * (tau0 + sqrt(tau0 * tau0 + cs_ * qn * ir)); // Smagorinsky: csm = 18 sqrt(2) Cs^2
#ifdef TAUN // lower bound of tau in the wall cells
	if (fl & F_NEAR) tau = fmax(tau, (float)(TAUN));
#endif
	const float k = 1.0f - 1.0f / tau;
#ifdef REG
	const float tr = (pxx + pyy + pzz) * (1.0f / 3.0f);
#pragma unroll
	for (int i = 0; i < 19; i++) {
		const float cx = (float)CX[i], cy = (float)CY[i], cz = (float)CZ[i];
		const float cpc = cx * cx * pxx + cy * cy * pyy + cz * cz * pzz + 2.0f * (cx * cy * pxy + cx * cz * pxz + cy * cz * pyz);
#ifdef KB // trace of Pi_neq (bulk-viscosity mode) relaxed with 1 - KB, the deviatoric part with 1/tau
		const float c2 = cx * cx + cy * cy + cz * cz;
		ST(B[i], n, ge[i] + 4.5f * W[i] * (k * (cpc - tr * c2) + (float)(KB) * tr * (c2 - 1.0f)));
#else
		ST(B[i], n, ge[i] + k * 4.5f * W[i] * (cpc - tr)); // regularized: f_eq + (1 - 1/tau) f1(Pi_neq)
#endif
	}
#else
#pragma unroll
	for (int i = 0; i < 19; i++) ST(B[i], n, ge[i] + k * (g[i] - ge[i])); // BGK
#endif
}

// set both lattices to equilibrium: rho = 1, u = inflow (+ small hashed noise in fluid cells), wall velocity in solid cells
kernel void init_cells(FARG(a), FARG(b), global const uchar* restrict flags, const float uin, const float pert,
		const float om, const float ccx, const float ccy, const float ccz) {
	const uint n = get_global_id(0);
	if (n >= NCELLS) return;
	const uint fl = flags[n];
	global fs* A[19] = FLIST(a);
	global fs* B[19] = FLIST(b);
	const float x = (float)(n % NX), z = (float)(n / (NX * NY));
	float ux = uin, uy = 0.0f, uz = 0.0f;
	if (fl & F_SOLID) {
		ux = om * (z - ccz); uz = -om * (x - ccx);
	} else if (!(fl & (F_EQ | F_OUT)) && pert > 0.0f) {
		uint h = n * 2654435761u + 0x9E3779B9u;
		float r[3];
		for (int k = 0; k < 3; k++) {
			h ^= h >> 16; h *= 0x7feb352du; h ^= h >> 15; h *= 0x846ca68bu; h ^= h >> 16;
			r[k] = (float)(h & 0xFFFFFFu) * (2.0f / 16777215.0f) - 1.0f;
		}
		ux += pert * uin * r[0]; uy = pert * uin * r[1]; uz = pert * uin * r[2];
	}
	const float usq = ux * ux + uy * uy + uz * uz;
#pragma unroll
	for (int i = 0; i < 19; i++) {
		const float v = geq(i, 0.0f, 1.0f, ux, uy, uz, usq);
		ST(A[i], n, v); ST(B[i], n, v);
	}
}

// geometry pass 1 over the body box: F_NEW = cell centre inside the body. Sphere: |r| <= R (r2 > 0). Otherwise the
// body-frame occupancy grid occ (M^3 voxels of size h, first voxel at -rg) sampled at Rot_y(-theta) (x - c).
kernel void geo_solid(global uchar* flags, global const uchar* restrict occ, const uint bx0, const uint by0, const uint bz0,
		const uint bx, const uint by, const uint bz, const float ccx, const float ccy, const float ccz, const float ct,
		const float st, const float r2, const uint M, const float h, const float rg) {
	const uint id = get_global_id(0);
	if (id >= bx * by * bz) return;
	const uint x = bx0 + id % bx, y = by0 + (id / bx) % by, z = bz0 + id / (bx * by);
	const uint n = x + NX * (y + NY * z);
	const uint fl = flags[n];
	if (fl & (F_EQ | F_OUT)) return;
	const float rx = (float)x - ccx, ry = (float)y - ccy, rz = (float)z - ccz;
	bool s;
	if (r2 > 0.0f) {
		s = rx * rx + ry * ry + rz * rz <= r2;
	} else {
		const float px = rx * ct - rz * st, pz = rx * st + rz * ct;
		const int kx = (int)floor((px + rg) / h), ky = (int)floor((ry + rg) / h), kz = (int)floor((pz + rg) / h);
		s = kx >= 0 && ky >= 0 && kz >= 0 && kx < (int)M && ky < (int)M && kz < (int)M &&
			occ[(uint)kx + M * ((uint)ky + M * (uint)kz)] != (uchar)0;
	}
	flags[n] = (uchar)(s ? (fl | F_NEW) : (fl & ~F_NEW));
}

// geometry pass 2 over the body box: commit F_SOLID, set F_NEAR from the neighbours' F_NEW, refill uncovered cells
// (solid -> fluid) with the equilibrium at the local wall velocity
kernel void geo_commit(FARG(a), global uchar* flags, const uint bx0, const uint by0, const uint bz0, const uint bx,
		const uint by, const uint bz, const float ccx, const float ccy, const float ccz, const float om) {
	const uint id = get_global_id(0);
	if (id >= bx * by * bz) return;
	const uint x = bx0 + id % bx, y = by0 + (id / bx) % by, z = bz0 + id / (bx * by);
	const uint n = x + NX * (y + NY * z);
	const uint fl = flags[n];
	if (fl & (F_EQ | F_OUT)) return;
	const bool ns = (fl & F_NEW) != 0u, os = (fl & F_SOLID) != 0u;
	bool nb = false;
	if (!ns) {
#pragma unroll
		for (int i = 1; i < 19; i++) nb = nb || ((flags[(uint)((int)n + OFS(i))] & F_NEW) != 0u);
	}
	flags[n] = (uchar)((fl & ~(F_SOLID | F_NEAR)) | (ns ? F_SOLID : 0u) | (nb ? F_NEAR : 0u));
	if (os && !ns) {
		global fs* A[19] = FLIST(a);
		const float ux = om * ((float)z - ccz), uz = -om * ((float)x - ccx), usq = ux * ux + uz * uz;
#pragma unroll
		for (int i = 0; i < 19; i++) ST(A[i], n, geq(i, 0.0f, 1.0f, ux, 0.0f, uz, usq));
	}
}

// force and torque on the body by momentum exchange over every fluid-solid link, from the post-collision lattice a:
// dF = c_i (2 g*_i(x) - 6 w_i c_i.u_w) for x fluid, x + c_i solid (the uniform part 2 w_i c_i sums to zero over a
// closed voxel body, and so does its torque). Torque arm: link midpoint x + c_i/2 - c. Per-group sums to part[6 g + k]
// and sg times them to partn (sg = +-1 by step parity: period-2 check), added to the stored sums when acc = 1 (time
// average over every step between two samples).
kernel void body_force(FARG(a), global const uchar* restrict flags, const uint bx0, const uint by0, const uint bz0,
		const uint bx, const uint by, const uint bz, const float ccx, const float ccy, const float ccz, const float om,
		const uint acc, const float sg, global float* part, global float* partn) {
	local float red[6 * WG];
	const uint id = get_global_id(0), lid = get_local_id(0);
	float fx = 0.0f, fy = 0.0f, fz = 0.0f, tx = 0.0f, ty = 0.0f, tz = 0.0f;
	if (id < bx * by * bz) {
		const uint x = bx0 + id % bx, y = by0 + (id / bx) % by, z = bz0 + id / (bx * by);
		const uint n = x + NX * (y + NY * z);
		const uint fl = flags[n];
		if ((fl & F_NEAR) && !(fl & (F_SOLID | F_EQ | F_OUT))) {
			global fs* A[19] = FLIST(a);
#pragma unroll
			for (int i = 1; i < 19; i++) {
				if (flags[(uint)((int)n + OFS(i))] & F_SOLID) {
					const float cx = (float)CX[i], cy = (float)CY[i], cz = (float)CZ[i];
					const float rx = (float)x + 0.5f * cx - ccx, ry = (float)y + 0.5f * cy - ccy, rz = (float)z + 0.5f * cz - ccz;
					const float m = 2.0f * LD(A[i], n) - 6.0f * W[i] * om * (cx * rz - cz * rx);
					const float dx = cx * m, dy = cy * m, dz = cz * m;
					fx += dx; fy += dy; fz += dz;
					tx += ry * dz - rz * dy; ty += rz * dx - rx * dz; tz += rx * dy - ry * dx;
				}
			}
		}
	}
	red[lid] = fx; red[WG + lid] = fy; red[2 * WG + lid] = fz;
	red[3 * WG + lid] = tx; red[4 * WG + lid] = ty; red[5 * WG + lid] = tz;
	barrier(CLK_LOCAL_MEM_FENCE);
	for (uint s = WG / 2u; s > 0u; s >>= 1) {
		if (lid < s) {
			for (uint k = 0u; k < 6u; k++) red[k * WG + lid] += red[k * WG + lid + s];
		}
		barrier(CLK_LOCAL_MEM_FENCE);
	}
	if (lid == 0u) {
		for (uint k = 0u; k < 6u; k++) {
			const uint j = 6u * get_group_id(0) + k;
			part[j] = (acc ? part[j] : 0.0f) + red[k * WG];
			partn[j] = (acc ? partn[j] : 0.0f) + sg * red[k * WG];
		}
	}
}
