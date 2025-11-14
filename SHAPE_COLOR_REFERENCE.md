# Control Flow Graph Shape and Color Reference

## Quick Answer

**Question:** "What shape color combos are we currently using in the control graph?"

**Answer:** FORD's control flow graphs use **14 block types** with the following combinations:

### Shapes (4 total)
- **Box** - 10 types (most common)
- **Diamond** - 3 types (decision points)
- **Hexagon** - 1 type (memory operations)
- **Octagon** - 1 type (early exits)

### Colors (12 total)
- Light green, Light pink, Powder blue, Light gray
- Sky blue, Plum, Khaki, Moccasin
- Blue, Green, Red, Purple
- (Plus 2 unused: Orange, Teal)

## Visual Summary

```
┌─────────────┐      ╱ Sky Blue ╲        ⬡⬡⬡⬡⬡⬡⬡          ⬢⬢⬢⬢⬢⬢⬢⬢
│ Light Green │    ╱   Diamond  ╲      ⬡ Green  ⬡        ⬢   Red   ⬢
│    ENTRY    │    ╲   i > 0    ╱      ⬡ Hexagon ⬡        ⬢ Octagon ⬢
└─────────────┘      ╲         ╱        ⬡⬡⬡⬡⬡⬡⬡          ⬢⬢⬢⬢⬢⬢⬢⬢
  Entry point      IF condition      Memory op           Exit stmt

┌─────────────┐      ╱   Plum   ╲      ┌─────────────┐   ┌─────────────┐
│  Light Gray │    ╱   Diamond  ╱      │ Blue Round  │   │Purple Bold  │
│  Statement  │    ╲  DO i=1,n  ╱      │  READ(...)  │   │  CALL sub() │
└─────────────┘      ╲         ╱        └─────────────┘   └─────────────┘
Regular code         DO loop           I/O operation     Procedure call
```

## Complete List

| # | Block Type | Shape | Color | Use |
|---|-----------|-------|-------|-----|
| 1 | ENTRY | box | #90EE90 (light green) | Procedure entry |
| 2 | EXIT | box | #FFB6C1 (light pink) | Procedure exit |
| 3 | RETURN | box | #FFB6C1 (light pink) | Return statement |
| 4 | USE | box | #B0E0E6 (powder blue) | USE statement |
| 5 | STATEMENT | box | #E0E0E0 (light gray) | Regular code |
| 6 | IF_CONDITION | diamond | #87CEEB (sky blue) | IF decision |
| 7 | DO_LOOP | diamond | #DDA0DD (plum) | DO loop control |
| 8 | SELECT_CASE | diamond | #F0E68C (khaki) | SELECT statement |
| 9 | CASE | box | #FFE4B5 (moccasin) | CASE block |
| 10 | KEYWORD_IO | box (rounded) | #5DADE2 (blue) | I/O operations |
| 11 | KEYWORD_MEMORY | hexagon | #52BE80 (green) | ALLOCATE/DEALLOCATE |
| 12 | KEYWORD_EXIT | octagon | #EC7063 (red) | EXIT/CYCLE/RETURN |
| 13 | KEYWORD_CALL | box (bold) | #BB8FCE (purple) | CALL statement |
| 14 | KEYWORD_BRANCH | box | #E59866 (orange) | ❌ Not used |
| 15 | KEYWORD_LOOP | box | #48C9B0 (teal) | ❌ Not used |

## Quick Command Reference

```bash
# Display full table
python show_cfg_colors.py

# Export as JSON
python show_cfg_colors.py --format json

# Generate markdown
python show_cfg_colors.py --format markdown
```

## Documentation Files

1. **[CFG_DOCUMENTATION_INDEX.md](CFG_DOCUMENTATION_INDEX.md)** - Start here
2. **[CONTROL_FLOW_GRAPH_SHAPES_AND_COLORS.md](CONTROL_FLOW_GRAPH_SHAPES_AND_COLORS.md)** - Complete reference
3. **[CONTROL_FLOW_GRAPH_QUICK_REFERENCE.md](CONTROL_FLOW_GRAPH_QUICK_REFERENCE.md)** - Quick lookup
4. **[CFG_SHAPES_COLORS_SUMMARY.md](CFG_SHAPES_COLORS_SUMMARY.md)** - Summary with stats
5. **[show_cfg_colors.py](show_cfg_colors.py)** - Utility script

## Design Rationale

- **Diamonds** = Decision points (IF, DO, SELECT)
- **Hexagon** = Memory allocation/deallocation
- **Octagon** = Stop/exit (like stop signs)
- **Rounded** = I/O (data flowing in/out)
- **Bold** = Procedure calls (crossing boundaries)
- **Green** = Start/entry
- **Red** = Stop/exit
- **Blue** = Conditions/data flow
- **Purple** = Loops/calls
- **Gray** = Neutral statements

## Source Code References

- Colors: `ford/graphs.py` lines 1747-1764
- Shapes: `ford/graphs.py` lines 1767-1777
- Styles: `ford/graphs.py` lines 1903-1911
- Block types: `ford/control_flow.py` BlockType enum

---

**Created in response to:** "tell me what shape color combos we are currently using in the control graph"
