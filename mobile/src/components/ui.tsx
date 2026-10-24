import type { ReactNode } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { C, F, S } from '@/theme';

export function Panel({ title, aside, children }: { title: string; aside?: ReactNode; children: ReactNode }) {
  return (
    <View style={styles.panel}>
      <View style={styles.panelHead}>
        <Text style={st.label}>{title}</Text>
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
      <Text style={[styles.btnText, primary && { color: C.primaryInk }]}>{label}</Text>
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

export function Meter({ value, color = C.primary }: { value: number; color?: string }) {
  return (
    <View style={styles.meter} accessibilityRole="progressbar" accessibilityValue={{ min: 0, max: 100, now: Math.round(value * 100) }}>
      <View style={{ height: 6, width: `${Math.min(1, Math.max(0, value)) * 100}%`, backgroundColor: color }} />
    </View>
  );
}

export function Note({ tone, children }: { tone: 'amber' | 'red' | 'blue'; children: ReactNode }) {
  const t = { amber: [C.amberBg, C.amber], red: [C.redBg, C.red], blue: [C.primaryBg, C.primary] }[tone];
  return (
    <View style={[styles.note, { backgroundColor: t[0], borderLeftColor: t[1] }]}>
      <Text style={styles.noteText}>{children}</Text>
    </View>
  );
}

export const st = StyleSheet.create({
  body: { fontFamily: F.regular, fontSize: 16, lineHeight: 22, color: C.text },
  small: { fontFamily: F.regular, fontSize: 14, lineHeight: 19, color: C.muted },
  big: { fontFamily: F.displayBold, fontSize: 28, color: C.text },
  label: { fontFamily: F.mono, fontSize: 11, letterSpacing: 1, textTransform: 'uppercase', color: C.muted },
});

const styles = StyleSheet.create({
  panel: { backgroundColor: C.panel, borderWidth: 1, borderColor: C.line, borderRadius: S.radius, padding: 14 },
  panelHead: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 },
  btn: { minHeight: 52, borderRadius: S.radiusS, borderWidth: 1, borderColor: C.hair, backgroundColor: C.panel, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 14 },
  btnPrimary: { backgroundColor: C.primary, borderColor: C.primary },
  btnText: { fontFamily: F.display, fontSize: 18, letterSpacing: 0.4, color: C.text },
  kv: { flexDirection: 'row', justifyContent: 'space-between', gap: 12, paddingVertical: 7, borderBottomWidth: 1, borderBottomColor: C.line },
  kvLabel: { fontFamily: F.regular, fontSize: 15, color: C.text, flexShrink: 1 },
  kvValue: { fontFamily: F.semibold, fontSize: 15, fontVariant: ['tabular-nums'], textAlign: 'right' },
  meter: { height: 6, backgroundColor: C.panel2, overflow: 'hidden' },
  note: { borderLeftWidth: 3, padding: 10 },
  noteText: { fontFamily: F.regular, fontSize: 14, lineHeight: 19, color: C.text },
});
