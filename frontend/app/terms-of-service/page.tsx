import Link from 'next/link'

export default function TermsOfServicePage() {
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
          <h1 className="text-4xl font-bold text-blue-900 mb-8">Kullanım Şartları</h1>
          <p className="text-blue-700 mb-8 text-lg">
            Son güncelleme: 19 Aralık 2024
          </p>

          <div className="prose prose-lg max-w-none">
            <section className="mb-8">
              <h2 className="text-2xl font-bold text-blue-900 mb-4">1. Giriş ve Kabul</h2>
              <p className="text-blue-700 leading-relaxed mb-4">
                Bu Kullanım Şartları ("Şartlar"), Astoper platformunu ("Hizmet") kullanırken 
                geçerli olan kuralları ve koşulları belirler. Hizmetimizi kullanarak bu şartları 
                kabul etmiş sayılırsınız.
              </p>
              <p className="text-blue-700 leading-relaxed">
                Eğer bu şartları kabul etmiyorsanız, lütfen hizmetimizi kullanmayın.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold text-blue-900 mb-4">2. Hizmet Tanımı</h2>
              <p className="text-blue-700 leading-relaxed mb-4">
                Astoper, kullanıcıların email otomasyonu yapmalarını sağlayan bir platformdur. 
                Hizmetimiz şunları içerir:
              </p>
              <ul className="list-disc list-inside text-blue-700 mb-4 space-y-2">
                <li>Google arama sonuçlarından email adreslerini bulma</li>
                <li>Email adreslerini doğrulama</li>
                <li>Otomatik email gönderimi</li>
                <li>Email şablonları</li>
                <li>Raporlama ve analitik</li>
                <li>API erişimi (belirli planlarda)</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold text-blue-900 mb-4">3. Kullanıcı Yükümlülükleri</h2>
              <h3 className="text-xl font-semibold text-blue-800 mb-3">3.1 Yasaya Uygun Kullanım</h3>
              <p className="text-blue-700 leading-relaxed mb-4">
                Hizmetimizi kullanırken aşağıdaki kurallara uymalısınız:
              </p>
              <ul className="list-disc list-inside text-blue-700 mb-4 space-y-2">
                <li>Türkiye Cumhuriyeti yasalarına uygun hareket etmek</li>
                <li>Spam gönderimi yapmamak</li>
                <li>Telif hakkı ihlali yapmamak</li>
                <li>Başkalarının haklarını ihlal etmemek</li>
                <li>Zararlı içerik paylaşmamak</li>
              </ul>

              <h3 className="text-xl font-semibold text-blue-800 mb-3">3.2 Hesap Güvenliği</h3>
              <ul className="list-disc list-inside text-blue-700 mb-4 space-y-2">
                <li>Hesap bilgilerinizi güvenli tutmak</li>
                <li>Şifrenizi başkalarıyla paylaşmamak</li>
                <li>Şüpheli aktiviteleri derhal bildirmek</li>
                <li>Hesap bilgilerinizi güncel tutmak</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold text-blue-900 mb-4">4. Yasaklanan Kullanımlar</h2>
              <p className="text-blue-700 leading-relaxed mb-4">
                Aşağıdaki faaliyetler kesinlikle yasaktır:
              </p>
              <ul className="list-disc list-inside text-blue-700 mb-4 space-y-2">
                <li>Spam email gönderimi</li>
                <li>Sahte kimlik kullanımı</li>
                <li>Sistem güvenliğini tehdit etme</li>
                <li>Başka kullanıcıları rahatsız etme</li>
                <li>Telif hakkı ihlali</li>
                <li>Yasadışı faaliyetler</li>
                <li>Hizmeti tersine mühendislik yapma</li>
                <li>Bot veya otomatik araçlarla aşırı kullanım</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold text-blue-900 mb-4">5. Fiyatlandırma ve Ödeme</h2>
              <h3 className="text-xl font-semibold text-blue-800 mb-3">5.1 Fiyatlandırma</h3>
              <p className="text-blue-700 leading-relaxed mb-4">
                Hizmet fiyatlarımız web sitemizde belirtilmiştir. Fiyatlar önceden haber 
                verilmeksizin değiştirilebilir.
              </p>

              <h3 className="text-xl font-semibold text-blue-800 mb-3">5.2 Ödeme Koşulları</h3>
              <ul className="list-disc list-inside text-blue-700 mb-4 space-y-2">
                <li>Ödemeler peşin olarak yapılır</li>
                <li>İade politikamız 14 günlük deneme süresi içinde geçerlidir</li>
                <li>Ödeme yapılmadığında hizmet askıya alınır</li>
                <li>Vergi yükümlülükleri kullanıcıya aittir</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold text-blue-900 mb-4">6. Hizmet Kesintileri</h2>
              <p className="text-blue-700 leading-relaxed mb-4">
                Aşağıdaki durumlarda hizmetimizi geçici olarak kesebiliriz:
              </p>
              <ul className="list-disc list-inside text-blue-700 mb-4 space-y-2">
                <li>Teknik bakım ve güncellemeler</li>
                <li>Güvenlik tehditleri</li>
                <li>Yasal zorunluluklar</li>
                <li>Kullanıcı ihlalleri</li>
                <li>Ödeme gecikmeleri</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold text-blue-900 mb-4">7. Fikri Mülkiyet Hakları</h2>
              <p className="text-blue-700 leading-relaxed mb-4">
                Astoper platformu ve tüm içerikleri telif hakkı ve diğer fikri mülkiyet 
                yasaları ile korunmaktadır. Hizmetimizi kullanırken:
              </p>
              <ul className="list-disc list-inside text-blue-700 mb-4 space-y-2">
                <li>Telif hakkı ihlali yapmamalısınız</li>
                <li>İçeriklerimizi izinsiz kopyalamamalısınız</li>
                <li>Ticari markalarımızı izinsiz kullanmamalısınız</li>
                <li>Kaynak kodunu tersine mühendislik yapmamalısınız</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold text-blue-900 mb-4">8. Sorumluluk Sınırları</h2>
              <p className="text-blue-700 leading-relaxed mb-4">
                Astoper olarak sorumluluğumuz aşağıdaki durumlarla sınırlıdır:
              </p>
              <ul className="list-disc list-inside text-blue-700 mb-4 space-y-2">
                <li>Hizmet kesintilerinden kaynaklanan zararlar</li>
                <li>Üçüncü taraf hizmetlerinden kaynaklanan sorunlar</li>
                <li>Kullanıcı hatalarından kaynaklanan veri kayıpları</li>
                <li>İnternet bağlantı sorunları</li>
                <li>Yasal zorunluluklar nedeniyle hizmet kesintileri</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold text-blue-900 mb-4">9. Hesap Sonlandırma</h2>
              <h3 className="text-xl font-semibold text-blue-800 mb-3">9.1 Kullanıcı Tarafından Sonlandırma</h3>
              <p className="text-blue-700 leading-relaxed mb-4">
                Hesabınızı istediğiniz zaman sonlandırabilirsiniz. Hesap sonlandırma 
                işlemi geri alınamaz.
              </p>

              <h3 className="text-xl font-semibold text-blue-800 mb-3">9.2 Astoper Tarafından Sonlandırma</h3>
              <p className="text-blue-700 leading-relaxed mb-4">
                Aşağıdaki durumlarda hesabınızı sonlandırabiliriz:
              </p>
              <ul className="list-disc list-inside text-blue-700 mb-4 space-y-2">
                <li>Kullanım şartlarını ihlal etme</li>
                <li>Ödeme yapmama</li>
                <li>Yasadışı faaliyetler</li>
                <li>Diğer kullanıcıları rahatsız etme</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold text-blue-900 mb-4">10. Değişiklikler</h2>
              <p className="text-blue-700 leading-relaxed mb-4">
                Bu kullanım şartlarını zaman zaman güncelleyebiliriz. Önemli değişiklikler 
                olduğunda kullanıcılarımızı bilgilendiririz. Güncellenmiş şartları kabul 
                etmek istemiyorsanız hizmetimizi kullanmayı bırakabilirsiniz.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold text-blue-900 mb-4">11. Uygulanacak Hukuk</h2>
              <p className="text-blue-700 leading-relaxed mb-4">
                Bu kullanım şartları Türkiye Cumhuriyeti hukukuna tabidir. Herhangi bir 
                anlaşmazlık durumunda İstanbul mahkemeleri yetkilidir.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-bold text-blue-900 mb-4">12. İletişim</h2>
              <p className="text-blue-700 leading-relaxed mb-4">
                Kullanım şartları hakkında sorularınız varsa bizimle iletişime geçin:
              </p>
              <div className="bg-blue-50 p-6 rounded-lg">
                <p className="text-blue-700 mb-2"><strong>E-posta:</strong> legal@astoper.com</p>
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
