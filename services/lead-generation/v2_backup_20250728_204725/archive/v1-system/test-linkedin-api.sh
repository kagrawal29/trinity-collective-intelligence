#!/bin/bash

# LinkedIn Person Profile API Test
# Note: You'll need to add your RapidAPI key

RAPIDAPI_KEY="YOUR_RAPIDAPI_KEY_HERE"

echo "Testing LinkedIn Person Profile API..."
echo "Target: https://www.linkedin.com/in/ingmar-klein"
echo "----------------------------------------"

curl --request POST \
  --url https://linkedin-data-scraper.p.rapidapi.com/person \
  --header 'Content-Type: application/json' \
  --header 'x-rapidapi-host: linkedin-data-scraper.p.rapidapi.com' \
  --header "x-rapidapi-key: $RAPIDAPI_KEY" \
  --data '{"link":"https://www.linkedin.com/in/ingmar-klein"}' \
  | python3 -m json.tool