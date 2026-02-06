#!/usr/bin/env python
"""
Command-line interface for the file classification system.

This script allows users to classify input files from the command line.
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import List
from ford.file_classifier import FileClassifier, classify_file


def main():
    """Main entry point for the file classifier CLI."""
    parser = argparse.ArgumentParser(
        description='Classify input files based on their structure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Classifications:
  Simple   - Tabular data files with straightforward structure
  Unique   - Single-instance configuration or master files
  Connect  - Files that link or connect different model components
  Unknown  - Files that don't match any classification pattern

Examples:
  # Classify a single file
  %(prog)s file.cio
  
  # Classify multiple files
  %(prog)s *.cli *.con
  
  # Classify files and output as CSV
  %(prog)s --format csv *.hru
  
  # Classify all files in a directory
  %(prog)s input_files/*
        """
    )
    
    parser.add_argument(
        'files',
        nargs='+',
        help='File(s) to classify'
    )
    
    parser.add_argument(
        '-f', '--format',
        choices=['table', 'csv', 'json'],
        default='table',
        help='Output format (default: table)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed structure information'
    )
    
    args = parser.parse_args()
    
    # Collect all files
    files_to_classify = []
    for file_pattern in args.files:
        path = Path(file_pattern)
        if path.is_file():
            files_to_classify.append(str(path))
        elif path.is_dir():
            # If directory, get all files in it
            files_to_classify.extend(str(f) for f in path.iterdir() if f.is_file())
        else:
            # Try glob pattern
            parent = path.parent if path.parent.exists() else Path('.')
            files_to_classify.extend(str(f) for f in parent.glob(path.name))
    
    if not files_to_classify:
        print("No files found to classify", file=sys.stderr)
        return 1
    
    # Classify files
    classifier = FileClassifier()
    results = []
    
    for filepath in files_to_classify:
        try:
            classification = classifier.classify(filepath)
            
            if args.verbose:
                structure = classifier._analyze_structure(filepath)
                results.append({
                    'file': filepath,
                    'classification': classification,
                    'lines': structure.num_lines,
                    'columns': f'{structure.num_columns_avg:.1f}',
                    'tables': structure.num_tables,
                })
            else:
                results.append({
                    'file': filepath,
                    'classification': classification,
                })
        except Exception as e:
            print(f"Error classifying {filepath}: {e}", file=sys.stderr)
            results.append({
                'file': filepath,
                'classification': 'Error',
            })
    
    # Output results
    if args.format == 'table':
        output_table(results, args.verbose)
    elif args.format == 'csv':
        output_csv(results, args.verbose)
    elif args.format == 'json':
        output_json(results)
    
    return 0


def output_table(results: List[dict], verbose: bool):
    """Output results as a formatted table."""
    if not results:
        return
    
    if verbose:
        # Calculate column widths
        max_file_len = max(len(r['file']) for r in results)
        max_class_len = max(len(r['classification']) for r in results)
        
        # Header
        header = f"{'File':<{max_file_len}}  {'Classification':<{max_class_len}}  Lines  Cols  Tables"
        print(header)
        print('-' * len(header))
        
        # Rows
        for r in results:
            print(f"{r['file']:<{max_file_len}}  {r['classification']:<{max_class_len}}  "
                  f"{r['lines']:>5}  {r['columns']:>4}  {r['tables']:>6}")
    else:
        # Calculate column widths
        max_file_len = max(len(r['file']) for r in results)
        max_class_len = max(len(r['classification']) for r in results)
        
        # Header
        header = f"{'File':<{max_file_len}}  Classification"
        print(header)
        print('-' * len(header))
        
        # Rows
        for r in results:
            print(f"{r['file']:<{max_file_len}}  {r['classification']}")


def output_csv(results: List[dict], verbose: bool):
    """Output results as CSV."""
    if not results:
        return
    
    writer = csv.DictWriter(sys.stdout, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)


def output_json(results: List[dict]):
    """Output results as JSON."""
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    sys.exit(main())
