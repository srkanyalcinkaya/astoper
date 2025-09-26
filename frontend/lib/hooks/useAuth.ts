import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAppStore } from '../store'
import api from '../api'

export const useAuth = (redirectToLogin = true) => {
  const router = useRouter()
  const { user, isAuthenticated, logout } = useAppStore()
  const [isChecking, setIsChecking] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        setIsChecking(true)
        setError(null)
        
        const token = localStorage.getItem('access_token')
        
        if (!token) {
          if (redirectToLogin) {
            router.push('/login')
          }
          return
        }

        // Check if user data exists in store
        if (!user) {
          // Try to get user data from API
          try {
            const response = await api.get('/auth/me')
            useAppStore.getState().setUser(response.data)
          } catch (error: any) {
            console.error('Auth check failed:', error)
            
            // If API call fails, clear auth data
            localStorage.removeItem('access_token')
            useAppStore.getState().logout()
            
            if (error.response?.status === 401 && redirectToLogin) {
              router.push('/login')
            } else {
              setError('Authentication failed')
            }
          }
        }
      } catch (error) {
        console.error('Auth check error:', error)
        setError('Authentication error')
      } finally {
        setIsChecking(false)
      }
    }

    checkAuth()
  }, [user, isAuthenticated, redirectToLogin, router])

  const handleLogout = () => {
    logout()
    router.push('/login')
  }

  return {
    user,
    isAuthenticated,
    isChecking,
    error,
    logout: handleLogout
  }
}

export const useRequireAuth = () => {
  return useAuth(true)
}

export const useOptionalAuth = () => {
  return useAuth(false)
}
