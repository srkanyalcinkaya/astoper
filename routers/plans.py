from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import get_async_db
from models import DEFAULT_PLANS
from bson import ObjectId
from typing import Dict, Any
import jwt
from config import settings

router = APIRouter(prefix="/plans", tags=["plans"])
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

def calculate_plan_costs(plan_data: Dict[str, Any]) -> Dict[str, float]:
    """Plan maliyetlerini hesapla"""
    name = plan_data.get("name", "")
    
    if name == "Free":
        return {
            "server_cost": 0.0,
            "ai_cost": 0.0,
            "email_cost": 0.0,
            "domain_cost": 0.0,
            "total_cost": 0.0
        }
    elif name == "Starter":
        return {
            "server_cost": 5.0,
            "ai_cost": 3.0,
            "email_cost": 2.0,
            "domain_cost": 0.1,
            "total_cost": 10.1
        }
    elif name == "Professional":
        return {
            "server_cost": 15.0,
            "ai_cost": 12.0,
            "email_cost": 8.0,
            "domain_cost": 0.1,
            "total_cost": 35.1
        }
    elif name == "Enterprise":
        return {
            "server_cost": 40.0,
            "ai_cost": 30.0,
            "email_cost": 25.0,
            "domain_cost": 0.1,
            "total_cost": 95.1
        }
    else:
        return {
            "server_cost": 0.0,
            "ai_cost": 0.0,
            "email_cost": 0.0,
            "domain_cost": 0.0,
            "total_cost": 0.0
        }

def convert_objectid_to_str(obj):
    """ObjectId'leri string'e çevir"""
    if isinstance(obj, dict):
        return {k: convert_objectid_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(item) for item in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    else:
        return obj

@router.get("/")
async def get_plans():
    """Get available plans with cost breakdown"""
    try:
        db = await get_async_db()
        
        plans = await db.plans.find({"is_active": True}).to_list(length=None)
        
        if not plans:
            for plan_data in DEFAULT_PLANS:
                plan_data["cost_breakdown"] = calculate_plan_costs(plan_data)
                await db.plans.insert_one(plan_data)
            plans = DEFAULT_PLANS
        else:
            for default_plan in DEFAULT_PLANS:
                default_plan["cost_breakdown"] = calculate_plan_costs(default_plan)
                await db.plans.update_one(
                    {"name": default_plan["name"]},
                    {"$set": {
                        "price": default_plan["price"],
                        "currency": default_plan["currency"],
                        "cost_breakdown": default_plan["cost_breakdown"],
                        "features": default_plan["features"],
                        "max_queries_per_month": default_plan["max_queries_per_month"],
                        "max_emails_per_month": default_plan["max_emails_per_month"],
                        "max_file_uploads": default_plan["max_file_uploads"],
                        "max_results_per_query": default_plan["max_results_per_query"],
                        "max_templates": default_plan["max_templates"],
                        "max_file_size_mb": default_plan["max_file_size_mb"]
                    }},
                    upsert=True
                )
            plans = await db.plans.find({"is_active": True}).to_list(length=None)
        
        for plan in plans:
            if "cost_breakdown" not in plan:
                plan["cost_breakdown"] = calculate_plan_costs(plan)
        
        plans = convert_objectid_to_str(plans)
        
        return {"plans": plans}
    except Exception as e:
        default_plans = DEFAULT_PLANS.copy()
        for plan in default_plans:
            plan["cost_breakdown"] = calculate_plan_costs(plan)
        return {"plans": convert_objectid_to_str(default_plans)}

@router.get("/costs")
async def get_plan_costs():
    """Get plan cost breakdown"""
    try:
        db = await get_async_db()
        
        plans = await db.plans.find({"is_active": True}).to_list(length=None)
        
        if not plans:
            plans = DEFAULT_PLANS
        
        cost_data = []
        for plan in plans:
            cost_breakdown = calculate_plan_costs(plan)
            cost_data.append({
                "name": plan.get("name", ""),
                "price": plan.get("price", 0),
                "currency": plan.get("currency", "USD"),
                "cost_breakdown": cost_breakdown,
                "profit_margin": round(((plan.get("price", 0) - cost_breakdown["total_cost"]) / plan.get("price", 1)) * 100, 1) if plan.get("price", 0) > 0 else 0
            })
        
        return {"cost_analysis": cost_data}
    except Exception as e:
        cost_data = []
        for plan in DEFAULT_PLANS:
            cost_breakdown = calculate_plan_costs(plan)
            cost_data.append({
                "name": plan.get("name", ""),
                "price": plan.get("price", 0),
                "currency": plan.get("currency", "USD"),
                "cost_breakdown": cost_breakdown,
                "profit_margin": round(((plan.get("price", 0) - cost_breakdown["total_cost"]) / plan.get("price", 1)) * 100, 1) if plan.get("price", 0) > 0 else 0
            })
        return {"cost_analysis": cost_data}

@router.get("/limits")
async def get_user_limits(current_user: str = Depends(get_current_user)):
    """Get current user's plan limits"""
    try:
        from plan_limit_service import PlanLimitService
        
        db = await get_async_db()
        user_id = ObjectId(current_user)
        
        user = await db.users.find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        plan = None
        if user.get("plan_id"):
            plan = await db.plans.find_one({"_id": user["plan_id"]})
        
        if not plan:
            # Varsayılan ücretsiz plan limitleri
            plan = {
                "name": "Free",
                "price": 0,
                "max_emails_per_month": 0,
                "max_templates": 1,
                "max_queries_per_month": 0,
                "max_file_uploads": 1,
                "max_file_size_mb": 5
            }
        
        limit_service = PlanLimitService()
        limits = await limit_service.get_all_limits(current_user, plan)
        
        return limits
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Limit bilgileri alınamadı: {str(e)}")
