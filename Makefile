IMAGE_NAME=scottyhind/data-nfl-pipeline
IMAGE_TAG:=$(shell git rev-parse HEAD)
RUNNING_CONTAINER_NAME=data-nfl-pipeline-live

.PHONY: build
build:
	@echo building $(IMAGE_TAG) image...
	docker build \
		--cache-from $(IMAGE_NAME):build-cache \
		-t $(IMAGE_NAME):$(IMAGE_TAG) \
		-t $(IMAGE_NAME):latest .

.PHONY: lint
lint:
	@flake8

.PHONY: push
push: build
	@echo "pushing $(IMAGE_NAME):$(IMAGE_TAG) to docker hub..."
	docker push $(IMAGE_NAME)

.PHONY: run
run-pipeline:
	@echo "running $(APP_NAME) container..."
	docker run \
		-it \
		--env-file .env \
		-v $$(PWD)/data:/app/data \
		$(IMAGE_NAME) python3 pipeline.py

.PHONY: pull
pull-cache:
	docker pull $(IMAGE_NAME):build-cache

.PHONY: shell
shell:
	docker run -d --name $(RUNNING_CONTAINER_NAME) $(IMAGE_NAME)
	docker exec -it $(RUNNING_CONTAINER_NAME) bash
	docker stop $(RUNNING_CONTAINER_NAME)
	docker rm $(RUNNING_CONTAINER_NAME)

.PHONY: test
test: build
	@echo testing...
	docker run $(IMAGE_NAME) python3 -m unittest discover tests

blah:
	@echo $(shell pwd)
