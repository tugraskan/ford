#!/usr/bin/env python3
"""
Compare Analysis Formats: Enhanced File.cio vs Modular Database_5_15_24_nbs

This script compares the two output formats generated from the same comprehensive 
file.cio ecosystem analysis logic.
"""

import pandas as pd
import argparse
from pathlib import Path

def analyze_enhanced_format(file_path):
    """Analyze the enhanced file.cio ecosystem analysis format"""
    df = pd.read_csv(file_path)
    
    analysis = {
        'total_parameters': len(df),
        'total_files': df['SWAT_File'].nunique(),
        'classifications': df['Classification'].value_counts().to_dict(),
        'top_files': df['SWAT_File'].value_counts().head(10).to_dict(),
        'source_procedures': df['Source_Procedure'].nunique(),
        'data_types': df['Data_Type'].value_counts().to_dict()
    }
    
    return analysis, df

def analyze_modular_format(file_path):
    """Analyze the Modular Database_5_15_24_nbs format"""
    df = pd.read_csv(file_path)
    
    analysis = {
        'total_parameters': len(df),
        'total_files': df['SWAT_File'].nunique(),
        'classifications': df['Broad_Classification'].value_counts().to_dict(),
        'top_files': df['SWAT_File'].value_counts().head(10).to_dict(),
        'source_procedures': 'N/A',  # Not directly comparable
        'data_types': df['Data_Type'].value_counts().to_dict()
    }
    
    return analysis, df

def compare_formats(enhanced_file, modular_file):
    """Compare the two formats"""
    print("🔍 ANALYSIS FORMAT COMPARISON")
    print("="*60)
    
    # Load and analyze both formats
    enhanced_analysis, enhanced_df = analyze_enhanced_format(enhanced_file)
    modular_analysis, modular_df = analyze_modular_format(modular_file)
    
    print("\n📊 BASIC STATISTICS")
    print("-" * 30)
    print(f"Enhanced Format:")
    print(f"  Total Parameters: {enhanced_analysis['total_parameters']:,}")
    print(f"  Total Files: {enhanced_analysis['total_files']}")
    print(f"  Source Procedures: {enhanced_analysis['source_procedures']}")
    
    print(f"\nModular Format:")
    print(f"  Total Parameters: {modular_analysis['total_parameters']:,}")
    print(f"  Total Files: {modular_analysis['total_files']}")
    print(f"  Structured Records: Yes")
    
    # Compare parameter counts
    ratio = modular_analysis['total_parameters'] / enhanced_analysis['total_parameters']
    print(f"\nParameter Ratio: {ratio:.2f}x (Modular vs Enhanced)")
    
    print("\n🏷️  CLASSIFICATION COMPARISON")
    print("-" * 35)
    
    # Get all unique classifications
    all_classifications = set(enhanced_analysis['classifications'].keys()) | set(modular_analysis['classifications'].keys())
    
    print(f"{'Classification':<15} {'Enhanced':<10} {'Modular':<10} {'Diff':<8}")
    print("-" * 45)
    
    for classification in sorted(all_classifications):
        enhanced_count = enhanced_analysis['classifications'].get(classification, 0)
        modular_count = modular_analysis['classifications'].get(classification, 0)
        diff = modular_count - enhanced_count
        diff_str = f"+{diff}" if diff > 0 else str(diff) if diff < 0 else "0"
        
        print(f"{classification:<15} {enhanced_count:<10} {modular_count:<10} {diff_str:<8}")
    
    print("\n📁 TOP FILES COMPARISON")
    print("-" * 40)
    
    # Get top 10 files from each format
    enhanced_top = enhanced_analysis['top_files']
    modular_top = modular_analysis['top_files']
    
    all_top_files = set(list(enhanced_top.keys())[:10]) | set(list(modular_top.keys())[:10])
    
    print(f"{'Filename':<20} {'Enhanced':<10} {'Modular':<10} {'Diff':<8}")
    print("-" * 50)
    
    for filename in list(all_top_files)[:15]:
        enhanced_count = enhanced_top.get(filename, 0)
        modular_count = modular_top.get(filename, 0)
        diff = modular_count - enhanced_count
        diff_str = f"+{diff}" if diff > 0 else str(diff) if diff < 0 else "0"
        
        print(f"{filename:<20} {enhanced_count:<10} {modular_count:<10} {diff_str:<8}")
    
    print("\n🔢 DATA TYPE COMPARISON")
    print("-" * 30)
    
    enhanced_types = enhanced_analysis['data_types']
    modular_types = modular_analysis['data_types']
    
    all_types = set(enhanced_types.keys()) | set(modular_types.keys())
    
    print(f"{'Data Type':<12} {'Enhanced':<10} {'Modular':<10} {'Diff':<8}")
    print("-" * 42)
    
    for data_type in sorted(all_types):
        enhanced_count = enhanced_types.get(data_type, 0)
        modular_count = modular_types.get(data_type, 0)
        diff = modular_count - enhanced_count
        diff_str = f"+{diff}" if diff > 0 else str(diff) if diff < 0 else "0"
        
        print(f"{data_type:<12} {enhanced_count:<10} {modular_count:<10} {diff_str:<8}")
    
    print("\n📋 FORMAT ANALYSIS")
    print("-" * 20)
    
    print("Enhanced Format Features:")
    print("  ✅ Detailed I/O procedure traceability")
    print("  ✅ Original parameter names preserved")
    print("  ✅ Source file context included")
    print("  ✅ Comprehensive parameter coverage")
    print("  ❌ Not standardized SWAT+ format")
    
    print("\nModular Format Features:")
    print("  ✅ Standard SWAT+ Modular Database format")
    print("  ✅ Unique ID system")
    print("  ✅ Position and line number tracking")
    print("  ✅ Database table structure")
    print("  ✅ Units and ranges included")
    print("  ❌ Less detailed source traceability")
    
    print("\n🎯 RECOMMENDATION")
    print("-" * 15)
    print("Use Enhanced Format for:")
    print("  • Source code analysis and debugging")
    print("  • Parameter traceability and validation")
    print("  • Understanding I/O operations")
    
    print("\nUse Modular Format for:")
    print("  • SWAT+ model database integration")
    print("  • Standard toolchain compatibility")  
    print("  • Production database applications")
    
    print(f"\n{'='*60}")
    
    # Find common files
    enhanced_files = set(enhanced_df['SWAT_File'].unique())
    modular_files = set(modular_df['SWAT_File'].unique())
    
    common_files = enhanced_files & modular_files
    enhanced_only = enhanced_files - modular_files
    modular_only = modular_files - enhanced_files
    
    print(f"\n📂 FILE COVERAGE ANALYSIS")
    print(f"Common Files: {len(common_files)}")
    print(f"Enhanced Only: {len(enhanced_only)}")
    print(f"Modular Only: {len(modular_only)}")
    
    if enhanced_only:
        print(f"\nFiles only in Enhanced: {list(enhanced_only)[:10]}")
    if modular_only:
        print(f"\nFiles only in Modular: {list(modular_only)[:10]}")

def main():
    parser = argparse.ArgumentParser(description='Compare enhanced and modular database formats')
    parser.add_argument('--enhanced', default='enhanced_file_cio_ecosystem_analysis.csv',
                       help='Enhanced format CSV file')
    parser.add_argument('--modular', default='Modular_Database_5_15_24_nbs.csv',
                       help='Modular format CSV file')
    
    args = parser.parse_args()
    
    enhanced_path = Path(args.enhanced)
    modular_path = Path(args.modular)
    
    if not enhanced_path.exists():
        print(f"❌ Enhanced format file not found: {enhanced_path}")
        return
        
    if not modular_path.exists():
        print(f"❌ Modular format file not found: {modular_path}")
        return
    
    compare_formats(enhanced_path, modular_path)

if __name__ == "__main__":
    main()