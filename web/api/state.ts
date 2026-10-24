import { json, preflight, view } from '../lib/http.js';
import { getStore } from '../lib/store.js';

export async function GET(req: Request) {
  const store = getStore();
  if (!store) return json(req, 503, { error: 'Dispatch storage is not configured.' });
  try {
    const state = await store.load();
    return json(req, 200, view(state, Date.now()));
  } catch (err) {
    console.error('state load failed', err);
    return json(req, 503, { error: 'Dispatch storage is unavailable. Try again shortly.' });
  }
}

export const OPTIONS = preflight;
