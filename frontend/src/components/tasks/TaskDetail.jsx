import {
  Box,
  Chip,
  Dialog,
  DialogContent,
  DialogTitle,
  Divider,
  IconButton,
  LinearProgress,
  Stack,
  Typography,
} from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import { useDispatch, useSelector } from 'react-redux'
import { clearSelectedTask } from '../../features/tasks/tasksSlice'
import { colorForPriority, nameForPriority } from '../../utils/priorityColors'
import { formatDateTime } from '../../utils/dateUtils'

const SCORE_ROWS = [
  { key: 'urgency_score', label: 'Urgency', calcKey: 'urgency_calculation' },
  { key: 'importance_score', label: 'Importance', calcKey: 'importance_calculation' },
  { key: 'deadline_proximity_score', label: 'Deadline proximity', calcKey: 'deadline_proximity_calculation' },
  { key: 'effort_score', label: 'Effort', calcKey: 'effort_calculation' },
]

export default function TaskDetail() {
  const dispatch = useDispatch()
  const task = useSelector((state) => state.tasks.selectedTask)

  if (!task) return null

  const { scores } = task

  return (
    <Dialog open={Boolean(task)} onClose={() => dispatch(clearSelectedTask())} fullWidth maxWidth="sm">
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span>{task.title}</span>
        <IconButton onClick={() => dispatch(clearSelectedTask())} data-testid="close-task-detail">
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      <DialogContent>
        <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
          <Chip
            label={`${task.priority_label} - ${nameForPriority(task.priority_label)}`}
            sx={{ bgcolor: colorForPriority(task.priority_label), color: '#fff', fontWeight: 700 }}
          />
          {task.category && <Chip label={task.category} variant="outlined" />}
          <Chip label={task.status} variant="outlined" />
        </Stack>

        {task.description && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {task.description}
          </Typography>
        )}

        <Typography variant="body2" sx={{ mb: 2 }}>
          Due: {formatDateTime(task.due_date)}
        </Typography>

        <Divider sx={{ mb: 2 }} />

        <Typography variant="subtitle1" fontWeight={700} gutterBottom data-testid="priority-score">
          Priority score: {task.priority_score.toFixed(2)} / 10
        </Typography>

        <Stack spacing={1.5} sx={{ mt: 2 }}>
          {SCORE_ROWS.map((row) => (
            <Box key={row.key}>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="body2">{row.label}</Typography>
                <Typography variant="body2" fontWeight={600}>
                  {scores[row.key].toFixed(2)} / 10
                </Typography>
              </Stack>
              <LinearProgress variant="determinate" value={(scores[row.key] / 10) * 100} sx={{ height: 6, borderRadius: 3 }} />
              {scores.breakdown && (
                <Typography variant="caption" color="text.secondary">
                  {scores.breakdown[row.calcKey]}
                </Typography>
              )}
            </Box>
          ))}
        </Stack>

        {scores.breakdown && (
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2 }}>
            {scores.breakdown.final_calculation}
          </Typography>
        )}

        {task.reminder && (
          <>
            <Divider sx={{ my: 2 }} />
            <Typography variant="body2">
              Reminder ({task.reminder.status}): {formatDateTime(task.reminder.trigger_time)}
            </Typography>
          </>
        )}
      </DialogContent>
    </Dialog>
  )
}
