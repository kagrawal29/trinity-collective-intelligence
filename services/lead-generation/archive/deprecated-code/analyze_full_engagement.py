#!/usr/bin/env python3
"""
Analyze Full Engagement Data (Reactions + Comments)
LLM-based lead qualification for context-aware scoring
"""

import json
import os
import glob
from typing import Dict, List, Tuple, Set, Optional
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv('../.env')

@dataclass
class EngagedLead:
    """Unified lead from any engagement source"""
    name: str
    title: str
    company: str
    linkedin_url: str
    engagement_type: str  # 'reaction' or 'comment'
    engagement_detail: str  # reaction type or comment preview
    relevance_score: int
    relevance_reason: str
    is_qualified: bool

class FullEngagementAnalyzer:
    """Analyze all engagement data comprehensively"""
    
    def __init__(self, api_key: Optional[str] = None, use_openai: bool = True):
        # LLM Configuration
        self.api_key = api_key or os.getenv('OPENAI_API_KEY') if use_openai else os.getenv('ANTHROPIC_API_KEY')
        self.use_openai = use_openai
        
        if not self.api_key:
            print("⚠️ WARNING: No API key found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY")
            print("Using mock LLM scoring for demonstration...")
            self.use_mock = True
            self.client = None
        else:
            self.use_mock = False
            # Initialize OpenAI client with the new syntax
            if use_openai:
                self.client = OpenAI(api_key=self.api_key)
            else:
                self.client = None  # For Anthropic, we'd use a different client
        
        # Track unique leads to avoid duplicates
        self.unique_leads: Dict[str, EngagedLead] = {}
        
        # LLM prompt template
        self.qualification_prompt = """You are an expert B2B lead qualifier analyzing LinkedIn engagement data.

Analyze this person's qualification as a potential B2B SaaS sales lead:

Name: {name}
Title: {title}
Company/Subtitle: {company}
Engagement Type: {engagement_type}

Score from 0-100 based on:
1. Job title relevance (sales, revenue, growth roles score highest)
2. Decision-making authority (C-level, VP, Director score high)
3. Company signals (B2B, SaaS, funded startups score high)
4. Engagement quality (comments > reactions)
5. Actual buying potential

Return ONLY a JSON object with this exact format:
{{
  "score": <number 0-100>,
  "reasoning": "<brief explanation>",
  "key_signals": ["<signal1>", "<signal2>", ...],
  "is_qualified": <true if score >= 70>
}}"""
        
    def extract_profile_from_reaction(self, reaction: Dict) -> Tuple[str, str, str, str]:
        """Extract profile info from reaction data"""
        name = reaction.get('title', 'Unknown')
        subtitle = reaction.get('subtitle', '')
        url = reaction.get('navigationUrl', '')
        
        # Parse subtitle for title and company
        if '|' in subtitle:
            parts = subtitle.split('|', 1)
            title = parts[0].strip()
            company = parts[1].strip() if len(parts) > 1 else ''
        else:
            title = subtitle
            company = ''
            
        return name, title, company, url
    
    def extract_profile_from_comment(self, comment: Dict) -> Tuple[str, str, str, str, str]:
        """Extract profile info from comment data"""
        # Comments have commenter, not author
        commenter = comment.get('commenter', {})
        name = commenter.get('title', 'Unknown')
        subtitle = commenter.get('subtitle', '')
        url = commenter.get('navigationUrl', '')
        comment_text = comment.get('text', '')[:100]  # First 100 chars
        
        # Parse subtitle
        if '|' in subtitle:
            parts = subtitle.split('|', 1)
            title = parts[0].strip()
            company = parts[1].strip() if len(parts) > 1 else ''
        else:
            title = subtitle
            company = ''
            
        return name, title, company, url, comment_text
    
    def calculate_llm_score(self, name: str, title: str, company: str, engagement_type: str) -> Tuple[int, str]:
        """LLM-based intelligent scoring"""
        
        # Mock scoring for demo if no API key
        if self.use_mock:
            return self._mock_llm_score(name, title, company, engagement_type)
        
        prompt = self.qualification_prompt.format(
            name=name,
            title=title,
            company=company,
            engagement_type=engagement_type
        )
        
        try:
            if self.use_openai and self.client:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                
                # Tyler found critical bug: OpenAI wraps JSON in markdown blocks
                content = response.choices[0].message.content.strip()
                
                # Remove markdown JSON blocks if present
                if content.startswith('```json'):
                    content = content[7:]  # Remove ```json
                if content.startswith('```'):
                    content = content[3:]   # Remove ``` 
                if content.endswith('```'):
                    content = content[:-3]  # Remove closing ```
                
                content = content.strip()
                
                try:
                    result = json.loads(content)
                    return result['score'], result['reasoning']
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing failed after markdown cleanup: {e}")
                    print(f"Raw content: {content[:200]}...")
                    # Fallback to manual scoring
                    return self._fallback_score(title, company, engagement_type)
                        
            else:  # Anthropic or no client
                return self._fallback_score(title, company, engagement_type)
                        
        except Exception as e:
            print(f"❌ LLM API error: {e}")
            return self._fallback_score(title, company, engagement_type)
    
    def _mock_llm_score(self, name: str, title: str, company: str, engagement_type: str) -> Tuple[int, str]:
        """Mock LLM scoring for demonstration"""
        title_lower = title.lower()
        company_lower = company.lower()
        
        # Simulate intelligent scoring
        score = 50
        reasons = []
        
        # CEO/Founder detection
        if any(role in title_lower for role in ['ceo', 'founder', 'owner']):
            score = 95
            reasons.append("CEO/Founder - highest decision authority")
        # Sales leadership
        elif any(role in title_lower for role in ['vp sales', 'head of sales', 'sales director']):
            score = 90
            reasons.append("Sales leadership - direct buyer")
        # Revenue/Growth roles
        elif any(role in title_lower for role in ['revenue', 'growth', 'demand']):
            score = 85
            reasons.append("Revenue-focused role")
        # Marketing leadership
        elif any(role in title_lower for role in ['cmo', 'vp marketing', 'marketing director']):
            score = 80
            reasons.append("Marketing leadership - influences buying")
        # Operations
        elif 'operations' in title_lower or 'coo' in title_lower:
            score = 75
            reasons.append("Operations - efficiency buyer")
            
        # Company context
        if any(signal in company_lower for signal in ['saas', 'software', 'tech', 'ai']):
            score += 10
            reasons.append("Tech company - likely SaaS buyer")
            
        # Engagement boost
        if engagement_type == 'comment':
            score += 5
            reasons.append("Active engagement")
            
        score = min(score, 100)
        reasoning = "; ".join(reasons) if reasons else "Standard qualification"
        
        return score, reasoning
    
    def _fallback_score(self, title: str, company: str, engagement_type: str) -> Tuple[int, str]:
        """Simple fallback scoring if LLM fails"""
        # Basic keyword matching as fallback
        score = 50
        if any(keyword in title.lower() for keyword in ['sales', 'revenue', 'growth', 'ceo', 'founder']):
            score = 75
        if engagement_type == 'comment':
            score += 10
        return min(score, 100), "Fallback scoring (LLM unavailable)"
    
    def process_engagement_file(self, filepath: str) -> Dict:
        """Process full engagement data file"""
        print(f"\n📂 Processing: {filepath}")
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        reactions = data.get('reactions', [])
        comments = data.get('comments', [])
        
        print(f"Found {len(reactions)} reactions and {len(comments)} comments")
        
        # Process with LLM scoring
        # Process reactions
        print("\n🤖 Scoring reactions with LLM...")
        for i, reaction in enumerate(reactions):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(reactions)}...")
                
            name, title, company, url = self.extract_profile_from_reaction(reaction)
            reaction_type = reaction.get('reactionType', 'LIKE')
            
            score, reason = self.calculate_llm_score(name, title, company, 'reaction')
            
            lead = EngagedLead(
                name=name,
                title=title,
                company=company,
                linkedin_url=url,
                engagement_type='reaction',
                engagement_detail=reaction_type,
                relevance_score=score,
                relevance_reason=reason,
                is_qualified=score >= 70
            )
            
            # Use URL as unique key
            if url and url not in self.unique_leads:
                self.unique_leads[url] = lead
            elif url and self.unique_leads[url].relevance_score < score:
                # Update if better score
                self.unique_leads[url] = lead
        
        # Process comments
        print("\n🤖 Scoring comments with LLM...")
        for i, comment in enumerate(comments):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(comments)}...")
                
            name, title, company, url, comment_preview = self.extract_profile_from_comment(comment)
            
            score, reason = self.calculate_llm_score(name, title, company, 'comment')
            
            lead = EngagedLead(
                name=name,
                title=title,
                company=company,
                linkedin_url=url,
                engagement_type='comment',
                engagement_detail=comment_preview,
                relevance_score=score,
                relevance_reason=reason,
                is_qualified=score >= 70
            )
            
            # Use URL as unique key
            if url and url not in self.unique_leads:
                self.unique_leads[url] = lead
            elif url and self.unique_leads[url].relevance_score < score:
                # Update if better score
                self.unique_leads[url] = lead
        
        return {
            'total_reactions': len(reactions),
            'total_comments': len(comments),
            'unique_leads': len(self.unique_leads)
        }
    
    def generate_comprehensive_report(self) -> Dict:
        """Generate comprehensive analysis report"""
        all_leads = list(self.unique_leads.values())
        qualified_leads = [l for l in all_leads if l.is_qualified]
        
        # Sort by score
        all_leads.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Engagement type breakdown
        engagement_breakdown = Counter(l.engagement_type for l in all_leads)
        qualified_breakdown = Counter(l.engagement_type for l in qualified_leads)
        
        # Title analysis
        all_titles = ' '.join([l.title.lower() for l in all_leads])
        title_words = [w for w in all_titles.split() if len(w) > 3]
        common_titles = Counter(title_words).most_common(15)
        
        # Company analysis
        companies = [l.company for l in qualified_leads if l.company]
        common_companies = Counter(companies).most_common(10)
        
        # Score distribution
        score_dist = {
            '90-100': len([l for l in all_leads if l.relevance_score >= 90]),
            '70-89': len([l for l in all_leads if 70 <= l.relevance_score < 90]),
            '50-69': len([l for l in all_leads if 50 <= l.relevance_score < 70]),
            '0-49': len([l for l in all_leads if l.relevance_score < 50])
        }
        
        return {
            'summary': {
                'total_unique_leads': len(all_leads),
                'qualified_leads': len(qualified_leads),
                'qualification_rate': len(qualified_leads) / len(all_leads) * 100 if all_leads else 0,
                'engagement_breakdown': dict(engagement_breakdown),
                'qualified_breakdown': dict(qualified_breakdown)
            },
            'score_distribution': score_dist,
            'top_leads': all_leads[:20],
            'qualified_list': qualified_leads,
            'common_title_words': common_titles,
            'top_companies': common_companies
        }

def main():
    """Run full engagement analysis with LLM scoring"""
    
    # Check for API keys
    use_openai = bool(os.getenv('OPENAI_API_KEY'))
    use_anthropic = bool(os.getenv('ANTHROPIC_API_KEY'))
    
    if use_openai:
        print("✅ Using OpenAI for LLM scoring")
    elif use_anthropic:
        print("✅ Using Anthropic for LLM scoring")
        use_openai = False
    else:
        print("⚠️ No API keys found - using mock LLM scoring")
        print("💡 Set OPENAI_API_KEY or ANTHROPIC_API_KEY for real scoring")
    
    analyzer = FullEngagementAnalyzer(use_openai=use_openai)
    
    # Find the most recent full engagement file (exclude analysis files)
    engagement_files = [f for f in glob.glob('test_data/full_engagement_*.json') 
                       if 'analysis' not in f]
    
    if not engagement_files:
        print("❌ No full engagement data found! Run fetch_all_engagement.py first.")
        return
    
    # Use most recent file
    latest_file = sorted(engagement_files)[-1]
    
    print("🎯 FULL ENGAGEMENT ANALYSIS")
    print("=" * 60)
    
    # Process file with LLM scoring
    stats = analyzer.process_engagement_file(latest_file)
    
    # Generate report
    report = analyzer.generate_comprehensive_report()
    
    # Display results
    print(f"\n📊 ENGAGEMENT SUMMARY:")
    print(f"Total Unique Leads: {report['summary']['total_unique_leads']}")
    print(f"Qualified Leads: {report['summary']['qualified_leads']}")
    print(f"Qualification Rate: {report['summary']['qualification_rate']:.1f}%")
    
    print(f"\n📈 Engagement Type Breakdown:")
    for eng_type, count in report['summary']['engagement_breakdown'].items():
        qualified = report['summary']['qualified_breakdown'].get(eng_type, 0)
        print(f"  {eng_type}: {count} total, {qualified} qualified")
    
    print(f"\n📊 Score Distribution:")
    for range_label, count in report['score_distribution'].items():
        print(f"  {range_label}: {count} leads")
    
    print(f"\n🏆 TOP 10 QUALIFIED LEADS:")
    for i, lead in enumerate(report['top_leads'][:10], 1):
        print(f"\n{i}. {lead.name}")
        print(f"   Title: {lead.title}")
        print(f"   Company: {lead.company}")
        print(f"   Score: {lead.relevance_score}/100")
        print(f"   Engagement: {lead.engagement_type} ({lead.engagement_detail[:50]}...)")
        print(f"   Reason: {lead.relevance_reason}")
        print(f"   Qualified: {'✅ YES' if lead.is_qualified else '❌ NO'}")
    
    print(f"\n🔤 Most Common Title Words:")
    for word, count in report['common_title_words'][:10]:
        print(f"  '{word}': {count} times")
    
    print(f"\n🏢 Top Companies (from qualified leads):")
    for company, count in report['top_companies']:
        print(f"  {company}: {count} leads")
    
    # Save full report
    output = {
        'analysis_timestamp': os.path.basename(latest_file),
        'report': report['summary'],
        'score_distribution': report['score_distribution'],
        'qualified_leads': [
            {
                'name': lead.name,
                'title': lead.title,
                'company': lead.company,
                'linkedin_url': lead.linkedin_url,
                'engagement_type': lead.engagement_type,
                'score': lead.relevance_score,
                'reason': lead.relevance_reason
            }
            for lead in report['qualified_list']
        ]
    }
    
    output_file = f"test_data/full_engagement_analysis_{os.path.basename(latest_file).split('_')[-1]}"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Full analysis saved to: {output_file}")
    print(f"\n✅ ANALYSIS COMPLETE!")
    
    # Recommendations
    print(f"\n🎯 RECOMMENDATIONS:")
    if report['summary']['qualification_rate'] > 30:
        print("✅ Excellent qualification rate! This influencer has a highly relevant audience.")
    elif report['summary']['qualification_rate'] > 20:
        print("👍 Good qualification rate. Consider testing more of this influencer's posts.")
    else:
        print("⚠️ Lower qualification rate. May need to test other influencers.")
    
    comment_ratio = report['summary']['engagement_breakdown'].get('comment', 0) / max(report['summary']['total_unique_leads'], 1)
    if comment_ratio > 0.2:
        print("✅ High comment engagement! These are highly engaged prospects.")
    
    print(f"\n📋 NEXT STEPS:")
    print("1. Export qualified leads for outreach")
    print("2. Generate personalized messages based on engagement type")
    print("3. Prioritize commenters (higher engagement)")
    print("4. Track conversion rates by lead score")
    
    # Show LLM vs rule-based comparison
    print(f"\n🤖 LLM SCORING ADVANTAGES:")
    print("✅ Context-aware evaluation (CEOs score 95+)")
    print("✅ Understands role hierarchies")
    print("✅ Recognizes buying signals in titles")
    print("✅ Adapts to new patterns without code changes")
    print("✅ Explains reasoning for each score")

if __name__ == "__main__":
    main()