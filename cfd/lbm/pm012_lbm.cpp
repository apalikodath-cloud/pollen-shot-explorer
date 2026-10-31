// PM-012 (FTC POLLEN Magnus project): own GPU lattice Boltzmann LES solver for flow past a smooth sphere or the POLLEN
// ball (binary STL), still or spinning about +y. Written for this project from the textbook method (no third-party
// source): D3Q19, two-lattice pull scheme, regularized (default) or BGK collision with a Smagorinsky subgrid model,
// halfway bounce-back with the moving-wall term (Ladd 1994), force and torque by momentum exchange; optional local grid
// refinement around the body (lv=2..4 nested boxes, factor 2 per level, sub-cycled, mass-conserving volumetric coupling
// after Rohde et al. 2006, Int. J. Numer. Meth. Fluids 51:439; see the header of pm012_lbm.cl).
// Kernels: pm012_lbm.cl. The OpenCL runtime (OpenCL.dll of the GPU driver, loaded from System32 at run time) is the
// only external code; the few OpenCL 1.2 types, constants and entry points used are declared below.
//
// Build: cfd/lbm/build.cmd (MSVC x64, output outside the repo). Usage: pm012_lbm.exe key=value ... (see usage()).
// Output: CSV in the format of cfd/fluidx3d/setup.cpp (header keys, columns step,tstar,Fx,Fy,Fz,Tx,Ty,Tz,Cd,Cy,Cl,CM),
// so cfd/postprocess.py reads it unchanged. Lattice units; coefficients use A = pi (D/2)^2, q = 0.5 u^2 A,
// Cd = Fx/q, Cy = Fy/q, Cl = Fz/q (spin about +y: backspin lift along +z), CM = -Ty/(q D/2).
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdarg>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <functional>
#include <map>
#include <string>
#include <vector>

// ---- minimal OpenCL 1.2 declarations (from the Khronos specification) ----
typedef int32_t cl_int;
typedef uint32_t cl_uint;
typedef uint64_t cl_ulong;
typedef cl_ulong cl_bitfield;
typedef cl_uint cl_bool;
typedef struct _cl_platform_id* cl_platform_id;
typedef struct _cl_device_id* cl_device_id;
typedef struct _cl_context* cl_context;
typedef struct _cl_command_queue* cl_command_queue;
typedef struct _cl_mem* cl_mem;
typedef struct _cl_program* cl_program;
typedef struct _cl_kernel* cl_kernel;
typedef struct _cl_event* cl_event;
typedef intptr_t cl_context_properties;
#define CL_SUCCESS 0
#define CL_DEVICE_TYPE_GPU ((cl_bitfield)1 << 2)
#define CL_DEVICE_GLOBAL_MEM_SIZE 0x101F
#define CL_DEVICE_MAX_MEM_ALLOC_SIZE 0x1010
#define CL_DEVICE_NAME 0x102B
#define CL_DEVICE_VERSION 0x102F
#define CL_CONTEXT_PLATFORM 0x1084
#define CL_MEM_READ_WRITE ((cl_bitfield)1 << 0)
#define CL_PROGRAM_BUILD_LOG 0x1183
#define CL_TRUE 1
#define CLAPI __stdcall
typedef cl_int(CLAPI* P_GetPlatformIDs)(cl_uint, cl_platform_id*, cl_uint*);
typedef cl_int(CLAPI* P_GetDeviceIDs)(cl_platform_id, cl_bitfield, cl_uint, cl_device_id*, cl_uint*);
typedef cl_int(CLAPI* P_GetDeviceInfo)(cl_device_id, cl_uint, size_t, void*, size_t*);
typedef cl_context(CLAPI* P_CreateContext)(const cl_context_properties*, cl_uint, const cl_device_id*,
	void(CLAPI*)(const char*, const void*, size_t, void*), void*, cl_int*);
typedef cl_command_queue(CLAPI* P_CreateCommandQueue)(cl_context, cl_device_id, cl_bitfield, cl_int*);
typedef cl_mem(CLAPI* P_CreateBuffer)(cl_context, cl_bitfield, size_t, void*, cl_int*);
typedef cl_program(CLAPI* P_CreateProgramWithSource)(cl_context, cl_uint, const char**, const size_t*, cl_int*);
typedef cl_int(CLAPI* P_BuildProgram)(cl_program, cl_uint, const cl_device_id*, const char*, void(CLAPI*)(cl_program, void*), void*);
typedef cl_int(CLAPI* P_GetProgramBuildInfo)(cl_program, cl_device_id, cl_uint, size_t, void*, size_t*);
typedef cl_kernel(CLAPI* P_CreateKernel)(cl_program, const char*, cl_int*);
typedef cl_int(CLAPI* P_SetKernelArg)(cl_kernel, cl_uint, size_t, const void*);
typedef cl_int(CLAPI* P_EnqueueNDRangeKernel)(cl_command_queue, cl_kernel, cl_uint, const size_t*, const size_t*, const size_t*,
	cl_uint, const cl_event*, cl_event*);
typedef cl_int(CLAPI* P_EnqueueReadBuffer)(cl_command_queue, cl_mem, cl_bool, size_t, size_t, void*, cl_uint, const cl_event*, cl_event*);
typedef cl_int(CLAPI* P_EnqueueWriteBuffer)(cl_command_queue, cl_mem, cl_bool, size_t, size_t, const void*, cl_uint, const cl_event*, cl_event*);
typedef cl_int(CLAPI* P_Finish)(cl_command_queue);

static struct {
	P_GetPlatformIDs GetPlatformIDs; P_GetDeviceIDs GetDeviceIDs; P_GetDeviceInfo GetDeviceInfo; P_CreateContext CreateContext;
	P_CreateCommandQueue CreateCommandQueue; P_CreateBuffer CreateBuffer; P_CreateProgramWithSource CreateProgramWithSource;
	P_BuildProgram BuildProgram; P_GetProgramBuildInfo GetProgramBuildInfo; P_CreateKernel CreateKernel; P_SetKernelArg SetKernelArg;
	P_EnqueueNDRangeKernel EnqueueNDRangeKernel; P_EnqueueReadBuffer EnqueueReadBuffer; P_EnqueueWriteBuffer EnqueueWriteBuffer;
	P_Finish Finish;
} cl;

[[noreturn]] static void die(const char* fmt, ...) {
	va_list ap; va_start(ap, fmt); fprintf(stderr, "pm012_lbm: "); vfprintf(stderr, fmt, ap); va_end(ap); fputc('\n', stderr);
	exit(2);
}
#define CK(call) do { const cl_int e_ = (call); if (e_ != CL_SUCCESS) die("OpenCL error %d in %s (line %d)", (int)e_, #call, __LINE__); } while (0)

static void load_opencl() {
	HMODULE h = LoadLibraryExA("OpenCL.dll", nullptr, 0x00000800 /* LOAD_LIBRARY_SEARCH_SYSTEM32 */);
	if (!h) die("cannot load OpenCL.dll from System32");
#define GETP(name) cl.name = (P_##name)(void*)GetProcAddress(h, "cl" #name); if (!cl.name) die("OpenCL.dll lacks cl" #name)
	GETP(GetPlatformIDs); GETP(GetDeviceIDs); GETP(GetDeviceInfo); GETP(CreateContext); GETP(CreateCommandQueue);
	GETP(CreateBuffer); GETP(CreateProgramWithSource); GETP(BuildProgram); GETP(GetProgramBuildInfo); GETP(CreateKernel);
	GETP(SetKernelArg); GETP(EnqueueNDRangeKernel); GETP(EnqueueReadBuffer); GETP(EnqueueWriteBuffer); GETP(Finish);
#undef GETP
}

// ---- arguments ----
static std::map<std::string, std::string> g_arg;
static std::string arg_s(const char* k, const std::string& def) { const auto it = g_arg.find(k); return it == g_arg.end() ? def : it->second; }
static double arg_d(const char* k, double def) {
	const auto it = g_arg.find(k);
	if (it == g_arg.end()) return def;
	char* e = nullptr;
	const double v = strtod(it->second.c_str(), &e);
	if (e == it->second.c_str() || *e != '\0' || !std::isfinite(v)) die("argument %s=%s is not a number", k, it->second.c_str());
	return v;
}

static void usage() {
	printf("pm012_lbm.exe key=value ...\n"
		"  body=sphere|stl|rotstokes|none|masstest  smooth sphere, POLLEN binary STL (mm), or sphere spinning in still fluid (torque check)\n"
		"  D=48 body diameter in cells   Re=3e4 (u D/nu)   u=0.05 inflow (lattice)   S=0 spin ratio omega R/u about +y\n"
		"  Lx,Ly,Lz=6,4,4 box in D (rotstokes 4,4,4)   xc=2 body centre from the inlet in D   T=55 run length in D/u (rotstokes R^2/nu: 40)\n"
		"  every=<steps> sampling (default about 50 per D/u)   out=run.csv   cl=<path of pm012_lbm.cl> (default: next to the exe)\n"
		"  prec=fp16|fp32 (default fp16; rotstokes fp32)   coll=reg|bgk (default reg)   Cs=0.1 Smagorinsky   outlet=p|eq (default p)\n"
		"  stl=<path> Dmm=71.12 (outer diameter mapped to D)   rx,ry,rz=<deg> static orientation (about x, then y, then z)\n"
		"  ref=4 occupancy voxels per cell   revox=<steps> geometry update interval of a spinning STL (default: wall moves <= 0.1 cell)\n"
		"  svol=22312.36 STL enclosed volume in mm^3 (check)   pert=1e-3 initial noise (fraction of u)   wg=128 work-group size\n"
		"  favg=1 each CSV row averages the force over every step since the previous row (0: instantaneous sample)\n"
		"  bulk=<omega> relaxation rate of the bulk (trace) part of the stress, regularized only (default: same as shear)\n"
		"  csn=<Cs> Smagorinsky constant of the wall cells (default Cs)   taun=<tau> lower bound of tau in the wall cells\n"
		"  rotstokes: uw=0.005 wall speed omega R, nu=0.2 (finest level)   platform=0 device=0 (GPU index on that OpenCL platform)\n"
		"  grid refinement: lv=1 number of levels (1 = uniform grid; 2..4 nested boxes around the body, factor 2 each).\n"
		"    D is the FINEST level's cells per diameter; Lx,Ly,Lz,xc describe the coarsest level (level 0, D/2^(lv-1)).\n"
		"    fb=0.7,1.5,0.7 finest box in D around the body centre: upstream, downstream, lateral half width (rotstokes 0.8,0.8,0.8)\n"
		"    gb=0.5,1.0,0.4 added per coarser refined level   plan=1 print levels, cells and memory, then exit (no GPU)\n"
		"  body=none (no body: uniform-flow check) or body=masstest (closed box with bounce-back walls: total-mass check)\n"
		"  seed=0 offset of the initial-noise hash\n"
		"  hole and cavity diagnostics (sphere and stl): holes=<holes.json of stl_holes.py> (hole axes, CAD frame)\n"
		"    wall_mm=1.778 shell wall   hole_mm=11.2 disc diameter for the through-hole flux (mid-wall, normal to the hole axis)\n"
		"    each CSV row gets a '# dg ...' line; a '# dg_avg ...' footer line averages the rows with t* >= 15\n");
}

// ---- STL occupancy grid (body frame, cell units, centred on the ball centre) ----
struct Occ { int M = 0; double h = 0.25, rg = 0.0; std::vector<uint8_t> v; long long odd_rays = 0, rays = 0; double vol_cells = 0.0; };

static std::vector<double> load_stl_cells(const std::string& path, double scale, const double Rm[9], uint32_t& ntri, double bbc[3]) {
	FILE* f = fopen(path.c_str(), "rb");
	if (!f) die("cannot open STL %s", path.c_str());
	_fseeki64(f, 0, SEEK_END);
	const long long sz = _ftelli64(f);
	_fseeki64(f, 0, SEEK_SET);
	unsigned char hdr[84];
	if (fread(hdr, 1, 84, f) != 84) die("STL %s too short", path.c_str());
	memcpy(&ntri, hdr + 80, 4);
	if (ntri == 0u || ntri > 20000000u || sz != 84LL + 50LL * (long long)ntri) die("%s is not a binary STL (%lld bytes, %u triangles)", path.c_str(), sz, ntri);
	std::vector<unsigned char> buf((size_t)ntri * 50u);
	if (fread(buf.data(), 1, buf.size(), f) != buf.size()) die("STL read failed");
	fclose(f);
	double lo[3] = { 1e300, 1e300, 1e300 }, hi[3] = { -1e300, -1e300, -1e300 };
	std::vector<double> V((size_t)ntri * 9u);
	for (size_t t = 0; t < ntri; t++) {
		float p[9];
		memcpy(p, &buf[t * 50u + 12u], 36);
		for (int k = 0; k < 9; k++) {
			if (!std::isfinite(p[k])) die("STL has a non-finite vertex");
			lo[k % 3] = std::min(lo[k % 3], (double)p[k]); hi[k % 3] = std::max(hi[k % 3], (double)p[k]);
		}
		for (int j = 0; j < 3; j++) {
			const double a = p[3 * j], b = p[3 * j + 1], c = p[3 * j + 2];
			for (int k = 0; k < 3; k++) V[t * 9u + 3u * j + k] = scale * (Rm[3 * k] * a + Rm[3 * k + 1] * b + Rm[3 * k + 2] * c);
		}
	}
	for (int k = 0; k < 3; k++) bbc[k] = 0.5 * (lo[k] + hi[k]);
	return V;
}

static Occ voxelize(const std::vector<double>& V, uint32_t ntri, int ref) {
	Occ o;
	double rmax = 0.0;
	for (size_t i = 0; i < V.size(); i += 3) rmax = std::max(rmax, std::sqrt(V[i] * V[i] + V[i + 1] * V[i + 1] + V[i + 2] * V[i + 2]));
	o.h = 1.0 / ref;
	o.rg = rmax + 2.0 * o.h;
	o.M = (int)std::ceil(2.0 * o.rg / o.h);
	o.v.assign((size_t)o.M * o.M * o.M, 0u);
	const int nb = (int)std::ceil(2.0 * o.rg); // 2D bins (y, z) of one cell
	std::vector<std::vector<uint32_t>> bins((size_t)nb * nb);
	for (uint32_t t = 0; t < ntri; t++) {
		const double* a = &V[(size_t)t * 9u];
		const double y0 = std::min({ a[1], a[4], a[7] }), y1 = std::max({ a[1], a[4], a[7] });
		const double z0 = std::min({ a[2], a[5], a[8] }), z1 = std::max({ a[2], a[5], a[8] });
		const int iy0 = std::max(0, (int)std::floor(y0 + o.rg)), iy1 = std::min(nb - 1, (int)std::floor(y1 + o.rg));
		const int iz0 = std::max(0, (int)std::floor(z0 + o.rg)), iz1 = std::min(nb - 1, (int)std::floor(z1 + o.rg));
		for (int iz = iz0; iz <= iz1; iz++) for (int iy = iy0; iy <= iy1; iy++) bins[(size_t)iz * nb + iy].push_back(t);
	}
	std::vector<double> xs;
	long long filled = 0;
	for (int kz = 0; kz < o.M; kz++) for (int ky = 0; ky < o.M; ky++) {
		o.rays++;
		bool even = false;
		for (int attempt = 0; attempt < 4 && !even; attempt++) { // jittered ray along +x; retry on odd parity
			const double yr = -o.rg + (ky + 0.5) * o.h + o.h * 1e-4 * (0.7071067811865476 + 0.618 * attempt);
			const double zr = -o.rg + (kz + 0.5) * o.h + o.h * 1e-4 * (0.5772156649015329 - 0.414 * attempt);
			const int iy = (int)std::floor(yr + o.rg), iz = (int)std::floor(zr + o.rg);
			xs.clear();
			if (iy >= 0 && iz >= 0 && iy < nb && iz < nb) {
				for (const uint32_t t : bins[(size_t)iz * nb + iy]) {
					const double* a = &V[(size_t)t * 9u];
					const double d = (a[4] - a[1]) * (a[8] - a[2]) - (a[7] - a[1]) * (a[5] - a[2]);
					if (d == 0.0) continue; // triangle edge-on to the ray
					const double l1 = ((yr - a[1]) * (a[8] - a[2]) - (a[7] - a[1]) * (zr - a[2])) / d;
					const double l2 = ((a[4] - a[1]) * (zr - a[2]) - (yr - a[1]) * (a[5] - a[2])) / d;
					const double l0 = 1.0 - l1 - l2;
					if (l0 < 0.0 || l1 < 0.0 || l2 < 0.0) continue;
					xs.push_back(l0 * a[0] + l1 * a[3] + l2 * a[6]);
				}
			}
			even = (xs.size() % 2u) == 0u;
		}
		if (!even) { o.odd_rays++; xs.pop_back(); }
		std::sort(xs.begin(), xs.end());
		for (size_t p = 0; p + 1 < xs.size(); p += 2) {
			const int k0 = std::max(0, (int)std::ceil((xs[p] + o.rg) / o.h - 0.5));
			const int k1 = std::min(o.M - 1, (int)std::floor((xs[p + 1] + o.rg) / o.h - 0.5));
			for (int kx = k0; kx <= k1; kx++) { o.v[(size_t)kx + (size_t)o.M * ((size_t)ky + (size_t)o.M * kz)] = 1u; filled++; }
		}
	}
	o.vol_cells = (double)filled * o.h * o.h * o.h;
	return o;
}

static void rot_xyz(double rx, double ry, double rz, double R[9]) { // R = Rz(rz) Ry(ry) Rx(rx), degrees, right-handed
	const double d = 3.14159265358979323846 / 180.0;
	const double cx = cos(rx * d), sx = sin(rx * d), cy = cos(ry * d), sy = sin(ry * d), cz = cos(rz * d), sz = sin(rz * d);
	const double X[9] = { 1, 0, 0, 0, cx, -sx, 0, sx, cx }, Y[9] = { cy, 0, sy, 0, 1, 0, -sy, 0, cy }, Z[9] = { cz, -sz, 0, sz, cz, 0, 0, 0, 1 };
	double T[9];
	for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++) { T[3 * i + j] = 0; for (int k = 0; k < 3; k++) T[3 * i + j] += Y[3 * i + k] * X[3 * k + j]; }
	for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++) { R[3 * i + j] = 0; for (int k = 0; k < 3; k++) R[3 * i + j] += Z[3 * i + k] * T[3 * k + j]; }
}

static cl_kernel make_kernel(cl_program p, const char* name) {
	cl_int e = 0;
	cl_kernel k = cl.CreateKernel(p, name, &e);
	if (e != CL_SUCCESS || !k) die("clCreateKernel(%s) failed: %d", name, (int)e);
	return k;
}
struct ArgSetter {
	cl_kernel k; cl_uint i = 0;
	explicit ArgSetter(cl_kernel kk) : k(kk) {}
	template <class T> ArgSetter& operator()(const T& v) { CK(cl.SetKernelArg(k, i, sizeof(T), &v)); i++; return *this; }
	ArgSetter& lattice(const cl_mem* f) { for (int d = 0; d < 19; d++) (*this)(f[d]); return *this; }
};

static float half_to_float(uint16_t h) { // IEEE binary16 -> float (host readback of FP16 lattices)
	const uint32_t s = (uint32_t)(h & 0x8000u) << 16, e = (h >> 10) & 0x1Fu, m = h & 0x3FFu;
	if (e == 0u) { const float v = std::ldexp((float)m, -24); return s ? -v : v; }
	const uint32_t bits = e == 31u ? (s | 0x7F800000u | (m << 13)) : (s | ((e + 112u) << 23) | (m << 13));
	float f;
	memcpy(&f, &bits, 4);
	return f;
}

// one grid level: a dense box. Level 0 is the whole domain; level l >= 1 covers whole cells of level l-1, starting at
// parent cell (o[0], o[1], o[2]), each split into 2x2x2 cells.
struct Level {
	uint32_t n[3] = { 0, 0, 0 };
	uint64_t N = 0;
	int o[3] = { 0, 0, 0 };
	double D = 0, nu = 0, tau0 = 0, cc[3] = { 0, 0, 0 }, ext[3] = { 0, 0, 0 };
	cl_program prog = nullptr;
	cl_mem f[2][19] = {};
	cl_mem flags = nullptr;
	cl_kernel sc[2][2] = {};   // [own lattice holding time t][parent lattice holding the parent's time t]
	cl_kernel coal[2][2] = {}; // l >= 1: [parent lattice][own lattice holding t + 1/2]
	cl_kernel init = nullptr;
	size_t ncoal = 0;
};

int main(int argc, char** argv) {
	for (int i = 1; i < argc; i++) {
		const std::string s = argv[i];
		if (s == "-h" || s == "--help" || s == "help") { usage(); return 0; }
		const size_t e = s.find('=');
		if (e == std::string::npos || e == 0) die("argument \"%s\" is not key=value (try help)", s.c_str());
		g_arg[s.substr(0, e)] = s.substr(e + 1);
	}
	static const char* known[] = { "body", "D", "Re", "u", "S", "Lx", "Ly", "Lz", "xc", "T", "every", "out", "cl", "prec", "coll", "Cs",
		"outlet", "stl", "Dmm", "rx", "ry", "rz", "ref", "revox", "svol", "pert", "wg", "uw", "nu", "platform", "device", "favg", "bulk", "csn",
		"taun", "lv", "fb", "gb", "plan", "seed", "holes", "wall_mm", "hole_mm" };
	for (const auto& kv : g_arg) {
		bool ok = false;
		for (const char* k : known) ok = ok || kv.first == k;
		if (!ok) die("unknown argument %s (try help)", kv.first.c_str());
	}
	const std::string body = arg_s("body", "sphere");
	const bool stokes = body == "rotstokes", use_stl = body == "stl", mtest = body == "masstest", nobody = body == "none" || mtest;
	if (!stokes && !use_stl && !nobody && body != "sphere") die("body must be sphere, stl, rotstokes, none or masstest");
	const int L = (int)arg_d("lv", 1.0);
	if (L < 1 || L > 4) die("lv must be 1..4");
	const double ratio = (double)(1 << (L - 1));
	const double D = arg_d("D", 48.0), R = 0.5 * D, D0 = D / ratio;
	const double u = stokes ? 0.0 : arg_d("u", 0.05);
	const double Re = arg_d("Re", 3.0e4), S = (stokes || nobody) ? 0.0 : arg_d("S", 0.0);
	const double uw = stokes ? arg_d("uw", 0.005) : S * u, omega = uw / R; // omega in finest-level lattice units
	const double nu = stokes ? arg_d("nu", 0.2) : u * D / Re;              // finest-level lattice viscosity
	const double Lx = arg_d("Lx", stokes ? 4.0 : 6.0), Ly = arg_d("Ly", 4.0), Lz = arg_d("Lz", 4.0);
	const double xc = arg_d("xc", stokes ? 0.5 * Lx : 2.0);
	const std::string prec = arg_s("prec", stokes || mtest ? "fp32" : "fp16"), coll = arg_s("coll", "reg"), outlet = arg_s("outlet", "p");
	if (prec != "fp16" && prec != "fp32") die("prec must be fp16 or fp32");
	if (coll != "reg" && coll != "bgk") die("coll must be reg or bgk");
	if (outlet != "p" && outlet != "eq") die("outlet must be p or eq");
	const double Cs = arg_d("Cs", 0.1), csm = 18.0 * std::sqrt(2.0) * Cs * Cs;
	const double csn = arg_d("csn", Cs), bulk = arg_d("bulk", 0.0), taun = arg_d("taun", 0.0);
	if (csn < 0.0 || bulk < 0.0 || bulk >= 2.0 || taun < 0.0 || taun > 2.0) die("csn, bulk or taun out of range");
	if (bulk > 0.0 && coll != "reg") die("bulk needs coll=reg");
	const bool favg = arg_d("favg", 1.0) != 0.0;
	const double pert = stokes ? 0.0 : arg_d("pert", 1e-3);
	const int wg = (int)arg_d("wg", 128.0);
	if (wg < 32 || wg > 1024 || (wg & (wg - 1))) die("wg must be a power of two in 32..1024");
	if (D0 < 8.0 || D > 1600.0 || u < 0.0 || u > 0.15 || nu <= 0.0) die("D, u or nu out of range (coarsest level needs D/2^(lv-1) >= 8)");
	auto triple = [&](const char* k, const double def[3], double v[3]) {
		const std::string s = arg_s(k, "");
		for (int i = 0; i < 3; i++) v[i] = def[i];
		if (s.empty()) return;
		if (sscanf(s.c_str(), "%lf,%lf,%lf", &v[0], &v[1], &v[2]) != 3 || v[0] <= 0 || v[1] <= 0 || v[2] <= 0) die("%s needs three positive numbers a,b,c", k);
	};
	const double fb_def[3] = { stokes ? 0.8 : 0.7, stokes ? 0.8 : 1.5, stokes ? 0.8 : 0.7 }, gb_def[3] = { 0.5, 1.0, 0.4 };
	double fb[3], gb[3];
	triple("fb", fb_def, fb);
	triple("gb", gb_def, gb);
	if (L > 1 && coll == "reg" && u * D0 / Re < 1e-3)
		printf("WARNING: coll=reg with lv > 1 at low viscosity grew a disturbance at the box interface in the uniform-flow check; use coll=bgk\n");

	// ---- levels ----
	std::vector<Level> lv(L);
	{
		Level& c = lv[0];
		c.n[0] = 2u * (uint32_t)std::lround(0.5 * Lx * D0); c.n[1] = 2u * (uint32_t)std::lround(0.5 * Ly * D0); c.n[2] = 2u * (uint32_t)std::lround(0.5 * Lz * D0);
		c.D = D0;
		c.cc[0] = stokes ? 0.5 * c.n[0] - 0.5 : std::floor(xc * D0) - 0.5; c.cc[1] = 0.5 * c.n[1] - 0.5; c.cc[2] = 0.5 * c.n[2] - 0.5; // cell corner
		c.ext[0] = Lx; c.ext[1] = Ly; c.ext[2] = Lz;
	}
	for (int l = 1; l < L; l++) {
		const Level& p = lv[l - 1];
		Level& c = lv[l];
		const double k = (double)(L - 1 - l);
		const double xm = fb[0] + k * gb[0], xp = fb[1] + k * gb[1], rr = fb[2] + k * gb[2];
		const double lo_d[3] = { xm, rr, rr }, hi_d[3] = { xp, rr, rr };
		for (int a = 0; a < 3; a++) {
			const int cpar = (int)std::lround(p.cc[a] + 0.5); // the body centre is the corner between parent cells cpar-1 and cpar
			const int s = cpar - (int)std::ceil(lo_d[a] * p.D), e = cpar + (int)std::ceil(hi_d[a] * p.D);
			if (s < 4 || e > (int)p.n[a] - 4) die("level %d box (fb/gb) does not fit inside level %d with a 4-cell margin (axis %d)", l, l - 1, a);
			c.o[a] = s;
			c.n[a] = 2u * (uint32_t)(e - s);
			c.cc[a] = 2.0 * (cpar - s) - 0.5;
			c.ext[a] = (double)(e - s) / p.D;
		}
		c.D = 2.0 * p.D;
	}
	for (int l = 0; l < L; l++) {
		Level& c = lv[l];
		c.N = (uint64_t)c.n[0] * c.n[1] * c.n[2];
		if (c.N >= 0x7FFFFFFFull) die("too many cells on level %d (%llu)", l, (unsigned long long)c.N);
		c.nu = stokes ? nu / (double)(1 << (L - 1 - l)) : u * c.D / Re; // same physical viscosity: nu_lattice ~ 1/dx
		c.tau0 = 3.0 * c.nu + 0.5;
	}
	Level& F = lv[L - 1]; // the finest level holds the body
	const double* cc = F.cc;
	const uint32_t Nx = F.n[0], Ny = F.n[1], Nz = F.n[2];
	const double tau0 = F.tau0;
	const double tunit = stokes ? R * R / nu : D / u; // in finest steps
	const uint64_t rat = (uint64_t)ratio;
	uint64_t steps = (uint64_t)std::llround(arg_d("T", stokes ? 40.0 : 55.0) * tunit);
	steps = ((steps + rat - 1) / rat) * rat;
	const bool spin_mesh = use_stl && omega != 0.0;
	uint64_t revox = (uint64_t)arg_d("revox", std::max(1.0, std::floor(0.1 / std::max(std::fabs(uw), 1e-9))));
	if (revox < 1) revox = 1;
	uint64_t every = (uint64_t)arg_d("every", std::max(1.0, std::round(tunit / 50.0)));
	if (every < 1) every = 1;
	uint64_t mstep = rat;
	if (spin_mesh) { uint64_t a = rat, b = revox; while (b) { const uint64_t t = a % b; a = b; b = t; } mstep = rat / a * revox; }
	every = ((every + mstep - 1) / mstep) * mstep;
	if (favg && every % 2u == 1u) every += mstep; // even: a period-2 force oscillation cancels in each row
	const std::string out = arg_s("out", "pm012_run.csv");
	std::string clpath = arg_s("cl", "");
	if (clpath.empty()) {
		char exe[MAX_PATH];
		const DWORD Lp = GetModuleFileNameA(nullptr, exe, MAX_PATH);
		std::string p(exe, Lp);
		clpath = p.substr(0, p.find_last_of("\\/") + 1) + "pm012_lbm.cl";
	}

	// ---- geometry on the host: STL occupancy grid (finest-level cell units) ----
	const double Dmm = arg_d("Dmm", 71.12), svol = arg_d("svol", 22312.36);
	Occ occ;
	uint32_t ntri = 0;
	double bbc[3] = { 0, 0, 0 }, rbody = R;
	const bool plan = arg_d("plan", 0.0) != 0.0;
	if (use_stl && !plan) {
		const std::string stl = arg_s("stl", "");
		if (stl.empty()) die("body=stl needs stl=<path>");
		double Rm[9];
		rot_xyz(arg_d("rx", 0.0), arg_d("ry", 0.0), arg_d("rz", 0.0), Rm);
		const std::vector<double> V = load_stl_cells(stl, D / Dmm, Rm, ntri, bbc);
		const auto t0 = std::chrono::steady_clock::now();
		const int ref_def = std::max(1, std::min(4, (int)std::lround(376.0 / D))); // occupancy grid about 400^3 at most
		occ = voxelize(V, ntri, (int)arg_d("ref", (double)ref_def));
		rbody = occ.rg;
		printf("STL: %u triangles, bbox centre (%.4f, %.4f, %.4f) mm, occupancy %d^3 voxels of %.3f cells, volume/STL volume %.4f, odd rays %lld/%lld (%.1f s)\n",
			ntri, bbc[0], bbc[1], bbc[2], occ.M, occ.h, occ.vol_cells / (svol * std::pow(D / Dmm, 3.0)), occ.odd_rays, occ.rays,
			std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count());
	} else if (use_stl) rbody = R + 1.0;

	// ---- hole and cavity diagnostics: hole axes (CAD frame, unit vectors) turned by rx, ry, rz like the STL ----
	const bool dgon = (use_stl || body == "sphere") && u > 0.0;
	std::vector<double> haxes; // 3 per hole, lattice frame at spin angle 0
	const std::string hpath = arg_s("holes", "");
	if (!hpath.empty() && dgon) {
		FILE* f = fopen(hpath.c_str(), "rb");
		if (!f) die("cannot open %s", hpath.c_str());
		std::string js;
		char b[4096];
		size_t r;
		while ((r = fread(b, 1, sizeof(b), f)) > 0) js.append(b, r);
		fclose(f);
		size_t p = js.find("\"hole_axes\"");
		if (p == std::string::npos) die("%s has no hole_axes", hpath.c_str());
		p = js.find('[', p);
		size_t e = std::string::npos;
		for (size_t i = p, depth = 0; p != std::string::npos && i < js.size(); i++) { // the matching closing bracket
			if (js[i] == '[') depth++;
			else if (js[i] == ']' && --depth == 0) { e = i; break; }
		}
		if (p == std::string::npos || e == std::string::npos) die("cannot read hole_axes in %s", hpath.c_str());
		std::vector<double> a;
		const char* c = js.c_str() + p;
		const char* ce = js.c_str() + e;
		while (c < ce) {
			if ((*c >= '0' && *c <= '9') || *c == '-' || *c == '.') { char* q = nullptr; a.push_back(strtod(c, &q)); c = q; }
			else c++;
		}
		if (a.empty() || a.size() % 3u != 0u || a.size() / 3u > 28u) die("hole_axes in %s: need 1..28 triples", hpath.c_str());
		double Rm[9];
		rot_xyz(arg_d("rx", 0.0), arg_d("ry", 0.0), arg_d("rz", 0.0), Rm);
		for (size_t h = 0; h < a.size(); h += 3) {
			const double n = std::sqrt(a[h] * a[h] + a[h + 1] * a[h + 1] + a[h + 2] * a[h + 2]);
			for (int k = 0; k < 3; k++) haxes.push_back((Rm[3 * k] * a[h] + Rm[3 * k + 1] * a[h + 1] + Rm[3 * k + 2] * a[h + 2]) / n);
		}
	}
	const uint32_t nh = (uint32_t)(haxes.size() / 3u);
	const double cpm = D / Dmm; // finest cells per mm (the outer diameter Dmm maps to D)
	const double wall_c = arg_d("wall_mm", 1.778) * cpm, Rin = R - wall_c, rmid = R - 0.5 * wall_c, rh = 0.5 * arg_d("hole_mm", 11.2) * cpm;
	if (wall_c <= 0.0 || Rin <= 2.0 || rh <= 0.0) die("wall_mm or hole_mm out of range");
	const int pad = 3, mrg = L > 1 ? 4 : 1;
	int lo[3], hi[3];
	for (int k = 0; k < 3; k++) {
		lo[k] = (int)std::floor(cc[k] - rbody) - pad;
		hi[k] = (int)std::ceil(cc[k] + rbody) + pad;
		if (!nobody && (lo[k] < mrg || hi[k] > (int)F.n[k] - 1 - mrg)) die("body does not fit the %s box (axis %d)", L > 1 ? "finest-level" : "", k);
		lo[k] = std::max(lo[k], 1); hi[k] = std::min(hi[k], (int)F.n[k] - 2);
	}
	const cl_uint bx0 = lo[0], by0 = lo[1], bz0 = lo[2], bx = hi[0] - lo[0] + 1, by = hi[1] - lo[1] + 1, bz = hi[2] - lo[2] + 1;
	const size_t nbox = (size_t)bx * by * bz;

	// ---- memory plan ----
	const size_t es = prec == "fp16" ? 2u : 4u;
	double need = (double)occ.v.size(), maxbuf = 0.0, upd = 0.0;
	printf("levels (D = cells per body diameter; box in body diameters; memory = 2 lattices x 19 + flags):\n");
	for (int l = 0; l < L; l++) {
		const Level& c = lv[l];
		const double mem = 38.0 * (double)c.N * es + (double)c.N;
		need += mem;
		maxbuf = std::max(maxbuf, (double)c.N * es);
		upd += (double)c.N * (double)(1 << l);
		printf("  L%d: D=%g dx=%.4g mm  %ux%ux%u = %.2f M cells  box %.2fx%.2fx%.2f D  origin(parent) %d,%d,%d  nu=%.4g tau0=%.6f  %.0f MiB (buffer %.1f MiB)\n",
			l, c.D, use_stl ? Dmm / c.D : 71.12 / c.D, c.n[0], c.n[1], c.n[2], c.N * 1e-6, c.ext[0], c.ext[1], c.ext[2], c.o[0], c.o[1], c.o[2],
			c.nu, c.tau0, mem / 1048576.0, (double)c.N * es / 1048576.0);
	}
	printf("  total %.0f MiB, largest buffer %.1f MiB, %.1f M cell updates per level-0 step, finest box margin %g..%g cells from the body\n",
		need / 1048576.0, maxbuf / 1048576.0, upd * 1e-6, (double)std::min({ lo[0], lo[1], lo[2] }), (double)std::min({ (int)Nx - 1 - hi[0], (int)Ny - 1 - hi[1], (int)Nz - 1 - hi[2] }));
	printf("  finest dx = D/%g: %.2f-%.2f cells across a 10.2-11.2 mm hole, %.2f cells across the 1.778 mm wall (POLLEN scale)\n",
		D, 10.2 * D / 71.12, 11.2 * D / 71.12, 1.778 * D / 71.12);
	printf("need_mib=%.0f\n", need / 1048576.0 + 64.0);
	fflush(stdout);
	if (plan) return 0;

	// ---- OpenCL setup ----
	load_opencl();
	cl_uint np = 0;
	CK(cl.GetPlatformIDs(0, nullptr, &np));
	std::vector<cl_platform_id> plats(np);
	CK(cl.GetPlatformIDs(np, plats.data(), nullptr));
	const int pi = (int)arg_d("platform", 0.0), di = (int)arg_d("device", 0.0);
	if (pi < 0 || pi >= (int)np) die("no OpenCL platform %d", pi);
	cl_uint nd = 0;
	CK(cl.GetDeviceIDs(plats[pi], CL_DEVICE_TYPE_GPU, 0, nullptr, &nd));
	std::vector<cl_device_id> devs(nd);
	CK(cl.GetDeviceIDs(plats[pi], CL_DEVICE_TYPE_GPU, nd, devs.data(), nullptr));
	if (di < 0 || di >= (int)nd) die("no GPU %d on platform %d", di, pi);
	cl_device_id dev = devs[di];
	char dname[256] = { 0 };
	cl_ulong gmem = 0, amax = 0;
	CK(cl.GetDeviceInfo(dev, CL_DEVICE_NAME, sizeof(dname) - 1, dname, nullptr));
	CK(cl.GetDeviceInfo(dev, CL_DEVICE_GLOBAL_MEM_SIZE, sizeof(gmem), &gmem, nullptr));
	CK(cl.GetDeviceInfo(dev, CL_DEVICE_MAX_MEM_ALLOC_SIZE, sizeof(amax), &amax, nullptr));
	if (maxbuf > (double)amax || need > 0.92 * (double)gmem) die("needs %.2f GB (device %.2f GB, max buffer %.2f GB)", need * 1e-9, gmem * 1e-9, amax * 1e-9);
	const cl_context_properties props[3] = { CL_CONTEXT_PLATFORM, (cl_context_properties)plats[pi], 0 };
	cl_int err = 0;
	cl_context ctx = cl.CreateContext(props, 1, &dev, nullptr, nullptr, &err);
	if (err != CL_SUCCESS) die("clCreateContext failed: %d", (int)err);
	cl_command_queue q = cl.CreateCommandQueue(ctx, dev, 0, &err);
	if (err != CL_SUCCESS) die("clCreateCommandQueue failed: %d", (int)err);

	std::string src;
	{
		FILE* f = fopen(clpath.c_str(), "rb");
		if (!f) die("cannot open kernel source %s", clpath.c_str());
		char b[65536];
		size_t r;
		while ((r = fread(b, 1, sizeof(b), f)) > 0) src.append(b, r);
		fclose(f);
	}
	char extra[256] = "";
	{
		int o = 0;
		if (csn != Cs) o += snprintf(extra + o, sizeof(extra) - o, " -DCSMN=%.9g", 18.0 * std::sqrt(2.0) * csn * csn);
		if (bulk > 0.0) o += snprintf(extra + o, sizeof(extra) - o, " -DKB=%.9g", 1.0 - bulk);
		if (taun > 0.0) o += snprintf(extra + o, sizeof(extra) - o, " -DTAUN=%.9g", taun);
	}
	for (int l = 0; l < L; l++) {
		Level& c = lv[l];
		char opts[1024], par[256] = "";
		if (l > 0) snprintf(par, sizeof(par), " -DPARENT -DPNX=%uu -DPNY=%uu -DPNZ=%uu -DOX=%d -DOY=%d -DOZ=%d", lv[l - 1].n[0], lv[l - 1].n[1],
			lv[l - 1].n[2], c.o[0], c.o[1], c.o[2]);
		snprintf(opts, sizeof(opts), "-cl-fast-relaxed-math -DNX=%uu -DNY=%uu -DNZ=%uu -DNCELLS=%lluu -DWG=%du%s%s%s%s", c.n[0], c.n[1], c.n[2],
			(unsigned long long)c.N, wg, prec == "fp16" ? " -DFP16" : "", coll == "reg" ? " -DREG" : "", extra, par);
		const char* srcp = src.c_str();
		const size_t srcl = src.size();
		c.prog = cl.CreateProgramWithSource(ctx, 1, &srcp, &srcl, &err);
		if (err != CL_SUCCESS) die("clCreateProgramWithSource failed: %d", (int)err);
		const cl_int berr = cl.BuildProgram(c.prog, 1, &dev, opts, nullptr, nullptr);
		if (berr != CL_SUCCESS) {
			size_t ls = 0;
			cl.GetProgramBuildInfo(c.prog, dev, CL_PROGRAM_BUILD_LOG, 0, nullptr, &ls);
			std::string log(ls + 1, '\0');
			cl.GetProgramBuildInfo(c.prog, dev, CL_PROGRAM_BUILD_LOG, ls, &log[0], nullptr);
			die("kernel build failed for level %d (%d):\n%s", l, (int)berr, log.c_str());
		}
		for (int a = 0; a < 2; a++) for (int d = 0; d < 19; d++) {
			c.f[a][d] = cl.CreateBuffer(ctx, CL_MEM_READ_WRITE, (size_t)c.N * es, nullptr, &err);
			if (err != CL_SUCCESS) die("buffer allocation failed on level %d: %d", l, (int)err);
		}
		c.flags = cl.CreateBuffer(ctx, CL_MEM_READ_WRITE, (size_t)c.N, nullptr, &err);
		if (err != CL_SUCCESS) die("flags allocation failed: %d", (int)err);
	}
	cl_mem flags = F.flags;
	const size_t nocc = std::max<size_t>(occ.v.size(), 16u);
	cl_mem occb = cl.CreateBuffer(ctx, CL_MEM_READ_WRITE, nocc, nullptr, &err);
	if (err != CL_SUCCESS) die("occupancy allocation failed: %d", (int)err);
	const size_t ngf = (nbox + wg - 1) / wg;
	cl_mem partb = cl.CreateBuffer(ctx, CL_MEM_READ_WRITE, ngf * 6u * sizeof(float), nullptr, &err);
	if (err != CL_SUCCESS) die("partial-sum allocation failed: %d", (int)err);
	cl_mem partnb = cl.CreateBuffer(ctx, CL_MEM_READ_WRITE, ngf * 6u * sizeof(float), nullptr, &err);
	if (err != CL_SUCCESS) die("partial-sum allocation failed: %d", (int)err);

	// flags. Level 0: faces are fixed equilibrium cells, the outlet face (without its edges) a pressure outlet
	// (masstest: all faces are bounce-back walls). Refined levels: outermost layer F_IF. Cells under a finer level: F_COVER.
	for (int l = 0; l < L; l++) {
		const Level& c = lv[l];
		const uint32_t X = c.n[0], Y = c.n[1], Z = c.n[2];
		std::vector<uint8_t> h((size_t)c.N, 0u);
		for (uint32_t z = 0; z < Z; z++) for (uint32_t y = 0; y < Y; y++) for (uint32_t x = 0; x < X; x++) {
			uint8_t f = 0;
			const bool face = x == 0 || x == X - 1 || y == 0 || y == Y - 1 || z == 0 || z == Z - 1;
			if (l == 0) {
				const bool side = y == 0 || y == Y - 1 || z == 0 || z == Z - 1;
				if (mtest) {
					if (face) f = 1u;
					else if (x == 1 || x == X - 2 || y == 1 || y == Y - 2 || z == 1 || z == Z - 2) f = 8u;
				} else if (x == 0 || side) f = 2u;
				else if (x == X - 1) f = (outlet == "p" && !stokes) ? 4u : 2u;
			} else if (face) f = 64u;
			if (l + 1 < L) {
				const Level& k = lv[l + 1];
				if ((int)x >= k.o[0] && (int)x < k.o[0] + (int)k.n[0] / 2 && (int)y >= k.o[1] && (int)y < k.o[1] + (int)k.n[1] / 2 &&
					(int)z >= k.o[2] && (int)z < k.o[2] + (int)k.n[2] / 2) f |= 32u;
			}
			h[(size_t)x + (size_t)X * ((size_t)y + (size_t)Y * z)] = f;
		}
		CK(cl.EnqueueWriteBuffer(q, c.flags, CL_TRUE, 0, (size_t)c.N, h.data(), 0, nullptr, nullptr));
	}
	if (!occ.v.empty()) CK(cl.EnqueueWriteBuffer(q, occb, CL_TRUE, 0, occ.v.size(), occ.v.data(), 0, nullptr, nullptr));
	else { const uint8_t z16[16] = { 0 }; CK(cl.EnqueueWriteBuffer(q, occb, CL_TRUE, 0, 16, z16, 0, nullptr, nullptr)); }

	const size_t lwg = (size_t)wg;
	auto launch = [&](cl_kernel k, size_t n) {
		const size_t g = ((n + lwg - 1) / lwg) * lwg;
		CK(cl.EnqueueNDRangeKernel(q, k, 1, nullptr, &g, &lwg, 0, nullptr, nullptr));
	};
	for (int l = 0; l < L; l++) {
		Level& c = lv[l];
		const float oml = (float)(uw / (0.5 * c.D)), cx = (float)c.cc[0], cy = (float)c.cc[1], cz = (float)c.cc[2];
		for (int p = 0; p < 2; p++) for (int pp = 0; pp < 2; pp++) {
			c.sc[p][pp] = make_kernel(c.prog, "stream_collide");
			ArgSetter(c.sc[p][pp]).lattice(c.f[p]).lattice(c.f[1 - p]).lattice(l > 0 ? lv[l - 1].f[pp] : c.f[p])(c.flags)(oml)(cx)(cy)(cz)
				((float)c.tau0)((float)csm)((cl_int)1);
			if (l > 0) {
				c.coal[pp][p] = make_kernel(c.prog, "coalesce");
				ArgSetter(c.coal[pp][p]).lattice(lv[l - 1].f[pp]).lattice(c.f[1 - p]).lattice(c.f[p]);
			}
		}
		if (l > 0) c.ncoal = (size_t)(c.n[0] / 2 + 2) * (c.n[1] / 2 + 2) * (c.n[2] / 2 + 2);
		c.init = make_kernel(c.prog, "init_cells");
		ArgSetter(c.init).lattice(c.f[0]).lattice(c.f[1])(c.flags)((float)u)((float)pert)(oml)(cx)(cy)(cz)
			((cl_uint)((cl_uint)arg_d("seed", 0.0) + 0x10000000u * (cl_uint)l));
	}
	const cl_kernel k_force[2] = { make_kernel(F.prog, "body_force"), make_kernel(F.prog, "body_force") };
	const cl_kernel k_commit[2] = { make_kernel(F.prog, "geo_commit"), make_kernel(F.prog, "geo_commit") };
	const cl_kernel k_solid = make_kernel(F.prog, "geo_solid");
	const float om = (float)omega, fcx = (float)cc[0], fcy = (float)cc[1], fcz = (float)cc[2];
	cl_mem partsb = cl.CreateBuffer(ctx, CL_MEM_READ_WRITE, ngf * 18u * sizeof(float), nullptr, &err);
	if (err != CL_SUCCESS) die("partial-sum allocation failed: %d", (int)err);
	const size_t NDG = 34u; // must match the kernel
	cl_mem dpartb = cl.CreateBuffer(ctx, CL_MEM_READ_WRITE, ngf * NDG * sizeof(float), nullptr, &err);
	if (err != CL_SUCCESS) die("partial-sum allocation failed: %d", (int)err);
	cl_mem axesb = cl.CreateBuffer(ctx, CL_MEM_READ_WRITE, 28u * 3u * sizeof(float), nullptr, &err);
	if (err != CL_SUCCESS) die("axes allocation failed: %d", (int)err);
	// force split by the fluid cell p of each link: hole walls = R_inner - 1 < |p| < R + 1 and within r_hole + 1 cell of
	// a hole axis; the rest: outer surface |p| >= mid-wall radius, else inner surface. (A split by link radius alone,
	// outer >= R - 1.5 and inner <= R_inner + 1.5, left the hole walls empty: the wall is 2.4 cells at D = 96.)
	const float rm2 = (float)(rmid * rmid), rlo2 = (float)((Rin - 1.0) * (Rin - 1.0)), rhi2 = (float)((R + 1.0) * (R + 1.0));
	const float rw2 = (float)((rh + 1.0) * (rh + 1.0));
	const cl_uint nhk = (dgon && use_stl) ? (cl_uint)nh : 0u; // a smooth sphere has no hole walls
	for (int p = 0; p < 2; p++) {
		ArgSetter(k_force[p]).lattice(F.f[p])(flags)(bx0)(by0)(bz0)(bx)(by)(bz)(fcx)(fcy)(fcz)(om)((cl_uint)0)(1.0f)(partb)(partnb)
			(rm2)(rlo2)(rhi2)(axesb)(nhk)(rw2)(partsb);
		ArgSetter(k_commit[p]).lattice(F.f[p])(flags)(bx0)(by0)(bz0)(bx)(by)(bz)(fcx)(fcy)(fcz)(om);
	}
	const cl_kernel k_diag[2] = { make_kernel(F.prog, "diag"), make_kernel(F.prog, "diag") };
	for (int p = 0; p < 2; p++)
		ArgSetter(k_diag[p]).lattice(F.f[p])(flags)(bx0)(by0)(bz0)(bx)(by)(bz)(fcx)(fcy)(fcz)((float)rmid)((float)(rh * rh))
			((float)((Rin - 1.0) * (Rin - 1.0)))(axesb)((cl_uint)nh)(dpartb)((float)(R * R));
	double theta_now = 0.0; // spin angle of the voxelised geometry
	const float r2 = use_stl ? -1.0f : (float)(R * R);
	const cl_uint occM = (cl_uint)occ.M;
	ArgSetter(k_solid)(flags)(occb)(bx0)(by0)(bz0)(bx)(by)(bz)(fcx)(fcy)(fcz)(1.0f)(0.0f)(r2)(occM)((float)occ.h)((float)occ.rg);
	std::vector<int> cur(L, 0); // cur[l]: lattice of level l holding its post-collision populations of the current time
	auto geometry = [&](double theta) {
		if (nobody) return;
		theta_now = theta;
		if (nh > 0) { // hole axes at this spin angle, for the force split and the hole-flux discs
			std::vector<float> ax(84, 0.0f);
			const double c = std::cos(theta), sn = std::sin(theta); // body frame -> lattice: x = px c + pz sn, z = -px sn + pz c
			for (uint32_t h = 0; h < nh; h++) {
				const double px = haxes[3 * h], py = haxes[3 * h + 1], pz = haxes[3 * h + 2];
				ax[3 * h] = (float)(px * c + pz * sn); ax[3 * h + 1] = (float)py; ax[3 * h + 2] = (float)(-px * sn + pz * c);
			}
			CK(cl.EnqueueWriteBuffer(q, axesb, CL_TRUE, 0, ax.size() * sizeof(float), ax.data(), 0, nullptr, nullptr));
		}
		const float ct = (float)std::cos(theta), st = (float)std::sin(theta);
		CK(cl.SetKernelArg(k_solid, 11, sizeof(float), &ct));
		CK(cl.SetKernelArg(k_solid, 12, sizeof(float), &st));
		launch(k_solid, nbox);
		launch(k_commit[cur[L - 1]], nbox);
	};
	geometry(0.0);
	for (int l = 0; l < L; l++) launch(lv[l].init, (size_t)lv[l].N);
	CK(cl.Finish(q));

	std::vector<uint8_t> hf((size_t)F.N);
	CK(cl.EnqueueReadBuffer(q, flags, CL_TRUE, 0, (size_t)F.N, hf.data(), 0, nullptr, nullptr));
	uint64_t solid = 0, nearc = 0;
	for (size_t n = 0; n < (size_t)F.N; n++) { solid += hf[n] & 1u; nearc += (hf[n] >> 3) & 1u; }
	std::vector<uint8_t>().swap(hf);
	const double PI = 3.14159265358979323846, A = PI * R * R, qd = 0.5 * u * u * A;
	const double vol_ref = use_stl ? svol * std::pow(D / Dmm, 3.0) : 4.0 / 3.0 * PI * R * R * R;

	// host readback of a level's current lattice: per real cell rho - 1 and j (checks only)
	auto moments = [&](int l, std::vector<float>& dr, std::vector<float>& jx, std::vector<float>& jy, std::vector<float>& jz, std::vector<uint8_t>& fg) {
		const Level& c = lv[l];
		const size_t n = (size_t)c.N;
		dr.assign(n, 0.0f); jx.assign(n, 0.0f); jy.assign(n, 0.0f); jz.assign(n, 0.0f); fg.resize(n);
		CK(cl.Finish(q));
		CK(cl.EnqueueReadBuffer(q, c.flags, CL_TRUE, 0, n, fg.data(), 0, nullptr, nullptr));
		static const int CXh[19] = { 0, 1, -1, 0, 0, 0, 0, 1, -1, 1, -1, 0, 0, 1, -1, 1, -1, 0, 0 };
		static const int CYh[19] = { 0, 0, 0, 1, -1, 0, 0, 1, -1, 0, 0, 1, -1, -1, 1, 0, 0, 1, -1 };
		static const int CZh[19] = { 0, 0, 0, 0, 0, 1, -1, 0, 0, 1, -1, 1, -1, 0, 0, -1, 1, -1, 1 };
		std::vector<float> v(n);
		std::vector<uint16_t> hv(es == 2 ? n : 0);
		for (int d = 0; d < 19; d++) {
			if (es == 2) {
				CK(cl.EnqueueReadBuffer(q, c.f[cur[l]][d], CL_TRUE, 0, n * 2, hv.data(), 0, nullptr, nullptr));
				for (size_t i = 0; i < n; i++) v[i] = half_to_float(hv[i]) * 3.0517578125e-5f;
			} else CK(cl.EnqueueReadBuffer(q, c.f[cur[l]][d], CL_TRUE, 0, n * 4, v.data(), 0, nullptr, nullptr));
			for (size_t i = 0; i < n; i++) { dr[i] += v[i]; jx[i] += CXh[d] * v[i]; jy[i] += CYh[d] * v[i]; jz[i] += CZh[d] * v[i]; }
		}
	};
	auto total_mass = [&](double& m) { // sum over real cells of rho times the cell volume (level-0 cells = 1)
		std::vector<float> dr, jx, jy, jz;
		std::vector<uint8_t> fg;
		m = 0.0;
		for (int l = 0; l < L; l++) {
			moments(l, dr, jx, jy, jz, fg);
			double s = 0.0;
			for (size_t i = 0; i < dr.size(); i++) if (!(fg[i] & (1u | 2u | 4u | 32u))) s += 1.0 + (double)dr[i];
			m += s / std::pow(8.0, l);
		}
	};

	FILE* fo = fopen(out.c_str(), "wb");
	if (!fo) die("cannot write %s", out.c_str());
	fprintf(fo, "# PM-012 pm012_lbm run; body=%s stl=%s D=%.9g Re=%.9g u=%.9g S=%.9g omega=%.9g nu=%.9g tau=%.9g N=%ux%ux%u centre=%.9g,%.9g,%.9g "
		"every=%llu revox=%llu rx=%.9g ry=%.9g rz=%.9g Dmm=%.9g prec=%s coll=%s Cs=%.9g csn=%.9g bulk=%.9g taun=%.9g favg=%d "
		"outlet=%s pert=%.9g Lx=%.9g Ly=%.9g Lz=%.9g xc=%.9g lv=%d fb=%g,%g,%g gb=%g,%g,%g device=%s\n",
		body.c_str(), use_stl ? arg_s("stl", "").c_str() : "", D, Re, u, S, omega, nu, tau0, Nx, Ny, Nz, cc[0], cc[1], cc[2],
		(unsigned long long)every, (unsigned long long)(spin_mesh ? revox : 0), arg_d("rx", 0.0), arg_d("ry", 0.0), arg_d("rz", 0.0),
		use_stl ? Dmm : 0.0, prec.c_str(), coll.c_str(), Cs, csn, bulk, taun, favg ? 1 : 0, outlet.c_str(), pert, Lx, Ly, Lz, xc, L,
		fb[0], fb[1], fb[2], gb[0], gb[1], gb[2], dname);
	for (int l = 0; l < L; l++)
		fprintf(fo, "# level=%d level_D=%.9g level_N=%ux%ux%u level_origin_in_parent=%d,%d,%d level_box_D=%.6g,%.6g,%.6g level_nu=%.9g level_tau0=%.9g\n", l, lv[l].D, lv[l].n[0],
			lv[l].n[1], lv[l].n[2], lv[l].o[0], lv[l].o[1], lv[l].o[2], lv[l].ext[0], lv[l].ext[1], lv[l].ext[2], lv[l].nu, lv[l].tau0);
	fprintf(fo, "# solid_cells=%llu solid_over_reference_volume=%.9g near_cells=%llu A_ref=pi*(D/2)^2=%.9g cells; Cd=Fx/q Cy=Fy/q Cl=Fz/q CM=-Ty/(q*R), q=0.5*u^2*A (finest level units)\n",
		(unsigned long long)solid, (double)solid / vol_ref, (unsigned long long)nearc, A);
	if (use_stl) fprintf(fo, "# stl_triangles=%u stl_bbox_centre_mm=%.6g,%.6g,%.6g occ_M=%d occ_h=%.6g occ_volume_over_stl_volume=%.6g odd_rays=%lld/%lld\n",
		ntri, bbc[0], bbc[1], bbc[2], occ.M, occ.h, occ.vol_cells / vol_ref, occ.odd_rays, occ.rays);
	if (dgon) fprintf(fo, "# dg_setup dg_holes_file=%s dg_nholes=%u dg_R_out_cells=%.6g dg_R_in_cells=%.6g dg_r_disc_cells=%.6g dg_r_hole_cells=%.6g "
		"dg_split_hole_r_gt=%.6g dg_split_hole_r_lt=%.6g dg_split_hole_lateral_lt=%.6g dg_split_out_r_ge=%.6g dg_cav_r_lt=%.6g\n",
		hpath.empty() ? "none" : hpath.c_str(), nh, R, Rin, rmid, rh, Rin - 1.0, R + 1.0, rh + 1.0, rmid, Rin - 1.0);
	fprintf(fo, "step,tstar,Fx,Fy,Fz,Tx,Ty,Tz,Cd,Cy,Cl,CM\n");
	fflush(fo);
	uint64_t Ntot = 0;
	for (int l = 0; l < L; l++) Ntot += lv[l].N;
	printf("PM-012 %s on %s: N=%ux%ux%u (finest; %d levels, %.1f M cells in all), D=%g, Re=%g, nu=%.4g, tau0=%.6f, S=%g, %s/%s, solid/ref volume %.4f, steps %llu (finest)\n",
		body.c_str(), dname, Nx, Ny, Nz, L, Ntot * 1e-6, D, Re, nu, tau0, S, prec.c_str(), coll.c_str(), (double)solid / vol_ref, (unsigned long long)steps);
	fflush(stdout);
	double mass0 = 0.0, dmax = 0.0;
	if (mtest) { total_mass(mass0); printf("masstest: initial mass %.12g\n", mass0); }

	std::vector<float> part(ngf * 6u), partn(ngf * 6u);
	double last[6] = { 0, 0, 0, 0, 0, 0 };
	// period-2 check: per row, p2 = mean of (-1)^t F over the row's steps (F = mean + a (-1)^t gives p2 = a for an even
	// row length); accumulated over the rows with t* >= 15 into a footer line (Cd, Cl and CM units)
	double p2sum[3] = { 0, 0, 0 }, p2sq[3] = { 0, 0, 0 };
	uint64_t p2n = 0;
	uint64_t nacc = 0; // force evaluations summed in partb since the last row
	auto accumulate = [&](uint64_t t) {
		if (nobody) { nacc++; return; }
		const cl_uint acc = nacc > 0 ? 1u : 0u;
		const float sg = (t % 2u == 0u) ? 1.0f : -1.0f;
		const int p = cur[L - 1];
		CK(cl.SetKernelArg(k_force[p], 30, sizeof(cl_uint), &acc));
		CK(cl.SetKernelArg(k_force[p], 31, sizeof(float), &sg));
		launch(k_force[p], nbox);
		nacc++;
	};
	// hole and cavity diagnostics, one '# dg' line per CSV row (see usage); averages over t* >= 15 for the footer.
	// Hole flux Q_k = sum of rho u.a_k over the mid-wall disc of hole k (a_k turned by the current spin angle), given as
	// Q_k / (u pi r_h^2): + = out of the cavity. Force split: the momentum-exchange sums of the row (same averaging as the
	// CSV columns): outer surface, inner surface, hole walls (see the force split above). Cavity: fluid cells with r < R_inner - 1 (cells): mean |u| / u, mean |curl u| D / u,
	// angular momentum about the spin axis (+y) over the solid-body value omega sum rho (x^2 + z^2) (0 without spin).
	std::vector<float> parts(ngf * 18u), dpart(ngf * NDG);
	const double qh = u * 3.14159265358979323846 * rh * rh;
	std::vector<double> dg_hsum(nh, 0.0), dg_habs(nh, 0.0);
	double dg_sum[17] = { 0 }; // net, abs, cav umean, cav vort, cav Lratio, 12 split coefficients (out Cd Cy Cl CM, in ..., hole ...)
	uint64_t dg_n = 0;
	auto diagnostics = [&](uint64_t t, double ts, uint64_t nrow) {
		double sp[18] = { 0 };
		CK(cl.EnqueueReadBuffer(q, partsb, CL_TRUE, 0, parts.size() * sizeof(float), parts.data(), 0, nullptr, nullptr));
		for (size_t g = 0; g < ngf; g++) for (int k = 0; k < 18; k++) sp[k] += parts[18 * g + k];
		for (int k = 0; k < 18; k++) sp[k] /= (double)std::max<uint64_t>(nrow, 1u);
		double co[12];
		for (int s = 0; s < 3; s++) {
			co[4 * s] = sp[6 * s] / qd; co[4 * s + 1] = sp[6 * s + 1] / qd; co[4 * s + 2] = sp[6 * s + 2] / qd; co[4 * s + 3] = -sp[6 * s + 4] / (qd * R);
		}
		launch(k_diag[cur[L - 1]], nbox);
		CK(cl.EnqueueReadBuffer(q, dpartb, CL_TRUE, 0, dpart.size() * sizeof(float), dpart.data(), 0, nullptr, nullptr));
		std::vector<double> d(NDG, 0.0);
		for (size_t g = 0; g < ngf; g++) for (size_t k = 0; k < NDG; k++) d[k] += dpart[NDG * g + k];
		std::vector<double> hq(nh);
		double net = 0.0, tot = 0.0;
		for (uint32_t h = 0; h < nh; h++) { hq[h] = d[h] / qh; net += hq[h]; tot += std::fabs(hq[h]); }
		std::vector<uint32_t> order(nh);
		for (uint32_t h = 0; h < nh; h++) order[h] = h;
		std::sort(order.begin(), order.end(), [&](uint32_t a, uint32_t b) { return std::fabs(hq[a]) > std::fabs(hq[b]); });
		const double* c6 = &d[NDG - 6];
		const double cn = c6[0], umean = cn > 0 ? c6[1] / cn / u : 0.0, vort = c6[3] > 0 ? c6[2] / c6[3] * D / u : 0.0;
		const double lratio = (omega != 0.0 && c6[5] > 0) ? c6[4] / (omega * c6[5]) : 0.0;
		char top[160] = "";
		for (uint32_t i = 0, o = 0; i < std::min<uint32_t>(3u, nh); i++)
			o += snprintf(top + o, sizeof(top) - o, "%s%u:%.5g", i ? "," : "", order[i], hq[order[i]]);
		fprintf(fo, "# dg dg_step=%llu dg_tstar=%.6g dg_theta=%.6g dg_holes=%u dg_hole_net_out=%.6g dg_hole_abs=%.6g dg_hole_top3=%s "
			"dg_cav_cells=%.0f dg_cav_umean=%.6g dg_cav_vortD=%.6g dg_cav_Lratio=%.6g "
			"dg_Cd_out=%.6g dg_Cy_out=%.6g dg_Cl_out=%.6g dg_CM_out=%.6g dg_Cd_in=%.6g dg_Cy_in=%.6g dg_Cl_in=%.6g dg_CM_in=%.6g "
			"dg_Cd_hole=%.6g dg_Cy_hole=%.6g dg_Cl_hole=%.6g dg_CM_hole=%.6g\n",
			(unsigned long long)t, ts, theta_now, nh, net, tot, nh ? top : "none", cn, umean, vort, lratio,
			co[0], co[1], co[2], co[3], co[4], co[5], co[6], co[7], co[8], co[9], co[10], co[11]);
		if (ts >= 15.0) {
			for (uint32_t h = 0; h < nh; h++) { dg_hsum[h] += hq[h]; dg_habs[h] += std::fabs(hq[h]); }
			dg_sum[0] += net; dg_sum[1] += tot; dg_sum[2] += umean; dg_sum[3] += vort; dg_sum[4] += lratio;
			for (int k = 0; k < 12; k++) dg_sum[5 + k] += co[k];
			dg_n++;
		}
	};
	auto sample = [&](uint64_t t) {
		if (!favg || nacc == 0) { nacc = 0; accumulate(t); }
		double s[6] = { 0, 0, 0, 0, 0, 0 }, sn[6] = { 0, 0, 0, 0, 0, 0 };
		if (!nobody) {
			CK(cl.EnqueueReadBuffer(q, partb, CL_TRUE, 0, part.size() * sizeof(float), part.data(), 0, nullptr, nullptr));
			CK(cl.EnqueueReadBuffer(q, partnb, CL_TRUE, 0, partn.size() * sizeof(float), partn.data(), 0, nullptr, nullptr));
			for (size_t g = 0; g < ngf; g++) for (int k = 0; k < 6; k++) { s[k] += part[6 * g + k]; sn[k] += partn[6 * g + k]; }
			for (int k = 0; k < 6; k++) { s[k] /= (double)nacc; sn[k] /= (double)nacc; last[k] = s[k]; }
		}
		const double ts = ((double)t - 0.5 * (double)(nacc - 1)) / tunit; // centre of the averaging interval
		if (favg && nacc % 2u == 0u && ts >= 15.0 && qd > 0) {
			const double a[3] = { sn[0] / qd, sn[2] / qd, -sn[4] / (qd * R) };
			for (int k = 0; k < 3; k++) { p2sum[k] += a[k]; p2sq[k] += a[k] * a[k]; }
			p2n++;
		}
		const uint64_t nacc_row = nacc;
		nacc = 0;
		const double Cd = qd > 0 ? s[0] / qd : 0, Cy = qd > 0 ? s[1] / qd : 0, Cl = qd > 0 ? s[2] / qd : 0, CM = qd > 0 ? -s[4] / (qd * R) : 0;
		fprintf(fo, "%llu,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g\n", (unsigned long long)t, ts, s[0], s[1], s[2], s[3], s[4], s[5], Cd, Cy, Cl, CM);
		if (dgon) diagnostics(t, ts, nacc_row);
		if (mtest) {
			double m = 0.0;
			total_mass(m);
			dmax = std::max(dmax, std::fabs(m / mass0 - 1.0));
			fprintf(fo, "# mass_step=%llu mass_total=%.12g mass_rel_change=%.6e\n", (unsigned long long)t, m, m / mass0 - 1.0);
		}
		if (!std::isfinite(s[0]) || !std::isfinite(s[4])) {
			fprintf(fo, "# DIVERGED step=%llu\n", (unsigned long long)t);
			fclose(fo);
			die("diverged at step %llu (t* %.2f)", (unsigned long long)t, ts);
		}
		return std::vector<double>{ ts, Cd, Cl, CM, s[4] };
	};

	// one step of level l (sub = 1: first, 2: second half of the parent's step); recursion: the child's two steps and
	// the coalescence run before this level streams, so the parent lattice holds the parent's time t throughout
	uint64_t tf = 0; // finest steps done
	std::function<void(int, int)> step = [&](int l, int sub) {
		if (l + 1 < L) {
			step(l + 1, 1);
			launch(lv[l + 1].coal[cur[l]][cur[l + 1]], lv[l + 1].ncoal);
			step(l + 1, 2);
		}
		cl_kernel k = lv[l].sc[cur[l]][l > 0 ? cur[l - 1] : 0];
		const cl_int sb = sub < 1 ? 1 : sub;
		CK(cl.SetKernelArg(k, 64, sizeof(cl_int), &sb));
		launch(k, (size_t)lv[l].N);
		cur[l] ^= 1;
		if (l == L - 1) {
			tf++;
			if (spin_mesh && tf % revox == 0) geometry(omega * (double)tf);
			if (favg) accumulate(tf);
		}
	};
	double upd0 = 0.0; // cell updates per level-0 step
	for (int l = 0; l < L; l++) upd0 += (double)lv[l].N * (double)(1 << l);
	const auto t0 = std::chrono::steady_clock::now();
	uint64_t next_print = (uint64_t)tunit;
	for (;;) {
		if (tf > 0 && (tf % every == 0 || tf >= steps)) {
			const std::vector<double> r = sample(tf);
			if (tf >= next_print) {
				fflush(fo);
				const double el = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
				printf("t*=%.2f Cd=%.4f Cl=%.4f CM=%.4f Ty=%.6g  %.0f MLUPs\n", r[0], r[1], r[2], r[3], r[4], upd0 * (double)(tf / rat) / el * 1e-6);
				fflush(stdout);
				while (next_print <= tf) next_print += (uint64_t)tunit;
			}
		}
		if (tf >= steps) break;
		step(0, 0);
	}
	CK(cl.Finish(q));
	const double secs = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
	const double mlups = upd0 * (double)(steps / rat) / secs * 1e-6;
	fprintf(fo, "# runtime_s=%.6g steps=%llu MLUPs=%.6g finest_equivalent_MLUPs=%.6g\n", secs, (unsigned long long)steps, mlups,
		(double)lv[0].N * std::pow(8.0, L - 1) * (double)steps / secs * 1e-6);
	if (p2n > 0) {
		double m[3], r[3];
		for (int k = 0; k < 3; k++) { m[k] = p2sum[k] / p2n; r[k] = std::sqrt(p2sq[k] / p2n); }
		fprintf(fo, "# period2 rows=%llu p2_Cd_mean=%.6g p2_Cd_rms=%.6g p2_Cl_mean=%.6g p2_Cl_rms=%.6g p2_CM_mean=%.6g p2_CM_rms=%.6g\n",
			(unsigned long long)p2n, m[0], r[0], m[1], r[1], m[2], r[2]);
		printf("period-2 force component (t* >= 15): Cd rms %.4f, Cl rms %.4f, CM rms %.4f\n", r[0], r[1], r[2]);
	}
	if (dgon && dg_n > 0) {
		const double n = (double)dg_n;
		std::vector<uint32_t> order(nh);
		for (uint32_t h = 0; h < nh; h++) order[h] = h;
		std::sort(order.begin(), order.end(), [&](uint32_t a, uint32_t b) { return dg_habs[a] > dg_habs[b]; });
		std::string top, mean;
		char b[64];
		for (uint32_t i = 0; i < std::min<uint32_t>(3u, nh); i++) {
			snprintf(b, sizeof(b), "%s%u:%.5g", i ? "," : "", order[i], dg_habs[order[i]] / n); top += b;
		}
		for (uint32_t h = 0; h < nh; h++) { snprintf(b, sizeof(b), "%s%.5g", h ? "," : "", dg_hsum[h] / n); mean += b; }
		const double* a = dg_sum;
		fprintf(fo, "# dg_avg dg_avg_rows=%llu dg_avg_from_tstar=15 dg_avg_hole_net_out=%.6g dg_avg_hole_abs=%.6g dg_avg_hole_top3_abs=%s "
			"dg_avg_hole_mean=%s dg_avg_cav_umean=%.6g dg_avg_cav_vortD=%.6g dg_avg_cav_Lratio=%.6g "
			"dg_avg_Cd_out=%.6g dg_avg_Cy_out=%.6g dg_avg_Cl_out=%.6g dg_avg_CM_out=%.6g dg_avg_Cd_in=%.6g dg_avg_Cy_in=%.6g dg_avg_Cl_in=%.6g "
			"dg_avg_CM_in=%.6g dg_avg_Cd_hole=%.6g dg_avg_Cy_hole=%.6g dg_avg_Cl_hole=%.6g dg_avg_CM_hole=%.6g\n",
			(unsigned long long)dg_n, a[0] / n, a[1] / n, nh ? top.c_str() : "none", nh ? mean.c_str() : "none", a[2] / n, a[3] / n, a[4] / n,
			a[5] / n, a[6] / n, a[7] / n, a[8] / n, a[9] / n, a[10] / n, a[11] / n, a[12] / n, a[13] / n, a[14] / n, a[15] / n, a[16] / n);
		printf("diagnostics (t* >= 15, %llu rows): hole flux net %.4g, sum|Q| %.4g (u pi r_h^2); cavity |u|/u %.4g, |w|D/u %.4g, L/L_solid %.4g; "
			"Cd out/in/hole %.4f/%.4f/%.4f, Cl %.4f/%.4f/%.4f, CM %.4f/%.4f/%.4f\n", (unsigned long long)dg_n, a[0] / n, a[1] / n, a[2] / n, a[3] / n,
			a[4] / n, a[5] / n, a[9] / n, a[13] / n, a[7] / n, a[11] / n, a[15] / n, a[8] / n, a[12] / n, a[16] / n);
	}
	if (stokes) {
		const double Tst = -8.0 * PI * nu * R * R * R * omega;
		fprintf(fo, "# rotstokes body_Ty=%.9g stokes_Ty(R_nominal)=%.9g\n", last[4], Tst);
		printf("rotstokes: body Ty %.6g, Stokes -8 pi nu R^3 omega %.6g, ratio %.4f\n", last[4], Tst, last[4] / Tst);
	}
	if (nobody) { // field check: per level, largest |rho - 1| and |u - u_in| over the real cells
		for (int l = 0; l < L; l++) {
			std::vector<float> dr, jx, jy, jz;
			std::vector<uint8_t> fg;
			moments(l, dr, jx, jy, jz, fg);
			double mr = 0.0, mu = 0.0, sr = 0.0;
			size_t cnt = 0, imax = 0;
			for (size_t i = 0; i < dr.size(); i++) {
				if (fg[i] & (1u | 2u | 4u | 32u)) continue;
				const double rho = 1.0 + dr[i], ux = jx[i] / rho - (mtest ? 0.0 : u), uy = jy[i] / rho, uz = jz[i] / rho;
				mr = std::max(mr, std::fabs((double)dr[i]));
				const double e = std::sqrt(ux * ux + uy * uy + uz * uz);
				if (e > mu) { mu = e; imax = i; }
				sr += dr[i]; cnt++;
			}
			const uint32_t X = lv[l].n[0], Y = lv[l].n[1];
			const unsigned ix = (unsigned)(imax % X), iy = (unsigned)((imax / X) % Y), iz = (unsigned)(imax / ((size_t)X * Y));
			fprintf(fo, "# field field_level=%d field_cells=%llu max_abs_rho_minus_1=%.6e mean_rho_minus_1=%.6e max_abs_u_minus_uin=%.6e field_at=%u,%u,%u\n", l,
				(unsigned long long)cnt, mr, cnt ? sr / cnt : 0.0, mu, ix, iy, iz);
			printf("field L%d: max|rho-1| %.3e, mean rho-1 %.3e, max|u-u_in| %.3e (u_in %g) at cell %u,%u,%u (flags %u)\n", l, mr, cnt ? sr / cnt : 0.0,
				mu, mtest ? 0.0 : u, ix, iy, iz, (unsigned)fg[imax]);
		}
		if (mtest) {
			double m = 0.0;
			total_mass(m);
			fprintf(fo, "# masstest mass0=%.12g mass_end=%.12g rel_change_end=%.6e max_abs_rel_change=%.6e\n", mass0, m, m / mass0 - 1.0,
				std::max(dmax, std::fabs(m / mass0 - 1.0)));
			printf("masstest: mass %.12g -> %.12g, relative change %.3e (largest over the samples %.3e)\n", mass0, m, m / mass0 - 1.0,
				std::max(dmax, std::fabs(m / mass0 - 1.0)));
		}
	}
	fclose(fo);
	printf("PM-012 done: %.1f s, %.0f MLUPs, wrote %s\n", secs, mlups, out.c_str());
	return 0;
}
