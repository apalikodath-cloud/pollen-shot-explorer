// PM-012 (FTC POLLEN Magnus project): own GPU lattice Boltzmann LES solver for flow past a smooth sphere or the POLLEN
// ball (binary STL), still or spinning about +y. Written for this project from the textbook method (no third-party
// source): D3Q19, two-lattice pull scheme, regularized (default) or BGK collision with a Smagorinsky subgrid model,
// halfway bounce-back with the moving-wall term (Ladd 1994), force and torque by momentum exchange.
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
		"  body=sphere|stl|rotstokes  smooth sphere, POLLEN binary STL (mm), or sphere spinning in still fluid (torque check)\n"
		"  D=48 body diameter in cells   Re=3e4 (u D/nu)   u=0.05 inflow (lattice)   S=0 spin ratio omega R/u about +y\n"
		"  Lx,Ly,Lz=6,4,4 box in D (rotstokes 4,4,4)   xc=2 body centre from the inlet in D   T=55 run length in D/u (rotstokes R^2/nu: 40)\n"
		"  every=<steps> sampling (default about 50 per D/u)   out=run.csv   cl=<path of pm012_lbm.cl> (default: next to the exe)\n"
		"  prec=fp16|fp32 (default fp16; rotstokes fp32)   coll=reg|bgk (default reg)   Cs=0.1 Smagorinsky   outlet=p|eq (default p)\n"
		"  stl=<path> Dmm=71.12 (outer diameter mapped to D)   rx,ry,rz=<deg> static orientation (about x, then y, then z)\n"
		"  ref=4 occupancy voxels per cell   revox=<steps> geometry update interval of a spinning STL (default: wall moves <= 0.1 cell)\n"
		"  svol=22312.36 STL enclosed volume in mm^3 (check)   pert=1e-3 initial noise (fraction of u)   wg=128 work-group size\n"
		"  favg=1 each CSV row averages the force over every step since the previous row (0: instantaneous sample)\n"
		"  rotstokes: uw=0.005 wall speed omega R, nu=0.2   platform=0 device=0 (GPU index on that OpenCL platform)\n");
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

int main(int argc, char** argv) {
	for (int i = 1; i < argc; i++) {
		const std::string s = argv[i];
		if (s == "-h" || s == "--help" || s == "help") { usage(); return 0; }
		const size_t e = s.find('=');
		if (e == std::string::npos || e == 0) die("argument \"%s\" is not key=value (try help)", s.c_str());
		g_arg[s.substr(0, e)] = s.substr(e + 1);
	}
	static const char* known[] = { "body", "D", "Re", "u", "S", "Lx", "Ly", "Lz", "xc", "T", "every", "out", "cl", "prec", "coll", "Cs",
		"outlet", "stl", "Dmm", "rx", "ry", "rz", "ref", "revox", "svol", "pert", "wg", "uw", "nu", "platform", "device", "favg" };
	for (const auto& kv : g_arg) {
		bool ok = false;
		for (const char* k : known) ok = ok || kv.first == k;
		if (!ok) die("unknown argument %s (try help)", kv.first.c_str());
	}
	const std::string body = arg_s("body", "sphere");
	const bool stokes = body == "rotstokes", use_stl = body == "stl";
	if (!stokes && !use_stl && body != "sphere") die("body must be sphere, stl or rotstokes");
	const double D = arg_d("D", 48.0), R = 0.5 * D;
	const double u = stokes ? 0.0 : arg_d("u", 0.05);
	const double Re = arg_d("Re", 3.0e4), S = stokes ? 0.0 : arg_d("S", 0.0);
	const double uw = stokes ? arg_d("uw", 0.005) : S * u, omega = uw / R;
	const double nu = stokes ? arg_d("nu", 0.2) : u * D / Re;
	const double tau0 = 3.0 * nu + 0.5;
	const double Lx = arg_d("Lx", stokes ? 4.0 : 6.0), Ly = arg_d("Ly", 4.0), Lz = arg_d("Lz", 4.0);
	const double xc = arg_d("xc", stokes ? 0.5 * Lx : 2.0);
	const std::string prec = arg_s("prec", stokes ? "fp32" : "fp16"), coll = arg_s("coll", "reg"), outlet = arg_s("outlet", "p");
	if (prec != "fp16" && prec != "fp32") die("prec must be fp16 or fp32");
	if (coll != "reg" && coll != "bgk") die("coll must be reg or bgk");
	if (outlet != "p" && outlet != "eq") die("outlet must be p or eq");
	const double Cs = arg_d("Cs", 0.1), csm = 18.0 * std::sqrt(2.0) * Cs * Cs;
	const double pert = stokes ? 0.0 : arg_d("pert", 1e-3);
	const int wg = (int)arg_d("wg", 128.0);
	if (wg < 32 || wg > 1024 || (wg & (wg - 1))) die("wg must be a power of two in 32..1024");
	if (D < 8.0 || D > 400.0 || u < 0.0 || u > 0.15 || nu <= 0.0) die("D, u or nu out of range");
	const uint32_t Nx = 2u * (uint32_t)std::lround(0.5 * Lx * D), Ny = 2u * (uint32_t)std::lround(0.5 * Ly * D), Nz = 2u * (uint32_t)std::lround(0.5 * Lz * D);
	const uint64_t N = (uint64_t)Nx * Ny * Nz;
	if (N >= 0x7FFFFFFFull) die("too many cells (%llu)", (unsigned long long)N);
	const double tunit = stokes ? R * R / nu : D / u;
	const uint64_t steps = (uint64_t)std::llround(arg_d("T", stokes ? 40.0 : 55.0) * tunit);
	const double cc[3] = { stokes ? 0.5 * Nx - 0.5 : std::floor(xc * D) - 0.5, 0.5 * Ny - 0.5, 0.5 * Nz - 0.5 }; // half-integer centre
	if (cc[0] - R < 4.0 || cc[0] + R > Nx - 5.0 || R > 0.5 * Ny - 4.0 || R > 0.5 * Nz - 4.0) die("body does not fit the box");
	const bool spin_mesh = use_stl && omega != 0.0;
	uint64_t revox = (uint64_t)arg_d("revox", std::max(1.0, std::floor(0.1 / std::max(std::fabs(uw), 1e-9))));
	if (revox < 1) revox = 1;
	uint64_t every = (uint64_t)arg_d("every", std::max(1.0, std::round(tunit / 50.0)));
	if (every < 1) every = 1;
	if (spin_mesh) every = ((every + revox - 1) / revox) * revox;
	const std::string out = arg_s("out", "pm012_run.csv");
	std::string clpath = arg_s("cl", "");
	if (clpath.empty()) {
		char exe[MAX_PATH];
		const DWORD L = GetModuleFileNameA(nullptr, exe, MAX_PATH);
		std::string p(exe, L);
		clpath = p.substr(0, p.find_last_of("\\/") + 1) + "pm012_lbm.cl";
	}

	// ---- geometry on the host: STL occupancy grid ----
	const double Dmm = arg_d("Dmm", 71.12), svol = arg_d("svol", 22312.36);
	Occ occ;
	uint32_t ntri = 0;
	double bbc[3] = { 0, 0, 0 }, rbody = R;
	if (use_stl) {
		const std::string stl = arg_s("stl", "");
		if (stl.empty()) die("body=stl needs stl=<path>");
		double Rm[9];
		rot_xyz(arg_d("rx", 0.0), arg_d("ry", 0.0), arg_d("rz", 0.0), Rm);
		const std::vector<double> V = load_stl_cells(stl, D / Dmm, Rm, ntri, bbc);
		const auto t0 = std::chrono::steady_clock::now();
		occ = voxelize(V, ntri, (int)arg_d("ref", 4.0));
		rbody = occ.rg;
		printf("STL: %u triangles, bbox centre (%.4f, %.4f, %.4f) mm, occupancy %d^3 voxels of %.3f cells, volume/STL volume %.4f, odd rays %lld/%lld (%.1f s)\n",
			ntri, bbc[0], bbc[1], bbc[2], occ.M, occ.h, occ.vol_cells / (svol * std::pow(D / Dmm, 3.0)), occ.odd_rays, occ.rays,
			std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count());
	}
	const int pad = 3;
	int lo[3], hi[3];
	const uint32_t NN[3] = { Nx, Ny, Nz };
	for (int k = 0; k < 3; k++) {
		lo[k] = std::max(1, (int)std::floor(cc[k] - rbody) - pad);
		hi[k] = std::min((int)NN[k] - 2, (int)std::ceil(cc[k] + rbody) + pad);
	}
	const cl_uint bx0 = lo[0], by0 = lo[1], bz0 = lo[2], bx = hi[0] - lo[0] + 1, by = hi[1] - lo[1] + 1, bz = hi[2] - lo[2] + 1;
	const size_t nbox = (size_t)bx * by * bz;

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
	const size_t es = prec == "fp16" ? 2u : 4u;
	const double need = 38.0 * (double)N * es + (double)N + (double)occ.v.size();
	if ((double)N * es > (double)amax || need > 0.92 * (double)gmem) die("needs %.2f GB (device %.2f GB, max buffer %.2f GB)", need * 1e-9, gmem * 1e-9, amax * 1e-9);
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
	char opts[512];
	snprintf(opts, sizeof(opts), "-cl-fast-relaxed-math -DNX=%uu -DNY=%uu -DNZ=%uu -DNCELLS=%lluu -DWG=%du%s%s", Nx, Ny, Nz,
		(unsigned long long)N, wg, prec == "fp16" ? " -DFP16" : "", coll == "reg" ? " -DREG" : "");
	const char* srcp = src.c_str();
	const size_t srcl = src.size();
	cl_program prog = cl.CreateProgramWithSource(ctx, 1, &srcp, &srcl, &err);
	if (err != CL_SUCCESS) die("clCreateProgramWithSource failed: %d", (int)err);
	const cl_int berr = cl.BuildProgram(prog, 1, &dev, opts, nullptr, nullptr);
	if (berr != CL_SUCCESS) {
		size_t ls = 0;
		cl.GetProgramBuildInfo(prog, dev, CL_PROGRAM_BUILD_LOG, 0, nullptr, &ls);
		std::string log(ls + 1, '\0');
		cl.GetProgramBuildInfo(prog, dev, CL_PROGRAM_BUILD_LOG, ls, &log[0], nullptr);
		die("kernel build failed (%d):\n%s", (int)berr, log.c_str());
	}

	cl_mem fl[2][19];
	for (int l = 0; l < 2; l++) for (int d = 0; d < 19; d++) {
		fl[l][d] = cl.CreateBuffer(ctx, CL_MEM_READ_WRITE, (size_t)N * es, nullptr, &err);
		if (err != CL_SUCCESS) die("buffer allocation failed: %d", (int)err);
	}
	cl_mem flags = cl.CreateBuffer(ctx, CL_MEM_READ_WRITE, (size_t)N, nullptr, &err);
	if (err != CL_SUCCESS) die("flags allocation failed: %d", (int)err);
	const size_t nocc = std::max<size_t>(occ.v.size(), 16u);
	cl_mem occb = cl.CreateBuffer(ctx, CL_MEM_READ_WRITE, nocc, nullptr, &err);
	if (err != CL_SUCCESS) die("occupancy allocation failed: %d", (int)err);
	const size_t ngf = (nbox + wg - 1) / wg;
	cl_mem partb = cl.CreateBuffer(ctx, CL_MEM_READ_WRITE, ngf * 6u * sizeof(float), nullptr, &err);
	if (err != CL_SUCCESS) die("partial-sum allocation failed: %d", (int)err);

	// flags: faces are fixed equilibrium cells, the outlet face (without its edges) a pressure outlet
	{
		std::vector<uint8_t> h((size_t)N, 0u);
		for (uint32_t z = 0; z < Nz; z++) for (uint32_t y = 0; y < Ny; y++) for (uint32_t x = 0; x < Nx; x++) {
			const bool side = y == 0 || y == Ny - 1 || z == 0 || z == Nz - 1;
			uint8_t f = 0;
			if (x == 0 || side) f = 2u;
			else if (x == Nx - 1) f = (outlet == "p" && !stokes) ? 4u : 2u;
			h[(size_t)x + (size_t)Nx * ((size_t)y + (size_t)Ny * z)] = f;
		}
		CK(cl.EnqueueWriteBuffer(q, flags, CL_TRUE, 0, (size_t)N, h.data(), 0, nullptr, nullptr));
	}
	if (!occ.v.empty()) CK(cl.EnqueueWriteBuffer(q, occb, CL_TRUE, 0, occ.v.size(), occ.v.data(), 0, nullptr, nullptr));
	else { const uint8_t z16[16] = { 0 }; CK(cl.EnqueueWriteBuffer(q, occb, CL_TRUE, 0, 16, z16, 0, nullptr, nullptr)); }

	const cl_kernel k_sc[2] = { make_kernel(prog, "stream_collide"), make_kernel(prog, "stream_collide") };
	const cl_kernel k_force[2] = { make_kernel(prog, "body_force"), make_kernel(prog, "body_force") };
	const cl_kernel k_commit[2] = { make_kernel(prog, "geo_commit"), make_kernel(prog, "geo_commit") };
	const cl_kernel k_solid = make_kernel(prog, "geo_solid"), k_init = make_kernel(prog, "init_cells");
	const float om = (float)omega, fcx = (float)cc[0], fcy = (float)cc[1], fcz = (float)cc[2];
	for (int p = 0; p < 2; p++) {
		ArgSetter(k_sc[p]).lattice(fl[p]).lattice(fl[1 - p])(flags)(om)(fcx)(fcy)(fcz)((float)tau0)((float)csm);
		ArgSetter(k_force[p]).lattice(fl[p])(flags)(bx0)(by0)(bz0)(bx)(by)(bz)(fcx)(fcy)(fcz)(om)((cl_uint)0)(partb);
		ArgSetter(k_commit[p]).lattice(fl[p])(flags)(bx0)(by0)(bz0)(bx)(by)(bz)(fcx)(fcy)(fcz)(om);
	}
	const float r2 = use_stl ? -1.0f : (float)(R * R);
	const cl_uint occM = (cl_uint)occ.M;
	ArgSetter(k_solid)(flags)(occb)(bx0)(by0)(bz0)(bx)(by)(bz)(fcx)(fcy)(fcz)(1.0f)(0.0f)(r2)(occM)((float)occ.h)((float)occ.rg);
	ArgSetter(k_init).lattice(fl[0]).lattice(fl[1])(flags)((float)u)((float)pert)(om)(fcx)(fcy)(fcz);
	const size_t lwg = (size_t)wg;
	auto launch = [&](cl_kernel k, size_t n) {
		const size_t g = ((n + lwg - 1) / lwg) * lwg;
		CK(cl.EnqueueNDRangeKernel(q, k, 1, nullptr, &g, &lwg, 0, nullptr, nullptr));
	};
	int par = 0; // lattice fl[par] holds the post-collision populations of the current time step
	auto geometry = [&](double theta) {
		const float ct = (float)std::cos(theta), st = (float)std::sin(theta);
		CK(cl.SetKernelArg(k_solid, 11, sizeof(float), &ct));
		CK(cl.SetKernelArg(k_solid, 12, sizeof(float), &st));
		launch(k_solid, nbox);
		launch(k_commit[par], nbox);
	};
	geometry(0.0);
	launch(k_init, (size_t)N);
	CK(cl.Finish(q));

	std::vector<uint8_t> hf((size_t)N);
	CK(cl.EnqueueReadBuffer(q, flags, CL_TRUE, 0, (size_t)N, hf.data(), 0, nullptr, nullptr));
	uint64_t solid = 0, nearc = 0;
	for (size_t n = 0; n < (size_t)N; n++) { solid += hf[n] & 1u; nearc += (hf[n] >> 3) & 1u; }
	std::vector<uint8_t>().swap(hf);
	const double PI = 3.14159265358979323846, A = PI * R * R, qd = 0.5 * u * u * A;
	const double vol_ref = use_stl ? svol * std::pow(D / Dmm, 3.0) : 4.0 / 3.0 * PI * R * R * R;

	FILE* fo = fopen(out.c_str(), "wb");
	if (!fo) die("cannot write %s", out.c_str());
	fprintf(fo, "# PM-012 pm012_lbm run; body=%s stl=%s D=%.9g Re=%.9g u=%.9g S=%.9g omega=%.9g nu=%.9g tau=%.9g N=%ux%ux%u centre=%.9g,%.9g,%.9g "
		"every=%llu revox=%llu rx=%.9g ry=%.9g rz=%.9g Dmm=%.9g prec=%s coll=%s Cs=%.9g outlet=%s pert=%.9g Lx=%.9g Ly=%.9g Lz=%.9g xc=%.9g device=%s\n",
		body.c_str(), use_stl ? arg_s("stl", "").c_str() : "", D, Re, u, S, omega, nu, tau0, Nx, Ny, Nz, cc[0], cc[1], cc[2],
		(unsigned long long)every, (unsigned long long)(spin_mesh ? revox : 0), arg_d("rx", 0.0), arg_d("ry", 0.0), arg_d("rz", 0.0),
		use_stl ? Dmm : 0.0, prec.c_str(), coll.c_str(), Cs, outlet.c_str(), pert, Lx, Ly, Lz, xc, dname);
	fprintf(fo, "# solid_cells=%llu solid_over_reference_volume=%.9g near_cells=%llu A_ref=pi*(D/2)^2=%.9g cells; Cd=Fx/q Cy=Fy/q Cl=Fz/q CM=-Ty/(q*R), q=0.5*u^2*A\n",
		(unsigned long long)solid, (double)solid / vol_ref, (unsigned long long)nearc, A);
	if (use_stl) fprintf(fo, "# stl_triangles=%u stl_bbox_centre_mm=%.6g,%.6g,%.6g occ_M=%d occ_h=%.6g occ_volume_over_stl_volume=%.6g odd_rays=%lld/%lld\n",
		ntri, bbc[0], bbc[1], bbc[2], occ.M, occ.h, occ.vol_cells / vol_ref, occ.odd_rays, occ.rays);
	fprintf(fo, "step,tstar,Fx,Fy,Fz,Tx,Ty,Tz,Cd,Cy,Cl,CM\n");
	fflush(fo);
	printf("PM-012 %s on %s: N=%ux%ux%u (%.1f M cells), D=%g, Re=%g, nu=%.4g, tau0=%.6f, S=%g, %s/%s, solid/ref volume %.4f, steps %llu\n",
		body.c_str(), dname, Nx, Ny, Nz, N * 1e-6, D, Re, nu, tau0, S, prec.c_str(), coll.c_str(), (double)solid / vol_ref, (unsigned long long)steps);
	fflush(stdout);

	std::vector<float> part(ngf * 6u);
	double last[6] = { 0, 0, 0, 0, 0, 0 };
	const bool favg = arg_d("favg", 1.0) != 0.0;
	uint64_t nacc = 0; // force evaluations summed in partb since the last row
	auto accumulate = [&]() {
		const cl_uint acc = nacc > 0 ? 1u : 0u;
		CK(cl.SetKernelArg(k_force[par], 30, sizeof(cl_uint), &acc));
		launch(k_force[par], nbox);
		nacc++;
	};
	auto sample = [&](uint64_t t) {
		if (!favg || nacc == 0) { nacc = 0; accumulate(); }
		CK(cl.EnqueueReadBuffer(q, partb, CL_TRUE, 0, part.size() * sizeof(float), part.data(), 0, nullptr, nullptr));
		double s[6] = { 0, 0, 0, 0, 0, 0 };
		for (size_t g = 0; g < ngf; g++) for (int k = 0; k < 6; k++) s[k] += part[6 * g + k];
		for (int k = 0; k < 6; k++) { s[k] /= (double)nacc; last[k] = s[k]; }
		const double ts = ((double)t - 0.5 * (double)(nacc - 1)) / tunit; // centre of the averaging interval
		nacc = 0;
		const double Cd = qd > 0 ? s[0] / qd : 0, Cy = qd > 0 ? s[1] / qd : 0, Cl = qd > 0 ? s[2] / qd : 0, CM = qd > 0 ? -s[4] / (qd * R) : 0;
		fprintf(fo, "%llu,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g\n", (unsigned long long)t, ts, s[0], s[1], s[2], s[3], s[4], s[5], Cd, Cy, Cl, CM);
		if (!std::isfinite(s[0]) || !std::isfinite(s[4])) {
			fprintf(fo, "# DIVERGED step=%llu\n", (unsigned long long)t);
			fclose(fo);
			die("diverged at step %llu (t* %.2f)", (unsigned long long)t, ts);
		}
		return std::vector<double>{ ts, Cd, Cl, CM, s[4] };
	};
	const auto t0 = std::chrono::steady_clock::now();
	uint64_t next_print = (uint64_t)tunit;
	for (uint64_t t = 0;; t++) {
		if (spin_mesh && t > 0 && t % revox == 0) geometry(omega * (double)t);
		if (favg && t > 0) accumulate();
		if (t > 0 && (t % every == 0 || t == steps)) {
			const std::vector<double> r = sample(t);
			if (t >= next_print) {
				fflush(fo);
				const double el = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
				printf("t*=%.2f Cd=%.4f Cl=%.4f CM=%.4f Ty=%.6g  %.0f MLUPs\n", r[0], r[1], r[2], r[3], r[4], (double)N * t / el * 1e-6);
				fflush(stdout);
				while (next_print <= t) next_print += (uint64_t)tunit;
			}
		}
		if (t >= steps) break;
		launch(k_sc[par], (size_t)N);
		par = 1 - par;
	}
	CK(cl.Finish(q));
	const double secs = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
	const double mlups = (double)N * (double)steps / secs * 1e-6;
	fprintf(fo, "# runtime_s=%.6g steps=%llu MLUPs=%.6g\n", secs, (unsigned long long)steps, mlups);
	if (stokes) {
		const double Tst = -8.0 * PI * nu * R * R * R * omega;
		fprintf(fo, "# rotstokes body_Ty=%.9g stokes_Ty(R_nominal)=%.9g\n", last[4], Tst);
		printf("rotstokes: body Ty %.6g, Stokes -8 pi nu R^3 omega %.6g, ratio %.4f\n", last[4], Tst, last[4] / Tst);
	}
	fclose(fo);
	printf("PM-012 done: %.1f s, %.0f MLUPs, wrote %s\n", secs, mlups, out.c_str());
	return 0;
}
