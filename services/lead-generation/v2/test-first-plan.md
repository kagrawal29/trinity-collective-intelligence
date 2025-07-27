# TEST-FIRST LEAN DEVELOPMENT PLAN

## 🎯 Target Influencer
**Suprava Sabat**: https://www.linkedin.com/in/suprava-sabat-saasleadgen/
- B2B SaaS Lead Generation expert
- Perfect for our use case!

## 📋 PHASE 1: API Discovery (Tyler Leads)

### Step 1.1: Test getPersonDeepProfile
```bash
# Tyler's first test
curl -X POST https://linkedin-data-scraper.p.rapidapi.com/person_deep \
  -H "x-rapidapi-key: [API_KEY]" \
  -H "Content-Type: application/json" \
  -d '{"link": "https://www.linkedin.com/in/suprava-sabat-saasleadgen/"}'
```

**Document:**
- Full response structure
- Available fields
- Any missing data
- Response time
- Rate limit headers

### Step 1.2: Test getPersonPosts
```bash
# Tyler's second test
curl -X GET "https://linkedin-data-scraper.p.rapidapi.com/profile_updates?profile_url=https://www.linkedin.com/in/suprava-sabat-saasleadgen/&page=1" \
  -H "x-rapidapi-key: [API_KEY]"
```

**Document:**
- Post structure
- Pagination info
- How many posts returned
- URNs for reactions/comments

### Step 1.3: Pick ONE High-Engagement Post
- Find a post about lead generation/outbound sales
- High engagement (100+ reactions)
- Recent (last 30 days)

## 📋 PHASE 2: Engagement Data (Tyler Continues)

### Step 2.1: Test getPostData
```bash
# Get detailed post data including URNs
curl -X POST https://linkedin-data-scraper.p.rapidapi.com/post \
  -H "x-rapidapi-key: [API_KEY]" \
  -H "Content-Type: application/json" \
  -d '{"link": "[POST_URL_FROM_STEP_1.3]"}'
```

### Step 2.2: Test getPostReactions (First Page)
```bash
# Get people who reacted
curl -X POST https://linkedin-data-scraper.p.rapidapi.com/post_reactions \
  -H "x-rapidapi-key: [API_KEY]" \
  -H "Content-Type: application/json" \
  -d '{"reactionsUrn": "[URN_FROM_STEP_2.1]", "page": 1}'
```

**Critical Data to Capture:**
- Profile URLs of reactors
- Their titles/subtitles
- Reaction types
- How many per page

## 📋 PHASE 3: Initial Schema Design (Dev Plans)

### Based on Tyler's Real Data, Dev Creates:

```python
# Minimal test schema - ONLY what we need now
def test_data_structures():
    """
    influencer_response = {
        # Tyler fills this with ACTUAL response
    }
    
    post_response = {
        # Tyler fills this with ACTUAL response
    }
    
    reactions_response = {
        # Tyler fills this with ACTUAL response
    }
    """
    pass
```

### Dev's Minimal Schema (For Review):
```sql
-- ONLY these tables to start
CREATE TABLE test_influencers (
    id SERIAL PRIMARY KEY,
    linkedin_url VARCHAR(255),
    raw_data JSONB,  -- Store everything for now
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE test_posts (
    id SERIAL PRIMARY KEY,
    influencer_id INTEGER,
    post_url VARCHAR(500),
    reactions_urn VARCHAR(255),
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE test_engagements (
    id SERIAL PRIMARY KEY,
    post_id INTEGER,
    profile_url VARCHAR(255),
    title TEXT,
    subtitle TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🔄 ITERATIVE WORKFLOW

### Round 1: Get Influencer Data
1. Tyler tests API → shares response
2. Dev reviews → proposes storage
3. Guide approves → implement minimal storage
4. Store Suprava's data

### Round 2: Get Posts
1. Tyler tests posts API → shares response
2. Dev reviews → updates schema if needed
3. Guide approves → fetch and store posts
4. Pick best post for testing

### Round 3: Get Engagements
1. Tyler tests reactions API → shares response
2. Dev reviews → updates schema if needed
3. Guide approves → fetch first 50 reactions
4. Analyze the data quality

### Round 4: Pre-Qualification Test
1. Use ONLY title/subtitle from reactions
2. Test LLM pre-qualification
3. Document what works/doesn't
4. Refine criteria

## ✅ APPROVAL GATES

Before ANY implementation:

### Tyler's Checklist:
- [ ] API tested with real URL
- [ ] Response documented
- [ ] Edge cases found
- [ ] Rate limits understood

### Dev's Checklist:
- [ ] Test plan written
- [ ] Schema matches real data
- [ ] Only essential fields
- [ ] Clear next steps

### Guide's Checklist:
- [ ] Data quality verified
- [ ] Approach is minimal
- [ ] Team aligned
- [ ] User value clear

## 🚫 WHAT WE'RE NOT DOING (YET)

1. NO complete database design
2. NO fancy frameworks
3. NO optimization
4. NO error handling beyond basic
5. NO UI/API endpoints

## 📊 SUCCESS METRICS FOR PHASE 1

1. Successfully fetch Suprava's profile ✓
2. Get her last 20 posts ✓
3. Find 1 high-engagement relevant post ✓
4. Extract 50 people who engaged ✓
5. Pre-qualify 10 leads from titles ✓

**If we achieve this, we've validated the approach!**

## 💬 COMMUNICATION PROTOCOL

```
Tyler: "Tested person_deep API. Response has X structure. Found Y issue."
Dev: "Based on data, propose storing only A, B, C fields. Test plan: [...]"
Guide: "Approved with modification: [...]" 
Tyler: "Implementing test for next step..."
```

## 🎯 DELIVERABLE FOR TODAY

A Jupyter notebook or script that:
1. Fetches Suprava's profile
2. Gets her posts
3. Picks one relevant post
4. Gets 50 engagers
5. Shows their titles/subtitles
6. Attempts basic pre-qualification

**That's it! Lean, testable, valuable.**

---

Team: Share your plans in the comms before implementing ANYTHING. We build only what we test first!