SHELL := /bin/bash
PWD := $(shell pwd)

GIT_REMOTE = github.com/7574-sistemas-distribuidos/docker-compose-init

default: build

all:

deps:
	go mod tidy
	# go mod vendor  NO HACE FALTA CREO

build: deps
	GOOS=linux go build -o bin/client github.com/7574-sistemas-distribuidos/docker-compose-init/client
.PHONY: build

docker-image-server:
	docker build -f ./server/Dockerfile -t "server:latest" .  # Construir imagen del servidor
.PHONY: docker-image-server

docker-image-client:
	docker build -f ./client/Dockerfile -t "client:latest" .  # Construir imagen del cliente
.PHONY: docker-image-client

docker-image-worker-mac:
	docker build -f ./worker_mac/Dockerfile -t "worker_mac:latest" .  # Construir imagen del worker mac
.PHONY: docker-image-worker-mac

docker-image-worker-linux:
	docker build -f ./worker_linux/Dockerfile -t "worker_linux:latest" .  # Construir imagen del worker linux
.PHONY: docker-image-worker-linux

docker-image-worker-windows:
	docker build -f ./worker_windows/Dockerfile -t "worker_windows:latest" .  # Construir imagen del worker windows
.PHONY: docker-image-worker-windows

docker-image-worker-game-validator:
	docker build -f ./worker_game_validator/Dockerfile -t "worker_game_validator:latest" .  # Construir imagen del worker game validator
.PHONY: docker-image-worker-game-validator

docker-image-worker-indie:
	docker build -f ./worker_indie/Dockerfile -t "worker_indie:latest" .  # Construir imagen del worker indie
.PHONY: docker-image-worker-indie

docker-image-worker-2010:
	docker build -f ./worker_2010/Dockerfile -t "worker_2010:latest" .  # Construir imagen del worker 2010
.PHONY: docker-image-worker-2010

docker-image-query1-reducer:
	docker build -f ./query1_reducer/Dockerfile -t "query1_reducer:latest" .  # Construir imagen del query1 reducer
.PHONY: docker-image-query1-reducer

docker-image-query2-reducer:
	docker build -f ./query2_reducer/Dockerfile -t "query2_reducer:latest" .  # Construir imagen del query2 reducer
.PHONY: docker-image-query2-reducer

docker-image: docker-image-server docker-image-client docker-image-worker-game-validator docker-image-worker-mac docker-image-worker-linux docker-image-worker-windows docker-image-query1-reducer docker-image-query2-reducer docker-image-worker-indie docker-image-worker-2010 # Construir imágenes
.PHONY: docker-image

docker-compose-up: docker-image
	docker compose -f docker-compose-dev.yaml up -d --build  # Levantar ambos servicios
.PHONY: docker-compose-up

docker-compose-down:
	docker compose -f docker-compose-dev.yaml stop -t 1
	docker compose -f docker-compose-dev.yaml down
.PHONY: docker-compose-down

docker-compose-logs:
	docker compose -f docker-compose-dev.yaml logs -f
.PHONY: docker-compose-logs
