// Local stand-in for Vercel: serves the console and the two API routes with an in-memory store.
import { readFileSync } from 'node:fs';
import { createServer } from 'node:http';
import { join } from 'node:path';

import { POST } from '../api/action.js';
import { GET, OPTIONS } from '../api/state.js';

const PORT = Number(process.env.PORT ?? 3300);
const page = join(import.meta.dirname, '../../prototype/lone-mesa-gate-console.html');

createServer(async (req, res) => {
  const url = new URL(req.url ?? '/', `http://${req.headers.host}`);
  const chunks: Buffer[] = [];
  for await (const c of req) chunks.push(c as Buffer);
  const request = new Request(url, {
    method: req.method,
    headers: req.headers as Record<string, string>,
    body: req.method === 'POST' ? Buffer.concat(chunks) : undefined,
  });
  let response: Response;
  if (url.pathname === '/api/state') response = req.method === 'OPTIONS' ? OPTIONS(request) : await GET(request);
  else if (url.pathname === '/api/action') response = req.method === 'OPTIONS' ? OPTIONS(request) : await POST(request);
  else response = new Response(readFileSync(page), { headers: { 'content-type': 'text/html' } });
  res.writeHead(response.status, Object.fromEntries(response.headers));
  res.end(Buffer.from(await response.arrayBuffer()));
}).listen(PORT, () => console.log(`console + API on http://localhost:${PORT}/?api=http://localhost:${PORT}`));
