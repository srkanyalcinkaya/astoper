from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

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

class PlanBase(BaseModel):
    name: str
    price: float
    max_queries_per_month: int
    max_file_uploads: int
    max_results_per_query: int = 10
    features: List[str] = []

class PlanCreate(PlanBase):
    pass

class PlanUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    max_queries_per_month: Optional[int] = None
    max_file_uploads: Optional[int] = None
    max_results_per_query: Optional[int] = None
    features: Optional[List[str]] = None
    is_active: Optional[bool] = None

class Plan(PlanBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    is_active: bool = True
    created_at: datetime
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserLogin(BaseModel):
    email: EmailStr  # Login with email
    password: str

class User(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    is_active: bool = True
    created_at: datetime
    plan_id: Optional[PyObjectId] = None
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserProfile(User):
    plan: Optional[Plan] = None
    queries_this_month: int = 0
    file_uploads_this_month: int = 0

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class QueryBase(BaseModel):
    query_type: str
    search_terms: Optional[str] = None
    target_urls: Optional[List[str]] = []

class QueryCreate(QueryBase):
    pass

class QueryUpdate(BaseModel):
    status: Optional[str] = None
    results_count: Optional[int] = None
    emails_found: Optional[int] = None
    emails_sent: Optional[int] = None
    results_data: Optional[Dict[str, Any]] = None
    completed_at: Optional[datetime] = None

class Query(QueryBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    file_path: Optional[str] = None
    status: str = "pending"
    results_count: int = 0
    emails_found: int = 0
    emails_sent: int = 0
    results_data: Optional[Dict[str, Any]] = {}
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class LogBase(BaseModel):
    action: str
    details: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class LogCreate(LogBase):
    user_id: PyObjectId
    query_id: Optional[PyObjectId] = None

class Log(LogBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    query_id: Optional[PyObjectId] = None
    created_at: datetime
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class FileUploadBase(BaseModel):
    filename: str
    file_type: str
    file_size: int

class FileUploadCreate(FileUploadBase):
    user_id: PyObjectId
    file_path: str

class FileUpload(FileUploadBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    file_path: str
    status: str = "uploaded"
    upload_date: datetime
    processed_data: Optional[Dict[str, Any]] = {}
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class EmailAutomationRequest(BaseModel):
    automation_type: str  # "search" or "file"
    search_queries: Optional[List[str]] = None
    target_urls: Optional[List[str]] = None
    file_id: Optional[str] = None  # File-based automation
    use_serpapi: bool = True
    selected_emails: Optional[List[str]] = None  # Kullanıcının seçtiği emailler
    template_id: Optional[str] = None  # Seçilen şablon ID'si
    ai_template_prompt: Optional[str] = None  # AI şablon için prompt
    custom_data: Optional[Dict[str, Any]] = {}  # Şablonda kullanılacak özel veriler

class EmailAutomationResponse(BaseModel):
    query_id: str  # ObjectId as string
    status: str
    message: str
    estimated_time: Optional[str] = None

class FileUploadResponse(BaseModel):
    id: str  # ObjectId as string
    filename: str
    file_path: str
    file_size: int
    file_type: str
    message: str

class SubscriptionBase(BaseModel):
    stripe_subscription_id: str
    stripe_customer_id: str
    status: str

class SubscriptionCreate(SubscriptionBase):
    user_id: PyObjectId
    plan_id: PyObjectId
    current_period_start: datetime
    current_period_end: datetime

class Subscription(SubscriptionBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    plan_id: PyObjectId
    current_period_start: datetime
    current_period_end: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class SubscriptionCancellationRequest(BaseModel):
    """Abonelik iptal talebi şeması"""
    cancellation_reason: str = Field(..., description="İptal nedeni")
    feedback: Optional[str] = Field(None, description="Ek geri bildirim")
    auto_renewal: bool = Field(default=True, description="Otomatik yenileme durumu")

class SubscriptionCancellationResponse(BaseModel):
    """Abonelik iptal yanıt şeması"""
    success: bool
    message: str
    cancellation_date: datetime
    service_end_date: datetime
    auto_renewal: bool

class SubscriptionUpdateRequest(BaseModel):
    """Abonelik güncelleme şeması"""
    auto_renewal: Optional[bool] = None
    cancellation_reason: Optional[str] = None

class EmailTemplateBase(BaseModel):
    name: str
    subject: str
    content: str  # HTML content
    category: Optional[str] = "general"
    is_ai_generated: bool = False
    ai_prompt: Optional[str] = None

class EmailTemplateCreate(EmailTemplateBase):
    user_id: PyObjectId

class EmailTemplateUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

class EmailTemplate(EmailTemplateBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class EmailCategory(BaseModel):
    email: str
    category: str
    confidence: float
    website_url: Optional[str] = None
    company_name: Optional[str] = None
    industry: Optional[str] = None

class EmailSearchResponse(BaseModel):
    emails: List[EmailCategory]
    total_found: int
    search_queries: List[str]
    categories: List[str]  # Bulunan kategoriler

class AITemplateRequest(BaseModel):
    prompt: str
    template_name: str
    category: Optional[str] = "custom"

class AITemplateResponse(BaseModel):
    template_id: str
    content: str
    subject: str

class UserStats(BaseModel):
    total_queries: int
    queries_this_month: int
    total_emails_sent: int
    emails_sent_this_month: int
    plan_usage: Dict[str, Any]
    recent_activity: List[Log]
