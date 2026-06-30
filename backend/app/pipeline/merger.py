import hashlib
from typing import List, Dict, Any
from .normalizer import normalize_email, normalize_phone, normalize_country, normalize_skill_canonical

def merge_profiles(extracted_sources: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not extracted_sources:
        return {}
        
    sorted_sources = sorted(extracted_sources, key=lambda x: x.get("confidence", 0.0), reverse=True)
    
    canonical = {
        "candidate_id": "",
        "full_name": "",
        "emails": [],
        "phones": [],
        "location": {},
        "links": {"other": []},
        "headline": None,
        "years_experience": None,
        "skills": [],
        "experience": [],
        "education": [],
        "provenance": [],
        "overall_confidence": 0.0
    }
    
    # 1. Names
    for src in sorted_sources:
        if src.get("full_name") and not canonical["full_name"]:
            canonical["full_name"] = src["full_name"]
            canonical["provenance"].append({
                "field": "full_name",
                "source": src["source_name"],
                "method": "highest_confidence"
            })
            break
            
    # 2. Emails (dedup and normalize)
    seen_emails = set()
    for src in sorted_sources:
        for email in src.get("emails", []):
            norm_email = normalize_email(email)
            if norm_email and norm_email not in seen_emails:
                seen_emails.add(norm_email)
                canonical["emails"].append(norm_email)
                canonical["provenance"].append({
                    "field": f"emails[{norm_email}]",
                    "source": src["source_name"],
                    "method": "normalize"
                })
                
    # 3. Phones (dedup and normalize)
    seen_phones = set()
    for src in sorted_sources:
        for phone in src.get("phones", []):
            norm_phone = normalize_phone(phone)
            if norm_phone and norm_phone not in seen_phones:
                seen_phones.add(norm_phone)
                canonical["phones"].append(norm_phone)
                canonical["provenance"].append({
                    "field": f"phones[{norm_phone}]",
                    "source": src["source_name"],
                    "method": "normalize"
                })
                
    # Identify Candidate ID based on email or name
    id_base = canonical["emails"][0] if canonical["emails"] else canonical["full_name"]
    canonical["candidate_id"] = "cand_" + hashlib.md5((id_base or "unknown").encode()).hexdigest()[:12]
    
    # Simple overall confidence avg
    if sorted_sources:
        canonical["overall_confidence"] = sum(s.get("confidence", 0.0) for s in sorted_sources) / len(sorted_sources)
        
    return canonical
