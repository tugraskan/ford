#!/usr/bin/env python3
"""
Enhanced File.cio Ecosystem Analysis Tool with Better I/O Matching

This enhanced version provides better matching between files and I/O procedures
by using more sophisticated pattern matching and cross-referencing techniques.
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

class EnhancedFileCioEcosystemAnalyzer:
    """
    Enhanced analyzer with better file-to-procedure matching
    """
    
    def __init__(self, json_outputs_dir: str, src_dir: str = None):
        self.json_outputs_dir = Path(json_outputs_dir)
        self.src_dir = Path(src_dir) if src_dir else None
        
        # Core data structures
        self.file_cio_structure = {}
        self.file_variables = []
        self.input_file_module = {}
        self.file_mapping = {}
        self.file_analysis = {}
        self.io_files = {}
        
        # Enhanced matching structures
        self.file_to_procedures = defaultdict(list)  # Maps files to I/O procedures
        self.procedure_parameters = {}  # Parameters found in each procedure
        
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
            return
            
        input_module_path = self.src_dir / "input_file_module.f90"
        if not input_module_path.exists():
            return
            
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
            return False
    
    def create_file_mapping(self):
        """Create enhanced file mapping"""
        print("\n🔗 Creating enhanced file mapping...")
        
        for file_var in self.file_variables:
            files_for_var = []
            
            if file_var in self.input_file_module:
                var_files = self.input_file_module[file_var]
                for var_name, filename in var_files.items():
                    files_for_var.append(filename)
            
            self.file_mapping[file_var] = files_for_var
            print(f"   {file_var} -> {len(files_for_var)} files")
    
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
                    
                    # Analyze the I/O data to extract parameters
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
        
        # Now create enhanced mappings
        self._create_enhanced_file_procedure_mapping()
    
    def _extract_parameters_from_io(self, io_data: Dict[str, Any], procedure_name: str) -> List[Dict[str, Any]]:
        """Extract parameters from I/O analysis data"""
        parameters = []
        
        for file_key, file_info in io_data.items():
            # Skip if file_info is not a dictionary (some entries are integers)
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
                    # Clean up the column name
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
        param_name = re.sub(r'%.*', '', param_name)  # Remove derived type components
        param_name = param_name.strip()
        
        # Skip very generic or empty names
        if param_name in ['k', 'i', 'j', 'ii', 'ires', 'ich', 'name'] or len(param_name) <= 1:
            return ""
        
        return param_name
    
    def _create_enhanced_file_procedure_mapping(self):
        """Create enhanced mapping between files and I/O procedures"""
        print("\n🔍 Creating enhanced file-procedure mappings...")
        
        # Get all unique files from file.cio mapping
        all_files = set()
        for file_list in self.file_mapping.values():
            all_files.update(file_list)
        
        # Enhanced matching patterns
        for filename in all_files:
            if not filename or filename.strip() == '':
                continue
                
            matching_procedures = []
            
            # Extract base name and extension
            base_name = os.path.splitext(filename)[0]
            extension = os.path.splitext(filename)[1][1:] if '.' in filename else ''
            
            # Multiple matching strategies
            strategies = [
                # Strategy 1: Direct filename matching
                self._find_direct_filename_matches,
                # Strategy 2: Base name matching
                self._find_basename_matches,
                # Strategy 3: Extension-based matching
                self._find_extension_matches,
                # Strategy 4: Content-based matching
                self._find_content_matches
            ]
            
            for strategy in strategies:
                matches = strategy(filename, base_name, extension)
                for match in matches:
                    if match not in matching_procedures:
                        matching_procedures.append(match)
            
            self.file_to_procedures[filename] = matching_procedures
            
            if matching_procedures:
                print(f"   ✅ {filename}: {len(matching_procedures)} procedures")
            else:
                print(f"   ⚠️  {filename}: No matches found")
    
    def _find_direct_filename_matches(self, filename: str, base_name: str, extension: str) -> List[str]:
        """Find procedures that directly reference the filename"""
        matches = []
        
        # Look for procedures that contain the filename or base name
        for procedure_name, info in self.io_files.items():
            io_data = info['data']
            
            # Check if filename appears in the I/O data
            for file_key in io_data.keys():
                if filename.lower() in file_key.lower() or base_name.lower() in file_key.lower():
                    matches.append(procedure_name)
                    break
        
        return matches
    
    def _find_basename_matches(self, filename: str, base_name: str, extension: str) -> List[str]:
        """Find procedures based on base name patterns"""
        matches = []
        
        # Common patterns for procedure names
        search_patterns = [
            f"{base_name}_read",
            f"read_{base_name}",
            f"{base_name.replace('-', '_')}_read",
            f"{base_name.replace('_', '')}_read"
        ]
        
        for pattern in search_patterns:
            if pattern in self.io_files:
                matches.append(pattern)
        
        return matches
    
    def _find_extension_matches(self, filename: str, base_name: str, extension: str) -> List[str]:
        """Find procedures based on file extension"""
        matches = []
        
        # Extension-specific procedure patterns
        extension_patterns = {
            'cha': ['ch_read_hyd', 'ch_read_sed', 'ch_read_nut', 'ch_read_temp', 'ch_read'],
            'res': ['res_read_hyd', 'res_read_sed', 'res_read_nut', 'res_read'],
            'hru': ['hru_read', 'hru_lte_read'],
            'con': ['hru_read', 'ch_read', 'res_read', 'aqu_read', 'recall_read'],
            'cli': ['cli_staread', 'cli_pmeas', 'cli_tmeas', 'cli_hmeas', 'cli_wmeas'],
            'prt': ['object_read_output'],
            'sim': ['time_read'],
            'bsn': ['basin_read_prm'],
            'ini': ['soil_plant_init', 'om_water_init'],
            'del': ['dr_read'],
            'exc': ['exco_read'],
            'rec': ['recall_read'],
            'aqu': ['aqu_read'],
            'wet': ['wet_read'],
            'wro': ['water_allocation_read'],
            'lum': ['landuse_read'],
            'ops': ['mgt_read_harvops', 'mgt_read_grazeops', 'mgt_read_irrops'],
            'cal': ['cal_parm_read'],
            'sft': ['calsoft_control'],
            'cs': ['constit_db_read']
        }
        
        if extension in extension_patterns:
            for pattern in extension_patterns[extension]:
                if pattern in self.io_files:
                    matches.append(pattern)
        
        return matches
    
    def _find_content_matches(self, filename: str, base_name: str, extension: str) -> List[str]:
        """Find procedures by analyzing their content for file references"""
        matches = []
        
        # Look for procedures that might process this type of file
        for procedure_name, info in self.io_files.items():
            parameters = info['parameters']
            
            # Check if the procedure has parameters that suggest it handles this file type
            relevant_score = 0
            
            # Score based on parameter names and patterns
            for param in parameters:
                param_name = param['name'].lower()
                
                if extension == 'cha' and any(x in param_name for x in ['ch_', 'chan', 'channel']):
                    relevant_score += 1
                elif extension == 'hru' and any(x in param_name for x in ['hru', 'hydrologic']):
                    relevant_score += 1
                elif extension == 'res' and any(x in param_name for x in ['res', 'reservoir']):
                    relevant_score += 1
                elif base_name in param_name:
                    relevant_score += 2
            
            # If score is high enough, consider it a match
            if relevant_score >= 1:
                matches.append(procedure_name)
        
        return matches
    
    def _infer_parameter_type(self, param_name: str) -> str:
        """Enhanced parameter type inference"""
        param_lower = param_name.lower()
        
        int_patterns = r'(id|cnt|num|day|yr|index|nbyr|tstep)'
        real_patterns = r'(area|lat|lon|elev|rate|frac|tmp|pcp|flow|slp|len|wdt|dep|vol|mann)'
        
        if re.search(int_patterns, param_lower):
            return 'int'
        elif re.search(real_patterns, param_lower):
            return 'real'
        else:
            return 'char'
    
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
    
    def analyze_file_parameters(self, filename: str) -> Dict[str, Any]:
        """Enhanced file parameter analysis"""
        print(f"\n🔍 Analyzing file: {filename}")
        
        file_analysis = {
            'filename': filename,
            'found_io_analysis': False,
            'parameters': [],
            'io_procedures': [],
            'parameter_count': 0,
            'total_procedures': 0
        }
        
        # Get matching procedures
        matching_procedures = self.file_to_procedures.get(filename, [])
        file_analysis['total_procedures'] = len(matching_procedures)
        
        if matching_procedures:
            file_analysis['found_io_analysis'] = True
            file_analysis['io_procedures'] = matching_procedures
            
            print(f"   ✅ Found {len(matching_procedures)} matching procedures:")
            
            for proc in matching_procedures:
                print(f"      - {proc} ({self.io_files[proc]['parameter_count']} params)")
                
                # Add parameters from this procedure
                proc_params = self.io_files[proc]['parameters']
                
                # Filter out duplicate or generic parameters
                for param in proc_params:
                    if param['name'] and len(param['name']) > 1:
                        # Update classification to match the file
                        param_copy = param.copy()
                        param_copy['classification'] = self._classify_parameter(filename, param['name'])
                        file_analysis['parameters'].append(param_copy)
            
        else:
            print(f"   ⚠️  No I/O procedures found")
            # Use inferred parameters as fallback
            file_analysis['parameters'] = self._infer_common_parameters(filename)
        
        file_analysis['parameter_count'] = len(file_analysis['parameters'])
        return file_analysis
    
    def _classify_parameter(self, filename: str, param_name: str) -> str:
        """Enhanced parameter classification"""
        if 'hru' in filename.lower():
            return 'HRU'
        elif any(x in filename.lower() for x in ['channel', 'cha']):
            return 'CHANNEL'
        elif any(x in filename.lower() for x in ['res', 'reservoir']):
            return 'RESERVOIR'
        elif any(x in filename.lower() for x in ['cli', 'weather']):
            return 'CLIMATE'
        elif 'con' in filename.lower():
            return 'CONNECT'
        elif any(x in filename.lower() for x in ['sim', 'time']):
            return 'SIMULATION'
        elif any(x in filename.lower() for x in ['aqu', 'aquifer']):
            return 'AQUIFER'
        elif any(x in filename.lower() for x in ['plant', 'crop']):
            return 'PLANT'
        elif any(x in filename.lower() for x in ['soil']):
            return 'SOIL'
        elif any(x in filename.lower() for x in ['pest']):
            return 'PESTICIDE'
        elif any(x in filename.lower() for x in ['salt']):
            return 'SALT'
        elif any(x in filename.lower() for x in ['carbon', 'nut']):
            return 'NUTRIENT'
        else:
            return 'GENERAL'
    
    def _infer_common_parameters(self, filename: str) -> List[Dict[str, Any]]:
        """Infer common parameters when no I/O analysis is available"""
        common_params = []
        base_params = ['id', 'name']
        
        # File-specific parameters
        if 'hru' in filename.lower():
            base_params.extend(['area', 'lat', 'lon', 'elev'])
        elif any(x in filename.lower() for x in ['channel', 'cha']):
            base_params.extend(['len', 'wdt', 'dep', 'slp'])
        elif any(x in filename.lower() for x in ['res', 'reservoir']):
            base_params.extend(['vol', 'area_ps', 'vol_ps'])
        elif any(x in filename.lower() for x in ['cli', 'weather']):
            base_params.extend(['tmp', 'pcp', 'slr', 'hmd'])
        
        for param in base_params:
            common_params.append({
                'name': param,
                'rows': 1,
                'procedure': 'inferred',
                'data_type': self._infer_parameter_type(param),
                'classification': self._classify_parameter(filename, param)
            })
        
        return common_params
    
    def generate_comprehensive_analysis(self) -> Dict[str, Any]:
        """Generate enhanced comprehensive analysis"""
        print("\n📊 Generating enhanced ecosystem analysis...")
        
        analysis = {
            'file_cio_variables': self.file_variables,
            'file_mapping': self.file_mapping,
            'file_analyses': {},
            'total_files': 0,
            'total_parameters': 0,
            'files_with_io_analysis': 0,
            'files_without_io_analysis': 0,
            'io_procedures_used': len(self.io_files),
            'total_io_parameters': sum(info['parameter_count'] for info in self.io_files.values())
        }
        
        # Analyze each file
        all_files = set()
        for file_list in self.file_mapping.values():
            all_files.update([f for f in file_list if f and f.strip()])
        
        for filename in sorted(all_files):
            file_analysis = self.analyze_file_parameters(filename)
            analysis['file_analyses'][filename] = file_analysis
            
            analysis['total_parameters'] += file_analysis['parameter_count']
            if file_analysis['found_io_analysis']:
                analysis['files_with_io_analysis'] += 1
            else:
                analysis['files_without_io_analysis'] += 1
        
        analysis['total_files'] = len(all_files)
        return analysis
    
    def export_to_csv(self, analysis: Dict[str, Any], output_file: str = "enhanced_file_cio_ecosystem_analysis.csv"):
        """Export enhanced analysis to CSV"""
        output_path = Path(output_file)
        print(f"\n💾 Exporting enhanced analysis to {output_path}")
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # CSV Header
            writer.writerow([
                'Variable', 'Classification', 'SWAT_File', 'Text_File_Structure',
                'Line', 'Code', 'Data_Type', 'Units', 'Default', 'Min_Value', 
                'Max_Value', 'Description', 'Source_Procedure', 'Original_Name'
            ])
            
            # Write parameters
            line_counter = 1
            for filename, file_info in analysis['file_analyses'].items():
                for param in file_info['parameters']:
                    writer.writerow([
                        param['name'],
                        param['classification'],
                        filename,
                        filename,
                        line_counter,
                        'R',
                        param['data_type'],
                        self._get_parameter_units(param['name']),
                        '',  # Default
                        '',  # Min
                        '',  # Max
                        f"Parameter from {filename} via {param['procedure']}",
                        param['procedure'],
                        param.get('original_name', param['name'])
                    ])
                    line_counter += 1
        
        print(f"✅ Exported {analysis['total_parameters']} parameters from {analysis['total_files']} files")
    
    def _get_parameter_units(self, param_name: str) -> str:
        """Enhanced unit detection"""
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
            'frac': 'fraction'
        }
        
        for pattern, unit in unit_patterns.items():
            if pattern in param_lower:
                return unit
        
        return ''
    
    def print_enhanced_summary(self, analysis: Dict[str, Any]):
        """Print enhanced analysis summary"""
        print("\n" + "="*80)
        print("📋 ENHANCED FILE.CIO ECOSYSTEM ANALYSIS SUMMARY")
        print("="*80)
        
        print(f"📁 File.cio Variables: {len(analysis['file_cio_variables'])}")
        print(f"📊 I/O Procedures Available: {analysis['io_procedures_used']}")
        print(f"🔧 Total I/O Parameters Available: {analysis['total_io_parameters']}")
        
        print(f"\n📊 Analysis Results:")
        print(f"   Total Files Analyzed: {analysis['total_files']}")
        print(f"   Total Parameters Extracted: {analysis['total_parameters']}")
        print(f"   Files with I/O Analysis: {analysis['files_with_io_analysis']}")
        print(f"   Files without I/O Analysis: {analysis['files_without_io_analysis']}")
        print(f"   I/O Coverage: {analysis['files_with_io_analysis']/analysis['total_files']*100:.1f}%")
        
        print(f"\n🏆 Top Files by Parameter Count:")
        sorted_files = sorted(analysis['file_analyses'].items(), 
                            key=lambda x: x[1]['parameter_count'], reverse=True)
        
        for filename, file_info in sorted_files[:10]:
            status = "✅" if file_info['found_io_analysis'] else "⚠️"
            procs = f" ({file_info['total_procedures']} procs)" if file_info['total_procedures'] > 0 else ""
            print(f"   {status} {filename}: {file_info['parameter_count']} parameters{procs}")
        
        print("\n" + "="*80)
    
    def run_analysis(self) -> bool:
        """Run enhanced analysis"""
        print("🚀 Starting Enhanced File.cio Ecosystem Analysis")
        print("="*60)
        
        steps = [
            ("Loading file.cio structure", self.load_file_cio_structure),
            ("Loading input_file_module.f90", self.load_input_file_module),
            ("Creating file mapping", self.create_file_mapping),
            ("Scanning I/O files", self.scan_available_io_files),
        ]
        
        for step_name, step_func in steps:
            print(f"\n{step_name}...")
            if not step_func():
                return False
        
        # Generate and export analysis
        analysis = self.generate_comprehensive_analysis()
        self.export_to_csv(analysis)
        self.print_enhanced_summary(analysis)
        
        return True

def main():
    parser = argparse.ArgumentParser(
        description='Enhanced file.cio ecosystem analysis with better I/O matching')
    parser.add_argument('--json-dir', default='json_outputs',
                      help='Directory containing FORD JSON outputs')
    parser.add_argument('--src-dir', default='test_data/src',
                      help='Directory containing Fortran source files')
    parser.add_argument('--output', default='enhanced_file_cio_ecosystem_analysis.csv',
                      help='Output CSV file name')
    
    args = parser.parse_args()
    
    analyzer = EnhancedFileCioEcosystemAnalyzer(args.json_dir, args.src_dir)
    
    if analyzer.run_analysis():
        print(f"\n✅ Enhanced analysis completed successfully!")
        print(f"📄 Results saved to: {args.output}")
    else:
        print("\n❌ Enhanced analysis failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()