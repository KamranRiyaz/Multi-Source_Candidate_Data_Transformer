from typing import Dict, Any, List
from ..models import ProjectionConfig
from .normalizer import normalize_phone, normalize_skill_canonical, normalize_date, normalize_email, normalize_country

def resolve_path(data: Dict, path: str) -> Any:
    """Resolve a dot-notation or array path (e.g. emails[0], location.city, skills[].name or skills[*].name)."""
    parts = path.replace(']', '').replace('[', '.').split('.')
    current = data
    for i, part in enumerate(parts):
        # Support both [] and [*] syntax for array mapping
        if not part or part == '*':
            if isinstance(current, list):
                remaining_path = '.'.join(parts[i+1:])
                if not remaining_path:
                    return current
                
                # Flatten the list and strip out Nones
                result = [resolve_path(item, remaining_path) for item in current]
                return [x for x in result if x is not None]
            return current
            
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError):
                return None
        else:
            return None
    return current

def project_data(canonical_dict: Dict[str, Any], config: ProjectionConfig) -> Dict[str, Any]:
    projected = {}
    successful_source_bases = set()
    
    for field_conf in config.fields:
        source_path = field_conf.from_path if field_conf.from_path else field_conf.path
        val = resolve_path(canonical_dict, source_path)
        
        # Check for empty string, empty list, or None to trigger missing policies
        is_missing = val is None or val == [] or val == ""
        
        if is_missing:
            if getattr(field_conf, 'default_value', None) is not None:
                val = field_conf.default_value
            elif config.on_missing == "omit" and not getattr(field_conf, 'required', False):
                continue
            # Raise error if globally requested OR locally required
            elif config.on_missing == "error" or getattr(field_conf, 'required', False):
                missing_path = source_path if source_path else field_conf.path
                raise ValueError(
                    f"Missing value for required projection field '{field_conf.path}' "
                    f"(source path: '{missing_path}')"
                )
            else:
                val = None
                
        if val is not None:
            # Type Enforcement
            expected_type = getattr(field_conf, 'type', "")
            if "[]" in expected_type and not isinstance(val, list):
                val = [val]
            elif expected_type == "string" and isinstance(val, list):
                val = str(val[0]) if val else None

            # Normalization
            norm = getattr(field_conf, 'normalize', None)
            if norm in ("E164", "E.164"):
                if isinstance(val, list):
                    val = [normalize_phone(v) for v in val if isinstance(v, str)]
                elif isinstance(val, str):
                    val = normalize_phone(val)
            elif norm == "canonical":
                if isinstance(val, list):
                    val = [normalize_skill_canonical(v) for v in val if isinstance(v, str)]
                elif isinstance(val, str):
                    val = normalize_skill_canonical(val)
            elif norm == "YYYY-MM":
                if isinstance(val, list):
                    val = [normalize_date(v) for v in val if isinstance(v, str)]
                elif isinstance(val, str):
                    val = normalize_date(val)
            elif norm == "uppercase":
                val = [v.upper() for v in val if isinstance(v, str)] if isinstance(val, list) else val.upper()
            elif norm == "lowercase":
                val = [v.lower() for v in val if isinstance(v, str)] if isinstance(val, list) else val.lower()
            elif norm == "email":
                if isinstance(val, list):
                    val = [normalize_email(v) for v in val if isinstance(v, str)]
                elif isinstance(val, str):
                    val = normalize_email(val)
            elif norm == "ISO-3166-2":
                if isinstance(val, list):
                    val = [normalize_country(v) for v in val if isinstance(v, str)]
                elif isinstance(val, str):
                    val = normalize_country(val)
            
            projected[field_conf.path] = val
            
            # Track the base path for provenance filtering (e.g., "skills" from "skills[*].name")
            base_path = source_path.split('[')[0].split('.')[0]
            successful_source_bases.add(base_path)
        else:
            # If the value evaluates to None and wasn't intentionally omitted, create the null key
            projected[field_conf.path] = None
        
    if getattr(config, 'include_confidence', False):
        projected["overall_confidence"] = canonical_dict.get("overall_confidence", 0.0)
        
    if getattr(config, 'include_provenance', False):
        all_provenance = canonical_dict.get("provenance", [])
        # Filter provenance metadata to only match requested fields
        filtered_provenance = [
            p for p in all_provenance 
            if any(p.get("field", "").startswith(base) for base in successful_source_bases)
        ]
        projected["provenance"] = filtered_provenance
        
    return projected