#!/usr/bin/env python3
"""
Enhanced Dynamic Modular Database Generator Using input_file_module.f90

This enhanced version uses the input_file_module.f90 to identify ALL SWAT+ input files
and their structures, rather than only discovering files through I/O operations.

Key Enhancements:
1. Parse input_file_module.f90 to extract all defined file structures
2. Map file.cio JSON data_reads to actual input file definitions
3. Generate templates for ALL files in the module, not just discovered ones
4. Use module type definitions to infer parameter structures
"""

import json
import csv
import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict

class EnhancedDynamicGenerator:
    """
    Enhanced generator that uses input_file_module.f90 to discover missing input files
    """
    
    def __init__(self, json_outputs_dir: str, fortran_src_dir: str = "test_data/src", output_dir: str = "enhanced_dynamic_output"):
        self.json_outputs_dir = Path(json_outputs_dir)
        self.fortran_src_dir = Path(fortran_src_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Core data structures
        self.input_file_definitions = {}  # All files from input_file_module.f90
        self.file_cio_mappings = {}       # Mappings from file.cio data_reads
        self.dynamic_templates = {}       # Combined templates
        self.parameters = []              # Final parameter database
        
        # Enhanced classification mapping
        self.classification_mapping = {
            'simulation': 'SIMULATION',
            'basin': 'BASIN',
            'climate': 'CLIMATE', 
            'connect': 'CONNECT',
            'channel': 'CHANNEL',
            'reservoir': 'RESERVOIR',
            'routing': 'ROUTING',
            'hru': 'HRU',
            'exco': 'EXCO',
            'recall': 'RECALL',
            'delivery': 'DELIVERY',
            'aquifer': 'AQUIFER',
            'herd': 'HERD',
            'water_rights': 'WATER',
            'link': 'LINK',
            'hydrology': 'HYDROLOGY',
            'structural': 'STRUCTURAL',
            'parameter_databases': 'PLANT',
            'operation': 'OPERATION',
            'land_use': 'LANDUSE',
            'calibration': 'CALIBRATION',
            'initial': 'INITIAL',
            'soils': 'SOIL',
            'conditional': 'CONDITIONAL',
            'regions': 'REGIONAL',
            'path': 'PATH'
        }
    
    def parse_input_file_module(self) -> None:
        """Parse input_file_module.f90 to extract all file definitions"""
        input_module_path = self.fortran_src_dir / "input_file_module.f90"
        
        if not input_module_path.exists():
            print(f"Warning: input_file_module.f90 not found at {input_module_path}")
            return
        
        print(f"Parsing input_file_module.f90 from {input_module_path}")
        
        with open(input_module_path, 'r') as f:
            content = f.read()
        
        # Parse type definitions to extract file structures
        self._extract_type_definitions(content)
        
        print(f"Extracted {len(self.input_file_definitions)} file categories from input_file_module.f90")
        
        # Print summary of discovered files
        total_files = sum(len(files) for files in self.input_file_definitions.values())
        print(f"Total input files defined: {total_files}")
        
        for category, files in self.input_file_definitions.items():
            print(f"  {category}: {len(files)} files")
    
    def _extract_type_definitions(self, content: str) -> None:
        """Extract type definitions and their file assignments"""
        # Pattern to match type definitions
        type_pattern = r'type\s+input_(\w+)\s*\n(.*?)\n\s*end\s+type'
        
        matches = re.findall(type_pattern, content, re.DOTALL | re.MULTILINE)
        
        for type_name, type_content in matches:
            # Extract character variable assignments
            char_pattern = r'character\(len=\d+\)\s*::\s*(\w+)\s*=\s*"([^"]+)"'
            file_assignments = re.findall(char_pattern, type_content)
            
            if file_assignments:
                self.input_file_definitions[type_name] = {}
                
                for var_name, file_name in file_assignments:
                    # Skip empty or placeholder values
                    if file_name.strip() and file_name != " ":
                        self.input_file_definitions[type_name][var_name] = file_name
                
                print(f"Found {len(file_assignments)} files in input_{type_name}")
    
    def load_file_cio_mappings(self) -> None:
        """Load file.cio JSON to understand which file categories are used"""
        cio_json_path = self.json_outputs_dir / "readcio_read.io.json"
        
        if not cio_json_path.exists():
            print(f"Warning: file.cio JSON not found at {cio_json_path}")
            return
        
        print(f"Loading file.cio mappings from {cio_json_path}")
        
        with open(cio_json_path) as f:
            data = json.load(f)
        
        # Extract data_reads to understand which input categories are referenced
        file_cio_data = data.get("file.cio", {}).get("summary", {})
        data_reads = file_cio_data.get("data_reads", [])
        
        print(f"Found {len(data_reads)} data read operations in file.cio")
        
        # Map data_reads to input file categories
        for read_op in data_reads:
            columns = read_op.get("columns", [])
            for column in columns:
                if column.startswith("in_"):
                    # Extract category name (e.g., "in_sim" -> "sim")
                    category = column[3:]  # Remove "in_" prefix
                    
                    if category in self.input_file_definitions:
                        self.file_cio_mappings[column] = self.input_file_definitions[category]
                        print(f"Mapped {column} to {len(self.input_file_definitions[category])} files")
    
    def generate_enhanced_templates(self) -> None:
        """Generate templates for all files from input_file_module.f90"""
        print("\nGenerating enhanced templates from input_file_module.f90...")
        
        total_generated = 0
        
        for category, files in self.input_file_definitions.items():
            for var_name, file_name in files.items():
                # Generate basic template for each file
                template = self._create_file_template(file_name, category, var_name)
                
                if template:
                    self.dynamic_templates[file_name] = template
                    total_generated += 1
        
        print(f"Generated {total_generated} enhanced templates")
    
    def _create_file_template(self, file_name: str, category: str, var_name: str) -> Dict[str, Any]:
        """Create a basic template for a file based on its category and context"""
        
        # Infer SWAT+ classification
        classification = self._get_classification(file_name, category)
        
        # Create basic parameters based on file type and common patterns
        parameters = self._infer_parameters_for_file(file_name, category)
        
        template = {
            'file_name': file_name,
            'category': category,
            'variable_name': var_name,
            'classification': classification,
            'parameters': parameters,
            'source': 'input_file_module.f90'
        }
        
        return template
    
    def _get_classification(self, file_name: str, category: str) -> str:
        """Get SWAT+ classification for a file"""
        # First try category mapping
        if category in self.classification_mapping:
            return self.classification_mapping[category]
        
        # Then try file extension patterns
        if file_name.endswith('.con'):
            return 'CONNECT'
        elif file_name.endswith('.cha'):
            return 'CHANNEL'
        elif file_name.endswith('.res'):
            return 'RESERVOIR'
        elif file_name.endswith('.hru'):
            return 'HRU'
        elif file_name.endswith('.sol'):
            return 'SOIL'
        elif file_name.endswith('.plt'):
            return 'PLANT'
        elif file_name.endswith('.cli'):
            return 'CLIMATE'
        elif file_name.endswith('.dtl'):
            return 'CONDITIONAL'
        else:
            return 'GENERAL'
    
    def _infer_parameters_for_file(self, file_name: str, category: str) -> List[Dict[str, Any]]:
        """Infer likely parameters for a file based on its name and category"""
        parameters = []
        
        # Common parameters based on file patterns
        if file_name.endswith('.con'):
            # Connection files typically have ID and name columns
            parameters.extend([
                {'name': 'id', 'line': 1, 'position': 1, 'data_type': 'int', 'units': 'none', 'default_value': '1'},
                {'name': 'name', 'line': 1, 'position': 2, 'data_type': 'string', 'units': 'none', 'default_value': 'default'}
            ])
        
        elif file_name.endswith('.cha'):
            # Channel files have geometry and flow parameters
            parameters.extend([
                {'name': 'name', 'line': 1, 'position': 1, 'data_type': 'string', 'units': 'none', 'default_value': 'channel1'},
                {'name': 'len2', 'line': 1, 'position': 2, 'data_type': 'real', 'units': 'm', 'default_value': '1000.0'},
                {'name': 'wd', 'line': 1, 'position': 3, 'data_type': 'real', 'units': 'm', 'default_value': '10.0'},
                {'name': 'dp', 'line': 1, 'position': 4, 'data_type': 'real', 'units': 'm', 'default_value': '2.0'}
            ])
        
        elif file_name.endswith('.hru'):
            # HRU files have area and land use parameters
            parameters.extend([
                {'name': 'name', 'line': 1, 'position': 1, 'data_type': 'string', 'units': 'none', 'default_value': 'hru1'},
                {'name': 'area', 'line': 1, 'position': 2, 'data_type': 'real', 'units': 'ha', 'default_value': '100.0'},
                {'name': 'lat', 'line': 1, 'position': 3, 'data_type': 'real', 'units': 'deg', 'default_value': '40.0'},
                {'name': 'lon', 'line': 1, 'position': 4, 'data_type': 'real', 'units': 'deg', 'default_value': '-90.0'}
            ])
        
        elif file_name.endswith('.res'):
            # Reservoir files have volume and release parameters
            parameters.extend([
                {'name': 'name', 'line': 1, 'position': 1, 'data_type': 'string', 'units': 'none', 'default_value': 'reservoir1'},
                {'name': 'vol', 'line': 1, 'position': 2, 'data_type': 'real', 'units': 'm3', 'default_value': '1000000.0'},
                {'name': 'sa', 'line': 1, 'position': 3, 'data_type': 'real', 'units': 'ha', 'default_value': '100.0'}
            ])
        
        elif file_name.endswith('.plt'):
            # Plant files have biological parameters
            parameters.extend([
                {'name': 'name', 'line': 1, 'position': 1, 'data_type': 'string', 'units': 'none', 'default_value': 'plant1'},
                {'name': 'plnt_typ', 'line': 1, 'position': 2, 'data_type': 'string', 'units': 'none', 'default_value': 'warm_annual'},
                {'name': 'gro_trig', 'line': 1, 'position': 3, 'data_type': 'string', 'units': 'none', 'default_value': 'plant_gro'},
                {'name': 'hvsti', 'line': 1, 'position': 4, 'data_type': 'real', 'units': 'fraction', 'default_value': '0.5'}
            ])
        
        elif file_name.endswith('.sol'):
            # Soil files have physical and chemical properties
            parameters.extend([
                {'name': 'name', 'line': 1, 'position': 1, 'data_type': 'string', 'units': 'none', 'default_value': 'soil1'},
                {'name': 'hydgrp', 'line': 1, 'position': 2, 'data_type': 'string', 'units': 'none', 'default_value': 'B'},
                {'name': 'dp_tot', 'line': 1, 'position': 3, 'data_type': 'real', 'units': 'mm', 'default_value': '1500.0'},
                {'name': 'bd', 'line': 1, 'position': 4, 'data_type': 'real', 'units': 'mg_m3', 'default_value': '1.3'}
            ])
        
        else:
            # Generic file with basic structure
            parameters.extend([
                {'name': 'name', 'line': 1, 'position': 1, 'data_type': 'string', 'units': 'none', 'default_value': 'default'},
                {'name': 'value', 'line': 1, 'position': 2, 'data_type': 'real', 'units': 'none', 'default_value': '0.0'}
            ])
        
        return parameters
    
    def generate_database(self) -> None:
        """Generate the final modular database CSV"""
        print("\nGenerating enhanced modular database...")
        
        self.parameters = []
        
        for file_name, template in self.dynamic_templates.items():
            for param in template['parameters']:
                # Create database row
                row = {
                    'SWAT_File': file_name,
                    'Text_File_Structure': f"Line {param['line']}, Position {param['position']}",
                    'Code_Type': param['data_type'],
                    'Default_Value': param.get('default_value', ''),
                    'Parameter_Name': param['name'],
                    'Units': param.get('units', 'none'),
                    'Min_Value': '',  # Could be enhanced with inference
                    'Max_Value': '',
                    'Definition': f"Parameter {param['name']} from {file_name}",
                    'Classification': template['classification']
                }
                
                self.parameters.append(row)
        
        # Export to CSV
        output_file = self.output_dir / "enhanced_modular_database.csv"
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['SWAT_File', 'Text_File_Structure', 'Code_Type', 'Default_Value', 
                         'Parameter_Name', 'Units', 'Min_Value', 'Max_Value', 'Definition', 'Classification']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.parameters)
        
        print(f"✅ Enhanced database exported: {output_file}")
        print(f"📊 Total parameters: {len(self.parameters)}")
        print(f"📁 Total files: {len(self.dynamic_templates)}")
        
        # Generate summary report
        self._generate_summary_report()
    
    def _generate_summary_report(self) -> None:
        """Generate detailed summary report"""
        summary_file = self.output_dir / "enhancement_summary.md"
        
        # Count by classification
        classification_counts = defaultdict(int)
        file_counts = defaultdict(int)
        
        for param in self.parameters:
            classification_counts[param['Classification']] += 1
            file_counts[param['SWAT_File']] += 1
        
        with open(summary_file, 'w') as f:
            f.write("# Enhanced Dynamic Modular Database Generation Summary\n\n")
            
            f.write(f"## Overall Statistics\n")
            f.write(f"- **Total Parameters**: {len(self.parameters)}\n")
            f.write(f"- **Total Files**: {len(self.dynamic_templates)}\n")
            f.write(f"- **Data Source**: input_file_module.f90 + pattern inference\n\n")
            
            f.write("## Classification Distribution\n")
            for classification, count in sorted(classification_counts.items()):
                f.write(f"- **{classification}**: {count} parameters\n")
            
            f.write("\n## Top Files by Parameter Count\n")
            for file_name, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
                f.write(f"- **{file_name}**: {count} parameters\n")
            
            f.write("\n## All Files Discovered\n")
            for category, files in self.input_file_definitions.items():
                f.write(f"\n### {category.upper()} ({len(files)} files)\n")
                for var_name, file_name in files.items():
                    param_count = file_counts.get(file_name, 0)
                    f.write(f"- `{file_name}` ({param_count} parameters)\n")
        
        print(f"✅ Summary report: {summary_file}")


def main():
    """Main execution function"""
    print("="*80)
    print("Enhanced Dynamic Modular Database Generator")
    print("Using input_file_module.f90 to Discover Missing Input Files")
    print("="*80)
    
    # Initialize generator
    generator = EnhancedDynamicGenerator(
        json_outputs_dir="json_outputs",
        fortran_src_dir="test_data/src",
        output_dir="enhanced_dynamic_output"
    )
    
    # Step 1: Parse input_file_module.f90
    generator.parse_input_file_module()
    
    # Step 2: Load file.cio mappings
    generator.load_file_cio_mappings()
    
    # Step 3: Generate enhanced templates
    generator.generate_enhanced_templates()
    
    # Step 4: Generate database
    generator.generate_database()
    
    print("\n" + "="*80)
    print("Enhanced generation complete! 🎉")
    print(f"Check the enhanced_dynamic_output/ directory for results.")
    

if __name__ == "__main__":
    main()