#!/usr/bin/env python3
"""Test correct API flow based on apiCatalog.json"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('../.env')

API_KEY = os.getenv('RAPIDAPI_KEY', '')
HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'linkedin-data-scraper.p.rapidapi.com',
    'Content-Type': 'application/json'
}

def test_profile_posts():
    """Test GET /profile_updates to get person's posts"""
    print("🔍 Step 1: Getting Suprava's posts...")
    
    # Use GET method for profile_updates
    url = "https://linkedin-data-scraper.p.rapidapi.com/profile_updates"
    params = {
        'profile_url': 'https://linkedin.com/in/suprava-sabat-saasleadgen',
        'page': '1',
        'paginationToken': ''
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return data
    else:
        print(f"Error: {response.text}")
        return None

def test_post_data(post_link):
    """Test POST /post to get post details and URNs"""
    print(f"\n🔍 Step 2: Getting post data for: {post_link}")
    
    url = "https://linkedin-data-scraper.p.rapidapi.com/post"
    payload = {'link': post_link}
    
    response = requests.post(url, headers=HEADERS, json=payload)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return data
    else:
        print(f"Error: {response.text}")
        return None

if __name__ == "__main__":
    # Test with our known post URL
    known_post = "https://www.linkedin.com/feed/update/urn:li:activity:7353758072894320642"
    
    # Step 1: Try to get Suprava's posts
    posts_data = test_profile_posts()
    
    # Step 2: Test post data endpoint with known post
    post_data = test_post_data(known_post)