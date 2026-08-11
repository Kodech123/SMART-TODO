import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline'
import { Box, Card, CardContent, Checkbox, Chip, IconButton, Stack, Tooltip, Typography } from '@mui/material'
import { useDispatch } from 'react-redux'
import { completeTask, deleteTask } from '../../features/tasks/tasksSlice'
import { colorForPriority } from '../../utils/priorityColors'
import { daysRemainingLabel, formatDateTime } from '../../utils/dateUtils'

export default function TaskCard({ task, onClick }) {
  const dispatch = useDispatch()
  const isCompleted = task.status === 'completed'
  const isOverdue = !isCompleted && task.days_remaining < 0

  function handleComplete(event) {
    event.stopPropagation()
    dispatch(completeTask(task.task_id))
  }

  function handleDelete(event) {
    event.stopPropagation()
    dispatch(deleteTask(task.task_id))
  }

  return (
    <Card
      variant="outlined"
      onClick={onClick}
      data-testid="task-card"
      sx={{
        mb: 1.5,
        cursor: 'pointer',
        borderLeft: `4px solid ${colorForPriority(task.priority_label)}`,
        opacity: isCompleted ? 0.6 : 1,
        '&:hover': { boxShadow: 2 },
      }}
    >
      <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 1, '&:last-child': { pb: 2 } }}>
        <Checkbox checked={isCompleted} onClick={handleComplete} disabled={isCompleted} />
        <Box sx={{ flexGrow: 1, minWidth: 0 }}>
          <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
            <Chip
              label={task.priority_label}
              size="small"
              data-testid="priority-badge"
              sx={{ bgcolor: colorForPriority(task.priority_label), color: '#fff', fontWeight: 700 }}
            />
            {task.category && <Chip label={task.category} size="small" variant="outlined" />}
            <Typography
              variant="subtitle1"
              sx={{ textDecoration: isCompleted ? 'line-through' : 'none', fontWeight: 600 }}
            >
              {task.title}
            </Typography>
          </Stack>
          <Typography variant="body2" color={isOverdue ? 'error' : 'text.secondary'}>
            Due: {formatDateTime(task.due_date)} · {daysRemainingLabel(task.days_remaining)}
          </Typography>
        </Box>
        {!isCompleted && (
          <Tooltip title="Mark complete">
            <IconButton onClick={handleComplete} color="success">
              <CheckCircleOutlineIcon />
            </IconButton>
          </Tooltip>
        )}
        <Tooltip title="Delete">
          <IconButton onClick={handleDelete} color="default">
            <DeleteOutlineIcon />
          </IconButton>
        </Tooltip>
      </CardContent>
    </Card>
  )
}
