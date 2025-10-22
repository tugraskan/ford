# Test Data Source Code

This directory contains Fortran source files used for testing FORD's ability to process large codebases.

## Usage

To generate documentation for this code using FORD:

```bash
cd test_data/src
ford doc.md
```

The documentation will be generated in the `doc/` directory.

## Testing

A test is provided in `test/test_projects/test_src.py` that verifies FORD can successfully process this codebase and generate documentation.

To run the test:

```bash
pytest test/test_projects/test_src.py
```

## Files

- `doc.md`: FORD project configuration file
- `*.f90`: Fortran 90 source files (646 files total)
- `doc/`: Generated documentation directory (git-ignored)
