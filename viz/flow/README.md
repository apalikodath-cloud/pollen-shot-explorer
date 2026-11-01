# viz/flow: interactive 3D flow viewer

`flow.html` + `flow.js` show a CFD snapshot of the POLLEN ball as dense speed-coloured
streamlines, animated flow dashes, vortex-core (Q) isosurfaces, contour slices and the
holed body. Orbit, pan and zoom (down to about 0.05 D); double-click focuses a point.
Everything shown is **PREDICTED (CFD model output, not a measurement)**. A bundle made
from the synthetic test field is labelled "SYNTHETIC TEST FIELD - not CFD" with a banner.

three.js 0.160.0 loads from cdn.jsdelivr.net through an import map; nothing else is external.

## Make a bundle from a solver snapshot

Needs python3 with numpy, scipy, scikit-image, matplotlib and Pillow.

    python viz/flow/make_flow.py <base>_f<t>.json --fine <base>_solid_fine.json \
        -o viz/flow/flows/<run_id> --label "Re 33057, S 0.5, t* 21"

The raw field stays on the solver machine. Output is about 3-8 MB per snapshot:
`streamlines.bin`, `vortex.bin`, `body.bin`, `slices.bin`, `slice_*.png` and
`manifest.json` (typed arrays with byte offsets, bounds, colour ranges, labels).
Useful options: `--n-up/--n-wake/--n-hole` (seed counts), `--every` (vertex thinning),
`--stride` (grid stride for Q), `--q-fracs` (three Q levels as fractions of the 99.9th
percentile), `--max-faces`, `--slice-up` (slice texture upsampling).

Contour planes: the plane normal to the spin axis comes first (it shows the Magnus-deflected
wake) and is the default; the second is the other plane containing the flow direction.

## Where bundles go

    viz/flow/flows/index.json            {"runs":[{"id","label","path":"<run_id>/manifest.json"}, ...]}
    viz/flow/flows/<run_id>/...          one folder per make_flow.py output

List the no-spin twin and the backspin case in `index.json` to compare them (side by side
or by switching run; the camera is shared). With no runs the page shows an empty state.
`?flows=<dir>` loads a different bundle folder (for local tests).

## Test it without a solver

    python viz/flow/make_test_field.py -o <scratch>/snap                 # no spin
    python viz/flow/make_test_field.py -o <scratch>/snap --name testspin --spin
    python viz/flow/make_flow.py <scratch>/snap/test_f0.json --fine <scratch>/snap/test_f0_solid_fine.json -o viz/flow/flows_test/test_nospin
    python -m http.server   # from viz/flow, open flow.html?flows=flows_test

`flows_test/` is gitignored. Never commit a synthetic bundle under `flows/`.

## Time series (animation)

Pass a glob of snapshot JSON files to make_flow.py to add per-frame slice data:

    python make_flow.py <reference snapshot>.json --fine <base>_solid_fine.json \
        --series "<base>_f*.json" -o flows/<run> --label "POLLEN 7 m/s, no spin" [--u-mps 7 --d-mm 71.12]

`frames.bin` holds, per frame and per slice plane, uint8 speed, int8 vorticity and (first plane only) int8 in-plane velocity, at the snapshot resolution. The viewer colours the slices, draws contour lines (marching squares) and advects particles in the plane from these fields, with play/pause, a frame slider, speed and loop controls. Compare mode plays both runs in sync. The flow is in the ball's frame (ball fixed, air moving past); the elapsed flow time is t* x D/U.

## Shot flow scene (shot.html)

`shot.html` puts a draggable, rotatable robot on the field with the HIVE, draws the
predicted shot (and its no-spin twin) from the explorer physics, and animates the ball
along it. The nearest CFD case is drawn around the ball at true scale (slices with
contours, streamlines, Q surfaces). The CFD +x axis is aligned with the ball's velocity
relative to the air and the spin axis follows the ball's spin. Orientation is ASSUMED.

- Needs the built explorer field data at `../explorer/data/field/index.json`
  (or pass `?field=<url>`), and the flow bundles listed in `flows/index.json`
  (or `?flows=<folder>`).
- Index entries carry `id, label, path, speed_mps, S, orientation, series, n_frames`.
  The nearest case is chosen from speed, S and orientation. Series with 10 or more
  frames count as animated.
- Add a bundle with one command:
  `python make_flow.py <snapshot args> --add-index flows/index.json`
  (`--frame-step N` subsamples a series; short frame files are skipped).
- URL params: `flows, field, x, y, v, th, S, hd, cam, mag, off, plane, anim, t, play, free, hidepanel`.
- Synthetic test bundles show a "SYNTHETIC TEST FIELD, not CFD" banner.
