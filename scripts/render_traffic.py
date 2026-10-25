#!/usr/bin/env python3
"""Render data/<repo>/traffic.svg: unique visitors and unique cloners per week (summed over the
days; one person on two days counts twice), the cloners split into automated at least and possibly
people (see traffic_history.py).

Two panels with a scale each: cloners are often many times the visitors, one scale would flatten
the visitors to nothing. Same look as the star chart.

Standard library only: the workflow runner must not need a pip install.
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

from render_star_history import COLORS, DATA_NAME, FONT, MONTHS, nice_step, read_snapshots
from traffic_history import Day, days

OUTPUT_NAME = "traffic.svg"
WIDTH = 800
PANEL_HEIGHT = 150
MARGIN_LEFT = 55
MARGIN_RIGHT = 24
MARGIN_TOP = 60
PANEL_GAP = 46
MARGIN_BOTTOM = 52
AUTOMATED_COLOR = "#8b949e"
CLONE_COLOR = "#d29922"


def weeks(history: list[Day]) -> list[tuple[date, int, int, int]]:
    """(Monday, visitors, cloners possibly people, cloners automated at least) per week."""
    buckets: dict[date, list[int]] = {}
    for day in history:
        monday = day.day - timedelta(days=day.day.weekday())
        bucket = buckets.setdefault(monday, [0, 0, 0])
        bucket[0] += day.view_uniques
        bucket[1] += day.clone_uniques - day.automated_cloners
        bucket[2] += day.automated_cloners
    return [(monday, *values) for monday, values in sorted(buckets.items())]


def panel(rows: list[tuple[date, list[tuple[int, str]]]], top: float, title: str) -> list[str]:
    """Stacked weekly bars from the bottom of the panel; each row's parts as (value, color)."""
    plot_width = WIDTH - MARGIN_LEFT - MARGIN_RIGHT
    highest = max((sum(value for value, _ in parts) for _, parts in rows), default=0)
    step = nice_step(max(highest, 1))
    y_max = ((max(highest, 1) - 1) // step + 1) * step
    bottom = top + PANEL_HEIGHT
    bar = plot_width / len(rows)
    grid = f'stroke="{COLORS["grid"]}" stroke-width="1" opacity="0.28"'
    label = f'{FONT} font-size="11" fill="{COLORS["text"]}"'
    parts = [f'<text {FONT} font-size="12" font-weight="600" fill="{COLORS["title"]}" x="{MARGIN_LEFT}" y="{top - 10}">{title}</text>']
    for value in range(0, y_max + 1, step):
        y = bottom - PANEL_HEIGHT * value / y_max
        parts.append(f'<line {grid} x1="{MARGIN_LEFT}" y1="{y:.1f}" x2="{WIDTH - MARGIN_RIGHT}" y2="{y:.1f}"/>')
        parts.append(f'<text {label} x="{MARGIN_LEFT - 10}" y="{y + 4:.1f}" text-anchor="end">{value}</text>')
    for index, (_, stack) in enumerate(rows):
        x = MARGIN_LEFT + index * bar + bar * 0.12
        y = bottom
        for value, color in stack:
            height = PANEL_HEIGHT * value / y_max
            if height > 0:
                y -= height
                parts.append(f'<rect fill="{color}" x="{x:.1f}" y="{y:.1f}" width="{bar * 0.76:.1f}" height="{height:.1f}"/>')
    return parts


def build_svg(repo: str, history: list[Day]) -> str:
    rows = weeks(history)
    views_top = MARGIN_TOP
    clones_top = views_top + PANEL_HEIGHT + PANEL_GAP
    height = clones_top + PANEL_HEIGHT + MARGIN_BOTTOM
    parts = [f'<text {FONT} font-size="15" font-weight="600" fill="{COLORS["title"]}" x="{MARGIN_LEFT}" y="22">Visitors and cloners per week</text>']
    parts += panel([(monday, [(views, COLORS["line"])]) for monday, views, _, _ in rows], views_top, "Unique visitors per day, summed")
    parts += panel(
        [(monday, [(automated, AUTOMATED_COLOR), (seen, CLONE_COLOR)]) for monday, _, seen, automated in rows],
        clones_top,
        "Unique cloners per day, summed",
    )
    legend_y = clones_top - 10
    parts.append(f'<rect fill="{CLONE_COLOR}" x="{WIDTH - 260}" y="{legend_y - 9}" width="10" height="10"/>')
    parts.append(f'<text {FONT} font-size="11" fill="{COLORS["text"]}" x="{WIDTH - 246}" y="{legend_y}">possibly people</text>')
    parts.append(f'<rect fill="{AUTOMATED_COLOR}" x="{WIDTH - 150}" y="{legend_y - 9}" width="10" height="10"/>')
    parts.append(f'<text {FONT} font-size="11" fill="{COLORS["text"]}" x="{WIDTH - 136}" y="{legend_y}">automated, at least</text>')
    plot_width = WIDTH - MARGIN_LEFT - MARGIN_RIGHT
    bar = plot_width / len(rows)
    shown_month = None
    for index, (monday, *_rest) in enumerate(rows):
        if monday.month != shown_month and monday.day <= 7:
            shown_month = monday.month
            x = MARGIN_LEFT + index * bar + bar / 2
            text = f"{MONTHS[monday.month - 1]} {monday.year}" if monday.month == 1 or index < 4 else MONTHS[monday.month - 1]
            parts.append(f'<text {FONT} font-size="11" fill="{COLORS["text"]}" x="{x:.1f}" y="{height - MARGIN_BOTTOM + 18}" text-anchor="middle">{text}</text>')
    first, last = history[0].day, history[-1].day
    parts.append(f'<text {FONT} font-size="11" fill="{COLORS["text"]}" x="{MARGIN_LEFT}" y="{height - 8}">{repo} &#183; {first.isoformat()} &#8211; {last.isoformat()} &#183; weeks from Monday, collected daily from the GitHub API</text>')
    body = "\n  ".join(parts)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" height="{height}" role="img" aria-label="Visitors and cloners per week for {repo}">
  {body}
</svg>
'''


def main() -> int:
    """render_traffic.py <owner> <data dir>: a chart for every repository folder in it."""
    if len(sys.argv) != 3:
        raise SystemExit("usage: render_traffic.py <owner> <data dir>")
    owner, data = sys.argv[1], Path(sys.argv[2])
    for directory in sorted(path for path in data.iterdir() if (path / DATA_NAME).exists()):
        history = days(read_snapshots(directory / DATA_NAME))
        if not history:
            print(f"{directory}: no views or clones yet")
            continue
        (directory / OUTPUT_NAME).write_text(build_svg(f"{owner}/{directory.name}", history), encoding="utf-8")
        print(f"{directory / OUTPUT_NAME}: {len(history)} days")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
