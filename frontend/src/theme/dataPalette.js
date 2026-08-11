// Validated data-viz palette (see dataviz skill reference/palette.md).
// Status roles map onto the four priority tiers (P1=critical .. P4=good) since
// priority labels are literally a severity scale.
export const STATUS_PALETTE = {
  critical: '#d03b3b',
  serious: '#ec835a',
  warning: '#fab219',
  good: '#0ca30c',
}

export const PRIORITY_STATUS_COLOR = {
  P1: STATUS_PALETTE.critical,
  P2: STATUS_PALETTE.serious,
  P3: STATUS_PALETTE.warning,
  P4: STATUS_PALETTE.good,
}

export const SEQUENTIAL_BLUE = {
  100: '#cde2fb',
  250: '#86b6ef',
  400: '#3987e5',
  500: '#256abf',
  700: '#0d366b',
}

export const CHART_INK = {
  primary: '#0b0b0b',
  secondary: '#52514e',
  muted: '#898781',
  gridline: '#e1e0d9',
  baseline: '#c3c2b7',
  surface: '#fcfcfb',
}
