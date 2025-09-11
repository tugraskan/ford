#!/usr/bin/env python3
"""
Dynamic FORD Modular Database Generator

This generator creates dynamic templates by analyzing FORD JSON outputs
rather than using static hardcoded templates. It extracts actual file
structures and parameters from source code analysis.

Key Features:
1. Dynamic template discovery from JSON files
2. Automatic parameter extraction from I/O operations
3. Real file structure mapping from source code
4. SWAT+-compatible output format
"""

import json
import csv
import os
import sys
import re
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict

class DynamicModularDatabaseGenerator:
    """
    Generates modular database with dynamic templates extracted from FORD JSON analysis
    """
    
    def __init__(self, json_outputs_dir: str, output_dir: str = "modular_database"):
        self.json_outputs_dir = Path(json_outputs_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Core data structures for dynamic template generation
        self.dynamic_templates = {}  # Dynamically discovered file templates
        self.parameters = []  # Final parameter database
        self.file_structures = {}  # Actual file structures from JSON
        self.io_operations = {}  # All I/O operations analysis
        
        # Parameter type inference patterns (enhanced for dynamic analysis)
        self.type_patterns = {
            'int': r'(nyskip|day_start|day_end|yrc_start|yrc_end|numint|cnt|id|num)',
            'real': r'(area|lat|lon|elev|dp|wd|len|slp|mann|k|co|frac|rate|tmp|pcp)',
            'string': r'(name|file|path|titldum|header|csvout|cdfout)',
            'logical': r'(out|flag|use_|print|crop_|mgt)'
        }
        
        # Unit inference patterns  
        self.unit_patterns = {
            'ha': r'(area)',
            'deg': r'(lat|lon)',
            'm': r'(elev|dp|wd|len)',
            'm/m': r'(slp)',
            'none': r'(id|num|cnt|name|file|path|flag|out)',
            'days': r'(day_|nyskip)',
            'years': r'(yrc_|yrs)',
            'fraction': r'(frac)',
            'deg_c': r'(tmp)',
            'mm': r'(pcp)'
        }
        
        # SWAT+ classification mapping (enhanced for dynamic discovery)
        self.classification_mapping = {
            'file.cio': 'SIMULATION',
            'print.prt': 'SIMULATION', 
            'time.sim': 'SIMULATION',
            'basin': 'SIMULATION',
            'hru.con': 'CONNECT',
            'channel.con': 'CONNECT',
            'reservoir.con': 'CONNECT',
            'hru': 'HRU',
            'channel': 'CHANNEL',
            'cha': 'CHANNEL',
            'reservoir': 'RESERVOIR',
            'res': 'RESERVOIR',
            'plant': 'PLANT',
            'soil': 'SOIL',
            'climate': 'CLIMATE',
            'cli': 'CLIMATE'
        }
    
    def load_and_analyze_json_files(self) -> None:
        """Load all JSON files and perform dynamic analysis"""
        print("Loading and analyzing JSON files for dynamic template generation...")
        
        # Focus on I/O files that contain actual file reading operations
        io_files = list(self.json_outputs_dir.glob("*.io.json"))
        print(f"Found {len(io_files)} I/O analysis files")
        
        for io_file in io_files:
            try:
                with open(io_file) as f:
                    data = json.load(f)
                    procedure_name = io_file.stem.replace('.io', '')
                    self.io_operations[procedure_name] = data
                    self._analyze_file_structure(procedure_name, data)
            except Exception as e:
                print(f"Error loading {io_file}: {e}")
    
    def _analyze_file_structure(self, procedure_name: str, io_data: Dict[str, Any]) -> None:
        """Analyze I/O data to extract dynamic file structures"""
        for file_unit, unit_data in io_data.items():
            if not isinstance(unit_data, dict) or 'summary' not in unit_data:
                continue
            
            # Extract file name from unit identifier or procedure context
            file_name = self._infer_file_name(file_unit, procedure_name)
            
            if file_name:
                file_structure = self._extract_file_structure(file_name, unit_data['summary'])
                if file_structure['parameters']:
                    self.file_structures[file_name] = file_structure
                    print(f"Discovered file structure: {file_name} with {len(file_structure['parameters'])} parameters")
    
    def _infer_file_name(self, file_unit: str, procedure_name: str) -> Optional[str]:
        """Infer actual file name from unit identifier and procedure context"""
        # Direct file name detection
        if '.' in file_unit:
            return file_unit
        
        # Map procedure names to file names based on common patterns
        file_mappings = {
            'readcio_read': 'file.cio',
            'basin_print_codes_read': 'print.prt',
            'time_read': 'time.sim',
            'hru_con_read': 'hru.con', 
            'channel_con_read': 'channel.con',
            'reservoir_con_read': 'reservoir.con',
            'hru_read': 'hru-data.hru',
            'channel_read': 'channel.cha',
            'plant_read': 'plants.plt',
            'soil_read': 'soils.sol'
        }
        
        # Try direct mapping first
        for proc_pattern, filename in file_mappings.items():
            if proc_pattern in procedure_name.lower():
                return filename
        
        # Try pattern matching for complex procedure names
        proc_lower = procedure_name.lower()
        if 'cio' in proc_lower or 'file' in proc_lower:
            return 'file.cio'
        elif 'print' in proc_lower and 'basin' in proc_lower:
            return 'print.prt'
        elif 'hru' in proc_lower and 'con' in proc_lower:
            return 'hru.con'
        elif 'channel' in proc_lower or 'cha' in proc_lower:
            if 'con' in proc_lower:
                return 'channel.con'
            else:
                return 'channel.cha'
        elif 'reservoir' in proc_lower or 'res' in proc_lower:
            if 'con' in proc_lower:
                return 'reservoir.con'
            else:
                return 'reservoir.res'
        
        return None
    
    def _extract_file_structure(self, file_name: str, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Extract file structure and parameters from I/O summary"""
        structure = {
            'file_name': file_name,
            'parameters': [],
            'headers': summary.get('headers', []),
            'data_reads': summary.get('data_reads', []),
            'total_lines': 0
        }
        
        # Process headers as parameters
        for i, header in enumerate(structure['headers']):
            param = self._create_parameter_from_name(header, i + 1, 1, 'header')
            structure['parameters'].append(param)
        
        # Process data reads to extract parameters
        current_line = len(structure['headers']) + 1
        for read_op in structure['data_reads']:
            columns = read_op.get('columns', [])
            rows = read_op.get('rows', 1)
            
            for i, column in enumerate(columns):
                # Clean parameter name (remove array indices and module prefixes)
                clean_name = self._clean_parameter_name(column)
                param = self._create_parameter_from_name(clean_name, i + 1, current_line, 'data')
                structure['parameters'].append(param)
            
            current_line += rows
        
        structure['total_lines'] = current_line - 1
        return structure
    
    def _clean_parameter_name(self, raw_name: str) -> str:
        """Clean parameter name by removing prefixes, array indices, etc."""
        # Remove module/type prefixes (e.g., 'pco%', 'in_sim%')
        if '%' in raw_name:
            raw_name = raw_name.split('%')[-1]
        
        # Remove array indices (e.g., 'aa_yrs(ii), ii = 1, pco%aa_numint' -> 'aa_yrs')
        if '(' in raw_name:
            raw_name = raw_name.split('(')[0]
        
        # Remove extra whitespace and formatting
        raw_name = raw_name.strip()
        
        # Handle special cases
        if ', ii =' in raw_name:
            raw_name = raw_name.split(',')[0].strip()
        
        return raw_name
    
    def _create_parameter_from_name(self, param_name: str, position: int, line: int, param_type: str) -> Dict[str, Any]:
        """Create parameter definition from name with intelligent type inference"""
        param = {
            'name': param_name,
            'position': position,
            'line': line,
            'param_type': param_type,
            'data_type': self._infer_data_type(param_name),
            'units': self._infer_units(param_name),
            'description': self._generate_description(param_name),
            'min_range': self._infer_min_range(param_name),
            'max_range': self._infer_max_range(param_name),
            'default_value': self._infer_default_value(param_name)
        }
        
        return param
    
    def _infer_data_type(self, param_name: str) -> str:
        """Infer data type from parameter name patterns"""
        name_lower = param_name.lower()
        
        for data_type, pattern in self.type_patterns.items():
            if re.search(pattern, name_lower):
                return 'integer' if data_type == 'int' else data_type
        
        # Default inference based on common patterns
        if any(x in name_lower for x in ['name', 'file', 'path', 'header', 'title']):
            return 'string'
        elif any(x in name_lower for x in ['id', 'num', 'cnt', 'day', 'yr']):
            return 'integer'
        elif any(x in name_lower for x in ['out', 'flag', 'use']):
            return 'string'  # Often used as yes/no flags in SWAT
        else:
            return 'real'  # Default for scientific parameters
    
    def _infer_units(self, param_name: str) -> str:
        """Infer units from parameter name patterns"""
        name_lower = param_name.lower()
        
        for unit, pattern in self.unit_patterns.items():
            if re.search(pattern, name_lower):
                return unit
        
        return 'none'
    
    def _generate_description(self, param_name: str) -> str:
        """Generate human-readable description from parameter name"""
        name_lower = param_name.lower()
        
        # Common parameter descriptions
        descriptions = {
            'nyskip': 'Number of years to skip for output',
            'day_start': 'Starting day of simulation',
            'day_end': 'Ending day of simulation', 
            'yrc_start': 'Starting year of simulation',
            'yrc_end': 'Ending year of simulation',
            'csvout': 'CSV output flag',
            'cdfout': 'NetCDF output flag',
            'crop_yld': 'Crop yield output flag',
            'mgtout': 'Management output flag',
            'hydcon': 'Hydrologic connectivity output flag',
            'titldum': 'Title line (dummy)',
            'header': 'Header line',
            'name': 'Name or identifier',
            'area': 'Area',
            'lat': 'Latitude', 
            'lon': 'Longitude',
            'elev': 'Elevation',
            'id': 'Unique identifier'
        }
        
        # Try exact match first
        if name_lower in descriptions:
            return descriptions[name_lower]
        
        # Try partial matches
        for key, desc in descriptions.items():
            if key in name_lower:
                return f"{desc} parameter"
        
        # Generate generic description
        formatted_name = param_name.replace('_', ' ').title()
        return f"{formatted_name} parameter"
    
    def _infer_min_range(self, param_name: str) -> str:
        """Infer minimum range for parameter"""
        name_lower = param_name.lower()
        
        if any(x in name_lower for x in ['id', 'num', 'cnt']):
            return '1'
        elif any(x in name_lower for x in ['frac', 'fraction']):
            return '0'
        elif any(x in name_lower for x in ['day', 'yrc', 'yr']):
            return '0'
        else:
            return '0'
    
    def _infer_max_range(self, param_name: str) -> str:
        """Infer maximum range for parameter"""
        name_lower = param_name.lower()
        
        if 'frac' in name_lower or 'fraction' in name_lower:
            return '1'
        elif 'day' in name_lower and 'start' in name_lower or 'end' in name_lower:
            return '366'
        elif 'yrc' in name_lower or 'yr' in name_lower:
            return '2100'
        elif any(x in name_lower for x in ['id', 'num', 'cnt']):
            return '9999'
        elif 'area' in name_lower:
            return '100000'
        elif 'lat' in name_lower:
            return '90'
        elif 'lon' in name_lower:
            return '180'
        else:
            return '999'
    
    def _infer_default_value(self, param_name: str) -> str:
        """Infer default value for parameter"""
        name_lower = param_name.lower()
        
        if any(x in name_lower for x in ['name', 'file', 'path', 'header', 'title']):
            return 'default'
        elif any(x in name_lower for x in ['out', 'flag']) and name_lower != 'outflow':
            return 'n'  # Default for SWAT output flags
        elif any(x in name_lower for x in ['day_start', 'yrc_start']):
            return '1' if 'day' in name_lower else '2000'
        elif any(x in name_lower for x in ['day_end']):
            return '365'
        elif any(x in name_lower for x in ['yrc_end']):
            return '2010'
        elif any(x in name_lower for x in ['id', 'num', 'cnt']):
            return '1'
        elif 'frac' in name_lower:
            return '0.5'
        else:
            return '0'
    
    def generate_dynamic_templates(self) -> None:
        """Generate dynamic templates from discovered file structures"""
        print("Generating dynamic templates from source code analysis...")
        
        unique_id = 1
        
        for file_name, structure in self.file_structures.items():
            classification = self._get_classification(file_name)
            table_name = self._create_table_name(file_name)
            
            print(f"Processing dynamic template for {file_name} ({len(structure['parameters'])} parameters)")
            
            for param in structure['parameters']:
                param_entry = {
                    'Unique_ID': unique_id,
                    'Broad_Classification': classification,
                    'SWAT_File': file_name,
                    'database_table': table_name,
                    'DATABASE_FIELD_NAME': param['name'],
                    'SWAT_Header_Name': param['name'],
                    'Text_File_Structure': 'delimited',
                    'Position_in_File': param['position'],
                    'Line_in_file': param['line'],
                    'Swat_code_type': self._get_code_type(file_name),
                    'SWAT_Code_Variable_Name': param['name'],
                    'Description': param['description'],
                    'Core': 'yes' if classification == 'SIMULATION' else 'no',
                    'Units': param['units'],
                    'Data_Type': param['data_type'],
                    'Minimum_Range': param['min_range'],
                    'Maximum_Range': param['max_range'],
                    'Default_Value': param['default_value'],
                    'Use_in_DB': 'yes'
                }
                
                self.parameters.append(param_entry)
                unique_id += 1
        
        print(f"Generated {len(self.parameters)} parameters from dynamic template analysis")
    
    def _get_classification(self, file_name: str) -> str:
        """Get SWAT+ classification for file"""
        # Direct mapping
        if file_name in self.classification_mapping:
            return self.classification_mapping[file_name]
        
        # Pattern-based classification
        name_lower = file_name.lower()
        for pattern, classification in self.classification_mapping.items():
            if pattern in name_lower:
                return classification
        
        return 'GENERAL'
    
    def _create_table_name(self, file_name: str) -> str:
        """Create database table name from file name"""
        # Remove extension and convert to valid table name
        base_name = file_name.split('.')[0]
        table_name = base_name.replace('-', '_').replace('.', '_')
        return table_name
    
    def _get_code_type(self, file_name: str) -> str:
        """Get SWAT code type from file name"""
        return file_name.replace('.', '_').replace('-', '_')
    
    def export_to_csv(self) -> None:
        """Export dynamic parameter database to CSV"""
        print("Exporting dynamic modular database to CSV...")
        
        csv_file = self.output_dir / 'dynamic_modular_database.csv'
        
        # SWAT+ compatible field order
        fieldnames = [
            'Unique_ID', 'Broad_Classification', 'SWAT_File', 'database_table',
            'DATABASE_FIELD_NAME', 'SWAT_Header_Name', 'Text_File_Structure', 
            'Position_in_File', 'Line_in_file', 'Swat_code_type',
            'SWAT_Code_Variable_Name', 'Description', 'Core', 'Units',
            'Data_Type', 'Minimum_Range', 'Maximum_Range', 'Default_Value', 'Use_in_DB'
        ]
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            # Sort by classification and file for better organization
            sorted_params = sorted(self.parameters, key=lambda x: (x['Broad_Classification'], x['SWAT_File'], x['Unique_ID']))
            writer.writerows(sorted_params)
        
        print(f"Exported {len(self.parameters)} dynamically generated parameters to {csv_file}")
    
    def generate_analysis_report(self) -> None:
        """Generate analysis report of dynamic template generation"""
        report_file = self.output_dir / 'dynamic_template_analysis.md'
        
        # Statistics
        by_classification = defaultdict(int)
        by_file = defaultdict(int)
        
        for param in self.parameters:
            by_classification[param['Broad_Classification']] += 1
            by_file[param['SWAT_File']] += 1
        
        with open(report_file, 'w') as f:
            f.write("# Dynamic Modular Database Generation Report\n\n")
            f.write("## Overview\n\n")
            f.write("This database was generated using **dynamic template analysis** of FORD JSON outputs.\n")
            f.write("Instead of static templates, parameters were extracted directly from source code I/O operations.\n\n")
            
            f.write(f"**Total Parameters**: {len(self.parameters)}\n")
            f.write(f"**Files Analyzed**: {len(self.file_structures)}\n")
            f.write(f"**I/O Procedures**: {len(self.io_operations)}\n\n")
            
            f.write("## Dynamic Template Discovery\n\n")
            f.write("### Files with Dynamic Templates\n\n")
            for file_name, structure in self.file_structures.items():
                f.write(f"- **{file_name}**: {len(structure['parameters'])} parameters, {structure['total_lines']} lines\n")
            
            f.write("\n### Parameters by Classification\n\n")
            for classification, count in sorted(by_classification.items()):
                f.write(f"- **{classification}**: {count} parameters\n")
            
            f.write("\n### Parameters by File\n\n")
            for file_name, count in sorted(by_file.items()):
                f.write(f"- **{file_name}**: {count} parameters\n")
            
            f.write("\n## Advantages of Dynamic Templates\n\n")
            f.write("✅ **Source Code Accuracy**: Parameters extracted from actual file reading operations\n")
            f.write("✅ **Automatic Discovery**: No manual template maintenance required\n") 
            f.write("✅ **Real Structure Mapping**: Reflects actual file formats and line positions\n")
            f.write("✅ **Comprehensive Coverage**: Captures all parameters the source code actually reads\n")
            f.write("✅ **Type Intelligence**: Smart inference of data types, units, and ranges\n\n")
            
            f.write("## Template Generation Process\n\n")
            f.write("1. **JSON Analysis**: Load FORD I/O analysis files (`*.io.json`)\n")
            f.write("2. **File Discovery**: Identify input files from procedure names and units\n")
            f.write("3. **Parameter Extraction**: Parse data_reads sections for column information\n")
            f.write("4. **Type Inference**: Apply intelligent patterns for data types and units\n")
            f.write("5. **Structure Mapping**: Map parameters to file positions and lines\n")
            f.write("6. **Database Generation**: Create SWAT+-compatible parameter database\n")
    
    def generate_all(self) -> None:
        """Generate complete dynamic modular database"""
        print("Starting dynamic modular database generation...")
        print(f"Input directory: {self.json_outputs_dir}")
        print(f"Output directory: {self.output_dir}")
        
        # Load and analyze JSON files
        self.load_and_analyze_json_files()
        
        # Generate dynamic templates
        self.generate_dynamic_templates()
        
        # Export results
        self.export_to_csv()
        self.generate_analysis_report()
        
        print(f"\nDynamic modular database generation complete!")
        print(f"Generated {len(self.parameters)} parameters from {len(self.file_structures)} dynamically discovered files")
        print(f"Output files saved to: {self.output_dir}")

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Generate Dynamic SWAT+ Modular Database from FORD Analysis')
    parser.add_argument('json_outputs_dir', help='Directory containing FORD JSON outputs')
    parser.add_argument('--output-dir', '-o', default='modular_database', 
                       help='Output directory for generated database (default: modular_database)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.json_outputs_dir):
        print(f"Error: JSON outputs directory '{args.json_outputs_dir}' does not exist")
        sys.exit(1)
    
    generator = DynamicModularDatabaseGenerator(args.json_outputs_dir, args.output_dir)
    generator.generate_all()

if __name__ == '__main__':
    main()