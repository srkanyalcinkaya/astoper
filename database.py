import motor.motor_asyncio
from pymongo import MongoClient
from config import settings
from models import DEFAULT_PLANS, Plan
import logging
import asyncio

logger = logging.getLogger(__name__)

client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
database = client[settings.DATABASE_NAME]

sync_client = MongoClient(settings.MONGODB_URL)
sync_database = sync_client[settings.DATABASE_NAME]

collections = {
    "users": database.users,
    "plans": database.plans,
    "queries": database.queries,
    "logs": database.logs,
    "file_uploads": database.file_uploads,
    "subscriptions": database.subscriptions,
    "email_templates": database.email_templates,
    "analytics": database.analytics,
    "email_providers": database.email_providers,
    "email_tracking": database.email_tracking
}

def get_db():
    return sync_database

async def get_async_db():
    return database

async def get_users_collection():
    return database.users

async def get_plans_collection():
    return database.plans

async def get_queries_collection():
    return database.queries

async def get_logs_collection():
    return database.logs

async def get_file_uploads_collection():
    return database.file_uploads

async def get_subscriptions_collection():
    return database.subscriptions

async def get_email_templates_collection():
    return database.email_templates

async def get_analytics_collection():
    return database.analytics

async def get_email_providers_collection():
    return database.email_providers

async def get_email_tracking_collection():
    return database.email_tracking

async def create_indexes():
    """Create database indexes for better performance."""
    try:
        await database.users.create_index("email", unique=True)
        await database.users.create_index("username", unique=True)
        await database.users.create_index("is_active")
        
        await database.queries.create_index("user_id")
        await database.queries.create_index("status")
        await database.queries.create_index("created_at")
        
        await database.logs.create_index("user_id")
        await database.logs.create_index("action")
        await database.logs.create_index("created_at")
        
        await database.file_uploads.create_index("user_id")
        await database.file_uploads.create_index("status")
        
        await database.subscriptions.create_index("user_id")
        await database.subscriptions.create_index("stripe_subscription_id", unique=True)
        await database.subscriptions.create_index("status")
        
        await database.email_providers.create_index("user_id")
        await database.email_providers.create_index("email_address")
        await database.email_providers.create_index("is_active")
        
        await database.email_tracking.create_index("user_id")
        await database.email_tracking.create_index("email_address")
        await database.email_tracking.create_index("status")
        await database.email_tracking.create_index("sent_at")
        await database.email_tracking.create_index("template_id")
        await database.email_tracking.create_index("campaign_id")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

def create_default_plans():
    """Create default plans in MongoDB."""
    try:
        existing_plans = sync_database.plans.count_documents({})
        if existing_plans > 0:
            logger.info("Plans already exist, skipping creation")
            return
        
        plans_to_insert = []
        for plan_data in DEFAULT_PLANS:
            plans_to_insert.append(plan_data)
        
        if plans_to_insert:
            result = sync_database.plans.insert_many(plans_to_insert)
            logger.info(f"Created {len(result.inserted_ids)} default plans")
        
    except Exception as e:
        logger.error(f"Error creating default plans: {e}")

async def init_database():
    """Initialize database with indexes and default data."""
    try:
        await create_indexes()
        
        create_default_plans()
        
        logger.info("Database initialization completed")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

async def check_database_connection():
    """Check if database connection is working."""
    try:
        await database.command("ping")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

