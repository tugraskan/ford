# -*- coding: utf-8 -*-
#
#  project.py
#  This file is part of FORD.
#
#  Copyright 2014 Christopher MacMackin <cmacmackin@gmail.com>
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
import json
import toposort
from itertools import chain, product
from typing import List, Optional, Union, Dict, Set
from pathlib import Path
from fnmatch import fnmatch

from ford.console import warn
from ford.external_project import load_external_modules, get_module_metadata
from ford.utils import ProgressBar
from ford.sourceform import (
    _find_in_list,
    FortranBase,
    FortranBlockData,
    FortranCodeUnit,
    FortranModule,
    FortranSubmodule,
    ExternalModule,
    FortranInterface,
    FortranType,
    FortranModuleProcedureImplementation,
    FortranCommon,
    ExternalFunction,
    ExternalSubroutine,
    FortranNamelist,
    ExternalType,
    ExternalInterface,
    ExternalVariable,
    FortranProcedure,
    FortranSourceFile,
    GenericSource,
    FortranProgram,
)
from ford.settings import ProjectSettings
from ford._typing import PathLike


LINK_TYPES = {
    "module": "modules",
    "submodule": "submodules",
    "extmodule": "extModules",
    "type": "types",
    "exttype": "extTypes",
    "procedure": "procedures",
    "extprocedure": "extProcedures",
    "subroutine": "procedures",
    "extsubroutine": "extProcedures",
    "function": "procedures",
    "extfunction": "extProcedures",
    "proc": "procedures",
    "extproc": "extProcedures",
    "file": "allfiles",
    "interface": "absinterfaces",
    "extinterface": "extInterfaces",
    "absinterface": "absinterfaces",
    "extabsinterface": "extInterfaces",
    "program": "programs",
    "block": "blockdata",
    "namelist": "namelists",
}


def find_all_files(settings: ProjectSettings) -> Set[Path]:
    """Returns a list of all selected files below a set of directories"""

    file_extensions = chain(
        settings.extensions,
        settings.fixed_extensions,
        settings.extra_filetypes.keys(),
    )

    # Get initial list of all files in all source directories
    src_files: Set[Path] = set()

    for src_dir, extension in product(settings.src_dir, file_extensions):
        src_files.update(Path(src_dir).glob(f"**/*.{extension}"))

    # Remove files under excluded directories
    for exclude_dir in settings.exclude_dir:
        src_files = {
            src for src in src_files if not fnmatch(str(src), f"{exclude_dir}/*")
        }

    bottom_level_dirs = [src_dir.name for src_dir in settings.src_dir]
    # First, let's check if the files are relative paths or not
    for i, exclude in enumerate(settings.exclude):
        exclude_path = Path(exclude)
        if (
            not exclude_path.is_file()
            and exclude_path.parent.name not in bottom_level_dirs
            and "*" not in exclude
        ):
            glob_exclude = f"**/{exclude}"
            warn(
                f"exclude file '{exclude}' is not relative to any source directories, all matching files will be excluded.\n"
                f"To suppress this warning please change it to '{glob_exclude}' in your settings file"
            )
            settings.exclude[i] = glob_exclude

    for exclude in settings.exclude:
        src_files = {
            src for src in src_files if not fnmatch(os.path.relpath(src), exclude)
        }

    return src_files


class Project:
    """
    An object which collects and contains all of the information about the
    project which is to be documented.
    """

    def __init__(self, settings: ProjectSettings):
        self.settings = settings
        self.name = settings.project
        self.external = settings.external
        self.topdirs = settings.src_dir
        self.extensions = settings.extensions
        self.fixed_extensions = settings.fixed_extensions
        self.extra_filetypes = settings.extra_filetypes
        self.display = settings.display
        self.encoding = settings.encoding

        self.files: List[FortranSourceFile] = []
        self.modules: List[FortranModule] = []
        self.programs: List[FortranProgram] = []
        self.procedures: List[FortranProcedure] = []
        self.absinterfaces: List[FortranInterface] = []
        self.types: List[FortranType] = []
        self.submodules: List[FortranSubmodule] = []
        self.submodprocedures: List[FortranModuleProcedureImplementation] = []
        self.extra_files: List[GenericSource] = []
        self.blockdata: List[FortranBlockData] = []
        self.common: Dict[str, FortranCommon] = {}
        self.extModules: List[ExternalModule] = []
        self.extProcedures: List[Union[ExternalSubroutine, ExternalFunction]] = []
        self.extInterfaces: List[ExternalInterface] = []
        self.extTypes: List[ExternalType] = []
        self.extVariables: List[ExternalVariable] = []
        self.namelists: List[FortranNamelist] = []

        # Get all files within topdir, recursively

        for filename in (
            progress := ProgressBar("Parsing files", find_all_files(settings))
        ):
            relative_path = os.path.relpath(filename)
            progress.set_current(relative_path)

            extension = str(filename.suffix)[1:]  # Don't include the initial '.'
            fortran_extensions = self.extensions + self.fixed_extensions
            try:
                if extension in fortran_extensions:
                    self._fortran_file(extension, filename, settings)
                elif extension in self.extra_filetypes:
                    self.extra_files.append(GenericSource(filename, settings))
            except Exception as e:
                if not settings.dbg:
                    raise e

                warn(
                    f"Error parsing {relative_path}.\n\t{e.args if len(e.args) == 0 else e.args[0]}"
                )
                continue

    def _fortran_file(
        self, extension: str, filename: PathLike, settings: ProjectSettings
    ):
        if extension in settings.fpp_extensions:
            preprocessor = settings.preprocessor.split()
        else:
            preprocessor = None

        new_file = FortranSourceFile(
            str(filename),
            settings,
            preprocessor,
            extension in self.fixed_extensions,
            incl_src=settings.incl_src,
            encoding=self.encoding,
        )
        def namelist_check(entity):
            self.namelists.extend(getattr(entity, "namelists", []))

        for module in new_file.modules:
            self.modules.append(module)
            for routine in module.routines:
                namelist_check(routine)

        for submod in new_file.submodules:
            self.submodules.append(submod)
            for routine in submod.routines:
                namelist_check(routine)

        for function in new_file.functions:
            function.visible = True
            self.procedures.append(function)
            namelist_check(function)

        for subroutine in new_file.subroutines:
            subroutine.visible = True
            self.procedures.append(subroutine)
            namelist_check(subroutine)
            self.extract_non_fortran_and_non_integers(subroutine)
            self.build_stype_dictionary(subroutine)


        for program in new_file.programs:
            program.visible = True
            self.programs.append(program)
            namelist_check(program)
            for routine in program.routines:
                namelist_check(routine)

        for block in new_file.blockdata:
            self.blockdata.append(block)

        self.files.append(new_file)

    def extract_non_fortran_and_non_integers(self, subroutine):
        """
        Extracts items that are neither Fortran keywords, integers, symbols, nor self-defined variables.

        Parameters
        ----------
        subroutine : object
            An object containing `other_results`, `variables`, and `member_access_results`.

        Updates
        -------
        subroutine.member_access_results : list
            Appends filtered items that pass the criteria.

        Returns
        -------
        set
            A filtered set of items that are neither Fortran keywords, integers, symbols, nor self-defined variables.
        """

        # Extract the names of subroutine variables
        subroutine_variable_names = {var.name for var in subroutine.variables}

        # Combine all Fortran keywords dynamically using set union
        all_fortran_keywords = (
                subroutine.fortran_control |
                subroutine.fortran_operators |
                subroutine.fortran_intrinsics |
                subroutine.fortran_reserved |
                subroutine.fortran_custom |
                subroutine.symbols |
                subroutine.fortran_io |
                subroutine_variable_names

        )

        # Convert `other_results` to a set for efficient processing
        items = {item.strip().strip("'\"") for item in subroutine.other_results}

        # Initialize a filtered set for deduplication
        filtered_items = set()

        for item in items:
            # Skip empty strings, Fortran keywords, integers, symbols, and subroutine variables
            if (
                    item
                    and item not in all_fortran_keywords
                    and not subroutine.NUMBER_RE.match(item)
            ):
                # Add to filtered set if not already in member_access_results
                if item not in subroutine.member_access_results:
                    subroutine.member_access_results.append(item)
                    filtered_items.add(item)

        return filtered_items


    def build_stype_dictionary(self, subroutine):
        """
        Builds a nested dictionary representing types and their attributes from a list of variable paths,
        without creating empty dictionaries.

        Parameters
        ----------
        subroutine : object
            An object containing `member_access_results` (a list of variable paths) and `type_results` (a list to be updated).

        Updates
        -------
        subroutine.type_results : list
            Appends the final nested dictionary representing the types and their attributes.

        Returns
        -------
        dict
            A nested dictionary representing the types and their attributes.
        """
        type_dict = {}

        # Check if member_access_results is a valid list
        if not isinstance(subroutine.member_access_results, list):
            raise TypeError("Expected 'member_access_results' to be a list.")

        for var in subroutine.member_access_results:
            parts = var.split('%')  # Split by '%' to get nested type parts
            current = type_dict

            for part in parts:
                # Skip empty parts to avoid creating unnecessary empty dictionaries
                if part:
                    current = current.setdefault(part, {})

        # Update the subroutine with the final type dictionary
        subroutine.type_results = type_dict

        return type_dict  # Optional, if you want to return the dictionary

    def _clean_fvar_recursive(self, data):
        """
        Recursively process the data structure for JSON serialization.

        Since your fvar structure already contains only simple keys (such as
        'name', 'vartype', 'initial', 'filename', 'doc_list', and 'variables'),
        this function recurses over dictionaries and lists and returns the same structure.

        Parameters:
          data: a dict, list, or primitive value.

        Returns:
          data with all nested values processed.
        """
        if isinstance(data, dict):
            new_data = {}
            for key, value in data.items():
                new_data[key] = self._clean_fvar_recursive(value)
            return new_data
        elif isinstance(data, list):
            return [self._clean_fvar_recursive(item) for item in data]
        else:
            return data

    def procedures_fvar_to_json(self, procedures):
        """
        Iterate over the provided list of procedures, convert each procedure's fvar
        structure (a custom nested dictionary) into a JSON string, and store that string
        in the procedure's pjson attribute.

        Each procedure is expected to have a 'name' attribute and an 'fvar' attribute.
        After processing, procedure.pjson will contain that procedure's JSON.

        Parameters:
          procedures (list): A list of procedure objects.
        """
        for procedure in procedures:
            # Process the fvar structure if available, otherwise use an empty dictionary.
            if hasattr(procedure, 'fvar'):
                cleaned = self._clean_fvar_recursive(procedure.fvar)
            else:
                cleaned = {}

            # Store the JSON string in the procedure's pjson attribute.
            procedure.pjson = json.dumps(cleaned, indent=2)

    def io_xwalk(self, procedures):
        master_list = []

        for proc in procedures:
            if not hasattr(proc, "io_tracker"):
                continue

            proc.io_tracker.finalize()

            # completed is now a dict: unit → [IoSession, ...]
            for unit, sessions in proc.io_tracker.completed.items():
                for sess in sessions:
                    master_list.append({
                        "used_in": proc.name,
                        "unit": unit,
                        "file": sess.file,
                        "operations": [
                            {"kind": kind, "raw_line": raw.strip()}
                            for kind, raw in sess.operations
                        ],
                    })

        return json.dumps(master_list, indent=2)

    def _find_variable_info(self, procedure, var_ref):
        """
        Given a Fortran variable reference (e.g., 'in_link%aqu_cha'),
        walk through procedure.fvar to find the matching dictionary that includes keys like
        'name', 'vartype', 'filename', 'initial', and 'doc_list'.

        Returns the variable's dictionary or None if not found.
        """
        # If there's no fvar or it's not a dict, we can't proceed
        if not hasattr(procedure, 'fvar') or not isinstance(procedure.fvar, dict):
            return None

        # Split the reference by '%'
        parts = var_ref.split('%')
        if not parts:
            return None

        # Start at the top-level fvar
        current_dict = procedure.fvar
        for i, part in enumerate(parts):
            if part in current_dict:
                # If this is not the last part, move into its 'variables' sub-dict
                if i < len(parts) - 1:
                    # Move inside the nested structure
                    next_dict = current_dict[part].get('variables', None)
                    if not next_dict:
                        return None
                    current_dict = next_dict
                else:
                    # Last part; we've found the final variable dict
                    return current_dict[part]
            else:
                # No match
                return None
        # If we exit the loop without returning, no match was found
        return None
    def get_procedures(self):
        procedures = []

        for procedure in self.procedures:
            # If the procedure does not have a module (assuming `procedure.module` is a Boolean or exists)
            print('!!!! ' + procedure.name)
            if procedure.parobj == 'sourcefile':
                procedures.append(procedure)


        # Sort the procedures (assuming you want to sort by procedure name)
        procedures.sort(key=lambda x: x.name)

        return procedures   # Return the list of non-procedure variables


    def cross_walk_type_dicts(self, procedures):
        for procedure in procedures:
            print('%%%% ' + procedure.name)
            for key, value in procedure.type_results.items():
                if key in procedure.all_vars:
                    procedure.fvar[key] = {
                        'name': procedure.all_vars[key].name,
                        'vartype': procedure.all_vars[key].vartype,
                        'initial': procedure.all_vars[key].initial,
                        'filename': procedure.all_vars[key].filename,
                        'doc_list': procedure.all_vars[key].doc_list,
                        'variables': {},
                        'original': procedure.all_vars[key]
                    }
                    if value:
                        print(f"$$$$ {key} nested structure")
                        self.r_check(procedure.fvar[key], value)
                        # Remove original from the top-level branch after recursion.
                        procedure.fvar[key].pop('original', None)
                        print('check 1')
                    else:
                        procedure.fvar[key].pop('original', None)
                        print('check 2')
                else:
                    procedure.var_ug_na.append(key)
                    print('check 3')
            print("wowza")

    def r_check(self, parent_rep, value):
        """
        Recursive function to check nested keys/values and add them to the parent's custom representation.

        The custom representation is a dictionary that includes:
          - 'name', 'vartype', 'initial', 'filename', 'doc_list', 'variables'
          - 'original' is stored temporarily only for recursion.

        After processing each branch, the 'original' key is removed.
        """
        for nested_key, nested_values in value.items():
            parent_orig = parent_rep.get('original')
            if not parent_orig:
                print("Parent original object not found; cannot continue recursion.")
                continue

            # Find the matching variable in parent's proto[0].variables by name.
            found_var = next(
                (var for var in parent_orig.proto[0].variables if var.name == nested_key),
                None
            )

            if found_var is not None:
                # Build a custom representation for the nested variable.
                new_rep = {
                    'name': found_var.name,
                    'vartype': found_var.vartype,
                    'initial': found_var.initial,
                    # 'filename': found_var.filename,  # If you want to include filename, uncomment it.
                    'doc_list': found_var.doc_list,
                    'variables': {},
                    'original': found_var  # temporary; used only for recursion.
                }
                parent_rep['variables'][nested_key] = new_rep

                if nested_values:
                    print(f"Recursively checking nested structure for key: {nested_key}")
                    self.r_check(new_rep, nested_values)
                    print("Nested check complete.")
                else:
                    print(f"No further nested values for key: {nested_key}")

                # Remove the 'original' key from this branch now that recursion is complete.
                new_rep.pop('original', None)
            else:
                print(f"Key '{nested_key}' not found in parent's proto variables by name.")

    @property
    def allfiles(self):
        """Instead of duplicating files, it is much more efficient to create the itterator on the fly"""
        for f in self.files:
            yield f
        for f in self.extra_files:
            yield f

    def __str__(self):
        return self.name

    def correlate(self):
        """
        Associates various constructs with each other.
        """

        self.extModules.extend(
            [
                ExternalModule(name, url)
                for name, url in self.settings.extra_mods.items()
            ]
        )

        # load external FORD FortranModules
        load_external_modules(self)

        # Match USE statements up with the module objects or links
        for entity in chain(
            self.modules,
            self.procedures,
            self.programs,
            self.submodules,
            self.blockdata,
        ):
            find_used_modules(entity, self.modules, self.submodules, self.extModules)

        def get_deps(item):
            uselist = [m[0] for m in item.uses]
            interfaceprocs = []
            for intr in getattr(item, "interfaces", []):
                if hasattr(intr, "procedure"):
                    interfaceprocs.append(intr.procedure)
            for procedure in chain(item.routines, interfaceprocs):
                uselist.extend(get_deps(procedure))
            return uselist

        def filter_modules(entity) -> List[FortranModule]:
            """Return a list of `FortranModule` from the dependencies of `entity`"""
            return [dep for dep in get_deps(entity) if type(dep) is FortranModule]

        # Get the order to process other correlations with
        for mod in self.modules:
            mod.deplist = filter_modules(mod)

        for mod in self.submodules:
            if type(mod.ancestor_module) is not FortranModule:
                warn(
                    f"Could not identify ancestor module ('{mod.ancestor_module}') of submodule '{mod.name}' "
                    f"(in '{mod.filename}').\n"
                    f"         This is usually because Ford hasn't found '{mod.ancestor_module}' "
                    "in any of the source directories.\n"
                )
                continue

            if not isinstance(mod.parent_submodule, (FortranSubmodule, type(None))):
                warn(
                    f"Could not identify parent submodule ('{mod.parent_submodule}') of submodule '{mod.name}' "
                    f"(in '{mod.filename}').\n"
                    f"         This is usually because Ford hasn't found '{mod.parent_submodule}' "
                    "in any of the source directories.\n"
                )

            mod.deplist = [
                mod.parent_submodule or mod.ancestor_module
            ] + filter_modules(mod)

        deplist = {
            module: set(module.deplist)
            for module in chain(self.modules, self.submodules)
        }

        # Get dependencies for programs and top-level procedures as well,
        # if dependency graphs are to be produced
        if self.settings.graph:
            for entity in chain(self.procedures, self.programs, self.blockdata):
                entity.deplist = set(filter_modules(entity))

        ranklist = toposort.toposort_flatten(deplist)
        for proc in self.procedures:
            if proc.parobj == "sourcefile":
                ranklist.append(proc)
        ranklist.extend(self.programs)
        ranklist.extend(self.blockdata)

        # Perform remaining correlations for the project
        for container in ranklist:
            if not isinstance(container, str):
                container.correlate(self)
        for container in ranklist:
            if not isinstance(container, str):
                container.prune()

        # Mapping of various entity containers in code units to the
        # corresponding container in the project
        CONTAINERS = {
            "functions": "procedures",
            "subroutines": "procedures",
            "interfaces": "procedures",
            "absinterfaces": "absinterfaces",
            "types": "types",
            "modfunctions": "submodprocedures",
            "modsubroutines": "submodprocedures",
            "modprocedures": "submodprocedures",
        }

        # Gather all the entity containers from each code unit in each
        # file into the corresponding project container
        for sfile in self.files:
            for code_unit in chain(
                sfile.modules, sfile.submodules, sfile.programs, sfile.blockdata
            ):
                for entity_kind, container in CONTAINERS.items():
                    entities = getattr(code_unit, entity_kind, [])
                    getattr(self, container).extend(entities)

        def sum_lines(*argv, **kwargs):
            """Wrapper for minimizing memory consumption"""
            routine = kwargs.get("func", "num_lines")
            n = 0
            for arg in argv:
                for item in arg:
                    n += getattr(item, routine)
            return n

        self.mod_lines = sum_lines(self.modules, self.submodules)
        self.proc_lines = sum_lines(self.procedures)
        self.file_lines = sum_lines(self.files)
        self.type_lines = sum_lines(self.types)
        self.type_lines_all = sum_lines(self.types, func="num_lines_all")
        self.absint_lines = sum_lines(self.absinterfaces)
        self.prog_lines = sum_lines(self.programs)
        self.block_lines = sum_lines(self.blockdata)

        # Store module metadata
        #self.module_metadata = [get_module_metadata(module) for module in self.modules] # do this in xwalk  instead or is a json still ultimately needed?
        #self.xwalk_type_dicts = [self.cross_walk_type_dicts(procedures) for procedures in self.procedures] #all_vars exists, still need a xwalk but do it after correlating


    def markdown(self, md):
        """
        Process the documentation with Markdown to produce HTML.
        """
        if self.settings.warn:
            print()

        items = []
        for src in self.allfiles:
            items.extend(src.markdownable_items)

        for item in (bar := ProgressBar("Processing comments", items)):
            bar.set_current(item.name)
            item.markdown(md)

    def find(
        self,
        name: str,
        entity: Optional[str] = None,
        child_name: Optional[str] = None,
        child_entity: Optional[str] = None,
    ) -> Optional[FortranBase]:
        """Find an entity somewhere in the project

        Parameters
        ----------
        name : str
            Name of entity to look up
        entity : Optional[str]
            The class of entity (module, program, and so on)
        child_name : Optional[str]
            Name of a child of ``name`` to look up
        child_entity : Optional[str]
            The class of ``child_name``

        Returns
        -------
        Optional[FortranBase]
            Returns `None` if ``name`` not found

        """

        item = None

        if entity is not None:
            try:
                collection = getattr(self, LINK_TYPES[entity.lower()])
            except KeyError:
                raise ValueError(f"Unknown class of entity {entity!r}")
        else:
            collection = chain(
                *(getattr(self, collection) for collection in LINK_TYPES.values())
            )

        item = _find_in_list(collection, name)

        if child_name is None or item is None:
            return item

        return item.find_child(child_name, child_entity)


def find_used_modules(
    entity: FortranCodeUnit,
    modules: List[FortranModule],
    submodules: List[FortranSubmodule],
    external_modules: List[ExternalModule],
) -> None:
    """Find the module objects (or links to intrinsic/external
    module) for all of the ``USED``d names in ``entity``

    Parameters
    ----------
    entity
        A program, module, submodule or procedure
    modules
        Known Fortran modules
    intrinsic_modules
        Known intrinsic Fortran modules
    submodules
        Known Fortran submodules
    external_modules
        Known external Fortran modules

    """
    # Find the modules that this entity uses
    for dependency in entity.uses:
        # Can safely skip if already known
        if isinstance(dependency[0], FortranModule):
            continue
        dependency_name = dependency[0].lower()
        for candidate in chain(modules, external_modules):
            if dependency_name == candidate.name.lower():
                dependency[0] = candidate

                """
                matches = []
                for result in entity.type_results:  # Iterate over each list item
                    if isinstance(result, dict):  # Process only if it's a dictionary
                        for key, value in result.items():
                            # Check if the key matches any candidate variable name
                            if any(var.name == key for var in candidate.variables):
                                matches.append(key)

                            # If the value is a nested dictionary, search deeper
                            if isinstance(value, dict):
                                matches.extend(search_type_results_in_candidate(value, candidate.variables))

                print(matches)


                # Check if dependency variables are used in the entity's subroutines
                #if hasattr(candidate, "variables"):
                    #module_vars = {var.name for var in candidate.variables}
                    #for var in candidate.variables:
                        #if var.name in entity.type_results:
                            #print(f"Found variable {var.name} in {entity.name}")


                """

                break
    # Find the ancestor of this submodule (if entity is one)
    if hasattr(entity, "parent_submodule") and entity.parent_submodule:
        parent_submodule_name = entity.parent_submodule.lower()
        for submod in submodules:
            if parent_submodule_name == submod.name.lower():
                entity.parent_submodule = submod
                break

    if hasattr(entity, "ancestor_module"):
        ancestor_module_name = entity.ancestor_module.lower()
        for mod in modules:
            if ancestor_module_name == mod.name.lower():
                entity.ancestor_module = mod
                break

    # Find the modules that this entity's procedures use
    for procedure in entity.routines:
        find_used_modules(procedure, modules, submodules, external_modules)

    # Find the modules that this entity's interfaces' procedures use
    for interface in getattr(entity, "interfaces", []):
        if hasattr(interface, "procedure"):
            find_used_modules(
                interface.procedure, modules, submodules, external_modules
            )
        else:
            for procedure in interface.routines:
                find_used_modules(procedure, modules, submodules, external_modules)
