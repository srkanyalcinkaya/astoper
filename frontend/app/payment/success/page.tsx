'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import DashboardLayout from '@/components/layout/DashboardLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { apiService } from '@/lib/api'
import Link from 'next/link'

export default function PaymentSuccessPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [loading, setLoading] = useState(true)
  const [planInfo, setPlanInfo] = useState<any>(null)

  const sessionId = searchParams.get('session_id')
  const planId = searchParams.get('plan_id')

  useEffect(() => {
    const fetchPlanInfo = async () => {
      if (planId) {
        try {
          const plans = await apiService.getPlans()
          const plan = plans.plans.find((p: any) => p._id === planId)
          setPlanInfo(plan)
        } catch (error) {
          console.error('Plan bilgileri yüklenemedi:', error)
        }
      }
      setLoading(false)
    }

    fetchPlanInfo()
  }, [planId])

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Ödeme durumu kontrol ediliyor...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-green-600 text-2xl">✓</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Ödeme Başarılı!</h1>
          <p className="text-gray-600">
            Aboneliğiniz başarıyla oluşturuldu ve hemen kullanmaya başlayabilirsiniz.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-green-600">🎉 Hoş Geldiniz!</CardTitle>
            <CardDescription>
              {planInfo ? `${planInfo.name} planına başarıyla geçiş yaptınız` : 'Aboneliğiniz aktif'}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {planInfo && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold mb-2">{planInfo.name} Plan Özellikleri:</h3>
                <ul className="space-y-1 text-sm text-gray-600">
                  <li>• {planInfo.max_queries_per_month} aylık sorgu hakkı</li>
                  <li>• {planInfo.max_file_uploads} dosya yükleme hakkı</li>
                  <li>• Sorgu başına {planInfo.max_results_per_query} sonuç</li>
                  {planInfo.features.map((feature: string, index: number) => (
                    <li key={index}>• {feature}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-semibold text-blue-900 mb-2">📋 Sonraki Adımlar:</h4>
              <ol className="list-decimal list-inside space-y-1 text-sm text-blue-800">
                <li>Email provider ekleyin (henüz eklemediyseniz)</li>
                <li>İlk email otomasyonunuzu oluşturun</li>
                <li>Dosya yükleyerek veya arama sorguları ile başlayın</li>
              </ol>
            </div>

            <div className="flex gap-4">
              <Link href="/dashboard" className="flex-1">
                <Button className="w-full">
                  Dashboard'a Git
                </Button>
              </Link>
              <Link href="/automation" className="flex-1">
                <Button variant="outline" className="w-full">
                  Otomasyon Başlat
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        {sessionId && (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">İşlem Detayları</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-gray-500 font-mono">
                Session ID: {sessionId}
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  )
}
