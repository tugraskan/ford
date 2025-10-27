# Testing the Codespace Setup

This guide helps you verify that the Ford development environment is set up correctly in your Codespace.

## Quick Validation Steps

Once your Codespace has started, run these commands to verify everything is working:

### 1. Check Python Version

```bash
python --version
```

Expected output: `Python 3.11.x` or higher

### 2. Check Ford Installation

```bash
ford --version
```

This should display the Ford version without errors.

### 3. Check Graphviz Installation

```bash
dot -V
```

Expected output should show graphviz version (e.g., `dot - graphviz version 2.x.x`)

### 4. Verify Ford Dependencies

```bash
python -c "import ford; import markdown; import jinja2; import pygments; import graphviz; print('All imports successful')"
```

Expected output: `All imports successful`

### 5. Test with Example Project

```bash
# Navigate to the example directory
cd /workspace/example

# Generate documentation
ford example-project-file.md

# Check that documentation was generated
ls -la doc/
```

You should see generated HTML files in the `doc/` directory.

### 6. Run Tests

```bash
# Return to workspace root
cd /workspace

# Run the test suite (excluding slow tests)
pytest

# Or run all tests including slow ones
pytest -m ""
```

Tests should pass or show expected results based on the current state of the codebase.

## Troubleshooting

### Ford Not Found

If `ford --version` fails:

```bash
pip install -e .[docs,tests]
```

### Import Errors

If you get import errors:

```bash
pip list | grep -i ford
pip install --upgrade -e .[docs,tests]
```

### Graphviz Not Working

If dot command is not found:

```bash
sudo apt-get update
sudo apt-get install -y graphviz
```

### Permission Issues

If you encounter permission issues:

```bash
# Check current user
whoami

# If needed, fix ownership
sudo chown -R $(whoami):$(whoami) /workspace
```

## Development Workflow Validation

After setup, try making a small change to verify the development environment:

1. Edit a Python file in `ford/` directory
2. Run `pytest` to ensure tests still pass
3. Generate documentation with an example project
4. View the generated HTML in the browser

## Next Steps

Once validation is complete, you're ready to:

- Work on Ford features and bug fixes
- Run the full test suite
- Generate and preview documentation
- Use the Ford compare functionality to track API changes

## Support

If you continue to have issues, please:

1. Check the `.devcontainer/README.md` for additional documentation
2. Review the main `README.md` for general Ford usage
3. Open an issue on GitHub with details about your problem
