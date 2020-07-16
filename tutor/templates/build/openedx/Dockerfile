FROM docker.io/ubuntu:16.04
MAINTAINER Overhang.io <contact@overhang.io>

############ common to lms & cms

# Install system requirements
RUN apt update && \
    # Global requirements
    apt install -y language-pack-en git build-essential software-properties-common curl git-core libmysqlclient-dev libxml2-dev libxslt1-dev libxmlsec1-dev libfreetype6-dev swig gcc g++ \
    # pyenv/python requirements
    libbz2-dev libreadline-dev \
    # openedx requirements
    gettext gfortran graphviz graphviz-dev libffi-dev libfreetype6-dev libgeos-dev libjpeg8-dev liblapack-dev libpng12-dev libsqlite3-dev libxml2-dev libxmlsec1-dev libxslt1-dev lynx nodejs npm ntp pkg-config \
    && rm -rf /var/lib/apt/lists/*
ENV LC_ALL en_US.UTF-8

# Install python with pyenv
ARG PYTHON_VERSION=3.5.9
ENV PYENV_ROOT /opt/pyenv
RUN git clone https://github.com/pyenv/pyenv $PYENV_ROOT --branch v1.2.18 --depth 1 \
    && $PYENV_ROOT/bin/pyenv install $PYTHON_VERSION

# Dockerize will be useful to wait for mysql DB availability
ARG DOCKERIZE_VERSION=v0.6.1
RUN curl -L -o /tmp/dockerize.tar.gz https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf /tmp/dockerize.tar.gz \
    && rm /tmp/dockerize.tar.gz

# Checkout edx-platform code
ARG EDX_PLATFORM_REPOSITORY=https://github.com/edx/edx-platform.git
ARG EDX_PLATFORM_VERSION=open-release/juniper.2
RUN mkdir -p /openedx/edx-platform && \
    git clone $EDX_PLATFORM_REPOSITORY --branch $EDX_PLATFORM_VERSION --depth 1 /openedx/edx-platform
WORKDIR /openedx/edx-platform

# Patch edx-platform
# Get rid of lepl-related warnings
# https://github.com/edx/edx-platform/pull/24059
# https://github.com/overhangio/edx-platform/tree/overhangio/lepl-rfc6266-warning
RUN curl https://github.com/overhangio/edx-platform/commit/5f21bbe77056d71ca61b97b6badcff3c1a31b858.patch | git apply -
# Fix creation of LTI provider objects
# https://github.com/edx/edx-platform/pull/24055
# https://github.com/overhangio/edx-platform/tree/regisb/fix-lti-provider-admin
RUN curl https://github.com/overhangio/edx-platform/commit/089b26eed0302ed1f9a5b24c5f3e563dd44abb04.patch | git apply -
# Fix problem viewing when CSMH is disabled
# https://github.com/edx/edx-platform/pull/24237
# https://github.com/overhangio/edx-platform/tree/overhangio/fix-no-csmh
RUN curl https://github.com/overhangio/edx-platform/commit/6dbf2eddf7a4563c04c3b51edf5e131106d69e19.patch | git apply -

# Download extra locales to /openedx/locale/contrib/locale
RUN cd /tmp \
    && curl -L -o openedx-i18n.tar.gz https://github.com/openedx/openedx-i18n/archive/juniper.2.tar.gz \
    && tar xzf /tmp/openedx-i18n.tar.gz \
    && mkdir -p /openedx/locale/contrib \
    && mv openedx-i18n-juniper.2/edx-platform/locale /openedx/locale/contrib \
    && rm -rf openedx-i18n*

# Install python requirements in a virtualenv
RUN $PYENV_ROOT/versions/$PYTHON_VERSION/bin/pyvenv /openedx/venv
ENV PATH /openedx/venv/bin:${PATH}
ENV VIRTUAL_ENV /openedx/venv/
RUN pip install setuptools==44.1.0 pip==20.0.2 wheel==0.34.2
RUN pip install -r requirements/edx/base.txt

# Install patched version of ora2
RUN pip install https://github.com/overhangio/edx-ora2/archive/overhangio/boto2to3.zip

# Install scorm xblock
RUN pip install "openedx-scorm-xblock<11.0.0,>=10.0.0"

# Install a recent version of nodejs
RUN nodeenv /openedx/nodeenv --node=12.13.0 --prebuilt
ENV PATH /openedx/nodeenv/bin:${PATH}

# Install nodejs requirements
ARG NPM_REGISTRY=https://registry.npmjs.org/
RUN npm install --verbose --registry=$NPM_REGISTRY
ENV PATH ./node_modules/.bin:${PATH}

# Install private requirements: this is useful for installing custom xblocks.
COPY ./requirements/ /openedx/requirements
RUN cd /openedx/requirements/ \
  && touch ./private.txt \
  && pip install -r ./private.txt

# Create folder that will store lms/cms.env.json files, as well as
# the tutor-specific settings files.
RUN mkdir -p /openedx/config ./lms/envs/tutor ./cms/envs/tutor
COPY revisions.yml /openedx/config/
ENV LMS_CFG /openedx/config/lms.env.json
ENV STUDIO_CFG /openedx/config/cms.env.json
ENV REVISION_CFG /openedx/config/revisions.yml
COPY settings/lms/*.py ./lms/envs/tutor/
COPY settings/cms/*.py ./cms/envs/tutor/

# Copy user-specific locales to /openedx/locale/user/locale and compile them
RUN mkdir -p /openedx/locale/user
COPY ./locale/ /openedx/locale/user/locale/
RUN cd /openedx/locale/user && \
    django-admin.py compilemessages -v1
# Compile i18n strings: in Ironwood, js locales are not properly compiled out of the box
# and we need to do a pass ourselves. Also, we need to compile the djangojs.js files for
# the downloaded locales.
RUN ./manage.py lms --settings=tutor.i18n compilejsi18n
RUN ./manage.py cms --settings=tutor.i18n compilejsi18n

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
ENV NO_PYTHON_UNINSTALL 1
ENV NO_PREREQ_INSTALL 1
# We need to rely on a separate openedx-assets command to accelerate asset processing.
# For instance, we don't want to run all steps of asset collection every time the theme
# is modified.
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

# Entrypoint will set right environment variables
ENTRYPOINT ["docker-entrypoint.sh"]

# Run server
COPY gunicorn_conf.py /openedx/gunicorn_conf.py
EXPOSE 8000
CMD gunicorn -c /openedx/gunicorn_conf.py --name ${SERVICE_VARIANT} --bind=0.0.0.0:8000 --max-requests=1000 --access-logfile - ${SERVICE_VARIANT}.wsgi:application
