from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import get_async_db
from models import Subscription, User
from schemas import (
    SubscriptionCancellationRequest, 
    SubscriptionCancellationResponse,
    SubscriptionUpdateRequest
)
from bson import ObjectId
from datetime import datetime, timedelta
import stripe
import os
from typing import Optional
import jwt
from config import settings

router = APIRouter(prefix="/subscription", tags=["subscription"])
security = HTTPBearer()

stripe.api_key = settings.STRIPE_SECRET_KEY

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Mevcut kullanıcıyı JWT token'dan al"""
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Geçersiz token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token süresi dolmuş")
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail="Geçersiz token")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Kimlik doğrulama hatası")

@router.get("/status")
async def get_subscription_status(
    current_user: str = Depends(get_current_user),
    db=Depends(get_async_db)
):
    """Kullanıcının abonelik durumunu getir"""
    try:
        subscription = await db.subscriptions.find_one({
            "user_id": ObjectId(current_user),
            "status": {"$in": ["active", "past_due"]}
        })
        
        if not subscription:
            return {
                "has_subscription": False,
                "message": "Aktif abonelik bulunamadı"
            }
        
        now = datetime.utcnow()
        current_period_end = subscription["current_period_end"]
        
        if isinstance(current_period_end, str):
            current_period_end = datetime.fromisoformat(current_period_end.replace('Z', '+00:00'))
        
        days_remaining = (current_period_end - now).days
        
        return {
            "has_subscription": True,
            "subscription": {
                "id": str(subscription["_id"]),
                "status": subscription["status"],
                "current_period_end": subscription["current_period_end"].isoformat() if isinstance(subscription["current_period_end"], datetime) else subscription["current_period_end"],
                "days_remaining": max(0, days_remaining),
                "auto_renewal": subscription.get("auto_renewal", True),
                "cancellation_requested": subscription.get("cancellation_requested", False),
                "service_end_date": subscription.get("service_end_date").isoformat() if subscription.get("service_end_date") and isinstance(subscription.get("service_end_date"), datetime) else subscription.get("service_end_date")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Abonelik durumu alınamadı: {str(e)}")

@router.post("/cancel", response_model=SubscriptionCancellationResponse)
async def cancel_subscription(
    cancellation_data: SubscriptionCancellationRequest,
    current_user: str = Depends(get_current_user),
    db=Depends(get_async_db)
):
    """Abonelik iptal talebi"""
    try:
        subscription = await db.subscriptions.find_one({
            "user_id": ObjectId(current_user),
            "status": {"$in": ["active", "past_due"]}
        })
        
        if not subscription:
            raise HTTPException(
                status_code=404, 
                detail="Aktif abonelik bulunamadı"
            )
        
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            stripe_subscription = stripe.Subscription.retrieve(
                subscription["stripe_subscription_id"],
                api_key=settings.STRIPE_SECRET_KEY
            )
            
            if not cancellation_data.auto_renewal:
                stripe.Subscription.modify(
                    subscription["stripe_subscription_id"],
                    cancel_at_period_end=True,
                    api_key=settings.STRIPE_SECRET_KEY
                )
            else:
                pass
                
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Stripe hatası: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"İptal işlemi sırasında hata: {str(e)}"
            )
        
        now = datetime.utcnow()
        service_end_date = subscription["current_period_end"]  # Mevcut dönem sonuna kadar hizmet
        
        update_data = {
            "cancellation_requested": True,
            "cancellation_date": now,
            "cancellation_reason": cancellation_data.cancellation_reason,
            "cancellation_feedback": cancellation_data.feedback,
            "auto_renewal": cancellation_data.auto_renewal,
            "service_end_date": service_end_date,
            "updated_at": now
        }
        
        await db.subscriptions.update_one(
            {"_id": subscription["_id"]},
            {"$set": update_data}
        )
        
        
        return SubscriptionCancellationResponse(
            success=True,
            message="Abonelik iptal talebi başarıyla kaydedildi. Hizmetiniz mevcut dönem sonuna kadar devam edecek.",
            cancellation_date=now,
            service_end_date=service_end_date,
            auto_renewal=cancellation_data.auto_renewal
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"İptal işlemi sırasında hata: {str(e)}"
        )

@router.post("/reactivate")
async def reactivate_subscription(
    current_user: str = Depends(get_current_user),
    db=Depends(get_async_db)
):
    """İptal edilmiş aboneliği yeniden aktifleştir"""
    try:
        subscription = await db.subscriptions.find_one({
            "user_id": ObjectId(current_user),
            "cancellation_requested": True
        })
        
        if not subscription:
            raise HTTPException(
                status_code=404, 
                detail="İptal edilmiş abonelik bulunamadı"
            )
        
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            stripe.Subscription.modify(
                subscription["stripe_subscription_id"],
                cancel_at_period_end=False,
                api_key=settings.STRIPE_SECRET_KEY
            )
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Stripe hatası: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Yeniden aktifleştirme sırasında hata: {str(e)}"
            )
        
        await db.subscriptions.update_one(
            {"_id": subscription["_id"]},
            {
                "$set": {
                    "cancellation_requested": False,
                    "auto_renewal": True,
                    "updated_at": datetime.utcnow()
                },
                "$unset": {
                    "cancellation_date": "",
                    "cancellation_reason": "",
                    "cancellation_feedback": "",
                    "service_end_date": ""
                }
            }
        )
        
        return {
            "success": True,
            "message": "Abonelik başarıyla yeniden aktifleştirildi"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Yeniden aktifleştirme sırasında hata: {str(e)}"
        )

@router.put("/update")
async def update_subscription(
    update_data: SubscriptionUpdateRequest,
    current_user: str = Depends(get_current_user),
    db=Depends(get_async_db)
):
    """Abonelik ayarlarını güncelle"""
    try:
        subscription = await db.subscriptions.find_one({
            "user_id": ObjectId(current_user),
            "status": {"$in": ["active", "past_due"]}
        })
        
        if not subscription:
            raise HTTPException(
                status_code=404, 
                detail="Aktif abonelik bulunamadı"
            )
        
        update_fields = {"updated_at": datetime.utcnow()}
        
        if update_data.auto_renewal is not None:
            update_fields["auto_renewal"] = update_data.auto_renewal
            
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            stripe.Subscription.modify(
                subscription["stripe_subscription_id"],
                cancel_at_period_end=not update_data.auto_renewal,
                api_key=settings.STRIPE_SECRET_KEY
            )
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Stripe hatası: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Güncelleme sırasında hata: {str(e)}"
            )
        
        if update_data.cancellation_reason:
            update_fields["cancellation_reason"] = update_data.cancellation_reason
        
        await db.subscriptions.update_one(
            {"_id": subscription["_id"]},
            {"$set": update_fields}
        )
        
        return {
            "success": True,
            "message": "Abonelik ayarları başarıyla güncellendi"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Güncelleme sırasında hata: {str(e)}"
        )

@router.get("/cancellation-reasons")
async def get_cancellation_reasons():
    """İptal nedenleri listesini getir"""
    return {
        "reasons": [
            {"id": "too_expensive", "label": "Çok pahalı"},
            {"id": "not_using", "label": "Kullanmıyorum"},
            {"id": "found_alternative", "label": "Alternatif buldum"},
            {"id": "technical_issues", "label": "Teknik sorunlar"},
            {"id": "missing_features", "label": "Eksik özellikler"},
            {"id": "poor_support", "label": "Kötü destek"},
            {"id": "other", "label": "Diğer"}
        ]
    }
