# PM-012 CFD: POLLEN in still room air (FluidX3D LBM-LES)

The coach asked to "add fluid sims of standard room temp static air so it's more accurate". Today the model's drag
(Cd 0.5, range 0.33-0.9), Magnus lift (Cl = min(c1 S, Cl_max)) and spin decay k are ASSUMED literature values
(`research/params_lit.json`). This folder holds a CFD setup meant to give PREDICTED values for POLLEN itself. It must be
validated on smooth spheres before any POLLEN number is used.

Labels follow HANDOFF section 5: CONFIRMED, user, ASSUMED, derived, PREDICTED.

## Update 2026-10-31: local grid refinement (`lv=`)

Everything away from the ball is still room-temperature air in uniform flow, so the solver now puts fine cells only
around the ball. Own code in `cfd/lbm/`, following the published method of Rohde et al. (2006).
`lv=1` (the default) is the old uniform grid.

**Method.**
- Nested boxes, refinement factor 2 per level, cell-centred (a coarse cell holds 2x2x2 fine cells). `D` is the
  finest level's cells per diameter; level l has D / 2^(L-1-l).
- Acoustic scaling: the same lattice u on every level, nu_l = u D_l / Re, so tau differs per level. The Smagorinsky
  model runs on each level with its own tau.
- Sub-cycling: a level takes two steps per parent step (recursive: child step, coalescence, child step, own step).
- Coupling: the volumetric, mass-conserving scheme of Rohde et al. (2006). Populations that a fine interface cell
  pulls from outside its box come from the parent cell they lie in (uniform explosion); after its first sub-step the
  fine level is summed back into the covered parent cells (coalescence). No non-equilibrium rescaling.
- The body, the moving-wall term, the STL re-voxelisation of a spinning ball and the momentum-exchange force all live
  on the finest level only. The finest box must hold the whole shell and the hollow inside (default margin
  0.7 D upstream, 1.5 D downstream, 0.7 D sideways; each coarser refined level adds 0.5 / 1.0 / 0.4 D).

**Options.** `lv=1` (uniform, the old behaviour) to 4; `fb=up,down,side` finest box; `gb=up,down,side` growth per
coarser level; `plan=1` prints per-level cells and memory, cells across a hole and across the wall, and
`need_mib=` for a queue, then exits without the GPU; `body=none` (uniform-flow check) and `body=masstest` (closed box,
total mass) are checks. `lv=3 D=192` (box 6x4x4 D) needs about 4.3 GB in FP16 (derived, solver plan):

| Level | D | Cells | Memory (FP16) |
|---|---|---|---|
| L0 | 48 | 288x192x192 = 10.6 M | 780 MiB |
| L1 | 96 | 356x212x212 = 16.0 M | 1175 MiB |
| L2 | 192 | 424x272x272 = 31.4 M | 2304 MiB |

The finest D 192 gives 27.5-30.2 cells across a hole and 4.8 across the wall (derived; D 94 uniform gave 13-15 and
2.35). A uniform D 192 grid would need about 680 M cells, which does not fit. `lv=3 D=96` uses 0.54 GB.

**Hole and cavity diagnostics** (`holes=<file from stl_holes.py>`, sphere or STL). New `# dg ...` lines after every
CSV row and a `# dg_avg ...` footer (t* >= 15); the existing keys are unchanged.
- Through-hole flow: for each of the 26 holes, the mass flux through a disc at mid-wall, normal to the hole axis,
  radius = hole radius (`hole_mm=11.2`, `wall_mm=1.778`), axes rotated by the current spin angle. Positive = out of
  the cavity; normalised by rho u pi r_h^2. Keys: `dg_hole_net_out`, `dg_hole_abs` (sum of |flux|), `dg_hole_top3`,
  `dg_avg_hole_mean` (26 values).
- Cavity (fluid cells with r < R_inner - 1 cell): `dg_cav_umean` (mean |u|/U), `dg_cav_vortD` (mean |curl u| D/U),
  `dg_cav_Lratio` (air angular momentum about the spin axis / solid-body value, rho omega r_perp^2 summed over the
  same cells).
- Force split over the wall links, by the fluid cell p of each link (cells; a fluid cell is never inside the wall):
  hole walls = R_inner - 1 < |p| < R + 1 and within r_hole + 1 cell of a hole axis (axes at the current spin angle);
  the other links are outer surface (|p| >= mid-wall radius) or inner surface. Keys `dg_Cd_out`, `dg_Cy_out`,
  `dg_Cl_out`, `dg_CM_out`, then `_in` and `_hole`; the three parts add up to the total. A smooth sphere has no hole
  walls. A split by link radius alone (outer r >= R - 1.5, inner r <= R_inner + 1.5) was tried first and left the
  hole walls empty: the wall is only 2.4 cells thick at D 96, so the two bands overlap. The hole-wall part includes a
  rim of about 1 cell on the outer and inner surface around each hole.

**Checks of the refinement** (derived, own solver, RTX 3060 shared with other runs):

| Check | Result | Target |
|---|---|---|
| Total mass, closed box, lv 2 D 32 and lv 3 D 64, FP32 | relative change 2.2e-9 and -1.5e-9 (largest 3.5e-9) | round-off |
| Uniform flow, no body, lv 3 D 64, BGK | FP16 noise max \|u - U\|/U 4.5e-4 = same as the uniform grid (4.6-5.2e-4); FP32, no noise: max \|u - U\|/U 9.2e-6 and \|rho - 1\| 1.5e-6 at t* 12 on every level | no growth at the interfaces |
| Uniform flow, no body, regularized collision, Re 3e4 | lv 3 FP32 grows: 8.6e-4 (t* 3), 3.3e-2 (t* 6), 3.9e-2 (t* 12), first at the upstream face of the finest box. The **uniform** grid does the same (D 16: 3.9e-3 at t* 12, 3.95e-2 at t* 24; D 32: 3.9e-2 at t* 12; also with Cs 0); stable at u 0.02 (6e-7) and at Re 3000 (7.6e-6) | **fails**; see below |
| Old uniform runs (`lv=1`) with the new code | 192 CSV rows: forces and Cd, Cy, Cl bit-identical; torques differ by at most 1.2e-7 (lattice units; summation order of the force split) | same as before |
| V0 rotating sphere, Stokes torque, lv 2 D 32 FP32 | 1.0286 x analytic; uniform grid 1.0264 (+0.2 %) | 0.97-1.10 |
| Sphere Re 100, lv 2 D 32 FP32 | Cd 1.2013; uniform grid 1.1890 (+1.0 %) | within a few % of the uniform grid |
| Diagnostics unit check: closed smooth sphere, S 0.5, lv 2 D 32, `holes=` given | hole flux 0, cavity 0 cells, inner and hole-wall force 0, outer part = total (Cd 0.654) | exactly that |
| Diagnostics, spinning POLLEN STL (hole facing the flow), S 0.5, lv 2 D 96, t* 3 (smoke test) | STL volume ratio 1.0005, odd rays 0; 371,848 cavity cells; hole fluxes non-zero; at t* 3 Cd split outer / inner / hole walls 0.567 / 0.067 / 0.065, sum = total to 1e-6 | runs; not a result |
| **V1** smooth sphere Re 33057, S 0, lv 3 D 96, BGK FP16, box 6x4x4, T 55, mean t* 15-55 | Cd 0.553 (se 0.004, half-window drift -0.011); Cl -0.004, Cy -0.023 | Cd 0.317-0.589 (0.4532 +- 30 %): **inside**, settled. Uniform BGK D 80 same box: Cd 0.539, Cl 0.104 |
| **V2** smooth sphere Re 33057, S 0.5, same grid | Cl 0.220 (se 0.007, drift +0.012), Cd 0.510, CM -0.014; S 0 twin above: Cl -0.004, Cd 0.553 | Cl 0.22-0.33: **at the lower edge** (0.2197), not a clear pass |

All numbers in this table are derived from our own solver (smooth sphere: validation only, not POLLEN). The V1 and V2
grid study continues at finest D 192 (lv 3, queued); D 384 does not fit in 12 GB (lv 4: 31 GiB with these boxes,
15 GiB even with tight boxes).

**Collision: BGK for production.** The regularized collision (`coll=reg`) is unstable in plain uniform flow at
tau close to 0.5 with u 0.05 (table above), on the uniform grid as well as the refined one, with or without the
Smagorinsky term. That fits its high sphere Cd (0.67-0.70 against 0.54-0.56 for BGK). All refined and production runs
use `coll=bgk`.

No POLLEN number from the refined solver exists yet. Queued after V1 and V2 at D 192 (same configuration, refined
lv 3 D 192 BGK): POLLEN hole facing the flow and between holes at S 0 and S 0.5; 8 random orientations at S 0 and 4
of them at S 1.0 (7 m/s); between holes at S 0 and S 1.0 at 4 and 10 m/s. Every spin case has its no-spin twin and a
smooth-sphere twin on the same grid. Estimated cost (derived): about 3 h per case at D 192 on the RTX 3060, more
for spinning POLLEN (re-voxelisation).

## Update 2026-10-31: route (b), own solver

FluidX3D stays unbuilt (the permission check refused it). The runs use **route (b)**, an LBM-LES solver written
from scratch for PM-012 in `cfd/lbm/` (no FluidX3D code):

- D3Q19, FP16 or FP32 storage, regularized (or BGK) collision with Smagorinsky Cs 0.1;
- halfway bounce-back with the moving-wall term, so the sphere or the STL can spin;
- momentum-exchange force and torque, by default averaged over every step between CSV rows (`favg=1`);
- the same CSV format as the FluidX3D setup, so `postprocess.py` reads it.

Build it with `cfd/lbm/build.cmd` (MSVC; output in `%PM012_CFD_ROOT%\pm012_lbm\bin`, outside the repo).
Run `pm012_lbm.exe` with no arguments for the key=value list. `cfd/lbm/stl_holes.py` finds the 26 hole axes of the
POLLEN STL and gives the rx/ry/rz values for "hole facing the flow" and "between holes".

Checks so far (derived, own solver):

- rotating sphere, Stokes torque, D32 FP32: 1.026 x analytic (target 0.97-1.10);
- sphere at Re 100: Cd 1.17-1.19 (reference 1.087, +8-9 %);
- sphere at Re 33057, D48: Cd 0.698 (reference 0.4532): fails the 30 % gate. Diagnosis runs are queued.

No POLLEN result exists until the smooth-sphere check passes. The status below is the earlier FluidX3D status.

## Status (2026-10-31)

- **No CFD case has been built or run, so this folder contains no CFD results.** The validation table below gives
  reference values only. Its CFD column is empty.
- **Done:**
  - route (a) chosen;
  - FluidX3D cloned and pinned outside the repo;
  - setup source and force patch written and reviewed;
  - POLLEN CAD converted to STL and checked;
  - resolution and memory planned;
  - post-processing written and self-tested;
  - run script written.
- **Blocker:** the session's permission check refused to build FluidX3D ("[Code from External]"). That blocks every
  build and run. To continue, the user can either:
  - allow the two commands (the MSBuild line in `run_cases.sh build`, and `$PM012_CFD_ROOT/FluidX3D/bin/FluidX3D.exe`), or
  - run `bash cfd/run_cases.sh build`, then `validate`, themselves.

## Route

| Option | Choice | Why |
|---|---|---|
| (a) FluidX3D, GPU lattice Boltzmann, OpenCL | **chosen** | Runs on the RTX 3060 through OpenCL. Includes Smagorinsky LES, moving (rotating) walls, an STL voxelizer and on-GPU force/torque sums. Needs no CUDA toolkit. |
| (b) own Warp/CuPy LBM | not used | Only a fallback if (a) cannot build. Neither package nor a CUDA toolkit is installed. It would need the same outside-code permission. |

- **Clone:** `$PM012_CFD_ROOT\FluidX3D` (https://github.com/ProjectPhysX/FluidX3D), pinned at commit
  `b85d64ee39a72687d163d42806c9a0ccdaed6d3c`. It is never copied into this repo.
- **Build:** VS 18 MSBuild, Release x64, toolset v145. The project file asks for v142, which VS 2019 BuildTools also
  provides.

## FluidX3D licence (read 2026-10-31 from the clone's LICENSE.md; verbatim copy in `fluidx3d/LICENSE-FluidX3D.md`)

Copyright (c) 2022-2026 Dr. Moritz Lehmann. The terms are below; each one says how this project complies.

1. **Use.** Allowed only for public research, education or personal use.
   - This is an FTC student-team (education) project.
   - **No commercial use.** That includes paid services whose value comes from FluidX3D, so it must not be used for
     the firm's paid work.
2. **Origin.** The origin must not be misrepresented, and altered source must be plainly marked.
   - `fluidx3d/setup.cpp` is headed "ALTERED FluidX3D SOURCE".
   - The kernel patch lines carry "PM-012 patch".
3. **No military use.**
4. **No training of AI models** on FluidX3D source.
5. **Publishing.** If results or binaries from an altered version are published, the altered source must be
   published too.
   - Our alterations are `fluidx3d/setup.cpp` and the patch in `fluidx3d/prepare_fluidx3d.py`.
   - Publish them alongside any shared CFD numbers or figures.
6. **Citation.** Scientific publications must cite the FluidX3D references:
   - Lehmann, *Computation* 10:92 (2022), doi 10.3390/computation10060092;
   - Lehmann et al., *Phys. Rev. E* 106:015308 (2022).
7. **Notice.** The licence notice must stay in source distributions. That is why the verbatim copy is kept here.

## Method

**Solver.** D3Q19 lattice Boltzmann, SRT collision, Esoteric-Pull in-place streaming, FP16C DDF storage. Smagorinsky-Lilly
LES (FluidX3D `SUBGRID`) provides the sub-grid viscosity.

**Domain and boundaries.**
- The body is fixed in a uniform stream along +x.
- All six faces are equilibrium boundaries with rho 1 and u = (u, 0, 0).
- Walls use bounce-back. The moving-wall (Ladd) term gives the spinning wall its velocity u_w = w x (x - c), with spin
  about +y, so backspin lift points along +z.

**Force and torque: momentum exchange (our patch, `fluidx3d/prepare_fluidx3d.py`).**
- Stock FluidX3D sums 2 f_i c_i over all 18 links of each solid cell.
- That misses the moving-wall term and counts stale solid-solid links. Both matter for the torque of a spinning ball.
- The patch sums only links to fluid cells, each contributing (2 f_i - 6 w_i c_i.u_w) c_i (Ladd 1994; Krueger et al. 2017).

**Coefficients**, written by `setup.cpp` for each sample:
- q = 0.5 u^2 pi R^2, with R = D/2 in cells.
- Cd = Fx/q, Cy = Fy/q, Cl = Fz/q.
- CM = -Ty/(q R).
- The run also writes solid cells / reference volume (the leak and voxelization check), runtime and MLUPs/s.

**Numerical regime** (all derived):
- Lattice u is 0.05, so lattice Mach is 0.087 (below 0.1). Physical Mach is at most 0.032 at 11 m/s.
- nu_lattice = u D/Re. At D 94 and Re 3.3e4 that gives tau = 0.5004, so the run is stable only with the LES.
- The laminar boundary layer is about D/sqrt(Re) = 0.0055 D, about 0.5 cell at D 94. **The wall layer is not
  resolved.** This is an under-resolved LES with staircase walls, and separation and transition are not reliable.
  Smooth-sphere validation errors therefore set the CFD uncertainty band.

**Post-processing** (`postprocess.py`, standard library only):
- Mean, standard deviation, batch-means standard error and half-window drift after a transient (default t* 15).
- Grid comparison: change, Richardson extrapolation and GCI for an assumed order of 1 or 2 (Celik et al. 2008).
- Conversion to the model's convention.

## Inputs

| Quantity | Value | Label and source |
|---|---|---|
| Air | still, dry, 20 C, 101.325 kPa | user (task) |
| rho | 1.2041 kg/m^3 | derived: p/(R_d T), R_d 287.06 J/(kg K) (CIPM-2007, Picard et al. 2008, *Metrologia* 45:149); `src/air.py` |
| mu | 1.8133e-5 Pa s | derived: Sutherland (U.S. Standard Atmosphere 1976 form, S 110.4 K); `src/air.py`. Textbook value 1.81e-5. |
| nu | 1.506e-5 m^2/s | derived: mu/rho |
| POLLEN outer diameter (CFD) | 71.12 mm (R 35.56 mm) | CONFIRMED: CAD, outer vertex radius of the STL |
| Wall | 1.778 mm | CONFIRMED: CAD, vertex radii 33.782-35.56 mm |
| Holes | 26, 0.40-0.44 in (10.2-11.2 mm) | CONFIRMED: 26 from the STL (genus 25); 0.44 in from the STEP, 0.40 in from the print (`research/params_lit.json` geometry_from_cad, grade C) |
| Model R, A | 0.0355 m, A = pi R^2 | CONFIRMED: `src/flight.py` (radius), `src/feasibility.py` (A) |
| Re = v D/nu | 4722 per m/s: 14,170 at 3 m/s, 33,057 at 7 m/s, 51,950 at 11 m/s | derived |
| I (spin decay) | 1.98e-5 kg m^2 (1.73e-5 to 2.36e-5) | `params_lit.json` I_b, grade B |

The CAD is the public AndyMark am-5851 STEP: 175,070 bytes, sha256 `3876dea7...5f445`. It is stored in
`$PM012_CFD_ROOT\dl_am5851_step` and not in git. Its exact download URL was not recorded; the product page is
andymark.com/products/biobuzz-scoring-elements.

`step_to_stl.py` (gmsh, MeshSizeMax 1.2 mm) produced `$PM012_CFD_ROOT\pollen_stl\pollen_mm.stl` (3.2 MB, not in git). The
mesh check gives:
- 64,098 triangles;
- watertight and consistently oriented;
- genus 25 (26 through-holes);
- enclosed material volume 22,312.36 mm^3;
- polar holes on CAD +y, which is also the default spin axis.

## Resolution and GPU memory (derived)

**Memory per cell.** FP16C DDFs take 38 B; rho, u and flags take 17 B; the force field takes 12 B. That is 67 B per cell.

**GPU budget.** The RTX 3060 has 12 GB, about 1.1 GB of it in use, so about 11 GB is free.

**DDF buffer limit.** The single DDF buffer should stay under 3 GiB. NVIDIA OpenCL often reports a maximum allocation
of 25% of VRAM.

| D (cells) | dx (mm) | Wall (cells) | Hole (cells) | Box (D) | Cells | GPU memory | DDF buffer | Use |
|---|---|---|---|---|---|---|---|---|
| 48 | 1.482 | 1.20, **leaks** | 6.9-7.5 | 6x4x4 / 8x5x5 / 10x7x7 | 10.6M / 22.1M / 54.2M | 0.71 / 1.48 / 3.6 GB | 385-1964 MiB | smooth-sphere coarse grid and box study only |
| 80 | 0.889 | 2.0 | 11.4-12.6 | 6x4x4 | 49.2M | 3.3 GB | 1781 MiB | minimum for 2 wall cells |
| **94** | 0.757 | **2.35** | **13.4-14.8** | 6x4x4 | 79.7M | **5.3 GB** | 2890 MiB | **production and fine grid** |
| 96 | 0.741 | 2.40 | 13.7-15.1 | 6x4x4 | 84.9M | 5.7 GB | 3078 MiB (over 3 GiB) | avoided |
| 120 | 0.593 | 3.0 | 17.1-18.9 | 6x4x4 / 5x3.5x3.5 | 165.9M / 105.8M | 11.1 / 7.1 GB | 6012 / 3836 MiB | 3 wall cells; does not fit or has 6.4% blockage |

**Leak criterion** (derived, flat wall, cell-centre voxelization). A fluid-fluid D3Q19 link, at most sqrt(2) dx long,
can cross a wall of thickness t only if sqrt(2) dx > t.

| D | sqrt(2) dx | Compared with t = 1.778 mm | Result |
|---|---|---|---|
| 57 or more | 1.765 mm or less | at or below t | no tunnelling |
| 94 | 1.070 mm | below t | no tunnelling |
| 48 | 2.10 mm | above t | leaks |

So POLLEN runs use D 94. In the 6x4x4 box the solid blockage is 4.9%. The 8x5x5 and 10x7x7 runs measure the effect of
box size.

## Validation (must pass before any POLLEN number is used)

The smooth sphere is voxelized analytically at the same D. Spin is about +y. S = w R/U.

| ID | Case | Grid / box | Reference (source, label) | Acceptance | CFD |
|---|---|---|---|---|---|
| V0 | Rotating sphere in still fluid, Stokes regime (Re_rot 0.4): torque | D 32, cube of side 4 D | Stokes torque 8 pi mu R^3 w (exact, unbounded fluid). The box raises it by 1.003-1.016x (derived): a concentric spherical container of radius R2 gives 1/(1-(R/R2)^3), with R2 between the sphere around the cube (6.9 R) and the sphere inside it (4 R); the equal-volume sphere gives 1.008. | Body torque / Stokes in 0.97-1.10. Cube-flux torques within 2% of the body torque (angular momentum balance). | not run |
| V1a-c | Smooth sphere, Re 3e4, S 0: box size | D 48; 6x4x4, 8x5x5, 10x7x7 | none | Gives the blockage correction | not run |
| V1d | Smooth sphere, Re 3e4, S 0: fine grid | D 94, 6x4x4 | Cd 0.450 (Brown & Lawler 2003, Eq. 19, evaluated, derived). Task band 0.45-0.50. Smooth table-tennis ball in free flight: 0.39-0.43 at Re 3e4, SP 0-0.3 (Sakai et al. 2016, Fig. 7, by eye). | Box-corrected Cd in 0.43-0.50. Change from D 48 to D 94 reported. | not run |
| V2a-b | Rotating smooth sphere, Re 3e4, S 0.5; its S 0 twin is V1 | D 48 and D 94, 6x4x4 | Cl about 0.29 at SP 0.55 (Sakai et al. 2016, Fig. 8, Re 3e4 bin, by eye). Cl 0.26 at Re 3.6e4, Sp 0.5 (Conti et al. 2026, recomputed; unreviewed preprint). Cd about 0.49 near SP 0.5 (Sakai, Fig. 7). | Cl in 0.22-0.33 | not run |
| V3 (optional) | Rotating sphere, Re 1e4, Gamma 0 / 0.2 / 1.0 | D 48, 8x5x5 | Muto et al. 2012 LES, Table I: Cl 0.167 (s.d. 0.029) at Gamma 0.2 and 0.301 (s.d. 0.096) at Gamma 1.0. Cd about 0.45 (Fig. 8), 0.474 and 0.661. The authors flag disagreement in subcritical Cd, and Gamma may be 2S. | Cl within 1 s.d. | not run |

The CFD uncertainty band is the larger of three numbers:
- the V1d Cd error against 0.450;
- the V2 Cl error;
- the D 48 to D 94 change.

Use this band on every POLLEN result.

Kim et al. 2014 covers Re 6e4-2.6e5 (inverse Magnus). That is above this Re range, so it is context only, not an anchor.

## Rerun (Git Bash, from the repo root)

```bash
bash cfd/run_cases.sh build        # prepare_fluidx3d.py (pins the commit, sets defines, applies the patch, copies setup.cpp), then MSBuild
bash cfd/run_cases.sh validate     # V0-V2 + summary + grid comparisons
bash cfd/run_cases.sh muto         # optional V3
bash cfd/run_cases.sh pollen7      # POLLEN static at 7 m/s, two orientations: Cd and runtime
bash cfd/run_cases.sh production   # v 4/7/10 m/s x S 0/0.5/1.0/1.5 (S 0 = no-spin twin)
C:/Python313/python.exe -I cfd/postprocess.py summary cfd/results/p1_pollen_v7_S0_D94_box644.csv
```

A single case, for example POLLEN at 7 m/s with S 0.5:

```bash
$PM012_CFD_ROOT/FluidX3D/bin/FluidX3D.exe body=stl stl=$PM012_CFD_ROOT/pollen_stl/pollen_mm.stl D=94 Re=33057 S=0.5 \
  Lx=6 Ly=4 Lz=4 T=40 out=cfd/results/p2_pollen_v7_S0.5_D94_box644.csv
```

To recreate the STL:

```bash
$PM012_CFD_ROOT/venv/Scripts/python.exe -I cfd/step_to_stl.py <STEP> <out.stl>
```

`setup.cpp` takes these arguments:

| Argument | Meaning |
|---|---|
| `body=sphere\|stl\|rotstokes` | body type |
| `D` | diameter in cells |
| `Re` | Reynolds number |
| `u` | lattice velocity (0.05) |
| `S` | spin ratio |
| `Lx Ly Lz` | box size, in D |
| `xc` | body distance from the inlet (2.5 D) |
| `T` | run length, in t* = D/U |
| `every` | sampling interval |
| `stl Dmm rx ry rz` | STL file, its diameter in mm, and its orientation |
| `revox` | re-voxelize a spinning STL every this many steps |
| `out` | output CSV |

Results go to `cfd/results/*.csv`, which are small and tracked. Logs go to `cfd/results/raw/`, which git ignores.

## Converting to the model's convention

The model uses A = pi R^2 with R = 0.0355 m, S = |w|R/|v| and w(t) = w0 exp(-k t). The CFD references the CAD
R_cfd of 35.56 mm. The conversions (derived; done by `postprocess.py`) are:
- **Drag and lift:** Cd_model = Cd_cfd (R_cfd/R)^2 = 1.0034 Cd_cfd. Cl converts the same way.
- **Spin ratio:** S_model = 0.9983 S_cfd.
- **Spin decay:** k = T/(I w) = CM 0.5 rho v pi R_cfd^4 / (I S). At 7 m/s that is about 1.07 CM/S per second.

## Runtime (PREDICTED, not measured)

These estimates come from the FluidX3D README benchmark for the RTX 3060: 3566 MLUPs/s for FP32/FP16C. The
estimates assume 70-100% of that speed with the extensions enabled.

| Run | Predicted time |
|---|---|
| D 48, 6x4x4, T 40 | 2-3 min |
| D 48, 8x5x5 | 4-6 min |
| D 48, 10x7x7 | 10-14 min |
| D 94, 6x4x4, T 40 (75,200 steps) | 28-40 min |
| Validation set | about 1.2-1.8 h |
| POLLEN static, 7 m/s | about 30-40 min |
| Spinning POLLEN | adds a re-voxelization every 4 / 2 / 1 steps at S 0.5 / 1.0 / 1.5; cost not measured, possibly 2-4x |

## Open risks

- Under-resolved LES, both for the smooth sphere and for flow through the holes. Trust POLLEN numbers only within the
  validation band.
- Re-voxelizing 64k triangles at S 1.5 (every step) may dominate runtime. Options: decimate the STL, or raise `revox`
  after checking that Cl does not change.
- Windows GPU timeout (TDR) during voxelization. FluidX3D's own advice is a TdrDelay registry value, which needs
  the user.
- Free-stream equilibrium faces with 4.9% blockage. V1a-c measures the correction.
- The STEP download URL was not recorded. The hash is recorded above.
- Our force patch has been reviewed but not yet tested. V0 is its test.

## Files

| File | Purpose |
|---|---|
| `fluidx3d/setup.cpp` | Our cases. Altered FluidX3D source. |
| `fluidx3d/prepare_fluidx3d.py` | Pins the commit, sets the defines, applies the force patch, copies setup.cpp. Idempotent. |
| `fluidx3d/LICENSE-FluidX3D.md` | Licence notice. |
| `step_to_stl.py` | STEP to STL conversion and mesh check. |
| `postprocess.py` | Statistics, grid study and model conversion; has `--selftest`. |
| `run_cases.sh` | Build and case list. |
| `.gitignore` | Keeps STL, STEP, VTK, binaries and logs out of git. |

## References

- Brown P.P., Lawler D.F. (2003) Sphere drag and settling velocity revisited. *J. Environ. Eng.* 129(3):222-231,
  doi 10.1061/(ASCE)0733-9372(2003)129:3(222). Eq. 19: Cd = 24/Re (1 + 0.150 Re^0.681) + 0.407/(1 + 8710/Re).
- Sakai W., Miyazaki T., Komatsu T., Takahashi N., Himeno R. (2016) Aerodynamics of a spinning table tennis ball:
  lift crisis. JSME Annual Meeting, J2340102, doi 10.1299/jsmemecj.2016.J2340102 (notes: `research/papers/sakai2016.md`).
- Conti et al. (2026) arXiv:2606.28805v2, unreviewed preprint (checked in `research/checks/sweep_aero.md`).
- Muto M., Tsubokura M., Oshima N. (2012) Negative Magnus lift on a rotating sphere at around the critical Reynolds
  number. *Phys. Fluids* 24:014102, doi 10.1063/1.3673571.
- Kim J., Choi H., Park H., Yoo J.Y. (2014) Inverse Magnus effect on a rotating sphere: when and why. *J. Fluid Mech.*
  754:R2, doi 10.1017/jfm.2014.428.
- Ladd A.J.C. (1994) Numerical simulations of particulate suspensions via a discretized Boltzmann equation, Part 1.
  *J. Fluid Mech.* 271:285-309.
- Krueger T. et al. (2017) *The Lattice Boltzmann Method: Principles and Practice.* Springer.
- Rohde M., Kandhai D., Derksen J.J., Van den Akker H.E.A. (2006) A generic, mass conservative local grid refinement
  technique for lattice-Boltzmann schemes. *Int. J. Numer. Meth. Fluids* 51:439-468, doi 10.1002/fld.1140.
- Latt J., Chopard B. (2006) Lattice Boltzmann method with regularized pre-collision distribution functions.
  *Math. Comput. Simul.* 72:165-168.
- Hou S., Sterling J., Chen S., Doolen G.D. (1996) A lattice Boltzmann subgrid model for high Reynolds number flows.
  *Fields Inst. Commun.* 6:151-166.
- Smagorinsky J. (1963) *Mon. Weather Rev.* 91:99-164.
- Celik I.B. et al. (2008) *J. Fluids Eng.* 130:078001 (GCI).
- Lehmann M. (2022) *Computation* 10:92.
- Lehmann M. et al. (2022) *Phys. Rev. E* 106:015308.
