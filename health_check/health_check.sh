#!/bin/bash


LOG_FILE="/var/data/log/health_check.log"

http_response=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL")
if [ "$http_response" == "200" ]; then
    echo "$(date): API at $SERVICE_URL is reachable - Health check passed" >> "$LOG_FILE"
else
    echo "$(date): API at $SERVICE_URL is unreachable - Health check failed (HTTP $http_response)" >> "$LOG_FILE"
fi

cat /var/data/log/health_check.log
