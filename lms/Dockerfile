FROM ubuntu:16.04

# Install system requirements
RUN apt update
RUN apt upgrade -y
# Global requirements
RUN apt install -y language-pack-en git python-virtualenv build-essential software-properties-common curl git-core libxml2-dev libxslt1-dev python-pip libmysqlclient-dev python-apt python-dev libxmlsec1-dev libfreetype6-dev swig gcc g++
# lms requirements
RUN apt install -y gettext gfortran graphviz graphviz-dev libffi-dev libfreetype6-dev libgeos-dev libjpeg8-dev liblapack-dev libpng12-dev libxml2-dev libxmlsec1-dev libxslt1-dev nodejs npm ntp pkg-config 

# Install symlink so that we have access to 'node' binary without virtualenv.
# This replaces the "nodeenv" install.
RUN apt install -y nodejs-legacy

# Create necessary folders
RUN mkdir /openedx
RUN mkdir /openedx/data
RUN mkdir /openedx/logs
RUN mkdir /openedx/uploads
RUN mkdir /openedx/staticfiles
VOLUME /openedx/data
VOLUME /openedx/logs
VOLUME /openedx/staticfiles
VOLUME /openedx/uploads
WORKDIR /openedx

# Checkout edx-platform code
RUN git clone https://github.com/edx/edx-platform.git
WORKDIR /openedx/edx-platform
RUN git checkout open-release/ficus.master 

# Install python requirements
RUN pip install pip==8.1.2
RUN pip install setuptools==24.0.3
RUN pip install -r requirements/edx/pre.txt
RUN pip install -r requirements/edx/github.txt
RUN pip install -r requirements/edx/local.txt
RUN pip install -r requirements/edx/base.txt
RUN pip install -r requirements/edx/post.txt
RUN pip install -r requirements/edx/paver.txt

# Finish requirements install
RUN paver install_prereqs

# Copy configuration files
COPY ./config/lms.env.json /openedx/
COPY ./config/lms.auth.json /openedx/
COPY ./config/production.py /openedx/edx-platform/lms/envs/

# Configure environment
ENV DJANGO_SETTINGS_MODULE lms.envs.production
ENV SERVICE_VARIANT lms

# Run server
EXPOSE 8000

# Migrate
ARG RUN_MIGRATIONS=0
ENV RUN_MIGRATIONS ${RUN_MIGRATIONS}
# Collect static assets
ARG COLLECT_STATIC=0
ENV COLLECT_STATIC ${COLLECT_STATIC}

# TODO Here we wait until mysql and mongodb become available but it's a terrible solution
CMD sleep 5 && \
  if [ "$RUN_MIGRATIONS" = "1" ] ; then ./manage.py lms migrate --settings=production ; fi && \
  if [ "$COLLECT_STATIC" = "1" ] ; then paver update_assets lms --settings=production ; fi && \
  gunicorn --name lms --bind=0.0.0.0:8000 --max-requests=1000 lms.wsgi:application
