# V2 Lead Generation System Design - Critical Decisions

## 🏗️ Architecture Overview

### Key Questions We Need to Answer:

1. **Where does the data live?**
2. **What database should we use?**
3. **Should we use a framework (LangChain/LangGraph)?**
4. **How do we handle state management?**
5. **What's our deployment strategy?**
6. **How do we ensure scalability?**

## 💾 Data Architecture

### Data Categories & Storage Requirements

#### 1. **Transient Data** (Short-lived, API responses)
- Raw API responses
- Temporary processing data
- Rate limit counters
- **Storage**: Redis/In-memory cache
- **TTL**: 24-48 hours

#### 2. **Operational Data** (Pipeline state)
- Job queues
- Processing status
- Error logs
- Performance metrics
- **Storage**: PostgreSQL + Redis
- **Retention**: 30-90 days

#### 3. **Business Data** (Long-term value)
- Qualified leads
- Influencer profiles
- Engagement history
- Research reports
- **Storage**: PostgreSQL
- **Retention**: Indefinite

#### 4. **Analytics Data** (Insights)
- Lead quality metrics
- Conversion tracking
- Cost analysis
- **Storage**: PostgreSQL + Time-series DB
- **Retention**: 1 year+

### Database Decision Matrix

| Criteria | PostgreSQL | MongoDB | SQLite | DynamoDB |
|----------|------------|---------|---------|-----------|
| **Relational Integrity** | ✅ Excellent | ❌ Weak | ✅ Good | ❌ None |
| **JSON Support** | ✅ Native JSONB | ✅ Native | ⚠️ Text only | ✅ Native |
| **Scalability** | ✅ Vertical+Horizontal | ✅ Horizontal | ❌ Single file | ✅ Infinite |
| **Complex Queries** | ✅ SQL power | ⚠️ Limited | ✅ SQL | ❌ Basic |
| **Cost** | 💰 Medium | 💰 Medium | 💰 Free | 💰💰 High |
| **Operational Overhead** | ⚠️ Medium | ⚠️ Medium | ✅ None | ✅ Managed |

### 🎯 Recommended Data Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │   Redis     │  │  PostgreSQL  │  │   S3/CloudStore  │   │
│  │  (Cache)    │  │  (Primary)   │  │   (Archives)     │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
│        │                 │                    │               │
│        └─────────────────┴────────────────────┘              │
│                          │                                    │
│                    Data Access Layer                          │
└─────────────────────────────────────────────────────────────┘

Primary: PostgreSQL (with JSONB for flexibility)
Cache: Redis (for rate limits, temp data)
Archive: S3 (for logs, old data)
```

## 🤖 Framework Analysis

### LangChain vs LangGraph vs Custom

#### **LangChain**
✅ **Pros:**
- Rich ecosystem of tools
- Built-in LLM integrations
- Document loaders
- Vector store support
- Active community

❌ **Cons:**
- Heavy abstraction
- Overkill for our use case
- Learning curve
- Version instability

**Verdict**: Too heavy for our focused use case

#### **LangGraph**
✅ **Pros:**
- State machine approach
- Visual workflow
- Good for complex flows
- Checkpoint/resume support

❌ **Cons:**
- Still evolving
- Limited documentation
- Overhead for simple pipelines

**Verdict**: Good fit if we need complex state management

#### **Custom Pipeline**
✅ **Pros:**
- Full control
- Optimized for our needs
- No unnecessary abstractions
- Easier to debug

❌ **Cons:**
- More initial work
- Need to build utilities

**Verdict**: Best for our specific needs

### 🏆 Recommended Stack

```python
# Core Framework: Custom with specific libraries

tech_stack = {
    # Data Layer
    "database": "PostgreSQL 15+",
    "cache": "Redis",
    "orm": "SQLAlchemy 2.0",
    
    # API Layer  
    "http_client": "httpx",  # Better than requests for async
    "rate_limiting": "ratelimit",
    "retry": "tenacity",
    
    # LLM Integration
    "llm": "OpenAI SDK",  # Direct, no LangChain wrapper
    "prompts": "Jinja2",  # Template management
    
    # Pipeline Orchestration
    "workflow": "Prefect 2",  # Modern, Python-native
    "queue": "Celery + Redis",  # For distributed processing
    "scheduling": "APScheduler",
    
    # Monitoring
    "logging": "structlog",  # Structured logging
    "monitoring": "Prometheus + Grafana",
    "tracing": "OpenTelemetry",
    
    # Development
    "testing": "pytest + pytest-asyncio",
    "typing": "pydantic v2",
    "config": "pydantic-settings"
}
```

## 📁 Project Structure

```
services/lead-generation-v2/
├── alembic/                 # Database migrations
├── app/
│   ├── core/               # Core utilities
│   │   ├── config.py       # Pydantic settings
│   │   ├── database.py     # DB connections
│   │   ├── logging.py      # Structured logging
│   │   └── security.py     # API key management
│   ├── models/             # SQLAlchemy models
│   │   ├── influencer.py
│   │   ├── post.py
│   │   ├── engagement.py
│   │   ├── lead.py
│   │   └── research.py
│   ├── schemas/            # Pydantic schemas
│   │   ├── api_responses.py
│   │   ├── linkedin.py
│   │   └── qualification.py
│   ├── services/           # Business logic
│   │   ├── linkedin_api.py
│   │   ├── content_analyzer.py
│   │   ├── lead_qualifier.py
│   │   ├── research_engine.py
│   │   └── message_crafter.py
│   ├── workflows/          # Prefect flows
│   │   ├── influencer_pipeline.py
│   │   ├── qualification_flow.py
│   │   └── daily_processing.py
│   ├── api/               # REST API (FastAPI)
│   │   ├── endpoints/
│   │   └── dependencies.py
│   └── cli/               # CLI commands
│       └── commands.py
├── tests/
├── scripts/               # Utility scripts
├── logs/
├── data/                  # Local data cache
├── docker-compose.yml     # Local dev environment
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🔄 State Management Design

### Pipeline State Machine

```python
from enum import Enum
from typing import Optional
from pydantic import BaseModel

class PipelineState(Enum):
    # Influencer stages
    INFLUENCER_SELECTED = "influencer_selected"
    POSTS_FETCHED = "posts_fetched"
    POSTS_FILTERED = "posts_filtered"
    
    # Engagement stages
    ENGAGEMENTS_EXTRACTED = "engagements_extracted"
    PROFILES_PREQUALIFIED = "profiles_prequalified"
    
    # Qualification stages
    PROFILES_FETCHED = "profiles_fetched"
    LEADS_QUALIFIED = "leads_qualified"
    
    # Final stages
    RESEARCH_COMPLETED = "research_completed"
    MESSAGES_GENERATED = "messages_generated"
    
    # Error states
    FAILED = "failed"
    PAUSED = "paused"

class PipelineRun(BaseModel):
    id: str
    influencer_url: str
    current_state: PipelineState
    processed_posts: int = 0
    extracted_profiles: int = 0
    qualified_leads: int = 0
    error: Optional[str] = None
    metadata: dict = {}
```

## 🚀 Deployment Architecture

### Development Environment
```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: leadgen
      POSTGRES_USER: leadgen
      POSTGRES_PASSWORD: leadgen
    volumes:
      - postgres_data:/var/lib/postgresql/data
    
  redis:
    image: redis:7-alpine
    
  app:
    build: .
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URL: postgresql://leadgen:leadgen@postgres/leadgen
      REDIS_URL: redis://redis:6379
    volumes:
      - ./app:/app
      - ./logs:/logs
```

### Production Considerations

1. **Database**: 
   - AWS RDS PostgreSQL (Multi-AZ)
   - Read replicas for analytics
   - Automated backups

2. **Caching**:
   - AWS ElastiCache Redis
   - Separate cache for API responses vs job queue

3. **Compute**:
   - ECS Fargate for pipeline workers
   - Lambda for lightweight tasks
   - EC2 for heavy processing

4. **Monitoring**:
   - CloudWatch for infrastructure
   - Datadog/New Relic for APM
   - Sentry for error tracking

## 🎯 Decision Summary

### Database: **PostgreSQL + Redis**
- PostgreSQL for persistent data with JSONB for flexibility
- Redis for caching and job queues
- S3 for long-term archive

### Framework: **Custom + Prefect**
- Custom pipeline code for full control
- Prefect for workflow orchestration
- Direct OpenAI SDK (no LangChain)

### Architecture: **Modular Services**
- Separate services for each major component
- Clear interfaces between services
- Easy to test and scale independently

### State Management: **Database-backed**
- Pipeline state in PostgreSQL
- Checkpointing at each stage
- Full resume capability

## 🔐 Security Considerations

1. **API Keys**: 
   - Stored in AWS Secrets Manager
   - Rotated regularly
   - Never in code or logs

2. **Data Privacy**:
   - PII handling protocols
   - Data retention policies
   - GDPR compliance

3. **Access Control**:
   - Role-based access
   - API authentication
   - Audit logging

## 📊 Monitoring & Observability

```python
# Every service emits structured logs
logger.info("profile_fetched", 
    profile_id=profile.id,
    source="linkedin_api",
    duration_ms=response_time,
    cache_hit=False
)

# Metrics for everything
metrics.increment("api.calls", tags=["endpoint:person_deep"])
metrics.histogram("pipeline.stage.duration", duration, tags=["stage:qualification"])

# Distributed tracing
with tracer.start_span("fetch_influencer_posts") as span:
    span.set_attribute("influencer.url", url)
    span.set_attribute("posts.count", len(posts))
```

## 🤔 Questions for Team Discussion

1. **Scale expectations**: How many leads/day are we targeting?
2. **Budget constraints**: What's acceptable cost per lead?
3. **SLA requirements**: What's the expected processing time?
4. **Integration needs**: What systems need to consume our data?
5. **Compliance**: Any industry-specific requirements?

This architecture provides:
- **Flexibility** to evolve
- **Reliability** through proper state management
- **Observability** for debugging
- **Scalability** when needed
- **Simplicity** where possible

Let's discuss and refine based on specific requirements!