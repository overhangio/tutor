FROM docker.io/ubuntu:20.04
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

RUN mkdir /openedx

# Install ruby-build for building specific version of ruby
# The ruby-build version should be periodically updated to reflect the latest release
ARG RUBY_BUILD_VERSION=v20200401
RUN git clone https://github.com/rbenv/ruby-build.git --branch $RUBY_BUILD_VERSION /openedx/ruby-build
WORKDIR /openedx/ruby-build
RUN PREFIX=/usr/local ./install.sh

# Install ruby and some specific dependencies
ARG RUBY_VERSION=2.5.7
ARG BUNDLER_VERSION=1.17.3
ARG RAKE_VERSION=13.0.1
RUN ruby-build $RUBY_VERSION /openedx/ruby
ENV PATH "/openedx/ruby/bin:$PATH"
RUN gem install bundler -v $BUNDLER_VERSION
RUN gem install rake -v $RAKE_VERSION

# Install forum
RUN git clone https://github.com/edx/cs_comments_service.git --branch {{ OPENEDX_COMMON_VERSION }} --depth 1 /openedx/cs_comments_service
WORKDIR /openedx/cs_comments_service
RUN bundle install --deployment

COPY ./bin /openedx/bin
RUN chmod a+x /openedx/bin/*
ENV PATH /openedx/bin:${PATH}
ENTRYPOINT ["docker-entrypoint.sh"]

ENV SINATRA_ENV staging
ENV NEW_RELIC_ENABLE false
ENV API_KEY forumapikey
ENV SEARCH_SERVER "http://elasticsearch:9200"
ENV MONGODB_AUTH ""
ENV MONGOID_AUTH_MECH ""
ENV MONGODB_HOST "mongodb"
ENV MONGODB_PORT "27017"
EXPOSE 4567
CMD ./bin/unicorn -c config/unicorn_tcp.rb -I '.'
