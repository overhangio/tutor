FROM ubuntu:18.04
MAINTAINER Régis Behmo <regis@behmo.com>

RUN apt update && \
  apt upgrade -y && \
  apt install -y language-pack-en git python-pip libmysqlclient-dev

RUN mkdir /openedx
RUN git clone https://github.com/edx/xqueue --branch open-release/ironwood.1 --depth 1 /openedx/xqueue 
WORKDIR /openedx/xqueue

RUN pip install -r requirements.txt

EXPOSE 8040
CMD gunicorn --name xqueue --bind=0.0.0.0:8040 --max-requests=1000 xqueue.wsgi:application
