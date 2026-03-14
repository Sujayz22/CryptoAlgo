.PHONY: build run run-once logs stop clean shell

## Build the Docker image
build:
	DOCKER_HOST=unix:///var/run/docker.sock docker build -t cryptoalgo-bot .

## Start the scheduled bot (runs daily at 00:05 UTC)
run:
	DOCKER_HOST=unix:///var/run/docker.sock docker compose up -d

## Run one trading cycle right now (paper mode test)
run-once:
	DOCKER_HOST=unix:///var/run/docker.sock docker run --rm \
		--env-file .env \
		-v $(PWD)/logs:/app/logs \
		cryptoalgo-bot python main.py

## Tail live logs
logs:
	DOCKER_HOST=unix:///var/run/docker.sock docker compose logs -f

## Stop the bot
stop:
	DOCKER_HOST=unix:///var/run/docker.sock docker compose down

## Remove image and containers
clean:
	DOCKER_HOST=unix:///var/run/docker.sock docker compose down --rmi local

## Open a shell inside the container for debugging
shell:
	DOCKER_HOST=unix:///var/run/docker.sock docker run --rm -it \
		--env-file .env \
		-v $(PWD)/logs:/app/logs \
		cryptoalgo-bot /bin/bash
