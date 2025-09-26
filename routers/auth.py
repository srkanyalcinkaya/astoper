from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase
from database import get_async_db
from schemas import UserCreate, UserLogin, User as UserSchema, Token
from auth import (
    verify_password, get_password_hash, create_access_token, 
    get_current_active_user, authenticate_user, get_user_by_email
)
from datetime import timedelta, datetime
from config import settings
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register")
async def register(user: UserCreate, db = Depends(get_async_db)):
    """Kullanıcı kayıt"""
    try:
        existing_user = await get_user_by_email(user.email, db)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bu email adresi zaten kullanılıyor"
            )
        
        free_plan = await db.plans.find_one({"name": "Free"})
        if not free_plan:
            free_plan = await db.plans.find_one({"name": "Ücretsiz"})
        plan_id = free_plan["_id"] if free_plan else None
        
        hashed_password = get_password_hash(user.password)
        new_user = {
            "email": user.email,
            "full_name": user.full_name,
            "hashed_password": hashed_password,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "plan_id": plan_id
        }
        
        result = await db.users.insert_one(new_user)
        
        created_user = await db.users.find_one({"_id": result.inserted_id})
        
        created_user["_id"] = str(created_user["_id"])
        if created_user.get("plan_id"):
            created_user["plan_id"] = str(created_user["plan_id"])
        
        created_user.pop("hashed_password", None)
        
        return {
            "id": created_user["_id"],
            "email": created_user["email"],
            "full_name": created_user.get("full_name"),
            "is_active": created_user["is_active"],
            "created_at": created_user["created_at"],
            "plan_id": created_user.get("plan_id")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kayıt sırasında bir hata oluştu"
        )

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db = Depends(get_async_db)):
    """Kullanıcı giriş"""
    try:
        user = await authenticate_user(user_credentials.email, user_credentials.password, db)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email veya şifre hatalı",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hesap deaktif"
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["_id"]}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "user": {
                "id": user["_id"],
                "email": user["email"],
                "username": user["username"],
                "full_name": user.get("full_name"),
                "is_active": user["is_active"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Giriş sırasında bir hata oluştu"
        )

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_active_user)):
    """Mevcut kullanıcı bilgilerini getir"""
    return {
        "id": current_user["_id"],
        "email": current_user["email"],
        "username": current_user["username"],
        "full_name": current_user.get("full_name"),
        "is_active": current_user["is_active"],
        "created_at": current_user["created_at"],
        "plan_id": current_user.get("plan_id")
    }

@router.post("/logout")
async def logout():
    """Kullanıcı çıkış (client-side token silme)"""
    return {"message": "Başarıyla çıkış yapıldı"}

