import api from './api'
import { AuthResponse, User } from '../types'

export const authService = {
  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await api.post('/auth/login', { email, password })
    return response.data
  },

  async register(
    email: string,
    password: string,
    full_name: string,
    role: string
  ): Promise<User> {
    const response = await api.post('/auth/register', {
      email,
      password,
      full_name,
      role
    })
    return response.data
  },

  async getMe(): Promise<User> {
    const response = await api.get('/auth/me')
    return response.data
  },

  logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    window.location.href = '/login'
  }
}