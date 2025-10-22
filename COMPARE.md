# Comparing FORD Documentation Between Commits

FORD now includes functionality to compare documentation metadata between different versions of your Fortran project. This is useful for:

- Identifying new or removed modules, subroutines, and functions
- Tracking API changes between versions
- Reviewing changes in input/output files
- Generating change reports for release notes

## Overview

The comparison functionality works by:

1. Generating FORD metadata (JSON) for each version
2. Comparing the metadata to identify differences
3. Producing a detailed report of changes

## Installation

The comparison tools are included with FORD. After installing FORD, you'll have access to:

- `ford-compare`: Command-line tool for comparing metadata files
- Python API: `ford.compare` module for programmatic access

## Quick Start

### Comparing Two Metadata Files

If you already have FORD metadata files (modules.json) from different versions:

```bash
ford-compare old_doc/modules.json new_doc/modules.json
```

Save the report to a file:

```bash
ford-compare old_doc/modules.json new_doc/modules.json -o changes.txt
```

Include detailed information (shows public module variables):

```bash
ford-compare old_doc/modules.json new_doc/modules.json --verbose
```

## Generating Metadata for Comparison

To generate metadata, ensure your FORD project file includes the `externalize` option:

```markdown
---
project: My Fortran Project
externalize: true
output_dir: ./doc
---
```

Or in TOML format:

```toml
[project]
name = "My Fortran Project"
externalize = true
output_dir = "./doc"
```

Then run FORD to generate documentation and metadata:

```bash
ford my_project.md
```

This creates `doc/modules.json` containing the metadata.

## Comparing Git Commits

### Using the Utility Script

The `ford_diff_utility.py` script provides a convenient way to compare different project versions:

```bash
# Compare two project directories
python ford_diff_utility.py compare-dirs old_version/ new_version/ ford.md

# Generate metadata for a single version
python ford_diff_utility.py generate ford.md -o output/

# Compare existing metadata files
python ford_diff_utility.py compare old.json new.json -v
```

### Using the Example Script (with Git)

The `example/compare_commits_example.py` script can compare commits directly:

```bash
# Compare two commits by hash
python example/compare_commits_example.py abc123 def456

# Compare a tag with current HEAD
python example/compare_commits_example.py v1.0.0 HEAD

# Use a custom project file
python example/compare_commits_example.py v1.0 v2.0 --project my_ford.md
```

## Understanding the Report

The comparison report includes several sections:

### Modules Section
```
MODULES
--------------------------------------------------------------------------------
  New modules (1):
    + new_module
  Removed modules (1):
    - old_module
```

### Procedures Section
```
PROCEDURES (Functions and Subroutines)
--------------------------------------------------------------------------------
  New procedures (2):
    + module_a::new_function
    + module_b::new_subroutine
  Removed procedures (1):
    - module_a::deprecated_function
```

### Derived Types Section
```
DERIVED TYPES (Used in Procedure Inputs/Outputs)
  New types used in procedure arguments (1):
    + module_a::new_type
```

### Variables Section (Verbose Mode)
```
PUBLIC MODULE VARIABLES
  New public variables (2):
    + module_a::new_var
    + module_b::config_var
```

### Summary
```
SUMMARY
================================================================================
Total changes detected: 7
  Modules: +1 -1
  Procedures: +2 -1
  Types: +1 -0
  Files: +2 -0
================================================================================
```

## Programmatic Usage

You can also use the comparison functionality in your Python scripts:

```python
from pathlib import Path
from ford.compare import compare_commits, load_metadata, compare_metadata

# Compare two metadata files
old_meta = load_metadata(Path("old_doc/modules.json"))
new_meta = load_metadata(Path("new_doc/modules.json"))

result = compare_metadata(old_meta, new_meta)

# Access specific changes
print(f"New modules: {result.new_modules}")
print(f"Removed procedures: {result.removed_procedures}")
print(f"New types: {result.new_types}")

# Or use the high-level function with formatted output
compare_commits(
    Path("old_doc/modules.json"),
    Path("new_doc/modules.json"),
    output_file=Path("report.txt"),
    verbose=True
)
```

## Use Cases

### Release Documentation

Generate a changelog for your release:

```bash
# Compare previous release with current
ford-compare v1.0/doc/modules.json v2.0/doc/modules.json -o CHANGELOG_API.md
```

### Code Review

Review API changes in a pull request:

```bash
# Compare main branch with feature branch
python ford_diff_utility.py compare-dirs main/ feature-branch/ ford.md
```

### Continuous Integration

Integrate into CI/CD to track API evolution:

```yaml
# Example GitHub Actions workflow
- name: Generate old version metadata
  run: |
    git checkout main
    ford ford.md
    mv doc old_doc
    
- name: Generate new version metadata
  run: |
    git checkout ${{ github.sha }}
    ford ford.md
    
- name: Compare versions
  run: ford-compare old_doc/modules.json doc/modules.json -o api_changes.txt
  
- name: Upload report
  uses: actions/upload-artifact@v2
  with:
    name: api-changes
    path: api_changes.txt
```

## What Gets Compared

The comparison tool analyzes:

1. **Modules**: New, removed, or modified modules and submodules
2. **Procedures**: Functions and subroutines (including their locations)
3. **Derived Types**: User-defined types **that are used in procedure inputs/outputs** (argument types)
4. **Variables**: Public module-level variables that affect the module's API interface (in verbose mode)
5. **Files**: Source files included in the documentation

**Note**: The comparison focuses on API-relevant changes. Internal types and private variables that don't affect procedure interfaces are not tracked.

## Limitations

- File-level changes are based on module locations in the metadata
- The tool compares structural changes but not implementation details
- Documentation text changes are not included in the comparison
- Fine-grained changes within procedures (e.g., parameter changes) are not detected in the basic comparison

## Advanced Features

### Custom Comparison Logic

You can extend the comparison logic by subclassing or modifying the comparison functions:

```python
from ford.compare import ComparisonResult, extract_module_names

def custom_compare(old_meta, new_meta):
    result = ComparisonResult()
    
    # Add your custom comparison logic
    old_modules = extract_module_names(old_meta)
    new_modules = extract_module_names(new_meta)
    
    result.new_modules = new_modules - old_modules
    result.removed_modules = old_modules - new_modules
    
    # ... more custom logic
    
    return result
```

### Filtering Results

Filter the comparison to specific modules:

```python
result = compare_metadata(old_meta, new_meta)

# Filter to specific module
target_module = "my_module"
relevant_procs = {
    proc for proc in result.new_procedures 
    if proc.startswith(f"{target_module}::")
}
print(f"New procedures in {target_module}: {relevant_procs}")
```

## Troubleshooting

### No metadata file generated

Ensure `externalize: true` is set in your FORD project file.

### Comparison shows no changes when changes exist

Check that:
1. Both metadata files are from different versions
2. The metadata was regenerated after code changes
3. Changes are in analyzed entities (modules, procedures, types)

### Memory issues with large projects

For very large projects, consider:
1. Comparing specific modules rather than entire projects
2. Using the command-line tool instead of loading all data into memory
3. Increasing available memory for the Python process

## Further Reading

- [FORD Documentation](https://forddocs.readthedocs.io/)
- [External Projects](https://forddocs.readthedocs.io/en/latest/user_guide/external_projects.html) - How FORD generates metadata
- [GitHub Issues](https://github.com/Fortran-FOSS-Programmers/ford/issues) - Report bugs or request features
