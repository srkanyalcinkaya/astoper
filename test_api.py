"""
Email Automation Platform API Test Script
Bu script API endpoint'lerini test eder.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Health check test"""
    print("🔍 Health check testi...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check başarılı")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check başarısız: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check hatası: {e}")

def test_api_info():
    """API info test"""
    print("\n🔍 API info testi...")
    try:
        response = requests.get(f"{BASE_URL}/api/info")
        if response.status_code == 200:
            print("✅ API info başarılı")
            data = response.json()
            print(f"   Title: {data['title']}")
            print(f"   Version: {data['version']}")
        else:
            print(f"❌ API info başarısız: {response.status_code}")
    except Exception as e:
        print(f"❌ API info hatası: {e}")

def test_plans():
    """Plans endpoint test"""
    print("\n🔍 Plans endpoint testi...")
    try:
        response = requests.get(f"{BASE_URL}/plans/")
        if response.status_code == 200:
            print("✅ Plans endpoint başarılı")
            plans = response.json()
            print(f"   {len(plans)} plan bulundu:")
            for plan in plans:
                print(f"   - {plan['name']}: ${plan['price']}")
        else:
            print(f"❌ Plans endpoint başarısız: {response.status_code}")
    except Exception as e:
        print(f"❌ Plans endpoint hatası: {e}")

def test_register():
    """User registration test"""
    print("\n🔍 User registration testi...")
    try:
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=user_data
        )
        
        if response.status_code == 200:
            print("✅ User registration başarılı")
            user = response.json()
            print(f"   User ID: {user['id']}")
            print(f"   Email: {user['email']}")
            return user
        else:
            print(f"❌ User registration başarısız: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ User registration hatası: {e}")
        return None

def test_login():
    """User login test"""
    print("\n🔍 User login testi...")
    try:
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data
        )
        
        if response.status_code == 200:
            print("✅ User login başarılı")
            token_data = response.json()
            print(f"   Token type: {token_data['token_type']}")
            return token_data['access_token']
        else:
            print(f"❌ User login başarısız: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ User login hatası: {e}")
        return None

def test_authenticated_endpoints(token):
    """Authenticated endpoints test"""
    if not token:
        print("\n❌ Token olmadan authenticated endpoint'ler test edilemez")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🔍 User profile testi...")
    try:
        response = requests.get(f"{BASE_URL}/users/profile", headers=headers)
        if response.status_code == 200:
            print("✅ User profile başarılı")
            profile = response.json()
            print(f"   Username: {profile['username']}")
            print(f"   Plan: {profile['plan']['name']}")
        else:
            print(f"❌ User profile başarısız: {response.status_code}")
    except Exception as e:
        print(f"❌ User profile hatası: {e}")
    
    print("\n🔍 User stats testi...")
    try:
        response = requests.get(f"{BASE_URL}/users/stats", headers=headers)
        if response.status_code == 200:
            print("✅ User stats başarılı")
            stats = response.json()
            print(f"   Total queries: {stats['total_queries']}")
            print(f"   Plan: {stats['plan_usage']['plan_name']}")
        else:
            print(f"❌ User stats başarısız: {response.status_code}")
    except Exception as e:
        print(f"❌ User stats hatası: {e}")
    
    print("\n🔍 Plan usage testi...")
    try:
        response = requests.get(f"{BASE_URL}/plans/usage", headers=headers)
        if response.status_code == 200:
            print("✅ Plan usage başarılı")
            usage = response.json()
            print(f"   Current plan: {usage['current_plan']['name']}")
            print(f"   Queries used: {usage['usage']['queries']['used']}")
        else:
            print(f"❌ Plan usage başarısız: {response.status_code}")
    except Exception as e:
        print(f"❌ Plan usage hatası: {e}")

def main():
    """Ana test fonksiyonu"""
    print("🚀 Email Automation Platform API Test Başlıyor...")
    print("=" * 50)
    
    test_health()
    test_api_info()
    test_plans()
    
    user = test_register()
    token = test_login()
    
    test_authenticated_endpoints(token)
    
    print("\n" + "=" * 50)
    print("🎉 API testleri tamamlandı!")
    print("\n📚 API dokümantasyonu için:")
    print(f"   Swagger UI: {BASE_URL}/docs")
    print(f"   ReDoc: {BASE_URL}/redoc")

if __name__ == "__main__":
    main()

