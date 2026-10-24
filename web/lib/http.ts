import { AUTO_KM_PER_S, SHAKE_KM, WORK_S, materialize, type DispatchState } from './dispatch.js';

// The console on Vercel is same-origin. Cross-origin is only for the console served from a laptop.
// The phone app is native and sends no Origin header.
function allowedOrigin(origin: string | null) {
  if (!origin) return null;
  if (/^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(origin)) return origin;
  const extra = (process.env.ALLOWED_ORIGINS ?? '').split(',').map((s) => s.trim()).filter(Boolean);
  return extra.includes(origin) ? origin : null;
}

export function json(req: Request, status: number, body: unknown) {
  const headers: Record<string, string> = {
    'content-type': 'application/json',
    'cache-control': 'no-store',
    'x-content-type-options': 'nosniff',
  };
  const origin = allowedOrigin(req.headers.get('origin'));
  if (origin) {
    headers['access-control-allow-origin'] = origin;
    headers['access-control-allow-methods'] = 'GET, POST, OPTIONS';
    headers['access-control-allow-headers'] = 'content-type';
    headers['vary'] = 'origin';
  }
  return new Response(status === 204 ? null : JSON.stringify(body), { status, headers });
}

export const preflight = (req: Request) => json(req, 204, null);

// What clients receive: the state as of `now`, plus `now` so they can correct for their own clock.
export function view(state: DispatchState, now: number) {
  return { now, config: { autoKmPerS: AUTO_KM_PER_S, shakeKm: SHAKE_KM, workS: WORK_S }, state: materialize(state, now) };
}
