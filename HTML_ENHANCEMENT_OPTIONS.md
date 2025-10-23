# HTML Enhancement Options for FORD Documentation

This document identifies project.md (or fpm.toml) options that can be turned on to enhance your FORD-generated HTML documentation.

## Visual Enhancement Options

### Graph Visualization

**`graph: true`** *(default: false)*

Generates interactive dependency diagrams, call-trees, and inheritance diagrams using Graphviz. This creates:
- Module dependency graphs showing `use` relationships
- Type inheritance and composition diagrams
- Procedure call-trees
- Overall project structure visualizations

**Requires:** Graphviz must be installed on your system.

**Example:**
```yaml
---
graph: true
graph_maxdepth: 10
graph_maxnodes: 1000
coloured_edges: true
show_proc_parent: true
---
```

**Related options:**
- **`coloured_edges: true`** - Uses colors for graph edges, making large graphs easier to read
- **`graph_maxdepth: 10`** - Limits recursion depth in graphs (default: 10000)
- **`graph_maxnodes: 1000`** - Maximum nodes per graph (default: 1000000000)
- **`show_proc_parent: true`** - Displays parent modules in graphs as "parent::procedure"
- **`graph_dir: ./graphs`** - Saves SVG and graphviz files for all graphs

### Source Code Display

**`source: true`** *(default: false)*

Displays syntax-highlighted source code at the bottom of documentation pages for each procedure, program, and derived type. This allows users to see the actual implementation alongside the documentation.

**Note:** This substantially increases run-time.

**Example:**
```yaml
---
source: true
---
```

**Related options:**
- **`incl_src: true`** *(default: true)* - Makes source files accessible in documentation. Set to `false` to hide file listings while still showing procedures.

### Search Functionality

**`search: true`** *(default: true)*

Adds a powerful search feature to documentation using Lunr Search. Can be time-consuming for large projects but greatly improves usability.

**Performance tip:** Install the `lxml` library to speed up search indexing.

**Example:**
```yaml
---
search: true
---
```

## Content Enhancement Options

### Project Information Display

**`summary: "Your project summary"`**

Displays a prominent "Jumbotron" element at the top of the documentation index page with your project description. Supports Markdown formatting.

**Example:**
```yaml
---
summary: |
    A high-performance **Fortran library** for computational fluid dynamics.
    
    Features:
    - Fast sparse matrix operations
    - Parallel processing support
    - Modern Fortran 2008 standards
---
```

### Author Information

Add comprehensive author information that appears in the documentation sidebar:

**Example:**
```yaml
---
author: Jane Doe
author_description: |
    Research scientist specializing in computational physics.
    Check out my other projects!
author_pic: ./images/author.jpg
email: jane.doe@example.com
github: https://github.com/janedoe
linkedin: https://linkedin.com/in/janedoe
twitter: https://twitter.com/janedoe
website: https://janedoe.com
---
```

### Project Links

Add social and repository links that appear as badges/buttons:

**Example:**
```yaml
---
project_github: https://github.com/yourname/yourproject
project_website: https://yourproject.com
project_download: https://github.com/yourname/yourproject/releases
project_gitlab: https://gitlab.com/yourname/yourproject
project_bitbucket: https://bitbucket.org/yourname/yourproject
project_sourceforge: https://sourceforge.net/projects/yourproject
---
```

### License Display

Show the software license with automatically generated links:

**Example:**
```yaml
---
license: mit
doc_license: by-sa
---
```

**Available licenses:** agpl, bsd, by, by-nc, by-nc-nd, by-nc-sa, by-nd, by-sa, gfdl, gpl, isc, lgpl, mit, opl, pdl

### Version Information

**Example:**
```yaml
---
version: 2.1.0
revision: beta
year: 2024
print_creation_date: true
creation_date: %Y-%m-%d %H:%M
---
```

## Content Organization Options

### Additional Pages

**`page_dir: ./pages`**

Creates a hierarchical set of general information pages (tutorials, examples, theory) from Markdown files.

**Example:**
```yaml
---
page_dir: ./pages
---
```

**Directory structure example:**
```
pages/
├── index.md          (becomes "Documentation" in menu)
├── tutorial.md
├── examples/
│   ├── index.md
│   ├── example1.md
│   └── example2.md
```

### Media Files

**`media_dir: ./media`**

Makes images and other media accessible via the `|media|` macro in your documentation.

**Example:**
```yaml
---
media_dir: ./images
---
```

**Usage in documentation:**
```fortran
!! ![Architecture diagram](|media|/architecture.png)
```

### Copy Additional Resources

**`copy_subdir: ./resources`**

Copies entire directories verbatim into documentation output (e.g., for PDFs, datasets, or external assets).

**Example:**
```yaml
---
copy_subdir: ./resources
    ./static
---
```

## Styling Customization

### Custom Stylesheet

**`css: ./custom.css`**

Applies custom CSS to override default Bootstrap styling.

**Example:**
```yaml
---
css: ./custom-theme.css
---
```

**Sample custom.css:**
```css
/* Make headers dark blue */
h1, h2, h3 { color: #003366; }

/* Custom sidebar background */
.sidebar { background-color: #f5f5f5; }
```

### Custom Favicon

**`favicon: ./favicon.png`**

Replaces default FORD icon with your project's icon.

**Example:**
```yaml
---
favicon: ./images/myproject-icon.png
---
```

## Mathematics Support

**LaTeX math rendering** is enabled by default using MathJax.

**`mathjax_config: ./mathjax_config.js`**

Customize MathJax behavior (define TeX macros, change rendering options).

**Example mathjax_config.js:**
```javascript
window.MathJax = {
  tex: {
    macros: {
      RR: "\\mathbb{R}",
      vec: ["\\mathbf{#1}", 1]
    }
  }
};
```

**Example usage:**
```yaml
---
mathjax_config: ./mathjax_config.js
---
```

## Documentation Scope Options

### Visibility Control

**`display: [public, protected, private]`** *(default: [public, protected])*

Controls which entities appear in documentation based on their access level.

**Example:**
```yaml
---
display: public
    protected
    private
---
```

### Procedure Internals

**`proc_internals: true`** *(default: false)*

Shows local variables, derived types, and internal details within procedures.

**Example:**
```yaml
---
proc_internals: true
---
```

### Hide Undocumented Items

**`hide_undoc: true`** *(default: false)*

Hides any entities without documentation comments.

**Example:**
```yaml
---
hide_undoc: true
warn: true  # Get warnings about what's missing
---
```

## Sorting and Organization

**`sort: permission-alpha`** *(default: src)*

Controls display order of entities in documentation.

**Options:**
- `src` - Source code order
- `alpha` - Alphabetical
- `permission` - Public, protected, then private (source order within)
- `permission-alpha` - Public, protected, then private (alphabetical within)
- `type` - By variable/function type
- `type-alpha` - By type, then alphabetical

**Example:**
```yaml
---
sort: permission-alpha
---
```

### Front Page Items

**`max_frontpage_items: 4`** *(default: 10)*

Limits number of modules/procedures/types shown on the front page.

**Example:**
```yaml
---
max_frontpage_items: 5
---
```

## External Project Integration

### Link to External Documentation

**`external: ./other-project`**

Links to entities in other FORD-documented projects. Requires those projects to use `externalize: true`.

**Example:**
```yaml
---
external: ../libmath
    https://example.com/libcore/doc
externalize: true  # Allow other projects to link to us
---
```

### Reference External Modules

**`extra_mods:`**

Links to documentation for modules not in your project.

**Example:**
```yaml
---
extra_mods: json_module: http://jacobwilliams.github.io/json-fortran/
    blas: https://www.netlib.org/blas/
---
```

## Interactive Features

### Gitter Chat Integration

**`gitter_sidecar: yourproject/community`**

Embeds a Gitter chat sidecar in your documentation.

**Example:**
```yaml
---
gitter_sidecar: myorg/myproject
---
```

## Non-Fortran Source Files

**`extra_filetypes:`**

Extracts documentation from non-Fortran files (C++, Python, shell scripts, etc.) and displays them with syntax highlighting.

**Example:**
```yaml
---
extra_filetypes: cpp //
    py # python
    sh # bash
---
```

**TOML format:**
```toml
extra_filetypes = [
  { extension = "cpp", comment = "//" },
  { extension = "py", comment = "#", lexer = "python" },
  { extension = "sh", comment = "#", lexer = "bash" },
]
```

## Complete Enhanced Example

Here's a complete example using many enhancement options:

### Markdown metadata (project.md):
```yaml
---
project: My Amazing Fortran Project
version: 1.0.0
summary: |
    A **modern Fortran** library for scientific computing.
    Features parallel processing and GPU acceleration.
author: Dr. Jane Smith
author_pic: ./images/author.jpg
github: https://github.com/jsmith
email: jane.smith@university.edu

project_github: https://github.com/jsmith/amazing-fortran
project_website: https://amazing-fortran.org
license: mit
doc_license: by-sa

graph: true
coloured_edges: true
graph_maxdepth: 15
source: true
search: true

display: public
    protected
hide_undoc: false
proc_internals: true
sort: permission-alpha
max_frontpage_items: 8

page_dir: ./docs/pages
media_dir: ./docs/images
css: ./docs/custom.css
favicon: ./docs/favicon.png
mathjax_config: ./docs/mathjax-config.js

extra_filetypes: cpp //
    py # python

externalize: true
external: ../dependency-lib

print_creation_date: true
---
```

### TOML format (fpm.toml):
```toml
[extra.ford]
project = "My Amazing Fortran Project"
version = "1.0.0"
summary = """
A **modern Fortran** library for scientific computing.
Features parallel processing and GPU acceleration.
"""

author = "Dr. Jane Smith"
author_pic = "./images/author.jpg"
github = "https://github.com/jsmith"
email = "jane.smith@university.edu"

project_github = "https://github.com/jsmith/amazing-fortran"
project_website = "https://amazing-fortran.org"
license = "mit"
doc_license = "by-sa"

graph = true
coloured_edges = true
graph_maxdepth = 15
source = true
search = true

display = ["public", "protected"]
hide_undoc = false
proc_internals = true
sort = "permission-alpha"
max_frontpage_items = 8

page_dir = "./docs/pages"
media_dir = "./docs/images"
css = "./docs/custom.css"
favicon = "./docs/favicon.png"
mathjax_config = "./docs/mathjax-config.js"

extra_filetypes = [
  { extension = "cpp", comment = "//" },
  { extension = "py", comment = "#", lexer = "python" },
]

externalize = true
external = { dependency-lib = "../dependency-lib" }

print_creation_date = true
```

## Performance Considerations

Options that significantly increase generation time:
- **`graph: true`** - Can be very slow for large projects
- **`source: true`** - Substantially increases run-time
- **`search: true`** - Time-consuming for large projects (use `lxml` to speed up)

Use `parallel: 8` (or appropriate CPU count) to speed up processing.

## Debugging Options

- **`warn: true`** - Prints warnings about undocumented items and missing source code
- **`quiet: false`** *(default)* - Shows progress information
- **`dbg: true`** *(default)* - Shows Python backtrace on errors

## More Information

For complete option documentation, see:
- [Project File Options](https://forddocs.readthedocs.io/en/latest/user_guide/project_file_options.html)
- [Writing Documentation](https://forddocs.readthedocs.io/en/latest/user_guide/writing_documentation.html)
- [Example project file](./example/example-project-file.md)
- [Example fpm.toml](./example/fpm.toml)
