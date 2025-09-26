# Email Automation Platform - Proje Yapısı

```
demo-otomosyon/
├── app.py                          # Ana FastAPI uygulaması
├── config.py                       # Konfigürasyon ayarları
├── database.py                     # Veritabanı modelleri ve bağlantı
├── auth.py                         # JWT authentication sistemi
├── middleware.py                   # Plan limitleri ve loglama middleware
├── email_automation_service.py     # Email otomasyon servisi
├── file_processor.py               # Dosya işleme servisi
├── schemas.py                      # Pydantic şemaları
├── requirements.txt                # Python bağımlılıkları
├── README.md                       # Proje dokümantasyonu
├── PROJECT_STRUCTURE.md            # Bu dosya
├── start.sh                        # Başlatma scripti
├── test_api.py                     # API test scripti
├── main.py                         # Eski email otomasyon scripti
├── email_automation.log            # Log dosyası
├── email_automation.db             # SQLite veritabanı (otomatik oluşur)
├── uploads/                        # Yüklenen dosyalar klasörü (otomatik oluşur)
└── routers/                        # API router'ları
    ├── __init__.py
    ├── auth.py                     # Authentication endpoint'leri
    ├── automation.py               # Email otomasyon endpoint'leri
    ├── files.py                    # Dosya yükleme endpoint'leri
    ├── plans.py                    # Plan yönetimi endpoint'leri
    └── users.py                    # Kullanıcı yönetimi endpoint'leri
```

## 📁 Dosya Açıklamaları

### Ana Dosyalar
- **`app.py`**: FastAPI uygulamasının ana dosyası, tüm router'ları birleştirir
- **`config.py`**: Uygulama konfigürasyonu (API key'ler, veritabanı URL'i, vb.)
- **`database.py`**: SQLAlchemy modelleri ve veritabanı bağlantısı
- **`auth.py`**: JWT token tabanlı authentication sistemi
- **`middleware.py`**: Plan limitleri kontrolü ve kullanıcı aktivite loglama
- **`email_automation_service.py`**: Email otomasyon işlemlerini yöneten servis
- **`file_processor.py`**: Excel, CSV, PDF, DOCX dosyalarını işleyen servis
- **`schemas.py`**: Pydantic şemaları (API request/response modelleri)

### Router Dosyaları
- **`routers/auth.py`**: Kullanıcı kayıt, giriş, çıkış endpoint'leri
- **`routers/automation.py`**: Email otomasyon başlatma, durum takibi endpoint'leri
- **`routers/files.py`**: Dosya yükleme, listeleme, silme endpoint'leri
- **`routers/plans.py`**: Plan listeleme, yükseltme, kullanım bilgileri endpoint'leri
- **`routers/users.py`**: Kullanıcı profili, istatistikler, dashboard endpoint'leri

### Yardımcı Dosyalar
- **`requirements.txt`**: Python paket bağımlılıkları
- **`start.sh`**: Uygulamayı başlatmak için bash scripti
- **`test_api.py`**: API endpoint'lerini test etmek için Python scripti
- **`README.md`**: Detaylı proje dokümantasyonu

## 🗄️ Veritabanı Yapısı

### Tablolar
1. **`users`**: Kullanıcı bilgileri
   - id, email, username, hashed_password, full_name, is_active, created_at, plan_id

2. **`plans`**: Plan bilgileri
   - id, name, price, max_queries_per_month, max_file_uploads, features, is_active, created_at

3. **`queries`**: Sorgu kayıtları
   - id, user_id, query_type, search_terms, target_urls, file_path, status, results_count, emails_found, emails_sent, created_at, completed_at

4. **`logs`**: Aktivite logları
   - id, user_id, query_id, action, details, ip_address, user_agent, created_at

### İlişkiler
- User → Plan (many-to-one)
- User → Query (one-to-many)
- User → Log (one-to-many)
- Query → Log (one-to-many)

## 🔧 Konfigürasyon

### Environment Variables (config.py)
- `SECRET_KEY`: JWT token şifreleme anahtarı
- `DATABASE_URL`: SQLite veritabanı yolu
- `GEMINI_API_KEY`: Google Gemini AI API anahtarı
- `SERPAPI_KEY`: SerpAPI arama servisi anahtarı
- `SMTP_*`: Email gönderimi için SMTP ayarları

## 🚀 Başlatma

### Manuel Başlatma
```bash
python app.py
```

### Script ile Başlatma
```bash
./start.sh
```

### Test
```bash
python test_api.py
```

## 📊 API Endpoints Özeti

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

## 🔒 Güvenlik

- JWT token tabanlı authentication
- Şifre hashleme (bcrypt)
- Plan bazlı erişim kontrolü
- IP adresi ve user agent loglama
- Rate limiting (SerpAPI için)
- Input validation (Pydantic)

## 📈 Performans

- SQLite local database
- Asenkron background tasks
- Connection pooling
- Error handling ve logging
- File upload size limits
- Memory efficient file processing

