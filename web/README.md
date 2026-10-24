# Dispatch API and console hosting (Vercel)

Vercel project `casequest-2026` (root directory `web/`). Production: <https://casequest-2026.vercel.app>.

- `/` serves `prototype/parvius.html`, with `prototype/fieldwork.js` beside it and the failure model's `data/model/predictions.json` as `/model.json` (copied at build by `scripts/build.mjs`).
- `GET /api/state` returns the shared dispatch state as of now.
- `POST /api/action` applies one manager or engineer action (`lib/actions.ts` lists them).
- State is one JSON document in Upstash Redis, written with compare-and-set so concurrent writers retry instead of overwriting each other.
- `lib/dispatch.ts` is the whole model. It is pure and is also imported by the phone app, so both compute the same timings.

Vercel Functions have no WebSockets, so the console polls every 2 s and the phone every 1 s while open.

## Flow

1. The failure model flags a machine for the replay day: likely cause, chance of failure within 3 days, the readings behind it, and which kits are on the site shelf.
2. The manager clicks **Send engineer** (Overview, the map's field overview, the asset inspector or the Work board). Kits missing from the shelf are ordered first; each site's lead time is its observed 2025 median parts wait, played at 3 s per hour.
3. Dispatch books the engineer to leave so they arrive as the parts land. The 3D map shows the parts truck leaving the warehouse and the engineer driving out and back.
4. The phone buzzes with the job, then again when it is time to leave. The engineer shakes the phone to drive (0.5 km per shake) or uses auto drive.
5. On site, the engineer taps **Start repair** once the parts are there and **Mark repaired** when done (about 20 s in the demo), then **Leave site**. Dispatch never starts, stops or changes a machine, and nothing is sent without the manager: the model only alerts.

## Local

```bash
npm install
npm run dev     # console + API on http://localhost:3300 with an in-memory store
npm test
npm run typecheck
```

Open `http://localhost:3300/`. The console uses the same-origin API on `*.vercel.app` and on port 3300; opened anywhere else it talks to production unless given `?api=<url>`.

## Environment

`KV_REST_API_URL` and `KV_REST_API_TOKEN` (or the `UPSTASH_REDIS_REST_*` pair) come from the Upstash integration. Without them the deployed API returns 503. `ALLOWED_ORIGINS` (comma-separated) adds cross-origin console hosts beyond localhost.

## Known gaps

- No login. Anyone with the URL can act as the manager or the engineer. Fine for a judged demo, not for real use.
- The console's HSE HOLD state lives in each browser, so the server cannot enforce it. Requests at held sites go through and carry the open sev-5 actions to the engineer's phone.
