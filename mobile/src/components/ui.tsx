import type { ReactNode } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { C, F, S } from '@/theme';

export function Panel({ title, aside, children }: { title: string; aside?: ReactNode; children: ReactNode }) {
  return (
    <View style={styles.panel}>
      <View style={styles.panelHead}>
        <Text style={styles.panelTitle}>{title}</Text>
        {aside}
      </View>
      {children}
    </View>
  );
}

export function Btn({ label, onPress, primary, disabled }: { label: string; onPress: () => void; primary?: boolean; disabled?: boolean }) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityState={{ disabled }}
      disabled={disabled}
      onPress={onPress}
      style={({ pressed }) => [styles.btn, primary && styles.btnPrimary, disabled && { opacity: 0.45 }, pressed && { opacity: 0.8 }]}
    >
      <Text style={[styles.btnText, primary && { color: C.tealInk }]}>{label}</Text>
    </Pressable>
  );
}

export function KV({ label, value, tone }: { label: string; value: string; tone?: 'ok' | 'warn' | 'bad' }) {
  const color = tone === 'ok' ? C.green : tone === 'warn' ? C.amber : tone === 'bad' ? C.red : C.text;
  return (
    <View style={styles.kv}>
      <Text style={styles.kvLabel}>{label}</Text>
      <Text style={[styles.kvValue, { color }]}>{value}</Text>
    </View>
  );
}

export function Meter({ value, color = C.teal }: { value: number; color?: string }) {
  return (
    <View style={styles.meter} accessibilityRole="progressbar" accessibilityValue={{ min: 0, max: 100, now: Math.round(value * 100) }}>
      <View style={{ height: 6, width: `${Math.min(1, Math.max(0, value)) * 100}%`, backgroundColor: color }} />
    </View>
  );
}

export function Note({ tone, children }: { tone: 'amber' | 'red' | 'teal'; children: ReactNode }) {
  const t = { amber: [C.amberBg, C.amberLine, '#ffe9a8'], red: [C.redBg, C.redLine, '#ffc5c5'], teal: [C.tealBg, '#1d5a52', '#aaf0e3'] }[tone];
  return (
    <View style={[styles.note, { backgroundColor: t[0], borderColor: t[1] }]}>
      <Text style={[styles.noteText, { color: t[2] }]}>{children}</Text>
    </View>
  );
}

export const st = StyleSheet.create({
  body: { fontFamily: F.regular, fontSize: 15, lineHeight: 21, color: C.text },
  small: { fontFamily: F.regular, fontSize: 13, lineHeight: 18, color: C.muted },
  big: { fontFamily: F.displayBold, fontSize: 26, color: C.text },
});

const styles = StyleSheet.create({
  panel: { backgroundColor: C.panel, borderWidth: 1, borderColor: C.line, borderRadius: S.radius, padding: 14 },
  panelHead: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 },
  panelTitle: { fontFamily: F.semibold, fontSize: 12, letterSpacing: 0.8, textTransform: 'uppercase', color: C.muted },
  btn: { minHeight: 48, borderRadius: S.radiusS, borderWidth: 1, borderColor: C.line, backgroundColor: C.panel2, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 14 },
  btnPrimary: { backgroundColor: C.teal, borderColor: C.teal },
  btnText: { fontFamily: F.semibold, fontSize: 16, color: C.text },
  kv: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 4 },
  kvLabel: { fontFamily: F.regular, fontSize: 14, color: C.muted },
  kvValue: { fontFamily: F.display, fontSize: 15, fontVariant: ['tabular-nums'] },
  meter: { height: 6, borderRadius: 3, backgroundColor: C.panel2, overflow: 'hidden' },
  note: { borderWidth: 1, borderRadius: S.radiusS, padding: 10 },
  noteText: { fontFamily: F.regular, fontSize: 13, lineHeight: 18 },
});
