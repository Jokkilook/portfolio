"""content/projects/*.md → 프로젝트 상세 페이지(projects/*.html)와 index.html의 목록.

노션 프로젝트 DB의 내용을 content/projects/에 마크다운으로 옮겨 두고,
이 스크립트로 정적 페이지를 다시 만든다.  실행: python build.py

index.html에서 이 스크립트가 채우는 곳 (주석 마커 사이):
  rail  왼쪽 메뉴 (상세 페이지와 같은 것을 쓴다)
  ai    AI 활용 프로젝트 묶음
  hand  직접 구현 프로젝트 묶음

프로젝트 파일에 points(구현 내용)가 있으면 이미지가 있는 큰 줄로, 없으면 표의 한 줄(brief)로 나온다.
"""
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
CONTENT = ROOT / "content" / "projects"
OUT = ROOT / "projects"
KIND_LABEL = {"ai": "AI 활용", "hand": "직접 구현"}
FEATURED = "pung"  # 강조 테두리와 채운 버튼으로 표시하는 대표 프로젝트
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


def status_label(p):
    """'Steam 출시'처럼 어디에 출시했는지까지 적는다."""
    if p["status"] == "출시" and p["links"]:
        return f'{p["links"][0][0]} 출시'
    return p["status"]


def row(p):
    """역할과 구현 내용이 있는 프로젝트 한 줄. 줄 전체가 상세 페이지 링크다."""
    lead = " row--lead" if p["slug"] == FEATURED else ""
    points = "".join(f"<li>{inline(t.strip())}</li>" for t in p["points"].split(" | "))
    detail_url = f'projects/{p["slug"]}.html'
    side = f'<a class="mini mini--{"primary" if lead else "accent"}" href="{detail_url}">{html.escape(p.get("cta", "자세히 보기"))}</a>'
    if p["links"]:
        name, url = p["links"][0]
        side += f'<a class="mini" href="{url}" target="_blank" rel="noopener">{html.escape(name)}</a>'
    return f"""        <article class="row{lead}">
          <div class="row__media">{image(p, '')}</div>
          <div class="row__body">
            <div class="row__head">
              <h3 class="row__title"><a href="{detail_url}">{html.escape(p['title'])}</a></h3>
              <span class="badge">{html.escape(status_label(p))}</span>
              <span class="row__meta">{html.escape(p['meta'])}</span>
            </div>
            <p class="row__role"><b>내 역할</b>{html.escape(p['role'])}</p>
            <ul class="row__points">{points}</ul>
          </div>
          <div class="row__side">{side}</div>
        </article>"""


def table_row(p):
    return f"""          <a class="ptable__row" href="projects/{p['slug']}.html">
            <span class="ptable__name">{html.escape(p['title'])}</span>
            <span>{html.escape(status_label(p))}</span>
            <span class="ptable__brief">{html.escape(p.get('brief', p['summary']))}</span>
            <span class="ptable__period">{p['period']}</span>
          </a>"""


def group(projects, kind, heading, note):
    """한 구분(AI 활용 / 직접 구현)의 제목, 큰 줄들, 나머지 표."""
    mine = [p for p in projects if p["kind"] == kind]
    rows = "\n".join(row(p) for p in mine if p.get("points"))
    rest = "\n".join(table_row(p) for p in mine if not p.get("points"))
    table = f'\n        <div class="ptable panel">\n{rest}\n        </div>' if rest else ""
    return f"""        <div class="group-head group-head--{kind}">
          <h2>{heading} <span class="count">{len(mine)}</span></h2>
          <p>{note}</p>
        </div>
{rows}{table}"""


MAIL_ICON = (
    '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"/>'
    '<path d="M3 7l9 6 9-6"/></svg>'
)
GITHUB_ICON = (
    '<svg viewBox="0 0 16 16" aria-hidden="true" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 '
    "2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-"
    ".82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78"
    "-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-"
    ".27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-"
    "3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8"
    '-8-8z"/></svg>'
)


def rail(prefix, home, total):
    """왼쪽 메뉴. 메인에서는 섹션 이동, 상세 페이지에서는 메인의 각 섹션으로 돌아가는 링크."""
    base = "" if home else f"{prefix}index.html"
    return f"""<aside class="rail">
    <div class="rail__top">
      <div>
        <a class="rail__name" href="{base}#top">조성윤</a>
        <p class="rail__intro">직접 만들어 보며 익힌 것을 기준 삼아, <em>AI와 함께 일하는</em> 게임 개발자 조성윤입니다.</p>
        <div class="rail__role">Unreal Engine · C++</div>
      </div>
      <nav class="rail__nav" aria-label="섹션 이동">
        <a href="{base}#top" class="is-active">프로젝트<span class="count">{total}</span></a>
        <a href="{base}#skills">기술 스택<span class="count">{SKILL_COUNT}</span></a>
        <a href="{base}#career">수상 · 이력<span class="count">{AWARD_COUNT}</span></a>
        <a href="{base}#about">소개</a>
      </nav>
      <div class="rail__block">
        <div class="eyebrow">수상</div>
        <ul>
          <li><b>2026</b> 상명대 하계 게임잼 최우수상</li>
          <li><b>2025</b> 상명대 동계 게임잼 우수상</li>
          <li><b>2025</b> 상명대 게임 개발 공모전 우수상</li>
          <li><b>2024</b> 대림대 경진 대회 대상</li>
          <li><b>2023</b> 대림대 경진 대회 최우수상</li>
        </ul>
      </div>
      <div class="rail__block">
        <div class="eyebrow">주력 기술</div>
        <ul class="chips">
          <li class="is-key">Unreal Engine</li>
          <li class="is-key">C++</li>
          <li>멀티플레이</li>
          <li>Steam 연동</li>
          <li>Claude Code</li>
        </ul>
      </div>
    </div>
    <div class="rail__bottom">
      <a class="icon-link" href="mailto:{EMAIL}">{MAIL_ICON}{EMAIL}</a>
      <a class="icon-link plain" href="https://github.com/Jokkilook" target="_blank" rel="noopener">{GITHUB_ICON}github.com/Jokkilook</a>
      <span>상명대학교 게임전공 재학</span>
      {THEME_BUTTON}
    </div>
  </aside>"""


def detail(p, newer, older, total):
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
  {rail('../', False, total)}

  <main class="main">
    <div class="wrap doc">
      <a class="doc__back" href="../index.html">← 프로젝트 목록</a>
      <div class="doc__top">
      <header class="doc__head">
        <div class="meta">{badges(p)}<span>{p['period']}</span></div>
        <h1 class="doc__title">{title}</h1>
        <p class="doc__summary">{html.escape(p['summary'])}</p>
        <ul class="tags">{''.join(f'<li>{html.escape(t)}</li>' for t in p['tags'])}</ul>
        <div class="btn-row">{links}</div>
      </header>
      {cover(p, '../')}
      </div>
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
    # AI 활용 프로젝트를 먼저, 그 안에서는 대표 프로젝트를 맨 앞에 두고 나머지는 최신순
    projects = sorted((load(f) for f in CONTENT.glob("*.md")), key=lambda p: p["date"], reverse=True)
    projects.sort(key=lambda p: (p["kind"] != "ai", p["slug"] != FEATURED))
    counts = {k: sum(p["kind"] == k for p in projects) for k in KIND_LABEL}
    total = len(projects)

    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.html"):
        old.unlink()
    for i, p in enumerate(projects):
        newer = projects[i - 1] if i > 0 else None
        older = projects[i + 1] if i + 1 < total else None
        page = detail(p, newer, older, total)
        (OUT / f"{p['slug']}.html").write_text(page, encoding="utf-8", newline="\n")

    index = ROOT / "index.html"
    text = index.read_text(encoding="utf-8")
    text = fill(text, "rail", "  " + rail("", True, total))
    ai_note = "Claude Code 같은 AI 도구가 일하는 방식을 설계하고 결과를 검증해 만든 프로젝트"
    hand_note = "AI 없이 설계하고 구현한 프로젝트. AI의 결과물을 판단하는 기준이 된 경험"
    text = fill(text, "ai", group(projects, "ai", "AI 활용 프로젝트", ai_note))
    text = fill(text, "hand", group(projects, "hand", "직접 구현 프로젝트", hand_note))
    text = re.sub(r'(css/style\.css|js/main\.js)(\?v=\d+)?"', lambda m: f'{m.group(1)}?v={VERSION}"', text)
    index.write_text(text, encoding="utf-8", newline="\n")
    print(f"built {total} projects: ai {counts['ai']}, hand {counts['hand']}")


if __name__ == "__main__":
    main()
