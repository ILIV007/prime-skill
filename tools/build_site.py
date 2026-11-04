#!/usr/bin/env python3
"""Generate the Prime Skill catalog site (site/index.html) from skills.json.

Stdlib only. The output is a single self-contained HTML page: inline CSS and
JS, no external assets, no tracking. Run locally to preview, or let the
pages.yml workflow run it on every skills.json change.

  python3 tools/build_site.py
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "skills.json"
OUT = ROOT / "site" / "index.html"
REPO_URL = "https://github.com/ILIV007/prime-skill"
CATEGORY_ORDER = ["development", "design", "marketing", "research",
                  "security", "reverse-engineering"]

CSS = """
:root{
  --bg:#0d1117; --panel:#161b22; --panel2:#1c2330; --line:#2d333b;
  --text:#e6edf3; --muted:#9aa7b4; --faint:#6e7d8c;
  --accent:#58a6ff; --accent2:#bc8cff; --warn:#e3a008;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  line-height:1.5}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:1200px;margin:0 auto;padding:0 20px 64px}
header{padding:48px 0 8px;text-align:center}
h1{font-size:2.6rem;margin:0 0 6px;letter-spacing:-.02em}
h1 .grad{background:linear-gradient(90deg,var(--accent),var(--accent2));
  -webkit-background-clip:text;background-clip:text;color:transparent}
.tagline{color:var(--muted);margin:0 auto;max-width:640px}
.count-line{color:var(--faint);margin-top:14px;font-size:.95rem}
.count-line b{color:var(--text)}
.btn{display:inline-block;margin-top:16px;padding:9px 18px;border:1px solid var(--line);
  border-radius:999px;background:var(--panel);color:var(--text);font-weight:600}
.btn:hover{border-color:var(--accent);text-decoration:none}
.controls{position:sticky;top:0;background:var(--bg);padding:18px 0 12px;z-index:5}
#search{width:100%;padding:12px 16px;font-size:1rem;color:var(--text);
  background:var(--panel);border:1px solid var(--line);border-radius:10px;outline:none}
#search:focus{border-color:var(--accent)}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.chip{padding:6px 14px;border-radius:999px;border:1px solid var(--line);
  background:var(--panel);color:var(--muted);cursor:pointer;font-size:.9rem}
.chip:hover{color:var(--text)}
.chip.active{background:var(--accent);border-color:var(--accent);color:#0d1117;font-weight:600}
.chip .n{opacity:.75;font-size:.82em;margin-left:4px}
#result-count{color:var(--faint);font-size:.9rem;margin:14px 2px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));
  gap:16px;margin-top:12px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;
  padding:18px;display:flex;flex-direction:column;gap:8px}
.card:hover{border-color:#3d4754}
.card h3{margin:0;font-size:1.15rem;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.badge{font-size:.68rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;
  padding:2px 8px;border-radius:999px;vertical-align:middle}
.badge.linkonly{background:rgba(227,160,8,.15);color:var(--warn);border:1px solid var(--warn)}
.badge.cat{background:var(--panel2);color:var(--accent2);border:1px solid var(--line)}
.desc{margin:0;color:var(--text)}
.why{margin:0;color:var(--muted);font-size:.92rem;font-style:italic}
.meta{display:flex;flex-wrap:wrap;gap:6px 14px;color:var(--faint);font-size:.85rem;margin-top:2px}
.req{display:flex;flex-wrap:wrap;gap:6px}
.req span{background:var(--panel2);border:1px solid var(--line);border-radius:6px;
  padding:1px 8px;font-size:.78rem;color:var(--muted)}
.card footer{margin-top:auto;padding-top:8px;font-size:.9rem}
#empty{display:none;color:var(--muted);text-align:center;padding:48px 0}
.site-footer{margin-top:56px;text-align:center;color:var(--faint);font-size:.85rem}
@media (max-width:560px){h1{font-size:2rem}.grid{grid-template-columns:1fr}}
"""

JS = """
const search=document.getElementById('search');
const cards=[...document.querySelectorAll('.card')];
const chips=[...document.querySelectorAll('.chip')];
const countEl=document.getElementById('result-count');
const emptyEl=document.getElementById('empty');
let cat='all';
function apply(){
  const q=search.value.trim().toLowerCase();
  let shown=0;
  for(const c of cards){
    const okCat=cat==='all'||c.dataset.category===cat;
    const okQ=!q||c.dataset.search.includes(q);
    const show=okCat&&okQ;
    c.style.display=show?'':'none';
    if(show)shown++;
  }
  countEl.textContent=shown+' of '+cards.length+' skills';
  emptyEl.style.display=shown?'none':'block';
}
search.addEventListener('input',apply);
for(const ch of chips){
  ch.addEventListener('click',()=>{
    chips.forEach(x=>x.classList.remove('active'));
    ch.classList.add('active');
    cat=ch.dataset.cat;
    apply();
  });
}
apply();
"""


def esc(value):
    return html.escape(str(value), quote=True)


def source_url(skill):
    src = skill.get("source") or {}
    url = src.get("url") or REPO_URL
    commit = src.get("commit")
    path = (src.get("path") or "").strip("/")
    if commit:
        url = f"{url}/tree/{commit}"
        if path and path != ".":
            url = f"{url}/{path}"
    return url


def card(skill):
    name = skill.get("title") or skill.get("name") or ""
    category = skill.get("category") or ""
    link_only = skill.get("entry") == "link-only"
    stars = skill.get("stars_at_import")
    stars_txt = f"{stars:,}" if isinstance(stars, int) else "—"
    license_txt = skill.get("license") or "—"
    if license_txt == "none":
        license_txt = "no license declared"
    requires = skill.get("requires") or []
    req_html = ""
    if requires:
        req_html = ('<div class="req">' +
                    "".join(f"<span>{esc(r)}</span>" for r in requires) +
                    "</div>")
    badge = '<span class="badge linkonly">link-only</span>' if link_only else ""
    search_blob = " ".join([
        str(skill.get("name") or ""), name, str(skill.get("description") or ""),
        str(skill.get("why") or ""), category,
        str((skill.get("source") or {}).get("repo") or ""),
    ]).lower()
    return f"""<article class="card" data-category="{esc(category)}" data-search="{esc(search_blob)}">
  <h3>{esc(name)} {badge}<span class="badge cat">{esc(category)}</span></h3>
  <p class="desc">{esc(skill.get('description') or '')}</p>
  <p class="why">{esc(skill.get('why') or '')}</p>
  <div class="meta"><span>License: {esc(license_txt)}</span><span>★ {esc(stars_txt)} at import</span></div>
  {req_html}
  <footer><a href="{esc(source_url(skill))}" target="_blank" rel="noopener">Source ↗</a></footer>
</article>"""


def main():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    skills = data["skills"]
    total = data.get("count", len(skills))
    link_only_count = sum(1 for s in skills if s.get("entry") == "link-only")

    counts = {}
    for s in skills:
        counts[s.get("category") or ""] = counts.get(s.get("category") or "", 0) + 1
    ordered = [c for c in CATEGORY_ORDER if c in counts]
    ordered += sorted(c for c in counts if c not in ordered)

    chips = [f'<button class="chip active" data-cat="all">All'
             f'<span class="n">{total}</span></button>']
    for c in ordered:
        chips.append(f'<button class="chip" data-cat="{esc(c)}">{esc(c)}'
                     f'<span class="n">{counts[c]}</span></button>')

    by_cat = {}
    for s in skills:
        by_cat.setdefault(s.get("category") or "", []).append(s)
    cards = []
    for c in ordered:
        for s in sorted(by_cat[c], key=lambda x: (x.get("name") or "").lower()):
            cards.append(card(s))

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Prime Skill — curated agent skills</title>
<meta name="description" content="Prime Skill: a curated, categorized collection of genuinely useful agent skills.">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>Prime <span class="grad">Skill</span></h1>
  <p class="tagline">A curated collection of genuinely useful agent skills — one representative per capability, vetted for quality, categorized by function.</p>
  <p class="count-line"><b>{total}</b> skills · <b>{len(ordered)}</b> categories · <b>{link_only_count}</b> link-only</p>
  <a class="btn" href="{REPO_URL}">View on GitHub</a>
</header>
<div class="controls">
  <input id="search" type="search" placeholder="Search skills, descriptions, categories…" aria-label="Search skills">
  <div class="chips">{''.join(chips)}</div>
  <p id="result-count"></p>
</div>
<main class="grid">
{''.join(cards)}
</main>
<p id="empty">No skills match your search.</p>
<p class="site-footer">Generated from <a href="{REPO_URL}/blob/main/skills.json">skills.json</a> · “Link-only” entries are listed with metadata and a source link only, because their license does not permit redistribution.</p>
</div>
<script>{JS}</script>
</body>
</html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT} ({total} skills, {link_only_count} link-only)")


if __name__ == "__main__":
    main()
