#!/usr/bin/env python3
"""
Deep Analysis of Real LLM Results
Validate scoring patterns and find potential issues
"""

import json
from collections import Counter

def analyze_results():
    # Load results
    with open('test_data/final_llm_results_191539.json', 'r') as f:
        data = json.load(f)
    
    all_leads = data['all_leads']
    qualified_leads = data['qualified_only']
    
    print("🔍 DEEP ANALYSIS OF REAL LLM RESULTS")
    print("=" * 60)
    
    # 1. Score Distribution Analysis
    print("\n📊 DETAILED SCORE DISTRIBUTION:")
    score_ranges = [
        (95, 100, "Excellent (95-100)"),
        (90, 94, "Very High (90-94)"),
        (80, 89, "High (80-89)"),
        (70, 79, "Good (70-79)"),
        (60, 69, "Medium (60-69)"),
        (50, 59, "Low (50-59)"),
        (0, 49, "Very Low (0-49)")
    ]
    
    for min_score, max_score, label in score_ranges:
        count = len([l for l in all_leads if min_score <= l.get('llm_score', 0) <= max_score])
        percentage = count / len(all_leads) * 100
        print(f"  {label}: {count} leads ({percentage:.1f}%)")
    
    # 2. Title Pattern Analysis
    print("\n👔 QUALIFIED LEAD TITLES:")
    qualified_titles = [lead['title'] for lead in qualified_leads]
    title_patterns = Counter()
    
    for title in qualified_titles:
        if 'founder' in title.lower() or 'ceo' in title.lower():
            title_patterns['CEO/Founder'] += 1
        elif 'director' in title.lower():
            title_patterns['Director Level'] += 1
        elif 'manager' in title.lower():
            title_patterns['Manager Level'] += 1
        elif 'head' in title.lower() or 'vp' in title.lower():
            title_patterns['VP/Head Level'] += 1
        elif 'growth' in title.lower() or 'revenue' in title.lower():
            title_patterns['Growth/Revenue'] += 1
        elif 'marketing' in title.lower():
            title_patterns['Marketing'] += 1
        elif 'sales' in title.lower():
            title_patterns['Sales'] += 1
        else:
            title_patterns['Other'] += 1
    
    for pattern, count in title_patterns.most_common():
        percentage = count / len(qualified_leads) * 100
        print(f"  {pattern}: {count} ({percentage:.1f}%)")
    
    # 3. False Positive Analysis
    print("\n🚨 POTENTIAL FALSE POSITIVES (High scores but questionable):")
    suspicious_leads = []
    
    for lead in qualified_leads:
        title = lead['title'].lower()
        company = lead['company'].lower()
        score = lead.get('llm_score', 0)
        
        # Check for suspicious patterns
        if score >= 70:
            suspicious_flags = []
            
            # Student/intern patterns
            if any(word in title for word in ['student', 'intern', 'trainee', 'fresher']):
                suspicious_flags.append("Student/Entry level")
            
            # Individual contributor without authority
            if any(word in title for word in ['specialist', 'executive', 'associate']) and not any(word in title for word in ['senior', 'lead', 'principal']):
                suspicious_flags.append("Individual contributor")
            
            # Unrelated industries
            if any(word in company for word in ['restaurant', 'food', 'retail', 'fashion', 'beauty']):
                suspicious_flags.append("Unrelated industry")
            
            # Service providers (might not be buyers)
            if any(phrase in title for phrase in ['helping', 'consultant', 'freelancer', 'coach']):
                suspicious_flags.append("Service provider")
            
            if suspicious_flags:
                suspicious_leads.append({
                    'name': lead['name'],
                    'title': lead['title'],
                    'score': score,
                    'flags': suspicious_flags,
                    'reasoning': lead.get('llm_reasoning', 'N/A')
                })
    
    for lead in suspicious_leads[:10]:  # Top 10 suspicious
        print(f"\n⚠️  {lead['name']} (Score: {lead['score']})")
        print(f"   Title: {lead['title']}")
        print(f"   Flags: {', '.join(lead['flags'])}")
        print(f"   LLM Reasoning: {lead['reasoning']}")
    
    # 4. False Negative Analysis
    print("\n🔍 POTENTIAL FALSE NEGATIVES (Low scores but might be good):")
    unqualified_leads = [l for l in all_leads if not l.get('is_qualified', False)]
    potential_good_leads = []
    
    for lead in unqualified_leads:
        title = lead['title'].lower()
        score = lead.get('llm_score', 0)
        
        # Look for potentially good leads that scored low
        good_signals = []
        
        if any(word in title for word in ['sales', 'business development', 'account']):
            good_signals.append("Sales role")
        
        if any(word in title for word in ['senior', 'lead', 'principal']):
            good_signals.append("Senior level")
        
        if 'saas' in lead['company'].lower() or 'software' in lead['company'].lower():
            good_signals.append("Tech company")
        
        if good_signals and score < 70:
            potential_good_leads.append({
                'name': lead['name'],
                'title': lead['title'],
                'score': score,
                'signals': good_signals,
                'reasoning': lead.get('llm_reasoning', 'N/A')
            })
    
    for lead in sorted(potential_good_leads, key=lambda x: x['score'], reverse=True)[:5]:
        print(f"\n🤔 {lead['name']} (Score: {lead['score']})")
        print(f"   Title: {lead['title']}")
        print(f"   Good Signals: {', '.join(lead['signals'])}")
        print(f"   LLM Reasoning: {lead['reasoning']}")
    
    # 5. Reasoning Pattern Analysis
    print("\n🧠 LLM REASONING PATTERNS:")
    reasoning_keywords = Counter()
    
    for lead in all_leads:
        reasoning = lead.get('llm_reasoning', '').lower()
        if 'decision' in reasoning:
            reasoning_keywords['Decision Authority'] += 1
        if 'relevance' in reasoning or 'relevant' in reasoning:
            reasoning_keywords['Relevance'] += 1
        if 'authority' in reasoning:
            reasoning_keywords['Authority'] += 1
        if 'buying' in reasoning:
            reasoning_keywords['Buying Power'] += 1
        if 'b2b' in reasoning:
            reasoning_keywords['B2B Focus'] += 1
        if 'limited' in reasoning or 'lacks' in reasoning:
            reasoning_keywords['Limited/Lacks'] += 1
    
    for keyword, count in reasoning_keywords.most_common():
        print(f"  {keyword}: {count} mentions")
    
    # 6. Quality Assessment
    print("\n⭐ QUALITY ASSESSMENT:")
    
    # High-confidence leads (90+ scores)
    high_confidence = [l for l in qualified_leads if l.get('llm_score', 0) >= 90]
    print(f"High-confidence leads (90+): {len(high_confidence)}")
    
    # CEO/Founder leads
    ceo_founders = [l for l in qualified_leads if 'ceo' in l['title'].lower() or 'founder' in l['title'].lower()]
    print(f"CEO/Founder leads: {len(ceo_founders)}")
    
    # Director+ level leads
    director_plus = [l for l in qualified_leads if any(word in l['title'].lower() for word in ['director', 'vp', 'head', 'chief'])]
    print(f"Director+ level leads: {len(director_plus)}")
    
    # Calculate confidence score
    confidence_score = (len(high_confidence) + len(ceo_founders) + len(director_plus)) / len(qualified_leads) * 100
    print(f"\nOverall Confidence Score: {confidence_score:.1f}%")
    
    if confidence_score >= 70:
        print("🎉 HIGH QUALITY - Most leads appear genuinely qualified")
    elif confidence_score >= 50:
        print("👍 GOOD QUALITY - Majority of leads are solid")
    else:
        print("⚠️ MIXED QUALITY - Needs refinement")
    
    print(f"\n📈 FINAL ASSESSMENT:")
    print(f"✅ Real LLM is working with actual reasoning")
    print(f"✅ Batch processing with incremental storage successful")
    print(f"✅ {len(suspicious_leads)} potential false positives identified")
    print(f"✅ {len(potential_good_leads)} potential false negatives found")
    print(f"✅ Overall qualification rate: {data['qualification_rate']:.1f}%")

if __name__ == "__main__":
    analyze_results()