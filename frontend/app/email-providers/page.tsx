'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAppStore } from '@/lib/store'
import { useRequireAuth } from '@/lib/hooks/useAuth'
import api from '@/lib/api'
import DashboardLayout from '@/components/layout/DashboardLayout'

interface EmailProvider {
  id: string
  provider_name: string
  email_address: string
  is_active: boolean
  is_verified: boolean
  last_used?: string
  created_at: string
}

interface SMTPConfig {
  host: string
  port: number
  username: string
  password: string
  use_ssl: boolean
  use_tls: boolean
}

interface CreateProviderData {
  provider_name: 'gmail' | 'outlook' | 'yahoo' | 'custom'
  email_address: string
  smtp_config?: SMTPConfig
}

const providerInfo = {
  gmail: {
    name: 'Gmail',
    smtp_host: 'smtp.gmail.com',
    smtp_port: 587,
    instructions: 'Gmail için App Password kullanmanız önerilir. 2FA aktif olmalıdır.'
  },
  outlook: {
    name: 'Outlook/Hotmail',
    smtp_host: 'smtp-mail.outlook.com',
    smtp_port: 587,
    instructions: 'Outlook için modern authentication kullanın.'
  },
  yahoo: {
    name: 'Yahoo Mail',
    smtp_host: 'smtp.mail.yahoo.com',
    smtp_port: 587,
    instructions: 'Yahoo için App Password gerekir.'
  },
  custom: {
    name: 'Özel SMTP',
    smtp_host: '',
    smtp_port: 587,
    instructions: 'Kendi SMTP sunucunuzun bilgilerini girin.'
  }
}

export default function EmailProvidersPage() {
  const router = useRouter()
  const { user, isAuthenticated, isChecking } = useRequireAuth()
  const [providers, setProviders] = useState<EmailProvider[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [creating, setCreating] = useState(false)
  const [testing, setTesting] = useState<string | null>(null)
  
  const [formData, setFormData] = useState<CreateProviderData>({
    provider_name: 'gmail',
    email_address: '',
    smtp_config: {
      host: providerInfo.gmail.smtp_host,
      port: providerInfo.gmail.smtp_port,
      username: '',
      password: '',
      use_ssl: false,
      use_tls: true
    }
  })

  useEffect(() => {
    if (!isAuthenticated && !isChecking) {
      return
    }
    if (isAuthenticated) {
      loadProviders()
    }
  }, [isAuthenticated, isChecking])

  const loadProviders = async () => {
    try {
      setLoading(true)
      const response = await api.get('/email-providers/')
      setProviders(response.data)
    } catch (error) {
      console.error('Error loading email providers:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleProviderChange = (provider_name: 'gmail' | 'outlook' | 'yahoo' | 'custom') => {
    const info = providerInfo[provider_name]
    setFormData({
      ...formData,
      provider_name,
      smtp_config: {
        host: info.smtp_host,
        port: info.smtp_port,
        username: formData.smtp_config?.username || '',
        password: '',
        use_ssl: provider_name === 'gmail' || provider_name === 'yahoo',
        use_tls: true
      }
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setCreating(true)
      
      const payload: CreateProviderData = {
        provider_name: formData.provider_name,
        email_address: formData.email_address,
        smtp_config: formData.smtp_config
      }

      await api.post('/email-providers/', payload)
      
      setFormData({
        provider_name: 'gmail',
        email_address: '',
        smtp_config: {
          host: providerInfo.gmail.smtp_host,
          port: providerInfo.gmail.smtp_port,
          username: '',
          password: '',
          use_ssl: false,
          use_tls: true
        }
      })
      
      setShowCreateForm(false)
      loadProviders()
    } catch (error) {
      console.error('Error creating email provider:', error)
      alert('Email provider oluşturulurken hata oluştu')
    } finally {
      setCreating(false)
    }
  }

  const testProvider = async (providerId: string) => {
    try {
      setTesting(providerId)
      const response = await api.post(`/email-providers/${providerId}/test`)
      
      if (response.data.success) {
        alert('Test email başarıyla gönderildi!')
        loadProviders()
      } else {
        alert(`Test başarısız: ${response.data.message}`)
      }
    } catch (error: any) {
      console.error('Error testing email provider:', error)
      alert(`Test başarısız: ${error.response?.data?.detail || 'Bilinmeyen hata'}`)
    } finally {
      setTesting(null)
    }
  }

  const deleteProvider = async (providerId: string) => {
    if (!confirm('Bu email provider\'ı silmek istediğinizden emin misiniz?')) {
      return
    }

    try {
      await api.delete(`/email-providers/${providerId}`)
      loadProviders()
    } catch (error) {
      console.error('Error deleting email provider:', error)
      alert('Email provider silinirken hata oluştu')
    }
  }

  if (isChecking || loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">
            {isChecking ? 'Kimlik doğrulanıyor...' : 'Email provider\'lar yükleniyor...'}
          </p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null // Will redirect to login
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Email Provider'lar</h1>
          <p className="mt-2 text-gray-600">
            Email göndermek için kullanacağınız email hesaplarını yönetin
          </p>
        </div>

        {/* Provider List */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h2 className="text-lg font-medium text-gray-900">Kayıtlı Email Provider'lar</h2>
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            >
              Yeni Provider Ekle
            </button>
          </div>

          {providers.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              <p>Henüz email provider kaydınız yok.</p>
              <p>Email göndermek için bir provider ekleyin.</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {providers.map((provider) => (
                <div key={provider.id} className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center">
                        <h3 className="text-lg font-medium text-gray-900">
                          {providerInfo[provider.provider_name as keyof typeof providerInfo]?.name}
                        </h3>
                        <div className="ml-4 flex space-x-2">
                          {provider.is_verified ? (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              Doğrulanmış
                            </span>
                          ) : (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                              Doğrulanmamış
                            </span>
                          )}
                          {provider.is_active ? (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              Aktif
                            </span>
                          ) : (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                              Pasif
                            </span>
                          )}
                        </div>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{provider.email_address}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        Oluşturulma: {new Date(provider.created_at).toLocaleDateString('tr-TR')}
                      </p>
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => testProvider(provider.id)}
                        disabled={testing === provider.id}
                        className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 disabled:opacity-50"
                      >
                        {testing === provider.id ? 'Test Ediliyor...' : 'Test Et'}
                      </button>
                      <button
                        onClick={() => deleteProvider(provider.id)}
                        className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
                      >
                        Sil
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Create Form Modal */}
        {showCreateForm && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
              <div className="mt-3">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Yeni Email Provider Ekle</h3>
                
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Provider</label>
                    <select
                      value={formData.provider_name}
                      onChange={(e) => handleProviderChange(e.target.value as any)}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="gmail">Gmail</option>
                      <option value="outlook">Outlook/Hotmail</option>
                      <option value="yahoo">Yahoo Mail</option>
                      <option value="custom">Özel SMTP</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Email Adresi</label>
                    <input
                      type="email"
                      required
                      value={formData.email_address}
                      onChange={(e) => setFormData({ ...formData, email_address: e.target.value })}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">SMTP Host</label>
                    <input
                      type="text"
                      required
                      value={formData.smtp_config?.host || ''}
                      onChange={(e) => setFormData({
                        ...formData,
                        smtp_config: { ...formData.smtp_config!, host: e.target.value }
                      })}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Port</label>
                    <input
                      type="number"
                      required
                      value={formData.smtp_config?.port || 587}
                      onChange={(e) => setFormData({
                        ...formData,
                        smtp_config: { ...formData.smtp_config!, port: parseInt(e.target.value) }
                      })}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Kullanıcı Adı</label>
                    <input
                      type="text"
                      required
                      value={formData.smtp_config?.username || ''}
                      onChange={(e) => setFormData({
                        ...formData,
                        smtp_config: { ...formData.smtp_config!, username: e.target.value }
                      })}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Şifre</label>
                    <input
                      type="password"
                      required
                      value={formData.smtp_config?.password || ''}
                      onChange={(e) => setFormData({
                        ...formData,
                        smtp_config: { ...formData.smtp_config!, password: e.target.value }
                      })}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                    />
                    <p className="mt-1 text-xs text-gray-500">
                      {providerInfo[formData.provider_name]?.instructions}
                    </p>
                  </div>

                  <div className="flex items-center space-x-4">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={formData.smtp_config?.use_ssl || false}
                        onChange={(e) => setFormData({
                          ...formData,
                          smtp_config: { ...formData.smtp_config!, use_ssl: e.target.checked }
                        })}
                        className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200"
                      />
                      <span className="ml-2 text-sm text-gray-700">SSL Kullan</span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={formData.smtp_config?.use_tls || false}
                        onChange={(e) => setFormData({
                          ...formData,
                          smtp_config: { ...formData.smtp_config!, use_tls: e.target.checked }
                        })}
                        className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200"
                      />
                      <span className="ml-2 text-sm text-gray-700">TLS Kullan</span>
                    </label>
                  </div>

                  <div className="flex justify-end space-x-3 pt-4">
                    <button
                      type="button"
                      onClick={() => setShowCreateForm(false)}
                      className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                    >
                      İptal
                    </button>
                    <button
                      type="submit"
                      disabled={creating}
                      className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50"
                    >
                      {creating ? 'Oluşturuluyor...' : 'Oluştur'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
