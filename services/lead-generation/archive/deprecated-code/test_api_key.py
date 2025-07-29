#!/usr/bin/env python3
"""
Quick API key test - verify the correct key works
"""

import os
import requests
import time

# Load from .env file
from dotenv import load_dotenv
load_dotenv('../.env')

API_KEY = os.getenv('RAPIDAPI_KEY')

HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'linkedin-data-scraper.p.rapidapi.com',
    'Content-Type': 'application/json'
}

def test_endpoints():
    """Test various endpoints with the correct API key"""
    
    print(f"🔑 Testing with API key: {API_KEY[:10]}...")
    print("="*60)
    
    # Test 1: Post data
    print("\n1️⃣ Testing post endpoint...")
    post_url = "https://www.linkedin.com/feed/update/urn:li:activity:7353758072894320642"
    
    try:
        response = requests.post(
            'https://linkedin-data-scraper.p.rapidapi.com/post',
            headers=HEADERS,
            json={'link': post_url},
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ POST endpoint works!")
        else:
            print(f"   ❌ Error: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Wait between calls
    time.sleep(15)
    
    # Test 2: Person endpoint
    print("\n2️⃣ Testing person endpoint...")
    profile_url = "https://linkedin.com/in/suprava-sabat-saasleadgen"
    
    try:
        response = requests.post(
            'https://linkedin-data-scraper.p.rapidapi.com/person',
            headers=HEADERS,
            json={'link': profile_url},
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ PERSON endpoint works!")
        else:
            print(f"   ❌ Error: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print("\n✅ API key test complete!")

if __name__ == "__main__":
    test_endpoints()