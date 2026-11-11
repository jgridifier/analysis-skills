"""CI checks: SKILL.md frontmatter, skills index coverage, and the newsroom manifest.

- every skills/<name>/SKILL.md starts with YAML frontmatter holding `name` (== folder name) and a `description`
  that says when to use it (must contain "Use when" or "Use first when");
- every skill is listed in skills/README.md;
- docs/articles.json: unique slugs, type in {method, application}, each application has a parent method article,
  every linked article page and content fragment exists, and each method's children point back to it.
"""
import json, pathlib, re, sys
R = pathlib.Path(__file__).resolve().parents[1]; err = []
idx = (R / "skills" / "README.md").read_text()
for p in sorted((R / "skills").glob("*/SKILL.md")):
    t = p.read_text(); m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    if not m: err.append(f"{p}: no YAML frontmatter"); continue
    fm = dict(re.findall(r"^(\w+):\s*(.+)$", m.group(1), re.M))
    if fm.get("name") != p.parent.name: err.append(f"{p}: name {fm.get('name')!r} != folder {p.parent.name!r}")
    d = fm.get("description", "")
    if not re.search(r"Use (first )?when", d): err.append(f"{p}: description must say when to use it")
    if len(d) > 1024: err.append(f"{p}: description longer than 1024 chars")
    if f"({p.parent.name}/SKILL.md)" not in idx: err.append(f"{p.parent.name} missing from skills/README.md")
M = json.load(open(R / "docs" / "articles.json"))["articles"]; slugs = [a["slug"] for a in M]
if len(set(slugs)) != len(slugs): err.append("duplicate slugs in articles.json")
by = {a["links"]["self"]: a for a in M}
for a in M:
    for k in ["slug", "title", "type", "method", "date", "tags", "links"]:
        if k not in a: err.append(f"{a.get('slug')}: missing {k}")
    if a["type"] not in ("method", "application"): err.append(f"{a['slug']}: bad type")
    if not (R / "docs" / "content" / f"{a['slug']}.html").exists(): err.append(f"{a['slug']}: no content fragment")
    if not (R / "docs" / a["links"]["self"]).exists(): err.append(f"{a['slug']}: page not built (run docs/build.py)")
    if a["type"] == "application":
        par = by.get(a["links"].get("parent"))
        if not par or par["type"] != "method" or a["links"]["self"] not in par["links"]["children"]:
            err.append(f"{a['slug']}: parent method article missing or does not list it")
    for k in ("code", "results", "skill"):
        if a["links"].get(k) and not (R / a["links"][k]).exists(): err.append(f"{a['slug']}: {k} path {a['links'][k]} missing")
print("\n".join(err) if err else f"OK: {len(list((R / 'skills').glob('*/SKILL.md')))} skills, {len(M)} articles")
sys.exit(1 if err else 0)
