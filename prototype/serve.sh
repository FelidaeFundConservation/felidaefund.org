#!/bin/sh
# Static server for the prototype, detached so it outlives any one session.
# The in-app preview server kept dying with the session; this does not.
#   ./prototype/serve.sh        start (no-op if already up)
#   ./prototype/serve.sh stop   stop it
PORT=8811
DIR=$(cd "$(dirname "$0")" && pwd)

if [ "$1" = "stop" ]; then
  pid=$(lsof -ti tcp:$PORT 2>/dev/null)
  [ -n "$pid" ] && kill "$pid" && echo "stopped $pid" || echo "nothing on $PORT"
  exit 0
fi

if lsof -ti tcp:$PORT >/dev/null 2>&1; then
  echo "already serving $PORT"
else
  cd "$DIR" || exit 1
  nohup python3 -m http.server $PORT >/tmp/felidae-prototype-$PORT.log 2>&1 &
  sleep 1
  echo "serving $DIR on $PORT"
fi
echo "http://localhost:$PORT/species-cheetah.html"
