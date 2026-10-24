import { StyleSheet, View } from 'react-native';
import Svg, { Circle, G, Line, Rect, Text as SvgText } from 'react-native-svg';

import { BASE, HOME, SITES, type Job, type PartsOrder, type Vec } from '@dispatch/dispatch';
import { C, F, S } from '@/theme';

// Where parts orders ship from on the console's 3D map.
export const WAREHOUSE: Vec = [-17, 0];

// Same schematic layout as the console's field map: six sites, the base in the middle, home off to the east.
// Labels are drawn at 10x and scaled down: Android mangles letter spacing at font sizes below 1.
export function FieldMap({ me, job, holdSites, parts, now }: { me: Vec | null; job?: Job; holdSites: Set<string>; parts?: PartsOrder; now: number }) {
  const truck = parts && now < parts.arriveAt ? truckPos(parts, now) : null;
  const target = job ? SITES.find((s) => s.id === job.site) : undefined;
  return (
    <View style={styles.map} accessibilityLabel={job ? `Field map with your route to ${target?.name}` : 'Field map'}>
      <Svg width="100%" height="100%" viewBox="-18.8 -9.4 37 18.8" preserveAspectRatio="xMidYMid meet">
        {SITES.map((s) => {
          const isTarget = job?.site === s.id;
          const hold = holdSites.has(s.id);
          return (
            <G key={s.id}>
              <Rect x={s.pos[0] - 1.9} y={s.pos[1] - 1.3} width={3.8} height={2.6}
                fill={hold ? C.redBg : C.panel} stroke={isTarget ? C.primary : hold ? C.red : C.hair} strokeWidth={isTarget ? 0.28 : 0.08} />
              {[0, 1, 2].map((i) => <Rect key={i} x={s.pos[0] - 1.35 + i * 1} y={s.pos[1] - 0.55} width={0.7} height={0.7} fill={isTarget && i === assetIndex(job) ? C.amber : C.muted} />)}
              <SvgText transform="scale(0.1)" x={s.pos[0] * 10} y={(s.pos[1] + 2.35) * 10} fontSize={11} fill={isTarget ? C.primary : C.muted} textAnchor="middle" fontFamily={F.semibold}>{s.name}</SvgText>
            </G>
          );
        })}
        <Rect x={-0.8} y={-0.8} width={1.6} height={1.6} transform="rotate(45)" fill={C.panel2} stroke={C.text} strokeWidth={0.08} />
        <SvgText transform="scale(0.1)" x={BASE.pos[0] * 10} y={22} fontSize={9.5} fill={C.text} textAnchor="middle" fontFamily={F.mono}>BASE</SvgText>
        <SvgText transform="scale(0.1)" x={HOME[0] * 10} y={22} fontSize={9.5} fill={C.muted} textAnchor="middle" fontFamily={F.mono}>OFF SITE</SvgText>
        <Rect x={WAREHOUSE[0] - 0.9} y={-0.7} width={1.8} height={1.4} fill={C.panel2} stroke={C.hair} strokeWidth={0.08} />
        <SvgText transform="scale(0.1)" x={WAREHOUSE[0] * 10} y={22} fontSize={9.5} fill={C.muted} textAnchor="middle" fontFamily={F.mono}>PARTS</SvgText>
        {truck && target && (
          <G>
            <Line x1={truck[0]} y1={truck[1]} x2={target.pos[0]} y2={target.pos[1]} stroke={C.amber} strokeWidth={0.12} strokeDasharray="0.4 0.3" />
            <Rect x={truck[0] - 0.55} y={truck[1] - 0.35} width={1.1} height={0.7} fill={C.amber} />
          </G>
        )}
        {job?.leg && (job.status === 'en-route' || job.status === 'leaving') && (
          <Line x1={job.leg.from[0]} y1={job.leg.from[1]} x2={job.leg.to[0]} y2={job.leg.to[1]} stroke={C.primary} strokeWidth={0.16} strokeDasharray="0.5 0.35" />
        )}
        {me && (
          <G>
            <Circle cx={me[0]} cy={me[1]} r={1.2} fill={C.primary} opacity={0.18} />
            <Circle cx={me[0]} cy={me[1]} r={0.55} fill={C.primary} stroke={C.panel} strokeWidth={0.14} />
          </G>
        )}
      </Svg>
    </View>
  );
}

function assetIndex(job?: Job) {
  if (!job) return -1;
  return (Number(job.asset.slice(1)) - 1) % 3;
}

function truckPos(p: PartsOrder, now: number): Vec {
  const site = SITES.find((s) => s.id === p.site)!;
  const f = Math.min(1, Math.max(0, (now - p.orderedAt) / (p.arriveAt - p.orderedAt)));
  return [WAREHOUSE[0] + (site.pos[0] - WAREHOUSE[0]) * f, WAREHOUSE[1] + (site.pos[1] - WAREHOUSE[1]) * f];
}

const styles = StyleSheet.create({
  map: { height: 190, backgroundColor: C.bg, borderWidth: 1, borderColor: C.line, borderRadius: S.radius, overflow: 'hidden', padding: 4 },
});
