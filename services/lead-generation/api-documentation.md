# LinkedIn Data API Documentation

## Overview
This document contains detailed specifications for LinkedIn data scraping APIs used in our lead generation engine.

---

## 1. Person Profile API

### Endpoint
```
POST https://linkedin-data-scraper.p.rapidapi.com/person
```

### Headers
```json
{
  "Content-Type": "application/json",
  "x-rapidapi-host": "linkedin-data-scraper.p.rapidapi.com",
  "x-rapidapi-key": "YOUR_API_KEY"
}
```

### Request Body
```json
{
  "link": "https://www.linkedin.com/in/[username]"
}
```

### Input Parameters
- **link** (required): Full LinkedIn profile URL
  - Format: `https://www.linkedin.com/in/[username]`
  - Example: `https://www.linkedin.com/in/ingmar-klein`

### Response Structure
```json
{
  "success": true,
  "status": 200,
  "data": {
    "firstName": "string",
    "lastName": "string", 
    "fullName": "string",
    "publicIdentifier": "string",
    "headline": "string",
    "connections": number,
    "followers": number,
    "addressWithCountry": "string",
    "profilePic": "string (URL)",
    "about": "string",
    "experiences": [
      {
        "companyId": "string",
        "title": "string",
        "subtitle": "string (company name)",
        "caption": "string (duration)",
        "metadata": "string (location)",
        "logo": "string (URL)",
        "description": [
          {
            "type": "textComponent",
            "text": "string"
          }
        ]
      }
    ],
    "educations": [
      {
        "companyId": "string",
        "title": "string (institution)",
        "subtitle": "string (degree)",
        "logo": "string (URL)"
      }
    ],
    "skills": [
      {
        "title": "string",
        "subComponents": [
          {
            "description": [
              {
                "type": "insightComponent",
                "text": "X endorsements"
              }
            ]
          }
        ]
      }
    ],
    "updates": [
      {
        "postText": "string",
        "image": "string (URL)",
        "postLink": "string (URL)",
        "numLikes": number,
        "numComments": number,
        "reactionTypeCounts": [
          {
            "count": number,
            "reactionType": "string"
          }
        ]
      }
    ]
  }
}
```

### Example Request
```bash
curl --request POST \
  --url https://linkedin-data-scraper.p.rapidapi.com/person \
  --header 'Content-Type: application/json' \
  --header 'x-rapidapi-host: linkedin-data-scraper.p.rapidapi.com' \
  --header 'x-rapidapi-key: YOUR_API_KEY' \
  --data '{"link":"https://www.linkedin.com/in/ingmar-klein"}'
```

### Notes
- Requires RapidAPI subscription
- Rate limits may apply
- Response time varies based on profile complexity

---

## API Testing Log

### Test 1: Person Profile - Ingmar Klein
- **Date**: January 27, 2025
- **Status**: ✅ Success
- **Response Time**: ~2 seconds
- **Key Data Points**:
  - Name: Ingmar Klein
  - Headline: CEO @ Huzzle | St. Gallen | Sigma² | EWOR
  - Connections: 17,005
  - Followers: 41,534
  - Location: Berlin Metropolitan Area, Germany
  - Current Role: CEO at Huzzle (4 yrs 5 mos)
  - Recent Updates: 5 posts included
  - Education: University of St.Gallen (BA)
  - Skills: Leadership, Public Speaking, Digital Marketing (with endorsement counts)