#!/usr/bin/env python3
"""
Show actual data examined vs what was processed
"""

import json

def show_actual_data():
    print("📋 ACTUAL DATA EXAMINATION SUMMARY")
    print("=" * 60)
    
    # 1. Source Data
    with open('test_data/full_engagement_20250727_182551.json', 'r') as f:
        source_data = json.load(f)
    
    print(f"🔍 SOURCE DATA (what we have):")
    print(f"  Reactions: {len(source_data['reactions'])}")
    print(f"  Comments: {len(source_data['comments'])}")
    print(f"  Total: {len(source_data['reactions']) + len(source_data['comments'])}")
    
    # 2. Processed Data
    with open('test_data/final_llm_results_191539.json', 'r') as f:
        processed_data = json.load(f)
    
    print(f"\n🤖 PROCESSED DATA (what LLM analyzed):")
    print(f"  Total leads: {processed_data['total_leads']}")
    print(f"  Reactions: {processed_data['engagement_breakdown']['reactions']['total']}")
    print(f"  Comments: {processed_data['engagement_breakdown']['comments']['total']}")
    
    # 3. Sample of actual source data
    print(f"\n📝 SAMPLE SOURCE REACTIONS (first 3):")
    for i, reaction in enumerate(source_data['reactions'][:3]):
        name = reaction.get('title', 'Unknown')
        subtitle = reaction.get('subtitle', '')
        print(f"  {i+1}. {name}")
        print(f"     Subtitle: {subtitle[:100]}...")
    
    print(f"\n💬 SAMPLE SOURCE COMMENTS (first 3):")
    for i, comment in enumerate(source_data['comments'][:3]):
        commenter = comment.get('commenter', {})
        name = commenter.get('title', 'Unknown')
        subtitle = commenter.get('subtitle', '')
        text = comment.get('text', '')[:50]
        print(f"  {i+1}. {name}")
        print(f"     Subtitle: {subtitle[:80]}...")
        print(f"     Comment: {text}...")
    
    # 4. What was actually processed
    print(f"\n🎯 WHAT LLM ACTUALLY PROCESSED:")
    qualified_leads = processed_data['qualified_only']
    print(f"  Top 5 qualified leads:")
    for i, lead in enumerate(qualified_leads[:5]):
        print(f"  {i+1}. {lead['name']} - {lead['title'][:50]}...")
        print(f"     Score: {lead.get('llm_score', 'N/A')}/100")
        print(f"     Reasoning: {lead.get('llm_reasoning', 'N/A')[:80]}...")
    
    # 5. Missing data calculation
    print(f"\n❌ MISSING DATA:")
    print(f"  Missing reactions: {len(source_data['reactions']) - processed_data['engagement_breakdown']['reactions']['total']}")
    print(f"  Missing comments: {len(source_data['comments']) - processed_data['engagement_breakdown']['comments']['total']}")
    print(f"  Total missing: {(len(source_data['reactions']) + len(source_data['comments'])) - processed_data['total_leads']}")
    
    # 6. Quality issues found
    print(f"\n⚠️ QUALITY ISSUES IDENTIFIED:")
    service_providers = 0
    for lead in qualified_leads:
        title = lead['title'].lower()
        if any(word in title for word in ['helping', 'consultant', 'coach']):
            service_providers += 1
    
    print(f"  Service providers scored as qualified: {service_providers}")
    print(f"  High scores (90+): {len([l for l in processed_data['all_leads'] if l.get('llm_score', 0) >= 90])}")
    print(f"  CEO/Founders: {len([l for l in qualified_leads if 'ceo' in l['title'].lower() or 'founder' in l['title'].lower()])}")
    
    print(f"\n🎯 CONCLUSION:")
    print(f"✅ I examined both source data (195 leads) and processed results (120 leads)")
    print(f"❌ 75 leads missing from analysis (38% data loss)")
    print(f"❌ ALL 52 comments missing (highest value prospects)")
    print(f"⚠️ Quality issues: service providers getting high scores")
    print(f"🔧 Need to fix: complete processing + better qualification criteria")

if __name__ == "__main__":
    show_actual_data()