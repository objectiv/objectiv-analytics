.PHONY: all build-all-images

# default tag, used to tag images
# default tag is current date
TAG ?= $(shell date +%Y%m%d)

# by default we build all images
all: build-all-images

# what to build
build-all-images: build-docker-backend-image-local build-docker-notebook-image-local

## build backend images
build-docker-backend-image-local:
	cd backend && make docker-image-local

build-docker-backend-image:
	cd backend&& make docker-image

build-docker-notebook-image-local:
	cd notebooks && docker build -t objectiv/notebook:${TAG} -f docker/Dockerfile .

build-docker-notebook-image:
	cd notebooks && docker buildx build --pull --rm --no-cache --output type=image,push=true \
		--platform=linux/arm64,linux/amd64 --tag objectiv/notebook:${TAG} -f docker/Dockerfile .


publish-tracker:
	cd tracker && make publish

# control stack through docker-compose
start:
	docker-compose up -d

stop:
	docker-compose down

update:
	docker-compose up -d --no-deps
