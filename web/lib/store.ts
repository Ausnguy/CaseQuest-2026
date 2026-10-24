import { Redis } from '@upstash/redis';

import { initialState, type DispatchState } from './dispatch.js';

const KEY_STATE = 'cq:dispatch:state';
const KEY_VER = 'cq:dispatch:v';
const TIMEOUT_MS = 4000;

// Writes only if nobody else wrote since we read, so two clients can't overwrite each other.
const CAS = `
local v = redis.call('GET', KEYS[1])
if (v or '0') ~= ARGV[1] then return 0 end
redis.call('SET', KEYS[2], ARGV[2])
redis.call('SET', KEYS[1], ARGV[3])
return 1`;

export interface Store {
  load(): Promise<DispatchState>;
  save(next: DispatchState, expectedV: number): Promise<boolean>;
}

function withTimeout<T>(p: Promise<T>): Promise<T> {
  return Promise.race([
    p,
    new Promise<T>((_, reject) => setTimeout(() => reject(new Error('storage timeout')), TIMEOUT_MS)),
  ]);
}

function redisStore(redis: Redis): Store {
  return {
    async load() {
      const [v, state] = await withTimeout(redis.mget<[string | number | null, DispatchState | null]>(KEY_VER, KEY_STATE));
      if (!state) return initialState();
      return { ...state, v: Number(v ?? 0) };
    },
    async save(next, expectedV) {
      const nextV = expectedV + 1;
      const body = JSON.stringify({ ...next, v: nextV });
      const ok = await withTimeout(redis.eval(CAS, [KEY_VER, KEY_STATE], [String(expectedV), body, String(nextV)]));
      return ok === 1;
    },
  };
}

// Local development only: one process, state lost on restart.
function memoryStore(): Store {
  let state = initialState();
  return {
    async load() {
      return structuredClone(state);
    },
    async save(next, expectedV) {
      if (state.v !== expectedV) return false;
      state = { ...structuredClone(next), v: expectedV + 1 };
      return true;
    },
  };
}

let cached: Store | null = null;

export function getStore(): Store | null {
  if (cached) return cached;
  const url = process.env.KV_REST_API_URL ?? process.env.UPSTASH_REDIS_REST_URL;
  const token = process.env.KV_REST_API_TOKEN ?? process.env.UPSTASH_REDIS_REST_TOKEN;
  if (url && token) cached = redisStore(new Redis({ url, token }));
  else if (!process.env.VERCEL) cached = memoryStore();
  return cached;
}
