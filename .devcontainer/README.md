# Ford Development Container

This directory contains the configuration for running Ford in a GitHub Codespace or VS Code dev container.

## What's Included

The development container provides:

- **Python 3.11**: The recommended Python version for Ford development
- **Graphviz**: Required for generating call graphs and dependency diagrams
- **Git**: For version control operations
- **All Ford dependencies**: Automatically installed from `pyproject.toml`, including:
  - Core dependencies (markdown, jinja2, pygments, etc.)
  - Documentation tools (sphinx, etc.)
  - Testing framework (pytest)

## Using in GitHub Codespaces

1. Navigate to the Ford repository on GitHub
2. Click the green "Code" button
3. Select the "Codespaces" tab
4. Click "Create codespace on main" (or your branch)
5. Wait for the container to build and start

Once the codespace is ready, you can:
- Run Ford: `ford example/example-project-file.md`
- Run tests: `pytest`
- Build documentation: `cd docs && make html`

## Using with VS Code Dev Containers

1. Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) for VS Code
2. Open the Ford repository folder in VS Code
3. Press `F1` and select "Dev Containers: Reopen in Container"
4. Wait for the container to build and start

## Customization

You can customize the development environment by editing:
- `.devcontainer/devcontainer.json`: VS Code settings and extensions
- `Dockerfile`: System packages and Python dependencies

## Testing the Ford Installation

After the container starts, verify Ford is working:

```bash
# Check Ford version
ford --version

# Test with the example project
ford example/example-project-file.md

# Run the test suite
pytest
```

## Troubleshooting

If you encounter issues:

1. **Container won't build**: Check the Docker build logs and ensure all dependencies in `pyproject.toml` are valid
2. **Ford command not found**: The installation might have failed. Try running `pip install -e .[docs,tests]` manually
3. **Graphviz errors**: Ensure the graphviz system package is installed (`apt-get install graphviz`)

## Development Workflow

1. Make changes to Ford source code in the `ford/` directory
2. The package is installed in editable mode, so changes are immediately reflected
3. Run tests frequently: `pytest`
4. Generate documentation: `cd docs && make html`
5. Test with example projects in the `example/` directory
