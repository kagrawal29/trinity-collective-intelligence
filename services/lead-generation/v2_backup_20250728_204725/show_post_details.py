#!/usr/bin/env python3
"""
Display post details for user review
"""

import json
from datetime import datetime

def analyze_post_sample():
    """Show example of what we're looking for in posts"""
    
    print("📋 POST DETAILS TEMPLATE")
    print("="*60)
    
    example_post = {
        "url": "https://www.linkedin.com/feed/update/urn:li:activity:7353758072894320642",
        "text": """🚀 Just helped a B2B SaaS company 3x their qualified leads in 90 days!

Here's what we did:
1. Implemented Clay for data enrichment
2. Built custom lead scoring with AI
3. Automated outreach sequences
4. A/B tested messaging strategies

The result? Their sales team is now talking to 3x more qualified prospects, 
and close rates improved by 40%.

What's your biggest challenge with lead generation? Drop a comment below! 👇

#B2BSales #LeadGeneration #SalesAutomation #RevOps""",
        "engagement": {
            "reactions": 146,
            "comments": 62,
            "total": 208
        },
        "qualification_criteria": {
            "target_audience": "B2B companies, SaaS teams",
            "relevant_topics": "Lead generation, sales automation",
            "engagement_quality": "Decision-makers discussing strategies",
            "action_triggers": "Question prompts engagement"
        }
    }
    
    print("🎯 EXAMPLE POST STRUCTURE:")
    print(f"URL: {example_post['url']}")
    print(f"\nContent Preview:")
    print(f"{example_post['text'][:200]}...")
    print(f"\nEngagement:")
    print(f"  Reactions: {example_post['engagement']['reactions']}")
    print(f"  Comments: {example_post['engagement']['comments']}")
    print(f"  Total: {example_post['engagement']['total']}")
    
    print(f"\n🎯 QUALIFICATION CRITERIA:")
    for key, value in example_post['qualification_criteria'].items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print(f"\n💡 Tyler should share:")
    print("1. Specific post URL from Suprava's 8 posts")
    print("2. Post content/text")
    print("3. Engagement numbers (reactions, comments)")
    print("4. Why this post is good for lead generation")

if __name__ == "__main__":
    analyze_post_sample()