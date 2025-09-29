========================
Visual Studio Code Setup
========================

This guide explains how to configure Visual Studio Code (VS Code) to work seamlessly with FORD for generating Fortran documentation.

Prerequisites
=============

Before setting up FORD in VS Code, ensure you have:

1. **VS Code** installed
2. **FORD** installed (see `sec-installation`)
3. **Python extension** for VS Code (for debugging FORD itself)
4. **Modern Fortran** extension (recommended for Fortran syntax highlighting)

Quick Setup
===========

The FORD repository includes pre-configured VS Code settings. To use them:

1. Copy the ``.vscode`` folder from the FORD repository to your Fortran project root
2. Modify the ``projectFile`` default in the configuration files to match your project file name

VS Code Configuration Files
===========================

tasks.json
----------

The ``tasks.json`` file defines tasks for running FORD from within VS Code. Here's a basic configuration:

.. code-block:: json

    {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "FORD: Generate Documentation",
                "type": "shell",
                "command": "ford",
                "args": ["${workspaceFolder}/${input:projectFile}"],
                "group": {
                    "kind": "build",
                    "isDefault": true
                },
                "presentation": {
                    "echo": true,
                    "reveal": "always",
                    "focus": false,
                    "panel": "shared"
                },
                "problemMatcher": [],
                "detail": "Generate documentation using FORD"
            }
        ],
        "inputs": [
            {
                "id": "projectFile",
                "description": "FORD project file",
                "default": "ford-project.md",
                "type": "promptString"
            }
        ]
    }

Available Tasks
~~~~~~~~~~~~~~~

The configuration includes several pre-defined tasks:

- **FORD: Generate Documentation** - Standard documentation generation
- **FORD: Generate Documentation with Debug** - Generate docs with debug output
- **FORD: Generate Documentation with Graphs** - Generate docs with call graphs
- **FORD: Open Documentation** - Open generated documentation in VS Code

launch.json
-----------

For debugging FORD itself (useful for FORD developers), the ``launch.json`` file provides Python debugging configurations:

.. code-block:: json

    {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "FORD: Debug Documentation Generation",
                "type": "python",
                "request": "launch",
                "module": "ford",
                "args": ["${workspaceFolder}/${input:projectFile}"],
                "console": "integratedTerminal",
                "justMyCode": false,
                "cwd": "${workspaceFolder}"
            }
        ]
    }

settings.json
-------------

The workspace settings optimize VS Code for Fortran projects with FORD:

.. code-block:: json

    {
        "files.associations": {
            "*.md": "markdown",
            "*.f90": "fortran-modern",
            "*.f95": "fortran-modern",
            "*.f03": "fortran-modern",
            "*.f08": "fortran-modern",
            "*.fpp": "fortran-modern"
        },
        "files.exclude": {
            "**/doc/**": false
        },
        "search.exclude": {
            "**/doc/**": true
        }
    }

Usage Instructions
==================

Running FORD from VS Code
--------------------------

1. **Using Tasks (Recommended)**:
   
   - Press ``Ctrl+Shift+P`` (or ``Cmd+Shift+P`` on Mac)
   - Type "Tasks: Run Task"
   - Select "FORD: Generate Documentation"
   - Enter your project file name when prompted (or accept the default)

2. **Using the Command Palette**:
   
   - Press ``Ctrl+Shift+P``
   - Type "Terminal: Create New Terminal"
   - Run ``ford your-project-file.md`` in the terminal

3. **Using Keyboard Shortcuts**:
   
   - Press ``Ctrl+Shift+P`` and run "Tasks: Run Build Task" to run the default FORD task

Setting Up Your Project
------------------------

1. Create a FORD project file (e.g., ``ford-project.md``) in your workspace root
2. Update the ``projectFile`` default in ``.vscode/tasks.json`` if your project file has a different name
3. Ensure your Fortran source files are in the correct directory (``src/`` by default)

Example Project Structure
-------------------------

.. code-block:: text

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

Customization
=============

Modifying Tasks
---------------

You can customize the FORD tasks by editing ``.vscode/tasks.json``:

- Change the default project file name in the ``inputs`` section
- Add custom FORD command-line arguments
- Modify presentation settings (where output appears)

Adding Custom Tasks
-------------------

To add a custom FORD task with specific options:

.. code-block:: json

    {
        "label": "FORD: Custom Build",
        "type": "shell",
        "command": "ford",
        "args": [
            "--graph",
            "--warn", 
            "--output_dir", "custom-docs",
            "${workspaceFolder}/my-project.md"
        ],
        "group": "build"
    }

Troubleshooting
===============

Common Issues
-------------

1. **FORD command not found**: Ensure FORD is installed and available in your PATH
2. **Project file not found**: Check that the project file path is correct in your task configuration
3. **Permission errors**: Ensure VS Code has write permissions to the output directory

Debugging FORD
--------------

To debug FORD execution:

1. Use the "FORD: Generate Documentation with Debug" task
2. Or use the Python debugger with the provided launch configuration
3. Check the integrated terminal for detailed error messages

Tips and Best Practices
========================

1. **Use relative paths** in your FORD project file for portability
2. **Add the documentation output directory to .gitignore** to avoid committing generated files
3. **Use keyboard shortcuts** for frequently used tasks
4. **Organize your Fortran source files** in clear directory structures
5. **Document your code thoroughly** with FORD-compatible comments

Recommended Extensions
======================

For the best experience with FORD and Fortran in VS Code, install these extensions:

- **Modern Fortran** - Syntax highlighting and IntelliSense for Fortran
- **Python** - Required for debugging FORD (if needed)
- **Markdown All in One** - Better editing for FORD project files
- **Live Server** - Preview generated HTML documentation

Integration with Build Systems
==============================

FMP Integration
---------------

If you're using the Fortran Package Manager (fmp), FORD can read project metadata from ``fmp.toml``. Your VS Code tasks can then simply run:

.. code-block:: json

    {
        "command": "ford",
        "args": ["${workspaceFolder}/fmp.toml"]
    }

Make Integration
----------------

You can integrate FORD tasks with existing Makefiles by creating a task that runs ``make docs`` if your Makefile includes FORD targets.

Conclusion
==========

With proper VS Code configuration, generating documentation with FORD becomes a seamless part of your development workflow. The provided configuration files serve as a starting point that you can customize to fit your specific project needs.