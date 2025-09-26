#!/usr/bin/env python3
"""
Simple test script to generate CSV from FORD analysis
"""

import os
import sys
from pathlib import Path

# Add ford module to path
sys.path.insert(0, '/home/runner/work/ford/ford')

from ford.fortran_project import Project
from ford.settings import ProjectSettings

def main():
    """Test CSV generation with a simple setup"""
    
    # Use our isolated test directory
    source_dir = Path("test_src")
    
    print(f"Using source directory: {source_dir}")
    
    try:
        # Create ProjectSettings with the source directory  
        project_settings = ProjectSettings(src_dir=[source_dir])
        project_settings.dbg = False  # Reduce debug output
        
        # Create the project instance
        project = Project(project_settings)
        
        print("Attempting to correlate project...")
        # Try to correlate the project data
        project.correlate()
        
        print("Getting procedures...")
        procedures = project.get_procedures()
        print(f"Found {len(procedures)} procedures")
        
        # Also check modules and programs
        print(f"Modules: {len(project.modules)}")
        print(f"Programs: {len(project.programs)}")
        
        # List what we found
        if project.modules:
            for module in project.modules:
                print(f"  Module: {module.name}")
                if hasattr(module, 'subroutines'):
                    print(f"    Subroutines: {[s.name for s in module.subroutines]}")
                if hasattr(module, 'functions'):
                    print(f"    Functions: {[f.name for f in module.functions]}")
        
        if project.programs:
            for program in project.programs:
                print(f"  Program: {program.name}")
        
        # Get all procedures from modules and programs
        all_procedures = []
        for module in project.modules:
            if hasattr(module, 'subroutines'):
                all_procedures.extend(module.subroutines)
            if hasattr(module, 'functions'):
                all_procedures.extend(module.functions)
        for program in project.programs:
            all_procedures.append(program)
        
        print(f"Total procedures found: {len(all_procedures)}")
        
        if all_procedures or procedures:
            # Use all_procedures if available, otherwise use procedures
            procs_to_use = all_procedures if all_procedures else procedures
            
            # Cross-walk type dictionaries
            project.cross_walk_type_dicts(procs_to_use)
            
            # Generate CSV
            csv_file = project.procedures_to_csv(procs_to_use)
            if csv_file:
                print(f"Successfully generated: {csv_file}")
                
                # Show first few lines of the CSV
                with open(csv_file, 'r') as f:
                    print("\nFirst 10 lines of the CSV:")
                    for i, line in enumerate(f):
                        if i < 10:
                            print(line.strip())
                        else:
                            break
            else:
                print("Failed to generate CSV")
        else:
            print("No procedures found to process")
            
    except Exception as e:
        print(f"Error during processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()