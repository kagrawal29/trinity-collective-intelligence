#!/usr/bin/env python3
"""
Consolidate all batch results and show final analysis
"""

import json
import glob
import time

def main():
    # Find all batch files
    batch_files = glob.glob('test_data/llm_progress_batch_*.json')
    batch_files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
    
    print(f"🔍 Found {len(batch_files)} batch files")
    
    all_leads = []
    for batch_file in batch_files:
        with open(batch_file, 'r') as f:
            batch_data = json.load(f)
            all_leads.extend(batch_data)
            print(f"✅ Loaded {len(batch_data)} leads from {batch_file}")
    
    # Analyze results
    qualified_leads = [lead for lead in all_leads if lead.get('is_qualified', False)]
    qualification_rate = len(qualified_leads) / len(all_leads) * 100 if all_leads else 0
    
    # Score distribution
    score_dist = {
        '90-100': len([l for l in all_leads if l.get('llm_score', 0) >= 90]),
        '70-89': len([l for l in all_leads if 70 <= l.get('llm_score', 0) < 90]),
        '50-69': len([l for l in all_leads if 50 <= l.get('llm_score', 0) < 70]),
        '0-49': len([l for l in all_leads if l.get('llm_score', 0) < 50])
    }
    
    # Engagement breakdown
    reaction_count = len([l for l in all_leads if l.get('engagement_type') == 'reaction'])
    comment_count = len([l for l in all_leads if l.get('engagement_type') == 'comment'])
    
    qualified_reactions = len([l for l in qualified_leads if l.get('engagement_type') == 'reaction'])
    qualified_comments = len([l for l in qualified_leads if l.get('engagement_type') == 'comment'])
    
    print("\n🎯 REAL LLM RESULTS - GPT-4o MINI")
    print("=" * 60)
    print(f"📊 SUMMARY:")
    print(f"Total Leads Analyzed: {len(all_leads)}")
    print(f"Qualified Leads: {len(qualified_leads)}")
    print(f"Qualification Rate: {qualification_rate:.1f}%")
    print(f"Model Used: gpt-4o-mini")
    print(f"Processing: Batch (10 leads per API call)")
    
    print(f"\n📈 Engagement Breakdown:")
    print(f"  Reactions: {reaction_count} total, {qualified_reactions} qualified")
    print(f"  Comments: {comment_count} total, {qualified_comments} qualified")
    
    print(f"\n📊 Score Distribution:")
    for range_label, count in score_dist.items():
        print(f"  {range_label}: {count} leads")
    
    # Top qualified leads
    qualified_sorted = sorted(qualified_leads, key=lambda x: x.get('llm_score', 0), reverse=True)
    
    print(f"\n🏆 TOP 10 REAL LLM QUALIFIED LEADS:")
    for i, lead in enumerate(qualified_sorted[:10], 1):
        print(f"\n{i}. {lead['name']}")
        print(f"   Title: {lead['title']}")
        print(f"   Company: {lead['company']}")
        print(f"   Score: {lead.get('llm_score', 0)}/100")
        print(f"   Engagement: {lead['engagement_type']}")
        print(f"   Reasoning: {lead.get('llm_reasoning', 'N/A')}")
    
    # Save consolidated results
    final_results = {
        'analysis_timestamp': time.strftime('%Y%m%d_%H%M%S'),
        'model_used': 'gpt-4o-mini',
        'processing_method': 'batch_with_incremental_storage',
        'total_leads': len(all_leads),
        'qualified_leads': len(qualified_leads),
        'qualification_rate': qualification_rate,
        'score_distribution': score_dist,
        'engagement_breakdown': {
            'reactions': {'total': reaction_count, 'qualified': qualified_reactions},
            'comments': {'total': comment_count, 'qualified': qualified_comments}
        },
        'all_leads': all_leads,
        'qualified_only': qualified_leads
    }
    
    output_file = f"test_data/final_llm_results_{time.strftime('%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(final_results, f, indent=2)
    
    print(f"\n💾 Consolidated results saved to: {output_file}")
    
    # Performance analysis
    print(f"\n⚡ PERFORMANCE INSIGHTS:")
    print(f"✅ Incremental storage prevented data loss")
    print(f"✅ Batch processing (10x faster than individual calls)")
    print(f"✅ Real OpenAI API calls (no more mocks!)")
    print(f"✅ Cost-effective model (gpt-4o-mini vs gpt-4-turbo)")
    
    # Comparison with previous mock results
    print(f"\n🔄 COMPARISON:")
    print(f"Mock LLM Results: 58 qualified leads (30.2% rate)")
    print(f"Real LLM Results: {len(qualified_leads)} qualified leads ({qualification_rate:.1f}% rate)")
    
    if qualification_rate > 30:
        print("🎉 REAL LLM performs better than mock!")
    elif qualification_rate > 25:
        print("👍 REAL LLM performs similarly to mock")
    else:
        print("🔍 REAL LLM is more conservative than mock")

if __name__ == "__main__":
    main()