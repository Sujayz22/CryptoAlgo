# CryptoAlgo Bot Deployment Guide

This guide covers deploying the Delta Exchange Trading Bot to an Ubuntu-based VPS or EC2 instance.

## Prerequisites

1. An Ubuntu 22.04 or newer instance (1 vCPU, 1GB RAM is completely fine since the bot is lightweight).
2. SSH access to the instance.
3. Your Delta Exchange API Key and Secret.

---

## Step 1: Server Initial Setup

Connect to your instance via SSH:
```bash
ssh user@your_server_ip
```

Update your package lists and install basic dependencies:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl ufw
```

*(Optional but recommended)* Set up a basic firewall to allow only SSH (and other ports if you need them):
```bash
sudo ufw allow OpenSSH
sudo ufw enable
```

---

## Step 2: Install Docker and Docker Compose

The easiest way to install Docker is via their official convenience script:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

Add your current user to the `docker` group so you don't need to use `sudo` for every command:
```bash
sudo usermod -aG docker $USER
```
*(Note: You will need to log out and log back in for this to take effect, or run `newgrp docker`)*

Install Docker Compose v2 (usually included with the script above, but good to verify):
```bash
docker compose version
```

---

## Step 3: Clone the Repository

Clone your trading bot repository to the server:
```bash
# Example using HTTPS format
git clone https://github.com/your-username/CryptoAlgo.git
cd CryptoAlgo
```

---

## Step 4: Configure the Environment

Create your `.env` file based on your local setup:
```bash
nano .env
```

Add your configuration variables. Make sure to set `PAPER_MODE=False` if you want it to place real trades (or keep it `True` to just simulate on the server first).

```ini
API_KEY=your_delta_api_key
API_SECRET=your_delta_api_secret

# Use testnet URL or production URL
DELTA_BASE_URL=https://cdn-ind.testnet.deltaex.org
# DELTA_BASE_URL=https://api.delta.exchange # For live trading

# Set to False to place REAL trades
PAPER_MODE=False
```
*(Press `Ctrl+O`, `Enter`, `Ctrl+X` to save and exit nano)*

---

## Step 5: Build and Run the Bot

Your repository includes a `docker-compose.yml` and a `Makefile` that make this simple. Since you are on a Linux host, you can use the standard docker compose commands.

Build the Docker image:
```bash
docker compose build
```

Start the bot in detached mode (it will run continuously in the background):
```bash
docker compose up -d
```

---

## Step 6: Monitoring and Logs

The bot uses Docker with a built-in JSON file logging driver, and it also mounts a local `./logs` directory.

To view live logs from the container:
```bash
docker compose logs -f
```

Or you can use the Makefile shortcut if you prefer:
```bash
make logs
```

To see the bot's internal application logs saved to the file:
```bash
cat logs/trading.log
# Or tail the file to watch it live:
tail -f logs/trading.log
```

---

## Updating the Bot

When you make changes to your logic and push them to your repository, here is how to update the running instance:

```bash
cd CryptoAlgo
git pull origin main

# Rebuild the image with the new code
docker compose build

# Recreate the container (this causes a brief downtime as it swaps the container)
docker compose up -d
```

## Useful Commands (Makefile Reference)

- `make build` : Builds the docker image
- `make run` : Starts the scheduled bot in the background
- `make run-once` : Runs a single trading cycle and exits (great for testing)
- `make logs` : Follows the live docker logs
- `make stop` : Stops the background bot
- `make clean` : Stops the bot and removes the built images to free space
