# FORD Comparison Example

This directory contains an example demonstrating FORD's comparison functionality.

## Quick Start

### Using Pre-Generated Metadata

If you already have FORD documentation from two different versions:

```bash
# Compare two metadata files
ford-compare old_version/doc/modules.json new_version/doc/modules.json

# Save to a file
ford-compare old.json new.json -o api_changes.txt

# Verbose output
ford-compare old.json new.json --verbose
```

### Comparing Git Commits

Use the `compare_commits_example.py` script to compare two git commits:

```bash
# Compare two commits
python compare_commits_example.py abc123 def456

# Compare tag with HEAD
python compare_commits_example.py v1.0.0 HEAD

# Custom project file
python compare_commits_example.py v1.0 v2.0 --project my_ford.md -o report.txt
```

## Example Output

When comparing two versions, you'll get a report like:

```
================================================================================
FORD Metadata Comparison Report
================================================================================

MODULES
--------------------------------------------------------------------------------
  New modules (1):
    + new_module

PROCEDURES (Functions and Subroutines)
--------------------------------------------------------------------------------
  New procedures (3):
    + module_a::new_function
    + module_b::new_subroutine
  Removed procedures (1):
    + module_a::old_function

DERIVED TYPES
--------------------------------------------------------------------------------
  New types (1):
    + module_a::new_type

SUMMARY
--------------------------------------------------------------------------------
Total changes detected: 6
  Modules: +1 -0
  Procedures: +3 -1
  Types: +1 -0
  Files: +1 -0
================================================================================
```

## What Gets Compared

The comparison tool analyzes:
- **Modules and Submodules**: New, removed, or modified
- **Procedures**: Functions and subroutines
- **Derived Types**: User-defined types
- **Variables**: Module-level variables (verbose mode)
- **Files**: Source files in the documentation

## Real-World Example

### Before (v1.0):

```fortran
module math_operations
    implicit none
    
    type :: point
        real :: x, y
    end type point
    
contains
    
    function add(a, b) result(c)
        real, intent(in) :: a, b
        real :: c
        c = a + b
    end function add
    
end module math_operations
```

### After (v2.0):

```fortran
module math_operations
    implicit none
    
    type :: point
        real :: x, y
    end type point
    
    type :: vector  ! NEW
        real :: x, y, z
    end type vector
    
contains
    
    function add(a, b) result(c)
        real, intent(in) :: a, b
        real :: c
        c = a + b
    end function add
    
    function subtract(a, b) result(c)  ! NEW
        real, intent(in) :: a, b
        real :: c
        c = a - b
    end function subtract
    
end module math_operations

module io_operations  ! NEW MODULE
    implicit none
contains
    
    subroutine write_data(filename, data)
        character(len=*), intent(in) :: filename
        real, intent(in) :: data(:)
        ! ... implementation ...
    end subroutine write_data
    
end module io_operations
```

### Comparison Result:

```
MODULES
  New modules (1):
    + io_operations

PROCEDURES
  New procedures (2):
    + io_operations::write_data
    + math_operations::subtract

DERIVED TYPES
  New types (1):
    + math_operations::vector
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: API Change Detection

on: [pull_request]

jobs:
  compare-api:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
        with:
          fetch-depth: 0
      
      - name: Install FORD
        run: pip install ford
      
      - name: Generate docs for base branch
        run: |
          git checkout ${{ github.base_ref }}
          ford ford.md
          mv doc base_doc
      
      - name: Generate docs for PR branch
        run: |
          git checkout ${{ github.sha }}
          ford ford.md
      
      - name: Compare API
        run: |
          ford-compare base_doc/modules.json doc/modules.json -o api_changes.txt
      
      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: api-changes
          path: api_changes.txt
```

## See Also

- [COMPARE.md](../COMPARE.md) - Full documentation
- [ford.compare](../ford/compare.py) - Source code
- [test_compare.py](../test/test_compare.py) - Test examples
