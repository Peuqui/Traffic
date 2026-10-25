#!/usr/bin/env python3
"""Write charts/<kind>-<n>.svg: stars, visitors and cloners of all repositories, several per chart,
grouped by size (see group_chart.py). The folder is written anew on every run, as the groups change.

Standard library only: the workflow runner must not need a pip install.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from group_chart import Series, build_svg, groups
from render_star_history import DATA_NAME, read_snapshots, star_series
from render_traffic import weeks
from traffic_history import days

CHARTS = Path("charts")
# (file name, title, footer, step line)
KINDS = {
    "stars": ("Stars", "stars per repository, daily", True),
    "visitors": ("Visitors per week", "unique visitors per day, summed per week from Monday", False),
    "cloners": ("Cloners per week", "unique cloners per day, summed per week from Monday", False),
}


def collect(data: Path) -> dict[str, dict[str, Series]]:
    series: dict[str, dict[str, Series]] = {kind: {} for kind in KINDS}
    for directory in sorted(path for path in data.iterdir() if (path / DATA_NAME).exists()):
        name = directory.name
        series["stars"][name], _ = star_series(directory)
        weekly = weeks(days(read_snapshots(directory / DATA_NAME)))
        series["visitors"][name] = [(monday, visitors) for monday, visitors, _, _ in weekly]
        series["cloners"][name] = [(monday, people + automated) for monday, _, people, automated in weekly]
    return series


def main() -> int:
    """render_groups.py <data dir>: the charts, and their file names per kind for the overview."""
    if len(sys.argv) != 2:
        raise SystemExit("usage: render_groups.py <data dir>")
    shutil.rmtree(CHARTS, ignore_errors=True)
    CHARTS.mkdir()
    for kind, by_name in collect(Path(sys.argv[1])).items():
        title, footer, step_line = KINDS[kind]
        for number, group in enumerate(groups(by_name), start=1):
            path = CHARTS / f"{kind}-{number}.svg"
            path.write_text(build_svg(title, footer, {name: by_name[name] for name in group}, step_line), encoding="utf-8")
            print(f"{path}: {', '.join(group)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
