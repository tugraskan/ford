# Pure I/O Pattern-Based Classification

## Overview

The file classification system now uses **pure I/O pattern analysis** without relying on filename keywords or extensions. Files are classified based on how Fortran code actually accesses them.

## Classification Logic

### 🔵 Connect Files
**Pattern**: Looped reads with repeating structure

```fortran
! Example: Connection file linking HRUs to channels
DO i = 1, nhru
  READ(10,*) hru_id, channel_id, aquifer_id  ! Same 3 columns repeated
END DO
```

**Detection**:
- ✓ >60% of reads are inside loops (`condition` or `condition_stack` present)
- ✓ At least 3 read operations
- ✓ Consistent parameter structure (same number of columns per read)

**Why Connect**: Rows repeat with the same columns in a loop pattern - linking/connecting data.

---

### 🟢 Simple Files
**Pattern**: Sequential reads with consistent structure

```fortran
! Example: Weather data file
READ(10,*) header
DO i = 1, ndays
  READ(10,*) date, temp, precip  ! Same 3 columns every time
END DO
```

**Detection**:
- ✓ Sequential access (no REWIND/BACKSPACE)
- ✓ Consistent parameter structure
- ✓ <60% looped reads (or simple sequential pattern)

**Why Simple**: Flat tabular data with consistent rows.

---

### 🟡 Unique Files
**Pattern**: Variable structure or complex access

```fortran
! Example 1: Variable structure (different columns per row)
READ(10,*) version              ! 1 column
READ(10,*) date, author, desc   ! 3 columns
READ(10,*) setting1, setting2   ! 2 columns

! Example 2: Probe reads (testing file structure)
READ(10,*) test_value
REWIND(10)  ! Go back to beginning
READ(10,*) actual_data

! Example 3: Complex positioning
READ(10,*) config
BACKSPACE(10)  ! Go back one record
READ(10,*) modified_config
```

**Detection**:
- ✓ Has probe reads (marked with `is_probe_read`)
- ✓ Uses REWIND/BACKSPACE (complex positioning)
- ✓ Variable parameter structure (different columns per read)
- ✓ Few operations with complex positioning (<10 ops)

**Why Unique**: Non-standard structure, configuration files, or complex access patterns.

---

## What Changed

### Before (Filename-Based) ❌
```python
if any(ext in filename for ext in ['.con', '.lin']):
    return "Connect"

if any(ext in filename for ext in ['.cli', '.bsn', '.hru']):
    return "Simple"
```

### After (I/O Pattern-Based) ✅
```python
# Analyze actual I/O operations
looped_reads = [op for op in read_ops if op.get("condition")]
loop_ratio = len(looped_reads) / len(read_ops)

if loop_ratio > 0.6 and has_consistent_structure(params):
    return "Connect"  # Repeating pattern in loops

if is_sequential and has_consistent_structure(params):
    return "Simple"   # Flat tabular data
```

---

## Key Benefits

### 1. **No Hardcoding**
- Works with **any filename** or extension
- Classification based on actual code behavior

### 2. **Accurate**
- Detects repeating patterns from loop analysis
- Identifies variable structure from parameter variance
- Recognizes complex access from REWIND/BACKSPACE

### 3. **Uses FORD's I/O Tracking**
- `condition` / `condition_stack` → Loop detection
- `parameters` → Column structure analysis
- `is_probe_read` → Test read detection
- `kind` (rewind/backspace) → Complex positioning

---

## Examples

### Example 1: Connect File Detection

**Fortran Code**:
```fortran
OPEN(20, FILE='connections.dat')
DO i = 1, nconnections
  READ(20,*) from_id, to_id, weight
END DO
CLOSE(20)
```

**I/O Analysis**:
- 100% of reads in loop ✓
- Consistent 3-parameter structure ✓
- **Result**: **Connect** 🔵

---

### Example 2: Simple File Detection

**Fortran Code**:
```fortran
OPEN(10, FILE='weather.dat')
READ(10,*) header
DO day = 1, 365
  READ(10,*) date, temperature, rainfall
END DO
CLOSE(10)
```

**I/O Analysis**:
- Sequential access ✓
- Consistent 3-parameter structure ✓
- ~99% looped but simple sequential pattern ✓
- **Result**: **Simple** 🟢

---

### Example 3: Unique File Detection

**Fortran Code**:
```fortran
OPEN(30, FILE='config.dat')
READ(30,*) version
READ(30,*) project_name, start_year, end_year
READ(30,*) option_flag
REWIND(30)
READ(30,*) all_settings
CLOSE(30)
```

**I/O Analysis**:
- Variable structure (1, 3, 1, 1 parameters) ✓
- Uses REWIND ✓
- **Result**: **Unique** 🟡

---

## Technical Implementation

### Data Available from FORD

Each I/O operation has:
```python
{
    "kind": "read",                    # read/write/rewind/backspace
    "raw": "READ(10,*) hru_id, ...",  # Original Fortran line
    "parameters": ["hru_id", "..."],   # Variables read/written
    "condition": "i",                  # Loop variable if in loop
    "condition_stack": ["DO i=1,n"],   # Full loop context
    "is_probe_read": False,            # Test read?
    "file_line": 5                     # Sequential line number
}
```

### Classification Algorithm

```python
1. Count looped vs non-looped reads
2. Analyze parameter consistency
3. Check for complex positioning (REWIND/BACKSPACE)
4. Classify based on patterns:
   
   IF >60% looped + consistent structure:
     → Connect (repeating pattern)
   
   ELSE IF has probe reads OR variable structure OR complex positioning:
     → Unique (non-standard)
   
   ELSE IF sequential + consistent structure:
     → Simple (flat tabular)
   
   ELSE:
     → Unknown
```

---

## Migration Notes

### Old Behavior
- Relied on `.con`, `.cli`, `.bsn` extensions
- Hardcoded filename keywords
- Couldn't classify renamed files

### New Behavior
- Works with **any filename**
- Based on **actual I/O behavior**
- More accurate classification
- Handles edge cases better

### Compatibility
- HTML templates unchanged
- Same classification types (Simple/Unique/Connect)
- Classification appears in same locations
- More files may be classified as "Unknown" initially until FORD has enough I/O data

---

## Summary

✅ **No filename keywords** - Pure pattern analysis  
✅ **Uses FORD's I/O tracking** - Loop context, parameters, positioning  
✅ **Accurate classification** - Based on actual code behavior  
✅ **Handles edge cases** - Probe reads, variable structure, complex positioning  

The system now truly understands how files are used, not just what they're named! 🎉
