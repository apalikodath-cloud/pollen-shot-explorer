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
