#!/usr/bin/env python3

import json
import os

def debug_outside_variables():
    """Debug the outside variables extraction logic."""
    # Look for the I/O analysis JSON file
    json_path = os.path.join('json_outputs', 'basin_print_codes_read.io.json')
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            io_data = json.load(f)
        
        print("=== JSON Data Structure ===")
        for unit, operations in io_data.items():
            print(f"Unit: {unit}")
            if isinstance(operations, dict) and 'summary' in operations:
                print(f"  Summary found")
                for data_read in operations['summary'].get('data_reads', []):
                    print(f"  Data read columns: {data_read.get('columns', [])}")
        
        # Extract variable usage from JSON data
        variable_usage = {}  # {base_var: {'attributes': set(), 'type': str, 'module': str}}
        
        for unit, operations in io_data.items():
            if isinstance(operations, dict) and 'summary' in operations:
                # Process data_reads to find variable usage
                for data_read in operations['summary'].get('data_reads', []):
                    for column in data_read.get('columns', []):
                        print(f"Processing column: {column}")
                        # Parse variables like "pco%wb_bsn%d", "in_sim%prt", etc.
                        if '%' in column:
                            parts = column.split('%')
                            base_var = parts[0].strip()
                            attribute = '%'.join(parts[1:])
                            
                            print(f"  Found attribute: {base_var} -> {attribute}")
                            
                            if base_var not in variable_usage:
                                variable_usage[base_var] = {'attributes': set(), 'type': '', 'module': ''}
                            variable_usage[base_var]['attributes'].add(attribute)
                        else:
                            # Simple variable reference
                            base_var = column.strip()
                            print(f"  Found simple var: {base_var}")
                            if base_var not in variable_usage:
                                variable_usage[base_var] = {'attributes': set(), 'type': '', 'module': ''}
        
        print("\n=== Variable Usage Extracted ===")
        for base_var, var_info in variable_usage.items():
            print(f"{base_var}:")
            print(f"  Attributes: {var_info['attributes']}")
            print(f"  Type: {var_info['type']}")
            print(f"  Module: {var_info['module']}")
        
        return variable_usage
    
    return {}

if __name__ == "__main__":
    debug_outside_variables()