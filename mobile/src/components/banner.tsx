import { useEffect } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { useStore } from '@/state/store';
import { C, F, S } from '@/theme';

const AUTO_HIDE_MS = 8000;

export function Banner() {
  const banner = useStore((s) => s.banner);
  const dismiss = useStore((s) => s.dismissBanner);
  const insets = useSafeAreaInsets();
  useEffect(() => {
    if (!banner) return;
    const id = setTimeout(dismiss, AUTO_HIDE_MS);
    return () => clearTimeout(id);
  }, [banner, dismiss]);
  if (!banner) return null;
  const color = banner.tone === 'go' ? C.teal : banner.tone === 'error' ? C.red : C.amber;
  return (
    <View style={[styles.wrap, { top: insets.top + 8 }]} accessibilityLiveRegion="assertive">
      <Pressable onPress={dismiss} accessibilityRole="button" accessibilityHint="Dismisses the alert" style={[styles.card, { borderLeftColor: color }]}>
        <Text style={[styles.title, { color }]}>{banner.title}</Text>
        <Text style={styles.body}>{banner.body}</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { position: 'absolute', left: S.gutter, right: S.gutter },
  card: { backgroundColor: '#050a14', borderWidth: 1, borderColor: C.line, borderLeftWidth: 4, borderRadius: S.radiusS, padding: 12, elevation: 8 },
  title: { fontFamily: F.display, fontSize: 17 },
  body: { fontFamily: F.regular, fontSize: 14, lineHeight: 19, color: C.text, marginTop: 2 },
});
