FROM ubuntu:16.04

############ common to lms & cms

# Install system requirements
RUN apt update
RUN apt upgrade -y
# Global requirements
RUN apt install -y language-pack-en git python-virtualenv build-essential software-properties-common curl git-core libxml2-dev libxslt1-dev python-pip libmysqlclient-dev python-apt python-dev libxmlsec1-dev libfreetype6-dev swig gcc g++
# edxapp requirements
RUN apt install -y gettext gfortran graphviz graphviz-dev libffi-dev libfreetype6-dev libgeos-dev libjpeg8-dev liblapack-dev libpng12-dev libxml2-dev libxmlsec1-dev libxslt1-dev nodejs npm ntp pkg-config 

# Install symlink so that we have access to 'node' binary without virtualenv.
# This replaces the "nodeenv" install.
RUN apt install -y nodejs-legacy

# Static assets will reside in /openedx/data and edx-platform will be
# checked-out in /openedx
VOLUME /openedx/data
WORKDIR /openedx

# Checkout edx-platform code
RUN git clone https://github.com/edx/edx-platform.git
WORKDIR /openedx/edx-platform
RUN git fetch && \
  git checkout open-release/ginkgo.master 

# Install python requirements
RUN pip install pip==8.1.2
RUN pip install setuptools==24.0.3
RUN pip install -r requirements/edx/pre.txt
RUN pip install -r requirements/edx/github.txt
RUN pip install -r requirements/edx/local.txt
RUN pip install -r requirements/edx/base.txt
RUN pip install -r requirements/edx/post.txt
RUN pip install -r requirements/edx/paver.txt
# TODO install ced from pip
RUN curl https://raw.githubusercontent.com/regisb/ced/v0.2/ced/ced > /usr/local/bin/ced
RUN chmod a+x /usr/local/bin/ced

# Finish requirements install
RUN paver install_prereqs

ARG lms_host=localhost:8000
ARG cms_host=localhost:8000
ARG platform_name="My Ginkgo Open edX"
# service variang is "lms" or "cms"
ARG service_variant
ARG secret_key

# Generate configuration files
ENV LMS_HOST=$lms_host CMS_HOST=$cms_host PLATFORM_NAME=$platform_name SECRET_KEY=$secret_key
COPY ./config/production_lms.py /openedx/edx-platform/lms/envs/production.py
COPY ./config/production_cms.py /openedx/edx-platform/cms/envs/production.py
COPY ./config/lms.env.json.templ /openedx/
COPY ./config/cms.env.json.templ /openedx/
COPY ./config/lms.auth.json.templ /openedx/
COPY ./config/cms.auth.json.templ /openedx/
RUN ced /openedx/lms.env.json.templ -o /openedx/lms.env.json
RUN ced /openedx/cms.env.json.templ -o /openedx/cms.env.json
RUN ced /openedx/lms.auth.json.templ -o /openedx/lms.auth.json
RUN ced /openedx/cms.auth.json.templ -o /openedx/cms.auth.json


############ End of code common to lms & cms

# Configure environment
ENV DJANGO_SETTINGS_MODULE ${service_variant}.envs.production
ENV SERVICE_VARIANT ${service_variant}

# Run server
EXPOSE 8000
CMD gunicorn --name ${SERVICE_VARIANT} --bind=0.0.0.0:8000 --max-requests=1000 ${SERVICE_VARIANT}.wsgi:application
