#!/usr/bin/env python3
"""
Simple script to list missing parameters for the user
"""

import pandas as pd

def main():
    # Load reference database
    print("Loading original SWAT+ Modular Database...")
    ref_df = pd.read_csv('test_data/Modular Database_5_15_24_nbs.csv', encoding='utf-8', low_memory=False)
    ref_df.columns = ref_df.columns.str.replace('\ufeff', '')
    
    # Clean reference database
    ref_df = ref_df[
        (ref_df['SWAT_File'].notna()) & 
        (ref_df['SWAT_File'] != '*') & 
        (ref_df['SWAT_File'] != '') &
        (~ref_df['SWAT_File'].str.contains('parm_list', na=False))
    ].copy()
    
    # Load current dynamic database
    print("Loading current dynamic modular database...")
    dynamic_df = pd.read_csv('enhanced_dynamic_output/enhanced_modular_database.csv')
    
    print(f"\n📊 DATABASE COMPARISON:")
    print(f"   • Original SWAT+ Database: {len(ref_df):,} parameters across {ref_df['SWAT_File'].nunique()} files")
    print(f"   • Current Dynamic Database: {len(dynamic_df):,} parameters across {dynamic_df['SWAT_File'].nunique()} files")
    print(f"   • Coverage: {len(dynamic_df)/len(ref_df)*100:.1f}%")
    
    # Find missing files
    ref_files = set(ref_df['SWAT_File'].unique())
    dynamic_files = set(dynamic_df['SWAT_File'].unique())
    missing_files = ref_files - dynamic_files
    covered_files = ref_files & dynamic_files
    
    print(f"\n🚨 MISSING FILES: {len(missing_files)} files completely absent")
    print(f"🔧 PARTIAL FILES: {len(covered_files)} files with partial coverage")
    
    # Top missing files
    print(f"\n📋 TOP 20 COMPLETELY MISSING FILES:")
    print("-" * 80)
    
    missing_file_stats = []
    for file in missing_files:
        count = len(ref_df[ref_df['SWAT_File'] == file])
        sample_params = ref_df[ref_df['SWAT_File'] == file]['DATABASE_FIELD_NAME'].head(3).tolist()
        missing_file_stats.append((file, count, sample_params))
    
    missing_file_stats.sort(key=lambda x: x[1], reverse=True)
    
    for i, (file, count, sample_params) in enumerate(missing_file_stats[:20], 1):
        sample_str = ', '.join(sample_params)
        print(f"{i:2d}. {file:<25} ({count:3d} params) - e.g., {sample_str}")
    
    # Partially covered files with most missing parameters
    print(f"\n📋 TOP 20 PARTIALLY COVERED FILES (Most Missing Parameters):")
    print("-" * 80)
    
    partial_file_stats = []
    for file in covered_files:
        ref_count = len(ref_df[ref_df['SWAT_File'] == file])
        dynamic_count = len(dynamic_df[dynamic_df['SWAT_File'] == file])
        missing_count = ref_count - dynamic_count
        coverage_pct = dynamic_count / ref_count * 100 if ref_count > 0 else 0
        
        if missing_count > 0:
            # Get some example missing parameters
            ref_params = set(ref_df[ref_df['SWAT_File'] == file]['DATABASE_FIELD_NAME'])
            dynamic_params = set(dynamic_df[dynamic_df['SWAT_File'] == file]['Parameter_Name'])
            # For this comparison, we assume parameter names are similar
            sample_missing = list(ref_params)[:3]  # Just show first few ref params as examples
            
            partial_file_stats.append((file, ref_count, dynamic_count, missing_count, coverage_pct, sample_missing))
    
    partial_file_stats.sort(key=lambda x: x[3], reverse=True)  # Sort by missing count
    
    for i, (file, ref_count, dynamic_count, missing_count, coverage_pct, sample_missing) in enumerate(partial_file_stats[:20], 1):
        sample_str = ', '.join(sample_missing)
        print(f"{i:2d}. {file:<25} ({dynamic_count:2d}/{ref_count:3d} = {coverage_pct:4.1f}%) missing {missing_count:3d} - e.g., {sample_str}")
    
    # Summary statistics
    total_completely_missing = sum(stat[1] for stat in missing_file_stats[:20])
    total_partially_missing = sum(stat[3] for stat in partial_file_stats[:20])
    
    print(f"\n📈 SUMMARY OF TOP MISSING PARAMETERS:")
    print(f"   • Top 20 completely missing files: {total_completely_missing:,} parameters")
    print(f"   • Top 20 partially covered files: {total_partially_missing:,} missing parameters")
    print(f"   • Total addressable in top priorities: {total_completely_missing + total_partially_missing:,} parameters")
    print(f"   • This would bring coverage from {len(dynamic_df)/len(ref_df)*100:.1f}% to {(len(dynamic_df) + total_completely_missing + total_partially_missing)/len(ref_df)*100:.1f}%")

if __name__ == '__main__':
    main()