from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from datetime import datetime, timedelta
import jwt
import asyncio
from bson import ObjectId

from database import get_async_db
from models import Query, User, Plan
from schemas import QueryCreate, QueryUpdate, EmailAutomationRequest, EmailAutomationResponse, EmailSearchResponse, EmailCategory
from config import settings
from email_automation_service import EmailAutomationService

router = APIRouter(prefix="/automation", tags=["automation"])
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def run_automation_background(query_id: str, user_id: str, automation_request: EmailAutomationRequest = None, max_results: int = 10):
    """Background task to run email automation"""
    try:
        db = await get_async_db()
        query_object_id = ObjectId(query_id)
        user_object_id = ObjectId(user_id)
        
        await db.queries.update_one(
            {"_id": query_object_id},
            {"$set": {"status": "processing", "updated_at": datetime.utcnow()}}
        )
        
        await db.logs.insert_one({
            "user_id": user_object_id,
            "query_id": query_object_id,
            "action": "automation_started",
            "details": f"Email otomasyonu başlatıldı - Max sonuç: {max_results}",
            "created_at": datetime.utcnow()
        })
        
        email_provider = await db.email_providers.find_one({
            "user_id": user_object_id,
            "is_active": True,
            "is_verified": True
        })
        
        if not email_provider:
            raise Exception("Email provider bulunamadı")
        
        automation_service = EmailAutomationService()
        
        if automation_request.automation_type == "file":
            query_record = await db.queries.find_one({"_id": query_object_id})
            file_path = query_record.get("file_path")
            
            result = automation_service.run_file_automation(
                file_path=file_path,
                max_results=max_results,
                selected_emails=automation_request.selected_emails,
                template_id=automation_request.template_id,
                custom_data=automation_request.custom_data
            )
        else:
            result = automation_service.run_automation(
                search_queries=automation_request.search_queries,
                target_urls=automation_request.target_urls,
                use_serpapi=automation_request.use_serpapi,
                selected_emails=automation_request.selected_emails,
                template_id=automation_request.template_id,
                custom_data=automation_request.custom_data
            )
        
        await db.queries.update_one(
            {"_id": query_object_id},
            {"$set": {
                "status": result.get("status", "completed"),
                "results_count": result.get("websites_analyzed", 0),
                "emails_found": result.get("emails_found", 0),
                "emails_sent": result.get("emails_sent", 0),
                "results_data": result,
                "completed_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }}
        )
        
        await db.logs.insert_one({
            "user_id": user_object_id,
            "query_id": query_object_id,
            "action": "automation_completed",
            "details": f"Otomasyon tamamlandı: {result.get('emails_sent', 0)} email gönderildi",
            "created_at": datetime.utcnow()
        })
        
    except Exception as e:
        await db.logs.insert_one({
            "user_id": ObjectId(user_id),
            "query_id": ObjectId(query_id),
            "action": "automation_failed",
            "details": f"Otomasyon hatası: {str(e)}",
            "created_at": datetime.utcnow()
        })
        
        await db.queries.update_one(
            {"_id": ObjectId(query_id)},
            {"$set": {"status": "failed", "updated_at": datetime.utcnow()}}
        )

@router.post("/search-emails", response_model=EmailSearchResponse)
async def search_and_categorize_emails(
    request: dict,
    current_user: str = Depends(get_current_user)
):
    """Arama sorgularından eposta adreslerini getir ve kategorize et"""
    search_queries = request.get("search_queries", [])
    target_urls = request.get("target_urls", [])
    use_serpapi = request.get("use_serpapi", True)
    max_results = request.get("max_results", 50)
    
    if not search_queries and not target_urls:
        raise HTTPException(
            status_code=400,
            detail="En az bir arama sorgusu veya hedef URL gerekli"
        )
    
    try:
        automation_service = EmailAutomationService()
        
        all_website_urls = set()
        target_websites = []
        
        if use_serpapi and search_queries:
            for query in search_queries:
                results = automation_service.get_serpapi_results(query, 10)
                
                for result in results:
                    url = result['url']
                    all_website_urls.add(url)
                    
                    is_wordpress = automation_service.is_wordpress_site(url)
                    seo_analysis = automation_service.analyze_seo_quality(url)
                    
                    if is_wordpress or seo_analysis['is_poor_seo']:
                        target_websites.append({
                            'url': url,
                            'title': result['title'],
                            'is_wordpress': is_wordpress,
                            'seo_score': seo_analysis['seo_score'],
                            'seo_issues': seo_analysis['issues']
                        })
        
        if target_urls:
            for url in target_urls:
                all_website_urls.add(url)
                target_websites.append({
                    'url': url,
                    'title': 'Manuel Giriş',
                    'is_wordpress': automation_service.is_wordpress_site(url),
                    'seo_score': automation_service.analyze_seo_quality(url)['seo_score'],
                    'seo_issues': automation_service.analyze_seo_quality(url)['issues']
                })
        
        if not target_websites:
            return EmailSearchResponse(
                emails=[],
                total_found=0,
                search_queries=search_queries,
                categories=[]
            )
        
        all_emails = set()
        email_data = []
        
        for website_data in target_websites[:max_results]:  # Limit uygula
            website_url = website_data['url']
            emails = automation_service.scrape_emails(website_url)
            
            for email in emails:
                if email not in all_emails:
                    all_emails.add(email)
                    
                    category = automation_service.categorize_email_with_ai(email, website_data)
                    
                    email_data.append(EmailCategory(
                        email=email,
                        category=category["category"],
                        confidence=category["confidence"],
                        website_url=website_url,
                        company_name=website_data.get('title', ''),
                        industry=category.get("industry", "")
                    ))
        
        categories = list(set([email.category for email in email_data]))
        
        return EmailSearchResponse(
            emails=email_data,
            total_found=len(email_data),
            search_queries=search_queries,
            categories=categories
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Email arama hatası: {str(e)}"
        )

@router.get("/", response_model=List[dict])
async def get_user_automations(current_user: str = Depends(get_current_user)):
    """Get user's automations"""
    db = await get_async_db()
    user_id = ObjectId(current_user)
    
    queries_cursor = db.queries.find({"user_id": user_id}).sort("created_at", -1).limit(50)
    queries = await queries_cursor.to_list(length=None)
    
    for query in queries:
        query["_id"] = str(query["_id"])
        query["user_id"] = str(query["user_id"])
        if query.get("plan_id"):
            query["plan_id"] = str(query["plan_id"])
    
    return queries

@router.get("/stats", response_model=dict)
async def get_automation_stats(current_user: str = Depends(get_current_user)):
    """Get user's automation statistics"""
    db = await get_async_db()
    user_id = ObjectId(current_user)
    
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    
    user = await db.users.find_one({"_id": user_id})
    plan = None
    if user and user.get("plan_id"):
        plan = await db.plans.find_one({"_id": user["plan_id"]})
    
    total_queries = await db.queries.count_documents({"user_id": user_id})
    monthly_queries = await db.queries.count_documents({
        "user_id": user_id,
        "created_at": {"$gte": month_start}
    })
    
    total_emails_cursor = db.queries.aggregate([
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": None, "total": {"$sum": "$emails_sent"}}}
    ])
    total_emails_list = await total_emails_cursor.to_list(length=None)
    total_emails_sent = total_emails_list[0]["total"] if total_emails_list else 0
    
    monthly_emails_cursor = db.queries.aggregate([
        {"$match": {"user_id": user_id, "created_at": {"$gte": month_start}}},
        {"$group": {"_id": None, "total": {"$sum": "$emails_sent"}}}
    ])
    monthly_emails_list = await monthly_emails_cursor.to_list(length=None)
    monthly_emails_sent = monthly_emails_list[0]["total"] if monthly_emails_list else 0
    
    successful_queries = await db.queries.count_documents({
        "user_id": user_id,
        "status": "completed"
    })
    success_rate = (successful_queries / total_queries * 100) if total_queries > 0 else 0
    
    plan_limit = plan["max_queries_per_month"] if plan else 10
    plan_usage = (monthly_queries / plan_limit * 100) if plan_limit > 0 else 0
    
    return {
        "totalQueries": total_queries,
        "queriesThisMonth": monthly_queries,
        "totalEmailsSent": total_emails_sent,
        "emailsSentThisMonth": monthly_emails_sent,
        "successRate": round(success_rate, 1),
        "planUsage": round(plan_usage, 1),
        "planLimit": plan_limit,
        "plan": {
            "name": plan["name"] if plan else "Ücretsiz",
            "query_limit": plan_limit
        } if plan else {"name": "Ücretsiz", "query_limit": 10}
    }

@router.post("/", response_model=EmailAutomationResponse)
async def create_automation(
    automation_request: EmailAutomationRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """Create new email automation"""
    db = await get_async_db()
    user_id = ObjectId(current_user)
    
    email_provider = await db.email_providers.find_one({
        "user_id": user_id,
        "is_active": True,
        "is_verified": True
    })
    
    if not email_provider:
        raise HTTPException(
            status_code=400,
            detail="Email otomasyonu başlatmak için önce email provider eklemelisiniz. Email Providers sayfasından email hesabınızı ekleyin."
        )
    
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    plan = None
    if user.get("plan_id"):
        plan = await db.plans.find_one({"_id": user["plan_id"]})
    
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    monthly_queries = await db.queries.count_documents({
        "user_id": user_id,
        "created_at": {"$gte": month_start}
    })
    
    plan_limit = plan["max_queries_per_month"] if plan else 1
    if monthly_queries >= plan_limit:
        raise HTTPException(
            status_code=400,
            detail=f"Aylık sorgu limitinize ulaştınız ({plan_limit}). Paketinizi yükseltebilirsiniz."
        )
    
    monthly_emails_sent = db.queries.aggregate([
        {"$match": {"user_id": user_id, "created_at": {"$gte": month_start}}},
        {"$group": {"_id": None, "total": {"$sum": "$emails_sent"}}}
    ])
    monthly_emails_list = await monthly_emails_sent.to_list(length=None)
    monthly_emails_count = monthly_emails_list[0]["total"] if monthly_emails_list else 0
    
    email_limit = plan["max_emails_per_month"] if plan else 10
    if monthly_emails_count >= email_limit:
        raise HTTPException(
            status_code=400,
            detail=f"Aylık email gönderim limitinize ulaştınız ({email_limit}). Paketinizi yükseltebilirsiniz."
        )
    
    if automation_request.automation_type == "search":
        if not automation_request.search_queries and not automation_request.target_urls:
            raise HTTPException(
                status_code=400,
                detail="Arama otomasyonu için en az bir arama sorgusu veya hedef URL gerekli."
            )
    elif automation_request.automation_type == "file":
        if not automation_request.file_id:
            raise HTTPException(
                status_code=400,
                detail="Dosya otomasyonu için dosya seçmelisiniz."
            )
    else:
        raise HTTPException(
            status_code=400,
            detail="Geçersiz otomasyon tipi. 'search' veya 'file' olmalı."
        )
    
    file_path = None
    if automation_request.file_id:
        if not ObjectId.is_valid(automation_request.file_id):
            raise HTTPException(status_code=400, detail="Geçersiz dosya ID")
        
        file_record = await db.file_uploads.find_one({
            "_id": ObjectId(automation_request.file_id),
            "user_id": user_id
        })
        
        if not file_record:
            raise HTTPException(status_code=404, detail="Dosya bulunamadı")
        
        file_path = file_record["file_path"]
    
    if automation_request.automation_type == "file":
        query_type = "file_upload"
    elif automation_request.automation_type == "search":
        if automation_request.use_serpapi:
            query_type = "serpapi"
        else:
            query_type = "manual"
    
    query_data = {
        "user_id": user_id,
        "query_type": query_type,
        "automation_type": automation_request.automation_type,
        "search_terms": ", ".join(automation_request.search_queries) if automation_request.search_queries else None,
        "target_urls": automation_request.target_urls or [],
        "file_path": file_path,
        "selected_emails": automation_request.selected_emails or [],
        "template_id": automation_request.template_id,
        "ai_template_prompt": automation_request.ai_template_prompt,
        "custom_data": automation_request.custom_data or {},
        "status": "pending",
        "results_count": 0,
        "emails_found": 0,
        "emails_sent": 0,
        "results_data": {},
        "max_results": plan["max_results_per_query"] if plan else 10,
        "created_at": datetime.utcnow(),
        "completed_at": None
    }
    
    result = await db.queries.insert_one(query_data)
    query_id = str(result.inserted_id)
    
    log_details = f"Otomasyon oluşturuldu: {query_type}"
    if automation_request.search_queries:
        log_details += f" - {len(automation_request.search_queries)} arama sorgusu"
    if automation_request.file_id:
        log_details += f" - Dosya ID: {automation_request.file_id}"
    log_details += f" - Maksimum sonuç: {query_data['max_results']}"
    
    await db.logs.insert_one({
        "user_id": user_id,
        "query_id": result.inserted_id,
        "action": "automation_created",
        "details": log_details,
        "created_at": datetime.utcnow()
    })
    
    background_tasks.add_task(
        run_automation_background,
        query_id=query_id,
        user_id=current_user,
        automation_request=automation_request,
        max_results=query_data['max_results']
    )
    
    return EmailAutomationResponse(
        query_id=query_id,
        status="pending",
        message="Email automation started in background",
        estimated_time="5-10 minutes"
    )

@router.get("/user-logs")
async def get_automation_logs(current_user: str = Depends(get_current_user)):
    """Get user's automation logs"""
    try:
        db = await get_async_db()
        user_id = ObjectId(current_user)
        
        logs_cursor = db.logs.find({"user_id": user_id}).sort("created_at", -1).limit(50)
        logs = await logs_cursor.to_list(length=None)
        
        for log in logs:
            log["_id"] = str(log["_id"])
            log["user_id"] = str(log["user_id"])
            if log.get("query_id"):
                log["query_id"] = str(log["query_id"])
        
        return logs
    except Exception as e:
        print(f"Logs endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Logs fetch failed: {str(e)}")

@router.get("/{query_id}", response_model=dict)
async def get_automation(
    query_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get specific automation details"""
    db = await get_async_db()
    user_id = ObjectId(current_user)
    
    if not ObjectId.is_valid(query_id):
        raise HTTPException(status_code=400, detail="Invalid query ID")
    
    query = await db.queries.find_one({
        "_id": ObjectId(query_id),
        "user_id": user_id
    })
    
    if not query:
        raise HTTPException(status_code=404, detail="Automation not found")
    
    query["_id"] = str(query["_id"])
    query["user_id"] = str(query["user_id"])
    
    return query

@router.get("/logs/stats", response_model=dict)
async def get_logs_stats(current_user: str = Depends(get_current_user)):
    """Get user's log statistics"""
    db = await get_async_db()
    user_id = ObjectId(current_user)
    
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    
    total_logs = await db.logs.count_documents({"user_id": user_id})
    monthly_logs = await db.logs.count_documents({
        "user_id": user_id,
        "created_at": {"$gte": month_start}
    })
    
    action_stats = db.logs.aggregate([
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$action", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ])
    action_distribution = await action_stats.to_list(length=None)
    
    return {
        "totalLogs": total_logs,
        "logsThisMonth": monthly_logs,
        "actionDistribution": action_distribution
    }

@router.put("/{query_id}", response_model=dict)
async def update_automation(
    query_id: str,
    update_data: QueryUpdate,
    current_user: str = Depends(get_current_user)
):
    """Update automation status"""
    db = await get_async_db()
    user_id = ObjectId(current_user)
    
    if not ObjectId.is_valid(query_id):
        raise HTTPException(status_code=400, detail="Invalid query ID")
    
    update_dict = update_data.dict(exclude_unset=True)
    if update_dict:
        update_dict["updated_at"] = datetime.utcnow()
        await db.queries.update_one(
            {"_id": ObjectId(query_id), "user_id": user_id},
            {"$set": update_dict}
        )
    
    query = await db.queries.find_one({
        "_id": ObjectId(query_id),
        "user_id": user_id
    })
    
    if not query:
        raise HTTPException(status_code=404, detail="Automation not found")
    
    query["_id"] = str(query["_id"])
    query["user_id"] = str(query["user_id"])
    
    return query