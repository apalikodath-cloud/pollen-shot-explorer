# viz/flow: interactive 3D flow viewers

Two pages, both showing **PREDICTED** results (CFD model output, not a measurement):

- `flow.html` + `flow.js` (+ `flowview.js`, shared): one CFD case of the POLLEN ball as
  speed-coloured streamlines, animated flow dashes, vortex cores (Q-criterion surfaces),
  contour slices and the holed body. Orbit, pan and zoom (down to about 0.05 D); double-click
  focuses a point. A backspin case opens next to its no-spin twin at the same speed.
  The view is the solver frame: lift (+z) up, the air (+x) running left to right, the spin axis
  (+y) pointing away from the camera. The ball turns backspin about +y like the solver's body
  (2 S rad per unit t*): in Instant it follows the CFD time (`body_t_star` is the time of the
  body mesh), in Averaged it turns slowly to show the sense.
  Bundles with a 3D velocity volume (`make_vol.py`, below) also get `particles.js`: GPU tracer
  particles with fading trails (released upstream, all over the ball and in the wake), a glowing
  ray-marched vortex volume, and lift pairs (see below). These replace the streamlines and tubes
  as the default layers; the older layers stay in the panel.
- `shot.html` + `shot.js`: a robot on the field with the HIVE, the predicted shot and its
  no-spin twin from the explorer physics, and the CFD flow drawn around each ball along the flight.
  The explorer's "3D flow" tab embeds this page and drives it with the Robot tab's current shot.

Live: https://apalikodath-cloud.github.io/pollen-shot-explorer/flow/shot.html and
https://apalikodath-cloud.github.io/pollen-shot-explorer/flow/flow.html

three.js 0.160.0 loads from cdn.jsdelivr.net through an import map; nothing else is external.
A bundle made from the synthetic test field is labelled "SYNTHETIC TEST FIELD - not CFD" with a banner.

All commands below run from the repository root.

## Instant and Averaged

Each view has an Instant / Averaged switch. Instant shows one saved moment of the turbulent
(LES) wake: the tubes are vortex cores (Q-criterion) of that moment and the blotchy slice is the
same turbulence, not a model error. Averaged shows the time-mean flow over the saved frames
(bundles made with `--mean`; without it the page falls back to Instant).

Slices and streamlines are coloured by air speed relative to the ball in m/s, on one scale
shared by every case on screen.

## Make a bundle from a solver snapshot

Needs python3 with numpy, scipy, scikit-image, matplotlib and Pillow.

    python viz/flow/make_flow.py <base>_f<t>.json --fine <base>_solid_fine.json \
        -o viz/flow/flows/<run_id> --label "Re 33057, S 0.5, t* 21"

The raw field stays on the solver machine. Output is about 3-8 MB per snapshot:
`streamlines.bin`, `vortex.bin`, `body.bin`, `slices.bin`, `slice_*.png` and
`manifest.json` (typed arrays with byte offsets, bounds, colour ranges, labels).
Useful options: `--n-up/--n-wake/--n-hole` (seed counts), `--every` (vertex thinning),
`--stride` (grid stride for Q), `--q-levels` (Q iso-levels in (U/D)^2), `--max-faces`,
`--slice-up` (slice texture upsampling), `--orientation` (hole orientation tag, ASSUMED).

Contour planes: the plane normal to the spin axis comes first (it shows the Magnus-deflected
wake) and is the default; the second is the other plane containing the flow direction.

### Time series and the averaged field

Pass a glob of snapshot JSON files to add per-frame slice data, and `--mean` to also write
the time-mean field (velocity averaged over the series frames; all static layers are then
built from the mean as well):

    python viz/flow/make_flow.py <reference snapshot>.json --fine <base>_solid_fine.json \
        --series "<base>_f*.json" --mean -o viz/flow/flows/<run_id> \
        --label "POLLEN 7 m/s, S 0.5" --u-mps 7 --add-index viz/flow/flows/index.json

`frames.bin` holds, per frame and per slice plane, uint8 speed, int8 vorticity and (first plane
only) int8 in-plane velocity. The viewer colours the slices, draws contour lines and advects
particles in the plane from these fields. The flow is in the ball's frame (ball fixed, air
moving past); the elapsed flow time is t* x D/U. `--frame-step N` keeps every Nth frame;
incomplete frame files are skipped. `--add-index` adds or updates the bundle's entry in
`index.json` (id, label, path, speed_mps, S, orientation, series, n_frames, mean).

## 3D tracers, vortex volume and lift pairs (`make_vol.py`, `particles.js`)

    python viz/flow/make_vol.py <bundle_dir> --series "<fields>/<run>_f*.json" [--ds 2]

adds `vol/fNNN.vgz` (one per frame in the bundle's manifest) and, for a bundle with a time mean,
`vol/mean.vgz`, plus a `vol` section in `manifest.json` (size, origin of the first voxel centre,
dx, vel_scale, q_scale). Each file is a gzip of int8 RGBA voxels, x fastest, on the solver grid
coarsened `ds` times (block mean): RGB = velocity / vel_scale x 127 (U units), A = sign of the
streamwise vorticity x sqrt(max(Q, 0)) / q_scale x 127 (U/D), Q from the full-resolution field.
About 0.6 MB per frame at `--ds 2`. Run it after `make_flow.py`, on the same snapshots.

The viewer loads the volume into a 3D texture (WebGL2 with float render targets; without them
the panel says so and the old layers stay). On the GPU, tracers are advected with RK2 through
the two saved frames around the current time, blended linearly; a tracer that leaves the box,
stops on the ball or ages out is released again. These layers are added on top of the old ones:
streamlines, vortex cores, slices and the 2D particles keep their usual defaults. Play keeps the
usual frame pace; tick "Tracer pace" (`sync=1`) to run the CFD time at 0.8 t* per second (x the
speed menu) so tracers and field stay in step. Paused, the tracers keep moving through the frozen
field. The vortex volume ray-marches |A| above the vortex-level
threshold, red for vortices turning with the flow and blue against; it fades out within 0.1 D
of the wall, where the zeroed solid velocity spoils the Q estimate.

Lift pairs: every 1.6 t* a vertical line of 37 tracers is released at x = -0.68 D (a timeline,
advected on the CPU through the same field). The tracers at z = +0.6 D (orange) and -0.6 D
(blue) are a pair joined by a thin line. When both have passed x = 1 D the page records how much
sooner the top one got there and shows the mean of the last 8 pairs in t* and ms. Faster flow
over the top than under the bottom means the air is turned down behind the ball, which is the
lift. Always read it next to the no-spin twin. PREDICTED, and tracers are massless (they follow
the air exactly; a real smoke speck would lag a little).

## Where bundles go

    viz/flow/flows/index.json            {"runs":[{"id","label","path":"<run_id>/manifest.json", ...}, ...]}
    viz/flow/flows/<run_id>/...          one folder per make_flow.py output

Flow bundles are not committed: in the repository `viz/flow/flows/index.json` is
`{"runs":[]}` and the pages show an empty state. `viz/explorer/build_site.py` reads the bundles
from `viz/flow/flows` (or the folder in the `FLOW_BUNDLES` environment variable), publishes
only the non-synthetic bundles listed in its `index.json`, and writes a matching
`site/flow/flows/index.json`:

    FLOW_BUNDLES=<bundle folder> python -B viz/explorer/build_site.py

It also rewrites the shot scene's field-data path to `../data/field/index.json` and the pages'
back links to `../index.html` for the site layout.

## Test it without a solver

    python viz/flow/make_test_field.py -o <scratch>/snap                 # no spin
    python viz/flow/make_test_field.py -o <scratch>/snap --name testspin --spin
    python viz/flow/make_flow.py <scratch>/snap/test_f0.json --fine <scratch>/snap/test_f0_solid_fine.json \
        -o viz/flow/flows_test/test_nospin --add-index viz/flow/flows_test/index.json
    python -m http.server -d viz           # open http://localhost:8000/flow/flow.html?flows=flows_test

`flows_test/` is gitignored. Never commit a synthetic bundle under `flows/`.

## How the shot scene picks the flow (general solution)

The CFD library is the set of cases in `index.json` (speed, spin ratio S, orientation).
At each moment of the flight the scene takes the ball's speed relative to the air and its local
spin ratio S (the spin decays along the flight while the speed changes, so S changes too). It
crossfades the two cases that bracket the local S at the nearest speed, weighted by how close
each is, and says which cases are blended in the caption. A local S outside the library is drawn
at the nearest library S and the caption says so. The CFD +x axis is aligned with the ball's
velocity relative to the air and the spin axis follows the ball's spin; the ball and its holes
rotate with the spin (drawn slower than real so the rotation is visible). Hole orientation is ASSUMED.
The no-spin twin is drawn next to the backspin ball, with its own S 0 flow.

The scene needs the built explorer field data at `../explorer/data/field/index.json`
(or `?field=<url>`); `python -B viz/explorer/build_site.py` builds it.

## URL parameters

`flow.html`

| param | effect |
|---|---|
| `flows=<folder>` | load bundles from another folder (default `flows`) |
| `run=<id>` | open this case (default: the first in `index.json`) |
| `cmp=1` | side by side with a second case |
| `avg=0` | start in Instant (default Averaged) |
| `view=body\|wake\|zoom` | start camera |
| `plane=a\|b\|ab` | which contour planes are on |
| `field=speed\|vort` | colour slices by speed or vorticity |
| `nostream=1`, `noanim=1`, `nopart=1`, `q=0` | turn off streamlines, flow dashes, particles, vortex cores |
| `tracers=0\|1`, `vvol=0\|1`, `pairs=0\|1` | 3D tracers, vortex volume, lift pairs (bundles with a volume) |
| `sync=1` | play the frames at the tracer pace |
| `pcol=0\|1\|2`, `pq=64\|128\|256` | tracer colour (speed, above/below, vortex sense), tracer texture side (4 k, 16 k, 65 k) |
| `warm=<t*>` | run the tracers this long before the first draw |
| `t=<s>`, `play=1` | start time, start playing |
| `hidepanel=1` | hide the control panel (screenshots) |

`shot.html`

| param | effect |
|---|---|
| `x`, `y`, `hd`, `h` | robot spot (m), heading (deg), release height (m) |
| `v`, `th`, `S` | ball speed (m/s), launch angle (deg from horizontal), backspin ratio |
| `avg=0` | start in Instant (default Averaged) |
| `embed=1` | embedded mode (no top bar, robot placed by the parent page) |
| `cam=follow\|followT\|free`, `free=1` | follow the backspin ball, the twin, or free orbit |
| `mag=<n>`, `off=<n>` | flow size multiplier, side offset between the two balls |
| `plane=a\|b\|ab`, `anim=1` | contour planes; prefer the long time-series cases |
| `spd=<x>`, `t=<s>`, `play=1` | playback speed, start time, start playing |
| `flows=<folder>`, `field=<url>` | other bundle folder or field-data file |
| `hidepanel=1` | hide the control panel |

Embedded, the page also takes the shot from its parent (same origin only) with
`postMessage({type: 'pollen-shot', x, y, hd, h, v, th, S, q, reset})`, where `q` is the
explorer's full model query (air, drag, lift, robot); it answers `{type: 'pollen-flow-ready'}`
once loaded, and `{type: 'pollen-flow-visible', on}` pauses drawing while the parent hides it.
