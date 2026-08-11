import axiosClient from './axiosClient'

export function register({ email, password, displayName }) {
  return axiosClient
    .post('/api/v1/auth/register', { email, password, display_name: displayName })
    .then((res) => res.data)
}

export function login({ email, password }) {
  return axiosClient.post('/api/v1/auth/login', { email, password }).then((res) => res.data)
}

export function logout() {
  return axiosClient.post('/api/v1/auth/logout').then((res) => res.data)
}
