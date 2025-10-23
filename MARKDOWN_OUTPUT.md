# Markdown and GitBook Output

FORD now supports generating documentation in Markdown and GitBook formats in addition to the default HTML output. This allows you to:

- Publish documentation directly on GitHub/GitLab
- Convert documentation to other formats using Pandoc
- Integrate with GitBook or other static site generators
- View documentation in text editors

## Usage

### Basic Markdown Output

To generate Markdown documentation, add the `output_format` option to your project configuration:

**Using fpm.toml (recommended):**

```toml
[extra.ford]
project = "My Project"
output_format = "markdown"
```

**Using project file metadata:**

```yaml
---
project: My Project
output_format: markdown
---
```

Then run FORD as usual:

```bash
ford project-file.md
```

This will generate a directory structure like:

```
doc/
├── index.md
├── modules/
│   ├── index.md
│   ├── module1.md
│   └── module2.md
├── procedures/
│   ├── index.md
│   ├── subroutine1.md
│   └── function1.md
├── types/
│   ├── index.md
│   └── type1.md
├── programs/
│   ├── index.md
│   └── program1.md
├── files/
│   └── index.md
└── pages/
    └── custom_page.md
```

### GitBook Output

For GitBook-compatible output, use:

```toml
[extra.ford]
output_format = "gitbook"
```

This generates the same Markdown structure but with additional GitBook-specific files:

- `README.md` - Main introduction page (instead of index.md)
- `SUMMARY.md` - Table of contents for GitBook navigation
- `book.json` - GitBook configuration file

### HTML Output (Default)

To explicitly use HTML output or revert to it:

```toml
[extra.ford]
output_format = "html"
```

## Output Structure

### Markdown Files

Each entity in your Fortran project gets its own Markdown file:

**Modules** (`modules/modulename.md`):
- Module documentation
- List of procedures
- List of types
- List of variables

**Procedures** (`procedures/procname.md`):
- Procedure documentation
- Procedure type (subroutine/function)
- Arguments with types and intents
- Return value (for functions)

**Types** (`types/typename.md`):
- Type documentation
- Components/fields
- Type-bound procedures

**Programs** (`programs/progname.md`):
- Program documentation

### Index Files

Each category has an `index.md` file listing all entities of that type with links to their individual pages.

### Custom Pages

Custom pages from your `page_dir` are copied to the `pages/` directory, maintaining their structure.

## Examples

### Example 1: Basic Markdown Export

```toml
[extra.ford]
project = "Fortran Library"
src_dir = "./src"
output_dir = "./docs"
output_format = "markdown"
```

### Example 2: GitBook for GitHub Pages

```toml
[extra.ford]
project = "Fortran Library"
author = "John Doe"
summary = "A library for scientific computing"
output_dir = "./docs"
output_format = "gitbook"
```

Then you can publish the `docs/` directory to GitHub Pages or GitBook.

### Example 3: Converting to PDF with Pandoc

Generate Markdown output, then use Pandoc to create a PDF:

```bash
# Generate markdown
ford project.md

# Convert to PDF
pandoc doc/**/*.md -o documentation.pdf
```

## Use Cases

### Publishing on GitHub

Markdown output is perfect for GitHub repositories:

1. Generate markdown documentation
2. Commit the `doc/` directory
3. GitHub automatically renders the markdown files

### GitBook Integration

GitBook format is designed for GitBook.com:

1. Generate gitbook documentation
2. Connect your repository to GitBook
3. GitBook automatically builds and publishes your documentation

### Custom Documentation Sites

Markdown output can be integrated with:

- MkDocs
- Sphinx (with MyST parser)
- Docusaurus
- Hugo
- Jekyll

## Notes

- The markdown output preserves most formatting from FORD comments
- LaTeX equations are preserved in markdown format
- Links between entities work within the markdown documentation
- Custom pages maintain their structure and formatting
- All three formats (HTML, Markdown, GitBook) use the same source code and project file

## Compatibility

The markdown export feature is available from FORD version 7.1 onwards. The output format is case-insensitive (`"html"`, `"HTML"`, `"Html"` all work).
