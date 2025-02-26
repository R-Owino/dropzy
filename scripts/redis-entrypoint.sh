#!/usr/bin/env bash
set -e

# Start Redis server in the background
redis-server --bind 0.0.0.0 &

# Wait for Redis to start
sleep 2

# Set the password using redis-cli
if ! redis-cli CONFIG SET requirepass "$REDIS_PASSWORD"; then
  echo "Failed to set Redis password."
  exit 1
fi

echo "Redis password set successfully."
wait
