'use client'

import DashboardLayout from '@/components/layout/DashboardLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import Link from 'next/link'

export default function PaymentCancelPage() {
  return (
    <DashboardLayout>
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-gray-600 text-2xl">✕</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Ödeme İptal Edildi</h1>
          <p className="text-gray-600">
            Ödeme işlemi iptal edildi. Planınız değişmedi.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>💡 Ne Yapmak İstiyorsunuz?</CardTitle>
            <CardDescription>
              Ödeme işleminiz iptal edildi, ancak istediğiniz zaman tekrar deneyebilirsiniz
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-semibold text-blue-900 mb-2">🔄 Tekrar Denemek İster misiniz?</h4>
              <p className="text-sm text-blue-800 mb-3">
                Planınızı yükseltmek için tekrar deneyebilir veya mevcut ücretsiz planınızla devam edebilirsiniz.
              </p>
              <div className="flex gap-3">
                <Link href="/plans">
                  <Button size="sm">
                    Planları Görüntüle
                  </Button>
                </Link>
                <Link href="/dashboard">
                  <Button variant="outline" size="sm">
                    Dashboard'a Dön
                  </Button>
                </Link>
              </div>
            </div>

            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold mb-2">📞 Yardıma İhtiyacınız Var mı?</h4>
              <p className="text-sm text-gray-600 mb-3">
                Ödeme sırasında sorun yaşadıysanız bizimle iletişime geçebilirsiniz.
              </p>
              <Button variant="outline" size="sm">
                Destek Ekibi ile İletişime Geç
              </Button>
            </div>

            <div className="bg-green-50 p-4 rounded-lg">
              <h4 className="font-semibold text-green-900 mb-2">🆓 Ücretsiz Plan ile Devam</h4>
              <p className="text-sm text-green-800 mb-3">
                Ücretsiz planınızla email otomasyonlarını denemeye devam edebilirsiniz:
              </p>
              <ul className="text-sm text-green-800 space-y-1 mb-3">
                <li>• 1 aylık sorgu hakkı</li>
                <li>• 1 dosya yükleme hakkı</li>
                <li>• Sorgu başına 10 sonuç</li>
                <li>• Temel email gönderimi</li>
              </ul>
              <Link href="/automation">
                <Button variant="outline" size="sm" className="border-green-300 text-green-700 hover:bg-green-100">
                  Ücretsiz Plan ile Başla
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        <div className="text-center">
          <p className="text-sm text-gray-500">
            Sorularınız için:{' '}
            <a href="mailto:support@example.com" className="text-blue-600 hover:underline">
              support@example.com
            </a>
          </p>
        </div>
      </div>
    </DashboardLayout>
  )
}
