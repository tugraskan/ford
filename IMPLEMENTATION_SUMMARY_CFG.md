# Control Flow Graph Implementation Summary

## Overview
This implementation adds comprehensive control flow graph (CFG) generation for Fortran subroutines and functions to FORD, addressing the requirement to "breakdown logic block in each subroutine" and "produce a graph for each subroutine on how the code works."

## Files Changed

### New Files
1. **ford/control_flow.py** (516 lines)
   - Core control flow parsing and graph generation logic
   - `ControlFlowGraph` class: Represents the CFG structure
   - `BasicBlock` dataclass: Represents individual code blocks
   - `FortranControlFlowParser`: Parses Fortran source to extract control flow
   - `parse_control_flow()`: Main entry point for parsing

2. **test/test_control_flow.py** (241 lines)
   - Comprehensive test suite with 8 test cases
   - Tests IF/THEN/ELSE, DO loops, SELECT CASE, nested structures
   - All tests passing ✓

3. **docs/api/ford.control_flow.rst**
   - API documentation for the new module

### Modified Files
1. **ford/graphs.py**
   - Added `create_control_flow_graph_svg()` function for visualization
   - Integrated CFG generation in `GraphManager.graph_all()`
   - Added control flow graph legend

2. **ford/sourceform.py**
   - Added `get_control_flow_graph()` method to `FortranProcedure` class
   - Extracts procedure source code and invokes parser

3. **ford/templates/proc_page.html**
   - Added collapsible "Control Flow Graph" section
   - Includes help modal with graph key

4. **docs/user_guide/project_file_options.rst**
   - Updated Graph Settings section to mention control flow graphs
   - Added dedicated Control Flow Graphs section explaining the feature

5. **docs/api/ford.rst**
   - Added ford.control_flow to module list

## Features Implemented

### Supported Control Flow Structures
1. **IF/THEN/ELSE Statements**
   - Simple IF-THEN
   - IF-THEN-ELSE
   - ELSE IF chains
   - Nested IF statements
   - IF without ELSE (with implicit false branch)

2. **DO Loops**
   - Standard DO loops with loop control
   - Back-edges showing loop iteration
   - Clear loop body and exit paths

3. **SELECT CASE Statements**
   - Multiple CASE branches
   - CASE DEFAULT
   - Multiple cases in SELECT

4. **Single-line IF Statements**
   - Conditional execution without THEN

### Graph Visualization
- **Color-coded blocks**:
  - Entry: Light green (#90EE90)
  - Exit: Light pink (#FFB6C1)
  - IF conditions: Sky blue (#87CEEB) - diamond shape
  - DO loops: Plum (#DDA0DD) - diamond shape
  - SELECT CASE: Khaki (#F0E68C) - diamond shape
  - CASE blocks: Moccasin (#FFE4B5)
  - Statements: Light gray (#E0E0E0)

- **Edge labels**:
  - "T" and "F" for IF conditions (true/false branches)
  - "loop" and "exit" for DO loops

- **Block labels**:
  - Show condition expressions for conditionals
  - Show loop control for DO loops
  - Show first few statements in statement blocks

## Testing

### Test Coverage
- ✅ All 8 new control flow tests pass
- ✅ All 15 existing graph tests pass
- ✅ All 12 existing procedure tests pass
- ✅ Successfully generated documentation for example project

### Test Cases
1. `test_simple_if_then_else`: Basic IF-THEN-ELSE
2. `test_do_loop`: DO loop structure
3. `test_select_case`: SELECT CASE with multiple cases
4. `test_nested_if`: Nested IF statements
5. `test_if_without_else`: IF without ELSE branch
6. `test_function_parsing`: Function vs subroutine
7. `test_empty_procedure`: Empty procedure handling
8. `test_complex_control_flow`: Complex mixed structures

## Usage

### For Users
When FORD generates documentation with graphs enabled (graph: true), control flow graphs are automatically generated for each subroutine and function. They appear in a collapsible section on the procedure's documentation page.

### Example
For a subroutine like:
```fortran
subroutine do_stuff(repeat)
  integer, intent(in) :: repeat
  integer :: i
  
  do i=1,repeat
    global_pi = acos(-1)
  end do
end subroutine do_stuff
```

FORD generates a control flow graph showing:
1. Entry block
2. Variable declarations
3. DO loop (diamond)
4. Loop body with statement
5. After loop block
6. Exit block
With edges showing "loop" and "exit" paths.

## Benefits

1. **Better Code Understanding**: Visualizes complex control flow
2. **Documentation**: Automatically documents algorithmic behavior
3. **Debugging Aid**: Helps identify logical flow issues
4. **Code Review**: Makes review of control flow easier
5. **Maintenance**: Helps new developers understand code structure

## Technical Details

### Parser Implementation
- Uses regex patterns to identify control flow statements
- Maintains a stack to handle nested structures
- Creates basic blocks for code segments
- Tracks predecessor/successor relationships
- Handles both free-form and fixed-form Fortran

### Graph Generation
- Uses graphviz for rendering
- Creates SVG output embedded in HTML
- Supports zoom for large graphs
- Consistent with existing FORD graph styling

## Limitations

### Current Scope
- Parses standard control flow structures (IF, DO, SELECT CASE)
- Focuses on procedural control flow
- Does not analyze data flow or dependencies
- Does not show GOTO statements or computed GOTO
- Does not show DO WHILE or DO CONCURRENT

### Future Enhancements
- Could add support for GOTO statements
- Could add support for DO WHILE
- Could add support for DO CONCURRENT
- Could add data flow analysis
- Could optimize graph layout for very complex procedures

## Conclusion

This implementation fully addresses the problem statement by:
- ✅ Breaking down logic blocks in each subroutine
- ✅ Producing a graph for each subroutine
- ✅ Showing how the code works
- ✅ Showing which blocks happen first (entry/exit flow)
- ✅ Showing conditions and logic (IF conditions, loop controls, case values)

All requirements met, all tests passing, documentation complete, and ready for use.
