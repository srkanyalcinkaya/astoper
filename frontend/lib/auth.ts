import api from './api'
import { useAppStore } from './store'

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  full_name?: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: any
}

export const authService = {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await api.post('/auth/login', credentials, {
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    const { access_token, user } = response.data
    localStorage.setItem('access_token', access_token)
    
    if (user) {
      useAppStore.getState().setUser(user)
    }
    
    return response.data
  },

  async register(userData: RegisterRequest): Promise<AuthResponse> {
    const response = await api.post('/auth/register', userData)
    
    const { access_token, user } = response.data
    localStorage.setItem('access_token', access_token)
    
    if (user) {
      useAppStore.getState().setUser(user)
    }
    
    return response.data
  },

  async getCurrentUser(): Promise<any> {
    const response = await api.get('/auth/me')
    return response.data
  },

  async logout(): Promise<void> {
    localStorage.removeItem('access_token')
    useAppStore.getState().logout()
  },

  async forgotPassword(email: string): Promise<void> {
    await api.post('/auth/forgot-password', { email })
  },

  async resetPassword(token: string, newPassword: string): Promise<void> {
    await api.post('/auth/reset-password', { 
      token, 
      new_password: newPassword 
    })
  },

  getToken(): string | null {
    return localStorage.getItem('access_token')
  },

  isAuthenticated(): boolean {
    const token = this.getToken()
    return !!token
  }
}

