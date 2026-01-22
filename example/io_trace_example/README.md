# I/O Trace Example for FORD

This directory contains a complete example demonstrating FORD's capability to document Fortran I/O operations in detail.

## Overview

This example includes:

1. **Fortran Source Code** (`src/` directory): A set of modules simulating a hydrological model with file I/O operations
2. **I/O Trace Documentation** (`IO_TRACE_DOCUMENTATION.md`): Comprehensive documentation analyzing all I/O operations

## Files Included

### Source Code Modules

- **input_file_module.f90**: Defines input file names and paths
- **aquifer_database.f90**: Defines aquifer data structures
- **aquifer_module.f90**: Contains `aqu_read` subroutine for reading aquifer data
- **object_module.f90**: Contains `object_cnt_read` for reading object counts
- **output_module.f90**: Contains output writing routines for management and aquifer data

### Target I/O Files

The example demonstrates I/O operations on four files:

1. **aquifer.aqu** (input): Aquifer hydraulic properties
2. **object.cnt** (input): Spatial object counts
3. **mgt.out** (output): Management operations log
4. **aquifer.out** (output): Aquifer water balance output

## Documentation Features

The `IO_TRACE_DOCUMENTATION.md` file demonstrates:

- **Filename Resolution Map**: Traces how filename variables are defined and potentially overridden
- **I/O Sites and Unit Mappings**: Documents all file operations and unit number associations
- **Read/Write Payload Map**: Complete analysis of all read/write operations with variable definitions
- **Worked Example**: Detailed walkthrough of the `aqu_read` subroutine

## Location Format

All source code locations use the consistent format:
- Single line: `relative/path/to/file.f90:123`
- Range: `relative/path/to/file.f90:123-145`

## Purpose

This example serves as:

1. A template for documenting I/O operations in Fortran codes
2. A demonstration of FORD's documentation capabilities
3. A reference for understanding file I/O patterns in scientific computing applications

## Usage

To view the full I/O trace analysis, see [IO_TRACE_DOCUMENTATION.md](IO_TRACE_DOCUMENTATION.md).

To build and run the example:

```bash
# Build the program
make

# Run the demonstration
make run

# Clean up build artifacts
make clean
```

The demonstration program will:
1. Read aquifer parameters from `data/aquifer.aqu`
2. Read object counts from `data/object.cnt`
3. Create and write to `mgt.out` (management operations)
4. Create and write to `aquifer.out` (aquifer water balance)

The source code can be compiled and used as a starting point for similar I/O documentation tasks in other Fortran projects.
