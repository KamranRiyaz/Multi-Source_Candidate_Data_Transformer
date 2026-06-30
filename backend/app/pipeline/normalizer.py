import re

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
    """Normalize date to YYYY-MM."""
    if not date_str:
        return None
    val = date_str.strip().lower()
    if val in ("present", "current"):
        return "Present"
    
    # YYYY-MM or YYYY/MM
    match_yyyymm = re.match(r'^(\d{4})[-/](\d{1,2})', val)
    if match_yyyymm:
        return f"{match_yyyymm.group(1)}-{int(match_yyyymm.group(2)):02d}"
    
    # MM/YYYY
    match_mmyyyy = re.match(r'^(\d{1,2})[-/](\d{4})', val)
    if match_mmyyyy:
        return f"{match_mmyyyy.group(2)}-{int(match_mmyyyy.group(1)):02d}"
    
    # Year only
    if re.match(r'^\d{4}$', val):
        return f"{val}-01"
        
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
