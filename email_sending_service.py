import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Optional, Any
import re
from datetime import datetime
import base64
from cryptography.fernet import Fernet
import os
from bson import ObjectId
import uuid

logger = logging.getLogger(__name__)

class EmailSendingService:
    """Email gönderme servisi - kullanıcının email provider'ı ile şablon gönderme"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_encryption_key(self):
        """Şifreleme anahtarı al"""
        key = os.getenv("ENCRYPTION_KEY", "your-32-byte-encryption-key-here!!")
        return base64.urlsafe_b64encode(key.encode()[:32].ljust(32, b'0'))

    def decrypt_password(self, encrypted_password: str) -> str:
        """Şifreyi çöz"""
        try:
            key = self.get_encryption_key()
            fernet = Fernet(key)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_password.encode())
            decrypted_password = fernet.decrypt(encrypted_bytes)
            return decrypted_password.decode()
        except Exception as e:
            self.logger.error(f"Şifre çözme hatası: {e}")
            raise
    
    def personalize_template_content(self, template_content: str, template_subject: str, 
                                  custom_data: Dict[str, Any], recipient_email: str = None) -> tuple:
        """Şablon içeriğini kişiselleştir"""
        try:
            personalized_content = template_content
            personalized_subject = template_subject
            
            default_values = {
                "company_name": "Astoper",
                "company_tagline": "Dijital Dönüşüm Partneriniz",
                "email": "syalcinkaya895@gmail.com",
                "phone": "+90 XXX XXX XX XX",
                "website_url": "https://www.astoper.com",
                "greeting_message": "Şirketinizin dijital varlığını güçlendirmek için profesyonel web tasarım hizmetlerimizi sunuyoruz.",
                "service_1": "Modern ve responsive web tasarımı",
                "service_2": "SEO optimizasyonu",
                "service_3": "E-ticaret çözümleri",
                "service_4": "Web sitesi bakım ve güncelleme",
                "offer_title": "Ücretsiz Danışmanlık",
                "offer_description": "Projeniz için detaylı analiz ve teklif sunuyoruz"
            }
            
            all_data = {**default_values, **custom_data}
            
            for key, value in all_data.items():
                placeholder = f"{{{{{key}}}}}"
                personalized_content = personalized_content.replace(placeholder, str(value))
                personalized_subject = personalized_subject.replace(placeholder, str(value))
            
            if recipient_email and "{{recipient_email}}" in personalized_content:
                personalized_content = personalized_content.replace("{{recipient_email}}", recipient_email)
            
            current_date = datetime.now().strftime("%d.%m.%Y")
            personalized_content = personalized_content.replace("{{current_date}}", current_date)
            personalized_subject = personalized_subject.replace("{{current_date}}", current_date)
            
            return personalized_content, personalized_subject
            
        except Exception as e:
            self.logger.error(f"Template kişiselleştirme hatası: {e}")
            return template_content, template_subject
    
    async def send_email_with_template(self, 
                                     provider_data: Dict,
                                     template_data: Dict,
                                     recipient_email: str,
                                     custom_data: Dict[str, Any] = None,
                                     user_id: str = None,
                                     campaign_id: str = None) -> Dict[str, Any]:
        """Şablon ile email gönder"""
        try:
            smtp_config = provider_data.get("smtp_config")
            if not smtp_config:
                raise Exception("SMTP konfigürasyonu bulunamadı")
            
            smtp_config = smtp_config.copy()
            smtp_config["password"] = self.decrypt_password(smtp_config["password"])
            
            personalized_content, personalized_subject = self.personalize_template_content(
                template_data["content"],
                template_data["subject"],
                custom_data or {},
                recipient_email
            )
            
            msg = MIMEMultipart('alternative')
            msg['From'] = provider_data["email_address"]
            msg['To'] = recipient_email
            msg['Subject'] = personalized_subject
            
            html_part = MIMEText(personalized_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            server = None
            try:
                if smtp_config["host"] == "smtp.gmail.com":
                    server = smtplib.SMTP(smtp_config["host"], smtp_config["port"])
                    server.starttls()
                elif smtp_config.get("use_ssl", False):
                    server = smtplib.SMTP_SSL(smtp_config["host"], smtp_config["port"])
                else:
                    server = smtplib.SMTP(smtp_config["host"], smtp_config["port"])
                    if smtp_config.get("use_tls", False):
                        server.starttls()
                
                server.login(smtp_config["username"], smtp_config["password"])
                
                text = msg.as_string()
                server.sendmail(provider_data["email_address"], recipient_email, text)
                
                if user_id:
                    await self._create_email_tracking_record(
                        user_id=user_id,
                        email_address=recipient_email,
                        subject=personalized_subject,
                        template_id=template_data.get("_id"),
                        provider_id=provider_data.get("_id"),
                        status="sent",
                        campaign_id=campaign_id
                    )
                
                self.logger.info(f"Email başarıyla gönderildi: {recipient_email}")
                
                return {
                    "success": True,
                    "message": "Email başarıyla gönderildi",
                    "recipient": recipient_email,
                    "subject": personalized_subject
                }
                
            finally:
                if server:
                    server.quit()
                    
        except smtplib.SMTPException as e:
            self.logger.error(f"SMTP hatası: {e}")
            
            if user_id:
                await self._create_email_tracking_record(
                    user_id=user_id,
                    email_address=recipient_email,
                    subject=personalized_subject if 'personalized_subject' in locals() else template_data.get("subject", ""),
                    template_id=template_data.get("_id"),
                    provider_id=provider_data.get("_id"),
                    status="failed",
                    error_message=str(e),
                    campaign_id=campaign_id
                )
            
            return {
                "success": False,
                "message": f"SMTP hatası: {str(e)}",
                "recipient": recipient_email
            }
        except Exception as e:
            self.logger.error(f"Email gönderme hatası: {e}")
            
            if user_id:
                await self._create_email_tracking_record(
                    user_id=user_id,
                    email_address=recipient_email,
                    subject=personalized_subject if 'personalized_subject' in locals() else template_data.get("subject", ""),
                    template_id=template_data.get("_id"),
                    provider_id=provider_data.get("_id"),
                    status="failed",
                    error_message=str(e),
                    campaign_id=campaign_id
                )
            
            return {
                "success": False,
                "message": f"Email gönderme hatası: {str(e)}",
                "recipient": recipient_email
            }
    
    async def send_bulk_emails_with_template(self,
                                           provider_data: Dict,
                                           template_data: Dict,
                                           recipient_emails: List[str],
                                           custom_data: Dict[str, Any] = None,
                                           delay_between_emails: float = 1.0,
                                           user_id: str = None,
                                           campaign_id: str = None) -> Dict[str, Any]:
        """Toplu email gönderme - şablon ile"""
        try:
            results = {
                "total_emails": len(recipient_emails),
                "successful": 0,
                "failed": 0,
                "results": []
            }
            
            for i, recipient_email in enumerate(recipient_emails):
                try:
                    email_custom_data = custom_data.copy() if custom_data else {}
                    
                    result = await self.send_email_with_template(
                        provider_data=provider_data,
                        template_data=template_data,
                        recipient_email=recipient_email,
                        custom_data=email_custom_data,
                        user_id=user_id,
                        campaign_id=campaign_id
                    )
                    
                    if result["success"]:
                        results["successful"] += 1
                    else:
                        results["failed"] += 1
                    
                    results["results"].append(result)
                    
                    if i < len(recipient_emails) - 1:  # Son email değilse
                        import asyncio
                        await asyncio.sleep(delay_between_emails)
                    
                except Exception as e:
                    self.logger.error(f"Email gönderme hatası ({recipient_email}): {e}")
                    results["failed"] += 1
                    results["results"].append({
                        "success": False,
                        "message": str(e),
                        "recipient": recipient_email
                    })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Toplu email gönderme hatası: {e}")
            return {
                "total_emails": len(recipient_emails),
                "successful": 0,
                "failed": len(recipient_emails),
                "error": str(e)
            }
    
    def validate_email_address(self, email: str) -> bool:
        """Email adresini doğrula"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    async def test_email_provider_connection(self, provider_data: Dict) -> Dict[str, Any]:
        """Email provider bağlantısını test et"""
        try:
            smtp_config = provider_data.get("smtp_config")
            if not smtp_config:
                return {"success": False, "message": "SMTP konfigürasyonu bulunamadı"}
            
            smtp_config = smtp_config.copy()
            smtp_config["password"] = self.decrypt_password(smtp_config["password"])
            
            server = None
            try:
                if smtp_config["host"] == "smtp.gmail.com":
                    server = smtplib.SMTP(smtp_config["host"], smtp_config["port"])
                    server.starttls()
                elif smtp_config.get("use_ssl", False):
                    server = smtplib.SMTP_SSL(smtp_config["host"], smtp_config["port"])
                else:
                    server = smtplib.SMTP(smtp_config["host"], smtp_config["port"])
                    if smtp_config.get("use_tls", False):
                        server.starttls()
                
                server.login(smtp_config["username"], smtp_config["password"])
                
                return {"success": True, "message": "Bağlantı başarılı"}
                
            finally:
                if server:
                    server.quit()
                    
        except Exception as e:
            self.logger.error(f"Provider test hatası: {e}")
            return {"success": False, "message": f"Bağlantı hatası: {str(e)}"}
    
    async def _create_email_tracking_record(self, user_id: str, email_address: str, 
                                          subject: str, template_id: str = None, 
                                          provider_id: str = None, status: str = "sent",
                                          error_message: str = None, campaign_id: str = None):
        """Email tracking kaydı oluştur"""
        try:
            from database import get_async_db
            db = await get_async_db()
            
            if not campaign_id:
                campaign_id = str(uuid.uuid4())
            
            tracking_record = {
                "user_id": ObjectId(user_id),
                "email_address": email_address,
                "subject": subject,
                "template_id": template_id,
                "provider_id": provider_id,
                "status": status,
                "sent_at": datetime.utcnow(),
                "error_message": error_message,
                "campaign_id": campaign_id
            }
            
            await db.email_tracking.insert_one(tracking_record)
            self.logger.info(f"Email tracking kaydı oluşturuldu: {email_address}")
            
        except Exception as e:
            self.logger.error(f"Email tracking kaydı oluşturma hatası: {e}")
    
    async def get_email_tracking_stats(self, user_id: str, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """Kullanıcının email gönderim istatistiklerini getir"""
        try:
            from database import get_async_db
            db = await get_async_db()
            
            filter_query = {"user_id": ObjectId(user_id)}
            if start_date:
                filter_query["sent_at"] = {"$gte": start_date}
            if end_date:
                if "sent_at" in filter_query:
                    filter_query["sent_at"]["$lte"] = end_date
                else:
                    filter_query["sent_at"] = {"$lte": end_date}
            
            total_emails = await db.email_tracking.count_documents(filter_query)
            
            sent_count = await db.email_tracking.count_documents({**filter_query, "status": "sent"})
            failed_count = await db.email_tracking.count_documents({**filter_query, "status": "failed"})
            delivered_count = await db.email_tracking.count_documents({**filter_query, "status": "delivered"})
            opened_count = await db.email_tracking.count_documents({**filter_query, "status": "opened"})
            clicked_count = await db.email_tracking.count_documents({**filter_query, "status": "clicked"})
            
            pipeline = [
                {"$match": filter_query},
                {"$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$sent_at"}},
                    "count": {"$sum": 1},
                    "sent": {"$sum": {"$cond": [{"$eq": ["$status", "sent"]}, 1, 0]}},
                    "failed": {"$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}}
                }},
                {"$sort": {"_id": 1}}
            ]
            
            daily_stats = await db.email_tracking.aggregate(pipeline).to_list(length=None)
            
            processed_daily_stats = []
            for stat in daily_stats:
                processed_stat = {
                    "date": stat["_id"],
                    "count": stat["count"],
                    "sent": stat["sent"],
                    "failed": stat["failed"]
                }
                processed_daily_stats.append(processed_stat)
            
            return {
                "total_emails": total_emails,
                "sent": sent_count,
                "failed": failed_count,
                "delivered": delivered_count,
                "opened": opened_count,
                "clicked": clicked_count,
                "success_rate": (sent_count / total_emails * 100) if total_emails > 0 else 0,
                "daily_stats": processed_daily_stats
            }
            
        except Exception as e:
            self.logger.error(f"Email tracking istatistikleri alma hatası: {e}")
            return {
                "total_emails": 0,
                "sent": 0,
                "failed": 0,
                "delivered": 0,
                "opened": 0,
                "clicked": 0,
                "success_rate": 0,
                "daily_stats": []
            }
