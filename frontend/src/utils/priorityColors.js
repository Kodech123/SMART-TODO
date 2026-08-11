import { PRIORITY_COLORS, PRIORITY_LABELS } from '../theme/theme'

export function colorForPriority(label) {
  return PRIORITY_COLORS[label] ?? PRIORITY_COLORS.P4
}

export function nameForPriority(label) {
  return PRIORITY_LABELS[label] ?? label
}
