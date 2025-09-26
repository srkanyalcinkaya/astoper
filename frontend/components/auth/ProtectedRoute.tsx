'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAppStore } from '@/lib/store'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const [isLoading, setIsLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const router = useRouter()
  const { user } = useAppStore()

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('access_token')
      
      if (!token) {
        console.log('No token found, redirecting to login')
        router.push('/login')
        return
      }

      if (!user) {
        console.log('No user in store, redirecting to login')
        router.push('/login')
        return
      }

      console.log('User authenticated:', user)
      setIsAuthenticated(true)
      setIsLoading(false)
    }

    checkAuth()
  }, [user, router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return <>{children}</>
}
