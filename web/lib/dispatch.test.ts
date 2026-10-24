import { describe, expect, it } from 'vitest';

import { actionSchema } from './actions.js';
import {
  AUTO_KM_PER_S, DEMO_S_PER_HOUR, PHONE_ENGINEER, SITES, WORK_S, apply, dist, initialState, leadTimeS, materialize,
  type Action, type DispatchState,
} from './dispatch.js';

const T0 = 1_000_000;

function run(state: DispatchState, a: Action, now: number) {
  const r = apply(materialize(state, now), a, now);
  if (!r.ok) throw new Error(r.error);
  return r.state;
}

const cedar = SITES[0];

describe('parts first, engineer timed to the parts', () => {
  it('schedules the engineer to leave so they arrive when the parts do', () => {
    let s = run(initialState(), { type: 'orderParts', asset: 'A001', kit: 'Bearing kit' }, T0);
    const parts = s.parts[0];
    expect(parts.arriveAt).toBe(T0 + leadTimeS('S01') * 1000);

    s = run(s, { type: 'requestEngineer', asset: 'A001', engineerId: PHONE_ENGINEER, partsId: parts.id, timing: 'with-parts', note: '', hseHold: null }, T0);
    const job = s.jobs[0];
    const travelMs = (dist([0, 0], cedar.pos) / AUTO_KM_PER_S) * 1000;
    expect(job.leaveAt).toBeCloseTo(parts.arriveAt - travelMs, 0);
    expect(job.status).toBe('scheduled');
  });

  it('dispatches at once when the parts are already late', () => {
    let s = run(initialState(), { type: 'orderParts', asset: 'A002', kit: 'Seal kit' }, T0);
    s = run(s, { type: 'requestEngineer', asset: 'A002', engineerId: PHONE_ENGINEER, partsId: s.parts[0].id, timing: 'with-parts', note: '', hseHold: null }, T0 + 40_000);
    expect(s.jobs[0].leaveAt).toBe(T0 + 40_000);
  });

  it('never starts the repair itself; the engineer can only start once the parts are on site', () => {
    let s = run(initialState(), { type: 'orderParts', asset: 'A001', kit: 'Bearing kit' }, T0);
    s = run(s, { type: 'requestEngineer', asset: 'A001', engineerId: PHONE_ENGINEER, partsId: s.parts[0].id, timing: 'now', note: '', hseHold: null }, T0);
    s = run(s, { type: 'depart', jobId: s.jobs[0].id, engineerId: PHONE_ENGINEER }, T0);
    s = run(s, { type: 'autoTravel', engineerId: PHONE_ENGINEER, on: true }, T0);
    const arrive = T0 + (dist([0, 0], cedar.pos) / AUTO_KM_PER_S) * 1000;
    const atSite = materialize(s, arrive + 1000);
    expect(atSite.jobs[0].status).toBe('on-site');
    expect(atSite.engineers[0].at).toBe('S01');

    const partsIn = s.parts[0].arriveAt;
    expect(materialize(s, partsIn + 60_000).jobs[0].status).toBe('on-site');
    const start = { type: 'startWork', jobId: s.jobs[0].id, engineerId: PHONE_ENGINEER } as const;
    expect(apply(materialize(s, partsIn - 1), start, partsIn - 1)).toMatchObject({ ok: false, error: expect.stringMatching(/not arrived/) });
    s = run(s, start, partsIn + 1);
    expect(s.jobs[0]).toMatchObject({ status: 'working', workStartAt: partsIn + 1 });
    expect(materialize(s, partsIn + WORK_S * 10_000).jobs[0].status).toBe('working');
    s = run(s, { type: 'finishWork', jobId: s.jobs[0].id, engineerId: PHONE_ENGINEER }, partsIn + WORK_S * 1000);
    expect(s.jobs[0].status).toBe('done');
  });
});

describe('requests from the failure model', () => {
  it('uses each site\'s observed parts lead time', () => {
    for (const s of SITES) expect(leadTimeS(s.id)).toBe(Math.round(s.partsLeadH * DEMO_S_PER_HOUR));
    expect(leadTimeS('S06')).toBeLessThan(leadTimeS('S03'));
  });

  it('carries kits, tools and the predicted chance to the engineer', () => {
    let s = run(initialState(), { type: 'orderParts', asset: 'A011', kit: 'Mechanical seal kit' }, T0);
    s = run(s, {
      type: 'requestEngineer', asset: 'A011', engineerId: PHONE_ENGINEER, partsId: s.parts[0].id, timing: 'with-parts', note: 'Predicted failure',
      hseHold: null, kits: ['Bearing kit', 'Mechanical seal kit'], tools: ['Lockout/tagout kit'], chance: 0.67,
    }, T0);
    expect(s.jobs[0]).toMatchObject({ kits: ['Bearing kit', 'Mechanical seal kit'], tools: ['Lockout/tagout kit'], chance: 0.67 });
  });

  it('rejects a chance outside 0 to 1 and oversized tool lists', () => {
    const base = { type: 'requestEngineer', asset: 'A011', engineerId: PHONE_ENGINEER, partsId: null, timing: 'now', note: '', hseHold: null };
    expect(actionSchema.safeParse({ ...base, chance: 1.5 }).success).toBe(false);
    expect(actionSchema.safeParse({ ...base, tools: Array(13).fill('x') }).success).toBe(false);
    expect(actionSchema.safeParse({ ...base, chance: 0.67, kits: ['Bearing kit'] }).success).toBe(true);
  });
});

describe('engineer on the phone', () => {
  function onRoad() {
    let s = run(initialState(), { type: 'requestEngineer', asset: 'A001', engineerId: PHONE_ENGINEER, partsId: null, timing: 'now', note: 'Check bearing', hseHold: null }, T0);
    s = run(s, { type: 'depart', jobId: s.jobs[0].id, engineerId: PHONE_ENGINEER }, T0);
    return s;
  }

  it('moves only when shaken', () => {
    let s = onRoad();
    expect(materialize(s, T0 + 60_000).jobs[0].status).toBe('en-route');
    s = run(s, { type: 'travel', engineerId: PHONE_ENGINEER, km: 5 }, T0 + 1000);
    expect(s.jobs[0].leg?.doneKm).toBe(5);
    expect(s.engineers[0].at).toBeNull();
  });

  it('arrives, works, then leaves for the base when told to', () => {
    let s = onRoad();
    // Cedar is about 11.3 km from the base.
    for (let i = 0; i < 2; i++) s = run(s, { type: 'travel', engineerId: PHONE_ENGINEER, km: 6 }, T0 + i * 1000);
    expect(s.jobs[0].status).toBe('on-site');
    expect(apply(s, { type: 'travel', engineerId: PHONE_ENGINEER, km: 1 }, T0 + 2000).ok).toBe(false);
    expect(() => run(s, { type: 'leave', jobId: s.jobs[0].id, engineerId: PHONE_ENGINEER }, T0 + 2000)).toThrow(/not finished/);
    s = run(s, { type: 'startWork', jobId: s.jobs[0].id, engineerId: PHONE_ENGINEER }, T0 + 2000);
    const done = T0 + 2000 + WORK_S * 1000;
    s = run(s, { type: 'finishWork', jobId: s.jobs[0].id, engineerId: PHONE_ENGINEER }, done);
    s = run(s, { type: 'leave', jobId: s.jobs[0].id, engineerId: PHONE_ENGINEER }, done);
    s = run(s, { type: 'autoTravel', engineerId: PHONE_ENGINEER, on: true }, done);
    const back = materialize(s, done + 60_000);
    expect(back.jobs[0].status).toBe('closed');
    expect(back.engineers[0]).toMatchObject({ at: 'BASE', jobId: null, pos: [0, 0] });
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
  it('set off on time and come back on their own', () => {
    let s = run(initialState(), { type: 'requestEngineer', asset: 'A013', engineerId: 'ENG-2', partsId: null, timing: 'now', note: '', hseHold: null }, T0);
    // ENG-2 already stands at Canyon (S05), where A013 is.
    expect(s.jobs[0].status).toBe('working');
    const later = materialize(s, T0 + WORK_S * 1000 + 60_000);
    expect(later.jobs[0].status).toBe('closed');
    expect(later.engineers[1].at).toBe('BASE');
  });
});

describe('rules', () => {
  const base = () => run(initialState(), { type: 'requestEngineer', asset: 'A001', engineerId: PHONE_ENGINEER, partsId: null, timing: 'now', note: '', hseHold: null }, T0);

  it('refuses a second job for a busy engineer or a busy asset', () => {
    const s = base();
    expect(apply(s, { type: 'requestEngineer', asset: 'A002', engineerId: PHONE_ENGINEER, partsId: null, timing: 'now', note: '', hseHold: null }, T0).ok).toBe(false);
    expect(apply(s, { type: 'requestEngineer', asset: 'A001', engineerId: 'ENG-3', partsId: null, timing: 'now', note: '', hseHold: null }, T0).ok).toBe(false);
  });

  it('refuses parts that belong to another asset', () => {
    const s = run(initialState(), { type: 'orderParts', asset: 'A004', kit: 'Seal kit' }, T0);
    const r = apply(s, { type: 'requestEngineer', asset: 'A001', engineerId: PHONE_ENGINEER, partsId: s.parts[0].id, timing: 'with-parts', note: '', hseHold: null }, T0);
    expect(r).toEqual({ ok: false, error: 'That parts order is not for this asset.' });
  });

  it('refuses a duplicate order while parts are in transit', () => {
    const s = run(initialState(), { type: 'orderParts', asset: 'A001', kit: 'Seal kit' }, T0);
    expect(apply(s, { type: 'orderParts', asset: 'A001', kit: 'Seal kit' }, T0 + 1000).ok).toBe(false);
  });

  it('frees the engineer when a job is cancelled', () => {
    const s = run(base(), { type: 'cancelJob', jobId: 'J-001' }, T0 + 1000);
    expect(s.engineers[0].jobId).toBeNull();
    expect(s.jobs[0].status).toBe('cancelled');
  });

  it('only lets the assigned engineer move the job', () => {
    expect(apply(base(), { type: 'depart', jobId: 'J-001', engineerId: 'ENG-3' }, T0).ok).toBe(false);
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
  it('rejects oversized travel and unknown actions', () => {
    expect(actionSchema.safeParse({ type: 'travel', engineerId: 'ENG-1', km: 50 }).success).toBe(false);
    expect(actionSchema.safeParse({ type: 'dropTables' }).success).toBe(false);
    expect(actionSchema.safeParse({ type: 'orderParts', asset: 'A001', kit: 'Bearing kit' }).success).toBe(true);
  });
});
