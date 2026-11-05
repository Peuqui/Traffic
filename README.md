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
| [Agent-Orc](data/Agent-Orc/README.md) | 1 | 0 | 0 | 355 | 100 % | 0 (11.10.2026) | 2057 (11.10.2026) | 0 |
| [AI-Connect](data/AI-Connect/README.md) | 8 | 4 | 11 | 69 | 84 % | 228 (09.02.2026) | 4271 (09.02.2026) | 11 |
| [AIfred-Intelligence](data/AIfred-Intelligence/README.md) | 39 | 3 | 27 | 412 | 93 % | 1518 (09.02.2026) | 36906 (09.02.2026) | 0 |
| [GPU-Orc](data/GPU-Orc/README.md) | 2 | 0 | 0 | 140 | 100 % | 0 (11.10.2026) | 269 (11.10.2026) | 0 |
| [Grafana-Dashboards](data/Grafana-Dashboards/README.md) | 0 | 0 | 1 | 51 | 98 % | 1 (11.10.2026) | 174 (11.10.2026) | 0 |
| [mtp-quant-transplant](data/mtp-quant-transplant/README.md) | 2 | 0 | 5 | 17 | 88 % | 8 (11.10.2026) | 31 (11.10.2026) | 0 |
| [Mundwerk](data/Mundwerk/README.md) | 1 | 0 | 0 | 0 | – | 0 (23.10.2026) | 0 (23.10.2026) | 0 |
| [NarcoCalc](data/NarcoCalc/README.md) | 1 | 0 | 2 | 59 | 98 % | 64 (09.02.2026) | 3239 (09.02.2026) | 0 |
| [sandbox-install](data/sandbox-install/README.md) | 1 | 0 | 0 | 24 | 100 % | 1 (11.10.2026) | 47 (11.10.2026) | 0 |
| [SolarSystemSimulator](data/SolarSystemSimulator/README.md) | 1 | 0 | 1 | 22 | 95 % | 1 (11.10.2026) | 65 (11.10.2026) | 0 |
| [STT-Suite](data/STT-Suite/README.md) | 1 | 0 | 0 | 75 | 100 % | 0 (11.10.2026) | 394 (11.10.2026) | 0 |
| [Traffic](data/Traffic/README.md) | 2 | 0 | 0 | 118 | 100 % | 0 (12.10.2026) | 229 (12.10.2026) | 0 |
| [TTS-Suite](data/TTS-Suite/README.md) | 2 | 0 | 0 | 118 | 100 % | 0 (11.10.2026) | 1191 (11.10.2026) | 0 |
| [vllm-bench](data/vllm-bench/README.md) | 0 | 0 | 0 | 24 | 100 % | 0 (10.10.2026) | 49 (10.10.2026) | 0 |

- **Visitors, cloners 14 d:** unique per day, summed over the last 14 days (one person on two days
  counts twice; GitHub's own 14-day uniques are in each snapshot).
- **Automated, at least:** the share of those cloners that cannot have been visitors of the page that
  day. People nearly always look at the page before they clone; mirrors, archives, scanners and
  crawlers do not. A lower bound, not a count: a bot may open the page too.
- **since:** every day counted once, from the first snapshot (date in brackets).
- **Release downloads:** GitHub's running total per release file, summed.

Each repository's folder holds its page with charts and referrers, `traffic.jsonl` (one snapshot per
day), `stars-daily.json` (stars per day, without names) and the charts.
