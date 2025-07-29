# 🗺️ Trinity V2 Data Mapping Architecture - CRITICAL

## 🎯 THE MAPPING PROBLEM

We have a **broken data lineage** that prevents ROI analysis and scaling decisions:

### ❌ Current State (INCOMPLETE MAPPING)
```
post_url → reactions/comments → leads → qualification scores
```

### ✅ Required State (COMPLETE MAPPING)
```
Influencer → Post → Content → Engagement → Lead → Qualification → ROI
```

## 📊 ENTITY RELATIONSHIP MAP

### 1. **INFLUENCER** (Currently Missing)
- `influencer_id` (unique identifier)
- `influencer_name`
- `influencer_profile_url`
- `follower_count`
- `typical_engagement_rate`
- `niche/category`
- `partnership_status`

### 2. **POST** (Partially Captured)
- `post_id` (from URL)
- `post_url` ✅ (we have this)
- `influencer_id` ❌ (missing link)
- `post_content` ❌ (missing)
- `post_type` ❌ (text/image/video)
- `posted_date` ❌
- `hashtags` ❌
- `campaign_id` ❌

### 3. **ENGAGEMENT** (Captured)
- `engagement_id`
- `post_id`
- `engagement_type` ✅ (reaction/comment)
- `engagement_detail` ✅ (reaction type/comment text)
- `timestamp` ✅

### 4. **LEAD** (Captured)
- `lead_id`
- `linkedin_url` ✅
- `name` ✅
- `title` ✅
- `company` ✅
- `engagement_id` (implicit link)

### 5. **QUALIFICATION** (Captured)
- `qualification_id`
- `lead_id`
- `llm_score` ✅
- `tier_classification` ✅
- `reasoning` ✅
- `is_qualified` ✅
- `prompt_version` ✅

### 6. **CAMPAIGN** (Missing)
- `campaign_id`
- `campaign_name`
- `start_date`
- `influencer_ids[]`
- `target_metrics`
- `budget`

## 🔄 PROPER RELATIONAL MAPPING

```sql
-- Enhanced SQLite Schema for Complete Mapping

-- New Tables Needed:
CREATE TABLE influencers (
    influencer_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    profile_url TEXT UNIQUE,
    follower_count INTEGER,
    engagement_rate REAL,
    niche TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE posts (
    post_id TEXT PRIMARY KEY,
    post_url TEXT UNIQUE NOT NULL,
    influencer_id TEXT NOT NULL,
    content TEXT,
    post_type TEXT,
    posted_date DATETIME,
    campaign_id TEXT,
    total_reactions INTEGER,
    total_comments INTEGER,
    fetch_timestamp DATETIME,
    FOREIGN KEY (influencer_id) REFERENCES influencers(influencer_id)
);

CREATE TABLE campaigns (
    campaign_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    start_date DATETIME,
    end_date DATETIME,
    target_leads INTEGER,
    budget REAL,
    status TEXT
);

-- Update existing lead_qualification_results table:
ALTER TABLE lead_qualification_results ADD COLUMN post_id TEXT;
ALTER TABLE lead_qualification_results ADD COLUMN campaign_id TEXT;
```

## 🎯 BUSINESS INTELLIGENCE QUERIES ENABLED

With proper mapping, we can answer:

### 1. **Influencer Performance**
```sql
SELECT 
    i.name,
    COUNT(DISTINCT l.lead_id) as total_leads,
    SUM(CASE WHEN l.is_qualified THEN 1 ELSE 0 END) as qualified_leads,
    AVG(l.llm_score) as avg_lead_quality
FROM influencers i
JOIN posts p ON i.influencer_id = p.influencer_id
JOIN lead_qualification_results l ON p.post_id = l.post_id
GROUP BY i.influencer_id
ORDER BY qualified_leads DESC;
```

### 2. **Content Performance**
```sql
SELECT 
    p.content,
    p.post_type,
    COUNT(DISTINCT l.lead_id) as leads_generated,
    AVG(l.llm_score) as avg_quality
FROM posts p
JOIN lead_qualification_results l ON p.post_id = l.post_id
WHERE l.is_qualified = true
GROUP BY p.post_id
ORDER BY leads_generated DESC;
```

### 3. **Campaign ROI**
```sql
SELECT 
    c.name,
    c.budget,
    COUNT(DISTINCT l.lead_id) as total_leads,
    SUM(CASE WHEN l.is_qualified THEN 1 ELSE 0 END) as qualified_leads,
    c.budget / NULLIF(SUM(CASE WHEN l.is_qualified THEN 1 ELSE 0 END), 0) as cost_per_qualified_lead
FROM campaigns c
JOIN posts p ON c.campaign_id = p.campaign_id
JOIN lead_qualification_results l ON p.post_id = l.post_id
GROUP BY c.campaign_id;
```

## 🚨 IMPLEMENTATION PRIORITY

### Phase 1: Capture Missing Data (URGENT)
1. Modify data fetching to capture influencer info
2. Extract post content when fetching engagement
3. Create campaign tracking mechanism

### Phase 2: Update Database Schema
1. Add new tables (influencers, posts, campaigns)
2. Update existing tables with foreign keys
3. Migrate existing data with proper relationships

### Phase 3: Update Processing Pipeline
1. Modify `analyze_batch_llm_sqlite.py` to include mapping
2. Update logging system to track full lineage
3. Create reporting queries for business intelligence

## 🎯 SUCCESS METRICS

With proper mapping, we can track:
- **Cost per qualified lead** by influencer
- **Content type performance** (what messaging works)
- **Influencer lifetime value** (total qualified leads generated)
- **Campaign effectiveness** (which tests succeeded)
- **Scaling decisions** (which influencers to invest in)

## ⚡ IMMEDIATE ACTION REQUIRED

The current system is like having a car with no speedometer - we're moving but can't measure performance! We need this mapping to make the lead generation system truly scalable and optimizable.

**USER RAGE about improper mapping: 10/10** 🔥

---

*This mapping architecture is CRITICAL for transforming the lead generation system from a proof-of-concept to a scalable business intelligence platform.*