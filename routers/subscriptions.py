from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from datetime import datetime, timedelta
import jwt
import stripe
from bson import ObjectId
from pydantic import BaseModel

from database import get_async_db
from models import Subscription, Plan, User
from config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])
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

@router.get("/", response_model=dict)
async def get_user_subscription(current_user: str = Depends(get_current_user)):
    """Get user's current subscription"""
    db = await get_async_db()
    user_id = ObjectId(current_user)
    
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    subscription = await db.subscriptions.find_one({
        "user_id": user_id,
        "status": {"$in": ["active", "trialing"]}
    })
    
    plan = None
    if subscription:
        plan = await db.plans.find_one({"_id": subscription["plan_id"]})
    elif user.get("plan_id"):
        plan = await db.plans.find_one({"_id": user["plan_id"]})
    
    if subscription:
        subscription["_id"] = str(subscription["_id"])
        subscription["user_id"] = str(subscription["user_id"])
        subscription["plan_id"] = str(subscription["plan_id"])
    
    if plan:
        plan["_id"] = str(plan["_id"])
    
    return {
        "subscription": subscription,
        "plan": plan,
        "user": {
            "id": str(user["_id"]),
            "email": user["email"],
            "username": user["username"],
            "full_name": user.get("full_name"),
            "stripe_customer_id": user.get("stripe_customer_id")
        }
    }

@router.get("/plans", response_model=dict)
async def get_available_plans():
    """Get all available subscription plans"""
    db = await get_async_db()
    
    plans_cursor = db.plans.find({"is_active": True}).sort("price", 1)
    plans = await plans_cursor.to_list(length=None)
    
    for plan in plans:
        plan["_id"] = str(plan["_id"])
    
    return {"plans": plans}

class SubscriptionRequest(BaseModel):
    plan_id: str
    payment_method_id: Optional[str] = None  # Checkout için gerekli değil

@router.post("/create-checkout-session", response_model=dict)
async def create_checkout_session(
    request: SubscriptionRequest,
    current_user: str = Depends(get_current_user)
):
    """Create Stripe Checkout Session for subscription"""
    db = await get_async_db()
    user_id = ObjectId(current_user)
    
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not ObjectId.is_valid(request.plan_id):
        raise HTTPException(status_code=400, detail="Invalid plan ID")
    
    plan = await db.plans.find_one({"_id": ObjectId(request.plan_id)})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    try:
        stripe_customer_id = user.get("stripe_customer_id")
        if not stripe_customer_id:
            customer = stripe.Customer.create(
                email=user["email"],
                name=user.get("full_name") or user["username"],
                metadata={"user_id": str(user_id)}
            )
            stripe_customer_id = customer.id
            
            await db.users.update_one(
                {"_id": user_id},
                {"$set": {"stripe_customer_id": stripe_customer_id}}
            )
        
        checkout_session = stripe.checkout.Session.create(
            customer=stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'try',
                    'product_data': {
                        'name': f"{plan['name']} Plan",
                        'description': f"{plan['max_queries_per_month']} aylık sorgu, {plan['max_file_uploads']} dosya yükleme, sorgu başına {plan.get('max_results_per_query', 10)} sonuç"
                    },
                    'unit_amount': int(plan["price"] * 100),  # Convert to kuruş
                    'recurring': {'interval': 'month'}
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f"http://localhost:3000/payment/success?session_id={{CHECKOUT_SESSION_ID}}&plan_id={request.plan_id}",
            cancel_url="http://localhost:3000/payment/cancel",
            metadata={
                'user_id': str(user_id),
                'plan_id': request.plan_id
            },
            subscription_data={
                'metadata': {
                    'user_id': str(user_id),
                    'plan_id': request.plan_id
                }
            }
        )
        
        await db.logs.insert_one({
            "user_id": user_id,
            "action": "checkout_session_created",
            "details": f"Stripe Checkout oturumu oluşturuldu: {plan['name']} - ₺{plan['price']}/ay",
            "created_at": datetime.utcnow()
        })
        
        return {
            "success": True,
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Subscription creation failed: {str(e)}")

class UpgradeRequest(BaseModel):
    new_plan_id: str

@router.post("/upgrade-subscription", response_model=dict)
async def upgrade_subscription(
    request: UpgradeRequest,
    current_user: str = Depends(get_current_user)
):
    """Upgrade user's subscription to a new plan"""
    db = await get_async_db()
    user_id = ObjectId(current_user)
    
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    current_subscription = await db.subscriptions.find_one({
        "user_id": user_id,
        "status": {"$in": ["active", "trialing"]}
    })
    
    if not current_subscription:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    if not ObjectId.is_valid(request.new_plan_id):
        raise HTTPException(status_code=400, detail="Invalid plan ID")
    
    new_plan = await db.plans.find_one({"_id": ObjectId(request.new_plan_id)})
    if not new_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    try:
        stripe_subscription = stripe.Subscription.retrieve(
            current_subscription["stripe_subscription_id"]
        )
        
        updated_subscription = stripe.Subscription.modify(
            stripe_subscription.id,
            items=[{
                "id": stripe_subscription["items"]["data"][0].id,
                "price_data": {
                    "currency": "try",
                    "product_data": {
                        "name": new_plan["name"],
                        "description": f"{new_plan['name']} - {new_plan['max_queries_per_month']} aylık sorgu"
                    },
                    "unit_amount": int(new_plan["price"] * 100),
                    "recurring": {"interval": "month"}
                }
            }],
            proration_behavior="always_invoice"
        )
        
        await db.subscriptions.update_one(
            {"_id": current_subscription["_id"]},
            {"$set": {
                "plan_id": ObjectId(request.new_plan_id),
                "status": updated_subscription.status,
                "current_period_start": datetime.fromtimestamp(updated_subscription.current_period_start),
                "current_period_end": datetime.fromtimestamp(updated_subscription.current_period_end),
                "updated_at": datetime.utcnow()
            }}
        )
        
        await db.users.update_one(
            {"_id": user_id},
            {"$set": {"plan_id": ObjectId(request.new_plan_id)}}
        )
        
        await db.logs.insert_one({
            "user_id": user_id,
            "action": "subscription_upgraded",
            "details": f"Abonelik yükseltildi: {new_plan['name']} - ₺{new_plan['price']}/ay",
            "created_at": datetime.utcnow()
        })
        
        return {
            "success": True,
            "message": "Subscription upgraded successfully",
            "new_plan": new_plan["name"]
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Subscription upgrade failed: {str(e)}")

@router.post("/cancel-subscription", response_model=dict)
async def cancel_subscription(current_user: str = Depends(get_current_user)):
    """Cancel user's subscription"""
    db = await get_async_db()
    user_id = ObjectId(current_user)
    
    subscription = await db.subscriptions.find_one({
        "user_id": user_id,
        "status": {"$in": ["active", "trialing"]}
    })
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    try:
        stripe.Subscription.delete(subscription["stripe_subscription_id"])
        
        await db.subscriptions.update_one(
            {"_id": subscription["_id"]},
            {"$set": {
                "status": "canceled",
                "updated_at": datetime.utcnow()
            }}
        )
        
        free_plan = await db.plans.find_one({"name": "Ücretsiz"})
        if free_plan:
            await db.users.update_one(
                {"_id": user_id},
                {"$set": {"plan_id": free_plan["_id"]}}
            )
        
        await db.logs.insert_one({
            "user_id": user_id,
            "action": "subscription_canceled",
            "details": "Abonelik iptal edildi - Ücretsiz plana geçiş yapıldı",
            "created_at": datetime.utcnow()
        })
        
        return {
            "success": True,
            "message": "Subscription canceled successfully"
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Subscription cancellation failed: {str(e)}")

@router.get("/usage", response_model=dict)
async def get_subscription_usage(current_user: str = Depends(get_current_user)):
    """Get current subscription usage"""
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
    
    query_limit = plan["max_queries_per_month"] if plan else 10
    file_limit = plan["max_file_uploads"] if plan else 0
    
    query_usage = (queries_this_month / query_limit * 100) if query_limit > 0 else 0
    file_usage = (files_this_month / file_limit * 100) if file_limit > 0 else 0
    
    return {
        "plan": {
            "name": plan["name"] if plan else "Ücretsiz",
            "query_limit": query_limit,
            "file_limit": file_limit
        },
        "usage": {
            "queries_this_month": queries_this_month,
            "files_this_month": files_this_month,
            "query_usage_percent": round(query_usage, 1),
            "file_usage_percent": round(file_usage, 1)
        },
        "limits_reached": {
            "queries": queries_this_month >= query_limit,
            "files": files_this_month >= file_limit if file_limit > 0 else False
        }
    }