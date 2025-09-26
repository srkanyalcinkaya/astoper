#!/bin/bash

echo "🚀 Email Automation Platform Başlatılıyor..."
echo "=============================================="

# Python virtual environment kontrolü
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment oluşturuluyor..."
    python3 -m venv venv
fi

# Virtual environment'ı aktifleştir
echo "🔧 Virtual environment aktifleştiriliyor..."
source venv/bin/activate

# Bağımlılıkları yükle
echo "📚 Bağımlılıklar yükleniyor..."
pip install -r requirements.txt

# Veritabanını başlat
echo "🗄️ Veritabanı hazırlanıyor..."
python -c "
import asyncio
from database import init_database
asyncio.run(init_database())
print('✅ Veritabanı hazır!')
"

# Uygulamayı başlat
echo "🌟 Uygulama başlatılıyor..."
echo "📍 API adresi: http://localhost:8000"
echo "📖 Dokümantasyon: http://localhost:8000/docs"
echo "🔄 ReDoc: http://localhost:8000/redoc"
echo ""
echo "⏹️ Durdurmak için Ctrl+C kullanın"
echo "=============================================="

python app.py

