"""Inject open source contribution data into README.md."""

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
README_PATH = "README.md"
START_MARKER = "<!-- CONTRIBUTIONS:START -->"
END_MARKER = "<!-- CONTRIBUTIONS:END -->"


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


def build_card(owner: str, repo: str, data: dict, prs: dict) -> str:
    desc = data.get("description") or ""
    lang = data.get("language") or ""
    stars = format_count(data["stargazers_count"])
    forks = format_count(data["forks_count"])

    # PR badges using shields.io
    badges = ""
    if prs["merged"] > 0:
        badges += (
            f'<a href="https://github.com/{owner}/{repo}/pulls?q=is%3Apr+author%3A{USERNAME}+is%3Amerged">'
            f'<img src="https://img.shields.io/badge/PRs_merged-{prs["merged"]}-238636?style=flat-square&logo=git-merge&logoColor=white" />'
            f"</a> "
        )
    if prs["open"] > 0:
        badges += (
            f'<a href="https://github.com/{owner}/{repo}/pulls?q=is%3Apr+author%3A{USERNAME}+is%3Aopen">'
            f'<img src="https://img.shields.io/badge/PRs_open-{prs["open"]}-1f6feb?style=flat-square&logo=git-pull-request&logoColor=white" />'
            f"</a> "
        )

    return f"""<td>
      <a href="https://github.com/{owner}/{repo}"><strong>{owner}/{repo}</strong></a><br>
      <sub>{desc}</sub><br><br>
      {badges.strip()}<br>
      <sub>
        <img src="https://img.shields.io/github/stars/{owner}/{repo}?style=flat-square&label=stars" />
        <img src="https://img.shields.io/github/forks/{owner}/{repo}?style=flat-square&label=forks" />
        <img src="https://img.shields.io/github/languages/top/{owner}/{repo}?style=flat-square" />
      </sub>
    </td>"""


def main():
    cards = []
    for owner, repo in REPOS:
        data = fetch_repo(owner, repo)
        prs = fetch_pr_counts(owner, repo)
        cards.append(build_card(owner, repo, data, prs))
        print(f"{owner}/{repo}: {prs['merged']} merged, {prs['open']} open")

    # Build table with 2 columns
    rows = []
    for i in range(0, len(cards), 2):
        row_cells = cards[i : i + 2]
        if len(row_cells) == 1:
            row_cells.append("<td></td>")
        rows.append("  <tr>\n    " + "\n    ".join(row_cells) + "\n  </tr>")

    table = "<table>\n" + "\n".join(rows) + "\n</table>"
    section = f"{START_MARKER}\n{table}\n{END_MARKER}"

    # Inject into README
    with open(README_PATH) as f:
        readme = f.read()

    start = readme.index(START_MARKER)
    end = readme.index(END_MARKER) + len(END_MARKER)
    readme = readme[:start] + section + readme[end:]

    with open(README_PATH, "w") as f:
        f.write(readme)

    print(f"Updated {README_PATH}")


if __name__ == "__main__":
    main()
