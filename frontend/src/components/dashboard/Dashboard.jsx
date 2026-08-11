import { Box, Stack, Typography } from '@mui/material'
import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { fetchTaskStats } from '../../features/tasks/tasksSlice'
import StatsCard from './StatsCard'
import TaskStats from './TaskStats'

export default function Dashboard() {
  const dispatch = useDispatch()
  const stats = useSelector((state) => state.tasks.stats)

  useEffect(() => {
    dispatch(fetchTaskStats())
  }, [dispatch])

  return (
    <Box>
      <Typography variant="h5" fontWeight={700} gutterBottom>
        Dashboard
      </Typography>

      {stats && (
        <Stack direction="row" spacing={2} flexWrap="wrap" sx={{ mb: 3 }}>
          <StatsCard label="Active tasks" value={stats.active_tasks} />
          <StatsCard label="Completed" value={stats.completed_tasks} accentColor="#0ca30c" />
          <StatsCard label="Overdue" value={stats.overdue_tasks} accentColor={stats.overdue_tasks > 0 ? '#d03b3b' : undefined} />
          <StatsCard label="Completion rate" value={`${Math.round(stats.completion_rate * 100)}%`} />
        </Stack>
      )}

      <TaskStats stats={stats} />
    </Box>
  )
}
