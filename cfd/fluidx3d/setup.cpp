// PM-012 (FTC POLLEN Magnus project): CFD cases for FluidX3D.
// ALTERED FluidX3D SOURCE. This file replaces src/setup.cpp of FluidX3D (https://github.com/ProjectPhysX/FluidX3D,
// commit b85d64ee39a72687d163d42806c9a0ccdaed6d3c, Copyright (c) Dr. Moritz Lehmann). FluidX3D licence terms apply:
// non-commercial, non-military, cite FluidX3D in publications, publish altered source with published results.
// cfd/fluidx3d/prepare_fluidx3d.py copies this file in, sets defines.hpp and patches update_force_field (see cfd/README.md).
//
// Console arguments (key=value, any order):
//   body=sphere|stl|rotstokes  smooth sphere, binary STL in mm (POLLEN), or rotating sphere in still fluid (torque check)
//   D=<cells>      body outer diameter in lattice cells                       (default 48)
//   Re=<number>    U*D/nu                                                     (default 3e4)
//   u=<lattice>    inflow velocity, Mach = u*sqrt(3)                          (default 0.05)
//   S=<number>     spin ratio omega*R/U, spin about +y, lift along +z         (default 0)
//   Lx,Ly,Lz=<D>   box size in body diameters                                 (default 8,5,5)
//   xc=<D>         body centre distance from the inlet face                   (default 2.5)
//   T=<t*>         run length in t* = D/U (rotstokes: in R^2/nu)              (default 60)
//   every=<steps>  sampling interval                                          (default ~50 samples per t*)
//   stl=<path>     binary STL in mm, centred on its origin (body=stl)
//   Dmm=<mm>       STL outer diameter mapped to D cells                       (default 71.12, POLLEN CAD)
//   rx,ry,rz=<deg> STL orientation (rotations about x, then y, then z)       (default 0: CAD polar axis = +y = spin axis)
//   revox=<steps>  re-voxelize a spinning STL every this many steps           (default: wall moves <= 0.1 cell)
//   uw,nu          rotstokes only: wall speed omega*R and viscosity          (defaults 0.005, 0.2)
//   out=<path>     CSV output (forces/torques in lattice units + coefficients)
#include "setup.hpp"
#ifdef BENCHMARK
#error "PM-012 setup: #define BENCHMARK must be commented out in defines.hpp (prepare_fluidx3d.py does this)"
#endif
#include <chrono>
#include <fstream>
#include <iomanip>
#include <map>

static std::map<string, string> pm_arg;
static string arg_s(const string& key, const string& fallback) { const auto it = pm_arg.find(key); return it==pm_arg.end() ? fallback : it->second; }
static double arg_d(const string& key, const double fallback) { const auto it = pm_arg.find(key); return it==pm_arg.end() ? fallback : std::stod(it->second); }

static void cube_torque(LBM& lbm, const float3& c, const float a, const float nu, double* T) { // torque transmitted through a cube surface of half-width a around c (stress + momentum flux)
	lbm.update_fields();
	lbm.rho.read_from_device();
	lbm.u.read_from_device();
	const ulong Nx=lbm.get_Nx(), Ny=lbm.get_Ny();
	auto idx = [&](const int x, const int y, const int z) { return (ulong)x+((ulong)y+(ulong)z*Ny)*Nx; };
	auto uc = [&](const int* p, const int k) { const ulong n = idx(p[0], p[1], p[2]); return (double)(k==0 ? lbm.u.x[n] : k==1 ? lbm.u.y[n] : lbm.u.z[n]); };
	const double cc[3] = { c.x, c.y, c.z };
	int lo[3], hi[3];
	for(int k=0; k<3; k++) { lo[k] = (int)lround(cc[k]-a); hi[k] = (int)lround(cc[k]+a); }
	T[0] = T[1] = T[2] = 0.0;
	for(int d=0; d<3; d++) for(int s=-1; s<=1; s+=2) {
		const int e1=(d+1)%3, e2=(d+2)%3;
		for(int i1=lo[e1]; i1<=hi[e1]; i1++) for(int i2=lo[e2]; i2<=hi[e2]; i2++) {
			int p[3]; p[d] = s<0 ? lo[d] : hi[d]; p[e1] = i1; p[e2] = i2;
			const double wgt = (i1==lo[e1]||i1==hi[e1] ? 0.5 : 1.0)*(i2==lo[e2]||i2==hi[e2] ? 0.5 : 1.0); // trapezoid rule
			double G[3][3]; // G[j][k] = d u_k / d x_j, central differences
			for(int j=0; j<3; j++) {
				int pp[3]={p[0], p[1], p[2]}, pm[3]={p[0], p[1], p[2]}; pp[j]++; pm[j]--;
				for(int k=0; k<3; k++) G[j][k] = 0.5*(uc(pp, k)-uc(pm, k));
			}
			const ulong n = idx(p[0], p[1], p[2]);
			const double rho = (double)lbm.rho[n], pr = (rho-1.0)/3.0, un[3] = { uc(p, 0), uc(p, 1), uc(p, 2) };
			double t[3]; // traction on the inner region: sigma.n - rho*u*(u.n), n = s*e_d
			for(int j=0; j<3; j++) t[j] = s*((double)nu*rho*(G[j][d]+G[d][j])-(j==d ? pr : 0.0))-rho*un[j]*(s*un[d]);
			const double r[3] = { p[0]-cc[0], p[1]-cc[1], p[2]-cc[2] };
			T[0] += wgt*(r[1]*t[2]-r[2]*t[1]);
			T[1] += wgt*(r[2]*t[0]-r[0]*t[2]);
			T[2] += wgt*(r[0]*t[1]-r[1]*t[0]);
		}
	}
}

void main_setup() { // required extensions in defines.hpp: VOLUME_FORCE, FORCE_FIELD, EQUILIBRIUM_BOUNDARIES, MOVING_BOUNDARIES, SUBGRID (+ FP16C)
	for(const string& s : main_arguments) { const size_t e = s.find('='); if(e!=string::npos) pm_arg[s.substr(0u, e)] = s.substr(e+1u); else print_warning("ignored argument \""+s+"\""); }
	main_arguments.clear(); // FluidX3D would read console arguments as OpenCL device ids
	const string body = arg_s("body", "sphere");
	const bool stokes = body=="rotstokes", use_stl = body=="stl";
	if(!stokes&&!use_stl&&body!="sphere") print_error("body must be sphere, stl or rotstokes");
	const float D = (float)arg_d("D", 48.0), R = 0.5f*D;
	const float u = stokes ? 0.0f : (float)arg_d("u", 0.05);
	const float Re = (float)arg_d("Re", 3.0E4);
	const float S = (float)arg_d("S", 0.0);
	const float uw = stokes ? (float)arg_d("uw", 0.005) : S*u; // wall speed at the equator
	const float omega = uw/R; // spin about +y
	const float nu = stokes ? (float)arg_d("nu", 0.2) : u*D/Re;
	const float Lx = (float)arg_d("Lx", stokes ? 4.0 : 8.0), Ly = (float)arg_d("Ly", stokes ? 4.0 : 5.0), Lz = (float)arg_d("Lz", stokes ? 4.0 : 5.0);
	const float xc = (float)arg_d("xc", stokes ? 0.5*Lx : 2.5);
	const uint Nx = 2u*to_uint(0.5f*Lx*D), Ny = 2u*to_uint(0.5f*Ly*D), Nz = 2u*to_uint(0.5f*Lz*D); // even sizes: centre on a cell corner
	const float tunit = stokes ? R*R/nu : D/u; // steps per time unit
	const ulong steps_total = (ulong)((float)arg_d("T", stokes ? 40.0 : 60.0)*tunit+0.5f);
	const string stl = arg_s("stl", ""), out = arg_s("out", "pm012_run.csv");
	const float Dmm = (float)arg_d("Dmm", 71.12);
	const float deg = 3.14159265f/180.0f;
	ulong revox = (ulong)arg_d("revox", fmax(1.0, floor(0.1/fmax((double)uw, 1E-9))));
	ulong every = (ulong)arg_d("every", fmax(1.0, round((double)tunit/50.0)));
	const bool spin_mesh = use_stl&&omega!=0.0f;
	if(spin_mesh) every = ((every+revox-1ull)/revox)*revox;

	LBM lbm(Nx, Ny, Nz, nu);
	const float3 c = float3(stokes ? 0.5f*(float)Nx-0.5f : floor(xc*D)-0.5f, 0.5f*(float)Ny-0.5f, 0.5f*(float)Nz-0.5f); // half-integer: symmetric voxels
	const float3 w = float3(0.0f, omega, 0.0f);
	Mesh* mesh = nullptr;
	if(use_stl) {
		const float3x3 rot = float3x3(float3(0.0f, 0.0f, 1.0f), (float)arg_d("rz", 0.0)*deg)*float3x3(float3(0.0f, 1.0f, 0.0f), (float)arg_d("ry", 0.0)*deg)*float3x3(float3(1.0f, 0.0f, 0.0f), (float)arg_d("rx", 0.0)*deg);
		mesh = read_stl(stl, D/Dmm, rot, c); // cells per mm, placed at c
		lbm.voxelize_mesh_on_device(mesh, TYPE_S, c, float3(0.0f), w);
	}
	const uint Nxm=Nx-1u, Nym=Ny-1u, Nzm=Nz-1u;
	parallel_for(lbm.get_N(), [&](ulong n) { uint x=0u, y=0u, z=0u; lbm.coordinates(n, x, y, z);
		if(!use_stl&&sphere(x, y, z, c, R)) {
			lbm.flags[n] = TYPE_S;
			lbm.u.x[n] = omega*((float)z-c.z); lbm.u.y[n] = 0.0f; lbm.u.z[n] = -omega*((float)x-c.x); // w x (r-c), w = omega*e_y
		} else if(lbm.flags[n]!=TYPE_S) {
			lbm.u.x[n] = u; lbm.u.y[n] = 0.0f; lbm.u.z[n] = 0.0f;
			if(x==0u||x==Nxm||y==0u||y==Nym||z==0u||z==Nzm) lbm.flags[n] = TYPE_E; // inflow, outflow and side faces: rho=1, u=(u,0,0)
		}
	});
	ulong solid = 0ull; for(ulong n=0ull; n<lbm.get_N(); n++) solid += (lbm.flags[n]==TYPE_S);
	const double PI = 3.141592653589793, A = PI*R*R, q = 0.5*(double)u*(double)u*A;
	const double vol_ref = use_stl ? 22312.36*pow((double)(D/Dmm), 3.0) : 4.0/3.0*PI*R*R*R; // POLLEN STL enclosed volume 22312.36 mm^3 (cfd/step_to_stl.py)
	std::ofstream f(out);
	f << std::setprecision(9);
	f << "# PM-012 FluidX3D run; body=" << body << " stl=" << stl << " D=" << D << " Re=" << Re << " u=" << u << " S=" << S << " omega=" << omega << " nu=" << nu
	  << " tau=" << 3.0f*nu+0.5f << " N=" << Nx << "x" << Ny << "x" << Nz << " centre=" << c.x << "," << c.y << "," << c.z << " every=" << every << " revox=" << (spin_mesh ? revox : 0ull)
	  << " rx=" << arg_d("rx", 0.0) << " ry=" << arg_d("ry", 0.0) << " rz=" << arg_d("rz", 0.0) << " Dmm=" << (use_stl ? Dmm : 0.0f) << "\n";
	f << "# solid_cells=" << solid << " solid_over_reference_volume=" << (double)solid/vol_ref << " A_ref=pi*(D/2)^2=" << A << " cells; Cd=Fx/q Cy=Fy/q Cl=Fz/q CM=-Ty/(q*R), q=0.5*u^2*A\n";
	f << "step,tstar,Fx,Fy,Fz,Tx,Ty,Tz,Cd,Cy,Cl,CM\n";
	print_info("PM-012 "+body+": N="+to_string(Nx)+"x"+to_string(Ny)+"x"+to_string(Nz)+", D="+to_string(D, 1u)+", nu="+to_string(nu, 6u)+", solid/ref volume="+to_string((float)((double)solid/vol_ref), 4u)+", steps="+to_string(steps_total));

	lbm.run(0u, steps_total); // initialize
	const float3 cpos = c-lbm.center(); // object_torque() takes box-centred positions
	const auto t0 = std::chrono::steady_clock::now();
	ulong next_print = (ulong)tunit;
	while(lbm.get_t()<steps_total) {
		if(spin_mesh) {
			for(ulong k=0ull; k<every; k+=revox) {
				lbm.run(revox, steps_total);
				mesh->rotate(float3x3(float3(0.0f, 1.0f, 0.0f), omega*(float)revox));
				lbm.voxelize_mesh_on_device(mesh, TYPE_S, c, float3(0.0f), w);
			}
		} else {
			lbm.run(every, steps_total);
		}
		const float3 F = lbm.object_force(TYPE_S);
		const float3 Tq = lbm.object_torque(cpos, TYPE_S);
		const ulong t = lbm.get_t();
		const double ts = (double)t/(double)tunit;
		const double Cd = q>0.0 ? F.x/q : 0.0, Cy = q>0.0 ? F.y/q : 0.0, Cl = q>0.0 ? F.z/q : 0.0, CM = q>0.0 ? -Tq.y/(q*R) : 0.0;
		f << t << "," << ts << "," << F.x << "," << F.y << "," << F.z << "," << Tq.x << "," << Tq.y << "," << Tq.z << "," << Cd << "," << Cy << "," << Cl << "," << CM << "\n";
		if(t>=next_print) {
			f.flush();
			print_info("t*="+to_string((float)ts, 2u)+" Cd="+to_string((float)Cd, 4u)+" Cl="+to_string((float)Cl, 4u)+" CM="+to_string((float)CM, 4u)+" Ty="+to_string(Tq.y, 6u));
			next_print += (ulong)tunit;
		}
	}
	const double secs = std::chrono::duration<double>(std::chrono::steady_clock::now()-t0).count();
	const double mlups = (double)lbm.get_N()*(double)lbm.get_t()/secs*1E-6;
	f << "# runtime_s=" << secs << " steps=" << lbm.get_t() << " MLUPs=" << mlups << "\n";
	if(stokes) { // torque check: momentum exchange vs angular momentum flux through cubes vs Stokes 8*pi*mu*R^3*omega
		const float3 Tb = lbm.object_torque(cpos, TYPE_S);
		const double Tst = -8.0*PI*(double)nu*(double)R*(double)R*(double)R*(double)omega;
		f << "# rotstokes body_Ty=" << Tb.y << " stokes_Ty(R_nominal)=" << Tst;
		for(const float k : { 1.5f, 2.0f, 2.5f, 3.0f }) {
			const float a = floor(k*R)+0.5f;
			if(c.x+a+1.0f>=(float)Nxm||c.x-a-1.0f<=0.0f) continue;
			double T[3]; cube_torque(lbm, c, a, nu, T);
			f << " cube_" << a << "_Ty=" << T[1];
		}
		f << "\n";
	}
	f.close();
	print_info("PM-012 done: "+to_string((float)secs, 1u)+" s, "+to_string((float)mlups, 0u)+" MLUPs/s, wrote "+out);
	if(mesh) delete mesh;
}
