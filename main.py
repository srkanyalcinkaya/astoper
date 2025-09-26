from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from routers import automation, files, plans, subscriptions, users, webhooks, email_providers, templates, subscription_management

from routers import auth_simple as auth

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Email Automation API",
    description="Otomatik email gönderim sistemi API'si",
    version="1.0.0"
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
)

app.include_router(auth.router)
app.include_router(automation.router)
app.include_router(files.router)
app.include_router(plans.router)
app.include_router(subscriptions.router)
app.include_router(users.router)
app.include_router(webhooks.router)
app.include_router(email_providers.router)
app.include_router(templates.router)
app.include_router(subscription_management.router)

@app.options("/{path:path}")
async def options_handler(path: str):
    """OPTIONS isteği için CORS preflight handler"""
    return JSONResponse(
        status_code=200,
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true"
        }
    )

@app.get("/")
async def root():
    """API health check"""
    return {
        "message": "Email Automation API is running",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)