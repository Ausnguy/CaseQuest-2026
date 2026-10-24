# Lone Mesa Field (mobile)

Engineer's phone for the CaseQuest 2026 prototype. Expo SDK 57, Expo Router, TypeScript.

The phone is engineer R. Ortiz (`ENG-1`). It polls the dispatch API on Vercel (see `../web/README.md`), buzzes when the manager assigns a job and again when it is time to leave, and the engineer shakes the phone to drive to the site and back. The repair starts on its own once engineer and parts are both there.

The app talks to production by default. To use a laptop API instead:

```bash
(cd ../web && npm run dev)
adb reverse tcp:3300 tcp:3300
EXPO_PUBLIC_API_URL=http://127.0.0.1:3300 npx expo start --lan
```

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
| `src/app/` | Routes only (Expo Router). `index.tsx` is the job screen |
| `src/state/store.ts` | Polling, actions, shake detection, alerts |
| `src/components/` | Field map, alert banner, shared UI |
| `src/theme.ts` | Colors and fonts, same as the console |
| `@dispatch/*` | `../web/lib/*`, the shared dispatch model |

Add packages with `npx expo install <pkg>` so versions match the SDK.
