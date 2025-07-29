# V2 Lead Generation - Database Setup Guide

## 🚀 Production PostgreSQL Setup

### Prerequisites
1. PostgreSQL 12+ installed and running
2. Python 3.8+ with required packages
3. Environment variables configured

### Quick Setup

1. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your PostgreSQL credentials
   ```

2. **Run Database Setup**
   ```bash
   python3 database_setup.py
   ```

3. **Verify Installation**
   The setup script will automatically:
   - Create `lead_generation_v2` database
   - Create all required tables with proper schema
   - Insert Tyler's 4-tier prompt system
   - Test logging system functionality
   - Verify production readiness

### Environment Variables Required

```env
DB_HOST=localhost
DB_NAME=lead_generation_v2  
DB_USER=postgres
DB_PASSWORD=your_password
OPENAI_API_KEY=your_openai_key
```

### Database Schema

- **prompt_versions**: Git-style prompt versioning with SHA256 hashing
- **processing_runs**: Run metadata and completion tracking
- **processing_logs**: Step-by-step processing provenance
- **lead_qualification_results**: Individual lead scoring results

### Production Features

✅ **NO MOCK DATA** - All operations require database connection  
✅ **Full Provenance** - Every lead qualification tracked  
✅ **Git-style Versioning** - Prompt changes tracked with hashes  
✅ **Comprehensive Logging** - Processing steps, errors, performance  
✅ **Tyler's 4-tier System** - Pre-loaded disciplined buyer classification  

### Usage

```bash
# Run production analysis with full logging
python3 analyze_batch_llm_logged.py
```

This will process all leads with comprehensive database logging and Tyler's disciplined 4-tier buyer classification system.

### Troubleshooting

If database connection fails:
1. Verify PostgreSQL is running
2. Check credentials in .env file  
3. Ensure database user has CREATE privileges
4. Review error messages from setup script

---
*Built by Trinity Collective Intelligence - Guide's Phase 1 Logging Vision*