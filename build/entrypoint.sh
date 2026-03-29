#!/usr/bin/env bash
set -e

SERVER_SEED_FILE=/home/steam/rustserver/server/server.seed

SERVER_LOGS_FOLDER=/home/steam/rustserver/server/logs
SERVER_LOGS_FILE="$SERVER_LOGS_FOLDER/$(date +'%Y-%m-%d_%H-%M-%S').log"

SERVER_SAVE_FILES_FOLDER=/home/steam/rustserver/server/my_server_identity

mkdir -p "$SERVER_LOGS_FOLDER"

ln -sf "$SERVER_LOGS_FILE" "$SERVER_LOGS_FOLDER/last.log"
ln -sf "$SERVER_LOGS_FILE" ./last.log

# Wipe Cleanup

if [ -f "$SERVER_SEED_FILE" ]; then
  SERVER_SEED=$(cat "$SERVER_SEED_FILE")
else
  rand=$(od -An -N4 -tu4 /dev/urandom)
  SERVER_SEED=$(( rand & 0x7fffffff ))
  echo $SERVER_SEED > "$SERVER_SEED_FILE"

  if [ "${WIPE_SERVER_SAVE_FILES:-0}" -eq 1 ]; then
    rm -f "$SERVER_SAVE_FILES_FOLDER"/proceduralmap.* \
          "$SERVER_SAVE_FILES_FOLDER"/relationship.* \
          "$SERVER_SAVE_FILES_FOLDER"/sv.files.* \
          "$SERVER_SAVE_FILES_FOLDER"/player.*
  fi
fi

# Try to Update

set +e
/home/steam/steamcmd/steamcmd.sh \
  +force_install_dir "$(pwd)" \
  +login anonymous \
  +app_update 258550 \
  +quit
set -e

# Run

trap "curl -sS -X POST http://$ADMIN_CONTAINER_NAME:8000/docker/restart" SIGTERM SIGINT

./carbon.sh -batchmode \
  +server.seed $SERVER_SEED \
\
  +server.port $SERVER_PORT \
  +server.queryport $QUERY_PORT \
  +app.port $APP_PORT \
\
  +rcon.password ZxAKvf4zh7U3P1Pxxv70qjsRhHA3TK \
  +rcon.port 28016 \
\
  "$@" \
\
  -logfile "$SERVER_LOGS_FILE" 2>&1 \
\
  &

wait $!
