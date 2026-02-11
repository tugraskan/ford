# SWAT+ Input File Issue Example

This directory contains examples demonstrating the common mistake of pointing FORD at data files instead of source code.

## Files

- `broken_config.md` - Original configuration that doesn't work (points at TxtInOut data directory)
- `working_config.md` - Fixed configuration that works (points at src directory)
- `sample_data.txt` - Example of what's in TxtInOut directory (not Fortran code)
- `sample_source.f90` - Example of actual Fortran source code that FORD should process

## The Problem

Users often try to run:
```bash
ford broken_config.md
```

This fails because `src_dir: ./TxtInOut` points to model data files, not Fortran source code.

## The Solution

Run this instead:
```bash
ford working_config.md
```

This works because `src_dir: ./src` points to actual Fortran `.f90` files.

## Key Differences

| broken_config.md | working_config.md |
|------------------|-------------------|
| `src_dir: ./TxtInOut` | `src_dir: ./src` |
| Points at data files | Points at Fortran code |
| Missing extensions | Specifies `.f90` files |
| No exclude rules | Excludes data directories |

## See Also

- [Troubleshooting Input Files](../../troubleshooting_input_files.md)
- [SWAT+ Documentation Guide](../../user_guide/swatplus_documentation_guide.md)
