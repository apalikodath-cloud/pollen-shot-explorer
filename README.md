# POLLEN shot explorer

A physics study and an interactive 3D explorer from **FTC Team 207 Critical Mass** (FIRST Tech Challenge
2026-2027, BIOBUZZ). **The question:** can one powered 98 mm flywheel, with a fixed hood or a passive upper
roller, put enough backspin on POLLEN (71 mm, about 25 g, a perforated polyethylene ball) for it to drop into the
upward-facing CELL of the HIVE from the unfavourable side, where the mouth faces away from the robot? The
explorer answers that for any robot position: it solves the flight with drag, spin lift and spin decay against the
official HIVE geometry, and gives the wheel rpm and hood angle that put the ball in clean, each next to the same
shot with no spin.

## Open it

- **Explorer:** https://apalikodath-cloud.github.io/pollen-shot-explorer/
- **CFD flow around the ball along a shot:** https://apalikodath-cloud.github.io/pollen-shot-explorer/flow/shot.html
- **CFD case viewer (13 cases):** https://apalikodath-cloud.github.io/pollen-shot-explorer/flow/flow.html
- **Measurement kit:** https://apalikodath-cloud.github.io/pollen-shot-explorer/measure/measure.html
- **Write-up (PDF):** [`paper/main.pdf`](paper/main.pdf)

> **Everything here is a model prediction.** No POLLEN drag, spin lift, spin decay, bounce or launcher grip
> has been measured. The air coefficients are literature ranges (mostly pickleball and smooth-sphere data),
> not POLLEN facts. One clean simulated shot says nothing about how repeatable a real shot is.

## How to use

1. Open the **Explorer**. It starts on the **Robot** tab ("Where can I shoot from?"). Drag the robot on the field
   map, or drag the white knob to turn it. The turret aims at the up CELL by itself.
2. Under **Shooter settings**, set the shooter height and the backspin. **Advanced settings** hold the rest: grip,
   air, drafts, a moving robot, spin lift, shot scatter, flywheel droop, turret travel and HIVE tilt.
3. Read the **answer card**: the wheel rpm and hood angle for a clean shot from that spot, always beside the
   no-spin twin. "Details" shows the knife edges and clearances.
4. The other tabs: **Side view** ("One shot up close") flies one shot straight down the HIVE tipping plane and
   shows every clean speed and angle from that distance. **Field map** ("Every spot at once") shows where a clean
   shot exists across the field. **CFD** ("Our wind-flow results") shows our CFD coefficients, each backspin case
   beside its no-spin twin.
5. The links under the tabs open the CFD flow pages and the **Measurement kit**. The kit fits drag (Cd) and spin
   lift (Cl) from a slow-motion video of a no-spin shot and its backspin twin. Enter the results in the explorer's
   Advanced settings. The protocol is in [`docs/MEASURE.md`](docs/MEASURE.md).

## How to read the labels

Every number carries one of these labels:

| Label | Meaning |
|---|---|
| CONFIRMED | From the official field CAD or game manual (for example the HIVE section and its 30° tilt). |
| USER | Given by the team (for example the 98 mm wheel). |
| ASSUMED | A modelling choice or a literature value used in place of a measurement (drag, spin lift, spin decay, grip, robot height limits). |
| DERIVED | Computed from the values above (for example wheel rpm from exit speed and grip). |
| PREDICTED | Model output (every clean window, minimum rpm, hood angle and CFD result). |

Terms used in the explorer and the docs:

- **Clean**: the ball centre crosses the CELL mouth inward without touching anything first.
  A shot that touches the HIVE stops there. A real bounce can still score (see `docs/05_contact.md`).
- **No-spin twin**: the same shot (same speed, angle and release point) with no spin. Every backspin result
  is shown next to its twin, so you can see what the spin changes.
- **Tolerant minimum**: the lowest rpm (or hood angle) that still has room for speed and angle to drift and
  stay clean.
- **Knife edge**: the lowest clean shot the solver found at all. It grazes the HIVE. Do not set a robot there.
- **S**: the spin ratio ω R / v (ball surface speed over ball speed). Positive S is backspin.

Two physics points the model is careful about:

- At the top of the arc only the vertical speed is zero. The ball is still moving sideways, and spin does not
  turn into a sudden hook there.
- More backspin is not always better. Spin lift is capped in the model, so past a point extra spin adds
  nothing, and some shots get worse with spin.

## The model in brief

- **Flight.** Gravity, quadratic drag (constant Cd), Magnus lift Cl = min(c1 S, Cl_max) at right angles to the
  velocity, and exponential spin decay with rate k, integrated with RK4 at a 2 ms step (`src/feasibility.py`,
  `viz/explorer/physics.js`). The shot flies in the vertical plane of its bearing; a sideways draft or a moving
  robot switches the browser solver to full 3D flight. An adaptive integrator in `src/flight.py` is the
  reference. The parameter ranges (ASSUMED) are in `research/params_lit.json`, graded in
  `research/LITERATURE_SYNTHESIS.md`.
- **HIVE.** The cross-section comes from the official CAD for both tip states (`docs/01_hive_geometry.md`,
  `src/hive.py`). A 3D CELL built from it, with side walls, roof and lips (`src/cell3d.py`), judges every shot,
  including oblique ones (`viz/explorer/FIELD_DATA.md`).
- **Launcher.** One wheel with a hood or passive roller gives exit speed and spin (`docs/04_launcher.md`,
  `src/launcher.py`). It is uncalibrated: grip and slip are unknown.
- **Contact.** Rim and interior bounces with restitution and Coulomb friction (`docs/05_contact.md`,
  `src/contact.py`), kept separate from clean entry.

**What it finds (PREDICTED).** Clean entry from the unfavourable side is possible, but only as a precision shot.
The clean shots form a narrow diagonal band in exit speed and elevation. Backspin moves the band but is not
required for it, and the unknown aero moves the band more than the band is wide, so the shooter has to be tuned on
the field. Over a whole-field grid, backspin never has a clearly higher model hit chance than the no-spin twin
(`research/SPIN_VS_TWIN.md`). Details are in `docs/08_shooter_spec.md` and `paper/main.pdf`.

## CFD

We run our own **D3Q19 lattice-Boltzmann large-eddy simulation (LES)** on GPUs (OpenCL), with the grid refined
near the ball, to see how air flows around POLLEN with and without backspin.

- The explorer's **CFD** tab lists the mean drag (Cd), spin lift (Cl) and spin-down torque (CM) of each finished
  case, with each backspin case beside its no-spin twin (`viz/explorer/cfd_runs.json`).
- The flow pages show the air in the ball's frame: **streamlines** coloured by speed, **vortex cores**
  (Q isosurfaces), which mark the turbulent wake behind the ball, and **slices** through the flow with contour
  lines. The shot page draws the nearest CFD case around the ball along a predicted shot, beside its no-spin twin.
- Every CFD number and picture is **PREDICTED**. The hole orientation of the ball in flight is **ASSUMED**. The
  flight model still uses the literature aero, not the CFD.
- Solver source, validation rules and run notes: `cfd/README.md`. Flow page tools: `viz/flow/README.md`.

## Repository map

| Path | What it holds |
|---|---|
| `cfd/` | Our lattice-Boltzmann CFD solver (`cfd/lbm/`), post-processing and the validation notes |
| `crosscheck/` | Independent rebuilds of the HIVE geometry and the flight solver, plus empirical evidence notes |
| `data/` | Model outputs (CSV/JSON, PREDICTED unless labelled) and the aero parameter set |
| `docs/` | Write-ups 01-08 (geometry, aero, clean entry, launcher, contact, required vs achievable, test plan, shooter targets), `INTERFACES.md` (frames, units, labels) and `MEASURE.md` (measurement protocol) |
| `figures/` | Figures used by the docs and the paper |
| `paper/` | LaTeX write-up (`main.tex`, `sections/`) and the built `main.pdf` |
| `research/` | Literature synthesis, per-paper notes and checks, the parameter file `params_lit.json` |
| `src/` | Python model: flight, HIVE and 3D cell, feasibility, launcher, contact, robustness, shooter spec, spin vs twin, aero fit |
| `tests/` | Python unit tests and Node checks of the browser solver |
| `viz/` | Web pages and videos: `explorer/` (the explorer and the site build), `flow/` (CFD flow pages), `measure/` (measurement kit), plus side-view shot videos and a replay (`viz/README.md`) |
| `HANDOFF.md` | The original project brief and its rules (section 5) |
| `RESEARCH_PAPERS.md` | Reading list of the main sources |

## Run it

You need Python 3.13 with numpy, scipy and matplotlib (plus Pillow, and optionally imageio-ffmpeg, for the
videos), and Node.js for the browser solver checks. Run everything from the repo root.

**Tests**

```
python -B -m unittest discover -s tests
node tests/js_solver_check.js
```

The Python suite also drives the Node checks, and skips them if Node or the local run caches are missing.
`tests/js_solver_check.js` needs the whole-field data in `viz/explorer/data/field/`, which is not committed: on a
fresh clone it prints `SKIP field data missing` and exits with code 77 until `export_field.py` has been run.

**Model runs** (slow; each writes into `data/`)

```
python -B -m src.shooter_spec                        # design targets (slow; SPEC_WORKERS sets the workers; caches runs in data/_spec_cache)
python -B -m src.feasibility --workers 4             # clean windows
python -B -m src.contact --stage all --workers 4     # contact sweeps
python -B -m src.robustness --steps req,map,mc --workers 3
```

The backspin-against-twin study has its own steps (`src/spin_vs_twin.py`, see `research/SPIN_VS_TWIN.md`).

For the feasibility, contact and robustness runs, `--aero-path <json>` picks the aero file. The default is `research/params_lit.json`. The run caches
(`data/_spec_cache/`) are not committed, so a fresh clone has to run `src.shooter_spec` before the explorer
data can be rebuilt.

## Rebuild the site

```
python -B viz/explorer/export_explorer.py              # model grid for the Side view (from data/_spec_cache)
python -B viz/explorer/export_field.py compute --workers 3
python -B viz/explorer/export_field.py finalize        # whole-field data for the Robot and Field map tabs
python -B viz/explorer/export_cfd.py RUNS_DIR          # optional: CFD tab table from finished run CSVs
python -B viz/explorer/build_site.py                   # explorer + flow pages + measurement kit -> viz/explorer/site/
```

- `viz/explorer/cfd_runs.json` is committed, so `export_cfd.py` is needed only when new CFD runs finish.
- The CFD flow bundles are not committed. `build_site.py` reads them from `viz/flow/flows/` or from the folder in
  the `FLOW_BUNDLES` environment variable, and publishes only real CFD bundles. `viz/flow/README.md` shows how to
  make them.
- Open the result through a web server (for example `python -m http.server` inside `viz/explorer/site`), not as a
  `file://` page. `viz/explorer/HOSTING.md` explains how the site and this repo are published.

**Rebuild the paper**

```
cd paper
pdflatex main.tex
pdflatex main.tex
```

The figures are read from `../figures/`.

## Limitations

- Nothing about POLLEN is measured: drag, spin lift, spin decay, restitution, friction, compression and
  launcher grip are all ASSUMED ranges. The windows move by more than their own width across those ranges.
- Literature values come from other balls, mostly pickleballs and smooth spheres. They are not POLLEN facts.
- The CFD is our own unvalidated model; its results are PREDICTED and are not used in the flight model.
- Sidespin, spin-axis tilt and ball-to-ball variation are not modelled. Drafts and a moving robot are options,
  not measurements.
- Clean entry stops at the first touch. Bounce-in shots are studied separately and are less certain.
- The model makes no claim about repeatability. A clean window is a band of shots the model says go in,
  not a hit rate.
- The release point is the robot centre at the chosen height unless an offset is set, and the turret is assumed
  to aim exactly.

## Credits

FTC Team 207 **Critical Mass**. The HIVE geometry comes from the official FIRST BIOBUZZ field CAD and
competition manual. The POLLEN data comes from the AndyMark scoring-element listing. The literature sources
are listed in `RESEARCH_PAPERS.md` and `research/LITERATURE_SYNTHESIS.md`. FIRST, FTC and BIOBUZZ are
trademarks of their owners. This is an independent team project and is not endorsed by FIRST.

## Licence

TODO (owner): choose a licence. Until one is added, all rights are reserved by the authors.
