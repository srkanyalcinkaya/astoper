'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { useState, useEffect } from 'react'
import Image from 'next/image'
import { usePlans } from '@/lib/hooks/usePlans'
import { usePlanCosts } from '@/lib/hooks/usePlanCosts'

export default function LandingPage() {
  const [isVisible, setIsVisible] = useState(false)
  const [currentFeature, setCurrentFeature] = useState(0)
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })
  const { plans, loading, error } = usePlans()
  const { costs, loading: costsLoading, error: costsError } = usePlanCosts()

  useEffect(() => {
    setIsVisible(true)
    
    const interval = setInterval(() => {
      setCurrentFeature((prev) => (prev + 1) % 3)
    }, 3000)

    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY })
    }

    window.addEventListener('mousemove', handleMouseMove)

    return () => {
      clearInterval(interval)
      window.removeEventListener('mousemove', handleMouseMove)
    }
  }, [])

  const features = [
    {
      icon: "⚡",
      title: "Hızlı Kurulum",
      description: "Sadece birkaç dakikada email otomasyonunuzu kurun ve çalıştırın. Tek tıkla Google aramaları başlatın, email adreslerini otomatik bulun ve hedef müşterilerinize ulaşın.",
      color: "from-blue-500 to-blue-600",
      details: [
        "5 dakikada kurulum",
        "Tek tıkla başlatma",
        "Otomatik email bulma",
        "Anında sonuç alma"
      ]
    },
    {
      icon: "🎯",
      title: "Akıllı Hedefleme", 
      description: "Gelişmiş algoritmalarımız ile doğru müşterileri bulun. Sektör, lokasyon, şirket büyüklüğü gibi kriterlere göre hedefleme yapın.",
      color: "from-green-500 to-green-600",
      details: [
        "%95+ doğruluk oranı",
        "Sektörel filtreleme",
        "Lokasyon bazlı arama",
        "Şirket büyüklüğü seçimi"
      ]
    },
    {
      icon: "📈",
      title: "Ölçeklenebilir Planlar",
      description: "İhtiyacınıza göre ölçeklenebilir planlar ve özellikler. Küçük işletmeden büyük kurumsal şirketlere kadar herkese uygun çözümler.",
      color: "from-blue-600 to-blue-700",
      details: [
        "Esnek fiyatlandırma",
        "İhtiyaca göre özelleştirme",
        "Sınırsız email gönderimi",
        "7/24 teknik destek"
      ]
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100 overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-200/30 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-300/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-blue-100/20 rounded-full blur-3xl animate-pulse delay-500"></div>
        
        {/* Mouse follower effect */}
        <div 
          className="absolute w-32 h-32 bg-blue-200/20 rounded-full blur-2xl transition-all duration-300 pointer-events-none"
          style={{
            left: mousePosition.x - 64,
            top: mousePosition.y - 64,
          }}
        ></div>
      </div>

      {/* Header */}
      <header className="relative z-10 border-b border-blue-200/30 bg-white/80 backdrop-blur-xl shadow-sm">
        <div className="container mx-auto px-4 py-6 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
                <div className="w-6 h-6 bg-white rounded-sm transform rotate-45"></div>
                <div className="absolute w-4 h-4 bg-blue-300 rounded-sm transform rotate-45"></div>
              </div>
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-ping"></div>
            </div>
            <span className="font-bold text-2xl text-blue-900">Astoper</span>
          </div>
          <div className="flex space-x-4">
            <Link href="/login">
              <Button variant="outline" className="bg-white/80 border-blue-300 text-blue-700 hover:bg-blue-50 backdrop-blur-sm">
                Giriş Yap
              </Button>
            </Link>
            <Link href="/register">
              <Button className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200">
                Ücretsiz Başla
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative z-10 py-12 md:py-20 px-4">
        <div className="container mx-auto text-center">
          <div className={`transform transition-all duration-1000 ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'}`}>
            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-blue-900 mb-6 md:mb-8 leading-tight">
              Email Otomasyonunuzu
              <br />
              <span className="gradient-text animate-pulse">
                Kolaylaştırın
              </span>
            </h1>
            <p className="text-lg sm:text-xl md:text-2xl text-blue-700 mb-6 md:mb-8 max-w-4xl mx-auto leading-relaxed animate-fadeInUp">
              Astoper ile hedef müşterilerinize otomatik email gönderin. Arama sorguları ve URL'ler ile 
              potansiyel müşterileri bulun, onlara ulaşın ve satışlarınızı artırın.
            </p>
            <p className="text-base sm:text-lg text-blue-600 mb-8 md:mb-12 max-w-3xl mx-auto leading-relaxed">
              🎯 <strong>Google'da arama yapın</strong> → 📧 <strong>Email adreslerini bulun</strong> → 🚀 <strong>Otomatik email gönderin</strong> → 💰 <strong>Satışlarınızı artırın</strong>
            </p>
            <div className="flex flex-col sm:flex-row gap-4 md:gap-6 justify-center max-w-2xl mx-auto">
              <Link href="/register" className="flex-1">
                <Button size="lg" className="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white text-base sm:text-lg px-6 md:px-8 py-3 md:py-4 shadow-2xl hover:shadow-blue-500/25 transform hover:scale-105 transition-all duration-300 animate-glow">
                  <span className="mr-2 animate-bounce">🚀</span>
                  Ücretsiz Deneyin
                </Button>
              </Link>
              <Link href="/plans" className="flex-1">
                <Button variant="outline" size="lg" className="w-full bg-white/80 border-blue-300 text-blue-700 hover:bg-blue-50 text-base sm:text-lg px-6 md:px-8 py-3 md:py-4 backdrop-blur-sm transform hover:scale-105 transition-all duration-300 hover-lift">
                  Planları İncele
                </Button>
              </Link>
            </div>
          </div>
          
          {/* Floating elements */}
          <div className="absolute top-20 left-10 w-4 h-4 bg-blue-400 rounded-full animate-float opacity-60"></div>
          <div className="absolute top-40 right-20 w-6 h-6 bg-blue-300 rounded-full animate-float delay-1000 opacity-60"></div>
          <div className="absolute bottom-20 left-20 w-3 h-3 bg-blue-500 rounded-full animate-float delay-500 opacity-60"></div>
          <div className="absolute bottom-40 right-10 w-5 h-5 bg-blue-400 rounded-full animate-float delay-700 opacity-60"></div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative z-10 py-12 md:py-20 bg-white/80 backdrop-blur-sm">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-center text-blue-900 mb-12 md:mb-16 animate-fadeInUp">
            Neden <span className="gradient-text">Astoper</span>?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
            {features.map((feature, index) => (
              <div 
                key={index}
                className={`transform transition-all duration-500 hover:scale-105 hover-lift ${
                  currentFeature === index ? 'scale-105 animate-glow' : 'scale-100'
                }`}
                style={{
                  animationDelay: `${index * 200}ms`
                }}
              >
                <div className="bg-white rounded-2xl p-6 md:p-8 border border-blue-200 hover:border-blue-300 transition-all duration-300 hover:shadow-2xl shadow-lg">
                  <div className={`w-16 h-16 md:w-20 md:h-20 bg-gradient-to-br ${feature.color} rounded-2xl flex items-center justify-center mx-auto mb-4 md:mb-6 text-2xl md:text-3xl shadow-lg animate-float`}>
                    {feature.icon}
                  </div>
                  <h3 className="text-xl md:text-2xl font-bold text-blue-900 mb-3 md:mb-4 text-center">{feature.title}</h3>
                  <p className="text-sm md:text-base text-blue-700 text-center leading-relaxed mb-4 md:mb-6">
                    {feature.description}
                  </p>
                  <ul className="space-y-2">
                    {feature.details.map((detail, detailIndex) => (
                      <li key={detailIndex} className="flex items-center text-sm md:text-base text-blue-600">
                        <span className="w-2 h-2 bg-blue-500 rounded-full mr-3 flex-shrink-0"></span>
                        <span className="leading-relaxed">{detail}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="relative z-10 py-12 md:py-20 bg-blue-50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-center text-blue-900 mb-4">
            Pricing <span className="gradient-text">Plans</span>
          </h2>
          <p className="text-lg sm:text-xl text-blue-700 text-center mb-12 md:mb-16 max-w-3xl mx-auto">
            Choose the plan that fits your needs and start your email automation
          </p>
          
          {loading ? (
            <div className="flex justify-center items-center py-20">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
          ) : error ? (
            <div className="text-center py-20">
              <p className="text-red-500 mb-4">Planlar yüklenirken bir hata oluştu</p>
              <p className="text-blue-600">Lütfen sayfayı yenileyin</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8 max-w-6xl mx-auto">
              {plans.slice(0, 3).map((plan, index) => (
                <div 
                  key={plan._id}
                  className={`bg-white rounded-2xl p-6 md:p-8 border transition-all duration-300 hover:shadow-xl hover-lift ${
                    index === 1 ? 'border-2 border-blue-500 hover:border-blue-600 relative' : 'border-blue-200 hover:border-blue-300'
                  }`}
                >
                  {index === 1 && (
                    <div className="absolute -top-3 md:-top-4 left-1/2 transform -translate-x-1/2">
                      <span className="bg-blue-500 text-white px-3 md:px-4 py-1 md:py-2 rounded-full text-xs md:text-sm font-semibold">
                        Most Popular
                      </span>
                    </div>
                  )}
                  <div className="text-center mb-6 md:mb-8">
                    <h3 className="text-xl md:text-2xl font-bold text-blue-900 mb-2">{plan.name}</h3>
                    <p className="text-sm md:text-base text-blue-600 mb-4">
                      {index === 0 ? 'For small businesses' : 
                       index === 1 ? 'For growing businesses' : 
                       'For large enterprises'}
                    </p>
                    <div className="text-3xl md:text-4xl font-bold text-blue-900 mb-2">
                      ${plan.price.toLocaleString()}
                      <span className="text-base md:text-lg text-blue-600">/month</span>
                    </div>
                    <p className="text-sm md:text-base text-blue-600">
                      {plan.max_emails_per_month === 0 ? 'Unlimited emails' : `${plan.max_emails_per_month.toLocaleString()} emails/month`}
                    </p>
                  </div>
                  <ul className="space-y-3 md:space-y-4 mb-6 md:mb-8">
                    {plan.features.slice(0, 6).map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-start text-sm md:text-base text-blue-700">
                        <span className="w-4 h-4 md:w-5 md:h-5 bg-green-500 rounded-full flex items-center justify-center mr-3 mt-0.5 flex-shrink-0">
                          <span className="text-white text-xs">✓</span>
                        </span>
                        <span className="leading-relaxed">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <Link href="/register">
                    <Button className="w-full bg-blue-500 hover:bg-blue-600 text-white text-sm md:text-base py-2 md:py-3">
                      {index === 2 ? 'Contact Us' : 'Get Started'}
                    </Button>
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Cost Breakdown Section */}
      <section className="relative z-10 py-12 md:py-20 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-center text-blue-900 mb-4">
            Cost <span className="gradient-text">Breakdown</span>
          </h2>
          <p className="text-lg sm:text-xl text-blue-700 text-center mb-12 md:mb-16 max-w-3xl mx-auto">
            Transparent pricing based on real infrastructure costs
          </p>
          
          {costsLoading ? (
            <div className="flex justify-center items-center py-20">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
          ) : costsError ? (
            <div className="text-center py-20">
              <p className="text-red-500 mb-4">Cost information could not be loaded</p>
              <p className="text-blue-600">Please refresh the page</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8 max-w-7xl mx-auto">
              {costs.map((cost, index) => (
                <div 
                  key={cost.name}
                  className="bg-white rounded-2xl p-6 md:p-8 border border-blue-200 hover:border-blue-300 transition-all duration-300 hover:shadow-xl hover-lift"
                >
                  <div className="text-center mb-6">
                    <h3 className="text-xl md:text-2xl font-bold text-blue-900 mb-2">{cost.name}</h3>
                    <div className="text-3xl md:text-4xl font-bold text-blue-900 mb-2">
                      ${cost.price}
                      <span className="text-base md:text-lg text-blue-600">/month</span>
                    </div>
                    <div className="text-sm text-green-600 font-semibold">
                      {cost.profit_margin}% profit margin
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-blue-600">Server Cost:</span>
                      <span className="font-semibold">${cost.cost_breakdown.server_cost}</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-blue-600">AI Cost:</span>
                      <span className="font-semibold">${cost.cost_breakdown.ai_cost}</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-blue-600">Email Cost:</span>
                      <span className="font-semibold">${cost.cost_breakdown.email_cost}</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-blue-600">Domain Cost:</span>
                      <span className="font-semibold">${cost.cost_breakdown.domain_cost}</span>
                    </div>
                    <div className="border-t border-blue-200 pt-2 mt-3">
                      <div className="flex justify-between items-center text-base font-bold">
                        <span className="text-blue-900">Total Cost:</span>
                        <span className="text-red-600">${cost.cost_breakdown.total_cost}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Stats Section */}
      <section className="relative z-10 py-12 md:py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 md:gap-8">
            <div className="text-center hover-lift">
              <div className="text-3xl md:text-4xl lg:text-5xl font-bold text-blue-900 mb-2 gradient-text animate-pulse">10K+</div>
              <div className="text-sm md:text-base text-blue-600">Aktif Kullanıcı</div>
            </div>
            <div className="text-center hover-lift">
              <div className="text-3xl md:text-4xl lg:text-5xl font-bold text-blue-900 mb-2 gradient-text animate-pulse delay-200">1M+</div>
              <div className="text-sm md:text-base text-blue-600">Gönderilen Email</div>
            </div>
            <div className="text-center hover-lift">
              <div className="text-3xl md:text-4xl lg:text-5xl font-bold text-blue-900 mb-2 gradient-text animate-pulse delay-400">%95</div>
              <div className="text-sm md:text-base text-blue-600">Başarı Oranı</div>
            </div>
            <div className="text-center hover-lift">
              <div className="text-3xl md:text-4xl lg:text-5xl font-bold text-blue-900 mb-2 gradient-text animate-pulse delay-600">24/7</div>
              <div className="text-sm md:text-base text-blue-600">Destek</div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="relative z-10 py-12 md:py-20 bg-blue-50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-center text-blue-900 mb-4">
            Nasıl <span className="gradient-text">Çalışır?</span>
          </h2>
          <p className="text-lg sm:text-xl text-blue-700 text-center mb-12 md:mb-16 max-w-3xl mx-auto">
            Astoper ile email otomasyonunuzu 3 basit adımda başlatın
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-8 max-w-5xl mx-auto">
            <div className="text-center">
              <div className="w-16 h-16 md:w-20 md:h-20 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-4 md:mb-6 text-2xl md:text-3xl text-white shadow-lg">
                1
              </div>
              <h3 className="text-xl md:text-2xl font-bold text-blue-900 mb-3 md:mb-4">Arama Yapın</h3>
              <p className="text-sm md:text-base text-blue-700 leading-relaxed mb-4">
                Google'da hedef müşterilerinizi bulun. "İstanbul'da yazılım şirketleri" gibi arama sorguları kullanın.
              </p>
              <div className="mt-4 md:mt-6 bg-white p-3 md:p-4 rounded-lg border border-blue-200">
                <p className="text-xs md:text-sm text-blue-600 font-mono">"Ankara'da dijital pazarlama ajansları"</p>
              </div>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 md:w-20 md:h-20 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-4 md:mb-6 text-2xl md:text-3xl text-white shadow-lg">
                2
              </div>
              <h3 className="text-xl md:text-2xl font-bold text-blue-900 mb-3 md:mb-4">Email Bulun</h3>
              <p className="text-sm md:text-base text-blue-700 leading-relaxed mb-4">
                Astoper otomatik olarak web sitelerinden email adreslerini bulur ve doğrular.
              </p>
              <div className="mt-4 md:mt-6 bg-white p-3 md:p-4 rounded-lg border border-blue-200">
                <p className="text-xs md:text-sm text-blue-600">info@ajans.com</p>
                <p className="text-xs md:text-sm text-blue-600">satış@ajans.com</p>
                <p className="text-xs md:text-sm text-blue-600">destek@ajans.com</p>
              </div>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 md:w-20 md:h-20 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-4 md:mb-6 text-2xl md:text-3xl text-white shadow-lg">
                3
              </div>
              <h3 className="text-xl md:text-2xl font-bold text-blue-900 mb-3 md:mb-4">Email Gönderin</h3>
              <p className="text-sm md:text-base text-blue-700 leading-relaxed mb-4">
                Hazır şablonlarınızı kullanarak otomatik email gönderin ve sonuçları takip edin.
              </p>
              <div className="mt-4 md:mt-6 bg-white p-3 md:p-4 rounded-lg border border-blue-200">
                <p className="text-xs md:text-sm text-green-600">✓ 150 email gönderildi</p>
                <p className="text-xs md:text-sm text-green-600">✓ 45 açılma oranı</p>
                <p className="text-xs md:text-sm text-green-600">✓ 12 yanıt alındı</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Use Cases Section */}
      <section className="relative z-10 py-12 md:py-20 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-center text-blue-900 mb-4">
            Kullanım <span className="gradient-text">Örnekleri</span>
          </h2>
          <p className="text-lg sm:text-xl text-blue-700 text-center mb-12 md:mb-16 max-w-3xl mx-auto">
            Astoper'ı farklı sektörlerde nasıl kullanabilirsiniz?
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
            <div className="bg-blue-50 rounded-2xl p-6 md:p-8 border border-blue-200 hover:border-blue-300 transition-all duration-300 hover:shadow-xl">
              <div className="w-12 h-12 md:w-16 md:h-16 bg-blue-500 rounded-xl flex items-center justify-center mb-4 md:mb-6 text-xl md:text-2xl">
                💼
              </div>
              <h3 className="text-lg md:text-xl font-bold text-blue-900 mb-3 md:mb-4">B2B Satış</h3>
              <p className="text-sm md:text-base text-blue-700 mb-3 md:mb-4">
                Potansiyel müşteri şirketlerini bulun ve onlara ulaşın.
              </p>
              <ul className="space-y-1 md:space-y-2 text-sm md:text-base text-blue-600">
                <li>• "İstanbul'da yazılım şirketleri"</li>
                <li>• "Ankara'da danışmanlık firmaları"</li>
                <li>• "İzmir'de e-ticaret şirketleri"</li>
              </ul>
            </div>
            
            <div className="bg-blue-50 rounded-2xl p-6 md:p-8 border border-blue-200 hover:border-blue-300 transition-all duration-300 hover:shadow-xl">
              <div className="w-12 h-12 md:w-16 md:h-16 bg-blue-500 rounded-xl flex items-center justify-center mb-4 md:mb-6 text-xl md:text-2xl">
                🏢
              </div>
              <h3 className="text-lg md:text-xl font-bold text-blue-900 mb-3 md:mb-4">Emlak</h3>
              <p className="text-sm md:text-base text-blue-700 mb-3 md:mb-4">
                Emlak danışmanları için müşteri bulma.
              </p>
              <ul className="space-y-1 md:space-y-2 text-sm md:text-base text-blue-600">
                <li>• "İstanbul'da emlak ofisleri"</li>
                <li>• "Ankara'da inşaat şirketleri"</li>
                <li>• "İzmir'de mimarlık büroları"</li>
              </ul>
            </div>
            
            <div className="bg-blue-50 rounded-2xl p-6 md:p-8 border border-blue-200 hover:border-blue-300 transition-all duration-300 hover:shadow-xl">
              <div className="w-12 h-12 md:w-16 md:h-16 bg-blue-500 rounded-xl flex items-center justify-center mb-4 md:mb-6 text-xl md:text-2xl">
                🎯
              </div>
              <h3 className="text-lg md:text-xl font-bold text-blue-900 mb-3 md:mb-4">Pazarlama</h3>
              <p className="text-sm md:text-base text-blue-700 mb-3 md:mb-4">
                Pazarlama ajansları için müşteri bulma.
              </p>
              <ul className="space-y-1 md:space-y-2 text-sm md:text-base text-blue-600">
                <li>• "İstanbul'da pazarlama ajansları"</li>
                <li>• "Ankara'da reklam şirketleri"</li>
                <li>• "İzmir'de sosyal medya ajansları"</li>
              </ul>
            </div>
            
            <div className="bg-blue-50 rounded-2xl p-6 md:p-8 border border-blue-200 hover:border-blue-300 transition-all duration-300 hover:shadow-xl">
              <div className="w-12 h-12 md:w-16 md:h-16 bg-blue-500 rounded-xl flex items-center justify-center mb-4 md:mb-6 text-xl md:text-2xl">
                🏥
              </div>
              <h3 className="text-lg md:text-xl font-bold text-blue-900 mb-3 md:mb-4">Sağlık</h3>
              <p className="text-sm md:text-base text-blue-700 mb-3 md:mb-4">
                Sağlık sektörü için hedefleme.
              </p>
              <ul className="space-y-1 md:space-y-2 text-sm md:text-base text-blue-600">
                <li>• "İstanbul'da özel hastaneler"</li>
                <li>• "Ankara'da klinikler"</li>
                <li>• "İzmir'de diş hekimleri"</li>
              </ul>
            </div>
            
            <div className="bg-blue-50 rounded-2xl p-6 md:p-8 border border-blue-200 hover:border-blue-300 transition-all duration-300 hover:shadow-xl">
              <div className="w-12 h-12 md:w-16 md:h-16 bg-blue-500 rounded-xl flex items-center justify-center mb-4 md:mb-6 text-xl md:text-2xl">
                🎓
              </div>
              <h3 className="text-lg md:text-xl font-bold text-blue-900 mb-3 md:mb-4">Eğitim</h3>
              <p className="text-sm md:text-base text-blue-700 mb-3 md:mb-4">
                Eğitim kurumları için hedefleme.
              </p>
              <ul className="space-y-1 md:space-y-2 text-sm md:text-base text-blue-600">
                <li>• "İstanbul'da özel okullar"</li>
                <li>• "Ankara'da kurs merkezleri"</li>
                <li>• "İzmir'de dil okulları"</li>
              </ul>
            </div>
            
            <div className="bg-blue-50 rounded-2xl p-6 md:p-8 border border-blue-200 hover:border-blue-300 transition-all duration-300 hover:shadow-xl">
              <div className="w-12 h-12 md:w-16 md:h-16 bg-blue-500 rounded-xl flex items-center justify-center mb-4 md:mb-6 text-xl md:text-2xl">
                🍽️
              </div>
              <h3 className="text-lg md:text-xl font-bold text-blue-900 mb-3 md:mb-4">Restoran</h3>
              <p className="text-sm md:text-base text-blue-700 mb-3 md:mb-4">
                Restoran ve catering şirketleri.
              </p>
              <ul className="space-y-1 md:space-y-2 text-sm md:text-base text-blue-600">
                <li>• "İstanbul'da restoranlar"</li>
                <li>• "Ankara'da catering şirketleri"</li>
                <li>• "İzmir'de kafeler"</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="relative z-10 py-12 md:py-20 bg-blue-50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-center text-blue-900 mb-4">
            Sıkça Sorulan <span className="gradient-text">Sorular</span>
          </h2>
          <p className="text-lg sm:text-xl text-blue-700 text-center mb-12 md:mb-16 max-w-3xl mx-auto">
            Astoper hakkında merak ettiğiniz her şey
          </p>
          
          <div className="max-w-4xl mx-auto space-y-4 md:space-y-6">
            <div className="bg-white rounded-2xl p-6 md:p-8 border border-blue-200 hover:border-blue-300 transition-all duration-300">
              <h3 className="text-lg md:text-xl font-bold text-blue-900 mb-3 md:mb-4">Astoper nasıl çalışır?</h3>
              <p className="text-sm md:text-base text-blue-700 leading-relaxed">
                Astoper, Google arama sonuçlarını analiz ederek web sitelerinden email adreslerini otomatik olarak bulur. 
                Bulunan email adreslerini doğrular ve size temiz bir liste sunar. Sonrasında hazır şablonlarınızla 
                otomatik email gönderimi yapabilirsiniz.
              </p>
            </div>
            
            <div className="bg-white rounded-2xl p-6 md:p-8 border border-blue-200 hover:border-blue-300 transition-all duration-300">
              <h3 className="text-lg md:text-xl font-bold text-blue-900 mb-3 md:mb-4">Email gönderim limitleri nelerdir?</h3>
              <p className="text-sm md:text-base text-blue-700 leading-relaxed">
                Starter planında aylık 1,000 email, Professional planında 5,000 email, Enterprise planında ise 
                sınırsız email gönderimi yapabilirsiniz. Tüm planlarımızda günlük gönderim limitleri bulunmaktadır 
                ve spam koruması sağlanmaktadır.
              </p>
            </div>
            
            <div className="bg-white rounded-2xl p-6 md:p-8 border border-blue-200 hover:border-blue-300 transition-all duration-300">
              <h3 className="text-lg md:text-xl font-bold text-blue-900 mb-3 md:mb-4">Email adreslerinin doğruluğu nasıl sağlanıyor?</h3>
              <p className="text-sm md:text-base text-blue-700 leading-relaxed">
                Astoper, gelişmiş algoritmalar kullanarak email adreslerinin geçerliliğini kontrol eder. 
                Bounce oranını minimize etmek için çoklu doğrulama yöntemleri kullanır ve %95+ doğruluk oranı sağlar.
              </p>
            </div>
            
            <div className="bg-white rounded-2xl p-6 md:p-8 border border-blue-200 hover:border-blue-300 transition-all duration-300">
              <h3 className="text-lg md:text-xl font-bold text-blue-900 mb-3 md:mb-4">Hangi email sağlayıcıları destekleniyor?</h3>
              <p className="text-sm md:text-base text-blue-700 leading-relaxed">
                Gmail, Outlook, Yahoo, Yandex ve diğer tüm popüler email sağlayıcıları desteklenmektedir. 
                Ayrıca kendi SMTP sunucunuzu da kullanabilirsiniz.
              </p>
            </div>
            
            <div className="bg-white rounded-2xl p-6 md:p-8 border border-blue-200 hover:border-blue-300 transition-all duration-300">
              <h3 className="text-lg md:text-xl font-bold text-blue-900 mb-3 md:mb-4">Veri güvenliği nasıl sağlanıyor?</h3>
              <p className="text-sm md:text-base text-blue-700 leading-relaxed">
                Tüm verileriniz SSL şifreleme ile korunur. GDPR uyumlu veri işleme politikalarımız bulunmaktadır. 
                Verileriniz sadece size aittir ve üçüncü taraflarla paylaşılmaz.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 py-12 md:py-20 bg-gradient-to-r from-blue-500 to-blue-600">
        <div className="container mx-auto px-4 text-center">
          <div className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 md:p-12 border border-white/20 animate-fadeInUp">
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-4 md:mb-6">
              Bugün <span className="gradient-text">Başlayın</span>
            </h2>
            <p className="text-blue-100 mb-6 md:mb-8 text-lg sm:text-xl max-w-2xl mx-auto animate-fadeInUp">
              Ücretsiz hesap oluşturun ve ilk email otomasyonunuzu başlatın. 14 gün ücretsiz deneme!
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center max-w-2xl mx-auto">
              <Link href="/register" className="flex-1">
                <Button size="lg" className="w-full bg-white text-blue-600 hover:bg-blue-50 text-base sm:text-lg md:text-xl px-6 md:px-12 py-3 md:py-6 shadow-2xl hover:shadow-white/25 transform hover:scale-105 transition-all duration-300">
                  <span className="mr-2 md:mr-3 animate-bounce">🚀</span>
                  Ücretsiz Deneyin
                </Button>
              </Link>
              <Link href="/plans" className="flex-1">
                <Button variant="outline" size="lg" className="w-full bg-transparent border-white text-white hover:bg-white/10 text-base sm:text-lg md:text-xl px-6 md:px-12 py-3 md:py-6 backdrop-blur-sm transform hover:scale-105 transition-all duration-300">
                  Planları İncele
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 bg-blue-900 text-white py-8 md:py-12">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 md:gap-8 mb-6 md:mb-8">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-6 h-6 md:w-8 md:h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                  <div className="w-3 h-3 md:w-4 md:h-4 bg-white rounded-sm transform rotate-45"></div>
                </div>
                <span className="font-bold text-lg md:text-xl">Astoper</span>
              </div>
              <p className="text-sm md:text-base text-blue-200 leading-relaxed">
                Email otomasyonunuzu kolaylaştırın. Hedef müşterilerinize ulaşın ve satışlarınızı artırın.
              </p>
            </div>
            
            <div>
              <h3 className="text-base md:text-lg font-bold mb-3 md:mb-4">Ürün</h3>
              <ul className="space-y-2 text-sm md:text-base text-blue-200">
                <li><a href="#" className="hover:text-white transition-colors">Özellikler</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Fiyatlandırma</a></li>
                <li><a href="#" className="hover:text-white transition-colors">API</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Entegrasyonlar</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-base md:text-lg font-bold mb-3 md:mb-4">Destek</h3>
              <ul className="space-y-2 text-sm md:text-base text-blue-200">
                <li><a href="#" className="hover:text-white transition-colors">Yardım Merkezi</a></li>
                <li><a href="#" className="hover:text-white transition-colors">İletişim</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Durum Sayfası</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Güvenlik</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-base md:text-lg font-bold mb-3 md:mb-4">Şirket</h3>
              <ul className="space-y-2 text-sm md:text-base text-blue-200">
                <li><a href="#" className="hover:text-white transition-colors">Hakkımızda</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Kariyer</a></li>
                <li><Link href="/privacy-policy" className="hover:text-white transition-colors">Gizlilik Politikası</Link></li>
                <li><Link href="/terms-of-service" className="hover:text-white transition-colors">Kullanım Şartları</Link></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-blue-800 pt-6 md:pt-8 text-center">
            <p className="text-sm md:text-base text-blue-200">&copy; 2024 Astoper Platform. Tüm hakları saklıdır.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
