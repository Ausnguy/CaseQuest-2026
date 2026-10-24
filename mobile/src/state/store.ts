import * as Haptics from 'expo-haptics';
import { Accelerometer } from 'expo-sensors';
import { AppState, Vibration } from 'react-native';
import { create } from 'zustand';

import { PHONE_ENGINEER, SHAKE_KM, isActive, siteById, type Action, type DispatchState, type Job } from '@dispatch/dispatch';

// Production by default so the phone works anywhere. For a laptop API over USB:
// EXPO_PUBLIC_API_URL=http://127.0.0.1:3300 plus `adb reverse tcp:3300 tcp:3300`.
const API = (process.env.EXPO_PUBLIC_API_URL ?? 'https://casequest-2026.vercel.app').replace(/\/$/, '') + '/api';
const TIMEOUT_MS = 5000;
const POLL_MS = 1000;
const FLUSH_MS = 700;
// Acceleration beyond gravity, in g, that counts as a shake, and the shortest gap between two.
const SHAKE_G = 0.7;
const SHAKE_GAP_MS = 220;

export const ME = PHONE_ENGINEER;

export type Link = 'connecting' | 'live' | 'offline';
export interface Banner { key: string; title: string; body: string; tone: 'job' | 'go' | 'error' }
export interface Shake { status: 'listening' | 'unavailable'; count: number }

interface Store {
  state: DispatchState | null;
  // Server clock minus phone clock, so countdowns match the manager's screen.
  offset: number;
  link: Link;
  error: string | null;
  banner: Banner | null;
  shake: Shake | null;
  // Shaken distance not yet confirmed by the server, shown right away so the dot moves under your hand.
  pendingKm: number;
  busy: boolean;
  act: (a: Action) => Promise<boolean>;
  dismissBanner: () => void;
  startShake: () => Promise<void>;
  stopShake: () => void;
}

let shakeSub: { remove: () => void } | null = null;
let sending = 0;

async function call(path: string, body?: Action) {
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), TIMEOUT_MS);
  try {
    const res = await fetch(API + path, {
      method: body ? 'POST' : 'GET',
      headers: body ? { 'content-type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
      signal: ctl.signal,
    });
    const json = (await res.json().catch(() => ({}))) as { now?: number; state?: DispatchState; error?: string };
    return { ok: res.ok, ...json };
  } finally {
    clearTimeout(timer);
  }
}

export const useStore = create<Store>((set, get) => ({
  state: null,
  offset: 0,
  link: 'connecting',
  error: null,
  banner: null,
  shake: null,
  pendingKm: 0,
  busy: false,
  act: async (a) => {
    set({ busy: true, error: null });
    sending++;
    try {
      const r = await call('/action', a);
      if (r.state && r.now) receive(r.state, r.now);
      if (!r.ok) {
        set({ error: r.error ?? 'Dispatch refused that.' });
        return false;
      }
      return true;
    } catch {
      set({ error: 'No connection to dispatch. Nothing was sent.', link: 'offline' });
      return false;
    } finally {
      sending--;
      set({ busy: false });
    }
  },
  dismissBanner: () => set({ banner: null }),
  startShake: async () => {
    if (shakeSub) return;
    const ok = await Accelerometer.isAvailableAsync().catch(() => false);
    if (!ok) {
      set({ shake: { status: 'unavailable', count: 0 } });
      return;
    }
    set({ shake: { status: 'listening', count: 0 } });
    Accelerometer.setUpdateInterval(40);
    let last = 0;
    shakeSub = Accelerometer.addListener(({ x, y, z }) => {
      const now = Date.now();
      if (Math.abs(Math.hypot(x, y, z) - 1) < SHAKE_G || now - last < SHAKE_GAP_MS) return;
      last = now;
      const sh = get().shake;
      if (!sh) return;
      set({ shake: { ...sh, count: sh.count + 1 }, pendingKm: get().pendingKm + SHAKE_KM });
      Haptics.selectionAsync().catch(() => {});
    });
  },
  stopShake: () => {
    shakeSub?.remove();
    shakeSub = null;
    set({ shake: null });
  },
}));

export function myJob(state: DispatchState | null): Job | undefined {
  return state?.jobs.find((j) => j.engineerId === ME && isActive(j));
}

export const serverNow = () => Date.now() + useStore.getState().offset;

const seen = new Set<string>();
function notify(state: DispatchState, now: number) {
  const job = myJob(state);
  if (!job) return;
  const site = siteById(job.site)?.name ?? job.site;
  if (!seen.has(job.id)) {
    seen.add(job.id);
    useStore.setState({
      banner: { key: job.id, tone: 'job', title: `New job: ${job.asset} at ${site}`, body: `${job.carry.length ? `Collect ${job.carry.length > 1 ? `${job.carry.length} kits` : 'the kit'} at the warehouse and set off. ` : 'Set off when ready. '}${job.note}`.trim() },
    });
    Vibration.vibrate([0, 400, 200, 400]);
    Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning).catch(() => {});
  }
  const readyKey = `${job.id}:ready`;
  if (job.status === 'on-site' && !seen.has(readyKey)) {
    seen.add(readyKey);
    useStore.setState({ banner: { key: readyKey, tone: 'go', title: `On site at ${site}`, body: 'Tap Start repair when you begin work.' } });
    Vibration.vibrate([0, 300, 150, 300]);
  }
}

function receive(state: DispatchState, now: number) {
  useStore.setState({ state, offset: now - Date.now(), link: 'live' });
  notify(state, now);
}

async function poll() {
  // A poll that started before an action finished would show the old state for a second.
  if (sending > 0) return;
  try {
    const r = await call('/state');
    if (r.state && r.now) receive(r.state, r.now);
    else useStore.setState({ link: 'offline', error: r.error ?? null });
  } catch {
    useStore.setState({ link: 'offline' });
  }
}

async function flushShakes() {
  const { pendingKm, state } = useStore.getState();
  const job = myJob(state);
  if (pendingKm <= 0 || sending > 0) return;
  if (!job || (job.status !== 'en-route' && job.status !== 'leaving')) {
    useStore.setState({ pendingKm: 0 });
    return;
  }
  const km = Math.min(pendingKm, 6);
  sending++;
  try {
    const r = await call('/action', { type: 'travel', engineerId: ME, km });
    useStore.setState({ pendingKm: Math.max(0, useStore.getState().pendingKm - km) });
    if (r.state && r.now) receive(r.state, r.now);
    // Arrived mid-batch: the server refuses the leftover distance, which is fine.
    if (!r.ok) useStore.setState({ pendingKm: 0 });
  } catch {
    useStore.setState({ link: 'offline' });
  } finally {
    sending--;
  }
}

export function startLink() {
  let active = AppState.currentState === 'active';
  poll();
  const pollId = setInterval(() => { if (active) poll(); }, POLL_MS);
  const flushId = setInterval(flushShakes, FLUSH_MS);
  const sub = AppState.addEventListener('change', (s) => {
    active = s === 'active';
    if (active) poll();
  });
  return () => {
    clearInterval(pollId);
    clearInterval(flushId);
    sub.remove();
    useStore.getState().stopShake();
  };
}
