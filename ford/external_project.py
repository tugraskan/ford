from __future__ import annotations

import json
import pathlib
import re
from urllib.error import URLError
from urllib.request import urlopen
from urllib.parse import urljoin

from ford.sourceform import (
    FortranBase,
    FortranModule,
    FortranType,
    FortranVariable,
    FortranSubroutine,
    ExternalModule,
    ExternalFunction,
    ExternalSubroutine,
    ExternalInterface,
    ExternalType,
    ExternalVariable,
    ExternalBoundProcedure,
)
from ford.version import __version__


# attributes of a module object needed for further processing
ATTRIBUTES = [
    "pub_procs",
    "pub_absints",
    "pub_types",
    "pub_vars",
    "functions",
    "subroutines",
    "interfaces",
    "absinterfaces",
    "types",
    "variables",
    "boundprocs",
    "vartype",
    "permission",
    "deferred",
    "generic",
    "attribs",
    "args",
]

# Mapping between entity name and its type
ENTITIES = {
    "module": ExternalModule,
    "interface": ExternalInterface,
    "type": ExternalType,
    "variable": ExternalVariable,
    "function": ExternalFunction,
    "subroutine": ExternalSubroutine,
    "boundprocedure": ExternalBoundProcedure,
}

METADATA_NAME = "ford-metadata"


def obj2dict(intObj):
    """
    Converts an object to a dictionary.
    """
    if hasattr(intObj, "external_url"):
        return None
    if isinstance(intObj, str):
        return intObj
    extDict = {
        "name": intObj.name,
        "external_url": f"./{intObj.get_url()}",
        "obj": intObj.obj,
    }
    if hasattr(intObj, "proctype"):
        extDict["proctype"] = intObj.proctype
    for attrib in ATTRIBUTES:
        if not hasattr(intObj, attrib):
            continue

        attribute = getattr(intObj, attrib)

        if isinstance(attribute, list):
            extDict[attrib] = [obj2dict(item) for item in attribute]
        elif isinstance(attribute, dict):
            extDict[attrib] = {key: obj2dict(val) for key, val in attribute.items()}
        else:
            extDict[attrib] = str(attribute)
    return extDict


def modules_from_local(url: pathlib.Path):
    """
    Get module information from an external project but on the
    local file system.
    """

    return json.loads((url / "modules.json").read_text(encoding="utf-8"))


def dict2obj(project, extDict, url, parent=None, remote: bool = False) -> FortranBase:
    """
    Converts a dictionary to an object and immediately adds it to the project
    """
    if isinstance(extDict, str):
        return extDict
    name = extDict["name"]
    if extDict["external_url"]:
        extDict["external_url"] = extDict["external_url"].split("/", 1)[-1]
        if remote:
            external_url = urljoin(url, extDict["external_url"])
        else:
            external_url = url / extDict["external_url"]
    else:
        external_url = extDict["external_url"]

    # Look up what type of entity this is
    obj_type = extDict.get("proctype", extDict["obj"]).lower()
    # Construct the entity
    extObj = ENTITIES[obj_type](name, external_url, parent)
    # Now add it to the correct project list
    project_list = getattr(project, extObj._project_list)
    project_list.append(extObj)

    if obj_type == "interface":
        extObj.proctype = extDict["proctype"]

    for key in ATTRIBUTES:
        if key not in extDict:
            continue
        if isinstance(extDict[key], list):
            tmpLs = [
                dict2obj(project, item, url, extObj, remote)
                for item in extDict[key]
                if item
            ]
            setattr(extObj, key, tmpLs)
        elif isinstance(extDict[key], dict):
            tmpDict = {
                key2: dict2obj(project, item, url, extObj, remote)
                for key2, item in extDict[key].items()
                if item
            }
            setattr(extObj, key, tmpDict)
        else:
            setattr(extObj, key, extDict[key])
    return extObj


def dump_modules(project, path="."):
    """Dump modules to JSON file"""

    modules = [obj2dict(module) for module in project.modules]
    metadata = [get_module_metadata(module) for module in project.modules]
    data = {
        METADATA_NAME: {
            "version": __version__,
        },
        "modules": modules,
        "metadata": metadata,
    }
    (pathlib.Path(path) / "modules.json").write_text(json.dumps(data))


def load_external_modules(project):
    """Load external modules from JSON file into an existing project"""

    # get the external modules from the external URLs
    for url in project.external.values():
        remote = re.match("https?://", url)
        try:
            if remote:
                # Ensure the URL ends with '/' to have urljoin work as
                # intentend.
                if url[-1] != "/":
                    url = url + "/"
                extModules = json.loads(
                    urlopen(urljoin(url, "modules.json")).read().decode("utf8")
                )
            else:
                if not pathlib.Path(url).is_absolute():
                    url = project.settings.directory.joinpath(url).resolve()
                extModules = modules_from_local(url)
        except (URLError, json.JSONDecodeError) as error:
            extModules = []
            print(f"Could not open external URL '{url}', reason: {error}")

        if METADATA_NAME in extModules:
            # TODO: Check version compatibility
            extModules = extModules["modules"]

        # convert modules defined in the JSON database to module objects
        for extModule in extModules:
            dict2obj(project, extModule, url, remote=remote)


def get_module_metadata(module: FortranModule) -> dict:
    """
    Extract comprehensive metadata for a given Fortran module.
    
    This function processes module variables, derived types, and usage patterns
    to create a structured metadata representation.
    
    Args:
        module: The Fortran module to extract metadata from.
        
    Returns:
        Dictionary containing metadata including variables, types, and subroutine usage.
    """
    metadata = {
        "all_vars": [],
        "all_types": [],
        "subroutine_usage": [],
    }

    # Extract module variables
    if hasattr(module, "all_vars"):
        for var_name, var in module.all_vars.items():
            # Extract derived type name from full_type if it's a derived type reference
            derived_type_match = re.search(r"type\\([a-zA-Z_][a-zA-Z0-9_]*)\.html", var.full_type)
            derived_type = derived_type_match.group(1) if derived_type_match else var.full_type

            metadata["all_vars"].append({
                "ident": var.name,
                "type": derived_type,
                "initial": var.initial,
                "doc": var.doc_list,
            })

    # Extract metadata for derived types
    if hasattr(module, "all_types"):
        for type_name, dtype in module.all_types.items():
            vars_metadata = []

            # Iterate through variables in the derived type
            for variable in dtype.variables:
                # Use a regular expression to extract the type if it's a derived type
                derived_type_match = re.search(r"type\\([a-zA-Z_][a-zA-Z0-9_]*)\.html", variable.full_type)
                derived_type = derived_type_match.group(1) if derived_type_match else variable.full_type
                vars_metadata.append({
                    "ident": variable.name,
                    "type": derived_type,
                    "initial": getattr(variable, "initial", None),  # Handle missing attributes safely
                    "doc": getattr(variable, "doc_list", []),  # Default to an empty list
                })

            # Append the metadata for the derived type
            metadata["all_types"].append({
                "name": dtype.name,
                "variables": vars_metadata,  # Include the list of variables metadata
                "doc": getattr(dtype, "doc_list", []),  # Optional documentation for the derived type
            })

        # Populate the subroutines list for each module
    #for subroutine in project.subroutines:
        #if subroutine.uses == 'x':
           # continue

    # Identify derived types and specific variables used in subroutines
    for subroutine in module.subroutines:
        subroutine_usage = {
            "subroutine_name": subroutine.name,
            "used_derived_types": [],
            "used_variables": [],
        }

        for call in subroutine.calls:
            if isinstance(call, FortranType):
                subroutine_usage["used_derived_types"].append(call.name)
            elif isinstance(call, FortranVariable):
                subroutine_usage["used_variables"].append(call.name)

        metadata["subroutine_usage"].append(subroutine_usage)

    return metadata