#!/usr/bin/env python3
"""
Demo: Dynamic Template Generation for FORD Modular Database

This demonstrates how dynamic templates are generated from FORD JSON outputs
instead of using static hardcoded templates.

Key Benefits:
- Templates are generated directly from source code analysis
- No manual maintenance of template definitions required  
- Parameters reflect actual file reading operations in the code
- Complete file structure mapping with line positions
"""

import os
import sys
from pathlib import Path

# Add current directory to path so we can import our generator
sys.path.insert(0, os.getcwd())

from dynamic_modular_database_generator import DynamicModularDatabaseGenerator

def demonstrate_dynamic_templates():
    """Demonstrate dynamic template generation"""
    print("=" * 70)
    print("FORD Dynamic Modular Database Template Generation Demo")
    print("=" * 70)
    print()
    
    # Initialize generator
    json_dir = "json_outputs"
    output_dir = "demo_dynamic_output"
    
    if not os.path.exists(json_dir):
        print(f"❌ Error: {json_dir} directory not found")
        print("Please run FORD first to generate JSON outputs")
        return
    
    print(f"📁 Input directory: {json_dir}")
    print(f"📁 Output directory: {output_dir}")
    print()
    
    # Create generator
    generator = DynamicModularDatabaseGenerator(json_dir, output_dir)
    
    # Step 1: Load and analyze JSON files
    print("🔍 Step 1: Loading and analyzing FORD JSON files...")
    generator.load_and_analyze_json_files()
    
    print(f"   ✅ Analyzed {len(generator.io_operations)} I/O procedures")
    print(f"   ✅ Discovered {len(generator.file_structures)} input files with parameters")
    print()
    
    # Show some discovered files
    print("📋 Some discovered file structures:")
    for i, (file_name, structure) in enumerate(generator.file_structures.items()):
        if i >= 10:  # Show first 10
            break
        print(f"   • {file_name}: {len(structure['parameters'])} parameters")
    
    if len(generator.file_structures) > 10:
        print(f"   ... and {len(generator.file_structures) - 10} more files")
    print()
    
    # Step 2: Generate dynamic templates  
    print("🛠️  Step 2: Generating dynamic templates...")
    generator.generate_dynamic_templates()
    
    print(f"   ✅ Generated {len(generator.parameters)} parameters")
    print()
    
    # Show classification breakdown
    classifications = {}
    for param in generator.parameters:
        cls = param['Broad_Classification']
        classifications[cls] = classifications.get(cls, 0) + 1
    
    print("📊 Parameters by classification:")
    for cls, count in sorted(classifications.items()):
        print(f"   • {cls}: {count} parameters")
    print()
    
    # Step 3: Export results
    print("💾 Step 3: Exporting results...")
    generator.export_to_csv()
    generator.generate_analysis_report()
    
    print(f"   ✅ CSV database: {output_dir}/dynamic_modular_database.csv")
    print(f"   ✅ Analysis report: {output_dir}/dynamic_template_analysis.md")
    print()
    
    # Show example of file.cio parameters if found
    file_cio_params = [p for p in generator.parameters if p['SWAT_File'] == 'file.cio']
    if file_cio_params:
        print("📄 Example: file.cio parameters (first 10):")
        for i, param in enumerate(file_cio_params[:10]):
            print(f"   • Line {param['Line_in_file']}, Pos {param['Position_in_File']}: {param['DATABASE_FIELD_NAME']} ({param['Data_Type']})")
        if len(file_cio_params) > 10:
            print(f"   ... and {len(file_cio_params) - 10} more file.cio parameters")
        print()
    
    print("🎉 Dynamic template generation complete!")
    print()
    print("🔍 Key advantages of dynamic templates:")
    print("   ✅ Extracted from actual source code I/O operations")
    print("   ✅ No hardcoded templates to maintain")
    print("   ✅ Reflects real file structures and parameter positions")
    print("   ✅ Automatically discovers new files and parameters")
    print("   ✅ Intelligent type and unit inference")
    print()
    
    # Compare with static approach
    print("📈 Comparison with static templates:")
    print("   🔸 Static: Manual template definition, limited coverage")  
    print("   🔸 Dynamic: Automatic discovery, comprehensive coverage")
    print("   🔸 Static: Fixed parameter sets")
    print("   🔸 Dynamic: Adapts to actual source code")
    print()
    
    return generator

def show_file_analysis_example(generator):
    """Show detailed analysis of a specific file"""
    if 'file.cio' not in generator.file_structures:
        print("file.cio not found in analysis")
        return
    
    print("=" * 50)
    print("Detailed Analysis Example: file.cio")
    print("=" * 50)
    
    structure = generator.file_structures['file.cio']
    
    print(f"File: {structure['file_name']}")
    print(f"Total parameters: {len(structure['parameters'])}")
    print(f"Total lines: {structure['total_lines']}")
    print()
    
    print("Headers found:")
    for header in structure['headers']:
        print(f"   • {header}")
    print()
    
    print("Parameter details (first 15):")
    for i, param in enumerate(structure['parameters'][:15]):
        print(f"   {i+1:2d}. {param['name']} (Line {param['line']}, {param['data_type']}, {param['units']})")
        print(f"       {param['description']}")
    
    if len(structure['parameters']) > 15:
        print(f"   ... and {len(structure['parameters']) - 15} more parameters")

if __name__ == "__main__":
    # Run the demonstration
    generator = demonstrate_dynamic_templates()
    
    if generator and generator.file_structures:
        print()
        show_file_analysis_example(generator)