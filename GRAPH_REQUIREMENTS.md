# Graph Requirements for FORD

## Overview

FORD can generate call graphs, module dependency graphs, type inheritance graphs, and control flow graphs to visualize relationships in your Fortran code.

## Requirements

### 1. Graphviz Installation

Graph generation requires [Graphviz](https://graphviz.org/) to be installed on your system.

#### Installation Instructions

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get install graphviz
```

**macOS (using Homebrew):**
```bash
brew install graphviz
```

**Windows:**
Download and install from [graphviz.org/download/](https://graphviz.org/download/)

**Verify Installation:**
```bash
dot -V
```
This should output the Graphviz version if installed correctly.

### 2. Enable Graphs in Configuration

In your FORD project file (e.g., `project_file.md`), set:

```
graph: true
```

Or use the `graphs` alias:

```
graphs: true
```

## Graph Types

When enabled, FORD generates several types of graphs:

### Call Graphs
- **Calls Graph**: Shows procedures that a given procedure calls
- **Called By Graph**: Shows procedures that call a given procedure
- Located in procedure documentation pages under the "Calls" section

### Module Graphs
- **Uses Graph**: Shows modules that a module uses
- **Used By Graph**: Shows modules that use a given module
- Located in module documentation pages

### Type Graphs
- **Inheritance Graph**: Shows type inheritance relationships
- **Component Graph**: Shows types that are components of other types
- Located in type documentation pages

### Control Flow Graphs (NEW)
- Visual representation of the execution flow within procedures
- Shows IF conditions, DO loops, SELECT CASE structures
- Located in procedure documentation pages under the "Control Flow" section

### Logic Blocks
- Hierarchical view of control structures in source code
- Collapsible blocks for navigating complex procedures
- Located in procedure documentation pages under the "Control Flow" section

## Troubleshooting

### "Will not be able to generate graphs. Graphviz not installed."

This warning means Graphviz is not installed or not in your system PATH.

**Solution**: Install Graphviz as described above and ensure the `dot` executable is in your PATH.

### Graphs show "n/a" in documentation

**Possible causes:**
1. `graph: false` in your project configuration file
2. Graphviz not installed
3. The procedure/module has no calls/dependencies to graph

**Solution**:
1. Set `graph: true` in your configuration
2. Install Graphviz
3. Verify your code actually has relationships to graph

### Graph generation is slow

Graph generation can take time for large projects.

**Solutions:**
- Use `graph_maxnodes` to limit graph size
- Use `graph_maxdepth` to limit graph depth
- Set these in your project file or in source code documentation

Example in project file:
```
graph_maxnodes: 50
graph_maxdepth: 3
```

### Graph generation hangs or times out

FORD includes timeout protection for control flow graph generation (30 seconds per procedure). If CFG generation takes too long, FORD will skip that procedure and continue with a warning message.

**What happens:**
- Control flow graphs have a 30-second timeout per procedure
- If timeout occurs, a warning is printed and the procedure's CFG is skipped
- Documentation generation continues for other procedures

**If you see timeout warnings:**
1. The procedure may have extremely complex control flow
2. Consider simplifying the procedure structure if possible
3. The rest of the documentation will still be generated correctly

## Example Configuration

Complete example of a FORD project file with graphs enabled:

```
project: MyFortranProject
src_dir: src/
output_dir: doc/
graph: true
graph_maxnodes: 100
graph_maxdepth: 5
coloured_edges: true
show_proc_parent: true
```

## Additional Resources

- [FORD Documentation](https://forddocs.readthedocs.io/)
- [Graphviz Documentation](https://graphviz.org/documentation/)
- [FORD GitHub Repository](https://github.com/Fortran-FOSS-Programmers/ford)
