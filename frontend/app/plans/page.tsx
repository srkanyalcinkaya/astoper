'use client'

import { useState, useEffect } from 'react'
import DashboardLayout from '@/components/layout/DashboardLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useAppStore } from '@/lib/store'
import { apiService } from '@/lib/api'
import { toast } from 'sonner'
import { usePlanCosts } from '@/lib/hooks/usePlanCosts'

export default function PlansPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [plans, setPlans] = useState<any[]>([])
  const [subscription, setSubscription] = useState<any>(null)
  const [currentPlan, setCurrentPlan] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const { user } = useAppStore()
  const { costs, loading: costsLoading } = usePlanCosts()

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const [plansData, subscriptionData, dashboardData] = await Promise.all([
          apiService.getPlans(),
          apiService.getSubscription(),
          apiService.getDashboardData()
        ])
        
        setPlans(plansData.plans || [])
        setSubscription(subscriptionData.subscription)
        
        if (dashboardData.plan) {
          console.log('Dashboard plan:', dashboardData.plan)
          console.log('Available plans:', plansData.plans.map((p: any) => ({ name: p.name, _id: p._id })))
          
          const fullPlan = plansData.plans.find((p: any) => p.name === dashboardData.plan.name)
          if (fullPlan) {
            console.log('Found matching plan:', fullPlan)
            setCurrentPlan(fullPlan)
          } else {
            console.log('No matching plan found, using dashboard plan')
            const dashboardPlan = {
              ...dashboardData.plan,
              _id: dashboardData.plan._id || 'unknown',
              price: dashboardData.plan.price || 0,
              currency: dashboardData.plan.currency || 'USD',
              max_queries_per_month: dashboardData.plan.query_limit || 1,
              max_emails_per_month: dashboardData.plan.email_limit || 10,
              max_file_uploads: dashboardData.plan.file_limit || 1,
              max_results_per_query: dashboardData.plan.results_per_query || 10,
              max_templates: dashboardData.plan.max_templates || 1,
              max_file_size_mb: dashboardData.plan.max_file_size_mb || 5,
              features: dashboardData.plan.features || [],
              is_active: true
            }
            setCurrentPlan(dashboardPlan)
          }
        } else {
          console.log('No plan data from dashboard')
        }
      } catch (error) {
        console.error('Plan verileri yüklenirken hata:', error)
        toast.error('Plan verileri yüklenemedi')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const refreshData = async () => {
    try {
      const [plansData, subscriptionData, dashboardData] = await Promise.all([
        apiService.getPlans(),
        apiService.getSubscription(),
        apiService.getDashboardData()
      ])
      
      setPlans(plansData.plans || [])
      setSubscription(subscriptionData.subscription)
      
      if (dashboardData.plan) {
        const fullPlan = plansData.plans.find((p: any) => p.name === dashboardData.plan.name)
        if (fullPlan) {
          setCurrentPlan(fullPlan)
        } else {
          const dashboardPlan = {
            ...dashboardData.plan,
            _id: dashboardData.plan._id || 'unknown',
            price: dashboardData.plan.price || 0,
            currency: dashboardData.plan.currency || 'USD',
            max_queries_per_month: dashboardData.plan.query_limit || 1,
            max_emails_per_month: dashboardData.plan.email_limit || 10,
            max_file_uploads: dashboardData.plan.file_limit || 1,
            max_results_per_query: dashboardData.plan.results_per_query || 10,
            max_templates: dashboardData.plan.max_templates || 1,
            max_file_size_mb: dashboardData.plan.max_file_size_mb || 5,
            features: dashboardData.plan.features || [],
            is_active: true
          }
          setCurrentPlan(dashboardPlan)
        }
      }
      
      toast.success('Plan bilgileri güncellendi!')
    } catch (error) {
      console.error('Plan refresh hatası:', error)
      toast.error('Plan bilgileri güncellenemedi')
    }
  }


  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Planlar yükleniyor...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  const handlePlanSelect = async (plan: any) => {
    if (!user) {
      toast.error('Lütfen önce giriş yapın')
      return
    }

    if (plan.price === 0) {
      setIsLoading(true)
      try {
        toast.success('Ücretsiz plana geçiş yapıldı!')
        
        const subscriptionData = await apiService.getSubscription()
        setSubscription(subscriptionData.subscription)
      } catch (error) {
        toast.error('Plan değişikliği başarısız')
      } finally {
        setIsLoading(false)
      }
      return
    }

    setIsLoading(true)
    try {
      const result = await apiService.createCheckoutSession({
        plan_id: plan._id
      })

      if (result.success && result.checkout_url) {
        window.location.href = result.checkout_url
      } else {
        toast.error('Ödeme sayfası oluşturulamadı')
      }
    } catch (error: any) {
      console.error('Checkout session error:', error)
      toast.error(error.response?.data?.detail || 'Ödeme işlemi başlatılamadı')
    } finally {
      setIsLoading(false)
    }
  }


  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="text-center">
          <div className="flex items-center justify-center gap-4 mb-4">
            <h1 className="text-3xl font-bold text-gray-900">Planlar ve Fiyatlandırma</h1>
            <Button
              variant="outline"
              size="sm"
              onClick={refreshData}
              className="flex items-center gap-2"
            >
              🔄 Yenile
            </Button>
          </div>
          <p className="text-gray-600">
            İhtiyacınıza en uygun planı seçin ve email otomasyonunuzu büyütün
          </p>
        </div>

        {/* Current Plan Status - Dynamic */}
        {currentPlan && (
          <Card className={`border-2 ${
            currentPlan.name === 'Free' ? 'bg-gray-50 border-gray-200' :
            currentPlan.name === 'Starter' ? 'bg-blue-50 border-blue-200' :
            currentPlan.name === 'Professional' ? 'bg-purple-50 border-purple-200' :
            currentPlan.name === 'Enterprise' ? 'bg-gold-50 border-yellow-200' : 'bg-blue-50 border-blue-200'
          }`}>
            <CardHeader>
              <CardTitle className={`flex items-center justify-between ${
                currentPlan.name === 'Free' ? 'text-gray-900' :
                currentPlan.name === 'Starter' ? 'text-blue-900' :
                currentPlan.name === 'Professional' ? 'text-purple-900' :
                currentPlan.name === 'Enterprise' ? 'text-yellow-900' : 'text-blue-900'
              }`}>
                <span>
                  {currentPlan.name === 'Free' ? '🆓' :
                   currentPlan.name === 'Starter' ? '🚀' :
                   currentPlan.name === 'Professional' ? '💼' :
                   currentPlan.name === 'Enterprise' ? '🏢' : '📋'} Current Plan: {currentPlan.name}
                </span>
                {currentPlan.name !== 'Enterprise' && (
                  <span className="text-sm bg-green-100 text-green-800 px-2 py-1 rounded-full">
                    Active
                  </span>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Aylık Sorgu:</span>
                      <span className="font-semibold">{currentPlan.max_queries_per_month}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Aylık Email:</span>
                      <span className="font-semibold text-blue-600">{currentPlan.max_emails_per_month === -1 ? 'Sınırsız' : currentPlan.max_emails_per_month}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Dosya Yükleme:</span>
                      <span className="font-semibold">{currentPlan.max_file_uploads}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Sorgu Başına Sonuç:</span>
                      <span className="font-semibold">{currentPlan.max_results_per_query}</span>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`text-3xl font-bold ${
                    currentPlan.name === 'Free' ? 'text-gray-900' :
                    currentPlan.name === 'Starter' ? 'text-blue-900' :
                    currentPlan.name === 'Professional' ? 'text-purple-900' :
                    currentPlan.name === 'Enterprise' ? 'text-yellow-900' : 'text-blue-900'
                  }`}>
                    {currentPlan.price === 0 ? 'Free' : `$${currentPlan.price}/month`}
                  </p>
                  {subscription?.current_period_end && (
                    <p className="text-sm text-gray-600">
                      Sonraki ödeme: {new Date(subscription.current_period_end).toLocaleDateString('tr-TR')}
                    </p>
                  )}
                  {currentPlan.price === 0 && (
                    <p className="text-sm text-gray-600">
                      Sınırsız kullanım
                    </p>
                  )}
                </div>
              </div>
              
              {/* Plan Features Preview */}
              {currentPlan.features && currentPlan.features.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Aktif Özellikler:</h4>
                  <div className="flex flex-wrap gap-2">
                    {currentPlan.features.slice(0, 3).map((feature: string, index: number) => (
                      <span key={index} className={`px-2 py-1 rounded-full text-xs ${
                        currentPlan.name === 'Ücretsiz' ? 'bg-gray-100 text-gray-700' :
                        currentPlan.name === 'Başlangıç' ? 'bg-blue-100 text-blue-700' :
                        currentPlan.name === 'Profesyonel' ? 'bg-purple-100 text-purple-700' :
                        currentPlan.name === 'Kurumsal' ? 'bg-yellow-100 text-yellow-700' : 'bg-blue-100 text-blue-700'
                      }`}>
                        {feature}
                      </span>
                    ))}
                    {currentPlan.features.length > 3 && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded-full text-xs">
                        +{currentPlan.features.length - 3} daha
                      </span>
                    )}
                  </div>
                </div>
              )}
              
              {/* Upgrade Suggestion */}
              {currentPlan.name !== 'Kurumsal' && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-700">Daha fazla özellik mi istiyorsunuz?</p>
                      <p className="text-xs text-gray-600">Planınızı yükselterek daha fazla sorgu ve özellik kazanın</p>
                    </div>
                    <div className="text-sm text-blue-600 font-medium">
                      ⬇ Aşağıdan seçin
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Plans Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {plans.map((plan) => (
            <Card 
              key={plan._id} 
              className={`relative ${
                plan.name === 'Starter' ? 'border-blue-500 shadow-lg' : ''
              } ${currentPlan?._id === plan._id ? 'bg-gray-50 border-green-500 shadow-lg' : ''}`}
            >
              {plan.name === 'Starter' && currentPlan?._id !== plan._id && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <span className="bg-blue-500 text-white px-3 py-1 rounded-full text-xs font-medium">
                    Most Popular
                  </span>
                </div>
              )}
              
              {currentPlan?._id === plan._id && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <span className="bg-green-500 text-white px-3 py-1 rounded-full text-xs font-medium">
                    ✓ Current Plan
                  </span>
                </div>
              )}

              <CardHeader className="text-center">
                <CardTitle className="text-xl">{plan.name}</CardTitle>
                <div className="mt-4">
                  <span className="text-4xl font-bold">${plan.price}</span>
                  <span className="text-gray-500">/month</span>
                </div>
                <CardDescription>
                  {plan.max_queries_per_month} sorgu limiti • {plan.max_emails_per_month === -1 ? 'Sınırsız' : plan.max_emails_per_month} email/ay
                </CardDescription>
              </CardHeader>

              <CardContent>
                <ul className="space-y-3">
                  {plan.features.map((feature: string, index: number) => (
                    <li key={index} className="flex items-center text-sm">
                      <span className="text-green-500 mr-2">✓</span>
                      {feature}
                    </li>
                  ))}
                </ul>

                <div className="mt-6">
                  <Button
                    className={`w-full ${
                      plan.name === 'Starter' 
                        ? 'bg-blue-600 hover:bg-blue-700' 
                        : subscription?.plan?._id === plan._id
                        ? 'bg-gray-400 cursor-not-allowed'
                        : ''
                    }`}
                    onClick={() => handlePlanSelect(plan)}
                    disabled={currentPlan?._id === plan._id || isLoading}
                  >
                    {currentPlan?._id === plan._id
                      ? 'Current Plan' 
                      : isLoading
                      ? 'Processing...'
                      : plan.price === 0
                      ? 'Get Started Free'
                      : currentPlan && currentPlan.price < plan.price
                      ? 'Upgrade'
                      : currentPlan && currentPlan.price > plan.price
                      ? 'Downgrade'
                      : 'Select Plan'
                    }
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Cost Breakdown Section */}
        {!costsLoading && costs.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Cost Breakdown</CardTitle>
              <CardDescription>
                Transparent pricing based on real infrastructure costs
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {costs.map((cost) => (
                  <div key={cost.name} className="bg-gray-50 rounded-lg p-4">
                    <div className="text-center mb-4">
                      <h3 className="text-lg font-semibold text-gray-900">{cost.name}</h3>
                      <div className="text-2xl font-bold text-blue-900">
                        ${cost.price}
                        <span className="text-sm text-gray-500">/month</span>
                      </div>
                      <div className="text-sm text-green-600 font-semibold">
                        {cost.profit_margin}% profit margin
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Server:</span>
                        <span className="font-semibold">${cost.cost_breakdown.server_cost}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">AI:</span>
                        <span className="font-semibold">${cost.cost_breakdown.ai_cost}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Email:</span>
                        <span className="font-semibold">${cost.cost_breakdown.email_cost}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Domain:</span>
                        <span className="font-semibold">${cost.cost_breakdown.domain_cost}</span>
                      </div>
                      <div className="border-t border-gray-300 pt-2 mt-2">
                        <div className="flex justify-between text-sm font-bold">
                          <span className="text-gray-900">Total Cost:</span>
                          <span className="text-red-600">${cost.cost_breakdown.total_cost}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Features Comparison */}
        <Card>
          <CardHeader>
            <CardTitle>Özellik Karşılaştırması</CardTitle>
            <CardDescription>
              Tüm planların detaylı özellik karşılaştırması
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3">Özellik</th>
                    {plans.map(plan => (
                      <th key={plan._id} className="text-center py-3">{plan.name}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b">
                    <td className="py-3">Aylık Sorgu Limiti</td>
                    {plans.map(plan => (
                      <td key={plan._id} className="text-center">{plan.max_queries_per_month}</td>
                    ))}
                  </tr>
                  <tr className="border-b">
                    <td className="py-3">Aylık Email Limiti</td>
                    {plans.map(plan => (
                      <td key={plan._id} className="text-center font-semibold text-blue-600">
                        {plan.max_emails_per_month === -1 ? 'Sınırsız' : plan.max_emails_per_month}
                      </td>
                    ))}
                  </tr>
                  <tr className="border-b">
                    <td className="py-3">Dosya Yükleme Limiti</td>
                    {plans.map(plan => (
                      <td key={plan._id} className="text-center">
                        {plan.max_file_uploads === -1 ? 'Sınırsız' : plan.max_file_uploads}
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* FAQ */}
        <Card>
          <CardHeader>
            <CardTitle>Sıkça Sorulan Sorular</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h4 className="font-medium">Plan değişikliği nasıl yapılır?</h4>
              <p className="text-sm text-gray-600">
                İstediğiniz planın "Planı Seç" butonuna tıklayarak anında plan değişikliği yapabilirsiniz.
              </p>
            </div>
            
            <div>
              <h4 className="font-medium">Ödeme güvenli mi?</h4>
              <p className="text-sm text-gray-600">
                Evet, tüm ödemeler Stripe üzerinden güvenli şekilde işlenmektedir.
              </p>
            </div>
            
            <div>
              <h4 className="font-medium">İptal etme politikası nedir?</h4>
              <p className="text-sm text-gray-600">
                İstediğiniz zaman planınızı iptal edebilirsiniz. İptal sonrası mevcut dönem sonuna kadar hizmet alabilirsiniz.
              </p>
            </div>
          </CardContent>
        </Card>

      </div>
    </DashboardLayout>
  )
}

