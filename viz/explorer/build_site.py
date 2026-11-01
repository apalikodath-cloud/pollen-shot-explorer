"""Build the static site: runs build_page.py, copies index.html + data/ and the measurement kit
(viz/measure -> site/measure, plus site/explorer/physics.js that it loads) into site/."""
import shutil, subprocess, sys
from pathlib import Path
d = Path(__file__).parent
site = d / "site"
subprocess.run([sys.executable, str(d / "build_page.py")], check=True)
if site.exists():
    shutil.rmtree(site)
site.mkdir()
# index.html sits at the site root, so its link to the measurement kit (../measure/ in the source tree)
# becomes measure/ here.
idx = (d / "index.html").read_text(encoding="utf-8")
assert idx.count('href="../measure/measure.html"') == 1, "explorer page must link the measurement kit once"
(site / "index.html").write_text(idx.replace('href="../measure/measure.html"', 'href="measure/measure.html"'), encoding="utf-8")
# Measurement kit (viz/measure): site/measure/, with the physics.js it loads from ../explorer/ and its
# back link pointed at the site root.
shutil.copytree(d.parent / "measure", site / "measure", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
(site / "explorer").mkdir()
shutil.copy2(d / "physics.js", site / "explorer" / "physics.js")
mh = site / "measure" / "measure.html"
mt = mh.read_text(encoding="utf-8")
assert mt.count('href="../explorer/index.html"') == 1 and mt.count('src="../explorer/physics.js"') == 1
mh.write_text(mt.replace('href="../explorer/index.html"', 'href="../index.html"'), encoding="utf-8")
shutil.copytree(d / "data", site / "data", ignore=shutil.ignore_patterns("_stale*", "_spec_cache*", "*.tmp.npz", "*.npz", "*.bin", "*.log", "_work", "_spec_run.log", "__pycache__"))
# CFD view data: cfd_runs.json is written by export_cfd.py (rerun it on the runs folder to add finished runs);
# optional flow-field images/manifests live in cfd/fields/<run_id>/ next to this script.
cfd_json = d / "cfd_runs.json"
if cfd_json.exists():
    shutil.copy2(cfd_json, site / "data" / "cfd_runs.json")
else:
    print("WARN: cfd_runs.json missing; the CFD view will show no runs (run export_cfd.py RUNS_DIR)")
if (d / "cfd" / "fields").is_dir():
    shutil.copytree(d / "cfd" / "fields", site / "cfd" / "fields")
# 3D flow viewer + shot flow scene (viz/flow): site/flow/, with solver.js next to physics.js, links and the
# field-data path rewritten for the site layout. Flow bundles come from viz/flow/flows (or FLOW_BUNDLES);
# only real CFD bundles listed in that folder's index.json are published, synthetic test fields are left out.
import json, os
fsrc = d.parent / "flow"
fdst = site / "flow"
fdst.mkdir()
for name in ("flow.html", "flow.js", "flowview.js", "shot.html", "shot.js"):
    shutil.copy2(fsrc / name, fdst / name)
shutil.copy2(d / "solver.js", site / "explorer" / "solver.js")
for name in ("flow.html", "shot.html"):
    p = fdst / name
    t = p.read_text(encoding="utf-8")
    assert t.count('href="../explorer/"') == 1, name
    p.write_text(t.replace('href="../explorer/"', 'href="../index.html"'), encoding="utf-8")
p = fdst / "shot.js"
t = p.read_text(encoding="utf-8")
assert t.count("'../explorer/data/field/index.json'") == 1
p.write_text(t.replace("'../explorer/data/field/index.json'", "'../data/field/index.json'"), encoding="utf-8")
bsrc = Path(os.environ.get("FLOW_BUNDLES", fsrc / "flows"))
runs = []
if (bsrc / "index.json").exists():
    for r in json.loads((bsrc / "index.json").read_text(encoding="utf-8"))["runs"]:
        man = json.loads((bsrc / r["path"]).read_text(encoding="utf-8"))
        if man.get("synthetic"):
            continue
        rid = Path(r["path"]).parent.name
        shutil.copytree(bsrc / rid, fdst / "flows" / rid)
        runs.append(r)
(fdst / "flows").mkdir(exist_ok=True)
(fdst / "flows" / "index.json").write_text(json.dumps({"runs": runs}), encoding="utf-8")
print(f"flow bundles: {len(runs)} ({', '.join(r['id'] for r in runs)})")
(site / ".nojekyll").write_text("", encoding="utf-8")
(site / "404.html").write_text(
    '<!doctype html><meta charset="utf-8"><title>Redirecting</title>'
    '<meta http-equiv="refresh" content="0; url=./index.html">'
    '<script>location.replace("./index.html")</script>'
    '<a href="./index.html">POLLEN shot explorer</a>', encoding="utf-8")
(site / "README.md").write_text(
"""# POLLEN 3D shot explorer

Interactive 3D explorer for the POLLEN shot design (Team 207, Critical Mass).

All results shown are PREDICTED by simulation, not measured.

Open `index.html` through a web server (it fetches `data/` by relative URL).
`measure/measure.html` is the measurement kit: track a slow-motion video of a shot and fit drag
(Cd) and spin lift (Cl) from a no-spin shot and its backspin twin. Files stay in the browser.

## Rebuild

From the source repo: `python viz/explorer/build_site.py` writes this folder
(`viz/explorer/site/`). Publish it with `viz/explorer/deploy_pages.ps1`.
""", encoding="utf-8")
total = 0
for p in site.rglob("*"):
    if p.is_file():
        s = p.stat().st_size
        total += s
        if s > 100e6:
            print("ERROR over 100 MB:", p)
            sys.exit(1)
        elif s > 50e6:
            print("WARN over 50 MB:", p)
print(f"site: {total/1e6:.1f} MB")
