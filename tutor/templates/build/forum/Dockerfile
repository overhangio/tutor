FROM ubuntu:18.04
MAINTAINER Overhang.io <contact@overhang.io>

RUN mkdir /openedx

RUN apt update && \
  apt upgrade -y && \
  apt install -y git wget autoconf bison build-essential libssl-dev libyaml-dev libreadline6-dev zlib1g-dev libncurses5-dev libffi-dev libgdbm-dev

# Install dockerize to wait for mongodb/elasticsearch availability
ARG DOCKERIZE_VERSION=v0.6.1
RUN wget -O /tmp/dockerize.tar.gz https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf /tmp/dockerize.tar.gz \
    && rm /tmp/dockerize.tar.gz

# Install ruby-build for building specific version of ruby
RUN git clone https://github.com/rbenv/ruby-build.git /openedx/ruby-build
WORKDIR /openedx/ruby-build
RUN PREFIX=/usr/local ./install.sh

# Install ruby and some specific dependencies
ENV RUBY_VERSION 2.4.1
ENV BUNDLER_VERSION 1.11.2
ENV RAKE_VERSION 10.4.2
RUN ruby-build $RUBY_VERSION /openedx/ruby
ENV PATH "/openedx/ruby/bin:$PATH"
RUN gem install bundler -v $BUNDLER_VERSION
RUN gem install rake -v $RAKE_VERSION
# gem upgrade must come after bundler/rake install
RUN gem install rubygems-update && update_rubygems

# Install forum
RUN git clone https://github.com/edx/cs_comments_service.git --branch open-release/ironwood.2 --depth 1 /openedx/cs_comments_service
WORKDIR /openedx/cs_comments_service
RUN bundle install --deployment

COPY ./bin /openedx/bin
RUN chmod a+x /openedx/bin/*
ENV PATH /openedx/bin:${PATH}
ENTRYPOINT ["docker-entrypoint.sh"]

ENV RACK_ENV staging
ENV NEW_RELIC_ENABLE false
ENV API_KEY forumapikey
ENV SEARCH_SERVER "http://elasticsearch:9200"
ENV MONGODB_AUTH ""
ENV MONGODB_HOST "mongodb"
ENV MONGODB_PORT "27017"
ENV MONGOHQ_URL "mongodb://$MONGODB_AUTH$MONGODB_HOST:$MONGODB_PORT/cs_comments_service"
EXPOSE 4567
CMD ./bin/unicorn -c config/unicorn_tcp.rb -I '.'
