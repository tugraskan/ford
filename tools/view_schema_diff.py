#!/usr/bin/env python3
"""Display side-by-side diff of compare_inputs_schema_diffs.csv file."""

import argparse
import ast
import csv
import sys
from typing import Dict, Optional, Tuple


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # Background colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'


def format_value(value: str, max_width: int = 40) -> str:
    """Format a value for display, truncating if needed."""
    if not value or value == '-':
        return value
    
    # Truncate if too long
    if len(value) > max_width:
        return value[:max_width-3] + '...'
    return value


def print_side_by_side_diff(
    input_file: str,
    line_in_file: str,
    position_in_file: str,
    component: str,
    old_row: Optional[Dict],
    new_row: Optional[Dict],
    show_unchanged: bool = False,
    no_color: bool = False
) -> None:
    """Print a side-by-side comparison of old and new row."""
    
    # Color helpers
    def red(text):
        return f"{Colors.FAIL}{text}{Colors.ENDC}" if not no_color else text
    
    def green(text):
        return f"{Colors.OKGREEN}{text}{Colors.ENDC}" if not no_color else text
    
    def yellow(text):
        return f"{Colors.WARNING}{text}{Colors.ENDC}" if not no_color else text
    
    def bold(text):
        return f"{Colors.BOLD}{text}{Colors.ENDC}" if not no_color else text
    
    def cyan(text):
        return f"{Colors.OKCYAN}{text}{Colors.ENDC}" if not no_color else text
    
    # Print header
    print(bold(f"\n{'='*100}"))
    print(bold(f"File: {input_file} | Line: {line_in_file} | Position: {position_in_file} | Component: {component}"))
    print(bold(f"{'='*100}"))
    
    # Handle cases where one row is missing
    if not old_row and not new_row:
        print("Both old and new rows are empty")
        return
    
    if not old_row:
        print(green(">>> NEW COMPONENT ADDED <<<"))
        print(f"\n{'Field':<25} {'New Value':<40}")
        print("-" * 70)
        for key, value in sorted(new_row.items()):
            print(f"{key:<25} {green(format_value(str(value))):<40}")
        return
    
    if not new_row:
        print(red(">>> COMPONENT REMOVED <<<"))
        print(f"\n{'Field':<25} {'Old Value':<40}")
        print("-" * 70)
        for key, value in sorted(old_row.items()):
            print(f"{key:<25} {red(format_value(str(value))):<40}")
        return
    
    # Both rows exist - show differences
    print(f"\n{'Field':<25} {'Old Value':<40} {'New Value':<40}")
    print("-" * 110)
    
    # Get all unique keys
    all_keys = sorted(set(list(old_row.keys()) + list(new_row.keys())))
    
    has_differences = False
    for key in all_keys:
        old_val = old_row.get(key, '')
        new_val = new_row.get(key, '')
        
        old_str = format_value(str(old_val), 35)
        new_str = format_value(str(new_val), 35)
        
        # Check if values are different
        if old_val != new_val:
            has_differences = True
            # Highlight the difference
            if key not in old_row:
                # Key added
                print(f"{cyan(key):<25} {'':<40} {green(new_str):<40} {green('(ADDED)')}")
            elif key not in new_row:
                # Key removed
                print(f"{cyan(key):<25} {red(old_str):<40} {'':<40} {red('(REMOVED)')}")
            else:
                # Value changed
                print(f"{cyan(key):<25} {red(old_str):<40} {green(new_str):<40} {yellow('(CHANGED)')}")
        elif show_unchanged:
            # Show unchanged fields if requested
            print(f"{key:<25} {old_str:<40} {new_str:<40}")
    
    if not has_differences:
        print(yellow("No differences found (this shouldn't happen in a diff file)"))


def main():
    parser = argparse.ArgumentParser(
        description='Display side-by-side diff of compare_inputs_schema_diffs.csv'
    )
    parser.add_argument(
        'csv_file',
        nargs='?',
        default='compare_inputs_schema_diffs.csv',
        help='Path to the schema diffs CSV file (default: compare_inputs_schema_diffs.csv)'
    )
    parser.add_argument(
        '--filter-file',
        help='Filter to only show diffs for this input file'
    )
    parser.add_argument(
        '--filter-component',
        help='Filter to only show diffs for this component'
    )
    parser.add_argument(
        '--show-unchanged',
        action='store_true',
        help='Show fields that have not changed'
    )
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )
    parser.add_argument(
        '--max-rows',
        type=int,
        help='Maximum number of rows to display'
    )
    parser.add_argument(
        '--output-html',
        help='Generate HTML output to specified file'
    )
    
    args = parser.parse_args()
    
    # Check if we should output HTML
    if args.output_html:
        generate_html_output(args)
        return
    
    # Read and process CSV
    try:
        with open(args.csv_file, 'r') as f:
            reader = csv.DictReader(f)
            
            rows_displayed = 0
            for row in reader:
                # Apply filters
                if args.filter_file and row['input_file'] != args.filter_file:
                    continue
                
                if args.filter_component and row['component'] != args.filter_component:
                    continue
                
                # Parse old_row and new_row
                old_row = None
                new_row = None
                
                if row['old_row']:
                    try:
                        old_row = ast.literal_eval(row['old_row'])
                    except (ValueError, SyntaxError) as e:
                        print(f"Warning: Could not parse old_row: {e}", file=sys.stderr)
                
                if row['new_row']:
                    try:
                        new_row = ast.literal_eval(row['new_row'])
                    except (ValueError, SyntaxError) as e:
                        print(f"Warning: Could not parse new_row: {e}", file=sys.stderr)
                
                # Display the diff
                print_side_by_side_diff(
                    row['input_file'],
                    row['line_in_file'],
                    row['position_in_file'],
                    row['component'],
                    old_row,
                    new_row,
                    show_unchanged=args.show_unchanged,
                    no_color=args.no_color
                )
                
                rows_displayed += 1
                if args.max_rows and rows_displayed >= args.max_rows:
                    print(f"\n... (truncated, showing first {args.max_rows} rows)")
                    break
            
            if rows_displayed == 0:
                print("No matching rows found.")
            else:
                print(f"\n\nTotal rows displayed: {rows_displayed}")
    
    except FileNotFoundError:
        print(f"Error: File '{args.csv_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def generate_html_output(args):
    """Generate HTML output for better visualization in a browser."""
    html_parts = []
    html_parts.append("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Schema Diff Viewer</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }
        .diff-block {
            background: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-bottom: 20px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .diff-header {
            background: #007bff;
            color: white;
            padding: 10px;
            margin: -15px -15px 15px -15px;
            border-radius: 5px 5px 0 0;
            font-weight: bold;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th {
            background: #f8f9fa;
            padding: 10px;
            text-align: left;
            border-bottom: 2px solid #dee2e6;
            font-weight: 600;
        }
        td {
            padding: 8px;
            border-bottom: 1px solid #dee2e6;
        }
        .field-name {
            font-weight: 500;
            color: #495057;
        }
        .removed {
            background-color: #ffebee;
            color: #c62828;
        }
        .added {
            background-color: #e8f5e9;
            color: #2e7d32;
        }
        .changed-old {
            background-color: #fff3e0;
            color: #e65100;
        }
        .changed-new {
            background-color: #e3f2fd;
            color: #1565c0;
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.85em;
            font-weight: 600;
            margin-left: 10px;
        }
        .badge-removed {
            background: #c62828;
            color: white;
        }
        .badge-added {
            background: #2e7d32;
            color: white;
        }
        .badge-changed {
            background: #f57c00;
            color: white;
        }
        .filter-info {
            background: #e3f2fd;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 4px solid #1976d2;
        }
    </style>
</head>
<body>
    <h1>Schema Diff Viewer</h1>
""")
    
    # Add filter info if applicable
    if args.filter_file or args.filter_component:
        html_parts.append('<div class="filter-info">')
        html_parts.append('<strong>Filters Applied:</strong><br>')
        if args.filter_file:
            html_parts.append(f'File: {args.filter_file}<br>')
        if args.filter_component:
            html_parts.append(f'Component: {args.filter_component}<br>')
        html_parts.append('</div>')
    
    # Read and process CSV
    try:
        with open(args.csv_file, 'r') as f:
            reader = csv.DictReader(f)
            
            rows_displayed = 0
            for row in reader:
                # Apply filters
                if args.filter_file and row['input_file'] != args.filter_file:
                    continue
                
                if args.filter_component and row['component'] != args.filter_component:
                    continue
                
                # Parse old_row and new_row
                old_row = None
                new_row = None
                
                if row['old_row']:
                    try:
                        old_row = ast.literal_eval(row['old_row'])
                    except (ValueError, SyntaxError):
                        pass
                
                if row['new_row']:
                    try:
                        new_row = ast.literal_eval(row['new_row'])
                    except (ValueError, SyntaxError):
                        pass
                
                # Generate HTML for this diff
                html_parts.append('<div class="diff-block">')
                html_parts.append(f'<div class="diff-header">')
                html_parts.append(f'File: {row["input_file"]} | ')
                html_parts.append(f'Line: {row["line_in_file"]} | ')
                html_parts.append(f'Position: {row["position_in_file"]} | ')
                html_parts.append(f'Component: {row["component"]}')
                html_parts.append('</div>')
                
                # Handle different cases
                if not old_row and new_row:
                    html_parts.append('<span class="badge badge-added">NEW COMPONENT</span>')
                    html_parts.append('<table><thead><tr><th>Field</th><th>New Value</th></tr></thead><tbody>')
                    for key, value in sorted(new_row.items()):
                        html_parts.append(f'<tr><td class="field-name">{key}</td><td class="added">{value}</td></tr>')
                    html_parts.append('</tbody></table>')
                elif old_row and not new_row:
                    html_parts.append('<span class="badge badge-removed">COMPONENT REMOVED</span>')
                    html_parts.append('<table><thead><tr><th>Field</th><th>Old Value</th></tr></thead><tbody>')
                    for key, value in sorted(old_row.items()):
                        html_parts.append(f'<tr><td class="field-name">{key}</td><td class="removed">{value}</td></tr>')
                    html_parts.append('</tbody></table>')
                elif old_row and new_row:
                    html_parts.append('<table><thead><tr><th>Field</th><th>Old Value</th><th>New Value</th><th>Status</th></tr></thead><tbody>')
                    all_keys = sorted(set(list(old_row.keys()) + list(new_row.keys())))
                    for key in all_keys:
                        old_val = old_row.get(key, '')
                        new_val = new_row.get(key, '')
                        
                        if old_val != new_val:
                            if key not in old_row:
                                status = '<span class="badge badge-added">ADDED</span>'
                                html_parts.append(f'<tr><td class="field-name">{key}</td><td></td><td class="added">{new_val}</td><td>{status}</td></tr>')
                            elif key not in new_row:
                                status = '<span class="badge badge-removed">REMOVED</span>'
                                html_parts.append(f'<tr><td class="field-name">{key}</td><td class="removed">{old_val}</td><td></td><td>{status}</td></tr>')
                            else:
                                status = '<span class="badge badge-changed">CHANGED</span>'
                                html_parts.append(f'<tr><td class="field-name">{key}</td><td class="changed-old">{old_val}</td><td class="changed-new">{new_val}</td><td>{status}</td></tr>')
                        elif args.show_unchanged:
                            html_parts.append(f'<tr><td class="field-name">{key}</td><td>{old_val}</td><td>{new_val}</td><td></td></tr>')
                    html_parts.append('</tbody></table>')
                
                html_parts.append('</div>')
                
                rows_displayed += 1
                if args.max_rows and rows_displayed >= args.max_rows:
                    html_parts.append(f'<p><em>Truncated, showing first {args.max_rows} rows</em></p>')
                    break
            
            html_parts.append(f'<p><strong>Total rows displayed: {rows_displayed}</strong></p>')
    
    except FileNotFoundError:
        html_parts.append(f'<p style="color: red;">Error: File "{args.csv_file}" not found.</p>')
    
    html_parts.append('</body></html>')
    
    # Write HTML to file
    with open(args.output_html, 'w') as f:
        f.write('\n'.join(html_parts))
    
    print(f"HTML output written to: {args.output_html}")


if __name__ == '__main__':
    main()
