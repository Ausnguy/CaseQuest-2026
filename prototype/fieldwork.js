// Field work for Parvius: failure predictions (data/model/predictions.json), the parts warehouse and engineer
// dispatch, shared live with the engineer's phone through the dispatch API in web/.
// Loaded after parvius.html's own script; uses its globals (S, D, UI, siteBy, assetBy, stat, esc, addLog,
// and the 3D map's addBox/addLine/addText/proj/items).
(() => {
  const PROD = 'https://casequest-2026.vercel.app';
  const q = new URLSearchParams(location.search).get('api');
  // On Vercel and on the local dev server (web/scripts/dev.ts) the API is same-origin; anywhere else use production.
  const ORIGIN = q ? q.replace(/\/$/, '') : /\.vercel\.app$/.test(location.hostname) || location.port === '3300' ? '' : PROD;
  const PHONE = 'ENG-1';
  // The warehouse stands beside the maintenance base: engineers collect their kits as they leave.
  const WAREHOUSE = [-2.9, 0], SUPPLIER = [-21, 0];
  const FW = { state: null, cfg: null, off: 0, err: null, model: null, modelErr: null, sig: '', ticks: 0, disp: {}, sending: new Set() };
  window.FW = FW;

  const now = () => Date.now() + FW.off;
  const dur = (ms) => { const s = Math.max(0, Math.ceil(ms / 1000)); return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`; };
  const clock = (t) => new Date(t - FW.off).toLocaleTimeString('en-GB', { hour12: false });
  const active = (j) => j.status !== 'closed' && j.status !== 'cancelled';
  const pct = (x) => `${Math.round(x * 100)}%`;
  const short = (name) => name.replace(' (phone)', '');
  const legDone = (l, t) => Math.min(l.km, l.doneKm + (l.autoSince === null ? 0 : Math.max(0, t - l.autoSince) / 1000 * FW.cfg.autoKmPerS));
  const isMgr = () => S.role === 'Manager';

  async function call(path, opt = {}) {
    const ctl = new AbortController(), tm = setTimeout(() => ctl.abort(), 6000);
    try {
      const r = await fetch(ORIGIN + path, { ...opt, signal: ctl.signal, headers: opt.body ? { 'content-type': 'application/json' } : {} });
      const b = await r.json().catch(() => ({}));
      if (b.state) { FW.off = b.now - Date.now(); FW.state = b.state; if (b.config) FW.cfg = b.config; }
      return { ok: r.ok, ...b };
    } finally { clearTimeout(tm); }
  }
  async function act(a) {
    try {
      const r = await call('/api/action', { method: 'POST', body: JSON.stringify(a) });
      if (!r.ok) { toast(r.error || 'Dispatch refused that.'); return false; }
      FW.err = null;
      return true;
    } catch { toast('Dispatch server unreachable. Nothing was sent.'); return false; }
  }
  function toast(msg) {
    let t = document.getElementById('fwToast');
    if (!t) { t = document.createElement('div'); t.id = 'fwToast'; t.setAttribute('role', 'status'); document.body.appendChild(t); }
    t.textContent = msg; t.classList.add('on');
    clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove('on'), 6000);
  }

  // ---------- what the model says, and what dispatch is doing about it ----------
  const planFor = (aid) => (FW.model?.plans[dayStr(S.day)] || []).find((p) => p.asset_id === aid) || null;
  const jobsFor = (aid) => (FW.state?.jobs || []).filter((j) => j.asset === aid);
  const liveJob = (aid) => jobsFor(aid).filter(active).slice(-1)[0] || null;
  const doneJob = (aid) => jobsFor(aid).filter((j) => j.status === 'closed').slice(-1)[0] || null;
  // Kits are stocked per machine type, named like the server's SKUs: "Bearing kit · Lift pump".
  const skuOf = (plan, k) => `${k.kit} · ${plan.asset_type}`;
  const kitSkus = (plan) => plan.parts.slice().sort((x, y) => y.likelihood - x.likelihood).map((k) => skuOf(plan, k));
  const onShelf = (sk) => FW.state?.stock?.[sk] ?? 0;
  const onOrder = (sk) => (FW.state?.restocks || []).find((r) => r.sku === sk && !r.received) || null;
  const shortKits = (plan) => (plan && FW.state ? kitSkus(plan).filter((sk) => onShelf(sk) < 1) : []);
  const kitName = (sk) => sk.split(' · ')[0];
  const engName = (id) => short(FW.state?.engineers.find((e) => e.id === id)?.name || id);
  const freeEngineer = () => FW.state && (FW.state.engineers.find((e) => e.id === PHONE && !e.jobId) || FW.state.engineers.find((e) => !e.jobId));
  const topCause = (plan) => plan.parts.slice().sort((x, y) => y.likelihood - x.likelihood);

  function issueText(plan) {
    const [a, b] = topCause(plan);
    return `${a.for_cause} likely (${pct(a.likelihood)})${b ? `, or a ${b.for_cause.toLowerCase()} (${pct(b.likelihood)})` : ''}`;
  }

  const usedText = (j) => (!j.used ? '' : j.used.length ? `Fitted the ${lst(j.used.map((k) => kitName(k).toLowerCase()))}` : 'No parts needed');
  function jobLine(j, t) {
    const who = engName(j.engineerId);
    switch (j.status) {
      case 'scheduled': return `${who} has the kits and is due to leave the base`;
      case 'en-route': return `${who} driving to site, ${(j.leg.km - legDone(j.leg, t)).toFixed(1)} km to go`;
      case 'on-site': return `${who} on site, about to start the repair`;
      case 'working': { const left = j.workStartAt + FW.cfg.workS * 1000 - t; return left > 0 ? `${who} repairing, about ${dur(left)} left` : `${who} finishing the repair`; }
      case 'done': return `Repaired. ${usedText(j)}. ${who} packing up`;
      case 'leaving': return `Repaired. ${usedText(j)}. ${who} heading back${j.carry.length > (j.used || []).length ? ' with the unused kits' : ''}`;
      default: return '';
    }
  }
  const stage = (j) => (!j ? 0 : j.status === 'scheduled' ? 1 : j.status === 'en-route' ? 2 : j.status === 'on-site' || j.status === 'working' ? 3 : 4);

  // Map state per asset, read by parvius.html's scene().
  FW.assetState = (aid) => {
    if (!FW.state) return {};
    const j = liveJob(aid), plan = planFor(aid);
    // The engineer's own map label says what is happening while a job is live. Nothing here changes the machine.
    if (j && (j.status === 'done' || j.status === 'leaving')) return { repaired: true, label: 'REPAIRED', labelCol: 'rgb(30,127,79)' };
    if (j) return { predicted: !!plan };
    if (doneJob(aid)) return { repaired: true };
    if (plan) return { predicted: true, label: `${topCause(plan)[0].for_cause.toUpperCase()}?` };
    return {};
  };

  // ---------- one card body, used on the Work board, in the inspector and in the field overview ----------
  function readings(plan) {
    const ev = plan.evidence;
    return `<div class="fw-read"><span class="${ev.vibration_x_normal > 1.3 ? 'hi' : ''}"><b>${ev.vibration_x_normal}×</b> vibration</span><span class="${ev.temp_above_normal_c > 5 ? 'hi' : ''}"><b>${ev.temp_above_normal_c > 0 ? '+' : ''}${ev.temp_above_normal_c} °C</b> temperature</span>${ev.noise_notes ? `<span class="hi"><b>${ev.noise_notes}</b> noise note${ev.noise_notes > 1 ? 's' : ''}</span>` : ''}</div>`;
  }
  function stockCell(sk) {
    const n = onShelf(sk), o = onOrder(sk);
    if (n > 0) return `<b class="fw-ok">${n} in the warehouse</b>`;
    if (o) return `<b class="fw-amb">Out of stock · ${o.qty} arriving in <span data-eta="${o.arriveAt}">${dur(o.arriveAt - now())}</span></b>`;
    return `<b class="fw-bad">Out of stock</b>${isMgr() ? `<button class="ghost fw-mini" data-act="fwRestock" data-sku="${esc(sk)}" data-qty="2">Restock 2</button>` : ''}`;
  }
  function kitsHtml(aid, plan, j) {
    const rows = j ? j.carry.map((sk) => {
      const fitted = (j.used || []).includes(sk);
      const v = !j.used ? `<b class="fw-amb">With ${esc(engName(j.engineerId))}</b>` : fitted ? '<b class="fw-ok">Fitted</b>' : '<b class="fw-ok">Not needed, going back</b>';
      return `<div class="fw-row"><span>${esc(kitName(sk))}</span>${v}</div>`;
    }) : kitSkus(plan).map((sk) => `<div class="fw-row"><span>${esc(kitName(sk))}</span><span class="fw-r">${stockCell(sk)}</span></div>`);
    return `<div class="fw-parts">${rows.join('')}</div>`;
  }
  function steps(j) {
    const n = stage(j), lab = ['Predicted', 'Booked', 'Driving', 'On site', 'Repaired'];
    return `<ol class="fw-steps">${lab.map((l, i) => `<li class="${i < n ? 'done' : i === n ? 'cur' : ''}">${l}</li>`).join('')}</ol>`;
  }
  function actionHtml(aid, plan) {
    const j = liveJob(aid), done = doneJob(aid);
    if (j) {
      const cancel = isMgr() && ['scheduled', 'en-route', 'on-site'].includes(j.status) ? `<button class="ghost" data-act="fwCancel" data-job="${j.id}">Cancel</button>` : '';
      return `<div class="fw-live" data-a="${aid}">${jobLine(j, now())}</div><div class="wc-act">${UI.page === 'map' ? '' : `<button class="ghost" data-act="fwMap" data-a="${aid}">Watch on map</button>`}${cancel}</div>`;
    }
    if (done) return `<div class="fw-live fw-done">Repaired by ${esc(engName(done.engineerId))} at ${clock(done.doneAt)}. ${usedText(done)}.</div>`;
    if (!plan) return '';
    if (!FW.state) return `<p class="fw-plan muted">${FW.err ? esc(FW.err) : 'Connecting to dispatch…'}</p>`;
    const miss = shortKits(plan), eng = freeEngineer(), who = eng ? esc(short(eng.name)) : 'an engineer';
    const plain = miss.length
      ? `The warehouse is out of the ${lst(miss.map((k) => kitName(k).toLowerCase()))}. Restock before an engineer can be assigned.`
      : `${who} takes ${plan.parts.length > 1 ? 'both kits' : 'the kit'} from the warehouse and leaves now. Kits not fitted come back to the shelf.`;
    if (!isMgr()) return `<p class="fw-plan">${plain}</p><div class="wc-act"><button class="locked" data-act="fwBeMgr" title="Only the manager restocks and sends engineers">${ico('lock')} Switch to manager to send</button></div>`;
    if (!eng) return `<p class="fw-plan">All engineers are on jobs.</p>`;
    const busy = FW.sending.has(aid);
    if (miss.length) return `<p class="fw-plan">${plain}</p><div class="wc-act"><button class="primary" disabled title="Kits missing from the warehouse">Send engineer</button><a class="ghost btn-link" href="#/inventory">Inventory</a></div>`;
    return `<p class="fw-plan">${plain}</p><div class="wc-act"><button class="primary" data-act="fwSend" data-a="${aid}" ${busy ? 'disabled' : ''}>${busy ? 'Sending…' : 'Send engineer'}</button></div>`;
  }
  function holdHtml(aid) {
    const sid = assetBy[aid].site;
    if (stat(sid) !== 'HOLD') return '';
    const hz = [...new Set(openGates(sid).map((g) => g.hazard))];
    return `<div class="fw-hold">${esc(siteBy[sid].name)} is on safety hold (${esc(lst(hz))}). The engineer gets the hazard list and works under those controls.</div>`;
  }
  function body(aid) {
    const plan = planFor(aid), j = liveJob(aid);
    if (!plan) return `<p class="wc-say">Work in flight on the ${esc(assetBy[aid].type.toLowerCase())}.</p>${actionHtml(aid, null)}`;
    return `<p class="wc-say"><b>${issueText(plan)}.</b> ${pct(plan.chance)} chance it fails within 3 days.</p>
      ${readings(plan)}${steps(j)}${kitsHtml(aid, plan, j)}${j || doneJob(aid) ? '' : holdHtml(aid)}${actionHtml(aid, plan)}`;
  }

  // Assets with a prediction for the replay day, plus anything with a live job so it stays visible.
  function predItems() {
    const ids = new Set((FW.model?.plans[dayStr(S.day)] || []).map((p) => p.asset_id));
    (FW.state?.jobs || []).filter(active).forEach((j) => ids.add(j.asset));
    return [...ids].filter((aid) => assetBy[aid]).map((aid) => ({ k: 'p:' + aid, type: 'predict', a: assetBy[aid], sid: assetBy[aid].site }));
  }
  FW.addWork = (nowList, blocked) => {
    if (!FW.model) return;
    const list = predItems(), ids = new Set(list.map((it) => it.a.id));
    // The prediction card replaces the readiness flag for the same machine.
    for (const arr of [nowList, blocked]) for (let i = arr.length - 1; i >= 0; i--) if (arr[i].type === 'flag' && ids.has(arr[i].a.id)) arr.splice(i, 1);
    nowList.unshift(...list);
  };
  FW.card = (it) => {
    const aid = it.a.id, s = siteBy[it.sid];
    return `<div class="wcard p2 fw-card" id="wc-p-${aid}">
      <div class="wc-top"><span class="prio p2" title="The failure model expects a breakdown soon">P2</span><b>${aid}</b><button class="site" data-wk="site" data-site="${it.sid}">${s.name}</button><span class="kind">${esc(it.a.type)}</span></div>
      ${body(aid)}
    </div>`;
  };
  FW.assetBlock = (aid) => {
    if (!FW.model) return FW.modelErr ? `<p class="muted small">Failure model unavailable: ${esc(FW.modelErr)}</p>` : '';
    if (!planFor(aid) && !liveJob(aid)) return `<span class="mono" style="margin-top:6px">FAILURE MODEL</span><p>No failure predicted for ${prettyDay(S.day)}.</p>`;
    return `<span class="mono" style="margin-top:6px">FAILURE MODEL</span><div class="fw-insp">${body(aid)}</div>`;
  };
  FW.overviewBlock = (bare) => {
    if (!FW.model) return FW.modelErr && bare ? `<p class="small muted">Failure model unavailable: ${esc(FW.modelErr)}</p>` : '';
    const list = predItems(), head = bare ? '' : `<span class="mono">PREDICTED FAILURES · ${prettyDay(S.day).toUpperCase()}</span>`;
    if (!list.length) return `<div class="${bare ? '' : 'fw-ov'}">${head}<p class="small muted">None for ${prettyDay(S.day)}.</p></div>`;
    return `<div class="${bare ? 'fw-ov bare' : 'fw-ov'}">${head}${list.map((it) => {
      const aid = it.a.id, plan = planFor(aid), j = liveJob(aid), done = doneJob(aid);
      const sub = j ? `<span class="fw-live" data-a="${aid}">${jobLine(j, now())}</span>` : done ? '<span class="fw-ok">Repaired</span>' : plan ? `<span>${issueText(plan)}</span>` : '';
      const miss = plan ? shortKits(plan) : [];
      const btn = j || done || !plan || !isMgr() || !freeEngineer() ? ''
        : miss.length ? `<a class="ghost btn-link" href="#/inventory" title="Out of the ${esc(lst(miss.map(kitName)).toLowerCase())}">Restock first</a>`
          : `<button class="primary" data-act="fwSend" data-a="${aid}" ${FW.sending.has(aid) ? 'disabled' : ''}>Send engineer</button>`;
      return `<div class="fw-ovrow"><button class="fw-ovname" data-act="asset" data-a="${aid}"><b>${aid} · ${esc(it.a.type)}, ${esc(siteBy[it.sid].name)}</b>${sub}</button>${btn}</div>`;
    }).join('')}${isMgr() ? '' : `<button class="locked fw-ovmgr" data-act="fwBeMgr">${ico('lock')} Switch to manager to send engineers</button>`}</div>`;
  };

  FW.handle = async (b) => {
    const a = b.dataset.act;
    if (a === 'fwBeMgr') { setRole('Manager'); toast('Acting as manager. You can now send engineers.'); refresh(true); return; }
    if (a === 'fwMap') { showOnMap('asset', b.dataset.a); return; }
    if (a === 'fwReset') {
      if (!isMgr()) { toast('Only the manager can reset dispatch.'); return; }
      if (!confirm('Reset the warehouse to its starting stock and clear every order and job for everyone, including the engineer phone?')) return;
      if (await act({ type: 'reset' })) addLog({ fw: true, action: 'Reset dispatch', reason: 'Warehouse back to starting stock, all jobs cleared' });
      refresh(true); return;
    }
    if (!isMgr()) { toast('Only the manager can do this.'); return; }
    if (a === 'fwSend') await send(b.dataset.a);
    else if (a === 'fwRestock') {
      const sk = b.dataset.sku, qty = Number(b.dataset.qty || document.getElementById('fwQty-' + b.dataset.i)?.value || 2);
      if (await act({ type: 'restock', sku: sk, qty })) {
        addLog({ fw: true, action: `Restock ${qty} × ${sk}`, reason: `Supplier delivery to the warehouse in ${dur(FW.cfg.restockS * 1000)}` });
        toast(`${qty} × ${sk} ordered. Lands in the warehouse in ${dur(FW.cfg.restockS * 1000)}.`);
      }
    }
    else if (a === 'fwCancel') {
      const j = FW.state.jobs.find((x) => x.id === b.dataset.job);
      if (await act({ type: 'cancelJob', jobId: b.dataset.job }) && j) addLog({ fw: true, action: 'Cancel job', asset: j.asset, site: j.site, reason: j.id });
    }
    refresh(true);
  };

  // Assign the free engineer with the plan's kits, most likely cause first. The server refuses if any is not in stock.
  async function send(aid) {
    // Only a manager sends work. The model alerts; it never books anyone by itself.
    if (!isMgr()) { toast('Only the manager can send an engineer.'); return; }
    if (FW.sending.has(aid)) return;
    FW.sending.add(aid); refresh(true);
    try {
      const plan = planFor(aid), asset = assetBy[aid], eng = freeEngineer();
      if (!plan || !eng) { toast('Nothing to send.'); return; }
      const miss = shortKits(plan);
      if (miss.length) { toast(`Out of the ${lst(miss)}. Restock it first.`); return; }
      const hz = stat(asset.site) === 'HOLD' ? openGates(asset.site).map((g) => `${g.id} ${g.hazard}`) : [];
      const note = `${issueText(plan)}. Vibration ${plan.evidence.vibration_x_normal}× normal, temperature ${plan.evidence.temp_above_normal_c > 0 ? '+' : ''}${plan.evidence.temp_above_normal_c} °C above normal.`;
      const kits = kitSkus(plan);
      const ok = await act({
        type: 'requestEngineer', asset: aid, engineerId: eng.id,
        note: note.slice(0, 200), hseHold: hz.length ? hz.join('; ').slice(0, 200) : null,
        kits, tools: plan.tools.slice(0, 12), chance: plan.chance,
      });
      if (!ok) return;
      addLog({ fw: true, action: 'Send engineer', asset: aid, site: asset.site, reason: `${short(eng.name)}, carrying ${lst(kits.map(kitName)).toLowerCase()}` });
      const [sx, sz] = POS[asset.site];
      if (UI.page === 'map') cam.goal = { yaw: cam.yaw, pitch: 0.82, dist: 40, tx: sx * 0.55, tz: sz * 0.55 };
      toast(`${short(eng.name)} took the kits from the warehouse and is heading to ${siteBy[asset.site].name}.`);
    } finally { FW.sending.delete(aid); }
  }

  // ---------- Inventory page (manager's view of the warehouse) ----------
  // Kits each predicted machine for the replay day still needs, that no engineer has been sent with yet.
  function neededToday() {
    const need = {};
    for (const plan of FW.model?.plans[dayStr(S.day)] || []) {
      if (liveJob(plan.asset_id) || doneJob(plan.asset_id)) continue;
      for (const sk of kitSkus(plan)) (need[sk] = need[sk] || []).push(plan.asset_id);
    }
    return need;
  }
  function inventoryHtml() {
    if (!FW.state || !FW.cfg) return `<div class="panel"><p class="muted">${FW.err ? esc(FW.err) : 'Connecting to dispatch…'}</p></div>`;
    const need = neededToday(), out = {};
    for (const j of FW.state.jobs.filter(active)) for (const sk of j.carry) if (!(j.used || []).includes(sk)) (out[sk] = out[sk] || []).push(j);
    const mgr = isMgr(), t = now();
    const groups = [...new Set(FW.cfg.skus.map((sk) => sk.split(' · ')[1]))];
    let i = 0, shortN = 0;
    const body = groups.map((ty) => `<tr class="inv-grp"><th colspan="6" scope="rowgroup">${esc(ty)}</th></tr>` + FW.cfg.skus.filter((sk) => sk.endsWith(' · ' + ty)).map((sk) => {
      const n = onShelf(sk), o = onOrder(sk), nd = need[sk] || [], ow = out[sk] || [], k = i++;
      const short = nd.length > n;
      if (short) shortN++;
      const st = short ? `<span class="inv-st bad">${n === 0 ? 'Out' : 'Short'}</span>` : n === 0 ? '<span class="inv-st amb">Empty</span>' : '<span class="inv-st ok">OK</span>';
      const act = o ? `<span class="muted">${o.qty} arriving in <span data-eta="${o.arriveAt}">${dur(o.arriveAt - t)}</span></span>`
        : mgr ? `<span class="inv-act"><input type="number" id="fwQty-${k}" min="1" max="10" value="${Math.max(2, nd.length - n)}" aria-label="Quantity of ${esc(sk)}"><button class="ghost fw-mini" data-act="fwRestock" data-sku="${esc(sk)}" data-i="${k}">Restock</button></span>` : '';
      return `<tr class="${short ? 'short' : ''}"><td>${esc(kitName(sk))}</td><td class="num"><b>${n}</b></td>
        <td>${ow.length ? ow.map((j) => `${esc(engName(j.engineerId))} · ${j.asset}`).join('<br>') : '<span class="muted">none</span>'}</td>
        <td>${nd.length ? nd.join(', ') : '<span class="muted">none</span>'}</td><td>${st}</td><td>${act}</td></tr>`;
    }).join('')).join('');
    const moves = FW.state.moves.slice().reverse().slice(0, 14).map((m) =>
      `<li><span class="mono">${clock(m.t)}</span><b class="${m.qty > 0 ? 'fw-ok' : m.qty < 0 ? 'fw-amb' : ''}">${m.qty > 0 ? '+' + m.qty : m.qty < 0 ? m.qty : 'fitted'}</b><span>${esc(m.sku)}</span><span class="muted">${esc(m.why.replace(' (phone)', ''))}</span></li>`).join('');
    return `<div class="inv-grid">
      <div class="panel"><div class="panel-h"><h2>Stock by kit</h2><span class="muted small">${shortN ? `<b class="fw-bad">${shortN} kit${shortN > 1 ? 's' : ''} short</b> for ${prettyDay(S.day)}'s predictions` : `Covers every prediction for ${prettyDay(S.day)}`}</span></div>
        <div class="inv-scroll"><table class="inv"><thead><tr><th scope="col">Kit</th><th scope="col" class="num">On shelf</th><th scope="col">Out with engineers</th><th scope="col">Needed for predictions</th><th scope="col">Status</th><th scope="col">${mgr ? 'Restock' : ''}</th></tr></thead><tbody>${body}</tbody></table></div>
        ${mgr ? `<p class="small muted">Supplier deliveries land in ${dur(FW.cfg.restockS * 1000)} (the sites' median 2025 parts wait, at 3 s per hour). Starting quantities are modeled; the workbook has no item-level stock.</p>` : `<button class="locked" data-act="fwBeMgr">${ico('lock')} Switch to manager to restock</button>`}
      </div>
      <div class="panel"><div class="panel-h"><h2>Movements</h2></div>${moves ? `<ul class="inv-moves">${moves}</ul>` : '<p class="muted small">Nothing has moved yet.</p>'}</div>
    </div>`;
  }
  FW.renderInventory = () => { const el = document.getElementById('invBody'); if (el) el.innerHTML = inventoryHtml(); };
  document.getElementById('invBody')?.addEventListener('click', (e) => { const b = e.target.closest('[data-act]'); if (b) FW.handle(b); });

  // ---------- Field crew panel on the Work page ----------
  function engWhere(e) {
    if (e.at === 'BASE') return 'at the base';
    if (e.at && siteBy[e.at]) return `at ${siteBy[e.at].name}`;
    return e.jobId ? 'on the road' : 'off site';
  }
  function sideHtml() {
    if (!FW.state) return `<p class="muted small">${FW.err ? esc(FW.err) : 'Connecting to dispatch…'}</p>`;
    const t = now();
    const engs = FW.state.engineers.map((e) => { const j = e.jobId && FW.state.jobs.find((x) => x.id === e.jobId); return `<div class="fw-row"><span><b>${esc(e.name)}</b><br><span class="muted">${engWhere(e)}</span></span><span class="fw-r">${j ? `${j.asset}<br><span class="muted">${j.status.replace('-', ' ')}</span>` : '<span class="muted">free</span>'}</span></div>`; }).join('');
    const parts = FW.state.restocks.filter((r) => !r.received).map((r) => `<div class="fw-row"><span>${r.qty} × ${esc(r.sku)}</span><b>${dur(r.arriveAt - t)}</b></div>`).join('');
    return `<span class="mono">ENGINEERS</span>${engs}${parts ? `<span class="mono">RESTOCKS ON THE WAY</span>${parts}` : ''}
      <div class="wc-act"><a class="ghost btn-link" href="#/inventory">Inventory</a><button class="ghost" data-act="fwReset" title="Clears the warehouse, orders and jobs for everyone">Reset dispatch</button></div>`;
  }
  FW.side = () => `<div class="panel" id="fwPanel"><div class="panel-h"><h2>Field crew <span class="fw-conn" id="fwConn"></span></h2></div><div id="fwSide">${sideHtml()}</div></div>`;

  // ---------- 3D map: base, warehouse, engineers and supplier trucks ----------
  const ENG = [89, 128, 166], TRUCK = [93, 93, 96];
  const siteSpot = (sid) => [POS[sid][0], POS[sid][1] + 1.3];
  const same = (a, b) => a[0] === b[0] && a[1] === b[1];
  function assetSpot(aid) {
    const a = assetBy[aid], i = D.assets.filter((x) => x.site === a.site).indexOf(a), [cx, cz] = POS[a.site];
    return [cx - 2.2 + i * 2.2, cz + 0.55];
  }
  function engTarget(e, t) {
    const j = e.jobId && FW.state.jobs.find((x) => x.id === e.jobId);
    if (j && j.leg && (j.status === 'en-route' || j.status === 'leaving')) {
      const f = j.leg.km ? legDone(j.leg, t) / j.leg.km : 1;
      const from = same(j.leg.from, POS[j.site]) ? siteSpot(j.site) : j.leg.from, to = same(j.leg.to, POS[j.site]) ? siteSpot(j.site) : j.leg.to;
      return { p: [from[0] + (to[0] - from[0]) * f, from[1] + (to[1] - from[1]) * f], j, to };
    }
    if (j && ['on-site', 'working', 'done'].includes(j.status)) return { p: siteSpot(j.site), j, onSite: true };
    // Engineers at the base park side by side in front of it instead of on one spot.
    const i = FW.state.engineers.indexOf(e), park = [-1.1 + i * 1.1, 1.6];
    if (j) return { p: same(e.pos, [0, 0]) ? park : e.pos, j };
    if (e.at && POS[e.at]) return { p: siteSpot(e.at) };
    return { p: same(e.pos, [0, 0]) ? park : e.pos };
  }
  // Ground level, or the pad's top when the vehicle is inside a site's pad.
  const groundAt = (x, z) => (Object.values(POS).some(([cx, cz]) => Math.abs(x - cx) < 3.7 && Math.abs(z - cz) < 3.2) ? 0.28 : 0.02);
  function vehicle(x, z, col, t, lights) {
    const y = groundAt(x, z);
    addBox(x, y, z, 0.75, 0.32, 0.5, col, { stroke: 'rgba(29,31,32,.6)' });
    addBox(x + 0.12, y + 0.32, z, 0.4, 0.22, 0.46, col.map((v) => Math.min(255, v + 60)), { stroke: 'rgba(29,31,32,.6)' });
    if (lights) { const s = proj([x + 0.12, y + 0.66, z]); items.push({ t: 'dot', x: s[0], y: s[1], r: Math.max(2, s[3] * 0.07), col: Math.floor(t / 300) % 2 ? 'rgba(255,170,40,.95)' : 'rgba(255,170,40,.25)', d: s[2] - 0.5 }); }
  }
  FW.scene3d = (t) => {
    addBox(0, 0, 0, 2.2, 0.55, 1.4, [226, 226, 229], { stroke: 'rgba(29,31,32,.45)' });
    addBox(0, 0.55, 0, 2.2, 0.12, 1.4, [196, 196, 200], { stroke: 'rgba(29,31,32,.45)' });
    addText([0, 1.2, 0], 'MAINTENANCE BASE', { size: 10, col: MAPC.ink, bold: 1, mono: 1, pri: 3 });
    addBox(WAREHOUSE[0], 0, WAREHOUSE[1], 1.5, 0.75, 1.4, [214, 214, 218], { stroke: 'rgba(29,31,32,.45)' });
    addBox(WAREHOUSE[0], 0.75, WAREHOUSE[1], 1.5, 0.1, 1.4, [190, 190, 195], { stroke: 'rgba(29,31,32,.45)' });
    const stocked = FW.state?.stock ? Object.values(FW.state.stock).reduce((a, b) => a + b, 0) : null;
    addText([WAREHOUSE[0], 1.35, WAREHOUSE[1]], `WAREHOUSE${stocked === null ? '' : ` · ${stocked} KITS`}`, { size: 10, col: MAPC.muted, bold: 1, mono: 1, pri: 2 });
    if (!FW.state || !FW.cfg) return;
    const tt = now();
    for (const r of FW.state.restocks.filter((x) => !x.received && tt < x.arriveAt)) {
      const f = Math.min(1, Math.max(0, (tt - r.orderedAt) / (r.arriveAt - r.orderedAt)));
      const x = SUPPLIER[0] + (WAREHOUSE[0] - 1 - SUPPLIER[0]) * f, z = SUPPLIER[1] + (WAREHOUSE[1] - SUPPLIER[1]) * f;
      addLine([x, 0.3, z], [WAREHOUSE[0] - 1, 0.3, WAREHOUSE[1]], 'rgba(168,114,34,.8)', 1.6, [4, 4], 1);
      vehicle(x, z, TRUCK, t, true);
      addText([x, 1.3, z], `${r.qty} × ${kitName(r.sku).toUpperCase()} · ${dur(r.arriveAt - tt)}`, { size: 10, col: MAPC.amber, bold: 1, mono: 1, pri: 3 });
    }
    for (const e of FW.state.engineers) {
      const g = engTarget(e, tt), d = FW.disp[e.id] || (FW.disp[e.id] = g.p.slice());
      d[0] += (g.p[0] - d[0]) * 0.12; d[1] += (g.p[1] - d[1]) * 0.12;
      if (g.to) addLine([d[0], 0.3, d[1]], [g.to[0], 0.3, g.to[1]], 'rgba(89,128,166,.9)', 2, [6, 4], 1);
      vehicle(d[0], d[1], ENG, t, !!g.to);
      if (g.onSite) {
        const [wx, wz] = assetSpot(g.j.asset), bob = g.j.status === 'working' ? 0.05 * Math.abs(Math.sin(t / 160)) : 0;
        addBox(wx, 0.28 + bob, wz, 0.2, 0.5, 0.2, [255, 160, 40], { stroke: 'rgba(29,31,32,.6)' });
        addBox(wx, 0.78 + bob, wz, 0.16, 0.16, 0.16, [236, 200, 160], { stroke: 'rgba(29,31,32,.6)' });
        if (g.j.status === 'working') { const s = proj([wx, 1.0, wz]), pu = 0.5 + 0.5 * Math.sin(t / 180); items.push({ t: 'ring', x: s[0], y: s[1], r: (6 + pu * 5) * s[3] / 34, col: MAPC.accent, d: s[2] - 1 }); }
      }
      const st = g.j?.status, tag = !g.j ? '' : st === 'working' ? 'REPAIRING' : st === 'on-site' ? 'ON SITE' : st === 'done' ? 'PACKING UP' : st === 'leaving' ? 'HEADING BACK' : st === 'en-route' ? `TO ${siteBy[g.j.site].name.toUpperCase()}` : 'LEAVING WITH KITS';
      addText([d[0], 1.25, d[1]], `${short(e.name).toUpperCase()}${e.phone ? ' (PHONE)' : ''}${tag ? ' · ' + tag : ''}`, { size: 11, col: '#41678c', bold: 1, pri: 4 });
    }
  };

  // ---------- live updates ----------
  function connHtml() { return FW.err ? `<span class="fw-bad">● ${esc(FW.err)}</span>` : FW.state ? '<span class="fw-ok">● live</span>' : '…'; }
  function tick() {
    const t = now();
    document.querySelectorAll('.fw-live[data-a]').forEach((el) => { const j = liveJob(el.dataset.a); if (j) el.textContent = jobLine(j, t); });
    document.querySelectorAll('[data-eta]').forEach((el) => { el.textContent = dur(Number(el.dataset.eta) - t); });
    const side = document.getElementById('fwSide'); if (side) side.innerHTML = sideHtml();
    const c = document.getElementById('fwConn'); if (c) c.innerHTML = connHtml();
  }
  // Re-render only when something that changes buttons happened, and never under an open dialog.
  function refresh(force) {
    const sig = FW.state ? JSON.stringify([UI.page, S.sel && S.sel.id, !!FW.model, S.role, S.day, [...FW.sending], FW.state.jobs.map((j) => j.id + j.status), FW.state.restocks.map((r) => r.id + r.received), FW.state.moves.at(-1)?.t, FW.state.engineers.map((e) => e.jobId)]) : String(FW.err);
    if (!force && sig === FW.sig) { tick(); return; }
    FW.sig = sig;
    if (typeof dlgOpen === 'function' && dlgOpen()) { tick(); return; }
    if (UI.page === 'work') renderWork();
    if (UI.page === 'map') renderInsp();
    if (UI.page === 'inventory') FW.renderInventory();
    const ov = document.getElementById('ovPred'); if (ov && UI.page === 'overview') ov.innerHTML = FW.overviewBlock(true);
    tick();
  }
  async function poll() {
    if (document.hidden) return;
    try { const r = await call('/api/state'); FW.err = r.ok ? null : (r.error || 'Dispatch server error'); }
    catch { FW.err = 'Dispatch server unreachable'; }
    refresh(false);
  }
  async function loadModel() {
    try {
      const r = await fetch(ORIGIN + '/model.json');
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      FW.model = await r.json();
      refresh(true);
    } catch (e) { FW.modelErr = String(e.message || e); }
  }
  document.getElementById('ovPred')?.addEventListener('click', (e) => {
    const b = e.target.closest('[data-act]'); if (!b) return;
    if (b.dataset.act === 'asset') showOnMap('asset', b.dataset.a); else FW.handle(b);
  });
  setInterval(() => { FW.ticks++; if (FW.ticks % 2 === 0) poll(); else tick(); }, 1000);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) poll(); });
  loadModel();
  poll();
})();
