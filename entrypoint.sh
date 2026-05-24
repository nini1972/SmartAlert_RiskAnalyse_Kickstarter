#!/bin/bash
# Entrypoint script for SmartAlert Risk Analysis Kickstarter

set -e

echo "Starting SmartAlert Risk Analysis Kickstarter..."

# Start nginx in background
echo "Starting nginx..."
nginx -g "daemon off;" &
NGINX_PID=$!

# Start backend API server
echo "Starting backend API server..."
cd /backend
uvicorn server:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Function to handle shutdown
shutdown() {
    echo "Shutting down services..."
    kill $NGINX_PID $BACKEND_PID 2>/dev/null || true
    wait $NGINX_PID $BACKEND_PID 2>/dev/null || true
    echo "Services stopped."
}

# Trap SIGTERM and SIGINT
trap shutdown SIGTERM SIGINT

# Wait for any process to exit
wait -n

# If we get here, one of the processes has exited unexpectedly
echo "One of the services has exited. Shutting down..."
shutdown
exit 1