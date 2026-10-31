# POLLEN shot explorer

A physics study and an interactive 3D explorer from **FTC Team 207 Critical Mass** (FIRST Tech Challenge
2026-2027, BIOBUZZ).

**The question.** Can one powered 98 mm flywheel, with a fixed hood or a passive upper roller, put enough
backspin on POLLEN (71 mm, about 25 g, a perforated polyethylene ball) for it to drop into the upward-facing
CELL of the HIVE from the unfavourable side, where the mouth faces away from the robot?

**Live explorer:** https://apalikodath-cloud.github.io/pollen-shot-explorer/

The explorer opens in the **Robot** view. Place a robot anywhere on the field, set its heading, turret,
release height, backspin and wheel grip, and the page solves the clean-entry window for that spot in your
browser. It reports the minimum wheel rpm, the minimum hood angle and the most forgiving shot, each beside its
no-spin twin. The **Single plane** view shows the original model grid. The **Field map** view shows
precomputed windows across the field.

> **Everything here is a model prediction.** No POLLEN drag, spin lift, spin decay, bounce or launcher grip
> has been measured. The air coefficients are literature ranges (mostly pickleball and smooth-sphere data),
> not POLLEN facts. One clean simulated shot says nothing about how repeatable a real shot is.

## How to read the labels

Every number carries one of these labels:

| Label | Meaning |
|---|---|
| CONFIRMED | From the official field CAD or game manual (for example the HIVE section and its 30° tilt). |
| USER | Given by the team (for example the 98 mm wheel). |
| ASSUMED | A modelling choice or a literature value used in place of a measurement (drag, spin lift, spin decay, grip, robot height limits). |
| DERIVED | Computed from the values above (for example wheel rpm from exit speed and grip). |
| PREDICTED | Model output (every clean window, minimum rpm and hood angle). |

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

- **Flight.** A planar flight with gravity, quadratic drag (constant Cd), Magnus lift
  Cl = min(c1 S, Cl_max) at right angles to the velocity, and exponential spin decay with rate k.
  It is integrated with RK4 at a 2 ms step (`src/feasibility.py`, `viz/explorer/physics.js`). An adaptive
  integrator in `src/flight.py` serves as the reference. The parameter ranges (ASSUMED) are in
  `research/params_lit.json`, graded against about 25 sources in `research/LITERATURE_SYNTHESIS.md`.
- **HIVE.** The cross-section in its tipping plane comes from the official CAD for both tip states
  (`docs/01_hive_geometry.md`, `src/hive.py`). The obstacles are grown by the ball radius, so the ball can be
  tested as a point.
- **Oblique shots.** A shot from off the tipping plane flies in the vertical plane of its bearing and is
  projected onto the HIVE section at an ASSUMED lateral offset. The CELL side walls are not modelled, so
  steep bearings are optimistic (`viz/explorer/FIELD_DATA.md`).
- **Launcher.** A model of one wheel with a hood or passive roller that gives exit speed and spin
  (`docs/04_launcher.md`, `src/launcher.py`). It is uncalibrated: grip and slip are unknown.
- **Contact.** Rim and interior bounces with restitution and Coulomb friction (`docs/05_contact.md`,
  `src/contact.py`). These are kept separate from clean entry.

**What it finds (PREDICTED).** Clean entry from the unfavourable side is possible, but only as a precision
shot. The clean shots form a narrow diagonal band in exit speed and elevation. Backspin moves the band but is
not required for it, and the unknown aero moves the band more than the band is wide. The shooter has to be
tuned on the field and then hold that tune. Over a whole-field grid, backspin never has a clearly higher model
hit chance than the no-spin twin: tuned to the true lift it is level, and a setting picked without knowing the
lift is lower (`research/SPIN_VS_TWIN.md`, paper section 8). Details are in `docs/08_shooter_spec.md` and
`paper/main.pdf`.

## Repository map

| Path | What it holds |
|---|---|
| `HANDOFF.md` | The original project brief and its binding rules (section 5) |
| `docs/01`-`08` | Geometry, aero, clean entry, launcher, contact, required vs achievable, test plan, shooter design targets |
| `docs/INTERFACES.md` | Frames, units and the provenance labels shared by the code |
| `src/` | Python model: `flight`, `hive`, `feasibility`, `launcher`, `contact`, `robustness`, `shooter_spec`, `spec_figs` |
| `tests/` | Python unit tests and Node checks of the browser solver |
| `data/` | Model outputs (CSV/JSON, all PREDICTED unless labelled) and the first-pass aero set |
| `figures/` | Figures used by the docs and the paper |
| `research/` | Literature synthesis, per-paper notes and checks, the parameter file `params_lit.json` |
| `RESEARCH_PAPERS.md` | Reading list of the main sources |
| `crosscheck/` | Independent re-builds of the HIVE geometry and the flight solver, plus empirical evidence notes |
| `paper/` | LaTeX write-up (`main.tex`, `sections/`) and the built `main.pdf` |
| `viz/explorer/` | The 3D explorer: `page.html`, `physics.js`, `solver.js`, data exporters, site build and deploy scripts |
| `viz/` (rest) | Side-view shot videos with their no-spin twins and a web replay (`viz/README.md`) |

## Run it

You need Python 3.13 with numpy, scipy and matplotlib (plus Pillow, and optionally imageio-ffmpeg, for the
videos), and Node.js for the browser solver checks. Run everything from the repo root.

**Tests**

```
python -B -m unittest discover -s tests
node tests/js_solver_check.js
```

The Python suite also drives `tests/js_oblique_check.js` through Node, and skips those checks if Node or the
local run caches are missing. `tests/js_solver_check.js` needs the whole-field data in `viz/explorer/data/field/`,
which is not committed: on a fresh clone it prints `SKIP field data missing` and exits with code 77 until
`export_field.py` has been run (see **Rebuild the site** below).

**Model runs** (slow; each writes into `data/`)

```
python -B -m src.shooter_spec --workers 4            # design targets (hours; caches runs in data/_spec_cache)
python -B -m src.feasibility --workers 4             # clean windows
python -B -m src.contact --stage all --workers 4     # contact sweeps
python -B -m src.robustness --steps req,map,mc --workers 3
```

`--aero-path <json>` picks the aero file. The default is `research/params_lit.json`. The run caches
(`data/_spec_cache/`) are not committed, so a fresh clone has to run `src.shooter_spec` before the explorer
data can be rebuilt.

**Rebuild the site**

```
python -B viz/explorer/export_explorer.py            # single-plane data from data/_spec_cache
python -B viz/explorer/export_field.py compute --workers 3
python -B viz/explorer/export_field.py finalize      # whole-field data
python -B viz/explorer/build_site.py                 # page.html + physics.js + solver.js -> viz/explorer/site/
```

Open the result through a web server (for example `python -m http.server` inside `viz/explorer/site`),
not as a `file://` page. `viz/explorer/HOSTING.md` explains how the site and this repo are published.

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
- Flight is planar. There is no sidespin, no wind, no spin-axis tilt and no ball-to-ball variation in the
  flight model. The CELL side walls are not modelled for oblique shots.
- Clean entry stops at the first touch. Bounce-in shots are studied separately and are less certain.
- The model makes no claim about repeatability. A clean window is a band of shots the model says go in,
  not a hit rate.
- The release point is the robot centre at the chosen height, and the turret is assumed to aim exactly.

## Credits

FTC Team 207 **Critical Mass**. The HIVE geometry comes from the official FIRST BIOBUZZ field CAD and
competition manual. The POLLEN data comes from the AndyMark scoring-element listing. The literature sources
are listed in `RESEARCH_PAPERS.md` and `research/LITERATURE_SYNTHESIS.md`. FIRST, FTC and BIOBUZZ are
trademarks of their owners. This is an independent team project and is not endorsed by FIRST.

## Licence

TODO (owner): choose a licence. Until one is added, all rights are reserved by the authors.
