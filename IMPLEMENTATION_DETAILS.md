# Implementation Details: Markdown/GitBook Export

## Overview
This document describes the implementation of Markdown and GitBook export functionality for FORD, enabling users to convert FORD-generated Fortran documentation into Markdown format suitable for GitHub, GitBook, and other markdown-based documentation systems.

## Problem Statement
Users requested the ability to convert FORD outputs to Markdown format and eventually to GitBook, allowing for better integration with modern documentation platforms and version control systems like GitHub/GitLab.

## Solution Architecture

### 1. Settings Extension
**File**: `ford/settings.py`

Added `output_format` field to `ProjectSettings` dataclass:
- Type: `str`
- Default: `"html"`
- Valid values: `"html"`, `"markdown"`, `"gitbook"` (case-insensitive)
- Validation in `__post_init__` method

### 2. Markdown Output Module
**File**: `ford/markdown_output.py`

Created `MarkdownDocumentation` class that:
- Mirrors the structure of the HTML output system
- Generates organized markdown files by entity type
- Handles cross-references and documentation preservation
- Implements GitBook-specific features (SUMMARY.md, book.json)

Key methods:
- `generate()`: Main entry point for markdown generation
- `_generate_modules()`: Creates module documentation
- `_generate_procedures()`: Creates procedure documentation
- `_generate_types()`: Creates type documentation
- `_generate_programs()`: Creates program documentation
- `_generate_files()`: Creates source file listings
- `_generate_custom_pages()`: Processes user-defined pages
- `_generate_gitbook_files()`: Creates GitBook-specific files

### 3. Integration
**File**: `ford/__init__.py`

Modified the main workflow to:
1. Check `output_format` setting
2. Route to appropriate documentation generator:
   - HTML: Use existing `ford.output.Documentation`
   - Markdown/GitBook: Use new `ford.markdown_output.MarkdownDocumentation`

### 4. Testing
**File**: `test/test_markdown_output.py`

Comprehensive test suite covering:
- Markdown output file creation
- GitBook format generation
- Content structure validation
- Settings validation
- Integration testing with example project

### 5. Documentation
**Files**: 
- `docs/user_guide/project_file_options.rst`
- `docs/user_guide/getting_started.rst`
- `MARKDOWN_OUTPUT.md`

Added:
- Complete documentation of `output_format` option
- Usage examples for all three formats
- Integration guides for GitHub, GitBook, Pandoc
- Getting started section with practical examples

## Output Structure

### Markdown Format
```
doc/
├── index.md                    # Main index
├── modules/
│   ├── index.md               # Module listing
│   └── [module_name].md       # Individual modules
├── procedures/
│   ├── index.md               # Procedure listing
│   └── [proc_name].md         # Individual procedures
├── types/
│   ├── index.md               # Type listing
│   └── [type_name].md         # Individual types
├── programs/
│   ├── index.md               # Program listing
│   └── [program_name].md      # Individual programs
├── files/
│   └── index.md               # Source file listing
└── pages/
    └── [custom_pages].md      # User-defined pages
```

### GitBook Format
Same as Markdown, plus:
- `README.md` (instead of index.md)
- `SUMMARY.md` (navigation table of contents)
- `book.json` (GitBook configuration)

## Technical Details

### Entity Documentation Generation
Each entity type follows a consistent pattern:
1. Create directory for entity type
2. Generate index file listing all entities
3. Generate individual files for each entity
4. Include relevant metadata (type, intent, etc.)
5. Preserve cross-references and documentation

### Filename Safety
Implemented `_safe_filename()` method to:
- Convert entity names to safe filenames
- Handle special characters
- Maintain uniqueness
- Use lowercase for consistency

### Content Preservation
- Documentation comments are preserved with HTML formatting
- LaTeX equations are maintained
- Cross-references are converted to relative links
- Custom pages maintain their structure

## Design Decisions

1. **Minimal Changes**: Implementation follows FORD's existing patterns and structure
2. **Backward Compatibility**: Default behavior unchanged (HTML output)
3. **Extensibility**: Architecture allows for additional formats in the future
4. **Validation**: Input validation prevents invalid format specifications
5. **Separation of Concerns**: New module isolated from existing HTML generation

## Future Enhancements

Potential improvements:
1. More sophisticated markdown formatting options
2. Support for additional formats (AsciiDoc, reStructuredText)
3. Custom templates for markdown output
4. Enhanced cross-reference resolution in markdown
5. Integration with specific static site generators

## Testing Strategy

1. **Unit Tests**: Validation of settings and individual methods
2. **Integration Tests**: Full workflow with example project
3. **Format Tests**: Verification of all three output formats
4. **Security**: CodeQL analysis (no vulnerabilities found)

## Performance Considerations

- Markdown generation is faster than HTML (no template rendering)
- File I/O is the primary bottleneck
- Memory usage similar to HTML generation
- Suitable for projects of all sizes

## Compatibility

- Python 3.8+
- All existing FORD dependencies
- Works with both fpm.toml and markdown metadata configurations
- Compatible with all existing FORD features (preprocessing, graphs, etc.)

## Conclusion

This implementation successfully adds Markdown and GitBook export capabilities to FORD while maintaining backward compatibility and following the project's established patterns. The feature enables users to integrate FORD-generated documentation with modern documentation platforms and workflows.
