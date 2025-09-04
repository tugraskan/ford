#!/usr/bin/env python3

import re

# Test the regex pattern for variable extraction
source_lines = [
    "      character (len=500) :: header = \"\" !              |header of file",
    "      character (len=80) :: titldum = \"\" !              |title of file", 
    "      character (len=16) :: name = \"\"  !              |name",
    "      integer :: eof = 0               !              |end of file",
    "      logical :: i_exist               !              |check to determine if file exists",
    "      integer :: ii = 0                !none          |counter",
    "      integer :: result",
]

print("Testing variable extraction regex...")

var_patterns = [
    r'^\s*(integer|real|character|logical|double\s+precision)\s*(?:\([^)]*\))?\s*::\s*([^!]+)',
    r'^\s*(character)\s*\([^)]*\)\s*::\s*([^!]+)',
]

for line in source_lines:
    for pattern in var_patterns:
        match = re.match(pattern, line.strip(), re.IGNORECASE)
        if match:
            var_type = match.group(1)
            var_declarations = match.group(2)
            
            # Parse variable names (handle multiple variables on one line)
            var_names = [name.strip().split('=')[0].strip() for name in var_declarations.split(',')]
            
            print(f"Line: {line}")
            print(f"  Type: {var_type}")
            print(f"  Variables: {var_names}")
            print()
            break