import { useEffect, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { BASE, SHAKE_KM, WORK_S, assetById, isActive, legDoneKm, legPos, siteById, type DispatchState, type Job, type Vec } from '@dispatch/dispatch';
import { FieldMap } from '@/components/field-map';
import { Btn, KV, Meter, Note, Panel, st } from '@/components/ui';
import { ME, myJob, serverNow, useStore } from '@/state/store';
import { C, F, S, countdown } from '@/theme';

function useNow(ms = 500) {
  const [now, setNow] = useState(serverNow);
  useEffect(() => {
    const id = setInterval(() => setNow(serverNow()), ms);
    return () => clearInterval(id);
  }, [ms]);
  return now;
}

function whereText(state: DispatchState, job: Job | undefined) {
  const me = state.engineers.find((e) => e.id === ME);
  if (!me) return 'Unknown';
  if (job?.leg && (job.status === 'en-route' || job.status === 'leaving')) return 'On the road';
  if (me.at === BASE.id) return 'At the maintenance base';
  if (me.at) return `On site at ${siteById(me.at)?.name ?? me.at}`;
  return 'Off site';
}

const STEPS = ['Booked', 'Driving', 'On site', 'Repairing', 'Back'];
function stepOf(job: Job) {
  return { scheduled: 0, 'en-route': 1, 'on-site': 2, working: 3, done: 3, leaving: 4, closed: 4, cancelled: 0 }[job.status];
}

function Steps({ job }: { job: Job }) {
  const n = stepOf(job);
  return (
    <View style={styles.steps} accessibilityLabel={`Step ${n + 1} of ${STEPS.length}: ${STEPS[n]}`}>
      {STEPS.map((s, i) => (
        <View key={s} style={styles.step}>
          <View style={[styles.stepBar, i < n && { backgroundColor: C.text }, i === n && { backgroundColor: C.primary }]} />
          <Text style={[styles.stepText, i <= n && { color: C.text }]}>{s}</Text>
        </View>
      ))}
    </View>
  );
}

// What to do right now: one headline, one line of context, one action.
function Now({ state, job, now, kmLeft, legDone }: { state: DispatchState; job: Job; now: number; kmLeft: number; legDone: number }) {
  const act = useStore((s) => s.act);
  const busy = useStore((s) => s.busy);
  const shake = useStore((s) => s.shake);
  const site = siteById(job.site);
  // Kits the engineer reports as fitted. Starts empty: a repair does not always replace a part.
  const [pick, setPick] = useState<{ job: string; used: number[] }>({ job: job.id, used: [] });
  const used = pick.job === job.id ? pick.used : [];
  const toggle = (i: number) => setPick({ job: job.id, used: used.includes(i) ? used.filter((x) => x !== i) : [...used, i] });
  const auto = job.leg?.autoSince != null;
  const to = job.status === 'en-route' ? site?.name : 'the base';

  let head = '';
  let sub = '';
  let tone: string = C.text;
  if (job.status === 'scheduled') {
    head = 'Time to leave';
    sub = job.carry.length ? `Collect ${job.carry.length > 1 ? `the ${job.carry.length} kits` : 'the kit'} at the warehouse and head to ${site?.name}.` : `Head to ${site?.name}.`;
    tone = C.primary;
  } else if (job.status === 'en-route' || job.status === 'leaving') {
    head = `${kmLeft.toFixed(1)} km to ${to}`;
    sub = shake?.status === 'unavailable' ? 'No motion sensor on this phone. Use auto drive.' : auto ? 'Auto driving. Shake to go faster.' : `Shake your phone to drive. Each shake is ${SHAKE_KM} km.`;
    tone = C.primary;
  } else if (job.status === 'on-site') {
    head = 'Ready to repair';
    sub = 'You have the kits. Start when you begin work.';
    tone = C.amber;
  } else if (job.status === 'working') {
    const left = job.workStartAt! + WORK_S * 1000 - now;
    head = left > 0 ? `Repairing · ${countdown(left)}` : 'Repairing';
    sub = job.carry.length ? 'Tick the kits you fitted, then mark it repaired. Kits you did not use go back to the warehouse.' : 'Mark it repaired when you are done.';
    tone = C.amber;
  } else if (job.status === 'done') {
    head = 'Repair done';
    const back = job.carry.length - (job.used?.length ?? 0);
    sub = back > 0 ? `Pack up and take the ${back} unused kit${back > 1 ? 's' : ''} back to the warehouse.` : 'Pack up and head back to the base when you are ready.';
    tone = C.green;
  }

  return (
    <View style={styles.now}>
      <Steps job={job} />
      <Text style={[styles.head, { color: tone }]}>{head}</Text>
      <Text style={st.small}>{sub}</Text>
      <View style={{ gap: 8, marginTop: 12 }}>
        {(job.status === 'en-route' || job.status === 'leaving') && <Meter value={legDone} />}
        {job.status === 'working' && <Meter value={(now - job.workStartAt!) / (WORK_S * 1000)} color={C.amber} />}
        {job.status === 'on-site' && (
          <Btn label="Start repair" primary disabled={busy} onPress={() => act({ type: 'startWork', jobId: job.id, engineerId: ME })} />
        )}
        {job.status === 'working' && job.carry.length > 0 && (
          <View accessibilityLabel="Kits fitted">
            <Text style={st.label}>KITS FITTED</Text>
            {job.carry.map((k, i) => {
              const on = used.includes(i);
              return (
                <Pressable key={`${k}${i}`} accessibilityRole="checkbox" accessibilityState={{ checked: on }} onPress={() => toggle(i)} style={styles.kit}>
                  <View style={[styles.box, on && { backgroundColor: C.primary, borderColor: C.primary }]}>{on ? <Text style={styles.tick}>✓</Text> : null}</View>
                  <Text style={[st.body, { flex: 1 }]}>{k.split(' · ')[0]}</Text>
                  <Text style={[st.small, { color: on ? C.primary : C.muted }]}>{on ? 'Fitted' : 'Not used'}</Text>
                </Pressable>
              );
            })}
          </View>
        )}
        {job.status === 'working' && (
          <Btn
            label={job.carry.length ? (used.length ? `Mark repaired · ${used.length} fitted` : 'Mark repaired · no parts used') : 'Mark repaired'}
            primary={now >= job.workStartAt! + WORK_S * 1000}
            disabled={busy}
            onPress={() => act({ type: 'finishWork', jobId: job.id, engineerId: ME, used: used.map((i) => job.carry[i]) })}
          />
        )}
        {job.status === 'scheduled' && (
          <Btn label="Set off" primary disabled={busy} onPress={() => act({ type: 'depart', jobId: job.id, engineerId: ME })} />
        )}
        {(job.status === 'en-route' || job.status === 'leaving') && (
          <Btn label={auto ? 'Stop auto drive' : 'Auto drive instead'} disabled={busy} onPress={() => act({ type: 'autoTravel', engineerId: ME, on: !auto })} />
        )}
        {job.status === 'done' && <Btn label="Leave site" primary disabled={busy} onPress={() => act({ type: 'leave', jobId: job.id, engineerId: ME })} />}
      </View>
    </View>
  );
}

function Details({ job }: { job: Job }) {
  const [tools, setTools] = useState(false);
  const site = siteById(job.site);
  const asset = assetById(job.asset);
  const toFit = [...(job.used ?? [])];
  const fitted = job.carry.map((k) => { const i = toFit.indexOf(k); if (i < 0) return false; toFit.splice(i, 1); return true; });
  return (
    <Panel title={`Job ${job.id} · ${site?.name}`}>
      <Text style={styles.asset}>{job.asset} · {asset?.type}</Text>
      {job.note ? <Text style={[st.body, { marginTop: 4 }]}>{job.note}</Text> : null}
      {job.chance != null ? <Text style={[st.small, { marginTop: 2 }]}>Failure model: {Math.round(job.chance * 100)}% chance it fails within 3 days.</Text> : null}
      {job.hseHold ? <View style={{ marginTop: 10 }}><Note tone="red">Safety hold at {site?.name}: {job.hseHold}. Follow isolation and gas checks before work.</Note></View> : null}
      <View style={{ marginTop: 10 }}>
        {job.carry.length ? job.carry.map((k, i) => {
          const value = !job.used ? 'With you' : fitted[i] ? 'Fitted' : 'Back to warehouse';
          return <KV key={`${k}${i}`} label={k.split(' · ')[0]} value={value} tone={value === 'Back to warehouse' ? 'warn' : 'ok'} />;
        }) : <Text style={st.small}>No kits taken for this job.</Text>}
      </View>
      {job.tools?.length ? (
        <Pressable accessibilityRole="button" accessibilityState={{ expanded: tools }} onPress={() => setTools(!tools)} style={styles.toolsHead}>
          <Text style={styles.toolsTitle}>Tools to take · {job.tools.length}</Text>
          <Text style={styles.toolsToggle}>{tools ? 'Hide' : 'Show'}</Text>
        </Pressable>
      ) : null}
      {tools && job.tools ? job.tools.map((t) => <Text key={t} style={styles.tool}>{t}</Text>) : null}
    </Panel>
  );
}

export default function MyJob() {
  const state = useStore((s) => s.state);
  const link = useStore((s) => s.link);
  const error = useStore((s) => s.error);
  const pendingKm = useStore((s) => s.pendingKm);
  const shake = useStore((s) => s.shake);
  const startShake = useStore((s) => s.startShake);
  const stopShake = useStore((s) => s.stopShake);
  const now = useNow();
  const job = myJob(state);
  const travelling = job?.status === 'en-route' || job?.status === 'leaving';

  // Listen for shakes only while there is somewhere to drive to.
  useEffect(() => {
    if (travelling && !shake) startShake();
    if (!travelling && shake) stopShake();
  }, [travelling, shake, startShake, stopShake]);

  if (!state) {
    return (
      <SafeAreaView style={styles.center}>
        <Text style={st.big}>Lone Mesa Field</Text>
        <Text style={st.small}>{link === 'offline' ? 'No connection to dispatch. Retrying…' : 'Connecting to dispatch…'}</Text>
      </SafeAreaView>
    );
  }

  const me = state.engineers.find((e) => e.id === ME);
  let pos: Vec | null = me?.pos ?? null;
  let kmLeft = 0;
  let legDone = 0;
  if (job?.leg && travelling) {
    const doneKm = Math.min(job.leg.km, legDoneKm(job.leg, now) + pendingKm);
    kmLeft = job.leg.km - doneKm;
    legDone = job.leg.km ? doneKm / job.leg.km : 1;
    pos = legPos({ ...job.leg, doneKm, autoSince: null }, now);
  }
  const history = state.jobs.filter((j) => j.engineerId === ME && !isActive(j)).reverse().slice(0, 6);

  return (
    <SafeAreaView edges={['top']} style={{ flex: 1, backgroundColor: C.bg }}>
      <View style={styles.top}>
        <View>
          <Text style={styles.brand}>LONE MESA FIELD</Text>
          <Text style={st.small}>{me?.name.replace(' (phone)', '') ?? ME} · {whereText(state, job)}</Text>
        </View>
        <Text style={[styles.link, { color: link === 'live' ? C.green : C.red }]}>{link === 'live' ? '● LIVE' : '● OFFLINE'}</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: S.gutter, gap: S.gap, paddingBottom: 40 }}>
        {error ? <Note tone="red">{error}</Note> : null}
        {job ? (
          <Now state={state} job={job} now={now} kmLeft={kmLeft} legDone={legDone} />
        ) : (
          <View style={styles.now}>
            <Text style={styles.head}>No job</Text>
            <Text style={st.small}>When the manager sends you to a machine, this phone buzzes and the job shows here with when to leave.</Text>
          </View>
        )}
        <FieldMap me={pos} job={job} holdSites={job?.hseHold ? new Set([job.site]) : new Set()} />
        {job ? <Details job={job} /> : null}
        {history.length ? (
          <Panel title="Done today">
            {history.map((j) => (
              <View key={j.id} style={styles.hist}>
                <Text style={[st.body, { flex: 1 }]}>{j.asset} · {siteById(j.site)?.name}</Text>
                <Text style={[st.small, { color: j.status === 'closed' ? C.green : C.muted }]}>{j.status === 'closed' ? 'Repaired' : 'Cancelled'}</Text>
              </View>
            ))}
          </Panel>
        ) : null}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  kit: { flexDirection: 'row', alignItems: 'center', gap: 10, minHeight: 48, borderBottomWidth: 1, borderBottomColor: C.line },
  box: { width: 22, height: 22, borderWidth: 1.5, borderColor: C.text, borderRadius: 2, alignItems: 'center', justifyContent: 'center' },
  tick: { color: C.panel, fontFamily: F.semibold, fontSize: 14, lineHeight: 16 },
  center: { flex: 1, backgroundColor: C.bg, alignItems: 'center', justifyContent: 'center', gap: 6 },
  top: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: S.gutter, paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: C.line, backgroundColor: C.panel },
  brand: { fontFamily: F.displayBold, fontSize: 20, color: C.text, letterSpacing: 1.6 },
  link: { fontFamily: F.mono, fontSize: 11, letterSpacing: 0.8 },
  now: { backgroundColor: C.panel, borderWidth: 1, borderColor: C.line, borderTopWidth: 3, borderTopColor: C.text, padding: 14 },
  head: { fontFamily: F.displayBold, fontSize: 38, lineHeight: 42, color: C.text, marginTop: 10, fontVariant: ['tabular-nums'] },
  steps: { flexDirection: 'row', gap: 3 },
  step: { flex: 1, gap: 5 },
  stepBar: { height: 4, backgroundColor: C.line },
  stepText: { fontFamily: F.mono, fontSize: 9.5, letterSpacing: 0.4, textTransform: 'uppercase', color: C.muted },
  asset: { fontFamily: F.displayBold, fontSize: 24, color: C.text },
  toolsHead: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 12, minHeight: 44 },
  toolsTitle: { fontFamily: F.semibold, fontSize: 15, color: C.text },
  toolsToggle: { fontFamily: F.semibold, fontSize: 15, color: C.primary },
  tool: { fontFamily: F.regular, fontSize: 15, color: C.text, paddingVertical: 5, borderTopWidth: 1, borderTopColor: C.line },
  hist: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: C.line },
});
