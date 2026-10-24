# Lone Mesa Field (mobile)

Engineer's phone app for the CaseQuest 2026 prototype. Expo SDK 57, Expo Router, TypeScript.

Only a placeholder home screen exists so far.

## Run on an Android phone

Requires Node 20+ and Expo Go 57 on the phone (Expo Go only opens projects on its own SDK).

```bash
cd mobile
npm install
npx expo start --lan
```

Scan the QR code with Expo Go. If the phone is on USB and the network blocks LAN traffic:

```bash
adb reverse tcp:8081 tcp:8081
adb shell am start -a android.intent.action.VIEW -d exp://127.0.0.1:8081 host.exp.exponent
```

## Checks

```bash
npm run typecheck
npm run lint
```

## Layout

| Path | What it is |
|---|---|
| `src/app/` | Routes only (Expo Router). Every file is a screen |
| `src/components/` | Shared UI |
| `src/constants/theme.ts` | Colors, fonts, spacing |
| `src/hooks/` | Shared hooks |

Add packages with `npx expo install <pkg>` so versions match the SDK.
