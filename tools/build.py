#!/usr/bin/env python3
"""台中咖啡散步 — 網站產生器

讀取 wiki/places/*.md 與 wiki/areas/*.md，產生：
  - pages/places/<slug>.html   店家頁
  - pages/areas/<slug>.html    地區頁
  - index.html                 首頁（自動列出所有店家與地區）

只用 Python 標準函式庫。用法：在專案根目錄執行  python3 tools/build.py
網站的 HTML 一律由本程式產生，不要手動修改 pages/ 或 index.html。
"""
import html
import re
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_NAME = "台中咖啡散步"
AREA_ORDER = ["西區", "中區", "北區", "南區", "東區", "西屯區", "南屯區", "北屯區", "大里區", "太平區", "烏日區"]

esc = html.escape


# ── 讀取 wiki ─────────────────────────────────────────────
def parse_md(path):
    text = path.read_text(encoding="utf-8")
    meta, body = {}, text
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = m.group(2)
    meta["tags"] = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
    return meta, body


def sections(body):
    """把 markdown 依 '## 標題' 切成 {標題: 內容}，並取出開頭的「- 欄位：值」清單。"""
    facts, secs, cur = OrderedDict(), OrderedDict(), None
    for line in body.splitlines():
        if line.startswith("## "):
            cur = line[3:].strip()
            secs[cur] = []
        elif cur is None:
            fm = re.match(r"^- (.+?)：(.*)$", line)
            if fm:
                facts[fm.group(1)] = fm.group(2).strip()
        else:
            secs[cur].append(line)
    return facts, {k: "\n".join(v).strip() for k, v in secs.items()}


def inline(s):
    s = esc(s)
    # [文字](連結) — 指向 raw/ 的連結改成相對於 pages/places/ 的路徑
    def link(m):
        href = m.group(2).replace("../../raw/", "../../raw/")
        return f'<a href="{href}">{m.group(1)}</a>'
    return re.sub(r"\[(.+?)\]\((.+?)\)", link, s)


def md_block(text):
    if not text or text in ("待確認",) or text.startswith("（尚未填寫"):
        msg = text or "待確認"
        return f'<p class="empty">{esc(msg)}</p>'
    out, items = [], []
    for line in text.splitlines():
        if line.startswith("- "):
            items.append(f"<li>{inline(line[2:])}</li>")
            continue
        if items:
            out.append("<ul>" + "".join(items) + "</ul>")
            items = []
        if line.strip():
            out.append(f"<p>{inline(line)}</p>")
    if items:
        out.append("<ul>" + "".join(items) + "</ul>")
    return "\n".join(out)


# ── 共用版型 ─────────────────────────────────────────────
def page(title, body, depth, desc=""):
    up = "../" * depth
    return f"""<!doctype html>
<html lang="zh-Hant-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700&family=Noto+Serif+TC:wght@600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{up}assets/style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>☕</text></svg>">
</head>
<body>
<header class="site-head"><div class="wrap">
  <a class="logo" href="{up}index.html">台中<span>咖啡</span>散步</a>
  <nav><a href="{up}index.html#areas">地區</a><a href="{up}about.html">關於</a></nav>
</div></header>
{body}
<footer class="site-foot"><div class="wrap">
  資料整理自我的 Google 地圖收藏與店家公開資訊。營業時間會變動，出發前請以店家公告為準。<br>
  本站由 AI Agent 依 <code>AGENTS.md</code> 規則產生。
</div></footer>
</body>
</html>
"""


def card(p, up):
    tags = "".join(f'<span class="tag">#{esc(t)}</span>' for t in p["tags"])
    return f"""<a class="card" href="{up}pages/places/{p['slug']}.html" data-tags="{esc(' '.join(p['tags']))}">
  <div class="meta"><span>{esc(p['area'])}</span><span>{esc(p.get('type',''))}</span><span>★ {esc(p.get('rating',''))}</span></div>
  <h3>{esc(p['name'])}</h3>
  <p>{esc(p.get('tagline',''))}</p>
  <div class="tags">{tags}</div>
</a>"""


# ── 產生各頁 ─────────────────────────────────────────────
def build():
    places = []
    for f in sorted((ROOT / "wiki/places").glob("*.md")):
        meta, body = parse_md(f)
        meta["facts"], meta["secs"] = sections(body)
        places.append(meta)
    areas = {}
    for f in sorted((ROOT / "wiki/areas").glob("*.md")):
        meta, body = parse_md(f)
        intro = [l for l in body.splitlines() if l.strip() and not l.startswith(("#", "-"))]
        meta["intro"] = intro[0] if intro else ""
        areas[meta["name"]] = meta

    by_area = OrderedDict()
    for a in sorted({p["area"] for p in places}, key=lambda a: (AREA_ORDER.index(a) if a in AREA_ORDER else 99, a)):
        by_area[a] = [p for p in places if p["area"] == a]

    (ROOT / "pages/places").mkdir(parents=True, exist_ok=True)
    (ROOT / "pages/areas").mkdir(parents=True, exist_ok=True)

    # 店家頁
    for p in places:
        f, s = p["facts"], p["secs"]
        area_slug = areas.get(p["area"], {}).get("slug", "")
        rows = [("地區", f.get("地區", "")), ("地址", f.get("地址", "待確認")), ("營業時間", f.get("營業時間", "待確認")),
                ("價位", f.get("價位", "待確認")), ("服務", f.get("服務", "待確認")), ("Google 評分", f"★ {p.get('rating','')}（{p.get('reviews','')} 則評論）")]
        dl = "".join(f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>" for k, v in rows)
        tags = "".join(f'<span class="tag">#{esc(t)}</span>' for t in p["tags"])
        prose = "".join(f"<h2>{esc(h)}</h2>\n{md_block(s.get(h, ''))}" for h in ["特色", "推薦品項", "我的筆記", "資料來源"])
        body = f"""<main class="wrap">
  <div class="crumbs"><a href="../../index.html">首頁</a> › <a href="../areas/{area_slug}.html">{esc(p['area'])}</a> › {esc(p['name'])}</div>
  <div class="place-head">
    <div class="type">{esc(p.get('type',''))}</div>
    <h1>{esc(p['name'])}</h1>
    <p class="tagline">{esc(p.get('tagline',''))}</p>
    <div class="tags">{tags}</div>
  </div>
  <div class="layout">
    <article class="prose">{prose}</article>
    <aside class="facts">
      <dl>{dl}</dl>
      <a class="btn" href="{esc(p['maps'])}" target="_blank" rel="noopener">在 Google 地圖開啟</a>
      <p class="note">資料查詢日期：{esc(p.get('updated',''))}</p>
    </aside>
  </div>
</main>"""
        (ROOT / f"pages/places/{p['slug']}.html").write_text(
            page(f"{p['name']}｜{SITE_NAME}", body, 2, p.get("tagline", "")), encoding="utf-8")

    # 地區頁
    for a, ps in by_area.items():
        meta = areas.get(a, {"slug": "", "intro": ""})
        body = f"""<main class="wrap">
  <div class="crumbs"><a href="../../index.html">首頁</a> › {esc(a)}</div>
  <section class="hero"><div class="kicker">AREA</div><h1>臺中市{esc(a)}</h1><p>{esc(meta['intro'])}</p></section>
  <div class="cards">{''.join(card(p, '../../') for p in ps)}</div>
  <p style="padding:28px 0"><a href="../../index.html">← 回首頁看全部地區</a></p>
</main>"""
        (ROOT / f"pages/areas/{meta['slug']}.html").write_text(
            page(f"{a}｜{SITE_NAME}", body, 2, meta["intro"]), encoding="utf-8")

    # 首頁
    all_tags = OrderedDict()
    for p in places:
        for t in p["tags"]:
            all_tags[t] = all_tags.get(t, 0) + 1
    chips = '<button class="chip" aria-pressed="true" data-tag="">全部</button>' + "".join(
        f'<button class="chip" aria-pressed="false" data-tag="{esc(t)}">#{esc(t)}</button>'
        for t, _ in sorted(all_tags.items(), key=lambda x: -x[1]))
    blocks = "".join(f"""<section class="area" data-area>
  <div class="area-head"><h2>{esc(a)}</h2><small>{len(ps)} 家</small><a href="pages/areas/{areas[a]['slug']}.html">地區頁 →</a></div>
  <div class="cards">{''.join(card(p, '') for p in ps)}</div>
</section>""" for a, ps in by_area.items())
    body = f"""<main class="wrap">
  <section class="hero">
    <div class="kicker">TAICHUNG CAFÉ WALK</div>
    <h1>從我的地圖收藏，<br>走進台中的咖啡店</h1>
    <p>這裡整理了我在 Google 地圖上收藏的台中咖啡廳。每家店都附上地址、營業時間與評論中常被提到的品項，方便下次決定要去哪一家。</p>
    <div class="stats"><div><b>{len(places)}</b><span>家咖啡店</span></div><div><b>{len(by_area)}</b><span>個行政區</span></div><div><b>{sum(1 for p in places if '深夜' in p['tags'])}</b><span>家開到深夜</span></div></div>
  </section>
  <div class="filters" role="group" aria-label="依標籤篩選">{chips}</div>
  <div id="areas">{blocks}</div>
</main>
<script>
(function () {{
  var chips = document.querySelectorAll('.chip');
  chips.forEach(function (c) {{
    c.addEventListener('click', function () {{
      var tag = c.dataset.tag;
      chips.forEach(function (x) {{ x.setAttribute('aria-pressed', x === c ? 'true' : 'false'); }});
      document.querySelectorAll('.card').forEach(function (card) {{
        var ok = !tag || card.dataset.tags.split(' ').indexOf(tag) > -1;
        card.classList.toggle('is-hidden', !ok);
      }});
      document.querySelectorAll('[data-area]').forEach(function (sec) {{
        sec.classList.toggle('is-hidden', !sec.querySelector('.card:not(.is-hidden)'));
      }});
    }});
  }});
}})();
</script>"""
    (ROOT / "index.html").write_text(page(SITE_NAME, body, 0, "我的 Google 地圖台中咖啡廳收藏導覽"), encoding="utf-8")

    # 關於頁
    about = """<main class="wrap"><section class="hero"><div class="kicker">ABOUT</div><h1>關於這個網站</h1>
<p>這是一個「讓 AI 照規則持續擴充」的練習專案。我把 Google 地圖收藏匯出成原始資料（raw），由 AI Agent 依照 <code>AGENTS.md</code> 補查店家資訊、整理成 wiki 知識庫，再用 <code>tools/build.py</code> 產生每一頁 HTML。</p></section>
<div class="prose" style="padding-bottom:48px">
<h2>資料流程</h2><p>raw/google-maps（收藏清單）→ raw/research（每店查詢紀錄）→ wiki/places（知識庫）→ pages/（網頁）</p>
<h2>收錄原則</h2><ul><li>只收錄臺中市、目前仍在營業的店家</li><li>查不到的資訊標示「待確認」，不猜測</li><li>不使用網路上的店家照片</li></ul>
</div></main>"""
    (ROOT / "about.html").write_text(page(f"關於｜{SITE_NAME}", about, 0), encoding="utf-8")

    print(f"完成：{len(places)} 家店、{len(by_area)} 個地區頁、index.html、about.html")


if __name__ == "__main__":
    build()
