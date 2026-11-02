#!/usr/bin/env bash
# PM-012: build FluidX3D (outside the repo) and run the PM-012 CFD cases, then summarise them.
# Git Bash, from the repo folder ftc-pollen-magnus:   bash cfd/run_cases.sh build|validate|muto|pollen7|production|summary
# Order: build -> validate (must pass, see cfd/README.md) -> pollen7 -> production.
# Needs permission to build and run third-party code (FluidX3D). Status 2026-10-31: NOT run yet.
set -euo pipefail
CFD=${PM012_CFD_ROOT:?set PM012_CFD_ROOT to a folder outside the repo}
FX=$CFD/FluidX3D
VPY=$CFD/venv/Scripts/python.exe          # venv (gmsh/numpy) for prepare/step_to_stl
SPY=${SPY:-C:/Python313/python.exe}         # standard-library Python for postprocess.py
MSB=${MSB:-"C:/Program Files/Microsoft Visual Studio/18/Community/MSBuild/Current/Bin/amd64/MSBuild.exe"}
EXE=$FX/bin/FluidX3D.exe
STL=$CFD/pollen_stl/pollen_mm.stl           # 64,098 triangles, mm, from cfd/step_to_stl.py (git-ignored, 3.2 MB)
OUT=cfd/results                             # small CSVs (tracked)
RAW=cfd/results/raw                         # console logs (git-ignored)

run() { # run <name> key=value ...   one FluidX3D case -> $OUT/<name>.csv, console log -> $RAW/<name>.log
	local name=$1; shift
	mkdir -p "$OUT" "$RAW"
	if [ -s "$OUT/$name.csv" ] && grep -q "^# runtime_s=" "$OUT/$name.csv"; then echo "skip $name (done)"; return 0; fi
	echo "run  $name: $*"
	"$EXE" "$@" "out=$OUT/$name.csv" > "$RAW/$name.log" 2>&1 || { echo "FAILED $name, see $RAW/$name.log"; return 1; }
	grep -E "PM-012 done" "$RAW/$name.log" || true
}

build() {
	"$VPY" -I cfd/fluidx3d/prepare_fluidx3d.py "$FX"
	"$MSB" "$FX/FluidX3D.sln" -p:Configuration=Release -p:Platform=x64 -p:PlatformToolset=v145 -m -v:m
}

validate() { # smooth sphere, Re 3e4: torque check, box sensitivity, two grids; then spin S 0.5 (its S = 0 twin is V1)
	run v0_rotstokes_D32                 body=rotstokes D=32
	run v1_sphere_Re3e4_S0_D48_box644    body=sphere Re=3e4 S=0   D=48 Lx=6  Ly=4 Lz=4 T=40
	run v1_sphere_Re3e4_S0_D48_box855    body=sphere Re=3e4 S=0   D=48 Lx=8  Ly=5 Lz=5 T=40
	run v1_sphere_Re3e4_S0_D48_box1077   body=sphere Re=3e4 S=0   D=48 Lx=10 Ly=7 Lz=7 T=40
	run v1_sphere_Re3e4_S0_D94_box644    body=sphere Re=3e4 S=0   D=94 Lx=6  Ly=4 Lz=4 T=40
	run v2_sphere_Re3e4_S0.5_D48_box644  body=sphere Re=3e4 S=0.5 D=48 Lx=6  Ly=4 Lz=4 T=40
	run v2_sphere_Re3e4_S0.5_D94_box644  body=sphere Re=3e4 S=0.5 D=94 Lx=6  Ly=4 Lz=4 T=40
	summary
	"$SPY" -I cfd/postprocess.py grid "$OUT/v1_sphere_Re3e4_S0_D48_box644.csv" "$OUT/v1_sphere_Re3e4_S0_D94_box644.csv"
	"$SPY" -I cfd/postprocess.py grid "$OUT/v2_sphere_Re3e4_S0.5_D48_box644.csv" "$OUT/v2_sphere_Re3e4_S0.5_D94_box644.csv"
}

muto() { # optional LES-to-LES check against Muto et al. 2012 Table I (Re 1e4)
	for S in 0 0.2 1.0; do run "v3_sphere_Re1e4_S${S}_D48_box855" body=sphere Re=1e4 S=$S D=48 Lx=8 Ly=5 Lz=5 T=40; done
}

pollen7() { # POLLEN static at 7 m/s (Re = v D/nu = 7*0.07112/1.506e-5 = 33057), runtime measurement; second orientation brackets the hole pattern
	run p1_pollen_v7_S0_D94_box644       body=stl stl=$STL D=94 Re=33057 S=0 Lx=6 Ly=4 Lz=4 T=40
	run p1_pollen_v7_S0_D94_box644_rx90  body=stl stl=$STL D=94 Re=33057 S=0 Lx=6 Ly=4 Lz=4 T=40 rx=90
	"$SPY" -I cfd/postprocess.py summary "$OUT"/p1_*.csv
}

production() { # POLLEN backspin grid after validation passes: v 4/7/10 m/s x S 0 (no-spin twin)/0.5/1.0/1.5; spinning STL is re-voxelized
	local v Re S
	for v in 4 7 10; do
		case $v in 4) Re=18890;; 7) Re=33057;; 10) Re=47224;; esac
		for S in 0 0.5 1.0 1.5; do run "p2_pollen_v${v}_S${S}_D94_box644" body=stl stl=$STL D=94 Re=$Re S=$S Lx=6 Ly=4 Lz=4 T=40; done
	done
	"$SPY" -I cfd/postprocess.py summary "$OUT"/p2_*.csv
}

summary() { "$SPY" -I cfd/postprocess.py summary "$OUT"/*.csv; }

case ${1:-} in
	build|validate|muto|pollen7|production|summary) "$1" ;;
	*) echo "usage: bash cfd/run_cases.sh build|validate|muto|pollen7|production|summary"; exit 2 ;;
esac
