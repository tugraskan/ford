# Control Flow Graph Documentation Index

This directory contains several resources documenting the shape and color combinations used in FORD's control flow graphs.

## Available Resources

### 📚 For Detailed Study
**[CONTROL_FLOW_GRAPH_SHAPES_AND_COLORS.md](CONTROL_FLOW_GRAPH_SHAPES_AND_COLORS.md)**
- Complete reference with all details
- Color palette analysis
- Design principles
- Implementation notes

### ⚡ For Quick Reference
**[CONTROL_FLOW_GRAPH_QUICK_REFERENCE.md](CONTROL_FLOW_GRAPH_QUICK_REFERENCE.md)**
- At-a-glance lookup tables
- Visual examples with emoji
- Quick decision guide

### 📊 For Summary
**[CFG_SHAPES_COLORS_SUMMARY.md](CFG_SHAPES_COLORS_SUMMARY.md)**
- Executive summary
- Statistics and distribution
- Links to all other resources

### 🔧 For Programmatic Access
**[show_cfg_colors.py](show_cfg_colors.py)**
- Python utility script
- Multiple output formats (table, JSON, markdown)
- Executable from command line

## Quick Answer

**"What shape/color combos are we currently using in the control graph?"**

We use **14 block types** with **4 different shapes** and **12 colors**:

- **Boxes** (10 types): Entry, Exit, Return, Use, Statement, Case, I/O, Call, and 2 unused
- **Diamonds** (3 types): IF conditions, DO loops, SELECT CASE
- **Hexagon** (1 type): Memory operations
- **Octagon** (1 type): Early exits

**Color scheme:**
- Green for entry/memory
- Pink/Red for exits
- Blue for conditions/I/O
- Purple for loops/calls
- Yellow for SELECT/CASE
- Gray for regular statements

## Usage Examples

### View as formatted table
```bash
python show_cfg_colors.py
```

### Export as JSON
```bash
python show_cfg_colors.py --format json > cfg_colors.json
```

### Generate markdown table
```bash
python show_cfg_colors.py --format markdown
```

## Related Documentation

- [GRAPH_REQUIREMENTS.md](GRAPH_REQUIREMENTS.md) - General graph requirements
- [IMPLEMENTATION_SUMMARY_CFG.md](IMPLEMENTATION_SUMMARY_CFG.md) - Control flow implementation
- [ford/graphs.py](ford/graphs.py) - Source code implementation
- [ford/control_flow.py](ford/control_flow.py) - Control flow parser

## Contributing

If you need to add or modify shape/color combinations:

1. Update the definitions in `ford/graphs.py`
2. Update the BlockType enum in `ford/control_flow.py` if adding new types
3. Update all documentation files listed above
4. Update the `show_cfg_colors.py` script
5. Test the visualization with example code
6. Update the CONTROL_FLOW_GRAPH_KEY legend in `ford/graphs.py`
