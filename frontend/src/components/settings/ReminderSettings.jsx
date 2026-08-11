import { Alert, Button, FormControlLabel, Slider, Stack, Switch, Typography } from '@mui/material'
import { usePushSubscription } from '../../hooks/usePushSubscription'

export default function ReminderSettings({ defaultReminderMinutes, notificationOptIn, onChange }) {
  const { subscribe, status, error } = usePushSubscription()

  return (
    <Stack spacing={2}>
      <Typography variant="subtitle1" fontWeight={600}>
        Notifications
      </Typography>

      <FormControlLabel
        control={
          <Switch
            checked={notificationOptIn}
            onChange={(e) => onChange({ notification_opt_in: e.target.checked })}
          />
        }
        label="Enable reminder notifications"
      />

      <Stack sx={{ maxWidth: 360 }}>
        <Typography variant="body2" gutterBottom>
          Default reminder offset: {defaultReminderMinutes} minutes before due time
        </Typography>
        <Slider
          value={defaultReminderMinutes}
          min={5}
          max={180}
          step={5}
          valueLabelDisplay="auto"
          onChangeCommitted={(_e, value) => onChange({ default_reminder_minutes: value })}
        />
      </Stack>

      <Stack spacing={1} sx={{ maxWidth: 360 }}>
        <Button variant="outlined" onClick={subscribe} disabled={status === 'subscribing' || status === 'subscribed'}>
          {status === 'subscribed' ? 'Push notifications enabled' : 'Enable browser push notifications'}
        </Button>
        {error && <Alert severity="warning">{error}</Alert>}
      </Stack>
    </Stack>
  )
}
