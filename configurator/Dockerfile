FROM ubuntu:18.04

RUN apt update && \
  apt install -y python3 python3-pip
RUN pip3 install jinja2

RUN mkdir /openedx
VOLUME /openedx/config
COPY ./bin/configure.py /openedx/configure.py
COPY ./bin/docker-entrypoint.sh /openedx/docker-entrypoint.sh
WORKDIR /openedx

ENV SILENT=''
ENV ACTIVATE_HTTPS=''
ENV ACTIVATE_XQUEUE=''
ENTRYPOINT ["./docker-entrypoint.sh"]
