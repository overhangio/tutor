FROM docker.io/ruby:2.5.7-slim-stretch
MAINTAINER Overhang.io <contact@overhang.io>

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && \
  apt upgrade -y && \
  apt install -y git wget autoconf bison build-essential libssl-dev libyaml-dev libreadline6-dev zlib1g-dev libncurses5-dev libffi-dev libgdbm-dev

# Install dockerize to wait for mongodb/elasticsearch availability
ARG DOCKERIZE_VERSION=v0.6.1
RUN wget -O /tmp/dockerize.tar.gz https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf /tmp/dockerize.tar.gz \
    && rm /tmp/dockerize.tar.gz

# Create unprivileged "app" user
RUN useradd --home-dir /app --create-home --shell /bin/bash --uid 1000 app

# Copy custom scripts
COPY ./bin /app/bin
RUN chmod a+x /app/bin/*
ENV PATH :${PATH}

# From then on, run as unprivileged app user
USER app

# Install rake and bundler
ENV PATH "/app/bin:/app/.gem/ruby/2.5.0/bin:$PATH"
RUN gem install --user-install bundler --version 1.17.3
RUN gem install --user-install rake --version 13.0.1

# Install forum
RUN git clone https://github.com/edx/cs_comments_service.git --branch {{ OPENEDX_COMMON_VERSION }} --depth 1 /app/cs_comments_service
WORKDIR /app/cs_comments_service
RUN bundle install --deployment

ENTRYPOINT ["docker-entrypoint.sh"]

ENV SINATRA_ENV staging
ENV NEW_RELIC_ENABLE false
ENV API_KEY forumapikey
ENV SEARCH_SERVER "http://elasticsearch:9200"
ENV MONGODB_AUTH ""
ENV MONGOID_AUTH_MECH ""
ENV MONGODB_HOST "mongodb"
ENV MONGODB_PORT "27017"
ENV MONGODB_DATABASE "cs_comments_service"
EXPOSE 4567
CMD ./bin/unicorn -c config/unicorn_tcp.rb -I '.'
