#!/bin/bash

APP_NAME="CommonApiSpring"
APP_HOME="/home/itbong/CommonApiSpring"
APP_WAR="$APP_HOME/CommonApiSpring.war"
LOG_DIR="$APP_HOME/logs"
APP_PORT=5100

mkdir -p $LOG_DIR

# ================================
# 기존 프로세스 종료 (포트 기반)
# ================================
PID=$(netstat -npl 2>/dev/null | grep ":$APP_PORT " | awk '{print $7}' | cut -d'/' -f1)

if [ -n "$PID" ]; then
  echo "Stopping existing $APP_NAME (PID: $PID, Port: $APP_PORT) ..."
  kill $PID
  sleep 5
  if kill -0 $PID 2>/dev/null; then
    echo "Force killing $APP_NAME (PID: $PID) ..."
    kill -9 $PID
  fi
else
  echo "No process found on port $APP_PORT"
fi

# ================================
# 포트 확인
# ================================
echo "Checking port $APP_PORT ..."
for i in {1..10}; do
  if ! netstat -npl 2>/dev/null | grep ":$APP_PORT " >/dev/null; then
    echo "Port $APP_PORT is free"
    break
  fi
  echo "Port $APP_PORT still in use... waiting ($i/10)"
  sleep 2
done

if netstat -npl 2>/dev/null | grep ":$APP_PORT " >/dev/null; then
  echo "ERROR: Port $APP_PORT is still in use. Aborting start."
  exit 1
fi

# ================================
# 새로운 프로세스 실행
# ================================
echo "Starting $APP_NAME ..."
nohup java -jar "$APP_WAR" \
  --spring.profiles.active=prod \
  --server.port=$APP_PORT \
  > "$LOG_DIR/$APP_NAME.out" 2>&1 < /dev/null &

NEW_PID=$!
echo "$APP_NAME started with PID $NEW_PID on port $APP_PORT"

# Jenkins 즉시 성공 응답
exit 0