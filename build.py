# -*- coding: utf-8 -*-
"""
從 projects.json 產生 works/ 底下的專案內頁，並同步首頁作品卡的連結。

用法：  python build.py
改內容：只改 projects.json，不用碰 HTML。
空白欄位（location / size / style / materials / concept / highlights）會自動隱藏。
"""
import io, json, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
SITE = "https://wayne7111184-create.github.io/"

def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))

def slot(src, hint, extra=""):
    """圖片欄位：檔案不在就顯示提示（畫廊則整格自動消失）"""
    return (f'<div class="slot"><img src="{src}" alt="{esc(hint)}" {extra} '
            f'onerror="imgFallback(this)"><div class="hint"><b>{esc(src)}</b>{esc(hint)}</div></div>')

NAV = '''<nav class="nav">
  <a href="{root}index.html" class="brand">Wayne Wang<span>王東群</span></a>
  <ul>
    <li><a href="{root}index.html#works">Works</a></li>
    <li><a href="{root}index.html#about">About</a></li>
    <li><a href="{root}index.html#resume">Résumé</a></li>
    <li><a href="{root}index.html#contact">Contact</a></li>
  </ul>
</nav>'''

FALLBACK_JS = '''<script>
/* 圖片副檔名容錯；畫廊圖找不到就整格移除，版面不會開天窗 */
function imgFallback(img){
  var exts = ['.jpg','.png','.jpeg','.webp','.JPG','.PNG','.jpg.jpg','.png.png'];
  if(!img.dataset.base){
    img.dataset.base = img.getAttribute('src').replace(/\\.[a-z0-9]+$/i,'');
    img.dataset.i = '0';
  }
  var i = parseInt(img.dataset.i, 10);
  while(i < exts.length){
    var cand = img.dataset.base + exts[i];
    i++;
    if(cand !== img.getAttribute('src')){
      img.dataset.i = i;
      img.setAttribute('src', cand);
      return;
    }
  }
  var cell = img.closest('.g-item');
  if(cell){
    var g = cell.parentElement;
    cell.remove();
    /* 整個畫廊都沒圖就把這一段收起來，不留空白區塊 */
    if(g && !g.querySelector('.g-item')){
      var sec = g.closest('section');
      if(sec){ sec.style.display = 'none'; }
    }
  } else {
    img.remove();
  }
}
</script>'''


def build_page(p, prev_p, next_p):
    root = "../"
    slug = p["slug"]
    full = f'{p["title"]}{p["sub"]}'
    desc = f'{full}｜{p["typeZh"]} · {p["year"]}｜王東群 Wayne Wang 室內設計作品'

    # ── 專案資訊（空的欄位不出現）
    rows = [("Type", p["typeZh"]), ("Year", p["year"]),
            ("Location", p.get("location", "")), ("Size", p.get("size", "")),
            ("Style", p.get("style", "")), ("Scope", p.get("scope", "")),
            ("Studio", p.get("team", "")), ("Materials", p.get("materials", ""))]
    meta = "\n".join(
        '        <div{cls}><div class="k">{k}</div><div class="v">{v}</div></div>'.format(
            cls=' class="wide"' if k == "Materials" else "", k=k, v=esc(v))
        for k, v in rows if v)

    # ── 設計概念 + 亮點
    body = ""
    if p["concept"] or p["highlights"]:
        paras = "\n          ".join(f"<p>{esc(t)}</p>" for t in p["concept"])
        points = ""
        if p["highlights"]:
            lis = "\n            ".join(f"<li>{esc(t)}</li>" for t in p["highlights"])
            points = f'''
        <ul class="p-points">
            {lis}
        </ul>'''
        body = f'''
  <section class="container sec" style="padding-bottom:0">
    <div class="sec-head"><h2>Concept</h2><span class="zh">設 計 概 念</span><span class="ln"></span></div>
    <div class="p-body">
      <div>
          {paras}
      </div>{points}
    </div>
  </section>'''

    # ── 畫廊（captions 有寫才出現圖說，沒寫就只有圖）
    caps = p.get("captions") or {}

    def caption_of(i):
        if isinstance(caps, list):
            return caps[i - 1] if i - 1 < len(caps) else ""
        return caps.get("%02d" % i) or caps.get(str(i)) or ""

    cell_list = []
    for i in range(1, p["gallery"] + 1):
        img = slot(f"{root}uploads/{slug}/{i:02d}.jpg",
                   f"{p['title']} 第 {i} 張",
                   'loading="lazy" decoding="async"')
        cap = caption_of(i)
        cap_html = f'\n        <div class="g-cap">{esc(cap)}</div>' if cap else ""
        is_plan = i in (p.get("plans") or [])
        if is_plan:
            # 平面圖：整列滿版，可點開看原尺寸
            img = (f'<a class="plan-zoom" href="{root}uploads/{slug}/{i:02d}.jpg" '
                   f'target="_blank" rel="noopener" title="點擊看大圖">{img}'
                   f'<span class="zoom-tag">點圖放大</span></a>')
        cls = " plan" if is_plan else ""
        cell_list.append(f'      <div class="g-item{cls}">{img}{cap_html}\n      </div>')
    cells = "\n".join(cell_list)

    nav_prev = (f'''    <a class="prev" href="{prev_p["slug"]}.html">
      <div class="dir">← 上一個</div>
      <div class="nm">{esc(prev_p["title"])}</div>
    </a>''')
    nav_next = (f'''    <a class="next" href="{next_p["slug"]}.html">
      <div class="dir">下一個 →</div>
      <div class="nm">{esc(next_p["title"])}</div>
    </a>''')

    return f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(full)} — 王東群 Wayne Wang</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}works/{slug}.html">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%23171512'/%3E%3Ctext x='16' y='23' font-family='Helvetica,Arial' font-size='19' font-weight='700' fill='%23C4703F' text-anchor='middle'%3EW%3C/text%3E%3C/svg%3E">
<meta property="og:type" content="article">
<meta property="og:url" content="{SITE}works/{slug}.html">
<meta property="og:title" content="{esc(full)} — 王東群 Wayne Wang">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE}{p["cover"]}">
<meta property="og:locale" content="zh_TW">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@75..125,400..900&family=Schibsted+Grotesk:wght@300;400;500;600;700&family=Noto+Sans+TC:wght@200;300;400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/site.css">
</head>
<body>

{NAV.format(root=root)}

<header class="p-hero">
  {slot(root + p["cover"], p["title"], 'fetchpriority="high" decoding="async"')}
  <div class="p-head">
    <div class="inner">
      <div class="p-no">Project {p["no"]}</div>
      <h1 class="p-title">{esc(p["title"])}<small>{esc(p["sub"])}</small></h1>
      <div class="p-sub">{p["typeEn"]} · {p["typeZh"]} · {p["year"]}</div>
    </div>
  </div>
</header>

<section class="container sec" style="padding-bottom:0">
  <div class="p-meta">
{meta}
  </div>
</section>
{body}

<section class="container sec">
  <div class="sec-head"><h2>Gallery</h2><span class="zh">空 間 紀 錄</span><span class="ln"></span></div>
  <div class="gallery">
{cells}
  </div>
  <a class="p-back" href="{root}index.html#works">← 回作品列表</a>
</section>

<nav class="p-nav">
{nav_prev}
{nav_next}
</nav>

<section class="container sec">
  <div class="sec-head"><h2>Contact</h2><span class="zh">聯 絡</span><span class="ln"></span></div>
  <div class="contact">
    <div class="c-item">
      <div class="k">Email</div>
      <a class="v" href="mailto:wayne7111184@gmail.com">wayne7111184@gmail.com</a>
      <div class="s">歡迎來信談合作</div>
    </div>
    <div class="c-item">
      <div class="k">Behance</div>
      <a class="v" href="https://www.behance.net/28c586d5" target="_blank" rel="noopener">behance.net/28c586d5</a>
      <div class="s">完整作品集</div>
    </div>
  </div>
</section>

<footer>
  <div>王東群 · Wayne Wang</div>
  <div>Interior Designer · 台中</div>
</footer>

<button class="print-btn" onclick="window.print()"><span class="pb-long">列印 / 存成 PDF</span><span class="pb-short">PDF</span></button>

{FALLBACK_JS}
</body>
</html>
'''


def main():
    data = json.load(io.open(os.path.join(BASE, "projects.json"), encoding="utf-8"))
    ps = data["projects"]
    os.makedirs(os.path.join(BASE, "works"), exist_ok=True)

    for i, p in enumerate(ps):
        html = build_page(p, ps[i - 1], ps[(i + 1) % len(ps)])
        path = os.path.join(BASE, "works", p["slug"] + ".html")
        io.open(path, "w", encoding="utf-8").write(html)
        os.makedirs(os.path.join(BASE, "uploads", p["slug"]), exist_ok=True)
        print("產生", os.path.relpath(path, BASE))

    # 首頁作品卡連結 → 對應內頁
    idx_path = os.path.join(BASE, "index.html")
    s = io.open(idx_path, encoding="utf-8").read()
    for i, p in enumerate(ps, 1):
        s = re.sub(
            r'<a class="work" href="[^"]*"[^>]*>(\s*<div class="slot">\s*<img src="uploads/work-%02d\.jpg")' % i,
            r'<a class="work" href="works/%s.html">\1' % p["slug"],
            s, count=1)
    io.open(idx_path, "w", encoding="utf-8").write(s)
    print("首頁連結已更新：", s.count('href="works/'), "個")


if __name__ == "__main__":
    main()
