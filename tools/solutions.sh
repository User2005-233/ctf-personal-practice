#!/usr/bin/env bash
# Reference solutions. Run as `student`:  bash tools/solutions.sh
# Used by ./verify to prove every lab is solvable from a clean state.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
if [ -f "$HERE/../README.md" ] && [ -d "$HERE/../module-01-linux" ]; then
  cd "$HERE/.."
fi
COURSE=$(pwd)
mkdir -p answers

# ---- Lab 01 -------------------------------------------------------------
grep -rh "flag part" /srv/lab/01 | sort | sed 's/.*: //' | tr -d '\n' > answers/01.txt
printf '\n' >> answers/01.txt
find /srv/lab/01 -samefile /srv/lab/01/inbox/notes.txt \
  | grep -v '^/srv/lab/01/inbox/notes.txt$' >> answers/01.txt
readlink /srv/lab/01/shared/link >> answers/01.txt

# ---- Lab 02 -------------------------------------------------------------
cd /srv/lab/02
IP=$(awk '$9 == 404 {print $1}' access.log | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')
N=$(awk -v ip="$IP" '$1 == ip && $9 == 404' access.log | wc -l)
USER=$(grep 'Accepted password' auth.log | grep -v 'from 10\.' | awk '{print $9}' | head -1)
FLAG=$(grep -o 'echo [A-Za-z0-9+/=]* | base64 -d > /tmp/.stash' \
        backup/home/svc_backup/.bash_history | awk '{print $2}' | base64 -d)
cd "$COURSE" >/dev/null
printf '%s\n%s\n%s\n%s\n' "$IP" "$N" "$USER" "$FLAG" > answers/02.txt

# ---- Lab 03 -------------------------------------------------------------
cd /srv/lab/03
./bin/find secrets -maxdepth 1 -name flag.txt -exec cat {} \; > "$COURSE/answers/03.txt"
printf '/srv/lab/03/bin/find\n\n' >> "$COURSE/answers/03.txt"
find /srv/lab/03 -perm -0002 -not -type l -exec chmod o-w {} +
cd "$COURSE"

# ---- Lab 04 -------------------------------------------------------------
P=$(cat /srv/lab/04/.svc/agent.pid)
tr '\0' '\n' < "/proc/$P/cmdline" | grep -o 'FLAG{[^}]*}' > answers/04.txt
lsof -p "$P" 2>/dev/null | awk '/beacon\.log$/ {print $NF}' | tail -1 >> answers/04.txt
printf '\n' >> answers/04.txt
kill "$P" || true
sleep 1

# ---- Lab 05 -------------------------------------------------------------
printf '#!/bin/sh\n/usr/bin/cat /srv/lab/05/secrets/flag.txt > /srv/lab/05/out/flag.txt\n' \
  > /srv/lab/05/bin/tar
chmod +x /srv/lab/05/bin/tar
for _ in $(seq 1 12); do
  [ -s /srv/lab/05/out/flag.txt ] && break
  sleep 1
done
cat /srv/lab/05/out/flag.txt > answers/05.txt
printf '/srv/lab/05/bin\n\n' >> answers/05.txt

echo "solutions complete"
