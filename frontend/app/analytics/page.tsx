'use client'

import { useState, useEffect } from 'react'
import DashboardLayout from '@/components/layout/DashboardLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { apiService } from '@/lib/api'
import { toast } from 'sonner'

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState('30d')
  const [analytics, setAnalytics] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true)
        const data = await apiService.getAnalytics()
        setAnalytics(data)
      } catch (error) {
        console.error('Analitik veriler yüklenirken hata:', error)
        toast.error('Analitik veriler yüklenemedi')
      } finally {
        setLoading(false)
      }
    }

    fetchAnalytics()
  }, [timeRange])

  const timeRanges = [
    { value: '7d', label: 'Son 7 Gün' },
    { value: '30d', label: 'Son 30 Gün' },
    { value: '90d', label: 'Son 90 Gün' },
    { value: '1y', label: 'Son 1 Yıl' }
  ]

  const exportData = (format: 'csv' | 'pdf') => {
    // Export simülasyonu
    const filename = `analytics_${new Date().toISOString().split('T')[0]}.${format}`
    alert(`${filename} dosyası indiriliyor...`)
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Analitik veriler yükleniyor...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  if (!analytics) {
    return (
      <DashboardLayout>
        <div className="text-center py-8">
          <p className="text-gray-500">Analitik veriler bulunamadı</p>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Analitik</h1>
            <p className="text-gray-600">
              Email otomasyonlarınızın performans analizi ve istatistikleri
            </p>
          </div>
          
          <div className="flex space-x-4">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm"
            >
              {timeRanges.map(range => (
                <option key={range.value} value={range.value}>
                  {range.label}
                </option>
              ))}
            </select>
            
            <Button variant="outline" onClick={() => exportData('csv')}>
              CSV İndir
            </Button>
            <Button variant="outline" onClick={() => exportData('pdf')}>
              PDF İndir
            </Button>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Toplam Sorgu</CardTitle>
              <span className="text-2xl">🔍</span>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{analytics.queryStats.total}</div>
              <p className="text-xs text-muted-foreground">
                %{analytics.queryStats.successRate} başarı oranı
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Gönderilen Email</CardTitle>
              <span className="text-2xl">✉️</span>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{analytics.emailStats.sent}</div>
              <p className="text-xs text-muted-foreground">
                %{analytics.emailStats.openRate} açılma oranı
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Email Açılma</CardTitle>
              <span className="text-2xl">📧</span>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{analytics.emailStats.opened}</div>
              <p className="text-xs text-muted-foreground">
                {analytics.emailStats.sent} gönderimden
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Tıklama Oranı</CardTitle>
              <span className="text-2xl">👆</span>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">%{analytics.emailStats.clickRate}</div>
              <p className="text-xs text-muted-foreground">
                {analytics.emailStats.clicked} tıklama
              </p>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top Performing Queries */}
          <Card>
            <CardHeader>
              <CardTitle>En Başarılı Sorgular</CardTitle>
              <CardDescription>
                En yüksek performans gösteren arama sorguları
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analytics.topQueries.map((item, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex-1">
                      <p className="font-medium text-sm">{item.query}</p>
                      <p className="text-xs text-gray-500">{item.count} sorgu</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium">%{item.successRate}</p>
                      <p className="text-xs text-gray-500">başarı</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Monthly Trend */}
          <Card>
            <CardHeader>
              <CardTitle>Aylık Trend</CardTitle>
              <CardDescription>
                Son 6 ayın sorgu ve email istatistikleri
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analytics.monthlyData.map((month, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 text-sm font-medium">{month.month}</div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <div className="w-20 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full" 
                              style={{ width: `${(month.queries / 70) * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-sm text-gray-600">{month.queries} sorgu</span>
                        </div>
                        <div className="flex items-center space-x-2 mt-1">
                          <div className="w-20 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-green-600 h-2 rounded-full" 
                              style={{ width: `${(month.emails / 400) * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-sm text-gray-600">{month.emails} email</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Detailed Stats */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Sorgu İstatistikleri</CardTitle>
              <CardDescription>
                Arama sorgularınızın detaylı analizi
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm">Toplam Sorgu</span>
                  <span className="font-medium">{analytics.queryStats.total}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Başarılı</span>
                  <span className="font-medium text-green-600">{analytics.queryStats.successful}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Başarısız</span>
                  <span className="font-medium text-red-600">{analytics.queryStats.failed}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Başarı Oranı</span>
                  <span className="font-medium">%{analytics.queryStats.successRate}</span>
                </div>
                
                <div className="mt-4">
                  <div className="bg-gray-200 rounded-full h-3">
                    <div 
                      className="bg-green-600 h-3 rounded-full" 
                      style={{ width: `${analytics.queryStats.successRate}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Email Performansı</CardTitle>
              <CardDescription>
                Email kampanyalarınızın detaylı analizi
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm">Gönderilen</span>
                  <span className="font-medium">{analytics.emailStats.sent}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Açılan</span>
                  <span className="font-medium text-blue-600">{analytics.emailStats.opened}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Tıklanan</span>
                  <span className="font-medium text-purple-600">{analytics.emailStats.clicked}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Açılma Oranı</span>
                  <span className="font-medium">%{analytics.emailStats.openRate}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Tıklama Oranı</span>
                  <span className="font-medium">%{analytics.emailStats.clickRate}</span>
                </div>

                <div className="mt-4 space-y-2">
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span>Açılma Oranı</span>
                      <span>%{analytics.emailStats.openRate}</span>
                    </div>
                    <div className="bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${analytics.emailStats.openRate}%` }}
                      ></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span>Tıklama Oranı</span>
                      <span>%{analytics.emailStats.clickRate}</span>
                    </div>
                    <div className="bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-purple-600 h-2 rounded-full" 
                        style={{ width: `${analytics.emailStats.clickRate}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  )
}

