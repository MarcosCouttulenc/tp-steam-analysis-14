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

docker-image-query1-file:
	docker build -f ./query1_file/Dockerfile -t "query1_file:latest" .  # Construir imagen del query1 file
.PHONY: docker-image-query1-file

docker-image-query2-file:
	docker build -f ./query2_file/Dockerfile -t "query2_file:latest" .  # Construir imagen del query2 file
.PHONY: docker-image-query2-file

docker-image-query3-file:
	docker build -f ./query3_file/Dockerfile -t "query3_file:latest" .  # Construir imagen del query3 file
.PHONY: docker-image-query3-file

docker-image-query4-file:
	docker build -f ./query4_file/Dockerfile -t "query4_file:latest" .  # Construir imagen del query4 file
.PHONY: docker-image-query4-file

docker-image-query5-file:
	docker build -f ./query5_file/Dockerfile -t "query5_file:latest" .  # Construir imagen del query5 file
.PHONY: docker-image-query5-file

docker-image-database:
	docker build -f ./database/Dockerfile -t "database:latest" .  # Construir imagen de la base de datos
.PHONY: docker-image-database

docker-image-result-responser:
	docker build -f ./result_responser/Dockerfile -t "result_responser:latest" .  # Construir imagen de result-responser
.PHONY: docker-image-result-responser

docker-image-worker-review-validator:
	docker build -f ./worker_review_validator/Dockerfile -t "worker_review_validator:latest" .  # Construir imagen de worker_review_validator
.PHONY: docker-image-worker-review-validator

docker-image-worker-review-indie:
	docker build -f ./worker_review_indie/Dockerfile -t "worker_review_indie:latest" .  # Construir imagen de worker_review_indie
.PHONY: docker-image-worker-review-indie

docker-image-worker-review-positive:
	docker build -f ./worker_review_positive/Dockerfile -t "worker_review_positive:latest" .  # Construir imagen de worker_review_positive
.PHONY: docker-image-worker-review-positive

docker-image-worker-review-english:
	docker build -f ./worker_review_english/Dockerfile -t "worker_review_english:latest" .  # Construir imagen de worker_review_english
.PHONY: docker-image-worker-review-english

docker-image-worker-review-action:
	docker build -f ./worker_review_action/Dockerfile -t "worker_review_action:latest" .  # Construir imagen de worker_review_action
.PHONY: docker-image-worker-review-action

docker-image-health-checker:
	docker build -f ./healthchecker/Dockerfile -t "healthchecker:latest" .  # Construir imagen de healthchecker
.PHONY: docker-image-health-checker


docker-image: docker-image-server docker-image-client docker-image-worker-game-validator docker-image-worker-mac docker-image-worker-linux docker-image-worker-windows docker-image-worker-indie docker-image-worker-2010 docker-image-database docker-image-query1-file docker-image-result-responser docker-image-query2-file docker-image-worker-review-validator docker-image-worker-review-action docker-image-worker-review-english docker-image-worker-review-positive docker-image-worker-review-indie docker-image-query3-file docker-image-query4-file docker-image-query5-file docker-image-health-checker # Construir imágenes
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

docker-compose-logs-client:
	docker compose -f docker-compose-dev.yaml logs -f client
.PHONY: docker-compose-logs-client