#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ford.compare
============

This module provides functionality to compare FORD documentation metadata
between two different commits or versions of a Fortran project.

It can identify:
- New, modified, or removed input files (source files)
- New, modified, or removed modules and submodules
- New, modified, or removed subroutines and functions
- Changes to derived types used in procedure inputs/outputs
- Changes to public module variables that affect the API interface
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ComparisonResult:
    """Container for comparison results between two versions"""

    # Source files
    new_files: Set[str] = field(default_factory=set)
    removed_files: Set[str] = field(default_factory=set)
    modified_files: Set[str] = field(default_factory=set)

    # Modules
    new_modules: Set[str] = field(default_factory=set)
    removed_modules: Set[str] = field(default_factory=set)
    modified_modules: Set[str] = field(default_factory=set)

    # Procedures (functions and subroutines)
    new_procedures: Set[str] = field(default_factory=set)
    removed_procedures: Set[str] = field(default_factory=set)
    modified_procedures: Set[str] = field(default_factory=set)

    # Types
    new_types: Set[str] = field(default_factory=set)
    removed_types: Set[str] = field(default_factory=set)
    modified_types: Set[str] = field(default_factory=set)

    # Variables
    new_variables: Set[str] = field(default_factory=set)
    removed_variables: Set[str] = field(default_factory=set)
    modified_variables: Set[str] = field(default_factory=set)


def load_metadata(json_path: Path) -> Dict[str, Any]:
    """
    Load FORD metadata from a JSON file.

    Args:
        json_path: Path to the modules.json file

    Returns:
        Dictionary containing the metadata

    Raises:
        FileNotFoundError: If the JSON file doesn't exist
        json.JSONDecodeError: If the JSON is malformed
    """
    if not json_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_module_names(metadata: Dict[str, Any]) -> Set[str]:
    """Extract module names from metadata"""
    modules = set()
    for module in metadata.get("modules", []):
        if module and "name" in module:
            modules.add(module["name"])
    return modules


def extract_procedure_names(metadata: Dict[str, Any]) -> Set[str]:
    """Extract procedure names (functions and subroutines) from metadata"""
    procedures = set()
    for module in metadata.get("modules", []):
        if not module:
            continue
        # Get functions
        for func in module.get("functions", []):
            if func and "name" in func:
                procedures.add(f"{module['name']}::{func['name']}")
        # Get subroutines
        for sub in module.get("subroutines", []):
            if sub and "name" in sub:
                procedures.add(f"{module['name']}::{sub['name']}")
    return procedures


def extract_procedure_argument_types(metadata: Dict[str, Any]) -> Set[str]:
    """
    Extract derived types that are used in procedure arguments (inputs/outputs).
    Only tracks types that affect the interface of procedures.
    """
    io_types = set()

    for module in metadata.get("modules", []):
        if not module:
            continue

        module_name = module.get("name", "")

        # Check all procedures (functions and subroutines)
        for proc_list in [module.get("functions", []), module.get("subroutines", [])]:
            for proc in proc_list:
                if not proc:
                    continue

                # Check procedure arguments for type usage
                # The 'args' field contains argument information
                args = proc.get("args", [])

                # If args is a list of dictionaries with type info
                if isinstance(args, list):
                    for arg in args:
                        if isinstance(arg, dict):
                            # Check if argument uses a derived type
                            arg_type = arg.get("vartype", "") or arg.get("type", "")
                            if arg_type and "type(" in arg_type.lower():
                                # Extract type name from type(typename)
                                import re

                                match = re.search(
                                    r"type\s*\(\s*(\w+)\s*\)", arg_type, re.IGNORECASE
                                )
                                if match:
                                    type_name = match.group(1)
                                    io_types.add(f"{module_name}::{type_name}")

                # Check return type for functions
                if proc.get("obj") == "function":
                    ret_type = proc.get("retvar", {})
                    if isinstance(ret_type, dict):
                        ret_vartype = ret_type.get("vartype", "") or ret_type.get(
                            "type", ""
                        )
                        if ret_vartype and "type(" in ret_vartype.lower():
                            import re

                            match = re.search(
                                r"type\s*\(\s*(\w+)\s*\)", ret_vartype, re.IGNORECASE
                            )
                            if match:
                                type_name = match.group(1)
                                io_types.add(f"{module_name}::{type_name}")

    return io_types


def extract_type_names(metadata: Dict[str, Any]) -> Set[str]:
    """
    Extract derived type names that are used in procedure inputs/outputs.
    This focuses only on types that affect the API interface.
    """
    return extract_procedure_argument_types(metadata)


def extract_variable_names(metadata: Dict[str, Any]) -> Set[str]:
    """
    Extract public module-level variables that could be used as inputs/outputs.
    Only tracks variables that are publicly accessible and could affect the module interface.
    """
    variables = set()
    for module in metadata.get("modules", []):
        if not module:
            continue

        # Only extract public variables
        pub_vars = module.get("pub_vars", [])
        if isinstance(pub_vars, list):
            for var in pub_vars:
                if var and isinstance(var, dict) and "name" in var:
                    variables.add(f"{module['name']}::{var['name']}")

        # Fallback: check variables with public permission
        for var in module.get("variables", []):
            if var and "name" in var:
                # Check if variable is public (default assumption if not specified)
                permission = var.get("permission", "public")
                if permission == "public" or permission == "protected":
                    variables.add(f"{module['name']}::{var['name']}")

    return variables


def extract_file_info(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract file information from metadata.

    Returns a dictionary mapping file paths to their metadata
    """
    files = {}
    for module in metadata.get("modules", []):
        if not module:
            continue
        # Some modules may have file information
        if "external_url" in module:
            # Extract filename from URL if present
            url = module["external_url"]
            # This is a simplified extraction - actual implementation may vary
            files[module["name"]] = module
    return files


def compare_metadata(
    old_metadata: Dict[str, Any], new_metadata: Dict[str, Any]
) -> ComparisonResult:
    """
    Compare two metadata dictionaries and identify differences.

    Args:
        old_metadata: Metadata from the older version
        new_metadata: Metadata from the newer version

    Returns:
        ComparisonResult containing all identified differences
    """
    result = ComparisonResult()

    # Compare modules
    old_modules = extract_module_names(old_metadata)
    new_modules = extract_module_names(new_metadata)
    result.new_modules = new_modules - old_modules
    result.removed_modules = old_modules - new_modules
    result.modified_modules = (
        old_modules & new_modules
    )  # Simplified - could be enhanced

    # Compare procedures
    old_procedures = extract_procedure_names(old_metadata)
    new_procedures = extract_procedure_names(new_metadata)
    result.new_procedures = new_procedures - old_procedures
    result.removed_procedures = old_procedures - new_procedures

    # Compare types
    old_types = extract_type_names(old_metadata)
    new_types = extract_type_names(new_metadata)
    result.new_types = new_types - old_types
    result.removed_types = old_types - new_types

    # Compare variables
    old_variables = extract_variable_names(old_metadata)
    new_variables = extract_variable_names(new_metadata)
    result.new_variables = new_variables - old_variables
    result.removed_variables = old_variables - new_variables

    # Compare files (simplified version)
    old_files = extract_file_info(old_metadata)
    new_files = extract_file_info(new_metadata)
    result.new_files = set(new_files.keys()) - set(old_files.keys())
    result.removed_files = set(old_files.keys()) - set(new_files.keys())

    return result


def format_report(result: ComparisonResult, verbose: bool = False) -> str:
    """
    Format a comparison result into a readable report.

    Args:
        result: The comparison result to format
        verbose: If True, include more detailed information

    Returns:
        A formatted string report
    """
    lines = []
    lines.append("=" * 80)
    lines.append("FORD Metadata Comparison Report")
    lines.append("=" * 80)
    lines.append("")

    # Modules section
    lines.append("MODULES")
    lines.append("-" * 80)
    if result.new_modules:
        lines.append(f"  New modules ({len(result.new_modules)}):")
        for module in sorted(result.new_modules):
            lines.append(f"    + {module}")
    if result.removed_modules:
        lines.append(f"  Removed modules ({len(result.removed_modules)}):")
        for module in sorted(result.removed_modules):
            lines.append(f"    - {module}")
    if not result.new_modules and not result.removed_modules:
        lines.append("  No module changes detected")
    lines.append("")

    # Procedures section
    lines.append("PROCEDURES (Functions and Subroutines)")
    lines.append("-" * 80)
    if result.new_procedures:
        lines.append(f"  New procedures ({len(result.new_procedures)}):")
        for proc in sorted(result.new_procedures):
            lines.append(f"    + {proc}")
    if result.removed_procedures:
        lines.append(f"  Removed procedures ({len(result.removed_procedures)}):")
        for proc in sorted(result.removed_procedures):
            lines.append(f"    - {proc}")
    if not result.new_procedures and not result.removed_procedures:
        lines.append("  No procedure changes detected")
    lines.append("")

    # Types section
    lines.append("DERIVED TYPES (Used in Procedure Inputs/Outputs)")
    lines.append("-" * 80)
    if result.new_types:
        lines.append(
            f"  New types used in procedure arguments ({len(result.new_types)}):"
        )
        for dtype in sorted(result.new_types):
            lines.append(f"    + {dtype}")
    if result.removed_types:
        lines.append(
            f"  Removed types used in procedure arguments ({len(result.removed_types)}):"
        )
        for dtype in sorted(result.removed_types):
            lines.append(f"    - {dtype}")
    if not result.new_types and not result.removed_types:
        lines.append("  No changes to types used in procedure arguments")
    lines.append("")

    # Variables section
    if verbose:
        lines.append("PUBLIC MODULE VARIABLES")
        lines.append("-" * 80)
        if result.new_variables:
            lines.append(f"  New public variables ({len(result.new_variables)}):")
            for var in sorted(result.new_variables):
                lines.append(f"    + {var}")
        if result.removed_variables:
            lines.append(
                f"  Removed public variables ({len(result.removed_variables)}):"
            )
            for var in sorted(result.removed_variables):
                lines.append(f"    - {var}")
        if not result.new_variables and not result.removed_variables:
            lines.append("  No public variable changes detected")
        lines.append("")

    # Files section
    lines.append("SOURCE FILES")
    lines.append("-" * 80)
    if result.new_files:
        lines.append(f"  New files ({len(result.new_files)}):")
        for fname in sorted(result.new_files):
            lines.append(f"    + {fname}")
    if result.removed_files:
        lines.append(f"  Removed files ({len(result.removed_files)}):")
        for fname in sorted(result.removed_files):
            lines.append(f"    - {fname}")
    if not result.new_files and not result.removed_files:
        lines.append("  No file changes detected")
    lines.append("")

    # Summary
    lines.append("=" * 80)
    lines.append("SUMMARY")
    lines.append("=" * 80)
    total_changes = (
        len(result.new_modules)
        + len(result.removed_modules)
        + len(result.new_procedures)
        + len(result.removed_procedures)
        + len(result.new_types)
        + len(result.removed_types)
        + len(result.new_files)
        + len(result.removed_files)
    )
    lines.append(f"Total changes detected: {total_changes}")
    lines.append(
        f"  Modules: +{len(result.new_modules)} -{len(result.removed_modules)}"
    )
    lines.append(
        f"  Procedures: +{len(result.new_procedures)} -{len(result.removed_procedures)}"
    )
    lines.append(f"  Types: +{len(result.new_types)} -{len(result.removed_types)}")
    lines.append(f"  Files: +{len(result.new_files)} -{len(result.removed_files)}")
    lines.append("=" * 80)

    return "\n".join(lines)


def compare_commits(
    old_json: Path,
    new_json: Path,
    output_file: Optional[Path] = None,
    verbose: bool = False,
) -> ComparisonResult:
    """
    Compare FORD metadata between two commits.

    Args:
        old_json: Path to the older metadata JSON file
        new_json: Path to the newer metadata JSON file
        output_file: Optional path to write the report to
        verbose: Include detailed information in the report

    Returns:
        ComparisonResult object containing the differences
    """
    old_metadata = load_metadata(old_json)
    new_metadata = load_metadata(new_json)

    result = compare_metadata(old_metadata, new_metadata)

    report = format_report(result, verbose=verbose)

    if output_file:
        output_file.write_text(report, encoding="utf-8")
        print(f"Report written to: {output_file}")
    else:
        print(report)

    return result


def main():
    """Command-line interface for comparing FORD metadata"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Compare FORD documentation metadata between two versions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare metadata from two different commits
  ford-compare old_commit/modules.json new_commit/modules.json
  
  # Save the comparison report to a file
  ford-compare old.json new.json -o comparison_report.txt
  
  # Include detailed variable information
  ford-compare old.json new.json --verbose
        """,
    )

    parser.add_argument(
        "old_metadata", type=Path, help="Path to the older metadata JSON file"
    )
    parser.add_argument(
        "new_metadata", type=Path, help="Path to the newer metadata JSON file"
    )
    parser.add_argument(
        "-o", "--output", type=Path, help="Output file for the comparison report"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Include detailed information (e.g., variables)",
    )

    args = parser.parse_args()

    try:
        compare_commits(
            args.old_metadata,
            args.new_metadata,
            output_file=args.output,
            verbose=args.verbose,
        )
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
