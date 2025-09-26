from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
import jwt
import bcrypt
from bson import ObjectId
import logging

from database import get_async_db
from schemas import UserCreate as UserCreateSchema, UserLogin as UserLoginSchema, Token
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using bcrypt"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/register", response_model=dict)
async def register(user: UserCreate):
    """Kullanıcı kayıt"""
    try:
        db = await get_async_db()
        
        existing_user = await db.users.find_one({
            "$or": [
                {"email": user.email},
                {"username": user.username}
            ]
        })
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bu email veya kullanıcı adı zaten kullanılıyor"
            )
        
        hashed_password = hash_password(user.password)
        
        user_data = {
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "hashed_password": hashed_password,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "plan_id": None
        }
        
        result = await db.users.insert_one(user_data)
        user_id = str(result.inserted_id)
        
        access_token = create_access_token(data={"sub": user_id})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": True,
                "created_at": user_data["created_at"].isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kayıt sırasında bir hata oluştu"
        )

@router.post("/login", response_model=dict)
async def login(user_credentials: UserLogin):
    """Kullanıcı giriş"""
    try:
        db = await get_async_db()
        
        user = await db.users.find_one({
            "$or": [
                {"username": user_credentials.username},
                {"email": user_credentials.username}
            ]
        })
        
        if not user or not verify_password(user_credentials.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Kullanıcı adı veya şifre hatalı"
            )
        
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Hesap deaktif edilmiş"
            )
        
        user_id = str(user["_id"])
        access_token = create_access_token(data={"sub": user_id})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "username": user["username"],
                "email": user["email"],
                "full_name": user.get("full_name"),
                "is_active": user["is_active"],
                "created_at": user["created_at"].isoformat()
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

@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: str = Depends(get_current_user)):
    """Mevcut kullanıcı bilgilerini getir"""
    try:
        db = await get_async_db()
        user_id = ObjectId(current_user)
        
        user = await db.users.find_one({"_id": user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kullanıcı bulunamadı"
            )
        
        return {
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"],
            "full_name": user.get("full_name"),
            "is_active": user["is_active"],
            "created_at": user["created_at"].isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kullanıcı bilgileri alınamadı"
        )

@router.post("/logout")
async def logout():
    """Kullanıcı çıkış"""
    return {"message": "Başarıyla çıkış yapıldı"}
