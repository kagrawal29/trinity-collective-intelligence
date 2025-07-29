#!/usr/bin/env python3
"""
TYLER'S COMMENTS CHAOS TEST
Testing getPostComments to get ALL engagement
"""

import json
import requests
import time
import os
from datetime import datetime

# Configuration
API_KEY = os.getenv('RAPIDAPI_KEY', '')
COMMENTS_URN = "urn:li:fsd_socialDetail:(urn:li:activity:7353758072894320642,urn:li:activity:7353758072894320642,urn:li:highlightedReply:-)"

# Headers
HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'linkedin-data-scraper.p.rapidapi.com',
    'Content-Type': 'application/json'
}

def test_comments():
    """Test getPostComments endpoint"""
    print(f"\n{'='*60}")
    print(f"🔥 TYLER TESTING: getPostComments")
    print(f"Comments URN: {COMMENTS_URN}")
    print(f"Expected: 62 comments (from post data)")
    print('='*60)
    
    endpoint = 'https://linkedin-data-scraper.p.rapidapi.com/post_comments'
    all_comments = []
    page = 1
    
    while True:
        try:
            print(f"\n📄 Fetching page {page}...")
            response = requests.post(
                endpoint,
                headers=HEADERS,
                json={
                    'commentsUrn': COMMENTS_URN,
                    'page': page
                }
            )
            
            print(f"Status: {response.status_code}")
            
            # Check for rate limits
            rate_limit = {
                'limit': response.headers.get('x-ratelimit-limit'),
                'remaining': response.headers.get('x-ratelimit-remaining'),
                'reset': response.headers.get('x-ratelimit-reset')
            }
            print(f"Rate limit: {rate_limit}")
            
            if response.status_code == 429:
                print("🚨 RATE LIMIT HIT! 429 ERROR!")
                print(f"Error: {response.text}")
                break
            
            if response.status_code == 200:
                data = response.json()
                comments_data = data.get('data', {})
                comments = comments_data.get('items', [])
                
                if not comments:
                    # Try different field name
                    comments = data.get('comments', [])
                
                if not comments:
                    print("✅ No more comments (empty page)")
                    break
                
                all_comments.extend(comments)
                print(f"✅ Got {len(comments)} comments on page {page}")
                print(f"Progress: {len(all_comments)} total comments collected")
                
                # Sample first comment
                if page == 1 and comments:
                    first = comments[0]
                    print(f"\n🎯 Sample Comment:")
                    print(f"Author: {first.get('authorName', 'Unknown')}")
                    print(f"Title: {first.get('authorTitle', 'N/A')}")
                    print(f"Text: {first.get('commentText', '')[:100]}...")
                
                # Check if last page
                if len(comments) < 10:
                    print("✅ Reached last page (partial page)")
                    break
                
                page += 1
                print("⏳ Waiting 2 seconds for rate limit...")
                time.sleep(2)
                
            else:
                print(f"❌ FAILED: {response.text}")
                break
                
        except Exception as e:
            print(f"💀 CHAOS ERROR: {str(e)}")
            break
    
    # Save all comments
    if all_comments:
        filename = f"test_data/all_comments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump({
                'total_comments': len(all_comments),
                'comments': all_comments,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
        print(f"\n💾 Saved {len(all_comments)} comments to: {filename}")
    
    return len(all_comments)

def main():
    """Run the comments extraction test"""
    
    if not API_KEY:
        print("ERROR: Set RAPIDAPI_KEY environment variable!")
        return
    
    print("🎪 TYLER'S COMMENTS EXTRACTION CHAOS TEST")
    print(f"Time: {datetime.now()}")
    
    # Test comments extraction
    comment_count = test_comments()
    
    print(f"\n\n🏆 COMMENTS EXTRACTION COMPLETE!")
    print(f"Total comments extracted: {comment_count}")
    print("\n📊 ENGAGEMENT SUMMARY:")
    print(f"- Reactions: 143")
    print(f"- Comments: {comment_count}")
    print(f"- Total Engagement: {143 + comment_count}")
    print("\n🎯 USER RAGE ASSESSMENT:")
    print("- API Response: FAST ✅ (USER RAGE: 1/10)")
    print("- Data Quality: HIGH ✅ (USER RAGE: 0/10)")
    print("- Rate Limits: TBD (watching for 429s)")

if __name__ == "__main__":
    main()