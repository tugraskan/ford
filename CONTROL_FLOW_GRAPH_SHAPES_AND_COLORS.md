# Control Flow Graph: Shape and Color Combinations

This document describes all the shape and color combinations currently used in FORD's control flow graphs.

## Overview

Control flow graphs in FORD use different shapes and colors to distinguish various types of code blocks. This visual distinction makes it easier to understand the flow of execution within procedures.

## Current Shape and Color Combinations

### Basic Control Flow Structures

| Block Type | Color | Color Name | Hex Code | Shape | Description |
|-----------|-------|------------|----------|-------|-------------|
| **ENTRY** | Light green | Light green | `#90EE90` | box | Procedure entry point (shows procedure name and arguments) |
| **EXIT** | Light red | Light red | `#FFB3BA` | box | Procedure exit point |
| **RETURN** | Light pink | Light pink | `#FFB6C1` | box | Return statement |
| **USE** | Powder blue | Powder blue | `#B0E0E6` | box | USE statement |
| **STATEMENT** | Light gray | Light gray | `#E0E0E0` | box | Regular statement block |

### Conditional and Loop Structures

| Block Type | Color | Color Name | Hex Code | Shape | Description |
|-----------|-------|------------|----------|-------|-------------|
| **IF_CONDITION** | Sky blue | Sky blue | `#87CEEB` | diamond | IF condition decision point |
| **DO_LOOP** | Plum | Plum | `#DDA0DD` | diamond | DO loop control |
| **SELECT_CASE** | Khaki | Khaki | `#F0E68C` | diamond | SELECT CASE statement |
| **CASE** | Moccasin | Moccasin | `#FFE4B5` | box | CASE block within SELECT |

### Keyword Nodes

These are special nodes that represent specific Fortran keywords/operations and use custom shapes to make them visually distinct:

| Block Type | Color | Color Name | Hex Code | Shape | Style | Description |
|-----------|-------|------------|----------|-------|-------|-------------|
| **KEYWORD_IO** | Blue | Blue | `#5DADE2` | box | filled,rounded | I/O operations (OPEN, READ, WRITE, CLOSE, REWIND, INQUIRE) |
| **KEYWORD_MEMORY** | Green | Green | `#52BE80` | hexagon | filled | Memory operations (ALLOCATE, DEALLOCATE) |
| **KEYWORD_EXIT** | Red | Red | `#EC7063` | octagon | filled | Early exit statements (RETURN, EXIT, CYCLE) |
| **KEYWORD_CALL** | Purple | Purple | `#BB8FCE` | box | filled,bold | Procedure call (CALL statement) |

### Currently Unused (Defined but Not Used)

| Block Type | Color | Color Name | Hex Code | Shape | Note |
|-----------|-------|------------|----------|-------|------|
| **KEYWORD_BRANCH** | Orange | Orange | `#E59866` | diamond | Not used - IF/SELECT handle branching |
| **KEYWORD_LOOP** | Teal | Teal | `#48C9B0` | ellipse | Not used - DO handles loops |

## Shape Guide

- **box**: Rectangle (default shape for most nodes)
- **diamond**: Diamond shape (used for decision points: IF, DO, SELECT)
- **hexagon**: Six-sided polygon (used for memory operations)
- **octagon**: Eight-sided polygon (used for exit statements)

## Style Guide

- **filled**: Node background is filled with color
- **rounded**: Rectangle with rounded corners
- **bold**: Thick outline

## Edge Labels

Edges (arrows) in the control flow graph may have labels to indicate the flow direction:

- **IF conditions**: Labeled with "T" (true) or "F" (false)
- **DO loops**: Labeled with "loop" (enter loop body) or "exit" (exit loop)

## Color Palette Summary

The color scheme uses pastel/light colors for easy readability:

- **Green tones** (`#90EE90`, `#52BE80`): Entry points and memory operations
- **Pink/Red tones** (`#FFB6C1`, `#FFB3BA`): Return statements and exit points
- **Blue tones** (`#87CEEB`, `#B0E0E6`, `#5DADE2`): Conditions, USE statements, I/O operations
- **Purple tones** (`#DDA0DD`, `#BB8FCE`): Loops and procedure calls
- **Yellow tones** (`#F0E68C`, `#FFE4B5`): SELECT/CASE statements
- **Gray** (`#E0E0E0`): Regular statements
- **Red** (`#EC7063`): Early exits (dangerous operations)

## Implementation Notes

These combinations are defined in `/ford/graphs.py` in the `create_control_flow_graph_svg()` function:

- Colors are defined in the `colors` dictionary (lines 1747-1764)
- Shapes are defined in the `shapes` dictionary (lines 1767-1777)
- Styles are applied conditionally based on block type (lines 1903-1911)

## Visual Hierarchy

The design follows these principles:

1. **Decision points** (IF, DO, SELECT) use **diamond shapes** to stand out
2. **Special operations** (I/O, memory, exit, call) use **unique shapes and bright colors**
3. **Regular statements** use **neutral gray** to avoid distraction
4. **Entry/Exit** use **green/pink** as universal indicators
5. **Rounded corners** indicate I/O operations (data going in/out)
6. **Bold outlines** indicate procedure calls (crossing boundaries)
7. **Octagons** indicate stop/exit points (like stop signs)

This design makes it easy to quickly scan a control flow graph and identify key decision points, special operations, and the overall flow of execution.
