"""Inline physics.js and solver.js into page.html at the <!--PHYSICS--> marker -> index.html.

Both go in as <script id="js-physics"> / <script id="js-solver">: the Robot view builds its Web Worker
(Blob URL) from the text of those two tags, so the page stays one self-contained file plus data/.
"""
from pathlib import Path
d = Path(__file__).parent
page = (d / "page.html").read_text(encoding="utf-8")
assert "<!--PHYSICS-->" in page
tags = []
for name, sid in (("physics.js", "js-physics"), ("solver.js", "js-solver")):
    js = (d / name).read_text(encoding="utf-8")
    assert "</script" not in js.lower(), name + " must not contain a closing script tag"
    tags.append(f'<script id="{sid}">\n{js}\n</script>')
(d / "index.html").write_text(page.replace("<!--PHYSICS-->", "\n".join(tags)), encoding="utf-8")
print("wrote index.html")
