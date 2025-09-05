#!/usr/bin/env python3
"""
FORD Modular Database Generator

Generates a comprehensive parameter mapping system similar to SWAT+ Modular Database
that maps source code variables to input file parameters, database schemas, and documentation.

This leverages existing FORD analysis capabilities to create automated documentation
of the entire model parameter system.
"""

import json
import csv
import os
import sys
import re
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict

class ModularDatabaseGenerator:
    """
    Generates comprehensive modular database from FORD analysis outputs
    """
    
    def __init__(self, json_outputs_dir: str, output_dir: str = "modular_database"):
        self.json_outputs_dir = Path(json_outputs_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Core data structures
        self.parameters = []  # Main parameter database
        self.file_mappings = {}  # File to variable mappings
        self.variable_registry = {}  # Complete variable registry
        self.io_operations = {}  # I/O operation analysis
        self.module_dependencies = {}  # Module relationships
        self.type_definitions = {}  # Data type definitions
        
        # Classification mappings
        self.broad_classifications = {
            'time_': 'SIMULATION',
            'file_': 'SIMULATION', 
            'basin_': 'BASIN',
            'hru_': 'HRU',
            'channel_': 'CHANNEL',
            'cha_': 'CHANNEL',
            'res_': 'RESERVOIR',
            'aqu_': 'AQUIFER',
            'plant_': 'PLANT',
            'soil_': 'SOIL',
            'mgt_': 'MANAGEMENT',
            'cli_': 'CLIMATE',
            'cal_': 'CALIBRATION',
            'wet_': 'WETLAND',
            'pest_': 'PESTICIDE',
            'nut_': 'NUTRIENT'
        }
    
    def load_json_files(self) -> None:
        """Load all JSON analysis files"""
        print("Loading JSON analysis files...")
        
        # Load procedure analysis files
        procedure_files = list(self.json_outputs_dir.glob("*.json"))
        io_files = list(self.json_outputs_dir.glob("*.io.json"))
        
        print(f"Found {len(procedure_files)} procedure files and {len(io_files)} I/O files")
        
        for file_path in procedure_files:
            if file_path.name.endswith('.io.json'):
                continue
            try:
                with open(file_path) as f:
                    data = json.load(f)
                    self._process_procedure_file(file_path.stem, data)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        for file_path in io_files:
            try:
                with open(file_path) as f:
                    data = json.load(f)
                    self._process_io_file(file_path.stem.replace('.io', ''), data)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    
    def _process_procedure_file(self, procedure_name: str, data: Dict[str, Any]) -> None:
        """Process individual procedure analysis file"""
        if 'calls' in data:
            for call in data['calls']:
                self._register_variable(call['name'], procedure_name, 'procedure_call')
    
    def _process_io_file(self, procedure_name: str, data: Dict[str, Any]) -> None:
        """Process I/O operation analysis file"""
        self.io_operations[procedure_name] = data
        
        for unit_name, unit_data in data.items():
            # Skip if unit_data is not a dictionary (some files have integer values)
            if not isinstance(unit_data, dict):
                continue
                
            if 'summary' in unit_data:
                summary = unit_data['summary']
                
                # Process headers
                for header in summary.get('headers', []):
                    self._register_io_variable(header, procedure_name, unit_name, 'header')
                
                # Process data reads
                for read_op in summary.get('data_reads', []):
                    for column in read_op.get('columns', []):
                        self._register_io_variable(column, procedure_name, unit_name, 'data_read')
                
                # Process data writes
                for write_op in summary.get('data_writes', []):
                    for column in write_op.get('columns', []):
                        self._register_io_variable(column, procedure_name, unit_name, 'data_write')
    
    def _register_variable(self, var_name: str, procedure: str, var_type: str) -> None:
        """Register a variable in the registry"""
        if var_name not in self.variable_registry:
            self.variable_registry[var_name] = {
                'name': var_name,
                'procedures': set(),
                'types': set(),
                'io_operations': []
            }
        
        self.variable_registry[var_name]['procedures'].add(procedure)
        self.variable_registry[var_name]['types'].add(var_type)
    
    def _register_io_variable(self, var_name: str, procedure: str, unit: str, operation: str) -> None:
        """Register an I/O variable"""
        cleaned_name = self._clean_variable_name(var_name)
        self._register_variable(cleaned_name, procedure, f'io_{operation}')
        
        self.variable_registry[cleaned_name]['io_operations'].append({
            'procedure': procedure,
            'unit': unit,
            'operation': operation
        })
    
    def _clean_variable_name(self, var_name: str) -> str:
        """Clean variable name for consistent processing"""
        # Remove quotes and extra formatting
        cleaned = re.sub(r'^"|"$', '', var_name)
        cleaned = re.sub(r'\s+', ' ', cleaned.strip())
        return cleaned
    
    def _classify_parameter(self, var_name: str, procedure: str) -> str:
        """Classify parameter into broad categories"""
        name_lower = var_name.lower()
        proc_lower = procedure.lower()
        
        # Check procedure name first
        for prefix, classification in self.broad_classifications.items():
            if proc_lower.startswith(prefix):
                return classification
        
        # Check variable name
        for prefix, classification in self.broad_classifications.items():
            if name_lower.startswith(prefix):
                return classification
        
        # Default classification based on common patterns
        if any(x in name_lower for x in ['read', 'input', 'file']):
            return 'INPUT_FILE'
        elif any(x in name_lower for x in ['write', 'output', 'print']):
            return 'OUTPUT_FILE'
        else:
            return 'GENERAL'
    
    def _extract_data_type(self, var_name: str) -> str:
        """Extract or infer data type from variable name"""
        name_lower = var_name.lower()
        
        # Pattern matching for common types
        if any(x in name_lower for x in ['id', 'num', 'cnt', 'numb']):
            return 'integer'
        elif any(x in name_lower for x in ['name', 'file', 'description']):
            return 'string'
        elif any(x in name_lower for x in ['rate', 'co', 'frac', 'area', 'dp', 'wd']):
            return 'real'
        elif 'date' in name_lower or 'time' in name_lower:
            return 'datetime'
        else:
            return 'real'  # Default for scientific parameters
    
    def _extract_units(self, var_name: str) -> str:
        """Extract or infer units from variable name and context"""
        name_lower = var_name.lower()
        
        # Common unit patterns
        unit_patterns = {
            'area': 'ha',
            'dp': 'm',
            'wd': 'm', 
            'len': 'm',
            'slp': 'm/m',
            'frac': 'fraction',
            'rate': 'm/s',
            'co': 'coefficient',
            'temp': 'deg_c',
            'pcp': 'mm',
            'flow': 'm3/s',
            'sed': 'tons/ha',
            'yld': 'kg/ha'
        }
        
        for pattern, unit in unit_patterns.items():
            if pattern in name_lower:
                return unit
        
        return 'none'
    
    def _infer_file_structure(self, procedure: str, io_data: Dict) -> Dict[str, Any]:
        """Infer file structure from I/O operations"""
        structure = {
            'format': 'text',
            'has_headers': False,
            'line_count': 0,
            'columns': []
        }
        
        for unit_name, unit_data in io_data.items():
            # Skip if unit_data is not a dictionary
            if not isinstance(unit_data, dict):
                continue
                
            if 'summary' in unit_data:
                summary = unit_data['summary']
                
                if summary.get('headers'):
                    structure['has_headers'] = True
                
                # Count data operations
                structure['line_count'] += len(summary.get('data_reads', []))
                structure['line_count'] += len(summary.get('data_writes', []))
                
                # Collect columns
                for read_op in summary.get('data_reads', []):
                    structure['columns'].extend(read_op.get('columns', []))
        
        return structure
    
    def generate_parameter_database(self) -> None:
        """Generate the main parameter database"""
        print("Generating parameter database...")
        
        unique_id = 1
        
        for var_name, var_data in self.variable_registry.items():
            for procedure in var_data['procedures']:
                # Create parameter entry
                param = {
                    'Unique_ID': unique_id,
                    'Broad_Classification': self._classify_parameter(var_name, procedure),
                    'SWAT_File': f"{procedure}.f90",
                    'database_table': procedure.replace('_read', '').replace('_', ''),
                    'DATABASE_FIELD_NAME': var_name.split('%')[-1] if '%' in var_name else var_name,
                    'SWAT_Header_Name': var_name,
                    'Text_File_Structure': 'delimited',
                    'Position_in_File': self._get_position_in_file(var_name, procedure),
                    'Line_in_file': self._get_line_in_file(var_name, procedure),
                    'Swat_code_type': procedure,
                    'SWAT_Code_Variable_Name': var_name,
                    'Description': self._generate_description(var_name, procedure),
                    'Core': 'yes' if any('read' in t for t in var_data['types']) else 'no',
                    'Units': self._extract_units(var_name),
                    'Data_Type': self._extract_data_type(var_name),
                    'Minimum_Range': self._infer_min_range(var_name),
                    'Maximum_Range': self._infer_max_range(var_name),
                    'Default_Value': self._infer_default_value(var_name),
                    'Use_in_DB': 'yes'
                }
                
                self.parameters.append(param)
                unique_id += 1
    
    def _get_position_in_file(self, var_name: str, procedure: str) -> int:
        """Get position of variable in file"""
        if procedure in self.io_operations:
            position = 1
            for unit_name, unit_data in self.io_operations[procedure].items():
                # Skip if unit_data is not a dictionary
                if not isinstance(unit_data, dict):
                    continue
                    
                if 'summary' in unit_data:
                    summary = unit_data['summary']
                    for read_op in summary.get('data_reads', []):
                        if var_name in read_op.get('columns', []):
                            return position + read_op.get('columns', []).index(var_name)
                        position += len(read_op.get('columns', []))
        return 1
    
    def _get_line_in_file(self, var_name: str, procedure: str) -> int:
        """Get line number of variable in file"""
        if procedure in self.io_operations:
            line = 1
            for unit_name, unit_data in self.io_operations[procedure].items():
                # Skip if unit_data is not a dictionary
                if not isinstance(unit_data, dict):
                    continue
                    
                if 'summary' in unit_data:
                    summary = unit_data['summary']
                    if summary.get('headers') and var_name in summary['headers']:
                        return line
                    line += 1
                    for i, read_op in enumerate(summary.get('data_reads', [])):
                        if var_name in read_op.get('columns', []):
                            return line + i
        return 1
    
    def _generate_description(self, var_name: str, procedure: str) -> str:
        """Generate description for parameter"""
        # Clean variable name for description
        base_name = var_name.split('%')[-1] if '%' in var_name else var_name
        
        # Generate human-readable description
        description_patterns = {
            'id': 'Unique identifier',
            'name': 'Name or label',
            'area': 'Area in hectares',
            'dp': 'Depth in meters',
            'wd': 'Width in meters',
            'len': 'Length in meters',
            'slp': 'Slope ratio',
            'mann': 'Manning roughness coefficient',
            'k': 'Hydraulic conductivity',
            'frac': 'Fraction or ratio',
            'co': 'Coefficient',
            'init': 'Initial value',
            'max': 'Maximum value',
            'min': 'Minimum value',
            'rate': 'Rate parameter',
            'pcp': 'Precipitation',
            'tmp': 'Temperature',
            'hmd': 'Humidity',
            'wnd': 'Wind',
            'sol': 'Solar radiation',
            'yr': 'Year',
            'mo': 'Month',
            'day': 'Day'
        }
        
        base_lower = base_name.lower()
        for pattern, description in description_patterns.items():
            if pattern in base_lower:
                return f"{description} for {procedure.replace('_', ' ')}"
        
        return f"{base_name} parameter for {procedure.replace('_', ' ')}"
    
    def _infer_min_range(self, var_name: str) -> str:
        """Infer minimum range for parameter"""
        name_lower = var_name.lower()
        
        if any(x in name_lower for x in ['id', 'num', 'cnt']):
            return '1'
        elif 'frac' in name_lower or 'ratio' in name_lower:
            return '0'
        elif any(x in name_lower for x in ['area', 'dp', 'wd', 'len']):
            return '0'
        else:
            return '0'
    
    def _infer_max_range(self, var_name: str) -> str:
        """Infer maximum range for parameter"""
        name_lower = var_name.lower()
        
        if 'frac' in name_lower or 'ratio' in name_lower:
            return '1'
        elif any(x in name_lower for x in ['id', 'num', 'cnt']):
            return '9999'
        elif 'area' in name_lower:
            return '100000'
        else:
            return '999'
    
    def _infer_default_value(self, var_name: str) -> str:
        """Infer default value for parameter"""
        name_lower = var_name.lower()
        
        if any(x in name_lower for x in ['id', 'num', 'cnt']):
            return '1'
        elif 'frac' in name_lower:
            return '0.5'
        elif any(x in name_lower for x in ['name', 'file']):
            return 'default'
        else:
            return '0'
    
    def generate_file_schema(self) -> None:
        """Generate database schema from file analysis"""
        print("Generating file schema...")
        
        schema = {}
        
        for procedure, io_data in self.io_operations.items():
            table_name = procedure.replace('_read', '').replace('_', '')
            schema[table_name] = {
                'table_name': table_name,
                'source_procedure': procedure,
                'fields': [],
                'structure': self._infer_file_structure(procedure, io_data)
            }
            
            # Extract field definitions
            for unit_name, unit_data in io_data.items():
                # Skip if unit_data is not a dictionary
                if not isinstance(unit_data, dict):
                    continue
                    
                if 'summary' in unit_data:
                    summary = unit_data['summary']
                    
                    for read_op in summary.get('data_reads', []):
                        for column in read_op.get('columns', []):
                            field = {
                                'field_name': self._clean_variable_name(column),
                                'data_type': self._extract_data_type(column),
                                'units': self._extract_units(column),
                                'nullable': True,
                                'description': self._generate_description(column, procedure)
                            }
                            schema[table_name]['fields'].append(field)
        
        # Save schema
        with open(self.output_dir / 'database_schema.json', 'w') as f:
            json.dump(schema, f, indent=2)
    
    def generate_variable_mapping(self) -> None:
        """Generate comprehensive variable mapping"""
        print("Generating variable mapping...")
        
        mapping = {
            'source_code_to_file': {},
            'file_to_database': {},
            'module_dependencies': {},
            'io_operations_summary': {}
        }
        
        # Source code to file mapping
        for var_name, var_data in self.variable_registry.items():
            mapping['source_code_to_file'][var_name] = {
                'procedures': list(var_data['procedures']),
                'types': list(var_data['types']),
                'io_operations': var_data['io_operations']
            }
        
        # I/O operations summary
        mapping['io_operations_summary'] = self.io_operations
        
        # Save mapping
        with open(self.output_dir / 'variable_mapping.json', 'w') as f:
            json.dump(mapping, f, indent=2, default=str)
    
    def export_to_csv(self) -> None:
        """Export parameter database to CSV format like SWAT+ modular database"""
        print("Exporting to CSV...")
        
        if not self.parameters:
            print("No parameters to export")
            return
        
        csv_file = self.output_dir / 'modular_database.csv'
        
        # Get all field names
        fieldnames = list(self.parameters[0].keys()) if self.parameters else []
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.parameters)
        
        print(f"Exported {len(self.parameters)} parameters to {csv_file}")
    
    def generate_documentation(self) -> None:
        """Generate comprehensive documentation"""
        print("Generating documentation...")
        
        doc_content = f"""# FORD Generated Modular Database

## Overview

This modular database was automatically generated from FORD source code analysis.
It contains {len(self.parameters)} parameters extracted from {len(self.variable_registry)} unique variables
across {len(self.io_operations)} procedures with I/O operations.

## Database Structure

### Parameters
- **Total Parameters**: {len(self.parameters)}
- **Unique Variables**: {len(self.variable_registry)}
- **Procedures with I/O**: {len(self.io_operations)}

### Classifications
"""
        
        # Count by classification
        classifications = defaultdict(int)
        for param in self.parameters:
            classifications[param['Broad_Classification']] += 1
        
        for classification, count in sorted(classifications.items()):
            doc_content += f"- **{classification}**: {count} parameters\n"
        
        doc_content += """

## Files Generated

1. **modular_database.csv** - Main parameter database in CSV format
2. **database_schema.json** - Database table schemas
3. **variable_mapping.json** - Comprehensive variable mappings
4. **modular_database_documentation.md** - This documentation

## Usage

This modular database can be used for:
- Parameter validation and documentation
- Automatic GUI generation
- Model coupling and integration
- Quality assurance and testing
- User interface development

## Integration with Model Development

The database provides mappings between:
- Source code variables ↔ Input file parameters
- File structures ↔ Database schemas
- Variable relationships and data flows
- Parameter types, ranges, and validation rules

"""
        
        with open(self.output_dir / 'modular_database_documentation.md', 'w') as f:
            f.write(doc_content)
    
    def generate_all(self) -> None:
        """Generate complete modular database"""
        print(f"Starting modular database generation...")
        print(f"Input directory: {self.json_outputs_dir}")
        print(f"Output directory: {self.output_dir}")
        
        # Load and process all data
        self.load_json_files()
        
        # Generate outputs
        self.generate_parameter_database()
        self.generate_file_schema()
        self.generate_variable_mapping()
        self.export_to_csv()
        self.generate_documentation()
        
        print(f"\nModular database generation complete!")
        print(f"Generated {len(self.parameters)} parameters from {len(self.variable_registry)} variables")
        print(f"Output files saved to: {self.output_dir}")


def main():
    parser = argparse.ArgumentParser(description='Generate FORD Modular Database')
    parser.add_argument('json_outputs_dir', help='Directory containing FORD JSON outputs')
    parser.add_argument('--output-dir', '-o', default='modular_database', 
                       help='Output directory for generated database (default: modular_database)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.json_outputs_dir):
        print(f"Error: JSON outputs directory '{args.json_outputs_dir}' does not exist")
        sys.exit(1)
    
    generator = ModularDatabaseGenerator(args.json_outputs_dir, args.output_dir)
    generator.generate_all()


if __name__ == '__main__':
    main()