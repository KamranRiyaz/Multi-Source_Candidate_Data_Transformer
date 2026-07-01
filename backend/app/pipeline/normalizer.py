import re
from datetime import datetime

def normalize_phone(phone: str) -> str:
    """Normalize phone to E.164-like format."""
    if not phone:
        return ""
    cleaned = re.sub(r'[\s\(\)\-\.]', '', phone)
    if cleaned.startswith('+'):
        return cleaned
    if len(cleaned) == 10 and cleaned.isdigit():
        return "+1" + cleaned
    if cleaned.isdigit():
        return "+" + cleaned
    return phone

def normalize_email(email: str) -> str:
    """Lowercase and strip emails."""
    if not email:
        return ""
    return email.strip().lower()

def normalize_date(date_str: str) -> str:
    if not date_str or not isinstance(date_str, str):
        return date_str
        
    date_str = date_str.strip()
    
    # Common date formats found in resumes and ATS systems
    formats = (
        "%Y-%m-%d", "%Y-%m", "%m/%Y", "%m/%d/%Y", 
        "%b %Y", "%B %Y", "%b %d, %Y", "%B %d, %Y"
    )
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m")
        except ValueError:
            continue
            
    # Fallback to the original string if it doesn't match any known format
    return date_str

def normalize_country(country: str) -> str:
    """Normalize to ISO-3166 alpha-2."""
    if not country:
        return None
    mapping = {
        "united states": "US", "usa": "US", "us": "US",
        "united kingdom": "GB", "uk": "GB", "great britain": "GB",
        "india": "IN", "ind": "IN",
        "canada": "CA", "germany": "DE", "france": "FR",
        "australia": "AU"
    }
    return mapping.get(country.strip().lower(), country.upper()[:2])

def normalize_skill_canonical(skill: str) -> str:
    """Canonicalize skill names."""
    if not skill:
        return ""
    
    skill_str = str(skill).strip()
    if not skill_str:
        return ""
        
    mapping = {
        "react": "React", "react.js": "React", "reactjs": "React",
        "python": "Python", "python 3": "Python",
        "node": "Node.js", "nodejs": "Node.js", "node.js": "Node.js",
        "aws": "AWS", "gcp": "GCP"
    }
    return mapping.get(skill_str.lower(), skill_str)
