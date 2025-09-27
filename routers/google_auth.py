from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from datetime import datetime, timedelta
import jwt
import requests
from bson import ObjectId

from database import get_async_db
from models import User
from config import settings

router = APIRouter(prefix="/auth/google", tags=["google-auth"])
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

class GoogleAuthService:
    """Google OAuth entegrasyonu için servis"""
    
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
    
    async def verify_google_token(self, token: str) -> dict:
        """Google token'ını doğrula ve kullanıcı bilgilerini al"""
        try:
            url = f"https://oauth2.googleapis.com/tokeninfo?access_token={token}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Geçersiz Google token")
            
            token_info = response.json()
            
            if token_info.get("aud") != self.client_id:
                raise HTTPException(status_code=401, detail="Geçersiz client ID")
            
            user_info_url = f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={token}"
            user_response = requests.get(user_info_url, timeout=10)
            
            if user_response.status_code != 200:
                raise HTTPException(status_code=401, detail="Kullanıcı bilgileri alınamadı")
            
            user_info = user_response.json()
            
            return {
                "google_id": user_info.get("id"),
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "picture": user_info.get("picture"),
                "verified_email": user_info.get("verified_email", False)
            }
            
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Google API hatası: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Token doğrulama hatası: {str(e)}")

@router.post("/login")
async def google_login(request: dict):
    """Google ile giriş yap"""
    google_token = request.get("token")
    
    if not google_token:
        raise HTTPException(status_code=400, detail="Google token gerekli")
    
    try:
        google_service = GoogleAuthService()
        google_user = await google_service.verify_google_token(google_token)
        
        if not google_user.get("verified_email"):
            raise HTTPException(status_code=400, detail="Email adresi doğrulanmamış")
        
        db = await get_async_db()
        
        user = await db.users.find_one({"email": google_user["email"]})
        
        if user:
            await db.users.update_one(
                {"_id": user["_id"]},
                {"$set": {
                    "google_id": google_user["google_id"],
                    "google_picture": google_user["picture"],
                    "username": google_user["email"].split("@")[0],
                    "full_name": google_user["name"],
                    "last_login": datetime.utcnow()
                }}
            )
        else:
            user_data = {
                "email": google_user["email"],
                "username": google_user["email"].split("@")[0],
                "full_name": google_user["name"],
                "hashed_password": "",  # Google ile giriş yapan kullanıcılar için şifre yok
                "is_active": True,
                "google_id": google_user["google_id"],
                "google_picture": google_user["picture"],
                "created_at": datetime.utcnow(),
                "last_login": datetime.utcnow()
            }
            
            result = await db.users.insert_one(user_data)
            user = await db.users.find_one({"_id": result.inserted_id})
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = jwt.encode(
            {
                "sub": str(user["_id"]),
                "exp": datetime.utcnow() + access_token_expires,
                "email": user["email"],
                "login_method": "google"
            },
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        await db.logs.insert_one({
            "user_id": user["_id"],
            "action": "google_login",
            "details": f"Google ile giriş yapıldı: {user['email']}",
            "created_at": datetime.utcnow()
        })
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user["_id"]),
                "email": user["email"],
                "username": user.get("username", user["email"].split("@")[0]),
                "full_name": user.get("full_name"),
                "picture": user.get("google_picture"),
                "is_active": user["is_active"],
                "plan_id": str(user.get("plan_id", "")) if user.get("plan_id") else None
            },
            "message": "Google ile başarıyla giriş yapıldı"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google giriş hatası: {str(e)}")

@router.get("/callback")
async def google_callback(request: Request):
    """Google OAuth callback endpoint"""
    return {
        "message": "Google OAuth callback endpoint",
        "note": "Frontend'den Google OAuth flow'u tamamlandıktan sonra /auth/google/login endpoint'ini kullanın"
    }

@router.post("/link-account")
async def link_google_account(
    request: dict,
    current_user: str = Depends(get_current_user)
):
    """Mevcut hesabı Google hesabı ile bağla"""
    google_token = request.get("token")
    
    if not google_token:
        raise HTTPException(status_code=400, detail="Google token gerekli")
    
    try:
        google_service = GoogleAuthService()
        google_user = await google_service.verify_google_token(google_token)
        
        db = await get_async_db()
        user_id = ObjectId(current_user)
        
        user = await db.users.find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
        
        await db.users.update_one(
            {"_id": user_id},
            {"$set": {
                "google_id": google_user["google_id"],
                "google_picture": google_user["picture"],
                "updated_at": datetime.utcnow()
            }}
        )
        
        await db.logs.insert_one({
            "user_id": user_id,
            "action": "google_account_linked",
            "details": f"Google hesabı bağlandı: {google_user['email']}",
            "created_at": datetime.utcnow()
        })
        
        return {
            "message": "Google hesabı başarıyla bağlandı",
            "google_email": google_user["email"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hesap bağlama hatası: {str(e)}")
