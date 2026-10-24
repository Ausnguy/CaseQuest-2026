import { describe, expect, it } from 'vitest';

import { actionSchema } from './actions.js';
import {
  AUTO_KM_PER_S, PHONE_ENGINEER, RESTOCK_S, SITES, SKUS, WORK_S, apply, dist, initialState, materialize, sku,
  type Action, type DispatchState,
} from './dispatch.js';

const T0 = 1_000_000;

function run(state: DispatchState, a: Action, now: number) {
  const r = apply(materialize(state, now), a, now);
  if (!r.ok) throw new Error(r.error);
  return r.state;
}

const cedar = SITES[0];
const LIFT_BEARING = sku('Bearing kit', 'Lift pump');
const LIFT_SEAL = sku('Mechanical seal kit', 'Lift pump');
const TP_BEARING = sku('Bearing kit', 'Transfer pump');
const TP_SEAL = sku('Mechanical seal kit', 'Transfer pump');
const COMP_BEARING = sku('Bearing kit', 'Compressor');

// A001 is Cedar's transfer pump, A002 its lift pump, A006 Mesa's compressor.
const request = (asset: string, kits: string[], engineerId = PHONE_ENGINEER): Action =>
  ({ type: 'requestEngineer', asset, engineerId, note: '', hseHold: null, kits });

describe('warehouse', () => {
  it('refuses to assign an engineer until every kit is in stock', () => {
    const s = initialState();
    expect(s.stock[COMP_BEARING]).toBe(0);
    const r = apply(s, request('A006', [COMP_BEARING, sku('Mechanical seal kit', 'Compressor')]), T0);
    expect(r).toMatchObject({ ok: false, error: expect.stringMatching(/Not in the warehouse: Bearing kit · Compressor/) });
  });

  it('takes the kits off the shelf when the engineer is assigned', () => {
    const s = run(initialState(), request('A002', [LIFT_BEARING, LIFT_SEAL]), T0);
    expect(s.stock[LIFT_BEARING]).toBe(0);
    expect(s.stock[LIFT_SEAL]).toBe(0);
    expect(s.jobs[0]).toMatchObject({ carry: [LIFT_BEARING, LIFT_SEAL], used: null, leaveAt: T0 });
    expect(s.moves.filter((m) => m.qty === -1)).toHaveLength(2);
  });

  it('refuses kits that do not fit the machine', () => {
    const r = apply(initialState(), request('A002', [TP_BEARING]), T0);
    expect(r).toMatchObject({ ok: false, error: expect.stringMatching(/does not fit a lift pump/) });
  });

  it('adds a restock to the shelf only when the supplier delivers', () => {
    let s = run(initialState(), { type: 'restock', sku: COMP_BEARING, qty: 3 }, T0);
    expect(apply(s, { type: 'restock', sku: COMP_BEARING, qty: 1 }, T0 + 1000).ok).toBe(false);
    const due = T0 + RESTOCK_S * 1000;
    expect(materialize(s, due - 1).stock[COMP_BEARING]).toBe(0);
    s = materialize(s, due + 5000);
    expect(s.stock[COMP_BEARING]).toBe(3);
    expect(s.moves.at(-1)).toMatchObject({ t: due, qty: 3 });
    // Materializing again must not deliver twice.
    expect(materialize(s, due + 9000).stock[COMP_BEARING]).toBe(3);
  });

  it('returns kits to the shelf when a job is cancelled', () => {
    const s = run(run(initialState(), request('A002', [LIFT_BEARING]), T0), { type: 'cancelJob', jobId: 'J-001' }, T0 + 1000);
    expect(s.stock[LIFT_BEARING]).toBe(1);
  });
});

describe('engineer on the phone', () => {
  function onRoad(kits: string[] = []) {
    let s = run(initialState(), { ...request('A001', kits), note: 'Check bearing' } as Action, T0);
    s = run(s, { type: 'depart', jobId: s.jobs[0].id, engineerId: PHONE_ENGINEER }, T0);
    return s;
  }
  const arrive = (s: DispatchState) => {
    // Cedar is about 11.3 km from the base.
    for (let i = 0; i < 2; i++) s = run(s, { type: 'travel', engineerId: PHONE_ENGINEER, km: 6 }, T0 + i * 1000);
    return s;
  };

  it('moves only when shaken', () => {
    let s = onRoad();
    expect(materialize(s, T0 + 60_000).jobs[0].status).toBe('en-route');
    s = run(s, { type: 'travel', engineerId: PHONE_ENGINEER, km: 5 }, T0 + 1000);
    expect(s.jobs[0].leg?.doneKm).toBe(5);
    expect(s.engineers[0].at).toBeNull();
  });

  it('never starts or finishes the repair by itself', () => {
    const s = arrive(onRoad());
    expect(s.jobs[0].status).toBe('on-site');
    expect(materialize(s, T0 + 600_000).jobs[0].status).toBe('on-site');
    const working = run(s, { type: 'startWork', jobId: 'J-001', engineerId: PHONE_ENGINEER }, T0 + 3000);
    expect(materialize(working, T0 + WORK_S * 50_000).jobs[0].status).toBe('working');
  });

  it('fits only the kits the engineer reports and returns the rest at the base', () => {
    let s = arrive(onRoad([TP_BEARING, TP_SEAL]));
    expect(s.stock[TP_BEARING]).toBe(1);
    s = run(s, { type: 'startWork', jobId: 'J-001', engineerId: PHONE_ENGINEER }, T0 + 2000);
    const finish = { type: 'finishWork', jobId: 'J-001', engineerId: PHONE_ENGINEER } as const;
    expect(apply(s, { ...finish, used: [LIFT_SEAL] }, T0 + 3000)).toMatchObject({ ok: false, error: expect.stringMatching(/not taken/) });
    s = run(s, { ...finish, used: [TP_BEARING] }, T0 + 3000);
    expect(s.jobs[0].used).toEqual([TP_BEARING]);
    expect(s.stock[TP_SEAL]).toBe(1);
    s = run(s, { type: 'leave', jobId: 'J-001', engineerId: PHONE_ENGINEER }, T0 + 4000);
    s = run(s, { type: 'autoTravel', engineerId: PHONE_ENGINEER, on: true }, T0 + 4000);
    const back = materialize(s, T0 + 4000 + (dist(cedar.pos, [0, 0]) / AUTO_KM_PER_S) * 1000 + 1000);
    expect(back.jobs[0].status).toBe('closed');
    expect(back.engineers[0]).toMatchObject({ at: 'BASE', jobId: null, pos: [0, 0] });
    expect(back.stock[TP_SEAL]).toBe(2);
    expect(back.stock[TP_BEARING]).toBe(1);
  });

  it('lets a repair need no parts at all', () => {
    let s = arrive(onRoad([TP_BEARING]));
    s = run(s, { type: 'startWork', jobId: 'J-001', engineerId: PHONE_ENGINEER }, T0 + 2000);
    s = run(s, { type: 'finishWork', jobId: 'J-001', engineerId: PHONE_ENGINEER, used: [] }, T0 + 3000);
    expect(s.log.at(-1)?.text).toMatch(/no parts needed/);
  });

  it('cannot leave before the repair is marked done', () => {
    const s = arrive(onRoad());
    expect(() => run(s, { type: 'leave', jobId: 'J-001', engineerId: PHONE_ENGINEER }, T0 + 2000)).toThrow(/not finished/);
  });

  it('does not double count distance when shaking during auto travel', () => {
    let s = onRoad();
    s = run(s, { type: 'autoTravel', engineerId: PHONE_ENGINEER, on: true }, T0);
    s = run(s, { type: 'travel', engineerId: PHONE_ENGINEER, km: 1 }, T0 + 4000);
    expect(s.jobs[0].leg?.doneKm).toBeCloseTo(4000 / 1000 * AUTO_KM_PER_S + 1, 6);
    expect(s.jobs[0].leg?.autoSince).toBe(T0 + 4000);
  });
});

describe('stand-in engineers', () => {
  it('drive out, fit the most likely kit, and bring the rest back', () => {
    const s = run(initialState(), request('A001', [TP_BEARING, TP_SEAL], 'ENG-2'), T0);
    const later = materialize(s, T0 + 200_000);
    expect(later.jobs[0]).toMatchObject({ status: 'closed', used: [TP_BEARING] });
    expect(later.engineers[1].at).toBe('BASE');
    expect(later.stock[TP_BEARING]).toBe(1);
    expect(later.stock[TP_SEAL]).toBe(2);
  });
});

describe('rules', () => {
  const base = () => run(initialState(), request('A001', []), T0);

  it('refuses a second job for a busy engineer or a busy asset', () => {
    const s = base();
    expect(apply(s, request('A002', []), T0).ok).toBe(false);
    expect(apply(s, request('A001', [], 'ENG-3'), T0).ok).toBe(false);
  });

  it('only lets the assigned engineer move the job', () => {
    expect(apply(base(), { type: 'depart', jobId: 'J-001', engineerId: 'ENG-3' }, T0).ok).toBe(false);
  });

  it('starts documents saved before the warehouse existed from a clean state', () => {
    const old = { v: 7, seq: 3, engineers: initialState().engineers, parts: [], jobs: [], log: [] } as unknown as DispatchState;
    const s = materialize(old, T0);
    expect(s.v).toBe(7);
    expect(Object.keys(s.stock)).toEqual(SKUS);
  });

  it('never mutates its input', () => {
    const s = base();
    const copy = JSON.stringify(s);
    apply(s, { type: 'depart', jobId: 'J-001', engineerId: PHONE_ENGINEER }, T0);
    materialize(s, T0 + 999_999);
    expect(JSON.stringify(s)).toBe(copy);
  });
});

describe('action schema', () => {
  it('rejects oversized travel, unknown kits and unknown actions', () => {
    expect(actionSchema.safeParse({ type: 'travel', engineerId: 'ENG-1', km: 50 }).success).toBe(false);
    expect(actionSchema.safeParse({ type: 'dropTables' }).success).toBe(false);
    expect(actionSchema.safeParse({ type: 'restock', sku: 'Gold kit', qty: 1 }).success).toBe(false);
    expect(actionSchema.safeParse({ type: 'restock', sku: LIFT_SEAL, qty: 11 }).success).toBe(false);
    expect(actionSchema.safeParse({ type: 'restock', sku: LIFT_SEAL, qty: 2 }).success).toBe(true);
    expect(actionSchema.safeParse({ type: 'finishWork', jobId: 'J-001', engineerId: 'ENG-1' }).success).toBe(false);
  });
});
