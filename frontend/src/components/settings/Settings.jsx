import { Divider, Paper, Stack, Typography } from '@mui/material'
import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import * as userApi from '../../api/userApi'
import { showToast } from '../../features/ui/uiSlice'
import ActiveHours from './ActiveHours'
import ReminderSettings from './ReminderSettings'

export default function Settings() {
  const dispatch = useDispatch()
  const [settings, setSettings] = useState(null)

  useEffect(() => {
    userApi.getSettings().then(setSettings)
  }, [])

  async function handleChange(patch) {
    const updated = await userApi.updateSettings(patch)
    setSettings(updated)
    dispatch(showToast('Settings saved'))
  }

  if (!settings) return null

  return (
    <Paper variant="outlined" sx={{ p: 3, maxWidth: 480 }}>
      <Typography variant="h5" fontWeight={700} gutterBottom>
        Settings
      </Typography>

      <Stack spacing={3} sx={{ mt: 2 }}>
        <ActiveHours
          start={settings.active_hours_start.slice(0, 5)}
          end={settings.active_hours_end.slice(0, 5)}
          onChange={handleChange}
        />
        <Divider />
        <ReminderSettings
          defaultReminderMinutes={settings.default_reminder_minutes}
          notificationOptIn={settings.notification_opt_in}
          onChange={handleChange}
        />
      </Stack>
    </Paper>
  )
}
