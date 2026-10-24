# Dispatch API and console hosting (Vercel)

Vercel project `casequest-2026` (root directory `web/`). Production: <https://casequest-2026.vercel.app>.

- `/` serves `prototype/lone-mesa-gate-console.html` (copied at build by `scripts/build.mjs`).
- `GET /api/state` returns the shared dispatch state as of now.
- `POST /api/action` applies one manager or engineer action (`lib/actions.ts` lists them).
- State is one JSON document in Upstash Redis, written with compare-and-set so concurrent writers retry instead of overwriting each other.
- `lib/dispatch.ts` is the whole model. It is pure and is also imported by the phone app, so both compute the same timings.

Vercel Functions have no WebSockets, so the console polls every 2 s and the phone every 1 s while open.

## Flow

1. Manager orders parts for an asset. Lead time depends on the site's spare fill (demo seconds).
2. Manager requests an engineer, timed to the parts. Dispatch sets the departure so the engineer arrives as the parts land.
3. The phone buzzes with the job, then again when it is time to leave. The engineer shakes the phone to drive (0.5 km per shake) or uses auto drive.
4. The repair starts by itself once the engineer and the parts are both on site, takes 20 s, then the engineer leaves for the base.

## Local

```bash
npm install
npm run dev     # console + API on http://localhost:3300 with an in-memory store
npm test
npm run typecheck
```

Open `http://localhost:3300/?api=http://localhost:3300`. Without `?api=`, a console opened anywhere other than `*.vercel.app` talks to production.

## Environment

`KV_REST_API_URL` and `KV_REST_API_TOKEN` (or the `UPSTASH_REDIS_REST_*` pair) come from the Upstash integration. Without them the deployed API returns 503. `ALLOWED_ORIGINS` (comma-separated) adds cross-origin console hosts beyond localhost.

## Known gaps

- No login. Anyone with the URL can act as the manager or the engineer. Fine for a judged demo, not for real use.
- The console's HSE HOLD state lives in each browser, so the server cannot enforce it. Requests at held sites go through and carry the open sev-5 actions to the engineer's phone.
