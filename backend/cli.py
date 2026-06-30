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
    parser.add_argument("--dir", help="Path to a directory containing candidate files to process together")
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
        print("Running in interactive mode. Leave input blank to skip.")
        print("You can provide a directory to process multiple files at once.\n")
        args.dir = input("Path to a directory (e.g. ../sample_data) [Leave blank for individual files]: ").strip() or None
        if not args.dir:
            args.csv = input("Path to recruiter CSV file (e.g. ../sample_data/recruiter.csv): ").strip() or None
            args.ats = input("Path to ATS JSON file (e.g. ../sample_data/ats.json): ").strip() or None
            args.github = input("Path to GitHub JSON file (e.g. ../sample_data/github.json): ").strip() or None
            args.notes = input("Path to recruiter notes (.txt) file (e.g. ../sample_data/notes.txt): ").strip() or None
        args.config = input("Path to Projection Config JSON file (e.g. ../sample_data/config.json): ").strip() or None
        args.out = input("Output JSON path (default: results.json): ").strip() or "results.json"
        print("\nProcessing...\n")

    sources = {}
    
    if args.dir and os.path.isdir(args.dir):
        sources["csv_list"] = []
        sources["ats_json_list"] = []
        sources["github_list"] = []
        sources["notes_list"] = []
        
        for filename in os.listdir(args.dir):
            filepath = os.path.join(args.dir, filename)
            if not os.path.isfile(filepath):
                continue
                
            with open(filepath, 'r') as f:
                content = f.read()
                
            if filename.endswith('.csv'):
                sources["csv_list"].append(content)
            elif filename.endswith('.txt'):
                sources["notes_list"].append(content)
            elif filename.endswith('.json') and 'config' not in filename.lower():
                try:
                    data = json.loads(content)
                    if isinstance(data, dict) and ('login' in data or 'repos_url' in data):
                        sources["github_list"].append(content)
                    else:
                        sources["ats_json_list"].append(content)
                except:
                    pass
    else:
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
                
    # Check if we actually found anything
    has_files = any(bool(v) for v in sources.values())
    if not has_files:
        print("Error: Provide at least one valid source file or directory.")
        sys.exit(1)
        
    extracted = extract_all_sources(sources)
    
    from app.pipeline.grouper import group_profiles
    grouped = group_profiles(extracted)
    
    results = []
    
    # Process configuration if provided
    config_obj = None
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config_data = json.load(f)
            config_obj = ProjectionConfig(**config_data)
            
    for group in grouped:
        canonical = merge_profiles(group)
        if config_obj:
            output = project_data(canonical, config_obj)
        else:
            output = canonical
        results.append(output)
            
    # If there's only one candidate, just return the single object to keep the output clean
    if len(results) == 1:
        final_output = results[0]
    else:
        final_output = results
    
    result_json = json.dumps(final_output, indent=2)
    
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
