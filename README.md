# Traffic

Daily GitHub statistics of the public repositories of [Peuqui](https://github.com/Peuqui), collected by
[a workflow](.github/workflows/traffic.yml) at 01:00 UTC. GitHub keeps views and clones for 14 days
only; the daily snapshots in [data/](data/) turn them into a history. GitHub reports counts, never who:
no names, no addresses. Repositories of a similar size share a chart; the groups follow the numbers.

## Stars

![Stars](charts/stars-1.svg)

![Stars](charts/stars-2.svg)

![Stars](charts/stars-3.svg)

## Visitors per week

![Visitors per week](charts/visitors-1.svg)

![Visitors per week](charts/visitors-2.svg)

![Visitors per week](charts/visitors-3.svg)

## Cloners per week

![Cloners per week](charts/cloners-1.svg)

![Cloners per week](charts/cloners-2.svg)

![Cloners per week](charts/cloners-3.svg)

## All repositories

| Repository | Stars | Forks | Visitors 14 d | Cloners 14 d | Automated, at least | Views since | Clones since | Release downloads |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| [Agent-Orc](data/Agent-Orc/README.md) | 1 | 0 | 0 | 397 | 100 % | 0 (11.10.2026) | 2035 (11.10.2026) | 0 |
| [AI-Connect](data/AI-Connect/README.md) | 8 | 4 | 11 | 82 | 87 % | 227 (09.02.2026) | 4258 (09.02.2026) | 11 |
| [AIfred-Intelligence](data/AIfred-Intelligence/README.md) | 39 | 3 | 26 | 355 | 93 % | 1513 (09.02.2026) | 36144 (09.02.2026) | 0 |
| [GPU-Orc](data/GPU-Orc/README.md) | 2 | 0 | 0 | 127 | 100 % | 0 (11.10.2026) | 249 (11.10.2026) | 0 |
| [Grafana-Dashboards](data/Grafana-Dashboards/README.md) | 0 | 0 | 1 | 58 | 98 % | 1 (11.10.2026) | 171 (11.10.2026) | 0 |
| [mtp-quant-transplant](data/mtp-quant-transplant/README.md) | 2 | 0 | 3 | 18 | 94 % | 5 (11.10.2026) | 28 (11.10.2026) | 0 |
| [NarcoCalc](data/NarcoCalc/README.md) | 1 | 0 | 3 | 65 | 97 % | 64 (09.02.2026) | 3235 (09.02.2026) | 0 |
| [sandbox-install](data/sandbox-install/README.md) | 1 | 0 | 1 | 24 | 100 % | 1 (11.10.2026) | 45 (11.10.2026) | 0 |
| [SolarSystemSimulator](data/SolarSystemSimulator/README.md) | 1 | 0 | 1 | 24 | 96 % | 1 (11.10.2026) | 63 (11.10.2026) | 0 |
| [STT-Suite](data/STT-Suite/README.md) | 1 | 0 | 0 | 89 | 100 % | 0 (11.10.2026) | 392 (11.10.2026) | 0 |
| [Traffic](data/Traffic/README.md) | 2 | 0 | 0 | 87 | 100 % | 0 (12.10.2026) | 167 (12.10.2026) | 0 |
| [TTS-Suite](data/TTS-Suite/README.md) | 2 | 0 | 0 | 129 | 100 % | 0 (11.10.2026) | 1173 (11.10.2026) | 0 |
| [vllm-bench](data/vllm-bench/README.md) | 0 | 0 | 0 | 25 | 100 % | 0 (10.10.2026) | 48 (10.10.2026) | 0 |

- **Visitors, cloners 14 d:** unique per day, summed over the last 14 days (one person on two days
  counts twice; GitHub's own 14-day uniques are in each snapshot).
- **Automated, at least:** the share of those cloners that cannot have been visitors of the page that
  day. People nearly always look at the page before they clone; mirrors, archives, scanners and
  crawlers do not. A lower bound, not a count: a bot may open the page too.
- **since:** every day counted once, from the first snapshot (date in brackets).
- **Release downloads:** GitHub's running total per release file, summed.

Each repository's folder holds its page with charts and referrers, `traffic.jsonl` (one snapshot per
day), `stars-daily.json` (stars per day, without names) and the charts.
