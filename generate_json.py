#!/usr/bin/env python3
"""
JSON Export Utility for FORD

This utility processes Fortran source code and exports detailed metadata
to JSON format for external analysis tools.
"""

import argparse
import json
import logging as log
import sys
from pathlib import Path
from typing import List, Optional

from ford.fortran_project import Project
from ford.settings import ProjectSettings


def setup_logging(debug: bool = False) -> None:
    """Configure logging for the utility."""
    level = log.DEBUG if debug else log.INFO
    log.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s'
    )


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate JSON exports from Fortran source code analysis'
    )
    parser.add_argument(
        'src_dirs',
        nargs='+',
        type=Path,
        help='Source directories containing Fortran files'
    )
    parser.add_argument(
        '-o', '--output-dir',
        type=Path,
        default=Path.cwd() / 'json_outputs',
        help='Output directory for JSON files (default: ./json_outputs)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    return parser.parse_args()


def validate_source_dirs(src_dirs: List[Path]) -> List[Path]:
    """Validate that source directories exist and contain Fortran files."""
    valid_dirs = []
    
    for src_dir in src_dirs:
        if not src_dir.exists():
            log.error("Source directory does not exist: %s", src_dir)
            continue
        if not src_dir.is_dir():
            log.error("Source path is not a directory: %s", src_dir)
            continue
        valid_dirs.append(src_dir)
    
    if not valid_dirs:
        log.error("No valid source directories found")
        sys.exit(1)
    
    return valid_dirs


def main() -> None:
    """Main entry point for the JSON export utility."""
    args = parse_args()
    setup_logging(args.debug)
    
    # Validate source directories
    src_dirs = validate_source_dirs(args.src_dirs)
    log.info("Processing source directories: %s", [str(d) for d in src_dirs])
    
    try:
        # Create ProjectSettings with the source directories
        project_settings = ProjectSettings(src_dir=src_dirs)
        
        # Create the project instance
        project = Project(project_settings)
        
        # Correlate the project data (parses and processes the Fortran files)
        log.info("Correlating project data...")
        project.correlate()
        log.info("Project correlation completed")
        
        # Get procedures and process them
        procedures = project.get_procedures()
        log.info("Found %d procedures", len(procedures))
        
        if not procedures:
            log.warning("No procedures found in source directories")
            return
        
        # Cross-walk type dictionaries
        log.info("Cross-walking type dictionaries...")
        project.cross_walk_type_dicts(procedures)
        
        # Generate JSON exports
        log.info("Generating JSON exports...")
        output_dir = str(args.output_dir)
        
        project.procedures_fvar_to_json(procedures, output_dir)
        project.procedures_io_to_json(procedures, output_dir)
        project.procedures_call_to_json(procedures, output_dir)
        
        log.info("JSON export completed successfully")
        log.info("Output written to: %s", args.output_dir)
        
    except Exception as e:
        log.error("Failed to process Fortran source: %s", e)
        if args.debug:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()
