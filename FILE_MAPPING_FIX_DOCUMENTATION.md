# File Mapping Fix Documentation

## Issue Identified

The user correctly identified that **codes.bsn** and **weather-sta.cli** entries were wrong in the modular database. Investigation revealed that the file-to-procedure matching logic was fundamentally flawed.

## Root Cause Analysis

### Problem 1: Crude String Matching
The original `_find_matching_procedures` method used crude substring matching:

```python
# WRONG: Too broad substring matching
if filename.lower() in procedure_name.lower() or base_name.lower() in procedure_name.lower():
    matches.append(procedure_name)
```

This caused:
- **codes.bsn** to match both `basin_print_codes_read.io` (contains "codes") AND `calsoft_read_codes.io` (contains "codes")
- **weather-sta.cli** to match `cli_read_atmodep.io` (contains "cli") instead of the correct `cli_staread.io`

### Problem 2: Cross-File Context Contamination
Procedures often read multiple files, but the logic included ALL parameters from a procedure regardless of which file they came from:

**Example: `basin_read_cc.io.json`**
```json
{
  "in_basin%codes_bas": { /* codes.bsn parameters */ },
  "pet.cli": { /* pet.cli parameters */ }
}
```

The old logic would assign BOTH `codes.bsn` parameters AND `pet.cli` parameters to `codes.bsn` file.

## Solution Implemented

### Fix 1: Context-Based Procedure Matching
Replaced crude string matching with proper file context correlation:

```python
def _find_matching_procedures(self, filename: str) -> List[str]:
    # Find the input_file_module mapping for this filename
    # e.g., codes.bsn -> in_basin%codes_bas
    target_file_var = None
    target_var_name = None
    
    for file_var, var_files in self.input_file_module.items():
        for var_name, mapped_filename in var_files.items():
            if mapped_filename == filename:
                target_file_var = file_var    # e.g., "in_basin"
                target_var_name = var_name    # e.g., "codes_bas"
                break
    
    # Find procedures that read the correct file context
    for procedure_name, procedure_data in self.io_files.items():
        for param in procedure_data['parameters']:
            file_context = param.get('file_context', '')
            if file_context.startswith(f"{target_file_var}%"):
                context_var = file_context.split('%')[1]
                if context_var == target_var_name:  # e.g., "codes_bas"
                    matches.append(procedure_name)
```

### Fix 2: File Context Filtering
Enhanced `_process_input_file` to only include parameters from the correct file context:

```python
def _process_input_file(self, filename: str, classification: str, file_var: str):
    for param in parameters:
        file_context = param.get('file_context', '')
        
        # Only include parameters from the correct file context
        if target_var_name and file_context.startswith(f"{file_var}%"):
            context_var = file_context.split('%')[1]
            if context_var != target_var_name:
                continue  # Skip parameters from other file contexts
```

## Results

### Dramatic Improvement
- **Before**: 6,848 parameters (with incorrect cross-contamination)
- **After**: 834 parameters (clean, correct mappings)

### Specific Fixes

**codes.bsn - BEFORE (292 entries - WRONG):**
```csv
codes.bsn,...,titldum header from in_chg%codes_sft via calsoft_read_codes
codes.bsn,...,titldum header from in_sim%prt via basin_print_codes_read
codes.bsn,...,pco%nyskip parameter from in_sim%prt via basin_print_codes_read
```

**codes.bsn - AFTER (3 entries - CORRECT):**
```csv
codes.bsn,...,titldum header from in_basin%codes_bas via basin_read_cc
codes.bsn,...,header header from in_basin%codes_bas via basin_read_cc  
codes.bsn,...,bsn_cc header from in_basin%codes_bas via basin_read_cc
```

**weather-sta.cli - BEFORE (178 entries - WRONG):**
```csv
weather-sta.cli,...,atmodep_cont%num_sta parameter from in_cli%atmo_cli via cli_read_atmodep
```

**weather-sta.cli - AFTER (4 entries - CORRECT):**
```csv
weather-sta.cli,...,titldum header from in_cli%weat_sta via cli_staread
weather-sta.cli,...,header header from in_cli%weat_sta via cli_staread
weather-sta.cli,...,wst%name parameter from in_cli%weat_sta via cli_staread
weather-sta.cli,...,wst%wco_c parameter from in_cli%weat_sta via cli_staread
```

## Technical Architecture

### Proper Flow
1. **Input File Module**: Defines `in_basin%codes_bas = "codes.bsn"`
2. **I/O Analysis**: Finds procedure `basin_read_cc.io` reading `in_basin%codes_bas`
3. **Parameter Extraction**: Only extracts parameters with `file_context = "in_basin%codes_bas"`
4. **Database Entry**: Creates entries for `codes.bsn` with correct parameters

### Key Insights
- **File Context is King**: The `file_context` field in I/O analysis is the authoritative source
- **Input File Module Mapping**: Provides the ground truth for filename → file variable mapping
- **Procedure Isolation**: Parameters from different file contexts within the same procedure must be kept separate

## Impact

This fix eliminates the massive over-counting and cross-contamination issues, providing users with:

- **Accurate Parameter Counts**: Each file shows only its actual parameters
- **Correct Procedure Attribution**: Parameters traced to the right I/O procedures
- **Clean Database**: No more duplicate or misattributed entries
- **Proper File Structure**: Each SWAT+ input file shows its true structure

The database now accurately reflects the actual SWAT+ input file ecosystem without artificial inflation from incorrect mappings.