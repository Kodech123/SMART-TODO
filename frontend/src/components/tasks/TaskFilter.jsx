import { MenuItem, Stack, TextField, ToggleButton, ToggleButtonGroup } from '@mui/material'
import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { fetchCategories } from '../../features/categories/categoriesSlice'
import { setFilters } from '../../features/tasks/tasksSlice'

export default function TaskFilter() {
  const dispatch = useDispatch()
  const filters = useSelector((state) => state.tasks.filters)
  const categories = useSelector((state) => state.categories.items)

  useEffect(() => {
    dispatch(fetchCategories())
  }, [dispatch])

  return (
    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems={{ sm: 'center' }} sx={{ mb: 2 }}>
      <ToggleButtonGroup
        exclusive
        size="small"
        value={filters.status}
        onChange={(_e, value) => value && dispatch(setFilters({ status: value }))}
      >
        <ToggleButton value="active">Active</ToggleButton>
        <ToggleButton value="completed">Completed</ToggleButton>
        <ToggleButton value="all">All</ToggleButton>
      </ToggleButtonGroup>

      <TextField
        select
        size="small"
        label="Category"
        value={filters.category ?? ''}
        onChange={(e) => dispatch(setFilters({ category: e.target.value || null }))}
        sx={{ minWidth: 160 }}
      >
        <MenuItem value="">All categories</MenuItem>
        {categories.map((category) => (
          <MenuItem key={category.category_id} value={category.category_name}>
            {category.category_name}
          </MenuItem>
        ))}
      </TextField>

      <TextField
        select
        size="small"
        label="Sort by"
        value={filters.sortBy}
        onChange={(e) => dispatch(setFilters({ sortBy: e.target.value }))}
        sx={{ minWidth: 160 }}
      >
        <MenuItem value="priority_score">Priority</MenuItem>
        <MenuItem value="due_date">Due date</MenuItem>
        <MenuItem value="created_at">Recently added</MenuItem>
      </TextField>
    </Stack>
  )
}
