.PHONY: all clean python-package docker-image tests base_schema

# Targets:
# docker-image:   Build docker image that includes installed python package. Only dependency is docker
# python-package: Build python package locally
# clean:          Remove python package built by python-package

# All (sub) directories with python files that are relevant for the python package.
# If a file in any of these directories changes then we want to rebuild the package.
PYTHON_DIRECTORIES=$(shell find objectiv_backend -type d)

# The name of the python package we'll build depends on the version
OBJ_PACKAGE_VERSION = $(shell cat objectiv_backend/VERSION)
PACKAGE_NAME = dist/objectiv_backend-$(OBJ_PACKAGE_VERSION)-py3-none-any.whl

# tag of the container image we'll build
TAG ?= $(shell date +%Y%m%d)

all: docker-image python-package

docker-image-local: base_schema
	docker build -t objectiv/backend:$(TAG) -f docker/Dockerfile .

docker-image:
	docker buildx build --pull --rm --no-cache --output type=image,push=true \
		--platform=linux/arm64,linux/amd64 --tag objectiv/backend:${TAG} -f docker/Dockerfile .

python-package: $(PACKAGE_NAME)

# copy base schema into the scope of the python package
# we always do this, to make sure, we're not using old stuff
base_schema:
	cp -f ../schema/base_schema.json5 ../schema/event_list.json5 objectiv_backend/schema/



$(PACKAGE_NAME): base_schema $(PYTHON_DIRECTORIES)
	python3 -m build --wheel

clean:
	rm dist/*
	rm -r build
	rm objectiv_backend/schema/base_schema.json5

tests:
	mypy objectiv_backend
	pytest tests
