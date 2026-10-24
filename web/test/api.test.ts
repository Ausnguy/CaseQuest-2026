import { describe, expect, it } from 'vitest';

import { POST } from '../api/action.js';
import { GET, OPTIONS } from '../api/state.js';

const post = (body: string, origin?: string) =>
  POST(new Request('http://x/api/action', { method: 'POST', body, headers: origin ? { origin } : {} }));

describe('dispatch API (in-memory store)', () => {
  it('orders a restock and returns the new state', async () => {
    const res = await post(JSON.stringify({ type: 'restock', sku: 'Bearing kit · Compressor', qty: 2 }));
    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body.state.restocks.at(-1)).toMatchObject({ sku: 'Bearing kit · Compressor', qty: 2, received: false });
    const state = await (await GET(new Request('http://x/api/state'))).json();
    expect(state.config.skus).toContain('Bearing kit · Compressor');
    expect(state.state.stock['Bearing kit · Compressor']).toBe(0);
  });

  it('rejects bad JSON, unknown actions, oversized bodies and rule breaks', async () => {
    expect((await post('{nope')).status).toBe(400);
    expect((await post(JSON.stringify({ type: 'nuke' }))).status).toBe(400);
    expect((await post('x'.repeat(5000))).status).toBe(413);
    const dup = await post(JSON.stringify({ type: 'restock', sku: 'Bearing kit · Compressor', qty: 1 }));
    expect(dup.status).toBe(409);
    expect((await dup.json()).error).toMatch(/already on order/);
    const short = await post(JSON.stringify({ type: 'requestEngineer', asset: 'A006', engineerId: 'ENG-1', note: '', hseHold: null, kits: ['Bearing kit · Compressor'] }));
    expect(short.status).toBe(409);
    expect((await short.json()).error).toMatch(/Not in the warehouse/);
  });

  it('allows the console from localhost only', async () => {
    const ok = await OPTIONS(new Request('http://x/api/state', { headers: { origin: 'http://localhost:8000' } }));
    expect(ok.status).toBe(204);
    expect(ok.headers.get('access-control-allow-origin')).toBe('http://localhost:8000');
    const bad = await post(JSON.stringify({ type: 'reset' }), 'https://evil.example');
    expect(bad.headers.get('access-control-allow-origin')).toBeNull();
  });
});
