---
project: I/O Trace Example
summary: Demonstration of Fortran file I/O operations with comprehensive documentation
author: Example Author
author_description: This example demonstrates best practices for documenting file I/O operations in Fortran
github: https://github.com/tugraskan/ford
src_dir: ./src
output_dir: ./doc
media_dir: ./data
page_dir: ./
exclude_dir: ./obj
             ./mod
preprocessor: gfortran -E
display: public
         protected
source: true
graph: true
search: true
macro: TEST
       LOGIC=.true.
extra_mods: iso_fortran_env:https://gcc.gnu.org/onlinedocs/gfortran/ISO_005fFORTRAN_005fENV.html
license: gpl
extra_filetypes: aqu !
                cnt !
project_github: https://github.com/tugraskan/ford
project_download: https://github.com/tugraskan/ford/releases
print_creation_date: true
creation_date: %Y-%m-%d %H:%M %z
md_extensions: markdown.extensions.toc
               markdown.extensions.smarty

---

# I/O Trace Example Documentation

This example demonstrates comprehensive documentation of file I/O operations in Fortran code.

## Files Documented

The example covers four files:

1. **aquifer.aqu** - Aquifer hydraulic properties (input)
2. **object.cnt** - Spatial object counts (input)
3. **mgt.out** - Management operations log (output)
4. **aquifer.out** - Aquifer water balance (output)

## Key Features

- **Filename Resolution**: Demonstrates how filenames are defined and potentially overridden
- **Unit Mappings**: Shows explicit unit-to-file associations
- **Read/Write Payloads**: Complete variable definitions for all I/O operations
- **Derived Types**: Full expansion of user-defined types with component documentation

## Documentation Approach

See [IO_TRACE_DOCUMENTATION.md](IO_TRACE_DOCUMENTATION.md) for the complete I/O trace analysis, which includes:

- Filename resolution chains
- I/O site locations with line numbers
- Variable definitions with types, defaults, units, and descriptions
- Worked example with detailed walkthrough

This example serves as a template for documenting I/O operations in scientific computing applications.
