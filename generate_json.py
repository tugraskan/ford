import json
from ford.fortran_project import Project
from ford.external_project import get_module_metadata

def main():
    project = Project()
    project.correlate()

    metadata = [get_module_metadata(module) for module in project.modules]

    with open("derived_types_metadata.json", "w") as json_file:
        json.dump(metadata, json_file, indent=4)

if __name__ == "__main__":
    main()
