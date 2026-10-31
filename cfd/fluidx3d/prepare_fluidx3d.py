"""PM-012: prepare a FluidX3D clone for the PM-012 cases (run before MSBuild; idempotent).

Usage: $PM012_CFD_ROOT/venv/Scripts/python.exe -I cfd/fluidx3d/prepare_fluidx3d.py <FluidX3D clone> [--precision FP16C|FP16S]
1. checks the clone is at the pinned commit (FluidX3D source is never copied into this repo)
2. src/defines.hpp: BENCHMARK off; FP16C (or FP16S); VOLUME_FORCE, FORCE_FIELD, EQUILIBRIUM_BOUNDARIES,
   MOVING_BOUNDARIES, SUBGRID on; graphics stay off (console build)
3. src/kernel.cpp + src/lbm.cpp: update_force_field() patch. Stock FluidX3D sums 2*f_i*c_i over all 18 links of a
   solid cell; for a moving wall that misses the Ladd term -6*w_i*rho_w*(c_i.u_w)*c_i (Ladd 1994; Krueger et al. 2017),
   which dominates the torque of a spinning ball, and it also counts solid-solid links whose stored DDFs are stale.
   Patched: links to fluid cells only, each 2*f_i*c_i - 6*w_i*(c_i.u_w)*c_i (rho_w = 1, as FluidX3D's own moving
   boundaries use). Shifted DDFs (f - w_i) are fine: the uniform part sums to zero force and torque over a closed body.
4. copies cfd/fluidx3d/setup.cpp over src/setup.cpp (the original is kept once as src/setup.cpp.orig)
"""
import argparse
import pathlib
import re
import shutil
import subprocess
import sys

PINNED = "b85d64ee39a72687d163d42806c9a0ccdaed6d3c"
ON = ["VOLUME_FORCE", "FORCE_FIELD", "EQUILIBRIUM_BOUNDARIES", "MOVING_BOUNDARIES", "SUBGRID"]
OFF = ["BENCHMARK", "INTERACTIVE_GRAPHICS", "INTERACTIVE_GRAPHICS_ASCII", "GRAPHICS"]

K_SIG_OLD = "kernel void update_force_field(const global fpxx* fi, const global uchar* flags, const ulong t, global float* F) {"
K_SIG_NEW = "kernel void update_force_field(const global fpxx* fi, const global uchar* flags, const ulong t, global float* F, const global float* u) { // PM-012 patch"
K_BODY_OLD = (
    "\tfloat Fb=1.0f, fx=0.0f, fy=0.0f, fz=0.0f;\n"
    "\tcalculate_rho_u(fhn, &Fb, &fx, &fy, &fz); // abuse calculate_rho_u() method for calculating force\n"
    "\tstore3(F, n, 2.0f*Fb*(float3)(fx, fy, fz)); // 2x because fi are reflected on solid boundary cells (bounced-back)\n"
)
K_BODY_NEW = (
    "\tconst float uxn=u[n], uyn=u[def_N+(ulong)n], uzn=u[2ul*def_N+(ulong)n]; // PM-012 patch: wall velocity of this solid cell\n"
    "\tfloat fx=0.0f, fy=0.0f, fz=0.0f;\n"
    "\tfor(uint i=1u; i<def_velocity_set; i++) { // PM-012 patch: momentum exchange over links to fluid cells, with the Ladd moving-wall term\n"
    "\t\tconst uchar fbj = flags[j[i%2u ? i+1u : i-1u]]&TYPE_BO; // neighbor n-c_i, from which fhn[i] streamed in\n"
    "\t\tif(fbj==TYPE_S||fbj==TYPE_E) continue; // skip solid-solid and boundary links\n"
    "\t\tconst float cx=(float)c(i), cy=(float)c(def_velocity_set+i), cz=(float)c(2u*def_velocity_set+i);\n"
    "\t\tconst float g = 2.0f*fhn[i]-6.0f*w(i)*(cx*uxn+cy*uyn+cz*uzn); // rho_wall=1 as in apply_moving_boundaries()\n"
    "\t\tfx += cx*g; fy += cy*g; fz += cz*g;\n"
    "\t}\n"
    "\tstore3(F, n, (float3)(fx, fy, fz));\n"
)
L_OLD = 'kernel_update_force_field = Kernel(device, N, "update_force_field", fi, flags, t, F);'
L_NEW = 'kernel_update_force_field = Kernel(device, N, "update_force_field", fi, flags, t, F, u); // PM-012 patch'


CRLF, LF = b"\r\n".decode(), "\n"


def read(p):
    raw = p.read_bytes()
    return raw.decode("utf-8").replace(CRLF, LF), CRLF.encode() in raw


def write(p, text, crlf):
    p.write_bytes((text.replace(LF, CRLF) if crlf else text).encode("utf-8"))


def replace_once(text, old, new, name):
    if new in text:
        return text, False
    if text.count(old) != 1:
        raise SystemExit("anchor not found exactly once in %s; is the clone at %s?" % (name, PINNED))
    return text.replace(old, new), True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clone")
    ap.add_argument("--precision", choices=["FP16C", "FP16S"], default="FP16C")
    ap.add_argument("--setup", default=str(pathlib.Path(__file__).with_name("setup.cpp")))
    a = ap.parse_args()
    root = pathlib.Path(a.clone)
    head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    if head != PINNED:
        raise SystemExit("FluidX3D clone is at %r, expected %s" % (head, PINNED))
    src = root / "src"

    d, crlf = read(src / "defines.hpp")
    for name in ON + [a.precision]:
        d = re.sub(r"(?m)^//#define %s\b" % name, "#define %s" % name, d)
    for name in OFF + [{"FP16C": "FP16S", "FP16S": "FP16C"}[a.precision]]:
        d = re.sub(r"(?m)^#define %s\b" % name, "//#define %s" % name, d)
    for name in ON + [a.precision]:
        if not re.search(r"(?m)^#define %s\b" % name, d):
            raise SystemExit("could not enable %s in defines.hpp" % name)
    write(src / "defines.hpp", d, crlf)

    k, crlf = read(src / "kernel.cpp")
    k, c1 = replace_once(k, K_SIG_OLD, K_SIG_NEW, "kernel.cpp")
    k, c2 = replace_once(k, K_BODY_OLD, K_BODY_NEW, "kernel.cpp")
    write(src / "kernel.cpp", k, crlf)
    lb, crlf = read(src / "lbm.cpp")
    lb, c3 = replace_once(lb, L_OLD, L_NEW, "lbm.cpp")
    write(src / "lbm.cpp", lb, crlf)

    orig = src / "setup.cpp.orig"
    if not orig.exists():
        shutil.copyfile(src / "setup.cpp", orig)
    shutil.copyfile(a.setup, src / "setup.cpp")
    print("prepared %s at %s: %s on, patch %s" % (root, PINNED[:12], ",".join(ON + [a.precision]),
                                                  "applied" if (c1 or c2 or c3) else "already present"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
