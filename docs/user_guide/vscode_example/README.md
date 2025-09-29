# FORD VS Code Integration Example

This directory contains example configuration files for integrating FORD with Visual Studio Code.

## Quick Start

1. Copy the `.vscode` folder to your Fortran project root
2. Modify the `projectFile` default in the configuration files to match your project file name
3. Use `Ctrl+Shift+P` → "Tasks: Run Build Task" to generate documentation

## Files Included

- **`.vscode/tasks.json`** - Task definitions for running FORD
- **`.vscode/launch.json`** - Debug configurations 
- **`.vscode/settings.json`** - Workspace settings optimized for Fortran projects
- **`ford-example.code-workspace`** - Complete VS Code workspace file

## Usage

### Running FORD

**Method 1: Using Tasks (Recommended)**
1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type "Tasks: Run Task" 
3. Select "FORD: Generate Documentation"
4. Enter your project file name when prompted

**Method 2: Using Build Task Shortcut**
1. Press `Ctrl+Shift+B` (Windows/Linux) or `Cmd+Shift+B` (Mac) 
2. This runs the default build task (FORD documentation generation)

**Method 3: Using Terminal**
1. Open integrated terminal (`Ctrl+\``)
2. Run `ford your-project-file.md`

### Available Tasks

- **FORD: Generate Documentation** - Standard documentation generation
- **FORD: Generate Documentation with Debug** - Generate docs with debug output  
- **FORD: Generate Documentation with Graphs** - Generate docs with call graphs
- **FORD: Open Documentation** - Open generated documentation in VS Code

### Debugging FORD

For developers working on FORD itself:
1. Press `F5` or use "Run and Debug" panel
2. Select "FORD: Debug Documentation Generation" 
3. Enter your project file name when prompted

## Customization

### Change Default Project File

Edit `.vscode/tasks.json` and modify the `inputs` section:

```json
"inputs": [
    {
        "id": "projectFile", 
        "description": "FORD project file",
        "default": "my-project-file.md",  // <- Change this
        "type": "promptString"
    }
]
```

### Add Custom FORD Arguments

Modify the `args` array in any task:

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

- **Modern Fortran** (`fortls.fortls`) - Fortran language support
- **Python** (`ms-python.python`) - Required for debugging FORD
- **Markdown All in One** (`yzhang.markdown-all-in-one`) - Better Markdown editing
- **Live Server** (`ritwickdey.liveserver`) - Preview generated HTML docs

## Project Structure Example

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
├── README.md
└── .gitignore
```

## Troubleshooting

**FORD command not found**
- Ensure FORD is installed: `pip install ford`
- Check if FORD is in your PATH: `ford --version`

**Project file not found**
- Verify the path in your task configuration
- Use `${workspaceFolder}/your-file.md` for files in workspace root

**Permission errors** 
- Ensure VS Code has write permissions to output directory
- Check that output directory isn't read-only

## Integration with Build Systems

### FMP Integration
If using Fortran Package Manager, modify tasks to use `fmp.toml`:

```json
"args": ["${workspaceFolder}/fmp.toml"]
```

### Makefile Integration
Create a task that runs your existing Makefile:

```json
{
    "label": "Make Documentation",
    "type": "shell", 
    "command": "make",
    "args": ["docs"]
}
```