#!/usr/bin/env python3

import re

# Test the method implementation directly
def extract_local_variables_from_source(source_text):
    """Extract local variable declarations from source code."""
    local_vars = []
    
    if not source_text:
        return local_vars
        
    # Simple regex to find variable declarations
    var_patterns = [
        r'^\s*(integer|real|character|logical|double\s+precision)\s*(?:\([^)]*\))?\s*::\s*([^!]+)',
        r'^\s*(character)\s*\([^)]*\)\s*::\s*([^!]+)',
    ]
    
    source_lines = source_text.split('\n')
    print(f"Processing {len(source_lines)} lines of source code")
    
    for line_num, line in enumerate(source_lines):
        for pattern in var_patterns:
            match = re.match(pattern, line.strip(), re.IGNORECASE)
            if match:
                print(f"Line {line_num}: Found match: {line.strip()}")
                var_type = match.group(1)
                var_declarations = match.group(2)
                
                # Parse variable names (handle multiple variables on one line)
                var_names = [name.strip().split('=')[0].strip() for name in var_declarations.split(',')]
                print(f"  Type: {var_type}, Variables: {var_names}")
                
                for var_name in var_names:
                    if var_name:
                        # Create a mock variable object
                        class MockVariable:
                            def __init__(self, name, var_type):
                                self.name = name
                                self.var_type = var_type
                                self.full_type = var_type
                                self.dimension = ""
                                
                            def meta(self, key):
                                if key == 'summary':
                                    return f"Local variable of type {self.var_type}"
                                return ""
                        
                        mock_var = MockVariable(var_name, var_type)
                        local_vars.append(mock_var)
    
    return local_vars

# Read the actual source file and test
with open('/home/runner/work/ford/ford/test_data/src/basin_print_codes_read.f90', 'r') as f:
    source = f.read()

print("Testing local variable extraction...")
vars = extract_local_variables_from_source(source)
print(f"Found {len(vars)} variables:")
for var in vars:
    print(f"  - {var.name}: {var.var_type}")