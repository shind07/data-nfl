IMAGE_NAME=scottyhind/data-nfl-pipeline
IMAGE_TAG:=$(shell git rev-parse HEAD)
RUNNING_CONTAINER_NAME=data-nfl-pipeline-live

.PHONY: build
build:
	@echo building $(IMAGE_TAG) image...
	docker build \
		--cache-from $(IMAGE_NAME):build-cache \
		--cache-from $(IMAGE_NAME):latest \
		-t $(IMAGE_NAME):latest \
		-t $(IMAGE_NAME):$(IMAGE_TAG) ./app

.PHONY: cleanup
cleanup:
	docker image prune
	docker rm -v $(docker ps -a -q -f status=exited)
	docker image prune

.PHONY: db-shell
db-shell:
	docker-compose up -d --build
	docker exec data-nfl-pipeline-app wait-for-port postgres
	docker exec -it data-nfl-pipeline-db psql nfl -U postgres --host localhost
	docker-compose down

.PHONY: lint
lint:
	@find . -type f -name '*.yml' -exec yamllint  -f parsable {} +
	@find . -type f -name '*.yaml' -exec yamllint -f parsable {} +
	@flake8

.PHONY: pull
pull-cache:
	@echo pulling from build-cache
	docker pull $(IMAGE_NAME):build-cache || true

.PHONY: push
push: build
	@echo "pushing $(IMAGE_NAME) to docker hub..."
	docker tag $(IMAGE_NAME):$(IMAGE_TAG) $(IMAGE_NAME):build-cache
	docker push $(IMAGE_NAME):$(IMAGE_TAG) 
	docker push $(IMAGE_NAME):build-cache
	docker push $(IMAGE_NAME):latest

.PHONY: deploy
deploy: push
	docker tag $(IMAGE_NAME):latest $(IMAGE_NAME):$(IMAGE_TAG) 
	docker push $(IMAGE_NAME):$(IMAGE_TAG) 

.PHONY: run-app
run-app:
	docker-compose up -d --build
	docker-compose logs -f -t >> app.log

.PHONY: run-pipeline
run-pipeline:
	@echo "running $(IMAGE_NAME) container..."
	docker-compose up -d --build
	docker exec data-nfl-pipeline-app wait-for-port postgres
	docker exec data-nfl-pipeline-app python3 -m pipeline
	docker-compose down

.PHONY: shell
shell:
	docker run -d -v $(PWD)/app/data:/app/data --name $(RUNNING_CONTAINER_NAME) $(IMAGE_NAME) sleep infinity
	docker exec -it $(RUNNING_CONTAINER_NAME) bash
	docker stop $(RUNNING_CONTAINER_NAME)
	docker rm $(RUNNING_CONTAINER_NAME)

.PHONY: test
test: build
	@echo testing...
	docker run $(IMAGE_NAME):latest python3 -m unittest discover tests
