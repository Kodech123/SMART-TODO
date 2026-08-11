import { Paper, Stack, Typography } from '@mui/material'

export default function StatsCard({ label, value, accentColor }) {
  return (
    <Paper
      variant="outlined"
      sx={{ p: 2, flex: '1 1 160px', borderTop: accentColor ? `3px solid ${accentColor}` : undefined }}
    >
      <Stack spacing={0.5}>
        <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', letterSpacing: 0.5 }}>
          {label}
        </Typography>
        <Typography variant="h4" fontWeight={700} sx={{ fontVariantNumeric: 'tabular-nums' }}>
          {value}
        </Typography>
      </Stack>
    </Paper>
  )
}
