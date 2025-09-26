from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase
from database import get_async_db, get_users_collection
from schemas import TokenData, User
from models import User as UserModel
from config import settings
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Şifre doğrulama"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Şifre hashleme"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """JWT token oluşturma"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    """Token doğrulama"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(email=user_id)  # user_id'yi email field'ında saklıyoruz
    except JWTError:
        raise credentials_exception
    return token_data

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_async_db)
) -> dict:
    """Mevcut kullanıcıyı getir"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token doğrulanamadı",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    token_data = verify_token(token, credentials_exception)
    
    try:
        user = await db.users.find_one({"_id": ObjectId(token_data.email)})
        if user is None:
            raise credentials_exception
        
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hesap deaktif"
            )
        
        user["_id"] = str(user["_id"])
        if user.get("plan_id"):
            user["plan_id"] = str(user["plan_id"])
        
        return user
        
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise credentials_exception

async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Aktif kullanıcıyı getir"""
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hesap deaktif"
        )
    return current_user

async def authenticate_user(email: str, password: str, db: AsyncIOMotorDatabase) -> Optional[dict]:
    """Kullanıcı doğrulama"""
    try:
        user = await db.users.find_one({"email": email})
        if not user:
            return None
        
        if not verify_password(password, user["hashed_password"]):
            return None
        
        user["_id"] = str(user["_id"])
        if user.get("plan_id"):
            user["plan_id"] = str(user["plan_id"])
        
        return user
        
    except Exception as e:
        logger.error(f"Error authenticating user: {e}")
        return None

async def get_user_by_email(email: str, db: AsyncIOMotorDatabase) -> Optional[dict]:
    """Email ile kullanıcı bul"""
    try:
        user = await db.users.find_one({"email": email})
        if user:
            user["_id"] = str(user["_id"])
            if user.get("plan_id"):
                user["plan_id"] = str(user["plan_id"])
        return user
    except Exception as e:
        logger.error(f"Error getting user by email: {e}")
        return None


