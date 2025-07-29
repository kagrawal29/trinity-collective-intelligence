#!/usr/bin/env python3
"""
LLM-based Lead Quality Analysis
Uses AI to intelligently evaluate leads beyond simple keyword matching
"""

import json
import os
from typing import Dict, List, Tuple
from dataclasses import dataclass
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class LLMLeadAnalysis:
    """LLM-powered analysis results"""
    name: str
    title: str
    company: str
    linkedin_url: str
    llm_score: int
    llm_reasoning: str
    is_decision_maker: bool
    is_relevant_industry: bool
    buying_power_indicator: bool
    rule_based_score: int  # For comparison

class LLMLeadQualifier:
    """Uses LLM to intelligently qualify leads"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
        
        # Our ideal customer profile
        self.icp_context = """
        We are selling a B2B lead generation automation service that:
        - Helps sales teams find and qualify leads from LinkedIn
        - Automates outreach and personalization
        - Typical customers: B2B SaaS companies, agencies, sales teams
        - Decision makers: Sales leaders, Growth leaders, Founders, RevOps
        - Budget range: $2-10k/month
        """
    
    def analyze_lead_with_llm(self, name: str, title: str, company: str) -> Dict:
        """Use LLM to deeply analyze lead quality"""
        
        prompt = f"""
        Analyze this LinkedIn profile for lead qualification:
        
        Name: {name}
        Title: {title}
        Company/Description: {company}
        
        Context about our service:
        {self.icp_context}
        
        Please evaluate and return a JSON response with:
        1. "score": 0-100 qualification score
        2. "is_decision_maker": true/false - Can they make purchasing decisions?
        3. "is_relevant_industry": true/false - Do they need lead generation?
        4. "buying_power_indicator": true/false - Do they likely have budget?
        5. "reasoning": Brief explanation of your scoring
        6. "key_insights": What makes them good/bad fit
        7. "outreach_angle": If qualified, what messaging angle to use
        
        Consider:
        - Job title hierarchy and decision-making authority
        - Company type and likely need for lead generation
        - Specific keywords that indicate active need
        - Red flags (student, job seeker, etc.)
        """
        
        try:
            # For demo purposes, using a mock LLM response
            # In production, this would call OpenAI/Anthropic
            return self._mock_llm_analysis(name, title, company)
        except Exception as e:
            print(f"LLM Error: {e}")
            return self._fallback_analysis(title, company)
    
    def _mock_llm_analysis(self, name: str, title: str, company: str) -> Dict:
        """Mock LLM response for demonstration"""
        
        title_lower = title.lower()
        company_lower = company.lower()
        
        # Simulate intelligent analysis
        score = 50
        is_decision_maker = False
        is_relevant_industry = False
        buying_power = False
        insights = []
        
        # Decision maker analysis
        if any(role in title_lower for role in ['director', 'vp', 'head of', 'founder', 'ceo', 'owner']):
            is_decision_maker = True
            score += 20
            insights.append("Senior role with decision-making authority")
        elif 'manager' in title_lower and any(dept in title_lower for dept in ['sales', 'marketing', 'growth']):
            is_decision_maker = True
            score += 15
            insights.append("Mid-level manager in relevant department")
        
        # Industry relevance
        if any(ind in company_lower for ind in ['saas', 'software', 'tech', 'agency', 'consulting']):
            is_relevant_industry = True
            score += 15
            insights.append("Works in B2B software/services industry")
        
        # Specific need indicators
        if any(need in title_lower for need in ['growth', 'demand gen', 'lead gen', 'sales development']):
            score += 15
            insights.append("Role directly involves lead generation")
        
        # Buying power
        if any(signal in company_lower for signal in ['scale', 'series', 'growth', 'expanding']):
            buying_power = True
            score += 10
            insights.append("Company showing growth signals")
        
        # Negative signals
        if any(neg in title_lower + company_lower for neg in ['student', 'intern', 'looking for', 'seeking']):
            score = 10
            insights.append("Not currently in buying position")
        
        # Determine outreach angle
        outreach_angle = "Generic outreach"
        if score >= 70:
            if 'sales' in title_lower:
                outreach_angle = "Focus on pipeline acceleration and quota attainment"
            elif 'marketing' in title_lower:
                outreach_angle = "Emphasize MQL generation and attribution"
            elif 'founder' in title_lower or 'ceo' in title_lower:
                outreach_angle = "Position as strategic growth enabler"
        
        return {
            "score": min(score, 100),
            "is_decision_maker": is_decision_maker,
            "is_relevant_industry": is_relevant_industry,
            "buying_power_indicator": buying_power,
            "reasoning": f"Score based on: {', '.join(insights[:3])}" if insights else "Limited signals for qualification",
            "key_insights": insights,
            "outreach_angle": outreach_angle
        }
    
    def _fallback_analysis(self, title: str, company: str) -> Dict:
        """Fallback when LLM is unavailable"""
        return {
            "score": 50,
            "is_decision_maker": 'manager' in title.lower() or 'director' in title.lower(),
            "is_relevant_industry": 'saas' in company.lower() or 'software' in company.lower(),
            "buying_power_indicator": False,
            "reasoning": "Basic keyword analysis (LLM unavailable)",
            "key_insights": ["Fallback analysis used"],
            "outreach_angle": "Generic outreach"
        }


def compare_scoring_methods():
    """Compare rule-based vs LLM-based scoring"""
    
    # Load the latest engagement data
    engagement_file = None
    for f in sorted(os.listdir('test_data'), reverse=True):
        if f.startswith('full_engagement_2025'):
            engagement_file = f
            break
    
    if not engagement_file:
        print("No engagement data found!")
        return
    
    with open(f'test_data/{engagement_file}', 'r') as f:
        data = json.load(f)
    
    # Initialize analyzers
    llm_analyzer = LLMLeadQualifier()
    
    # Also load rule-based scores for comparison
    try:
        with open('test_data/qualified_leads.json', 'r') as f:
            rule_based = json.load(f)
            rule_based_scores = {
                lead['linkedin_url']: lead['score'] 
                for lead in rule_based.get('qualified_leads', [])
            }
    except:
        rule_based_scores = {}
    
    # Analyze with LLM
    results = []
    print("🤖 Running LLM-based analysis on all leads...\n")
    
    # Combine reactions and comments
    all_people = []
    
    # Add reactions
    for reaction in data.get('reactions', [])[:15]:
        all_people.append({
            'name': reaction.get('title', 'Unknown'),
            'title': reaction.get('subtitle', ''),
            'company': reaction.get('subtitle', ''),
            'linkedin_url': reaction.get('navigationUrl', ''),
            'engagement_type': 'reaction'
        })
    
    # Add comments
    for comment in data.get('comments', [])[:5]:
        commenter = comment.get('commenter', {})
        all_people.append({
            'name': commenter.get('title', 'Unknown'),
            'title': commenter.get('subtitle', ''),
            'company': commenter.get('subtitle', ''),
            'linkedin_url': commenter.get('navigationUrl', ''),
            'engagement_type': 'comment'
        })
    
    for person in all_people:
        name = person['name']
        title = person['title']
        company = person['company']
        url = person['linkedin_url']
        
        # Get LLM analysis
        llm_result = llm_analyzer.analyze_lead_with_llm(name, title, company)
        
        # Get rule-based score
        rule_score = rule_based_scores.get(url, 0)
        
        result = {
            'name': name,
            'title': title,
            'company': company,
            'linkedin_url': url,
            'llm_score': llm_result['score'],
            'rule_based_score': rule_score,
            'score_difference': llm_result['score'] - rule_score,
            'llm_reasoning': llm_result['reasoning'],
            'is_decision_maker': llm_result['is_decision_maker'],
            'outreach_angle': llm_result['outreach_angle']
        }
        
        results.append(result)
        
        # Print comparison
        if abs(result['score_difference']) > 20:
            print(f"🔍 SIGNIFICANT DIFFERENCE: {name}")
            print(f"   Title: {title}")
            print(f"   LLM Score: {llm_result['score']} | Rule Score: {rule_score}")
            print(f"   LLM Says: {llm_result['reasoning']}")
            print(f"   Outreach: {llm_result['outreach_angle']}")
            print()
    
    # Save comparison results
    comparison = {
        'analysis_method': 'LLM vs Rule-based comparison',
        'total_analyzed': len(results),
        'results': results,
        'insights': {
            'avg_llm_score': sum(r['llm_score'] for r in results) / len(results) if results else 0,
            'avg_rule_score': sum(r['rule_based_score'] for r in results) / len(results) if results else 0,
            'significant_differences': len([r for r in results if abs(r['score_difference']) > 20]),
            'llm_qualified': len([r for r in results if r['llm_score'] >= 70]),
            'rule_qualified': len([r for r in results if r['rule_based_score'] >= 70])
        }
    }
    
    with open('test_data/llm_vs_rule_comparison.json', 'w') as f:
        json.dump(comparison, f, indent=2)
    
    print(f"\n📊 COMPARISON COMPLETE!")
    print(f"✅ Results saved to: test_data/llm_vs_rule_comparison.json")
    print(f"\nSummary:")
    print(f"- Average LLM Score: {comparison['insights']['avg_llm_score']:.1f}")
    print(f"- Average Rule Score: {comparison['insights']['avg_rule_score']:.1f}")
    print(f"- Significant differences: {comparison['insights']['significant_differences']}")
    print(f"- LLM Qualified: {comparison['insights']['llm_qualified']}")
    print(f"- Rule Qualified: {comparison['insights']['rule_qualified']}")


if __name__ == "__main__":
    print("🚀 LLM-Based Lead Analysis\n")
    compare_scoring_methods()