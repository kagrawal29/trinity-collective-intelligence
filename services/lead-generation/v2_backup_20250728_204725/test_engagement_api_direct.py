#!/usr/bin/env python3
"""
Direct Engagement API Test - Test reactions and comments endpoints directly
Based on apiCatalog.json specifications
"""

import json
import requests
import os
import time
from dotenv import load_dotenv

# Load environment from parent directory
load_dotenv('../.env')

# API Configuration
API_KEY = os.getenv('RAPIDAPI_KEY')
HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'linkedin-data-scraper.p.rapidapi.com',
    'Content-Type': 'application/json'
}

def test_post_data_endpoint():
    """Test getPostData endpoint first to get reactionsUrn and commentsUrn"""
    print("🔍 TESTING POST DATA ENDPOINT")
    print("=" * 50)
    
    # Use a known LinkedIn post URL
    test_post_url = "https://www.linkedin.com/feed/update/urn:li:activity:7340393305525911552"
    
    try:
        response = requests.post(
            "https://linkedin-data-scraper.p.rapidapi.com/post",
            headers=HEADERS,
            json={"link": test_post_url},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ POST DATA SUCCESS!")
            print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            # Look for reactions and comments URNs
            reactions_urn = None
            comments_urn = None
            
            if isinstance(data, dict):
                # Check for URNs in the nested data object
                post_data = data.get('data', {})
                reactions_urn = post_data.get('reactionsUrn')
                comments_urn = post_data.get('commentsUrn')
                
                # Also get social counts
                social_count = post_data.get('socialCount', {})
                num_likes = social_count.get('numLikes', 0)
                num_comments = social_count.get('numComments', 0)
                
                print(f"Reactions URN: {reactions_urn}")
                print(f"Comments URN: {comments_urn}")
                print(f"Social Counts - Likes: {num_likes}, Comments: {num_comments}")
                
                # Save full response for analysis
                with open('test_data/post_data_response.json', 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"📁 Full response saved to test_data/post_data_response.json")
            
            return reactions_urn, comments_urn, data
            
        else:
            print(f"❌ POST DATA FAILED: {response.status_code}")
            print(f"Error: {response.text[:500]}")
            return None, None, None
            
    except Exception as e:
        print(f"❌ POST DATA EXCEPTION: {e}")
        return None, None, None

def test_reactions_endpoint(reactions_urn):
    """Test getPostReactions endpoint"""
    print(f"\n🎯 TESTING REACTIONS ENDPOINT")
    print("=" * 50)
    
    if not reactions_urn:
        print("❌ No reactions URN available")
        return None
    
    try:
        response = requests.post(
            "https://linkedin-data-scraper.p.rapidapi.com/post_reactions",
            headers=HEADERS,
            json={
                "reactionsUrn": reactions_urn,
                "page": 1
            },
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ REACTIONS SUCCESS!")
            print(f"Response type: {type(data)}")
            
            if isinstance(data, dict):
                print(f"Response keys: {list(data.keys())}")
                reactions = data.get('reactions', [])
                print(f"Number of reactions: {len(reactions)}")
            elif isinstance(data, list):
                print(f"Number of reactions: {len(data)}")
                
            # Save response
            with open('test_data/reactions_api_response.json', 'w') as f:
                json.dump(data, f, indent=2)
            print(f"📁 Reactions response saved to test_data/reactions_api_response.json")
            
            return data
            
        else:
            print(f"❌ REACTIONS FAILED: {response.status_code}")
            print(f"Error: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"❌ REACTIONS EXCEPTION: {e}")
        return None

def test_comments_endpoint(comments_urn):
    """Test getPostComments endpoint"""
    print(f"\n💬 TESTING COMMENTS ENDPOINT")
    print("=" * 50)
    
    if not comments_urn:
        print("❌ No comments URN available")
        return None
    
    try:
        response = requests.post(
            "https://linkedin-data-scraper.p.rapidapi.com/post_comments",
            headers=HEADERS,
            json={
                "commentsUrn": comments_urn,
                "page": 1
            },
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ COMMENTS SUCCESS!")
            print(f"Response type: {type(data)}")
            
            if isinstance(data, dict):
                print(f"Response keys: {list(data.keys())}")
                comments = data.get('comments', [])
                print(f"Number of comments: {len(comments)}")
            elif isinstance(data, list):
                print(f"Number of comments: {len(data)}")
                
            # Save response
            with open('test_data/comments_api_response.json', 'w') as f:
                json.dump(data, f, indent=2)
            print(f"📁 Comments response saved to test_data/comments_api_response.json")
            
            return data
            
        else:
            print(f"❌ COMMENTS FAILED: {response.status_code}")
            print(f"Error: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"❌ COMMENTS EXCEPTION: {e}")
        return None

def test_api_key():
    """Quick API key validation"""
    print("🔑 TESTING API KEY VALIDITY")
    print("=" * 50)
    
    if not API_KEY:
        print("❌ No RAPIDAPI_KEY found in environment")
        return False
    
    print(f"✅ API Key loaded: {API_KEY[:10]}...{API_KEY[-4:]}")
    return True

def main():
    """Run comprehensive engagement API tests"""
    print("🚀 DIRECT ENGAGEMENT API TEST SUITE")
    print("=" * 80)
    
    # Ensure test_data directory exists
    os.makedirs('test_data', exist_ok=True)
    
    # Test 1: API Key validation
    if not test_api_key():
        print("❌ API key test failed - aborting")
        return
    
    # Test 2: Get post data with URNs
    reactions_urn, comments_urn, post_data = test_post_data_endpoint()
    
    # Small delay between requests
    time.sleep(2)
    
    # Test 3: Get reactions
    reactions_data = test_reactions_endpoint(reactions_urn)
    
    # Small delay between requests
    time.sleep(2)
    
    # Test 4: Get comments
    comments_data = test_comments_endpoint(comments_urn)
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 50)
    print(f"✅ Post Data: {'Success' if post_data else 'Failed'}")
    print(f"✅ Reactions: {'Success' if reactions_data else 'Failed'}")
    print(f"✅ Comments: {'Success' if comments_data else 'Failed'}")
    
    if reactions_data:
        reaction_count = len(reactions_data) if isinstance(reactions_data, list) else len(reactions_data.get('reactions', []))
        print(f"📈 Total reactions found: {reaction_count}")
    
    if comments_data:
        comment_count = len(comments_data) if isinstance(comments_data, list) else len(comments_data.get('comments', []))
        print(f"💬 Total comments found: {comment_count}")
    
    # Save summary
    summary = {
        "test_timestamp": time.time(),
        "post_data_success": bool(post_data),
        "reactions_success": bool(reactions_data),
        "comments_success": bool(comments_data),
        "reactions_urn": reactions_urn,
        "comments_urn": comments_urn,
        "reaction_count": len(reactions_data) if reactions_data and isinstance(reactions_data, list) else (len(reactions_data.get('reactions', [])) if reactions_data and isinstance(reactions_data, dict) else 0),
        "comment_count": len(comments_data) if comments_data and isinstance(comments_data, list) else (len(comments_data.get('comments', [])) if comments_data and isinstance(comments_data, dict) else 0)
    }
    
    with open('test_data/engagement_api_test_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"📁 Test summary saved to test_data/engagement_api_test_summary.json")

if __name__ == "__main__":
    main()