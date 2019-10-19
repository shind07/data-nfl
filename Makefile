include .env


.PHONY: build-nflscrapr
build-nflscrapr:
	echo "building $(NFLSCRAPR_APP_NAME) container..."
	docker build -f nflscrapr/Dockerfile -t $(NFLSCRAPR_APP_NAME) ./nflscrapr

.PHONY: build
build:
	echo "building container for $(APP_NAME)..."
	docker build -t $(APP_NAME) .


.PHONY: run-nflscrapr
run-nflscrapr: build-nflscrapr
	docker run -v ${PWD}/data:/app/data $(NFLSCRAPR_APP_NAME) games --year=2019 --type=reg


.PHONY: run
run: build
	echo "running $(APP_NAME) container..."
	docker run -it --env-file .env -v ${PWD}/data:/app/data $(APP_NAME) 
