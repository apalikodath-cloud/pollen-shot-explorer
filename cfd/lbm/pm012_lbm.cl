// PM-012 (FTC POLLEN Magnus project): OpenCL C 1.2 kernels of the own D3Q19 lattice Boltzmann LES solver.
// Written for this project (no third-party source); host program: pm012_lbm.cpp. Method: Krueger et al. 2017,
// "The Lattice Boltzmann Method" (D3Q19, BGK, halfway bounce-back, moving wall, momentum exchange); Ladd 1994
// (moving-wall term); Hou et al. 1996 (Smagorinsky in LBM); Latt & Chopard 2006 (regularized collision);
// Rohde et al. 2006 (volumetric, mass-conserving local grid refinement; see "grid refinement" below).
//
// Storage: two lattices (pull scheme), one buffer per direction, shifted populations g_i = f_i - w_i.
// FP16: IEEE half storage scaled by 2^15 (all arithmetic in float). Compile-time constants from the host, one program
// per grid level: NX, NY, NZ, NCELLS (this level), WG (work-group size of body_force), optional FP16 and REG
// (regularized collision; else BGK); a refined level also gets PARENT, PNX, PNY, PNZ (parent level size) and OX, OY, OZ
// (its first cell's parent cell). Lattice units of each level: dx = dt = 1, cs^2 = 1/3, rho0 = 1.
// Spin is about +y: wall velocity u_w = om e_y x (r - c).
//
// Grid refinement (cell-centred, factor 2 per level, acoustic scaling dt ~ dx, so the lattice velocity is the same on
// every level and tau_fine - 1/2 = 2 (tau_coarse - 1/2) keeps the physical viscosity). A refined level is a box that
// covers whole parent cells, each split into 2x2x2 cells. Parent cells under the box are "covered" (F_COVER): never
// updated. Per parent step the child does two steps, A then B; then the parent streams. Transfers follow the volumetric
// scheme of Rohde et al. 2006 (explosion = homogeneous copy, coalescence = average over the 8 sub-cells), written here
// in pull form so that no ghost layer is stored:
//  - explosion: a child cell whose upstream neighbour x - c_i lies outside the box reads the parent's post-collision
//    population of the parent cell holding x - c_i (step A) or x - 2 c_i (step B): those are the populations that,
//    moving at one parent cell per parent step, reach x during that step;
//  - coalescence (after step A, kernel coalesce): a covered parent cell Z gets, for every direction i whose target
//    Z + c_i is a real parent cell, the mean over the 8 sub-cells g of Z + c_i of the child population that reaches g
//    at the end of step B: the child's post-collision value at g - c_i (time t + 1/2) if that is a child cell, else at
//    g - 2 c_i (time t). The parent then streams as usual and pulls it;
//  - corner clipping: at a convex box edge a parent population can cross a child cell between two real parent cells;
//    the child pulled it in step A, so its post-collision child value replaces it on the parent route (same kernel).
// Every population is handed over exactly once, so mass and momentum are conserved to round-off. The body (and every
// solid cell) lies on the finest level, inside its box.

#define F_SOLID 1u
#define F_EQ 2u    // fixed equilibrium cell (inlet, sides): rho = 1, u = inflow, never updated
#define F_OUT 4u   // pressure outlet cell: rho = 1, u copied from the cell upstream
#define F_NEAR 8u  // fluid cell with at least one solid neighbour
#define F_NEW 16u  // scratch bit of the geometry update
#define F_COVER 32u // covered by the next finer level: not updated; holds the coalesced populations
#define F_IF 64u   // outermost layer of a refined level: some upstream neighbours lie in the parent level

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
#define IN_BOX(x, y, z) ((x) >= 0 && (x) < (int)NX && (y) >= 0 && (y) < (int)NY && (z) >= 0 && (z) < (int)NZ)
#define IDX(x, y, z) ((uint)(x) + NX * ((uint)(y) + NY * (uint)(z)))
#ifdef PARENT
#define HALF(v) ((((v) + 4) >> 1) - 2) // floor(v / 2) for v >= -4
#define PIDX(x, y, z) ((uint)(OX + HALF(x)) + PNX * ((uint)(OY + HALF(y)) + PNY * (uint)(OZ + HALF(z))))
#endif

// shifted equilibrium g_eq = f_eq - w_i, second order; d = rho - 1
inline float geq(const int i, const float d, const float rho, const float ux, const float uy, const float uz, const float usq) {
	const float cu = (float)CX[i] * ux + (float)CY[i] * uy + (float)CZ[i] * uz;
	return W[i] * (d + rho * (3.0f * cu + 4.5f * cu * cu - 1.5f * usq));
}

// one time step for every fluid and outlet cell: pull-stream from lattice a, collide, store in lattice b.
// p: the parent level's post-collision lattice (refined levels only; level 0 gets a dummy), sub = 1 (step A) or 2 (B)
kernel void stream_collide(FARG(a), FARG(b), FARG(p), global const uchar* restrict flags, const float om, const float ccx,
		const float ccy, const float ccz, const float tau0, const float csm, const int sub) {
	const uint n = get_global_id(0);
	if (n >= NCELLS) return;
	const uint fl = flags[n];
	if (fl & (F_SOLID | F_EQ | F_COVER)) return;
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
	const int x = (int)(n % NX), y = (int)((n / NX) % NY), z = (int)(n / (NX * NY));
	float g[19];
#ifdef PARENT
	if (fl & F_IF) { // explosion: upstream neighbours outside the box come from the parent (see the header)
		global fs* P[19] = FLIST(p);
#pragma unroll
		for (int i = 0; i < 19; i++) {
			const int xs = x - CX[i], ys = y - CY[i], zs = z - CZ[i];
			if (IN_BOX(xs, ys, zs)) g[i] = LD(A[i], IDX(xs, ys, zs));
			else g[i] = LD(P[i], PIDX(x - sub * CX[i], y - sub * CY[i], z - sub * CZ[i]));
		}
	} else
#endif
	{
#pragma unroll
		for (int i = 0; i < 19; i++) g[i] = LD(A[i], (uint)((int)n - OFS(i))); // f_i(x, t+1) = f*_i(x - c_i, t)
	}
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
	float tau = 0.5f * (tau0 + sqrt(tau0 * tau0 + cs_ * qn * ir)); // Smagorinsky: csm = 18 sqrt(2) Cs^2, filter = 1 cell of this level
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

#ifdef PARENT
// coalescence and corner clipping (see the header), run after the child's step A. One work item per parent cell of the
// covered box grown by one parent cell. p: parent post-collision lattice at parent time t (updated here); a: child
// lattice at child time t (post-collision, before step A); b: child lattice at t + 1/2 (after step A).
kernel void coalesce(FARG(p), FARG(a), FARG(b)) {
	const int SX = (int)NX / 2 + 2, SY = (int)NY / 2 + 2, SZ = (int)NZ / 2 + 2;
	const int id = (int)get_global_id(0);
	if (id >= SX * SY * SZ) return;
	const int sx = id % SX, sy = (id / SX) % SY, sz = id / (SX * SY); // shell coordinates: covered cells are 1..S-2
	const bool cov = sx >= 1 && sx <= SX - 2 && sy >= 1 && sy <= SY - 2 && sz >= 1 && sz <= SZ - 2;
	if (sx >= 2 && sx <= SX - 3 && sy >= 2 && sy <= SY - 3 && sz >= 2 && sz <= SZ - 3) return; // deep inside: no real neighbour
	global fs* P[19] = FLIST(p);
	global fs* A[19] = FLIST(a);
	global fs* B[19] = FLIST(b);
	const uint pn = (uint)(OX - 1 + sx) + PNX * ((uint)(OY - 1 + sy) + PNY * (uint)(OZ - 1 + sz));
	const int gx0 = 2 * (sx - 1), gy0 = 2 * (sy - 1), gz0 = 2 * (sz - 1); // first child cell of this parent cell
#pragma unroll
	for (int i = 1; i < 19; i++) {
		const int tx = sx + CX[i], ty = sy + CY[i], tz = sz + CZ[i];
		const bool tcov = tx >= 1 && tx <= SX - 2 && ty >= 1 && ty <= SY - 2 && tz >= 1 && tz <= SZ - 2;
		if (tcov) continue; // the target is covered: nobody pulls this population
		if (cov) { // coalescence: mean over the sub-cells g of the target of the child population arriving there
			float s = 0.0f;
			for (int k = 0; k < 8; k++) {
				const int gx = 2 * (tx - 1) + (k & 1), gy = 2 * (ty - 1) + ((k >> 1) & 1), gz = 2 * (tz - 1) + (k >> 2);
				const int hx = gx - CX[i], hy = gy - CY[i], hz = gz - CZ[i];
				if (IN_BOX(hx, hy, hz)) s += LD(B[i], IDX(hx, hy, hz));
				else s += LD(A[i], IDX(hx - CX[i], hy - CY[i], hz - CZ[i]));
			}
			ST(P[i], pn, 0.125f * s);
		} else { // corner clipping: sub-cells s whose s + c_i is a child cell took the parent value in step A
			float s = 0.0f;
			int m = 0;
			for (int k = 0; k < 8; k++) {
				const int qx = gx0 + (k & 1) + CX[i], qy = gy0 + ((k >> 1) & 1) + CY[i], qz = gz0 + (k >> 2) + CZ[i];
				if (IN_BOX(qx, qy, qz)) { s += LD(B[i], IDX(qx, qy, qz)); m++; }
			}
			if (m > 0) {
				const float v = LD(P[i], pn);
				ST(P[i], pn, v + 0.125f * (s - (float)m * v));
			}
		}
	}
}
#endif

// set both lattices to equilibrium: rho = 1, u = inflow (+ small hashed noise in fluid cells), wall velocity in solid cells
kernel void init_cells(FARG(a), FARG(b), global const uchar* restrict flags, const float uin, const float pert,
		const float om, const float ccx, const float ccy, const float ccz, const uint seed) {
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
		uint h = (n + seed) * 2654435761u + 0x9E3779B9u;
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
	if (fl & (F_EQ | F_OUT | F_COVER | F_IF)) return;
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
	if (fl & (F_EQ | F_OUT | F_COVER | F_IF)) return;
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
// average over every step between two samples). Split by the fluid cell p = x - c of the link (a fluid cell is never
// inside the wall, so |p| is beyond the outer or inside the inner radius except in a hole): hole walls when
// rlo2 < |p|^2 < rhi2 and p lies within sqrt(rw2) of a hole axis (axes[3 k], k < nh, unit, current spin angle; p.a > 0),
// else outer surface (|p|^2 >= rm2, the mid-wall radius) or inner surface; summed to parts[18 g + 6 s + k]
// (s = 0 outer, 1 inner, 2 holes).
kernel void body_force(FARG(a), global const uchar* restrict flags, const uint bx0, const uint by0, const uint bz0,
		const uint bx, const uint by, const uint bz, const float ccx, const float ccy, const float ccz, const float om,
		const uint acc, const float sg, global float* part, global float* partn, const float rm2, const float rlo2,
		const float rhi2, global const float* axes, const uint nh, const float rw2, global float* parts) {
	local float red[6 * WG];
	const uint id = get_global_id(0), lid = get_local_id(0);
	float v[18];
#pragma unroll
	for (int k = 0; k < 18; k++) v[k] = 0.0f;
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
					const float px = (float)x - ccx, py = (float)y - ccy, pz = (float)z - ccz, p2 = px * px + py * py + pz * pz;
					int s = p2 >= rm2 ? 0 : 6;
					if (p2 > rlo2 && p2 < rhi2) {
						for (uint k = 0u; k < nh; k++) {
							const float d = px * axes[3u * k] + py * axes[3u * k + 1u] + pz * axes[3u * k + 2u];
							if (d > 0.0f && p2 - d * d < rw2) { s = 12; break; }
						}
					}
					v[s] += dx; v[s + 1] += dy; v[s + 2] += dz;
					v[s + 3] += ry * dz - rz * dy; v[s + 4] += rz * dx - rx * dz; v[s + 5] += rx * dy - ry * dx;
				}
			}
		}
	}
	for (int pass = 0; pass < 4; pass++) { // passes 0-2: the three parts; pass 3: their sum
		for (int k = 0; k < 6; k++) red[k * WG + lid] = pass < 3 ? v[6 * pass + k] : v[k] + v[6 + k] + v[12 + k];
		barrier(CLK_LOCAL_MEM_FENCE);
		for (uint s = WG / 2u; s > 0u; s >>= 1) {
			if (lid < s) {
				for (uint k = 0u; k < 6u; k++) red[k * WG + lid] += red[k * WG + lid + s];
			}
			barrier(CLK_LOCAL_MEM_FENCE);
		}
		if (lid == 0u) {
			for (uint k = 0u; k < 6u; k++) {
				if (pass < 3) {
					const uint j = 18u * get_group_id(0) + 6u * (uint)pass + k;
					parts[j] = (acc ? parts[j] : 0.0f) + red[k * WG];
				} else {
					const uint j = 6u * get_group_id(0) + k;
					part[j] = (acc ? part[j] : 0.0f) + red[k * WG];
					partn[j] = (acc ? partn[j] : 0.0f) + sg * red[k * WG];
				}
			}
		}
		barrier(CLK_LOCAL_MEM_FENCE);
	}
}

// moments of one cell of lattice a: rho and u
inline float4 cell_u(global fs* A[19], const uint n) {
	float d = 0.0f, jx = 0.0f, jy = 0.0f, jz = 0.0f;
#pragma unroll
	for (int i = 0; i < 19; i++) {
		const float v = LD(A[i], n);
		d += v; jx += (float)CX[i] * v; jy += (float)CY[i] * v; jz += (float)CZ[i] * v;
	}
	const float rho = 1.0f + d, ir = 1.0f / rho;
	return (float4)(jx * ir, jy * ir, jz * ir, rho);
}

// hole and cavity diagnostics over the body box, from the lattice a (finest level, current time). Per work-group sums
// to dpart[NDG g + k]: k < nh: mass flux rho u.a_k of the fluid cells in the disc of hole k (slab |r.a_k - rmid| < 0.5,
// lateral distance^2 < rh2, |r|^2 < rl2; one cell thick, so the sum is the flux through the disc); then, over the fluid cells with
// |r|^2 < rc2 (cavity): count, sum |u|, sum |curl u| (central differences; cells with a solid neighbour skipped from
// this sum and counted in the next), count of cells in the vorticity sum, sum rho (r x u)_y, sum rho (rx^2 + rz^2).
#define NDG 34
kernel void diag(FARG(a), global const uchar* restrict flags, const uint bx0, const uint by0, const uint bz0,
		const uint bx, const uint by, const uint bz, const float ccx, const float ccy, const float ccz, const float rmid,
		const float rh2, const float rc2, global const float* axes, const uint nh, global float* dpart, const float rl2) {
	local float red[WG];
	const uint id = get_global_id(0), lid = get_local_id(0);
	int hk = -1;
	float hq = 0.0f, cn = 0.0f, cu = 0.0f, cw = 0.0f, cwn = 0.0f, cl = 0.0f, ci = 0.0f;
	if (id < bx * by * bz) {
		const uint x = bx0 + id % bx, y = by0 + (id / bx) % by, z = bz0 + id / (bx * by);
		const uint n = x + NX * (y + NY * z);
		const uint fl = flags[n];
		if (!(fl & (F_SOLID | F_EQ | F_OUT))) {
			global fs* A[19] = FLIST(a);
			const float rx = (float)x - ccx, ry = (float)y - ccy, rz = (float)z - ccz, r2 = rx * rx + ry * ry + rz * rz;
			const float r = sqrt(r2);
			if (r > rmid - 0.5f && r2 < rl2) { // rl2 = R^2: the whole disc (|s - rmid| < 0.5, r_perp < r_h) and no outer-flow cell
				for (uint k = 0u; k < nh && hk < 0; k++) {
					const float ax = axes[3u * k], ay = axes[3u * k + 1u], az = axes[3u * k + 2u];
					const float s = rx * ax + ry * ay + rz * az;
					if (fabs(s - rmid) < 0.5f && r2 - s * s < rh2) {
						const float4 u = cell_u(A, n);
						hk = (int)k;
						hq = u.w * (u.x * ax + u.y * ay + u.z * az);
					}
				}
			}
			if (r2 < rc2) {
				const float4 u = cell_u(A, n);
				cn = 1.0f;
				cu = sqrt(u.x * u.x + u.y * u.y + u.z * u.z);
				cl = u.w * (rz * u.x - rx * u.z);
				ci = u.w * (rx * rx + rz * rz);
				const uint sx = 1u, sy = NX, sz = NX * NY;
				if (!((flags[n + sx] | flags[n - sx] | flags[n + sy] | flags[n - sy] | flags[n + sz] | flags[n - sz]) & F_SOLID)) {
					const float4 xp = cell_u(A, n + sx), xm = cell_u(A, n - sx), yp = cell_u(A, n + sy), ym = cell_u(A, n - sy);
					const float4 zp = cell_u(A, n + sz), zm = cell_u(A, n - sz);
					const float wx = 0.5f * ((yp.z - ym.z) - (zp.y - zm.y));
					const float wy = 0.5f * ((zp.x - zm.x) - (xp.z - xm.z));
					const float wz = 0.5f * ((xp.y - xm.y) - (yp.x - ym.x));
					cw = sqrt(wx * wx + wy * wy + wz * wz);
					cwn = 1.0f;
				}
			}
		}
	}
	for (uint k = 0u; k < NDG; k++) {
		float v = 0.0f;
		if (k < nh) v = (int)k == hk ? hq : 0.0f;
		else if (k >= NDG - 6u) {
			const uint j = k - (NDG - 6u);
			v = j == 0u ? cn : j == 1u ? cu : j == 2u ? cw : j == 3u ? cwn : j == 4u ? cl : ci;
		}
		red[lid] = v;
		barrier(CLK_LOCAL_MEM_FENCE);
		for (uint s = WG / 2u; s > 0u; s >>= 1) {
			if (lid < s) red[lid] += red[lid + s];
			barrier(CLK_LOCAL_MEM_FENCE);
		}
		if (lid == 0u) dpart[NDG * get_group_id(0) + k] = red[0];
		barrier(CLK_LOCAL_MEM_FENCE);
	}
}
