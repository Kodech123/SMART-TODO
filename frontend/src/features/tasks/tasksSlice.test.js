import { describe, expect, it } from 'vitest'
import reducer, { fetchTaskDetail, fetchTasks, setFilters } from './tasksSlice'

describe('tasksSlice', () => {
  it('has sensible initial filters', () => {
    const state = reducer(undefined, { type: '@@INIT' })
    expect(state.filters).toEqual({ status: 'active', category: null, sortBy: 'priority_score' })
    expect(state.items).toEqual([])
  })

  it('setFilters merges into existing filters without clobbering other keys', () => {
    const state = reducer(undefined, setFilters({ category: 'Academic' }))
    expect(state.filters).toEqual({ status: 'active', category: 'Academic', sortBy: 'priority_score' })
  })

  it('fetchTasks.fulfilled stores the returned tasks and total count', () => {
    const payload = {
      tasks: [{ task_id: 1, title: 'Task A', priority_score: 8, priority_label: 'P1' }],
      total_count: 1,
    }
    const state = reducer(undefined, fetchTasks.fulfilled(payload, 'requestId'))

    expect(state.items).toHaveLength(1)
    expect(state.totalCount).toBe(1)
    expect(state.isLoading).toBe(false)
  })

  it('fetchTasks.pending sets isLoading and clears the previous error', () => {
    const state = reducer({ items: [], filters: {}, isLoading: false, error: 'old error', totalCount: 0 }, fetchTasks.pending('id'))
    expect(state.isLoading).toBe(true)
    expect(state.error).toBeNull()
  })

  it('fetchTaskDetail.fulfilled sets the selected task', () => {
    const task = { task_id: 5, title: 'Detail task' }
    const state = reducer(undefined, fetchTaskDetail.fulfilled(task, 'id', 5))
    expect(state.selectedTask).toEqual(task)
  })
})
