#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utility Script: Generate and Compare FORD Metadata

This utility helps generate FORD metadata and compare it between different
versions of a Fortran project.

Usage:
    # Generate metadata for a project
    python ford_diff_utility.py generate ford.md

    # Compare two metadata files
    python ford_diff_utility.py compare old_modules.json new_modules.json
    
    # Compare two different directories
    python ford_diff_utility.py compare-dirs old_project/ new_project/ ford.md
"""

import sys
import json
from pathlib import Path
from typing import Optional

# Try to import FORD modules
try:
    from ford import main as ford_main
    from ford.settings import load_markdown_settings, load_toml_settings
    from ford.compare import compare_commits, load_metadata, compare_metadata, format_report
except ImportError:
    print("Error: FORD modules not found. Make sure FORD is installed.")
    print("Run: pip install -e . from the FORD repository root")
    sys.exit(1)


def generate_metadata(project_file: Path, output_dir: Optional[Path] = None) -> Path:
    """
    Generate FORD documentation and extract metadata.
    
    Args:
        project_file: Path to FORD project file (.md or .toml)
        output_dir: Optional custom output directory
        
    Returns:
        Path to the generated modules.json file
    """
    if not project_file.exists():
        raise FileNotFoundError(f"Project file not found: {project_file}")
    
    project_dir = project_file.parent if project_file.parent != Path('.') else Path.cwd()
    
    # Load settings based on file extension
    if str(project_file).endswith('.toml'):
        settings, docs = load_toml_settings(project_dir, project_file.name)
    else:
        settings, docs = load_markdown_settings(project_dir, str(project_file), project_file.name)
    
    # Enable externalization to generate modules.json
    settings.externalize = True
    
    if output_dir:
        settings.output_dir = output_dir
    
    print(f"Generating FORD documentation...")
    print(f"  Project file: {project_file}")
    print(f"  Output directory: {settings.output_dir}")
    
    # Run FORD
    ford_main(settings, docs)
    
    metadata_path = settings.output_dir / 'modules.json'
    
    if metadata_path.exists():
        print(f"✓ Metadata generated: {metadata_path}")
        return metadata_path
    else:
        raise RuntimeError(f"Failed to generate metadata at {metadata_path}")


def compare_metadata_files(old_file: Path, new_file: Path, 
                           output: Optional[Path] = None,
                           verbose: bool = False) -> None:
    """
    Compare two FORD metadata JSON files.
    
    Args:
        old_file: Path to older metadata file
        new_file: Path to newer metadata file
        output: Optional output file for the report
        verbose: Include detailed information
    """
    print(f"Loading metadata files...")
    print(f"  Old: {old_file}")
    print(f"  New: {new_file}")
    print()
    
    result = compare_commits(old_file, new_file, output_file=output, verbose=verbose)


def compare_directories(old_dir: Path, new_dir: Path, 
                       project_file: str,
                       output: Optional[Path] = None) -> None:
    """
    Compare FORD metadata between two project directories.
    
    Args:
        old_dir: Directory with older version
        new_dir: Directory with newer version
        project_file: Name of FORD project file
        output: Optional output file for the report
    """
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        print("Generating metadata for old version...")
        old_project = old_dir / project_file
        old_output = temp_path / 'old_output'
        old_metadata = generate_metadata(old_project, old_output)
        
        print("\nGenerating metadata for new version...")
        new_project = new_dir / project_file
        new_output = temp_path / 'new_output'
        new_metadata = generate_metadata(new_project, new_output)
        
        print("\n" + "=" * 80)
        compare_metadata_files(old_metadata, new_metadata, output=output, verbose=True)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='FORD metadata generation and comparison utility',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', 
                                       help='Generate FORD metadata')
    gen_parser.add_argument('project_file', type=Path,
                           help='Path to FORD project file (.md or .toml)')
    gen_parser.add_argument('-o', '--output', type=Path,
                           help='Output directory (default: from project file)')
    
    # Compare command
    cmp_parser = subparsers.add_parser('compare',
                                       help='Compare two metadata files')
    cmp_parser.add_argument('old_metadata', type=Path,
                           help='Path to old modules.json')
    cmp_parser.add_argument('new_metadata', type=Path,
                           help='Path to new modules.json')
    cmp_parser.add_argument('-o', '--output', type=Path,
                           help='Output file for comparison report')
    cmp_parser.add_argument('-v', '--verbose', action='store_true',
                           help='Include detailed information')
    
    # Compare directories command
    cmpdir_parser = subparsers.add_parser('compare-dirs',
                                          help='Compare two project directories')
    cmpdir_parser.add_argument('old_dir', type=Path,
                              help='Path to old project directory')
    cmpdir_parser.add_argument('new_dir', type=Path,
                              help='Path to new project directory')
    cmpdir_parser.add_argument('project_file',
                              help='Name of FORD project file')
    cmpdir_parser.add_argument('-o', '--output', type=Path,
                              help='Output file for comparison report')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'generate':
            generate_metadata(args.project_file, args.output)
            
        elif args.command == 'compare':
            compare_metadata_files(args.old_metadata, args.new_metadata,
                                  args.output, getattr(args, 'verbose', False))
            
        elif args.command == 'compare-dirs':
            compare_directories(args.old_dir, args.new_dir,
                              args.project_file, args.output)
        
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 2


if __name__ == '__main__':
    sys.exit(main())
