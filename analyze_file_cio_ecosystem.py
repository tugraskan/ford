#!/usr/bin/env python3
"""
Comprehensive File.cio Ecosystem Analysis Tool

This tool analyzes the file.cio structure to:
1. Identify all variables being read from file.cio
2. Use those variables as filename references
3. Find where those files are used/read in the code or FORD outputs
4. List all attributes being read from each file (similar to modular spreadsheet)

Usage:
    python analyze_file_cio_ecosystem.py --json-dir json_outputs --src-dir test_data/src
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

class FileCioEcosystemAnalyzer:
    """
    Analyzes the complete file.cio ecosystem and traces all referenced files
    """
    
    def __init__(self, json_outputs_dir: str, src_dir: str = None):
        self.json_outputs_dir = Path(json_outputs_dir)
        self.src_dir = Path(src_dir) if src_dir else None
        
        # Core data structures
        self.file_cio_structure = {}  # Structure from readcio_read.io.json
        self.file_variables = []  # All file variables from file.cio
        self.input_file_module = {}  # Data from input_file_module.f90
        self.file_mapping = {}  # Maps file.cio variables to actual filenames
        self.file_analysis = {}  # Analysis of each referenced file
        self.io_files = {}  # All available I/O JSON files
        
    def load_file_cio_structure(self):
        """Load and parse readcio_read.io.json to understand file.cio structure"""
        readcio_path = self.json_outputs_dir / "readcio_read.io.json"
        
        if not readcio_path.exists():
            print(f"❌ Error: {readcio_path} not found")
            return False
            
        try:
            with open(readcio_path, 'r') as f:
                self.file_cio_structure = json.load(f)
            
            print(f"✅ Loaded file.cio structure from {readcio_path}")
            
            # Extract all file variables from data_reads
            file_cio_data = self.file_cio_structure.get("file.cio", {})
            data_reads = file_cio_data.get("summary", {}).get("data_reads", [])
            
            for read_section in data_reads:
                columns = read_section.get("columns", [])
                for col in columns:
                    if col.startswith("in_"):  # File variables typically start with in_
                        if col not in self.file_variables:
                            self.file_variables.append(col)
            
            print(f"📁 Found {len(self.file_variables)} file variables in file.cio:")
            for var in self.file_variables:
                print(f"   - {var}")
                
            return True
            
        except Exception as e:
            print(f"❌ Error loading file.cio structure: {e}")
            return False
    
    def load_input_file_module(self):
        """Parse input_file_module.f90 to map file.cio variables to filenames"""
        if not self.src_dir:
            print("⚠️  No source directory provided, skipping input_file_module analysis")
            return
            
        input_module_path = self.src_dir / "input_file_module.f90"
        if not input_module_path.exists():
            print(f"⚠️  {input_module_path} not found, skipping input_file_module analysis")
            return
            
        try:
            with open(input_module_path, 'r') as f:
                content = f.read()
            
            # Parse type definitions and their file mappings
            type_pattern = r'type input_(\w+).*?end type input_\w+'
            matches = re.findall(type_pattern, content, re.DOTALL)
            
            for type_name in matches:
                # Extract file mappings within each type
                type_section = re.search(rf'type input_{type_name}.*?end type input_{type_name}', content, re.DOTALL)
                if type_section:
                    section_content = type_section.group(0)
                    
                    # Find character variable definitions
                    char_pattern = r'character\(len=\d+\)\s*::\s*(\w+)\s*=\s*"([^"]+)"'
                    char_matches = re.findall(char_pattern, section_content)
                    
                    self.input_file_module[f"in_{type_name}"] = {}
                    for var_name, filename in char_matches:
                        self.input_file_module[f"in_{type_name}"][var_name] = filename
            
            print(f"✅ Loaded input_file_module.f90 with {len(self.input_file_module)} type definitions")
            
            return True
            
        except Exception as e:
            print(f"❌ Error parsing input_file_module.f90: {e}")
            return False
    
    def create_file_mapping(self):
        """Create mapping between file.cio variables and actual filenames"""
        print(f"\n🔗 Creating file.cio variable to filename mapping...")
        
        for file_var in self.file_variables:
            files_for_var = []
            
            # Look up in input_file_module
            if file_var in self.input_file_module:
                var_files = self.input_file_module[file_var]
                for var_name, filename in var_files.items():
                    files_for_var.append(filename)
            
            self.file_mapping[file_var] = files_for_var
            print(f"   {file_var} -> {files_for_var}")
    
    def scan_available_io_files(self):
        """Scan all available I/O JSON files"""
        io_pattern = re.compile(r'(.+)\.io\.json$')
        
        for json_file in self.json_outputs_dir.glob("*.io.json"):
            match = io_pattern.match(json_file.name)
            if match:
                procedure_name = match.group(1)
                
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                    self.io_files[procedure_name] = {
                        'file_path': json_file,
                        'data': data
                    }
                except Exception as e:
                    print(f"⚠️  Error loading {json_file}: {e}")
        
        print(f"📊 Found {len(self.io_files)} I/O analysis files")
    
    def analyze_file_parameters(self, filename: str) -> Dict[str, Any]:
        """Analyze parameters read from a specific file"""
        print(f"\n🔍 Analyzing file: {filename}")
        
        # Try to find I/O analysis for this file
        file_analysis = {
            'filename': filename,
            'found_io_analysis': False,
            'parameters': [],
            'io_procedures': [],
            'parameter_count': 0
        }
        
        # Look for I/O procedures that might read this file
        base_name = os.path.splitext(filename)[0].replace('-', '_').replace('.', '_')
        
        # Common patterns for procedure names
        search_patterns = [
            f"{base_name}_read",
            f"read_{base_name}",
            f"{base_name.replace('_', '')}_read",
            base_name,
        ]
        
        for pattern in search_patterns:
            if pattern in self.io_files:
                print(f"   ✅ Found I/O analysis: {pattern}")
                file_analysis['found_io_analysis'] = True
                file_analysis['io_procedures'].append(pattern)
                
                # Extract parameters from I/O analysis
                io_data = self.io_files[pattern]['data']
                
                for file_key, file_info in io_data.items():
                    if file_key == filename or file_key.endswith(filename):
                        summary = file_info.get('summary', {})
                        data_reads = summary.get('data_reads', [])
                        
                        for read_section in data_reads:
                            columns = read_section.get('columns', [])
                            rows = read_section.get('rows', 1)
                            
                            for col in columns:
                                parameter_info = {
                                    'name': col,
                                    'rows': rows,
                                    'procedure': pattern,
                                    'data_type': self._infer_parameter_type(col),
                                    'classification': self._classify_parameter(filename, col)
                                }
                                file_analysis['parameters'].append(parameter_info)
        
        file_analysis['parameter_count'] = len(file_analysis['parameters'])
        
        if not file_analysis['found_io_analysis']:
            print(f"   ⚠️  No I/O analysis found for {filename}")
            # Try to infer common parameters based on file extension
            file_analysis['parameters'] = self._infer_common_parameters(filename)
            file_analysis['parameter_count'] = len(file_analysis['parameters'])
        
        return file_analysis
    
    def _infer_parameter_type(self, param_name: str) -> str:
        """Infer parameter data type from name"""
        int_patterns = r'(id|cnt|num|day|yr|index)'
        real_patterns = r'(area|lat|lon|elev|rate|frac|tmp|pcp|flow)'
        
        if re.search(int_patterns, param_name, re.IGNORECASE):
            return 'int'
        elif re.search(real_patterns, param_name, re.IGNORECASE):
            return 'real'
        else:
            return 'char'
    
    def _classify_parameter(self, filename: str, param_name: str) -> str:
        """Classify parameter based on file type and name"""
        if 'hru' in filename.lower():
            return 'HRU'
        elif 'channel' in filename.lower() or 'cha' in filename.lower():
            return 'CHANNEL'
        elif 'res' in filename.lower() or 'reservoir' in filename.lower():
            return 'RESERVOIR'
        elif 'cli' in filename.lower() or 'weather' in filename.lower():
            return 'CLIMATE'
        elif 'con' in filename.lower():
            return 'CONNECT'
        elif 'sim' in filename.lower() or 'time' in filename.lower():
            return 'SIMULATION'
        else:
            return 'GENERAL'
    
    def _infer_common_parameters(self, filename: str) -> List[Dict[str, Any]]:
        """Infer common parameters for files without I/O analysis"""
        common_params = []
        
        # Basic parameters most SWAT+ files have
        base_params = ['id', 'name']
        
        # File-specific parameter patterns
        if 'hru' in filename.lower():
            base_params.extend(['area', 'lat', 'lon', 'elev'])
        elif 'channel' in filename.lower():
            base_params.extend(['len', 'wdt', 'dep', 'slp'])
        elif 'reservoir' in filename.lower():
            base_params.extend(['vol', 'area_ps', 'vol_ps'])
        elif 'weather' in filename.lower() or 'cli' in filename.lower():
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
        """Generate comprehensive analysis of entire file.cio ecosystem"""
        print(f"\n📊 Generating comprehensive ecosystem analysis...")
        
        analysis = {
            'file_cio_variables': self.file_variables,
            'file_mapping': self.file_mapping,
            'file_analyses': {},
            'total_files': 0,
            'total_parameters': 0,
            'files_with_io_analysis': 0,
            'files_without_io_analysis': 0
        }
        
        # Analyze each file referenced in file.cio
        all_files = set()
        for file_list in self.file_mapping.values():
            all_files.update(file_list)
        
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
    
    def export_to_csv(self, analysis: Dict[str, Any], output_file: str = "file_cio_ecosystem_analysis.csv"):
        """Export analysis to CSV in modular database format"""
        output_path = Path(output_file)
        
        print(f"\n💾 Exporting analysis to {output_path}")
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # CSV Header (matching SWAT+ Modular Database format)
            writer.writerow([
                'Variable', 'Classification', 'SWAT_File', 'Text_File_Structure',
                'Line', 'Code', 'Data_Type', 'Units', 'Default', 'Min_Value', 
                'Max_Value', 'Description', 'Source_Procedure'
            ])
            
            # Write parameters for each file
            line_counter = 1
            for filename, file_info in analysis['file_analyses'].items():
                for param in file_info['parameters']:
                    writer.writerow([
                        param['name'],
                        param['classification'],
                        filename,
                        filename,
                        line_counter,
                        'R',  # Read operation
                        param['data_type'],
                        self._get_parameter_units(param['name']),
                        '',  # Default value (could be enhanced)
                        '',  # Min value (could be enhanced)
                        '',  # Max value (could be enhanced)
                        f"Parameter from {filename} via {param['procedure']}",
                        param['procedure']
                    ])
                    line_counter += 1
        
        print(f"✅ Exported {analysis['total_parameters']} parameters from {analysis['total_files']} files")
        
    def _get_parameter_units(self, param_name: str) -> str:
        """Get units for parameter based on name patterns"""
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
            'flow': 'm3/s'
        }
        
        for pattern, unit in unit_patterns.items():
            if pattern in param_name.lower():
                return unit
        
        return ''
    
    def print_summary(self, analysis: Dict[str, Any]):
        """Print comprehensive summary of the analysis"""
        print("\n" + "="*80)
        print("📋 FILE.CIO ECOSYSTEM ANALYSIS SUMMARY")
        print("="*80)
        
        print(f"📁 File.cio Variables Found: {len(analysis['file_cio_variables'])}")
        for var in analysis['file_cio_variables']:
            files = analysis['file_mapping'].get(var, [])
            print(f"   {var}: {len(files)} files")
        
        print(f"\n📊 Analysis Results:")
        print(f"   Total Files Analyzed: {analysis['total_files']}")
        print(f"   Total Parameters Found: {analysis['total_parameters']}")
        print(f"   Files with I/O Analysis: {analysis['files_with_io_analysis']}")
        print(f"   Files without I/O Analysis: {analysis['files_without_io_analysis']}")
        
        print(f"\n🔍 Detailed File Analysis:")
        for filename, file_info in analysis['file_analyses'].items():
            status = "✅" if file_info['found_io_analysis'] else "⚠️"
            procedures = ", ".join(file_info['io_procedures']) if file_info['io_procedures'] else "none"
            print(f"   {status} {filename}: {file_info['parameter_count']} parameters (via {procedures})")
        
        print("\n" + "="*80)
    
    def run_analysis(self) -> bool:
        """Run complete ecosystem analysis"""
        print("🚀 Starting File.cio Ecosystem Analysis")
        print("="*50)
        
        # Step 1: Load file.cio structure
        if not self.load_file_cio_structure():
            return False
        
        # Step 2: Load input_file_module if available
        self.load_input_file_module()
        
        # Step 3: Create file mapping
        self.create_file_mapping()
        
        # Step 4: Scan available I/O files
        self.scan_available_io_files()
        
        # Step 5: Generate comprehensive analysis
        analysis = self.generate_comprehensive_analysis()
        
        # Step 6: Export results
        self.export_to_csv(analysis)
        
        # Step 7: Print summary
        self.print_summary(analysis)
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Analyze file.cio ecosystem and trace all referenced files')
    parser.add_argument('--json-dir', default='json_outputs', 
                      help='Directory containing FORD JSON outputs')
    parser.add_argument('--src-dir', default='test_data/src',
                      help='Directory containing Fortran source files')
    parser.add_argument('--output', default='file_cio_ecosystem_analysis.csv',
                      help='Output CSV file name')
    
    args = parser.parse_args()
    
    analyzer = FileCioEcosystemAnalyzer(args.json_dir, args.src_dir)
    
    if analyzer.run_analysis():
        print(f"\n✅ Analysis completed successfully!")
        print(f"📄 Results saved to: {args.output}")
    else:
        print("\n❌ Analysis failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()