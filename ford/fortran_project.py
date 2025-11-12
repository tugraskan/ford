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

import re
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
    FortranIOFile,
    ExternalType,
    ExternalInterface,
    ExternalVariable,
    FortranProcedure,
    FortranSourceFile,
    GenericSource,
    FortranProgram,
    FortranSubroutine,  # ← add this
    FortranFunction,
)
from ford.settings import ProjectSettings
from ford._typing import PathLike
import logging as log


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
        self.iofiles: List[FortranIOFile] = []

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

    def procedures_call_to_json(
        self, procedures: List[FortranProcedure], out_dir: Optional[str] = None
    ) -> None:
        """
        Export procedure call relationships and call chains to JSON files.

        For each procedure, this method:
        - Writes <proc>.json with all calls (name + line_number)
        - Writes <proc>_subs.json with only the subroutine calls
        - Creates a master subroutine_calls.json in the parent 'json_outputs' directory

        Args:
            procedures: List of procedures to process
            out_dir: Output directory path. Defaults to ./json_outputs/calls_json
        """
        # Set up per-procedure directory
        calls_dir = out_dir or os.path.join(os.getcwd(), "json_outputs", "calls_json")
        os.makedirs(calls_dir, exist_ok=True)

        # Prepare master dict for subroutine calls
        master_subs: dict[str, list[dict]] = {}

        for proc in procedures:
            # Gather all calls from proc.call_records (chain, line_no)
            all_calls = [
                {"name": chain[-1], "line_number": ln}
                for chain, ln in getattr(proc, "call_records", [])
            ]

            # Filter only those whose name appears in proc.calls (subroutines)
            sub_calls = [c for c in all_calls if c["name"] in proc.calls]

            # Write full calls JSON
            full_path = os.path.join(calls_dir, f"{proc.name}.json")
            full_payload = {
                "file": proc.filename,
                "line_number": getattr(proc, "line_number", None),
                "calls": all_calls,
            }
            try:
                with open(full_path, "w") as fp:
                    json.dump(full_payload, fp, indent=2)
                log.info("Wrote full call graph for %s → %s", proc.name, full_path)
            except IOError as e:
                log.error("Failed to write full call graph for %s: %s", proc.name, e)

            # --- write subroutine‐only JSON ---
            sub_path = os.path.join(calls_dir, f"{proc.name}_subs.json")
            sub_payload = {
                "file": proc.filename,
                "line_number": getattr(proc, "line_number", None),
                "subroutines": sub_calls,
            }
            try:
                with open(sub_path, "w") as sp:
                    json.dump(sub_payload, sp, indent=2)
                log.info("Wrote subroutine-only graph for %s → %s", proc.name, sub_path)
            except IOError as e:
                log.error(
                    "Failed to write subroutine-only graph for %s: %s", proc.name, e
                )

            # collect for master if any subroutine calls exist
            if sub_calls:
                master_subs[proc.name] = sub_calls

        # 3) write master subroutine_calls.json in json_outputs
        master_dir = os.path.dirname(calls_dir)
        os.makedirs(master_dir, exist_ok=True)
        master_path = os.path.join(master_dir, "subroutine_calls.json")
        try:
            with open(master_path, "w") as mf:
                json.dump(master_subs, mf, indent=2)
            log.info("Wrote master subroutine-call graph → %s", master_path)
        except IOError as e:
            log.error("Failed to write master subroutine-call graph: %s", e)

        return master_subs

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
            subroutine.fortran_control
            | subroutine.fortran_operators
            | subroutine.fortran_intrinsics
            | subroutine.fortran_reserved
            | subroutine.fortran_custom
            | subroutine.symbols
            | subroutine.fortran_io
            | subroutine_variable_names
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

        # copy variables to var_ug_local
        subroutine.var_ug_local = subroutine.variables

        # Check if member_access_results is a valid list
        if not isinstance(subroutine.member_access_results, list):
            raise TypeError("Expected 'member_access_results' to be a list.")

        for var in subroutine.member_access_results:
            parts = var.split("%")  # Split by '%' to get nested type parts
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

    def procedures_fvar_to_json(
        self, procedures: List[FortranProcedure], out_dir: Optional[str] = None
    ) -> None:
        """
        Export procedure variable information and local variables to JSON files.

        For each procedure, this method:
        - Cleans up its fvar dictionary
        - Collects local variables
        - Exports both to a JSON file if non-empty

        Args:
            procedures: List of procedures to process
            out_dir: Output directory path. Defaults to ./json_outputs/fvar_json
        """
        # Prepare output directory
        if out_dir is None:
            out_dir = os.path.join(os.getcwd(), "json_outputs", "fvar_json")
        os.makedirs(out_dir, exist_ok=True)

        for proc in procedures:
            # Clean the existing fvar dict
            cleaned = {}
            if hasattr(proc, "fvar"):
                cleaned = self._clean_fvar_recursive(proc.fvar) or {}

            # Build the local-variable list
            local_list = []
            if hasattr(proc, "var_ug_local"):
                for var in proc.var_ug_local:
                    local_list.append(
                        {
                            "name": var.name,
                            "vartype": getattr(
                                var, "vartype", getattr(var, "type", None)
                            ),
                            "initial": getattr(var, "initial", None),
                            "doc_list": getattr(var, "doc_list", []),
                            "line_number": getattr(var, "line_number", None),
                        }
                    )

            # 4. only write JSON if there’s any fvar or any locals
            if cleaned or local_list:
                payload = {}
                if cleaned:
                    payload["fvar"] = cleaned
                if local_list:
                    payload["locals"] = local_list

                # Add top-level line number of the procedure
                payload["line_number"] = getattr(proc, "line_number", None)

                # Write to file
                fname = os.path.join(out_dir, f"{proc.name}.json")
                try:
                    with open(fname, "w") as fp:
                        json.dump(payload, fp, indent=2)
                    log.info("Wrote JSON for %s → %s", proc.name, fname)
                    proc.pjson = json.dumps(payload, indent=2)
                except IOError as e:
                    log.error("Failed to write JSON for %s: %s", proc.name, e)
            else:
                log.debug("No fvar or locals for %s; skipping JSON", proc.name)

    def _find_variable_info(self, procedure, var_ref):
        """
        Given a Fortran variable reference (e.g., 'in_link%aqu_cha'),
        walk through procedure.fvar to find the matching dictionary that includes keys like
        'name', 'vartype', 'filename', 'initial', and 'doc_list'.

        Returns the variable's dictionary or None if not found.
        """
        # If there's no fvar or it's not a dict, we can't proceed
        if not hasattr(procedure, "fvar") or not isinstance(procedure.fvar, dict):
            return None

        # Split the reference by '%'
        parts = var_ref.split("%")
        if not parts:
            return None

        # Start at the top-level fvar
        current_dict = procedure.fvar
        for i, part in enumerate(parts):
            if part in current_dict:
                # If this is not the last part, move into its 'variables' sub-dict
                if i < len(parts) - 1:
                    # Move inside the nested structure
                    next_dict = current_dict[part].get("variables", None)
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

    def get_procedures(self) -> List[FortranProcedure]:
        """
        Extract procedures that are defined at the source file level.

        Returns:
            List of procedures that have 'sourcefile' as their parent object,
            sorted alphabetically by name.
        """
        procedures = [
            procedure
            for procedure in self.procedures
            if procedure.parobj == "sourcefile"
        ]

        # Sort procedures alphabetically by name
        procedures.sort(key=lambda x: x.name)

        return procedures

    def cross_walk_type_dicts(self, procedures: List[FortranProcedure]) -> None:
        """
        Cross-reference type dictionaries with variable definitions to create
        comprehensive variable metadata for procedures.

        This method populates the fvar attribute of each procedure with detailed
        variable information including type, documentation, and nested structures.

        Args:
            procedures: List of procedures to process
        """
        for procedure in procedures:
            for key, value in procedure.type_results.items():
                if key in procedure.all_vars:
                    procedure.fvar[key] = {
                        "name": procedure.all_vars[key].name,
                        "vartype": procedure.all_vars[key].vartype,
                        "initial": procedure.all_vars[key].initial,
                        "filename": procedure.all_vars[key].filename,
                        "doc_list": procedure.all_vars[key].doc_list,
                        "variables": {},
                        "original": procedure.all_vars[key],
                    }
                    if value:
                        # Handle nested structure
                        self.r_check(procedure.fvar[key], value)
                        # Remove original from the top-level branch after recursion
                        procedure.fvar[key].pop("original", None)
                    else:
                        procedure.fvar[key].pop("original", None)
                else:
                    procedure.var_ug_na.append(key)

    def r_check(self, parent_rep, value):
        """
        Recursive function to check nested keys/values and add them to the parent's custom representation.

        The custom representation is a dictionary that includes:
          - 'name', 'vartype', 'initial', 'filename', 'doc_list', 'variables'
          - 'original' is stored temporarily only for recursion.

                log.error("Parent original object not found; cannot continue recursion.")
        """
        for nested_key, nested_values in value.items():
            parent_orig = parent_rep.get("original")
            if not parent_orig:
                log.error(
                    "Parent original object not found; cannot continue recursion."
                )
                continue
            # Find the matching variable in parent's proto[0].variables by name.
            found_var = next(
                (
                    var
                    for var in parent_orig.proto[0].variables
                    if var.name == nested_key
                ),
                None,
            )

            if found_var is not None:
                # Build a custom representation for the nested variable.
                new_rep = {
                    "name": found_var.name,
                    "vartype": found_var.vartype,
                    "initial": found_var.initial,
                    # 'filename': found_var.filename,  # If you want to include filename, uncomment it.
                    "doc_list": found_var.doc_list,
                    "variables": {},
                    "original": found_var,  # temporary; used only for recursion.
                }
                parent_rep["variables"][nested_key] = new_rep

                if nested_values:
                    self.r_check(new_rep, nested_values)

                # Remove the 'original' key from this branch now that recursion is complete.
                new_rep.pop("original", None)
            else:
                log.warning(
                    "Key '%s' not found in parent's proto variables by name", nested_key
                )

    def procedures_io_to_json(
        self, procedures: List[FortranProcedure], out_dir: Optional[str] = None
    ) -> None:
        """
        Export I/O operations and timeline analysis for procedures to JSON files.

        For each procedure, this method:
        - Finalizes its io_tracker
        - Generates summarize_file_io() result including summary and timeline
        - Adds line number information
        - Writes to individual .io.json files

        Also creates a master io_summary.json file.

        Args:
            procedures: List of procedures to process
            out_dir: Output directory path. Defaults to ./json_outputs/io_summary
        """
        out_dir = out_dir or os.path.join(os.getcwd(), "json_outputs", "io_summary")
        os.makedirs(out_dir, exist_ok=True)

        project_summary = {}

        for proc in procedures:
            tracker = proc.io_tracker
            tracker.finalize()

            result = tracker.summarize_file_io()
            if not result:
                continue

            # ——— New: add the procedure's line number
            result["line_number"] = getattr(proc, "line_number", None)

            # ——— Optional: if your result has a 'timeline' list of I/O events,
            #             and each event has its own 'lineno' attribute, copy it in:
            if "timeline" in result:
                for event in result["timeline"]:
                    # adjust 'lineno' to match whatever your tracker uses
                    event["line_number"] = event.get("lineno", None)

            project_summary[proc.name] = result

            # Save individual file
            path = os.path.join(out_dir, f"{proc.name}.io.json")
            try:
                with open(path, "w") as f:
                    json.dump(result, f, indent=2)
                log.info("Wrote I/O summary for %s → %s", proc.name, path)
            except IOError as e:
                log.error("Failed to write I/O summary for %s: %s", proc.name, e)

        # Save master summary
        master_path = os.path.join(out_dir, "io_summary.json")
        try:
            with open(master_path, "w") as f:
                json.dump(project_summary, f, indent=2)
            log.info("Wrote master I/O summary → %s", master_path)
        except IOError as e:
            log.error("Failed to write master I/O summary: %s", e)

        return project_summary

    def procedures_input_analysis_to_json(
        self, procedures: List[FortranProcedure], out_dir: Optional[str] = None
    ) -> None:
        """
        Export detailed input file analysis for procedures to JSON files.

        For each procedure that reads input files, this method analyzes:
        - Subroutine name that reads the input
        - Unit number used for file operations
        - Whether files are opened via assigned variables vs hardcoded strings
        - Read structure of the file (title, header, data)
        - What data is read and to what data types/variables

        Args:
            procedures: List of procedures to process
            out_dir: Output directory path. Defaults to ./json_outputs/input_analysis
        """
        out_dir = out_dir or os.path.join(os.getcwd(), "json_outputs", "input_analysis")
        os.makedirs(out_dir, exist_ok=True)

        project_summary = {}

        for proc in procedures:
            # Only analyze procedures that have I/O operations
            if not hasattr(proc, "io_tracker") or not proc.io_tracker.completed:
                continue

            tracker = proc.io_tracker
            tracker.finalize()

            # Get I/O summary data
            io_summary = tracker.summarize_file_io()
            if not io_summary:
                continue

            # Analyze input patterns for this procedure
            input_analysis = self._analyze_input_patterns(proc, tracker, io_summary)
            if not input_analysis:
                continue

            project_summary[proc.name] = input_analysis

            # Save individual file
            path = os.path.join(out_dir, f"{proc.name}.input_analysis.json")
            try:
                with open(path, "w") as f:
                    json.dump(input_analysis, f, indent=2)
                log.info("Wrote input analysis for %s → %s", proc.name, path)
            except IOError as e:
                log.error("Failed to write input analysis for %s: %s", proc.name, e)

        # Save master summary
        master_path = os.path.join(out_dir, "input_analysis_summary.json")
        try:
            with open(master_path, "w") as f:
                json.dump(project_summary, f, indent=2)
            log.info("Wrote master input analysis → %s", master_path)
        except IOError as e:
            log.error("Failed to write master input analysis: %s", e)

        return project_summary

    def procedures_output_analysis_to_json(
        self, procedures: List[FortranProcedure], out_dir: Optional[str] = None
    ) -> None:
        """
        Export detailed output file analysis for procedures to JSON files.

        For each procedure that writes output files, this method analyzes:
        - Subroutine name that writes the output
        - Unit number used for file operations
        - Whether files are opened via assigned variables vs hardcoded strings
        - Write structure of the file (title, header, data)
        - What data is written and from what data types/variables

        Args:
            procedures: List of procedures to process
            out_dir: Output directory path. Defaults to ./json_outputs/output_analysis
        """
        out_dir = out_dir or os.path.join(
            os.getcwd(), "json_outputs", "output_analysis"
        )
        os.makedirs(out_dir, exist_ok=True)

        project_summary = {}

        for proc in procedures:
            # Only analyze procedures that have I/O operations
            if not hasattr(proc, "io_tracker") or not proc.io_tracker.completed:
                continue

            tracker = proc.io_tracker
            tracker.finalize()

            # Get I/O summary data
            io_summary = tracker.summarize_file_io()
            if not io_summary:
                continue

            # Analyze output patterns for this procedure
            output_analysis = self._analyze_output_patterns(proc, tracker, io_summary)
            if not output_analysis:
                continue

            project_summary[proc.name] = output_analysis

            # Save individual file
            path = os.path.join(out_dir, f"{proc.name}.output_analysis.json")
            try:
                with open(path, "w") as f:
                    json.dump(output_analysis, f, indent=2)
                log.info("Wrote output analysis for %s → %s", proc.name, path)
            except IOError as e:
                log.error("Failed to write output analysis for %s: %s", proc.name, e)

        # Save master summary
        master_path = os.path.join(out_dir, "output_analysis_summary.json")
        try:
            with open(master_path, "w") as f:
                json.dump(project_summary, f, indent=2)
            log.info("Wrote master output analysis → %s", master_path)
        except IOError as e:
            log.error("Failed to write master output analysis: %s", e)

        return project_summary

    def _analyze_output_patterns(
        self, proc: FortranProcedure, tracker, io_summary: Dict
    ) -> Optional[Dict]:
        """
        Analyze output file patterns for a specific procedure.

        Returns detailed analysis of output operations including:
        - Unit numbers and file opening methods
        - Write structure patterns
        - Variable assignments and data types
        """
        import re

        if not io_summary:
            return None

        analysis = {
            "subroutine_name": proc.name,
            "line_number": getattr(proc, "line_number", None),
            "source_file": getattr(proc, "filename", None),
            "output_files": [],
        }

        # Analyze each file that has output operations
        for filename, file_data in io_summary.items():
            if "summary" not in file_data:
                continue

            summary = file_data["summary"]
            timeline = file_data.get("timeline", [])

            # Only process files that have write operations
            if not self._has_write_operations(summary, timeline):
                continue

            file_analysis = {
                "filename": filename,
                "unit_number": summary.get("unit"),
                "opening_method": self._analyze_file_opening(timeline, filename),
                "write_structure": self._analyze_write_structure(summary, timeline),
                "data_variables": self._analyze_output_variables(
                    summary, timeline, proc
                ),
            }

            analysis["output_files"].append(file_analysis)

        return analysis if analysis["output_files"] else None

    def _has_write_operations(self, summary: Dict, timeline: List[Dict]) -> bool:
        """Check if a file has write operations."""
        # Check for write operations in timeline
        for op in timeline:
            if op.get("kind") == "write":
                return True

        # Check for data writes in summary
        if summary.get("data_writes"):
            return True

        return False

    def _analyze_write_structure(self, summary: Dict, timeline: List[Dict]) -> Dict:
        """Analyze the write structure of the file (title, header, data)."""
        structure = {
            "has_title": False,
            "has_header": False,
            "has_data": False,
            "write_sequence": [],
        }

        # Check for header writes
        headers = summary.get("headers", [])
        if "titldum" in headers:
            structure["has_title"] = True
        if "header" in headers or any(h for h in headers if h != "titldum"):
            structure["has_header"] = True

        # Check for data writes
        data_writes = summary.get("data_writes", [])
        if data_writes:
            structure["has_data"] = True

        # Build write sequence from timeline
        for op in timeline:
            if op.get("kind") == "write":
                raw = op.get("raw", "")
                line_no = op.get("lineno")

                # Extract variables being written
                write_vars = self._extract_write_variables(raw)
                structure["write_sequence"].append(
                    {
                        "line_number": line_no,
                        "variables": write_vars,
                        "raw_statement": raw,
                    }
                )

        return structure

    def _analyze_output_variables(
        self, summary: Dict, timeline: List[Dict], proc: FortranProcedure
    ) -> List[Dict]:
        """Analyze what data variables are written and their types."""
        variables = []

        # Process data writes from summary
        data_writes = summary.get("data_writes", [])
        for write_group in data_writes:
            columns = write_group.get("columns", [])
            rows = write_group.get("rows", 1)

            for var_name in columns:
                var_info = self._get_variable_type_info(proc, var_name)
                variables.append(
                    {
                        "name": var_name,
                        "type": var_info.get("type"),
                        "kind": var_info.get("kind"),
                        "dimensions": var_info.get("dimensions"),
                        "write_count": rows,
                    }
                )

        return variables

    def _extract_write_variables(self, raw_statement: str) -> List[str]:
        """Extract variable names from a write statement."""
        import re

        # Match write(...) variable_list pattern
        match = re.search(r"write\s*\([^)]*\)\s*(.+)", raw_statement, re.IGNORECASE)
        if not match:
            return []

        var_part = match.group(1).strip()

        # Split on commas, handling nested parentheses
        variables = []
        current_var = ""
        paren_depth = 0

        for char in var_part:
            if char == "(":
                paren_depth += 1
                current_var += char
            elif char == ")":
                paren_depth -= 1
                current_var += char
            elif char == "," and paren_depth == 0:
                if current_var.strip():
                    variables.append(current_var.strip())
                current_var = ""
            else:
                current_var += char

        if current_var.strip():
            variables.append(current_var.strip())

        return variables

    def _analyze_input_patterns(
        self, proc: FortranProcedure, tracker, io_summary: Dict
    ) -> Optional[Dict]:
        """
        Analyze input file patterns for a specific procedure.

        Returns detailed analysis of input operations including:
        - Unit numbers and file opening methods
        - Read structure patterns
        - Variable assignments and data types
        """
        import re

        if not io_summary:
            return None

        analysis = {
            "subroutine_name": proc.name,
            "line_number": getattr(proc, "line_number", None),
            "source_file": getattr(proc, "filename", None),
            "input_files": [],
        }

        # Analyze each file that has input operations
        for filename, file_data in io_summary.items():
            if "summary" not in file_data:
                continue

            summary = file_data["summary"]
            timeline = file_data.get("timeline", [])

            # Only process files that have read operations
            if not summary.get("headers") and not summary.get("data_reads"):
                continue

            file_analysis = {
                "filename": filename,
                "unit_number": summary.get("unit"),
                "opening_method": self._analyze_file_opening(timeline, filename),
                "read_structure": self._analyze_read_structure(summary, timeline),
                "data_variables": self._analyze_data_variables(summary, timeline, proc),
            }

            analysis["input_files"].append(file_analysis)

        return analysis if analysis["input_files"] else None

    def _analyze_file_opening(self, timeline: List[Dict], filename: str) -> Dict:
        """Analyze how a file is opened (assigned variable vs hardcoded string)."""
        for op in timeline:
            if op.get("kind") == "open":
                raw = op.get("raw", "")

                # Extract the file parameter from the open statement
                file_match = re.search(r"file\s*=\s*([^,)]+)", raw, re.IGNORECASE)
                if file_match:
                    file_expr = file_match.group(1).strip()

                    # Check if it's a hardcoded string (in quotes)
                    if (file_expr.startswith('"') and file_expr.endswith('"')) or (
                        file_expr.startswith("'") and file_expr.endswith("'")
                    ):
                        return {
                            "method": "hardcoded_string",
                            "expression": file_expr,
                            "line_number": op.get("lineno"),
                        }
                    else:
                        return {
                            "method": "assigned_variable",
                            "expression": file_expr,
                            "line_number": op.get("lineno"),
                        }

        return {"method": "unknown", "expression": None, "line_number": None}

    def _analyze_read_structure(self, summary: Dict, timeline: List[Dict]) -> Dict:
        """Analyze the read structure of the file (title, header, data)."""
        structure = {
            "has_title": False,
            "has_header": False,
            "has_data": False,
            "read_sequence": [],
        }

        # Check for title/header reads
        headers = summary.get("headers", [])
        if "titldum" in headers:
            structure["has_title"] = True
        if "header" in headers or any(h for h in headers if h != "titldum"):
            structure["has_header"] = True

        # Check for data reads
        data_reads = summary.get("data_reads", [])
        if data_reads:
            structure["has_data"] = True

        # Build read sequence from timeline
        for op in timeline:
            if op.get("kind") == "read":
                raw = op.get("raw", "")
                line_no = op.get("lineno")

                # Extract variables being read
                read_vars = self._extract_read_variables(raw)
                structure["read_sequence"].append(
                    {
                        "line_number": line_no,
                        "variables": read_vars,
                        "raw_statement": raw,
                    }
                )

        return structure

    def _analyze_data_variables(
        self, summary: Dict, timeline: List[Dict], proc: FortranProcedure
    ) -> List[Dict]:
        """Analyze what data variables are read and their types."""
        variables = []

        # Process data reads from summary
        data_reads = summary.get("data_reads", [])
        for read_group in data_reads:
            columns = read_group.get("columns", [])
            rows = read_group.get("rows", 1)

            for var_name in columns:
                var_info = self._get_variable_type_info(proc, var_name)
                variables.append(
                    {
                        "name": var_name,
                        "type": var_info.get("type"),
                        "kind": var_info.get("kind"),
                        "dimensions": var_info.get("dimensions"),
                        "read_count": rows,
                    }
                )

        return variables

    def _extract_read_variables(self, raw_statement: str) -> List[str]:
        """Extract variable names from a read statement."""
        import re

        # Match read(...) variable_list pattern
        match = re.search(r"read\s*\([^)]*\)\s*(.+)", raw_statement, re.IGNORECASE)
        if not match:
            return []

        var_part = match.group(1).strip()

        # Split on commas, handling nested parentheses
        variables = []
        current_var = ""
        paren_depth = 0

        for char in var_part:
            if char == "(":
                paren_depth += 1
                current_var += char
            elif char == ")":
                paren_depth -= 1
                current_var += char
            elif char == "," and paren_depth == 0:
                if current_var.strip():
                    variables.append(current_var.strip())
                current_var = ""
            else:
                current_var += char

        if current_var.strip():
            variables.append(current_var.strip())

        return variables

    def _get_variable_type_info(self, proc: FortranProcedure, var_name: str) -> Dict:
        """Get type information for a variable from the procedure's fvar."""
        if not hasattr(proc, "fvar") or not isinstance(proc.fvar, dict):
            return {"type": "unknown", "kind": None, "dimensions": None}

        # Look for the variable in fvar
        var_info = self._find_variable_info(proc, var_name)
        if var_info:
            return {
                "type": var_info.get("vartype", "unknown"),
                "kind": var_info.get("kind"),
                "dimensions": var_info.get("dimension"),
            }

        return {"type": "unknown", "kind": None, "dimensions": None}

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
        # self.module_metadata = [get_module_metadata(module) for module in self.modules] # do this in xwalk  instead or is a json still ultimately needed?
        # self.xwalk_type_dicts = [self.cross_walk_type_dicts(procedures) for procedures in self.procedures] #all_vars exists, still need a xwalk but do it after correlating

        # Collect I/O files from all procedures
        self.collect_io_files()

    def build_call_site_mappings(self) -> Dict[str, List[Dict]]:
        """
        Build a mapping of procedure names to their call sites with argument values.
        This is used to resolve parameter filenames in IO operations.

        Returns:
            Dict mapping procedure name (lowercase) to list of call site info dicts
            Each call site dict contains: {
                'caller': calling procedure,
                'arguments': list of argument expressions,
                'line_no': line number of call
            }
        """
        import re

        call_site_map = {}

        # Pattern to match procedure calls: call procname(arg1, arg2, ...)
        # Also handle function-style calls: result = procname(arg1, arg2)
        call_pattern = re.compile(
            r"\b(?:call\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", re.IGNORECASE
        )

        for proc in self.procedures:
            # Get the source file and lines for this procedure
            if not hasattr(proc, "source_file") or not proc.source_file:
                continue

            # Read source lines
            source_lines = []
            if hasattr(proc.source_file, "raw_src"):
                source_lines = proc.source_file.raw_src.split("\n")
            elif hasattr(proc.source_file, "source"):
                source_lines = proc.source_file.source

            # Look for call statements
            for line_no, line in enumerate(source_lines, 1):
                # Skip comments
                comment_pos = line.find("!")
                if comment_pos >= 0:
                    line = line[:comment_pos]

                line = line.strip()
                if not line:
                    continue

                # Find calls in this line
                for match in call_pattern.finditer(line):
                    called_proc_name = match.group(1).lower()

                    # Try to extract arguments
                    # Find the opening parenthesis position
                    paren_start = match.end() - 1

                    # Extract the argument list by matching parentheses
                    try:
                        args_str = self._extract_parenthesized_content(
                            line[paren_start:]
                        )
                        if args_str:
                            # Split arguments by commas (respecting nested parentheses)
                            arguments = self._split_arguments(args_str)

                            # Store call site info
                            if called_proc_name not in call_site_map:
                                call_site_map[called_proc_name] = []

                            call_site_map[called_proc_name].append(
                                {
                                    "caller": proc,
                                    "arguments": arguments,
                                    "line_no": line_no,
                                    "raw_line": line,
                                }
                            )
                    except:
                        # If parsing fails, skip this call
                        continue

        return call_site_map

    def _extract_parenthesized_content(self, text: str) -> str:
        """
        Extract content within the first set of parentheses.
        Returns the content without the outer parentheses.
        """
        if not text or text[0] != "(":
            return ""

        depth = 0
        for i, char in enumerate(text):
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    return text[1:i]
        return ""

    def _split_arguments(self, args_str: str) -> List[str]:
        """
        Split a comma-separated argument list while respecting nested parentheses.
        """
        arguments = []
        current_arg = ""
        depth = 0

        for char in args_str:
            if char == "," and depth == 0:
                arguments.append(current_arg.strip())
                current_arg = ""
            else:
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                current_arg += char

        # Don't forget the last argument
        if current_arg.strip():
            arguments.append(current_arg.strip())

        return arguments

    def build_unit_filename_mapping(self) -> Dict[str, str]:
        """
        Build a project-wide mapping of unit numbers to filenames by scanning
        all OPEN statements across all procedures.

        Returns:
            Dict mapping unit number (as string) to filename
        """
        unit_to_filename = {}

        for proc in self.procedures:
            if hasattr(proc, "io_tracker") and proc.io_tracker:
                # Get all completed I/O sessions
                for unit, sessions in proc.io_tracker.completed.items():
                    for session in sessions:
                        if session.file and session.file != "<unknown>":
                            # Skip synthetic "unit_XXXX" filenames - we only want real filenames
                            if not session.file.startswith("unit_"):
                                # Prefer sessions with explicit filenames over synthetic ones
                                unit_to_filename[str(unit)] = session.file

        return unit_to_filename

    def build_variable_type_mapping(self) -> Dict[str, str]:
        """
        Build a project-wide mapping of variable names to their type names
        by scanning all variable declarations in all modules.
        
        Returns:
            Dict mapping variable name (lowercase) to type name (lowercase)
        """
        var_to_type = {}
        
        # Scan all modules
        for module in self.modules:
            if hasattr(module, "variables"):
                for var in module.variables:
                    # Get the type name from the variable's vartype or meta information
                    if hasattr(var, "vartype") and var.vartype:
                        vartype_str = var.vartype.strip()
                        # Extract type name from declarations like "type(input_exco)"
                        import re
                        m = re.match(r"type\s*\(\s*(\w+)\s*\)", vartype_str, re.IGNORECASE)
                        if m:
                            type_name = m.group(1).lower()
                            var_name = var.name.lower()
                            var_to_type[var_name] = type_name
        
        return var_to_type

    def build_type_defaults_mapping(self) -> Dict[str, str]:
        """
        Build a project-wide mapping of type component names to their default values
        by scanning all type definitions in all modules.

        Returns:
            Dict mapping component name (compound names like 'typename%component')
            to default value
        """
        type_defaults = {}

        # Scan all types in all modules
        for module in self.modules:
            if hasattr(module, "types"):
                for dtype in module.types:
                    if hasattr(dtype, "variables"):
                        # Extract defaults from type components
                        for var in dtype.variables:
                            if hasattr(var, "initial") and var.initial:
                                # Store compound name (typename%varname)
                                compound_name = f"{dtype.name}%{var.name}".lower()

                                # Convert initial value to string
                                initial_value = str(var.initial).strip()

                                # Skip empty strings but keep actual quoted strings
                                if initial_value and initial_value not in (
                                    '""',
                                    "''",
                                    "",
                                ):
                                    # Store compound name (typename%componentname)
                                    type_defaults[compound_name] = initial_value

        return type_defaults

    def collect_io_files(self):
        """
        Collect all I/O files accessed by procedures in the project.
        Creates FortranIOFile objects for each unique file.
        Now with enhanced cross-file and cross-module resolution including call-site analysis.
        """
        # Build project-wide mappings for better resolution
        unit_to_filename_map = self.build_unit_filename_mapping()
        type_defaults_map = self.build_type_defaults_mapping()
        var_to_type_map = self.build_variable_type_mapping()
        call_site_map = self.build_call_site_mappings()

        # Set the class-level mappings on IoTracker so they're available
        # when procedure pages access the io_operations property
        from ford.sourceform import IoTracker

        IoTracker._unit_filename_map = unit_to_filename_map
        IoTracker._type_defaults_map = type_defaults_map
        IoTracker._var_to_type_map = var_to_type_map

        io_files_dict: Dict[str, FortranIOFile] = {}

        # Iterate through all procedures that have I/O operations
        for proc in self.procedures:
            if hasattr(proc, "io_operations"):
                io_ops = proc.io_operations
                if io_ops:
                    for file_key, operations in io_ops.items():
                        # Enhanced filename resolution
                        filename = operations.get("filename", file_key)
                        filename_resolved = operations.get("filename_resolved")
                        unit = operations.get("unit", "unknown")
                        unit_resolved = operations.get("unit_resolved")

                        # FIRST: Try call-site resolution if filename appears to be a parameter
                        # This takes precedence over other resolution methods to avoid incorrect
                        # unit-based fallback matches
                        filenames_from_calls = []
                        if filename:
                            # Check if filename is a simple identifier (could be a parameter)
                            # Skip if it's a literal string (starts/ends with quotes) or synthetic unit name
                            if (
                                not filename.startswith('"')
                                and not filename.startswith("'")
                                and not filename.startswith("unit_")
                                and "%" not in filename
                            ):
                                # Check if this procedure has the filename as a parameter
                                if hasattr(proc, "args") and proc.args:
                                    param_index = -1
                                    for i, arg in enumerate(proc.args):
                                        # Args can be FortranVariable objects or strings
                                        arg_name = (
                                            arg.name
                                            if hasattr(arg, "name")
                                            else str(arg)
                                        )
                                        if arg_name.lower() == filename.lower():
                                            param_index = i
                                            break

                                    # If filename matches a parameter, look at call sites
                                    if param_index >= 0:
                                        proc_name_lower = proc.name.lower()
                                        if proc_name_lower in call_site_map:
                                            for call_site in call_site_map[
                                                proc_name_lower
                                            ]:
                                                args = call_site["arguments"]
                                                if param_index < len(args):
                                                    arg_value = args[
                                                        param_index
                                                    ].strip()

                                                    # Try to resolve the argument value
                                                    resolved_arg = None

                                                    # Check if it's a literal string
                                                    if arg_value.startswith(
                                                        '"'
                                                    ) or arg_value.startswith("'"):
                                                        resolved_arg = arg_value.strip(
                                                            '"'
                                                        ).strip("'")
                                                    # Check if it's a compound variable in type defaults
                                                    elif "%" in arg_value:
                                                        arg_lower = arg_value.lower()
                                                        if (
                                                            arg_lower
                                                            in type_defaults_map
                                                        ):
                                                            resolved_arg = (
                                                                type_defaults_map[
                                                                    arg_lower
                                                                ]
                                                            )
                                                        else:
                                                            # Try just the last component
                                                            parts = arg_value.split("%")
                                                            if len(parts) >= 2:
                                                                simple_name = parts[
                                                                    -1
                                                                ].lower()
                                                                if (
                                                                    simple_name
                                                                    in type_defaults_map
                                                                ):
                                                                    resolved_arg = type_defaults_map[
                                                                        simple_name
                                                                    ]

                                                    if resolved_arg:
                                                        # Clean up the resolved value (remove quotes if present)
                                                        resolved_arg = (
                                                            resolved_arg.strip(
                                                                '"'
                                                            ).strip("'")
                                                        )
                                                        if (
                                                            resolved_arg
                                                            not in filenames_from_calls
                                                        ):
                                                            filenames_from_calls.append(
                                                                resolved_arg
                                                            )

                        # If we found filenames from call sites, use those and skip other resolution
                        # Otherwise, continue with normal resolution
                        if not filenames_from_calls:
                            # Try to resolve using project-wide mappings
                            # 1. If unit is a number (either directly or resolved), try to find its filename from OPEN statements
                            # BUT: Only use unit-based resolution for synthetic filenames (unit_XXX)
                            # Don't use it for literal strings or variable references, as unit numbers are reused
                            unit_number = unit_resolved if unit_resolved else unit
                            # Only use unit-based resolution if:
                            # - We don't have a concrete filename (it's a synthetic unit_XXX name)
                            # - The filename is not a literal string or variable reference
                            should_use_unit_resolution = (
                                filename and filename.startswith("unit_") and
                                unit_number and str(unit_number) in unit_to_filename_map
                            )
                            if should_use_unit_resolution:
                                cross_file_filename = unit_to_filename_map[
                                    str(unit_number)
                                ]
                                # Only use if we don't already have a better resolution
                                if not filename_resolved:
                                    filename_resolved = cross_file_filename

                            # 2. If filename looks like a variable, try type defaults mapping
                            if filename and not filename_resolved:
                                # Check for compound names (e.g., in_sim%time)
                                if "%" in filename:
                                    filename_lower = filename.lower()
                                    # Try exact match first
                                    if filename_lower in type_defaults_map:
                                        filename_resolved = type_defaults_map[
                                            filename_lower
                                        ]
                                    else:
                                        # Try to resolve by matching variable to its type
                                        # E.g., in_exco%pest -> get type of in_exco -> input_exco -> look up input_exco%pest
                                        parts = filename.split("%")
                                        if len(parts) == 2:
                                            var_name = parts[0].strip().lower()
                                            component_name = parts[1].strip().lower()
                                            if var_name in var_to_type_map:
                                                type_name = var_to_type_map[var_name]
                                                type_component_key = f"{type_name}%{component_name}"
                                                if type_component_key in type_defaults_map:
                                                    filename_resolved = type_defaults_map[
                                                        type_component_key
                                                    ]

                        # Determine the final display filename(s)
                        # If we found multiple filenames from call sites, create separate entries
                        filenames_to_process = []
                        if filenames_from_calls:
                            # We have call-site resolved filenames, use them
                            for resolved_filename in filenames_from_calls:
                                filenames_to_process.append(
                                    {
                                        "display_filename": resolved_filename,
                                        "filename_resolved": resolved_filename,
                                        "source": "call_site",
                                    }
                                )
                        else:
                            # Use the single resolved or unresolved filename
                            display_filename = (
                                filename_resolved if filename_resolved else filename
                            )
                            # Strip quotes from display filename if present
                            if display_filename:
                                display_filename = display_filename.strip('"').strip(
                                    "'"
                                )
                            filenames_to_process.append(
                                {
                                    "display_filename": display_filename,
                                    "filename_resolved": filename_resolved,
                                    "source": "direct",
                                }
                            )

                        # Process each filename (usually just one, but could be multiple from call sites)
                        for filename_info in filenames_to_process:
                            display_filename = filename_info["display_filename"]
                            filename_resolved_for_entry = filename_info[
                                "filename_resolved"
                            ]

                            # Create a unique key for this file based on filename only
                            # Multiple procedures can access the same file with different unit numbers
                            io_key = display_filename

                            # Create or retrieve the FortranIOFile object
                            if io_key not in io_files_dict:
                                # Use the first encountered unit as the default
                                # (The template will show individual units for each procedure)
                                io_file = FortranIOFile(display_filename, unit)
                                # Set base_url for link generation (as string, not Path)
                                io_file.base_url = str(self.settings.project_url)
                                io_files_dict[io_key] = io_file

                            # Update operations with enhanced resolution
                            enhanced_operations = operations.copy()
                            if filename_resolved_for_entry:
                                enhanced_operations["filename_resolved"] = (
                                    filename_resolved_for_entry
                                )

                            # Add this procedure to the file's list of users
                            io_files_dict[io_key].add_procedure(
                                proc, enhanced_operations
                            )
                            
                            # Store reference to the FortranIOFile object in the procedure's io_operations
                            # This allows the template to link to the I/O file page
                            # Use the original file_key from the procedure's io_operations dict
                            if hasattr(proc, "io_operations") and proc.io_operations:
                                if file_key in proc.io_operations:
                                    proc.io_operations[file_key]["iofile_object"] = io_files_dict[io_key]

        # Convert dict to list and sort by filename
        self.iofiles = sorted(io_files_dict.values(), key=lambda x: x.io_filename)
        
        # Create a mapping from filenames to IOFile objects that templates can use
        # This allows procedure pages to link to I/O file pages
        self.iofile_map = {}
        for io_key, io_file in io_files_dict.items():
            self.iofile_map[io_key] = io_file
            # Also store by the actual io_filename in case they differ
            self.iofile_map[io_file.io_filename] = io_file

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
