#!/usr/bin/env python3
"""
LinkedIn Post Discovery - Find relevant B2B/lead-gen posts
Part of the automated workflow to ensure we process only relevant content
"""

import json
import requests
import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

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

class PostDiscovery:
    """Discover and validate LinkedIn posts for lead generation"""
    
    def __init__(self):
        self.relevance_keywords = [
            'lead generation', 'b2b sales', 'sales development',
            'revenue operations', 'growth marketing', 'demand generation',
            'sales enablement', 'outbound sales', 'cold outreach',
            'sales automation', 'pipeline generation', 'saas sales',
            'gtm strategy', 'revenue growth', 'sales intelligence'
        ]
        
        self.minimum_engagement = 100  # Minimum reactions for relevance
        
    def search_influencer_posts(self, influencer_profile_url: str) -> List[Dict]:
        """Search recent posts from a specific influencer"""
        print(f"\n🔍 Searching posts from: {influencer_profile_url}")
        
        # Use the person endpoint to get recent activity
        endpoint = 'https://linkedin-data-scraper.p.rapidapi.com/person'
        
        try:
            response = requests.post(
                endpoint,
                headers=HEADERS,
                json={'link': influencer_profile_url}
            )
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                activities = data.get('activities', [])
                
                posts = []
                for activity in activities:
                    if activity.get('type') == 'post':
                        posts.append({
                            'url': activity.get('url'),
                            'content': activity.get('text', ''),
                            'posted_date': activity.get('postedDate'),
                            'reactions': activity.get('reactionsCount', 0),
                            'comments': activity.get('commentsCount', 0)
                        })
                
                print(f"✅ Found {len(posts)} posts from influencer")
                return posts
            else:
                print(f"❌ Error fetching influencer posts: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            return []
    
    def get_post_details(self, post_url: str) -> Optional[Dict]:
        """Get detailed information about a post"""
        endpoint = 'https://linkedin-data-scraper.p.rapidapi.com/post'
        
        try:
            response = requests.post(
                endpoint,
                headers=HEADERS,
                json={'link': post_url}
            )
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                
                return {
                    'url': post_url,
                    'content': data.get('content', ''),
                    'author': data.get('author', {}),
                    'reactions_count': data.get('reactionsCount', 0),
                    'comments_count': data.get('commentsCount', 0),
                    'shares_count': data.get('sharesCount', 0),
                    'total_engagement': (
                        data.get('reactionsCount', 0) + 
                        data.get('commentsCount', 0) + 
                        data.get('sharesCount', 0)
                    ),
                    'posted_date': data.get('postedDate'),
                    'reactions_urn': data.get('reactionsUrn'),
                    'comments_urn': data.get('commentsUrn')
                }
            else:
                print(f"❌ Error fetching post details: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            return None
    
    def is_relevant_post(self, post_details: Dict) -> Dict[str, Any]:
        """Check if post matches our lead generation criteria"""
        
        relevance_score = 0
        reasons = []
        
        # Check content relevance
        content = post_details.get('content', '').lower()
        matched_keywords = []
        
        for keyword in self.relevance_keywords:
            if keyword in content:
                matched_keywords.append(keyword)
                relevance_score += 10
        
        if matched_keywords:
            reasons.append(f"Contains relevant keywords: {', '.join(matched_keywords[:3])}")
        
        # Check engagement levels
        reactions = post_details.get('reactions_count', 0)
        comments = post_details.get('comments_count', 0)
        total_engagement = post_details.get('total_engagement', 0)
        
        if reactions >= self.minimum_engagement:
            relevance_score += 20
            reasons.append(f"High reactions: {reactions}")
        
        if comments >= 20:
            relevance_score += 15
            reasons.append(f"High comments: {comments}")
        
        if total_engagement >= 150:
            relevance_score += 10
            reasons.append(f"High total engagement: {total_engagement}")
        
        # Check author credibility
        author = post_details.get('author', {})
        if author.get('followersCount', 0) > 5000:
            relevance_score += 10
            reasons.append(f"Influential author: {author.get('followersCount', 0)} followers")
        
        # Final assessment
        is_relevant = relevance_score >= 30
        
        return {
            'is_relevant': is_relevant,
            'relevance_score': relevance_score,
            'reasons': reasons,
            'engagement_metrics': {
                'reactions': reactions,
                'comments': comments,
                'total': total_engagement
            }
        }
    
    def discover_posts(self, source_urls: List[str]) -> List[Dict]:
        """Discover relevant posts from multiple sources"""
        
        discovered_posts = []
        
        for url in source_urls:
            print(f"\n{'='*60}")
            print(f"Processing: {url}")
            
            # Check if it's a profile or post URL
            if '/in/' in url:
                # It's a profile - get their posts
                posts = self.search_influencer_posts(url)
                
                for post in posts:
                    time.sleep(30)  # Long delay between post lookups
                    
                    post_details = self.get_post_details(post['url'])
                    if post_details:
                        relevance = self.is_relevant_post(post_details)
                        
                        if relevance['is_relevant']:
                            discovered_posts.append({
                                'post': post_details,
                                'relevance': relevance,
                                'source': url
                            })
                            
                            print(f"\n✅ RELEVANT POST FOUND!")
                            print(f"URL: {post['url']}")
                            print(f"Score: {relevance['relevance_score']}")
                            print(f"Reasons: {'; '.join(relevance['reasons'])}")
                        else:
                            print(f"\n❌ Post not relevant (score: {relevance['relevance_score']})")
            
            elif '/feed/update/' in url:
                # It's a post URL - validate it directly
                post_details = self.get_post_details(url)
                if post_details:
                    relevance = self.is_relevant_post(post_details)
                    
                    discovered_posts.append({
                        'post': post_details,
                        'relevance': relevance,
                        'source': 'direct'
                    })
                    
                    print(f"\n{'✅ RELEVANT' if relevance['is_relevant'] else '❌ NOT RELEVANT'}")
                    print(f"Score: {relevance['relevance_score']}")
                    print(f"Reasons: {'; '.join(relevance['reasons'])}")
        
        return discovered_posts
    
    def save_discoveries(self, discoveries: List[Dict]) -> str:
        """Save discovered posts to file"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_data/discovered_posts_{timestamp}.json"
        
        output = {
            'discovery_timestamp': datetime.now().isoformat(),
            'total_discovered': len(discoveries),
            'relevant_posts': [d for d in discoveries if d['relevance']['is_relevant']],
            'all_posts': discoveries
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 Discoveries saved to: {filename}")
        return filename

def main():
    """Run post discovery"""
    
    if not API_KEY:
        print("❌ Error: RAPIDAPI_KEY not set")
        print("Run: export RAPIDAPI_KEY='your-key-here'")
        return
    
    print("🔍 LINKEDIN POST DISCOVERY")
    print("="*60)
    
    # Example sources (can be profiles or posts)
    sources = [
        # Known B2B influencers
        "https://www.linkedin.com/in/example-sales-influencer",
        # Specific posts to validate
        "https://www.linkedin.com/feed/update/urn:li:activity:7353758072894320642",
    ]
    
    # Allow command line arguments
    import sys
    if len(sys.argv) > 1:
        sources = sys.argv[1:]
    
    discovery = PostDiscovery()
    discoveries = discovery.discover_posts(sources)
    
    # Summary
    relevant = [d for d in discoveries if d['relevance']['is_relevant']]
    
    print(f"\n{'='*60}")
    print(f"📊 DISCOVERY SUMMARY:")
    print(f"Total posts analyzed: {len(discoveries)}")
    print(f"Relevant posts found: {len(relevant)}")
    
    if relevant:
        print(f"\n🎯 RECOMMENDED POSTS FOR PROCESSING:")
        for i, disc in enumerate(relevant, 1):
            post = disc['post']
            print(f"\n{i}. {post['url']}")
            print(f"   Engagement: {post['total_engagement']} (R:{post['reactions_count']} C:{post['comments_count']})")
            print(f"   Score: {disc['relevance']['relevance_score']}")
    
    # Save results
    if discoveries:
        discovery.save_discoveries(discoveries)

if __name__ == "__main__":
    main()