#!/usr/bin/env python3
"""
Enhanced FORD Modular Database Generator
Creates a comprehensive parameter mapping system similar to the original SWAT+ Modular Database

This generator focuses on:
1. Input file parameter mapping (like file.cio, hru.con, channel.cha)
2. Database schema correlations 
3. Proper SWAT+-style classification (SIMULATION, CONNECT, HRU, CHANNEL, etc.)
4. Comprehensive parameter coverage
5. File structure and position mapping
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

class EnhancedModularDatabaseGenerator:
    """
    Enhanced generator that creates SWAT+-style modular database from FORD analysis
    """
    
    def __init__(self, json_outputs_dir: str, output_dir: str = "modular_database"):
        self.json_outputs_dir = Path(json_outputs_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Core data structures
        self.parameters = []  # Main parameter database
        self.file_mappings = {}  # Input file to parameter mappings
        self.io_analysis = {}  # I/O operation analysis
        
        # SWAT+-style classification system
        self.swat_classifications = {
            # Core simulation files
            'file.cio': 'SIMULATION',
            'time.sim': 'SIMULATION', 
            'print.prt': 'SIMULATION',
            'object.cnt': 'SIMULATION',
            'codes.bsn': 'SIMULATION',
            'parameters.bsn': 'SIMULATION',
            
            # Connection files  
            'hru.con': 'CONNECT',
            'channel.con': 'CONNECT',
            'reservoir.con': 'CONNECT',
            'aquifer.con': 'CONNECT',
            'routing_unit.con': 'CONNECT',
            'outlet.con': 'CONNECT',
            
            # HRU data files
            'hru-data.hru': 'HRU',
            'topography.hyd': 'HRU', 
            'hydrology.hyd': 'HRU',
            'soils.sol': 'HRU',
            'nutrients.sol': 'HRU',
            
            # Channel files
            'channel.cha': 'CHANNEL',
            'hydrology.cha': 'CHANNEL',
            'sediment.cha': 'CHANNEL',
            'nutrients.cha': 'CHANNEL',
            
            # Plant files
            'plants.plt': 'PLANT',
            'plant.ini': 'PLANT',
            'landuse.lum': 'PLANT',
            'management.sch': 'PLANT',
            
            # Climate files
            'weather-sta.cli': 'CLIMATE',
            'weather-wgn.cli': 'CLIMATE',
            'pcp.cli': 'CLIMATE',
            'tmp.cli': 'CLIMATE',
            'slr.cli': 'CLIMATE',
            
            # Reservoir files
            'reservoir.res': 'RESERVOIR',
            'hydrology.res': 'RESERVOIR',
            
            # Aquifer files  
            'aquifer.aqu': 'AQUIFER',
            
            # Calibration files
            'cal_parms.cal': 'CALIBRATION',
            'calibration.cal': 'CALIBRATION'
        }
        
        # Parameter type inference patterns
        self.parameter_patterns = {
            'id': {'type': 'integer', 'units': 'none', 'description': 'Unique identifier'},
            'name': {'type': 'string', 'units': 'none', 'description': 'Name or label'},
            'area': {'type': 'real', 'units': 'ha', 'description': 'Area in hectares'},
            'lat': {'type': 'real', 'units': 'deg', 'description': 'Latitude'},
            'lon': {'type': 'real', 'units': 'deg', 'description': 'Longitude'},
            'elev': {'type': 'real', 'units': 'm', 'description': 'Elevation'},
            'dp': {'type': 'real', 'units': 'm', 'description': 'Depth'},
            'wd': {'type': 'real', 'units': 'm', 'description': 'Width'},
            'len': {'type': 'real', 'units': 'm', 'description': 'Length'},
            'slp': {'type': 'real', 'units': 'm/m', 'description': 'Slope'},
            'mann': {'type': 'real', 'units': 'none', 'description': 'Manning roughness coefficient'},
            'k': {'type': 'real', 'units': 'm/s', 'description': 'Hydraulic conductivity'},
            'frac': {'type': 'real', 'units': 'fraction', 'description': 'Fraction'},
            'co': {'type': 'real', 'units': 'none', 'description': 'Coefficient'},
            'yr': {'type': 'integer', 'units': 'none', 'description': 'Year'},
            'mo': {'type': 'integer', 'units': 'none', 'description': 'Month'},
            'day': {'type': 'integer', 'units': 'none', 'description': 'Day'},
            'cnt': {'type': 'integer', 'units': 'none', 'description': 'Count'},
            'tmp': {'type': 'real', 'units': 'deg_c', 'description': 'Temperature'},
            'pcp': {'type': 'real', 'units': 'mm', 'description': 'Precipitation'},
            'flow': {'type': 'real', 'units': 'm3/s', 'description': 'Flow rate'},
            'vol': {'type': 'real', 'units': 'm3', 'description': 'Volume'},
            'conc': {'type': 'real', 'units': 'mg/l', 'description': 'Concentration'}
        }
    
    def load_json_files(self) -> None:
        """Load and process JSON analysis files"""
        print("Loading JSON analysis files...")
        
        # Load I/O analysis files 
        io_files = list(self.json_outputs_dir.glob("*.io.json"))
        procedure_files = list(self.json_outputs_dir.glob("*.json"))
        
        print(f"Found {len(io_files)} I/O files and {len(procedure_files)} procedure files")
        
        # Process I/O files to extract file operations
        for io_file in io_files:
            try:
                with open(io_file) as f:
                    data = json.load(f)
                    procedure_name = io_file.stem.replace('.io', '')
                    self.io_analysis[procedure_name] = data
                    self._extract_file_parameters(procedure_name, data)
            except Exception as e:
                print(f"Error loading {io_file}: {e}")
        
        # Process procedure files for additional context
        for proc_file in procedure_files:
            if proc_file.name.endswith('.io.json'):
                continue
            try:
                with open(proc_file) as f:
                    data = json.load(f)
                    procedure_name = proc_file.stem
                    self._process_procedure_context(procedure_name, data)
            except Exception as e:
                print(f"Error loading {proc_file}: {e}")
    
    def _extract_file_parameters(self, procedure_name: str, io_data: Dict[str, Any]) -> None:
        """Extract parameter mappings from I/O operations"""
        for unit_name, unit_data in io_data.items():
            if not isinstance(unit_data, dict):
                continue
                
            # Extract file information from unit operations
            file_info = self._analyze_unit_operations(unit_name, unit_data, procedure_name)
            
            if file_info:
                self._register_file_parameters(file_info, procedure_name)
    
    def _analyze_unit_operations(self, unit_name: str, unit_data: Dict, procedure_name: str) -> Optional[Dict]:
        """Analyze unit operations to extract file and parameter information"""
        file_info = {
            'unit_name': unit_name,
            'procedure': procedure_name,
            'parameters': [],
            'file_type': 'unknown',
            'operations': []
        }
        
        # Check for operations in the unit data
        if 'operations' in unit_data:
            operations = unit_data['operations']
            for op in operations:
                op_info = {
                    'type': op.get('operation', 'unknown'),
                    'line': op.get('line', 0),
                    'details': op.get('details', ''),
                    'variables': []
                }
                
                # Extract variables from operation details
                variables = self._extract_variables_from_operation(op.get('details', ''))
                op_info['variables'] = variables
                file_info['operations'].append(op_info)
                
                # Add variables as parameters
                for var in variables:
                    if var not in [p['name'] for p in file_info['parameters']]:
                        param_info = self._create_parameter_info(var, op_info)
                        file_info['parameters'].append(param_info)
        
        # Infer file type from unit name or procedure
        file_info['file_type'] = self._infer_file_type(unit_name, procedure_name)
        
        return file_info if file_info['parameters'] else None
    
    def _extract_variables_from_operation(self, operation_details: str) -> List[str]:
        """Extract variable names from operation details"""
        variables = []
        
        # Common patterns for read/write operations
        patterns = [
            r'read\s*\([^)]*\)\s*([^,\n]+)',  # read(...) variables
            r'write\s*\([^)]*\)\s*([^,\n]+)', # write(...) variables  
            r'([a-zA-Z_][a-zA-Z0-9_%]*)',     # general variable names
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, operation_details)
            for match in matches:
                # Clean and validate variable names
                var_name = match.strip()
                if self._is_valid_variable_name(var_name):
                    variables.append(var_name)
        
        return list(set(variables))  # Remove duplicates
    
    def _is_valid_variable_name(self, name: str) -> bool:
        """Check if a string is a valid variable name"""
        if not name or len(name) < 2:
            return False
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_%]*$', name):
            return False
        # Exclude common Fortran keywords and operators
        keywords = {'read', 'write', 'open', 'close', 'if', 'then', 'else', 'end', 'do', 'while'}
        return name.lower() not in keywords
    
    def _create_parameter_info(self, var_name: str, operation_info: Dict) -> Dict:
        """Create parameter information from variable name and context"""
        param_info = {
            'name': var_name,
            'operation_type': operation_info['type'],
            'line': operation_info['line'],
            'data_type': 'real',  # default
            'units': 'none',
            'description': f'{var_name} parameter',
            'min_range': '0',
            'max_range': '999',
            'default_value': '0'
        }
        
        # Enhance with pattern matching
        var_lower = var_name.lower()
        for pattern, info in self.parameter_patterns.items():
            if pattern in var_lower:
                param_info.update(info)
                break
        
        return param_info
    
    def _infer_file_type(self, unit_name: str, procedure_name: str) -> str:
        """Infer file type from unit name and procedure context"""
        unit_lower = unit_name.lower()
        proc_lower = procedure_name.lower()
        
        # Common file extension patterns
        if any(ext in unit_lower for ext in ['.cio', '.sim', '.prt']):
            return 'SIMULATION'
        elif any(ext in unit_lower for ext in ['.con', '.hru', '.cha', '.res']):
            return 'CONNECTION'
        elif any(word in proc_lower for word in ['read', 'input']):
            return 'INPUT_FILE'
        elif any(word in proc_lower for word in ['write', 'output', 'print']):
            return 'OUTPUT_FILE'
        else:
            return 'DATA_FILE'
    
    def _register_file_parameters(self, file_info: Dict, procedure_name: str) -> None:
        """Register file parameters in the main database"""
        file_name = self._extract_file_name(file_info['unit_name'], procedure_name)
        classification = self._get_classification(file_name, file_info['file_type'])
        
        for i, param in enumerate(file_info['parameters']):
            param_entry = {
                'Unique_ID': len(self.parameters) + 1,
                'Broad_Classification': classification,
                'SWAT_File': file_name,
                'database_table': self._create_table_name(file_name),
                'DATABASE_FIELD_NAME': param['name'],
                'SWAT_Header_Name': param['name'],
                'Text_File_Structure': 'delimited',
                'Position_in_File': i + 1,
                'Line_in_file': param['line'] if param['line'] > 0 else 1,
                'Swat_code_type': procedure_name,
                'SWAT_Code_Variable_Name': param['name'],
                'Description': param['description'],
                'Core': 'yes' if param['operation_type'] == 'read' else 'no',
                'Units': param['units'],
                'Data_Type': param['data_type'],
                'Minimum_Range': param['min_range'],
                'Maximum_Range': param['max_range'],
                'Default_Value': param['default_value'],
                'Use_in_DB': 'yes'
            }
            
            self.parameters.append(param_entry)
    
    def _extract_file_name(self, unit_name: str, procedure_name: str) -> str:
        """Extract meaningful file name from unit name or procedure"""
        # Try to extract from unit name first
        if '.' in unit_name:
            return unit_name
        
        # Infer from procedure name
        proc_lower = procedure_name.lower()
        
        # Common file name patterns
        file_mappings = {
            'basin_print_codes_read': 'file.cio',
            'hru_read': 'hru-data.hru',
            'channel_read': 'channel.cha',
            'reservoir_read': 'reservoir.res',
            'plant_read': 'plants.plt',
            'soil_read': 'soils.sol',
            'climate_read': 'weather-sta.cli'
        }
        
        for proc_pattern, file_name in file_mappings.items():
            if proc_pattern in proc_lower:
                return file_name
        
        # Default fallback
        return f"{procedure_name}.dat"
    
    def _get_classification(self, file_name: str, file_type: str) -> str:
        """Get SWAT-style classification for file"""
        if file_name in self.swat_classifications:
            return self.swat_classifications[file_name]
        
        # Fallback classification based on file type
        type_classifications = {
            'SIMULATION': 'SIMULATION',
            'CONNECTION': 'CONNECT', 
            'INPUT_FILE': 'INPUT',
            'OUTPUT_FILE': 'OUTPUT',
            'DATA_FILE': 'DATA'
        }
        
        return type_classifications.get(file_type, 'GENERAL')
    
    def _create_table_name(self, file_name: str) -> str:
        """Create database table name from file name"""
        # Remove extension and convert to table format
        base_name = file_name.split('.')[0]
        table_name = base_name.replace('-', '_').replace('.', '_')
        return table_name
    
    def _process_procedure_context(self, procedure_name: str, data: Dict[str, Any]) -> None:
        """Process procedure data for additional context"""
        # This can be expanded to extract more context from procedure analysis
        pass
    
    def add_swat_core_parameters(self) -> None:
        """Add core SWAT+ parameters based on the original modular database structure"""
        print("Adding core SWAT+ parameters...")
        
        # Complete file.cio parameters (based on original SWAT+ database)
        core_params = [
            {
                'file': 'file.cio',
                'table': 'file_cio', 
                'classification': 'SIMULATION',
                'parameters': [
                    # Line 2: Core simulation files
                    {'field': 'time_sim', 'pos': 2, 'line': 2, 'desc': 'Defines simulation period', 'type': 'string', 'default': 'time.sim', 'code_type': 'in_sim'},
                    {'field': 'print', 'pos': 3, 'line': 2, 'desc': 'Defines which files will be printed and timestep', 'type': 'string', 'default': 'print.prt', 'code_type': 'in_sim'},
                    {'field': 'obj_prt', 'pos': 4, 'line': 2, 'desc': 'User defined output files', 'type': 'string', 'default': 'object.prt', 'code_type': 'in_sim'},
                    {'field': 'obj_cnt', 'pos': 5, 'line': 2, 'desc': 'Spatial object counts', 'type': 'string', 'default': 'object.cnt', 'code_type': 'in_sim'},
                    {'field': 'cs_db', 'pos': 6, 'line': 2, 'desc': 'Constituents files', 'type': 'string', 'default': 'constituents.cs', 'code_type': 'in_sim'},
                    
                    # Line 3: Basin files
                    {'field': 'bsn_code', 'pos': 2, 'line': 3, 'desc': 'Basin codes', 'type': 'string', 'default': 'codes.bsn', 'code_type': 'in_basin'},
                    {'field': 'bsn_parm', 'pos': 3, 'line': 3, 'desc': 'Basin parameters', 'type': 'string', 'default': 'parameters.bsn', 'code_type': 'in_basin'},
                    
                    # Line 4: Climate files
                    {'field': 'wst_dat', 'pos': 2, 'line': 4, 'desc': 'Weather stations', 'type': 'string', 'default': 'weather-sta.cli', 'code_type': 'in_cli'},
                    {'field': 'wgn_dat', 'pos': 3, 'line': 4, 'desc': 'Weather generator data', 'type': 'string', 'default': 'weather-wgn.cli', 'code_type': 'in_cli'},
                    {'field': 'pet_dat', 'pos': 4, 'line': 4, 'desc': 'Potential evaporation data', 'type': 'string', 'default': 'wind-dir.cli', 'code_type': 'in_cli'},
                    
                    # Line 5: Connection files
                    {'field': 'hru_con', 'pos': 2, 'line': 5, 'desc': 'HRU connection data', 'type': 'string', 'default': 'hru.con', 'code_type': 'in_connect'},
                    {'field': 'hru_data', 'pos': 3, 'line': 5, 'desc': 'HRU data file', 'type': 'string', 'default': 'hru-data.hru', 'code_type': 'in_connect'},
                    {'field': 'cha_con', 'pos': 4, 'line': 5, 'desc': 'Channel connection data', 'type': 'string', 'default': 'channel.con', 'code_type': 'in_connect'},
                    {'field': 'cha_data', 'pos': 5, 'line': 5, 'desc': 'Channel data file', 'type': 'string', 'default': 'channel.cha', 'code_type': 'in_connect'},
                    {'field': 'res_con', 'pos': 6, 'line': 5, 'desc': 'Reservoir connection data', 'type': 'string', 'default': 'reservoir.con', 'code_type': 'in_connect'},
                    {'field': 'res_data', 'pos': 7, 'line': 5, 'desc': 'Reservoir data file', 'type': 'string', 'default': 'reservoir.res', 'code_type': 'in_connect'},
                    
                    # Line 6: Land use and management files
                    {'field': 'lum_data', 'pos': 2, 'line': 6, 'desc': 'Land use management', 'type': 'string', 'default': 'landuse.lum', 'code_type': 'in_lum'},
                    {'field': 'mgt_data', 'pos': 3, 'line': 6, 'desc': 'Management operations', 'type': 'string', 'default': 'management.sch', 'code_type': 'in_mgt'},
                    {'field': 'sol_data', 'pos': 4, 'line': 6, 'desc': 'Soil data file', 'type': 'string', 'default': 'soils.sol', 'code_type': 'in_sol'},
                    {'field': 'nut_data', 'pos': 5, 'line': 6, 'desc': 'Nutrients data', 'type': 'string', 'default': 'nutrients.nut', 'code_type': 'in_nut'},
                    
                    # Line 7-10: Plant and database files
                    {'field': 'plt_data', 'pos': 2, 'line': 7, 'desc': 'Plant database', 'type': 'string', 'default': 'plants.plt', 'code_type': 'in_plt'},
                    {'field': 'til_data', 'pos': 3, 'line': 7, 'desc': 'Tillage database', 'type': 'string', 'default': 'tillage.til', 'code_type': 'in_til'},
                    {'field': 'frt_data', 'pos': 4, 'line': 7, 'desc': 'Fertilizer database', 'type': 'string', 'default': 'fertilizer.frt', 'code_type': 'in_frt'},
                    {'field': 'pst_data', 'pos': 5, 'line': 7, 'desc': 'Pesticide database', 'type': 'string', 'default': 'pesticide.pst', 'code_type': 'in_pst'},
                    {'field': 'urb_data', 'pos': 6, 'line': 7, 'desc': 'Urban database', 'type': 'string', 'default': 'urban.urb', 'code_type': 'in_urb'},
                    {'field': 'sep_data', 'pos': 7, 'line': 7, 'desc': 'Septic database', 'type': 'string', 'default': 'septic.sep', 'code_type': 'in_sep'},
                    
                    # Line 8-15: Additional model components
                    {'field': 'cal_data', 'pos': 2, 'line': 8, 'desc': 'Calibration data', 'type': 'string', 'default': 'calibration.cal', 'code_type': 'in_cal'},
                    {'field': 'rte_data', 'pos': 3, 'line': 8, 'desc': 'Routing parameters', 'type': 'string', 'default': 'routing.rte', 'code_type': 'in_rte'},
                    {'field': 'ops_data', 'pos': 4, 'line': 8, 'desc': 'Operations data', 'type': 'string', 'default': 'operations.ops', 'code_type': 'in_ops'},
                    {'field': 'lte_data', 'pos': 5, 'line': 8, 'desc': 'LTE data file', 'type': 'string', 'default': 'lte.dat', 'code_type': 'in_lte'},
                    
                    # Lines 9-26: Regional definitions for different components
                    {'field': 'hru_reg_def', 'pos': 2, 'line': 9, 'desc': 'HRU regional definitions', 'type': 'string', 'default': 'hru_reg.def', 'code_type': 'in_regs'},
                    {'field': 'hru_catunit_def', 'pos': 3, 'line': 9, 'desc': 'HRU catchment unit definitions', 'type': 'string', 'default': 'hru_catunit.def', 'code_type': 'in_regs'},
                    {'field': 'hru_catunit_ele', 'pos': 4, 'line': 9, 'desc': 'HRU catchment unit elements', 'type': 'string', 'default': 'hru_catunit.ele', 'code_type': 'in_regs'},
                    
                    {'field': 'cha_reg_def', 'pos': 2, 'line': 10, 'desc': 'Channel regional definitions', 'type': 'string', 'default': 'cha_reg.def', 'code_type': 'in_regs'},
                    {'field': 'cha_catunit_def', 'pos': 3, 'line': 10, 'desc': 'Channel catchment unit definitions', 'type': 'string', 'default': 'cha_catunit.def', 'code_type': 'in_regs'},
                    {'field': 'cha_catunit_ele', 'pos': 4, 'line': 10, 'desc': 'Channel catchment unit elements', 'type': 'string', 'default': 'cha_catunit.ele', 'code_type': 'in_regs'},
                    
                    {'field': 'res_reg_def', 'pos': 2, 'line': 11, 'desc': 'Reservoir regional definitions', 'type': 'string', 'default': 'res_reg.def', 'code_type': 'in_regs'},
                    {'field': 'res_catunit_def', 'pos': 3, 'line': 11, 'desc': 'Reservoir catchment unit definitions', 'type': 'string', 'default': 'res_catunit.def', 'code_type': 'in_regs'},
                    {'field': 'res_catunit_ele', 'pos': 4, 'line': 11, 'desc': 'Reservoir catchment unit elements', 'type': 'string', 'default': 'res_catunit.ele', 'code_type': 'in_regs'},
                    
                    # Lines 12-26: More regional components
                    {'field': 'aqu_reg_def', 'pos': 2, 'line': 12, 'desc': 'Aquifer regional definitions', 'type': 'string', 'default': 'aqu_reg.def', 'code_type': 'in_regs'},
                    {'field': 'aqu_catunit_def', 'pos': 3, 'line': 12, 'desc': 'Aquifer catchment unit definitions', 'type': 'string', 'default': 'aqu_catunit.def', 'code_type': 'in_regs'},
                    {'field': 'aqu_catunit_ele', 'pos': 4, 'line': 12, 'desc': 'Aquifer catchment unit elements', 'type': 'string', 'default': 'aqu_catunit.ele', 'code_type': 'in_regs'},
                    
                    {'field': 'cha_lte_reg_def', 'pos': 2, 'line': 13, 'desc': 'Channel LTE regional definitions', 'type': 'string', 'default': 'cha_lte_reg.def', 'code_type': 'in_regs'},
                    {'field': 'cha_lte_catunit_def', 'pos': 3, 'line': 13, 'desc': 'Channel LTE catchment unit definitions', 'type': 'string', 'default': 'cha_lte_catunit.def', 'code_type': 'in_regs'},
                    {'field': 'cha_lte_catunit_ele', 'pos': 4, 'line': 13, 'desc': 'Channel LTE catchment unit elements', 'type': 'string', 'default': 'cha_lte_catunit.ele', 'code_type': 'in_regs'},
                    
                    # Lines 27-31: Path configurations
                    {'field': 'path_pcp', 'pos': 2, 'line': 27, 'desc': 'Directory path for pcp file', 'type': 'string', 'default': 'null', 'code_type': 'in_path_pcp'},
                    {'field': 'path_tmp', 'pos': 2, 'line': 28, 'desc': 'Directory path for tmp file', 'type': 'string', 'default': 'null', 'code_type': 'in_path_tmp'},
                    {'field': 'path_slr', 'pos': 2, 'line': 29, 'desc': 'Directory path for slr file', 'type': 'string', 'default': 'null', 'code_type': 'in_path_slr'},
                    {'field': 'path_hmd', 'pos': 2, 'line': 30, 'desc': 'Directory path for hmd file', 'type': 'string', 'default': 'null', 'code_type': 'in_path_hmd'},
                    {'field': 'path_wnd', 'pos': 2, 'line': 31, 'desc': 'Directory path for wnd file', 'type': 'string', 'default': 'null', 'code_type': 'in_path_wnd'},
                ]
            },
            {
                'file': 'hru.con',
                'table': 'hru_con',
                'classification': 'CONNECT', 
                'parameters': [
                    {'field': 'id', 'pos': 1, 'line': 1, 'desc': 'HRU unique identifier', 'type': 'integer', 'units': 'none'},
                    {'field': 'name', 'pos': 2, 'line': 1, 'desc': 'HRU name', 'type': 'string', 'units': 'none'},
                    {'field': 'gis_id', 'pos': 3, 'line': 1, 'desc': 'GIS identifier', 'type': 'string', 'units': 'none'},
                    {'field': 'area', 'pos': 4, 'line': 1, 'desc': 'HRU area', 'type': 'real', 'units': 'ha'},
                    {'field': 'lat', 'pos': 5, 'line': 1, 'desc': 'Latitude', 'type': 'real', 'units': 'deg'},
                    {'field': 'lon', 'pos': 6, 'line': 1, 'desc': 'Longitude', 'type': 'real', 'units': 'deg'},
                    {'field': 'elev', 'pos': 7, 'line': 1, 'desc': 'Elevation', 'type': 'real', 'units': 'm'},
                ]
            },
            {
                'file': 'channel.con',
                'table': 'cha_con',
                'classification': 'CONNECT',
                'parameters': [
                    {'field': 'id', 'pos': 1, 'line': 1, 'desc': 'Channel unique identifier', 'type': 'integer', 'units': 'none'},
                    {'field': 'name', 'pos': 2, 'line': 1, 'desc': 'Channel name', 'type': 'string', 'units': 'none'},
                    {'field': 'gis_id', 'pos': 3, 'line': 1, 'desc': 'GIS identifier', 'type': 'string', 'units': 'none'},
                    {'field': 'area', 'pos': 4, 'line': 1, 'desc': 'Channel area', 'type': 'real', 'units': 'ha'},
                    {'field': 'lat', 'pos': 5, 'line': 1, 'desc': 'Latitude', 'type': 'real', 'units': 'deg'},
                    {'field': 'lon', 'pos': 6, 'line': 1, 'desc': 'Longitude', 'type': 'real', 'units': 'deg'},
                    {'field': 'elev', 'pos': 7, 'line': 1, 'desc': 'Elevation', 'type': 'real', 'units': 'm'},
                ]
            }
        ]
        
        for file_params in core_params:
            for param in file_params['parameters']:
                param_entry = {
                    'Unique_ID': len(self.parameters) + 1,
                    'Broad_Classification': file_params['classification'],
                    'SWAT_File': file_params['file'],
                    'database_table': file_params['table'],
                    'DATABASE_FIELD_NAME': param['field'],
                    'SWAT_Header_Name': '*',
                    'Text_File_Structure': 'Unique',
                    'Position_in_File': param['pos'],
                    'Line_in_file': param['line'],
                    'Swat_code_type': param.get('code_type', file_params['file'].replace('.', '_')),
                    'SWAT_Code_Variable_Name': '*',
                    'Description': param['desc'],
                    'Core': 'core',
                    'Units': param.get('units', '*'),
                    'Data_Type': param['type'],
                    'Minimum_Range': '*',
                    'Maximum_Range': '*',
                    'Default_Value': param.get('default', '*'),
                    'Use_in_DB': '*'
                }
                
                self.parameters.append(param_entry)
    
    def generate_comprehensive_database(self) -> None:
        """Generate comprehensive modular database"""
        print("Generating comprehensive modular database...")
        
        # Add core SWAT+ parameters first
        self.add_swat_core_parameters()
        
        # Generate CSV output
        csv_file = self.output_dir / "enhanced_modular_database.csv"
        
        # Define field order to match original
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
            writer.writerows(self.parameters)
        
        print(f"Generated enhanced modular database with {len(self.parameters)} parameters")
        print(f"Output saved to: {csv_file}")
        
        # Generate summary report
        self._generate_summary_report()
    
    def _generate_summary_report(self) -> None:
        """Generate summary report of the database"""
        summary_file = self.output_dir / "enhanced_database_summary.md"
        
        # Count by classification
        by_classification = defaultdict(int)
        by_file_type = defaultdict(int)
        
        for param in self.parameters:
            by_classification[param['Broad_Classification']] += 1
            by_file_type[param['SWAT_File']] += 1
        
        with open(summary_file, 'w') as f:
            f.write("# Enhanced Modular Database Summary\n\n")
            f.write(f"**Total Parameters**: {len(self.parameters)}\n\n")
            
            f.write("## Parameters by Classification\n\n")
            for classification, count in sorted(by_classification.items()):
                f.write(f"- **{classification}**: {count} parameters\n")
            
            f.write("\n## Parameters by File Type\n\n")
            for file_type, count in sorted(by_file_type.items()):
                f.write(f"- **{file_type}**: {count} parameters\n")
            
            f.write("\n## Key Features\n\n")
            f.write("- **SWAT+-Compatible Structure**: Matches original modular database format\n")
            f.write("- **File-Parameter Mapping**: Links input files to database schemas\n") 
            f.write("- **Comprehensive Coverage**: Includes core simulation, connection, and data parameters\n")
            f.write("- **Validation Support**: Provides ranges, units, and data types\n")
            f.write("- **Database Integration**: Ready for GUI generation and model coupling\n")

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Generate Enhanced SWAT+-style Modular Database')
    parser.add_argument('--json-dir', default='json_outputs', 
                       help='Directory containing FORD JSON analysis files')
    parser.add_argument('--output-dir', default='modular_database',
                       help='Output directory for modular database')
    
    args = parser.parse_args()
    
    generator = EnhancedModularDatabaseGenerator(args.json_dir, args.output_dir)
    
    # Load JSON analysis files
    generator.load_json_files()
    
    # Generate comprehensive database
    generator.generate_comprehensive_database()
    
    print("Enhanced modular database generation complete!")

if __name__ == "__main__":
    main()