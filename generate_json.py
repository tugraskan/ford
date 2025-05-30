import json
from ford.fortran_project import Project
from ford.settings import ProjectSettings
from ford.external_project import get_module_metadata
from pathlib import Path


def main():
    # Specify the source directory for the Fortran files\
    source_dir = r'C:\Users\taci.ugraskan\source\repos\ford\tsrc'
    source_dir = r'C:\Users\taci.ugraskan\source\repos\ford\src'

    


    # Create ProjectSettings with the source directory
    project_settings = ProjectSettings(src_dir=[Path(source_dir)])
    #project_settings.dbg = False

    # Create the project instance
    project = Project(project_settings)

    # Correlate the project data (parses and processes the Fortran files)!
    project.correlate()

    print(f"Project data has been correlated for source directory: {source_dir}")

    procedures = project.get_procedures()


    project.cross_walk_type_dicts(procedures)

    # Extract metadata for each module in the project

    # Write the metadata to a JSON file
    project.procedures_fvar_to_json(procedures)

    project.procedures_io_to_json(procedures)

    project.procedures_call_to_json(procedures)

    #output_file = project_settings.output_file if hasattr(project_settings, 'output_file') else "output.json"
    #print(f"Metadata has been written to {output_file}")

if __name__ == "__main__":
    main()
