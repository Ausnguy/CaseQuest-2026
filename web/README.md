# Dispatch API and console hosting (Vercel)

Vercel project `casequest-2026` (root directory `web/`). Production: <https://casequest-2026.vercel.app>.

- `/` serves `prototype/parvius.html`, with `prototype/fieldwork.js` beside it and the failure model's `data/model/predictions.json` as `/model.json` (copied at build by `scripts/build.mjs`).
- `GET /api/state` returns the shared dispatch state as of now.
- `POST /api/action` applies one manager or engineer action (`lib/actions.ts` lists them).
- State is one JSON document in Upstash Redis, written with compare-and-set so concurrent writers retry instead of overwriting each other.
- `lib/dispatch.ts` is the whole model. It is pure and is also imported by the phone app, so both compute the same timings.

Vercel Functions have no WebSockets, so the console polls every 2 s and the phone every 1 s while open.

## Flow

1. The failure model flags a machine for the replay day: likely cause, chance of failure within 3 days, the readings behind it, and the kits each cause needs.
2. The warehouse (`stock` in the state) holds every kit, one line per kit and machine type. The manager tracks it on the **Inventory** page and restocks from the supplier; a delivery lands after the sites' median 2025 parts wait (18 h, played at 3 s per hour).
3. The manager clicks **Send engineer**. The server refuses unless every kit for the job is on the shelf. Assigning takes the kits off the shelf and the engineer leaves the base with them.
4. The phone buzzes with the job. The engineer shakes the phone to drive (0.5 km per shake) or uses auto drive.
5. On site, the engineer taps **Start repair**, ticks the kits actually fitted (a repair does not always replace a part) and taps **Mark repaired**, then **Leave site**. Kits not fitted go back on the shelf when they reach the base.

Dispatch never starts, stops or changes a machine, and nothing is sent without the manager: the model only alerts. Every shelf change is recorded in `moves`.

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
- Starting stock is modeled: the workbook has no item-level inventory.
- The console's HSE HOLD state lives in each browser, so the server cannot enforce it. Requests at held sites go through and carry the open sev-5 actions to the engineer's phone.
