#!/usr/bin/env python3
"""Generate the Prime Skill catalog site (site/index.html) from skills.json.

Stdlib only. The output is a single HTML page: inline CSS and JS, pixel-arcade
theme. Fonts (Press Start 2P / Space Grotesk) and the Three.js hero load from
CDNs, but every piece of content and core function (search, category / tag /
specials filters, cards) works if the CDNs fail. Run locally to preview, or
let the pages.yml workflow run it on every skills.json change.

  python3 tools/build_site.py
"""
import html
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "skills.json"
OUT = ROOT / "site" / "index.html"
REPO_URL = "https://github.com/ILIV007/prime-skill"
CATEGORY_ORDER = ["development", "design", "marketing", "media", "research",
                  "security", "reverse-engineering"]
# Neon accent per category. Base scheme grounded in ui-ux-pro-max's bundled
# "Arcade & Retro Game" palette (dark indigo bases, neon red/blue, score
# green), extended with the classic arcade companions yellow/cyan/purple.
CATEGORY_COLORS = {
    "development": "#22d3ee",
    "design": "#ff2e63",
    "marketing": "#ffd319",
    "media": "#a855f7",
    "research": "#22c55e",
    "security": "#dc2626",
    "reverse-engineering": "#fb923c",
}

CSS = """
:root{
  --bg:#0e0b1e; --panel:#1d1836; --panel2:#2a2350; --ink:#05030d;
  --text:#f2eefc; --muted:#b6add6; --faint:#8d81b8;
  --pink:#ff2e63; --cyan:#22d3ee; --yellow:#ffd319; --green:#22c55e;
  --purple:#a855f7; --red:#dc2626; --orange:#fb923c; --blue:#3b82f6;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
  font-family:"Space Grotesk",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  line-height:1.5}
a{color:var(--cyan);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:1200px;margin:0 auto;padding:0 20px 64px}
.hero{position:relative;overflow:hidden;border-bottom:4px solid var(--ink);
  background:
    radial-gradient(600px 240px at 15% 0%,rgba(255,46,99,.20),transparent 60%),
    radial-gradient(700px 260px at 85% 10%,rgba(34,211,238,.16),transparent 60%),
    radial-gradient(500px 300px at 50% 110%,rgba(168,85,247,.18),transparent 60%),
    linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),
    linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px),
    #14102a;
  background-size:auto,auto,auto,24px 24px,24px 24px,auto}
#hero3d{position:absolute;inset:0;width:100%;height:100%;display:block}
.hero-inner{position:relative;z-index:1;text-align:center;padding:56px 20px 46px;pointer-events:none}
.hero-inner .btn{pointer-events:auto}
.kicker{font-family:"Press Start 2P","Courier New",monospace;font-size:.6rem;
  letter-spacing:.12em;color:var(--yellow);margin:0 0 18px}
h1{font-family:"Press Start 2P","Courier New",monospace;font-size:2.1rem;line-height:1.35;
  margin:0 0 16px;color:#fff;text-shadow:3px 3px 0 var(--pink),6px 6px 0 rgba(0,0,0,.45)}
.tagline{color:var(--muted);margin:0 auto;max-width:660px;font-size:1.05rem}
.count-line{color:var(--faint);margin-top:16px;font-size:.95rem}
.count-line b{color:var(--text)}
.btn{display:inline-block;margin-top:20px;padding:11px 20px;border:3px solid var(--ink);
  background:var(--yellow);color:#171233;font-weight:700;box-shadow:5px 5px 0 var(--ink);
  font-family:"Press Start 2P","Courier New",monospace;font-size:.68rem;letter-spacing:.04em}
.btn:hover{text-decoration:none;transform:translate(2px,2px);box-shadow:3px 3px 0 var(--ink)}
.btn:active{transform:translate(5px,5px);box-shadow:0 0 0 var(--ink)}
.controls{position:sticky;top:0;background:var(--bg);padding:18px 0 12px;z-index:5;
  border-bottom:2px dashed #352d5e}
#search{width:100%;padding:12px 16px;font-size:1rem;color:var(--text);
  background:var(--panel);border:3px solid var(--ink);border-radius:4px;outline:none;
  box-shadow:4px 4px 0 rgba(3,2,10,.6)}
#search:focus{border-color:var(--cyan)}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px;align-items:center}
.chips .lbl{font-family:"Press Start 2P","Courier New",monospace;font-size:.55rem;
  color:var(--faint);margin-right:2px}
.chip{padding:6px 13px;border:2px solid var(--ink);border-radius:3px;
  background:var(--panel);color:var(--muted);cursor:pointer;font-size:.88rem;font-weight:600;
  box-shadow:3px 3px 0 rgba(3,2,10,.55)}
.chip:hover{color:var(--text);transform:translate(1px,1px);box-shadow:2px 2px 0 rgba(3,2,10,.55)}
.chip.active{background:var(--catc,var(--cyan));border-color:var(--ink);color:#120e26}
.chip .n{opacity:.75;font-size:.82em;margin-left:4px}
.chip.star.active{background:var(--yellow)}
.tagchips .chip{font-size:.78rem;padding:4px 10px;background:var(--panel2)}
#result-count{color:var(--faint);font-size:.9rem;margin:14px 2px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));
  gap:18px;margin-top:14px}
.card{position:relative;background:var(--panel);border:3px solid var(--ink);border-radius:4px;
  padding:24px 18px 16px;display:flex;flex-direction:column;gap:8px;
  box-shadow:7px 7px 0 rgba(3,2,10,.65)}
.card::before{content:"";position:absolute;top:0;left:0;right:0;height:8px;background:var(--catc,var(--cyan))}
.card:hover{transform:translate(-2px,-2px);box-shadow:9px 9px 0 rgba(3,2,10,.65)}
.card.special{border-color:var(--yellow);box-shadow:7px 7px 0 rgba(255,211,25,.35)}
.card.special:hover{box-shadow:9px 9px 0 rgba(255,211,25,.4)}
.card h3{margin:0;font-size:1.12rem;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.badge{font-size:.66rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;
  padding:2px 8px;border-radius:2px;border:2px solid var(--ink);vertical-align:middle}
.badge.linkonly{background:rgba(255,211,25,.16);color:var(--yellow)}
.badge.cat{background:var(--panel2);color:var(--text)}
.badge.star{background:var(--yellow);color:#171233}
.desc{margin:0;color:var(--text)}
.why{margin:0;color:var(--muted);font-size:.92rem;font-style:italic}
.meta{display:flex;flex-wrap:wrap;gap:6px 14px;color:var(--faint);font-size:.85rem;margin-top:2px}
.req,.tags{display:flex;flex-wrap:wrap;gap:6px}
.req span{background:var(--panel2);border:2px solid var(--ink);border-radius:2px;
  padding:1px 8px;font-size:.78rem;color:var(--muted)}
.tag{background:#171233;border:2px solid #453a85;border-radius:2px;color:var(--cyan);
  padding:1px 8px;font-size:.74rem;cursor:pointer;font-family:inherit}
.tag:hover{border-color:var(--cyan);color:#fff}
.card footer{margin-top:auto;padding-top:8px;font-size:.9rem;display:flex;gap:16px}
#empty{display:none;color:var(--muted);text-align:center;padding:48px 0}
.site-footer{margin-top:56px;text-align:center;color:var(--faint);font-size:.85rem}
@media (max-width:560px){h1{font-size:1.35rem}.grid{grid-template-columns:1fr}}
"""

JS = """
const search=document.getElementById('search');
const cards=[...document.querySelectorAll('.card')];
const catChips=[...document.querySelectorAll('.chip[data-cat]')];
const tagChips=[...document.querySelectorAll('.chip[data-tag]')];
const specialChip=document.getElementById('chip-special');
const countEl=document.getElementById('result-count');
const emptyEl=document.getElementById('empty');
let cat='all', tag=null, specialOnly=false;
function apply(){
  const q=search.value.trim().toLowerCase();
  let shown=0;
  for(const c of cards){
    const okCat=cat==='all'||c.dataset.category===cat;
    const okTag=!tag||(c.dataset.tags||'').split(' ').includes(tag);
    const okSp=!specialOnly||c.dataset.special==='1';
    const okQ=!q||c.dataset.search.includes(q);
    const show=okCat&&okTag&&okSp&&okQ;
    c.style.display=show?'':'none';
    if(show)shown++;
  }
  countEl.textContent=shown+' of '+cards.length+' skills';
  emptyEl.style.display=shown?'none':'block';
}
search.addEventListener('input',apply);
for(const ch of catChips){
  ch.addEventListener('click',()=>{
    catChips.forEach(x=>x.classList.remove('active'));
    ch.classList.add('active');
    cat=ch.dataset.cat;
    apply();
  });
}
for(const ch of tagChips){
  ch.addEventListener('click',()=>{
    if(tag===ch.dataset.tag){tag=null;ch.classList.remove('active');}
    else{
      tagChips.forEach(x=>x.classList.remove('active'));
      ch.classList.add('active');
      tag=ch.dataset.tag;
    }
    apply();
  });
}
specialChip.addEventListener('click',()=>{
  specialOnly=!specialOnly;
  specialChip.classList.toggle('active',specialOnly);
  apply();
});
for(const t of document.querySelectorAll('.card .tag')){
  t.addEventListener('click',()=>{
    const chip=tagChips.find(x=>x.dataset.tag===t.dataset.tag);
    if(chip&&tag!==t.dataset.tag) chip.click();
    document.querySelector('.controls').scrollIntoView({behavior:'smooth'});
  });
}
apply();
"""

HERO_JS = """
(function(){
  var canvas=document.getElementById('hero3d');
  if(!canvas||!window.THREE) return;
  var reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var renderer;
  try{
    renderer=new THREE.WebGLRenderer({canvas:canvas,alpha:true,antialias:true});
  }catch(e){ return; }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,1.5));
  var scene=new THREE.Scene();
  var camera=new THREE.PerspectiveCamera(42,2,0.1,100);
  camera.position.set(7.5,6,9.5);
  camera.lookAt(0,0.4,0);
  scene.add(new THREE.AmbientLight(0xffffff,0.8));
  var key=new THREE.DirectionalLight(0xffffff,0.85);
  key.position.set(5,10,6);
  scene.add(key);
  var colors=[0xff2e63,0x22d3ee,0xffd319,0x22c55e,0xa855f7,0x3b82f6,0xfb923c];
  var group=new THREE.Group();
  var geo=new THREE.BoxGeometry(1,1,1);
  var seed=7;
  function rnd(){ seed=(seed*16807)%2147483647; return seed/2147483647; }
  for(var i=0;i<42;i++){
    var cube=new THREE.Mesh(geo,new THREE.MeshLambertMaterial({color:colors[i%colors.length]}));
    var gx=(i%7)-3, gz=(Math.floor(i/7)%3)-1;
    cube.position.set(gx*1.4+(rnd()-0.5)*0.3, 0.4+Math.floor(rnd()*3)*0.55, gz*1.4+(rnd()-0.5)*0.3);
    var s=0.55+rnd()*0.5;
    cube.scale.set(s,s,s);
    cube.userData.ph=rnd()*6.28;
    cube.userData.y=cube.position.y;
    group.add(cube);
  }
  scene.add(group);
  var tx=0,ty=0,mx=0,my=0,visible=true,t=0;
  window.addEventListener('pointermove',function(e){
    mx=e.clientX/window.innerWidth-0.5;
    my=e.clientY/window.innerHeight-0.5;
  },{passive:true});
  if('IntersectionObserver' in window){
    new IntersectionObserver(function(en){ visible=en[0].isIntersecting; },{threshold:0.02}).observe(canvas);
  }
  function resize(){
    var w=canvas.clientWidth||2, h=canvas.clientHeight||1;
    renderer.setSize(w,h,false);
    camera.aspect=w/h;
    camera.updateProjectionMatrix();
  }
  function frame(){
    requestAnimationFrame(frame);
    if(!visible) return;
    t+=0.008;
    tx+=(mx-tx)*0.04; ty+=(my-ty)*0.04;
    group.rotation.y=t*0.7+tx*0.9;
    group.rotation.x=0.12+ty*0.35;
    for(var j=0;j<group.children.length;j++){
      var c=group.children[j];
      c.position.y=c.userData.y+Math.sin(t*1.6+c.userData.ph)*0.12;
    }
    renderer.render(scene,camera);
  }
  resize();
  renderer.render(scene,camera);
  window.addEventListener('resize',function(){ resize(); if(reduced) renderer.render(scene,camera); });
  if(!reduced) requestAnimationFrame(frame);
})();
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


def folder_url(skill):
    return f"{REPO_URL}/tree/main/categories/{skill.get('category')}/{skill.get('name')}"


def card(skill):
    name = skill.get("title") or skill.get("name") or ""
    category = skill.get("category") or ""
    link_only = skill.get("entry") == "link-only"
    special = bool(skill.get("special"))
    tags = skill.get("tags") or []
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
    badges = ""
    if special:
        badges += '<span class="badge star">⭐ special</span>'
    if link_only:
        badges += '<span class="badge linkonly">link-only</span>'
    badges += f'<span class="badge cat">{esc(category)}</span>'
    tags_html = ""
    if tags:
        tags_html = ('<div class="tags">' +
                     "".join(f'<button class="tag" data-tag="{esc(t)}">#{esc(t)}</button>'
                             for t in tags) +
                     "</div>")
    search_blob = " ".join([
        str(skill.get("name") or ""), name, str(skill.get("description") or ""),
        str(skill.get("why") or ""), category, " ".join(tags),
        "special" if special else "",
        str((skill.get("source") or {}).get("repo") or ""),
    ]).lower()
    color = CATEGORY_COLORS.get(category, "#22d3ee")
    return f"""<article class="card{' special' if special else ''}" style="--catc:{color}" data-category="{esc(category)}" data-tags="{esc(' '.join(tags))}" data-special="{'1' if special else ''}" data-search="{esc(search_blob)}">
  <h3>{esc(name)} {badges}</h3>
  <p class="desc">{esc(skill.get('description') or '')}</p>
  <p class="why">{esc(skill.get('why') or '')}</p>
  <div class="meta"><span>License: {esc(license_txt)}</span><span>★ {esc(stars_txt)} at import</span></div>
  {req_html}
  {tags_html}
  <footer><a href="{esc(folder_url(skill))}" target="_blank" rel="noopener">Files ↗</a><a href="{esc(source_url(skill))}" target="_blank" rel="noopener">Source ↗</a></footer>
</article>"""


def main():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    skills = data["skills"]
    total = data.get("count", len(skills))
    link_only_count = sum(1 for s in skills if s.get("entry") == "link-only")
    special_count = sum(1 for s in skills if s.get("special"))

    counts = {}
    for s in skills:
        counts[s.get("category") or ""] = counts.get(s.get("category") or "", 0) + 1
    ordered = [c for c in CATEGORY_ORDER if c in counts]
    ordered += sorted(c for c in counts if c not in ordered)

    chips = [f'<button class="chip active" data-cat="all">All'
             f'<span class="n">{total}</span></button>']
    for c in ordered:
        color = CATEGORY_COLORS.get(c, "#22d3ee")
        chips.append(f'<button class="chip" data-cat="{esc(c)}" style="--catc:{color}">{esc(c)}'
                     f'<span class="n">{counts[c]}</span></button>')
    chips.append(f'<button class="chip star" id="chip-special">⭐ Specials'
                 f'<span class="n">{special_count}</span></button>')

    tag_counts = Counter(t for s in skills for t in (s.get("tags") or []))
    tag_chips = []
    for t, n in sorted(tag_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        tag_chips.append(f'<button class="chip" data-tag="{esc(t)}">#{esc(t)}'
                         f'<span class="n">{n}</span></button>')

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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Space+Grotesk:wght@400;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<header class="hero">
  <canvas id="hero3d" aria-hidden="true"></canvas>
  <div class="hero-inner">
    <p class="kicker">★ Curated agent skills ★</p>
    <h1>Prime Skill</h1>
    <p class="tagline">A curated collection of genuinely useful agent skills — one representative per capability, vetted for quality, categorized by function.</p>
    <p class="count-line"><b>{total}</b> skills · <b>{len(ordered)}</b> categories · <b>{special_count}</b> ⭐ specials · <b>{link_only_count}</b> link-only</p>
    <a class="btn" href="{REPO_URL}">View on GitHub</a>
  </div>
</header>
<div class="wrap">
<div class="controls">
  <input id="search" type="search" placeholder="Search skills, descriptions, tags, categories…" aria-label="Search skills">
  <div class="chips"><span class="lbl">Category</span>{''.join(chips)}</div>
  <div class="chips tagchips"><span class="lbl">Tags</span>{''.join(tag_chips)}</div>
  <p id="result-count"></p>
</div>
<main class="grid">
{''.join(cards)}
</main>
<p id="empty">No skills match your filters. Try clearing a tag or the search.</p>
<p class="site-footer">Generated from <a href="{REPO_URL}/blob/main/skills.json">skills.json</a> · “Link-only” entries are listed with metadata and a source link only, because their license does not permit redistribution.</p>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>{JS}</script>
<script>{HERO_JS}</script>
</body>
</html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT} ({total} skills, {special_count} specials, {link_only_count} link-only, {len(tag_counts)} tags)")


if __name__ == "__main__":
    main()
