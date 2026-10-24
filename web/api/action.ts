import { actionSchema } from '../lib/actions.js';
import { apply, materialize } from '../lib/dispatch.js';
import { json, preflight, view } from '../lib/http.js';
import { getStore } from '../lib/store.js';

const MAX_BODY = 4096;
const ATTEMPTS = 5;

export async function POST(req: Request) {
  const store = getStore();
  if (!store) return json(req, 503, { error: 'Dispatch storage is not configured.' });

  const raw = await req.text();
  if (raw.length > MAX_BODY) return json(req, 413, { error: 'Request too large.' });
  let body: unknown;
  try {
    body = JSON.parse(raw);
  } catch {
    return json(req, 400, { error: 'Body must be JSON.' });
  }
  const parsed = actionSchema.safeParse(body);
  if (!parsed.success) return json(req, 400, { error: 'Invalid action.', issues: parsed.error.issues.slice(0, 3) });

  try {
    for (let i = 0; i < ATTEMPTS; i++) {
      const stored = await store.load();
      const now = Date.now();
      const result = apply(materialize(stored, now), parsed.data, now);
      if (!result.ok) return json(req, 409, { error: result.error, ...view(stored, now) });
      if (await store.save(result.state, stored.v)) return json(req, 200, view({ ...result.state, v: stored.v + 1 }, now));
    }
    return json(req, 503, { error: 'Too many people changed this at once. Try again.' });
  } catch (err) {
    console.error('action failed', parsed.data.type, err);
    return json(req, 503, { error: 'Dispatch storage is unavailable. Try again shortly.' });
  }
}

export const OPTIONS = preflight;
