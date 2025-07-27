#!/usr/bin/env python3
"""
Quick Engagement Extraction Test Script
For Tyler to test getPostData and getPostReactions

Target Post: https://www.linkedin.com/feed/update/urn:li:activity:7353758072894320642
Post by Suprava about "turning LinkedIn engagement into qualified sales calls"
"""

import json
import requests
import os
import time
from datetime import datetime

# Configuration
API_KEY = os.getenv('RAPIDAPI_KEY', '')
POST_URL = "https://www.linkedin.com/feed/update/urn:li:activity:7353758072894320642"

HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'linkedin-data-scraper.p.rapidapi.com',
    'Content-Type': 'application/json'
}

def test_post_data():
    """Test getPostData to extract URNs"""
    print("🎯 TESTING getPostData")
    print(f"Post URL: {POST_URL}")
    print("-" * 60)
    
    response = requests.post(
        'https://linkedin-data-scraper.p.rapidapi.com/post',
        headers=HEADERS,
        json={'link': POST_URL}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        # Save full response
        with open('test_data/3_post_data_response.json', 'w') as f:
            json.dump({
                'url': POST_URL,
                'status_code': response.status_code,
                'response': data
            }, f, indent=2)
        
        # Extract key info
        post_data = data.get('data', {})
        print(f"\n✅ Post Data Retrieved!")
        print(f"Text Preview: {post_data.get('text', '')[:100]}...")
        print(f"Reactions Count: {post_data.get('reactionsCount', 0)}")
        print(f"Comments Count: {post_data.get('commentsCount', 0)}")
        print(f"Reactions URN: {post_data.get('reactionsUrn', 'NOT FOUND')}")
        print(f"Comments URN: {post_data.get('commentsUrn', 'NOT FOUND')}")
        
        return post_data.get('reactionsUrn'), post_data.get('commentsUrn')
    else:
        print(f"❌ Error: {response.text}")
        return None, None

def test_reactions(reactions_urn):
    """Test getPostReactions to get engaged users"""
    if not reactions_urn:
        print("\n❌ No reactions URN available!")
        return
    
    print(f"\n\n🎯 TESTING getPostReactions")
    print(f"Reactions URN: {reactions_urn}")
    print("-" * 60)
    
    # Test first page
    response = requests.post(
        'https://linkedin-data-scraper.p.rapidapi.com/post_reactions',
        headers=HEADERS,
        json={
            'reactionsUrn': reactions_urn,
            'page': 1
        }
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        # Save full response
        with open('test_data/4_reactions_response.json', 'w') as f:
            json.dump({
                'reactions_urn': reactions_urn,
                'page': 1,
                'status_code': response.status_code,
                'response': data
            }, f, indent=2)
        
        # Analyze reactions (Tyler discovered they're directly under response)
        reactions = data.get('reactions', [])
        
        print(f"\n✅ Found {len(reactions)} reactions on page 1")
        # Note: Check if more pages available in response structure
        
        # Show first 5 engaged users
        print("\n🎯 Sample Engaged Users:")
        for i, reaction in enumerate(reactions[:5]):
            profile = reaction.get('profile', {})
            print(f"\n{i+1}. {profile.get('fullName')}")
            print(f"   Title: {profile.get('title')}")
            print(f"   Company: {profile.get('subtitle')}")
            print(f"   Profile: {profile.get('url')}")
            print(f"   Reaction: {reaction.get('reactionType')}")
        
        # Count relevant titles
        relevant_count = 0
        keywords = ['sales', 'business development', 'sdr', 'bdr', 'growth', 'revenue']
        
        for reaction in reactions:
            title = reaction.get('profile', {}).get('title', '').lower()
            if any(kw in title for kw in keywords):
                relevant_count += 1
        
        print(f"\n📊 Quick Analysis:")
        print(f"Total reactions analyzed: {len(reactions)}")
        print(f"Potentially relevant (sales roles): {relevant_count}")
        print(f"Relevance rate: {relevant_count/len(reactions)*100:.1f}%")
        
    else:
        print(f"❌ Error: {response.text}")

def main():
    """Run the engagement extraction test"""
    os.makedirs('test_data', exist_ok=True)
    
    if not API_KEY:
        print("❌ ERROR: Set RAPIDAPI_KEY environment variable!")
        return
    
    print("🚀 ENGAGEMENT EXTRACTION TEST")
    print("=" * 60)
    
    # Step 1: Get post data
    reactions_urn, comments_urn = test_post_data()
    
    # Wait for rate limit
    print("\n⏳ Waiting 2 seconds...")
    time.sleep(2)
    
    # Step 2: Get reactions
    if reactions_urn:
        test_reactions(reactions_urn)
    
    print("\n\n✅ ENGAGEMENT TEST COMPLETE!")
    print("\nNEXT STEPS:")
    print("1. Review test_data/3_post_data_response.json")
    print("2. Review test_data/4_reactions_response.json") 
    print("3. Share findings with Dev for schema refinement")
    print("4. Test pagination if needed (hasMore = true)")

if __name__ == "__main__":
    main()