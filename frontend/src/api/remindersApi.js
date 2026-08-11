import axiosClient from './axiosClient'

export function listReminders({ status = 'pending', limit = 50, offset = 0 } = {}) {
  return axiosClient.get('/api/v1/reminders', { params: { status, limit, offset } }).then((res) => res.data)
}

export function snoozeReminder(reminderId, minutes) {
  return axiosClient
    .get(`/api/v1/reminders/${reminderId}/snooze`, { params: { minutes } })
    .then((res) => res.data)
}
