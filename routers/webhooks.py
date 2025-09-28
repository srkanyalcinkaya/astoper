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
    
    print(f"🔔 Webhook received: {request.method} {request.url}")
    print(f"📦 Payload size: {len(payload)} bytes")
    print(f"🔐 Signature header: {sig_header[:20]}..." if sig_header else "No signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        print(f"✅ Event constructed successfully: {event['type']}")
        print(f"📋 Event ID: {event['id']}")
    except ValueError as e:
        print(f"❌ Invalid payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        print(f"❌ Invalid signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    db = await get_async_db()
    
    try:
        if event['type'] == 'checkout.session.completed':
            print(f"🛒 Processing checkout.session.completed")
            session = event['data']['object']
            await handle_checkout_completed(db, session)
            
        elif event['type'] == 'customer.subscription.created':
            print(f"🆕 Processing customer.subscription.created")
            subscription = event['data']['object']
            await handle_subscription_created(db, subscription)
            
        elif event['type'] == 'customer.subscription.updated':
            print(f"🔄 Processing customer.subscription.updated")
            subscription = event['data']['object']
            await handle_subscription_updated(db, subscription)
            
        elif event['type'] == 'customer.subscription.deleted':
            print(f"🗑️ Processing customer.subscription.deleted")
            subscription = event['data']['object']
            await handle_subscription_deleted(db, subscription)
            
        elif event['type'] == 'invoice.payment_succeeded':
            print(f"💰 Processing invoice.payment_succeeded")
            invoice = event['data']['object']
            await handle_payment_succeeded(db, invoice)
            
        elif event['type'] == 'invoice.payment_failed':
            print(f"❌ Processing invoice.payment_failed")
            invoice = event['data']['object']
            await handle_payment_failed(db, invoice)
            
        else:
            print(f"⚠️ Unhandled event type: {event['type']}")
    except Exception as e:
        print(f"❌ Error processing webhook {event['type']}: {str(e)}")
        # Webhook'u başarısız olarak işaretleme, sadece logla
        import traceback
        traceback.print_exc()
    
    return {"status": "success"}

async def handle_checkout_completed(db, session):
    """Handle checkout session completed event"""
    print(f"🛒 handle_checkout_completed called")
    print(f"📋 Session ID: {session.get('id')}")
    print(f"👤 Customer ID: {session.get('customer')}")
    print(f"📊 Metadata: {session.get('metadata')}")
    
    user_id_str = session["metadata"].get("user_id")
    plan_id_str = session["metadata"].get("plan_id")
    
    print(f"🔍 User ID from metadata: {user_id_str}")
    print(f"🔍 Plan ID from metadata: {plan_id_str}")
    
    if not user_id_str or not plan_id_str:
        print("❌ Missing metadata in checkout session")
        return
    
    user_id = ObjectId(user_id_str)
    plan_id = ObjectId(plan_id_str)
    
    print(f"✅ Parsed User ID: {user_id}")
    print(f"✅ Parsed Plan ID: {plan_id}")
    
    subscription_id = session["subscription"]
    print(f"🔗 Subscription ID: {subscription_id}")
    
    subscription = stripe.Subscription.retrieve(subscription_id)
    print(f"📊 Stripe Subscription Status: {subscription.status}")
    print(f"👤 Stripe Customer ID: {subscription.customer}")
    
    subscription_data = {
        "user_id": user_id,
        "stripe_subscription_id": subscription.id,
        "stripe_customer_id": subscription.customer,
        "plan_id": plan_id,
        "status": subscription.status,
        "current_period_start": datetime.fromtimestamp(subscription.current_period_start) if hasattr(subscription, 'current_period_start') else datetime.utcnow(),
        "current_period_end": datetime.fromtimestamp(subscription.current_period_end) if hasattr(subscription, 'current_period_end') else datetime.utcnow(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    print(f"💾 Subscription data prepared: {subscription_data}")
    
    existing_subscription = await db.subscriptions.find_one({
        "stripe_subscription_id": subscription.id
    })
    
    if not existing_subscription:
        print(f"➕ Creating new subscription in database")
        result = await db.subscriptions.insert_one(subscription_data)
        print(f"✅ Subscription created with ID: {result.inserted_id}")
    else:
        print(f"⚠️ Subscription already exists: {existing_subscription['_id']}")
    
    print(f"👤 Updating user plan_id to: {plan_id}")
    user_update_result = await db.users.update_one(
        {"_id": user_id},
        {"$set": {
            "plan_id": plan_id,
            "stripe_subscription_id": subscription.id
        }}
    )
    print(f"✅ User updated: {user_update_result.modified_count} documents modified")
    
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
    
    update_data = {
        "status": subscription["status"],
        "updated_at": datetime.utcnow()
    }
    
    # Sadece mevcut alanları ekle
    if "current_period_start" in subscription:
        update_data["current_period_start"] = datetime.fromtimestamp(subscription["current_period_start"])
    if "current_period_end" in subscription:
        update_data["current_period_end"] = datetime.fromtimestamp(subscription["current_period_end"])
    
    await db.subscriptions.update_one(
        {"stripe_subscription_id": subscription["id"]},
        {"$set": update_data}
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
    # Invoice'da subscription alanı olmayabilir, kontrol et
    if "subscription" not in invoice:
        print(f"⚠️ Invoice'da subscription alanı yok: {invoice.get('id', 'unknown')}")
        return
    
    subscription_obj = await db.subscriptions.find_one({
        "stripe_subscription_id": invoice["subscription"]
    })
    
    if not subscription_obj:
        print(f"⚠️ Subscription bulunamadı: {invoice['subscription']}")
        return
    
    user = await db.users.find_one({"_id": subscription_obj["user_id"]})
    if not user:
        print(f"⚠️ User bulunamadı: {subscription_obj['user_id']}")
        return
    
    await db.logs.insert_one({
        "user_id": user["_id"],
        "action": "payment_succeeded",
        "details": f"Stripe webhook: Ödeme başarılı - Tutar: ${invoice.get('amount_paid', 0)/100}",
        "created_at": datetime.utcnow()
    })

async def handle_payment_failed(db, invoice):
    """Handle failed payment"""
    # Invoice'da subscription alanı olmayabilir, kontrol et
    if "subscription" not in invoice:
        print(f"⚠️ Invoice'da subscription alanı yok: {invoice.get('id', 'unknown')}")
        return
    
    subscription_obj = await db.subscriptions.find_one({
        "stripe_subscription_id": invoice["subscription"]
    })
    
    if not subscription_obj:
        print(f"⚠️ Subscription bulunamadı: {invoice['subscription']}")
        return
    
    user = await db.users.find_one({"_id": subscription_obj["user_id"]})
    if not user:
        print(f"⚠️ User bulunamadı: {subscription_obj['user_id']}")
        return
    
    await db.logs.insert_one({
        "user_id": user["_id"],
        "action": "payment_failed",
        "details": f"Stripe webhook: Ödeme başarısız - Tutar: ${invoice.get('amount_due', 0)/100}",
        "created_at": datetime.utcnow()
    })