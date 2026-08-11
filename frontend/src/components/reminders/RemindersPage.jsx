import { Box, Button, ButtonGroup, List, ListItem, ListItemText, Paper, Typography } from '@mui/material'
import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { fetchReminders, snoozeReminder } from '../../features/reminders/remindersSlice'
import { formatDateTime } from '../../utils/dateUtils'

const SNOOZE_OPTIONS = [15, 30, 60, 120]

export default function RemindersPage() {
  const dispatch = useDispatch()
  const { items, isLoading } = useSelector((state) => state.reminders)

  useEffect(() => {
    dispatch(fetchReminders('pending'))
  }, [dispatch])

  return (
    <Box>
      <Typography variant="h5" fontWeight={700} gutterBottom>
        Upcoming reminders
      </Typography>

      <Paper variant="outlined">
        {!isLoading && items.length === 0 && (
          <Typography color="text.secondary" sx={{ p: 3, textAlign: 'center' }}>
            No pending reminders.
          </Typography>
        )}
        <List disablePadding>
          {items.map((reminder) => (
            <ListItem
              key={reminder.reminder_id}
              divider
              secondaryAction={
                <ButtonGroup size="small" variant="outlined">
                  {SNOOZE_OPTIONS.map((minutes) => (
                    <Button
                      key={minutes}
                      onClick={() => dispatch(snoozeReminder({ reminderId: reminder.reminder_id, minutes }))}
                    >
                      +{minutes}m
                    </Button>
                  ))}
                </ButtonGroup>
              }
            >
              <ListItemText
                primary={reminder.task_title}
                secondary={`${formatDateTime(reminder.trigger_time)} · ${reminder.time_until_delivery ?? ''}`}
              />
            </ListItem>
          ))}
        </List>
      </Paper>
    </Box>
  )
}
