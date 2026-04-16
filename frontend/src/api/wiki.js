import api from './index'

export const wikiAPI = {
  uploadFile(file, category) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/admin/ingest/upload', formData, {
      params: { category },
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  triggerIngest() {
    return api.post('/admin/ingest')
  },

  getIngestStatus() {
    return api.get('/admin/ingest/status')
  },

  triggerLint(autoFix = true) {
    return api.post('/admin/lint', null, { params: { auto_fix: autoFix } })
  },

  getLintReport() {
    return api.get('/admin/lint/report')
  },

  triggerPublish(format = 'markdown') {
    return api.post('/admin/publish', null, { params: { format } })
  },

  query(question) {
    return api.post('/user/query', { question })
  },

  getQueryHistory() {
    return api.get('/user/query/history')
  },

  getWikiPages() {
    return api.get('/admin/wiki/pages')
  },

  updateWikiPage(id, data) {
    return api.put(`/admin/wiki/pages/${id}`, data)
  }
}