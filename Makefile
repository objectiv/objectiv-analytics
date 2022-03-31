.PHONY: all build-all-images build-ds push-images

# default tag, used to tag images
# we use latest as default, for convenience
export TAG ?= latest

REVISION ?= $(shell git rev-parse HEAD)

# where to push docker images
CONTAINER_REPO=eu.gcr.io/objectiv-production

# by default we build all images
all: build-all-images

# what to build
build-all-images: build-backend build-notebook

# what images to push
push-images: push-image-backend push-image-notebook

# images are pushed, tagged both "latest" and $REVISION
push-image-%:
	$(eval MODULE = $(subst push-image-,,$@))
	$(eval URL=$(CONTAINER_REPO)/$(MODULE))
	docker tag objectiv/$(MODULE):$(TAG) $(URL):test
	docker push $(URL):test
	gcloud container images add-tag --quiet $(URL):test $(URL):$(REVISION)


## build backend images
build-backend:
	cd backend && make docker-image

build-notebook:
	# first, build required packages and put them in the docker scope
	# for this to work, we need to be in a VENV with bach installed
	pip wheel --no-deps -w notebooks/docker/ ./bach
	pip wheel --no-deps -w notebooks/docker/ ./modelhub
	docker build -t objectiv/notebook -f notebooks/docker/Dockerfile notebooks

publish-tracker:
	cd tracker && make publish

# control stack through docker-compose
start:
	docker-compose up -d

stop:
	docker-compose down

update:
	docker-compose up -d --no-deps
