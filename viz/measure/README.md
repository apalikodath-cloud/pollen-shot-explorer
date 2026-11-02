# viz/measure: POLLEN measurement kit (PM-018)

`measure.html` is a browser page for tracking a slow-motion side-view video of a POLLEN shot by hand. From the
track it fits drag (Cd) on a no-spin shot and spin lift (Cl) on a backspin shot. Files are read locally in the page
and nothing is uploaded. The full protocol is in [docs/MEASURE.md](../../docs/MEASURE.md).

## Open it

Serve the `viz/` folder, because the page loads `../explorer/physics.js`:

```
cd viz
python -m http.server 8718
```

Then open `http://127.0.0.1:8718/measure/measure.html`. Opening the file directly from disk also works in most
browsers. Two hashes help with checks:

- `#demo` loads the synthetic demo.
- `#demo-fit` loads the demo and runs Fit A, then Fit B.

`shotlab.html` (the Shot Lab) also needs the field data at `../explorer/data/field/index.json`, which
`viz/explorer/build_site.py` writes. Its hashes: `#demo` loads demo shots and telemetry and builds the rpm map,
`#demo-lip` also runs the lip test, and `move` in the hash also runs the shoot-on-the-move 3D check.

## Files

| File | What it is |
|---|---|
| `measure.html` | The page: layout, styles and controls. |
| `measure.js` | Fit core (UMD; it also runs under node) plus the page UI. The equations are the explorer's `physics.js` `integrate` (RK4). |
| `../../src/fit_aero.py` | The same fit in Python, for a CSV pasted out of the page: `python -B -m src.fit_aero track.csv [--lift single\|linear\|capped] [--scale clicked\|gravity] [--boot 200]`. |
| `tracker.js` | Auto-track: follows the ball by colour against a median background from one click (UMD; tested under node). |
| `assist.js` | Telemetry parsing, column guessing, launch-dip detection and the Shot Lab log (local storage). |
| `shotlab.html`, `shotlab.js` | The Shot Lab page. |
| `shotlab_worker.js` | Web worker for the Shot Lab's model jobs: rpm map, lip test, shoot-on-the-move check (also loads under node). |
| `shotcore.js` | Pure maths for the Shot Lab: fits, sag compensation, interpolation, virtual target, lip distance and the Java generators. |
| `../../tests/test_tracker.py`, `test_assist.py`, `test_shotcore.py`, `test_shotlab.py` | Node-run tests for the files above. |
| `../../tests/test_fit_aero.py` | Python matches `physics.js`; JS and Python agree; fits recover noisy synthetic tracks; the identifiability flags fire. |

## What the page does

1. **Source.** Load a video (stepped one frame at a time) or an image sequence. Enter the capture fps; phone slow
   motion often saves 240 fps capture as a 30 fps file.
2. **Scale and level.** Click both ends of a known length, ideally a bar of 1 m or more lying in the flight plane.
   Level is optional: two points on a level line.
3. **Track.** Click the ball centre on each frame. Use ← and → to step, Shift for ×10, Backspace to delete and Z
   for the loupe. Shot A is the no-spin twin and shot B is the backspin shot, at the same settings.
4. **Fit.** Fit A gives v0, the launch angle and Cd, plus a gravity check of the scale. Fit B holds A's Cd and
   gives Cl, with the no-spin twin path drawn dashed beside it.
5. **CSV.** The track lands in a text box with a Copy button, and "Load from text" reads it back in.
6. **Auto-track and telemetry.** Optional helpers: the tracker follows the ball from one click (check every
   point), and a robot log gives the wheel rpm and battery volts at the launch. "Add shot to the Shot Lab log"
   keeps the shot for the Shot Lab (docs/MEASURE.md §9–10).

Every number on the page carries a label: user, ASSUMED, derived or PREDICTED. The demo is synthetic: it is
`physics.js` run with ASSUMED values plus click noise. It is not a POLLEN measurement.
