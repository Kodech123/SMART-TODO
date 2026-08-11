import axiosClient from './axiosClient'

export function listCategories() {
  return axiosClient.get('/api/v1/categories').then((res) => res.data)
}

export function createCategory(payload) {
  return axiosClient.post('/api/v1/categories', payload).then((res) => res.data)
}

export function updateCategory(categoryId, patch) {
  return axiosClient.patch(`/api/v1/categories/${categoryId}`, patch).then((res) => res.data)
}

export function deleteCategory(categoryId) {
  return axiosClient.delete(`/api/v1/categories/${categoryId}`).then((res) => res.data)
}
