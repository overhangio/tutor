FROM ubuntu:16.04
MAINTAINER Overhang.io <contact@overhang.io>

############ common to lms & cms

# Install system requirements
RUN apt update && \
    # Global requirements
    apt install -y language-pack-en git python-virtualenv build-essential software-properties-common curl git-core libxml2-dev libxslt1-dev python-virtualenv libmysqlclient-dev python-apt python-dev libxmlsec1-dev libfreetype6-dev swig gcc g++ \
    # openedx requirements
    gettext gfortran graphviz graphviz-dev libffi-dev libfreetype6-dev libgeos-dev libjpeg8-dev liblapack-dev libpng12-dev libsqlite3-dev libxml2-dev libxmlsec1-dev libxslt1-dev lynx nodejs npm ntp pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Dockerize will be useful to wait for mysql DB availability
ARG DOCKERIZE_VERSION=v0.6.1
RUN curl -L -o /tmp/dockerize.tar.gz https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf /tmp/dockerize.tar.gz \
    && rm /tmp/dockerize.tar.gz

# Checkout edx-platform code
ARG EDX_PLATFORM_REPOSITORY=https://github.com/edx/edx-platform.git
ARG EDX_PLATFORM_VERSION=open-release/ironwood.2
RUN mkdir -p /openedx/edx-platform && \
    git clone $EDX_PLATFORM_REPOSITORY --branch $EDX_PLATFORM_VERSION --depth 1 /openedx/edx-platform
WORKDIR /openedx/edx-platform

# Apply patches
# Certificates XSS vulnerability https://github.com/edx/edx-platform/pull/20904
RUN curl https://github.com/edx/edx-platform/commit/b33db2c548a1a530510d785f7659c78783a187fa.patch | git apply -

# Download extra locales to /openedx/locale
# TODO upgrade this to ironwood
RUN cd /tmp \
    && curl -L -o openedx-i18n.tar.gz https://github.com/openedx/openedx-i18n/archive/hawthorn.tar.gz \
    && tar xzf /tmp/openedx-i18n.tar.gz \
    && mv openedx-i18n-hawthorn/edx-platform/locale/ /openedx/locale/ \
    && rm -rf openedx-i18n*

# Install python requirements (clone source repos in a separate dir, otherwise
# they will be overwritten when we mount edx-platform)
ENV NO_PYTHON_UNINSTALL 1
RUN virtualenv /openedx/venv
ENV PATH /openedx/venv/bin:${PATH}
ENV VIRTUAL_ENV /openedx/venv/
RUN pip install setuptools==39.0.1 pip==9.0.3
RUN pip install -r requirements/edx/development.txt

# Install patched version of ora2
RUN pip uninstall -y ora2 && \
    pip install git+https://github.com/overhangio/edx-ora2.git@2.2.0-patched#egg=ora2==2.2.0

# Install a recent version of nodejs
RUN nodeenv /openedx/nodeenv --node=8.9.3 --prebuilt
ENV PATH /openedx/nodeenv/bin:${PATH}

# Install nodejs requirements
RUN npm set progress=false \
    && npm install
ENV PATH ./node_modules/.bin:${PATH}

# Install private requirements: this is useful for installing custom xblocks.
COPY ./requirements/ /openedx/requirements
RUN cd /openedx/requirements/ && pip install -r ./private.txt

# Create folder that will store *.env.json and *.auth.json files, as well as
# the tutor-specific settings files.
RUN mkdir -p /openedx/config ./lms/envs/tutor ./cms/envs/tutor
ENV CONFIG_ROOT /openedx/config
COPY settings/lms/*.py ./lms/envs/tutor/
COPY settings/cms/*.py ./cms/envs/tutor/

# Copy scripts
COPY ./bin /openedx/bin
RUN chmod a+x /openedx/bin/*
ENV PATH /openedx/bin:${PATH}

{{ patch("openedx-dockerfile-pre-assets") }}

# Collect production assets. By default, only assets from the default theme
# will be processed. This makes the docker image lighter and faster to build.
# Only the custom themes added to /openedx/themes will be compiled.
# Here, we don't run "paver update_assets" which is slow, compiles all themes
# and requires a complex settings file. Instead, we decompose the commands
# and run each one individually to collect the production static assets to
# /openedx/staticfiles.
RUN openedx-assets xmodule \
    && openedx-assets npm \
    && openedx-assets webpack --env=prod \
    && openedx-assets common
COPY ./themes/ /openedx/themes/
RUN openedx-assets themes \
    && openedx-assets collect --settings=tutor.assets

# Create a data directory, which might be used (or not)
RUN mkdir /openedx/data

# service variant is "lms" or "cms"
ENV SERVICE_VARIANT lms
ENV SETTINGS tutor.production

{{ patch("openedx-dockerfile") }}

# Entrypoint will fix permissions of all files and run commands as openedx
ENTRYPOINT ["docker-entrypoint.sh"]

# Run server
COPY gunicorn_conf.py /openedx/gunicorn_conf.py
EXPOSE 8000
CMD gunicorn -c /openedx/gunicorn_conf.py --name ${SERVICE_VARIANT} --bind=0.0.0.0:8000 --max-requests=1000 ${SERVICE_VARIANT}.wsgi:application
