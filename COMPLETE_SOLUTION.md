# Complete File Classification Solution

## Overview

We've implemented **TWO complementary classification methods** that work together:

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Method 1: Standalone Classifier (CLI/API)                 │
│  ────────────────────────────────────────                  │
│  • Analyzes file structure directly                        │
│  • Works with any files                                    │
│  • Command line: python -m ford.classify_files             │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Method 2: FORD HTML Integration ⭐ NEW!                   │
│  ────────────────────────────────────                      │
│  • Analyzes Fortran I/O patterns                           │
│  • Uses REWIND/BACKSPACE detection                         │
│  • Automatic in FORD-generated HTML                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Method 1: Standalone Classifier

### What It Does
Reads any file and analyzes its structure.

### How to Use
```bash
# Classify files
python -m ford.classify_files weather.cli hru.con file.cio

# Output
File          Classification
-----------   --------------
weather.cli   Simple         (tabular structure)
hru.con       Connect        (.con extension)
file.cio      Unique         (master config)
```

### Classification Logic
- **Simple**: Consistent columns, tabular data
- **Connect**: .con/.lin extensions, connection keywords
- **Unique**: Config extensions, mixed structure

---

## Method 2: FORD HTML Integration ⭐

### What It Does
When FORD analyzes Fortran code, it tracks I/O operations and classifies files based on **how they're actually accessed**.

### What You See

#### On File List Page:
```
Input Files (3)
─────────────────────────────────────────────────────────
Filename       Unit    Classification       Used By
─────────────────────────────────────────────────────────
weather.cli    10      [Simple] 🟢         3 procedures
hru.con        20      [Connect] 🔵        2 procedures  
file.cio       30      [Unique] 🟡         1 procedure
─────────────────────────────────────────────────────────
```

#### On Individual File Page:
```
┌────────────────────────────────────┐
│  weather.cli - I/O File            │
├────────────────────────────────────┤
│  Unit Number: 10                   │
│  I/O Type: Input                   │
│  Classification: [Simple] 🟢       │
│                  Tabular data file │
│  Total Operations: 45              │
└────────────────────────────────────┘
```

### Classification Logic (I/O Based)

#### Simple Files
```fortran
! Sequential READ operations
OPEN(10, FILE='weather.cli')
DO i = 1, ndays
  READ(10,*) date, temp, precip  ! ← Sequential
END DO
```
**Pattern**: Pure sequential I/O → **Simple**

#### Connect Files
```fortran
! Links components together
OPEN(20, FILE='hru.con')
DO i = 1, nhru
  READ(20,*) hru_id, channel_id  ! ← Linkage data
END DO
```
**Pattern**: .con filename + linkage → **Connect**

#### Unique Files
```fortran
! Complex positioning
OPEN(30, FILE='file.cio')
READ(30,*) version
REWIND(30)  ! ← Complex I/O positioning
READ(30,*) settings
```
**Pattern**: REWIND/BACKSPACE usage → **Unique**

---

## Key Differences

| Aspect | Method 1: Standalone | Method 2: FORD HTML |
|--------|---------------------|---------------------|
| **Input** | Any file | Fortran code analysis |
| **Analysis** | File structure | I/O operations |
| **Detects** | Columns, patterns | REWIND, BACKSPACE |
| **Output** | CLI/CSV/JSON | HTML badges |
| **Use Case** | Quick file sorting | Code documentation |

---

## Why Both Methods?

### Standalone Classifier
- ✅ Works on **any files** (not just Fortran)
- ✅ **Quick analysis** without running FORD
- ✅ **Batch processing** with CSV export
- ✅ Can classify files that aren't in code yet

### FORD HTML Integration  
- ✅ Based on **actual code behavior**
- ✅ Detects **complex I/O patterns** (REWIND/BACKSPACE)
- ✅ **Automatic** - no manual classification needed
- ✅ **Visual** - color-coded in documentation
- ✅ More **accurate** for Fortran projects

### Together They Provide
1. **Fast classification** for any files (Method 1)
2. **Deep analysis** based on actual usage (Method 2)
3. **Visual documentation** in HTML (Method 2)
4. **No hardcoding** in either method!

---

## Example: Complete Workflow

### Step 1: Quick Classification (Standalone)
```bash
# Classify files in a directory
python -m ford.classify_files swat_inputs/*.cli

File              Classification
---------------   --------------
weather.cli       Simple
pcp.cli           Simple
tmp.cli           Simple
```

### Step 2: Run FORD Documentation
```bash
ford project.md
```

### Step 3: View HTML Documentation
Open `docs/lists/iofiles.html` and see:

```
Input Files (15)
─────────────────────────────────────────────────────────
Filename       Classification       Actual I/O Pattern
─────────────────────────────────────────────────────────
weather.cli    [Simple] 🟢         Sequential reads
hru.con        [Connect] 🔵        Component linkage
file.cio       [Unique] 🟡         Uses REWIND
parameters.bsn [Simple] 🟢         Sequential reads
─────────────────────────────────────────────────────────
```

**Notice**: Both methods agree! ✓

---

## Summary

✅ **Dual approach** - Structure AND I/O pattern analysis  
✅ **No hardcoding** - Both methods analyze automatically  
✅ **FORD integrated** - Classification in HTML documentation  
✅ **Visual feedback** - Color-coded badges  
✅ **Production ready** - Tested and documented  

**The best of both worlds!** 🎉

---

## Quick Links

- 📖 [HOW_IT_WORKS.md](HOW_IT_WORKS.md) - Simple explanation
- 📖 [SIMPLE_GUIDE.md](SIMPLE_GUIDE.md) - Quick start
- 📖 [HTML_CLASSIFICATION.md](HTML_CLASSIFICATION.md) - HTML display details
- 📖 [FILE_CLASSIFICATION.md](FILE_CLASSIFICATION.md) - Full technical docs
- 💻 [example_classification.py](example_classification.py) - Working demo
