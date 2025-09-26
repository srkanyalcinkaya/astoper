from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from bson import ObjectId
import json

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema

class MongoBaseModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Plan(MongoBaseModel):
    name: str
    price: float
    currency: str = "USD"  # Ana para birimi
    max_queries_per_month: int
    max_file_uploads: int
    max_results_per_query: int = 10
    max_emails_per_month: int = 0  # Aylık email gönderim limiti
    max_templates: int = 1  # Maksimum şablon sayısı
    max_file_size_mb: int = 10  # Maksimum dosya boyutu (MB)
    features: List[str] = []
    is_active: bool = True
    cost_breakdown: Optional[Dict[str, float]] = None  # Maliyet dağılımı
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        schema_extra = {
            "example": {
                "name": "Free",
                "price": 0.0,
                "max_queries_per_month": 10,
                "max_file_uploads": 0,
                "features": ["10 sorgu/ay", "Temel email gönderimi"],
                "is_active": True
            }
        }

class User(MongoBaseModel):
    email: EmailStr
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    plan_id: Optional[PyObjectId] = None
    
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "Test User",
                "is_active": True
            }
        }

class Query(MongoBaseModel):
    user_id: PyObjectId
    query_type: str  # serpapi, manual, file_upload
    search_terms: Optional[str] = None
    target_urls: Optional[List[str]] = []
    file_path: Optional[str] = None
    status: str = "pending"  # pending, processing, completed, failed
    results_count: int = 0
    emails_found: int = 0
    emails_sent: int = 0
    results_data: Optional[Dict[str, Any]] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        schema_extra = {
            "example": {
                "query_type": "serpapi",
                "search_terms": "web tasarım şirketleri İstanbul",
                "target_urls": ["https://example.com"],
                "status": "pending"
            }
        }

class Log(MongoBaseModel):
    user_id: PyObjectId
    query_id: Optional[PyObjectId] = None
    action: str  # login, query_start, email_sent, error, etc.
    details: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        schema_extra = {
            "example": {
                "action": "login",
                "details": "User logged in successfully",
                "ip_address": "192.168.1.1"
            }
        }

class FileUpload(MongoBaseModel):
    user_id: PyObjectId
    filename: str
    file_path: str
    file_type: str
    file_size: int
    status: str = "uploaded"  # uploaded, processing, processed, failed
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    processed_data: Optional[Dict[str, Any]] = {}

    class Config:
        schema_extra = {
            "example": {
                "filename": "emails.xlsx",
                "file_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "file_size": 1024,
                "status": "uploaded"
            }
        }

class Subscription(MongoBaseModel):
    user_id: PyObjectId
    stripe_subscription_id: str
    stripe_customer_id: str
    plan_id: PyObjectId
    status: str  # active, cancelled, past_due, incomplete
    current_period_start: datetime
    current_period_end: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    cancellation_requested: bool = Field(default=False, description="İptal talebi yapıldı mı")
    cancellation_date: Optional[datetime] = Field(None, description="İptal tarihi")
    cancellation_reason: Optional[str] = Field(None, description="İptal nedeni")
    cancellation_feedback: Optional[str] = Field(None, description="İptal geri bildirimi")
    auto_renewal: bool = Field(default=True, description="Otomatik yenileme aktif mi")
    service_end_date: Optional[datetime] = Field(None, description="Hizmet sona erme tarihi")

    class Config:
        schema_extra = {
            "example": {
                "stripe_subscription_id": "sub_1234567890",
                "stripe_customer_id": "cus_1234567890",
                "status": "active"
            }
        }

class EmailTemplate(MongoBaseModel):
    user_id: PyObjectId
    name: str
    subject: str
    content: str
    is_default: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        schema_extra = {
            "example": {
                "name": "Default Template",
                "subject": "Professional Website Redesign Proposal",
                "content": "Email content here...",
                "is_default": True
            }
        }

class Analytics(MongoBaseModel):
    user_id: PyObjectId
    date: datetime = Field(default_factory=datetime.utcnow)
    queries_count: int = 0
    emails_sent: int = 0
    emails_opened: int = 0
    emails_clicked: int = 0
    success_rate: float = 0.0

    class Config:
        schema_extra = {
            "example": {
                "queries_count": 5,
                "emails_sent": 50,
                "emails_opened": 20,
                "emails_clicked": 5,
                "success_rate": 0.4
            }
        }

COLLECTIONS = {
    "users": User,
    "plans": Plan,
    "queries": Query,
    "logs": Log,
    "file_uploads": FileUpload,
    "subscriptions": Subscription,
    "email_templates": EmailTemplate,
    "analytics": Analytics
}

DEFAULT_PLANS = [
    {
        "name": "Free",
        "price": 0.0,
        "currency": "USD",
        "max_queries_per_month": 1,
        "max_file_uploads": 1,
        "max_results_per_query": 10,
        "max_emails_per_month": 10,
        "max_templates": 1,
        "max_file_size_mb": 5,
        "features": ["1 monthly query", "10 results per query", "1 file upload", "10 emails/month", "1 template", "5MB file size"],
        "is_active": True,
        "cost_breakdown": {
            "server_cost": 0,
            "ai_cost": 0,
            "email_cost": 0,
            "domain_cost": 0,
            "total_cost": 0
        }
    },
    {
        "name": "Starter",
        "price": 29.0,
        "currency": "USD",
        "max_queries_per_month": 10,
        "max_file_uploads": 10,
        "max_results_per_query": 100,
        "max_emails_per_month": 500,
        "max_templates": 5,
        "max_file_size_mb": 10,
        "features": [
            "10 monthly queries", 
            "100 results per query",
            "10 file uploads",
            "500 emails/month",
            "5 templates",
            "10MB file size",
            "SerpAPI integration",
            "Priority support", 
            "Basic analytics", 
            "CSV export"
        ],
        "is_active": True,
        "cost_breakdown": {
            "server_cost": 5.0,
            "ai_cost": 3.0,
            "email_cost": 2.0,
            "domain_cost": 0.1,
            "total_cost": 10.1
        }
    },
    {
        "name": "Professional",
        "price": 79.0,
        "currency": "USD",
        "max_queries_per_month": 50,
        "max_file_uploads": 50,
        "max_results_per_query": 250,
        "max_emails_per_month": 2500,
        "max_templates": 20,
        "max_file_size_mb": 25,
        "features": [
            "50 monthly queries",
            "250 results per query",
            "50 file uploads",
            "2500 emails/month",
            "20 templates",
            "25MB file size",
            "API access",
            "24/7 live support",
            "Advanced analytics",
            "White-label option",
            "Custom integrations"
        ],
        "is_active": True,
        "cost_breakdown": {
            "server_cost": 15.0,
            "ai_cost": 12.0,
            "email_cost": 8.0,
            "domain_cost": 0.1,
            "total_cost": 35.1
        }
    },
    {
        "name": "Enterprise",
        "price": 199.0,
        "currency": "USD",
        "max_queries_per_month": 250,
        "max_file_uploads": 250,
        "max_results_per_query": 500,
        "max_emails_per_month": 10000,
        "max_templates": 100,
        "max_file_size_mb": 100,
        "features": [
            "250 monthly queries",
            "500 results per query",
            "250 file uploads",
            "10000 emails/month",
            "100 templates",
            "100MB file size",
            "Unlimited features",
            "Custom API limits",
            "Dedicated account manager",
            "Custom reporting",
            "SLA guarantee",
            "Custom development"
        ],
        "is_active": True,
        "cost_breakdown": {
            "server_cost": 40.0,
            "ai_cost": 30.0,
            "email_cost": 25.0,
            "domain_cost": 0.1,
            "total_cost": 95.1
        }
    }
]

class SMTPConfig(BaseModel):
    """SMTP konfigürasyon modeli"""
    host: str = Field(..., description="SMTP sunucu adresi")
    port: int = Field(..., description="SMTP port numarası")
    username: str = Field(..., description="SMTP kullanıcı adı")
    password: str = Field(..., description="SMTP şifresi")
    use_ssl: bool = Field(default=True, description="SSL kullanımı")
    use_tls: bool = Field(default=False, description="TLS kullanımı")

class OAuthConfig(BaseModel):
    """OAuth2 konfigürasyon modeli"""
    access_token: str = Field(..., description="OAuth2 access token")
    refresh_token: Optional[str] = Field(None, description="OAuth2 refresh token")
    expires_at: Optional[datetime] = Field(None, description="Token sona erme zamanı")
    scope: List[str] = Field(default_factory=list, description="OAuth2 scope'ları")

class EmailProvider(BaseModel):
    """Email provider modeli"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId = Field(..., description="Kullanıcı ID")
    provider_name: Literal["gmail", "outlook", "yahoo", "custom"] = Field(..., description="Email provider adı")
    email_address: str = Field(..., description="Email adresi")
    
    oauth_config: Optional[OAuthConfig] = Field(None, description="OAuth2 konfigürasyonu")
    smtp_config: Optional[SMTPConfig] = Field(None, description="SMTP konfigürasyonu")
    
    is_active: bool = Field(default=True, description="Aktif durumu")
    is_verified: bool = Field(default=False, description="Doğrulanmış durumu")
    last_used: Optional[datetime] = Field(None, description="Son kullanım zamanı")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class EmailTracking(MongoBaseModel):
    """Email gönderim takip modeli"""
    user_id: PyObjectId = Field(..., description="Kullanıcı ID")
    email_address: str = Field(..., description="Gönderilen email adresi")
    subject: str = Field(..., description="Email konusu")
    template_id: Optional[str] = Field(None, description="Kullanılan şablon ID")
    provider_id: str = Field(..., description="Kullanılan email provider ID")
    status: Literal["sent", "failed", "delivered", "opened", "clicked"] = Field(default="sent", description="Email durumu")
    sent_at: datetime = Field(default_factory=datetime.utcnow, description="Gönderim zamanı")
    delivered_at: Optional[datetime] = Field(None, description="Teslimat zamanı")
    opened_at: Optional[datetime] = Field(None, description="Açılma zamanı")
    clicked_at: Optional[datetime] = Field(None, description="Tıklama zamanı")
    error_message: Optional[str] = Field(None, description="Hata mesajı")
    campaign_id: Optional[str] = Field(None, description="Kampanya ID")
    
    class Config:
        schema_extra = {
            "example": {
                "email_address": "test@example.com",
                "subject": "Test Email",
                "template_id": "template123",
                "provider_id": "provider123",
                "status": "sent"
            }
        }

class EmailProviderCreate(BaseModel):
    """Email provider oluşturma şeması"""
    provider_name: Literal["gmail", "outlook", "yahoo", "custom"]
    email_address: str
    smtp_config: Optional[SMTPConfig] = None

class EmailProviderUpdate(BaseModel):
    """Email provider güncelleme şeması"""
    is_active: Optional[bool] = None
    smtp_config: Optional[SMTPConfig] = None

class EmailProviderResponse(BaseModel):
    """Email provider response şeması"""
    id: str
    provider_name: str
    email_address: str
    is_active: bool
    is_verified: bool
    last_used: Optional[datetime]
    created_at: datetime
    
    class Config:
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}
