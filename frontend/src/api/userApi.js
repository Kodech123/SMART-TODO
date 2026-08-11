import axiosClient from './axiosClient'

export function getSettings() {
  return axiosClient.get('/api/v1/user/settings').then((res) => res.data)
}

export function updateSettings(patch) {
  return axiosClient.patch('/api/v1/user/settings', patch).then((res) => res.data)
}
