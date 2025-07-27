#!/usr/bin/env python3
"""
TEST FIRST: Real API testing with Suprava Sabat
This script is for Tyler to test and document API responses
"""

import json
import requests
import time
from datetime import datetime
import os
from typing import Dict, Any

# Configuration
API_KEY = os.getenv('RAPIDAPI_KEY', '')
INFLUENCER_URL = "https://www.linkedin.com/in/suprava-sabat-saasleadgen/"

# API Endpoints from catalog
ENDPOINTS = {
    'person_deep': 'https://linkedin-data-scraper.p.rapidapi.com/person_deep',
    'profile_updates': 'https://linkedin-data-scraper.p.rapidapi.com/profile_updates',
    'post': 'https://linkedin-data-scraper.p.rapidapi.com/post',
    'post_reactions': 'https://linkedin-data-scraper.p.rapidapi.com/post_reactions',
    'post_comments': 'https://linkedin-data-scraper.p.rapidapi.com/post_comments'
}

# Headers
HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'linkedin-data-scraper.p.rapidapi.com',
    'Content-Type': 'application/json'
}


def test_api_call(endpoint: str, method: str = 'GET', params: Dict = None, 
                  data: Dict = None) -> Dict[str, Any]:
    """
    Test an API endpoint and document the response
    """
    print(f"\n{'='*60}")
    print(f"Testing: {endpoint}")
    print(f"Method: {method}")
    print(f"Params: {params}")
    print(f"Data: {data}")
    print(f"Time: {datetime.now()}")
    print('='*60)
    
    start_time = time.time()
    
    try:
        if method == 'GET':
            response = requests.get(endpoint, headers=HEADERS, params=params)
        else:
            response = requests.post(endpoint, headers=HEADERS, json=data)
        
        duration = time.time() - start_time
        
        result = {
            'endpoint': endpoint,
            'status_code': response.status_code,
            'duration_seconds': round(duration, 2),
            'headers': dict(response.headers),
            'response': response.json() if response.status_code == 200 else response.text
        }
        
        # Check rate limit headers
        rate_limit_headers = {
            'x-ratelimit-limit': response.headers.get('x-ratelimit-limit'),
            'x-ratelimit-remaining': response.headers.get('x-ratelimit-remaining'),
            'x-ratelimit-reset': response.headers.get('x-ratelimit-reset')
        }
        
        print(f"Status: {response.status_code}")
        print(f"Duration: {duration:.2f}s")
        print(f"Rate Limits: {rate_limit_headers}")
        
        return result
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {
            'endpoint': endpoint,
            'error': str(e),
            'duration_seconds': time.time() - start_time
        }


def save_response(data: Dict, filename: str):
    """Save response to file for analysis"""
    with open(f"test_data/{filename}", 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\nSaved to: test_data/{filename}")


def main():
    """
    Tyler's test sequence
    """
    # Create test data directory
    os.makedirs('test_data', exist_ok=True)
    
    if not API_KEY:
        print("ERROR: Set RAPIDAPI_KEY environment variable!")
        return
    
    print(f"🎯 TARGET INFLUENCER: {INFLUENCER_URL}")
    
    # STEP 1: Test getPersonDeepProfile
    print("\n\n📋 STEP 1: Testing getPersonDeepProfile")
    person_result = test_api_call(
        ENDPOINTS['person_deep'],
        method='POST',
        data={'link': INFLUENCER_URL}
    )
    
    if person_result.get('status_code') == 200:
        save_response(person_result, '1_person_deep_response.json')
        
        # Extract key info
        data = person_result['response'].get('data', {})
        print(f"\n✅ Influencer: {data.get('fullName')}")
        print(f"Headline: {data.get('headline')}")
        print(f"Followers: {data.get('followerCount', 0):,}")
        print(f"Connections: {data.get('connectionsCount', 0):,}")
    else:
        print("❌ Failed to fetch influencer profile!")
        return
    
    # Wait to respect rate limits
    print("\n⏳ Waiting 2 seconds...")
    time.sleep(2)
    
    # STEP 2: Test getPersonPosts
    print("\n\n📋 STEP 2: Testing getPersonPosts")
    posts_result = test_api_call(
        ENDPOINTS['profile_updates'],
        method='GET',
        params={
            'profile_url': INFLUENCER_URL,
            'page': 1,
            'paginationToken': ''
        }
    )
    
    if posts_result.get('status_code') == 200:
        save_response(posts_result, '2_posts_response.json')
        
        # Analyze posts
        data = posts_result['response'].get('data', {})
        posts = data.get('posts', [])  # Changed from 'items' to 'posts'
        print(f"\n✅ Found {len(posts)} posts")
        
        # Find high-engagement post about lead generation
        relevant_posts = []
        for i, post in enumerate(posts[:10]):  # Check first 10
            text = post.get('text', '').lower()
            reactions = post.get('reactionsCount', 0)
            
            # Check relevance
            if any(keyword in text for keyword in ['lead', 'outbound', 'sales', 'sdr', 'pipeline']):
                relevant_posts.append({
                    'index': i,
                    'url': post.get('url'),
                    'text': text[:100] + '...',
                    'reactions': reactions,
                    'comments': post.get('commentsCount', 0)
                })
        
        print(f"\n🎯 Found {len(relevant_posts)} relevant posts:")
        for rp in relevant_posts[:3]:
            print(f"\nPost {rp['index']}:")
            print(f"Text: {rp['text']}")
            print(f"Reactions: {rp['reactions']}, Comments: {rp['comments']}")
            print(f"URL: {rp['url']}")
    else:
        print("❌ Failed to fetch posts!")
        return
    
    print("\n\n✅ PHASE 1 COMPLETE!")
    print("\nNEXT STEPS:")
    print("1. Tyler: Review the saved JSON files in test_data/")
    print("2. Tyler: Pick the best post for engagement extraction")
    print("3. Tyler: Test getPostData with that post URL")
    print("4. Dev: Review data structure and propose minimal schema")
    print("5. Guide: Approve next phase")


if __name__ == "__main__":
    main()