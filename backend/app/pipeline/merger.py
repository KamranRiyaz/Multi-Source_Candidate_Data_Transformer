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

    # 4. Skills (dedup and normalize canonical)
    seen_skills = {}
    for src in sorted_sources:
        for skill in src.get("skills", []):
            norm_skill = normalize_skill_canonical(skill)
            if norm_skill:
                if norm_skill not in seen_skills:
                    seen_skills[norm_skill] = {
                        "name": skill, # preserve original case for the primary name
                        "confidence": src.get("confidence", 0.0),
                        "sources": [src["source_name"]]
                    }
                    canonical["skills"].append(seen_skills[norm_skill])
                    canonical["provenance"].append({
                        "field": f"skills[{norm_skill}]",
                        "source": src["source_name"],
                        "method": "canonicalize"
                    })
                else:
                    if src["source_name"] not in seen_skills[norm_skill]["sources"]:
                        seen_skills[norm_skill]["sources"].append(src["source_name"])
                
    # 5. Experience
    seen_experience = set()
    for src in sorted_sources:
        for exp in src.get("experience", []):
            company = exp.get("company", "")
            title = exp.get("title", "")
            key = f"{company}::{title}".lower()
            if key and key not in seen_experience:
                seen_experience.add(key)
                canonical["experience"].append(exp)
                canonical["provenance"].append({
                    "field": f"experience[{company}]",
                    "source": src["source_name"],
                    "method": "merge"
                })

    # 6. Education
    seen_education = set()
    for src in sorted_sources:
        for edu in src.get("education", []):
            institution = edu.get("institution", "")
            degree = edu.get("degree", "")
            key = f"{institution}::{degree}".lower()
            if key and key not in seen_education:
                seen_education.add(key)
                canonical["education"].append(edu)
                canonical["provenance"].append({
                    "field": f"education[{institution}]",
                    "source": src["source_name"],
                    "method": "merge"
                })
                
    # Identify Candidate ID based on email or name
    id_base = canonical["emails"][0] if canonical["emails"] else canonical["full_name"]
    canonical["candidate_id"] = "cand_" + hashlib.md5((id_base or "unknown").encode()).hexdigest()[:12]
    
    # Simple overall confidence avg
    if sorted_sources:
        canonical["overall_confidence"] = sum(s.get("confidence", 0.0) for s in sorted_sources) / len(sorted_sources)
        
    return canonical
