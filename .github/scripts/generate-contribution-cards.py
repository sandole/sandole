"""Generate SVG repo cards for open source contributions."""

import json
import os
import urllib.request

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
USERNAME = "sandole"
REPOS = [
    ("python", "cpython"),
    ("OpenBB-finance", "OpenBB"),
    ("run-llama", "llama_index"),
]
OUTPUT_DIR = "contribution-cards"


def gh_api(url: str):
    req = urllib.request.Request(url)
    if GITHUB_TOKEN:
        req.add_header("Authorization", f"token {GITHUB_TOKEN}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def fetch_repo(owner: str, repo: str) -> dict:
    return gh_api(f"https://api.github.com/repos/{owner}/{repo}")


def fetch_pr_counts(owner: str, repo: str) -> dict:
    base = "https://api.github.com/search/issues"
    merged = gh_api(
        f"{base}?q=type:pr+author:{USERNAME}+repo:{owner}/{repo}+is:merged"
    )["total_count"]
    opened = gh_api(
        f"{base}?q=type:pr+author:{USERNAME}+repo:{owner}/{repo}+is:open"
    )["total_count"]
    return {"merged": merged, "open": opened}


def format_count(n: int) -> str:
    if n >= 1000:
        return f"{n / 1000:.1f}k"
    return str(n)


def lang_color(lang: str) -> str:
    colors = {
        "Python": "#3572A5",
        "C": "#555555",
        "Jupyter Notebook": "#DA5B0B",
        "TypeScript": "#3178C6",
        "JavaScript": "#F1E05A",
    }
    return colors.get(lang, "#8B8B8B")


def generate_svg(data: dict, prs: dict) -> str:
    name = data["full_name"]
    desc = data.get("description") or ""
    if len(desc) > 70:
        desc = desc[:67] + "..."
    stars = format_count(data["stargazers_count"])
    forks = format_count(data["forks_count"])
    lang = data.get("language") or ""
    lc = lang_color(lang)
    merged = prs["merged"]
    opened = prs["open"]

    # Build contribution badges
    badges = ""
    badge_x = 20
    if merged > 0:
        label = f"{merged} merged"
        w = len(label) * 7 + 16
        badges += f"""  <rect x="{badge_x}" y="74" width="{w}" height="22" rx="11" fill="#238636"/>
  <svg x="{badge_x + 6}" y="77" width="16" height="16" viewBox="0 0 16 16" fill="#ffffff">
    <path d="M5.45 5.154A4.25 4.25 0 0 0 9.25 7.5h1.378a2.251 2.251 0 1 1 0 1.5H9.25A5.734 5.734 0 0 1 5 7.123v3.505a2.25 2.25 0 1 1-1.5 0V5.372a2.25 2.25 0 1 1 1.95-.218ZM4.25 13.5a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm8.5-4.5a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5ZM5 3.25a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Z"/>
  </svg>
  <text x="{badge_x + 24}" y="89" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif" font-size="11" font-weight="600" fill="#ffffff">{label}</text>
"""
        badge_x += w + 8
    if opened > 0:
        label = f"{opened} open"
        w = len(label) * 7 + 16
        badges += f"""  <rect x="{badge_x}" y="74" width="{w}" height="22" rx="11" fill="#1f6feb"/>
  <svg x="{badge_x + 6}" y="77" width="16" height="16" viewBox="0 0 16 16" fill="#ffffff">
    <path d="M1.5 3.25a2.25 2.25 0 1 1 3 2.122v5.256a2.251 2.251 0 1 1-1.5 0V5.372A2.25 2.25 0 0 1 1.5 3.25Zm5.677-.177L9.573.677A.25.25 0 0 1 10 .854V2.5h1A2.5 2.5 0 0 1 13.5 5v5.628a2.251 2.251 0 1 1-1.5 0V5a1 1 0 0 0-1-1h-1v1.646a.25.25 0 0 1-.427.177L7.177 3.427a.25.25 0 0 1 0-.354ZM3.75 2.5a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5Zm0 9.5a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5Zm8.25.75a.75.75 0 1 0 1.5 0 .75.75 0 0 0-1.5 0Z"/>
  </svg>
  <text x="{badge_x + 24}" y="89" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif" font-size="11" font-weight="600" fill="#ffffff">{label}</text>
"""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="150" viewBox="0 0 400 150">
  <rect width="400" height="150" rx="8" fill="#0d1117" stroke="#30363d" stroke-width="1"/>
  <!-- Repo icon -->
  <svg x="20" y="20" width="16" height="16" viewBox="0 0 16 16" fill="#8b949e">
    <path d="M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z"/>
  </svg>
  <text x="42" y="33" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif" font-size="14" font-weight="600" fill="#58a6ff">{name}</text>
  <!-- Description -->
  <text x="20" y="58" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif" font-size="12" fill="#8b949e">{desc}</text>
  <!-- PR badges -->
{badges}  <!-- Language -->
  <circle cx="28" cy="124" r="6" fill="{lc}"/>
  <text x="40" y="128" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif" font-size="12" fill="#8b949e">{lang}</text>
  <!-- Star icon -->
  <svg x="150" y="116" width="16" height="16" viewBox="0 0 16 16" fill="#8b949e">
    <path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"/>
  </svg>
  <text x="172" y="128" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif" font-size="12" fill="#8b949e">{stars}</text>
  <!-- Fork icon -->
  <svg x="220" y="116" width="16" height="16" viewBox="0 0 16 16" fill="#8b949e">
    <path d="M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75v-.878a2.25 2.25 0 1 1 1.5 0v.878a2.25 2.25 0 0 1-2.25 2.25h-1.5v2.128a2.251 2.251 0 1 1-1.5 0V8.5h-1.5A2.25 2.25 0 0 1 3.5 6.25v-.878a2.25 2.25 0 1 1 1.5 0ZM5 3.25a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Zm6.75.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm-3 8.75a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Z"/>
  </svg>
  <text x="242" y="128" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif" font-size="12" fill="#8b949e">{forks}</text>
</svg>"""


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for owner, repo in REPOS:
        data = fetch_repo(owner, repo)
        prs = fetch_pr_counts(owner, repo)
        svg = generate_svg(data, prs)
        filename = f"{owner}-{repo}.svg"
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, "w") as f:
            f.write(svg)
        print(f"Generated {path} (merged: {prs['merged']}, open: {prs['open']})")


if __name__ == "__main__":
    main()
