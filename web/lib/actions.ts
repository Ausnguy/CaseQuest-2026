import { z } from 'zod';

import type { Action } from './dispatch.js';

const id = z.string().regex(/^[A-Z]+-?\d{1,4}$/);
const text = (max: number) => z.string().trim().max(max);

export const actionSchema: z.ZodType<Action> = z.discriminatedUnion('type', [
  z.object({ type: z.literal('orderParts'), asset: id, kit: text(80).min(3) }),
  z.object({
    type: z.literal('requestEngineer'),
    asset: id,
    engineerId: id,
    partsId: id.nullable(),
    timing: z.enum(['with-parts', 'now']),
    note: text(200),
    hseHold: text(200).nullable(),
    kits: z.array(text(60)).max(4).optional(),
    tools: z.array(text(60)).max(12).optional(),
    chance: z.number().min(0).max(1).nullable().optional(),
  }),
  z.object({ type: z.literal('cancelJob'), jobId: id }),
  z.object({ type: z.literal('depart'), jobId: id, engineerId: id }),
  // A phone batches its shakes; more than this in one call is not a person shaking a phone.
  z.object({ type: z.literal('travel'), engineerId: id, km: z.number().positive().max(6) }),
  z.object({ type: z.literal('autoTravel'), engineerId: id, on: z.boolean() }),
  z.object({ type: z.literal('leave'), jobId: id, engineerId: id }),
  z.object({ type: z.literal('reset') }),
]);
