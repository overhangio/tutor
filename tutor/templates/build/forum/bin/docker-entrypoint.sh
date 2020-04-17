#!/bin/sh -e

export MONGOHQ_URL="mongodb://$MONGODB_AUTH$MONGODB_HOST:$MONGODB_PORT/cs_comments_service"

echo "Waiting for mongodb/elasticsearch..."
dockerize -wait tcp://$MONGODB_HOST:$MONGODB_PORT -wait $SEARCH_SERVER -wait-retry-interval 5s -timeout 600s

exec "$@"
