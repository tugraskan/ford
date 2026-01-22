# -*- coding: utf-8 -*-
#
#  io_trace.py
#  This file is part of FORD.
#
#  Copyright 2026
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

"""
I/O Trace Analysis Module for FORD

This module provides functionality to analyze Fortran source code and generate
comprehensive I/O trace documentation showing all file read/write operations,
filename resolution chains, unit mappings, and variable definitions.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
import logging

log = logging.getLogger(__name__)


@dataclass
class FileReference:
    """Represents a reference to a file in the source code."""
    filename: str  # The actual filename or expression
    expression: str  # Variable expression that resolves to filename
    file_path: Path  # Source file containing the reference
    line_number: int  # Line number in source file
    io_type: str  # 'input' or 'output'
    

@dataclass
class IOOperation:
    """Represents a single I/O operation (open, read, write, etc.)."""
    operation_type: str  # 'open', 'read', 'write', 'close', 'inquire', etc.
    unit_number: Optional[int]  # Unit number if applicable
    file_expression: Optional[str]  # File expression if applicable
    file_path: Path  # Source file containing the operation
    line_number: int  # Line number in source file
    statement: str  # Full statement text
    variables: List[str] = field(default_factory=list)  # Variables in read/write
    routine_name: Optional[str] = None  # Containing routine/subroutine name


@dataclass
class VariableDefinition:
    """Represents a variable definition with metadata."""
    name: str
    var_type: str  # 'integer', 'real', 'character', 'type(...)', etc.
    scope: str  # 'local', 'module', 'dummy_arg', 'component'
    default_value: Optional[str] = None
    units: Optional[str] = None
    description: Optional[str] = None
    file_path: Optional[Path] = None
    line_number: Optional[int] = None
    dimensions: Optional[str] = None
    kind: Optional[str] = None


@dataclass
class DerivedTypeDefinition:
    """Represents a derived type definition."""
    name: str
    components: List[VariableDefinition] = field(default_factory=list)
    file_path: Optional[Path] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    has_user_defined_io: bool = False


class IOTraceAnalyzer:
    """Analyzes Fortran source code for I/O operations and generates trace documentation."""
    
    def __init__(self, project):
        """
        Initialize the analyzer.
        
        Args:
            project: FORD Project object containing parsed source files
        """
        self.project = project
        self.file_references: Dict[str, List[FileReference]] = defaultdict(list)
        self.io_operations: List[IOOperation] = defaultdict(list)
        self.variable_definitions: Dict[str, VariableDefinition] = {}
        self.type_definitions: Dict[str, DerivedTypeDefinition] = {}
        self.unit_file_mappings: Dict[int, str] = {}
        
    def analyze(self, target_files: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Perform I/O trace analysis on the project.
        
        Args:
            target_files: List of target filenames to trace (e.g., ['aquifer.aqu', 'object.cnt'])
                         If None, analyze all files found in source code.
        
        Returns:
            Dictionary containing analysis results
        """
        log.info("Starting I/O trace analysis...")
        
        # Step 1: Scan for file references
        self._scan_file_references()
        
        # Step 2: Find all I/O operations
        self._scan_io_operations()
        
        # Step 3: Collect variable and type definitions
        self._collect_variable_definitions()
        self._collect_type_definitions()
        
        # Step 4: Build unit-file mappings
        self._build_unit_mappings()
        
        # Step 5: Filter by target files if specified
        if target_files:
            self._filter_by_target_files(target_files)
        
        # Step 6: Generate documentation
        return self._generate_documentation()
    
    def _scan_file_references(self):
        """Scan source code for filename references."""
        log.info("Scanning for file references...")
        
        # Patterns for finding file references
        patterns = [
            # String literals in quotes
            r'["\']([a-zA-Z0-9_\-\.]+\.(aqu|cnt|out|dat|txt|inp|prt))["\']',
            # Variable assignments with filenames
            r'(\w+)\s*=\s*["\']([a-zA-Z0-9_\-\.]+)["\']',
        ]
        
        # Scan all source files in the project
        for source_file in self.project.files:
            try:
                # Ensure path is a Path object
                file_path = Path(source_file.path) if isinstance(source_file.path, str) else source_file.path
                content = file_path.read_text()
                lines = content.splitlines()
                
                for line_num, line in enumerate(lines, 1):
                    # Skip comments
                    if line.strip().startswith('!'):
                        continue
                    
                    for pattern in patterns:
                        for match in re.finditer(pattern, line, re.IGNORECASE):
                            # Extract filename from match
                            filename = match.group(1) if '=' not in match.group(0) else match.group(2)
                            
                            # Determine I/O type based on extension
                            io_type = 'input' if any(ext in filename.lower() for ext in ['.aqu', '.cnt', '.dat', '.inp']) else 'output'
                            
                            ref = FileReference(
                                filename=filename,
                                expression=match.group(0),
                                file_path=file_path,
                                line_number=line_num,
                                io_type=io_type
                            )
                            self.file_references[filename].append(ref)
            except Exception as e:
                log.warning(f"Error scanning {source_file.path}: {e}")
    
    def _scan_io_operations(self):
        """Scan source code for I/O operations (open, read, write, etc.)."""
        log.info("Scanning for I/O operations...")
        
        # Patterns for I/O operations
        io_patterns = {
            'open': r'open\s*\(',
            'read': r'read\s*\(',
            'write': r'write\s*\(',
            'close': r'close\s*\(',
            'inquire': r'inquire\s*\(',
            'rewind': r'rewind\s*\(',
            'backspace': r'backspace\s*\(',
        }
        
        for source_file in self.project.files:
            try:
                # Ensure path is a Path object
                file_path = Path(source_file.path) if isinstance(source_file.path, str) else source_file.path
                content = file_path.read_text()
                lines = content.splitlines()
                
                for line_num, line in enumerate(lines, 1):
                    # Skip comments
                    if line.strip().startswith('!'):
                        continue
                    
                    for op_type, pattern in io_patterns.items():
                        if re.search(pattern, line, re.IGNORECASE):
                            # Extract unit number if present
                            unit_match = re.search(r'unit\s*=\s*(\d+)', line, re.IGNORECASE)
                            unit_number = int(unit_match.group(1)) if unit_match else None
                            
                            # If no unit= keyword, check for positional unit
                            if not unit_number:
                                positional_match = re.search(r'(?:open|read|write|close)\s*\(\s*(\d+)', line, re.IGNORECASE)
                                unit_number = int(positional_match.group(1)) if positional_match else None
                            
                            # Extract file expression for open statements
                            file_expr = None
                            if op_type == 'open':
                                file_match = re.search(r'file\s*=\s*(["\']?[a-zA-Z0-9_\.%]+["\']?)', line, re.IGNORECASE)
                                file_expr = file_match.group(1) if file_match else None
                            
                            operation = IOOperation(
                                operation_type=op_type,
                                unit_number=unit_number,
                                file_expression=file_expr,
                                file_path=file_path,
                                line_number=line_num,
                                statement=line.strip()
                            )
                            self.io_operations[file_path].append(operation)
            except Exception as e:
                log.warning(f"Error scanning I/O operations in {source_file.path}: {e}")
    
    def _collect_variable_definitions(self):
        """Collect variable definitions from parsed source."""
        log.info("Collecting variable definitions...")
        
        # Iterate through all modules and procedures in the project
        for module in getattr(self.project, 'modules', []):
            # Get module-level variables
            for var in getattr(module, 'variables', []):
                var_def = VariableDefinition(
                    name=var.name,
                    var_type=getattr(var, 'vartype', 'unknown'),
                    scope='module',
                    default_value=getattr(var, 'initial', None),
                    description=getattr(var, 'doc', None),
                    file_path=getattr(module, 'path', None),
                    line_number=getattr(var, 'line', None)
                )
                self.variable_definitions[var.name] = var_def
            
            # Get subroutine/function variables
            for proc in getattr(module, 'procedures', []):
                for var in getattr(proc, 'variables', []):
                    full_name = f"{proc.name}::{var.name}"
                    var_def = VariableDefinition(
                        name=var.name,
                        var_type=getattr(var, 'vartype', 'unknown'),
                        scope='local',
                        default_value=getattr(var, 'initial', None),
                        description=getattr(var, 'doc', None),
                        file_path=getattr(proc, 'path', None),
                        line_number=getattr(var, 'line', None)
                    )
                    self.variable_definitions[full_name] = var_def
    
    def _collect_type_definitions(self):
        """Collect derived type definitions from parsed source."""
        log.info("Collecting type definitions...")
        
        for module in getattr(self.project, 'modules', []):
            for dtype in getattr(module, 'types', []):
                components = []
                for var in getattr(dtype, 'variables', []):
                    comp = VariableDefinition(
                        name=var.name,
                        var_type=getattr(var, 'vartype', 'unknown'),
                        scope='component',
                        default_value=getattr(var, 'initial', None),
                        description=getattr(var, 'doc', None),
                        line_number=getattr(var, 'line', None)
                    )
                    components.append(comp)
                
                type_def = DerivedTypeDefinition(
                    name=dtype.name,
                    components=components,
                    file_path=getattr(dtype, 'path', None),
                    line_start=getattr(dtype, 'line', None),
                    line_end=getattr(dtype, 'line', None)  # Would need to track end line
                )
                self.type_definitions[dtype.name] = type_def
    
    def _build_unit_mappings(self):
        """Build mappings between unit numbers and files."""
        log.info("Building unit-file mappings...")
        
        for file_path, operations in self.io_operations.items():
            for op in operations:
                if op.operation_type == 'open' and op.unit_number and op.file_expression:
                    self.unit_file_mappings[op.unit_number] = op.file_expression
    
    def _filter_by_target_files(self, target_files: List[str]):
        """Filter results to only include specified target files."""
        log.info(f"Filtering by target files: {target_files}")
        
        # Filter file references
        filtered_refs = {}
        for filename, refs in self.file_references.items():
            if any(target in filename for target in target_files):
                filtered_refs[filename] = refs
        self.file_references = filtered_refs
    
    def _generate_documentation(self) -> Dict[str, Any]:
        """Generate the I/O trace documentation structure."""
        log.info("Generating documentation...")
        
        doc = {
            'filename_resolution_map': self._generate_filename_map(),
            'io_sites_and_mappings': self._generate_io_sites(),
            'variable_definitions': self.variable_definitions,
            'type_definitions': self.type_definitions,
            'unit_mappings': self.unit_file_mappings,
        }
        
        return doc
    
    def _generate_filename_map(self) -> Dict[str, Any]:
        """Generate the filename resolution map section."""
        filename_map = {}
        
        for filename, refs in self.file_references.items():
            resolution_chain = {
                'target_filename': filename,
                'references': []
            }
            
            for ref in refs:
                resolution_chain['references'].append({
                    'expression': ref.expression,
                    'location': f"{ref.file_path}:{ref.line_number}",
                    'io_type': ref.io_type
                })
            
            filename_map[filename] = resolution_chain
        
        return filename_map
    
    def _generate_io_sites(self) -> Dict[Path, List[Dict[str, Any]]]:
        """Generate the I/O sites and unit mappings section."""
        io_sites = {}
        
        for file_path, operations in self.io_operations.items():
            sites = []
            for op in operations:
                site = {
                    'operation': op.operation_type,
                    'unit': op.unit_number,
                    'file_expression': op.file_expression,
                    'location': f"{op.file_path}:{op.line_number}",
                    'statement': op.statement
                }
                sites.append(site)
            
            io_sites[file_path] = sites
        
        return io_sites


def generate_io_trace_markdown(analysis_results: Dict[str, Any], output_path: Path):
    """
    Generate a markdown file with I/O trace documentation.
    
    Args:
        analysis_results: Results from IOTraceAnalyzer.analyze()
        output_path: Path where markdown file should be written
    """
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    lines = []
    
    # Header
    lines.append("# Fortran I/O Trace Analysis Report\n")
    lines.append(f"Generated by FORD I/O Trace Analyzer\n\n")
    lines.append("---\n\n")
    
    # Section 1: Filename Resolution Map
    lines.append("## 1. Filename Resolution Map\n\n")
    
    filename_map = analysis_results.get('filename_resolution_map', {})
    for i, (filename, data) in enumerate(filename_map.items(), 1):
        lines.append(f"### 1.{i} {filename}\n\n")
        lines.append(f"**Target filename:** `{data['target_filename']}`\n\n")
        
        if data['references']:
            lines.append("**References:**\n")
            for ref in data['references']:
                lines.append(f"- Expression: `{ref['expression']}`\n")
                lines.append(f"  - Location: `{ref['location']}`\n")
                lines.append(f"  - Type: {ref['io_type']}\n")
        lines.append("\n")
    
    # Section 2: I/O Sites and Unit Mappings
    lines.append("## 2. I/O Sites and Unit Mappings\n\n")
    
    io_sites = analysis_results.get('io_sites_and_mappings', {})
    for file_path, sites in io_sites.items():
        lines.append(f"### File: {file_path}\n\n")
        
        for site in sites:
            lines.append(f"**{site['operation'].upper()}** — `{site['location']}`\n")
            if site['unit']:
                lines.append(f"- Unit: {site['unit']}\n")
            if site['file_expression']:
                lines.append(f"- File: `{site['file_expression']}`\n")
            lines.append(f"```fortran\n{site['statement']}\n```\n\n")
    
    # Section 3: Variable Definitions
    lines.append("## 3. Variable Definitions\n\n")
    
    var_defs = analysis_results.get('variable_definitions', {})
    if var_defs:
        lines.append("| Variable | Type | Scope | Default | Description |\n")
        lines.append("|----------|------|-------|---------|-------------|\n")
        for var_name, var_def in var_defs.items():
            desc = var_def.description or ''
            default = var_def.default_value or ''
            lines.append(f"| `{var_name}` | {var_def.var_type} | {var_def.scope} | {default} | {desc} |\n")
    
    lines.append("\n")
    
    # Section 4: Derived Type Definitions
    lines.append("## 4. Derived Type Definitions\n\n")
    
    type_defs = analysis_results.get('type_definitions', {})
    for type_name, type_def in type_defs.items():
        lines.append(f"### Type: {type_name}\n\n")
        if type_def.file_path:
            lines.append(f"**Defined at:** `{type_def.file_path}:{type_def.line_start}`\n\n")
        
        if type_def.components:
            lines.append("**Components:**\n\n")
            for comp in type_def.components:
                lines.append(f"- `{comp.name}`: {comp.var_type}")
                if comp.default_value:
                    lines.append(f" = {comp.default_value}")
                if comp.description:
                    lines.append(f" — {comp.description}")
                lines.append("\n")
        lines.append("\n")
    
    # Write to file
    output_path.write_text(''.join(lines))
    log.info(f"I/O trace documentation written to {output_path}")


def run_io_trace_analysis(project, target_files: Optional[List[str]] = None, output_file: Optional[Path] = None):
    """
    Main entry point for I/O trace analysis.
    
    Args:
        project: FORD Project object
        target_files: Optional list of target filenames to trace
        output_file: Optional output path for markdown report
    """
    analyzer = IOTraceAnalyzer(project)
    results = analyzer.analyze(target_files=target_files)
    
    # Print summary
    print(f"  Found {len(results.get('filename_resolution_map', {}))} file references")
    print(f"  Found {sum(len(ops) for ops in results.get('io_sites_and_mappings', {}).values())} I/O operations")
    print(f"  Found {len(results.get('variable_definitions', {}))} variable definitions")
    print(f"  Found {len(results.get('type_definitions', {}))} type definitions")
    
    if output_file:
        generate_io_trace_markdown(results, output_file)
        print(f"  Report saved to: {output_file}")
    
    return results
