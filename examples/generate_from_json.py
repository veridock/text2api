#!/usr/bin/env python3
"""
Script to generate a FastAPI server from a JSON API specification.
"""
import json
import os
import sys
from pathlib import Path
from text2api.generators.fastapi_generator import FastAPIGenerator

def load_spec_from_file(spec_file: str) -> dict:
    """Load API specification from a JSON file."""
    try:
        with open(spec_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file {spec_file}: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <spec_file.json> <output_dir> [project_name]")
        sys.exit(1)
    
    spec_file = sys.argv[1]
    output_dir = sys.argv[2]
    project_name = sys.argv[3] if len(sys.argv) > 3 else Path(spec_file).stem
    
    # Load the API specification
    api_spec = load_spec_from_file(spec_file)
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate the FastAPI server
    try:
        generator = FastAPIGenerator(output_dir=output_dir)
        generator.set_project_name(project_name)
        # Set the API spec directly to bypass the NLP parsing
        generator.api_spec = api_spec
        
        # Generate the server code
        result = generator.generate()
        print(f"✅ Successfully generated FastAPI server in: {output_dir}")
        print("\nNext steps:")
        print(f"1. cd {os.path.abspath(output_dir)}")
        print("2. pip install -r requirements.txt")
        print("3. uvicorn app.main:app --reload")
        print("\nOpen http://localhost:8000/docs to view the API documentation")
        
    except Exception as e:
        print(f"❌ Error generating server: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
