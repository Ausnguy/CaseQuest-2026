import { StyleSheet, View } from 'react-native';
import Svg, { Circle, G, Line, Rect, Text as SvgText } from 'react-native-svg';

import { BASE, HOME, SITES, type Job, type Vec } from '@dispatch/dispatch';
import { C, F, S } from '@/theme';

// Same schematic layout as the console's field map: six sites, the base in the middle, home off to the east.
export function FieldMap({ me, job, holdSites }: { me: Vec | null; job?: Job; holdSites: Set<string> }) {
  return (
    <View style={styles.map} accessibilityLabel={job ? `Field map with your route to site ${job.site}` : 'Field map'}>
      <Svg width="100%" height="100%" viewBox="-13 -9.6 31 19.2" preserveAspectRatio="xMidYMid meet">
        {SITES.map((s) => {
          const target = job?.site === s.id;
          const hold = holdSites.has(s.id);
          return (
            <G key={s.id}>
              <Rect x={s.pos[0] - 1.6} y={s.pos[1] - 1.1} width={3.2} height={2.2} rx={0.3}
                fill={hold ? '#4a1d24' : '#12392f'} stroke={target ? C.amber : hold ? C.red : C.teal} strokeWidth={target ? 0.25 : 0.08} />
              <SvgText x={s.pos[0]} y={s.pos[1] + 2.1} fontSize={0.95} fill={target ? C.amber : C.muted} textAnchor="middle" fontFamily={F.medium}>{s.name}</SvgText>
            </G>
          );
        })}
        <Rect x={-0.8} y={-0.8} width={1.6} height={1.6} transform="rotate(45)" fill="#2b2150" stroke={C.violet} strokeWidth={0.08} />
        <SvgText x={BASE.pos[0]} y={2} fontSize={0.8} fill={C.violet} textAnchor="middle" fontFamily={F.medium}>Base</SvgText>
        <SvgText x={HOME[0]} y={2} fontSize={0.8} fill={C.muted} textAnchor="middle" fontFamily={F.medium}>Off site</SvgText>
        {job?.leg && (
          <Line x1={job.leg.from[0]} y1={job.leg.from[1]} x2={job.leg.to[0]} y2={job.leg.to[1]} stroke={C.blue} strokeWidth={0.15} strokeDasharray="0.5 0.35" />
        )}
        {me && (
          <G>
            <Circle cx={me[0]} cy={me[1]} r={1.1} fill={C.teal} opacity={0.2} />
            <Circle cx={me[0]} cy={me[1]} r={0.5} fill={C.teal} stroke={C.bg} strokeWidth={0.12} />
          </G>
        )}
      </Svg>
    </View>
  );
}

const styles = StyleSheet.create({
  map: { height: 200, backgroundColor: '#0d1730', borderWidth: 1, borderColor: C.line, borderRadius: S.radius, overflow: 'hidden', padding: 4 },
});
