# Sample Input Data Files

This directory contains example input files that demonstrate the format expected by the I/O routines.

## aquifer.aqu

Format:
```
Header line (description)
Number of aquifers
For each aquifer: index  name  area  K  Sy  alpha  storage_init  storage_min  storage_max
```

Fields:
- **index**: Aquifer record number
- **name**: Aquifer identifier (up to 16 characters)
- **area**: Surface area [ha]
- **K**: Hydraulic conductivity [m/day]
- **Sy**: Specific yield (dimensionless, 0-1)
- **alpha**: Baseflow recession coefficient [1/day]
- **storage_init**: Initial water storage [m³]
- **storage_min**: Minimum storage threshold [m³]
- **storage_max**: Maximum storage capacity [m³]

## object.cnt

Format:
```
Header line
Number of subbasins
Number of HRUs
Number of aquifers
Number of channels
Number of reservoirs
Number of point sources
```

All counts are integers representing the number of spatial objects in each category.

## Output Files

The output files (mgt.out and aquifer.out) are created by the program and should not be provided as input. They will be generated in the working directory when the output routines are called.
