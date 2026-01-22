# I/O Trace Analysis Feature

FORD now includes automatic I/O trace analysis capability that can analyze any Fortran codebase and generate comprehensive documentation of all file input/output operations.

## Overview

The I/O trace analyzer scans Fortran source code to identify and document:

1. **Filename Resolution** - How filenames are defined and potentially overridden
2. **I/O Operations** - All open, read, write, close, inquire operations
3. **Unit Mappings** - Associations between unit numbers and files
4. **Variable Definitions** - Complete metadata for all variables involved in I/O
5. **Derived Types** - Expansion of user-defined types with component details

## Usage

### Basic Usage

Generate I/O trace documentation for all files:

```bash
ford --io-trace project.md
```

This will create `IO_TRACE_REPORT.md` in the output directory.

### Filter by Target Files

Analyze only specific files:

```bash
ford --io-trace --io-trace-files aquifer.aqu object.cnt mgt.out aquifer.out project.md
```

### Custom Output Path

Specify a custom output location:

```bash
ford --io-trace --io-trace-output path/to/custom_report.md project.md
```

### Combined Example

```bash
ford --io-trace \
     --io-trace-files aquifer.aqu object.cnt mgt.out aquifer.out \
     --io-trace-output docs/IO_ANALYSIS.md \
     project.md
```

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--io-trace` | Enable I/O trace analysis | `False` |
| `--io-trace-files FILE [FILE ...]` | Specific files to analyze | All files |
| `--io-trace-output PATH` | Output report path | `IO_TRACE_REPORT.md` |

## Generated Report Structure

The generated markdown report contains four main sections:

### 1. Filename Resolution Map

Shows how each target filename is resolved:
- Variable expressions that hold the filename
- Type definitions
- Default values
- Potential runtime overrides
- Source locations (file:line format)

Example:
```
### 1.1 aquifer.aqu

**Target filename:** `aquifer.aqu`

**Resolution Chain**:
- Expression: `in_aqu%aqu`
- Type definition: `input_aqu` at src/input_file_module.f90:128-132
- Default value: `"aquifer.aqu"` set at src/input_file_module.f90:130
```

### 2. I/O Sites and Unit Mappings

Documents every I/O operation:
- Operation type (open, read, write, close, etc.)
- Unit number associations
- File expressions
- Source locations
- Full statement text

Example:
```
**OPEN** — `src/aquifer_module.f90:32`
- Unit: 107
- File: `in_aqu%aqu`
```fortran
open(unit=107, file=in_aqu%aqu, status='old', action='read')
```
```

### 3. Variable Definitions

Table of all variables involved in I/O operations:
- Variable name
- Type (integer, real, character, derived type, etc.)
- Scope (local, module, dummy argument, component)
- Default values
- Description from comments

### 4. Derived Type Definitions

Detailed expansion of user-defined types:
- Type name and definition location
- All components in declaration order
- Component types, defaults, and descriptions
- Notes on user-defined I/O if present

## Integration with Existing FORD Workflow

The I/O trace analysis integrates seamlessly with FORD:

1. It runs after source code parsing is complete
2. It uses FORD's existing AST (Abstract Syntax Tree) for variable and type information
3. It generates documentation alongside regular FORD output
4. It can be enabled/disabled without affecting normal FORD operation

## Use Cases

### Scientific Computing

Document data flow in simulation models:
- Track input parameter files
- Monitor output data files
- Verify unit number assignments

### Code Review

Facilitate code review by documenting:
- All file dependencies
- I/O operation patterns
- Variable usage in file operations

### Legacy Code Understanding

Help understand legacy Fortran codebases:
- Map file I/O operations
- Trace filename variables
- Document derived type usage

### Quality Assurance

Ensure code quality:
- Verify proper file handling
- Check for resource leaks
- Document I/O error handling

## Example Output

For a real-world example, see the SWAT+ model analysis mentioned in the GitHub issue, which shows:
- Complete filename resolution chains
- Unit-to-file mappings
- Detailed variable definitions with units and descriptions
- Derived type expansions for hydraulic parameters

## Technical Details

### Implementation

The I/O trace analyzer (`ford/io_trace.py`) provides:

- **IOTraceAnalyzer class**: Main analysis engine
- **FileReference dataclass**: File reference tracking
- **IOOperation dataclass**: I/O operation representation
- **VariableDefinition dataclass**: Variable metadata
- **DerivedTypeDefinition dataclass**: Type metadata

### Analysis Process

1. **Scan Phase**: Identify file references and I/O operations using regex patterns
2. **Collection Phase**: Extract variable and type definitions from FORD's AST
3. **Mapping Phase**: Build unit-to-file associations
4. **Filter Phase**: Apply target file filters if specified
5. **Generation Phase**: Create structured markdown documentation

### Pattern Matching

The analyzer recognizes:
- String literals: `'aquifer.aqu'`, `"object.cnt"`
- Variable assignments: `filename = "data.txt"`
- I/O statements: `open()`, `read()`, `write()`, `close()`, `inquire()`
- Unit numbers: Both positional and keyword forms

## Limitations

Current version limitations:
- Requires files to have standard Fortran extensions (.f90, .f, etc.)
- Runtime filename assignments may not be fully traced
- Computed/concatenated filenames may not be resolved
- Focus on standard Fortran I/O (not C interop or stream I/O)

## Future Enhancements

Potential improvements:
- Data flow analysis for runtime filename resolution
- Control flow analysis for conditional I/O
- Cross-module filename tracing
- I/O performance metrics
- Graphical I/O diagrams

## Contributing

To extend or improve I/O trace analysis:

1. Modify `ford/io_trace.py` for analysis enhancements
2. Update pattern matching in `_scan_file_references()` and `_scan_io_operations()`
3. Enhance documentation generation in `generate_io_trace_markdown()`
4. Add tests for new functionality

## License

This feature is part of FORD and is licensed under the GNU General Public License v3.0.
