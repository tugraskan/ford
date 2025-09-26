#!/usr/bin/env python3
"""
Analyze Missing Parameters: Compare Dynamic Template Generation vs Original SWAT+ Database

This script identifies which files and parameters are missing from the current dynamic 
template generation compared to the original SWAT+ Modular Database.
"""

import pandas as pd
import argparse
from pathlib import Path
from collections import defaultdict

def load_reference_database(ref_file):
    """Load and parse the reference SWAT+ database"""
    print(f"Loading reference database: {ref_file}")
    
    # Read CSV, handling potential encoding issues
    try:
        df = pd.read_csv(ref_file, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(ref_file, encoding='latin-1')
    
    # Clean up column names (remove BOM if present)
    df.columns = df.columns.str.replace('\ufeff', '')
    
    # Filter out metadata rows and focus on actual parameters
    # Remove rows where SWAT_File is empty, '*', or contains 'parm_list'
    df_clean = df[
        (df['SWAT_File'].notna()) & 
        (df['SWAT_File'] != '*') & 
        (df['SWAT_File'] != '') &
        (~df['SWAT_File'].str.contains('parm_list', na=False))
    ].copy()
    
    print(f"Reference database: {len(df_clean)} parameters across {df_clean['SWAT_File'].nunique()} files")
    return df_clean

def load_dynamic_database(dynamic_file):
    """Load and parse the dynamic template database"""
    print(f"Loading dynamic database: {dynamic_file}")
    
    df = pd.read_csv(dynamic_file)
    print(f"Dynamic database: {len(df)} parameters across {df['SWAT_File'].nunique()} files")
    return df

def analyze_file_coverage(ref_df, dynamic_df):
    """Analyze which files are covered and which are missing"""
    print("\n" + "="*80)
    print("FILE COVERAGE ANALYSIS")
    print("="*80)
    
    ref_files = set(ref_df['SWAT_File'].unique())
    dynamic_files = set(dynamic_df['SWAT_File'].unique())
    
    # Files in reference but not in dynamic (MISSING)
    missing_files = ref_files - dynamic_files
    # Files in dynamic but not in reference (EXTRA)
    extra_files = dynamic_files - ref_files
    # Files in both (COVERED)
    covered_files = ref_files & dynamic_files
    
    print(f"Reference files: {len(ref_files)}")
    print(f"Dynamic files: {len(dynamic_files)}")
    print(f"Covered files: {len(covered_files)} ({len(covered_files)/len(ref_files)*100:.1f}%)")
    print(f"Missing files: {len(missing_files)} ({len(missing_files)/len(ref_files)*100:.1f}%)")
    print(f"Extra files: {len(extra_files)}")
    
    return missing_files, covered_files, extra_files

def analyze_parameter_coverage(ref_df, dynamic_df, covered_files):
    """Analyze parameter coverage for files that exist in both databases"""
    print("\n" + "="*80)
    print("PARAMETER COVERAGE ANALYSIS")
    print("="*80)
    
    coverage_stats = []
    
    for file in sorted(covered_files):
        ref_params = ref_df[ref_df['SWAT_File'] == file]
        dynamic_params = dynamic_df[dynamic_df['SWAT_File'] == file]
        
        ref_count = len(ref_params)
        dynamic_count = len(dynamic_params)
        coverage_pct = (dynamic_count / ref_count * 100) if ref_count > 0 else 0
        
        coverage_stats.append({
            'file': file,
            'ref_count': ref_count,
            'dynamic_count': dynamic_count,
            'coverage_pct': coverage_pct,
            'missing_count': ref_count - dynamic_count
        })
    
    # Sort by missing count (descending) to prioritize
    coverage_stats.sort(key=lambda x: x['missing_count'], reverse=True)
    
    print(f"{'File':<30} {'Ref':<6} {'Dynamic':<8} {'Coverage':<10} {'Missing':<8}")
    print("-" * 70)
    
    total_ref = 0
    total_dynamic = 0
    
    for stat in coverage_stats:
        total_ref += stat['ref_count']
        total_dynamic += stat['dynamic_count']
        
        print(f"{stat['file']:<30} {stat['ref_count']:<6} {stat['dynamic_count']:<8} "
              f"{stat['coverage_pct']:<9.1f}% {stat['missing_count']:<8}")
    
    print("-" * 70)
    overall_coverage = (total_dynamic / total_ref * 100) if total_ref > 0 else 0
    print(f"{'TOTAL':<30} {total_ref:<6} {total_dynamic:<8} {overall_coverage:<9.1f}% {total_ref - total_dynamic:<8}")
    
    return coverage_stats

def analyze_top_missing_files(ref_df, missing_files):
    """Analyze the top missing files by parameter count"""
    print("\n" + "="*80)
    print("TOP MISSING FILES (by parameter count)")
    print("="*80)
    
    missing_stats = []
    
    for file in missing_files:
        ref_params = ref_df[ref_df['SWAT_File'] == file]
        param_count = len(ref_params)
        
        # Get sample parameters for context
        sample_params = ref_params['DATABASE_FIELD_NAME'].head(5).tolist()
        
        missing_stats.append({
            'file': file,
            'param_count': param_count,
            'sample_params': sample_params
        })
    
    # Sort by parameter count (descending)
    missing_stats.sort(key=lambda x: x['param_count'], reverse=True)
    
    print(f"{'File':<30} {'Count':<6} {'Sample Parameters'}")
    print("-" * 80)
    
    for stat in missing_stats[:25]:  # Top 25 missing files
        sample_str = ', '.join(stat['sample_params'][:3])
        if len(stat['sample_params']) > 3:
            sample_str += "..."
        print(f"{stat['file']:<30} {stat['param_count']:<6} {sample_str}")
    
    return missing_stats

def generate_recommendations(missing_files, coverage_stats, missing_stats):
    """Generate actionable recommendations"""
    print("\n" + "="*80)
    print("IMPLEMENTATION RECOMMENDATIONS")
    print("="*80)
    
    # High-impact missing files (>30 parameters)
    high_impact_missing = [stat for stat in missing_stats if stat['param_count'] >= 30]
    
    # Files with poor coverage (<50%)
    poor_coverage = [stat for stat in coverage_stats if stat['coverage_pct'] < 50 and stat['ref_count'] >= 10]
    
    print("🎯 HIGH PRIORITY: Top Missing Files (30+ parameters)")
    print("-" * 60)
    for i, stat in enumerate(high_impact_missing[:10], 1):
        print(f"{i:2d}. {stat['file']:<25} ({stat['param_count']:3d} parameters)")
    
    print("\n🔧 MEDIUM PRIORITY: Files with Poor Coverage (<50%)")
    print("-" * 60)
    for i, stat in enumerate(poor_coverage[:10], 1):
        print(f"{i:2d}. {stat['file']:<25} ({stat['dynamic_count']:2d}/{stat['ref_count']:2d} = {stat['coverage_pct']:.1f}%)")
    
    # Calculate potential impact
    high_impact_total = sum(stat['param_count'] for stat in high_impact_missing[:10])
    poor_coverage_missing = sum(stat['missing_count'] for stat in poor_coverage[:10])
    
    print(f"\n📊 POTENTIAL IMPACT:")
    print(f"   • Adding top 10 missing files: +{high_impact_total} parameters")
    print(f"   • Improving top 10 poor coverage: +{poor_coverage_missing} parameters")
    print(f"   • Combined potential increase: +{high_impact_total + poor_coverage_missing} parameters")
    
    current_total = sum(stat['dynamic_count'] for stat in coverage_stats)
    potential_total = current_total + high_impact_total + poor_coverage_missing
    ref_total = sum(stat['ref_count'] for stat in coverage_stats) + sum(stat['param_count'] for stat in missing_stats)
    
    current_pct = (current_total / ref_total * 100) if ref_total > 0 else 0
    potential_pct = (potential_total / ref_total * 100) if ref_total > 0 else 0
    
    print(f"   • Current coverage: {current_total:,} / {ref_total:,} = {current_pct:.1f}%")
    print(f"   • Potential coverage: {potential_total:,} / {ref_total:,} = {potential_pct:.1f}%")
    print(f"   • Improvement: +{potential_pct - current_pct:.1f} percentage points")

def main():
    parser = argparse.ArgumentParser(description='Analyze missing parameters in dynamic template generation')
    parser.add_argument('--reference', '-r', 
                       default='test_data/Modular Database_5_15_24_nbs.csv',
                       help='Reference SWAT+ database file')
    parser.add_argument('--dynamic', '-d',
                       default='dynamic_analysis/dynamic_modular_database.csv', 
                       help='Dynamic template database file')
    
    args = parser.parse_args()
    
    # Load databases
    ref_df = load_reference_database(args.reference)
    dynamic_df = load_dynamic_database(args.dynamic)
    
    # Analyze coverage
    missing_files, covered_files, extra_files = analyze_file_coverage(ref_df, dynamic_df)
    coverage_stats = analyze_parameter_coverage(ref_df, dynamic_df, covered_files)
    missing_stats = analyze_top_missing_files(ref_df, missing_files)
    
    # Generate recommendations
    generate_recommendations(missing_files, coverage_stats, missing_stats)
    
    print(f"\n✅ Analysis complete! Current dynamic database covers {len(dynamic_df):,} parameters.")
    print(f"📈 Reference database contains {len(ref_df):,} parameters for comparison.")

if __name__ == '__main__':
    main()