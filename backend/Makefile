.PHONY=all clean python-dist docker-image

OBJ_PACKAGE_VERSION ?= 0.0.1
PACKAGE_NAME = dist/objectiv_backend-$(OBJ_PACKAGE_VERSION)-py3-none-any.whl
TAG ?= latest

all: docker-image

docker-image: python-dist
	docker build \
	--build-arg VERSION=$(OBJ_PACKAGE_VERSION) \
	--build-arg TAG=$(TAG) \
	-t objectiv/backend:$(TAG) -f docker/Dockerfile .

python-dist: $(PACKAGE_NAME)

$(PACKAGE_NAME): objectiv_backend
	echo $(OBJ_PACKAGE_VERSION) > objectiv_backend/VERSION
	python3 -m build --wheel

clean:
	rm $(PACKAGE_NAME)
