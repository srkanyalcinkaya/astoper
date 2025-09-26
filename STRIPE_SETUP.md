# Stripe Ödeme Sistemi Kurulum Rehberi

## 🏦 İngiltere için Stripe Kurulumu

### 1. Stripe Hesabı Oluşturma

1. **Stripe Dashboard'a Git**: https://dashboard.stripe.com/register
2. **İngiltere seçin** (United Kingdom)
3. **Business bilgilerinizi girin**:
   - Company name: The Octopus Labs
   - Business type: Technology/Software
   - Website: https://www.theoctopuslabs.com
   - Business address: İngiltere adresi

### 2. Stripe API Keys Alma

#### Test Keys (Development):
```bash
# Publishable key (Frontend'de kullanılır)
STRIPE_PUBLISHABLE_KEY=pk_test_51...

# Secret key (Backend'de kullanılır)
STRIPE_SECRET_KEY=sk_test_51...
```

#### Live Keys (Production):
```bash
# Publishable key
STRIPE_PUBLISHABLE_KEY=pk_live_51...

# Secret key  
STRIPE_SECRET_KEY=sk_live_51...
```

### 3. Webhook Endpoint Kurulumu

1. **Stripe Dashboard** → **Developers** → **Webhooks**
2. **Add endpoint** butonuna tıklayın
3. **Endpoint URL**: `https://yourdomain.com/webhooks/stripe`
4. **Events to send**:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`

5. **Webhook secret** alın: `whsec_ca25012dedac7b7e78332729120e2a9603fbe21c121a3dbe42480f322af93d3d`

### 4. Environment Variables

`.env` dosyasına ekleyin:
```env
# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

### 5. İngiltere Özel Ayarlar

#### Para Birimi:
- **GBP (British Pound)** kullanın
- Fiyatları **pence** cinsinden gönderin (1 GBP = 100 pence)

#### Vergi Ayarları:
- **VAT** (Value Added Tax) %20
- Stripe otomatik olarak VAT hesaplar
- Business VAT number gerekebilir

#### Banka Hesabı:
- İngiltere banka hesabı gerekli
- **Sort code** ve **Account number** gerekli
- **IBAN** da kullanılabilir

### 6. Test Kartları

#### Başarılı Ödemeler:
```
4242 4242 4242 4242 - Visa
4000 0566 5566 5556 - Visa (debit)
5555 5555 5555 4444 - Mastercard
```

#### Başarısız Ödemeler:
```
4000 0000 0000 0002 - Declined
4000 0000 0000 9995 - Insufficient funds
4000 0000 0000 9987 - Lost card
```

#### 3D Secure Test:
```
4000 0025 0000 3155 - 3D Secure authentication required
```

### 7. Frontend Entegrasyonu

#### React + Stripe Elements:
```bash
npm install @stripe/stripe-js @stripe/react-stripe-js
```

#### Stripe Provider:
```typescript
import { loadStripe } from '@stripe/stripe-js'
import { Elements } from '@stripe/react-stripe-js'

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY!)

function App() {
  return (
    <Elements stripe={stripePromise}>
      <YourApp />
    </Elements>
  )
}
```

#### Payment Form:
```typescript
import { CardElement, useStripe, useElements } from '@stripe/react-stripe-js'

function PaymentForm() {
  const stripe = useStripe()
  const elements = useElements()

  const handleSubmit = async (event) => {
    event.preventDefault()
    
    if (!stripe || !elements) return

    const { error, paymentMethod } = await stripe.createPaymentMethod({
      type: 'card',
      card: elements.getElement(CardElement),
    })

    if (!error) {
      // Backend'e payment method gönder
      const response = await fetch('/api/subscriptions/create-subscription', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plan_id: selectedPlanId,
          payment_method_id: paymentMethod.id
        })
      })
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <CardElement />
      <button disabled={!stripe}>Subscribe</button>
    </form>
  )
}
```

### 8. Backend API Endpoints

#### Yeni Endpoints:
- `POST /subscriptions/create-subscription` - Abonelik oluştur
- `GET /subscriptions/subscription-status` - Abonelik durumu
- `POST /subscriptions/cancel-subscription` - Abonelik iptal et
- `POST /subscriptions/update-subscription` - Plan güncelle
- `GET /subscriptions/billing-history` - Fatura geçmişi
- `POST /webhooks/stripe` - Stripe webhook

### 9. Güvenlik Önlemleri

#### Backend:
- **Webhook signature verification** zorunlu
- **HTTPS** kullanın (production'da)
- **Rate limiting** uygulayın
- **Input validation** yapın

#### Frontend:
- **Publishable key** sadece frontend'de
- **Secret key** asla frontend'e göndermeyin
- **HTTPS** kullanın
- **CSP headers** ekleyin

### 10. Test Senaryoları

#### Abonelik Testleri:
1. **Yeni abonelik oluşturma**
2. **Plan yükseltme/düşürme**
3. **Abonelik iptal etme**
4. **Ödeme başarısızlığı**
5. **Webhook işleme**

#### Test Checklist:
- [ ] Test kartları çalışıyor
- [ ] Webhook'lar doğru işleniyor
- [ ] Plan güncellemeleri çalışıyor
- [ ] Fatura geçmişi görüntüleniyor
- [ ] 3D Secure çalışıyor

### 11. Production'a Geçiş

#### Gereksinimler:
- [ ] **Business verification** tamamlandı
- [ ] **Bank account** bağlandı
- [ ] **Live API keys** alındı
- [ ] **Webhook endpoint** production'da
- [ ] **SSL certificate** aktif
- [ ] **Domain verification** yapıldı

#### Go-Live Checklist:
- [ ] Test ödemeleri başarılı
- [ ] Webhook'lar production'da çalışıyor
- [ ] Error handling test edildi
- [ ] Monitoring kuruldu
- [ ] Backup planı hazır

### 12. Maliyetler

#### Stripe Fees (İngiltere):
- **Online payments**: 1.4% + 20p per transaction
- **European cards**: 1.4% + 20p per transaction
- **Non-European cards**: 2.9% + 20p per transaction
- **Recurring payments**: 0.5% + 20p per transaction

#### Örnek Hesaplama:
- **Basic Plan**: £20
- **Stripe Fee**: £20 × 1.4% + 20p = 48p
- **Net Revenue**: £19.52

### 13. Compliance

#### GDPR (İngiltere):
- **Data processing agreement** imzalayın
- **Privacy policy** güncelleyin
- **Cookie consent** ekleyin
- **Data retention** politikası

#### PCI DSS:
- Stripe **PCI Level 1** compliant
- **Sensitive data** Stripe'da saklanır
- **Card data** asla kendi sunucunuzda saklamayın

### 14. Monitoring & Analytics

#### Stripe Dashboard:
- **Real-time payments** monitoring
- **Failed payments** tracking
- **Revenue analytics**
- **Customer insights**

#### Custom Monitoring:
- **Webhook delivery** monitoring
- **API response times**
- **Error rates** tracking
- **Business metrics**

### 15. Support

#### Stripe Support:
- **24/7 support** (paid plans)
- **Documentation**: https://stripe.com/docs
- **Community**: https://github.com/stripe
- **Status page**: https://status.stripe.com

#### Troubleshooting:
- **Webhook failures**: Log'ları kontrol edin
- **Payment failures**: Stripe Dashboard'u kontrol edin
- **API errors**: Error codes'ları kontrol edin
- **Test issues**: Test mode'da olduğunuzdan emin olun

Bu rehber ile İngiltere'de Stripe ödeme sistemini başarıyla entegre edebilirsiniz. Tüm adımları takip ederek güvenli ve yasal bir ödeme sistemi kurabilirsiniz.
