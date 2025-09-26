from fastapi import APIRouter
from database import get_async_db
from models import DEFAULT_PLANS
from bson import ObjectId
from typing import Dict, Any

router = APIRouter(prefix="/plans", tags=["plans"])

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
