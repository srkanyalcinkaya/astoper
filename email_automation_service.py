import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
import google.generativeai as genai
import logging
import time
from typing import List, Optional, Dict
import os
from urllib.parse import urljoin, urlparse
import json
import re
from config import settings

logger = logging.getLogger(__name__)

class EmailAutomationService:
    def __init__(self):
        """Email otomasyon servisi başlat"""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        try:
            self.model = genai.GenerativeModel('gemini-1.5-flash-002')
            logger.info("EmailAutomationService başlatıldı (Google Gemini 1.5 Flash)")
        except Exception as e:
            logger.warning(f"Gemini 1.5 Flash bulunamadı: {e}")
            try:
                self.model = genai.GenerativeModel('gemini-1.5-pro-002')
                logger.info("EmailAutomationService başlatıldı (Google Gemini 1.5 Pro)")
            except Exception as e2:
                logger.error(f"Gemini modelleri bulunamadı: {e2}")
                raise Exception("Google Gemini modelleri kullanılamıyor. API anahtarınızı kontrol edin.")

    def get_serpapi_results(self, query: str, num: int = 10) -> List[Dict]:
        """SerpAPI ile arama yap"""
        try:
            params = {
                "q": query,
                "location": "United Kingdom",
                "hl": "en",
                "gl": "uk",
                "num": num,
                "api_key": settings.SERPAPI_KEY
            }
            
            response = requests.get("https://serpapi.com/search", params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for result in data.get('organic_results', []):
                results.append({
                    'url': result.get('link', ''),
                    'title': result.get('title', ''),
                    'snippet': result.get('snippet', ''),
                    'position': result.get('position', 0)
                })
            
            logger.info(f"SerpAPI'den {len(results)} sonuç bulundu: {query}")
            return results
            
        except Exception as e:
            logger.error(f"SerpAPI hatası: {e}")
            return []

    def is_wordpress_site(self, url: str) -> bool:
        """WordPress sitesi mi kontrol et"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            wordpress_indicators = [
                'wp-content',
                'wp-includes',
                'wp-admin',
                'wordpress',
                'wp-json',
                'generator" content="WordPress'
            ]
            
            content = response.text.lower()
            for indicator in wordpress_indicators:
                if indicator in content:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"WordPress kontrolü hatası {url}: {e}")
            return False

    def analyze_seo_quality(self, url: str) -> Dict:
        """SEO kalitesini analiz et"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            seo_score = 0
            issues = []
            
            title = soup.find('title')
            if not title or len(title.get_text().strip()) < 30:
                issues.append("Eksik veya kısa title tag")
                seo_score -= 20
            else:
                seo_score += 10
            
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if not meta_desc or len(meta_desc.get('content', '')) < 120:
                issues.append("Eksik veya kısa meta description")
                seo_score -= 15
            else:
                seo_score += 10
            
            h1_tags = soup.find_all('h1')
            if len(h1_tags) == 0:
                issues.append("H1 tag bulunamadı")
                seo_score -= 15
            elif len(h1_tags) > 1:
                issues.append("Birden fazla H1 tag")
                seo_score -= 10
            else:
                seo_score += 10
            
            images = soup.find_all('img')
            images_without_alt = [img for img in images if not img.get('alt')]
            if len(images_without_alt) > 0:
                issues.append(f"{len(images_without_alt)} resim alt text olmadan")
                seo_score -= 5
            
            internal_links = soup.find_all('a', href=True)
            if len(internal_links) < 5:
                issues.append("Az internal link")
                seo_score -= 10
            
            return {
                'seo_score': max(0, seo_score),
                'issues': issues,
                'is_poor_seo': seo_score < 30 or len(issues) > 3
            }
            
        except Exception as e:
            logger.error(f"SEO analizi hatası {url}: {e}")
            return {'seo_score': 0, 'issues': ['Analiz başarısız'], 'is_poor_seo': True}

    def is_valid_email(self, email: str) -> bool:
        """Email adresi geçerli mi kontrol et"""
        if not email or len(email) < 5:
            return False
        
        file_extensions = [
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp', '.ico',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.zip', '.rar', '.tar', '.gz', '.mp4', '.avi', '.mov', '.wmv',
            '.mp3', '.wav', '.flac', '.css', '.js', '.html', '.htm', '.xml',
            '.json', '.txt', '.log', '.sql', '.php', '.asp', '.jsp'
        ]
        
        email_lower = email.lower()
        for ext in file_extensions:
            if ext in email_lower:
                return False
        
        invalid_patterns = [
            'example.com', 'test.com', 'localhost', '127.0.0.1',
            'admin@', 'noreply@', 'no-reply@', 'donotreply@',
            'webmaster@', 'postmaster@', 'mailer-daemon@',
            'www.', 'http://', 'https://', 'ftp://',
            'data:', 'javascript:', 'mailto:', 'tel:',
            'image/', 'video/', 'audio/', 'application/',
            'text/', 'font/', 'model/', 'multipart/'
        ]
        
        for pattern in invalid_patterns:
            if pattern in email_lower:
                return False
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False
        
        if len(email) > 100:
            return False
        
        invalid_domains = [
            'example.com', 'test.com', 'localhost', 'invalid.com',
            'spam.com', 'fake.com', 'dummy.com', 'temp.com'
        ]
        
        domain = email.split('@')[1].lower() if '@' in email else ''
        if domain in invalid_domains:
            return False
        
        return True

    def categorize_email_with_ai(self, email: str, website_data: Dict = None) -> Dict:
        """AI ile email adresini kategorize et"""
        try:
            website_context = ""
            if website_data:
                website_context = f"""
                Website bilgileri:
                - URL: {website_data.get('url', 'Bilinmiyor')}
                - Başlık: {website_data.get('title', 'Bilinmiyor')}
                - WordPress: {website_data.get('is_wordpress', False)}
                - SEO Skor: {website_data.get('seo_score', 0)}/100
                """
            
            prompt = f"""
            {email} email adresini analiz et ve kategorize et.
            
            {website_context}
            
            Bu email adresini ve website bilgilerini analiz ederek aşağıdaki kategorilerden birine yerleştir:
            
            1. "web_design" - Web tasarım ve geliştirme hizmetleri ihtiyacı olan şirketler
            2. "seo" - SEO ve dijital pazarlama hizmetleri ihtiyacı olan şirketler  
            3. "ecommerce" - E-ticaret çözümleri ihtiyacı olan şirketler
            4. "marketing" - Genel dijital pazarlama hizmetleri
            5. "tech" - Teknoloji ve yazılım hizmetleri
            6. "general" - Belirsiz veya genel kategori
            
            Ayrıca şirketin hangi sektörde olduğunu da belirle (örn: "restoran", "e-ticaret", "hizmet", "teknoloji", "sağlık", vb.)
            
            Sadece JSON formatında yanıt ver:
            {{
                "category": "kategori_adı",
                "confidence": 0.85,
                "industry": "sektör_adı",
                "reason": "kategorilendirme nedeni"
            }}
            
            Confidence 0-1 arasında olsun (1 en yüksek güven).
            """
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=200,
                    temperature=0.3,
                )
            )
            
            if response.text:
                import json
                try:
                    result = json.loads(response.text.strip())
                    return {
                        "category": result.get("category", "general"),
                        "confidence": float(result.get("confidence", 0.5)),
                        "industry": result.get("industry", ""),
                        "reason": result.get("reason", "")
                    }
                except json.JSONDecodeError:
                    return {
                        "category": "general",
                        "confidence": 0.5,
                        "industry": "",
                        "reason": "AI yanıtı parse edilemedi"
                    }
            else:
                return {
                    "category": "general",
                    "confidence": 0.3,
                    "industry": "",
                    "reason": "AI yanıtı alınamadı"
                }
                
        except Exception as e:
            logger.error(f"Email kategorilendirme hatası: {e}")
            return {
                "category": "general",
                "confidence": 0.2,
                "industry": "",
                "reason": f"Hata: {str(e)}"
            }

    def clean_html_content(self, content: str) -> str:
        """AI'den gelen HTML içeriğini temizle"""
        try:
            content = re.sub(r'```html\s*', '', content)
            content = re.sub(r'```\s*$', '', content)
            content = re.sub(r'```', '', content)
            
            content = content.strip()
            
            if not content.lower().startswith('<!doctype') and not content.lower().startswith('<html'):
                if not content.lower().startswith('<'):
                    content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    {content.replace(chr(10), '<br>')}
</body>
</html>
                    """.strip()
            
            logger.info("HTML içeriği temizlendi")
            return content
            
        except Exception as e:
            logger.error(f"HTML temizleme hatası: {e}")
            return content

    def scrape_emails(self, website_url: str) -> List[str]:
        """Websiteden email adreslerini topla"""
        try:
            logger.info(f"Website taranıyor: {website_url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(website_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            emails = []

            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith("mailto:"):
                    email = href.replace("mailto:", "").strip()
                    if '?' in email:
                        email = email.split('?')[0]
                    if '&' in email:
                        email = email.split('&')[0]
                    
                    if self.is_valid_email(email) and email not in emails:
                        emails.append(email)
                        logger.info(f"Geçerli email bulundu: {email}")

            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            page_emails = re.findall(email_pattern, response.text)
            
            for email in page_emails:
                if self.is_valid_email(email) and email not in emails:
                    emails.append(email)
                    logger.info(f"Sayfa içeriğinde email bulundu: {email}")

            logger.info(f"Toplam {len(emails)} geçerli email adresi bulundu")
            return emails
            
        except requests.RequestException as e:
            logger.error(f"Website tarama hatası: {e}")
            return []
        except Exception as e:
            logger.error(f"Email toplama hatası: {e}")
            return []


    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """HTML email gönder"""
        try:
            msg = EmailMessage()
            msg['From'] = settings.SENDER_EMAIL
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.set_content(body, subtype='html')

            with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT) as smtp:
                smtp.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
                smtp.send_message(msg)
            
            logger.info(f"HTML email başarıyla gönderildi: {to_email}")
            return True
            
        except smtplib.SMTPException as e:
            logger.error(f"Email gönderme hatası ({to_email}): {e}")
            return False
        except Exception as e:
            logger.error(f"Beklenmeyen email gönderme hatası ({to_email}): {e}")
            return False

    def run_automation(self, search_queries: List[str] = None, target_urls: List[str] = None, use_serpapi: bool = True, selected_emails: List[str] = None, template_id: str = None, custom_data: Dict = None) -> Dict:
        """Email otomasyonu çalıştır"""
        all_website_urls = set()
        target_websites = []
        
        if use_serpapi and search_queries:
            logger.info("SerpAPI ile WordPress siteleri ve kötü SEO'lu siteler aranıyor...")
            for query in search_queries:
                logger.info(f"Aranıyor: {query}")
                results = self.get_serpapi_results(query, 10)
                
                for result in results:
                    url = result['url']
                    all_website_urls.add(url)
                    
                    logger.info(f"Analiz ediliyor: {url}")
                    
                    is_wordpress = self.is_wordpress_site(url)
                    seo_analysis = self.analyze_seo_quality(url)
                    
                    if is_wordpress or seo_analysis['is_poor_seo']:
                        target_websites.append({
                            'url': url,
                            'title': result['title'],
                            'is_wordpress': is_wordpress,
                            'seo_score': seo_analysis['seo_score'],
                            'seo_issues': seo_analysis['issues']
                        })
                        logger.info(f"Hedef bulundu: {url} (WordPress: {is_wordpress}, SEO Skor: {seo_analysis['seo_score']})")
                    
                    time.sleep(1)  # Rate limiting
                
                time.sleep(2)  # SerpAPI rate limiting
        
        if target_urls:
            for url in target_urls:
                all_website_urls.add(url)
                target_websites.append({
                    'url': url,
                    'title': 'Manuel Giriş',
                    'is_wordpress': self.is_wordpress_site(url),
                    'seo_score': self.analyze_seo_quality(url)['seo_score'],
                    'seo_issues': self.analyze_seo_quality(url)['issues']
                })
        
        if not target_websites:
            logger.warning("Hedef website bulunamadı!")
            return {
                'status': 'failed',
                'message': 'Hedef website bulunamadı',
                'websites_analyzed': 0,
                'emails_found': 0,
                'emails_sent': 0
            }
        
        logger.info(f"{len(target_websites)} hedef website bulundu")
        
        all_emails = set()
        
        for i, website_data in enumerate(target_websites, 1):
            website_url = website_data['url']
            logger.info(f"Website taranıyor ({i}/{len(target_websites)}): {website_url}")
            emails = self.scrape_emails(website_url)
            
            for email in emails:
                all_emails.add(email)
            
            if i < len(target_websites):
                time.sleep(settings.REQUEST_DELAY)
        
        if not all_emails:
            logger.warning("Email adresi bulunamadı!")
            return {
                'status': 'failed',
                'message': 'Email adresi bulunamadı',
                'websites_analyzed': len(target_websites),
                'emails_found': 0,
                'emails_sent': 0
            }
        
        logger.info(f"Toplam {len(all_emails)} benzersiz email adresi bulundu")
        
        emails_to_send = selected_emails if selected_emails else list(all_emails)
        logger.info(f"{len(emails_to_send)} email gönderilecek")
        
        email_to_website = {}
        for website_data in target_websites:
            website_emails = self.scrape_emails(website_data['url'])
            for email in website_emails:
                if email in emails_to_send and email not in email_to_website:
                    email_to_website[email] = website_data
        
        successful_sends = 0
        for i, email in enumerate(emails_to_send, 1):
            logger.info(f"AI email içeriği oluşturuluyor ve gönderiliyor ({i}/{len(emails_to_send)}): {email}")
            
            company_info = email_to_website.get(email)
            
            if not company_info and target_websites:
                company_info = target_websites[0]
            
            if template_id:
                email_body, subject = self.get_template_content(template_id, email, company_info, custom_data)
            else:
                logger.error(f"Şablon seçilmediği için email gönderilemedi: {email}")
                continue
            
            if not email_body:
                logger.error(f"Email içeriği oluşturulamadı: {email}")
                continue
            
            if self.send_email(email, subject, email_body):
                successful_sends += 1
            
            if i < len(emails_to_send):
                time.sleep(settings.REQUEST_DELAY)
        
        logger.info(f"Otomasyon tamamlandı. {successful_sends}/{len(emails_to_send)} email başarıyla gönderildi.")
        
        return {
            'status': 'completed',
            'message': f'{successful_sends}/{len(emails_to_send)} email başarıyla gönderildi',
            'websites_analyzed': len(target_websites),
            'emails_found': len(all_emails),
            'emails_sent': successful_sends
        }

    def create_file_based_email_content(self, email: str) -> Optional[str]:
        """Dosya tabanlı otomasyon için AI email içeriği oluştur"""
        try:
            prompt = f"""
            {email} adresine Türkçe profesyonel bir HTML email yaz.
            
            ÖNEMLİ: Sadece HTML kodunu yaz, hiç markdown formatlaması kullanma (```html gibi).
            Direkt HTML ile başla ve bitir.
            
            HTML email oluştur:
            - Profesyonel inline CSS stilleri kullan
            - Şirket bilgileri: Kullanıcının kendi şirket bilgilerini kullan
            - Sabit şirket adı, telefon, email yazma
            - Kullanıcının girdiği bilgileri kullan
            
            Email konusu:
            Web siteniz için dijital pazarlama ve web geliştirme hizmetlerimizi tanıtmak istiyoruz.
            
            Hizmetlerimizi tanıt:
            1. Modern ve kullanıcı dostu web sitesi tasarımı
            2. SEO optimizasyonu ve Google sıralamasında yükselme
            3. Sosyal medya yönetimi ve dijital pazarlama
            4. E-ticaret çözümleri ve online satış artırma
            5. Web sitesi bakım ve güvenlik hizmetleri
            
            Email özellikleri:
            - Samimi ve profesyonel ton
            - Güçlü call-to-action
            - İletişim bilgileri dahil
            - Email uyumluluğu için inline CSS kullan
            - Türkçe olarak yaz
            
            Email sonunda ücretsiz danışmanlık teklif et.
            
            Sadece temiz HTML kodu döndür, başka hiçbir metin ekleme.
            """
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=800,
                    temperature=0.7,
                )
            )
            
            if response.text:
                content = response.text.strip()
                
                content = self.clean_html_content(content)
                
                logger.info(f"Dosya tabanlı AI email içeriği oluşturuldu: {email}")
                return content
            else:
                logger.error("Gemini'den boş yanıt alındı")
                return None
                
        except Exception as e:
            logger.error(f"Dosya tabanlı email içeriği oluşturma hatası: {e}")
            return None

    def create_search_based_email_content(self, email: str, company_info: Dict = None) -> Optional[str]:
        """Arama tabanlı otomasyon için AI email içeriği oluştur"""
        try:
            company_context = ""
            if company_info:
                company_context = f"""
                Şirket bilgileri:
                - Website: {company_info.get('url', 'Bilinmiyor')}
                - Başlık: {company_info.get('title', 'Bilinmiyor')}
                - SEO Durumu: {company_info.get('seo_score', 0)}/100 puan
                """
            
            prompt = f"""
            {email} adresine Türkçe profesyonel bir HTML email yaz.
            
            ÖNEMLİ: Sadece HTML kodunu yaz, hiç markdown formatlaması kullanma (```html gibi).
            Direkt HTML ile başla ve bitir.
            
            {company_context}
            
            HTML email oluştur:
            - Profesyonel inline CSS stilleri kullan
            - Şirket bilgileri: Kullanıcının kendi şirket bilgilerini kullan
            - Sabit şirket adı, telefon, email yazma
            - Kullanıcının girdiği bilgileri kullan
            
            Email konusu:
            Şirketinizin online varlığını güçlendirmek için dijital çözümlerimizi sunuyoruz.
            
            Hizmetlerimizi tanıt:
            1. Web sitesi analizi ve iyileştirme önerileri
            2. SEO optimizasyonu ve arama motorlarında görünürlük
            3. Modern web tasarım ve kullanıcı deneyimi iyileştirme
            4. Dijital pazarlama stratejileri ve sosyal medya yönetimi
            5. E-ticaret entegrasyonu ve online satış artırma
            6. Web sitesi hız optimizasyonu ve güvenlik
            
            Email özellikleri:
            - Samimi ve profesyonel ton
            - Şirkete özel yaklaşım (eğer bilgi varsa)
            - Güçlü call-to-action
            - İletişim bilgileri dahil
            - Email uyumluluğu için inline CSS kullan
            - Türkçe olarak yaz
            
            Email sonunda ücretsiz web sitesi analizi teklif et.
            
            Sadece temiz HTML kodu döndür, başka hiçbir metin ekleme.
            """
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=800,
                    temperature=0.7,
                )
            )
            
            if response.text:
                content = response.text.strip()
                
                content = self.clean_html_content(content)
                
                logger.info(f"Arama tabanlı AI email içeriği oluşturuldu: {email}")
                return content
            else:
                logger.error("Gemini'den boş yanıt alındı")
                return None
                
        except Exception as e:
            logger.error(f"Arama tabanlı email içeriği oluşturma hatası: {e}")
            return None

    def get_template_content(self, template_id: str, email: str, company_info: Dict = None, custom_data: Dict = None) -> tuple:
        """Şablon içeriğini getir ve kişiselleştir"""
        try:
            if custom_data:
                if template_id == "default_1":
                    content, subject = self.get_web_design_template_with_fields(custom_data)
                elif template_id == "default_2":
                    content, subject = self.get_seo_template_with_fields(custom_data)
                elif template_id == "default_3":
                    content, subject = self.get_ecommerce_template_with_fields(custom_data)
                else:
                    content, subject = self.get_web_design_template_with_fields(custom_data)
            else:
                content = self.create_search_based_email_content(email, company_info)
                subject = "Dijital Çözümlerimiz"
            
            return content, subject
                
        except Exception as e:
            logger.error(f"Şablon içeriği alma hatası: {e}")
            content = self.create_search_based_email_content(email, company_info)
            return content, "Dijital Çözümlerimiz"

    def get_web_design_template_with_fields(self, custom_data: Dict) -> tuple:
        """Web tasarım şablonu - kullanıcı bilgileriyle"""
        subject = custom_data.get('subject', 'Profesyonel Web Tasarım Hizmetlerimiz')
        
        company_name = custom_data.get('company_name', 'Şirket Adınız')
        company_tagline = custom_data.get('company_tagline', 'Dijital Dönüşüm Partneriniz')
        greeting_message = custom_data.get('greeting_message', 'Şirketinizin dijital varlığını güçlendirmek için profesyonel web tasarım hizmetlerimizi sunuyoruz.')
        service_1 = custom_data.get('service_1', 'Modern ve responsive web tasarımı')
        service_2 = custom_data.get('service_2', 'SEO optimizasyonu')
        service_3 = custom_data.get('service_3', 'E-ticaret çözümleri')
        service_4 = custom_data.get('service_4', 'Web sitesi bakım ve güncelleme')
        offer_title = custom_data.get('offer_title', 'Ücretsiz Danışmanlık')
        offer_description = custom_data.get('offer_description', 'Projeniz için detaylı analiz ve teklif sunuyoruz')
        website_url = custom_data.get('website_url', 'https://www.example.com')
        email = custom_data.get('email', 'info@example.com')
        phone = custom_data.get('phone', '+90 XXX XXX XX XX')
        
        content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0; font-size: 24px;">{company_name}</h1>
        <p style="color: #f0f0f0; margin: 10px 0 0 0;">{company_tagline}</p>
    </div>
    
    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
        <h2 style="color: #333; margin-top: 0;">Merhaba!</h2>
        <p>{greeting_message}</p>
    </div>
    
    <div style="margin-bottom: 20px;">
        <h3 style="color: #667eea;">Hizmetlerimiz:</h3>
        <ul style="list-style: none; padding: 0;">
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">✓ {service_1}</li>
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">✓ {service_2}</li>
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">✓ {service_3}</li>
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">✓ {service_4}</li>
        </ul>
    </div>
    
    <div style="background: #e8f4f8; padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0;">
        <p style="margin: 0; font-weight: bold; color: #2c5aa0;">{offer_title}</p>
        <p style="margin: 5px 0 0 0; font-size: 14px;">{offer_description}</p>
    </div>
    
    <div style="text-align: center; margin: 30px 0;">
        <a href="{website_url}" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Web Sitemizi İnceleyin</a>
    </div>
    
    <div style="border-top: 1px solid #eee; padding-top: 20px; text-align: center; color: #666; font-size: 12px;">
        <p><strong>{company_name}</strong><br>
        📧 {email} | 📞 {phone}<br>
        🌐 {website_url}</p>
    </div>
</body>
</html>
        """
        
        return content, subject

    def get_web_design_template(self, email: str, company_info: Dict = None) -> tuple:
        """Web tasarım şablonu"""
        subject = "Profesyonel Web Tasarım Hizmetlerimiz"
        
        company_name = ""
        if company_info:
            company_name = f"<p>Merhaba {company_info.get('title', 'Değerli Müşteri')} ekibi,</p>"
        
        content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0; font-size: 24px;">The Octopus Labs</h1>
        <p style="color: #f0f0f0; margin: 10px 0 0 0;">Dijital Dönüşüm Partneriniz</p>
    </div>
    
    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
        <h2 style="color: #333; margin-top: 0;">Merhaba!</h2>
        {company_name}
        <p>Şirketinizin dijital varlığını güçlendirmek için profesyonel web tasarım hizmetlerimizi sunuyoruz.</p>
    </div>
    
    <div style="margin-bottom: 20px;">
        <h3 style="color: #667eea;">Hizmetlerimiz:</h3>
        <ul style="list-style: none; padding: 0;">
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">✓ Modern ve responsive web tasarımı</li>
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">✓ SEO optimizasyonu</li>
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">✓ E-ticaret çözümleri</li>
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">✓ Web sitesi bakım ve güncelleme</li>
        </ul>
    </div>
    
    <div style="background: #e8f4f8; padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0;">
        <p style="margin: 0; font-weight: bold; color: #2c5aa0;">Ücretsiz Danışmanlık</p>
        <p style="margin: 5px 0 0 0; font-size: 14px;">Projeniz için detaylı analiz ve teklif sunuyoruz</p>
    </div>
    
    <div style="text-align: center; margin: 30px 0;">
        <a href="https://www.theoctopuslabs.com" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Web Sitemizi İnceleyin</a>
    </div>
    
    <div style="border-top: 1px solid #eee; padding-top: 20px; text-align: center; color: #666; font-size: 12px;">
        <p><strong>The Octopus Labs</strong><br>
        📧 info@theoctopuslabs.com | 📞 07497105540<br>
        🌐 https://www.theoctopuslabs.com</p>
    </div>
</body>
</html>
        """
        
        return content, subject

    def get_seo_template_with_fields(self, custom_data: Dict) -> tuple:
        """SEO şablonu - kullanıcı bilgileriyle"""
        subject = custom_data.get('subject', 'Web Sitenizin Arama Motorlarında Görünürlüğünü Artıralım')
        
        company_name = custom_data.get('company_name', 'SEO Uzmanları')
        company_tagline = custom_data.get('company_tagline', 'SEO Uzmanları')
        problem_title = custom_data.get('problem_title', 'Web Siteniz Görünmüyor mu?')
        problem_description = custom_data.get('problem_description', 'Müşterileriniz sizi Google\'da bulamıyor olabilir. Bu büyük bir fırsat kaybı!')
        service_category_1 = custom_data.get('service_category_1', 'Teknik SEO')
        service_1 = custom_data.get('service_1', 'Site hızı optimizasyonu')
        service_2 = custom_data.get('service_2', 'Mobil uyumluluk')
        service_3 = custom_data.get('service_3', 'Meta tag optimizasyonu')
        service_category_2 = custom_data.get('service_category_2', 'İçerik SEO')
        service_4 = custom_data.get('service_4', 'Anahtar kelime analizi')
        service_5 = custom_data.get('service_5', 'İçerik optimizasyonu')
        service_6 = custom_data.get('service_6', 'Blog yazıları')
        offer_title = custom_data.get('offer_title', 'Ücretsiz SEO Analizi')
        offer_description = custom_data.get('offer_description', 'Web sitenizin mevcut SEO durumunu analiz edelim')
        website_url = custom_data.get('website_url', 'https://www.example.com')
        email = custom_data.get('email', 'info@example.com')
        phone = custom_data.get('phone', '+90 XXX XXX XX XX')
        
        content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0; font-size: 24px;">{company_name}</h1>
        <p style="color: #f0f0f0; margin: 10px 0 0 0;">{company_tagline}</p>
    </div>
    
    <div style="background: #fff3cd; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #ffc107;">
        <h2 style="color: #856404; margin-top: 0;">⚠️ {problem_title}</h2>
        <p style="color: #856404; margin: 0;">{problem_description}</p>
    </div>
    
    <div style="margin-bottom: 20px;">
        <h3 style="color: #4facfe;">SEO Hizmetlerimiz:</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                <h4 style="margin: 0 0 10px 0; color: #333;">{service_category_1}</h4>
                <ul style="margin: 0; padding-left: 15px; font-size: 14px;">
                    <li>{service_1}</li>
                    <li>{service_2}</li>
                    <li>{service_3}</li>
                </ul>
            </div>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                <h4 style="margin: 0 0 10px 0; color: #333;">{service_category_2}</h4>
                <ul style="margin: 0; padding-left: 15px; font-size: 14px;">
                    <li>{service_4}</li>
                    <li>{service_5}</li>
                    <li>{service_6}</li>
                </ul>
            </div>
        </div>
    </div>
    
    <div style="background: #d4edda; padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0; border: 1px solid #c3e6cb;">
        <p style="margin: 0; font-weight: bold; color: #155724;">📊 {offer_title}</p>
        <p style="margin: 5px 0 0 0; font-size: 14px; color: #155724;">{offer_description}</p>
    </div>
    
    <div style="text-align: center; margin: 30px 0;">
        <a href="{website_url}" style="background: #4facfe; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Hemen İletişime Geçin</a>
    </div>
    
    <div style="border-top: 1px solid #eee; padding-top: 20px; text-align: center; color: #666; font-size: 12px;">
        <p><strong>{company_name}</strong><br>
        📧 {email} | 📞 {phone}<br>
        🌐 {website_url}</p>
    </div>
</body>
</html>
        """
        
        return content, subject

    def get_seo_template(self, email: str, company_info: Dict = None) -> tuple:
        """SEO şablonu"""
        subject = "Web Sitenizin Arama Motorlarında Görünürlüğünü Artıralım"
        
        content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0; font-size: 24px;">SEO Uzmanları</h1>
        <p style="color: #f0f0f0; margin: 10px 0 0 0;">The Octopus Labs</p>
    </div>
    
    <div style="background: #fff3cd; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #ffc107;">
        <h2 style="color: #856404; margin-top: 0;">⚠️ Web Siteniz Görünmüyor mu?</h2>
        <p style="color: #856404; margin: 0;">Müşterileriniz sizi Google'da bulamıyor olabilir. Bu büyük bir fırsat kaybı!</p>
    </div>
    
    <div style="text-align: center; margin: 30px 0;">
        <a href="https://www.theoctopuslabs.com" style="background: #4facfe; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Hemen İletişime Geçin</a>
    </div>
    
    <div style="border-top: 1px solid #eee; padding-top: 20px; text-align: center; color: #666; font-size: 12px;">
        <p><strong>The Octopus Labs - SEO Uzmanları</strong><br>
        📧 info@theoctopuslabs.com | 📞 07497105540<br>
        🌐 https://www.theoctopuslabs.com</p>
    </div>
</body>
</html>
        """
        
        return content, subject

    def get_ecommerce_template_with_fields(self, custom_data: Dict) -> tuple:
        """E-ticaret şablonu - kullanıcı bilgileriyle"""
        subject = custom_data.get('subject', 'Online Satışlarınızı Artırmak İçin E-ticaret Çözümlerimiz')
        
        company_name = custom_data.get('company_name', 'E-ticaret Uzmanları')
        company_tagline = custom_data.get('company_tagline', 'E-ticaret Uzmanları')
        headline = custom_data.get('headline', 'Online Satışlarınızı Patlatın!')
        description = custom_data.get('description', 'Modern e-ticaret çözümleri ile müşterilerinize 7/24 satış yapma imkanı sunun.')
        solution_1_title = custom_data.get('solution_1_title', 'Özel E-ticaret Sitesi')
        solution_1_description = custom_data.get('solution_1_description', 'Ürün kataloğu, sepet, ödeme sistemi entegrasyonu')
        solution_2_title = custom_data.get('solution_2_title', 'Mobil Uyumlu Tasarım')
        solution_2_description = custom_data.get('solution_2_description', 'Mobil cihazlarda mükemmel görünüm ve kullanım')
        solution_3_title = custom_data.get('solution_3_title', 'Güvenli Ödeme Sistemi')
        solution_3_description = custom_data.get('solution_3_description', 'Kredi kartı, havale, kapıda ödeme seçenekleri')
        guarantee_title = custom_data.get('guarantee_title', 'Satış Artış Garantisi')
        guarantee_description = custom_data.get('guarantee_description', 'Profesyonel e-ticaret sitesi ile satışlarınız %300\'e kadar artabilir!')
        website_url = custom_data.get('website_url', 'https://www.example.com')
        cta_text = custom_data.get('cta_text', 'Ücretsiz Teklif Alın')
        email = custom_data.get('email', 'info@example.com')
        phone = custom_data.get('phone', '+90 XXX XXX XX XX')
        
        content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0; font-size: 24px;">{company_name}</h1>
        <p style="color: #f0f0f0; margin: 10px 0 0 0;">{company_tagline}</p>
    </div>
    
    <div style="background: #fff; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <h2 style="color: #333; margin-top: 0;">🚀 {headline}</h2>
        <p>{description}</p>
    </div>
    
    <div style="margin-bottom: 20px;">
        <h3 style="color: #fa709a;">E-ticaret Çözümlerimiz:</h3>
        <div style="display: grid; grid-template-columns: 1fr; gap: 15px;">
            <div style="background: linear-gradient(90deg, #fa709a, #fee140); color: white; padding: 15px; border-radius: 8px;">
                <h4 style="margin: 0 0 10px 0;">🛒 {solution_1_title}</h4>
                <p style="margin: 0; font-size: 14px;">{solution_1_description}</p>
            </div>
            <div style="background: linear-gradient(90deg, #fa709a, #fee140); color: white; padding: 15px; border-radius: 8px;">
                <h4 style="margin: 0 0 10px 0;">📱 {solution_2_title}</h4>
                <p style="margin: 0; font-size: 14px;">{solution_2_description}</p>
            </div>
            <div style="background: linear-gradient(90deg, #fa709a, #fee140); color: white; padding: 15px; border-radius: 8px;">
                <h4 style="margin: 0 0 10px 0;">💳 {solution_3_title}</h4>
                <p style="margin: 0; font-size: 14px;">{solution_3_description}</p>
            </div>
        </div>
    </div>
    
    <div style="background: #e8f5e8; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
        <h3 style="color: #2d5a2d; margin-top: 0;">💰 {guarantee_title}</h3>
        <p style="color: #2d5a2d; margin: 0;">{guarantee_description}</p>
    </div>
    
    <div style="text-align: center; margin: 30px 0;">
        <a href="{website_url}" style="background: linear-gradient(135deg, #fa709a, #fee140); color: white; padding: 15px 40px; text-decoration: none; border-radius: 25px; display: inline-block; font-weight: bold;">{cta_text}</a>
    </div>
    
    <div style="border-top: 1px solid #eee; padding-top: 20px; text-align: center; color: #666; font-size: 12px;">
        <p><strong>{company_name}</strong><br>
        📧 {email} | 📞 {phone}<br>
        🌐 {website_url}</p>
    </div>
</body>
</html>
        """
        
        return content, subject

    def get_ecommerce_template(self, email: str, company_info: Dict = None) -> tuple:
        """E-ticaret şablonu"""
        subject = "Online Satışlarınızı Artırmak İçin E-ticaret Çözümlerimiz"
        
        content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0; font-size: 24px;">E-ticaret Uzmanları</h1>
        <p style="color: #f0f0f0; margin: 10px 0 0 0;">The Octopus Labs</p>
    </div>
    
    <div style="background: #fff; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <h2 style="color: #333; margin-top: 0;">🚀 Online Satışlarınızı Patlatın!</h2>
        <p>Modern e-ticaret çözümleri ile müşterilerinize 7/24 satış yapma imkanı sunun.</p>
    </div>
    
    <div style="text-align: center; margin: 30px 0;">
        <a href="https://www.theoctopuslabs.com" style="background: linear-gradient(135deg, #fa709a, #fee140); color: white; padding: 15px 40px; text-decoration: none; border-radius: 25px; display: inline-block; font-weight: bold;">Ücretsiz Teklif Alın</a>
    </div>
    
    <div style="border-top: 1px solid #eee; padding-top: 20px; text-align: center; color: #666; font-size: 12px;">
        <p><strong>The Octopus Labs - E-ticaret Uzmanları</strong><br>
        📧 info@theoctopuslabs.com | 📞 07497105540<br>
        🌐 https://www.theoctopuslabs.com</p>
    </div>
</body>
</html>
        """
        
        return content, subject

    def run_file_automation(self, file_path: str, max_results: int = 10, selected_emails: List[str] = None, template_id: str = None, custom_data: Dict = None) -> Dict:
        """Dosya tabanlı email otomasyonu - AI yazılı emailler ile"""
        try:
            logger.info(f"Dosya otomasyonu başlatıldı: {file_path}")
            
            from file_processor import FileProcessor
            
            extracted_data = FileProcessor.process_file_from_path(file_path)
            
            if not extracted_data.get('emails'):
                logger.warning("Dosyada email adresi bulunamadı")
                return {
                    'status': 'completed',
                    'message': 'Dosyada email adresi bulunamadı',
                    'websites_analyzed': 0,
                    'emails_found': 0,
                    'emails_sent': 0
                }
            
            all_emails = extracted_data['emails'][:max_results]  # Plan limitine göre sınırla
            logger.info(f"Dosyadan {len(all_emails)} email adresi bulundu (limit: {max_results})")
            
            emails_to_send = selected_emails if selected_emails else all_emails
            logger.info(f"{len(emails_to_send)} email gönderilecek")
            
            successful_sends = 0
            for i, email in enumerate(emails_to_send, 1):
                logger.info(f"Email içeriği oluşturuluyor ve gönderiliyor ({i}/{len(emails_to_send)}): {email}")
                
                if template_id:
                    email_body, subject = self.get_template_content(template_id, email, None, custom_data)
                else:
                    logger.error(f"Şablon seçilmediği için email gönderilemedi: {email}")
                    continue
                
                if not email_body:
                    logger.error(f"Email içeriği oluşturulamadı: {email}")
                    continue
                
                if self.send_email(email, subject, email_body):
                    successful_sends += 1
                
                if i < len(emails_to_send):
                    time.sleep(settings.REQUEST_DELAY)
            
            logger.info(f"Dosya otomasyonu tamamlandı. {successful_sends}/{len(emails_to_send)} email gönderildi.")
            
            return {
                'status': 'completed',
                'message': f'{successful_sends}/{len(emails_to_send)} email başarıyla gönderildi',
                'websites_analyzed': 1,  # Dosya sayısı
                'emails_found': len(all_emails),
                'emails_sent': successful_sends
            }
            
        except Exception as e:
            logger.error(f"Dosya otomasyonu hatası: {e}")
            return {
                'status': 'failed',
                'message': f'Dosya otomasyonu hatası: {str(e)}',
                'websites_analyzed': 0,
                'emails_found': 0,
                'emails_sent': 0
            }

