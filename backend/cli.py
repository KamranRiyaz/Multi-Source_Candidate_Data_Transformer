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
    parser.add_argument("--out", default="results.json", help="Output JSON path (defaults to results.json)")
    
    args = parser.parse_args()
    
    # Interactive mode if no arguments are provided
    if len(sys.argv) == 1:
        print("\n=== Multi-Source Candidate Data Transformer ===")
        print("Running in interactive mode. Leave input blank to skip a file.\n")
        args.csv = input("Path to recruiter CSV file (e.g. ./sample_data/recruiter.csv): ").strip() or None
        args.ats = input("Path to ATS JSON file (e.g. ./sample_data/ats.json): ").strip() or None
        args.github = input("Path to GitHub JSON file (e.g. ./sample_data/github.json): ").strip() or None
        args.notes = input("Path to recruiter notes (.txt) file (e.g. ./sample_data/notes.txt): ").strip() or None
        args.config = input("Path to Projection Config JSON file (e.g. ./sample_data/config.json): ").strip() or None
        args.out = input("Output JSON path (default: results.json): ").strip() or "results.json"
        print("\nProcessing...\n")

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
        print("Error: Provide at least one valid source file.")
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
        print(f"✅ Output successfully written to {args.out}")
        print("\n--- Generated Profile ---")
        print(result_json)
        print("-------------------------\n")
    else:
        print("\n✅ Successfully Transformed Profile:\n")
        print("=" * 40)
        print(result_json)
        print("=" * 40)
        print("\n")

if __name__ == "__main__":
    main()
