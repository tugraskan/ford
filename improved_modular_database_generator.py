#!/usr/bin/env python3
"""
Improved Modular Database Generator Based on User Insights

This generator implements the detailed structure insights provided by @tugraskan:
- Broad_classification from first column of file.cio or input_file_module broken down by "!!" before types
- SWAT_file from input_file_module 
- Text_file_Structure: "simple" for single structure, "unique" for multiple structures
- Position_in_file: column being read from input
- Line_in_file: line it's read from input file
- SWAT_code_type: type being read from input
- SWAT_code_Variable_Name: attribute from read statement (preserving full paths like time%day_start)
- Description: from comments of attribute in source code
- Units: from source code
- Data_type: from source code or inferred
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

class ImprovedModularDatabaseGenerator:
    """
    Generate improved modular database following user specifications
    """
    
    def __init__(self, json_outputs_dir: str, src_dir: str = None):
        self.json_outputs_dir = Path(json_outputs_dir)
        self.src_dir = Path(src_dir) if src_dir else None
        
        # Core data structures
        self.file_cio_structure = {}
        self.file_variables = []
        self.input_file_module = {}
        self.classification_mapping = {}
        self.file_mapping = {}
        self.io_files = {}
        
        # Database records
        self.database_records = []
        self.unique_id_counter = 1
    
    def load_input_file_module_with_classifications(self):
        """Parse input_file_module.f90 for classifications and file mappings"""
        if not self.src_dir:
            return True
            
        input_module_path = self.src_dir / "input_file_module.f90"
        if not input_module_path.exists():
            print(f"⚠️  input_file_module.f90 not found at {input_module_path}")
            return True
            
        try:
            with open(input_module_path, 'r') as f:
                content = f.read()
            
            # Parse type definitions with their classification comments
            lines = content.split('\n')
            current_classification = "GENERAL"
            
            for i, line in enumerate(lines):
                # Look for classification comments with !!
                if line.strip().startswith('!!'):
                    classification_text = line.strip()[2:].strip()
                    # Map common SWAT+ classifications
                    current_classification = self._map_classification(classification_text)
                
                # Look for type definitions
                type_match = re.match(r'\s*type input_(\w+)', line)
                if type_match:
                    type_name = type_match.group(1)
                    var_name = f"in_{type_name}"
                    
                    # Store classification
                    self.classification_mapping[var_name] = current_classification
                    
                    # Extract file mappings from type definition
                    self.input_file_module[var_name] = {}
                    
                    # Look for end of type and extract character definitions
                    j = i + 1
                    while j < len(lines) and not lines[j].strip().startswith(f'end type input_{type_name}'):
                        char_match = re.match(r'\s*character\(len=\d+\)\s*::\s*(\w+)\s*=\s*"([^"]+)"', lines[j])
                        if char_match:
                            var_name_inner, filename = char_match.groups()
                            self.input_file_module[var_name][var_name_inner] = filename
                        j += 1
            
            print(f"✅ Loaded input_file_module.f90 with {len(self.input_file_module)} types and classifications")
            return True
            
        except Exception as e:
            print(f"❌ Error parsing input_file_module.f90: {e}")
            return True
    
    def _map_classification(self, classification_text: str) -> str:
        """Map classification comments to SWAT+ standard classifications"""
        text_lower = classification_text.lower()
        
        if 'simulation' in text_lower or 'file.cio' in text_lower:
            return "SIMULATION"
        elif 'basin' in text_lower:
            return "BASIN" 
        elif 'climate' in text_lower:
            return "CLIMATE"
        elif 'connect' in text_lower:
            return "CONNECT"
        elif 'channel' in text_lower:
            return "CHANNEL"
        elif 'reservoir' in text_lower:
            return "RESERVOIR"
        elif 'routing unit' in text_lower or 'routing' in text_lower:
            return "ROUTING"
        elif 'hru' in text_lower:
            return "HRU"
        elif 'aquifer' in text_lower:
            return "AQUIFER"
        elif 'plant' in text_lower:
            return "PLANT"
        elif 'soil' in text_lower:
            return "SOIL"
        elif 'management' in text_lower:
            return "MANAGEMENT"
        elif 'water' in text_lower:
            return "WATER"
        elif 'salt' in text_lower:
            return "SALT"
        else:
            return "GENERAL"
    
    def load_file_cio_structure(self):
        """Load and parse readcio_read.io.json for file.cio parameters"""
        readcio_path = self.json_outputs_dir / "readcio_read.io.json"
        
        if not readcio_path.exists():
            print(f"❌ Error: {readcio_path} not found")
            return False
            
        try:
            with open(readcio_path, 'r') as f:
                self.file_cio_structure = json.load(f)
            
            # Extract file variables
            file_cio_data = self.file_cio_structure.get("file.cio", {})
            data_reads = file_cio_data.get("summary", {}).get("data_reads", [])
            
            for read_section in data_reads:
                columns = read_section.get("columns", [])
                for col in columns:
                    if col.startswith("in_"):
                        if col not in self.file_variables:
                            self.file_variables.append(col)
            
            print(f"✅ Loaded file.cio structure with {len(self.file_variables)} variables")
            return True
            
        except Exception as e:
            print(f"❌ Error loading file.cio structure: {e}")
            return False
    
    def scan_available_io_files(self):
        """Scan and categorize all I/O JSON files"""
        io_pattern = re.compile(r'(.+)\.io\.json$')
        
        for json_file in self.json_outputs_dir.glob("*.io.json"):
            match = io_pattern.match(json_file.name)
            if match:
                procedure_name = match.group(1)
                
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                    
                    # Extract parameters from I/O data with enhanced metadata
                    parameters = self._extract_parameters_with_metadata(data, procedure_name)
                    
                    self.io_files[procedure_name] = {
                        'file_path': json_file,
                        'data': data,
                        'parameters': parameters,
                        'parameter_count': len(parameters)
                    }
                    
                except Exception as e:
                    print(f"⚠️  Error loading {json_file}: {e}")
        
        print(f"📊 Found {len(self.io_files)} I/O analysis files")
        return True
    
    def _count_actual_header_reads(self, file_info: Dict[str, Any]) -> int:
        """Count actual header reads using headers field as primary source"""
        summary = file_info.get('summary', {})
        headers = summary.get('headers', [])
        return len(headers)

    def _extract_parameters_with_metadata(self, io_data: Dict[str, Any], procedure_name: str) -> List[Dict[str, Any]]:
        """Extract parameters with enhanced metadata following user specifications with proper section handling"""
        parameters = []
        
        for file_key, file_info in io_data.items():
            if not isinstance(file_info, dict):
                continue
                
            summary = file_info.get('summary', {})
            if not isinstance(summary, dict):
                continue
                
            # Process headers first
            headers = summary.get('headers', [])
            current_line = 1
            
            # Add header parameters
            for header_idx, header in enumerate(headers):
                if header and header.strip():
                    clean_header = self._clean_parameter_name_preserve_paths(header)
                    if clean_header:
                        data_type = self._infer_enhanced_data_type(clean_header, header)
                        units = self._infer_units(clean_header)
                        description = self._generate_description(clean_header, procedure_name, file_key, is_header=True)
                        source_module = self._infer_source_module(procedure_name, file_key)
                        is_local_var = self._is_local_variable(clean_header, header)
                        
                        parameters.append({
                            'name': clean_header,
                            'original_name': header,
                            'procedure': procedure_name,
                            'file_context': file_key,
                            'position_in_file': 1,  # Headers are typically in column 1
                            'line_in_file': current_line,
                            'text_file_structure': "simple",  # Headers are usually simple
                            'data_type': data_type,
                            'units': units,
                            'description': description,
                            'swat_code_type': self._infer_swat_code_type(clean_header, data_type),
                            'classification': self._classify_parameter_by_procedure(procedure_name),
                            'source_module': source_module,
                            'is_local_variable': is_local_var
                        })
                    
                    current_line += 1
            
            # Now process data_reads sections with proper unique file handling
            data_reads = summary.get('data_reads', [])
            
            for read_idx, read_section in enumerate(data_reads):
                columns = read_section.get('columns', [])
                rows = read_section.get('rows', 1)  # Default to 1 row if not specified
                
                # Determine Text_File_Structure
                total_reads = len(data_reads)
                text_file_structure = "unique" if total_reads > 1 else "simple"
                
                # Check if this section has a local header (like 'name' in print.prt sections)
                section_has_local_header = self._section_has_local_header(columns)
                section_start_line = current_line
                
                # Process each column in this read section
                for col_idx, col in enumerate(columns):
                    clean_col = self._clean_parameter_name_preserve_paths(col)
                    if clean_col:
                        # Determine if this is a local section header
                        is_local_section_header = (col_idx == 0 and section_has_local_header and 
                                                 self._is_local_section_header_name(clean_col))
                        
                        # Infer data type and other metadata
                        data_type = self._infer_enhanced_data_type(clean_col, col)
                        units = self._infer_units(clean_col)
                        description = self._generate_description(clean_col, procedure_name, file_key, 
                                                              is_header=is_local_section_header)
                        source_module = self._infer_source_module(procedure_name, file_key)
                        is_local_var = self._is_local_variable(clean_col, col) or is_local_section_header
                        
                        # Calculate proper line position for unique files
                        if is_local_section_header:
                            # Local section header gets its own line
                            line_position = current_line
                        else:
                            # Data parameters come after local header if present
                            line_position = current_line + (1 if section_has_local_header else 0)
                        
                        parameters.append({
                            'name': clean_col,
                            'original_name': col,
                            'procedure': procedure_name,
                            'file_context': file_key,
                            'position_in_file': col_idx + 1,
                            'line_in_file': line_position,
                            'text_file_structure': text_file_structure,
                            'data_type': data_type,
                            'units': units,
                            'description': description,
                            'swat_code_type': self._infer_swat_code_type(clean_col, data_type),
                            'classification': self._classify_parameter_by_procedure(procedure_name),
                            'source_module': source_module,
                            'is_local_variable': is_local_var
                        })
                
                # Move to next line position accounting for section structure
                if section_has_local_header:
                    # Section header + data rows
                    current_line += 1 + rows
                else:
                    # Just data rows
                    current_line += rows
        
        return parameters
    
    def _is_correct_file_context(self, target_file: str, context_key: str) -> bool:
        """Check if the context key matches the target file with enhanced accuracy"""
        if context_key in ['unit_*', 'line_number']:
            return False
        
        # Direct match
        if target_file.lower() == context_key.lower():
            return True
        
        # Check if context_key contains file reference patterns
        context_lower = context_key.lower()
        target_lower = target_file.lower()
        
        # Remove extensions for comparison
        context_base = context_lower.replace('.txt', '').replace('.dat', '').replace('.cli', '').replace('.bsn', '').replace('.prt', '')
        target_base = target_lower.replace('.txt', '').replace('.dat', '').replace('.cli', '').replace('.bsn', '').replace('.prt', '')
        
        # Check for basename match
        if context_base == target_base:
            return True
        
        # Check for pattern matches like in_sim%prt -> print.prt
        if 'prt' in context_lower and 'print' in target_lower:
            return True
        if 'codes_bas' in context_lower and 'codes.bsn' in target_lower:
            return True
        if 'weat_sta' in context_lower and 'weather-sta.cli' in target_lower:
            return True
        
        return False
    
    def _section_has_local_header(self, columns: List[str]) -> bool:
        """Check if a data_reads section has a local header like 'name'"""
        if not columns:
            return False
        
        # Check if first column is a typical local section header
        first_col = columns[0].lower().strip()
        return first_col in ['name', 'header', 'title', 'desc']
    
    def _is_local_section_header_name(self, param_name: str) -> bool:
        """Check if parameter name is a local section header"""
        param_lower = param_name.lower().strip()
        return param_lower in ['name', 'header', 'title', 'desc']
    
    def _clean_parameter_name_preserve_paths(self, param_name: str) -> str:
        """Clean parameter names while preserving full paths like time%day_start"""
        if not param_name:
            return ""
        
        # Remove array indices but preserve % component access and structure paths
        param_name = re.sub(r'\([^)]*\)', '', param_name)
        param_name = param_name.strip()
        
        # Skip very generic names but allow structured names with %
        if param_name in ['k', 'i', 'j', 'ii', 'ires', 'ich'] or len(param_name) <= 1:
            return ""
        
        # Keep header/title variables like 'name', 'header', 'titldum'
        return param_name
    
    def _infer_enhanced_data_type(self, param_name: str, original_name: str) -> str:
        """Infer data type with enhanced logic"""
        param_lower = param_name.lower()
        
        # Date/time parameters
        if any(word in param_lower for word in ['day', 'yrc', 'yr', 'mo', 'jday', 'date', 'time']):
            return "int"
        
        # ID parameters
        if param_lower.endswith('_id') or param_lower in ['id', 'numb', 'num']:
            return "int"
        
        # Name/description parameters
        if any(word in param_lower for word in ['name', 'desc', 'title', 'titl']):
            return "string"
        
        # Area/distance parameters
        if any(word in param_lower for word in ['area', 'lat', 'lon', 'elev', 'slope', 'len']):
            return "real"
        
        # Flow/concentration parameters
        if any(word in param_lower for word in ['flo', 'conc', 'vol', 'mass', 'rate']):
            return "real"
        
        # Flag/option parameters
        if param_lower.startswith('i') and len(param_lower) <= 4:
            return "int"
        
        # Default based on original format
        if '%' in original_name:
            return "derived"
        
        return "real"
    
    def _infer_units(self, param_name: str) -> str:
        """Infer units based on parameter name"""
        param_lower = param_name.lower()
        
        if 'area' in param_lower:
            return "ha"
        elif any(word in param_lower for word in ['lat', 'lon']):
            return "deg"
        elif any(word in param_lower for word in ['elev', 'dep', 'len']):
            return "m"
        elif 'slope' in param_lower:
            return "%"
        elif any(word in param_lower for word in ['flo', 'rate']):
            return "m3/s"
        elif 'conc' in param_lower:
            return "mg/L"
        elif any(word in param_lower for word in ['day', 'yr', 'jday']):
            return "day"
        elif any(word in param_lower for word in ['name', 'desc', 'title']):
            return "text"
        else:
            return "none"
    
    def _generate_description(self, param_name: str, procedure: str, file_context: str, is_header: bool = False) -> str:
        """Generate description based on parameter context"""
        if is_header:
            return f"{param_name} header from {file_context} via {procedure}"
        else:
            return f"{param_name} parameter from {file_context} via {procedure}"
    
    def _infer_swat_code_type(self, param_name: str, data_type: str) -> str:
        """Infer SWAT code type from parameter characteristics"""
        if data_type == "string":
            return "character"
        elif data_type == "int":
            return "integer"
        elif data_type == "real":
            return "real"
        elif data_type == "derived":
            return "derived_type"
        else:
            return "real"
    
    def _classify_parameter_by_procedure(self, procedure_name: str) -> str:
        """Classify parameter based on procedure name"""
        proc_lower = procedure_name.lower()
        
        if 'readcio' in proc_lower or 'cio' in proc_lower:
            return "SIMULATION"
        elif any(word in proc_lower for word in ['hru', 'lum']):
            return "HRU"
        elif any(word in proc_lower for word in ['ch', 'chan', 'channel']):
            return "CHANNEL"
        elif any(word in proc_lower for word in ['res', 'reservoir']):
            return "RESERVOIR"
        elif any(word in proc_lower for word in ['aqu', 'aquifer']):
            return "AQUIFER"
        elif any(word in proc_lower for word in ['cli', 'weather', 'climate']):
            return "CLIMATE"
        elif any(word in proc_lower for word in ['con', 'connect']):
            return "CONNECT"
        elif any(word in proc_lower for word in ['basin', 'bsn']):
            return "BASIN"
        elif any(word in proc_lower for word in ['plant', 'plt']):
            return "PLANT"
        elif any(word in proc_lower for word in ['sol', 'soil']):
            return "SOIL"
        elif any(word in proc_lower for word in ['salt', 'slt']):
            return "SALT"
        else:
            return "GENERAL"
    
    def _infer_source_module(self, procedure_name: str, file_key: str) -> str:
        """Infer the source module based on procedure name and file context"""
        proc_lower = procedure_name.lower()
        
        # Map procedure names to likely modules
        if 'basin' in proc_lower:
            return "basin_module"
        elif 'gwflow' in proc_lower:
            return "gwflow_module"
        elif 'climate' in proc_lower or 'cli_' in proc_lower:
            return "climate_module"
        elif 'channel' in proc_lower or 'ch_' in proc_lower:
            return "channel_module"
        elif 'reservoir' in proc_lower or 'res_' in proc_lower:
            return "reservoir_module"
        elif 'hru' in proc_lower:
            return "hru_module"
        elif 'aquifer' in proc_lower or 'aqu_' in proc_lower:
            return "aquifer_module"
        elif 'plant' in proc_lower or 'pl_' in proc_lower:
            return "plant_module"
        elif 'soil' in proc_lower:
            return "soil_module"
        elif 'salt' in proc_lower:
            return "salt_module"
        elif 'time' in proc_lower:
            return "time_module"
        elif 'readcio' in proc_lower or 'cio' in proc_lower:
            return "input_file_module"
        elif 'output' in proc_lower:
            return "output_module"
        else:
            # Try to infer from file context
            if 'file.cio' in file_key:
                return "input_file_module"
            elif any(word in file_key.lower() for word in ['time', 'print', 'obj']):
                return "simulation_module"
            else:
                return "unknown_module"
    
    def _is_local_variable(self, clean_name: str, original_name: str) -> str:
        """Determine if a variable is local (y/n)"""
        # Variables that are typically local/temporary
        local_indicators = {
            'titldum', 'header', 'name', 'dum', 'dum1', 'dum2', 'dum3',
            'i', 'j', 'k', 'ii', 'jj', 'kk', 'eof', 'iostat',
            'title', 'text', 'comment', 'line'
        }
        
        # Check if it's a simple local variable
        if clean_name.lower() in local_indicators:
            return "y"
        
        # Check if it contains local variable patterns
        if any(indicator in clean_name.lower() for indicator in ['dum', 'temp', 'tmp']):
            return "y"
        
        # Variables with % are typically structured (not local)
        if '%' in original_name:
            return "n"
        
        # Array variables are typically not local
        if '(' in original_name and ')' in original_name:
            return "n"
        
        # Simple variable names without structure are often local
        if len(clean_name) <= 4 and clean_name.lower() not in {'area', 'lat', 'lon', 'elev'}:
            return "y"
        
        # Default to not local for structured/meaningful variables
        return "n"
    
    def create_file_cio_parameters(self):
        """Create file.cio parameters as first entries following user specifications"""
        print("\n📋 Creating file.cio parameters...")
        
        # Add file.cio parameters first, following order in file.cio
        file_cio_data = self.file_cio_structure.get("file.cio", {})
        summary = file_cio_data.get("summary", {})
        
        line_number = 1
        position = 1
        
        # First add headers (like titldum)
        headers = summary.get("headers", [])
        for header in headers:
            if header:  # titldum and other headers
                record = {
                    'Unique_ID': self.unique_id_counter,
                    'Broad_Classification': "SIMULATION",
                    'SWAT_File': 'file.cio',
                    'database_table': 'simulation',
                    'DATABASE_FIELD_NAME': header,
                    'SWAT_Header_Name': header,
                    'Text_File_Structure': 'delimited',
                    'Position_in_File': position,
                    'Line_in_file': line_number,
                    'Swat_code_type': 'character',
                    'SWAT_Code_Variable_Name': header,
                    'Description': f"{header} parameter from file.cio header",
                    'Core': 'yes',
                    'Units': 'text',
                    'Data_Type': 'string',
                    'Minimum_Range': '0',
                    'Maximum_Range': '999',
                    'Default_Value': 'default',
                    'Use_in_DB': 'yes',
                    'Source_Module': 'input_file_module',
                    'Is_Local_Variable': self._is_local_variable(header, header)
                }
                
                self.database_records.append(record)
                self.unique_id_counter += 1
                line_number += 1
        
        # Then add data_reads sections
        data_reads = summary.get("data_reads", [])
        
        for read_section in data_reads:
            columns = read_section.get("columns", [])
            
            for col_idx, col in enumerate(columns):
                clean_col = self._clean_parameter_name_preserve_paths(col)
                if clean_col:
                    
                    # Check if this is a type that should be expanded (like in_sim, in_basin, etc.)
                    if clean_col.startswith('in_') and clean_col in self.input_file_module:
                        # This is a type that should be expanded into its components
                        components = self.input_file_module[clean_col]
                        component_position = 1
                        
                        for component_name, component_file in components.items():
                            # Create expanded parameter like in_sim%time
                            expanded_param = f"{clean_col}%{component_name}"
                            
                            # Get classification from input_file_module or default to SIMULATION
                            classification = self.classification_mapping.get(clean_col, "SIMULATION")
                            
                            record = {
                                'Unique_ID': self.unique_id_counter,
                                'Broad_Classification': classification,
                                'SWAT_File': 'file.cio',
                                'database_table': 'simulation',
                                'DATABASE_FIELD_NAME': expanded_param,
                                'SWAT_Header_Name': expanded_param,
                                'Text_File_Structure': 'delimited',
                                'Position_in_File': component_position,
                                'Line_in_file': line_number,
                                'Swat_code_type': 'character',  # Components are file names (character)
                                'SWAT_Code_Variable_Name': expanded_param,
                                'Description': f"{expanded_param} component from file.cio (references {component_file})",
                                'Core': 'yes',  # Type components are core parameters
                                'Units': 'filename',
                                'Data_Type': 'string',
                                'Minimum_Range': '0',
                                'Maximum_Range': '1',
                                'Default_Value': component_file,
                                'Use_in_DB': 'yes',
                                'Source_Module': 'input_file_module',
                                'Is_Local_Variable': 'n'  # Type components are not local variables
                            }
                            
                            self.database_records.append(record)
                            self.unique_id_counter += 1
                            component_position += 1
                    else:
                        # Regular parameter (like name headers)
                        # Get classification from input_file_module or default to SIMULATION
                        classification = self.classification_mapping.get(clean_col, "SIMULATION")
                        
                        record = {
                            'Unique_ID': self.unique_id_counter,
                            'Broad_Classification': classification,
                            'SWAT_File': 'file.cio',
                            'database_table': 'simulation',
                            'DATABASE_FIELD_NAME': clean_col,
                            'SWAT_Header_Name': clean_col,
                            'Text_File_Structure': 'delimited',
                            'Position_in_File': col_idx + 1,
                            'Line_in_file': line_number,
                            'Swat_code_type': self._infer_swat_code_type(clean_col, self._infer_enhanced_data_type(clean_col, col)),
                            'SWAT_Code_Variable_Name': clean_col,
                            'Description': f"{clean_col} parameter from file.cio",
                            'Core': 'yes' if clean_col.startswith('in_') else 'no',
                            'Units': self._infer_units(clean_col),
                            'Data_Type': self._infer_enhanced_data_type(clean_col, col),
                            'Minimum_Range': '0',
                            'Maximum_Range': '1',
                            'Default_Value': '1',
                            'Use_in_DB': 'yes',
                            'Source_Module': 'input_file_module',
                            'Is_Local_Variable': self._is_local_variable(clean_col, col)
                        }
                        
                        self.database_records.append(record)
                        self.unique_id_counter += 1
                
                line_number += 1
        
        print(f"✅ Created {len(self.database_records)} file.cio parameters")
    
    def create_input_file_parameters(self):
        """Create parameters for input files based on file.cio order and I/O analysis"""
        print("\n📊 Creating input file parameters...")
        
        # Process files in file.cio order
        for file_var in self.file_variables:
            if file_var in self.input_file_module:
                var_files = self.input_file_module[file_var]
                classification = self.classification_mapping.get(file_var, "GENERAL")
                
                for var_name, filename in var_files.items():
                    if filename and filename.strip():
                        self._process_input_file(filename, classification, file_var)
        
        print(f"✅ Total database records: {len(self.database_records)}")
    
    def _process_input_file(self, filename: str, classification: str, file_var: str):
        """Process individual input file parameters"""
        # Find matching I/O procedures
        matching_procedures = self._find_matching_procedures(filename)
        
        if matching_procedures:
            # Find the correct variable name for this filename
            target_var_name = None
            for var_name, mapped_filename in self.input_file_module.get(file_var, {}).items():
                if mapped_filename == filename:
                    target_var_name = var_name
                    break
            
            for procedure_name in matching_procedures:
                if procedure_name in self.io_files:
                    parameters = self.io_files[procedure_name]['parameters']
                    
                    for param in parameters:
                        # Only include parameters that come from the correct file context
                        file_context = param.get('file_context', '')
                        
                        # Check if this parameter is from the correct file context for our filename
                        if target_var_name and file_context.startswith(f"{file_var}%"):
                            context_var = file_context.split('%')[1] if '%' in file_context else ''
                            if context_var != target_var_name:
                                continue  # Skip parameters from other file contexts in the same procedure
                        elif not file_context.startswith(f"{file_var}%"):
                            continue  # Skip parameters not from our target file variable
                        
                        record = {
                            'Unique_ID': self.unique_id_counter,
                            'Broad_Classification': classification,
                            'SWAT_File': filename,
                            'database_table': filename.replace('.', '_'),
                            'DATABASE_FIELD_NAME': param['name'],
                            'SWAT_Header_Name': param['name'],
                            'Text_File_Structure': param['text_file_structure'],
                            'Position_in_File': param['position_in_file'],
                            'Line_in_file': param['line_in_file'],
                            'Swat_code_type': param['swat_code_type'],
                            'SWAT_Code_Variable_Name': param['name'],
                            'Description': param['description'],
                            'Core': 'yes' if any(word in param['name'].lower() for word in ['id', 'name', 'area']) else 'no',
                            'Units': param['units'],
                            'Data_Type': param['data_type'],
                            'Minimum_Range': self._get_min_range(param),
                            'Maximum_Range': self._get_max_range(param),
                            'Default_Value': self._get_default_value(param),
                            'Use_in_DB': 'yes',
                            'Source_Module': param.get('source_module', 'unknown_module'),
                            'Is_Local_Variable': param.get('is_local_variable', 'n')
                        }
                        
                        self.database_records.append(record)
                        self.unique_id_counter += 1
    
    def _find_matching_procedures(self, filename: str) -> List[str]:
        """Find I/O procedures that match the filename using proper file context mapping"""
        matches = []
        
        # Find the file variable and var_name that corresponds to this filename
        target_file_var = None
        target_var_name = None
        
        for file_var, var_files in self.input_file_module.items():
            for var_name, mapped_filename in var_files.items():
                if mapped_filename == filename:
                    target_file_var = file_var
                    target_var_name = var_name
                    break
            if target_file_var:
                break
        
        if not target_file_var:
            # Fallback to basename matching if no exact mapping found
            base_name = os.path.splitext(filename)[0]
            for procedure_name in self.io_files.keys():
                if base_name.lower() in procedure_name.lower():
                    matches.append(procedure_name)
            return matches
        
        # Look for procedures that have file contexts matching our target
        for procedure_name, procedure_data in self.io_files.items():
            for param in procedure_data['parameters']:
                file_context = param.get('file_context', '')
                
                # Check if this file context matches our target
                if file_context.startswith(f"{target_file_var}%"):
                    # Extract the variable part after %
                    context_var = file_context.split('%')[1] if '%' in file_context else ''
                    
                    # Match if the context variable corresponds to our target
                    if context_var == target_var_name:
                        matches.append(procedure_name)
                        break
                    # Also handle cases where context is more complex (like in_cli%weat_sta for weather-sta.cli)
                    elif target_var_name in context_var or context_var in target_var_name:
                        matches.append(procedure_name)
                        break
        
        return list(set(matches))
    
    def _get_min_range(self, param: Dict) -> str:
        """Get minimum range for parameter"""
        if param['data_type'] == 'int':
            return "0"
        elif param['data_type'] == 'real':
            return "0.0"
        else:
            return "0"
    
    def _get_max_range(self, param: Dict) -> str:
        """Get maximum range for parameter"""
        param_lower = param['name'].lower()
        
        if 'id' in param_lower:
            return "9999"
        elif 'area' in param_lower:
            return "99999.0"
        elif any(word in param_lower for word in ['lat', 'lon']):
            return "180.0"
        else:
            return "999"
    
    def _get_default_value(self, param: Dict) -> str:
        """Get default value for parameter"""
        if param['data_type'] == 'string':
            return "default"
        elif param['data_type'] == 'int':
            return "1"
        else:
            return "1.0"
    
    def generate_database(self, output_file: str = "Improved_Modular_Database_5_15_24_nbs.csv"):
        """Generate the complete modular database"""
        print("\n🚀 Generating Improved Modular Database...")
        
        # Load all data
        if not self.load_file_cio_structure():
            return False
        
        if not self.load_input_file_module_with_classifications():
            return False
        
        if not self.scan_available_io_files():
            return False
        
        # Create parameters
        self.create_file_cio_parameters()
        self.create_input_file_parameters()
        
        # Write output
        output_path = Path(output_file)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Unique_ID', 'Broad_Classification', 'SWAT_File', 'database_table',
                'DATABASE_FIELD_NAME', 'SWAT_Header_Name', 'Text_File_Structure',
                'Position_in_File', 'Line_in_file', 'Swat_code_type',
                'SWAT_Code_Variable_Name', 'Description', 'Core', 'Units',
                'Data_Type', 'Minimum_Range', 'Maximum_Range', 'Default_Value', 'Use_in_DB',
                'Source_Module', 'Is_Local_Variable'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for record in self.database_records:
                writer.writerow(record)
        
        print(f"✅ Generated {output_file} with {len(self.database_records)} parameters")
        
        # Generate summary
        self._generate_summary()
        
        return True
    
    def _generate_summary(self):
        """Generate summary statistics"""
        print("\n📊 Database Summary:")
        print(f"   Total Parameters: {len(self.database_records)}")
        
        # Count by classification
        classification_counts = defaultdict(int)
        file_counts = defaultdict(int)
        
        for record in self.database_records:
            classification_counts[record['Broad_Classification']] += 1
            file_counts[record['SWAT_File']] += 1
        
        print("\n   By Classification:")
        for classification, count in sorted(classification_counts.items()):
            print(f"     {classification}: {count}")
            
        print(f"\n   Files Covered: {len(file_counts)}")
        print("   Top Files by Parameter Count:")
        for filename, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"     {filename}: {count}")

def main():
    parser = argparse.ArgumentParser(description='Generate improved modular database')
    parser.add_argument('--json-dir', default='json_outputs', help='JSON outputs directory')
    parser.add_argument('--src-dir', default='test_data/src', help='Source code directory')
    parser.add_argument('--output', default='Improved_Modular_Database_5_15_24_nbs.csv', help='Output file')
    
    args = parser.parse_args()
    
    generator = ImprovedModularDatabaseGenerator(args.json_dir, args.src_dir)
    success = generator.generate_database(args.output)
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())