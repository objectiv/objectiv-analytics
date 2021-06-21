###
### Container image that contains the objectiv-backend package, and can run that as collector
### behind gunicorn.
###


### Two steps build process
# We build the Docker Image in two steps:
# 1. Build the objectiv-backend python package in a build container
# 2. Install the objectiv-backend python package in the run container
#
# Both steps use the same base image, so that introduces some overhead. But the duplicated layers will be
# cached by docker, so it shouldn't impact build time much.


### Python Base Image
# We'll build our own python base image here based on ubuntu:20.04, as that is what most of our devs use.
# We could build this image in a separate Dockerfile and re-use it here. But building it here makes the
# build process simpler.
#

### Start of the Pyhthon-base-image part
FROM ubuntu:20.04 AS builder
## Install python, and prepare a virtual environment
# Using a virtual environment guarantees that we start with a clean slate, and python libraries that
# e.g. apt-get might install won't conflict with our specific requirements.txt
RUN \
    # Setting DEBIAN_FRONTEND prevents apt-get outputting warnings about not running interactively
    DEBIAN_FRONTEND="noninteractive" && \
    apt-get update && \
    apt-get install -y python3 python3-virtualenv && \
    apt-get -y autoremove && \
    apt-get -y clean && \
    rm -rf /var/lib/apt/lists/* && \
    virtualenv -p python3.8 /venv_python_3_8/

## Activate this virtualenv
# Instead of using /venv_python_3_8/bin/activate we'll set the variables that activate would set.
# The advantage of this approach is that it will work inside the running container too, even if we have
# a shell in which bin/activate wasn't read.
# The drawback of this manual method is that we cannot do 'deactivate', but that's of no importance to us.
ENV VIRTUAL_ENV="/venv_python_3_8/"
ENV PATH="${VIRTUAL_ENV}bin:${PATH}"
ENV PYTHONHOME=""
# Upgrade pip to what is currently the latest version
RUN pip --no-cache-dir install pip==21.1.* --upgrade
### End of the Pyhthon-base-image part

# Install dependencies needed to build package
COPY requirements-build.txt /tmp/requirements-build.txt
RUN pip --no-cache-dir install --require-hashes -r /tmp/requirements-build.txt && \
    rm /tmp/requirements-build.txt

# Copy files
WORKDIR /build_dir/
COPY setup.cfg pyproject.toml /build_dir/
COPY objectiv_backend/ /build_dir/objectiv_backend/

# Build package
RUN python3 -m build --wheel
# Done. Resulting file can be found in /build_dir/dist/objectiv_backend-${VERSION}-py3-none-any.whl


### Start of the Pyhthon-base-image part
# Make sure these lines are exactly the same as for the above builder image. That will allow docker to
# cache these layers efficiently.
FROM ubuntu:20.04 AS result
RUN \
    DEBIAN_FRONTEND="noninteractive" && \
    apt-get update && \
    apt-get install -y python3 python3-virtualenv && \
    apt-get -y autoremove && \
    apt-get -y clean && \
    rm -rf /var/lib/apt/lists/* && \
    virtualenv -p python3.8 /venv_python_3_8/
ENV VIRTUAL_ENV="/venv_python_3_8/"
ENV PATH="${VIRTUAL_ENV}bin:${PATH}"
ENV PYTHONHOME=""
RUN pip --no-cache-dir install pip==21.1.* --upgrade
### End of the Pyhthon-base-image part

RUN \
    mkdir -p /services && \
    mkdir -p /services/jsons/OK/ && \
    mkdir -p /services/jsons/NOK/ && \
    chown -R www-data /services/jsons
WORKDIR /services

# entrypoint scripts
COPY docker/*.sh /services/
COPY docker/gunicorn.conf.py /etc/
CMD /services/entry_point.sh

# python requirements
COPY requirements.txt /services/

RUN \
    pip --no-cache-dir install gunicorn && \
    pip --no-cache-dir install -r requirements.txt

# Install the objectiv-backend package
# Use a wildcard, because the exact package name depends on the current version
COPY --from=builder /build_dir/dist/* /tmp/
RUN pip --no-cache-dir install /tmp/objectiv_backend-*-py3-none-any.whl && \
    rm /tmp/*
