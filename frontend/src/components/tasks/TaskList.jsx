import AddIcon from '@mui/icons-material/Add'
import { Box, Chip, Fab, Stack, Typography } from '@mui/material'
import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { fetchTaskDetail, fetchTasks, fetchTaskStats } from '../../features/tasks/tasksSlice'
import { openTaskForm } from '../../features/ui/uiSlice'
import TaskCard from './TaskCard'
import TaskDetail from './TaskDetail'
import TaskFilter from './TaskFilter'
import TaskForm from './TaskForm'

export default function TaskList() {
  const dispatch = useDispatch()
  const { items, isLoading, filters, stats } = useSelector((state) => state.tasks)

  useEffect(() => {
    dispatch(fetchTasks())
  }, [dispatch, filters])

  useEffect(() => {
    dispatch(fetchTaskStats())
  }, [dispatch])

  return (
    <Box>
      {stats && (
        <Stack direction="row" spacing={1} sx={{ mb: 2 }} flexWrap="wrap">
          <Chip label={`Tasks: ${stats.total_tasks}`} />
          <Chip label={`P1: ${stats.priority_distribution.P1}`} color="error" variant="outlined" />
          <Chip label={`P2: ${stats.priority_distribution.P2}`} color="warning" variant="outlined" />
          <Chip label={`Completed: ${stats.completed_tasks} (${Math.round(stats.completion_rate * 100)}%)`} color="success" variant="outlined" />
          {stats.overdue_tasks > 0 && <Chip label={`Overdue: ${stats.overdue_tasks}`} color="error" />}
        </Stack>
      )}

      <TaskFilter />

      {!isLoading && items.length === 0 && (
        <Typography color="text.secondary" sx={{ mt: 4, textAlign: 'center' }}>
          No tasks yet. Create one to get started.
        </Typography>
      )}

      {items.map((task) => (
        <TaskCard key={task.task_id} task={task} onClick={() => dispatch(fetchTaskDetail(task.task_id))} />
      ))}

      <Fab
        color="primary"
        aria-label="add task"
        data-testid="add-task-btn"
        sx={{ position: 'fixed', bottom: 32, right: 32 }}
        onClick={() => dispatch(openTaskForm())}
      >
        <AddIcon />
      </Fab>

      <TaskForm />
      <TaskDetail />
    </Box>
  )
}
