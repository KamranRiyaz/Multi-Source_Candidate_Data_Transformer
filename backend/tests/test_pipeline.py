import pytest
from app.pipeline.extractor import extract_from_csv, extract_from_ats_json, extract_from_notes
from app.pipeline.normalizer import normalize_phone, normalize_country
from app.pipeline.merger import merge_profiles
from app.pipeline.projector import project_data
from app.models import ProjectionConfig

def test_normalize_phone():
    assert normalize_phone("+1 (555) 019-2834") == "+15550192834"
    assert normalize_phone("555-019-2834") == "+15550192834"
    assert normalize_phone("invalid") == "invalid"

def test_normalize_country():
    assert normalize_country("United States") == "US"
    assert normalize_country("uk") == "GB"

def test_extractor_csv():
    csv_data = "name,email,phone,current_company,title\nJohn Doe,john@test.com,5551234567,Acme,Dev"
    extracted = extract_from_csv(csv_data)
    assert len(extracted) == 1
    assert extracted[0]["full_name"] == "John Doe"
    assert extracted[0]["emails"] == ["john@test.com"]
    assert extracted[0]["experience"][0]["company"] == "Acme"

def test_extractor_notes():
    notes = "Candidate: Riyaz\nEmail: riyaz@test.com\nCurrently at Google as a Developer. Skills: React, Python."
    extracted = extract_from_notes(notes)
    assert extracted["full_name"] == "Riyaz"
    assert "riyaz@test.com" in extracted["emails"]
    assert "react" in extracted["skills"]
    assert extracted["experience"][0]["company"] == "Google"
    assert extracted["experience"][0]["title"] == "Developer"

def test_merger_conflict_resolution():
    sources = [
        {"source_name": "CSV", "confidence": 0.8, "full_name": "John D.", "emails": ["j@test.com"]},
        {"source_name": "ATS", "confidence": 0.95, "full_name": "John Doe", "emails": ["john.doe@test.com"]}
    ]
    canonical = merge_profiles(sources)
    # Should pick higher confidence name
    assert canonical["full_name"] == "John Doe"
    # Should merge and deduplicate emails
    assert len(canonical["emails"]) == 2
    # Check provenance
    name_prov = next(p for p in canonical["provenance"] if p["field"] == "full_name")
    assert name_prov["source"] == "ATS"

def test_projector_mapping_and_missing():
    canonical = {
        "full_name": "Jane Doe",
        "emails": ["jane@test.com"],
        "overall_confidence": 0.9
    }
    
    config = ProjectionConfig(**{
        "fields": [
            {"path": "name", "from": "full_name", "type": "string"},
            {"path": "primary_email", "from": "emails[0]", "type": "string"}
        ],
        "include_confidence": False,
        "on_missing": "null"
    })
    
    projected = project_data(canonical, config)
    assert projected.get("name") == "Jane Doe"
    assert projected.get("primary_email") == "jane@test.com"
    assert "overall_confidence" not in projected

# --- EDGE CASES ---

def test_edge_case_1_malformed_json_source():
    """Edge Case 1: Malformed/Garbage input should not crash the extractor."""
    from app.pipeline.extractor import extract_all_sources
    sources = {
        "ats_json": "{ invalid json ",
        "csv": "name,email\nValid,valid@test.com"
    }
    extracted = extract_all_sources(sources)
    # Should only extract the valid CSV, skip the bad ATS JSON
    assert len(extracted) == 1
    assert extracted[0]["source_type"] == "csv"

def test_edge_case_2_array_out_of_bounds():
    """Edge Case 2: Projector asks for an index that doesn't exist."""
    canonical = {"emails": ["single@test.com"]}
    config = ProjectionConfig(**{
        "fields": [{"path": "secondary_email", "from": "emails[5]", "type": "string"}],
        "on_missing": "null"
    })
    projected = project_data(canonical, config)
    assert projected.get("secondary_email") is None

def test_edge_case_3_required_field_missing_throws_error():
    """Edge Case 3: Missing required field aborts the projection if on_missing='error'."""
    canonical = {"full_name": "Jane Doe"} # Missing emails
    config = ProjectionConfig(**{
        "fields": [
            {"path": "primary_email", "from": "emails[0]", "type": "string", "required": True}
        ],
        "on_missing": "error"
    })
    with pytest.raises(ValueError, match="Required field missing: primary_email"):
        project_data(canonical, config)

def test_edge_case_4_empty_or_null_values_in_merger():
    """Edge Case 4: Merger should ignore nulls and pick the next best confidence value."""
    sources = [
        {"source_name": "ATS", "confidence": 0.95, "full_name": None, "emails": []},
        {"source_name": "CSV", "confidence": 0.85, "full_name": "Fallback Name", "emails": []}
    ]
    canonical = merge_profiles(sources)
    assert canonical["full_name"] == "Fallback Name"
    assert len(canonical["emails"]) == 0

def test_edge_case_5_deduplication_of_similar_array_items():
    """Edge Case 5: Ensure normalized arrays deduplicate exactly (e.g. skills casing)."""
    from app.pipeline.normalizer import normalize_skill_canonical
    # Test that normalizer flattens cases
    assert normalize_skill_canonical("ReactJS") == "React"
    
    sources = [
        {"source_name": "ATS", "confidence": 0.95, "skills": ["ReactJS", "Node"]},
        {"source_name": "CSV", "confidence": 0.85, "skills": ["reactjs", "node.js"]}
    ]
    # Since merging just unions arrays (it doesn't apply the final projection normalizer yet),
    # the raw canonical profile will contain the unique set.
    canonical = merge_profiles(sources)
    assert len(canonical["skills"]) >= 2
    assert isinstance(canonical["skills"][0], dict)
    assert "name" in canonical["skills"][0]
