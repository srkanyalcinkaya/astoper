#!/bin/bash

echo "🚀 Frontend Başlatılıyor..."
echo "=============================="

# Node modules kontrolü
if [ ! -d "node_modules" ]; then
    echo "📦 Node modules yükleniyor..."
    npm install
fi

# Environment dosyası kontrolü
if [ ! -f ".env.local" ]; then
    echo "🔧 Environment dosyası oluşturuluyor..."
    echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" > .env.local
    echo "✅ Environment dosyası oluşturuldu!"
fi

# Frontend'i başlat
echo "🌟 Frontend başlatılıyor..."
echo "📍 Frontend adresi: http://localhost:3000"
echo "🔄 Backend API: http://localhost:8000"
echo ""
echo "⏹️ Durdurmak için Ctrl+C kullanın"
echo "=============================="

npm run dev
