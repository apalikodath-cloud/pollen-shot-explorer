# Shared interfaces (PM-001)

All parallel agents code against these contracts so their pieces fit. SI units everywhere (m, s, kg, rad). Python 3.13 + numpy/scipy/matplotlib only; no pytest, tests use `unittest` (`python -m unittest discover -s tests -v` from the repo root). Every numeric input carries provenance: `confirmed` (official source, cite URL + section), `measured` (none yet), `user` (user-stated), `assumed` (modeling assumption) or `derived` (computed from the others; give formula).

## Frames
- HIVE frame for the 2D tipping-plane cross-section: origin on the tile surface directly below the alliance HIVE pivot axis; z up; x horizontal, perpendicular to the pivot axis (i.e. in the plane the CELLS tip in); y along the pivot axis.
- Shots are fired from x<0 toward +x or from x>0 toward -x. The solver mirrors geometry rather than duplicating it.
- Pose names: `pose_neg` = the pose whose upward-facing CELL sits on the -x side of the pivot; `pose_pos` = mirror. For each pose the geometry file states which shooting side is `favorable` and which is `unfavorable`, with the reasoning.

## data/hive_geometry.json
```
{
  "units": "m",
  "ball_radius": {"value": 0.0355, "prov": "..."},
  "pivot": {"x": 0.0, "z": ..., "prov": "..."},
  "poses": {
    "pose_neg": {
      "tilt_deg": {"value": ..., "low": ..., "high": ..., "prov": "..."},
      "obstacles": [ {"name": "cell_floor", "p0": [x,z], "p1": [x,z], "prov": "..."}, ... ],   // 2D segments, solid geometry (NOT inflated)
      "mouth": {"p0": [x,z], "p1": [x,z]},          // the opening line of the upward-facing CELL
      "inside": [[x,z], ...],                       // polygon: ball CENTER inside here = scored (retained)
      "favorable_side": "neg" | "pos", "reason": "..."
    },
    "pose_pos": { ... mirror ... }
  },
  "y_extent": {"cell_width": ..., "prov": "..."},  // for later 3D
  "open_questions": ["..."]
}
```
Where an official value is missing, give `low`/`high` bounds and mark `assumed`; never invent a single precise number.

## data/aero_params.json
```
{
  "rho": {...}, "mass": {...}, "radius": {...},
  "I_b": {"value": ..., "low": ..., "high": ..., "prov": "..."},   // hollow perforated shell; thin-shell 2/3 m R^2 is an upper-ish bound
  "Cd": {"low": ..., "nominal": ..., "high": ..., "prov": "..."},
  "Cl": {"model": "linear_capped", "formula": "Cl = min(c1*S, Cl_max)",
         "sets": {"low": {"c1": ..., "Cl_max": ...}, "nominal": {...}, "high": {...}}, "prov": "..."},
  "spin_decay_k": {"low": ..., "nominal": ..., "high": ..., "units": "1/s", "prov": "..."},
  "Re_range_note": "...",
  "sources": [ {"cite": "...", "url": "...", "what_it_gives": "..."} ]
}
```

## src/flight.py (free flight)
- `simulate(x0, v0, omega0, params, wind=(0,0,0), t_max=3.0, dt_max=1e-3, stop=None) -> Trajectory` where x0, v0, omega0 are 3-vectors (2D shots use y=0, omega along ±y). `params` is a dict with rho, mass, radius, Cd, Cl callable or (c1, Cl_max), spin_decay_k.
- `Trajectory` has arrays `t, pos (N,3), vel (N,3), omega (N,3)` plus `apex()` returning the state at the vz=0 crossing and `magnus_force(i)` / `drag_force(i)`.
- Backspin convention: for a ball moving +x, backspin is omega along -y, so that omega × v points +z. Helper `backspin_omega(v_dir, spin_rad_s)` builds the vector. Unit-tested.
- Aero forces → 0 smoothly as |v_rel| → 0 (no S singularity).

## src/launcher.py (single 98 mm flywheel)
- `hood_ideal(wheel_rpm_exit) -> (v_exit, omega_exit)` and the full impulse/slip model `hood_model(...)`, `roller_model(...)` with flywheel inertia, RPM drop, friction, compression, ball I_b, roller inertia/bearing drag.
- Writes `data/launch_envelope.json`: achievable (v_exit, spin_rpm, S) region per configuration, with the assumptions listed.

## src/hive.py, src/contact.py, src/feasibility.py
- `hive.py` loads hive_geometry.json, mirrors poses, gives ball-center clearance (segments inflated by ball radius) and `classify(traj, pose, side) -> "clean" | "hit:<name>" | "miss"`.
- `contact.py` rim/interior impact: normal restitution e, Coulomb friction mu, spin update with I_b; repeated contacts; outcome retained/bounced.
- `feasibility.py` sweeps and writes `data/*.csv` and `figures/*.png`.
