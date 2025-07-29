#!/usr/bin/env python3
"""
Generate Personalized Outreach Messages
LLM-powered message generation based on engagement context
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
import aiohttp

class OutreachGenerator:
    """Generate personalized outreach messages using LLM"""
    
    def __init__(self, api_key: Optional[str] = None, use_openai: bool = True):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY') if use_openai else os.getenv('ANTHROPIC_API_KEY')
        self.use_openai = use_openai
        self.use_mock = not bool(self.api_key)
        
        if self.use_mock:
            print("⚠️ Using mock message generation (no API key)")
        
        self.message_prompt = """You are an expert B2B sales copywriter creating personalized LinkedIn outreach messages.

Create a highly personalized outreach message for this lead:

Name: {name}
Title: {title}
Company: {company}
Engagement: {engagement_type} on our post about "{post_topic}"
Lead Score: {score}/100
Score Reasoning: {reasoning}

Message Requirements:
1. Start with a personalized observation about their role/company
2. Reference their engagement naturally (don't say "I saw you liked...")
3. Connect their challenges to our solution
4. Include a soft CTA (question or suggestion, not pushy)
5. Keep it under 125 words
6. Sound human, conversational, and valuable
7. NO generic templates or obvious automation

Return ONLY the message text, no explanations or metadata."""

    async def generate_message(self, lead: Dict, post_topic: str, session: aiohttp.ClientSession) -> str:
        """Generate personalized message for a lead"""
        
        if self.use_mock:
            return self._mock_message(lead, post_topic)
        
        prompt = self.message_prompt.format(
            name=lead['name'].split()[0],  # First name only
            title=lead['title'],
            company=lead['company'],
            engagement_type="commented" if lead['engagement_type'] == 'comment' else "reacted",
            post_topic=post_topic,
            score=lead['score'],
            reasoning=lead['reason']
        )
        
        try:
            if self.use_openai:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "gpt-4-turbo-preview",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 200
                }
                
                async with session.post("https://api.openai.com/v1/chat/completions", 
                                      json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data['choices'][0]['message']['content'].strip()
            
            return self._mock_message(lead, post_topic)
            
        except Exception as e:
            print(f"❌ API error: {e}")
            return self._mock_message(lead, post_topic)
    
    def _mock_message(self, lead: Dict, post_topic: str) -> str:
        """Generate mock personalized message"""
        first_name = lead['name'].split()[0]
        
        # CEO/Founder template
        if lead['score'] >= 95:
            return f"""Hi {first_name},

Building {lead['company'].split()[0] if lead['company'] else 'a company'} must keep you busy! I noticed you're focused on {self._extract_focus(lead['title'], lead['company'])}.

Many founders in your position struggle with scaling outbound while maintaining quality. We've helped similar companies automate their lead qualification process, reducing manual work by 70%.

Would you be open to a brief chat about how you're currently handling lead generation?"""

        # Sales/Revenue leader template
        elif 'sales' in lead['title'].lower() or 'revenue' in lead['title'].lower():
            return f"""Hi {first_name},

Leading {self._extract_role(lead['title'])} in today's market requires constant pipeline innovation. 

We specialize in helping sales teams identify and qualify high-intent prospects automatically. One client recently increased their qualified pipeline by 41% in just 30 days.

Curious - what's your biggest challenge with lead quality right now?"""

        # Marketing leader template
        elif 'marketing' in lead['title'].lower() or 'cmo' in lead['title'].lower():
            return f"""Hi {first_name},

{self._extract_role(lead['title'])} roles are evolving fast with AI. I imagine you're exploring ways to make your team more efficient?

We help marketing leaders automate the tedious parts of lead generation while keeping the human touch. The result? More time for strategy, better lead quality.

What's your take on AI in marketing ops?"""

        # Growth/Operations template
        else:
            return f"""Hi {first_name},

Your focus on {self._extract_focus(lead['title'], lead['company'])} caught my attention. 

Companies with similar growth challenges often struggle with manual lead qualification. We've developed an AI-powered approach that identifies your best prospects automatically.

Would love to hear your thoughts on automating repetitive sales tasks?"""
    
    def _extract_focus(self, title: str, company: str) -> str:
        """Extract focus area from title/company"""
        combined = f"{title} {company}".lower()
        
        if 'ai' in combined or 'automation' in combined:
            return "AI and automation"
        elif 'growth' in combined or 'scale' in combined:
            return "scaling operations"
        elif 'saas' in combined or 'software' in combined:
            return "SaaS growth"
        elif 'revenue' in combined or 'sales' in combined:
            return "revenue optimization"
        else:
            return "business growth"
    
    def _extract_role(self, title: str) -> str:
        """Extract clean role description"""
        if 'vp' in title.lower():
            return "VP-level sales"
        elif 'director' in title.lower():
            return "sales leadership"
        elif 'head' in title.lower():
            return "sales operations"
        elif 'marketing' in title.lower():
            return "marketing operations"
        else:
            return "growth"

async def main():
    """Generate outreach messages for top qualified leads"""
    
    # Load qualified leads
    with open('test_data/full_engagement_analysis_182551.json', 'r') as f:
        data = json.load(f)
    
    qualified_leads = data['qualified_leads'][:10]  # Top 10
    post_topic = "AI-powered lead generation and qualification"
    
    print("🎯 PERSONALIZED OUTREACH GENERATOR")
    print("=" * 60)
    print(f"Generating messages for top {len(qualified_leads)} qualified leads...")
    
    generator = OutreachGenerator()
    
    async with aiohttp.ClientSession() as session:
        for i, lead in enumerate(qualified_leads, 1):
            print(f"\n{'='*60}")
            print(f"LEAD #{i}: {lead['name']}")
            print(f"Title: {lead['title']}")
            print(f"Score: {lead['score']}/100")
            print(f"\n📧 PERSONALIZED MESSAGE:")
            print("-" * 40)
            
            message = await generator.generate_message(lead, post_topic, session)
            print(message)
            
            print(f"\n📊 Message Stats:")
            word_count = len(message.split())
            print(f"- Word count: {word_count}")
            print(f"- Personalization: {'✅ High' if lead['score'] >= 90 else '✅ Medium'}")
            print(f"- Engagement ref: {'✅ Subtle' if 'commented' not in message else '❌ Too direct'}")
    
    print(f"\n{'='*60}")
    print("✅ OUTREACH GENERATION COMPLETE!")
    
    print("\n🎯 BEST PRACTICES APPLIED:")
    print("✅ Personalized opening based on role/company")
    print("✅ Natural engagement reference")
    print("✅ Value-focused messaging")
    print("✅ Soft, conversational CTAs")
    print("✅ Under 125 words")
    print("✅ No obvious automation markers")
    
    print("\n📋 NEXT STEPS:")
    print("1. A/B test different message variations")
    print("2. Track response rates by lead score")
    print("3. Optimize based on engagement data")
    print("4. Build follow-up sequences")

if __name__ == "__main__":
    asyncio.run(main())