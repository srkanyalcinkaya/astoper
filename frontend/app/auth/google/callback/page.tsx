'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useAppStore } from '@/lib/store'
import { apiService } from '@/lib/api'
import { toast } from 'sonner'

export default function GoogleCallbackPage() {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')
  const router = useRouter()
  const { setUser } = useAppStore()

  useEffect(() => {
    const handleGoogleCallback = async () => {
      try {
        const hash = window.location.hash.substring(1)
        const params = new URLSearchParams(hash)
        const token = params.get('access_token')
        
        if (!token) {
          throw new Error('Google token bulunamadı')
        }

        const response = await apiService.googleLogin(token)
        
        setUser(response.user)
        localStorage.setItem('access_token', response.access_token)
        
        setStatus('success')
        setMessage('Google ile başarıyla giriş yapıldı!')
        toast.success('Giriş başarılı!')
        
        setTimeout(() => {
          router.push('/dashboard')
        }, 2000)
        
      } catch (error: any) {
        console.error('Google giriş hatası:', error)
        setStatus('error')
        setMessage(error.response?.data?.detail || 'Google ile giriş yapılamadı')
        toast.error('Giriş başarısız')
      }
    }

    handleGoogleCallback()
  }, [router, setUser])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        <Card>
          <CardHeader>
            <CardTitle className="text-center">
              {status === 'loading' && 'Google ile Giriş Yapılıyor...'}
              {status === 'success' && 'Giriş Başarılı!'}
              {status === 'error' && 'Giriş Başarısız'}
            </CardTitle>
            <CardDescription className="text-center">
              {status === 'loading' && 'Lütfen bekleyin...'}
              {status === 'success' && 'Dashboard\'a yönlendiriliyorsunuz...'}
              {status === 'error' && 'Bir hata oluştu'}
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            {status === 'loading' && (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            )}
            
            {status === 'success' && (
              <div className="text-green-600">
                <svg className="w-12 h-12 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <p className="text-sm text-gray-600">{message}</p>
              </div>
            )}
            
            {status === 'error' && (
              <div className="text-red-600">
                <svg className="w-12 h-12 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                <p className="text-sm text-gray-600 mb-4">{message}</p>
                <Button onClick={() => router.push('/login')}>
                  Giriş Sayfasına Dön
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
