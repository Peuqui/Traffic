"""Several repositories in one line chart, grouped by size so the small ones do not lie flat at the
bottom under a big one.

Grouping is decided anew on every run from the numbers: repositories sorted by their peak, a group
takes the next one while its peak is at least 1/GROUP_RATIO of the group's largest, and holds at most
GROUP_SIZE lines; one left alone joins its closer neighbour if the joined group stays within twice
the ratio. A repository that grows moves to another
group by itself.

Same look as the star chart; standard library only.
"""

from __future__ import annotations

from datetime import date

from render_star_history import COLORS, FONT, MONTHS, month_ticks, nice_step

# Peaks within a group differ by at most this factor.
GROUP_RATIO = 4
# More lines than this are hard to tell apart.
GROUP_SIZE = 6
# Mid-tones that stay legible on light and dark backgrounds, one per line of a group.
LINE_COLORS = ("#2f81f7", "#d29922", "#3fb950", "#db61a2", "#a371f7", "#f0883e")

WIDTH = 800
HEIGHT = 340
MARGIN_LEFT = 55
MARGIN_RIGHT = 24
MARGIN_TOP = 80
MARGIN_BOTTOM = 42

Series = list[tuple[date, int]]


def groups(series: dict[str, Series]) -> list[list[str]]:
    """Names grouped by the size of their peak, biggest group first; series without any value left out."""
    peaks = {name: max(value for _, value in points) for name, points in series.items() if points}
    ordered = sorted((name for name in peaks if peaks[name] > 0), key=lambda name: (-peaks[name], name.lower()))
    result: list[list[str]] = []
    for name in ordered:
        group = result[-1] if result else None
        if group and len(group) < GROUP_SIZE and peaks[name] * GROUP_RATIO >= peaks[group[0]]:
            group.append(name)
        else:
            result.append([name])
    # A repository alone in its chart only repeats its own page: it joins the neighbour with the
    # closer peak, if that one has room.
    merged: list[list[str]] = []
    for index, group in enumerate(result):
        if len(group) > 1 or len(result) == 1:
            merged.append(group)
            continue
        # Only where the joined group stays within twice the ratio: a big one rather stays alone.
        neighbours = [g for g in (merged[-1] if merged else None, result[index + 1] if index + 1 < len(result) else None)
                      if g is not None and len(g) < GROUP_SIZE
                      and max(peaks[n] for n in g + group) <= 2 * GROUP_RATIO * min(peaks[n] for n in g + group)]
        if not neighbours:
            merged.append(group)
            continue
        closest = min(neighbours, key=lambda g: abs(peaks[g[0]] - peaks[group[0]]))
        closest.append(group[0])
        closest.sort(key=lambda name: (-peaks[name], name.lower()))
    return merged


def build_svg(title: str, footer: str, series: dict[str, Series], step_line: bool) -> str:
    """One line per name. ``step_line``: hold a value until the day it changes (counts like stars),
    else straight lines between the points (weekly sums)."""
    first = min(points[0][0] for points in series.values())
    last = max(points[-1][0] for points in series.values())
    span_days = max((last - first).days, 1)
    highest = max(value for points in series.values() for _, value in points)
    y_step = nice_step(highest)
    y_max = (highest // y_step + 1) * y_step
    plot_width = WIDTH - MARGIN_LEFT - MARGIN_RIGHT
    plot_height = HEIGHT - MARGIN_TOP - MARGIN_BOTTOM

    def x_of(day: date) -> float:
        return MARGIN_LEFT + plot_width * (day - first).days / span_days

    def y_of(value: float) -> float:
        return MARGIN_TOP + plot_height * (1 - value / y_max)

    grid = f'stroke="{COLORS["grid"]}" stroke-width="1" opacity="0.28"'
    label = f'{FONT} font-size="11" fill="{COLORS["text"]}"'
    parts = [f'<text {FONT} font-size="15" font-weight="600" fill="{COLORS["title"]}" x="{MARGIN_LEFT}" y="22">{title}</text>']
    for value in range(0, y_max + 1, y_step):
        y = y_of(value)
        parts.append(f'<line {grid} x1="{MARGIN_LEFT}" y1="{y:.1f}" x2="{WIDTH - MARGIN_RIGHT}" y2="{y:.1f}"/>')
        parts.append(f'<text {label} x="{MARGIN_LEFT - 10}" y="{y + 4:.1f}" text-anchor="end">{value}</text>')
    for position, tick in enumerate(month_ticks(first, last)):
        text = f"{MONTHS[tick.month - 1]} {tick.year}" if position == 0 or tick.month == 1 else MONTHS[tick.month - 1]
        parts.append(f'<text {label} x="{x_of(tick):.1f}" y="{HEIGHT - MARGIN_BOTTOM + 20}" text-anchor="middle">{text}</text>')
    legend_x, legend_y = MARGIN_LEFT, 45
    for index, (name, points) in enumerate(series.items()):
        color = LINE_COLORS[index % len(LINE_COLORS)]
        coordinates: list[str] = []
        previous = None
        for day, value in points:
            if step_line and previous is not None:
                coordinates.append(f"{x_of(day):.1f},{y_of(previous):.1f}")
            coordinates.append(f"{x_of(day):.1f},{y_of(value):.1f}")
            previous = value
        if step_line and points[-1][0] < last:
            coordinates.append(f"{x_of(last):.1f},{y_of(points[-1][1]):.1f}")
        parts.append(f'<polyline fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round" points="{" ".join(coordinates)}"/>')
        entry = f"{name} ({points[-1][1]})"
        # About 6.5 px per character at this size; a second row when the first is full.
        width = 34 + 6.5 * len(entry)
        if legend_x + width > WIDTH - MARGIN_RIGHT:
            legend_x, legend_y = MARGIN_LEFT, legend_y + 16
        parts.append(f'<rect fill="{color}" x="{legend_x}" y="{legend_y - 9}" width="10" height="10"/>')
        parts.append(f'<text {label} x="{legend_x + 14}" y="{legend_y}">{entry}</text>')
        legend_x += width
    axis = f'stroke="{COLORS["axis"]}" stroke-width="1" opacity="0.55"'
    parts.append(f'<line {axis} x1="{MARGIN_LEFT}" y1="{MARGIN_TOP}" x2="{MARGIN_LEFT}" y2="{HEIGHT - MARGIN_BOTTOM}"/>')
    parts.append(f'<line {axis} x1="{MARGIN_LEFT}" y1="{HEIGHT - MARGIN_BOTTOM}" x2="{WIDTH - MARGIN_RIGHT}" y2="{HEIGHT - MARGIN_BOTTOM}"/>')
    parts.append(f'<text {label} x="{MARGIN_LEFT}" y="{HEIGHT - 8}">{footer}</text>')
    body = "\n  ".join(parts)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}" role="img" aria-label="{title}">
  {body}
</svg>
'''
