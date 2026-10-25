"""What the daily snapshots say over time: views and clones per day, referrers per 14-day window,
and how many cloners were automated at least.

GitHub reports views and clones per day for the last 14 days, and every snapshot repeats that
window; a day counts once, from the newest snapshot that has it. Referrers come as totals over the
14 days before a snapshot, so snapshots 14 days apart give windows that do not overlap.

Automated cloners, at least: on each day, the unique cloners beyond the unique visitors of the
repository page. People nearly always look at the page before they clone; mirrors, archives,
scanners and crawlers clone without. So at most as many people cloned as visited, and the rest was
automated. It is a lower bound, not a count: a bot may also open the page, and a person may clone
from a link without opening it. GitHub says nothing about who clones.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

WINDOW_DAYS = 14


@dataclass(frozen=True)
class Day:
    day: date
    views: int
    view_uniques: int
    clones: int
    clone_uniques: int

    @property
    def automated_cloners(self) -> int:
        """Unique cloners of the day that cannot have been visitors: at least this many were automated."""
        return max(0, self.clone_uniques - self.view_uniques)


def days(snapshots: list[dict]) -> list[Day]:
    """Every day any snapshot covers, oldest first; a day missing in one kind counts as 0 there
    (GitHub leaves out days without views or clones)."""
    views: dict[str, dict] = {}
    clones: dict[str, dict] = {}
    for snapshot in sorted(snapshots, key=lambda entry: entry.get("date", "")):
        for entry in (snapshot.get("views") or {}).get("views") or []:
            views[entry["timestamp"][:10]] = entry
        for entry in (snapshot.get("clones") or {}).get("clones") or []:
            clones[entry["timestamp"][:10]] = entry
    if not views and not clones:
        return []
    first = date.fromisoformat(min(views | clones))
    last = date.fromisoformat(max(views | clones))
    result = []
    for offset in range((last - first).days + 1):
        day = first + timedelta(days=offset)
        key = day.isoformat()
        view, clone = views.get(key, {}), clones.get(key, {})
        result.append(Day(day, view.get("count", 0), view.get("uniques", 0), clone.get("count", 0), clone.get("uniques", 0)))
    return result


def referrer_windows(snapshots: list[dict], count: int) -> list[tuple[date, dict[str, int]]]:
    """Referrers of up to ``count`` 14-day windows, newest first: (end of window, {referrer: views})."""
    by_day = {date.fromisoformat(entry["date"]): entry for entry in snapshots if entry.get("date")}
    if not by_day:
        return []
    windows = []
    end = max(by_day)
    earliest = min(by_day)
    while len(windows) < count and end >= earliest:
        snapshot = by_day.get(end)
        if snapshot is not None:
            referrers = {item["referrer"]: item["count"] for item in snapshot.get("referrers") or []}
            windows.append((end, referrers))
        end -= timedelta(days=WINDOW_DAYS)
    return windows
