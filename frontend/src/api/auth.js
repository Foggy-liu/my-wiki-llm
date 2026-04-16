import api from './index'

export const authAPI = {
  login(username, password) {
    const params = new URLSearchParams()
    params.append('username', username)
    params.append('password', password)
    return api.post('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
  },

  register(username, password, role = 'user') {
    return api.post('/auth/register', { username, password, role })
  },

  getMe() {
    return api.get('/auth/me')
  }
}