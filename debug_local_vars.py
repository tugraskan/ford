#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '/home/runner/work/ford/ford')

from ford.sourceform import FortranReader

# Try to parse the basin_print_codes_read.f90 file
with open('/home/runner/work/ford/ford/test_data/src/basin_print_codes_read.f90', 'r') as f:
    source = f.read()

reader = FortranReader(source, '/home/runner/work/ford/ford/test_data/src/basin_print_codes_read.f90')

print("Parsing basin_print_codes_read.f90...")

# Get the first procedure found
for obj in reader:
    if hasattr(obj, 'name') and 'basin_print_codes_read' in obj.name:
        print(f"Found procedure: {obj.name}")
        print(f"Type: {type(obj)}")
        print(f"Has variables: {hasattr(obj, 'variables')}")
        if hasattr(obj, 'variables'):
            print(f"Number of variables: {len(obj.variables)}")
            for var in obj.variables:
                print(f"  - {var.name}: {getattr(var, 'vartype', 'unknown type')}")
        
        print(f"Has src: {hasattr(obj, 'src')}")
        if hasattr(obj, 'src'):
            print(f"Source length: {len(obj.src) if obj.src else 0}")
            if obj.src:
                print("First few lines of source:")
                for i, line in enumerate(obj.src.split('\n')[:10]):
                    print(f"  {i+1}: {line}")
        
        print(f"Local variables: {len(obj.local_variables)}")
        print(f"Outside variables: {len(obj.outside_variables_used)}")
        break