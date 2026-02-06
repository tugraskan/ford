# File Classification System

## Overview

The File Classification System provides automatic classification of input files based on their internal structure and content, rather than relying on hardcoded filename mappings. This is particularly useful for SWAT+ model input files and similar structured data formats.

## Classifications

The system categorizes files into four types:

### 1. **Simple**
Tabular data files with straightforward, consistent structure.

**Characteristics:**
- Consistent number of columns across rows
- Multiple rows of data (typically 5+ rows)
- Predictable, tabular format
- Contains primarily data values

**Examples:**
- `parameters.bsn` - Basin parameters
- `pcp.cli` - Precipitation data
- `hru-data.hru` - HRU (Hydrologic Response Unit) data
- `codes.bsn` - Basin codes
- `channel.cha` - Channel parameters

### 2. **Unique**
Single-instance configuration or master files.

**Characteristics:**
- Project-level configuration files
- Mixed structure (key-value pairs with some data)
- Small files with high configuration density
- Typically one per project or component

**Examples:**
- `file.cio` - Master control file
- `management.sch` - Management schedule
- `rout_unit.def` - Routing unit definitions
- `weather-wgn.cli` - Weather generator configuration
- `plant.ini` - Plant initialization

### 3. **Connect**
Files that link or connect different model components.

**Characteristics:**
- Contains references to multiple components (HRUs, channels, reservoirs, etc.)
- Defines relationships between model objects
- Typically has `.con` or `.lin` extension
- Tabular with ID/reference columns

**Examples:**
- `hru.con` - HRU connections
- `channel.con` - Channel connections
- `reservoir.con` - Reservoir connections
- `aqu_cha.lin` - Aquifer-channel linkage

### 4. **Unknown**
Files that don't match any classification pattern.

## How It Works

The classifier analyzes files based on their structural properties:

1. **File Structure Analysis**
   - Number of lines and columns
   - Column consistency (variance in column count)
   - Presence of headers
   - Number of table-like sections

2. **Content Pattern Detection**
   - References to other components
   - Keywords and identifiers
   - Mixed vs. pure tabular structure
   - Data types (numeric vs. text)

3. **Filename Heuristics**
   - File extension (`.con`, `.cli`, `.hru`, etc.)
   - Filename keywords (connection words, configuration indicators)
   - Known patterns from domain knowledge

4. **Classification Priority**
   - Connect files are checked first (most specific)
   - Unique files are checked second (configuration files)
   - Simple files are checked last (default for tabular data)

## Usage

### Python API

```python
from ford.file_classifier import FileClassifier, classify_file

# Classify a single file
classification = classify_file('parameters.bsn')
print(f"Classification: {classification}")  # Output: Classification: Simple

# Classify multiple files
classifier = FileClassifier()
files = ['file.cio', 'hru.con', 'pcp.cli']
for f in files:
    result = classifier.classify(f)
    print(f"{f}: {result}")
```

### Command-Line Interface

```bash
# Classify a single file
python -m ford.classify_files file.cio

# Classify multiple files
python -m ford.classify_files *.cli *.con

# Get detailed output
python -m ford.classify_files --verbose *.hru

# Output as CSV
python -m ford.classify_files --format csv input_files/*

# Output as JSON
python -m ford.classify_files --format json *.bsn
```

## Example Output

### Table Format (default)
```
File                 Classification
-----------------------------------
file.cio             Unique
hru.con              Connect
pcp.cli              Simple
parameters.bsn       Simple
management.sch       Unique
```

### Verbose Table Format
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

## Architecture

### FileClassifier Class

The main classifier class with methods:

- `classify(filepath)` - Classify a single file
- `_analyze_structure(filepath)` - Analyze file structure
- `_is_connect_file(filepath, structure)` - Check if file is Connect type
- `_is_unique_file(filepath, structure)` - Check if file is Unique type
- `_is_simple_file(filepath, structure)` - Check if file is Simple type

### FileStructure Dataclass

Stores analyzed file properties:
- `num_lines` - Number of content lines
- `num_columns_avg` - Average columns per line
- `num_tables` - Number of table-like sections
- `has_header` - Whether file has a header
- `has_references` - Contains component references
- `has_mixed_structure` - Mixed key-value and tabular
- `keyword_density` - Ratio of keyword/identifier lines

## Classification Logic

The classifier uses a priority-based decision tree:

```
1. Is it a Connect file?
   ✓ Has .con or .lin extension?
   ✓ Contains connection keywords + references?
   → Classify as Connect

2. Is it a Unique file?
   ✓ Has .cio, .dtl, .sch extension?
   ✓ Mixed structure with low line count?
   ✓ Configuration keywords in filename?
   → Classify as Unique

3. Is it a Simple file?
   ✓ Has consistent tabular structure?
   ✓ Has appropriate extension (.cli, .hru, .bsn, etc.)?
   ✓ Multiple rows with predictable columns?
   → Classify as Simple

4. Otherwise → Unknown
```

## Benefits Over Hardcoding

1. **Maintainability**: No need to update code when new file types are added
2. **Flexibility**: Works with renamed files or custom extensions
3. **Accuracy**: Based on actual file content, not just naming conventions
4. **Extensibility**: Easy to add new classification rules or types
5. **Discovery**: Can classify unknown file types based on structure

## Testing

Run the test suite:

```bash
pytest test/test_file_classifier.py -v
```

The test suite includes:
- Classification tests for each file type
- Structure analysis tests
- Edge case handling (empty files, mixed structures)
- File extension tests
- Convenience function tests

## Extension and Customization

To add new classification types or modify rules:

1. Add new classification method to `FileClassifier`:
```python
def _is_my_new_type(self, filepath: str, structure: FileStructure) -> bool:
    # Your classification logic here
    return condition
```

2. Register it in `__init__`:
```python
self.classification_rules = {
    'Connect': self._is_connect_file,
    'Unique': self._is_unique_file,
    'MyNewType': self._is_my_new_type,  # Add here
    'Simple': self._is_simple_file,
}
```

3. Add tests for the new type:
```python
def test_my_new_type_classification(self, classifier, temp_dir):
    content = """..."""
    filepath = self.create_test_file(temp_dir, 'test.ext', content)
    result = classifier.classify(filepath)
    assert result == 'MyNewType'
```

## Performance Considerations

- The classifier reads each file once to analyze structure
- Structure analysis examines up to the first 100 lines for column patterns
- Reference detection checks only the first 20 lines
- File operations use error-tolerant encoding (`errors='ignore'`)
- Results are not cached (classify each time)

## Future Enhancements

Potential improvements:
- Caching of classification results
- Machine learning-based classification
- Schema validation for classified files
- Auto-generation of file format documentation
- Integration with file format validators
