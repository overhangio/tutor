FROM ubuntu:18.04
MAINTAINER Régis Behmo <regis@behmo.com>

RUN apt update && \
  apt upgrade -y && \
  apt install -y language-pack-en git python-pip libmysqlclient-dev

RUN mkdir /openedx
RUN git clone https://github.com/edx/edx-notes-api --branch open-release/ironwood.1 --depth 1 /openedx/edx-notes-api
WORKDIR /openedx/edx-notes-api

RUN pip install -r requirements/base.txt

EXPOSE 8000
CMD gunicorn --workers=2 --name notes --bind=0.0.0.0:8000 --max-requests=1000 notesserver.wsgi:application
