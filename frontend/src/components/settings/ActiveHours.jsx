import { Stack, TextField, Typography } from '@mui/material'

export default function ActiveHours({ start, end, onChange }) {
  return (
    <Stack spacing={1}>
      <Typography variant="subtitle1" fontWeight={600}>
        Active hours
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Reminders are delivered within this window.
      </Typography>
      <Stack direction="row" spacing={2}>
        <TextField
          label="Start"
          type="time"
          value={start}
          onChange={(e) => onChange({ active_hours_start: e.target.value })}
          InputLabelProps={{ shrink: true }}
        />
        <TextField
          label="End"
          type="time"
          value={end}
          onChange={(e) => onChange({ active_hours_end: e.target.value })}
          InputLabelProps={{ shrink: true }}
        />
      </Stack>
    </Stack>
  )
}
