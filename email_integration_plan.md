# Email Entegrasyon Planı

## 1. OAuth2 Entegrasyonu (Önerilen)

### Desteklenen Provider'lar:
- **Gmail**: Google OAuth2
- **Outlook/Hotmail**: Microsoft OAuth2  
- **Yahoo Mail**: Yahoo OAuth2

### Avantajlar:
- ✅ Kullanıcı şifresi güvenli
- ✅ Token tabanlı erişim
- ✅ Kullanıcı istediği zaman erişimi iptal edebilir
- ✅ Modern standart

### Gereksinimler:
- OAuth2 client credentials
- Refresh token yönetimi
- Token yenileme mekanizması

## 2. SMTP Konfigürasyonu (Gelişmiş Kullanıcılar)

### Desteklenen Servisler:
- **Gmail SMTP**: smtp.gmail.com:587
- **Outlook SMTP**: smtp-mail.outlook.com:587
- **Yahoo SMTP**: smtp.mail.yahoo.com:587
- **Custom SMTP**: Kullanıcı kendi sunucusunu girebilir

### Güvenlik Önlemleri:
- App-specific passwords
- 2FA gereksinimi
- Şifre şifreleme (AES-256)

## 3. Hibrit Yaklaşım

### Önerilen Sistem:
1. **İlk Tercih**: OAuth2 (Gmail, Outlook, Yahoo)
2. **İkinci Seçenek**: App Password (Gmail için)
3. **Gelişmiş**: Custom SMTP

### Kullanıcı Deneyimi:
1. Kullanıcı email provider'ını seçer
2. OAuth2 varsa direkt bağlanır
3. Yoksa SMTP bilgilerini girer
4. Test email gönderilir

## 4. Güvenlik Önlemleri

### Veri Koruma:
- Email şifreleri AES-256 ile şifrelenir
- Database'de plain text şifre saklanmaz
- Token'lar encrypt edilir

### Erişim Kontrolü:
- Kullanıcı kendi email'lerini yönetir
- Admin erişimi yok
- Log kayıtları tutulur

## 5. Teknik Implementasyon

### Database Schema:
```javascript
{
  user_id: ObjectId,
  email_provider: "gmail" | "outlook" | "yahoo" | "custom",
  oauth_token: String (encrypted),
  oauth_refresh_token: String (encrypted),
  smtp_config: {
    host: String,
    port: Number,
    username: String,
    password: String (encrypted),
    ssl: Boolean
  },
  is_active: Boolean,
  created_at: Date
}
```

### API Endpoints:
- POST /email-providers/connect (OAuth2)
- POST /email-providers/smtp (SMTP config)
- GET /email-providers/
- DELETE /email-providers/:id
- POST /email-providers/:id/test
