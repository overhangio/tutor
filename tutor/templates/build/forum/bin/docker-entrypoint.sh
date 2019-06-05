#!/bin/sh -e

echo "Waiting for mongodb/elasticsearch..."
dockerize -wait tcp://$MONGODB_HOST:$MONGODB_PORT -wait $SEARCH_SERVER/content -wait-retry-interval 5s -timeout 600s

exec "$@"
