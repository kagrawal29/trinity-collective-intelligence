# Lead Qualification System Architecture

## Overview
A scalable system for batch processing LinkedIn leads with profile storage, qualification analysis, and CSV updates.

## System Components

### 1. Data Storage Layer

#### Profile Database (SQLite/PostgreSQL)
```sql
-- profiles table
CREATE TABLE profiles (
    id INTEGER PRIMARY KEY,
    linkedin_url TEXT UNIQUE,
    full_name TEXT,
    headline TEXT,
    followers INTEGER,
    connections INTEGER,
    about TEXT,
    profile_data JSON,  -- Full API response
    fetched_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- qualifications table
CREATE TABLE qualifications (
    id INTEGER PRIMARY KEY,
    profile_id INTEGER REFERENCES profiles(id),
    decision_maker BOOLEAN,
    decision_maker_reason TEXT,
    competitor BOOLEAN,
    competitor_reason TEXT,
    influencer_score INTEGER,
    influencer_reason TEXT,
    is_qualified BOOLEAN,
    qualification_summary TEXT,
    disqualification_reason TEXT,
    analyzed_at TIMESTAMP
);

-- leads table (mirrors CSV structure)
CREATE TABLE leads (
    id INTEGER PRIMARY KEY,
    profile_id INTEGER REFERENCES profiles(id),
    source_file TEXT,
    row_data JSON,  -- Original CSV row
    processed_at TIMESTAMP
);
```

### 2. Processing Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   CSV Input     │────▶│  Lead Processor  │────▶│  CSV Output     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Profile Fetcher   │
                    │  (RapidAPI Cache)   │
                    └─────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    LLM Analyzer     │
                    │  (OpenAI GPT-4)     │
                    └─────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   SQLite Database   │
                    │  - Profiles         │
                    │  - Qualifications   │
                    │  - Leads            │
                    └─────────────────────┘
```

### 3. Recommended Implementation Approach

#### Phase 1: Database Setup (Current Priority)
1. Use SQLite for simplicity (can migrate to PostgreSQL later)
2. Store full profile JSON for future analysis
3. Index on linkedin_url for fast lookups

#### Phase 2: Batch Processing Pipeline
```python
class LeadQualificationPipeline:
    def __init__(self):
        self.db = DatabaseManager()
        self.fetcher = ProfileFetcher()
        self.analyzer = LLMAnalyzer()
    
    def process_batch(self, csv_file):
        # 1. Load CSV
        leads = self.load_csv(csv_file)
        
        # 2. For each lead:
        for lead in leads:
            # Check if profile exists in DB
            profile = self.db.get_profile(lead.linkedin_url)
            
            if not profile or self.is_stale(profile):
                # Fetch from API
                profile = self.fetcher.fetch(lead.linkedin_url)
                self.db.save_profile(profile)
            
            # Check if qualification exists
            qualification = self.db.get_qualification(profile.id)
            
            if not qualification:
                # Analyze with LLM
                qualification = self.analyzer.analyze(profile)
                self.db.save_qualification(qualification)
            
            # Update lead record
            lead.update(qualification)
        
        # 3. Export updated CSV
        self.export_csv(leads)
```

#### Phase 3: Optimization Features
1. **Parallel Processing**: Process multiple leads concurrently
2. **Rate Limiting**: Respect API limits (X requests/minute)
3. **Progress Tracking**: Resume from interruptions
4. **Error Handling**: Retry failed requests, log errors

### 4. File Structure
```
services/lead-generation/
├── database/
│   ├── __init__.py
│   ├── models.py          # SQLAlchemy models
│   ├── manager.py         # Database operations
│   └── schema.sql         # Schema definition
├── processors/
│   ├── __init__.py
│   ├── profile_fetcher.py # RapidAPI integration
│   ├── llm_analyzer.py    # OpenAI analysis
│   └── csv_processor.py   # CSV I/O
├── pipeline/
│   ├── __init__.py
│   ├── orchestrator.py    # Main pipeline
│   └── batch_processor.py # Batch operations
├── config/
│   ├── settings.py        # Configuration
│   └── .env              # Environment vars
└── main.py               # Entry point
```

### 5. Key Benefits

1. **Data Persistence**: Never lose fetched profiles
2. **Deduplication**: Don't re-fetch same profiles
3. **Incremental Processing**: Add new leads anytime
4. **Analytics Ready**: Query qualified leads easily
5. **Scalable**: Can handle millions of leads

### 6. Next Steps

1. **Immediate**: Create SQLite database schema
2. **Short-term**: Refactor existing code into modular structure
3. **Medium-term**: Add web dashboard for monitoring
4. **Long-term**: API endpoints for integration

### 7. Example Usage

```bash
# Process first 100 leads
python main.py --input leads.csv --limit 100

# Resume processing
python main.py --input leads.csv --resume

# Export qualified leads only
python main.py --export-qualified qualified_leads.csv

# Re-analyze with updated criteria
python main.py --reanalyze --input leads.csv
```

## Recommended Implementation Order

1. **Database Setup** (2 hours)
   - Create schema
   - Build models
   - Test CRUD operations

2. **Refactor Fetcher** (1 hour)
   - Add database caching
   - Implement staleness check

3. **Refactor Analyzer** (1 hour)
   - Modularize LLM calls
   - Add database storage

4. **CSV Integration** (2 hours)
   - Update processor
   - Add progress tracking
   - Implement resume capability

5. **Testing & Optimization** (2 hours)
   - Error handling
   - Performance tuning
   - Documentation