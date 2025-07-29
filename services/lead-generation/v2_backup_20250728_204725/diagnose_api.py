#!/usr/bin/env python3
"""
Diagnose API response issues - test different payload structures
"""

import json
import requests
import os
import time
from dotenv import load_dotenv

# Load from .env file
load_dotenv('../.env')

API_KEY = os.getenv('RAPIDAPI_KEY')

HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'linkedin-data-scraper.p.rapidapi.com',
    'Content-Type': 'application/json'
}

def test_variations():
    """Test different payload variations"""
    
    post_url = "https://www.linkedin.com/feed/update/urn:li:activity:7353758072894320642"
    
    print("🔍 API DIAGNOSTIC TEST")
    print(f"API Key: {API_KEY[:20]}...")
    print("="*60)
    
    # Test 1: Original format with 'url'
    print("\n1️⃣ Testing get_post_reactions with 'url' key...")
    try:
        response = requests.post(
            "https://linkedin-data-scraper.p.rapidapi.com/get_post_reactions",
            json={"url": post_url, "start": 0},
            headers=HEADERS,
            timeout=30
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)[:500]}")
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(10)
    
    # Test 2: Try with 'link' key
    print("\n2️⃣ Testing get_post_reactions with 'link' key...")
    try:
        response = requests.post(
            "https://linkedin-data-scraper.p.rapidapi.com/get_post_reactions",
            json={"link": post_url, "start": 0},
            headers=HEADERS,
            timeout=30
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)[:500]}")
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(10)
    
    # Test 3: Try post endpoint
    print("\n3️⃣ Testing 'post' endpoint...")
    try:
        response = requests.post(
            "https://linkedin-data-scraper.p.rapidapi.com/post",
            json={"link": post_url},
            headers=HEADERS,
            timeout=30
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)[:500]}")
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(10)
    
    # Test 4: Try without /v1 or /v2 paths
    print("\n4️⃣ Testing direct endpoint paths...")
    try:
        response = requests.get(
            "https://linkedin-data-scraper.p.rapidapi.com/",
            headers=HEADERS,
            timeout=30
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n✅ Diagnostic complete!")

if __name__ == "__main__":
    test_variations()