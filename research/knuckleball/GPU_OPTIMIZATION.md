# GPU optimization of the PM-012 LBM solver on an RTX 3060

Status: analysis note, 2026-11-05. Labels:
- **[M]** measured on the RTX 3060 (12 GB, GA106);
- **[M-c]** measured while other jobs shared the GPU (contended: ratios are indicative, absolute values are not);
- **[V]** vendor figure;
- **[C]** read from the source code (`cfd/lbm/pm012_lbm.cpp`, `cfd/lbm/pm012_lbm.cl`);
- **[D]** derived by hand from [M], [V] and [C];
- **[P]** predicted, not yet measured;
- **[Lit]** from the literature (references in `LITERATURE_REVIEW.md`).

The exclusive benchmark set (section 7) ran on 2026-11-05, one job at a time with the GPU otherwise idle.
Its results are in section 2.4 and replace the earlier predictions in sections 3 to 5.
Items still marked [P] are not measured.

## 0. Summary

1. Production speed is 2912 to 2942 MLUPs counted [M].
   - The hot kernel, `stream_collide`, moves about 255 to 270 GB/s, which is 73 to 77 % of the 350 GB/s DRAM peak [D from M].
   - Well-tuned streaming LBM codes reach 70 to 85 % [Lit], so this kernel is already near the usual ceiling.
2. The solver is limited by memory bandwidth, not by arithmetic.
   - The regularised collision costs the same as BGK (0.985× vs 0.983×) [M].
   - FP32 storage is 0.61× the speed of FP16 [M]. It moves 1.99× the bytes [D].
   - The card ran at 89 % memory-controller utilisation and 161 W of its 170 W power limit [M].
3. In the production case (`bench_d128`), the GPU time splits as [M]:
   - `stream_collide` 83.9 %;
   - `body_force` (the momentum-exchange force sum) 11.3 %;
   - `coalesce` 4.5 %;
   - `diag` 0.3 %.

   The 28 % `body_force` share of the earlier smoke test came from a tiny contended case and does not represent production.
4. Predicted gains:
   - A `body_force` work list (section 5.1) gives about 1.11× [D].
   - With `stream_collide` also raised to 85 % of peak, the realistic total is about 1.2× [D].
   - The hard ceiling at 100 % bandwidth is about 1.4× [D].
5. Faster is not automatically better here. The physics needs long records:
   - wake statistics need at least 1000 D/U [Lit];
   - one D128 case at 150 D/U already takes 3.2 h [M].

   A 1.2× speed-up saves hours. It does not change which questions can be answered.
   More seeds and orientations at D96 are worth more than a faster D128 (see `CFD_TEST_PLAN.md`).

## 1. Hardware and solver facts

| Item | Value | Label |
|---|---|---|
| GPU | RTX 3060 12 GB, 28 SMs, 192-bit GDDR6 | [V] |
| DRAM bandwidth | 360 GB/s spec; 350 GB/s at the observed 7300 MHz memory clock | [V], [D] |
| API | OpenCL 1.2 (NVIDIA). Nsight Compute does not profile OpenCL kernels on this card, hence the in-code event profiler (`prof=1`) | [C] |
| Lattice | D3Q19, two lattices (A/B), pull streaming | [C] |
| Layout | SoA: one buffer per direction; cell index n = x + NX(y + NY z) | [C] |
| Storage | FP16 (`prec=fp16`, default), scaled by 2^15; FP32 option; arithmetic always FP32 | [C] |
| Collision | BGK (default) or regularised (`coll=reg`), Smagorinsky Cs 0.1 | [C] |
| Walls | halfway bounce-back (`wall=hbb`) or interpolated bounce-back with wall distance q (`wall=ibb`) | [C] |
| Refinement | nested boxes, 2:1 per level, sub-cycled (level l does 2^l steps per level-0 step), fine-to-coarse `coalesce` kernel | [C] |
| Spin | prescribed about +y; wall velocity in the bounce-back; the body is re-voxelised every `revox` finest steps (19 at D128) | [C] |
| Launch shape | 1-D NDRange, work-group `wg` (default 128) | [C] |

### Production case (D128, 3 levels; POLLEN; Re 33057; u = 0.05; FP16; BGK; IBB)

| Level | Cells | Updates per level-0 step | Share | Label |
|---|---|---|---|---|
| L0 (D/32) | 192×128×128 = 3.15 M | 3.15 M | 0.9 % | [C] |
| L1 (D/64) | 336×224×224 = 16.86 M | 33.7 M | 9.9 % | [C] |
| L2 (D/128) | 512×384×384 = 75.50 M | 302.0 M | 89.1 % | [C] |
| Total | 95.5 M cells, 7193 MiB | 338.9 M | | [C] |

About 67 % of L0 and 56 % of L1 lie under a finer level and are still updated [D].
That is about 21 M of the 339 M updates per level-0 step (6 %) [D].

## 2. Measured performance

### 2.1 Production throughput [M]

Case: D128 lv3, S = 0.1, alone on the GPU.

| Quantity | Value |
|---|---|
| Counted MLUPs (Σ updates / wall time) | 2907–2912 |
| Time per level-0 step | 0.1164 s |
| Wall time per D/U | about 77 s (t* 0 to 17 in 22 min) |
| nvidia-smi | 100 % GPU, 89 % memory-controller utilisation, SM 1942 MHz, memory 7300 MHz, 161.1 W of 170 W, 9212 MiB |

Note on reporting: the progress line and the last `MLUPs=` value give the *finest-equivalent* rate, N0 × 8^(L−1) per level-0 step.
For multi-level runs this overstates the work actually done. The `# runtime_s` line of the csv gives both numbers.
This note uses counted MLUPs only.

Other counted rates [M], each alone on the GPU:
- D48 lv3 wake run: 3473 MLUPs;
- D128 S0.02: 2782 MLUPs.

The smaller grid runs faster per cell. A likely reason is a larger L2-cache hit share on the coarse levels [P].

### 2.2 FP16 vs FP32 storage [M-c]

Case: D64 lv3, BGK.
- FP16: 1277.5 MLUPs.
- FP32: 627.6 MLUPs.
- Ratio: 2.04.

Both runs shared the GPU with about three other jobs, so the absolute rates are low. The ratio matches the byte ratio (section 3).
The exclusive repeat is `bench_fp32` vs `bench_wg128`.

### 2.3 Per-kernel profile (smoke test) [M-c]

New option `prof=1`: OpenCL profiling events on every launch, drained every 256 launches, written as `# prof` lines to the csv.
Test case: sealed sphere, D = 32, one level, T = 2 D/U, run next to the production case.

| Kernel | Items | Calls | ms per call | Share of GPU time |
|---|---|---|---|---|
| stream_collide | 3.15 M | 1280 | 1.587 | 71.7 % |
| body_force | 64 k (body box) | 1280 | 0.621 | 28.1 % |
| diag | | | | 0.3 % |

Total GPU time was 2.83 s against 5.6 s of wall time; the gap is the shared GPU and start-up.

Per item, `body_force` cost 9.7 ns against 0.50 ns for `stream_collide` [D], that is 19× more per item.

This smoke test is superseded by section 2.4. The case was tiny and the GPU was shared. In the exclusive production profile, `body_force` costs 1.23 ns per item, which is 4.1× the per-update cost of `stream_collide` on L2.

### 2.4 Exclusive benchmarks [M]

All runs were alone on the GPU, in one queue, on 2026-11-05.
- Base case: POLLEN, D64, 3 levels, T = 8 D/U (10240 finest steps), BGK, IBB, S = 0, `prof=1`, wg 128.
- `vs base` is the finest-equivalent rate relative to `bench_noprof`.
- Shares are fractions of the summed GPU kernel time.
- Raw numbers: `data/bench_summary.json`, made by `bench_summary.py`.

| Case | Change | Wall s | Counted MLUPs | Finest-eq. MLUPs | vs base | stream_collide / body_force / coalesce / geo_q |
|---|---|---|---|---|---|---|
| bench_noprof | prof off | 41.3 | 2624 | 6235 | 1.000 | (no profile) |
| bench_wg128 | base, prof on | 42.0 | 2579 | 6130 | 0.983 | 0.769 / 0.149 / 0.077 / 0 |
| bench_wg64 | wg 64 | 42.6 | 2545 | 6048 | 0.970 | 0.749 / 0.165 / 0.081 / 0 |
| bench_wg256 | wg 256 | 42.3 | 2566 | 6098 | 0.978 | 0.758 / 0.157 / 0.080 / 0 |
| bench_wg512 | wg 512 | 44.0 | 2464 | 5855 | 0.939 | 0.763 / 0.160 / 0.071 / 0 |
| bench_fp32 | `prec=fp32` | 68.9 | 1573 | 3739 | 0.600 | 0.876 / 0.093 / 0.028 / 0 |
| bench_reg | `coll=reg` | 42.0 | 2585 | 6143 | 0.985 | 0.765 / 0.150 / 0.079 / 0 |
| bench_hbb | `wall=hbb` | 41.2 | 2629 | 6247 | 1.002 | 0.774 / 0.141 / 0.080 / – |
| bench_lv1 | one level | 82.2 | 3136 | 3136 | 0.503 | 0.921 / 0.076 / – / 0 |
| bench_spin | S = 0.5 | 44.5 | 2438 | 5794 | 0.929 | 0.727 / 0.142 / 0.074 / 0.049 |
| bench_d128 | D128 production grid, T = 1.5 | 110.6 | 2942 | 6992 | 1.121 | 0.839 / 0.113 / 0.045 / 0 |

Findings:
- **Profiler overhead** is 1.7 % (wg128 vs noprof) [M]. The profile does not distort the shares.
- **Work-group size.** 128 is best. 64 and 256 are within 1 %, which is below the unmeasured run-to-run spread. 512 is 4.5 % slower [M]. Keep 128.
- **Collision model.** REG and BGK take the same time (`stream_collide` 31.8 s vs 32.0 s of GPU time) [M]. Arithmetic is free; the kernel is bandwidth-bound.
- **FP32 storage** runs at 0.61× [M], not the 0.50× the byte ratio predicts.
  - The FP32 run moves about 241 GB/s for the whole step, against 199 GB/s for FP16 [D].
  - So the 2-byte FP16 loads leave some bandwidth unused. This is the one sign of latency-bound access (section 5.3) [D].
- **Wall treatment.** IBB costs about 1.3 % of `stream_collide` time over HBB (32.0 s vs 31.6 s) [M]. That is below the noise floor. Wall divergence is not worth optimising.
- **Refinement.** Three nested levels reach the same finest resolution 1.95× faster than one level [M]. Per counted update, one level is 1.22× faster, because it has no `coalesce` and no covered coarse cells [M].
- **Spin.** Re-voxelisation at S = 0.5 takes 4.9 % of GPU time; the whole run is 5.5 % slower [M].
- **Production grid** (`bench_d128`).
  - 0.1152 s per level-0 step, which matches the 0.1164 s of the real production runs (section 2.1).
  - GPU busy 110.4 s of 110.6 s of wall time, so host gaps are under 0.2 %.
  - `stream_collide` on L2 takes 22.76 ms per call for 75.5 M cells. That is 0.301 ns per update, about 255 GB/s at 77 B, or 73 % of peak [D].
  - `body_force` takes 3.24 ms per call for 2.63 M items (1.23 ns per item) [M].

## 3. Bytes per update and the roofline [D]

Per cell update with FP16 storage:
- read 19 × 2 B;
- write 19 × 2 B;
- read 1 B of flags;
- total about 77 B.

With FP32 storage it is about 153 B, a ratio of 1.99.
- The contended ratio of 2.04 (section 2.2) matched this.
- The exclusive ratio is 1.64 (section 2.4), because FP16 does not reach as high a bandwidth as FP32.

Effective bandwidth of the production case (`bench_d128`) [D from M]:
- whole step: 2942 M counted updates/s × 77 B = 227 GB/s (65 % of peak). This includes the time spent in `body_force` and `coalesce`.
- `stream_collide` alone, all levels: 2942 / 0.839 = 3507 M updates/s, × 77 B = 270 GB/s (77 %).
- `stream_collide` on L2 alone: 255 GB/s (73 %). L0 and L1 run faster, probably from L2-cache hits [P].

Well-tuned streaming LBM codes usually reach 70 to 85 % [Lit, Lehmann 2022]. The hot kernel is inside that band. The earlier 60 to 64 % figure mixed in the other kernels' time.

Gain for the whole step [D]:

| Scenario | GPU time per step (production = 1) | Speed-up |
|---|---|---|
| `body_force` work list only (≈ 1 % left) | 0.897 | 1.11× |
| plus `stream_collide` at 85 % of peak | 0.82 | about 1.22× |
| plus `stream_collide` at 100 % of peak (ceiling) | 0.70 | about 1.43× |

**The realistic gain for the whole step is about 1.2×. The hard ceiling is about 1.4×** [D].

The bytes per update are not reduced by:
- Esoteric-Pull streaming, which halves the memory (one lattice instead of two) but moves the same bytes per update [Lit];
- changing the collision model;
- smaller work-groups.

## 4. Where the time goes (production, measured)

Measured shares come from `bench_d128` (S = 0); the revox row comes from `bench_spin` (D64, S = 0.5).

| Item | Work per level-0 step | Earlier prediction | Measured share | Label |
|---|---|---|---|---|
| stream_collide, all levels | 338.9 M updates | 80 to 95 % | 83.9 % (L2 alone 79.2 %) | [M] |
| body_force | 4 launches over the body box (2.63 M items each); about 8 % of the box is wall-adjacent | 3 to 20 % | 11.3 % | [M] |
| coalesce (L1, L2) | about (n/2)³ per level, read 8 cells, write 1 | 1 to 3 % | 4.5 % | [M] |
| revox (geo_solid, geo_commit, geo_q), spinning cases only | every 19 finest steps over the body box | 1 to 5 % at S > 0 | 4.9 % at S = 0.5 (D64) | [M] |
| diag, row read-back | once per csv row (76 finest steps = 19 level-0 steps) | < 0.5 % | 0.3 % | [M] |
| Launch overhead and host sync | about 12 to 15 launches × 5 to 10 µs; one read-back per row | < 0.25 % | GPU idle < 0.2 % of wall time | [M] |

## 5. Optimisation options, ranked by predicted gain per effort

Each item lists the predicted gain [P], the risk, and how a benchmark decides it.

### 5.1 body_force: work list instead of the whole box (rank 1)

**Code facts [C].**
- With `favg=1` (default) the force is accumulated at every finest step.
- `body_force` launches one work-item per cell of the body box.
- Each item:
  - reads its flag and, for wall-adjacent fluid cells, 18 neighbour flags;
  - computes the IBB link force;
  - classifies the link as outer, inner or hole wall (a loop over the hole axes).
- Every work-group then performs 4 passes × 7 levels of a 6-wide local-memory tree reduction with a barrier per level, whether or not it holds a wall cell.

**Option.** At each (re)voxelisation, build a compact list of wall-adjacent fluid cells and launch only over it.
- That is about 2 × 4π × 64² × 2 ≈ 0.2 M cells at D128 instead of 2.46 M [D].
- Replace the tree with sub-group (warp) reductions plus one atomic add per group, or store per-link partial sums.
- Precompute the outer/inner/hole class per list entry.

**Gain.** The measured share at D128 is 11.3 % [M]. Cutting it to about 1 % speeds the case up by about 1.11× [D].

**Risk.** Low. The force is a sum, so the result must match the current kernel to rounding. Check Cd and Cl to 1e-6 on a short case.

### 5.2 Fuse the force into stream_collide (rank 2, only if 5.1 is not enough)

`stream_collide` already loads the populations of wall cells. Accumulating the momentum exchange there saves a second read of 19 populations for those cells.

This adds registers and divergence to the hottest kernel. Predicted gain over 5.1 is small (< 2 %) [P]. Not recommended unless the profile says otherwise.

### 5.3 Bandwidth efficiency of stream_collide (rank 3)

Levers:
1. **Work-group size.** Settled: 128 is best. 64 and 256 are within 1 %; 512 is 4.5 % slower [M]. No change.
2. **Row alignment.**
   - L1 rows are 336 cells × 2 B = 672 B, not a multiple of 128 B, so many warps touch one extra cache line per direction.
   - Padding NX to a multiple of 64 cells costs < 2 % memory. Predicted gain is < 1 % overall, because L1 is 10 % of the work [P].
   - L2 (512) is already aligned [C].
3. **Registers and occupancy.**
   - The kernel keeps 19 inputs and 19 outputs live. With the FP32 Smagorinsky and IBB code, an estimated 90 to 128 registers per thread allow 16 to 22 of 48 warps per SM (33 to 45 % occupancy) [P].
   - For a streaming kernel on Ampere this is usually enough to saturate DRAM. The kernel reaches 73 to 77 % of peak, but FP32 storage reaches a higher bandwidth than FP16 (section 2.4). So the 2-byte loads may not keep enough bytes in flight [D].
   - A possible lever is wider loads (two FP16 values per load where the stencil allows) [P: 0 to +8 % on `stream_collide`].
   - Measurement: dump the PTX through `clGetProgramInfo(CL_PROGRAM_BINARIES)` and run `ptxas -v` to read the register count [M, pending].
   - Then test `-cl-nv-maxrregcount=64/80` as a build option [P: −5 to +10 %; spilling can make it slower].
4. **Branch divergence at walls.**
   - A warp with one IBB cell runs the IBB path for all 32 lanes. Wall cells are 0.3 % of L2 cells, but they lie in about 3 % of warps [D].
   - `bench_hbb` vs `bench_wg128` bounds the whole wall-treatment cost: about 1.3 % of `stream_collide` time [M]. Not worth optimising.

### 5.4 Skip covered coarse cells (rank 4)

About 6 % of updates are for coarse cells under a finer level [D]. Skipping them needs a per-level mask or a cell list, and care at the coalesce boundary.

Predicted gain is ≤ 6 % [P]. Medium risk, because the coalesce stencil relies on the overlap layer.

### 5.5 Esoteric-Pull (memory, not speed)

One lattice in place halves the lattice memory [Lit]. That would allow a finest box about 1.26× larger in each direction, or D160 to D192 grids with the current box, on 12 GB.

Speed is unchanged or slightly lower [P]. The grid study (`CFD_TEST_PLAN.md` §4.1.1) found that the mean forces at D128 are within 2.2 % of D192, and D192 already fits on 12 GB. The fluctuation statistics are limited by record length, not grid, so this option is not needed now [P].

### 5.6 Options not recommended

- **AoS layout.** It breaks coalescing for 2-byte pull reads. SoA is the right layout for this pattern [Lit, P].
- **FP32 storage by default.** It runs at 0.61× the speed of FP16 [M] (2.04× slower when contended [M-c]).
  - FP16 with scaling is validated in the literature for flows like this [Lit, Lehmann 2022].
  - It is validated here by `p_fp32_d64` vs `p_grid_d64` (`CFD_TEST_PLAN.md` §4.1.1) [P]: Cd +0.6 %, Cl +0.001, sd Cy +7 %, sd Cl −8 %, fluctuating miss −11 %. That is inside every tolerance except the Strouhal peak, which is unreliable on records this short.
  - Keep FP16.
- **Temporal blocking or shared-memory tiling of several steps.** For D3Q19 with 48 KB of shared memory per block the gain is uncertain (≤ 1.5× in the literature for simpler stencils) [P]. Interaction with refinement and IBB is complex. High effort for at most the roofline gap.
- **More launches fused to cut overhead.** Launch overhead is < 0.2 % [P].
- **Sparse storage of the fluid region.** The ball is about 1.5 % of the finest box [D], and the far field is already coarse thanks to the nesting. Little to gain.
- **AMR (dynamic refinement).** The wake region the questions need is fixed in the body frame; a static nested box is the right choice [P].

## 6. Effect on the research questions [D]

| Run | Wall time at measured rates |
|---|---|
| D128 lv3, 150 D/U | 3.2 h [M] |
| D128 lv3, 1000 D/U (converged wake statistics) | about 21 h |
| D64 lv3, 1000 D/U | 8× fewer cells and 2× fewer steps, about 1.4 h (if MLUPs are similar) |
| D96 lv3, 1000 D/U | about 7 h (0.42× the cells, 0.75× the steps) |

Even the 1.4× ceiling (section 3) leaves D128 at about 15 h per 1000 D/U. The realistic 1.2× leaves about 17.5 h.

The binding limits are sampling and statistics, not speed:
- one flight is only 30 to 55 D/U [D];
- wake states switch on a scale of 10³ D/U [Lit].

The useful plan is therefore many independent short records (seeds × orientations) at D96 to D128 and a few long ones at D64 to D96.

Speed work is worth doing only for 5.1. Its measured share is 11.3 %, above the 5 % threshold set before the benchmarks, so 5.1 is worth building.

## 7. Benchmark plan (ran 2026-11-05, exclusive, one job at a time)

Base case: POLLEN, D64, 3 levels, T = 8 D/U, BGK, IBB, S = 0, Re 33057, production geometry and orientation. All cases except `bench_noprof` use `prof=1`.

| Case | Change | Answers |
|---|---|---|
| bench_noprof | prof off, wg 128 | profiler overhead (vs bench_wg128) |
| bench_wg64 / 128 / 256 / 512 | work-group size | launch shape, occupancy proxy |
| bench_fp32 | `prec=fp32` | exclusive FP16/FP32 ratio |
| bench_reg | `coll=reg` | collision cost (expected ≈ 0 if bandwidth-bound) |
| bench_hbb | `wall=hbb` | wall-treatment cost (IBB vs halfway) |
| bench_lv1 | one level | refinement and coalesce overhead per update |
| bench_d128 | D128, T = 1.5 | production per-kernel shares, body_force share |
| bench_spin | S = 0.5 | revox cost in spinning cases |

Pass rules:
- A change is adopted only if it is faster by more than 3 % (the run-to-run spread is not yet measured; two repeats are needed before any change under 5 % is believed).
- The force coefficients over the same window must agree to rounding (5.1) or within the validation band (`CFD_TEST_PLAN.md`).

Results are in section 2.4, and the [P] values in section 4 are replaced.
- Each case ran once. Repeats are still needed to measure the run-to-run spread.
- No code change was adopted. The only change that passes the 3 % rule is wg 512 → 128, and 128 is already the default.
