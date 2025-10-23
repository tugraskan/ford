# Using Graphs in Markdown and GitBook Output

FORD now supports generating call graphs, type graphs, and dependency graphs in Markdown and GitBook formats. This guide explains how to enable and use this feature.

## Prerequisites

- Graphviz must be installed on your system
- FORD version 7.1 or later

### Installing Graphviz

**Ubuntu/Debian:**
```bash
sudo apt-get install graphviz
```

**macOS:**
```bash
brew install graphviz
```

**Windows:**
Download from https://graphviz.org/download/

## Enabling Graphs

Add these options to your project configuration:

### Using fpm.toml (Recommended)

```toml
[extra.ford]
output_format = "gitbook"  # or "markdown"
graph = true
```

### Using project file metadata

```yaml
---
output_format: gitbook
graph: true
---
```

## What Gets Generated

### 1. Project-Level Graphs

Four main graphs are created at the project level:

#### Call Graph
Shows calling relationships between all procedures in the project.
- File: `graphs/callgraph.svg`
- Page: `graphs/callgraph.md`

#### Type Graph
Shows inheritance and composition relationships between derived types.
- File: `graphs/typegraph.svg`
- Page: `graphs/typegraph.md`

#### Module Use Graph
Shows dependencies between modules (which modules use which).
- File: `graphs/usegraph.svg`
- Page: `graphs/usegraph.md`

#### File Graph
Shows dependencies between source files.
- File: `graphs/filegraph.svg`
- Page: `graphs/filegraph.md`

### 2. Entity-Specific Graphs

Each module, type, and procedure can have its own graphs:

**Module graphs:**
- Uses graph: Shows modules/entities this module depends on
- Used-by graph: Shows what depends on this module

**Type graphs:**
- Inheritance graph: Shows parent types
- Inherited-by graph: Shows child types

**Procedure graphs:**
- Calls graph: Shows procedures this procedure calls
- Called-by graph: Shows what calls this procedure

## Output Structure

```
doc/
├── README.md                           # Main page with graph links
├── SUMMARY.md                          # GitBook navigation (includes graphs)
├── graphs/
│   ├── callgraph.md                   # Call graph page
│   ├── callgraph.svg                  # Call graph image
│   ├── typegraph.md                   # Type graph page
│   ├── typegraph.svg                  # Type graph image
│   ├── usegraph.md                    # Module use graph page
│   ├── module~~graph~~ModuleGraph.svg # Module use graph image
│   ├── module~~mymod~~UsesGraph.svg   # Individual module graph
│   └── [many more entity graphs]
├── modules/
│   └── mymodule.md                    # Includes inline dependency graph
├── procedures/
│   └── myproc.md                      # May include call graph
└── types/
    └── mytype.md                      # May include inheritance graph
```

## How Graphs Appear in Documentation

### In the Main Page (README.md)

```markdown
## Project Graphs
- [Call Graph](graphs/callgraph.md)
- [Type Graph](graphs/typegraph.md)
- [Module Use Graph](graphs/usegraph.md)
- [File Graph](graphs/filegraph.md)
```

### In Module Pages

Each module page automatically includes its dependency graph:

```markdown
# Module: my_module

[module documentation]

## Module Dependencies Graph

![my_module dependencies](../graphs/module~~my_module~~UsesGraph.svg)

## Procedures
[...]
```

### In Graph Pages

Each project-level graph gets a dedicated page:

```markdown
# Call Graph

This graph shows the calling relationships between procedures in the project.

![Call Graph](callgraph.svg)
```

## Viewing Graphs

### In GitBook

1. Generate your documentation with graphs enabled
2. Publish to GitBook (via GitHub integration or manual upload)
3. Graphs render as high-quality SVG images
4. Click graph links in the navigation or main page

### On GitHub

1. Push your documentation to GitHub
2. GitHub automatically renders the markdown files
3. SVG graphs display inline with proper scaling
4. Navigate through the documentation using links

### Locally

1. View markdown files in any markdown viewer
2. SVG files can be opened in browsers
3. Use a local GitBook server:
   ```bash
   npm install -g gitbook-cli
   cd doc/
   gitbook serve
   ```

## Customizing Graph Appearance

You can customize graph generation with these settings:

```toml
[extra.ford]
output_format = "gitbook"
graph = true
graph_maxdepth = 10000      # Maximum nesting depth
graph_maxnodes = 1000000000 # Maximum nodes in graph
coloured_edges = true       # Use colored arrows
```

## Examples

### Basic Usage

```toml
[extra.ford]
project = "My Fortran Library"
output_format = "gitbook"
graph = true
```

Then run:
```bash
ford project.md
```

The `doc/graphs/` directory will contain all graph SVG files and markdown pages.

### With Custom Graph Settings

```toml
[extra.ford]
project = "Large Fortran Project"
output_format = "gitbook"
graph = true
graph_maxdepth = 5          # Limit depth for large projects
coloured_edges = true       # Easier to distinguish relationships
```

## Troubleshooting

### Graphs Not Generated

**Problem:** No graphs directory appears

**Solution:** Check that:
1. Graphviz is installed: `dot -V`
2. `graph: true` is set in your configuration
3. Your project has documentable entities

### Broken Graph Links

**Problem:** Graph images don't display

**Solution:** 
1. Verify SVG files exist in `graphs/` directory
2. Check relative path syntax in markdown files
3. Ensure GitBook/GitHub can access the files

### Graphs Too Large

**Problem:** Graphs are overwhelming or slow to render

**Solution:**
1. Reduce `graph_maxdepth` to limit recursion
2. Reduce `graph_maxnodes` to limit graph size
3. Document only key modules/procedures

## Performance Considerations

- Graph generation adds ~10-30% to documentation build time
- Larger projects produce more graph files
- SVG files are typically 2-20KB each
- Total graph output usually < 5MB for most projects

## Integration with Documentation Platforms

### GitBook.com

1. Connect your repository to GitBook
2. GitBook automatically builds from SUMMARY.md
3. Graphs render as interactive SVG images
4. Navigation includes graph pages

### GitHub Pages

1. Enable GitHub Pages for your repository
2. Point to the `doc/` directory
3. GitHub renders markdown with embedded graphs
4. Use a Jekyll theme for better styling

### Read the Docs

1. Convert markdown to RST or use MyST parser
2. Include SVG files in documentation
3. Build with Sphinx for advanced features

## Best Practices

1. **Enable graphs for published documentation** - They provide valuable insights
2. **Use GitBook format** - Better navigation with SUMMARY.md
3. **Limit graph depth for large projects** - Prevents overwhelming graphs
4. **Review generated graphs** - Ensure they're meaningful
5. **Include graph links in your README** - Make them easy to find

## Comparison with HTML Output

| Feature | HTML Output | Markdown/GitBook Output |
|---------|-------------|-------------------------|
| Graph format | Inline SVG | SVG files |
| Interactive | Yes (pan/zoom) | Static |
| File size | Larger | Smaller |
| Portability | Browser only | Any markdown viewer |
| Version control | Poor | Excellent |

## Future Enhancements

Potential improvements:
- Interactive graph navigation
- Graph filtering options
- Custom graph templates
- PNG/PDF export options
- Clickable nodes in graphs

## See Also

- [MARKDOWN_OUTPUT.md](MARKDOWN_OUTPUT.md) - General markdown output guide
- [FEATURE_COMPARISON.md](FEATURE_COMPARISON.md) - Format comparison
- [FORD Documentation](https://forddocs.readthedocs.io/) - Complete user guide
