# FORD project file for running the test_data source tree
@Project
name: TestDataProject
# Source tree containing Fortran source files to document/run
src: test_data/src
source_dir: test_data/src

# Output directory (as requested: "nerw" inside test_data)
out: test_data/nerw
output: test_data/nerw
out_dir: test_data/nerw

# Enable graphs and graph-related output
graphs: true
show_graphs: true
graphviz: true

# Turn on local variable display in generated docs
local_variables: true
local_vars: true
show_local_variables: true

# Extra common/run options (include any custom/new options you added below)
# Add or rename any keys here to match the new options you've implemented.
verbose: true
force: true
clean: false

# Placeholders for any additional new options you added to FORD.
# Replace or extend these with the exact option names/values your fork expects.
new_option_1: true
new_option_2: some_value
new_option_flag: true
@endproject

# Optional: brief usage instructions (run from repo root)
Run Ford on this project file to process source and emit outputs into test_data/nerw:

```sh
# from /workspaces/ford
ford test/test_data/project.md
# or explicitly point at the project file
python -m ford test/test_data/project.md
```