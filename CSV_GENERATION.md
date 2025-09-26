# CSV Generation in FORD

This document explains how to generate the `automated.csv` file using FORD's CSV generation capabilities.

## Overview

FORD (FORtran Documenter) can now generate a comprehensive CSV file containing information about procedures, variables, I/O operations, and function calls in your Fortran code. This feature complements the existing JSON generation functionality.

## How to Generate automated.csv

### Using the generate_json.py Script

The `generate_json.py` script has been updated to generate both JSON files and the `automated.csv` file:

```bash
python generate_json.py
```

This will:
1. Parse your Fortran source files
2. Generate JSON files with detailed metadata
3. Generate `automated.csv` with procedure information

### Using FORD Programmatically

You can also generate CSV files programmatically:

```python
from ford.fortran_project import Project
from ford.settings import ProjectSettings
from pathlib import Path

# Set up your project
project_settings = ProjectSettings(src_dir=[Path("your_source_directory")])
project = Project(project_settings)
project.correlate()

# Get procedures from modules and programs
all_procedures = []
for module in project.modules:
    if hasattr(module, 'subroutines'):
        all_procedures.extend(module.subroutines)
    if hasattr(module, 'functions'):
        all_procedures.extend(module.functions)
for program in project.programs:
    all_procedures.append(program)

# Process and generate CSV
project.cross_walk_type_dicts(all_procedures)
csv_file = project.procedures_to_csv(all_procedures)
print(f"Generated: {csv_file}")
```

## CSV File Format

The `automated.csv` file contains the following columns:

- **procedure_name**: Name of the procedure (subroutine, function, or program)
- **procedure_type**: Type of procedure (Subroutine, Function, or unknown for programs)
- **file_name**: Source file where the procedure is defined
- **line_number**: Line number where the procedure starts
- **variable_name**: Name of local variables within the procedure
- **variable_type**: Data type of the variable
- **variable_initial**: Initial value of the variable (if any)
- **variable_doc**: Documentation for the variable
- **io_operation**: Type of I/O operation (read/write)
- **io_unit**: Unit number or name used in I/O operations
- **io_file**: File name used in I/O operations
- **io_line**: Line number of the I/O operation
- **call_name**: Name of called procedures
- **call_type**: Type of called procedure
- **call_line**: Line number of the procedure call

## Example Output

```csv
procedure_name,procedure_type,file_name,line_number,variable_name,variable_type,variable_initial,variable_doc,io_operation,io_unit,io_file,io_line,call_name,call_type,call_line
test_subroutine,Subroutine,test_simple.f90,16,,,,,,,,,,,
test_function,Function,test_simple.f90,32,,,,,,,,,,,
test_program,unknown,test_simple.f90,42,,,,,,,,,test_subroutine,Subroutine,16
test_program,unknown,test_simple.f90,42,,,,,,,,,test_function,Function,32
```

## Configuration

The CSV generation respects the same project settings as the JSON generation:

- **src_dir**: Source directories to analyze
- **exclude**: Files to exclude from analysis
- **exclude_dir**: Directories to exclude from analysis

## Notes

- The CSV file is generated in the current working directory by default
- Each row represents either a procedure definition or a relationship (variable, I/O operation, or function call)
- Empty columns in a row indicate that information is not applicable for that particular entry
- The CSV format makes it easy to import into spreadsheet applications or analyze with data processing tools

## Integration with Existing Workflow

The CSV generation is fully integrated with FORD's existing functionality:
- It works alongside the JSON generation
- It uses the same parsing and correlation logic
- It respects the same configuration options

This makes it easy to add CSV output to your existing FORD documentation workflow.