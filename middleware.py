from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db, User, Plan, Query, Log
from datetime import datetime, timedelta
from typing import Optional
import json

class PlanLimiter:
    """Plan limitlerini kontrol eden sınıf"""
    
    @staticmethod
    def check_query_limit(user: User, db: Session) -> bool:
        """Sorgu limitini kontrol et"""
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        queries_this_month = db.query(Query).filter(
            Query.user_id == user.id,
            Query.created_at >= month_start
        ).count()
        
        if user.plan.max_queries_per_month == -1:  # Unlimited
            return True
        
        return queries_this_month < user.plan.max_queries_per_month
    
    @staticmethod
    def check_file_upload_limit(user: User, db: Session) -> bool:
        """Dosya yükleme limitini kontrol et"""
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        files_this_month = db.query(Query).filter(
            Query.user_id == user.id,
            Query.created_at >= month_start,
            Query.file_path.isnot(None)
        ).count()
        
        if user.plan.max_file_uploads == -1:  # Unlimited
            return True
        
        return files_this_month < user.plan.max_file_uploads
    
    @staticmethod
    def get_usage_stats(user: User, db: Session) -> dict:
        """Kullanım istatistiklerini getir"""
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        queries_this_month = db.query(Query).filter(
            Query.user_id == user.id,
            Query.created_at >= month_start
        ).count()
        
        files_this_month = db.query(Query).filter(
            Query.user_id == user.id,
            Query.created_at >= month_start,
            Query.file_path.isnot(None)
        ).count()
        
        total_emails = db.query(Query).filter(Query.user_id == user.id).with_entities(
            db.func.sum(Query.emails_sent)
        ).scalar() or 0
        
        return {
            "queries_this_month": queries_this_month,
            "queries_limit": user.plan.max_queries_per_month,
            "files_this_month": files_this_month,
            "files_limit": user.plan.max_file_uploads,
            "total_emails_sent": total_emails,
            "plan_name": user.plan.name,
            "plan_price": user.plan.price
        }

def require_plan_feature(feature: str):
    """Plan özellik kontrolü decorator'ı"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            user = None
            for arg in args:
                if isinstance(arg, User):
                    user = arg
                    break
            
            if not user:
                for key, value in kwargs.items():
                    if isinstance(value, User):
                        user = value
                        break
            
            if not user:
                raise HTTPException(status_code=500, detail="User bilgisi bulunamadı")
            
            if feature == "file_upload" and user.plan.max_file_uploads == 0:
                raise HTTPException(
                    status_code=403, 
                    detail="Dosya yükleme özelliği mevcut planınızda bulunmuyor. Plan yükseltin."
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def log_user_activity(action: str, details: str = None):
    """Kullanıcı aktivitesini logla"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            user = None
            db = None
            request = None
            
            for arg in args:
                if isinstance(arg, User):
                    user = arg
                elif isinstance(arg, Session):
                    db = arg
                elif hasattr(arg, 'client') and hasattr(arg, 'url'):  # Request object
                    request = arg
            
            if not user or not db:
                for key, value in kwargs.items():
                    if isinstance(value, User):
                        user = value
                    elif isinstance(value, Session):
                        db = value
                    elif hasattr(value, 'client') and hasattr(value, 'url'):
                        request = value
            
            if user and db:
                log = Log(
                    user_id=user.id,
                    action=action,
                    details=details or f"{func.__name__} endpoint çağrıldı",
                    ip_address=request.client.host if request else None,
                    user_agent=request.headers.get("user-agent") if request else None
                )
                db.add(log)
                db.commit()
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

