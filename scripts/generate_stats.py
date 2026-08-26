#!/usr/bin/env python3
import json
import os
import urllib.request

USERNAME = os.environ.get("GH_LOGIN", "t4zn")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

def fetch_contributions(user):
    try:
        url = f"https://github-contributions-api.jogruber.de/v4/{user}?y=last"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching contributions: {e}")
        return None

def fetch_repos(user):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        if GITHUB_TOKEN:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"
        req = urllib.request.Request(f"https://api.github.com/users/{user}/repos?per_page=100", headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching repos: {e}")
        return []

def generate_year_svg(data, out_path="assets/year.svg"):
    if data:
        total = data.get("total", {}).get("lastYear", 0)
        contribs = data.get("contributions", [])
        active_days = sum(1 for c in contribs if c["count"] > 0)
        weeks = []
        cur_w = 0
        for i, c in enumerate(contribs):
            cur_w += c["count"]
            if (i + 1) % 7 == 0 or i == len(contribs) - 1:
                weeks.append(cur_w)
                cur_w = 0
        best_week = max(weeks) if weeks else 0
    else:
        total = 1952
        active_days = 179
        best_week = 367
        weeks = [10, 15, 8, 20, 35, 12, 10, 5, 2, 18, 45, 90, 125, 40, 25, 30, 10, 5, 15, 8, 2, 4, 10, 15, 22, 14, 8, 12, 35, 60, 15, 4, 10, 12]

    width = 620
    height = 160
    chart_y_base = 142
    chart_max_h = 42
    max_val = max(max(weeks) if weeks else 1, 1)

    pts = []
    n = len(weeks)
    for idx, val in enumerate(weeks):
        x = 24 + idx * ((width - 48) / max(n - 1, 1))
        norm = (val / max_val)
        y = chart_y_base - (norm * chart_max_h)
        pts.append((x, y))

    path_d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f}"
    for pt in pts[1:]:
        path_d += f" L {pt[0]:.1f} {pt[1]:.1f}"

    last_pt = pts[-1]

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none">
  <style>
    .bignum {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
      font-size: 52px;
      font-weight: 700;
      fill: #24292f;
    }}
    .statnum {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 22px;
      font-weight: 700;
      fill: #24292f;
      text-anchor: end;
    }}
    .label {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 13px;
      font-weight: 400;
      fill: #6e7681;
    }}
    .statlabel {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 12px;
      font-weight: 400;
      fill: #6e7681;
      text-anchor: end;
    }}
    .sparkline {{
      stroke: #6e7681;
      stroke-width: 1.8;
      stroke-linejoin: round;
      stroke-linecap: round;
    }}
    .baseline {{
      stroke: #d0d7de;
      stroke-width: 1;
    }}
    .dot {{
      fill: #ffffff;
      stroke: #24292f;
      stroke-width: 1.5;
    }}
    @media (prefers-color-scheme: dark) {{
      .bignum, .statnum {{ fill: #f0f6fc; }}
      .label, .statlabel {{ fill: #8b949e; }}
      .sparkline {{ stroke: #c9d1d9; }}
      .baseline {{ stroke: #30363d; }}
      .dot {{ fill: #ffffff; stroke: #c9d1d9; }}
    }}
  </style>

  <!-- Big contribution count -->
  <text x="24" y="60" class="bignum">{total:,}</text>
  <text x="24" y="86" class="label">contributions in the last year</text>

  <!-- Right side stats -->
  <text x="{width - 24}" y="36" class="statnum">{active_days}</text>
  <text x="{width - 24}" y="52" class="statlabel">active days</text>

  <text x="{width - 24}" y="82" class="statnum">{best_week}</text>
  <text x="{width - 24}" y="98" class="statlabel">best week</text>

  <!-- Sparkline baseline -->
  <line x1="24" y1="{chart_y_base}" x2="{width - 24}" y2="{chart_y_base}" class="baseline"/>

  <!-- Sparkline -->
  <path d="{path_d}" class="sparkline" fill="none"/>

  <!-- End indicator dot -->
  <circle cx="{last_pt[0]:.1f}" cy="{last_pt[1]:.1f}" r="3.5" class="dot"/>
</svg>
"""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {out_path}")

def generate_streak_svg(data, out_path="assets/streak.svg"):
    cur_streak = 0
    max_streak = 0
    if data:
        contribs = data.get("contributions", [])
        streak = 0
        for c in contribs:
            if c["count"] > 0:
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 0
        for c in reversed(contribs):
            if c["count"] > 0:
                cur_streak += 1
            else:
                if cur_streak == 0:
                    continue
                break
    else:
        cur_streak = 2
        max_streak = 19

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="620" height="40" viewBox="0 0 620 40" fill="none">
  <style>
    .label {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 13px; fill: #6e7681; }}
    .val {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 13px; font-weight: 700; fill: #24292f; }}
    @media (prefers-color-scheme: dark) {{
      .label {{ fill: #8b949e; }}
      .val {{ fill: #f0f6fc; }}
    }}
  </style>
  <text x="0" y="24" class="label">current streak <tspan class="val">{cur_streak} days</tspan> &nbsp;·&nbsp; longest streak <tspan class="val">{max_streak} days</tspan></text>
</svg>
"""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {out_path}")

def generate_langs_svg(repos, out_path="assets/langs.svg"):
    lang_counts = {}
    for r in repos:
        l = r.get("language")
        if l:
            lang_counts[l] = lang_counts.get(l, 0) + 1
    
    total = sum(lang_counts.values()) or 1
    sorted_langs = sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)
    
    parts = []
    for l, count in sorted_langs[:4]:
        pct = int(round((count / total) * 100))
        parts.append(f'<tspan class="bold">{l}</tspan> {pct}%')
    
    body = " &nbsp;·&nbsp; ".join(parts) if parts else '<tspan class="bold">TypeScript</tspan> 36% &nbsp;·&nbsp; <tspan class="bold">JavaScript</tspan> 16% &nbsp;·&nbsp; <tspan class="bold">Python</tspan> 16%'

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="620" height="40" viewBox="0 0 620 40" fill="none">
  <style>
    .txt {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 13px; fill: #6e7681; }}
    .bold {{ font-weight: 700; fill: #24292f; }}
    @media (prefers-color-scheme: dark) {{
      .txt {{ fill: #8b949e; }}
      .bold {{ fill: #f0f6fc; }}
    }}
  </style>
  <text x="0" y="24" class="txt">{body}</text>
</svg>
"""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {out_path}")

if __name__ == "__main__":
    contrib_data = fetch_contributions(USERNAME)
    repos_data = fetch_repos(USERNAME)
    generate_year_svg(contrib_data)
    generate_streak_svg(contrib_data)
    generate_langs_svg(repos_data)
