#!/usr/bin/env python3
"""Write README.md (one row per repository) and data/<repo>/README.md (its charts and where its
visitors came from), from the daily snapshots in data/ (see traffic_history.py for the counting).

Standard library only: the workflow runner must not need a pip install.
"""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

from render_star_history import DATA_NAME, OUTPUT_NAME as STAR_CHART, read_snapshots
from render_traffic import OUTPUT_NAME as TRAFFIC_CHART
from traffic_history import WINDOW_DAYS, Day, days, referrer_windows

# How many 14-day windows of referrers a repository page shows (about half a year).
REFERRER_WINDOWS = 13

OVERVIEW = """# Traffic

Daily GitHub statistics of the public repositories of [{owner}](https://github.com/{owner}), collected by
[a workflow](.github/workflows/traffic.yml) at 01:00 UTC. GitHub keeps views and clones for 14 days
only; the daily snapshots in [data/](data/) turn them into a history. GitHub reports counts, never who:
no names, no addresses.

| Repository | Stars | Forks | Visitors 14 d | Cloners 14 d | Automated, at least | Views since | Clones since | Release downloads |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
{rows}

- **Visitors, cloners 14 d:** unique per day, summed over the last 14 days (one person on two days
  counts twice; GitHub's own 14-day uniques are in each snapshot).
- **Automated, at least:** the share of those cloners that cannot have been visitors of the page that
  day. People nearly always look at the page before they clone; mirrors, archives, scanners and
  crawlers do not. A lower bound, not a count: a bot may open the page too.
- **since:** every day counted once, from the first snapshot (date in brackets).
- **Release downloads:** GitHub's running total per release file, summed.

Each repository's folder holds its page with charts and referrers, `traffic.jsonl` (one snapshot per
day), `stars-daily.json` (stars per day, without names) and the charts.
"""

PAGE = """# {name}

[Repository](https://github.com/{owner}/{name}) · [all repositories](../../README.md)

![Star History]({star_chart})

![Visitors and cloners per week]({traffic_chart})

## Where visitors came from

Views from each referring site in the 14 days up to the date, newest first. Days without a snapshot
leave a gap.

{referrers}
"""


def last_days(history: list[Day], count: int) -> list[Day]:
    if not history:
        return []
    start = history[-1].day - timedelta(days=count - 1)
    return [day for day in history if day.day >= start]


def release_downloads(snapshot: dict) -> str:
    releases = snapshot.get("releases")
    if releases is None:
        return ""  # snapshot from before the field was collected
    return str(sum(asset["downloads"] for release in releases for asset in release["assets"]))


def overview_row(owner: str, directory: Path, snapshots: list[dict], history: list[Day]) -> str:
    latest = max(snapshots, key=lambda entry: entry.get("date", ""))
    name = directory.name
    recent = last_days(history, WINDOW_DAYS)
    visitors = sum(day.view_uniques for day in recent)
    cloners = sum(day.clone_uniques for day in recent)
    automated = sum(day.automated_cloners for day in recent)
    share = f"{round(100 * automated / cloners)} %" if cloners else "–"
    since = history[0].day.isoformat() if history else latest["date"]
    return (
        f"| [{name}](data/{name}/README.md) | {latest.get('stars', '')} | {latest.get('forks', '')} "
        f"| {visitors} | {cloners} | {share} "
        f"| {sum(day.views for day in history)} ({since}) | {sum(day.clones for day in history)} ({since}) "
        f"| {release_downloads(latest)} |"
    )


def referrer_table(snapshots: list[dict]) -> str:
    windows = referrer_windows(snapshots, REFERRER_WINDOWS)
    sites = sorted({site for _, referrers in windows for site in referrers},
                   key=lambda site: -sum(referrers.get(site, 0) for _, referrers in windows))
    if not sites:
        return "No referrers reported yet."
    header = "| Site | " + " | ".join(end.isoformat() for end, _ in windows) + " |"
    rule = "|---|" + "---:|" * len(windows)
    lines = [header, rule]
    for site in sites:
        cells = " | ".join(str(referrers.get(site, "")) for _, referrers in windows)
        lines.append(f"| {site} | {cells} |")
    return "\n".join(lines)


def main() -> int:
    """render_overview.py <owner> <data dir>: README.md here and a page per repository folder."""
    if len(sys.argv) != 3:
        raise SystemExit("usage: render_overview.py <owner> <data dir>")
    owner, data = sys.argv[1], Path(sys.argv[2])
    directories = sorted((path for path in data.iterdir() if (path / DATA_NAME).exists()),
                         key=lambda path: path.name.lower())
    rows = []
    for directory in directories:
        snapshots = read_snapshots(directory / DATA_NAME)
        history = days(snapshots)
        rows.append(overview_row(owner, directory, snapshots, history))
        page = PAGE.format(
            name=directory.name, owner=owner, star_chart=STAR_CHART, traffic_chart=TRAFFIC_CHART,
            referrers=referrer_table(snapshots),
        )
        (directory / "README.md").write_text(page, encoding="utf-8")
    Path("README.md").write_text(OVERVIEW.format(owner=owner, rows="\n".join(rows)), encoding="utf-8")
    print(f"README.md and {len(directories)} repository pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
