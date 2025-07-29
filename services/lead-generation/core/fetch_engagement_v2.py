#!/usr/bin/env python3
"""
Enhanced Engagement Fetcher - Supports multiple posts with full metadata
"""

import json
import requests
import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import sys

# Load from .env file
from dotenv import load_dotenv
load_dotenv('../.env')

# Configuration
API_KEY = os.getenv('RAPIDAPI_KEY', '')

HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'linkedin-data-scraper.p.rapidapi.com',
    'Content-Type': 'application/json'
}

class EnhancedEngagementFetcher:
    """Fetch engagement data with post metadata and attribution"""
    
    def __init__(self):
        self.test_data_dir = "test_data"
        os.makedirs(self.test_data_dir, exist_ok=True)
    
    def _create_empty_result(self, post_url: str, timestamp: datetime) -> Dict:
        """Create empty result when API calls fail"""
        return {
            "post_url": post_url,
            "fetch_timestamp": timestamp.isoformat(),
            "post_details": self.fetch_post_details(post_url),
            "total_reactions": 0,
            "total_comments": 0,
            "total_engagement": 0,
            "reactions": [],
            "comments": []
        }
        
    def fetch_post_details(self, post_url: str, post_data: Optional[Dict] = None) -> Dict:
        """Fetch post content and metadata"""
        print(f"\n📄 Fetching post details for: {post_url}")
        
        # Extract activity ID from URL
        activity_id = post_url.split(':')[-1] if 'activity' in post_url else None
        
        # If post_data is provided from previous API call, use it
        if post_data:
            actor = post_data.get('actor', {})
            social_count = post_data.get('socialCount', {})
            
            return {
                "post_url": post_url,
                "activity_id": activity_id,
                "post_content": post_data.get('postText', ''),
                "post_type": "text" if post_data.get('postText') else "image",
                "posted_date": post_data.get('postedAt', datetime.now().isoformat()),
                "hashtags": [],  # Could extract from postText
                "mentions": [],  # Could extract from postText
                "social_count": {
                    "likes": social_count.get('numLikes', 0),
                    "comments": social_count.get('numComments', 0),
                    "shares": social_count.get('numShares', 0)
                },
                "influencer": {
                    "name": actor.get('actorName', 'Unknown'),
                    "profile_url": actor.get('actorLink', ''),
                    "description": actor.get('actorDescription', ''),
                    "image": actor.get('actorImage', '')
                }
            }
        
        # Fallback for backward compatibility
        return {
            "post_url": post_url,
            "activity_id": activity_id,
            "post_content": "[Post content would be fetched here]",
            "post_type": "text",
            "posted_date": datetime.now().isoformat(),
            "hashtags": [],
            "mentions": [],
            "influencer": {
                "name": "LinkedIn Influencer",
                "profile_url": "https://linkedin.com/in/influencer",
                "followers": 50000,
                "industry": "B2B Sales & Marketing"
            }
        }
    
    def fetch_engagement_data(self, post_url: str) -> Dict:
        """Fetch reactions and comments for a post using correct URN flow"""
        print(f"\n🎯 Fetching engagement data for: {post_url}")
        
        timestamp = datetime.now()
        all_reactions = []
        all_comments = []
        
        # Step 1: Get post data and URNs
        print("\n📄 Getting post URNs...")
        try:
            time.sleep(15)  # Rate limiting
            
            response = requests.post(
                "https://linkedin-data-scraper.p.rapidapi.com/post",
                json={"link": post_url},
                headers=HEADERS,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"❌ Error getting post URNs: {response.status_code}")
                return self._create_empty_result(post_url, timestamp)
            
            post_data = response.json().get('data', {})
            reactions_urn = post_data.get('reactionsUrn')
            comments_urn = post_data.get('commentsUrn')
            
            if not reactions_urn or not comments_urn:
                print(f"❌ Missing URNs in response: {post_data}")
                return self._create_empty_result(post_url, timestamp)
            
            print(f"✅ Got URNs - reactions: {reactions_urn[:50]}..., comments: {comments_urn[:50]}...")
            
        except Exception as e:
            print(f"❌ Exception getting URNs: {e}")
            return self._create_empty_result(post_url, timestamp)
        
        # Step 2: Fetch reactions using URN
        print("\n📊 Fetching reactions with URN...")
        print(f"Expected reactions to fetch: {post_data.get('socialCount', {}).get('numLikes', 'unknown')}")
        page = 1
        max_pages = 50  # Safety limit to prevent infinite loops
        
        while page <= max_pages:
            try:
                time.sleep(15)  # Rate limiting between pages
                
                print(f"  📄 Fetching reactions page {page}...")
                response = requests.post(
                    "https://linkedin-data-scraper.p.rapidapi.com/post_reactions",
                    json={"reactionsUrn": reactions_urn, "page": page},
                    headers=HEADERS,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    reactions = data.get('reactions', [])
                    
                    if not reactions:
                        print(f"  ✅ No more reactions on page {page} - stopping")
                        break
                    
                    all_reactions.extend(reactions)
                    print(f"  ✅ Page {page}: {len(reactions)} reactions (total: {len(all_reactions)})")
                    
                    # Continue to next page if we got a full page of results
                    if len(reactions) >= 5:  # Continue if we got meaningful results
                        page += 1
                        continue
                    else:
                        print(f"  ✅ Partial page ({len(reactions)} reactions) - likely last page")
                        break
                        
                else:
                    print(f"❌ Error fetching reactions page {page}: {response.status_code} - {response.text[:100]}")
                    break
                    
            except Exception as e:
                print(f"❌ Exception on reactions page {page}: {e}")
                break
        
        # Step 3: Fetch comments using URN
        print("\n💬 Fetching comments with URN...")
        print(f"Expected comments to fetch: {post_data.get('socialCount', {}).get('numComments', 'unknown')}")
        page = 1
        max_pages = 20  # Comments typically have fewer pages
        
        while page <= max_pages:
            try:
                time.sleep(20)  # Longer delay for comments
                
                print(f"  📄 Fetching comments page {page}...")
                response = requests.post(
                    "https://linkedin-data-scraper.p.rapidapi.com/post_comments",
                    json={"commentsUrn": comments_urn, "page": page},
                    headers=HEADERS,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    comments = data.get('comments', [])
                    
                    if not comments:
                        print(f"  ✅ No more comments on page {page} - stopping")
                        break
                    
                    all_comments.extend(comments)
                    print(f"  ✅ Page {page}: {len(comments)} comments (total: {len(all_comments)})")
                    
                    # Continue to next page if we got a full page of results
                    if len(comments) >= 5:  # Continue if we got meaningful results
                        page += 1
                        continue
                    else:
                        print(f"  ✅ Partial page ({len(comments)} comments) - likely last page")
                        break
                        
                else:
                    print(f"❌ Error fetching comments page {page}: {response.status_code} - {response.text[:100]}")
                    break
                    
            except Exception as e:
                print(f"❌ Exception on comments page {page}: {e}")
                break
        
        # Get post details (pass the post_data we already fetched)
        post_details = self.fetch_post_details(post_url, post_data)
        
        # Combine everything
        result = {
            "post_url": post_url,
            "fetch_timestamp": timestamp.isoformat(),
            "post_details": post_details,
            "total_reactions": len(all_reactions),
            "total_comments": len(all_comments),
            "total_engagement": len(all_reactions) + len(all_comments),
            "reactions": all_reactions,
            "comments": all_comments
        }
        
        # Save to file
        filename = f"engagement_{post_url.split(':')[-1]}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.test_data_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved to: {filepath}")
        print(f"\n📊 SUMMARY:")
        print(f"  Total Reactions: {len(all_reactions)}")
        print(f"  Total Comments: {len(all_comments)}")
        print(f"  Total Engagement: {len(all_reactions) + len(all_comments)}")
        
        return result

def main():
    """Run engagement fetcher for multiple posts"""
    
    if not API_KEY:
        print("❌ Error: RAPIDAPI_KEY not set")
        print("Run: export RAPIDAPI_KEY='your-key-here'")
        return
    
    # Support multiple posts
    posts = [
        "https://www.linkedin.com/feed/update/urn:li:activity:7353758072894320642",
        # Add more posts here
    ]
    
    # Allow command line argument
    if len(sys.argv) > 1:
        posts = [sys.argv[1]]
    
    fetcher = EnhancedEngagementFetcher()
    
    for post_url in posts:
        print(f"\n{'='*60}")
        print(f"Processing: {post_url}")
        print(f"{'='*60}")
        
        try:
            result = fetcher.fetch_engagement_data(post_url)
            print(f"\n✅ Successfully fetched engagement for post")
        except Exception as e:
            print(f"\n❌ Failed to fetch engagement: {e}")
    
    print("\n✅ All posts processed!")

if __name__ == "__main__":
    main()