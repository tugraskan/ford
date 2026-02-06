# How It Works - Simple Explanation

## The Problem

You have lots of input files with different purposes. Instead of writing code for each filename (hardcoding), we want the computer to figure out what type of file it is by **looking inside**.

## The Solution

The classifier reads your file and checks:

### 1. **Is it a table?** (Simple)
- Does it have rows and columns?
- Are the columns consistent?
- **Example**: Weather data, parameter tables
- **Result**: → **Simple**

### 2. **Does it connect things?** (Connect)  
- Does it link components together (like HRU→Channel)?
- Filename ends in `.con` or `.lin`?
- **Example**: `hru.con` linking HRUs to channels
- **Result**: → **Connect**

### 3. **Is it a master config?** (Unique)
- Is it a control/settings file?
- Mixed structure or special extensions (`.cio`, `.sch`)?
- **Example**: `file.cio` master configuration
- **Result**: → **Unique**

## Quick Example

```bash
# You run this:
python -m ford.classify_files my_files/*

# It outputs:
File              Type
----------------  --------
weather.cli       Simple      # Saw: table with rows/columns
hru.con           Connect     # Saw: links between objects
settings.cio      Unique      # Saw: master config file
```

## Why It's Better

❌ **Old way**: `if filename == "hru.con": type = "Connect"` (hundreds of rules)  
✅ **New way**: Reads the file, sees it connects things → automatically classifies it

**No hardcoding needed!** 🎉
