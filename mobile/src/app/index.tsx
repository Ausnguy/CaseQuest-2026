import { useEffect, useState } from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
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

function whereText(state: DispatchState, job: Job | undefined, kmLeft: number) {
  const me = state.engineers.find((e) => e.id === ME);
  if (!me) return { label: 'Unknown', detail: '' };
  if (job?.leg && (job.status === 'en-route' || job.status === 'leaving')) {
    const to = job.status === 'en-route' ? siteById(job.site)?.name : BASE.name;
    return { label: 'Off site, on the road', detail: `${kmLeft.toFixed(1)} km to ${to}` };
  }
  if (me.at === BASE.id) return { label: 'Off site', detail: 'At the maintenance base' };
  if (me.at) return { label: 'On site', detail: siteById(me.at)?.name ?? me.at };
  return { label: 'Off site', detail: 'Away from all sites' };
}

function Travel({ job, kmLeft, done }: { job: Job; kmLeft: number; done: number }) {
  const shake = useStore((s) => s.shake);
  const act = useStore((s) => s.act);
  const busy = useStore((s) => s.busy);
  const startShake = useStore((s) => s.startShake);
  const auto = job.leg?.autoSince !== null;
  const to = job.status === 'en-route' ? siteById(job.site)?.name : BASE.name;
  return (
    <View style={{ gap: 10 }}>
      <KV label={`Distance to ${to}`} value={`${kmLeft.toFixed(1)} km`} />
      <Meter value={done} />
      {shake?.status === 'unavailable' ? (
        <Note tone="amber">This phone has no motion sensor. Use auto drive.</Note>
      ) : shake ? (
        <View style={styles.shakeBox}>
          <Text style={styles.shakeBig}>Shake your phone to drive</Text>
          <Text style={st.small}>{shake.count} {shake.count === 1 ? 'shake' : 'shakes'}. Each one is {SHAKE_KM} km. The manager sees you move.</Text>
        </View>
      ) : (
        <Btn label="Shake to drive" primary onPress={startShake} />
      )}
      <Btn label={auto ? 'Stop auto drive' : 'Auto drive instead'} disabled={busy} onPress={() => act({ type: 'autoTravel', engineerId: ME, on: !auto })} />
    </View>
  );
}

function JobCard({ state, job, now, kmLeft, legDone }: { state: DispatchState; job: Job; now: number; kmLeft: number; legDone: number }) {
  const act = useStore((s) => s.act);
  const busy = useStore((s) => s.busy);
  const site = siteById(job.site);
  const asset = assetById(job.asset);
  const parts = job.partsId ? state.parts.find((p) => p.id === job.partsId) : undefined;
  const partsIn = parts ? now >= parts.arriveAt : true;
  const due = now >= job.leaveAt;

  let headline = '';
  if (job.status === 'scheduled') headline = due ? 'Time to leave' : `Leave in ${countdown(job.leaveAt - now)}`;
  else if (job.status === 'en-route') headline = 'On the way';
  else if (job.status === 'on-site') headline = partsIn ? 'On site' : `Parts in ${countdown(parts!.arriveAt - now)}`;
  else if (job.status === 'working') headline = `Repairing, ${countdown(job.workStartAt! + WORK_S * 1000 - now)} left`;
  else if (job.status === 'done') headline = 'Repair done';
  else if (job.status === 'leaving') headline = 'Heading back to base';

  return (
    <Panel title={`Your job · ${job.id}`}>
      <Text style={styles.asset}>{job.asset} · {asset?.type}</Text>
      <Text style={st.small}>{site?.name} site</Text>
      {job.note ? (
        <View style={styles.check}>
          <Text style={styles.checkLabel}>What to check</Text>
          <Text style={st.body}>{job.note}</Text>
        </View>
      ) : null}
      {job.hseHold ? (
        <View style={{ marginTop: 10 }}>
          <Note tone="red">HSE HOLD at {site?.name}: {job.hseHold}. Follow site isolation and gas checks before work.</Note>
        </View>
      ) : null}

      <Text style={[styles.headline, job.status === 'scheduled' && due && { color: C.teal }]}>{headline}</Text>

      <View style={{ gap: 2, marginBottom: 12 }}>
        {parts ? (
          <KV label={parts.kit} value={partsIn ? 'On site' : `Arrives in ${countdown(parts.arriveAt - now)}`} tone={partsIn ? 'ok' : 'warn'} />
        ) : (
          <KV label="Parts" value="None needed" />
        )}
        {job.status === 'scheduled' && parts && !due ? (
          <Text style={st.small}>Dispatch timed your departure so you arrive as the parts land, with no waiting on site.</Text>
        ) : null}
      </View>

      {job.status === 'scheduled' && (
        <Btn label={due ? 'Set off' : 'Set off early'} primary={due} disabled={busy} onPress={() => act({ type: 'depart', jobId: job.id, engineerId: ME })} />
      )}
      {(job.status === 'en-route' || job.status === 'leaving') && <Travel job={job} kmLeft={kmLeft} done={legDone} />}
      {job.status === 'on-site' && !partsIn && <Note tone="amber">You are early. The repair starts on its own when the parts arrive.</Note>}
      {job.status === 'working' && <Meter value={(now - job.workStartAt!) / (WORK_S * 1000)} color={C.amber} />}
      {job.status === 'done' && <Btn label="Leave site" primary disabled={busy} onPress={() => act({ type: 'leave', jobId: job.id, engineerId: ME })} />}
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
  const where = whereText(state, job, kmLeft);
  const history = state.jobs.filter((j) => j.engineerId === ME && !isActive(j)).reverse().slice(0, 6);

  return (
    <SafeAreaView edges={['top']} style={{ flex: 1, backgroundColor: C.bg }}>
      <View style={styles.top}>
        <View>
          <Text style={styles.brand}>Lone Mesa Field</Text>
          <Text style={st.small}>{me?.name ?? ME}</Text>
        </View>
        <Text style={[styles.link, { color: link === 'live' ? C.green : C.red }]}>{link === 'live' ? '● live' : '● offline'}</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: S.gutter, gap: S.gap, paddingBottom: 40 }}>
        {error ? <Note tone="red">{error}</Note> : null}
        <View style={styles.where}>
          <Text style={styles.whereLabel}>{where.label}</Text>
          <Text style={st.small}>{where.detail}</Text>
        </View>
        <FieldMap me={pos} job={job} holdSites={job?.hseHold ? new Set([job.site]) : new Set()} />
        {job ? (
          <JobCard state={state} job={job} now={now} kmLeft={kmLeft} legDone={legDone} />
        ) : (
          <Panel title="Your job">
            <Text style={st.body}>No job right now. When the manager requests you, this phone buzzes and the job shows here with the time to leave.</Text>
          </Panel>
        )}
        <Panel title="Done today">
          {history.length === 0 ? <Text style={st.small}>Nothing yet.</Text> : history.map((j) => (
            <View key={j.id} style={styles.hist}>
              <Text style={[st.body, { flex: 1 }]}>{j.id} · {j.asset} · {siteById(j.site)?.name}</Text>
              <Text style={[st.small, { color: j.status === 'closed' ? C.green : C.muted }]}>{j.status === 'closed' ? 'Repaired' : 'Cancelled'}</Text>
            </View>
          ))}
        </Panel>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, backgroundColor: C.bg, alignItems: 'center', justifyContent: 'center', gap: 6 },
  top: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: S.gutter, paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: C.line },
  brand: { fontFamily: F.displayBold, fontSize: 18, color: C.text, letterSpacing: 0.3 },
  link: { fontFamily: F.semibold, fontSize: 12 },
  where: { paddingVertical: 2 },
  whereLabel: { fontFamily: F.displayBold, fontSize: 28, color: C.text },
  asset: { fontFamily: F.display, fontSize: 22, color: C.text },
  headline: { fontFamily: F.displayBold, fontSize: 24, color: C.amber, marginTop: 14, marginBottom: 8, fontVariant: ['tabular-nums'] },
  check: { borderLeftWidth: 3, borderLeftColor: C.amber, backgroundColor: C.panel2, borderRadius: S.radiusS, padding: 10, marginTop: 12 },
  checkLabel: { fontFamily: F.semibold, fontSize: 12, color: C.muted, marginBottom: 2 },
  shakeBox: { gap: 6, padding: 12, borderRadius: S.radiusS, backgroundColor: C.tealBg, borderWidth: 1, borderColor: '#1d5a52' },
  shakeBig: { fontFamily: F.displayBold, fontSize: 20, color: C.teal },
  hist: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: C.line },
});
