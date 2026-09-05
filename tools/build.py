"""Assemble the static pages.

src/layout.html            -> page shell ({{title}}, {{description}}, {{content}})
src/partials/*.html        -> reusable blocks, pulled in with {{include:name}}
src/pages/*.html           -> one file per page; optional front matter comment at top:
    <!--
    title: Page title
    description: Meta description
    nav: products          (which header link is active)
    -->
Output: <slug>.html in the repo root. Run:  python tools/build.py
"""
import re, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
layout = (SRC / "layout.html").read_text(encoding="utf-8")
partials = {p.stem: p.read_text(encoding="utf-8") for p in (SRC / "partials").glob("*.html")}

def expand(html, depth=0):
    if depth > 8:
        raise RuntimeError("include recursion too deep")
    def sub(m):
        name = m.group(1).strip()
        if name not in partials:
            sys.exit(f"missing partial: {name}")
        return expand(partials[name], depth + 1)
    return re.sub(r"\{\{include:([\w-]+)\}\}", sub, html)

built = []
for page in sorted((SRC / "pages").glob("*.html")):
    raw = page.read_text(encoding="utf-8")
    meta = {"title": "Covexall", "description": "", "nav": "", "body": ""}
    m = re.match(r"\s*<!--(.*?)-->", raw, re.S)
    if m:
        for line in m.group(1).strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        raw = raw[m.end():]
    content = expand(raw)
    html = layout.replace("{{content}}", content)
    for k in ("title", "description", "body"):
        html = html.replace("{{" + k + "}}", meta[k])
    html = expand(html)
    # mark the active nav link
    if meta["nav"]:
        html = re.sub(r'(<a[^>]*data-nav="%s")' % re.escape(meta["nav"]), r'\1 class="active"', html, count=1)
    out = ROOT / page.name
    out.write_text(html, encoding="utf-8")
    built.append(page.name)

print("built:", ", ".join(built))
