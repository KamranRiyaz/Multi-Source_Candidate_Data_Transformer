from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import TransformationRequest, CanonicalProfile
from .pipeline.extractor import extract_all_sources
from .pipeline.merger import merge_profiles
from .pipeline.projector import project_data

app = FastAPI(title="Candidate Data Transformer API")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/transform")
def transform_profile(request: TransformationRequest):
    try:
        # 1. Detect & Extract
        extracted = extract_all_sources(request.sources)
        if not extracted:
            raise HTTPException(status_code=400, detail="No valid data extracted from sources.")
            
        # 2 & 3. Normalize & Merge
        canonical_dict = merge_profiles(extracted)
        
        # 4. Project
        projected = {}
        if request.config:
            projected = project_data(canonical_dict, request.config)
        else:
            projected = canonical_dict
            
        return {
            "canonical": canonical_dict,
            "projected": projected
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
