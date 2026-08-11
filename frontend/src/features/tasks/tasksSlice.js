import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import * as tasksApi from '../../api/tasksApi'

export const fetchTasks = createAsyncThunk('tasks/fetchAll', async (_args, { getState }) => {
  const { filters } = getState().tasks
  const data = await tasksApi.listTasks({
    status: filters.status,
    category: filters.category || undefined,
    sortBy: filters.sortBy,
  })
  return data
})

export const fetchTaskStats = createAsyncThunk('tasks/fetchStats', async () => tasksApi.getTaskStats())

export const fetchTaskDetail = createAsyncThunk('tasks/fetchDetail', async (taskId) => tasksApi.getTask(taskId))

export const createTask = createAsyncThunk('tasks/create', async (payload, { dispatch }) => {
  const task = await tasksApi.createTask(payload)
  dispatch(fetchTasks())
  dispatch(fetchTaskStats())
  return task
})

export const updateTask = createAsyncThunk('tasks/update', async ({ taskId, patch }, { dispatch }) => {
  const task = await tasksApi.updateTask(taskId, patch)
  dispatch(fetchTasks())
  dispatch(fetchTaskStats())
  return task
})

export const completeTask = createAsyncThunk('tasks/complete', async (taskId, { dispatch }) => {
  const result = await tasksApi.completeTask(taskId)
  dispatch(fetchTasks())
  dispatch(fetchTaskStats())
  return result
})

export const deleteTask = createAsyncThunk('tasks/delete', async (taskId, { dispatch }) => {
  await tasksApi.deleteTask(taskId)
  dispatch(fetchTasks())
  dispatch(fetchTaskStats())
  return taskId
})

const initialState = {
  items: [],
  selectedTask: null,
  stats: null,
  filters: {
    status: 'active',
    category: null,
    sortBy: 'priority_score',
  },
  isLoading: false,
  error: null,
  totalCount: 0,
}

const tasksSlice = createSlice({
  name: 'tasks',
  initialState,
  reducers: {
    setFilters(state, action) {
      state.filters = { ...state.filters, ...action.payload }
    },
    clearSelectedTask(state) {
      state.selectedTask = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchTasks.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(fetchTasks.fulfilled, (state, action) => {
        state.isLoading = false
        state.items = action.payload.tasks
        state.totalCount = action.payload.total_count
      })
      .addCase(fetchTasks.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.error.message
      })
      .addCase(fetchTaskStats.fulfilled, (state, action) => {
        state.stats = action.payload
      })
      .addCase(fetchTaskDetail.fulfilled, (state, action) => {
        state.selectedTask = action.payload
      })
  },
})

export const { setFilters, clearSelectedTask } = tasksSlice.actions
export default tasksSlice.reducer
