#!/bin/sh -e

if test "$MONGODB_PROTOCOL" = 'mongodb+srv'; then
  export MONGOHQ_URL="$MONGODB_PROTOCOL://$MONGODB_AUTH$MONGODB_HOST/cs_comments_service$MONGODB_PARAMS"
  MONGO_WAIT=""
  services='elasticsearch'
else
  export MONGOHQ_URL="$MONGODB_PROTOCOL://$MONGODB_AUTH$MONGODB_HOST:$MONGODB_PORT/cs_comments_service$MONGODB_PARAMS"
  MONGO_WAIT="-wait tcp://$MONGODB_HOST:$MONGODB_PORT"
  services='mongodb/elasticsearch'
fi

echo "Waiting for $services"
dockerize $MONGO_WAIT -wait $SEARCH_SERVER -wait-retry-interval 5s -timeout 600s

exec "$@"
