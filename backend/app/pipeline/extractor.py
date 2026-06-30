import csv
import io
import json
from typing import List, Dict, Any
from .normalizer import normalize_email, normalize_phone

def extract_from_csv(csv_text: str) -> List[Dict[str, Any]]:
    """Extract from recruiter CSV."""
    if not csv_text:
        return []
        
    reader = csv.DictReader(io.StringIO(csv_text.strip()))
    results = []
    
    for row in reader:
        # Standardize keys
        normalized_row = {k.strip().lower(): v.strip() for k, v in row.items() if k and v}
        
        extracted = {
            "source_type": "csv",
            "source_name": "Recruiter CSV",
            "confidence": 0.85,
            "full_name": normalized_row.get("name"),
            "emails": [normalized_row.get("email")] if normalized_row.get("email") else [],
            "phones": [normalized_row.get("phone")] if normalized_row.get("phone") else [],
            "experience": []
        }
        
        company = normalized_row.get("current_company")
        title = normalized_row.get("title")
        if company or title:
            extracted["experience"].append({
                "company": company or "Unknown",
                "title": title or "Candidate",
                "end": "Present"
            })
            
        if extracted["full_name"] or extracted["emails"]:
            results.append(extracted)
            
    return results

def extract_from_ats_json(json_text: str) -> List[Dict[str, Any]]:
    """Extract from semi-structured ATS JSON blob."""
    if not json_text:
        return []
        
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError:
        return []
        
    candidates = data if isinstance(data, list) else [data]
    results = []
    
    for item in candidates:
        raw_skills = item.get("skills", [])
        if isinstance(raw_skills, str):
            parsed_skills = [s.strip() for s in raw_skills.split(",")]
        elif isinstance(raw_skills, list):
            parsed_skills = [s.get("name", "") if isinstance(s, dict) else str(s) for s in raw_skills]
        else:
            parsed_skills = []

        extracted = {
            "source_type": "ats_json",
            "source_name": "ATS System",
            "confidence": 0.95,
            "full_name": item.get("name") or item.get("full_name"),
            "emails": [],
            "phones": [],
            "skills": parsed_skills,
            "location": {},
            "experience": [],
            "education": []
        }
        
        if "email" in item:
            extracted["emails"].append(item["email"])
        if "phone" in item:
            extracted["phones"].append(item["phone"])
            
        if "experience" in item:
            extracted["experience"] = item["experience"]
            
        if "education" in item:
            extracted["education"] = item["education"]
            
        loc = item.get("location")
        if isinstance(loc, str):
            parts = [p.strip() for p in loc.split(",")]
            if len(parts) > 0:
                extracted["location"]["city"] = parts[0]
            if len(parts) > 1:
                extracted["location"]["country"] = parts[-1]
                
        results.append(extracted)
        
    return results

def extract_from_github(github_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract from GitHub Profile JSON."""
    if not github_data:
        return {}
        
    raw_languages = github_data.get("languages", [])
    if isinstance(raw_languages, str):
        gh_skills = [s.strip() for s in raw_languages.split(",")]
    elif isinstance(raw_languages, dict):
        gh_skills = list(raw_languages.keys())
    elif isinstance(raw_languages, list):
        gh_skills = [s.get("name", "") if isinstance(s, dict) else str(s) for s in raw_languages]
    else:
        gh_skills = []
        
    return {
        "source_type": "github_profile",
        "source_name": f"GitHub ({github_data.get('login', 'User')})",
        "confidence": 0.75,
        "full_name": github_data.get("name") or github_data.get("login"),
        "emails": [github_data["email"]] if github_data.get("email") else [],
        "phones": [],
        "skills": gh_skills,
        "experience": [],
        "education": [],
        "location": {"city": github_data.get("location", "").split(",")[0]} if github_data.get("location") else {},
        "links": {"github": github_data.get("html_url")} if github_data.get("html_url") else {},
        "headline": github_data.get("bio")
    }

import re

def extract_from_notes(notes_text: str) -> Dict[str, Any]:
    """Extract from unstructured recruiter notes using regex/heuristics."""
    if not notes_text:
        return {}
        
    extracted = {
        "source_type": "recruiter_notes",
        "source_name": "Recruiter Notes",
        "confidence": 0.50, # Lower confidence for unstructured text
        "full_name": "",
        "emails": [],
        "phones": [],
        "skills": [],
        "experience": []
    }
    
    # 1. Emails
    email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    extracted["emails"] = list(set(re.findall(email_regex, notes_text)))
    
    # 2. Phones
    phone_regex = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    extracted["phones"] = list(set(re.findall(phone_regex, notes_text)))
    
    # 3. Name (Heuristic: "Name: John Doe" or "Candidate: John Doe")
    name_match = re.search(r'(?:candidate|name):\s*([^\n\r]+)', notes_text, re.IGNORECASE)
    if name_match:
        extracted["full_name"] = name_match.group(1).strip()
        
    # 4. Skills (Keywords)
    common_skills = [
        "react", "angular", "vue", "javascript", "typescript", "python", "node", "express",
        "fastapi", "django", "flask", "postgresql", "mysql", "mongodb", "aws", "gcp",
        "docker", "kubernetes", "java", "c\\+\\+", "rust", "go", "ci/cd", "machine learning"
    ]
    for skill in common_skills:
        if re.search(rf'\b{skill}\b', notes_text, re.IGNORECASE):
            extracted["skills"].append(skill.replace('\\', ''))
            
    # 5. Experience (Heuristic: "works at Acme" or "company: Acme")
    company_match = re.search(r'(?:works at|currently at|company:)\s*([A-Za-z0-9\s]+?)(?:\.|\n|as\b)', notes_text, re.IGNORECASE)
    title_match = re.search(r'(?:as a|title:)\s*([A-Za-z0-9\s\-]+?)(?:\.|\n|at\b|who\b)', notes_text, re.IGNORECASE)
    
    if company_match or title_match:
        extracted["experience"].append({
            "company": company_match.group(1).strip() if company_match else "Unknown Company",
            "title": title_match.group(1).strip() if title_match else "Software Engineer",
            "end": "Present"
        })
        
    return extracted

def extract_all_sources(sources_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    extracted_list = []
    
    # Handle single files (Legacy CLI)
    if "csv" in sources_dict:
        extracted_list.extend(extract_from_csv(sources_dict["csv"]))
    if "ats_json" in sources_dict:
        extracted_list.extend(extract_from_ats_json(sources_dict["ats_json"]))
    if "github" in sources_dict:
        if isinstance(sources_dict["github"], dict):
            extracted_list.append(extract_from_github(sources_dict["github"]))
        elif isinstance(sources_dict["github"], str):
            try:
                extracted_list.append(extract_from_github(json.loads(sources_dict["github"])))
            except:
                pass
    if "notes" in sources_dict:
        extracted_list.append(extract_from_notes(sources_dict["notes"]))

    # Handle multiple files (Directory mode)
    if "csv_list" in sources_dict:
        for csv_data in sources_dict["csv_list"]:
            extracted_list.extend(extract_from_csv(csv_data))
            
    if "ats_json_list" in sources_dict:
        for ats_data in sources_dict["ats_json_list"]:
            extracted_list.extend(extract_from_ats_json(ats_data))
            
    if "github_list" in sources_dict:
        for gh_data in sources_dict["github_list"]:
            if isinstance(gh_data, str):
                try: gh_data = json.loads(gh_data)
                except: continue
            extracted_list.append(extract_from_github(gh_data))
            
    if "notes_list" in sources_dict:
        for notes_data in sources_dict["notes_list"]:
            extracted_list.append(extract_from_notes(notes_data))
                
    return [e for e in extracted_list if e]
