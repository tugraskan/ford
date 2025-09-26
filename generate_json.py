import json
from ford.fortran_project import Project
from ford.settings import ProjectSettings
from ford.external_project import get_module_metadata
from pathlib import Path


def main():
    # Specify the source directory for the Fortran files
    source_dir = 'test_src'  # Use our test directory

    # Create ProjectSettings with the source directory
    project_settings = ProjectSettings(src_dir=[Path(source_dir)])
    #project_settings.dbg = False

    # Create the project instance
    project = Project(project_settings)

    # Correlate the project data (parses and processes the Fortran files)!
    project.correlate()

    print(f"Project data has been correlated for source directory: {source_dir}")

    procedures = project.get_procedures()
    
    # Get all procedures from modules and programs too
    all_procedures = []
    for module in project.modules:
        if hasattr(module, 'subroutines'):
            all_procedures.extend(module.subroutines)
        if hasattr(module, 'functions'):
            all_procedures.extend(module.functions)
    for program in project.programs:
        all_procedures.append(program)
    
    # Use all_procedures if available, otherwise use procedures
    procs_to_use = all_procedures if all_procedures else procedures

    project.cross_walk_type_dicts(procs_to_use)

    # Extract metadata for each module in the project

    # Write the metadata to a JSON file
    project.procedures_fvar_to_json(procs_to_use)

    project.procedures_io_to_json(procs_to_use)

    project.procedures_call_to_json(procs_to_use)
    
    # Generate the automated.csv file
    csv_file = project.procedures_to_csv(procs_to_use)
    if csv_file:
        print(f"Generated automated.csv file at: {csv_file}")
    else:
        print("Failed to generate CSV file")

    #output_file = project_settings.output_file if hasattr(project_settings, 'output_file') else "output.json"
    #print(f"Metadata has been written to {output_file}")

if __name__ == "__main__":
    main()