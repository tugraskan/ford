# HTML Classification Display

## What You'll See in FORD's Generated HTML

When FORD generates documentation, each I/O file now has a **classification badge** based on how the Fortran code accesses it.

### On Individual File Pages

```
┌─────────────────────────────────────────┐
│  hru.con - I/O File                     │
├─────────────────────────────────────────┤
│  Unit Number: 101                       │
│  I/O Type: Input                        │
│  Classification: [Connect]              │ ← NEW!
│                  Component linkage      │
│  Total Operations: 15                   │
└─────────────────────────────────────────┘
```

### On the I/O Files List Page

```
Input Files (12)
────────────────────────────────────────────────────────────
Filename         Unit    Classification    Used By
────────────────────────────────────────────────────────────
weather.cli      10      [Simple]         3 procedure(s)
hru.con          20      [Connect]        2 procedure(s)
file.cio         30      [Unique]         1 procedure(s)
────────────────────────────────────────────────────────────
```

## Color Coding

- 🟢 **[Simple]** (Green) = Tabular data files
- 🔵 **[Connect]** (Blue) = Files that link components
- 🟡 **[Unique]** (Yellow) = Master configuration files
- ⚫ **[Unknown]** (Gray) = Unclassified files

## How It Works

The classification is based on **actual I/O patterns** that FORD detects in your Fortran code:

### Example 1: Simple File
```fortran
! Sequential reads = Simple classification
OPEN(10, FILE='weather.cli')
READ(10,*) header
DO i = 1, ndays
  READ(10,*) date, temp, precip
END DO
CLOSE(10)
```
**Result**: `weather.cli` → **Simple** (sequential reads)

### Example 2: Connect File  
```fortran
! Links HRUs to channels = Connect classification
OPEN(20, FILE='hru.con')
DO i = 1, nhru
  READ(20,*) hru_id, channel_id, aquifer_id
END DO
```
**Result**: `hru.con` → **Connect** (filename + linkage pattern)

### Example 3: Unique File
```fortran
! Master config with REWIND = Unique classification
OPEN(30, FILE='file.cio')
READ(30,*) version
REWIND(30)  ! ← Complex positioning
READ(30,*) project_settings
```
**Result**: `file.cio` → **Unique** (config file + complex I/O)

## Benefits

✅ **Automatic** - No manual tagging needed  
✅ **Accurate** - Based on actual code analysis  
✅ **Visual** - Easy to spot file types at a glance  
✅ **Integrated** - Works with FORD's existing I/O tracking

## Technical Details

The classification uses FORD's IoSession tracking which monitors:
- READ/WRITE operations
- REWIND/BACKSPACE usage
- File positioning patterns
- Sequential vs random access

This is much more sophisticated than just looking at filenames!
