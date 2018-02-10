FROM ubuntu:16.04

############ common to lms & cms

# Install system requirements
RUN apt update && \
  apt upgrade -y && \
  # Global requirements
  apt install -y language-pack-en git python-virtualenv build-essential software-properties-common curl git-core libxml2-dev libxslt1-dev python-pip libmysqlclient-dev python-apt python-dev libxmlsec1-dev libfreetype6-dev swig gcc g++ && \
  # edxapp requirements
  apt install -y gettext gfortran graphviz graphviz-dev libffi-dev libfreetype6-dev libgeos-dev libjpeg8-dev liblapack-dev libpng12-dev libxml2-dev libxmlsec1-dev libxslt1-dev nodejs npm ntp pkg-config && \
  # Our requirements
  apt install -y mysql-client

# Install symlink so that we have access to 'node' binary without virtualenv.
# This replaces the "nodeenv" install.
RUN apt install -y nodejs-legacy

# Static assets will reside in /openedx/data and edx-platform will be
# checked-out in /openedx/
RUN mkdir /openedx /openedx/data /openedx/edx-platform
VOLUME /openedx/data
WORKDIR /openedx/edx-platform

## Checkout edx-platform code
RUN git clone https://github.com/edx/edx-platform.git --branch open-release/ginkgo.master --depth 1 .

# Install python requirements
RUN pip install -r requirements/edx/pre.txt
RUN pip install -r requirements/edx/github.txt
RUN pip install -r requirements/edx/local.txt
RUN pip install -r requirements/edx/base.txt
RUN pip install -r requirements/edx/post.txt
RUN pip install -r requirements/edx/paver.txt

# Install nodejs requirements
RUN npm install

# Copy configuration files
COPY ./config/production_lms.py /openedx/edx-platform/lms/envs/production.py
COPY ./config/production_cms.py /openedx/edx-platform/cms/envs/production.py
COPY ./config/production_common.py /openedx/edx-platform/lms/envs/production_common.py
COPY ./config/production_common.py /openedx/edx-platform/cms/envs/production_common.py
COPY ./config/lms.env.json /openedx/
COPY ./config/cms.env.json /openedx/
COPY ./config/lms.auth.json /openedx/
COPY ./config/cms.auth.json /openedx/

# Copy convenient script
COPY ./wait-for-greenlight.sh .

############ End of code common to lms & cms

# service variant is "lms" or "cms"
ARG service_variant

# Configure environment
ENV DJANGO_SETTINGS_MODULE ${service_variant}.envs.production
ENV SERVICE_VARIANT ${service_variant}

# Run server
EXPOSE 8000
CMD gunicorn --name ${SERVICE_VARIANT} --bind=0.0.0.0:8000 --max-requests=1000 ${SERVICE_VARIANT}.wsgi:application
