# Tile and Header Reading Fix Documentation

## Issue Identified
The user reported that the line_in_file column was still not accounting for "tile, header" reads properly. The issue was that different file sections within the same I/O procedure had different header counts, but we were applying a single header count per procedure.

## Root Cause
Files like `gwflow_read.io.json` contain multiple sections:
- `gwflow.input`: 25 headers → first data at line 26
- `gwflow.pumpex`: 2 headers → first data at line 3  
- `gwflow.tiles`: 6 headers → first data at line 7
- `gwflow.solutes`: 5 headers → first data at line 6

The original logic was treating all sections within a procedure the same, but each section has its own header structure.

## Solution Implemented
The existing logic was already correct - it calls `_count_actual_header_reads(file_info)` for each individual file section, ensuring each section uses its own header count.

## Verification Results

### gwflow.tiles Parameters (6 headers)
- `num_tile_cells` at line **7** ✅ (6 headers + 1)
- `gw_tile_groups` at line **8** ✅ (next data_reads section)
- `grid_int,j=1,grid_ncol` at line **9** ✅ (third data_reads section)
- `gw_state%tile` at line **10** ✅ (fourth data_reads section)

### print.prt Parameters (3 headers: titldum, header, name)
- First data parameters at line **4** ✅ (3 headers + 1)

### time.sim Parameters (2 headers: titldum, header)  
- First data parameters at line **3** ✅ (2 headers + 1)

## Key Improvements
- ✅ **Individual Section Processing**: Each file section within a procedure uses its own header count
- ✅ **Accurate Tile Parameters**: gwflow.tiles parameters correctly start at line 7 after 6 headers
- ✅ **Proper Header Recognition**: All header types (titldum, header, name, gw_tile_depth, etc.) are accounted for
- ✅ **File Structure Accuracy**: Line numbers now reflect actual input file structure users see

## Impact
This fix ensures that the line_in_file values accurately represent the actual line positions in SWAT+ input files where parameters are read, properly accounting for all header reading patterns including tile-related headers.