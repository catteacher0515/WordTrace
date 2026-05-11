import html
from collections import defaultdict


def render_wordbook_html(rows: list[dict[str, str]], title: str) -> str:
    groups = defaultdict(list)
    for row in rows:
        groups[row["备考建议"]].append(row)

    order = ["优先掌握", "重点熟悉", "可以积累"]
    descriptions = {
        "优先掌握": "这些词在真题中出现稳定、频次高，建议优先进入复习主线。",
        "重点熟悉": "这些词覆盖面较广，理解和识别能力要尽量稳定。",
        "可以积累": "这些词不一定最先背，但适合在二轮复习中补强。",
    }

    counts = {key: len(groups.get(key, [])) for key in order}

    def card(row: dict[str, str]) -> str:
        rank = html.escape(row["序号"])
        word = html.escape(row["重点词汇"])
        meaning = html.escape(row["中文义项"] or "待补充")
        forms = html.escape(row["常见词形"])
        advice = html.escape(row["备考建议"])
        total = html.escape(row["总出现次数"])
        papers = html.escape(row["覆盖真题套数"])
        word_key = html.escape(f"{row['序号']}-{row['重点词汇']}")
        return f"""
        <article class="word-card" data-word-key="{word_key}" data-tier="{advice}">
          <div class="card-top">
            <span class="rank">#{rank}</span>
            <div class="top-actions">
              <span class="badge">{advice}</span>
              <button class="mastery-toggle" data-word-key="{word_key}" type="button">待记</button>
            </div>
          </div>
          <h3 class="word">{word}</h3>
          <p class="meaning">{meaning}</p>
          <p class="forms"><span>常见词形</span>{forms}</p>
          <div class="meta">
            <div class="meta-item"><span>总出现次数</span><strong>{total}</strong></div>
            <div class="meta-item"><span>覆盖真题套数</span><strong>{papers}</strong></div>
          </div>
        </article>
        """

    sections = []
    for key in order:
        cards = "\n".join(card(row) for row in groups.get(key, []))
        sections.append(
            f"""
            <section id="{key}" class="tier-section" data-tier-section="{key}">
              <div class="section-head">
                <div>
                  <p class="eyebrow">{key}</p>
                  <h2>{key}</h2>
                  <p class="section-desc">{descriptions[key]}</p>
                </div>
                <div class="section-side">
                  <div class="section-count">{counts[key]} 词</div>
                  <div class="section-progress" id="section-progress-{key}">已记住 0 / {counts[key]}</div>
                </div>
              </div>
              <div class="card-grid">
                {cards}
              </div>
            </section>
            """
        )

    total_words = len(rows)
    safe_title = html.escape(title)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{safe_title}</title>
  <style>
    :root {{
      --paper: #f4efe4;
      --paper-2: #efe6d4;
      --ink: #222018;
      --muted: #6a6253;
      --line: rgba(34, 32, 24, 0.14);
      --accent: #8e4b2e;
      --accent-soft: #d6b597;
      --olive: #6d7456;
      --shadow: 0 20px 60px rgba(73, 55, 24, 0.10);
      --green: #4b6b53;
      --green-soft: rgba(75,107,83,0.12);
      --mastered-ink: #8a5a43;
      --mastered-line: rgba(138, 90, 67, 0.34);
      --mastered-fill: radial-gradient(circle at 30% 28%, rgba(255,248,239,0.96), rgba(236,221,201,0.98) 72%);
      --mastered-card: linear-gradient(180deg, rgba(255,255,255,0.84), rgba(246,237,224,0.94));
      --mastered-wash: radial-gradient(circle at 84% 18%, rgba(176,123,92,0.16), rgba(176,123,92,0.02) 52%);
    }}

    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(255,255,255,0.65), transparent 28%),
        linear-gradient(180deg, #f8f3e8 0%, #f1e7d2 100%);
      font-family: Georgia, 'Times New Roman', serif;
    }}

    .grain::before {{
      content: '';
      position: fixed;
      inset: 0;
      pointer-events: none;
      opacity: 0.07;
      background-image:
        linear-gradient(rgba(0,0,0,0.08) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,0,0,0.06) 1px, transparent 1px);
      background-size: 24px 24px;
      mix-blend-mode: multiply;
    }}

    .page {{
      width: min(1240px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 32px 0 80px;
      position: relative;
    }}

    .hero {{
      background: rgba(255,255,255,0.48);
      border: 1px solid rgba(34, 32, 24, 0.12);
      border-radius: 28px;
      padding: 40px 32px 30px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(4px);
      position: relative;
      overflow: hidden;
    }}

    .hero::after {{
      content: '';
      position: absolute;
      right: -70px;
      top: -70px;
      width: 220px;
      height: 220px;
      border-radius: 999px;
      background: radial-gradient(circle, rgba(142,75,46,0.18), rgba(142,75,46,0.02) 70%);
    }}

    .kicker {{
      margin: 0 0 10px;
      letter-spacing: 0.14em;
      font-size: 12px;
      text-transform: uppercase;
      color: var(--accent);
      font-weight: 700;
    }}

    h1 {{
      margin: 0;
      font-size: clamp(40px, 6vw, 72px);
      line-height: 0.98;
      letter-spacing: -0.04em;
      max-width: 820px;
    }}

    .lead {{
      margin: 18px 0 0;
      max-width: 760px;
      font-size: 18px;
      line-height: 1.75;
      color: var(--muted);
    }}

    .hero-meta {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-top: 28px;
    }}

    .meta-box {{
      padding: 16px 18px;
      border-radius: 18px;
      background: rgba(255,255,255,0.55);
      border: 1px solid rgba(34, 32, 24, 0.1);
    }}

    .meta-box span {{
      display: block;
      font-size: 12px;
      color: var(--muted);
      margin-bottom: 8px;
    }}

    .meta-box strong {{
      font-size: 22px;
      font-weight: 700;
    }}

    .progress-strip {{
      margin-top: 22px;
      padding: 18px;
      border-radius: 20px;
      background: rgba(255,255,255,0.6);
      border: 1px solid rgba(34, 32, 24, 0.1);
    }}

    .progress-head {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      margin-bottom: 12px;
    }}

    .progress-head h3 {{
      margin: 0;
      font-size: 18px;
    }}

    .progress-head p {{
      margin: 4px 0 0;
      color: var(--muted);
      font-size: 14px;
    }}

    .progress-value {{
      font-size: 28px;
      font-weight: 700;
      white-space: nowrap;
    }}

    .progress-bar {{
      height: 12px;
      border-radius: 999px;
      overflow: hidden;
      background: rgba(34, 32, 24, 0.08);
    }}

    .progress-bar-fill {{
      width: 0%;
      height: 100%;
      border-radius: 999px;
      background: linear-gradient(90deg, #4b6b53 0%, #78a06f 100%);
      transition: width 180ms ease;
    }}

    .jump-nav {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin: 26px 0 0;
    }}

    .control-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 18px;
    }}

    .jump-nav a {{
      text-decoration: none;
      color: var(--ink);
      padding: 10px 16px;
      border-radius: 999px;
      border: 1px solid rgba(34, 32, 24, 0.12);
      background: rgba(255,255,255,0.58);
      font-size: 14px;
    }}

    .filter-toggle {{
      appearance: none;
      border: 1px solid rgba(34, 32, 24, 0.12);
      background: rgba(255,255,255,0.58);
      color: var(--ink);
      padding: 10px 16px;
      border-radius: 999px;
      font-size: 14px;
      font-family: inherit;
      cursor: pointer;
    }}

    .filter-toggle.subtle {{
      color: var(--muted);
      border-color: rgba(34, 32, 24, 0.10);
      background: rgba(255,255,255,0.42);
    }}

    .filter-toggle.active {{
      background: rgba(75,107,83,0.14);
      border-color: rgba(75,107,83,0.28);
      color: var(--green);
      font-weight: 700;
    }}

    .tier-section {{
      margin-top: 36px;
      padding: 28px 0 0;
    }}

    .section-head {{
      display: flex;
      justify-content: space-between;
      align-items: end;
      gap: 20px;
      margin-bottom: 18px;
    }}

    .section-side {{
      display: flex;
      flex-direction: column;
      align-items: end;
      gap: 8px;
    }}

    .eyebrow {{
      margin: 0 0 6px;
      font-size: 12px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--olive);
      font-weight: 700;
    }}

    h2 {{
      margin: 0;
      font-size: clamp(30px, 4vw, 44px);
      letter-spacing: -0.03em;
    }}

    .section-desc {{
      margin: 10px 0 0;
      color: var(--muted);
      line-height: 1.7;
      max-width: 720px;
      font-size: 16px;
    }}

    .section-count, .section-progress {{
      white-space: nowrap;
      font-size: 14px;
      color: var(--muted);
      padding: 10px 14px;
      border-radius: 999px;
      background: rgba(255,255,255,0.55);
      border: 1px solid rgba(34, 32, 24, 0.1);
    }}

    .card-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 18px;
    }}

    .word-card {{
      position: relative;
      overflow: hidden;
      background: rgba(255,255,255,0.68);
      border: 1px solid rgba(34, 32, 24, 0.1);
      border-radius: 22px;
      padding: 18px;
      box-shadow: 0 10px 28px rgba(45, 35, 18, 0.08);
      min-height: 280px;
      display: flex;
      flex-direction: column;
      transition: transform 180ms ease, border-color 180ms ease, background 180ms ease;
    }}

    .word-card.mastered {{
      border-color: rgba(142,75,46,0.18);
      background: var(--mastered-card);
      box-shadow:
        0 12px 32px rgba(45, 35, 18, 0.08),
        inset 0 1px 0 rgba(255,255,255,0.55);
    }}

    .word-card.mastered::after {{
      content: '';
      position: absolute;
      inset: 0;
      pointer-events: none;
      background: var(--mastered-wash);
    }}

    .card-top {{
      display: flex;
      justify-content: space-between;
      align-items: start;
      gap: 12px;
      margin-bottom: 16px;
    }}

    .top-actions {{
      display: flex;
      flex-direction: column;
      align-items: end;
      gap: 8px;
    }}

    .rank {{
      font-size: 12px;
      color: var(--muted);
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}

    .badge {{
      font-size: 12px;
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(142,75,46,0.12);
      color: var(--accent);
      font-weight: 700;
    }}

    .mastery-toggle {{
      appearance: none;
      border: 1px solid rgba(34, 32, 24, 0.14);
      background: rgba(255,255,255,0.84);
      color: var(--muted);
      border-radius: 999px;
      padding: 9px 14px;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.02em;
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.65);
      cursor: pointer;
      transition:
        background 160ms ease,
        border-color 160ms ease,
        color 160ms ease,
        box-shadow 160ms ease,
        transform 160ms ease;
    }}

    .mastery-toggle:hover {{
      transform: translateY(-1px);
      border-color: rgba(34, 32, 24, 0.22);
    }}

    .mastery-toggle:focus-visible {{
      outline: none;
      box-shadow:
        0 0 0 3px rgba(142,75,46,0.14),
        inset 0 1px 0 rgba(255,255,255,0.7);
    }}

    .word-card.mastered .mastery-toggle {{
      position: relative;
      border-color: var(--mastered-line);
      background: var(--mastered-fill);
      color: var(--mastered-ink);
      box-shadow:
        0 8px 18px rgba(118, 81, 61, 0.10),
        inset 0 1px 0 rgba(255,255,255,0.72);
      transform: rotate(-4deg);
    }}

    .word-card.mastered .mastery-toggle::after {{
      content: '';
      position: absolute;
      inset: 4px;
      border: 1px dashed rgba(138, 90, 67, 0.24);
      border-radius: 999px;
      pointer-events: none;
    }}

    .word {{
      margin: 0;
      font-size: 34px;
      line-height: 1.02;
      letter-spacing: -0.04em;
      font-weight: 700;
    }}

    .meaning {{
      margin: 12px 0 0;
      font-size: 18px;
      line-height: 1.75;
      color: #2d2a20;
    }}

    .forms {{
      margin: 16px 0 0;
      padding-top: 14px;
      border-top: 1px dashed rgba(34, 32, 24, 0.14);
      color: var(--muted);
      font-size: 14px;
      line-height: 1.7;
    }}

    .forms span {{
      display: block;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--olive);
      margin-bottom: 6px;
    }}

    .meta {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
      margin-top: auto;
      padding-top: 18px;
    }}

    .meta-item {{
      background: rgba(239,230,212,0.75);
      border-radius: 16px;
      padding: 12px 12px 10px;
      border: 1px solid rgba(34, 32, 24, 0.08);
    }}

    .meta-item span {{
      display: block;
      font-size: 11px;
      color: var(--muted);
      margin-bottom: 8px;
      letter-spacing: 0.06em;
    }}

    .meta-item strong {{
      font-size: 22px;
      font-weight: 700;
    }}

    .footer-note {{
      margin-top: 42px;
      padding: 18px 20px;
      border-radius: 20px;
      background: rgba(255,255,255,0.48);
      border: 1px solid rgba(34, 32, 24, 0.1);
      color: var(--muted);
      line-height: 1.8;
    }}

    @media (max-width: 1100px) {{
      .card-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .hero-meta {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}

    @media (max-width: 720px) {{
      .page {{ width: min(100vw - 20px, 1240px); padding-top: 20px; }}
      .hero {{ padding: 28px 20px 22px; border-radius: 22px; }}
      .hero-meta {{ grid-template-columns: 1fr; }}
      .progress-head {{ display: block; }}
      .progress-value {{ margin-top: 12px; display: block; }}
      .section-head {{ display: block; }}
      .section-side {{ align-items: start; margin-top: 14px; }}
      .card-grid {{ grid-template-columns: 1fr; }}
      .word {{ font-size: 30px; }}
      .meaning {{ font-size: 17px; }}
    }}
  </style>
</head>
<body class="grain">
  <main class="page">
    <header class="hero">
      <p class="kicker">CET-4 Wordbook</p>
      <h1>{safe_title}</h1>
      <p class="lead">这不是一张表格，而是一份更适合连续阅读和记忆的本地词书页。内容来自 2021-2025 年四级真题词频筛选，并补充了中文义项与常见词形，适合二轮复习时按优先级往下读。</p>
      <div class="hero-meta">
        <div class="meta-box"><span>数据范围</span><strong>2021-2025 真题</strong></div>
        <div class="meta-box"><span>词书规模</span><strong>Top {total_words}</strong></div>
        <div class="meta-box"><span>优先掌握</span><strong>{counts['优先掌握']}</strong></div>
        <div class="meta-box"><span>重点熟悉 / 可以积累</span><strong>{counts['重点熟悉']} / {counts['可以积累']}</strong></div>
      </div>
      <section class="progress-strip">
        <div class="progress-head">
          <div>
            <h3>记忆进度</h3>
            <p>每张词卡都可以标记“已记住”，进度会保存在当前浏览器。</p>
          </div>
          <div class="progress-value" id="overall-progress-text">已记住 0 / {total_words}</div>
        </div>
        <div class="progress-bar">
          <div class="progress-bar-fill" id="overall-progress-fill"></div>
        </div>
      </section>
      <div class="control-row">
        <nav class="jump-nav">
          <a href="#优先掌握">优先掌握</a>
          <a href="#重点熟悉">重点熟悉</a>
          <a href="#可以积累">可以积累</a>
        </nav>
        <button id="filter-unmastered-toggle" class="filter-toggle" type="button">只看待记</button>
        <button id="reset-progress-button" class="filter-toggle subtle" type="button">重置进度</button>
      </div>
    </header>

    {''.join(sections)}

    <section class="footer-note">
      词表说明：中文义项为程序化整理结果，更适合快速记忆与识别；如果你后面准备继续精修，可以优先从前 100 个词开始补更贴近真题语境的义项和例句。
    </section>
  </main>

  <script>
    const STORAGE_KEY = 'wordtrace-cet4-top300-progress-v1';
    const FILTER_STORAGE_KEY = 'wordbook-filter-unmastered-v1';
    const cards = [...document.querySelectorAll('.word-card')];
    const buttons = [...document.querySelectorAll('.mastery-toggle')];
    const filterToggle = document.getElementById('filter-unmastered-toggle');
    const resetButton = document.getElementById('reset-progress-button');
    const total = cards.length;

    function loadProgress() {{
      try {{
        return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{{}}');
      }} catch (e) {{
        return {{}};
      }}
    }}

    function saveProgress(progress) {{
      localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
    }}

    function loadFilterState() {{
      return localStorage.getItem(FILTER_STORAGE_KEY) === '1';
    }}

    function saveFilterState(value) {{
      localStorage.setItem(FILTER_STORAGE_KEY, value ? '1' : '0');
    }}

    function resetProgressState() {{
      localStorage.removeItem(STORAGE_KEY);
      localStorage.removeItem(FILTER_STORAGE_KEY);
      Object.keys(progress).forEach(key => delete progress[key]);
      showUnmasteredOnly = false;
      applyProgress(progress, showUnmasteredOnly);
    }}

    function applyProgress(progress, showUnmasteredOnly) {{
      let masteredCount = 0;
      const sectionState = {{}};

      cards.forEach(card => {{
        const key = card.dataset.wordKey;
        const tier = card.dataset.tier;
        const mastered = !!progress[key];
        if (!sectionState[tier]) {{
          sectionState[tier] = {{ done: 0, total: 0 }};
        }}
        sectionState[tier].total += 1;
        if (mastered) {{
          masteredCount += 1;
          sectionState[tier].done += 1;
          card.classList.add('mastered');
        }} else {{
          card.classList.remove('mastered');
        }}

        const shouldHide = showUnmasteredOnly && mastered;
        card.style.display = shouldHide ? 'none' : '';
      }});

      buttons.forEach(button => {{
        const mastered = !!progress[button.dataset.wordKey];
        button.textContent = mastered ? '已记住' : '待记';
        button.setAttribute('aria-pressed', mastered ? 'true' : 'false');
      }});

      const overallText = document.getElementById('overall-progress-text');
      const overallFill = document.getElementById('overall-progress-fill');
      const percent = total ? Math.round(masteredCount / total * 100) : 0;
      overallText.textContent = `已记住 ${{masteredCount}} / ${{total}}`;
      overallFill.style.width = `${{percent}}%`;

      filterToggle.classList.toggle('active', showUnmasteredOnly);
      filterToggle.textContent = showUnmasteredOnly ? '正在只看待记' : '只看待记';
      document.body.classList.toggle('show-unmastered-only', showUnmasteredOnly);

      Object.entries(sectionState).forEach(([tier, state]) => {{
        const el = document.getElementById(`section-progress-${{tier}}`);
        if (el) {{
          el.textContent = `已记住 ${{state.done}} / ${{state.total}}`;
        }}
      }});
    }}

    const progress = loadProgress();
    let showUnmasteredOnly = loadFilterState();
    applyProgress(progress, showUnmasteredOnly);

    buttons.forEach(button => {{
      button.addEventListener('click', () => {{
        const key = button.dataset.wordKey;
        progress[key] = !progress[key];
        saveProgress(progress);
        applyProgress(progress, showUnmasteredOnly);
      }});
    }});

    filterToggle.addEventListener('click', () => {{
      showUnmasteredOnly = !showUnmasteredOnly;
      saveFilterState(showUnmasteredOnly);
      applyProgress(progress, showUnmasteredOnly);
    }});

    resetButton.addEventListener('click', () => {{
      resetProgressState();
    }});
  </script>
</body>
</html>"""
