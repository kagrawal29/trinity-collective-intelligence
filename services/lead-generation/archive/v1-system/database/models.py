"""Database models for lead qualification system"""

from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass
import json


@dataclass
class Profile:
    """LinkedIn Profile model"""
    id: Optional[int] = None
    linkedin_url: str = ""
    full_name: str = ""
    headline: str = ""
    followers: int = 0
    connections: int = 0
    about: str = ""
    profile_data: Dict[str, Any] = None
    fetched_at: datetime = None
    updated_at: datetime = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return {
            'id': self.id,
            'linkedin_url': self.linkedin_url,
            'full_name': self.full_name,
            'headline': self.headline,
            'followers': self.followers,
            'connections': self.connections,
            'about': self.about,
            'profile_data': json.dumps(self.profile_data) if self.profile_data else None,
            'fetched_at': self.fetched_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_api_response(cls, linkedin_url: str, api_data: Dict[str, Any]) -> 'Profile':
        """Create Profile from LinkedIn API response"""
        return cls(
            linkedin_url=linkedin_url,
            full_name=api_data.get('fullName', ''),
            headline=api_data.get('headline', ''),
            followers=api_data.get('followers', 0),
            connections=api_data.get('connections', 0),
            about=api_data.get('about', ''),
            profile_data=api_data,
            fetched_at=datetime.now()
        )


@dataclass
class Qualification:
    """Qualification analysis model"""
    id: Optional[int] = None
    profile_id: int = None
    decision_maker: bool = False
    decision_maker_reason: str = ""
    decision_maker_confidence: int = 0
    competitor: bool = False
    competitor_reason: str = ""
    competitor_confidence: int = 0
    influencer_score: int = 0
    influencer_reason: str = ""
    posting_frequency: str = ""
    is_qualified: bool = False
    qualification_summary: str = ""
    disqualification_reason: str = ""
    overall_score: int = 0
    analyzed_at: datetime = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'decision_maker': self.decision_maker,
            'decision_maker_reason': self.decision_maker_reason,
            'decision_maker_confidence': self.decision_maker_confidence,
            'competitor': self.competitor,
            'competitor_reason': self.competitor_reason,
            'competitor_confidence': self.competitor_confidence,
            'influencer_score': self.influencer_score,
            'influencer_reason': self.influencer_reason,
            'posting_frequency': self.posting_frequency,
            'is_qualified': self.is_qualified,
            'qualification_summary': self.qualification_summary,
            'disqualification_reason': self.disqualification_reason,
            'overall_score': self.overall_score,
            'analyzed_at': self.analyzed_at
        }


@dataclass
class Lead:
    """Lead tracking model"""
    id: Optional[int] = None
    profile_id: Optional[int] = None
    source_file: str = ""
    source_row_number: int = 0
    linkedin_url: str = ""
    original_data: Dict[str, Any] = None
    processing_status: str = "pending"
    error_message: str = ""
    processed_at: Optional[datetime] = None
    created_at: datetime = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'source_file': self.source_file,
            'source_row_number': self.source_row_number,
            'linkedin_url': self.linkedin_url,
            'original_data': json.dumps(self.original_data) if self.original_data else None,
            'processing_status': self.processing_status,
            'error_message': self.error_message,
            'processed_at': self.processed_at,
            'created_at': self.created_at
        }


@dataclass
class ProcessingBatch:
    """Batch processing tracking model"""
    id: Optional[int] = None
    source_file: str = ""
    total_leads: int = 0
    processed_leads: int = 0
    qualified_leads: int = 0
    started_at: datetime = None
    completed_at: Optional[datetime] = None
    status: str = "running"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return {
            'id': self.id,
            'source_file': self.source_file,
            'total_leads': self.total_leads,
            'processed_leads': self.processed_leads,
            'qualified_leads': self.qualified_leads,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'status': self.status
        }