"""content/projects/*.md → 프로젝트 상세 페이지(projects/*.html)와 index.html의 목록.

노션 프로젝트 DB의 내용을 content/projects/에 마크다운으로 옮겨 두고,
이 스크립트로 정적 페이지를 다시 만든다.  실행: python build.py

index.html에서 이 스크립트가 채우는 곳 (주석 마커 사이):
  rail      왼쪽 메뉴 (상세 페이지와 같은 것을 쓴다)
  shelf     첫 화면의 프로젝트 선반 (대표작 제외)
  projects  라이브러리 카드 전체
"""
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
CONTENT = ROOT / "content" / "projects"
OUT = ROOT / "projects"
KIND_LABEL = {"ai": "AI 활용", "hand": "직접 구현"}
FEATURED = "pung"  # 첫 화면 배너에 크게 나가는 프로젝트 (선반에서는 뺀다)
SKILL_COUNT = 10
AWARD_COUNT = 5
EMAIL = "tjddbs8295@gmail.com"

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900'
    '&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">'
)
THEME_BOOT = (
    "<script>(function(){var t=null;try{t=localStorage.getItem('theme')}catch(e){}"
    "if(t!=='light'&&t!=='dark'){t=matchMedia('(prefers-color-scheme: light)').matches?'light':'dark'}"
    "document.documentElement.dataset.theme=t})();</script>"
)
THEME_BUTTON = (
    '<button type="button" class="theme-toggle" aria-label="밝은 모드와 어두운 모드 전환">'
    '<span class="when-dark"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/>'
    '<path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>'
    "</svg>밝은 모드</span>"
    '<span class="when-light"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>어두운 모드</span></button>'
)


def asset_version():
    """CSS·JS가 바뀌면 값이 달라지는 꼬리표. 브라우저가 예전 파일을 캐시에서 꺼내 쓰지 않게 한다."""
    files = [ROOT / "css" / "style.css", ROOT / "js" / "main.js"]
    return str(int(max(f.stat().st_mtime for f in files)))


VERSION = asset_version()


def load(path):
    _, front, body = path.read_text(encoding="utf-8").split("---\n", 2)
    meta = {}
    for line in front.strip().splitlines():
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    meta["tags"] = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
    meta["links"] = [
        tuple(part.strip() for part in item.split("|", 1))
        for item in meta.get("links", "").split(";")
        if "|" in item
    ]
    meta["body"] = body
    return meta


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
        r'<a href="\2" target="_blank" rel="noopener">\1</a>',
        text,
    )
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)


def youtube_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([\w-]{6,})", url)
    return match.group(1) if match else ""


def render_body(body):
    out = []
    in_list = in_section = info = False

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</dl>" if info else "</ul>")
            in_list = False

    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            close_list()
            continue
        if line.startswith("## "):
            close_list()
            if in_section:
                out.append("</section>")
            title = line[3:].strip()
            info = title == "프로젝트 정보"
            in_section = True
            out.append(f'<section class="doc__section">\n<h2>{inline(title)}</h2>')
        elif line.startswith("#### "):
            close_list()
            out.append(f"<h4>{inline(line[5:])}</h4>")
        elif line.startswith("### "):
            close_list()
            out.append(f"<h3>{inline(line[4:])}</h3>")
        elif line.startswith("- "):
            item = line[2:]
            if not in_list:
                out.append('<dl class="info">' if info else "<ul>")
                in_list = True
            if info and ": " in item:
                key, value = item.split(": ", 1)
                out.append(
                    f'<div class="info__row"><dt>{inline(key)}</dt><dd>{inline(value)}</dd></div>'
                )
            elif info:
                out.append(f'<div class="info__row"><dd>{inline(item)}</dd></div>')
            else:
                out.append(f"<li>{inline(item)}</li>")
        elif line.startswith("@video "):
            close_list()
            vid = youtube_id(line[7:])
            out.append(
                '<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/'
                f'{vid}" title="플레이 영상" loading="lazy" allowfullscreen '
                'allow="accelerometer; encrypted-media; gyroscope; picture-in-picture"></iframe></div>'
            )
        else:
            close_list()
            out.append(f"<p>{inline(line)}</p>")
    close_list()
    if in_section:
        out.append("</section>")
    return "\n".join(out)


def image(p, prefix):
    """표지 <img>. focus는 16:9로 잘릴 때 남길 지점 (CSS object-position 값)."""
    focus = f' style="object-position: {p["focus"]}"' if p.get("focus") else ""
    return (
        f'<img src="{prefix}{p["cover"]}" alt="{html.escape(p["title"])} 대표 이미지" '
        f'loading="lazy"{focus}>'
    )


def cover(p, prefix, extra=""):
    if p.get("cover"):
        return f'<div class="cover{extra}">{image(p, prefix)}</div>'
    return (
        f'<div class="cover cover--type{extra}" style="--hue: {p.get("hue", "40")}">'
        f'<span class="cover__word">{html.escape(p["title"])}</span></div>'
    )


def badges(p):
    ai = " badge--ai" if p["kind"] == "ai" else ""
    return (
        f'<span class="badge{ai}">{KIND_LABEL[p["kind"]]}</span>'
        f'<span class="badge">{html.escape(p["status"])}</span>'
    )


def card(p):
    tags = "".join(f"<li>{html.escape(t)}</li>" for t in p["tags"])
    return f"""          <a class="card" href="projects/{p['slug']}.html" data-kind="{p['kind']}">
            {cover(p, '')}
            <div class="card__body">
              <div class="meta">{badges(p)}<span>{p['period']}</span></div>
              <h3 class="h3">{html.escape(p['title'])}</h3>
              <p>{html.escape(p['summary'])}</p>
              <ul class="tags">{tags}</ul>
              <span class="card__more">자세히 보기 →</span>
            </div>
          </a>"""


def shelf_item(p):
    sub = KIND_LABEL[p["kind"]]
    if p["status"] == "출시" and p["links"]:
        sub += " · " + p["links"][0][0]
    ai = " is-ai" if p["kind"] == "ai" else ""
    pic = image(p, "") if p.get("cover") else ""
    return f"""          <a class="shelf__item" href="projects/{p['slug']}.html">
            <span class="shelf__cover">{pic}</span>
            <span><span class="shelf__name">{html.escape(p['title'])}</span><br><span class="shelf__sub{ai}">{html.escape(sub)}</span></span>
          </a>"""


def rail(prefix, home, counts, total):
    """왼쪽 메뉴. 메인에서는 섹션 이동과 필터, 상세 페이지에서는 메인으로 돌아가는 링크."""
    base = "" if home else f"{prefix}index.html"
    active = lambda on: ' class="is-active"' if on else ""
    filters = ""
    if home:
        filters = f"""
      <div class="rail__filter" role="group" aria-label="프로젝트 구분">
        <div class="eyebrow">FILTER</div>
        <button type="button" class="filter-btn" data-filter="all" aria-pressed="true">전체 <span class="count">{total}</span></button>
        <button type="button" class="filter-btn" data-filter="ai" aria-pressed="false">AI 활용 <span class="count">{counts['ai']}</span></button>
        <button type="button" class="filter-btn" data-filter="hand" aria-pressed="false">직접 구현 <span class="count">{counts['hand']}</span></button>
      </div>"""
    return f"""<aside class="rail">
    <div class="rail__top">
      <div>
        <a class="rail__name" href="{base}#top">조성윤</a>
        <div class="rail__role">게임 개발자 · Unreal Engine</div>
      </div>
      <nav class="rail__nav" aria-label="섹션 이동">
        <a href="{base}#top"{active(home)}>홈</a>
        <a href="{base}#projects"{active(not home)}>라이브러리<span class="count">{total}</span></a>
        <a href="{base}#skills">기술 스택<span class="count">{SKILL_COUNT}</span></a>
        <a href="{base}#career">수상 · 이력<span class="count">{AWARD_COUNT}</span></a>
        <a href="{base}#about">소개</a>
      </nav>{filters}
    </div>
    <div class="rail__bottom">
      <a href="mailto:{EMAIL}">{EMAIL}</a>
      <a class="plain" href="https://github.com/Jokkilook" target="_blank" rel="noopener">github.com/Jokkilook</a>
      <span>상명대학교 게임학부 재학</span>
      {THEME_BUTTON}
    </div>
  </aside>"""


def detail(p, newer, older, counts, total):
    title = html.escape(p["title"])
    links = "".join(
        f'<a class="btn btn--{"primary" if i == 0 else "ghost"}" href="{url}" '
        f'target="_blank" rel="noopener">{html.escape(name)}</a>'
        for i, (name, url) in enumerate(p["links"])
    )
    pager = ""
    if older:
        pager += (
            f'<a href="{older["slug"]}.html"><span class="dir">← 이전 프로젝트</span>'
            f'{html.escape(older["title"])}</a>'
        )
    if newer:
        pager += (
            f'<a class="next" href="{newer["slug"]}.html"><span class="dir">다음 프로젝트 →</span>'
            f'{html.escape(newer["title"])}</a>'
        )
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} · 조성윤 포트폴리오</title>
  <meta name="description" content="{html.escape(p['summary'])}">
  {FONTS}
  {THEME_BOOT}
  <link rel="stylesheet" href="../css/style.css?v={VERSION}">
</head>
<body>
  {rail('../', False, counts, total)}

  <main class="main">
    <div class="wrap doc">
      <a class="doc__back" href="../index.html#projects">← 라이브러리</a>
      <header class="doc__head">
        <div class="meta">{badges(p)}<span>{p['period']}</span></div>
        <h1 class="doc__title">{title}</h1>
        <p class="doc__summary">{html.escape(p['summary'])}</p>
        <ul class="tags">{''.join(f'<li>{html.escape(t)}</li>' for t in p['tags'])}</ul>
        <div class="btn-row">{links}</div>
      </header>
      {cover(p, '../', ' doc__cover')}
{render_body(p['body'])}
      <nav class="doc__pager" aria-label="다른 프로젝트">{pager}</nav>
    </div>
  </main>
<script src="../js/main.js?v={VERSION}"></script>
</body>
</html>
"""


def fill(text, name, block):
    pattern = rf"<!-- {name}:start.*?<!-- {name}:end -->"
    text, n = re.subn(
        pattern,
        lambda _: f"<!-- {name}:start (build.py가 생성) -->\n{block}\n        <!-- {name}:end -->",
        text,
        flags=re.S,
    )
    assert n == 1, f"index.html에 {name} 마커가 없습니다"
    return text


def main():
    # AI 활용 프로젝트를 먼저, 그 안에서는 최신순
    projects = sorted((load(f) for f in CONTENT.glob("*.md")), key=lambda p: p["date"], reverse=True)
    projects.sort(key=lambda p: p["kind"] != "ai")
    counts = {k: sum(p["kind"] == k for p in projects) for k in KIND_LABEL}
    total = len(projects)

    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.html"):
        old.unlink()
    for i, p in enumerate(projects):
        newer = projects[i - 1] if i > 0 else None
        older = projects[i + 1] if i + 1 < total else None
        page = detail(p, newer, older, counts, total)
        (OUT / f"{p['slug']}.html").write_text(page, encoding="utf-8", newline="\n")

    index = ROOT / "index.html"
    text = index.read_text(encoding="utf-8")
    text = fill(text, "rail", "  " + rail("", True, counts, total))
    text = fill(text, "shelf", "\n".join(shelf_item(p) for p in projects if p["slug"] != FEATURED))
    text = fill(text, "projects", "\n".join(card(p) for p in projects))
    text = re.sub(r'(css/style\.css|js/main\.js)(\?v=\d+)?"', lambda m: f'{m.group(1)}?v={VERSION}"', text)
    index.write_text(text, encoding="utf-8", newline="\n")
    print(f"built {total} projects: ai {counts['ai']}, hand {counts['hand']}")


if __name__ == "__main__":
    main()
