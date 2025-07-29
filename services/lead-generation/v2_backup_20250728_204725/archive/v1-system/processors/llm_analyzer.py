"""LLM-based qualification analyzer"""

import os
import json
from typing import Dict, Any
from datetime import datetime
from openai import OpenAI

from database.models import Profile, Qualification
from database.manager import DatabaseManager


class LLMAnalyzer:
    """Analyzes profiles using LLM for qualification"""
    
    def __init__(self, db_manager: DatabaseManager, api_key: str = None):
        self.db = db_manager
        self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
        
        # Load service description
        service_desc_path = 'our-service-description.md'
        if os.path.exists(service_desc_path):
            with open(service_desc_path, 'r') as f:
                self.service_description = f.read()
        else:
            self.service_description = "AI-powered lead generation platform for outbound sales teams"
    
    def analyze_profile(self, profile: Profile, force_reanalyze: bool = False) -> Qualification:
        """
        Analyze profile for qualification
        
        Args:
            profile: Profile to analyze
            force_reanalyze: Force re-analysis even if cached
            
        Returns:
            Qualification object
        """
        # Check for existing qualification
        if not force_reanalyze:
            existing = self.db.get_qualification_by_profile_id(profile.id)
            if existing:
                print(f"  📋 Using cached qualification analysis")
                return existing
        
        print(f"  🤖 Analyzing with LLM...")
        
        # Perform analyses
        dm_analysis = self._analyze_decision_maker(profile)
        comp_analysis = self._analyze_competitor(profile)
        inf_analysis = self._analyze_influencer(profile)
        
        # Calculate overall qualification
        is_qualified = (
            dm_analysis['is_decision_maker'] and 
            not comp_analysis['is_competitor'] and 
            inf_analysis['influencer_score'] < 70
        )
        
        # Build disqualification reasons
        disqual_reasons = []
        if not dm_analysis['is_decision_maker']:
            disqual_reasons.append("Not a decision maker")
        if comp_analysis['is_competitor']:
            disqual_reasons.append("Competitor")
        if inf_analysis['influencer_score'] >= 70:
            disqual_reasons.append(f"Influencer (score: {inf_analysis['influencer_score']})")
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(dm_analysis, comp_analysis, inf_analysis, is_qualified)
        
        # Create qualification object
        qualification = Qualification(
            profile_id=profile.id,
            decision_maker=dm_analysis['is_decision_maker'],
            decision_maker_reason=dm_analysis['reasoning'][:200],
            decision_maker_confidence=dm_analysis.get('confidence', 0),
            competitor=comp_analysis['is_competitor'],
            competitor_reason=comp_analysis['reasoning'][:200],
            competitor_confidence=comp_analysis.get('confidence', 0),
            influencer_score=inf_analysis['influencer_score'],
            influencer_reason=inf_analysis['reasoning'][:200],
            posting_frequency=inf_analysis.get('posting_frequency', 'unknown'),
            is_qualified=is_qualified,
            qualification_summary=self._generate_summary(profile, is_qualified, disqual_reasons),
            disqualification_reason='; '.join(disqual_reasons) if disqual_reasons else '',
            overall_score=overall_score,
            analyzed_at=datetime.now()
        )
        
        # Save to database
        qualification.id = self.db.save_qualification(qualification)
        
        print(f"  ✅ Analysis complete - Qualified: {'YES' if is_qualified else 'NO'}")
        return qualification
    
    def _analyze_decision_maker(self, profile: Profile) -> Dict[str, Any]:
        """Analyze if person is a decision maker"""
        prompt = f"""Based on this LinkedIn profile, determine if this person is a decision maker who could purchase our lead generation service.

Our Service: {self.service_description}

Profile:
- Name: {profile.full_name}
- Headline: {profile.headline}
- About: {profile.about[:500] if profile.about else 'Not provided'}

Focus on titles like: CEO, CMO, CRO, VP Sales/Marketing, Director, Head of Sales/Growth

Return JSON with:
1. "is_decision_maker": true/false
2. "confidence": 0-100
3. "reasoning": brief explanation (max 150 chars)"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {
                "is_decision_maker": False,
                "confidence": 0,
                "reasoning": f"Analysis error: {str(e)[:50]}"
            }
    
    def _analyze_competitor(self, profile: Profile) -> Dict[str, Any]:
        """Analyze if person/company is a competitor"""
        # Extract experience info from profile data
        experiences_text = ""
        if profile.profile_data and 'experiences' in profile.profile_data:
            for exp in profile.profile_data['experiences'][:3]:
                title = exp.get('title', '')
                company = exp.get('subtitle', '')
                experiences_text += f"\n- {title} at {company}"
        
        prompt = f"""Analyze if this person or their company is a competitor to our lead generation service.

Our Service: AI-powered lead generation platform for outbound sales teams

Profile:
- Name: {profile.full_name}
- Headline: {profile.headline}
- Experience: {experiences_text[:500]}

Competitors would offer: lead generation, sales automation, AI SDR, outbound tools

Return JSON with:
1. "is_competitor": true/false
2. "confidence": 0-100
3. "reasoning": brief explanation (max 150 chars)"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {
                "is_competitor": False,
                "confidence": 0,
                "reasoning": f"Analysis error: {str(e)[:50]}"
            }
    
    def _analyze_influencer(self, profile: Profile) -> Dict[str, Any]:
        """Analyze influencer status"""
        # Count posts if available
        post_count = 0
        if profile.profile_data and 'updates' in profile.profile_data:
            post_count = len(profile.profile_data['updates'])
        
        prompt = f"""Determine if this person is an influencer (regular content creator).

Profile:
- Followers: {profile.followers:,}
- Connections: {profile.connections:,}
- Recent Posts: {post_count}

TRUE INFLUENCER criteria (score 70+):
- Posts 2+ times/week (8+ posts/month)
- 10k+ followers preferred
- High engagement on posts
- Thought leadership content

Score 0-69 = Not influencer, 70-100 = Influencer

Return JSON with:
1. "influencer_score": 0-100
2. "posting_frequency": "regular"/"occasional"/"rare"
3. "reasoning": brief explanation (max 150 chars)"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {
                "influencer_score": 0,
                "posting_frequency": "unknown",
                "reasoning": f"Analysis error: {str(e)[:50]}"
            }
    
    def _calculate_overall_score(self, dm_analysis: Dict, comp_analysis: Dict, 
                                inf_analysis: Dict, is_qualified: bool) -> int:
        """Calculate overall lead score (0-100)"""
        score = 0
        
        # Decision maker weight: 40 points
        if dm_analysis['is_decision_maker']:
            score += 40 * (dm_analysis.get('confidence', 50) / 100)
        
        # Non-competitor weight: 30 points
        if not comp_analysis['is_competitor']:
            score += 30
        
        # Non-influencer weight: 30 points
        if inf_analysis['influencer_score'] < 70:
            score += 30 * ((70 - inf_analysis['influencer_score']) / 70)
        
        # Bonus for perfect qualification
        if is_qualified:
            score = min(100, score + 10)
        
        return int(score)
    
    def _generate_summary(self, profile: Profile, is_qualified: bool, 
                         disqual_reasons: list) -> str:
        """Generate qualification summary"""
        if is_qualified:
            return f"{profile.full_name} is a qualified lead - decision maker in a non-competing company with business-focused profile"
        else:
            return f"{profile.full_name} is not qualified - {', '.join(disqual_reasons)}"
    
    def bulk_analyze(self, profiles: list) -> Dict[int, Qualification]:
        """Analyze multiple profiles"""
        results = {}
        
        for i, profile in enumerate(profiles):
            print(f"\n[{i+1}/{len(profiles)}] Analyzing {profile.full_name}")
            qualification = self.analyze_profile(profile)
            results[profile.id] = qualification
        
        return results