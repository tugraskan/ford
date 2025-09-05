#!/usr/bin/env python3
"""
Modular Database Analysis Report Generator

Generates a summary report of the modular database with key insights and comparisons
to the original SWAT+ modular database structure.
"""

import json
import csv
import pandas as pd
from pathlib import Path
from collections import defaultdict, Counter

def analyze_modular_database():
    """Generate comprehensive analysis of the generated modular database"""
    
    # Load the data
    modular_db_path = Path('modular_database')
    
    print("=== FORD Generated Modular Database Analysis ===\n")
    
    # 1. Load and analyze CSV data
    df = pd.read_csv(modular_db_path / 'modular_database.csv')
    
    print(f"🔍 **OVERVIEW**")
    print(f"Total Parameters: {len(df):,}")
    print(f"Unique Variables: {df['SWAT_Code_Variable_Name'].nunique():,}")
    print(f"Source Files: {df['SWAT_File'].nunique():,}")
    print(f"Database Tables: {df['database_table'].nunique():,}")
    print()
    
    # 2. Classification analysis
    print(f"📊 **PARAMETER CLASSIFICATIONS**")
    classifications = df['Broad_Classification'].value_counts()
    for classification, count in classifications.items():
        percentage = (count / len(df)) * 100
        print(f"  {classification}: {count:,} ({percentage:.1f}%)")
    print()
    
    # 3. Data type analysis
    print(f"🔢 **DATA TYPES**")
    data_types = df['Data_Type'].value_counts()
    for dtype, count in data_types.items():
        percentage = (count / len(df)) * 100
        print(f"  {dtype}: {count:,} ({percentage:.1f}%)")
    print()
    
    # 4. Units analysis
    print(f"📏 **UNITS DISTRIBUTION**")
    units = df['Units'].value_counts().head(10)
    for unit, count in units.items():
        print(f"  {unit}: {count:,}")
    print()
    
    # 5. Core parameters
    core_params = df[df['Core'] == 'yes']
    print(f"⭐ **CORE PARAMETERS**")
    print(f"Core parameters: {len(core_params):,} ({(len(core_params)/len(df)*100):.1f}%)")
    print(f"Non-core parameters: {len(df) - len(core_params):,}")
    print()
    
    # 6. Top procedures by parameter count
    print(f"🔧 **TOP PROCEDURES BY PARAMETER COUNT**")
    top_procedures = df['Swat_code_type'].value_counts().head(10)
    for procedure, count in top_procedures.items():
        print(f"  {procedure}: {count:,}")
    print()
    
    # 7. Load schema data
    with open(modular_db_path / 'database_schema.json') as f:
        schema = json.load(f)
    
    print(f"🗄️ **DATABASE SCHEMA**")
    print(f"Total Tables: {len(schema):,}")
    
    # Table sizes
    table_sizes = [(name, len(data['fields'])) for name, data in schema.items()]
    table_sizes.sort(key=lambda x: x[1], reverse=True)
    
    print(f"Largest Tables:")
    for table_name, field_count in table_sizes[:10]:
        print(f"  {table_name}: {field_count} fields")
    print()
    
    # 8. Load variable mapping
    with open(modular_db_path / 'variable_mapping.json') as f:
        mapping = json.load(f)
    
    print(f"🔗 **VARIABLE MAPPINGS**")
    print(f"Source code to file mappings: {len(mapping['source_code_to_file']):,}")
    print(f"I/O operations tracked: {len(mapping['io_operations_summary']):,}")
    print()
    
    # 9. I/O Analysis
    print(f"📁 **I/O OPERATIONS ANALYSIS**")
    io_stats = analyze_io_operations(mapping['io_operations_summary'])
    for stat, value in io_stats.items():
        print(f"  {stat}: {value:,}")
    print()
    
    # 10. Comparison with SWAT+ original
    print(f"⚖️ **COMPARISON WITH ORIGINAL SWAT+ MODULAR DATABASE**")
    print(f"Original SWAT+ parameters: 3,330")
    print(f"FORD generated parameters: {len(df):,}")
    print(f"Increase factor: {len(df)/3330:.1f}x")
    print(f"Coverage: Comprehensive source code analysis vs. manual documentation")
    print()
    
    # 11. Quality metrics
    print(f"✅ **QUALITY METRICS**")
    complete_descriptions = df[df['Description'].str.len() > 10]
    print(f"Parameters with descriptions: {len(complete_descriptions):,} ({len(complete_descriptions)/len(df)*100:.1f}%)")
    
    valid_ranges = df[(df['Minimum_Range'] != '0') | (df['Maximum_Range'] != '999')]
    print(f"Parameters with specific ranges: {len(valid_ranges):,} ({len(valid_ranges)/len(df)*100:.1f}%)")
    
    typed_params = df[df['Data_Type'] != 'real']
    print(f"Parameters with specific types: {len(typed_params):,} ({len(typed_params)/len(df)*100:.1f}%)")
    print()
    
    # 12. Sample entries
    print(f"📋 **SAMPLE ENTRIES**")
    sample_entries = df.sample(5)[['SWAT_Code_Variable_Name', 'Broad_Classification', 
                                  'SWAT_File', 'Data_Type', 'Description']]
    for _, row in sample_entries.iterrows():
        print(f"  • {row['SWAT_Code_Variable_Name']} ({row['Data_Type']})")
        print(f"    Classification: {row['Broad_Classification']}")
        print(f"    File: {row['SWAT_File']}")
        print(f"    Description: {row['Description']}")
        print()

def analyze_io_operations(io_summary):
    """Analyze I/O operations summary"""
    stats = {
        'Total procedures with I/O': len(io_summary),
        'Total file units': 0,
        'Read operations': 0,
        'Write operations': 0,
        'Header operations': 0
    }
    
    for procedure, io_data in io_summary.items():
        for unit_name, unit_data in io_data.items():
            if isinstance(unit_data, dict) and 'summary' in unit_data:
                stats['Total file units'] += 1
                summary = unit_data['summary']
                stats['Read operations'] += len(summary.get('data_reads', []))
                stats['Write operations'] += len(summary.get('data_writes', []))
                stats['Header operations'] += len(summary.get('headers', []))
    
    return stats

def export_summary_files():
    """Export additional summary files for easier analysis"""
    
    modular_db_path = Path('modular_database')
    df = pd.read_csv(modular_db_path / 'modular_database.csv')
    
    # Export by classification
    classification_summary = df.groupby('Broad_Classification').agg({
        'Unique_ID': 'count',
        'SWAT_File': 'nunique',
        'database_table': 'nunique'
    }).rename(columns={
        'Unique_ID': 'Parameter_Count',
        'SWAT_File': 'Source_Files',
        'database_table': 'Database_Tables'
    })
    classification_summary.to_csv(modular_db_path / 'classification_summary.csv')
    
    # Export procedure summary
    procedure_summary = df.groupby('Swat_code_type').agg({
        'Unique_ID': 'count',
        'Broad_Classification': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'GENERAL',
        'Data_Type': lambda x: ', '.join(x.unique()[:3])
    }).rename(columns={
        'Unique_ID': 'Parameter_Count',
        'Broad_Classification': 'Primary_Classification',
        'Data_Type': 'Data_Types'
    }).sort_values('Parameter_Count', ascending=False)
    procedure_summary.to_csv(modular_db_path / 'procedure_summary.csv')
    
    print(f"📊 Additional summary files exported:")
    print(f"  • classification_summary.csv")
    print(f"  • procedure_summary.csv")

if __name__ == '__main__':
    analyze_modular_database()
    export_summary_files()