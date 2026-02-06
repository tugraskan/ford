# How It Works - Simple Explanation

## The Problem

You have lots of input files with different purposes. Instead of writing code for each filename (hardcoding), we want the computer to figure out what type of file it is by **looking at how it's actually used**.

## The Solution - Two Ways!

### 1. **Standalone Classifier** (For any files)
Reads a file and checks its structure:
- Rows and columns? → **Simple**
- Links components? → **Connect**  
- Master config? → **Unique**

### 2. **FORD HTML Integration** (For Fortran I/O files) ⭐ NEW!
Analyzes how your Fortran code accesses the file:
- Sequential READ/WRITE? → **Simple**
- Connects things (`.con` file)? → **Connect**
- Uses REWIND/BACKSPACE? → **Unique**

## What You See in FORD's HTML

When FORD generates documentation, each I/O file gets a **colored badge**:

```
I/O Files List
─────────────────────────────────────────────
Filename         Classification    
─────────────────────────────────────────────
weather.cli      [Simple] 🟢       Tabular data
hru.con          [Connect] 🔵      Links components  
file.cio         [Unique] 🟡       Master config
─────────────────────────────────────────────
```

## How Classification Works

### For Standalone Files:
Looks at the file content structure (columns, patterns)

### For FORD I/O Files:
Looks at **actual Fortran I/O operations**:

```fortran
! Example: Simple file
OPEN(10, FILE='weather.cli')
READ(10,*) date, temp, rain  ! Sequential reads → Simple
CLOSE(10)

! Example: Unique file  
OPEN(20, FILE='config.cio')
READ(20,*) settings
REWIND(20)  ! ← Complex positioning → Unique
```

## Why It's Better

❌ **Old way**: `if filename == "hru.con": type = "Connect"` (hundreds of rules)  
✅ **New way**: Analyzes actual I/O patterns → automatically classifies

**No hardcoding needed!** 🎉

---

**See also:**
- [SIMPLE_GUIDE.md](SIMPLE_GUIDE.md) - Basic usage guide
- [HTML_CLASSIFICATION.md](HTML_CLASSIFICATION.md) - How it appears in FORD HTML
- [FILE_CLASSIFICATION.md](FILE_CLASSIFICATION.md) - Full technical details
