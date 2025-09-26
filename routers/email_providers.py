from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import List, Optional
from datetime import datetime
import jwt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bson import ObjectId
import logging

from database import get_async_db
from models import EmailProvider, EmailProviderCreate, EmailProviderUpdate, EmailProviderResponse, SMTPConfig
from config import settings
from cryptography.fernet import Fernet
import base64
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/email-providers", tags=["email-providers"])
security = HTTPBearer()

def get_encryption_key():
    """Şifreleme anahtarı al"""
    key = os.getenv("ENCRYPTION_KEY", "your-32-byte-encryption-key-here!!")
    return base64.urlsafe_b64encode(key.encode()[:32].ljust(32, b'0'))

def encrypt_password(password: str) -> str:
    """Şifreyi şifrele"""
    key = get_encryption_key()
    fernet = Fernet(key)
    encrypted_password = fernet.encrypt(password.encode())
    return base64.urlsafe_b64encode(encrypted_password).decode()

def decrypt_password(encrypted_password: str) -> str:
    """Şifreyi çöz"""
    key = get_encryption_key()
    fernet = Fernet(key)
    encrypted_bytes = base64.urlsafe_b64decode(encrypted_password.encode())
    decrypted_password = fernet.decrypt(encrypted_bytes)
    return decrypted_password.decode()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Mevcut kullanıcıyı JWT token'dan al"""
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/", response_model=List[EmailProviderResponse])
async def get_email_providers(current_user: str = Depends(get_current_user)):
    """Kullanıcının email provider'larını listele"""
    try:
        db = await get_async_db()
        user_id = ObjectId(current_user)
        
        providers_cursor = db.email_providers.find({"user_id": user_id})
        providers = await providers_cursor.to_list(length=None)
        
        result = []
        for provider in providers:
            result.append(EmailProviderResponse(
                id=str(provider["_id"]),
                provider_name=provider["provider_name"],
                email_address=provider["email_address"],
                is_active=provider["is_active"],
                is_verified=provider["is_verified"],
                last_used=provider.get("last_used"),
                created_at=provider["created_at"]
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting email providers: {e}")
        raise HTTPException(status_code=500, detail="Email provider'lar alınamadı")

@router.post("/", response_model=EmailProviderResponse)
async def create_email_provider(
    provider_data: EmailProviderCreate,
    current_user: str = Depends(get_current_user)
):
    """Yeni email provider oluştur"""
    try:
        db = await get_async_db()
        user_id = ObjectId(current_user)
        
        existing = await db.email_providers.find_one({
            "user_id": user_id,
            "email_address": provider_data.email_address
        })
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Bu email adresi zaten kayıtlı"
            )
        
        encrypted_smtp_config = None
        if provider_data.smtp_config:
            encrypted_smtp_config = provider_data.smtp_config.dict()
            encrypted_smtp_config["password"] = encrypt_password(provider_data.smtp_config.password)
        
        new_provider = {
            "user_id": user_id,
            "provider_name": provider_data.provider_name,
            "email_address": provider_data.email_address,
            "smtp_config": encrypted_smtp_config,
            "is_active": True,
            "is_verified": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.email_providers.insert_one(new_provider)
        created_provider = await db.email_providers.find_one({"_id": result.inserted_id})
        
        return EmailProviderResponse(
            id=str(created_provider["_id"]),
            provider_name=created_provider["provider_name"],
            email_address=created_provider["email_address"],
            is_active=created_provider["is_active"],
            is_verified=created_provider["is_verified"],
            last_used=created_provider.get("last_used"),
            created_at=created_provider["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating email provider: {e}")
        raise HTTPException(status_code=500, detail="Email provider oluşturulamadı")

@router.post("/{provider_id}/test")
async def test_email_provider(
    provider_id: str,
    current_user: str = Depends(get_current_user)
):
    """Email provider'ı test et"""
    try:
        db = await get_async_db()
        user_id = ObjectId(current_user)
        
        provider = await db.email_providers.find_one({
            "_id": ObjectId(provider_id),
            "user_id": user_id
        })
        
        if not provider:
            raise HTTPException(status_code=404, detail="Email provider bulunamadı")
        
        if not provider.get("smtp_config"):
            raise HTTPException(status_code=400, detail="SMTP konfigürasyonu bulunamadı")
        
        smtp_config = provider["smtp_config"].copy()
        smtp_config["password"] = decrypt_password(smtp_config["password"])
        
        try:
            if smtp_config["host"] == "smtp.gmail.com":
                server = smtplib.SMTP(smtp_config["host"], smtp_config["port"])
                server.starttls()
            elif smtp_config["use_ssl"]:
                server = smtplib.SMTP_SSL(smtp_config["host"], smtp_config["port"])
            else:
                server = smtplib.SMTP(smtp_config["host"], smtp_config["port"])
                if smtp_config["use_tls"]:
                    server.starttls()
            
            server.login(smtp_config["username"], smtp_config["password"])
            
            msg = MIMEMultipart()
            msg['From'] = provider["email_address"]
            msg['To'] = provider["email_address"]
            msg['Subject'] = "Email Provider Test - Astoper Platform"
            
            body = """
            Bu bir test email'idir.
            
            Astoper Platform'dan gönderildi.
            
            Bu email'i aldıysanız, email provider konfigürasyonunuz başarılı!
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            text = msg.as_string()
            server.sendmail(provider["email_address"], provider["email_address"], text)
            server.quit()
            
            await db.email_providers.update_one(
                {"_id": ObjectId(provider_id)},
                {
                    "$set": {
                        "is_verified": True,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return {
                "success": True,
                "message": "Test email başarıyla gönderildi",
                "verified": True
            }
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return {
                "success": False,
                "message": f"Email gönderilemedi: {str(e)}",
                "verified": False
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing email provider: {e}")
        raise HTTPException(status_code=500, detail="Email provider test edilemedi")

@router.put("/{provider_id}", response_model=EmailProviderResponse)
async def update_email_provider(
    provider_id: str,
    provider_update: EmailProviderUpdate,
    current_user: str = Depends(get_current_user)
):
    """Email provider güncelle"""
    try:
        db = await get_async_db()
        user_id = ObjectId(current_user)
        
        provider = await db.email_providers.find_one({
            "_id": ObjectId(provider_id),
            "user_id": user_id
        })
        
        if not provider:
            raise HTTPException(status_code=404, detail="Email provider bulunamadı")
        
        update_data = {
            "updated_at": datetime.utcnow()
        }
        
        if provider_update.is_active is not None:
            update_data["is_active"] = provider_update.is_active
        
        if provider_update.smtp_config:
            encrypted_smtp_config = provider_update.smtp_config.dict()
            encrypted_smtp_config["password"] = encrypt_password(provider_update.smtp_config.password)
            update_data["smtp_config"] = encrypted_smtp_config
            update_data["is_verified"] = False  # SMTP değiştiği için tekrar doğrula
        
        await db.email_providers.update_one(
            {"_id": ObjectId(provider_id)},
            {"$set": update_data}
        )
        
        updated_provider = await db.email_providers.find_one({"_id": ObjectId(provider_id)})
        
        return EmailProviderResponse(
            id=str(updated_provider["_id"]),
            provider_name=updated_provider["provider_name"],
            email_address=updated_provider["email_address"],
            is_active=updated_provider["is_active"],
            is_verified=updated_provider["is_verified"],
            last_used=updated_provider.get("last_used"),
            created_at=updated_provider["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating email provider: {e}")
        raise HTTPException(status_code=500, detail="Email provider güncellenemedi")

@router.delete("/{provider_id}")
async def delete_email_provider(
    provider_id: str,
    current_user: str = Depends(get_current_user)
):
    """Email provider sil"""
    try:
        db = await get_async_db()
        user_id = ObjectId(current_user)
        
        result = await db.email_providers.delete_one({
            "_id": ObjectId(provider_id),
            "user_id": user_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Email provider bulunamadı")
        
        return {"message": "Email provider başarıyla silindi"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting email provider: {e}")
        raise HTTPException(status_code=500, detail="Email provider silinemedi")

@router.get("/providers/info")
async def get_provider_info():
    """Desteklenen email provider'lar hakkında bilgi"""
    return {
        "supported_providers": [
            {
                "name": "gmail",
                "display_name": "Gmail",
                "auth_method": "OAuth2 (Önerilen) veya App Password",
                "smtp_host": "smtp.gmail.com",
                "smtp_port": 587,
                "instructions": "Gmail için App Password kullanmanız önerilir. 2FA aktif olmalıdır."
            },
            {
                "name": "outlook",
                "display_name": "Outlook/Hotmail",
                "auth_method": "OAuth2 (Önerilen) veya SMTP",
                "smtp_host": "smtp-mail.outlook.com",
                "smtp_port": 587,
                "instructions": "Outlook için modern authentication kullanın."
            },
            {
                "name": "yahoo",
                "display_name": "Yahoo Mail",
                "auth_method": "App Password",
                "smtp_host": "smtp.mail.yahoo.com",
                "smtp_port": 587,
                "instructions": "Yahoo için App Password gerekir."
            },
            {
                "name": "custom",
                "display_name": "Özel SMTP",
                "auth_method": "SMTP",
                "instructions": "Kendi SMTP sunucunuzun bilgilerini girin."
            }
        ]
    }
