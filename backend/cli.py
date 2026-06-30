import argparse
import json
import sys
import os
from app.pipeline.extractor import extract_all_sources
from app.pipeline.merger import merge_profiles
from app.pipeline.projector import project_data
from app.models import ProjectionConfig

def main():
    parser = argparse.ArgumentParser(description="Multi-Source Candidate Data Transformer")
    parser.add_argument("--csv", help="Path to recruiter CSV file")
    parser.add_argument("--ats", help="Path to ATS JSON file")
    parser.add_argument("--github", help="Path to GitHub JSON file")
    parser.add_argument("--notes", help="Path to recruiter notes (.txt) file")
    parser.add_argument("--config", help="Path to Projection Config JSON file")
    parser.add_argument("--out", help="Output JSON path (optional, prints to stdout if omitted)")
    
    args = parser.parse_args()
    
    sources = {}
    
    if args.csv and os.path.exists(args.csv):
        with open(args.csv, 'r') as f:
            sources["csv"] = f.read()
            
    if args.ats and os.path.exists(args.ats):
        with open(args.ats, 'r') as f:
            sources["ats_json"] = f.read()
            
    if args.github and os.path.exists(args.github):
        with open(args.github, 'r') as f:
            sources["github"] = f.read()
            
    if args.notes and os.path.exists(args.notes):
        with open(args.notes, 'r') as f:
            sources["notes"] = f.read()
            
    if not sources:
        print("Error: Provide at least one source file (--csv, --ats, --github, or --notes).")
        sys.exit(1)
        
    extracted = extract_all_sources(sources)
    canonical = merge_profiles(extracted)
    
    output = canonical
    
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config_data = json.load(f)
            config_obj = ProjectionConfig(**config_data)
            output = project_data(canonical, config_obj)
            
    result_json = json.dumps(output, indent=2)
    
    if args.out:
        with open(args.out, 'w') as f:
            f.write(result_json)
        print(f"Output written to {args.out}")
    else:
        print(result_json)

if __name__ == "__main__":
    main()

