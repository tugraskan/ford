# Use Python 3.11 as base image (compatible with Ford's requirements)
FROM python:3.11-slim

# Install system dependencies
# - graphviz: Required for generating call graphs and diagrams
# - git: Useful for version control operations
# - gfortran: Fortran compiler for testing
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    graphviz \
    git \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Set the default command to bash
CMD ["/bin/bash"]
