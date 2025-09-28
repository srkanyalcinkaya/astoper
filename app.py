from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import uvicorn

from database import create_default_plans, init_database
from routers import auth, automation, files, plans, users, subscriptions, webhooks, email_providers, templates, search_engine, google_auth, email_sending, subscription_management

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama başlangıç ve bitiş olayları"""
    logger.info("Astoper Platform başlatılıyor...")
    
    await init_database()
    logger.info("Veritabanı başarıyla başlatıldı")
    
    logger.info("Astoper Platform başarıyla başlatıldı!")
    
    yield
    
    logger.info("Astoper Platform kapatılıyor...")

app = FastAPI(
    title="Astoper Platform",
    description="""
    
    Bu platform, işletmelerin hedef müşterilerine otomatik email gönderimi yapmasını sağlar.
    
    - **Kullanıcı Yönetimi**: Kayıt, giriş, profil yönetimi
    - **Plan Sistemi**: Free, Basic ($20), Premium ($50) planları
    - **Email Otomasyonu**: SerpAPI ile hedef bulma ve otomatik email gönderimi
    - **Dosya Yükleme**: Excel, CSV, PDF, DOCX dosyalarından URL çıkarma
    - **Loglama**: Tüm işlemlerin detaylı loglanması
    - **Plan Limitleri**: Her plan için farklı kullanım limitleri
    
    - **Free**: 1 sorgu/ay, dosya yükleme yok
    - **Basic**: 100 sorgu/ay, 10 dosya/ay, $20
    - **Premium**: 1000 sorgu/ay, sınırsız dosya, $50
    """,
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "https://astoper.com",
        "http://astoper.com",
        "https://www.astoper.com",
        "http://www.astoper.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Sunucu hatası oluştu. Lütfen daha sonra tekrar deneyin."}
    )

app.include_router(auth.router)
app.include_router(automation.router)
app.include_router(files.router)
app.include_router(plans.router)
app.include_router(users.router)
app.include_router(subscriptions.router)
app.include_router(webhooks.router)
app.include_router(email_providers.router)
app.include_router(templates.router)
app.include_router(search_engine.router)
app.include_router(google_auth.router)
app.include_router(email_sending.router)
app.include_router(subscription_management.router)

@app.options("/{path:path}")
async def options_handler(request: Request, path: str):
    """OPTIONS isteği için CORS preflight handler"""
    origin = request.headers.get("origin")
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "https://astoper.com",
        "http://astoper.com",
        "https://www.astoper.com",
        "http://www.astoper.com"
    ]
    
    if origin in allowed_origins:
        return JSONResponse(
            status_code=200,
            content={},
            headers={
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Credentials": "true"
            }
        )
    else:
        return JSONResponse(
            status_code=403,
            content={"detail": "CORS policy violation"}
        )

@app.get("/")
async def root():
    """Ana sayfa"""
    return {
        "message": "Astoper Platform API",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs",
        "features": [
            "Kullanıcı kayıt/giriş sistemi",
            "3 farklı plan (Free, Basic, Premium)",
            "Email otomasyonu",
            "Dosya yükleme (Excel, CSV, PDF, DOCX)",
            "Detaylı loglama",
            "Plan limitleri"
        ]
    }

@app.get("/health")
async def health_check():
    """Sağlık kontrolü"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0"
    }

@app.get("/api/info")
async def api_info():
    """API bilgileri"""
    return {
        "title": "Astoper Platform API",
        "version": "1.0.0",
        "description": "İşletmeler için email otomasyon platformu",
        "endpoints": {
            "authentication": "/auth",
            "email_automation": "/automation", 
            "file_upload": "/files",
            "plans": "/plans",
            "users": "/users"
        },
        "plans": {
            "free": {
                "price": 0,
                "queries_per_month": 1,
                "file_uploads": 0
            },
            "basic": {
                "price": 20,
                "queries_per_month": 100,
                "file_uploads": 10
            },
            "premium": {
                "price": 50,
                "queries_per_month": 1000,
                "file_uploads": -1  # unlimited
            }
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

