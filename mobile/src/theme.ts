// Same tokens as the Gate Console so the phone and the manager's screen read as one product.
export const C = {
  bg: '#0a111f',
  panel: '#111b30',
  panel2: '#16233f',
  line: '#243456',
  text: '#e8eefb',
  muted: '#92a3c4',
  teal: '#2dd4bf',
  tealInk: '#04201c',
  tealBg: '#0f2a27',
  amber: '#fbbf24',
  amberBg: '#2a2410',
  amberLine: '#6b5a1f',
  red: '#f87171',
  redBg: '#2a1216',
  redLine: '#6b2a33',
  blue: '#60a5fa',
  violet: '#a78bfa',
  green: '#4ade80',
};

// Archivo for headings and the numbers people glance at, IBM Plex Sans for reading.
export const F = {
  regular: 'IBMPlexSans_400Regular',
  medium: 'IBMPlexSans_500Medium',
  semibold: 'IBMPlexSans_600SemiBold',
  display: 'Archivo_700Bold',
  displayBold: 'Archivo_800ExtraBold',
};

export const S = { gutter: 16, gap: 12, radius: 12, radiusS: 8 };

export function countdown(ms: number) {
  const s = Math.max(0, Math.ceil(ms / 1000));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
}
