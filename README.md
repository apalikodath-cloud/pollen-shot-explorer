# POLLEN 3D shot explorer

Interactive 3D explorer for the POLLEN shot design (Team 207, Critical Mass).

All results shown are PREDICTED by simulation, not measured.

Open `index.html` through a web server (it fetches `data/` by relative URL).
`measure/measure.html` is the measurement kit: track a slow-motion video of a shot and fit drag
(Cd) and spin lift (Cl) from a no-spin shot and its backspin twin. Files stay in the browser.

## Rebuild

From the source repo: `python viz/explorer/build_site.py` writes this folder
(`viz/explorer/site/`). Publish it with `viz/explorer/deploy_pages.ps1`.
