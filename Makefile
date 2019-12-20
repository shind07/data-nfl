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


.PHONY: up
up:
	docker-compose up -d --build


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


.PHONY: auto-revision
auto-revision: up
	@echo creating auto-revision with message $(message)
	docker exec data-nfl-pipeline-app wait-for-port postgres
	docker exec data-nfl-pipeline-app alembic revision --autogenerate -m $(message)
	docker-compose down


.PHONY: migrate
migrate: up
	@echo migrating DB...
	docker exec data-nfl-pipeline-app wait-for-port postgres
	docker exec data-nfl-pipeline-app alembic upgrade head
	docker-compose down


.PHONY: run-app
run-app: up
	docker-compose logs -f -t >> app.log


.PHONY: run-pipeline
run-pipeline: up
	@echo "running $(IMAGE_NAME) container..."
	docker exec data-nfl-pipeline-app wait-for-port postgres
	docker exec data-nfl-pipeline-app python3 -m pipeline
	docker-compose down


.PHONY: shell
shell:
	docker-compose up -d --build
	docker exec data-nfl-pipeline-app wait-for-port postgres
	docker exec -it data-nfl-pipeline-app bash
	docker-compose down


.PHONY: test
test: build
	@echo testing...
	docker run $(IMAGE_NAME):latest python3 -m unittest discover tests
