# Control Flow Graph Quick Reference

## Shape and Color Combinations - At a Glance

### Shapes Used

🔷 **Diamond** - Decision points (IF, DO, SELECT)  
🔲 **Box** - Regular statements, I/O, calls  
⬡ **Hexagon** - Memory operations  
🛑 **Octagon** - Early exits  

### Color Palette

```
🟢 Green (#90EE90, #52BE80)  - Entry, Memory
🟣 Purple (#DDA0DD, #BB8FCE) - Loops, Calls
🔵 Blue (#87CEEB, #5DADE2)   - Conditions, I/O
🟡 Yellow (#F0E68C, #FFE4B5) - SELECT/CASE
🔴 Red (#EC7063)             - Exit statements
🩷 Pink (#FFB6C1)            - Procedure exits
⚪ Gray (#E0E0E0)            - Regular statements
```

### Quick Lookup Table

| If You See... | It Means... |
|---------------|-------------|
| 🔷 Sky Blue Diamond | IF condition - decision point |
| 🔷 Plum Diamond | DO loop - iteration control |
| 🔷 Khaki Diamond | SELECT CASE - multi-way branch |
| 🔲 Light Green Box | ENTRY - procedure starts here |
| 🔲 Light Pink Box | EXIT/RETURN - procedure ends here |
| 🔲 Blue Rounded Box | I/O operation (READ, WRITE, etc.) |
| ⬡ Green Hexagon | Memory operation (ALLOCATE, DEALLOCATE) |
| 🛑 Red Octagon | Early exit (EXIT, CYCLE, RETURN) |
| 🔲 Purple Bold Box | Procedure CALL |
| 🔲 Gray Box | Regular statement |

### Edge Labels

- **T** / **F** - True/False branches from IF conditions
- **loop** / **exit** - DO loop iteration vs. loop exit

### Visual Examples

```
   ┌─────────────┐
   │ Light Green │  ← ENTRY (where procedure begins)
   │    ENTRY    │
   └─────────────┘
         ↓
      ╱     ╲
    ╱  Blue  ╲      ← IF CONDITION (diamond shape)
  ╱  Diamond  ╲
  ╲    i>0    ╱
    ╲       ╱
      ╲   ╱
        ↓T        F↓
   ┌─────────┐   ┌─────────┐
   │  Gray   │   │  Gray   │  ← STATEMENT blocks
   │ x = x+1 │   │ x = 0   │
   └─────────┘   └─────────┘
         ↓           ↓
         └───────┬───┘
                 ↓
         ┌─────────────┐
         │ Light Pink  │  ← EXIT (where procedure ends)
         │    EXIT     │
         └─────────────┘
```

### Special Styles

- **Rounded corners** → I/O operations (data flowing in/out)
- **Bold outline** → Procedure calls (crossing boundaries)
- **Octagon** → Stop/exit points (like stop signs)

---

**For complete details, see:** [CONTROL_FLOW_GRAPH_SHAPES_AND_COLORS.md](CONTROL_FLOW_GRAPH_SHAPES_AND_COLORS.md)
