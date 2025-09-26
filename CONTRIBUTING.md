# Contributing Guide / Katkıda Bulunma Rehberi

Thank you for your interest in contributing to Astoper! / Astoper projesine katkıda bulunduğunuz için teşekkürler! 

This guide explains how you can contribute to the project. / Bu rehber, projeye nasıl katkıda bulunabileceğinizi açıklar.

---

## 🇺🇸 English

### 🚀 How to Contribute?

#### 🐛 Bug Reports
- **Found a bug?**: Create a new issue on the [Issues](https://github.com/srkanyalcinkaya/astoper/issues) page
- **Description**: Describe how the bug occurred, expected behavior, and actual behavior in detail
- **System info**: Include technical details like OS, Python version, browser info

#### ✨ Feature Requests
- **Feature suggestion**: Create a new issue on the [Issues](https://github.com/srkanyalcinkaya/astoper/issues) page with "Feature Request" label
- **Use case**: Explain why the feature is needed and how it will be used
- **Alternatives**: Mention any alternative solutions you've considered

#### 🔧 Code Contributions
- **Fork the project**: Fork the project to your own GitHub account
- **Create a branch**: `git checkout -b feature/new-feature` or `git checkout -b fix/bug-fix`
- **Make changes**: Write your code and test it
- **Commit**: Write meaningful commit messages
- **Push**: Push your changes to your fork
- **Create Pull Request**: Submit a pull request to the main project

### 📝 Development Environment Setup

#### Requirements
- Python 3.8+
- Node.js 16+
- Git

#### Setup Steps

1. **Clone the repository**:
```bash
git clone https://github.com/srkanyalcinkaya/astoper.git
cd astoper
```

2. **Create Python virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

4. **Install frontend dependencies**:
```bash
cd frontend
npm install
cd ..
```

5. **Create environment file**:
```bash
cp .env.example .env
# Edit .env file and add necessary API keys
```

6. **Initialize database**:
```bash
python database.py
```

7. **Run the application**:
```bash
# Backend
python main.py

# Frontend (new terminal)
cd frontend
npm run dev
```

### 🧪 Testing

#### Backend Tests
```bash
python -m pytest tests/
```

#### Frontend Tests
```bash
cd frontend
npm test
```

#### Linting
```bash
# Python
flake8 .
black .

# Frontend
cd frontend
npm run lint
```

### 📋 Code Standards

#### Python
- Follow **PEP 8** standards
- Use **type hints**
- Write **docstrings**
- Use **Black** formatter

#### JavaScript/TypeScript
- Follow **ESLint** rules
- Use **Prettier** formatter
- Use **TypeScript**
- Prefer **functional components**

#### Git Commit Messages
```
feat: add new feature
fix: bug fix
docs: documentation change
style: code formatting (linting)
refactor: code refactoring
test: add/fix tests
chore: build processes, helper tools
```

### 🏗️ Project Structure

```
astoper/
├── app.py                 # Main application
├── main.py               # Application starter
├── config.py             # Configuration
├── database.py           # Database operations
├── models.py             # Data models
├── schemas.py            # Pydantic schemas
├── routers/              # API routes
│   ├── auth.py
│   ├── files.py
│   ├── automation.py
│   └── ...
├── frontend/             # Next.js frontend
│   ├── app/              # Pages
│   ├── components/       # React components
│   ├── lib/              # Helper functions
│   └── ...
└── tests/                # Test files
```

### 🎯 Contribution Areas

#### 🐛 Bug Fixes
- Issues with "bug" label on [Issues](https://github.com/srkanyalcinkaya/astoper/issues) page
- Priority: High-priority labeled bugs

#### ✨ New Features
- Email template system
- Advanced analytics
- API integrations
- UI/UX improvements

#### 📚 Documentation
- README updates
- API documentation
- Code comments
- Video guides

#### 🧪 Tests
- Unit tests
- Integration tests
- E2E tests
- Performance tests

### 🔍 Code Review Process

1. **Automatic checks**: Must pass CI/CD pipeline
2. **Code review**: Must be reviewed by at least 1 person
3. **Test coverage**: New code must have 80%+ test coverage
4. **Documentation**: New features must be documented

### 📞 Communication

- **GitHub Issues**: Technical questions and bug reports
- **Discussions**: General questions and suggestions
- **Email**: [Contact information]

### 🏆 Contributors

Thank you to everyone who contributes to this project! 🎉

### 📄 License

This project is licensed under the MIT License. By contributing, you agree that your contributions will be licensed under the same license.

---

## 🇹🇷 Türkçe

### 🚀 Nasıl Katkıda Bulunabilirsiniz?

#### 🐛 Bug Bildirimi
- **Bug bulduğunuzda**: [Issues](https://github.com/srkanyalcinkaya/astoper/issues) sayfasından yeni bir issue oluşturun
- **Açıklama**: Bug'ın nasıl oluştuğunu, beklenen davranışı ve gerçek davranışı detaylı şekilde açıklayın
- **Sistem bilgisi**: İşletim sistemi, Python versiyonu, tarayıcı bilgileri gibi teknik detayları ekleyin

#### ✨ Yeni Özellik Önerisi
- **Özellik önerisi**: [Issues](https://github.com/srkanyalcinkaya/astoper/issues) sayfasından "Feature Request" etiketi ile yeni issue oluşturun
- **Kullanım senaryosu**: Özelliğin neden gerekli olduğunu ve nasıl kullanılacağını açıklayın
- **Alternatif çözümler**: Düşündüğünüz alternatif çözümleri de belirtin

#### 🔧 Kod Katkısı
- **Fork yapın**: Projeyi kendi GitHub hesabınıza fork edin
- **Branch oluşturun**: `git checkout -b feature/yeni-ozellik` veya `git checkout -b fix/bug-duzeltme`
- **Değişiklik yapın**: Kodunuzu yazın ve test edin
- **Commit yapın**: Anlamlı commit mesajları yazın
- **Push edin**: Değişikliklerinizi kendi fork'unuza push edin
- **Pull Request oluşturun**: Ana projeye pull request gönderin

### 📝 Geliştirme Ortamı Kurulumu

#### Gereksinimler
- Python 3.8+
- Node.js 16+
- Git

#### Kurulum Adımları

1. **Repository'yi klonlayın**:
```bash
git clone https://github.com/srkanyalcinkaya/astoper.git
cd astoper
```

2. **Python sanal ortamı oluşturun**:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate  # Windows
```

3. **Python bağımlılıklarını yükleyin**:
```bash
pip install -r requirements.txt
```

4. **Frontend bağımlılıklarını yükleyin**:
```bash
cd frontend
npm install
cd ..
```

5. **Environment dosyasını oluşturun**:
```bash
cp .env.example .env
# .env dosyasını düzenleyin ve gerekli API anahtarlarını ekleyin
```

6. **Veritabanını başlatın**:
```bash
python database.py
```

7. **Uygulamayı çalıştırın**:
```bash
# Backend
python main.py

# Frontend (yeni terminal)
cd frontend
npm run dev
```

### 🧪 Test Etme

#### Backend Testleri
```bash
python -m pytest tests/
```

#### Frontend Testleri
```bash
cd frontend
npm test
```

#### Linting
```bash
# Python
flake8 .
black .

# Frontend
cd frontend
npm run lint
```

### 📋 Kod Standartları

#### Python
- **PEP 8** standartlarına uyun
- **Type hints** kullanın
- **Docstring** yazın
- **Black** formatter kullanın

#### JavaScript/TypeScript
- **ESLint** kurallarına uyun
- **Prettier** formatter kullanın
- **TypeScript** kullanın
- **Functional components** tercih edin

#### Git Commit Mesajları
```
feat: yeni özellik ekleme
fix: bug düzeltme
docs: dokümantasyon değişikliği
style: kod formatı (linting)
refactor: kod yeniden düzenleme
test: test ekleme/düzeltme
chore: build süreçleri, yardımcı araçlar
```

### 🏗️ Proje Yapısı

```
astoper/
├── app.py                 # Ana uygulama
├── main.py               # Uygulama başlatıcı
├── config.py             # Konfigürasyon
├── database.py           # Veritabanı işlemleri
├── models.py             # Veri modelleri
├── schemas.py            # Pydantic şemaları
├── routers/              # API route'ları
│   ├── auth.py
│   ├── files.py
│   ├── automation.py
│   └── ...
├── frontend/             # Next.js frontend
│   ├── app/              # Sayfalar
│   ├── components/       # React bileşenleri
│   ├── lib/              # Yardımcı fonksiyonlar
│   └── ...
└── tests/                # Test dosyaları
```

### 🎯 Katkı Alanları

#### 🐛 Bug Düzeltmeleri
- [Issues](https://github.com/srkanyalcinkaya/astoper/issues) sayfasındaki "bug" etiketli konular
- Öncelik: Yüksek etiketli bug'lar

#### ✨ Yeni Özellikler
- Email template sistemi
- Gelişmiş analytics
- API entegrasyonları
- UI/UX iyileştirmeleri

#### 📚 Dokümantasyon
- README güncellemeleri
- API dokümantasyonu
- Kod yorumları
- Video rehberler

#### 🧪 Testler
- Unit testler
- Integration testler
- E2E testler
- Performance testler

### 🔍 Code Review Süreci

1. **Otomatik kontroller**: CI/CD pipeline'ı geçmeli
2. **Code review**: En az 1 kişi tarafından review edilmeli
3. **Test coverage**: Yeni kod %80+ test coverage'a sahip olmalı
4. **Dokümantasyon**: Yeni özellikler dokümante edilmeli

### 📞 İletişim

- **GitHub Issues**: Teknik sorular ve bug raporları
- **Discussions**: Genel sorular ve öneriler
- **Email**: [İletişim bilgisi]

### 🏆 Katkıda Bulunanlar

Bu projeye katkıda bulunan herkese teşekkürler! 🎉

### 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Katkıda bulunarak, katkılarınızın aynı lisans altında lisanslanacağını kabul etmiş olursunuz.

---

**Not**: Bu rehber sürekli güncellenmektedir. Önerileriniz için issue açabilirsiniz! / **Note**: This guide is constantly updated. You can open an issue for your suggestions!