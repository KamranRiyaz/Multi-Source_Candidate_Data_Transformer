from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict

class Location(BaseModel):
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None

class Links(BaseModel):
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    other: List[str] = Field(default_factory=list)

class Skill(BaseModel):
    name: str
    confidence: float
    sources: List[str] = Field(default_factory=list)

class Experience(BaseModel):
    company: str
    title: str
    start: Optional[str] = None
    end: Optional[str] = None
    summary: Optional[str] = None

class Education(BaseModel):
    institution: str
    degree: Optional[str] = None
    field: Optional[str] = None
    end_year: Optional[int] = None

class Provenance(BaseModel):
    field: str
    source: str
    method: str

class CanonicalProfile(BaseModel):
    candidate_id: str
    full_name: str
    emails: List[str] = Field(default_factory=list)
    phones: List[str] = Field(default_factory=list)
    location: Location = Field(default_factory=Location)
    links: Links = Field(default_factory=Links)
    headline: Optional[str] = None
    years_experience: Optional[float] = None
    skills: List[Skill] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    provenance: List[Provenance] = Field(default_factory=list)
    overall_confidence: float = 0.0

class FieldConfig(BaseModel):
    # CRITICAL: Allows Pydantic to map the JSON key "from" to "from_path"
    model_config = ConfigDict(populate_by_name=True)

    path: str
    type: str
    required: bool = False
    from_path: Optional[str] = Field(default=None, alias="from")
    
    # Enforce strict literals for normalization
    normalize: Optional[Literal[
        "E164", 
        "E.164", 
        "canonical", 
        "uppercase", 
        "lowercase", 
        "YYYY-MM",        # Added for dates
        "email",          # Added for emails
        "ISO-3166-2"]] = None
    default_value: Optional[Any] = None

class ProjectionConfig(BaseModel):
    fields: List[FieldConfig]
    include_confidence: bool = True
    include_provenance: bool = True
    # Enforce strict literals for missing handling
    on_missing: Literal["null", "omit", "error"] = "null"

class TransformationRequest(BaseModel):
    sources: Dict[str, Any] 
    config: Optional[ProjectionConfig] = None