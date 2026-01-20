import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const API_URL = 'http://localhost:8000/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  
  const isAuthenticated = computed(() => !!token.value)
  
  async function login(email, password) {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Giriş başarısız')
    }
    
    const data = await response.json()
    setAuth(data.access_token, data.user)
    return data
  }
  
  async function register(name, email, password) {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password }),
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Kayıt başarısız')
    }
    
    const data = await response.json()
    setAuth(data.access_token, data.user)
    return data
  }
  
  async function loginWithGoogle(code, redirectUri) {
    const response = await fetch(`${API_URL}/auth/google`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code, redirect_uri: redirectUri }),
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Google giriş başarısız')
    }
    
    const data = await response.json()
    setAuth(data.access_token, data.user)
    return data
  }
  
  function setAuth(newToken, newUser) {
    token.value = newToken
    user.value = newUser
    localStorage.setItem('token', newToken)
    localStorage.setItem('user', JSON.stringify(newUser))
  }
  
  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
  
  return {
    token,
    user,
    isAuthenticated,
    login,
    register,
    loginWithGoogle,
    logout,
  }
})
