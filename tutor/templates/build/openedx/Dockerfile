# syntax=docker/dockerfile:1.4


###########################################################################################################################
############## MINIMAL
############## Minimal image with base system requirements for most stages
###########################################################################################################################
FROM docker.io/ubuntu:20.04 as minimal
LABEL maintainer="Overhang.io <contact@overhang.io>"

ENV DEBIAN_FRONTEND=noninteractive
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt update && \
    apt install -y build-essential curl git language-pack-en
ENV LC_ALL en_US.UTF-8
{{ patch("openedx-dockerfile-minimal") }}


###########################################################################################################################
############## PYTHON
############## Install python with pyenv in /opt/pyenv and create virtualenv in /openedx/venv
###########################################################################################################################
FROM minimal as python

# https://github.com/pyenv/pyenv/wiki/Common-build-problems#prerequisites
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
	apt update && \
    apt install -y libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
    xz-utils tk-dev libffi-dev liblzma-dev python-openssl git \
    software-properties-common libmysqlclient-dev libxmlsec1-dev libgeos-dev

ARG PYTHON_VERSION=3.8.15
ENV PYENV_ROOT /opt/pyenv
ENV PATH /openedx/venv/bin:${PATH}
ENV VIRTUAL_ENV /openedx/venv/
ENV XDG_CACHE_HOME /openedx/.cache

# Install pyenv
# https://www.python.org/downloads/
# https://github.com/pyenv/pyenv/releases
RUN git clone https://github.com/pyenv/pyenv $PYENV_ROOT --branch v2.3.17 --depth 1

# Install Python
RUN $PYENV_ROOT/bin/pyenv install $PYTHON_VERSION

# Create virtualenv
RUN $PYENV_ROOT/versions/$PYTHON_VERSION/bin/python -m venv /openedx/venv

# Install the right version of pip/setuptools
RUN --mount=type=cache,target=/openedx/.cache/pip,sharing=shared \
    pip install \
    # https://pypi.org/project/setuptools/
    # https://pypi.org/project/pip/
    # https://pypi.org/project/wheel/
    setuptools==67.6.1 pip==23.0.1. wheel==0.40.0


###########################################################################################################################
############## CODE
###########################################################################################################################
FROM minimal as code

###### Checkout edx-platform code
ARG EDX_PLATFORM_REPOSITORY={{ EDX_PLATFORM_REPOSITORY }}
ARG EDX_PLATFORM_VERSION={{ EDX_PLATFORM_VERSION }}
RUN echo break cache 200
RUN mkdir -p /openedx/edx-platform && \
    git clone $EDX_PLATFORM_REPOSITORY --branch $EDX_PLATFORM_VERSION --depth 1 /openedx/edx-platform
WORKDIR /openedx/edx-platform

# Identify tutor user to apply patches using git
RUN git config --global user.email "tutor@overhang.io" \
  && git config --global user.name "Tutor"

{%- if patch("openedx-dockerfile-git-patches-default") %}
# Custom edx-platform patches
{{ patch("openedx-dockerfile-git-patches-default") }}
{%- else %}
# Patch edx-platform
{%- endif %}

{# Example: RUN curl -fsSL https://github.com/openedx/edx-platform/commit/<GITSHA1>.patch | git am #}
{{ patch("openedx-dockerfile-post-git-checkout") }}

# TODO: Temporary
# Apply these edx-platform changes which have not yet merged.
RUN curl -fsSL https://github.com/openedx/edx-platform/pull/32835.patch | git am


###########################################################################################################################
############## EDX-PLATFORM
############## Empty layer with just the repo at the root.
############## This is useful when overriding the build context with a host repo:
############## docker build --build-context edx-platform=/path/to/edx-platform
###########################################################################################################################
FROM scratch as edx-platform
COPY --from=code /openedx/edx-platform /


###########################################################################################################################
############## LOCALES
###########################################################################################################################
###### Download extra locales to /openedx/locale/contrib/locale
FROM minimal as locales
ARG OPENEDX_I18N_VERSION={{ OPENEDX_COMMON_VERSION }}
RUN cd /tmp \
    && curl -L -o openedx-i18n.tar.gz https://github.com/openedx/openedx-i18n/archive/$OPENEDX_I18N_VERSION.tar.gz \
    && tar xzf /tmp/openedx-i18n.tar.gz \
    && mkdir -p /openedx/locale/contrib \
    && mv openedx-i18n-*/edx-platform/locale /openedx/locale/contrib \
    && rm -rf openedx-i18n*



###########################################################################################################################
############## FRONTEND REQUIREMENTS
###########################################################################################################################
FROM python as requirements-frontend

WORKDIR /openedx/edx-platform

# Install python reqs for building assets
RUN --mount=type=bind,from=edx-platform,source=/requirements/edx/assets.txt,target=requirements/edx/assets.txt \
    pip install -r requirements/edx/assets.txt

# Set up node env
ENV PATH /openedx/nodeenv/bin:/openedx/venv/bin:${PATH}
RUN nodeenv /openedx/nodeenv --node=16.14.0 --prebuilt

# Install nodejs requirements
ARG NPM_REGISTRY={{ NPM_REGISTRY }}
RUN --mount=type=bind,from=edx-platform,source=/package.json,target=package.json \
    --mount=type=bind,from=edx-platform,source=/package-lock.json,target=package-lock.json \
    --mount=type=bind,from=edx-platform,source=/scripts/copy-node-modules.sh,target=scripts/copy-node-modules.sh \
    --mount=type=cache,target=/root/.npm,sharing=shared \
    npm clean-install --no-audit --registry=$NPM_REGISTRY

# Set up static root.
# By default, CMS static root is assumed to be $STUDIO_ROOT_LMS/studio.
ENV STATIC_ROOT_LMS=/openedx/staticfiles
RUN mkdir -p "$STATIC_ROOT_LMS"


###########################################################################################################################
############## BUNDLES: PRODUCTION
###########################################################################################################################
FROM requirements-frontend as bundles-production

# Run webpack
RUN --mount=type=bind,from=edx-platform,source=/package.json,target=package.json \
    --mount=type=bind,from=edx-platform,source=/package-lock.json,target=/openedx/edx-platform/package-lock.json \
    --mount=type=bind,from=edx-platform,source=/.babelrc,target=.babelrc \
    --mount=type=bind,from=edx-platform,source=/webpack.common.config.js,target=webpack.common.config.js \
    --mount=type=bind,from=edx-platform,source=/webpack-config/file-lists.js,target=webpack-config/file-lists.js \
    --mount=type=bind,from=edx-platform,source=/webpack.dev.config.js,target=webpack.dev.config.js \
    --mount=type=bind,from=edx-platform,source=/webpack.prod.config.js,target=webpack.prod.config.js \
    --mount=type=bind,from=edx-platform,source=/webpack.builtinblocks.config.js,target=webpack.builtinblocks.config.js \
    --mount=type=bind,from=edx-platform,source=/cms/djangoapps/pipeline_js/js/xmodule.js,target=cms/djangoapps/pipeline_js/js/xmodule.js \
    --mount=type=bind,from=edx-platform,source=/cms/static,target=cms/static \
    --mount=type=bind,from=edx-platform,source=/cms/templates/,target=cms/templates/ \
    --mount=type=bind,from=edx-platform,source=/common/static/js/,target=common/static/js \
    --mount=type=bind,from=edx-platform,source=/common/static/common,target=common/static/common \
    --mount=type=bind,from=edx-platform,source=/lms/djangoapps/discussion/static,target=lms/djangoapps/discussion/static \
    --mount=type=bind,from=edx-platform,source=/lms/djangoapps/instructor/static,target=lms/djangoapps/instructor/static \
    --mount=type=bind,from=edx-platform,source=/lms/djangoapps/support/static/support,target=lms/djangoapps/support/static/support \
    --mount=type=bind,from=edx-platform,source=/lms/djangoapps/teams/static,target=lms/djangoapps/teams/static \
    --mount=type=bind,from=edx-platform,source=/lms/static/,target=lms/static/ \
    --mount=type=bind,from=edx-platform,source=/lms/templates/,target=lms/templates/ \
    --mount=type=bind,from=edx-platform,source=/openedx/features/announcements/static,target=openedx/features/announcements/static \
    --mount=type=bind,from=edx-platform,source=/openedx/features/course_bookmarks/static,target=openedx/features/course_bookmarks/static \
    --mount=type=bind,from=edx-platform,source=/openedx/features/course_experience/static,target=openedx/features/course_experience/static \
    --mount=type=bind,from=edx-platform,source=/openedx/features/course_search/static,target=openedx/features/course_search/static \
    --mount=type=bind,from=edx-platform,source=/openedx/features/learner_profile/static,target=openedx/features/learner_profile/static \
    --mount=type=bind,from=edx-platform,source=/xmodule/assets,target=xmodule/assets \
    --mount=type=bind,from=edx-platform,source=/xmodule/js,target=xmodule/js \
    npm run webpack


###########################################################################################################################
############## BUNDLES: DEVELOPMENT
###########################################################################################################################
FROM requirements-frontend as bundles-development

# Run webpack
RUN --mount=type=bind,from=edx-platform,source=/package.json,target=package.json \
    --mount=type=bind,from=edx-platform,source=/package-lock.json,target=/openedx/edx-platform/package-lock.json \
    --mount=type=bind,from=edx-platform,source=/.babelrc,target=.babelrc \
    --mount=type=bind,from=edx-platform,source=/webpack.common.config.js,target=webpack.common.config.js \
    --mount=type=bind,from=edx-platform,source=/webpack-config/file-lists.js,target=webpack-config/file-lists.js \
    --mount=type=bind,from=edx-platform,source=/webpack.dev.config.js,target=webpack.dev.config.js \
    --mount=type=bind,from=edx-platform,source=/webpack.prod.config.js,target=webpack.prod.config.js \
    --mount=type=bind,from=edx-platform,source=/webpack.builtinblocks.config.js,target=webpack.builtinblocks.config.js \
    --mount=type=bind,from=edx-platform,source=/cms/djangoapps/pipeline_js/js/xmodule.js,target=cms/djangoapps/pipeline_js/js/xmodule.js \
    --mount=type=bind,from=edx-platform,source=/cms/static,target=cms/static \
    --mount=type=bind,from=edx-platform,source=/cms/templates/,target=cms/templates/ \
    --mount=type=bind,from=edx-platform,source=/common/static/js/,target=common/static/js \
    --mount=type=bind,from=edx-platform,source=/common/static/common,target=common/static/common \
    --mount=type=bind,from=edx-platform,source=/lms/djangoapps/discussion/static,target=lms/djangoapps/discussion/static \
    --mount=type=bind,from=edx-platform,source=/lms/djangoapps/instructor/static,target=lms/djangoapps/instructor/static \
    --mount=type=bind,from=edx-platform,source=/lms/djangoapps/support/static/support,target=lms/djangoapps/support/static/support \
    --mount=type=bind,from=edx-platform,source=/lms/djangoapps/teams/static,target=lms/djangoapps/teams/static \
    --mount=type=bind,from=edx-platform,source=/lms/static/,target=lms/static/ \
    --mount=type=bind,from=edx-platform,source=/lms/templates/,target=lms/templates/ \
    --mount=type=bind,from=edx-platform,source=/openedx/features/announcements/static,target=openedx/features/announcements/static \
    --mount=type=bind,from=edx-platform,source=/openedx/features/course_bookmarks/static,target=openedx/features/course_bookmarks/static \
    --mount=type=bind,from=edx-platform,source=/openedx/features/course_experience/static,target=openedx/features/course_experience/static \
    --mount=type=bind,from=edx-platform,source=/openedx/features/course_search/static,target=openedx/features/course_search/static \
    --mount=type=bind,from=edx-platform,source=/openedx/features/learner_profile/static,target=openedx/features/learner_profile/static \
    --mount=type=bind,from=edx-platform,source=/xmodule/assets,target=xmodule/assets \
    --mount=type=bind,from=edx-platform,source=/xmodule/js,target=xmodule/js \
    npm run webpack-dev


###########################################################################################################################
############## CSS: PRODUCTION
###########################################################################################################################
FROM requirements-frontend as css-production

ENV PATH ./node_modules/.bin:${PATH}

# Compile default CSS
RUN --mount=type=bind,from=edx-platform,source=/package.json,target=package.json \
    --mount=type=bind,from=edx-platform,source=/scripts/compile_sass.py,target=scripts/compile_sass.py \
    --mount=type=bind,from=edx-platform,source=/common/static,target=common/static \
    --mount=type=bind,from=edx-platform,source=/lms/static/sass,target=lms/static/sass \
    --mount=type=bind,from=edx-platform,source=/lms/static/sass/partials,target=lms/static/sass/partials \
    --mount=type=bind,from=edx-platform,source=/lms/static/certificates/sass,target=lms/static/certificates/sass \
    --mount=type=bind,from=edx-platform,source=/cms/static/sass,target=cms/static/sass \
    --mount=type=bind,from=edx-platform,source=/cms/static/sass/partials,target=cms/static/sass/partials \
    --mount=type=bind,from=edx-platform,source=/xmodule/assets,target=xmodule/assets \
    npm run compile-sass -- --skip-themes

# Compile themed CSS
ENV EDX_PLATFORM_THEME_DIRS=/openedx/themes
COPY --chown=app:app ./themes/ /openedx/themes/
RUN --mount=type=bind,from=edx-platform,source=/package.json,target=package.json \
    --mount=type=bind,from=edx-platform,source=/scripts/compile_sass.py,target=scripts/compile_sass.py \
    --mount=type=bind,from=edx-platform,source=/common/static,target=common/static \
    --mount=type=bind,from=edx-platform,source=/lms/static/sass,target=lms/static/sass \
    --mount=type=bind,from=edx-platform,source=/lms/static/sass/partials,target=lms/static/sass/partials \
    --mount=type=bind,from=edx-platform,source=/lms/static/certificates/sass,target=lms/static/certificates/sass \
    --mount=type=bind,from=edx-platform,source=/cms/static/sass,target=cms/static/sass \
    --mount=type=bind,from=edx-platform,source=/cms/static/sass/partials,target=cms/static/sass/partials \
    --mount=type=bind,from=edx-platform,source=/xmodule/assets,target=xmodule/assets \
    npm run compile-sass -- --skip-default


###########################################################################################################################
############## CSS: DEVELOPMENT
###########################################################################################################################
FROM requirements-frontend as css-development

ENV PATH ./node_modules/.bin:${PATH}

# Compile default CSS
RUN --mount=type=bind,from=edx-platform,source=/package.json,target=package.json \
    --mount=type=bind,from=edx-platform,source=/scripts/compile_sass.py,target=scripts/compile_sass.py \
    --mount=type=bind,from=edx-platform,source=/common/static,target=common/static \
    --mount=type=bind,from=edx-platform,source=/lms/static/sass,target=lms/static/sass \
    --mount=type=bind,from=edx-platform,source=/lms/static/sass/partials,target=lms/static/sass/partials \
    --mount=type=bind,from=edx-platform,source=/lms/static/certificates/sass,target=lms/static/certificates/sass \
    --mount=type=bind,from=edx-platform,source=/cms/static/sass,target=cms/static/sass \
    --mount=type=bind,from=edx-platform,source=/cms/static/sass/partials,target=cms/static/sass/partials \
    --mount=type=bind,from=edx-platform,source=/xmodule/assets,target=xmodule/assets \
    npm run compile-sass -- --skip-themes --env=dev

# Compile themed CSS
ENV EDX_PLATFORM_THEME_DIRS=/openedx/themes
COPY --chown=app:app ./themes/ /openedx/themes/
RUN --mount=type=bind,from=edx-platform,source=/package.json,target=package.json \
    --mount=type=bind,from=edx-platform,source=/scripts/compile_sass.py,target=scripts/compile_sass.py \
    --mount=type=bind,from=edx-platform,source=/common/static,target=common/static \
    --mount=type=bind,from=edx-platform,source=/lms/static/sass,target=lms/static/sass \
    --mount=type=bind,from=edx-platform,source=/lms/static/sass/partials,target=lms/static/sass/partials \
    --mount=type=bind,from=edx-platform,source=/lms/static/certificates/sass,target=lms/static/certificates/sass \
    --mount=type=bind,from=edx-platform,source=/cms/static/sass,target=cms/static/sass \
    --mount=type=bind,from=edx-platform,source=/cms/static/sass/partials,target=cms/static/sass/partials \
    --mount=type=bind,from=edx-platform,source=/xmodule/assets,target=xmodule/assets \
    npm run compile-sass -- --skip-default --env=dev


###########################################################################################################################
############## APPLICATION REQUIREMENTS
###########################################################################################################################
FROM requirements-frontend as requirements-application

# Install base requirements
RUN --mount=type=bind,from=edx-platform,source=/requirements/edx/base.txt,target=/openedx/edx-platform/requirements/edx/base.txt \
    --mount=type=cache,target=/openedx/.cache/pip,sharing=shared \
	pip install -r /openedx/edx-platform/requirements/edx/base.txt

# Install extra requirements
RUN --mount=type=cache,target=/openedx/.cache/pip,sharing=shared \
    pip install \
    # Use redis as a django cache https://pypi.org/project/django-redis/
    django-redis==5.2.0 \
    # uwsgi server https://pypi.org/project/uWSGI/
    uwsgi==2.0.21

{{ patch("openedx-dockerfile-post-python-requirements") }}

# Install private requirements: this is useful for installing custom xblocks.
COPY ./requirements/ /openedx/requirements
RUN --mount=type=cache,target=/openedx/.cache/pip,sharing=shared \
    cd /openedx/requirements/ \
    && touch ./private.txt \
    && pip install -r ./private.txt

{% for extra_requirements in OPENEDX_EXTRA_PIP_REQUIREMENTS %}RUN --mount=type=cache,target=/openedx/.cache/pip,sharing=shared pip install '{{ extra_requirements }}'
{% endfor %}


###########################################################################################################################
############## PRODUCTION REQUIREMENTS
############## Simply take the general requirements, and remove everything related to libsass.
############## Alternatively, we could have based requirements-application on minimal, thus keeping libsass out of it,
############## BUT that would have required requirements-development to recompile libsass, which is slow.
###########################################################################################################################
FROM requirements-application as requirements-production

RUN rm -r /openedx/venv/lib/python3.8/site-packages/*sass*


###########################################################################################################################
############## DEVELOPMENT REQUIREMENTS
###########################################################################################################################
FROM requirements-application as requirements-development

# Install dev requirements
RUN --mount=type=bind,from=edx-platform,source=/requirements/edx/development.txt,target=/openedx/edx-platform/requirements/edx/development.txt \
    --mount=type=cache,target=/openedx/.cache/pip,sharing=shared \
    pip install -r /openedx/edx-platform/requirements/edx/development.txt


###########################################################################################################################
############## APPLICATION
############## Application image with system and python requirements.
############## Basis for final prod and dev images.
###########################################################################################################################
FROM minimal as application

# Install system requirements
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
	apt update \
    && apt install -y gettext gfortran graphviz graphviz-dev libffi-dev libfreetype6-dev libgeos-dev libjpeg8-dev liblapack-dev libmysqlclient-dev libpng-dev libsqlite3-dev libxmlsec1-dev lynx mysql-client ntp pkg-config rdfind

# From then on, run as unprivileged "app" user
# Note that this must always be different from root (APP_USER_ID=0)
ARG APP_USER_ID=1000
RUN if [ "$APP_USER_ID" = 0 ]; then echo "app user may not be root" && false; fi
RUN useradd --home-dir /openedx --create-home --shell /bin/bash --uid ${APP_USER_ID} app
USER ${APP_USER_ID}

# https://hub.docker.com/r/powerman/dockerize/tags
COPY --link --from=docker.io/powerman/dockerize:0.19.0 /usr/local/bin/dockerize /usr/local/bin/dockerize
COPY --chown=app:app --from=edx-platform / /openedx/edx-platform
COPY --chown=app:app --from=locales /openedx/locale /openedx/locale
COPY --chown=app:app --from=python /opt/pyenv /opt/pyenv
COPY --chown=app:app --from=requirements-production /openedx/venv /openedx/venv
COPY --chown=app:app --from=requirements-production /openedx/requirements /openedx/requirements
COPY --chown=app:app --from=requirements-frontend /openedx/nodeenv /openedx/nodeenv
COPY --chown=app:app --from=requirements-frontend /openedx/edx-platform/node_modules /openedx/node_modules
COPY --chown=app:app --from=requirements-frontend /openedx/edx-platform/common/static/node_copies /openedx/edx-platform/common/static/node_copies

# Symlink node_modules such that we can bind-mount the edx-platform repository
RUN ln -s /openedx/node_modules /openedx/edx-platform/node_modules

ENV PATH /openedx/venv/bin:./node_modules/.bin:/openedx/nodeenv/bin:${PATH}
ENV VIRTUAL_ENV /openedx/venv/
WORKDIR /openedx/edx-platform

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

# Copy user-specific locales to /openedx/locale/user/locale and compile them
RUN mkdir /openedx/locale/user
COPY --chown=app:app ./locale/ /openedx/locale/user/locale/
RUN cd /openedx/locale/user && \
    django-admin compilemessages -v1

# Compile i18n strings: in some cases, js locales are not properly compiled out of the box
# and we need to do a pass ourselves. Also, we need to compile the djangojs.js files for
# the downloaded locales.
RUN ./manage.py lms --settings=tutor.i18n compilejsi18n
RUN ./manage.py cms --settings=tutor.i18n compilejsi18n

# Copy scripts
COPY --chown=app:app ./bin /openedx/bin
RUN chmod a+x /openedx/bin/*
ENV PATH /openedx/bin:${PATH}

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

{{ patch("openedx-dockerfile") }}

EXPOSE 8000


###########################################################################################################################
############## PRODUCTION
###########################################################################################################################
FROM application as production

# Copy in and collect production static assets.
COPY --chown=app:app --from=bundles-production /openedx/staticfiles /openedx/staticfiles
COPY --chown=app:app --from=bundles-production /openedx/edx-platform/common/static/bundles /openedx/edx-platform/common/static/bundles
COPY --chown=app:app --from=css-production /openedx/edx-platform/lms/static/css /openedx/edx-platform/lms/static/css
COPY --chown=app:app --from=css-production /openedx/edx-platform/lms/static/certificates/css /openedx/edx-platform/lms/static/certificates/css
COPY --chown=app:app --from=css-production /openedx/edx-platform/cms/static/css /openedx/edx-platform/cms/static/css
RUN ./manage.py lms collectstatic --noinput --settings=tutor.assets
RUN ./manage.py cms collectstatic --noinput --settings=tutor.assets

# De-dupe static assets with synlinks
RUN rdfind -makesymlinks true -followsymlinks true /openedx/staticfiles/

# Default amount of uWSGI processes
ENV UWSGI_WORKERS=2

# Copy the default uWSGI configuration
COPY --chown=app:app settings/uwsgi.ini .

# Default django settings
ENV DJANGO_SETTINGS_MODULE lms.envs.tutor.production

# Run server
CMD uwsgi uwsgi.ini

{{ patch("openedx-dockerfile-final") }}


###########################################################################################################################
############## DEVELOPMENT
###########################################################################################################################
FROM application as development

# Install useful system requirements (as root)
USER root
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
	apt update && \
    apt install -y vim iputils-ping dnsutils telnet
USER app

# Copy in dev python requirements
COPY --chown=app:app --from=requirements-development /openedx/venv /openedx/venv

# https://pypi.org/project/ipdb/
# https://pypi.org/project/ipython
RUN --mount=type=cache,target=/openedx/.cache/pip,sharing=shared \
    pip install ipdb==0.13.13 ipython==8.12.0

# Add ipdb as default PYTHONBREAKPOINT
ENV PYTHONBREAKPOINT=ipdb.set_trace

# Copy in development static assets.
# In development mode, edx-platform expects the files to be in the repo, and pointed to by webpack-stats.json...
COPY --chown=app:app --from=bundles-development /openedx/staticfiles/webpack-stats.json /openedx/staticfiles/webpack-stats.json
COPY --chown=app:app --from=bundles-development /openedx/staticfiles/studio/webpack-stats.json /openedx/staticfiles/studio/webpack-stats.json

# ...however, we instead copy the files into the /openedx/devcache directory; otherwise, bind-mounting edx-platform
# would clobber them and force the user to rebuild assets.
COPY --chown=app:app --from=bundles-development /openedx/edx-platform/common/static/bundles /openedx/devcache/common/static/bundles
COPY --chown=app:app --from=css-development /openedx/edx-platform/lms/static/css /openedx/devcache/lms/static/css
COPY --chown=app:app --from=css-development /openedx/edx-platform/lms/static/certificates/css /openedx/devcache/lms/static/certificates/css
COPY --chown=app:app --from=css-development /openedx/edx-platform/cms/static/css /openedx/devcache/cms/static/css

# Create links for static dirs from edx-platform to devcache.
RUN link-static-to-devcache

{{ patch("openedx-dev-dockerfile-post-python-requirements") }}

# Default django settings
ENV DJANGO_SETTINGS_MODULE lms.envs.tutor.development

CMD ./manage.py $SERVICE_VARIANT runserver 0.0.0.0:8000
