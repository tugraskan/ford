#!/usr/bin/env python
"""
Example: Demonstrating the file classification system.

This script shows how the classifier can automatically determine file types
based on their structure, matching (or suggesting improvements to) the 
classifications provided in the problem statement.
"""

from ford.file_classifier import FileClassifier
import tempfile
import os

# Sample file definitions based on the problem statement
SAMPLE_FILES = {
    # Simple files - tabular data
    'time.sim': """
1  2020  2025
2  1     365
""",
    'object.cnt': """
obj_type  count
hru       100
channel   25
reservoir 5
""",
    'codes.bsn': """
code  name        value
1     pet_method  1
2     rte_method  2
3     sed_method  3
""",
    'pcp.cli': """
date        pcp
2020-01-01  5.2
2020-01-02  0.0
2020-01-03  2.1
2020-01-04  0.0
2020-01-05  3.5
""",
    'channel.cha': """
id  name      width  depth  slope
1   chan001   10.5   2.5    0.02
2   chan002   12.3   2.8    0.03
3   chan003   9.8    2.2    0.025
""",
    'hru-data.hru': """
id  name    area   slope  soil
1   hru001  50.5   0.05   clay
2   hru002  45.2   0.03   loam
3   hru003  55.8   0.07   sand
""",
    
    # Connect files - link components
    'hru.con': """
hru_id  channel_id  aquifer_id  reservoir_id
1       101         201         301
2       102         202         302
3       103         203         303
""",
    'channel.con': """
chan_id  upstream_id  downstream_id  type
1        0            2              main
2        1            3              main
3        2            4              main
""",
    'reservoir.con': """
res_id  hru_id  channel_id  outflow_type
1       10      100         controlled
2       20      200         spillway
""",
    'aqu_cha.lin': """
aquifer_id  channel_id  connection_type
1           10          seepage
2           20          seepage
3           30          direct
""",
    
    # Unique files - configuration/master files
    'file.cio': """
master_file_version: 2.0
project_name: test_swat
base_year: 2020
num_years: 10
output_interval: daily
""",
    'management.sch': """
schedule_definition
operations:
  - plant: corn
  - fertilize: nitrogen
  - harvest: grain
""",
    'weather-wgn.cli': """
weather_generator_config
method: richardson
stations: 5
generate_missing: true
""",
    'rout_unit.def': """
routing_unit_definitions
num_units: 25
routing_method: variable_storage
""",
    'plant.ini': """
plant_initialization
default_lai: 0.05
default_cover: 0.0
""",
}

def main():
    """Demonstrate the file classification system."""
    
    print("=" * 70)
    print("FILE CLASSIFICATION SYSTEM DEMONSTRATION")
    print("=" * 70)
    print()
    print("This demonstrates automatic file classification based on structure")
    print("rather than hardcoded filename mappings.")
    print()
    
    classifier = FileClassifier()
    
    # Create temporary files and classify them
    results = {
        'Simple': [],
        'Unique': [],
        'Connect': [],
        'Unknown': []
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        for filename, content in SAMPLE_FILES.items():
            filepath = os.path.join(tmpdir, filename)
            with open(filepath, 'w') as f:
                f.write(content.strip())
            
            classification = classifier.classify(filepath)
            results[classification].append(filename)
    
    # Display results by classification
    for classification in ['Simple', 'Unique', 'Connect', 'Unknown']:
        if results[classification]:
            print(f"\n{classification.upper()} FILES:")
            print("-" * 40)
            for filename in sorted(results[classification]):
                print(f"  • {filename}")
    
    print()
    print("=" * 70)
    print("CLASSIFICATION SUMMARY")
    print("=" * 70)
    print(f"Simple:   {len(results['Simple'])} files  (tabular data)")
    print(f"Unique:   {len(results['Unique'])} files  (configuration/master)")
    print(f"Connect:  {len(results['Connect'])} files (component linkage)")
    print(f"Unknown:  {len(results['Unknown'])} files (unclassified)")
    print()
    
    # Show the benefits
    print("=" * 70)
    print("BENEFITS OF STRUCTURE-BASED CLASSIFICATION")
    print("=" * 70)
    print()
    print("✓ No hardcoded filename mappings required")
    print("✓ Works with renamed files or custom extensions")
    print("✓ Based on actual file content and structure")
    print("✓ Easy to extend with new classification types")
    print("✓ Handles unknown file types gracefully")
    print()
    
    # Show some detailed analysis
    print("=" * 70)
    print("STRUCTURAL ANALYSIS EXAMPLE")
    print("=" * 70)
    print()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Analyze a Simple file
        filepath = os.path.join(tmpdir, 'pcp.cli')
        with open(filepath, 'w') as f:
            f.write(SAMPLE_FILES['pcp.cli'].strip())
        
        structure = classifier._analyze_structure(filepath)
        print("File: pcp.cli (Simple)")
        print(f"  Lines: {structure.num_lines}")
        print(f"  Avg Columns: {structure.num_columns_avg:.1f}")
        print(f"  Tables: {structure.num_tables}")
        print(f"  Has Header: {structure.has_header}")
        print(f"  Has References: {structure.has_references}")
        print()
        
        # Analyze a Connect file
        filepath = os.path.join(tmpdir, 'hru.con')
        with open(filepath, 'w') as f:
            f.write(SAMPLE_FILES['hru.con'].strip())
        
        structure = classifier._analyze_structure(filepath)
        print("File: hru.con (Connect)")
        print(f"  Lines: {structure.num_lines}")
        print(f"  Avg Columns: {structure.num_columns_avg:.1f}")
        print(f"  Tables: {structure.num_tables}")
        print(f"  Has Header: {structure.has_header}")
        print(f"  Has References: {structure.has_references}")
        print()
        
        # Analyze a Unique file
        filepath = os.path.join(tmpdir, 'file.cio')
        with open(filepath, 'w') as f:
            f.write(SAMPLE_FILES['file.cio'].strip())
        
        structure = classifier._analyze_structure(filepath)
        print("File: file.cio (Unique)")
        print(f"  Lines: {structure.num_lines}")
        print(f"  Avg Columns: {structure.num_columns_avg:.1f}")
        print(f"  Tables: {structure.num_tables}")
        print(f"  Mixed Structure: {structure.has_mixed_structure}")
        print(f"  Keyword Density: {structure.keyword_density:.2f}")
        print()


if __name__ == '__main__':
    main()
