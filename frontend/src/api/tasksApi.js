import axiosClient from './axiosClient'

export function listTasks({ status = 'active', category, sortBy = 'priority_score', limit = 50, offset = 0 } = {}) {
  return axiosClient
    .get('/api/v1/tasks', { params: { status, category, sort_by: sortBy, limit, offset } })
    .then((res) => res.data)
}

export function getTaskStats() {
  return axiosClient.get('/api/v1/tasks/stats').then((res) => res.data)
}

export function getTask(taskId) {
  return axiosClient.get(`/api/v1/tasks/${taskId}`).then((res) => res.data)
}

export function createTask(payload) {
  return axiosClient.post('/api/v1/tasks', payload).then((res) => res.data)
}

export function updateTask(taskId, patch) {
  return axiosClient.patch(`/api/v1/tasks/${taskId}`, patch).then((res) => res.data)
}

export function completeTask(taskId) {
  return axiosClient.put(`/api/v1/tasks/${taskId}/complete`).then((res) => res.data)
}

export function deleteTask(taskId) {
  return axiosClient.delete(`/api/v1/tasks/${taskId}`).then((res) => res.data)
}
