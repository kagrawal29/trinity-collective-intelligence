#!/usr/bin/env python3
"""
Profile Post Discovery - Get posts from influencer profiles with database storage
Uses correct API catalog flow: GET /profile_updates
Stores posts and qualification results in SQLite database
"""

import json
import requests
import os
import time
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
from qualify_post_llm import PostQualificationLLM
from logging_system_sqlite import V2LoggingSystemSQLite

# Load environment
load_dotenv('../.env')

API_KEY = os.getenv('RAPIDAPI_KEY')

HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'linkedin-data-scraper.p.rapidapi.com',
    'Content-Type': 'application/json'
}

class ProfilePostDiscovery:
    """Discover and qualify posts from influencer profiles with database storage"""
    
    def __init__(self):
        self.qualifier = PostQualificationLLM()
        self.logger = V2LoggingSystemSQLite()
        self.test_data_dir = "test_data"
        os.makedirs(self.test_data_dir, exist_ok=True)
        
        # Initialize database
        self.logger.connect_database()
        
        # Register prompt version for post qualification
        self.prompt_version = self.logger.register_prompt_version(
            version_tag="post_qualification_v1.0",
            prompt_content=self.qualifier.prompt_template,
            tier_definitions={
                "QUALIFIED": {"threshold": 70, "description": "Posts suitable for lead generation"},
                "NOT_QUALIFIED": {"threshold": 70, "description": "Posts below qualification threshold"}
            },
            scoring_rules={
                "target_audience_weight": 25,
                "topic_relevance_weight": 25, 
                "lead_quality_weight": 25,
                "action_trigger_weight": 25,
                "qualification_threshold": 70
            }
        )
    
    def get_profile_posts(self, profile_url: str, max_pages: int = 3) -> List[Dict]:
        """Get posts from a profile using correct API catalog flow"""
        
        print(f"\n👤 Fetching posts from profile: {profile_url}")
        all_posts = []
        
        for page in range(1, max_pages + 1):
            print(f"\n📄 Fetching page {page}...")
            
            try:
                time.sleep(30)  # Long delay to avoid rate limits
                
                # Use GET /profile_updates as per API catalog
                response = requests.get(
                    "https://linkedin-data-scraper.p.rapidapi.com/profile_updates",
                    params={
                        "profile_url": profile_url,
                        "page": page,
                        "paginationToken": ""  # Empty for first page
                    },
                    headers=HEADERS,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get('posts', [])  # Tyler's successful format uses 'posts' key
                    
                    if not posts:
                        print(f"  No posts on page {page}")
                        break
                    
                    print(f"  Found {len(posts)} posts on page {page}")
                    all_posts.extend(posts)
                    
                    # Check if there's pagination token for next page
                    pagination_token = data.get('paginationToken')
                    if not pagination_token:
                        print(f"  No more pages after {page}")
                        break
                        
                else:
                    print(f"❌ Error on page {page}: {response.status_code} - {response.text[:200]}")
                    break
                    
            except Exception as e:
                print(f"❌ Exception on page {page}: {e}")
                break
        
        print(f"\n✅ Total posts found: {len(all_posts)}")
        return all_posts
    
    def qualify_and_store_posts(self, posts: List[Dict], influencer_id: int, 
                               qualification_threshold: int = 70) -> List[Dict]:
        """Qualify posts using LLM, store in database, and filter by score"""
        
        print(f"\n🎯 Qualifying and storing {len(posts)} posts...")
        qualified_posts = []
        
        # Start processing run
        run_id = self.logger.start_processing_run(
            run_type="post_qualification",
            prompt_version_hash=self.prompt_version,
            total_leads=len(posts)
        )
        
        for i, post in enumerate(posts, 1):
            start_time = time.time()
            
            # Extract post content and metadata (Tyler's successful format)
            post_content = post.get('postText', '') or post.get('text', '') or post.get('content', '')
            post_url = post.get('postLink', '') or post.get('url', '') or post.get('permalink', '')
            post_type = post.get('type', 'text')
            
            # Extract engagement from Tyler's format
            social_count = post.get('socialCount', {})
            reactions_count = social_count.get('numLikes', 0)
            comments_count = social_count.get('numComments', 0)
            
            if not post_content:
                print(f"  Post {i}: No content found, skipping")
                continue
            
            print(f"\n  Post {i}: Processing...")
            print(f"    Content preview: {post_content[:100]}...")
            print(f"    URL: {post_url}")
            
            # Step 1: Store post in database
            post_id = self.logger.register_post(
                post_url=post_url,
                total_reactions=reactions_count,
                total_comments=comments_count,
                post_content=post_content,
                influencer_id=influencer_id
            )
            
            # Step 2: Qualify with LLM
            qualification = self.qualifier.qualify_post(post_content, post_url)
            score = qualification.get('overall_score', 0)
            
            print(f"    Score: {score}/100")
            print(f"    Status: {qualification.get('qualification', 'UNKNOWN')}")
            print(f"    Reasoning: {qualification.get('reasoning', 'N/A')}")
            
            # Step 3: Store qualification results in database
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Log qualification in dedicated post_qualifications table
            qualification_id = self.logger.log_post_qualification(
                post_id=post_id,
                qualification_result=qualification,
                processing_time_ms=execution_time_ms
            )
            
            # Also log the processing step for workflow tracking
            self.logger.log_processing_step(
                workflow_step="post_qualification",
                input_data={
                    "post_url": post_url,
                    "post_content": post_content[:200] + "..." if len(post_content) > 200 else post_content
                },
                output_data=qualification,
                processing_params={
                    "model": qualification.get('model_used', 'gpt-4o-mini'),
                    "threshold": qualification_threshold,
                    "qualification_id": qualification_id
                },
                execution_time_ms=execution_time_ms,
                status="success" if score >= 0 else "error",
                leads_processed=1,
                leads_qualified=1 if score >= qualification_threshold else 0
            )
            
            # Step 4: Filter qualified posts
            if score >= qualification_threshold:
                # Add qualification data and database IDs to post
                post['qualification'] = qualification
                post['post_id'] = post_id
                post['influencer_id'] = influencer_id
                qualified_posts.append(post)
                print(f"    ✅ QUALIFIED!")
            else:
                print(f"    ❌ Not qualified (threshold: {qualification_threshold})")
        
        # Complete processing run
        qualification_rate = (len(qualified_posts) / len(posts) * 100) if posts else 0
        self.logger.complete_processing_run(len(qualified_posts), qualification_rate)
        
        print(f"\n📊 Qualification Results:")
        print(f"  Total posts: {len(posts)}")
        print(f"  Qualified: {len(qualified_posts)}")
        print(f"  Qualification rate: {qualification_rate:.1f}%")
        print(f"  Database run ID: {run_id}")
        
        return qualified_posts
    
    def save_results(self, profile_url: str, all_posts: List[Dict], qualified_posts: List[Dict]) -> str:
        """Save discovery results to file"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"profile_discovery_{timestamp}.json"
        filepath = os.path.join(self.test_data_dir, filename)
        
        results = {
            "profile_url": profile_url,
            "discovery_timestamp": datetime.now().isoformat(),
            "total_posts_found": len(all_posts),
            "qualified_posts_count": len(qualified_posts),
            "qualification_rate": len(qualified_posts)/len(all_posts)*100 if all_posts else 0,
            "all_posts": all_posts,
            "qualified_posts": qualified_posts
        }
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: {filepath}")
        return filepath
    
    def discover_qualified_posts(self, profile_url: str, qualification_threshold: int = 70) -> Dict:
        """Complete workflow: discover → store → qualify → filter posts with full database logging"""
        
        print(f"\n🔍 PROFILE POST DISCOVERY WORKFLOW WITH DATABASE STORAGE")
        print(f"Profile: {profile_url}")
        print(f"Qualification threshold: {qualification_threshold}")
        print("="*80)
        
        # Step 1: Register influencer in database
        print(f"\n👤 Registering influencer...")
        influencer_name = profile_url.split('/')[-1].replace('-', ' ').title() if profile_url else "Unknown"
        influencer_id = self.logger.register_influencer(
            influencer_name=influencer_name,
            profile_url=profile_url,
            industry="B2B Lead Generation",
            tier="verified"  # Since we're manually selecting them
        )
        
        # Step 2: Get posts from profile
        print(f"\n📱 Fetching posts from profile...")
        all_posts = self.get_profile_posts(profile_url)
        
        if not all_posts:
            print("❌ No posts found!")
            return {
                "profile_url": profile_url,
                "influencer_id": influencer_id,
                "total_posts": 0,
                "qualified_posts": [],
                "error": "No posts found"
            }
        
        # Step 3: Qualify posts with LLM and store in database
        print(f"\n🎯 Starting LLM qualification and database storage...")
        qualified_posts = self.qualify_and_store_posts(all_posts, influencer_id, qualification_threshold)
        
        # Step 4: Save results to file for backup
        results_file = self.save_results(profile_url, all_posts, qualified_posts)
        
        # Step 5: Log summary
        print(f"\n📊 WORKFLOW COMPLETE:")
        print(f"  Influencer ID: {influencer_id}")
        print(f"  Posts stored in DB: {len(all_posts)}")
        print(f"  Posts qualified: {len(qualified_posts)}")
        print(f"  Qualification rate: {len(qualified_posts)/len(all_posts)*100 if all_posts else 0:.1f}%")
        print(f"  Database logging: ✅ Complete")
        print(f"  File backup: {results_file}")
        
        # Return summary
        return {
            "profile_url": profile_url,
            "influencer_id": influencer_id,
            "total_posts": len(all_posts),
            "qualified_posts": qualified_posts,
            "qualification_rate": len(qualified_posts)/len(all_posts)*100 if all_posts else 0,
            "results_file": results_file,
            "database_stored": True
        }

def main():
    """Test profile post discovery with Suprava"""
    
    # Test with Suprava's profile (from our DB)
    suprava_url = "https://linkedin.com/in/suprava-sabat-saasleadgen"
    
    discovery = ProfilePostDiscovery()
    results = discovery.discover_qualified_posts(suprava_url, qualification_threshold=70)
    
    print(f"\n🎯 DISCOVERY COMPLETE!")
    print(f"Qualified posts: {len(results.get('qualified_posts', []))}")
    if 'qualification_rate' in results:
        print(f"Qualification rate: {results['qualification_rate']:.1f}%")
    else:
        print(f"No posts found to qualify")
    
    # Show qualified posts
    for i, post in enumerate(results['qualified_posts'], 1):
        qualification = post.get('qualification', {})
        print(f"\n{i}. Score: {qualification.get('overall_score', 'N/A')}")
        print(f"   URL: {post.get('url', 'N/A')}")
        print(f"   Reasoning: {qualification.get('reasoning', 'N/A')}")

if __name__ == "__main__":
    main()