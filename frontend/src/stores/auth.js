import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const isReady = ref(false)

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  async function login(username, password) {
    const response = await authAPI.login(username, password)
    token.value = response.data.access_token
    localStorage.setItem('token', token.value)
    await fetchUser()
    return true
  }

  async function register(username, password, role) {
    await authAPI.register(username, password, role)
    return true
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      const response = await authAPI.getMe()
      user.value = response.data
    } catch (e) {
      logout()
    } finally {
      isReady.value = true
    }
  }

  function logout() {
    user.value = null
    token.value = null
    isReady.value = false
    localStorage.removeItem('token')
  }

  if (token.value) {
    fetchUser()
  } else {
    isReady.value = true
  }

  return { user, token, isReady, isLoggedIn, isAdmin, login, register, logout, fetchUser }
})