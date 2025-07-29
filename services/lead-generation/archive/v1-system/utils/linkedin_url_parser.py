"""LinkedIn URL parser utility"""

import re
from typing import Optional


def parse_linkedin_url(url: str) -> Optional[str]:
    """
    Parse and normalize LinkedIn URLs from various formats
    
    Handles:
    - Standard URLs: https://www.linkedin.com/in/username
    - Encoded URLs: https://www.linkedin.com/in/acoaaab5dbcbu-ptga0qnyrl...
    - URNs: urn:li:fsd_profile:ACoAAAB5DBcBU-Ptga0Qnyrl...
    
    Returns:
    - None if no valid username can be extracted
    - Normalized URL if successful
    """
    if not url:
        return None
    
    # For encoded profile URLs, we need to extract the actual username
    # These are temporary and won't work with the API
    if '/in/aco' in url.lower():
        # This is an encoded profile identifier, not a username
        # We can't use these directly with the API
        return None
    
    # Standard LinkedIn URL pattern
    standard_pattern = r'linkedin\.com/in/([a-zA-Z0-9\-_]+)'
    match = re.search(standard_pattern, url)
    
    if match:
        username = match.group(1)
        # Skip if it looks like an encoded identifier
        if username.lower().startswith('aco'):
            return None
        return f"https://www.linkedin.com/in/{username}"
    
    return None


def extract_username_from_row(row: dict) -> Optional[str]:
    """
    Try to extract a valid LinkedIn username from various fields in a CSV row
    
    Looks for actual usernames (not encoded IDs) in:
    - influencerUrl (best source)
    - Any field containing linkedin.com/in/ URLs
    - dedupKey field which might contain usernames
    
    Returns:
    - LinkedIn username if found
    - None if no valid username can be extracted
    """
    # First, check influencerUrl as it often contains the actual profile
    influencer_url = row.get('influencerUrl', '')
    if influencer_url:
        parsed = parse_linkedin_url(influencer_url)
        if parsed:
            return parsed
    
    # Check dedupKey which might contain username info
    dedup_key = row.get('dedupKey', '')
    if dedup_key:
        # dedupKey format appears to be "name|||title"
        # We can't derive LinkedIn URL from just the name
        pass
    
    # Check all fields for any valid LinkedIn URLs
    for key, value in row.items():
        if value and isinstance(value, str) and 'linkedin.com/in/' in value:
            parsed = parse_linkedin_url(value)
            if parsed:
                return parsed
    
    return None