# New Columns Enhancement Documentation

## Added Columns

The Improved Modular Database has been enhanced with two new columns as requested:

### 1. Source_Module
**Column Position**: 20  
**Description**: Specifies what module the read-in type comes from

**Module Mapping Logic**:
- `basin_module` - Parameters from basin-related procedures
- `gwflow_module` - Parameters from groundwater flow procedures  
- `climate_module` - Parameters from climate-related procedures
- `channel_module` - Parameters from channel-related procedures
- `reservoir_module` - Parameters from reservoir-related procedures
- `hru_module` - Parameters from HRU-related procedures
- `aquifer_module` - Parameters from aquifer-related procedures
- `plant_module` - Parameters from plant-related procedures
- `soil_module` - Parameters from soil-related procedures
- `salt_module` - Parameters from salt-related procedures
- `time_module` - Parameters from time-related procedures
- `input_file_module` - Parameters from file.cio and input file reading
- `output_module` - Parameters from output procedures
- `simulation_module` - Parameters from simulation control procedures
- `unknown_module` - Default when module cannot be determined

**Examples**:
- `time%day_start` → `time_module`
- `pco%nyskip` → `basin_module`
- `num_tile_cells` → `gwflow_module`
- `titldum` → `input_file_module`

### 2. Is_Local_Variable
**Column Position**: 21  
**Description**: Y/N flag indicating if the parameter is a local variable

**Local Variable Detection Logic**:
- **Y (Yes - Local Variable)**:
  - Common local variables: `titldum`, `header`, `name`, `dum`, `dum1`, `dum2`, etc.
  - Temporary variables: `i`, `j`, `k`, `ii`, `jj`, `kk`, `eof`, `iostat`
  - Variables containing patterns: `dum`, `temp`, `tmp`
  - Simple variable names (≤4 characters) except meaningful ones like `area`, `lat`, `lon`

- **N (No - Not Local Variable)**:
  - Structured variables with `%` (e.g., `time%day_start`, `pco%nyskip`)
  - Array variables with `()` notation
  - Meaningful parameter names representing actual data

**Examples**:
- `titldum` → `y` (header/title dummy variable)
- `hru_dum` → `y` (dummy variable)
- `time%day_start` → `n` (structured parameter)
- `pco%nyskip` → `n` (meaningful parameter)
- `area` → `n` (meaningful parameter)

## Enhanced Header and Title Tracking

The new columns improve tracking of headers and titles in SWAT files by:

1. **Module Attribution**: Each header/title is now attributed to its source module
2. **Local Variable Classification**: Headers like `titldum`, `header`, `name` are properly flagged as local variables
3. **Complete Traceability**: Users can now trace where each parameter originates and whether it's a local variable or actual data parameter

## Database Structure

The complete fieldnames are now:
```python
fieldnames = [
    'Unique_ID', 'Broad_Classification', 'SWAT_File', 'database_table',
    'DATABASE_FIELD_NAME', 'SWAT_Header_Name', 'Text_File_Structure',
    'Position_in_File', 'Line_in_file', 'Swat_code_type',
    'SWAT_Code_Variable_Name', 'Description', 'Core', 'Units',
    'Data_Type', 'Minimum_Range', 'Maximum_Range', 'Default_Value', 'Use_in_DB',
    'Source_Module', 'Is_Local_Variable'  # New columns
]
```

This enhancement provides users with better understanding of parameter origins and classification, making it easier to identify which parameters are actual data vs. local variables or headers.