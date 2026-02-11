# Troubleshooting FORD Input File Issues

## Common Problem: Pointing FORD at Data Files Instead of Source Code

### The Issue

A common mistake when first using FORD is attempting to generate documentation from data files, model inputs, or other non-Fortran content.

### Example Scenario

**User's Original Attempt:**
```bash
$ ford my_project.md
```

With configuration file `my_project.md`:
```yaml
---
project: My Project
src_dir: ./TxtInOut
---
```

**What Happened:**
- FORD found no Fortran files, OR
- FORD crashed trying to parse `.txt`, `.dat`, or other data files as Fortran code
- Error messages like: "No Fortran files found" or "Parse error"

### Root Cause

The user pointed `src_dir` at a directory containing model input/output data files (commonly `TxtInOut` in SWAT+ models or similar hydrological modeling projects) instead of Fortran source code.

### Symptoms

1. **No files found:**
   ```
   WARNING: No Fortran files found in ./TxtInOut
   ```

2. **Parse errors:**
   ```
   ERROR: Could not parse file: ./TxtInOut/hru.dat
   Fatal error in parsing
   ```

3. **Wrong file types:**
   ```
   INFO: Skipping non-Fortran file: data.txt
   INFO: Skipping non-Fortran file: config.dat
   ```

## The Solution

### Step 1: Identify Your Source Code Directory

FORD needs to process **Fortran source code** files, typically with extensions:
- `.f90` (Fortran 90/95/2003/2008)
- `.f` or `.for` (Fortran 77/90)
- `.F90` or `.F` (Fortran with preprocessing)

Find where your Fortran files are located:
```bash
find . -name "*.f90" -o -name "*.f" -o -name "*.F90"
```

Common locations:
- `./src/`
- `./source/`
- `./fortran/`
- `./code/`

### Step 2: Update Configuration

**Corrected `my_project.md`:**
```yaml
---
project: My Project
author: Your Name
summary: Brief description of what your code does
src_dir: ./src
output_dir: ./documentation
extensions: f90 f F90
exclude_dir: ./TxtInOut
             ./data
             ./build
docmark: !!
source: true
---

# My Project Documentation

This is auto-generated documentation for My Project's Fortran source code.
```

### Step 3: Exclude Data Directories

Explicitly exclude directories containing data files:
```yaml
exclude_dir: ./TxtInOut
             ./data
             ./input
             ./output
             ./results
             ./build
             ./bin
             ./obj
```

### Step 4: Specify File Extensions

Only include Fortran source files:
```yaml
extensions: f90
            F90
            f
            F
```

## Complete Before/After Comparison

### ❌ Before (Broken)

**Directory Structure:**
```
my_project/
├── TxtInOut/          # Data files (NOT source code)
│   ├── hru.dat
│   ├── channels.txt
│   └── config.dat
└── ford_config.md
```

**ford_config.md:**
```yaml
---
project: My Project
src_dir: ./TxtInOut
---
```

**Result:** FORD fails - no Fortran files found or parse errors

### ✅ After (Working)

**Directory Structure:**
```
my_project/
├── src/               # Fortran source code
│   ├── main.f90
│   ├── hydrology.f90
│   └── utilities.f90
├── TxtInOut/          # Data files (excluded)
│   ├── hru.dat
│   ├── channels.txt
│   └── config.dat
├── ford_config.md
└── pages/
    └── index.md
```

**ford_config.md:**
```yaml
---
project: My Project
author: Development Team
summary: Hydrological modeling software
src_dir: ./src
output_dir: ./docs
extensions: f90 F90 f
exclude_dir: ./TxtInOut
docmark: !!
predocmark: >
display: public protected
source: true
graph: true
page_dir: ./pages
---

# My Project

Complete documentation for My Project Fortran source code.
```

**Result:** FORD successfully generates documentation from Fortran files

## What I Did to Make It Work

1. **Located the Actual Source Code**
   - Searched for `.f90`, `.f`, and `.F90` files
   - Found them in `./src/` directory (not `./TxtInOut/`)

2. **Fixed Configuration File**
   - Changed `src_dir: ./TxtInOut` to `src_dir: ./src`
   - Added `extensions: f90 f F90` to specify Fortran files only
   - Added `exclude_dir: ./TxtInOut` to skip data files

3. **Added Proper Documentation**
   - Set project name, author, and summary
   - Configured documentation markers (`docmark` and `predocmark`)
   - Enabled source code display and call graphs

4. **Tested Incrementally**
   - Ran FORD on configuration: `ford ford_config.md`
   - Verified documentation generated successfully
   - Checked output in web browser

5. **Added Inline Documentation**
   - Added `!!` comment blocks before modules, subroutines, and functions
   - Documented parameters and return values
   - Included algorithm explanations

## Key Differences

| Aspect | Wrong Approach | Correct Approach |
|--------|---------------|------------------|
| **src_dir** | `./TxtInOut` (data) | `./src` (source code) |
| **File Types** | `.dat`, `.txt` | `.f90`, `.f`, `.F90` |
| **Purpose** | Model inputs/outputs | Fortran source code |
| **FORD Processing** | Fails/Errors | Success |
| **Extensions** | Not specified | Explicitly listed |
| **Exclude** | Nothing | Data directories |

## Checklist for Success

- [ ] Identified where Fortran source files are located
- [ ] Updated `src_dir` to point at source code directory
- [ ] Added `extensions` to specify Fortran file types only
- [ ] Added `exclude_dir` for data directories
- [ ] Set project metadata (name, author, summary)
- [ ] Configured documentation comment markers
- [ ] Tested with: `ford your_config.md`
- [ ] Verified documentation generated without errors
- [ ] Added inline documentation to source files

## Additional Resources

- **FORD Documentation**: https://forddocs.readthedocs.io
- **Project File Options**: See `project_file_options.rst`
- **Writing Documentation**: See `writing_documentation.rst`
- **SWAT+ Specific Guide**: See `swatplus_documentation_guide.md`

## Still Having Issues?

If FORD still isn't working:

1. **Check file permissions**: Ensure FORD can read your source files
2. **Verify file encoding**: Use UTF-8 encoding for all files
3. **Test with minimal config**: Start with bare minimum configuration
4. **Check for syntax errors**: Ensure your Fortran code compiles
5. **Look at examples**: See the `example/` directory in FORD repository
6. **Enable verbose output**: Run `ford -d your_config.md` for debug info

Remember: FORD is a **documentation generator for Fortran source code**, not a general-purpose file processor. It needs actual `.f90`, `.f`, or `.F90` files to work with!
