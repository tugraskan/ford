# File Classification System - Quick Start

## What is This?

This is an **automatic file classification system** that categorizes input files (particularly SWAT+ model files) based on their **internal structure** rather than hardcoded filename mappings.

## Quick Example

```bash
# Classify files in your directory
python -m ford.classify_files input_files/*

# Output:
# File                 Classification
# -----------------------------------
# file.cio             Unique
# hru.con              Connect
# pcp.cli              Simple
# parameters.bsn       Simple
```

## Installation

The classifier is included in this FORD package. No additional dependencies required beyond those needed for FORD.

## Usage

### Command Line

```bash
# Basic usage
python -m ford.classify_files file1.cli file2.con file3.hru

# Verbose mode (shows structure details)
python -m ford.classify_files --verbose *.cli

# CSV output
python -m ford.classify_files --format csv *.* > results.csv

# JSON output
python -m ford.classify_files --format json input_files/*
```

### Python API

```python
from ford.file_classifier import classify_file, FileClassifier

# Quick classification
result = classify_file('parameters.bsn')
print(result)  # Output: Simple

# Detailed analysis
classifier = FileClassifier()
classification = classifier.classify('hru.con')
structure = classifier._analyze_structure('hru.con')

print(f"Classification: {classification}")
print(f"Lines: {structure.num_lines}")
print(f"Columns: {structure.num_columns_avg}")
```

## Classification Types

| Type | Description | Examples |
|------|-------------|----------|
| **Simple** | Tabular data files | `pcp.cli`, `codes.bsn`, `hru-data.hru` |
| **Unique** | Configuration/master files | `file.cio`, `management.sch`, `plant.ini` |
| **Connect** | Component linkage files | `hru.con`, `channel.con`, `aqu_cha.lin` |
| **Unknown** | Unmatched patterns | Files with unusual structure |

## How It Works

The classifier analyzes:

1. **File Structure** - rows, columns, consistency
2. **Content Patterns** - references, keywords, data types
3. **Filename Hints** - extensions and naming conventions

No hardcoded mappings! The system understands file purpose from content.

## Benefits

✓ **No hardcoding** - works with renamed files  
✓ **Adaptive** - handles variations in structure  
✓ **Accurate** - based on actual file content  
✓ **Extensible** - easy to add new types  
✓ **Discoverable** - handles unknown files gracefully

## Documentation

- **[FILE_CLASSIFICATION.md](FILE_CLASSIFICATION.md)** - Complete usage guide
- **[CLASSIFICATION_ANALYSIS.md](CLASSIFICATION_ANALYSIS.md)** - Analysis of the classification system
- **[example_classification.py](example_classification.py)** - Working demonstration

## Testing

Run the test suite:

```bash
pytest test/test_file_classifier.py -v
```

All 19 tests passing ✓

## Example Output

### Table Format (default)
```
File                 Classification
-----------------------------------
file.cio             Unique
hru.con              Connect
pcp.cli              Simple
```

### Verbose Mode
```
File                 Classification  Lines  Cols  Tables
--------------------------------------------------------
file.cio             Unique             15   2.5       1
hru.con              Connect            50   3.0       1
pcp.cli              Simple            365   4.0       1
```

### CSV Format
```csv
file,classification
file.cio,Unique
hru.con,Connect
pcp.cli,Simple
```

## Common Use Cases

### Classify All Files in a Project
```bash
python -m ford.classify_files /path/to/swat_project/* > classifications.txt
```

### Find All Connection Files
```bash
python -m ford.classify_files /path/to/project/* --format csv | grep Connect
```

### Analyze Unknown Files
```bash
python -m ford.classify_files --verbose unknown_file.txt
```

## Problem Statement

**Question**: "Does the classification make sense? Can we figure out a way to classify files without hardcoding?"

**Answer**: ✓ Yes! This system successfully classifies files based on structure rather than hardcoded names.

See [CLASSIFICATION_ANALYSIS.md](CLASSIFICATION_ANALYSIS.md) for the complete analysis.

## Support

For issues or questions, refer to the documentation files or examine the test cases in `test/test_file_classifier.py` for examples.
