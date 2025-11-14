#!/usr/bin/env python3
"""
Control Flow Graph Shape and Color Reference Tool

This script displays the shape and color combinations used in FORD's
control flow graphs in a nicely formatted table.

Usage:
    python show_cfg_colors.py [--format FORMAT]

Format options:
    - table (default): Display as a formatted table
    - json: Display as JSON
    - markdown: Display as a markdown table
"""

import argparse
import json
from enum import Enum


class BlockType(Enum):
    """Types of basic blocks in a control flow graph"""
    ENTRY = "entry"
    EXIT = "exit"
    RETURN = "return"
    USE = "use"
    STATEMENT = "statement"
    IF_CONDITION = "if_condition"
    DO_LOOP = "do_loop"
    SELECT_CASE = "select_case"
    CASE = "case"
    # I/O operations - each with distinct color
    KEYWORD_IO_OPEN = "keyword_io_open"
    KEYWORD_IO_READ = "keyword_io_read"
    KEYWORD_IO_WRITE = "keyword_io_write"
    KEYWORD_IO_CLOSE = "keyword_io_close"
    KEYWORD_IO_REWIND = "keyword_io_rewind"
    KEYWORD_IO_INQUIRE = "keyword_io_inquire"
    KEYWORD_IO_PRINT = "keyword_io_print"
    # Other keyword types
    KEYWORD_MEMORY = "keyword_memory"
    KEYWORD_BRANCH = "keyword_branch"
    KEYWORD_LOOP = "keyword_loop"
    KEYWORD_EXIT = "keyword_exit"
    KEYWORD_CALL = "keyword_call"


# Color scheme for different block types
COLORS = {
    BlockType.ENTRY: "#90EE90",  # Light green
    BlockType.EXIT: "#FFB6C1",  # Light pink
    BlockType.RETURN: "#FFB6C1",  # Light pink (same as EXIT)
    BlockType.USE: "#B0E0E6",  # Powder blue
    BlockType.STATEMENT: "#E0E0E0",  # Light gray
    BlockType.IF_CONDITION: "#87CEEB",  # Sky blue
    BlockType.DO_LOOP: "#DDA0DD",  # Plum
    BlockType.SELECT_CASE: "#F0E68C",  # Khaki
    BlockType.CASE: "#FFE4B5",  # Moccasin
    # I/O operation colors - distinct color for each operation type
    BlockType.KEYWORD_IO_OPEN: "#4A90E2",  # Medium blue
    BlockType.KEYWORD_IO_READ: "#50C878",  # Emerald green
    BlockType.KEYWORD_IO_WRITE: "#FF6B6B",  # Coral red
    BlockType.KEYWORD_IO_CLOSE: "#9370DB",  # Medium purple
    BlockType.KEYWORD_IO_REWIND: "#FFD700",  # Gold
    BlockType.KEYWORD_IO_INQUIRE: "#20B2AA",  # Light sea green
    BlockType.KEYWORD_IO_PRINT: "#FF69B4",  # Hot pink
    # Other keyword node colors
    BlockType.KEYWORD_MEMORY: "#52BE80",  # Green (hexagon)
    BlockType.KEYWORD_BRANCH: "#E59866",  # Orange (diamond) - not used
    BlockType.KEYWORD_LOOP: "#48C9B0",  # Teal (ellipse) - not used
    BlockType.KEYWORD_EXIT: "#EC7063",  # Red (octagon)
    BlockType.KEYWORD_CALL: "#BB8FCE",  # Purple (rectangle with bold outline)
}

# Shape scheme for different block types
SHAPES = {
    BlockType.IF_CONDITION: "diamond",
    BlockType.DO_LOOP: "diamond",
    BlockType.SELECT_CASE: "diamond",
    # I/O keyword node shapes - all rounded boxes
    BlockType.KEYWORD_IO_OPEN: "box",
    BlockType.KEYWORD_IO_READ: "box",
    BlockType.KEYWORD_IO_WRITE: "box",
    BlockType.KEYWORD_IO_CLOSE: "box",
    BlockType.KEYWORD_IO_REWIND: "box",
    BlockType.KEYWORD_IO_INQUIRE: "box",
    BlockType.KEYWORD_IO_PRINT: "box",
    # Other keyword node shapes
    BlockType.KEYWORD_MEMORY: "hexagon",
    BlockType.KEYWORD_EXIT: "octagon",
    BlockType.KEYWORD_CALL: "box",  # Will use bold outline
}

# Default shape for blocks not in SHAPES
DEFAULT_SHAPE = "box"

# Style information
STYLES = {
    BlockType.KEYWORD_IO_OPEN: "filled,rounded",
    BlockType.KEYWORD_IO_READ: "filled,rounded",
    BlockType.KEYWORD_IO_WRITE: "filled,rounded",
    BlockType.KEYWORD_IO_CLOSE: "filled,rounded",
    BlockType.KEYWORD_IO_REWIND: "filled,rounded",
    BlockType.KEYWORD_IO_INQUIRE: "filled,rounded",
    BlockType.KEYWORD_IO_PRINT: "filled,rounded",
    BlockType.KEYWORD_CALL: "filled,bold",
}

DEFAULT_STYLE = "filled"

# Color names
COLOR_NAMES = {
    "#90EE90": "Light green",
    "#FFB6C1": "Light pink",
    "#B0E0E6": "Powder blue",
    "#E0E0E0": "Light gray",
    "#87CEEB": "Sky blue",
    "#DDA0DD": "Plum",
    "#F0E68C": "Khaki",
    "#FFE4B5": "Moccasin",
    "#4A90E2": "Medium blue",
    "#50C878": "Emerald green",
    "#FF6B6B": "Coral red",
    "#9370DB": "Medium purple",
    "#FFD700": "Gold",
    "#20B2AA": "Light sea green",
    "#FF69B4": "Hot pink",
    "#52BE80": "Green",
    "#E59866": "Orange",
    "#48C9B0": "Teal",
    "#EC7063": "Red",
    "#BB8FCE": "Purple",
}

# Descriptions
DESCRIPTIONS = {
    BlockType.ENTRY: "Procedure entry point",
    BlockType.EXIT: "Procedure exit point",
    BlockType.RETURN: "Return statement",
    BlockType.USE: "USE statement",
    BlockType.STATEMENT: "Regular statement block",
    BlockType.IF_CONDITION: "IF condition decision point",
    BlockType.DO_LOOP: "DO loop control",
    BlockType.SELECT_CASE: "SELECT CASE statement",
    BlockType.CASE: "CASE block within SELECT",
    BlockType.KEYWORD_IO_OPEN: "I/O: OPEN file operation",
    BlockType.KEYWORD_IO_READ: "I/O: READ operation",
    BlockType.KEYWORD_IO_WRITE: "I/O: WRITE operation",
    BlockType.KEYWORD_IO_CLOSE: "I/O: CLOSE file operation",
    BlockType.KEYWORD_IO_REWIND: "I/O: REWIND file operation",
    BlockType.KEYWORD_IO_INQUIRE: "I/O: INQUIRE file status",
    BlockType.KEYWORD_IO_PRINT: "I/O: PRINT output",
    BlockType.KEYWORD_MEMORY: "Memory operations (ALLOCATE, DEALLOCATE)",
    BlockType.KEYWORD_BRANCH: "Branch keywords (not used)",
    BlockType.KEYWORD_LOOP: "Loop keywords (not used)",
    BlockType.KEYWORD_EXIT: "Early exit (RETURN, EXIT, CYCLE)",
    BlockType.KEYWORD_CALL: "Procedure call (CALL)",
}


def get_block_info(block_type):
    """Get all information about a block type."""
    return {
        "block_type": block_type.name,
        "color": COLORS[block_type],
        "color_name": COLOR_NAMES.get(COLORS[block_type], "Unknown"),
        "shape": SHAPES.get(block_type, DEFAULT_SHAPE),
        "style": STYLES.get(block_type, DEFAULT_STYLE),
        "description": DESCRIPTIONS[block_type],
    }


def display_table():
    """Display as a formatted text table."""
    print("\n" + "=" * 120)
    print("CONTROL FLOW GRAPH: SHAPE AND COLOR COMBINATIONS")
    print("=" * 120)
    print()
    
    # Header
    print(f"{'Block Type':<20} {'Color':<12} {'Color Name':<15} {'Shape':<12} {'Style':<18} {'Description':<40}")
    print("-" * 120)
    
    # Basic structures
    print("\nBASIC CONTROL FLOW STRUCTURES:")
    for bt in [BlockType.ENTRY, BlockType.EXIT, BlockType.RETURN, BlockType.USE, BlockType.STATEMENT]:
        info = get_block_info(bt)
        print(f"{info['block_type']:<20} {info['color']:<12} {info['color_name']:<15} {info['shape']:<12} {info['style']:<18} {info['description']:<40}")
    
    # Conditional and loop structures
    print("\nCONDITIONAL AND LOOP STRUCTURES:")
    for bt in [BlockType.IF_CONDITION, BlockType.DO_LOOP, BlockType.SELECT_CASE, BlockType.CASE]:
        info = get_block_info(bt)
        print(f"{info['block_type']:<20} {info['color']:<12} {info['color_name']:<15} {info['shape']:<12} {info['style']:<18} {info['description']:<40}")
    
    # I/O keyword nodes
    print("\nI/O KEYWORD NODES:")
    for bt in [BlockType.KEYWORD_IO_OPEN, BlockType.KEYWORD_IO_READ, BlockType.KEYWORD_IO_WRITE, 
               BlockType.KEYWORD_IO_CLOSE, BlockType.KEYWORD_IO_REWIND, BlockType.KEYWORD_IO_INQUIRE, 
               BlockType.KEYWORD_IO_PRINT]:
        info = get_block_info(bt)
        print(f"{info['block_type']:<20} {info['color']:<12} {info['color_name']:<15} {info['shape']:<12} {info['style']:<18} {info['description']:<40}")
    
    # Other keyword nodes
    print("\nOTHER KEYWORD NODES:")
    for bt in [BlockType.KEYWORD_MEMORY, BlockType.KEYWORD_EXIT, BlockType.KEYWORD_CALL]:
        info = get_block_info(bt)
        print(f"{info['block_type']:<20} {info['color']:<12} {info['color_name']:<15} {info['shape']:<12} {info['style']:<18} {info['description']:<40}")
    
    # Unused
    print("\nCURRENTLY UNUSED:")
    for bt in [BlockType.KEYWORD_BRANCH, BlockType.KEYWORD_LOOP]:
        info = get_block_info(bt)
        print(f"{info['block_type']:<20} {info['color']:<12} {info['color_name']:<15} {info['shape']:<12} {info['style']:<18} {info['description']:<40}")
    
    print("\n" + "=" * 120)
    print()


def display_json():
    """Display as JSON."""
    data = {}
    for bt in BlockType:
        data[bt.name] = get_block_info(bt)
    print(json.dumps(data, indent=2))


def display_markdown():
    """Display as a markdown table."""
    print("\n# Control Flow Graph: Shape and Color Combinations\n")
    print("| Block Type | Color | Color Name | Shape | Style | Description |")
    print("|-----------|-------|------------|-------|-------|-------------|")
    
    for bt in BlockType:
        info = get_block_info(bt)
        print(f"| {info['block_type']} | {info['color']} | {info['color_name']} | {info['shape']} | {info['style']} | {info['description']} |")
    
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Display control flow graph shape and color combinations"
    )
    parser.add_argument(
        "--format",
        choices=["table", "json", "markdown"],
        default="table",
        help="Output format (default: table)",
    )
    
    args = parser.parse_args()
    
    if args.format == "table":
        display_table()
    elif args.format == "json":
        display_json()
    elif args.format == "markdown":
        display_markdown()


if __name__ == "__main__":
    main()
