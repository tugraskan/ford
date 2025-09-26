# FORD Modular Database Guide

## Overview

The FORD Modular Database is a comprehensive system that enables cross-project documentation linking, parameter extraction, and structured data export from Fortran source code analysis. This system provides several layers of functionality to support complex Fortran project ecosystems.

## Core Features

### 1. External Module Integration (`--externalize`)

**Purpose**: Create JSON exports of Fortran modules for cross-project documentation linking.

**Usage**:
```bash
ford --externalize project.md
```

**Output**: Creates `modules.json` in the output directory containing:
- Module metadata and structure
- Public procedures, types, and variables
- Cross-reference URLs for documentation linking
- Enhanced metadata for detailed analysis

**Example modules.json structure**:
```json
{
  "ford-metadata": {"version": "0.1.dev2+g7ed05c533"},
  "modules": [
    {
      "name": "example_module",
      "external_url": "./module/example_module.html",
      "pub_procs": {...},
      "pub_types": {...},
      "pub_vars": {...}
    }
  ],
  "metadata": [...]
}
```

### 2. Cross-Project Documentation Linking

**Purpose**: Reference external FORD-generated documentation in your project.

**Configuration** (in project.md):
```yaml
external: 
  my_library = ../library_project/doc
  remote_lib = https://example.com/docs
```

**Functionality**:
- Automatic linking to external procedures and types
- Cross-project dependency resolution
- Unified documentation across multiple projects

### 3. Parameter Database Generation

**Purpose**: Extract comprehensive parameter information and create SWAT+-style databases.

**Available Scripts**:

#### `generate_json.py` - JSON Export Utility
```bash
python generate_json.py src_directory -o json_outputs/
```
- Extracts detailed metadata from Fortran source
- Creates JSON files for further processing
- Supports multiple source directories

#### `modular_database_generator.py` - SWAT+ Style Database
```bash
python modular_database_generator.py json_outputs/ -o database/
```
- Creates comprehensive parameter databases
- Generates CSV files compatible with SWAT+ format
- Maps source code variables to input file parameters

#### Other Generators:
- `dynamic_modular_database_generator.py` - Dynamic template generation
- `enhanced_modular_database_generator.py` - Enhanced analysis features

## Practical Applications

### Multi-Project Fortran Development

**Scenario**: Large modeling system with multiple libraries

1. **Library Project Setup**:
```bash
# Generate library documentation with externalization
ford --externalize library_project.md
```

2. **Main Project Configuration**:
```yaml
# In main_project.md
external:
  hydro_lib = ../hydro_library/doc
  utils_lib = ../utilities/doc
```

3. **Automatic Cross-Linking**:
- References to library procedures automatically linked
- Type definitions shared across projects
- Unified documentation navigation

### Parameter Documentation and Validation

**Use Case**: Model parameter management

1. **Extract Parameters**:
```bash
python generate_json.py model_src/ -o analysis/
python modular_database_generator.py analysis/ -o param_db/
```

2. **Generated Outputs**:
- `modular_database.csv` - Complete parameter catalog
- `database_schema.json` - Database table definitions
- `variable_mapping.json` - Source-to-file mappings
- Comprehensive documentation

3. **Applications**:
- GUI generation from parameter schemas
- Input validation systems
- Model coupling interfaces
- Quality assurance frameworks

### Model Integration and Coupling

**Benefits**:
- Standardized interface documentation
- Automated parameter mapping
- Cross-model data flow analysis
- Integration testing support

## Technical Implementation

### JSON Export Process

1. **Source Analysis**: FORD parses Fortran source code
2. **Metadata Extraction**: Procedures, types, variables cataloged
3. **JSON Generation**: Structured export with cross-references
4. **Documentation Integration**: Links embedded in HTML output

### External Module Loading

1. **Configuration Reading**: External URLs parsed from project config
2. **JSON Retrieval**: Remote or local modules.json files loaded
3. **Object Creation**: External entities created as linkable objects
4. **Cross-Reference Resolution**: Links established during correlation

### Parameter Database Generation

1. **I/O Analysis**: File operations and variable usage tracked
2. **Classification**: Parameters categorized by function/domain
3. **Schema Generation**: Database structures inferred
4. **Export**: Multiple formats (CSV, JSON, documentation)

## Best Practices

### Project Organization

```
project_root/
├── src/                    # Source code
├── doc/                    # Generated documentation
│   └── modules.json       # External module data
├── external_libs/         # External project references
└── project.md            # FORD configuration
```

### Configuration Recommendations

```yaml
# Optimal project.md for modular database
project: My Project
externalize: true          # Enable JSON export
search: true              # Enable search functionality
external:                 # External references
  common_lib = ../common/doc
graph: true               # Enable dependency graphs
```

### Workflow Integration

1. **Development Phase**: Use external linking for active development
2. **Documentation Phase**: Generate comprehensive databases
3. **Integration Phase**: Leverage parameter mappings
4. **Maintenance Phase**: Update cross-references as needed

## Available Scripts and Tools

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `ford --externalize` | Basic JSON export | Source code | modules.json |
| `generate_json.py` | Detailed analysis | Source directories | JSON analysis files |
| `modular_database_generator.py` | Parameter database | JSON analysis | CSV database |
| `dynamic_modular_database_generator.py` | Dynamic templates | JSON analysis | Enhanced database |
| `enhanced_modular_database_generator.py` | Advanced features | JSON analysis | Extended analysis |

## Troubleshooting

### Common Issues

**External Links Not Working**:
- Verify external project has `modules.json`
- Check file paths in configuration
- Ensure external project was generated with `--externalize`

**Missing Parameters in Database**:
- Verify I/O operations are recognized
- Check variable naming patterns
- Review generator script configuration

**Cross-Project Dependencies**:
- Use relative paths for portable references
- Validate external project structure
- Test link resolution in generated docs

## Future Development

The modular database system continues to evolve with:
- Enhanced parameter extraction algorithms
- Improved cross-project dependency resolution
- Extended database schema generation
- Better integration with external tools

This system provides a powerful foundation for managing complex Fortran project ecosystems and enables sophisticated documentation and parameter management workflows.