#!/bin/sh -e

export MONGOHQ_URL="mongodb://$MONGODB_AUTH$MONGODB_HOST:$MONGODB_PORT/$MONGODB_DATABASE"
# the search server variable was renamed after the upgrade to elasticsearch 7
export SEARCH_SERVER_ES7="$SEARCH_SERVER"

echo "Waiting for mongodb/elasticsearch..."
dockerize -wait tcp://$MONGODB_HOST:$MONGODB_PORT -wait $SEARCH_SERVER -wait-retry-interval 5s -timeout 600s

exec "$@"
