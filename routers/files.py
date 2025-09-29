from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from datetime import datetime
import jwt
import os
import shutil
import logging
from bson import ObjectId

from database import get_async_db
from models import FileUpload
from schemas import FileUploadResponse, EmailCategory
from config import settings
from file_processor import FileProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/files", tags=["files"])
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

@router.get("/", response_model=List[dict])
async def get_user_files(current_user: str = Depends(get_current_user)):
    """Get user's uploaded files"""
    db = await get_async_db()
    user_id = ObjectId(current_user)
    
    files_cursor = db.file_uploads.find({"user_id": user_id}).sort("upload_date", -1)
    files = await files_cursor.to_list(length=None)
    
    for file in files:
        file["_id"] = str(file["_id"])
        file["user_id"] = str(file["user_id"])
    
    return files

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    """Upload a file"""
    db = await get_async_db()
    user_id = ObjectId(current_user)
    
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    plan = None
    if user.get("plan_id"):
        plan = await db.plans.find_one({"_id": user["plan_id"]})
    
    # Plan limit kontrolü
    from plan_limit_service import PlanLimitService
    limit_service = PlanLimitService()
    
    if plan:
        file_limit_check = await limit_service.check_file_upload_limit(current_user, plan)
        if not file_limit_check["can_upload"]:
            raise HTTPException(
                status_code=400,
                detail=f"Dosya yükleme limitinize ulaştınız. Kullanılan: {file_limit_check['used']}/{file_limit_check['limit']}. Paketinizi yükseltebilirsiniz."
            )
    else:
        # Plan yoksa varsayılan limit (1 dosya)
        total_files = await db.file_uploads.count_documents({"user_id": user_id})
        if total_files >= 1:
            raise HTTPException(
                status_code=400,
                detail="Ücretsiz planınızda sadece 1 dosya yükleyebilirsiniz. Paket satın alarak limitinizi artırabilirsiniz."
            )
    
    allowed_types = [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # Excel
        "text/csv",
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"  # Word
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Desteklenmeyen dosya türü. Sadece Excel, CSV, PDF ve Word dosyaları kabul edilir."
        )
    
    max_file_size = plan["max_file_size_mb"] if plan else 5
    max_file_size_bytes = max_file_size * 1024 * 1024
    
    if file.size > max_file_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"Dosya boyutu çok büyük. Maksimum {max_file_size}MB kabul edilir."
        )
    
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(upload_dir, filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dosya kaydedilemedi: {str(e)}")
    
    file_data = {
        "user_id": user_id,
        "filename": file.filename,
        "file_path": file_path,
        "file_type": file.content_type,
        "file_size": file.size,
        "status": "uploaded",
        "upload_date": datetime.utcnow(),
        "processed_data": {}
    }
    
    result = await db.file_uploads.insert_one(file_data)
    file_id = str(result.inserted_id)
    
    await db.logs.insert_one({
        "user_id": user_id,
        "action": "file_uploaded",
        "details": f"Uploaded file: {file.filename} ({file.size} bytes)",
        "created_at": datetime.utcnow()
    })
    
    response_data = FileUploadResponse(
        id=file_id,
        filename=file.filename,
        file_path=file_path,
        file_size=file.size,
        file_type=file.content_type,
        message="Dosya başarıyla yüklendi"
    )
    
    # Frontend uyumluluğu için _id alanı ekle
    response_dict = response_data.model_dump()
    response_dict['_id'] = file_id
    
    logger.info(f"Dosya yükleme response: {response_dict}")
    
    return response_dict

@router.get("/{file_id}", response_model=dict)
async def get_file(
    file_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get specific file details"""
    db = await get_async_db()
    user_id = ObjectId(current_user)
    
    if not ObjectId.is_valid(file_id):
        raise HTTPException(status_code=400, detail="Invalid file ID")
    
    file = await db.file_uploads.find_one({
        "_id": ObjectId(file_id),
        "user_id": user_id
    })
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    file["_id"] = str(file["_id"])
    file["user_id"] = str(file["user_id"])
    
    return file

@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user: str = Depends(get_current_user)
):
    """Delete a file"""
    try:
        logger.info(f"Dosya silme isteği: file_id={file_id}, user_id={current_user}")
        
        db = await get_async_db()
        user_id = ObjectId(current_user)
        
        if not file_id or file_id == "undefined" or file_id == "null":
            logger.error(f"Geçersiz file_id: {file_id}")
            raise HTTPException(status_code=400, detail="Geçersiz dosya ID")
        
        if not ObjectId.is_valid(file_id):
            raise HTTPException(status_code=400, detail="Geçersiz dosya ID formatı")
        
        file = await db.file_uploads.find_one({
            "_id": ObjectId(file_id),
            "user_id": user_id
        })
        
        if not file:
            raise HTTPException(status_code=404, detail="Dosya bulunamadı")
        
        # Dosyayı dosya sisteminden sil
        try:
            if os.path.exists(file["file_path"]):
                os.remove(file["file_path"])
                logger.info(f"Dosya silindi: {file['file_path']}")
        except Exception as e:
            logger.error(f"Dosya silme hatası: {e}")
        
        # Veritabanından sil
        result = await db.file_uploads.delete_one({
            "_id": ObjectId(file_id),
            "user_id": user_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Dosya veritabanından silinemedi")
        
        await db.logs.insert_one({
            "user_id": user_id,
            "action": "file_deleted",
            "details": f"Deleted file: {file['filename']}",
            "created_at": datetime.utcnow()
        })
        
        return {"message": "Dosya başarıyla silindi"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dosya silme hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Dosya silinemedi: {str(e)}")

@router.get("/stats/summary", response_model=dict)
async def get_file_stats(current_user: str = Depends(get_current_user)):
    """Get user's file upload statistics"""
    db = await get_async_db()
    user_id = ObjectId(current_user)
    
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    
    total_files = await db.file_uploads.count_documents({"user_id": user_id})
    monthly_files = await db.file_uploads.count_documents({
        "user_id": user_id,
        "upload_date": {"$gte": month_start}
    })
    
    total_size = db.file_uploads.aggregate([
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": None, "total": {"$sum": "$file_size"}}}
    ])
    total_size_bytes = list(total_size)[0]["total"] if list(total_size) else 0
    
    file_types = db.file_uploads.aggregate([
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$file_type", "count": {"$sum": 1}}}
    ])
    
    return {
        "totalFiles": total_files,
        "filesThisMonth": monthly_files,
        "totalSizeBytes": total_size_bytes,
        "fileTypes": list(file_types)
    }

@router.post("/{file_id}/extract-emails", response_model=dict)
async def extract_emails_from_file(
    file_id: str,
    current_user: str = Depends(get_current_user)
):
    """Dosyadan email adreslerini çıkar"""
    try:
        db = await get_async_db()
        user_id = ObjectId(current_user)
        
        if not file_id or file_id == "undefined" or file_id == "null":
            raise HTTPException(status_code=400, detail="Geçersiz dosya ID")
        
        if not ObjectId.is_valid(file_id):
            raise HTTPException(status_code=400, detail="Geçersiz dosya ID formatı")
        
        file = await db.file_uploads.find_one({
            "_id": ObjectId(file_id),
            "user_id": user_id
        })
        
        if not file:
            raise HTTPException(status_code=404, detail="Dosya bulunamadı")
    
        # Dosya yolunu kontrol et
        if not os.path.exists(file["file_path"]):
            raise HTTPException(status_code=404, detail="Dosya dosya sisteminde bulunamadı")
        
        # Dosyayı işle
        extracted_data = FileProcessor.process_file_from_path(file["file_path"])
        
        if not extracted_data or not extracted_data.get("emails"):
            return {
                "emails": [],
                "message": "Dosyada email adresi bulunamadı",
                "total_found": 0
            }
        
        # Sadece email adreslerini döndür, AI kategorilendirme yok
        emails = []
        for email in extracted_data["emails"]:
            emails.append({
                "email": email,
                "category": "general",
                "confidence": 1.0,
                "website_url": None,
                "company_name": "",
                "industry": ""
            })
        
        await db.file_uploads.update_one(
            {"_id": ObjectId(file_id)},
            {"$set": {
                "processed_data": {
                    "emails_found": len(emails),
                    "categories": ["general"],
                    "extracted_at": datetime.utcnow()
                }
            }}
        )
        
        await db.logs.insert_one({
            "user_id": user_id,
            "action": "emails_extracted",
            "details": f"Dosyadan {len(emails)} email adresi çıkarıldı: {file['filename']}",
            "created_at": datetime.utcnow()
        })
        
        return {
            "emails": emails,
            "total_found": len(emails),
            "categories": ["general"],
            "file_info": {
                "filename": file["filename"],
                "file_type": file["file_type"],
                "upload_date": file["upload_date"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email çıkarma hatası: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Email çıkarma hatası: {str(e)}"
        )