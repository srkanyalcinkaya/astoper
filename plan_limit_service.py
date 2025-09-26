import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from bson import ObjectId

logger = logging.getLogger(__name__)

class PlanLimitService:
    """Plan limitlerini kontrol eden servis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def check_email_limit(self, user_id: str, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Kullanıcının email gönderim limitini kontrol et"""
        try:
            from database import get_async_db
            db = await get_async_db()
            
            max_emails_per_month = plan_data.get("max_emails_per_month", 0)
            
            if max_emails_per_month == -1:  # Sınırsız
                return {
                    "can_send": True,
                    "remaining": -1,
                    "used": 0,
                    "limit": -1
                }
            
            start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_of_month = start_of_month + timedelta(days=32)
            end_of_month = end_of_month.replace(day=1) - timedelta(days=1)
            
            emails_sent_this_month = await db.email_tracking.count_documents({
                "user_id": ObjectId(user_id),
                "sent_at": {
                    "$gte": start_of_month,
                    "$lte": end_of_month
                },
                "status": {"$in": ["sent", "delivered", "opened", "clicked"]}
            })
            
            remaining = max_emails_per_month - emails_sent_this_month
            can_send = remaining > 0
            
            return {
                "can_send": can_send,
                "remaining": max(0, remaining),
                "used": emails_sent_this_month,
                "limit": max_emails_per_month
            }
            
        except Exception as e:
            self.logger.error(f"Email limit kontrolü hatası: {e}")
            return {
                "can_send": False,
                "remaining": 0,
                "used": 0,
                "limit": 0
            }
    
    async def check_template_limit(self, user_id: str, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Kullanıcının şablon limitini kontrol et"""
        try:
            from database import get_async_db
            db = await get_async_db()
            
            max_templates = plan_data.get("max_templates", 1)
            
            if max_templates == -1:  # Sınırsız
                return {
                    "can_create": True,
                    "remaining": -1,
                    "used": 0,
                    "limit": -1
                }
            
            templates_count = await db.email_templates.count_documents({
                "user_id": ObjectId(user_id)
            })
            
            remaining = max_templates - templates_count
            can_create = remaining > 0
            
            return {
                "can_create": can_create,
                "remaining": max(0, remaining),
                "used": templates_count,
                "limit": max_templates
            }
            
        except Exception as e:
            self.logger.error(f"Şablon limit kontrolü hatası: {e}")
            return {
                "can_create": False,
                "remaining": 0,
                "used": 0,
                "limit": 0
            }
    
    async def check_query_limit(self, user_id: str, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Kullanıcının sorgu limitini kontrol et"""
        try:
            from database import get_async_db
            db = await get_async_db()
            
            max_queries_per_month = plan_data.get("max_queries_per_month", 0)
            
            if max_queries_per_month == -1:  # Sınırsız
                return {
                    "can_query": True,
                    "remaining": -1,
                    "used": 0,
                    "limit": -1
                }
            
            start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_of_month = start_of_month + timedelta(days=32)
            end_of_month = end_of_month.replace(day=1) - timedelta(days=1)
            
            queries_this_month = await db.queries.count_documents({
                "user_id": ObjectId(user_id),
                "created_at": {
                    "$gte": start_of_month,
                    "$lte": end_of_month
                }
            })
            
            remaining = max_queries_per_month - queries_this_month
            can_query = remaining > 0
            
            return {
                "can_query": can_query,
                "remaining": max(0, remaining),
                "used": queries_this_month,
                "limit": max_queries_per_month
            }
            
        except Exception as e:
            self.logger.error(f"Sorgu limit kontrolü hatası: {e}")
            return {
                "can_query": False,
                "remaining": 0,
                "used": 0,
                "limit": 0
            }
    
    async def check_file_upload_limit(self, user_id: str, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Kullanıcının dosya yükleme limitini kontrol et"""
        try:
            from database import get_async_db
            db = await get_async_db()
            
            max_file_uploads = plan_data.get("max_file_uploads", 0)
            
            if max_file_uploads == -1:  # Sınırsız
                return {
                    "can_upload": True,
                    "remaining": -1,
                    "used": 0,
                    "limit": -1
                }
            
            files_count = await db.file_uploads.count_documents({
                "user_id": ObjectId(user_id)
            })
            
            remaining = max_file_uploads - files_count
            can_upload = remaining > 0
            
            return {
                "can_upload": can_upload,
                "remaining": max(0, remaining),
                "used": files_count,
                "limit": max_file_uploads
            }
            
        except Exception as e:
            self.logger.error(f"Dosya yükleme limit kontrolü hatası: {e}")
            return {
                "can_upload": False,
                "remaining": 0,
                "used": 0,
                "limit": 0
            }
    
    async def get_all_limits(self, user_id: str, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tüm limitleri kontrol et"""
        try:
            email_limit = await self.check_email_limit(user_id, plan_data)
            template_limit = await self.check_template_limit(user_id, plan_data)
            query_limit = await self.check_query_limit(user_id, plan_data)
            file_limit = await self.check_file_upload_limit(user_id, plan_data)
            
            return {
                "email_limit": email_limit,
                "template_limit": template_limit,
                "query_limit": query_limit,
                "file_limit": file_limit,
                "plan_name": plan_data.get("name", "Unknown"),
                "plan_price": plan_data.get("price", 0)
            }
            
        except Exception as e:
            self.logger.error(f"Limit kontrolü hatası: {e}")
            return {
                "email_limit": {"can_send": False, "remaining": 0, "used": 0, "limit": 0},
                "template_limit": {"can_create": False, "remaining": 0, "used": 0, "limit": 0},
                "query_limit": {"can_query": False, "remaining": 0, "used": 0, "limit": 0},
                "file_limit": {"can_upload": False, "remaining": 0, "used": 0, "limit": 0},
                "plan_name": "Unknown",
                "plan_price": 0
            }
