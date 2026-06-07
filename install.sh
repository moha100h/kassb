#!/bin/bash
set -e
echo '========================================'
echo '   Kassb Bot - Auto Installer'
echo '========================================'
echo ''
read -rp '>>> Bot Token: ' BOT_TOKEN
if [ -z "$BOT_TOKEN" ]; then echo 'ERROR: BOT_TOKEN empty'; exit 1; fi
read -rp '>>> Admin ID (numeric): ' ADMIN_ID
if ! echo "$ADMIN_ID" | grep -qE '^[0-9]+$'; then echo 'ERROR: ADMIN_ID must be numeric'; exit 1; fi
echo ''
echo '[INFO] Installing dependencies...'
apt-get update -qq && apt-get upgrade -y -qq
apt-get install -y -qq git curl docker.io docker-compose python3 python3-pip
systemctl enable docker --now 2>/dev/null || true
echo '[OK]   Dependencies installed.'
echo '[INFO] Cloning repository...'
mkdir -p /opt/kassb && cd /opt/kassb
rm -rf kassb
git clone -q https://github.com/moha100h/kassb.git
cd kassb
echo '[OK]   Repository cloned.'
echo '[INFO] Creating .env...'
cat > .env <<EOF
BOT_TOKEN=${BOT_TOKEN}
ADMIN_ID=${ADMIN_ID}
MAX_RESULTS=200
DB_PATH=/app/data/kassb.db
EXPORT_DIR=/app/data/exports
EOF
echo '[OK]   .env created.'
mkdir -p data/exports
echo '[INFO] Building Docker image...'
docker-compose build --no-cache
echo '[INFO] Starting bot...'
docker-compose up -d
sleep 5
STATUS=$(docker inspect --format='{{.State.Status}}' kassb_bot 2>/dev/null || echo 'unknown')
echo ''
echo '========================================'
echo '   Installation Complete!'
echo '========================================'
echo "  Bot status : $STATUS"
echo '  Logs: docker-compose -f /opt/kassb/kassb/docker-compose.yml logs -f'
echo '========================================'
