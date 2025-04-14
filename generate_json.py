import json
from ford.fortran_project import Project
from ford.settings import ProjectSettings
from ford.external_project import get_module_metadata
from pathlib import Path


def main():
    # Specify the source directory for the Fortran files
    source_dir = r'C:\Users\taci.ugraskan\source\repos\swatnet\Globals\src'
    #source_dir = r'C:\Users\taci.ugraskan\source\repos\swatnet\Globals\OG'

    # Create ProjectSettings with the source directory
    project_settings = ProjectSettings(src_dir=[Path(source_dir)])

    # Create the project instance
    project = Project(project_settings)

    # Correlate the project data (parses and processes the Fortran files)!
    project.correlate()

    procedures = project.get_procedures()

    #project.ncross_walk_type_dicts(procedures)

    project.cross_walk_type_dicts(procedures)

    # Extract metadata for each module in the project

    # Write the metadata to a JSON file
    project.buildjson(procedures)



    #print(f"Metadata has been written to {output_file}")

if __name__ == "__main__":
    main()
