include .env

build:
	echo "building container for $(APP_NAME)..."
	docker build -t $(APP_NAME) .

run: build
	echo "running $(APP_NAME) container..."
	docker run -it --env-file .env $(APP_NAME)
