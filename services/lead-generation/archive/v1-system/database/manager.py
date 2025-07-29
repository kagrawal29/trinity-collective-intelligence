"""Database manager for lead qualification system"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
import os

from .models import Profile, Qualification, Lead, ProcessingBatch


class DatabaseManager:
    """Manages all database operations"""
    
    def __init__(self, db_path: str = "lead_qualification.db"):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database with schema"""
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as f:
            schema = f.read()
        
        with self.get_connection() as conn:
            conn.executescript(schema)
            conn.commit()
    
    # Profile operations
    def save_profile(self, profile: Profile) -> int:
        """Save or update profile"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if profile exists
            existing = cursor.execute(
                "SELECT id FROM profiles WHERE linkedin_url = ?",
                (profile.linkedin_url,)
            ).fetchone()
            
            if existing:
                # Update existing profile
                profile.id = existing['id']
                profile.updated_at = datetime.now()
                cursor.execute("""
                    UPDATE profiles SET
                        full_name = ?, headline = ?, followers = ?,
                        connections = ?, about = ?, profile_data = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (
                    profile.full_name, profile.headline, profile.followers,
                    profile.connections, profile.about,
                    json.dumps(profile.profile_data),
                    profile.updated_at, profile.id
                ))
            else:
                # Insert new profile
                cursor.execute("""
                    INSERT INTO profiles (
                        linkedin_url, full_name, headline, followers,
                        connections, about, profile_data, fetched_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile.linkedin_url, profile.full_name, profile.headline,
                    profile.followers, profile.connections, profile.about,
                    json.dumps(profile.profile_data), datetime.now()
                ))
                profile.id = cursor.lastrowid
            
            conn.commit()
            return profile.id
    
    def get_profile_by_url(self, linkedin_url: str) -> Optional[Profile]:
        """Get profile by LinkedIn URL"""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM profiles WHERE linkedin_url = ?",
                (linkedin_url,)
            ).fetchone()
            
            if row:
                profile = Profile(
                    id=row['id'],
                    linkedin_url=row['linkedin_url'],
                    full_name=row['full_name'],
                    headline=row['headline'],
                    followers=row['followers'],
                    connections=row['connections'],
                    about=row['about'],
                    profile_data=json.loads(row['profile_data']) if row['profile_data'] else None,
                    fetched_at=row['fetched_at'],
                    updated_at=row['updated_at']
                )
                return profile
        return None
    
    def is_profile_stale(self, profile: Profile, days: int = 30) -> bool:
        """Check if profile data is stale"""
        if not profile.fetched_at:
            return True
        
        fetched_datetime = datetime.fromisoformat(profile.fetched_at)
        age_days = (datetime.now() - fetched_datetime).days
        return age_days > days
    
    # Qualification operations
    def save_qualification(self, qualification: Qualification) -> int:
        """Save qualification analysis"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if qualification exists for profile
            existing = cursor.execute(
                "SELECT id FROM qualifications WHERE profile_id = ?",
                (qualification.profile_id,)
            ).fetchone()
            
            if existing:
                # Update existing
                qualification.id = existing['id']
                cursor.execute("""
                    UPDATE qualifications SET
                        decision_maker = ?, decision_maker_reason = ?,
                        decision_maker_confidence = ?, competitor = ?,
                        competitor_reason = ?, competitor_confidence = ?,
                        influencer_score = ?, influencer_reason = ?,
                        posting_frequency = ?, is_qualified = ?,
                        qualification_summary = ?, disqualification_reason = ?,
                        overall_score = ?, analyzed_at = ?
                    WHERE id = ?
                """, (
                    qualification.decision_maker, qualification.decision_maker_reason,
                    qualification.decision_maker_confidence, qualification.competitor,
                    qualification.competitor_reason, qualification.competitor_confidence,
                    qualification.influencer_score, qualification.influencer_reason,
                    qualification.posting_frequency, qualification.is_qualified,
                    qualification.qualification_summary, qualification.disqualification_reason,
                    qualification.overall_score, datetime.now(),
                    qualification.id
                ))
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO qualifications (
                        profile_id, decision_maker, decision_maker_reason,
                        decision_maker_confidence, competitor, competitor_reason,
                        competitor_confidence, influencer_score, influencer_reason,
                        posting_frequency, is_qualified, qualification_summary,
                        disqualification_reason, overall_score, analyzed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    qualification.profile_id, qualification.decision_maker,
                    qualification.decision_maker_reason, qualification.decision_maker_confidence,
                    qualification.competitor, qualification.competitor_reason,
                    qualification.competitor_confidence, qualification.influencer_score,
                    qualification.influencer_reason, qualification.posting_frequency,
                    qualification.is_qualified, qualification.qualification_summary,
                    qualification.disqualification_reason, qualification.overall_score,
                    datetime.now()
                ))
                qualification.id = cursor.lastrowid
            
            conn.commit()
            return qualification.id
    
    def get_qualification_by_profile_id(self, profile_id: int) -> Optional[Qualification]:
        """Get qualification by profile ID"""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM qualifications WHERE profile_id = ?",
                (profile_id,)
            ).fetchone()
            
            if row:
                return Qualification(**dict(row))
        return None
    
    # Lead operations
    def save_lead(self, lead: Lead) -> int:
        """Save lead record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO leads (
                    profile_id, source_file, source_row_number,
                    linkedin_url, original_data, processing_status,
                    error_message, processed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lead.profile_id, lead.source_file, lead.source_row_number,
                lead.linkedin_url, json.dumps(lead.original_data),
                lead.processing_status, lead.error_message, lead.processed_at
            ))
            conn.commit()
            return cursor.lastrowid
    
    def update_lead_status(self, lead_id: int, status: str, 
                          error_message: str = None, profile_id: int = None):
        """Update lead processing status"""
        with self.get_connection() as conn:
            if error_message:
                conn.execute("""
                    UPDATE leads SET 
                        processing_status = ?, error_message = ?, 
                        processed_at = ?
                    WHERE id = ?
                """, (status, error_message, datetime.now(), lead_id))
            else:
                conn.execute("""
                    UPDATE leads SET 
                        processing_status = ?, profile_id = ?,
                        processed_at = ?
                    WHERE id = ?
                """, (status, profile_id, datetime.now(), lead_id))
            conn.commit()
    
    def get_pending_leads(self, source_file: str, limit: int = None) -> List[Dict]:
        """Get pending leads from a source file"""
        with self.get_connection() as conn:
            query = """
                SELECT * FROM leads 
                WHERE source_file = ? AND processing_status = 'pending'
                ORDER BY source_row_number
            """
            if limit:
                query += f" LIMIT {limit}"
            
            rows = conn.execute(query, (source_file,)).fetchall()
            return [dict(row) for row in rows]
    
    # Batch operations
    def create_batch(self, source_file: str, total_leads: int) -> int:
        """Create new processing batch"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO processing_batches (
                    source_file, total_leads, started_at
                ) VALUES (?, ?, ?)
            """, (source_file, total_leads, datetime.now()))
            conn.commit()
            return cursor.lastrowid
    
    def update_batch_progress(self, batch_id: int, processed: int, qualified: int):
        """Update batch processing progress"""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE processing_batches SET
                    processed_leads = ?, qualified_leads = ?
                WHERE id = ?
            """, (processed, qualified, batch_id))
            conn.commit()
    
    def complete_batch(self, batch_id: int, status: str = 'completed'):
        """Mark batch as complete"""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE processing_batches SET
                    status = ?, completed_at = ?
                WHERE id = ?
            """, (status, datetime.now(), batch_id))
            conn.commit()
    
    # Export operations
    def export_qualified_leads(self, source_file: str = None) -> List[Dict]:
        """Export qualified leads"""
        with self.get_connection() as conn:
            if source_file:
                query = """
                    SELECT * FROM qualified_leads_view 
                    WHERE source_file = ?
                    ORDER BY overall_score DESC
                """
                rows = conn.execute(query, (source_file,)).fetchall()
            else:
                query = """
                    SELECT * FROM qualified_leads_view 
                    ORDER BY overall_score DESC
                """
                rows = conn.execute(query).fetchall()
            
            return [dict(row) for row in rows]
    
    def get_statistics(self, source_file: str = None) -> Dict[str, Any]:
        """Get processing statistics"""
        with self.get_connection() as conn:
            if source_file:
                stats = conn.execute("""
                    SELECT 
                        COUNT(*) as total_leads,
                        SUM(CASE WHEN processing_status = 'completed' THEN 1 ELSE 0 END) as processed,
                        SUM(CASE WHEN q.is_qualified = 1 THEN 1 ELSE 0 END) as qualified
                    FROM leads l
                    LEFT JOIN qualifications q ON l.profile_id = q.profile_id
                    WHERE l.source_file = ?
                """, (source_file,)).fetchone()
            else:
                stats = conn.execute("""
                    SELECT 
                        COUNT(*) as total_leads,
                        SUM(CASE WHEN processing_status = 'completed' THEN 1 ELSE 0 END) as processed,
                        SUM(CASE WHEN q.is_qualified = 1 THEN 1 ELSE 0 END) as qualified
                    FROM leads l
                    LEFT JOIN qualifications q ON l.profile_id = q.profile_id
                """).fetchone()
            
            return dict(stats)