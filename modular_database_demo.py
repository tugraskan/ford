#!/usr/bin/env python3
"""
FORD Modular Database Integration Demo

Demonstrates how to use the generated modular database for various applications
including parameter validation, GUI generation, and model integration.
"""

import json
import csv
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

class ModularDatabaseAPI:
    """API for interacting with the FORD-generated modular database"""
    
    def __init__(self, db_path: str = "modular_database"):
        self.db_path = Path(db_path)
        self.parameters = self._load_parameters()
        self.schema = self._load_schema()
        self.mappings = self._load_mappings()
    
    def _load_parameters(self) -> List[Dict]:
        """Load parameter database"""
        with open(self.db_path / 'modular_database.csv', 'r') as f:
            return list(csv.DictReader(f))
    
    def _load_schema(self) -> Dict:
        """Load database schema"""
        with open(self.db_path / 'database_schema.json', 'r') as f:
            return json.load(f)
    
    def _load_mappings(self) -> Dict:
        """Load variable mappings"""
        with open(self.db_path / 'variable_mapping.json', 'r') as f:
            return json.load(f)
    
    def search_parameters(self, query: str, classification: Optional[str] = None) -> List[Dict]:
        """Search parameters by name or description"""
        results = []
        query_lower = query.lower()
        
        for param in self.parameters:
            # Search in variable name and description
            if (query_lower in param['SWAT_Code_Variable_Name'].lower() or 
                query_lower in param['Description'].lower()):
                
                # Filter by classification if specified
                if classification is None or param['Broad_Classification'] == classification:
                    results.append(param)
        
        return results
    
    def get_parameters_by_classification(self, classification: str) -> List[Dict]:
        """Get all parameters for a specific classification"""
        return [p for p in self.parameters if p['Broad_Classification'] == classification]
    
    def get_parameters_by_file(self, filename: str) -> List[Dict]:
        """Get all parameters from a specific source file"""
        return [p for p in self.parameters if filename in p['SWAT_File']]
    
    def get_table_schema(self, table_name: str) -> Optional[Dict]:
        """Get schema for a specific database table"""
        return self.schema.get(table_name)
    
    def validate_parameter_value(self, param_name: str, value: str) -> Dict[str, Any]:
        """Validate a parameter value against its constraints"""
        # Find parameter
        param = None
        for p in self.parameters:
            if p['SWAT_Code_Variable_Name'] == param_name:
                param = p
                break
        
        if not param:
            return {'valid': False, 'error': 'Parameter not found'}
        
        result = {'valid': True, 'warnings': [], 'info': param}
        
        try:
            # Type validation
            data_type = param['Data_Type']
            if data_type == 'integer':
                val = int(value)
            elif data_type == 'real':
                val = float(value)
            elif data_type == 'string':
                val = str(value)
            else:
                val = value
            
            # Range validation
            if data_type in ['integer', 'real']:
                min_val = float(param['Minimum_Range'])
                max_val = float(param['Maximum_Range'])
                
                if val < min_val or val > max_val:
                    result['warnings'].append(f'Value {val} outside range [{min_val}, {max_val}]')
            
        except ValueError as e:
            result['valid'] = False
            result['error'] = f'Type conversion error: {e}'
        
        return result
    
    def generate_input_template(self, classification: str) -> str:
        """Generate input file template for a classification"""
        params = self.get_parameters_by_classification(classification)
        
        template = f"# {classification} Parameters Template\n"
        template += f"# Generated from FORD Modular Database\n"
        template += f"# Total parameters: {len(params)}\n\n"
        
        # Group by source file
        files = {}
        for param in params:
            file_name = param['SWAT_File']
            if file_name not in files:
                files[file_name] = []
            files[file_name].append(param)
        
        for file_name, file_params in files.items():
            template += f"## {file_name}\n"
            for param in file_params[:5]:  # Show first 5 parameters per file
                template += f"# {param['Description']}\n"
                template += f"# Type: {param['Data_Type']}, Units: {param['Units']}\n"
                template += f"# Range: [{param['Minimum_Range']}, {param['Maximum_Range']}]\n"
                template += f"{param['DATABASE_FIELD_NAME']} = {param['Default_Value']}\n\n"
            
            if len(file_params) > 5:
                template += f"# ... and {len(file_params) - 5} more parameters\n\n"
        
        return template
    
    def get_io_summary(self, procedure: str) -> Dict[str, Any]:
        """Get I/O operations summary for a procedure"""
        return self.mappings['io_operations_summary'].get(procedure, {})
    
    def generate_documentation(self, classification: str) -> str:
        """Generate documentation for a parameter classification"""
        params = self.get_parameters_by_classification(classification)
        
        doc = f"# {classification} Parameters Documentation\n\n"
        doc += f"Total parameters: {len(params)}\n\n"
        
        # Summary table
        doc += "## Parameter Summary\n\n"
        doc += "| Parameter | Type | Units | Description |\n"
        doc += "|-----------|------|-------|-------------|\n"
        
        for param in params[:20]:  # Show first 20
            name = param['SWAT_Code_Variable_Name'].split('%')[-1]
            doc += f"| {name} | {param['Data_Type']} | {param['Units']} | {param['Description']} |\n"
        
        if len(params) > 20:
            doc += f"\n*... and {len(params) - 20} more parameters*\n"
        
        return doc

def demo_basic_usage():
    """Demonstrate basic usage of the modular database API"""
    print("=== FORD Modular Database API Demo ===\n")
    
    api = ModularDatabaseAPI()
    
    print(f"📊 Database loaded:")
    print(f"  Parameters: {len(api.parameters):,}")
    print(f"  Tables: {len(api.schema):,}")
    print(f"  I/O Procedures: {len(api.mappings['io_operations_summary']):,}")
    print()
    
    # 1. Search demonstration
    print("🔍 **SEARCH EXAMPLES**")
    
    # Search for area parameters
    area_params = api.search_parameters("area")
    print(f"Parameters containing 'area': {len(area_params)}")
    for param in area_params[:3]:
        print(f"  • {param['SWAT_Code_Variable_Name']} ({param['Data_Type']})")
    print()
    
    # Search HRU parameters
    hru_params = api.get_parameters_by_classification("HRU")
    print(f"HRU parameters: {len(hru_params)}")
    for param in hru_params[:3]:
        print(f"  • {param['SWAT_Code_Variable_Name']} - {param['Description']}")
    print()
    
    # 2. Parameter validation
    print("✅ **PARAMETER VALIDATION**")
    
    if hru_params:
        test_param = hru_params[0]['SWAT_Code_Variable_Name']
        
        # Valid value
        result = api.validate_parameter_value(test_param, "1.5")
        print(f"Validating {test_param} = 1.5: {'✓' if result['valid'] else '✗'}")
        
        # Invalid value (string for numeric)
        result = api.validate_parameter_value(test_param, "invalid")
        print(f"Validating {test_param} = 'invalid': {'✓' if result['valid'] else '✗'}")
        if not result['valid']:
            print(f"  Error: {result['error']}")
    print()
    
    # 3. Template generation
    print("📝 **TEMPLATE GENERATION**")
    template = api.generate_input_template("SIMULATION")
    print("Generated SIMULATION template:")
    print(template[:500] + "..." if len(template) > 500 else template)
    print()
    
    # 4. I/O operations
    print("📁 **I/O OPERATIONS**")
    io_summary = api.get_io_summary("basin_print_codes_read")
    if io_summary:
        print("basin_print_codes_read I/O operations:")
        for unit, data in list(io_summary.items())[:2]:
            if isinstance(data, dict) and 'summary' in data:
                summary = data['summary']
                reads = len(summary.get('data_reads', []))
                writes = len(summary.get('data_writes', []))
                print(f"  Unit {unit}: {reads} reads, {writes} writes")
    print()

def demo_advanced_features():
    """Demonstrate advanced features and integration possibilities"""
    print("🚀 **ADVANCED FEATURES DEMO**\n")
    
    api = ModularDatabaseAPI()
    
    # 1. Cross-reference analysis
    print("🔗 **CROSS-REFERENCE ANALYSIS**")
    
    # Find parameters that appear in multiple files
    param_files = {}
    for param in api.parameters:
        var_name = param['SWAT_Code_Variable_Name']
        file_name = param['SWAT_File']
        
        if var_name not in param_files:
            param_files[var_name] = set()
        param_files[var_name].add(file_name)
    
    shared_params = {k: v for k, v in param_files.items() if len(v) > 1}
    print(f"Parameters used in multiple files: {len(shared_params)}")
    
    for param, files in list(shared_params.items())[:3]:
        print(f"  • {param}: {len(files)} files")
    print()
    
    # 2. Schema relationships
    print("🗄️ **SCHEMA RELATIONSHIPS**")
    
    # Find tables with similar field patterns
    field_patterns = {}
    for table_name, table_data in api.schema.items():
        for field in table_data['fields']:
            field_type = field['data_type']
            if field_type not in field_patterns:
                field_patterns[field_type] = []
            field_patterns[field_type].append(table_name)
    
    print("Data type distribution across tables:")
    for dtype, tables in field_patterns.items():
        unique_tables = len(set(tables))
        print(f"  {dtype}: {unique_tables} tables")
    print()
    
    # 3. Model component mapping
    print("🏗️ **MODEL COMPONENT MAPPING**")
    
    # Group by model components
    component_map = {
        'Hydrology': ['HRU', 'BASIN', 'CHANNEL', 'AQUIFER'],
        'Vegetation': ['PLANT', 'SOIL'],
        'Management': ['MANAGEMENT', 'CLIMATE'],
        'Water Quality': ['NUTRIENT', 'PESTICIDE'],
        'Infrastructure': ['RESERVOIR', 'WETLAND'],
        'System': ['SIMULATION', 'CALIBRATION']
    }
    
    for component, classifications in component_map.items():
        total_params = sum(len(api.get_parameters_by_classification(c)) for c in classifications)
        print(f"  {component}: {total_params:,} parameters")
    print()

def export_integration_examples():
    """Export example files for different integration scenarios"""
    print("📤 **EXPORTING INTEGRATION EXAMPLES**\n")
    
    api = ModularDatabaseAPI()
    output_dir = Path("integration_examples")
    output_dir.mkdir(exist_ok=True)
    
    # 1. GUI Configuration
    gui_config = {
        'parameter_groups': {},
        'validation_rules': {},
        'default_values': {}
    }
    
    for classification in ['SIMULATION', 'HRU', 'BASIN']:
        params = api.get_parameters_by_classification(classification)
        gui_config['parameter_groups'][classification] = []
        
        for param in params[:5]:  # First 5 parameters per group
            param_info = {
                'name': param['DATABASE_FIELD_NAME'],
                'type': param['Data_Type'],
                'description': param['Description'],
                'units': param['Units']
            }
            gui_config['parameter_groups'][classification].append(param_info)
            
            # Validation rules
            gui_config['validation_rules'][param['DATABASE_FIELD_NAME']] = {
                'min': param['Minimum_Range'],
                'max': param['Maximum_Range'],
                'required': param['Core'] == 'yes'
            }
            
            # Default values
            gui_config['default_values'][param['DATABASE_FIELD_NAME']] = param['Default_Value']
    
    with open(output_dir / 'gui_config.json', 'w') as f:
        json.dump(gui_config, f, indent=2)
    
    # 2. Database DDL
    ddl = "-- FORD Generated Database Schema\n"
    ddl += "-- Auto-generated from modular database\n\n"
    
    for table_name, table_data in list(api.schema.items())[:3]:  # First 3 tables
        ddl += f"CREATE TABLE {table_name} (\n"
        
        for field in table_data['fields'][:5]:  # First 5 fields per table
            sql_type = {
                'integer': 'INTEGER',
                'real': 'REAL',
                'string': 'VARCHAR(255)',
                'datetime': 'DATETIME'
            }.get(field['data_type'], 'TEXT')
            
            nullable = "NULL" if field['nullable'] else "NOT NULL"
            ddl += f"    {field['field_name']} {sql_type} {nullable},\n"
        
        ddl = ddl.rstrip(',\n') + "\n);\n\n"
    
    with open(output_dir / 'database_schema.sql', 'w') as f:
        f.write(ddl)
    
    # 3. API Documentation
    api_doc = api.generate_documentation("SIMULATION")
    with open(output_dir / 'api_documentation.md', 'w') as f:
        f.write(api_doc)
    
    # 4. Validation script
    validation_script = '''#!/usr/bin/env python3
"""
Parameter validation script generated from FORD Modular Database
"""

def validate_parameters(param_dict):
    """Validate parameters using FORD database rules"""
    from modular_database_demo import ModularDatabaseAPI
    
    api = ModularDatabaseAPI()
    results = {}
    
    for param_name, value in param_dict.items():
        result = api.validate_parameter_value(param_name, str(value))
        results[param_name] = result
    
    return results

if __name__ == '__main__':
    # Example usage
    test_params = {
        'area': '100.5',
        'invalid_param': 'test'
    }
    
    results = validate_parameters(test_params)
    for param, result in results.items():
        status = "✓" if result['valid'] else "✗"
        print(f"{param}: {status}")
'''
    
    with open(output_dir / 'parameter_validator.py', 'w') as f:
        f.write(validation_script)
    
    print(f"Integration examples exported to: {output_dir}")
    print("Files created:")
    print("  • gui_config.json - GUI configuration")
    print("  • database_schema.sql - Database DDL")
    print("  • api_documentation.md - API documentation")
    print("  • parameter_validator.py - Validation script")

if __name__ == '__main__':
    demo_basic_usage()
    demo_advanced_features() 
    export_integration_examples()