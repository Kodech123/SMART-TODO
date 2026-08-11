import axiosClient from './axiosClient'

export function subscribe(subscription) {
  return axiosClient.post('/api/v1/push/subscribe', { subscription }).then((res) => res.data)
}

export function unsubscribe(endpoint) {
  return axiosClient.post('/api/v1/push/unsubscribe', { endpoint }).then((res) => res.data)
}
