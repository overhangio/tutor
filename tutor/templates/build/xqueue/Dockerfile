FROM ubuntu:18.04
MAINTAINER Overhang.io <contact@overhang.io>

RUN apt update && \
  apt upgrade -y && \
  apt install -y language-pack-en git python-pip libmysqlclient-dev

RUN mkdir /openedx /openedx/data
RUN git clone https://github.com/edx/xqueue --branch open-release/ironwood.2 --depth 1 /openedx/xqueue
WORKDIR /openedx/xqueue

RUN pip install -r requirements.txt

EXPOSE 8040
CMD gunicorn --workers=2 --name xqueue --bind=0.0.0.0:8040 --max-requests=1000 xqueue.wsgi:application
