# Control Flow Graph Shape and Color Combinations - Summary

This document provides a summary of the shape and color combinations used in FORD's control flow graphs.

## Resources Available

We have created three resources to help you understand and reference the shape and color combinations:

### 1. Comprehensive Documentation
**File:** `CONTROL_FLOW_GRAPH_SHAPES_AND_COLORS.md`

This is the complete reference guide that includes:
- Detailed tables of all block types with colors, shapes, and descriptions
- Color palette summary with visual hierarchy explanations
- Implementation notes with code references
- Design principles behind the color/shape choices

**When to use:** For detailed understanding and reference

### 2. Quick Reference Guide
**File:** `CONTROL_FLOW_GRAPH_QUICK_REFERENCE.md`

This is a concise, at-a-glance reference that includes:
- Quick lookup tables
- Visual examples
- Emoji-enhanced color guide
- Common patterns and what they mean

**When to use:** For quick lookups while working

### 3. Python Utility Script
**File:** `show_cfg_colors.py`

This is an executable Python script that can display the information in multiple formats:

```bash
# Display as formatted table
python show_cfg_colors.py --format table

# Display as JSON (for programmatic use)
python show_cfg_colors.py --format json

# Display as Markdown (for documentation)
python show_cfg_colors.py --format markdown
```

**When to use:** For programmatic access or when you need different output formats

## Quick Summary

### Current Shape/Color Combinations in Use

**14 Block Types Total:**

**Basic Structures (5):**
- ENTRY: Light green box (#90EE90)
- EXIT: Light pink box (#FFB6C1)
- RETURN: Light pink box (#FFB6C1)
- USE: Powder blue box (#B0E0E6)
- STATEMENT: Light gray box (#E0E0E0)

**Control Flow Structures (4):**
- IF_CONDITION: Sky blue diamond (#87CEEB)
- DO_LOOP: Plum diamond (#DDA0DD)
- SELECT_CASE: Khaki diamond (#F0E68C)
- CASE: Moccasin box (#FFE4B5)

**Keyword Nodes (4 in use, 2 unused):**
- KEYWORD_IO: Blue rounded box (#5DADE2)
- KEYWORD_MEMORY: Green hexagon (#52BE80)
- KEYWORD_EXIT: Red octagon (#EC7063)
- KEYWORD_CALL: Purple bold box (#BB8FCE)
- ~~KEYWORD_BRANCH: Orange box (#E59866) - Not used~~
- ~~KEYWORD_LOOP: Teal box (#48C9B0) - Not used~~

### Shape Summary
- **box**: 10 block types (most common)
- **diamond**: 3 block types (decision points)
- **hexagon**: 1 block type (memory operations)
- **octagon**: 1 block type (early exits)

### Color Distribution
- **Green tones**: 2 (entry, memory)
- **Blue tones**: 3 (conditions, USE, I/O)
- **Purple tones**: 2 (loops, calls)
- **Yellow tones**: 2 (SELECT/CASE)
- **Pink tones**: 2 (exits)
- **Red tones**: 1 (early exit)
- **Gray tones**: 1 (statements)
- **Unused**: 2 (orange, teal)

### Special Styles
- **filled,rounded**: I/O operations only
- **filled,bold**: Procedure calls only
- **filled**: All others (default)

## Design Rationale

The shape and color scheme follows these principles:

1. **Decision points** use **diamond shapes** for visual distinction
2. **Special operations** use **unique shapes** (hexagon, octagon)
3. **Color hierarchy**:
   - Green = start/entry
   - Pink/Red = exit/stop
   - Blue = conditions/data flow
   - Purple = loops/calls
   - Yellow = branching
   - Gray = neutral/regular statements

4. **Style modifiers** add semantic meaning:
   - Rounded = data flowing in/out (I/O)
   - Bold = crossing boundaries (calls)
   - Octagon = stop sign (exit)

## Implementation Location

All definitions are in `/ford/graphs.py`:
- **Colors dictionary**: Lines 1747-1764
- **Shapes dictionary**: Lines 1767-1777
- **Style assignments**: Lines 1903-1911

## Examples of Use

### IF Condition
```
    ╱ Sky Blue  ╲
  ╱   Diamond   ╲  ← #87CEEB, diamond shape
  ╲   i > 0     ╱
    ╲         ╱
      T     F
```

### DO Loop
```
    ╱   Plum    ╲
  ╱   Diamond   ╲  ← #DDA0DD, diamond shape
  ╲  i=1,n      ╱
    ╲         ╱
    loop  exit
```

### I/O Operation
```
┌─────────────────┐
│ Blue Rounded    │  ← #5DADE2, box with rounded style
│ READ (L15)      │
│ read(10,*) x    │
└─────────────────┘
```

### Memory Operation
```
     ⬡⬡⬡⬡⬡⬡⬡
    ⬡ Green  ⬡      ← #52BE80, hexagon shape
   ⬡ ALLOCATE ⬡
    ⬡ (L42)  ⬡
     ⬡⬡⬡⬡⬡⬡⬡
```

### Early Exit
```
    ⬢⬢⬢⬢⬢⬢⬢⬢
   ⬢   Red   ⬢     ← #EC7063, octagon shape
  ⬢  RETURN  ⬢
   ⬢  (L88)  ⬢
    ⬢⬢⬢⬢⬢⬢⬢⬢
```

## See Also

- `ford/graphs.py` - Implementation
- `ford/control_flow.py` - Block type definitions
- `GRAPH_REQUIREMENTS.md` - Graph feature documentation
- `IMPLEMENTATION_SUMMARY_CFG.md` - Control flow graph implementation details
