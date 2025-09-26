# Email Automation Platform - Frontend Geliştirme Prompt

## 🎯 Proje Özeti
Email Automation Platform için modern, responsive ve kullanıcı dostu bir frontend uygulaması geliştir. Bu platform, işletmelerin hedef müşterilerine otomatik email gönderimi yapmasını sağlar.

## 🛠️ Teknoloji Stack Önerileri

### Ana Framework Seçenekleri:
2. **Next.js + TypeScript** (SSR için)

### UI Kütüphaneleri:
- **Tailwind CSS** + **Headless UI** + **Shadcn UI** (Önerilen)

### State Management:
- **Zustand** (basit ve etkili)
- **Redux Toolkit**
- **Context API**

### HTTP Client:
- **Axios** (interceptor'lar ile)
- **TanStack Query** (React Query) - cache ve state management için

## 🎨 Tasarım Gereksinimleri

### Renk Paleti:
```css
Primary: #3B82F6 (Blue)
Secondary: #10B981 (Green)
Accent: #F59E0B (Amber)
Danger: #EF4444 (Red)
Success: #10B981 (Green)
Warning: #F59E0B (Amber)
Gray: #6B7280
Dark: #1F2937
```

### Typography:
- **Font**: Inter, system-ui, sans-serif
- **Headings**: 600-700 weight
- **Body**: 400-500 weight

### Layout:
- **Sidebar Navigation** (desktop)
- **Bottom Navigation** (mobile)
- **Responsive Grid System**
- **Card-based Design**

## 📱 Sayfa Yapısı

### 1. Landing Page (`/`)
- Hero section with value proposition
- Features showcase
- Pricing plans comparison
- Testimonials
- CTA buttons

### 2. Authentication Pages
- **Login** (`/login`)
- **Register** (`/register`)
- **Forgot Password** (`/forgot-password`)
- **Reset Password** (`/reset-password`)

### 3. Dashboard (`/dashboard`)
- **Overview Cards**: Total queries, emails sent, plan usage
- **Recent Activity**: Last queries and results
- **Quick Actions**: Start automation, upload file
- **Usage Statistics**: Charts and graphs
- **Plan Status**: Current plan and upgrade options

### 4. Email Automation (`/automation`)
- **New Automation Form**:
  - Search queries input
  - Target URLs input
  - File upload option
  - SerpAPI toggle
- **Automation History**: List of past automations
- **Automation Details**: Status, results, logs

### 5. File Management (`/files`)
- **Upload Area**: Drag & drop interface
- **File List**: Uploaded files with metadata
- **File Actions**: View, download, delete
- **Supported Formats**: Excel, CSV, PDF, DOCX

### 6. Plans & Billing (`/plans`)
- **Plan Comparison**: Feature comparison table
- **Current Plan**: Usage statistics
- **Upgrade/Downgrade**: Plan change options
- **Billing History**: Past payments
- **Payment Methods**: Card management

### 7. Profile & Settings (`/profile`)
- **Personal Information**: Name, email, username
- **Account Settings**: Password change, notifications
- **API Keys**: Integration settings
- **Account Actions**: Deactivate account

### 8. Analytics (`/analytics`)
- **Query Statistics**: Success rates, response times
- **Email Performance**: Open rates, click rates
- **Usage Trends**: Monthly/weekly charts
- **Export Options**: CSV, PDF reports

## 🔐 Authentication Flow

### JWT Token Management:
```typescript
// Token storage
localStorage.setItem('access_token', token)

// Axios interceptor
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Token refresh logic
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

## 💳 Ödeme Sistemi Entegrasyonu

### İngiltere için Önerilen Ödeme Sağlayıcıları:

#### 1. **Stripe** (En Önerilen)
- **Avantajlar**: 
  - İngiltere'de yaygın kullanım
  - GBP desteği
  - Recurring payments (abonelik)
  - Webhook'lar
  - PCI compliance
- **Entegrasyon**: Stripe Elements, Stripe Checkout
- **Maliyet**: 1.4% + 20p per transaction

#### 2. **PayPal**
- **Avantajlar**: 
  - Yaygın kullanım
  - Express checkout
  - Recurring payments
- **Entegrasyon**: PayPal SDK
- **Maliyet**: 2.9% + 30p per transaction

#### 3. **Square**
- **Avantajlar**: 
  - İngiltere'de büyüyen
  - Modern API
  - Subscription management
- **Maliyet**: 1.4% + 20p per transaction

### Ödeme Akışı:
1. **Plan Seçimi**: Kullanıcı plan seçer
2. **Checkout**: Stripe Checkout sayfası
3. **Payment**: Kredi kartı/banka kartı
4. **Webhook**: Backend'e ödeme onayı
5. **Plan Update**: Kullanıcı planı güncellenir
6. **Confirmation**: Başarı mesajı

## 🔄 Abonelik Sistemi

### Backend API Endpoints (Eklenmesi Gereken):
```python
# routers/subscriptions.py
@router.post("/create-subscription")
async def create_subscription(
    plan_id: int,
    payment_method_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Stripe subscription oluştur"""

@router.get("/subscription-status")
async def get_subscription_status(
    current_user: User = Depends(get_current_active_user)
):
    """Abonelik durumunu getir"""

@router.post("/cancel-subscription")
async def cancel_subscription(
    current_user: User = Depends(get_current_active_user)
):
    """Abonelik iptal et"""

@router.post("/update-subscription")
async def update_subscription(
    new_plan_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Abonelik planını güncelle"""
```

### Frontend Abonelik Yönetimi:
```typescript
// Subscription management
interface Subscription {
  id: string
  status: 'active' | 'cancelled' | 'past_due'
  current_period_end: string
  plan: Plan
  payment_method: PaymentMethod
}

// Subscription actions
const createSubscription = async (planId: number) => {
  const response = await api.post('/subscriptions/create', {
    plan_id: planId,
    payment_method_id: paymentMethodId
  })
  return response.data
}
```

## 📊 State Management Yapısı

### Zustand Store Örneği:
```typescript
interface AppState {
  user: User | null
  subscription: Subscription | null
  automations: Automation[]
  files: File[]
  isLoading: boolean
  error: string | null
  
  // Actions
  setUser: (user: User) => void
  setSubscription: (subscription: Subscription) => void
  addAutomation: (automation: Automation) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}
```

## 🎯 Özellik Detayları

### 1. Real-time Updates
- **WebSocket** veya **Server-Sent Events** ile automation durumu
- **Toast notifications** için başarı/hata mesajları
- **Progress bars** için uzun süren işlemler

### 2. File Upload
- **Drag & drop** interface
- **Progress indicators**
- **File validation** (size, type)
- **Preview** functionality

### 3. Data Visualization
- **Chart.js** veya **Recharts** ile grafikler
- **Usage statistics** charts
- **Performance metrics** dashboards

### 4. Responsive Design
- **Mobile-first** approach
- **Breakpoints**: 320px, 768px, 1024px, 1280px
- **Touch-friendly** interactions

## 🚀 Geliştirme Adımları

### 1. Proje Kurulumu
```bash
# React + TypeScript + Vite
npm create vite@latest email-automation-frontend -- --template react-ts
cd email-automation-frontend
npm install

# Dependencies
npm install axios zustand react-router-dom
npm install @headlessui/react @heroicons/react
npm install tailwindcss @tailwindcss/forms
npm install @stripe/stripe-js @stripe/react-stripe-js
```

### 2. Environment Variables
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
VITE_APP_NAME=Email Automation Platform
```

### 3. API Integration
```typescript
// api/client.ts
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})
```

### 4. Routing Setup
```typescript
// App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/automation" element={<AutomationPage />} />
        <Route path="/files" element={<FilesPage />} />
        <Route path="/plans" element={<PlansPage />} />
        <Route path="/profile" element={<ProfilePage />} />
      </Routes>
    </BrowserRouter>
  )
}
```

## 📋 Checklist

### Phase 1: Core Features
- [ ] Authentication (login/register)
- [ ] Dashboard layout
- [ ] API integration
- [ ] Basic routing

### Phase 2: Main Features
- [ ] Email automation form
- [ ] File upload functionality
- [ ] Plan management
- [ ] User profile

### Phase 3: Advanced Features
- [ ] Payment integration
- [ ] Subscription management
- [ ] Real-time updates
- [ ] Analytics dashboard

### Phase 4: Polish
- [ ] Responsive design
- [ ] Error handling
- [ ] Loading states
- [ ] Performance optimization

## 🎨 UI/UX Best Practices

### 1. User Experience
- **Clear navigation** with breadcrumbs
- **Loading states** for all async operations
- **Error boundaries** for graceful error handling
- **Confirmation dialogs** for destructive actions
- **Success feedback** for completed actions

### 2. Accessibility
- **ARIA labels** for screen readers
- **Keyboard navigation** support
- **Color contrast** compliance
- **Focus management**

### 3. Performance
- **Code splitting** with React.lazy
- **Image optimization**
- **Bundle size** monitoring
- **Caching strategies**

## 🔧 Development Tools

### Recommended Tools:
- **ESLint** + **Prettier** for code quality
- **Husky** for git hooks
- **Storybook** for component development
- **Jest** + **React Testing Library** for testing
- **Cypress** for E2E testing

### Deployment:
- **Vercel** (React apps için ideal)
- **Netlify**
- **AWS S3** + **CloudFront**

## 📞 Support & Documentation

### API Documentation:
- Swagger UI: `http://localhost:8000/docs`
- Postman collection oluştur
- API response examples

### User Documentation:
- Onboarding tour
- Help tooltips
- FAQ section
- Video tutorials

Bu prompt ile modern, kullanıcı dostu ve ödeme sistemi entegreli bir frontend uygulaması geliştirebilirsiniz. Stripe önerilen ödeme sağlayıcısıdır çünkü İngiltere'de yaygın kullanılır ve abonelik sistemi için mükemmel desteği vardır.
