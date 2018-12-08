FROM ubuntu:16.04

############ common to lms & cms

# Install system requirements
RUN apt update && \
  apt upgrade -y && \
  # Global requirements
  apt install -y language-pack-en git python-virtualenv build-essential software-properties-common curl git-core libxml2-dev libxslt1-dev python-pip libmysqlclient-dev python-apt python-dev libxmlsec1-dev libfreetype6-dev swig gcc g++ && \
  # openedx requirements
  apt install -y gettext gfortran graphviz graphviz-dev libffi-dev libfreetype6-dev libgeos-dev libjpeg8-dev liblapack-dev libpng12-dev libsqlite3-dev libxml2-dev libxmlsec1-dev libxslt1-dev nodejs npm ntp pkg-config && \
  # Our requirements
  apt install -y mysql-client

# Install symlink so that we have access to 'node' binary without virtualenv.
# This replaces the "nodeenv" install.
RUN apt install -y nodejs-legacy

# Dockerize will be useful to wait for mysql DB availability
ENV DOCKERIZE_VERSION v0.6.1
RUN curl -L -o /tmp/dockerize.tar.gz https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf /tmp/dockerize.tar.gz \
    && rm /tmp/dockerize.tar.gz

# Static assets will reside in /openedx/data, themes in /openedx/themes and
# edx-platform will be checked-out in /openedx/
RUN mkdir /openedx /openedx/data /openedx/themes /openedx/edx-platform
WORKDIR /openedx/edx-platform

## Checkout edx-platform code
ARG EDX_PLATFORM_REPOSITORY=https://github.com/edx/edx-platform.git
ARG EDX_PLATFORM_VERSION=open-release/hawthorn.2
RUN git clone $EDX_PLATFORM_REPOSITORY --branch $EDX_PLATFORM_VERSION --depth 1 .

# Download extra locales to /openedx/locale
RUN cd /tmp \
    && curl -L -o openedx-i18n.tar.gz https://github.com/regisb/openedx-i18n/archive/hawthorn.tar.gz \
    && tar xzf /tmp/openedx-i18n.tar.gz \
    && mv openedx-i18n-hawthorn/edx-platform/locale/ /openedx/ \
    && rm -rf openedx-i18n*

# Copy convenient scripts
COPY ./bin/docker-entrypoint.sh /usr/local/bin/

# Install python requirements (clone source repos in a separate dir, otherwise
# will be overwritten when we mount edx-platform)
ENV NO_PYTHON_UNINSTALL 1
RUN pip install --src ../venv/src -r requirements/edx/base.txt
RUN pip install --src ../venv/src -r requirements/edx/development.txt

# Install patched version of ora2
RUN pip uninstall -y ora2 && \
    pip install --src ../venv/src git+https://github.com/regisb/edx-ora2.git@open-release/hawthorn.2#egg=ora2==2.1.17

# Install nodejs requirements
RUN npm set progress=false \
    && npm install
ENV PATH ./node_modules/.bin:${PATH}

# Install private requirements: this is useful for installing custom xblocks.
# In particular, to install xblocks from a private repository, clone the
# respositories to ./requirements on the host and add `-e ./myxblock/` to
# ./requirements/private.txt.
COPY ./requirements/ /openedx/requirements
RUN touch /openedx/requirements/private.txt \
    && pip install --src ../venv/src -r /openedx/requirements/private.txt

# Link configuration files to common /openedx/config folder, which should later
# be mounted as a volume. Note that this image will not be functional until
# config files have been mounted inside the container
RUN mkdir -p /openedx/config/universal/lms /openedx/config/universal/cms \
    && ln -s /openedx/config/universal/lms/ /openedx/edx-platform/lms/envs/universal \
    && ln -s /openedx/config/universal/cms/ /openedx/edx-platform/cms/envs/universal \
    && ln -s /openedx/config/lms.env.json /openedx/ \
    && ln -s /openedx/config/cms.env.json /openedx/ \
    && ln -s /openedx/config/lms.auth.json /openedx/ \
    && ln -s /openedx/config/cms.auth.json /openedx/
COPY settings/lms/*.py /openedx/config/universal/lms/
COPY settings/cms/*.py /openedx/config/universal/cms/

# Collect production assets. By default, only assets from the default theme
# will be processed. This makes the docker image lighter and faster to build.
# To compile assets from other themes, build the image with the THEMES
# argument: THEMES=dark-theme,edx.org
# Custom themes added to /openedx/themes can also be compiled.
# Here, we don't run "paver update_assets" which is slow, compiles all themes
# and requires a complex settings file. Instead, we decompose the commands
# and run each one individually to collect the production static assets to
# /openedx/data/staticfiles.
# 1. xmodule_assets: run xmodule.static_content.main, which lists all xblocks and generates webpack manifest in common/static/xmodule
# 2. pavelib.assets.process_npm_assets: copy libraries installed via npm to common/static/common/*/vendor
# 3. webpack: generate webpack-stats.json
# 4. compile_sass: compile each sass file individually with libsass.
# 5. pavelib.assets.collect_assets: run ./manage.py lms/cms collectstatic. This is the only command that requires a settings file.
RUN xmodule_assets common/static/xmodule \
    && python -c "import pavelib.assets; pavelib.assets.process_npm_assets()" \ 
    && STATIC_ROOT_LMS=/openedx/data/staticfiles STATIC_ROOT_CMS=/openedx/data/staticfiles/studio NODE_ENV=production ./node_modules/.bin/webpack --config=webpack.prod.config.js
ARG THEMES=open-edx
COPY ./themes/ /openedx/themes/
RUN paver compile_sass --theme-dirs=/openedx/edx-platform/themes,/openedx/themes --themes=$THEMES \
    && python -c "import pavelib.assets; pavelib.assets.collect_assets(['lms', 'cms'], 'universal.assets')"

# service variant is "lms" or "cms"
ENV SERVICE_VARIANT lms
ENV SETTINGS universal.production

# Entrypoint will fix permissions of all files and run commands as openedx
ENTRYPOINT ["docker-entrypoint.sh"]

# Run server
EXPOSE 8000
CMD gunicorn --name ${SERVICE_VARIANT} --bind=0.0.0.0:8000 --max-requests=1000 ${SERVICE_VARIANT}.wsgi:application
