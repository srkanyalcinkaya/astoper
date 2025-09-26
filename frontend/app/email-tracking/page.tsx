'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { apiService } from '@/lib/api'
import { toast } from 'sonner'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import DashboardLayout from '@/components/layout/DashboardLayout'

interface EmailStats {
  total_emails: number
  sent: number
  failed: number
  delivered: number
  opened: number
  clicked: number
  success_rate: number
  daily_stats: Array<{
    _id: string
    count: number
    sent: number
    failed: number
  }>
}

interface EmailHistory {
  _id: string
  email_address: string
  subject: string
  template_id?: string
  provider_id: string
  status: 'sent' | 'failed' | 'delivered' | 'opened' | 'clicked'
  sent_at: string
  delivered_at?: string
  opened_at?: string
  clicked_at?: string
  error_message?: string
  campaign_id: string
}

interface UserLimits {
  email_limit: {
    can_send: boolean
    remaining: number
    used: number
    limit: number
  }
  template_limit: {
    can_create: boolean
    remaining: number
    used: number
    limit: number
  }
  query_limit: {
    can_query: boolean
    remaining: number
    used: number
    limit: number
  }
  file_limit: {
    can_upload: boolean
    remaining: number
    used: number
    limit: number
  }
  plan_name: string
  plan_price: number
}

export default function EmailTrackingPage() {
  const [stats, setStats] = useState<EmailStats | null>(null)
  const [history, setHistory] = useState<EmailHistory[]>([])
  const [limits, setLimits] = useState<UserLimits | null>(null)
  const [loading, setLoading] = useState(true)
  const [historyLoading, setHistoryLoading] = useState(false)
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [limit, setLimit] = useState(50)
  const [offset, setOffset] = useState(0)

  useEffect(() => {
    loadData()
  }, [])

  useEffect(() => {
    loadHistory()
  }, [statusFilter, limit, offset])

  const loadData = async () => {
    try {
      setLoading(true)
      
      const token = localStorage.getItem('access_token')
      if (!token) {
        toast.error('Giriş yapmanız gerekiyor')
        window.location.href = '/login'
        return
      }
      
      console.log('Loading email tracking data...')
      
      try {
        const authTest = await apiService.get('/email-sending/test-auth')
        console.log('Auth test successful:', authTest)
      } catch (authError: any) {
        console.error('Auth test failed:', authError)
        throw authError
      }
      
      const [statsResponse, limitsResponse] = await Promise.all([
        apiService.getEmailTrackingStats(),
        apiService.getUserLimits()
      ])
      
      setStats(statsResponse)
      setLimits(limitsResponse)
    } catch (error: any) {
      console.error('Veri yükleme hatası:', error)
      if (error.response?.status === 401 || error.response?.status === 403) {
        toast.error('Oturum süreniz dolmuş. Lütfen tekrar giriş yapın.')
        localStorage.removeItem('access_token')
        window.location.href = '/login'
      } else {
        toast.error('Veriler yüklenirken hata oluştu')
      }
    } finally {
      setLoading(false)
    }
  }

  const loadHistory = async () => {
    try {
      setHistoryLoading(true)
      
      const response = await apiService.getEmailTrackingHistory(limit, offset, statusFilter === 'all' ? undefined : statusFilter)
      setHistory(response.emails)
    } catch (error: any) {
      console.error('Geçmiş yükleme hatası:', error)
      toast.error('Email geçmişi yüklenirken hata oluştu')
    } finally {
      setHistoryLoading(false)
    }
  }

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'sent':
        return 'default'
      case 'delivered':
        return 'secondary'
      case 'opened':
        return 'outline'
      case 'clicked':
        return 'default'
      case 'failed':
        return 'destructive'
      default:
        return 'secondary'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'sent':
        return 'Gönderildi'
      case 'delivered':
        return 'Teslim Edildi'
      case 'opened':
        return 'Açıldı'
      case 'clicked':
        return 'Tıklandı'
      case 'failed':
        return 'Başarısız'
      default:
        return status
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('tr-TR')
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="container mx-auto p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">Email Takibi</h1>
              <p className="text-gray-600">Email gönderim istatistiklerinizi ve geçmişinizi görüntüleyin</p>
            </div>
          </div>

      {/* Plan Limitleri */}
      {limits && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Email Limiti</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{limits.email_limit.used}/{limits.email_limit.limit === -1 ? '∞' : limits.email_limit.limit}</div>
              <p className="text-xs text-gray-600">Kalan: {limits.email_limit.limit === -1 ? '∞' : limits.email_limit.remaining}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Şablon Limiti</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{limits.template_limit.used}/{limits.template_limit.limit === -1 ? '∞' : limits.template_limit.limit}</div>
              <p className="text-xs text-gray-600">Kalan: {limits.template_limit.limit === -1 ? '∞' : limits.template_limit.remaining}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Sorgu Limiti</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{limits.query_limit.used}/{limits.query_limit.limit === -1 ? '∞' : limits.query_limit.limit}</div>
              <p className="text-xs text-gray-600">Kalan: {limits.query_limit.limit === -1 ? '∞' : limits.query_limit.remaining}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Dosya Limiti</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{limits.file_limit.used}/{limits.file_limit.limit === -1 ? '∞' : limits.file_limit.limit}</div>
              <p className="text-xs text-gray-600">Kalan: {limits.file_limit.limit === -1 ? '∞' : limits.file_limit.remaining}</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* İstatistikler */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Toplam Email</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_emails}</div>
              <p className="text-xs text-gray-600">Tüm zamanlar</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Başarı Oranı</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.success_rate.toFixed(1)}%</div>
              <p className="text-xs text-gray-600">Gönderim başarısı</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Başarılı</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats.sent}</div>
              <p className="text-xs text-gray-600">Gönderilen</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Başarısız</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{stats.failed}</div>
              <p className="text-xs text-gray-600">Hatalı</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Email Geçmişi */}
      <Card>
        <CardHeader>
          <CardTitle>Email Geçmişi</CardTitle>
          <CardDescription>
            Gönderilen emaillerin detaylı listesi
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Filtreler */}
          <div className="flex gap-4 mb-4">
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Durum Filtresi" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tümü</SelectItem>
                <SelectItem value="sent">Gönderildi</SelectItem>
                <SelectItem value="delivered">Teslim Edildi</SelectItem>
                <SelectItem value="opened">Açıldı</SelectItem>
                <SelectItem value="clicked">Tıklandı</SelectItem>
                <SelectItem value="failed">Başarısız</SelectItem>
              </SelectContent>
            </Select>

            <Select value={limit.toString()} onValueChange={(value) => setLimit(parseInt(value))}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="25">25</SelectItem>
                <SelectItem value="50">50</SelectItem>
                <SelectItem value="100">100</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Tablo */}
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Email</th>
                  <th className="text-left p-2">Konu</th>
                  <th className="text-left p-2">Durum</th>
                  <th className="text-left p-2">Gönderim Zamanı</th>
                  <th className="text-left p-2">Kampanya</th>
                </tr>
              </thead>
              <tbody>
                {historyLoading ? (
                  <tr>
                    <td colSpan={5} className="text-center p-4">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
                    </td>
                  </tr>
                ) : history.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="text-center p-4 text-gray-500">
                      Henüz email gönderilmedi
                    </td>
                  </tr>
                ) : (
                  history.map((email) => (
                    <tr key={email._id} className="border-b hover:bg-gray-50">
                      <td className="p-2">{email.email_address}</td>
                      <td className="p-2">{email.subject}</td>
                      <td className="p-2">
                        <Badge variant={getStatusBadgeVariant(email.status)}>
                          {getStatusText(email.status)}
                        </Badge>
                      </td>
                      <td className="p-2">{formatDate(email.sent_at)}</td>
                      <td className="p-2">
                        <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                          {email.campaign_id}
                        </code>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Sayfalama */}
          <div className="flex justify-between items-center mt-4">
            <Button 
              variant="outline" 
              disabled={offset === 0}
              onClick={() => setOffset(Math.max(0, offset - limit))}
            >
              Önceki
            </Button>
            <span className="text-sm text-gray-600">
              Sayfa {Math.floor(offset / limit) + 1}
            </span>
            <Button 
              variant="outline" 
              disabled={history.length < limit}
              onClick={() => setOffset(offset + limit)}
            >
              Sonraki
            </Button>
          </div>
        </CardContent>
      </Card>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
