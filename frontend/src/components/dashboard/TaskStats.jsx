import { Box, Paper, Stack, Typography } from '@mui/material'
import dayjs from 'dayjs'
import { CHART_INK, PRIORITY_STATUS_COLOR, SEQUENTIAL_BLUE } from '../../theme/dataPalette'
import { nameForPriority } from '../../utils/priorityColors'

const PRIORITY_ORDER = ['P1', 'P2', 'P3', 'P4']

function PriorityDistributionChart({ distribution }) {
  const total = PRIORITY_ORDER.reduce((sum, key) => sum + (distribution[key] ?? 0), 0)
  const width = 400
  const height = 28
  const gap = 2

  let x = 0
  const segments = []
  if (total > 0) {
    PRIORITY_ORDER.forEach((key, index) => {
      const count = distribution[key] ?? 0
      if (count === 0) return
      const segmentWidth = (count / total) * width - (PRIORITY_ORDER.length > 1 ? gap : 0)
      segments.push({ key, count, x, width: Math.max(segmentWidth, 0), isFirst: index === 0 })
      x += segmentWidth + gap
    })
  }

  return (
    <Box>
      <Typography variant="subtitle2" gutterBottom>
        Priority distribution
      </Typography>
      {total === 0 ? (
        <Typography variant="body2" color="text.secondary">
          No active tasks yet.
        </Typography>
      ) : (
        <>
          <svg width="100%" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Active tasks by priority tier">
            {segments.map((segment) => (
              <rect
                key={segment.key}
                x={segment.x}
                y={0}
                width={segment.width}
                height={height}
                rx={4}
                fill={PRIORITY_STATUS_COLOR[segment.key]}
              >
                <title>
                  {nameForPriority(segment.key)} ({segment.key}): {segment.count}
                </title>
              </rect>
            ))}
          </svg>
          <Stack direction="row" spacing={2} flexWrap="wrap" sx={{ mt: 1 }}>
            {PRIORITY_ORDER.map((key) => (
              <Stack key={key} direction="row" spacing={0.5} alignItems="center">
                <Box sx={{ width: 10, height: 10, borderRadius: '2px', bgcolor: PRIORITY_STATUS_COLOR[key] }} />
                <Typography variant="caption" color="text.secondary">
                  {key} {nameForPriority(key)}: {distribution[key] ?? 0}
                </Typography>
              </Stack>
            ))}
          </Stack>
        </>
      )}
    </Box>
  )
}

function ProductivityTrendChart({ dailyCompletions }) {
  const width = 400
  const height = 120
  const gap = 3
  const barWidth = (width - gap * (dailyCompletions.length - 1)) / dailyCompletions.length
  const maxCount = Math.max(1, ...dailyCompletions.map((d) => d.count))

  return (
    <Box>
      <Typography variant="subtitle2" gutterBottom>
        Tasks completed, last 7 days
      </Typography>
      <svg width="100%" viewBox={`0 0 ${width} ${height + 20}`} role="img" aria-label="Tasks completed per day, last 7 days">
        <line x1={0} y1={height} x2={width} y2={height} stroke={CHART_INK.baseline} strokeWidth={1} />
        {dailyCompletions.map((day, index) => {
          const barHeight = (day.count / maxCount) * (height - 8)
          const x = index * (barWidth + gap)
          const y = height - barHeight
          return (
            <g key={day.date}>
              <rect x={x} y={y} width={barWidth} height={Math.max(barHeight, 1)} rx={4} fill={SEQUENTIAL_BLUE[400]}>
                <title>
                  {dayjs(day.date).format('ddd, MMM D')}: {day.count} completed
                </title>
              </rect>
              {day.count > 0 && (
                <text x={x + barWidth / 2} y={y - 4} textAnchor="middle" fontSize="10" fill={CHART_INK.secondary}>
                  {day.count}
                </text>
              )}
              <text
                x={x + barWidth / 2}
                y={height + 14}
                textAnchor="middle"
                fontSize="10"
                fill={CHART_INK.muted}
              >
                {dayjs(day.date).format('dd')[0]}
              </text>
            </g>
          )
        })}
      </svg>
    </Box>
  )
}

export default function TaskStats({ stats }) {
  if (!stats) return null

  return (
    <Paper variant="outlined" sx={{ p: 3 }}>
      <Stack spacing={3}>
        <PriorityDistributionChart distribution={stats.priority_distribution} />
        <ProductivityTrendChart dailyCompletions={stats.daily_completions} />
      </Stack>
    </Paper>
  )
}
