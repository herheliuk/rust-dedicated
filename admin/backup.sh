#!/bin/bash
set -euo pipefail

SRC=/home/user/server/my_server_identity
DEST=/home/user/server_data_backups

NEW="$DEST/$(date +'%Y-%m-%d_%H-%M-%S')"
LAST="$DEST/latest"

mkdir -p "$NEW"

if [ -e "$LAST" ]; then
  LINK_DEST="--link-dest=$(readlink -f "$LAST")"
else
  LINK_DEST=""
fi

rsync -a \
  ${LINK_DEST:+$LINK_DEST} \
  --include="proceduralmap.*" \
  --include="relationship.*" \
  --include="sv.files.*" \
  --include="player.*" \
  --exclude="*" \
  "$SRC/" "$NEW/"

ln -sfn "$NEW" "$LAST"
