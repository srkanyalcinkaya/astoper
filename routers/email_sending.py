from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
from datetime import datetime
import jwt
from bson import ObjectId
from pydantic import BaseModel

from database import get_async_db
from email_sending_service import EmailSendingService
from config import settings

router = APIRouter(prefix="/email-sending", tags=["email-sending"])
security = HTTPBearer()

class EmailSendRequest(BaseModel):
    """Tek email gönderme isteği"""
    provider_id: str
    template_id: str
    recipient_email: str
    custom_data: Optional[Dict[str, Any]] = {}

class BulkEmailSendRequest(BaseModel):
    """Toplu email gönderme isteği"""
    provider_id: str
    template_id: str
    recipient_emails: List[str]
    custom_data: Optional[Dict[str, Any]] = {}
    delay_between_emails: Optional[float] = 1.0

class EmailSendResponse(BaseModel):
    """Email gönderme yanıtı"""
    success: bool
    message: str
    recipient: Optional[str] = None
    subject: Optional[str] = None

class BulkEmailSendResponse(BaseModel):
    """Toplu email gönderme yanıtı"""
    total_emails: int
    successful: int
    failed: int
    results: List[Dict[str, Any]]

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Mevcut kullanıcıyı JWT token'dan al"""
    try:
        print(f"Received token: {credentials.credentials[:20]}...")
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            print("No user_id in token payload")
            raise HTTPException(status_code=401, detail="Invalid token")
        
        db = await get_async_db()
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            print(f"User not found: {user_id}")
            raise HTTPException(status_code=401, detail="User not found")
        
        print(f"User authenticated: {user_id}")
        return user_id
    except jwt.ExpiredSignatureError:
        print("Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError as e:
        print(f"JWT error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

@router.post("/send-single", response_model=EmailSendResponse)
async def send_single_email(
    request: EmailSendRequest,
    current_user: str = Depends(get_current_user)
):
    """Tek email gönder - seçilen şablon ile"""
    try:
        db = await get_async_db()
        user_id = ObjectId(current_user)
        
        provider = await db.email_providers.find_one({
            "_id": ObjectId(request.provider_id),
            "user_id": user_id,
            "is_active": True,
            "is_verified": True
        })
        
        if not provider:
            raise HTTPException(
                status_code=404, 
                detail="Email provider bulunamadı veya doğrulanmamış"
            )
        
        template = None
        if request.template_id.startswith("default_"):
            default_templates = {
                "default_1": {
                    "name": "Web Tasarım Teklifi",
                    "subject": "Profesyonel Web Tasarım Hizmetlerimiz",
                    "content": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0; font-size: 24px;">{{company_name}}</h1>
        <p style="color: #f0f0f0; margin: 10px 0 0 0;">{{company_tagline}}</p>
    </div>
    
    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
        <h2 style="color: #333; margin-top: 0;">Merhaba!</h2>
        <p>{{greeting_message}}</p>
    </div>
    
    <div style="margin-bottom: 20px;">
        <h3 style="color: #667eea;">Hizmetlerimiz:</h3>
        <ul style="list-style: none; padding: 0;">
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">✓ {{service_1}}</li>
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">✓ {{service_2}}</li>
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">✓ {{service_3}}</li>
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">✓ {{service_4}}</li>
        </ul>
    </div>
    
    <div style="background: #e8f4f8; padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0;">
        <p style="margin: 0; font-weight: bold; color: #2c5aa0;">{{offer_title}}</p>
        <p style="margin: 5px 0 0 0; font-size: 14px;">{{offer_description}}</p>
    </div>
    
    <div style="text-align: center; margin: 30px 0;">
        <a href="{{website_url}}" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Web Sitemizi İnceleyin</a>
    </div>
    
    <div style="border-top: 1px solid #eee; padding-top: 20px; text-align: center; color: #666; font-size: 12px;">
        <p><strong>{{company_name}}</strong><br>
        📧 {{email}} | 📞 {{phone}}<br>
        🌐 {{website_url}}</p>
    </div>
</body>
</html>
                    """
                }
            }
            template = default_templates.get(request.template_id)
        else:
            template = await db.email_templates.find_one({
                "_id": ObjectId(request.template_id),
                "user_id": user_id,
                "is_active": True
            })
        
        if not template:
            raise HTTPException(
                status_code=404,
                detail="Email şablonu bulunamadı"
            )
        
        email_service = EmailSendingService()
        if not email_service.validate_email_address(request.recipient_email):
            raise HTTPException(
                status_code=400,
                detail="Geçersiz email adresi"
            )
        
        user = await db.users.find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
        
        user_plan = None
        if user.get("plan_id"):
            user_plan = await db.plans.find_one({"_id": user["plan_id"]})
        
        from plan_limit_service import PlanLimitService
        limit_service = PlanLimitService()
        email_limit = await limit_service.check_email_limit(current_user, user_plan)
        
        if not email_limit["can_send"]:
            raise HTTPException(
                status_code=403,
                detail=f"Email gönderim limitiniz dolmuş. Plan: {user_plan['name']}, Kullanılan: {email_limit['used']}/{email_limit['limit']}"
            )
        
        result = await email_service.send_email_with_template(
            provider_data=provider,
            template_data=template,
            recipient_email=request.recipient_email,
            custom_data=request.custom_data,
            user_id=current_user,
            campaign_id=f"single_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        )
        
        await db.logs.insert_one({
            "user_id": user_id,
            "action": "email_sent",
            "details": f"Email gönderildi: {request.recipient_email} - Template: {template.get('name', 'Unknown')}",
            "created_at": datetime.utcnow()
        })
        
        await db.email_providers.update_one(
            {"_id": ObjectId(request.provider_id)},
            {"$set": {"last_used": datetime.utcnow()}}
        )
        
        return EmailSendResponse(
            success=result["success"],
            message=result["message"],
            recipient=result.get("recipient"),
            subject=result.get("subject")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Email gönderme hatası: {str(e)}"
        )

@router.post("/send-bulk", response_model=BulkEmailSendResponse)
async def send_bulk_emails(
    request: BulkEmailSendRequest,
    current_user: str = Depends(get_current_user)
):
    """Toplu email gönder - seçilen şablon ile"""
    try:
        db = await get_async_db()
        user_id = ObjectId(current_user)
        
        user = await db.users.find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
        
        user_plan = None
        if user.get("plan_id"):
            user_plan = await db.plans.find_one({"_id": user["plan_id"]})
        
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)
        
        monthly_emails_cursor = db.queries.aggregate([
            {"$match": {"user_id": user_id, "created_at": {"$gte": month_start}}},
            {"$group": {"_id": None, "total": {"$sum": "$emails_sent"}}}
        ])
        monthly_emails_list = await monthly_emails_cursor.to_list(length=None)
        monthly_emails_count = monthly_emails_list[0]["total"] if monthly_emails_list else 0
        
        email_limit = user_plan.get("max_emails_per_month", 10) if user_plan else 10
        if monthly_emails_count + len(request.recipient_emails) > email_limit:
            raise HTTPException(
                status_code=400,
                detail=f"Aylık email limitinizi aşacaksınız. Limit: {email_limit}, Mevcut: {monthly_emails_count}, Gönderilecek: {len(request.recipient_emails)}"
            )
        
        provider = await db.email_providers.find_one({
            "_id": ObjectId(request.provider_id),
            "user_id": user_id,
            "is_active": True,
            "is_verified": True
        })
        
        if not provider:
            raise HTTPException(
                status_code=404, 
                detail="Email provider bulunamadı veya doğrulanmamış"
            )
        
        template = None
        if request.template_id.startswith("default_"):
            default_templates = {
                "default_1": {
                    "name": "Web Tasarım Teklifi",
                    "subject": "Profesyonel Web Tasarım Hizmetlerimiz",
                    "content": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0; font-size: 24px;">{{company_name}}</h1>
        <p style="color: #f0f0f0; margin: 10px 0 0 0;">{{company_tagline}}</p>
    </div>
    
    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
        <h2 style="color: #333; margin-top: 0;">Merhaba!</h2>
        <p>{{greeting_message}}</p>
    </div>
    
    <div style="margin-bottom: 20px;">
        <h3 style="color: #667eea;">Hizmetlerimiz:</h3>
        <ul style="list-style: none; padding: 0;">
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">✓ {{service_1}}</li>
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">✓ {{service_2}}</li>
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">✓ {{service_3}}</li>
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">✓ {{service_4}}</li>
        </ul>
    </div>
    
    <div style="background: #e8f4f8; padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0;">
        <p style="margin: 0; font-weight: bold; color: #2c5aa0;">{{offer_title}}</p>
        <p style="margin: 5px 0 0 0; font-size: 14px;">{{offer_description}}</p>
    </div>
    
    <div style="text-align: center; margin: 30px 0;">
        <a href="{{website_url}}" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Web Sitemizi İnceleyin</a>
    </div>
    
    <div style="border-top: 1px solid #eee; padding-top: 20px; text-align: center; color: #666; font-size: 12px;">
        <p><strong>{{company_name}}</strong><br>
        📧 {{email}} | 📞 {{phone}}<br>
        🌐 {{website_url}}</p>
    </div>
</body>
</html>
                    """
                }
            }
            template = default_templates.get(request.template_id)
        else:
            template = await db.email_templates.find_one({
                "_id": ObjectId(request.template_id),
                "user_id": user_id,
                "is_active": True
            })
        
        if not template:
            raise HTTPException(
                status_code=404,
                detail="Email şablonu bulunamadı"
            )
        
        email_service = EmailSendingService()
        valid_emails = []
        for email in request.recipient_emails:
            if email_service.validate_email_address(email):
                valid_emails.append(email)
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Geçersiz email adresi: {email}"
                )
        
        from plan_limit_service import PlanLimitService
        limit_service = PlanLimitService()
        email_limit = await limit_service.check_email_limit(current_user, user_plan)
        
        emails_to_send = len(valid_emails)
        if email_limit["limit"] != -1 and email_limit["remaining"] < emails_to_send:
            raise HTTPException(
                status_code=403,
                detail=f"Email gönderim limitiniz yetersiz. Plan: {user_plan['name']}, Kalan: {email_limit['remaining']}, Gönderilecek: {emails_to_send}"
            )
        
        campaign_id = f"bulk_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        result = await email_service.send_bulk_emails_with_template(
            provider_data=provider,
            template_data=template,
            recipient_emails=valid_emails,
            custom_data=request.custom_data,
            delay_between_emails=request.delay_between_emails,
            user_id=current_user,
            campaign_id=campaign_id
        )
        
        await db.logs.insert_one({
            "user_id": user_id,
            "action": "bulk_email_sent",
            "details": f"Toplu email gönderildi: {result['successful']}/{result['total_emails']} başarılı - Template: {template.get('name', 'Unknown')}",
            "created_at": datetime.utcnow()
        })
        
        await db.email_providers.update_one(
            {"_id": ObjectId(request.provider_id)},
            {"$set": {"last_used": datetime.utcnow()}}
        )
        
        return BulkEmailSendResponse(
            total_emails=result["total_emails"],
            successful=result["successful"],
            failed=result["failed"],
            results=result.get("results", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Toplu email gönderme hatası: {str(e)}"
        )

@router.post("/test-provider")
async def test_email_provider_connection(
    provider_id: str,
    current_user: str = Depends(get_current_user)
):
    """Email provider bağlantısını test et"""
    try:
        db = await get_async_db()
        user_id = ObjectId(current_user)
        
        provider = await db.email_providers.find_one({
            "_id": ObjectId(provider_id),
            "user_id": user_id
        })
        
        if not provider:
            raise HTTPException(
                status_code=404,
                detail="Email provider bulunamadı"
            )
        
        email_service = EmailSendingService()
        result = await email_service.test_email_provider_connection(provider)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Provider test hatası: {str(e)}"
        )

@router.get("/available-providers")
async def get_available_providers(current_user: str = Depends(get_current_user)):
    """Kullanıcının kullanılabilir email provider'larını listele"""
    try:
        db = await get_async_db()
        user_id = ObjectId(current_user)
        
        providers_cursor = db.email_providers.find({
            "user_id": user_id,
            "is_active": True,
            "is_verified": True
        })
        providers = await providers_cursor.to_list(length=None)
        
        result = []
        for provider in providers:
            result.append({
                "id": str(provider["_id"]),
                "provider_name": provider["provider_name"],
                "email_address": provider["email_address"],
                "last_used": provider.get("last_used")
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Provider listesi alınamadı: {str(e)}"
        )

@router.get("/available-templates")
async def get_available_templates(current_user: str = Depends(get_current_user)):
    """Kullanıcının kullanılabilir email şablonlarını listele"""
    try:
        db = await get_async_db()
        user_id = ObjectId(current_user)
        
        templates_cursor = db.email_templates.find({
            "user_id": user_id,
            "is_active": True
        })
        user_templates = await templates_cursor.to_list(length=None)
        
        default_templates = [
            {
                "_id": "default_1",
                "name": "Web Tasarım Teklifi",
                "subject": "Profesyonel Web Tasarım Hizmetlerimiz",
                "category": "web_design",
                "is_default": True
            },
            {
                "_id": "default_2",
                "name": "SEO Optimizasyon Teklifi", 
                "subject": "Web Sitenizin Arama Motorlarında Görünürlüğünü Artıralım",
                "category": "seo",
                "is_default": True
            },
            {
                "_id": "default_3",
                "name": "E-ticaret Çözümleri",
                "subject": "Online Satışlarınızı Artırmak İçin E-ticaret Çözümlerimiz",
                "category": "ecommerce",
                "is_default": True
            }
        ]
        
        result = []
        
        for template in default_templates:
            result.append({
                "id": template["_id"],
                "name": template["name"],
                "subject": template["subject"],
                "category": template["category"],
                "is_default": True
            })
        
        for template in user_templates:
            result.append({
                "id": str(template["_id"]),
                "name": template["name"],
                "subject": template["subject"],
                "category": template.get("category", "custom"),
                "is_default": False
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Şablon listesi alınamadı: {str(e)}"
        )

@router.get("/tracking/stats")
async def get_email_tracking_stats(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """Email gönderim istatistiklerini getir"""
    try:
        from datetime import datetime
        
        start_datetime = None
        end_datetime = None
        
        if start_date:
            start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        email_service = EmailSendingService()
        stats = await email_service.get_email_tracking_stats(
            user_id=current_user,
            start_date=start_datetime,
            end_date=end_datetime
        )
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Email istatistikleri alınamadı: {str(e)}"
        )

@router.get("/tracking/history")
async def get_email_tracking_history(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """Email gönderim geçmişini getir"""
    try:
        db = await get_async_db()
        user_id = ObjectId(current_user)
        
        filter_query = {"user_id": user_id}
        if status:
            filter_query["status"] = status
        
        cursor = db.email_tracking.find(filter_query).sort("sent_at", -1).skip(offset).limit(limit)
        emails = await cursor.to_list(length=None)
        
        processed_emails = []
        for email in emails:
            processed_email = {
                "_id": str(email["_id"]),
                "user_id": str(email["user_id"]),
                "email_address": email["email_address"],
                "subject": email["subject"],
                "template_id": str(email.get("template_id")) if email.get("template_id") else None,
                "provider_id": str(email.get("provider_id")) if email.get("provider_id") else None,
                "status": email["status"],
                "sent_at": email["sent_at"].isoformat() if email.get("sent_at") else None,
                "delivered_at": email.get("delivered_at").isoformat() if email.get("delivered_at") else None,
                "opened_at": email.get("opened_at").isoformat() if email.get("opened_at") else None,
                "clicked_at": email.get("clicked_at").isoformat() if email.get("clicked_at") else None,
                "error_message": email.get("error_message"),
                "campaign_id": email.get("campaign_id")
            }
            processed_emails.append(processed_email)
        
        total_count = await db.email_tracking.count_documents(filter_query)
        
        return {
            "emails": processed_emails,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Email geçmişi alınamadı: {str(e)}"
        )

@router.get("/limits")
async def get_user_limits(current_user: str = Depends(get_current_user)):
    """Kullanıcının plan limitlerini getir"""
    try:
        db = await get_async_db()
        user_id = ObjectId(current_user)
        
        user = await db.users.find_one({"_id": user_id})
        if not user:
            raise HTTPException(
                status_code=404,
                detail="Kullanıcı bulunamadı"
            )
        
        plan = None
        if user.get("plan_id"):
            plan = await db.plans.find_one({"_id": user["plan_id"]})
        
        if not plan:
            plan = await db.plans.find_one({"name": "Free"})
            if not plan:
                plan = {
                    "_id": "default_free",
                    "name": "Free",
                    "max_queries_per_month": 1,
                    "max_emails_per_month": 10,
                    "max_file_uploads": 1,
                    "max_results_per_query": 10,
                    "max_templates": 1,
                    "max_file_size_mb": 5,
                    "price": 0,
                    "currency": "USD"
                }
        
        from plan_limit_service import PlanLimitService
        limit_service = PlanLimitService()
        limits = await limit_service.get_all_limits(current_user, plan)
        
        return limits
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Limit bilgileri alınamadı: {str(e)}"
        )

@router.get("/test-auth")
async def test_auth(current_user: str = Depends(get_current_user)):
    """Authentication test endpoint"""
    return {
        "message": "Authentication successful",
        "user_id": current_user,
        "status": "ok"
    }
