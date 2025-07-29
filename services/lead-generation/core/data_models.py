"""
Minimal Data Models for V2 Lead Generation
Based on LinkedIn API responses - LEAN approach
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class QualificationStatus(Enum):
    """Lead qualification status"""
    PENDING = "pending"
    RELEVANT = "relevant" 
    NOT_RELEVANT = "not_relevant"
    NEEDS_REVIEW = "needs_review"

@dataclass
class InfluencerProfile:
    """Minimal influencer data model"""
    linkedin_url: str
    full_name: str
    headline: str
    follower_count: int
    raw_data: Dict[str, Any]  # Store complete response
    
    @classmethod
    def from_api_response(cls, url: str, api_data: Dict[str, Any]) -> 'InfluencerProfile':
        """Create from LinkedIn API response"""
        data = api_data.get('data', {})
        return cls(
            linkedin_url=url,
            full_name=data.get('fullName', ''),
            headline=data.get('headline', ''),
            follower_count=data.get('followerCount', 0),
            raw_data=api_data
        )

@dataclass  
class InfluencerPost:
    """Minimal post data model"""
    post_url: str
    text: str
    reactions_count: int
    comments_count: int
    reactions_urn: Optional[str] = None
    comments_urn: Optional[str] = None
    posted_at: Optional[datetime] = None
    raw_data: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_api_response(cls, post_data: Dict[str, Any]) -> 'InfluencerPost':
        """Create from LinkedIn API response"""
        return cls(
            post_url=post_data.get('url', ''),
            text=post_data.get('text', ''),
            reactions_count=post_data.get('reactionsCount', 0),
            comments_count=post_data.get('commentsCount', 0),
            reactions_urn=post_data.get('reactionsUrn'),
            comments_urn=post_data.get('commentsUrn'),
            posted_at=post_data.get('postedAt'),  # Parse later if needed
            raw_data=post_data
        )
    
    def is_relevant_to_lead_gen(self) -> bool:
        """Check if post is relevant to lead generation"""
        keywords = ['lead', 'outbound', 'sales', 'sdr', 'pipeline', 
                   'prospect', 'outreach', 'cold email', 'linkedin']
        text_lower = self.text.lower()
        return any(keyword in text_lower for keyword in keywords)

@dataclass
class EngagedProspect:
    """Minimal engaged prospect model"""
    profile_url: str
    full_name: str
    title: str
    subtitle: str  # Usually company name
    reaction_type: str
    qualification_status: QualificationStatus = QualificationStatus.PENDING
    qualification_score: Optional[int] = None
    qualification_notes: Optional[str] = None
    
    @classmethod
    def from_reaction_data(cls, reaction: Dict[str, Any]) -> 'EngagedProspect':
        """Create from reaction API data"""
        profile = reaction.get('profile', {})
        return cls(
            profile_url=profile.get('url', ''),
            full_name=profile.get('fullName', ''),
            title=profile.get('title', ''),
            subtitle=profile.get('subtitle', ''),
            reaction_type=reaction.get('reactionType', 'LIKE')
        )
    
    def get_qualification_context(self) -> str:
        """Get context string for LLM qualification"""
        return f"{self.title} at {self.subtitle}"

@dataclass
class QualificationCriteria:
    """Criteria for qualifying leads"""
    target_titles: List[str] = None
    target_companies: List[str] = None
    min_company_size: Optional[int] = None
    max_company_size: Optional[int] = None
    industries: List[str] = None
    exclude_titles: List[str] = None
    
    def __post_init__(self):
        # Default values
        if self.target_titles is None:
            self.target_titles = [
                'sales', 'business development', 'sdr', 'bdr',
                'account executive', 'growth', 'revenue', 'demand gen'
            ]
        if self.exclude_titles is None:
            self.exclude_titles = [
                'student', 'intern', 'freelance', 'consultant'
            ]

@dataclass
class TestSession:
    """Track a test session"""
    session_id: str
    influencer_url: str
    start_time: datetime
    end_time: Optional[datetime] = None
    posts_analyzed: int = 0
    prospects_found: int = 0
    prospects_qualified: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
    
    def add_error(self, error: str):
        """Add error to session"""
        self.errors.append(f"{datetime.now()}: {error}")
    
    def complete(self):
        """Mark session as complete"""
        self.end_time = datetime.now()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get session summary"""
        return {
            'session_id': self.session_id,
            'influencer_url': self.influencer_url,
            'duration_seconds': (self.end_time - self.start_time).total_seconds() if self.end_time else None,
            'posts_analyzed': self.posts_analyzed,
            'prospects_found': self.prospects_found,
            'prospects_qualified': self.prospects_qualified,
            'qualification_rate': self.prospects_qualified / self.prospects_found if self.prospects_found > 0 else 0,
            'errors': len(self.errors)
        }