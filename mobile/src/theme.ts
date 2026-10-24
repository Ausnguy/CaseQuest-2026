// Parvius "Industry" tokens, matching the manager's console: ink on paper, red for blocked or stopped,
// amber for early warning, green for cleared, blue for the engineer and anything in motion.
export const C = {
  bg: '#f2f2f3',
  panel: '#ffffff',
  panel2: '#e9e9ea',
  line: '#d4d4d7',
  hair: '#b7b7ba',
  text: '#1d1f20',
  muted: '#5d5d60',
  primary: '#41678c',
  primaryInk: '#ffffff',
  primaryBg: '#e5ecf3',
  amber: '#94600f',
  amberBg: '#f7eedd',
  amberLine: '#d6ad66',
  red: '#b7282a',
  redBg: '#f9e7e6',
  redLine: '#e3a5a4',
  green: '#1e7f4f',
  greenBg: '#e3f1e9',
};

// Barlow Condensed for headings and the numbers people glance at, Barlow for reading, Plex Mono for labels.
export const F = {
  regular: 'Barlow_400Regular',
  medium: 'Barlow_500Medium',
  semibold: 'Barlow_600SemiBold',
  display: 'BarlowCondensed_600SemiBold',
  displayBold: 'BarlowCondensed_700Bold',
  mono: 'IBMPlexMono_500Medium',
};

export const S = { gutter: 16, gap: 12, radius: 2, radiusS: 2 };

export function countdown(ms: number) {
  const s = Math.max(0, Math.ceil(ms / 1000));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
}
