# Running FORD in Visual Studio Code

This guide shows you how to run FORD (FORtran Documenter) directly within Visual Studio Code for an integrated development experience.

## Quick Setup

1. **Copy VS Code configuration files** to your Fortran project:
   ```bash
   cp -r /path/to/ford/.vscode /path/to/your/fortran/project/
   ```

2. **Open your Fortran project** in VS Code

3. **Run FORD** using one of these methods:

   **Method 1: Build Task (Recommended)**
   - Press `Ctrl+Shift+B` (Windows/Linux) or `Cmd+Shift+B` (Mac)
   - Enter your FORD project file name when prompted

   **Method 2: Command Palette**
   - Press `Ctrl+Shift+P` → "Tasks: Run Task" → "FORD: Generate Documentation"

   **Method 3: Terminal**
   - Press `Ctrl+`` to open terminal
   - Run: `ford your-project-file.md`

## What's Included

The `.vscode` folder contains:

- **`tasks.json`** - Predefined tasks for running FORD with different options
- **`launch.json`** - Debug configurations for FORD development
- **`settings.json`** - Workspace settings optimized for Fortran projects

## Available Tasks

- **FORD: Generate Documentation** - Standard documentation generation (default build task)
- **FORD: Generate Documentation with Debug** - Generate docs with debug output
- **FORD: Generate Documentation with Graphs** - Generate docs with call graphs  
- **FORD: Open Documentation** - Open generated documentation in VS Code

## Customization

### Change Default Project File

Edit `.vscode/tasks.json` and update the `inputs` section:

```json
"inputs": [
    {
        "id": "projectFile",
        "description": "FORD project file", 
        "default": "my-project.md",  // <- Change this
        "type": "promptString"
    }
]
```

### Add Custom FORD Options

Modify any task's `args` array:

```json
{
    "label": "FORD: Custom Build",
    "command": "ford",
    "args": [
        "--graph",
        "--warn",
        "--output_dir", "custom-docs", 
        "${workspaceFolder}/my-project.md"
    ]
}
```

## Recommended Extensions

Install these VS Code extensions for the best experience:

- **Modern Fortran** - Fortran language support and syntax highlighting
- **Python** - Required for debugging FORD (if needed)
- **Markdown All in One** - Better editing for FORD project files
- **Live Server** - Preview generated HTML documentation

## Example Project Structure

```
my-fortran-project/
├── .vscode/
│   ├── tasks.json
│   ├── launch.json
│   └── settings.json
├── src/
│   ├── main.f90
│   └── module.f90  
├── ford-project.md
└── README.md
```

## Troubleshooting

**"ford: command not found"**
- Install FORD: `pip install ford`
- Verify installation: `ford --version`

**"Project file not found"**  
- Check the file path in your task configuration
- Ensure the project file exists in your workspace

**Permission errors**
- Ensure VS Code can write to the output directory
- Check that the output directory isn't read-only

## Full Documentation

For complete documentation on VS Code integration, see: [docs/user_guide/vs_code_integration.rst]

## Example Workspace

A complete VS Code workspace example is available in `ford-example.code-workspace` which includes all configurations in a single file.