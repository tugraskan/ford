#!/usr/bin/env python3
"""
Generate a detailed list of missing parameters for the user
"""

import pandas as pd
from pathlib import Path

def load_databases():
    """Load reference and dynamic databases"""
    
    # Load reference database
    ref_file = 'test_data/Modular Database_5_15_24_nbs.csv'
    print(f"Loading reference database: {ref_file}")
    
    try:
        ref_df = pd.read_csv(ref_file, encoding='utf-8')
    except UnicodeDecodeError:
        ref_df = pd.read_csv(ref_file, encoding='latin-1')
    
    ref_df.columns = ref_df.columns.str.replace('\ufeff', '')
    
    # Clean reference database
    ref_df = ref_df[
        (ref_df['SWAT_File'].notna()) & 
        (ref_df['SWAT_File'] != '*') & 
        (ref_df['SWAT_File'] != '') &
        (~ref_df['SWAT_File'].str.contains('parm_list', na=False))
    ].copy()
    
    # Load latest dynamic database
    dynamic_file = 'enhanced_dynamic_output/enhanced_modular_database.csv'
    print(f"Loading dynamic database: {dynamic_file}")
    dynamic_df = pd.read_csv(dynamic_file)
    
    return ref_df, dynamic_df

def analyze_missing_parameters():
    """Generate detailed missing parameter analysis"""
    
    ref_df, dynamic_df = load_databases()
    
    ref_files = set(ref_df['SWAT_File'].unique()) 
    dynamic_files = set(dynamic_df['SWAT_File'].unique())
    
    # Files completely missing
    missing_files = ref_files - dynamic_files
    # Files with coverage but missing parameters  
    covered_files = ref_files & dynamic_files
    
    print("\n" + "="*100)
    print("DETAILED MISSING PARAMETERS ANALYSIS")
    print("="*100)
    
    print(f"\n📊 SUMMARY:")
    print(f"   • Reference Database: {len(ref_df):,} parameters across {len(ref_files)} files")
    print(f"   • Current Dynamic Database: {len(dynamic_df):,} parameters across {len(dynamic_files)} files")
    print(f"   • Completely Missing Files: {len(missing_files)} ({len(missing_files)/len(ref_files)*100:.1f}%)")
    print(f"   • Files with Partial Coverage: {len(covered_files)} ({len(covered_files)/len(ref_files)*100:.1f}%)")
    
    # 1. TOP MISSING FILES (Completely absent)
    print(f"\n🚨 TOP MISSING FILES (Completely Absent from Dynamic Database)")
    print("-" * 100)
    
    missing_stats = []
    for file in missing_files:
        ref_params = ref_df[ref_df['SWAT_File'] == file]['DATABASE_FIELD_NAME'].tolist()
        missing_stats.append({
            'file': file,
            'count': len(ref_params),
            'params': ref_params
        })
    
    missing_stats.sort(key=lambda x: x['count'], reverse=True)
    
    for i, stat in enumerate(missing_stats[:10], 1):
        print(f"\n{i:2d}. {stat['file']} ({stat['count']} parameters)")
        # Show first 10 parameters as examples
        for j, param in enumerate(stat['params'][:10], 1):
            print(f"    {j:2d}) {param}")
        if len(stat['params']) > 10:
            print(f"    ... and {len(stat['params']) - 10} more parameters")
    
    # 2. PARTIAL COVERAGE FILES (Present but incomplete)
    print(f"\n🔧 FILES WITH POOR COVERAGE (<50% complete)")
    print("-" * 100)
    
    partial_stats = []
    for file in covered_files:
        ref_params = set(ref_df[ref_df['SWAT_File'] == file]['DATABASE_FIELD_NAME'])
        dynamic_params = set(dynamic_df[dynamic_df['SWAT_File'] == file]['DATABASE_FIELD_NAME'])
        
        missing_params = ref_params - dynamic_params
        coverage_pct = len(dynamic_params) / len(ref_params) * 100 if ref_params else 0
        
        if coverage_pct < 50 and len(ref_params) >= 5:  # Only show significant files
            partial_stats.append({
                'file': file,
                'ref_count': len(ref_params),
                'dynamic_count': len(dynamic_params),
                'coverage_pct': coverage_pct,
                'missing_params': sorted(list(missing_params))
            })
    
    partial_stats.sort(key=lambda x: len(x['missing_params']), reverse=True)
    
    for i, stat in enumerate(partial_stats[:10], 1):
        print(f"\n{i:2d}. {stat['file']} ({stat['dynamic_count']}/{stat['ref_count']} = {stat['coverage_pct']:.1f}% coverage)")
        print(f"    Missing {len(stat['missing_params'])} parameters:")
        # Show first 15 missing parameters
        for j, param in enumerate(stat['missing_params'][:15], 1):
            print(f"    {j:2d}) {param}")
        if len(stat['missing_params']) > 15:
            print(f"    ... and {len(stat['missing_params']) - 15} more missing parameters")
    
    # 3. SUMMARY STATISTICS
    total_missing_completely = sum(stat['count'] for stat in missing_stats[:10])
    total_missing_partial = sum(len(stat['missing_params']) for stat in partial_stats[:10])
    
    print(f"\n📈 IMPLEMENTATION IMPACT:")
    print(f"   • Top 10 completely missing files: {total_missing_completely:,} parameters")
    print(f"   • Top 10 partially covered files: {total_missing_partial:,} missing parameters")
    print(f"   • Total addressable gap: {total_missing_completely + total_missing_partial:,} parameters")
    print(f"   • Current coverage: {len(dynamic_df):,} / {len(ref_df):,} = {len(dynamic_df)/len(ref_df)*100:.1f}%")
    print(f"   • Potential coverage: {len(dynamic_df) + total_missing_completely + total_missing_partial:,} / {len(ref_df):,} = {(len(dynamic_df) + total_missing_completely + total_missing_partial)/len(ref_df)*100:.1f}%")

if __name__ == '__main__':
    analyze_missing_parameters()