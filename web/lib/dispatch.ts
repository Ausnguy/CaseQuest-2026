// Shared dispatch model for the manager console (web) and the engineer phone (mobile).
// Pure: every function takes the current time instead of reading a clock, so the server,
// the phone and the tests all compute the same state from the same stored document.

export type Vec = [number, number];

export interface Site { id: string; name: string; pos: Vec; spare: number; partsLeadH: number }
export interface Asset { id: string; site: string; type: string }

// Same layout as the console's 3D map (two rows of three), read as kilometres. `partsLeadH` is the
// observed median hours a 2025 repair waited when parts were not on hand (casequest.maintenance.site_times).
export const SITES: Site[] = [
  { id: 'S01', name: 'Cedar', pos: [-9.5, -6.2], spare: 86, partsLeadH: 20.0 },
  { id: 'S02', name: 'Mesa', pos: [0, -6.2], spare: 65, partsLeadH: 14.8 },
  { id: 'S03', name: 'Juniper', pos: [9.5, -6.2], spare: 92, partsLeadH: 23.9 },
  { id: 'S04', name: 'Arroyo', pos: [-9.5, 6.2], spare: 42, partsLeadH: 16.5 },
  { id: 'S05', name: 'Canyon', pos: [0, 6.2], spare: 78, partsLeadH: 19.9 },
  { id: 'S06', name: 'Prairie', pos: [9.5, 6.2], spare: 70, partsLeadH: 13.3 },
];
export const BASE = { id: 'BASE', name: 'Maintenance base', pos: [0, 0] as Vec };

const TYPES = ['Transfer pump', 'Lift pump', 'Compressor'];
export const ASSETS: Asset[] = SITES.flatMap((s, i) =>
  TYPES.map((type, j) => ({ id: `A${String(i * 3 + j + 1).padStart(3, '0')}`, site: s.id, type })),
);

export const siteById = (id: string) => SITES.find((s) => s.id === id);
export const assetById = (id: string) => ASSETS.find((a) => a.id === id);

// Demo clock: the whole loop (order, travel, repair) plays out in a minute or two at a judging table.
export const AUTO_KM_PER_S = 0.5;
export const SHAKE_KM = 0.5;
export const WORK_S = 20;
// Demo clock for parts: each real hour of lead time plays as this many seconds.
export const DEMO_S_PER_HOUR = 3;
export const leadTimeS = (siteId: string) => Math.round((siteById(siteId)?.partsLeadH ?? 18) * DEMO_S_PER_HOUR);

export const PHONE_ENGINEER = 'ENG-1';

export interface Leg { from: Vec; to: Vec; km: number; doneKm: number; autoSince: number | null }

// Engineers without a phone are demo stand-ins: they set off and come back on their own.
export interface Engineer {
  id: string;
  name: string;
  phone: boolean;
  pos: Vec;
  // Site id or BASE when on site there, null when off site (home or on the road).
  at: string | null;
  jobId: string | null;
}

export interface PartsOrder { id: string; asset: string; site: string; kit: string; orderedAt: number; arriveAt: number }

export type JobStatus = 'scheduled' | 'en-route' | 'on-site' | 'working' | 'done' | 'leaving' | 'closed' | 'cancelled';

export interface Job {
  id: string;
  asset: string;
  site: string;
  note: string;
  partsId: string | null;
  engineerId: string;
  createdAt: number;
  // When the engineer should set off so they arrive as the parts do.
  leaveAt: number;
  status: JobStatus;
  leg: Leg | null;
  arrivedAt: number | null;
  workStartAt: number | null;
  doneAt: number | null;
  closedAt: number | null;
  // Open severity-5 HSE actions at the site when the manager made the request, shown to the engineer.
  hseHold: string | null;
  // From the failure model's plan when the request came from a prediction. Older stored jobs lack them.
  kits?: string[];
  tools?: string[];
  chance?: number | null;
}

export interface LogEntry { t: number; who: string; text: string }

export interface DispatchState {
  v: number;
  seq: number;
  engineers: Engineer[];
  parts: PartsOrder[];
  jobs: Job[];
  log: LogEntry[];
}

export const HOME: Vec = [15, 0];

export function initialState(): DispatchState {
  return {
    v: 0,
    seq: 0,
    engineers: [
      { id: PHONE_ENGINEER, name: 'R. Ortiz (phone)', phone: true, pos: [...BASE.pos], at: BASE.id, jobId: null },
      { id: 'ENG-2', name: 'D. Patel', phone: false, pos: [...SITES[4].pos], at: 'S05', jobId: null },
      { id: 'ENG-3', name: 'K. Moore', phone: false, pos: [...HOME], at: null, jobId: null },
    ],
    parts: [],
    jobs: [],
    log: [],
  };
}

export const dist = (a: Vec, b: Vec) => Math.hypot(a[0] - b[0], a[1] - b[1]);
export const travelS = (from: Vec, to: Vec) => dist(from, to) / AUTO_KM_PER_S;

export function legDoneKm(leg: Leg, now: number) {
  const auto = leg.autoSince === null ? 0 : (Math.max(0, now - leg.autoSince) / 1000) * AUTO_KM_PER_S;
  return Math.min(leg.km, leg.doneKm + auto);
}

export function legPos(leg: Leg, now: number): Vec {
  const f = leg.km === 0 ? 1 : legDoneKm(leg, now) / leg.km;
  return [leg.from[0] + (leg.to[0] - leg.from[0]) * f, leg.from[1] + (leg.to[1] - leg.from[1]) * f];
}

// When the leg finishes, given what is known now. Null if it depends on more shakes.
function legArrival(leg: Leg, now: number): number | null {
  if (legDoneKm(leg, now) < leg.km) return null;
  if (leg.autoSince === null) return now;
  return Math.max(leg.autoSince, leg.autoSince + ((leg.km - leg.doneKm) / AUTO_KM_PER_S) * 1000);
}

const makeLeg = (from: Vec, to: Vec, autoSince: number | null): Leg => ({ from: [...from], to: [...to], km: dist(from, to), doneKm: 0, autoSince });

export const isActive = (j: Job) => j.status !== 'closed' && j.status !== 'cancelled';
export const partsArrived = (p: PartsOrder, now: number) => now >= p.arriveAt;

function clone(s: DispatchState): DispatchState {
  return JSON.parse(JSON.stringify(s)) as DispatchState;
}

function addLog(s: DispatchState, t: number, who: string, text: string) {
  s.log.push({ t, who, text });
  if (s.log.length > 40) s.log.splice(0, s.log.length - 40);
}

// Applies every transition that time alone causes, up to `now`. Transitions use the moment they
// happened (arrival, parts delivery), not `now`, so a late poll gives the same answer as an early one.
export function materialize(input: DispatchState, now: number): DispatchState {
  const s = clone(input);
  for (const job of s.jobs) {
    const eng = s.engineers.find((e) => e.id === job.engineerId);
    if (!eng) continue;
    const parts = job.partsId ? s.parts.find((p) => p.id === job.partsId) : undefined;
    for (let guard = 0; guard < 6; guard++) {
      const before = job.status;
      if (job.status === 'scheduled' && !eng.phone && now >= job.leaveAt) {
        const site = siteById(job.site)!;
        job.leg = makeLeg(eng.pos, site.pos, job.leaveAt);
        job.status = 'en-route';
        eng.at = null;
      } else if ((job.status === 'en-route' || job.status === 'leaving') && job.leg) {
        const t = legArrival(job.leg, now);
        if (t !== null) {
          eng.pos = [...job.leg.to];
          if (job.status === 'en-route') {
            job.status = 'on-site';
            job.arrivedAt = t;
            eng.at = job.site;
            addLog(s, t, eng.name, `Arrived at ${siteById(job.site)?.name} for ${job.asset}`);
          } else {
            job.status = 'closed';
            job.closedAt = t;
            eng.at = BASE.id;
            eng.jobId = null;
          }
          job.leg = null;
        }
      // The phone engineer starts and finishes the repair themselves ('startWork', 'finishWork'); dispatch never
      // acts on a machine. Stand-in engineers are simulated people, so they follow the same steps on their own.
      } else if (job.status === 'on-site' && job.arrivedAt !== null && !eng.phone) {
        const start = Math.max(job.arrivedAt, parts ? parts.arriveAt : job.arrivedAt);
        if (now >= start) {
          job.status = 'working';
          job.workStartAt = start;
        }
      } else if (job.status === 'working' && job.workStartAt !== null && !eng.phone) {
        const end = job.workStartAt + WORK_S * 1000;
        if (now >= end) {
          job.status = 'done';
          job.doneAt = end;
          addLog(s, end, eng.name, `Repaired ${job.asset}`);
        }
      } else if (job.status === 'done' && !eng.phone && job.doneAt !== null) {
        job.leg = makeLeg(eng.pos, BASE.pos, job.doneAt);
        job.status = 'leaving';
        eng.at = null;
      }
      if (job.status === before) break;
    }
    if ((job.status === 'en-route' || job.status === 'leaving') && job.leg) eng.pos = legPos(job.leg, now);
  }
  return s;
}

export type Action =
  | { type: 'orderParts'; asset: string; kit: string }
  | { type: 'requestEngineer'; asset: string; engineerId: string; partsId: string | null; timing: 'with-parts' | 'now'; note: string; hseHold: string | null; kits?: string[]; tools?: string[]; chance?: number | null }
  | { type: 'cancelJob'; jobId: string }
  | { type: 'depart'; jobId: string; engineerId: string }
  | { type: 'travel'; engineerId: string; km: number }
  | { type: 'autoTravel'; engineerId: string; on: boolean }
  | { type: 'startWork'; jobId: string; engineerId: string }
  | { type: 'finishWork'; jobId: string; engineerId: string }
  | { type: 'leave'; jobId: string; engineerId: string }
  | { type: 'reset' };

export type Result = { ok: true; state: DispatchState } | { ok: false; error: string };

const fail = (error: string): Result => ({ ok: false, error });
const pad = (n: number) => String(n).padStart(3, '0');

// The latest suggested departure time that still has the engineer on site when the parts land.
export function plannedLeaveAt(eng: Engineer, siteId: string, parts: PartsOrder | undefined, timing: 'with-parts' | 'now', now: number) {
  const site = siteById(siteId);
  if (!site || !parts || timing === 'now') return now;
  return Math.max(now, parts.arriveAt - travelS(eng.pos, site.pos) * 1000);
}

// Expects a materialized state. Returns a new state; never mutates the input.
export function apply(input: DispatchState, a: Action, now: number): Result {
  if (a.type === 'reset') return { ok: true, state: { ...initialState(), v: input.v } };
  const s = clone(input);

  switch (a.type) {
    case 'orderParts': {
      const asset = assetById(a.asset);
      if (!asset) return fail('Unknown asset.');
      if (s.parts.some((p) => p.asset === a.asset && !partsArrived(p, now))) return fail(`Parts for ${a.asset} are already on the way.`);
      const id = `P-${pad(++s.seq)}`;
      s.parts.push({ id, asset: a.asset, site: asset.site, kit: a.kit, orderedAt: now, arriveAt: now + leadTimeS(asset.site) * 1000 });
      addLog(s, now, 'Manager', `Ordered ${a.kit} for ${a.asset} (${id})`);
      break;
    }
    case 'requestEngineer': {
      const asset = assetById(a.asset);
      if (!asset) return fail('Unknown asset.');
      const eng = s.engineers.find((e) => e.id === a.engineerId);
      if (!eng) return fail('Unknown engineer.');
      if (eng.jobId) return fail(`${eng.name} already has a job.`);
      if (s.jobs.some((j) => j.asset === a.asset && isActive(j))) return fail(`${a.asset} already has an engineer assigned.`);
      let parts: PartsOrder | undefined;
      if (a.partsId) {
        parts = s.parts.find((p) => p.id === a.partsId);
        if (!parts || parts.asset !== a.asset) return fail('That parts order is not for this asset.');
        if (s.jobs.some((j) => j.partsId === a.partsId && isActive(j))) return fail('Those parts are already assigned to a job.');
      }
      const id = `J-${pad(++s.seq)}`;
      const leaveAt = plannedLeaveAt(eng, asset.site, parts, a.timing, now);
      s.jobs.push({
        id, asset: a.asset, site: asset.site, note: a.note, partsId: parts?.id ?? null, engineerId: eng.id, createdAt: now,
        leaveAt, status: 'scheduled', leg: null, arrivedAt: null, workStartAt: null, doneAt: null, closedAt: null, hseHold: a.hseHold,
        kits: a.kits ?? [], tools: a.tools ?? [], chance: a.chance ?? null,
      });
      eng.jobId = id;
      addLog(s, now, 'Manager', `Requested ${eng.name} for ${a.asset} (${id})`);
      break;
    }
    case 'cancelJob': {
      const job = s.jobs.find((j) => j.id === a.jobId);
      if (!job || !isActive(job)) return fail('That job is not active.');
      const eng = s.engineers.find((e) => e.id === job.engineerId);
      if (eng) {
        if (job.leg) eng.pos = legPos(job.leg, now);
        if (job.status === 'en-route' || job.status === 'leaving') eng.at = null;
        eng.jobId = null;
      }
      job.status = 'cancelled';
      job.leg = null;
      job.closedAt = now;
      addLog(s, now, 'Manager', `Cancelled ${job.id}`);
      break;
    }
    case 'depart': {
      const job = s.jobs.find((j) => j.id === a.jobId);
      if (!job || job.engineerId !== a.engineerId) return fail('That job is not assigned to you.');
      if (job.status !== 'scheduled') return fail('You are already on this job.');
      const eng = s.engineers.find((e) => e.id === a.engineerId)!;
      job.leg = makeLeg(eng.pos, siteById(job.site)!.pos, null);
      job.status = 'en-route';
      eng.at = null;
      const early = job.leaveAt - now;
      addLog(s, now, eng.name, `Set off for ${job.asset}${early > 1000 ? `, ${Math.round(early / 1000)} s early` : ''}`);
      break;
    }
    case 'travel':
    case 'autoTravel': {
      const eng = s.engineers.find((e) => e.id === a.engineerId);
      const job = eng?.jobId ? s.jobs.find((j) => j.id === eng.jobId) : undefined;
      if (!eng || !job?.leg || (job.status !== 'en-route' && job.status !== 'leaving')) return fail('You are not travelling.');
      const leg = job.leg;
      leg.doneKm = legDoneKm(leg, now);
      if (leg.autoSince !== null) leg.autoSince = now;
      if (a.type === 'travel') leg.doneKm = Math.min(leg.km, leg.doneKm + a.km);
      else leg.autoSince = a.on ? now : null;
      break;
    }
    case 'startWork': {
      const job = s.jobs.find((j) => j.id === a.jobId);
      if (!job || job.engineerId !== a.engineerId) return fail('That job is not assigned to you.');
      if (job.status !== 'on-site') return fail('You are not on site for this job.');
      const parts = job.partsId ? s.parts.find((p) => p.id === job.partsId) : null;
      if (parts && now < parts.arriveAt) return fail('The parts have not arrived yet.');
      job.status = 'working';
      job.workStartAt = now;
      addLog(s, now, s.engineers.find((e) => e.id === a.engineerId)!.name, `Started repair on ${job.asset}`);
      break;
    }
    case 'finishWork': {
      const job = s.jobs.find((j) => j.id === a.jobId);
      if (!job || job.engineerId !== a.engineerId) return fail('That job is not assigned to you.');
      if (job.status !== 'working') return fail('The repair has not started.');
      job.status = 'done';
      job.doneAt = now;
      addLog(s, now, s.engineers.find((e) => e.id === a.engineerId)!.name, `Repaired ${job.asset}`);
      break;
    }
    case 'leave': {
      const job = s.jobs.find((j) => j.id === a.jobId);
      if (!job || job.engineerId !== a.engineerId) return fail('That job is not assigned to you.');
      if (job.status !== 'done') return fail('The repair is not finished.');
      const eng = s.engineers.find((e) => e.id === a.engineerId)!;
      job.leg = makeLeg(eng.pos, BASE.pos, null);
      job.status = 'leaving';
      eng.at = null;
      addLog(s, now, eng.name, `Left ${siteById(job.site)?.name}`);
      break;
    }
  }
  prune(s);
  // Arrivals of zero length (already standing at the site) happen in the same step.
  return { ok: true, state: materialize(s, now) };
}

// Keeps the stored document small: active work stays, history is trimmed.
function prune(s: DispatchState) {
  const done = s.jobs.filter((j) => !isActive(j));
  if (done.length > 20) {
    const drop = new Set(done.slice(0, done.length - 20).map((j) => j.id));
    s.jobs = s.jobs.filter((j) => !drop.has(j.id));
  }
  const used = new Set(s.jobs.map((j) => j.partsId));
  if (s.parts.length > 30) s.parts = s.parts.filter((p, i) => used.has(p.id) || i >= s.parts.length - 30);
}

// How far the engineer's arrival is from the parts' arrival for this job, in seconds.
// Positive: the engineer waits for parts. Negative: parts wait for the engineer.
export function arrivalGapS(job: Job, parts: PartsOrder | undefined) {
  if (!parts || job.arrivedAt === null) return null;
  return Math.round((parts.arriveAt - job.arrivedAt) / 1000);
}
