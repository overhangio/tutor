FROM ubuntu:16.04

RUN apt update && \
  apt upgrade -y && \
  apt install -y language-pack-en git git-core python-pip libmysqlclient-dev

RUN mkdir /openedx
RUN git clone https://github.com/edx/xqueue --branch open-release/hawthorn.1 --depth 1 /openedx/xqueue 
WORKDIR /openedx/xqueue

RUN pip install -r requirements.txt

ENV DJANGO_SETTINGS_MODULE xqueue.universal
RUN ln -s /openedx/config/universal.py xqueue/universal.py

EXPOSE 8040
CMD gunicorn --name xqueue --bind=0.0.0.0:8040 --max-requests=1000 xqueue.wsgi:application
