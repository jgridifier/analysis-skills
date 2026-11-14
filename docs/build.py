"""Render the newsroom: docs/index.html (front page) and docs/articles/<slug>.html from
docs/articles.json (manifest) + docs/content/<slug>.html (article body fragments).

Add an article: append an entry to articles.json, write docs/content/<slug>.html, run `python docs/build.py`.
Placeholders inside fragments: SKILLROOT -> GitHub blob URL of the repo's main branch;
CHILDREN -> cards linking to the method's application articles.
"""
import html, json, pathlib
from datetime import date

D = pathlib.Path(__file__).resolve().parent
M = json.load(open(D / "articles.json"))
REPO = M["repo"]; BLOB = REPO + "/blob/main"
HEAD = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title><meta name="description" content="{dek}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=Newsreader:ital,opsz,wght@0,6..72,400..600;1,6..72,400..500&family=JetBrains+Mono:wght@400;500;700&display=swap">
<link rel="stylesheet" href="{root}assets/brief.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js" onload="renderMathInElement(document.body,{{delimiters:[{{left:'$$',right:'$$',display:true}},{{left:'\\\\(',right:'\\\\)',display:false}}]}})"></script>
<style>.grid figure img,figure img{{max-width:100%;height:auto}} .card h3 a{{color:inherit}} .tags .tag{{margin-right:.35rem}}</style>
</head><body><main>
"""
FOOT = """<footer><p>analysis-skills newsroom · scripts, lockfiles and full results in <a href="{repo}">{repo}</a> ·
no raw data is published, only aggregates and fitted structure · built {built}</p></footer></main></body></html>
"""
ACC = {"promoted": "green", "rejected": "red"}
NOV = {"obscure": 0, "niche": 1, "well-known": 2}  # lower = more prominent (diamonds in the rough first)
VCL = lambda v: "adopt" if v.startswith("promoted") or "all gates" in v else ("skip" if "rejected" in v else "interesting")


def badges(a):
    st = a.get("status", "recommended, awaiting approval")
    return (f'<span class="tag{" green" if st == "promoted" else ""}">status: {html.escape(st)}</span>'
            f'<span class="tag">novelty: {html.escape(a.get("novelty", "unrated"))}</span>')


def fmt_date(s):
    d = date.fromisoformat(s); return d.strftime("%A · %B %-d, %Y")


def tags(a):
    return "".join(f'<span class="tag{" teal" if t.startswith("run-") else ""}">{html.escape(t)}</span>' for t in a["tags"])


def card(a, prefix):
    acc = ACC.get(a.get("status"), "blue" if a["type"] == "application" else ("" if a.get("novelty") == "well-known" else "teal"))
    if a["type"] == "scout": acc = ""
    kind = {"method": "Method", "application": "Application", "scout": "Daily scout"}[a["type"]]
    href = a["links"]["self"] if a["links"]["self"].startswith("http") else prefix + a["links"]["self"]
    return (f'<div class="card {acc}"><div class="card-top"><span class="tag">{kind} · {html.escape(a["method"])}</span>'
            f'<span class="verdict {VCL(a["verdict"])}">{html.escape(a["verdict"])}</span></div>'
            f'<h3><a href="{href}">{html.escape(a["title"])}</a></h3><p>{html.escape(a["dek"])}</p>'
            f'<div class="foot tags">{badges(a)}{tags(a)}<span class="meta">{a["date"]}</span></div></div>')


def order(arts):  # newest first; within a date, more novel first (obscure > niche > well-known), then manifest order
    arts = sorted(arts, key=lambda a: NOV.get(a.get("novelty"), 1))
    return sorted(arts, key=lambda a: a["date"], reverse=True)


def status_note(a, parent):
    st = a.get("status", "recommended, awaiting approval"); m = a["method"]
    if st == "promoted": return ""
    who = "This application's method" if parent else "This method"
    return (f'<div class="note"><strong>Status: {html.escape(st)}.</strong> {who} ({html.escape(m)}) is not promoted. '
            f'Promotion needs Jared\'s own dated approval recorded in <code>methods/{html.escape(m)}/APPROVAL.md</code> '
            f'(<a href="{BLOB}/docs/WORKFLOW.md">workflow</a>, Stage 4b). Until then the skill it feeds is a DRAFT.</div>')


def build_article(a, by_self):
    body = (D / "content" / f'{a["slug"]}.html').read_text().replace("SKILLROOT/", "").replace('href="../', 'href="../')
    body = body.replace('href="../methods/', f'href="{BLOB}/methods/').replace('href="../skills/', f'href="{BLOB}/skills/')
    if "CHILDREN" in body:
        kids = [by_self[c] for c in a["links"]["children"]]
        body = body.replace("CHILDREN", '<div class="grid">' + "".join(card(k, "../") for k in kids) + "</div>")
    parent = by_self.get(a["links"]["parent"]) if a["links"].get("parent") else None
    nav = '<a href="../index.html">Newsroom</a>'
    if parent: nav += f'<a href="../{parent["links"]["self"]}">← Method: {html.escape(parent["method"])}</a>'
    nav += f'<a href="{BLOB}/{a["links"]["code"]}">Code</a><a href="{BLOB}/{a["links"]["results"]}">Results</a><a href="{BLOB}/{a["links"]["skill"]}">Skill</a>'
    kind = "Method article" if a["type"] == "method" else "Application article"
    mast = (f'<header class="mast"><div class="date">{fmt_date(a["date"])} · {kind}</div><h1>{html.escape(a["title"])}</h1>'
            f'<p class="dek">{html.escape(a["dek"])}</p><nav>{nav}</nav></header><div class="ticker">{badges(a)}{tags(a)}</div>'
            + status_note(a, parent))
    back = ""
    if parent:
        back = (f'<div class="sec-head"><span class="n">↩</span><h2>Back to the method</h2><span class="line"></span></div>'
                f'<div class="grid">{card(parent, "../")}</div>')
    out = HEAD.format(title=html.escape(a["title"]) + " · analysis-skills", dek=html.escape(a["dek"]), root="../") + mast + body + back
    (D / "articles").mkdir(exist_ok=True)
    (D / a["links"]["self"]).write_text(out + FOOT.format(repo=REPO, built=max(x["date"] for x in M["articles"])))


def build_index(arts):
    arts = order(arts)
    lead = sorted([a for a in arts if a["type"] == "method"], key=lambda a: (NOV.get(a.get("novelty"), 1), [-ord(c) for c in a["date"]]))[0]
    rest = [a for a in arts if a is not lead]
    methods = [a for a in arts if a["type"] == "method"]
    methods = sorted(methods, key=lambda a: NOV.get(a.get("novelty"), 1))
    tick = "".join(f'<span><b>●</b> {html.escape(a["title"])} ({html.escape(a.get("status", ""))})</span>' for a in methods)
    status = "".join(
        f'<tr><td><a href="{m["links"]["self"]}">{html.escape(m["method"])}</a></td><td>{html.escape(m["verdict"])}</td><td>{html.escape(m.get("novelty", ""))}</td>'
        f'<td>{len(m["links"]["children"])}</td><td><a href="{BLOB}/{m["links"]["results"]}">RESULTS.md</a></td>'
        f'<td><a href="{BLOB}/{m["links"]["skill"]}">{m["links"]["skill"].split("/")[1]}</a>{"" if m.get("status") == "promoted" else " (DRAFT)"}</td></tr>' for m in methods)
    body = f"""<header class="mast"><div class="date">{fmt_date(arts[0]["date"])} · newsroom</div><h1>Analysis skills</h1>
<p class="dek">Lesser-known, fast, interpretable methods, each run three ways on our own data, reproduced from a clean environment, and folded into general agent skills when they survive. No neural nets.</p>
<nav><a href="{REPO}">Repo</a><a href="{BLOB}/docs/WORKFLOW.md">Workflow</a><a href="{BLOB}/skills/README.md">Skills</a><a href="articles.json">articles.json</a></nav></header>
<div class="ticker">{tick}</div>
<div class="sec-head"><span class="n">Lead</span><h2>Top story</h2><span class="line"></span></div>
<div class="card dark"><div class="card-top"><span class="tag">Method · {html.escape(lead["method"])}</span><span class="verdict {VCL(lead["verdict"])}">{html.escape(lead["verdict"])}</span></div>
<h2 style="margin-top:.4rem;color:#fffdf7"><a href="{lead["links"]["self"]}" style="color:#fffdf7;text-decoration-color:#e8902e">{html.escape(lead["title"])}</a></h2><p class="lede">{html.escape(lead["dek"])}</p><div class="foot tags">{badges(lead)}{tags(lead)}</div></div>
<div class="sec-head"><span class="n">All</span><h2>Articles, newest first</h2><span class="line"></span></div>
<div class="grid">{"".join(card(a, "") for a in rest)}</div>
<div class="sec-head"><span class="n">Desk</span><h2>Reproduction status</h2><span class="line"></span></div>
<div class="table-wrap"><table><thead><tr><th>method</th><th>status</th><th>novelty</th><th>applications</th><th>results</th><th>skill</th></tr></thead><tbody>{status}</tbody></table></div>
<div class="sec-head"><span class="n">How</span><h2>The workflow</h2><span class="line"></span></div>
<section class="tldr"><ul>
<li><strong>1 · Candidate</strong>: a method is picked from the daily methods scout.</li>
<li><strong>2 · Three applications</strong> on our real data, each a script with a pinned environment, a fixed seed and a data manifest (Drive id, retrieval date, rows, sha256; the data itself is never committed).</li>
<li><strong>3 · Reproduce</strong> from lockfiles in a fresh environment and compare every number; then seeds, windows, a dependence-aware null and a plain baseline.</li>
<li><strong>4 · Decide</strong>: recommend only what reproduces and clears the null and the baseline; otherwise record a rejection with the reason.</li>
<li><strong>4b · Jared approves</strong>: a recommendation stays "recommended, awaiting approval" until Jared's own dated words are recorded in <code>methods/&lt;method&gt;/APPROVAL.md</code>. A relayed "he agreed" doesn't count, and no agent creates that file on its own.</li>
<li><strong>5 · Skill</strong>: fold the lessons into a general task skill (one row per method in its chooser), then publish a method article and one article per application here.</li>
</ul><p class="meta">Full text: <a href="{BLOB}/docs/WORKFLOW.md">docs/WORKFLOW.md</a> · agent version: <a href="{BLOB}/skills/promote-method-to-skill/SKILL.md">promote-method-to-skill</a></p></section>
<div class="sec-head"><span class="n">Skills</span><h2>What agents can use</h2><span class="line"></span></div>
<ul>
<li><strong><a href="{BLOB}/skills/choose-analysis-method/SKILL.md">choose-analysis-method</a></strong>: router from question type and data shape to a skill and a starting method.</li>
<li><strong><a href="{BLOB}/skills/run-changepoint-analysis/SKILL.md">run-changepoint-analysis</a></strong> (DRAFT, pending approval): when did behaviour change? changeforest by default; mean and kernel baselines.</li>
<li><strong><a href="{BLOB}/skills/run-regime-tree-analysis/SKILL.md">run-regime-tree-analysis</a></strong> (DRAFT, pending approval): which conditions mark different groups, and does the slope depend on the state? ctree and MOB.</li>
<li><strong><a href="{BLOB}/skills/run-empirical-bayes-shrinkage/SKILL.md">run-empirical-bayes-shrinkage</a></strong>: shrink many noisy observations and call which moves are real. ebnm (promoted 2026-11-13; Stage 2–3 not yet run).</li>
<li><strong><a href="{BLOB}/skills/run-line-density-chart/SKILL.md">run-line-density-chart</a></strong>: see the typical path and unusual branches in a bundle of short series. DenseLines (promoted 2026-11-13; Stage 2–3 not yet run).</li>
<li><strong><a href="{BLOB}/skills/run-community-rank-analysis/SKILL.md">run-community-rank-analysis</a></strong>: co-movement and rank rearrangement in a closed group. codyn rank clocks (promoted 2026-11-13; Stage 2–3 not yet run).</li>
<li><strong><a href="{BLOB}/skills/promote-method-to-skill/SKILL.md">promote-method-to-skill</a></strong>: the workflow above, as an agent checklist.</li>
</ul>
"""
    (D / "index.html").write_text(HEAD.format(title="Analysis skills · newsroom", dek="Methods newsroom", root="") + body
                                  + FOOT.format(repo=REPO, built=max(x["date"] for x in M["articles"])))


def main():
    arts = M["articles"]; by_self = {a["links"]["self"]: a for a in arts}
    for a in arts:
        if a["type"] != "scout": build_article(a, by_self)  # scout cards link out to the research-lab scout page
    build_index(arts); print(f"built index + {len(arts)} articles")


if __name__ == "__main__":
    main()
