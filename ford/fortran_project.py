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
            #self.build_mtype_dictionary(module) # is this really necessary?

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
            self.build_stype_set(subroutine)

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

    def build_stype_set(self, subroutine):
        """
        Builds a set of key-value pairs representing the types and their attributes from a list of variable paths.

        Parameters
        ----------
        subroutine : object
            An object containing `member_access_results` and `type_results`.

        Updates
        -------
        subroutine.type_results : set
            Updates the type_results attribute to hold a set of key-value pairs representing the types and their attributes.

        Returns
        -------
        set
            A set of key-value pairs representing the types and their attributes.
        """
        type_set = set()

        for var in subroutine.member_access_results:
            parts = var.split('%')  # Split by '%'
            # Create a tuple of the split parts
            path_tuple = tuple(parts)
            type_set.add(path_tuple)  # Add the tuple to the set

        # Update subroutine.type_results with the final set
        subroutine.type_results2 = type_set

        return type_set



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


    def build_mtype_dictionary (self, module):
        """
        Extracts metadata for variables and derived types in the module and returns it as a nested dictionary.
        """

        # Initialize the metadata dictionary
        type_dict = {}

        # Process variables in the module:
        for var in module.variables():
            # Extract the derived type if it's a derived type
            derived_type_match = re.search(r"type\\([a-zA-Z_][a-zA-Z0-9_]*)\.html", var.full_type)
            derived_type = derived_type_match.group(1) if derived_type_match else var.full_type

            # Create nested structure for the variable type if not present
            if derived_type not in type_dict:
                type_dict[derived_type] = {}

            type_dict[derived_type][var_name] = {
                "initial": var.initial,
                "doc": var.doc_list,
            }


        # Process derived types
        for type_name, dtype in module.all_types.items():
            # Create an entry for the derived type if not already present
            if type_name not in metadata:
                type_dict[type_name] = {}

            # Iterate through variables within the derived type
            for variable in dtype.variables:
                derived_type_match = re.search(r"type\\([a-zA-Z_][a-zA-Z0-9_]*)\.html", variable.full_type)
                derived_type = derived_type_match.group(1) if derived_type_match else variable.full_type

                # Ensure the nested dictionary structure
                if derived_type not in type_dict:
                    type_dict[derived_type] = {}

                type_dict[derived_type][variable.name] = {
                    "initial": getattr(variable, "initial", None),
                    "doc": getattr(variable, "doc_list", []),
                }


        return type_dict

    import json


    def cross_walk_type_dicts(self):
        """Main function to crosswalk type_results and all_vars to generate JSON output."""
        for procedure in self.procedures:
            # If the procedure does not have a module (assuming `procedure.module` is a Boolean or exists)
            if not getattr(procedure, 'module', False):
                print('*****' + procedure.name)

                for key, value in procedure.type_results.items():
                    if key in procedure.all_vars:
                        print (f"$$$$ {key} Found in all_vars")
                        mvar = procedure.all_vars[key]
                        procedure.var_ug[mvar.name] = mvar

                        # Recursively check for nested structures (if needed)
                        if value:
                            self.recursive_check(key, value, procedure.var_ug, mvar)
                        else:
                            print (f"$$$$ {key} No nested structure")
                            #self.recursive_check(key, value, procedure.var_ug, mvar)
                    else:
                        print(f" $$$$ {key} Not Found in all_vars")
                        # add missing variables to the procedure_json DICT
                        procedure.var_ug[key] = None

            else:
                print(f"Skipping procedure {procedure.name} because it has a module.")

    def recursive_check(self, key, value, var_ug, mvar):
        """Recursive function to check for nested keys and values and add them to the JSON structure."""
        print("dafuq")
        print(f"Checking if {key} is in 1proto variables...")
        print(f"Checking if {value} is in 1proto variables...")
        new_v = []
        # Handle the case when json is a dictionary
        if isinstance(var_ug, dict):
            for nested_key, nested_values in value.items():
                print(f"Checking if {nested_key} is in proto variables...")
                # Assuming proto is a list with the first element being the correct object
                proto_vars_dict = {pvar.name: pvar for pvar in mvar.proto[0].variables if hasattr(pvar, 'name')}
                pvar = mvar
                self.recursive_check2(nested_key, nested_values, pvar, proto_vars_dict, new_v)
            var_ug[key].proto[0].variables = new_v

        # Handle the case when json is not a dictionary (assuming it's a class or object with a proto attribute)
        else:
            for nested_key, nested_values in value.items():
                print(f"Checking if {nested_key} is in proto variables...")
                proto_vars_dict = {pvar.name: pvar for pvar in mvar[0].variables if hasattr(pvar, 'name')}
                pvar = mvar  # Assuming pvar is json
                self.recursive_check2(nested_key, nested_values, pvar, proto_vars_dict, new_v,)
            var_ug.proto[0].variables = new_v

    def recursive_check2(self, k, v, var, vars_dict, new_v):
        """Helper function to handle nested keys and process them."""
        if k in vars_dict:
            print(f"Keeping {k}")
            var = vars_dict[k]
            new_v.append(var)

            if v and isinstance(v, dict) and bool(v):
                print(f"Recursing into {k} with value {v}")
                self.recursive_check(k, v, vars_dict, var)  # Recurse into the nested values
            else:
                print(f"{k} is a leaf node")
                var.proto = None
        else:
            print(f"{k} Not Found in proto_vars")
            new_v.append(k)

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
