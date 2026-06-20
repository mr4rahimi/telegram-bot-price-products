import { client } from './client'

export const productsApi = {
  list: (categoryId) => {
    const params = categoryId ? { category_id: categoryId } : {}
    return client.get('/api/products', { params }).then(r => r.data)
  },
  create: (data) => client.post('/api/products', data).then(r => r.data),
  update: (id, data) => client.put(`/api/products/${id}`, data).then(r => r.data),
  delete: (id) => client.delete(`/api/products/${id}`),
  uploadImage: (file) => {
    const form = new FormData()
    form.append('file', file)
    return client.post('/api/uploads', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }).then(r => r.data)
  },
}