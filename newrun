from fortran_project import Project
from ford.settings import ProjectSettings

# Load settings and initialize the project
settings = ProjectSettings("project.yml")
project = Project(settings)

# Extract and print derived types
for dtype in project.types:
    print(f"Derived Type: {dtype.name}")
    for member in dtype.variables:
        print(f"  - Name: {member.name}, Type: {member.vartype}, Initial Value: {member.initial_value}, Description: {member.description}")

# Extract and print module variables
for module in project.modules:
    print(f"Module: {module.name}")
    for variable in module.variables:
        print(f"  - Name: {variable.name}, Type: {variable.vartype}, Initial Value: {variable.initial_value}, Description: {variable.description}")
