.PHONY=all build-all-images build-ds push-images

# default tag, used to tag images
# we use latest as default, for convenience
export TAG ?= latest

REVISION ?= $(shell git rev-parse HEAD)

# where to push docker images
CONTAINER_REPO=eu.gcr.io/objectiv-production

BUILD_ARGS := --build-arg TAG=$(TAG)

# by default we build all images
all: build-all-images

# what to build
build-all-images: build-backend build-ds

# ds images, build jupyter notebook with DB requirements
build-ds: build-ds-notebook

# what images to push
push-images: push-image-backend

# images are pushed, tagged both "latest" and $REVISION
push-image-%:
	$(eval MODULE = $(subst push-image-,,$@))
	$(eval URL=$(CONTAINER_REPO)/$(MODULE))
	docker tag objectiv/$(MODULE):$(TAG) $(URL):latest
	docker push $(URL)
	gcloud container images add-tag --quiet $(URL):latest $(URL):$(REVISION)


## build backend images
build-backend: build-docker-python3
	cd backend && make docker-image

build-ds-notebook:
	cd ds/docker/notebook && docker build -t objectiv/notebook:$(TAG) $(BUILD_ARGS) .

# build generic modules
build-docker-%:
	$(eval MODULE = $(subst build-docker-,,$@))
	cd docker/$(MODULE) && docker build -t objectiv/$(MODULE):$(TAG) $(BUILD_ARGS) .


# control stack through docker-compose
start:
	docker-compose up -d

stop:
	docker-compose down

update:
	docker-compose up -d --no-deps
