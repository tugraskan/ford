# -*- coding: utf-8 -*-
#
#  output.py
#  This file is part of FORD.
#
#  Copyright 2015 Christopher MacMackin <cmacmackin@gmail.com>
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

from dataclasses import asdict
import sys
import os
import re
import shutil
import traceback
from itertools import chain
import pathlib
import time
from typing import List, Union, Callable, Type, Tuple
from warnings import simplefilter

from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
import jinja2

from ford.console import warn
from ford.sourceform import FortranBase
import ford.tipue_search
from ford.utils import ProgressBar
from ford.graphs import graphviz_installed, GraphManager
from ford.settings import ProjectSettings, EntitySettings

loc = pathlib.Path(__file__).parent
env = jinja2.Environment(
    trim_blocks=True,
    lstrip_blocks=True,
)
env.globals["path"] = os.path  # this lets us call path.* in templates

# Ignore bs4 warning about parsing strings that look like filenames
simplefilter("ignore", MarkupResemblesLocatorWarning)


def is_more_than_one(collection):
    return collection > 1


def meta(entity, item):
    """Get item from entity's meta dict, but give a more helpful
    error message if entity doesn't have a meta attribute

    Hopefully gives a better error than the common "RuntimeError: 'str
    object' has no attribute 'meta'"

    """
    if not hasattr(entity, "meta"):
        return jinja2.StrictUndefined(
            f"Unknown entity '{entity}': This likely means an error in parsing, "
            "please check that this file compiles with a Fortran compiler"
        )

    return getattr(entity.meta, item, None)


def relative_url(entity: Union[FortranBase, str], page_url: pathlib.Path) -> str:
    """Convert any links with absolute paths to the output directory
    to relative paths to ``page_url``
    """
    if isinstance(entity, str) and "/" not in entity or entity is None:
        return entity

    # Find first link in `entity` and get the path. If `entity`
    # doesn't have any links, it might be a URL itself that needs
    # fixing
    link_str = str(entity)
    link = BeautifulSoup(link_str, features="html.parser").a
    if link is not None:
        link_href = str(link["href"])
        if link_href.startswith("http"):
            # This is (almost certainly) an external link, so better
            # be correct already
            return entity
        link_path = str(pathlib.Path(link_href).resolve())
    else:
        link_path = link_str

    new_path = os.path.relpath(link_path, page_url.parent)
    return link_str.replace(link_path, new_path)


def extract_io_variables(io_statement, procedure=None):
    """
    Extract variable names and their types from I/O statements.

    Args:
        io_statement: String containing the Fortran I/O statement
        procedure: FortranProcedure object to get variable type information

    Returns:
        List of tuples (variable_name, variable_type)
    """
    if not procedure or not io_statement:
        return []

    # Get all variables from the procedure (args + local + non-local)
    all_vars = {}

    # Add arguments
    if hasattr(procedure, "args") and procedure.args:
        for var in procedure.args:
            if hasattr(var, "name") and hasattr(var, "full_type"):
                all_vars[var.name.lower()] = str(var.full_type)

    # Add local variables
    if hasattr(procedure, "local_variables") and procedure.local_variables:
        for var in procedure.local_variables:
            if hasattr(var, "name") and hasattr(var, "full_type"):
                all_vars[var.name.lower()] = str(var.full_type)

    # Add non-local variables
    if hasattr(procedure, "non_local_variables") and procedure.non_local_variables:
        for var in procedure.non_local_variables:
            if hasattr(var, "name") and hasattr(var, "full_type"):
                all_vars[var.name.lower()] = str(var.full_type)

    # Extract variable names from I/O statement
    # For write/read statements with format: write(unit, 'format') variables
    # Match patterns like: write(..., '...') var1, var2

    # Pattern to match write/read with format and variables
    patterns = [
        # write(unit, 'format') variables
        r"(?:read|write)\s*\([^)]+\s*,\s*\'[^\']*\'\s*\)\s*(.+)",
        # write(unit, "format") variables
        r"(?:read|write)\s*\([^)]+\s*,\s*\"[^\"]*\"\s*\)\s*(.+)",
        # write(unit, format=...) variables
        r"(?:read|write)\s*\([^)]+\)\s*(.+)",
    ]

    var_part = None
    for pattern in patterns:
        io_match = re.search(pattern, io_statement, re.IGNORECASE)
        if io_match:
            var_part = io_match.group(1).strip()
            break

    if not var_part:
        return []

    # Split by commas, but be careful with quoted strings
    var_items = []
    current_item = ""
    in_quotes = False
    quote_char = None

    for char in var_part:
        if char in ["'", '"'] and not in_quotes:
            in_quotes = True
            quote_char = char
            current_item += char
        elif char == quote_char and in_quotes:
            in_quotes = False
            quote_char = None
            current_item += char
        elif char == "," and not in_quotes:
            if current_item.strip():
                var_items.append(current_item.strip())
            current_item = ""
        else:
            current_item += char

    # Add the last item
    if current_item.strip():
        var_items.append(current_item.strip())

    # Extract variable names from each item
    var_names = []
    for item in var_items:
        # Skip string literals
        if item.startswith(("'", '"')):
            continue

        # Extract variable names (handle array indices, expressions, etc.)
        # Look for word characters at the start (variable name)
        var_match = re.match(r"([a-zA-Z_][a-zA-Z0-9_]*)", item)
        if var_match:
            var_names.append(var_match.group(1))

    # Match variable names to their types
    result = []
    for var_name in var_names:
        var_key = var_name.lower()
        if var_key in all_vars:
            result.append((var_name, all_vars[var_key]))
        else:
            # If we can't find the type, still show the variable name
            result.append((var_name, "unknown"))

    return result


def create_header_table(var, parent_type_name=None):
    """
    Create a transposed table for Fortran header type declarations.

    Args:
        var: FortranVariable or FortranType object containing the header type
        parent_type_name: Optional name of the parent type for the Attributes row

    Returns:
        Dictionary with table data structure:
        {
            'fields': [field_names],
            'attributes': [attribute_references],
            'names': [field_names],
            'initials': [initial_values],
            'types': [type_declarations]
        }
    """
    if not var:
        return None

    # Get the type definition - could be from var.proto[0] if it's a variable
    # or directly if it's a type
    type_def = None
    if hasattr(var, "proto") and var.proto and len(var.proto) > 0:
        type_def = var.proto[0]
        # If proto[0] is a string, we couldn't resolve the type
        if isinstance(type_def, str):
            return None
    elif hasattr(var, "variables"):
        # It's already a type definition
        type_def = var
    else:
        return None

    # Check if it's actually a FortranType with variables
    if not hasattr(type_def, "variables") or not type_def.variables:
        return None

    # Extract the type name for attributes
    if parent_type_name is None:
        parent_type_name = getattr(type_def, "name", "unknown")

    fields = []
    attributes = []
    names = []
    initials = []
    types = []

    # Process each variable in the type
    for component in type_def.variables:
        if not hasattr(component, "name"):
            continue

        field_name = component.name
        fields.append(field_name)

        # Attributes: parent_type%field_name
        attributes.append(f"{parent_type_name}%{field_name}")

        # Name: just the field name
        names.append(field_name)

        # Initial: the initial value (preserve exact spacing)
        initial_value = getattr(component, "initial", None)
        if initial_value is not None:
            # Initial values should already be strings with quotes preserved
            initials.append(str(initial_value))
        else:
            initials.append("")

        # Type: the full type specification (e.g., character(len=6))
        type_str = getattr(
            component,
            "full_type",
            component.vartype if hasattr(component, "vartype") else "",
        )
        types.append(str(type_str))

    if not fields:
        return None

    return {
        "fields": fields,
        "attributes": attributes,
        "names": names,
        "initials": initials,
        "types": types,
    }


def create_io_schema_table(operation, procedure):
    """
    Create a schema table for an I/O operation (read or write).
    
    For each variable in the operation, this creates a row with:
    - Variable name
    - Data type
    - Initial/default value
    - Description
    
    If a variable is a whole type (not just a component), it expands to show all components.
    
    Args:
        operation: Dictionary containing the I/O operation details with 'parameters' key
        procedure: The FortranProcedure object that contains variable information
        
    Returns:
        List of dictionaries, each representing a row in the schema table:
        {
            'name': variable name,
            'type': data type,
            'initial': initial/default value,
            'description': description from meta/doc
        }
    """
    if not operation or not procedure:
        return []
    
    # Get the list of variables from the operation
    variables = operation.get('parameters', [])
    if not variables:
        return []
    
    schema_rows = []
    
    for var_expr in variables:
        # Parse the variable expression - it might be:
        # 1. Simple variable: "varname"
        # 2. Array element: "var(i)"
        # 3. Derived type component: "module%varname" or "type%component"
        
        # Extract base variable name
        base_var_name = var_expr.split('%')[0].split('(')[0].strip()
        
        # Try to find this variable in the procedure's variables
        var_obj = None
        if hasattr(procedure, 'variables'):
            for v in procedure.variables:
                if hasattr(v, 'name') and v.name.lower() == base_var_name.lower():
                    var_obj = v
                    break
        
        # If not found locally, try module variables
        if not var_obj and hasattr(procedure, 'all_vars'):
            var_obj = procedure.all_vars.get(base_var_name.lower())
        
        # Check if this is a whole type or a component access
        is_component_access = '%' in var_expr
        
        if var_obj and not is_component_access:
            # Check if this is a derived type that should be expanded
            type_def = None
            if hasattr(var_obj, 'proto') and var_obj.proto and len(var_obj.proto) > 0:
                type_def = var_obj.proto[0]
                if not isinstance(type_def, str) and hasattr(type_def, 'variables') and type_def.variables:
                    # Expand the type to show all components
                    for component in type_def.variables:
                        if not hasattr(component, 'name'):
                            continue
                        
                        comp_name = f"{var_expr}%{component.name}"
                        comp_type = getattr(component, 'full_type', 
                                          getattr(component, 'vartype', 'unknown'))
                        comp_initial = getattr(component, 'initial', '')
                        comp_desc = ''
                        if hasattr(component, 'meta'):
                            comp_desc = component.meta('summary', '')
                        
                        schema_rows.append({
                            'name': comp_name,
                            'type': str(comp_type),
                            'initial': str(comp_initial) if comp_initial else '-',
                            'description': comp_desc
                        })
                    continue
        
        # For component access or simple variables, add a single row
        var_type = 'unknown'
        var_initial = '-'
        var_desc = ''
        
        if var_obj:
            var_type = getattr(var_obj, 'full_type', 
                             getattr(var_obj, 'vartype', 'unknown'))
            var_initial = getattr(var_obj, 'initial', '-')
            if hasattr(var_obj, 'meta'):
                var_desc = var_obj.meta('summary', '')
        
        schema_rows.append({
            'name': var_expr,
            'type': str(var_type),
            'initial': str(var_initial) if var_initial and var_initial != '-' else '-',
            'description': var_desc
        })
    
    return schema_rows




env.tests["more_than_one"] = is_more_than_one
env.filters["meta"] = meta
env.filters["relurl"] = relative_url
env.filters["extract_io_variables"] = extract_io_variables
env.filters["create_header_table"] = create_header_table
env.filters["create_io_schema_table"] = create_io_schema_table

USER_WRITABLE_ONLY = 0o755


class Documentation:
    """
    Represents and handles the creation of the documentation files from
    a project.
    """

    def __init__(self, settings: ProjectSettings, proj_docs: str, project, pagetree):
        # This lets us use meta data anywhere within the template.
        # Also, in future for other template, we may not need to
        # pass the data obj.
        env.globals["projectData"] = asdict(settings)
        env.loader = jinja2.FileSystemLoader(
            settings.html_template_dir + [loc / "templates"]
        )

        self.project = project
        self.settings = settings
        # Jinja2's `if` statement counts `None` as truthy, so to avoid
        # lots of refactoring and messiness in the templates, just get
        # rid of None values
        self.data = {k: v for k, v in asdict(settings).items() if v is not None}
        self.data["pages"] = pagetree
        # Remove "project_url" so we can set it as a relative path for
        # each page individually and not have it clobbered by this dict
        del self.data["project_url"]
        self.lists: List[ListPage] = []
        self.docs = []
        self.njobs = settings.parallel
        self.parallel = self.njobs > 0

        self.index = IndexPage(self.data, project, proj_docs)
        self.search = SearchPage(self.data, project)
        if not graphviz_installed and settings.graph:
            warn("Will not be able to generate graphs. Graphviz not installed.")
        if settings.relative:
            graphparent = "../"
        else:
            graphparent = ""

        print("  Creating HTML documentation... ", end="")
        html_time_start = time.time()
        try:
            PageFactory = Union[Type, Callable]

            # Create individual entity pages
            entity_list_page_map: List[Tuple[List, PageFactory]] = [
                (project.types, TypePage),
                (project.absinterfaces, AbsIntPage),
                (project.procedures, ProcPage),
                (project.submodprocedures, ProcPage),
                (project.modules, ModulePage),
                (project.submodules, ModulePage),
                (project.programs, ProgPage),
                (project.blockdata, BlockPage),
                (project.namelists, NamelistPage),
                (project.iofiles, IOFilePage),
            ]
            if settings.incl_src:
                entity_list_page_map.append((project.allfiles, FilePage))

            for entity_list, page_class in entity_list_page_map:
                for item in entity_list:
                    self.docs.append(page_class(self.data, project, item))

            # Create lists of each entity type
            if len(project.procedures) > 0:
                self.lists.append(ProcList(self.data, project))
            if settings.incl_src and (
                len(project.files) + len(project.extra_files) > 1
            ):
                self.lists.append(FileList(self.data, project))
            if len(project.modules) + len(project.submodules) > 0:
                self.lists.append(ModList(self.data, project))
            if len(project.programs) > 1:
                self.lists.append(ProgList(self.data, project))
            if len(project.types) > 0:
                self.lists.append(TypeList(self.data, project))
            if len(project.absinterfaces) > 0:
                self.lists.append(AbsIntList(self.data, project))
            if len(project.blockdata) > 1:
                self.lists.append(BlockList(self.data, project))
            if project.namelists:
                self.lists.append(NamelistList(self.data, project))
            if project.iofiles:
                self.lists.append(IOList(self.data, project))

            # Create static pages
            self.pagetree = [
                PagetreePage(self.data, project, item) for item in (pagetree or [])
            ]
        except Exception:
            if settings.dbg:
                traceback.print_exc()
                sys.exit("Error encountered.")
            else:
                sys.exit('Error encountered. Run with "--debug" flag for traceback.')

        html_time_end = time.time()
        print(f"done in {html_time_end - html_time_start:5.3f}s")

        self.graphs = GraphManager(
            self.data.get("graph_dir", ""),
            graphparent,
            settings.coloured_edges,
            settings.show_proc_parent,
            save_graphs=bool(self.data.get("graph_dir", False)),
        )

        if graphviz_installed and settings.graph:
            for entity_list in [
                project.types,
                project.procedures,
                project.submodprocedures,
                project.modules,
                project.submodules,
                project.programs,
                project.files,
                project.blockdata,
            ]:
                for item in entity_list:
                    self.graphs.register(item)

            self.graphs.graph_all()
            project.callgraph = self.graphs.callgraph
            project.typegraph = self.graphs.typegraph
            project.usegraph = self.graphs.usegraph
            project.filegraph = self.graphs.filegraph
        else:
            # Even when graphs are disabled, we still need to populate calledby lists
            # Register all entities first (bypass meta.graph check)
            for entity_list in [
                project.types,
                project.procedures,
                project.submodprocedures,
                project.modules,
                project.submodules,
                project.programs,
                project.files,
                project.blockdata,
            ]:
                for item in entity_list:
                    # Register directly in GraphData, bypassing the meta.graph check
                    self.graphs.data.register(item)

            # Populate called_by relationships
            self.graphs._populate_called_by_relationships()
            # Populate calledby lists on procedure objects
            self.graphs._populate_calledby_lists()

            project.callgraph = ""
            project.typegraph = ""
            project.usegraph = ""
            project.filegraph = ""

        # Extract logic blocks for procedures (independent of graph generation)
        for entity_list in [
            project.procedures,
            project.submodprocedures,
        ]:
            for proc in entity_list:
                try:
                    proc.logic_blocks = proc.get_logic_blocks()
                except Exception:
                    proc.logic_blocks = None

                try:
                    proc.procedure_badges = proc.get_procedure_badges()
                except Exception:
                    proc.procedure_badges = None

        if settings.search:
            url = "" if settings.relative else settings.project_url
            self.tipue = ford.tipue_search.Tipue_Search_JSON_Generator(
                settings.output_dir, url
            )
            self.tipue.create_node(
                self.index.html, "index.html", EntitySettings(category="home")
            )
            jobs = len(self.docs) + len(self.pagetree)
            for page in (
                bar := ProgressBar(
                    "Creating search index", chain(self.docs, self.pagetree), total=jobs
                )
            ):
                bar.set_current(page.loc)
                self.tipue.create_node(page.html, page.loc, page.meta)

    def writeout(self) -> None:
        out_dir: pathlib.Path = self.data["output_dir"]
        # Remove any existing file/directory. This avoids errors coming from
        # `shutils.copytree` for Python < 3.8, where we can't explicitly ignore them
        if out_dir.is_file():
            out_dir.unlink()
        else:
            shutil.rmtree(out_dir, ignore_errors=True)

        try:
            out_dir.mkdir(USER_WRITABLE_ONLY, parents=True)
        except Exception as e:
            print(f"Error: Could not create output directory. {e.args[0]}")

        for directory in [
            "lists",
            "sourcefile",
            "type",
            "proc",
            "interface",
            "module",
            "program",
            "src",
            "blockdata",
            "namelist",
            "iofile",
        ]:
            (out_dir / directory).mkdir(USER_WRITABLE_ONLY)

        for directory in ["css", "js", "webfonts"]:
            copytree(loc / directory, out_dir / directory)

        if self.data["graph"]:
            self.graphs.output_graphs(self.njobs)
        if self.data["search"]:
            copytree(loc / "search", out_dir / "search")
            self.tipue.print_output()

        try:
            copytree(self.data["media_dir"], out_dir / "media")
        except OSError as e:
            warn(f"error copying media directory {self.data['media_dir']}, {e}")
        except KeyError:
            pass

        if "css" in self.data:
            shutil.copy(self.data["css"], out_dir / "css" / "user.css")

        shutil.copy(self.data["favicon"], out_dir / "favicon.png")

        if self.data["incl_src"]:
            for src in self.project.allfiles:
                shutil.copy(src.path, out_dir / "src" / src.name)

        if "mathjax_config" in self.data:
            mathjax_path = out_dir / "js" / "MathJax-config"
            mathjax_path.mkdir(parents=True, exist_ok=True)
            shutil.copy(
                self.data["mathjax_config"],
                mathjax_path / os.path.basename(self.data["mathjax_config"]),
            )

        items = list(
            chain(self.docs, self.lists, self.pagetree, [self.index, self.search])
        )
        for page in (bar := ProgressBar("Writing files", items)):
            bar.set_current(os.path.relpath(page.outfile))
            page.writeout()

        print(f"\nBrowse the generated documentation: file://{out_dir}/index.html")


class BasePage:
    """
    Abstract class for representation of pages in the documentation.

      data
        Dictionary containing project information (to be used when rendering)
      proj
        FortranProject object
      obj
        The object/item in the code which this page is documenting
    """

    def __init__(self, data, proj, obj=None):
        self.data = data
        self.proj = proj
        self.obj = obj
        self.meta = getattr(obj, "meta", EntitySettings())
        self.out_dir = self.data["output_dir"]
        self.page_dir = self.out_dir / "page"
        self.relative = data["relative"]
        self.project_url = (
            os.path.relpath(proj.settings.project_url, self.outfile.parent)
            if self.relative
            else proj.settings.project_url
        )

    @property
    def html(self) -> str:
        """Wrapper for only doing the rendering on request (drastically reduces memory)"""
        try:
            return self.render(self.data, self.proj, self.obj)
        except Exception as e:
            raise RuntimeError(
                f"Error rendering '{self.outfile.name}':\n"
                f'  File "{self.obj.filename}": {self.obj.obj} "{self.obj.name}"\n'
                f"    {e}"
            )

    @property
    def outfile(self) -> pathlib.Path:
        raise NotImplementedError()

    def writeout(self) -> None:
        self.outfile.write_bytes(self.html.encode("utf8"))

    @property
    def template_path(self) -> str:
        """Path to page template file (relative to 'templates/')"""
        raise NotImplementedError()

    @property
    def template(self):
        """Jinja template loaded from `template_path` with globals set"""
        return env.get_template(
            self.template_path,
            globals=dict(page_url=self.outfile, project_url=self.project_url),
        )

    def render(self, data, proj, obj):
        """
        Get the HTML for the page. This method must be overridden. Arguments
        are proj_data, project object, and item in the code which the
        page documents.
        """
        raise NotImplementedError("Should not instantiate BasePage type")


class ListTopPage(BasePage):
    @property
    def outfile(self):
        return self.out_dir / self.template_path

    def render(self, data, proj, obj):
        return self.template.render(data, project=proj, proj_docs=obj)


class IndexPage(ListTopPage):
    template_path = "index.html"


class SearchPage(ListTopPage):
    template_path = "search.html"


class ListPage(BasePage):
    @property
    def out_page(self):
        raise NotImplementedError("ListPage subclass missing 'out_page' property")

    @property
    def outfile(self):
        return self.out_dir / "lists" / self.out_page

    def render(self, data, proj, obj):
        return self.template.render(data, project=proj)


class ProcList(ListPage):
    out_page = "procedures.html"
    template_path = "proc_list.html"


class FileList(ListPage):
    out_page = "files.html"
    template_path = "file_list.html"


class ModList(ListPage):
    out_page = "modules.html"
    template_path = "mod_list.html"


class ProgList(ListPage):
    out_page = "programs.html"
    template_path = "prog_list.html"


class TypeList(ListPage):
    out_page = "types.html"
    template_path = "types_list.html"


class AbsIntList(ListPage):
    out_page = "absint.html"
    template_path = "absint_list.html"


class BlockList(ListPage):
    out_page = "blockdata.html"
    template_path = "block_list.html"


class NamelistList(ListPage):
    out_page = "namelists.html"
    template_path = "namelist_list.html"


class IOList(ListPage):
    out_page = "iofiles.html"
    template_path = "io_list.html"


class DocPage(BasePage):
    """
    Abstract class to be inherited by all pages for items in the code.
    """

    @property
    def payload_key(self):
        raise NotImplementedError("DocPage subclass missing 'payload_key'")

    @property
    def object_page(self):
        return self.obj.ident + ".html"

    @property
    def loc(self):
        return pathlib.Path(self.obj.get_dir()) / self.object_page

    @property
    def outfile(self):
        return self.out_dir / self.obj.get_dir() / self.object_page

    def render(self, data, project, object):
        try:
            return self.template.render(
                data, project=project, **{self.payload_key: object}
            )
        except jinja2.exceptions.TemplateError:
            print(f"Error rendering page '{self.outfile}'")
            raise


class FilePage(DocPage):
    template_path = "file_page.html"
    payload_key = "src"


class TypePage(DocPage):
    template_path = "type_page.html"
    payload_key = "dtype"


class AbsIntPage(DocPage):
    template_path = "nongenint_page.html"
    payload_key = "interface"


class ModulePage(DocPage):
    template_path = "mod_page.html"
    payload_key = "module"


class ProgPage(DocPage):
    template_path = "prog_page.html"
    payload_key = "program"


class BlockPage(DocPage):
    template_path = "block_page.html"
    payload_key = "blockdat"


class ProcedurePage(DocPage):
    template_path = "proc_page.html"
    payload_key = "procedure"


class GenericInterfacePage(DocPage):
    template_path = "genint_page.html"
    payload_key = "interface"


class InterfacePage(DocPage):
    template_path = "nongenint_page.html"
    payload_key = "interface"


class NamelistPage(DocPage):
    template_path = "namelist_page.html"
    payload_key = "namelist"


class IOFilePage(DocPage):
    template_path = "iofile_page.html"
    payload_key = "iofile"


def ProcPage(data, proj, obj):
    """Factory function for creating procedure or interface pages"""
    if obj.obj == "proc":
        return ProcedurePage(data, proj, obj)
    if obj.generic:
        return GenericInterfacePage(data, proj, obj)
    return InterfacePage(data, proj, obj)


class PagetreePage(BasePage):
    template_path = "info_page.html"

    @property
    def loc(self):
        return pathlib.Path("page") / self.obj.path

    @property
    def outfile(self):
        return self.page_dir / self.obj.path

    def render(self, data, proj, obj):
        return self.template.render(data, page=obj, project=proj, topnode=obj.topnode)

    def writeout(self):
        if self.obj.filename.stem == "index":
            (self.page_dir / self.obj.location).mkdir(USER_WRITABLE_ONLY, exist_ok=True)
        super(PagetreePage, self).writeout()

        from_path = self.data["page_dir"] / self.obj.location
        to_path = self.page_dir / self.obj.location

        for item in self.obj.copy_subdir:
            item_path = from_path / item
            try:
                copytree(item_path, to_path / item)
            except Exception as e:
                warn(f"could not copy directory '{item_path}'. Error: {e.args[0]}")

        for item in self.obj.files:
            item_path = from_path / item
            try:
                shutil.copy(item_path, to_path)
            except Exception as e:
                warn(f"could not copy file '{item_path}'. Error: {e.args[0]}")


def copytree(src: pathlib.Path, dst: pathlib.Path) -> None:
    """Wrapper around `shutil.copytree` that:
    a) doesn't try to set xattrs; and
    b) ensures modification time is time of current FORD run
    """
    shutil.copytree(src, dst, copy_function=shutil.copy)
    for file in dst.rglob("*"):
        file.touch()
