# SWAT+ Model Documentation with FORD

## Overview

This guide addresses common issues when attempting to generate documentation for SWAT+ (Soil and Water Assessment Tool Plus) Fortran code using FORD.

## Common Issues with SWAT+ Input Files

### Issue 1: File Format Expectations

**Problem**: SWAT+ uses various input file formats (TxtInOut directory) that are not Fortran source files.

**What Users Often Try**:
- Users may attempt to point FORD at the `TxtInOut` directory containing model input/output files
- These files include: `.dat`, `.txt`, `.cal`, `.cha`, `.hru`, `.sub` files
- These are data files, not Fortran source code

**Solution**:
FORD is designed to document Fortran **source code**, not model input/output files. To document SWAT+:
1. Point FORD at the Fortran source code directory (typically `src/` or similar)
2. Input/output file formats should be documented in separate markdown pages
3. Use FORD's `page_dir` option to include additional documentation pages

### Issue 2: Incorrect Project Configuration

**Original Input** (Common Mistake):
```yaml
---
project: SWAT+ Model
src_dir: ./TxtInOut
output_dir: ./doc
---
```

**Issues**:
- `src_dir` points to data files instead of Fortran source
- No documentation on what the project does
- Missing file extensions specification

**Corrected Configuration**:
```yaml
---
project: SWAT+ Model
author: [Your Name]
summary: Soil and Water Assessment Tool Plus - A hydrological model
src_dir: ./src
         ./modules
output_dir: ./documentation
exclude_dir: ./TxtInOut
             ./build
extensions: f90
            f
            F90
docmark: !
predocmark: >
display: public
         protected
source: true
graph: true
page_dir: ./pages
---

# SWAT+ Model Documentation

This documentation covers the SWAT+ hydrological model Fortran source code.
```

### Issue 3: Mixed File Types

**Problem**: SWAT+ projects often contain:
- Fortran source files (`.f90`, `.f`, `.F90`)
- Input data files (`.txt`, `.dat`)
- Configuration files
- Output files

**What Happened**:
Users tried to include all files, causing FORD to fail parsing non-Fortran content.

**Fix**:
1. Use `extensions` to specify only Fortran file types
2. Use `exclude_dir` to skip data directories
3. Use `exclude` to skip specific files

Example:
```yaml
extensions: f90
            F90
            f
exclude_dir: ./TxtInOut
             ./build
             ./temp
exclude: config.txt
         README.txt
```

### Issue 4: Documentation Comments

**Problem**: SWAT+ source code may use different comment styles.

**Original Code** (No FORD-compatible docs):
```fortran
! This subroutine reads HRU data
subroutine read_hru_data()
  ! Open file
  open(unit=10, file='hru.txt')
end subroutine
```

**What Needs to Change**:
FORD requires special comment markers (default: `!` for docmark)

**Corrected Code**:
```fortran
!! This subroutine reads Hydrologic Response Unit (HRU) data from input files
!! @param None
!! @return Populates HRU data structures in memory
subroutine read_hru_data()
  ! Internal comment (not included in docs)
  open(unit=10, file='hru.txt')
end subroutine
```

Or configure FORD to use existing comment style:
```yaml
docmark: !
predocmark: !
```

### Issue 5: Large Projects with Many Files

**Problem**: SWAT+ is a large model with many source files.

**What to Do**:
1. Organize source into logical directories:
   ```
   src/
   ├── hydrology/
   ├── climate/
   ├── management/
   └── utilities/
   ```

2. Use multiple `src_dir` entries:
   ```yaml
   src_dir: ./src/hydrology
            ./src/climate
            ./src/management
            ./src/utilities
   ```

3. Create a page structure matching code organization:
   ```
   pages/
   ├── index.md
   ├── hydrology.md
   ├── climate.md
   └── management.md
   ```

## Comparison: Before and After

### Before (Non-working Configuration)
```yaml
---
project: SWAT
src_dir: ./TxtInOut
---
```

**Issues**:
- Points to data files, not source code
- Missing essential configuration
- No file extension specification
- No documentation content

**Result**: FORD fails to find any Fortran files or produces errors parsing data files

### After (Working Configuration)
```yaml
---
project: SWAT+ Model
author: SWAT+ Development Team
summary: Soil and Water Assessment Tool Plus
src_dir: ./src
output_dir: ./ford_docs
extensions: f90 F90 f
exclude_dir: ./TxtInOut ./build
docmark: !!
predocmark: >
display: public protected
source: true
graph: true
---

# SWAT+ Hydrological Model

Complete documentation for the SWAT+ model source code.
```

**Result**: FORD successfully generates documentation from Fortran source files

## Best Practices for SWAT+ Documentation

1. **Separate Code from Data**
   - Keep Fortran source in `src/` directory
   - Keep model inputs/outputs in `TxtInOut/` or `data/`
   - Use `exclude_dir` to prevent FORD from processing data files

2. **Add Inline Documentation**
   - Document each module, subroutine, and function
   - Explain parameters and return values
   - Include algorithm descriptions for complex calculations

3. **Create Supplementary Pages**
   - File format descriptions
   - User guides
   - Theoretical background
   - Example applications

4. **Use FORD Features**
   - Enable call graphs with `graph: true`
   - Show source code with `source: true`
   - Link to related subroutines and modules

5. **Test Incrementally**
   - Start with one module
   - Verify documentation builds
   - Add more modules gradually
   - Fix issues as they arise

## Example Minimal Working Setup

Directory structure:
```
swatplus/
├── src/              # Fortran source files
│   ├── main.f90
│   ├── hydrology.f90
│   └── climate.f90
├── TxtInOut/         # Model data (excluded)
├── ford_project.md   # FORD configuration
└── pages/            # Additional documentation
    └── index.md
```

`ford_project.md`:
```yaml
---
project: SWAT+ Model
src_dir: ./src
output_dir: ./docs
extensions: f90
exclude_dir: ./TxtInOut
---

# SWAT+ Model Documentation

Auto-generated documentation for SWAT+ Fortran source code.
```

Run FORD:
```bash
ford ford_project.md
```

## Conclusion

The key to successfully using FORD with SWAT+ is understanding that:
1. FORD documents **source code**, not data files
2. The `TxtInOut` directory contains data, not Fortran code
3. Proper configuration is essential for successful documentation generation
4. Inline documentation comments make the output much more useful

For questions or issues, refer to the [FORD documentation](https://forddocs.readthedocs.io) or open an issue on the FORD GitHub repository.
