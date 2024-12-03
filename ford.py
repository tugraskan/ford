#!/usr/bin/env python
"""Wrapper for FORD fortran documentation generator"""

from ford import run
from ford.fortran_project import Project
from ford.external_project import dump_modules

def main():
    project = Project()
    project.correlate()
    if project.settings.externalize:
        dump_modules(project)

if __name__ == "__main__":
    main()
