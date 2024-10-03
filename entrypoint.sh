#!/bin/bash
set -e

# Maximum number of restarts
MAX_RESTARTS=5
restart_count=0

while [ $restart_count -lt $MAX_RESTARTS ]; do
    echo "Starting the application (Attempt $((restart_count + 1)))"
    python -m app.main || true
    
    restart_count=$((restart_count + 1))
    
    if [ $restart_count -lt $MAX_RESTARTS ]; then
        echo "Application crashed. Restarting in 10 seconds..."
        sleep 10
    else
        echo "Maximum restart attempts reached. Exiting."
    fi
done

echo "Application failed to start after $MAX_RESTARTS attempts. Please check the logs and fix the issue."