# Email Automation Platform

Bu proje, işletmelerin hedef müşterilerine otomatik email gönderimi yapmasını sağlayan bir FastAPI platformudur.

## 🚀 Özellikler

### Kullanıcı Yönetimi
- Kullanıcı kayıt/giriş sistemi
- JWT token tabanlı authentication
- Profil yönetimi
- Hesap deaktivasyonu

### Plan Sistemi
- **Free Plan**: 1 sorgu/ay, dosya yükleme yok
- **Basic Plan**: 100 sorgu/ay, 10 dosya/ay, $20
- **Premium Plan**: 1000 sorgu/ay, sınırsız dosya, $50

### Email Otomasyonu
- SerpAPI ile hedef website bulma
- WordPress ve SEO analizi
- Otomatik email içeriği oluşturma (Google Gemini AI)
- Kişiselleştirilmiş email gönderimi
- Background task ile asenkron işlem

### Dosya Yükleme
- Excel (.xlsx, .xls) dosyalarından URL çıkarma
- CSV dosyalarından URL çıkarma
- PDF dosyalarından URL çıkarma
- DOCX dosyalarından URL çıkarma
- Plan bazlı dosya yükleme limitleri

### Loglama ve İzleme
- Tüm kullanıcı aktivitelerinin loglanması
- Sorgu durumu takibi
- Kullanım istatistikleri
- Dashboard ile görselleştirme

## 🛠️ Kurulum

### Gereksinimler
- Python 3.8+
- MongoDB (yerel veya MongoDB Atlas)
- Node.js 18+ (Frontend için)

### Hızlı Başlangıç

#### 1. Backend Kurulumu
```bash
# Proje dizinine gidin
cd demo-otomosyon

# Backend'i başlatın (otomatik kurulum ile)
chmod +x start.sh
./start.sh
```

#### 2. Frontend Kurulumu (Yeni Terminal)
```bash
# Frontend dizinine gidin
cd frontend

# Frontend'i başlatın (otomatik kurulum ile)
chmod +x start.sh
./start.sh
```

#### Manuel Kurulum
```bash
# Backend
pip install -r requirements.txt
python app.py

# Frontend (yeni terminal)
cd frontend
npm install
npm run dev
```

### Erişim
- **API**: http://localhost:8000
- **API Dokümantasyonu**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000

### ✅ Güncellenen Özellikler
- **Gerçek API Entegrasyonu**: Mock data yerine backend'den gerçek veriler
- **Kullanıcı Kimlik Doğrulama**: JWT token tabanlı güvenli giriş
- **Dosya Yükleme**: Excel, CSV, PDF, Word dosyaları
- **Email Otomasyonu**: SerpAPI entegrasyonu ile hedef bulma
- **Plan Yönetimi**: Ücretsiz, Başlangıç, Profesyonel, Kurumsal planlar
- **Analitik Dashboard**: Gerçek zamanlı istatistikler
- **Responsive Tasarım**: Mobil ve masaüstü uyumlu

## 📚 API Dokümantasyonu

Uygulama çalıştıktan sonra aşağıdaki adreslerden API dokümantasyonuna erişebilirsiniz:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔑 API Endpoints

### Authentication (`/auth`)
- `POST /auth/register` - Kullanıcı kaydı
- `POST /auth/login` - Kullanıcı girişi
- `GET /auth/me` - Mevcut kullanıcı bilgileri
- `POST /auth/logout` - Kullanıcı çıkışı

### Email Automation (`/automation`)
- `POST /automation/start` - Email otomasyonu başlat
- `GET /automation/status/{query_id}` - Otomasyon durumu
- `GET /automation/my-queries` - Kullanıcı sorguları
- `DELETE /automation/cancel/{query_id}` - Otomasyonu iptal et
- `GET /automation/stats` - Otomasyon istatistikleri

### File Upload (`/files`)
- `POST /files/upload` - Dosya yükle
- `GET /files/my-files` - Yüklenen dosyalar
- `DELETE /files/delete/{file_id}` - Dosya sil

### Plans (`/plans`)
- `GET /plans/` - Tüm planlar
- `GET /plans/my-plan` - Mevcut plan
- `POST /plans/upgrade/{plan_id}` - Plan yükselt
- `GET /plans/usage` - Plan kullanım bilgileri
- `GET /plans/features` - Plan özellikleri

### Users (`/users`)
- `GET /users/profile` - Kullanıcı profili
- `GET /users/stats` - Kullanıcı istatistikleri
- `GET /users/activity` - Aktivite geçmişi
- `PUT /users/profile` - Profil güncelle
- `POST /users/deactivate` - Hesabı deaktive et
- `GET /users/dashboard` - Dashboard verileri

## 🗄️ Veritabanı Yapısı

### Tablolar
- **users**: Kullanıcı bilgileri
- **plans**: Plan bilgileri
- **queries**: Sorgu kayıtları
- **logs**: Aktivite logları

### İlişkiler
- User → Plan (many-to-one)
- User → Query (one-to-many)
- User → Log (one-to-many)
- Query → Log (one-to-many)

## 🔧 Konfigürasyon

`config.py` dosyasında aşağıdaki ayarları yapabilirsiniz:

- JWT secret key
- Database URL
- Email ayarları (SMTP)
- Google Gemini API key
- SerpAPI key
- Şirket bilgileri

## 📊 Kullanım Örnekleri

### 1. Kullanıcı Kaydı
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "password123",
    "full_name": "Test User"
  }'
```

### 2. Email Otomasyonu Başlatma
```bash
curl -X POST "http://localhost:8000/automation/start" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "search_queries": ["wordpress site:uk", "outdated website site:uk"],
    "use_serpapi": true
  }'
```

### 3. Dosya Yükleme
```bash
curl -X POST "http://localhost:8000/files/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@example.xlsx"
```

## 🚨 Güvenlik Notları

- Production ortamında JWT secret key'i değiştirin
- CORS ayarlarını sadece gerekli domainler için yapın
- SMTP şifrelerini environment variable olarak saklayın
- API key'leri güvenli şekilde saklayın

## 📝 Loglama

Tüm aktiviteler `email_automation.log` dosyasına kaydedilir:
- Kullanıcı giriş/çıkış işlemleri
- Email otomasyon durumları
- Dosya yükleme işlemleri
- Plan değişiklikleri
- Hata mesajları

## 🔄 Background Tasks

Email otomasyonu background task olarak çalışır:
- Asenkron işlem
- Kullanıcı deneyimi kesintisiz
- Büyük veri setleri için uygun
- Durum takibi

## 📈 Performans

- SQLite local database
- Connection pooling
- Asenkron işlemler
- Rate limiting
- Error handling

## 🐛 Hata Ayıklama

Log dosyalarını kontrol edin:
```bash
tail -f email_automation.log
```

API endpoint'lerini test edin:
```bash
curl http://localhost:8000/health
```

## 📞 Destek

Herhangi bir sorun yaşarsanız:
1. Log dosyalarını kontrol edin
2. API dokümantasyonunu inceleyin
3. GitHub issues bölümünü kullanın

## 🔮 Gelecek Özellikler

- [ ] Gerçek ödeme entegrasyonu
- [ ] Email template sistemi
- [ ] Gelişmiş analitik
- [ ] Webhook desteği
- [ ] Multi-language desteği
- [ ] Mobile app API

