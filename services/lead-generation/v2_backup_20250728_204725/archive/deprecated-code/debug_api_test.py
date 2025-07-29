#!/usr/bin/env python3
"""Debug API responses to understand empty data issue"""

import requests
import json
import os

API_KEY = os.getenv('RAPIDAPI_KEY', '03f25c1267msh8befbf9f32825c5p104c76jsn952863a7ff5a')

HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'linkedin-data-scraper.p.rapidapi.com',
    'Content-Type': 'application/json'
}

def test_reactions():
    """Test reactions endpoint with debug output"""
    post_url = "https://www.linkedin.com/feed/update/urn:li:activity:7353758072894320642"
    
    print("Testing reactions endpoint...")
    print(f"URL: {post_url}")
    print(f"Headers: {HEADERS}")
    
    payload = {
        "url": post_url,
        "start": 0
    }
    
    response = requests.post(
        "https://linkedin-data-scraper.p.rapidapi.com/get_post_reactions",
        json=payload,
        headers=HEADERS,
        timeout=30
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"\nResponse Body:")
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        print(response.text)
    
    return response

if __name__ == "__main__":
    test_reactions()