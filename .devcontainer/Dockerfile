FROM mcr.microsoft.com/devcontainers/base:alpine

# Install system packages required for Ford development, including Graphviz
# Installing these in the image avoids needing root during postCreateCommand
USER root
RUN apk update \
    && apk add --no-cache \
        python3 \
        py3-pip \
        git \
        graphviz \
        gfortran \
        build-base \
    && rm -rf /var/cache/apk/*

# Upgrade pip in the image (keeps postCreateCommand shorter)
RUN python3 -m pip install --upgrade pip setuptools wheel || true

# Keep using the vscode user by default (devcontainer.json will set remoteUser)
USER vscode
