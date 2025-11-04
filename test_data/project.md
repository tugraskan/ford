---
project: TestDataProject
src_dir: src
output_dir: doc
graph: true
proc_internals: true
force: true
---

# FORD project file for running the test_data source tree

This project file processes the Fortran source files in src and generates
documentation in doc with graphs enabled.

Run Ford on this project file from the repository root:

```sh
ford test_data/project.md
```