# How It Works - Simple Explanation

## The Problem

You have lots of input files with different purposes. We want the computer to figure out what type of file it is by **looking at how the Fortran code actually uses it** - no filename guessing!

## The Solution - Pure I/O Pattern Analysis ⭐

The classifier analyzes **actual Fortran I/O operations** from FORD's code analysis:

### 1. **Simple Files** (Flat tabular data) 🟢
**Pattern**: Sequential reads with the same columns every time

```fortran
! Weather data - same 3 columns repeated
DO day = 1, 365
  READ(10,*) date, temp, rainfall  ! Consistent structure
END DO
```

**Detection**: Sequential access + consistent columns + mostly non-looped
**Example**: Weather data, parameter tables

---

### 2. **Connect Files** (Repeating link patterns) 🔵  
**Pattern**: Looped reads where same columns repeat

```fortran
! Linking HRUs to channels - pattern repeats in loop
DO i = 1, nhru
  READ(20,*) hru_id, channel_id, aquifer_id  ! Same 3 every iteration
END DO
```

**Detection**: >60% reads in loops + consistent structure
**Example**: Connection tables, linkage files

---

### 3. **Unique Files** (Variable/complex structure) 🟡
**Pattern**: Different columns per row OR complex positioning

```fortran
! Config file - different structure per line
READ(30,*) version              ! 1 column
READ(30,*) name, year, author   ! 3 columns
READ(30,*) option1, option2     ! 2 columns

! Or: Testing file with REWIND
READ(30,*) test_value
REWIND(30)  ! Go back
READ(30,*) actual_data
```

**Detection**: Variable columns OR REWIND/BACKSPACE usage OR probe reads
**Example**: Config files, master settings

---

## How Classification Works

### NO Filename Checking! ❌
```python
# OLD WAY (removed):
if filename.endswith('.con'):
    return "Connect"
```

### YES I/O Pattern Analysis! ✅
```python
# NEW WAY:
loop_ratio = looped_reads / total_reads

if loop_ratio > 0.6 and consistent_columns:
    return "Connect"  # Repeating pattern
```

## What FORD Tracks

For each READ/WRITE operation:
- **Loop context**: Is it inside a DO loop?
- **Parameters**: What variables are read? (columns)
- **Positioning**: REWIND? BACKSPACE?
- **Pattern**: Probe read (test then rewind)?

**Example**:
```fortran
DO i = 1, 100
  READ(10,*) id, value, status
END DO
```

FORD tracks:
- ✓ In loop (condition = "i")
- ✓ 3 parameters per read
- ✓ Sequential (no REWIND)
- ✓ Pattern repeats 100 times
- → **Classification: Connect!**

## Why This is Better

❌ **Old approach**: "If filename has .con → Connect"  
✅ **New approach**: "If reads repeat in loops → Connect"

**Benefits**:
- Works with **any filename**
- Based on **actual code behavior**
- More **accurate**
- Handles renamed files

**No guessing!** 🎉

---

**See also:**
- [IO_PATTERN_CLASSIFICATION.md](IO_PATTERN_CLASSIFICATION.md) - Technical details
- [SIMPLE_GUIDE.md](SIMPLE_GUIDE.md) - Basic usage guide
- [HTML_CLASSIFICATION.md](HTML_CLASSIFICATION.md) - How it appears in FORD HTML
