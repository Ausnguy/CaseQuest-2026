import { describe, expect, it } from 'vitest';

import { POST } from '../api/action.js';
import { GET, OPTIONS } from '../api/state.js';

const post = (body: string, origin?: string) =>
  POST(new Request('http://x/api/action', { method: 'POST', body, headers: origin ? { origin } : {} }));

describe('dispatch API (in-memory store)', () => {
  it('orders parts and returns the new state', async () => {
    const res = await post(JSON.stringify({ type: 'orderParts', asset: 'A007', kit: 'Bearing kit' }));
    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body.state.parts.at(-1)).toMatchObject({ asset: 'A007', site: 'S03' });
    const state = await (await GET(new Request('http://x/api/state'))).json();
    expect(state.state.parts.some((p: { asset: string }) => p.asset === 'A007')).toBe(true);
  });

  it('rejects bad JSON, unknown actions, oversized bodies and rule breaks', async () => {
    expect((await post('{nope')).status).toBe(400);
    expect((await post(JSON.stringify({ type: 'nuke' }))).status).toBe(400);
    expect((await post('x'.repeat(5000))).status).toBe(413);
    const dup = await post(JSON.stringify({ type: 'orderParts', asset: 'A007', kit: 'Bearing kit' }));
    expect(dup.status).toBe(409);
    expect((await dup.json()).error).toMatch(/already on the way/);
  });

  it('allows the console from localhost only', async () => {
    const ok = await OPTIONS(new Request('http://x/api/state', { headers: { origin: 'http://localhost:8000' } }));
    expect(ok.status).toBe(204);
    expect(ok.headers.get('access-control-allow-origin')).toBe('http://localhost:8000');
    const bad = await post(JSON.stringify({ type: 'reset' }), 'https://evil.example');
    expect(bad.headers.get('access-control-allow-origin')).toBeNull();
  });
});
