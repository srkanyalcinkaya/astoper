import Link from 'next/link'

export default function PrivacyPolicyPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100">
      {/* Header */}
      <header className="border-b border-blue-200/30 bg-white/80 backdrop-blur-xl shadow-sm">
        <div className="container mx-auto px-4 py-6 flex justify-between items-center">
          <Link href="/" className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
              <div className="w-6 h-6 bg-white rounded-sm transform rotate-45"></div>
            </div>
            <span className="font-bold text-2xl text-blue-900">Astoper</span>
          </Link>
          <Link href="/" className="text-blue-600 hover:text-blue-700 font-medium">
            Ana Sayfaya Dön
          </Link>
        </div>
      </header>

      {/* Content */}
      <div className="container mx-auto px-4 py-12 max-w-4xl">
        <div className="bg-white rounded-2xl shadow-lg p-8 md:p-12">
          <h1 className="text-4xl font-bold text-blue-900 mb-8">Gizlilik Politikası</h1>
          <p className="text-blue-700 mb-8 text-lg">
            Son güncelleme: 19 Aralık 2024
          </p>

          <div className="prose prose-lg max-w-none">
            <section className="mb-8">
              <h2 className="text-2xl font-bold text-blue-900 mb-4">1. Giriş</h2>
              <p className="text-blue-700 leading-relaxed mb-4">
                Astoper olarak, kullanıcılarımızın gizliliğini korumak bizim için en önemli önceliklerden biridir. 
                Bu Gizlilik Politikası, Astoper platformunu kullanırken kişisel verilerinizin nasıl toplandığını, 
                kullanıldığını ve korunduğunu açıklamaktadır.
              </p>
              <p className="text-blue-700 leading-relaxed">
                Bu politikayı dikkatli bir şekilde okuyun ve herhangi bir sorunuz varsa bizimle iletişime geçin.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold text-blue-900 mb-4">2. Toplanan Bilgiler</h2>
              <h3 className="text-xl font-semibold text-blue-800 mb-3">2.1 Kişisel Bilgiler</h3>
              <p className="text-blue-700 leading-relaxed mb-4">
                Aşağıdaki kişisel bilgileri topluyoruz:
              </p>
              <ul className="list-disc list-inside text-blue-700 mb-4 space-y-2">
                <li>Ad ve soyad</li>
                <li>E-posta adresi</li>
                <li>Telefon numarası (isteğe bağlı)</li>
                <li>Şirket bilgileri</li>
                <li>Google hesap bilgileri (Google ile giriş yapıldığında)</li>
              </ul>

              <h3 className="text-xl font-semibold text-blue-800 mb-3">2.2 Teknik Bilgiler</h3>
              <ul className="list-disc list-inside text-blue-700 mb-4 space-y-2">
                <li>IP adresi</li>
                <li>Tarayıcı türü ve versiyonu</li>
                <li>İşletim sistemi</li>
                <li>Sayfa ziyaret süreleri</li>
                <li>Kullanılan özellikler</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold text-blue-900 mb-4">3. Bilgilerin Kullanımı</h2>
              <p className="text-blue-700 leading-relaxed mb-4">
                Topladığımız bilgileri aşağıdaki amaçlarla kullanırız:
              </p>
              <ul className="list-disc list-inside text-blue-700 mb-4 space-y-2">
                <li>Hizmetlerimizi sağlamak ve geliştirmek</li>
                <li>Kullanıcı hesaplarını yönetmek</li>
                <li>Müşteri desteği sağlamak</li>
                <li>Güvenlik ve dolandırıcılık önleme</li>
                <li>Yasal yükümlülüklerimizi yerine getirmek</li>
                <li>Hizmet kalitesini artırmak</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold text-blue-900 mb-4">4. Bilgi Paylaşımı</h2>
              <p className="text-blue-700 leading-relaxed mb-4">
                Kişisel bilgilerinizi aşağıdaki durumlar dışında üçüncü taraflarla paylaşmayız:
              </p>
              <ul className="list-disc list-inside text-blue-700 mb-4 space-y-2">
                <li>Yasal zorunluluklar</li>
                <li>Mahkeme kararları</li>
                <li>Güvenlik tehditleri</li>
                <li>Kullanıcının açık rızası</li>
                <li>Hizmet sağlayıcılarımız (veri işleme amaçlı)</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold text-blue-900 mb-4">5. Veri Güvenliği</h2>
              <p className="text-blue-700 leading-relaxed mb-4">
                Verilerinizin güvenliğini sağlamak için aşağıdaki önlemleri alıyoruz:
              </p>
              <ul className="list-disc list-inside text-blue-700 mb-4 space-y-2">
                <li>SSL şifreleme</li>
                <li>Güvenli sunucu altyapısı</li>
                <li>Düzenli güvenlik güncellemeleri</li>
                <li>Erişim kontrolü</li>
                <li>Veri yedekleme sistemleri</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold text-blue-900 mb-4">6. Çerezler (Cookies)</h2>
              <p className="text-blue-700 leading-relaxed mb-4">
                Web sitemizde kullanıcı deneyimini iyileştirmek için çerezler kullanırız. 
                Çerezler, web sitesinin düzgün çalışması, kullanıcı tercihlerinin hatırlanması 
                ve analitik verilerin toplanması için kullanılır.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold text-blue-900 mb-4">7. Kullanıcı Hakları</h2>
              <p className="text-blue-700 leading-relaxed mb-4">
                KVKK ve GDPR kapsamında aşağıdaki haklara sahipsiniz:
              </p>
              <ul className="list-disc list-inside text-blue-700 mb-4 space-y-2">
                <li>Kişisel verilerinize erişim hakkı</li>
                <li>Yanlış bilgilerin düzeltilmesi</li>
                <li>Verilerin silinmesi</li>
                <li>Veri işlemeye itiraz etme</li>
                <li>Veri taşınabilirliği</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold text-blue-900 mb-4">8. Çocukların Gizliliği</h2>
              <p className="text-blue-700 leading-relaxed mb-4">
                Hizmetlerimiz 18 yaş altındaki kişilere yönelik değildir. 18 yaş altındaki 
                kişilerden bilerek kişisel bilgi toplamayız.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold text-blue-900 mb-4">9. Politika Değişiklikleri</h2>
              <p className="text-blue-700 leading-relaxed mb-4">
                Bu Gizlilik Politikasını zaman zaman güncelleyebiliriz. Önemli değişiklikler 
                olduğunda kullanıcılarımızı e-posta yoluyla bilgilendiririz.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold text-blue-900 mb-4">10. İletişim</h2>
              <p className="text-blue-700 leading-relaxed mb-4">
                Gizlilik politikamız hakkında sorularınız varsa bizimle iletişime geçin:
              </p>
              <div className="bg-blue-50 p-6 rounded-lg">
                <p className="text-blue-700 mb-2"><strong>E-posta:</strong> privacy@astoper.com</p>
                <p className="text-blue-700 mb-2"><strong>Adres:</strong> İstanbul, Türkiye</p>
                <p className="text-blue-700"><strong>Telefon:</strong> +90 (212) 123 45 67</p>
              </div>
            </section>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-blue-900 text-white py-8">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; 2024 Astoper Platform. Tüm hakları saklıdır.</p>
        </div>
      </footer>
    </div>
  )
}
