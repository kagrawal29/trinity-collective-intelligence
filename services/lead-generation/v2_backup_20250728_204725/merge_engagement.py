#!/usr/bin/env python3
"""
Merge Reactions and Comments into Single Engagement Dataset
Prepare for comprehensive analysis
"""

import json
import os
from datetime import datetime

def merge_engagement_data():
    """Merge reactions and comments into single file"""
    
    # Load reactions
    reactions_file = 'test_data/all_reactions_20250727_182155.json'
    comments_file = 'test_data/all_comments_20250727_182323.json'
    
    print("🔄 MERGING ENGAGEMENT DATA")
    print("=" * 60)
    
    # Load reactions
    with open(reactions_file, 'r') as f:
        reactions_data = json.load(f)
    
    # Load comments
    with open(comments_file, 'r') as f:
        comments_data = json.load(f)
    
    # Extract data
    reactions = reactions_data.get('reactions', [])
    comments = comments_data.get('comments', [])  # Comments are directly under 'comments'
    
    print(f"✅ Loaded {len(reactions)} reactions")
    print(f"✅ Loaded {len(comments)} comments")
    
    # Create merged dataset
    merged_data = {
        'post_url': reactions_data.get('post_url', ''),
        'fetch_timestamp': datetime.now().isoformat(),
        'total_reactions': len(reactions),
        'total_comments': len(comments),
        'total_engagement': len(reactions) + len(comments),
        'reactions': reactions,
        'comments': comments
    }
    
    # Save merged file
    output_file = f'test_data/full_engagement_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w') as f:
        json.dump(merged_data, f, indent=2)
    
    print(f"\n💾 Saved merged data to: {output_file}")
    print(f"📊 Total engagement: {merged_data['total_engagement']} people")
    
    return output_file

if __name__ == "__main__":
    merged_file = merge_engagement_data()
    print(f"\n✅ MERGE COMPLETE! Run: python3 analyze_full_engagement.py")