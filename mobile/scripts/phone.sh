#!/usr/bin/env bash
# Starts the engineer app against the live dispatch server (never a local API).
# With an Android phone on USB it forwards Metro and opens the app in Expo Go;
# otherwise scan the QR code with Expo Go on the same wifi.
set -euo pipefail

API_URL="https://casequest-2026.vercel.app"
cd "$(dirname "$0")/.."

if ! curl -fsS --max-time 8 "$API_URL/api/state" -o /dev/null; then
  echo "Dispatch server at $API_URL is not answering. Check your connection or the Vercel deployment." >&2
  exit 1
fi

[ -d node_modules ] || npm install

export EXPO_PUBLIC_API_URL="$API_URL"

if command -v adb >/dev/null && adb get-state >/dev/null 2>&1; then
  adb reverse tcp:8081 tcp:8081 >/dev/null
  echo "Phone on USB. Opening the app in Expo Go once Metro is up."
  ( until curl -fsS --max-time 2 http://127.0.0.1:8081/status >/dev/null 2>&1; do sleep 1; done
    adb shell am start -a android.intent.action.VIEW -d "exp://127.0.0.1:8081" host.exp.exponent >/dev/null ) &
  exec npx expo start --localhost --clear
fi

echo "No phone on USB. Scan the QR code with Expo Go (same wifi as this computer)."
exec npx expo start --lan --clear
