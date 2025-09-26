from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from datetime import datetime
import jwt
from bson import ObjectId

from database import get_async_db
from models import User, Plan, Query, FileUpload
from schemas import UserUpdate, UserProfile
from config import settings

router = APIRouter(prefix="/users", tags=["users"])
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

@router.get("/me", response_model=dict)
async def get_current_user_profile(current_user: str = Depends(get_current_user)):
    """Get current user's profile"""
    db = await get_async_db()
    user_id = ObjectId(current_user)
    
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    plan = None
    if user.get("plan_id"):
        plan = await db.plans.find_one({"_id": user["plan_id"]})
    
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    
    queries_this_month = await db.queries.count_documents({
        "user_id": user_id,
        "created_at": {"$gte": month_start}
    })
    
    files_this_month = await db.file_uploads.count_documents({
        "user_id": user_id,
        "upload_date": {"$gte": month_start}
    })
    
    user["_id"] = str(user["_id"])
    if user.get("plan_id"):
        user["plan_id"] = str(user["plan_id"])
    
    if plan:
        plan["_id"] = str(plan["_id"])
    
    return {
        "user": user,
        "plan": plan,
        "usage": {
            "queries_this_month": queries_this_month,
            "files_this_month": files_this_month,
            "plan_limit": plan["max_queries_per_month"] if plan else 10,
            "file_limit": plan["max_file_uploads"] if plan else 0
        }
    }

@router.put("/me", response_model=dict)
async def update_current_user(
    user_update: UserUpdate,
    current_user: str = Depends(get_current_user)
):
    """Update current user's profile"""
    db = await get_async_db()
    user_id = ObjectId(current_user)
    
    update_dict = user_update.dict(exclude_unset=True)
    if update_dict:
        update_dict["updated_at"] = datetime.utcnow()
        await db.users.update_one(
            {"_id": user_id},
            {"$set": update_dict}
        )
    
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user["_id"] = str(user["_id"])
    if user.get("plan_id"):
        user["plan_id"] = str(user["plan_id"])
    
    return user

@router.get("/dashboard", response_model=dict)
async def get_dashboard_data(current_user: str = Depends(get_current_user)):
    """Get dashboard data for current user"""
    db = await get_async_db()
    user_id = ObjectId(current_user)
    
    user = await db.users.find_one({"_id": user_id})
    plan = None
    if user and user.get("plan_id"):
        plan = await db.plans.find_one({"_id": user["plan_id"]})
    
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    
    total_queries = await db.queries.count_documents({"user_id": user_id})
    monthly_queries = await db.queries.count_documents({
        "user_id": user_id,
        "created_at": {"$gte": month_start}
    })
    
    total_emails = db.queries.aggregate([
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": None, "total": {"$sum": "$emails_sent"}}}
    ])
    total_emails_list = await total_emails.to_list(length=None)
    total_emails_sent = total_emails_list[0]["total"] if total_emails_list else 0
    
    monthly_emails = db.queries.aggregate([
        {"$match": {"user_id": user_id, "created_at": {"$gte": month_start}}},
        {"$group": {"_id": None, "total": {"$sum": "$emails_sent"}}}
    ])
    monthly_emails_list = await monthly_emails.to_list(length=None)
    monthly_emails_sent = monthly_emails_list[0]["total"] if monthly_emails_list else 0
    
    successful_queries = await db.queries.count_documents({
        "user_id": user_id,
        "status": "completed"
    })
    success_rate = (successful_queries / total_queries * 100) if total_queries > 0 else 0
    
    plan_limit = plan["max_queries_per_month"] if plan else 1
    plan_usage = (monthly_queries / plan_limit * 100) if plan_limit > 0 else 0
    
    monthly_files = await db.file_uploads.count_documents({
        "user_id": user_id,
        "upload_date": {"$gte": month_start}
    })
    file_limit = plan["max_file_uploads"] if plan else 1
    file_usage = (monthly_files / file_limit * 100) if file_limit > 0 else 0
    
    recent_automations_cursor = db.queries.find({"user_id": user_id}).sort("created_at", -1).limit(5)
    recent_automations = await recent_automations_cursor.to_list(length=None)
    
    for automation in recent_automations:
        automation["_id"] = str(automation["_id"])
        automation["user_id"] = str(automation["user_id"])
    
    return {
        "stats": {
            "totalQueries": total_queries,
            "emailsSent": total_emails_sent,
            "successRate": round(success_rate, 1),
            "planUsage": round(plan_usage, 1),
            "fileUsage": round(file_usage, 1),
            "queriesThisMonth": monthly_queries,
            "filesThisMonth": monthly_files
        },
        "plan": {
            "_id": str(plan["_id"]) if plan else None,
            "name": plan["name"] if plan else "Free",
            "price": plan["price"] if plan else 0,
            "currency": plan["currency"] if plan else "USD",
            "query_limit": plan_limit,
            "file_limit": file_limit,
            "email_limit": plan["max_emails_per_month"] if plan else 10,
            "results_per_query": plan["max_results_per_query"] if plan else 10,
            "max_templates": plan["max_templates"] if plan else 1,
            "max_file_size_mb": plan["max_file_size_mb"] if plan else 5,
            "features": plan["features"] if plan else ["1 aylık sorgu", "Sorgu başına 10 sonuç", "1 dosya yükleme"]
        },
        "recentAutomations": recent_automations
    }

@router.get("/analytics", response_model=dict)
async def get_user_analytics(current_user: str = Depends(get_current_user)):
    """Get user analytics data"""
    db = await get_async_db()
    user_id = ObjectId(current_user)
    
    now = datetime.utcnow()
    
    query_stats_cursor = db.queries.aggregate([
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": None,
            "total": {"$sum": 1},
            "successful": {"$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}},
            "failed": {"$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}}
        }}
    ])
    
    query_stats_list = await query_stats_cursor.to_list(length=None)
    stats = query_stats_list[0] if query_stats_list else {"total": 0, "successful": 0, "failed": 0}
    
    email_stats_cursor = db.queries.aggregate([
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": None,
            "sent": {"$sum": "$emails_sent"},
            "found": {"$sum": "$emails_found"}
        }}
    ])
    
    email_stats_list = await email_stats_cursor.to_list(length=None)
    email_data = email_stats_list[0] if email_stats_list else {"sent": 0, "found": 0}
    
    top_queries_cursor = db.queries.aggregate([
        {"$match": {"user_id": user_id, "search_terms": {"$exists": True, "$ne": None}}},
        {"$group": {
            "_id": "$search_terms",
            "count": {"$sum": 1},
            "successful": {"$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ])
    
    monthly_data = []
    for i in range(6):
        month_date = datetime(now.year, now.month - i, 1)
        next_month = datetime(now.year, now.month - i + 1, 1) if now.month - i + 1 <= 12 else datetime(now.year + 1, 1, 1)
        
        month_queries = await db.queries.count_documents({
            "user_id": user_id,
            "created_at": {"$gte": month_date, "$lt": next_month}
        })
        
        month_emails_cursor = db.queries.aggregate([
            {"$match": {
                "user_id": user_id,
                "created_at": {"$gte": month_date, "$lt": next_month}
            }},
            {"$group": {"_id": None, "total": {"$sum": "$emails_sent"}}}
        ])
        
        month_emails_list = await month_emails_cursor.to_list(length=None)
        month_emails_sent = month_emails_list[0]["total"] if month_emails_list else 0
        
        monthly_data.append({
            "month": month_date.strftime("%b"),
            "queries": month_queries,
            "emails": month_emails_sent
        })
    
    monthly_data.reverse()
    
    return {
        "queryStats": {
            "total": stats["total"],
            "successful": stats["successful"],
            "failed": stats["failed"],
            "successRate": round((stats["successful"] / stats["total"] * 100) if stats["total"] > 0 else 0, 1)
        },
        "emailStats": {
            "sent": email_data["sent"],
            "found": email_data["found"],
            "opened": int(email_data["sent"] * 0.37),  # Mock open rate
            "clicked": int(email_data["sent"] * 0.072),  # Mock click rate
            "openRate": 37.0,
            "clickRate": 7.2
        },
        "topQueries": [
            {
                "query": item["_id"],
                "count": item["count"],
                "successRate": round((item["successful"] / item["count"] * 100) if item["count"] > 0 else 0)
            }
            for item in await top_queries_cursor.to_list(length=None)
        ],
        "monthlyData": monthly_data
    }