# Lead Qualification Criteria

## Overview
Our lead generation engine uses a strict qualification process to identify the most relevant prospects for our service. A lead must meet ALL three criteria to be qualified.

## Qualification Criteria

### ✅ QUALIFIED = Decision Maker AND NOT Competitor AND NOT Influencer

### 1. Must Be a Decision Maker
- **Definition**: Person has authority to purchase lead generation services
- **Indicators**:
  - C-level executives (CEO, CMO, CRO, CSO)
  - VP or Director of Sales/Marketing/Revenue
  - Founders of B2B companies
  - Head of Sales/Business Development
- **LLM Analysis**: Examines title, role, and company position

### 2. Must NOT Be a Competitor
- **Definition**: Their company doesn't offer competing lead generation services
- **Red Flags**:
  - Lead generation platforms
  - Sales automation tools
  - Outbound marketing services
  - AI SDR solutions
- **LLM Analysis**: Analyzes company description and services offered

### 3. Must NOT Be an Influencer (Score < 70)
- **Definition**: Not primarily focused on regular content creation/thought leadership
- **Key Criteria**:
  - Regular posting frequency (2+ times per week)
  - High follower count (10k+)
  - Significant engagement on posts
  - Thought leadership content (not just reactions)
- **Why Exclude**: Influencers typically:
  - Want partnerships/sponsorships, not to buy services
  - Are approached by many vendors
  - Have different engagement patterns
- **Scoring Threshold**: Influencer score must be below 70/100
- **LLM Analysis**: Evaluates posting frequency, followers, engagement quality

## Examples

### ❌ NOT Qualified Examples:

1. **Daniel Shnaider** - Co-founder @Warmy.io & AnyBiz.io
   - ✅ Decision Maker: Yes (Co-founder)
   - ❌ Competitor: Yes (AnyBiz = lead gen)
   - ❌ Influencer: Yes (Score: 65)
   - **Result**: NOT QUALIFIED (competitor)

2. **Marketing Influencer Example** - CMO & LinkedIn Top Voice
   - ✅ Decision Maker: Yes (CMO)
   - ✅ Competitor: No
   - ❌ Influencer: Yes (Score: 85 - posts 3x/week, 50k followers)
   - **Result**: NOT QUALIFIED (influencer)

### ✅ Qualified Example (Ideal):

**Hypothetical: John Smith** - VP Sales at TechCorp (B2B SaaS)
- ✅ Decision Maker: Yes (VP Sales)
- ✅ Competitor: No (sells project management software)
- ✅ Influencer: No (Score: 15, low social presence)
- **Result**: QUALIFIED ✅

## Why These Criteria?

1. **Decision Makers**: Can actually buy our service
2. **Non-Competitors**: No conflict of interest, genuine need
3. **Non-Influencers**: Looking for solutions, not partnerships

## Workflow Output

For each prospect, the system provides:
- **Binary Qualification**: YES/NO
- **Individual Criteria Status**: ✅/❌ for each criterion
- **Disqualification Reasons**: If not qualified
- **Personalization Hooks**: Only for qualified leads
- **Outreach Strategy**: Only for qualified leads