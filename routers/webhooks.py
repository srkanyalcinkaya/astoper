from fastapi import APIRouter, Request, HTTPException
import stripe
import json
from datetime import datetime
from bson import ObjectId

from database import get_async_db
from config import settings

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

stripe.api_key = settings.STRIPE_SECRET_KEY

@router.post("/stripe")
async def stripe_webhook(request: Request):
    """Stripe webhook handler"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    db = await get_async_db()
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        await handle_checkout_completed(db, session)
        
    elif event['type'] == 'customer.subscription.created':
        subscription = event['data']['object']
        await handle_subscription_created(db, subscription)
        
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        await handle_subscription_updated(db, subscription)
        
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        await handle_subscription_deleted(db, subscription)
        
    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        await handle_payment_succeeded(db, invoice)
        
    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        await handle_payment_failed(db, invoice)
        
    else:
        print(f"Unhandled event type: {event['type']}")
    
    return {"status": "success"}

async def handle_checkout_completed(db, session):
    """Handle checkout session completed event"""
    user_id_str = session["metadata"].get("user_id")
    plan_id_str = session["metadata"].get("plan_id")
    
    if not user_id_str or not plan_id_str:
        print("Missing metadata in checkout session")
        return
    
    user_id = ObjectId(user_id_str)
    plan_id = ObjectId(plan_id_str)
    
    subscription_id = session["subscription"]
    subscription = stripe.Subscription.retrieve(subscription_id)
    
    subscription_data = {
        "user_id": user_id,
        "stripe_subscription_id": subscription.id,
        "stripe_customer_id": subscription.customer,
        "plan_id": plan_id,
        "status": subscription.status,
        "current_period_start": datetime.fromtimestamp(subscription.current_period_start),
        "current_period_end": datetime.fromtimestamp(subscription.current_period_end),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    existing_subscription = await db.subscriptions.find_one({
        "stripe_subscription_id": subscription.id
    })
    
    if not existing_subscription:
        await db.subscriptions.insert_one(subscription_data)
    
    await db.users.update_one(
        {"_id": user_id},
        {"$set": {
            "plan_id": plan_id,
            "stripe_subscription_id": subscription.id
        }}
    )
    
    plan = await db.plans.find_one({"_id": plan_id})
    
    await db.logs.insert_one({
        "user_id": user_id,
        "action": "checkout_completed",
        "details": f"Stripe Checkout tamamlandı: {plan['name'] if plan else 'Plan'} - Abonelik aktif",
        "created_at": datetime.utcnow()
    })

async def handle_subscription_created(db, subscription):
    """Handle subscription created event"""
    user = await db.users.find_one({"stripe_customer_id": subscription["customer"]})
    if not user:
        return
    
    await db.subscriptions.update_one(
        {"stripe_subscription_id": subscription["id"]},
        {"$set": {
            "status": subscription["status"],
            "current_period_start": datetime.fromtimestamp(subscription["current_period_start"]),
            "current_period_end": datetime.fromtimestamp(subscription["current_period_end"]),
            "updated_at": datetime.utcnow()
        }}
    )
    
    await db.logs.insert_one({
        "user_id": user["_id"],
        "action": "subscription_webhook_created",
        "details": f"Stripe webhook: Abonelik oluşturuldu - Status: {subscription['status']}",
        "created_at": datetime.utcnow()
    })

async def handle_subscription_updated(db, subscription):
    """Handle subscription updated event"""
    user = await db.users.find_one({"stripe_customer_id": subscription["customer"]})
    if not user:
        return
    
    cancel_at_period_end = subscription.get("cancel_at_period_end", False)
    
    update_data = {
        "status": subscription["status"],
        "current_period_start": datetime.fromtimestamp(subscription["current_period_start"]),
        "current_period_end": datetime.fromtimestamp(subscription["current_period_end"]),
        "updated_at": datetime.utcnow()
    }
    
    if cancel_at_period_end:
        update_data.update({
            "cancellation_requested": True,
            "auto_renewal": False,
            "service_end_date": datetime.fromtimestamp(subscription["current_period_end"])
        })
    
    await db.subscriptions.update_one(
        {"stripe_subscription_id": subscription["id"]},
        {"$set": update_data}
    )
    
    log_details = f"Stripe webhook: Abonelik güncellendi - Status: {subscription['status']}"
    if cancel_at_period_end:
        log_details += " - Dönem sonunda iptal edilecek"
    
    await db.logs.insert_one({
        "user_id": user["_id"],
        "action": "subscription_webhook_updated",
        "details": log_details,
        "created_at": datetime.utcnow()
    })

async def handle_subscription_deleted(db, subscription):
    """Handle subscription deleted event"""
    user = await db.users.find_one({"stripe_customer_id": subscription["customer"]})
    if not user:
        return
    
    await db.subscriptions.update_one(
        {"stripe_subscription_id": subscription["id"]},
        {"$set": {
            "status": "canceled",
            "updated_at": datetime.utcnow()
        }}
    )
    
    free_plan = await db.plans.find_one({"name": "Ücretsiz"})
    if free_plan:
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"plan_id": free_plan["_id"]}}
        )
    
    await db.logs.insert_one({
        "user_id": user["_id"],
        "action": "subscription_webhook_canceled",
        "details": "Stripe webhook: Abonelik iptal edildi - Ücretsiz plana geçiş",
        "created_at": datetime.utcnow()
    })

async def handle_payment_succeeded(db, invoice):
    """Handle successful payment"""
    subscription_obj = await db.subscriptions.find_one({
        "stripe_subscription_id": invoice["subscription"]
    })
    
    if not subscription_obj:
        return
    
    user = await db.users.find_one({"_id": subscription_obj["user_id"]})
    if not user:
        return
    
    await db.logs.insert_one({
        "user_id": user["_id"],
        "action": "payment_succeeded",
        "details": f"Stripe webhook: Ödeme başarılı - Tutar: ₺{invoice['amount_paid']/100}",
        "created_at": datetime.utcnow()
    })

async def handle_payment_failed(db, invoice):
    """Handle failed payment"""
    subscription_obj = await db.subscriptions.find_one({
        "stripe_subscription_id": invoice["subscription"]
    })
    
    if not subscription_obj:
        return
    
    user = await db.users.find_one({"_id": subscription_obj["user_id"]})
    if not user:
        return
    
    await db.logs.insert_one({
        "user_id": user["_id"],
        "action": "payment_failed",
        "details": f"Stripe webhook: Ödeme başarısız - Tutar: ₺{invoice['amount_due']/100}",
        "created_at": datetime.utcnow()
    })