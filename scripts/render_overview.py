#!/usr/bin/env python3
"""Write README.md: one row per repository with what the daily snapshots in data/ say.

GitHub reports views and clones per day for the last 14 days; every snapshot repeats that window.
The totals here take each day once, from the newest snapshot that has it. Unique visitors and
cloners cannot be added up over days (one person on two days counts on both), so they are shown
for the latest 14 days only.

Standard library only: the workflow runner must not need a pip install.
"""

from __future__ import annotations

import sys
from pathlib import Path

from render_star_history import DATA_NAME, OUTPUT_NAME, read_snapshots

HEADER = """# Traffic

Daily GitHub statistics of the public repositories of [{owner}](https://github.com/{owner}), collected by
[a workflow](.github/workflows/traffic.yml) at 01:00 UTC. GitHub keeps views and clones for 14 days
only; the daily snapshots in [data/](data/) turn them into a history. GitHub reports counts, never who:
no names, no addresses.

| Repository | Stars | Forks | Views 14 d (unique) | Clones 14 d (unique) | Views since | Clones since | Release downloads | Top referrers 14 d |
|---|---:|---:|---:|---:|---:|---:|---:|---|
"""

FOOTER = """
"since" counts every day once, from the first snapshot on (the date in brackets). Release downloads are
GitHub's running total per release file, summed. Each repository's folder holds `traffic.jsonl` (one
snapshot per day), `stars-daily.json` (stars per day, without names) and `star-history.svg`.
"""


def daily_totals(snapshots: list[dict], kind: str) -> dict[str, int]:
    """Count per day for ``views`` or ``clones``; a newer snapshot overrides an older one."""
    days: dict[str, int] = {}
    for snapshot in sorted(snapshots, key=lambda entry: entry.get("date", "")):
        for entry in (snapshot.get(kind) or {}).get(kind) or []:
            days[entry["timestamp"][:10]] = entry["count"]
    return days


def release_downloads(snapshot: dict) -> int | None:
    releases = snapshot.get("releases")
    if releases is None:
        return None  # snapshot from before the field was collected
    return sum(asset["downloads"] for release in releases for asset in release["assets"])


def row(owner: str, directory: Path) -> str:
    snapshots = read_snapshots(directory / DATA_NAME)
    latest = max(snapshots, key=lambda entry: entry.get("date", ""))
    name = directory.name
    views, clones = latest.get("views") or {}, latest.get("clones") or {}
    view_days, clone_days = daily_totals(snapshots, "views"), daily_totals(snapshots, "clones")
    since = min(view_days | clone_days, default=latest["date"])
    downloads = release_downloads(latest)
    referrers = ", ".join(f"{entry['referrer']} ({entry['count']})" for entry in (latest.get("referrers") or [])[:3])
    chart = f"[{name}](https://github.com/{owner}/{name}) · [chart](data/{name}/{OUTPUT_NAME})"
    return (
        f"| {chart} | {latest.get('stars', '')} | {latest.get('forks', '')} "
        f"| {views.get('count', 0)} ({views.get('uniques', 0)}) | {clones.get('count', 0)} ({clones.get('uniques', 0)}) "
        f"| {sum(view_days.values())} ({since}) | {sum(clone_days.values())} ({since}) "
        f"| {'' if downloads is None else downloads} | {referrers or '–'} |"
    )


def main() -> int:
    """render_overview.py <owner> <data dir>: README.md in the current directory."""
    if len(sys.argv) != 3:
        raise SystemExit("usage: render_overview.py <owner> <data dir>")
    owner, data = sys.argv[1], Path(sys.argv[2])
    directories = sorted((path for path in data.iterdir() if (path / DATA_NAME).exists()), key=lambda path: path.name.lower())
    rows = "\n".join(row(owner, directory) for directory in directories)
    Path("README.md").write_text(HEADER.format(owner=owner) + rows + "\n" + FOOTER, encoding="utf-8")
    print(f"README.md: {len(directories)} repositories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
