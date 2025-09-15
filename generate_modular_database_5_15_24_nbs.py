#!/usr/bin/env python3
"""
Generate Modular Database_5_15_24_nbs Format from File.cio Ecosystem Analysis

This script transforms the comprehensive file.cio ecosystem analysis tool logic
to generate the original SWAT+ Modular Database format (Modular Database_5_15_24_nbs).
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

class ModularDatabase5_15_24_NBSGenerator:
    """
    Generate the original SWAT+ Modular Database format using file.cio ecosystem analysis logic
    """
    
    def __init__(self, json_outputs_dir: str, src_dir: str = None):
        self.json_outputs_dir = Path(json_outputs_dir)
        self.src_dir = Path(src_dir) if src_dir else None
        
        # Core data structures
        self.file_cio_structure = {}
        self.file_variables = []
        self.input_file_module = {}
        self.file_mapping = {}
        self.io_files = {}
        self.file_to_procedures = defaultdict(list)
        self.procedure_parameters = {}
        
        # Modular database records
        self.database_records = []
        self.unique_id_counter = 1
    
    def load_file_cio_structure(self):
        """Load and parse readcio_read.io.json"""
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
    
    def load_input_file_module(self):
        """Parse input_file_module.f90 for file mappings"""
        if not self.src_dir:
            return True
            
        input_module_path = self.src_dir / "input_file_module.f90"
        if not input_module_path.exists():
            print(f"⚠️  input_file_module.f90 not found at {input_module_path}")
            return True
            
        try:
            with open(input_module_path, 'r') as f:
                content = f.read()
            
            # Parse type definitions
            type_pattern = r'type input_(\w+).*?end type input_\w+'
            matches = re.findall(type_pattern, content, re.DOTALL)
            
            for type_name in matches:
                type_section = re.search(rf'type input_{type_name}.*?end type input_{type_name}', content, re.DOTALL)
                if type_section:
                    section_content = type_section.group(0)
                    char_pattern = r'character\(len=\d+\)\s*::\s*(\w+)\s*=\s*"([^"]+)"'
                    char_matches = re.findall(char_pattern, section_content)
                    
                    self.input_file_module[f"in_{type_name}"] = {}
                    for var_name, filename in char_matches:
                        self.input_file_module[f"in_{type_name}"][var_name] = filename
            
            print(f"✅ Loaded input_file_module.f90 with {len(self.input_file_module)} types")
            return True
            
        except Exception as e:
            print(f"❌ Error parsing input_file_module.f90: {e}")
            return True  # Don't fail if this is missing
    
    def create_file_mapping(self):
        """Create file mapping from file.cio variables to actual files"""
        print("\n🔗 Creating file mapping...")
        
        for file_var in self.file_variables:
            files_for_var = []
            
            # Use input_file_module mapping if available
            if file_var in self.input_file_module:
                var_files = self.input_file_module[file_var]
                for var_name, filename in var_files.items():
                    if filename and filename.strip():
                        files_for_var.append(filename)
            
            # If no mapping found, infer from variable name
            if not files_for_var:
                inferred_files = self._infer_files_from_variable(file_var)
                files_for_var.extend(inferred_files)
            
            self.file_mapping[file_var] = files_for_var
            print(f"   {file_var} -> {files_for_var}")
        
        print(f"✅ Created file mapping for {len(self.file_mapping)} variables")
    
    def _infer_files_from_variable(self, file_var: str) -> List[str]:
        """Infer likely filenames from file.cio variable names"""
        var_name = file_var.replace("in_", "")
        
        # Common patterns for SWAT+ file naming
        inferred_files = []
        
        if var_name == "sim":
            inferred_files = ["time.sim", "print.prt", "object.prt"]
        elif var_name == "basin":
            inferred_files = ["parameters.bsn"]  
        elif var_name == "cli":
            inferred_files = ["weather-sta.cli", "weather-wgn.cli"]
        elif var_name == "con":
            inferred_files = ["hru.con", "channel.con", "reservoir.con", "aquifer.con"]
        elif var_name == "hyd":
            inferred_files = ["hydrology.hyd", "topography.hyd", "field.fld"]
        elif var_name == "mgt":
            inferred_files = ["management.sch", "fertilizer.frt", "pesticide.pst"]
        elif var_name == "cli_sta":
            inferred_files = ["weather-sta.cli"]
        elif var_name == "cli_wgn":
            inferred_files = ["weather-wgn.cli"]
        elif var_name == "plant":
            inferred_files = ["plants.plt", "fertilizer.frt"]
        elif var_name == "soil":
            inferred_files = ["soils.sol"]
        elif var_name == "nut":
            inferred_files = ["nutrients.sol"]
        elif var_name == "tillage":
            inferred_files = ["tillage.til"]
        elif var_name == "pest":
            inferred_files = ["pesticide.pst"]
        elif var_name == "path":
            inferred_files = ["pathogen.pth"]
        elif var_name == "hmet":
            inferred_files = ["hmet.met"]
        elif var_name == "salt":
            inferred_files = ["salt.slt"]
        elif var_name == "urban":
            inferred_files = ["urban.urb"]
        elif var_name == "septic":
            inferred_files = ["septic.sep"]
        elif var_name == "snow":
            inferred_files = ["snow.sno"]
        
        return inferred_files
    
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
                    
                    # Extract parameters from I/O data
                    parameters = self._extract_parameters_from_io(data, procedure_name)
                    
                    self.io_files[procedure_name] = {
                        'file_path': json_file,
                        'data': data,
                        'parameters': parameters,
                        'parameter_count': len(parameters)
                    }
                    
                except Exception as e:
                    print(f"⚠️  Error loading {json_file}: {e}")
        
        print(f"📊 Found {len(self.io_files)} I/O analysis files")
        
        # Create file-procedure mappings
        self._create_file_procedure_mapping()
        return True
    
    def _extract_parameters_from_io(self, io_data: Dict[str, Any], procedure_name: str) -> List[Dict[str, Any]]:
        """Extract parameters from I/O analysis data"""
        parameters = []
        
        for file_key, file_info in io_data.items():
            if not isinstance(file_info, dict):
                continue
                
            summary = file_info.get('summary', {})
            if not isinstance(summary, dict):
                continue
                
            data_reads = summary.get('data_reads', [])
            
            for read_section in data_reads:
                columns = read_section.get('columns', [])
                rows = read_section.get('rows', 1)
                
                for col in columns:
                    clean_col = self._clean_parameter_name(col)
                    if clean_col:
                        parameters.append({
                            'name': clean_col,
                            'original_name': col,
                            'rows': rows,
                            'procedure': procedure_name,
                            'file_context': file_key,
                            'data_type': self._infer_parameter_type(clean_col),
                            'classification': self._classify_parameter_by_procedure(procedure_name)
                        })
        
        return parameters
    
    def _clean_parameter_name(self, param_name: str) -> str:
        """Clean parameter names to extract meaningful variable names"""
        if not param_name:
            return ""
        
        # Remove array indices and complex expressions
        param_name = re.sub(r'\([^)]*\)', '', param_name)
        param_name = re.sub(r'%.*', '', param_name)
        param_name = param_name.strip()
        
        # Skip very generic or empty names
        if param_name in ['k', 'i', 'j', 'ii', 'ires', 'ich', 'name'] or len(param_name) <= 1:
            return ""
        
        return param_name
    
    def _create_file_procedure_mapping(self):
        """Create mapping between files and I/O procedures"""
        print("\n🔍 Creating file-procedure mappings...")
        
        # Get all unique files from file.cio mapping
        all_files = set()
        for file_list in self.file_mapping.values():
            all_files.update([f for f in file_list if f and f.strip()])
        
        for filename in all_files:
            matching_procedures = []
            
            # Extract base name and extension
            base_name = os.path.splitext(filename)[0]
            extension = os.path.splitext(filename)[1][1:] if '.' in filename else ''
            
            # Find matching procedures
            matching_procedures.extend(self._find_direct_matches(filename, base_name))
            matching_procedures.extend(self._find_extension_matches(filename, extension))
            matching_procedures.extend(self._find_pattern_matches(filename, base_name))
            
            # Remove duplicates
            matching_procedures = list(set(matching_procedures))
            self.file_to_procedures[filename] = matching_procedures
            
            if matching_procedures:
                print(f"   ✅ {filename}: {len(matching_procedures)} procedures")
            else:
                print(f"   ⚠️  {filename}: No matches found")
    
    def _find_direct_matches(self, filename: str, base_name: str) -> List[str]:
        """Find procedures that directly reference the filename"""
        matches = []
        
        for procedure_name, info in self.io_files.items():
            io_data = info['data']
            
            for file_key in io_data.keys():
                if (filename.lower() in file_key.lower() or 
                    base_name.lower() in file_key.lower()):
                    matches.append(procedure_name)
                    break
        
        return matches
    
    def _find_extension_matches(self, filename: str, extension: str) -> List[str]:
        """Find procedures based on file extension patterns"""
        extension_patterns = {
            'cha': ['ch_read_hyd', 'ch_read_sed', 'ch_read_nut'],
            'res': ['res_read_hyd', 'res_read_sed', 'res_read_nut'], 
            'hru': ['hru_read', 'hru_lte_read'],
            'con': ['hru_read', 'ch_read', 'res_read', 'aqu_read'],
            'cli': ['cli_staread', 'cli_pmeas', 'cli_tmeas'],
            'prt': ['object_read_output'],
            'sim': ['time_read'],
            'bsn': ['basin_read_prm'],
            'plt': ['pl_read'],
            'sol': ['soil_read'],
            'til': ['tillage_read'],
            'pst': ['pest_read'],
            'frt': ['fert_read'],
            'urb': ['urban_read'],
            'wro': ['water_allocation_read'],
            'dtl': ['decision_table_read']
        }
        
        matches = []
        if extension in extension_patterns:
            for pattern in extension_patterns[extension]:
                if pattern in self.io_files:
                    matches.append(pattern)
        
        return matches
    
    def _find_pattern_matches(self, filename: str, base_name: str) -> List[str]:
        """Find procedures using naming patterns"""
        search_patterns = [
            f"{base_name}_read",
            f"read_{base_name}",
            f"{base_name.replace('-', '_')}_read",
            f"{base_name.replace('_', '')}_read"
        ]
        
        matches = []
        for pattern in search_patterns:
            if pattern in self.io_files:
                matches.append(pattern)
        
        return matches
    
    def _infer_parameter_type(self, param_name: str) -> str:
        """Infer parameter data type"""
        param_lower = param_name.lower()
        
        int_patterns = r'(id|cnt|num|day|yr|index|nbyr|tstep|numb)'
        real_patterns = r'(area|lat|lon|elev|rate|frac|tmp|pcp|flow|slp|len|wdt|dep|vol|mann)'
        
        if re.search(int_patterns, param_lower):
            return 'integer'
        elif re.search(real_patterns, param_lower):
            return 'real'
        else:
            return 'string'
    
    def _classify_parameter_by_procedure(self, procedure_name: str) -> str:
        """Classify parameters based on procedure name"""
        proc_lower = procedure_name.lower()
        
        if any(x in proc_lower for x in ['hru', 'hydrologic']):
            return 'HRU'
        elif any(x in proc_lower for x in ['ch_', 'chan', 'channel']):
            return 'CHANNEL'
        elif any(x in proc_lower for x in ['res', 'reservoir']):
            return 'RESERVOIR'
        elif any(x in proc_lower for x in ['cli', 'weather', 'wgn']):
            return 'CLIMATE'
        elif any(x in proc_lower for x in ['con', 'connect']):
            return 'CONNECT'
        elif any(x in proc_lower for x in ['sim', 'time']):
            return 'SIMULATION'
        elif any(x in proc_lower for x in ['aqu', 'aquifer']):
            return 'AQUIFER'
        elif any(x in proc_lower for x in ['plant', 'crop']):
            return 'PLANT'
        elif any(x in proc_lower for x in ['soil']):
            return 'SOIL'
        elif any(x in proc_lower for x in ['pest', 'pesticide']):
            return 'PESTICIDE'
        elif any(x in proc_lower for x in ['salt']):
            return 'SALT'
        elif any(x in proc_lower for x in ['carbon', 'nutrient']):
            return 'NUTRIENT'
        else:
            return 'GENERAL'
    
    def generate_database_records(self):
        """Generate database records in Modular Database_5_15_24_nbs format"""
        print("\n📊 Generating modular database records...")
        
        # Get all files from mapping
        all_files = set()
        for file_list in self.file_mapping.values():
            all_files.update([f for f in file_list if f and f.strip()])
        
        for filename in sorted(all_files):
            self._process_file_for_records(filename)
        
        print(f"✅ Generated {len(self.database_records)} database records")
        return True
    
    def _process_file_for_records(self, filename: str):
        """Process a single file to generate database records"""
        # Get matching procedures
        matching_procedures = self.file_to_procedures.get(filename, [])
        
        if matching_procedures:
            # Use I/O analysis data
            for proc in matching_procedures:
                if proc in self.io_files:
                    parameters = self.io_files[proc]['parameters']
                    for param in parameters:
                        self._create_database_record(filename, param, proc)
        else:
            # Use inferred parameters
            inferred_params = self._infer_common_parameters(filename)
            for param in inferred_params:
                self._create_database_record(filename, param, 'inferred')
    
    def _create_database_record(self, filename: str, param: Dict[str, Any], procedure: str):
        """Create a database record in the target format"""
        
        # Calculate position and line
        position = len([r for r in self.database_records if r['SWAT_File'] == filename]) + 1
        line = position
        
        # Create database table name from filename
        database_table = os.path.splitext(filename)[0].replace('.', '_').replace('-', '_')
        
        # Create swat code type
        swat_code_type = database_table
        
        # Get classification
        classification = param.get('classification', self._classify_parameter_by_filename(filename))
        
        # Get units
        units = self._get_parameter_units(param['name'])
        
        # Get ranges and defaults
        min_range, max_range, default_value = self._get_parameter_ranges(param['name'], param['data_type'])
        
        record = {
            'Unique_ID': self.unique_id_counter,
            'Broad_Classification': classification,
            'SWAT_File': filename,
            'database_table': database_table,
            'DATABASE_FIELD_NAME': param['name'],
            'SWAT_Header_Name': param['name'],
            'Text_File_Structure': 'delimited',
            'Position_in_File': position,
            'Line_in_file': line,
            'Swat_code_type': swat_code_type,
            'SWAT_Code_Variable_Name': param['name'],
            'Description': f"{param['name']} parameter from {filename} via {procedure}",
            'Core': 'no',
            'Units': units,
            'Data_Type': param['data_type'],
            'Minimum_Range': min_range,
            'Maximum_Range': max_range,
            'Default_Value': default_value,
            'Use_in_DB': 'yes'
        }
        
        self.database_records.append(record)
        self.unique_id_counter += 1
    
    def _classify_parameter_by_filename(self, filename: str) -> str:
        """Classify parameter based on filename"""
        filename_lower = filename.lower()
        
        if any(x in filename_lower for x in ['hru', 'hydrologic']):
            return 'HRU'
        elif any(x in filename_lower for x in ['channel', 'cha']):
            return 'CHANNEL'
        elif any(x in filename_lower for x in ['res', 'reservoir']):
            return 'RESERVOIR'
        elif any(x in filename_lower for x in ['cli', 'weather']):
            return 'CLIMATE'
        elif 'con' in filename_lower:
            return 'CONNECT'
        elif any(x in filename_lower for x in ['sim', 'time', 'prt']):
            return 'SIMULATION'
        elif any(x in filename_lower for x in ['aqu', 'aquifer']):
            return 'AQUIFER'
        elif any(x in filename_lower for x in ['plant', 'plt']):
            return 'PLANT'
        elif any(x in filename_lower for x in ['soil', 'sol']):
            return 'SOIL'
        elif any(x in filename_lower for x in ['pest', 'pst']):
            return 'PESTICIDE'
        elif any(x in filename_lower for x in ['salt', 'slt']):
            return 'SALT'
        elif any(x in filename_lower for x in ['carbon', 'nut']):
            return 'NUTRIENT'
        elif any(x in filename_lower for x in ['urban', 'urb']):
            return 'URBAN'
        elif any(x in filename_lower for x in ['basin', 'bsn']):
            return 'BASIN'
        elif any(x in filename_lower for x in ['management', 'mgt']):
            return 'MANAGEMENT'
        else:
            return 'GENERAL'
    
    def _infer_common_parameters(self, filename: str) -> List[Dict[str, Any]]:
        """Infer common parameters when no I/O analysis is available"""
        common_params = []
        base_params = ['titldum', 'header']  # Common SWAT+ file headers
        
        # Add file-specific parameters based on filename
        if any(x in filename.lower() for x in ['hru', 'hydrologic']):
            base_params.extend(['id', 'name', 'area', 'lat', 'lon', 'elev'])
        elif any(x in filename.lower() for x in ['channel', 'cha']):
            base_params.extend(['id', 'name', 'len', 'wdt', 'dep', 'slp'])
        elif any(x in filename.lower() for x in ['res', 'reservoir']):
            base_params.extend(['id', 'name', 'vol', 'area_ps', 'vol_ps'])
        elif any(x in filename.lower() for x in ['cli', 'weather']):
            base_params.extend(['station_name', 'tmp', 'pcp', 'slr', 'hmd'])
        elif any(x in filename.lower() for x in ['plant', 'plt']):
            base_params.extend(['name', 'typ', 'lai', 'bio_e', 'harv_idx'])
        elif any(x in filename.lower() for x in ['soil', 'sol']):
            base_params.extend(['name', 'layer', 'dep', 'bd', 'awc', 'k'])
        elif 'con' in filename.lower():
            base_params.extend(['name', 'gis_id', 'area'])
        else:
            base_params.extend(['name', 'id'])
        
        for param_name in base_params:
            common_params.append({
                'name': param_name,
                'data_type': self._infer_parameter_type(param_name),
                'classification': self._classify_parameter_by_filename(filename)
            })
        
        return common_params
    
    def _get_parameter_units(self, param_name: str) -> str:
        """Get units for parameter"""
        param_lower = param_name.lower()
        
        unit_patterns = {
            'area': 'ha',
            'lat': 'deg',
            'lon': 'deg', 
            'elev': 'm',
            'len': 'm',
            'wdt': 'm',
            'dep': 'm',
            'vol': 'm3',
            'tmp': 'degC',
            'pcp': 'mm',
            'flow': 'm3/s',
            'slp': '%',
            'mann': 's/m^(1/3)',
            'rate': '1/day',
            'frac': 'fraction',
            'lai': 'm2/m2',
            'bd': 'g/cm3',
            'awc': 'mm/mm',
            'k': 'mm/hr'
        }
        
        for pattern, unit in unit_patterns.items():
            if pattern in param_lower:
                return unit
        
        return 'none'
    
    def _get_parameter_ranges(self, param_name: str, data_type: str) -> Tuple[str, str, str]:
        """Get parameter ranges and default values"""
        param_lower = param_name.lower()
        
        # Default ranges by data type
        if data_type == 'integer':
            min_val, max_val, default = '1', '9999', '1'
        elif data_type == 'real':
            min_val, max_val, default = '0', '999', '0'
        else:  # string
            min_val, max_val, default = '0', '999', 'default'
        
        # Special cases for common parameters
        if param_name in ['titldum']:
            default = '0'
        elif param_name in ['header']:
            default = 'default'
        elif 'id' in param_lower:
            min_val, max_val, default = '1', '9999', '1'
        elif 'area' in param_lower:
            min_val, max_val, default = '0.01', '100000', '1'
        elif param_lower in ['lat', 'lon']:
            min_val, max_val, default = '-90', '90', '0'
        
        return min_val, max_val, default
    
    def export_to_csv(self, output_file: str = "Modular_Database_5_15_24_nbs.csv"):
        """Export to Modular Database_5_15_24_nbs format"""
        output_path = Path(output_file)
        print(f"\n💾 Exporting to {output_path}")
        
        # Column headers for Modular Database_5_15_24_nbs format
        headers = [
            'Unique_ID', 'Broad_Classification', 'SWAT_File', 'database_table',
            'DATABASE_FIELD_NAME', 'SWAT_Header_Name', 'Text_File_Structure',
            'Position_in_File', 'Line_in_file', 'Swat_code_type',
            'SWAT_Code_Variable_Name', 'Description', 'Core', 'Units',
            'Data_Type', 'Minimum_Range', 'Maximum_Range', 'Default_Value',
            'Use_in_DB'
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for record in self.database_records:
                writer.writerow(record)
        
        print(f"✅ Exported {len(self.database_records)} records to Modular Database_5_15_24_nbs format")
    
    def print_summary(self):
        """Print generation summary"""
        print("\n" + "="*80)
        print("📋 MODULAR DATABASE_5_15_24_NBS GENERATION SUMMARY") 
        print("="*80)
        
        # Count by classification
        classification_counts = defaultdict(int)
        file_counts = defaultdict(int)
        
        for record in self.database_records:
            classification_counts[record['Broad_Classification']] += 1
            file_counts[record['SWAT_File']] += 1
        
        print(f"📊 Total Records: {len(self.database_records)}")
        print(f"📁 Total Files: {len(file_counts)}")
        print(f"🔢 File Variables from file.cio: {len(self.file_variables)}")
        print(f"⚡ I/O Procedures Used: {len(self.io_files)}")
        
        print(f"\n🏷️  Classification Breakdown:")
        for classification, count in sorted(classification_counts.items()):
            print(f"   {classification}: {count} parameters")
        
        print(f"\n🏆 Top Files by Parameter Count:")
        sorted_files = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)
        for filename, count in sorted_files[:15]:
            print(f"   {filename}: {count} parameters")
        
        print("\n" + "="*80)
    
    def run(self) -> bool:
        """Run the complete generation process"""
        print("🚀 Starting Modular Database_5_15_24_nbs Generation")
        print("="*60)
        
        steps = [
            ("Loading file.cio structure", self.load_file_cio_structure),
            ("Loading input_file_module.f90", self.load_input_file_module),
            ("Creating file mapping", self.create_file_mapping),
            ("Scanning I/O files", self.scan_available_io_files),
            ("Generating database records", self.generate_database_records),
        ]
        
        for step_name, step_func in steps:
            print(f"\n{step_name}...")
            try:
                result = step_func()
                if result is False:
                    print(f"❌ Step '{step_name}' failed")
                    return False
            except Exception as e:
                print(f"❌ Step '{step_name}' failed with error: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        try:
            # Export and summarize
            self.export_to_csv()
            self.print_summary()
        except Exception as e:
            print(f"❌ Export/summary failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True

def main():
    parser = argparse.ArgumentParser(
        description='Generate Modular Database_5_15_24_nbs format from file.cio ecosystem analysis')
    parser.add_argument('--json-dir', default='json_outputs',
                      help='Directory containing FORD JSON outputs')
    parser.add_argument('--src-dir', default='test_data/src',
                      help='Directory containing Fortran source files')
    parser.add_argument('--output', default='Modular_Database_5_15_24_nbs.csv',
                      help='Output CSV file name')
    
    args = parser.parse_args()
    
    generator = ModularDatabase5_15_24_NBSGenerator(args.json_dir, args.src_dir)
    
    if generator.run():
        print(f"\n✅ Modular Database_5_15_24_nbs generation completed successfully!")
        print(f"📄 Results saved to: {args.output}")
    else:
        print("\n❌ Generation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()