import axios from 'axios'

const axiosClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
})

axiosClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('dosmart_access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

axiosClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('dosmart_access_token')
      if (!window.location.pathname.startsWith('/login')) {
        window.location.assign('/login')
      }
    }

    // FastAPI's error body is {"detail": "..."} for a single message (validation errors
    // instead carry an array under `detail`, which isn't a useful .message string, so
    // those are left as axios's generic "Request failed with status code NNN"). Without
    // this, every consumer of these thunks' rejected.error.message sees that generic
    // message instead of e.g. "Email already registered".
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') {
      error.message = detail
    }

    return Promise.reject(error)
  },
)

export default axiosClient
