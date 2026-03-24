#!/usr/bin/env bash
# Render build script
# Installs dependencies and system packages needed for mysqlclient

set -o errexit

# Install system-level dependencies for mysqlclient
apt-get update && apt-get install -y default-libmysqlclient-dev build-essential pkg-config

pip install --upgrade pip
pip install -r requirements.txt
