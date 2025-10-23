# -*- coding: utf-8 -*-
#
#  markdown_output.py
#  This file is part of FORD.
#
#  Copyright 2024 Christopher MacMackin <cmacmackin@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import os
import shutil
import pathlib
from typing import List, Optional
from itertools import chain

from ford.settings import ProjectSettings
from ford.utils import ProgressBar
from ford.console import warn
from ford.graphs import graphviz_installed, GraphManager


class MarkdownDocumentation:
    """
    Handles the creation of Markdown documentation files from a project.
    Can be used for standalone Markdown or GitBook format.
    """

    def __init__(self, settings: ProjectSettings, proj_docs: str, project, pagetree):
        self.project = project
        self.settings = settings
        self.proj_docs = proj_docs
        self.pagetree = pagetree
        self.output_dir = settings.output_dir
        self.is_gitbook = settings.output_format.lower() == "gitbook"
        
        # Store all pages that will be generated
        self.pages = []
        
        # Initialize graph manager if graphs are enabled
        self.graphs = None
        if settings.graph and graphviz_installed:
            # Use graphs subdirectory in output for markdown/gitbook
            graph_output_dir = self.output_dir / "graphs"
            graphparent = ""  # Relative path for markdown
            self.graphs = GraphManager(
                graph_output_dir,
                graphparent,
                settings.coloured_edges,
                settings.show_proc_parent,
                save_graphs=True,  # Always save graphs for markdown output
            )

    def generate(self):
        """Generate the markdown documentation"""
        print(f"  Creating Markdown documentation ({self.settings.output_format})... ", end="")
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate graphs if enabled
        if self.graphs and graphviz_installed:
            self._generate_graphs()
        
        # Generate index/README
        self._generate_index()
        
        # Generate documentation for each entity type
        self._generate_modules()
        self._generate_procedures()
        self._generate_types()
        self._generate_programs()
        self._generate_files()
        
        # Generate custom pages
        self._generate_custom_pages()
        
        # Generate GitBook-specific files if needed
        if self.is_gitbook:
            self._generate_gitbook_files()
        
        print("done")

    def _generate_graphs(self):
        """Generate graphs and export as SVG/PNG files"""
        if not self.graphs:
            return
        
        # Create graphs directory
        graphs_dir = self.output_dir / "graphs"
        graphs_dir.mkdir(exist_ok=True)
        
        # Register all entities with the graph manager
        for item in chain(
            self.project.types,
            self.project.absinterfaces,
            self.project.procedures,
            self.project.modules,
            self.project.submodules,
            self.project.programs,
            self.project.blockdata,
        ):
            self.graphs.register(item)
        
        # Generate all graphs
        self.graphs.graph_all()
        
        # Store graph references on project for use in documentation
        self.project.callgraph = self.graphs.callgraph
        self.project.typegraph = self.graphs.typegraph
        self.project.usegraph = self.graphs.usegraph
        self.project.filegraph = self.graphs.filegraph
        
        # Export graphs as SVG files to the graphs directory
        self.graphs.output_graphs(0)  # 0 = sequential processing
        
        # Also save individual entity graphs
        for mod in chain(self.project.modules, self.project.submodules):
            if hasattr(mod, 'usesgraph') and mod.usesgraph:
                mod.usesgraph.create_svg(graphs_dir)
        
        # Create markdown pages for project-level graphs
        self._create_graph_pages(graphs_dir)
    
    def _create_graph_pages(self, graphs_dir):
        """Create markdown pages for project-level graphs"""
        if not self.graphs:
            return
        
        # Call graph page
        if hasattr(self.project, 'callgraph') and self.project.callgraph:
            callgraph_file = graphs_dir / "callgraph.md"
            content = ["# Call Graph\n\n"]
            content.append("This graph shows the calling relationships between procedures in the project.\n\n")
            content.append("![Call Graph](callgraph.svg)\n\n")
            callgraph_file.write_text("".join(content), encoding="utf-8")
        
        # Type graph page
        if hasattr(self.project, 'typegraph') and self.project.typegraph:
            typegraph_file = graphs_dir / "typegraph.md"
            content = ["# Type Graph\n\n"]
            content.append("This graph shows the inheritance and composition relationships between types.\n\n")
            content.append("![Type Graph](typegraph.svg)\n\n")
            typegraph_file.write_text("".join(content), encoding="utf-8")
        
        # Module use graph page
        if hasattr(self.project, 'usegraph') and self.project.usegraph:
            usegraph_file = graphs_dir / "usegraph.md"
            content = ["# Module Use Graph\n\n"]
            content.append("This graph shows the dependencies between modules.\n\n")
            content.append("![Module Use Graph](usegraph.svg)\n\n")
            usegraph_file.write_text("".join(content), encoding="utf-8")
        
        # File graph page
        if hasattr(self.project, 'filegraph') and self.project.filegraph:
            filegraph_file = graphs_dir / "filegraph.md"
            content = ["# File Graph\n\n"]
            content.append("This graph shows the dependencies between source files.\n\n")
            content.append("![File Graph](filegraph.svg)\n\n")
            filegraph_file.write_text("".join(content), encoding="utf-8")

    def _generate_index(self):
        """Generate the main index/README file"""
        index_file = self.output_dir / ("README.md" if self.is_gitbook else "index.md")
        
        content = []
        content.append(f"# {self.settings.project}\n")
        
        if self.settings.summary:
            content.append(f"{self.settings.summary}\n")
        
        if self.proj_docs:
            content.append(f"\n{self.proj_docs}\n")
        
        # Add project information
        if self.settings.author:
            content.append(f"\n**Author:** {self.settings.author}\n")
        
        if self.settings.version:
            content.append(f"**Version:** {self.settings.version}\n")
        
        if self.settings.license:
            content.append(f"**License:** {self.settings.license}\n")
        
        # Add links to main sections
        content.append("\n## Documentation\n")
        
        if len(self.project.modules) + len(self.project.submodules) > 0:
            content.append("- [Modules](modules/index.md)\n")
        
        if len(self.project.procedures) > 0:
            content.append("- [Procedures](procedures/index.md)\n")
        
        if len(self.project.types) > 0:
            content.append("- [Types](types/index.md)\n")
        
        if len(self.project.programs) > 0:
            content.append("- [Programs](programs/index.md)\n")
        
        if self.settings.incl_src and len(self.project.files) > 0:
            content.append("- [Source Files](files/index.md)\n")
        
        # Add graphs section if available
        if self.graphs and hasattr(self.project, 'callgraph') and self.project.callgraph:
            content.append("\n## Project Graphs\n")
            if self.project.callgraph:
                content.append("- [Call Graph](graphs/callgraph.md)\n")
            if hasattr(self.project, 'typegraph') and self.project.typegraph:
                content.append("- [Type Graph](graphs/typegraph.md)\n")
            if hasattr(self.project, 'usegraph') and self.project.usegraph:
                content.append("- [Module Use Graph](graphs/usegraph.md)\n")
            if hasattr(self.project, 'filegraph') and self.project.filegraph:
                content.append("- [File Graph](graphs/filegraph.md)\n")
        
        index_file.write_text("".join(content), encoding="utf-8")
        self.pages.append(("", index_file.name, self.settings.project))

    def _generate_modules(self):
        """Generate documentation for modules"""
        if len(self.project.modules) + len(self.project.submodules) == 0:
            return
        
        modules_dir = self.output_dir / "modules"
        modules_dir.mkdir(exist_ok=True)
        
        # Generate index
        index_file = modules_dir / "index.md"
        content = ["# Modules\n\n"]
        
        all_modules = list(self.project.modules) + list(self.project.submodules)
        for mod in sorted(all_modules, key=lambda x: x.name.lower()):
            content.append(f"- [{mod.name}]({self._safe_filename(mod.name)}.md)")
            if hasattr(mod, 'meta') and mod.meta.summary:
                content.append(f" - {mod.meta.summary}")
            content.append("\n")
        
        index_file.write_text("".join(content), encoding="utf-8")
        self.pages.append(("modules", "index.md", "Modules"))
        
        # Generate individual module pages
        for mod in all_modules:
            self._generate_module_page(mod, modules_dir)

    def _generate_module_page(self, mod, modules_dir):
        """Generate a page for a single module"""
        filename = self._safe_filename(mod.name) + ".md"
        filepath = modules_dir / filename
        
        content = []
        content.append(f"# Module: {mod.name}\n\n")
        
        # Add module documentation
        if hasattr(mod, 'doc') and mod.doc:
            content.append(f"{mod.doc}\n\n")
        
        # Add graph if available
        if self.graphs and hasattr(mod, 'usesgraph') and mod.usesgraph:
            # The graph identifier is constructed by the Graph class
            graph_ident = mod.usesgraph.ident
            # Check if graph file exists (it would be saved in graphs directory)
            svg_path = self.output_dir / "graphs" / f"{graph_ident}.svg"
            if svg_path.exists():
                content.append("## Module Dependencies Graph\n\n")
                content.append(f"![{mod.name} dependencies](../graphs/{graph_ident}.svg)\n\n")
        
        # Add procedures
        if hasattr(mod, 'routines') and mod.routines:
            content.append("## Procedures\n\n")
            for routine in mod.routines:
                content.append(f"### {routine.name}\n\n")
                if hasattr(routine, 'doc') and routine.doc:
                    content.append(f"{routine.doc}\n\n")
                if hasattr(routine, 'proctype'):
                    content.append(f"**Type:** {routine.proctype}\n\n")
        
        # Add types
        if hasattr(mod, 'types') and mod.types:
            content.append("## Types\n\n")
            for dtype in mod.types:
                content.append(f"### {dtype.name}\n\n")
                if hasattr(dtype, 'doc') and dtype.doc:
                    content.append(f"{dtype.doc}\n\n")
        
        # Add variables
        if hasattr(mod, 'variables') and mod.variables:
            content.append("## Variables\n\n")
            for var in mod.variables:
                content.append(f"### {var.name}\n\n")
                if hasattr(var, 'vartype'):
                    content.append(f"**Type:** {var.vartype}\n\n")
                if hasattr(var, 'doc') and var.doc:
                    content.append(f"{var.doc}\n\n")
        
        filepath.write_text("".join(content), encoding="utf-8")
        self.pages.append(("modules", filename, mod.name))

    def _generate_procedures(self):
        """Generate documentation for procedures"""
        if len(self.project.procedures) == 0:
            return
        
        procs_dir = self.output_dir / "procedures"
        procs_dir.mkdir(exist_ok=True)
        
        # Generate index
        index_file = procs_dir / "index.md"
        content = ["# Procedures\n\n"]
        
        for proc in sorted(self.project.procedures, key=lambda x: x.name.lower()):
            content.append(f"- [{proc.name}]({self._safe_filename(proc.name)}.md)")
            if hasattr(proc, 'meta') and proc.meta.summary:
                content.append(f" - {proc.meta.summary}")
            content.append("\n")
        
        index_file.write_text("".join(content), encoding="utf-8")
        self.pages.append(("procedures", "index.md", "Procedures"))
        
        # Generate individual procedure pages
        for proc in self.project.procedures:
            self._generate_procedure_page(proc, procs_dir)

    def _generate_procedure_page(self, proc, procs_dir):
        """Generate a page for a single procedure"""
        filename = self._safe_filename(proc.name) + ".md"
        filepath = procs_dir / filename
        
        content = []
        content.append(f"# {proc.proctype.title()}: {proc.name}\n\n")
        
        # Add procedure documentation
        if hasattr(proc, 'doc') and proc.doc:
            content.append(f"{proc.doc}\n\n")
        
        # Add procedure signature
        if hasattr(proc, 'proctype'):
            content.append(f"**Type:** {proc.proctype}\n\n")
        
        # Add arguments
        if hasattr(proc, 'args') and proc.args:
            content.append("## Arguments\n\n")
            for arg in proc.args:
                content.append(f"### {arg.name}\n\n")
                if hasattr(arg, 'vartype'):
                    content.append(f"**Type:** {arg.vartype}\n\n")
                if hasattr(arg, 'intent'):
                    content.append(f"**Intent:** {arg.intent}\n\n")
                if hasattr(arg, 'doc') and arg.doc:
                    content.append(f"{arg.doc}\n\n")
        
        # Add return value for functions
        if hasattr(proc, 'retvar') and proc.retvar:
            content.append("## Return Value\n\n")
            if hasattr(proc.retvar, 'vartype'):
                content.append(f"**Type:** {proc.retvar.vartype}\n\n")
            if hasattr(proc.retvar, 'doc') and proc.retvar.doc:
                content.append(f"{proc.retvar.doc}\n\n")
        
        filepath.write_text("".join(content), encoding="utf-8")
        self.pages.append(("procedures", filename, proc.name))

    def _generate_types(self):
        """Generate documentation for derived types"""
        if len(self.project.types) == 0:
            return
        
        types_dir = self.output_dir / "types"
        types_dir.mkdir(exist_ok=True)
        
        # Generate index
        index_file = types_dir / "index.md"
        content = ["# Derived Types\n\n"]
        
        for dtype in sorted(self.project.types, key=lambda x: x.name.lower()):
            content.append(f"- [{dtype.name}]({self._safe_filename(dtype.name)}.md)")
            if hasattr(dtype, 'meta') and dtype.meta.summary:
                content.append(f" - {dtype.meta.summary}")
            content.append("\n")
        
        index_file.write_text("".join(content), encoding="utf-8")
        self.pages.append(("types", "index.md", "Derived Types"))
        
        # Generate individual type pages
        for dtype in self.project.types:
            self._generate_type_page(dtype, types_dir)

    def _generate_type_page(self, dtype, types_dir):
        """Generate a page for a single derived type"""
        filename = self._safe_filename(dtype.name) + ".md"
        filepath = types_dir / filename
        
        content = []
        content.append(f"# Type: {dtype.name}\n\n")
        
        # Add type documentation
        if hasattr(dtype, 'doc') and dtype.doc:
            content.append(f"{dtype.doc}\n\n")
        
        # Add components/fields
        if hasattr(dtype, 'variables') and dtype.variables:
            content.append("## Components\n\n")
            for var in dtype.variables:
                content.append(f"### {var.name}\n\n")
                if hasattr(var, 'vartype'):
                    content.append(f"**Type:** {var.vartype}\n\n")
                if hasattr(var, 'doc') and var.doc:
                    content.append(f"{var.doc}\n\n")
        
        # Add type-bound procedures
        if hasattr(dtype, 'boundprocs') and dtype.boundprocs:
            content.append("## Type-Bound Procedures\n\n")
            for proc in dtype.boundprocs:
                content.append(f"### {proc.name}\n\n")
                if hasattr(proc, 'doc') and proc.doc:
                    content.append(f"{proc.doc}\n\n")
        
        filepath.write_text("".join(content), encoding="utf-8")
        self.pages.append(("types", filename, dtype.name))

    def _generate_programs(self):
        """Generate documentation for programs"""
        if len(self.project.programs) == 0:
            return
        
        progs_dir = self.output_dir / "programs"
        progs_dir.mkdir(exist_ok=True)
        
        # Generate index
        index_file = progs_dir / "index.md"
        content = ["# Programs\n\n"]
        
        for prog in sorted(self.project.programs, key=lambda x: x.name.lower()):
            content.append(f"- [{prog.name}]({self._safe_filename(prog.name)}.md)")
            if hasattr(prog, 'meta') and prog.meta.summary:
                content.append(f" - {prog.meta.summary}")
            content.append("\n")
        
        index_file.write_text("".join(content), encoding="utf-8")
        self.pages.append(("programs", "index.md", "Programs"))
        
        # Generate individual program pages
        for prog in self.project.programs:
            self._generate_program_page(prog, progs_dir)

    def _generate_program_page(self, prog, progs_dir):
        """Generate a page for a single program"""
        filename = self._safe_filename(prog.name) + ".md"
        filepath = progs_dir / filename
        
        content = []
        content.append(f"# Program: {prog.name}\n\n")
        
        # Add program documentation
        if hasattr(prog, 'doc') and prog.doc:
            content.append(f"{prog.doc}\n\n")
        
        filepath.write_text("".join(content), encoding="utf-8")
        self.pages.append(("programs", filename, prog.name))

    def _generate_files(self):
        """Generate documentation for source files"""
        if not self.settings.incl_src or len(self.project.files) == 0:
            return
        
        files_dir = self.output_dir / "files"
        files_dir.mkdir(exist_ok=True)
        
        # Generate index
        index_file = files_dir / "index.md"
        content = ["# Source Files\n\n"]
        
        for src_file in sorted(self.project.files, key=lambda x: x.name.lower()):
            content.append(f"- [{src_file.name}]({self._safe_filename(src_file.name)}.md)\n")
        
        index_file.write_text("".join(content), encoding="utf-8")
        self.pages.append(("files", "index.md", "Source Files"))

    def _generate_custom_pages(self):
        """Generate custom user-defined pages from pagetree"""
        if not self.pagetree:
            return
        
        for page in self.pagetree:
            self._generate_custom_page(page)

    def _generate_custom_page(self, page, parent_dir=None):
        """Generate a custom page"""
        if parent_dir is None:
            parent_dir = self.output_dir / "pages"
            parent_dir.mkdir(exist_ok=True)
        
        # Write the page content
        if hasattr(page, 'contents') and hasattr(page, 'title'):
            filename = self._safe_filename(page.title) + ".md"
            filepath = parent_dir / filename
            filepath.write_text(page.contents, encoding="utf-8")
            
            rel_path = str(filepath.relative_to(self.output_dir))
            self.pages.append((os.path.dirname(rel_path), os.path.basename(rel_path), page.title))
        
        # Process child pages
        if hasattr(page, 'subpages') and page.subpages:
            for subpage in page.subpages:
                self._generate_custom_page(subpage, parent_dir)

    def _generate_gitbook_files(self):
        """Generate GitBook-specific files (SUMMARY.md, book.json)"""
        # Generate SUMMARY.md
        summary_file = self.output_dir / "SUMMARY.md"
        content = ["# Summary\n\n"]
        content.append("* [Introduction](README.md)\n")
        
        # Add all pages in a structured way
        sections = {}
        for directory, filename, title in self.pages:
            if directory == "":
                continue  # Skip the main README
            if directory not in sections:
                sections[directory] = []
            sections[directory].append((filename, title))
        
        # Add sections in a logical order
        section_order = ["modules", "procedures", "types", "programs", "files", "pages"]
        for section in section_order:
            if section in sections:
                # Capitalize section name for display
                section_title = section.replace("_", " ").title()
                content.append(f"\n## {section_title}\n\n")
                
                # Add index first
                index_items = [(f, t) for f, t in sections[section] if f == "index.md"]
                other_items = [(f, t) for f, t in sections[section] if f != "index.md"]
                
                for filename, title in sorted(index_items + other_items, key=lambda x: x[0]):
                    if filename == "index.md":
                        content.append(f"* [{section_title} Overview]({section}/{filename})\n")
                    else:
                        content.append(f"* [{title}]({section}/{filename})\n")
        
        summary_file.write_text("".join(content), encoding="utf-8")
        
        # Generate book.json
        book_json = {
            "title": self.settings.project,
            "description": self.settings.summary or "",
            "author": self.settings.author or "",
            "language": "en",
            "structure": {
                "readme": "README.md",
                "summary": "SUMMARY.md"
            }
        }
        
        import json
        book_file = self.output_dir / "book.json"
        book_file.write_text(json.dumps(book_json, indent=2), encoding="utf-8")

    @staticmethod
    def _safe_filename(name: str) -> str:
        """Convert a name to a safe filename"""
        # Replace unsafe characters with underscores
        safe = name.replace("/", "_").replace("\\", "_").replace(" ", "_")
        # Remove other problematic characters
        safe = "".join(c for c in safe if c.isalnum() or c in "_-.")
        return safe.lower()

    def writeout(self):
        """Write out the markdown documentation"""
        self.generate()
        print(f"\nBrowse the generated documentation: {self.output_dir}")
