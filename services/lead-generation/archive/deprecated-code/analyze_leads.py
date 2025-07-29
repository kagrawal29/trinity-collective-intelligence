#!/usr/bin/env python3
"""
Lead Quality Analysis and Pre-Qualification Script
Analyzes Tyler's test data to identify high-quality leads
"""

import json
import os
from typing import Dict, List, Tuple
from dataclasses import dataclass
from collections import Counter

@dataclass
class LeadAnalysis:
    """Analysis results for a single lead"""
    name: str
    title: str
    subtitle: str
    navigation_url: str
    relevance_score: int
    relevance_reason: str
    is_qualified: bool

class LeadQualifier:
    """Analyzes and qualifies leads based on title/subtitle"""
    
    def __init__(self):
        # High-value title keywords (sales/revenue roles)
        self.high_value_keywords = [
            'sales', 'business development', 'bdr', 'sdr', 
            'account executive', 'revenue', 'growth', 'demand gen',
            'appointment setter', 'lead gen', 'outbound', 'outreach'
        ]
        
        # Medium-value keywords (marketing/operations)
        self.medium_value_keywords = [
            'marketing', 'digital marketing', 'performance marketing',
            'operations', 'strategy', 'manager', 'director'
        ]
        
        # Exclude keywords (usually not decision makers)
        self.exclude_keywords = [
            'student', 'intern', 'freelance', 'looking for',
            'seeking', 'aspiring', 'entry level'
        ]
        
        # Target company indicators
        self.company_indicators = [
            'saas', 'software', 'tech', 'agency', 'consulting',
            'startup', 'inc', 'llc', 'ltd', 'corporation'
        ]
    
    def calculate_relevance_score(self, title: str, subtitle: str) -> Tuple[int, str]:
        """Calculate 0-100 relevance score with reason"""
        title_lower = title.lower()
        subtitle_lower = subtitle.lower()
        combined = f"{title_lower} {subtitle_lower}"
        
        score = 50  # Base score
        reasons = []
        
        # Check exclusions first
        for exclude in self.exclude_keywords:
            if exclude in combined:
                return 0, f"Excluded: {exclude}"
        
        # High-value keywords (worth 20 points each, max 60)
        high_value_found = 0
        for keyword in self.high_value_keywords:
            if keyword in title_lower:
                score += 20
                high_value_found += 1
                reasons.append(f"'{keyword}' in title")
                if high_value_found >= 3:
                    break
        
        # Medium-value keywords (worth 10 points each, max 20)
        medium_value_found = 0
        for keyword in self.medium_value_keywords:
            if keyword in combined:
                score += 10
                medium_value_found += 1
                reasons.append(f"'{keyword}' found")
                if medium_value_found >= 2:
                    break
        
        # Company indicators (worth 10 points)
        for indicator in self.company_indicators:
            if indicator in subtitle_lower:
                score += 10
                reasons.append(f"Company type: {indicator}")
                break
        
        # Penalty for generic titles
        if len(title) < 10 or 'looking' in title_lower:
            score -= 20
            reasons.append("Generic/unclear title")
        
        # Cap at 100
        score = min(score, 100)
        
        reason = "; ".join(reasons) if reasons else "Base qualification"
        return score, reason
    
    def analyze_lead(self, reaction_data: Dict) -> LeadAnalysis:
        """Analyze a single lead from reaction data"""
        name = reaction_data.get('title', 'Unknown')
        title = reaction_data.get('subtitle', '')
        subtitle = reaction_data.get('subtitle', '')  # Company info
        navigation_url = reaction_data.get('navigationUrl', '')
        
        # Extract actual job title and company from subtitle
        # Format is usually "Job Title | Company Info"
        if '|' in title:
            parts = title.split('|', 1)
            actual_title = parts[0].strip()
            company_info = parts[1].strip() if len(parts) > 1 else ''
        else:
            actual_title = title
            company_info = ''
        
        score, reason = self.calculate_relevance_score(actual_title, company_info)
        
        return LeadAnalysis(
            name=name,
            title=actual_title,
            subtitle=company_info,
            navigation_url=navigation_url,
            relevance_score=score,
            relevance_reason=reason,
            is_qualified=score >= 70  # 70+ is qualified
        )
    
    def analyze_reactions_file(self, filepath: str) -> Dict:
        """Analyze reactions from Tyler's test data"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Handle both test format and full format
        if 'reactions' in data and isinstance(data['reactions'], list):
            # Full dataset format (from fetch_all_reactions.py)
            reactions = data['reactions']
        else:
            # Test format (from test_engagement.py)
            reactions = data.get('response', {}).get('reactions', [])
        
        # Analyze each reaction
        analyzed_leads = []
        for reaction in reactions:
            lead = self.analyze_lead(reaction)
            analyzed_leads.append(lead)
        
        # Sort by relevance score
        analyzed_leads.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Calculate statistics
        qualified_leads = [l for l in analyzed_leads if l.is_qualified]
        
        # Title word frequency
        all_titles = ' '.join([l.title.lower() for l in analyzed_leads])
        title_words = [w for w in all_titles.split() if len(w) > 3]
        word_freq = Counter(title_words).most_common(10)
        
        return {
            'total_reactions': len(reactions),
            'qualified_leads': len(qualified_leads),
            'qualification_rate': len(qualified_leads) / len(reactions) * 100 if reactions else 0,
            'top_leads': analyzed_leads[:10],
            'qualified_list': qualified_leads,
            'common_title_words': word_freq,
            'score_distribution': {
                '90-100': len([l for l in analyzed_leads if l.relevance_score >= 90]),
                '70-89': len([l for l in analyzed_leads if 70 <= l.relevance_score < 90]),
                '50-69': len([l for l in analyzed_leads if 50 <= l.relevance_score < 70]),
                '0-49': len([l for l in analyzed_leads if l.relevance_score < 50])
            }
        }

def main():
    """Run lead analysis on Tyler's test data"""
    qualifier = LeadQualifier()
    
    # Check for full dataset first, fallback to test data
    import glob
    all_reactions_files = glob.glob('test_data/all_reactions_*.json')
    
    if all_reactions_files:
        # Use the most recent full dataset
        reactions_file = sorted(all_reactions_files)[-1]
        print(f"📂 Using full dataset: {reactions_file}")
    else:
        # Fallback to test data
        reactions_file = 'test_data/4_reactions_response.json'
        print(f"📂 Using test dataset: {reactions_file}")
    
    if not os.path.exists(reactions_file):
        print("❌ No reactions data found! Run test_engagement.py or fetch_all_reactions.py first.")
        return
    
    print("🎯 LEAD QUALITY ANALYSIS")
    print("=" * 60)
    
    results = qualifier.analyze_reactions_file(reactions_file)
    
    # Display results
    print(f"\n📊 ANALYSIS SUMMARY:")
    print(f"Total Reactions Analyzed: {results['total_reactions']}")
    print(f"Qualified Leads Found: {results['qualified_leads']}")
    print(f"Qualification Rate: {results['qualification_rate']:.1f}%")
    
    print(f"\n📈 Score Distribution:")
    for range_label, count in results['score_distribution'].items():
        print(f"  {range_label}: {count} leads")
    
    print(f"\n🏆 TOP 10 QUALIFIED LEADS:")
    for i, lead in enumerate(results['top_leads'][:10], 1):
        print(f"\n{i}. {lead.name}")
        print(f"   Title: {lead.title}")
        print(f"   Company: {lead.subtitle}")
        print(f"   Score: {lead.relevance_score}/100")
        print(f"   Reason: {lead.relevance_reason}")
        print(f"   Qualified: {'✅ YES' if lead.is_qualified else '❌ NO'}")
    
    print(f"\n🔤 Most Common Title Words:")
    for word, count in results['common_title_words']:
        print(f"  '{word}': {count} times")
    
    # Save qualified leads
    qualified_output = {
        'analysis_summary': {
            'total_analyzed': results['total_reactions'],
            'qualified_count': results['qualified_leads'],
            'qualification_rate': results['qualification_rate']
        },
        'qualified_leads': [
            {
                'name': lead.name,
                'title': lead.title,
                'company': lead.subtitle,
                'linkedin_url': lead.navigation_url,
                'score': lead.relevance_score,
                'qualification_reason': lead.relevance_reason
            }
            for lead in results['qualified_list']
        ]
    }
    
    with open('test_data/qualified_leads.json', 'w') as f:
        json.dump(qualified_output, f, indent=2)
    
    print(f"\n💾 Qualified leads saved to: test_data/qualified_leads.json")
    print(f"\n✅ ANALYSIS COMPLETE!")
    
    # Recommendations
    print(f"\n🎯 RECOMMENDATIONS:")
    if results['qualification_rate'] > 20:
        print("✅ High qualification rate! This influencer attracts quality audience.")
    else:
        print("⚠️ Lower qualification rate. Consider testing other influencers.")
    
    print(f"\n📋 NEXT STEPS:")
    print("1. Review qualified_leads.json for outreach targets")
    print("2. Test more posts from this influencer")
    print("3. Implement automated qualification pipeline")
    print("4. Generate personalized messages for top leads")

if __name__ == "__main__":
    main()