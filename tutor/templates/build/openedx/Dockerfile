# syntax=docker/dockerfile:1
###### Minimal image with base system requirements for most stages
FROM docker.io/python:3.11.9-slim-bookworm as minimal
LABEL maintainer="Overhang.io <contact@overhang.io>"

ENV DEBIAN_FRONTEND=noninteractive
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt update && \
    apt install -y locales python3-dev build-essential curl git
ENV LC_ALL en_US.UTF-8
{{ patch("openedx-dockerfile-minimal") }}

# Create virtualenv
RUN python -m venv /openedx/venv

###### Checkout edx-platform code
FROM minimal as code
ARG EDX_PLATFORM_REPOSITORY={{ EDX_PLATFORM_REPOSITORY }}
ARG EDX_PLATFORM_VERSION={{ EDX_PLATFORM_VERSION }}
RUN mkdir -p /openedx/edx-platform && \
    git clone $EDX_PLATFORM_REPOSITORY --branch $EDX_PLATFORM_VERSION --depth 1 /openedx/edx-platform
WORKDIR /openedx/edx-platform

# Identify tutor user to apply patches using git
RUN git config --global user.email "tutor@overhang.io" \
  && git config --global user.name "Tutor"

{%- if patch("openedx-dockerfile-git-patches-default") %}
# Custom edx-platform patches
{{ patch("openedx-dockerfile-git-patches-default") }}
{%- elif EDX_PLATFORM_VERSION == "master" %}
# Patches in nightly node
{%- else %}
# Patches in non-nightly mode
# Prevent course structure cache infinite growth
# https://github.com/openedx/edx-platform/pull/34210
RUN curl -fsSL https://github.com/openedx/edx-platform/commit/ad201cd664b6c722cbefcbda23ae390c06daf621.patch | git am
{%- endif %}

{# Example: RUN curl -fsSL https://github.com/openedx/edx-platform/commit/<GITSHA1>.patch | git am #}
{{ patch("openedx-dockerfile-post-git-checkout") }}

##### Empty layer with just the repo at the root.
# This is useful when overriding the build context with a host repo:
# docker build --build-context edx-platform=/path/to/edx-platform
FROM scratch as edx-platform
COPY --from=code /openedx/edx-platform /

{# Create empty layers for all bind-mounted directories #}
{% for name in iter_mounted_directories(MOUNTS, "openedx") %}
FROM scratch as mnt-{{ name }}
{% endfor %}

###### Install python requirements in virtualenv
FROM minimal as python-requirements
ENV PATH /openedx/venv/bin:${PATH}
ENV VIRTUAL_ENV /openedx/venv/
ENV XDG_CACHE_HOME /openedx/.cache

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt update \
    && apt install -y software-properties-common default-libmysqlclient-dev libxmlsec1-dev libgeos-dev

# Install the right version of pip/setuptools
RUN --mount=type=cache,target=/openedx/.cache/pip,sharing=shared \
    pip install \
    # https://pypi.org/project/setuptools/
    # https://pypi.org/project/pip/
    # https://pypi.org/project/wheel/
    setuptools==69.1.1 pip==24.0 wheel==0.43.0

# Install base requirements
RUN --mount=type=bind,from=edx-platform,source=/requirements/edx/base.txt,target=/openedx/edx-platform/requirements/edx/base.txt \
    --mount=type=cache,target=/openedx/.cache/pip,sharing=shared \
    pip install -r /openedx/edx-platform/requirements/edx/base.txt

# Install extra requirements
RUN --mount=type=cache,target=/openedx/.cache/pip,sharing=shared \
    pip install \
    # Use redis as a django cache https://pypi.org/project/django-redis/
    django-redis==5.4.0 \
    # uwsgi server https://pypi.org/project/uWSGI/
    uwsgi==2.0.24

{{ patch("openedx-dockerfile-post-python-requirements") }}

# Install scorm xblock
RUN pip install "openedx-scorm-xblock>=17.0.0,<18.0.0"

{% for extra_requirements in OPENEDX_EXTRA_PIP_REQUIREMENTS %}
RUN --mount=type=cache,target=/openedx/.cache/pip,sharing=shared \
    pip install '{{ extra_requirements }}'
{% endfor %}

###### Install nodejs with nodeenv in /openedx/nodeenv
FROM python as nodejs-requirements
ENV PATH /openedx/nodeenv/bin:/openedx/venv/bin:${PATH}

# Install nodeenv with the version provided by edx-platform
# https://github.com/openedx/edx-platform/blob/master/requirements/edx/base.txt
# https://github.com/pyenv/pyenv/releases
RUN pip install nodeenv==1.8.0
RUN nodeenv /openedx/nodeenv --node=18.20.1 --prebuilt

# Install nodejs requirements
ARG NPM_REGISTRY={{ NPM_REGISTRY }}
WORKDIR /openedx/edx-platform
RUN --mount=type=bind,from=edx-platform,source=/package.json,target=/openedx/edx-platform/package.json \
    --mount=type=bind,from=edx-platform,source=/package-lock.json,target=/openedx/edx-platform/package-lock.json \
    --mount=type=bind,from=edx-platform,source=/scripts/copy-node-modules.sh,target=/openedx/edx-platform/scripts/copy-node-modules.sh \
    --mount=type=cache,target=/root/.npm,sharing=shared \
    npm clean-install --no-audit --registry=$NPM_REGISTRY

###### Production image with system and python requirements
FROM minimal as production

# Install system requirements
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt update \
    && apt install -y gettext gfortran graphviz graphviz-dev libffi-dev libfreetype6-dev libgeos-dev libjpeg62-turbo-dev liblapack-dev default-libmysqlclient-dev libpng-dev libsqlite3-dev libxmlsec1-dev lynx default-mysql-client ntp pkg-config rdfind

# From then on, run as unprivileged "app" user
# Note that this must always be different from root (APP_USER_ID=0)
ARG APP_USER_ID=1000
RUN if [ "$APP_USER_ID" = 0 ]; then echo "app user may not be root" && false; fi
RUN useradd --no-log-init --home-dir /openedx --create-home --shell /bin/bash --uid ${APP_USER_ID} app
USER ${APP_USER_ID}

# https://hub.docker.com/r/powerman/dockerize/tags
COPY --link --from=docker.io/powerman/dockerize:0.19.0 /usr/local/bin/dockerize /usr/local/bin/dockerize
COPY --chown=app:app --from=edx-platform / /openedx/edx-platform
COPY --chown=app:app --from=python-requirements /openedx/venv /openedx/venv
COPY --chown=app:app --from=python-requirements /mnt /mnt
COPY --chown=app:app --from=nodejs-requirements /openedx/nodeenv /openedx/nodeenv
COPY --chown=app:app --from=nodejs-requirements /openedx/edx-platform/node_modules /openedx/node_modules

# Symlink node_modules such that we can bind-mount the edx-platform repository
RUN ln -s /openedx/node_modules /openedx/edx-platform/node_modules

ENV PATH /openedx/venv/bin:./node_modules/.bin:/openedx/nodeenv/bin:${PATH}
ENV VIRTUAL_ENV /openedx/venv/
WORKDIR /openedx/edx-platform

{# Install auto-mounted directories as Python packages. #}
{% for name in iter_mounted_directories(MOUNTS, "openedx") %}
COPY --from=mnt-{{ name }} --chown=app:app / /mnt/{{ name }}
RUN pip install -e "/mnt/{{ name }}"
{% endfor %}

# We install edx-platform here because it creates an egg-info folder in the current
# repo. We need both the source code and the virtualenv to run this command.
RUN pip install -e .

# Create folder that will store lms/cms.env.yml files, as well as
# the tutor-specific settings files.
RUN mkdir -p /openedx/config ./lms/envs/tutor ./cms/envs/tutor
COPY --chown=app:app revisions.yml /openedx/config/
ENV LMS_CFG /openedx/config/lms.env.yml
ENV CMS_CFG /openedx/config/cms.env.yml
ENV REVISION_CFG /openedx/config/revisions.yml
COPY --chown=app:app settings/lms/*.py ./lms/envs/tutor/
COPY --chown=app:app settings/cms/*.py ./cms/envs/tutor/

# Pull latest translations via atlas
RUN ./manage.py lms --settings=tutor.i18n pull_plugin_translations --verbose --repository='{{ ATLAS_REPOSITORY }}' --revision='{{ ATLAS_REVISION }}' {{ ATLAS_OPTIONS }}
RUN ./manage.py lms --settings=tutor.i18n pull_xblock_translations --repository='{{ ATLAS_REPOSITORY }}' --revision='{{ ATLAS_REVISION }}' {{ ATLAS_OPTIONS }}
RUN atlas pull --repository='{{ ATLAS_REPOSITORY }}' --revision='{{ ATLAS_REVISION }}' {{ ATLAS_OPTIONS }} \
    translations/edx-platform/conf/locale:conf/locale \
    translations/studio-frontend/src/i18n/messages:conf/plugins-locale/studio-frontend
RUN ./manage.py lms --settings=tutor.i18n compile_xblock_translations
RUN ./manage.py cms --settings=tutor.i18n compile_xblock_translations
RUN ./manage.py lms --settings=tutor.i18n compile_plugin_translations
RUN ./manage.py lms --settings=tutor.i18n compilemessages -v1
RUN ./manage.py lms --settings=tutor.i18n compilejsi18n
RUN ./manage.py cms --settings=tutor.i18n compilejsi18n

# Copy scripts
COPY --chown=app:app ./bin /openedx/bin
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
COPY --chown=app:app ./themes/ /openedx/themes/
RUN openedx-assets themes \
    && openedx-assets collect --settings=tutor.assets \
    # De-duplicate static assets with symlinks
    && rdfind -makesymlinks true -followsymlinks true /openedx/staticfiles/

# Create a data directory, which might be used (or not)
RUN mkdir /openedx/data

# If this "canary" file is missing from a container, then that indicates that a
# local edx-platform was bind-mounted into that container, thus overwriting the
# canary. This information is useful during edx-platform initialisation.
RUN echo \
  "This copy of edx-platform was built into a Docker image." \
  > bindmount-canary

# service variant is "lms" or "cms"
ENV SERVICE_VARIANT lms
ENV DJANGO_SETTINGS_MODULE lms.envs.tutor.production

{{ patch("openedx-dockerfile") }}

EXPOSE 8000

###### Intermediate image with dev/test dependencies
FROM production as development

# Install useful system requirements (as root)
USER root
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt update && \
    apt install -y vim iputils-ping dnsutils telnet
USER app

# Install dev python requirements
RUN --mount=type=cache,target=/openedx/.cache/pip,sharing=shared \
    pip install -r requirements/edx/development.txt
# https://pypi.org/project/ipdb/
# https://pypi.org/project/ipython (8.12.x for Python 3.8)
RUN --mount=type=cache,target=/openedx/.cache/pip,sharing=shared \
    pip install ipdb==0.13.13 ipython==8.12.3

{# Re-install mounted requirements, otherwise they will be superseded by upstream reqs #}
{% for name in iter_mounted_directories(MOUNTS, "openedx") %}
COPY --from=mnt-{{ name }} --chown=app:app / /mnt/{{ name }}
RUN pip install -e "/mnt/{{ name }}"
{% endfor %}

# Add ipdb as default PYTHONBREAKPOINT
ENV PYTHONBREAKPOINT=ipdb.set_trace

# Recompile static assets: in development mode all static assets are stored in edx-platform,
# and the location of these files is stored in webpack-stats.json. If we don't recompile
# static assets, then production assets will be served instead.
RUN rm -r /openedx/staticfiles && \
    mkdir /openedx/staticfiles && \
    openedx-assets webpack --env=dev

{{ patch("openedx-dev-dockerfile-post-python-requirements") }}

# Default django settings
ENV DJANGO_SETTINGS_MODULE lms.envs.tutor.development

CMD ./manage.py $SERVICE_VARIANT runserver 0.0.0.0:8000

###### Final image with production cmd
FROM production as final

# Default amount of uWSGI processes
ENV UWSGI_WORKERS=2

# Copy the default uWSGI configuration
COPY --chown=app:app settings/uwsgi.ini .

# Run server
CMD uwsgi uwsgi.ini

{{ patch("openedx-dockerfile-final") }}

