'use client'

import { useEffect, useState } from 'react'
import DashboardLayout from '@/components/layout/DashboardLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { useAppStore } from '@/lib/store'
import { apiService } from '@/lib/api'
import { useRequireAuth } from '@/lib/hooks/useAuth'
import { toast } from 'sonner'

export default function DashboardPage() {
  const { user, isAuthenticated, isChecking } = useRequireAuth()
  const { automations, subscription, setUser } = useAppStore()
  const [stats, setStats] = useState({
    totalQueries: 0,
    emailsSent: 0,
    successRate: 0,
    planUsage: 0,
    fileUsage: 0,
    queriesThisMonth: 0,
    filesThisMonth: 0
  })
  const [recentAutomations, setRecentAutomations] = useState<any[]>([])
  const [planInfo, setPlanInfo] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isAuthenticated && !isChecking) {
      return
    }

    const fetchDashboardData = async () => {
      try {
        setLoading(true)
        const data = await apiService.getDashboardData()
        
        setStats({
          totalQueries: data.stats.totalQueries,
          emailsSent: data.stats.emailsSent,
          successRate: data.stats.successRate,
          planUsage: data.stats.planUsage,
          fileUsage: data.stats.fileUsage || 0,
          queriesThisMonth: data.stats.queriesThisMonth || 0,
          filesThisMonth: data.stats.filesThisMonth || 0
        })
        
        setRecentAutomations(data.recentAutomations || [])
        setPlanInfo(data.plan)

        // Kullanıcı bilgilerini de güncelle (plan değişiklikleri için)
        const userProfile = await apiService.getUserProfile()
        setUser(userProfile)
      } catch (error) {
        console.error('Dashboard verileri yüklenirken hata:', error)
        toast.error('Dashboard verileri yüklenemedi')
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [isAuthenticated, isChecking])

  if (isChecking || loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">
              {isChecking ? 'Kimlik doğrulanıyor...' : 'Dashboard yükleniyor...'}
            </p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  if (!isAuthenticated) {
    return null // Will redirect to login
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">
            Hoş geldin, {user?.full_name || user?.email}! Email otomasyonlarınızın özetini görün.
          </p>
        </div>

        {/* Plan Usage Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Aylık Sorgu</CardTitle>
              <span className="text-2xl">🔍</span>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {stats.queriesThisMonth} / {planInfo?.query_limit || 1}
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div 
                  className={`h-2 rounded-full ${stats.planUsage >= 90 ? 'bg-red-500' : stats.planUsage >= 70 ? 'bg-yellow-500' : 'bg-green-500'}`}
                  style={{ width: `${Math.min(stats.planUsage, 100)}%` }}
                />
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                %{stats.planUsage.toFixed(1)} kullanıldı
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Dosya Yükleme</CardTitle>
              <span className="text-2xl">📁</span>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {stats.filesThisMonth} / {planInfo?.file_limit || 1}
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div 
                  className={`h-2 rounded-full ${stats.fileUsage >= 90 ? 'bg-red-500' : stats.fileUsage >= 70 ? 'bg-yellow-500' : 'bg-green-500'}`}
                  style={{ width: `${Math.min(stats.fileUsage, 100)}%` }}
                />
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                %{stats.fileUsage.toFixed(1)} kullanıldı
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Sorgu Başına Sonuç</CardTitle>
              <span className="text-2xl">📊</span>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{planInfo?.results_per_query || 10}</div>
              <p className="text-xs text-muted-foreground">
                Maksimum sonuç sayısı
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Gönderilen Email</CardTitle>
              <span className="text-2xl">✉️</span>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.emailsSent}</div>
              <p className="text-xs text-muted-foreground">
                Toplam gönderim
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Başarı Oranı</CardTitle>
              <span className="text-2xl">📈</span>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">%{stats.successRate}</div>
              <p className="text-xs text-muted-foreground">
                Otomasyon başarısı
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Plan Kullanımı</CardTitle>
              <span className="text-2xl">💎</span>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">%{stats.planUsage}</div>
              <p className="text-xs text-muted-foreground">
                {planInfo?.name || 'Ücretsiz'} Plan
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Plan Info */}
        {planInfo && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>📋 {planInfo.name} Paket</span>
                <Link href="/plans">
                  <Button variant="outline" size="sm">Paketi Değiştir</Button>
                </Link>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-lg font-bold text-blue-600">{planInfo.query_limit}</div>
                  <div className="text-sm text-gray-600">Aylık Sorgu</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-lg font-bold text-green-600">{planInfo.file_limit}</div>
                  <div className="text-sm text-gray-600">Dosya Yükleme</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-lg font-bold text-purple-600">{planInfo.results_per_query}</div>
                  <div className="text-sm text-gray-600">Sorgu Başına Sonuç</div>
                </div>
              </div>
              {planInfo.features && (
                <div className="mt-4">
                  <h4 className="font-medium mb-2">Paket Özellikleri:</h4>
                  <div className="flex flex-wrap gap-2">
                    {planInfo.features.slice(0, 4).map((feature: string, index: number) => (
                      <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                        {feature}
                      </span>
                    ))}
                    {planInfo.features.length > 4 && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded-full text-xs">
                        +{planInfo.features.length - 4} daha
                      </span>
                    )}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Automations */}
          <Card>
            <CardHeader>
              <CardTitle>Son Otomasyonlar</CardTitle>
              <CardDescription>
                En son çalıştırılan email otomasyonlarınız
              </CardDescription>
            </CardHeader>
            <CardContent>
              {recentAutomations.length > 0 ? (
                <div className="space-y-4">
                  {recentAutomations.map((automation) => (
                    <div key={automation._id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <p className="font-medium">
                          {automation.search_terms ? automation.search_terms.split(', ').slice(0, 2).join(', ') : 'Manuel otomasyon'}
                          {automation.search_terms && automation.search_terms.split(', ').length > 2 && ` +${automation.search_terms.split(', ').length - 2} daha`}
                        </p>
                        <p className="text-sm text-gray-500">
                          {new Date(automation.created_at).toLocaleDateString('tr-TR')}
                        </p>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        automation.status === 'completed' ? 'bg-green-100 text-green-800' :
                        automation.status === 'running' ? 'bg-blue-100 text-blue-800' :
                        automation.status === 'failed' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {automation.status === 'completed' ? 'Tamamlandı' :
                         automation.status === 'running' ? 'Çalışıyor' :
                         automation.status === 'failed' ? 'Başarısız' : 'Beklemede'}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-500 mb-4">Henüz otomasyon çalıştırmadınız</p>
                  <Link href="/automation">
                    <Button>İlk Otomasyonunuzu Başlatın</Button>
                  </Link>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Hızlı İşlemler</CardTitle>
              <CardDescription>
                Sık kullanılan işlemlere hızlı erişim
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 gap-4">
                <Link href="/search">
                  <Button className="w-full justify-start" variant="outline">
                    <span className="mr-2">🔍</span>
                    Arama Motoru
                  </Button>
                </Link>
                
                <Link href="/files">
                  <Button className="w-full justify-start" variant="outline">
                    <span className="mr-2">📁</span>
                    Dosya Otomasyonu
                  </Button>
                </Link>
                
                <Link href="/analytics">
                  <Button className="w-full justify-start" variant="outline">
                    <span className="mr-2">📊</span>
                    Analitik Görüntüle
                  </Button>
                </Link>
                
                <Link href="/plans">
                  <Button className="w-full justify-start" variant="outline">
                    <span className="mr-2">⬆️</span>
                    Plan Yükselt
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Plan Status */}
        <Card>
          <CardHeader>
            <CardTitle>Plan Durumu</CardTitle>
            <CardDescription>
              Mevcut planınız ve kullanım detayları
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">
                  {planInfo?.name || 'Ücretsiz Plan'}
                </p>
                <p className="text-sm text-gray-500">
                  {planInfo?.query_limit || 10} sorgu limiti
                </p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold">
                  {stats.totalQueries}/{planInfo?.query_limit || 10}
                </p>
                <p className="text-sm text-gray-500">Bu ay kullanılan</p>
              </div>
            </div>
            
            <div className="mt-4">
              <div className="bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full" 
                  style={{ width: `${stats.planUsage}%` }}
                ></div>
              </div>
            </div>
            
            {stats.planUsage > 80 && (
              <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-sm text-yellow-800">
                  Plan limitinizin %{stats.planUsage}'ini kullandınız. 
                  <Link href="/plans" className="font-medium underline ml-1">
                    Plan yükseltmeyi düşünün
                  </Link>
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}

