from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
from datetime import datetime
import jwt
import requests
import asyncio
from bson import ObjectId

from database import get_async_db
from models import Query, User, Plan
from schemas import QueryCreate, QueryUpdate
from config import settings

router = APIRouter(prefix="/search", tags=["search-engine"])
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

class SerpAPIService:
    """SERP API entegrasyonu için servis"""
    
    def __init__(self):
        self.api_key = settings.SERPAPI_KEY
        self.base_url = "https://serpapi.com/search"
    
    async def search(self, query: str, target_url: Optional[str] = None, num_results: int = 10) -> List[Dict[str, Any]]:
        """SERP API ile arama yap"""
        try:
            params = {
                "q": query,
                "api_key": self.api_key,
                "engine": "google",
                "num": num_results,
                "gl": "tr",  # Türkiye için
                "hl": "tr"   # Türkçe dil
            }
            
            if target_url:
                params["site"] = target_url
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if "organic_results" in data:
                for result in data["organic_results"]:
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("link", ""),
                        "snippet": result.get("snippet", ""),
                        "position": result.get("position", 0)
                    })
            
            return results
            
        except Exception as e:
            print(f"SERP API error: {e}")
            return []
    
    async def search_with_target_url(self, query: str, target_url: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Belirli bir site içinde arama yap"""
        try:
            site_query = f"site:{target_url} {query}"
            return await self.search(site_query, None, num_results)
        except Exception as e:
            print(f"Target URL search error: {e}")
            return []

class EmailExtractor:
    """Email adreslerini çıkaran servis"""
    
    def __init__(self):
        pass
    
    async def extract_emails_from_url(self, url: str) -> List[str]:
        """URL'den email adreslerini çıkar"""
        try:
            import re
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                        emails = re.findall(email_pattern, content)
                        
                        unique_emails = list(set(emails))
                        filtered_emails = [email for email in unique_emails if not self._is_spam_email(email)]
                        
                        return filtered_emails
                    else:
                        return []
        except Exception as e:
            print(f"Email extraction error for {url}: {e}")
            return []
    
    def _is_spam_email(self, email: str) -> bool:
        """Spam email'leri filtrele"""
        spam_domains = [
            "noreply", "no-reply", "donotreply", "do-not-reply",
            "example.com", "test.com", "localhost"
        ]
        
        email_lower = email.lower()
        for spam_domain in spam_domains:
            if spam_domain in email_lower:
                return True
        return False

@router.post("/serp-search")
async def serp_search(
    request: dict,
    current_user: str = Depends(get_current_user)
):
    """SERP API ile arama yap ve sonuçları döndür"""
    search_query = request.get("query", "")
    target_url = request.get("target_url")
    max_results = request.get("max_results", 10)
    
    if not search_query:
        raise HTTPException(
            status_code=400,
            detail="Arama sorgusu gerekli"
        )
    
    try:
        db = await get_async_db()
        user_id = ObjectId(current_user)
        
        user = await db.users.find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
        
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
        
        serp_service = SerpAPIService()
        
        if target_url:
            results = await serp_service.search_with_target_url(search_query, target_url, max_results)
        else:
            results = await serp_service.search(search_query, None, max_results)
        
        email_extractor = EmailExtractor()
        all_emails = []
        
        for result in results:
            url = result["url"]
            emails = await email_extractor.extract_emails_from_url(url)
            
            for email in emails:
                all_emails.append({
                    "email": email,
                    "source_url": url,
                    "source_title": result["title"],
                    "source_snippet": result["snippet"]
                })
        
        unique_emails = []
        seen_emails = set()
        for email_data in all_emails:
            if email_data["email"] not in seen_emails:
                unique_emails.append(email_data)
                seen_emails.add(email_data["email"])
        
        query_data = {
            "user_id": user_id,
            "query_type": "serpapi",
            "search_terms": search_query,
            "target_urls": [target_url] if target_url else [],
            "status": "completed",
            "results_count": len(results),
            "emails_found": len(unique_emails),
            "emails_sent": 0,
            "results_data": {
                "search_results": results,
                "emails_found": unique_emails
            },
            "created_at": datetime.utcnow(),
            "completed_at": datetime.utcnow()
        }
        
        result = await db.queries.insert_one(query_data)
        query_id = str(result.inserted_id)
        
        await db.logs.insert_one({
            "user_id": user_id,
            "query_id": result.inserted_id,
            "action": "serp_search_completed",
            "details": f"SERP arama tamamlandı: {len(results)} sonuç, {len(unique_emails)} email",
            "created_at": datetime.utcnow()
        })
        
        return {
            "query_id": query_id,
            "search_query": search_query,
            "target_url": target_url,
            "results_count": len(results),
            "emails_found": len(unique_emails),
            "search_results": results,
            "emails": unique_emails,
            "status": "completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Arama hatası: {str(e)}"
        )

@router.post("/extract-emails")
async def extract_emails_from_urls(
    request: dict,
    current_user: str = Depends(get_current_user)
):
    """URL listesinden email adreslerini çıkar"""
    urls = request.get("urls", [])
    
    if not urls:
        raise HTTPException(
            status_code=400,
            detail="En az bir URL gerekli"
        )
    
    try:
        email_extractor = EmailExtractor()
        all_emails = []
        
        for url in urls:
            emails = await email_extractor.extract_emails_from_url(url)
            for email in emails:
                all_emails.append({
                    "email": email,
                    "source_url": url
                })
        
        unique_emails = []
        seen_emails = set()
        for email_data in all_emails:
            if email_data["email"] not in seen_emails:
                unique_emails.append(email_data)
                seen_emails.add(email_data["email"])
        
        return {
            "urls_processed": len(urls),
            "emails_found": len(unique_emails),
            "emails": unique_emails
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Email çıkarma hatası: {str(e)}"
        )

@router.get("/history")
async def get_search_history(
    current_user: str = Depends(get_current_user),
    limit: int = 20
):
    """Kullanıcının arama geçmişini getir"""
    try:
        db = await get_async_db()
        user_id = ObjectId(current_user)
        
        queries_cursor = db.queries.find({
            "user_id": user_id,
            "query_type": "serpapi"
        }).sort("created_at", -1).limit(limit)
        
        queries = await queries_cursor.to_list(length=None)
        
        for query in queries:
            query["_id"] = str(query["_id"])
            query["user_id"] = str(query["user_id"])
        
        return {
            "queries": queries,
            "total": len(queries)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Geçmiş getirme hatası: {str(e)}"
        )

@router.get("/stats")
async def get_search_stats(
    current_user: str = Depends(get_current_user)
):
    """Kullanıcının arama istatistiklerini getir"""
    try:
        db = await get_async_db()
        user_id = ObjectId(current_user)
        
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)
        
        monthly_queries = await db.queries.count_documents({
            "user_id": user_id,
            "query_type": "serpapi",
            "created_at": {"$gte": month_start}
        })
        
        total_queries = await db.queries.count_documents({
            "user_id": user_id,
            "query_type": "serpapi"
        })
        
        total_emails_cursor = db.queries.aggregate([
            {"$match": {"user_id": user_id, "query_type": "serpapi"}},
            {"$group": {"_id": None, "total": {"$sum": "$emails_found"}}}
        ])
        total_emails_list = await total_emails_cursor.to_list(length=None)
        total_emails_found = total_emails_list[0]["total"] if total_emails_list else 0
        
        user = await db.users.find_one({"_id": user_id})
        plan = None
        if user and user.get("plan_id"):
            plan = await db.plans.find_one({"_id": user["plan_id"]})
        
        plan_limit = plan["max_queries_per_month"] if plan else 1
        usage_percentage = (monthly_queries / plan_limit * 100) if plan_limit > 0 else 0
        
        return {
            "monthly_queries": monthly_queries,
            "total_queries": total_queries,
            "total_emails_found": total_emails_found,
            "plan_limit": plan_limit,
            "usage_percentage": round(usage_percentage, 1),
            "plan_name": plan["name"] if plan else "Ücretsiz"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"İstatistik getirme hatası: {str(e)}"
        )
