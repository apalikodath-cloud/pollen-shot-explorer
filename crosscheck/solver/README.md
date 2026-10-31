# crosscheck/solver: blind cross-check of the POLLEN free-flight model

Task PM-001, written 2026-10-30. This is an independent re-implementation of HANDOFF §4A. It was written **without opening `src/` or `docs/`**, so it can be used to cross-validate `src/flight.py`.

| File | What it is |
|---|---|
| `xflight.py` | Independent solver: fixed-step classical RK4 (no `solve_ivp`), step halving until positions at shared nodes change by < 1e-8 m, cubic-Hermite event location. Run `python xflight.py --selftest` or `python xflight.py --write-cases [--g 9.80665]`. |
| `reference_cases.json` | 24 reference cases. Each has inputs, outputs and its spin/no-spin twin comparison. `meta` records every parameter, its label and every definition. |
| `compare.py` | Harness. It runs any solver through a small adapter and extracts all metrics with the same event code, then checks them against the JSON. |

## Model (from HANDOFF §4A only)
Frame: x points toward the target, z points up, and y = z × x (left). The state is the ball **centre**, which is released at x = 0 in the x-z plane.

```
m dv/dt = m(0,0,-g) - 0.5 rho Cd A |v_rel| v_rel + 0.5 rho Cl A |v_rel|^2 unit(omega x v_rel)
v_rel = v - v_wind     A = pi R^2     S(t) = |omega(t)| R / max(|v_rel|, eps_v)
Cl = min(c1 S(t), Cl_max)     omega(t) = omega0 exp(-k t) * axis     omega0 = S0 |v_rel(0)| / R
```
- **S is recomputed in flight.** S0 is only the spin parameter at release. As the ball slows, S rises, so with these placeholders Cl saturates at Cl_max for most of every spin case.
- **Backspin axis = (0, −1, 0)**, derived and asserted in `backspin_axis_check()`. The top of the ball must move in −x, so ω × ẑ = −x̂, which gives ω ∥ −ŷ. The Magnus direction is then (−ŷ) × x̂ = +ẑ, i.e. up. The force points rearward on the way up and forward on the way down.
- Regularisation: Cl has a ceiling, so both forces go to 0 as |v| goes to 0. If ω × v_rel = 0, the Magnus term is 0.

## Placeholder parameters (stated in the JSON `meta.parameters`)
| Parameter | Value | Label |
|---|---|---|
| m | 0.025 kg | user/HANDOFF (AndyMark nominal 0.055 lb ≈ 24.95 g; not re-verified by me) |
| R | 0.0355 m | user/HANDOFF (official nominal 71 mm) |
| rho | 1.225 kg/m³ | assumed (ISA sea level) |
| Cd | 0.5 | **assumed placeholder**, uncalibrated |
| c1 | 0.3 | **assumed placeholder**, uncalibrated |
| Cl_max | 0.35 | **assumed placeholder**, uncalibrated |
| k_spin | 0 or 0.5 1/s | **assumed placeholder** |
| g | 9.81 m/s² | assumed. **It must match src.** |
| wind | 0 | assumed for all 24 cases (the solver supports wind) |
| z0 | 0.3 m (release height of the ball centre) | user/task |

Every output is **predicted**: it is model output under these placeholders. None of it is a measured POLLEN property.

## Case design (24 cases)
There are 4 launch states, (v0 m/s, elev °) = (3, 80), (5, 55), (7.5, 70), (10, 30), each run with 6 spin settings (S0, k) = (0,0), (0.5,0), (1,0), (2,0), (0.5,0.5), (1,0.5). The S0 = 0 case is the no-spin twin of its launch state (`twin_id`). I left out (2, 0.5) because Cl is saturated throughout, so it gives exactly the same result as (2, 0). Cases 01–06 never reach z = 1.0 m, so their `z1p0` is `null` on purpose: this checks how the main solver handles null crossings.

Output fields per case:
- `apex`: the first crossing of vz from + to 0. It gives t, x, z and vx, plus ω, S, Cl, |F_M| and a_M at the apex.
- `z1p0`, `z0p3`: the **last descending** crossing of z = 1.0 m and of z = 0.3 m, giving t, x, vx and vz. `ground_R` is the same for z = R (the ball bottom touches the tiles).
- `flight_time_s`: the time to return to the release height z0 = 0.3 m. **It is not the time to reach the ground.**
- `spin_vs_nospin.equal_x`: the maximum of |z_spin(x) − z_nospin(x)| over x from 0 to the smaller of the two `z0p3` x values. It records where the maximum occurs (x, z_spin, t_spin) and whether that point is the end of the common range.
- `spin_vs_nospin.equal_t`: the same comparison at equal times, over t from 0 to the smaller flight time.
- `spin_vs_nospin` also holds `dx_at_z1p0_m`, `dx_at_z0p3_m` and `dz_apex_m`, each computed as spin minus no-spin.
- `min_vx_m_s` and `horizontal_reversal`: the explicit mid-air reversal test from HANDOFF §0.

## How the lead should compare against `src/flight.py`
1. Use the same inputs. Set src to the JSON's m, R, rho, Cd, c1, Cl_max, k_spin, g and wind = 0, with release at (0, 0.3) and a backspin of S0 at release. **Check these four points first:**
   - **g.** If src uses 9.80665, rerun `python xflight.py --write-cases --g 9.80665`. The 0.003 m/s² difference alone fails 23/24 cases at 1 mm (negative control, below).
   - **S0 at release vs S in flight.** Does src set Cl from S0 at release, or recompute S as the ball slows? This file recomputes it in flight (HANDOFF §4A). If src holds S fixed, the spin cases will differ by centimetres.
   - **Spin decay.** This file uses the analytic ω0·exp(−kt), and src should match. If src integrates dω/dt = −kω, that is the same thing.
   - **z is the ball centre**, and flight time means the return to 0.3 m.
2. Write an adapter: `run(inputs: dict, params: dict) -> {"t","x","z","vx","vz"}`. It should call src and return a dense trajectory (dt ≤ 1e-3 s, e.g. from `dense_output`) running from release until z < 0.
3. Run `python crosscheck/solver/compare.py --adapter my_adapter:run` from the project root. The harness puts the current directory on `sys.path`, so `my_adapter.py` can sit in the root or in a scratch folder.
4. Tolerances: **lengths 1 mm** (apex x/z, x at z = 1.0 and 0.3, max Δz and its x location), times 0.5 ms and velocities 1 mm/s. The exit code is 0 only if everything passes.
5. Self-demo: `python crosscheck/solver/compare.py --adapter compare:example_adapter` runs scipy DOP853 on xflight's own physics. It shows the harness works and nothing more. Result: 0 FAILs over 24 cases.

The harness extracts events from your trajectory using finite-difference vz' for the Hermite apex. That adds about 1e-7 m of error, which is negligible at a 1 mm tolerance.

## Validation done here (all predicted/derived, reproducible with `--selftest`)
| Check | Result |
|---|---|
| Backspin sign: top surface moves −x, lift is +z, force rearward on ascent and forward on descent | asserted, PASS |
| HANDOFF scale check: 5 m/s, Cl = 0.20 → 0.485 m/s² | PASS |
| v = 0 regularisation: only gravity remains | PASS |
| Vacuum vs closed form (apex t/z, range, time of flight) | 8e-14 m |
| Quadratic drag, vertical shot vs closed-form apex height and time | 3e-13 |
| RK4 vs scipy DOP853 (rtol 1e-12), v 7.5, 70°, S0 2, k 0.5 | 1.1e-9 m |
| Step halving, final dt | 1e-3 to 2.5e-4 s, < 1e-8 m change |
| Negative control g = 9.80665 instead of 9.81 | 23/24 cases FAIL (harness is sensitive enough) |
| Negative control with the spin axis flipped | 202 metric FAILs |

## Predicted observations under these placeholders (not measurements)
- **No horizontal reversal in any case.** The lowest vx is 0.48 m/s, in the 3 m/s, 80° case.
- **Backspin can shorten or lengthen the range depending on the shot:**
  - High lob at 7.5 m/s, 70°: backspin **shortens** the return-to-0.3 m point by 0.14–0.28 m. Over the long, steep climb the Magnus force points rearward.
  - Flat shot at 10 m/s, 30°: backspin **lengthens** it by 0.46–1.01 m.

  So "more backspin always helps" (HANDOFF §5) is not true here either.
- **At the apex the Magnus acceleration is small when the ball is slow,** because a_M scales with |v|², even when S is large:
  - 3 m/s, 80°: a_M ≈ 0.008 m/s² (S ≈ 3–12)
  - 10 m/s, 30°: about 1.5 m/s²
- **The largest Δz at equal x usually comes at the end of the common range** (near landing), not at the apex. It reaches 0.80 m for the 7.5 m/s, 70° lob with S0 = 2. That metric therefore depends on the definition of the comparison range, which is why the range is given in the JSON.
- **Cl is saturated:** with c1 = 0.3 and Cl_max = 0.35, Cl reaches its ceiling for any S ≥ 1.17. Cases with S0 = 1 and S0 = 2 differ by only a few mm to 3 cm. Real POLLEN data on Cl(S) would change this.
