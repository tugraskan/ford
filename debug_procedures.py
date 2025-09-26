#!/usr/bin/env python3
"""
Debug script to examine what data is available in procedures
"""

import os
import sys
from pathlib import Path

# Add ford module to path
sys.path.insert(0, '/home/runner/work/ford/ford')

from ford.fortran_project import Project
from ford.settings import ProjectSettings

def main():
    """Debug what data is available in procedures"""
    
    source_dir = Path("test_src")
    
    try:
        project_settings = ProjectSettings(src_dir=[source_dir])
        project_settings.dbg = False
        
        project = Project(project_settings)
        project.correlate()
        
        # Get all procedures
        all_procedures = []
        for module in project.modules:
            if hasattr(module, 'subroutines'):
                all_procedures.extend(module.subroutines)
            if hasattr(module, 'functions'):
                all_procedures.extend(module.functions)
        for program in project.programs:
            all_procedures.append(program)
        
        project.cross_walk_type_dicts(all_procedures)
        
        for proc in all_procedures:
            print(f"\n=== Procedure: {proc.name} ===")
            print(f"Type: {getattr(proc, 'proctype', 'unknown')}")
            print(f"Filename: {getattr(proc, 'filename', '')}")
            print(f"Line: {getattr(proc, 'line_number', '')}")
            
            # List all attributes
            attrs = [attr for attr in dir(proc) if not attr.startswith('_')]
            print(f"Available attributes: {attrs}")
            
            # Check for variables
            if hasattr(proc, 'variables'):
                print(f"Variables: {[v.name for v in proc.variables]}")
            if hasattr(proc, 'var_ug_local'):
                print(f"Local variables: {[v.name for v in proc.var_ug_local]}")
            if hasattr(proc, 'args'):
                print(f"Arguments: {[arg.name for arg in proc.args]}")
            
            # Check for I/O
            if hasattr(proc, 'io_read'):
                print(f"Read operations: {len(proc.io_read)}")
            if hasattr(proc, 'io_write'):
                print(f"Write operations: {len(proc.io_write)}")
                
            # Check for calls
            if hasattr(proc, 'calls'):
                print(f"Calls: {[call.name for call in proc.calls]}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()