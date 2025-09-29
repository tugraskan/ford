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


# Regular expression patterns for type extraction
DERIVED_TYPE_RE = re.compile(r"type\\([a-zA-Z_][a-zA-Z0-9_]*)\.html")

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


def _extract_derived_type_name(full_type: str) -> str:
    """
    Extract derived type name from full_type string.
    
    Args:
        full_type: The full type string to extract from.
        
    Returns:
        The derived type name if found, otherwise the original full_type.
    """
    if not full_type:
        return ""
    
    match = DERIVED_TYPE_RE.search(full_type)
    return match.group(1) if match else full_type


def _extract_variable_metadata(var, var_name: str) -> dict:
    """
    Extract metadata for a single variable.
    
    Args:
        var: The variable object to extract metadata from.
        var_name: The variable name as fallback.
        
    Returns:
        Dictionary containing variable metadata.
    """
    full_type = getattr(var, "full_type", "")
    return {
        "ident": getattr(var, "name", var_name),
        "type": _extract_derived_type_name(full_type),
        "initial": getattr(var, "initial", None),
        "doc": getattr(var, "doc_list", []),
    }


def _extract_type_metadata(dtype, type_name: str) -> dict:
    """
    Extract metadata for a single derived type.
    
    Args:
        dtype: The derived type object to extract metadata from.
        type_name: The type name as fallback.
        
    Returns:
        Dictionary containing type metadata.
    """
    variables = getattr(dtype, "variables", [])
    vars_metadata = []
    
    for variable in variables:
        full_type = getattr(variable, "full_type", "")
        vars_metadata.append({
            "ident": getattr(variable, "name", ""),
            "type": _extract_derived_type_name(full_type),
            "initial": getattr(variable, "initial", None),
            "doc": getattr(variable, "doc_list", []),
        })
    
    return {
        "name": getattr(dtype, "name", type_name),
        "variables": vars_metadata,
        "doc": getattr(dtype, "doc_list", []),
    }


def _extract_subroutine_usage(subroutine) -> dict:
    """
    Extract usage metadata for a single subroutine.
    
    Args:
        subroutine: The subroutine object to extract metadata from.
        
    Returns:
        Dictionary containing subroutine usage metadata.
    """
    usage = {
        "subroutine_name": getattr(subroutine, "name", ""),
        "used_derived_types": [],
        "used_variables": [],
    }
    
    calls = getattr(subroutine, "calls", [])
    for call in calls:
        if isinstance(call, FortranType):
            call_name = getattr(call, "name", "")
            if call_name:
                usage["used_derived_types"].append(call_name)
        elif isinstance(call, FortranVariable):
            call_name = getattr(call, "name", "")
            if call_name:
                usage["used_variables"].append(call_name)
    
    return usage


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
    all_vars = getattr(module, "all_vars", {})
    for var_name, var in all_vars.items():
        metadata["all_vars"].append(_extract_variable_metadata(var, var_name))

    # Extract metadata for derived types
    all_types = getattr(module, "all_types", {})
    for type_name, dtype in all_types.items():
        metadata["all_types"].append(_extract_type_metadata(dtype, type_name))

    # Extract subroutine usage metadata
    subroutines = getattr(module, "subroutines", [])
    for subroutine in subroutines:
        metadata["subroutine_usage"].append(_extract_subroutine_usage(subroutine))

    return metadata