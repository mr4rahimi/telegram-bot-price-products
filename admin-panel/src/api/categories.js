import { client } from './client'

export const categoriesApi = {
  list: () => client.get('/api/categories').then(r => r.data),
  create: (data) => client.post('/api/categories', data).then(r => r.data),
  update: (id, data) => client.put(`/api/categories/${id}`, data).then(r => r.data),
  delete: (id) => client.delete(`/api/categories/${id}`),
}