from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from datetime import datetime
import jwt
from bson import ObjectId
import google.generativeai as genai
import os
import uuid

from database import get_async_db
from schemas import (
    EmailTemplate, EmailTemplateCreate, EmailTemplateUpdate,
    AITemplateRequest, AITemplateResponse
)
from config import settings

router = APIRouter(prefix="/templates", tags=["templates"])
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
async def get_user_templates(current_user: str = Depends(get_current_user)):
    """Kullanıcının email şablonlarını getir"""
    db = await get_async_db()
    user_id = ObjectId(current_user)
    
    templates_cursor = db.email_templates.find({"user_id": user_id, "is_active": True}).sort("created_at", -1)
    templates = await templates_cursor.to_list(length=None)
    
    for template in templates:
        template["_id"] = str(template["_id"])
        template["user_id"] = str(template["user_id"])
    
    return templates

@router.get("/default")
async def get_default_templates():
    """Varsayılan email şablonlarını getir"""
    default_templates = [
        {
            "_id": "default_1",
            "name": "Web Tasarım Teklifi",
            "subject": "Profesyonel Web Tasarım Hizmetlerimiz",
            "category": "web_design",
            "content": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0; font-size: 24px;">{{company_name}}</h1>
        <p style="color: #f0f0f0; margin: 10px 0 0 0;">{{company_tagline}}</p>
    </div>
    
    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
        <h2 style="color: #333; margin-top: 0;">Merhaba!</h2>
        <p>{{greeting_message}}</p>
    </div>
    
    <div style="margin-bottom: 20px;">
        <h3 style="color: #667eea;">Hizmetlerimiz:</h3>
        <ul style="list-style: none; padding: 0;">
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">✓ {{service_1}}</li>
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">✓ {{service_2}}</li>
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">✓ {{service_3}}</li>
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">✓ {{service_4}}</li>
        </ul>
    </div>
    
    <div style="background: #e8f4f8; padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0;">
        <p style="margin: 0; font-weight: bold; color: #2c5aa0;">{{offer_title}}</p>
        <p style="margin: 5px 0 0 0; font-size: 14px;">{{offer_description}}</p>
    </div>
    
    <div style="text-align: center; margin: 30px 0;">
        <a href="{{website_url}}" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Web Sitemizi İnceleyin</a>
    </div>
    
    <div style="border-top: 1px solid #eee; padding-top: 20px; text-align: center; color: #666; font-size: 12px;">
        <p><strong>{{company_name}}</strong><br>
        📧 {{email}} | 📞 {{phone}}<br>
        🌐 {{website_url}}</p>
    </div>
</body>
</html>
            """,
            "is_ai_generated": False,
            "template_fields": [
                {"name": "company_name", "label": "Şirket Adı", "type": "text", "required": True, "default": "Şirket Adınız"},
                {"name": "company_tagline", "label": "Şirket Sloganı", "type": "text", "required": False, "default": "Dijital Dönüşüm Partneriniz"},
                {"name": "greeting_message", "label": "Karşılama Mesajı", "type": "textarea", "required": True, "default": "Şirketinizin dijital varlığını güçlendirmek için profesyonel web tasarım hizmetlerimizi sunuyoruz."},
                {"name": "service_1", "label": "Hizmet 1", "type": "text", "required": True, "default": "Modern ve responsive web tasarımı"},
                {"name": "service_2", "label": "Hizmet 2", "type": "text", "required": True, "default": "SEO optimizasyonu"},
                {"name": "service_3", "label": "Hizmet 3", "type": "text", "required": True, "default": "E-ticaret çözümleri"},
                {"name": "service_4", "label": "Hizmet 4", "type": "text", "required": True, "default": "Web sitesi bakım ve güncelleme"},
                {"name": "offer_title", "label": "Teklif Başlığı", "type": "text", "required": True, "default": "Ücretsiz Danışmanlık"},
                {"name": "offer_description", "label": "Teklif Açıklaması", "type": "textarea", "required": True, "default": "Projeniz için detaylı analiz ve teklif sunuyoruz"},
                {"name": "email", "label": "Email Adresi", "type": "email", "required": True, "default": "info@example.com"},
                {"name": "phone", "label": "Telefon", "type": "text", "required": True, "default": "+90 XXX XXX XX XX"},
                {"name": "website_url", "label": "Website URL", "type": "url", "required": True, "default": "https://www.example.com"}
            ]
        },
        {
            "_id": "default_2", 
            "name": "SEO Optimizasyon Teklifi",
            "subject": "Web Sitenizin Arama Motorlarında Görünürlüğünü Artıralım",
            "category": "seo",
            "content": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0; font-size: 24px;">{{company_name}} - SEO Uzmanları</h1>
        <p style="color: #f0f0f0; margin: 10px 0 0 0;">{{company_tagline}}</p>
    </div>
    
    <div style="background: #fff3cd; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #ffc107;">
        <h2 style="color: #856404; margin-top: 0;">⚠️ {{problem_title}}</h2>
        <p style="color: #856404; margin: 0;">{{problem_description}}</p>
    </div>
    
    <div style="margin-bottom: 20px;">
        <h3 style="color: #4facfe;">SEO Hizmetlerimiz:</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                <h4 style="margin: 0 0 10px 0; color: #333;">{{service_category_1}}</h4>
                <ul style="margin: 0; padding-left: 15px; font-size: 14px;">
                    <li>{{service_1}}</li>
                    <li>{{service_2}}</li>
                    <li>{{service_3}}</li>
                </ul>
            </div>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                <h4 style="margin: 0 0 10px 0; color: #333;">{{service_category_2}}</h4>
                <ul style="margin: 0; padding-left: 15px; font-size: 14px;">
                    <li>{{service_4}}</li>
                    <li>{{service_5}}</li>
                    <li>{{service_6}}</li>
                </ul>
            </div>
        </div>
    </div>
    
    <div style="background: #d4edda; padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0; border: 1px solid #c3e6cb;">
        <p style="margin: 0; font-weight: bold; color: #155724;">📊 {{offer_title}}</p>
        <p style="margin: 5px 0 0 0; font-size: 14px; color: #155724;">{{offer_description}}</p>
    </div>
    
    <div style="text-align: center; margin: 30px 0;">
        <a href="{{website_url}}" style="background: #4facfe; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Hemen İletişime Geçin</a>
    </div>
    
    <div style="border-top: 1px solid #eee; padding-top: 20px; text-align: center; color: #666; font-size: 12px;">
        <p><strong>{{company_name}} - SEO Uzmanları</strong><br>
        📧 {{email}} | 📞 {{phone}}<br>
        🌐 {{website_url}}</p>
    </div>
</body>
</html>
            """,
            "is_ai_generated": False,
            "template_fields": [
                {"name": "company_name", "label": "Şirket Adı", "type": "text", "required": True, "default": "Şirket Adınız"},
                {"name": "company_tagline", "label": "Şirket Sloganı", "type": "text", "required": False, "default": "SEO Uzmanları"},
                {"name": "problem_title", "label": "Problem Başlığı", "type": "text", "required": True, "default": "Web Siteniz Görünmüyor mu?"},
                {"name": "problem_description", "label": "Problem Açıklaması", "type": "textarea", "required": True, "default": "Müşterileriniz sizi Google'da bulamıyor olabilir. Bu büyük bir fırsat kaybı!"},
                {"name": "service_category_1", "label": "Hizmet Kategorisi 1", "type": "text", "required": True, "default": "Teknik SEO"},
                {"name": "service_1", "label": "Hizmet 1", "type": "text", "required": True, "default": "Site hızı optimizasyonu"},
                {"name": "service_2", "label": "Hizmet 2", "type": "text", "required": True, "default": "Mobil uyumluluk"},
                {"name": "service_3", "label": "Hizmet 3", "type": "text", "required": True, "default": "Meta tag optimizasyonu"},
                {"name": "service_category_2", "label": "Hizmet Kategorisi 2", "type": "text", "required": True, "default": "İçerik SEO"},
                {"name": "service_4", "label": "Hizmet 4", "type": "text", "required": True, "default": "Anahtar kelime analizi"},
                {"name": "service_5", "label": "Hizmet 5", "type": "text", "required": True, "default": "İçerik optimizasyonu"},
                {"name": "service_6", "label": "Hizmet 6", "type": "text", "required": True, "default": "Blog yazıları"},
                {"name": "offer_title", "label": "Teklif Başlığı", "type": "text", "required": True, "default": "Ücretsiz SEO Analizi"},
                {"name": "offer_description", "label": "Teklif Açıklaması", "type": "textarea", "required": True, "default": "Web sitenizin mevcut SEO durumunu analiz edelim"},
                {"name": "email", "label": "Email Adresi", "type": "email", "required": True, "default": "info@example.com"},
                {"name": "phone", "label": "Telefon", "type": "text", "required": True, "default": "+90 XXX XXX XX XX"},
                {"name": "website_url", "label": "Website URL", "type": "url", "required": True, "default": "https://www.example.com"}
            ]
        },
        {
            "_id": "default_3",
            "name": "E-ticaret Çözümleri",
            "subject": "Online Satışlarınızı Artırmak İçin E-ticaret Çözümlerimiz",
            "category": "ecommerce", 
            "content": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0; font-size: 24px;">{{company_name}} - E-ticaret Uzmanları</h1>
        <p style="color: #f0f0f0; margin: 10px 0 0 0;">{{company_tagline}}</p>
    </div>
    
    <div style="background: #fff; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <h2 style="color: #333; margin-top: 0;">🚀 {{headline}}</h2>
        <p>{{description}}</p>
    </div>
    
    <div style="margin-bottom: 20px;">
        <h3 style="color: #fa709a;">E-ticaret Çözümlerimiz:</h3>
        <div style="display: grid; grid-template-columns: 1fr; gap: 15px;">
            <div style="background: linear-gradient(90deg, #fa709a, #fee140); color: white; padding: 15px; border-radius: 8px;">
                <h4 style="margin: 0 0 10px 0;">🛒 {{solution_1_title}}</h4>
                <p style="margin: 0; font-size: 14px;">{{solution_1_description}}</p>
            </div>
            <div style="background: linear-gradient(90deg, #fa709a, #fee140); color: white; padding: 15px; border-radius: 8px;">
                <h4 style="margin: 0 0 10px 0;">📱 {{solution_2_title}}</h4>
                <p style="margin: 0; font-size: 14px;">{{solution_2_description}}</p>
            </div>
            <div style="background: linear-gradient(90deg, #fa709a, #fee140); color: white; padding: 15px; border-radius: 8px;">
                <h4 style="margin: 0 0 10px 0;">💳 {{solution_3_title}}</h4>
                <p style="margin: 0; font-size: 14px;">{{solution_3_description}}</p>
            </div>
        </div>
    </div>
    
    <div style="background: #e8f5e8; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
        <h3 style="color: #2d5a2d; margin-top: 0;">💰 {{guarantee_title}}</h3>
        <p style="color: #2d5a2d; margin: 0;">{{guarantee_description}}</p>
    </div>
    
    <div style="text-align: center; margin: 30px 0;">
        <a href="{{website_url}}" style="background: linear-gradient(135deg, #fa709a, #fee140); color: white; padding: 15px 40px; text-decoration: none; border-radius: 25px; display: inline-block; font-weight: bold;">{{cta_text}}</a>
    </div>
    
    <div style="border-top: 1px solid #eee; padding-top: 20px; text-align: center; color: #666; font-size: 12px;">
        <p><strong>{{company_name}} - E-ticaret Uzmanları</strong><br>
        📧 {{email}} | 📞 {{phone}}<br>
        🌐 {{website_url}}</p>
    </div>
</body>
</html>
            """,
            "is_ai_generated": False,
            "template_fields": [
                {"name": "company_name", "label": "Şirket Adı", "type": "text", "required": True, "default": "Şirket Adınız"},
                {"name": "company_tagline", "label": "Şirket Sloganı", "type": "text", "required": False, "default": "E-ticaret Uzmanları"},
                {"name": "headline", "label": "Ana Başlık", "type": "text", "required": True, "default": "Online Satışlarınızı Patlatın!"},
                {"name": "description", "label": "Açıklama", "type": "textarea", "required": True, "default": "Modern e-ticaret çözümleri ile müşterilerinize 7/24 satış yapma imkanı sunun."},
                {"name": "solution_1_title", "label": "Çözüm 1 Başlık", "type": "text", "required": True, "default": "Özel E-ticaret Sitesi"},
                {"name": "solution_1_description", "label": "Çözüm 1 Açıklama", "type": "textarea", "required": True, "default": "Ürün kataloğu, sepet, ödeme sistemi entegrasyonu"},
                {"name": "solution_2_title", "label": "Çözüm 2 Başlık", "type": "text", "required": True, "default": "Mobil Uyumlu Tasarım"},
                {"name": "solution_2_description", "label": "Çözüm 2 Açıklama", "type": "textarea", "required": True, "default": "Mobil cihazlarda mükemmel görünüm ve kullanım"},
                {"name": "solution_3_title", "label": "Çözüm 3 Başlık", "type": "text", "required": True, "default": "Güvenli Ödeme Sistemi"},
                {"name": "solution_3_description", "label": "Çözüm 3 Açıklama", "type": "textarea", "required": True, "default": "Kredi kartı, havale, kapıda ödeme seçenekleri"},
                {"name": "guarantee_title", "label": "Garanti Başlığı", "type": "text", "required": True, "default": "Satış Artış Garantisi"},
                {"name": "guarantee_description", "label": "Garanti Açıklaması", "type": "textarea", "required": True, "default": "Profesyonel e-ticaret sitesi ile satışlarınız %300'e kadar artabilir!"},
                {"name": "cta_text", "label": "Buton Metni", "type": "text", "required": True, "default": "Ücretsiz Teklif Alın"},
                {"name": "email", "label": "Email Adresi", "type": "email", "required": True, "default": "info@example.com"},
                {"name": "phone", "label": "Telefon", "type": "text", "required": True, "default": "+90 XXX XXX XX XX"},
                {"name": "website_url", "label": "Website URL", "type": "url", "required": True, "default": "https://www.example.com"}
            ]
        }
    ]
    
    return default_templates

@router.post("/", response_model=dict)
async def create_template(
    template_data: EmailTemplateCreate,
    current_user: str = Depends(get_current_user)
):
    """Yeni email şablonu oluştur"""
    db = await get_async_db()
    user_id = ObjectId(current_user)
    
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    
    plan = None
    if user.get("plan_id"):
        plan = await db.plans.find_one({"_id": user["plan_id"]})
    
    current_templates = await db.email_templates.count_documents({
        "user_id": user_id,
        "is_active": True
    })
    
    template_limit = plan["max_templates"] if plan else 1
    if current_templates >= template_limit:
        raise HTTPException(
            status_code=400,
            detail=f"Şablon limitinize ulaştınız ({template_limit}). Paketinizi yükseltebilirsiniz."
        )
    
    template_dict = template_data.dict()
    template_dict["user_id"] = user_id
    template_dict["created_at"] = datetime.utcnow()
    template_dict["updated_at"] = datetime.utcnow()
    
    result = await db.email_templates.insert_one(template_dict)
    
    return {
        "id": str(result.inserted_id),
        "message": "Email şablonu başarıyla oluşturuldu"
    }

@router.post("/ai-generate", response_model=AITemplateResponse)
async def generate_ai_template(
    request: AITemplateRequest,
    current_user: str = Depends(get_current_user)
):
    """AI ile email şablonu oluştur"""
    try:
        db = await get_async_db()
        user_id = ObjectId(current_user)
        
        user = await db.users.find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
        
        plan = None
        if user.get("plan_id"):
            plan = await db.plans.find_one({"_id": user["plan_id"]})
        
        current_templates = await db.email_templates.count_documents({
            "user_id": user_id,
            "is_active": True
        })
        
        template_limit = plan.get("max_templates", 1) if plan else 1
        if current_templates >= template_limit:
            raise HTTPException(
                status_code=400,
                detail=f"Şablon limitinize ulaştınız ({template_limit}). Paketinizi yükseltebilirsiniz."
            )
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        {request.prompt}
        
        Bu prompt için profesyonel bir HTML email şablonu oluştur.
        
        ÖNEMLİ: Sadece HTML kodunu yaz, hiç markdown formatlaması kullanma (```html gibi).
        Direkt HTML ile başla ve bitir.
        
        HTML email özellikleri:
        - Profesyonel inline CSS stilleri kullan
        - Şirket: Astoper
        - Website: https://www.astoper.com
        - Telefon: +90 XXX XXX XX XX
        - Email: syalcinkaya895@gmail.com
        - Gönderen: Serkan
        
        Email özellikleri:
        - Modern ve çekici tasarım
        - Responsive (mobil uyumlu)
        - Güçlü call-to-action butonları
        - İletişim bilgileri dahil
        - Email uyumluluğu için inline CSS kullan
        - Türkçe olarak yaz
        
        Sadece temiz HTML kodu döndür, başka hiçbir metin ekleme.
        """
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=1000,
                temperature=0.7,
            )
        )
        
        if not response.text:
            raise HTTPException(status_code=500, detail="AI şablon oluşturulamadı")
        
        content = response.text.strip()
        content = content.replace('```html', '').replace('```', '').strip()
        
        subject_prompt = f"""
        {request.prompt}
        
        Bu email için kısa, çekici bir konu başlığı öner.
        Maksimum 60 karakter olsun.
        Türkçe olarak yaz.
        Sadece konu başlığını döndür, başka hiçbir metin ekleme.
        """
        
        subject_response = model.generate_content(subject_prompt)
        subject = subject_response.text.strip() if subject_response.text else "Dijital Çözümlerimiz"
        
        db = await get_async_db()
        user_id = ObjectId(current_user)
        
        template_data = {
            "name": request.template_name,
            "subject": subject,
            "content": content,
            "category": request.category,
            "is_ai_generated": True,
            "ai_prompt": request.prompt,
            "user_id": user_id,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.email_templates.insert_one(template_data)
        
        return AITemplateResponse(
            template_id=str(result.inserted_id),
            content=content,
            subject=subject
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI şablon oluşturma hatası: {str(e)}")

@router.put("/{template_id}", response_model=dict)
async def update_template(
    template_id: str,
    update_data: EmailTemplateUpdate,
    current_user: str = Depends(get_current_user)
):
    """Email şablonunu güncelle"""
    db = await get_async_db()
    user_id = ObjectId(current_user)
    
    if not ObjectId.is_valid(template_id):
        raise HTTPException(status_code=400, detail="Geçersiz şablon ID")
    
    template = await db.email_templates.find_one({
        "_id": ObjectId(template_id),
        "user_id": user_id
    })
    
    if not template:
        raise HTTPException(status_code=404, detail="Şablon bulunamadı")
    
    update_dict = update_data.dict(exclude_unset=True)
    if update_dict:
        update_dict["updated_at"] = datetime.utcnow()
        
        await db.email_templates.update_one(
            {"_id": ObjectId(template_id)},
            {"$set": update_dict}
        )
    
    return {"message": "Şablon başarıyla güncellendi"}

@router.delete("/{template_id}", response_model=dict)
async def delete_template(
    template_id: str,
    current_user: str = Depends(get_current_user)
):
    """Email şablonunu sil"""
    db = await get_async_db()
    user_id = ObjectId(current_user)
    
    if not ObjectId.is_valid(template_id):
        raise HTTPException(status_code=400, detail="Geçersiz şablon ID")
    
    result = await db.email_templates.update_one(
        {"_id": ObjectId(template_id), "user_id": user_id},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Şablon bulunamadı")
    
    return {"message": "Şablon başarıyla silindi"}

@router.get("/{template_id}", response_model=dict)
async def get_template(
    template_id: str,
    current_user: str = Depends(get_current_user)
):
    """Belirli bir şablonu getir"""
    db = await get_async_db()
    user_id = ObjectId(current_user)
    
    if not ObjectId.is_valid(template_id):
        raise HTTPException(status_code=400, detail="Geçersiz şablon ID")
    
    template = await db.email_templates.find_one({
        "_id": ObjectId(template_id),
        "user_id": user_id,
        "is_active": True
    })
    
    if not template:
        raise HTTPException(status_code=404, detail="Şablon bulunamadı")
    
    template["_id"] = str(template["_id"])
    template["user_id"] = str(template["user_id"])
    
    return template

@router.post("/upload-template")
async def upload_template(
    file: UploadFile = File(...),
    template_name: str = None,
    current_user: str = Depends(get_current_user)
):
    """Hazır email şablonu yükle"""
    try:
        db = await get_async_db()
        user_id = ObjectId(current_user)
        
        user = await db.users.find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
        
        plan = await db.plans.find_one({"_id": user.get("plan_id")})
        
        current_templates = await db.email_templates.count_documents({"user_id": user_id, "is_active": True})
        template_limit = plan.get("max_templates", 1) if plan else 1
        
        if current_templates >= template_limit:
            raise HTTPException(
                status_code=400,
                detail=f"Şablon limitinize ulaştınız ({template_limit}). Paketinizi yükseltebilirsiniz."
            )
        
        allowed_types = ["text/html", "text/plain"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Sadece HTML ve TXT dosyaları kabul edilir"
            )
        
        content = await file.read()
        if len(content) > 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="Dosya boyutu 1MB'dan büyük olamaz"
            )
        
        content_str = content.decode('utf-8')
        
        if not template_name:
            template_name = file.filename.split('.')[0]
        
        new_template = {
            "user_id": user_id,
            "name": template_name,
            "subject": "Şablon Konusu",  # Kullanıcı daha sonra düzenleyebilir
            "content": content_str,
            "is_active": True,
            "is_uploaded": True,  # Yüklenen şablon olduğunu belirt
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.email_templates.insert_one(new_template)
        
        return {
            "message": "Şablon başarıyla yüklendi",
            "template_id": str(result.inserted_id),
            "template_name": template_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Şablon yüklenirken hata oluştu: {str(e)}"
        )

@router.get("/preview/{template_id}")
async def preview_template(
    template_id: str,
    current_user: str = Depends(get_current_user)
):
    """Şablon önizlemesi"""
    try:
        db = await get_async_db()
        user_id = ObjectId(current_user)
        
        template = await db.email_templates.find_one({
            "_id": ObjectId(template_id),
            "user_id": user_id,
            "is_active": True
        })
        
        if not template:
            raise HTTPException(status_code=404, detail="Şablon bulunamadı")
        
        return {
            "id": str(template["_id"]),
            "name": template["name"],
            "subject": template["subject"],
            "content": template["content"],
            "is_uploaded": template.get("is_uploaded", False),
            "created_at": template["created_at"],
            "updated_at": template["updated_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Şablon önizlenirken hata oluştu: {str(e)}"
        )
