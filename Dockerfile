# Use Python 3.11 as base image (compatible with Ford's requirements)
FROM python:3.11-slim

# Install system dependencies
# - graphviz: Required for generating call graphs and diagrams
# - git: Useful for version control operations
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    graphviz \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Copy only necessary files for installation
# This allows better layer caching during development
COPY pyproject.toml setup.py README.md LICENSE ./
COPY ford/ ./ford/

# Install Ford and its dependencies
# Install in editable mode for development
RUN pip install --no-cache-dir -e .[docs,tests]

# Copy the rest of the project files
COPY . .

# Set the default command to bash
CMD ["/bin/bash"]
