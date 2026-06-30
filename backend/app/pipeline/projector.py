from typing import Dict, Any, List
from ..models import ProjectionConfig, CanonicalProfile
import pydantic
from .normalizer import normalize_phone, normalize_skill_canonical

def resolve_path(data: Dict, path: str) -> Any:
    """Resolve a dot-notation or array path (e.g. emails[0], location.city)."""
    parts = path.replace(']', '').replace('[', '.').split('.')
    current = data
    for part in parts:
        if not part:
            continue
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
    
    for field_conf in config.fields:
        source_path = field_conf.from_path if field_conf.from_path else field_conf.path
        val = resolve_path(canonical_dict, source_path)
        
        if val is None:
            if getattr(field_conf, 'default_value', None) is not None:
                val = field_conf.default_value
            elif config.on_missing == "omit":
                continue
            elif config.on_missing == "error":
                if field_conf.required:
                    raise ValueError(f"Required field missing: {field_conf.path}")
                val = None
            else:
                val = None
                
        # Normalization config support
        if val is not None:
            if field_conf.normalize == "uppercase" and isinstance(val, str):
                val = val.upper()
            elif field_conf.normalize == "lowercase" and isinstance(val, str):
                val = val.lower()
            elif field_conf.normalize in ("E164", "E.164") and isinstance(val, str):
                val = normalize_phone(val)
            elif field_conf.normalize == "canonical" and isinstance(val, str):
                val = normalize_skill_canonical(val)
            # Handle lists of strings for canonical/E164 mapping
            elif field_conf.normalize in ("E164", "E.164") and isinstance(val, list):
                val = [normalize_phone(v) for v in val if isinstance(v, str)]
            elif field_conf.normalize == "canonical" and isinstance(val, list):
                val = [normalize_skill_canonical(v) for v in val if isinstance(v, str)]
            elif field_conf.normalize == "uppercase" and isinstance(val, list):
                val = [v.upper() for v in val if isinstance(v, str)]
            elif field_conf.normalize == "lowercase" and isinstance(val, list):
                val = [v.lower() for v in val if isinstance(v, str)]
            
        # Set to projected dict (assuming flat for simplicity, though nested could be built)
        projected[field_conf.path] = val
        
    if config.include_confidence:
        projected["overall_confidence"] = canonical_dict.get("overall_confidence")
        
    if getattr(config, 'include_provenance', False):
        projected["provenance"] = canonical_dict.get("provenance")
        
    return projected
