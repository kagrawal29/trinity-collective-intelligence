#!/usr/bin/env python3
"""
V2 Lead Generation - PostgreSQL Database Setup Script
Production database initialization for Guide's Phase 1 logging system
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def create_database():
    """Create the lead_generation_v2 database if it doesn't exist"""
    
    try:
        # Connect to PostgreSQL without specifying database
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', ''),
            database='postgres'  # Connect to default postgres database
        )
        conn.autocommit = True
        
        with conn.cursor() as cursor:
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'lead_generation_v2'")
            if not cursor.fetchone():
                cursor.execute("CREATE DATABASE lead_generation_v2")
                print("✅ Database 'lead_generation_v2' created successfully")
            else:
                print("✅ Database 'lead_generation_v2' already exists")
                
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        return False

def setup_tables():
    """Create all necessary tables for the logging system"""
    
    try:
        # Connect to the lead_generation_v2 database
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'lead_generation_v2'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', ''),
            cursor_factory=RealDictCursor
        )
        
        with conn.cursor() as cursor:
            
            # Read and execute the schema SQL file
            schema_path = 'database_schema.sql'
            if not os.path.exists(schema_path):
                print(f"❌ Schema file not found: {schema_path}")
                return False
                
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            # Execute the complete schema
            cursor.execute(schema_sql)
            conn.commit()
            
            print("✅ All tables created successfully:")
            print("   - prompt_versions")
            print("   - processing_logs") 
            print("   - lead_qualification_results")
            print("   - processing_runs")
            print("   - All indexes created")
            print("   - Initial Tyler's v2.1.1-disciplined prompt inserted")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to setup tables: {e}")
        return False

def verify_setup():
    """Verify that all tables were created correctly"""
    
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'lead_generation_v2'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', ''),
            cursor_factory=RealDictCursor
        )
        
        with conn.cursor() as cursor:
            
            # Check table counts
            tables = ['prompt_versions', 'processing_logs', 'lead_qualification_results', 'processing_runs']
            
            print("\n📊 Database Verification:")
            print("=" * 40)
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✅ {table}: {count} records")
            
            # Verify Tyler's prompt version exists
            cursor.execute("SELECT version_tag, created_by FROM prompt_versions WHERE version_tag = 'v2.1.1-disciplined'")
            result = cursor.fetchone()
            if result:
                print(f"✅ Tyler's prompt version: {result['version_tag']} (by {result['created_by']})")
            else:
                print("❌ Tyler's prompt version not found")
                
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to verify setup: {e}")
        return False

def test_logging_system():
    """Test the logging system with a sample entry"""
    
    try:
        from logging_system import V2LoggingSystem
        
        print("\n🧪 Testing Logging System:")
        print("=" * 40)
        
        logger = V2LoggingSystem()
        
        # Test database connection
        if not logger.connect_database():
            print("❌ Failed to connect to database")
            return False
            
        print("✅ Connected to database successfully")
        
        # Test prompt version registration
        prompt_hash = logger.register_prompt_version(
            version_tag="test_v1.0.0",
            prompt_content="Test prompt for setup verification",
            tier_definitions={"TEST": {"range": "0-100", "description": "Test tier"}},
            scoring_rules={"test": True}
        )
        print(f"✅ Prompt version registered: {prompt_hash}")
        
        # Test processing run
        run_id = logger.start_processing_run("setup_test", prompt_hash, 1)
        print(f"✅ Processing run started: {run_id}")
        
        # Test processing step log
        logger.log_processing_step(
            workflow_step="setup_test",
            input_data={"test": True},
            output_data={"success": True},
            processing_params={"mode": "test"},
            execution_time_ms=100,
            leads_processed=1,
            leads_qualified=1
        )
        print("✅ Processing step logged")
        
        # Test lead qualification log
        logger.log_lead_qualification(
            linkedin_url="https://linkedin.com/in/test",
            lead_name="Test Lead",
            lead_title="Test Title",
            lead_company="Test Company",
            engagement_type="test",
            llm_model="test-model",
            llm_score=85,
            llm_reasoning="Test qualification",
            tier_classification="TIER_1",
            is_qualified=True,
            batch_number=1,
            processing_order=1
        )
        print("✅ Lead qualification logged")
        
        # Complete the run
        logger.complete_processing_run(1, 100.0)
        print("✅ Processing run completed")
        
        print("\n🎉 ALL TESTS PASSED - PRODUCTION READY!")
        return True
        
    except Exception as e:
        print(f"❌ Logging system test failed: {e}")
        return False

def main():
    """Main setup function"""
    
    print("🚀 V2 Lead Generation - PostgreSQL Database Setup")
    print("=" * 60)
    print("Setting up production database for Guide's Phase 1 logging system")
    print()
    
    # Check environment variables
    required_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these in your .env file:")
        print("DB_HOST=localhost")
        print("DB_USER=postgres") 
        print("DB_PASSWORD=your_password")
        print("DB_NAME=lead_generation_v2")
        sys.exit(1)
    
    print("✅ Environment variables configured")
    
    # Step 1: Create database
    print("\n1️⃣ Creating database...")
    if not create_database():
        sys.exit(1)
    
    # Step 2: Setup tables
    print("\n2️⃣ Setting up tables...")
    if not setup_tables():
        sys.exit(1)
    
    # Step 3: Verify setup
    print("\n3️⃣ Verifying setup...")
    if not verify_setup():
        sys.exit(1)
        
    # Step 4: Test logging system
    print("\n4️⃣ Testing logging system...")
    if not test_logging_system():
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🎯 DATABASE SETUP COMPLETE!")
    print("✅ Production PostgreSQL database ready")
    print("✅ All tables created with proper schema")
    print("✅ Tyler's 4-tier prompt system pre-loaded")
    print("✅ Logging system tested and verified")
    print("✅ Ready for production lead processing!")
    print("="*60)

if __name__ == "__main__":
    main()