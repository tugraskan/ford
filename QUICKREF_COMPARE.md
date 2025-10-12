# FORD Comparison Quick Reference

## Installation
```bash
pip install ford
# or
pip install -e .  # from source
```

## Basic Commands

### Compare Two Metadata Files
```bash
ford-compare old.json new.json
```

### Save Report to File
```bash
ford-compare old.json new.json -o report.txt
```

### Verbose Mode (includes public variables)
```bash
ford-compare old.json new.json --verbose
```

## Generating Metadata

Ensure your FORD project file has `externalize: true`:

```markdown
---
project: My Project
externalize: true
output_dir: ./doc
---
```

Then generate documentation:
```bash
ford project.md
```

This creates `doc/modules.json` with metadata.

## Utility Scripts

### Generate Metadata Only
```bash
python ford_diff_utility.py generate ford.md
```

### Compare Two Projects
```bash
python ford_diff_utility.py compare-dirs old_project/ new_project/ ford.md
```

### Compare Existing Metadata
```bash
python ford_diff_utility.py compare old.json new.json
```

## Example Workflows

### Release Workflow
```bash
# Generate docs for v1.0
cd v1.0
ford ford.md
cd ..

# Generate docs for v2.0
cd v2.0
ford ford.md
cd ..

# Compare versions
ford-compare v1.0/doc/modules.json v2.0/doc/modules.json -o CHANGELOG_API.md
```

### Git Workflow
```bash
# Compare two commits
python example/compare_commits_example.py v1.0.0 v2.0.0

# Compare with current
python example/compare_commits_example.py v1.0.0 HEAD
```

### CI/CD Workflow
```yaml
# .github/workflows/api-check.yml
- name: Generate old docs
  run: |
    git checkout main
    ford ford.md
    mv doc old_doc

- name: Generate new docs
  run: |
    git checkout ${{ github.sha }}
    ford ford.md

- name: Compare
  run: ford-compare old_doc/modules.json doc/modules.json -o api_changes.txt
```

## Report Sections

### Modules
```
MODULES
  New modules (2):
    + module_new1
    + module_new2
  Removed modules (1):
    - module_old
```

### Procedures
```
PROCEDURES (Functions and Subroutines)
  New procedures (3):
    + module_a::new_function
    + module_b::new_subroutine
  Removed procedures (1):
    - module_a::old_function
```

### Types
```
DERIVED TYPES (Used in Procedure Inputs/Outputs)
  New types used in procedure arguments (1):
    + module_a::new_type
```

### Summary
```
SUMMARY
Total changes detected: 7
  Modules: +2 -1
  Procedures: +3 -1
  Types: +1 -0
  Files: +2 -1
```

## Programmatic Usage

```python
from pathlib import Path
from ford.compare import compare_commits, load_metadata, compare_metadata

# High-level comparison
result = compare_commits(
    Path("old/modules.json"),
    Path("new/modules.json"),
    output_file=Path("report.txt"),
    verbose=True
)

# Low-level comparison
old_meta = load_metadata(Path("old/modules.json"))
new_meta = load_metadata(Path("new/modules.json"))
result = compare_metadata(old_meta, new_meta)

# Access results
print(f"New modules: {result.new_modules}")
print(f"Removed procedures: {result.removed_procedures}")
```

## Common Options

| Option | Short | Description |
|--------|-------|-------------|
| `--help` | `-h` | Show help message |
| `--output FILE` | `-o FILE` | Save report to file |
| `--verbose` | `-v` | Include variable changes |

## Tips

1. Always set `externalize: true` in your FORD project file
2. Use verbose mode for detailed analysis
3. Save reports for documentation
4. Integrate into CI/CD for automated tracking
5. Compare tagged releases for changelog generation

## Troubleshooting

**Problem:** No modules.json file generated  
**Solution:** Ensure `externalize: true` in project file

**Problem:** Comparison shows no changes  
**Solution:** Verify both files are from different versions

**Problem:** Module not in PATH  
**Solution:** Reinstall with `pip install -e .`

## Learn More

- Full documentation: [COMPARE.md](COMPARE.md)
- Examples: [example/COMPARE_EXAMPLE.md](example/COMPARE_EXAMPLE.md)
- Source code: [ford/compare.py](ford/compare.py)
- Tests: [test/test_compare.py](test/test_compare.py)
