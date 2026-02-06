"""
File Classification System for SWAT+ Input Files

This module provides functionality to automatically classify input files
based on their structure and content, rather than hardcoded filename mappings.

Classifications:
- Simple: Tabular data files with straightforward structure
- Unique: Single-instance configuration or master files
- Connect: Files that link or connect different model components
"""

import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class FileStructure:
    """Represents the analyzed structure of a file."""
    
    num_lines: int
    num_columns_avg: float
    num_tables: int
    has_header: bool
    has_references: bool  # Contains IDs/names that reference other files
    has_mixed_structure: bool
    keyword_density: float  # Ratio of lines with keywords/identifiers


class FileClassifier:
    """
    Classifies input files based on their internal structure.
    
    The classification is based on analyzing:
    - File structure (tabular vs. hierarchical)
    - Data patterns (references, connections, single values)
    - Content organization (sections, tables, key-value pairs)
    """
    
    # Patterns that suggest different classifications
    CONNECTION_KEYWORDS = [
        'hru', 'rout_unit', 'modflow', 'aquifer', 'channel', 'reservoir',
        'recall', 'exco', 'delratio', 'outlet', 'chandeg'
    ]
    
    UNIQUE_PATTERNS = [
        r'^\s*\d+\s*$',  # Single number lines (count/flag)
        r'^\s*[a-zA-Z_]+\s*[:=]',  # Key-value pairs
        r'^\s*#',  # Comment lines
    ]
    
    def __init__(self):
        self.classification_rules = {
            'Connect': self._is_connect_file,
            'Unique': self._is_unique_file,
            'Simple': self._is_simple_file,
        }
    
    def classify(self, filepath: str) -> str:
        """
        Classify a file based on its structure.
        
        Args:
            filepath: Path to the file to classify
            
        Returns:
            Classification string: 'Simple', 'Unique', 'Connect', or 'Unknown'
        """
        try:
            structure = self._analyze_structure(filepath)
            
            # Check each classification in priority order
            for classification, rule_func in self.classification_rules.items():
                if rule_func(filepath, structure):
                    return classification
            
            return 'Unknown'
            
        except Exception as e:
            print(f"Error classifying {filepath}: {e}")
            return 'Unknown'
    
    def _analyze_structure(self, filepath: str) -> FileStructure:
        """Analyze the structure of a file."""
        path = Path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # Filter out empty lines and comments
        content_lines = [
            line.strip() for line in lines 
            if line.strip() and not line.strip().startswith('!')
        ]
        
        if not content_lines:
            return FileStructure(0, 0, 0, False, False, False, 0)
        
        # Analyze column structure
        columns_per_line = []
        for line in content_lines[:min(100, len(content_lines))]:
            # Count whitespace-separated tokens
            tokens = line.split()
            if tokens:
                columns_per_line.append(len(tokens))
        
        avg_columns = sum(columns_per_line) / len(columns_per_line) if columns_per_line else 0
        
        # Check for tabular structure (consistent column count)
        is_tabular = False
        if columns_per_line:
            column_variance = sum(
                abs(c - avg_columns) for c in columns_per_line
            ) / len(columns_per_line)
            is_tabular = column_variance < 2.0  # Low variance suggests table
        
        # Check for headers
        has_header = self._check_header(content_lines)
        
        # Check for references to other components
        has_references = self._check_references(content_lines)
        
        # Count table-like sections
        num_tables = self._count_tables(content_lines)
        
        # Check for mixed structure (both key-value and tabular)
        has_mixed = self._check_mixed_structure(content_lines)
        
        # Calculate keyword density
        keyword_density = self._calculate_keyword_density(content_lines)
        
        return FileStructure(
            num_lines=len(content_lines),
            num_columns_avg=avg_columns,
            num_tables=num_tables,
            has_header=has_header,
            has_references=has_references,
            has_mixed_structure=has_mixed,
            keyword_density=keyword_density
        )
    
    def _check_header(self, lines: List[str]) -> bool:
        """Check if file has a header section."""
        if not lines:
            return False
        
        first_line = lines[0]
        # Headers often contain text labels or have fewer columns
        tokens = first_line.split()
        if tokens:
            # Check if first line has mostly text (not just numbers)
            text_tokens = sum(1 for t in tokens if not self._is_numeric(t))
            return text_tokens > len(tokens) / 2
        
        return False
    
    def _check_references(self, lines: List[str]) -> bool:
        """Check if file contains references to other components."""
        # Look for patterns like: component_id, component_name, etc.
        reference_patterns = [
            r'\bhru\b', r'\bchan\b', r'\bres\b', r'\baqu\b',
            r'\bunit\b', r'\bobj\b', r'\bobject\b',
            r'_id\b', r'_name\b', r'_num\b'
        ]
        
        content = ' '.join(lines[:20])  # Check first 20 lines
        for pattern in reference_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _count_tables(self, lines: List[str]) -> int:
        """Count number of table-like sections in file."""
        # A table is a sequence of lines with consistent column count
        if not lines:
            return 0
        
        tables = 0
        in_table = False
        prev_cols = 0
        consistent_count = 0
        
        for line in lines:
            cols = len(line.split())
            
            if cols > 0:
                if abs(cols - prev_cols) <= 1:  # Similar column count
                    consistent_count += 1
                    if consistent_count >= 3 and not in_table:
                        tables += 1
                        in_table = True
                else:
                    consistent_count = 0
                    in_table = False
                
                prev_cols = cols
        
        return tables
    
    def _check_mixed_structure(self, lines: List[str]) -> bool:
        """Check if file has mixed structure (both key-value and tabular)."""
        has_keyvalue = False
        has_tabular = False
        
        for line in lines[:20]:
            # Check for key-value pattern
            if re.match(r'^\s*[a-zA-Z_]+\s*[:=]', line):
                has_keyvalue = True
            
            # Check for tabular (multiple numeric values)
            tokens = line.split()
            if len(tokens) >= 3:
                numeric_count = sum(1 for t in tokens if self._is_numeric(t))
                if numeric_count >= len(tokens) / 2:
                    has_tabular = True
        
        return has_keyvalue and has_tabular
    
    def _calculate_keyword_density(self, lines: List[str]) -> float:
        """Calculate the ratio of lines containing keywords/identifiers."""
        if not lines:
            return 0.0
        
        keyword_lines = 0
        for line in lines:
            # Check if line starts with or contains identifier-like patterns
            if re.match(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*', line):
                keyword_lines += 1
        
        return keyword_lines / len(lines)
    
    def _is_numeric(self, token: str) -> bool:
        """Check if a token is numeric."""
        try:
            float(token)
            return True
        except ValueError:
            return False
    
    def _is_connect_file(self, filepath: str, structure: FileStructure) -> bool:
        """
        Determine if file is a 'Connect' type.
        
        Connect files link different model components together.
        Characteristics:
        - Filename contains connection keywords (.con extension or connect-related names)
        - Contains references to multiple objects/components
        - Has tabular structure with IDs/names
        """
        filename = Path(filepath).name.lower()
        
        # Check filename patterns
        if filename.endswith('.con') or 'connect' in filename:
            return True
        
        # Check if any connection keywords in filename
        for keyword in self.CONNECTION_KEYWORDS:
            if keyword in filename:
                # If it references other components, likely a connector
                if structure.has_references and structure.num_columns_avg >= 2:
                    return True
        
        # Files with .lin extension (link files)
        if filename.endswith('.lin'):
            return True
        
        return False
    
    def _is_unique_file(self, filepath: str, structure: FileStructure) -> bool:
        """
        Determine if file is a 'Unique' type.
        
        Unique files are master/configuration files, typically one per project.
        Characteristics:
        - Master configuration files (.cio, .def, etc.)
        - Single-instance files (only one in project)
        - Mixed or hierarchical structure
        - Contains project-level settings
        """
        filename = Path(filepath).name.lower()
        
        # Known unique file patterns - but exclude those that can be simple
        unique_extensions = ['.cio', '.dtl', '.sch']
        unique_names = ['file.cio', 'management.sch', 'water_allocation.wro']
        
        if any(filename.endswith(ext) for ext in unique_extensions):
            return True
        
        if filename in unique_names:
            return True
        
        # .def files are unique only for certain names
        if filename.endswith('.def') and any(name in filename for name in ['rout_unit', 'ls_unit', 'ls_reg']):
            return True
        
        # Files with unique/master keywords
        unique_keywords = ['master', 'config', 'allocation', 'weather-wgn', 'atmo']
        if any(keyword in filename for keyword in unique_keywords):
            return True
        
        # Characteristics of unique files
        # - Mixed structure or very low line count with high keyword density
        if structure.has_mixed_structure and structure.num_lines < 20:
            return True
        
        if structure.num_lines < 5 and structure.keyword_density > 0.7:
            return True
        
        # Initialization files that are per-type singletons - but only small ones
        if filename.endswith('.ini') and structure.num_lines < 20:
            return True
        
        # Data files that are typically unique
        if filename.endswith('.dat') or filename.endswith('.prt'):
            return True
        
        return False
    
    def _is_simple_file(self, filepath: str, structure: FileStructure) -> bool:
        """
        Determine if file is a 'Simple' type.
        
        Simple files contain straightforward tabular data.
        Characteristics:
        - Consistent tabular structure
        - Multiple rows of data
        - Predictable column count
        - Often parameter or data tables
        """
        # Simple files have consistent structure
        if structure.num_tables >= 1:
            # Has at least one clear table
            if not structure.has_mixed_structure:
                # Not mixed structure (pure tabular)
                if structure.num_columns_avg >= 2:
                    # Has multiple columns
                    return True
        
        # Files with simple extensions typically containing tabular data
        filename = Path(filepath).name.lower()
        simple_extensions = [
            '.bsn', '.cli', '.cha', '.res', '.wet', '.ele', '.rtu', '.dr',
            '.hru', '.exc', '.del', '.aqu', '.hyd', '.fld', '.str', '.plt',
            '.frt', '.til', '.pes', '.pth', '.urb', '.sep', '.sno', '.ops',
            '.lum', '.cal', '.sft', '.sol', '.reg', '.key'
        ]
        
        if any(filename.endswith(ext) for ext in simple_extensions):
            # Verify it has tabular structure
            if structure.num_lines > 0 and structure.num_columns_avg > 0:
                return True
        
        return False


def classify_file(filepath: str) -> str:
    """
    Convenience function to classify a single file.
    
    Args:
        filepath: Path to the file to classify
        
    Returns:
        Classification string: 'Simple', 'Unique', 'Connect', or 'Unknown'
    """
    classifier = FileClassifier()
    return classifier.classify(filepath)


def classify_files(filepaths: List[str]) -> Dict[str, str]:
    """
    Classify multiple files.
    
    Args:
        filepaths: List of file paths to classify
        
    Returns:
        Dictionary mapping filepath to classification
    """
    classifier = FileClassifier()
    return {fp: classifier.classify(fp) for fp in filepaths}
