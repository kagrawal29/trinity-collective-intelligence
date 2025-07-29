#!/usr/bin/env python3
"""
Debug Data Loading - Find missing leads in batch processing
"""

import json

def debug_data_loading():
    """Debug why batch analyzer misses leads"""
    
    # Load engagement data 
    with open('test_data/full_engagement_20250727_182551.json', 'r') as f:
        data = json.load(f)
    
    print("🔍 DEBUGGING DATA LOADING")
    print("=" * 50)
    
    reactions = data.get('reactions', [])
    comments = data.get('comments', [])
    
    print(f"Raw data counts:")
    print(f"  Reactions: {len(reactions)}")
    print(f"  Comments: {len(comments)}")
    print(f"  Total: {len(reactions) + len(comments)}")
    
    # Simulate batch analyzer logic
    leads = []
    reaction_urls = set()
    comment_urls = set()
    
    # Process reactions (same logic as batch analyzer)
    valid_reactions = 0
    for reaction in reactions:
        name = reaction.get('title', 'Unknown')
        subtitle = reaction.get('subtitle', '')
        url = reaction.get('navigationUrl', '')
        
        if url:  # Only count if has URL
            valid_reactions += 1
            reaction_urls.add(url)
            
        # Parse subtitle
        if '|' in subtitle:
            parts = subtitle.split('|', 1)
            title = parts[0].strip()
            company = parts[1].strip()
        else:
            title = subtitle
            company = ''
        
        leads.append({
            'name': name,
            'title': title,
            'company': company,
            'linkedin_url': url,
            'engagement_type': 'reaction',
            'source': 'reaction'
        })
    
    # Process comments (same logic as batch analyzer)
    valid_comments = 0
    for comment in comments:
        commenter = comment.get('commenter', {})
        name = commenter.get('title', 'Unknown')
        subtitle = commenter.get('subtitle', '')
        url = commenter.get('navigationUrl', '')
        
        if url:  # Only count if has URL
            valid_comments += 1
            comment_urls.add(url)
        
        # Parse subtitle
        if '|' in subtitle:
            parts = subtitle.split('|', 1)
            title = parts[0].strip()
            company = parts[1].strip()
        else:
            title = subtitle
            company = ''
        
        leads.append({
            'name': name,
            'title': title,
            'company': company,
            'linkedin_url': url,
            'engagement_type': 'comment',
            'source': 'comment'
        })
    
    print(f"\nAfter processing:")
    print(f"  Valid reactions (with URLs): {valid_reactions}")
    print(f"  Valid comments (with URLs): {valid_comments}")
    print(f"  Total leads created: {len(leads)}")
    
    # Check for overlaps
    url_overlap = reaction_urls.intersection(comment_urls)
    print(f"  URL overlap (same person in both): {len(url_overlap)}")
    
    # Check for empty URLs
    empty_url_reactions = sum(1 for r in reactions if not r.get('navigationUrl'))
    empty_url_comments = sum(1 for c in comments if not c.get('commenter', {}).get('navigationUrl'))
    
    print(f"\nData quality issues:")
    print(f"  Reactions with empty URLs: {empty_url_reactions}")
    print(f"  Comments with empty URLs: {empty_url_comments}")
    
    # Sample missing URLs
    print(f"\nSample reactions without URLs:")
    for i, reaction in enumerate(reactions[:5]):
        url = reaction.get('navigationUrl', '')
        name = reaction.get('title', 'Unknown')
        print(f"  {i+1}. {name}: URL='{url}'")
    
    print(f"\nSample comments without URLs:")
    for i, comment in enumerate(comments[:5]):
        url = comment.get('commenter', {}).get('navigationUrl', '')
        name = comment.get('commenter', {}).get('title', 'Unknown')
        print(f"  {i+1}. {name}: URL='{url}'")

if __name__ == "__main__":
    debug_data_loading()