#!/usr/bin/env bash
# Tages-Snapshot der GitHub-Statistik aller öffentlichen eigenen Repos (ohne Forks und Archiv)
# nach data/<repo>/: traffic.jsonl (eine Zeile pro Tag) und stars-daily.json (Sterne je Tag).
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
  local views clones referrers paths stars forks releases created daily snapshot
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

  # Zeitstempel der einzelnen Sterne, auf Tage zusammengefasst und OHNE Benutzernamen: genau die
  # personenbezogenen Daten, wegen derer GitHub die API am 30.06.2026 gesperrt hat, gehören nicht in
  # ein öffentliches Repo. Als Repo-Admin liefert die API sie weiterhin. Reicht bis zum ersten Stern
  # zurück und schließt damit die Lücke vor Messbeginn. --slurp verträgt sich nicht mit --jq, daher
  # die nachgelagerte jq-Pipe; ohne --slurp käme pro Seite ein eigenes Array.
  created=$(gh api "repos/$OWNER/$repo" --jq '.created_at' | cut -dT -f1)
  daily=$(gh api "repos/$OWNER/$repo/stargazers" --paginate --slurp \
            -H "Accept: application/vnd.github.star+json" \
          | jq 'add // [] | [.[].starred_at | split("T")[0]]
                | group_by(.) | map({key: .[0], value: length}) | from_entries')
  # Erst in eine Temp-Datei: Ein gescheiterter Abruf darf die vorhandene Datei nicht leeren.
  jq -n --arg created "$created" --argjson daily "$daily" \
    '{repo_created: $created, daily_stars: $daily}' > "$dir/stars-daily.json.tmp"
  mv "$dir/stars-daily.json.tmp" "$dir/stars-daily.json"
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
