#!/usr/bin/env python3
"""
Post Qualification using LLM - Evaluate if post is relevant for lead generation
"""

import json
import os
from datetime import datetime
from typing import Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

# Load environment
load_dotenv('../.env')

# Initialize OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class PostQualificationLLM:
    """LLM-based post qualification for B2B lead generation relevance"""
    
    def __init__(self):
        self.model = "gpt-4o-mini"
        self.prompt_template = """
You are an expert B2B lead generation specialist evaluating LinkedIn posts for relevance.

Evaluate this post content against our Ideal Customer Profile (ICP):
- Target Audience: B2B companies, SaaS, Sales/Marketing teams
- Relevant Topics: Lead generation, sales automation, revenue operations, GTM strategy
- High Value Indicators: Discussion of tools, strategies, pain points, success stories
- Engagement Quality: Professional discourse, decision-makers participating

Post Content:
{post_content}

Evaluate the post on these criteria:
1. Target Audience Match (0-100): Are the readers likely our ICP?
2. Topic Relevance (0-100): Does it discuss lead gen/sales/marketing?
3. Lead Quality Potential (0-100): Will engaged users be qualified prospects?
4. Action Trigger (0-100): Does it prompt engagement from decision-makers?

Provide your evaluation in this JSON format:
{{
    "overall_score": <weighted average 0-100>,
    "target_audience_score": <0-100>,
    "topic_relevance_score": <0-100>,
    "lead_quality_score": <0-100>,
    "action_trigger_score": <0-100>,
    "qualification": "QUALIFIED" or "NOT_QUALIFIED",
    "reasoning": "<brief explanation>",
    "key_indicators": ["<indicator1>", "<indicator2>", ...],
    "recommended_action": "PROCESS" or "SKIP"
}}

Only return the JSON, no other text.
"""
    
    def qualify_post(self, post_content: str, post_url: str = None) -> Dict[str, Any]:
        """Qualify a post using LLM evaluation"""
        
        try:
            # Prepare prompt
            prompt = self.prompt_template.format(post_content=post_content)
            
            # Call OpenAI
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a B2B lead generation expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse response
            content = response.choices[0].message.content.strip()
            
            # Remove markdown if present
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            
            result = json.loads(content.strip())
            
            # Add metadata
            result['post_url'] = post_url
            result['evaluated_at'] = datetime.now().isoformat()
            result['model_used'] = self.model
            
            return result
            
        except Exception as e:
            print(f"Error qualifying post: {e}")
            return {
                "overall_score": 0,
                "qualification": "ERROR",
                "reasoning": f"Failed to evaluate: {str(e)}",
                "recommended_action": "SKIP",
                "error": str(e)
            }
    
    def is_qualified(self, result: Dict[str, Any], threshold: int = 70) -> bool:
        """Check if post meets qualification threshold"""
        return result.get('overall_score', 0) >= threshold

def main():
    """Test post qualification"""
    
    # Example post content
    test_post = """
    🚀 Just helped a B2B SaaS company 3x their qualified leads in 90 days!

    Here's what we did:
    1. Implemented Clay for data enrichment
    2. Built custom lead scoring with AI
    3. Automated outreach sequences
    4. A/B tested messaging strategies

    The result? Their sales team is now talking to 3x more qualified prospects, 
    and close rates improved by 40%.

    What's your biggest challenge with lead generation? Drop a comment below! 👇

    #B2BSales #LeadGeneration #SalesAutomation #RevOps
    """
    
    qualifier = PostQualificationLLM()
    
    print("🎯 POST QUALIFICATION TEST")
    print("="*60)
    print("Post Content:")
    print(test_post[:200] + "...")
    print("\n🤖 Evaluating with LLM...")
    
    result = qualifier.qualify_post(test_post, "https://example.com/post/123")
    
    print("\n📊 QUALIFICATION RESULTS:")
    print(json.dumps(result, indent=2))
    
    if qualifier.is_qualified(result):
        print("\n✅ POST QUALIFIED! Ready for lead extraction.")
    else:
        print("\n❌ POST NOT QUALIFIED. Skip processing.")

if __name__ == "__main__":
    main()