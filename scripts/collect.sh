#!/usr/bin/env bash
# Tages-Snapshot der GitHub-Statistik aller öffentlichen eigenen Repos (ohne Forks und Archiv)
# nach data/<repo>/traffic.jsonl (eine Zeile pro Tag).
#
# data/<repo>/stars-daily.json (Sterne je Tag vor Messbeginn, ohne Namen) wurde beim Umzug am
# 25.10.2026 einmal mit der Anmeldung des Besitzers erzeugt: Die Liste der Sterne-Geber gibt GitHub
# seit Juni 2026 keinem Fine-grained-Schlüssel mehr heraus (HTTP 403). Ab Messbeginn reicht die
# tägliche Sternzahl; ein später neues Repo beginnt seinen Verlauf mit dem ersten Tag.
#
# GitHub hält Aufrufe und Klone nur 14 Tage vor; die tägliche Zeile macht daraus eine Historie,
# und ein ausgefallener Tag wird vom 14-Tage-Fenster des nächsten Laufs nachgeholt.
#
# Kein Fallback auf Ersatzwerte: Ein gescheiterter Abruf schreibt keine 0 in die Historie ("0 Sterne"
# ist eine Aussage, kein "nicht gemessen", und war als Phantom-Einbruch in der Kurve zu sehen). Ein
# Repo, dessen Abruf scheitert, wird übersprungen und in $FAILED_FILE vermerkt; die übrigen werden
# trotzdem gesammelt, der Lauf endet danach rot.
set -euo pipefail

OWNER=${OWNER:?OWNER fehlt}
FAILED_FILE=${FAILED_FILE:-failed-repos.txt}
DATE=$(date -u +%Y-%m-%d)

collect() {
  local repo=$1 dir=data/$1
  local views clones referrers paths stars forks releases snapshot
  mkdir -p "$dir"

  views=$(gh api "repos/$OWNER/$repo/traffic/views")
  clones=$(gh api "repos/$OWNER/$repo/traffic/clones")
  referrers=$(gh api "repos/$OWNER/$repo/traffic/popular/referrers")
  paths=$(gh api "repos/$OWNER/$repo/traffic/popular/paths")
  stars=$(gh api "repos/$OWNER/$repo" --jq '.stargazers_count')
  forks=$(gh api "repos/$OWNER/$repo" --jq '.forks_count')
  # Downloads der Release-Dateien: GitHub zählt sie je Datei seit dem Hochladen auf, ohne
  # Zeitverlauf; die tägliche Zeile macht daraus einen. Ohne Releases eine leere Liste.
  releases=$(gh api "repos/$OWNER/$repo/releases" --paginate --slurp \
             | jq -c '[add // [] | .[] | {tag: .tag_name, published: .published_at,
                       assets: [.assets[] | {name, downloads: .download_count}]}]')

  # -c: eine Zeile pro Tag, damit die Datei echtes JSONL ist und der Duplikat-Check greift.
  snapshot=$(jq -nc \
    --arg date "$DATE" \
    --argjson views "$views" \
    --argjson clones "$clones" \
    --argjson referrers "$referrers" \
    --argjson paths "$paths" \
    --argjson stars "$stars" \
    --argjson forks "$forks" \
    --argjson releases "$releases" \
    '{date: $date, views: $views, clones: $clones, referrers: $referrers, paths: $paths,
      stars: $stars, forks: $forks, releases: $releases}')

  # Nicht doppelt speichern, wenn der Lauf am selben Tag wiederholt wird. Das optionale Leerzeichen
  # deckt beide Formate ab: übernommene Altbestände sind mehrzeilig-eingerückt, neue Zeilen kompakt.
  if [ -f "$dir/traffic.jsonl" ] && grep -qE "\"date\": ?\"$DATE\"" "$dir/traffic.jsonl"; then
    echo "$repo: $DATE schon vorhanden"
  else
    echo "$snapshot" >> "$dir/traffic.jsonl"
    echo "$repo: $DATE gespeichert"
  fi
}

# Je Repo ein eigener Prozess: In einer if-Bedingung schaltet Bash set -e ab, auch in Funktionen und
# Subshells darin; ein eigener Aufruf behält es, und ein Fehler bricht nur dieses Repo ab.
if [ "${1:-}" = "--repo" ]; then
  collect "$2"
  exit 0
fi

: > "$FAILED_FILE"
# Diese Liste von GitHub enthält nur öffentliche Repos; Forks und archivierte fallen weg.
repos=$(gh api "users/$OWNER/repos" --paginate \
          --jq '.[] | select(.fork | not) | select(.archived | not) | .name' | sort)
for repo in $repos; do
  # Ein Fehler in einem Repo hält die anderen nicht auf; die Ursache steht im Log darüber.
  if ! "$0" --repo "$repo"; then
    echo "::error::$repo: Abruf gescheitert"
    echo "$repo" >> "$FAILED_FILE"
  fi
done
