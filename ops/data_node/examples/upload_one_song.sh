#!/usr/bin/env bash
set -euo pipefail

LOCAL_FILE="${1:?usage: upload_one_song.sh LOCAL_FILE USER@SERVER}"
SERVER="${2:?usage: upload_one_song.sh LOCAL_FILE USER@SERVER}"
NAME="$(basename "$LOCAL_FILE")"

scp "$LOCAL_FILE" "$SERVER:/var/lib/moodify/staging/$NAME.part"
ssh "$SERVER" "mv '/var/lib/moodify/staging/$NAME.part' '/var/lib/moodify/inbox/$NAME'"

echo "Submitted atomically: $NAME"
