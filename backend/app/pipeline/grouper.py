from typing import List, Dict, Any
from .normalizer import normalize_email

def group_profiles(extracted_sources: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """
    Groups extracted profiles by matching emails or names to identify the same candidate.
    """
    groups = []
    
    for src in extracted_sources:
        src_emails = set([normalize_email(e) for e in src.get("emails", []) if normalize_email(e)])
        src_name = src.get("full_name", "").lower().strip()
        
        matched_group_idx = -1
        for i, group in enumerate(groups):
            # Check for email match
            group_emails = set()
            group_names = set()
            for g_src in group:
                for e in g_src.get("emails", []):
                    norm_e = normalize_email(e)
                    if norm_e:
                        group_emails.add(norm_e)
                if g_src.get("full_name"):
                    group_names.add(g_src.get("full_name", "").lower().strip())
                    
            # If any email matches, it's the same person
            if src_emails and group_emails and (src_emails & group_emails):
                matched_group_idx = i
                break
            
            # Fallback: if exact name match
            if src_name and src_name in group_names:
                matched_group_idx = i
                break
                
        if matched_group_idx >= 0:
            groups[matched_group_idx].append(src)
        else:
            groups.append([src])
            
    return groups
