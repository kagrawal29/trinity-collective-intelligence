#!/usr/bin/env python3
"""
LLM-based Prospect Qualification Workflow
Uses OpenAI to analyze LinkedIn profiles for:
1. Decision maker status
2. Competitor/partner potential
3. Influencer status
"""

import json
import os
from typing import Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMProspectQualifier:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Load our service description
        with open('our-service-description.md', 'r') as f:
            self.service_description = f.read()
    
    def analyze_decision_maker(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to determine if person is a decision maker"""
        
        prompt = f"""Based on the following LinkedIn profile data, determine if this person is a decision maker who could purchase our lead generation service.

Our Service: We provide an AI-powered lead generation platform for outbound sales teams to automate prospect research and qualification.

Profile Data:
- Name: {profile.get('fullName', 'Unknown')}
- Headline: {profile.get('headline', '')}
- Current Role: {profile.get('experiences', [{}])[0].get('title', '') if profile.get('experiences') else 'Unknown'}
- About: {profile.get('about', '')[:500]}

Analyze and return JSON with:
1. "is_decision_maker": true/false
2. "confidence": 0-100
3. "reasoning": explanation
4. "role_level": "C-level", "VP", "Director", "Manager", "IC", or "Unknown"
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    def analyze_competitor_partner(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to determine competitor/partner status"""
        
        # Extract company descriptions
        experiences_text = ""
        for exp in profile.get('experiences', [])[:3]:
            experiences_text += f"\n- {exp.get('title', '')} at {exp.get('subtitle', '')}"
            for desc in exp.get('description', []):
                if desc.get('type') == 'textComponent':
                    experiences_text += f"\n  {desc.get('text', '')}"
        
        prompt = f"""Analyze if this person or their company is a competitor, potential partner, or neither for our lead generation service.

Our Service:
{self.service_description}

Profile:
- Name: {profile.get('fullName', '')}
- Headline: {profile.get('headline', '')}
- About: {profile.get('about', '')[:500]}
- Recent Experience: {experiences_text[:1000]}

Return JSON with:
1. "status": "competitor", "partner", or "neither"
2. "confidence": 0-100
3. "reasoning": detailed explanation
4. "overlap_areas": list of overlapping service areas if any
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    def analyze_influencer_status(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to calculate influencer score"""
        
        # Get engagement metrics
        total_engagement = 0
        post_summaries = []
        updates = profile.get('updates', [])
        
        for update in updates[:5]:  # Check last 5 posts
            engagement = update.get('numLikes', 0) + update.get('numComments', 0)
            total_engagement += engagement
            post_summaries.append({
                'text': update.get('postText', '')[:200],
                'likes': update.get('numLikes', 0),
                'comments': update.get('numComments', 0)
            })
        
        prompt = f"""Analyze if this person is truly an influencer who regularly creates content and has significant reach.

Profile:
- Name: {profile.get('fullName', '')}
- Followers: {profile.get('followers', 0):,}
- Connections: {profile.get('connections', 0):,}
- About: {profile.get('about', '')[:300]}
- Number of Recent Posts: {len(post_summaries)}
- Recent Posts: {json.dumps(post_summaries, indent=2) if post_summaries else "No recent posts found"}

IMPORTANT CRITERIA FOR BEING AN INFLUENCER:
1. Must post regularly (minimum 2 times per week / 8+ posts per month)
2. Should have substantial followers (10k+ preferred)
3. Posts should get significant engagement
4. Content should be thought leadership, not just reactions

Based on the above, score them where:
- 70-100: True influencer (regular poster, high engagement, thought leader)
- 40-69: Occasional poster or moderate influence
- 0-39: Not an influencer (rare posting, low engagement)

Return JSON with:
1. "influencer_score": 0-100 (use strict criteria above)
2. "posting_frequency": "regular" (2+/week), "occasional" (1-4/month), or "rare" (<1/month)
3. "is_thought_leader": true/false
4. "reasoning": detailed explanation including posting frequency analysis
5. "follower_engagement_rate": "high", "medium", or "low"
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    def generate_qualification_summary(self, profile: Dict[str, Any], analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall qualification and personalized approach"""
        
        # Determine if lead is qualified based on criteria
        is_decision_maker = analyses['decision_maker'].get('is_decision_maker', False)
        is_competitor = analyses['competitor'].get('status') == 'competitor'
        influencer_score = analyses['influencer'].get('influencer_score', 0)
        
        # Lead is qualified if: decision maker AND NOT competitor AND NOT influencer (score < 70)
        is_qualified = is_decision_maker and not is_competitor and influencer_score < 70
        
        prompt = f"""Based on the analysis below, provide a final qualification assessment and personalized outreach strategy.

Profile: {profile.get('fullName', '')} - {profile.get('headline', '')}

Decision Maker Analysis: {json.dumps(analyses['decision_maker'], indent=2)}
Competitor/Partner Analysis: {json.dumps(analyses['competitor'], indent=2)}
Influencer Analysis: {json.dumps(analyses['influencer'], indent=2)}

QUALIFICATION CRITERIA:
- Must be a decision maker: {is_decision_maker}
- Must NOT be a competitor: {not is_competitor}
- Must NOT be an influencer (score < 70): {influencer_score < 70}

Lead Qualified: {is_qualified}

Return JSON with:
1. "is_qualified": {str(is_qualified).lower()} (based on all criteria above)
2. "overall_score": 0-100 (qualification score)
3. "priority": "high", "medium", or "low" (only "high" if qualified)
4. "qualification_summary": brief explanation of why they are/aren't qualified
5. "disqualification_reasons": list of reasons if not qualified (empty if qualified)
6. "personalization_hooks": list of 3 specific points to mention in outreach (only if qualified)
7. "recommended_approach": "direct_pitch" or "value_first" (only if qualified, null otherwise)
8. "potential_objections": list of likely objections (only if qualified)
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    def qualify_prospect(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run complete LLM-based qualification workflow"""
        
        print(f"Analyzing {profile_data.get('fullName', 'Unknown')}...")
        
        # Run analyses
        decision_maker = self.analyze_decision_maker(profile_data)
        print("✓ Decision maker analysis complete")
        
        competitor = self.analyze_competitor_partner(profile_data)
        print("✓ Competitor/partner analysis complete")
        
        influencer = self.analyze_influencer_status(profile_data)
        print("✓ Influencer analysis complete")
        
        # Generate summary
        analyses = {
            'decision_maker': decision_maker,
            'competitor': competitor,
            'influencer': influencer
        }
        
        summary = self.generate_qualification_summary(profile_data, analyses)
        print("✓ Qualification summary generated")
        
        return {
            "prospect": {
                "name": profile_data.get('fullName', 'Unknown'),
                "headline": profile_data.get('headline', ''),
                "linkedin_url": f"https://www.linkedin.com/in/{profile_data.get('publicIdentifier', '')}"
            },
            "analyses": analyses,
            "qualification": summary
        }


if __name__ == "__main__":
    # Load the profile data
    import sys
    profile_file = sys.argv[1] if len(sys.argv) > 1 else 'daniel_shnaider_profile.json'
    with open(profile_file, 'r') as f:
        response = json.load(f)
    
    if response.get('success') and response.get('data'):
        profile_data = response['data']
        
        # Initialize qualifier
        qualifier = LLMProspectQualifier()
        
        # Run qualification
        result = qualifier.qualify_prospect(profile_data)
        
        # Save results
        output_file = profile_file.replace('_profile.json', '_qualification.json')
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print("\n" + "="*50)
        print("QUALIFICATION COMPLETE")
        print("="*50)
        print(f"\nProspect: {result['prospect']['name']}")
        print(f"QUALIFIED: {'✅ YES' if result['qualification']['is_qualified'] else '❌ NO'}")
        print(f"\nDecision Maker: {'✅' if result['analyses']['decision_maker']['is_decision_maker'] else '❌'}")
        print(f"Competitor: {'❌ Yes' if result['analyses']['competitor']['status'] == 'competitor' else '✅ No'}")
        print(f"Influencer: {'❌ Yes' if result['analyses']['influencer']['influencer_score'] >= 70 else '✅ No'} (Score: {result['analyses']['influencer']['influencer_score']})")
        
        if not result['qualification']['is_qualified']:
            print(f"\nDisqualification Reasons:")
            for reason in result['qualification'].get('disqualification_reasons', []):
                print(f"  - {reason}")
        
        print(f"\nOverall Score: {result['qualification']['overall_score']}/100")
        print(f"Priority: {result['qualification']['priority']}")
        print(f"\nSummary: {result['qualification']['qualification_summary']}")
        print(f"\nFull results saved to: {output_file}")
    else:
        print("Error: Invalid profile data")